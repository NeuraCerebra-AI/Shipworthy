"""Authoritative validation for one repository-only Gauntlet agent result."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SUPPORT = HERE.parent / "support"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.skill_product.support.frontier_validation import (  # noqa: E402
    FrontierValidationError,
    validate_frontier,
)
from tests.skill_product.support.schema_subset import (  # noqa: E402
    SchemaReferenceError,
    SchemaValidationError,
    validate,
)


SCHEMAS = ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas"
COMPARISON_KINDS = ("feature", "surface", "control", "transition")
MAX_DIAGNOSTICS = 12


class ArtifactValidationError(ValueError):
    """One or more final artifacts cannot support an acceptance decision."""

    def __init__(self, diagnostics: list[str]):
        self.diagnostics = tuple(diagnostics[:MAX_DIAGNOSTICS])
        super().__init__("; ".join(self.diagnostics))


def _read_object(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{label} is unreadable JSON: {error}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label} must be a JSON object")
        return None
    return value


def _resolve_evidence(reference: Any, evidence_root: Path) -> bool:
    if not isinstance(reference, str) or not reference:
        return False
    candidate = Path(reference.split("#", 1)[0])
    if candidate.is_absolute() or ".." in candidate.parts:
        return False
    resolved = (evidence_root / candidate).resolve()
    try:
        resolved.relative_to(evidence_root.resolve())
    except ValueError:
        return False
    return resolved.is_file() and resolved.stat().st_size > 0


def validate_agent_artifacts(evidence_root: Path) -> dict[str, Any]:
    """Validate the canonical JSON pair and HTML, then return comparator input."""

    evidence_root = Path(evidence_root).resolve()
    errors: list[str] = []
    report_path = evidence_root / "report-input.json"
    ledger_path = evidence_root / "readiness-ledger.json"
    html_path = evidence_root / "report.html"
    report = _read_object(report_path, "report-input.json", errors)
    ledger = _read_object(ledger_path, "readiness-ledger.json", errors)
    try:
        html = html_path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"report.html is unreadable: {error}")
        html = ""

    if report is not None:
        try:
            validate(report, SCHEMAS / "report-input.schema.json")
        except (SchemaValidationError, SchemaReferenceError, OSError, json.JSONDecodeError) as error:
            errors.append(f"report-input.json schema validation failed: {error}")
    if ledger is not None:
        try:
            validate(ledger, SCHEMAS / "readiness-ledger.schema.json")
        except (SchemaValidationError, SchemaReferenceError, OSError, json.JSONDecodeError) as error:
            errors.append(f"readiness-ledger.json schema validation failed: {error}")

    source = report.get("source_ledger") if report else None
    if not isinstance(source, dict):
        errors.append("report-input.json must contain canonical source_ledger")
    elif ledger is not None and source != ledger:
        errors.append("readiness-ledger.json and report-input.json source_ledger diverge")

    canonical = ledger if ledger is not None else source
    frontier = canonical.get("path_frontier") if isinstance(canonical, dict) else None
    if not isinstance(frontier, dict):
        errors.append("canonical source ledger must contain object-shaped path_frontier")
    else:
        try:
            validate_frontier(frontier, evidence_root)
        except FrontierValidationError as error:
            errors.extend(f"path_frontier: {item}" for item in error.diagnostics)

    findings = canonical.get("findings") if isinstance(canonical, dict) else None
    if not isinstance(findings, list):
        errors.append("canonical source ledger findings must be an array")
        findings = []
    row_keys = {
        row.get("semantic_key")
        for row in (frontier.get("rows", []) if isinstance(frontier, dict) else [])
        if isinstance(row, dict)
    }
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict) or finding.get("action") != "Fix":
            continue
        affected = finding.get("affected_semantic_keys")
        if not isinstance(affected, list) or not affected or any(key not in row_keys for key in affected):
            errors.append(f"findings[{index}] Fix lineage does not resolve to exact frontier rows")
        references = finding.get("evidence_refs")
        if not isinstance(references, list) or not references or any(
            not _resolve_evidence(reference, evidence_root) for reference in references
        ):
            errors.append(f"findings[{index}] evidence does not resolve under agent output")

    closure = frontier.get("closure_state") if isinstance(frontier, dict) else ""
    if not closure or f'data-closure-state="{closure}"' not in html:
        errors.append("report.html closure contradicts canonical frontier")
    if errors:
        raise ArtifactValidationError(errors)

    rows = frontier["rows"]
    return {
        "closure_state": closure,
        "html_closure_state": closure,
        "summary": {kind: sum(row.get("kind") == kind for row in rows) for kind in COMPARISON_KINDS},
        "rows": rows,
        "findings": findings,
    }

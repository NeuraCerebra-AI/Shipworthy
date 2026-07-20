"""Repository-only cross-field validation for the canonical path frontier."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


METHOD_FAMILIES = frozenset(
    {
        "runtime_human_interaction",
        "runtime_structural_inventory",
        "static_implementation_inventory",
        "declared_behavior_inventory",
    }
)
KINDS = ("intent", "feature", "surface", "control", "transition")
PARENT_KIND = {
    "feature": "intent",
    "surface": "feature",
    "control": "surface",
    "transition": "control",
}
TERMINAL_STATUSES = frozenset(
    {
        "covered",
        "sampled_with_justification",
        "blocked",
        "avoided",
        "missing",
        "out_of_scope",
        "evidence_debt",
    }
)
UNRESOLVED_STATUSES = frozenset({"unattempted", "unknown", "maybe"})
CLOSURE_STATES = frozenset(
    {"closed_multi_source", "incomplete", "single_source", "blocked", "static_only"}
)
MAX_DIAGNOSTICS = 20


class FrontierValidationError(ValueError):
    """The frontier violates one or more bounded cross-field invariants."""

    def __init__(self, diagnostics: Iterable[str]):
        self.diagnostics = tuple(list(diagnostics)[:MAX_DIAGNOSTICS])
        super().__init__("; ".join(self.diagnostics))


def _evidence_path(reference: str, root: Path) -> Path | None:
    candidate = Path(reference)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    return resolved


def _check_evidence(references: Any, root: Path, label: str, errors: list[str]) -> None:
    if not isinstance(references, list) or not references:
        errors.append(f"{label}: evidence_refs must be a non-empty array")
        return
    for reference in references:
        if not isinstance(reference, str):
            errors.append(f"{label}: evidence reference must be a string")
            continue
        resolved = _evidence_path(reference, root)
        if resolved is None or not resolved.is_file():
            errors.append(f"{label}: evidence reference does not resolve under evidence root: {reference}")


def _derive_closure(frontier: dict[str, Any], families: set[str]) -> str:
    rows = frontier.get("rows", [])
    material = [row for row in rows if row.get("material", True)]
    if frontier.get("reconciliation_differences") or any(
        row.get("status") in UNRESOLVED_STATUSES | {"evidence_debt"} for row in material
    ):
        return "incomplete"
    if any(row.get("status") == "blocked" for row in material):
        return "blocked"
    runtime = families & {"runtime_human_interaction", "runtime_structural_inventory"}
    independent = families & {"static_implementation_inventory", "declared_behavior_inventory"}
    if not runtime and independent:
        return "static_only"
    if len(families) < 2:
        return "single_source"
    return "closed_multi_source"


def validate_frontier(frontier: dict[str, Any], evidence_root: Path) -> dict[str, Any]:
    """Validate one frontier and return a small machine-readable success packet."""

    errors: list[str] = []
    root = Path(evidence_root).resolve()
    if not root.is_dir():
        raise FrontierValidationError(["evidence root is not a directory"])
    if not isinstance(frontier, dict):
        raise FrontierValidationError(["path_frontier must be an object"])

    if frontier.get("normalization_version") != "shipworthy-semantic-v1":
        errors.append("normalization_version must be shipworthy-semantic-v1")
    if frontier.get("method_taxonomy_version") != "shipworthy-methods-v1":
        errors.append("method_taxonomy_version must be shipworthy-methods-v1")
    if frontier.get("closure_state") not in CLOSURE_STATES:
        errors.append("closure_state is not recognized")

    rows = frontier.get("rows")
    if not isinstance(rows, list):
        raise FrontierValidationError(errors + ["rows must be an array"])
    ids = [row.get("id") for row in rows if isinstance(row, dict)]
    for row_id, count in Counter(ids).items():
        if row_id is None or count > 1:
            errors.append(f"row id must be present and unique: {row_id}")
    semantic_keys = [row.get("semantic_key") for row in rows if isinstance(row, dict)]
    for semantic_key, count in Counter(semantic_keys).items():
        if semantic_key is None or count > 1:
            errors.append(f"semantic_key must be present and unique: {semantic_key}")
    by_id = {row.get("id"): row for row in rows if isinstance(row, dict) and row.get("id")}
    children: Counter[str] = Counter()
    observed_families: set[str] = set()

    for index, row in enumerate(rows):
        label = f"rows[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label}: row must be an object")
            continue
        kind = row.get("kind")
        if kind not in KINDS:
            errors.append(f"{label}: invalid kind")
            continue
        semantic_key = row.get("semantic_key")
        if not isinstance(semantic_key, str) or not semantic_key.startswith(f"{kind}:"):
            errors.append(f"{label}: semantic_key must start with {kind}:")
        if row.get("normalization_version") != "shipworthy-semantic-v1":
            errors.append(f"{label}: invalid normalization_version")
        if row.get("method_taxonomy_version") != "shipworthy-methods-v1":
            errors.append(f"{label}: invalid method_taxonomy_version")

        if kind == "intent":
            if row.get("parent_id") is not None:
                errors.append(f"{label}: intent cannot have a parent")
        else:
            parent_id = row.get("parent_id")
            parent = by_id.get(parent_id)
            if parent is None or parent.get("kind") != PARENT_KIND[kind]:
                errors.append(f"{label}: {kind} parent must be {PARENT_KIND[kind]}")
            elif isinstance(parent_id, str):
                children[parent_id] += 1

        if kind == "control":
            identity = row.get("control_identity")
            required = {"name", "control_type", "disambiguator"}
            if not isinstance(identity, dict) or not required <= set(identity):
                errors.append(f"{label}: control_identity requires name, control_type, and disambiguator")
        if kind == "transition" and not all(row.get(field) for field in ("before_state", "after_state")):
            errors.append(f"{label}: transition requires before_state and after_state")

        status = row.get("status")
        if status not in TERMINAL_STATUSES | UNRESOLVED_STATUSES:
            errors.append(f"{label}: invalid status")
        if status == "covered" and kind in {"control", "transition"}:
            if not isinstance(row.get("attempt_count"), int) or row["attempt_count"] < 1:
                errors.append(f"{label}: covered {kind} requires attempt_count >= 1")
            _check_evidence(row.get("evidence_refs"), root, label, errors)

        observations = row.get("observations", [])
        if not isinstance(observations, list):
            errors.append(f"{label}: observations must be an array")
            observations = []
        for offset, item in enumerate(observations):
            observation_label = f"{label}.observations[{offset}]"
            if not isinstance(item, dict):
                errors.append(f"{observation_label}: observation must be an object")
                continue
            family = item.get("method_family")
            if family not in METHOD_FAMILIES:
                errors.append(f"{observation_label}: invalid method_family")
            else:
                observed_families.add(family)
            if item.get("method_taxonomy_version") != "shipworthy-methods-v1":
                errors.append(f"{observation_label}: invalid method_taxonomy_version")
            _check_evidence(item.get("evidence_refs"), root, observation_label, errors)

    for row in rows:
        if isinstance(row, dict) and row.get("kind") == "feature":
            if children[row.get("id")] == 0 and row.get("status") not in TERMINAL_STATUSES - {"covered"}:
                errors.append(f"{row.get('id')}: feature needs a child path or explicit terminal disposition")

    expected_summary = {kind: sum(row.get("kind") == kind for row in rows if isinstance(row, dict)) for kind in KINDS}
    if frontier.get("summary") != expected_summary:
        errors.append("summary does not reconcile exactly with rows")

    differences = frontier.get("reconciliation_differences", [])
    if not isinstance(differences, list):
        errors.append("reconciliation_differences must be an array")
    elif frontier.get("closure_state") == "closed_multi_source" and differences:
        errors.append("closed_multi_source cannot retain reconciliation differences")

    passes = frontier.get("discovery_passes", [])
    pass_families: set[str] = set()
    zero_yield: list[dict[str, Any]] = []
    if not isinstance(passes, list):
        errors.append("discovery_passes must be an array")
        passes = []
    for index, item in enumerate(passes):
        if not isinstance(item, dict):
            errors.append(f"discovery_passes[{index}]: pass must be an object")
            continue
        family = item.get("method_family")
        if family not in METHOD_FAMILIES:
            errors.append(f"discovery_passes[{index}]: invalid method_family")
        else:
            pass_families.add(family)
        if item.get("method_taxonomy_version") != "shipworthy-methods-v1":
            errors.append(f"discovery_passes[{index}]: invalid method_taxonomy_version")
        if item.get("new_semantic_keys") == [] and item.get("starting_frontier_digest") == item.get("ending_frontier_digest"):
            zero_yield.append(item)

    pass_ids = [item.get("id") for item in passes if isinstance(item, dict)]
    if len(pass_ids) != len(set(pass_ids)):
        errors.append("discovery pass ids must be unique")
    known_pass_ids = set(pass_ids)
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        for offset, item in enumerate(row.get("observations", [])):
            if isinstance(item, dict) and item.get("discovery_pass_id") not in known_pass_ids:
                errors.append(
                    f"rows[{index}].observations[{offset}]: discovery_pass_id is not declared"
                )

    if frontier.get("closure_state") == "closed_multi_source":
        material = [row for row in rows if isinstance(row, dict) and row.get("material", True)]
        if any(row.get("status") not in TERMINAL_STATUSES for row in material):
            errors.append("closed_multi_source has unresolved material rows")
        signatures = {
            (item.get("method_family"), item.get("role"), item.get("fixture"), item.get("viewport"))
            for item in zero_yield
        }
        if len(zero_yield) < 2 or len(signatures) < 2 or len({item.get("method_family") for item in zero_yield}) < 2:
            errors.append("closed_multi_source requires two independent qualifying zero-yield passes")
        if len(pass_families | observed_families) < 2:
            errors.append("closed_multi_source requires at least two canonical method families")

    derived = _derive_closure(frontier, pass_families | observed_families)
    if frontier.get("closure_state") != derived:
        errors.append(f"closure_state must be {derived} from the recorded evidence")

    if errors:
        raise FrontierValidationError(errors)
    return {
        "status": "valid",
        "closure_state": frontier["closure_state"],
        "row_count": len(rows),
        "diagnostics": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one Shipworthy path frontier")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--evidence-root", required=True, type=Path)
    args = parser.parse_args()
    try:
        frontier = json.loads(args.input.read_text(encoding="utf-8"))
        result = validate_frontier(frontier, args.evidence_root)
    except (OSError, json.JSONDecodeError, FrontierValidationError) as error:
        diagnostics = list(getattr(error, "diagnostics", (str(error),)))[:MAX_DIAGNOSTICS]
        print(json.dumps({"status": "invalid", "diagnostics": diagnostics}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

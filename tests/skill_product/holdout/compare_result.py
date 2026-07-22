#!/usr/bin/env python3
"""Private structural scoring for the unfamiliar holdout."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tests.skill_product.gauntlet.behavior_graph import normalize_text, verify_private_expectation
from tests.skill_product.gauntlet.artifact_validation import ArtifactValidationError, validate_agent_artifacts


MAX_ARTIFACT_BYTES = 16 * 1024 * 1024
REQUIRED_ARTIFACTS = (
    "holdout-observation.json", "readiness-ledger.json", "report-input.json", "report.html",
)


_STOP_WORDS = {"a", "after", "as", "but", "can", "is", "it", "re", "still", "the", "to", "without"}
_TOKEN_EQUIVALENTS = {
    "access": "permission", "authorization": "permission", "revoked": "revoke",
    "successful": "success", "successfully": "success", "presented": "shown",
    "refresh": "reentry", "reload": "reentry", "entry": "reentry",
    "draft": "progress", "lost": "lose", "loses": "lose", "loss": "lose",
    "discarded": "lose", "discards": "lose", "confirmation": "warning",
    "creation": "create", "submitted": "submit", "selection": "choice",
    "corrected": "valid", "old": "stale", "remains": "keeps",
}


def _text(value: Any) -> str:
    return normalize_text(json.dumps(value, ensure_ascii=False, sort_keys=True))


def _tokens(value: Any) -> set[str]:
    return {
        _TOKEN_EQUIVALENTS.get(token, token)
        for token in _text(value).split("-")
        if token and token not in _STOP_WORDS
    }


def _semantic_score(value: Any, alias: str) -> float:
    text, normalized_alias = _text(value), normalize_text(alias)
    if normalized_alias in text:
        return 2.0
    expected = _tokens(alias)
    if len(expected) < 2:
        return 0.0
    score = len(expected & _tokens(value)) / len(expected)
    return score if score >= 0.75 else 0.0


def _semantically_contains(value: Any, alias: str) -> bool:
    return _semantic_score(value, alias) > 0


def _contains_alias(value: Any, aliases: list[str]) -> bool:
    return any(_semantically_contains(value, alias) for alias in aliases)


def _metric(found: int, total: int) -> dict:
    return {"found": found, "total": total, "recall": 1.0 if total == 0 else round(found / total, 4)}


def _assign_findings(expectations: list[dict], findings: list[dict]) -> tuple[list[dict], set[int]]:
    """Find a deterministic maximum one-to-one defect/finding assignment."""
    adjacency: dict[int, list[tuple[float, int]]] = {}
    for expectation_index, expectation in enumerate(expectations):
        for finding_index, finding in enumerate(findings):
            score = max((_semantic_score(finding, alias) for alias in expectation["aliases"]), default=0.0)
            if score:
                adjacency.setdefault(expectation_index, []).append((score, finding_index))
    for edges in adjacency.values():
        edges.sort(key=lambda edge: (-edge[0], edge[1]))
    finding_owner: dict[int, int] = {}

    def augment(expectation_index: int, visited: set[int]) -> bool:
        for _score, finding_index in adjacency.get(expectation_index, []):
            if finding_index in visited:
                continue
            visited.add(finding_index)
            owner = finding_owner.get(finding_index)
            if owner is None or augment(owner, visited):
                finding_owner[finding_index] = expectation_index
                return True
        return False

    for expectation_index in range(len(expectations)):
        augment(expectation_index, set())
    assigned_expectations = set(finding_owner.values())
    assigned_findings = set(finding_owner)
    return [expectation for index, expectation in enumerate(expectations) if index in assigned_expectations], assigned_findings


def validate_holdout_artifacts(root: Path | str) -> dict:
    """Compute integrity with the same canonical validator used by the Gauntlet."""
    root = Path(root).resolve()
    errors: list[str] = []
    values: dict[str, Any] = {}
    for name in REQUIRED_ARTIFACTS:
        path = root / name
        if not path.is_file() or path.is_symlink():
            errors.append(f"missing:{name}")
            continue
        if path.stat().st_size > MAX_ARTIFACT_BYTES:
            errors.append(f"oversize:{name}")
            continue
        if name == "holdout-observation.json":
            try:
                values[name] = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                errors.append(f"invalid-json:{name}")
    observation = values.get("holdout-observation.json")
    rows = 0
    if not errors:
        try:
            canonical = validate_agent_artifacts(root)
            rows = len(canonical["rows"])
        except ArtifactValidationError as error:
            errors.extend(f"canonical:{diagnostic}" for diagnostic in error.diagnostics)
    if not isinstance(observation, dict):
        errors.append("invalid-observation")
    errors = list(dict.fromkeys(errors))
    return {"valid": not errors, "errors": errors, "frontier_rows": rows}


def compare_holdout(observation: dict, receipt_events: list[dict], oracle: dict, *, artifact_integrity: bool = False) -> dict:
    material = oracle.get("material_behaviors", [])
    defects = oracle.get("seeded_defects", [])
    discovery_evidence = {
        "routes": observation.get("routes", []),
        "controls": observation.get("controls", []),
        "transitions": observation.get("transitions", []),
    }
    discovered = [item for item in material if _contains_alias(discovery_evidence, item["aliases"])]
    executed = [item for item in material if verify_private_expectation(item["receipt"], receipt_events).status == "supported"]
    findings = observation.get("findings") if isinstance(observation.get("findings"), list) else []
    detected, matched_finding_indexes = _assign_findings(defects, findings)
    accepted_extras = oracle.get("valid_extra_findings", [])
    valid_extras = sorted(route for route in observation.get("routes", []) if route not in {"/", "/welcome", "/onboarding", "/complete"} and any(event.get("event_type") == "route_visit" and event.get("route") == route for event in receipt_events))
    valid_extra_findings = []
    for index, finding in enumerate(findings):
        if index in matched_finding_indexes:
            continue
        if any(_contains_alias(finding, item["aliases"]) for item in accepted_extras):
            matched_finding_indexes.add(index)
            valid_extra_findings.append(finding.get("finding_code", f"finding-{index + 1}"))
    unsupported = [finding.get("finding_code", f"finding-{index + 1}") for index, finding in enumerate(findings) if index not in matched_finding_indexes]
    dimensions = {
        "discovery": _metric(len(discovered), len(material)),
        "execution": _metric(len(executed), len(material)),
        "defect_detection": _metric(len(detected), len(defects)),
        "evidence_integrity": {"valid": artifact_integrity},
    }
    closure = observation.get("closure_honesty") if isinstance(observation.get("closure_honesty"), dict) else {}
    false_closure = bool(closure.get("claimed_exhaustive")) and (
        dimensions["discovery"]["recall"] < 1 or dimensions["execution"]["recall"] < 1 or not dimensions["evidence_integrity"]["valid"]
    )
    blockers = {item["id"] for item in defects if item.get("release_blocking")}
    detected_ids = {item["id"] for item in detected}
    status = "FAIL" if false_closure or not dimensions["evidence_integrity"]["valid"] or not blockers.issubset(detected_ids) or dimensions["discovery"]["recall"] < 1 or dimensions["execution"]["recall"] < 1 else "REVIEW_REQUIRED" if unsupported else "PASS"
    return {
        "status": status, "dimensions": dimensions, "false_exhaustive_closure": false_closure,
        "missing_behavior_ids": [item["id"] for item in material if item not in discovered],
        "unexecuted_behavior_ids": [item["id"] for item in material if item not in executed],
        "missed_defect_ids": [item["id"] for item in defects if item not in detected],
        "release_blocking_defects_found": sorted(blockers & detected_ids),
        "D_valid_extra": valid_extras, "D_valid_extra_finding": valid_extra_findings,
        "E_unsupported_finding": unsupported,
    }

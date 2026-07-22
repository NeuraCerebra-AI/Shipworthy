#!/usr/bin/env python3
"""Pure semantic comparison for the repository-only Gauntlet."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

if __package__:
    from .behavior_graph import BehaviorNode, Match, match_behavior, normalize_route as graph_normalize_route, normalize_text, parse_semantic_key, unique_receipt_nodes, verify_execution_claim, verify_private_expectation
else:
    from behavior_graph import BehaviorNode, Match, match_behavior, normalize_route as graph_normalize_route, normalize_text, parse_semantic_key, unique_receipt_nodes, verify_execution_claim, verify_private_expectation


NORMALIZATION_VERSION = "shipworthy-semantic-v1"
METHOD_VERSION = "shipworthy-methods-v1"
KINDS = ("feature", "surface", "control", "transition")
TERMINAL = frozenset({"covered", "avoided", "blocked", "missing", "unavailable"})


def normalize_token(value: Any) -> str:
    return normalize_text(value)


def normalize_route(value: Any) -> str:
    return graph_normalize_route(value)


def derive_semantic_key(item: dict[str, Any]) -> str:
    kind = item["kind"]
    if kind == "intent":
        return f"intent:{normalize_token(item.get('role', 'all-users'))}:{normalize_token(item['goal'])}"
    if kind == "feature":
        return f"feature:{normalize_token(item['identity'])}"
    if kind == "surface":
        return ":".join(
            ("surface", normalize_route(item["route"]), normalize_token(item["state"]), normalize_token(item["role"]), normalize_token(item["viewport"]))
        )
    if kind == "control":
        return ":".join(
            ("control", item["surface_key"], normalize_token(item["identity"]), normalize_token(item["control_type"]), normalize_token(item["disambiguator"]))
        )
    if kind == "transition":
        return ":".join(
            ("transition", normalize_token(item["before_state"]), item["control_key"], normalize_token(item.get("after_state") or item["expected_result"]))
        )
    raise ValueError(f"unsupported semantic kind: {kind}")


def _load(path: Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"oracle document must be an object: {path}")
    return data


def load_and_validate_oracle(surface_path: Path, defect_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    surface, defects = _load(surface_path), _load(defect_path)
    if surface.get("schema_version") != "shipworthy-gauntlet-surface-v1":
        raise ValueError("unsupported surface oracle version")
    if defects.get("schema_version") != "shipworthy-gauntlet-defects-v1":
        raise ValueError("unsupported defect oracle version")
    items = surface.get("items")
    supporting_routes = surface.get("supporting_routes")
    if not isinstance(supporting_routes, list) or not supporting_routes:
        raise ValueError("surface oracle must declare supporting routes")
    if len(set(supporting_routes)) != len(supporting_routes) or any(normalize_route(route) != route for route in supporting_routes):
        raise ValueError("supporting routes must be unique normalized paths")
    supporting_features = surface.get("supporting_features")
    if not isinstance(supporting_features, list) or not supporting_features or len(set(supporting_features)) != len(supporting_features):
        raise ValueError("surface oracle must declare unique supporting features")
    if not isinstance(items, list) or len(items) != 18:
        raise ValueError("surface oracle must contain exactly eighteen cases")
    keys: set[str] = set()
    required = {
        "id", "case_id", "kind", "semantic_key", "normalization_version",
        "method_taxonomy_version", "identity", "disambiguator", "materiality",
        "availability_condition", "safety_class", "allowed_dispositions_by_mode",
        "minimum_evidence_class", "accepted_aliases", "required_modes",
    }
    for item in items:
        missing = required - set(item)
        if missing:
            raise ValueError(f"{item.get('id', '<unknown>')}: missing {sorted(missing)[0]}")
        if item["semantic_key"] in keys:
            raise ValueError(f"duplicate semantic key: {item['semantic_key']}")
        keys.add(item["semantic_key"])
        if item["normalization_version"] != NORMALIZATION_VERSION or item["method_taxonomy_version"] != METHOD_VERSION:
            raise ValueError(f"{item['id']}: incompatible normalization metadata")
        for mode in item["required_modes"]:
            allowed = item["allowed_dispositions_by_mode"].get(mode, [])
            if not allowed or not set(allowed).issubset(TERMINAL):
                raise ValueError(f"{item['id']}: invalid dispositions for {mode}")
    for decoy in surface.get("negative_controls", []):
        if decoy.get("decoy_policy") != "negative_control":
            raise ValueError("negative control policy is required")
    for defect in defects.get("defects", []):
        if not defect.get("affected_semantic_keys") or not defect.get("observed_effect_code"):
            raise ValueError(f"{defect.get('id', '<unknown>')}: incomplete expected defect")
    return surface, defects


def _counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {kind: sum(row.get("kind") == kind for row in rows) for kind in KINDS}


def _control_parts(key: str) -> tuple[str, ...] | None:
    parts = tuple(key.split(":"))
    return parts if len(parts) == 9 and parts[:2] == ("control", "surface") else None


def _transition_parts(key: str) -> tuple[str, ...] | None:
    parts = tuple(key.split(":"))
    return parts if len(parts) == 12 and parts[0] == "transition" and parts[2:4] == ("control", "surface") else None


def _accepted_states(item: dict[str, Any], expected: str) -> set[str]:
    return {normalize_token(value) for value in item.get("accepted_surface_states", [expected])}


def _behavior_tokens(*values: str) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        tokens.update(normalize_token(value).split("-"))
    return tokens


def _canonical_viewport_key(value: str) -> str:
    return re.sub(r":(desktop|mobile|tablet)-[1-9][0-9]*(?=:)", r":\1", value)


def _matches_item(row: dict[str, Any], item: dict[str, Any]) -> bool:
    actual_key = _canonical_viewport_key(str(row.get("semantic_key", "")))
    accepted_keys = {
        _canonical_viewport_key(key)
        for key in {item["semantic_key"], *item.get("accepted_semantic_keys", [])}
    }
    if actual_key in accepted_keys:
        return True
    if row.get("kind") != item["kind"]:
        return False
    aliases = {normalize_token(item["identity"]), *(normalize_token(value) for value in item.get("accepted_aliases", []))}
    if item["kind"] == "feature":
        return normalize_token(str(row.get("semantic_key", "")).removeprefix("feature:")) in aliases
    if item["kind"] == "control":
        actual, expected = _control_parts(actual_key), _control_parts(item["semantic_key"])
        if actual is None or expected is None:
            return False
        identity = normalize_token(row.get("control_identity", {}).get("name", actual[6]))
        same_surface = (
            actual[2] == expected[2]
            and actual[4:6] == expected[4:6]
            and actual[3] in _accepted_states(item, expected[3])
        )
        exact_behavior = actual[7:] == expected[7:] and identity in aliases
        actual_behavior = _behavior_tokens(identity, actual[7], actual[8])
        expected_behavior = _behavior_tokens(expected[7], expected[8])
        equivalent_behavior = expected_behavior.issubset(actual_behavior)
        return same_surface and (exact_behavior or equivalent_behavior)
    if item["kind"] == "transition":
        actual, expected = _transition_parts(actual_key), _transition_parts(item["semantic_key"])
        if actual is None or expected is None:
            return False
        transition_aliases = {
            *aliases,
            normalize_token(item.get("control_identity", "")),
            normalize_token(expected[8]),
        }
        return (
            actual[4] == expected[4]
            and actual[6:8] == expected[6:8]
            and actual[5] in _accepted_states(item, expected[5])
            and actual[9] == expected[9]
            and normalize_token(actual[8]) in transition_aliases
        )
    return False


def _match_item_rows(item: dict[str, Any], rows: list[dict[str, Any]]) -> Match:
    """Prefer one canonical key; require uniqueness for every fallback."""
    canonical = _canonical_viewport_key(item["semantic_key"])
    keys = [_canonical_viewport_key(str(row.get("semantic_key", ""))) for row in rows]
    exact_indexes = [index for index, key in enumerate(keys) if key == canonical]
    exact = match_behavior(
        BehaviorNode(item["kind"], semantic_key=canonical),
        [BehaviorNode(rows[index].get("kind", ""), semantic_key=keys[index]) for index in exact_indexes],
    )
    if exact.status == "exact":
        return Match("exact", exact_indexes[exact.index])
    if exact.status == "ambiguous":
        return Match("ambiguous", candidate_indexes=tuple(exact_indexes[index] for index in exact.candidate_indexes))

    accepted = {_canonical_viewport_key(key) for key in item.get("accepted_semantic_keys", [])}
    accepted_indexes = [index for index, key in enumerate(keys) if key in accepted]
    if accepted_indexes:
        probe = match_behavior(
            BehaviorNode(item["kind"]),
            [BehaviorNode(rows[index].get("kind", "")) for index in accepted_indexes],
        )
        if probe.status == "equivalent":
            return Match("equivalent", accepted_indexes[probe.index])
        return Match("ambiguous", candidate_indexes=tuple(accepted_indexes[index] for index in probe.candidate_indexes))

    structural_indexes = [index for index, row in enumerate(rows) if _matches_item(row, item)]
    if not structural_indexes:
        return Match("missing")
    structural = match_behavior(
        BehaviorNode(item["kind"]),
        [BehaviorNode(rows[index].get("kind", "")) for index in structural_indexes],
    )
    if structural.status == "equivalent":
        return Match("equivalent", structural_indexes[structural.index])
    return Match("ambiguous", candidate_indexes=tuple(structural_indexes[index] for index in structural.candidate_indexes))


def _row_route(row: dict[str, Any]) -> str | None:
    match = re.search(r"(?:^|:)surface:([^:]+):", str(row.get("semantic_key", "")))
    return match.group(1) if match else None


def _extra_has_receipt(row: dict[str, Any], events: list[dict[str, Any]]) -> bool:
    expected = parse_semantic_key(row.get("semantic_key", ""), evidence_links=row.get("evidence_refs", ()))
    expected = BehaviorNode(
        kind=expected.kind,
        route=expected.route,
        role=expected.role,
        viewport=expected.viewport,
        control_identity=expected.control_identity,
        control_type=expected.control_type,
        evidence_links=expected.evidence_links,
    )
    status = row.get("status")
    types = {"blocked"} if status == "blocked" else {"avoided"} if status == "avoided" else (
        {"route_visit", "surface_spawn"} if expected.kind == "surface" else
        {"transition", "reload_reentry"} if expected.kind == "transition" else
        {"activation", "input"}
    )
    candidates = unique_receipt_nodes(event for event in events if event.get("event_type") in types)
    return bool(expected.evidence_links) and match_behavior(expected, candidates).status in {"exact", "equivalent"}


def compare_frontier(
    agent: dict[str, Any],
    oracle: dict[str, Any],
    defects: dict[str, Any],
    mode: str,
    *,
    receipt_events: list[dict[str, Any]] | None = None,
    receipt_expectations: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reasons: list[str] = []
    execution_failures: list[str] = []
    comparator_problems: list[str] = []
    rows = agent.get("rows") if isinstance(agent.get("rows"), list) else []
    by_key: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_key.setdefault(row.get("semantic_key", ""), []).append(row)
    duplicates = sorted(key for key, grouped in by_key.items() if key and len(grouped) > 1)
    if duplicates:
        reasons.append("duplicate semantic rows")

    required = {
        item["semantic_key"]: item
        for item in oracle["items"]
        if mode in item["required_modes"] and item.get("decoy_policy") != "negative_control"
    }
    missing: list[str] = []
    matched_rows: set[int] = set()
    matched_keys: dict[str, set[str]] = {}
    for key, item in required.items():
        match = _match_item_rows(item, rows)
        if match.status in {"missing", "key_mismatch"}:
            missing.append(key)
            continue
        if match.status == "ambiguous":
            comparator_problems.append(key)
            matched_rows.update(match.candidate_indexes)
            continue
        index = match.index
        assert index is not None
        row = rows[index]
        matched_keys[key] = {row["semantic_key"]}
        allowed = item["allowed_dispositions_by_mode"][mode]
        matched_rows.add(index)
        if row.get("status") not in allowed:
            reasons.append(f"invalid terminal disposition for {key}")
        if row.get("status") == "covered" and not row.get("evidence_refs"):
            reasons.append(f"covered row lacks required evidence for {key}")
        if item["kind"] == "transition" and (not row.get("before_state") or not row.get("after_state")):
            reasons.append(f"transition lacks before/after evidence for {key}")
        if receipt_events is not None and receipt_expectations is not None and item["kind"] in {"surface", "control", "transition"}:
            expectation = receipt_expectations.get(item["id"])
            if not isinstance(expectation, dict):
                comparator_problems.append(item["id"])
            else:
                expectation_match = verify_private_expectation(expectation, receipt_events)
                claim_match = verify_execution_claim(item, row, receipt_events)
                if "ambiguous" in {expectation_match.status, claim_match.status}:
                    comparator_problems.append(f"receipt:{key}")
                elif expectation_match.status != "supported" or claim_match.status != "supported":
                    execution_failures.append(key)
                    reasons.append(f"private receipt does not support execution claim for {key}")
    if missing:
        reasons.append(f"material oracle misses: {len(missing)}")

    actual_counts = _counts(rows)
    if agent.get("summary") != actual_counts:
        reasons.append("summary/row count drift")
    if agent.get("html_closure_state") != agent.get("closure_state"):
        reasons.append("JSON/HTML closure contradiction")

    observed_findings = agent.get("findings") if isinstance(agent.get("findings"), list) else []
    defect_findings = [finding for finding in observed_findings if finding.get("action", "Fix") == "Fix"]
    expected_defects = [defect for defect in defects.get("defects", []) if mode in defect["required_modes"]]

    def matches(finding: dict[str, Any], defect: dict[str, Any]) -> bool:
        expected_keys = set(defect["affected_semantic_keys"])
        actual_keys = set(finding.get("affected_semantic_keys", []))
        accepted_affected = set(defect.get("accepted_affected_semantic_keys", []))
        lineage_matches = all(
            bool(actual_keys & ({key} | matched_keys.get(key, set()) | accepted_affected))
            for key in expected_keys
        )
        return (
            lineage_matches
            and normalize_token(finding.get("observed_effect_code", ""))
            in {normalize_token(defect["observed_effect_code"]), *(normalize_token(alias) for alias in defect.get("accepted_observation_aliases", []))}
            and bool(finding.get("evidence_refs"))
        )

    edges = {
        defect_index: [
            finding_index for finding_index, finding in enumerate(defect_findings)
            if matches(finding, defect)
        ]
        for defect_index, defect in enumerate(expected_defects)
    }
    finding_owner: dict[int, int] = {}

    def assign(defect_index: int, seen: set[int]) -> bool:
        for finding_index in edges[defect_index]:
            if finding_index in seen:
                continue
            seen.add(finding_index)
            owner = finding_owner.get(finding_index)
            if owner is None or assign(owner, seen):
                finding_owner[finding_index] = defect_index
                return True
        return False

    for defect_index in range(len(expected_defects)):
        assign(defect_index, set())
    assigned_defects = set(finding_owner.values())
    assigned_findings = set(finding_owner)
    missed_defects = [
        defect["id"] for index, defect in enumerate(expected_defects)
        if index not in assigned_defects
    ]
    if missed_defects:
        reasons.append(f"expected defect misses: {len(missed_defects)}")
    unexpected_findings = [
        finding for index, finding in enumerate(defect_findings)
        if index not in assigned_findings
    ]

    known_features = set(oracle.get("supporting_features", []))
    known_routes = set(oracle.get("supporting_routes", []))
    unmatched = [row for index, row in enumerate(rows) if index not in matched_rows and row.get("kind") != "intent" and row.get("material", True)]
    valid_extras: list[dict[str, Any]] = []
    unexpected: list[dict[str, Any]] = []
    for row in unmatched:
        key = row.get("semantic_key", "")
        explicit_support = key in known_features or (row.get("kind") == "surface" and _row_route(row) in known_routes)
        receipt_support = receipt_events is not None and _extra_has_receipt(row, receipt_events)
        if explicit_support or receipt_support:
            valid_extras.append(row)
        else:
            unexpected.append(row)
    if reasons:
        status = "FAIL"
    elif comparator_problems or unexpected or unexpected_findings:
        status = "REVIEW_REQUIRED"
    else:
        status = "PASS"
    return {
        "packet_version": "shipworthy-gauntlet-comparison-v1",
        "mode": mode,
        "status": status,
        "agent_claimed_closure": agent.get("closure_state"),
        "oracle_derived_closure": "closed_multi_source" if status == "PASS" else "incomplete",
        "reasons": reasons,
        "missing_semantic_keys": missing,
        "missed_defect_ids": missed_defects,
        "duplicate_semantic_keys": duplicates,
        "unexpected_rows": unexpected,
        "unexpected_findings": unexpected_findings,
        "diagnostics": {
            "A_material_discovery_miss": missing,
            "B_execution_proof_lineage_failure": execution_failures,
            "C_normalization_or_comparator_problem": comparator_problems,
            "D_valid_extra": [row.get("semantic_key", "") for row in valid_extras],
            "E_unsupported_or_false_positive": [row.get("semantic_key", "") for row in unexpected] + [finding.get("observed_effect_code", "") for finding in unexpected_findings],
        },
        "counts": actual_counts,
    }

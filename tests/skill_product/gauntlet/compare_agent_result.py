#!/usr/bin/env python3
"""Pure semantic comparison for the repository-only Gauntlet."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


NORMALIZATION_VERSION = "shipworthy-semantic-v1"
METHOD_VERSION = "shipworthy-methods-v1"
KINDS = ("feature", "surface", "control", "transition")
TERMINAL = frozenset({"covered", "avoided", "blocked", "missing", "unavailable"})


def normalize_token(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value)).strip().casefold()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def normalize_route(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value)).strip()
    parsed = urlsplit(text if "://" in text else "https://local.invalid/" + text.lstrip("/"))
    path = re.sub(r"/+", "/", parsed.path or "/").casefold()
    return path.rstrip("/") or "/"


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


def _matches_item(row: dict[str, Any], item: dict[str, Any]) -> bool:
    if row.get("semantic_key") in {item["semantic_key"], *item.get("accepted_semantic_keys", [])}:
        return True
    if row.get("kind") != item["kind"]:
        return False
    aliases = {normalize_token(item["identity"]), *(normalize_token(value) for value in item.get("accepted_aliases", []))}
    if item["kind"] == "feature":
        return normalize_token(str(row.get("semantic_key", "")).removeprefix("feature:")) in aliases
    if item["kind"] == "control":
        actual, expected = _control_parts(str(row.get("semantic_key", ""))), _control_parts(item["semantic_key"])
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
        actual, expected = _transition_parts(str(row.get("semantic_key", ""))), _transition_parts(item["semantic_key"])
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


def _row_route(row: dict[str, Any]) -> str | None:
    match = re.search(r"(?:^|:)surface:([^:]+):", str(row.get("semantic_key", "")))
    return match.group(1) if match else None


def compare_frontier(agent: dict[str, Any], oracle: dict[str, Any], defects: dict[str, Any], mode: str) -> dict[str, Any]:
    reasons: list[str] = []
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
        grouped = [(index, row) for index, row in enumerate(rows) if _matches_item(row, item)]
        if not grouped:
            missing.append(key)
            continue
        matched_keys[key] = {candidate["semantic_key"] for _, candidate in grouped}
        allowed = item["allowed_dispositions_by_mode"][mode]
        index, row = next(
            ((candidate_index, candidate) for candidate_index, candidate in grouped if candidate.get("status") in allowed),
            grouped[0],
        )
        matched_rows.update(candidate_index for candidate_index, _ in grouped)
        if row.get("status") not in allowed:
            reasons.append(f"invalid terminal disposition for {key}")
        if row.get("status") == "covered" and not row.get("evidence_refs"):
            reasons.append(f"covered row lacks required evidence for {key}")
        if item["kind"] == "transition" and (not row.get("before_state") or not row.get("after_state")):
            reasons.append(f"transition lacks before/after evidence for {key}")
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
        lineage_matches = all(
            bool(actual_keys & ({key} | matched_keys.get(key, set())))
            for key in expected_keys
        )
        return (
            lineage_matches
            and normalize_token(finding.get("observed_effect_code", ""))
            in {normalize_token(defect["observed_effect_code"]), *(normalize_token(alias) for alias in defect.get("accepted_observation_aliases", []))}
            and bool(finding.get("evidence_refs"))
        )

    missed_defects = [
        defect["id"] for defect in expected_defects
        if not any(matches(finding, defect) for finding in defect_findings)
    ]
    if missed_defects:
        reasons.append(f"expected defect misses: {len(missed_defects)}")
    unexpected_findings = [
        finding for finding in defect_findings
        if not any(matches(finding, defect) for defect in expected_defects)
    ]

    known_routes = set(oracle.get("supporting_routes", []))
    known_features = set(oracle.get("supporting_features", []))
    unexpected = [
        row for index, row in enumerate(rows)
        if index not in matched_rows
        and row.get("kind") != "intent"
        and row.get("material", True)
        and _row_route(row) not in known_routes
        and row.get("semantic_key") not in known_features
        and ":not-found:" not in str(row.get("semantic_key", ""))
    ]
    if reasons:
        status = "FAIL"
    elif unexpected or unexpected_findings:
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
        "counts": actual_counts,
    }

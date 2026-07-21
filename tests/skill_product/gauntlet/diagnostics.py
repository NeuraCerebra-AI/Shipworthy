#!/usr/bin/env python3
"""Categorical A/B/C/D/E behavioral comparison diagnostics."""

from __future__ import annotations

from typing import Iterable

from .behavior_graph import BehaviorNode, match_behavior


def _identity(node: BehaviorNode, index: int) -> str:
    return node.semantic_key or f"structural:{node.kind}:{node.route}:{node.control_identity}:{index}"


def classify_comparison(
    expected: Iterable[BehaviorNode],
    reported: Iterable[BehaviorNode],
    receipt: Iterable[BehaviorNode],
    *,
    supported_extra_keys: set[str],
    finding_keys: set[str],
) -> dict:
    expected, reported, receipt = list(expected), list(reported), list(receipt)
    discovery_misses: list[str] = []
    execution_failures: list[str] = []
    comparator_problems: list[str] = []
    valid_extras: list[str] = []
    expected_report_indexes: set[int] = set()

    for index, item in enumerate(expected):
        report_match = match_behavior(item, reported)
        identity = _identity(item, index)
        if report_match.status in {"missing", "key_mismatch"}:
            discovery_misses.append(identity)
            continue
        if report_match.status == "ambiguous":
            comparator_problems.append(f"report:{identity}")
            continue
        report_index = report_match.index
        assert report_index is not None
        expected_report_indexes.add(report_index)
        claim = reported[report_index]
        receipt_match = match_behavior(claim, receipt)
        if receipt_match.status == "ambiguous":
            comparator_problems.append(f"receipt:{identity}")
        elif receipt_match.status in {"missing", "key_mismatch"} or not claim.evidence_links:
            execution_failures.append(identity)

    for index, item in enumerate(reported):
        if index in expected_report_indexes:
            continue
        identity = _identity(item, index)
        if item.semantic_key in supported_extra_keys and match_behavior(item, receipt).status in {"exact", "equivalent"}:
            valid_extras.append(identity)

    expected_keys = {item.semantic_key for item in expected if item.semantic_key}
    false_findings = sorted(key for key in finding_keys if key not in expected_keys and key not in supported_extra_keys)
    if discovery_misses or execution_failures or false_findings:
        status = "FAIL"
    elif comparator_problems:
        status = "REVIEW_REQUIRED"
    else:
        status = "PASS"
    return {
        "status": status,
        "A_material_discovery_miss": sorted(discovery_misses),
        "B_execution_proof_lineage_failure": sorted(execution_failures),
        "C_normalization_or_comparator_problem": sorted(comparator_problems),
        "D_valid_extra": sorted(valid_extras),
        "E_unsupported_finding": false_findings,
    }

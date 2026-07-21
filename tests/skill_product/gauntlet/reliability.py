#!/usr/bin/env python3
"""Per-run reliability metrics without cross-run evidence aggregation."""

from __future__ import annotations

import statistics
from typing import Any


class ReliabilityError(ValueError):
    pass


def _recall(value: Any, field: str) -> float:
    if not isinstance(value, dict):
        raise ReliabilityError(f"{field} must be an object")
    found, total = value.get("found"), value.get("total")
    if not isinstance(found, int) or not isinstance(total, int) or total < 0 or found < 0 or found > total:
        raise ReliabilityError(f"{field} counts are invalid")
    return 1.0 if total == 0 else round(found / total, 4)


def score_run(packet: dict) -> dict:
    if not isinstance(packet, dict) or not packet.get("run_id") or not packet.get("revision"):
        raise ReliabilityError("run identity and revision are required")
    sources = packet.get("source_run_ids")
    if sources != [packet["run_id"]]:
        raise ReliabilityError("cross-run aggregation is forbidden")
    defects = packet.get("defects") if isinstance(packet.get("defects"), dict) else {}
    blocker_recall = _recall(
        {"found": defects.get("release_blocking_found"), "total": defects.get("release_blocking_total")},
        "release-blocking defects",
    )
    duration = packet.get("duration_seconds")
    attempts = packet.get("attempt_count")
    artifact_bytes = packet.get("artifact_bytes")
    if not isinstance(duration, (int, float)) or duration < 0 or not isinstance(attempts, int) or attempts < 0 or not isinstance(artifact_bytes, int) or artifact_bytes < 0:
        raise ReliabilityError("run cost fields are invalid")
    return {
        "run_id": packet["run_id"],
        "revision": packet["revision"],
        "mode": packet.get("mode", ""),
        "material_discovery_recall": _recall(packet.get("discovery"), "discovery"),
        "execution_recall": _recall(packet.get("execution"), "execution"),
        "defect_recall": _recall(defects, "defects"),
        "release_blocking_defect_recall": blocker_recall,
        "false_exhaustive_closure": packet.get("false_exhaustive_closure") is True,
        "artifact_integrity": packet.get("artifact_integrity") is True,
        "false_positive_count": int(packet.get("false_positive_count", 0)),
        "valid_extra_count": int(packet.get("valid_extra_count", 0)),
        "cost": {"duration_seconds": float(duration), "attempt_count": attempts, "artifact_bytes": artifact_bytes},
    }


def _distribution(scored: list[dict], field: str) -> dict[str, float]:
    values = [run[field] for run in scored]
    return {"median": round(float(statistics.median(values)), 4), "worst": min(values)}


def summarize_runs(packets: list[dict]) -> dict:
    if len(packets) != 5:
        raise ReliabilityError("exactly five independent runs are required")
    scored = [score_run(packet) for packet in packets]
    if len({run["run_id"] for run in scored}) != 5:
        raise ReliabilityError("run identifiers must be unique")
    if len({run["revision"] for run in scored}) != 1:
        raise ReliabilityError("all runs must use the same revision")
    discovery = _distribution(scored, "material_discovery_recall")
    execution = _distribution(scored, "execution_recall")
    defects = _distribution(scored, "defect_recall")
    false_closure_rate = sum(run["false_exhaustive_closure"] for run in scored) / 5
    integrity_rate = sum(run["artifact_integrity"] for run in scored) / 5
    blocker_found = sum(packet["defects"]["release_blocking_found"] for packet in packets)
    blocker_total = sum(packet["defects"]["release_blocking_total"] for packet in packets)
    blocker_recall = 1.0 if blocker_total == 0 else round(blocker_found / blocker_total, 4)
    false_positives = sum(run["false_positive_count"] for run in scored)
    classified = false_positives + sum(packet["defects"]["found"] for packet in packets) + sum(run["valid_extra_count"] for run in scored)
    false_positive_rate = 0.0 if classified == 0 else round(false_positives / classified, 4)
    failed: list[str] = []
    if discovery["median"] < .9: failed.append("discovery-median-below-0.90")
    if discovery["worst"] < .8: failed.append("discovery-worst-below-0.80")
    if false_closure_rate: failed.append("false-exhaustive-closure")
    if integrity_rate != 1: failed.append("artifact-integrity-not-5-of-5")
    if blocker_recall != 1: failed.append("release-blocker-missed")
    return {
        "release_gate": "FAIL" if failed else "PASS",
        "failed_gates": failed,
        "material_discovery_recall": discovery,
        "execution_recall": execution,
        "defect_recall": defects,
        "false_exhaustive_closure_rate": false_closure_rate,
        "artifact_integrity_rate": integrity_rate,
        "release_blocking_defect_recall": blocker_recall,
        "false_positive_rate": false_positive_rate,
        "runtime_evidence_cost": {
            "duration_seconds": _distribution([{"value": run["cost"]["duration_seconds"]} for run in scored], "value"),
            "attempt_count": _distribution([{"value": run["cost"]["attempt_count"]} for run in scored], "value"),
            "artifact_bytes": _distribution([{"value": run["cost"]["artifact_bytes"]} for run in scored], "value"),
        },
        "runs": scored,
    }

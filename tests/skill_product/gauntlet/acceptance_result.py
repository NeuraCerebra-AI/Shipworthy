"""Schema-bounded atomic acceptance-result writing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


EXIT_CODES = {"PASS": 0, "FAIL": 1, "NOT_PROVEN": 2, "REVIEW_REQUIRED": 3}


def validate_acceptance_result(result: dict[str, Any]) -> None:
    required = {
        "schema_version", "status", "mode", "native_dispatch_status",
        "native_agent_id", "failure_code", "diagnostic", "comparison_status",
        "oracle_blindness", "filesystem_containment", "artifacts",
    }
    missing = required - set(result)
    if missing:
        raise ValueError(f"missing acceptance field: {sorted(missing)[0]}")
    if result["schema_version"] != "shipworthy-gauntlet-acceptance-v1":
        raise ValueError("invalid acceptance schema version")
    if result["status"] not in EXIT_CODES:
        raise ValueError("invalid acceptance status")
    if result["native_dispatch_status"] not in {"completed", "unavailable", "failed", "timeout", "internal"}:
        raise ValueError("invalid dispatch status")
    if not isinstance(result["artifacts"], dict):
        raise ValueError("artifacts must be an object")


def _fallback() -> dict[str, Any]:
    return {
        "schema_version": "shipworthy-gauntlet-acceptance-v1",
        "status": "FAIL", "mode": "internal", "native_dispatch_status": "internal",
        "native_agent_id": "", "failure_code": "internal-invalid-result",
        "diagnostic": "acceptance result draft failed validation",
        "comparison_status": "FAIL", "oracle_blindness": "PROCEDURAL_ONLY",
        "filesystem_containment": "NOT_PROVEN", "artifacts": {},
    }


def atomic_final_result(output: Path, draft: dict[str, Any]) -> dict[str, Any]:
    try:
        validate_acceptance_result(draft)
        final = draft
    except (TypeError, ValueError):
        final = _fallback()
    validate_acceptance_result(final)
    temporary = Path(output) / ".acceptance-result.json.tmp"
    temporary.write_text(json.dumps(final, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(Path(output) / "acceptance-result.json")
    return final

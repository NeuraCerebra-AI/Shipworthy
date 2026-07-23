#!/usr/bin/env python3
"""
Shipworthy — render a structured readiness audit into a self-contained HTML report.

Usage:
    python3 render_report.py [input.json] [output.html]

Produces ONE self-contained file: inline CSS, system fonts, and no network calls.
Default output has no JavaScript; --interactive adds inline no-network controls.
Every text field is HTML-escaped. Legacy input degrades gracefully; canonical
frontier input fails closed on broken lineage, evidence, digest, or checkpoint data.
"""
import sys, json, html, datetime, re, os, tempfile, hashlib
sys.dont_write_bytecode = True
MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_CHECKPOINT_BYTES = 256 * 1024
CHECKPOINT_REQUIRED = {
    "target_name", "lanes", "mode", "multi_agent_authorization", "frontend_path_walk_performed",
    "frontend_tool", "runtime_target", "path_walk_status", "verifier", "omitted",
    "ledger_path", "evidence_locations", "exhaustion_status",
    "audit_status", "goal_mode_status", "goal_completion_status",
    "raw_lane_output_paths", "raw_verifier_output_paths", "control_census_paths",
    "zero_yield_pass_ids", "evidence_debt_actions",
    "recovery_status", "recovery_attempts", "recovery_receipt_paths",
    "browser_failover_status", "browser_failover_receipt_paths",
}
AUDIT_STATUSES = {"active", "complete", "blocked", "user_stopped"}
GOAL_COMPLETION_STATUSES = {"active", "complete", "blocked", "user_stopped", "not_applicable"}
BROWSER_FAILOVER_STATUSES = {"not_needed", "active", "succeeded", "blocked", "user_stopped"}
RECOVERY_STATUSES = {"not_needed", "active", "succeeded", "blocked", "user_stopped"}
CONTROL_CENSUS_METHODS = {"runtime_structural_inventory", "static_implementation_inventory"}


def recovery_projection(declared_status, attempts):
    """Validate bounded recovery attempts and derive the human report projection."""
    if declared_status not in RECOVERY_STATUSES:
        raise ValueError("recovery_status is not canonical")
    if not isinstance(attempts, list) or not all(isinstance(item, dict) for item in attempts):
        raise ValueError("recovery_attempts must be an array of objects")
    if declared_status == "not_needed" and attempts:
        raise ValueError("recovery_status not_needed cannot retain attempts")
    latest_by_recovery = {}
    candidate_keys = set()
    recovered_paths = set()
    for index, attempt in enumerate(attempts):
        required = {
            "recovery_id", "status", "failed_binding_id", "method_family", "binding_id",
            "authorized", "available", "applicable", "safe", "attempt_count", "result",
            "continuity_before_attempt", "continuity_before_resumption",
            "resumed_path_keys", "remaining_debt_ids", "evidence_refs",
            "cleanup_result", "transient_retry_performed", "path_outcomes",
            "inventory_refresh", "new_available_method_ids",
            "controller_id", "verifier_id", "verifier_debt",
            "driven_semantic_keys", "assertion_ids", "assertion_evidence_refs",
            "independence_debt_ids",
        }
        if not required.issubset(attempt):
            raise ValueError(f"recovery attempt[{index}] is incomplete")
        status = attempt.get("status")
        if status not in RECOVERY_STATUSES - {"not_needed"}:
            raise ValueError(f"recovery attempt[{index}] status is not canonical")
        recovery_id = attempt.get("recovery_id")
        if not isinstance(recovery_id, str) or not recovery_id.strip():
            raise ValueError(f"recovery attempt[{index}] recovery_id is invalid")
        latest_by_recovery[recovery_id] = attempt
        candidate_key = (recovery_id, attempt.get("method_family"), attempt.get("binding_id"))
        if candidate_key in candidate_keys:
            raise ValueError(f"recovery attempt[{index}] duplicates a method/binding candidate")
        candidate_keys.add(candidate_key)
        for field in ("authorized", "available", "applicable", "safe",
                      "continuity_before_attempt", "continuity_before_resumption",
                      "transient_retry_performed", "inventory_refresh", "verifier_debt"):
            if not isinstance(attempt.get(field), bool):
                raise ValueError(f"recovery attempt[{index}] {field} must be boolean")
        count = attempt.get("attempt_count")
        if not isinstance(count, int) or count < 0 or count > 1:
            raise ValueError(f"recovery attempt[{index}] exceeds the one-attempt budget")
        if (
            attempt["authorized"] and attempt["available"]
            and attempt["applicable"] and attempt["safe"]
            and count == 0 and declared_status == "blocked"
        ):
            raise ValueError("recovery must remain active while an applicable safe authorized method is unattempted")
        if not isinstance(attempt.get("cleanup_result"), str) or not attempt["cleanup_result"].strip():
            raise ValueError(f"recovery attempt[{index}] cleanup_result is invalid")
        path_outcomes = attempt.get("path_outcomes")
        if (
            not isinstance(path_outcomes, list) or not path_outcomes
            or not all(
                isinstance(item, dict)
                and isinstance(item.get("semantic_key"), str)
                and item.get("status") == status
                for item in path_outcomes
            )
        ):
            raise ValueError(f"recovery attempt[{index}] path outcomes are missing or heterogeneous")
        new_methods = attempt.get("new_available_method_ids")
        if not isinstance(new_methods, list) or not all(
            isinstance(item, str) and item.strip() for item in new_methods
        ):
            raise ValueError(f"recovery attempt[{index}] inventory delta is invalid")
        if new_methods and declared_status != "active":
            raise ValueError("newly available recovery methods require recovery to remain active")
        if status == "blocked" and not attempt.get("inventory_refresh"):
            raise ValueError("blocked recovery requires a final inventory refresh")
        result = attempt.get("result")
        if result == "recovered":
            if attempt.get("method_family") == "supporting_evidence":
                raise ValueError("supporting evidence cannot recover required frontend execution")
            if attempt.get("binding_id") == attempt.get("failed_binding_id"):
                raise ValueError("recovered frontend execution requires an independent binding")
            if not attempt.get("continuity_before_attempt") or not attempt.get("continuity_before_resumption"):
                raise ValueError("recovery requires continuity before the attempt and resumption")
            resumed = attempt.get("resumed_path_keys")
            if not isinstance(resumed, list) or not resumed:
                raise ValueError("successful recovery requires resumed paths")
            if attempt.get("remaining_debt_ids"):
                raise ValueError("successful recovery cannot retain affected recovery debt")
            if (
                not isinstance(attempt.get("controller_id"), str)
                or not isinstance(attempt.get("verifier_id"), str)
                or not attempt["verifier_id"].strip()
                or attempt["verifier_id"] == attempt["controller_id"]
                or attempt.get("verifier_debt")
            ):
                raise ValueError("successful recovery requires a fresh independent verifier")
            if attempt.get("method_family") == "target_owned_e2e" and not (
                attempt.get("driven_semantic_keys")
                and attempt.get("assertion_ids")
                and attempt.get("assertion_evidence_refs")
                and set(attempt["driven_semantic_keys"]).issubset(set(resumed))
            ):
                raise ValueError("target-owned E2E recovery requires driven semantic paths and assertion evidence")
            if attempt.get("method_family") in {
                "reassigned_frontend_driver", "sequential_frontend_driver"
            } and not attempt.get("independence_debt_ids"):
                raise ValueError("reassigned or sequential recovery must record independence debt")
            recovered_paths.update(resumed)
        for field in (
            "resumed_path_keys", "remaining_debt_ids", "evidence_refs",
            "driven_semantic_keys", "assertion_ids", "assertion_evidence_refs",
            "independence_debt_ids",
        ):
            if not isinstance(attempt.get(field), list) or not all(
                isinstance(item, str) and item.strip() for item in attempt[field]
            ):
                raise ValueError(f"recovery attempt[{index}] {field} is invalid")
    terminal = list(latest_by_recovery.values())
    terminal_statuses = [item.get("status") for item in terminal]
    derived = (
        "user_stopped" if "user_stopped" in terminal_statuses
        else "active" if "active" in terminal_statuses
        else "blocked" if any(
            item.get("status") == "blocked" or item.get("remaining_debt_ids")
            for item in terminal
        )
        else "succeeded" if terminal and all(
            item.get("result") == "recovered" for item in terminal
        )
        else "blocked" if terminal
        else "not_needed"
    )
    if declared_status != derived:
        raise ValueError(f"recovery_status {declared_status} does not match derived {derived}")
    return {
        "status": derived,
        "attempt_count": sum(item.get("attempt_count", 0) for item in attempts),
        "recovered_paths": len(recovered_paths),
        "remaining_debt": len({
            debt for item in terminal for debt in item.get("remaining_debt_ids", [])
        }),
    }

def atomic_write_text(path, value):
    destination = os.path.abspath(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=os.path.dirname(destination), prefix="." + os.path.basename(destination) + ".", delete=False) as handle:
            temporary = handle.name
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)

COV = {
    "covered": "#34D399", "sampled": "#3B82F6", "blocked": "#F59E0B",
    "avoided": "#9F5B6B", "inferred": "#38BDF8", "missing": "#F43F5E",
    "out_of_scope": "#64748B", "evidence_debt": "#3A4763",
    "debt": "#3A4763",
}
COV_LABEL = {
    "covered": "Tried + evidenced", "sampled": "Spot-checked", "blocked": "Blocked",
    "avoided": "Skipped for safety", "inferred": "Inferred", "missing": "Missing",
    "out_of_scope": "Out of scope", "evidence_debt": "Proof missing",
    "debt": "Proof missing",
}
SECTION = {
    "clear_before_ship": ("#F43F5E", "Clear Before Ship", "tier-clear-before-ship"),
    "fix_next": ("#F59E0B", "Fix Next", "tier-fix-next"),
    "not_proven_not_tested": ("#38BDF8", "Not Proven / Not Tested", "tier-not-proven"),
    "passed_keep": ("#34D399", "Passed / Keep", "tier-passed-keep"),
}
SECTION_ORDER = ["clear_before_ship", "fix_next", "not_proven_not_tested", "passed_keep"]
SEV_ALIAS = {
    "blocker": "blocker", "critical": "blocker", "p0 blocker": "blocker", "p0": "blocker",
    "strong": "strong", "major": "strong", "high": "strong", "p1 major": "strong", "p1": "strong",
    "provisional": "provisional", "moderate": "provisional", "medium": "provisional", "p2 moderate": "provisional", "p2": "provisional",
    "info": "info", "note": "info", "minor": "info", "low": "info", "p3 minor": "info", "p3": "info",
    "unscored": "info", "hypothesis": "info", "preserve note": "info",
}
SECTION_ALIAS = {
    "clear before ship": "clear_before_ship",
    "clear": "clear_before_ship",
    "fix before ship": "clear_before_ship",
    "must fix before ship": "clear_before_ship",
    "blocks readiness": "clear_before_ship",
    "release blocker": "clear_before_ship",
    "blocker": "clear_before_ship",
    "critical": "clear_before_ship",
    "p0 blocker": "clear_before_ship",
    "p0": "clear_before_ship",
    "fix next": "fix_next",
    "should fix": "fix_next",
    "quality issue": "fix_next",
    "broken or risky workflow": "fix_next",
    "major": "fix_next",
    "high": "fix_next",
    "p1 major": "fix_next",
    "p1": "fix_next",
    "moderate": "fix_next",
    "medium": "fix_next",
    "p2 moderate": "fix_next",
    "p2": "fix_next",
    "provisional": "fix_next",
    "not proven not tested": "not_proven_not_tested",
    "not proven / not tested": "not_proven_not_tested",
    "not proven": "not_proven_not_tested",
    "not tested": "not_proven_not_tested",
    "needs proof": "not_proven_not_tested",
    "proof missing": "not_proven_not_tested",
    "evidence debt": "not_proven_not_tested",
    "skipped": "not_proven_not_tested",
    "unknown": "not_proven_not_tested",
    "maybe": "not_proven_not_tested",
    "hypothesis": "not_proven_not_tested",
    "info": "not_proven_not_tested",
    "note": "not_proven_not_tested",
    "minor": "not_proven_not_tested",
    "low": "not_proven_not_tested",
    "p3 minor": "not_proven_not_tested",
    "p3": "not_proven_not_tested",
    "unscored": "not_proven_not_tested",
    "passed keep": "passed_keep",
    "passed / keep": "passed_keep",
    "passed": "passed_keep",
    "keep": "passed_keep",
    "passed in this run": "passed_keep",
    "working": "passed_keep",
    "worked": "passed_keep",
    "strong": "passed_keep",
}
ACTION_ALIAS = {
    "fix": "Fix", "prove": "Prove", "decide": "Decide", "skip": "Skip", "keep": "Keep",
    "preserve": "Keep", "investigate": "Prove", "verify": "Prove", "defer": "Decide",
}
PROOF_ALIAS = {
    "confirmed": "Confirmed", "direct": "Confirmed", "observed": "Confirmed", "reproduced": "Confirmed",
    "partial": "Partial", "strong": "Partial", "provisional": "Partial", "some proof": "Partial",
    "inferred": "Inferred", "hypothesis": "Inferred", "assumed": "Inferred",
    "not tested": "Not tested", "not_tested": "Not tested", "untested": "Not tested",
    "skipped": "Not tested", "blocked": "Not tested", "unknown": "Not tested",
}
VERDICT = {
    "NOT READY":        ("#2A1220", "#7F2740", "#FB7185"),
    "READY WITH RISKS": ("#241A05", "#7A5A16", "#FBBF24"),
    "CONDITIONAL":      ("#241A05", "#7A5A16", "#FBBF24"),
    "READY":            ("#0B241A", "#1E6B4E", "#34D399"),
}
VERDICT_NEUTRAL = ("#141A28", "#2A3654", "#AEBAD4")  # unknown verdict -> neutral, not alarming

V1_SEVERITY = {
    "P0 Blocker": "blocker", "P1 Major": "strong",
    "P2 Moderate": "provisional", "P3 Minor": "info", "Unscored": "info",
}
V1_VERDICT = {
    "ready": "READY", "conditionally_ready": "CONDITIONAL",
    "not_ready": "NOT READY", "cannot_determine": "NOT READY",
}
CLOSURE_STATES = {"closed_multi_source", "incomplete", "single_source", "blocked", "static_only"}
PARENT_KIND = {"feature": "intent", "surface": "feature", "control": "surface", "transition": "control"}

def _semantic_digest(keys):
    keys = sorted(key for key in keys if isinstance(key, str))
    return hashlib.sha256(json.dumps(keys, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()

def _frontier_digest(rows):
    return _semantic_digest(row.get("semantic_key") for row in rows if isinstance(row, dict))


AFFORDANCE_CLASSES = {
    "functional", "informational", "unavailable", "false_affordance", "rejected_with_proof", "out_of_scope",
}
CANONICAL_ARTIFACT_NAMES = frozenset({
    "readiness-ledger.json", "report-input.json", "orchestration-checkpoint.json", "readiness-report.html",
})


def validate_wave_contract(checkpoint):
    """Require the minimum independent verified waves for a current full run."""
    if not isinstance(checkpoint, dict) or checkpoint.get("run_scope") != "full":
        return {"required": False}
    wave_ids = checkpoint.get("verified_wave_ids")
    certificates = checkpoint.get("wave_certificate_paths")
    if not isinstance(wave_ids, list) or len(wave_ids) < 3 or len(set(wave_ids)) != len(wave_ids):
        raise ValueError("full Shipworthy runs require three verified waves with distinct wave IDs")
    if not isinstance(certificates, list) or len(certificates) != len(wave_ids):
        raise ValueError("three verified waves require one verifier certificate per wave")
    if not all(isinstance(item, str) and item.strip() for item in certificates):
        raise ValueError("three verified waves require retained verifier certificate paths")
    return {"required": True, "wave_ids": tuple(wave_ids), "certificate_paths": tuple(certificates)}


def validate_input_mode(data):
    """Distinguish explicit historical legacy import from a current full run."""
    if not isinstance(data, dict):
        return "unknown"
    source = data.get("source_ledger") if isinstance(data.get("source_ledger"), dict) else data
    input_format = str(data.get("input_format") or source.get("input_format") or "").strip().lower()
    run_scope = data.get("run_scope") or source.get("run_scope")
    if input_format.startswith("legacy/"):
        if run_scope == "full" and data.get("import_mode") != "historical" and source.get("import_mode") != "historical":
            raise ValueError("legacy input is only valid through an explicit historical import")
        return "historical_import" if data.get("import_mode") == "historical" or source.get("import_mode") == "historical" else "legacy"
    return "canonical" if data.get("schema_name", "").startswith("shipworthy/") else "unknown"


def validate_discovery_exhaustion(frontier):
    """Reject closure while discovery still yields material paths."""
    if not isinstance(frontier, dict):
        raise ValueError("frontier must be an object")
    passes = frontier.get("discovery_passes") or []
    if frontier.get("closure_state") == "closed_multi_source":
        # Earlier passes may legitimately grow the frontier.  Only the final
        # closure attempt is incompatible with a positive yield.
        if any(item.get("new_semantic_keys") for item in passes[-2:] if isinstance(item, dict)):
            raise ValueError("positive discovery yield keeps the frontier open")
        quiet = [
            item for item in passes[-2:]
            if isinstance(item, dict) and item.get("new_semantic_keys") == []
        ]
        if len(quiet) < 2 or len({item.get("method_family") for item in quiet}) < 2:
            raise ValueError("closed discovery requires two distinct zero-yield method families")
    return frontier.get("closure_state")


def reconcile_raw_discoveries(ledger):
    """Ensure every material raw discovery has a retained canonical disposition."""
    if not isinstance(ledger, dict):
        raise ValueError("raw observation reconciliation requires a ledger object")
    frontier = ledger.get("path_frontier") or {}
    row_keys = {
        row.get("semantic_key") for row in frontier.get("rows", [])
        if isinstance(row, dict) and isinstance(row.get("semantic_key"), str)
    }
    finding_keys = {
        key for finding in ledger.get("findings", []) if isinstance(finding, dict)
        for key in (finding.get("affected_semantic_keys") or [])
        if isinstance(key, str)
    }
    dispositions = {
        item.get("semantic_key") for item in (
            ledger.get("rejected_discoveries", [])
            + ledger.get("out_of_scope_discoveries", [])
            + ledger.get("evidence_debt_discoveries", [])
        ) if isinstance(item, dict) and isinstance(item.get("semantic_key"), str)
    }
    unresolved = []
    for item in ledger.get("raw_discoveries", []) or []:
        if not isinstance(item, dict) or not item.get("observation_id"):
            unresolved.append("unnamed raw observation")
            continue
        key = item.get("semantic_key")
        if key not in row_keys and key not in finding_keys and key not in dispositions:
            unresolved.append(str(item.get("observation_id")))
    if unresolved:
        raise ValueError("raw observation reconciliation dropped: " + ", ".join(unresolved[:8]))
    return True


def validate_affordance_census(census):
    """Classify action-signalling surfaces, including non-control false affordances."""
    entries = census.get("entries") if isinstance(census, dict) else None
    if not isinstance(entries, list):
        raise ValueError("apparent affordance census requires entries")
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not entry.get("affordance_id"):
            raise ValueError(f"apparent affordance census entry[{index}] is incomplete")
        if entry.get("classification") not in AFFORDANCE_CLASSES:
            raise ValueError(f"apparent affordance entry[{index}] requires a disposition")
        if entry.get("action_signaling") is True and not entry.get("evidence_refs"):
            raise ValueError(f"apparent affordance entry[{index}] requires evidence")
        if entry.get("classification") == "rejected_with_proof" and not entry.get("reason"):
            raise ValueError(f"apparent affordance entry[{index}] rejection requires a reason")
    return True


def _receipt_identity(key):
    parts = str(key or "").split(":")
    if len(parts) >= 9 and parts[0] == "control" and parts[1] == "surface":
        return {
            "kind": "control", "route": parts[2], "state": parts[3], "role": parts[4],
            "viewport": parts[5], "name": parts[6], "type": parts[7], "behavior": parts[8],
        }
    if len(parts) >= 12 and parts[0] == "transition" and parts[2:4] == ["control", "surface"]:
        return {
            "kind": "transition", "before_state": parts[1], "route": parts[4],
            "state": parts[5], "role": parts[6], "viewport": parts[7],
            "name": parts[8], "type": parts[9], "behavior": parts[10], "after_state": parts[11],
        }
    return None


def validate_execution_receipt(row, event, expected_control=None):
    """Return true only for a visible exact route/variant/before-after receipt."""
    if not isinstance(row, dict) or not isinstance(event, dict):
        return False
    identity = _receipt_identity(row.get("semantic_key"))
    if not identity or event.get("semantic_key") != row.get("semantic_key"):
        return False
    if event.get("route") != identity["route"] or event.get("role") != identity["role"]:
        return False
    if event.get("state") != identity["state"] or event.get("viewport") != identity["viewport"]:
        return False
    control = event.get("control") if isinstance(event.get("control"), dict) else {}
    expected = expected_control if isinstance(expected_control, dict) else (
        row.get("control_identity") if isinstance(row.get("control_identity"), dict) else {}
    )
    if control.get("identity") != expected.get("name") or control.get("type") != expected.get("control_type"):
        return False
    if event.get("visible") is not True or event.get("enabled") is not True:
        return False
    if event.get("off_route") is True or event.get("instrumentation") is True:
        return False
    if not isinstance(event.get("surface"), str) or not event["surface"].strip():
        return False
    if row.get("surface_identity") and event.get("surface") != row.get("surface_identity"):
        return False
    if not isinstance(event.get("input_mechanism"), str) or not event["input_mechanism"].strip():
        return False
    if row.get("input_mechanism") and event.get("input_mechanism") != row.get("input_mechanism"):
        return False
    if not isinstance(event.get("before_state"), str) or not event["before_state"].strip():
        return False
    if not isinstance(event.get("after_state"), str) or not event["after_state"].strip():
        return False
    if identity.get("kind") == "transition":
        if event.get("before_state") != identity["before_state"] or event.get("after_state") != identity["after_state"]:
            return False
    elif row.get("before_state") and event.get("before_state") != row.get("before_state"):
        return False
    if row.get("after_state") and event.get("after_state") != row.get("after_state"):
        return False
    return isinstance(event.get("evidence_refs"), list) and bool(event["evidence_refs"])


def validate_execution_receipt_set(rows, events, strict=False):
    """Require covered rows to have exact proof when the full-run contract applies."""
    for row in rows:
        if not isinstance(row, dict) or row.get("status") != "covered":
            continue
        references = row.get("execution_receipt_refs")
        material_path = row.get("material", True) and row.get("kind") in {"control", "transition"}
        if strict and material_path and (
            not row.get("surface_identity") or not row.get("input_mechanism")
            or not row.get("before_state") or not row.get("after_state")
        ):
            raise ValueError("covered path lacks exact execution binding fields")
        parent_control = next(
            (candidate for candidate in rows if isinstance(candidate, dict) and candidate.get("id") == row.get("parent_id")),
            None,
        )
        candidates = [
            event for event in events
            if not references or event.get("receipt_id") in references
        ]
        if (references or (strict and material_path)) and not any(
            validate_execution_receipt(row, event, parent_control.get("control_identity") if parent_control else None)
            for event in candidates
        ):
            raise ValueError("covered path lacks a matching execution receipt")
    return True


def classify_missing_path(proof):
    if not isinstance(proof, dict):
        return "evidence_debt"
    if (
        proof.get("promised") is True
        and proof.get("entry_points") == 0
        and proof.get("pending_state") is False
        and proof.get("cancellation_primitive") is False
    ):
        return "missing"
    return "evidence_debt"


def validate_derived_closure(frontier):
    if not isinstance(frontier, dict):
        raise ValueError("derived closure requires frontier state")
    if frontier.get("closure_state") == "closed_multi_source":
        receipts = frontier.get("closure_receipts")
        if not isinstance(receipts, list) or not receipts:
            raise ValueError("closure requires retained source receipts")
        if not all(isinstance(item, dict) and item.get("source") and item.get("receipt_ref") for item in receipts):
            raise ValueError("closure requires retained source receipts")
    return True


def validate_behavioral_identity(finding):
    identity = finding.get("behavioral_identity") if isinstance(finding, dict) else None
    affected = finding.get("affected_semantic_keys") if isinstance(finding, dict) else None
    if not isinstance(affected, list) or not affected:
        raise ValueError("behavioral lineage is required")
    if not isinstance(identity, dict) or identity.get("semantic_key") not in affected:
        raise ValueError("behavioral lineage must resolve to an affected frontier row")
    effect = str(finding.get("observed_effect_code") or "")
    if re.fullmatch(r"(?:effect|issue)[-_]?\d+", effect) or effect.startswith("report-only:"):
        raise ValueError("report-only identity cannot replace behavioral lineage")
    return True


def validate_visual_finding(finding):
    if not isinstance(finding, dict) or finding.get("finding_kind") != "visual":
        return True
    proof = finding.get("visual_proof") if isinstance(finding.get("visual_proof"), dict) else {}
    required = {"viewport", "target_state", "reproduction_steps", "screenshot_or_geometry_ref", "observed_symptom", "source_mechanism", "fresh_disconfirmation"}
    if (
        not required.issubset(proof)
        or not finding.get("evidence_refs")
        or any(not isinstance(proof.get(field), str) or not proof.get(field).strip() for field in required)
    ):
        raise ValueError("visual proof requires viewport, reproduction, retained artifact, symptom, mechanism, and disconfirmation")
    if proof.get("fresh_disconfirmation") in {"contradicted", "rejected"}:
        raise ValueError("visual proof is contradicted by fresh disconfirmation")
    return True


def validate_verifier_provenance(verifier):
    if not isinstance(verifier, dict) or not verifier.get("verifier_output") or not verifier.get("citations"):
        raise ValueError("verifier provenance is unsupported without retained output and citations")
    if verifier.get("verifier") == "approved" and verifier.get("verifier_id") == verifier.get("controller_id"):
        raise ValueError("verifier approval requires an independent verifier")
    if verifier.get("replacement_for_rejected") and verifier.get("verifier_id") == verifier.get("controller_id"):
        raise ValueError("controller cannot self-repair verifier failure; use an independent verifier")
    if verifier.get("verifier") == "approved" and verifier.get("citation_status") in {"missing", "fabricated", "unsafe", "unresolved"}:
        raise ValueError("verifier provenance is unsupported")
    return True


def validate_recovery_inventory(recovery):
    if not isinstance(recovery, dict):
        raise ValueError("recovery inventory is required")
    if recovery.get("status") == "blocked":
        for item in recovery.get("alternatives", []):
            if item.get("available") and not item.get("attempted"):
                raise ValueError("recovery remains active while a safe alternative is available")
    return True


def derive_record_counts(ledger):
    findings = [item for item in (ledger.get("findings") or []) if isinstance(item, dict)]
    frontier_rows = [item for item in ((ledger.get("path_frontier") or {}).get("rows") or []) if isinstance(item, dict)]
    return {
        "actionable": sum(item.get("action") in {"Fix", "Decide", "Prove"} and item.get("section") != "passed_keep" for item in findings),
        "evidence_debt": len([item for item in (ledger.get("evidence_debt") or []) if isinstance(item, dict)]),
        "passed_keep": sum(item.get("section") == "passed_keep" or item.get("action") == "Keep" for item in findings),
        "avoided": sum(item.get("action") == "Skip" and item.get("section") != "passed_keep" for item in findings)
        + sum(item.get("status") == "avoided" for item in frontier_rows),
        "scoped_out": sum(item.get("section") == "scoped_out" for item in findings)
        + sum(item.get("status") == "out_of_scope" for item in frontier_rows)
        + sum(item.get("status") == "scoped-out" for item in (ledger.get("evidence_debt") or []) if isinstance(item, dict)),
    }


def validate_record_count_projection(ledger, projection):
    """Reject caller-authored visible counts that drift from canonical records."""
    expected = derive_record_counts(ledger)
    if not isinstance(projection, dict) or projection.get("record_counts") != expected:
        raise ValueError("record-class counts do not reconcile with canonical records")
    summary = projection.get("summary") if isinstance(projection.get("summary"), dict) else {}
    expected_summary = {
        "clear_before_ship": sum(item.get("section") == "clear_before_ship" for item in ledger.get("findings", []) if isinstance(item, dict)),
        "fix_next": sum(item.get("section") == "fix_next" for item in ledger.get("findings", []) if isinstance(item, dict)),
        "not_proven_not_tested": sum(item.get("section") == "not_proven_not_tested" for item in ledger.get("findings", []) if isinstance(item, dict)) + expected["evidence_debt"],
        "passed_keep": expected["passed_keep"],
    }
    if summary != expected_summary:
        raise ValueError("visible action summary does not reconcile with canonical record classes")
    return True


def validate_record_language(record):
    section = record.get("section") if isinstance(record, dict) else None
    action = record.get("action") if isinstance(record, dict) else None
    fix = str(record.get("fix") or "").strip() if isinstance(record, dict) else ""
    verify = str(record.get("verify") or "").strip() if isinstance(record, dict) else ""
    if section == "passed_keep" or action == "Keep":
        if re.search(r"\b(correct|fix|change|remove|replace)\b", (fix + " " + verify).lower()):
            raise ValueError("Passed / Keep records cannot receive corrective language")
        return True
    if action in {"Fix", "Decide", "Prove"}:
        if (
            len(fix.split()) < 4
            or len(verify.split()) < 4
            or re.fullmatch(r"correct .* so .* no longer occurs", fix, re.I)
            or re.fullmatch(r"(?:verify|test|check)\s+(?:it|the fix|the behavior)\.?", verify, re.I)
        ):
            raise ValueError("actionable records require concrete, non-tautological fix and verification text")
    return True


def canonical_artifact_names():
    return set(CANONICAL_ARTIFACT_NAMES)


def calibrate_target_severity(context):
    target_intent = str((context or {}).get("target_intent") or "").lower()
    finding = str((context or {}).get("finding") or "").lower()
    if "ci" in finding or "deployment" in finding:
        return "scope_limitation" if target_intent in {"benchmark_fixture", "fixture", "prototype", "internal_tool", "library"} else "release_gate"
    return "normal"

def _evidence_path(reference, root):
    if not isinstance(reference, str) or not reference:
        return None
    relative = reference.split("#", 1)[0]
    if not relative or os.path.isabs(relative) or ".." in relative.replace("\\", "/").split("/"):
        return None
    candidate = os.path.realpath(os.path.join(root, relative))
    root = os.path.realpath(root)
    if os.path.commonpath((root, candidate)) != root:
        return None
    return candidate

def _sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def _checkpoint_file(reference, root, label, errors):
    relative = reference.split("#", 1)[0] if isinstance(reference, str) else ""
    cursor = os.path.realpath(root)
    for part in relative.replace("\\", "/").split("/"):
        if not part:
            continue
        cursor = os.path.join(cursor, part)
        if os.path.islink(cursor):
            errors.append(f"{label} must not use a symlink")
            return None
    path = _evidence_path(reference, root)
    if path is None or not os.path.isfile(path) or os.path.getsize(path) == 0:
        errors.append(f"{label} does not resolve to a safe non-empty file")
        return None
    return path

def _checkpoint_json(reference, root, label, errors):
    path = _checkpoint_file(reference, root, label, errors)
    if path is None:
        return None
    if os.path.getsize(path) > MAX_CHECKPOINT_BYTES:
        errors.append(f"{label} exceeds {MAX_CHECKPOINT_BYTES} bytes")
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError):
        errors.append(f"{label} is not readable JSON")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label} must contain an object")
        return None
    return value


def _checkpoint_citation(reference, root, label, errors):
    """Resolve a retained citation and validate an optional line anchor."""
    path = _checkpoint_file(reference, root, label, errors)
    if path is None:
        return None
    fragment = reference.split("#", 1)[1] if isinstance(reference, str) and "#" in reference else ""
    if not fragment:
        return path
    match = re.fullmatch(r"L(\d+)(?:-L(\d+))?", fragment)
    if not match:
        errors.append(f"{label} has an invalid line anchor")
        return path
    start = int(match.group(1))
    end = int(match.group(2) or match.group(1))
    try:
        with open(path, encoding="utf-8") as handle:
            line_count = sum(1 for _ in handle)
    except OSError:
        errors.append(f"{label} cannot be read for line-anchor validation")
        return path
    if start < 1 or end < start or end > line_count:
        errors.append(f"{label} line anchor is outside the retained artifact")
    return path

def validate_canonical_input(data, evidence_root=None):
    """Fail closed on cross-field defects before projecting a canonical v1 report."""
    if not isinstance(data, dict):
        return
    # Reject a current full run before the legacy fallback renderer can see it.
    # Historical imports remain readable only when explicitly identified as
    # historical by the caller.
    if data.get("run_scope") == "full" or (
        isinstance(data.get("source_ledger"), dict)
        and data["source_ledger"].get("run_scope") == "full"
    ):
        try:
            validate_input_mode(data)
        except ValueError:
            raise
    schema_name = data.get("schema_name")
    full_scope = data.get("run_scope") == "full" or (
        isinstance(data.get("source_ledger"), dict)
        and data["source_ledger"].get("run_scope") == "full"
    )
    if full_scope and schema_name not in {"shipworthy/readiness-report-input", "shipworthy/readiness-ledger"}:
        raise ValueError("current full runs require canonical ledger/report-input artifacts")
    if not isinstance(schema_name, str) or not schema_name.startswith("shipworthy/"):
        return
    if schema_name not in {"shipworthy/readiness-report-input", "shipworthy/readiness-ledger"}:
        raise ValueError(f"unknown Shipworthy schema name: {schema_name}")
    if data.get("schema_version") != "1.0":
        raise ValueError("unsupported Shipworthy schema version; expected 1.0")
    wrapper = data if schema_name == "shipworthy/readiness-report-input" else None
    ledger = data.get("source_ledger") if wrapper else data
    if wrapper and (
        not isinstance(ledger, dict)
        or ledger.get("schema_name") != "shipworthy/readiness-ledger"
        or ledger.get("schema_version") != "1.0"
    ):
        raise ValueError(
            "shipworthy/readiness-report-input source_ledger must be a Shipworthy readiness-ledger 1.0 object"
        )
    errors = []
    strict_run = data.get("run_scope") == "full" or ledger.get("run_scope") == "full"
    try:
        validate_input_mode(data)
    except ValueError as error:
        errors.append(str(error))
    frontier = ledger.get("path_frontier")
    if frontier is None:
        return
    if not isinstance(frontier, dict):
        raise ValueError("path_frontier must be an object when present")
    rows = frontier.get("rows")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        errors.append("path_frontier rows must be objects")
        rows = []
    by_id = {}
    semantic_keys = set()
    for index, row in enumerate(rows):
        row_id = row.get("id")
        key = row.get("semantic_key")
        if not isinstance(row_id, str) or row_id in by_id:
            errors.append("path_frontier row ids must be present and unique")
        else:
            by_id[row_id] = row
        if not isinstance(key, str) or key in semantic_keys:
            errors.append("path_frontier semantic keys must be present and unique")
        else:
            semantic_keys.add(key)
    for index, row in enumerate(rows):
        kind = row.get("kind")
        key = row.get("semantic_key")
        if kind == "intent":
            if row.get("parent_id") is not None:
                errors.append("intent cannot have a parent")
            continue
        expected = PARENT_KIND.get(kind)
        parent = by_id.get(row.get("parent_id"))
        if expected and (not parent or parent.get("kind") != expected):
            errors.append(f"{kind} parent must be {expected}")
        if (
            kind == "control"
            and parent
            and not str(key).startswith("control:" + str(parent.get("semantic_key")) + ":")
        ):
            errors.append("control semantic key must derive from its parent surface")
        if kind == "transition" and parent:
            expected_key = (
                f"transition:{row.get('before_state')}:{parent.get('semantic_key')}:"
                f"{row.get('after_state')}"
            )
            if key != expected_key:
                errors.append("transition semantic key must embed its parent control")
        if (
            row.get("material", True)
            and row.get("status") == "covered"
            and kind in {"control", "transition"}
            and (
                not isinstance(row.get("attempt_count"), int)
                or row.get("attempt_count", 0) < 1
                or not isinstance(row.get("evidence_refs"), list)
                or not row.get("evidence_refs")
            )
        ):
            errors.append(f"covered material {kind} requires an attempt and evidence")
        if (
            kind == "control"
            and row.get("material", True)
            and row.get("status") == "sampled_with_justification"
        ):
            errors.append("safe material control requires direct proof and cannot be sampled")
        missing_proof = row.get("missing_path_proof")
        if strict_run and isinstance(missing_proof, dict):
            expected_status = classify_missing_path(missing_proof)
            if row.get("status") != expected_status:
                errors.append(f"{kind} missing-path classification does not reconcile with its absence proof")
    expected_summary = {kind: sum(row.get("kind") == kind for row in rows) for kind in ("intent", "feature", "surface", "control", "transition")}
    if frontier.get("summary") != expected_summary:
        errors.append("path_frontier summary does not reconcile with rows")

    artifacts = [artifact for artifact in ledger.get("artifacts", []) if isinstance(artifact, dict)]
    artifact_ids = [artifact.get("artifact_id") for artifact in artifacts]
    if len(artifact_ids) != len(set(artifact_ids)):
        errors.append("artifact ids must be unique")
    finding_ids = [
        finding.get("finding_id")
        for finding in ledger.get("findings", [])
        if isinstance(finding, dict)
    ]
    debt_ids = [
        debt.get("debt_id")
        for debt in ledger.get("evidence_debt", [])
        if isinstance(debt, dict)
    ]
    if len(finding_ids) != len(set(finding_ids)):
        errors.append("finding ids must be unique")
    if len(debt_ids) != len(set(debt_ids)):
        errors.append("debt ids must be unique")
    if ledger.get("completion_status") == "complete":
        unavailable = [
            artifact.get("artifact_id")
            for artifact in artifacts
            if artifact.get("availability") in {"missing", "corrupt", "externally_linked"}
        ]
        if unavailable:
            errors.append("complete ledger contains missing, corrupt, or externally linked artifact")
    declared_artifacts = set(artifact_ids)
    for index, finding in enumerate(ledger.get("findings", [])):
        if isinstance(finding, dict):
            validators = (validate_record_language, validate_visual_finding) if strict_run else (
                (validate_visual_finding,) if finding.get("finding_kind") == "visual" else ()
            )
            for validator in validators:
                try:
                    validator(finding)
                except ValueError as error:
                    errors.append(f"findings[{index}] {error}")
            if finding.get("behavioral_identity") is not None or (
                strict_run and finding.get("action") in {"Fix", "Decide", "Prove"}
            ):
                try:
                    validate_behavioral_identity(finding)
                except ValueError as error:
                    errors.append(f"findings[{index}] {error}")
            if strict_run and finding.get("action") in {"Fix", "Decide", "Prove"} and finding.get("behavioral_identity") is None:
                errors.append(f"findings[{index}] behavioral lineage is required for an actionable record")
        finding_artifacts = finding.get("artifact_ids", []) if isinstance(finding, dict) else []
        if not isinstance(finding_artifacts, list) or any(artifact_id not in declared_artifacts for artifact_id in finding_artifacts):
            errors.append(f"findings[{index}] artifact_ids do not resolve")
        if not isinstance(finding, dict) or (
            finding.get("action") != "Fix"
            and not (strict_run and finding.get("action") in {"Decide", "Prove"})
        ):
            continue
        affected = finding.get("affected_semantic_keys")
        if not isinstance(affected, list) or not affected or any(key not in semantic_keys for key in affected):
            errors.append(f"findings[{index}] Fix lineage does not resolve to exact frontier rows")
        references = finding.get("evidence_refs")
        if not isinstance(references, list) or not references:
            errors.append(f"findings[{index}] Fix requires evidence_refs")
    for index, finding in enumerate(ledger.get("findings", [])):
        if not isinstance(finding, dict) or finding.get("proof") != "Confirmed":
            continue
        if (
            finding.get("confidence") != "Confirmed"
            or finding.get("verifier_status") != "approved"
            or not finding.get("artifact_ids")
        ):
            errors.append(
                f"Confirmed finding[{index}] requires Confirmed confidence, approved verifier, and artifact proof"
            )

    passes = frontier.get("discovery_passes", [])
    if not isinstance(passes, list):
        errors.append("discovery_passes must be an array")
        passes = []
    digest_pattern = r"^[a-f0-9]{64}$"
    for index, item in enumerate(passes):
        if not isinstance(item, dict):
            errors.append(f"discovery_passes[{index}] must be an object")
            continue
        for field in ("starting_frontier_digest", "ending_frontier_digest"):
            digest = item.get(field)
            if not isinstance(digest, str) or not re.fullmatch(digest_pattern, digest) or len(set(digest)) == 1:
                errors.append(f"discovery_passes[{index}] {field} is not a computed digest")
        if index and isinstance(passes[index - 1], dict) and passes[index - 1].get("ending_frontier_digest") != item.get("starting_frontier_digest"):
            errors.append(f"discovery_passes[{index}] digest chain does not reconcile")
        if item.get("new_semantic_keys") and item.get("starting_frontier_digest") == item.get("ending_frontier_digest"):
            errors.append(f"discovery_passes[{index}] claims new semantic keys without changing digest")
    if frontier.get("closure_state") == "closed_multi_source":
        final_digest = _frontier_digest(rows)
        qualifying = [item for item in passes[-2:] if isinstance(item, dict) and item.get("new_semantic_keys") == [] and item.get("starting_frontier_digest") == item.get("ending_frontier_digest") == final_digest]
        if len(qualifying) != 2:
            errors.append("closed_multi_source requires two final zero-yield passes with the computed frontier digest")
        elif len({item.get("method_family") for item in qualifying}) != 2:
            errors.append("closed_multi_source requires final zero-yield passes from distinct method families")
        unresolved = [
            row.get("semantic_key")
            for row in rows
            if row.get("material", True)
            and row.get("status") in {"unattempted", "unknown", "maybe", "evidence_debt", "blocked", "missing"}
        ]
        if unresolved:
            errors.append("closed_multi_source contains unresolved material frontier rows")
        if frontier.get("reconciliation_differences"):
            errors.append("closed_multi_source contains unresolved reconciliation differences")
        if strict_run:
            try:
                validate_discovery_exhaustion(frontier)
                validate_derived_closure(frontier)
            except ValueError as error:
                errors.append(str(error))

    if strict_run and ledger.get("completion_status") == "complete" and frontier:
        if not isinstance(ledger.get("raw_discoveries"), list):
            errors.append("complete canonical runs require raw discoveries for raw-to-final reconciliation")
        else:
            try:
                reconcile_raw_discoveries(ledger)
            except ValueError as error:
                errors.append(str(error))
        try:
            validate_execution_receipt_set(
                frontier.get("rows", []), ledger.get("execution_receipts", []), strict=True
            )
        except ValueError as error:
            errors.append(str(error))

    if evidence_root is not None:
        references = []
        references.extend(row.get("evidence_refs", []) for row in rows if isinstance(row.get("evidence_refs"), list))
        references.extend(
            observation.get("evidence_refs", [])
            for row in rows
            for observation in row.get("observations", [])
            if isinstance(observation, dict) and isinstance(observation.get("evidence_refs"), list)
        )
        references.extend(finding.get("evidence_refs", []) for finding in ledger.get("findings", []) if isinstance(finding, dict) and isinstance(finding.get("evidence_refs"), list))
        references.extend(
            [finding.get("visual_proof", {}).get("screenshot_or_geometry_ref")]
            for finding in ledger.get("findings", [])
            if isinstance(finding, dict)
            and isinstance(finding.get("visual_proof"), dict)
            and finding.get("visual_proof", {}).get("screenshot_or_geometry_ref")
        )
        manifest = frontier.get("manifest_artifact")
        if manifest:
            references.append([manifest])
        for group in references:
            for reference in group:
                path = _evidence_path(reference, evidence_root)
                if path is None or not os.path.isfile(path) or os.path.getsize(path) == 0:
                    errors.append(f"evidence reference does not resolve to a non-empty file: {reference}")
        for artifact in ledger.get("artifacts", []):
            if not isinstance(artifact, dict) or artifact.get("availability") != "available":
                continue
            descriptor = artifact.get("descriptor") if isinstance(artifact.get("descriptor"), dict) else {}
            reference = descriptor.get("relative_path")
            path = _evidence_path(reference, evidence_root)
            if path is None or not os.path.isfile(path) or os.path.getsize(path) == 0:
                errors.append(f"available artifact does not resolve to a non-empty file: {reference}")
                continue
            if descriptor.get("byte_size") != os.path.getsize(path) or descriptor.get("digest") != _sha256_file(path):
                errors.append(f"available artifact integrity mismatch: {reference}")
    if errors:
        raise ValueError("; ".join(errors[:20]))

def load_orchestration_checkpoint(input_path, data):
    """Load the schema-external operational checkpoint for canonical frontier reports."""
    if not isinstance(data, dict):
        return {}
    ledger = data.get("source_ledger") if data.get("schema_name") == "shipworthy/readiness-report-input" else data
    if not isinstance(ledger, dict) or ledger.get("schema_name") != "shipworthy/readiness-ledger":
        return {}
    frontier = ledger.get("path_frontier")
    if frontier is None:
        return {}
    if not isinstance(frontier, dict):
        raise ValueError("path_frontier must be an object when present")
    root = os.path.dirname(os.path.abspath(input_path))
    path = os.path.join(os.path.dirname(os.path.abspath(input_path)), "orchestration-checkpoint.json")
    if not os.path.isfile(path):
        raise ValueError("orchestration-checkpoint.json is required beside canonical frontier report input")
    if os.path.getsize(path) > MAX_CHECKPOINT_BYTES:
        raise ValueError(f"orchestration-checkpoint.json exceeds {MAX_CHECKPOINT_BYTES} bytes")
    try:
        with open(path, encoding="utf-8") as handle:
            checkpoint = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"orchestration-checkpoint.json is unreadable ({error})")
    if not isinstance(checkpoint, dict):
        raise ValueError("orchestration-checkpoint.json must contain an object")
    missing = sorted(CHECKPOINT_REQUIRED - set(checkpoint))
    if missing:
        raise ValueError("orchestration-checkpoint.json missing: " + ", ".join(missing))
    if not isinstance(checkpoint.get("lanes"), list) or not all(isinstance(item, str) and item.strip() for item in checkpoint["lanes"]):
        raise ValueError("orchestration-checkpoint.json lanes must be a string array")
    for field in (
        "omitted", "evidence_locations", "raw_lane_output_paths",
        "raw_verifier_output_paths", "control_census_paths",
        "zero_yield_pass_ids", "recovery_receipt_paths", "browser_failover_receipt_paths",
    ):
        if not isinstance(checkpoint.get(field), list) or not all(isinstance(item, str) for item in checkpoint[field]):
            raise ValueError(f"orchestration-checkpoint.json {field} must be a string array")
    if not checkpoint["evidence_locations"]:
        raise ValueError("orchestration-checkpoint.json evidence_locations must not be empty")
    if not isinstance(checkpoint.get("frontend_path_walk_performed"), bool):
        raise ValueError("orchestration-checkpoint.json frontend_path_walk_performed must be boolean")
    string_fields = CHECKPOINT_REQUIRED - {
        "lanes", "omitted", "evidence_locations", "raw_lane_output_paths",
        "raw_verifier_output_paths", "control_census_paths", "zero_yield_pass_ids",
        "evidence_debt_actions", "recovery_attempts", "recovery_receipt_paths",
        "browser_failover_receipt_paths",
        "frontend_path_walk_performed",
    }
    if any(not isinstance(checkpoint.get(field), str) or not checkpoint[field].strip() for field in string_fields):
        raise ValueError("orchestration-checkpoint.json required text fields must be non-empty strings")

    errors = []
    audit_status = checkpoint.get("audit_status")
    goal_completion_status = checkpoint.get("goal_completion_status")
    browser_status = checkpoint.get("browser_failover_status")
    recovery_status = checkpoint.get("recovery_status")
    if audit_status not in AUDIT_STATUSES:
        errors.append("audit_status is not canonical")
    if goal_completion_status not in GOAL_COMPLETION_STATUSES:
        errors.append("goal_completion_status is not canonical")
    if browser_status not in BROWSER_FAILOVER_STATUSES:
        errors.append("browser_failover_status is not canonical")
    # The v1 checkpoint remains readable for historical/older operational
    # records.  A current full run opts into the non-waivable contract by
    # declaring run_scope=full; that declaration is then validated strictly.
    strict_full_run = checkpoint.get("run_scope") == "full"
    if audit_status == "complete" and strict_full_run:
        strict_checkpoint = dict(checkpoint)
        try:
            validate_wave_contract(strict_checkpoint)
        except ValueError as error:
            errors.append(str(error))
        for field in (
            "host_orchestration_requirement", "host_orchestration_actual",
            "host_orchestration_compatibility", "host_orchestration_fallback_reason",
            "apparent_affordance_census_paths", "controller_id", "verifier_id",
            "target_intent", "target_calibration", "target_calibration_reason",
            "verifier_citation_refs", "verifier_citation_status",
        ):
            if not isinstance(checkpoint.get(field), (str, list)) or not checkpoint.get(field):
                errors.append(f"audit_status complete requires {field}")
        for field in ("apparent_affordance_census_paths", "verifier_citation_refs"):
            if not isinstance(checkpoint.get(field), list) or not all(
                isinstance(item, str) and item.strip() for item in checkpoint.get(field, [])
            ):
                errors.append(f"audit_status complete requires {field} as a string array")
        if checkpoint.get("host_orchestration_requirement") == "structured" and checkpoint.get("host_orchestration_actual") != "structured" and not checkpoint.get("host_orchestration_fallback_reason"):
            errors.append("host orchestration fallback reason is required")
        if checkpoint.get("target_calibration") not in {"scope_limitation", "release_gate", "normal"}:
            errors.append("target calibration is not canonical")
        if checkpoint.get("target_intent") in {"benchmark_fixture", "fixture", "prototype", "internal_tool", "library"}:
            if checkpoint.get("target_calibration") == "release_gate":
                errors.append("fixture target cannot inherit production release severity")
        try:
            validate_verifier_provenance({
                "verifier": checkpoint.get("verifier"),
                "verifier_output": checkpoint.get("raw_verifier_output_paths"),
                "citations": checkpoint.get("verifier_citation_refs"),
                "controller_id": checkpoint.get("controller_id"),
                "verifier_id": checkpoint.get("verifier_id"),
                "citation_status": checkpoint.get("verifier_citation_status"),
            })
        except ValueError as error:
            errors.append(str(error))
    try:
        checkpoint["_recovery_summary"] = recovery_projection(
            recovery_status, checkpoint.get("recovery_attempts")
        )
    except ValueError as error:
        errors.append(str(error))
    if goal_completion_status == "complete" and audit_status != "complete":
        errors.append("persistent goal cannot be complete while audit is not complete")
    if checkpoint.get("exhaustion_status") != frontier.get("closure_state"):
        errors.append("exhaustion_status does not match path_frontier closure_state")
    if audit_status in {"active", "blocked", "user_stopped"} and (
        ledger.get("completion_status") == "complete"
        or ledger.get("readiness_disposition") != "cannot_determine"
        or frontier.get("closure_state") == "closed_multi_source"
    ):
        errors.append(
            "non-complete audit_status requires an incomplete ledger, cannot_determine readiness, "
            "and a non-closed frontier"
        )

    ledger_document = _checkpoint_json(checkpoint.get("ledger_path"), root, "ledger_path", errors)
    if ledger_document is not None and ledger_document != ledger:
        errors.append("ledger_path does not match report-input source_ledger")

    for field, label in (
        ("raw_lane_output_paths", "raw lane output"),
        ("raw_verifier_output_paths", "raw verifier output"),
    ):
        for reference in checkpoint.get(field, []):
            _checkpoint_file(reference, root, label, errors)
    if audit_status == "complete":
        if checkpoint.get("omitted"):
            errors.append("audit_status complete cannot retain an omitted gate")
        if strict_full_run:
            certificate_paths = checkpoint.get("wave_certificate_paths")
            if not isinstance(certificate_paths, list) or len(certificate_paths) != len(checkpoint.get("verified_wave_ids", [])):
                errors.append("full audit requires one wave certificate per verified wave")
            # Current full runs retain machine-readable raw packets.  A plain
            # narrative can be retained as evidence, but cannot be shadow-read
            # for raw-to-final reconciliation.
            raw_packet_discoveries = []
            for index, reference in enumerate(checkpoint.get("raw_lane_output_paths", []) + checkpoint.get("raw_verifier_output_paths", [])):
                packet = _checkpoint_json(reference, root, f"raw operational packet[{index}]", errors)
                if isinstance(packet, dict):
                    candidates = packet.get("raw_discoveries", packet.get("discoveries"))
                    if isinstance(candidates, list):
                        raw_packet_discoveries.extend(candidates)
                    else:
                        errors.append(f"raw operational packet[{index}] discoveries must be an array")
            ledger_raw = [
                (item.get("observation_id"), item.get("semantic_key"))
                for item in (ledger.get("raw_discoveries") or [])
                if isinstance(item, dict) and item.get("observation_id")
            ]
            packet_raw = [
                (item.get("observation_id"), item.get("semantic_key"))
                for item in raw_packet_discoveries
                if isinstance(item, dict) and item.get("observation_id")
            ]
            if (
                not raw_packet_discoveries
                or len(ledger_raw) != len(set(ledger_raw))
                or set(packet_raw) != set(ledger_raw)
            ):
                errors.append("raw operational packets do not reconcile one-to-one with ledger discoveries")
            retained_receipt_refs = set(
                reference.split("#", 1)[0]
                for field in (
                    "raw_lane_output_paths", "raw_verifier_output_paths", "wave_certificate_paths",
                    "control_census_paths", "apparent_affordance_census_paths",
                    "recovery_receipt_paths", "browser_failover_receipt_paths",
                )
                for reference in checkpoint.get(field, [])
                if isinstance(reference, str)
            )
            for receipt in (frontier.get("closure_receipts") or []):
                if isinstance(receipt, dict):
                    receipt_ref = receipt.get("receipt_ref")
                    if receipt_ref not in retained_receipt_refs:
                        errors.append("closure receipt is not retained in an operational source packet")
                    _checkpoint_file(receipt_ref, root, "closure receipt", errors)
            for citation in checkpoint.get("verifier_citation_refs", []):
                _checkpoint_citation(citation, root, "verifier citation", errors)
        certified_wave_ids = []
        for index, reference in enumerate(checkpoint.get("wave_certificate_paths", [])):
            certificate = _checkpoint_json(reference, root, f"wave certificate[{index}]", errors)
            if isinstance(certificate, dict):
                certified_wave_ids.append(certificate.get("wave_id"))
                if certificate.get("wave_id") not in checkpoint.get("verified_wave_ids", []):
                    errors.append(f"wave certificate[{index}] does not resolve to a verified wave")
                if certificate.get("decision") != "approved" or not certificate.get("verifier_id"):
                    errors.append(f"wave certificate[{index}] lacks independent approval provenance")
                if certificate.get("verifier_id") == checkpoint.get("controller_id"):
                    errors.append(f"wave certificate[{index}] verifier is not independent")
                if not certificate.get("citation_refs") or not certificate.get("raw_output_ref"):
                    errors.append(f"wave certificate[{index}] lacks retained citation provenance")
                for citation in certificate.get("citation_refs", []):
                    _checkpoint_citation(citation, root, f"wave certificate[{index}] citation", errors)
                _checkpoint_file(certificate.get("raw_output_ref"), root, f"wave certificate[{index}] raw output", errors)
        if strict_full_run and (
            len(certified_wave_ids) != len(set(certified_wave_ids))
            or set(certified_wave_ids) != set(checkpoint.get("verified_wave_ids", []))
        ):
            errors.append("full audit requires one-to-one wave certificate coverage")
        for index, reference in enumerate(checkpoint.get("apparent_affordance_census_paths", [])):
            census = _checkpoint_json(reference, root, f"apparent affordance census[{index}]", errors)
            if isinstance(census, dict):
                try:
                    validate_affordance_census(census)
                except ValueError as error:
                    errors.append(str(error))

    rows = frontier.get("rows") if isinstance(frontier.get("rows"), list) else []
    frontier_digest = _frontier_digest(rows)
    frontier_controls = {
        row.get("semantic_key")
        for row in rows
        if isinstance(row, dict) and row.get("kind") == "control" and isinstance(row.get("semantic_key"), str)
    }
    census_controls = set()
    census_methods = set()
    census_unmatched = []
    for index, reference in enumerate(checkpoint.get("control_census_paths", [])):
        census = _checkpoint_json(reference, root, f"control census[{index}]", errors)
        if census is None:
            continue
        required = {"method_family", "semantic_keys", "digest", "frontier_digest", "unmatched_controls"}
        if not required.issubset(census):
            errors.append(f"control census[{index}] is incomplete")
            continue
        keys = census.get("semantic_keys")
        unmatched = census.get("unmatched_controls")
        if (
            not isinstance(keys, list)
            or not all(isinstance(item, str) and item.startswith("control:") for item in keys)
            or len(keys) != len(set(keys))
        ):
            errors.append(f"control census[{index}] semantic_keys are invalid")
            continue
        if not isinstance(unmatched, list) or not all(isinstance(item, str) and item.strip() for item in unmatched):
            errors.append(f"control census[{index}] unmatched_controls are invalid")
            continue
        if census.get("digest") != _semantic_digest(keys):
            errors.append(f"control census[{index}] digest does not reconcile")
        if census.get("frontier_digest") != frontier_digest:
            errors.append(f"control census[{index}] frontier digest does not reconcile")
        method = census.get("method_family")
        if not isinstance(method, str) or not method:
            errors.append(f"control census[{index}] method_family is invalid")
        else:
            census_methods.add(method)
        census_controls.update(keys)
        census_unmatched.extend(unmatched)

    passes = frontier.get("discovery_passes") if isinstance(frontier.get("discovery_passes"), list) else []
    pass_ids = [item.get("id") for item in passes if isinstance(item, dict)]
    zero_yield_ids = checkpoint.get("zero_yield_pass_ids", [])
    if len(zero_yield_ids) != len(set(zero_yield_ids)) or any(item not in pass_ids for item in zero_yield_ids):
        errors.append("zero-yield pass IDs do not resolve uniquely")

    unresolved = [
        row.get("semantic_key")
        for row in rows
        if isinstance(row, dict)
        and row.get("material", True)
        and row.get("status") in {"unattempted", "unknown", "maybe", "evidence_debt", "blocked", "missing"}
    ]
    if audit_status == "complete":
        if not rows:
            errors.append("audit_status complete requires a non-empty frontier")
        if not any(
            isinstance(row, dict) and row.get("kind") == "surface"
            for row in rows
        ):
            errors.append("audit_status complete requires at least one discovered frontend surface")
        if not checkpoint["lanes"]:
            errors.append("audit_status complete requires at least one recorded lane")
        for field in ("raw_lane_output_paths", "raw_verifier_output_paths", "control_census_paths"):
            if not checkpoint[field]:
                errors.append(f"audit_status complete requires {field}")
        if ledger.get("completion_status") != "complete":
            errors.append("audit_status complete requires ledger completion_status complete")
        if frontier.get("closure_state") != "closed_multi_source":
            errors.append("audit_status complete requires closed_multi_source frontier")
        if unresolved:
            errors.append("audit_status complete has unresolved material frontier rows")
        if frontier.get("reconciliation_differences"):
            errors.append("audit_status complete has unresolved frontier reconciliation differences")
        if checkpoint.get("frontend_path_walk_performed") is not True or checkpoint.get("path_walk_status") != "full":
            errors.append("audit_status complete requires a full frontend path-walk")
        if checkpoint.get("verifier") != "approved":
            errors.append("audit_status complete requires approved verifier")
        if len(passes) < 2 or zero_yield_ids != pass_ids[-2:]:
            errors.append("audit_status complete requires the final two zero-yield pass IDs")
        elif any(item.get("new_semantic_keys") != [] for item in passes[-2:] if isinstance(item, dict)):
            errors.append("audit_status complete names a non-zero-yield discovery pass")
        elif len({item.get("method_family") for item in passes[-2:] if isinstance(item, dict)}) != 2:
            errors.append("audit_status complete requires zero-yield passes from distinct method families")
        if census_controls != frontier_controls:
            errors.append("control census does not reconcile with frontier controls")
        if not CONTROL_CENSUS_METHODS.issubset(census_methods):
            errors.append("control census lacks runtime and static method families")
        if census_unmatched:
            errors.append("control census contains unmatched controls")
        if browser_status not in {"not_needed", "succeeded"}:
            errors.append("audit_status complete cannot retain active, blocked, or user-stopped browser failover")
        if recovery_status not in {"not_needed", "succeeded"}:
            errors.append("audit_status complete cannot retain active or blocked recovery")

    for index, reference in enumerate(checkpoint.get("recovery_receipt_paths", [])):
        _checkpoint_json(reference, root, f"recovery receipt[{index}]", errors)

    ledger_debts = {
        item.get("debt_id"): item
        for item in ledger.get("evidence_debt", [])
        if isinstance(item, dict) and isinstance(item.get("debt_id"), str)
    }
    actions = checkpoint.get("evidence_debt_actions")
    if not isinstance(actions, list):
        errors.append("evidence_debt_actions must be an array")
        actions = []
    action_by_id = {}
    for index, action in enumerate(actions):
        required = {"debt_id", "next_action", "alternate_method", "attempt_count", "last_blocker", "disposition"}
        if not isinstance(action, dict) or not required.issubset(action):
            errors.append(f"evidence debt action[{index}] is incomplete")
            continue
        debt_id = action.get("debt_id")
        if not isinstance(debt_id, str) or debt_id in action_by_id:
            errors.append(f"evidence debt action[{index}] debt_id is invalid or duplicated")
            continue
        action_by_id[debt_id] = action
        if (
            not isinstance(action.get("next_action"), str) or not action["next_action"].strip()
            or not isinstance(action.get("alternate_method"), str) or not action["alternate_method"].strip()
            or not isinstance(action.get("attempt_count"), int) or action["attempt_count"] < 0
            or not isinstance(action.get("last_blocker"), str)
            or action.get("disposition") not in {"active", "blocked", "scoped_out", "resolved"}
        ):
            errors.append(f"evidence debt action[{index}] fields are invalid")
        if action.get("disposition") == "blocked" and (
            action.get("attempt_count", 0) < 1 or not action.get("last_blocker", "").strip()
        ):
            errors.append(f"evidence debt action[{index}] final blocker lacks attempts or blocker detail")
    if set(action_by_id) != set(ledger_debts):
        errors.append("evidence debt actions do not reconcile with canonical evidence debt")
    for debt_id, debt in ledger_debts.items():
        action = action_by_id.get(debt_id, {})
        expected = {"needs-proof": "active", "blocked": "blocked", "scoped-out": "scoped_out"}.get(debt.get("status"))
        if expected and action.get("disposition") != expected:
            errors.append(f"evidence debt action for {debt_id} has inconsistent disposition")

    receipt_paths = checkpoint.get("browser_failover_receipt_paths", [])
    if browser_status == "not_needed" and receipt_paths:
        errors.append("browser failover receipts exist while status is not_needed")
    if browser_status in {"active", "succeeded", "blocked", "user_stopped"} and not receipt_paths:
        errors.append("browser failover receipt is required")
    receipt_results = []
    for index, reference in enumerate(receipt_paths):
        receipt = _checkpoint_json(reference, root, f"browser failover receipt[{index}]", errors)
        if receipt is None:
            continue
        required = {
            "native_error", "cleanup_result", "fallback_kind", "process_or_context_id",
            "isolation_proof", "fallback_result", "remaining_evidence_debt",
        }
        if not required.issubset(receipt):
            errors.append(f"browser failover receipt[{index}] is incomplete")
            continue
        if not isinstance(receipt.get("native_error"), str) or not receipt["native_error"].strip():
            errors.append(f"browser failover receipt[{index}] lacks native error")
        if not isinstance(receipt.get("cleanup_result"), str) or not receipt["cleanup_result"].strip():
            errors.append(f"browser failover receipt[{index}] lacks cleanup result")
        remaining = receipt.get("remaining_evidence_debt")
        if not isinstance(remaining, list) or not all(isinstance(item, str) and item.strip() for item in remaining):
            errors.append(f"browser failover receipt[{index}] remaining evidence debt is invalid")
        result = receipt.get("fallback_result")
        receipt_results.append(result)
        if result == "recovered":
            recovered_kinds = {
                "independent_playwright", "chrome", "computer_use",
                "target_owned_e2e", "reassigned_frontend_driver",
                "sequential_frontend_driver",
            }
            if receipt.get("fallback_kind") not in recovered_kinds:
                errors.append(f"browser failover receipt[{index}] did not use an allowed independent Playwright or frontend fallback")
            process_id = str(receipt.get("process_or_context_id") or "").strip().casefold()
            isolation = str(receipt.get("isolation_proof") or "").strip().casefold()
            same_binding_markers = (
                "same browser", "same locked", "same native", "shared browser",
                "reused browser", "attached browser", "native-browser binding",
                "native browser binding",
            )
            if (
                not process_id
                or process_id == "tab.playwright"
                or not isolation
                or not any(marker in isolation for marker in ("separate", "independent", "isolated"))
                or any(marker in isolation for marker in same_binding_markers)
            ):
                errors.append(
                    f"browser failover receipt[{index}] does not prove isolation from the same locked browser binding"
                )
            if remaining:
                errors.append(f"browser failover receipt[{index}] recovered but retains evidence debt")
        elif result in {"blocked", "failed"}:
            if receipt.get("fallback_kind") not in {
                "independent_playwright", "independent_playwright_unavailable",
                "independent_playwright_forbidden",
            }:
                errors.append(f"browser failover receipt[{index}] did not attempt or bound independent Playwright")
            if not remaining:
                errors.append(f"browser failover receipt[{index}] does not preserve blocked evidence debt")
        else:
            errors.append(f"browser failover receipt[{index}] fallback_result is not canonical")
    if browser_status == "succeeded" and (
        not receipt_results or receipt_results[-1] != "recovered"
    ):
        errors.append("browser_failover_status succeeded requires the final recovery receipt to recover")
    if browser_status == "blocked" and (
        not receipt_results or receipt_results[-1] not in {"blocked", "failed"}
    ):
        errors.append("browser_failover_status blocked requires a terminal blocked receipt")

    if errors:
        raise ValueError("; ".join(errors[:20]))
    checkpoint["_validated_checkpoint"] = True
    checkpoint["_control_census_summary"] = (
        f"{len(census_controls)} controls; {', '.join(sorted(census_methods))}; "
        f"{len(census_unmatched)} unmatched"
    )
    return checkpoint

def summarize_frontier(frontier):
    """Derive a compact Product Coverage projection and reject caller count drift."""
    if not isinstance(frontier, dict):
        return None
    closure = frontier.get("closure_state")
    if closure not in CLOSURE_STATES:
        raise ValueError("path_frontier closure_state is not canonical")
    rows = frontier.get("rows")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError("path_frontier rows must be objects")
    kinds = ("intent", "feature", "surface", "control", "transition")
    counts = {kind: sum(row.get("kind") == kind for row in rows) for kind in kinds}
    if frontier.get("summary") != counts:
        raise ValueError("path_frontier summary does not reconcile with rows")
    observations = [item for row in rows for item in row.get("observations", []) if isinstance(item, dict)]
    passes = [item for item in frontier.get("discovery_passes", []) if isinstance(item, dict)]
    roles = sorted({str(item.get("role")) for item in observations + passes if item.get("role")})
    states = sorted({str(item.get("state")) for item in observations if item.get("state")})
    viewports = sorted({str(item.get("viewport")) for item in observations + passes if item.get("viewport")})
    families = sorted({str(item.get("method_family")) for item in observations + passes if item.get("method_family")})
    variants = sorted({" / ".join(str(item.get(key) or "—") for key in ("role", "state", "viewport")) for item in observations})
    controls = [row for row in rows if row.get("kind") == "control" and row.get("material", True)]
    attempted = sum(isinstance(row.get("attempt_count"), int) and row.get("attempt_count", 0) > 0 for row in controls)
    pct = round(100 * attempted / len(controls)) if controls else 0
    return {
        "closure_state": closure, "closure_reason": frontier.get("closure_reason") or "No closure reason recorded.",
        "counts": counts, "rows": rows, "roles": roles, "states": states,
        "viewports": viewports, "variants": variants,
        "method_families": families, "control_attempts": (attempted, len(controls), pct),
        "features": [row for row in rows if row.get("kind") == "feature"],
        "controls": controls,
        "dispositions": [row for row in rows if row.get("status") in {"blocked", "avoided"}],
        "differences": [row for row in frontier.get("reconciliation_differences", []) if isinstance(row, dict)],
        "manifest": frontier.get("manifest_artifact"),
    }

def coverage_confidence_html(frontier, checkpoint=None, record_counts=None):
    """Render a bounded early explanation of scope and honest closure."""
    summary = summarize_frontier(frontier)
    if not summary:
        return ('<section class="confidence-summary"><div class="section-head">'
                '<h2>Coverage Confidence</h2></div><p class="muted-note">'
                'Coverage confidence was not recorded for this run.</p></section>')
    material = [row for row in summary["rows"] if row.get("material", True)]
    status_counts = {status: sum(row.get("status") == status for row in material) for status in (
        "covered", "sampled_with_justification", "blocked", "avoided", "inferred",
        "missing", "out_of_scope", "evidence_debt",
    )}
    covered = status_counts["covered"]
    not_proven = status_counts["missing"] + status_counts["evidence_debt"] + int((record_counts or {}).get("evidence_debt", 0))
    roles = ", ".join(summary["roles"]) or "not recorded"
    states = ", ".join(summary["states"]) or "not recorded"
    viewports = ", ".join(summary["viewports"]) or "not recorded"
    closure_achieved = summary["closure_state"] == "closed_multi_source"
    closure = "Closure achieved" if closure_achieved else "Closure not achieved"
    limits = (
        f'{status_counts["avoided"]} avoided for safety; {status_counts["inferred"]} inferred; '
        f'{status_counts["blocked"]} blocked; {not_proven} NOT_PROVEN'
    )
    recovery = (checkpoint or {}).get("_recovery_summary") or {
        "status": "not_needed", "attempt_count": 0, "recovered_paths": 0, "remaining_debt": 0
    }
    labels = {
        "not_needed": "Not needed", "active": "In progress", "succeeded": "Recovered",
        "blocked": "Blocked", "user_stopped": "User stopped",
    }
    recovery_html = (
        f'<p><b>Recovery</b><span>{esc(labels.get(recovery["status"], "NOT_PROVEN"))}: '
        f'{recovery["recovered_paths"]} paths resumed; {recovery["remaining_debt"]} debt items remain.</span></p>'
        '<details><summary>Recovery attempts</summary>'
        f'<p>{recovery["attempt_count"]} bounded attempt(s). '
        f'Status: {esc(recovery["status"])}.</p></details>'
    )
    record_counts = record_counts or {}
    record_text = (
        f'{record_counts.get("actionable", 0)} actionable · '
        f'{record_counts.get("evidence_debt", 0)} evidence debt · '
        f'{record_counts.get("passed_keep", 0)} passed/keep · '
        f'{record_counts.get("avoided", 0)} avoided · '
        f'{record_counts.get("scoped_out", 0)} scoped out'
    )
    return (
        '<section class="confidence-summary"><div class="section-head"><h2>Coverage Confidence</h2></div>'
        '<div class="confidence-grid">'
        f'<p><b>What was tested</b><span>{covered} of {len(material)} material frontier items were covered by evidence.</span></p>'
        f'<p><b>Coverage conditions</b><span>Roles: {esc(roles)} · States: {esc(states)} · Viewports: {esc(viewports)}</span></p>'
        f'<p><b>What was not tested / Important proof limits</b><span>{esc(limits)}. '
        f'{status_counts["out_of_scope"]} out of scope; {status_counts["sampled_with_justification"]} sampled.</span></p>'
        f'<p><b>Record classes</b><span>{esc(record_text)}</span></p>'
        f'<p><b>Why testing stopped</b><span>{esc(summary["closure_reason"])}</span></p>'
        f'<p><b>{closure}</b><span>{esc(title_case(norm_token(summary["closure_state"])))}</span></p>'
        f'{recovery_html}'
        '</div></section>'
    )

def project_input(data, orchestration_checkpoint=None):
    """Project validated v1 ledger/report-input data into the stable report shape."""
    if not isinstance(data, dict):
        return {}
    wrapper = data if data.get("schema_name") == "shipworthy/readiness-report-input" else None
    ledger = data.get("source_ledger") if wrapper else data
    if not isinstance(ledger, dict) or ledger.get("schema_name") != "shipworthy/readiness-ledger":
        if data.get("run_scope") == "full" or (
            isinstance(data.get("source_ledger"), dict)
            and data["source_ledger"].get("run_scope") == "full"
        ):
            validate_canonical_input(data)
        return data
    validate_canonical_input(data)
    checkpoint = orchestration_checkpoint if isinstance(orchestration_checkpoint, dict) else None
    strict_full = data.get("run_scope") == "full" or ledger.get("run_scope") == "full"
    if strict_full and (
        not isinstance(checkpoint, dict)
        or checkpoint.get("run_scope") != "full"
        or checkpoint.get("_validated_checkpoint") is not True
    ):
        raise ValueError(
            "current full runs require a validated orchestration-checkpoint.json before rendering"
        )
    debt_actions = {
        item.get("debt_id"): item
        for item in (checkpoint or {}).get("evidence_debt_actions", [])
        if isinstance(item, dict) and item.get("debt_id")
    }
    artifacts = {
        row.get("artifact_id"): row for row in ledger.get("artifacts", [])
        if isinstance(row, dict) and row.get("artifact_id")
    }
    findings = []
    for row in ledger.get("findings", []):
        if not isinstance(row, dict):
            continue
        subject = row.get("subject") if isinstance(row.get("subject"), dict) else {}
        artifact_ids = [value for value in row.get("artifact_ids", []) if value in artifacts]
        evidence = []
        for artifact_id in artifact_ids:
            artifact = artifacts[artifact_id]
            descriptor = artifact.get("descriptor") if isinstance(artifact.get("descriptor"), dict) else {}
            lineage = artifact.get("lineage") if isinstance(artifact.get("lineage"), dict) else {}
            evidence.append(
                f"{artifact_id} ({artifact.get('availability')}; {descriptor.get('relative_path')}; "
                f"sha256={descriptor.get('digest') or 'not sealed'}; producer={lineage.get('producer')}; "
                f"operation={lineage.get('operation')})"
            )
        finding = {
            "record_id": row.get("finding_id"), "record_kind": "finding",
            "title": f"{row.get('finding_id')} — {subject.get('title')}",
            "consequence": row.get("summary"), "action": row.get("action"),
            "proof": row.get("proof"), "confidence": row.get("confidence"),
            "section": row.get("section"),
            "severity": V1_SEVERITY.get(row.get("severity"), "info"),
            "canonical_severity": row.get("severity"),
            "artifact_ids": artifact_ids,
            "evidence": (("Evidence: " + ", ".join(row.get("evidence_refs", []))) if row.get("evidence_refs") else "No evidence reference is attached to this record.") +
                        ((" · Artifacts: " + "; ".join(evidence)) if evidence else ""),
            "fix": row.get("fix") or (f"Correct {subject.get('title') or row.get('finding_id')} so the observed effect "
                    f"`{row.get('observed_effect_code')}` no longer occurs."),
            "verify": row.get("verify") or ("Re-exercise " + ", ".join(row.get("affected_semantic_keys", [])) +
                       f" and confirm `{row.get('observed_effect_code')}` no longer occurs."),
        }
        if subject.get("location"):
            finding["location"] = {"file": subject["location"]}
        findings.append(finding)
    evidence_debt = []
    for row in ledger.get("evidence_debt", []):
        if not isinstance(row, dict):
            continue
        action = debt_actions.get(row.get("debt_id"), {})
        blocker = action.get("last_blocker")
        evidence = f"Evidence-debt status: {row.get('status')}"
        if blocker:
            evidence += f" · Last blocker: {blocker}"
        evidence_debt.append({
            "record_id": row.get("debt_id"), "record_kind": "evidence_debt",
            "title": f"{row.get('debt_id')} — Evidence required for {row.get('subject')}",
            "consequence": row.get("reason"), "action": "Prove", "proof": "Not tested",
            "confidence": "Hypothesis", "section": "not_proven_not_tested",
            "severity": "info", "canonical_severity": "Unscored",
            "artifact_ids": row.get("artifact_ids", []),
            "evidence": evidence,
            "fix": action.get("next_action") or row.get("proof_needed"),
            "verify": action.get("alternate_method") or f"Evidence-debt status: {row.get('status')}.",
        })
    producer = ledger.get("producer") if isinstance(ledger.get("producer"), dict) else {}
    checkpoint = checkpoint or {
        "producer": f"{producer.get('name')} {producer.get('version')}",
        "completion_status": ledger.get("completion_status"),
        "gate_policy": (ledger.get("gate") or {}).get("policy"),
        "source_report_input": wrapper.get("report_input_id") if wrapper else None,
        "frontier_total": len((ledger.get("path_frontier") or {}).get("rows", [])),
        "exhaustion_status": (ledger.get("path_frontier") or {}).get("closure_state"),
        "omitted": ["lane roster and agent execution are not encoded by canonical ledger v1.0"],
    }
    projected = {
        "target": checkpoint.get("target_name") or ledger.get("ledger_id", "target"),
        "generated_at": ledger.get("generated_at"),
        "verdict": V1_VERDICT.get(ledger.get("readiness_disposition"), "NOT READY"),
        "findings": findings,
        "evidence_debt": evidence_debt,
        "record_counts": derive_record_counts(ledger),
        "summary": {
            "clear_before_ship": sum(item.get("section") == "clear_before_ship" for item in findings),
            "fix_next": sum(item.get("section") == "fix_next" for item in findings),
            "not_proven_not_tested": sum(item.get("section") == "not_proven_not_tested" for item in findings) + len(evidence_debt),
            "passed_keep": sum(item.get("section") == "passed_keep" for item in findings),
        },
        "path_frontier": ledger.get("path_frontier"),
        "checkpoint": checkpoint,
    }
    validate_record_count_projection(ledger, projected)
    return projected

def esc(x): return html.escape("" if x is None else str(x))

def row_text(x):
    if isinstance(x, list):
        return " · ".join(str(v) for v in x)
    return x

def semantic_label(key):
    token = str(key or "(unnamed)").split(":", 1)[-1]
    return title_case(re.sub(r"[-_/]+", " ", token))

def detail_section(label, body):
    return f'<details class="coverage-detail"><summary>{esc(label)}</summary><div class="ev-block">{body}</div></details>'

def product_coverage_html(frontier):
    summary = summarize_frontier(frontier)
    if summary is None:
        return ('<section class="section product-coverage"><div class="section-head"><h2>Product Coverage</h2></div>'
                '<div class="muted-note">Product coverage not recorded for this run.</div></section>')
    counts = summary["counts"]
    attempted, total_controls, pct = summary["control_attempts"]
    closure_label = title_case(norm_token(summary["closure_state"]))
    metrics = "".join(
        f'<span class="coverage-metric"><b>{counts[kind]}</b> {esc(kind if counts[kind] == 1 else kind + "s")}</span>'
        for kind in ("feature", "surface", "control", "transition")
    )
    feature_rows = []
    by_parent = {}
    for row in summary["rows"]:
        by_parent.setdefault(row.get("parent_id"), []).append(row)
    for feature in summary["features"][:20]:
        surface_ids = {row.get("id") for row in by_parent.get(feature.get("id"), []) if row.get("kind") == "surface"}
        control_count = sum(row.get("kind") == "control" and row.get("parent_id") in surface_ids for row in summary["rows"])
        feature_rows.append(
            f'<div class="coverage-feature"><b>{esc(semantic_label(feature.get("semantic_key")))}</b>'
            f'<span>{len(surface_ids)} surfaces · {control_count} controls · {esc(feature.get("status"))}</span></div>'
        )
    if len(summary["features"]) > 20:
        feature_rows.append(f'<p class="muted-note">{len(summary["features"]) - 20} more features are in the frontier manifest.</p>')

    control_rows = []
    for row in summary["controls"][:12]:
        identity = row.get("control_identity") if isinstance(row.get("control_identity"), dict) else {}
        control_rows.append(
            f'<div class="coverage-proof"><b>{esc(identity.get("name") or semantic_label(row.get("semantic_key")))}</b>'
            f'<span>{esc(row.get("status"))} · {esc(row.get("attempt_count", 0))} attempts · '
            f'{len(row.get("evidence_refs", []))} evidence refs</span></div>'
        )
    if len(summary["controls"]) > 12:
        control_rows.append(f'<p class="muted-note">{len(summary["controls"]) - 12} more controls are in the frontier manifest.</p>')

    variants = "".join(f'<span class="coverage-tag">{esc(value)}</span>' for value in summary["variants"][:20])
    dispositions = "".join(
        f'<div class="coverage-proof"><b>{esc(semantic_label(row.get("semantic_key")))}</b>'
        f'<span>{esc(row.get("status"))} · {esc(row.get("terminal_reason") or "No reason recorded")}</span></div>'
        for row in summary["dispositions"][:20]
    ) or '<p class="muted-note">No blocked or avoided material actions.</p>'
    differences = "".join(
        f'<div class="coverage-proof"><b>{esc(row.get("semantic_key"))}</b><span>{esc(row.get("reason"))}</span></div>'
        for row in summary["differences"][:20]
    ) or '<p class="muted-note">No unresolved discovery differences.</p>'
    manifest = summary["manifest"]
    manifest_text = '<p class="muted-note">No separate frontier manifest was recorded.</p>'
    if isinstance(manifest, str) and manifest and ":" not in manifest and not manifest.startswith("/") and ".." not in manifest.split("/"):
        manifest_text = f'<p><a href="{esc(manifest)}">Open the complete frontier JSON</a></p>'
    elif manifest:
        manifest_text = f'<p class="mono">{esc(manifest)}</p>'

    family_text = ", ".join(semantic_label(value) for value in summary["method_families"]) or "not recorded"
    role_text = ", ".join(summary["roles"]) or "not recorded"
    feature_html = "".join(feature_rows) or '<p class="muted-note">No feature rows recorded.</p>'
    return (
        '<section class="section product-coverage"><div class="section-head"><h2>Product Coverage</h2></div>'
        f'<div class="coverage-status"><span class="closure-chip">{esc(closure_label)}</span><p>{esc(summary["closure_reason"])}</p></div>'
        f'<div class="coverage-metrics">{metrics}</div>'
        f'<p class="cov-line"><strong>{attempted} of {total_controls}</strong>&nbsp; material controls attempted ({pct}%)</p>'
        f'<p class="coverage-meta"><b>Roles:</b> {esc(role_text)}<br><b>Discovery:</b> {esc(family_text)}</p>'
        f'<div class="coverage-features">{feature_html}</div>'
        + detail_section("Control evidence", "".join(control_rows) or '<p class="muted-note">No material controls recorded.</p>')
        + detail_section("Role / state / device coverage", variants or '<p class="muted-note">No observation variants recorded.</p>')
        + detail_section("Blocked / avoided actions", dispositions)
        + detail_section("Discovery reconciliation", differences)
        + detail_section("Frontier manifest", manifest_text)
        + '</section>'
    )

def title_case(x):
    return " ".join(w[:1].upper() + w[1:].lower() for w in str(x).split())

def num(x, default=0.0):
    try:
        v = float(x); return v if v == v else default   # reject NaN
    except (TypeError, ValueError):
        return default

def norm_token(x):
    return re.sub(r"\s+", " ", str(x or "").strip().lower().replace("_", " ").replace("-", " "))

def cov_kind(x):
    k = norm_token(x).replace(" ", "_")
    if k == "debt":
        return "evidence_debt"
    return k

def cov_label(s):
    s = s or {}
    kind = cov_kind(s.get("kind"))
    return s.get("label") or COV_LABEL.get(kind) or norm_token(s.get("kind")).replace("_", " ")

def sev_key(x):
    return SEV_ALIAS.get(norm_token(x), "info")

def explicit_section_key(f):
    f = f or {}
    for field in ("section", "category", "bucket", "decision"):
        raw = norm_token(f.get(field))
        if raw:
            k = SECTION_ALIAS.get(raw)
            if k:
                return k
    return None

def section_from_severity(raw):
    t = norm_token(raw)
    if not t:
        return "not_proven_not_tested"
    if t in SECTION_ALIAS:
        return SECTION_ALIAS[t]
    return {
        "blocker": "clear_before_ship",
        "critical": "clear_before_ship",
        "p0 blocker": "clear_before_ship",
        "p0": "clear_before_ship",
        "major": "fix_next",
        "high": "fix_next",
        "p1 major": "fix_next",
        "p1": "fix_next",
        "moderate": "fix_next",
        "medium": "fix_next",
        "p2 moderate": "fix_next",
        "p2": "fix_next",
        "provisional": "fix_next",
        "strong": "passed_keep",
        "info": "not_proven_not_tested",
        "note": "not_proven_not_tested",
        "minor": "not_proven_not_tested",
        "low": "not_proven_not_tested",
        "p3 minor": "not_proven_not_tested",
        "p3": "not_proven_not_tested",
        "unscored": "not_proven_not_tested",
        "hypothesis": "not_proven_not_tested",
        "preserve note": "not_proven_not_tested",
    }.get(t, "not_proven_not_tested")

def section_key(f):
    return explicit_section_key(f) or section_from_severity((f or {}).get("severity"))

def action_label(f, section):
    raw = norm_token((f or {}).get("action") or (f or {}).get("next_action"))
    if raw:
        return ACTION_ALIAS.get(raw, title_case(raw))
    return {
        "clear_before_ship": "Fix",
        "fix_next": "Fix",
        "not_proven_not_tested": "Prove",
        "passed_keep": "Keep",
    }.get(section, "Prove")

def proof_label(f):
    f = f or {}
    raw = norm_token(f.get("proof") or f.get("evidence_grade") or f.get("confidence"))
    if not raw:
        return "Not tested"
    return PROOF_ALIAS.get(raw, title_case(raw))

def seg_html(segments):
    total = sum(max(num((s or {}).get("value", 0)), 0) for s in segments) or 1
    out = []
    for s in segments:
        kind = cov_kind((s or {}).get("kind"))
        c = COV.get(kind, "#334155")
        v = max(num((s or {}).get("value", 0)), 0)
        pct = max((v / total) * 100, 0)
        label = cov_label(s)
        title = esc(f"{label} — {(s or {}).get('value','')}")
        out.append(f'<span style="flex:0 0 {pct:.1f}%;background:{c}" aria-hidden="true" title="{title}"></span>')
    return "".join(out)

def legend_html(segments):
    out = []
    for s in segments:
        s = s or {}
        kind = cov_kind(s.get("kind"))
        c = COV.get(kind, "#334155")
        out.append(f'<span class="cov-key"><i class="sw" style="background:{c}"></i>'
                   f'{esc(cov_label(s))}&nbsp;<b>{esc(s.get("value", ""))}</b></span>')
    return "".join(out)

def details_html(f):
    rows = []
    for k in ("evidence", "fix", "verify"):
        if f.get(k):
            cls = "mono" if k == "evidence" else "prose"
            rows.append(f'<div class="ev-row"><div class="ev-label">{k}</div>'
                        f'<p class="ev-value {cls}">{esc(f[k])}</p></div>')
    if not rows:
        return ""
    return ('<details><summary>Evidence · Fix · Verify</summary>'
            f'<div class="ev-block">{"".join(rows)}</div></details>')

def finding_html(f, idx):
    f = f or {}
    section = section_key(f)
    accent, _, _ = SECTION.get(section, SECTION["not_proven_not_tested"])
    action = action_label(f, section)
    proof = proof_label(f)
    action_chip = f'<span class="pill pill-action" style="color:{accent};border-color:{accent}66">{esc(action)}</span>'
    proof_chip = f'<span class="pill pill-proof">{esc(proof)}</span>'
    parts = [f'<article class="finding" data-section="{section}" style="border-left-color:{accent}">',
             f'<div class="finding-top c-head"><span class="finding-num">{idx:02d}</span>{action_chip}{proof_chip}</div>',
             f'<h3>{esc(f.get("title","(untitled finding)"))}</h3>']
    if f.get("consequence"):
        parts.append(f'<p class="consequence"><span class="arrow">↳</span>{esc(f["consequence"])}</p>')
    parts.append(details_html(f))
    parts.append("</article>")
    return "".join(parts)

def render(data, interactive=False, orchestration_checkpoint=None):
    data = project_input(data, orchestration_checkpoint=orchestration_checkpoint)
    if not isinstance(data, dict): data = {}
    target = esc(data.get("target", "target"))
    gen = esc(data.get("generated_at") or datetime.date.today().isoformat())
    historical_import = data.get("import_mode") == "historical" and str(data.get("input_format") or "").startswith("legacy/")
    historical_notice = (
        '\n    <p class="muted-note">Historical import — readable for record review; not a current flagship Shipworthy run.</p>'
        if historical_import else ""
    )
    frontier = data.get("path_frontier") if isinstance(data.get("path_frontier"), dict) else None
    confidence_block = coverage_confidence_html(frontier, data.get("checkpoint"), data.get("record_counts"))
    product_cov_block = product_coverage_html(frontier)
    closure_attr = f' data-closure-state="{esc(frontier.get("closure_state"))}"' if frontier else ""

    verdict = str(data.get("verdict", "NOT READY")).upper()
    verdict_label = title_case(verdict)
    vbg, vbd, vtx = VERDICT.get(verdict, VERDICT_NEUTRAL)

    findings = data.get("findings", [])
    if not isinstance(findings, list): findings = []
    findings = [f for f in findings if isinstance(f, dict)]
    findings.sort(key=lambda f: (SECTION_ORDER.index(section_key(f)), sev_key(f.get("severity")), str(f.get("title", ""))))

    # summary: prefer new action-first summary fields; otherwise derive from findings.
    s = data.get("summary") if isinstance(data.get("summary"), dict) else None
    if s and any(k in s for k in ("clear_before_ship", "clear", "fix_next", "not_proven_not_tested", "not_proven", "passed_keep", "passed")):
        clear = s.get("clear_before_ship", s.get("clear", 0))
        fix_next = s.get("fix_next", 0)
        not_proven = s.get("not_proven_not_tested", s.get("not_proven", 0))
        passed_keep = s.get("passed_keep", s.get("passed", 0))
    else:
        from collections import Counter
        c = Counter(section_key(f) for f in findings)
        clear = c.get("clear_before_ship", 0)
        fix_next = c.get("fix_next", 0)
        not_proven = c.get("not_proven_not_tested", 0)
        passed_keep = c.get("passed_keep", 0)

    cov = data.get("coverage") if isinstance(data.get("coverage"), dict) else {}
    segs = cov.get("segments", [])
    if not isinstance(segs, list): segs = []
    segs = [s for s in segs if isinstance(s, dict)]

    if segs:
        covered = sum(num(s.get("value")) for s in segs if cov_kind(s.get("kind")) == "covered")
        total = num(cov.get("total_paths"), 0)
        if total <= 0:
            total = sum(num(s.get("value")) for s in segs)
        pct = round(100 * covered / total) if total > 0 else 0
        cov_sum = (f'<p class="cov-line"><strong>{pct}%</strong>&nbsp; covered · '
                   f'{covered:g} of {total:g} discovered paths</p>') if total > 0 else ''
        aria = "Coverage breakdown" + (f" of {total:g} discovered paths: " if total > 0 else ": ")
        aria += ", ".join(f'{num(s.get("value")):g} {cov_label(s)}' for s in segs)
        cov_block = (f'<section class="section"><div class="section-head"><h2>Coverage</h2></div>{cov_sum}'
                     f'<div class="cov-bar" role="img" aria-label="{esc(aria)}">{seg_html(segs)}</div>'
                     f'<div class="cov-legend">{legend_html(segs)}</div></section>')
    elif frontier:
        cov_block = ""
    else:
        cov_block = ('<section class="section"><div class="section-head"><h2>Coverage</h2></div>'
                     '<div class="muted-note">Coverage not recorded for this run.</div></section>')

    if findings:
        buckets = {section: [] for section in SECTION_ORDER}
        for f in findings:
            buckets[section_key(f)].append(f)
        parts = ['<div class="group-label">Findings</div>']
        for section in SECTION_ORDER:
            b = buckets[section]
            if not b:
                continue
            accent, label, tier = SECTION[section]
            parts.append(f'<section class="section {tier}">'
                         f'<div class="section-head"><h2>{label}</h2><span class="count">{len(b)}</span></div>')
            parts.extend(finding_html(f, i) for i, f in enumerate(b, 1))
            parts.append('</section>')
        find_block = "".join(parts)
    else:
        find_block = ('<section class="section"><div class="section-head"><h2>Findings</h2></div>'
                      '<article class="finding" style="border-left-color:#34D399">'
                      '<h3>No blocking or open findings were recorded.</h3></article></section>')

    debt_records = data.get("evidence_debt", [])
    if not isinstance(debt_records, list):
        debt_records = []
    if debt_records:
        debt_cards = ['<section class="section tier-not-proven"><div class="section-head">'
                      '<h2>Evidence Debt / Not Proven</h2>'
                      f'<span class="count">{len(debt_records)}</span></div>']
        debt_cards.extend(finding_html(record, i) for i, record in enumerate(debt_records, 1))
        debt_cards.append('</section>')
        find_block += "".join(debt_cards)

    ck = data.get("checkpoint") if isinstance(data.get("checkpoint"), dict) else {}
    ck_rows = []
    if ck.get("target_intent"): ck_rows.append(("target intent", ck["target_intent"]))
    if ck.get("target_calibration"): ck_rows.append(("target calibration", ck["target_calibration"]))
    if ck.get("target_calibration_reason"): ck_rows.append(("calibration reason", ck["target_calibration_reason"]))
    if ck.get("producer"): ck_rows.append(("producer", ck["producer"]))
    if ck.get("completion_status"): ck_rows.append(("completion status", ck["completion_status"]))
    if ck.get("gate_policy"): ck_rows.append(("gate policy", ck["gate_policy"]))
    if ck.get("source_report_input"): ck_rows.append(("source report input", ck["source_report_input"]))
    if isinstance(ck.get("lanes"), list) and ck["lanes"]: ck_rows.append(("lanes", " · ".join(str(x) for x in ck["lanes"])))
    if ck.get("audit_status"): ck_rows.append(("audit status", ck["audit_status"]))
    if ck.get("goal_mode_status") or data.get("goal_mode_status"):
        ck_rows.append(("goal mode status", ck.get("goal_mode_status") or data.get("goal_mode_status")))
    if ck.get("goal_completion_status"):
        ck_rows.append(("goal completion status", ck["goal_completion_status"]))
    if ck.get("goal_mode_objective") or data.get("goal_mode_objective"):
        ck_rows.append(("goal mode objective", ck.get("goal_mode_objective") or data.get("goal_mode_objective")))
    auth = ck.get("multi_agent_authorization") or ck.get("authorization")
    if auth: ck_rows.append(("authorization", auth))
    if "frontend_path_walk_performed" in ck:
        ck_rows.append(("frontend path-walk", "yes" if ck.get("frontend_path_walk_performed") else "no"))
    if ck.get("frontend_tool"): ck_rows.append(("frontend tool", ck["frontend_tool"]))
    if ck.get("runtime_target"): ck_rows.append(("runtime target", ck["runtime_target"]))
    if ck.get("path_walk_status"): ck_rows.append(("path walk status", ck["path_walk_status"]))
    if ck.get("downgrade_reason"): ck_rows.append(("downgrade reason", ck["downgrade_reason"]))
    if ck.get("report_generation_status") or data.get("report_generation_status"):
        ck_rows.append(("report generation", ck.get("report_generation_status") or data.get("report_generation_status")))
    if ck.get("report_path") or data.get("report_path"):
        ck_rows.append(("report path", ck.get("report_path") or data.get("report_path")))
    if ck.get("ledger_path") or data.get("ledger_path"):
        ck_rows.append(("ledger path", ck.get("ledger_path") or data.get("ledger_path")))
    evidence_locations = ck.get("evidence_locations") or data.get("evidence_locations")
    if evidence_locations:
        ck_rows.append(("evidence locations", row_text(evidence_locations)))
    if ck.get("_control_census_summary"):
        ck_rows.append(("control census", ck["_control_census_summary"]))
    if ck.get("zero_yield_pass_ids"):
        ck_rows.append(("zero-yield passes", row_text(ck["zero_yield_pass_ids"])))
    if ck.get("browser_failover_status"):
        ck_rows.append(("browser failover", ck["browser_failover_status"]))
    if ck.get("recovery_status"):
        ck_rows.append(("recovery status", ck["recovery_status"]))
    if ck.get("raw_lane_output_paths"):
        ck_rows.append(("raw lane outputs", row_text(ck["raw_lane_output_paths"])))
    if ck.get("raw_verifier_output_paths"):
        ck_rows.append(("raw verifier outputs", row_text(ck["raw_verifier_output_paths"])))
    if isinstance(ck.get("evidence_debt_actions"), list):
        ck_rows.append(("active evidence-debt actions", len(ck["evidence_debt_actions"])))
    frontier_fields = [
        ("frontier total", "frontier_total"),
        ("frontier covered", "frontier_covered"),
        ("frontier sampled", "frontier_sampled"),
        ("frontier blocked", "frontier_blocked"),
        ("frontier missing", "frontier_missing"),
        ("frontier evidence debt", "frontier_evidence_debt"),
        ("frontier unattempted", "frontier_unattempted"),
        ("new paths last wave", "new_paths_last_wave"),
        ("new paths previous wave", "new_paths_previous_wave"),
        ("exhaustion status", "exhaustion_status"),
        ("exhaustion downgrade reason", "exhaustion_downgrade_reason"),
        ("next frontier batch", "next_frontier_batch"),
    ]
    for label, key in frontier_fields:
        value = ck.get(key, data.get(key))
        if value not in (None, "", []):
            ck_rows.append((label, row_text(value)))
    if ck.get("mode"):     ck_rows.append(("mode", ck["mode"]))
    if ck.get("verifier"): ck_rows.append(("verifier", ck["verifier"]))
    if isinstance(ck.get("omitted"), list):
        for o in ck["omitted"]: ck_rows.append(("omitted", o))
    ck_html = ("".join(f'<div class="orch-row"><div class="orch-label">{esc(k)}</div>'
                       f'<div class="orch-value">{esc(v)}</div></div>'
                       for k, v in ck_rows)
               or '<div class="muted-note">No orchestration checkpoint recorded.</div>')

    illus = ('<div class="illus">Illustrative example — the report format is real; '
             'the contents are a sample, not a live run.</div>') if data.get("illustrative") else ""

    # optional, opt-in client-side interactivity (no external deps, no network)
    controls = ""
    script = ""
    controls_css = ""
    if interactive:
        controls_css = (
            "  .controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 12px}\n"
            "  .fbtn{background:#101E36;border:1px solid #243350;border-radius:16px;padding:4px 12px;"
            "font-size:12.5px;color:#8B9AB8;cursor:pointer;font-family:inherit}\n"
            "  .fbtn:not(.on){opacity:.4}\n"
            "  .search{flex:1;min-width:160px;background:#101E36;border:1px solid #243350;border-radius:16px;"
            "padding:5px 12px;color:#D7DEEC;font-size:12.5px;font-family:inherit}\n"
            "  .search::placeholder{color:#5F6E90}\n"
            "  .is-hidden{display:none}\n"
            "  .finding[data-section] .c-head{cursor:pointer}\n"
            "  .finding.collapsed .consequence,.finding.collapsed details{display:none}\n")

        sections_present = []
        for section in SECTION_ORDER:
            if any(section_key(f) == section for f in findings):
                sections_present.append(section)
        btns = "".join(
            f'<button type="button" class="fbtn on" data-section="{section}" '
            f'style="border-color:{SECTION[section][0]}66;color:{SECTION[section][0]}">{SECTION[section][1]}</button>'
            for section in sections_present)
        controls = (f'<div class="controls">{btns}'
                    f'<input class="search" type="search" placeholder="Filter findings\u2026" aria-label="Filter findings">'
                    f'<button type="button" class="fbtn" id="collapseAll">Collapse all</button></div>')
        script = ("<script>(function(){"
                  "var on={};document.querySelectorAll('.fbtn[data-section]').forEach(function(b){on[b.dataset.section]=true;"
                  "b.addEventListener('click',function(){on[b.dataset.section]=!on[b.dataset.section];"
                  "b.classList.toggle('on');apply();});});"
                  "var q='';var si=document.querySelector('.search');"
                  "if(si){si.addEventListener('input',function(){q=si.value.toLowerCase();apply();});}"
                  "document.querySelectorAll('.c-head').forEach(function(h){h.addEventListener('click',function(e){"
                  "if(e.target.tagName==='A')return;h.closest('.finding').classList.toggle('collapsed');});});"
                  "var ca=document.getElementById('collapseAll');if(ca){ca.addEventListener('click',function(){"
                  "var cards=document.querySelectorAll('.finding[data-section]');"
                  "var anyOpen=[].some.call(cards,function(c){return !c.classList.contains('collapsed');});"
                  "cards.forEach(function(c){c.classList.toggle('collapsed',anyOpen);});"
                  "ca.textContent=anyOpen?'Expand all':'Collapse all';});}"
                  "function apply(){document.querySelectorAll('.finding[data-section]').forEach(function(c){"
                  "var okS=on[c.dataset.section];var okQ=!q||c.textContent.toLowerCase().indexOf(q)>-1;"
                  "c.classList.toggle('is-hidden',!(okS&&okQ));});"
                  "document.querySelectorAll('.section[class*=tier-]').forEach(function(s){"
                  "var vis=[].some.call(s.querySelectorAll('.finding'),function(c){return !c.classList.contains('is-hidden');});"
                  "s.classList.toggle('is-hidden',!vis);});}"
                  "})();</script>")
    return f"""<!doctype html>
<html lang="en"{closure_attr}><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Shipworthy Readiness Report — {target}</title>
<style>
  :root{{color-scheme:dark;--void:#0A1526;--panel:#101E36;--panel-raised:#16283F;--hairline:#243350;--hairline-soft:#1B2A44;--paper:#EDF1F8;--prose:#D7DEEC;--muted:#8B9AB8;--muted-dim:#647089;--radius:14px}}
  *{{box-sizing:border-box}}
  html{{background:var(--void)}}
  body{{margin:0;background:radial-gradient(ellipse 900px 460px at 50% -8%,#142644 0%,transparent 60%),var(--void);color:var(--paper);
    font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    line-height:1.5;-webkit-font-smoothing:antialiased;overflow-wrap:anywhere}}
  code,.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace}}
  .page{{max-width:740px;margin:0 auto;padding:34px 20px 72px}}
  .masthead{{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}}
  .brand{{font-weight:700;font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:{vtx}}}
  .badge-readonly{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:10.5px;letter-spacing:.04em;color:var(--muted);border:1px solid var(--hairline);padding:4px 10px;border-radius:999px;text-transform:uppercase;white-space:nowrap}}
  h1.title{{font-family:Georgia,serif;font-weight:600;font-size:clamp(28px,6.4vw,36px);margin:10px 0 6px;color:var(--paper);letter-spacing:0}}
  .meta-line{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px;color:var(--muted);margin:0 0 8px}}
  .meta-line .sep{{color:var(--hairline-soft);margin:0 7px}}
  .verdict-zone{{display:flex;flex-direction:column;align-items:center;text-align:center;margin:40px 0 12px}}
  .stamp{{position:relative;display:inline-block;transform:rotate(-4deg);border:3px solid {vtx};border-radius:8px;padding:14px 30px 12px;margin-bottom:22px}}
  .stamp::before{{content:"";position:absolute;inset:4px;border:1px solid {vtx};border-radius:4px;opacity:.55;pointer-events:none}}
  .stamp-text{{display:block;font-family:Georgia,serif;font-weight:900;font-size:clamp(30px,8vw,42px);letter-spacing:.03em;color:{vtx};text-transform:none;line-height:1}}
  .stamp-sub{{display:block;margin-top:5px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:9.5px;letter-spacing:.18em;text-transform:uppercase;color:{vbd}}}
  .epigraph{{font-family:Georgia,serif;font-style:italic;font-weight:500;font-size:16px;color:var(--muted);max-width:400px;margin:0 0 26px}}
  .stats-row{{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}}
  .stat-chip{{display:flex;align-items:baseline;gap:8px;border:1px solid var(--hairline);background:var(--panel);border-radius:10px;padding:9px 16px}}
  .stat-chip .n{{font-family:Georgia,serif;font-weight:700;font-size:20px;line-height:1}}
  .stat-chip .l{{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.07em;color:var(--muted)}}
  .c-clear .n{{color:{SECTION['clear_before_ship'][0]}}}.c-fixnext .n{{color:{SECTION['fix_next'][0]}}}.c-notproven .n{{color:{SECTION['not_proven_not_tested'][0]}}}.c-passed .n{{color:{SECTION['passed_keep'][0]}}}
  .read-key{{max-width:660px;margin:18px auto 0;color:var(--muted);font-size:13px;line-height:1.65;text-align:left;border:1px solid var(--hairline-soft);background:#0D1A30;border-radius:10px;padding:12px 14px}}
  .read-key b{{color:var(--paper)}}.key-actions{{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}}.key-chip{{font-weight:700;font-size:10px;letter-spacing:.06em;text-transform:uppercase;padding:2px 8px;border-radius:999px;border:1px solid var(--hairline);color:var(--paper)}}
  .confidence-summary{{margin:34px 0 12px;border:1px solid var(--hairline);background:#0D1A30;border-radius:var(--radius);padding:18px 20px}}.confidence-summary .section-head{{margin-bottom:10px}}.confidence-grid{{display:grid;gap:9px}}.confidence-grid p{{display:grid;grid-template-columns:155px 1fr;gap:12px;margin:0;font-size:12.8px;color:var(--prose)}}.confidence-grid b{{color:var(--paper);font-size:11px;letter-spacing:.04em}}.confidence-grid span{{color:var(--muted)}}
  .section{{margin-top:56px}}
  .section-head{{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin-bottom:18px;padding-bottom:11px;border-bottom:1px solid var(--hairline)}}
  .section-head h2{{font-weight:700;font-size:13px;letter-spacing:.14em;text-transform:uppercase;margin:0;color:var(--paper)}}
  .section-head .count{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;color:var(--muted-dim)}}
  .group-label{{margin-top:56px;margin-bottom:-30px;font-weight:700;font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:var(--muted-dim)}}
  .tier-clear-before-ship .section-head h2{{color:{SECTION['clear_before_ship'][0]}}}.tier-fix-next .section-head h2{{color:{SECTION['fix_next'][0]}}}.tier-not-proven .section-head h2{{color:{SECTION['not_proven_not_tested'][0]}}}.tier-passed-keep .section-head h2{{color:{SECTION['passed_keep'][0]}}}
  .cov-line{{font-size:14.5px;color:var(--prose);margin:0 0 16px}}.cov-line strong{{font-family:Georgia,serif;font-weight:700;font-size:21px;color:var(--paper)}}
  .cov-bar{{display:flex;width:100%;height:14px;border-radius:7px;overflow:hidden;background:var(--panel-raised);border:1px solid var(--hairline);margin-bottom:18px}}
  .cov-bar span{{height:100%;display:block}}
  .cov-legend{{display:flex;flex-wrap:wrap;gap:9px 20px}}.cov-key{{display:flex;align-items:center;gap:7px;font-size:12.5px;color:var(--muted)}}.cov-key .sw{{width:9px;height:9px;border-radius:2px;flex:none}}.cov-key b{{color:var(--paper);font-weight:700;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
  .coverage-status{{display:flex;align-items:flex-start;gap:12px;margin-bottom:16px}}.coverage-status p{{margin:1px 0;color:var(--prose);font-size:13.5px}}.closure-chip{{flex:none;border:1px solid #34D39966;color:#34D399;border-radius:999px;padding:3px 9px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.06em}}
  .coverage-metrics{{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 14px}}.coverage-metric{{border:1px solid var(--hairline);background:var(--panel);border-radius:8px;padding:7px 10px;color:var(--muted);font-size:12px}}.coverage-metric b{{color:var(--paper);font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
  .coverage-meta{{color:var(--muted);font-size:12.5px;line-height:1.7}}.coverage-meta b{{color:var(--prose)}}.coverage-features{{border:1px solid var(--hairline);border-radius:10px;overflow:hidden;margin-top:16px}}.coverage-feature,.coverage-proof{{display:flex;justify-content:space-between;gap:14px;padding:10px 12px;border-bottom:1px solid var(--hairline-soft);font-size:12.5px}}.coverage-feature:last-child,.coverage-proof:last-child{{border-bottom:0}}.coverage-feature span,.coverage-proof span{{color:var(--muted);text-align:right}}.coverage-tag{{display:inline-block;margin:3px 5px 3px 0;border:1px solid var(--hairline);border-radius:999px;padding:3px 8px;color:var(--muted);font-size:11px}}
  .muted-note{{color:var(--muted);font-size:13px;font-style:italic;margin-bottom:6px}}
  .finding{{background:var(--panel);border:1px solid var(--hairline);border-left:4px solid var(--hairline);border-radius:var(--radius);padding:19px 21px;margin-bottom:14px;overflow-wrap:anywhere}}
  .finding-top{{display:flex;align-items:center;gap:10px;margin-bottom:9px;flex-wrap:wrap}}.finding-num{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;color:var(--muted-dim)}}
  .pill{{font-weight:700;font-size:10px;letter-spacing:.06em;text-transform:uppercase;padding:3px 9px;border-radius:999px;border:1px solid;white-space:nowrap}}.pill-proof{{color:var(--muted);border-color:var(--hairline)}}
  .finding h3{{font-weight:600;font-size:16.5px;line-height:1.35;margin:0 0 9px;color:var(--paper)}}.consequence{{font-family:Georgia,serif;font-style:italic;font-size:14px;line-height:1.5;color:var(--muted);margin:0}}.consequence .arrow{{font-style:normal;color:var(--muted-dim);margin-right:7px}}
  details{{margin-top:12px}}summary{{cursor:pointer;list-style:none;display:inline-flex;align-items:center;gap:6px;font-weight:700;font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:{vtx};padding:6px 2px;user-select:none;border-radius:4px}}summary::-webkit-details-marker{{display:none}}summary::before{{content:"›";display:inline-block;font-size:16px;line-height:1;transition:transform .15s ease}}details[open] summary::before{{transform:rotate(90deg)}}summary:focus-visible{{outline:2px solid {vtx};outline-offset:3px}}
  .ev-block{{margin-top:6px;padding-top:6px}}.ev-row{{margin-bottom:13px}}.ev-row:last-child{{margin-bottom:0}}.ev-label{{font-weight:700;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted-dim);margin-bottom:5px}}.ev-value{{margin:0}}.ev-value.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.2px;line-height:1.65;color:var(--prose);background:var(--panel-raised);border:1px solid var(--hairline-soft);border-radius:8px;padding:11px 13px}}.ev-value.prose{{font-size:13.8px;line-height:1.6;color:var(--prose)}}
  .orch{{background:var(--panel);border:1px solid var(--hairline);border-radius:var(--radius);padding:6px 22px}}.orch-row{{display:grid;grid-template-columns:118px 1fr;gap:16px;padding:15px 0;border-bottom:1px solid var(--hairline-soft)}}.orch-row:last-child{{border-bottom:none}}.orch-label{{font-weight:700;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted-dim);padding-top:1px}}.orch-value{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.3px;line-height:1.65;color:var(--prose)}}
  footer{{margin-top:60px;padding-top:26px;border-top:1px solid var(--hairline);color:var(--muted-dim);font-size:12px;line-height:1.7}}.illus{{margin-top:10px;color:var(--muted-dim);font-size:12px}}
{controls_css}  a{{color:#34D399}}
  @media print{{
    .controls{{display:none !important}}
    .is-hidden{{display:block !important}}
    .finding.collapsed .consequence,.finding.collapsed details{{display:block !important}}
    body{{background:#fff;color:#0B1220}}
    .page{{max-width:none;padding:0}}
    footer,.section-head{{border-color:#ccd3df}}
    .brand{{color:#0B1220}} .brand .g{{color:#0B8A5B}}
    .meta-line,.muted-note,.cov-line,.cov-key,.illus,.consequence,.confidence-grid span,.read-key{{color:#4A5568}}
    h1.title,.confidence-grid b,.confidence-summary .section-head h2{{color:#111}}
    .confidence-summary,.read-key,.stat-chip{{background:#fff;border-color:#ccd3df}}
    .cov-line strong,.finding h3,.ev-value.mono,.ev-value.prose,.orch-value{{color:#111}}
    .ev-label,.orch-label{{color:#556}}
    .finding,.orch{{background:#fff;border-color:#ccd3df;break-inside:avoid;page-break-inside:avoid}}
    .pill,.key-chip{{color:#111 !important;border-color:#bbb !important}}
    footer{{color:#555}} a{{color:#0B1220}}
  }}
  @media (max-width:460px){{.orch-row,.confidence-grid p{{grid-template-columns:1fr;gap:5px;padding:5px 0}}}}
  @media (prefers-reduced-motion:reduce){{summary::before{{transition:none}}}}
</style></head>
<body><div class="page">
  <header>
    <div class="masthead"><span class="brand">Shipworthy</span><span class="badge-readonly">Read-only</span></div>
    <h1 class="title">Readiness Report</h1>
    <p class="meta-line">{target}<span class="sep">·</span>{gen}</p>{historical_notice}
  </header>
  <section class="verdict-zone">
    <div class="stamp"><span class="stamp-text">{esc(verdict_label)}</span><span class="stamp-sub">Status · Evidence gated</span></div>
    <p class="epigraph">&ldquo;nothing is called &lsquo;ready&rsquo; without evidence&rdquo;</p>
    <div class="stats-row">
      <div class="stat-chip c-clear"><span class="n">{esc(clear)}</span><span class="l">Required Fixes</span></div>
      <div class="stat-chip c-fixnext"><span class="n">{esc(fix_next)}</span><span class="l">Fix Next</span></div>
      <div class="stat-chip c-notproven"><span class="n">{esc(not_proven)}</span><span class="l">Not Proven</span></div>
      <div class="stat-chip c-passed"><span class="n">{esc(passed_keep)}</span><span class="l">Passed</span></div>
    </div>
    <p class="read-key"><b>Read this by action:</b> Clear Before Ship items block readiness. Fix Next items are real but non-blocking. Not Proven / Not Tested items are not passes. Passed / Keep items worked under the tested conditions. Each card says what to do and how strong the proof is.<span class="key-actions"><span class="key-chip">Fix</span><span class="key-chip">Prove</span><span class="key-chip">Decide</span><span class="key-chip">Skip</span><span class="key-chip">Keep</span></span></p>
  </section>
  {confidence_block}
  {controls}
  {find_block}
  {product_cov_block}
  {cov_block}
  <section class="section"><div class="section-head"><h2>Orchestration Checkpoint</h2></div><div class="orch">{ck_html}</div></section>
  <footer>
    <b style="color:#7E8CAD">Proof labels:</b> Confirmed (directly observed) &gt; Partial (some proof, incomplete coverage) &gt; Inferred (not directly observed) &gt; Not tested.
    Findings lead; scores never appear naked. Read-only by default — fixes are proposed with a verification step, not applied.
    {illus}
  </footer>
{script}
</div></body></html>"""

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    interactive = "--interactive" in sys.argv[1:]
    if len(args) != 2:
        print("usage: render_report.py INPUT.json OUTPUT.html [--interactive]", file=sys.stderr)
        sys.exit(2)
    inp = args[0]
    out = args[1]
    try:
        if os.path.getsize(inp) > MAX_INPUT_BYTES:
            print(f"error: input too large (limit {MAX_INPUT_BYTES} bytes)", file=sys.stderr); sys.exit(2)
        with open(inp, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print(f"error: input file not found: {inp}", file=sys.stderr); sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"error: {inp} is not valid JSON ({e})", file=sys.stderr); sys.exit(2)
    try:
        validate_canonical_input(data, evidence_root=os.path.dirname(os.path.abspath(inp)))
        checkpoint = load_orchestration_checkpoint(inp, data)
        if checkpoint:
            checkpoint["report_generation_status"] = "rendered"
            checkpoint["report_path"] = os.path.abspath(out)
        html_out = render(data, interactive=interactive, orchestration_checkpoint=checkpoint)
    except ValueError as e:
        print(f"error: canonical report input is invalid ({e})", file=sys.stderr); sys.exit(2)
    atomic_write_text(out, html_out)
    print(f"wrote {out} ({len(html_out)} bytes) from {inp}")

if __name__ == "__main__":
    main()

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ORCHESTRATOR = ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator"
SCRIPT_DIR = ORCHESTRATOR / "scripts"
SCRIPT = SCRIPT_DIR / "render_report.py"
BUNDLE_SCRIPT = SCRIPT_DIR / "make_bundle.py"
FIXTURE = ROOT / "tests/skill_product/fixtures/gauntlet-report-input.json"
sys.path.insert(0, str(SCRIPT_DIR))

from render_report import load_orchestration_checkpoint, render, validate_canonical_input  # noqa: E402


class OrchestrationCompletionGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def candidate(self) -> dict:
        candidate = deepcopy(self.fixture)
        frontier = candidate["source_ledger"]["path_frontier"]
        digest = hashlib.sha256(
            json.dumps(
                sorted(row["semantic_key"] for row in frontier["rows"]),
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        for discovery_pass in frontier["discovery_passes"]:
            discovery_pass["starting_frontier_digest"] = digest
            discovery_pass["ending_frontier_digest"] = digest
        return candidate

    @staticmethod
    def semantic_digest(keys: list[str]) -> str:
        return hashlib.sha256(
            json.dumps(sorted(keys), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def sync_frontier_digests(candidate: dict) -> None:
        frontier = candidate["source_ledger"]["path_frontier"]
        digest = hashlib.sha256(
            json.dumps(
                sorted(row["semantic_key"] for row in frontier["rows"]),
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        for discovery_pass in frontier["discovery_passes"]:
            discovery_pass["starting_frontier_digest"] = digest
            discovery_pass["ending_frontier_digest"] = digest

    def checkpoint(self, candidate: dict) -> dict:
        frontier = candidate["source_ledger"]["path_frontier"]
        control_keys = [
            row["semantic_key"]
            for row in frontier["rows"]
            if row["kind"] == "control"
        ]
        return {
            "target_name": "Gauntlet Projects",
            "lanes": [
                "runtime — completed — evidence/raw-runtime.json",
                "verifier — approved — evidence/raw-verifier.json",
            ],
            "mode": "authorized native Codex agents",
            "multi_agent_authorization": "explicitly authorized",
            "frontend_path_walk_performed": True,
            "frontend_tool": "native Codex browser",
            "runtime_target": "local fixture",
            "path_walk_status": "full",
            "verifier": "approved",
            "omitted": [],
            "ledger_path": "readiness-ledger.json",
            "evidence_locations": ["evidence/"],
            "exhaustion_status": "closed_multi_source",
            "audit_status": "complete",
            "goal_mode_status": "active",
            "goal_completion_status": "active",
            "raw_lane_output_paths": ["evidence/raw-runtime.json"],
            "raw_verifier_output_paths": ["evidence/raw-verifier.json"],
            "control_census_paths": [
                "evidence/runtime-control-census.json",
                "evidence/static-control-census.json",
            ],
            "zero_yield_pass_ids": [
                item["id"] for item in frontier["discovery_passes"][-2:]
            ],
            "evidence_debt_actions": [],
            "recovery_status": "not_needed",
            "recovery_attempts": [],
            "recovery_receipt_paths": [],
            "browser_failover_status": "not_needed",
            "browser_failover_receipt_paths": [],
        }

    def materialize_checkpoint_evidence(
        self,
        root: Path,
        checkpoint: dict,
        candidate: dict,
        census_keys: list[str] | None = None,
        receipt_payload: dict | list[dict] | None = None,
    ) -> None:
        references = set(checkpoint["raw_lane_output_paths"])
        references.update(checkpoint["raw_verifier_output_paths"])
        for reference in references:
            path = root / reference
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("raw evidence", encoding="utf-8")
        frontier = candidate["source_ledger"]["path_frontier"]
        control_keys = census_keys if census_keys is not None else [
            row["semantic_key"] for row in frontier["rows"] if row["kind"] == "control"
        ]
        method_families = [
            "runtime_structural_inventory",
            "static_implementation_inventory",
        ]
        for reference, method_family in zip(
            checkpoint["control_census_paths"],
            method_families,
        ):
            path = root / reference
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(
                    {
                        "method_family": method_family,
                        "semantic_keys": control_keys,
                        "digest": self.semantic_digest(control_keys),
                        "frontier_digest": hashlib.sha256(
                            json.dumps(
                                sorted(row["semantic_key"] for row in frontier["rows"]),
                                ensure_ascii=False,
                                separators=(",", ":"),
                            ).encode("utf-8")
                        ).hexdigest(),
                        "unmatched_controls": [],
                    }
                ),
                encoding="utf-8",
            )
        for index, reference in enumerate(checkpoint["browser_failover_receipt_paths"]):
            path = root / reference
            path.parent.mkdir(parents=True, exist_ok=True)
            selected_receipt = (
                receipt_payload[index]
                if isinstance(receipt_payload, list)
                else receipt_payload
            )
            path.write_text(
                json.dumps(
                    selected_receipt or {
                        "native_error": "browser profile locked",
                        "cleanup_result": "owning native context released",
                        "fallback_kind": "independent_playwright",
                        "process_or_context_id": "pw-context-1",
                        "isolation_proof": "separate Playwright browser process and profile",
                        "fallback_result": "recovered",
                        "remaining_evidence_debt": [],
                    }
                ),
                encoding="utf-8",
            )

    @staticmethod
    def materialize_canonical_evidence(root: Path, candidate: dict) -> None:
        references = {candidate["source_ledger"]["path_frontier"]["manifest_artifact"]}
        for row in candidate["source_ledger"]["path_frontier"]["rows"]:
            references.update(row.get("evidence_refs", []))
            for observation in row.get("observations", []):
                references.update(observation.get("evidence_refs", []))
        for finding in candidate["source_ledger"]["findings"]:
            references.update(finding.get("evidence_refs", []))
        for reference in references:
            path = root / reference
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("canonical evidence", encoding="utf-8")

    def load(
        self,
        candidate: dict,
        checkpoint: dict,
        census_keys: list[str] | None = None,
        receipt_payload: dict | list[dict] | None = None,
    ) -> dict:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            input_path = root / "report-input.json"
            input_path.write_text(json.dumps(candidate), encoding="utf-8")
            (root / "readiness-ledger.json").write_text(
                json.dumps(candidate["source_ledger"]),
                encoding="utf-8",
            )
            self.materialize_checkpoint_evidence(
                root,
                checkpoint,
                candidate,
                census_keys,
                receipt_payload,
            )
            (root / "orchestration-checkpoint.json").write_text(
                json.dumps(checkpoint),
                encoding="utf-8",
            )
            return load_orchestration_checkpoint(str(input_path), candidate)

    def test_accepts_complete_audit_with_reconciled_operational_proof(self) -> None:
        candidate = self.candidate()
        checkpoint = self.checkpoint(candidate)
        loaded = self.load(candidate, checkpoint)
        self.assertEqual("complete", loaded["audit_status"])
        self.assertEqual("active", loaded["goal_completion_status"])

    def test_rejects_persistent_goal_completion_while_audit_is_incomplete(self) -> None:
        candidate = self.candidate()
        candidate["source_ledger"]["completion_status"] = "incomplete"
        candidate["source_ledger"]["readiness_disposition"] = "cannot_determine"
        checkpoint = self.checkpoint(candidate)
        checkpoint["audit_status"] = "active"
        checkpoint["goal_completion_status"] = "complete"
        with self.assertRaisesRegex(ValueError, "persistent goal.*audit"):
            self.load(candidate, checkpoint)

    def test_legacy_nonfrontier_report_stays_readable_without_claiming_closure(self) -> None:
        candidate = self.candidate()
        candidate["source_ledger"].pop("path_frontier")
        validate_canonical_input(candidate)
        report = render(candidate)
        self.assertIn("Product coverage not recorded for this run.", report)
        self.assertNotIn('data-closure-state="closed_multi_source"', report)

    def test_rejects_malformed_or_unknown_shipworthy_schema_identity(self) -> None:
        candidate = self.candidate()
        cases = (
            (
                {
                    "schema_name": "shipworthy/readiness-report-input",
                    "schema_version": "1.0",
                },
                "source_ledger",
            ),
            (
                {**candidate, "schema_version": "9.9"},
                "unsupported Shipworthy schema version",
            ),
            (
                {
                    "schema_name": "shipworthy/readiness-report-input-typo",
                    "schema_version": "1.0",
                },
                "unknown Shipworthy schema name",
            ),
        )
        for value, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    validate_canonical_input(value)

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            input_path = root / "malformed.json"
            output_path = root / "readiness-report.html"
            input_path.write_text(json.dumps(cases[0][0]), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(2, result.returncode)
            self.assertFalse(output_path.exists())

    def test_rejects_complete_audit_with_unattempted_material_row(self) -> None:
        candidate = self.candidate()
        candidate["source_ledger"]["path_frontier"]["rows"][3]["status"] = "unattempted"
        checkpoint = self.checkpoint(candidate)
        with self.assertRaisesRegex(ValueError, "unresolved material frontier"):
            self.load(candidate, checkpoint)

    def test_rejects_covered_control_without_attempt_and_evidence(self) -> None:
        candidate = self.candidate()
        control = next(
            row
            for row in candidate["source_ledger"]["path_frontier"]["rows"]
            if row["kind"] == "control" and row["status"] == "covered"
        )
        control["attempt_count"] = 0
        control["evidence_refs"] = []
        with self.assertRaisesRegex(ValueError, "covered material.*attempt.*evidence"):
            validate_canonical_input(candidate)

    def test_rejects_sampled_safe_material_control_in_complete_audit(self) -> None:
        candidate = self.candidate()
        control = next(
            row
            for row in candidate["source_ledger"]["path_frontier"]["rows"]
            if row["kind"] == "control" and row["material"]
        )
        control["status"] = "sampled_with_justification"
        control["sample_justification"] = "Representative sample."
        control["attempt_count"] = 0
        control["evidence_refs"] = []
        with self.assertRaisesRegex(ValueError, "safe material control.*direct proof"):
            validate_canonical_input(candidate)

    def test_rejects_complete_ledger_with_missing_artifact(self) -> None:
        candidate = self.candidate()
        candidate["source_ledger"]["artifacts"] = [
            {"artifact_id": "ART-MISSING", "availability": "missing"}
        ]
        with self.assertRaisesRegex(ValueError, "complete ledger.*missing.*artifact"):
            validate_canonical_input(candidate)

    def test_rejects_confirmed_finding_without_confirmed_approved_artifact_proof(self) -> None:
        candidate = self.candidate()
        finding = candidate["source_ledger"]["findings"][0]
        finding["proof"] = "Confirmed"
        finding["confidence"] = "Hypothesis"
        finding["verifier_status"] = "blocked"
        finding["artifact_ids"] = []
        with self.assertRaisesRegex(ValueError, "Confirmed finding"):
            validate_canonical_input(candidate)

    def test_rejects_control_key_that_does_not_derive_from_parent_surface(self) -> None:
        candidate = self.candidate()
        control = next(
            row
            for row in candidate["source_ledger"]["path_frontier"]["rows"]
            if row["id"] == "PF-C2"
        )
        control["semantic_key"] = (
            "control:surface:/evil:normal:member:desktop:delete:button:destructive"
        )
        self.sync_frontier_digests(candidate)
        with self.assertRaisesRegex(ValueError, "control semantic key.*parent surface"):
            validate_canonical_input(candidate)

    def test_rejects_transition_key_that_does_not_embed_parent_control(self) -> None:
        candidate = self.candidate()
        transition = next(
            row
            for row in candidate["source_ledger"]["path_frontier"]["rows"]
            if row["kind"] == "transition"
        )
        transition["semantic_key"] = (
            "transition:editing:control:surface:/projects:normal:member:desktop:"
            "delete:button:destructive:saved"
        )
        self.sync_frontier_digests(candidate)
        with self.assertRaisesRegex(ValueError, "transition semantic key.*parent control"):
            validate_canonical_input(candidate)

    def test_rejects_duplicate_finding_and_debt_identities(self) -> None:
        candidate = self.candidate()
        candidate["source_ledger"]["findings"].append(
            deepcopy(candidate["source_ledger"]["findings"][0])
        )
        duplicate_debt = {
            "debt_id": "ED-DUPLICATE",
            "subject": "Blocked path",
            "proof_needed": "Exercise it.",
            "reason": "Unavailable.",
            "status": "blocked",
            "artifact_ids": [],
        }
        candidate["source_ledger"]["evidence_debt"] = [
            duplicate_debt,
            deepcopy(duplicate_debt),
        ]
        with self.assertRaisesRegex(ValueError, "finding ids.*debt ids"):
            validate_canonical_input(candidate)

    def test_rejects_complete_audit_when_control_census_does_not_match_frontier(self) -> None:
        candidate = self.candidate()
        checkpoint = self.checkpoint(candidate)
        census_keys = [
            row["semantic_key"]
            for row in candidate["source_ledger"]["path_frontier"]["rows"]
            if row["kind"] == "control"
        ][:-1]
        with self.assertRaisesRegex(ValueError, "control census.*frontier"):
            self.load(candidate, checkpoint, census_keys)

    def test_rejects_false_zero_yield_pass_claim(self) -> None:
        candidate = self.candidate()
        checkpoint = self.checkpoint(candidate)
        checkpoint["zero_yield_pass_ids"] = ["PASS-0", "PASS-1"]
        with self.assertRaisesRegex(ValueError, "zero-yield"):
            self.load(candidate, checkpoint)

    def test_rejects_zero_yield_passes_from_the_same_method_family(self) -> None:
        candidate = self.candidate()
        passes = candidate["source_ledger"]["path_frontier"]["discovery_passes"]
        passes[-1]["method_family"] = passes[-2]["method_family"]
        checkpoint = self.checkpoint(candidate)
        with self.assertRaisesRegex(ValueError, "distinct method families"):
            self.load(candidate, checkpoint)

    def test_rejects_checkpoint_exhaustion_that_disagrees_with_frontier(self) -> None:
        candidate = self.candidate()
        checkpoint = self.checkpoint(candidate)
        checkpoint["exhaustion_status"] = "incomplete"
        with self.assertRaisesRegex(ValueError, "exhaustion_status.*closure_state"):
            self.load(candidate, checkpoint)

    def test_rejects_complete_audit_with_an_empty_frontier(self) -> None:
        candidate = self.candidate()
        ledger = candidate["source_ledger"]
        frontier = ledger["path_frontier"]
        frontier["rows"] = []
        frontier["summary"] = {
            "intent": 0,
            "feature": 0,
            "surface": 0,
            "control": 0,
            "transition": 0,
        }
        empty_digest = hashlib.sha256(b"[]").hexdigest()
        for discovery_pass in frontier["discovery_passes"]:
            discovery_pass["starting_frontier_digest"] = empty_digest
            discovery_pass["ending_frontier_digest"] = empty_digest
        ledger["findings"] = []
        ledger["artifacts"] = []
        checkpoint = self.checkpoint(candidate)
        with self.assertRaisesRegex(ValueError, "non-empty frontier"):
            self.load(candidate, checkpoint, census_keys=[])

    def test_rejects_complete_frontend_audit_without_a_discovered_surface(self) -> None:
        candidate = self.candidate()
        ledger = candidate["source_ledger"]
        frontier = ledger["path_frontier"]
        frontier["rows"] = [
            next(row for row in frontier["rows"] if row["kind"] == "intent")
        ]
        frontier["summary"] = {
            "intent": 1,
            "feature": 0,
            "surface": 0,
            "control": 0,
            "transition": 0,
        }
        self.sync_frontier_digests(candidate)
        ledger["findings"] = []
        ledger["artifacts"] = []
        checkpoint = self.checkpoint(candidate)
        with self.assertRaisesRegex(ValueError, "discovered frontend surface"):
            self.load(candidate, checkpoint, census_keys=[])

    def test_rejects_blocked_audit_that_retains_complete_ready_closure(self) -> None:
        candidate = self.candidate()
        candidate["source_ledger"]["readiness_disposition"] = "ready"
        checkpoint = self.checkpoint(candidate)
        checkpoint["audit_status"] = "blocked"
        checkpoint["goal_completion_status"] = "blocked"
        with self.assertRaisesRegex(ValueError, "non-complete audit_status"):
            self.load(candidate, checkpoint)

    def test_rejects_evidence_debt_without_an_active_resolution_record(self) -> None:
        candidate = self.candidate()
        candidate["source_ledger"]["completion_status"] = "incomplete"
        candidate["source_ledger"]["readiness_disposition"] = "cannot_determine"
        candidate["source_ledger"]["evidence_debt"] = [
            {
                "debt_id": "ED-BROWSER",
                "subject": "Browser recovery",
                "proof_needed": "Re-enter the blocked path.",
                "reason": "Native browser lock.",
                "status": "blocked",
                "artifact_ids": [],
            }
        ]
        checkpoint = self.checkpoint(candidate)
        checkpoint["audit_status"] = "blocked"
        checkpoint["goal_completion_status"] = "blocked"
        checkpoint["evidence_debt_actions"] = [
            {
                "debt_id": "ED-BROWSER",
                "next_action": "Retry with independent Playwright.",
                "alternate_method": "",
                "attempt_count": 0,
                "last_blocker": "",
                "disposition": "blocked",
            }
        ]
        with self.assertRaisesRegex(ValueError, "evidence debt action"):
            self.load(candidate, checkpoint)

    def test_rejects_complete_audit_that_labels_live_blocked_debt_resolved(self) -> None:
        candidate = self.candidate()
        candidate["source_ledger"]["evidence_debt"] = [
            {
                "debt_id": "ED-BROWSER",
                "subject": "Browser recovery",
                "proof_needed": "Re-enter the blocked path.",
                "reason": "Native browser lock.",
                "status": "blocked",
                "artifact_ids": [],
            }
        ]
        checkpoint = self.checkpoint(candidate)
        checkpoint["evidence_debt_actions"] = [
            {
                "debt_id": "ED-BROWSER",
                "next_action": "Re-enter the blocked path.",
                "alternate_method": "Use an independent browser context.",
                "attempt_count": 1,
                "last_blocker": "Native browser lock.",
                "disposition": "resolved",
            }
        ]
        with self.assertRaisesRegex(ValueError, "inconsistent disposition"):
            self.load(candidate, checkpoint)

    def test_rejects_missing_raw_lane_or_verifier_evidence(self) -> None:
        candidate = self.candidate()
        checkpoint = self.checkpoint(candidate)
        checkpoint["raw_verifier_output_paths"] = ["evidence/missing-verifier.json"]
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            input_path = root / "report-input.json"
            input_path.write_text(json.dumps(candidate), encoding="utf-8")
            (root / "readiness-ledger.json").write_text(
                json.dumps(candidate["source_ledger"]),
                encoding="utf-8",
            )
            self.materialize_checkpoint_evidence(root, checkpoint, candidate)
            (root / checkpoint["raw_verifier_output_paths"][0]).unlink()
            (root / "orchestration-checkpoint.json").write_text(
                json.dumps(checkpoint),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "raw verifier output"):
                load_orchestration_checkpoint(str(input_path), candidate)

    def test_rejects_symlinked_raw_operational_evidence(self) -> None:
        candidate = self.candidate()
        checkpoint = self.checkpoint(candidate)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            input_path = root / "report-input.json"
            input_path.write_text(json.dumps(candidate), encoding="utf-8")
            (root / "readiness-ledger.json").write_text(
                json.dumps(candidate["source_ledger"]),
                encoding="utf-8",
            )
            self.materialize_checkpoint_evidence(root, checkpoint, candidate)
            linked = root / checkpoint["raw_lane_output_paths"][0]
            linked.unlink()
            linked.symlink_to(root / checkpoint["raw_verifier_output_paths"][0])
            (root / "orchestration-checkpoint.json").write_text(
                json.dumps(checkpoint),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "raw lane output.*symlink"):
                load_orchestration_checkpoint(str(input_path), candidate)

    def test_rejects_checkpoint_ledger_that_does_not_match_report_wrapper(self) -> None:
        candidate = self.candidate()
        checkpoint = self.checkpoint(candidate)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            input_path = root / "report-input.json"
            input_path.write_text(json.dumps(candidate), encoding="utf-8")
            (root / "readiness-ledger.json").write_text("{}", encoding="utf-8")
            self.materialize_checkpoint_evidence(root, checkpoint, candidate)
            (root / "orchestration-checkpoint.json").write_text(
                json.dumps(checkpoint),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "ledger_path.*source_ledger"):
                load_orchestration_checkpoint(str(input_path), candidate)

    def test_rejects_browser_failure_without_independent_failover_receipt(self) -> None:
        candidate = self.candidate()
        checkpoint = self.checkpoint(candidate)
        checkpoint["browser_failover_status"] = "succeeded"
        checkpoint["browser_failover_receipt_paths"] = []
        with self.assertRaisesRegex(ValueError, "browser failover receipt"):
            self.load(candidate, checkpoint)

    def test_rejects_complete_audit_with_active_browser_recovery(self) -> None:
        candidate = self.candidate()
        checkpoint = self.checkpoint(candidate)
        checkpoint["browser_failover_status"] = "active"
        checkpoint["browser_failover_receipt_paths"] = ["evidence/browser-failover.json"]
        receipt = {
            "native_error": "browser profile locked",
            "cleanup_result": "cleanup pending",
            "fallback_kind": "independent_playwright_unavailable",
            "process_or_context_id": "",
            "isolation_proof": "",
            "fallback_result": "blocked",
            "remaining_evidence_debt": ["ED-BROWSER"],
        }
        with self.assertRaisesRegex(ValueError, "cannot retain active"):
            self.load(candidate, checkpoint, receipt_payload=receipt)

    def test_accepts_failed_playwright_followed_by_recovered_computer_use(self) -> None:
        candidate = self.candidate()
        checkpoint = self.checkpoint(candidate)
        checkpoint["browser_failover_status"] = "succeeded"
        checkpoint["browser_failover_receipt_paths"] = [
            "evidence/playwright-unavailable.json",
            "evidence/computer-use-recovered.json",
        ]
        receipts = [
            {
                "native_error": "browser profile locked",
                "cleanup_result": "native context released",
                "fallback_kind": "independent_playwright_unavailable",
                "process_or_context_id": "",
                "isolation_proof": "",
                "fallback_result": "blocked",
                "remaining_evidence_debt": ["ED-TEMP"],
            },
            {
                "native_error": "browser profile locked",
                "cleanup_result": "native context released",
                "fallback_kind": "computer_use",
                "process_or_context_id": "computer-use-profile-2",
                "isolation_proof": "separate isolated Computer Use profile",
                "fallback_result": "recovered",
                "remaining_evidence_debt": [],
            },
        ]
        loaded = self.load(candidate, checkpoint, receipt_payload=receipts)
        self.assertEqual("succeeded", loaded["browser_failover_status"])

    def test_rejects_browser_receipt_that_reuses_the_native_binding(self) -> None:
        candidate = self.candidate()
        checkpoint = self.checkpoint(candidate)
        checkpoint["browser_failover_status"] = "succeeded"
        checkpoint["browser_failover_receipt_paths"] = ["evidence/browser-failover.json"]
        receipt = {
            "native_error": "browser profile locked",
            "cleanup_result": "not released",
            "fallback_kind": "same_native_binding",
            "process_or_context_id": "tab.playwright",
            "isolation_proof": "same attached browser",
            "fallback_result": "recovered",
            "remaining_evidence_debt": [],
        }
        with self.assertRaisesRegex(ValueError, "independent Playwright"):
            self.load(candidate, checkpoint, receipt_payload=receipt)

    def test_rejects_same_binding_masquerading_as_independent_playwright(self) -> None:
        candidate = self.candidate()
        checkpoint = self.checkpoint(candidate)
        checkpoint["browser_failover_status"] = "succeeded"
        checkpoint["browser_failover_receipt_paths"] = ["evidence/browser-failover.json"]
        receipt = {
            "native_error": "browser profile locked",
            "cleanup_result": "not released",
            "fallback_kind": "independent_playwright",
            "process_or_context_id": "tab.playwright",
            "isolation_proof": "same locked native-browser binding",
            "fallback_result": "recovered",
            "remaining_evidence_debt": [],
        }
        with self.assertRaisesRegex(ValueError, "same locked browser binding"):
            self.load(candidate, checkpoint, receipt_payload=receipt)

    def test_truthful_early_block_renders_without_lane_verifier_or_census_files(self) -> None:
        candidate = self.candidate()
        ledger = candidate["source_ledger"]
        ledger["completion_status"] = "incomplete"
        ledger["readiness_disposition"] = "cannot_determine"
        ledger["path_frontier"]["closure_state"] = "blocked"
        ledger["path_frontier"]["closure_reason"] = "Runtime could not start."
        checkpoint = self.checkpoint(candidate)
        checkpoint["audit_status"] = "blocked"
        checkpoint["goal_completion_status"] = "blocked"
        checkpoint["exhaustion_status"] = "blocked"
        checkpoint["lanes"] = []
        checkpoint["raw_lane_output_paths"] = []
        checkpoint["raw_verifier_output_paths"] = []
        checkpoint["control_census_paths"] = []
        checkpoint["zero_yield_pass_ids"] = []
        checkpoint["verifier"] = "not_run"
        loaded = self.load(candidate, checkpoint)
        report = render(candidate, orchestration_checkpoint=loaded)
        self.assertIn("Closure not achieved", report)
        self.assertIn("Runtime could not start.", report)

    def test_mixed_recovered_and_blocked_browser_history_renders_honestly(self) -> None:
        candidate = self.candidate()
        ledger = candidate["source_ledger"]
        ledger["completion_status"] = "incomplete"
        ledger["readiness_disposition"] = "cannot_determine"
        ledger["path_frontier"]["closure_state"] = "blocked"
        ledger["path_frontier"]["closure_reason"] = "A later browser path remained blocked."
        ledger["evidence_debt"] = [
            {
                "debt_id": "ED-BROWSER",
                "subject": "Later browser path",
                "proof_needed": "Re-enter the blocked path.",
                "reason": "No second isolated fallback was available.",
                "status": "blocked",
                "artifact_ids": [],
            }
        ]
        checkpoint = self.checkpoint(candidate)
        checkpoint["audit_status"] = "blocked"
        checkpoint["goal_completion_status"] = "blocked"
        checkpoint["exhaustion_status"] = "blocked"
        checkpoint["evidence_debt_actions"] = [
            {
                "debt_id": "ED-BROWSER",
                "next_action": "Resume the later path with an isolated browser.",
                "alternate_method": "Use another allowed frontend route.",
                "attempt_count": 1,
                "last_blocker": "No second isolated fallback was available.",
                "disposition": "blocked",
            }
        ]
        checkpoint["browser_failover_status"] = "blocked"
        checkpoint["browser_failover_receipt_paths"] = [
            "evidence/browser-recovered.json",
            "evidence/browser-blocked.json",
        ]
        receipts = [
            {
                "native_error": "first native context locked",
                "cleanup_result": "first context released",
                "fallback_kind": "independent_playwright",
                "process_or_context_id": "pw-context-1",
                "isolation_proof": "separate Playwright process and profile",
                "fallback_result": "recovered",
                "remaining_evidence_debt": [],
            },
            {
                "native_error": "second native context locked",
                "cleanup_result": "second context could not be released",
                "fallback_kind": "independent_playwright_unavailable",
                "process_or_context_id": "",
                "isolation_proof": "",
                "fallback_result": "blocked",
                "remaining_evidence_debt": ["ED-BROWSER"],
            },
        ]
        loaded = self.load(candidate, checkpoint, receipt_payload=receipts)
        report = render(candidate, orchestration_checkpoint=loaded)
        self.assertEqual("blocked", loaded["browser_failover_status"])
        self.assertIn("Closure not achieved", report)

    def test_truthful_blocked_audit_still_renders_honest_html(self) -> None:
        candidate = self.candidate()
        ledger = candidate["source_ledger"]
        ledger["completion_status"] = "incomplete"
        ledger["readiness_disposition"] = "cannot_determine"
        ledger["path_frontier"]["closure_state"] = "blocked"
        ledger["path_frontier"]["closure_reason"] = "Browser fallback unavailable."
        ledger["evidence_debt"] = [
            {
                "debt_id": "ED-BROWSER",
                "subject": "Browser recovery",
                "proof_needed": "Re-enter the blocked path.",
                "reason": "Native browser lock.",
                "status": "blocked",
                "artifact_ids": [],
            }
        ]
        checkpoint = self.checkpoint(candidate)
        checkpoint["audit_status"] = "blocked"
        checkpoint["goal_completion_status"] = "blocked"
        checkpoint["exhaustion_status"] = "blocked"
        checkpoint["evidence_debt_actions"] = [
            {
                "debt_id": "ED-BROWSER",
                "next_action": "Resume with independent Playwright when available.",
                "alternate_method": "Try another allowed frontend route.",
                "attempt_count": 1,
                "last_blocker": "No independent browser context was available.",
                "disposition": "blocked",
            }
        ]
        checkpoint["browser_failover_status"] = "blocked"
        checkpoint["browser_failover_receipt_paths"] = ["evidence/browser-failover.json"]
        receipt = {
            "native_error": "browser profile locked",
            "cleanup_result": "owning context could not be released",
            "fallback_kind": "independent_playwright_unavailable",
            "process_or_context_id": "",
            "isolation_proof": "",
            "fallback_result": "blocked",
            "remaining_evidence_debt": ["ED-BROWSER"],
        }
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            input_path = root / "report-input.json"
            output_path = root / "readiness-report.html"
            input_path.write_text(json.dumps(candidate), encoding="utf-8")
            (root / "readiness-ledger.json").write_text(
                json.dumps(candidate["source_ledger"]),
                encoding="utf-8",
            )
            self.materialize_canonical_evidence(root, candidate)
            self.materialize_checkpoint_evidence(
                root,
                checkpoint,
                candidate,
                receipt_payload=receipt,
            )
            (root / "orchestration-checkpoint.json").write_text(
                json.dumps(checkpoint),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            report = output_path.read_text(encoding="utf-8")
            self.assertIn("Closure not achieved", report)
            self.assertIn("audit status", report)
            self.assertIn("blocked", report)

    def test_cli_does_not_write_html_when_completion_contract_is_false(self) -> None:
        candidate = self.candidate()
        candidate["source_ledger"]["completion_status"] = "incomplete"
        candidate["source_ledger"]["readiness_disposition"] = "cannot_determine"
        checkpoint = self.checkpoint(candidate)
        checkpoint["audit_status"] = "active"
        checkpoint["goal_completion_status"] = "complete"
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            input_path = root / "report-input.json"
            output_path = root / "readiness-report.html"
            input_path.write_text(json.dumps(candidate), encoding="utf-8")
            (root / "readiness-ledger.json").write_text(
                json.dumps(candidate["source_ledger"]),
                encoding="utf-8",
            )
            self.materialize_canonical_evidence(root, candidate)
            self.materialize_checkpoint_evidence(root, checkpoint, candidate)
            (root / "orchestration-checkpoint.json").write_text(
                json.dumps(checkpoint),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("persistent goal", result.stderr)
            self.assertFalse(output_path.exists())

    def test_bundle_retains_checkpoint_and_raw_operational_evidence(self) -> None:
        candidate = self.candidate()
        checkpoint = self.checkpoint(candidate)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            input_path = root / "report-input.json"
            output_path = root / "evidence.zip"
            input_path.write_text(json.dumps(candidate), encoding="utf-8")
            (root / "readiness-ledger.json").write_text(
                json.dumps(candidate["source_ledger"]),
                encoding="utf-8",
            )
            self.materialize_canonical_evidence(root, candidate)
            self.materialize_checkpoint_evidence(root, checkpoint, candidate)
            (root / "orchestration-checkpoint.json").write_text(
                json.dumps(checkpoint),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(BUNDLE_SCRIPT), str(input_path), str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            with zipfile.ZipFile(output_path) as archive:
                names = set(archive.namelist())
            for expected in (
                "orchestration-checkpoint.json",
                "readiness-ledger.json",
                "evidence/raw-runtime.json",
                "evidence/raw-verifier.json",
                "evidence/runtime-control-census.json",
                "evidence/static-control-census.json",
            ):
                self.assertIn(expected, names)

    def test_bundle_rejects_reserved_generated_name_in_operational_evidence(self) -> None:
        candidate = self.candidate()
        checkpoint = self.checkpoint(candidate)
        checkpoint["raw_lane_output_paths"] = ["manifest.json"]
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            input_path = root / "report-input.json"
            output_path = root / "evidence.zip"
            input_path.write_text(json.dumps(candidate), encoding="utf-8")
            (root / "readiness-ledger.json").write_text(
                json.dumps(candidate["source_ledger"]),
                encoding="utf-8",
            )
            self.materialize_canonical_evidence(root, candidate)
            self.materialize_checkpoint_evidence(root, checkpoint, candidate)
            (root / "orchestration-checkpoint.json").write_text(
                json.dumps(checkpoint),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(BUNDLE_SCRIPT), str(input_path), str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(2, result.returncode)
            self.assertIn("reserved bundle name", result.stderr)
            self.assertFalse(output_path.exists())

    def test_skill_contract_names_every_mechanical_stop_gate(self) -> None:
        paths = [
            ORCHESTRATOR / "SKILL.md",
            ORCHESTRATOR / "references/ledger-validation-contract.md",
            ORCHESTRATOR / "references/final-report-contract.md",
            ORCHESTRATOR / "references/lane-prompts.md",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        for phrase in (
            "`audit_status`",
            "`goal_completion_status`",
            "`control_census_paths`",
            "`zero_yield_pass_ids`",
            "`evidence_debt_actions`",
            "`raw_lane_output_paths`",
            "`raw_verifier_output_paths`",
            "`browser_failover_receipt_paths`",
            "must not mark the persistent goal complete",
        ):
            self.assertIn(phrase, combined)


if __name__ == "__main__":
    unittest.main()

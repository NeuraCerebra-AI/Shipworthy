from __future__ import annotations

import sys
import hashlib
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/scripts"))
import render_report  # noqa: E402


class RemediationLedgerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(
            (ROOT / "tests/skill_product/fixtures/gauntlet-report-input.json").read_text(
                encoding="utf-8"
            )
        )

    @staticmethod
    def _digest(rows):
        return hashlib.sha256(
            json.dumps(
                sorted(row["semantic_key"] for row in rows),
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

    def full_candidate(self) -> dict:
        candidate = deepcopy(self.fixture)
        ledger = candidate["source_ledger"]
        ledger["run_scope"] = "full"
        finding = ledger["findings"][0]
        finding.update(
            fix="Persist the saved project record before returning success, then keep the reload path on the saved record.",
            verify="Save a project, reload /projects as member on desktop, and assert the saved value remains visible.",
            behavioral_identity={"semantic_key": finding["affected_semantic_keys"][0]},
        )
        rows = ledger["path_frontier"]["rows"]
        surface_key = next(row["semantic_key"] for row in rows if row["kind"] == "surface")
        save_key = next(row["semantic_key"] for row in rows if row.get("control_identity", {}).get("name") == "Save")
        for row in rows:
            if row["kind"] == "control" and row.get("status") == "covered":
                row.update(
                    surface_identity=surface_key,
                    input_mechanism="pointer",
                    before_state="editing",
                    after_state="saved",
                    execution_receipt_refs=["evidence/save-receipt.json"],
                )
            elif row["kind"] == "transition":
                row.update(
                    surface_identity=surface_key,
                    input_mechanism="pointer",
                    execution_receipt_refs=["evidence/save-transition-receipt.json"],
                )
        ledger["raw_discoveries"] = [
            {"observation_id": f"RAW-{index}", "semantic_key": row["semantic_key"]}
            for index, row in enumerate(rows, 1)
        ]
        ledger["path_frontier"]["closure_receipts"] = [
            {"source": "verifier", "receipt_ref": "evidence/raw-verifier.json"}
        ]
        ledger["execution_receipts"] = [
            {
                "receipt_id": "evidence/save-receipt.json",
                "semantic_key": save_key,
                "route": "/projects",
                "role": "member",
                "state": "normal",
                "viewport": "desktop",
                "surface": surface_key,
                "control": {"identity": "Save", "type": "button"},
                "visible": True,
                "enabled": True,
                "input_mechanism": "pointer",
                "before_state": "editing",
                "after_state": "saved",
                "evidence_refs": ["evidence/save.json"],
            },
            {
                "receipt_id": "evidence/save-transition-receipt.json",
                "semantic_key": next(row["semantic_key"] for row in rows if row["kind"] == "transition"),
                "route": "/projects",
                "role": "member",
                "state": "normal",
                "viewport": "desktop",
                "surface": surface_key,
                "control": {"identity": "Save", "type": "button"},
                "visible": True,
                "enabled": True,
                "input_mechanism": "pointer",
                "before_state": "editing",
                "after_state": "saved",
                "evidence_refs": ["evidence/save.json"],
            },
        ]
        return candidate

    def test_small_target_cannot_waive_three_verified_waves(self) -> None:
        with self.assertRaisesRegex(ValueError, "three verified waves"):
            render_report.validate_wave_contract(
                {
                    "run_scope": "full",
                    "target_intent": "benchmark_fixture",
                    "verified_wave_ids": ["W1", "W2"],
                    "wave_certificate_paths": ["c1.json", "c2.json"],
                }
            )

    def test_full_run_legacy_input_is_not_a_current_renderer_fallback(self) -> None:
        with self.assertRaisesRegex(ValueError, "historical import"):
            render_report.validate_input_mode(
                {"run_scope": "full", "input_format": "legacy/readiness-v0"}
            )
        self.assertEqual(
            "historical_import",
            render_report.validate_input_mode(
                {"import_mode": "historical", "input_format": "legacy/readiness-v0"}
            ),
        )
        with self.assertRaisesRegex(ValueError, "legacy input|canonical ledger/report-input"):
            render_report.validate_canonical_input(
                {"run_scope": "full", "input_format": "legacy/readiness-v0"}
            )

    def test_positive_discovery_yield_cannot_be_exhausted(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive discovery yield"):
            render_report.validate_discovery_exhaustion(
                {
                    "closure_state": "closed_multi_source",
                    "discovery_passes": [
                        {"id": "P1", "method_family": "runtime_human_interaction", "new_semantic_keys": []},
                        {"id": "P2", "method_family": "runtime_structural_inventory", "new_semantic_keys": ["surface:/upgrade"]},
                    ],
                }
            )

    def test_raw_observation_cannot_disappear_during_synthesis(self) -> None:
        with self.assertRaisesRegex(ValueError, "raw observation"):
            render_report.reconcile_raw_discoveries(
                {
                    "path_frontier": {"rows": [{"semantic_key": "surface:/dashboard:normal:member:desktop"}]},
                    "raw_discoveries": [
                        {"observation_id": "RAW-UPGRADE", "semantic_key": "surface:/dashboard:upgrade-card:member:desktop"}
                    ],
                }
            )

    def test_apparent_affordance_requires_a_census_disposition(self) -> None:
        with self.assertRaisesRegex(ValueError, "apparent affordance"):
            render_report.validate_affordance_census(
                {"entries": [{"affordance_id": "upgrade", "classification": "unclassified"}]}
            )

    def test_hidden_or_off_route_event_cannot_earn_execution_credit(self) -> None:
        row = {
            "semantic_key": "control:surface:/projects:editing:member:desktop:save:button:persist",
            "control_identity": {"name": "Save", "control_type": "button"},
        }
        event = {
            "semantic_key": row["semantic_key"],
            "route": "/projects",
            "role": "member",
            "state": "editing",
            "viewport": "desktop",
            "surface": "editor",
            "control": {"identity": "Save", "type": "button"},
            "visible": False,
            "enabled": True,
            "input_mechanism": "pointer",
            "before_state": "editing",
            "after_state": "saved",
            "evidence_refs": ["proof.json"],
        }
        self.assertFalse(render_report.validate_execution_receipt(row, event))

    def test_required_variant_without_matching_receipt_is_not_covered(self) -> None:
        row = {
            "semantic_key": "control:surface:/team:invite-dialog:admin:mobile:invite-member:button:open-dialog",
            "status": "covered",
            "execution_receipt_refs": ["missing.json"],
        }
        with self.assertRaisesRegex(ValueError, "matching execution receipt"):
            render_report.validate_execution_receipt_set([row], [])

    def test_promised_proven_missing_path_is_not_indefinite_debt(self) -> None:
        self.assertEqual(
            "missing",
            render_report.classify_missing_path(
                {"promised": True, "entry_points": 0, "pending_state": False, "cancellation_primitive": False}
            ),
        )

    def test_post_hoc_closure_without_receipts_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "retained source receipt"):
            render_report.validate_derived_closure(
                {"closure_state": "closed_multi_source", "closure_receipts": []}
            )

    def test_current_full_direct_render_cannot_bypass_validated_checkpoint(self) -> None:
        with self.assertRaisesRegex(ValueError, "validated orchestration-checkpoint"):
            render_report.render(self.full_candidate())

    def test_report_only_behavior_identity_is_not_a_lineage(self) -> None:
        with self.assertRaisesRegex(ValueError, "behavioral lineage"):
            render_report.validate_behavioral_identity(
                {
                    "affected_semantic_keys": ["control:surface:/projects:normal:member:desktop:save:button:persist"],
                    "observed_effect_code": "effect-999",
                    "behavioral_identity": {"semantic_key": "report-only:save"},
                }
            )

    def test_visual_finding_requires_retained_proof_and_disconfirmation(self) -> None:
        with self.assertRaisesRegex(ValueError, "visual proof"):
            render_report.validate_visual_finding(
                {
                    "finding_kind": "visual",
                    "summary": "Header overlaps content",
                    "evidence_refs": [],
                    "visual_proof": {"viewport": "desktop"},
                }
            )

    def test_missing_verifier_provenance_is_unsupported(self) -> None:
        with self.assertRaisesRegex(ValueError, "verifier provenance"):
            render_report.validate_verifier_provenance(
                {"verifier": "approved", "verifier_output": None, "citations": []}
            )

    def test_controller_cannot_self_repair_verifier_failure(self) -> None:
        with self.assertRaisesRegex(ValueError, "independent verifier"):
            render_report.validate_verifier_provenance(
                {
                    "verifier": "approved",
                    "verifier_output": "raw-verifier.json",
                    "citations": ["evidence/a.md"],
                    "controller_id": "controller-1",
                    "verifier_id": "controller-1",
                    "replacement_for_rejected": True,
                }
            )

    def test_upload_recovery_stays_active_while_alternative_is_available(self) -> None:
        with self.assertRaisesRegex(ValueError, "recovery remains active"):
            render_report.validate_recovery_inventory(
                {"status": "blocked", "alternatives": [{"id": "playwright", "available": True, "attempted": False}]}
            )

    def test_record_counts_exclude_passed_and_debt_from_findings(self) -> None:
        counts = render_report.derive_record_counts(
            {
                "findings": [
                    {"finding_id": "F1", "section": "fix_next", "action": "Fix"},
                    {"finding_id": "F2", "section": "passed_keep", "action": "Keep"},
                ],
                "evidence_debt": [{"debt_id": "ED1"}],
            }
        )
        self.assertEqual(
            {"actionable": 1, "evidence_debt": 1, "passed_keep": 1, "avoided": 0, "scoped_out": 0},
            counts,
        )

    def test_visible_record_projection_rejects_count_drift_and_debt_zero(self) -> None:
        ledger = {
            "findings": [{"section": "fix_next", "action": "Fix"}],
            "evidence_debt": [{"debt_id": "ED-1"}],
            "path_frontier": {"rows": []},
        }
        projection = {
            "record_counts": {"actionable": 1, "evidence_debt": 1, "passed_keep": 0, "avoided": 0, "scoped_out": 0},
            "summary": {"clear_before_ship": 0, "fix_next": 1, "not_proven_not_tested": 1, "passed_keep": 0},
        }
        self.assertTrue(render_report.validate_record_count_projection(ledger, projection))
        broken = deepcopy(projection)
        broken["summary"]["not_proven_not_tested"] = 0
        with self.assertRaisesRegex(ValueError, "visible action summary"):
            render_report.validate_record_count_projection(ledger, broken)

    def test_passed_keep_cannot_receive_corrective_language(self) -> None:
        with self.assertRaisesRegex(ValueError, "Passed / Keep"):
            render_report.validate_record_language(
                {"section": "passed_keep", "action": "Keep", "fix": "Correct the working path"}
            )

    def test_blank_or_tautological_fix_and_verification_text_is_rejected(self) -> None:
        for field in ("fix", "verify"):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "actionable"):
                render_report.validate_record_language(
                    {"section": "fix_next", "action": "Fix", field: "Correct X so effect Y no longer occurs"}
                )

    def test_canonical_filename_contract_has_no_redundant_report_json(self) -> None:
        self.assertEqual(
            {"readiness-ledger.json", "report-input.json", "orchestration-checkpoint.json", "readiness-report.html"},
            render_report.canonical_artifact_names(),
        )

    def test_fixture_target_intent_does_not_inherit_production_release_severity(self) -> None:
        self.assertEqual(
            "scope_limitation",
            render_report.calibrate_target_severity(
                {"target_intent": "benchmark_fixture", "finding": "missing CI/deployment configuration"}
            ),
        )
        self.assertEqual(
            "release_gate",
            render_report.calibrate_target_severity(
                {"target_intent": "production_product", "finding": "missing CI/deployment configuration"}
            ),
        )

    def test_current_full_input_reconciles_all_closure_sources(self) -> None:
        candidate = self.full_candidate()
        from tests.skill_product.support.schema_subset import validate
        schema_root = ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas"
        validate(candidate["source_ledger"], schema_root / "readiness-ledger.schema.json")
        validate(candidate, schema_root / "report-input.schema.json")
        render_report.validate_canonical_input(candidate)

        broken = deepcopy(candidate)
        broken["source_ledger"]["raw_discoveries"].append(
            {"observation_id": "RAW-UPGRADE", "semantic_key": "surface:/projects:upgrade:member:desktop"}
        )
        with self.assertRaisesRegex(ValueError, "raw observation"):
            render_report.validate_canonical_input(broken)

        broken = deepcopy(candidate)
        broken["source_ledger"]["path_frontier"]["closure_receipts"] = []
        with self.assertRaisesRegex(ValueError, "retained source receipt"):
            render_report.validate_canonical_input(broken)

        broken = deepcopy(candidate)
        broken["source_ledger"]["execution_receipts"][0]["visible"] = False
        with self.assertRaisesRegex(ValueError, "matching execution receipt"):
            render_report.validate_canonical_input(broken)

    def test_current_full_checkpoint_requires_three_certified_waves_and_provenance(self) -> None:
        candidate = self.full_candidate()
        frontier = candidate["source_ledger"]["path_frontier"]
        all_controls = [row["semantic_key"] for row in frontier["rows"] if row["kind"] == "control"]
        frontier_digest = self._digest(frontier["rows"])
        control_digest = hashlib.sha256(
            json.dumps(sorted(all_controls), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        checkpoint = {
            "run_scope": "full",
            "target_name": "Gauntlet Projects",
            "target_intent": "benchmark_fixture",
            "target_calibration": "scope_limitation",
            "target_calibration_reason": "This fixture does not claim production deployment; missing CI/deploy files are scope limits.",
            "lanes": ["runtime", "verifier"],
            "mode": "structured orchestration",
            "multi_agent_authorization": "explicitly authorized",
            "frontend_path_walk_performed": True,
            "frontend_tool": "native browser",
            "runtime_target": "local fixture",
            "path_walk_status": "full",
            "verifier": "approved",
            "verifier_citation_refs": ["evidence/citation.json"],
            "verifier_citation_status": "valid",
            "controller_id": "controller-1",
            "verifier_id": "verifier-1",
            "host_orchestration_requirement": "structured",
            "host_orchestration_actual": "structured",
            "host_orchestration_compatibility": "compatible",
            "host_orchestration_fallback_reason": "none",
            "omitted": [],
            "ledger_path": "readiness-ledger.json",
            "evidence_locations": ["evidence/"],
            "exhaustion_status": "closed_multi_source",
            "audit_status": "complete",
            "goal_mode_status": "active",
            "goal_completion_status": "active",
            "raw_lane_output_paths": ["evidence/raw-runtime.json"],
            "raw_verifier_output_paths": ["evidence/raw-verifier.json"],
            "control_census_paths": ["evidence/runtime-census.json", "evidence/static-census.json"],
            "apparent_affordance_census_paths": ["evidence/affordance-census.json"],
            "verified_wave_ids": ["W1", "W2", "W3"],
            "wave_certificate_paths": ["evidence/w1.json", "evidence/w2.json", "evidence/w3.json"],
            "zero_yield_pass_ids": [item["id"] for item in frontier["discovery_passes"][-2:]],
            "evidence_debt_actions": [],
            "recovery_status": "not_needed",
            "recovery_attempts": [],
            "recovery_receipt_paths": [],
            "browser_failover_status": "not_needed",
            "browser_failover_receipt_paths": [],
        }
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "report-input.json").write_text(json.dumps(candidate), encoding="utf-8")
            (root / "readiness-ledger.json").write_text(json.dumps(candidate["source_ledger"]), encoding="utf-8")
            for reference in checkpoint["raw_lane_output_paths"] + checkpoint["raw_verifier_output_paths"]:
                (root / reference).parent.mkdir(parents=True, exist_ok=True)
                (root / reference).write_text(json.dumps({"raw_discoveries": candidate["source_ledger"]["raw_discoveries"]}), encoding="utf-8")
            for reference in checkpoint["control_census_paths"]:
                (root / reference).write_text(json.dumps({
                    "method_family": "runtime_structural_inventory" if "runtime" in reference else "static_implementation_inventory",
                    "semantic_keys": all_controls,
                    "digest": control_digest,
                    "frontier_digest": frontier_digest,
                    "unmatched_controls": [],
                }), encoding="utf-8")
            (root / "evidence/affordance-census.json").write_text(json.dumps({
                "entries": [{"affordance_id": "upgrade-card", "action_signaling": True, "classification": "false_affordance", "evidence_refs": ["evidence/upgrade.png"]}]
            }), encoding="utf-8")
            for reference in ("evidence/citation.json", "evidence/upgrade.png", "evidence/save.json"):
                (root / reference).write_text("proof", encoding="utf-8")
            for index, reference in enumerate(checkpoint["wave_certificate_paths"], 1):
                (root / reference).write_text(json.dumps({
                    "wave_id": f"W{index}", "decision": "approved", "verifier_id": "verifier-1",
                    "citation_refs": ["evidence/citation.json"], "raw_output_ref": "evidence/raw-verifier.json",
                }), encoding="utf-8")
            (root / "orchestration-checkpoint.json").write_text(json.dumps(checkpoint), encoding="utf-8")
            loaded = render_report.load_orchestration_checkpoint(str(root / "report-input.json"), candidate)
            self.assertEqual("complete", loaded["audit_status"])
            broken = deepcopy(checkpoint)
            broken["verified_wave_ids"] = ["W1", "W2"]
            (root / "orchestration-checkpoint.json").write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "three verified waves"):
                render_report.load_orchestration_checkpoint(str(root / "report-input.json"), candidate)
            broken = deepcopy(checkpoint)
            broken["verifier_citation_refs"] = ["evidence/citation.json#L9"]
            (root / "orchestration-checkpoint.json").write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line anchor"):
                render_report.load_orchestration_checkpoint(str(root / "report-input.json"), candidate)
            broken = deepcopy(checkpoint)
            broken["omitted"] = ["Wave 3 reconciliation"]
            (root / "orchestration-checkpoint.json").write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "omitted gate"):
                render_report.load_orchestration_checkpoint(str(root / "report-input.json"), candidate)
            for reference in checkpoint["wave_certificate_paths"]:
                (root / reference).write_text(json.dumps({
                    "wave_id": "W1", "decision": "approved", "verifier_id": "verifier-1",
                    "citation_refs": ["evidence/citation.json"], "raw_output_ref": "evidence/raw-verifier.json",
                }), encoding="utf-8")
            (root / "orchestration-checkpoint.json").write_text(json.dumps(checkpoint), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "one-to-one wave certificate"):
                render_report.load_orchestration_checkpoint(str(root / "report-input.json"), candidate)
            for reference in checkpoint["wave_certificate_paths"]:
                wave_id = Path(reference).stem.upper()
                (root / reference).write_text(json.dumps({
                    "wave_id": wave_id, "decision": "approved", "verifier_id": "verifier-1",
                    "citation_refs": ["evidence/citation.json"], "raw_output_ref": "evidence/raw-verifier.json",
                }), encoding="utf-8")
            for reference in checkpoint["raw_lane_output_paths"] + checkpoint["raw_verifier_output_paths"]:
                (root / reference).write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "raw operational packets do not reconcile"):
                render_report.load_orchestration_checkpoint(str(root / "report-input.json"), candidate)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import sys
import hashlib
import json
import subprocess
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
        finding_by_key = {
            key: finding["finding_id"]
            for finding in ledger["findings"]
            for key in finding.get("affected_semantic_keys", [])
        }
        ledger["raw_discoveries"] = []
        for index, row in enumerate(rows, 1):
            key = row["semantic_key"]
            finding_id = finding_by_key.get(key)
            ledger["raw_discoveries"].append(
                {
                    "observation_id": f"RAW-{index}",
                    "semantic_key": key,
                    "material": row.get("material", True),
                    "source_kind": "runtime_human_interaction",
                    "source_id": f"EVENT-{index}",
                    "source_artifact": "evidence/raw-runtime.json",
                    "source_pointer": f"/observations/{index - 1}",
                    "behavioral_identity": {
                        "semantic_key": key,
                        **render_report._semantic_behavioral_identity(key),
                    },
                    "evidence_refs": list(row.get("evidence_refs", [])),
                    "terminal_disposition": {
                        "kind": "finding" if finding_id else "frontier",
                        "record_id": finding_id or row["id"],
                    },
                }
            )
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
                "backend_effect_expected": True,
                "backend_effect_reason": "Save should persist the edited project.",
                "backend_correlation": {
                    "status": "matched",
                    "ui_feedback": "success",
                    "state_change_expected": True,
                    "persistence_expected": True,
                    "channels": {
                        "network": {
                            "status": "observed",
                            "request_count": 1,
                            "expected_request_count": 1,
                            "method": "POST",
                            "path": "/api/projects",
                            "response_status": 200,
                            "evidence_refs": ["evidence/save-network.json"],
                        },
                        "logs": {
                            "status": "observed",
                            "source_ref": "evidence/backend.log",
                            "start_offset": 120,
                            "end_offset": 380,
                            "correlated_error_count": 0,
                            "evidence_refs": ["evidence/backend.log#bytes=120-380"],
                        },
                        "state": {
                            "status": "observed",
                            "before": "editing",
                            "after": "saved",
                            "evidence_refs": ["evidence/save-state.json"],
                        },
                        "reentry": {
                            "status": "observed",
                            "result": "saved",
                            "evidence_refs": ["evidence/save-reload.json"],
                        },
                    },
                },
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
        receipts_by_key = {
            item["semantic_key"]: item
            for item in ledger["execution_receipts"]
        }
        for item in ledger["raw_discoveries"]:
            if item["semantic_key"] in receipts_by_key:
                receipt = receipts_by_key[item["semantic_key"]]
                item.update(
                    source_kind="execution_receipt",
                    source_id=receipt["receipt_id"],
                )
                item["behavioral_identity"].update(
                    containing_surface=receipt["surface"],
                    control_identity=receipt["control"]["identity"],
                    control_type=receipt["control"]["type"],
                    input_mechanism=receipt["input_mechanism"],
                    before_state=receipt["before_state"],
                    after_state=receipt["after_state"],
                )
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

    def test_backend_correlation_accepts_matched_persistent_action(self) -> None:
        candidate = self.full_candidate()
        summary = render_report.reconcile_backend_correlations(
            candidate["source_ledger"]["path_frontier"]["rows"],
            candidate["source_ledger"]["execution_receipts"],
            candidate["source_ledger"]["findings"],
            strict=True,
        )
        self.assertEqual(
            {
                "backend_effecting_actions": 1,
                "matched": 1,
                "mismatch": 0,
                "blocked": 0,
                "not_proven": 0,
                "correlated_backend_errors": 0,
                "persistence_checks": 1,
                "blocked_channels": 0,
            },
            summary,
        )

    def test_backend_correlation_rejects_success_without_persistence(self) -> None:
        candidate = self.full_candidate()
        receipt = candidate["source_ledger"]["execution_receipts"][0]
        receipt["backend_correlation"]["channels"]["reentry"]["result"] = "editing"
        with self.assertRaisesRegex(ValueError, "re-entry result"):
            render_report.reconcile_backend_correlations(
                candidate["source_ledger"]["path_frontier"]["rows"],
                candidate["source_ledger"]["execution_receipts"],
                candidate["source_ledger"]["findings"],
                strict=True,
            )

    def test_backend_correlation_rejects_failure_feedback_after_state_changed(self) -> None:
        candidate = self.full_candidate()
        receipt = candidate["source_ledger"]["execution_receipts"][0]
        receipt["backend_correlation"]["ui_feedback"] = "failure"
        with self.assertRaisesRegex(ValueError, "contradictory evidence"):
            render_report.reconcile_backend_correlations(
                candidate["source_ledger"]["path_frontier"]["rows"],
                candidate["source_ledger"]["execution_receipts"],
                candidate["source_ledger"]["findings"],
                strict=True,
            )

    def test_backend_correlation_rejects_hidden_correlated_error_and_duplicate_request(self) -> None:
        candidate = self.full_candidate()
        receipt = candidate["source_ledger"]["execution_receipts"][0]
        receipt["backend_correlation"]["channels"]["logs"]["correlated_error_count"] = 1
        with self.assertRaisesRegex(ValueError, "correlated backend errors"):
            render_report.reconcile_backend_correlations(
                candidate["source_ledger"]["path_frontier"]["rows"],
                candidate["source_ledger"]["execution_receipts"],
                candidate["source_ledger"]["findings"],
                strict=True,
            )
        receipt["backend_correlation"]["channels"]["logs"]["correlated_error_count"] = 0
        receipt["backend_correlation"]["channels"]["network"]["request_count"] = 2
        with self.assertRaisesRegex(ValueError, "request count"):
            render_report.reconcile_backend_correlations(
                candidate["source_ledger"]["path_frontier"]["rows"],
                candidate["source_ledger"]["execution_receipts"],
                candidate["source_ledger"]["findings"],
                strict=True,
            )
        receipt["backend_correlation"]["status"] = "mismatch"
        summary = render_report.reconcile_backend_correlations(
            candidate["source_ledger"]["path_frontier"]["rows"],
            candidate["source_ledger"]["execution_receipts"],
            candidate["source_ledger"]["findings"],
            strict=True,
        )
        self.assertEqual(1, summary["mismatch"])

    def test_presentational_action_can_explicitly_have_no_backend_effect(self) -> None:
        candidate = self.full_candidate()
        receipt = candidate["source_ledger"]["execution_receipts"][0]
        receipt.update(
            backend_effect_expected=False,
            backend_effect_reason="Opening this local menu is presentational.",
            backend_correlation={"status": "not_applicable"},
        )
        summary = render_report.reconcile_backend_correlations(
            candidate["source_ledger"]["path_frontier"]["rows"],
            candidate["source_ledger"]["execution_receipts"],
            candidate["source_ledger"]["findings"],
            strict=True,
        )
        self.assertEqual(0, summary["backend_effecting_actions"])
        self.assertNotIn(
            "Frontend-to-backend correlation",
            render_report.coverage_confidence_html(
                candidate["source_ledger"]["path_frontier"],
                backend_correlation_summary=summary,
            ),
        )

    def test_full_control_cannot_omit_backend_correlation(self) -> None:
        candidate = self.full_candidate()
        receipt = candidate["source_ledger"]["execution_receipts"][0]
        del receipt["backend_effect_expected"]
        del receipt["backend_effect_reason"]
        del receipt["backend_correlation"]
        with self.assertRaisesRegex(ValueError, "backend_effect_expected"):
            render_report.reconcile_backend_correlations(
                candidate["source_ledger"]["path_frontier"]["rows"],
                candidate["source_ledger"]["execution_receipts"],
                candidate["source_ledger"]["findings"],
                strict=True,
            )

    def test_missing_logs_can_be_explicitly_blocked_with_other_runtime_proof(self) -> None:
        candidate = self.full_candidate()
        receipt = candidate["source_ledger"]["execution_receipts"][0]
        receipt["backend_correlation"]["channels"]["logs"] = {
            "status": "blocked",
            "reason": "Backend process output was unavailable.",
        }
        summary = render_report.reconcile_backend_correlations(
            candidate["source_ledger"]["path_frontier"]["rows"],
            candidate["source_ledger"]["execution_receipts"],
            candidate["source_ledger"]["findings"],
            strict=True,
        )
        self.assertEqual(1, summary["matched"])
        self.assertEqual(1, summary["blocked_channels"])

    def test_blocked_backend_channels_remain_not_proven(self) -> None:
        candidate = self.full_candidate()
        receipt = candidate["source_ledger"]["execution_receipts"][0]
        receipt["backend_correlation"] = {
            "status": "blocked",
            "ui_feedback": "success",
            "state_change_expected": True,
            "persistence_expected": True,
            "channels": {
                name: {"status": "blocked", "reason": "Channel unavailable."}
                for name in ("network", "logs", "state", "reentry")
            },
        }
        summary = render_report.reconcile_backend_correlations(
            candidate["source_ledger"]["path_frontier"]["rows"],
            candidate["source_ledger"]["execution_receipts"],
            candidate["source_ledger"]["findings"],
            strict=True,
        )
        self.assertEqual(1, summary["not_proven"])
        with self.assertRaisesRegex(ValueError, "cannot support covered closure"):
            render_report.reconcile_backend_correlations(
                candidate["source_ledger"]["path_frontier"]["rows"],
                candidate["source_ledger"]["execution_receipts"],
                candidate["source_ledger"]["findings"],
                strict=True,
                require_closure=True,
            )

    def test_backend_correlation_rejects_secrets_payloads_and_unbounded_logs(self) -> None:
        candidate = self.full_candidate()
        receipt = candidate["source_ledger"]["execution_receipts"][0]
        receipt["backend_correlation"]["channels"]["network"]["authorization"] = "secret"
        with self.assertRaisesRegex(ValueError, "sensitive or raw payload field"):
            render_report.reconcile_backend_correlations(
                candidate["source_ledger"]["path_frontier"]["rows"],
                candidate["source_ledger"]["execution_receipts"],
                candidate["source_ledger"]["findings"],
                strict=True,
            )
        del receipt["backend_correlation"]["channels"]["network"]["authorization"]
        receipt["backend_correlation"]["channels"]["logs"]["end_offset"] = 2_000_000
        with self.assertRaisesRegex(ValueError, "bounded log range"):
            render_report.reconcile_backend_correlations(
                candidate["source_ledger"]["path_frontier"]["rows"],
                candidate["source_ledger"]["execution_receipts"],
                candidate["source_ledger"]["findings"],
                strict=True,
            )

    def test_backend_mismatch_requires_finding_lineage(self) -> None:
        candidate = self.full_candidate()
        receipt = candidate["source_ledger"]["execution_receipts"][0]
        receipt["backend_correlation"]["status"] = "mismatch"
        receipt["backend_correlation"]["channels"]["state"]["after"] = "editing"
        candidate["source_ledger"]["findings"][0]["affected_semantic_keys"] = []
        with self.assertRaisesRegex(ValueError, "finding lineage"):
            render_report.reconcile_backend_correlations(
                candidate["source_ledger"]["path_frontier"]["rows"],
                candidate["source_ledger"]["execution_receipts"],
                candidate["source_ledger"]["findings"],
                strict=True,
            )

    def test_backend_summary_is_derived_and_human_readable(self) -> None:
        candidate = self.full_candidate()
        summary = render_report.reconcile_backend_correlations(
            candidate["source_ledger"]["path_frontier"]["rows"],
            candidate["source_ledger"]["execution_receipts"],
            candidate["source_ledger"]["findings"],
            strict=True,
        )
        output = render_report.coverage_confidence_html(
            candidate["source_ledger"]["path_frontier"],
            backend_correlation_summary=summary,
        )
        self.assertIn("Frontend-to-backend correlation", output)
        self.assertIn("1 of 1 backend-effecting actions correlated", output)
        self.assertIn("0 mismatches", output)
        self.assertNotIn("authorization", output)

    def test_backend_failure_uses_existing_bounded_repair_queue(self) -> None:
        manifest = render_report.build_validation_repair_manifest(
            "backend correlation EVENT-SAVE matched despite correlated backend errors",
            attempt_count=2,
        )
        self.assertEqual(
            "frontend_to_backend_correlation",
            manifest["failures"][0]["gate"],
        )
        self.assertIn("Re-exercise", manifest["failures"][0]["required_action"])
        self.assertEqual(3, manifest["max_attempts"])

    def test_benchmark_preflight_must_be_clean_and_external(self) -> None:
        clean = {
            "run_scope": "full",
            "target_intent": "benchmark_fixture",
            "benchmark_preflight": {
                "status": "clean",
                "baseline_revision": "0d40df9",
                "baseline_tag": "gauntlet-default-v1",
                "porcelain_entries": [],
                "generated_artifacts": [],
                "evidence_external": True,
            },
        }
        self.assertTrue(render_report.validate_benchmark_preflight(clean))
        dirty = deepcopy(clean)
        dirty["benchmark_preflight"]["porcelain_entries"] = ["?? evidence/"]
        with self.assertRaisesRegex(ValueError, "clean target"):
            render_report.validate_benchmark_preflight(dirty)
        dirty.update(
            audit_status="blocked",
            frontend_path_walk_performed=False,
            path_walk_status="not_performed",
        )
        self.assertTrue(
            render_report.validate_benchmark_preflight(
                dirty, allow_aborted_report=True
            )
        )
        ordinary = {
            "run_scope": "full",
            "target_intent": "production_product",
            "benchmark_preflight": {"status": "dirty"},
        }
        self.assertTrue(render_report.validate_benchmark_preflight(ordinary))

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

    def test_material_raw_observation_requires_explicit_terminal_disposition(self) -> None:
        ledger = {
            "path_frontier": {
                "rows": [
                    {
                        "id": "PF-S",
                        "kind": "surface",
                        "semantic_key": "surface:/dashboard:normal:member:desktop",
                    }
                ]
            },
            "findings": [],
            "evidence_debt": [],
            "raw_discoveries": [
                {
                    "observation_id": "RAW-DASHBOARD",
                    "semantic_key": "surface:/dashboard:normal:member:desktop",
                    "material": True,
                    "source_kind": "runtime_receipt",
                    "behavioral_identity": {
                        "semantic_key": "surface:/dashboard:normal:member:desktop",
                        "route": "/dashboard",
                        "state": "normal",
                        "role": "member",
                        "viewport": "desktop",
                    },
                    "evidence_refs": ["evidence/dashboard.json"],
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "terminal disposition"):
            render_report.reconcile_raw_discoveries(ledger, strict=True)

    def test_raw_observation_cannot_cross_credit_role_or_viewport(self) -> None:
        ledger = {
            "path_frontier": {
                "rows": [
                    {
                        "id": "PF-C",
                        "kind": "control",
                        "semantic_key": (
                            "control:surface:/team:normal:member:desktop:"
                            "invite:button:open-dialog"
                        ),
                    }
                ]
            },
            "findings": [],
            "evidence_debt": [],
            "raw_discoveries": [
                {
                    "observation_id": "RAW-INVITE",
                    "semantic_key": (
                        "control:surface:/team:normal:member:desktop:"
                        "invite:button:open-dialog"
                    ),
                    "material": True,
                    "source_kind": "runtime_receipt",
                    "behavioral_identity": {
                        "semantic_key": (
                            "control:surface:/team:normal:member:desktop:"
                            "invite:button:open-dialog"
                        ),
                        "route": "/team",
                        "state": "normal",
                        "role": "admin",
                        "viewport": "mobile",
                        "control_identity": "Invite",
                        "control_type": "button",
                    },
                    "evidence_refs": ["evidence/invite.json"],
                    "terminal_disposition": {"kind": "frontier", "record_id": "PF-C"},
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "behavioral identity"):
            render_report.reconcile_raw_discoveries(ledger, strict=True)

    def test_independently_fixable_defects_require_distinct_finding_lineage(self) -> None:
        key = "transition:editing:control:surface:/projects:normal:member:desktop:save:button:persist:saved"
        base = {
            "material": True,
            "source_kind": "runtime_receipt",
            "semantic_key": key,
            "behavioral_identity": {
                "semantic_key": key,
                "route": "/projects",
                "state": "normal",
                "role": "member",
                "viewport": "desktop",
                "control_identity": "Save",
                "control_type": "button",
                "before_state": "editing",
                "after_state": "saved",
            },
            "evidence_refs": ["evidence/save.json"],
            "terminal_disposition": {"kind": "finding", "record_id": "FND-SAVE"},
        }
        ledger = {
            "path_frontier": {"rows": [{"id": "PF-T", "kind": "transition", "semantic_key": key}]},
            "findings": [
                {"finding_id": "FND-SAVE", "affected_semantic_keys": [key]}
            ],
            "evidence_debt": [],
            "raw_discoveries": [
                dict(base, observation_id="RAW-MESSAGE", defect_class="misleading-success"),
                dict(base, observation_id="RAW-RELOAD", defect_class="reload-data-loss"),
            ],
        }
        with self.assertRaisesRegex(ValueError, "independently fixable"):
            render_report.reconcile_raw_discoveries(ledger, strict=True)

    def test_rejected_and_out_of_scope_dispositions_require_reason_and_proof(self) -> None:
        ledger = {
            "path_frontier": {"rows": []},
            "findings": [],
            "evidence_debt": [],
            "raw_discoveries": [
                {
                    "observation_id": "RAW-UPGRADE",
                    "semantic_key": "surface:/dashboard:upgrade:member:desktop",
                    "material": True,
                    "source_kind": "apparent_affordance_census",
                    "behavioral_identity": {
                        "semantic_key": "surface:/dashboard:upgrade:member:desktop",
                        "route": "/dashboard",
                        "state": "upgrade",
                        "role": "member",
                        "viewport": "desktop",
                    },
                    "evidence_refs": ["evidence/upgrade.json"],
                    "terminal_disposition": {"kind": "rejected", "record_id": "REJ-UPGRADE"},
                }
            ],
            "rejected_discoveries": [
                {
                    "discovery_id": "REJ-UPGRADE",
                    "observation_ids": ["RAW-UPGRADE"],
                    "semantic_key": "surface:/dashboard:upgrade:member:desktop",
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "reason and evidence"):
            render_report.reconcile_raw_discoveries(ledger, strict=True)

    def test_reconciliation_summary_counts_each_material_observation_once(self) -> None:
        key = "surface:/dashboard:normal:member:desktop"
        ledger = {
            "path_frontier": {"rows": [{"id": "PF-S", "kind": "surface", "semantic_key": key}]},
            "findings": [],
            "evidence_debt": [],
            "raw_discoveries": [
                {
                    "observation_id": "RAW-DASHBOARD",
                    "semantic_key": key,
                    "material": True,
                    "source_kind": "runtime_receipt",
                    "behavioral_identity": {
                        "semantic_key": key,
                        "route": "/dashboard",
                        "state": "normal",
                        "role": "member",
                        "viewport": "desktop",
                    },
                    "evidence_refs": ["evidence/dashboard.json"],
                    "terminal_disposition": {"kind": "frontier", "record_id": "PF-S"},
                }
            ],
        }
        self.assertEqual(
            {
                "material_observations": 1,
                "frontier": 1,
                "finding": 0,
                "evidence_debt": 0,
                "rejected": 0,
                "out_of_scope": 0,
                "unresolved": 0,
            },
            render_report.reconcile_raw_discoveries(ledger, strict=True),
        )

    def test_execution_receipt_cannot_exist_outside_the_frontier(self) -> None:
        receipt = {
            "receipt_id": "REC-AVATAR",
            "semantic_key": "control:surface:/dashboard:normal:member:desktop:avatar:button:open-menu",
            "route": "/dashboard",
            "role": "member",
            "state": "normal",
            "viewport": "desktop",
            "surface": "surface:/dashboard:normal:member:desktop",
            "control": {"identity": "Avatar", "type": "button"},
            "visible": True,
            "enabled": True,
            "input_mechanism": "pointer",
            "before_state": "normal",
            "after_state": "menu-open",
            "evidence_refs": ["evidence/avatar.json"],
        }
        with self.assertRaisesRegex(ValueError, "execution receipt.*frontier"):
            render_report.reconcile_execution_receipts([], [receipt])

    def test_execution_receipt_must_enter_the_raw_discovery_inventory(self) -> None:
        key = "control:surface:/dashboard:normal:member:desktop:avatar:button:open-menu"
        row = {
            "id": "PF-AVATAR",
            "kind": "control",
            "semantic_key": key,
            "control_identity": {"name": "Avatar", "control_type": "button"},
        }
        receipt = {
            "receipt_id": "REC-AVATAR",
            "semantic_key": key,
            "route": "/dashboard",
            "role": "member",
            "state": "normal",
            "viewport": "desktop",
            "surface": "surface:/dashboard:normal:member:desktop",
            "control": {"identity": "Avatar", "type": "button"},
            "visible": True,
            "enabled": True,
            "input_mechanism": "pointer",
            "before_state": "normal",
            "after_state": "menu-open",
            "evidence_refs": ["evidence/avatar.json"],
        }
        with self.assertRaisesRegex(ValueError, "raw discovery inventory"):
            render_report.reconcile_execution_receipts([row], [receipt], [])
        raw = {
            "observation_id": "RAW-AVATAR",
            "semantic_key": key,
            "source_kind": "execution_receipt",
            "source_id": "REC-AVATAR",
            "behavioral_identity": {
                "semantic_key": key,
                "route": "/dashboard",
                "role": "member",
                "state": "normal",
                "viewport": "desktop",
                "containing_surface": "surface:/dashboard:normal:member:desktop",
                "control_identity": "Avatar",
                "control_type": "button",
                "input_mechanism": "keyboard",
                "before_state": "normal",
                "after_state": "menu-open",
            },
        }
        with self.assertRaisesRegex(ValueError, "raw discovery identity"):
            render_report.reconcile_execution_receipts([row], [receipt], [raw])

    def test_original_evidence_packet_rejects_frontier_derived_observations(self) -> None:
        key = "surface:/dashboard:normal:member:desktop"
        ledger = {
            "path_frontier": {
                "rows": [{"id": "PF-DASH", "kind": "surface", "semantic_key": key}]
            },
            "raw_discoveries": [
                {
                    "observation_id": "OBS-ROW-PF-DASH",
                    "source_kind": "declared_behavior_inventory",
                    "source_id": "PF-DASH",
                    "source_artifact": "evidence/raw-runtime.json",
                    "source_pointer": "/observations/0",
                    "material": True,
                    "semantic_key": key,
                    "behavioral_identity": {
                        "semantic_key": key,
                        "route": "/dashboard",
                        "state": "normal",
                        "role": "member",
                        "viewport": "desktop",
                    },
                    "evidence_refs": ["evidence/dashboard.yml"],
                    "terminal_disposition": {"kind": "frontier", "record_id": "PF-DASH"},
                }
            ],
            "execution_receipts": [],
        }
        packet = {
            "packet_id": "PACKET-RUNTIME",
            "capture_phase": "pre_synthesis",
            "artifact_path": "evidence/raw-runtime.json",
            "observations": [
                {
                    key: value
                    for key, value in ledger["raw_discoveries"][0].items()
                    if key != "terminal_disposition"
                }
            ],
            "execution_receipts": [],
        }
        with self.assertRaisesRegex(ValueError, "circular provenance"):
            render_report.reconcile_original_evidence_packets([packet], ledger)

    def test_original_evidence_packet_cannot_omit_a_material_observation(self) -> None:
        key = "control:surface:/dashboard:normal:member:desktop:command-palette:keyboard:open"
        original = {
            "observation_id": "OBS-RUNTIME-42",
            "source_kind": "runtime_human_interaction",
            "source_id": "EVENT-42",
            "source_artifact": "evidence/raw-runtime.json",
            "source_pointer": "/observations/0",
            "material": True,
            "semantic_key": key,
            "behavioral_identity": {
                "semantic_key": key,
                "route": "/dashboard",
                "state": "normal",
                "role": "member",
                "viewport": "desktop",
                "containing_surface": "surface:/dashboard:normal:member:desktop",
                "control_identity": "command-palette",
                "control_type": "keyboard",
                "input_mechanism": "Meta+K",
                "before_state": "closed",
                "after_state": "open",
            },
            "evidence_refs": ["evidence/runtime-receipt.json#event-42"],
        }
        packet = {
            "packet_id": "PACKET-RUNTIME",
            "capture_phase": "pre_synthesis",
            "artifact_path": "evidence/raw-runtime.json",
            "observations": [original],
            "execution_receipts": [],
        }
        ledger = {"path_frontier": {"rows": []}, "raw_discoveries": [], "execution_receipts": []}
        with self.assertRaisesRegex(ValueError, "original observation.*absent"):
            render_report.reconcile_original_evidence_packets([packet], ledger)

    def test_material_state_change_receipt_requires_transition_lineage(self) -> None:
        key = "control:surface:/projects:editing:member:desktop:publish:button:publish"
        receipt = {
            "receipt_id": "EVENT-PUBLISH-1",
            "semantic_key": key,
            "route": "/projects",
            "role": "member",
            "state": "editing",
            "viewport": "desktop",
            "surface": "surface:/projects:editing:member:desktop",
            "control": {"identity": "Publish", "type": "button"},
            "visible": True,
            "enabled": True,
            "input_mechanism": "pointer",
            "before_state": "draft",
            "after_state": "published",
            "material_state_change": True,
            "evidence_refs": ["evidence/publish.yml"],
        }
        ledger = {
            "path_frontier": {
                "rows": [{"id": "PF-PUBLISH", "kind": "control", "semantic_key": key}]
            },
            "raw_discoveries": [],
            "execution_receipts": [receipt],
        }
        packet = {
            "packet_id": "PACKET-RUNTIME",
            "capture_phase": "pre_synthesis",
            "artifact_path": "evidence/raw-runtime.json",
            "observations": [],
            "execution_receipts": [receipt],
        }
        with self.assertRaisesRegex(ValueError, "material state change.*transition"):
            render_report.reconcile_original_evidence_packets([packet], ledger)

    def test_upstream_inventory_cannot_be_absent_from_original_packet(self) -> None:
        packet = {
            "capture_phase": "pre_synthesis",
            "artifact_path": "evidence/raw-runtime.json",
            "observations": [{
                "observation_id": "OBS-SAVE",
                "source_kind": "execution_receipt",
                "source_id": "EVENT-SAVE",
                "source_artifact": "evidence/raw-runtime.json",
                "source_pointer": "/observations/0",
                "semantic_key": "control:surface:/projects:normal:member:desktop:save:button:persist",
            }],
            "execution_receipts": [{
                "receipt_id": "EVENT-SAVE",
                "semantic_key": "control:surface:/projects:normal:member:desktop:save:button:persist",
            }],
        }
        with self.assertRaisesRegex(ValueError, "census control.*absent from original"):
            render_report.reconcile_upstream_inventory(
                [packet],
                {
                    "control:surface:/projects:normal:member:desktop:save:button:persist",
                    "control:surface:/projects:normal:member:desktop:archive:button:archive",
                },
                [],
            )

    def test_validation_failure_builds_bounded_machine_repair_queue(self) -> None:
        manifest = render_report.build_validation_repair_manifest(
            "execution receipt EVENT-42 is absent from original evidence; "
            "census control archive is absent from original evidence",
            attempt_count=2,
        )
        self.assertEqual("repair_required", manifest["status"])
        self.assertEqual(2, manifest["attempt_count"])
        self.assertEqual(2, len(manifest["failures"]))
        self.assertEqual("receipt_to_original", manifest["failures"][0]["gate"])
        self.assertIn("required_action", manifest["failures"][0])

        blocked = render_report.build_validation_repair_manifest(
            "; ".join(f"failure {index}" for index in range(40)),
            attempt_count=3,
        )
        self.assertEqual("blocked_required", blocked["status"])
        self.assertLessEqual(len(blocked["failures"]), 20)

    def test_completion_receipt_binds_ledger_checkpoint_packets_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            input_path = root / "report-input.json"
            report_path = root / "readiness-report.html"
            packet_path = root / "evidence" / "raw-runtime.json"
            packet_path.parent.mkdir()
            input_path.write_text('{"source_ledger":{"ledger_id":"LED-1"}}', encoding="utf-8")
            packet_path.write_text('{"observations":[]}', encoding="utf-8")
            checkpoint = {
                "validation_state": "complete",
                "validation_completion_receipt_path": "validation-completion.json",
                "raw_lane_output_paths": ["evidence/raw-runtime.json"],
                "raw_verifier_output_paths": [],
            }
            html = "<html>validated</html>"

            receipt = render_report.build_validation_completion_receipt(
                str(input_path), str(report_path), checkpoint, html
            )

            self.assertEqual("passed", receipt["status"])
            self.assertEqual(
                hashlib.sha256(html.encode("utf-8")).hexdigest(),
                receipt["report_sha256"],
            )
            self.assertEqual(
                hashlib.sha256(packet_path.read_bytes()).hexdigest(),
                receipt["original_packet_sha256"]["evidence/raw-runtime.json"],
            )
            self.assertEqual(
                render_report._canonical_digest({"ledger_id": "LED-1"}),
                receipt["ledger_sha256"],
            )
            self.assertIn("original_evidence_closure", receipt["gates"])

    def test_rejected_disposition_cannot_point_to_a_different_semantic_path(self) -> None:
        key = "surface:/dashboard:upgrade:member:desktop"
        ledger = {
            "path_frontier": {"rows": []},
            "findings": [],
            "evidence_debt": [],
            "raw_discoveries": [
                {
                    "observation_id": "RAW-UPGRADE",
                    "semantic_key": key,
                    "material": True,
                    "source_kind": "apparent_affordance_census",
                    "source_id": "upgrade-card",
                    "behavioral_identity": {
                        "semantic_key": key,
                        "route": "/dashboard",
                        "state": "upgrade",
                        "role": "member",
                        "viewport": "desktop",
                    },
                    "evidence_refs": ["evidence/upgrade.json"],
                    "terminal_disposition": {"kind": "rejected", "record_id": "REJ-UPGRADE"},
                }
            ],
            "rejected_discoveries": [
                {
                    "discovery_id": "REJ-UPGRADE",
                    "observation_ids": ["RAW-UPGRADE"],
                    "semantic_key": "surface:/billing:upgrade:member:desktop",
                    "reason": "Disconfirmed.",
                    "evidence_refs": ["evidence/upgrade.json"],
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "semantic path"):
            render_report.reconcile_raw_discoveries(ledger, strict=True)

    def test_evidence_debt_disposition_requires_a_concrete_proof_target(self) -> None:
        key = "control:surface:/team:normal:admin:mobile:invite:button:open-dialog"
        ledger = {
            "path_frontier": {"rows": []},
            "findings": [],
            "evidence_debt": [
                {
                    "debt_id": "ED-INVITE",
                    "reason": "Mobile runtime was unavailable.",
                }
            ],
            "raw_discoveries": [
                {
                    "observation_id": "RAW-INVITE",
                    "semantic_key": key,
                    "material": True,
                    "source_kind": "control_census",
                    "behavioral_identity": {
                        "semantic_key": key,
                        "route": "/team",
                        "state": "normal",
                        "role": "admin",
                        "viewport": "mobile",
                        "control_identity": "Invite",
                        "control_type": "button",
                    },
                    "evidence_refs": ["evidence/team-census.json"],
                    "terminal_disposition": {
                        "kind": "evidence_debt",
                        "record_id": "ED-INVITE",
                    },
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "proof target"):
            render_report.reconcile_raw_discoveries(ledger, strict=True)

    def test_apparent_affordance_must_reconcile_to_a_raw_observation(self) -> None:
        census = {
            "entries": [
                {
                    "affordance_id": "upgrade-card",
                    "semantic_key": "surface:/dashboard:upgrade:member:desktop",
                    "action_signaling": True,
                    "classification": "false_affordance",
                    "evidence_refs": ["evidence/upgrade.json"],
                }
            ]
        }
        with self.assertRaisesRegex(ValueError, "affordance.*raw discovery"):
            render_report.reconcile_affordance_census({"raw_discoveries": []}, census)

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

    def test_incomplete_full_run_cannot_bypass_raw_reconciliation(self) -> None:
        candidate = self.full_candidate()
        ledger = candidate["source_ledger"]
        ledger["completion_status"] = "incomplete"
        ledger["readiness_disposition"] = "cannot_determine"
        ledger["path_frontier"]["closure_state"] = "incomplete"
        ledger["path_frontier"]["closure_reason"] = "One material variant remains unproven."
        ledger["raw_discoveries"] = ledger["raw_discoveries"][:-1]

        with self.assertRaisesRegex(ValueError, "no material raw observation"):
            render_report.validate_canonical_input(candidate)

    def test_current_full_checkpoint_requires_three_certified_waves_and_provenance(self) -> None:
        candidate = self.full_candidate()
        frontier = candidate["source_ledger"]["path_frontier"]
        surface_key = next(
            row["semantic_key"] for row in frontier["rows"] if row["kind"] == "surface"
        )
        surface_raw = next(
            item
            for item in candidate["source_ledger"]["raw_discoveries"]
            if item["semantic_key"] == surface_key
        )
        surface_raw.update(
            source_kind="apparent_affordance_census",
            source_id="upgrade-card",
        )
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
            "benchmark_preflight": {
                "status": "clean",
                "baseline_revision": "0d40df9",
                "baseline_tag": "gauntlet-default-v1",
                "porcelain_entries": [],
                "generated_artifacts": [],
                "evidence_external": True,
            },
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
            "validation_state": "validating",
            "validation_attempts": [],
            "validation_repair_queue_path": "validation-repair.json",
            "validation_completion_receipt_path": "validation-completion.json",
        }
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "report-input.json").write_text(json.dumps(candidate), encoding="utf-8")
            (root / "readiness-ledger.json").write_text(json.dumps(candidate["source_ledger"]), encoding="utf-8")
            for reference in checkpoint["raw_lane_output_paths"] + checkpoint["raw_verifier_output_paths"]:
                (root / reference).parent.mkdir(parents=True, exist_ok=True)
                is_runtime = reference == "evidence/raw-runtime.json"
                (root / reference).write_text(
                    json.dumps({
                        "packet_id": "PACKET-RUNTIME" if is_runtime else "PACKET-VERIFIER",
                        "capture_phase": "pre_synthesis",
                        "artifact_path": reference,
                        "observations": [
                            {
                                key: value
                                for key, value in item.items()
                                if key != "terminal_disposition"
                            }
                            for item in candidate["source_ledger"]["raw_discoveries"]
                        ] if is_runtime else [],
                        "execution_receipts": (
                            candidate["source_ledger"]["execution_receipts"]
                            if is_runtime else []
                        ),
                    }),
                    encoding="utf-8",
                )
            for reference in checkpoint["control_census_paths"]:
                (root / reference).write_text(json.dumps({
                    "method_family": "runtime_structural_inventory" if "runtime" in reference else "static_implementation_inventory",
                    "semantic_keys": all_controls,
                    "digest": control_digest,
                    "frontier_digest": frontier_digest,
                    "unmatched_controls": [],
                }), encoding="utf-8")
            (root / "evidence/affordance-census.json").write_text(json.dumps({
                "entries": [{
                    "affordance_id": "upgrade-card",
                    "semantic_key": surface_key,
                    "action_signaling": True,
                    "classification": "false_affordance",
                    "evidence_refs": ["evidence/upgrade.png"],
                }]
            }), encoding="utf-8")
            for reference in (
                "evidence/citation.json",
                "evidence/upgrade.png",
                "evidence/save.json",
                "evidence/save-network.json",
                "evidence/backend.log",
                "evidence/save-state.json",
                "evidence/save-reload.json",
            ):
                (root / reference).write_text("proof", encoding="utf-8")
            for index, reference in enumerate(checkpoint["wave_certificate_paths"], 1):
                (root / reference).write_text(json.dumps({
                    "wave_id": f"W{index}", "decision": "approved", "verifier_id": "verifier-1",
                    "citation_refs": ["evidence/citation.json"], "raw_output_ref": "evidence/raw-verifier.json",
                }), encoding="utf-8")
            (root / "orchestration-checkpoint.json").write_text(json.dumps(checkpoint), encoding="utf-8")
            loaded = render_report.load_orchestration_checkpoint(str(root / "report-input.json"), candidate)
            self.assertEqual("complete", loaded["audit_status"])
            self.assertEqual(0, loaded["_upstream_accounting_summary"]["unresolved"])

            canonical_refs = {
                candidate["source_ledger"]["path_frontier"]["manifest_artifact"]
            }
            for row in candidate["source_ledger"]["path_frontier"]["rows"]:
                canonical_refs.update(row.get("evidence_refs", []))
                for observation in row.get("observations", []):
                    canonical_refs.update(observation.get("evidence_refs", []))
            for finding in candidate["source_ledger"]["findings"]:
                canonical_refs.update(finding.get("evidence_refs", []))
            for reference in canonical_refs:
                path = root / reference
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.exists():
                    path.write_text("canonical evidence", encoding="utf-8")

            output_path = root / "readiness-report.html"
            rendered = subprocess.run(
                [
                    sys.executable,
                    str(Path(render_report.__file__)),
                    str(root / "report-input.json"),
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, rendered.returncode, rendered.stderr)
            self.assertTrue(output_path.exists())
            report_html = output_path.read_text(encoding="utf-8")
            self.assertIn("Frontend-to-backend correlation", report_html)
            self.assertIn("1 of 1 backend-effecting actions correlated", report_html)
            self.assertIn("1 persistence checks", report_html)
            self.assertIn("backend matched", report_html)
            self.assertTrue((root / "validation-completion.json").exists())
            finalized_checkpoint = json.loads(
                (root / "orchestration-checkpoint.json").read_text(encoding="utf-8")
            )
            self.assertEqual("complete", finalized_checkpoint["validation_state"])
            self.assertIn(
                "validation_completion_receipt_sha256", finalized_checkpoint
            )
            raw_runtime_path = root / "evidence/raw-runtime.json"
            raw_runtime = json.loads(raw_runtime_path.read_text(encoding="utf-8"))
            raw_runtime["observations"][0]["behavioral_identity"]["role"] = "admin"
            raw_runtime_path.write_text(json.dumps(raw_runtime), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "changed during ledger synthesis"):
                render_report.load_orchestration_checkpoint(
                    str(root / "report-input.json"), candidate
                )
            raw_runtime_path.write_text(
                json.dumps({
                    "packet_id": "PACKET-RUNTIME",
                    "capture_phase": "pre_synthesis",
                    "artifact_path": "evidence/raw-runtime.json",
                    "observations": [
                        {
                            key: value
                            for key, value in item.items()
                            if key != "terminal_disposition"
                        }
                        for item in candidate["source_ledger"]["raw_discoveries"]
                    ],
                    "execution_receipts": candidate["source_ledger"]["execution_receipts"],
                }),
                encoding="utf-8",
            )
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
            with self.assertRaisesRegex(ValueError, "frozen before synthesis|requires pre-synthesis"):
                render_report.load_orchestration_checkpoint(str(root / "report-input.json"), candidate)


if __name__ == "__main__":
    unittest.main()

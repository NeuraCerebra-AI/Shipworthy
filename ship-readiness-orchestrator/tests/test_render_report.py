import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "shipworthy_render_report", ROOT / "scripts" / "render_report.py"
)
RENDERER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDERER)


def frontier_row(row_id="PF-S-001", key="surface:/settings:normal:member:desktop"):
    return {
        "id": row_id,
        "kind": "surface",
        "semantic_key": key,
        "normalization_version": "shipworthy-semantic-v1",
        "method_taxonomy_version": "shipworthy-methods-v1",
        "status": "covered",
        "material": True,
        "attempt_count": 1,
        "evidence_refs": ["evidence/row.json"],
        "observations": [],
        "owner_lane": "ship-product-workflows",
    }


def confirmed_p0():
    return {
        "action": "Fix",
        "section": "clear_before_ship",
        "severity": "P0 Blocker",
        "confidence": "Confirmed",
        "proof": "Confirmed",
        "verifier_status": "approved",
    }


class CandidateReconciliationTests(unittest.TestCase):
    def inventory(self, root, family, inventory_id, row, candidate_id):
        source_artifact = root / f"{inventory_id}-raw.txt"
        source_artifact.write_text(
            f"{family}|{candidate_id}|{row['semantic_key']}\n", encoding="utf-8"
        )
        artifact = root / f"{inventory_id}.json"
        candidate = {
            "candidate_id": candidate_id,
            "kind": row["kind"],
            "raw_locator": f"{family}:{candidate_id}",
            "material": True,
            "semantic_key": row["semantic_key"],
            "frontier_row_id": row["id"],
            "disposition": "mapped",
            "reason": "Independent source candidate.",
            "evidence_refs": [source_artifact.name],
        }
        inventory = {
            "inventory_id": inventory_id,
            "method_taxonomy_version": "shipworthy-methods-v1",
            "method_family": family,
            "role": "member",
            "state": "normal",
            "viewport": "desktop",
            "fixture": "resettable-test",
            "source_locator": f"test-source://{family}/{inventory_id}",
            "source_artifacts": [
                {
                    "ref": source_artifact.name,
                    "sha256": hashlib.sha256(source_artifact.read_bytes()).hexdigest(),
                }
            ],
            "artifact_ref": artifact.name,
            "candidate_digest": RENDERER._candidate_digest([candidate]),
            "candidates": [candidate],
        }
        if family == "runtime_structural_inventory":
            inventory["action_signaling_candidate_count"] = int(
                row["kind"] in {"control", "transition"}
            )
        extract = {
            "schema_name": "shipworthy/candidate-inventory-source",
            "schema_version": "1.0",
            **{
                field: inventory[field]
                for field in (
                    "inventory_id", "method_taxonomy_version", "method_family",
                    "role", "state", "viewport", "fixture", "source_locator",
                    "source_artifacts", "candidate_digest",
                    "action_signaling_candidate_count", "candidates",
                )
                if field in inventory
            },
        }
        artifact.write_text(
            json.dumps(extract, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        inventory["artifact_sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
        return inventory

    def complete_frontier(self, root, rows):
        inventories = []
        families = (
            "declared_behavior_inventory",
            "runtime_structural_inventory",
            "static_implementation_inventory",
        )
        for family_index, family in enumerate(families):
            for row_index, row in enumerate(rows):
                inventories.append(
                    self.inventory(
                        root,
                        family,
                        f"INV-{family_index}-{row_index}",
                        row,
                        f"CAND-{family_index}-{row_index}",
                    )
                )
        return {"rows": rows, "candidate_inventories": inventories, "reconciliation_differences": []}

    def test_three_source_inventory_reconciles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            frontier = self.complete_frontier(root, [frontier_row()])
            result = RENDERER.reconcile_candidate_inventories(
                frontier, evidence_root=str(root), require_closure=True
            )
            self.assertEqual(len(result["method_families"]), 3)

    def test_frontier_row_omitted_from_sources_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = [
                frontier_row(),
                frontier_row("PF-S-002", "surface:/profile:normal:member:desktop"),
            ]
            frontier = self.complete_frontier(root, rows[:1])
            frontier["rows"] = rows
            with self.assertRaisesRegex(ValueError, "do not reconcile"):
                RENDERER.reconcile_candidate_inventories(
                    frontier, evidence_root=str(root), require_closure=True
                )

    def test_current_full_mapping_cannot_use_an_unsourced_frontier(self):
        frontier = {
            "rows": [frontier_row()],
            "candidate_inventories": [],
            "reconciliation_differences": [],
        }
        with self.assertRaisesRegex(ValueError, "canonical frontier"):
            RENDERER.reconcile_candidate_inventories(
                frontier, require_complete_mapping=True
            )

    def test_arbitrary_method_family_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = frontier_row()
            frontier = self.complete_frontier(root, [row])
            frontier["candidate_inventories"][0]["method_family"] = "agent_second_look"
            with self.assertRaisesRegex(ValueError, "not canonical"):
                RENDERER.reconcile_candidate_inventories(frontier)

    def test_candidate_mapping_tamper_breaks_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = frontier_row()
            frontier = self.complete_frontier(root, [row])
            frontier["candidate_inventories"][0]["candidates"][0]["frontier_row_id"] = "PF-S-TAMPERED"
            with self.assertRaisesRegex(ValueError, "digest does not reconcile"):
                RENDERER.reconcile_candidate_inventories(frontier)

    def test_inventory_artifact_must_equal_extracted_candidates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            frontier = self.complete_frontier(root, [frontier_row()])
            inventory = frontier["candidate_inventories"][0]
            artifact = root / inventory["artifact_ref"]
            artifact.write_text('{"source":"independent"}\n', encoding="utf-8")
            inventory["artifact_sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "does not exactly match"):
                RENDERER.reconcile_candidate_inventories(
                    frontier, evidence_root=str(root)
                )

    def test_discovery_pass_without_source_inventory_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            frontier = self.complete_frontier(root, [frontier_row()])
            digest = RENDERER._combined_candidate_digest(frontier["candidate_inventories"])
            frontier["discovery_passes"] = [
                {
                    "method_taxonomy_version": "shipworthy-methods-v1",
                    "method_family": "runtime_structural_inventory",
                    "inventory_ids": [],
                    "evidence_refs": [],
                    "starting_candidate_digest": digest,
                    "ending_candidate_digest": digest,
                    "new_candidate_ids": [],
                }
            ]
            with self.assertRaisesRegex(ValueError, "inventory ids do not resolve"):
                RENDERER.validate_source_backed_discovery_passes(
                    frontier, evidence_root=str(root)
                )


class DecisionStateTests(unittest.TestCase):
    def test_incomplete_confirmed_p0_is_not_ready_even_with_debt(self):
        ledger = {
            "completion_status": "incomplete",
            "readiness_disposition": "not_ready",
            "findings": [confirmed_p0()],
            "evidence_debt": [{"debt_id": "ED-1"}],
        }
        frontier = {
            "closure_state": "blocked",
            "finality": "exhausted",
            "remaining_safe_work": [],
        }
        self.assertTrue(RENDERER.validate_decision_state(ledger, frontier, "blocked"))

    def test_cannot_determine_cannot_hide_confirmed_p0(self):
        ledger = {
            "completion_status": "incomplete",
            "readiness_disposition": "cannot_determine",
            "findings": [confirmed_p0()],
            "evidence_debt": [],
        }
        frontier = {
            "closure_state": "blocked",
            "finality": "exhausted",
            "remaining_safe_work": [],
        }
        with self.assertRaisesRegex(ValueError, "requires not_ready"):
            RENDERER.validate_decision_state(ledger, frontier, "blocked")

    def test_complete_exhaustive_audit_may_be_not_ready(self):
        ledger = {
            "completion_status": "complete",
            "readiness_disposition": "not_ready",
            "findings": [confirmed_p0()],
            "evidence_debt": [],
        }
        frontier = {
            "closure_state": "closed_multi_source",
            "finality": "exhausted",
            "remaining_safe_work": [],
        }
        self.assertTrue(RENDERER.validate_decision_state(ledger, frontier, "complete"))

    def test_complete_audit_cannot_be_indeterminate(self):
        ledger = {
            "completion_status": "complete",
            "readiness_disposition": "cannot_determine",
            "findings": [],
            "evidence_debt": [],
        }
        frontier = {
            "closure_state": "closed_multi_source",
            "finality": "exhausted",
            "remaining_safe_work": [],
        }
        with self.assertRaisesRegex(ValueError, "conclusive disposition"):
            RENDERER.validate_decision_state(ledger, frontier, "complete")

    def test_affirmative_readiness_rejects_open_frontier(self):
        ledger = {
            "completion_status": "incomplete",
            "readiness_disposition": "ready",
            "findings": [],
            "evidence_debt": [],
        }
        frontier = {
            "closure_state": "incomplete",
            "finality": "open",
            "remaining_safe_work": ["Walk settings dialog"],
        }
        with self.assertRaisesRegex(ValueError, "affirmative readiness"):
            RENDERER.validate_decision_state(ledger, frontier, "active")

    def test_affirmative_readiness_rejects_frontier_debt(self):
        row = frontier_row()
        row["status"] = "evidence_debt"
        ledger = {
            "completion_status": "complete",
            "readiness_disposition": "ready",
            "findings": [],
            "evidence_debt": [],
        }
        frontier = {
            "rows": [row],
            "closure_state": "closed_multi_source",
            "finality": "exhausted",
            "remaining_safe_work": [],
        }
        with self.assertRaisesRegex(ValueError, "every material row covered"):
            RENDERER.validate_decision_state(ledger, frontier, "complete")

    def test_exhausted_frontier_rejects_nonterminal_material_row(self):
        row = frontier_row()
        row["status"] = "unattempted"
        ledger = {
            "completion_status": "incomplete",
            "readiness_disposition": "cannot_determine",
            "findings": [],
            "evidence_debt": [],
        }
        frontier = {
            "rows": [row],
            "closure_state": "blocked",
            "finality": "exhausted",
            "remaining_safe_work": [],
        }
        with self.assertRaisesRegex(ValueError, "nonterminal material rows"):
            RENDERER.validate_decision_state(ledger, frontier, "blocked")

    def test_constrained_non_p0_cannot_claim_not_ready(self):
        ledger = {
            "completion_status": "incomplete",
            "readiness_disposition": "not_ready",
            "findings": [],
            "evidence_debt": [],
        }
        frontier = {
            "rows": [],
            "closure_state": "blocked",
            "finality": "exhausted",
            "remaining_safe_work": [],
        }
        with self.assertRaisesRegex(ValueError, "constrained audit disposition"):
            RENDERER.validate_decision_state(ledger, frontier, "blocked")

    def test_user_stopped_audit_may_retain_open_finality(self):
        row = frontier_row()
        row["status"] = "unattempted"
        ledger = {
            "completion_status": "incomplete",
            "readiness_disposition": "cannot_determine",
            "findings": [],
            "evidence_debt": [],
        }
        frontier = {
            "rows": [row],
            "closure_state": "incomplete",
            "finality": "open",
            "remaining_safe_work": ["Resume settings path"],
        }
        self.assertTrue(
            RENDERER.validate_decision_state(ledger, frontier, "user_stopped")
        )

    def test_cannot_determine_has_distinct_neutral_verdict(self):
        self.assertEqual(RENDERER.V1_VERDICT["cannot_determine"], "CANNOT DETERMINE")
        self.assertNotIn("CANNOT DETERMINE", RENDERER.VERDICT)
        html = RENDERER.render(
            {
                "target": "Neutral decision test",
                "verdict": "CANNOT DETERMINE",
                "summary": {},
                "coverage": {"total_paths": 0, "segments": []},
                "findings": [],
                "checkpoint": {},
            }
        )
        self.assertIn("Cannot Determine", html)
        self.assertIn(RENDERER.VERDICT_NEUTRAL[1], html)
        self.assertIn(RENDERER.VERDICT_NEUTRAL[2], html)
        self.assertNotIn('<span class="stamp-text">Not Ready</span>', html)

    def test_declared_full_frontend_walk_without_receipt_fails(self):
        row = frontier_row()
        row["observations"] = [
            {"method_family": "runtime_human_interaction"}
        ]
        frontier = {"rows": [row]}
        ledger = {
            "execution_receipts": [
                {"semantic_key": row["semantic_key"], "evidence_refs": ["fake.png"]}
            ]
        }
        with self.assertRaisesRegex(ValueError, "no-control frontend"):
            RENDERER.validate_frontend_walk_proof(ledger, frontier)

    def test_action_signalling_affordance_cannot_hide_as_surface(self):
        surface = frontier_row()
        ledger = {
            "raw_discoveries": [
                {
                    "observation_id": "OBS-CTA",
                    "source_kind": "apparent_affordance_census",
                    "source_id": "AFF-CTA",
                    "semantic_key": surface["semantic_key"],
                }
            ]
        }
        census = {
            "entries": [
                {
                    "affordance_id": "AFF-CTA",
                    "semantic_key": surface["semantic_key"],
                    "classification": "functional",
                    "action_signaling": True,
                    "evidence_refs": ["cta.png"],
                }
            ]
        }
        frontier = {
            "rows": [surface],
            "candidate_inventories": [
                {
                    "method_family": "runtime_structural_inventory",
                    "action_signaling_candidate_count": 0,
                    "candidates": [],
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "runtime control or transition"):
            RENDERER.reconcile_affordance_census(ledger, census, frontier)

    def test_incomplete_handoff_lists_every_unfinished_source(self):
        row = frontier_row()
        row.update({
            "status": "blocked",
            "terminal_reason": "Test account lacks the role.",
            "owner_lane": "runtime",
        })
        frontier = {
            "rows": [row],
            "closure_state": "blocked",
            "finality": "exhausted",
            "remaining_safe_work": ["Retry with an admin fixture."],
            "resume_conditions": ["Admin fixture becomes available."],
            "reconciliation_differences": [
                {"semantic_key": "surface:/admin:normal:admin:desktop", "reason": "Static-only candidate."}
            ],
        }
        checkpoint = {
            "audit_status": "blocked",
            "goal_mode_status": "not_authorized",
            "omitted": ["keyboard-only pass"],
        }
        debt = [{"record_id": "ED-1", "title": "Persistence proof is missing."}]

        block, question = RENDERER.continuation_handoff_html(
            frontier, checkpoint, debt
        )

        for expected in (
            row["semantic_key"], "Test account lacks the role.",
            "surface:/admin:normal:admin:desktop", "ED-1",
            "keyboard-only pass", "Retry with an admin fixture.",
            "Admin fixture becomes available.",
        ):
            self.assertIn(expected, block)
        self.assertIn(RENDERER.CONTINUATION_QUESTION, question)
        self.assertIn(RENDERER.GOAL_QUESTION, question)

    def test_finished_not_ready_audit_does_not_ask_to_continue_paths(self):
        missing = frontier_row()
        missing.update({
            "status": "missing",
            "terminal_reason": "The promised cancellation entry point is absent.",
        })
        frontier = {
            "rows": [missing],
            "closure_state": "closed_multi_source",
            "finality": "exhausted",
            "remaining_safe_work": [],
            "resume_conditions": [],
            "reconciliation_differences": [],
        }
        block, question = RENDERER.continuation_handoff_html(
            frontier,
            {"audit_status": "complete", "omitted": []},
            [],
        )
        self.assertEqual((block, question), ("", ""))

    def test_continuation_goal_wording_tracks_goal_availability(self):
        frontier = {
            "rows": [],
            "closure_state": "incomplete",
            "finality": "open",
            "remaining_safe_work": ["Finish discovery."],
            "resume_conditions": [],
            "reconciliation_differences": [],
        }
        cases = {
            "not_authorized": RENDERER.GOAL_QUESTION,
            "active": "Should I keep the persistent goal active",
            "unavailable": "use the resumable checkpoint as the goal-equivalent",
        }
        for status, expected in cases.items():
            with self.subTest(status=status):
                _, question = RENDERER.continuation_handoff_html(
                    frontier,
                    {"audit_status": "active", "goal_mode_status": status},
                    [],
                )
                self.assertIn(expected, question)


class BundledSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(
            (ROOT / "references" / "schemas" / "readiness-ledger.schema.json").read_text(
                encoding="utf-8"
            )
        )
        cls.row_validator = jsonschema.Draft202012Validator(cls.schema["$defs"]["FrontierRow"])

    def test_legacy_sampled_and_inferred_statuses_are_rejected(self):
        for status in ("sampled", "inferred"):
            row = frontier_row()
            row["status"] = status
            self.assertTrue(list(self.row_validator.iter_errors(row)), status)

    def test_unknown_frontier_fields_are_rejected(self):
        row = frontier_row()
        row["self_certified_complete"] = True
        self.assertTrue(list(self.row_validator.iter_errors(row)))

    def test_apparent_affordance_cannot_replace_a_frontier_control(self):
        candidate_schema = self.schema["$defs"]["FrontierCandidate"]
        candidate = {
            "candidate_id": "CAND-CTA",
            "kind": "apparent_affordance",
            "raw_locator": "role=button; name=Continue",
            "material": True,
            "semantic_key": "surface:/start:normal:member:desktop",
            "frontier_row_id": "PF-S-001",
            "disposition": "mapped",
            "reason": "attempted relabel",
            "evidence_refs": ["raw-runtime.json"],
        }
        errors = list(jsonschema.Draft202012Validator(candidate_schema).iter_errors(candidate))
        self.assertTrue(errors)

    def test_renderer_executes_bundled_schema(self):
        row = frontier_row()
        row["status"] = "inferred"
        ledger = {
            "schema_name": "shipworthy/readiness-ledger",
            "schema_version": "1.1",
            "generated_at": "2026-08-05T12:00:00Z",
            "producer": {"name": "test", "version": "1"},
            "ledger_id": "LED-TEST",
            "revision": 1,
            "completion_status": "incomplete",
            "readiness_disposition": "cannot_determine",
            "gate": {"policy": "confirmed_only"},
            "findings": [],
            "artifacts": [],
            "evidence_debt": [],
            "path_frontier": {
                "normalization_version": "shipworthy-semantic-v1",
                "method_taxonomy_version": "shipworthy-methods-v1",
                "closure_state": "incomplete",
                "summary": {"intent": 0, "feature": 0, "surface": 1, "control": 0, "transition": 0},
                "rows": [row],
                "discovery_passes": [],
                "reconciliation_differences": [],
            },
        }
        with self.assertRaisesRegex(ValueError, "bundled schema validation failed"):
            RENDERER.validate_bundled_schema(ledger)


class EndToEndRendererTests(unittest.TestCase):
    def test_cli_renders_truthful_active_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = {
                "schema_name": "shipworthy/readiness-ledger",
                "schema_version": "1.1",
                "generated_at": "2026-08-05T12:00:00Z",
                "producer": {"name": "test", "version": "1"},
                "ledger_id": "LED-E2E",
                "revision": 1,
                "completion_status": "incomplete",
                "readiness_disposition": "cannot_determine",
                "gate": {"policy": "confirmed_only"},
                "findings": [],
                "artifacts": [],
                "evidence_debt": [],
                "path_frontier": {
                    "normalization_version": "shipworthy-semantic-v1",
                    "method_taxonomy_version": "shipworthy-methods-v1",
                    "closure_state": "incomplete",
                    "closure_reason": "Collection is still active.",
                    "finality": "open",
                    "finality_reason": "A safe path remains to be attempted.",
                    "remaining_safe_work": ["Walk the settings route."],
                    "resume_conditions": ["Resume the runtime lane."],
                    "summary": {
                        "intent": 0, "feature": 0, "surface": 0,
                        "control": 0, "transition": 0,
                    },
                    "rows": [],
                    "candidate_inventories": [],
                    "discovery_passes": [],
                    "reconciliation_differences": [],
                },
            }
            ledger_path = root / "readiness-ledger.json"
            ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
            report_input = {
                "schema_name": "shipworthy/readiness-report-input",
                "schema_version": "1.1",
                "generated_at": "2026-08-05T12:00:00Z",
                "producer": {"name": "test", "version": "1"},
                "report_input_id": "RPT-E2E",
                "source_ledger": ledger,
            }
            input_path = root / "report-input.json"
            input_path.write_text(json.dumps(report_input), encoding="utf-8")
            checkpoint = {
                "target_name": "E2E active run",
                "lanes": ["runtime — active — pending"],
                "mode": "authorized sequential fixture",
                "multi_agent_authorization": "explicitly authorized",
                "frontend_path_walk_performed": False,
                "frontend_tool": "pending",
                "runtime_target": "local fixture",
                "path_walk_status": "not_performed",
                "verifier": "not run",
                "omitted": ["frontend walk pending"],
                "ledger_path": ledger_path.name,
                "evidence_locations": ["evidence/"],
                "exhaustion_status": "incomplete",
                "audit_status": "active",
                "goal_mode_status": "active",
                "goal_completion_status": "active",
                "raw_lane_output_paths": [],
                "raw_verifier_output_paths": [],
                "control_census_paths": [],
                "zero_yield_pass_ids": [],
                "evidence_debt_actions": [],
                "recovery_status": "not_needed",
                "recovery_attempts": [],
                "recovery_receipt_paths": [],
                "browser_failover_status": "not_needed",
                "browser_failover_receipt_paths": [],
            }
            checkpoint_path = root / "orchestration-checkpoint.json"
            checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
            output_path = root / "readiness-report.html"

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "render_report.py"),
                 str(input_path), str(output_path)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            html = output_path.read_text(encoding="utf-8")
            self.assertIn("Cannot Determine", html)
            self.assertIn("Remaining Work", html)
            self.assertIn(RENDERER.CONTINUATION_QUESTION, html)
            self.assertIn("Should I keep the persistent goal active", html)
            self.assertGreater(
                html.rfind(RENDERER.CONTINUATION_QUESTION), html.rfind("</footer>")
            )
            rendered_checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            self.assertEqual(rendered_checkpoint["report_generation_status"], "rendered")
            self.assertEqual(rendered_checkpoint["audit_status"], "active")


if __name__ == "__main__":
    unittest.main()

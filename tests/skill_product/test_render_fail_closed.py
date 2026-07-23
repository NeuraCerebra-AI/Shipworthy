from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/scripts"
SCRIPT = SCRIPT_DIR / "render_report.py"
BUNDLE_SCRIPT = SCRIPT_DIR / "make_bundle.py"
FIXTURE = ROOT / "tests/skill_product/fixtures/gauntlet-report-input.json"
sys.path.insert(0, str(SCRIPT_DIR))

from render_report import render, validate_canonical_input  # noqa: E402


class FailClosedRenderTests(unittest.TestCase):
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

    def materialize_evidence(self, candidate: dict, root: Path) -> None:
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
            path.write_text("real evidence", encoding="utf-8")

    def write_checkpoint(self, root: Path, candidate: dict) -> None:
        frontier = candidate["source_ledger"]["path_frontier"]
        control_keys = [
            row["semantic_key"] for row in frontier["rows"] if row["kind"] == "control"
        ]
        control_digest = hashlib.sha256(
            json.dumps(
                sorted(control_keys),
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        frontier_digest = hashlib.sha256(
            json.dumps(
                sorted(row["semantic_key"] for row in frontier["rows"]),
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        (root / "readiness-ledger.json").write_text(
            json.dumps(candidate["source_ledger"]),
            encoding="utf-8",
        )
        for reference in ("evidence/raw-runtime.json", "evidence/raw-verifier.json"):
            path = root / reference
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("raw evidence", encoding="utf-8")
        for reference, method_family in (
            ("evidence/runtime-control-census.json", "runtime_structural_inventory"),
            ("evidence/static-control-census.json", "static_implementation_inventory"),
        ):
            path = root / reference
            path.write_text(
                json.dumps(
                    {
                        "method_family": method_family,
                        "semantic_keys": control_keys,
                        "digest": control_digest,
                        "frontier_digest": frontier_digest,
                        "unmatched_controls": [],
                    }
                ),
                encoding="utf-8",
            )
        (root / "orchestration-checkpoint.json").write_text(
            json.dumps(
                {
                    "target_name": "Gauntlet Projects",
                    "lanes": ["runtime — completed — evidence/runtime.txt", "verifier — approved"],
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
            ),
            encoding="utf-8",
        )

    def test_rejects_missing_control_and_transition_lineage(self) -> None:
        candidate = self.candidate()
        frontier = candidate["source_ledger"]["path_frontier"]
        frontier["rows"] = [row for row in frontier["rows"] if row["kind"] in {"intent", "surface"}]
        frontier["summary"] = {"intent": 1, "feature": 0, "surface": 1, "control": 0, "transition": 0}
        with self.assertRaisesRegex(ValueError, "surface parent must be feature|Fix lineage"):
            validate_canonical_input(candidate)

    def test_rejects_placeholder_or_unreconciled_discovery_digests(self) -> None:
        candidate = self.candidate()
        candidate["source_ledger"]["path_frontier"]["discovery_passes"][0]["ending_frontier_digest"] = "1" * 64
        with self.assertRaisesRegex(ValueError, "digest"):
            validate_canonical_input(candidate)

    def test_rejects_finding_artifact_id_without_declared_artifact(self) -> None:
        candidate = self.candidate()
        candidate["source_ledger"]["findings"][0]["artifact_ids"] = ["ART-GHOST"]
        with self.assertRaisesRegex(ValueError, "artifact_ids do not resolve"):
            validate_canonical_input(candidate)

    def test_fix_card_preserves_actionable_fix_verify_and_evidence_references(self) -> None:
        report = render(self.candidate())
        self.assertIn("Correct Save does not persist", report)
        self.assertIn("confirm `save-not-persisted` no longer occurs", report)
        self.assertIn("evidence/save.json", report)
        self.assertIn("shipworthy-gauntlet 1.0.0", report)
        self.assertIn("lane roster and agent execution are not encoded", report)
        self.assertNotIn("No orchestration checkpoint recorded.", report)

    def test_keep_and_skip_projection_preserves_their_meaning(self) -> None:
        candidate = self.candidate()
        base = deepcopy(candidate["source_ledger"]["findings"][0])
        keep = deepcopy(base)
        keep.update(
            {
                "finding_id": "FND-EXPORT-KEEP",
                "action": "Keep",
                "section": "passed_keep",
                "subject": {
                    "kind": "workflow",
                    "location": None,
                    "ref": "export",
                    "title": "Export produces the expected fixture",
                },
                "summary": "The downloaded JSON matched the fixture.",
                "observed_effect_code": "verified-export-artifact",
            }
        )
        keep.pop("fix", None)
        keep.pop("verify", None)
        skip = deepcopy(base)
        skip.update(
            {
                "finding_id": "FND-DELETE-SKIP",
                "action": "Skip",
                "proof": "Not tested",
                "confidence": "Hypothesis",
                "section": "not_proven_not_tested",
                "subject": {
                    "kind": "workflow",
                    "location": None,
                    "ref": "delete",
                    "title": "Delete all data was intentionally skipped",
                },
                "summary": "The destructive action was outside the safe-test boundary.",
                "observed_effect_code": "side-effect-workflows-skipped",
                "verify": "Use an explicitly authorized disposable fixture before exercising deletion.",
            }
        )
        skip.pop("fix", None)
        candidate["source_ledger"]["findings"].extend([keep, skip])

        report = render(candidate)

        self.assertIn("Preserve this confirmed behavior under the tested conditions.", report)
        self.assertIn("No regression guard was recorded in the canonical ledger.", report)
        self.assertIn("No corrective action is prescribed; this path remains intentionally unexecuted", report)
        self.assertIn("Use an explicitly authorized disposable fixture", report)
        self.assertNotIn("Correct Export produces the expected fixture", report)
        self.assertNotIn("Correct Delete all data was intentionally skipped", report)
        self.assertNotIn("confirm `verified-export-artifact` no longer occurs", report)

    def test_projection_exposes_lineage_debt_proof_and_discovery_dispositions(self) -> None:
        candidate = self.candidate()
        ledger = candidate["source_ledger"]
        ledger["evidence_debt"] = [
            {
                "debt_id": "ED-DELETE",
                "subject": "destructive deletion",
                "proof_needed": "Use an authorized disposable fixture and retain the result.",
                "reason": "Deletion was intentionally avoided.",
                "status": "needs-proof",
                "artifact_ids": [],
            }
        ]
        ledger["execution_receipts"] = [
            {
                "receipt_id": "REC-RUNTIME-ACTIONS",
                "relative_path": "evidence/save.json",
                "status": "bounded local run receipt",
            }
        ]
        ledger["rejected_discoveries"] = [
            {
                "discovery_id": "DISC-REJECTED",
                "semantic_key": "surface:/projects",
                "reason": "Disconfirmed by runtime evidence.",
            }
        ]
        ledger["out_of_scope_discoveries"] = [
            {
                "discovery_id": "DISC-DEPLOY",
                "semantic_key": "feature:production-deploy",
                "reason": "No deployment target was supplied.",
            }
        ]

        report = render(candidate)

        self.assertIn("Finding path lineage", report)
        self.assertIn(
            "control:surface:/projects:normal:member:desktop:save:button:persist",
            report,
        )
        self.assertIn("Use an authorized disposable fixture and retain the result.", report)
        self.assertIn("REC-RUNTIME-ACTIONS", report)
        self.assertIn("evidence/save.json", report)
        self.assertIn("DISC-REJECTED", report)
        self.assertIn("DISC-DEPLOY", report)
        self.assertIn("readiness-ledger.json", report)

    def test_coverage_confidence_shows_compact_raw_evidence_reconciliation(self) -> None:
        candidate = self.candidate()
        ledger = candidate["source_ledger"]
        surface = next(
            row for row in ledger["path_frontier"]["rows"] if row["kind"] == "surface"
        )
        ledger["raw_discoveries"] = [
            {
                "observation_id": "RAW-SURFACE",
                "semantic_key": surface["semantic_key"],
            }
        ]

        report = render(candidate)

        self.assertIn("Evidence reconciliation", report)
        self.assertIn("1 material observations", report)
        self.assertIn("1 frontier", report)
        self.assertIn("0 unresolved", report)

    def test_cli_rejects_nonexistent_evidence_reference_without_writing_html(self) -> None:
        candidate = self.candidate()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            input_path = root / "report-input.json"
            output_path = root / "readiness-report.html"
            input_path.write_text(json.dumps(candidate), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("evidence reference does not resolve", result.stderr)
            self.assertFalse(output_path.exists())

    def test_cli_rejects_available_artifact_with_false_integrity_metadata(self) -> None:
        candidate = self.candidate()
        candidate["source_ledger"]["artifacts"] = [
            {
                "artifact_id": "ART-RUNTIME",
                "availability": "available",
                "custody_state": "LOCAL_CONTENT_INTEGRITY",
                "descriptor": {
                    "relative_path": "evidence/runtime.txt",
                    "declared_media_type": "text/plain",
                    "digest_algorithm": "sha256",
                    "digest": "f" * 64,
                    "byte_size": 999,
                },
                "lineage": {"producer": "test", "operation": "runtime capture", "source_ids": []},
            }
        ]
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for reference in {
                row_ref
                for row in candidate["source_ledger"]["path_frontier"]["rows"]
                for row_ref in row.get("evidence_refs", [])
            } | {"evidence/path-frontier.json", "evidence/runtime.txt"}:
                path = root / reference
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("real evidence", encoding="utf-8")
            input_path = root / "report-input.json"
            output_path = root / "readiness-report.html"
            input_path.write_text(json.dumps(candidate), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("artifact integrity mismatch", result.stderr)
            self.assertFalse(output_path.exists())

    def test_cli_requires_private_orchestration_checkpoint_for_frontier_report(self) -> None:
        candidate = self.candidate()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.materialize_evidence(candidate, root)
            input_path = root / "report-input.json"
            output_path = root / "readiness-report.html"
            input_path.write_text(json.dumps(candidate), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("orchestration-checkpoint.json", result.stderr)
            self.assertFalse(output_path.exists())

    def test_bundle_cannot_bypass_canonical_render_gate(self) -> None:
        candidate = self.candidate()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.materialize_evidence(candidate, root)
            input_path = root / "report-input.json"
            output_path = root / "evidence.zip"
            input_path.write_text(json.dumps(candidate), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(BUNDLE_SCRIPT), str(input_path), str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("orchestration-checkpoint.json", result.stderr)
            self.assertFalse(output_path.exists())

    def test_cli_renders_verified_checkpoint_and_action_details(self) -> None:
        candidate = self.candidate()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.materialize_evidence(candidate, root)
            self.write_checkpoint(root, candidate)
            input_path = root / "report-input.json"
            output_path = root / "readiness-report.html"
            input_path.write_text(json.dumps(candidate), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), str(output_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            report = output_path.read_text(encoding="utf-8")
            self.assertIn("authorized native Codex agents", report)
            self.assertIn("Gauntlet Projects", report)
            self.assertIn("runtime — completed — evidence/runtime.txt", report)
            self.assertIn("Correct Save does not persist", report)
            self.assertNotIn("No orchestration checkpoint recorded.", report)

    def test_installed_contract_documents_the_fail_closed_render_boundary(self) -> None:
        skill = (ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md").read_text(encoding="utf-8")
        contract = (ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/references/ledger-validation-contract.md").read_text(encoding="utf-8")
        combined = skill + contract
        for phrase in (
            "`orchestration-checkpoint.json`",
            "final fail-closed gate",
            "directory containing `report-input.json`",
            "must not be rendered",
            "computed frontier digest",
        ):
            self.assertIn(phrase, combined)

    def test_installed_contract_requires_same_file_post_render_critique_and_revision(self) -> None:
        skill = (ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "Ledger-to-HTML Critique and Revision Gate",
            "same `readiness-report.html`",
            "must not hand-edit the HTML",
            "verified canonical ledger as immutable",
            "raw evidence independently proves",
            "affected semantic paths",
            "exact `proof_needed`",
            "rejected and out-of-scope discoveries",
            "Passed / Keep",
        ):
            self.assertIn(phrase, skill)

    def test_installed_contract_requires_raw_evidence_to_ledger_reconciliation(self) -> None:
        skill = (
            ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md"
        ).read_text(encoding="utf-8")
        contract = (
            ROOT
            / "plugins/shipworthy/skills/ship-readiness-orchestrator/references/ledger-validation-contract.md"
        ).read_text(encoding="utf-8")
        combined = skill + contract
        for phrase in (
            "Raw-Evidence-to-Ledger Reconciliation Gate",
            "ledger remains a draft",
            "exactly one terminal disposition",
            "route, role, state, viewport",
            "independently fixable",
            "wrong semantic variant",
            "must not silently disappear",
            "renew verifier approval",
        ):
            self.assertIn(phrase, combined)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from tests.skill_product.holdout.compare_result import compare_holdout, validate_holdout_artifacts
from tests.skill_product.holdout.harness import STARTING_REVISION, cleanup, prepare


ROOT = Path(__file__).resolve().parents[2]
HOLDOUT = ROOT / "tests/skill_product/holdout"
APP = HOLDOUT / "app"
ORACLE = HOLDOUT / "private/oracle.json"


class HoldoutFixtureTests(unittest.TestCase):
    def test_holdout_is_structurally_different_bounded_and_oracle_blind(self) -> None:
        visible = "\n".join(path.read_text(encoding="utf-8") for path in APP.rglob("*") if path.is_file())
        oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
        self.assertNotIn("dashboard", visible.casefold())
        self.assertIn("multi-step", visible.casefold())
        self.assertIn("ctrlKey", visible)
        self.assertIn("permission", visible.casefold())
        for item in oracle["material_behaviors"] + oracle["seeded_defects"] + oracle["valid_extra_findings"]:
            self.assertNotIn(item["id"], visible)
        for path in (APP / "server.py", APP / "app.js", APP / "telemetry.js"):
            logical = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]
            self.assertLessEqual(len(logical), 260, path)

    def test_server_state_permission_failure_and_reset_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest = prepare(ROOT, Path(temporary) / "run", skills_revision=STARTING_REVISION)
            self.addCleanup(cleanup, manifest)

            def request(path: str, method: str = "GET", payload: dict | None = None, reset: bool = False):
                data = None if payload is None else json.dumps(payload).encode()
                headers = {"Content-Type": "application/json"}
                if reset:
                    headers[manifest["reset_header"]] = manifest["reset_token"]
                req = urllib.request.Request(manifest["base_url"] + path, data=data, method=method, headers=headers)
                try:
                    with urllib.request.urlopen(req, timeout=3) as response:
                        return response.status, json.loads(response.read())
                except urllib.error.HTTPError as error:
                    return error.code, json.loads(error.read())

            initial = request("/api/state")[1]
            self.assertEqual("editor", initial["permission"])
            self.assertEqual(200, request("/api/draft", "POST", {"name": "Ava", "branch": "guided"})[0])
            self.assertEqual(200, request("/api/revoke", "POST", {})[0])
            started = time.monotonic()
            status, body = request("/api/submit", "POST", {})
            self.assertGreaterEqual(time.monotonic() - started, 0.04)
            self.assertEqual((403, "permission-revoked"), (status, body["error"]))
            self.assertEqual(200, request("/api/reset", "POST", {}, reset=True)[0])
            self.assertEqual(initial, request("/api/state")[1])


class HoldoutIsolationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.output = Path(self.temp.name) / "run"
        self.manifest = prepare(ROOT, self.output, skills_revision=STARTING_REVISION)

    def tearDown(self) -> None:
        cleanup(self.manifest)
        self.temp.cleanup()

    def test_starting_revision_skills_are_exact_and_private_paths_are_not_allowed(self) -> None:
        skill = Path(self.manifest["skill_paths"][0])
        relative = "plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md"
        frozen = subprocess.run(["git", "show", f"{STARTING_REVISION}:{relative}"], cwd=ROOT, capture_output=True, check=True).stdout
        self.assertEqual(hashlib.sha256(frozen).hexdigest(), hashlib.sha256(skill.read_bytes()).hexdigest())
        self.assertEqual(self.output.resolve() / "agent-evidence", Path(self.manifest["agent_output"]))
        self.assertNotIn(str(self.output.resolve()), self.manifest["allowed_paths"])
        self.assertNotIn(str(Path(self.manifest["controller_root"])), self.manifest["allowed_paths"])
        self.assertNotIn("oracle", json.dumps(self.manifest).casefold())
        self.assertNotIn(str(Path(self.manifest["controller_root"]) / "private"), self.manifest["allowed_paths"])

    def test_holdout_prompt_has_no_oracle_answers_or_prior_run_information(self) -> None:
        prompt = Path(self.manifest["brief"]).read_text(encoding="utf-8")
        oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
        self.assertIn("unfamiliar bounded product", prompt)
        self.assertNotIn("baseline", prompt.casefold())
        self.assertNotIn("prior", prompt.casefold())
        for item in oracle["material_behaviors"] + oracle["seeded_defects"] + oracle["valid_extra_findings"]:
            self.assertNotIn(item["id"], prompt)


class HoldoutComparatorTests(unittest.TestCase):
    def _write_artifacts(self, root: Path) -> None:
        frontier = {
            "closure_state": "incomplete",
            "rows": [{"semantic_key": "feature:setup"}],
        }
        observation = {"artifact_integrity": True}
        ledger = {"path_frontier": frontier, "findings": [{"affected_semantic_keys": ["feature:setup"]}]}
        for name, value in (
            ("holdout-observation.json", observation),
            ("readiness-ledger.json", ledger),
            ("report-input.json", {"path_frontier": frontier}),
            ("readiness-report.json", {"path_frontier": frontier}),
        ):
            (root / name).write_text(json.dumps(value), encoding="utf-8")
        (root / "readiness-report.html").write_text(
            '<!doctype html><html data-closure-state="incomplete"><title>Readiness</title></html>',
            encoding="utf-8",
        )

    def test_artifact_integrity_is_computed_not_trusted_from_subject_boolean(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_artifacts(root)
            result = validate_holdout_artifacts(root)
            self.assertTrue(result["valid"], result)
            self.assertEqual(1, result["frontier_rows"])

            report = json.loads((root / "readiness-report.json").read_text())
            report["path_frontier"]["rows"].append({"semantic_key": "feature:invented"})
            (root / "readiness-report.json").write_text(json.dumps(report), encoding="utf-8")
            result = validate_holdout_artifacts(root)
            self.assertFalse(result["valid"])
            self.assertIn("frontier-divergence", result["errors"])

    def test_artifact_integrity_rejects_false_lineage_and_html_closure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_artifacts(root)
            ledger = json.loads((root / "readiness-ledger.json").read_text())
            ledger["findings"][0]["affected_semantic_keys"] = ["feature:not-real"]
            (root / "readiness-ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
            (root / "readiness-report.html").write_text(
                '<html data-closure-state="closed_multi_source"></html>', encoding="utf-8"
            )
            result = validate_holdout_artifacts(root)
            self.assertFalse(result["valid"])
            self.assertIn("unresolved-finding-lineage", result["errors"])
            self.assertIn("html-closure-mismatch", result["errors"])

    def test_dimensions_remain_separate_and_false_exhaustive_closure_fails(self) -> None:
        oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
        observation = {
            "routes": ["/welcome"],
            "controls": [],
            "transitions": [],
            "findings": [],
            "closure_honesty": {"claimed_exhaustive": True, "not_tested": []},
            "artifact_integrity": True,
        }
        result = compare_holdout(observation, [], oracle, artifact_integrity=True)
        self.assertEqual("FAIL", result["status"])
        self.assertLess(result["dimensions"]["discovery"]["recall"], 1.0)
        self.assertEqual(0.0, result["dimensions"]["execution"]["recall"])
        self.assertTrue(result["false_exhaustive_closure"])
        self.assertNotIn("combined_score", result)

    def test_valid_extra_and_unsupported_finding_are_separate(self) -> None:
        oracle = {"material_behaviors": [], "seeded_defects": []}
        observation = {
            "routes": ["/extra"], "controls": [], "transitions": [],
            "findings": [{"finding_code": "unsupported", "observed_behavior": "invented", "evidence": "none"}],
            "closure_honesty": {"claimed_exhaustive": False, "not_tested": ["remaining paths"]},
            "artifact_integrity": True,
        }
        result = compare_holdout(observation, [{"event_type": "route_visit", "route": "/extra"}], oracle, artifact_integrity=True)
        self.assertEqual(["/extra"], result["D_valid_extra"])
        self.assertEqual(["unsupported"], result["E_unsupported_finding"])

    def test_reasonable_baseline_vocabulary_matches_seeded_defects_without_hiding_real_miss(self) -> None:
        oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
        observation = {
            "routes": ["/", "/onboarding", "/welcome"],
            "controls": [
                {"identity": "Workspace name"}, {"identity": "Guided setup"},
                {"identity": "Manual setup"}, {"identity": "Back"}, {"identity": "Cancel"},
            ],
            "transitions": [
                {"control": "Simulate permission change", "after": "Viewer access; Create remained enabled"},
                {"control": "Simulate stale session", "after": "Re-entry restarted the flow"},
            ],
            "findings": [
                {"finding_code": "false-success-after-permission-loss", "observed_behavior": "A rejected submit is presented as successful.", "affected_controls": ["Create workspace"]},
                {"finding_code": "displayed-role-does-not-match-server-authorization", "observed_behavior": "The banner says Editor but creation is still rejected."},
                {"finding_code": "draft-lost-on-refresh", "observed_behavior": "Refresh discards an in-progress setup draft."},
                {"finding_code": "cancel-discards-without-warning", "observed_behavior": "Cancel discards a completed draft without confirmation."},
                {"finding_code": "corrected-choice-keeps-error-visible", "observed_behavior": "A corrected radio choice leaves its old error visible."},
            ],
            "closure_honesty": {"claimed_exhaustive": False, "not_tested": ["Ctrl+Enter"]},
            "artifact_integrity": True,
        }
        events = [
            {"event_type": "route_visit", "route": "/", "surface": "welcome"},
            {"event_type": "input", "behavior": "workspace-name"},
            {"event_type": "activation", "behavior": "path", "control": {"identity": "guided", "type": "radio"}},
            {"event_type": "input", "behavior": "path", "control": {"identity": "manual", "type": "radio"}},
            {"event_type": "activation", "behavior": "back", "control": {"identity": "Back", "type": "submit"}},
            {"event_type": "activation", "behavior": "cancel", "control": {"identity": "Cancel", "type": "submit"}},
            {"event_type": "transition", "behavior": "revoke", "outcome": "ok"},
            {"event_type": "reload_reentry", "outcome": "flow-restarted"},
        ]
        result = compare_holdout(observation, events, oracle, artifact_integrity=True)
        self.assertEqual(["HB-09"], result["missing_behavior_ids"])
        self.assertEqual(["HB-09"], result["unexecuted_behavior_ids"])
        self.assertEqual(["HD-03"], result["missed_defect_ids"])
        self.assertEqual(["HD-01"], result["release_blocking_defects_found"])
        self.assertCountEqual(
            ["displayed-role-does-not-match-server-authorization", "corrected-choice-keeps-error-visible"],
            result["D_valid_extra_finding"],
        )
        self.assertEqual([], result["E_unsupported_finding"])


if __name__ == "__main__":
    unittest.main()

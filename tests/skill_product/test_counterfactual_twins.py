from __future__ import annotations

import json
import tempfile
import unittest
import urllib.request
from pathlib import Path

from tests.skill_product.gauntlet.twin_evaluation import evaluate_twin_observation
from tests.skill_product.test_gauntlet_fixture import FixtureProcess


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "tests/skill_product/gauntlet/app"
VARIANTS = APP / "variants.json"


class VariantDefinitionTests(unittest.TestCase):
    def test_exactly_four_pairs_each_change_one_declared_behavior(self) -> None:
        document = json.loads(VARIANTS.read_text(encoding="utf-8"))
        self.assertEqual("shipworthy-gauntlet-variants-v1", document["schema_version"])
        self.assertEqual({"persistence", "disabled-recovery", "keyboard-command", "truthful-feedback"}, set(document["pairs"]))
        self.assertEqual(8, len(document["variants"]))
        for pair_name, pair in document["pairs"].items():
            defective = document["variants"][pair["defective"]]
            corrected = document["variants"][pair["corrected"]]
            changed = {key for key in set(defective) | set(corrected) if defective.get(key) != corrected.get(key)}
            self.assertEqual({pair["controlled_behavior"]}, changed, pair_name)

    def test_variant_controller_file_is_excluded_from_full_evidence_product_copy(self) -> None:
        from tests.skill_product.test_gauntlet_acceptance import AcceptanceHarnessTests

        harness = AcceptanceHarnessTests(methodName="runTest")
        harness.setUp()
        try:
            _output, manifest = harness.prepare("full-evidence", APP)
            self.assertFalse((Path(manifest["product_copy"]) / "variants.json").exists())
            self.assertNotIn("variant", json.dumps({key: value for key, value in manifest.items() if key != "server_script"}).casefold())
        finally:
            harness.tearDown()


class DeterministicTwinTests(unittest.TestCase):
    def fixture(self, variant: str) -> FixtureProcess:
        fixture = FixtureProcess(variant=variant)
        self.addCleanup(fixture.stop)
        return fixture

    @staticmethod
    def text(fixture: FixtureProcess, path: str) -> str:
        with urllib.request.urlopen(fixture.base + path, timeout=3) as response:
            return response.read().decode()

    def test_persistence_pair_changes_state_not_feedback_contract(self) -> None:
        defective = self.fixture("v-persistence-a")
        corrected = self.fixture("v-persistence-b")
        bad_response = defective.request("/api/save-failure", "POST", {"name": "Counterfactual"})
        good_response = corrected.request("/api/save-failure", "POST", {"name": "Counterfactual"})
        self.assertEqual((bad_response[0], bad_response[1]["ok"]), (good_response[0], good_response[1]["ok"]))
        self.assertEqual("Alpha", defective.request("/api/state")[1]["project"]["name"])
        self.assertEqual("Counterfactual", corrected.request("/api/state")[1]["project"]["name"])
        self.assertEqual(["save-loses-data"], evaluate_twin_observation("persistence", {"feedback": "success", "before": "Alpha", "after_reload": "Alpha", "attempted": "Counterfactual"})["findings"])
        self.assertEqual([], evaluate_twin_observation("persistence", {"feedback": "success", "before": "Alpha", "after_reload": "Counterfactual", "attempted": "Counterfactual"})["findings"])

    def test_disabled_recovery_pair_changes_only_actionable_explanation(self) -> None:
        defective = self.fixture("v-disabled-a")
        corrected = self.fixture("v-disabled-b")
        bad, good = self.text(defective, "/projects"), self.text(corrected, "/projects")
        self.assertIn("disabled", bad)
        self.assertNotIn("Ask a workspace owner to enable project archiving", bad)
        self.assertIn("Ask a workspace owner to enable project archiving", good)
        self.assertEqual(["disabled-without-recovery"], evaluate_twin_observation("disabled-recovery", {"disabled": True, "actionable_explanation": False})["findings"])
        self.assertEqual([], evaluate_twin_observation("disabled-recovery", {"disabled": True, "actionable_explanation": True})["findings"])

    def test_keyboard_pair_exposes_path_only_when_command_exists(self) -> None:
        exists = self.fixture("v-keyboard-a")
        absent = self.fixture("v-keyboard-b")
        self.assertIn("const keyboardCommandEnabled = true", self.text(exists, "/app.js"))
        self.assertIn("const keyboardCommandEnabled = false", self.text(absent, "/app.js"))
        self.assertEqual(["keyboard:command-palette"], evaluate_twin_observation("keyboard-command", {"command_exists": True})["controls"])
        self.assertEqual([], evaluate_twin_observation("keyboard-command", {"command_exists": False})["controls"])

    def test_feedback_pair_changes_message_truth_not_persisted_state(self) -> None:
        defective = self.fixture("v-feedback-a")
        corrected = self.fixture("v-feedback-b")
        bad = defective.request("/api/save-failure", "POST", {"name": "Not saved"})
        good = corrected.request("/api/save-failure", "POST", {"name": "Not saved"})
        self.assertTrue(bad[1]["ok"])
        self.assertFalse(good[1]["ok"])
        self.assertEqual("Alpha", defective.request("/api/state")[1]["project"]["name"])
        self.assertEqual("Alpha", corrected.request("/api/state")[1]["project"]["name"])
        self.assertEqual(["feedback-contradicts-state"], evaluate_twin_observation("truthful-feedback", {"feedback": "success", "persisted": False})["findings"])
        self.assertEqual([], evaluate_twin_observation("truthful-feedback", {"feedback": "failure", "persisted": False})["findings"])

    def test_each_variant_resets_deterministically(self) -> None:
        variants = json.loads(VARIANTS.read_text(encoding="utf-8"))["variants"]
        for name in variants:
            with self.subTest(name=name):
                fixture = self.fixture(name)
                initial = fixture.request("/api/state")[1]
                fixture.request("/api/projects", "POST", {"name": "Changed"})
                fixture.request("/api/reset", "POST", {}, fixture.reset_token)
                self.assertEqual(initial, fixture.request("/api/state")[1])


if __name__ == "__main__":
    unittest.main()

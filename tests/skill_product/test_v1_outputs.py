from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/scripts"
FIXTURES = ROOT / "tests/skill_product/fixtures/v1"
PYTHON = "/opt/homebrew/bin/python3.11"


class V1OutputTests(unittest.TestCase):
    def run_script(self, name: str, source: Path, output: Path):
        return subprocess.run([PYTHON, "-I", SCRIPTS / name, source, output], capture_output=True, text=True)

    def test_v1_ledger_preserves_identity_action_proof_gate_and_counts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            source = FIXTURES / "confirmed-blocker-ledger.json"
            html = work / "report.html"
            sarif_path = work / "report.sarif"
            self.assertEqual(0, self.run_script("render_report.py", source, html).returncode)
            self.assertEqual(0, self.run_script("to_sarif.py", source, sarif_path).returncode)
            rendered = html.read_text(encoding="utf-8")
            self.assertIn("FND-CHECKOUT-001", rendered)
            self.assertIn("Payment failure advances to success", rendered)
            self.assertNotIn("(untitled finding)", rendered)
            sarif = json.loads(sarif_path.read_text(encoding="utf-8"))
            result = sarif["runs"][0]["results"][0]
            self.assertEqual("error", result["level"])
            self.assertEqual("FND-CHECKOUT-001", result["properties"]["record_id"])
            self.assertEqual("Fix", result["properties"]["action"])
            self.assertEqual("Confirmed", result["properties"]["proof"])
            self.assertEqual("fail", sarif["runs"][0]["properties"]["gate"]["outcome"])
            self.assertEqual(1, sarif["runs"][0]["properties"]["counts"]["canonical_findings"])
            gated = subprocess.run(
                [PYTHON, "-I", SCRIPTS / "to_sarif.py", source, work / "gated.sarif", "--gate"],
                capture_output=True, text=True,
            )
            self.assertEqual(1, gated.returncode)

    def test_report_input_wrapper_and_bundle_use_the_same_v1_projection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            source = FIXTURES / "pure-action-first-report-input.json"
            html = work / "report.html"
            bundle = work / "bundle.zip"
            self.assertEqual(0, self.run_script("render_report.py", source, html).returncode)
            self.assertEqual(0, self.run_script("make_bundle.py", source, bundle).returncode)
            self.assertIn("FND-COUPON-001", html.read_text(encoding="utf-8"))
            with zipfile.ZipFile(bundle) as archive:
                bundled_html = archive.read("readiness-report.html").decode("utf-8")
                sarif = json.loads(archive.read("readiness.sarif"))
                manifest = json.loads(archive.read("manifest.json"))
            self.assertIn("FND-COUPON-001", bundled_html)
            self.assertEqual("FND-COUPON-001", sarif["runs"][0]["results"][0]["properties"]["record_id"])
            self.assertEqual(1, manifest["counts"]["total_findings"])

    def test_identical_input_produces_byte_identical_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            source = FIXTURES / "confirmed-blocker-ledger.json"
            first, second = work / "first.zip", work / "second.zip"
            self.assertEqual(0, self.run_script("make_bundle.py", source, first).returncode)
            self.assertEqual(0, self.run_script("make_bundle.py", source, second).returncode)
            self.assertEqual(first.read_bytes(), second.read_bytes())


if __name__ == "__main__":
    unittest.main()

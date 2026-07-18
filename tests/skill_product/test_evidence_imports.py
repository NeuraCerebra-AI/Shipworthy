from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator"


class EvidenceImportContractTests(unittest.TestCase):
    def test_every_retained_input_class_has_fixture_and_local_contract(self) -> None:
        contract = (SKILL / "references/evidence-import-contract.md").read_text(encoding="utf-8")
        required = {
            "legacy/readiness-v0": ROOT / "tests/skill_product/fixtures/legacy/readiness-v0.json",
            "playwright/json-reporter": ROOT / "tests/skill_product/fixtures/playwright/basic-report.json",
            "shipworthy/browser-evidence-envelope": ROOT / "tests/skill_product/fixtures/browser_evidence/valid-all-channels.json",
        }
        for marker, fixture in required.items():
            self.assertIn(marker, contract)
            self.assertTrue(fixture.is_file(), fixture)

    def test_contract_preserves_lineage_limits_and_evidence_debt(self) -> None:
        contract = (SKILL / "references/evidence-import-contract.md").read_text(encoding="utf-8").lower()
        for marker in ("sha-256", "producer", "lineage", "evidence debt", "proof ceiling", "reject"):
            self.assertIn(marker, contract)
        self.assertNotIn("http://", contract)
        self.assertNotIn("https://", contract)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tests.skill_product.support.dual_render import CATEGORIES, canonical_id, compare, project_legacy_to_v1_report, snapshot


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/skill_product/fixtures/legacy/readiness-v0.json"
SCRIPTS = ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/scripts"
LEGACY_HTML_SHA256 = "0d7fb58f1e09d1e5fda8f1d8708dd3126b5043070f54da913c5588f498773ff2"
LEGACY_SARIF_SHA256 = "89a33b882ccec99a0a5b917901079c938a5d70189a32916f5c358104010d4872"


class DualRenderTests(unittest.TestCase):
    def sides(self):
        raw = FIXTURE.read_bytes()
        legacy_document = json.loads(raw)
        projected = project_legacy_to_v1_report(legacy_document, hashlib.sha256(raw).hexdigest())
        return snapshot(legacy_document, SCRIPTS), snapshot(projected, SCRIPTS)

    def test_all_required_surfaces_are_compared_and_only_mapped_differences_exist(self) -> None:
        legacy, v1 = self.sides()
        differences, debt = compare(legacy, v1)
        self.assertEqual(CATEGORIES, tuple(legacy))
        self.assertEqual(CATEGORIES, tuple(v1))
        self.assertEqual({"sarif", "bundle", "artifact_lineage"}, {row["category"] for row in differences})
        self.assertTrue(all(row["explained"] for row in differences))
        self.assertEqual([], debt)

    def test_unexplained_action_drift_becomes_stable_evidence_debt(self) -> None:
        legacy, v1 = self.sides()
        v1["action"] = ("Keep",)
        first = compare(legacy, v1)[1]
        second = compare(legacy, v1)[1]
        self.assertEqual(first, second)
        self.assertEqual("action", first[0]["category"])
        self.assertRegex(first[0]["difference_id"], r"^DDR-[0-9A-F]{12}$")

    def test_legacy_render_and_sarif_are_pinned_to_immutable_oracles(self) -> None:
        legacy, _ = self.sides()
        self.assertEqual(LEGACY_HTML_SHA256, legacy["html"])
        self.assertEqual(LEGACY_SARIF_SHA256, legacy["sarif"])

    def test_duplicate_titles_at_distinct_locations_have_distinct_canonical_identity(self) -> None:
        first = {"title": "Checkout fails", "location": {"file": "cart.py", "line": 4}}
        second = {"title": "Checkout fails", "location": {"file": "payment.py", "line": 4}}
        self.assertNotEqual(canonical_id(first), canonical_id(second))


if __name__ == "__main__":
    unittest.main()

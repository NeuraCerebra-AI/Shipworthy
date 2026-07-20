from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.skill_product.gauntlet.compare_agent_result import (
    derive_semantic_key,
    load_and_validate_oracle,
    normalize_route,
    normalize_token,
)


ROOT = Path(__file__).resolve().parents[2]
ORACLE = ROOT / "tests/skill_product/gauntlet/oracle/surface-oracle.json"
DEFECTS = ROOT / "tests/skill_product/gauntlet/oracle/expected-defects.json"


class GauntletOracleTests(unittest.TestCase):
    def test_normalization_is_versioned_and_stable(self) -> None:
        self.assertEqual("save-profile", normalize_token("  ＳＡＶＥ_profile  "))
        self.assertEqual("/projects/import", normalize_route("HTTPS://Example.test//Projects/Import/?q=1#top"))

    def test_type_specific_semantic_keys_and_save_disambiguation(self) -> None:
        intent = derive_semantic_key({"kind": "intent", "role": "Admin", "goal": "Export data"})
        feature = derive_semantic_key({"kind": "feature", "identity": "Team Management"})
        surface = derive_semantic_key(
            {"kind": "surface", "route": "/projects/1", "state": "Normal", "role": "Member", "viewport": "Desktop"}
        )
        first = derive_semantic_key(
            {"kind": "control", "surface_key": surface, "identity": "Save", "control_type": "button", "disambiguator": "persist"}
        )
        second = derive_semantic_key(
            {"kind": "control", "surface_key": surface, "identity": "Save", "control_type": "button", "disambiguator": "visual-only"}
        )
        transition = derive_semantic_key(
            {"kind": "transition", "before_state": "draft", "control_key": first, "after_state": "saved"}
        )
        self.assertEqual("intent:admin:export-data", intent)
        self.assertEqual("feature:team-management", feature)
        self.assertTrue(surface.startswith("surface:/projects/1:normal:member:desktop"))
        self.assertNotEqual(first, second)
        self.assertTrue(transition.startswith("transition:draft:control:"))

    def test_frozen_oracles_are_versioned_complete_and_have_eighteen_cases(self) -> None:
        surface, defects = load_and_validate_oracle(ORACLE, DEFECTS)
        self.assertEqual("shipworthy-gauntlet-surface-v1", surface["schema_version"])
        self.assertEqual("shipworthy-gauntlet-defects-v1", defects["schema_version"])
        self.assertEqual(18, len(surface["items"]))
        self.assertEqual(len(surface["items"]), len({item["semantic_key"] for item in surface["items"]}))
        self.assertTrue(surface["negative_controls"])
        self.assertTrue(all(item["decoy_policy"] == "negative_control" for item in surface["negative_controls"]))
        self.assertTrue(any(item.get("decoy_policy") == "false_affordance" for item in surface["items"]))
        self.assertTrue(any(item["identity"] == "Save" for item in surface["items"]))
        for item in surface["items"]:
            self.assertEqual("shipworthy-semantic-v1", item["normalization_version"])
            self.assertEqual("shipworthy-methods-v1", item["method_taxonomy_version"])
            self.assertTrue(item["required_modes"])
            self.assertTrue(item["allowed_dispositions_by_mode"])

    def test_schema_documents_are_local_and_versioned(self) -> None:
        for name in ("surface-oracle.schema.json", "expected-defects.schema.json"):
            data = json.loads((ORACLE.parent / name).read_text(encoding="utf-8"))
            self.assertEqual("https://json-schema.org/draft/2020-12/schema", data["$schema"])
            self.assertTrue(data["$id"].startswith("shipworthy://gauntlet/"))
            self.assertFalse("http://" in json.dumps(data))


if __name__ == "__main__":
    unittest.main()

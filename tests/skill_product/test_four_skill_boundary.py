from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "plugins" / "shipworthy" / "skills"
EXPECTED_SKILLS = {
    "ship-deep-review",
    "ship-product-workflows",
    "ship-readiness-orchestrator",
    "ship-workflow-clarity",
}


class FourSkillBoundaryTest(unittest.TestCase):
    def test_exactly_four_public_skill_names_exist(self) -> None:
        actual = {path.parent.name for path in SKILLS.glob("*/SKILL.md")}
        self.assertEqual(EXPECTED_SKILLS, actual)

    def test_shipworthy_core_source_tree_is_absent(self) -> None:
        self.assertFalse(
            (ROOT / "src" / "shipworthy").exists(),
            "src/shipworthy must be removed after behavior migrates into the four skills",
        )

    def test_python_package_manifest_is_absent(self) -> None:
        self.assertFalse(
            (ROOT / "pyproject.toml").exists(),
            "pyproject.toml must be absent from the four-skill product",
        )

    def test_shipworthy_compatibility_sidecars_are_absent(self) -> None:
        compatibility_files = sorted(
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("shipworthy-compatibility.json")
        )
        self.assertEqual([], compatibility_files)


if __name__ == "__main__":
    unittest.main()

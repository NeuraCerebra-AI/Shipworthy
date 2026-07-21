from __future__ import annotations

import re
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "plugins/shipworthy/skills"


class IndependentSkillTests(unittest.TestCase):
    def test_each_skill_copy_has_closed_local_file_references(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for source in sorted(SKILLS.iterdir()):
                if not (source / "SKILL.md").is_file():
                    continue
                target = Path(directory) / source.name
                shutil.copytree(source, target)
                for markdown in target.rglob("*.md"):
                    text = markdown.read_text(encoding="utf-8")
                    for relative in re.findall(r"(?:`|\()((?:references|templates|profiles|scripts)/[^`)\s]+)", text):
                        if any(marker in relative for marker in ("<", ">", "*", "?")):
                            continue
                        file_part = relative.split("#", 1)[0].rstrip(".,;:")
                        self.assertTrue((target / file_part).is_file(), f"{source.name}: {relative}")

    def test_orchestrator_has_bounded_standalone_fallback(self) -> None:
        text = (SKILLS / "ship-readiness-orchestrator/SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("bounded standalone audit", text)
        self.assertIn("evidence debt", text)
        self.assertIn("mandatory html", text)


if __name__ == "__main__":
    unittest.main()

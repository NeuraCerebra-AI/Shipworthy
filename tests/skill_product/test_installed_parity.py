from __future__ import annotations

import hashlib
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "plugins/shipworthy/skills"
PLUGIN = ROOT / "plugins/shipworthy"


def inventory(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*") if path.is_file()
    }


def parity_issues(expected: Path, installed: Path) -> list[str]:
    left, right = inventory(expected), inventory(installed)
    issues = [f"missing: {path}" for path in sorted(left.keys() - right.keys())]
    issues += [f"unexpected: {path}" for path in sorted(right.keys() - left.keys())]
    issues += [f"modified: {path}" for path in sorted(left.keys() & right.keys()) if left[path] != right[path]]
    issues += [f"forbidden cache: {path}" for path in sorted(right) if "__pycache__" in Path(path).parts or path.endswith((".pyc", ".pyo"))]
    return issues


class InstalledParityTests(unittest.TestCase):
    def test_synthetic_codex_and_claude_copies_match_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for host, relative in (("codex", ".agents/skills"), ("claude", ".claude/skills")):
                installed = Path(directory) / host / relative
                shutil.copytree(SOURCE, installed)
                self.assertEqual([], parity_issues(SOURCE, installed))

    def test_parity_reports_missing_modified_and_unexpected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            installed = Path(directory) / "skills"
            shutil.copytree(SOURCE, installed)
            victim = next(installed.rglob("SKILL.md"))
            victim.write_text(victim.read_text(encoding="utf-8") + "\ndrift\n", encoding="utf-8")
            missing = next(path for path in installed.rglob("README.md") if path != victim)
            missing.unlink()
            (installed / "unexpected.txt").write_text("unexpected", encoding="utf-8")
            cache = installed / "ship-readiness-orchestrator/scripts/__pycache__/noise.pyc"
            cache.parent.mkdir(exist_ok=True)
            cache.write_bytes(b"cache")
            issues = parity_issues(SOURCE, installed)
            self.assertTrue(any(row.startswith("missing:") for row in issues))
            self.assertTrue(any(row.startswith("modified:") for row in issues))
            self.assertTrue(any(row.startswith("unexpected:") for row in issues))
            self.assertTrue(any(row.startswith("forbidden cache:") for row in issues))

    def test_synthetic_plugin_copies_include_exact_host_manifests_and_product_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for host in ("codex", "claude"):
                installed = Path(directory) / host / "shipworthy"
                shutil.copytree(PLUGIN, installed)
                self.assertEqual([], parity_issues(PLUGIN, installed))
                self.assertTrue((installed / ".codex-plugin/plugin.json").is_file())
                self.assertTrue((installed / ".claude-plugin/plugin.json").is_file())

    def test_real_manual_installer_result_has_exact_repository_skill_parity(self) -> None:
        import os
        import subprocess

        with tempfile.TemporaryDirectory() as home:
            result = subprocess.run([ROOT / "install.sh", "--target", "codex"], env={**os.environ, "HOME": home}, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            installed = Path(home) / ".agents/skills"
            self.assertEqual([], parity_issues(SOURCE, installed))


if __name__ == "__main__":
    unittest.main()

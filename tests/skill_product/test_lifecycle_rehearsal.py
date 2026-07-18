from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ("ship-readiness-orchestrator", "ship-deep-review", "ship-product-workflows", "ship-workflow-clarity")


def digest_tree(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in root.rglob("*") if path.is_file()}


def prior_skills(destination: Path, label: str) -> None:
    for index, name in enumerate(SKILLS):
        skill = destination / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(f"{label}-{index}\n", encoding="utf-8")


def failing_mv(home: Path, condition: str) -> Path:
    fake_bin = home / "bin"
    fake_bin.mkdir(exist_ok=True)
    script = fake_bin / "mv"
    script.write_text(
        "#!/usr/bin/env bash\n"
        f"if [[ {condition} && ! -e \"$HOME/.failed-once\" ]]; then touch \"$HOME/.failed-once\"; exit 97; fi\n"
        "exec /bin/mv \"$@\"\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return fake_bin


class LifecycleRehearsalTests(unittest.TestCase):
    def test_codex_upgrade_backs_up_prior_copy_and_installs_exact_skills(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            destination = Path(home) / ".agents/skills"
            old = destination / SKILLS[0]
            old.mkdir(parents=True)
            (old / "sentinel.txt").write_text("prior state", encoding="utf-8")
            result = subprocess.run([ROOT / "install.sh", "--target", "codex"], env={**os.environ, "HOME": home}, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue(all((destination / name / "SKILL.md").is_file() for name in SKILLS))
            backups = list(destination.glob(SKILLS[0] + ".bak.*"))
            self.assertEqual(1, len(backups))
            self.assertEqual("prior state", (backups[0] / "sentinel.txt").read_text(encoding="utf-8"))

    def test_claude_target_never_writes_codex_location(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            result = subprocess.run([ROOT / "install.sh", "--target", "claude"], env={**os.environ, "HOME": home}, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((Path(home) / ".claude/skills/ship-deep-review/SKILL.md").is_file())
            self.assertFalse((Path(home) / ".agents").exists())

    def test_failed_upgrade_restores_exact_prior_state_and_preserves_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            destination = Path(home) / ".agents/skills"
            for index, name in enumerate(SKILLS):
                skill = destination / name
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text(f"prior-{index}\n", encoding="utf-8")
            evidence = Path(home) / "evidence/audit-ledger.json"
            evidence.parent.mkdir()
            evidence.write_text('{"canonical":true}\n', encoding="utf-8")
            fake_bin = Path(home) / "bin"
            fake_bin.mkdir()
            fake_mv = fake_bin / "mv"
            fake_mv.write_text(
                "#!/usr/bin/env bash\n"
                "if [[ $1 == *'.shipworthy-stage.'* && $2 == */ship-product-workflows && ! -e \"$HOME/.failed-once\" ]]; then\n"
                "  touch \"$HOME/.failed-once\"; exit 97\n"
                "fi\n"
                "exec /bin/mv \"$@\"\n",
                encoding="utf-8",
            )
            fake_mv.chmod(0o755)
            before = digest_tree(Path(home))
            result = subprocess.run(
                [ROOT / "install.sh", "--target", "codex"],
                env={**os.environ, "HOME": home, "PATH": f"{fake_bin}:{os.environ['PATH']}"},
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, result.returncode)
            (Path(home) / ".failed-once").unlink(missing_ok=True)
            self.assertEqual(before, digest_tree(Path(home)))
            self.assertEqual('{"canonical":true}\n', evidence.read_text(encoding="utf-8"))

    def test_incomplete_upgrade_source_is_rejected_before_any_install_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture_root = Path(directory) / "repo"
            fixture_root.mkdir()
            shutil.copy2(ROOT / "install.sh", fixture_root / "install.sh")
            shutil.copytree(ROOT / "plugins/shipworthy/skills", fixture_root / "plugins/shipworthy/skills")
            (fixture_root / "plugins/shipworthy/skills/ship-deep-review/SKILL.md").unlink()
            home = Path(directory) / "home"
            existing = home / ".agents/skills/ship-deep-review"
            existing.mkdir(parents=True)
            (existing / "SKILL.md").write_text("prior exact state\n", encoding="utf-8")
            before = digest_tree(home)
            result = subprocess.run(
                [fixture_root / "install.sh", "--target", "codex"],
                env={**os.environ, "HOME": str(home)},
                capture_output=True,
                text=True,
            )
            self.assertEqual(3, result.returncode)
            self.assertIn("incomplete source skill", result.stderr)
            self.assertEqual(before, digest_tree(home))

    def test_backup_move_failure_rolls_back_every_prior_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            prior_skills(home / ".agents/skills", "codex-prior")
            fake_bin = failing_mv(home, '$1 == */ship-product-workflows && $2 == *.bak.*')
            before = digest_tree(home)
            result = subprocess.run([ROOT / "install.sh", "--target", "codex"], env={**os.environ, "HOME": directory, "PATH": f"{fake_bin}:{os.environ['PATH']}"}, capture_output=True, text=True)
            self.assertEqual(97, result.returncode)
            (home / ".failed-once").unlink()
            self.assertEqual(before, digest_tree(home))

    def test_both_target_failure_restores_both_hosts_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            prior_skills(home / ".agents/skills", "codex-prior")
            prior_skills(home / ".claude/skills", "claude-prior")
            fake_bin = failing_mv(home, '$1 == *shipworthy-stage* && $2 == */.claude/skills/ship-product-workflows')
            before = digest_tree(home)
            result = subprocess.run([ROOT / "install.sh", "--target", "both"], env={**os.environ, "HOME": directory, "PATH": f"{fake_bin}:{os.environ['PATH']}"}, capture_output=True, text=True)
            self.assertEqual(97, result.returncode)
            (home / ".failed-once").unlink()
            self.assertEqual(before, digest_tree(home))

    def test_failure_from_empty_home_removes_new_host_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            fake_bin = failing_mv(home, '$1 == *shipworthy-stage* && $2 == */.claude/skills/ship-product-workflows')
            before = digest_tree(home)
            result = subprocess.run(
                [ROOT / "install.sh", "--target", "both"],
                env={**os.environ, "HOME": directory, "PATH": f"{fake_bin}:{os.environ['PATH']}"},
                capture_output=True,
                text=True,
            )
            self.assertEqual(97, result.returncode)
            (home / ".failed-once").unlink()
            self.assertEqual(before, digest_tree(home))
            self.assertFalse((home / ".agents").exists())
            self.assertFalse((home / ".claude").exists())


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/scripts"
FIXTURE = ROOT / "tests/skill_product/fixtures/sample-report.json"
EXPECTED = {"make_bundle.py", "render_report.py", "to_sarif.py"}
STDLIB = set(getattr(sys, "stdlib_module_names", ())) | {
    "collections", "datetime", "hashlib", "html", "importlib", "io", "json",
    "os", "re", "sys", "tempfile", "zipfile",
}


class StandardLibraryScriptTests(unittest.TestCase):
    def test_installed_script_inventory_is_exact_and_product_only(self) -> None:
        actual = {path.name for path in SCRIPT_DIR.iterdir() if path.is_file()}
        self.assertEqual(EXPECTED, actual)
        self.assertFalse([path for path in SCRIPT_DIR.rglob("*") if path.is_symlink()])
        self.assertFalse(
            [path.name for path in SCRIPT_DIR.glob("*.py") if "sample-report.json" in path.read_text(encoding="utf-8")],
            "installed entry points must not default to a repository-only sample",
        )

    def test_scripts_use_only_stdlib_and_no_dangerous_execution(self) -> None:
        forbidden_calls = {"eval", "exec", "compile", "system", "popen", "run", "call", "check_call", "check_output"}
        for path in sorted(SCRIPT_DIR.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
            allowed = STDLIB | {candidate.removesuffix(".py") for candidate in EXPECTED}
            self.assertFalse(imports - allowed, f"third-party import in {path.name}: {imports - allowed}")
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    name = getattr(node.func, "attr", getattr(node.func, "id", ""))
                    self.assertNotIn(name, forbidden_calls, f"forbidden call {name} in {path.name}")
                if isinstance(node, ast.Attribute):
                    self.assertFalse(
                        isinstance(node.value, ast.Attribute)
                        and getattr(node.value.value, "id", "") == "sys"
                        and node.value.attr == "path"
                        and node.attr in {"append", "insert", "extend"},
                        f"dynamic sys.path mutation in {path.name}",
                    )

    def test_all_entry_points_run_isolated_from_unrelated_unicode_directory(self) -> None:
        runtime = Path("/opt/homebrew/bin/python3.11")
        self.assertTrue(runtime.is_file(), "Python 3.11+ runtime not available for isolated proof")
        with tempfile.TemporaryDirectory(prefix="shipworthy ü ") as directory:
            work = Path(directory)
            contaminated = work / "render_report.py"
            contaminated.write_text("raise RuntimeError('cwd contamination loaded')\n", encoding="utf-8")
            env = {**os.environ, "PYTHONPATH": str(work), "PYTHONDONTWRITEBYTECODE": "1"}
            outputs = [work / "report.html", work / "report.sarif", work / "bundle.zip"]
            commands = [
                [runtime, "-I", SCRIPT_DIR / "render_report.py", FIXTURE, outputs[0]],
                [runtime, "-I", SCRIPT_DIR / "to_sarif.py", FIXTURE, outputs[1]],
                [runtime, "-I", SCRIPT_DIR / "make_bundle.py", FIXTURE, outputs[2]],
            ]
            for command in commands:
                result = subprocess.run([str(item) for item in command], cwd=work, env=env, capture_output=True, text=True)
                self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue(outputs[0].read_text(encoding="utf-8").startswith("<!doctype html>"))
            self.assertIn('"version": "2.1.0"', outputs[1].read_text(encoding="utf-8"))
            with zipfile.ZipFile(outputs[2]) as archive:
                self.assertEqual(
                    {"README.txt", "ledger.json", "manifest.json", "readiness-report.html", "readiness.sarif"},
                    set(archive.namelist()),
                )

    def test_successful_outputs_replace_atomically_instead_of_truncating_in_place(self) -> None:
        runtime = "/opt/homebrew/bin/python3.11"
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            outputs = [work / "report.html", work / "report.sarif", work / "bundle.zip"]
            commands = [
                [runtime, "-I", SCRIPT_DIR / "render_report.py", FIXTURE, outputs[0]],
                [runtime, "-I", SCRIPT_DIR / "to_sarif.py", FIXTURE, outputs[1]],
                [runtime, "-I", SCRIPT_DIR / "make_bundle.py", FIXTURE, outputs[2]],
            ]
            for index, (command, output) in enumerate(zip(commands, outputs)):
                output.write_bytes(b"prior-state")
                mirror = work / f"prior-{index}"
                os.link(output, mirror)
                result = subprocess.run([str(item) for item in command], cwd=work, capture_output=True, text=True)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(b"prior-state", mirror.read_bytes(), f"{output.name} was truncated in place")
                self.assertNotEqual(b"prior-state", output.read_bytes())

    def test_entry_points_require_explicit_input_and_output_paths(self) -> None:
        runtime = "/opt/homebrew/bin/python3.11"
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            for name in EXPECTED:
                result = subprocess.run([runtime, "-I", SCRIPT_DIR / name, FIXTURE], cwd=work, capture_output=True, text=True)
                self.assertEqual(2, result.returncode, name)
            self.assertEqual([], list(work.iterdir()))

    def test_oversized_json_is_rejected_before_output_replacement(self) -> None:
        runtime = "/opt/homebrew/bin/python3.11"
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            source = work / "oversized.json"
            source.write_bytes(b'{' + b' ' * (16 * 1024 * 1024) + b'}')
            for name, suffix in (("render_report.py", "html"), ("to_sarif.py", "sarif"), ("make_bundle.py", "zip")):
                output = work / f"prior.{suffix}"
                output.write_bytes(b"prior-state")
                result = subprocess.run([runtime, "-I", SCRIPT_DIR / name, source, output], capture_output=True, text=True)
                self.assertEqual(2, result.returncode, name)
                self.assertIn("too large", result.stderr.lower())
                self.assertEqual(b"prior-state", output.read_bytes())

    def test_bundle_rejects_symlink_and_oversized_include_without_replacing_output(self) -> None:
        runtime = "/opt/homebrew/bin/python3.11"
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            output = work / "bundle.zip"
            output.write_bytes(b"prior-state")
            target = work / "secret.txt"
            target.write_text("do not follow", encoding="utf-8")
            link = work / "link.txt"
            link.symlink_to(target)
            result = subprocess.run(
                [runtime, "-I", SCRIPT_DIR / "make_bundle.py", FIXTURE, output, "--include", link],
                capture_output=True, text=True,
            )
            self.assertEqual(2, result.returncode)
            self.assertIn("symlink", result.stderr.lower())
            self.assertEqual(b"prior-state", output.read_bytes())

            oversized = work / "oversized.bin"
            oversized.write_bytes(b"x" * (64 * 1024 * 1024 + 1))
            result = subprocess.run(
                [runtime, "-I", SCRIPT_DIR / "make_bundle.py", FIXTURE, output, "--include", oversized],
                capture_output=True, text=True,
            )
            self.assertEqual(2, result.returncode)
            self.assertIn("include data too large", result.stderr.lower())
            self.assertEqual(b"prior-state", output.read_bytes())

    def test_runtime_discovery_and_no_runtime_fallback_are_documented(self) -> None:
        contract = (SCRIPT_DIR.parent / "references/visual-html-report.md").read_text(encoding="utf-8").lower()
        for marker in ("python3", "python", "py -3", "3.11", "instruction-only fallback", "not_proven"):
            self.assertIn(marker, contract)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.skill_product.gauntlet.compare_agent_result import load_and_validate_oracle
from tests.skill_product.gauntlet.run_acceptance import atomic_final_result, validate_acceptance_result


ROOT = Path(__file__).resolve().parents[2]
GAUNTLET = ROOT / "tests/skill_product/gauntlet"
RUNNER = GAUNTLET / "run_acceptance.py"
EXPORTER = GAUNTLET / "redact_evidence.py"
SKILLS = ROOT / "plugins/shipworthy/skills"
APP = GAUNTLET / "app"
ORACLE, DEFECTS = load_and_validate_oracle(GAUNTLET / "oracle/surface-oracle.json", GAUNTLET / "oracle/expected-defects.json")


def complete_result(mode: str) -> dict:
    rows = []
    for item in ORACLE["items"]:
        if mode not in item["required_modes"]:
            continue
        row = {
            "semantic_key": item["semantic_key"], "kind": item["kind"],
            "status": item["allowed_dispositions_by_mode"][mode][0],
            "evidence_refs": [f"evidence/{item['id'].lower()}.json"],
        }
        if item["kind"] == "transition":
            row.update(before_state=item["before_state"], after_state=item["after_state"])
        rows.append(row)
    findings = [
        {"affected_semantic_keys": item["affected_semantic_keys"], "observed_effect_code": item["observed_effect_code"], "evidence_refs": [f"evidence/{item['id'].lower()}.json"]}
        for item in DEFECTS["defects"] if mode in item["required_modes"]
    ]
    summary = {kind: sum(row["kind"] == kind for row in rows) for kind in ("feature", "surface", "control", "transition")}
    return {"mode": mode, "closure_state": "closed_multi_source", "html_closure_state": "closed_multi_source", "summary": summary, "rows": rows, "findings": findings}


class AcceptanceHarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.outputs: list[Path] = []
        self.counter = 0

    def tearDown(self) -> None:
        for output in self.outputs:
            manifest = output / "run-manifest.json"
            if manifest.exists():
                subprocess.run(["python3", "-I", RUNNER, "cleanup", "--run-manifest", manifest], capture_output=True)
        self.temp.cleanup()

    def command(self, *args: object) -> subprocess.CompletedProcess:
        return subprocess.run(["python3", "-I", str(RUNNER), *(str(arg) for arg in args)], cwd=ROOT, capture_output=True, text=True)

    def prepare(self, mode: str, source: Path | None = None) -> tuple[Path, dict]:
        self.counter += 1
        output = self.root / f"{mode}-{self.counter}"
        args: list[object] = ["prepare", "--mode", mode, "--skills-source", SKILLS, "--output", output]
        if source is not None:
            args.extend(("--product-source", source))
        result = self.command(*args)
        self.assertEqual(0, result.returncode, result.stderr)
        self.outputs.append(output)
        manifest = json.loads((output / "run-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest, json.loads(result.stdout))
        return output, manifest

    def write_agent_evidence(self, output: Path, mode: str) -> Path:
        evidence = output / "agent-evidence"
        evidence.mkdir()
        report = complete_result(mode)
        (evidence / "report-input.json").write_text(json.dumps(report), encoding="utf-8")
        (evidence / "readiness-ledger.json").write_text(json.dumps({"path_frontier": report["rows"]}), encoding="utf-8")
        (evidence / "report.html").write_text('<html data-closure-state="closed_multi_source"><h1>Readiness</h1></html>', encoding="utf-8")
        (output / "run.log").write_text("agent completed\n", encoding="utf-8")
        return evidence

    def test_prepare_runtime_only_is_isolated_and_healthy(self) -> None:
        output, manifest = self.prepare("runtime-only")
        self.assertNotEqual(str(output), manifest["controller_root"])
        self.assertEqual(4, len(manifest["skill_paths"]))
        self.assertTrue(all(Path(path).name == "SKILL.md" for path in manifest["skill_paths"]))
        self.assertTrue(Path(manifest["workspace"]).is_dir())
        self.assertEqual([], list(Path(manifest["workspace"]).iterdir()))
        self.assertNotIn("product_source", manifest)
        self.assertTrue(manifest["base_url"].startswith("http://127.0.0.1:"))
        self.assertEqual(manifest["server_pid"], os.getpgid(manifest["server_pid"]))

    def test_prepare_enforces_mode_specific_product_source_and_sanitizes(self) -> None:
        bad_runtime = self.command("prepare", "--mode", "runtime-only", "--skills-source", SKILLS, "--output", self.root / "bad-runtime", "--product-source", APP)
        self.assertNotEqual(0, bad_runtime.returncode)
        bad_full = self.command("prepare", "--mode", "full-evidence", "--skills-source", SKILLS, "--output", self.root / "bad-full")
        self.assertNotEqual(0, bad_full.returncode)
        output, manifest = self.prepare("full-evidence", APP)
        copy = Path(manifest["product_copy"])
        self.assertTrue((copy / "product-docs/README.md").is_file())
        self.assertFalse(any(path.name == "__pycache__" for path in copy.rglob("*")))
        self.assertNotIn(str(APP), manifest["allowed_paths"])

    def test_finalize_completed_pass_is_atomic_and_cleans_controller(self) -> None:
        output, manifest = self.prepare("runtime-only")
        evidence = self.write_agent_evidence(output, "runtime-only")
        result = self.command("finalize", "--run-manifest", output / "run-manifest.json", "--native-dispatch-status", "completed", "--native-agent-id", "native-123", "--agent-output", evidence)
        self.assertEqual(0, result.returncode, result.stderr)
        final = json.loads((output / "acceptance-result.json").read_text(encoding="utf-8"))
        self.assertEqual("PASS", final["status"])
        self.assertEqual("native-123", final["native_agent_id"])
        self.assertFalse(Path(manifest["controller_root"]).exists())
        self.assertFalse((output / ".acceptance-result.json.tmp").exists())
        self.assertTrue((output / "comparison-packet.json").is_file())

    def test_dispatch_outcomes_map_to_not_proven_and_fail(self) -> None:
        for dispatch, expected_status, expected_code in (("unavailable", "NOT_PROVEN", 2), ("failed", "FAIL", 1), ("timeout", "FAIL", 1)):
            output, _ = self.prepare("runtime-only")
            evidence = output / "agent-evidence"
            evidence.mkdir()
            (output / "run.log").write_text(f"{dispatch}\n", encoding="utf-8")
            result = self.command("finalize", "--run-manifest", output / "run-manifest.json", "--native-dispatch-status", dispatch, "--native-agent-id", "native-x", "--agent-output", evidence, "--coordinator-diagnostic", dispatch)
            self.assertEqual(expected_code, result.returncode)
            final = json.loads((output / "acceptance-result.json").read_text(encoding="utf-8"))
            self.assertEqual(expected_status, final["status"])

    def test_cleanup_is_idempotent(self) -> None:
        output, manifest = self.prepare("runtime-only")
        first = self.command("cleanup", "--run-manifest", output / "run-manifest.json")
        second = self.command("cleanup", "--run-manifest", output / "run-manifest.json")
        self.assertEqual((0, 0), (first.returncode, second.returncode))
        self.assertFalse(Path(manifest["controller_root"]).exists())

    def test_invalid_draft_becomes_schema_valid_internal_fail(self) -> None:
        output = self.root / "atomic"
        output.mkdir()
        result = atomic_final_result(output, {"status": "PASS"})
        self.assertEqual("FAIL", result["status"])
        self.assertEqual("internal-invalid-result", result["failure_code"])
        validate_acceptance_result(result)
        self.assertEqual(result, json.loads((output / "acceptance-result.json").read_text(encoding="utf-8")))

    def test_exporter_redacts_copies_validates_and_never_mutates_source(self) -> None:
        output, _ = self.prepare("runtime-only")
        evidence = self.write_agent_evidence(output, "runtime-only")
        finalized = self.command("finalize", "--run-manifest", output / "run-manifest.json", "--native-dispatch-status", "completed", "--native-agent-id", "native-123", "--agent-output", evidence)
        self.assertEqual(0, finalized.returncode)
        source_digest = hashlib.sha256((output / "run.log").read_bytes()).hexdigest()
        destination = self.root / "durable"
        exported = subprocess.run(["python3", "-I", EXPORTER, "--run-manifest", output / "run-manifest.json", "--source", output, "--destination", destination, "--status", "PASS"], capture_output=True, text=True)
        self.assertEqual(0, exported.returncode, exported.stderr)
        packet = json.loads(exported.stdout)
        self.assertEqual(6, len(packet["files"]))
        self.assertEqual(source_digest, hashlib.sha256((output / "run.log").read_bytes()).hexdigest())
        self.assertNotIn(str(Path.home()), (destination / "run.log").read_text(encoding="utf-8"))
        self.assertEqual({"acceptance-result.json", "comparison-packet.json", "readiness-ledger.json", "report-input.json", "report.html", "run.log"}, {path.name for path in destination.iterdir()})

    def test_briefs_name_exact_skills_and_do_not_expose_oracle(self) -> None:
        expected = {
            "plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md",
            "plugins/shipworthy/skills/ship-deep-review/SKILL.md",
            "plugins/shipworthy/skills/ship-product-workflows/SKILL.md",
            "plugins/shipworthy/skills/ship-workflow-clarity/SKILL.md",
        }
        for name in ("runtime-only.md", "full-evidence.md"):
            text = (GAUNTLET / "prompts" / name).read_text(encoding="utf-8")
            self.assertTrue(expected.issubset(set(text.splitlines())))
            self.assertIn("Do not inspect", text)
            self.assertNotIn("surface-oracle.json", text)
            self.assertIn("canonical readiness ledger", text)
            self.assertIn("self-contained HTML", text)


if __name__ == "__main__":
    unittest.main()

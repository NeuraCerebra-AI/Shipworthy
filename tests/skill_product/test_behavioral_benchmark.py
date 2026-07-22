from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BENCHMARK = ROOT / "tests/skill_product/gauntlet/benchmark-v1.json"


class BehavioralBenchmarkTests(unittest.TestCase):
    def test_benchmark_v1_is_closed_and_matches_frozen_files(self) -> None:
        benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
        self.assertEqual("shipworthy-behavioral-benchmark-v1", benchmark["schema_version"])
        self.assertEqual("4651c8d1cd006230788d0d37f0e3fc312e5fbe48", benchmark["source_revision"])
        self.assertEqual(
            ["discovery", "execution", "defect_detection", "evidence_integrity"],
            benchmark["diagnostic_dimensions"],
        )
        self.assertEqual("categorical", benchmark["official_acceptance_gate"])
        self.assertNotIn("combined_score", benchmark)
        for relative, expected in benchmark["frozen_files"].items():
            frozen = subprocess.run(
                ["git", "show", f"{benchmark['source_revision']}:{relative}"],
                cwd=ROOT,
                capture_output=True,
                check=True,
            ).stdout
            actual = hashlib.sha256(frozen).hexdigest()
            self.assertEqual(expected, actual, relative)

    def test_historical_results_remain_fail_without_reinterpretation(self) -> None:
        benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
        self.assertEqual("FAIL", benchmark["historical_results"]["runtime_only"]["status"])
        self.assertEqual("FAIL", benchmark["historical_results"]["full_evidence"]["status"])
        self.assertFalse(benchmark["historical_results"]["behavioral_acceptance_claimed"])
        predecessor = (ROOT / "docs/phase0/evidence/gauntlet-post-fix-acceptance.md").read_text(encoding="utf-8")
        for mode in ("runtime_only", "full_evidence"):
            for field in ("acceptance_result_sha256", "comparison_packet_sha256"):
                digest = benchmark["historical_results"][mode][field]
                self.assertRegex(digest, r"^[0-9a-f]{64}$")
                self.assertIn(digest, predecessor)


if __name__ == "__main__":
    unittest.main()

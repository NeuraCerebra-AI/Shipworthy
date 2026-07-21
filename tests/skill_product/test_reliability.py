from __future__ import annotations

import unittest

from tests.skill_product.gauntlet.reliability import ReliabilityError, score_run, summarize_runs


def run_packet(identifier: str, discovery: int, *, total: int = 10, execution: int | None = None, defects: int = 2, blockers: int = 1, false_closure: bool = False, integrity: bool = True, false_positives: int = 0) -> dict:
    return {
        "run_id": identifier,
        "revision": "abc123",
        "mode": "runtime-only",
        "source_run_ids": [identifier],
        "discovery": {"found": discovery, "total": total},
        "execution": {"found": discovery if execution is None else execution, "total": total},
        "defects": {"found": defects, "total": 2, "release_blocking_found": blockers, "release_blocking_total": 1},
        "false_exhaustive_closure": false_closure,
        "artifact_integrity": integrity,
        "false_positive_count": false_positives,
        "valid_extra_count": 1,
        "duration_seconds": 100,
        "attempt_count": 20,
        "artifact_bytes": 5000,
    }


class ReliabilityScoringTests(unittest.TestCase):
    def test_per_run_dimensions_cost_and_classifications_remain_independent(self) -> None:
        result = score_run(run_packet("r1", 9, execution=8, defects=1, blockers=1, false_positives=2))
        self.assertEqual(.9, result["material_discovery_recall"])
        self.assertEqual(.8, result["execution_recall"])
        self.assertEqual(.5, result["defect_recall"])
        self.assertEqual(1.0, result["release_blocking_defect_recall"])
        self.assertEqual(2, result["false_positive_count"])
        self.assertEqual(1, result["valid_extra_count"])
        self.assertEqual({"duration_seconds": 100.0, "attempt_count": 20, "artifact_bytes": 5000}, result["cost"])
        self.assertNotIn("combined_score", result)

    def test_summary_reports_median_worst_rates_and_release_gate(self) -> None:
        runs = [run_packet(f"r{index}", discovery) for index, discovery in enumerate((10, 9, 9, 8, 10), 1)]
        summary = summarize_runs(runs)
        self.assertEqual(.9, summary["material_discovery_recall"]["median"])
        self.assertEqual(.8, summary["material_discovery_recall"]["worst"])
        self.assertEqual(0.0, summary["false_exhaustive_closure_rate"])
        self.assertEqual(1.0, summary["artifact_integrity_rate"])
        self.assertEqual(0.0, summary["false_positive_rate"])
        self.assertEqual(1.0, summary["release_blocking_defect_recall"])
        self.assertEqual("PASS", summary["release_gate"])
        self.assertEqual(["r1", "r2", "r3", "r4", "r5"], [run["run_id"] for run in summary["runs"]])

    def test_threshold_failures_are_categorical_not_averaged_away(self) -> None:
        runs = [run_packet(f"r{index}", 10) for index in range(1, 6)]
        runs[2]["discovery"]["found"] = 7
        runs[3]["false_exhaustive_closure"] = True
        runs[4]["artifact_integrity"] = False
        runs[1]["defects"]["release_blocking_found"] = 0
        summary = summarize_runs(runs)
        self.assertEqual("FAIL", summary["release_gate"])
        self.assertIn("discovery-worst-below-0.80", summary["failed_gates"])
        self.assertIn("false-exhaustive-closure", summary["failed_gates"])
        self.assertIn("artifact-integrity-not-5-of-5", summary["failed_gates"])
        self.assertIn("release-blocker-missed", summary["failed_gates"])

    def test_requires_five_same_revision_independent_runs_and_rejects_aggregation(self) -> None:
        with self.assertRaisesRegex(ReliabilityError, "exactly five"):
            summarize_runs([run_packet("r1", 10)])
        runs = [run_packet(f"r{index}", 10) for index in range(1, 6)]
        runs[1]["source_run_ids"] = ["r1", "r2"]
        with self.assertRaisesRegex(ReliabilityError, "aggregation"):
            summarize_runs(runs)
        runs = [run_packet(f"r{index}", 10) for index in range(1, 6)]
        runs[4]["revision"] = "different"
        with self.assertRaisesRegex(ReliabilityError, "same revision"):
            summarize_runs(runs)


if __name__ == "__main__":
    unittest.main()

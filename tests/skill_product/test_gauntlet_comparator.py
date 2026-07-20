from __future__ import annotations

import copy
import unittest
from pathlib import Path

from tests.skill_product.gauntlet.compare_agent_result import compare_frontier, load_and_validate_oracle


ROOT = Path(__file__).resolve().parents[2]
ORACLE_PATH = ROOT / "tests/skill_product/gauntlet/oracle/surface-oracle.json"
DEFECTS_PATH = ROOT / "tests/skill_product/gauntlet/oracle/expected-defects.json"


class GauntletComparatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.oracle, cls.defects = load_and_validate_oracle(ORACLE_PATH, DEFECTS_PATH)

    def complete_result(self, mode: str = "runtime-only") -> dict:
        rows = []
        for item in self.oracle["items"]:
            if mode not in item["required_modes"] or item.get("decoy_policy") == "negative_control":
                continue
            status = item["allowed_dispositions_by_mode"][mode][0]
            row = {
                "semantic_key": item["semantic_key"],
                "kind": item["kind"],
                "status": status,
                "evidence_refs": [f"evidence/{item['id'].lower()}.json"],
            }
            if item["kind"] == "transition":
                row.update(before_state=item["before_state"], after_state=item["after_state"])
            rows.append(row)
        findings = [
            {
                "affected_semantic_keys": defect["affected_semantic_keys"],
                "observed_effect_code": defect["observed_effect_code"],
                "evidence_refs": [f"evidence/{defect['id'].lower()}.json"],
            }
            for defect in self.defects["defects"]
            if mode in defect["required_modes"]
        ]
        counts = {kind: sum(row["kind"] == kind for row in rows) for kind in ("feature", "surface", "control", "transition")}
        return {
            "mode": mode,
            "closure_state": "closed_multi_source",
            "html_closure_state": "closed_multi_source",
            "summary": counts,
            "rows": rows,
            "findings": findings,
        }

    def compare(self, result: dict) -> dict:
        return compare_frontier(result, self.oracle, self.defects, result["mode"])

    def test_complete_supported_frontier_passes_and_source_only_is_mode_filtered(self) -> None:
        result = self.complete_result("runtime-only")
        packet = self.compare(result)
        self.assertEqual("PASS", packet["status"], packet)
        source_only = {item["semantic_key"] for item in self.oracle["items"] if item["required_modes"] == ["full-evidence"]}
        self.assertTrue(source_only)
        self.assertTrue(source_only.isdisjoint({row["semantic_key"] for row in result["rows"]}))

    def test_material_miss_invalid_disposition_and_unproved_covered_control_fail(self) -> None:
        missing = self.complete_result()
        missing["rows"].pop(0)
        self.assertEqual("FAIL", self.compare(missing)["status"])

        invalid = self.complete_result()
        invalid["rows"][0]["status"] = "maybe"
        self.assertEqual("FAIL", self.compare(invalid)["status"])

        unproved = self.complete_result()
        covered = next(row for row in unproved["rows"] if row["kind"] == "control" and row["status"] == "covered")
        covered["evidence_refs"] = []
        self.assertEqual("FAIL", self.compare(unproved)["status"])

    def test_transition_requires_before_and_after_evidence(self) -> None:
        result = self.complete_result()
        transition = next(row for row in result["rows"] if row["kind"] == "transition")
        transition.pop("after_state")
        packet = self.compare(result)
        self.assertEqual("FAIL", packet["status"])
        self.assertTrue(any("before/after" in reason for reason in packet["reasons"]))

    def test_duplicates_count_drift_and_html_json_contradiction_fail(self) -> None:
        duplicate = self.complete_result()
        duplicate["rows"].append(copy.deepcopy(duplicate["rows"][0]))
        self.assertEqual("FAIL", self.compare(duplicate)["status"])

        drift = self.complete_result()
        drift["summary"]["control"] += 1
        self.assertEqual("FAIL", self.compare(drift)["status"])

        contradiction = self.complete_result()
        contradiction["html_closure_state"] = "incomplete"
        self.assertEqual("FAIL", self.compare(contradiction)["status"])

    def test_unexpected_row_requires_review(self) -> None:
        result = self.complete_result()
        result["rows"].append(
            {"semantic_key": "control:surface:/ghost:normal:member:desktop:launch:button:ghost", "kind": "control", "status": "covered", "evidence_refs": ["evidence/ghost.json"]}
        )
        result["summary"]["control"] += 1
        packet = self.compare(result)
        self.assertEqual("REVIEW_REQUIRED", packet["status"])
        self.assertEqual(1, len(packet["unexpected_rows"]))

    def test_structural_intents_and_explicit_nonmaterial_rows_do_not_require_review(self) -> None:
        result = self.complete_result()
        result["rows"].extend(
            [
                {"semantic_key": "intent:member:manage-projects", "kind": "intent", "status": "covered", "material": True, "evidence_refs": ["evidence/intent.json"]},
                {"semantic_key": "control:surface:/projects:normal:member:desktop:help:link:supporting", "kind": "control", "status": "covered", "material": False, "evidence_refs": ["evidence/help.json"]},
            ]
        )
        result["summary"] = {
            kind: sum(row["kind"] == kind for row in result["rows"])
            for kind in ("feature", "surface", "control", "transition")
        }
        packet = self.compare(result)
        self.assertEqual("PASS", packet["status"], packet)
        self.assertEqual([], packet["unexpected_rows"])

    def test_unexpected_finding_requires_review(self) -> None:
        result = self.complete_result()
        result["findings"].append(
            {
                "affected_semantic_keys": ["surface:/unexpected"],
                "observed_effect_code": "unexpected-material-effect",
                "evidence_refs": ["evidence/unexpected.json"],
            }
        )
        packet = self.compare(result)
        self.assertEqual("REVIEW_REQUIRED", packet["status"])
        self.assertEqual(1, len(packet["unexpected_findings"]))

    def test_separate_incomplete_runs_are_not_aggregated(self) -> None:
        first = self.complete_result()
        second = self.complete_result()
        midpoint = len(first["rows"]) // 2
        first["rows"] = first["rows"][:midpoint]
        second["rows"] = second["rows"][midpoint:]
        for result in (first, second):
            result["summary"] = {kind: sum(row["kind"] == kind for row in result["rows"]) for kind in ("feature", "surface", "control", "transition")}
            self.assertEqual("FAIL", self.compare(result)["status"])

    def test_defect_requires_lineage_and_effect_match(self) -> None:
        result = self.complete_result()
        result["findings"][0]["observed_effect_code"] = "generic-error"
        packet = self.compare(result)
        self.assertEqual("FAIL", packet["status"])
        self.assertTrue(any("defect" in reason for reason in packet["reasons"]))


if __name__ == "__main__":
    unittest.main()

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

    def test_non_defect_report_rows_do_not_become_unexpected_defects(self) -> None:
        result = self.complete_result()
        result["findings"].extend(
            [
                {"action": action, "affected_semantic_keys": ["surface:/support"], "observed_effect_code": "support", "evidence_refs": ["evidence/support.json"]}
                for action in ("Keep", "Skip", "Prove")
            ]
        )
        self.assertEqual("PASS", self.compare(result)["status"])

    def test_accepted_identity_alias_matches_without_private_vocabulary(self) -> None:
        result = self.complete_result()
        expected = "control:surface:/dashboard:normal:member:desktop:command-palette:keyboard:open"
        row = next(item for item in result["rows"] if item["semantic_key"] == expected)
        row["semantic_key"] = "control:surface:/dashboard:normal:member:desktop:quick-actions:keyboard:open"
        packet = self.compare(result)
        self.assertEqual("PASS", packet["status"], packet)

    def test_equivalent_behavioral_keys_match_without_private_state_vocabulary(self) -> None:
        result = self.complete_result()
        replacements = {
            "control:surface:/projects:editing:member:desktop:save:button:persist":
                "control:surface:/projects:normal:member:desktop:save:button:persist",
            "transition:draft:control:surface:/projects:draft:member:desktop:publish:button:publish:published":
                "transition:draft:control:surface:/projects:normal:member:desktop:publish:button:publish:published-without-visible-state",
            "control:surface:/projects:editing:member:desktop:archive:button:disabled":
                "control:surface:/projects:normal:member:desktop:archive:button:disabled",
        }
        for row in result["rows"]:
            if row["semantic_key"] in replacements:
                row["semantic_key"] = replacements[row["semantic_key"]]
        packet = self.compare(result)
        self.assertEqual("PASS", packet["status"], packet)

    def test_explicit_canonical_alternatives_match_the_same_observed_behavior(self) -> None:
        result = self.complete_result()
        replacements = {
            item["semantic_key"]: item["accepted_semantic_keys"][0]
            for item in self.oracle["items"]
            if item.get("accepted_semantic_keys")
        }
        self.assertTrue(replacements)
        for row in result["rows"]:
            if row["semantic_key"] in replacements:
                row["semantic_key"] = replacements[row["semantic_key"]]
        packet = self.compare(result)
        self.assertEqual("PASS", packet["status"], packet)

    def test_known_fixture_route_inventory_is_classified_but_unknown_route_is_reviewed(self) -> None:
        result = self.complete_result()
        result["rows"].append(
            {
                "semantic_key": "control:surface:/projects:normal:member:desktop:help:link:open-help",
                "kind": "control",
                "status": "covered",
                "material": True,
                "evidence_refs": ["evidence/help.json"],
            }
        )
        result["summary"]["control"] += 1
        self.assertEqual("PASS", self.compare(result)["status"])

        result["rows"][-1]["semantic_key"] = "control:surface:/ghost:normal:member:desktop:help:link:open-help"
        packet = self.compare(result)
        self.assertEqual("REVIEW_REQUIRED", packet["status"])
        self.assertEqual(1, len(packet["unexpected_rows"]))

    def test_arbitrary_not_found_probe_is_classified_as_fixture_support(self) -> None:
        result = self.complete_result()
        result["rows"].append(
            {
                "semantic_key": "surface:/definitely-absent:not-found:member:desktop",
                "kind": "surface",
                "status": "covered",
                "material": True,
                "evidence_refs": ["evidence/not-found.json"],
            }
        )
        result["summary"]["surface"] += 1
        self.assertEqual("PASS", self.compare(result)["status"])

    def test_known_fixture_feature_inventory_is_classified(self) -> None:
        result = self.complete_result()
        result["rows"].append(
            {
                "semantic_key": "feature:projects",
                "kind": "feature",
                "status": "covered",
                "material": True,
                "evidence_refs": ["evidence/projects.json"],
            }
        )
        result["summary"]["feature"] += 1
        self.assertEqual("PASS", self.compare(result)["status"])

    def test_observed_supporting_feature_names_are_classified(self) -> None:
        result = self.complete_result()
        for key in ("feature:project-import-export", "feature:profile", "feature:upgrade", "feature:navigation", "feature:project-lifecycle", "feature:team-management", "feature:data-portability"):
            result["rows"].append(
                {
                    "semantic_key": key,
                    "kind": "feature",
                    "status": "covered",
                    "material": True,
                    "evidence_refs": ["evidence/support.json"],
                }
            )
        result["summary"]["feature"] += 7
        self.assertEqual("PASS", self.compare(result)["status"])

    def test_supported_not_found_probe_route_name_is_classified(self) -> None:
        result = self.complete_result()
        for kind, key in (
            ("surface", "surface:/definitely-not-a-real-route:normal:member:desktop"),
            ("control", "control:surface:/definitely-not-a-real-route:normal:member:desktop:the-dashboard:link:navigate"),
        ):
            result["rows"].append({"semantic_key": key, "kind": kind, "status": "covered", "material": True, "evidence_refs": ["evidence/not-found.json"]})
            result["summary"][kind] += 1
        self.assertEqual("PASS", self.compare(result)["status"])

    def test_unavailable_feature_may_be_recorded_missing(self) -> None:
        result = self.complete_result()
        row = next(item for item in result["rows"] if item["semantic_key"] == "feature:advanced-analytics")
        row["status"] = "missing"
        self.assertEqual("PASS", self.compare(result)["status"])

    def test_observed_publish_semantics_and_expected_effect_vocabulary_match(self) -> None:
        result = self.complete_result()
        publish = "transition:draft:control:surface:/projects:draft:member:desktop:publish:button:publish:published"
        actual_publish = "transition:draft:control:surface:/projects:editing:member:desktop:publish:button:persist:published"
        next(row for row in result["rows"] if row["semantic_key"] == publish)["semantic_key"] = actual_publish
        replacements = {
            "false-affordance-noninteractive": "affordance_without_activation",
            "unexplained-disabled-control": "disabled_without_recovery",
            "duplicate-save-behavior-ambiguity": "ambiguous_duplicate_save_controls",
        }
        for finding in result["findings"]:
            finding["observed_effect_code"] = replacements.get(finding["observed_effect_code"], finding["observed_effect_code"])
        packet = self.compare(result)
        self.assertEqual("PASS", packet["status"], packet)

    def test_matching_prefers_an_allowed_direct_row_over_a_sampled_alias(self) -> None:
        result = self.complete_result()
        key = "control:surface:/projects:editing:member:desktop:save:button:persist"
        sampled = next(row for row in result["rows"] if row["semantic_key"] == key)
        sampled["status"] = "sampled_with_justification"
        direct = copy.deepcopy(sampled)
        direct["semantic_key"] = "control:surface:/projects:normal:admin:desktop:save:button:persist"
        direct["status"] = "covered"
        result["rows"].append(direct)
        result["summary"]["control"] += 1

        oracle = copy.deepcopy(self.oracle)
        item = next(item for item in oracle["items"] if item["semantic_key"] == key)
        item.setdefault("accepted_semantic_keys", []).append(direct["semantic_key"])
        packet = compare_frontier(result, oracle, self.defects, result["mode"])
        self.assertEqual("PASS", packet["status"], packet)

    def test_explicit_role_alternatives_and_observed_effect_aliases_match(self) -> None:
        result = self.complete_result()
        replacements = {
            "control:surface:/projects:editing:member:desktop:save:button:persist":
                "control:surface:/projects:normal:admin:desktop:save:button:persist",
            "transition:editing:control:surface:/projects:editing:member:desktop:save:button:persist:not-persisted":
                "transition:editing:control:surface:/projects:normal:admin:desktop:save:button:persist:not-persisted",
            "transition:apparently-saved:control:surface:/projects:editing:member:desktop:reload:browser:verify:lost":
                "transition:apparently-saved:control:surface:/projects:normal:admin:desktop:reload:browser:verify:lost",
        }
        for row in result["rows"]:
            if row["semantic_key"] in replacements:
                row["semantic_key"] = replacements[row["semantic_key"]]
        for finding in result["findings"]:
            finding["affected_semantic_keys"] = [replacements.get(key, key) for key in finding["affected_semantic_keys"]]
            if finding["observed_effect_code"] == "false-affordance-noninteractive":
                finding["observed_effect_code"] = "actionable-looking-noninteractive"
            elif finding["observed_effect_code"] == "duplicate-save-behavior-ambiguity":
                finding["observed_effect_code"] = "duplicate-name-divergent-behavior"
        packet = self.compare(result)
        self.assertEqual("PASS", packet["status"], packet)

    def test_exact_browser_width_suffixes_match_canonical_viewport_classes(self) -> None:
        result = self.complete_result()
        for row in result["rows"]:
            row["semantic_key"] = row["semantic_key"].replace(":desktop:", ":desktop-1200:").replace(":mobile:", ":mobile-390:")
        for finding in result["findings"]:
            finding["affected_semantic_keys"] = [
                key.replace(":desktop:", ":desktop-1200:").replace(":mobile:", ":mobile-390:")
                for key in finding["affected_semantic_keys"]
            ]
        packet = self.compare(result)
        self.assertEqual("PASS", packet["status"], packet)

    def test_equivalent_observed_effect_codes_remain_lineage_bound(self) -> None:
        result = self.complete_result()
        replacements = {
            "success-without-persistence": "edit-success-without-persistence",
            "false-affordance-noninteractive": "upgrade-apparent-action-no-navigation",
            "unexplained-disabled-control": "archive-control-unexplained-disabled",
        }
        for finding in result["findings"]:
            finding["observed_effect_code"] = replacements.get(finding["observed_effect_code"], finding["observed_effect_code"])
        packet = self.compare(result)
        self.assertEqual("PASS", packet["status"], packet)

    def test_observed_reload_and_duplicate_label_vocabulary_matches_expected_defects(self) -> None:
        result = self.complete_result()
        save_key = "control:surface:/projects:editing:member:desktop:save:button:persist"
        save_actual = "control:surface:/projects:normal:member:desktop:save:button:show-saved-success-without-persistence"
        misleading_key = "transition:editing:control:surface:/projects:editing:member:desktop:save:button:persist:not-persisted"
        misleading_actual = "transition:editing:control:surface:/projects:normal:member:desktop:save:button:show-saved-success-without-persistence:saved-success-message"
        reload_key = "transition:apparently-saved:control:surface:/projects:editing:member:desktop:reload:browser:verify:lost"
        reload_actual = "transition:saved-success-message:control:surface:/projects:editing:member:desktop:reload-page:keyboard-shortcut:verify-edit-persistence:not-persisted"
        replacements = {save_key: save_actual, misleading_key: misleading_actual, reload_key: reload_actual}
        for row in result["rows"]:
            row["semantic_key"] = replacements.get(row["semantic_key"], row["semantic_key"])
        for finding in result["findings"]:
            finding["affected_semantic_keys"] = [replacements.get(key, key) for key in finding["affected_semantic_keys"]]
            if finding["observed_effect_code"] == "duplicate-save-behavior-ambiguity":
                finding["observed_effect_code"] = "duplicate-labels-ambiguous-action"
        packet = self.compare(result)
        self.assertEqual("PASS", packet["status"], packet)

    def test_false_affordance_finding_may_use_observed_mobile_variant(self) -> None:
        result = self.complete_result()
        finding = next(item for item in result["findings"] if item["observed_effect_code"] == "false-affordance-noninteractive")
        finding["affected_semantic_keys"] = ["surface:/dashboard:upgrade-card:member:mobile"]
        packet = self.compare(result)
        self.assertEqual("PASS", packet["status"], packet)

    def test_observed_false_affordance_may_be_missing_or_blocked(self) -> None:
        for status in ("missing", "blocked"):
            result = self.complete_result()
            row = next(item for item in result["rows"] if item["semantic_key"] == "surface:/dashboard:upgrade-card:member:desktop")
            row["status"] = status
            self.assertEqual("PASS", self.compare(result)["status"])

    def test_defect_lineage_accepts_matched_canonical_alternative_and_effect_alias(self) -> None:
        result = self.complete_result()
        expected = "transition:editing:control:surface:/projects:editing:member:desktop:save:button:persist:not-persisted"
        actual = "transition:alpha-edited:control:surface:/projects:editing:member:desktop:save:button:persist:not-persisted"
        row = next(item for item in result["rows"] if item["semantic_key"] == expected)
        row["semantic_key"] = actual
        finding = next(item for item in result["findings"] if expected in item["affected_semantic_keys"])
        finding["affected_semantic_keys"] = [actual]
        finding["observed_effect_code"] = "save_false_success_not_persisted"
        packet = self.compare(result)
        self.assertEqual("PASS", packet["status"], packet)

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

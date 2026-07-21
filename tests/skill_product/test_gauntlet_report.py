from __future__ import annotations

import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/scripts"
FIXTURE = ROOT / "tests/skill_product/fixtures/gauntlet-report-input.json"
SCHEMA = ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/report-input.schema.json"
sys.path.insert(0, str(SCRIPT_DIR))

from render_report import render, summarize_frontier  # noqa: E402


class GauntletReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_fixture_is_valid_report_input(self) -> None:
        from tests.skill_product.support.schema_subset import validate

        validate(self.fixture, SCHEMA)

    def test_summary_reconciles_exact_counts_roles_and_families(self) -> None:
        frontier = self.fixture["source_ledger"]["path_frontier"]
        summary = summarize_frontier(frontier)
        self.assertEqual({"intent": 1, "feature": 1, "surface": 1, "control": 2, "transition": 1}, summary["counts"])
        self.assertEqual(["admin", "member"], summary["roles"])
        self.assertEqual(["runtime_human_interaction", "runtime_structural_inventory"], summary["method_families"])
        self.assertEqual((1, 2, 50), summary["control_attempts"])

    def test_summary_rejects_caller_count_drift(self) -> None:
        frontier = deepcopy(self.fixture["source_ledger"]["path_frontier"])
        frontier["summary"]["control"] = 99
        with self.assertRaisesRegex(ValueError, "summary does not reconcile"):
            summarize_frontier(frontier)

    def test_product_coverage_is_human_readable_and_after_actions(self) -> None:
        report = render(self.fixture)
        self.assertLess(report.index("<h2>Fix Next</h2>"), report.index("<h2>Product Coverage</h2>"))
        for text in (
            "Closed Multi Source",
            "All material rows reconciled",
            "member",
            "admin",
            "Runtime Human Interaction",
            "Runtime Structural Inventory",
            "Project Management",
        ):
            self.assertIn(text, report)
        for metric in ("<b>1</b> feature", "<b>1</b> surface", "<b>2</b> controls", "<b>1</b> transition"):
            self.assertIn(metric, report)
        self.assertIn("<strong>1 of 2</strong>&nbsp; material controls attempted (50%)", report)
        self.assertIn('data-closure-state="closed_multi_source"', report)
        self.assertNotIn("<h2>Coverage</h2>", report)

    def test_coverage_confidence_summary_is_early_plain_language_and_bounded(self) -> None:
        report = render(self.fixture)
        summary = report.index("<h2>Coverage Confidence</h2>")
        first_finding = report.index("<h2>Fix Next</h2>")
        product_detail = report.index("<h2>Product Coverage</h2>")
        self.assertLess(summary, first_finding)
        self.assertLess(first_finding, product_detail)
        for text in (
            "What was tested",
            "5 of 6 material frontier items were covered by evidence.",
            "What was not tested",
            "1 avoided for safety",
            "Roles: admin, member",
            "States: editing, normal",
            "Viewports: desktop, mobile",
            "Why testing stopped",
            "All material rows reconciled; two independent discovery passes reached zero yield.",
            "Closure achieved",
            "Important proof limits",
            "1 avoided",
            "0 inferred",
            "0 blocked",
            "0 NOT_PROVEN",
        ):
            self.assertIn(text, report)
        self.assertNotIn("PF-C2", report[summary:first_finding])

    def test_coverage_confidence_summary_matches_incomplete_closure_and_escapes_text(self) -> None:
        candidate = deepcopy(self.fixture)
        frontier = candidate["source_ledger"]["path_frontier"]
        frontier["closure_state"] = "incomplete"
        frontier["closure_reason"] = '<img src=x onerror="alert(1)">'
        frontier["rows"][0]["status"] = "inferred"
        report = render(candidate)
        self.assertIn("Closure not achieved", report)
        self.assertIn("1 inferred", report)
        self.assertIn("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;", report)
        self.assertNotIn('<img src=x onerror="alert(1)">', report)

    def test_product_coverage_uses_five_bounded_details_and_manifest_link(self) -> None:
        report = render(self.fixture)
        for label in (
            "Control evidence",
            "Role / state / device coverage",
            "Blocked / avoided actions",
            "Discovery reconciliation",
            "Frontier manifest",
        ):
            self.assertIn(f"<summary>{label}</summary>", report)
        self.assertIn('href="evidence/path-frontier.json"', report)
        self.assertNotIn('"normalization_version": "shipworthy-semantic-v1"', report)

    def test_default_has_no_javascript_and_escapes_frontier_text(self) -> None:
        hostile = deepcopy(self.fixture)
        hostile["source_ledger"]["path_frontier"]["closure_reason"] = "<script>alert(1)</script>"
        report = render(hostile)
        self.assertNotIn("<script", report.lower())
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", report)

    def test_print_styles_keep_title_and_confidence_summary_readable(self) -> None:
        report = render(self.fixture)
        self.assertIn("h1.title,.confidence-grid b,.confidence-summary .section-head h2{color:#111}", report)
        self.assertIn(".confidence-summary,.read-key,.stat-chip{background:#fff", report)
        self.assertIn(".confidence-grid span,.read-key{color:#4A5568}", report)

    def test_legacy_input_has_bounded_not_recorded_message(self) -> None:
        report = render({"findings": [{"section": "passed_keep", "title": "Legacy result"}]})
        self.assertIn("Product coverage not recorded for this run.", report)

    def test_only_canonical_closure_vocabulary_is_rendered(self) -> None:
        for closure in ("closed_multi_source", "incomplete", "single_source", "blocked", "static_only"):
            candidate = deepcopy(self.fixture)
            candidate["source_ledger"]["path_frontier"]["closure_state"] = closure
            report = render(candidate)
            self.assertIn(f'data-closure-state="{closure}"', report)
        candidate = deepcopy(self.fixture)
        candidate["source_ledger"]["path_frontier"]["closure_state"] = "complete"
        with self.assertRaisesRegex(ValueError, "closure_state"):
            render(candidate)

    def test_report_references_preserve_human_readable_coverage_contract(self) -> None:
        visual = (ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/references/visual-html-report.md").read_text(encoding="utf-8")
        contract = (ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/references/final-report-contract.md").read_text(encoding="utf-8")
        for phrase in (
            "Coverage Confidence",
            "what was tested",
            "what was not tested",
            "why testing stopped",
            "important proof limits",
            "Product Coverage",
            "Control evidence",
            "Role / state / device coverage",
            "Blocked / avoided actions",
            "Discovery reconciliation",
            "Frontier manifest",
        ):
            self.assertIn(phrase, visual)
        self.assertIn("after the action-first finding sections", visual)
        self.assertIn("near the beginning", visual)
        self.assertIn('data-closure-state="<exact canonical closure_state>"', visual)
        self.assertIn("exact denominator", contract)
        self.assertIn("roles, states, and viewports", contract)
        self.assertIn("caller totals must reconcile exactly with canonical rows", contract)


if __name__ == "__main__":
    unittest.main()

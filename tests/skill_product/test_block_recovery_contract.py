from __future__ import annotations

import unittest
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "plugins/shipworthy/skills"
ORCHESTRATOR = SKILLS / "ship-readiness-orchestrator"
sys.path.insert(0, str(ORCHESTRATOR / "scripts"))

from render_report import coverage_confidence_html, recovery_projection  # noqa: E402


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(document: str, heading: str, next_heading: str | None = None) -> str:
    start = document.index(heading)
    end = document.index(next_heading, start) if next_heading else len(document)
    return document[start:end]


class BlockRecoveryWordingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = read(ORCHESTRATOR / "SKILL.md")
        cls.routing = read(ORCHESTRATOR / "references/browser-evidence-routing.md")
        cls.lanes = read(ORCHESTRATOR / "references/lane-prompts.md")
        cls.final_report = read(ORCHESTRATOR / "references/final-report-contract.md")
        cls.ledger_contract = read(
            ORCHESTRATOR / "references/ledger-validation-contract.md"
        )
        cls.deep_review = read(
            SKILLS / "ship-deep-review/references/wave-protocol.md"
        )
        cls.product_agents = read(
            SKILLS
            / "ship-product-workflows/references/agent-and-wave-orchestration.md"
        )
        cls.clarity_agents = read(
            SKILLS
            / "ship-workflow-clarity/references/agent-and-tool-orchestration.md"
        )

    def test_authorization_question_is_a_visible_completion_contract(self) -> None:
        goal_gate = section(
            self.skill,
            "## Goal Mode Persistence Gate",
            "## Completion State Gate",
        )
        for phrase in (
            "every required wave",
            "verifier gate",
            "applicable safe alternative",
            "final HTML report",
            "will not be marked complete",
            "what remains unfinished",
        ):
            self.assertIn(phrase, goal_gate)
        self.assertEqual(1, goal_gate.count("> Shipworthy full blast"))
        self.assertIn(
            "Recommended: reply yes to authorize persistent goal mode and parallel subagents "
            "for this Shipworthy run. If authorized, I will complete every required wave",
            goal_gate,
        )
        self.assertNotIn(
            'use the combined wording: "Shipworthy full blast',
            self.lanes,
        )

    def test_persistent_goal_repeats_recovery_and_resumption_contract(self) -> None:
        goal_gate = section(
            self.skill,
            "## Goal Mode Persistence Gate",
            "## Completion State Gate",
        )
        for phrase in (
            "goal objective",
            "resume unfinished waves",
            "canonical recovery",
            "reread the active goal",
            "orchestration checkpoint",
        ):
            self.assertIn(phrase, goal_gate)

    def test_canonical_recovery_ladder_is_bounded_and_uses_alternatives(self) -> None:
        for phrase in (
            "one transient retry",
            "independent Playwright",
            "Chrome",
            "Computer Use",
            "reassign",
            "sequential",
            "supporting evidence",
            "inventory refresh",
            "exhausted",
            "resume the unfinished wave",
        ):
            self.assertIn(phrase, self.routing)

    def test_verifier_recovery_cannot_be_controller_self_approval(self) -> None:
        verifier = section(self.lanes, "## Independent Verifier")
        for phrase in (
            "fresh independent verifier",
            "controller self-verification",
            "verifier debt",
            "recovery",
        ):
            self.assertIn(phrase, verifier)

    def test_standalone_browser_prompts_return_recovery_results(self) -> None:
        for document in (
            self.deep_review,
            self.product_agents,
            self.clarity_agents,
        ):
            self.assertIn("independent Playwright", document)
            self.assertIn("recovery", document)
            self.assertIn("resume", document)

    def test_report_contract_keeps_recovery_human_readable(self) -> None:
        combined = self.final_report + self.ledger_contract
        for phrase in (
            "recovery_status",
            "recovery_attempts",
            "recovery_receipt",
            "In progress",
            "User stopped",
            "NOT_PROVEN",
            "<details>",
        ):
            self.assertIn(phrase, combined)


class BlockRecoveryBehaviorTests(unittest.TestCase):
    def attempt(self, status: str, **overrides: object) -> dict:
        value = {
            "recovery_id": "REC-1",
            "status": status,
            "failed_binding_id": "native-1",
            "method_family": "computer_use",
            "binding_id": "computer-use-1",
            "authorized": True,
            "available": True,
            "applicable": True,
            "safe": True,
            "attempt_count": 1,
            "result": "recovered" if status == "succeeded" else "failed",
            "continuity_before_attempt": True,
            "continuity_before_resumption": status == "succeeded",
            "resumed_path_keys": ["control:save"] if status == "succeeded" else [],
            "remaining_debt_ids": [] if status == "succeeded" else ["DEBT-1"],
            "evidence_refs": ["evidence/recovery.json"],
            "cleanup_result": "safe cleanup attempted",
            "transient_retry_performed": True,
            "path_outcomes": [{"semantic_key": "control:save", "status": status}],
            "inventory_refresh": status == "blocked",
            "new_available_method_ids": [],
            "controller_id": "controller-1",
            "verifier_id": "verifier-2",
            "verifier_debt": False,
            "driven_semantic_keys": [],
            "assertion_ids": [],
            "assertion_evidence_refs": [],
            "independence_debt_ids": [],
        }
        value.update(overrides)
        return value

    def test_failed_candidate_does_not_block_a_later_recovery(self) -> None:
        attempts = [
            self.attempt(
                "active",
                method_family="independent_playwright",
                binding_id="pw-1",
                available=False,
                attempt_count=0,
                result="unavailable",
                remaining_debt_ids=["DEBT-1"],
            ),
            self.attempt("succeeded"),
        ]
        projection = recovery_projection("succeeded", attempts)
        self.assertEqual("succeeded", projection["status"])
        self.assertEqual(1, projection["recovered_paths"])

    def test_unattempted_applicable_method_keeps_recovery_active(self) -> None:
        attempts = [
            self.attempt(
                "active",
                method_family="chrome",
                binding_id="chrome-2",
                attempt_count=0,
                result="not_attempted",
            )
        ]
        with self.assertRaisesRegex(ValueError, "must remain active"):
            recovery_projection("blocked", attempts)

    def test_same_binding_and_supporting_evidence_cannot_recover_frontend(self) -> None:
        with self.assertRaisesRegex(ValueError, "independent binding"):
            recovery_projection(
                "succeeded",
                [self.attempt("succeeded", binding_id="native-1")],
            )
        with self.assertRaisesRegex(ValueError, "supporting evidence"):
            recovery_projection(
                "succeeded",
                [
                    self.attempt(
                        "succeeded",
                        method_family="supporting_evidence",
                        binding_id="logs-1",
                    )
                ],
            )

    def test_recovery_requires_continuity_and_resumed_paths(self) -> None:
        with self.assertRaisesRegex(ValueError, "continuity"):
            recovery_projection(
                "succeeded",
                [self.attempt("succeeded", continuity_before_resumption=False)],
            )
        with self.assertRaisesRegex(ValueError, "resumed paths"):
            recovery_projection(
                "succeeded",
                [self.attempt("succeeded", resumed_path_keys=[])],
            )

    def test_recovery_requires_fresh_verifier_and_homogeneous_paths(self) -> None:
        with self.assertRaisesRegex(ValueError, "fresh independent verifier"):
            recovery_projection(
                "succeeded",
                [self.attempt("succeeded", verifier_id="controller-1")],
            )
        with self.assertRaisesRegex(ValueError, "heterogeneous"):
            recovery_projection(
                "succeeded",
                [
                    self.attempt(
                        "succeeded",
                        path_outcomes=[
                            {"semantic_key": "control:save", "status": "blocked"}
                        ],
                    )
                ],
            )

    def test_target_owned_e2e_is_limited_to_driven_asserted_paths(self) -> None:
        with self.assertRaisesRegex(ValueError, "driven semantic paths"):
            recovery_projection(
                "succeeded",
                [self.attempt("succeeded", method_family="target_owned_e2e")],
            )
        projection = recovery_projection(
            "succeeded",
            [
                self.attempt(
                    "succeeded",
                    method_family="target_owned_e2e",
                    driven_semantic_keys=["control:save"],
                    assertion_ids=["assert-save"],
                    assertion_evidence_refs=["evidence/assert-save.json"],
                )
            ],
        )
        self.assertEqual("succeeded", projection["status"])

    def test_blocked_recovery_requires_final_inventory_refresh(self) -> None:
        with self.assertRaisesRegex(ValueError, "final inventory refresh"):
            recovery_projection(
                "blocked",
                [
                    self.attempt(
                        "blocked",
                        inventory_refresh=False,
                        path_outcomes=[
                            {"semantic_key": "control:save", "status": "blocked"}
                        ],
                    )
                ],
            )

    def test_user_stop_has_highest_precedence(self) -> None:
        projection = recovery_projection(
            "user_stopped",
            [
                self.attempt("succeeded"),
                self.attempt(
                    "user_stopped",
                    method_family="chrome",
                    binding_id="chrome-2",
                ),
            ],
        )
        self.assertEqual("user_stopped", projection["status"])

    def test_human_summary_is_early_bounded_and_escaped(self) -> None:
        frontier = {
            "closure_state": "incomplete",
            "closure_reason": "<browser failed>",
            "rows": [],
            "summary": {
                "intent": 0, "feature": 0, "surface": 0,
                "control": 0, "transition": 0,
            },
            "discovery_passes": [],
            "reconciliation_differences": [],
        }
        rendered = coverage_confidence_html(
            frontier,
            {
                "_recovery_summary": {
                    "status": "active",
                    "attempt_count": 2,
                    "recovered_paths": 0,
                    "remaining_debt": 1,
                }
            },
        )
        self.assertIn("In progress", rendered)
        self.assertIn("<details>", rendered)
        self.assertIn("&lt;browser failed&gt;", rendered)
        self.assertNotIn("<script", rendered)


if __name__ == "__main__":
    unittest.main()

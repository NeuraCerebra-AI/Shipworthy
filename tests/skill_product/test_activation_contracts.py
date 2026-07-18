from pathlib import Path
import unittest


REPO = Path(__file__).resolve().parents[2]
SKILLS = REPO / "plugins" / "shipworthy" / "skills"


class DeepReviewActivationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.deep_review = (SKILLS / "ship-deep-review" / "SKILL.md").read_text(encoding="utf-8")
        cls.orchestrator = (SKILLS / "ship-readiness-orchestrator" / "SKILL.md").read_text(encoding="utf-8")

    def test_description_is_limited_to_two_activation_paths_and_veto(self):
        expected = (
            "description: Use only when the user explicitly invokes or names ship-deep-review, "
            "or when an active ship-readiness-orchestrator run explicitly loads it as the required "
            "controller. Do not activate from generic audit, review, critique, validation, research, "
            "or readiness language; an explicit instruction not to use ship-deep-review always "
            "prevents activation."
        )
        self.assertIn(expected, self.deep_review.split("---", 2)[1])

    def test_activation_gate_precedes_protocol_and_closes_all_workflow_actions(self):
        gate = self.deep_review.index("## Activation Gate")
        protocol = self.deep_review.index("## Required References")
        self.assertLess(gate, protocol)
        for text in (
            "explicitly invokes or names `ship-deep-review`",
            "`ship-readiness-orchestrator` is already active",
            "explicit instruction not to use `ship-deep-review`",
            "must not load\nthe skill’s references",
            "or dispatch review agents",
            "Once this gate legitimately opens",
        ):
            self.assertIn(text, self.deep_review)

    def test_generic_review_phrases_are_explicit_non_triggers(self):
        for phrase in (
            "deep review",
            "deep audit",
            "comprehensive audit",
            "adversarial or hostile review",
            "evidence-first audit",
            "multi-wave or multi-stage review",
            "product-readiness audit",
            "implementation-plan critique",
            "research validation",
        ):
            self.assertIn(f"- {phrase}", self.deep_review)

    def test_readiness_orchestrator_handoff_remains_required(self):
        self.assertIn(
            "**REQUIRED CONTROLLER:** Use `ship-deep-review` as the top-level controller",
            self.orchestrator,
        )


if __name__ == "__main__":
    unittest.main()

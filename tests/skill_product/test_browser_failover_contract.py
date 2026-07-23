from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "plugins/shipworthy/skills"
ORCHESTRATOR = SKILLS / "ship-readiness-orchestrator"
PRODUCT = SKILLS / "ship-product-workflows"
CLARITY = SKILLS / "ship-workflow-clarity"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(document: str, heading: str, next_heading: str | None = None) -> str:
    start = document.index(heading)
    end = document.index(next_heading, start) if next_heading else len(document)
    return document[start:end]


class BrowserFailoverContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.orchestrator = read(ORCHESTRATOR / "SKILL.md")
        cls.browser_routing = read(ORCHESTRATOR / "references/browser-evidence-routing.md")
        cls.lane_prompts = read(ORCHESTRATOR / "references/lane-prompts.md")
        cls.product = read(PRODUCT / "SKILL.md")
        cls.product_agents = read(PRODUCT / "references/agent-and-wave-orchestration.md")
        cls.clarity_agents = read(CLARITY / "references/agent-and-tool-orchestration.md")
        cls.deep_review_waves = read(SKILLS / "ship-deep-review/references/wave-protocol.md")

    def test_browser_failure_requires_independent_playwright_failover(self) -> None:
        for phrase in (
            "Browser Failover Contract",
            "locked, disconnected, stale, or unavailable",
            "independent Playwright",
            "same locked browser binding",
            "does not count as the fallback",
            "already-enabled host Playwright capability",
            "must not install Playwright",
        ):
            self.assertIn(phrase, self.browser_routing)

    def test_orchestrator_and_product_skill_make_failover_non_optional(self) -> None:
        for document in (self.orchestrator, self.product):
            self.assertIn("Browser Failover Gate", document)
            self.assertIn("independent Playwright", document)
            self.assertIn("do not stop the lane", document)

    def test_browser_using_orchestrator_agent_prompts_carry_failover_contract(self) -> None:
        controller = section(
            self.lane_prompts,
            "## Controller Brief",
            "## Product Workflow Lane",
        )
        product_lane = section(
            self.lane_prompts,
            "## Product Workflow Lane",
            "## Workflow Clarity Lane",
        )
        for prompt in (controller, product_lane):
            self.assertIn("independent Playwright", prompt)
            self.assertIn("same locked native-browser binding", prompt)
            self.assertIn("do not claim frontend coverage or closure", prompt)
        self.assertIn("browser_failover_receipt", product_lane)

    def test_browser_capable_lane_skeletons_carry_failover_contract(self) -> None:
        product_lane = section(
            self.product_agents,
            "Product audit lane:",
            "Clarity lane:",
        )
        claude_lane = section(
            self.clarity_agents,
            "Claude major audit lane:",
            "Wave handoff:",
        )
        for prompt in (product_lane, claude_lane):
            self.assertIn("independent Playwright", prompt)
            self.assertIn("same locked", prompt)
            self.assertIn("return the blocker", prompt)

    def test_verifier_rejects_skipped_or_fake_playwright_failover(self) -> None:
        verifier = section(self.lane_prompts, "## Independent Verifier")
        for phrase in (
            "browser failover receipt",
            "independent Playwright",
            "same locked browser binding",
            "cleanup result",
            "reject closure",
        ):
            self.assertIn(phrase, verifier)

    def test_standalone_deep_review_browser_wave_carries_failover_contract(self) -> None:
        wave_two = section(
            self.deep_review_waves,
            "## Wave 2: Targeted Deep Dive",
            "## Verified Barrier After Wave 2",
        )
        for phrase in (
            "independent Playwright",
            "same locked browser binding",
            "return the blocker",
            "do not claim browser coverage",
        ):
            self.assertIn(phrase, wave_two)


if __name__ == "__main__":
    unittest.main()

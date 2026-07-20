from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "plugins/shipworthy/skills"
ORCHESTRATOR = SKILLS / "ship-readiness-orchestrator"
PRODUCT = SKILLS / "ship-product-workflows"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class ExhaustiveSurfaceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.orchestrator = read(ORCHESTRATOR / "SKILL.md")
        cls.evidence = read(ORCHESTRATOR / "references/evidence-state.md")
        cls.prompts = read(ORCHESTRATOR / "references/lane-prompts.md")
        cls.pressure = read(ORCHESTRATOR / "references/pressure-tests.md")
        cls.product = read(PRODUCT / "SKILL.md")
        cls.discovery = read(PRODUCT / "references/path-discovery-and-coverage.md")

    def test_product_lane_requires_material_state_control_census_and_safe_attempts(self) -> None:
        for phrase in (
            "material-state control census",
            "every visible or discoverable interactive control",
            "once per materially different behavior",
            "noninteractive false affordance",
            "control identity",
        ):
            self.assertIn(phrase, self.product)

    def test_discovery_contract_names_four_real_method_families(self) -> None:
        for family in (
            "runtime_human_interaction",
            "runtime_structural_inventory",
            "static_implementation_inventory",
            "declared_behavior_inventory",
        ):
            self.assertIn(family, self.discovery)
        self.assertIn("A renamed method_detail does not create an independent method family", self.discovery)

    def test_discovery_requires_semantic_lineage_variants_and_reconciliation(self) -> None:
        for phrase in (
            "intent → feature → surface → control → transition",
            "shipworthy-semantic-v1",
            "role, state, viewport",
            "feature and surface levels",
            "before_state",
            "after_state",
        ):
            self.assertIn(phrase, self.discovery)

    def test_semantic_identity_is_mechanical_and_variant_rows_are_not_collapsed(self) -> None:
        for phrase in (
            "intent:<role>:<goal>",
            "feature:<feature>",
            "surface:<route>:<state>:<role>:<viewport>",
            "control:<parent-surface-key>:<name>:<control-type>:<behavior-disambiguator>",
            "transition:<before-state>:<parent-control-key>:<after-state>",
            "Dotted ad hoc IDs",
            "one surface row for each materially different role/state/viewport tuple",
        ):
            self.assertIn(phrase, self.discovery)

    def test_resettable_synthetic_fixture_keeps_reversible_actions_in_scope(self) -> None:
        for phrase in (
            "resettable synthetic fixture",
            "create, edit, validation-retry, publish, export, and download",
            "supplied reset mechanism",
            "explicitly destructive, external-message, payment, credential, or production action",
        ):
            self.assertIn(phrase, self.discovery)

    def test_variant_closure_covers_spawned_surfaces_and_canonical_states(self) -> None:
        for phrase in (
            "Canonical surface states",
            "`normal` for the default interactive state",
            "open every safe control that can spawn a menu, dialog, drawer, palette, popover, or nested route",
            "Test each material surface at every relevant supplied role and viewport",
            "record a reload/re-entry proof as its own transition row",
            "visible unavailable capability or disabled feature flag",
            "Synthetic role selectors",
        ):
            self.assertIn(phrase, self.discovery)

    def test_materiality_distinguishes_verdict_rows_from_lineage_support(self) -> None:
        self.assertIn("Set `material: false` only for a structural lineage/support row", self.discovery)
        self.assertIn("could not independently change the readiness verdict", self.discovery)
        self.assertIn("Do not use ordinal names such as `save-primary`", self.discovery)

    def test_top_level_skill_repeats_non_optional_frontier_identity_gate(self) -> None:
        for phrase in (
            "Canonical frontier identity gate",
            "surface:<actual-route>:<state>:<role>:<viewport>",
            "Shorthand keys such as `surface:dashboard`",
            "must not claim schema validation",
        ):
            self.assertIn(phrase, self.product)

    def test_top_level_gate_prevents_false_closure_on_material_substates(self) -> None:
        for phrase in (
            "spawned surface gets its own surface row",
            "disabled control is `blocked`",
            "unavailable capability gets a feature row",
            "reload or re-entry gets a separate transition row",
            "sampled_with_justification",
            "observed_effect_code",
        ):
            self.assertIn(phrase, self.product)

    def test_closure_reconciles_raw_interactions_findings_and_frontier_rows(self) -> None:
        for phrase in (
            "reconcile every raw runtime observation to frontier rows",
            "observation-to-frontier reconciliation table",
            "one control row per distinct observed input mechanism",
            "one transition row per observed state boundary",
            "includes the affected transition row",
            "disabled without an observed explanation or recovery route is a finding",
            "Canonical browser viewport key values are `desktop`, `mobile`, or `tablet`",
            "Record exact pixel dimensions in observations",
        ):
            self.assertIn(phrase, self.product)

        for phrase in (
            "raw observation has no corresponding distinct input control",
            "spawned surface",
            "state-boundary transition",
            "finding lineage",
        ):
            self.assertIn(phrase, self.prompts)

        for phrase in (
            "re-census newly revealed controls",
            "distinct input mode or keyboard shortcut gets its own control row",
            "Never model a noninteractive false affordance as a covered control",
            "triggering surface, not the resulting dialog",
            "every material surface-spawning control at each supplied role and viewport",
            "bounded conventional shortcut probe",
            "never only an intent or evidence-debt row",
        ):
            self.assertIn(phrase, self.product)

    def test_closed_frontier_requires_two_independent_zero_yield_passes(self) -> None:
        for document in (self.orchestrator, self.evidence, self.discovery):
            self.assertIn("two qualifying zero-yield discovery passes", document)
            self.assertIn("distinct canonical method families", document)

    def test_evidence_contract_defines_objective_closure_precedence(self) -> None:
        for state in ("closed_multi_source", "incomplete", "single_source", "blocked", "static_only"):
            self.assertIn(f"`{state}`", self.evidence)
        self.assertIn("Closure precedence", self.evidence)
        self.assertIn("caller-supplied counts must exactly equal counts derived from rows", self.evidence)
        self.assertIn("reconciliation differences", self.evidence)

    def test_findings_are_separate_from_expected_dispositions(self) -> None:
        for phrase in (
            "Do not turn a normal blocked, avoided, missing, or out-of-scope disposition into a finding",
            "affected_semantic_keys",
            "observed_effect_code",
            "evidence_refs",
        ):
            self.assertIn(phrase, self.prompts)

    def test_verifier_rejects_false_exhaustive_closure(self) -> None:
        for phrase in (
            "single_source",
            "unresolved material rows",
            "unreconciled feature or surface differences",
            "summary/row count drift",
            "closed_multi_source",
        ):
            self.assertIn(phrase, self.prompts)

    def test_verifier_rechecks_variant_execution_input_modes_and_safety_dispositions(self) -> None:
        for phrase in (
            "independently repeat the bounded conventional shortcut probe",
            "material supplied role/state/viewport variant",
            "cannot be `sampled_with_justification`",
            "in-scope destructive control is `avoided`, not `out_of_scope`",
            "event listeners and keyboard handlers",
        ):
            self.assertIn(phrase, self.prompts)

    def test_orchestrator_routes_to_canonical_contract_before_collection(self) -> None:
        for path in (
            "references/schemas/readiness-ledger.schema.json",
            "references/evidence-state.md",
            "ship-product-workflows/references/path-discovery-and-coverage.md",
        ):
            self.assertIn(path, self.orchestrator)
        self.assertIn("one canonical `path_frontier`", self.orchestrator)

    def test_pressure_suite_includes_confusing_surface_gauntlet(self) -> None:
        self.assertIn("Scenario 12: Exhaustive Surface Gauntlet", self.pressure)
        for phrase in (
            "duplicate labels",
            "mobile-only",
            "role-gated",
            "keyboard-only",
            "reload",
            "false affordance",
            "promised-but-missing",
        ):
            self.assertIn(phrase, self.pressure)


if __name__ == "__main__":
    unittest.main()

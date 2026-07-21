from __future__ import annotations

import unittest

from tests.skill_product.gauntlet.behavior_graph import (
    BehaviorNode,
    Match,
    match_behavior,
    normalize_input,
    normalize_role,
    normalize_route,
    normalize_text,
    normalize_viewport,
    parse_semantic_key,
    verify_execution_claim,
    verify_private_expectation,
)
from tests.skill_product.gauntlet.diagnostics import classify_comparison


class BehavioralNormalizationTests(unittest.TestCase):
    def test_unicode_letters_numbers_and_routes_normalize_without_ascii_data_loss(self) -> None:
        self.assertEqual("café-项目-12", normalize_text(" Café / 项目 １２ "))
        self.assertEqual("/projects/import/café", normalize_route("HTTPS://EXAMPLE.TEST/projects/%69mport/Caf%C3%A9/?q=ignored#x"))
        self.assertEqual("/projects/a%2fb", normalize_route("/projects/a%2Fb"))

    def test_roles_viewports_and_input_mechanisms_use_bounded_taxonomies(self) -> None:
        self.assertEqual("admin", normalize_role("Administrator"))
        self.assertEqual("mobile", normalize_viewport("phone-390"))
        self.assertEqual("desktop", normalize_viewport("desktop-1440"))
        self.assertEqual("keyboard", normalize_input("Meta+K shortcut"))
        self.assertEqual("secondary-pointer", normalize_input("right click"))


class BehavioralMatchingTests(unittest.TestCase):
    def node(self, **overrides) -> BehaviorNode:
        values = {
            "kind": "control",
            "route": "/projects",
            "role": "member",
            "state": "editing",
            "viewport": "desktop",
            "control_identity": "Save",
            "control_type": "button",
            "input_mechanism": "pointer",
            "surface": "editor",
            "behavior": "persist",
        }
        values.update(overrides)
        return BehaviorNode(**values)

    def test_exact_key_wins_and_a_supplied_wrong_key_cannot_be_overridden_by_fuzzy_text(self) -> None:
        expected = self.node(semantic_key="control:expected")
        exact = self.node(semantic_key="control:expected")
        wrong = self.node(semantic_key="control:different")
        self.assertEqual(Match("exact", 0), match_behavior(expected, [exact]))
        self.assertEqual("key_mismatch", match_behavior(expected, [wrong]).status)

    def test_unique_structural_alias_and_equivalent_input_are_accepted(self) -> None:
        expected = self.node(control_identity="Save", control_type="button", input_mechanism="pointer")
        actual = self.node(control_identity="Save changes", control_type="submit", input_mechanism="mouse click", behavior="persist project")
        match = match_behavior(expected, [actual], aliases=("save changes",), behavior_aliases=("persist project",))
        self.assertEqual(Match("equivalent", 0), match)

    def test_ambiguity_is_review_required_instead_of_arbitrary_selection(self) -> None:
        expected = self.node(control_identity="Save")
        candidates = [self.node(control_identity="Save changes"), self.node(control_identity="Save project")]
        match = match_behavior(expected, candidates, aliases=("save changes", "save project"))
        self.assertEqual("ambiguous", match.status)
        self.assertEqual((0, 1), match.candidate_indexes)

    def test_transition_requires_before_after_and_disambiguating_behavior(self) -> None:
        expected = self.node(kind="transition", before_state="editing", after_state="saved", behavior="reload verification")
        wrong = self.node(kind="transition", before_state="editing", after_state="lost", behavior="reload verification")
        right = self.node(kind="transition", before_state="editing", after_state="saved", behavior="reload check")
        self.assertEqual("equivalent", match_behavior(expected, [wrong, right], behavior_aliases=("reload check",)).status)

    def test_semantic_key_parser_extracts_route_role_state_viewport_and_control(self) -> None:
        node = parse_semantic_key("control:surface:/team:invite-dialog:admin:mobile:invite-member:button:open-dialog")
        self.assertEqual(("/team", "admin", "invite-dialog", "mobile"), (node.route, node.role, node.state, node.viewport))
        self.assertEqual(("invite-member", "button", "open-dialog"), (node.control_identity, node.control_type, node.behavior))


class DiagnosticClassificationTests(unittest.TestCase):
    def test_receipt_support_requires_right_action_type_and_disambiguating_behavior(self) -> None:
        item = {
            "kind": "control",
            "semantic_key": "control:surface:/projects:editing:member:desktop:save:button:persist",
            "identity": "Save",
            "accepted_aliases": ["Save changes"],
            "receipt_behavior_aliases": ["save-real"],
        }
        row = {"semantic_key": item["semantic_key"], "status": "covered", "evidence_refs": ["proof.json"]}
        event = {
            "event_type": "activation", "route": "/projects", "role": "member", "state": "editing", "viewport_class": "desktop",
            "control": {"identity": "Save changes", "type": "button"}, "input_mechanism": "pointer", "behavior": "save-real",
        }
        self.assertEqual("supported", verify_execution_claim(item, row, [event]).status)
        self.assertEqual("missing", verify_execution_claim(item, row, [{**event, "behavior": "save-visual"}]).status)
        self.assertEqual("missing", verify_execution_claim(item, row, []).status)

    def test_blocked_and_avoided_claims_require_matching_inventory_safety_events(self) -> None:
        blocked_item = {
            "kind": "control", "semantic_key": "control:surface:/projects:editing:member:desktop:archive:button:disabled",
            "identity": "Archive", "accepted_aliases": [], "receipt_behavior_aliases": [],
        }
        blocked_row = {"semantic_key": blocked_item["semantic_key"], "status": "blocked", "evidence_refs": ["archive.png"]}
        blocked_event = {"event_type": "blocked", "route": "/projects", "role": "member", "viewport_class": "desktop", "control": {"identity": "Archive", "type": "button"}, "reason": "disabled"}
        self.assertEqual("supported", verify_execution_claim(blocked_item, blocked_row, [blocked_event]).status)
        self.assertEqual("missing", verify_execution_claim(blocked_item, blocked_row, [{**blocked_event, "event_type": "activation"}]).status)

        avoided_item = {
            "kind": "control", "semantic_key": "control:surface:/admin/data:normal:admin:desktop:delete-all-data:button:destructive",
            "identity": "Delete all data", "accepted_aliases": [], "receipt_behavior_aliases": [],
        }
        avoided_row = {"semantic_key": avoided_item["semantic_key"], "status": "avoided", "evidence_refs": ["delete.png"]}
        avoided_event = {"event_type": "avoided", "route": "/admin/data", "role": "admin", "viewport_class": "desktop", "control": {"identity": "Delete all data", "type": "button"}, "reason": "authorization-required"}
        self.assertEqual("supported", verify_execution_claim(avoided_item, avoided_row, [avoided_event]).status)

    def test_private_multi_clause_expectation_requires_every_observed_transition(self) -> None:
        expectation = {
            "clauses": [
                {"event_types": ["transition"], "routes": ["/projects"], "behaviors": ["projects"], "outcomes": ["name-required"]},
                {"event_types": ["transition"], "routes": ["/projects"], "behaviors": ["projects"], "outcomes": ["ok"]},
            ]
        }
        invalid = {"event_type": "transition", "route": "/projects", "behavior": "projects", "outcome": "name-required"}
        recovered = {"event_type": "transition", "route": "/projects", "behavior": "projects", "outcome": "ok"}
        self.assertEqual("supported", verify_private_expectation(expectation, [invalid, recovered]).status)
        self.assertEqual("missing", verify_private_expectation(expectation, [invalid]).status)

    def test_discovery_miss_execution_failure_valid_extra_and_false_positive_are_separate(self) -> None:
        expected = [BehaviorNode(kind="control", semantic_key="control:a", route="/a", control_identity="A", control_type="button")]
        report = [
            BehaviorNode(kind="control", semantic_key="control:extra", route="/extra", control_identity="Extra", control_type="button", evidence_links=("extra.json",)),
        ]
        receipt = [report[0]]
        result = classify_comparison(expected, report, receipt, supported_extra_keys={"control:extra"}, finding_keys={"control:false"})
        self.assertEqual(["control:a"], result["A_material_discovery_miss"])
        self.assertEqual(["control:extra"], result["D_valid_extra"])
        self.assertEqual(["control:false"], result["E_unsupported_finding"])
        self.assertEqual([], result["B_execution_proof_lineage_failure"])

    def test_covered_claim_without_receipt_or_evidence_is_category_b(self) -> None:
        node = BehaviorNode(kind="control", semantic_key="control:save", route="/projects", control_identity="Save", control_type="button")
        result = classify_comparison([node], [node], [], supported_extra_keys=set(), finding_keys=set())
        self.assertEqual(["control:save"], result["B_execution_proof_lineage_failure"])
        self.assertEqual("FAIL", result["status"])

    def test_ambiguous_receipt_match_is_review_required_and_category_c(self) -> None:
        report = BehaviorNode(kind="control", route="/projects", control_identity="Save", control_type="button", evidence_links=("proof.json",))
        candidates = [
            BehaviorNode(kind="control", route="/projects", control_identity="Save", control_type="button"),
            BehaviorNode(kind="control", route="/projects", control_identity="Save", control_type="button"),
        ]
        result = classify_comparison([report], [report], candidates, supported_extra_keys=set(), finding_keys=set())
        self.assertEqual("REVIEW_REQUIRED", result["status"])
        self.assertTrue(result["C_normalization_or_comparator_problem"])


if __name__ == "__main__":
    unittest.main()

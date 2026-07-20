from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from tests.skill_product.support.frontier_validation import FrontierValidationError, validate_frontier


ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas"


def observation(method: str, evidence: str, pass_id: str) -> dict:
    return {
        "method_taxonomy_version": "shipworthy-methods-v1",
        "method_family": method,
        "method_detail": method + "-detail",
        "provenance": "native-codex",
        "role": "member",
        "state": "normal",
        "viewport": "desktop",
        "discovery_pass_id": pass_id,
        "evidence_refs": [evidence],
    }


def row(row_id: str, kind: str, key: str, parent: str | None, evidence: str) -> dict:
    value = {
        "id": row_id,
        "kind": kind,
        "semantic_key": key,
        "normalization_version": "shipworthy-semantic-v1",
        "method_taxonomy_version": "shipworthy-methods-v1",
        "status": "covered",
        "material": True,
        "attempt_count": 1,
        "evidence_refs": [evidence],
        "observations": [
            observation("runtime_human_interaction", evidence, "PASS-1"),
            observation("runtime_structural_inventory", evidence, "PASS-2"),
        ],
    }
    if parent is not None:
        value["parent_id"] = parent
    return value


def valid_frontier(evidence_name: str = "proof.json") -> dict:
    rows = [
        row("PF-I", "intent", "intent:member:manage-project", None, evidence_name),
        row("PF-F", "feature", "feature:project-management", "PF-I", evidence_name),
        row("PF-S", "surface", "surface:/projects:normal:member:desktop", "PF-F", evidence_name),
        row("PF-C", "control", "control:surface:/projects:normal:member:desktop:save:button:persist", "PF-S", evidence_name),
        row("PF-T", "transition", "transition:editing:control:surface:/projects:normal:member:desktop:save:button:persist:saved", "PF-C", evidence_name),
    ]
    rows[3]["control_identity"] = {"name": "Save", "control_type": "button", "disambiguator": "persist"}
    rows[4].update(before_state="editing", after_state="saved")
    return {
        "normalization_version": "shipworthy-semantic-v1",
        "method_taxonomy_version": "shipworthy-methods-v1",
        "closure_state": "closed_multi_source",
        "summary": {"intent": 1, "feature": 1, "surface": 1, "control": 1, "transition": 1},
        "rows": rows,
        "discovery_passes": [
            {"id": "PASS-1", "method_taxonomy_version": "shipworthy-methods-v1", "method_family": "runtime_human_interaction", "role": "member", "fixture": "seed", "viewport": "desktop", "starting_frontier_digest": "a" * 64, "ending_frontier_digest": "a" * 64, "new_semantic_keys": []},
            {"id": "PASS-2", "method_taxonomy_version": "shipworthy-methods-v1", "method_family": "runtime_structural_inventory", "role": "member", "fixture": "seed", "viewport": "desktop", "starting_frontier_digest": "a" * 64, "ending_frontier_digest": "a" * 64, "new_semantic_keys": []},
        ],
        "reconciliation_differences": [],
    }


class FrontierContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.evidence_root = Path(self.temp.name)
        (self.evidence_root / "proof.json").write_text("{}", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_valid_multi_source_frontier_passes(self) -> None:
        result = validate_frontier(valid_frontier(), self.evidence_root)
        self.assertEqual("closed_multi_source", result["closure_state"])
        self.assertEqual(5, result["row_count"])

    def test_rejects_duplicate_ids_bad_lineage_and_missing_kind_fields(self) -> None:
        for mutate in (
            lambda value: value["rows"].__setitem__(1, {**value["rows"][1], "id": "PF-I"}),
            lambda value: value["rows"][3].__setitem__("parent_id", "PF-I"),
            lambda value: value["rows"][4].pop("after_state"),
        ):
            candidate = valid_frontier()
            mutate(candidate)
            with self.assertRaises(FrontierValidationError):
                validate_frontier(candidate, self.evidence_root)

    def test_rejects_duplicate_semantic_identity_and_unknown_observation_pass(self) -> None:
        candidate = valid_frontier()
        candidate["rows"][4]["semantic_key"] = candidate["rows"][3]["semantic_key"]
        candidate["rows"][4]["kind"] = "control"
        candidate["rows"][4]["control_identity"] = candidate["rows"][3]["control_identity"]
        with self.assertRaises(FrontierValidationError):
            validate_frontier(candidate, self.evidence_root)

        candidate = valid_frontier()
        candidate["rows"][0]["observations"][0]["discovery_pass_id"] = "PASS-MISSING"
        with self.assertRaises(FrontierValidationError):
            validate_frontier(candidate, self.evidence_root)

    def test_rejects_covered_without_attempt_proof_and_unresolved_evidence(self) -> None:
        candidate = valid_frontier()
        candidate["rows"][3]["attempt_count"] = 0
        with self.assertRaises(FrontierValidationError):
            validate_frontier(candidate, self.evidence_root)
        candidate = valid_frontier("missing.json")
        with self.assertRaises(FrontierValidationError):
            validate_frontier(candidate, self.evidence_root)

    def test_rejects_count_drift_reconciliation_debt_and_unresolved_closed_rows(self) -> None:
        candidate = valid_frontier()
        candidate["summary"]["control"] = 2
        with self.assertRaises(FrontierValidationError):
            validate_frontier(candidate, self.evidence_root)
        candidate = valid_frontier()
        candidate["reconciliation_differences"] = [{"semantic_key": "feature:project-management", "reason": "runtime/source conflict"}]
        with self.assertRaises(FrontierValidationError):
            validate_frontier(candidate, self.evidence_root)
        candidate = valid_frontier()
        candidate["rows"][3]["status"] = "unknown"
        with self.assertRaises(FrontierValidationError):
            validate_frontier(candidate, self.evidence_root)

    def test_rejects_relabelled_method_details_and_nonqualifying_zero_yield_passes(self) -> None:
        candidate = valid_frontier()
        for item in candidate["rows"]:
            item["observations"][1]["method_family"] = "runtime_human_interaction"
            item["observations"][1]["method_detail"] = "renamed-browser-walk"
        candidate["discovery_passes"][1]["method_family"] = "runtime_human_interaction"
        with self.assertRaises(FrontierValidationError):
            validate_frontier(candidate, self.evidence_root)
        candidate = valid_frontier()
        candidate["discovery_passes"][1]["new_semantic_keys"] = ["control:new"]
        with self.assertRaises(FrontierValidationError):
            validate_frontier(candidate, self.evidence_root)

    def test_feature_requires_path_or_explicit_terminal_disposition(self) -> None:
        candidate = valid_frontier()
        candidate["rows"] = candidate["rows"][:2]
        candidate["rows"][1]["status"] = "unattempted"
        candidate["summary"] = {"intent": 1, "feature": 1, "surface": 0, "control": 0, "transition": 0}
        with self.assertRaises(FrontierValidationError):
            validate_frontier(candidate, self.evidence_root)

    def test_schemas_expose_one_canonical_frontier_definition(self) -> None:
        ledger = json.loads((SCHEMAS / "readiness-ledger.schema.json").read_text(encoding="utf-8"))
        report = json.loads((SCHEMAS / "report-input.schema.json").read_text(encoding="utf-8"))
        self.assertIn("path_frontier", ledger["$defs"])
        self.assertEqual({"$ref": "#/$defs/path_frontier"}, ledger["properties"]["path_frontier"])
        self.assertEqual({"$ref": "readiness-ledger.schema.json"}, report["$defs"]["ReadinessLedger"])

    def test_schema_subset_resolves_only_bounded_same_directory_refs(self) -> None:
        from tests.skill_product.support.schema_subset import SchemaReferenceError, validate

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "shared.json").write_text(json.dumps({"$defs": {"Token": {"type": "string", "pattern": "^ok$"}}}))
            schema = root / "schema.json"
            schema.write_text(json.dumps({"$ref": "shared.json#/$defs/Token"}))
            validate("ok", schema)
            for reference in ("https://example.invalid/x.json", "/tmp/x.json", "../x.json"):
                schema.write_text(json.dumps({"$ref": reference}))
                with self.subTest(reference=reference), self.assertRaises(SchemaReferenceError):
                    validate("ok", schema)


if __name__ == "__main__":
    unittest.main()

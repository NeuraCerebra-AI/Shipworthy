from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ORCHESTRATOR = ROOT / "plugins" / "shipworthy" / "skills" / "ship-readiness-orchestrator"
SCHEMA_DESTINATION = ORCHESTRATOR / "references" / "schemas"
FIXTURES = ROOT / "tests" / "skill_product" / "fixtures"
EXPECTED_SCHEMA_HASHES = {
    "browser-evidence-envelope.schema.json": "bad61277f885bb7ba1437ab85e07edbc5a4454448e82aa664dde7005344c8024",
    "readiness-ledger.schema.json": "5972326a8d0b91f642c3d6ad72b50db1b4e700332a3d13511804bd3993f31173",
    "report-input.schema.json": "9a6e6074184baca04e347508a1a3b299bb0167ced6667dd21f74fea213d3858c",
}


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _payload(path: Path):
    return json.loads(path.read_bytes())


class LedgerContractTest(unittest.TestCase):
    def test_installed_schemas_match_approved_v1_contract_hashes(self) -> None:
        for name, expected_hash in EXPECTED_SCHEMA_HASHES.items():
            destination = SCHEMA_DESTINATION / name
            self.assertEqual(expected_hash, _digest(destination))

    def test_skill_routes_structured_inputs_to_schema_contracts_conditionally(self) -> None:
        skill = (ORCHESTRATOR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/ledger-validation-contract.md", skill)
        self.assertIn("references/evidence-import-contract.md", skill)
        self.assertIn("before structured render or import", skill)
        self.assertIn("only for browser, Playwright, or legacy structured input", skill)
        for name in EXPECTED_SCHEMA_HASHES:
            self.assertIn(f"references/schemas/{name}", skill)

    def test_contract_references_keep_compatibility_policy_out(self) -> None:
        references = [
            ORCHESTRATOR / "SKILL.md",
            ORCHESTRATOR / "references" / "ledger-validation-contract.md",
            ORCHESTRATOR / "references" / "evidence-import-contract.md",
        ]
        combined = "\n".join(path.read_text().lower() for path in references)
        for forbidden in ("optional core", "package compatibility", "core compatibility"):
            self.assertNotIn(forbidden, combined)
        evidence_import = references[-1].read_text().lower()
        self.assertNotRegex(evidence_import, r"\bretir(?:e|ed|ement|ing)\b")
        retirement_authority = (
            ROOT / "docs" / "phase0" / "legacy-transform-retirement.md"
        ).read_text().lower()
        self.assertIn("legacy transform retirement criteria", retirement_authority)

    def test_schema_subset_accepts_all_direct_schema_golden_fixtures(self) -> None:
        from tests.skill_product.support.schema_subset import validate

        valid = {
            "readiness-ledger.schema.json": [
                FIXTURES / "v1" / "confirmed-blocker-ledger.json",
                FIXTURES / "v1" / "incomplete-ledger.json",
            ],
            "report-input.schema.json": [FIXTURES / "v1" / "pure-action-first-report-input.json"],
            "browser-evidence-envelope.schema.json": sorted(
                (FIXTURES / "browser_evidence").glob("valid-*.json")
            ),
        }
        for schema_name, fixtures in valid.items():
            for fixture in fixtures:
                with self.subTest(schema=schema_name, fixture=fixture.name):
                    validate(_payload(fixture), SCHEMA_DESTINATION / schema_name)

    def test_schema_subset_rejects_hostile_or_semantically_invalid_ledgers(self) -> None:
        from tests.skill_product.support.schema_subset import SchemaValidationError, validate

        names = (
            "hostile-path-ledger.json", "inconsistent-blocker-ledger.json",
            "lying-green-ledger.json", "mismatched-gate-ledger.json",
            "unknown-enum-ledger.json",
        )
        for name in names:
            with self.subTest(fixture=name), self.assertRaises(SchemaValidationError):
                validate(_payload(FIXTURES / "v1" / name), SCHEMA_DESTINATION / "readiness-ledger.schema.json")

    def test_missing_artifact_fixture_is_structurally_valid_but_semantic_debt(self) -> None:
        from tests.skill_product.support.schema_subset import validate

        candidate = _payload(FIXTURES / "v1" / "missing-artifact-ledger.json")
        validate(candidate, SCHEMA_DESTINATION / "readiness-ledger.schema.json")
        missing = {
            artifact["artifact_id"]
            for artifact in candidate["artifacts"]
            if artifact["availability"] == "missing"
        }
        self.assertEqual({"ART-MISSING-001"}, missing)
        contract = (ORCHESTRATOR / "references" / "ledger-validation-contract.md").read_text()
        self.assertIn("Missing", contract)

    def test_schema_subset_fails_closed_on_unknown_schema_keyword(self) -> None:
        from tests.skill_product.support.schema_subset import UnsupportedKeywordError, validate

        with tempfile.TemporaryDirectory() as directory:
            schema = Path(directory) / "schema.json"
            schema.write_text(json.dumps({"type": "object", "unevaluatedProperties": False}))
            with self.assertRaisesRegex(UnsupportedKeywordError, "unevaluatedProperties"):
                validate({}, schema)

    def test_schema_subset_rejects_remote_and_missing_external_refs(self) -> None:
        from tests.skill_product.support.schema_subset import SchemaReferenceError, validate

        with tempfile.TemporaryDirectory() as directory:
            schema = Path(directory) / "schema.json"
            for reference in ("https://example.invalid/schema.json", "other.json#/$defs/X"):
                schema.write_text(json.dumps({"$ref": reference}))
                with self.subTest(reference=reference), self.assertRaises(SchemaReferenceError):
                    validate({}, schema)

    def test_schema_version_and_field_by_field_semantic_copy(self) -> None:
        from tests.skill_product.support.schema_subset import semantic_diff

        for name in EXPECTED_SCHEMA_HASHES:
            destination = _payload(SCHEMA_DESTINATION / name)
            self.assertTrue(destination["$id"].startswith("https://shipworthy.local/schemas/v1/"))
            self.assertEqual([], semantic_diff(destination, deepcopy(destination)))
        ledger = (ROOT / "docs" / "phase0" / "schema-relocation-ledger.md").read_text()
        self.assertIn("remain v1", ledger)
        self.assertIn("Semantic diff: none", ledger)

    def test_legacy_and_playwright_are_bounded_pre_transform_inputs(self) -> None:
        contract = (ORCHESTRATOR / "references" / "evidence-import-contract.md").read_text()
        for phrase in ("legacy/readiness-v0", "playwright/json-reporter", "pre-transform", "post-transform"):
            self.assertIn(phrase, contract)
        self.assertIn("remote", contract.lower())
        self.assertIn("local", contract.lower())
        self.assertIn("proof ceiling", contract.lower())
        pre_transform = [
            FIXTURES / "legacy" / "readiness-v0.json",
            FIXTURES / "playwright" / "basic-report.json",
            FIXTURES / "playwright" / "unnamed-project-report.json",
        ]
        self.assertTrue(all(isinstance(_payload(path), dict) for path in pre_transform))

    def test_schema_subset_bounds_input_depth(self) -> None:
        from tests.skill_product.support.schema_subset import SchemaLimitError, validate

        candidate: dict[str, object] = {}
        cursor = candidate
        for _ in range(80):
            child: dict[str, object] = {}
            cursor["child"] = child
            cursor = child
        with self.assertRaises(SchemaLimitError):
            validate(candidate, SCHEMA_DESTINATION / "readiness-ledger.schema.json")

    def test_mutated_schema_copy_has_field_level_semantic_diff(self) -> None:
        from tests.skill_product.support.schema_subset import semantic_diff

        source = _payload(SCHEMA_DESTINATION / "readiness-ledger.schema.json")
        changed = deepcopy(source)
        changed["properties"]["schema_version"]["pattern"] = "^2\\.0$"
        self.assertEqual(
            ["$.properties.schema_version.pattern: '^1\\\\.0$' != '^2\\\\.0$'"],
            semantic_diff(source, changed),
        )


if __name__ == "__main__":
    unittest.main()

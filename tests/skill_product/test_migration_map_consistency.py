from __future__ import annotations

import unittest
import tempfile
import shutil
from pathlib import Path

try:
    from tests.skill_product import migration_contract
except ImportError:
    migration_contract = None


ROOT = Path(__file__).resolve().parents[2]
MIGRATION_MAP = ROOT / "docs" / "phase0" / "four-skill-migration-map.md"
DELETION_MANIFEST = ROOT / "docs" / "phase0" / "four-skill-deletion-manifest.md"
DIRTY_STATE = ROOT / "docs" / "phase0" / "preexisting-dirty-state.md"
SNAPSHOT_INVENTORY = (
    ROOT
    / "docs"
    / "phase0"
    / "evidence"
    / "preimplementation-snapshot"
    / "untracked-files.sha256"
)
APPROVED_INSTALLED_INVENTORY = (
    ROOT / "docs" / "phase0" / "approved-installed-inventory.txt"
)
BASE_COMMIT = "27e8425baa0cda1f64985eb361dfd90ef0752b6b"
ALLOWED_DISPOSITIONS = {
    "SKILL_INSTRUCTION",
    "REFERENCE",
    "SKILL_SCRIPT",
    "REPO_TEST",
    "REMOVE_PACKAGE_ONLY",
    "DEFER_EVIDENCE_DEBT",
}


class MigrationMapConsistencyTest(unittest.TestCase):
    def require_support(self):
        if migration_contract is None:
            self.skipTest("migration table parser support has not been implemented")
        return migration_contract

    def test_parser_support_exists(self) -> None:
        self.assertIsNotNone(
            migration_contract,
            "closed-world migration table parser support must be implemented",
        )

    def test_map_has_unique_ids_paths_and_one_allowed_disposition(self) -> None:
        support = self.require_support()
        rows = support.read_table(MIGRATION_MAP, "Stable ID", "Dirty ownership")
        self.assertEqual(len(rows), len({row["Stable ID"] for row in rows}))
        self.assertEqual(len(rows), len({row["Exact path"] for row in rows}))
        self.assertTrue(rows)
        self.assertTrue(
            all(row["Disposition"] in ALLOWED_DISPOSITIONS for row in rows)
        )

    def test_every_deletion_row_is_an_exact_mapped_row(self) -> None:
        support = self.require_support()
        mapped = {
            row["Stable ID"]: row
            for row in support.read_table(MIGRATION_MAP, "Stable ID", "Dirty ownership")
        }
        deletions = support.read_table(
            DELETION_MANIFEST, "Stable ID", "Replacement test"
        )
        self.assertEqual(len(deletions), len({row["Stable ID"] for row in deletions}))
        self.assertEqual(len(deletions), len({row["Exact path"] for row in deletions}))
        for deletion in deletions:
            self.assertNotRegex(deletion["Exact path"], r"[*?\[\]]")
            migration = mapped[deletion["Stable ID"]]
            self.assertEqual(deletion["Exact path"], migration["Exact path"])
            self.assertEqual(deletion["Pre-change SHA-256"], migration["Pre-change SHA-256"])
            self.assertEqual(deletion["Migrated destination"], migration["Destination"])
            self.assertEqual(deletion["Replacement test"], migration["Replacement test"])

    def test_deletion_manifest_is_the_complete_closed_world(self) -> None:
        support = self.require_support()
        mapped = support.read_table(MIGRATION_MAP, "Stable ID", "Dirty ownership")
        manifest_paths = {
            row["Exact path"]
            for row in support.read_table(
                DELETION_MANIFEST, "Stable ID", "Replacement test"
            )
        }
        expected_paths = {
            row["Exact path"]
            for row in mapped
            if support.is_expected_deletion(row)
        }
        self.assertEqual(expected_paths, manifest_paths)

    def test_completed_migration_has_real_destinations_tests_and_exact_deletions(self) -> None:
        support = self.require_support()
        mapped = support.read_table(MIGRATION_MAP, "Stable ID", "Dirty ownership")
        deletions = support.read_table(
            DELETION_MANIFEST, "Stable ID", "Replacement test"
        )
        missing_destinations = []
        missing_tests = []
        undeleted = []
        for row in mapped:
            destination = row["Destination"]
            if destination != "—" and not (ROOT / destination).exists():
                missing_destinations.append(destination)
            replacement = row["Replacement test"]
            if replacement != "—" and not (ROOT / replacement).is_file():
                missing_tests.append(replacement)
        for row in deletions:
            if (ROOT / row["Exact path"]).exists():
                undeleted.append(row["Exact path"])
        self.assertEqual([], sorted(set(missing_destinations)))
        self.assertEqual([], sorted(set(missing_tests)))
        self.assertEqual([], undeleted)

    def test_mandatory_behavior_is_not_deferred(self) -> None:
        support = self.require_support()
        rows = support.read_table(MIGRATION_MAP, "Stable ID", "Dirty ownership")
        mandatory_fragments = (
            "audit-ledger",
            "render_report",
            "sarif",
            "bundle",
            "dual_render",
            "installed_parity",
            "lifecycle_rehearsal",
            "/SKILL.md",
        )
        mandatory = [
            row
            for row in rows
            if any(fragment in row["Exact path"] for fragment in mandatory_fragments)
        ]
        self.assertTrue(mandatory)
        self.assertFalse(
            [row for row in mandatory if row["Disposition"] == "DEFER_EVIDENCE_DEBT"]
        )

    def test_installed_skill_inventory_excludes_non_product_artifacts(self) -> None:
        support = self.require_support()
        checker = getattr(support, "is_installed_inventory_path_allowed", None)
        self.assertTrue(callable(checker), "installed inventory policy must be explicit")
        rows = support.read_table(MIGRATION_MAP, "Stable ID", "Dirty ownership")
        installed_destinations = [
            row["Destination"]
            for row in rows
            if row["Destination"].startswith("plugins/shipworthy/skills/")
        ]
        self.assertFalse(
            [path for path in installed_destinations if not checker(path)],
            "installed skill destinations must deny tests, samples, fixtures, caches, "
            "and migration/lifecycle helpers; only three existing scripts are approved",
        )

    def test_installed_legacy_tests_and_sample_are_exact_deletions(self) -> None:
        support = self.require_support()
        deletion_paths = {
            row["Exact path"]
            for row in support.read_table(
                DELETION_MANIFEST, "Stable ID", "Replacement test"
            )
        }
        script_root = "plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/"
        expected = {
            script_root + "sample-report.json",
            script_root + "test_make_bundle.py",
            script_root + "test_render_report.py",
            script_root + "test_skill_contract.py",
            script_root + "test_to_sarif.py",
        }
        self.assertLessEqual(expected, deletion_paths)

    def test_dirty_state_ownership_matches_migration_map(self) -> None:
        support = self.require_support()
        reader = getattr(support, "read_dirty_ownership", None)
        self.assertTrue(callable(reader), "dirty ownership parser must be explicit")
        dirty = reader(DIRTY_STATE)
        mapped = {
            row["Exact path"]: row["Dirty ownership"]
            for row in support.read_table(MIGRATION_MAP, "Stable ID", "Dirty ownership")
        }
        for path, expected in dirty.items():
            if path in mapped:
                self.assertEqual(expected, mapped[path], path)
        mapped_dirty = {
            path: owner for path, owner in mapped.items() if owner != "CLEAN_TRACKED"
        }
        self.assertEqual(
            {path: owner for path, owner in dirty.items() if path in mapped},
            mapped_dirty,
        )

    def test_authoritative_baseline_covers_map_and_bytes(self) -> None:
        support = self.require_support()
        builder = getattr(support, "authoritative_baseline_inventory", None)
        self.assertTrue(callable(builder), "baseline inventory builder must be explicit")
        rows = support.read_table(MIGRATION_MAP, "Stable ID", "Dirty ownership")
        baseline = builder(ROOT, BASE_COMMIT, SNAPSHOT_INVENTORY)
        self.assertEqual(set(baseline), {row["Exact path"] for row in rows})
        for row in rows:
            path = row["Exact path"]
            self.assertTrue(support.is_safe_repository_path(path), path)
            self.assertRegex(row["Pre-change SHA-256"], r"^[0-9a-f]{64}$")
            self.assertEqual(support.stable_id(path), row["Stable ID"])
            self.assertEqual(baseline[path], row["Pre-change SHA-256"], path)

    def test_final_changed_deleted_reconciliation_is_closed(self) -> None:
        support = self.require_support()
        reconcile = getattr(support, "reconcile_final_state", None)
        self.assertTrue(callable(reconcile), "Task 7 reconciliation support is required")
        baseline = {"keep.txt": "a" * 64, "change.txt": "b" * 64, "delete.txt": "c" * 64}
        final = {
            "keep.txt": "a" * 64,
            "change.txt": "d" * 64,
            "declared/new.txt": "e" * 64,
        }
        result = reconcile(
            baseline,
            final,
            mapped_paths=set(baseline),
            deletion_paths={"delete.txt"},
            declared_new_paths={"declared/new.txt"},
        )
        self.assertEqual({"change.txt"}, result["changed"])
        self.assertEqual({"delete.txt"}, result["deleted"])
        self.assertEqual({"declared/new.txt"}, result["new"])
        with self.assertRaises(ValueError):
            reconcile(baseline, {"keep.txt": "a" * 64}, set(baseline), set(), set())
        with self.assertRaises(ValueError):
            reconcile(
                baseline,
                {**final, "undeclared.txt": "f" * 64},
                set(baseline),
                {"delete.txt"},
                {"declared/new.txt"},
            )
        with self.assertRaises(ValueError):
            reconcile(
                baseline,
                {**final, "../escape.txt": "f" * 64},
                set(baseline),
                {"delete.txt"},
                {"declared/new.txt", "../escape.txt"},
            )

    def test_actual_skill_trees_match_explicit_approved_inventory(self) -> None:
        support = self.require_support()
        reader = getattr(support, "read_path_inventory", None)
        auditor = getattr(support, "audit_installed_inventory", None)
        self.assertTrue(callable(reader) and callable(auditor))
        approved = reader(APPROVED_INSTALLED_INVENTORY)
        deletions = support.read_table(
            DELETION_MANIFEST, "Stable ID", "Replacement test"
        )
        skill_prefix = "plugins/shipworthy/skills/"
        pending = {
            row["Exact path"]
            for row in deletions
            if row["Exact path"].startswith(skill_prefix)
        }
        expected_pending = {
            "plugins/shipworthy/skills/ship-deep-review/shipworthy-compatibility.json",
            "plugins/shipworthy/skills/ship-product-workflows/shipworthy-compatibility.json",
            "plugins/shipworthy/skills/ship-readiness-orchestrator/shipworthy-compatibility.json",
            "plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/sample-report.json",
            "plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_make_bundle.py",
            "plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_render_report.py",
            "plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py",
            "plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_to_sarif.py",
            "plugins/shipworthy/skills/ship-workflow-clarity/shipworthy-compatibility.json",
        }
        self.assertEqual(expected_pending, pending)
        future_path = "plugins/shipworthy/skills/ship-readiness-orchestrator/references/manual-install-rollback.md"
        declared_future = set() if (ROOT / future_path).is_file() else {future_path}
        self.assertEqual(
            [],
            auditor(
                ROOT,
                approved,
                pending,
                mode="transitional",
                declared_future=declared_future,
            ),
        )
        final_issues = auditor(
            ROOT,
            approved,
            pending,
            mode="final",
            declared_future=declared_future,
        )
        if declared_future:
            missing_issue = next(issue for issue in final_issues if issue.startswith("missing approved files:"))
            self.assertTrue(all(path in missing_issue for path in declared_future))

    def test_dirty_ownership_rejects_duplicate_and_invalid_values(self) -> None:
        support = self.require_support()
        duplicate = """| Exact path | Hunk | Classification | Preservation rule |
| --- | --- | --- | --- |
| `a` | `H1` | `PREEXISTING_KEEP` | keep |

## Untracked paths: PREEXISTING_KEEP
- `a`
"""
        invalid = """| Exact path | Hunk | Classification | Preservation rule |
| --- | --- | --- | --- |
| `a` | `H1` | `INVALID` | keep |
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dirty.md"
            path.write_text(duplicate)
            with self.assertRaises(ValueError):
                support.read_dirty_ownership(path)
            path.write_text(invalid)
            with self.assertRaises(ValueError):
                support.read_dirty_ownership(path)

    def test_authoritative_baseline_rejects_inventory_and_archive_tampering(self) -> None:
        support = self.require_support()
        snapshot = SNAPSHOT_INVENTORY.parent
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory)
            for name in (
                "README.md",
                "untracked-files.sha256",
                "untracked-files.tar.gz",
            ):
                shutil.copy2(snapshot / name, copied / name)
            inventory = copied / "untracked-files.sha256"
            inventory.write_text(inventory.read_text().replace("a", "b", 1))
            with self.assertRaises(ValueError):
                support.authoritative_baseline_inventory(ROOT, BASE_COMMIT, inventory)

        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory)
            for name in (
                "README.md",
                "untracked-files.sha256",
                "untracked-files.tar.gz",
            ):
                shutil.copy2(snapshot / name, copied / name)
            archive = copied / "untracked-files.tar.gz"
            archive.write_bytes(archive.read_bytes() + b"tamper")
            with self.assertRaises(ValueError):
                support.authoritative_baseline_inventory(
                    ROOT, BASE_COMMIT, copied / "untracked-files.sha256"
                )


if __name__ == "__main__":
    unittest.main()

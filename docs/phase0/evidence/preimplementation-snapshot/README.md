# Preimplementation dirty-state snapshot

This directory preserves the worktree state that existed before Task 1 ran any
potentially writing test command. It is intentionally outside every production
path expected to be removed by the four-skill migration.

## Git identity and exact captured status

- Base commit: `27e8425baa0cda1f64985eb361dfd90ef0752b6b`
- Branch: `feature/lean-host-native-shipworthy`
- Status command: `git status --short --untracked-files=normal`

```text
 M .claude-plugin/marketplace.json
 M .gitignore
 M ARCHITECTURE.md
 M plugins/shipworthy/.claude-plugin/plugin.json
 M plugins/shipworthy/skills/ship-product-workflows/SKILL.md
 M plugins/shipworthy/skills/ship-product-workflows/references/living-audit-ledger.md
 M plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md
 M plugins/shipworthy/skills/ship-readiness-orchestrator/references/exports-and-ci.md
 M plugins/shipworthy/skills/ship-readiness-orchestrator/references/final-report-contract.md
 M plugins/shipworthy/skills/ship-readiness-orchestrator/references/lane-prompts.md
 M plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/make_bundle.py
 M plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py
?? .python-version
?? docs/phase0/
?? docs/strategy/
?? docs/superpowers/plans/2026-07-15-lean-host-native-shipworthy.md
?? docs/superpowers/plans/2026-07-17-four-self-contained-skills.md
?? docs/superpowers/specs/
?? plugins/shipworthy/shipworthy-compatibility.json
?? plugins/shipworthy/skills/ship-deep-review/shipworthy-compatibility.json
?? plugins/shipworthy/skills/ship-product-workflows/shipworthy-compatibility.json
?? plugins/shipworthy/skills/ship-product-workflows/templates/audit-ledger.md
?? plugins/shipworthy/skills/ship-readiness-orchestrator/references/browser-evidence-routing.md
?? plugins/shipworthy/skills/ship-readiness-orchestrator/references/host-execution-recipes.md
?? plugins/shipworthy/skills/ship-readiness-orchestrator/shipworthy-compatibility.json
?? plugins/shipworthy/skills/ship-workflow-clarity/shipworthy-compatibility.json
?? pyproject.toml
?? schemas/
?? scripts/
?? src/
?? tests/
?? uv.lock
```

## Snapshot artifacts

| Artifact | SHA-256 | Contents |
| --- | --- | --- |
| `tracked-dirty.patch` | `b9da20a8836748844023b6b9655d5d2a8bced132a82dc88f7c0c3afb53c7494a` | Exact `git diff --binary --no-ext-diff` for all 12 pre-existing tracked modifications; 32,843 bytes. |
| `untracked-files.tar.gz` | `63299f65ee7d61d092f4554ed0e72c1c54920844edc3f232cae08c025d8f613b` | Binary-capable archive of all 92 pre-existing untracked files, excluding this snapshot directory itself. |
| `untracked-files.sha256` | `f81e99c9b3d2f557e3c4ec76b52336120c2860b3ad2f4c17014f4195de48ee78` | Sorted SHA-256, byte count, and exact path inventory for those 92 files. |

## Recovery

Apply the tracked patch only to a clean checkout of the captured base revision:

```sh
git apply --binary docs/phase0/evidence/preimplementation-snapshot/tracked-dirty.patch
```

Restore untracked files into a separate recovery checkout first, never blindly
over the live worktree:

```sh
tar -xzf docs/phase0/evidence/preimplementation-snapshot/untracked-files.tar.gz
```

The inventory was verified against a fresh temporary extraction before any test
execution. The snapshot is evidence only; no reset or checkout operation was
used to create it.

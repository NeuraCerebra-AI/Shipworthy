# Pre-existing dirty-state ownership

Captured before Task 1 test execution. The authoritative binary recovery copy is
`docs/phase0/evidence/preimplementation-snapshot/`. These classifications govern
preservation; they do not authorize production migration or deletion in Task 1.

Captured Git identity: base commit
`27e8425baa0cda1f64985eb361dfd90ef0752b6b`, branch
`feature/lean-host-native-shipworthy`, with the exact preimplementation
`git status --short --untracked-files=normal` recorded in the protected snapshot
README. The status comprised 12 tracked modifications and 20 untracked status
entries expanding to 92 exact untracked files in the SHA-256 inventory.

## Tracked modified path ownership

This path-level table is unique by exact path and is the authoritative ownership
join used by the migration-map consistency test. The hunk table below preserves
the finer-grained classifications.

| Exact path | Classification | Preservation rule |
| --- | --- | --- |
| `.claude-plugin/marketplace.json` | `PREEXISTING_MIGRATE` | Preserve intent while later removing package-only compatibility metadata. |
| `.gitignore` | `PREEXISTING_MIGRATE` | Preserve both KEEP hunks and reconcile the package-only hunk. |
| `ARCHITECTURE.md` | `PREEXISTING_MIGRATE` | Preserve host-native claims while rewriting package claims. |
| `plugins/shipworthy/.claude-plugin/plugin.json` | `PREEXISTING_MIGRATE` | Preserve intent while later removing package-only compatibility metadata. |
| `plugins/shipworthy/skills/ship-product-workflows/SKILL.md` | `PREEXISTING_KEEP` | Keep the browser evidence behavior and make it self-contained. |
| `plugins/shipworthy/skills/ship-product-workflows/references/living-audit-ledger.md` | `PREEXISTING_KEEP` | Keep the canonical ledger section contract. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md` | `PREEXISTING_MIGRATE` | Preserve browser/host behavior while removing optional-core framing. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/references/exports-and-ci.md` | `PREEXISTING_KEEP` | Keep the passive export/CI boundary. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/references/final-report-contract.md` | `PREEXISTING_KEEP` | Keep final-report evidence requirements. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/references/lane-prompts.md` | `PREEXISTING_KEEP` | Keep lane evidence selection and proof ceilings. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/make_bundle.py` | `PREEXISTING_MIGRATE` | Preserve deterministic behavior in the existing exporter. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py` | `PREEXISTING_MIGRATE` | Move assertions to repository-only tests. |

## Tracked modified hunk inventory

| Exact path | Hunk ID / captured range | Existing hunk | Classification | Preservation rule |
| --- | --- | --- | --- | --- |
| `.claude-plugin/marketplace.json` | `H01 @@ -14,0 +15,8 @@` | Added optional-core compatibility metadata. | `PREEXISTING_MIGRATE` | Preserve intent while later removing package-only compatibility metadata. |
| `.gitignore` | `H02 @@ -24,0 +25 @@` | Unignored the recovered source audit-ledger template. | `PREEXISTING_KEEP` | Keep the narrow source-template exception. |
| `.gitignore` | `H03 @@ -25,0 +27,2 @@` | Unignored protected Phase 0 evidence and its ledger. | `PREEXISTING_KEEP` | Keep protected evidence reachable. |
| `.gitignore` | `H04 @@ -34,0 +38,5 @@` | Added package/build artifact ignores. | `PREEXISTING_MIGRATE` | Reconcile package-only ignores after package removal. |
| `ARCHITECTURE.md` | `H05 @@ -116,0 +117,65 @@` | Added optional-core/migration tooling plus lean host-native evidence flow. | `PREEXISTING_MIGRATE` | Preserve host-native evidence claims while rewriting package claims. |
| `plugins/shipworthy/.claude-plugin/plugin.json` | `H06 @@ -3,0 +4,8 @@` | Added optional-core compatibility metadata. | `PREEXISTING_MIGRATE` | Preserve intent while later removing package-only compatibility metadata. |
| `plugins/shipworthy/skills/ship-product-workflows/SKILL.md` | `H07 @@ -53,0 +54,7 @@` | Added bounded native/Playwright browser route and skill-only behavior. | `PREEXISTING_KEEP` | Keep the behavior and make it self-contained. |
| `plugins/shipworthy/skills/ship-product-workflows/references/living-audit-ledger.md` | `H08 @@ -95,17 +95,17 @@` | Replaced the generic list with canonical named ledger sections. | `PREEXISTING_KEEP` | Keep exact section-contract improvement. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md` | `H09 @@ -87,0 +88,4 @@` | Added browser routing and optional-core-independent behavior. | `PREEXISTING_MIGRATE` | Preserve browser behavior while removing optional-core framing. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md` | `H10 @@ -199,0 +204,2 @@` | Added browser-routing and host-execution reference loads. | `PREEXISTING_MIGRATE` | Preserve both loads while making their destinations self-contained. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/references/exports-and-ci.md` | `H11 @@ -16,0 +17,8 @@` | Added passive host-execution boundary. | `PREEXISTING_KEEP` | Keep export/CI non-runner boundary. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/references/final-report-contract.md` | `H12 @@ -28,0 +29 @@` | Added browser-routing proof-boundary fields. | `PREEXISTING_KEEP` | Keep final-report evidence requirements. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/references/lane-prompts.md` | `H13 @@ -50,0 +51,2 @@` | Added native-versus-Playwright selection and proof ceilings. | `PREEXISTING_KEEP` | Keep lane evidence boundary. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/make_bundle.py` | `H14 @@ -21,0 +22,9 @@` | Extracted stable bundle README bytes. | `PREEXISTING_MIGRATE` | Preserve exact bundle content in the existing installed exporter. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/make_bundle.py` | `H15 @@ -63,0 +73,41 @@` | Added deterministic ZIP timestamp/info and in-memory bundle builder. | `PREEXISTING_MIGRATE` | Preserve deterministic bundle behavior. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/make_bundle.py` | `H16 @@ -107,24 +157,7 @@` | Routed CLI output through deterministic bundle bytes and retained summary. | `PREEXISTING_MIGRATE` | Preserve CLI behavior in the existing installed exporter. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py` | `H17 @@ -13,0 +14,5 @@` | Added browser/host and four-skill path constants. | `PREEXISTING_MIGRATE` | Move assertions to repository-only tests. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py` | `H18 @@ -38,0 +44,3 @@` | Loaded new browser/host/product contract inputs. | `PREEXISTING_MIGRATE` | Move contract inputs to repository-only tests. |
| `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py` | `H19 @@ -121,0 +130,44 @@` | Added browser, host execution, independent-skill, and HTML checks. | `PREEXISTING_MIGRATE` | Preserve all assertions in replacement repository tests. |

No tracked hunk is classified `UNRELATED_DO_NOT_TOUCH`. The mixed architecture
and orchestrator hunks are conservative `PREEXISTING_MIGRATE`: later work must
separate claims rather than overwriting the entire hunk.

## Untracked paths: PREEXISTING_KEEP

- `docs/phase0/evidence/lean-host-native-red-green-ledger.md`
- `docs/phase0/legacy-transform-retirement.md`
- `docs/strategy/shipworthy-skill-first-roadmap-2026-07-15.md`
- `plugins/shipworthy/skills/ship-product-workflows/templates/audit-ledger.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/browser-evidence-routing.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/host-execution-recipes.md`

These are durable evidence, strategy, recovered template, or host-native skill
content. Later edits may integrate them but must preserve their substantive
contracts.

## Untracked paths: PREEXISTING_MIGRATE

- `.python-version`
- `pyproject.toml`
- `uv.lock`
- `plugins/shipworthy/shipworthy-compatibility.json`
- `plugins/shipworthy/skills/ship-deep-review/shipworthy-compatibility.json`
- `plugins/shipworthy/skills/ship-product-workflows/shipworthy-compatibility.json`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/shipworthy-compatibility.json`
- `plugins/shipworthy/skills/ship-workflow-clarity/shipworthy-compatibility.json`
- `schemas/v1/browser-evidence-envelope.schema.json`
- `schemas/v1/readiness-ledger.schema.json`
- `schemas/v1/report-input.schema.json`
- `scripts/clean_wheel_smoke.py`
- `scripts/generate_sbom_locked.py`
- `scripts/preflight_install.py`
- `scripts/run_python_target.py`
- `scripts/validate_local.py`
- `scripts/write_build_manifest.py`
- `scripts/write_phase0_receipts.py`
- `scripts/write_python_target_matrix.py`
- `scripts/write_uv_toolchain.py`
- `src/shipworthy/__init__.py`
- `src/shipworthy/phase0_receipts.py`
- `src/shipworthy/shipworthy-compatibility.json`
- `src/shipworthy/adapters/__init__.py`
- `src/shipworthy/adapters/importers/__init__.py`
- `src/shipworthy/adapters/importers/_evidence_normalization.py`
- `src/shipworthy/adapters/importers/browser_evidence.py`
- `src/shipworthy/adapters/importers/legacy_readiness.py`
- `src/shipworthy/adapters/importers/playwright_report.py`
- `src/shipworthy/adapters/reporting/__init__.py`
- `src/shipworthy/adapters/reporting/bundle.py`
- `src/shipworthy/adapters/reporting/compat_loader.py`
- `src/shipworthy/adapters/reporting/html.py`
- `src/shipworthy/adapters/reporting/html_safety.py`
- `src/shipworthy/adapters/reporting/projection.py`
- `src/shipworthy/adapters/reporting/sarif.py`
- `src/shipworthy/domain/__init__.py`
- `src/shipworthy/domain/browser_evidence.py`
- `src/shipworthy/domain/contracts.py`
- `src/shipworthy/domain/entities.py`
- `src/shipworthy/domain/enums.py`
- `src/shipworthy/domain/evidence_attachment.py`
- `src/shipworthy/domain/ids.py`
- `src/shipworthy/migration/__init__.py`
- `src/shipworthy/migration/dual_render.py`
- `src/shipworthy/migration/installed_parity.py`
- `src/shipworthy/migration/lifecycle_rehearsal.py`
- `tests/conftest.py`
- `tests/contract/test_browser_evidence_contract_v1.py`
- `tests/contract/test_readiness_contract_v1.py`
- `tests/domain/test_evidence_attachment.py`
- `tests/fixtures/browser_evidence/valid-all-channels.json`
- `tests/fixtures/browser_evidence/valid-deterministic-replay.json`
- `tests/fixtures/browser_evidence/valid-exploratory.json`
- `tests/fixtures/legacy/readiness-v0.json`
- `tests/fixtures/playwright/basic-report.json`
- `tests/fixtures/playwright/screenshot.png`
- `tests/fixtures/playwright/trace.zip`
- `tests/fixtures/playwright/unnamed-project-report.json`
- `tests/fixtures/v1/confirmed-blocker-ledger.json`
- `tests/fixtures/v1/hostile-path-ledger.json`
- `tests/fixtures/v1/incomplete-ledger.json`
- `tests/fixtures/v1/inconsistent-blocker-ledger.json`
- `tests/fixtures/v1/lying-green-ledger.json`
- `tests/fixtures/v1/mismatched-gate-ledger.json`
- `tests/fixtures/v1/missing-artifact-ledger.json`
- `tests/fixtures/v1/pure-action-first-report-input.json`
- `tests/fixtures/v1/unknown-enum-ledger.json`
- `tests/importers/test_browser_evidence.py`
- `tests/importers/test_legacy_readiness.py`
- `tests/importers/test_playwright_report.py`
- `tests/integration/test_audit_ledger_template.py`
- `tests/integration/test_compatibility_preflight.py`
- `tests/integration/test_host_execution_boundary.py`
- `tests/integration/test_packaging_gate.py`
- `tests/integration/test_phase0_receipts.py`
- `tests/integration/test_runtime_matrix_contract.py`
- `tests/migration/test_dual_render.py`
- `tests/migration/test_installed_parity.py`
- `tests/migration/test_lifecycle_rehearsal.py`
- `tests/migration/test_retirement_criteria.py`
- `tests/reporting/test_browser_evidence_reporting.py`
- `tests/reporting/test_reporting_projection.py`

`PREEXISTING_MIGRATE` means the behavior/evidence must be accounted for before
the package-era path is removed; it does not mean the path itself survives.

## Untracked paths: UNRELATED_DO_NOT_TOUCH

- `docs/superpowers/plans/2026-07-15-lean-host-native-shipworthy.md`
- `docs/superpowers/plans/2026-07-17-four-self-contained-skills.md`
- `docs/superpowers/specs/2026-07-17-four-self-contained-skills-design.md`

These coordination artifacts are outside implementation ownership. Task 1 did
not read the plan files and will not edit any of these three paths. The design
spec is also conservatively protected because ownership was not required to
complete this evidence-only boundary task.

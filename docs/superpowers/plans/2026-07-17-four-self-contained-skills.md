# Four Self-Contained Shipworthy Skills Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the unfinished `shipworthy-core` package boundary with four self-contained Shipworthy skills that preserve proven evidence, reporting, browser-intake, parity, and rollback behavior through concise references and small dependency-free scripts.

**Architecture:** Keep the four existing skills as the complete installed product. Move schemas and detailed contracts into skill references, move only deterministic user-facing transformations into `ship-readiness-orchestrator/scripts/`, keep development assurance in repository tests, and then remove Python package/build/compatibility infrastructure. Native Codex and Claude plugin managers own installation; manual copying remains an explicit fallback.

**Tech Stack:** Markdown skills, JSON/JSON Schema references, the three existing Python 3.11+ standard-library output scripts invoked in isolated mode, direct Python contract tests, synthetic temporary installation fixtures, existing Claude plugin metadata, and a new Codex plugin manifest. No Pydantic, Hatch, uv package, wheel, service, database, or network dependency.

**Execution status (2026-07-17):** Implemented through Task 8 under the user's
two-batch workflow. The authoritative RED/GREEN, review-repair, final artifact,
parity, rollback, and proof-ceiling receipts are in
`docs/phase0/evidence/lean-host-native-red-green-ledger.md`. Individual boxes
below preserve the approved plan text rather than acting as a second execution
ledger.

---

## Product and scope guardrails

Preserve:

- all four skill names, descriptions, triggers, and independent usability;
- the flagship `are we shipworthy?` routing behavior;
- the canonical readiness ledger and conservative proof/gate rules;
- native-browser-first and optional existing-Playwright evidence routing;
- mandatory self-contained HTML output; SARIF and the evidence bundle remain
  deterministic optional exports when a compatible Python runtime is available;
- legacy input support, dual-render evidence, installed-copy parity, temporary
  manual backup/failed-upgrade rollback rehearsal, and explicit evidence debt;
- the four legacy suites and their established 120 + 174 + 22 + 17 baseline;
- no network, credentials, external provider integration, browser launching from
  scripts, target mutation, installed-copy writes, commit, or push;
- independent installation of each skill, with a bounded orchestrator fallback
  when the other Shipworthy skills are absent;

Remove:

- `shipworthy-core` as a package or product concept;
- `src/shipworthy/`, root package schemas, build scripts, packaging gates,
  `.python-version`, `pyproject.toml`, and `uv.lock` after migration;
- Pydantic models and package/skill compatibility negotiation;
- wheel, SBOM, package-resource, and multi-runtime package proof;
- any roadmap language suggesting a CLI, daemon, API, portal, persistence layer,
  MCP server, hosted runner, or provider platform.

Do not begin implementation until the baseline mapping in Task 1 is reviewed.

## Target file map

### Installed product

- `plugins/shipworthy/.codex-plugin/plugin.json` — Codex plugin identity and skill root.
- `plugins/shipworthy/.claude-plugin/plugin.json` — Claude plugin identity and skill root.
- `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md` — flagship orchestration and resource routing.
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/*.json` — canonical ledger, report-input, and browser-evidence contracts.
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/*.md` — compatibility-free evidence, migration, and execution contracts.
- Existing `render_report.py`, `to_sarif.py`, and `make_bundle.py` — deterministic output utilities, tightened rather than replaced.
- The other three skill directories — instructions, references, templates, and metadata only unless a failing test demonstrates a script is required.

No other installed script is pre-approved. Validation and legacy/browser/
Playwright normalization begin as reference-driven agent workflows. A proposed
script must first fail an isolated-skill acceptance test and pass the necessity
gate in Task 3.

### Repository-only assurance

- `tests/__init__.py` and `tests/skill_product/__init__.py` — stable direct-unittest discovery without an installed project package.
- `tests/skill_product/test_manifest_and_install.py` — pre-removal manifest/manual-installer contract.
- `tests/skill_product/test_four_skill_boundary.py` — final four-skill/no-core structure contract; intentionally RED until Task 7.
- `tests/skill_product/test_independent_skills.py` — four isolated-skill copies and representative behavior.
- `tests/skill_product/test_stdlib_scripts.py` — installed-inventory, AST, runtime discovery, and isolated execution checks.
- `tests/skill_product/test_ledger_contract.py` — schema and hostile input behavior.
- `tests/skill_product/support/schema_subset.py` — repository-only generic evaluator for exactly the JSON Schema keywords used; fails on unsupported keywords.
- `tests/skill_product/test_evidence_imports.py` — browser, Playwright, and legacy fixtures.
- `tests/skill_product/test_dual_render.py` — legacy/v1 comparison and evidence debt.
- `tests/skill_product/test_installed_parity.py` — synthetic Codex/Claude copies.
- `tests/skill_product/test_lifecycle_rehearsal.py` — temporary manual-install backup, failed-upgrade rollback, and exact restoration.
- `tests/fixtures/` — retained synthetic inputs and expected outputs.

Tests must run directly with the standard library test runner or as standalone
scripts. They must not require installation of a project package.

The installed plugin inventory must deny `test_*.py`, samples, fixtures, cache
directories, migration-retirement helpers, and lifecycle helpers. Existing
tests currently stored inside the orchestrator skill move to repository-only
tests before the installed-copy parity baseline is finalized.

## Chunk 1: Freeze the boundary and migration map

### Task 1: Capture the baseline and classify every core artifact

**Files:**

- Create: `docs/phase0/four-skill-migration-map.md`
- Create: `docs/phase0/four-skill-deletion-manifest.md`
- Create: `docs/phase0/preexisting-dirty-state.md`
- Create: `tests/skill_product/test_four_skill_boundary.py`
- Modify: `docs/phase0/evidence/lean-host-native-red-green-ledger.md`

- [ ] **Step 1: Capture a recoverable raw snapshot of the dirty worktree before running any command that may write.**

  Save `git diff --binary` using Git's output option and archive every untracked
  file with metadata into a protected evidence directory excluded from all
  mutation/deletion paths. Record SHA-256 digests for the patch and archive.
  This snapshot is recovery evidence, not permission to reset or overwrite the
  user's work.

- [ ] **Step 2: Record the current branch, status, and exact pre-migration test totals without changing product files.**

  Run:

  ```bash
  git status --short --branch
  PYTHONDONTWRITEBYTECODE=1 python3 plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py
  PYTHONDONTWRITEBYTECODE=1 python3 plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_render_report.py
  PYTHONDONTWRITEBYTECODE=1 python3 plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_to_sarif.py
  PYTHONDONTWRITEBYTECODE=1 python3 plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_make_bundle.py
  ```

  Expected: the legacy suites pass at the established baseline. Record actual
  totals rather than forcing the expected numbers if the worktree already added
  intentional tests.

- [ ] **Step 3: Classify the pre-existing dirty worktree before touching overlapping files.**

  Record every modified/untracked path, a SHA-256 for each untracked file, and a
  patch-id or hunk-level description for each tracked modification. Mark each
  hunk `PREEXISTING_KEEP`, `PREEXISTING_MIGRATE`, or `UNRELATED_DO_NOT_TOUCH`.
  Stop on any overlapping hunk whose ownership cannot be classified.

- [ ] **Step 4: Inventory every tracked and untracked path affected by Tasks 2–7, not only the package directories.**

  For each file, record one destination in `four-skill-migration-map.md`:
  `SKILL_INSTRUCTION`, `REFERENCE`, `SKILL_SCRIPT`, `REPO_TEST`, `REMOVE_PACKAGE_ONLY`, or `DEFER_EVIDENCE_DEBT`.

  Give every row a stable artifact/behavior ID, exactly one disposition,
  pre-change digest, destination, and replacement test. Reject duplicate or
  unmapped IDs. `DEFER_EVIDENCE_DEBT` requires explicit user approval and is
  forbidden for ledger, HTML, SARIF, bundle, parity, independent-skill, and
  manual-rollback behavior.

- [ ] **Step 5: Create an exact deletion manifest.**

  List every path Task 7 may delete, its pre-removal digest, reason, migrated
  destination, and green replacement test. Task 7 must refuse to delete a path
  absent from this manifest; directory-wide wildcard deletion is prohibited.

- [ ] **Step 6: Write a failing four-skill boundary test.**

  The test must assert the desired end state:

  ```python
  import unittest

  class FourSkillBoundaryTests(unittest.TestCase):
      def test_installed_product_is_exactly_four_skills(self):
          self.assertEqual(discovered_skill_names(), {
              "ship-readiness-orchestrator",
              "ship-deep-review",
              "ship-product-workflows",
              "ship-workflow-clarity",
          })

      def test_no_separate_core_product_boundary(self):
          self.assertFalse((ROOT / "src" / "shipworthy").exists())
          self.assertFalse((ROOT / "pyproject.toml").exists())
          self.assertEqual(list(ROOT.glob("**/shipworthy-compatibility.json")), [])
  ```

- [ ] **Step 7: Run the boundary test and capture RED.**

  ```bash
  python3 -m unittest -v tests.skill_product.test_four_skill_boundary
  ```

  Expected: FAIL because the core/package boundary still exists.

- [ ] **Step 8: Assert the legacy baseline has not decreased.**

  Totals must be at least 120 + 174 + 22 + 17. Higher totals are recorded.
  Any lower total blocks migration unless every removed/renamed case is mapped
  and explicitly approved.

- [ ] **Step 9: Review the migration map, deletion manifest, dirty-state ledger, and recoverable snapshot before implementation.**

  Verify that every previously proven Phase 0 Task 1–7 behavior has an explicit destination and
  that no file is removed merely because it currently lives under `src/`.

**Acceptance:** The old architecture and every planned mutation are fully
accounted for, pre-existing hunks are protected, the desired four-skill boundary
is intentionally RED, and no production behavior has been deleted.

## Chunk 2: Move contracts and deterministic behavior into the skills

### Task 2: Relocate schemas and contracts into orchestrator references

**Files:**

- Create: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/readiness-ledger.schema.json`
- Create: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/report-input.schema.json`
- Create: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/browser-evidence-envelope.schema.json`
- Create: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/ledger-validation-contract.md`
- Create: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/evidence-import-contract.md`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md`
- Test: `tests/skill_product/test_ledger_contract.py`
- Create: `tests/skill_product/support/schema_subset.py`

- [ ] **Step 1: Write failing tests that require all three schemas to be local to the orchestrator skill and referenced from `SKILL.md`.**

  Implement a repository-only generic schema-subset oracle that reads the JSON
  Schema documents as the single structural authority. Support exactly the
  keywords present in those documents and fail if a schema introduces an
  unsupported keyword. Do not reproduce field names/enums in validator code.

- [ ] **Step 2: Run the focused test and record RED.**

  ```bash
  python3 -m unittest -v tests.skill_product.test_ledger_contract
  ```

- [ ] **Step 3: Copy the proven schemas byte-for-byte into the skill reference directory before changing their content.**

- [ ] **Step 4: Freeze golden validation results for every retained legacy and v1 fixture, then produce a field-by-field semantic schema diff.**

  Keep schema version `1` only if old valid ledgers remain valid and meaning is
  unchanged. Otherwise add a deterministic migration rule and version gate.
  Every intentional difference must have a golden fixture and evidence-debt rule.

- [ ] **Step 5: Move detailed validation, producer, lineage, proof-ceiling, and input-mapping rules into concise references.**

  Remove package-version and supported-core-range concepts. Keep schema version,
  artifact producer, transformation operation, and feature fields only where
  they describe evidence rather than an installable product.

  Keep `docs/phase0/legacy-transform-retirement.md` as the sole authoritative
  retirement document. Do not duplicate retirement policy inside an installed
  skill; the skill contains only the still-supported legacy input mapping.

- [ ] **Step 6: Add concise conditional routing to `SKILL.md`.**

  Example:

  ```markdown
  Before rendering or importing structured evidence, read
  `references/ledger-validation-contract.md`. Read
  `references/evidence-import-contract.md` only when browser, Playwright, or
  legacy structured input is present.
  ```

- [ ] **Step 7: Re-run golden legacy/v1 validation through the schema-subset oracle and the focused test; record GREEN.**

**Acceptance:** Detailed contracts load only when needed, schemas travel with
the skill, and no core-install compatibility concept remains.

### Task 3: Prove the minimum installed-script boundary

**Files:**

- Create: `tests/skill_product/test_stdlib_scripts.py`
- Create: `tests/skill_product/test_evidence_imports.py`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/ledger-validation-contract.md`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/evidence-import-contract.md`
- Create: `docs/phase0/evidence/agent-pressure-tests.md`
- Preserve/move fixtures under: `tests/fixtures/`

- [ ] **Step 1: Move all existing `test_*.py` files and `sample-report.json` out of the installed skill directory into repository-only tests/fixtures without changing their assertions.**

  Add an installed-inventory denylist for tests, samples, fixtures, caches,
  migration-retirement helpers, lifecycle helpers, and build metadata.

- [ ] **Step 2: Write mechanical tests for reference completeness, schema authority, fixture coverage, installed-file closure, and forbidden behaviors.**

  Standard-library tests do not claim to execute an agent. They prove that every
  required input class and invariant has one discoverable instruction/schema and
  that no installed resource reaches outside the isolated skill copy.

- [ ] **Step 3: Run behavioral pressure tests through fresh development subagents when the host provides them.**

  Give each fresh agent only an isolated synthetic skill copy, one fixture, and
  a representative prompt. Do not leak the expected answer. Record the raw
  transcript and output, then compare canonical identity, action, proof, gate,
  digest, limitations, and evidence debt against a checked-in golden oracle.
  Include remote-as-local artifacts, unsafe paths, duplicate IDs, corrupt
  digests, oversized inputs, and unknown versions.

  This is development evaluation authorized for this plan, not a production
  provider integration. If fresh-agent execution is unavailable, label
  instruction behavior `NOT_PROVEN`; do not let static tests stand in for it and
  do not add a script solely to manufacture a GREEN result.

- [ ] **Step 4: Run the mechanical tests without adding scripts and capture the result.**

  ```bash
  python3 -m unittest -v \
    tests.skill_product.test_stdlib_scripts \
    tests.skill_product.test_evidence_imports
  ```

- [ ] **Step 5: For every behavior that fails a real fresh-agent pressure test, complete a script-necessity record before proposing code.**

  Record: caller, frequency, exact failure consequence, why a schema/reference is
  insufficient, smallest alternative, production line/complexity budget,
  command interface, exit codes, size/depth/file-count limits, stdout/stderr
  rules, overwrite/atomicity policy, and retirement criterion.

- [ ] **Step 6: Prefer reference/schema repairs. Add an installed script only when a reproducible fresh-agent failure demonstrates deterministic code is required.**

  If a validator is approved, schemas remain authoritative for structural
  fields/enums; code may own bounded parsing and named cross-field invariants
  only. Add schema-to-invariant conformance tests so two mechanical truths cannot
  drift.

- [ ] **Step 7: Add AST checks for every installed script.**

  Reject third-party imports and capabilities involving network clients,
  package installation, browser launch, credentials, databases, daemons,
  dynamic `eval`/`exec`, or shell execution.

- [ ] **Step 8: Re-run mechanical tests and available pressure tests; record GREEN or explicit approved evidence debt with the evidence type stated.**

  Mandatory ledger/report behavior cannot be deferred. Browser/Playwright
  normalization may remain agent-driven if its conservative proof ceiling and
  artifact lineage are preserved.

**Acceptance:** Installed scripts remain the proven minimum rather than a hidden
core; one-time migration and development verification stay outside installed
copies.

### Task 4: Consolidate rendering, SARIF, and bundle behavior in existing scripts

**Files:**

- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/render_report.py`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/to_sarif.py`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/make_bundle.py`
- Move/modify: their existing direct test scripts under `tests/skill_product/`
- Create: `tests/skill_product/test_dual_render.py`

- [ ] **Step 1: Freeze each existing script's command line, exit codes, stdout/stderr behavior, input limits, overwrite behavior, and golden outputs before modifying it.**

  Then add failing tests for v1 lineage, browser evidence, evidence debt,
  canonical counts, HTML safety, SARIF identity, bundle digests, atomic output,
  and byte-stable output.

  Record the existing aggregate source lines and AST node/function counts. Any
  individual or aggregate growth above 10% or 100 source lines, whichever is
  smaller, requires the same necessity record as a new script and an independent
  lean review. Shared domain models, generic validators, and importer frameworks
  are prohibited inside the retained scripts.

- [ ] **Step 2: Add a failing dual-render comparison proving legacy and v1 outputs preserve identity, action, proof, gate, counts, HTML, SARIF, bundle manifest, and artifact lineage.**

  Differences without a defined transform rule must be emitted as evidence debt.

- [ ] **Step 3: Run focused and legacy rendering tests and record RED.**

  ```bash
  python3 tests/skill_product/test_render_report_legacy.py
  python3 tests/skill_product/test_to_sarif_legacy.py
  python3 tests/skill_product/test_make_bundle_legacy.py
  python3 -m unittest -v tests.skill_product.test_dual_render
  ```

- [ ] **Step 4: Port only the proven projection, HTML-safety, SARIF, and bundle behavior from `src/shipworthy/adapters/reporting/` into the existing scripts.**

  Keep their public input/output behavior stable. Split a script only if it
  cannot retain one clear responsibility; do not create a shared framework.

- [ ] **Step 5: Remove dynamic `sys.path` mutation between sibling scripts.**

  Use explicit data exchange or safe loading from the resolved skill directory;
  never import from the audited repository.

- [ ] **Step 6: Execute every production entry point from an unrelated temporary directory under a contaminated environment using the discovered compatible Python 3.11+ command and isolated mode.**

  Test Unicode paths, spaces, missing runtime behavior, `python3`/`python`/`py -3`
  discovery as applicable, and an instruction-only fallback that still produces
  the mandatory HTML report. When no compatible runtime exists, label
  deterministic HTML execution, SARIF, and evidence-bundle generation
  `NOT_PROVEN`; SARIF and bundle exports are optional, not silently fabricated.

- [ ] **Step 7: Re-run focused and legacy tests and record GREEN.**

**Acceptance:** The mandatory report pipeline remains deterministic and
self-contained, and the installed product still contains only skill-owned code.

## Chunk 3: Preserve lifecycle assurance without shipping lifecycle machinery

### Task 5: Convert parity and rollback into repository-only temporary-fixture tests

**Files:**

- Create: `tests/skill_product/test_installed_parity.py`
- Create: `tests/skill_product/test_lifecycle_rehearsal.py`
- Create: `tests/skill_product/test_independent_skills.py`
- Modify: `docs/phase0/legacy-transform-retirement.md`

- [ ] **Step 1: Write failing tests that build synthetic Codex and Claude installations from the repository plugin.**

  Compare every approved skill body, production script, reference, template,
  asset, and manifest. Report missing, stale, modified, and unexpected files;
  reject installed tests, samples, fixtures, caches, and development helpers.

- [ ] **Step 2: Write four static isolated-skill tests.**

  Install one skill at a time and resolve every local reference/template/script.
  Trace mechanical file access to prove the skill does not require another
  Shipworthy directory. Static tests do not claim behavioral independence.

- [ ] **Step 3: Forward-test each isolated skill through a fresh development subagent when available.**

  Give the agent only the isolated skill, a representative prompt, and a
  disposable fixture. Capture raw output and filesystem trace. The orchestrator
  must perform a bounded standalone audit with explicit evidence debt when
  sub-skills are absent rather than stopping or fetching them. If fresh-agent
  evaluation is unavailable, label behavioral independence `NOT_PROVEN` while
  retaining static file-closure proof.

- [ ] **Step 4: Write failing manual-installer lifecycle tests that invoke the real `install.sh` under a temporary HOME.**

  Cover backup-before-upgrade, rejection of an invalid/malformed skill fixture,
  failed-copy rollback, evidence preservation, and exact prior-state restoration.
  The manual fallback does not implement uninstall; record it
  `NOT_IMPLEMENTED — use the native plugin manager or remove an explicitly named
  manual skill directory`. Do not call this native plugin-manager proof.

- [ ] **Step 5: Patch all home-directory variables to temporary roots and add a sentinel assertion proving no path under real `~/.codex`, `~/.agents`, or `~/.claude` was opened for writing.**

- [ ] **Step 6: Run the mechanical tests and capture RED.**

  ```bash
  python3 -m unittest -v \
    tests.skill_product.test_installed_parity \
    tests.skill_product.test_lifecycle_rehearsal \
    tests.skill_product.test_independent_skills
  ```

- [ ] **Step 7: Implement only repository test support and real manual-installer behavior; do not add installed lifecycle code to any skill.**

- [ ] **Step 8: Re-run all mechanical tests and available behavioral forward tests; record the evidence type explicitly.**

**Acceptance:** Exact-copy, backup, upgrade-failure rollback, and exact restoration
claims are proven for the advanced manual installer. Static independence is
proven for all four skills; behavioral independence is claimed only when fresh
agent forward tests pass. Manual uninstall is `NOT_IMPLEMENTED`, and native
manager lifecycle remains externally owned and separately labeled.

## Chunk 4: Native distribution and removal of the package boundary

### Task 6: Make native plugin installation the public workflow

**Files:**

- Create: `plugins/shipworthy/.codex-plugin/plugin.json`
- Create: `.agents/plugins/marketplace.json`
- Modify: `plugins/shipworthy/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `README.md`
- Modify: `install.sh`
- Move/modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py` to repository-only tests
- Test: `tests/skill_product/test_manifest_and_install.py`

- [ ] **Step 1: Write failing tests for valid Codex and Claude plugin/marketplace manifests, exactly four bundled skills, and current documented installation paths.**

- [ ] **Step 2: Write failing installer tests requiring `--target codex|claude|both`, refusing ambiguous invocation, using `$HOME/.agents/skills` for Codex manual installation, and operating only under a temporary HOME.**

- [ ] **Step 3: Add contract checks requiring `/reload-plugins` for Claude and prohibiting a Documents-folder or target-repository clone recommendation.**

- [ ] **Step 4: Run focused tests and record RED.**

- [ ] **Step 5: Add the Codex plugin and marketplace manifests, reconcile Claude metadata, and rewrite the README happy path around native plugin installation.**

  Keep manual copying under an advanced fallback. Do not mention a core, CLI,
  Python package, Pydantic, uv, pipx, or additional runtime installation.

- [ ] **Step 6: Refactor `install.sh` to require an explicit target and preserve timestamped backups.**

- [ ] **Step 7: Re-run focused tests and record GREEN.**

- [ ] **Step 8: When installed Codex/Claude CLIs expose a local, no-network plugin workflow, run native smoke tests under isolated temporary HOME/config/cache roots.**

  Verify marketplace discovery, cache contents, exactly four discovered skills,
  reload/new-session behavior, and a representative invocation. If a host CLI
  or isolated local workflow is unavailable, record that host's native install,
  reload, upgrade, and uninstall behavior `NOT_PROVEN`; synthetic copying and
  `install.sh` must not be substituted as native proof.

**Acceptance:** Static manifest/catalog readiness is proven for both hosts and
the manual fallback is explicit and cannot silently choose the wrong host.
Operational native installation is `PROVEN` separately for each host only after
its isolated host smoke test passes; otherwise report `NATIVE INSTALL NOT_PROVEN`
for that host.

### Task 7: Remove core/package infrastructure after migration tests are green

**Files:**

- Delete only: exact paths enumerated in `docs/phase0/four-skill-deletion-manifest.md`
- Modify: `.gitignore`
- Modify: `ARCHITECTURE.md`
- Modify: `docs/strategy/shipworthy-skill-first-roadmap-2026-07-15.md`

- [ ] **Step 1: Confirm Tasks 2–6 focused suites are GREEN before deleting anything. Keep `test_four_skill_boundary.py` RED for only the enumerated package paths.**

- [ ] **Step 2: Use the migration map to verify each deletion is marked `REMOVE_PACKAGE_ONLY` or already has a green replacement test.**

- [ ] **Step 3: Run and snapshot the complete pre-deletion gate.**

  Run the full new suite, all four legacy suites, isolated-skill matrix,
  dual-render comparison, installed parity, manual lifecycle rehearsal, compile,
  forbidden-behavior scans, and artifact digest generation. No deletion may
  proceed unless this entire gate is green and the legacy totals have not fallen.

- [ ] **Step 4: Remove only manifest-listed package files with a reviewable patch. Preserve every pre-existing dirty hunk and the recovered `templates/audit-ledger.md`.**

- [ ] **Step 5: Update architecture documentation to show only four skills, their local resources, native host tools, target-owned commands, and the canonical ledger/report pipeline.**

- [ ] **Step 6: Mark wheel reproduction, SBOM execution, locked-package proof, and core package-runtime-matrix proof `NOT_APPLICABLE — package removed`.**

  Installed-script runtime remains applicable: record exact Python/OS variants
  exercised and mark unexercised variants `NOT_PROVEN`.

- [ ] **Step 7: Run the four-skill boundary test and capture GREEN.**

  ```bash
  python3 -m unittest -v tests.skill_product.test_four_skill_boundary
  ```

- [ ] **Step 8: Rerun the identical pre-deletion gate and compare totals and artifact digests. Any unexplained difference blocks completion.**

**Acceptance:** No installable core/package remains, while every retained product
behavior is owned by one of the four skills or by repository-only assurance.

## Chunk 5: Verification and independent review

### Task 8: Run the complete release gate

**Files:**

- Modify: `docs/phase0/evidence/lean-host-native-red-green-ledger.md`
- Modify: `docs/phase0/four-skill-migration-map.md`

- [ ] **Step 1: Run every new package-free test together.**

  ```bash
  python3 -m unittest discover -s tests/skill_product -p 'test_*.py' -v
  ```

- [ ] **Step 2: Run the four migrated legacy suites from their repository-only locations.**

  ```bash
  python3 tests/skill_product/test_skill_contract_legacy.py
  python3 tests/skill_product/test_render_report_legacy.py
  python3 tests/skill_product/test_to_sarif_legacy.py
  python3 tests/skill_product/test_make_bundle_legacy.py
  ```

- [ ] **Step 3: Compile and execute all installed Python entry points through the runtime/isolation matrix.**

  ```bash
  find plugins/shipworthy/skills -path '*/scripts/*.py' -type f -print0 \
    | xargs -0 -n1 python3 -m py_compile
  ```

  Execution—not compilation alone—must cover every entry point from a temporary
  working directory with spaces/Unicode and a contaminated environment. Record
  exact Python and OS versions exercised; use the documented instruction-only
  fallback when no compatible interpreter exists.

- [ ] **Step 4: Run hygiene and forbidden-behavior scans.**

  ```bash
  git diff --check
  git ls-files -co --exclude-standard -z | xargs -0 rg -n \
    "pydantic|hatchling|shipworthy-core|sqlite3|requests\.|httpx|aiohttp|playwright\.(sync_api|async_api)|mcp server|daemon|portal|credential store"
  rg -n "(^|[[:space:]])(from|import)[[:space:]]+shipworthy([[:space:].]|$)|project\.scripts|console_scripts" .
  find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .ruff_cache -o -name build -o -name dist \) -prune -print
  ```

  Review documentation-only matches explicitly rather than blindly requiring no
  textual mention of rejected architecture. Also assert that the installed
  product inventory exactly matches the approved manifest and contains no test,
  sample, fixture, migration, build, or lifecycle files.

- [ ] **Step 5: Run all tests with temporary Codex- and Claude-style fixture roots and confirm no real installed-copy writes.**

- [ ] **Step 6: Dispatch an independent specification-compliance review against the approved design and this plan. Repair findings with focused RED/GREEN evidence.**

- [ ] **Step 7: Dispatch a separate independent code-quality and workflow-clarity review. Repair findings and rerun affected tests.**

- [ ] **Step 8: Record final exact totals, artifact digests, dual-render differences, parity result, rollback state hashes, and remaining evidence debt.**

- [ ] **Step 9: Reconcile the final changed/deleted path set against the closed-world migration map and deletion manifest.**

  Fail if any final path lacks exactly one disposition, pre-change digest,
  destination, passing replacement test, and authorized debt status. Additions
  caused by review repairs or conditionally approved scripts must be mapped
  before acceptance.

- [ ] **Step 10: Compare the final worktree against `preexisting-dirty-state.md`; prove every pre-existing hunk remains or has its approved migrated replacement.**

- [ ] **Step 11: Remove only generated cache/build noise. Do not commit or push.**

**Acceptance:** The repository proves a four-skill, no-package product boundary,
static independent file closure, deterministic local output utilities, exact
synthetic parity, and manual-installer rollback without Phase 1 platform work.
Behavioral skill independence and operational native installation are claimed
only for the hosts actually exercised; all other host claims remain explicitly
`NOT_PROVEN`.

## Final stop report

Stop after Task 8 and report:

- the exact four-skill installed file inventory;
- which former core behaviors became references, skill scripts, repo-only tests,
  removals, or evidence debt;
- the exact new and legacy test totals;
- HTML, SARIF, bundle, lineage, parity, and rollback evidence;
- confirmation that both host manifests require no core package, plus separate
  per-host operational native-install proof or `NATIVE INSTALL NOT_PROVEN`;
- any Python-runtime variants not freshly exercised as `NOT_PROVEN`;
- wheel/SBOM/package-runtime claims as `NOT_APPLICABLE — package removed`;
- why Phase 1 and all platform work remain unstarted.

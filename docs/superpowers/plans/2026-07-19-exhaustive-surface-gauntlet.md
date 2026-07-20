# Exhaustive Surface Gauntlet Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a bounded adversarial UI and native-Codex acceptance harness, measure the current Shipworthy skills against a private oracle, then make the smallest skill/schema/report changes needed to prevent missed controls and false exhaustive closure.

**Architecture:** Keep Shipworthy as four self-contained skills. Add a repository-only Gauntlet fixture, oracle, comparator, and prepare/finalize harness; extend the existing canonical `path_frontier` rather than creating new ledgers; derive a compact human-readable Product Coverage section from canonical rows. The primary task implements directly; native Codex subagents are used only as oracle-blind audit subjects.

**Tech Stack:** Python 3.11+ standard library, HTML/CSS/JavaScript, JSON Schema, direct `unittest`, existing Shipworthy renderer and schema-subset evaluator, native Codex macOS subagents, no external packages or network-dependent fixture behavior.

**Specification:** `docs/superpowers/specs/2026-07-19-exhaustive-surface-gauntlet-design.md`

---

## Scope and file map

Repository-only test infrastructure:

- `tests/skill_product/gauntlet/app/server.py` — deterministic local fixture server and resettable API.
- `tests/skill_product/gauntlet/app/index.html` — bounded adversarial product shell.
- `tests/skill_product/gauntlet/app/app.js` — deterministic UI states and seeded defects.
- `tests/skill_product/gauntlet/app/styles.css` — responsive/mobile-only and visually plausible layout.
- `tests/skill_product/gauntlet/app/product-docs/README.md` — declared behavior, including one promised-but-missing path.
- `tests/skill_product/gauntlet/app/product-tests/contract.md` — source-visible behavior expectations for full-evidence mode.
- `tests/skill_product/gauntlet/app/fixtures/seed.json` — fixed roles, records, flags, and initial state.
- `tests/skill_product/gauntlet/app/roles.json` — synthetic member/admin credentials and capabilities.
- `tests/skill_product/gauntlet/oracle/*.json` — versioned private surface and defect truth.
- `tests/skill_product/gauntlet/oracle/*.schema.json` — oracle contracts.
- `tests/skill_product/gauntlet/prompts/*.md` — native Codex runtime-only/full-evidence test briefs.
- `tests/skill_product/gauntlet/compare_agent_result.py` — semantic normalization and oracle comparison.
- `tests/skill_product/gauntlet/run_acceptance.py` — prepare/finalize/cleanup lifecycle only; never dispatches agents.
- `tests/skill_product/gauntlet/redact_evidence.py` — repository-only validated export of bounded durable evidence; never changes authoritative run artifacts.
- `tests/skill_product/support/frontier_validation.py` — repository-only cross-field frontier checks; never copied into installed skills.
- `tests/skill_product/gauntlet/acceptance-result.schema.json` — authoritative result contract.
- `tests/skill_product/test_gauntlet_fixture.py` — fixture/reset/API tests.
- `tests/skill_product/test_gauntlet_oracle.py` — oracle/schema/semantic-key tests.
- `tests/skill_product/test_gauntlet_comparator.py` — PASS/FAIL/REVIEW_REQUIRED comparison tests.
- `tests/skill_product/test_gauntlet_acceptance.py` — harness lifecycle/result/cleanup tests.
- `docs/phase0/evidence/gauntlet-current-skill-baseline.md` — compact RED diagnostic; no raw build/cache noise.

Installed product changes, only after baseline RED:

- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/readiness-ledger.schema.json`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/report-input.schema.json`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/evidence-state.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/lane-prompts.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/final-report-contract.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/visual-html-report.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md`
- `plugins/shipworthy/skills/ship-product-workflows/SKILL.md`
- `plugins/shipworthy/skills/ship-product-workflows/references/path-discovery-and-coverage.md`
- `plugins/shipworthy/skills/ship-product-workflows/templates/coverage-map.json`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/render_report.py`

An installed `validate_frontier.py` is not pre-approved. Add it only if the native baseline demonstrates structural/count drift that schemas and instructions cannot prevent, and record the necessity gate first.

## Chunk 1: Build the measuring instrument and capture RED

### Task 1: Versioned oracle and semantic comparator

**Files:**

- Create: `tests/skill_product/gauntlet/oracle/surface-oracle.schema.json`
- Create: `tests/skill_product/gauntlet/oracle/expected-defects.schema.json`
- Create: `tests/skill_product/gauntlet/oracle/surface-oracle.json`
- Create: `tests/skill_product/gauntlet/oracle/expected-defects.json`
- Create: `tests/skill_product/gauntlet/compare_agent_result.py`
- Create: `tests/skill_product/test_gauntlet_oracle.py`
- Create: `tests/skill_product/test_gauntlet_comparator.py`

- [ ] **Step 1: Write RED tests for semantic normalization and oracle validity.**

  Cover NFKC/case/separator normalization, URL path normalization, intent/feature/surface/control/transition keys, same-label Save disambiguation, aliases, allowed dispositions, decoys, and effect matching.

  ```python
  def test_same_label_controls_have_distinct_semantic_keys(self):
      first = semantic_key({"kind": "control", "surface_key": "surface:project:edit:member:desktop", "identity": "Save", "control_type": "button", "disambiguator": "persist"})
      second = semantic_key({"kind": "control", "surface_key": "surface:project:edit:member:desktop", "identity": "Save", "control_type": "button", "disambiguator": "visual-only"})
      self.assertNotEqual(first, second)
  ```

- [ ] **Step 2: Run the focused tests and record RED.**

  ```bash
  python3 -m unittest -v tests.skill_product.test_gauntlet_oracle tests.skill_product.test_gauntlet_comparator
  ```

  Expected: import/file failures because the oracle and comparator do not exist.

- [ ] **Step 3: Implement the minimal versioned normalizer and oracle schemas.**

  Keep comparison functions pure: `normalize_token`, `normalize_route`, `derive_semantic_key`, `load_and_validate_oracle`, `compare_frontier`. Return structured packets; do not render HTML or manage processes here.

- [ ] **Step 4: Seed the frozen oracle.**

  Include the eighteen approved adversarial cases, mode-specific dispositions, materiality, aliases, evidence minima, negative controls, and seeded defect matchers. Do not expose oracle paths in agent prompts.

- [ ] **Step 5: Add comparator PASS, FAIL, and REVIEW_REQUIRED fixtures.**

  Prove mode filtering, invalid terminal dispositions, missing transition
  before/after evidence, a safe control marked `covered` without its required
  evidence, duplicate semantic rows, summary/row count drift, JSON/HTML closure
  contradiction, and material oracle misses fail. Prove an unclassified extra
  row requires review, a complete supported frontier passes, and discoveries
  from separate incomplete runs are never aggregated.

- [ ] **Step 6: Run focused GREEN and commit.**

  ```bash
  python3 -m unittest -v tests.skill_product.test_gauntlet_oracle tests.skill_product.test_gauntlet_comparator
  git add tests/skill_product/gauntlet/oracle tests/skill_product/gauntlet/compare_agent_result.py tests/skill_product/test_gauntlet_oracle.py tests/skill_product/test_gauntlet_comparator.py
  git commit -m "Add Gauntlet oracle comparator"
  ```

### Task 2: Deterministic adversarial fixture

**Files:**

- Create: `tests/skill_product/gauntlet/app/server.py`
- Create: `tests/skill_product/gauntlet/app/index.html`
- Create: `tests/skill_product/gauntlet/app/app.js`
- Create: `tests/skill_product/gauntlet/app/styles.css`
- Create: `tests/skill_product/gauntlet/app/product-docs/README.md`
- Create: `tests/skill_product/gauntlet/app/product-tests/contract.md`
- Create: `tests/skill_product/gauntlet/app/fixtures/seed.json`
- Create: `tests/skill_product/gauntlet/app/roles.json`
- Create: `tests/skill_product/test_gauntlet_fixture.py`

- [ ] **Step 1: Write RED server/reset/API tests.**

  Assert random-port startup, `/health`, deterministic `/api/state`, reset token enforcement, failed persistence endpoint, misleading-success response, stale-session transition, and idempotent shutdown.

- [ ] **Step 2: Run RED.**

  ```bash
  python3 -m unittest -v tests.skill_product.test_gauntlet_fixture
  ```

- [ ] **Step 3: Implement the smallest standard-library server.**

  Use `ThreadingHTTPServer`, explicit route handlers, in-memory state copied from `seed.json`, UTF-8 JSON, localhost binding, and a test-supplied reset token. Deny arbitrary path traversal and never contact external hosts.

- [ ] **Step 4: Implement the bounded UI.**

  Add only oracle-backed surfaces and controls: avatar settings, mobile invite, admin export, context menu, keyboard palette, deep import route, prerequisite publish, empty-state action, invalid-input recovery, stale-session recovery, duplicate Save behavior, misleading success, reload loss, missing cancellation, avoided delete, false affordance, unexplained disabled control, and unavailable flag.

- [ ] **Step 5: Add oracle-to-fixture traceability assertions.**

  For every required oracle item, assert at least one legitimate runtime or
  full-evidence discovery hook exists in fixture source/docs/state. Assert
  negative controls are noninteractive and the false-affordance defect is both
  visually present and noninteractive. Fail orphaned oracle rows and un-oracled
  material fixture controls.

- [ ] **Step 6: Enforce fixture size boundaries.**

  Keep `server.py` and `app.js` independently understandable, targeting no more
  than 300 logical lines each. If either exceeds that boundary, split state/API
  behavior or surface controllers by responsibility before proceeding.

- [ ] **Step 7: Prove deterministic fixture behavior and commit.**

  ```bash
  python3 -m unittest -v tests.skill_product.test_gauntlet_fixture tests.skill_product.test_gauntlet_oracle
  git add tests/skill_product/gauntlet/app tests/skill_product/test_gauntlet_fixture.py
  git commit -m "Add adversarial Gauntlet fixture"
  ```

### Task 3: Native Codex prepare/finalize harness

**Files:**

- Create: `tests/skill_product/gauntlet/acceptance-result.schema.json`
- Create: `tests/skill_product/gauntlet/run_acceptance.py`
- Create: `tests/skill_product/gauntlet/redact_evidence.py`
- Create: `tests/skill_product/gauntlet/prompts/runtime-only.md`
- Create: `tests/skill_product/gauntlet/prompts/full-evidence.md`
- Create: `tests/skill_product/gauntlet/README.md`
- Create: `tests/skill_product/test_gauntlet_acceptance.py`

- [ ] **Step 1: Write RED lifecycle tests.**

  Cover `prepare`, `finalize`, and idempotent `cleanup`; randomized controller
  paths; rejection of `--product-source` in runtime-only; required
  `--product-source` in full-evidence; sanitized full-evidence copy; server
  health/reset; artifact validation; explicit native dispatch status
  (`completed`, `unavailable`, `failed`, `timeout`), native agent ID, coordinator
  failure details; PASS/FAIL/NOT_PROVEN/REVIEW_REQUIRED exit mapping; timeout/
  failure retention; cleanup residual failure; schema-valid fallback `FAIL`
  after an invalid result draft; atomic final result writing; and safe evidence
  export that copies only status-allowed files, redacts manifest-declared secrets
  and host roots, validates copied JSON, reports source/destination SHA-256, and
  never mutates authoritative artifacts.

- [ ] **Step 2: Run RED.**

  ```bash
  python3 -m unittest -v tests.skill_product.test_gauntlet_acceptance
  ```

- [ ] **Step 3: Implement lifecycle-only commands.**

  `prepare` accepts optional `--product-source` only for full-evidence and
  prints a JSON run manifest. `finalize` accepts
  `--native-dispatch-status completed|unavailable|failed|timeout`,
  `--native-agent-id`, `--agent-output`, and optional bounded
  `--coordinator-diagnostic`; it calls the comparator only for `completed`,
  retains artifacts, cleans transient paths, validates the result, atomically
  renames it, and exits 0/1/2/3. An invalid draft is replaced by a schema-valid
  internal-error `FAIL`. `cleanup` may be called repeatedly. The script must not
  launch Codex or Claude. Keep `run_acceptance.py` and
  `compare_agent_result.py` near 250 logical lines each; split lifecycle/result
  construction or normalization/matching if either grows beyond one reviewable
  responsibility.

  `redact_evidence.py` accepts run manifest, source, destination, and status. For
  PASS it allowlists the six durable artifacts; for `NOT_PROVEN` it allowlists
  only result and log. It copies to a new destination, replaces only exact
  manifest-known reset token/controller root/user-home values with fixed labels,
  reparses all copied JSON, prints before/after hashes plus replacement counts,
  and fails on residual secret values or unexpected files.

- [ ] **Step 4: Write the two agent briefs.**

  Both briefs authorize goal mode and parallel native subagents and require
  reading exactly:

  ```text
  plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md
  plugins/shipworthy/skills/ship-deep-review/SKILL.md
  plugins/shipworthy/skills/ship-product-workflows/SKILL.md
  plugins/shipworthy/skills/ship-workflow-clarity/SKILL.md
  ```

  Prohibit oracle/test-tree discovery, require one coordinated runtime driver,
  and demand canonical ledger/frontier JSON plus HTML. Runtime-only supplies no
  private evidence: it supplies only the URL, accounts, safe boundary, reset
  conditions/token, output path, and explicit path allowlist. Full-evidence adds
  the sanitized source/docs/tests copy to those same operational inputs.

- [ ] **Step 5: Run GREEN, compile, and commit.**

  ```bash
  python3 -m unittest -v tests.skill_product.test_gauntlet_acceptance
  python3 -m py_compile tests/skill_product/gauntlet/app/server.py tests/skill_product/gauntlet/compare_agent_result.py tests/skill_product/gauntlet/run_acceptance.py tests/skill_product/gauntlet/redact_evidence.py
  git add tests/skill_product/gauntlet tests/skill_product/test_gauntlet_acceptance.py
  git commit -m "Add native Codex Gauntlet harness"
  ```

### Task 4: Capture the current-skill behavioral RED

**Files:**

- Create: `docs/phase0/evidence/gauntlet-current-skill-baseline.md`
- Create only if compact and non-sensitive: `docs/phase0/evidence/gauntlet-current-skill-baseline.json`

- [ ] **Step 1: Prepare runtime-only mode without modifying production skills.**

  Run `python3 tests/skill_product/gauntlet/run_acceptance.py prepare --mode runtime-only --skills-source plugins/shipworthy/skills --output <temp-output>` and read the emitted manifest.

- [ ] **Step 2: Launch one fresh native Codex test subject.**

  Use a native Codex subagent with `fork_turns: none`. Give it the runtime-only
  brief, exact four skill paths, target URL/accounts, safe boundary, allowed
  paths, reset conditions/token, and evidence output. Do not mention oracle
  identities or expected defects. Record the returned native agent ID.

- [ ] **Step 3: Finalize and compare.**

  ```bash
  python3 tests/skill_product/gauntlet/run_acceptance.py finalize \
    --run-manifest <temp-output>/run-manifest.json \
    --native-dispatch-status completed \
    --native-agent-id <agent-id> \
    --agent-output <temp-output>/agent-evidence
  ```

  Expected RED: nonzero `FAIL` or `REVIEW_REQUIRED` from at least one material
  miss, unsupported closure, structural incompatibility, or evidence gap. If the
  current skill unexpectedly passes, preserve that evidence and skip unjustified
  production changes.

- [ ] **Step 4: Record diagnostic causes, not only counts.**

  Classify each miss as discovery instruction, control census, role/state/device variation, source/runtime reconciliation, frontier structure, verifier closure, report visibility, or native-tool limitation. Record whether structural drift justifies an installed validator under the existing necessity gate.

- [ ] **Step 5: Commit compact RED evidence.**

  Verify and clean first:

  ```bash
  python3 -m json.tool <temp-output>/acceptance-result.json >/dev/null
  python3 tests/skill_product/gauntlet/run_acceptance.py cleanup --run-manifest <temp-output>/run-manifest.json
  git diff --check
  git add docs/phase0/evidence/gauntlet-current-skill-baseline.md
  test ! -f docs/phase0/evidence/gauntlet-current-skill-baseline.json || git add docs/phase0/evidence/gauntlet-current-skill-baseline.json
  git commit -m "Record current Shipworthy Gauntlet baseline"
  ```

  Do not commit raw host caches, sessions, screenshots containing unrelated
  data, or temporary server state. If dispatch fails or times out, call
  `cleanup`, preserve the authoritative failure result, and do not start
  production changes until a valid behavioral RED or unexpected PASS is
  available.

## Chunk 2: Improve Shipworthy from the observed failures

**Entry gate:** Before Task 5, map every proposed production edit to one or more
Task 4 diagnostic causes in `gauntlet-current-skill-baseline.md`. If the baseline
unexpectedly passed, stop this chunk and make no production changes. Omit any
schema, instruction, or renderer change that has no observed diagnostic cause;
the Gauntlet infrastructure may remain as the regression proof.

### Task 5: Canonical frontier schema and repository validation

**Files:**

- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/readiness-ledger.schema.json`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/report-input.schema.json`
- Modify: `plugins/shipworthy/skills/ship-product-workflows/templates/coverage-map.json`
- Create: `tests/skill_product/test_frontier_contract.py`
- Create: `tests/skill_product/support/frontier_validation.py`
- Modify: `tests/skill_product/support/schema_subset.py` to resolve bounded same-directory file `$ref` values used by the canonical frontier.
- Create conditionally: `docs/phase0/evidence/gauntlet-installed-validator-necessity.md`

- [ ] **Step 1: Write RED schema/invariant tests from baseline failures.**

  Require unique stable row IDs; permitted intent→feature→surface→control→
  transition lineage; kind-specific fields; versioned semantic keys;
  observations and discovery passes with `shipworthy-methods-v1`; covered
  controls/transitions with attempt evidence; a path or explicit terminal
  disposition for every feature; qualifying zero-yield passes; resolvable
  evidence references under a supplied evidence root; preserved reconciliation
  differences; rejection of unresolved material terminal states; objective
  closure derivation; machine-facing finding fields; exact caller-summary/row
  count reconciliation; and legacy input compatibility. Also prove the schema
  subset evaluator resolves the exact same-directory canonical frontier `$ref`
  while rejecting remote URLs, absolute paths, and `..` traversal.

- [ ] **Step 2: Run RED and record the baseline-linked failures.**

  ```bash
  python3 -m unittest -v tests.skill_product.test_frontier_contract
  ```

  Expected: failures only for invariants mapped to Task 4 diagnostic causes;
  preexisting legacy fixtures remain accepted.

- [ ] **Step 3: Minimally extend canonical schemas/templates.**

  `readiness-ledger.schema.json` owns complete frontier rows, observations,
  discovery passes, reconciliation differences, and closure fields.
  `report-input.schema.json` consumes it with the exact reference
  `readiness-ledger.schema.json#/$defs/path_frontier` and defines no second
  frontier shape. `coverage-map.json` is only the authoring example/template.
  Do not add fixture-specific defect enums or duplicate frontier structure.

- [ ] **Step 4: Add repository-only cross-field validation.**

  Put pure cross-field checks in
  `tests/skill_product/support/frontier_validation.py`; it owns lineage, stable
  identity, counts, closure precedence, observation independence,
  reconciliation, terminal-state, and evidence-root checks. Keep JSON Schema
  keyword evaluation in `schema_subset.py`. The validator accepts explicit data
  and evidence-root paths, performs no I/O outside that root, and never enters
  installed copies. Extend `schema_subset.py` only with bounded resolution of a
  relative schema filename plus local JSON Pointer: resolve from the referring
  schema's directory, require the resolved file to remain in that directory,
  reject schemes/absolute paths/traversal, cache loaded JSON, and retain the
  existing local-`#` behavior. It performs no network access.

- [ ] **Step 5: Run GREEN and existing ledger tests.**

  ```bash
  python3 -m unittest -v tests.skill_product.test_frontier_contract tests.skill_product.test_ledger_contract tests.skill_product.test_v1_outputs
  ```

- [ ] **Step 6: Apply the installed-validator necessity gate.**

  Only if Task 4 proved agent-side structural/count drift that prevents a
  trustworthy user report, create
  `docs/phase0/evidence/gauntlet-installed-validator-necessity.md` naming the
  caller, invocation frequency, failure consequence, smaller instruction/schema
  alternative, maximum reviewable size, and retirement criterion. Verify it
  with:

  ```bash
  test -f docs/phase0/evidence/gauntlet-installed-validator-necessity.md
  rg -n "Caller|Frequency|Failure consequence|Smaller alternative|Size budget|Retirement" docs/phase0/evidence/gauntlet-installed-validator-necessity.md
  ```

  Stop and write a separate bounded plan before adding any installed script.
  Otherwise record “installed validator not justified” in the baseline and
  continue with repository-only validation.

- [ ] **Step 7: Commit.**

  ```bash
  git add plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/readiness-ledger.schema.json plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/report-input.schema.json plugins/shipworthy/skills/ship-product-workflows/templates/coverage-map.json tests/skill_product/test_frontier_contract.py tests/skill_product/support/frontier_validation.py
  git diff --quiet -- tests/skill_product/support/schema_subset.py || git add tests/skill_product/support/schema_subset.py
  test ! -f docs/phase0/evidence/gauntlet-installed-validator-necessity.md || git add docs/phase0/evidence/gauntlet-installed-validator-necessity.md
  git diff --quiet -- docs/phase0/evidence/gauntlet-current-skill-baseline.md || git add docs/phase0/evidence/gauntlet-current-skill-baseline.md
  git commit -m "Strengthen canonical path frontier"
  ```

### Task 6: Discovery, census, and verifier behavior

**Files:**

- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/evidence-state.md`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/lane-prompts.md`
- Modify: `plugins/shipworthy/skills/ship-product-workflows/SKILL.md`
- Modify: `plugins/shipworthy/skills/ship-product-workflows/references/path-discovery-and-coverage.md`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/pressure-tests.md`
- Modify: `tests/skill_product/test_skill_contract_legacy.py`
- Create: `tests/skill_product/test_exhaustive_surface_contract.py`

- [ ] **Step 1: Write RED behavioral-contract assertions tied to Task 4 causes.**

  Test one frontier; material-state control census; the four canonical method
  families; rejection of relabeled details as independent families; two
  qualifying zero-yield passes; runtime plus independent reconciliation at both
  feature and surface level; exercising each safe control once per materially
  different behavior; direct observation or explicit disposition for every
  material control; semantic lineage; closure-state precedence; and verifier
  rejection of unresolved, inconsistent, or single-source exhaustive closure.

- [ ] **Step 2: Run RED.**

  ```bash
  python3 -m unittest -v tests.skill_product.test_exhaustive_surface_contract
  ```

  Expected: baseline-linked failures for missing census, independent discovery,
  reconciliation, and/or no-false-closure language; no unrelated activation or
  legacy skill-contract failure.

- [ ] **Step 3: Make the smallest instruction/reference changes.**

  `ship-product-workflows/SKILL.md` owns the user-facing requirement to census
  and exercise material controls. `path-discovery-and-coverage.md` owns method
  families, role/state/device variation, reconciliation, and zero-yield rules.
  `ship-readiness-orchestrator/SKILL.md` owns orchestration and the no-false-
  closure gate. `evidence-state.md` owns canonical row/closure semantics.
  `lane-prompts.md` gives agents bounded collection prompts. `pressure-tests.md`
  owns the adversarial regression scenario. Do not add a new public skill,
  lane, crawler, graph engine, or duplicate ledger. Keep `ship-deep-review`
  protocol unchanged except its existing orchestrator handoff.

- [ ] **Step 4: Add the Gauntlet scenario to pressure tests and run GREEN.**

  ```bash
  python3 -m unittest -v tests.skill_product.test_exhaustive_surface_contract
  python3 tests/skill_product/test_skill_contract_legacy.py
  ```

  Expected legacy aggregate: no regression from the current 139-pass baseline plus intentional new assertions.

- [ ] **Step 5: Commit.**

  ```bash
  git add plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md plugins/shipworthy/skills/ship-readiness-orchestrator/references/evidence-state.md plugins/shipworthy/skills/ship-readiness-orchestrator/references/lane-prompts.md plugins/shipworthy/skills/ship-readiness-orchestrator/references/pressure-tests.md plugins/shipworthy/skills/ship-product-workflows/SKILL.md plugins/shipworthy/skills/ship-product-workflows/references/path-discovery-and-coverage.md tests/skill_product/test_skill_contract_legacy.py tests/skill_product/test_exhaustive_surface_contract.py
  git commit -m "Require exhaustive material surface closure"
  ```

### Task 7: Human-readable Product Coverage HTML

**Files:**

- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/render_report.py`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/visual-html-report.md`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/final-report-contract.md`
- Modify: `tests/skill_product/test_render_report_legacy.py`
- Create: `tests/skill_product/test_gauntlet_report.py`
- Create: `tests/skill_product/fixtures/gauntlet-report-input.json`

- [ ] **Step 1: Write RED renderer tests.**

  Assert action-first sections remain first; Product Coverage uses only
  `closed_multi_source`, `incomplete`, `single_source`, `blocked`, or
  `static_only`; it shows the closure reason, exact feature/surface/control/
  transition counts, role summary, and discovery-family summary. Assert one
  compact feature row appears; separate bounded `<details>` sections cover
  control evidence, role/state/device coverage, blocked/avoided actions,
  discovery reconciliation, and the frontier manifest; large manifests link
  JSON instead of dumping rows; inconsistent caller totals fail; percentages
  always show their exact denominator; no JavaScript is introduced; legacy
  inputs retain bounded “coverage not recorded”; and hostile text is escaped.

- [ ] **Step 2: Run RED.**

  ```bash
  python3 -m unittest -v tests.skill_product.test_gauntlet_report
  ```

  Expected: baseline-linked failures because Product Coverage and its strict
  reconciliation/presentation rules are not yet implemented; existing escaping
  and action-first assertions continue to pass.

- [ ] **Step 3: Add pure frontier summarization and rendering.**

  `render_report.py` owns pure projection, derived counts, consistency failure,
  and escaped HTML and must remain under 800 logical lines; simplify helpers if
  necessary rather than adding another installed module. `visual-html-report.md`
  owns visual hierarchy and the five detail categories.
  `final-report-contract.md` owns required data, closure vocabulary,
  exact-denominator rules, and JSON/HTML consistency. Keep the main report
  decision-focused and use native `<details>` for secondary proof.

- [ ] **Step 4: Run renderer GREEN and legacy suite.**

  ```bash
  python3 -m unittest -v tests.skill_product.test_gauntlet_report
  python3 tests/skill_product/test_render_report_legacy.py
  ```

- [ ] **Step 5: Generate and visually inspect one report in the Codex app.**

  ```bash
  python3 plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/render_report.py tests/skill_product/fixtures/gauntlet-report-input.json /tmp/shipworthy-gauntlet-report.html
  test -s /tmp/shipworthy-gauntlet-report.html
  ```

  Expected: findings and actions remain above Product Coverage; the coverage
  summary is scannable; all five technical categories are collapsed by default;
  no control-row wall or vague score appears. Delete the temporary HTML after
  inspection with `rm -f /tmp/shipworthy-gauntlet-report.html`.

- [ ] **Step 6: Commit.**

  ```bash
  git add plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/render_report.py plugins/shipworthy/skills/ship-readiness-orchestrator/references/visual-html-report.md plugins/shipworthy/skills/ship-readiness-orchestrator/references/final-report-contract.md tests/skill_product/test_render_report_legacy.py tests/skill_product/test_gauntlet_report.py tests/skill_product/fixtures/gauntlet-report-input.json
  git commit -m "Add human-readable Product Coverage report"
  ```

## Chunk 3: Native Codex proof and final verification

### Task 8: Fresh post-fix native Codex acceptance

**Files:**

- Modify: `docs/phase0/evidence/gauntlet-current-skill-baseline.md`
- Create: `docs/phase0/evidence/gauntlet-post-fix-acceptance.md`
- Create on PASS: `docs/phase0/evidence/gauntlet-post-fix/runtime-only/acceptance-result.json`
- Create: `docs/phase0/evidence/gauntlet-post-fix/runtime-only/comparison-packet.json`
- Create: `docs/phase0/evidence/gauntlet-post-fix/runtime-only/readiness-ledger.json`
- Create: `docs/phase0/evidence/gauntlet-post-fix/runtime-only/report-input.json`
- Create: `docs/phase0/evidence/gauntlet-post-fix/runtime-only/report.html`
- Create: `docs/phase0/evidence/gauntlet-post-fix/runtime-only/run.log`
- Create the same six bounded files on PASS under: `docs/phase0/evidence/gauntlet-post-fix/full-evidence/`
- Create: `docs/phase0/evidence/gauntlet-final-spec-review.md`
- Create: `docs/phase0/evidence/gauntlet-final-quality-review.md`

- [ ] **Step 1: Prepare a clean runtime-only run.**

  ```bash
  rm -rf /tmp/shipworthy-gauntlet-runtime
  python3 tests/skill_product/gauntlet/run_acceptance.py prepare \
    --mode runtime-only \
    --skills-source plugins/shipworthy/skills \
    --output /tmp/shipworthy-gauntlet-runtime \
    > /tmp/shipworthy-gauntlet-runtime-manifest.json
  python3 -m json.tool /tmp/shipworthy-gauntlet-runtime/run-manifest.json >/dev/null
  ```

  Expected: exit 0; manifest names the randomized controller directory, healthy
  localhost URL, accounts/reset conditions, exact four copied skill paths,
  output allowlist, and empty runtime-only workspace with no source/test copy.

- [ ] **Step 2: Launch a new native Codex subagent with no history.**

  It must not receive the baseline misses, oracle, previous output, or expected fixes.
  Launch it with `fork_turns: none` and only the prepared runtime brief, copied
  four skill paths, URL/accounts, safe boundary, reset token/conditions,
  explicit allowlist, and `/tmp/shipworthy-gauntlet-runtime/agent-evidence`.
  Record its native agent ID and use a 60-minute coordinator deadline. No Claude,
  provider, CLI-agent, or browser-service substitution is permitted.

- [ ] **Step 3: Finalize and require an individual PASS.**

  Do not aggregate with the baseline. Any material miss, unsupported coverage, unexpected row, or false closure is FAIL/REVIEW_REQUIRED and must be diagnosed.

  ```bash
  python3 tests/skill_product/gauntlet/run_acceptance.py finalize \
    --run-manifest /tmp/shipworthy-gauntlet-runtime/run-manifest.json \
    --native-dispatch-status completed \
    --native-agent-id <native-agent-id> \
    --agent-output /tmp/shipworthy-gauntlet-runtime/agent-evidence
  python3 -m json.tool /tmp/shipworthy-gauntlet-runtime/acceptance-result.json >/dev/null
  ```

  Expected: exit 0 and authoritative `PASS`; retained result, comparison packet,
  canonical ledger, report input, HTML, and bounded log all validate. Always run
  `python3 tests/skill_product/gauntlet/run_acceptance.py cleanup --run-manifest /tmp/shipworthy-gauntlet-runtime/run-manifest.json` afterward.

  If native dispatch is unavailable, fails, or times out, call `finalize` with
  the matching status, agent ID if one exists, an empty evidence directory, and
  bounded `--coordinator-diagnostic`. Require `NOT_PROVEN` only for unavailable;
  retain the authoritative result, make no behavioral-PASS claim, and require
  explicit human release waiver. Failed/timeout available dispatch is `FAIL`.

- [ ] **Step 4: Repair only general skill behavior, then rerun fresh.**

  Do not mention fixture-specific button names in production skills. Preserve each general failure as a deterministic contract test.
  Classify every unexpected row as: real fixture behavior missing from the
  oracle, a nonmaterial/duplicate observation, or an unsupported agent claim.
  Repair oracle/comparator/traceability files only for a demonstrated instrument
  defect. Repair production only in the Task 5–7 files and only for a general
  baseline-linked behavior. First add a failing assertion to
  `test_frontier_contract.py`, `test_exhaustive_surface_contract.py`, or
  `test_gauntlet_report.py`; run its exact focused RED command, implement the
  minimum repair, and rerun it GREEN. Discard the failed run as a passing
  candidate and repeat Steps 1–3 with a brand-new `fork_turns: none` agent.
  Any production, schema, oracle, comparator, or harness repair invalidates all
  earlier acceptance results, including a prior PASS in the other mode.

- [ ] **Step 5: Run full-evidence mode with another fresh native Codex subagent.**

  Require source/runtime reconciliation and promised-but-missing cancellation discovery. Record procedural oracle blindness and filesystem containment `NOT_PROVEN` without treating that caveat as behavioral failure.

  ```bash
  rm -rf /tmp/shipworthy-gauntlet-full
  python3 tests/skill_product/gauntlet/run_acceptance.py prepare \
    --mode full-evidence \
    --skills-source plugins/shipworthy/skills \
    --product-source tests/skill_product/gauntlet/app \
    --output /tmp/shipworthy-gauntlet-full \
    > /tmp/shipworthy-gauntlet-full-manifest.json
  python3 -m json.tool /tmp/shipworthy-gauntlet-full/run-manifest.json >/dev/null
  ```

  Assert the manifest allowlist contains only copied skills, operational inputs,
  output, and the sanitizer-produced product copy—not the original product tree,
  Gauntlet tests, oracle, comparator, or prior runs. Launch another native Codex
  agent with `fork_turns: none`, the full-evidence brief, and only those manifest
  inputs; record its ID and use the same 60-minute deadline. Finalize with:

  ```bash
  python3 tests/skill_product/gauntlet/run_acceptance.py finalize \
    --run-manifest /tmp/shipworthy-gauntlet-full/run-manifest.json \
    --native-dispatch-status completed \
    --native-agent-id <native-agent-id> \
    --agent-output /tmp/shipworthy-gauntlet-full/agent-evidence
  python3 -m json.tool /tmp/shipworthy-gauntlet-full/acceptance-result.json >/dev/null
  python3 tests/skill_product/gauntlet/run_acceptance.py cleanup \
    --run-manifest /tmp/shipworthy-gauntlet-full/run-manifest.json
  ```

  Expected: exit 0 and individual `PASS`. Apply the identical unavailable/
  failed/timeout handling and fresh-rerun rule from runtime-only. Never substitute
  Claude or a provider. After the last repair of any kind, rerun both runtime-only
  and full-evidence from clean directories with fresh agents against the exact
  same final Git revision; only those two final individual results are durable.

- [ ] **Step 6: Commit compact acceptance evidence.**

  Copy only the six named text/JSON/HTML artifacts from each successful retained
  PASS into its durable mode directory. Bound `run.log` to relevant coordinator
  and agent diagnostics; omit screenshots/session state. Use the tested exporter
  so authoritative artifacts remain unchanged. For PASS, run exactly:

  ```bash
  rm -rf docs/phase0/evidence/gauntlet-post-fix/runtime-only docs/phase0/evidence/gauntlet-post-fix/full-evidence
  python3 tests/skill_product/gauntlet/redact_evidence.py --run-manifest /tmp/shipworthy-gauntlet-runtime/run-manifest.json --source /tmp/shipworthy-gauntlet-runtime --destination docs/phase0/evidence/gauntlet-post-fix/runtime-only --status PASS > /tmp/shipworthy-gauntlet-runtime-export.json
  python3 tests/skill_product/gauntlet/redact_evidence.py --run-manifest /tmp/shipworthy-gauntlet-full/run-manifest.json --source /tmp/shipworthy-gauntlet-full --destination docs/phase0/evidence/gauntlet-post-fix/full-evidence --status PASS > /tmp/shipworthy-gauntlet-full-export.json
  python3 -m json.tool /tmp/shipworthy-gauntlet-runtime-export.json >/dev/null
  python3 -m json.tool /tmp/shipworthy-gauntlet-full-export.json >/dev/null
  test -s docs/phase0/evidence/gauntlet-post-fix/runtime-only/report.html
  test -s docs/phase0/evidence/gauntlet-post-fix/runtime-only/run.log
  test -s docs/phase0/evidence/gauntlet-post-fix/full-evidence/report.html
  test -s docs/phase0/evidence/gauntlet-post-fix/full-evidence/run.log
  ```

  If a human explicitly waives native unavailability, run the corresponding
  exact export command with `--status NOT_PROVEN`; for example:

  ```bash
  rm -rf docs/phase0/evidence/gauntlet-post-fix/runtime-only
  python3 tests/skill_product/gauntlet/redact_evidence.py --run-manifest /tmp/shipworthy-gauntlet-runtime/run-manifest.json --source /tmp/shipworthy-gauntlet-runtime --destination docs/phase0/evidence/gauntlet-post-fix/runtime-only --status NOT_PROVEN > /tmp/shipworthy-gauntlet-runtime-export.json
  python3 -m json.tool docs/phase0/evidence/gauntlet-post-fix/runtime-only/acceptance-result.json >/dev/null
  test -s docs/phase0/evidence/gauntlet-post-fix/runtime-only/run.log
  test ! -e docs/phase0/evidence/gauntlet-post-fix/runtime-only/comparison-packet.json
  test ! -e docs/phase0/evidence/gauntlet-post-fix/runtime-only/readiness-ledger.json
  test ! -e docs/phase0/evidence/gauntlet-post-fix/runtime-only/report-input.json
  test ! -e docs/phase0/evidence/gauntlet-post-fix/runtime-only/report.html
  rm -rf docs/phase0/evidence/gauntlet-post-fix/full-evidence
  python3 tests/skill_product/gauntlet/redact_evidence.py --run-manifest /tmp/shipworthy-gauntlet-full/run-manifest.json --source /tmp/shipworthy-gauntlet-full --destination docs/phase0/evidence/gauntlet-post-fix/full-evidence --status NOT_PROVEN > /tmp/shipworthy-gauntlet-full-export.json
  python3 -m json.tool docs/phase0/evidence/gauntlet-post-fix/full-evidence/acceptance-result.json >/dev/null
  test -s docs/phase0/evidence/gauntlet-post-fix/full-evidence/run.log
  test ! -e docs/phase0/evidence/gauntlet-post-fix/full-evidence/comparison-packet.json
  test ! -e docs/phase0/evidence/gauntlet-post-fix/full-evidence/readiness-ledger.json
  test ! -e docs/phase0/evidence/gauntlet-post-fix/full-evidence/report-input.json
  test ! -e docs/phase0/evidence/gauntlet-post-fix/full-evidence/report.html
  ```

  Run only the block for the unavailable mode. Do not create placeholders or
  claim PASS. For two PASS results, verify:

  ```bash
  python3 -m json.tool docs/phase0/evidence/gauntlet-post-fix/runtime-only/acceptance-result.json >/dev/null
  python3 -m json.tool docs/phase0/evidence/gauntlet-post-fix/runtime-only/comparison-packet.json >/dev/null
  python3 -m json.tool docs/phase0/evidence/gauntlet-post-fix/runtime-only/readiness-ledger.json >/dev/null
  python3 -m json.tool docs/phase0/evidence/gauntlet-post-fix/runtime-only/report-input.json >/dev/null
  python3 -m json.tool docs/phase0/evidence/gauntlet-post-fix/full-evidence/acceptance-result.json >/dev/null
  python3 -m json.tool docs/phase0/evidence/gauntlet-post-fix/full-evidence/comparison-packet.json >/dev/null
  python3 -m json.tool docs/phase0/evidence/gauntlet-post-fix/full-evidence/readiness-ledger.json >/dev/null
  python3 -m json.tool docs/phase0/evidence/gauntlet-post-fix/full-evidence/report-input.json >/dev/null
  rg -n "cookie|authorization|bearer|reset[_ -]?token|/Users/" docs/phase0/evidence/gauntlet-post-fix && exit 1 || true
  git diff --check
  git add docs/phase0/evidence/gauntlet-current-skill-baseline.md docs/phase0/evidence/gauntlet-post-fix-acceptance.md docs/phase0/evidence/gauntlet-post-fix
  git commit -m "Prove exhaustive surface acceptance"
  ```

  For a waived `NOT_PROVEN` mode, omit that mode's PASS-only validation lines;
  the exact waiver checks above apply. The summary must name the waiver and must
  not say the mode passed.

### Task 9: Final verification and cleanliness

**Files:**

- Modify only as required by verified failures.

- [ ] **Step 1: Run the focused Gauntlet and frontier suites.**

  ```bash
  python3 -m unittest -v \
    tests.skill_product.test_gauntlet_fixture \
    tests.skill_product.test_gauntlet_oracle \
    tests.skill_product.test_gauntlet_comparator \
    tests.skill_product.test_gauntlet_acceptance \
    tests.skill_product.test_frontier_contract \
    tests.skill_product.test_exhaustive_surface_contract \
    tests.skill_product.test_gauntlet_report
  ```

  Expected: exit 0, zero failures, zero errors.

- [ ] **Step 2: Run the entire new suite.**

  ```bash
  python3 -m unittest discover -s tests/skill_product -p 'test_*.py'
  ```

  Expected: exit 0, zero failures, zero errors.

- [ ] **Step 3: Run all direct legacy suites.**

  ```bash
  python3 tests/skill_product/test_skill_contract_legacy.py
  python3 tests/skill_product/test_render_report_legacy.py
  python3 tests/skill_product/test_to_sarif_legacy.py
  python3 tests/skill_product/test_make_bundle_legacy.py
  ```

  Expected: every command exits 0 with its current aggregate plus intentional
  new assertions; zero failures and zero errors.

- [ ] **Step 4: Run compile, diff, parity, and forbidden-behavior checks.**

  ```bash
  python3 -m compileall -q plugins/shipworthy/skills tests/skill_product
  git diff --check
  python3 -m unittest -v tests.skill_product.test_installed_parity tests.skill_product.test_four_skill_boundary tests.skill_product.test_stdlib_scripts
  python3 -I tests/skill_product/support/frontier_validation.py \
    --input tests/skill_product/fixtures/gauntlet-report-input.json \
    --evidence-root tests/skill_product/fixtures
  ! rg -n '^\s*(import|from)\s+(requests|urllib\.request)|socket\.create_connection|subprocess\.(run|Popen).*\b(codex|claude)\b|pip install|playwright install' plugins/shipworthy/skills
  rg -n 'ThreadingHTTPServer|localhost|127\.0\.0\.1' tests/skill_product/gauntlet/app/server.py
  ! rg -n 'requests|urllib\.request|socket\.create_connection|subprocess\.(run|Popen).*\b(codex|claude)\b|pip install|playwright install' tests/skill_product/gauntlet --glob '!app/server.py'
  ```

  Expected: every command exits 0. The only network-capable fixture component is
  the allowlisted localhost `ThreadingHTTPServer`; installed skills contain no
  client network/provider dispatch or installation behavior.

- [ ] **Step 5: Remove caches and transient run state.**

  Remove only generated caches and named Gauntlet transient paths; preserve
  unrelated `docs/examples/` files.

  ```bash
  find plugins/shipworthy/skills tests/skill_product -type d -name __pycache__ -prune -exec rm -rf {} +
  rm -rf .pytest_cache /tmp/shipworthy-gauntlet-runtime /tmp/shipworthy-gauntlet-full
  rm -f /tmp/shipworthy-gauntlet-runtime-manifest.json /tmp/shipworthy-gauntlet-full-manifest.json /tmp/shipworthy-gauntlet-runtime-export.json /tmp/shipworthy-gauntlet-full-export.json
  test -z "$(find plugins/shipworthy/skills tests/skill_product -type d -name __pycache__ -print -quit)"
  test ! -e .pytest_cache
  test ! -e /tmp/shipworthy-gauntlet-runtime
  test ! -e /tmp/shipworthy-gauntlet-full
  test ! -e /tmp/shipworthy-gauntlet-runtime-manifest.json
  test ! -e /tmp/shipworthy-gauntlet-full-manifest.json
  test ! -e /tmp/shipworthy-gauntlet-runtime-export.json
  test ! -e /tmp/shipworthy-gauntlet-full-export.json
  test -d docs/examples
  ```

- [ ] **Step 6: Record exact proof and remaining NOT_PROVEN boundaries.**

  Update `docs/phase0/evidence/gauntlet-post-fix-acceptance.md` with native Codex
  runtime-only/full-evidence results, artifact digests/paths, oracle comparison,
  missed/currently fixed behaviors, HTML evidence, procedural oracle blindness,
  filesystem containment `NOT_PROVEN`, release-waiver state, and whether an
  installed validator was justified. Validate all linked local paths exist:

  ```bash
  python3 - <<'PY'
  import pathlib, re
  report = pathlib.Path("docs/phase0/evidence/gauntlet-post-fix-acceptance.md")
  missing = []
  for target in re.findall(r"\]\(([^)]+)\)", report.read_text(encoding="utf-8")):
      if "://" not in target and not (report.parent / target.split("#", 1)[0]).resolve().exists():
          missing.append(target)
  if missing:
      raise SystemExit("missing evidence links: " + ", ".join(missing))
  PY
  git diff --check
  ```

  Expected: link check exits 0 and `git diff --check` is silent.

- [ ] **Step 7: Run one independent specification review and one quality review.**

  Dispatch two fresh native Codex reviewers with `fork_turns: none` and a
  30-minute deadline each. Give both the repository root, final Git revision,
  `git diff origin/main...HEAD`, the design spec, implementation plan, complete
  focused/full/legacy command list, and durable acceptance-evidence paths—never
  earlier review conclusions. The specification reviewer maps every MUST and
  out-of-scope boundary to code/test/evidence and writes
  `docs/phase0/evidence/gauntlet-final-spec-review.md`. The quality reviewer
  inspects code, tests, security boundaries, maintainability, HTML usability,
  and bloat and writes
  `docs/phase0/evidence/gauntlet-final-quality-review.md`. Each verdict must be
  exactly `APPROVED` or `ISSUES`, followed by numbered findings with file/line,
  severity, evidence, and smallest repair. Any unresolved material finding,
  missing review artifact, timeout, or `ISSUES` verdict blocks release and goal
  completion. Repair real findings with focused RED/GREEN tests, then rerun both
  fresh reviews once against the repaired final diff.

- [ ] **Step 8: Re-run Steps 1–5 after any review repair.**

  First stage only the explicit affected Task 5–8 files, run
  `git diff --cached --check`, and commit the focused repair as
  `Repair Gauntlet review findings`. Record that commit SHA in both new review
  prompts. Any review-driven repair invalidates both acceptance modes. Rerun
  Task 8 Steps 1–6 with two new native agents on that identical committed
  revision, replace the durable evidence, then rerun Task 9 Steps 1–5 and both
  fresh reviews using `git diff origin/main...HEAD`. Expected: both acceptance
  modes individually PASS (or carry explicit human NOT_PROVEN waiver), both
  reviews say `APPROVED`, all deterministic gates exit 0, and no transient state
  remains. Never ask a reviewer or test subject to evaluate an uncommitted
  working-tree repair.

- [ ] **Step 9: Commit the final verified implementation. Do not push unless separately requested.**

  ```bash
  git diff --check
  git status --short
  git add plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md plugins/shipworthy/skills/ship-readiness-orchestrator/references/evidence-state.md plugins/shipworthy/skills/ship-readiness-orchestrator/references/lane-prompts.md plugins/shipworthy/skills/ship-readiness-orchestrator/references/pressure-tests.md plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/readiness-ledger.schema.json plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/report-input.schema.json plugins/shipworthy/skills/ship-readiness-orchestrator/references/visual-html-report.md plugins/shipworthy/skills/ship-readiness-orchestrator/references/final-report-contract.md plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/render_report.py plugins/shipworthy/skills/ship-product-workflows/SKILL.md plugins/shipworthy/skills/ship-product-workflows/references/path-discovery-and-coverage.md plugins/shipworthy/skills/ship-product-workflows/templates/coverage-map.json
  git add tests/skill_product/gauntlet tests/skill_product/support/frontier_validation.py tests/skill_product/support/schema_subset.py tests/skill_product/test_gauntlet_oracle.py tests/skill_product/test_gauntlet_comparator.py tests/skill_product/test_gauntlet_fixture.py tests/skill_product/test_gauntlet_acceptance.py tests/skill_product/test_frontier_contract.py tests/skill_product/test_exhaustive_surface_contract.py tests/skill_product/test_gauntlet_report.py tests/skill_product/test_skill_contract_legacy.py tests/skill_product/test_render_report_legacy.py tests/skill_product/fixtures/gauntlet-report-input.json
  git add docs/phase0/evidence/gauntlet-current-skill-baseline.md docs/phase0/evidence/gauntlet-post-fix-acceptance.md docs/phase0/evidence/gauntlet-post-fix docs/phase0/evidence/gauntlet-final-spec-review.md docs/phase0/evidence/gauntlet-final-quality-review.md
  git diff --cached --check
  git commit -m "Verify exhaustive surface Gauntlet"
  ```

  Include any review-driven code/test/evidence repairs in that final commit;
  never stage unrelated `docs/examples/` content.

# Lean Host-Native Shipworthy Implementation Plan

> **SUPERSEDED:** Do not execute this package-based plan. The approved product
> direction is four self-contained skills with no `shipworthy-core`; use
> `docs/superpowers/plans/2026-07-17-four-self-contained-skills.md`.

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents are explicitly authorized and available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn Shipworthy's proven Phase 0 core into a small, skill-first evidence layer that uses Codex/Claude native browser tools for adaptive product auditing and accepts Playwright output as optional deterministic regression evidence.

**Architecture:** Keep the four skills as the product surface and the immutable v1 readiness ledger as the source of truth. Add bounded, read-only import adapters for host-browser evidence and existing Playwright reports; attach their artifacts and limitations to the canonical ledger; render them through the existing HTML/SARIF/bundle pipeline. The host remains responsible for browser control and process execution. Shipworthy does not implement a browser, test DSL, daemon, database, portal, MCP server, provider service, or cloud runner.

**Tech Stack:** Python 3.12-3.14, Pydantic v2, JSON Schema, pytest, existing skill Markdown and stdlib-only report parsing. No Playwright runtime dependency is added to `shipworthy-core`.

---

## Approved product boundary

This plan supersedes the active implementation direction of the broad Phase 1-8 platform roadmap. Historical provider research remains useful evidence, but it is not an instruction to reproduce an external testing platform.

Build only:

- host-native browser evidence intake for Codex- and Claude-style skill workflows;
- optional import of an existing Playwright JSON report and its local attachments;
- canonical artifact lineage, evidence debt, proof ceilings, and independent verification;
- mandatory self-contained HTML, SARIF, and evidence-bundle output;
- small brownfield adapters only when a real repository already emits the format;
- host-native execution recipes for local tests, shell commands, and optional CI.

Do not build:

- a custom browser engine, browser DSL, or Playwright wrapper service;
- SQLite, event sourcing, a general content-addressed store, persistence service, or daemon;
- a public CLI product, portal, MCP server, provider abstraction, or external service integration;
- hosted runners, accounts, billing, schedules, notifications, or multi-tenant infrastructure;
- automatic dependency installation, network access, credential use, or destructive target changes.

## Delivery shape

Implement this as one compact milestone with five code tasks and one verification task. Stop after Task 6. Any later adapter requires a concrete repository fixture and a separate approval.

### Task 1: Lock native-browser-first routing in contract tests

**Files:**

- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md`
- Modify: `plugins/shipworthy/skills/ship-product-workflows/SKILL.md`
- Create: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/browser-evidence-routing.md`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/lane-prompts.md`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/final-report-contract.md`

- [ ] Write failing contract checks requiring all of the following:
  - Codex/Claude native browser or computer-use tools are the default for adaptive exploration.
  - Playwright is selected only for deterministic replay, explicit assertions, isolated contexts, traces, cross-browser checks, or CI regression proof.
  - A screenshot proves only the state visible at capture time; it does not prove an entire workflow.
  - Neither browser path silently upgrades a finding to `Confirmed` or verifier status to `approved`.
  - Shipworthy never installs Playwright or changes the target application merely to obtain browser evidence.
  - The four skill names, trigger language, skill-only behavior, and mandatory HTML-report contract remain unchanged.

- [ ] Run the contract test and capture RED evidence:

  ```bash
  uv run python plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py
  ```

- [ ] Add the smallest routing reference and skill edits that satisfy the checks. Describe tool capability classes, not hard-coded APIs that may differ by host version.

- [ ] Re-run the contract test and capture GREEN evidence.

- [ ] Run the four existing legacy report/contract suites to prove the routing change did not break existing behavior:

  ```bash
  uv run python plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py
  uv run python plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_render_report.py
  uv run python plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_to_sarif.py
  uv run python plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_make_bundle.py
  ```

**Acceptance:** A skill can explain why it chose native browsing or Playwright, and the choice never changes the canonical proof/verifier rules.

### Task 2: Add a bounded browser-evidence envelope

**Files:**

- Create: `src/shipworthy/domain/browser_evidence.py`
- Create: `schemas/v1/browser-evidence-envelope.schema.json`
- Modify: `src/shipworthy/domain/contracts.py`
- Modify: `src/shipworthy/domain/enums.py`
- Modify: `pyproject.toml` only if the existing schema force-include does not already package the new file
- Create: `tests/contract/test_browser_evidence_contract_v1.py`
- Create fixtures under: `tests/fixtures/browser_evidence/`

- [ ] Write failing tests for a strict envelope with these fields:
  - `schema_name`, `schema_version`, `generated_at`, and producer;
  - host family and driver label;
  - evidence mode: `exploratory` or `deterministic_replay`;
  - target fingerprint and path/intent reference;
  - bounded ordered steps and observed outcomes;
  - optional local artifact descriptors for screenshots, DOM/accessibility snapshots, console, network, trace, and recording;
  - explicit unavailable channels, limitations, and `not_proven` statements;
  - optional existing canonical finding IDs to which evidence may be attached.

- [ ] Test the same hostile boundaries as the v1 ledger: byte limit, duplicate JSON members, excessive depth/counts, unknown keys, invalid timestamps, unsafe paths, remote URLs masquerading as local artifacts, duplicate IDs, and unsupported schema versions.

- [ ] Require artifact bytes to be supplied separately by the caller. The envelope may declare a safe repo-relative path and SHA-256, but parsing it must perform no filesystem, network, browser, or subprocess access.

- [ ] Run the focused tests and record RED:

  ```bash
  uv run pytest -q tests/contract/test_browser_evidence_contract_v1.py
  ```

- [ ] Implement frozen strict models plus `parse_browser_evidence_json(raw: bytes)`. Reuse the existing bounded types and canonical serialization rules rather than creating parallel validation utilities.

- [ ] Generate/freeze the JSON Schema from the Pydantic contract using the same pattern as the existing readiness schemas.

- [ ] Re-run the focused tests and record GREEN.

**Acceptance:** The envelope records what a host actually observed without claiming that Shipworthy drove the browser or that a screenshot proves more than its captured state.

### Task 3: Normalize native and Playwright evidence without running either

**Files:**

- Create: `src/shipworthy/adapters/importers/browser_evidence.py`
- Create: `src/shipworthy/adapters/importers/playwright_report.py`
- Modify: `src/shipworthy/adapters/importers/__init__.py`
- Create: `tests/importers/test_browser_evidence.py`
- Create: `tests/importers/test_playwright_report.py`
- Create fixtures under: `tests/fixtures/playwright/`

- [ ] Write failing browser-import tests proving:
  - raw envelope bytes are retained and sealed with SHA-256;
  - supplied attachment bytes must exactly match declared digest and size;
  - missing, corrupt, or undeclared attachments become named evidence debt;
  - the result is deterministic, immutable, bounded, and contains no secret values in diagnostics;
  - import never reads arbitrary paths, starts a browser, opens a socket, or invokes a subprocess;
  - imported evidence cannot set `VerifierStatus.APPROVED` or create a confirmed blocker.

- [ ] Write failing Playwright-import tests using small synthetic JSON reporter fixtures. Cover pass, fail, skip, retry, flaky result, screenshot, trace, missing attachment, absolute-path rejection, duplicate test identity, malformed report, and oversized input.

- [ ] Define one normalized immutable result used by both adapters. It should contain sealed artifacts, observations, source identity, limitations, and evidence-debt drafts; it must not invent product findings or readiness disposition.

- [ ] Run both focused files and record RED:

  ```bash
  uv run pytest -q tests/importers/test_browser_evidence.py tests/importers/test_playwright_report.py
  ```

- [ ] Implement the host-envelope importer first.

- [ ] Implement the Playwright JSON importer as a translation into the same normalized result. Parse existing files only; do not add Playwright as a dependency and do not expose a Shipworthy browser-run command.

- [ ] Re-run the focused tests and record GREEN.

**Acceptance:** Native browser observations and Playwright reporter output arrive through one conservative evidence shape while preserving their different proof characteristics.

### Task 4: Attach evidence to the canonical ledger and surface lineage

**Files:**

- Create: `src/shipworthy/domain/evidence_attachment.py`
- Modify: `src/shipworthy/adapters/reporting/projection.py`
- Modify: `src/shipworthy/adapters/reporting/html.py` only if the compatibility renderer cannot display the added projection fields safely
- Modify: `src/shipworthy/adapters/reporting/sarif.py`
- Modify: `src/shipworthy/adapters/reporting/bundle.py`
- Create: `tests/domain/test_evidence_attachment.py`
- Create: `tests/reporting/test_browser_evidence_reporting.py`

- [ ] Write failing tests for a pure `attach_evidence(ledger, normalized_result)` transformation:
  - attach only to finding IDs already present in the ledger;
  - preserve all existing finding identity, action, proof, severity, confidence, gate, and verifier status;
  - add collision-free artifacts and named evidence debt;
  - reject digest/path/ID collisions rather than renaming silently;
  - produce byte-identical output for identical inputs.

- [ ] Write failing reporting tests requiring HTML, SARIF, and bundle manifest to expose:
  - evidence mode and driver;
  - source producer and lineage operation;
  - attachment availability and digest;
  - limitations and missing-channel evidence debt;
  - exact canonical finding IDs and unchanged gate outcome.

- [ ] Run focused tests and record RED:

  ```bash
  uv run pytest -q tests/domain/test_evidence_attachment.py tests/reporting/test_browser_evidence_reporting.py
  ```

- [ ] Implement the pure attachment transform with no persistence or implicit reads.

- [ ] Extend the existing reporting projection rather than creating a second report model. Preserve the mandatory noninteractive, self-contained HTML safety grammar.

- [ ] Re-run focused tests and record GREEN.

**Acceptance:** Browser evidence becomes inspectable lineage in the same HTML/SARIF/bundle generated from the canonical ledger, with no parallel truth store and no proof inflation.

### Task 5: Add only the brownfield execution recipes that the host needs

**Files:**

- Create: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/host-execution-recipes.md`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/exports-and-ci.md`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py`
- Create: `tests/integration/test_host_execution_boundary.py`

- [ ] Write failing tests/contract checks that require this decision order:
  1. discover and run the target repository's existing test commands;
  2. use native browser/computer-use for adaptive path discovery;
  3. use an existing Playwright setup for deterministic replay when useful;
  4. suggest a minimal target-owned Playwright test only with explicit user authorization;
  5. record unsupported or unavailable execution as evidence debt.

- [ ] Require recipes to preserve target-repo instructions, read-only defaults, safe fixtures, explicit destructive-test authorization, and local-only artifact handling.

- [ ] Add forbidden-behavior checks proving the core contains no browser launch, package installation, network client, daemon, database, MCP, portal, scheduler, credential store, or provider integration.

- [ ] Run the focused checks and record RED:

  ```bash
  uv run pytest -q tests/integration/test_host_execution_boundary.py
  uv run python plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py
  ```

- [ ] Add concise host recipes. They may show how an agent recognizes existing `pytest`, `npm test`, `playwright test`, SARIF, or JUnit outputs, but must not create a general command runner.

- [ ] Re-run focused checks and record GREEN.

**Acceptance:** Shipworthy delegates execution to capabilities the host or target repository already owns and records the returned evidence without becoming an execution platform.

### Task 6: Reconcile documentation and run the release gate

**Files:**

- Modify: `ARCHITECTURE.md`
- Create: `docs/strategy/shipworthy-skill-first-roadmap-2026-07-15.md`
- Create: `docs/phase0/evidence/lean-host-native-red-green-ledger.md`

- [ ] Update architecture diagrams and prose to show:

  ```text
  Codex/Claude native browser ─┐
                              ├─ bounded evidence adapters ─ canonical v1 ledger
  Existing Playwright report ─┘                         ├─ HTML
                                                       ├─ SARIF
                                                       └─ evidence bundle
  ```

- [ ] Record every focused RED command/output and corresponding GREEN command/output in the evidence ledger. Do not rewrite a failure after the implementation exists.

- [ ] Run all new tests together:

  ```bash
  uv run pytest -q \
    tests/contract/test_browser_evidence_contract_v1.py \
    tests/domain/test_evidence_attachment.py \
    tests/importers/test_browser_evidence.py \
    tests/importers/test_playwright_report.py \
    tests/reporting/test_browser_evidence_reporting.py \
    tests/integration/test_host_execution_boundary.py
  ```

- [ ] Run the complete Phase 0/core suite:

  ```bash
  uv run pytest -q
  ```

- [ ] Run the four existing legacy report/contract suites and confirm the established totals remain 120 + 174 + 22 + 17 unless an intentional test-only addition changes the contract total and is explained in the evidence ledger:

  ```bash
  uv run python plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py
  uv run python plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_render_report.py
  uv run python plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_to_sarif.py
  uv run python plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_make_bundle.py
  ```

- [ ] Run compile and repository hygiene checks:

  ```bash
  uv run python -m compileall -q src tests plugins/shipworthy/skills
  git diff --check
  find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .ruff_cache \) -prune -print
  ```

- [ ] Run a forbidden-behavior scan with explicit reviewed allowlists for documentation mentions:

  ```bash
  rg -n "sqlite3|create_connection|requests\.|httpx|aiohttp|subprocess\.|Popen\(|playwright\.sync_api|playwright\.async_api|mcp server|daemon|portal|scheduler|credential store" src tests
  ```

- [ ] Run packaging/preflight checks already established by Phase 0. Confirm the new schema is present in a built wheel without modifying the lockfile or using the network.

- [ ] Run an independent specification review against this plan, repair findings with focused RED/GREEN evidence, then run an independent code-quality review. If subagents are not explicitly enabled for the execution session, use two separate clean-context review passes and record that limitation.

- [ ] Remove only generated cache/build noise. Do not delete user files, fabricate `uv.lock`, write installed skill copies, commit, push, or access the network.

**Acceptance:** The complete core and legacy suites are green, installed-skill compatibility is unchanged, and the final report truthfully distinguishes native exploratory evidence from deterministic Playwright evidence.

## Stop conditions and proof labels

Stop after Task 6 and report:

- exactly which host-browser and Playwright fixtures were imported;
- exact artifact digests, lineage operations, finding attachments, and gate invariants;
- the HTML, SARIF, and evidence-bundle parity result;
- all review findings and repairs;
- current test totals and packaging/preflight results;
- `NOT_PROVEN` for Python 3.12-3.14 runtime execution, locked-wheel reproduction, SBOM execution, and OS-level network containment unless fresh evidence in the execution environment proves them;
- why no Phase 1-style platform work started.

Do not interpret completion of this plan as authorization for persistence, a public CLI, browser runners, portal/MCP/provider integrations, hosted infrastructure, or the retired Phase 1-8 backlog.

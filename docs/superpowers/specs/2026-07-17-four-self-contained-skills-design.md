# Four Self-Contained Shipworthy Skills Design

**Status:** Approved direction; implementation not started.

## Product statement

Shipworthy is four independently useful agent skills:

1. `ship-readiness-orchestrator`
2. `ship-deep-review`
3. `ship-product-workflows`
4. `ship-workflow-clarity`

There is no separately installed `shipworthy-core`, public CLI, Python package,
daemon, service, persistence layer, browser runner, or provider runtime. Native
Codex and Claude plugin installation is the primary distribution path.

## Architecture

Each skill owns the resources required for its job:

```text
skill-name/
├── SKILL.md       concise orchestration and judgment
├── references/    contracts, methods, schemas, and examples loaded as needed
├── templates/     user-facing or ledger templates
├── assets/        output resources, when required
└── scripts/       small deterministic standard-library utilities, when required
```

Only `ship-readiness-orchestrator` needs production scripts initially. The other
three skills remain instruction/reference/template skills unless a demonstrated
reliability gap justifies a local utility.

Each skill must also work when installed alone. The orchestrator may use the
other three skills when present, but their absence must produce a bounded
standalone fallback with explicit evidence debt rather than a hard stop or an
attempt to fetch missing skills.

## Resource placement rules

- Put judgment, routing, and tool-selection rules in `SKILL.md`.
- Put detailed contracts, schemas, mappings, and procedures in `references/`.
- Put files copied or adapted into outputs in `templates/` or `assets/`.
- Put deterministic transformations in `scripts/` only when repeated agent
  generation would weaken exactness or safety.
- Do not place executable code in `references/`.
- Do not create a shared runtime directory outside the four skills.
- Do not make one independently installable skill depend on another skill's
  private files.

## Deterministic utility boundary

The orchestrator initially retains only the three deterministic utilities that
already serve a mandatory output contract:

- self-contained HTML rendering;
- SARIF rendering;
- evidence-bundle construction.

Ledger validation, legacy normalization, host-browser normalization, and
Playwright-report normalization remain instructions, schemas, and repository
assurance by default. Add another installed script only after a failing
standalone-skill acceptance test proves that agent instructions cannot preserve
the required exactness. Every proposed script must document its caller,
frequency, failure consequence, smaller alternative, size budget, and retirement
criterion before it is approved.

Material growth of the three retained scripts is subject to the same gate. They
may not absorb a shared domain model, general validation framework, importer
framework, or package-shaped internal architecture merely because they already
exist.

Development-only parity, migration-retirement, lifecycle-rehearsal, and hostile
fixture helpers remain repository tests. They are not installed production
components. Installed copies also exclude `test_*.py`, sample ledgers, fixtures,
and development-only migration tools.

Every production script must:

- use only the Python standard library;
- perform one documented job;
- accept explicit inputs and outputs;
- be read-only unless an output path is explicitly supplied;
- perform no network, credential, dependency-installation, background-process,
  browser-launch, or target-repository mutation;
- produce deterministic UTF-8 output where the contract requires exactness;
- keep machine output separate from bounded human diagnostics;
- run from the directory containing the skill rather than assuming the audited
  repository is the current directory;
- support isolated invocation with `python3 -I`.

These scripts require a Python 3.11-or-newer standard-library interpreter, but
no Python package installation. The skill checks `python3`, then `python`, then
Windows `py -3`, verifies the version, and uses the first compatible command.
If none is available, the agent follows the documented instruction-only HTML
contract, still produces the mandatory HTML report, and labels deterministic
script execution, SARIF, and evidence-bundle generation `NOT_PROVEN` rather than
installing a runtime. Only HTML is mandatory for every operational run; SARIF
and the evidence bundle are deterministic optional exports.

## Canonical truth

The readiness ledger remains the source of truth. Its JSON Schemas live under
`ship-readiness-orchestrator/references/schemas/`. Skill instructions and
templates teach agents how to create and inspect the ledger. The schemas own
structural fields and enums; a repository-only schema-subset oracle executes the
keywords Shipworthy uses and fails on unsupported schema keywords. Any later
installed validator may own only bounded parsing and named cross-field
invariants after passing the script-necessity gate. The renderer, SARIF exporter,
and bundler consume the ledger.

Browser and Playwright artifacts are supporting evidence. They never create a
confirmed blocker, approve a verifier, or change a gate without an explicit
ledger finding supported under the existing proof rules.

## Installation and lifecycle

- Codex installs Shipworthy as a plugin with `.codex-plugin/plugin.json`.
- Claude installs Shipworthy through its marketplace/plugin manager.
- Manual installation is an advanced fallback with an explicit
  `--target codex|claude|both`; it never guesses.
- Installed copies contain the four skills and their local resources.
- Plugin managers own upgrades and uninstallation.
- No skill performs automatic production installation or upgrade work.
- Synthetic temporary fixtures prove repository-to-installed-copy content
  parity; real user skill directories are never modified by tests.
- Native Codex/Claude lifecycle behavior is exercised under isolated temporary
  host state when the corresponding host CLI is available and otherwise remains
  `NOT_PROVEN`. Synthetic copies are never presented as native-host proof.
- Backup and exact rollback claims apply only to Shipworthy's advanced manual
  installer, not to lifecycle behavior owned by external plugin managers.

## Removal boundary

Remove the package-only architecture after its useful behavior is migrated:

- `src/shipworthy/`;
- root `schemas/` after schema relocation;
- package/build/preflight scripts;
- Pydantic, Hatch, uv package metadata, `.python-version`, and `uv.lock`;
- core/skill compatibility metadata whose only purpose was coordinating two
  separately versioned products;
- wheel, SBOM, and Python-package runtime-matrix gates.

Wheel reproduction and SBOM execution become `NOT_APPLICABLE`, not silently
`PROVEN`, because the distributable Python package no longer exists.

## Evidence preservation

The removal is a migration, not a rewrite. Before deleting package code, map
every behavior and test to one of:

- preserved in a skill instruction/reference;
- preserved in a skill-local script;
- retained as a repository-only assurance test;
- deliberately removed as package/lifecycle infrastructure;
- deferred with explicit evidence debt.

The migration map is closed-world: every touched or removed path has one
disposition, pre-change digest, replacement, and preservation test. Unlisted
paths cannot be deleted. Mandatory ledger, HTML, SARIF, bundle, parity, and
manual-rollback behavior cannot be deferred.

The legacy test totals, mandatory HTML contract, four skill names and triggers,
safe read-only defaults, and skill-only independence remain protected.

## Non-goals

- No Phase 1 platform work.
- No SQLite, API, portal, daemon, MCP server, public CLI, hosted runner, provider
  integration, scheduler, accounts, billing, or credential store.
- No automatic Playwright installation or custom browser engine.
- No writes to real Codex or Claude installations.
- No commit or push during this implementation run unless the user later gives
  a new explicit instruction.
- No modification of a pre-existing dirty hunk until its ownership and intended
  migration are recorded in a dirty-state ledger.

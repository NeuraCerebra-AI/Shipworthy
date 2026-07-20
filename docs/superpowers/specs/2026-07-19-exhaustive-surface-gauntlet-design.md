# Exhaustive Surface Gauntlet Design

**Status:** Approved direction; implementation not started.

## Product objective

Shipworthy must do more than instruct an agent to inspect every safe path. It
must make missed product surface visible and make unsupported completeness
claims fail.

The test target is a bounded adversarial product with a private ground-truth
oracle. Fresh Codex and Claude sessions audit the product without seeing the
oracle. Deterministic repository tooling compares each resulting frontier to
the oracle and checks that Shipworthy discovered, exercised, bounded, and
reported the product surface honestly.

The intended Shipworthy promise is:

> Every material feature, surface, state, and discoverable interactive control
> inside the declared roles, fixtures, devices, and safety boundary is
> inventoried and dispositioned. Every safe material transition is exercised
> or explicitly marked blocked, avoided, sampled, missing, or not proven.

This is not a claim that every theoretical action sequence in an arbitrary
stateful system can be enumerated.

## Design principles

- Strengthen the existing `path_frontier`; do not create parallel ledgers.
- Test agent behavior, not merely the presence of contract wording.
- Keep continuous tests deterministic, offline, and fast.
- Run expensive fresh-agent tests as release acceptance, not on every edit.
- Keep the installed product as four self-contained skills.
- Add no core package, service, database, daemon, crawler, or browser engine.
- Use host-native browser/computer-use capabilities for adaptive discovery.
- Never make several incomplete runs look complete by aggregating their misses.
- Keep the default HTML report useful to a product owner; put exhaustive
  technical detail in machine-readable data and expandable sections.

## Chosen approach

Use one controlled adversarial micro-application, called the **Shipworthy
Gauntlet**.

Rejected alternatives:

- **Prompt-only pressure testing** is retained as contract documentation but
  cannot prove that an agent actually discovers hidden surface.
- **A large production-like demonstration application** would add maintenance,
  flakiness, and unrelated product code without improving the bounded oracle.
- **A general crawler or graph engine** would violate the four-skill architecture
  and duplicate capabilities already available from Codex and Claude hosts.

## Repository architecture

The development-only fixture lives under the existing test tree:

```text
tests/skill_product/gauntlet/
├── app/
│   ├── server.py
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   ├── product-docs/
│   ├── product-tests/
│   ├── fixtures/
│   └── roles.json
├── oracle/
│   ├── surface-oracle.json
│   ├── surface-oracle.schema.json
│   ├── expected-defects.json
│   └── expected-defects.schema.json
├── prompts/
│   ├── runtime-only.md
│   └── full-evidence.md
├── run_acceptance.py
├── compare_agent_result.py
└── README.md
```

The fixture is never included in installed skill copies. The only potential
installed production addition is a small, dependency-free frontier validator
inside `ship-readiness-orchestrator/scripts/`, subject to the existing script
necessity and size boundary.

## Gauntlet runtime

The app uses a Python standard-library HTTP server and plain HTML, CSS, and
JavaScript. It has:

- no package installation;
- no external network calls;
- deterministic seed data and time;
- resettable in-memory state;
- a random available localhost port;
- no credentials outside documented synthetic accounts;
- no writes outside a supplied temporary directory;
- a readiness endpoint for the harness;
- a reset endpoint available to the harness but not advertised as product UI.

The server, app, and docs are copied to a temporary target directory for each
run. The oracle and comparator remain outside that directory. Runtime-only
agents receive only the URL, synthetic credentials, safe-test boundary, reset
conditions, and output path.

`run_acceptance.py` is a development-only standard-library driver. Its public
interface is:

```text
run_acceptance.py --host codex|claude --mode runtime-only|full-evidence
                  --skills-source PATH --output PATH --timeout-seconds N
```

It starts and health-checks the fixture, prepares isolated host state, launches
one bounded host process, validates required artifacts, runs the comparator,
writes `acceptance-result.json`, terminates the complete fixture/host process
group, and exits with the authoritative gate status. It uses `try/finally` for
cleanup and preserves diagnostics and agent evidence on failure.

## Adversarial surface

The app remains small enough to understand but contains realistic discovery
failures. Its normal surface includes dashboard, projects, project details,
account/settings, team management, reports, billing, and help.

The oracle covers these adversarial cases:

1. Settings exists only inside an avatar menu.
2. Invite appears only at a mobile viewport.
3. Export appears only for an administrator.
4. A row action appears only in a context menu.
5. A command palette opens through a documented keyboard shortcut.
6. An import deep link exists but is absent from primary navigation.
7. Publish remains disabled until a prerequisite checklist is complete.
8. An empty-state action appears only when its fixture reaches empty state.
9. Invalid input reveals a recovery action not otherwise visible.
10. An expired session exposes a stale-session recovery path.
11. Two Save controls look equivalent, but one does not persist data.
12. A success message appears despite a failed API response.
13. Refresh or browser-back loses a filter or draft.
14. Documentation promises cancellation, but no cancellation path exists.
15. Delete is discoverable but must be avoided without exact authorization.
16. A prominent visual object is deliberately not interactive.
17. A disabled control lacks an explanation.
18. A feature flag creates an explicitly unavailable feature.

Each case must be material to coverage, safety, or readiness. Pure visual
trivia is excluded. The fixture must not hide features through impossible or
undocumented magic; each expected discovery has at least one legitimate runtime
or full-evidence discovery channel.

## Canonical frontier extension

Do not introduce separate feature, surface, control, and transition ledgers.
Extend the existing canonical `path_frontier` rows with these fields:

```text
kind: intent | feature | surface | control | transition
parent_id
semantic_key
observations[]
control_identity
before_state
after_state
status
evidence_refs
```

Existing fields for role, account state, fixture, state/device variant, risk,
attempt count, wave, blocker reason, sample justification, and next action
remain authoritative.

Each `observations[]` entry records:

```text
method_family
method_detail
provenance
role
state
viewport
discovery_pass_id
evidence_refs
```

Multiple discovery channels merge into one semantic frontier row. They do not
create duplicate rows. Conflicting observations on one semantic key are
preserved and must be reconciled or left as evidence debt.

Parent relationships provide traceable lineage:

```text
feature -> surface/state -> control -> transition
```

Fields that do not apply to a row kind may be absent. The schema must define
the conditional requirements for each kind without creating duplicated models.

Semantic keys follow deterministic type-specific rules:

```text
feature:    feature:<normalized-feature-name>
surface:    surface:<route-or-window>:<material-state>:<role>:<viewport-class>
control:    control:<surface-key>:<normalized-name>:<control-type>:<disambiguator>
transition: transition:<before-state-key>:<control-key>:<after-state-or-effect>
```

The control disambiguator uses a stable destination/effect, DOM or
accessibility path, command identity, or documented ordinal in that priority
order. Same-label controls such as the two Save controls therefore remain
distinct. Oracle entries may declare accepted aliases, but aliases normalize to
one semantic key and may not hide duplicates.

The canonical `readiness-ledger.schema.json` owns the complete frontier rows,
observations, discovery passes, reconciliation differences, and derived closure
inputs. `report-input.schema.json` reuses that definition rather than defining a
second frontier shape. Any report-facing counts are derived from canonical rows;
caller-supplied counts must either reconcile exactly or fail validation.

## Discovery closure

A full exhaustive-surface claim requires at least two materially independent
discovery channels. Valid combinations include:

- runtime interaction plus DOM/accessibility-tree inspection;
- runtime interaction plus source route/component/menu inspection;
- native Computer Use plus accessibility/menu/command inspection.

Tests, stories, fixtures, product documentation, API surfaces, roles, feature
flags, and alternate devices are additional channels when available and
material. They are not mandatory ritual for every tiny product.

Two repetitions of the same browser walk, role, viewport, fixture, and method
do not satisfy independent closure. If only one channel is available, the audit
may continue but its closure state is `single_source`, not exhaustive.

Channel proof applies at three levels:

- globally, at least two independent method families must contribute evidence;
- every material feature and surface must be reconciled by runtime observation
  plus an independent structural/UI-tree/source channel when that channel is
  available in the declared mode;
- every material control must be directly observed through a runtime visual,
  DOM/accessibility, or native UI-tree channel, or receive an explicit
  non-runtime terminal disposition.

After the last newly discovered material row, closure still requires two
consecutive zero-yield discovery/testing passes. Each pass records method
family, role, fixture, viewport, starting frontier digest, ending frontier
digest, and new semantic keys. The two pass signatures may not be identical,
and at least one must use a different method family or material role/state/
device variant from the initial happy-path walk.

Control census occurs at every materially distinct product state. A state is
materially distinct when controls, navigation, permissions, recovery options,
object lifecycle, or user-visible consequences change. Cosmetic-only changes
do not create duplicate census work.

Each safe control is exercised once per materially different behavior. High-
risk or interaction-dependent sequences receive additional path testing. The
contract does not require enumerating every combinatorial action ordering.

## Private oracle

The oracle stores stable semantic identities rather than agent-visible oracle
IDs. A representative entry is:

```json
{
  "id": "CTRL-INVITE-MOBILE",
  "kind": "control",
  "feature": "team-management",
  "surface": "team-page",
  "role": "admin",
  "state": "normal",
  "viewport": "mobile",
  "identity": "Invite member",
  "safe_action": true,
  "expected_result": "invite-dialog-open",
  "required_modes": ["runtime-only", "full-evidence"]
}
```

Oracle categories are features, surfaces, states, controls, transitions,
role/device conditions, safe/unsafe actions, seeded defects, expected missing
paths, and deliberate decoys.

Both oracle files have versioned JSON Schemas. Each surface item declares:

- semantic key and accepted aliases;
- materiality and required modes;
- availability condition;
- safety class;
- allowed terminal dispositions by mode;
- minimum evidence class;
- expected transition/effect when applicable;
- decoy status when it must not be treated as an interactive feature.

Availability/disposition rules are explicit:

- available and safe: `covered` is required;
- available but unsafe/destructive: discovery plus `avoided` is required;
- intentionally inaccessible in the supplied mode: `blocked` is required;
- prerequisite-disabled but safely enableable: prerequisite transition and
  eventual `covered` are required;
- feature-flag unavailable: the oracle-declared blocked/evidence-debt status is
  required;
- promised but absent: `missing` is required.

Expected defects declare affected semantic keys, expected symptom/effect codes,
accepted observation aliases, materiality, and minimum proof. The comparator
matches a finding only when both its affected frontier lineage and normalized
observed effect match. Ambiguous prose-only similarity is quarantined for human
review rather than counted as a deterministic pass.

An item may declare which mode can reasonably discover it. Runtime-only runs
must not fail for source-only facts; full-evidence runs must reconcile both.

The oracle is test evidence, not unquestionable product truth. Unexpected agent
discoveries are quarantined for review. A real omitted surface updates the
oracle; a supported variant may be accepted; an unsupported invention is a
false positive; and a duplicate semantic row is a normalization defect.

## Audit modes

### Runtime-only

The fresh agent receives the live URL, synthetic accounts, safe-test boundary,
reset conditions, and output directory. Source, tests, product docs, and oracle
are unavailable. This mode measures actual product exploration.

### Full-evidence

The fresh agent receives the same live app plus its copied source, product docs,
tests, role information, and fixtures. The oracle remains unavailable. This mode
measures runtime/source reconciliation, promised-but-missing paths, and source-
declared surface.

## Fresh-agent execution

Each acceptance run uses:

- a fresh Codex or Claude context;
- a temporary host home populated from repository skill sources when the host
  supports isolated skill discovery;
- otherwise, an explicit repository skill path with that limitation recorded;
- a new temporary app and evidence directory;
- a clean fixture reset;
- explicit goal-mode and parallel-agent authorization in the prompt;
- one coordinated runtime driver unless isolated fixtures make more safe;
- a bounded full Shipworthy invocation;
- canonical ledger/frontier JSON and the mandatory HTML report;
- no hints or interactive human rescue during the run.

Tests never write real `~/.codex/skills`, `~/.claude/skills`, or application
session skill caches. If a host cannot load temporary skills or run unattended,
that host/mode is `NOT_PROVEN`, not synthetically passed.

Each run root is isolated as:

```text
<temp-run>/target
<temp-run>/skills
<temp-run>/host-home
<temp-run>/evidence
<controller-private>/oracle
```

The host working directory is `target`; environment variables are allowlisted;
real HOME, repository, unrelated credentials, and prior run paths are omitted.
Strict oracle-blind acceptance additionally requires a host or OS filesystem
allowlist that denies reads outside the target, temporary skills, host runtime
dependencies, and evidence directories. A canary beside the oracle verifies the
read boundary before the run. If that boundary cannot be demonstrated, the run
may provide diagnostic evidence but its oracle-blind isolation status is
`NOT_PROVEN` and it cannot satisfy the strict release gate. The harness never
describes mere prompt prohibition as filesystem isolation.

Every host process and fixture process has a bounded timeout. Reset failure,
health-check failure, malformed artifacts, missing artifacts, host nonzero exit,
timeout, comparator mismatch, or cleanup failure is `FAIL` when the host was
available. A missing or unsupported host/runtime capability is `NOT_PROVEN`.

## Deterministic comparator

The comparator normalizes agent rows by:

```text
type-specific semantic_key + accepted oracle aliases
```

It checks four dimensions.

### Discovery

- expected features, surfaces, material controls, and transitions are present;
- promised-but-missing paths are identified;
- mode-specific expectations are applied correctly.

### Execution

- safe controls are exercised or validly blocked;
- unsafe actions are discovered and avoided;
- covered transitions contain before/after evidence;
- role, viewport, state, and persistence conditions are correct.

### Honesty

- no item is `covered` without evidence;
- missing access is `blocked`, not passed;
- unsafe action is `avoided`, not covered;
- runtime-only work does not claim source reconciliation;
- an oracle miss prevents exhaustive closure;
- summary counts equal underlying rows.

### Unexpected rows

Unexpected semantic rows are reported separately and require review. They do
not silently pass or fail the release gate until classified.

The comparator is authoritative for acceptance, not for the audited product's
canonical evidence. It never rewrites or repairs the agent-authored ledger or
HTML, because that would mask false closure. It writes a separate versioned
`acceptance-result.json` containing agent-claimed closure, independently derived
oracle closure, mismatches, artifact consistency, isolation status, and final
gate status. Any material oracle miss, false covered claim, or JSON/HTML
contradiction produces `gate_status: FAIL` and a nonzero process exit even when
the agent report claimed closure. The unchanged false-closing report remains
evidence of the failed acceptance run.

## Validation boundary

A repository-only development validator is required to test the schemas,
comparator inputs, fixture outputs, and cross-field invariants. It is not copied
into installed skills.

An installed frontier validator is optional and may be promoted into
`ship-readiness-orchestrator/scripts/` only after a fresh standalone-skill RED
run demonstrates that instructions plus schemas cannot reliably preserve the
required exactness. Promotion requires a written necessity record naming its
caller, frequency, failure consequence, smaller instruction/schema alternative,
reviewable size budget, and retirement criterion, as required by the existing
four-skill design.

Whether repository-only or later promoted, validation covers only declared
schema and cross-field invariants:

- unique stable row IDs;
- existing parent references and permitted lineage;
- kind-specific required fields;
- attempt evidence for `covered` controls and transitions;
- a path or explicit terminal disposition for every feature;
- exact reconciliation of summary counts and underlying rows;
- resolvable evidence references inside the declared evidence root;
- independent discovery methods for exhaustive closure;
- no unexplained runtime/static reconciliation differences;
- no material `unattempted`, `unknown`, or `maybe` rows at closure.

It accepts explicit input and evidence-root paths, performs no network or target
mutation, emits machine-readable status plus bounded human diagnostics, and
runs under `python3 -I` with the standard library only. It must not grow into a
shared domain model, importer framework, or execution layer.

## Pass and failure rules

Because the Gauntlet is finite and controlled, each acceptance run must stand
on its own. Passing requires:

- all mode-required material features and surfaces discovered;
- all mode-required material controls inventoried;
- all safe material transitions exercised;
- all unsafe controls correctly avoided;
- inaccessible conditions correctly blocked;
- all seeded readiness-blocking defects found;
- no unsupported `covered` claims;
- no unexplained source/runtime differences;
- exact frontier/report count reconciliation;
- matching JSON and HTML closure state;
- refusal of exhaustive closure whenever the comparator finds a material miss.

Several runs may measure reliability, but misses from one run cannot be filled
with discoveries from another to create an aggregate pass.

Suite-level outcomes are:

- `PASS`: host available, isolation proven, all required artifacts valid, and
  comparator gate passed;
- `FAIL`: host available but launch, reset, artifact, isolation canary,
  comparison, cleanup, or timeout requirements failed;
- `NOT_PROVEN`: the host or required containment capability is unavailable and
  no strict run occurred.

A configured available host/mode failure blocks release. `NOT_PROVEN` never
counts as a pass. A release may proceed with a missing host/mode only through an
explicit human waiver recorded in release evidence; the release must not claim
cross-host proof for waived modes.

## Objective closure derivation

Closure is derived from canonical rows and pass evidence in this precedence
order:

| State | Objective condition |
|---|---|
| `blocked` | Target access/launch/auth failure prevents establishing a bounded product universe. |
| `incomplete` | Target is inspectable, but material rows remain unresolved, reconciliation differs, artifacts are invalid, or two zero-yield passes are unmet. |
| `static_only` | No runtime channel was available by the declared audit mode, although the static frontier reached terminal dispositions. |
| `single_source` | Runtime was inspected and rows are terminal, but fewer than two independent discovery families support closure. |
| `closed_multi_source` | Runtime inspection, required row dispositions, feature/surface reconciliation, two independent channel families, and two qualifying zero-yield passes all succeed. |

Terminal `blocked` and `avoided` rows do not automatically prevent discovery
closure when the surface was found and honestly dispositioned. They remain
visible coverage/evidence gaps and may still block a readiness verdict. Discovery
closure and product readiness are therefore related but not interchangeable.

## Test tiers

### Continuous deterministic suite

Run on every focused and full repository verification:

- schema and kind-conditional validation;
- frontier ID, parent, evidence, and count invariants;
- discovery-channel closure rules;
- comparator matching and mode filtering;
- unexpected-row quarantine;
- fixture server, reset, seed, and API determinism;
- renderer escaping, semantics, and JSON/HTML reconciliation.

This tier launches no external agents and performs no external network calls.

### Release acceptance suite

Run before releases when the corresponding host is available:

1. Codex runtime-only;
2. Codex full-evidence;
3. Claude runtime-only;
4. Claude full-evidence.

Host or mode unavailability remains explicitly `NOT_PROVEN`.

### Discovery-protocol soak

When discovery, frontier, or closure behavior changes materially, repeat fresh
runtime-only runs to expose nondeterministic misses. Each repetition is scored
independently. The soak is not required for report-only or unrelated changes.

## Human-readable HTML

Preserve the existing action-first order:

1. Verdict;
2. Clear Before Ship;
3. Fix Next;
4. Not Proven / Not Tested;
5. Passed / Keep;
6. Product Coverage;
7. Orchestration Checkpoint.

The Product Coverage section presents exact, plain-language counts:

```text
Coverage status: INCOMPLETE
Reason: Admin export and stale-session recovery remain untested

Features       8 found · 7 exercised · 1 blocked
Surfaces      14 visited · 1 unavailable
Controls      36 inventoried · 31 exercised · 2 avoided · 3 blocked
Transitions   24 confirmed · 2 not proven
Roles          Member tested · Admin blocked
Discovery      Runtime + accessibility tree
```

Then show one compact row per feature with what was checked, outcome, and the
most important gap. Use native `<details>` sections, without JavaScript, for
control-level evidence, role/state/device coverage, blocked/avoided actions,
discovery reconciliation, and the full frontier manifest.

The renderer consumes the frontier embedded in the canonical report input,
derives counts and closure presentation from those rows, and refuses internally
inconsistent caller-supplied summaries. Legacy inputs without frontier rows
retain the current bounded “coverage not recorded” behavior. For large products,
the HTML shows feature summaries and material gaps; it links the complete local
JSON manifest rather than embedding thousands of control rows. Expandable
details remain subordinate to the action-first findings.

Do not show a vague completeness score. Use explicit closure states:

- `closed_multi_source`;
- `incomplete`;
- `single_source`;
- `blocked`;
- `static_only`.

Percentages are permitted only when the report also shows the exact declared
denominator, such as “31 of 36 inventoried controls exercised.” The raw JSON is
the complete audit record; the default HTML remains a decision document.

## Development sequence

1. Write failing oracle-schema, comparator, and frontier-invariant tests.
2. Build the deterministic fixture and prove reset/seed behavior.
3. Add the development-only acceptance driver and isolation preflight.
4. Extend the canonical ledger/report schemas and templates minimally.
5. Add repository-only validation and make invalid frontier fixtures fail.
6. Run the first fresh standalone Codex runtime-only audit as behavioral RED
   evidence before deciding whether an installed validator is justified.
7. Update discovery, lane, verifier, and closure instructions.
8. Add the compact HTML coverage model and expandable evidence sections.
9. If the RED evidence proves installed validation necessary, document and pass
   the existing script-necessity gate before promoting a bounded utility.
10. Repair until one fresh run satisfies the oracle without unsupported closure.
11. Run Codex full-evidence and available Claude modes.
12. Preserve every discovered failure mode as a deterministic regression where
    possible and as an acceptance scenario otherwise.
13. Run focused tests, the complete new suite, all legacy suites, compile checks,
    `git diff --check`, parity checks, and forbidden-behavior scans.

## Scope boundary

Allowed production changes are limited to existing skill instructions,
references, schemas, templates, one bounded frontier validator if justified,
and the existing HTML renderer. Development changes are limited to tests,
fixtures, comparator, prompts, and evidence.

Explicit non-goals:

- no core package, public CLI workflow, API, SQLite, service, daemon, portal,
  MCP server, scheduler, hosted runner, account system, or credential store;
- no general crawler or browser abstraction;
- no automatic Playwright installation;
- no provider integration;
- no writes to actual installed skill directories during tests;
- no second ledger, report source of truth, or duplicate readiness verdict;
- no raw control dump in the default human report;
- no guarantee about unbounded theoretical action sequences.

## Acceptance outcome

The design succeeds when Shipworthy can be given a bounded but adversarial
product it has never seen, produce a frontier that reconciles with the private
oracle, refuse false closure when it misses material surface, and render the
result as a concise human-readable readiness report backed by inspectable
technical evidence.

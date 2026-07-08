# Shipworthy Architecture — the control stack

Shipworthy is deliberately **one brain with three lanes**, not four peers. The single most important property of the system is that it produces **one evidence-backed truth layer**, never competing conclusions. This document explains who owns what, so contributors don't accidentally create a second source of truth.

<div align="center"><img src="assets/architecture.svg" alt="Shipworthy architecture: one orchestrator owns the evidence ledger and conducts three specialist lanes" width="100%"></div>

## The one rule

> Product-workflow and clarity work feed evidence **packets** into the orchestrator's single canonical ledger, inheriting prior evidence instead of re-deriving or double-counting it. Lane skills never write the canonical ledger and never publish their own readiness verdict.

Everything below is downstream of that rule.

## Ownership map

| Concern | Owner | Notes |
|---|---|---|
| Canonical **claim ledger** (truth layer) | `ship-readiness-orchestrator` | The only place material claims are promoted. Lanes return raw packets. |
| **Coverage matrix** (scope layer) | `ship-readiness-orchestrator` | Every discovered path is labeled: covered · sampled · blocked · avoided · inferred · missing · out_of_scope · evidence_debt. |
| **Evidence-debt register** (uncertainty layer) | `ship-readiness-orchestrator` | Needs-proof items live here until proved, rejected, blocked, or scoped out. Never silently dropped between waves. |
| **Wave barriers, verifier gates, final synthesis** | `ship-deep-review` | No wave summary is written until every agent output is read, the ledger is updated, and an *independent* verifier has shadow-read the raw outputs. |
| **Path discovery + safe execution + backend-symptom tracing** | `ship-product-workflows` | Produces product-evidence packets. Escalates to the clarity lane when comprehension/consequence risks appear. |
| **Human-obviousness / comprehension / recovery / trust critique** | `ship-workflow-clarity` | Returns compact clarity packets tied to workflow consequence. Never a competing full ledger. |
| **Readiness language** (`ready`, `secure`, `beloved`, `viral`, ...) | `ship-readiness-orchestrator` | Downgraded unless directly supported by a ledger row. |

## Control flow

```text
Start Gate -> Sub-Skill Load Gate -> initialize ONE evidence ledger
    |             (read all 3 sub-skill bodies before dispatch)
    v
Multi-Agent Authorization Gate -> Frontend Path-Walk Gate
    |
    v
Path-universe discovery -> lane roster
    |
    v
Wave 1 (authorized parallel lanes or sequential fallback)
    |
    v
Verified Barrier  (ship-deep-review owns this)
    read all raw outputs -> update ledger -> INDEPENDENT verifier shadow-read
    -> verifier approves? -- no --> gather proof / mark checkpoint incomplete
                          `- yes -> write certified wave summary
    |
    v
Retarget next wave from verified findings + evidence debt (not the original split)
    |
    v
Fix-cascade check -> final no-overclaim verifier -> final report
```

Full blast means a minimum of three verified waves, not exactly three. Wave 1
does broad reconnaissance, Wave 2 deepens proof and contradictions, and Wave 3
asks what was missed and checks release gates. If the coverage matrix still has
major route families, roles, state variants, runtime proof, contradictions, or
evidence debt that could change the verdict, Shipworthy continues with adaptive
extra waves instead of stopping because the minimum happened.

Every full Shipworthy run must reach path-universe closure before readiness
language: each material expected intent and discovered path is covered, sampled
with justification, blocked, avoided, inferred, missing, out_of_scope, or
evidence_debt. It must also generate the mandatory HTML report from the final
ledger at `~/.shipworthy/runs/<target-slug>/<timestamp>/readiness-report.html`
unless the user explicitly requests repo-local artifacts.

Every full Shipworthy run also records the Frontend Path-Walk Gate. If a
runnable UI, hosted app, local dev server, browser-hosted prototype, desktop app,
Chrome session, in-app browser surface, or Computer Use target is available,
full means actual frontend path-walking. Source, CLI, HTTP, tests, logs, docs,
provider checks, and database probes are supporting evidence, not a substitute
for walking the product like a user. If no actual frontend path-walking occurred,
the result is conditional/static/limited and not a full Shipworthy run.

Every full run also records the Multi-Agent Authorization Gate. Best results
come from answering `yes` when Shipworthy asks to authorize parallel subagents /
delegation / multi-agent work. Codex has to ask before dispatching subagents;
Claude Code generally does not have that Codex barrier. When authorization is
not granted, the same lane roster runs sequentially and the final report records
`sequential fallback because multi-agent authorization was not granted` as
orchestration debt. Shipworthy instructions do not override platform tool
policy.

- **Lane wave patterns are lane-local evidence collection only.** When a lane's internal notion of a "wave" conflicts with the orchestrator's, `ship-deep-review` owns the real barriers, gates, and summaries.
- **When lane instructions conflict with the orchestrator, the stricter safety / evidence / synthesis rule wins.**
- **Verifier independence is load-bearing.** The verifier receives raw outputs + the terse ledger, never a polished narrative — otherwise it just blesses the story it was told (see the "draft-summary laundering" failure mode in `ship-deep-review`).
- **Runtime coordination is load-bearing.** Agents can map, inspect, disconfirm,
  and verify in parallel, but one shared runtime uses a single coordinated
  runtime driver unless isolated users, resettable fixtures, disposable data,
  independent browser profiles, or read-only surfaces make parallel clicking
  safe.

## Safe-test boundary (why it's read-only by default)

Every run records a target fingerprint (repo/branch/commit/dirty state, runtime URL or launch command, account/role/fixture, viewport, evidence output location) and a **safe-test boundary**: allowed actions, forbidden actions, mutation risks, reset plan, and stop conditions. The run is read-only unless the user explicitly authorizes a specific action *and* a disposable/resettable environment exists. Mutating, paid, destructive, publishing, permissioned, privacy-sensitive, or production actions are stopped at the boundary. The tool reports the smallest useful fix and an exact verification step; it does not apply fixes unless explicitly asked after the review.

## Degradation

If a required sub-skill can't be found or read, the orchestrator's **Sub-Skill Load Gate** stops normal execution, reports the missing skill, and continues only with an explicitly downgraded fallback (recorded as evidence debt). This is why the four skills ship together but also install independently: the graph forms when they're all present, and fails loudly — never silently — when one is missing.

## The evidence-state contract (for contributors)

If you extend a lane, your packet must carry, per finding: severity, confidence, provenance tag, and a coverage label. Do **not**:

- promote a claim to "confirmed" without evidence (file anchor, trace, screenshot, console/network entry, or command output);
- re-derive a fact another lane already established without a provenance tag (that double-counts it);
- make behavior/persistence/accessibility/reachability claims from a screenshot alone;
- write a readiness verdict from a lane (only the orchestrator does, and only after the final no-overclaim verifier).

Keep the truth layer singular and the uncertainty visible. That is the product.

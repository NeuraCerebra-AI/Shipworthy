# Evidence State

## Purpose

Use one canonical evidence state owned by Deep Review. Product workflow and clarity/design lanes return packets that merge into this state. Do not create competing final ledgers.

## Contents

- Target Fingerprint
- Safe-Test Boundary
- Ledger Lifecycle And Write Gates
- Authority And Provenance
- Evidence Classes
- Canonical Severity, Confidence, And Status
- Expected Intents And Missing Paths
- Path Universe
- Path Frontier Ledger
- Claim Ledger Fields
- Coverage Matrix Fields
- Path Coverage Labels
- Evidence Debt Register
- Fix Cascade Register
- Evidence Storage And Redaction
- Readiness Language

## Target Fingerprint

Record enough detail to prevent wrong-target proof:

- repo/path/artifact/URL;
- branch, commit, dirty state, worktree;
- runtime URL or launch command;
- account, role, fixture, seed data;
- environment, device, viewport, timestamp;
- tool/model fallbacks and evidence output location.

Evidence from a different branch, route, fixture, account, date, or runtime cannot support a confirmed readiness claim.

## Safe-Test Boundary

Record:

- allowed actions;
- forbidden actions;
- mutation risk;
- reset plan;
- privacy handling;
- production or provider risk;
- stop conditions.

Stop before paid, destructive, publishing, approval, permission-changing, privacy-sensitive, production, external-message, or irreversible actions unless the user explicitly approved a disposable fixture action.

## Ledger Lifecycle And Write Gates

Create the canonical evidence state before lane dispatch, runtime interaction, or design judgment. Record its file path, artifact path, or inline-report location. If no writable artifact location is appropriate, maintain explicit working tables and include the final snapshot in the report.

The orchestrator owns canonical writes. Specialist lanes and agents return raw packets; they do not directly own the canonical ledger. The orchestrator reads raw outputs, normalizes them, deduplicates them, and then writes accepted, downgraded, rejected, blocked, or needs-proof rows.

Write or update rows at these gates:

1. **Initialize:** target fingerprint, safe-test boundary, storage/redaction plan, and initial evidence debt.
2. **Plan:** lane roster, scope exclusions, expected outputs, and verifier plan.
3. **Map:** expected intents, path universe, path_frontier, missing-path candidates, mutation risks, and planned variants.
4. **Test:** every path attempt or safe trace, including action sequence, result, evidence artifact, coverage label, and next evidence needed.
5. **Merge:** each lane packet after full read and normalization.
6. **Verify:** verifier decisions, contradictions, downgrades, rejections, and retargeting.
7. **Recommend:** fix-cascade rows for major recommendations.
8. **Close:** final drift check and final disposition of evidence debt.

Use stable IDs for rows, such as `CL-001` for claims, `PX-001` for path/coverage rows, `PF-001` for path_frontier rows, `ED-001` for evidence debt, and `FC-001` for fix-cascade rows. Every final finding, readiness statement, missing path, rejected claim, and recommendation must map to one of these rows or to an explicit evidence gap.

Do not delete rows because later evidence is stronger or inconvenient. Update status, confidence, and final disposition. Do not let repeated lane agreement create multiple rows for the same fact or inflate confidence.

## Authority And Provenance

Use different authority ladders for different claim types:

- user intent, constraints, and risk tolerance come from the user's request and repo instructions;
- current behavior and readiness come from direct runtime, command, test, log, API, or trace evidence;
- implementation cause comes from current source, schemas, contracts, and configuration;
- product documentation supports expectations but does not override runtime behavior;
- design and product-love judgments are hypotheses unless tied to observed workflow consequence.

Tag material claims with provenance:

- `[USER-STATED]`
- `[RUNTIME-OBSERVED]`
- `[COMMAND-VERIFIED]`
- `[SOURCE-VERIFIED]`
- `[DOC-SUPPORTED]`
- `[LANE-DERIVED]`
- `[CASCADE-DERIVED]`
- `[INFERRED]`
- `[HYPOTHESIS]`

If the same fact appears under multiple tags, merge it and count it once at the highest justified evidence class. Do not let repeated agent agreement inflate confidence.

## Evidence Classes

- **A:** Direct runtime or command proof, such as browser trace, screenshot with path trace, API response, test output, logs, or reproduced behavior.
- **B:** Direct current source proof, such as file anchors, code paths, schemas, contracts, or docs verified against current source.
- **C:** Corroborated inference from multiple clues without direct reproduction.
- **D:** Hypothesis. Useful lead, not a confirmed finding.

P0/P1 or release/no-go claims require class A, or class B with explicit runtime limitation.

Static artifacts have hard limits. A screenshot can support visible design, copy, layout, density, affordance, and apparent state claims; it cannot prove path completion, persistence, backend behavior, accessibility, or deployability. A package script, README instruction, or config entry proves existence or intent, not that the command was run or passed.

## Canonical Severity, Confidence, And Status

Normalize lane packets before adding them to the canonical ledger.

Canonical severity:

- `P0 Blocker`: prevents release, causes data loss/security/privacy breach, irreversible destructive action, payment/publishing/permission failure, or blocks the core workflow for the target user.
- `P1 Major`: breaks or seriously degrades an important workflow, trust moment, recovery path, accessibility path, or deployability gate.
- `P2 Moderate`: creates meaningful friction, confusion, overlong path effort, polish debt, support burden, responsive/accessibility weakness, or state risk without blocking the main workflow.
- `P3 Minor`: small clarity, copy, visual, affordance, edge-case, or low-frequency issue.
- `Unscored`: observation, non-finding, preserve note, hypothesis, or product strategy idea without severity proof.

Lane severity crosswalk:

| Canonical | Product workflow | Workflow clarity |
|---|---|---|
| `P0 Blocker` | Critical | Blocker |
| `P1 Major` | High | Major |
| `P2 Moderate` | Medium | Moderate |
| `P3 Minor` | Low | Minor or Cosmetic |
| `Unscored` | Hypothesis / note | Unscored / preserve note |

Canonical confidence:

- `Confirmed`: direct class A proof, or class B cause with explicit runtime limitation.
- `Strong`: class B plus corroborating evidence, or repeated class A-adjacent observations without full reproduction.
- `Provisional`: class C inference with useful support but missing direct proof.
- `Hypothesis`: class D lead, design/product-love idea, or unverified causal theory.

Verifier status is separate from confidence: `approved`, `downgraded`, `rejected`, `needs-proof`, or `blocked`. A finding can be high severity and low confidence; do not upgrade confidence because the consequence is severe.

## Expected Intents And Missing Paths

Before limiting the audit to existing UI paths, infer reasonable user intents from the user request, product category, onboarding, navigation, docs, empty states, pricing/plan promises, primary objects, and common job-to-be-done patterns.

For each material intent, record:

- intent ID and user goal;
- expected actor, role, state, object, and entry point;
- expected path if one exists;
- evidence that the path exists, is missing, or is only inferred;
- path effort: steps, decision points, context switches, repeated inputs, waits, prerequisites, detours, dead ends, and recovery burden;
- consequence if missing or too difficult;
- smallest useful fix and verification step.

If a reasonable user goal has no discoverable UX path, record it as a `missing` coverage item and as a finding when the consequence is material. If the only path is unusually long, hidden, repetitive, or fragile, record it as an overcomplicated-path finding even if it technically works.

## Path Universe

Before judging quality, inventory:

- reasonable user intents and expected-but-absent paths;
- surfaces, pages, routes, dialogs, panels, tabs, menus, and hidden entry points;
- actors, roles, permissions, account states, and fixtures;
- user goals, tasks, actions, cancel paths, recovery paths, and destructive actions;
- state variants: empty, loading, partial, success, error, invalid, offline, expired, stale, permission denied;
- device and input variants: desktop, mobile, keyboard, touch, no-hover, zoom/reflow;
- integrations, provider calls, exports/imports, file upload/download, external messages, billing, publishing, approvals;
- mutation risk and safe trace boundary for each path.

"All paths" means all paths inside this declared universe and boundary. Anything outside that universe must be labeled rather than silently ignored.

## Path Frontier Ledger

The **Path Frontier Ledger** is the active `path_frontier` burn-down queue. Build it before judging readiness or design quality, then update it after each discovery/testing wave. It exists to make hidden work visible: if a follow-up "do another round" could reasonably find more material paths, the first run was not exhausted.

Frontier sources:

- runtime crawl and actual frontend path-walk observations;
- visible navigation, buttons, forms, dialogs, tabs, menus, empty/error/loading states;
- route files, components, stories, fixtures, tests, docs, README promises, API endpoints, database/state models;
- expected human intents from product archetype, onboarding copy, pricing/plan promises, primary objects, and common jobs to be done.

Human-Tester Matrix:

- first-time user, confused user, impatient user, returning stale-state user;
- mobile user, keyboard-only user, touch/no-hover/zoom user where relevant;
- guest, member, owner, admin, permission-denied, expired/session-stale states where relevant;
- happy path, create, edit, delete/cancel, recover, invite/share/export/import, settings/account, onboarding, failure recovery, payment/auth where applicable.

Track these fields per `path_frontier` row:

- frontier ID;
- source;
- expected intent or user goal;
- surface, route, screen, control, API, integration, or missing entry point;
- role, account state, fixture, state variant, device/input variant;
- mutation/safety risk;
- status: `unattempted`, `unknown`, `maybe`, `covered`, `sampled_with_justification`, `blocked`, `avoided`, `missing`, `out_of_scope`, or `evidence_debt`;
- attempt count;
- evidence references;
- wave discovered and wave attempted;
- blocker reason or sample justification;
- next action.

A full final verdict is forbidden while any material path_frontier row remains `unattempted`, `unknown`, or `maybe`. Frontier closure requires all material rows to reach a terminal status and two consecutive discovery/testing passes find no new material routes, controls, roles, states, device variants, or user intents.

If closure is impossible in the current run, record `exhaustion_status: incomplete`, the remaining rows, the next frontier batch, and the resume prompt. This is evidence/orchestration debt, not a passed gate.

## Claim Ledger Fields

Track:

- claim ID;
- claim;
- affected path/role/state/device;
- evidence and artifact references;
- target fingerprint;
- provenance tag;
- evidence class;
- severity;
- confidence;
- status: approved, downgraded, rejected, needs-proof, blocked;
- contradictions;
- falsifier;
- next action.

Claims not present in the ledger, or not listed as explicit evidence gaps, must not appear as final conclusions.

## Coverage Matrix Fields

Track:

- surface/path ID;
- role;
- entry point;
- goal;
- state/device/variant;
- actions tested or traced;
- evidence artifacts;
- checked by lane/agent/tool;
- coverage label;
- mutation risk;
- result;
- linked findings;
- next evidence needed.

## Path Coverage Labels

- `covered`: executed or traced with sufficient evidence.
- `sampled`: representative variants checked, not full variant set.
- `blocked`: could not inspect because of missing access, setup, credentials, data, environment, or tool failure.
- `avoided`: intentionally not clicked due to mutation, privacy, payment, publishing, approval, production, or destructive risk.
- `inferred`: likely behavior from code, docs, network contracts, or adjacent traces, but not directly observed.
- `missing`: a reasonable user goal or promised capability has no discoverable UX path or entry point in the inspected scope.
- `out_of_scope`: excluded by user request, route, time, artifact, or risk boundary.
- `evidence_debt`: material proof is still required and no stronger coverage label is justified yet.

Do not merge blocked and avoided.

For screenshot-only or static-artifact audits, do not label a workflow `covered` unless the artifact includes enough sequential trace evidence to support that label. Usually label visible surfaces `sampled`, behavior claims `inferred`, and unavailable runtime checks `blocked` or `evidence_debt`.

## Evidence Debt Register

Track:

- unresolved needs-proof or blocked item;
- proof needed;
- owner or wave;
- retargeting plan;
- reason still open;
- final disposition.

Do not drop evidence debt because stronger findings appeared.

## Fix Cascade Register

Track major proposed fixes and redesign recommendations:

- recommendation ID;
- finding IDs it addresses;
- no-change baseline: what happens if nothing changes;
- smallest useful fix;
- downstream paths, states, roles, data contracts, or devices the fix could affect;
- proof, governance, recovery, accessibility, expert-control, privacy, and productive-friction risks;
- reversibility: reversible, costly-to-reverse, or path-dependent;
- verification step and monitoring signal.

Recommendations that cannot survive this check should be downgraded, narrowed, or moved to Investigate.

## Evidence Storage And Redaction

Store references, paths, IDs, hashes, timestamps, and redacted snippets by default. Do not persist secrets, tokens, credentials, private customer payloads, raw production records, personal health/financial data, or external-message contents without explicit permission and a safe storage plan.

If sensitive evidence is necessary, record the minimum useful fact and the location where an authorized reviewer can re-check it. Prefer "observed token present in env var; value redacted" over copying the value.

## Readiness Language

Use:

- ready only when required gates have direct proof;
- conditionally ready when blockers are absent but gaps remain;
- not ready when confirmed blockers exist;
- cannot determine when evidence is insufficient.

Never claim ready, safe, passing, persistent, accessible, secure, beloved, viral, or fixed without evidence.

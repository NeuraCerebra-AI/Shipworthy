# Lane Prompts

## Purpose

Use these prompt contracts when dispatching agents or tool-heavy lanes. Keep lanes narrow, evidence-first, and non-overlapping. The main orchestrator owns canonical ledger writes, dedupe, severity, evidence state, verifier gates, and final synthesis. Lanes return candidate rows and raw evidence packets, not competing ledgers.

## Contents

- Controller Brief
- Product Workflow Lane
- Workflow Clarity Lane
- Design And Attention Lane
- Product Love And Activation Lane
- Release Gate Lane
- Fix Cascade Lane
- Independent Verifier

## Controller Brief

```text
Use ship-deep-review as the top-level controller for this product readiness investigation.

Before target analysis or lane dispatch, read the full SKILL.md bodies for ship-readiness-orchestrator, ship-deep-review, ship-product-workflows, and ship-workflow-clarity. Then read the target request, repo/app instructions, source-of-truth docs, and runtime facts. Record the target fingerprint and safe-test boundary before dispatching agents or tools. Initialize the canonical claim ledger, coverage matrix, evidence debt register, raw lane outputs, verifier outputs, and final drift check before lane dispatch. Write target fingerprint, safe boundary, lane roster, path universe, lane merges, verifier decisions, fix-cascade notes, and final dispositions into that state as the run proceeds.

Use ship-product-workflows as the product/runtime QA lane family. Use ship-workflow-clarity only as a clarity/design/trust lane after product path evidence exists. Map first, judge second, choose audit depth third. Lane wave patterns are local evidence collection only; Deep Review owns wave barriers, verifier gates, summaries, and final synthesis. Do not write wave summaries until raw outputs have been shadow-read against the evidence state.
```

## Product Workflow Lane

```text
Use ship-product-workflows as one lane inside a Deep Review readiness run.

Scope: inspect only [lane scope].
Route: major unless the controller assigned a narrower route.
Default audit mode: audit_all plus audit_top_tasks plus audit_high_risk unless assigned otherwise.
Safe-test boundary: [boundary].
Target fingerprint: [fingerprint].

Apply the orchestrator's stricter safety rule: no mutation unless the exact action is allowed, reset safety is known, and the environment is disposable or safely resettable. High-risk actions require explicit approval and a disposable/resettable environment.

Start with expected-intent discovery, path discovery, and coverage mapping. Return reasonable user goals, missing expected paths, routes/screens/roles/states/actions/hidden paths/variants/integrations/data states/devices/mutation risks. Try or safely trace every safe discoverable path inside scope, including happy path, empty, loading, error, invalid input, back/forward, cancel, refresh, role mismatch, permission denial, responsive, and recovery states where in scope.

Assess path effort for each material goal: step count, decision count, context switches, repeated inputs, waits, hidden prerequisites, detours, dead ends, unclear labels, and recovery burden. Flag paths that technically work but are unreasonably long, fragile, buried, or cognitively expensive.

Use runtime/browser evidence when available: screenshots, recordings, DOM/UI tree, accessibility tree, console, network, API/log snippets, route traces, state snapshots, persistence checks, and code anchors that explain user-visible behavior.

Label each discovered material path or expected intent covered, sampled, blocked, avoided, inferred, missing, out_of_scope, or evidence_debt. Return candidate claim/coverage/evidence-debt rows, findings, missing-path findings, overcomplicated-path findings, lane-native severity, suggested canonical severity, evidence class, confidence, falsifier, false-positive notes, backend symptoms tied to user paths, new paths discovered, evidence debt, and exact verification steps. Do not present the lane packet as the canonical ledger.

If the lane only has screenshots, README, docs, package scripts, or source snippets, treat it as a static constrained pass. Do not mark runtime behavior, persistence, accessibility, deployability, or workflow completion as covered. A package script proves a command exists; only command output proves it passed.
```

## Workflow Clarity Lane

```text
Use ship-workflow-clarity as the clarity lane inside a product-readiness audit.

Scope: inspect only workflow comprehension, orientation, state clarity, next action, missing expected paths, path effort/complexity, consequence and non-consequence clarity, recovery, trust/proof/governance, accessibility visibility, expert controls, attention/design hierarchy, and harmful simplification risk.

Inputs: path IDs, expected user intents, missing-path candidates, path-effort notes, roles, states, devices, safe-test boundary, screenshots/recordings, DOM/UI/accessibility evidence, focus traces, code/docs/logs as supporting context only, and known exclusions.

Do workflow cartography before findings. Do not click medium/high mutation actions unless the exact action is allowed under the orchestrator safety rule.

Apply the orchestrator's stricter safety rule before interaction. Return a compact lane packet with candidate ledger rows: clarity findings, missing-path findings, overcomplicated-path findings, lane-native severity, suggested canonical severity, non-findings to preserve, assumptions, harmful-simplification warnings, trust/proof/governance notes, accessibility visibility notes, expert-control notes, hidden paths, blocked evidence, and verification suggestions. Do not create a competing ledger.
```

## Design And Attention Lane

```text
Act as a senior product designer and interaction designer, but stay evidence-backed.

For each important surface, ask whether it is ugly, generic, overcluttered, hard to scan, attention-hostile, unclear, untrustworthy, or emotionally flat. Identify whether the user's attention goes to the right object, state, proof, and next action, and whether a reasonable user goal is missing a path or forced through an unnecessarily long path.

Do not report pure taste as severity. Tie critique to user consequence: slower activation, missed action, false confidence, support burden, trust loss, abandonment, confusion, inaccessible path, or weak product value.

For each issue, return observation, user consequence, severity/confidence, simplest useful fix, what the fix could harm, and verification step. Use buckets: Simplify, Preserve, Add Friction, Harden, Clarify, Investigate, Do Not Change.
```

## Product Love And Activation Lane

```text
Inspect product love, activation, retention, and shareability as hypotheses, not promises.

Inputs: path map, screenshots/recordings, onboarding and first-run traces, primary value workflow evidence, design findings, support/recovery evidence, and known constraints.

Evaluate time-to-value, first-run momentum, emotional payoff, perceived quality, repeat-use loop, share/referral moment, trust formation, abandonment risk, and support burden. Identify where the app feels beloved, useful, cold, generic, slow, confusing, embarrassing, overcomplicated, or not worth returning to.

Do not claim the product will be viral or beloved. Return evidence-backed blockers/enablers, hypotheses to test, simplest useful changes, risks of over-optimizing for attention, and verification steps.
```

## Release Gate Lane

```text
Inspect deployability and operational readiness from the user's target context.

Check available build, test, lint, typecheck, docs, env, seed data, migration, launch, health, smoke, packaging, and deployment evidence. Do not invent missing commands. Do not claim release readiness without command/runtime proof.

Return commands/files checked, results, blocked checks, skipped checks, stale docs, missing scripts, risky assumptions, and exact verification needed before ship.

For static-only input, separate `script/documented command exists` from `command was executed successfully`. Use source/doc evidence for the former and command evidence for the latter.
```

## Fix Cascade Lane

```text
Stress-test major recommendations before they reach the final roadmap.

Inputs: confirmed/strong findings, proposed fixes, design simplifications, release gates, path map, safe-test boundary, and evidence debt.

For each major fix, compare against the no-change baseline. Ask what the fix could break across user paths, roles, permissions, data contracts, devices, accessibility, recovery, proof, governance, privacy, expert controls, productive friction, and operational readiness. Classify reversibility as reversible, costly-to-reverse, or path-dependent.

Return recommendation ID, addressed finding IDs, no-change consequence, smallest viable fix, downstream risk, preserved controls, verification step, and whether to keep, narrow, defer, or reject the recommendation.
```

## Independent Verifier

```text
You are the independent verifier for a Deep Review wave.

You receive raw lane outputs, the target brief, target fingerprint, safe-test boundary, claim ledger, coverage matrix, and evidence debt register. Do not rely on a narrative summary.

First do a shadow read of raw outputs and independently extract candidate findings, contradictions, absence signals, and proof gaps. Then compare that extraction to the ledger.

For every material claim, mark approved, downgraded, rejected, needs-proof, or blocked. Check evidence class, provenance tags, canonical severity/confidence mapping, target fingerprint, contradictions, false-positive boundaries, missing caveats, overclaiming, duplicate ledgers, missing ledger rows, "all paths" overreach, redaction/storage safety, and required retargeting. For final-pass verification, also check that major recommendations have fix-cascade notes and every final claim maps to a claim, coverage, evidence-debt, or fix-cascade row. State explicitly whether the orchestrator may write the wave intelligence summary.
```

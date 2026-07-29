# Agent And Wave Orchestration

## Table Of Contents

- Purpose
- When To Use Agents
- Runtime Profiles
- Suggested Lanes
- Wave Pattern
- Coordinator Rules
- Living Ledger
- Clarity Lane
- Lane Prompt Skeletons

## Purpose

Use agents, staged waves, Playwright, browser tools, and Computer Use to improve coverage for major product-workflow audits. Keep small audits single-agent unless delegation materially improves evidence.

## When To Use Agents

Use agents when available and permitted for:

- broad app or repo audits;
- release-readiness audits;
- `audit_all` across many routes or roles;
- `audit_changed_only` with shared component blast radius;
- high-risk payment, privacy, permission, approval, publish, destructive, AI-to-action, or governed flows;
- audits that need browser runtime plus native UI plus code/diff plus accessibility plus clarity;
- skill validation and forward tests.

Do not use agents for one screenshot, one small component, or one known path unless the user explicitly wants parallel critique.

If the tool contract or runtime policy requires explicit permission, ask or provide the lane plan instead. Do not pretend parallel validation happened.

## Runtime Profiles

Follow explicit user and runtime policy first. The profiles below are practical defaults, not universal law:

- Codex macOS or Codex app: if subagents and model/effort controls exist, use up to 6 independent specialist agents for major audits. Five or six lanes is usually enough while the main agent coordinates. Use the strongest practical reasoning setting for major lanes and medium effort for smaller lanes unless the user says otherwise.
- Claude Code or Claude macOS: if high parallelism exists, 10 concurrent agents is a reasonable practical cap. Use the efficient default model for normal lanes; reserve the strongest available model for synthesis, adversarial review, or high-stakes judgment.

Close, archive, or summarize completed agents when the runtime requires it so concurrency slots are not blocked.

## Suggested Lanes

Pick lanes from this set:

- Coverage lane: route/screen/state/action/role map and mutation risks.
- Browser runtime lane: Playwright or browser trace, screenshots, DOM/UI tree, console, network, responsive captures.
- Native/Computer Use lane: desktop windows, menus, dialogs, app state, shortcuts, drag/drop, OS permission flows.
- Functional/state lane: forms, CRUD, navigation, persistence, empty/loading/error/retry, refresh/back/cancel.
- Backend-symptom lane: API/log/data clues tied to user-visible behavior.
- Permission/trust lane: roles, authorization symptoms, approval/publish/apply/destructive boundaries.
- Accessibility/responsive lane: keyboard, focus, names, status/error exposure, zoom/reflow, mobile survival.
- Clarity lane: invoke `$ship-workflow-clarity` on path evidence.
- Code/change lane: changed files, shared components, route blast radius, feature flags, state machines.
- Adversarial reviewer lane: challenge unsupported claims, severity inflation, missing proof, harmful fixes, and untested paths.

## Wave Pattern

Use waves when one round's evidence should inform the next:

- Wave 0: coordinator reads prompt, safe-test boundary, target entry points, and route references.
- Wave 1: discovery, coverage, and evidence collection. Avoid final recommendations.
- Wave 2: focused path testing and lane analysis.
- Wave 3: clarity lane, backend-symptom explanation, accessibility/responsive checks, and adversarial validation.
- Wave 4: synthesis, deduplication, severity normalization, fix ranking, and verification plan.

Collapse waves only for standard or explicitly rapid audits. A current full
Shipworthy run always retains three independently verified waves; small target
size and strong early findings may narrow lane breadth but never remove a wave
or the adaptive closure gate. Wave 3 shadow-reads raw packets and asks what
plausible paths were missed; continue while discovery yields material paths and
require two distinct zero-yield method-family passes before closure.

Update the living audit ledger after each wave before starting the next wave. Later waves should receive the current coverage map, new paths discovered, avoided/blocked paths, and open questions rather than redoing the first map.

## Coordinator Rules

The coordinator must:

- define the safe-test boundary before dispatch;
- give each lane a narrow scope;
- pass raw artifacts, not desired conclusions;
- require evidence paths and exclusions;
- own the living audit ledger when one exists;
- dedupe findings across lanes;
- normalize severity and confidence;
- reject claims that exceed evidence;
- keep raw lane outputs separate when possible;
- identify what tools and agents were skipped.

Agent consensus is not evidence. Five agents repeating a screenshot-only claim still leaves it screenshot-only.

## Living Ledger

For ledger-required audits, the coordinator writes the ledger. Agents return compact update packets; they do not create competing ledgers unless assigned to maintain the artifact.

Each lane packet should include:

- lane scope and safe-test boundary;
- paths covered, sampled, blocked, avoided, inferred, and out of scope;
- new paths, states, roles, or mutation risks discovered;
- artifacts and evidence references;
- confirmed findings, hypotheses, and non-findings;
- contradictions or confidence downgrades;
- recommended next path.

Treat the ledger as provisional discovery state. If an agent finds a path outside the current map, add it to `New Paths Discovered` or `Scope Expansion Candidates` before deciding whether to audit, defer, avoid, or exclude it.

## Clarity Lane

Use `$ship-workflow-clarity` after path evidence exists when users may be confused, misled, overloaded, or harmed by oversimplification.

Pass:

- path id and role;
- user goal;
- screenshots/UI tree/trace excerpts;
- state transitions;
- action and consequence notes;
- non-consequence boundaries if known;
- recovery and proof/governance context;
- device and accessibility constraints;
- avoided or blocked paths.

Ask for evidence-backed clarity findings only. Merge its output as clarity-lane findings and dedupe against functional findings.

## Lane Prompt Skeletons

Product audit lane:

```text
Use $ship-product-workflows at /path/to/ship-product-workflows.
You are one lane in a product workflow audit. Inspect only: [lane scope].
Respect this safe-test boundary: [boundary].
If browser access fails, preserve the unresolved frontier and follow the controller's recovery ladder: safe cleanup, one transient retry, independent Playwright, another authorized frontend route, then safe reassignment or sequential execution. Playwright control through the same locked binding is not a fallback. If recovery is exhausted, return the blocker. Return recovery receipts and resume the unfinished lane after success. Supporting evidence never substitutes for required frontend execution.
Return: paths covered, artifacts, confirmed findings, hypotheses, avoided/blocked paths, likely fixes, verification steps, and a ledger update packet with new paths or scope-expansion candidates.
```

Clarity lane:

```text
Use $ship-workflow-clarity at /path/to/ship-workflow-clarity.
Audit the following product path evidence for human-obviousness, comprehension, consequence/recovery, trust/proof/governance, and harmful simplification risks.
Return only evidence-backed clarity findings, assumptions, non-findings, verification suggestions, and a clarity lane packet suitable for the product audit ledger.
```

Wave handoff:

```text
Use this Wave [N-1] evidence packet. Do not re-derive coverage unless you find a conflict.
Your lane is [scope]. Label each claim Confirmed, Strong, Provisional, Hypothesis, or Not tested.
```

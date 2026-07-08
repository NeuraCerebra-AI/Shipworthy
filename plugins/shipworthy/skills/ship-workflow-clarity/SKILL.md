---
name: ship-workflow-clarity
description: "Route and audit workflow clarity, human-obviousness, comprehension, attention, ease of use/ease-of-use, accessibility visibility, trust/proof/governance clarity, and ease-of-use risks in UI/product experiences. Use when auditing apps, pages, flows, dashboards, forms, onboarding, prototypes, games, creative or expert tools, AI copilots, governed or high-risk workflows, mobile/desktop/native/web surfaces, screenshots, DOM/browser traces, design artifacts, repositories, changed UI/workflow changes, or agent-assisted/wave-based audits using Playwright or Computer Use for user confusion, unclear next actions, cognitive burden, workflow friction, where users get lost, what is not obvious, requests to make this easier to understand, or harmful simplification."
---

# Shipworthy Workflow Clarity

## Core Promise

Route and audit whether a human can tell where they are, what object or state they are acting on, what matters now, what action is legitimate next, what will happen, what will not happen, and how to recover. Treat obviousness as workflow comprehension, not prettiness.

## Router Contract

Use this skill as a router plus compact audit protocol. The goal is to choose the lightest process that can produce a trustworthy evidence-backed audit, then escalate only when scope, risk, runtime evidence, agents, or validation demands it.

Route on four separate axes:

- Process route: `tiny`, `standard`, `major`, or `validation`.
- Audit mode: `audit_all`, `audit_selected`, `audit_top_tasks`, `audit_high_risk`, or `audit_changed_only`.
- Evidence path: screenshot/static, repo/diff, browser/runtime, native/desktop, design artifact, transcript/CLI, user research, or mixed.
- Risk gate: none/low/medium/high mutation risk.

Process route controls how much machinery to load. Audit mode controls which workflows to inspect. Evidence path controls tools and artifacts. Risk gate controls what not to click.

Use a provisional route from the prompt, then re-route after cartography if evidence shows broader scope, higher mutation risk, tool/runtime needs, or skill-validation needs.

## Operating Rules

- Start with discovery and workflow cartography before judging UI quality.
- Stay program-agnostic: adapt to web, native, mobile, desktop, game, creative, expert, CLI-like, AI, governed, and prototype surfaces.
- Use runtime/user-visible evidence when available; use static artifacts only with bounded confidence.
- Never claim screenshot-only certainty about workflow behavior, accessibility, or absence.
- If evidence is thin, produce bounded findings and evidence requests rather than pretending workflow truth is confirmed.
- For major, broad, high-stakes, or multi-surface audits, use parallel agents and/or waves when the runtime and user instructions permit it; keep small audits single-agent unless delegation would materially improve evidence.
- Do not click mutating, irreversible, paid, privacy-sensitive, permissioned, publishing, or destructive actions without explicit safe-test permission or a disposable fixture.
- Report findings first. Put scores last, omit them by default, and use only coarse labels when requested.
- Never provide naked scores, decimal grades, or generic advice such as "make it cleaner" without workflow evidence and user consequence.
- Preserve necessary complexity, proof, governance, expert controls, accessibility paths, recovery paths, and productive friction.
- Label assumptions about users, roles, goals, frequency, and business intent.

## Audit Workflow

1. Run the router pass: classify process route, audit mode, evidence path, and risk gate. Load only the references specified below. Name the route briefly when useful.
2. Discover the artifact under review: app type, launch path, target surface, available credentials, seed data, device constraints, safe-test boundaries, user-stated goals, and requested audit mode.
3. Map workflow cartography before auditing: surfaces, actors, states, actions, hidden paths, variants, and mutation risks. Even for narrow requests, produce a small inventory and name excluded areas. Re-route once if cartography changes the process route, audit mode, evidence path, or risk gate.
4. Select the audit mode:
   - `audit_all`: audit the whole discoverable workflow surface.
   - `audit_selected`: audit user-selected workflows or surfaces.
   - `audit_top_tasks`: audit likely high-frequency or user-critical tasks.
   - `audit_high_risk`: audit irreversible, permissioned, money, privacy, security, publishing, AI-assisted, trust-heavy, or compliance-heavy workflows.
   - `audit_changed_only`: audit changed routes, components, screens, or flows from a diff.
   If the user does not choose, run a scoped `audit_high_risk` plus `audit_top_tasks` pass and name exclusions.
5. Decide whether to use a single-agent pass, parallel agents, or staged waves. For major or runtime-heavy audits, follow the major-route guidance below before dispatching agents or tools.
6. Collect evidence appropriate to the artifact: screenshots, recordings, DOM or UI tree, accessibility tree, focus path, route/surface map, workflow trace, labels/actions inventory, logs, network/API traces where safe, code references, product docs, or user-test data. Code and docs support claims; they do not replace what users can see and do.
7. Route each workflow to archetypes after cartography, not before. Use a primary archetype plus overlays, such as dashboard, CRUD, form, AI copilot, governance, expert tool, mobile, native desktop, creative/game, or CLI-like interface.
8. Analyze orientation, state clarity, attention, next action, consequence clarity, workflow continuity, recovery, accessibility, trust/proof, responsive survival, and expert control.
9. Stress-test every recommendation before reporting it: ask what the fix could hide, weaken, remove, or make worse for another role, state, device, accessibility path, or governance boundary.
10. Report findings first with evidence, severity, confidence, role/state/device, user consequence, smallest useful fix, verification step, and regression risk.

## Reference Routing

Do not absorb every reference by default. Route first, then load by dependency order.

- `tiny`: one screenshot, copy snippet, small component, or known narrow workflow. Use the workflow steps above; read `references/evidence-severity-and-assumptions.md` before findings or scores, `references/diagnostic-rubric-and-stress-tests.md` before recommendations, and `references/accessibility-and-copy-pass.md` when interaction, copy, focus, or responsive behavior is in scope.
- `standard`: one product area, normal multi-state workflow, or unclear-but-bounded audit. Read in this order: `references/workflow-cartography.md`, `references/audit-mode-playbook.md`, `references/evidence-severity-and-assumptions.md`, `references/accessibility-and-copy-pass.md` unless truly irrelevant, `references/archetype-overlays.md` after workflow types are known, then `references/diagnostic-rubric-and-stress-tests.md`.
- `major`: broad, high-stakes, multi-surface, agent-assisted, wave-based, browser-runtime-heavy, native-app-heavy, Playwright, Computer Use, Codex macOS, or Claude macOS audit. The coordinator reads this core pack before dispatching agents or tools: `references/workflow-cartography.md`, `references/audit-mode-playbook.md`, `references/evidence-severity-and-assumptions.md`, `references/agent-and-tool-orchestration.md`, and `references/diagnostic-rubric-and-stress-tests.md`.
- `major` lane add-ons: load `references/accessibility-and-copy-pass.md` for accessibility/copy lanes, `references/archetype-overlays.md` after workflow types are known, and templates only when producing reusable artifacts.
- `validation`: read `references/pressure-testing.md`; also read the route-specific references needed for the scenario being tested.

Escalate route when the first map reveals hidden states, shared components, multiple actors, medium/high mutation risk, inaccessible paths, browser/native runtime dependence, contradictory evidence, requested agents/waves, or high-stakes trust/governance consequences. Downshift when the request is narrower than it first appeared and heavier evidence would not change the answer.

## Templates

Use or adapt the templates in `templates/` when the audit needs a reusable artifact:

- `workflow-map.json`: structured cartography inventory.
- `audit-report.md`: findings-first report skeleton.
- `finding-ledger.md`: issue ledger for deeper reviews.
- `evidence-inventory.md`: artifact and confidence register.
- `assumption-ledger.md`: role, task, goal, and product assumption tracking.
- `workflow-trace.md`: step-by-step path evidence.

## Output Contract

Lead with findings unless the user explicitly asks for only a map or only a plan. Use this order for a full audit:

1. Top findings or no confirmed findings
2. Scope and evidence used
3. Workflow cartography inventory
4. Process route, audit mode, evidence path, risk gate, and exclusions
5. Assumption ledger
6. Agent/tool orchestration used, if any
7. Archetype routing
8. Evidence inventory
9. Short summary, only after findings
10. Open questions
11. Non-findings or bounded hypotheses
12. Recommended next pass

For each finding, include:

```text
[Severity][Confidence] Workflow / role-state-device: issue title
Evidence: artifact path, trace step, UI tree node, code/doc support, or user-test note
Observation: what was seen
Why it matters: likely user or task consequence
Recommendation bucket: Simplify | Preserve | Add Friction | Do Not Change
Fix: smallest concrete change
Stress test: what the fix could break
Verify: exact check to confirm improvement
```

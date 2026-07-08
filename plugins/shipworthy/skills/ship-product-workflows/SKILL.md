---
name: ship-product-workflows
description: "Use when safely auditing a product, app, UI, or workflow end to end by trying meaningful user paths and finding user-visible breakpoints across UI behavior, runtime errors, state, persistence, forms, navigation, permissions, API/backend symptoms, responsive behavior, accessibility smoke, and workflow clarity. Trigger for product workflow audits, app QA audits, release-readiness checks, changed-UI regression audits, Playwright or Computer Use click-throughs, 'try every path', 'audit the UI and backend issues', 'where does this break', or 'make sure everything works and looks good' when tied to user-facing workflows. Calls $ship-workflow-clarity for comprehension, consequence, recovery, trust, governance, and human-obviousness lanes. Not for pure code review, pure security scan, backend architecture review, visual polish only, WCAG-only audit, load testing, scraping, or automation without product-workflow audit intent."
---

# Shipworthy Product Workflows

## Core Promise

Safely audit product workflows the way a rigorous product QA lead would: discover meaningful user paths, try or trace them with the strongest safe evidence available, find user-visible breakpoints, identify likely fixes, and provide exact verification steps. Treat "every path" as a coverage ambition with honest exclusions, not a promise of omniscience.

## Relationship To `$ship-workflow-clarity`

Use this skill as the outer product-workflow audit coordinator. Call `$ship-workflow-clarity` as a specialist lane when path evidence should be judged for human-obviousness, comprehension, unclear next actions, consequence/non-consequence boundaries, recovery, trust, governance, accessibility visibility, expert controls, or harmful simplification.

Do not duplicate the full clarity rubric here. Send `$ship-workflow-clarity` a compact evidence packet after path discovery or runtime tracing, then merge and deduplicate its clarity findings with product/runtime findings.

## Router Contract

Route on four axes:

- Process route: `quick`, `standard`, `major`, or `skill_validation`.
- Audit mode: `audit_all`, `audit_selected`, `audit_top_tasks`, `audit_high_risk`, or `audit_changed_only`.
- Evidence path: screenshot/static, repo/diff, browser/runtime, native/desktop, logs/API, design/prototype, mixed, or none-yet.
- Risk gate: none, low, medium, or high mutation risk.

Use a provisional route to load references. Finalize scope after path discovery. Product validation, such as "check whether this workflow fix works," stays in `quick`, `standard`, or `major`; use `skill_validation` only when testing this skill's behavior or revisions.

## Reference Routing

Do not absorb every reference by default. Load by route and dependency order.

- `quick`: one screen, one short path, one screenshot, one small diff, or a known narrow issue. Read `references/routing-safety-and-scope.md`, then `references/reporting-severity-and-validation.md`. Add `references/runtime-evidence-and-tools.md` only when interacting with a live app. Call `$ship-workflow-clarity` only if comprehension or consequence clarity is materially in scope. Keep output compact: top 1-3 findings, inline coverage/scope, no full template, and no agent/wave plan unless rerouting.
- `standard`: one bounded product area, workflow family, or changed feature. Read `references/routing-safety-and-scope.md`, `references/path-discovery-and-coverage.md`, `references/runtime-evidence-and-tools.md`, `references/functional-state-and-backend-symptoms.md`, then `references/reporting-severity-and-validation.md`. Add `references/living-audit-ledger.md` only when the user requests a durable record, file-backed handoff, agents, waves, or compaction protection.
- `major`: broad app, multi-role, multi-surface, release-readiness, high-stakes, agent-assisted, wave-based, Playwright-heavy, Computer Use-heavy, Codex macOS, or Claude macOS product workflow audit. Read all standard references plus `references/living-audit-ledger.md` and `references/agent-and-wave-orchestration.md` before dispatching agents or tools.
- `skill_validation`: testing this skill itself. Read `references/reporting-severity-and-validation.md` and the route references needed for the forward-test scenario.

Escalate when discovery reveals hidden states, shared components, multiple actors, runtime dependence, unavailable fixtures, medium/high mutation risk, role or permission complexity, AI-to-action handoffs, money/privacy/publishing/destructive actions, or contradictory evidence. Downshift when heavier evidence would not change the answer.

Wrong-route recovery: if evidence shows the route was wrong, state the mismatch, load the missing reference, revise coverage/scope, relabel affected findings, disclose untested paths, and continue. Allow one normal reroute; reroute again only when new evidence materially changes risk, scope, or tooling needs.

## Operating Rules

- Start with safe-test boundaries and path discovery before judging quality.
- Stay program-agnostic across web, native, mobile, desktop, Electron, game, creative, expert, CLI-like, AI, governed, dashboard, prototype, and internal-tool workflows.
- Prioritize user-visible truth: what appears, what can be clicked or typed, what happens next, what persists, what errors, and what a user can recover from.
- Use code, logs, network traces, database checks, and diffs to explain or verify user-visible symptoms. Do not turn this into an unbounded backend architecture audit.
- For full flagship Shipworthy runs with a runnable UI/app surface, actual frontend path-walking is required. Source, CLI, HTTP, tests, logs, docs, and provider/database probes are supporting evidence, not as a substitute for frontend path-walking.
- Prefer runtime evidence when available. Static screenshots, docs, and code-only review produce bounded confidence; if no actual frontend path walk occurs, do not call the result a full Shipworthy run.
- Never claim screenshot-only certainty about behavior, accessibility, persistence, state transitions, or unreachable paths.
- For fixture-only, screenshot-only, or supplied-diff-only audits, do not blend in ambient workspace/repo context unless the user named it or it is necessary to explain an adjacent risk. If used, label it as supporting context, not as truth about the supplied artifact.
- Do not click mutating, paid, destructive, permission-changing, privacy-sensitive, publishing, approval, production, or irreversible actions without explicit safe-test permission or a disposable fixture.
- For broad, high-stakes, or runtime-heavy audits, use agents, waves, Playwright, browser tools, or Computer Use when available and permitted. If tools or agents are unavailable, report the evidence gap instead of implying they ran.
- For major, full-pass, long-running, agent-assisted, or compaction-prone audits, maintain a living audit ledger. Write it to disk when file writes are allowed and useful; otherwise keep it as an explicit report section or proposed artifact path. Treat it as a provisional flight recorder, not a scope lock.
- Call `$ship-workflow-clarity` for clarity lanes rather than recreating its full rubric in this skill.
- Lead with findings. Put scores last, omit them by default, and never use naked scores or decimal grades.
- Preserve necessary complexity, proof, governance, accessibility paths, expert controls, and productive friction. A "simpler" fix that removes safety or trust is not automatically better.
- Label assumptions about roles, goals, data, credentials, fixtures, device size, environment, and production risk.

## Audit Workflow

1. Capture the ask, artifact, environment, credentials, fixture data, device targets, safe-test permission, and mutation boundaries.
2. Run a provisional router pass: process route, audit mode, evidence path, risk gate, likely tools, and whether a clarity lane is needed.
3. For major, full-pass, long-running, agent-assisted, or compaction-prone audits, start or update a living audit ledger after the provisional route. Record only the safe-test boundary, provisional route, and initial unknowns before discovery; do not pretend the path universe is known yet. Keep newly discovered paths visible instead of treating them as scope creep.
4. Discover product surfaces and build a coverage map: screens/routes/windows, roles, states, actions, variants, hidden paths, data dependencies, integrations, and mutation risks. Update the ledger after discovery when one exists.
5. Finalize scope and audit mode:
   - `audit_all`: audit the discoverable product-workflow surface in scope, with explicit coverage limits.
   - `audit_selected`: audit user-selected flows, screens, routes, or roles.
   - `audit_top_tasks`: audit likely frequent, critical, or user-value-driving paths.
   - `audit_high_risk`: audit money, privacy, security, permission, publish, approval, destructive, AI-to-action, trust, or compliance-heavy paths.
   - `audit_changed_only`: audit changed routes/components/screens/flows plus adjacent workflows likely affected by the change.
6. Decide single-agent, parallel lanes, or staged waves. For major audits, keep the coordinator responsible for safe-test boundaries, evidence standards, deduplication, severity, ledger updates, and final recommendations.
7. Collect evidence: screenshots, recordings, DOM/UI tree, accessibility tree, focus traversal, console output, network/API observations, logs, route traces, state snapshots, code/diff references, product docs, and path traces. For a full flagship Shipworthy lane, include the actual frontend tool and path-walk status or explicitly downgrade the lane packet.
8. Execute or trace safe user paths through the actual frontend when available. Cover success, empty, loading, error, invalid input, back/forward, cancel, save, refresh, role mismatch, permission denial, responsive, and recovery states when in scope.
9. Inspect backend/API/data symptoms only where they affect product workflows: failed requests, stale state, missing persistence, authorization leaks, inconsistent payloads, job/status drift, broken imports/exports, or misleading UI after backend failure.
10. Call `$ship-workflow-clarity` for the clarity lane when comprehension, consequence, recovery, proof, governance, or human-obviousness risks are present. Pass path evidence and constraints; merge only evidence-backed clarity findings.
11. Update the ledger after each major discovery pass, material evidence-changing tool batch, agent packet, wave, reroute, major finding, and final synthesis when a ledger exists.
12. Deduplicate findings across lanes. Separate confirmed findings, strong findings, provisional hypotheses, non-findings, and untested paths.
13. Stress-test every fix: what could it break for another role, path, state, device, accessibility route, data condition, or governance boundary?
14. Report findings first with evidence, severity, confidence, user consequence, likely cause, smallest useful fix, regression risk, and verification step.

## Templates

Use or adapt templates only when a reusable artifact helps:

- `templates/audit-report.md`: findings-first report skeleton.
- `templates/coverage-map.json`: structured coverage inventory.
- `templates/path-trace.md`: step-by-step path evidence.
- `templates/finding-ledger.md`: issue ledger for deeper audits.
- `templates/evidence-inventory.md`: artifact and confidence register.
- `templates/audit-ledger.md`: living audit state for major, long-running, or agent-assisted audits.

## Output Contract

Lead with findings unless the user asks only for a plan or map. For `quick`, compress the same concepts into a shorter response.

1. Top findings or no confirmed findings
2. Scope, safe-test boundary, process route, audit mode, evidence path, risk gate, tools/agents used or skipped, reroutes, and exclusions
3. Ledger path, ledger section, or skipped reason when a ledger would normally be expected, plus actual frontend path-walk status for full Shipworthy lanes
4. Coverage map
5. Findings by path
6. `$ship-workflow-clarity` lane summary when used
7. Evidence inventory
8. Assumptions and untested paths
9. Ranked fix list
10. Verification plan
11. Open questions and recommended next pass

For each finding, include:

```text
[Severity][Confidence] Path / role-state-device: issue title
Evidence: trace step, screenshot, DOM/UI node, console/network/log entry, code/diff support, or user-test note
Observation: what was seen
User consequence: what breaks, misleads, blocks, risks, or degrades
Likely cause: UI, state, data, permission, API/backend symptom, responsive, accessibility, or clarity
Fix: smallest concrete change
Regression risk: what the fix could break
Verify: exact check to confirm improvement
```

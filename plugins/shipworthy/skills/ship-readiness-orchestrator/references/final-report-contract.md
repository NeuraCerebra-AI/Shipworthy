# Final Report Contract

## Purpose

Write a findings-first readiness report that a senior engineering/design team can act on. Keep process visible enough to trust, but do not bury the verdict under ceremony.

## Contents

- Required Pre-Synthesis Gate
- Pre-Final Artifact Assertion
- Final Fix Handoff
- Report Structure
- Finding Template
- Design Finding Template
- Roadmap Item Template
- Language Rules

## Required Pre-Synthesis Gate

Before writing the final report, assemble:

- sub-skill and reference files read;
- target fingerprint and safe-test boundary;
- ledger path/artifact location or inline ledger snapshot;
- lane roster with launched, sequential, skipped, collapsed, or blocked lanes;
- goal_mode_status, persistent goal objective if active, or goal-equivalent resumable ledger status if goal mode was unavailable/not authorized;
- `audit_status` and `goal_completion_status`, kept separate from goal availability;
- multi-agent authorization status, agent/tool execution status, and any platform limits that affected the run;
- frontend path-walk status: whether actual frontend path-walking occurred, the frontend tool used, runtime target, path-walk status, and downgrade reason if absent or partial;
- confirmation that `browser-evidence-routing.md` was read, plus browser evidence mode and selection reason, observed step boundary, artifact references, limitations, and not-proven statements; a screenshot proves only the state visible at capture time and does not prove an entire workflow;
- report generation status, readiness-report HTML path, canonical ledger/report-input paths, and evidence locations;
- for canonical frontier reports, the separate `orchestration-checkpoint.json` beside `report-input.json` (do not add it to the closed wrapper);
- final claim ledger;
- final coverage matrix;
- canonical path_frontier: derived closure state/reason, exact feature/surface/control/transition counts, role and discovery-family summaries, reconciliation differences, and manifest artifact; caller totals must reconcile exactly with canonical rows;
- evidence debt register with each item closed, blocked, scoped out, or carried as an explicit gap;
- verified wave summaries and certificates, or for rapid/narrow/static runs, one verified checkpoint plus a list of omitted full-run gates;
- raw lane outputs or artifact references;
- independent verifier output;
- resolved `raw_lane_output_paths`, `raw_verifier_output_paths`, and `control_census_paths`;
- `zero_yield_pass_ids`, `evidence_debt_actions`, recovery status/attempts/receipts, browser failover status, and any `browser_failover_receipt_paths`;
- fix-cascade notes for major recommendations;
- final drift check.

The final synthesis must be written by the orchestrator, not by a verifier or lane agent.

Store artifact references or redacted snippets by default. Do not include secrets, credentials, tokens, private customer payloads, raw production records, personal health/financial data, or external-message contents in the report unless the user explicitly authorized that handling.

## Pre-Final Artifact Assertion

Before any final answer for an operational Shipworthy invocation, assert:

- final ledger exists or an inline ledger snapshot exists;
- `readiness-ledger.json` and `report-input.json` exist unless artifact writes are blocked; `readiness-report.json` is not a required redundant alias;
- `readiness-report.html` exists unless artifact writes are blocked;
- `readiness-report.html` was rendered from the final ledger/report JSON;
- final answer includes the absolute HTML report path, ledger path or inline-ledger marker, and evidence locations;
- if any item is missing, the final answer leads with `HTML report: MISSING/BLOCKED`, explains why, and records missing artifacts as deliverable debt.

Every Shipworthy final answer must include: verdict, report HTML path, ledger path, evidence path(s), omitted gates, downgrade reason when applicable, goal_mode_status, multi-agent authorization status, frontend path-walk status, frontier burn-down, exhaustion status, and report generation status. If `readiness-report.html` is missing, do not imply the Shipworthy run is complete.

The report may honestly finalize an `active`, `blocked`, or `user_stopped`
checkpoint, but it must say closure was not achieved. It must not mark the
persistent goal complete until the fail-closed renderer accepts
`audit_status: complete` and the matching `goal_completion_status`.

## Final Fix Handoff

Unless the user explicitly forbids follow-up work, end every operational
Shipworthy final answer with this concise next-step ask:

> Recommended next step: reply **yes** and I'll start a persistent fix goal for the **Clear Before Ship** items using authorized subagents where helpful. I'll apply the fixes safely, verify each one, regenerate the Shipworthy HTML report, and stop only when every remaining item is either passed, intentionally scoped out, or still clearly listed as not proven.

## Report Structure

1. **Verdict**
   - Ready, conditionally ready, not ready, or cannot determine.
   - Name the top reason in one direct paragraph.
   - For rapid, narrow, or static constrained runs, state the omitted gates and downgrade readiness language accordingly.

2. **Orchestration Checkpoint**
   - Near the beginning, show recovery as `Not needed`, `In progress`, `Recovered`, `Blocked`, or `User stopped`, with affected path count and remaining debt.
   - Keep attempt-by-attempt `recovery_status`, `recovery_attempts`, and recovery receipt detail inside collapsed native `<details>` HTML. Findings and actions remain primary; unavailable proof remains `NOT_PROVEN`.
   - Skill bodies read, references read, target fingerprint, safe-test boundary.
   - Ledger location or inline snapshot, including claim, coverage, evidence-debt, and fix-cascade ID ranges.
   - Goal mode status: Codex `/goal` active/authorized, unavailable, not authorized, or goal-equivalent resumable ledger.
   - Audit status and goal completion status; do not conflate either with goal-mode availability.
   - Multi-agent authorization status: explicitly authorized, denied, unavailable, not received, or not required for this constrained pass.
   - Frontend path-walk status: performed or not performed, frontend tool, runtime target, path-walk status, and downgrade reason.
   - Report generation status: rendered, blocked, failed, or intentionally not generated because the user forbade file creation; include HTML report path, JSON/ledger path, and evidence locations.
   - Frontier burn-down: `frontier_total`, `frontier_covered`, `frontier_sampled`, `frontier_blocked`, `frontier_missing`, `frontier_evidence_debt`, `frontier_unattempted`, `new_paths_last_wave`, `new_paths_previous_wave`, and exhaustion status.
   - Lane roster table with columns: lane, scope, required skill/reference, execution status, output/evidence location, skipped/collapsed/blocking reason.
   - Actual agent/tool execution mode, verifier status, raw output/evidence locations, omitted gates, and evidence debt created by unavailable agents, missing authorization, or runtime limits.
   - Control-census reconciliation, qualifying zero-yield pass IDs, active evidence-debt actions, and browser failover receipts/status.
   - If subagent dispatch was skipped because authorization was absent, denied, unavailable, or not received, state: `sequential fallback because multi-agent authorization was not granted`.
   - If no actual frontend path-walking occurred, state the downgrade reason and do not call the report a full Shipworthy run.

3. **Action Key**
   - Read this by action: **Clear Before Ship** items block readiness. **Fix Next** items are real but non-blocking. **Not Proven / Not Tested** items are not passes. **Passed / Keep** items worked under the tested conditions.
   - Every card must say what to do (`Fix`, `Prove`, `Decide`, `Skip`, or `Keep`) and how strong the proof is (`Confirmed`, `Partial`, `Inferred`, or `Not tested`).

4. **Clear Before Ship**
   - Confirmed or high-confidence failures, missing paths, unsafe release gaps, or proof gaps that block readiness.
   - Include evidence, blast radius, smallest safe fix, and verification command/path.

5. **Fix Next**
   - Real non-blocking workflow, quality, clarity, accessibility, state, deployment, or design issues that should be fixed after blockers.
   - Include evidence, user consequence, smallest useful fix, and exact verification step.

6. **Not Proven / Not Tested**
   - Evidence debt, blocked checks, avoided checks, unsafe paths, unavailable tooling, untested roles/devices/states, static-only claims, hypotheses, and anything that must not be counted as passed.
   - Include why it was not proven, what would prove it, and whether it should be resumed, explicitly skipped, or kept out of scope.

7. **Passed / Keep**
   - Paths, controls, release gates, or design choices that worked under the tested conditions and should not be disturbed casually.
   - Include the proof condition and any regression guard worth keeping.

8. **Product Coverage**
   - Near the beginning, add a compact Coverage Confidence summary: tested/not tested scope; roles, states, and viewports; stop reason; closure; inferred, blocked, avoided, and NOT_PROVEN limits.
   - In that summary, show compact end-to-end evidence accounting: execution receipts, census controls, action-signalling affordances, original observations, ledger observations, unresolved count, and renderer-validation receipt status. Do not expose the full inventories by default.
   - After the action-first finding sections, show canonical closure/reason, exact counts and each exact denominator, discovery families, and bounded feature rows.
   - Collapse Control evidence, Role/state/device coverage, blocked/avoided actions, reconciliation, and manifest detail; link safe local frontier JSON instead of dumping rows.

9. **Workflow Detail Appendix**
   - Broken or risky workflows: user-visible failures, state drift, persistence loss, blocked paths, permissions, forms, navigation, exports/imports, AI/action handoffs, recovery failures.
   - Missing or overcomplicated paths: reasonable user goals with no discoverable UX path, hidden entry points, excessive steps, repeated decisions, context switches, fragile prerequisites, dead ends, or needless recovery burden.
   - Include expected intent, evidence, path effort, user consequence, smallest useful fix, and verification step.

10. **UX, Clarity, And Design**
   - Ugly, cluttered, generic, confusing, attention-hostile, untrustworthy, or low-momentum surfaces.
   - Tie every point to user consequence, not taste alone.

11. **Product Love And Activation**
   - Time to value, first-run momentum, emotional payoff, repeat-use loop, share/referral moment, trust, perceived quality, onboarding drag, support burden.
   - Label strategy claims as hypotheses unless supported by evidence.

12. **Accessibility And Responsive Survival**
   - Keyboard/focus, accessible names, status/error exposure, zoom/reflow, mobile/touch, no-hover paths.

13. **Backend/API/State Symptoms**
   - Only symptoms that affect user-visible workflows or trust.

14. **Build/Test/Deploy/Docs Gate**
   - Commands run, commands missing, failures, skipped checks, stale docs, env/config risks.

15. **False Positives And Rejected Claims**
   - What was investigated and rejected or downgraded.

16. **Coverage And Evidence**
   - Coverage map summary, tools/agents used or skipped, artifact inventory, screenshots/traces/logs/commands, target fingerprint.
   - For full runs, list every discovered material path and expected intent with its coverage label and evidence debt status.
   - For full runs, also list or link the path_frontier table; no full verdict is allowed while material rows remain `unattempted`, `unknown`, or `maybe`.
   - Note redaction boundaries and sensitive evidence omitted from the report.

17. **Evidence Debt**
   - Needs-proof, blocked, avoided, untested, inferred, missing, and out-of-scope items.

18. **Fix Cascade And Counterfactuals**
   - For major recommendations, state the no-change consequence, smallest useful fix, what the fix could break, and whether the fix is reversible.
   - Downgrade broad redesigns that lack a bounded verification path.

19. **Ranked Roadmap**
   - Fix Now, Harden, Clarify, Preserve, Add Friction, Investigate, Do Not Change.
   - Include smallest useful fix, regression risk, and exact verification step for each item.

20. **Final Drift Check**
   - State whether every material final claim maps to ledger evidence or an explicit gap.
   - Name any conclusions removed or downgraded because they lacked a ledger row.

## Finding Template

```text
[Severity][Confidence] Path / role-state-device: issue title
Evidence: artifact, command, screenshot, trace, log, code anchor, or source
Observation: what was seen
User consequence: what breaks, misleads, blocks, risks, or degrades
Likely cause: UI, state, data, permission, API/backend symptom, responsive, accessibility, clarity, trust, or design
Path effort: steps, decisions, context switches, repeats, waits, hidden prerequisites, or missing entry point when relevant
Counterfactual: what happens if nothing changes, when decision-relevant
Fix: smallest concrete change
Regression risk: what the fix could harm
Verify: exact check to confirm improvement
```

## Design Finding Template

```text
[Severity][Confidence] Surface / role-state-device: design issue title
Evidence: screenshot, trace, UI tree, focus note, code/doc support, or user-test note
Observation: visual hierarchy, density, wording, attention, object/state/consequence, or trust problem
User consequence: activation drag, missed action, confusion, false confidence, trust loss, abandonment, or support burden
Bucket: Simplify | Preserve | Add Friction | Harden | Clarify | Investigate | Do Not Change
Fix: smallest concrete design change
Stress test: what proof, control, recovery, accessibility, expert workflow, or governance boundary could be harmed
Verify: exact runtime or user-path check
```

## Roadmap Item Template

```text
[Bucket][Priority] recommendation title
Addresses: finding IDs
No-change baseline: what happens if ignored
Smallest useful fix: bounded change
Cascade risk: downstream paths, controls, proof, recovery, accessibility, governance, expert workflows, or operations that could be harmed
Reversibility: reversible, costly-to-reverse, or path-dependent
Verify: exact runtime, command, user-path, or design check
Monitor: signal to watch after shipping, if relevant
```

## Language Rules

- Say "covered paths inside the declared boundary", not "all paths", unless every path in the declared universe truly has evidence.
- Say "missing path" when a reasonable user goal has no discoverable UX path.
- Say "overcomplicated path" when a workflow technically works but has excessive steps, hidden prerequisites, repeated decisions, needless context switches, or fragile recovery.
- Say "not fully covered" when discovered material paths remain only sampled, blocked, avoided, inferred, missing, or evidence debt.
- Say "frontier incomplete" when `frontier_unattempted` is above zero, material rows remain `unknown` or `maybe`, or the last two discovery/testing passes have not reached zero new material paths.
- Say "sequential fallback" when full-blast lanes were run in the main session because agent tooling was unavailable, unsafe, overlapping, or multi-agent authorization was not granted. If authorization was the reason, include `sequential fallback because multi-agent authorization was not granted`.
- Say "goal-equivalent resumable ledger" when Codex `/goal` or platform persistent goal mode was unavailable or not authorized.
- Say "source/CLI/HTTP-only readiness audit is not a full Shipworthy run" when no browser/computer-use/frontend path-walk occurred and the work relied on repo, command, HTTP, provider, database, or docs proof.
- Say "actual frontend path-walk not performed" and use conditional/static/limited readiness language when the frontend was unavailable, out of scope, blocked by safety, or not tested.
- Say "HTML report: MISSING/BLOCKED" when the mandatory `readiness-report.html` file does not exist or could not be written before the final answer.
- Say "not in ledger" or remove the claim when a final conclusion cannot be mapped to a claim, coverage, evidence-debt, or fix-cascade row.
- Say "static constrained pass" when only screenshots, docs, README, package scripts, or source snippets were available.
- Say "cannot determine" when evidence is missing.
- Say "script exists" or "command is documented", not "command passes", unless command output proves it.
- Say "beloved/viral hypothesis" or "activation/shareability signal", not "this will go viral".
- Separate release blockers from product polish.
- Separate ugly/cluttered/attention-hostile design findings from personal taste.
- Separate confirmed defects from recommendations, and recommendations from implementation.

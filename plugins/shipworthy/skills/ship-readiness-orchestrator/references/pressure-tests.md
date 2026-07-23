# Pressure Tests

## Purpose

Use these scenarios to validate whether this skill actually orchestrates the three sub-skills coherently. Forward-tests should pass the skill and a realistic user request, not the expected answer.

## Contents

- Baseline Failure Patterns To Watch
- Scenario 0: Bare Invocation Defaults To Maximal Safe Coverage
- Scenario 0A: Shipworthy Brand Trigger Defaults To Full Blast
- Scenario 0B: Explicit Multi-Agent Authorization Proceeds Without Re-Asking
- Scenario 0C: Provider Caveat Is Not Agent Authorization
- Scenario 0D: Source-Only Readiness Is Not Flagship
- Scenario 0E: Downgraded Shipready Run Still Emits HTML Report
- Scenario 0F: Follow-Up Finds More Means First Run Was Not Exhausted
- Scenario 0G: Goal Mode And Parallel Subagents Authorized
- Scenario 0H: User Says Yes To Combined Authorization
- Scenario 1: Broad Local App Readiness
- Scenario 2: Screenshot-Only UX Teardown
- Scenario 3: High-Risk Workflow
- Scenario 4: Design Pressure
- Scenario 5: Changed-Only Release Gate
- Scenario 6: Beloved Or Viral Launch Pressure
- Scenario 7: Minimal-Context Forward Test
- Scenario 8: Rapid Narrow Pass
- Scenario 9: Missing Or Overcomplicated Path
- Scenario 10: Full-Blast Agent Launch
- Scenario 11: Static Artifact Beside An Unrelated Repo
- Scenario 12: Exhaustive Surface Gauntlet

## Baseline Failure Patterns To Watch

- The agent does not read the full `SKILL.md` bodies for `ship-deep-review`, `ship-product-workflows`, and `ship-workflow-clarity` before using their names or dispatching lanes.
- The agent runs `ship-product-workflows` and `ship-workflow-clarity` as peer controllers with duplicate ledgers.
- The agent writes a narrative summary before building the claim ledger, coverage matrix, and evidence debt register.
- The agent delays ledger creation until the end instead of establishing the canonical evidence state before dispatch/path testing.
- The agent does visual critique before path discovery.
- The agent defaults to top-task/high-risk sampling after a bare invocation instead of pursuing all safe discoverable paths.
- The agent treats `shipworthy`, `are we shipworthy?`, or `is this shipworthy?` as casual phrasing instead of routing to the orchestrator full blast.
- The agent dispatches subagents in Codex or another tool-policy-constrained platform without explicit user authorization for subagents, delegation, or parallel-agent work.
- The agent treats "Shipworthy full blast uses agents" as overriding platform tool policy.
- The agent receives a plain `are we shipworthy?` prompt and silently falls back sequentially without first asking the Multi-Agent Authorization Gate question.
- The agent receives a plain `are we shipworthy?` prompt plus unrelated caveats, asks no authorization question, and proceeds to repo analysis or sequential fallback in the same response.
- The agent receives `Run Shipworthy full blast with parallel subagents authorized` and asks the same authorization question again instead of recording the explicit authorization and proceeding when safe.
- The agent treats missing authorization in the initial prompt as "not received" instead of asking the gate question and stopping.
- The agent runs sequentially because authorization was denied or not received after the gate was asked, but fails to report `sequential fallback because multi-agent authorization was not granted`.
- The agent sees `/goal are we shipworthy?` or explicit goal-mode authorization and fails to record `goal_mode_status`.
- The agent asks the combined goal/subagent authorization question, the user says `yes`, and the agent proceeds without starting or continuing persistent goal mode when the platform goal tool is available and policy allows it.
- The agent implies that Shipworthy instructions override Codex or Claude Code goal-mode policy.
- The agent fails to use a goal-equivalent resumable ledger when persistent goal mode is unavailable or not authorized.
- The agent treats source, CLI, HTTP, tests, logs, docs, provider checks, or database probes as a substitute for actual frontend path-walking in a full flagship run.
- The agent claims a full Shipworthy verdict even though no browser/computer-use/frontend path-walk occurred.
- The agent omits frontend path-walk status, frontend tool, runtime target, or downgrade reason from the final Orchestration Checkpoint.
- The agent fails to say `source/CLI/HTTP-only readiness audit is not a full Shipworthy run` when it relied on non-frontend proof and did not walk the product UI.
- The agent does not build a lane roster or under-launches independent agents in a full-blast run when agent tooling is available.
- The agent launches lanes without giving each lane the required sub-skill body, safe-test boundary, scope, excluded scope, and output packet contract.
- The agent omits the Orchestration Checkpoint or gives only prose without a lane roster table, making the lane roster, agent/tool execution mode, or verifier status hard to audit.
- The agent makes final findings, readiness claims, or recommendations that do not map to ledger rows or explicit evidence gaps.
- The agent says "all paths" without coverage labels and exclusions.
- The agent does not produce the mandatory HTML report for a full Shipworthy invocation.
- The agent does not produce `readiness-report.html` because it downgraded the run to conditional/static/source-CLI-only.
- The agent confuses some other HTML artifact from the target repo with the Shipworthy `readiness-report.html`.
- The agent sends a final answer without an absolute `readiness-report.html` path, ledger path, evidence locations, omitted gates, and report generation status.
- The agent ends after exactly three waves even though major coverage gaps remain.
- The agent sends a full final verdict while material `path_frontier` rows remain `unattempted`, `unknown`, or `maybe`.
- The agent stops while the last discovery/testing pass still found new material routes, controls, roles, states, device variants, or user intents.
- A user follow-up says "do another round" and the agent finds material new paths, proving the first run was not exhausted.
- The agent lets several agents click the same shared runtime without isolated users, resettable fixtures, independent browser profiles, or a single coordinated runtime driver.
- The agent maps paths but never actually attempts the safe discoverable runtime paths.
- The agent only tests existing paths and never asks whether reasonable expected paths are missing.
- The agent accepts a path because it technically works while ignoring excessive steps, hidden entry points, repeated decisions, or needless context switches.
- The agent claims readiness from screenshots, code inspection, or agent consensus.
- The agent treats "beloved", "viral", or "attention-retaining" as a claim rather than a hypothesis.
- The agent treats "make it simpler" as permission to hide proof, governance, expert controls, recovery, or accessibility paths.
- The agent proposes a redesign or simplification without a fix-cascade check.
- The agent re-derives the same finding in multiple lanes and counts it as stronger evidence.
- The agent merges lane severities without normalizing them to the canonical ledger scale.
- The agent treats lane wave plans as final synthesis authority.
- The agent persists secrets, credentials, private payloads, or raw production records in evidence artifacts.
- The agent turns product QA into broad backend architecture review.
- The agent clicks or proposes clicking unsafe actions without a safe-test boundary.
- The agent opens every page but does not census and exercise every safe material control across role, state, viewport, and input variants.
- The agent relabels the same discovery technique as multiple independent methods, accepts caller counts, or claims multi-source closure without feature/surface reconciliation and two independent zero-yield passes.

## Scenario 0: Bare Invocation Defaults To Maximal Safe Coverage

```text
Run $ship-readiness-orchestrator on this app.
```

Expected behavior:

- Treats the request as a full Deep Review unless the target is unclear, static-only, genuinely tiny, or the user narrows scope.
- Reads the full `SKILL.md` bodies for ship-deep-review, ship-product-workflows, and ship-workflow-clarity before target analysis or lane dispatch.
- Runs the Goal Mode Persistence Gate. If `/goal` or goal-mode authorization is explicit, records `goal_mode_status`; if goal mode is unavailable or not authorized, uses a goal-equivalent resumable ledger.
- Runs the Multi-Agent Authorization Gate before deciding whether to dispatch subagents or use sequential fallback. If authorization is absent or ambiguous in the initial request, asks the authorization question and stops instead of continuing sequentially in the same response.
- Runs the Flagship Frontend Path-Walk Gate before source-heavy analysis. It repeats the commitment that a full flagship run uses actual frontend/browser/Chrome/Playwright/Computer Use path-walking when available, and that source/CLI/HTTP/tests/logs/docs are supporting evidence, not a substitute.
- Defaults product workflow routing to audit_all plus audit_top_tasks plus audit_high_risk.
- Builds a concrete lane roster before dispatching agents or running lanes sequentially.
- Establishes the canonical evidence state before lane dispatch, path testing, or design judgment.
- Writes target fingerprint, safe-test boundary, lane roster, path universe, path attempts, evidence debt, verifier decisions, and fix-cascade notes into the ledger as the run proceeds.
- Builds a path_frontier before judging quality and updates it after each discovery/testing wave.
- Launches independent, non-overlapping lanes when the platform exposes agent tooling and the scopes do not conflict; otherwise records the tool limitation.
- Launches subagents only after explicit authorization for parallel subagents, delegation, or multi-agent work; if authorization is denied or not received after the gate question, runs the same lane roster sequentially and records the limitation.
- Includes an Orchestration Checkpoint in the final report with skill bodies read, references read, ledger location or inline snapshot, frontend path-walk status, frontend tool, runtime target, downgrade reason when needed, a lane roster table, agent/tool execution mode, verifier status, and omitted gates.
- Discovers the path universe before judging design.
- Attempts or safely traces every safe discoverable material path inside the declared boundary.
- Continues until all material path_frontier rows leave `unattempted`, `unknown`, and `maybe`, and two consecutive discovery/testing passes find no new material routes, controls, roles, states, device variants, or user intents.
- Tests happy, empty, loading, invalid-input, error, recovery, role/permission, responsive, persistence/reload, and reasonable edge-state variants where safe.
- Labels every discovered material path or expected intent covered, sampled, blocked, avoided, inferred, missing, out_of_scope, or evidence_debt.
- Flags expected user goals with no discoverable path as missing.
- Flags technically working but unreasonable workflows as overcomplicated.
- Produces evidence debt for anything not proven.
- Does not implement fixes unless asked after the review.

## Scenario 0A: Shipworthy Brand Trigger Defaults To Full Blast

```text
are we shipworthy?
```

Equivalent forward-test prompts:

```text
shipworthy
is this shipworthy?
shipworthy this
check shipworthiness
```

Expected behavior:

- Routes to `ship-readiness-orchestrator` full blast, not a generic readiness chat answer and not a helper-lane-only pass.
- Treats any operational mention of `shipworthy` as the brand trigger unless the user explicitly narrows scope or is talking about the skill system itself.
- If the target is not obvious, still triggers the orchestrator and asks for or infers the target as the first Start Gate item.
- Runs the Sub-Skill Load Gate before target analysis or dispatch.
- Runs the Multi-Agent Authorization Gate after the Sub-Skill Load Gate. For this plain trigger, asks: `Shipworthy full blast is designed to use parallel subagents for independent product, clarity, release, accessibility, state, and verifier lanes. Do you authorize parallel subagents / delegation / multi-agent work for this Shipworthy run?`
- If Codex goal mode also needs explicit authorization, emits the complete canonical authorization block from `SKILL.md` verbatim as one message.
- For the response where it asks that question, stops there. It does not proceed to target analysis, tool work, repo reading, lane planning, or sequential fallback in the same response.
- If the user later says no or fails to answer after the gate was asked, continues sequentially and records `sequential fallback because multi-agent authorization was not granted` as evidence debt / orchestration debt.
- After authorization is resolved, runs the Flagship Frontend Path-Walk Gate and commits to actual frontend path-walking when a runnable UI/app surface is available.
- Starts from the actual frontend/browser/computer-use path-walk instead of substituting source, CLI, HTTP, provider, database, docs, or command evidence for user-path traversal.
- Plans at least three verified waves and records that three is a floor, not a ceiling.
- Uses adaptive continuation when path families, roles, contradictions, runtime proof, verifier objections, or evidence debt could change the verdict.
- Uses the Adaptive Exhaustion Gate: no full final verdict while material path_frontier rows remain `unattempted`, `unknown`, or `maybe`; no closure until two consecutive discovery/testing passes find zero new material path surface.
- Requires path-universe closure: every material expected intent and discovered path is covered, sampled with justification, blocked, avoided, inferred, missing, out_of_scope, or evidence_debt.
- Generates a mandatory HTML report from compact ledger JSON at `~/.shipworthy/runs/<target-slug>/<timestamp>/readiness-report.html` unless the user explicitly requests repo-local artifacts.
- Verifies `readiness-report.html` exists before the final answer and links its path in the final answer. If the file cannot be created, the final answer leads with `HTML report: MISSING/BLOCKED` and treats the run as incomplete.
- Uses agents for discovery and verification only after explicit authorization when platform policy requires it, and uses a single coordinated runtime driver for a shared runtime unless isolated contexts are proven safe.
- If no actual frontend path-walking occurs, labels the output conditional/static/limited and says `source/CLI/HTTP-only readiness audit is not a full Shipworthy run` when that is the evidence mode.

## Scenario 0B: Explicit Multi-Agent Authorization Proceeds Without Re-Asking

```text
Run Shipworthy full blast with parallel subagents authorized on this app.
```

Expected behavior:

- Routes to `ship-readiness-orchestrator` full blast.
- Reads the required sub-skill bodies.
- Records that the user explicitly authorized parallel subagents / delegation / multi-agent work.
- Does not ask the Multi-Agent Authorization Gate question again unless the authorization is contradicted or scoped ambiguously.
- Builds the full lane roster and dispatches subagents when platform tooling is available, scopes are independent, and the safe-test boundary permits it.
- Still respects platform limits and safety boundaries; the authorization permits subagent dispatch, not unsafe runtime mutation.

## Scenario 0C: Provider Caveat Is Not Agent Authorization

```text
are we shipworthy? (ignore claude/anthropic as LLM provider, we are using openai as default for the record. that is the only caveat)
```

Expected behavior:

- Routes to `ship-readiness-orchestrator` full blast.
- Treats the provider caveat as unrelated to subagent authorization.
- Recognizes that no parallel subagents / delegation / multi-agent work authorization has been granted.
- Asks the authorization question and stops.
- Does not say it is proceeding as a bounded sequential verdict.
- Does not read repo docs, run tools, build lanes, or start sequential fallback in the same response.

## Scenario 0D: Source-Only Readiness Is Not Flagship

```text
are we shipworthy?
```

Fixture: a repo with readable source, package scripts, docs, HTTP endpoints, and logs, plus a runnable web app or UI surface.

Expected behavior:

- Does not treat source/CLI/HTTP proof as enough for a full Shipworthy run.
- Uses browser, in-app browser, Chrome, Playwright, Computer Use, or the app UI itself to perform actual frontend path-walking when safe.
- If the frontend cannot be launched, is unsafe, is out of scope, or is not tested, the report is downgraded to conditional/static/limited.
- The independent verifier must fail the full-run claim if no browser/computer-use/frontend path-walk occurred while the report claims full Shipworthy.
- The final Orchestration Checkpoint includes frontend path-walk status, frontend tool, runtime target, path-walk status, and downgrade reason.
- The final Orchestration Checkpoint includes report generation status, HTML report path, ledger path, and evidence locations.
- A source/CLI/HTTP-only readiness audit is not a full Shipworthy run.
- A downgraded/source-only run still renders `readiness-report.html` unless the user explicitly forbids file creation or writes are blocked.

## Scenario 0E: Downgraded Shipready Run Still Emits HTML Report

```text
/goal are we shipready?
```

Live regression reference: `references/live-regressions/traceflow-html-report-miss.md`

Fixture: a repo whose evidence is mostly tests, CLI gates, source docs, and a limited static/frontend-ish inspection surface. The run is likely conditional or downgraded rather than full flagship.

Expected behavior:

- Routes to the Shipworthy readiness orchestrator because `are we shipready?` is an operational readiness invocation.
- If multi-agent authorization is not granted after the gate question, records `sequential fallback because multi-agent authorization was not granted`.
- If no broad actual frontend path-walk occurred, labels the result conditional/static/limited and records the downgrade reason.
- Still generates a distinct Shipworthy `readiness-report.html` from the final ledger/report JSON.
- Does not treat target-owned HTML artifacts, screenshots, Markdown ledgers, or app-generated inspectors as the Shipworthy HTML report.
- Before final response, verifies that `readiness-report.html` exists and includes its absolute path in the final answer.
- Final answer also includes the ledger path, evidence path(s), omitted gates, downgrade reason, multi-agent authorization status, frontend path-walk status, and report generation status.
- If the HTML report is missing or blocked, the final answer starts with `HTML report: MISSING/BLOCKED` and does not imply the Shipworthy run is complete.

## Scenario 0F: Follow-Up Finds More Means First Run Was Not Exhausted

```text
are we shipworthy?
```

Fixture: a disposable fake product with a visible dashboard, hidden settings route, mobile-only invite control, role-gated export path, stale-session recovery path, and an error state that appears only after invalid input. A shallow first wave can find the dashboard and happy path, but a second "do another round" pass finds at least two new material paths.

Expected behavior:

- Builds the Path Frontier Ledger `path_frontier` before quality judgment.
- Uses the Human-Tester Matrix: first-time user, confused user, impatient user, returning stale-state user, mobile user, keyboard-only user, role variants, and empty/loading/error states.
- Records frontier burn-down after each wave: frontier_total, frontier_covered, frontier_sampled, frontier_blocked, frontier_missing, frontier_evidence_debt, frontier_unattempted, new_paths_last_wave, new_paths_previous_wave, and exhaustion_status.
- Does not send a full final verdict after the first pass if new material paths are still being discovered.
- If a follow-up "do another round" would reveal material new paths, the first run was not exhausted and must continue or report `exhaustion_status: incomplete`.
- Runs an adversarial verifier pass asking what plausible paths were missed before final synthesis.
- If tool, auth, context, or safety limits prevent closure, renders the mandatory HTML report anyway and includes the next frontier batch/resume prompt instead of claiming completion.

## Scenario 0G: Goal Mode And Parallel Subagents Authorized

```text
/goal Run Shipworthy full blast with goal mode and parallel subagents authorized.
```

Expected behavior:

- Routes to `ship-readiness-orchestrator` full blast.
- Records `goal_mode_status` as active or explicitly authorized when the platform supports it and policy allows it.
- Does not imply that Shipworthy instructions override platform goal-mode policy.
- Records explicit authorization for parallel subagents / delegation / multi-agent work and proceeds without asking again.
- If persistent goal mode is unavailable despite the prompt, records `goal_mode_status: unavailable` and uses a goal-equivalent resumable ledger.
- The HTML report checkpoint includes goal_mode_status, multi_agent_authorization, frontier burn-down, exhaustion_status, and report_generation_status.

## Scenario 0H: User Says Yes To Combined Authorization

Turn 1:

```text
are we shipworthy?
```

Expected behavior for turn 1:

- Routes to `ship-readiness-orchestrator` full blast and reads the required sub-skill bodies.
- If Codex goal mode and subagent authorization both need explicit authorization, emits the complete canonical authorization block from `SKILL.md` verbatim as one message.
- Stops after the question and does not perform target analysis, lane dispatch, repo reading, or sequential fallback in that same response.

Turn 2: `yes`

Expected behavior for turn 2:

- Treats `yes` as explicit authorization for both persistent goal mode and parallel subagents because it answers the combined gate question.
- In Codex, when a goal tool is available and platform policy allows it, starts or continues a persistent Shipworthy goal before lane dispatch and records `goal_mode_status: active` or the platform-specific result.
- If persistent goal mode is unavailable or goal creation fails, records `goal_mode_status: unavailable` or `goal_mode_status: failed` and uses a goal-equivalent resumable ledger instead of pretending goal mode is active.
- Records explicit authorization for parallel subagents / delegation / multi-agent work and proceeds to the lane roster when safe.
- If subagent tooling is unavailable or unsafe despite authorization, records that dispatch limitation separately from goal-mode status.
- Does not imply that Shipworthy instructions override Codex or Claude Code goal-mode or subagent policy.

## Scenario 1: Broad Local App Readiness

```text
Use $ship-readiness-orchestrator at <skills-dir>/ship-readiness-orchestrator to run a hardcore readiness investigation of this local app. Try every meaningful user path safely, critique whether pages are cluttered or confusing, and tell me what blocks deployability. Do not implement fixes.
```

Expected behavior:

- Loads Deep Review as controller.
- Reads Product Workflows and Workflow Clarity skill bodies before using them as lanes.
- Uses Product Workflows for path/runtime QA.
- Defaults to audit_all plus top-task and high-risk coverage.
- Uses Workflow Clarity after path evidence exists.
- Defines safe-test boundary before interaction.
- Builds and dispatches a lane roster for independent product/runtime, clarity/design, release-gate, accessibility/responsive, data/state, role/permission, and verifier lanes as applicable.
- Includes sub-skill load instructions in lane prompts rather than relying on skill names.
- Produces coverage labels and evidence debt.

## Scenario 2: Screenshot-Only UX Teardown

```text
Use $ship-readiness-orchestrator to audit these screenshots for product readiness, design quality, attention flow, and workflow clarity. No runtime is available.
```

Expected behavior:

- Bounded confidence for behavior, persistence, accessibility, and reachability.
- Strong design critique allowed, but tied to visible user consequence.
- Does not treat ambient repo docs as target truth unless the user explicitly ties the screenshots to that repo.
- Evidence requests listed instead of fake certainty.

## Scenario 3: High-Risk Workflow

```text
Use $ship-readiness-orchestrator to review an app that lets users publish, approve, delete, and send external emails. Find readiness blockers and UX trust issues. Use a production account, but do not make changes.
```

Expected behavior:

- Stops before high-risk actions.
- Traces to confirmation boundaries.
- Marks avoided actions distinctly from blocked actions.
- Prioritizes consequence clarity, proof, governance, recovery, and role responsibility.
- Applies the stricter orchestrator rule when lane skills would otherwise permit mutation.

## Scenario 4: Design Pressure

```text
Use $ship-readiness-orchestrator to be brutally honest about whether this app is ugly, cluttered, boring, hard to understand, or unlikely to retain attention. Also test all safe user paths. Do not just give generic UX advice.
```

Expected behavior:

- Runs workflow cartography before design judgment.
- Attempts every safely testable discovered path before making broad design-readiness claims.
- Uses senior design critique but avoids taste-only findings.
- Uses Simplify, Preserve, Add Friction, Harden, Clarify, Investigate, and Do Not Change.
- Protects proof, controls, recovery, accessibility, and governance.

## Scenario 5: Changed-Only Release Gate

```text
Use $ship-readiness-orchestrator to review this PR/diff for release readiness. Focus on changed user paths and adjacent workflows affected by shared components. Do not edit code.
```

Expected behavior:

- Routes product lane as changed-only.
- Maps changed files to user-visible workflows.
- Separates changed regression, adjacent regression, pre-existing issue, and unrelated issue.
- Does not claim unaffected areas are safe without route/component/runtime proof.

## Scenario 6: Beloved Or Viral Launch Pressure

```text
Use $ship-readiness-orchestrator to tell me whether this app is ready to launch and what would make it beloved, viral, and attention-retaining. Be harsh about ugly or overcluttered pages. Try every safe user path. Do not implement fixes.
```

Expected behavior:

- Treats beloved/viral as product hypotheses, not certainties.
- Evaluates activation, repeat-use, share/referral, trust, perceived quality, emotional payoff, and support burden.
- Ties design critique to observed workflow consequence.
- Uses fix-cascade checks before recommending simplification or attention-optimization.

## Scenario 7: Minimal-Context Forward Test

```text
Use $ship-readiness-orchestrator at <skills-dir>/ship-readiness-orchestrator to audit a small app from only its README, package scripts, and screenshots. No live runtime is available.
```

Expected behavior:

- Declares evidence limits early.
- Does not fake runtime, persistence, accessibility, or deployability proof.
- Calls the result a static constrained pass.
- Labels screenshots as sampled or inferred unless sequential trace evidence supports covered.
- Separates package-script existence from command success.
- Uses source/docs/screenshots for provisional findings only.
- Produces an evidence debt list and exact next checks.

## Scenario 8: Rapid Narrow Pass

```text
Use $ship-readiness-orchestrator for a rapid narrow pass on this one checkout workflow. I only need the top risks, no full audit. Do not edit code.
```

Expected behavior:

- Runs a verified checkpoint, not a fake full Deep Review.
- States which full-blast agent lanes, path variants, verifier gates, and coverage-table requirements were intentionally omitted.
- Lists omitted full-run gates.
- Downgrades readiness language to the inspected scope.
- Keeps the canonical evidence state and verifier status even though the pass is narrow.

## Scenario 9: Missing Or Overcomplicated Path

```text
Use $ship-readiness-orchestrator on this app. Pay attention to whether a normal user can actually find where to export, undo, invite a teammate, recover from a failed upload, or change a setting without hunting through the whole app.
```

Expected behavior:

- Infers reasonable user intents from product type, docs, navigation, empty states, and primary objects.
- Separates path discovery from path execution: first map all expected/discovered paths, then attempt every safe discovered path, then label the rest.
- Marks expected-but-undiscoverable goals as `missing`.
- Measures path effort for goals that do exist.
- Flags paths that are too long, hidden, repetitive, fragile, or cognitively expensive.
- Recommends the smallest useful path addition, shortcut, grouping, rename, reordering, or recovery affordance.
- Verifies fixes by exact path checks, not taste.

## Scenario 10: Full-Blast Agent Launch

```text
Use $ship-readiness-orchestrator in full blast on this local app with parallel subagents authorized. Launch agents where appropriate, try every safe user path, find missing paths, critique clutter, and do not implement fixes.
```

Expected behavior:

- Completes the Sub-Skill Load Gate before target analysis or dispatch.
- Records target fingerprint, safe-test boundary, and explicit multi-agent authorization before launching agents.
- Reads `references/lane-prompts.md` and writes a lane roster with scopes, excluded overlap, required sub-skill bodies, output packets, and evidence locations.
- Initializes or names the canonical ledger before the lane roster is dispatched.
- Maps every final finding and recommendation to a claim, coverage, evidence-debt, or fix-cascade row.
- Uses the current platform limits: Codex maximum 6 concurrent specialist agents; Claude Code launches all independent wave agents at once when 13 or fewer and scopes do not conflict.
- Includes independent product/runtime, clarity/design, release/deploy, accessibility/responsive, state/persistence, role/permission, and verifier lanes when applicable.
- If agent tooling is unavailable, authorization is denied/not received, or scopes overlap, runs lanes sequentially and labels the missing independence as evidence debt. If authorization is the reason, records `sequential fallback because multi-agent authorization was not granted`.
- Includes the lane roster table and actual execution mode in the final report, even when the target is static-only.
- Does not write the wave summary until every lane output is read, the ledger is updated, and the verifier approves summary-writing.

## Scenario 11: Static Artifact Beside An Unrelated Repo

```text
Use $ship-readiness-orchestrator to audit this pasted product concept and screenshots. No runtime is available, and the current repo is unrelated.
```

Expected behavior:

- Treats the pasted concept and screenshots as the target.
- Does not import ambient repo instructions, README, scripts, or architecture as target evidence.
- Runs a static constrained pass.
- Maps expected paths and missing paths, but marks runtime execution, persistence, deployability, and accessibility as blocked or evidence debt.

## Scenario 12: Exhaustive Surface Gauntlet

```text
Run Shipworthy full blast with authorized native agents against a bounded disposable UI intentionally containing hidden and confusing product behavior. Do not inspect its private oracle.
```

Fixture characteristics: duplicate labels with different behavior; nested and keyboard-only controls; mobile-only and role-gated actions; empty, invalid, stale-session, and prerequisite states; persistence that fails after reload; a visually plausible false affordance; a disabled control with no explanation; one avoided destructive action; and one promised-but-missing cancellation path visible only through runtime/source reconciliation.

Expected behavior:

- Builds semantic `intent → feature → surface → control → transition` rows rather than an ad hoc button list.
- Inventories every material surface and control across role, state, viewport, and input variants before claiming closure.
- Exercises each safe control once per materially different behavior, records before/after evidence, and checks material persistence after reload or re-entry.
- Preserves blocked and avoided controls as dispositions; does not inflate them into findings without a separately observed product failure.
- Reconciles runtime discovery with an independent canonical method at feature and surface levels.
- Requires two qualifying zero-yield passes from distinct canonical method families; renamed method details do not qualify.
- Rejects exhaustive closure for missing semantic rows, duplicate identities, unresolved evidence, caller/row count drift, reconciliation debt, or a JSON/HTML closure contradiction.
- Keeps the HTML action-first and human-readable; exhaustive proof lives in compact coverage summaries and collapsed details, not a wall of control rows.

# Pressure Tests

## Purpose

Use these scenarios to validate whether this skill actually orchestrates the three sub-skills coherently. Forward-tests should pass the skill and a realistic user request, not the expected answer.

## Contents

- Baseline Failure Patterns To Watch
- Scenario 0: Bare Invocation Defaults To Maximal Safe Coverage
- Scenario 0A: Shipworthy Brand Trigger Defaults To Full Blast
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
- The agent does not build a lane roster or under-launches independent agents in a full-blast run when agent tooling is available.
- The agent launches lanes without giving each lane the required sub-skill body, safe-test boundary, scope, excluded scope, and output packet contract.
- The agent omits the Orchestration Checkpoint or gives only prose without a lane roster table, making the lane roster, agent/tool execution mode, or verifier status hard to audit.
- The agent makes final findings, readiness claims, or recommendations that do not map to ledger rows or explicit evidence gaps.
- The agent says "all paths" without coverage labels and exclusions.
- The agent does not produce the mandatory HTML report for a full Shipworthy invocation.
- The agent ends after exactly three waves even though major coverage gaps remain.
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

## Scenario 0: Bare Invocation Defaults To Maximal Safe Coverage

```text
Run $ship-readiness-orchestrator on this app.
```

Expected behavior:

- Treats the request as a full Deep Review unless the target is unclear, static-only, genuinely tiny, or the user narrows scope.
- Reads the full `SKILL.md` bodies for ship-deep-review, ship-product-workflows, and ship-workflow-clarity before target analysis or lane dispatch.
- Runs the Multi-Agent Authorization Gate before deciding whether to dispatch subagents or use sequential fallback. If authorization is absent or ambiguous in the initial request, asks the authorization question and stops instead of continuing sequentially in the same response.
- Defaults product workflow routing to audit_all plus audit_top_tasks plus audit_high_risk.
- Builds a concrete lane roster before dispatching agents or running lanes sequentially.
- Establishes the canonical evidence state before lane dispatch, path testing, or design judgment.
- Writes target fingerprint, safe-test boundary, lane roster, path universe, path attempts, evidence debt, verifier decisions, and fix-cascade notes into the ledger as the run proceeds.
- Launches independent, non-overlapping lanes when the platform exposes agent tooling and the scopes do not conflict; otherwise records the tool limitation.
- Launches subagents only after explicit authorization for parallel subagents, delegation, or multi-agent work; if authorization is denied or not received after the gate question, runs the same lane roster sequentially and records the limitation.
- Includes an Orchestration Checkpoint in the final report with skill bodies read, references read, ledger location or inline snapshot, a lane roster table, agent/tool execution mode, verifier status, and omitted gates.
- Discovers the path universe before judging design.
- Attempts or safely traces every safe discoverable material path inside the declared boundary.
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
- For the response where it asks that question, stops there. It does not proceed to target analysis, tool work, repo reading, lane planning, or sequential fallback in the same response.
- If the user later says no or fails to answer after the gate was asked, continues sequentially and records `sequential fallback because multi-agent authorization was not granted` as evidence debt / orchestration debt.
- Plans at least three verified waves and records that three is a floor, not a ceiling.
- Uses adaptive continuation when path families, roles, contradictions, runtime proof, verifier objections, or evidence debt could change the verdict.
- Requires path-universe closure: every material expected intent and discovered path is covered, sampled with justification, blocked, avoided, inferred, missing, out_of_scope, or evidence_debt.
- Generates a mandatory HTML report from compact ledger JSON at `~/.shipworthy/runs/<target-slug>/<timestamp>/readiness-report.html` unless the user explicitly requests repo-local artifacts.
- Uses agents for discovery and verification only after explicit authorization when platform policy requires it, and uses a single coordinated runtime driver for a shared runtime unless isolated contexts are proven safe.

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

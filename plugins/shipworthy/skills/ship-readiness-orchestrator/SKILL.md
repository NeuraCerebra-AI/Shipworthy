---
name: ship-readiness-orchestrator
description: Use when the user mentions Shipworthy operationally; asks "are we shipworthy?", "are we shipready?", "is this shipworthy?", "shipworthy this", "check shipworthiness"; uses bare "shipworthy"; or asks for product/release readiness, full safe user-path audit, missing/overcomplicated UX paths, deployability, usability/design teardown, or making an app robust, clearer, simpler, beloved, viral, or effective.
---

# Shipworthy Readiness Orchestrator

## Core Promise

Run a repo-agnostic, evidence-heavy product readiness investigation that combines Deep Review, product workflow QA, and workflow clarity/design critique without creating competing truth layers or overclaiming readiness. Default invocation means maximum safe discoverable coverage: build a capped parallel lane roster when agents are available, map reasonable user intents, detect missing UX paths, test every safely testable path that can be reached within the declared boundary, judge path effort and design quality, then prove before proclaiming.

## Shipworthy Invocation Contract

Any operational mention of `shipworthy` triggers this orchestrator in full blast unless the user explicitly narrows scope, asks for a rapid/narrow/static pass, or is clearly discussing the Shipworthy skill system itself rather than asking to audit a target. The canonical trigger phrase is **"are we shipworthy?"**. Equivalent triggers include `shipworthy`, `is this shipworthy?`, `shipworthy this`, `make this shipworthy`, `check shipworthiness`, and readiness variants such as `are we shipready?`.

If no target is obvious, still treat the invocation as a Shipworthy run: complete the Sub-Skill Load Gate, then ask for or infer the target as the first Start Gate item. Do not silently downshift to a generic chat answer just because the trigger was short.

A full Shipworthy invocation is not a quick pass. Full blast means all safe discoverable path coverage, mandatory multi-wave evidence gates, adaptive continuation when coverage is unfinished, persistent goal-mode execution when the platform and user authorization allow it, and a mandatory HTML report generated from the final ledger. If the path universe, path_frontier, coverage matrix, verifier certificates, evidence debt register, goal-mode status, and HTML report path are missing, the run is incomplete.

## Required Sub-Skills

Use these skills as an ordered control stack:

1. **REQUIRED CONTROLLER:** Use `ship-deep-review` as the top-level controller for mission framing, waves, agent dispatch, the canonical claim ledger, coverage matrix, evidence debt, verifier gates, and final synthesis.
2. **REQUIRED PRODUCT LANE:** Use `ship-product-workflows` as the product/runtime workflow lane for path discovery, safe user-path testing, state, persistence, forms, navigation, permissions, backend symptoms tied to user-visible paths, responsive checks, accessibility smoke, and product evidence packets.
3. **REQUIRED CLARITY LANE:** Use `ship-workflow-clarity` after path discovery or runtime tracing for orientation, state clarity, next-action clarity, consequence and non-consequence clarity, recovery, trust/proof/governance, accessibility visibility, expert controls, design critique, and harmful simplification warnings.

Do not run these as peer controllers. Use one canonical Deep Review evidence state. Product workflow and clarity work feed packets into that state, inheriting prior evidence instead of re-deriving or double-counting it.

When lane skill instructions conflict with this orchestrator, apply the stricter safety, evidence, and synthesis rule. Lane wave patterns are lane-local evidence collection only; Deep Review owns wave barriers, verifier gates, summaries, readiness language, and final synthesis.

## Sub-Skill Load Gate

Before target analysis, agent dispatch, runtime testing, design critique, or final reporting:

1. Read this `ship-readiness-orchestrator/SKILL.md` completely.
2. Resolve and read the full `SKILL.md` for `ship-deep-review`.
3. Resolve and read the full `SKILL.md` for `ship-product-workflows`.
4. Resolve and read the full `SKILL.md` for `ship-workflow-clarity`.
5. If a sub-skill cannot be found or read, report it and continue as a **bounded standalone audit** using this skill's local references. Record the missing lane and lost independent coverage as evidence debt, keep the mandatory HTML report, and do not claim full multi-lane Shipworthy coverage.

Do not infer these sub-skills from their names. Do not dispatch a product or clarity lane before the matching sub-skill body has been read.

## Goal Mode Persistence Gate

For every full Shipworthy invocation, after the Sub-Skill Load Gate and before the Multi-Agent Authorization Gate, check whether the current platform offers persistent `/goal` mode, a goal tool, or an equivalent long-running objective mechanism. Do not imply that Shipworthy instructions override platform goal-mode policy; platform/tool policy wins.

If the current user request invokes `/goal`, says to use goal mode, asks for persistent goal mode, or explicitly authorizes goal persistence, start or continue a persistent Shipworthy goal when the platform exposes that capability and policy allows it. Use an objective such as: "Complete the full Shipworthy audit for <target>, including safe frontend path-walking, path_frontier closure, adaptive exhaustion, verifier gates, and mandatory HTML report." Record `goal_mode_status`, the objective, and whether the platform goal is active in the ledger and Orchestration Checkpoint.

If goal mode is available but explicit authorization is absent or ambiguous, ask once together with the multi-agent authorization ask when multi-agent authorization is also absent:

> Shipworthy full blast is a long-running audit. Recommended: reply yes to authorize persistent goal mode and parallel subagents for this Shipworthy run.

If the previous assistant message asked the combined authorization question and the user replies `yes`, `yes for both`, `authorized`, or equivalent, treat that as explicit authorization for both persistent goal mode and parallel subagents. In Codex, when a goal tool is available and platform policy allows it, create or continue the persistent Shipworthy goal before lane dispatch, then record `goal_mode_status: active` or the platform-specific result. If goal creation fails or is unavailable, record `goal_mode_status: unavailable` or `goal_mode_status: failed` and continue with a goal-equivalent resumable ledger; if subagent dispatch is unavailable despite authorization, record the dispatch limitation separately.

If the platform has goal mode but authorization is denied, unavailable, or not received after the gate question, record `goal_mode_status: not_authorized` and continue with a goal-equivalent resumable ledger. If the platform has no goal mode, record `goal_mode_status: unavailable` and continue with the same goal-equivalent resumable ledger. Goal-mode fallback is orchestration debt, not a reason to skip frontier closure, verifier gates, or the HTML report.

## Start Gate

Before dispatching agents, writing findings, or judging design quality:

1. Read the full user request and all target-defining files, screenshots, URLs, docs, or local instructions.
2. Read target repo/app instructions and source-of-truth docs when present and target-relevant: `AGENTS.md`, `CLAUDE.md`, README, architecture docs, product docs, test docs, deploy docs, package scripts, or equivalent. If the target is only a supplied static artifact, screenshot set, paste, or scenario, do not treat the ambient working directory as target truth unless the user explicitly connects it.
3. Record the target fingerprint: repo path, branch, commit, dirty state, worktree, runtime URL or launch command, environment, timestamp, account/role/fixture, viewport/device assumptions, and evidence output location.
4. Define the safe-test boundary: allowed actions, forbidden actions, mutation risks, reset plan, privacy constraints, paid/provider constraints, production risks, and stop conditions.
5. Treat the run as read-only unless the user explicitly authorizes a specific action, the fixture/reset plan is known, and the action is inside a disposable or safely resettable environment. High-risk actions require both explicit approval and a disposable/resettable environment.

## Multi-Agent Authorization Gate

For every full Shipworthy invocation, after the Goal Mode Persistence Gate and before lane dispatch or sequential fallback, check whether the current platform's agent tooling requires explicit user authorization for subagents, delegation, or parallel agent work. Do not imply that Shipworthy instructions override platform tool policy; platform/tool policy wins.

If the current user request already explicitly authorizes parallel subagents, delegation, or multi-agent work, such as **"Run Shipworthy full blast with parallel subagents authorized"**, record that authorization in the ledger and proceed to the multi-agent lane roster when safe.

If authorization is absent or ambiguous in the current user prompt, this is not yet a denial and not yet "not received." The next response must ask the authorization question and stop. Do not continue target analysis, tool work, lane planning, or sequential fallback in the same response. Do not say you are proceeding sequentially before the authorization question has been asked. If the Goal Mode Persistence Gate also needs authorization, ask the combined question from that gate. Otherwise ask exactly:

> Shipworthy full blast is designed to use parallel subagents for independent product, clarity, release, accessibility, state, and verifier lanes. Do you authorize parallel subagents / delegation / multi-agent work for this Shipworthy run?

Only dispatch subagents after the user explicitly authorizes parallel subagents, delegation, or multi-agent work. Not received means the user failed to answer after the authorization question was asked, not merely that the original request lacked authorization. If authorization is denied, unavailable, or not received after the gate question, run the same lane roster sequentially and record **"sequential fallback because multi-agent authorization was not granted"** in the ledger, Orchestration Checkpoint, evidence debt / orchestration debt, and final report. Do not treat sequential fallback as equivalent to independent multi-agent coverage.

## Flagship Frontend Path-Walk Gate

For every full Shipworthy invocation, after the Multi-Agent Authorization Gate and before source-heavy analysis, run the Flagship Frontend Path-Walk Gate. Repeat this commitment before starting work:

> I will run the full flagship Shipworthy audit unless you explicitly narrow scope. That means I will use the actual frontend through browser, in-app browser, Chrome, Playwright, or Computer Use when available; interact like a human; map the path universe; attempt every safe discoverable user path; record blocked, avoided, unsafe, and unavailable paths as evidence debt; and use source, CLI, HTTP, tests, logs, and docs as supporting evidence, not as a substitute for frontend path-walking. If I cannot perform actual frontend path-walking, I will label the result conditional, static, or limited, not a full Shipworthy run.

Actual frontend path-walking is required for a full flagship run when a runnable UI, hosted app, local dev server, browser-hosted prototype, desktop app, Chrome session, in-app browser surface, or Computer Use target is available. Human-style frontend evidence means action sequences through the product UI with observed screens/states and artifacts such as screenshots, DOM/UI/accessibility snapshots, console/network traces, recordings, or Computer Use screenshots.

Read `references/browser-evidence-routing.md` before selecting a frontend tool. Use the host's native browser or computer-use capability by default for adaptive exploration. Use an existing target-owned Playwright setup only for deterministic replay, explicit assertions, isolated contexts, traces, cross-browser checks, or CI regression proof. Record the selection and its proof boundary in the ledger; the tool choice never changes the canonical proof or verifier rules.

Shipworthy operates through the four public skills and their skill-owned resources. Continue to route and report through those skills without requiring another product surface.

Source, CLI, HTTP, tests, logs, docs, Railway/provider checks, and database probes are supporting evidence, not as a substitute for frontend path-walking. Use them to find routes, explain symptoms, verify backend causes, and support release gates, but do not let them replace the actual product walk.

If no actual frontend path-walking occurred, the result is not a full Shipworthy run. Label it as `bounded conditional audit`, `static constrained pass`, `changed-only pass`, or `source/CLI readiness audit`, record the downgrade reason, and do not use full flagship language. The final report must include frontend path-walk status, frontend tool, runtime target, path-walk status, and downgrade reason when applicable.

## HTML Report Gate

Every operational Shipworthy invocation must produce a self-contained HTML readiness report from the final ledger, regardless of whether the run is full flagship, conditional, static constrained, changed-only, source/CLI-only, or downgraded. Downgrade status changes the report contents and verdict language; it does not remove the report requirement.

Generate `readiness-report.json` and `readiness-report.html` from the final ledger after verification. Default to `~/.shipworthy/runs/<target-slug>/<timestamp>/readiness-report.html` so the audited repo stays read-only. Use repo-local `.shipworthy/reports/<timestamp>/readiness-report.html` only when the user explicitly requests repo artifacts or the target's instructions require repo-local audit artifacts.

Before final response, verify that `readiness-report.html` exists, was rendered from the final ledger/report JSON, and is linked in the final answer. If report generation fails, file writes are impossible, or the user explicitly forbids artifact creation, lead the final answer with **`HTML report: MISSING/BLOCKED`**, explain why, record it as deliverable debt, and do not imply the Shipworthy run is complete.

## Full-Blast Agent Rules

For a full readiness run, use agents when the platform exposes agent tooling, the work decomposes into independent non-overlapping lanes, and the Multi-Agent Authorization Gate has explicit authorization. Before launch, write a lane roster with each lane's scope, excluded overlap, required sub-skill body, expected output packet, evidence artifact location, safe-test boundary, and multi-agent authorization status. Each lane prompt must require reading the applicable `SKILL.md` body before acting. The final report must include or point to this roster; otherwise the full-blast run is incomplete.

- Codex: run at most 6 concurrent specialist agents; close completed agents after their outputs are read.
- Claude Code: launch all independent wave agents at once when there are 13 or fewer and scopes do not conflict; prefer fewer lanes when the target is small or scopes overlap.
- If agent tooling is unavailable, unsafe, too overlapping, or not explicitly authorized, run the lanes sequentially in the main session and record the limitation as evidence debt / orchestration debt in the final report. Do not pretend a sequential pass had independent-agent coverage.
- Agents parallelize discovery, route inventory, design critique, release gates, state/API tracing, role/permission checks, disconfirmation, and verification. The orchestrator owns the canonical ledger and runtime execution plan.
- For one shared runtime, use a single coordinated runtime driver by default. Multiple agents may drive the live app only when isolated users, resettable fixtures, disposable data, independent browser profiles, or read-only surfaces make the evidence safe and non-conflicting. Otherwise agents return path plans and evidence packets while the orchestrator or one designated runtime lane performs coordinated clicking.

## Full-Blast Wave Contract

Full blast requires a minimum of three verified waves after Wave 0 preflight: broad reconnaissance, targeted deep dive, and release-gate / what-did-we-miss. This is a minimum of three verified waves, not a maximum. Every wave summary requires the Deep Review read-all, evidence-state, independent-verifier, verification-certificate, and drift-check gate.

Use adaptive continuation after Wave 3 when coverage is not closed. Continue with additional waves when major route families, user roles, state variants, runtime proof, contradictions, high-severity disconfirmation, safe path attempts, or evidence debt remain unresolved, or when the verifier objects that coverage is too thin. Do not end a full blast because three waves happened; end only when the coverage matrix and evidence debt justify the final scope and verdict.

Path-universe closure is mandatory. Every material expected intent and discovered path must be labeled covered, sampled with justification, blocked, avoided, inferred, missing, out_of_scope, or evidence_debt before final readiness language is written. Treat all safe discoverable paths as the coverage ambition; do not substitute a few happy paths, top tasks, or agent consensus.

## Adaptive Exhaustion Gate

For a full flagship Shipworthy run, create a **Path Frontier Ledger** named `path_frontier` before quality judgment. The path_frontier is stricter than the coverage summary: it is the live queue of every material expected user intent, discovered route, screen, control, role, state variant, device/input variant, integration, and safe action that could change the readiness verdict.

Before collection, read `references/evidence-state.md`, `references/schemas/readiness-ledger.schema.json`, and `ship-product-workflows/references/path-discovery-and-coverage.md`. Maintain one canonical `path_frontier` using the readiness-ledger schema; do not accept an ad hoc list or a second frontier shape from a lane.

Path frontier sources must include runtime crawl, visible UI, routes, components, APIs, docs, tests, fixtures, roles, states, device variants, and expected human intents. Apply the **Human-Tester Matrix**: first-time user, confused user, impatient user, returning stale-state user, mobile user, keyboard-only user, empty/loading/error states, permission mismatch, guest/member/admin where applicable, and the intent families create, edit, delete/cancel, recover, invite/share/export/import, settings/account, onboarding, failure recovery, payment/auth where applicable.

Each `path_frontier` row must use versioned semantic lineage from intent through feature, surface, control, and transition; record observations from canonical method families; and carry attempt/evidence proof. Valid terminal statuses are `covered`, `sampled_with_justification`, `blocked`, `avoided`, `missing`, `out_of_scope`, and `evidence_debt`.

A full final verdict is forbidden while any material path_frontier row remains `unattempted`, `unknown`, or `maybe`. Continue after the minimum three waves until every material row has a terminal status, runtime discovery is reconciled at feature and surface levels, and two qualifying zero-yield discovery passes from distinct canonical method families find no new material routes, controls, roles, states, device variants, or user intents. Before final synthesis, run a verifier pass asking "what plausible paths were missed?" If that pass names a plausible untested material path, add it to `path_frontier` and continue or downgrade.

Use adaptive effort floors and caps to prevent shallow exits without wasting tiny targets: tiny targets close the frontier or spend 10-20 minutes / 15-30 meaningful attempts; small targets close the frontier or spend 30-45 minutes / 40-80 meaningful attempts; medium targets close the frontier or spend 60-90 minutes / 100-200 attempts; large targets may need multi-session frontier burn-down. Time or attempt count alone never proves completion.

If tool, auth, context, safety, or budget limits prevent frontier closure, set `exhaustion_status: incomplete`, list the remaining path_frontier rows and the next frontier batch, render the HTML report, and provide a resume prompt. Do not call the run complete or full Shipworthy when material frontier rows remain unresolved.

## Ledger Protocol

Before lane dispatch, path testing, verifier work, or summary-writing, establish one canonical evidence state owned by the orchestrator. If a writable evidence location exists, record the ledger path or artifact location; otherwise maintain the ledger explicitly in working notes and include its inline snapshot in the final report. Lane agents return raw packets; they do not write the canonical ledger directly.

Write to the ledger at these gates:

1. Target fingerprint and safe-test boundary.
2. Lane roster and planned evidence locations.
3. Expected intents, missing-path candidates, and path universe.
4. Each path attempt or safe trace, immediately after observation.
5. Each lane output after the orchestrator reads it in full and normalizes severity, confidence, provenance, and coverage labels.
6. Verifier decisions: approved, downgraded, rejected, needs-proof, blocked, and required retargeting.
7. Fix-cascade notes for major recommendations.
8. Final drift check and final disposition of evidence debt.

Every material claim, missing path, blocked check, avoided check, rejected claim, false positive, recommendation, and readiness statement must map to a ledger row or explicit evidence gap. Do not use a narrative paragraph as a substitute for a ledger write. Do not delete inconvenient rows; update status and final disposition.

## Mandatory Flow

1. Complete the Sub-Skill Load Gate.
2. Route the run as a full Deep Review unless the user explicitly asks for a rapid or narrow pass.
3. Run the Goal Mode Persistence Gate. If `/goal`, persistent goal mode, or goal authorization is explicit and platform policy allows it, start or continue that goal; otherwise record `goal_mode_status` and use a goal-equivalent resumable ledger.
4. Run the Multi-Agent Authorization Gate for full Shipworthy invocations. If explicit authorization is already present (for example, "Run Shipworthy full blast with parallel subagents authorized"), record it and continue. If authorization is absent or ambiguous, ask the authorization question and stop before deciding multi-agent dispatch vs sequential fallback. Do not continue sequentially in the same response.
5. Run the Flagship Frontend Path-Walk Gate. Identify the actual frontend target and tool plan before source-heavy analysis. If actual frontend path-walking is impossible or explicitly out of scope, downgrade the run label immediately and record why.
6. Route `ship-product-workflows` as `major` for broad readiness, defaulting to `audit_all` plus `audit_top_tasks` plus `audit_high_risk`. Downshift only when the user explicitly asks for a rapid/narrow pass, the target is genuinely small/static-only, actual frontend path-walking is impossible, or safe-test boundaries make full coverage impossible. If `audit_all` is not feasible, still map the whole discovered path universe and label every path covered, sampled, blocked, avoided, inferred, missing, out_of_scope, or evidence_debt. For a delta / in-session re-audit ("is my change ready?"), run changed-scope mode per `references/changed-scope.md`: scope to the changed surface plus its blast radius, mark untouched paths `out_of_scope`, and keep the verdict scoped to the change rather than the whole product.
7. Read `references/evidence-state.md` and initialize the canonical evidence state before lane roster, dispatch, path testing, or summaries. Record target fingerprint, safe-test boundary, ledger location or inline-ledger plan, goal_mode_status, multi-agent authorization status, frontend path-walk status, first evidence debt rows, and initial claim/coverage/debt/frontier table headers.
8. Read `references/lane-prompts.md` and build a concrete lane roster before dispatch: product/runtime path QA, workflow clarity/design critique, release/deploy gates, accessibility/responsive smoke, data/state/persistence, role/permission, and verifier lanes as applicable. Keep scopes independent and non-overlapping. Write the roster, goal_mode_status, multi-agent authorization status, frontend tool plan, and path-walk status to the ledger.
9. Launch the first wave of specialist agents according to the Full-Blast Agent Rules only if explicitly authorized. Give every lane the target fingerprint, safe-test boundary, evidence-state contract, required sub-skill body to read, exact scope, excluded scope, output packet format, frontend path-walk requirement, path_frontier additions requirement, and proof limits. If agents cannot be launched, or authorization was denied/unavailable/not received, record why and run the same lane roster sequentially.
10. Discover and map the bounded path universe and path_frontier before judging quality: reasonable user intents, surfaces, actors, roles, states, entry points, actions, hidden paths, variants, integrations, data states, devices, and mutation risks. Build a material-state control census on every material surface and role/state/device variant, including nested, keyboard-only, mobile-only, disabled, duplicate-label, and apparently actionable controls. Treat "try every single path" as a command to pursue every safe discoverable path inside the declared boundary, and to flag expected user goals with no discoverable UX path, with honest exclusions and evidence debt for anything unsafe, unavailable, duplicate, static-only, blocked, or infeasible. Write expected intents, path-universe rows, and path_frontier rows to the ledger. When the target matches a known archetype, load `profiles/<archetype>.json` per `references/archetype-overlays.md` and add its expected intents and frequently-missing paths as provenance-tagged hypotheses in the path universe — priors to confirm or disprove with evidence, never a checklist and never marked covered without proof.
11. Execute every safely testable discovered path inside the declared boundary through the actual frontend when available. Exercise every safe material control once per materially different behavior and record before/after evidence; verify persistence after refresh or re-entry when material. Try happy paths, empty states, loading states, invalid inputs, error states, recovery paths, navigation variants, role/permission variants, responsive/mobile variants, persistence/reload points, and reasonable edge cases. Stop at unsafe, paid, destructive, privacy-sensitive, production, or irreversible actions unless the user authorized that exact action and a reset/disposable environment exists. Write each path attempt, trace, result, label, frontend artifact, and source/supporting artifact reference to the ledger immediately after observation.
12. Run the Adaptive Exhaustion Gate after each wave: update the path_frontier burn-down, record new paths found this wave, retarget the next wave from unresolved frontier rows, and do not final while material rows remain `unattempted`, `unknown`, or `maybe`.
13. For every material user goal, assess path existence and path effort: whether a path exists, where it starts, how many steps and decisions it requires, whether it has detours, repeats, context switches, hidden prerequisites, waiting states, unclear labels, dead ends, or recovery burden. Flag paths that technically work but are unreasonably long, fragile, buried, or cognitively expensive. Write missing-path and overcomplicated-path findings to the ledger.
14. Maintain one shared evidence state: claim ledger, coverage matrix, path_frontier, evidence debt register, product coverage map, path traces, path-effort notes, evidence inventory, provenance tags, clarity lane packets, false positives, rejected claims, blocked checks, avoided checks, missing paths, and untested paths. Every material path or expected intent must have a status label: covered, sampled, sampled_with_justification, blocked, avoided, inferred, missing, out_of_scope, or evidence_debt.
15. If the available evidence is static only, such as screenshots, README, docs, package scripts, or source snippets with no runnable runtime, route as a static constrained pass. Keep runtime behavior, persistence, accessibility, deployability, and path completion claims provisional, blocked, inferred, missing, or evidence debt unless directly proven.
16. Pass product path evidence, missing-path candidates, and path-effort notes to `ship-workflow-clarity`; ask it for compact lane packets, not a competing full ledger. Clarity/design critique happens after path discovery and initial product evidence, and must tie visual or attention critiques to workflow consequence.
17. At the end of every wave, read every expected lane output in full, merge normalized lane packets into the ledger, then run an independent verifier against the raw outputs and ledger. The verifier must fail the full-run claim if no browser/computer-use/frontend path-walk occurred while the report claims full Shipworthy. Do not write a wave intelligence summary until the verifier explicitly approves summary-writing.
18. Retarget each later wave from verified findings, contradictions, coverage gaps, missing expected paths, overcomplicated paths, path_frontier burn-down, and evidence debt, not from the original lane split.
19. Run a fix-cascade check on major recommendations: compare against the no-change baseline, identify what the fix could break downstream, and preserve proof, governance, recovery, accessibility, expert controls, and necessary friction. Write fix-cascade notes to the ledger.
20. Before final synthesis, run a final no-overclaim verifier against the final claim ledger, path_frontier burn-down, evidence debt, coverage gaps, frontend path-walk status, and readiness language. The verifier must ask what plausible paths were missed and fail a full-run claim if material frontier rows remain unattempted/unknown/maybe or if the last two discovery/testing passes still found new material path surface. Downgrade claims such as ready, works, accessible, robust, secure, deployable, beloved, viral, complete, or full Shipworthy unless directly supported.
21. Run the HTML Report Gate for every operational Shipworthy invocation. Generate `readiness-report.json` and `readiness-report.html` from the final ledger even when the run is conditional, static constrained, changed-only, source/CLI-only, or downgraded. Default to `~/.shipworthy/runs/<target-slug>/<timestamp>/readiness-report.html` so the audited repo stays read-only. Use repo-local `.shipworthy/reports/<timestamp>/` only when the user explicitly requests repo artifacts.
22. Run the Pre-Final Artifact Assertion: final ledger exists or an inline ledger snapshot exists; `readiness-report.json` exists unless artifact writes are blocked; `readiness-report.html` exists unless artifact writes are blocked; final answer includes the absolute HTML path; and if any item is missing, the final answer leads with missing artifact debt instead of implying completion.
23. Write the final report only after the final claim ledger, path_frontier burn-down, exhaustion_status, evidence debt, coverage gaps, verified wave summaries, verifier outputs, fix-cascade notes, final drift check, goal_mode_status, multi-agent authorization status, frontend path-walk status, HTML report generation status, mandatory HTML report path, and ledger/evidence paths are complete.

## Design Critique Mandate

For every important page, screen, route, panel, dialog, flow, or state, ask:

- Is this ugly, generic, overcluttered, visually noisy, or hard to scan?
- Is attention going to the right thing first?
- Is there one obvious next action where the workflow needs one?
- Is there a reasonable path for what a user would naturally try to do here?
- Is the path too long, buried, repetitive, fragile, or cognitively expensive for the value it provides?
- Is the page saying too much, too early, or in the wrong order?
- Does layout clarify state, progress, object, consequence, and recovery?
- Does the experience feel trustworthy, polished, modern, and worth continuing?
- Would a first-time user feel momentum or friction?
- What should be removed, grouped, renamed, reordered, deemphasized, or made more prominent?
- What would make this simpler, clearer, more effective, and more attention-retaining without hiding proof, controls, recovery, accessibility paths, expert power, or governance boundaries?

Tie every design critique to observed workflow consequence. Do not report taste as severity without user impact.

When the user asks for "beloved", "viral", "attention-retaining", or similar product outcomes, translate that into testable hypotheses: time-to-value, first-run momentum, emotional payoff, repeat-use loop, share/referral moment, trust, perceived quality, and support burden. Do not claim the product will be beloved or viral; report what the evidence suggests would help or block those outcomes.

## Reference Routing

Load only the references needed for the current pass:

- Read `references/lane-prompts.md` before dispatching product, clarity, design, verifier, or release-gate lanes.
- Read `references/browser-evidence-routing.md` before native browser, computer-use, or Playwright work.
- Read `references/host-execution-recipes.md` before invoking target-owned execution. Follow its ordered delegation from existing repository tests, through native adaptive exploration and existing deterministic Playwright replay, to an explicitly authorized target-owned test proposal; otherwise record evidence debt.
- Read `references/ledger-validation-contract.md` before structured render or import; use its `references/schemas/readiness-ledger.schema.json`, `references/schemas/report-input.schema.json`, or `references/schemas/browser-evidence-envelope.schema.json` as selected by the declared input type.
- Read `references/evidence-import-contract.md` only for browser, Playwright, or legacy structured input.
- Read `references/evidence-state.md` and `ship-product-workflows/references/path-discovery-and-coverage.md` before creating ledgers, the material-state control census, coverage matrices, path labels, severity/confidence normalization, evidence debt, evidence storage, or readiness claims.
- Read `references/final-report-contract.md` before writing the final report or roadmap.
- Read `references/archetype-overlays.md` when the target matches a known product archetype (checkout, auth, ai-chat, dashboard, …). The `profiles/*.json` seed path discovery with priors — expected intents, common failure modes, and frequently-missing paths — as **hypotheses to confirm or disprove with evidence, never a pass/fail checklist**.
- Read `references/changed-scope.md` for a delta / in-session re-audit ("is my change ready?"): scope to the changed surface **plus its blast radius**, label untouched paths `out_of_scope`, and return a verdict scoped to the change — not the whole product.
- Read `references/visual-html-report.md` for every operational Shipworthy invocation. It documents the mandatory HTML dashboard, `scripts/render_report.py`, and the JSON contract.
- Read `references/exports-and-ci.md` when the user wants to share, archive, gate, or automate: the mandatory HTML render, the SARIF export (`scripts/to_sarif.py`), the tamper-evident evidence bundle (`scripts/make_bundle.py`), the confirmed-only merge gate, the opt-in `--interactive` report, and the optional GitHub code-scanning recipe. All local-first; all renders of the finished ledger.
- Read `references/pressure-tests.md` when validating or forward-testing this skill, or when the user asks whether the orchestration is strong enough.

## Output Contract

Lead with findings and readiness truth, organized by action. Use these visible sections before thematic detail: **Clear Before Ship** for readiness-blocking confirmed failures or missing paths; **Fix Next** for real non-blocking issues; **Not Proven / Not Tested** for evidence debt, blocked/avoided/unsafe/unavailable paths, hypotheses, and unverified claims; and **Passed / Keep** for paths that worked under the tested conditions. Each item must carry one action chip (`Fix`, `Prove`, `Decide`, `Skip`, or `Keep`) and one proof chip (`Confirmed`, `Partial`, `Inferred`, or `Not tested`). Do not use vague visible buckets such as "working signals" or "strong signals" in final user-facing output. Do not claim ready, safe, correct, accessible, persistent, secure, beloved, viral, passing, or fixed without evidence.

For operational Shipworthy runs, include an **Orchestration Checkpoint** in the report: skill bodies read, references read, target fingerprint, safe-test boundary, ledger location or inline snapshot, goal_mode_status, multi-agent authorization status, frontend path-walk status, actual agent/tool execution mode, runtime driver mode, verifier status, omitted gates, path_frontier burn-down, exhaustion_status, HTML report generation status, mandatory HTML report path, and where raw outputs/evidence live. Under that checkpoint, include a lane roster table with one row per planned lane and columns for lane, scope, required skill/reference, execution status, output/evidence location, and skipped/collapsed/blocking reason. If agent dispatch was skipped because authorization was denied, unavailable, or not received, state **"sequential fallback because multi-agent authorization was not granted"**. If actual frontend path-walking did not occur, state the downgrade reason and do not call the report a full Shipworthy run. If the checkpoint, roster table, path-universe closure, path_frontier closure, verifier certificates, frontend path-walk status, report generation status, or HTML report path is missing, the report is not complete.

For each finding include evidence, user consequence, likely cause, smallest useful fix, counterfactual/no-change baseline when relevant, downstream regression or simplification risk, and exact verification step. For full runs, include a coverage table for every discovered material path and expected user intent, including paths covered, sampled, blocked, avoided, inferred, missing, out of scope, and still carrying evidence debt.

### Canonical artifact gate

Before the verifier approves or HTML is rendered, the final readiness-ledger.json and report-input.json must each contain the same top-level `path_frontier` object with every canonical row, discovery pass, reconciliation difference, derived count, and closure field. Do not leave the frontier only in a raw observation file, sidecar, checkpoint, or narrative. Schema-valid legacy compatibility is not sufficient for a current full run. Every `Fix` finding must contain non-empty `affected_semantic_keys`, a semantic `observed_effect_code`, and `evidence_refs`. Re-open both final JSON files from disk after writing them, compare their frontier identities/counts/closure and finding lineage, then render HTML from that exact report input. Missing or divergent canonical data fails completion even when a legacy-compatible schema accepts the shell.

For a current full run, `path_frontier` must be an object, never a list. It must contain `rows`, `discovery_passes`, `reconciliation_differences`, and derived `summary` alongside its version and closure fields. Every finding's `affected_semantic_keys` must use exact `shipworthy-semantic-v1` keys present in `path_frontier.rows`, never unversioned aliases or finding-only shorthand. If either artifact uses the legacy list shape, any required object member is absent, or finding lineage does not resolve to exact rows, fail the run before rendering; do not translate, infer, or declare closure from that artifact.

Do not implement fixes unless the user explicitly asks for implementation after the review.

End every operational Shipworthy final answer with this concise fix handoff unless the user explicitly forbids follow-up work:

> Recommended next step: reply **yes** and I'll start a persistent fix goal for the **Clear Before Ship** items using authorized subagents where helpful. I'll apply the fixes safely, verify each one, regenerate the Shipworthy HTML report, and stop only when every remaining item is either passed, intentionally scoped out, or still clearly listed as not proven.

**Ledger-derived deliverables (local-first; never a second source of truth).** The inline report and self-contained **HTML report** (`scripts/render_report.py`; verdict, covered-%, action-first findings, checkpoint) are required for every operational Shipworthy invocation and are generated only after the ledger is final. The HTML report defaults to no JS; `--interactive` is an opt-in variant that adds client-side filter/search/collapse. Additional exports, when the user wants to share, archive, gate, or automate, are:
- a **SARIF 2.1.0** file (`scripts/to_sarif.py`) for GitHub code scanning, with an optional **merge gate** (`--gate`) that fails on confirmed blockers only;
- a tamper-evident **evidence bundle** (`scripts/make_bundle.py`; ledger + report + SARIF + a SHA-256 manifest) for a defensible audit trail — see `references/exports-and-ci.md`.
The ledger JSON is itself the canonical machine-readable export.

## Common Failure Modes

- Letting `ship-product-workflows` or `ship-workflow-clarity` become peer controllers with separate final readiness conclusions.
- Naming `ship-deep-review`, `ship-product-workflows`, or `ship-workflow-clarity` without reading their full `SKILL.md` bodies first.
- Skipping the lane roster or under-launching agents during a full-blast run when independent agent tooling is available and explicitly authorized.
- Dispatching subagents without explicit user authorization for parallel subagents, delegation, or multi-agent work when platform tool policy requires it.
- Treating Shipworthy instructions as overriding Codex or Claude Code tool policy.
- Pretending `/goal` or persistent goal mode was activated when platform goal-mode policy, missing authorization, or missing tooling prevented it.
- Sending a full final verdict while a material path_frontier row is still `unattempted`, `unknown`, or `maybe`.
- Stopping because no one asked "do another round" even though the frontier burn-down or verifier still names plausible untested paths.
- Hiding sequential fallback caused by missing multi-agent authorization instead of recording it as orchestration debt.
- Delaying ledger creation until the end, treating the final prose as the ledger, or letting lane agents create competing ledgers.
- Omitting the Orchestration Checkpoint from the final report, leaving agent/sequential fallback, lane roster, or verifier status invisible.
- Omitting `readiness-report.html` because the run was downgraded, static constrained, changed-only, or source/CLI-only. Shipworthy invocation means HTML report, always, unless the user forbids file creation or writes are impossible.
- Sending a final answer without first verifying that `readiness-report.html` exists and linking its absolute path.
- Starting with visual judgment before workflow cartography.
- Defaulting to top-task/high-risk sampling when the user invoked this skill for a full readiness run.
- Treating "try every path" as omniscience instead of coverage mapping, actual safe execution, labels, and exclusions.
- Substituting source/CLI/HTTP checks for actual frontend path-walking during a full flagship run.
- Calling a source/CLI/HTTP-only readiness audit a full Shipworthy run.
- Only testing paths that exist and missing reasonable user goals that have no UX path.
- Treating a path as acceptable because it technically completes, while ignoring excessive steps, hidden entry points, repeated decisions, fragile prerequisites, or needless context switches.
- Sending a draft narrative summary to the verifier instead of raw outputs and evidence state.
- Treating agent consensus as evidence.
- Dropping evidence debt between waves.
- Re-deriving prior lane evidence without provenance tags, then counting the same fact twice.
- Making screenshot-only claims about behavior, persistence, accessibility, or reachability.
- Turning clarity critique into generic visual polish.
- Treating "beloved", "viral", or "attention-retaining" as a promise rather than a hypothesis to test.
- Simplifying away proof, governance, recovery, expert controls, accessibility paths, or productive friction.
- Recommending a broad redesign when a smaller fix would solve the observed workflow consequence.
- Skipping the fix-cascade check and proposing changes that create new failure paths.
- Turning product workflow QA into an unbounded backend architecture review.
- Clicking mutating, paid, destructive, publishing, permissioned, privacy-sensitive, production, or irreversible actions without explicit safe-test permission.

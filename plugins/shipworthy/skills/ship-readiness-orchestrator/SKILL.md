---
name: ship-readiness-orchestrator
description: Use when the user mentions Shipworthy operationally; asks "are we shipworthy?", "is this shipworthy?", "shipworthy this", "check shipworthiness"; uses bare "shipworthy"; or asks for product/release readiness, full safe user-path audit, missing/overcomplicated UX paths, deployability, usability/design teardown, or making an app robust, clearer, simpler, attention-retaining, beloved, viral, or effective.
---

# Shipworthy Readiness Orchestrator

## Core Promise

Run a repo-agnostic, evidence-heavy product readiness investigation that combines Deep Review, product workflow QA, and workflow clarity/design critique without creating competing truth layers or overclaiming readiness. Default invocation means maximum safe discoverable coverage: build a capped parallel lane roster when agents are available, map reasonable user intents, detect missing UX paths, test every safely testable path that can be reached within the declared boundary, judge path effort and design quality, then prove before proclaiming.

## Shipworthy Invocation Contract

Any operational mention of `shipworthy` triggers this orchestrator in full blast unless the user explicitly narrows scope, asks for a rapid/narrow/static pass, or is clearly discussing the Shipworthy skill system itself rather than asking to audit a target. The canonical trigger phrase is **"are we shipworthy?"**. Equivalent triggers include `shipworthy`, `is this shipworthy?`, `shipworthy this`, `make this shipworthy`, and `check shipworthiness`.

If no target is obvious, still treat the invocation as a Shipworthy run: complete the Sub-Skill Load Gate, then ask for or infer the target as the first Start Gate item. Do not silently downshift to a generic chat answer just because the trigger was short.

A full Shipworthy invocation is not a quick pass. Full blast means all safe discoverable path coverage, mandatory multi-wave evidence gates, adaptive continuation when coverage is unfinished, and a mandatory HTML report generated from the final ledger. If the path universe, coverage matrix, verifier certificates, evidence debt register, and HTML report path are missing, the run is incomplete.

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
5. If a required sub-skill cannot be found or read, stop normal execution, report the missing skill, and continue only with an explicitly downgraded fallback.

Do not infer these sub-skills from their names. Do not dispatch a product or clarity lane before the matching sub-skill body has been read.

## Start Gate

Before dispatching agents, writing findings, or judging design quality:

1. Read the full user request and all target-defining files, screenshots, URLs, docs, or local instructions.
2. Read target repo/app instructions and source-of-truth docs when present and target-relevant: `AGENTS.md`, `CLAUDE.md`, README, architecture docs, product docs, test docs, deploy docs, package scripts, or equivalent. If the target is only a supplied static artifact, screenshot set, paste, or scenario, do not treat the ambient working directory as target truth unless the user explicitly connects it.
3. Record the target fingerprint: repo path, branch, commit, dirty state, worktree, runtime URL or launch command, environment, timestamp, account/role/fixture, viewport/device assumptions, and evidence output location.
4. Define the safe-test boundary: allowed actions, forbidden actions, mutation risks, reset plan, privacy constraints, paid/provider constraints, production risks, and stop conditions.
5. Treat the run as read-only unless the user explicitly authorizes a specific action, the fixture/reset plan is known, and the action is inside a disposable or safely resettable environment. High-risk actions require both explicit approval and a disposable/resettable environment.

## Full-Blast Agent Rules

For a full readiness run, use agents when the platform exposes agent tooling and the work decomposes into independent, non-overlapping lanes. Before launch, write a lane roster with each lane's scope, excluded overlap, required sub-skill body, expected output packet, evidence artifact location, and safe-test boundary. Each lane prompt must require reading the applicable `SKILL.md` body before acting. The final report must include or point to this roster; otherwise the full-blast run is incomplete.

- Codex: run at most 6 concurrent specialist agents; close completed agents after their outputs are read.
- Claude Code: launch all independent wave agents at once when there are 13 or fewer and scopes do not conflict; prefer fewer lanes when the target is small or scopes overlap.
- If agent tooling is unavailable, unsafe, or too overlapping, run the lanes sequentially in the main session and record the limitation as evidence debt in the final report. Do not pretend a sequential pass had independent-agent coverage.
- Agents parallelize discovery, route inventory, design critique, release gates, state/API tracing, role/permission checks, disconfirmation, and verification. The orchestrator owns the canonical ledger and runtime execution plan.
- For one shared runtime, use a single coordinated runtime driver by default. Multiple agents may drive the live app only when isolated users, resettable fixtures, disposable data, independent browser profiles, or read-only surfaces make the evidence safe and non-conflicting. Otherwise agents return path plans and evidence packets while the orchestrator or one designated runtime lane performs coordinated clicking.

## Full-Blast Wave Contract

Full blast requires a minimum of three verified waves after Wave 0 preflight: broad reconnaissance, targeted deep dive, and release-gate / what-did-we-miss. This is a minimum of three verified waves, not a maximum. Every wave summary requires the Deep Review read-all, evidence-state, independent-verifier, verification-certificate, and drift-check gate.

Use adaptive continuation after Wave 3 when coverage is not closed. Continue with additional waves when major route families, user roles, state variants, runtime proof, contradictions, high-severity disconfirmation, safe path attempts, or evidence debt remain unresolved, or when the verifier objects that coverage is too thin. Do not end a full blast because three waves happened; end only when the coverage matrix and evidence debt justify the final scope and verdict.

Path-universe closure is mandatory. Every material expected intent and discovered path must be labeled covered, sampled with justification, blocked, avoided, inferred, missing, out_of_scope, or evidence_debt before final readiness language is written. Treat all safe discoverable paths as the coverage ambition; do not substitute a few happy paths, top tasks, or agent consensus.

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
3. Route `ship-product-workflows` as `major` for broad readiness, defaulting to `audit_all` plus `audit_top_tasks` plus `audit_high_risk`. Downshift only when the user explicitly asks for a rapid/narrow pass, the target is genuinely small/static-only, or safe-test boundaries make full coverage impossible. If `audit_all` is not feasible, still map the whole discovered path universe and label every path covered, sampled, blocked, avoided, inferred, missing, out_of_scope, or evidence_debt. For a delta / in-session re-audit ("is my change ready?"), run changed-scope mode per `references/changed-scope.md`: scope to the changed surface plus its blast radius, mark untouched paths `out_of_scope`, and keep the verdict scoped to the change rather than the whole product.
4. Read `references/evidence-state.md` and initialize the canonical evidence state before lane roster, dispatch, path testing, or summaries. Record target fingerprint, safe-test boundary, ledger location or inline-ledger plan, first evidence debt rows, and initial claim/coverage/debt table headers.
5. Read `references/lane-prompts.md` and build a concrete lane roster before dispatch: product/runtime path QA, workflow clarity/design critique, release/deploy gates, accessibility/responsive smoke, data/state/persistence, role/permission, and verifier lanes as applicable. Keep scopes independent and non-overlapping. Write the roster to the ledger.
6. Launch the first wave of specialist agents according to the Full-Blast Agent Rules. Give every lane the target fingerprint, safe-test boundary, evidence-state contract, required sub-skill body to read, exact scope, excluded scope, output packet format, and proof limits. If agents cannot be launched, record why and run the same lane roster sequentially.
7. Discover and map the bounded path universe before judging quality: reasonable user intents, surfaces, actors, roles, states, entry points, actions, hidden paths, variants, integrations, data states, devices, and mutation risks. Treat "try every single path" as a command to pursue every safe discoverable path inside the declared boundary, and to flag expected user goals with no discoverable UX path, with honest exclusions and evidence debt for anything unsafe, unavailable, duplicate, static-only, blocked, or infeasible. Write expected intents and path-universe rows to the ledger. When the target matches a known archetype, load `profiles/<archetype>.json` per `references/archetype-overlays.md` and add its expected intents and frequently-missing paths as provenance-tagged hypotheses in the path universe — priors to confirm or disprove with evidence, never a checklist and never marked covered without proof.
8. Execute every safely testable discovered path inside the declared boundary. Try happy paths, empty states, loading states, invalid inputs, error states, recovery paths, navigation variants, role/permission variants, responsive/mobile variants, persistence/reload points, and reasonable edge cases. Stop at unsafe, paid, destructive, privacy-sensitive, production, or irreversible actions unless the user authorized that exact action and a reset/disposable environment exists. Write each path attempt, trace, result, label, and artifact reference to the ledger immediately after observation.
9. For every material user goal, assess path existence and path effort: whether a path exists, where it starts, how many steps and decisions it requires, whether it has detours, repeats, context switches, hidden prerequisites, waiting states, unclear labels, dead ends, or recovery burden. Flag paths that technically work but are unreasonably long, fragile, buried, or cognitively expensive. Write missing-path and overcomplicated-path findings to the ledger.
10. Maintain one shared evidence state: claim ledger, coverage matrix, evidence debt register, product coverage map, path traces, path-effort notes, evidence inventory, provenance tags, clarity lane packets, false positives, rejected claims, blocked checks, avoided checks, missing paths, and untested paths. Every material path or expected intent must have a status label: covered, sampled, blocked, avoided, inferred, missing, out_of_scope, or evidence_debt.
11. If the available evidence is static only, such as screenshots, README, docs, package scripts, or source snippets with no runnable runtime, route as a static constrained pass. Keep runtime behavior, persistence, accessibility, deployability, and path completion claims provisional, blocked, inferred, missing, or evidence debt unless directly proven.
12. Pass product path evidence, missing-path candidates, and path-effort notes to `ship-workflow-clarity`; ask it for compact lane packets, not a competing full ledger. Clarity/design critique happens after path discovery and initial product evidence, and must tie visual or attention critiques to workflow consequence.
13. At the end of every wave, read every expected lane output in full, merge normalized lane packets into the ledger, then run an independent verifier against the raw outputs and ledger. Do not write a wave intelligence summary until the verifier explicitly approves summary-writing.
14. Retarget each later wave from verified findings, contradictions, coverage gaps, missing expected paths, overcomplicated paths, and evidence debt, not from the original lane split.
15. Run a fix-cascade check on major recommendations: compare against the no-change baseline, identify what the fix could break downstream, and preserve proof, governance, recovery, accessibility, expert controls, and necessary friction. Write fix-cascade notes to the ledger.
16. Before final synthesis, run a final no-overclaim verifier against the final claim ledger, evidence debt, coverage gaps, and readiness language. Downgrade claims such as ready, works, accessible, robust, secure, deployable, beloved, viral, or complete unless directly supported.
17. Generate the mandatory HTML report from the final ledger for full Shipworthy invocations. Default to `~/.shipworthy/runs/<target-slug>/<timestamp>/readiness-report.html` so the audited repo stays read-only. Use repo-local `.shipworthy/reports/<timestamp>/` only when the user explicitly requests repo artifacts.
18. Write the final report only after the final claim ledger, evidence debt, coverage gaps, verified wave summaries, verifier outputs, fix-cascade notes, final drift check, and mandatory HTML report path are complete.

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
- Read `references/evidence-state.md` before creating ledgers, coverage matrices, path labels, severity/confidence normalization, evidence debt, evidence storage, or readiness claims.
- Read `references/final-report-contract.md` before writing the final report or roadmap.
- Read `references/archetype-overlays.md` when the target matches a known product archetype (checkout, auth, ai-chat, dashboard, …). The `profiles/*.json` seed path discovery with priors — expected intents, common failure modes, and frequently-missing paths — as **hypotheses to confirm or disprove with evidence, never a pass/fail checklist**.
- Read `references/changed-scope.md` for a delta / in-session re-audit ("is my change ready?"): scope to the changed surface **plus its blast radius**, label untouched paths `out_of_scope`, and return a verdict scoped to the change — not the whole product.
- Read `references/visual-html-report.md` for every full Shipworthy invocation and whenever the user wants a shareable visual report. It documents the mandatory HTML dashboard, `scripts/render_report.py`, and the JSON contract.
- Read `references/exports-and-ci.md` when the user wants to share, archive, gate, or automate: the mandatory HTML render for full runs, the SARIF export (`scripts/to_sarif.py`), the tamper-evident evidence bundle (`scripts/make_bundle.py`), the confirmed-only merge gate, the opt-in `--interactive` report, and the optional GitHub code-scanning recipe. All local-first; all renders of the finished ledger.
- Read `references/pressure-tests.md` when validating or forward-testing this skill, or when the user asks whether the orchestration is strong enough.

## Output Contract

Lead with findings and readiness truth. Separate confirmed findings, strong findings, provisional hypotheses, needs-proof items, blocked checks, avoided checks, false positives, rejected claims, and untested paths. Do not claim ready, safe, correct, accessible, persistent, secure, beloved, viral, passing, or fixed without evidence.

For full-blast runs, include an **Orchestration Checkpoint** in the report: skill bodies read, references read, target fingerprint, safe-test boundary, ledger location or inline snapshot, actual agent/tool execution mode, runtime driver mode, verifier status, omitted gates, mandatory HTML report path, and where raw outputs/evidence live. Under that checkpoint, include a lane roster table with one row per planned lane and columns for lane, scope, required skill/reference, execution status, output/evidence location, and skipped/collapsed/blocking reason. If the checkpoint, roster table, path-universe closure, verifier certificates, or HTML report path is missing, the report is not complete.

For each finding include evidence, user consequence, likely cause, smallest useful fix, counterfactual/no-change baseline when relevant, downstream regression or simplification risk, and exact verification step. For full runs, include a coverage table for every discovered material path and expected user intent, including paths covered, sampled, blocked, avoided, inferred, missing, out of scope, and still carrying evidence debt.

Do not implement fixes unless the user explicitly asks for implementation after the review.

**Ledger-derived deliverables (local-first; never a second source of truth).** The inline report and self-contained **HTML report** (`scripts/render_report.py`; verdict, covered-%, severity-grouped findings, checkpoint) are required for full Shipworthy invocations and are generated only after the ledger is final. The HTML report defaults to no JS; `--interactive` is an opt-in variant that adds client-side filter/search/collapse. Additional optional exports, when the user wants to share, archive, gate, or automate, are:
- a **SARIF 2.1.0** file (`scripts/to_sarif.py`) for GitHub code scanning, with an optional **merge gate** (`--gate`) that fails on confirmed blockers only;
- a tamper-evident **evidence bundle** (`scripts/make_bundle.py`; ledger + report + SARIF + a SHA-256 manifest) for a defensible audit trail — see `references/exports-and-ci.md`.
The ledger JSON is itself the canonical machine-readable export.

## Common Failure Modes

- Letting `ship-product-workflows` or `ship-workflow-clarity` become peer controllers with separate final readiness conclusions.
- Naming `ship-deep-review`, `ship-product-workflows`, or `ship-workflow-clarity` without reading their full `SKILL.md` bodies first.
- Skipping the lane roster or under-launching agents during a full-blast run when independent agent tooling is available.
- Delaying ledger creation until the end, treating the final prose as the ledger, or letting lane agents create competing ledgers.
- Omitting the Orchestration Checkpoint from the final report, leaving agent/sequential fallback, lane roster, or verifier status invisible.
- Starting with visual judgment before workflow cartography.
- Defaulting to top-task/high-risk sampling when the user invoked this skill for a full readiness run.
- Treating "try every path" as omniscience instead of coverage mapping, actual safe execution, labels, and exclusions.
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

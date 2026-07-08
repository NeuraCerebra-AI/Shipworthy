# Agent And Tool Orchestration

## Table Of Contents

- Purpose
- Coordinator Dependency Order
- Should This Skill Call Agents?
- Agent Runtime Profiles
- Suggested Audit Lanes
- Wave Patterns
- Playwright Routing
- Computer Use Routing
- Tool And Agent Evidence Rules
- Prompt Skeletons

## Purpose

Use parallel agents, staged waves, Playwright, and Computer Use to improve evidence coverage for major human-obviousness audits without turning every small audit into an orchestration project. This reference is runtime-aware: use the tools actually available in the current Codex or Claude environment.

## Coordinator Dependency Order

Before dispatching agents or starting tool-heavy waves, the coordinator should have already read the major-route core pack from `SKILL.md`: workflow cartography, audit mode, evidence/severity/assumptions, this orchestration reference, and the diagnostic rubric. This prevents lanes from using incompatible scope, confidence, severity, or recommendation standards.

Treat process route, audit mode, evidence path, and risk gate as separate decisions. A major route may still use `audit_selected`; a tiny route may still be `audit_high_risk` if the selected action is destructive.

Do not send every reference to every lane. Give each lane the shared cartography/mode/evidence rules plus only the lane-specific reference it needs. Later waves inherit evidence packets instead of re-reading the whole skill surface unless they find a conflict.

## Should This Skill Call Agents?

Yes for major work when the runtime and user instructions permit subagents. Examples:

- broad app or repo audits;
- `audit_all` across many routes or screens;
- `audit_changed_only` where changed components affect multiple workflows;
- high-risk governance, payment, privacy, approval, publish, AI-to-action, or destructive flows;
- audits that need desktop plus mobile plus accessibility plus copy plus code evidence;
- validation passes where independent critique is valuable.

No for narrow work unless delegation clearly helps. Examples:

- one screenshot;
- one small component;
- a short copy review;
- a single known workflow with enough evidence already present.

If subagents are not available or not allowed, write an agent-lane plan and proceed single-agent. Do not pretend parallel validation happened.

## Agent Runtime Profiles

Use the user's runtime norms when they are available:

- Codex macOS/Codex app: maximum practical concurrency is 6 agents. For major tasks, use up to 6 specialist agents when the lanes are independent and use `gpt-5.5` with `xhigh` reasoning when model/effort controls exist. For smaller delegated tasks, use `gpt-5.5` with medium reasoning unless the user asks otherwise.
- Claude Code or Claude macOS: parallelism is much higher, but use 10 concurrent agents as the normal practical cap unless the user explicitly asks for more. Use Sonnet for most lanes; use Opus for major synthesis, adversarial review, or high-stakes lanes.

Respect the active tool policy. Some runtimes require explicit user authorization before spawning agents. If the tool contract says not to spawn without an explicit user request, ask or provide the lane plan instead.

Close or archive completed agents when the runtime requires it so completed agents do not occupy concurrency slots.

## Suggested Audit Lanes

For a major audit, split lanes so outputs are independent:

- Cartography lane: routes/screens/states/actions/hidden paths/mutation risks.
- Runtime evidence lane: Playwright or equivalent browser trace, screenshots, DOM/UI tree, console/network, responsive captures.
- Accessibility lane: keyboard/focus, semantic names, headings, status/error states, zoom/reflow.
- Copy and comprehension lane: labels, instructions, jargon, consequence wording, action/object/scope clarity.
- High-risk/trust lane: proof, provenance, confidence, role responsibility, review/publish/apply/payment/destructive friction.
- Code/change lane: changed files/components/routes, shared UI primitives, state machines, feature flags, adjacent workflow blast radius.
- Archetype lane: dashboard/form/AI/governance/expert/mobile/game/native/CLI collision rules.
- Adversarial reviewer lane: challenge findings, spot unsupported assumptions, detect harmful simplification.

In Codex, pick up to 6 specialist lanes for the task while the main agent coordinates, inspects critical evidence, and synthesizes. In Claude environments where 10 agents are reasonable, include more lanes or split desktop/mobile/accessibility/code into separate agents.

## Wave Patterns

Use waves when one round's evidence should inform the next:

- Wave 0: coordinator reads prompt, constraints, app/repo entry points, safe-test rules, and decides lanes.
- Wave 1: discovery/cartography/evidence collection. Do not make final recommendations yet.
- Wave 2: focused analysis by workflow or archetype, using Wave 1 maps and artifacts.
- Wave 3: adversarial validation, contradiction search, accessibility/trust regression checks, and "what would this fix break?"
- Wave 4: synthesis, deduplication, severity normalization, and final report.

For small audits, collapse waves into one pass. For large audits, keep wave outputs short and evidence-indexed so later waves inherit rather than re-derive.

Use a second wave when:

- Wave 1 finds hidden states, permissions, or mutations;
- high-risk actions require consequence/recovery validation;
- evidence conflicts across screenshot, DOM/UI tree, trace, or code;
- an initial recommendation might hide proof, governance, expert controls, or accessibility.

## Playwright Routing

Use Playwright or equivalent browser automation for web and browser-hosted prototypes when it can safely capture:

- screenshots across desktop/mobile viewports;
- DOM and accessibility snapshots;
- focus traversal;
- route and link reachability;
- console errors;
- network/API observations where safe;
- before/after workflow traces;
- responsive and zoom/reflow behavior.

Prefer Playwright for deterministic browser evidence. Do not use it to click paid, destructive, permission-changing, privacy-sensitive, publishing, approval, or production mutations without explicit safe-test permission.

## Computer Use Routing

Use Computer Use when browser automation is insufficient or the task depends on a real desktop UI:

- Codex macOS app or Claude macOS app inspection;
- native macOS, Electron, desktop, game, or creative tools;
- logged-in Chrome/desktop state that cannot be reproduced in a clean browser context;
- visual menus, windows, panels, keyboard shortcuts, dialogs, drag/drop, or OS permission flows;
- Claude macOS and Codex macOS workflows where Computer Use can see and operate the actual app surface.

Computer Use evidence should be captured as screenshots, step traces, observed state transitions, and manual notes. Treat it as strong user-visible evidence when paired with a reproducible trace or secondary artifact.

## Tool And Agent Evidence Rules

- Every agent lane must report artifacts, paths, commands, screenshots, traces, or exact observations.
- Every lane must label untested states and avoided mutations.
- The coordinator must deduplicate findings and normalize severity/confidence.
- Do not let agent consensus replace evidence. Five agents repeating a screenshot-only claim still leaves it screenshot-only.
- Do not let Playwright or Computer Use traces replace comprehension analysis. They prove what appeared and what happened, not automatically what users understood.
- Keep raw lane outputs separate from final findings when possible so unsupported claims can be traced and rejected.

## Prompt Skeletons

Codex major audit lane:

```text
Use $ship-workflow-clarity at /path/to/ship-workflow-clarity.
You are one lane in a parallel audit. Inspect only: [lane scope].
Use evidence only. Do not click medium/high mutation actions.
Return: workflow areas covered, artifacts/paths, confirmed findings, hypotheses, exclusions, and what a fix could break.
Preferred runtime when available: gpt-5.5, xhigh for major audit lanes; medium for smaller lanes.
```

Claude major audit lane:

```text
Use $ship-workflow-clarity at /path/to/ship-workflow-clarity.
You are one lane in a parallel audit. Inspect only: [lane scope].
Use Sonnet for normal lanes; use Opus only for major synthesis/adversarial review/high-stakes judgment.
Use Computer Use and Playwright if available and appropriate to collect runtime-visible evidence.
Return evidence-indexed findings, hypotheses, exclusions, and regression risks.
```

Wave handoff:

```text
Use the Wave [N-1] evidence packet below. Do not re-derive cartography unless you find a conflict.
Your job is [analysis/validation/synthesis lane].
Tag every finding as Confirmed, Strong, Provisional, Hypothesis, or Not tested.
```

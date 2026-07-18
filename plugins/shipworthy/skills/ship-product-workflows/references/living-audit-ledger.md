# Living Audit Ledger

## Table Of Contents

- Purpose
- When To Create One
- Where To Put It
- Anti-Anchoring Rules
- Creation Timing
- Update Cadence
- Required Sections
- Agent And Wave Packets
- Clarity Lane Packets
- Resume State

## Purpose

Use a living audit ledger when a product workflow audit may outlive a single response, involve agents or waves, or risk losing state to compaction. The ledger is a flight recorder for evolving audit truth: what was discovered, tried, avoided, blocked, suspected, verified, and left for the next pass.

The ledger is not a contract that freezes scope. It should help the auditor find more paths, not make the first map feel final.

## When To Create One

Maintain a ledger for:

- `major` route audits;
- full-pass or "try every meaningful path" requests;
- long-running audits likely to span compaction;
- agent-assisted or wave-based audits;
- Playwright-heavy, browser-heavy, Computer Use-heavy, or native-app audits with many traces;
- high-risk product workflows where safe-test decisions and avoided actions need durable tracking;
- audits where the user explicitly asks for a durable record.

For `quick` audits, do not create a full ledger unless the user asks. For `standard`, create one only when durability, agents, waves, or compaction risk make it useful.

If file writes are not allowed, not useful, or would surprise the user, keep the ledger as a clearly labeled section in the response and provide a proposed path for a future artifact.

## Where To Put It

Choose the least surprising durable location when writing a ledger file:

- use the user-specified path if provided;
- use a repo-local audit or docs area only when the target repo is clearly in scope, writing audit deliverables there is expected, and the contents are safe to store, such as `docs/audits/`;
- otherwise use `/tmp/ship-product-workflows/<timestamp>-audit-ledger.md`.

Do not write secrets, private customer payloads, tokens, credentials, raw production records, or irreversible-action details into the ledger unless the user explicitly permits that storage. Prefer evidence references, redacted snippets, local artifact paths, run ids, screenshots, trace filenames, or summaries.

## Anti-Anchoring Rules

The ledger must prevent compaction forgetfulness without over-constraining discovery:

- label the first scope and coverage map as provisional;
- do not finalize the path universe until after the first discovery/cartography pass;
- append newly discovered routes, states, roles, and hidden paths to `New Paths Discovered`;
- put possible expansions in `Scope Expansion Candidates` before deciding whether to test, avoid, defer, or exclude them;
- keep `Blocked`, `Avoided`, `Inferred`, and `Out of scope` separate;
- do not treat a new path as scope creep until it has been triaged against user intent, risk, and available evidence;
- preserve contradicted or superseded notes with a short correction rather than silently deleting them.

## Creation Timing

For ledger-required audits:

1. Start with a minimal provisional ledger after initial route and safe-test boundary.
2. Mark the first scope as provisional and list initial unknowns.
3. Run discovery/cartography.
4. Update the ledger with discovered surfaces, paths, roles, states, variants, hidden paths, and mutation risks.
5. Finalize the working scope only after discovery, while keeping expansion candidates visible.

If a ledger requirement appears mid-audit, create it at the reroute point and include what is already known plus what remains untested.

Do not spend the first pass filling a large template before discovery. A thin opening ledger is enough: target, route, safe boundary, evidence available, unknowns, and next discovery action.

## Update Cadence

Update the ledger after:

- discovery/cartography;
- material evidence-changing tool batches, not every tiny click, screenshot, or command;
- each agent lane packet;
- each wave before starting the next wave;
- each reroute;
- each critical, high, or cross-cutting finding;
- each safe-test boundary change;
- final synthesis.

For long audits, update `Resume Here` before any likely interruption. The ledger should let a future agent continue without redoing solved orientation work.

Prefer concise deltas over rewriting the whole ledger. Preserve the latest useful state while avoiding a bloated transcript of every minor observation.

## Required Sections

A useful ledger includes:

- `Audit Identity`: audit name, target, route, mode, evidence path, and risk gate;
- `Safe-Test Boundary And Avoided Actions`: allowed, avoided, and authorization-gated actions;
- `Scope`: provisional scope, current working scope, and exclusions;
- `Initial Unknowns And Discovery Questions`: the questions that guide discovery;
- `Discovery And Cartography Inventory`: discovered surfaces, states, sources, and status;
- `New Paths Discovered`: paths found after the initial map;
- `Scope Expansion Candidates`: candidate additions and their disposition;
- `Coverage Map`: paths and their canonical coverage labels;
- `Execution Log`: material actions, results, evidence, and follow-up;
- `Findings Ledger`: findings, severity, confidence, status, and evidence;
- `Clarity Lane Packets`: clarity-lane scope, results, assumptions, and warnings;
- `Evidence Inventory`: artifacts, locations, provenance, confidence, and limitations;
- `Agent And Wave Packets`: lane or wave coverage, evidence, findings, and next paths;
- `Reroute Log`: routing changes, triggers, and consequences;
- `Assumptions And Open Questions`: unresolved assumptions, questions, and evidence needs;
- `Blocked Or Avoided Paths`: paths not exercised, reasons, and safe next steps;
- `Resume Here`: current state and the exact next action.

Use `templates/audit-ledger.md` when creating a reusable artifact. For a smaller ledger, keep the same section names but omit empty or irrelevant sections.

## Agent And Wave Packets

The coordinator owns the ledger. Agents should return packets that the coordinator can paste or merge.

Ask lanes to return:

- lane name and scope;
- paths covered, sampled, blocked, avoided, inferred, and out of scope;
- new paths or states discovered;
- artifacts and evidence references;
- findings with severity/confidence;
- contradictions or evidence conflicts;
- safe-test warnings;
- next recommended path.

Update the ledger after each wave before dispatching the next wave, so later lanes inherit the current map rather than rediscovering old terrain.

## Clarity Lane Packets

When `$ship-workflow-clarity` is called by this skill, ask it for a lane packet instead of a separate full ledger unless the user explicitly wants both.

The packet should include:

- path ids and role/state/device covered;
- clarity findings and non-findings;
- assumptions about user goals or comprehension;
- consequence/recovery/trust/governance concerns;
- harmful-simplification warnings;
- verification suggestions;
- any new hidden path, unclear state, or blocked evidence it discovered.

Store the packet under `Clarity Lane Packets` and merge only evidence-backed findings into the final report.

## Resume State

Keep `Resume Here` short and current:

- current route, audit mode, evidence path, and risk gate;
- current safe-test boundary;
- last completed action;
- next best action;
- active blockers;
- do-not-redo list;
- unmerged lane packets;
- highest-priority unverified findings;
- files, servers, URLs, fixtures, screenshots, traces, and commands needed next.

If the audit is paused, this section is the handoff.

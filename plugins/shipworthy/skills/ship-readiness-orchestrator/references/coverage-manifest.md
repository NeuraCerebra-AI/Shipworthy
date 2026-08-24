# Source-Backed Coverage Manifest

## Purpose

The canonical `path_frontier` is an executable work manifest, not an agent-authored summary. A full run must prove that the manifest was derived from independent product inventories and that every material inventory candidate was assigned, exercised when safe, or given an evidenced terminal disposition.

"Every path" means every material path that is discoverable within the declared target, roles, fixtures, states, viewports, input modes, integrations, safe-test boundary, and available authorized capabilities. Do not imply coverage of theoretical input combinations, inaccessible production-only state, or unauthorized actions.

## Mandatory Discovery Sequence

1. Freeze declared behavior candidates from product docs, contracts, stories, and expected human intents.
2. Freeze static implementation candidates from routes, components, controls, event handlers, command registrations, feature flags, guards, tests, fixtures, state machines, and API-backed user actions.
3. Freeze runtime structural candidates from the DOM, accessibility/UI tree, visible routes, deep links, controls, disabled controls, apparent affordances, keyboard paths, and every safely spawned menu, dialog, drawer, popover, palette, or nested surface.
4. Map each raw candidate to exactly one canonical frontier row or a retained reconciliation difference. Never derive a candidate inventory from frontier rows.
5. Assign every material frontier row to an owner lane before execution. Generate distinct rows for every materially different role, state, viewport, input mechanism, lifecycle boundary, and before/after transition.
6. Walk the actual frontend to a spawned-surface fixpoint: execute every safe material control, re-inventory after each state-changing action, and append newly exposed candidates before continuing.
7. Exercise the applicable lifecycle matrix: entry, valid success, invalid input, corrected retry, cancel/back/close, refresh or re-entry, stale/expired state, loading/error/retry, permission denial, and recovery.
8. Reconcile runtime, static, and declared inventories. Resolve every difference or retain it as explicit coverage debt.
9. Run two final negative-discovery passes from distinct canonical method families. Each pass must retain its source inventory and prove that no new raw candidate—not merely no new frontier key—was found.

## Candidate Inventory Contract

Every `candidate_inventory` records:

- a unique inventory ID and canonical method family;
- target role, state, viewport, fixture, and source-specific locator;
- retained raw source artifacts and SHA-256 digests;
- a canonical candidate-extract JSON artifact whose parsed candidates exactly equal the embedded inventory candidates; the manifest cannot serve as this artifact;
- raw candidates with stable candidate IDs, materiality, source locators, evidence references, proposed semantic keys, and exact frontier mappings;
- a digest computed from the full canonical candidate objects.

Every candidate cites at least one retained raw source artifact. Required method families cannot reuse the same raw source artifact as proof of independence. A runtime structural inventory records `action_signaling_candidate_count`, which must equal its control/transition candidate count. `apparent_affordance` is not a candidate kind: map a truly noninteractive affordance as a surface observation; map every action-signalling affordance to an exact runtime structural control/transition candidate and frontier row, count it in that runtime inventory, and require execution proof. A surface label cannot satisfy this rule.

Locators must be independent of the frontier: accessible name and role, DOM/UI-tree node, runtime route, keyboard registration, file and symbol, test/fixture identifier, or document heading. Copying frontier semantic keys into a "census" without retained raw locators is circular and cannot prove coverage.

For every current full run, including a constrained terminal report, the union of mapped source candidates must equal the canonical frontier; an unsourced frontier row is invalid. Closed multi-source coverage additionally requires `declared_behavior_inventory`, `runtime_structural_inventory`, and `static_implementation_inventory` with independent raw sources. Use `runtime_human_interaction` for actual execution.

## Work And Terminal Status

Canonical full-frontier statuses are:

- `covered` — directly executed or traced with sufficient evidence;
- `sampled_with_justification` — representative non-control variant only, with a written justification;
- `blocked` — unavailable after the bounded recovery ladder;
- `avoided` — intentionally not executed under the safe-test boundary;
- `missing` — a promised or reasonable material path is proven absent;
- `out_of_scope` — excluded by the declared user boundary;
- `evidence_debt` — the candidate is known but material proof remains unavailable;
- `unattempted`, `unknown`, or `maybe` — nonterminal work.

Do not use `sampled` or `inferred` in a full frontier. Inference is evidence debt until directly resolved. Every material row names `owner_lane`. Every terminal non-covered row carries `terminal_reason` and evidence; sampled rows also carry `sample_justification`.

## Completion, Coverage, And Readiness

Keep three axes independent:

- `audit_status` records operational lifecycle: `active`, `complete`, `blocked`, or `user_stopped`.
- `path_frontier.finality` records whether safe authorized work remains: `open` or `exhausted`. `exhausted` forbids nonterminal material rows; turn unavailable work into evidenced terminal dispositions. A user-stopped audit may remain `open` with named remaining work.
- `readiness_disposition` records the release decision: `ready`, `conditionally_ready`, `not_ready`, or `cannot_determine`.

An audit may be complete and `not_ready`. A proven missing path or failed tested behavior is a finding, not unfinished audit work. A blocked/user-stopped terminal report may retain blocked, avoided, or evidence-debt rows with a constrained disposition, but `audit_status: complete` requires closed coverage and no material debt.

Only `ready` or `conditionally_ready` requires every material row covered, closed multi-source coverage, exhausted finality, no material evidence debt, full frontend proof, approved verification, and every existing evidence gate. A confirmed approved P0 always yields `not_ready`, even when unrelated proof debt exists. A blocked or user-stopped audit without that confirmed P0 uses `cannot_determine`.

## Fixture Authorization

Reversible mutation is allowed only when the user's authorization covers the action and the supplied non-production fixture has a verified reset contract. A disposable fixture alone does not grant authorization. Payment, external messages, credentials, production mutation, destructive actions, publishing, approvals, and permission changes still require explicit action-level authority and a verified reset or sandbox boundary.

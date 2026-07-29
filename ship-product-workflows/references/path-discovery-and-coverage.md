# Path Discovery And Coverage

## Table Of Contents

- Purpose
- Coverage Principle
- Path Frontier For Full Shipworthy Runs
- Discovery Inventory
- Path Selection
- Coverage Labels
- Changed-Only Coverage
- Hidden And Variant Paths
- Coverage Map Requirements

## Purpose

Use this reference before auditing. A product workflow audit is only as strong as its map of what could be tried, what was tried, what was inferred, and what was avoided.

## Coverage Principle

Do not claim "all paths" unless the path universe is truly bounded and inspected. Prefer:

- "covered these paths";
- "sampled these variants";
- "blocked by missing access";
- "avoided because mutation risk";
- "not in scope";
- "next pass should cover."

The user may say "try every path." Interpret that as "build a serious coverage map and go as far as safe evidence permits."

When a living audit ledger exists, the first coverage map is provisional. Append newly discovered paths, states, roles, and hidden routes to the ledger before deciding whether they are in scope, out of scope, blocked, avoided, or deferred.

## Path Frontier For Full Shipworthy Runs

When this lane is running under `ship-readiness-orchestrator` for a full Shipworthy invocation, return additions to one canonical `path_frontier`, not just findings. Use stable rows with semantic lineage `intent → feature → surface → control → transition`. Use `shipworthy-semantic-v1` keys, and include role, state, viewport in each surface identity. A control identity contains its label or accessible name, control type, and behavior disambiguator; a transition contains `before_state` and `after_state`. Observations point to evidence and to the discovery pass that produced them.

Construct every semantic key mechanically after NFKC normalization: case-fold
each component, replace every non-alphanumeric run with one hyphen, trim outer
hyphens, and normalize routes to a lowercase leading-slash path without query,
fragment, duplicate slash, or trailing slash (except `/`). Use exactly:

- `intent:<role>:<goal>`;
- `feature:<feature>`;
- `surface:<route>:<state>:<role>:<viewport>`;
- `control:<parent-surface-key>:<name>:<control-type>:<behavior-disambiguator>`;
- `transition:<before-state>:<parent-control-key>:<after-state>`.

Dotted ad hoc IDs, prose slugs detached from their parent, and renamed aliases
are not semantic keys. A control key must be derived from its parent surface and
`control_identity`; a transition key must be derived from its parent control and
recorded states. Put display-friendly shorthand in prose, never in
`semantic_key` or `affected_semantic_keys`.

Do not collapse material variants into values such as `member/admin`,
`desktop/mobile`, or `normal/stale`. Create one surface row for each materially different role/state/viewport tuple,
then parent each control and transition to the exact surface variant where it exists. Reuse a feature parent where useful;
do not invent a second frontier merely to summarize variants.

Canonical surface states are behavioral, not prose synonyms: use `normal` for the default interactive state, then `empty`, `editing`, `draft`, `invalid`, or `stale` when that state materially changes the available behavior. For a material spawned overlay or subregion, use its normalized purpose such as `avatar-menu` or `upgrade-card`. Use the actual browser URL path, not an invented logical object route. The role axis carries `member` or `admin`; do not repeat the role as the state.

Use the exact accessible name in `control_identity.name` and therefore in the
key. The disambiguator describes behavior (`persist`, `visual-only`,
`open-dialog`, `download`, `disabled`), not DOM position. Do not use ordinal names such as `save-primary` or `first-save` when the observed behavior is
known. Use compact outcome states such as `created`, `published`, `restored`,
`not-persisted`, or `lost`, rather than copying a full toast sentence.

Set `material: false` only for a structural lineage/support row whose own
behavior could not independently change the readiness verdict. Navigation,
feature, and surface parents that exist only to connect a material descendant
may be nonmaterial; any risky, broken, missing, blocked, role/state-specific, or
user-consequential behavior remains material.

Use only the `shipworthy-methods-v1` canonical method families:

- `runtime_human_interaction`: adaptive interaction through the visible product;
- `runtime_structural_inventory`: an independent DOM, accessibility-tree, UI-tree, route, or equivalent runtime inventory;
- `static_implementation_inventory`: source, route, component, fixture, or test inventory;
- `declared_behavior_inventory`: product docs, contracts, stories, or declared promises.

A renamed method_detail does not create an independent method family. Reconcile runtime discovery against at least one independent canonical family at both feature and surface levels; preserve every discrepancy in `reconciliation_differences` until resolved or the run is downgraded. Runtime-only work may use two genuinely independent runtime families. Full-evidence work should reconcile runtime with static or declared behavior.

Closed multi-source exhaustion requires two qualifying zero-yield discovery passes from distinct canonical method families. Each pass records its family, role, fixture, viewport, starting and ending frontier digests, and new semantic keys. A pass qualifies only when it began from the current frontier, produced no new semantic keys, and did not merely relabel the same method.

Do not call the lane exhausted while material paths remain `unattempted`, `unknown`, or `maybe`, or while the last discovery/testing pass found new material routes, controls, roles, states, device variants, or user intents.

Before a zero-yield claim, open every safe control that can spawn a menu, dialog, drawer, palette, popover, or nested route and census the spawned surface. Test each material surface at every relevant supplied role and viewport; a mobile check of one representative screen does not prove a mobile-only control elsewhere. Trigger documented or discoverable keyboard commands, inventory visible unavailable capability or disabled feature flag messaging, and record a reload/re-entry proof as its own transition row whenever persistence is claimed or disproved.

Synthetic role selectors supplied by a bounded test fixture change fixture
state; they are not authentication or authorization boundaries unless the
target explicitly claims they are. Test their role-dependent surfaces without
inventing a security escalation finding. Real production role changes still
require the normal authorization and mutation safeguards.

When the supplied target is a resettable synthetic fixture and its controller
provides a working reset contract, use the supplied reset mechanism and treat
reversible local create, edit, validation-retry, publish, export, and download
behavior as safe to exercise. A download may be proven from the initiated
runtime response when reading the browser's default download directory would
cross the declared filesystem boundary. Continue to avoid any explicitly destructive, external-message, payment, credential, or production action. If
the reset contract is incomplete or fails, record the exact operational gap;
do not guess token placement and do not silently broaden access.

## Discovery Inventory

Map these before judging findings:

- product area, app type, platform, and launch path;
- roles, permissions, and actor types;
- routes, screens, windows, dialogs, panels, menus, tabs, overlays, and drawers;
- every visible or discoverable interactive control on each material role/state/device variant, including duplicate labels, nested menus, context menus, keyboard-only, mobile-only, and disabled controls;
- entry points and deep links;
- primary tasks and secondary tasks;
- success, empty, loading, error, disabled, unauthorized, stale, offline, pending, draft, dirty, conflict, and completed states;
- create/read/update/delete or equivalent object lifecycle;
- forms, uploads, imports, exports, search, filters, sorting, pagination, chat, AI handoffs, approvals, publish/apply actions, settings, notifications, and recovery paths;
- integrations, jobs, queues, webhooks, providers, data stores, and external dependencies visible to the user;
- mutation risks and reset plan.

For native or desktop surfaces, include windows, menu commands, toolbar actions, shortcuts, file dialogs, OS permissions, drag/drop, and app lifecycle states.

## Path Selection

Rank paths by:

- user frequency;
- user value;
- revenue or business impact;
- irreversible consequence;
- privacy/security/trust risk;
- new or changed code;
- shared component blast radius;
- support-ticket likelihood;
- accessibility dependence;
- unclear ownership or stale state.

For `audit_top_tasks`, cover the highest-value paths first.

For `audit_high_risk`, cover irreversible, governed, or trust-heavy paths first.

For `audit_all`, enumerate the full scoped path universe and path_frontier, then work in risk/value order and label what remains uncovered.

## Coverage Labels

Use these labels consistently:

- `covered`: executed or traced with sufficient evidence.
- `sampled`: checked one or more representative variants, not the full variant set.
- `blocked`: could not inspect because of missing access, setup, credentials, data, environment, or tool failure.
- `avoided`: intentionally not clicked due to mutation, privacy, payment, publishing, approval, production, or destructive risk.
- `inferred`: likely behavior based on code, docs, network contracts, or adjacent traces, but not directly observed.
- `missing`: a reasonable user goal or promised capability has no discoverable UX path.
- `out_of_scope`: excluded by user request, route, time, artifact, or risk boundary.
- `evidence_debt`: material proof is still required and no stronger label is justified.

Do not merge `blocked` and `avoided`. Blocked means unable. Avoided means intentionally not safe.

## Changed-Only Coverage

For `audit_changed_only`, map:

- changed files, routes, screens, components, commands, schemas, API contracts, feature flags, and styles;
- direct product paths using those changes;
- adjacent paths sharing the same component or state;
- old behavior needed for comparison;
- new behavior to verify;
- pre-existing debt that confounds the changed area.

If the changed artifact is a standalone fixture or pasted diff, do not silently expand into the current working repo. Use ambient repo evidence only when the prompt names that repo/product or when it is essential supporting context, and label it separately from the supplied change.

Label findings as:

- changed regression;
- changed improvement incomplete;
- adjacent regression;
- pre-existing issue;
- unrelated issue.

## Hidden And Variant Paths

Actively look for:

- role-specific paths;
- feature-flagged paths;
- mobile-only and desktop-only paths;
- keyboard-only paths;
- empty and first-run states;
- failure and retry states;
- interrupted flows;
- state restoration after refresh/back/close/reopen;
- partial-save or draft behavior;
- stale data, race, and conflict states;
- AI or automation handoffs;
- review, approval, and publish boundaries.

If a hidden path cannot be reached, list the condition required to test it.

## Coverage Map Requirements

A usable coverage map includes:

- path id;
- role;
- entry point;
- goal;
- current state;
- actions tested or traced;
- evidence artifacts;
- coverage label;
- mutation risk;
- result;
- linked findings;
- exclusions or next evidence needed.

Use `templates/coverage-map.json` when the map should survive beyond the response.

For major or long-running audits, mirror the coverage map into the living audit ledger so compaction does not erase what was already covered, sampled, blocked, avoided, inferred, or excluded.

For full Shipworthy runs, also mirror frontier burn-down: total frontier rows, covered, sampled, blocked, missing, evidence debt, unattempted, new paths found in the last pass, and new paths found in the previous pass.

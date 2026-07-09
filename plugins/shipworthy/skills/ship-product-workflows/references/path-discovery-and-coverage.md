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

When this lane is running under `ship-readiness-orchestrator` for a full Shipworthy invocation, return path_frontier additions, not just findings. Each addition should identify the expected intent, source, surface/route/control, role, state/device variant, mutation risk, current status, and next action. The orchestrator owns the canonical Path Frontier Ledger, but this lane must keep feeding it new paths until discovery dries up.

Do not call the lane exhausted while material paths remain `unattempted`, `unknown`, or `maybe`, or while the last discovery/testing pass found new material routes, controls, roles, states, device variants, or user intents.

## Discovery Inventory

Map these before judging findings:

- product area, app type, platform, and launch path;
- roles, permissions, and actor types;
- routes, screens, windows, dialogs, panels, menus, tabs, overlays, and drawers;
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

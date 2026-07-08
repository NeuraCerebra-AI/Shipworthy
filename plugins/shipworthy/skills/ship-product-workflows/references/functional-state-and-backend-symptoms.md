# Functional State And Backend Symptoms

## Table Of Contents

- Purpose
- Functional Checks
- State Checks
- Data And Persistence Checks
- Permission And Role Checks
- AI, Automation, And Job Checks
- Backend-Symptom Checks
- Likely Cause Labels

## Purpose

Use this reference to inspect whether product workflows actually work. The scope is user-visible function and backend symptoms that affect users, not an unconstrained backend audit.

## Functional Checks

Check the path mechanics:

- route opens and renders;
- primary call to action is reachable;
- links and navigation go to the expected place;
- forms accept valid input and reject invalid input with useful errors;
- cancel/back/close works without losing unexpected state;
- save/apply/submit produces visible result;
- search/filter/sort/pagination behave consistently;
- upload/import/export/download paths handle valid, invalid, empty, large, and unsupported inputs when in scope;
- modals, drawers, menus, panels, and popovers can be opened and dismissed;
- disabled actions explain why they are disabled;
- destructive or irreversible actions include appropriate friction;
- retry and recovery paths exist for failures.

## State Checks

Check important states:

- first-run or empty;
- normal loaded;
- loading/skeleton/progress;
- partial data;
- validation error;
- server error;
- unauthorized/forbidden;
- offline or network failure if relevant;
- stale data;
- dirty form;
- draft/saved/published/applied;
- pending job;
- conflict/concurrent edit;
- success confirmation;
- no-results;
- archived/deleted/restored.

State findings are often more important than happy-path findings because users discover broken systems under stress.

## Data And Persistence Checks

Where safe, verify:

- data survives refresh/reopen;
- UI reflects the saved object, not optimistic-only state;
- list/detail views agree;
- counters, badges, statuses, and timestamps update;
- imported/exported data matches what the UI promised;
- attachments/files remain reachable;
- cache invalidation is not misleading;
- multi-step workflows preserve prior inputs;
- object identity is clear when several similar objects exist.

If persistence cannot be tested safely, state the missing fixture or permission.

## Permission And Role Checks

Check:

- unauthenticated behavior;
- allowed role success;
- denied role failure message;
- hidden versus disabled controls;
- direct-link access;
- object-level authorization symptoms;
- role-switching or impersonation fixtures if provided;
- admin/owner/reviewer/member/viewer boundaries.

Do not treat "button hidden" as sufficient proof of authorization. Pair UI observations with API/log/code evidence when the risk is meaningful.

## AI, Automation, And Job Checks

For AI copilots, automation, scheduled jobs, imports, exports, and background processing, check:

- request starts;
- progress/status is visible;
- cancellation and retry semantics are clear;
- outputs are linked to source input;
- errors are recoverable;
- stale or partial results are labeled;
- user approval boundaries are preserved;
- generated output cannot silently publish, apply, email, delete, or mutate without appropriate confirmation;
- status in UI matches backend job/log state where safe to inspect.

Use `$ship-workflow-clarity` for proof, consequence, non-consequence, and trust clarity around AI-to-action handoffs.

## Backend-Symptom Checks

Inspect backend/API/data only to explain product symptoms:

- 4xx/5xx responses;
- request payload mismatch;
- response schema mismatch;
- stale cache;
- missing persistence;
- unauthorized access or false denial;
- job status drift;
- websocket or streaming failure;
- upload/download path break;
- external provider failure;
- database constraint surfaced as vague UI error;
- feature flag mismatch;
- environment variable or config mismatch affecting the path.

If the likely issue is deeper backend design, report it as a handoff rather than broadening the audit without permission.

## Likely Cause Labels

Use one or more labels:

- UI behavior;
- navigation;
- state management;
- persistence;
- data contract;
- API/backend symptom;
- authorization/permission;
- validation;
- async job/status;
- integration/provider;
- responsive layout;
- accessibility;
- workflow clarity;
- trust/governance;
- test fixture/environment;
- unknown pending evidence.

Labels help dedupe findings and route fixes to the right owner.

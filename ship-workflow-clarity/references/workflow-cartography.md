# Workflow Cartography

## Table Of Contents

- Purpose
- Discovery Inputs
- Inventory Fields
- Surface Discovery
- Actor Discovery
- State Discovery
- Action Discovery
- Hidden Paths And Variants
- Mutation Risk
- Audit Priority
- Exclusions

## Purpose

Build a lightweight map of what a user can possibly do before deciding what to audit. Cartography is not a full product spec; it is enough structure to prevent screenshot-only judgment, invented goals, and missed high-risk paths.

## Discovery Inputs

Capture these before judging the experience:

- Artifact type: web, mobile, desktop, native, game, prototype, design file, CLI-like UI, mixed, or unknown.
- Entry points: URL, command, executable, design link, screenshot packet, repo path, route list, or user-described flow.
- Safe-test constraints: disposable data, read-only areas, actions not to click, credentials, paid operations, privacy limits.
- User-stated scope: selected screens, changed files, top task, high-risk flow, full app, or unknown.
- Context evidence: product docs, code, analytics, support notes, user research, or no supporting context.

Proceed with bounded hypotheses when context is thin, but label what is unknown.

## Inventory Fields

Track:

- Surfaces: routes, screens, panels, tabs, drawers, modals, dialogs, overlays, command palettes, menus, empty shells, terminal prompts.
- Actors: anonymous, authenticated, owner, admin, member, approver, reviewer, support, auditor, buyer, operator, expert, novice, first-time, returning.
- States: loading, empty, partial, success, error, permission denied, offline, validation failure, dirty/unsaved, stale, conflict, archived, pending, long-running job, completed.
- Actions: navigate, reveal, search, filter, submit, create, edit, delete, export, invite, pay, publish, approve, reject, ask AI, simulate, inspect, recover, undo, retry.
- Hidden paths: deep links, role-only states, keyboard-only paths, feature-flagged states, settings, onboarding, recovery, error pages, admin-only controls.
- Variants: desktop, mobile, tablet, zoom/reflow, reduced motion, dark/light, locale, long text, high-density data, sparse data, touch, keyboard, controller.
- Mutation risks: destructive, irreversible, costly to reverse, paid, privacy-sensitive, permission-changing, publishing, AI-assisted, externally visible.

## Surface Discovery

Prefer direct exploration when safe:

- Use route maps, app navigation, menus, deep links, design frames, Storybook stories, component lists, screenshots, or recorded flows.
- For repositories, scan route directories, navigation components, router definitions, stories, tests, and feature flags.
- For native or game surfaces, inspect menus, settings, pause states, control maps, overlays, progression states, and error/recovery screens.
- For CLI-like tools, inspect commands, prompts, confirmations, output states, help, errors, and recovery paths.

Name surfaces not reached and why.

## Actor Discovery

Use roles and responsibilities instead of demographic personas unless the user provides research. Tag each actor source:

- `[USER-STATED]`
- `[DOC-SUPPORTED]`
- `[CODE-INFERRED]`
- `[SCREEN-INFERRED]`
- `[ANALYTICS-SUPPORTED]`
- `[UNVERIFIED]`
- `[CONFLICT]`

Distinguish buyer, admin, operator, reviewer, approver, collaborator, support, and end user. Distinguish novice, occasional, and expert use only when evidence supports it.

## State Discovery

Try to cover state transitions, not just steady-state screens. Important states include:

- first run and empty state;
- loading and long-running work;
- partial progress;
- validation failure;
- error and retry;
- permission denied;
- dirty or unsaved changes;
- stale or conflict state;
- success and confirmation;
- archived, completed, canceled, or reverted state.

If a state cannot be triggered safely, mark it as unverified rather than absent.

## Action Discovery

Inventory visible and semantic actions:

- visible label and accessible name;
- action type;
- object affected;
- expected consequence;
- reversibility;
- keyboard or non-pointer reachability;
- proximity to affected object or proof;
- confirmation, preview, undo, retry, or cancel affordance.

Watch for status elements styled like actions, repeated labels with different outcomes, and different labels for the same outcome.

## Hidden Paths And Variants

Actively look for paths that visible first screens often hide:

- keyboard-only and screen-reader paths;
- mobile nav and overflow menus;
- deep links and dynamic routes;
- settings and notification paths;
- onboarding and recovery;
- admin or permissioned workflows;
- empty, error, and edge data states;
- locale, long text, zoom, reduced motion, and no-hover behavior.

Do not claim a path is absent unless the surface map, runtime exploration, and supporting code or docs make that claim safe.

## Mutation Risk

Before interacting, classify each action:

- `none`: navigation, reveal, local-only inspection.
- `low`: reversible preference or local draft change.
- `medium`: persisted mutation, external request, invite, export, AI-generated action handoff.
- `high`: delete, publish, pay, approve, reject, permission change, privacy exposure, irreversible submission, production operation.

Stop before medium or high mutation unless the user approved the test boundary or the environment is disposable.

## Audit Priority

Prioritize workflows by:

- user-stated importance;
- critical task completion;
- frequency or reach, if supported;
- mutation risk;
- accessibility impact;
- trust, proof, or governance stakes;
- recovery difficulty;
- recent code or design change;
- visible confusion or contradiction.

When no priority evidence exists, default to high-risk and likely top-task paths, and say the ranking is provisional.

## Exclusions

For every audit, list:

- surfaces not reached;
- roles not tested;
- states not reproduced;
- devices or variants not checked;
- actions avoided for safety;
- assumptions that would change the result.

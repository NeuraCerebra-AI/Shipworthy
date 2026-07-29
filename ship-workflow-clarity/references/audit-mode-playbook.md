# Audit Mode Playbook

## Table Of Contents

- Purpose
- Default Mode
- `audit_all`
- `audit_selected`
- `audit_top_tasks`
- `audit_high_risk`
- `audit_changed_only`
- Mode Switching
- Mode Evidence Limits

## Purpose

Choose audit depth without inventing product goals. The mode controls what gets inspected, not the severity model or the evidence standard.

Always name:

- selected mode;
- mode rationale;
- included workflows;
- excluded workflows;
- evidence limits.

## Default Mode

If the user does not choose a mode, run a scoped `audit_high_risk` plus `audit_top_tasks` pass. Say the top-task ranking is provisional unless supported by user statements, analytics, support data, product docs, or obvious first-run navigation.

Do not imply full-app coverage from the default pass.

## `audit_all`

Use when:

- the app or artifact is small enough to cover;
- the user explicitly asks for a whole-surface audit;
- a release or handoff needs broad workflow inventory.

Minimum work:

- discover all reachable surfaces;
- sample core states for each major workflow;
- identify untested actors, variants, and mutation paths;
- report findings by workflow priority, not by route order.

Avoid exhaustive perfectionism. Name what remains untested.

## `audit_selected`

Use when the user names screens, flows, artifacts, screenshots, tickets, or components.

Minimum work:

- map selected surfaces plus adjacent entry/exit points;
- list relevant actors, states, and risky actions;
- avoid claims about unselected areas except as adjacent-risk hypotheses;
- ask only for missing inputs that block a meaningful audit.

## `audit_top_tasks`

Use when the goal is likely user success on common or important tasks.

Rank top tasks from evidence:

- user-stated task;
- visible primary navigation or onboarding;
- analytics, support logs, research, or docs;
- code-inferred primary flows;
- screen-inferred first-run paths.

Tag each task source. Do not invent frequency. If evidence is thin, use "likely top task" and explain what would verify it.

## `audit_high_risk`

Use when workflows include:

- deletion, irreversible save, publish, approval, rejection, payment, invite, permission change, privacy exposure, legal/medical/financial submission, production operation, AI-to-action handoff, or externally visible export.

Minimum work:

- verify consequence clarity;
- inspect confirmation, preview, undo, cancel, retry, and audit paths;
- check role/state clarity;
- preserve productive friction where it protects users or institutions;
- recommend `Add Friction` or `Preserve` as readily as `Simplify`.

## `audit_changed_only`

Use when auditing a diff, PR, changed files, or recent design/code changes.

Minimum work:

- identify changed routes, screens, components, command paths, copy, state machines, data contracts, and shared UI primitives;
- map changed artifacts to user-visible workflows;
- inspect adjacent states likely affected by shared components, not only files named in the diff;
- separate changed-surface findings from pre-existing findings;
- avoid "unaffected" claims unless the route/component graph and runtime check support them;
- run or request runtime checks when static diff evidence cannot prove human-visible behavior.

For repositories, changed-only is not code review by another name. Keep findings tied to user comprehension, workflow state, accessibility, trust, or ease of use.

## Mode Switching

Switch or expand modes when evidence shows the initial mode is too narrow:

- a selected flow exposes a high-risk mutation;
- a changed component is shared across many workflows;
- a top task depends on hidden settings, onboarding, permissions, or recovery;
- accessibility or state evidence contradicts the visible screenshot.

Name the switch and why it is necessary.

## Mode Evidence Limits

Do not let the mode overstate certainty:

- `audit_all` can still have untested roles and states.
- `audit_selected` does not validate the rest of the product.
- `audit_top_tasks` needs task-source tags.
- `audit_high_risk` may leave low-risk usability issues untouched.
- `audit_changed_only` may miss pre-existing workflow debt.

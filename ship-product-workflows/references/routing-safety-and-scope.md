# Routing, Safety, And Scope

## Table Of Contents

- Purpose
- Product Workflow Scope
- Route Definitions
- Audit Modes
- Evidence Paths
- Risk Gates
- Safe-Test Boundary
- Wrong-Route Recovery
- Non-Goals

## Purpose

Use this reference to decide what kind of audit is being run, what evidence can be collected safely, and what is explicitly out of scope. The goal is enough operational rigor to let the audit go run, without pretending every product question is the same kind of test.

## Product Workflow Scope

This skill covers user-facing workflow quality: navigation, interaction, state, persistence, error handling, responsive behavior, accessibility smoke, permission behavior, data/API symptoms, and workflow clarity.

It does not replace:

- security scans;
- deep backend architecture review;
- load/performance testing;
- pure visual design critique;
- pure WCAG compliance audit;
- isolated code review;
- scraping or browser automation without product audit intent.

Code, logs, network traffic, and data checks are supporting evidence when they explain user-visible behavior. If the user asks for deep backend correctness, route to the appropriate engineering, testing, security, or architecture workflow instead.

For fixture-only, screenshot-only, or supplied-diff-only audits, keep the supplied artifact as the evidence boundary. Do not inspect or cite the ambient workspace unless the user explicitly named it, the prompt identifies it as the target product, or the adjacent context is necessary to prevent a false recommendation. When ambient context is used, label it separately as supporting context.

## Route Definitions

`quick`:

- One screen, one small flow, one screenshot, one small diff, or one known issue.
- Use when a compact answer is more useful than a full audit package.
- Cap normal output at the top 1-3 findings plus brief scope, coverage, assumptions, and verification. Do not produce full templates, lane plans, or broad path maps unless the route escalates.
- Escalate if the path has hidden states, data dependencies, medium/high mutation risk, or multiple actors.

`standard`:

- One product area, feature, workflow family, or changed product surface.
- Use path discovery and runtime evidence when possible.
- Include a coverage map, findings, exclusions, and verification.

`major`:

- Broad app, multi-role, multi-surface, release-readiness, high-stakes, or agent/tool-heavy audit.
- Use waves or parallel lanes when available and useful.
- The coordinator owns safe-test boundaries, evidence standards, deduplication, severity, and final recommendations.

`skill_validation`:

- Testing this skill itself.
- Use only when the artifact under review is `ship-product-workflows` behavior, trigger quality, outputs, references, templates, or forward-test performance.

## Audit Modes

`audit_all` means all discoverable product-workflow surface in the agreed scope, not every theoretical state in the universe. Always report coverage limits.

`audit_selected` means user-selected screens, routes, roles, or paths.

`audit_top_tasks` means likely frequent, critical, revenue-driving, support-driving, or user-value-driving paths.

`audit_high_risk` means money, privacy, security, destructive, publishing, approval, permission, compliance, AI-to-action, trust, or governance paths.

`audit_changed_only` means changed routes/components/screens/flows plus adjacent paths likely affected by the change. Do not ignore pre-existing debt if it blocks judging the change; label it separately.

If the user does not pick a mode, default to scoped `audit_top_tasks` plus `audit_high_risk`.

## Evidence Paths

Screenshot/static:

- Good for visual state, labels, layout, obvious affordance problems, and bounded hypotheses.
- Weak for behavior, focus, persistence, accessibility semantics, hidden paths, and API truth.

Repo/diff:

- Good for changed-only audits, route maps, component blast radius, state machines, feature flags, and likely backend/API contracts.
- Weak if not paired with runtime evidence for user-visible behavior.

Browser/runtime:

- Good for web apps, prototypes, console/network capture, DOM/accessibility snapshots, responsive checks, route reachability, and repeatable path traces.

Native/desktop:

- Good for Mac apps, Electron, desktop tools, menus, dialogs, OS permission flows, drag/drop, keyboard shortcuts, and workflows that require actual app state.

Logs/API:

- Good for explaining visible failures, persistence mismatch, job/status drift, authorization behavior, or stale data.
- Weak for proving whether a user can understand what happened.

Mixed:

- Preferred for standard and major audits.

## Risk Gates

None:

- Static artifacts, disposable fixtures, mock data, or read-only paths.

Low:

- Reversible local state, navigation, filters, safe text input, non-persistent interactions.

Medium:

- Persistent edits in disposable or local environments, test-account actions, reversible mutations, imports/exports, role changes in fixtures.

High:

- Production data, payments, publishing, approval, deletion, permission changes, privacy-sensitive access, emails/messages to real people, irreversible workflows, external providers, or any action with real-world side effects.

## Safe-Test Boundary

Before interacting with an app, identify:

- environment: local, staging, disposable fixture, production, unknown;
- account and role;
- seed data and reset plan;
- actions allowed;
- actions avoided;
- whether screenshots/logs/network payloads may contain private data;
- stop conditions.

Do not click high-risk actions without explicit permission and a safe fixture. If permission is unclear, trace up to the confirmation boundary, inspect code/logs where safe, and mark the action as avoided.

## Wrong-Route Recovery

If the provisional route is wrong:

1. State the mismatch.
2. Load the missing reference.
3. Revise coverage and scope.
4. Relabel findings affected by weak evidence.
5. Disclose avoided or untested paths.
6. Continue under the corrected route.

One reroute is normal. A second reroute needs materially new evidence.

## Non-Goals

Do not turn a product workflow audit into:

- a broad codebase refactor;
- an exhaustive security assessment;
- a backend architecture rewrite;
- a visual-polish mood board;
- a theoretical UX essay;
- an unbounded attempt to click every production path.

Escalate or hand off those tasks explicitly when the user asks for them.

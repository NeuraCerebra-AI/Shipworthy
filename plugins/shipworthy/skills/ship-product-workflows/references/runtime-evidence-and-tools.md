# Runtime Evidence And Tools

## Table Of Contents

- Purpose
- Evidence Strength
- Browser And Playwright Routing
- Computer Use Routing
- Repo, Diff, Logs, And API Evidence
- Responsive And Accessibility Smoke
- Tool Safety
- Evidence Packet

## Purpose

Use this reference when an audit needs live or semi-live evidence. Runtime evidence proves what appeared and what happened. It does not automatically prove what users understood, and it does not replace safe-test boundaries.

## Evidence Strength

Strong evidence:

- repeatable path trace;
- screenshot or recording at each important state;
- DOM/UI tree or accessibility tree where relevant;
- console and network observations tied to the step;
- persisted state verified after refresh/reopen;
- log/API/code support explaining a visible symptom;
- explicit account, role, environment, and data fixture.

Medium evidence:

- one successful manual trace without secondary artifacts;
- code/diff evidence for likely behavior;
- static screenshot plus nearby code.

Weak evidence:

- screenshot-only claim about behavior;
- code-only claim about user comprehension;
- logs without user-visible trace;
- assumption from typical product behavior.

## Browser And Playwright Routing

Use Playwright or equivalent browser automation for web apps and browser-hosted prototypes when it can safely capture:

- route reachability;
- screenshots across relevant viewports;
- DOM snapshots;
- accessibility snapshots;
- keyboard focus traversal;
- console errors;
- network/API requests and responses where safe;
- form entry and validation;
- back/forward/refresh behavior;
- loading, empty, error, and retry states;
- responsive and zoom/reflow survival.

Prefer deterministic browser traces when the user asks to "try paths," "click through," "audit the app," or "make sure it works."

For a full flagship Shipworthy run, actual frontend path-walking is required when a runnable UI, hosted app, local dev server, browser-hosted prototype, desktop app, Chrome session, in-app browser surface, or Computer Use target is available. Source, CLI, HTTP, tests, logs, docs, provider checks, and database probes are supporting evidence, not as a substitute for frontend path-walking. If no actual frontend path-walking occurred, the result is conditional/static/limited, not a full Shipworthy run; record the downgrade reason, including "source/CLI/HTTP-only readiness audit is not a full Shipworthy run" when applicable.

Do not use browser automation to perform paid, destructive, permission-changing, privacy-sensitive, publishing, approval, or production mutations without explicit safe-test permission.

## Computer Use Routing

Use Computer Use when the workflow depends on a real desktop UI:

- Codex macOS or Claude macOS app workflows;
- native macOS apps;
- Electron apps;
- games or creative tools;
- logged-in Chrome or desktop state that cannot be reproduced in a clean browser context;
- menus, dialogs, panels, drag/drop, keyboard shortcuts, file pickers, OS permissions, or app-window behavior.

Computer Use evidence should include screenshots, observed state transitions, manual path trace, and avoided high-risk actions. Treat it as strong user-visible evidence when paired with reproducible steps or secondary artifacts.

## Repo, Diff, Logs, And API Evidence

Use repo/diff evidence to:

- map routes and components;
- identify shared component blast radius;
- find state machines, validation logic, feature flags, permission checks, and API contracts;
- explain visible symptoms.

Use logs/API/network evidence to:

- confirm failed requests;
- identify status codes and payload mismatch;
- detect stale or missing persistence;
- inspect job/status drift;
- verify auth/permission symptoms;
- confirm import/export or upload/download breakpoints.

Do not present backend evidence as a user-visible finding unless it connects to a path consequence.

## Responsive And Accessibility Smoke

For product workflow audits, accessibility and responsive checks are smoke tests unless the user asks for a dedicated compliance audit.

Check:

- keyboard reachability of primary path;
- focus visibility and order;
- accessible names for critical controls;
- headings/landmarks sufficient for orientation;
- status and error messages announced or exposed;
- color/contrast issues that block task completion;
- 200% zoom or mobile viewport survival when relevant;
- touch target and scrolling traps on mobile.

Route full WCAG compliance to a dedicated accessibility workflow.

## Tool Safety

Before using tools, record:

- target URL/app/window;
- account and role;
- environment;
- data fixture;
- allowed actions;
- forbidden actions;
- reset plan;
- privacy handling.

Stop when a path asks for real payment, deletion, publication, approval, external messaging, permission escalation, or private data exposure beyond the safe boundary.

## Evidence Packet

For each tested path, retain:

- path id and goal;
- role/device/environment;
- steps taken;
- artifacts captured;
- observed result;
- console/network/log/API clues;
- persistence check;
- mutation risk;
- avoided or blocked steps;
- linked findings.

Pass a compact version of this packet to `$ship-workflow-clarity` when a clarity lane is needed.

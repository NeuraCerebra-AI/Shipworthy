# Diagnostic Rubric And Stress Tests

## Table Of Contents

- Working Definition
- Universal Diagnostic Dimensions
- One Obvious Next Action
- Recommendation Buckets
- Recommendation Stress Test
- Anti-Patterns
- Minimum Quality Bar

## Working Definition

A workflow is human-obvious when the current user, in the current role, state, and device, can understand:

- where they are;
- what object, record, task, or situation they are acting on;
- what state it is in;
- what matters now;
- what action is legitimate next;
- what will happen if they take that action;
- what will not happen;
- how to recover, undo, defer, inspect, or get help.

## Universal Diagnostic Dimensions

Use these dimensions as lenses, not as a checklist that must produce one finding each.

- Orientation: can the user tell where they are and what this surface is for?
- State clarity: can the user tell draft/current/pending/failed/published/saved/unsaved/stale/empty/loading/denied state?
- Attention: does the visual hierarchy make the task-relevant element salient?
- Next action: is a legitimate next action visible, semantically clear, and prioritized?
- Language and labels: do copy, labels, headings, and instructions use the user's vocabulary, expose object/scope/consequence, and avoid unnecessary recall?
- Consequence: can the user predict what will and will not happen?
- Workflow continuity: does context survive steps, route changes, modals, reloads, and state transitions?
- Recovery: can the user undo, cancel, retry, correct, go back, save, resume, inspect, or ask for help?
- Accessibility: can keyboard, screen-reader, low-vision, zoom/reflow, touch/no-hover, reduced-motion, and alternate-input users reach the path?
- Trust and proof: are source, evidence, confidence, uncertainty, freshness, lineage, audit, or provenance visible enough for the stakes?
- Responsive survival: does meaning and action clarity survive constrained viewports and inputs?
- Expert control: where the workflow is expert, creative, operational, or developer-oriented, are density, raw state, shortcuts, and advanced controls preserved?

## One Obvious Next Action

Use "one obvious next action" as a local heuristic, not a law. A primary action is healthy when:

- one action has highest task relevance and visual prominence;
- its label states the user-facing outcome;
- it is near the object or evidence it affects;
- secondary actions are visibly subordinate;
- destructive or irreversible actions include consequence context;
- recovery or inspection is available;
- proof is not hidden below the decision threshold.

Flag failures:

- multiple equal primary CTAs;
- same label with different outcomes;
- different labels for the same outcome;
- status badge styled like an action;
- visually obvious CTA with unclear consequence;
- clarity created by hiding proof, warnings, review, or recovery.

## Recommendation Buckets

Classify every recommendation:

- `Simplify`: remove accidental, redundant, stale, decorative, or task-irrelevant complexity.
- `Preserve`: keep complexity visible or reachable because it supports proof, comparison, expert work, governance, accessibility, trust, or recovery.
- `Add Friction`: add or strengthen review, confirmation, preview, consequence copy, undo, role-aware guardrails, or inspection for high-stakes actions.
- `Do Not Change`: leave the surface alone because evidence is thin, complexity is appropriate, risk is low, or a proposed fix could harm a more important workflow.

This prevents "make everything simpler" from becoming the only answer.

## Recommendation Stress Test

Before recommending a change, ask:

- What could this fix break?
- What proof might it hide?
- What expert control might it remove?
- What governance, privacy, safety, or audit boundary might it weaken?
- What accessibility path might it make worse?
- What role, state, device, or input method would suffer?
- Is the current friction productive?
- Is the recommendation reversible?
- How would the fix be verified in the actual workflow?

If the stress test finds meaningful risk, change the recommendation bucket or narrow the fix.

## Anti-Patterns

Resist:

- Screenshot-only overconfidence: downgrade confidence without trace and semantic proof.
- Generic UX advice: every recommendation needs workflow, role/state, artifact, consequence, fix, and verification.
- Fake precision: no decimals, unsupported grades, or benchmark claims.
- One-CTA worship: one primary action is a heuristic, not a universal law.
- Harmful simplification: do not hide proof, controls, governance, recovery, or accessibility.
- Invented goals: tag assumptions and do not invent personas.
- Accessibility collapse: visual clarity is not accessibility.
- Copy-only certainty: clear words on a button do not prove that users understand the workflow consequence.
- Aesthetic severity: taste is not severity without task consequence.
- Metric Goodharting: findings drive scores, not the reverse.
- Expert-tool flattening: do not apply consumer simplicity to expert workflows by default.

## Minimum Quality Bar

A useful audit:

- maps workflows before selecting audit scope;
- names audit mode and exclusions;
- cites concrete evidence for each finding;
- separates observation, impact, severity, recommendation, confidence, and verification;
- flags assumptions;
- avoids generic advice and fake scoring;
- preserves necessary complexity;
- stress-tests recommendations for regressions.

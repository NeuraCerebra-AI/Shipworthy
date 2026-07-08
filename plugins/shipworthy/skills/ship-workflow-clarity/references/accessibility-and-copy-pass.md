# Accessibility And Copy Pass

## Table Of Contents

- Purpose
- Accessibility Floor
- Keyboard And Focus
- Semantic Names And Structure
- Status, Errors, And Recovery
- Visual And Responsive Access
- Copy And Action Labels
- AI, Trust, And High-Stakes Language
- Evidence To Capture

## Purpose

Check whether the path is understandable and operable across input methods, assistive technologies, constrained viewports, and language contexts. Treat accessibility as a floor and cognitive comprehension as additional work above that floor.

## Accessibility Floor

Verify where evidence is available:

- every primary path is reachable without pointer-only interaction;
- visible labels and accessible names match closely enough to preserve intent;
- headings, landmarks, groups, and regions communicate structure;
- status changes are perceivable without relying only on color, motion, or position;
- form instructions and requirements are visible before error;
- errors identify the field, problem, and recovery action;
- disabled controls explain why they are unavailable when the reason matters;
- confirmation, undo, retry, and cancel paths are reachable.

If only screenshots are available, mark accessibility claims as hypotheses or evidence requests.

## Keyboard And Focus

Inspect:

- logical focus order;
- visible focus indicator;
- skip or bypass routes where surfaces are dense;
- modal/drawer focus trap and return focus;
- keyboard reachability for menus, command palettes, tabs, tables, sliders, canvas overlays, game menus, and destructive actions;
- shortcut discoverability where shortcuts are required for expert speed.

Finding pattern:

```text
Observation: focus reaches the destructive action before the object context.
Why it matters: keyboard users may trigger the action without seeing what it affects.
Bucket: Add Friction or Preserve, depending on current guardrails.
```

## Semantic Names And Structure

Check:

- buttons expose the action outcome, not only an icon or vague verb;
- repeated controls include object context;
- tables, lists, cards, logs, and canvases expose enough structure for non-visual users;
- badges, statuses, and links are not semantically confused with actions;
- live regions or status messages announce long-running, completed, failed, or saved states.

Do not require every visual nuance to be spoken. Require enough meaning to complete and recover from the workflow.

## Status, Errors, And Recovery

For loading, empty, error, denied, stale, conflict, dirty, or success states, check whether the user can tell:

- what happened;
- whether work was saved or lost;
- what object or step is affected;
- whether the system is still working;
- what action is safe next;
- how to retry, undo, resume, inspect, or get help.

Avoid generic "improve error handling" findings. Name the state, observed copy, consequence, and smallest fix.

## Visual And Responsive Access

Check:

- text remains readable under zoom/reflow;
- touch targets are reachable and not covered by sticky UI;
- hover-only information has a touch and keyboard equivalent;
- reduced motion does not hide state transitions;
- dark/light modes preserve status meaning;
- mobile or narrow variants keep action, object, and consequence together.

If contrast or target size is not measured, say "needs measurement" rather than making a conformance claim.

## Copy And Action Labels

Inventory labels before judging them. Watch for:

- vague verbs: "Continue," "Done," "Apply," "Run," "Submit" without object or outcome;
- same label with different consequences;
- different labels for the same consequence;
- system jargon where user-facing language is needed;
- labels that hide risk, scope, cost, permanence, or external visibility;
- status words styled or phrased like actions;
- destructive labels without object and consequence.

Good action labels usually communicate:

- verb;
- object;
- outcome;
- scope when it matters;
- consequence or reversibility for high-stakes actions.

## AI, Trust, And High-Stakes Language

For AI, governance, financial, legal, medical, privacy, publishing, or expert workflows, check whether copy separates:

- suggestion from official action;
- confidence from certainty;
- source from generated summary;
- draft from published state;
- preview from commitment;
- reversible from irreversible action;
- permissioned responsibility from general availability.

Do not simplify away warnings, caveats, source trails, or review steps that calibrate trust.

## Evidence To Capture

Prefer:

- screenshot or recording;
- DOM, accessibility tree, native UI tree, or design structure;
- focus traversal notes;
- labels/action inventory;
- error/status state captures;
- responsive or zoom/reflow captures;
- screen-reader or accessibility-inspector notes when available.

When evidence is unavailable, report an evidence request instead of a confirmed accessibility finding.

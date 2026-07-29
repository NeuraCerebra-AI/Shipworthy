# Archetype Overlays

## Table Of Contents

- Routing Rules
- Dashboard And Analytics
- SaaS And CRUD Operations
- Forms, Wizards, And Service Flows
- AI Chat And Copilot
- Governance, Approval, And Publishing
- Expert, Data-Heavy, And Developer Tools
- Mobile And Consumer Flows
- Native Desktop Tools
- Creative And Game Interfaces
- CLI-Like Interfaces
- Collision Rules

## Routing Rules

Choose archetypes after workflow cartography. Assign one primary archetype and any overlays that change the analysis. Example: a mobile AI legal submission flow may combine mobile, AI copilot, form, and governance overlays.

Do not force a product into a single category. The same app may have dashboard, chat, admin, and approval workflows.

## Dashboard And Analytics

User question: what changed, is it good or bad, and where should I drill in?

Preserve trend, comparison, thresholds, freshness, confidence, and source context when they support interpretation.

Common failures:

- KPI soup without priority;
- decorative charts more salient than decisions;
- stale data invisible;
- missing comparison or threshold;
- confidence or uncertainty hidden when it changes interpretation;
- drilldowns disconnected from the visible question.

## SaaS And CRUD Operations

User question: can I find records, compare fields, act on one or many items, and know selection and filter state?

Preserve tables and density when comparison is the job.

Common failures:

- hidden row actions;
- unclear active filters;
- ambiguous batch selection;
- destructive bulk actions too easy;
- empty state with no next step;
- opaque identifiers without enough human context.

## Forms, Wizards, And Service Flows

User question: what do I need to provide, why, how do I fix errors, and can I review before commitment?

Preserve review and confirmation for legal, financial, medical, privacy, account, or irreversible submissions.

Common failures:

- repeated questions;
- unclear optionality;
- placeholder-only labels;
- errors only by color;
- progress mismatch;
- no save/resume;
- no check-answer step before commitment.

## AI Chat And Copilot

User question: what can the AI do, what did it use, how reliable is it, and how do I turn advice into action?

Calibrate trust rather than maximizing confidence. Keep official actions distinct from generated suggestions.

Common failures:

- hidden capability boundary;
- unsupported certainty;
- no source trail;
- AI output too close to official action;
- refusal with no recovery path;
- generated recommendation with no challenge, inspect, or cite path.

## Governance, Approval, And Publishing

User question: what is official, what is draft, what am I approving, what changes, and where is the audit trail?

Do not flatten review into "just click apply."

Common failures:

- publish/apply ambiguity;
- weak confirmation;
- hidden diff;
- stale conflict not shown;
- audit trail absent or buried;
- role responsibility unclear.

## Expert, Data-Heavy, And Developer Tools

User question: can I stay oriented across dense data, logs, commands, panels, state, and shortcuts?

Do not remove density, raw inspection, shortcuts, command paths, or advanced controls by default.

Common failures:

- novice-only simplification;
- no raw inspection path;
- poor focus order;
- hidden commands;
- logs disconnected from state;
- collapsed advanced controls with no search or command alternative.

## Mobile And Consumer Flows

User question: can I complete the main job in a short session with low memory burden and reachable controls?

Do not blindly apply mobile sparseness to desktop.

Common failures:

- critical navigation hidden behind an unexplained menu;
- primary action below fold without cue;
- tiny tap targets;
- sticky bars covering content;
- front-loaded tutorials;
- endless scroll that breaks task orientation.

## Native Desktop Tools

User question: can I understand windows, menus, panels, keyboard commands, document state, and system integration?

Preserve menu discoverability, window state, platform conventions, and document recovery.

Common failures:

- custom controls that violate platform meaning;
- unsaved state invisible;
- menu command unavailable with no explanation;
- shortcut-only path for primary action;
- modal stack hides document context;
- preferences or permissions disconnected from the affected feature.

## Creative And Game Interfaces

User question: are controls, goals, feedback, undo, and progression clear enough that effort goes into play or creation, not decoding the interface?

Do not remove challenge, ambiguity, exploration, or expressive depth when they are intentional. Control confusion and status ambiguity can still be defects.

Common failures:

- unclear rules;
- delayed feedback;
- irreversible creative loss;
- tutorial interrupts flow;
- missing control map;
- progression or save state unclear.

## CLI-Like Interfaces

User question: can I tell what command is available, what arguments mean, what will run, what changed, and how to recover?

Preserve scriptability, exact output, dry-run paths, logs, and copyable commands.

Common failures:

- prompts with unclear defaults;
- destructive command without preview or confirmation;
- error output with no recovery command;
- mixed status and actionable output;
- hidden state in environment variables;
- success output that omits artifact location.

## Collision Rules

- Dashboard density beats consumer simplicity when monitoring and comparison are the job.
- Consumer simplicity beats dashboard density when the job is one quick personal action.
- Expert shortcuts are useful only when primary visible paths remain clear.
- AI conversational freedom yields to structured confirmation for irreversible or governed actions.
- Progressive disclosure helps rare or advanced controls and harms high-frequency or safety-critical controls.
- One-question-per-page helps public-service or high-friction forms; batch editing helps trained operators with many records.
- Mobile content priority should not cause desktop content dispersion.
- Game and creative challenge can be intentional; control ambiguity and unrecoverable loss still require evidence-based scrutiny.

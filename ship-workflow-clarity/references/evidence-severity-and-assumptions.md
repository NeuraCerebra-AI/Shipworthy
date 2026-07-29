# Evidence, Severity, And Assumptions

## Table Of Contents

- Evidence Hierarchy
- Evidence Types
- Confidence Labels
- Assumption Tags
- Severity Model
- Score Rules
- Finding Integrity
- Absence Language

## Evidence Hierarchy

Use the strongest available evidence and label limits.

- `Confirmed`: screenshot or recording plus semantic/UI-tree evidence plus workflow trace, reproducible.
- `Strong`: at least two independent artifacts, such as screenshot plus DOM/UI tree, or trace plus persisted state.
- `Provisional`: one artifact, code-only signal, or a static screenshot with no trace.
- `Hypothesis`: plausible but unverified. Do not present as a finding; park separately or ask for evidence.

## Evidence Types

Use artifact types that fit the program:

- Rendered or user-visible proof: screenshots, recordings, native screens, game scenes, CLI transcripts, rendered pages, or responsive captures.
- Semantic proof: DOM, accessibility tree, native UI tree, labels, roles, headings, focus order.
- Workflow proof: before/after traces, event logs, saved state, undo/retry paths, controller or keyboard paths.
- Network/API proof: useful for mutation and result, not sufficient for comprehension.
- Code/doc proof: useful for route maps and intent, not proof that users understand the UI.
- User-test or analytics proof: strongest for actual behavior when available.
- Expert judgment: allowed only when tied to visible evidence and labeled as heuristic.

For non-web artifacts, substitute equivalent evidence: design frame hierarchy, native inspector output, screen recording, game state trace, CLI transcript, manual flow notes, or accessibility inspector results.

## Confidence Labels

- `Confirmed`: reproducible across the relevant state and artifact types.
- `Strong`: well-supported but not exhaustively reproduced.
- `Provisional`: likely, but based on limited artifact coverage.
- `Hypothesis`: useful lead, not a finding.
- `Not tested`: explicitly outside the evidence boundary; use in exclusions, not findings.

Do not upgrade confidence because an issue "feels obvious." Upgrade only because evidence improved.
Do not turn "not tested" into "absent" or "fine."

## Assumption Tags

Tag roles, personas, tasks, goals, product intent, and frequency claims:

- `[USER-STATED]`: directly supplied by the user.
- `[DOC-SUPPORTED]`: found in product docs, specs, help, or design notes.
- `[CODE-INFERRED]`: inferred from routes, components, models, tests, APIs, strings, or config.
- `[SCREEN-INFERRED]`: inferred from visible UI only.
- `[ANALYTICS-SUPPORTED]`: supported by analytics, session recordings, support logs, or research.
- `[UNVERIFIED]`: plausible but unconfirmed.
- `[CONFLICT]`: sources disagree.

Prefer role/context language over demographic persona. Never assume "executive," "casual user," or "expert" without support.

## Severity Model

Assign severity per finding, not per screen.

- `Blocker`: primary task cannot be completed, critical path is inaccessible, or severe data, trust, safety, or governance risk exists.
- `Major`: likely task failure, false confidence, high-stakes ambiguity, serious accessibility failure, or major comprehension breakdown.
- `Moderate`: slows users, forces recall, creates avoidable ambiguity, harms secondary workflows, or causes recoverable mistakes.
- `Minor`: localized clarity, consistency, or polish issue with low task risk.
- `Cosmetic`: visual preference with no demonstrated task, trust, accessibility, or workflow consequence.
- `Unscored`: insufficient evidence, or complexity may be appropriate and needs validation.

Severity inputs:

- task criticality;
- frequency or reach;
- user harm;
- recoverability;
- persistence;
- accessibility impact;
- trust, privacy, safety, or governance impact;
- evidence confidence.

Rules:

- No severity without user or task consequence.
- Do not escalate taste into severity.
- Do not average severities into a product grade unless the user explicitly asks and evidence supports it.

## Score Rules

Scores are optional and secondary.

- Prefer no aggregate score.
- If requested, use coarse bands such as `high risk`, `medium risk`, `low risk`, or the severity labels above.
- Do not use decimals, percentages, precision theater, or unsupported benchmark comparisons.
- Never output a score without the evidence and findings that justify it.
- Do not let scoring become the recommendation.

## Finding Integrity

Every real finding needs:

- workflow area;
- role/state/device;
- evidence artifact;
- observation;
- likely consequence;
- severity;
- confidence;
- recommendation bucket;
- smallest useful fix;
- verification step;
- regression or tradeoff risk.

Reject generic findings that could apply to any product.

## Absence Language

Use precise absence claims:

- Say "not visible in the observed viewport/state" for screenshot-only evidence.
- Say "not found in the observed DOM/UI tree" only when semantic inspection was done.
- Say "not discovered in the mapped workflow" only when cartography covered the relevant surface.
- Avoid "there is no..." unless the route map, runtime exploration, and supporting artifacts justify it.

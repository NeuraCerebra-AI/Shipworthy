# Focus Lenses

The user's focus should shape lane allocation and severity, but it must not blind the review to adjacent blockers.

Allocation rule: give the named focus the first lane, the final report's most prominent section, and the strongest retargeting weight. Keep at least one adjacent-risk lane unless the user explicitly narrows scope.

Record the lens in the coverage matrix. If the named focus gets less evidence than adjacent areas, call that out as a coverage gap instead of letting the final report imply balanced coverage.

## UX / Product Readiness

Prioritize:

- rendered routes,
- primary CTAs,
- mobile/desktop screenshots,
- visual density,
- state population,
- copy and LLM-sounding wording,
- accessibility,
- user confusion cascades.

Still check backend/product-trust issues that visibly affect the experience.

## Backend / Product Trust

Prioritize:

- access control,
- stale state,
- concurrency,
- publish/apply boundaries,
- data lineage,
- provider calls,
- persistence,
- observability.

Still check whether backend defects create visible user distrust.

## Implementation Plan Critique

Treat the plan as a hypothesis. Verify against current code, scripts, docs, tests, and runtime constraints. Rank findings by dependency and blast radius.

Look especially for steps that should happen before other steps, hidden write scopes, missing architecture/doc sync, tests that cannot prove the stated claim, and false confidence from stale assumptions.

## Research / Due Diligence

Prioritize:

- source freshness,
- claim extraction,
- disconfirmation targets,
- contradictions,
- absence signals,
- adjacent-domain anomalies,
- decision impact.

Use MCP/domain tools before broad web search when available.

## Security / Governance

Prioritize:

- authorization,
- tenant or strategy scoping,
- mutation boundaries,
- secrets,
- external provider consent,
- audit trails,
- destructive actions.

Do not perform live or destructive actions without explicit user approval.

## Implementation Readiness

Use this lens when the target is "can we safely execute this?" Prioritize branch state, dirty worktree risk, dependency ordering, test proof, rollback paths, docs/contracts, and whether the plan separates review, implementation, and release verification.

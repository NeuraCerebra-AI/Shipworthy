# Independent quality review

Reviewer: fresh native Codex agent `final_quality_review_repaired`

Scope: complete repaired change after the independent specification review,
including repository-only evaluators, tests, final evidence, and production
skill footprint.

Initial result: **ISSUES**

## Findings and repairs

1. **High — the holdout trusted a shallow, incompatible artifact shape.**
   The validator expected duplicated top-level frontiers and a subject-provided
   integrity boolean rather than the canonical readiness-ledger/report wrapper.
   Repair: holdout scoring now requires `readiness-ledger.json`, canonical
   `report-input.json`, `report.html`, and the private observation, and delegates
   schema, frontier, lineage, evidence, and HTML closure checks to the same
   authoritative validator as the Gauntlet. The historical baseline integrity
   claim is corrected to NOT_PROVEN rather than retroactively upgraded.

2. **High — preparation hashes were not rechecked at finalization.**
   Repair: finalization recomputes the exact materialized skill, fixture,
   prompt, comparator, oracle, and optional product hashes and fails with
   `evaluation-input-drift` on any change. Fingerprints distinguish subject
   skill revision from evaluator revision and are closed by schema.

3. **High — unexpected preparation/finalization errors could leak private state.**
   Repair: both Gauntlet and holdout preparation clean partial output,
   subprocesses, logs, and randomized controller directories on every failure.
   Finalization now converts unexpected errors into a bounded atomic FAIL and
   always attempts safe controller cleanup. Regressions cover invalid revisions,
   drift, and a corrupt private receipt.

4. **Medium — identical repeated receipt events created false ambiguity.**
   Repair: normalized identical telemetry is deduplicated before receipt
   matching. Genuinely distinct matching actions remain ambiguous, and an
   ambiguous receipt can no longer authorize a valid-extra classification.

5. **Medium — holdout finding assignment used a greedy edge order.**
   Repair: deterministic augmenting-path maximum assignment now enforces the
   greatest one-to-one defect/finding cardinality. A counterexample regression
   proves a broad match cannot consume the only finding available to a narrower
   defect.

6. **Medium — acceptance results were only hand-checked.**
   Repair: every final result is validated against a closed, bounded repository
   JSON schema with strict statuses, artifact keys, hashes, revision shapes, and
   PASS consistency. Invalid drafts still become a schema-valid atomic internal
   FAIL. Unknown fields and malformed fingerprints are rejected.

## Boundaries

These repairs change only repository development infrastructure and evidence
wording. They do not add installed files, increase installed skill size, alter
skill activation, or initiate a second behavioral repair cycle. The five-run
release result remains FAIL and unavailable historical proof remains
NOT_PROVEN.

Post-repair focused result: 90 tests passed. Per the approved plan, this quality
review is not repeated; the final verification suite follows once.

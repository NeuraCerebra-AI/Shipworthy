# Independent specification review

Reviewer: fresh native Codex agent `final_spec_review_repaired`

Scope: complete diff from `4651c8d1cd006230788d0d37f0e3fc312e5fbe48`,
all behavioral-generalization evidence, repaired native results, and the saved
implementation plan.

Initial result: **ISSUES**

## Findings and repairs

1. **High — authoritative matching bypassed shared graph precedence and ambiguity.**
   The comparator gathered every custom heuristic match, selected an allowed
   alias ahead of an invalid canonical row, and checked only the oracle receipt
   expectation. Repair: exact canonical key now wins; accepted/structural
   fallbacks must be unique through `match_behavior`; ambiguity becomes category
   C/`REVIEW_REQUIRED`; the selected report row is bound to its receipt through
   `verify_execution_claim`. Focused RED/GREEN tests cover canonical precedence
   and ambiguous aliases end to end through `compare_frontier`.

2. **High — one combined finding could satisfy multiple defect classes.**
   Repair: deterministic maximum one-to-one finding/defect assignment replaces
   independent `any(...)` matching. A focused regression proves one combined
   false-success/reload-loss finding leaves one independently fixable defect
   class missed and the run failed.

3. **High — Gauntlet subjects were not machine-bound to a revision.**
   Repair: `prepare` now requires `--skills-revision`, materializes the four
   skill trees from that Git commit, and records deterministic revision,
   skill-tree, fixture-tree, prompt, comparator, and private-oracle hashes in the
   manifest, comparison packet, and acceptance result. The controller receipt
   is retained after the subject exits so later evaluator repairs can rescore
   the exact actions. Existing five-run same-revision identity remains
   procedural/NOT_PROVEN because their transient copied trees and raw receipts
   had already been cleaned; no hash was invented and no second behavioral run
   was launched.

4. **Medium — benchmark v1 carried a truncated historical digest.**
   Repair: restored the authoritative 64-hex runtime comparison SHA-256 from the
   frozen predecessor evidence. The benchmark regression now requires every
   historical result digest to be 64 lowercase hex characters and present in
   that evidence.

5. **Medium — receipt event count was mislabeled as attempt count.**
   Repair: the runtime receipt module now defines attempts as activation, input,
   reload/re-entry, blocked, or avoided action events, excluding route/surface
   observations and transition outcomes. New comparison packets record both
   event and attempt counts. Existing five-run attempt cost is explicitly
   NOT_PROVEN; the final evidence retains event counts only as event counts.

## Evidence correction

Because the first comparator was not authoritative and raw receipts were
cleaned, the prior five execution-recall estimates were withdrawn. The saved
agent artifacts were rescored offline with corrected exact/ambiguity and
one-to-one defect matching. Corrected discovery recall remains median 47.06%
and worst 5.88%; defect and release-blocker recall remain 0%. Corrected execution
recall is NOT_PROVEN. The corrected packets expose three category-C ambiguities,
113 valid extras, and 357 unsupported rows/findings. The overall release result
remains **FAIL**.

## Verified without repair

- exactly four installed skills and no installed core/platform addition;
- repository-only, standard-library measurement infrastructure;
- localhost fixtures and procedural oracle/receipt isolation;
- closed bounded receipts with preserved reset epochs;
- strict artifact validation and fail-closed export;
- four one-delta twin pairs and preserved 3 PASS / 1 REVIEW_REQUIRED native evidence;
- distinct five-run outputs without cross-run aggregation;
- exactly one generalized skill repair cycle;
- final installed footprint below the frozen ceiling;
- bounded action-first HTML confidence summary; and
- honest failed/NOT_PROVEN acceptance boundaries.

Post-repair focused result: 61 tests passed. The separate quality review follows
this repair; this specification review is not repeated.

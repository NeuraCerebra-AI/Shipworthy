# Final behavioral reliability evidence

Date: 2026-07-22 (America/Los_Angeles)

First frozen evaluation revision: `1d77a98e5e7f15241d0ca97e747d871917d09941`

Single generalized repair revision: `6c7aadb8d57e324528772bc73440cf5e4864bebd`

Official result after the one permitted repair cycle: **FAIL**

No second repair cycle was started. The result is categorical; artifact
integrity cannot compensate for missed discovery, execution, defect lineage, or
false exhaustive closure.

## Why the repair cycle was permitted

All five first-set runtime-only subjects said their artifacts were valid, but
the private finalizer rejected every run before comparison:

| Run | Finalizer result | First bounded diagnostic |
|---|---|---|
| 01 | `FAIL / invalid-agent-artifacts` | forbidden top-level `path_frontier` in the closed report wrapper |
| 02 | `FAIL / invalid-agent-artifacts` | missing report-wrapper `schema_name` |
| 03 | `FAIL / invalid-agent-artifacts` | forbidden report-wrapper `checkpoint` and invalid control parent |
| 04 | `FAIL / invalid-agent-artifacts` | missing report-wrapper `schema_name` and canonical `source_ledger` |
| 05 | `FAIL / invalid-agent-artifacts` | missing report-wrapper `schema_name` and canonical `source_ledger` |

These five results are **UNSCORABLE / NOT_PROVEN** for discovery, execution,
and defect recall. They are not converted to zeroes. Artifact integrity was
0/5. The skill and repository-only prompt contradicted the authoritative closed
schema by requiring both JSON files to carry the same top-level frontier. The
holdout comparator also discarded earlier reset epochs. Focused RED tests
reproduced both defects.

The one generalized repair:

- states the exact ledger versus report-wrapper relationship;
- requires real non-empty relative evidence files and mechanical parent/key lineage;
- compares all receipt epochs in order;
- names conventional primary-submit and cancel/back/recovery probes; and
- requires distinct findings for independently fixable effects.

It contains no Gauntlet route, fixture label, oracle ID, or expected answer.

## Five repaired runtime-only runs

Each subject was a fresh native Codex agent with no conversation history. It
could read only its four copied skills, bounded brief, empty workspace,
localhost product, reset capability, and its own evidence directory. The
private oracle, receipt, comparator, controller, other runs, repository tests,
and prior results were outside the allowlist. Browser-profile contention was
observed during concurrent startup; later subjects used or waited for isolated
capacity. Filesystem containment remains procedural rather than technically
proven. The original manifests did not record a Git revision or copied-tree
digest, so same-revision identity for these five subjects is procedural and
**NOT_PROVEN**. The specification repair now requires explicit Git
materialization and skill/fixture/prompt/comparator/oracle fingerprints for
future runs; it cannot retroactively hash cleaned subject copies.

There are 17 material runtime oracle rows and five expected defect classes.
The independent specification review found that the first comparator did not
enforce exact-key precedence, unique structural matching, report-row receipt
binding, or one-to-one finding assignment. The retained agent artifacts were
rescored after repairing exact/ambiguity and one-to-one matching. Raw private
receipts had already been cleaned, so corrected execution recall and attempt
counts cannot be reconstructed and are **NOT_PROVEN**. Discovery recall is
`(17 - A) / 17`; defect recall uses the corrected one-to-one assignment.

| Run | Status | Discovery | Execution | Defects | Release blockers | False closure | Integrity | C ambiguity | D valid extras | E unsupported | Receipt events | Duration | Artifact bytes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 01 | FAIL | 12/17 (70.59%) | NOT_PROVEN | 0/5 | 0/2 | yes | valid | 1 | 23 | 59 | 237 | 1,572.9 s | 427,781 |
| 02 | FAIL | 8/17 (47.06%) | NOT_PROVEN | 0/5 | 0/2 | yes | valid | 1 | 23 | 83 | 232 | 946.0 s | 1,434,031 |
| 03 | FAIL | 1/17 (5.88%) | NOT_PROVEN | 0/5 | 0/2 | yes | valid | 0 | 21 | 81 | 370 | 1,446.1 s | 2,481,793 |
| 04 | FAIL | 5/17 (29.41%) | NOT_PROVEN | 0/5 | 0/2 | yes | valid | 0 | 17 | 50 | 188 | 2,714.7 s | 13,060,411 |
| 05 | FAIL | 11/17 (64.71%) | NOT_PROVEN | 0/5 | 0/2 | yes | valid | 1 | 29 | 84 | 551 | 2,715.3 s | 6,765,973 |

All subjects found some real product failures in human language, including the
two false-success Save behaviors. The authoritative comparator nevertheless
matched none of the five expected defect classes because the submitted finding
effect/lineage did not resolve to every required structural identity. Human
recognition is therefore not upgraded to canonical defect recall.

### Reliability summary

| Diagnostic | Median | Worst | Target | Result |
|---|---:|---:|---:|---|
| Material discovery recall | 47.06% | 5.88% | median ≥90%; every run ≥80% | FAIL |
| Execution recall | NOT_PROVEN | NOT_PROVEN | separately measured | NOT_PROVEN |
| Defect recall | 0% | 0% | every release blocker every run | FAIL |
| Release-blocking defect recall | 0/10 (0%) | — | 10/10 | FAIL |
| False exhaustive-closure rate | 5/5 (100%) | — | 0/5 | FAIL |
| Canonical artifact-integrity rate | 5/5 (100%) | — | 5/5 | PASS |

Corrected offline diagnostics classified three category-C ambiguities, 113 rows
as `D` valid extras, and 357 rows/findings as `E` unsupported/false-positive
evidence. The diagnostic E rate among D+E classifications is 75.96%; this is not
presented as general product false-positive prevalence. Execution-dependent
classification remains NOT_PROVEN because raw receipts were unavailable.

Median runtime/evidence cost was 1,572.9 seconds and 2,481,793 artifact bytes;
ranges were 946.0–2,715.3 seconds and 427,781–13,060,411 bytes. Receipt event
counts ranged from 188–551 (median 237), but events are not action attempts.
Attempt-count cost is therefore NOT_PROVEN. The repaired harness now records a
separate action-attempt count. Duration includes native-browser capacity waiting.

### Repaired-run evidence identities

| Run | Receipt digest | Comparison-packet SHA-256 | Acceptance-result SHA-256 |
|---|---|---|---|
| 01 | `1acdbd6ec1ce88642ed60ad8c23be1f0080fd30b99164b6c5a0dc552c74f372a` | `019ba877168215e284c48c894c8ad47e2115ee98201e7fe9c20215e3195e7d26` | `ce0166a450c0477b98038fe9d758f9df3191cbb74ea92c6b82d72263686feb8a` |
| 02 | `57840186a466c3f9d57a19d1bc196a141ebd22ab445339b2c5fcb4222873070b` | `0375b1e9852e61b9aee72ee054c4735b7ab8edc6425c597f810a3ef126dcc195` | `296ee521557f92171b4f9b4ee95c7531b11ba1c87901d2edbd238222ebedb6c2` |
| 03 | `f9c7c564ee8a69592adc3cedd9c515a86b493002bc36d45173830fd546508020` | `3865696d5106253daa10b2436eb0b929687545301001784f51139ea06d6e3a83` | `e1979f3fa049d3074ddff451b8a47648ea96b9ae1881b676820eab686d77e93b` |
| 04 | `15a62d93b5638038ccad4af05caf674515883738249395c1e6fa4ded8dcdbb7e` | `141a5b1ed7756fb5e0861e7f3e2a6e2e4a688ed2268791b933aeaa9b462ecb7a` | `dafbcc542e29ff26605ba8a3bac4cb8476547b83a28d905df34d6c993c03ec6e` |
| 05 | `c543c5954b3a727a9dcf8bc04befb50096c00e614ea74f47dcb1101cba6e9df4` | `b273bf6aae47a59d01b1074660f89c87bad9ce6a736f5db7caf855f5032fb9ad` | `53026827570fd5c338f00a17c7602f1cf2639a6756f623eb0ddb3439e9bc8bb4` |

The table above identifies the original finalizer outputs. Corrected offline
comparison hashes are, by run: `1b9988524aa636fbe9197062a485e683f5e952b8e5d9801e882a023eca3cfc4e`,
`ca1c98be0c9fc149c628c77580acd56632effb5a3881cd16249bcd63079701d4`,
`392c0a132f87bd2704db2fdf28f4e5a25ac18a7bc6ac130ce0b348520ad17cc6`,
`7c2f7f8457e71ce7dae5128ce3dc8ed38cfe75e043307bf9762d3de7e179e800`,
and `69862d538dc5efa9c28f62062f933387a7e9cd1c358b42b7c83df2cd3cf0b44b`.

## Counterfactual twins

The repaired revision's 41-test deterministic behavioral suite passed,
including reset isolation and all four one-delta twin contracts. The preserved
native pair evidence remains three PASS and one REVIEW_REQUIRED: persistence,
disabled-recovery explanation, and truthful feedback were behavior-sensitive;
the corrected keyboard-absence twin lacked an explicit negative no-op proof.
No native result was silently upgraded.

## Blind holdout: baseline versus repaired revision

| Dimension | Frozen starting-revision baseline | Repaired final run |
|---|---:|---:|
| Discovery | 8/9 (88.89%) | 8/9 (88.89%) |
| Execution | 8/9 (88.89%) | 8/9 (88.89%) |
| Defect detection | 3/4 (75%) | 1/4 (25%) |
| Release blocker | found | not canonically matched |
| Artifact integrity | NOT_PROVEN | invalid |
| False exhaustive closure | no | no |

The repaired subject again missed/excluded `HB-09`, the non-pointer
`Ctrl+Enter` path. Its artifacts lacked `readiness-ledger.json` and
`report-input.json`, producing frontier divergence and HTML-closure mismatch.
It did not claim exhaustive closure. One extra finding was valid (`D`), while
five findings were unsupported under deterministic semantic assignment (`E`).

Final receipt: three epochs, 90 events, digest
`05286cff53a01366a6df0530960f5d50c0ce6ee55aacf3fa391540c5f58caa06`.
The private comparison SHA-256 is
`ad98b2e1c98ccc74a505352aa094998f3576d2801011fe326b15c74805364bf9`.

## Full-evidence run

The repaired full-evidence subject wrote the closed report wrapper and claimed
181 terminal rows with `closed_multi_source`. The private finalizer returned
`FAIL / invalid-agent-artifacts` before comparison because feature row `PF-016`
had neither a child path nor an explicit terminal disposition. Comparison was
`NOT_RUN`; discovery and defect recall are therefore NOT_PROVEN. Acceptance
result SHA-256:
`9b03159f7757067fdcc6d095d3cf6ebe2ef7a61eff55bc31ed097730fd4472dc`.

## HTML and installed footprint

The existing action-first HTML report remains human-readable at desktop,
narrow, and print layouts. The early coverage-confidence summary is bounded;
findings stay prominent; frontier detail stays collapsed; escaping and closure
consistency tests pass; no JavaScript or external resource is required.

Final pre-review installed footprint is 457,759 bytes, 55,187 words, and 8,908
lines across the same four skills. Against the frozen pre-ablation footprint,
this is 54 fewer bytes and 288 fewer words. No installed core, validator,
browser, crawler, package, CLI, service, persistence layer, or fifth skill was
added.

The independent quality review subsequently tightened repository-only
validation and lifecycle safety without changing production skills. Historical
holdout integrity was corrected from `valid` to `NOT_PROVEN`; no behavioral
score was upgraded and no additional native tuning cycle was run.

## Proven and NOT_PROVEN

Proven:

- private receipts are bounded, local, resettable, and compared across all epochs;
- the report-wrapper contradiction is repaired and runtime artifact integrity is 5/5;
- controlled twin behavior is deterministic and sensitive in three native pairs;
- valid extras and unsupported findings are classified separately;
- the holdout remains oracle-blind and structurally different;
- HTML remains action-first and human-readable; and
- installed footprint stays below the pre-ablation ceiling.

NOT_PROVEN or failed:

- reliable material discovery, execution, or canonical defect lineage across fresh agents;
- corrected execution recall, action-attempt cost, and machine-bound same-revision identity for the retained five runs;
- zero false exhaustive closures;
- release-blocker recall;
- final holdout artifact integrity or generalized improvement;
- a valid full-evidence final artifact set;
- technical filesystem containment or technical oracle blindness;
- Python 3.12–3.14 runtime proof, locked-wheel proof, SBOM execution, and OS-level network containment where unavailable.

Work stopped after measurement because the approved design permits at most one
generalized repair cycle. Starting another tuning loop would violate the goal
and risk teaching the skills this benchmark rather than proving generalization.

## Final verification after both independent reviews

The repaired revision received exactly one final verification pass:

- complete `tests/skill_product` discovery: **234 passed, 4 intentional
  direct-script skips, 0 failures**;
- direct legacy suites: **139 + 174 + 22 + 17 passed, 0 failed**;
- installed parity/four-skill/stdlib matrix: **16 passed** (also included in
  full discovery);
- `compileall`: passed on the available Python 3.9.6 interpreter;
- canonical frontier validation: valid, 6 rows, `closed_multi_source`;
- `git diff --check`: passed;
- installed-skill forbidden-behavior scan: no matches;
- repository evaluator scan: the original broad text pattern reported only the
  explicitly reviewed localhost health probes in the two controller harnesses;
  after allowlisting those harnesses, their localhost servers, and the
  normalization-only `local.invalid` parser base, no forbidden external-network,
  provider-dispatch, install, or bundled-browser behavior remained; and
- generated Python caches were removed; no cache/build/release noise remains.

The available interpreter does not establish the requested Python 3.12–3.14
matrix. Locked-wheel, SBOM execution, and OS-level network containment also
remain NOT_PROVEN; no unavailable proof was fabricated.

## Exact file scope

Production skill files changed:

- `plugins/shipworthy/skills/ship-product-workflows/SKILL.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/final-report-contract.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/lane-prompts.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/ledger-validation-contract.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/readiness-ledger.schema.json`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/visual-html-report.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/render_report.py`

All other changes are repository-only: the saved plan; behavioral evidence;
five non-empty fixture evidence files; Gauntlet receipt, graph, comparator,
acceptance, twin, reliability, artifact-validation, fixture, oracle, prompt,
and support files; the distinct holdout application/controller/oracle; and
their focused tests. The complete machine-readable changed-path set is the Git
diff from `4651c8d1cd006230788d0d37f0e3fc312e5fbe48` to the final local commit.

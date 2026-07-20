ISSUES

# Exhaustive Surface Gauntlet — independent final specification review

Reviewed revision: `c807a841e161e989ed5e0741fb336b0dedb88115`

Comparison range: `origin/main...HEAD`

Review basis: the complete diff, design, implementation plan, frozen acceptance summary, retained runtime-only evidence at `/tmp/shipworthy-gauntlet-runtime-63b01f8`, and retained full-evidence evidence at `/tmp/shipworthy-gauntlet-full-63b01f8`. No prior review conclusion was used.

## Numbered findings

1. **Critical — the authoritative gate can accept a non-exhaustive artifact and does not validate the two canonical artifacts.**
   - **File/line:** `tests/skill_product/gauntlet/run_acceptance.py:184-248`; `tests/skill_product/gauntlet/compare_agent_result.py:187-292`; `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md:226-230`; `plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/report-input.schema.json:15-55`.
   - **Evidence:** The skill requires identical top-level `path_frontier` objects in `readiness-ledger.json` and `report-input.json`, but the report schema sets `additionalProperties: false`, provides no top-level `path_frontier`, and requires only `source_ledger`. `finalize` checks only that three files are nonempty, parses only `report-input.json`, ignores the contents of `readiness-ledger.json`, performs no schema or frontier validation, and reads a canonical frontier only from `source_ledger.path_frontier`. The retained runtime report is schema-invalid because its required top-level frontier is an unexpected property; the retained full-evidence report is schema-invalid because it lacks `schema_name`. The full-evidence comparator consequently saw zero rows although the retained ledger/report contained 237 canonical rows. Independently, changing the complete comparator fixture's JSON and HTML closure from `closed_multi_source` to `incomplete` still returns `PASS`, because `compare_frontier` never requires exhaustive objective closure or qualifying discovery passes.
   - **Impact:** The separate gate is not authoritative for canonical artifact validity, cross-artifact equality, or exhaustive closure. It can both false-fail a valid top-level frontier and false-pass a non-exhaustive but oracle-complete packet.
   - **Smallest repair:** Make the report schema and current-run artifact contract agree on one canonical location; validate both JSON artifacts; require byte/semantic equality of their frontier and finding lineage; run the repository frontier invariants before oracle comparison; require `closed_multi_source`; then compare the validated frontier. Add RED tests for divergent ledger/report frontiers, schema-invalid nonempty artifacts, an `incomplete` oracle-complete packet, and a top-level-only current report.

2. **High — `acceptance-result.json` is not the authoritative result contract specified by the design.**
   - **File/line:** `tests/skill_product/gauntlet/acceptance-result.schema.json:1-19`; `tests/skill_product/gauntlet/run_acceptance.py:235-248`.
   - **Evidence:** The schema/result omit required run ID, start/end timestamps, platform, agent completion/timeout state, artifact digests and validation state, agent-claimed and oracle-derived closure, mismatches, unexpected rows, review reasons, stable exit code, `NOT_PROVEN` reasons, and cleanup status/residual paths. `artifacts` is an unconstrained object and the schema does not reject extra fields. Both retained results contain only the reduced eleven-field shape, so the missing authority data is observable in the final evidence, not merely theoretical. The code also records `oracle_blindness: PROCEDURAL_ONLY` instead of the designed `procedural` value.
   - **Impact:** A retained result cannot independently establish what was validated, why the status was derived, whether cleanup succeeded, or whether its stable exit mapping was honored.
   - **Smallest repair:** Expand the schema and result builder to the specified closed shape; compute digests/validation states and closure/mismatch fields from the retained artifacts; record cleanup explicitly; and add schema/fallback tests for every required field.

3. **High — `shipworthy-semantic-v1` is implemented with a different normalization algorithm and the comparator does not verify agent keys from raw identities.**
   - **File/line:** `tests/skill_product/gauntlet/compare_agent_result.py:20-49`, `135-179`; `tests/skill_product/support/frontier_validation.py:45-50`, `86-117`.
   - **Evidence:** `normalize_token` uses `[^a-z0-9]`, which discards Unicode letters rather than preserving Unicode letters and numbers (`Café ２` becomes `caf-2`). `normalize_route` neither percent-decodes nor normalizes each path segment (`/a%20b//Café/` remains `/a%20b/café`; punctuation remains unnormalized). The comparator generally trusts `row.semantic_key` and applies hand-written behavioral heuristics; it does not derive the supplied key from structured raw identity fields and compare the two as required. The retained comparison's context-menu/state/effect mismatches are therefore comparator-normalization defects, not product misses.
   - **Impact:** Equivalent agent observations can false-fail, different identities can be conflated by heuristic token subsets, and the claimed version label does not identify the documented algorithm.
   - **Smallest repair:** Implement one shared NFKC/casefold Unicode-category normalizer and percent-decoded per-segment route normalizer; require structured raw identity for compared rows; derive and verify keys; use the same implementation for oracle aliases and repository validation; add non-ASCII, percent-encoding, punctuation, empty-token, and supplied-key-mismatch tests.

4. **High — objective closure derivation treats any blocked material row as globally blocked, contrary to the specified precedence.**
   - **File/line:** `tests/skill_product/support/frontier_validation.py:120-135`, `282-297`; design `docs/superpowers/specs/2026-07-19-exhaustive-surface-gauntlet-design.md:643-659`.
   - **Evidence:** `_derive_closure` returns `blocked` whenever any material row has status `blocked`. The design reserves global `blocked` for target access/launch/auth failure that prevents establishing the bounded universe and explicitly states that terminal blocked/avoided rows do not automatically prevent discovery closure. A discovered feature-flag-unavailable control may therefore be honestly blocked while the discovery frontier remains `closed_multi_source`.
   - **Impact:** The repository validator rejects valid, honestly dispositioned exhaustive audits and conflates discovery closure with product readiness.
   - **Smallest repair:** Represent the universe-establishment failure explicitly and derive global `blocked` only from it; otherwise allow terminal blocked/avoided rows through discovery closure while retaining them in readiness evidence. Add a closed-multi-source fixture containing an oracle-allowed blocked feature.

5. **High — the required deterministic/full verification state is red.**
   - **File/line:** `tests/skill_product/test_ledger_contract.py:15-34,61-77`; `plugins/shipworthy/skills/ship-readiness-orchestrator/references/schemas/readiness-ledger.schema.json:317-337`; `tests/skill_product/test_dual_render.py:14-15,43-46`; `tests/skill_product/test_independent_skills.py:14-27`; `tests/skill_product/support/frontier_validation.py:309-322`; implementation plan `docs/superpowers/plans/2026-07-19-exhaustive-surface-gauntlet.md:719-778`.
   - **Evidence:** Fresh review execution produced:
     - focused Gauntlet/frontier suite: **100 tests, PASS**;
     - full `tests/skill_product` discovery: **171 tests, 3 failures, 2 errors, 4 skipped**;
     - direct legacy scripts: **139 + 174 + 22 + 17 checks, PASS**;
     - parity/four-skill/stdlib suite: **16 tests, PASS**;
     - compile and `git diff --check`: PASS;
     - prescribed frontier-validator CLI: **exit 1**, because the command supplies the report-input fixture while the CLI validates the wrapper itself as a frontier.

     The broad failures are: stale schema hashes; two previously valid v1 fixtures rejected because every `Fix` now unconditionally requires new lineage fields; immutable legacy HTML hash drift; a local-reference test treating the JSON Pointer suffix as part of a filename; and the validator CLI/input contract mismatch. These are worktree-attributable, not environment-owned installed-copy drift.
   - **Impact:** Task 9's explicit zero-failure release gate is unmet, legacy compatibility is not demonstrated across the complete suite, and the documented validator invocation is unusable.
   - **Smallest repair:** Preserve or explicitly version legacy schema semantics, synchronize approved hashes only after the compatibility decision, intentionally reconcile the immutable renderer oracle, make local-reference checking strip JSON fragments, and make the validator CLI extract the canonical frontier from the documented report wrapper (or change the documented input and fixture coherently). Rerun the entire stated command set.

6. **Medium — runtime/oracle source is not placed in the randomized controller-private workspace.**
   - **File/line:** `tests/skill_product/gauntlet/run_acceptance.py:29-32`, `84-106`, `124-143`; design `docs/superpowers/specs/2026-07-19-exhaustive-surface-gauntlet-design.md:102-108,455-475`.
   - **Evidence:** `prepare` creates a randomized controller directory for copied skills/workspace/product, but starts `APP/server.py` directly from the repository and loads `ORACLE`/`DEFECTS` from fixed repository paths during finalize. The manifest records that repository server path. The design requires server source and oracle to remain in a controller-private randomized workspace. Procedural prohibitions still exist and the native evidence shows no oracle use, so this is an isolation-instrument conformance issue—not evidence that either subject cheated.
   - **Impact:** The intended obscurity boundary is weaker than documented, and the operational manifest reveals a path into the forbidden test tree.
   - **Smallest repair:** Copy the server fixture and oracle into separate randomized controller-private subtrees, execute/compare only from those copies, and omit original repository paths from agent-visible operational inputs. Retain the explicit `filesystem_containment: NOT_PROVEN` disclosure.

## Behavioral acceptance decision

**The current branch may not claim behavioral acceptance.** Both required native modes completed and each authoritative frozen result is `FAIL`; available dispatch means neither can be waived as `NOT_PROVEN`, and the design forbids aggregating discoveries across runs.

- **Runtime-only:** one genuine A-class execution miss remains. The admin/mobile Invite control was found but recorded as sampled with zero attempts instead of directly exercised. That alone prevents the individual runtime-only `PASS`.
- **Runtime-only comparator-only classifications:** the context-menu control-type variant, invalid/create/reload state variants, and four defect effect/lineage variants are normalization/alias defects; they are not additional product misses. Provider-managed profile editing and stale-session false success are supported extra discoveries, not failures to discover the product.
- **Full-evidence:** no A-class surface/control miss and no B-class canonical-proof miss was established. The subject produced 237 rows, `closed_multi_source`, all six seeded defects, and the promised-but-missing cancellation path. The frozen comparator read zero rows because it only projected `source_ledger.path_frontier`, while this current-run artifact used the instruction-required top-level frontier. Remaining aliases are comparator-normalization defects. The stale Create and stale Invite findings are supported extra discoveries. Nevertheless, the authoritative result remains `FAIL`, so full-evidence acceptance also was not achieved.
- **Product verdict:** the fixture's `NOT READY` verdict is expected and does not itself fail Gauntlet acceptance; acceptance concerns discovery, execution, evidence, and honest closure.

## MUST traceability

| Requirement cluster | Code/test/evidence mapping | Review result |
|---|---|---|
| One controlled development-only Gauntlet; no installed fixture | `tests/skill_product/gauntlet/`; `tests/skill_product/test_four_skill_boundary.py`; parity/four-skill tests passed | Conforms |
| Standard-library localhost app, deterministic seed/time, random port, health/reset, no external calls, bounded writes | `gauntlet/app/server.py:1-232`; `test_gauntlet_fixture.py:66-143`; fixture suite passed | Conforms, except controller-private copy in finding 6 |
| Eighteen material adversarial cases with legitimate hooks and explicit decoys | `gauntlet/oracle/surface-oracle.json`; `test_gauntlet_oracle.py:46-69`; `test_gauntlet_fixture.py:137-244`; focused suite passed | Conforms |
| Runtime-only versus sanitized full-evidence inputs; oracle absent; exact four skills | `run_acceptance.py:71-145`; `prompts/runtime-only.md`; `prompts/full-evidence.md`; `test_gauntlet_acceptance.py:85-135,203-224`; retained manifests | Procedural mode split conforms; controller-private boundary does not (finding 6) |
| Prepare/finalize/cleanup lifecycle; no agent/provider launch; idempotent cleanup; stable status mapping; atomic final result | `run_acceptance.py:71-292`; `acceptance_result.py`; `test_gauntlet_acceptance.py:136-182`; focused tests passed | Lifecycle mechanics conform; final artifact authority does not (findings 1-2) |
| State-appropriate bounded evidence export and redaction without mutating authority | `redact_evidence.py`; `test_gauntlet_acceptance.py:183-202`; retained hashes match the summary's agent-evidence artifact hashes | Conforms for tested export paths; no PASS export exists because no mode passed |
| One canonical `path_frontier`, five row kinds, lineage, observations, versions, discovery passes, reconciliation, counts, finding lineage | ledger schema `$defs` at `readiness-ledger.schema.json:608-750`; report schema `$ref` at `report-input.schema.json:2-11`; `test_frontier_contract.py`; `test_exhaustive_surface_contract.py` | Model exists; current report location/validation and legacy compatibility fail (findings 1 and 5) |
| Independent discovery families, material-state census, safe-control exercise, two zero-yield passes, no false exhaustive closure | `path-discovery-and-coverage.md:34-102`; orchestrator verifier gate; `test_exhaustive_surface_contract.py:36-260`; focused tests passed | Instruction contract conforms; executable closure gate does not (findings 1 and 4) |
| Versioned semantic keys, same-label disambiguation, authoritative derivation, aliases without duplicate hiding | `compare_agent_result.py`; `frontier_validation.py`; comparator/frontier focused tests | Does not fully conform (finding 3) |
| Oracle mode filtering, dispositions, defect lineage+effect, negative controls, unexpected-row quarantine, no cross-run aggregation | `surface-oracle.json`; `expected-defects.json`; `compare_agent_result.py:187-292`; `test_gauntlet_comparator.py`; focused tests passed | Core oracle rules conform; comparator authority/normalization gaps remain (findings 1 and 3) |
| Canonical closure vocabulary and separation from readiness | skill references and renderer; `test_gauntlet_report.py`; `test_exhaustive_surface_contract.py` | Presentation conforms; validator derivation does not (finding 4) |
| Action-first HTML, exact counts, compact feature rows, five bounded details, no default JS, large-manifest link, legacy fallback | `render_report.py:138-331,476`; `test_gauntlet_report.py:39-115`; focused and direct renderer suites passed | Feature behavior conforms; broad immutable legacy oracle remains red (finding 5) |
| Deterministic offline continuous suite plus two independent native release modes | focused 100/100; retained agents `runtime_confirm_63b01f8` and `full_confirm_63b01f8`; complete discovery 171 tests with five errors/failures | Release gate unmet (finding 5); neither behavioral mode passed |
| Every run stands alone; miss/false closure refuses `PASS`; no aggregation | comparator tests include separate-run non-aggregation; both retained results are `FAIL` | Refusal observed, but false-`PASS` path remains (finding 1) |
| Installed-validator necessity gate | baseline records "not justified"; no installed validator added; repository-only validator exists | Conforms |
| One repair cycle followed by one frozen runtime and one frozen full-evidence confirmation | production/harness revision `63b01f8`; final `c807a84` changes only the frozen summary; two retained confirmations identify that revision | Conforms to updated freeze; no further repair is authorized by this review |

## Out-of-scope boundary traceability

| Boundary | Evidence | Result |
|---|---|---|
| Keep exactly four self-contained installed skills | four-skill and installed-parity tests: 16/16 shared suite passed | Preserved |
| No core package, public CLI workflow, API/service/daemon/portal/MCP/scheduler/account/credential system | complete diff contains no such production addition; `test_four_skill_boundary.py` passed | Preserved |
| No general crawler/browser abstraction, automatic Playwright install, provider integration, or Claude acceptance | forbidden-behavior/source scan and direct inspection; harness launches only the local fixture process | Preserved |
| No writes to real installed skill directories | prepare copies skills into a temporary controller; parity tests passed | Preserved |
| No second ledger/report source of truth/duplicate readiness verdict | no parallel feature/control ledger added; report schema references ledger schema | Architecturally preserved, but duplicate top-level artifact wording is internally inconsistent (finding 1) |
| No raw control wall in default HTML | bounded feature/control display and manifest link in `render_report.py:274-324`; report tests passed | Preserved |
| No guarantee of unbounded theoretical action-sequence enumeration | design and workflow reference retain bounded-universe wording | Preserved |
| No installed frontier validator without necessity record | validator remains under `tests/skill_product/support`; no installed script added | Preserved |

The implementation-plan forbidden scan that rejects all `urllib.request` under the Gauntlet tree is internally inconsistent with the design's mandatory local readiness health check: `run_acceptance.py:59` uses it only against the randomized `127.0.0.1` fixture. I did not classify that mandated localhost call as an external-network or scope violation.

## Explicit NOT_PROVEN boundaries

- Filesystem containment is `NOT_PROVEN` for both native runs.
- Oracle blindness is procedural only; cryptographic or OS-level oracle isolation is `NOT_PROVEN`.
- The two single confirmations do not prove nondeterministic discovery reliability or soak-level repeatability.
- Runtime-only source/static reconciliation is intentionally not proven by that mode.
- No durable six-artifact `PASS` export exists, because neither mode passed.
- No guarantee is made or proven for unbounded theoretical action sequences outside the declared roles, fixtures, devices, states, and safety boundary.

Native dispatch, actual frontend browser path-walking, canonical object-shaped frontier production, exact current-run finding lineage, and full-evidence runtime/source reconciliation were directly evidenced; they are not listed as `NOT_PROVEN`.

# Shipworthy Behavioral Generalization, Calibration, and Simplification Implementation Plan

> **For agentic workers:** Execute directly in two coherent batches. Do not use per-task subagent development or per-task review loops. Native Codex agents are permitted only as fresh oracle-blind behavioral subjects and for the one final specification review plus one final quality review.

**Goal:** Make Shipworthy measurably more reliable across fresh agents and unfamiliar products while keeping four self-contained skills, no installed core/platform, and an equal-or-smaller installed instruction footprint after ablation.

**Architecture:** Keep all measurement machinery repository-only. A controller-private write-only runtime receipt records generic behavior without oracle identifiers; a structural behavior graph reconciles receipts, canonical report rows, and private oracle expectations. Parameterized Gauntlet twins and one structurally different holdout test sensitivity and generalization. Production changes are limited to evidence-backed wording compression and a bounded, action-first HTML coverage-confidence summary.

**Tech stack:** Python 3.11+ standard library, JSON/JSON Schema, deterministic localhost HTTP fixtures, dependency-free HTML/CSS/JavaScript, direct `unittest`, native Codex macOS agents. No external packages or external network behavior.

**Starting point:** `4651c8d1cd006230788d0d37f0e3fc312e5fbe48` on predecessor branch `codex/exhaustive-surface-gauntlet`. Its final reviews and red verification are historical benchmark facts, not a passing baseline.

**Compaction rule:** After any context compaction, reread this entire plan before continuing.

---

## Non-negotiable release rules

- Preserve exactly four installed skills and their names, activation contracts, installer behavior, and mandatory HTML report.
- No installed validator, package, CLI, browser, crawler, persistence, API, database, daemon, portal, MCP, provider integration, or real installed-copy write.
- The official gate is categorical: discovery, execution, defect detection, evidence integrity, closure honesty, and artifact validity must each pass. Aggregate percentages are diagnostic only.
- Valid extra discoveries never reduce recall and do not fail automatically. Unsupported findings are measured as false positives.
- Never aggregate separate native runs into one pass.
- Allow at most one generalized skill repair after final threshold evaluation. No fixture-label, route, or oracle-specific skill wording.
- After the complete change: one independent specification review, repair its findings; one independent quality review, repair its findings; one final verification suite; stop.
- Do not push.

## File map

Repository-only measurement:

- `tests/skill_product/gauntlet/benchmark-v1.json` — frozen predecessor revision, hashes, and authoritative results.
- `tests/skill_product/gauntlet/runtime_receipt.py` — bounded receipt model, validation, digest, and reset epochs.
- `tests/skill_product/gauntlet/receipt.schema.json` — closed receipt contract without oracle identifiers.
- `tests/skill_product/gauntlet/behavior_graph.py` — Unicode-safe normalization and structural matching.
- `tests/skill_product/gauntlet/diagnostics.py` — A/B/C/D/E classification and four diagnostic dimensions.
- `tests/skill_product/gauntlet/reliability.py` — per-run metrics and median/worst-case summary; never aggregates evidence.
- `tests/skill_product/gauntlet/app/variants.json` — four single-delta counterfactual pairs.
- `tests/skill_product/holdout/` — bounded non-dashboard micro-application, private oracle, prompt, and fixture.
- Modify `tests/skill_product/gauntlet/app/server.py`, `app.js`, and `run_acceptance.py` for controller-private receipt collection and parameterized variants.
- Modify `tests/skill_product/gauntlet/compare_agent_result.py`, `acceptance_result.py`, `acceptance-result.schema.json`, and `redact_evidence.py` so finalization is authoritative and exports cannot relabel failures.
- Add focused tests: `test_behavior_receipts.py`, `test_behavior_graph.py`, `test_counterfactual_twins.py`, `test_holdout.py`, `test_reliability.py`.

Potential installed changes, only after blind baseline and ablation evidence:

- `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/evidence-state.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/lane-prompts.md`
- `plugins/shipworthy/skills/ship-product-workflows/SKILL.md`
- `plugins/shipworthy/skills/ship-product-workflows/references/path-discovery-and-coverage.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/render_report.py`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/visual-html-report.md`
- `plugins/shipworthy/skills/ship-readiness-orchestrator/references/final-report-contract.md`

Evidence:

- `docs/phase0/evidence/behavioral-generalization/benchmark-v1.md`
- `docs/phase0/evidence/behavioral-generalization/holdout-baseline.md`
- `docs/phase0/evidence/behavioral-generalization/ablation.md`
- `docs/phase0/evidence/behavioral-generalization/final-reliability.md`
- `docs/phase0/evidence/behavioral-generalization/final-spec-review.md`
- `docs/phase0/evidence/behavioral-generalization/final-quality-review.md`

---

## Batch 1 — Trustworthy behavioral measurement

### Task 1: Freeze benchmark v1 and repair the authority boundary

- [ ] Record immutable hashes for the v1 fixture, oracle, predecessor evidence, starting revision, and known authoritative `FAIL` results. Define discovery, execution, defect-detection, and evidence-integrity metrics separately.
- [ ] Write RED tests proving: nonempty but schema-invalid artifacts cannot pass; ledger/report frontier or finding divergence cannot pass; incomplete closure cannot pass; nonexistent evidence cannot pass; a `FAIL` run cannot be exported as `PASS`; top-level versus `source_ledger` ambiguity is rejected rather than guessed.
- [ ] Align one report-input representation across schema, renderer, finalizer, and skill contract while retaining explicitly versioned legacy read compatibility.
- [ ] Validate both JSON artifacts, canonical frontier invariants, evidence references, HTML closure, exact finding lineage, cleanup result, and acceptance-result schema before atomic final status.
- [ ] Repair predecessor-suite compatibility failures intentionally: schema-version behavior, local `$ref` fragments, renderer oracle decision, and documented frontier-validator wrapper input.
- [ ] Run focused authority tests, full skill-product discovery, and all direct legacy suites. Commit only when the benchmark and authority boundary are reproducibly frozen.

### Task 2: Private runtime action receipts

- [ ] Write RED tests for deterministic bounded receipts, reset epochs, write-only behavior, path containment, secret/oracle-field rejection, and no external network.
- [ ] Copy the fixture server into the randomized controller-private area. Keep coordinator state and receipt outside agent-visible/allowlisted paths; expose only an agent evidence directory for writes.
- [ ] Instrument generic route, role, viewport, activation, input mechanism, spawned-surface, transition, reload/re-entry, blocked, and avoided events. Use behavior descriptors only—never oracle IDs or expected verdicts.
- [ ] Make receipt reading impossible over HTTP; reset creates a new epoch without erasing prior controller evidence. Cap event count, field lengths, file size, and diagnostics.
- [ ] Add finalizer checks that reported execution claims require a matching private receipt; semantically equivalent real actions remain matchable.
- [ ] Prove the prompt, DOM, URLs, fixture data, agent-visible manifest, and copied skills contain no receipt path, oracle identity, or expected defect answer.

### Task 3: Behavioral graph comparison and A/B/C/D/E diagnostics

- [ ] Write RED tests for NFKC/casefold Unicode letters and numbers, percent-decoded per-segment routes, role/state/viewport normalization, control-type/input equivalence, disambiguating behavior, transition matching, ambiguity, and supplied-key mismatch.
- [ ] Build one structural graph representation shared by oracle, receipt, report, and repository validator. Exact semantic keys win; unique structural equivalence is accepted; ambiguous matches become `REVIEW_REQUIRED`.
- [ ] Enforce action receipts and evidence class/minima. A safe covered control needs an actual receipt; blocked/avoided actions need the matching observed inventory/safety event and reason.
- [ ] Classify every discrepancy: A discovery miss, B execution/proof/lineage failure, C deterministic comparator defect, D valid extra, or E unsupported/false-positive finding.
- [ ] Keep D out of recall denominators and automatic failure. Measure E separately. Replace route-wide suppression with exact structural supporting identities.
- [ ] Require strict categorical acceptance while emitting per-dimension counts and diagnostic percentages.

### Task 4: Four parameterized counterfactual twin pairs

- [ ] Write RED tests proving each variant changes exactly one declared behavior and resets deterministically.
- [ ] Add no more than four pairs in `variants.json`: persistence, disabled-control recovery, keyboard command existence, and truthful failure feedback.
- [ ] Prove receipt deltas are limited to the declared behavior and do not leak variant truth to visible labels, routes, or prompts.
- [ ] Add comparator tests where defective twins require the relevant finding and corrected twins reject it as E; path presence follows actual existence; unrelated wording may differ.
- [ ] Run one oracle-blind native paired evaluation per pair using randomized opaque variant labels. Keep every pair independent and preserve individual results.

**Batch 1 checkpoint:** Focused receipt/graph/twin tests and the complete deterministic suite must pass before the holdout baseline. No production skill wording changes are allowed in Batch 1.

---

## Batch 2 — Generalization, reliability, and compression

### Task 5: Blind holdout micro-application and frozen baseline

- [ ] Build a small non-dashboard multi-step application with branching onboarding, back/cancel/recovery, delayed failure, mid-session permission change, re-entry behavior, and one non-pointer action. Keep server and client bounded and standard-library-only.
- [ ] Store its oracle and controller receipt outside the agent allowlist. Add isolation, deterministic reset, and oracle-traceability tests.
- [ ] Materialize the exact starting-revision (`4651c8d`) production skill tree into a temporary controller copy and launch one fresh oracle-blind runtime-only native subject. Preserve its individual baseline result before evaluating any later production-tree change.
- [ ] Classify misses only by generalized category. Do not place holdout names, routes, labels, or fixture details in production instructions.

### Task 6: Calibration runs and reliability metrics

- [ ] Write RED tests for per-run scoring, median/worst-case calculation, artifact-integrity rate, false-closure rate, false-positive rate, cost bounds, and rejection of cross-run evidence aggregation.
- [ ] Record discovery recall, execution recall, release-blocking defect recall, evidence integrity, closure honesty, E findings, duration, attempts, and artifact bytes independently for each run.
- [ ] Use focused native calibration runs only when they answer a specific uncertainty. They are not final evidence and cannot be merged.

### Task 7: Instruction ablation and simplification

- [ ] Measure the pre-ablation installed byte/word/line footprint for all four skills and references.
- [ ] Select at most three repetitive Gauntlet-era blocks: canonical artifact/lineage checks, repeated control-census/reconciliation wording, and repeated verifier closure rules.
- [ ] For each candidate, create one temporary skill copy, remove or consolidate one block, run deterministic contracts, and perform at most one paired native comparison when deterministic proof is insufficient.
- [ ] Permanently keep only simplifications that preserve discovery, execution, defect detection, evidence integrity, and honest closure. Do not compensate for stochastic variation with new wording.
- [ ] Require final installed footprint to be equal to or smaller than pre-ablation unless one specifically evidenced safety addition is unavoidable and documented.

### Task 8: Human coverage-confidence summary

- [ ] Write RED renderer tests for a short early summary of tested/not-tested scope, roles/states/viewports, stop reason, closure, and inferred/blocked/avoided/NOT_PROVEN claims.
- [ ] Render only derived canonical data; preserve action-first findings, deterministic escaping, no JavaScript/external resources, and collapsed/bounded frontier details.
- [ ] Visually inspect desktop and narrow/print renderings. Do not redesign the report.

---

## Final frozen evaluation

- [ ] Commit a clean evaluation revision after Tasks 5–8. No skill or harness edit is allowed during its first evaluation set.
- [ ] Run five fresh independent oracle-blind runtime-only Gauntlet subjects on that same revision. Never aggregate their evidence.
- [ ] Run the deterministic twin suite, one oracle-blind holdout run, and one full-evidence Gauntlet run on the same revision.
- [ ] Require: zero false exhaustive closures; median discovery recall at least 90%; no run below 80%; every release-blocking seeded defect in every run; artifact integrity 5/5.
- [ ] If any threshold misses, permit one generalized repair cycle only. First add focused RED tests, make no fixture-specific skill change, commit, then rerun every affected final acceptance artifact. Stop after that rerun regardless of result.

## Final review and verification

- [ ] Dispatch one fresh native Codex specification reviewer across the complete diff and final evidence. Repair genuine findings directly with focused RED/GREEN tests; do not run another spec-review loop.
- [ ] Dispatch one fresh native Codex quality reviewer after specification repairs. Repair genuine findings directly with focused RED/GREEN tests; do not run another quality-review loop.
- [ ] Run the final suite once: all focused new tests; full `tests/skill_product` discovery; direct legacy 139/174/22/17 suites; compile; parity/four-skill/stdlib; frontier validation; `git diff --check`; forbidden-behavior scans; cache/build-noise cleanup.
- [ ] Record exact production and repository-only files, installed size before/after, removed/compressed blocks, all five runs and median/worst metrics, false closure, release-blocker recall, twins, holdout baseline/final, artifact integrity, D/E classifications, HTML readability, review findings/repairs, proof and NOT_PROVEN boundaries, stop reason, and four-skill/no-core confirmation.
- [ ] Commit final verified evidence locally. Do not push. Mark the goal complete only after the requested stop condition is reached; a completed process must not be mislabeled as passing acceptance.

## Completion record

All planned tasks, the single permitted generalized repair cycle, one
independent specification review, one independent quality review, and the one
final verification pass were executed. Deterministic contracts are green, but
behavioral release acceptance is **FAIL**: the retained five repaired runs had
47.06% median and 5.88% worst material discovery recall, 0% canonical defect
recall, and 5/5 false exhaustive closures. Corrected execution recall and
machine-bound same-revision identity for those historical retained runs are
NOT_PROVEN. Work stops here by design rather than opening another tuning loop.

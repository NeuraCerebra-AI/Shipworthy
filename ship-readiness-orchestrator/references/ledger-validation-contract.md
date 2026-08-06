# Ledger Validation Contract

Use the schema JSON as structural authority before structured render or import:

- `schemas/readiness-ledger.schema.json` for `shipworthy/readiness-ledger`.
- `schemas/report-input.schema.json` for `shipworthy/readiness-report-input`.
- `schemas/browser-evidence-envelope.schema.json` for a normalized browser envelope.

Read the complete input once, cap it at 16 MiB, 100,000 aggregate values, 1,024
artifacts, and 512 findings, and stop on excessive nesting, malformed JSON, an
unknown schema name/version, unsupported schema behavior, or a non-local schema
reference. Apply every declared constraint; do not add permissive defaults or
silently discard extra fields. Version `1.1` is required for current full runs;
version `1.0` remains readable only as an explicitly historical import.

Final shapes differ: `readiness-ledger.json` is the canonical ledger with
top-level `path_frontier`; `report-input.json` is the closed 1.1 wrapper whose
`source_ledger` is structurally identical. Do not add sibling frontier or
checkpoint fields to that wrapper.

For an operational frontier report, store the human-auditable checkpoint as
`orchestration-checkpoint.json` in the directory containing `report-input.json`.
It records the human target name, actual lanes, execution mode, authorization, frontend path-walk,
verifier, omissions, ledger/evidence locations, audit/goal state, raw outputs,
control census, active evidence-debt work, browser failover, and exhaustion
status without changing the frozen 1.1 wrapper. Missing or contradictory
checkpoint data is a render failure, not an invitation to synthesize
orchestration claims.

```json
{
  "target_name": "Human product name",
  "target_intent": "production_product or benchmark_fixture",
  "lanes": ["runtime — completed — evidence/runtime.txt", "verifier — approved — evidence/verifier.txt"],
  "mode": "authorized native agents or sequential fallback",
  "multi_agent_authorization": "explicitly authorized, denied, unavailable, or not received",
  "frontend_path_walk_performed": true,
  "frontend_tool": "actual tool",
  "runtime_target": "actual local target",
  "path_walk_status": "full, partial, blocked, or not_performed",
  "verifier": "approved, rejected, or not run",
  "omitted": [],
  "ledger_path": "readiness-ledger.json",
  "evidence_locations": ["evidence/"],
  "exhaustion_status": "exact canonical coverage qualification",
  "audit_status": "active | complete | blocked | user_stopped",
  "goal_mode_status": "active | unavailable | not_authorized | failed | goal_equivalent",
  "goal_completion_status": "active | complete | blocked | user_stopped | not_applicable",
  "raw_lane_output_paths": ["evidence/raw-runtime.json"],
  "raw_verifier_output_paths": ["evidence/raw-verifier.json"],
  "control_census_paths": ["evidence/runtime-control-census.json", "evidence/static-control-census.json"],
  "zero_yield_pass_ids": ["PASS-11", "PASS-12"],
  "evidence_debt_actions": [],
  "recovery_status": "not_needed | active | succeeded | blocked | user_stopped",
  "recovery_attempts": [],
  "recovery_receipt_paths": [],
  "browser_failover_status": "not_needed | active | succeeded | blocked | user_stopped",
  "browser_failover_receipt_paths": [],
  "validation_state": "collecting | synthesizing | validating | repairing | complete | blocked",
  "validation_attempts": [],
  "validation_repair_queue_path": "validation-repair.json",
  "validation_completion_receipt_path": "validation-completion.json"
}
```

For `target_intent: benchmark_fixture` with `run_scope: full`, also retain
`benchmark_preflight` with `status: clean`, a non-empty `baseline_revision`,
optional `baseline_tag`, empty `porcelain_entries` and `generated_artifacts`,
and `evidence_external: true`. Any dirty entry aborts exploration. This
benchmark-only rule permits a blocked, not-performed checkpoint to render the
mandatory abort report; it does not permit benchmark results and does not
reject an ordinary product audit merely because its user worktree is dirty.

For `run_scope: full`, the checkpoint is a non-waivable completion contract:
retain three distinct `verified_wave_ids` and one approved independent
certificate per wave; retain raw lane and verifier packets; and retain an
apparent-affordance census that classifies action-signalling non-controls.
Every raw discovery must reconcile to a frontier row, finding lineage, or an
explicit evidence-backed rejection/out-of-scope disposition. Every covered
material control and transition must have an exact visible execution receipt
for route, role, state, viewport, containing surface, control identity/type,
input mechanism, and before/after state. Each material control receipt also
declares `backend_effect_expected` and a non-empty reason. A backend-effecting
control owns one nested `backend_correlation` whose overall status is
`matched`, `mismatch`, or `blocked` and whose `network`, `logs`, `state`, and
`reentry` channels each explicitly say `observed`, `blocked`, or
`not_applicable`; it also records boolean state-change/persistence expectations
and UI feedback as `success`, `failure`, or `none`. A presentational control may
use overall `not_applicable`.
Transition receipts preserve transition lineage without duplicating the
control's correlation. Closure receipts must resolve to a
retained operational source path; a report builder cannot originate closure.
Positive recent discovery yield, an omitted gate disclosure, strong early
findings, or a small target cannot produce complete status. Missing paths that
are promised but proven absent are `missing` findings, not indefinite debt.

Before execution, freeze declared, static, and runtime candidate inventories
under `path_frontier.candidate_inventories`. Each inventory retains its
canonical method family, role/state/viewport/fixture coordinates, source
locator, independently retained raw source artifacts/digests, candidate digest,
raw locators, and exact candidate-to-row mapping or difference. Its canonical
JSON extract must parse to exactly the embedded candidates; each candidate
cites a resolving raw source artifact, and different required method families
cannot reuse the same raw source as independence proof. A full closed frontier
requires declared, runtime-structural, and static inventories whose mapped union
equals the frontier. A census copied from frontier keys, a manifest reused as
source, or an unmapped candidate fails validation.

For the Raw-Evidence-to-Ledger Reconciliation Gate, first enforce the
**Original-Evidence Closure Gate**. Each retained lane/verifier packet must be
captured before frontier or finding synthesis with `capture_phase:
pre_synthesis`, its own `artifact_path`, and `observations` plus
`execution_receipts` arrays. Original observations must not be reconstructed
from frontier rows, findings, the ledger, checkpoint, report input, or HTML.
They carry no terminal disposition and no downstream `PF-*`/`FND-*` identity;
either condition is circular provenance and fails validation.

The ledger remains a draft until every original observation and execution
receipt matches the ledger one-to-one and every material raw observation has
exactly one terminal disposition. Original fields remain unchanged during
synthesis. A material before/after receipt requires exact transition lineage.
Missing, invented, changed, or circular records fail closure; verifier
approval, completed waves, zero-yield passes, and non-complete audit status do
not waive this check.

For backend correlation, `matched` requires bounded runtime backend proof.
Observed channels require safe evidence references. Log proof records a source,
non-negative byte offsets no more than 1 MiB apart, and correlated error count;
network proof records method, redacted path, response status, and expected and
actual request counts; state proof records before/after; persistence
additionally requires agreeing reload/re-entry proof.
Success with a failed or duplicate mutation, unchanged expected state,
correlated unhandled error, or failed re-entry cannot be `matched`. A
`mismatch` requires finding lineage. A `blocked` channel stays NOT_PROVEN and
must carry a reason; an overall `blocked` correlation cannot support closed
coverage, while `matched` may retain a blocked non-required channel when other
runtime proof supports the action claim. Reject secrets, headers, cookies,
tokens, bodies, personal data, and raw/unbounded log content.

For a current full run, checkpoint validation state is `collecting`,
`synthesizing`, `validating`, `repairing`, `complete`, or `blocked`, with at
most three bounded `validation_attempts`. Final validation also enforces
receipt/census-to-original reconciliation across execution receipts,
runtime/static control censuses, and action-signalling affordances. A failure
produces `validation-repair.json`, a bounded machine-readable repair queue
containing the failed gate, problem, and required action. The controller repairs
the cited artifact or re-exercises the path, returns the state to `validating`,
and reruns the renderer. The third failure requires blocked status and explicit
evidence debt.

Only `scripts/render_report.py` may move validation from `validating` to
`complete`. It writes `validation-completion.json`, a renderer-issued completion
receipt binding digests for report input, checkpoint, original packets, and
HTML. A completed validation state without a matching receipt and digest fails
closed; modifying any bound artifact invalidates that completion.

Retain its stable observation ID, source kind, evidence references, semantic
key, and behavioral identity. Compare route, role, state, viewport, containing
surface, control identity/type, input mechanism, and before/after state; reject
a wrong semantic variant even when its label is similar. Every retained
execution receipt and action-signalling affordance must resolve through the raw
discovery set into the frontier or an explicit disposition. Repeated events may
deduplicate only when their complete behavioral identity agrees. Independently
fixable effects require distinct finding lineage. Rejected and out-of-scope
records require linked observation IDs, reason, and evidence. Material
observations must not silently disappear. When raw evidence proves the ledger
wrong, increment its revision and renew verifier approval; otherwise preserve
the gap as evidence debt and keep closure incomplete. An incomplete or blocked
full run remains renderable only after this accounting succeeds; those statuses
cannot bypass reconciliation.

Actionable records carry an observed behavior, user consequence, concrete
smallest safe fix, exact verification step, evidence references, and canonical
behavioral lineage. Visual records additionally require exact viewport and
target state, reproduction steps, retained screenshot/geometry proof, a
separate source mechanism, and fresh disconfirmation. Passed/Keep records say
what to preserve and the regression guard; they never carry corrective text.
The target intent and calibration are retained in the checkpoint so fixture
scope limits are not silently promoted to production release blockers.

Each recovery summary and receipt is bounded and linked by a stable recovery ID.
It records the failed capability/binding, cleanup, continuity checks, one
transient retry, each alternative method and binding, inventory refresh,
resumed wave/paths, remaining debt, and fresh verifier identity or verifier
debt. Aggregate precedence is `user_stopped`, `active`, `blocked`, `succeeded`,
then `not_needed`. A recovered ladder may contain failed candidates without
becoming blocked. A newly available applicable safe authorized method makes
recovery active rather than exhausted. Required overflow uses ordered
continuation receipts; truncation cannot prove exhaustion.

Each control-census file is supporting bounded JSON containing `method_family`,
`semantic_keys`, the computed control `digest`, the computed full
`frontier_digest`, and `unmatched_controls`. A complete audit requires the
runtime-structural and static-implementation census union to equal the
frontier controls, with no unmatched controls. The `zero_yield_pass_ids` must
name the last two qualifying discovery passes from distinct canonical method
families. Control-census equality cannot replace candidate-inventory
reconciliation and receives no omission-proof credit on its own. Every current
full run requires the mapped source-candidate union to equal the canonical
frontier, even when the terminal audit is blocked or user-stopped; only closed
multi-source coverage additionally requires all three independent source
families.

Every canonical evidence-debt row has exactly one `evidence_debt_actions` row
with `next_action`, `alternate_method`, `attempt_count`, `last_blocker`, and
`disposition`; a debt row that remains in the ledger cannot be labeled
`resolved`. When present, raw lane/verifier paths and census paths are safe
relative, existing, non-empty files. They may be empty for a truthful early
`active`, `blocked`, or `user_stopped` checkpoint before that work could run,
but a complete audit requires all three groups. When browser failover was
needed, each path in
`browser_failover_receipt_paths` resolves to bounded JSON naming the native
error, cleanup result, fallback kind, independent process/context identifier,
isolation proof, fallback result, and remaining evidence debt. Same-binding
`tab.playwright` is not independent Playwright; successful isolation proof
must positively identify a separate, independent, or isolated process,
context, or profile and must not describe it as same, shared, reused, or
attached. Validate each receipt by its own fallback result; a mixed history is
globally `blocked` when any retained receipt preserves unresolved debt.

`goal_mode_status` describes goal availability; it does not claim completion.
Keep audit lifecycle, frontier finality/qualification, and release disposition
separate. `active` requires an incomplete ledger and `finality: open` with named
remaining work. `blocked` requires an incomplete ledger and exhausted finality;
`user_stopped` requires an incomplete ledger but may retain open finality and
named remaining work. Exhausted finality forbids nonterminal material rows. `audit_status: complete`
requires a complete ledger and exhausted frontier but may conclude
`not_ready`. A confirmed approved P0 always forces `not_ready`, even if
unrelated evidence debt exists. `cannot_determine` is permitted only when no
confirmed P0 already proves a no-go; blocked/user-stopped without it must use
`cannot_determine`. `ready` and `conditionally_ready` require every material
row covered in complete, exhausted, closed-multi-source coverage with no debt.

`goal_completion_status: complete` is valid only when `audit_status: complete`
and all ledger, frontier, census, verifier, frontend, raw-evidence, zero-yield,
recovery, and browser-failover gates agree. The orchestrator must not mark the persistent
goal complete before the renderer accepts that state. Honest `active`,
`blocked`, and `user_stopped` checkpoints remain renderable and visibly report
the constrained qualification and release decision separately.

`scripts/make_bundle.py` retains the validated checkpoint, canonical ledger,
raw lane/verifier outputs, census files, recovery receipts, and browser receipt files by default;
callers do not need to repeat those paths with `--include`.

After structural validation, check identity uniqueness and every cross-reference:
finding artifact IDs must resolve, lineage source IDs must name declared inputs,
and the gate, completion status, evidence debt, and readiness disposition must
agree. Preserve the declared producer and lineage through projection. Missing,
external, or unverifiable material stays evidence debt and cannot raise the
proof ceiling, confidence, verifier status, or readiness disposition.
Every evidence reference is a safe relative path to an existing non-empty file
under the evidence output, with only an optional fragment suffix. Each non-intent
frontier row names the correct immediate parent, and its semantic key is derived
mechanically from that parent under `shipworthy-semantic-v1`.
Discovery pass digests form a continuous source-backed chain. Closed
multi-source reports end with two qualifying zero-yield passes from distinct
canonical method families; both reference retained inventories/evidence, add no
candidate IDs, and end at the combined candidate-inventory digest. Compute each
candidate digest from its canonical candidate objects and bind it to the raw
artifact SHA-256; do not infer exhaustion from the frontier digest alone.

Treat `scripts/render_report.py` as the final fail-closed gate. Render only the
validated post-transform ledger/report input. Invalid canonical input must not be rendered. On failure, retain
the source unchanged, report a bounded field path and reason, and request a
corrected or explicitly mapped input. Validation never authorizes execution,
remote retrieval, or mutation of the audited target.

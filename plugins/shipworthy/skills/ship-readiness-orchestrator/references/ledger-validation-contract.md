# Ledger Validation Contract

Use the schema JSON as structural authority before structured render or import:

- `schemas/readiness-ledger.schema.json` for `shipworthy/readiness-ledger`.
- `schemas/report-input.schema.json` for `shipworthy/readiness-report-input`.
- `schemas/browser-evidence-envelope.schema.json` for a normalized browser envelope.

Read the complete input once, cap it at 16 MiB, 100,000 aggregate values, 1,024
artifacts, and 512 findings, and stop on excessive nesting, malformed JSON, an
unknown schema name/version, unsupported schema behavior, or a non-local schema
reference. Apply every declared constraint; do not add permissive defaults or
silently discard extra fields. Version `1.0` is the supported structured ledger
and report-input version.

Final shapes differ: `readiness-ledger.json` is the canonical ledger with
top-level `path_frontier`; `report-input.json` is the closed 1.0 wrapper whose
`source_ledger` is structurally identical. Do not add sibling frontier or
checkpoint fields to that wrapper.

For an operational frontier report, store the human-auditable checkpoint as
`orchestration-checkpoint.json` in the directory containing `report-input.json`.
It records the human target name, actual lanes, execution mode, authorization, frontend path-walk,
verifier, omissions, ledger/evidence locations, audit/goal state, raw outputs,
control census, active evidence-debt work, browser failover, and exhaustion
status without changing the frozen 1.0 wrapper. Missing or contradictory
checkpoint data is a render failure, not an invitation to synthesize
orchestration claims.

```json
{
  "target_name": "Human product name",
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
  "exhaustion_status": "exact canonical closure state",
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
  "browser_failover_receipt_paths": []
}
```

For `run_scope: full`, the checkpoint is a non-waivable completion contract:
retain three distinct `verified_wave_ids` and one approved independent
certificate per wave; retain raw lane and verifier packets; and retain an
apparent-affordance census that classifies action-signalling non-controls.
Every raw discovery must reconcile to a frontier row, finding lineage, or an
explicit evidence-backed rejection/out-of-scope disposition. Every covered
material control and transition must have an exact visible execution receipt
for route, role, state, viewport, containing surface, control identity/type,
input mechanism, and before/after state. Closure receipts must resolve to a
retained operational source path; a report builder cannot originate closure.
Positive recent discovery yield, an omitted gate disclosure, strong early
findings, or a small target cannot produce complete status. Missing paths that
are promised but proven absent are `missing` findings, not indefinite debt.

For the Raw-Evidence-to-Ledger Reconciliation Gate, the ledger remains a draft
until every material raw observation has exactly one terminal disposition.
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

Each control-census file is bounded JSON containing `method_family`,
`semantic_keys`, the computed control `digest`, the computed full
`frontier_digest`, and `unmatched_controls`. A complete audit requires the
runtime-structural and static-implementation census union to equal the
frontier controls, with no unmatched controls. The `zero_yield_pass_ids` must
name the last two qualifying discovery passes from distinct canonical method
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
`goal_completion_status: complete` is valid only when `audit_status: complete`
and all ledger, frontier, census, verifier, frontend, raw-evidence, zero-yield,
recovery, and browser-failover gates agree. The orchestrator must not mark the persistent
goal complete before the renderer accepts that state. Honest `active`,
`blocked`, and `user_stopped` checkpoints remain renderable and visibly report
that closure was not achieved.

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
Discovery pass digests form a continuous chain. Closed multi-source reports end
with two qualifying zero-yield passes from distinct canonical method families
whose digest equals the computed frontier digest.
Compute that digest as SHA-256 of the UTF-8 compact JSON array of all sorted
`semantic_key` strings (`ensure_ascii=false`, separators `,` and `:`).

Treat `scripts/render_report.py` as the final fail-closed gate. Render only the
validated post-transform ledger/report input. Invalid canonical input must not be rendered. On failure, retain
the source unchanged, report a bounded field path and reason, and request a
corrected or explicitly mapped input. Validation never authorizes execution,
remote retrieval, or mutation of the audited target.

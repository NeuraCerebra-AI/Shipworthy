# Visual HTML readiness report (mandatory for Shipworthy)

The audit already produces structured data — the coverage matrix and the finding
ledger. `scripts/render_report.py` turns compact ledger JSON into **one
self-contained HTML report** in the Shipworthy design system: masthead, verdict
stamp, stats chips, a coverage bar with a **covered-percentage** summary,
findings **grouped by action** (Clear Before Ship / Fix Next / Not Proven / Not
Tested / Passed / Keep, each with a count), action chips, proof chips,
collapsible Evidence / Fix / Verify details, and the
orchestration checkpoint. It **prints cleanly to PDF** (a light print stylesheet
keeps findings whole) and is **accessible** (the coverage bar carries an
`aria-label`; each segment has a `title`). The output is a single file: inline
CSS, system fonts, **no network calls and no JavaScript by default** — so it
opens offline, renders consistently in browsers and `wkhtmltopdf`, and prints
cleanly.

## Migration decision

The preferred visual direction came from a stronger hand-authored report style:
compact premium dark layout, clearer Shipworthy masthead, rotated verdict stamp,
stats chips, coverage legend, action-first finding sections, numbered finding
cards, action/proof pills, and collapsible Evidence / Fix / Verify rows. Those traits are
the template target.

The older renderer remains the operational model: JSON-driven, deterministic,
small, escaped, partial-data tolerant, self-contained, and simulation-tested. Do
not import the hand-authored report's Google Fonts dependency or make agents
write HTML prose by hand. Agents emit compact ledger JSON; `render_report.py`
fills the fixed template.

## When to generate it

Only after the final claim ledger, coverage, verifier outputs, and checkpoint are
complete (i.e., after the Mandatory Flow final ledger and verifier gates). It is
a *rendering* of the canonical ledger, never a second source of truth.

Shipworthy invocation means HTML report, always. Every operational Shipworthy
invocation must produce a self-contained HTML readiness report from the final
ledger, whether the run is full flagship, conditional, static constrained,
changed-only, source/CLI-only, or downgraded. Downgrade status changes the
report contents, checkpoint, and verdict language; it does not remove the report
requirement.

The default output path is outside the audited repo so read-only target behavior
is preserved:

```text
~/.shipworthy/runs/<target-slug>/<timestamp>/readiness-report.html
```

Use a repo-local path such as `.shipworthy/reports/<timestamp>/readiness-report.html`
only when the user explicitly asks for repo artifacts.

The only normal exceptions are: the user explicitly says not to create files, or
the environment cannot write artifacts. In those cases, the final answer must
lead with `HTML report: MISSING/BLOCKED`, explain why, and mark the run
incomplete as a normal artifacted Shipworthy run.

Agents should emit compact ledger JSON only and never generate full HTML by hand.
The renderer fills a fixed template. This keeps token use low and prevents
report style drift.

## Coverage Confidence And Product Coverage

Render a short **Coverage Confidence** summary near the beginning: what was tested, what was not tested, roles/states/viewports, why testing stopped, closure, and important proof limits. Keep findings prominent. Render **Product Coverage** after the action-first finding sections with canonical closure/reason, exact counts and denominators, discovery families, and bounded feature rows.

Keep Control evidence, Role / state / device coverage, Blocked / avoided actions, Discovery reconciliation, and Frontier manifest in collapsed native `<details>`. Link bounded frontier JSON rather than dumping rows. Default rendering has no JavaScript. Escape canonical text and reject unknown closure labels or caller/row count drift.

## How to generate it

1. Serialize the completed ledger into the JSON contract below (write it next to
   the evidence, e.g. `readiness-report.json`).
2. Run:

   ```bash
   python3 scripts/render_report.py readiness-report.json readiness-report.html
   ```

   Add `--interactive` for a client-side filter/search/collapse version (opt-in
   inline JS, no network; print-safe). The mandatory default report remains
   no-JS. Other formats — SARIF, evidence bundle, merge gate — are in
   `references/exports-and-ci.md`.

   Discover a compatible runtime in this order: `python3`, then `python`, then
   Windows `py -3`. Verify `major.minor` first and require Python 3.11 or newer;
   do not run a candidate merely because the command exists. If none is
   compatible, use the **instruction-only fallback**: have the host write one
   self-contained, escaped HTML document directly from the final ledger and this
   fixed contract, with no external resources. Record deterministic script
   execution, SARIF, and bundle generation as `NOT_PROVEN`; do not omit the
   mandatory HTML report or pretend the fallback was script-rendered. The
   fallback must put `data-closure-state="<exact canonical closure_state>"` on
   the root `<html>` element so HTML and JSON closure remain mechanically
   comparable.

3. Point the user to `readiness-report.html`. Repository contributors can use
   the repository-only fixtures under `tests/`; installed skills contain no
   samples or development test data.

## JSON contract

```json
{
  "target": "string — what was audited",
  "generated_at": "YYYY-MM-DD (optional; defaults to today)",
  "verdict": "NOT READY | READY WITH RISKS | CONDITIONAL | READY",
  "summary": {
    "clear_before_ship": 0,
    "fix_next": 0,
    "not_proven_not_tested": 0,
    "passed_keep": 0
  },
  "coverage": {
    "total_paths": 0,
    "segments": [
      { "kind": "covered|sampled|blocked|avoided|inferred|missing|out_of_scope|evidence_debt",
        "label": "human label", "value": 0 }
    ]
  },
  "path_frontier": "canonical readiness-ledger path_frontier object (optional for legacy input)",
  "findings": [
    { "section": "clear_before_ship|fix_next|not_proven_not_tested|passed_keep",
      "action": "Fix|Prove|Decide|Skip|Keep",
      "proof": "Confirmed|Partial|Inferred|Not tested",
      "severity": "backward-compatible legacy alias (optional)",
      "confidence": "backward-compatible legacy proof alias (optional)",
      "title": "one line",
      "consequence": "user consequence (optional)",
      "evidence": "what was observed (optional)",
      "fix": "smallest useful fix (optional)",
      "verify": "exact verification step (optional)" }
  ],
  "checkpoint": {
    "lanes": ["ship-deep-review", "ship-product-workflows", "ship-workflow-clarity"],
    "goal_mode_status": "active | explicitly authorized | not_authorized | unavailable | goal-equivalent resumable ledger",
    "goal_mode_objective": "persistent objective or fallback ledger objective",
    "multi_agent_authorization": "explicitly authorized | denied | unavailable | not received | not required for this constrained pass",
    "frontend_path_walk_performed": true,
    "frontend_tool": "browser | in-app browser | chrome | playwright | computer-use | none | other",
    "runtime_target": "URL, app/window, or local launch target",
    "path_walk_status": "full | partial | blocked | not_performed",
    "downgrade_reason": "required when the full-run claim is downgraded",
    "report_generation_status": "rendered | blocked | failed | intentionally_not_generated_by_user_constraint",
    "report_path": "absolute path to readiness-report.html, or missing/blocked reason",
    "ledger_path": "absolute path to readiness-report.json or ledger, or inline snapshot marker",
    "evidence_locations": ["absolute paths or redacted artifact references"],
    "frontier_total": 0,
    "frontier_covered": 0,
    "frontier_sampled": 0,
    "frontier_blocked": 0,
    "frontier_missing": 0,
    "frontier_evidence_debt": 0,
    "frontier_unattempted": 0,
    "new_paths_last_wave": 0,
    "new_paths_previous_wave": 0,
    "exhaustion_status": "complete | incomplete | incomplete_budget_exhausted | downgraded",
    "exhaustion_downgrade_reason": "required when frontier closure is incomplete",
    "next_frontier_batch": ["frontier IDs or user-path names to resume next"],
    "mode": "e.g. 5 authorized parallel agents | sequential fallback",
    "verifier": "e.g. Opus → APPROVED",
    "omitted": ["gate skipped → logged as evidence debt, not passed"]
  },
  "illustrative": false
}
```

Field notes: `goal_mode_status` records whether Codex `/goal` or a platform
persistent goal was actually active; when it is unavailable or not authorized, a
goal-equivalent resumable ledger is required. Checkpoint frontend fields make
the human-style path-walk explicit.
If `frontend_path_walk_performed` is false or `path_walk_status` is
`not_performed`, the report must not claim to be a full Shipworthy run. Use
`downgrade_reason` for language such as `source/CLI/HTTP-only readiness audit is
not a full Shipworthy run`. `report_generation_status`, `report_path`,
`ledger_path`, and `evidence_locations` make the deliverable invariant auditable.
Frontier fields make exhaustion auditable: if `frontier_unattempted` is above
zero, `new_paths_last_wave` / `new_paths_previous_wave` still show discovery
yield, or `exhaustion_status` is not `complete`, the report must show the
downgrade and include a next frontier batch or resume path.
If `report_generation_status` is not `rendered`, the final answer must say
`HTML report: MISSING/BLOCKED` and treat the run as incomplete. `findings` are
sorted by action section automatically; every text field is HTML-escaped; coverage
segment widths are proportional to `value`; `verdict` selects
the banner color (rose / amber / emerald). Coverage kind aliases are normalized:
`debt` renders as `evidence_debt`, and mixed-case kinds such as `COVERED` are accepted.
Action sections are the user-facing buckets:

- `Clear Before Ship`: readiness-blocking failures, missing paths, unsafe release gaps, or proof gaps.
- `Fix Next`: real non-blocking issues to repair after blockers.
- `Not Proven / Not Tested`: evidence debt, blocked/avoided paths, hypotheses, or unverified claims; these are not passes.
- `Passed / Keep`: paths or choices that worked under the tested conditions.

Action chips are `Fix | Prove | Decide | Skip | Keep`. Proof chips are
`Confirmed | Partial | Inferred | Not tested`.

Legacy severity aliases are accepted for old ledgers: `P0 Blocker`, `critical`,
and `blocker` map to Clear Before Ship; `P1 Major`, `major`, `high`, `P2
Moderate`, `moderate`, `medium`, and `provisional` map to Fix Next; `P3 Minor`,
`minor`, `low`, `note`, `unscored`, unknown values, and `info` map to Not
Proven / Not Tested; `strong`, `working`, `passed`, and `keep` map to Passed /
Keep. Unknown `kind` values fall back safely so the report never breaks on partial data. Setting
`"illustrative": true` stamps the report as a sample rather than a live run.

## Robustness

The generator degrades gracefully rather than crashing on partial or hostile data: every text field is HTML-escaped (XSS-safe), unknown verdict/kind values fall back safely, unknown finding categories land in Not Proven / Not Tested, missing sections render a muted note, non-numeric coverage values are ignored, long unbroken strings wrap, and file I/O is UTF-8 (emoji/CJK/RTL safe). Repository-only simulation suites cover empty input, XSS payloads in every field, Unicode, unknown verdicts, 40 findings, degenerate coverage, wrong types, nulls, layout anatomy, details rows, and default no-network/no-JS behavior.

# Visual HTML readiness report (mandatory for full Shipworthy)

The audit already produces structured data — the coverage matrix and the finding
ledger. `scripts/render_report.py` turns compact ledger JSON into **one
self-contained HTML report** in the Shipworthy design system: masthead, verdict
stamp, stats chips, a coverage bar with a **covered-percentage** summary,
findings **grouped by severity** (Blockers / Strong / Provisional / Notes, each
with a count), collapsible Evidence / Fix / Verify details, and the
orchestration checkpoint. It **prints cleanly to PDF** (a light print stylesheet
keeps findings whole) and is **accessible** (the coverage bar carries an
`aria-label`; each segment has a `title`). The output is a single file: inline
CSS, system fonts, **no network calls and no JavaScript by default** — so it
opens offline, renders consistently in browsers and `wkhtmltopdf`, and prints
cleanly.

## Migration decision

The preferred visual direction came from a stronger hand-authored report style:
compact premium dark layout, clearer Shipworthy masthead, rotated verdict stamp,
stats chips, coverage legend, severity-grouped findings, numbered finding cards,
confidence pills, and collapsible Evidence / Fix / Verify rows. Those traits are
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

For a full Shipworthy invocation, generate it by default. The default output path
is outside the audited repo so read-only target behavior is preserved:

```text
~/.shipworthy/runs/<target-slug>/<timestamp>/readiness-report.html
```

Use a repo-local path such as `.shipworthy/reports/<timestamp>/readiness-report.html`
only when the user explicitly asks for repo artifacts.

For rapid, narrow, or static constrained passes, generate it when requested or
when the result is being shared, archived, or handed off.

Agents should emit compact ledger JSON only and never generate full HTML by hand.
The renderer fills a fixed template. This keeps token use low and prevents
report style drift.

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

3. Point the user to `readiness-report.html`. A worked example ships as
   `scripts/sample-report.json` — `python3 scripts/render_report.py scripts/sample-report.json`
   produces a complete demo report.

## JSON contract

```json
{
  "target": "string — what was audited",
  "generated_at": "YYYY-MM-DD (optional; defaults to today)",
  "verdict": "NOT READY | READY WITH RISKS | CONDITIONAL | READY",
  "summary": { "blockers": 0, "strong": 0, "provisional": 0 },
  "coverage": {
    "total_paths": 0,
    "segments": [
      { "kind": "covered|sampled|blocked|avoided|inferred|missing|out_of_scope|evidence_debt",
        "label": "human label", "value": 0 }
    ]
  },
  "findings": [
    { "severity": "blocker|strong|provisional|info",
      "confidence": "confirmed|strong|provisional|inferred (optional)",
      "title": "one line",
      "consequence": "user consequence (optional)",
      "evidence": "what was observed (optional)",
      "fix": "smallest useful fix (optional)",
      "verify": "exact verification step (optional)" }
  ],
  "checkpoint": {
    "lanes": ["ship-deep-review", "ship-product-workflows", "ship-workflow-clarity"],
    "mode": "e.g. 5 parallel agents | sequential fallback",
    "verifier": "e.g. Opus → APPROVED",
    "omitted": ["gate skipped → logged as evidence debt, not passed"]
  },
  "illustrative": false
}
```

Field notes: `findings` are sorted by severity automatically; every text field is
HTML-escaped; coverage segment widths are proportional to `value`; `verdict` selects
the banner color (rose / amber / emerald). Coverage kind aliases are normalized:
`debt` renders as `evidence_debt`, and mixed-case kinds such as `COVERED` are accepted.
Severity aliases are normalized too: `P0 Blocker`, `critical`, and `blocker`
render as Blockers; `P1 Major`, `major`, `high`, and `strong` render as Strong
signals; `P2 Moderate`, `moderate`, `medium`, and `provisional` render as
Provisional; `P3 Minor`, `minor`, `low`, `note`, `unscored`, and `info` render
as Notes. Unknown `kind`/`severity` values fall back to a neutral slate so the report never breaks on partial data. Setting
`"illustrative": true` stamps the report as a sample rather than a live run.

## Robustness

The generator degrades gracefully rather than crashing on partial or hostile data: every text field is HTML-escaped (XSS-safe), unknown severity/verdict/kind values fall back to neutral styling, missing sections render a muted note, non-numeric coverage values are ignored, long unbroken strings wrap, and file I/O is UTF-8 (emoji/CJK/RTL safe). This is enforced by `scripts/test_render_report.py` across empty input, XSS payloads in every field, unicode, unknown verdicts, 40 findings, degenerate coverage, wrong types, nulls, premium layout anatomy, details rows, and default no-network/no-JS behavior. Run it with:

```bash
python3 scripts/test_render_report.py
```

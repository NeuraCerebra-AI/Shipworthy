# Visual HTML readiness report (optional final artifact)

The audit already produces structured data — the coverage matrix and the finding
ledger. `scripts/render_report.py` turns that data into **one self-contained HTML
report** in the Shipworthy design system: a verdict banner, a coverage bar with a
**covered-percentage** summary, findings **grouped by severity** (Blockers / Strong /
Provisional / Notes, each with a count), and the orchestration checkpoint. It **prints
cleanly to PDF** (a light print stylesheet keeps cards whole) and is **accessible**
(the coverage bar carries an `aria-label`; each segment has a `title`). The output is a single
file: inline CSS, system fonts, **no network calls and no JavaScript** — so it opens
offline, renders identically in browsers and `wkhtmltopdf`, and prints cleanly.

## When to generate it

Only after the final claim ledger, coverage, verifier outputs, and checkpoint are
complete (i.e., after step 17 of the Mandatory Flow). It is a *rendering* of the
canonical ledger, never a second source of truth. Offer it; don't force it.

## How to generate it

1. Serialize the completed ledger into the JSON contract below (write it next to the
   evidence, e.g. `readiness-report.json`).
2. Run:

   ```bash
   python3 scripts/render_report.py readiness-report.json readiness-report.html
   ```

   Add `--interactive` for a client-side filter/search/collapse version (opt-in inline
   JS, no network; print-safe). Other formats — SARIF, evidence bundle, merge gate — are in
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
      { "kind": "covered|sampled|blocked|avoided|missing|debt",
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
the banner color (rose / amber / emerald). Unknown `kind`/`severity` values fall back
to a neutral slate so the report never breaks on partial data. Setting
`"illustrative": true` stamps the report as a sample rather than a live run.

## Robustness

The generator degrades gracefully rather than crashing on partial or hostile data: every text field is HTML-escaped (XSS-safe), unknown severity/verdict/kind values fall back to neutral styling, missing sections render a muted note, non-numeric coverage values are ignored, long unbroken strings wrap, and file I/O is UTF-8 (emoji/CJK/RTL safe). This is enforced by `scripts/test_render_report.py` — 124 assertions across 18 scenarios (empty input, XSS payloads in every field, unicode, unknown verdicts, 40 findings, degenerate coverage, wrong types, nulls). Run it with:

```bash
python3 scripts/test_render_report.py
```

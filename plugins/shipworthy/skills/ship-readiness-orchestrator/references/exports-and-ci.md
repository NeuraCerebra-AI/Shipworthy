# Deliverables — exports, evidence bundle, gate, and (optional) CI

Everything here is a **render or transform of the finished ledger** — never a second source
of truth, and generated only after Mandatory Flow step 17. All of it runs **locally**: the
audit and its evidence never leave the machine (a real ZDR / data-sovereignty property for
regulated or enterprise use). Offer these; don't force them.

Primary usage is a human running a pre-flight audit inside Codex / Claude Code (desktop or
CLI). So the default deliverable is an **inline report**; these files are for when the user
wants to **share, archive, gate, or automate**.

## The scripts (all take the ledger JSON)

| Script | Produces | Use when |
|---|---|---|
| `scripts/render_report.py in.json out.html` | self-contained HTML report (verdict, coverage %, grouped findings, checkpoint); `--interactive` adds client-side filter/search/collapse | a shareable/printable human report |
| `scripts/to_sarif.py in.json out.sarif [--gate]` | SARIF 2.1.0 for GitHub code scanning; `--gate` exits non-zero per policy | machine-readable findings / a merge gate |
| `scripts/make_bundle.py in.json out.zip [--include PATH ...]` | a tamper-evident evidence bundle (ledger + report + SARIF + `manifest.json` with per-file SHA-256) | a defensible audit trail for a client/stakeholder |

The **ledger JSON itself** is the canonical machine-readable export — the contract is in
`references/visual-html-report.md`. `make_bundle.py` includes it verbatim.

## Interactive report (`--interactive`)

Off by default (the plain report is pure HTML, no JavaScript — maximally portable and
inspectable). `--interactive` adds a small **inline, dependency-free, no-network** script:
severity filter toggles, a text filter, and click-to-collapse cards. It is print-safe (all
findings show when printed; controls are hidden). Use it for large reports viewed as an
artifact in the desktop app; skip it for a quick CLI read.

## The gate (`--gate`)

`to_sarif.py --gate` exits non-zero so a script or CI job can **fail on real problems**.
Default policy: **confirmed blockers only** — provisional findings never block, because they
are too nondeterministic to gate a build on. Override via an optional `"policy"` block in the
ledger:

```json
"policy": { "fail_on": ["blocker"], "require_confirmed": true }
```

The gate controls **pass/fail only** — it never suppresses or downgrades a finding. Keep it
that way; a gate that hides findings to go green defeats the point.

## Optional: CI (for teams that also run headless)

Most runs are interactive, not CI. But because it emits SARIF, Shipworthy plugs into GitHub
code scanning for the minority who want automation — and GitHub then does **PR annotations,
Security-tab alerts, and native new/fixed/persistent tracking** for free (findings with a
`location` annotate the diff; UX/path findings appear as repo-level alerts — honest partial
fidelity). Sketch:

```yaml
# .github/workflows/readiness.yml (illustrative)
permissions: { contents: read, security-events: write }
steps:
  - uses: actions/checkout@v4
  - run: <produce ledger.json from a Shipworthy run>          # your invocation
  - run: python3 to_sarif.py ledger.json readiness.sarif --gate # gate on confirmed blockers
    if: always()
  - uses: github/codeql-action/upload-sarif@v3
    if: always()
    with: { sarif_file: readiness.sarif }
```

For new/fixed on a PR, upload SARIF for both the base and head commits (GitHub compares them);
stable fingerprints (already emitted) keep the comparison accurate across runs.

> The generated SARIF validates against the official SARIF 2.1.0 schema, and all three
> generators are covered by simulation suites (`scripts/test_*.py`) run in CI.

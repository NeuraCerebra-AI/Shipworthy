# Live Regression: TraceFlow Shipready HTML Report Miss

## Trigger

User asked: `/goal are we shipready?`

## What went right

- The agent loaded the Shipworthy stack.
- The agent used the Multi-Agent Authorization Gate and recorded sequential fallback when authorization was not received.
- The agent ran source/CLI evidence commands and a partial static Run Inspector path-walk.
- The agent produced a correct conditional verdict and avoided production/tapeout/signoff overclaims.
- The agent saved a Markdown audit ledger and browser evidence.

## What went wrong

The agent did not generate the distinct Shipworthy `readiness-report.html` before the first final answer. It confused a downgraded/source-CLI/static-audit path plus target-owned HTML artifacts with completion of the Shipworthy report deliverable.

## Root cause

The agent interpreted "not a full flagship run" as weakening the HTML report requirement. That interpretation is invalid. Downgrade status changes report contents and wording; it does not remove the report requirement.

## Required future behavior

Every operational Shipworthy invocation must generate `readiness-ledger.json`, `report-input.json`, and `readiness-report.html` unless the user explicitly forbids artifact creation or file writes are impossible. The final answer must include the absolute HTML path. If the HTML file is missing, the final answer must lead with `HTML report: MISSING/BLOCKED` and must not imply completion. A redundant `readiness-report.json` is not required.

## Regression assertion

A source/CLI-only, static constrained, changed-only, or downgraded Shipworthy run still emits a distinct Shipworthy `readiness-report.html` and does not substitute target-owned HTML, Markdown ledgers, screenshots, or chat summaries for that report.

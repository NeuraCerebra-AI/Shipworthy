# Native Codex runtime-only Gauntlet brief

Read these exact copied skill bodies and follow their operational handoff:

plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md
plugins/shipworthy/skills/ship-deep-review/SKILL.md
plugins/shipworthy/skills/ship-product-workflows/SKILL.md
plugins/shipworthy/skills/ship-workflow-clarity/SKILL.md

Audit only the supplied localhost product using the supplied member/admin
accounts, safe boundary, reset endpoint/token, and output allowlist. Use one
coordinated runtime driver. Safe controls may be exercised; destructive actions
must be inventoried and avoided. Reset between materially different fixtures.

Do not inspect any path outside the explicit allowlist. Do not inspect the
repository test tree, prior runs, comparison logic, or private expected data.
Do not use network hosts other than the supplied localhost URL.

Write a canonical readiness ledger (`readiness-ledger.json`), report input with
the canonical path frontier (`report-input.json`), and mandatory self-contained HTML
(`report.html`) to the supplied evidence output. State that filesystem
containment and oracle blindness are procedural, not technically proven.

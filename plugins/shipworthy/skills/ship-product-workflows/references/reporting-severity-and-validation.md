# Reporting, Severity, And Validation

## Table Of Contents

- Purpose
- Findings-First Reporting
- Severity
- Confidence
- Recommendation Buckets
- Verification
- Scores
- Skill Validation
- Trigger Probes

## Purpose

Use this reference before reporting findings, fix rankings, validation plans, or skill-forward-test results.

## Findings-First Reporting

Lead with confirmed or strongest findings. Put process, score, and narrative summary after findings.

For full audits, include:

1. Top findings or no confirmed findings.
2. Scope, route, mode, evidence path, risk gate, safe-test boundary, tools/agents used or skipped, reroutes, and exclusions.
3. Ledger path, ledger section, or skipped reason when a ledger would normally be expected.
4. Coverage map.
5. Findings by path.
6. `$ship-workflow-clarity` lane summary when used.
7. Evidence inventory.
8. Assumptions and untested paths.
9. Ranked fix list.
10. Verification plan.
11. Open questions and recommended next pass.

For quick audits, compress the same logic into a short findings-first response. Prefer completion over breadth: if the audit starts expanding into path mapping, agents, templates, or broad adjacent context, either reroute explicitly or stop at the top 1-3 evidence-backed findings with a recommended next pass.

## Severity

Use coarse severity:

- `Critical`: blocks a core workflow, risks data loss, unauthorized exposure, real money/privacy/publishing/destructive harm, or misleading high-stakes action.
- `High`: breaks a major path, causes persistent wrong state, blocks a key role, creates serious trust/governance failure, or makes recovery unclear after a consequential action.
- `Medium`: degrades a meaningful path, creates likely support burden, causes avoidable rework, hides important status, or fails in common variants.
- `Low`: local friction, copy/layout/accessibility smoke issue, minor inconsistency, or bounded edge case with limited consequence.

Severity follows user consequence, not how interesting the technical cause is.

## Confidence

Use coarse confidence:

- `Confirmed`: directly observed with adequate evidence.
- `Strong`: supported by multiple evidence types or direct code/log plus likely runtime path.
- `Provisional`: plausible from partial evidence, needs one verification step.
- `Hypothesis`: useful lead, not enough evidence for a finding.
- `Not tested`: explicitly outside current evidence.

Never let confidence exceed evidence. Screenshot-only behavior claims are usually provisional at best.

## Recommendation Buckets

Use buckets to prevent generic advice:

- `Fix now`: clear defect or regression with direct user consequence.
- `Harden`: add fallback, state handling, permission check, error handling, monitoring, or regression test.
- `Clarify`: improve labels, state, consequence, recovery, proof, or governance. Use `$ship-workflow-clarity` evidence when available.
- `Preserve`: keep necessary complexity, friction, proof, expert controls, or governance boundaries.
- `Investigate`: gather missing evidence before changing.
- `Do not change`: apparent friction is necessary or the proposed simplification would create risk.

## Verification

Every finding needs an exact verification step:

- browser path to click;
- role/account;
- input data;
- expected UI result;
- persistence check;
- console/network/log absence or expected status;
- responsive/accessibility check if relevant;
- regression test or code-level check when useful.

Verification should be executable by a future agent or developer without reconstructing the audit from scratch.

## Scores

Do not lead with scores. Omit scores unless requested.

If requested, use coarse labels only, such as:

- Ready with minor fixes;
- Not release-ready until high findings are fixed;
- Needs another evidence pass;
- Good coverage for selected paths, incomplete for app-wide claims.

Avoid decimal scores and fake precision.

## Skill Validation

Use `skill_validation` only when validating this skill itself. Forward-test with realistic tasks:

- quick static path;
- standard product area;
- changed-only diff;
- major multi-surface app;
- Computer Use or native-style workflow when possible;
- near-miss prompts that should not trigger.

Compare with a no-skill baseline when time permits. Grade whether the skill improves coverage, evidence discipline, safety boundaries, clarity-lane routing, findings-first output, and verification specificity.

For major, full-pass, long-running, or agent-assisted forward tests, also check that the output either creates/updates a living audit ledger, includes a ledger section, or explicitly explains why one was skipped. The ledger should preserve discovery without freezing scope.

Run structural validation after edits:

```bash
python3 <skills-dir>/.system/skill-creator/scripts/quick_validate.py <skills-dir>/ship-product-workflows
python3 -m json.tool <skills-dir>/ship-product-workflows/templates/coverage-map.json >/dev/null
```

Also run a placeholder, private-term, and hidden-metadata search appropriate to the installation before treating the skill as clean.

## Trigger Probes

Should trigger:

- "Audit this app end to end and find where users get stuck."
- "Use Playwright to try every meaningful path in this workflow."
- "Check this changed UI for regressions across product paths."
- "Audit the UI and backend issues so everything works and looks good."
- "Run a release-readiness product workflow audit."
- "Use Computer Use to click through this desktop app and find breakpoints."

Should not trigger:

- "Review this function for code style."
- "Run a security scan."
- "Do a WCAG-only accessibility audit."
- "Make this landing page prettier."
- "Scrape these pages with Playwright."
- "Explain this backend architecture."
- "Load test this endpoint."

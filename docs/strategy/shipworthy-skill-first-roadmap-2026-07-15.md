# Shipworthy skill-first roadmap

**Status:** Active product direction. Local migration evidence does not claim
publication, merge, or availability in `origin/main`.

## Product direction

Shipworthy is four self-contained skills for Codex and Claude. The host owns
browser control, computer use, shell execution, and target-repository tooling.
The skills own audit judgment, the canonical evidence ledger, proof ceilings,
lineage, evidence debt, and the mandatory self-contained HTML report.

Native browser or computer-use capabilities are the default for adaptive,
human-style path walking. An existing target-owned Playwright setup remains the
right tool for deterministic replay, assertions, isolated contexts, traces,
cross-browser checks, and CI regression proof. Shipworthy neither installs
Playwright nor launches a separate browser runner.

## Installed product boundary

- Four independently usable `SKILL.md` products with local references,
  templates, profiles, and agent metadata.
- Three Python standard-library output utilities inside the orchestrator:
  HTML, SARIF, and a tamper-evident evidence bundle.
- No separate runtime product, package installation, background process, data
  service, hosted surface, or account system.
- Codex and Claude plugin managers own the normal lifecycle. `install.sh` is an
  advanced explicit-target fallback with backup and failure rollback.
- Development fixtures, legacy comparison, installed-copy parity, and lifecycle
  rehearsal stay repository-only.

## Preserved proof contract

Every operational run produces `readiness-report.html`, including downgraded or
standalone runs. Imported browser, Playwright, and legacy inputs remain bounded;
missing bytes, unavailable channels, ambiguous mappings, and unexplained
dual-render differences remain evidence debt. Imported status cannot by itself
inflate confidence, proof, verifier approval, or readiness.

The recovered source template
`plugins/shipworthy/skills/ship-product-workflows/templates/audit-ledger.md`
remains explicitly unignored. Its eventual availability in `origin/main` is
**NOT_PROVEN** until reviewed integration occurs.

## Deferred work

No runner platform, persistent service, general command product, hosted UI,
scheduler, credential storage, external integration layer, billing, accounts,
or multi-tenant infrastructure is part of this migration. A later adapter is
considered only when a real target already emits its format, a sanitized fixture
demonstrates value, conservative lineage is possible, and separate approval is
given.

## Current proof ceiling

- Python 3.11 isolated execution on the current macOS host: proven locally.
- Other Python and OS variants: **NOT_PROVEN**.
- Operational native install/reload/upgrade/removal through each host:
  **NOT_PROVEN** unless separately exercised in an isolated host session.
- Real installed-copy parity: deliberately **NOT_PROVEN**; only synthetic
  temporary copies are exercised.
- Former package build, lockfile, wheel, and SBOM claims:
  **NOT_APPLICABLE — package removed**.
- OS-level network containment: **NOT_PROVEN**.
- Publication or merge to `origin/main`: **NOT_PROVEN**.

Phase 1 has not started because this work ends at the four-skill product
boundary and delegates execution to capabilities the host or target already owns.

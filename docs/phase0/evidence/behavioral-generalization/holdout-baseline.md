# Frozen holdout baseline

Date: 2026-07-20 (America/Los_Angeles)

Production skill revision: `4651c8d1cd006230788d0d37f0e3fc312e5fbe48`

Subject: fresh native Codex agent, oracle-blind, runtime-only

Fixture: repository-only Waypoint multi-step onboarding holdout

Historical result: **FAIL**

This is the first holdout result. It used exact skill copies materialized with
`git archive` from the starting revision before any production skill edit in
this goal. The subject could read only those four copied skills, the bounded
brief, an empty workspace, the localhost product, and its evidence directory.
The private oracle, controller, comparator, runtime receipt, repository, and
prior results were outside its allowlist.

## Categorical diagnostics

| Dimension | Result | Evidence |
|---|---:|---|
| Discovery | 8/9 (88.89%) | `HB-09`, the `Ctrl+Enter` path, was not named in the discovery artifacts. Text in `closure_honesty.not_tested` was excluded from discovery scoring. |
| Execution | 8/9 (88.89%) | The 54-event private receipt contains no `Ctrl+Enter` activation. |
| Defect detection | 3/4 (75%) | `HD-01`, `HD-02`, and `HD-04` had distinct findings. `HD-03`—the still-enabled submit after permission loss—was observed in a transition but did not receive its own finding. |
| Evidence integrity | valid for the required canonical artifacts | The 57-row frontier is identical in the ledger and both report JSON artifacts; finding keys resolve; HTML closure is `incomplete`. The subject's auxiliary validation note misstated the HTML byte count (29,927 versus 30,002), so that prose note is not used as proof. |
| Closure honesty | pass | `claimed_exhaustive` was `false`; seven untested boundaries were listed. False exhaustive closure: `false`. |

The release-blocking seeded defect `HD-01` was found. The run still fails the
strict official gate because discovery, execution, and distinct defect-lineage
coverage were incomplete. No combined percentage is used.

## Finding classification

- Seeded findings: false success after permission loss; cancel discards without warning; refresh/re-entry loses draft progress.
- Genuine material miss: permission loss left Create enabled, but this did not receive a distinct finding (`HD-03`).
- Valid extras (`D`): displayed role/server-authorization mismatch; corrected choice leaves stale validation visible.
- Unsupported findings (`E`): none after deterministic semantic normalization and one-finding-per-defect assignment.

The first comparator pass incorrectly called all five findings unsupported
because it depended on exact phrase substrings. Focused RED/GREEN tests repaired
that repository-only comparator problem without changing this raw run. It also
stopped treating text listed under `not_tested` as discovered behavior.

## Private receipt

- Epochs: 1
- Events: 54
- Deterministic receipt digest: `4c136d6713d0ce7eb8b02c9831186fb58bda1f8f27c317422873b58eb3dbc7e4`
- File SHA-256 before controller cleanup: `37c15b24715766fcb7f92dd8a1d0ba73e04c3fb0c983f44e44a7b68f24f662f2`

The receipt proves route visits, desktop/mobile viewports, Editor/Viewer roles,
pointer and keyboard inputs, branching, back/cancel, permission change, submit
rejection, and reload/re-entry. It does not prove `Ctrl+Enter`.

## Frozen artifact hashes

| Artifact | SHA-256 |
|---|---|
| `holdout-observation.json` | `4aa79f92bd9a88d3e3b28589f8e1d6c62bf7dc4bc5c29e107cc2f5ef2311fa07` |
| `readiness-ledger.json` | `0950aa3dc83202fb59a968b6786983bd39856603b2cc24c2a8e2cc5cdfea4be9` |
| `report-input.json` | `a67158568353334a7e46ce7eada2f6e2678b526764ac0037938c1ea6ebf3fda8` |
| `readiness-report.json` | `a67158568353334a7e46ce7eada2f6e2678b526764ac0037938c1ea6ebf3fda8` |
| `readiness-report.html` | `ec541e4ec75897ee29b127d507457637891a5d2ed84098b0438f005c47c58a04` |
| `runtime-evidence.md` | `782171a6d8496db2c713dae74591f55fe35826d8f453eda44c30f580b54cb4e7` |
| `lane-roster.md` | `3696a3762d3f610413c69e804f74115716e8d27a79f405304e01919dcc777bae` |
| `verifier-certificates.md` | `f46e9e5808cb1d5b57b35702c862ef75ba814001432a96cf4d0d956ddfc271ec` |
| `artifact-validation.json` | `9e52aeb093e73c581d4b66367813746ede97b594b703c62bca1e7dd936a19557` |

The controller-private receipt was read and hashed before cleanup. No raw
receipt or oracle answer was exposed to the subject.

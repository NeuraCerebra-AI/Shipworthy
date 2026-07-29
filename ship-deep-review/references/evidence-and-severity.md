# Evidence And Severity

## Evidence Classes

- **A: Direct runtime or command proof.** Browser interaction, screenshot, API response, test output, logs, or reproduced behavior from the target environment.
- **B: Direct source proof.** File anchors, code paths, schema/contracts, docs verified against current source.
- **C: Corroborated inference.** Multiple source clues support a likely issue, but no direct reproduction yet.
- **D: Hypothesis.** Plausible but unproven. Must not be reported as a confirmed finding.

Evidence is only valid for the target it came from. Branch, commit, route, dataset, account, environment, date, and runtime all matter. If those differ from the review target, downgrade or mark needs-proof.

## Target Fingerprint

Record enough target detail that another agent can tell whether evidence belongs to the same review:

- repo work: branch, commit, dirty state or worktree, command, runtime URL, and data fixture/account;
- browser work: URL, viewport/device, account/session, timestamp, and screenshot/video path;
- research work: source URL, publication/update date, access date, and jurisdiction/market/context.

Wrong-target evidence cannot support a confirmed finding. Use it only as a contradiction, branch-drift clue, or retargeting lead.

## Severity

- **P0:** data loss, security boundary failure, governance corruption, unsafe live action, or app cannot boot.
- **P1:** release blocker, wrong product truth, broken core workflow, severe UX trust failure, or a11y signoff blocker.
- **P2:** meaningful product friction, confusing state, cost risk, maintainability risk, or trust erosion with workaround.
- **P3:** papercut, copy polish, minor visual cleanup, or low-risk hardening.

## Proof Thresholds

- **P0/P1:** require evidence class A, or class B with direct current source proof plus explicit limitation that runtime was not reproduced. A stale note, wrong branch, or single inference cannot support P0/P1.
- **P2:** may use class A, class B, or strong class C if uncertainty and follow-up are explicit.
- **P3:** may group similar papercuts, but still needs at least one concrete anchor.
- **Readiness/no-go:** must cite the exact blocker claims and the unproven release-gate gaps.

## False-Positive Tribunal

Before promoting a finding:

1. Ask what would prove it wrong.
2. Check whether another agent contradicted it.
3. Check whether the evidence is from the correct branch, route, dataset, or runtime.
4. Separate "bad wording" from "bad mutation."
5. Separate "test fixture mismatch" from "product contract failure."
6. Mark unresolved claims as needs-proof instead of confirmed.

## Claim Status

- **Approved:** verifier agrees the claim and severity are supported.
- **Downgraded:** issue exists but severity, scope, or confidence was overstated.
- **Rejected:** evidence does not support the claim or wrong target was used.
- **Needs proof:** plausible but missing decisive evidence.
- **Blocked:** proof requires user approval, credentials, live provider calls, or unsafe mutation.

## Evidence Debt

Needs-proof and blocked items stay in the evidence debt register until they are approved, downgraded, rejected, closed as blocked with reason, or explicitly scoped out. Do not omit them from later waves because they are inconvenient or because stronger findings appeared.

## Readiness Claims

Never claim ready, passing, safe, or fixed unless the relevant command/browser evidence is present. If tests were not run, say so plainly.

# Wave Protocol

## Wave 0: Mission And Preflight

Capture:

- target and source of truth,
- target fingerprint: branch, commit, worktree, runtime URL, account/data fixture, environment, timestamp, and any external source date,
- focus lens,
- allowed mutation level,
- runtime/browser requirements,
- commands/tests expected,
- evidence standard,
- platform cap and model choices,
- final deliverable format.

For repo work, record branch, dirty state, worktree path, and any local app/server URL used.

Record where wave outputs will live. Acceptable forms include files in a scratch directory, agent IDs whose completed outputs can be read, or a report artifact. Do not depend on memory alone.

## Evidence State Artifacts

Maintain these artifacts after every wave:

- **Claim ledger:** claim ID, claim, evidence, target fingerprint, evidence class, severity, confidence, status, contradictions, falsifier, and next action.
- **Coverage matrix:** target surface, checked-by agent, evidence class, status, gaps, and whether the focus lens received enough coverage.
- **Evidence debt register:** unresolved needs-proof or blocked items, proof needed, owner/wave, deadline or retargeting plan, and final disposition.

Do not let prose replace these artifacts. Summaries and final reports are derived from them.

## Wave 1: Broad Reconnaissance

Dispatch distinct agents across the main surfaces. Each agent should search broadly, collect evidence, identify expected-but-absent signals, and mark uncertainty. Do not ask every agent to solve the whole problem.

## Verified Barrier After Wave 1

The orchestrator must:

1. Read every Wave 1 output in full.
2. Create evidence state: claim ledger, coverage matrix, and evidence debt register, not a narrative summary.
3. Dispatch one independent verifier with raw Wave 1 outputs, evidence state, preflight facts, and target brief.
4. Require the verifier to perform a shadow read first: extract its own findings from raw outputs before comparing with the orchestrator ledger.
5. Require the verifier to approve, downgrade, reject, mark needs-proof, or mark blocked for each claim, and to name any missing claims.
6. Read the verifier output in full.
7. Write the Wave 1 intelligence summary only after verifier approval.
8. Run a post-write drift check against the verified evidence state.
9. End the summary with a verification certificate.
10. Design Wave 2 from verified signals, contradictions, coverage gaps, and evidence debt.

## Wave 2: Targeted Deep Dive

Target the strongest findings, contradictions, cascade risks, and missing proof. Use reproduction, source tracing, browser checks, focused tests, and disconfirmation probes. Include deep-reasoning-style tradeoff analysis and domino-style consequence tracing when relevant.

Keep at least one disconfirmation lane when a high-severity finding depends on a single agent, a single evidence type, or a surprising absence signal.

## Verified Barrier After Wave 2

Repeat the read-all + evidence-state + independent verifier + verification-certificate + intelligence-summary gate. Promote only findings with real reachability or strong source/runtime proof. Reclassify weak items as papercuts, needs-proof, blocked, false positives, or open questions.

If the verifier withholds approval, do not start Wave 3. Either dispatch a narrow proof-gathering agent or write an incomplete checkpoint that clearly says the wave did not produce a verified intelligence summary.

Before Wave 3, every evidence-debt item from Wave 1 must be proved, rejected, downgraded, blocked, or explicitly carried forward with a reason.

## Wave 3: Release Gate / What-Did-We-Miss

Run final smoke and adjacent-surface checks. Look for missed route surfaces, hidden state boundaries, documentation drift, test gaps, stale assumptions, and severity inflation.

Use the coverage matrix to choose the final pass. Do not spend Wave 3 only rechecking already-proven lanes while untouched surfaces remain relevant to the user request.

## Minimum And Adaptive Waves

A full Shipworthy run has a minimum of three verified waves after Wave 0. Treat the first three verified waves as the floor, not the finish line. Additional waves are required when the coverage matrix still has major route families, user roles, state variants, runtime proof, contradictions, disconfirmation needs, safe path attempts, or evidence debt that could change the readiness verdict.

Adaptive continuation is driven by verified evidence, not by anxiety or time. If every material expected intent and discovered path is labeled covered, sampled with justification, blocked, avoided, inferred, missing, out_of_scope, or evidence_debt, the orchestrator may proceed to the final no-overclaim verifier. If the independent verifier says coverage is too thin, run additional waves or mark the run incomplete instead of writing a normal final report.

## Verified Barrier After Wave 3

Repeat the read-all + evidence-state + independent verifier + verification-certificate + summary gate before the final report. The final report must be based on verified wave summaries plus direct evidence, not raw agent volume.

Then build a final claim ledger and send it to the final no-overclaiming verifier. The verifier must compare final claims against verified wave evidence, unresolved debt, and coverage gaps before the orchestrator writes the final synthesis.

## Verification Certificate

Every wave intelligence summary must end with:

- outputs read,
- verifier agent/model,
- verification input scope,
- verifier approval status,
- approved findings,
- downgraded findings,
- rejected findings,
- findings still needing proof,
- blocked findings,
- coverage gaps,
- evidence debt carried forward or closed,
- unresolved contradictions,
- required retargeting.

If any field is missing, the summary is incomplete and the next wave must not start.

## Post-Write Drift Check

After writing each wave intelligence summary and the final report, scan the prose for factual, severity, readiness, and safety claims. Each must map to a claim ledger entry or coverage/debt statement. If the prose is stronger than the ledger, revise it before treating the artifact as complete.

## Resume Rule

If interrupted or compacted during a wave, list the wave output directory or agent IDs, identify completed outputs, and read each completed output in full before deciding whether the wave is complete or whether to re-dispatch missing lanes.

If the interruption happened after verification but before summary-writing, re-read the verifier output too. The summary must cite the verifier decision, not memory of it.

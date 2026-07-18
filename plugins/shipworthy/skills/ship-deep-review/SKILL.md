---
name: ship-deep-review
description: Use only when the user explicitly invokes or names ship-deep-review, or when an active ship-readiness-orchestrator run explicitly loads it as the required controller. Do not activate from generic audit, review, critique, validation, research, or readiness language; an explicit instruction not to use ship-deep-review always prevents activation.
---

# Shipworthy Deep Review

## Activation Gate

First honor any explicit instruction not to use `ship-deep-review`; it always
closes this gate, including during an orchestrator handoff.

Continue only when one of these conditions is present:

1. The user explicitly invokes or names `ship-deep-review`; or
2. `ship-readiness-orchestrator` is already active from an operational
   Shipworthy/readiness request and explicitly loads `ship-deep-review` as its
   required controller.

Generic audit or review language never satisfies this gate, regardless of how
comprehensive, adversarial, evidence-first, hostile, multi-stage, or “deep” the
request sounds. These phrases alone are not triggers:

- deep review
- deep audit
- comprehensive audit
- adversarial or hostile review
- evidence-first audit
- multi-wave or multi-stage review
- product-readiness audit
- implementation-plan critique
- research validation

If neither permitted condition exists, do not continue: the agent must not load
the skill’s references, apply this workflow, create claim ledgers, coverage
matrices, evidence-debt registers, or waves, or dispatch review agents. Handle
the request normally or route it to another applicable skill without using this
protocol.

Once this gate legitimately opens, continue with the deep-review protocol below
unchanged.

Deep Review is a repo-agnostic companion workflow for evidence-heavy investigation. It is a review controller, not a domain substitute: use repo instructions, browser tools, MCPs, security skills, research skills, and Superpowers where they fit the target.

The core rule: **no wave intelligence summary may be written until the orchestrator has read every agent output for that wave, created a claim ledger, an independent verifier has checked the raw outputs and ledger, and the summary records that verification.**

Evidence-state rule: the claim ledger is the truth layer, the coverage matrix is the scope layer, the evidence debt register is the uncertainty layer, and prose is only the delivery layer. Summaries and final reports must map material claims back to those artifacts and pass a drift check before being treated as complete.

## Required References

Read only the references needed for the current task:

- `references/platform-profiles.md`: platform-specific agent limits and model choices.
- `references/wave-protocol.md`: wave flow, barriers, retargeting, and verification gates.
- `references/agent-output-contract.md`: mandatory agent prompt/output contract.
- `references/evidence-and-severity.md`: evidence classes, severity calibration, and false-positive handling.
- `references/focus-lenses.md`: how to adapt the workflow when the user says "focus on UX", "focus on backend", etc.
- `references/final-report-template.md`: final deliverable structure.

For any multi-agent run, `platform-profiles.md`, `wave-protocol.md`, `agent-output-contract.md`, and `evidence-and-severity.md` are required.

## Quick Reference

| Situation | Required Move |
|---|---|
| User says "use this skill and focus on X" | Treat X as a priority lens, not a blinder. |
| User asks for review but no mutation | Keep the run read-only except explicit report artifacts. |
| User asks for fixes too | Complete the review first, then switch to implementation skills/plans. |
| Wave agents finish | Read all outputs, update evidence state, verify, then summarize. |
| Verifier rejects or withholds approval | Do not write a normal wave summary; gather proof or label the checkpoint incomplete. |
| A claim remains plausible but unproven | Keep it in the evidence debt register until proved, rejected, blocked, or scoped out. |
| Context compacts mid-wave | Re-read completed outputs before continuing. |

## Start Gate

Before dispatching agents or writing a plan:

1. Read the user's entire request and all attached files or referenced local files that define the target.
2. Identify the review target, focus lens, allowed mutation level, runtime/browser needs, and output format.
3. Confirm branch/worktree/source-of-truth when reviewing a repo.
4. If the task is mutable, prefer an isolated worktree and follow repo instructions such as `AGENTS.md`.
5. Default to full mode with three waves. Use rapid mode only when the user explicitly asks for a quick/time-boxed pass or the target is genuinely small; state that downgrade before proceeding. Rapid mode still requires a verified barrier before final claims.
6. If the user only asks for high concurrency without asking for a deep review/audit/research target, do not invoke this workflow solely for that reason.

## Platform Rule

Read `references/platform-profiles.md` before agent dispatch.

For Codex, use at most 6 concurrent agents. Prefer `gpt-5.5` with `xhigh` reasoning for the coordinator, specialist agents, wave verifiers, and final synthesis whenever available.

For Claude Code, use mostly Sonnet for specialist agents, with Opus for each wave's independent verification and final no-overclaiming verification. Claude Code does not have Codex's 6-agent limit; when a wave has 13 or fewer independent agents with non-conflicting scopes, launch the whole wave at once.

## Wave Barrier Rule

At the end of every wave:

1. Wait for all expected agents or mark missing outputs explicitly.
2. Read every completed agent output in full.
3. Create or update the evidence state: claim ledger, coverage matrix, and evidence debt register. This is not a wave intelligence summary.
4. Dispatch one independent verification agent using the strongest platform model:
   - Codex: `gpt-5.5` `xhigh` if available.
   - Claude Code: Opus.
5. Give the verifier the raw wave outputs, evidence state, preflight facts, and target brief. Do not give it a draft narrative summary, because that makes the verifier less independent.
6. Ask it to do a shadow read first: independently extract findings from raw outputs, then compare that extraction to the orchestrator ledger.
7. Ask it to check claim support, severity, contradictions, source quality, missing caveats, false positives, missing evidence, and overclaiming.
8. Read the verifier output in full.
9. If the verifier does not explicitly approve summary-writing, gather missing proof, re-dispatch a narrow agent, or write only an incomplete checkpoint. Do not proceed as if the wave is complete.
10. Only then write the wave intelligence summary.
11. Run a post-write drift check: every material factual or severity claim in the summary must trace to an approved, downgraded, needs-proof, blocked, or rejected ledger entry.
12. End every wave summary with a verification certificate naming the outputs read, verifier model/agent, approved/downgraded/rejected findings, unresolved contradictions, evidence debt, and next-wave targets.
13. Retarget the next wave from the verified summary and evidence debt, not from the original lane split.

If context compaction/resume happens after a wave has begun, first list and read every completed wave output before continuing. Do not rely on memory or a compacted summary alone.

## Workflow

1. **Frame the mission.** Define the target, focus lens, constraints, and success criteria.
2. **Build the wave plan.** Choose lanes based on the target, using the focus lens as priority rather than tunnel vision.
3. **Wave 1: broad reconnaissance.** Dispatch bounded, non-overlapping agents across the main surfaces.
4. **Verified Barrier 1.** Read all outputs, update evidence state, run independent shadow verification, then write Wave 1 intelligence summary with certificate.
5. **Wave 2: targeted reproduction and contradiction resolution.** Focus on strongest findings, missing proof, and high-impact cascades.
6. **Verified Barrier 2.** Repeat the read-all + evidence-state + independent-verifier + certified-summary gate.
7. **Wave 3: release gate / what-did-we-miss pass.** Run final smoke, adjacent-surface checks, and severity calibration.
8. **Verified Barrier 3.** Repeat the wave verification gate before final synthesis.
9. **Final synthesis.** The orchestrator writes the final synthesis because it owns the full continuity of user intent, preflight truth, all wave outputs, all verifier decisions, and retargeting history. Use Opus or `gpt-5.5 xhigh` to verify the final claim ledger, evidence debt, and coverage gaps before writing, not to replace the orchestrator as author.
10. **Final report.** Lead with product/research truth, blockers, evidence, false positives, tests/browser proof, and exact uncertainty boundaries.

## Superpowers Integration

When available, use relevant Superpowers skills:

- `superpowers:using-superpowers` to obey skill routing.
- `superpowers:dispatching-parallel-agents` for independent lanes.
- `superpowers:using-git-worktrees` for repo isolation.
- `superpowers:systematic-debugging` for reproducing defects.
- `superpowers:verification-before-completion` before readiness/fix claims.
- `superpowers:requesting-code-review` before final handoff of implemented fixes.

Do not let the presence of this skill override user constraints. If the user says read-only, do not mutate repo files except explicitly requested audit artifacts.

## Common Failure Modes

- **Draft-summary laundering:** writing a summary first and asking the verifier to bless it. Fix: send raw outputs plus a terse claim ledger, not prose synthesis.
- **Agent-volume illusion:** treating many agent reports as confidence. Fix: promote only verified claims with evidence.
- **Verifier anchoring:** giving the verifier the orchestrator's story first. Fix: require a raw-output shadow read before ledger comparison.
- **Evidence debt evaporation:** letting needs-proof items disappear between waves. Fix: keep the evidence debt register live until each item has a final disposition.
- **Prose drift:** final wording introduces claims stronger than the ledger. Fix: perform post-write drift checks before summaries and final reports are complete.
- **Focus-lens tunnel vision:** ignoring adjacent blockers because the user named one focus. Fix: prioritize the focus while preserving adjacent-risk lanes.
- **Readiness inflation:** saying ready, safe, or passing because most checks passed. Fix: list failed, skipped, and unproven checks.
- **Lost wave state after compaction:** relying on memory. Fix: re-read wave outputs before continuing.
- **Open-agent leakage:** leaving completed agents open and accidentally exceeding platform caps. Fix: close completed agents after reading their outputs.

## Output Rules

- Lead with the truth the user needs, not the process.
- Preserve exact evidence: file anchors, screenshots, command output, API payloads, URLs, or local paths.
- Separate confirmed findings, likely findings, needs-proof items, false positives, and rejected claims.
- Keep coverage gaps and evidence debt visible; do not silently drop unresolved items.
- State what was not run or not proven.
- Do not claim readiness, safety, or correctness without verification evidence.
- When the user requests a written artifact, save it to an appropriate repo-local or scratch path and report the exact location.

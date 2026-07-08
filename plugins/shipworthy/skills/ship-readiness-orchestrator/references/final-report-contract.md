# Final Report Contract

## Purpose

Write a findings-first readiness report that a senior engineering/design team can act on. Keep process visible enough to trust, but do not bury the verdict under ceremony.

## Contents

- Required Pre-Synthesis Gate
- Report Structure
- Finding Template
- Design Finding Template
- Roadmap Item Template
- Language Rules

## Required Pre-Synthesis Gate

Before writing the final report, assemble:

- sub-skill and reference files read;
- target fingerprint and safe-test boundary;
- ledger path/artifact location or inline ledger snapshot;
- lane roster with launched, sequential, skipped, collapsed, or blocked lanes;
- multi-agent authorization status, agent/tool execution status, and any platform limits that affected the run;
- frontend path-walk status: whether actual frontend path-walking occurred, the frontend tool used, runtime target, path-walk status, and downgrade reason if absent or partial;
- final claim ledger;
- final coverage matrix;
- evidence debt register with each item closed, blocked, scoped out, or carried as an explicit gap;
- verified wave summaries and certificates, or for rapid/narrow/static runs, one verified checkpoint plus a list of omitted full-run gates;
- raw lane outputs or artifact references;
- independent verifier output;
- fix-cascade notes for major recommendations;
- final drift check.

The final synthesis must be written by the orchestrator, not by a verifier or lane agent.

Store artifact references or redacted snippets by default. Do not include secrets, credentials, tokens, private customer payloads, raw production records, personal health/financial data, or external-message contents in the report unless the user explicitly authorized that handling.

## Report Structure

1. **Verdict**
   - Ready, conditionally ready, not ready, or cannot determine.
   - Name the top reason in one direct paragraph.
   - For rapid, narrow, or static constrained runs, state the omitted gates and downgrade readiness language accordingly.

2. **Orchestration Checkpoint**
   - Skill bodies read, references read, target fingerprint, safe-test boundary.
   - Ledger location or inline snapshot, including claim, coverage, evidence-debt, and fix-cascade ID ranges.
   - Multi-agent authorization status: explicitly authorized, denied, unavailable, not received, or not required for this constrained pass.
   - Frontend path-walk status: performed or not performed, frontend tool, runtime target, path-walk status, and downgrade reason.
   - Lane roster table with columns: lane, scope, required skill/reference, execution status, output/evidence location, skipped/collapsed/blocking reason.
   - Actual agent/tool execution mode, verifier status, raw output/evidence locations, omitted gates, and evidence debt created by unavailable agents, missing authorization, or runtime limits.
   - If subagent dispatch was skipped because authorization was absent, denied, unavailable, or not received, state: `sequential fallback because multi-agent authorization was not granted`.
   - If no actual frontend path-walking occurred, state the downgrade reason and do not call the report a full Shipworthy run.

3. **Release Blockers**
   - Highest severity findings first.
   - Include evidence, blast radius, and verification command/path.

4. **Broken Or Risky Workflows**
   - User-visible failures, state drift, persistence loss, blocked paths, permissions, forms, navigation, exports/imports, AI/action handoffs, recovery failures.

5. **Missing Or Overcomplicated Paths**
   - Reasonable user goals with no discoverable UX path, hidden entry points, excessive steps, repeated decisions, context switches, fragile prerequisites, dead ends, or needless recovery burden.
   - Include expected intent, evidence, path effort, user consequence, smallest useful fix, and verification step.

6. **UX, Clarity, And Design**
   - Ugly, cluttered, generic, confusing, attention-hostile, untrustworthy, or low-momentum surfaces.
   - Tie every point to user consequence, not taste alone.

7. **Product Love And Activation**
   - Time to value, first-run momentum, emotional payoff, repeat-use loop, share/referral moment, trust, perceived quality, onboarding drag, support burden.
   - Label strategy claims as hypotheses unless supported by evidence.

8. **Accessibility And Responsive Survival**
   - Keyboard/focus, accessible names, status/error exposure, zoom/reflow, mobile/touch, no-hover paths.

9. **Backend/API/State Symptoms**
   - Only symptoms that affect user-visible workflows or trust.

10. **Build/Test/Deploy/Docs Gate**
   - Commands run, commands missing, failures, skipped checks, stale docs, env/config risks.

11. **False Positives And Rejected Claims**
   - What was investigated and rejected or downgraded.

12. **Coverage And Evidence**
   - Coverage map summary, tools/agents used or skipped, artifact inventory, screenshots/traces/logs/commands, target fingerprint.
   - For full runs, list every discovered material path and expected intent with its coverage label and evidence debt status.
   - Note redaction boundaries and sensitive evidence omitted from the report.

13. **Evidence Debt**
   - Needs-proof, blocked, avoided, untested, inferred, missing, and out-of-scope items.

14. **Fix Cascade And Counterfactuals**
   - For major recommendations, state the no-change consequence, smallest useful fix, what the fix could break, and whether the fix is reversible.
   - Downgrade broad redesigns that lack a bounded verification path.

15. **Ranked Roadmap**
   - Fix Now, Harden, Clarify, Preserve, Add Friction, Investigate, Do Not Change.
   - Include smallest useful fix, regression risk, and exact verification step for each item.

16. **Final Drift Check**
   - State whether every material final claim maps to ledger evidence or an explicit gap.
   - Name any conclusions removed or downgraded because they lacked a ledger row.

## Finding Template

```text
[Severity][Confidence] Path / role-state-device: issue title
Evidence: artifact, command, screenshot, trace, log, code anchor, or source
Observation: what was seen
User consequence: what breaks, misleads, blocks, risks, or degrades
Likely cause: UI, state, data, permission, API/backend symptom, responsive, accessibility, clarity, trust, or design
Path effort: steps, decisions, context switches, repeats, waits, hidden prerequisites, or missing entry point when relevant
Counterfactual: what happens if nothing changes, when decision-relevant
Fix: smallest concrete change
Regression risk: what the fix could harm
Verify: exact check to confirm improvement
```

## Design Finding Template

```text
[Severity][Confidence] Surface / role-state-device: design issue title
Evidence: screenshot, trace, UI tree, focus note, code/doc support, or user-test note
Observation: visual hierarchy, density, wording, attention, object/state/consequence, or trust problem
User consequence: activation drag, missed action, confusion, false confidence, trust loss, abandonment, or support burden
Bucket: Simplify | Preserve | Add Friction | Harden | Clarify | Investigate | Do Not Change
Fix: smallest concrete design change
Stress test: what proof, control, recovery, accessibility, expert workflow, or governance boundary could be harmed
Verify: exact runtime or user-path check
```

## Roadmap Item Template

```text
[Bucket][Priority] recommendation title
Addresses: finding IDs
No-change baseline: what happens if ignored
Smallest useful fix: bounded change
Cascade risk: downstream paths, controls, proof, recovery, accessibility, governance, expert workflows, or operations that could be harmed
Reversibility: reversible, costly-to-reverse, or path-dependent
Verify: exact runtime, command, user-path, or design check
Monitor: signal to watch after shipping, if relevant
```

## Language Rules

- Say "covered paths inside the declared boundary", not "all paths", unless every path in the declared universe truly has evidence.
- Say "missing path" when a reasonable user goal has no discoverable UX path.
- Say "overcomplicated path" when a workflow technically works but has excessive steps, hidden prerequisites, repeated decisions, needless context switches, or fragile recovery.
- Say "not fully covered" when discovered material paths remain only sampled, blocked, avoided, inferred, missing, or evidence debt.
- Say "sequential fallback" when full-blast lanes were run in the main session because agent tooling was unavailable, unsafe, overlapping, or multi-agent authorization was not granted. If authorization was the reason, include `sequential fallback because multi-agent authorization was not granted`.
- Say "source/CLI/HTTP-only readiness audit is not a full Shipworthy run" when no browser/computer-use/frontend path-walk occurred and the work relied on repo, command, HTTP, provider, database, or docs proof.
- Say "actual frontend path-walk not performed" and use conditional/static/limited readiness language when the frontend was unavailable, out of scope, blocked by safety, or not tested.
- Say "not in ledger" or remove the claim when a final conclusion cannot be mapped to a claim, coverage, evidence-debt, or fix-cascade row.
- Say "static constrained pass" when only screenshots, docs, README, package scripts, or source snippets were available.
- Say "cannot determine" when evidence is missing.
- Say "script exists" or "command is documented", not "command passes", unless command output proves it.
- Say "beloved/viral hypothesis" or "activation/shareability signal", not "this will go viral".
- Separate release blockers from product polish.
- Separate ugly/cluttered/attention-hostile design findings from personal taste.
- Separate confirmed defects from recommendations, and recommendations from implementation.

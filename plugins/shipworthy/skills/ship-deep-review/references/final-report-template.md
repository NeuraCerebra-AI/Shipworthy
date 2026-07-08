# Final Report Template

Lead with the answer, then the evidence.

## Final Pre-Synthesis Gate

Before writing the final synthesis, the orchestrator must assemble:

- final claim ledger,
- final coverage matrix,
- evidence debt register with each item closed, blocked, scoped out, or carried as an explicit gap,
- verified wave summaries and certificates,
- final no-overclaiming verifier output.

The final verifier checks the claim ledger against verified evidence and unresolved gaps. The orchestrator still writes the final synthesis.

## Recommended Structure

1. **Verdict**
   - One direct paragraph: ready/not ready, true/false, ship/no-go, or what the evidence supports.

2. **Blockers**
   - Highest severity findings first.
   - Include evidence and blast radius.

3. **Broken Workflows Or Key Findings**
   - User-visible or decision-relevant issues.

4. **Data / State / Source Truth**
   - Wrong, stale, missing, or contradictory data.

5. **UX / Copy / Simplification**
   - Visual density, wording, hierarchy, accessibility, and simplification opportunities.

6. **Backend / Security / Governance**
   - Only issues material to trust, safety, or correctness.

7. **False Positives Rejected**
   - Claims investigated and rejected, with why.

8. **Evidence And Commands**
   - Tests run, browser paths, screenshots, local files, source anchors, and commands.

9. **What Was Not Proven**
   - Missing tests, live-provider gaps, inaccessible environments, evidence debt, coverage gaps, or open questions.

10. **Wave Verification Trail**
   - For multi-wave runs, list each wave summary and its verification certificate.

11. **Final Drift Check**
   - State that material final claims were checked against the final claim ledger, or name any remaining mismatch.

## Style Rules

- Be concise but evidence-rich.
- Do not bury the verdict under process.
- Use exact paths and commands.
- State uncertainty boundaries.
- Avoid saying "all good" unless all required evidence exists.
- Mention model/tool fallbacks when the requested verifier model was unavailable.
- Every material factual, severity, readiness, or safety claim must map to a ledger entry or explicit coverage/debt statement.
- The orchestrator writes the final synthesis. Independent Opus or `gpt-5.5 xhigh` verification checks the final claim ledger, evidence debt, and coverage gaps before that synthesis is written; it does not replace orchestrator authorship.

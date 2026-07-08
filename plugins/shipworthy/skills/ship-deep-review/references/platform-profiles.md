# Platform Profiles

Use these limits and model preferences when Deep Review dispatches agents or verification passes.

## Codex

- Hard concurrent-agent cap: 6.
- Use `gpt-5.5` with `xhigh` reasoning for the coordinator, all specialist agents, every wave verifier, and final synthesis when the tool surface supports it.
- If `gpt-5.5` is unavailable, use the strongest available GPT-5-class model with `xhigh` reasoning and disclose the fallback in the final report.
- Prefer bounded lanes with non-overlapping scope. Six good default lanes for repo/product work are runtime interaction, visual/UX polish, copy/simplification, state/API integration, backend/product trust, and tests/docs/release gate.
- Do not exceed the cap by leaving completed agents open. Close completed agents when their outputs have been read.
- For each wave, run the verifier after all specialist outputs are read and before the wave intelligence summary is written.

## Claude Code

- Claude Code does not have Codex's 6-agent concurrency limit.
- For a planned wave, launch all independent wave agents at once when the wave has 13 or fewer agents and scopes do not conflict.
- Use Sonnet for most specialist scout/deep-dive agents.
- Use Opus for:
  - every post-wave, pre-summary independent verification pass,
  - contradiction/severity tribunal work,
  - final no-overclaiming verification before the orchestrator writes the final synthesis.
- Use 10-13 concurrent agents only when the task decomposes cleanly, the user wants a large run, and budget/context supports it.
- Prefer 6-8 agents when the target is small, write scopes overlap, or the risk of duplicated work is high.
- If Claude Code cannot actually force a requested model for a given subagent, document the fallback and keep the verification gate.

## Cross-Platform Rule

The model allocation is part of the evidence protocol, not decoration. A wave summary must not be written until the independent verifier for that wave has completed and the orchestrator has read its output.

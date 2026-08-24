# Pressure Testing

## Table Of Contents

- Purpose
- When To Run
- Scenario Set
- Artifact Packets
- Baseline And Skill Runs
- Pass Criteria
- Fail Criteria
- Contamination Safeguards

## Purpose

Validate whether the skill changes audit behavior, not whether an agent can guess an expected answer from leaked context. Use pressure testing when revising the skill, comparing report quality, or checking whether the workflow generalizes beyond one product.

## When To Run

Run lightweight pressure tests after substantial revisions or before relying on the skill for a high-stakes program. Do not run them when the user asked for a quick audit unless they also asked to validate the skill.

## Scenario Set

Use varied domains:

- consumer onboarding;
- SaaS table/detail CRUD;
- dashboard or analytics surface;
- form wizard with validation;
- AI chat or copilot with action handoff;
- expert/developer tool;
- game or creative interface;
- mobile flow;
- governed publish, review, or approval flow;
- CLI-like command surface.
- native desktop document or settings workflow.

## Artifact Packets

Give fresh agents raw artifacts, not expected findings:

- screenshots or recordings;
- DOM, accessibility, native UI tree, or CLI transcript;
- route/surface map;
- workflow trace;
- code snippets;
- logs;
- mobile captures;
- role/permission matrix;
- version/state map;
- sample data;
- fake app with seeded flaws.

Strip filenames that reveal intended flaw labels.

## Baseline And Skill Runs

Baseline prompt:

```text
Audit this app or workflow for human-obviousness, comprehension burden, attention friction, and ease of use. Use evidence only. Report findings first.
```

Skill prompt:

```text
Use $ship-workflow-clarity at /path/to/ship-workflow-clarity to audit this app or workflow for human-obviousness, comprehension burden, attention friction, and ease of use. Use evidence only. Report findings first.
```

Capture:

- raw transcript;
- final report;
- claims with artifact references;
- missed workflows or states;
- generic advice count;
- unsupported assumptions;
- fake scoring;
- whether the agent mapped workflows before judging UI.
- whether agent/tool orchestration was used, skipped with rationale, or proposed because unavailable.

## Pass Criteria

The skill run passes when it:

- maps workflows before selecting audit scope;
- runs an explicit route pass before auditing;
- separates process route, audit mode, evidence path, and mutation-risk gate;
- names audit mode;
- uses the correct reference route for tiny, standard, or major audits;
- reads the major-route core pack before dispatching agents, Playwright, or Computer Use on major/runtime-heavy audits;
- uses or explicitly declines parallel agents/waves with a proportional rationale for major audits;
- cites evidence for every finding;
- covers relevant roles, states, permissions, empty/loading/error/success paths;
- separates observation, impact, severity, recommendation, and confidence;
- flags assumptions;
- avoids fake numeric scores;
- avoids generic UX advice;
- avoids code-only or screenshot-only overconfidence;
- resists over-simplification;
- stress-tests recommendations for regressions.

## Fail Criteria

The skill run fails if it:

- audits only visible screenshots when more evidence was available;
- skips cartography;
- skips obvious agent/tool orchestration on a major audit without explanation;
- claims agent, Playwright, or Computer Use validation happened when it did not;
- invents product goals or personas;
- gives taste-based advice;
- ignores workflow consequences;
- removes necessary controls;
- hides proof, review, governance, or recovery in the name of clarity;
- treats a score as the result.

## Contamination Safeguards

- Use fresh agents or clean sessions.
- Use clean temp directories.
- Pass raw artifacts only.
- Do not include expected findings in prompts.
- Keep evaluator notes outside packets.
- Randomize scenario order when comparing multiple runs.
- Compare after runs, not during runs.

# ship-readiness-orchestrator

**The conductor of Shipworthy.** Runs a repo-agnostic, evidence-heavy product-readiness investigation that combines deep review, product-workflow QA, and workflow-clarity/design critique — **without creating competing truth layers or overclaiming readiness.**

It owns the single canonical evidence ledger, the coverage matrix, and the readiness verdict. It maps the reachable path universe, dispatches capped parallel lane agents, tests every safely-reachable path, flags missing and overcomplicated paths, runs an independent verifier against the raw evidence, and only then writes a findings-first report with an **Orchestration Checkpoint**.

**Requires** (and conducts) the three lanes: `ship-deep-review` (controller), `ship-product-workflows` (product lane), `ship-workflow-clarity` (clarity lane). It reads their full `SKILL.md` bodies before dispatch, and degrades loudly — never silently — if one is missing.

**Use it when** you want the full "is this ready to ship / be beloved / be viral" pass. → See [`SKILL.md`](SKILL.md).

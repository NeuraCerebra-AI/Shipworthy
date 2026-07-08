# ship-readiness-orchestrator

**The conductor of Shipworthy.** Runs a repo-agnostic, evidence-heavy product-readiness investigation that combines deep review, product-workflow QA, and workflow-clarity/design critique — **without creating competing truth layers or overclaiming readiness.**

It owns the single canonical evidence ledger, the coverage matrix, and the readiness verdict. It maps the reachable path universe, asks for multi-agent authorization when platform policy requires it, dispatches capped parallel lane agents only when explicitly authorized and safe, tests every safely-reachable path, flags missing and overcomplicated paths, runs an independent verifier against the raw evidence, and only then writes a findings-first report with an **Orchestration Checkpoint**. If authorization is not granted, it runs the same lane roster sequentially and records the orchestration debt.

**Trigger phrase:** ask `are we shipworthy?` or mention `shipworthy` operationally. That means full blast unless you explicitly narrow the pass.

Full blast means at least three verified waves, adaptive extra waves when coverage is unfinished, path-universe closure over all safe discoverable paths, and a mandatory self-contained HTML report rendered from the final ledger.

**Requires** (and conducts) the three lanes: `ship-deep-review` (controller), `ship-product-workflows` (product lane), `ship-workflow-clarity` (clarity lane). It reads their full `SKILL.md` bodies before dispatch, and degrades loudly — never silently — if one is missing.

**Use it when** you want the full "is this ready to ship / be beloved / be viral" pass. → See [`SKILL.md`](SKILL.md).

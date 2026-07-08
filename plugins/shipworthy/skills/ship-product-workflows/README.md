# ship-product-workflows

**The path walker.** Safely audits product workflows the way a rigorous QA lead would: discover meaningful user paths, try or trace them with the strongest safe evidence available, find user-visible breakpoints, identify likely fixes, and give exact verification steps. "Every path" is a coverage ambition with honest exclusions — never a claim of omniscience.

Covers UI behavior, state, persistence, forms, navigation, permissions, responsive checks, accessibility smoke, and the **backend/API symptoms that surface in the UI** (failed requests, stale state, missing persistence, misleading UI after a backend failure). Calls `ship-workflow-clarity` as a specialist lane when comprehension/consequence/recovery/trust risks appear.

**Use it alone when** you need to know where a specific app or feature actually breaks for a real user. → See [`SKILL.md`](SKILL.md).

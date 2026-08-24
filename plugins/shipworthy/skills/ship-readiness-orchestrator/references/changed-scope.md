# Changed-scope mode — fast in-session re-audits

The full path audit is thorough but heavy. When someone is iterating inside Codex or
Claude Code — "I just changed X, is it ready before I open the PR?" — re-running the whole
thing every time is too slow, so they won't. Changed-scope mode audits **what changed plus
the paths it can affect**, and returns a **scoped** verdict.

## When to use it

- **Delta (this mode):** mid-session iteration, pre-PR sanity, "did my change break a path."
- **Full audit:** first pass on a codebase, a release gate, or after a large/structural change.

State which mode you ran. A delta verdict is *"ready with respect to these changes,"* never
*"the whole product is ready."*

## How to scope

1. **Get the changed surface.** From `git diff --name-only <base>...HEAD` (or the user names
   the changed files/feature). If there's no diff signal, ask what changed rather than
   guessing.
2. **Map changed code → affected user paths.** Which flows route through the changed files,
   components, endpoints, or state.
3. **Audit two rings:**
   - **Direct:** every path that exercises the changed code.
   - **Blast radius:** adjacent paths that could *regress* from the change — anything sharing
     a component, hook, endpoint, global/session state, or data contract with the change,
     plus the immediate upstream and downstream of the changed flow.
4. **Everything else is `out_of_scope` for this run** — labelled as such in the coverage map,
   never as `covered`. Honesty about what you *didn't* look at is the point.

## The guardrail (why this isn't just "audit the diff")

A change can break a path far from the lines it touched: a shared utility, a global store, a
changed API shape, a modified auth guard. **Auditing only the diff in isolation misses exactly
these regressions.** Changed-scope mode must reason about coupling and blast radius, not just
changed files — that reasoning *is* the value over a naive diff check. When the blast radius is
genuinely unclear or the change is structural, say so and recommend a full audit instead.

## New vs. fixed

To show what a change introduced or resolved, compare this run's findings to the prior run:
- **Locally:** diff against a saved prior ledger (`ledger.json`) by finding identity.
- **In CI via SARIF:** GitHub computes new/fixed natively from a source-branch vs. target-branch
  SARIF pair (see `references/exports-and-ci.md`) — no local bookkeeping needed.

Fingerprints are stable across runs (see the SARIF exporter), so "new/fixed/persistent" stays
accurate even as wording changes between runs.

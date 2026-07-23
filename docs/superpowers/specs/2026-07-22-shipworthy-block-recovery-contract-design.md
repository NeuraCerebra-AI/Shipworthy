# Shipworthy Block-Recovery Contract Design

## Purpose

Prevent a full Shipworthy run from stopping merely because its first browser,
agent, lane, or evidence method fails. A block must trigger bounded recovery
through safe, already-available alternatives. Shipworthy may report a final
block only after every applicable authorized alternative has been attempted
and recorded.

This contract strengthens completion behavior without promising impossible or
unsafe success. Missing credentials, unavailable capabilities, external
outages, destructive-only paths, and policy restrictions may remain blocked.
Supporting source or command evidence may explain a frontend block, but it
must not be relabeled as completed frontend execution.

## User-Visible Authorization Contract

Replace the short combined goal/subagent authorization question with a concise
execution contract:

> Shipworthy full blast is a long-running audit. Recommended: reply yes to
> authorize persistent goal mode and parallel subagents. If authorized,
> Shipworthy will run every required wave and verifier gate, complete every
> safely testable discovered path, recover blocked lanes through applicable
> safe alternative methods, preserve unresolved paths as evidence debt, and
> generate the final HTML report. The goal will not be marked complete until
> the required gates and artifacts reconcile. If a path remains blocked after
> all applicable authorized alternatives are exhausted, the report will state
> exactly what was tried and what remains unfinished.

The question authorizes goal mode and subagents; it does not authorize unsafe,
destructive, paid, credential-expanding, production-mutating, or otherwise
out-of-scope actions.

## Persistent Goal Contract

When goal mode is available and authorized, the created goal objective must
repeat the operational commitments rather than merely say “run Shipworthy”:

- complete every required wave and verifier barrier;
- resume unfinished waves after a recovered failure;
- apply the block-recovery ladder before accepting a block;
- generate and validate the canonical ledger, checkpoint, JSON, HTML, SARIF,
  and bundle artifacts required by the selected run;
- mark the goal complete only after the final mechanical gate succeeds;
- if recovery is genuinely exhausted, keep the goal/report truthfully blocked
  or incomplete and name the exact remaining work.

On compaction or resumption, reread the active goal and the canonical
orchestration checkpoint before dispatching more work.

## Canonical Recovery Ladder

Define the ladder once in the readiness orchestrator and reference it from
browser/runtime lane prompts:

1. Record the failed capability, exact error, affected paths, and current wave.
2. Release or clean up the failed capability once when safe host cleanup exists.
3. Retry once only when the failure is plausibly transient and retrying is safe.
4. Switch to an already-available independent Playwright process or isolated
   context for a failed native/attached browser. The same locked binding is not
   a fallback.
5. Try another already-authorized frontend capability, such as another native
   browser, Chrome, Computer Use, or a target-owned deterministic browser test.
6. Reassign the affected lane or execute it sequentially through the designated
   runtime driver when agent execution—not the target behavior—is blocked.
7. Use target-owned tests, API/CLI/log inspection, and source tracing as
   supporting or diagnostic evidence. These methods do not substitute for
   required frontend execution.
8. Resume the unfinished wave and verifier barrier after recovery.
9. Declare a terminal block only after every applicable authorized alternative
   is attempted or explicitly inapplicable, with a reason for each.

Step 6 never permits controller self-verification. A failed verifier must be
reassigned to a fresh independent verifier when authorized and available. If no
independent verifier remains, preserve verifier evidence debt and downgrade or
block after recovery exhaustion. Sequential recovery of any other agent lane
must retain the loss of independent-agent coverage as orchestration debt.

An actually executed target-owned browser/E2E test may serve as a frontend
recovery route only for the real frontend steps and assertions it drives.
Unit, API, CLI, source, logs, unexecuted browser-test code, and inspection of
existing tests remain supporting evidence and cannot satisfy required frontend
execution.

The ladder is bounded: no repeated blind retries, package installation, browser
download, credential acquisition, provider calls, destructive mutation, or
target modification merely to obtain evidence.

Safe cleanup must not close or reset a user-owned/shared session, discard
material state, change credentials, or mutate the target without the existing
exact-action and reset/disposable-environment authorization. Before each
alternative and before resuming a wave, revalidate the target fingerprint,
role/account, fixture or state continuity, and safe-test boundary. If continuity
cannot be proved, keep prior evidence scoped to its observed state and restart
only the affected path from a known safe state.

## Checkpoint And Mechanical Gate

Extend the schema-external orchestration checkpoint with a bounded
`recovery_attempts` array of bounded summaries, each covering one homogeneous
set of semantic paths that share the same recovery outcome. Split partially
recovered path sets into separate records. Each row records:

- `recovery_id`;
- affected lane, wave, and semantic path keys;
- failed capability and normalized failure class;
- an ordered candidate-method-family inventory captured at failure time;
- for each candidate: stable method identity; authorization, availability,
  applicability, and safety disposition; attempt count; result; reason; and
  evidence reference;
- safe cleanup result;
- resumed wave/lane evidence path when recovered;
- remaining evidence-debt IDs;
- record status: `active`, `recovered`, `exhausted`, or `user_stopped`.

One plausibly transient retry is permitted before alternatives. After that,
each distinct candidate method may be attempted at most once. A candidate that
is not attempted must have a concrete `unavailable`, `forbidden`, `unsafe`, or
`inapplicable` disposition and reason. Recovery still in progress keeps
`audit_status: active`; a final `blocked` state is legal only after every
applicable authorized candidate is attempted and every homogeneous path record
has reached a terminal truthful state: recovered records are allowed, while
every record retaining unresolved material debt must be `exhausted` and no
record may remain `active`. A user or policy stop immediately becomes
`user_stopped`, never `exhausted`.

Checkpoint summaries are capped at 128 records and eight canonical method
families: native/attached browser, Chrome, Computer Use, independent
Playwright, target-owned frontend/E2E, reassigned agent/runtime driver,
supporting diagnostics, and other authorized frontend. Every distinct
capability instance remains listed in bounded referenced recovery-receipt JSON;
the checkpoint stores each detail file's safe path, count, and digest. If
detail exceeds one bounded file, deterministically split it into numbered
continuation files and retain every file in the evidence bundle. Reaching a
summary or file cap keeps the recovery and audit `active`, records overflow
debt, and still renders mandatory HTML; it can never imply exhaustion or
truncate an applicable capability.

Immediately before declaring `exhausted`, refresh the available/authorized
capability inventory once and record a delta from the failure-time inventory.
A newly discovered or newly available applicable safe capability reopens the
record as `active` and receives its one bounded attempt. Removed or changed
capabilities remain in history with their new disposition and reason. The
refresh uses the same method-family grouping, continuation files, and
one-attempt rules.

The renderer must reject:

- a terminal block with an applicable method neither attempted nor explained;
- `recovered` without resumed-lane evidence;
- a completed audit with an exhausted recovery retaining material debt;
- repeated attempts for one candidate method, duplicate method identities, or
  more than the bounded retry limit;
- a blocked audit while a recovery record remains active;
- an exhausted record caused by a user or policy stop;
- exhaustion without the final capability-inventory refresh and delta;
- overflow or truncated receipt detail represented as exhausted;
- goal completion before recovery records, lanes, verifier state, artifacts,
  and frontier closure reconcile;
- repeated identical retries presented as alternative methods.

Truthful active, blocked, or user-stopped runs must still render HTML.

Browser receipts retain every intermediate attempt. Extend
`browser_failover_status` to `not_needed`, `active`, `succeeded`, `blocked`, or
`user_stopped`. `succeeded` means all affected browser semantic paths resumed
with proof, either after the one safe same-capability transient retry or through
a qualifying authorized frontend alternative; it is not limited to Playwright
and is not invalidated merely because an earlier candidate failed. `active`
means recovery or the required final inventory refresh remains in progress.
`blocked` means at least one affected browser path still has material debt after
inventory exhaustion. `user_stopped` means the user or policy ended recovery.
Only `not_needed` or fully reconciled `succeeded` may participate in audit/goal
completion. Validate final status against unresolved path/debt linkage and
resumed evidence while preserving the same-binding rejection for claimed
alternative-browser recovery.

Derive aggregate checkpoint and browser recovery status deterministically:

1. `user_stopped` if any record was stopped by the user or policy;
2. otherwise `active` if any record or required inventory refresh remains active;
3. otherwise `blocked` if any exhausted record retains material debt;
4. otherwise `succeeded` when recovery occurred and every affected path
   reconciles to resumed evidence;
5. otherwise `not_needed`.

Thus recovered and exhausted records may coexist in an honest blocked run;
active plus exhausted records remain active until recovery finishes.

## Agent And Verifier Propagation

Keep prompts short. Browser/runtime prompts receive one sentence directing them
to the canonical recovery contract and requiring a recovery packet. The
controller owns cross-method progression and resumption. The independent
verifier checks that:

- the ladder was followed in order where applicable;
- each skipped alternative has a concrete inapplicability or safety reason;
- recovered lanes actually resumed;
- target fingerprint, role/account, fixture/state continuity, and safe-test
  boundary were revalidated before alternatives and resumption;
- supporting evidence was not substituted for frontend execution;
- the controller did not replace an independent verifier with self-verification;
- the goal was not completed early.

Standalone `ship-deep-review`, `ship-product-workflows`, and
`ship-workflow-clarity` browser-capable prompts preserve their existing compact
independent-Playwright fallback and return recovery results to their controller.

## Human-Readable HTML

Do not add a large default section. In the early coverage-confidence summary,
state whether recovery was unnecessary, active/in progress, succeeded,
exhausted/blocked, or user-stopped. For blocked paths, show:

- what failed;
- alternatives attempted;
- why remaining alternatives were unavailable, forbidden, unsafe, or
  inapplicable;
- where execution resumed, or what remains NOT_PROVEN.

Detailed attempt rows remain inside a collapsed native HTML `<details>` block
and the bounded checkpoint JSON. Findings and actions stay visually primary.

## Focused Verification

Use RED/GREEN tests for:

- authorization wording and goal-objective contract;
- transient retry followed by successful resumption;
- native-browser failure followed by independent Playwright recovery;
- mixed recovered and exhausted histories;
- mixed active and exhausted history aggregating to active;
- recovered and exhausted history aggregating to blocked;
- failed Playwright followed by proven Chrome or Computer Use recovery;
- partially recovered paths split into homogeneous recovery records;
- agent-lane failure followed by sequential recovery;
- verifier failure requiring a fresh independent verifier or retained debt;
- rejected same-binding fallback;
- rejected repeated identical retry;
- rejected duplicate candidate identity or attempt count above one;
- rejected terminal block with an unexplained applicable alternative;
- rejected recovered state without resumed evidence;
- successful same-capability transient retry mapping to `succeeded`;
- active and user-stopped browser recovery remaining renderable but unable to
  satisfy completion;
- deterministic continuation receipts and overflow remaining active;
- exhaustion rejected without the final inventory refresh;
- a newly discovered capability reopening recovery as active;
- rejected recovery across changed target, role, fixture, or unsafe cleanup;
- user/policy stop remaining `user_stopped` rather than exhausted;
- rejected premature goal completion;
- truthful exhausted recovery rendering readable HTML;
- source/CLI evidence remaining supporting rather than frontend proof;
- escaping and deterministic collapsed recovery detail, including explicit
  in-progress and user-stopped summaries;
- exact Codex/Claude installed-copy parity using temporary fixtures only.

Then run the complete skill-product suite, four direct legacy suites,
compilation, frontier validation, `git diff --check`, forbidden-behavior scans,
and cache/build-noise checks. Do not modify real installed copies until the
repository change is separately approved and verified.

## Scope Boundary

This remains four self-contained skills. It adds no package, service, daemon,
database, browser engine, crawler, provider integration, persistence layer, or
public CLI. The checkpoint remains a run artifact written by the skill-owned
dependency-free scripts.

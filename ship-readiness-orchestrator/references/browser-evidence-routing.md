# Browser Evidence Routing

## Decision

Use a host-provided native browser or computer-use capability as the default for adaptive exploration in Codex and Claude-style workflows. It is the right path for discovering routes, reacting to unexpected state, following human-visible controls, and collecting bounded observations from a live product.

Use an existing target-owned Playwright setup only when the work needs deterministic replay, explicit assertions, isolated contexts, traces, cross-browser checks, or CI regression proof. An already-enabled host Playwright capability is also eligible for browser failover when it is independent of the failed binding and requires no installation or target change. Shipworthy never installs Playwright and must never change the target application merely to obtain browser evidence. If the required capability is absent, record the gap as evidence debt.

This is a capability decision, not a host API contract. Select the available native browser, attached-browser, or computer-use tool by what it can safely observe and control; do not assume a particular tool name or version.

## Browser Failover Contract

If the selected native or attached browser becomes locked, disconnected, stale, or unavailable, do not stop the lane. Record the failing capability and error, release it once when the host exposes safe cleanup, then follow the Block-Recovery Ladder below. Calling `tab.playwright` or an equivalent API on the same locked browser binding does not count as the fallback and is not an independent fallback.

### Block-Recovery Ladder

For every affected path, use this bounded order and record each disposition:

1. Record the failure without converting any path to covered.
2. Perform one safe cleanup when available. Cleanup must not close user/shared sessions, discard state, change credentials, mutate the target, or hide evidence.
3. Revalidate target, role, state, viewport, and fixture continuity, then make one transient retry on the failed method when the failure is plausibly transient.
4. Try an already available independent Playwright process or isolated context.
5. Try another already-authorized frontend capability, including Chrome, Computer Use, or target-owned end-to-end automation.
6. Reassign the unfinished runtime lane or use one sequential coordinated runtime driver when agent/browser ownership caused the failure.
7. Use source, CLI, API, tests, and logs only as supporting evidence; they never recover required frontend coverage.
8. After successful recovery, resume the unfinished wave from its unresolved frontier rows. Do not restart completed work or skip the verifier gate.

Before each alternative and before resumption, revalidate continuity. A target-owned end-to-end result proves only the semantic paths it actually drove and asserted. An ended verifier must be replaced by a fresh independent verifier; controller self-verification is forbidden. If replacement is unavailable, retain verifier debt.

Shipworthy must not install Playwright, download browser binaries, change credentials, close user sessions, or change the target merely to recover evidence. Keep recovery `active` while any applicable, safe, authorized, available method remains. Before declaring the ladder exhausted, perform an inventory refresh and compare the final capability inventory with the initial inventory; a newly available method reopens recovery. Use `blocked` only when the refreshed inventory proves every applicable safe authorized method was attempted or unavailable. Use `user_stopped` when the user ends recovery.

Retain bounded recovery summaries, per-candidate receipts, and initial/final/inventory-delta descriptors as JSON. Use continuation receipts rather than truncating required evidence. List safe relative receipt paths in `recovery_receipt_paths` and compatible browser receipts in `browser_failover_receipt_paths`. Record method family, binding/profile identity, isolation proof, continuity checks, attempt count, result, evidence refs, resumed paths, and remaining debt. `browser_failover_status` and `recovery_status` may be `not_needed`, `active`, `succeeded`, `blocked`, or `user_stopped`. A successful independent Playwright, Chrome, Computer Use, target-owned E2E, or safe reassigned/sequential frontend driver may set recovery to `succeeded` when it restores the affected execution and the unfinished wave resumes. Earlier failed candidates do not force a recovered ladder to remain blocked.

## Proof Boundaries

- A screenshot proves only the state visible at capture time; it does not prove an entire workflow, earlier or later state, persistence, accessibility, or hidden behavior.
- A native interactive trace can support the steps actually observed, subject to its recorded limitations.
- A passing Playwright assertion supports only its declared target, fixture, browser, steps, and assertion boundary.
- Browser evidence must not silently upgrade a finding to `Confirmed` or verifier status to `approved`. The canonical ledger's proof and independent-verifier rules still apply.
- Record the chosen capability, why it was chosen, target fingerprint, path and step boundaries, observed outcomes, artifacts, unavailable channels, limitations, and what remains not proven.
- Never treat a screenshot, trace, recording, or automated pass as self-approving evidence.

## Safety And Product Boundary

The host drives tools; Shipworthy only routes work and records evidence. Do not install packages, start unapproved services, use credentials without authorization, mutate production, or perform destructive actions merely to improve evidence. Preserve target-repository instructions and use safe fixtures or isolated contexts when the target already provides them.

Shipworthy operates through the four public skills and their skill-owned resources without requiring another product surface. Browser routing, the four skill names and triggers, proof ceilings, verifier rules, and the mandatory HTML report contract remain available in standalone skill operation.

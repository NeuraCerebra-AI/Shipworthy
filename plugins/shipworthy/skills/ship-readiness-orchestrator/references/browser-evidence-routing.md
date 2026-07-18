# Browser Evidence Routing

## Decision

Use a host-provided native browser or computer-use capability as the default for adaptive exploration in Codex and Claude-style workflows. It is the right path for discovering routes, reacting to unexpected state, following human-visible controls, and collecting bounded observations from a live product.

Use an existing target-owned Playwright setup only when the work needs deterministic replay, explicit assertions, isolated contexts, traces, cross-browser checks, or CI regression proof. Shipworthy never installs Playwright and must never change the target application merely to obtain browser evidence. If the required capability is absent, record the gap as evidence debt.

This is a capability decision, not a host API contract. Select the available native browser, attached-browser, or computer-use tool by what it can safely observe and control; do not assume a particular tool name or version.

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

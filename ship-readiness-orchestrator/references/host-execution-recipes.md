# Host Execution Recipes

## Boundary

The host and target repository own execution. Shipworthy routes work, imports bounded
results, and records evidence debt; it is not a general command runner. Read the target-repository
instructions before selecting any command, keep the target read-only by default, and retain
local-only artifacts unless the user explicitly authorizes another destination. Never add a
dependency, start an unapproved service, or change the application solely to collect evidence.

For each material claim or evidence need, evaluate capabilities in this order and run
every applicable safe path whose proof boundary adds relevant evidence. The paths are
cumulative when they prove different things, not global alternatives. Target-owned tests
are supporting evidence and never replace the required native frontend path-walk for a
full flagship run. Stop only for that specific claim when its declared evidence boundary
is sufficient and the flagship frontend gate remains satisfied; continue with other
applicable safe paths and other material claims.

Use this selection order for each path:

1. **Discover and run target-owned tests.** Read repository instructions and existing manifests or CI configuration, then use the exact documented command in its intended environment. Recognize existing `pytest`, `npm test`, JUnit, and SARIF output; do not synthesize a replacement command.
2. **Use native browser or computer-use for adaptive discovery.** Follow `browser-evidence-routing.md` and record only the paths and visible states actually observed.
3. **Reuse an existing target-owned Playwright setup for deterministic replay.** An existing `playwright test` configuration may provide assertions, screenshots, or traces. Preserve its project, fixture, browser, and assertion boundary.
4. **Propose a minimal target-owned Playwright test only with explicit user authorization.** Explain the proposed file and target change first. Do not create it merely because native evidence is unavailable.
5. **Record unavailable execution as evidence debt.** Name the missing capability or blocked command and the specific claim that remains not proven.

## Safety Check Before Execution

- Obey target-repository instructions, including working directory, environment, and test isolation.
- Stay read-only by default. Use a safe fixture, isolated account, disposable data, or documented reset when a test mutates state.
- Require explicit authorization for destructive, paid, publishing, credentialed, production, or irreversible actions even when a repository command exists.
- Do not use credentials or secrets unless the user authorized that exact use; redact them from diagnostics and artifacts.
- Keep screenshots, traces, JUnit, SARIF, logs, and normalized evidence as local-only artifacts. Record their paths and digests without uploading them.
- Treat an exit code or report as evidence within its declared test boundary, never as automatic verifier approval or proof of the entire workflow.

## Bounded Recognition, Not Command Construction

The host may recognize a repository's already-declared `pytest`, `npm test`, or
`playwright test` entry point and may import existing JUnit or SARIF output. This reference
does not authorize guessing flags, evaluating arbitrary project text as shell input, installing
tools, or exposing a Shipworthy execution command. If the declared command cannot run safely
and exactly as documented, preserve the gap as evidence debt.

## Verification Limit

The static forbidden-surface check is a defense-in-depth reviewed packaged-surface policy,
not proof that arbitrary Python behavior cannot evade analysis.
OS-level containment remains `NOT_PROVEN`; independent review and forbidden-behavior `rg` scans are still required. Keep
runtime-version, network-containment, and environment claims bounded to separately captured
evidence.

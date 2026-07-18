# Lean host-native RED/GREEN evidence ledger

**Evidence status:** The entries below preserve the original RED/GREEN
observations captured during Tasks 1-5 and the audit-ledger repair. Task 6 then
reran the combined focused suites, complete suite, legacy contracts, packaging,
preflight, compatibility, parity, rollback, compile, and hygiene checks in the
feature worktree. Original RED observations remain labeled as captured evidence
because a genuine pre-implementation failure cannot be recreated after the
implementation exists.

Counts use `passed/failed` when both were captured. A single number means the
captured report stated that many failures or passes, as indicated. These records
are deliberately not rewritten into cleaner-looking cycles after repairs.

## Pre-change baselines

| Scope | Captured result | Status |
| --- | ---: | --- |
| Phase 0/core suite | 554 passed | Subagent-captured baseline |
| Legacy skill contract | 120 passed | Subagent-captured baseline |
| Legacy HTML renderer | 174 passed | Subagent-captured baseline |
| Legacy SARIF renderer | 22 passed | Subagent-captured baseline |
| Legacy evidence bundle | 17 passed | Subagent-captured baseline |

## Task 1 — native-browser-first skill routing

Primary cycle:

| Stage | Captured result | Meaning |
| --- | ---: | --- |
| RED | 122 passed, 7 failed | New routing, proof-ceiling, and preservation checks failed before the skill/reference edits. |
| GREEN | 129 passed | Initial minimal routing implementation satisfied the primary contract additions. |
| Final focused | 139 passed | Focused contract total after the later Task 1 repairs and additions. |

Quality review found that the first wording/contract pass did not fully pin the
native-versus-Playwright distinction and proof ceilings. The repair was kept as
a separate cycle: **130 passed, 4 failed** at RED, followed by the final focused
**139 passed** result. Existing skill names, triggers, skill-only operation, and
mandatory HTML reporting were retained.

## Task 2 — bounded browser-evidence envelope

Primary cycle:

| Stage | Captured result | Meaning |
| --- | ---: | --- |
| RED | 32 failed | Contract and hostile-boundary tests preceded the model and schema implementation. |
| GREEN | 42 passed | Strict envelope, bounded parser, and frozen schema contract satisfied the focused suite. |

Review repairs remained visible:

- **37 passed, 3 failed** — first repair RED for hostile-boundary/strictness gaps;
- **40 passed, 1 failed** — metadata/schema consistency repair RED;
- **38 passed, 4 failed** — simplification and shared-validation repair RED;
- **42 passed** — final focused Task 2 GREEN.

The repair direction consolidated validation around existing bounded contract
utilities, kept artifact bytes caller-supplied, rejected unsafe paths and
unsupported input, and retained bounded human-readable diagnostics.

## Task 3 — native and Playwright evidence normalization

Primary cycle:

| Stage | Captured result | Meaning |
| --- | ---: | --- |
| RED | 20 failed | Importer behavior was specified before implementation. |
| GREEN | 20 passed | Initial native and Playwright normalization behavior passed. |

Independent review then exposed additional identity, attachment, resource, and
side-effect boundaries. Each repair was test-first:

- **19 passed, 1 failed**;
- **20 passed, 8 failed**;
- **25 passed, 15 failed**;
- **38 passed, 3 failed**;
- final focused Task 3 result: **41 passed**.

The repaired adapters retain and seal raw supplied evidence, require exact
attachment digest/size matches, preserve missing/corrupt/undeclared attachment
debt, reject ambiguous Playwright identity and unsafe paths, and expose no
finding, readiness, browser, subprocess, socket, or arbitrary-read surface.

## Task 4 — canonical attachment and report lineage

Primary and repair observations:

| Stage | Captured result | Meaning |
| --- | ---: | --- |
| RED | collection error: `ModuleNotFoundError` | The evidence-attachment module did not exist when its tests were introduced. |
| GREEN | 5 passed | Initial pure attachment behavior passed. |
| RED | `KeyError` in bundle manifest | New lineage fields were not yet represented consistently in the manifest. |
| Quality RED | 7 passed, 40 failed | Broader reporting/provenance review exposed incomplete behavior. |
| Provenance RED | collection failure: missing type | Required provenance type was absent during review repair. |
| Seal RED | 3 failed | Undeclared attachment seal behavior was not yet correct. |
| Focused checkpoint | 62 passed | Combined Task 3+4 suites after repairs. |
| Full checkpoint | 658 passed | Full suite at the Task 4 checkpoint. |

Reviewer-driven repairs authenticated normalized inputs before attachment,
rejected ID/digest/path collisions and forged provenance, represented missing
attachments without fake artifacts, preserved canonical finding fields and
gate precedence, and projected the same lineage through HTML, SARIF, and the
bundle. These are checkpoint results, not the final release gate.

## Task 5 — host-owned execution recipes and boundary scanner

Primary and review cycles:

| Stage | Captured result | Meaning |
| --- | ---: | --- |
| Primary RED | pytest: 2 passed, 3 failed; contract: 134 passed, 6 failed | Decision order and host/core boundary were not yet implemented. |
| Integration RED | semantic/scanner: 6 passed, 18 failed; contract: 140 passed, 1 failed | Most contract behavior had landed, but the semantic/scanner boundary and one contract check still failed. |
| Quality RED | 13 passed, 24 failed | Quality review found scanner/recipe coverage and metadata gaps. |
| Metadata repair | 49 passed | Current focused metadata/scanner repair checkpoint. |
| Scope RED | 50 passed, 5 failed | Scanner scope and packaged-surface behavior still needed repair. |
| Scope repair RED | 54 passed, 1 failed | One final scoped boundary remained. |
| Final focused checkpoint | 55 passed | Host execution boundary suite after repair; final Task 6 verification remained pending. |
| Final contract | 139 passed | Skill contract after Task 5 integration. |
| Full checkpoint | 713 passed | Full suite at the Task 5 checkpoint; not a final release-gate result. |

The repairs made the decision order explicit, reviewed packaged Python source
rather than only an easy subset, preserved target-owned execution and local-only
artifacts, and prohibited browser launch, dependency installation, networking,
daemon/database/MCP/portal/scheduler/credential/provider surfaces in the core.

## Audit-ledger source-template repair

The claim was verified against the working tree: two source documents reference
`templates/audit-ledger.md`, while the generated-output ignore pattern
`**/audit-ledger.md` also matched that source template. The repair adds one
narrow negation and includes the source template.

| Stage | Captured result | Meaning |
| --- | ---: | --- |
| RED | 3 failed | Template presence/tracking/reference contract failed before the ignore repair and source file. |
| Review RED | 1 failed | Canonical template headings were incomplete during review. |
| GREEN | 3 passed | Focused template contract passed after the heading repair. |

This is **subagent-captured evidence**. The file and ignore exception are local;
their availability in `origin/main` is **NOT_PROVEN** until the eventual commit
is reviewed and merged. No real `~/.codex/skills` or `~/.claude/skills` copy was
written.

## Task 6 release evidence

Fresh local results from the feature worktree:

| Scope | Result |
| --- | ---: |
| Lean focused suite plus audit-ledger template contract | 162 passed |
| Complete Phase 0/core suite | 733 passed |
| Legacy skill contract | 139 passed |
| Legacy HTML renderer | 174 passed |
| Legacy SARIF renderer | 22 passed |
| Legacy evidence bundle | 17 passed |
| Packaging/preflight/runtime-receipt group | 164 passed |
| Compatibility, dual-render, parity, lifecycle, retirement group | 106 passed |

The skill-contract total intentionally increased from the 120-test baseline to
139 because the native-browser/Playwright routing, proof ceilings, host-owned
execution order, mandatory HTML preservation, and audit-template/install
contracts added 19 tests. The other three legacy totals remain unchanged.

`python -m compileall -q src tests plugins/shipworthy/skills`, `ruff check src
tests`, and `git diff --check` passed. The exact forbidden-behavior scan returned
37 matches, all in tests as negative/adversarial fixtures or the existing Phase
0 validation harness; it returned no production `src` match. The semantic
packaged-surface boundary suite is included in the passing totals above.

An offline wheel was built only under `/tmp`. Its final post-review SHA-256 was
`55e53861b82ad97a799c8d000968e90414ba8736205f93209dc59f871bfa32a9`.
Archive inspection confirmed
`shipworthy/schemas/v1/browser-evidence-envelope.schema.json`, compatibility
metadata, importers, evidence attachment, and migration rehearsal modules were
present. This proves one local offline build and package-resource inspection;
it does not prove reproducible locked wheels across the supported runtime
matrix.

The lock-held offline SBOM command executed successfully into `/tmp`. It
produced a CycloneDX 1.6 document containing 73 components, 89,606 bytes, with
SHA-256
`3e7afd658f0f1613c1bfac7f2f6aa629bcdcabed077c02a9d801f62306b73e8f`.
This proves SBOM execution in the current environment only.

Exact evidence receipts used the exploratory browser fixture with producer
`codex-native-browser@1.2.3` and the existing Playwright JSON fixture with
producer `playwright@1.54.0`. The native source SHA-256 is
`c60afa0ed39a014443e2788f1e0908f6fa9532e70d74a056b29c2921b4f3cb77`;
its supplied screenshot SHA-256 is
`9003dc7c8d2b17a177fd502124677d907e2f90125c8fb3faf61602ae44fb4ec3`,
and its undeclared accessibility bytes remain an explicitly missing artifact.
The Playwright source SHA-256 is
`6efcf1b0b15dabf1b3e0be9230dc528a53f0b55c54c663cc6cdfc828a151a1d9`;
its screenshot and trace SHA-256 values are respectively
`12eeb235417c1a910054261255c559eb1341f7ecd404cbd6175cebcfd76587a0`
and `92ea5892931fa0354fc209aceae46ccebb669d7a416732dae9442677bedf36fc`.
Both attach only to `FND-CHECKOUT-001`; both retain the `confirmed_only` failed
gate with that same blocking ID. Their canonical lineage operations are
`browser-evidence/v1?role=source&mode=exploratory&driver=in-app-browser&producer_version=1.2.3`
and
`browser-evidence/v1?role=source&mode=deterministic_replay&driver=existing-playwright-json-reporter&producer_version=1.54.0`.
For each receipt, the browser-evidence projection is identical in SARIF and the
bundle manifest, while HTML remains the mandatory self-contained rendering of
the same ledger.

Synthetic installed-copy parity was exact for both Codex and Claude fixture
shapes: 72 files, zero issues, repository and installed tree SHA-256
`7f2668888abd6234205f5f2c93494c52f5bc5bbc414ea501cecf514c164ce2c2`.
No real installed-copy directory was read or written. An injected upgrade
failure restored the exact prior state SHA-256
`f8c1d7735b0a958386f3afd3519ca6196aea4a32842893d52bd5d4549543dfa4`;
an incompatible upgrade retained that same before/after digest; authorized
optional-core uninstall preserved canonical evidence and skill-only operation.

The legacy `readiness-v0.json` dual-render receipt ran in `comparison_only`
mode with `skills_switched_to_core: false`. Legacy and v1 retained canonical
finding ID `FND-LEGACY-1E9F15AB7D1EA4785B7B2C53`; all nine required surfaces
were compared; all expected action/proof/gate/count/HTML/SARIF/bundle/lineage
differences were explained; unexplained evidence-debt count was zero. The
legacy and v1 bundle SHA-256 values were
`6f1c1efc0cc15095e472c68060058bd27d4fa25af979eca1f8ff4adb3f9c81b8`
and `9f8f07ad45393a72cc554782b2fe32e4f73c25d21c5fa246bc7f180d92817187`.

The independent specification review found one P1 compatibility gap: the
preflight's advertised resource closure still described the pre-browser core,
so it could enable a partial installation missing the new evidence modules.
The repair was test-first: **44 passed, 10 failed** at RED, then **54 passed**
at GREEN. The compatibility sidecars and preflight now require the browser
envelope, evidence attachment, importer package closure, Playwright report
importer, and browser-evidence schema, and explicitly advertise browser intake,
Playwright report import, and evidence attachment. Removing any advertised
feature module disables only the core and preserves usable skills.

The specification re-review requested one explicit schema-deletion case. The
implementation already rejected the missing schema, so this coverage-only
addition was not misreported as a new RED cycle. The focused preflight suite
then passed **55 tests**, and the independent specification reviewer approved
the repair.

The separate quality review found two concurrency/safety gaps in temporary
evidence tooling: lifecycle rollback could be redirected by a whole-root swap,
and parity could report `exact` from unstable path reads. The primary
adversarial RED was **29 passed, 4 failed**. Descriptor-bound lifecycle roots,
descriptor/inode-bound parity reads, and repeated tree snapshots produced
**32 passed, 1 failed**; preserving the prior symlink diagnostic then produced
**33 passed**. Follow-up review found malformed metadata masking and an
unbound fixture marker: **2 failed** at RED, then **35 passed**. An in-place
marker rewrite was separately captured as **1 failed**, then **36 passed**.
Finally, forced initial-binding failure and partial-close handling produced
**2 failed**, then **38 passed** after descriptor ownership cleanup. The
independent quality reviewer approved the final repair.

Final cache-clean lifecycle receipts show exact rollback state SHA-256
`f8c1d7735b0a958386f3afd3519ca6196aea4a32842893d52bd5d4549543dfa4`
before and after the injected failure. The incompatible upgrade has the same
before/after digest and performs no rollback. Authorized uninstall reports
`skill_only`, preserves canonical evidence SHA-256
`840af4342930e3badaf6cd1965e27c359619f18eb8155aebcba9e78c1c290ee6`,
and removes only `core`.

Independent specification and quality reviews are both **APPROVED** after the
recorded repairs. This remains local release-gate evidence rather than a merge
or publication claim.

Current proof labels:

- Python 3.12-3.14 complete runtime matrix: **NOT_PROVEN**;
- locked-wheel reproduction: **NOT_PROVEN**;
- SBOM execution in the current Python 3.13 environment: **PROVEN**;
- SBOM equivalence across Python 3.12-3.14: **NOT_PROVEN**;
- OS-level network containment: **NOT_PROVEN**;
- availability in `origin/main`: **NOT_PROVEN**;
- parity with real installed Codex/Claude copies: **NOT_PROVEN**;
- exact parity with marked synthetic Codex/Claude fixtures: **PROVEN**.

No Phase 1 runner, persistence, public CLI, daemon, portal, MCP, provider,
external-provider, scheduler, or hosted-platform work is evidenced or authorized by
this ledger.

## Four-skill Task 1 — preimplementation boundary evidence (2026-07-17)

Before any potentially writing test command, Task 1 captured the 12 modified
tracked files and 92 untracked files reported by `git status --short`. Exact
ownership and hunk classifications are in
`docs/phase0/preexisting-dirty-state.md`. Recovery evidence is protected under
`docs/phase0/evidence/preimplementation-snapshot/`:

| Artifact | SHA-256 |
| --- | --- |
| `tracked-dirty.patch` | `b9da20a8836748844023b6b9655d5d2a8bced132a82dc88f7c0c3afb53c7494a` |
| `untracked-files.tar.gz` (92 files) | `63299f65ee7d61d092f4554ed0e72c1c54920844edc3f232cae08c025d8f613b` |
| `untracked-files.sha256` (92 rows) | `f81e99c9b3d2f557e3c4ec76b52336120c2860b3ad2f4c17014f4195de48ee78` |

The archive was extracted into a fresh `/tmp` directory and every SHA-256 and
byte count was verified before tests. The current tracked dirty diff also
matched the captured patch digest. No reset or checkout was used.

All test invocations used `PYTHONDONTWRITEBYTECODE=1`; output and any suites
that otherwise write beside themselves were copied to temporary roots under
`/tmp`. No transient suite file remained in the repository.

| Baseline command | Result | Captured stdout SHA-256 |
| --- | ---: | --- |
| `python3 plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py` | 139 passed, 0 failed | `4445589e2480328ca556c65dbd4217d945b932b70a7bea56060553a7a7904921` |
| `python3 plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_render_report.py` | 174 passed, 0 failed | `023422c5825465d1f3ab4a0198cc181758c3acc51cd99a94ecdfcaa3967031b1` |
| Temporary-copy invocation of `test_to_sarif.py` with its local dependencies | 22 passed, 0 failed | `2ffd4335df9953b2080901d4b26a45ad243e3c3408ab6f7b30bf8e7041be6a6d` |
| Temporary-copy invocation of `test_make_bundle.py` with its local dependencies | 17 passed, 0 failed | `9615853a5a3b9e864ce60afdedb3200be38d25cf6a3864c868e83c32f9b66e1d` |

Baseline total: **352 passed, 0 failed**, exceeding the required
`120 + 174 + 22 + 17` floor.

TDD boundary cycle:

| Stage | Command | Result | Meaning |
| --- | --- | ---: | --- |
| RED | `python3 -m unittest -v tests.skill_product.test_four_skill_boundary` | 1 passed, 3 failed; exit 1; output SHA-256 `c28b6081708042694f04c2ddbb445b064be288055a5679f7ad11934fb06e52a3` | Exactly four skill names already pass. Expected failures are only the existing `src/shipworthy`, `pyproject.toml`, and six `shipworthy-compatibility.json` package-era files. Intentionally left RED. |
| Support RED | `python3 -m unittest -v tests.skill_product.test_migration_map_consistency` | 1 failed, 4 skipped; exit 1 | Closed-world parser support was not yet implemented. |
| Support GREEN | same command | 5 passed; exit 0 | IDs and paths are unique; every exact deletion row maps identically; the deletion set is closed; mandatory behaviors are not deferred. |

The migration map contains 160 exact-path rows. The deletion manifest contains
88 exact paths and no wildcard. No production migration or deletion occurred in
Task 1, so the four-skill boundary remains intentionally RED for Tasks 2-7.

Specification-review repair stayed within Task 1 evidence. Focused RED was
**3 failed, 5 passed**: installed legacy tests/sample were absent from the
deletion manifest, installed-inventory and dirty-ownership parser policies were
missing, and the map still proposed four new installed helper scripts. Focused
GREEN was **8 passed** after adding the five exact deletion rows, limiting
installed scripts to the three existing exporters, routing browser/Playwright/
legacy/parity behavior to references or repository-only tests, joining dirty
ownership to the map, and recording all 19 tracked diff hunks individually.

Quality-review repair also stayed within Task 1 evidence. Focused RED was
**4 failed, 8 passed** for missing independent baseline construction, explicit
installed-tree inventory auditing, final changed/deleted reconciliation, and
duplicate/invalid ownership rejection. Focused GREEN was **12 passed**. The map
now validates safe normalized repository paths, stable derived IDs, exact
lowercase SHA-256 values, and baseline bytes against base commit
`27e8425baa0cda1f64985eb361dfd90ef0752b6b` plus the protected untracked
inventory. `docs/phase0/approved-installed-inventory.txt` explicitly lists 67
approved final skill-tree files; nine exact current artifacts remain a bounded
pending-removal set, and new undeclared files or symlinks fail the audit. Task 7
must recheck each digest immediately before deletion and reconcile every final
changed/deleted path.

Final quality cycle: **10 passed, 1 failed, 2 errors** at RED, then **13 passed**
at GREEN. It adds declared-new destination reconciliation, explicit transitional
and strict-final installed inventory modes, immutable snapshot checksum/archive
verification, full payload member size/hash comparison, and inventory/archive
tamper rejection.

## Four-skill Task 2 — schema relocation and agent contract evidence (2026-07-17)

Task 2 copied the three v1 schemas byte-for-byte into the orchestrator reference
closure, added repository-only subset-oracle coverage, and documented structured
ledger and evidence-import procedures. Root schemas remained in place.

| Stage | Command | Result | Meaning |
| --- | --- | ---: | --- |
| Supplemental RED | `uv run pytest -q tests/skill_product/test_ledger_contract.py` | 16 failed; exit 1 | Early runner feedback confirmed that the relocated schemas, references, routing, and oracle were absent. This is supplemental because the final repository-only suite uses standard-library `unittest`. |
| RED | `python3 -m unittest -v tests.skill_product.test_ledger_contract` | 11 run; 1 failure, 3 errors; exit 1 | The partial implementation did not yet recognize the schema's `x-shipworthy-runtime-constraints` annotation, and the missing-artifact fixture still needed truthful structural-versus-semantic classification. |
| GREEN | `python3 -m unittest -v tests.skill_product.test_ledger_contract` | 12 run; OK; exit 0 | Exact-copy hashes, conditional routing, bounded local references, fail-closed unsupported keywords, direct golden fixtures, hostile fixtures, v1 policy, semantic diff, and pre/post-transform classifications passed. |
| Review repair RED | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.skill_product.test_ledger_contract.LedgerContractTest.test_contract_references_keep_compatibility_policy_out` | 1 run; 1 failure; exit 1 | Extending the policy scan to `SKILL.md` detected conditional optional/unavailable-core framing. |
| Review repair GREEN | same command | 1 run; OK; exit 0 | The orchestrator now states unconditional operation through the four public skills and their skill-owned resources. |

The schema version remains v1 (`1.0`). Source and destination SHA-256 values are
`bad61277f885bb7ba1437ab85e07edbc5a4454448e82aa664dde7005344c8024`
for browser evidence,
`73b92405402623ae7fc4ace475467df6cbb1b8f12b142ee7411405a4c8325115`
for readiness ledgers, and
`82ba535fa07161b943f66b5f25a3ab8eccfb4ed78fe9b6412e074356aea5d0e1`
for report inputs. Field-by-field semantic diff is empty for all three copies.

## Four-skill Tasks 3–7 — final migration evidence (2026-07-17)

This section supersedes the earlier optional-core/package evidence as the current
product boundary. Historical receipts above remain provenance for the migration;
they do not describe an installed component. The final product is exactly four
self-contained skills, with three optional Python standard-library output
scripts inside `ship-readiness-orchestrator`. Package source, build metadata,
compatibility sidecars, and installed lifecycle helpers are absent.

Focused TDD repaired the two independent-review result sets without adding more
review loops. The specification review identified transactional installer,
runtime fallback, parity breadth/cache, explicit atomic/bounded script I/O, and
migration-ledger reconciliation gaps. The quality review identified canonical v1
projection/gate loss, nondeterministic bundle timestamps, weak legacy identity
and dual-render oracles, and overconfident Codex lifecycle wording. Each finding
now has direct repository coverage. A final installer RED additionally proved
that an empty-home failure left newly created host directories; GREEN removes
those directories and restores the exact empty prior state.

Final dual-render comparison preserves finding identity
`FND-LEGACY-06FC62A3337F`, action `Fix`, proof `Confirmed`, the confirmed-blocker
failed gate, and all counts. Legacy HTML and SARIF are pinned respectively to
SHA-256 `85ebab860f572287f0b2b9983192be6eea152274fc856a7b4f25601cc68babc5`
and `89a33b882ccec99a0a5b917901079c938a5d70189a32916f5c358104010d4872`.
The three differences are explained: v1 SARIF adds stable record/gate metadata,
the canonical source bytes differ by format inside the bundle, and v1 records
explicit import lineage. Unexplained dual-render evidence debt is zero.

The repository skill tree contains 69 files with aggregate path/content receipt
`c37594e232919282015271d4b367ebf9d110860ac781ec884061384ba5e5995f`.
Temporary `install.sh --target both` fixtures produced the same 69-file receipt
for both Codex-style `.agents/skills` and Claude-style `.claude/skills` copies;
both comparisons were exact. No real installed-copy directory was read or
written.

An injected second-host upgrade failure exited 97. The deterministic prior-tree
receipt was
`2d4d7f7bfb008bcdf401ae6ffb97e85a0e08dba912e16afa0c553a04415a0c61`
over 10 files both before and after rollback. Canonical evidence remained SHA-256
`a16e9bfc9bc0d49d850d838735e47df9372877ab10508a608ec136a358afd006`.
Additional fixtures cover failed backup moves, partial upgrade failure, an
incomplete source, both-host restoration, and removal of newly created empty host
directories. Automated destructive uninstall is intentionally absent; manual
removal requires direct authorization and names only the four skill directories.

The canonical confirmed-blocker v1 fixture produced these final artifacts:

- HTML SHA-256 `69d176b698325ac2c7efc77e9b6c83133b8ee795c3f631e710fba6c13b75e5f8`;
- SARIF SHA-256 `be60fc3d03b142bce8bdf8c938b5f0eaf656aa343d229914f14d64e613dae642`,
  with one error result and blocking ID `FND-CHECKOUT-001`;
- evidence-bundle SHA-256
  `b6744b6993fdbe291e50324be61a763efb8dcc0341b3c0556d970f2250efc956`,
  containing exactly `README.txt`, `ledger.json`, `manifest.json`,
  `readiness-report.html`, and `readiness.sarif`.

Current proof ceiling:

- four-skill/no-package boundary, local schemas, mandatory HTML, canonical v1
  HTML/SARIF/bundle behavior, legacy oracles, synthetic installed parity, and
  temporary transactional rollback: **PROVEN**;
- immediate pre-deletion revalidation of every historical manifest digest:
  **NOT_PROVEN** (the protected baseline snapshot and final absence/destination
  reconciliation are proven, but this timing-specific claim cannot be recreated);
- Python 3.11 isolated execution on this macOS host: **PROVEN**;
- Python 3.12–3.14 runtime matrix: **NOT_PROVEN**;
- native Codex/Claude install, reload, upgrade, and uninstall behavior:
  **NOT_PROVEN**;
- real installed-copy parity and independent live-agent usability:
  **NOT_PROVEN**;
- locked-wheel reproduction and SBOM execution: **NOT_APPLICABLE — package
  removed**;
- OS-level network containment: **NOT_PROVEN**;
- availability in `origin/main`: **NOT_PROVEN**.

Phase 1 has not started. No SQLite/API/browser runner, persistence, daemon,
portal, MCP, public CLI product, provider integration, scheduler, or hosted
platform was implemented. Browser execution remains host-native by default;
Playwright remains an optional target-owned source of deterministic evidence.

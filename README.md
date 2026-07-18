<div align="center">

<img src="assets/hero.svg" alt="Shipworthy — autonomous, evidence-graded product-readiness audits for apps and AI agents. Walks your whole product, proves it's worthy to ship, never overclaims." width="100%">

### Autonomous, evidence-graded product-readiness audits — for apps &amp; AI agents.

It walks your whole product like your most paranoid senior engineer — **every screen, every path, and the backend underneath** — then proves whether you're ready to ship.

[![GitHub stars](https://img.shields.io/github/stars/NeuraCerebra-AI/shipworthy?style=social)](https://github.com/NeuraCerebra-AI/shipworthy)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Validated](https://img.shields.io/github/actions/workflow/status/NeuraCerebra-AI/shipworthy/validate.yml?label=validated&style=flat-square)](https://github.com/NeuraCerebra-AI/shipworthy/actions)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin%20%2B%204%20skills-8A2BE2?style=flat-square)](https://code.claude.com/docs/en/skills)
[![Version](https://img.shields.io/badge/version-0.1.0-blue?style=flat-square)](https://github.com/NeuraCerebra-AI/shipworthy/releases)

**✓ Read-only by default  ✓ Self-contained markdown  ✓ No telemetry  ✓ No credential access  ✓ No auto-update**

</div>

---

## 😱 What silently breaks without this

Most "it works on my machine" ships die on the things a quick look never catches:

- The path that **technically completes** but is buried six clicks deep, repeats a decision, or dead-ends on reload.
- The backend call that fails while the UI stays **cheerfully green** — nobody notices until a customer does.
- The thing a user will **obviously** try — export, undo, invite a teammate, recover from a failed upload — that has **no path at all**.
- The screen that *looks* finished, retains no attention, and quietly leaks trust.
- And the meta-failure: an audit that declares **"ready"** after sampling three happy paths and calling it a day.

Shipworthy finds all of the above **and refuses the last one.** It treats "try every path" as a coverage ambition with honest exclusions — not a claim of omniscience — and keeps a live evidence ledger so every readiness statement traces back to proof.

<div align="center"><img src="assets/flow.svg" alt="How it works: map the path universe, walk every safe path across UI and backend, run an independent verifier, report coverage and evidence debt, then issue a proven ship-or-don't verdict" width="100%"></div>

## ⚡ Install in 30 seconds

Use the host's plugin manager so installation, updates, and removal stay owned by
the app. The plugin bundles all four self-contained skills.

In **Claude Code**:

```bash
/plugin marketplace add NeuraCerebra-AI/Shipworthy
/plugin install shipworthy@shipworthy
/reload-plugins
```

In **Codex**, add this repository as a plugin source and install `shipworthy`
through the plugin UI. Restart Codex if the four skills are not visible
immediately. Exact native Codex install/reload/upgrade/uninstall commands have
not been exercised in this migration and remain **NOT_PROVEN**; the advanced
manual fallback below is the only locally rehearsed install path.

Then ask:

```text
/goal are we shipworthy?
```

⛴️ In Codex, `/goal` helps Shipworthy keep going across a long audit. It will
ask whether to authorize persistent goal mode and parallel subagents; answer `yes`
for the best results. Claude Code does not have the same Codex `/goal` barrier,
but Shipworthy still uses a goal-equivalent resumable ledger when native goal
mode is unavailable.

That phrase is the flagship trigger: Shipworthy runs the full readiness
orchestrator unless you explicitly ask for a rapid, narrow, changed-only, or
static-only pass. It maps the path universe, tries every safe discoverable user
path, hunts for missing and overcomplicated paths, asks for multi-agent
authorization when the platform requires it, uses agents where authorized and
safe, runs verified waves, and generates a self-contained HTML report from the
final ledger.

Full Shipworthy ends by frontier closure, not vibes, a fixed wave count, or a
timer. It keeps a path frontier open until every material path is covered,
sampled with justification, blocked, avoided, missing, out of scope, or evidence
debt — and until repeated discovery passes stop finding new material paths.

For the flagship run, "tries every safe discoverable user path" means using the
actual frontend when one is available: browser, in-app browser, Chrome,
Playwright, Computer Use, or the app UI itself. Repo/source, CLI, HTTP, tests,
logs, provider checks, database probes, and docs are supporting evidence, not a
substitute for walking the product like a user.

<details>
<summary><b>Advanced manual fallback</b></summary>

```bash
git clone https://github.com/NeuraCerebra-AI/Shipworthy.git
cd Shipworthy
./install.sh --target codex   # installs into ~/.agents/skills
./install.sh --target claude  # installs into ~/.claude/skills
```
Use `--target both` only when you intentionally maintain both manual installations.
Existing copies receive timestamped backups. Each skill also works independently.
</details>

## 🎬 What a run looks like

<div align="center"><img src="assets/sample-report.svg" alt="Illustrative readiness report: NOT READY with Clear Before Ship, Fix Next, Not Proven / Not Tested, and Passed / Keep sections, a coverage map over 34 paths, and an orchestration checkpoint whose independent verifier is APPROVED" width="100%"></div>

<sub>*Illustrative — the report format is real; the contents are a sample, not a live run. A recorded asciinema/GIF walkthrough → `docs/demo.gif`; PRs welcome.*</sub>

> Every operational Shipworthy run renders a self-contained **HTML report** by default (verdict stamp, coverage bar, action-first findings, checkpoint — inline CSS, no JS, no network) via `scripts/render_report.py`. If a run is downgraded, the report still exists and shows why. See [`visual-html-report.md`](plugins/shipworthy/skills/ship-readiness-orchestrator/references/visual-html-report.md).

The report is meant to tell you what to do next, not bury you in audit prose:
**Clear Before Ship** blocks readiness, **Fix Next** is real but non-blocking,
**Not Proven / Not Tested** is not a pass, and **Passed / Keep** worked under
the tested conditions. Each card says whether to Fix, Prove, Decide, Skip, or
Keep, plus how strong the proof is.

<details><summary><b>See the same report as raw text</b></summary>

```text
── READINESS: NOT READY ────────────────────────────────────────────────────

[Clear Before Ship][Fix][Confirmed] Checkout / guest / mobile: payment fails silently
  Evidence: POST /api/pay → 500 (network trace); UI advances to "Thank you"
  User consequence: customer believes they paid; support ticket + chargeback risk
  Fix: gate the success screen on a 2xx + persisted order id
  Verify: force a 500, confirm the UI shows a recoverable error and writes no order

[Clear Before Ship][Fix][Confirmed] No path exists: "cancel an order after purchase"
  Evidence: full surface map — no route, button, or setting reaches cancellation
  Fix: add a cancel affordance on the order-detail screen (smallest viable path)

[Fix Next][Fix][Partial] Coupon field silently ignores invalid codes
  Evidence: 3 invalid codes → no message, no error state, field clears
  Verify: bad code stays visible and gets a clear inline message

[Not Proven / Not Tested][Prove][Not tested] Production order email
  Evidence: avoided to prevent sending real email; logged as evidence debt
  Prove: add a sandbox email sink and rerun the path

[Passed / Keep][Keep][Confirmed] Happy-path guest checkout reaches order detail
  Evidence: cart → address → payment sandbox → confirmation → order detail

── COVERAGE (34 discovered paths) ───────────────────────────────────────────
  Tried + evidenced 21 · Spot-checked 6 · Blocked 3 (paid)
  Skipped for safety 2 (prod email) · Missing 1 · Proof missing 1 (load)

── ORCHESTRATION CHECKPOINT ─────────────────────────────────────────────────
  lanes: ship-deep-review, ship-product-workflows, ship-workflow-clarity
  goal_mode_status: explicitly authorized
  authorization: yes
  mode: 5 lane agents · verifier: Opus, APPROVED
  frontier: 34 total · 0 unattempted · exhaustion_status complete
  omitted: load test (no safe env) → logged as evidence debt, NOT as "passed"
```
</details>

Notice what it *doesn't* do: it never calls the app "ready," never claims the untested path passed, and never silently changes your code. It hands you the smallest fix and the exact way to verify it.

At the end of a run, Shipworthy should ask whether you want to start a persistent fix goal
for the **Clear Before Ship** items using authorized subagents where helpful. Reply `yes` when you want it to
apply the fixes safely, verify each one, and regenerate the Shipworthy HTML report.

## 🧩 The four skills

| Skill | Role | Use it alone when… |
|---|---|---|
| **ship-readiness-orchestrator** | The conductor. Owns the one evidence ledger, the coverage matrix, and the readiness verdict; dispatches and reconciles the three lanes without letting them overclaim. | You want the full "is this ready to ship / be beloved / be viral" pass. |
| **ship-deep-review** | The evidence engine. Multi-wave agent dispatch with a hard rule: no wave summary until an **independent verifier** has checked the raw outputs against the claim ledger. | You want a hostile, multi-wave review or research validation. |
| **ship-product-workflows** | The path walker. Safely tries or traces every meaningful user path — UI, state, persistence, forms, nav, permissions, and backend symptoms that surface in the UI. | You want to know where a specific app or feature actually breaks. |
| **ship-workflow-clarity** | The human lens. Judges whether a person can tell where they are, what to do next, what will and won't happen, and how to recover — and warns when a "simpler" fix strips proof, governance, or recovery. | You want a clarity read on a screen, flow, or dashboard. |

## 🗺️ How it fits together

<div align="center"><img src="assets/architecture.svg" alt="Architecture: the ship-readiness-orchestrator owns the one evidence ledger, coverage matrix, verdict, and no-overclaim gate, and dispatches three lanes — ship-deep-review (waves and verifier gates), ship-product-workflows (walks every path across UI and backend), and ship-workflow-clarity (the human lens with harmful-simplify warnings); product-workflows feeds a clarity packet to workflow-clarity" width="100%"></div>

One truth layer, proven. The lanes feed evidence *packets* into the orchestrator's single ledger — they never publish competing conclusions. Full control stack in **[ARCHITECTURE.md](ARCHITECTURE.md)**.

## ⚖️ How it's different

| | **Shipworthy** | Just running an agent yourself | Code scanners (SonarQube, etc.) |
|---|:---:|:---:|:---:|
| Walks real **user paths** (UI) | ✅ | 🟡 ad hoc | ❌ |
| Checks **backend symptoms tied to UI** | ✅ | 🟡 | 🟡 static only |
| **Coverage map** with honest exclusions | ✅ | ❌ | ❌ |
| **Independent verifier** before it says "ready" | ✅ | ❌ | ❌ |
| Refuses to **overclaim** readiness | ✅ | ❌ | ❌ |
| **Read-only**, hands you the fix + verify step | ✅ | 🟡 | 🟡 |

Shipworthy isn't a "ship faster" boilerplate and it isn't a linter. It's the thing that tells you — with receipts — whether you *should* ship.

## 🔒 Safe by design

Skills are **self-contained folders** — markdown instructions and local resources,
plus three optional standard-library output scripts that never run during
installation. There is no telemetry, credential access, network call, or
auto-update of their own. When auditing, Shipworthy is **read-only by default**
and uses only the tools you already have (browser, agents) inside an explicit
safe-test boundary; it stops at mutating, paid, destructive, publishing, or
production actions unless you authorize the exact action in a disposable
environment. It reports the smallest useful fix and an exact verification step
— it does not apply fixes unless you ask after the review.

## 🙋 FAQ

**Is this a linter or a security scanner?** No. Those read code. Shipworthy walks the *product* — the paths a user takes and the backend behind them — and issues an evidence-backed readiness verdict.

**Does it need my source code?** It works from whatever you give it: a running app, a repo, a diff, screenshots, or docs. Runtime evidence yields the strongest confidence; static-only inputs stay honestly bounded.

**Will it change my code?** No — read-only by default. It gives you the fix and the verification step; you decide.

**Claude Code only?** It's built on the open `SKILL.md` standard, so it also runs in Codex and other SKILL.md-compatible agents. `./install.sh` covers the manual path.

**Why "Shipworthy"?** Because the tool tells you whether your product is *worthy* of shipping — an earned, evidence-backed verdict, not a naked score. The full naming story (and the eight names that were already taken) is in **[docs/naming.md](docs/naming.md)**.

## 🤝 Contributing

PRs welcome — we aim to respond within 48 hours. Great first contributions: new archetype overlays, better path-discovery heuristics, real worked examples, and a recorded demo. Start with issues labeled `good first issue`, and read **[CONTRIBUTING.md](CONTRIBUTING.md)** (the one rule: never add a second source of truth, and never let a lane declare "ready").

## ⭐ Star this if it saved you a bad launch

If Shipworthy caught something before your users did, a star helps other teams find it — and it's the only metric this repo cares about.

[View the star history chart](https://star-history.com/#NeuraCerebra-AI/shipworthy&Date)

## 📚 Docs

- **[Architecture](ARCHITECTURE.md)** — the control stack: who owns evidence, wave barriers, verifier gates.
- **[Naming](docs/naming.md)** — how the names were chosen (and the 8 that were taken) + the GitHub SEO kit.
- **[Launch playbook](docs/launch.md)** — where to list it, how to launch it, the exact About + Topics.

## 📄 License

MIT — see **[LICENSE](LICENSE)**.

<div align="center"><sub>Shipworthy · walk the whole product · prove it's worthy to ship · don't pretend</sub></div>

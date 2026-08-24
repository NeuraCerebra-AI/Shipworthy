<div align="center">

<img src=".github/assets/hero.svg" alt="Shipworthy — free, open-source AI testing agent for automated frontend, end-to-end (E2E), and backend-symptom testing of web apps and AI agents. Walks every safe user path, proves it's ready to ship, never overclaims." width="100%">

### Automated frontend &amp; end-to-end (E2E) testing + backend-symptom analysis — an AI agent that proves your app is ready to ship.

It walks your whole product like your most paranoid senior engineer — every safe, discoverable screen and path, plus the backend underneath — then proves whether you're ready to ship.

Point it at your app, ask **"Are we shipworthy?"**, and get a proof-backed ship-or-don't verdict.

[![GitHub stars](https://img.shields.io/github/stars/NeuraCerebra-AI/shipworthy?style=social)](https://github.com/NeuraCerebra-AI/shipworthy)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-4-8A2BE2?style=flat-square)](#-the-four-skills)
[![Version](https://img.shields.io/badge/version-0.1.0-blue?style=flat-square)](https://github.com/NeuraCerebra-AI/shipworthy/releases)

**Read-only · self-contained markdown · no telemetry · no credential access · no auto-update**

</div>

---

> **Shipworthy** is a free, open-source **AI testing agent** that runs **automated frontend and end-to-end (E2E) tests** on your web app — and analyzes the **backend symptoms** behind each path. It walks every safe user path like a real user (browser, Playwright, or Computer Use), catches failures the UI hides (a 500 behind a "success" screen, data that never saved), installs as a **Claude Code or Codex skill**, runs **read-only**, and returns a proof-backed *ship-or-don't* verdict: **ready, conditionally ready, not ready, or cannot determine**. It works on normal apps and on AI-built ("vibe-coded") apps and AI agents — and it never overclaims.

## 😱 What silently breaks without this

Most "it works on my machine" ships die on the things a quick look never catches:

- **Buried paths** — the flow that technically completes but sits six clicks deep, repeats a decision, or dead-ends on reload.
- **Silent backend failures** — the API call that fails while the UI stays cheerfully green (a 500 behind a "Thank you" screen); nobody notices until a customer does.
- **Missing paths** — the thing a user will obviously try (export, undo, invite a teammate, recover from a failed upload) that has no path at all.
- **Trust leaks** — the screen that *looks* finished, holds no attention, and quietly leaks trust.
- **The "ready" lie** — an audit that declares "ready" after sampling three happy paths and calling it a day.
- **Lost evidence** — an audit that finds a real path, then drops or mislabels it while merging agent output, so the report looks more complete than the evidence.

Shipworthy catches all of these — and refuses the last two itself. "Try every path" is an honest goal with stated exclusions, not a claim of omniscience: every readiness statement traces back to proof, and anything it couldn't test is labeled, not hidden.

<div align="center"><img src=".github/assets/flow.svg" alt="How Shipworthy works — automated end-to-end testing: map the path universe, walk every safe path across UI and backend, run an independent verifier, report coverage and evidence debt, then issue a proven ship-or-don't verdict" width="100%"></div>

## 🎬 What a run looks like

<div align="center"><img src=".github/assets/sample-report.svg" alt="Illustrative readiness report: NOT READY with Clear Before Ship, Fix Next, Not Proven / Not Tested, and Passed / Keep sections, a coverage map over 34 paths, and an orchestration checkpoint whose independent verifier is APPROVED" width="100%"></div>

<sub>*Illustrative — the report format is real; the contents are a sample, not a live run.*</sub>

Every run ends in one self-contained **HTML report** that tells you what to do next instead of burying you in audit prose. Findings are grouped by action: **Clear Before Ship** blocks the release, **Fix Next** is real but non-blocking, **Not Proven / Not Tested** is never a pass, and **Passed / Keep** worked under the tested conditions. Each card says whether to Fix, Prove, Decide, Skip, or Keep — and how strong the proof is.

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
  frontier: 34 total · 0 unattempted · finality exhausted · qualification incomplete
  omitted: load test (no safe env) → logged as evidence debt, NOT as "passed"
```
</details>

Notice what it *doesn't* do: it never calls the app "ready," never claims an untested path passed, and never silently changes your code. It hands you the smallest fix and the exact way to verify it — and, if you reply `yes`, it will fix the **Clear Before Ship** items and re-run the report.

## ⚡ Install in 30 seconds

Open Codex or Claude Code and ask:

> Install the four top-level skills from
> [NeuraCerebra-AI/Shipworthy](https://github.com/NeuraCerebra-AI/Shipworthy)
> into this environment's skills directory. Install each folder as a separate
> skill—not the repository as one nested skill.

Start a new session so the host discovers them. Then ask:

```text
Are we shipworthy?
```

### Install the bundled plugin

For a single namespaced install, use the packaged plugin and its marketplace:

**Codex**

```text
codex plugin marketplace add NeuraCerebra-AI/Shipworthy --sparse .agents/plugins
codex plugin add shipworthy@shipworthy
```

**Claude Code**

```text
claude plugin marketplace add NeuraCerebra-AI/Shipworthy
claude plugin install shipworthy@shipworthy
```

Claude Code exposes the bundled skills under the `shipworthy:` namespace. The
standalone folders above remain available for hosts that install individual
`SKILL.md` directories directly. The plugin package is generated from those
canonical folders; maintainers should run
`python3 tools/sync_plugin_package.py --write` after skill changes.

That's the trigger for a full run — automated **end-to-end testing** across your whole frontend. It walks every safe path it can find (and flags the ones users expect but that don't exist), checks the backend under each one, has an **independent verifier** sign off, and writes the HTML report. A full run is a **minimum of three independently-verified waves**: it keeps going until two separate sweeps turn up nothing new — not a fixed number of rounds or a timer — and it labels every path with one of **seven coverage statuses** (from `covered` to `evidence_debt`). Want something lighter? Ask for a **rapid**, **narrow**, **changed-only**, or **static** pass. The full mechanics live in **[ARCHITECTURE.md](ARCHITECTURE.md)**.

## 🧩 The four skills

| Skill | Role | Use it alone when… |
|---|---|---|
| **ship-readiness-orchestrator** | The conductor. Owns the one evidence ledger, the coverage matrix, and the readiness verdict; dispatches and reconciles the three lanes without letting them overclaim. | You want the full "is this ready to ship / be beloved / be viral" pass. |
| **ship-deep-review** | The evidence engine. Multi-wave agent dispatch with a hard rule: no wave summary until an **independent verifier** has checked the raw outputs against the claim ledger. | You explicitly invoke `ship-deep-review` by name, or the active readiness orchestrator loads it as its required controller. Generic review or audit language does not activate it. |
| **ship-product-workflows** | The path walker. Safely tries or traces every meaningful user path — UI, state, persistence, forms, nav, permissions, and backend symptoms that surface in the UI. | You want to know where a specific app or feature actually breaks. |
| **ship-workflow-clarity** | The human lens. Judges whether a person can tell where they are, what to do next, what will and won't happen, and how to recover — and warns when a "simpler" fix strips proof, governance, or recovery. | You want a clarity read on a screen, flow, or dashboard. |

## 🗺️ How it fits together

<div align="center"><img src=".github/assets/architecture.svg" alt="Architecture: the ship-readiness-orchestrator owns the one evidence ledger, coverage matrix, verdict, and no-overclaim gate, and dispatches three lanes — ship-deep-review (waves and verifier gates), ship-product-workflows (walks every path across UI and backend), and ship-workflow-clarity (the human lens with harmful-simplify warnings); product-workflows feeds a clarity packet to workflow-clarity" width="100%"></div>

**One** orchestrator, **three** specialist lanes, **one** evidence ledger. The lanes feed evidence *packets* into that single ledger and never publish competing conclusions — so a run yields one proof-backed verdict, not three. Full control stack in **[ARCHITECTURE.md](ARCHITECTURE.md)**.

## ⚖️ How it's different

| | **Shipworthy** | Just running an agent yourself | Code scanners (SonarQube, etc.) |
|---|:---:|:---:|:---:|
| Walks real **user paths** (UI) | ✅ | 🟡 ad hoc | ❌ |
| Checks **backend symptoms tied to UI** | ✅ | 🟡 | 🟡 static only |
| **Coverage map** with honest exclusions | ✅ | ❌ | ❌ |
| Proves raw observations survived into the final ledger and report | ✅ | ❌ | ❌ |
| **Independent verifier** before it says "ready" | ✅ | ❌ | ❌ |
| Refuses to **overclaim** readiness | ✅ | ❌ | ❌ |
| **Read-only**, hands you the fix + verify step | ✅ | 🟡 | 🟡 |

Shipworthy isn't a linter, a boilerplate, or a paid QA platform that makes you write and maintain a test suite. It's a free, read-only AI agent that walks your app end-to-end and tells you — with receipts — whether you *should* ship.

## 📊 Why this matters

AI writes more code than ever — and ships more defects with it. Independent testing across 100+ current models found **45% of AI-generated code introduced an OWASP Top 10 vulnerability** ([Veracode, 2025](https://www.veracode.com/blog/genai-code-security-report/)), and a controlled Stanford study found developers using an AI assistant wrote *less* secure code while feeling **more** confident it was safe ([Perry et al., ACM CCS 2023](https://arxiv.org/abs/2211.03622)). The consequences already ship: one AI-built app exposed roughly **18,700 records** through what the researcher who found it called "a classic logic inversion that a human security reviewer would catch in seconds" ([The Register, 2026](https://www.theregister.com/2026/02/27/lovable_app_vulnerabilities/)). And you can't just ask the AI whether it's ready — across leading generative engines, only **51.5% of AI-generated sentences were fully supported by their own citations** ([Liu et al., Stanford, 2023](https://aclanthology.org/2023.findings-emnlp.467/)). That gap is the whole point of Shipworthy: it walks your product and **proves** what works, instead of trusting a model's say-so.

## 🔒 Safe by design

Each skill is a self-contained folder — markdown instructions, local resources, and three optional output scripts that never run on install. When auditing, Shipworthy is **read-only by default**: it uses only the tools you already have (browser, agents) inside an explicit safe-test boundary, and it stops at any mutating, paid, destructive, publishing, or production action unless you authorize that exact action against a verified non-production sandbox. It reports the smallest useful fix and the way to verify it; it does not apply fixes unless you ask.

<sub>**Zero** telemetry, credential access, network calls, or auto-update. The report renderer validates every report against the bundled [JSON Schema](https://json-schema.org/) (Draft 2020-12) with Python `jsonschema` and fails closed if it's missing, and can export **SARIF** for GitHub code scanning. Repo CI runs the renderer suite and schema checks on **Python 3.9 and 3.13** (`ship-readiness-orchestrator/requirements-validation.txt`).</sub>

## 🙋 FAQ

**How do I know if my app or AI agent is ready to ship?** Point Shipworthy at it and ask *"Are we shipworthy?"*. It walks every safe user path plus the backend, has an independent verifier check the evidence, and returns one of four proof-backed verdicts — **ready, conditionally ready, not ready, or cannot determine** — with the exact blockers and the way to verify each fix. It never marks an untested path as passing.

**Can it test an app I built with AI (Lovable, Bolt, Replit, Cursor, v0)?** Yes. Shipworthy walks an AI-built ("vibe-coded") app's real user paths and checks the backend behind them, so you get an evidence-backed readiness verdict without having to read the generated code yourself.

**Does it test the backend, or just the UI?** Both — from the user's side. It runs the frontend end-to-end and analyzes the backend *symptoms* that surface in each path: failed API calls, 500s behind "success" screens, data that doesn't persist, auth that leaks across accounts. It is **not** a load test, a penetration test, or a full backend/security audit.

**Is it an alternative to QA Wolf, testRigor, or Cypress?** It's a free, open-source, read-only take on the same problem. Instead of writing and maintaining a test suite, it walks your app end-to-end on demand and reports what's ready and what isn't — runtime evidence is strongest, and it won't invent a passing result.

**Is this a linter or a security scanner?** No. Those read code. Shipworthy walks the *product* — the paths a user takes and the backend behind them — and issues an evidence-backed readiness verdict.

**Does it need my source code?** It works from whatever you give it: a running app, a repo, a diff, screenshots, or docs. Runtime evidence yields the strongest confidence; static-only inputs stay honestly bounded.

**Will it change my code?** No — read-only by default. It gives you the fix and the verification step; you decide.

**Claude Code only?** No. It's built on the open `SKILL.md` standard, so it also runs in Codex and other SKILL.md-compatible agents.

**Why "Shipworthy"?** Because the tool tells you whether your product is *worthy* of shipping — an earned, evidence-backed verdict, not a naked score.

## ⭐ Star this if it saved you a bad launch

If Shipworthy caught something before your users did, a star helps other teams find it — and it's the only metric this repo cares about.

[View the star history chart](https://star-history.com/#NeuraCerebra-AI/shipworthy&Date)

## 📚 Docs

- **[Architecture](ARCHITECTURE.md)** — the control stack: who owns evidence, wave barriers, verifier gates.
- **[Plugin publishing](PLUGIN_PUBLISHING.md)** — package layout, validation, release, and marketplace steps.

## 📄 License

MIT — see **[LICENSE](LICENSE)**.

<div align="center"><sub>Shipworthy · walk the whole product · prove it's worthy to ship · don't pretend</sub></div>

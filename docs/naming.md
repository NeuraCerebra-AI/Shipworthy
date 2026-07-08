# Naming — how "Shipworthy" and the `ship-*` skills were chosen

This suite uses a **two-layer naming model**. The two layers optimize for opposite goals and are kept separate on purpose.

- **Layer A — the suite/repo brand:** one memorable, searchable name that carries the GitHub-stars load → **Shipworthy**.
- **Layer B — the member skill names:** these must keep **auto-triggering** as Claude skills. Triggering depends on `name` + `description`, so member names stay keyword-bearing and every `description:` was preserved verbatim.

## Layer A: the brand

**Inputs.** FUNCTION: autonomous, evidence-graded product/UX/readiness auditing for apps and AI-heavy workflows. AUDIENCE: developers + enterprise engineering/QA leaders. DIFFERENTIATOR: multi-wave agent orchestration + honest coverage/evidence debt — *proves before it proclaims*. TONE: precision + authority, catchy enough to be talkable and searchable.

**Method.** Candidates were scored with the viral-naming rubric `V = (F × E × S) + C` (Fluency × Emotion × Semantic clarity + a Cultural-timing bonus), and — critically — every serious candidate went through an **availability-first** web check *before* scoring. In 2026 the AI-agent/audit namespace is a red ocean, so ownability is the binding constraint, not fluency.

**The finding that shaped everything.** Nearly every strong *evocative* candidate was already taken by an adjacent — often funded — competitor. Verified collisions during selection:

| Candidate | Collided with |
|---|---|
| OpenProof / the whole *Proof / Audit* family | multiple "OpenProof" repos incl. a digital-evidence format; the entire creative-"proofing" SaaS category; theorem provers |
| Preflight | Applitools Preflight + a second AI "Preflight" shipping *release-readiness reports* |
| DeepSweep | DeepSweep.ai — active AI-security auditor (audits AI code + MCP) |
| Verity | Caseware **Verity** (AI audit platform) + VerityLabs (agent orchestration + MCP + SOC 2 + pharma) + 3 more |
| Kestrel | **Kestrel AI (YC F25)** — autonomous multi-agent, MCP, "read-only by default," SOC 2 |
| Docket | DocketAI — agentic platform, SOC 2 |
| Tessera | Tessera Labs — **\$60M a16z Series A**, multi-agent orchestration, "audit with confidence" |
| Holon | `holon-run/holon` — local agent workbench ("ledgers / trust boundaries") + 5 more |
| ShipReady | ship-ready.xyz ("GTM **readiness audit** for dev tools in 60s") + a popular Shopify boilerplate |
| Shipshape | Google's `shipshape` static-analysis platform |

**The insight that unlocked it.** On GitHub, **repo names are namespaced to your org** — `github.com/<org>/<name>` never "collides" for naming. And discovery is driven, in order, by **Topics → the About/description field → README keywords → stars/activity**, *not* by name-match (Cursor and Ollama are opaque brands found through topics + description + being useful). So a keyword-forward, outcome-stating brand is both *available under your org* and *good for search* — the best of both worlds the evocative-word hunt kept missing.

**Why "Shipworthy" wins.** It reads as a legitimate coinage in the *trustworthy / creditworthy / newsworthy* family, and the `-worthy` suffix implies an **earned, holistic verdict** — "is this worthy of shipping?" — which is exactly what the tool produces: an evidence-backed readiness judgment, **not a naked score**. It states the outcome, contains the search term "ship," and is distinctive enough to brand. Runner-up **ShipGrade** had a cleaner handle but a philosophical conflict: the skills deliberately avoid naked letter-grades and decimal scores ("put scores last, omit by default"), so a name promising a "grade" oversells a number the tool won't lead with. Shipworthy has no such conflict.

> **Availability is never asserted — verify before you publish.** `github.com/shipworthy` (the bare org) is taken by an Elixir workflow project ("Journey") — but there is **no competing product named Shipworthy**, and this suite ships under `github.com/NeuraCerebra-AI/shipworthy`, so the org handle is moot. Confirm `shipworthy.com/.dev/.ai` and `shipworthy` on npm/PyPI yourself; the space moves weekly.

## Layer B: the member skills

**Scheme B (clean-tail):** brand root `ship-` + a descriptive tail that keeps each skill's distinctive trigger keyword(s). The redundant leading `audit-` was dropped from two names — safely, because the word "audit" survives verbatim in those skills' preserved descriptions (7× and 3×), so trigger behavior is unchanged.

| Old name | New name | Keyword retention |
|---|---|---|
| `product-readiness-orchestrator` | `ship-readiness-orchestrator` | "readiness" + "orchestrator" in name; "product readiness" verbatim in description |
| `deep-review` | `ship-deep-review` | "deep review" intact |
| `audit-product-workflows` | `ship-product-workflows` | "product workflows" in name; "audit" x7 verbatim in description |
| `audit-workflow-clarity` | `ship-workflow-clarity` | "workflow clarity" in name; "audit" x3 verbatim in description |

**Descriptions were preserved byte-for-byte**, with a single required exception: the cross-reference token inside `ship-product-workflows`' description (`$audit-workflow-clarity` → `$ship-workflow-clarity`). Every trigger keyword around it is unchanged.

**Atomic rename coverage.** All cross-references across markdown, YAML, and JSON were rewired — `name:` frontmatter, H1 titles, `$name` prompts, backtick refs, bare prose refs, `name/SKILL.md` load-gate paths, the `coverage-map.json` `"skill"` value — and machine-specific absolute paths were neutralized to `<skills-dir>/…`. Post-migration grep for every prior name returns zero references. The orchestrator's load gate resolves each sub-skill to a real folder; the graph forms (`orchestrator → {deep-review, product-workflows, workflow-clarity}`; `product-workflows → workflow-clarity`).

## GitHub discoverability (the real levers)

Set these on the repo — they matter far more than the name:

**About / description:**
> Autonomous, evidence-graded product-readiness auditing for apps & AI agents. A Claude Code / Codex skill suite (orchestrator + deep-review, product-workflow, and UX-clarity lanes) that walks every user path, checks UI *and* backend, and proves whether you're ready to ship — read-only, no overclaiming.

**Topics:** `ai-agents` · `agentic-ai` · `autonomous-agents` · `multi-agent` · `product-readiness` · `release-readiness` · `qa` · `quality-assurance` · `product-audit` · `ux-audit` · `workflow-audit` · `ai-audit` · `code-review` · `testing` · `claude` · `claude-code` · `claude-skills` · `anthropic` · `mcp` · `developer-tools`

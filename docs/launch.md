# Launch playbook — how Shipworthy gets found and shared

A great repo nobody links to still dies. In the 2026 Claude ecosystem there is **no single app store** — discovery is decentralized across plugin *marketplaces*, auto-syncing directory sites, and a handful of curated awesome-lists. Here's the concrete plan.

## 0. Pre-launch checklist

- [ ] Verify handles: `github.com/NeuraCerebra-AI/shipworthy`, `shipworthy` on npm/PyPI, `shipworthy.com/.dev/.ai`.
- [ ] Paste the **About** blurb + all 20 **Topics** (below) into repo settings — this drives GitHub + Google discovery far more than the name.
- [ ] Confirm the `validated` badge is green (the `validate` workflow runs on push).
- [ ] Record a real demo → `docs/demo.gif` and drop it under the hero. A visual is the single biggest conversion lever; the placeholder is a stopgap.
- [ ] Tag a release (`v0.1.0`) so the version badge and `sha`-pinned installs work.

## 1. Ship it as a plugin (installable + auto-discoverable)

The repo is already a plugin **marketplace** (`.claude-plugin/marketplace.json`) hosting one plugin that bundles all four skills. Users install with:

```
/plugin marketplace add NeuraCerebra-AI/shipworthy
/plugin install shipworthy@shipworthy
```

This is the official, discoverable route — a plain "copy these folders" repo is neither installable-as-a-unit nor centrally indexed.

## 2. Get auto-indexed (passive, days)

These directories sync public GitHub repos automatically — publishing is usually enough to appear:
`claudemarketplaces.com` · `skillsmp.com` · `awesomeclaude.ai/awesome-claude-skills` · `awesome-skills.com` · `agentskill.club` · `mcpmarket.com/tools/skills`. They surface **trust attributes** (no code exec, no creds, self-contained) — Shipworthy scores well here, so make sure the README trust strip is accurate and prominent.

## 3. Get into the curated lists (active PRs, highest signal)

- **`hesreallyhim/awesome-claude-code`** (~37k stars) — the canonical hand-curated list. One tool per category; quality-gated. Open a PR adding Shipworthy under testing / audit / orchestration.
- **`quemsah/awesome-claude-plugins`** — auto-discovered index (15k+ repos); catches new repos within hours.
- **`affaan-m/everything-claude-code`** — the aggregator firehose.
- Cross-tool lists (works in Codex/Cursor/Gemini too — lead with the open `SKILL.md` standard).
- **Aspiration:** `anthropics/claude-plugins-official` — the official directory. Community frameworks (e.g. `obra/superpowers`, 94k★) have been accepted; earn it with adoption + polish.

## 4. Launch channels (active, launch week)

- **Show HN** — "Show HN: Shipworthy — an AI agent that audits your whole product and proves it's ready to ship." Lead with the pain and the honesty angle (it refuses to overclaim). Post Tue–Thu morning ET.
- **Reddit** — r/ClaudeAI, r/ClaudeCode, and where relevant r/LocalLLaMA / r/SaaS. Value-first: share the "what silently breaks" list and the worked example, not a link dump.
- **X/Twitter** — a thread built around the comparison table + the sample report screenshot; tag the Claude Code ecosystem.
- **Product Hunt** — position as "the readiness gate for AI-built apps." A short demo video is table stakes there.
- **Dev.to / blog** — a "we audited N AI-built apps and here's what broke" post is highly shareable and doubles as SEO.

## 5. The SEO kit (paste verbatim)

**About / description:**
> Autonomous, evidence-graded product-readiness auditing for apps & AI agents. A Claude Code / Codex skill suite (orchestrator + deep-review, product-workflow, and UX-clarity lanes) that walks every user path, checks UI *and* backend, and proves whether you're ready to ship — read-only, no overclaiming.

**Topics (20):** `ai-agents` · `agentic-ai` · `autonomous-agents` · `multi-agent` · `product-readiness` · `release-readiness` · `qa` · `quality-assurance` · `product-audit` · `ux-audit` · `workflow-audit` · `ai-audit` · `code-review` · `testing` · `claude` · `claude-code` · `claude-skills` · `anthropic` · `mcp` · `developer-tools`

## 6. Loops that compound

- Every audit report ends with a shareable artifact — encourage users to post their coverage map / sample report.
- Turn recurring findings into a short "readiness anti-patterns" series (SEO + credibility).
- Respond to PRs within 48h and tag `good first issue` — contributor velocity is itself a discovery signal on the auto-indexed lists.

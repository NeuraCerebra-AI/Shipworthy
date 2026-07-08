# Shipworthy HTML Report Gate Follow-Up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Shipworthy "HTML report every time" requirement mechanically hard to skip, using the TraceFlow shipready miss as a live regression case.

**Architecture:** Treat the current `main` state as partially implemented because commit `ab26950 Require HTML report for all Shipworthy runs` already exists. First audit the current repo and installed skill copies, then patch only proven gaps. Keep the contract in four layers: orchestrator gate, report contract, renderer/tests, and pressure-test/live-regression documentation.

**Tech Stack:** Markdown skill docs, Python renderer/tests under `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts`, local installed skill directories under `/Users/warrencain/.codex/skills` and `/Users/warrencain/.claude/skills`, Git/GitHub validation.

---

## File Map

- Modify if gaps remain: `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md`
- Modify if gaps remain: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/visual-html-report.md`
- Modify if gaps remain: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/final-report-contract.md`
- Modify if gaps remain: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/lane-prompts.md`
- Modify if gaps remain: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/exports-and-ci.md`
- Modify if gaps remain: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/pressure-tests.md`
- Modify if gaps remain: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py`
- Modify if gaps remain: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_render_report.py`
- Modify if gaps remain: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/render_report.py`
- Modify if gaps remain: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/sample-report.json`
- Create: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/live-regressions/traceflow-html-report-miss.md`
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`
- Copy/sync after repo edits: `/Users/warrencain/.codex/skills/ship-readiness-orchestrator`
- Copy/sync after repo edits: `/Users/warrencain/.claude/skills/ship-readiness-orchestrator`

## Agent Orchestration Plan

Use `superpowers:subagent-driven-development` in the execution conversation. Dispatch these read-only audit agents first; each returns a concise packet and does not edit files.

1. **Docs Contract Agent**
   - Scope: `README.md`, `ARCHITECTURE.md`, `SKILL.md`, `references/visual-html-report.md`, `references/final-report-contract.md`, `references/lane-prompts.md`, `references/exports-and-ci.md`.
   - Goal: Confirm the always-on HTML report contract is present, unambiguous, and not contradicted by optional/static/downgrade wording.
   - Output: pass/fail list with exact file anchors and any required patches.

2. **Renderer And Tests Agent**
   - Scope: `scripts/render_report.py`, `scripts/test_render_report.py`, `scripts/test_skill_contract.py`, `scripts/sample-report.json`, `scripts/test_make_bundle.py`.
   - Goal: Confirm downgraded/static/source-CLI reports still render `readiness-report.html`, the report path/status fields exist, and tests would have caught the TraceFlow miss.
   - Output: pass/fail list with exact missing assertions.

3. **Installed Skill Sync Agent**
   - Scope: repo skill folder versus `/Users/warrencain/.codex/skills/ship-readiness-orchestrator` and `/Users/warrencain/.claude/skills/ship-readiness-orchestrator`.
   - Goal: Confirm installed copies match repo after edits; identify backup folders to remove.
   - Output: diff status and sync commands.

4. **Live Regression Agent**
   - Scope: this TraceFlow failure mode only.
   - Goal: Turn the miss into a durable regression reference: downgraded shipready audit produced Markdown and target HTML, but initially omitted distinct Shipworthy `readiness-report.html`.
   - Output: proposed `live-regressions/traceflow-html-report-miss.md` content and pressure-test linkage.

The coordinator reads all four packets, decides the exact patch set, then implements tasks below. If a subagent is unavailable, perform the same audit sequentially and record that limitation in the final answer.

## Task 1: Baseline Audit Current `main`

**Files:**
- Read: `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md`
- Read: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/visual-html-report.md`
- Read: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/final-report-contract.md`
- Read: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/pressure-tests.md`
- Read: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py`
- Read: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_render_report.py`

- [ ] **Step 1: Confirm branch, commit, and cleanliness**

Run:

```bash
git status --short --branch
git log --oneline -5
```

Expected:

```text
## main...origin/main
ab26950 Require HTML report for all Shipworthy runs
```

- [ ] **Step 2: Check for current always-on HTML report language**

Run:

```bash
rg -n "HTML Report Gate|Shipworthy invocation means HTML report, always|readiness-report.html|Every operational Shipworthy" plugins/shipworthy/skills README.md ARCHITECTURE.md
```

Expected:

```text
plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md: HTML Report Gate
plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md: Shipworthy invocation means HTML report, always
plugins/shipworthy/skills/ship-readiness-orchestrator/references/visual-html-report.md: mandatory for Shipworthy
README.md: Every operational Shipworthy run renders a self-contained HTML report
```

- [ ] **Step 3: Search for optional wording that would recreate the miss**

Run:

```bash
rg -n "generate it when requested|HTML report.*optional|readiness-report.html.*optional|full Shipworthy.*only" plugins/shipworthy/skills/ship-readiness-orchestrator README.md ARCHITECTURE.md
```

Expected:

```text
No matches that make the operational Shipworthy HTML report optional.
```

- [ ] **Step 4: Decide whether docs need edits**

If Task 1 finds no gaps, record `NO_DOC_PATCH_NEEDED` in the implementation notes and skip Task 2. If it finds contradictory optional wording, complete Task 2.

## Task 2: Patch Contract Language If The Audit Finds Gaps

**Files:**
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/visual-html-report.md`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/final-report-contract.md`
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`

- [ ] **Step 1: Add or repair the orchestrator HTML Report Gate**

Patch `plugins/shipworthy/skills/ship-readiness-orchestrator/SKILL.md` so it contains this exact operational invariant:

```markdown
## HTML Report Gate

Every operational Shipworthy invocation must produce a self-contained HTML readiness report from the final ledger, regardless of whether the run is full flagship, conditional, static constrained, changed-only, source/CLI-only, or downgraded. Downgrade status changes the report contents and verdict language; it does not remove the report requirement.

Before final response, verify that `readiness-report.html` exists, was rendered from the final ledger/report JSON, and is linked in the final answer. If report generation fails, file writes are impossible, or the user explicitly forbids artifact creation, lead the final answer with **`HTML report: MISSING/BLOCKED`**, explain why, record it as deliverable debt, and do not imply the Shipworthy run is complete.
```

- [ ] **Step 2: Repair visual report reference**

Patch `references/visual-html-report.md` so the opening line is unambiguous:

```markdown
# Visual HTML readiness report (mandatory for Shipworthy)
```

Ensure it also says:

```markdown
Shipworthy invocation means HTML report, always. A downgrade changes the report contents and checkpoint, not the report requirement.
```

- [ ] **Step 3: Repair final answer contract**

Patch `references/final-report-contract.md` so every final answer must include:

```markdown
Every Shipworthy final answer must include: verdict, report HTML path, ledger path, evidence path(s), omitted gates, downgrade reason when applicable, multi-agent authorization status, frontend path-walk status, and report generation status. If `readiness-report.html` is missing, do not imply the Shipworthy run is complete.
```

- [ ] **Step 4: Repair public docs**

Patch `README.md` and `ARCHITECTURE.md` so users see the invariant. Use this wording in `README.md` near the trigger/outputs section:

```markdown
Every operational Shipworthy run renders a self-contained **HTML report** by default. If a run is downgraded, the report still exists and shows why.
```

- [ ] **Step 5: Run focused doc contract tests**

Run:

```bash
python3 plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py
```

Expected:

```text
All checks passed
```

## Task 3: Add The TraceFlow Live Regression Reference

**Files:**
- Create: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/live-regressions/traceflow-html-report-miss.md`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/references/pressure-tests.md`
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py`

- [ ] **Step 1: Create the live-regressions directory**

Run:

```bash
mkdir -p plugins/shipworthy/skills/ship-readiness-orchestrator/references/live-regressions
```

Expected:

```text
Directory exists.
```

- [ ] **Step 2: Write the TraceFlow regression note**

Create `plugins/shipworthy/skills/ship-readiness-orchestrator/references/live-regressions/traceflow-html-report-miss.md` with this content:

```markdown
# Live Regression: TraceFlow Shipready HTML Report Miss

## Trigger

User asked: `/goal are we shipready?`

## What went right

- The agent loaded the Shipworthy stack.
- The agent used the Multi-Agent Authorization Gate and recorded sequential fallback when authorization was not received.
- The agent ran source/CLI evidence commands and a partial static Run Inspector path-walk.
- The agent produced a correct conditional verdict and avoided production/tapeout/signoff overclaims.
- The agent saved a Markdown audit ledger and browser evidence.

## What went wrong

The agent did not generate the distinct Shipworthy `readiness-report.html` before the first final answer. It confused a downgraded/source-CLI/static-audit path plus target-owned HTML artifacts with completion of the Shipworthy report deliverable.

## Root cause

The agent interpreted "not a full flagship run" as weakening the HTML report requirement. That interpretation is invalid. Downgrade status changes report contents and wording; it does not remove the report requirement.

## Required future behavior

Every operational Shipworthy invocation must generate `readiness-report.json` and `readiness-report.html` from the final ledger unless the user explicitly forbids artifact creation or file writes are impossible. The final answer must include the absolute HTML path. If the HTML file is missing, the final answer must lead with `HTML report: MISSING/BLOCKED` and must not imply completion.

## Regression assertion

A source/CLI-only, static constrained, changed-only, or downgraded Shipworthy run still emits a distinct Shipworthy `readiness-report.html` and does not substitute target-owned HTML, Markdown ledgers, screenshots, or chat summaries for that report.
```

- [ ] **Step 3: Link the regression from pressure tests**

Patch `references/pressure-tests.md` to include:

```markdown
Live regression reference: `references/live-regressions/traceflow-html-report-miss.md`
```

Place it under the scenario that checks downgraded/source-only runs still emit an HTML report.

- [ ] **Step 4: Add a contract test for the live regression file**

Patch `scripts/test_skill_contract.py` with:

```python
LIVE_REGRESSION = ORCH / "references" / "live-regressions" / "traceflow-html-report-miss.md"
live = LIVE_REGRESSION.read_text()
ck("H11 TraceFlow live regression exists", "TraceFlow Shipready HTML Report Miss" in live)
ck("H12 live regression forbids substituting target HTML", "does not substitute target-owned HTML" in live)
ck("H13 pressure tests link TraceFlow regression", "traceflow-html-report-miss.md" in pressure)
```

- [ ] **Step 5: Run focused contract test**

Run:

```bash
python3 plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py
```

Expected:

```text
All checks passed
```

## Task 4: Harden Renderer Test Coverage If Needed

**Files:**
- Modify: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_render_report.py`
- Modify if needed: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/render_report.py`
- Modify if needed: `plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/sample-report.json`

- [ ] **Step 1: Inspect current downgraded-report renderer tests**

Run:

```bash
rg -n "not_performed|report_path|downgrade_reason|report generation" plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_render_report.py plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/render_report.py plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/sample-report.json
```

Expected: tests and renderer mention `not_performed`, `report_path`, and report generation status.

- [ ] **Step 2: Add a missing-path regression if not already present**

If there is no test proving a downgraded report renders an HTML file with report path/status, add this test to `test_render_report.py`:

```python
def test_downgraded_run_still_renders_report_path_and_reason():
    html = render({
        "verdict": "CONDITIONAL",
        "checkpoint": {
            "frontend_path_walk_performed": False,
            "frontend_tool": "none",
            "runtime_target": "source/CLI only",
            "path_walk_status": "not_performed",
            "downgrade_reason": "source/CLI-only readiness audit is not a full Shipworthy run",
            "report_generation_status": "generated",
            "report_path": "/tmp/shipworthy/readiness-report.html"
        }
    })
    assert "source/CLI-only readiness audit is not a full Shipworthy run" in html
    assert "/tmp/shipworthy/readiness-report.html" in html
    assert "report generation" in html
```

- [ ] **Step 3: Run renderer tests**

Run:

```bash
python3 plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_render_report.py
```

Expected:

```text
All checks passed
```

## Task 5: Sync Installed Skill Copies

**Files:**
- Source: `plugins/shipworthy/skills/ship-readiness-orchestrator`
- Destination: `/Users/warrencain/.codex/skills/ship-readiness-orchestrator`
- Destination: `/Users/warrencain/.claude/skills/ship-readiness-orchestrator`

- [ ] **Step 1: Sync repo skill to Codex installed skill directory**

Run:

```bash
rsync -a --delete plugins/shipworthy/skills/ship-readiness-orchestrator/ /Users/warrencain/.codex/skills/ship-readiness-orchestrator/
```

Expected: command exits 0.

- [ ] **Step 2: Sync repo skill to Claude installed skill directory**

Run:

```bash
rsync -a --delete plugins/shipworthy/skills/ship-readiness-orchestrator/ /Users/warrencain/.claude/skills/ship-readiness-orchestrator/
```

Expected: command exits 0.

- [ ] **Step 3: Verify installed copies match repo**

Run:

```bash
diff -qr plugins/shipworthy/skills/ship-readiness-orchestrator /Users/warrencain/.codex/skills/ship-readiness-orchestrator
diff -qr plugins/shipworthy/skills/ship-readiness-orchestrator /Users/warrencain/.claude/skills/ship-readiness-orchestrator
```

Expected: no output.

- [ ] **Step 4: Remove installer backup folders if any were created**

Run:

```bash
find /Users/warrencain/.codex/skills /Users/warrencain/.claude/skills -maxdepth 2 -type d -name '*backup*' -print
```

Expected: no output. If backup folders appear, remove only the backup folders created by this sync and rerun the `find` command.

## Task 6: Full Validation

**Files:**
- Read/execute: repo tests and skill scripts.

- [ ] **Step 1: Run the focused Shipworthy validation scripts**

Run:

```bash
python3 plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_skill_contract.py
python3 plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_render_report.py
python3 plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_make_bundle.py
python3 plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/test_to_sarif.py
```

Expected: all checks pass.

- [ ] **Step 2: Run the repo-level validation command**

Run:

```bash
python3 scripts/validate.py
```

Expected: validation passes. If the repo uses a different canonical validation command, inspect `README.md` and `.github/workflows/` and run the documented equivalent.

- [ ] **Step 3: Render a sample downgraded report**

Run:

```bash
python3 plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/render_report.py plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/sample-report.json /tmp/shipworthy-sample-readiness-report.html
test -s /tmp/shipworthy-sample-readiness-report.html
```

Expected: renderer writes a nonempty HTML file.

- [ ] **Step 4: Confirm no stale optional wording remains**

Run:

```bash
rg -n "generate it when requested|HTML report.*optional|readiness-report.html.*optional" plugins/shipworthy/skills README.md ARCHITECTURE.md
```

Expected: no operational wording that makes `readiness-report.html` optional for Shipworthy invocations.

## Task 7: Commit, Push, And Hosted Proof

**Files:**
- Stage only intended docs/tests/skill files from previous tasks.

- [ ] **Step 1: Inspect final diff**

Run:

```bash
git diff --stat
git diff --check
git status --short
```

Expected: only intended Shipworthy plan/docs/tests/skill changes; `git diff --check` has no output.

- [ ] **Step 2: Commit changes**

Run:

```bash
git add docs/superpowers/plans/2026-07-08-shipworthy-html-report-gate-followup.md
git add plugins/shipworthy/skills/ship-readiness-orchestrator README.md ARCHITECTURE.md
git commit -m "Harden Shipworthy HTML report gate"
```

Expected: commit succeeds. If Task 1 proves no implementation patches were needed and only this plan was created, use:

```bash
git add docs/superpowers/plans/2026-07-08-shipworthy-html-report-gate-followup.md
git commit -m "docs: plan Shipworthy HTML report gate follow-up"
```

- [ ] **Step 3: Push and verify hosted CI**

Run:

```bash
git push origin main
gh run list --limit 5
```

Expected: push succeeds and latest validation workflow starts or passes. If queued, wait for the run and report the final GitHub Actions URL.

## Final Completion Criteria

- The current repo has an explicit always-on HTML Report Gate.
- Downgraded/static/source-CLI Shipworthy runs still generate `readiness-report.html`.
- Final answer contract requires absolute HTML report path.
- The TraceFlow HTML report miss exists as a live regression reference.
- Contract and renderer tests prove the invariant.
- Installed Codex and Claude skill copies match the repo.
- Local full validation passes.
- Changes are committed and pushed, or the final answer explicitly says no implementation patch was needed and why.

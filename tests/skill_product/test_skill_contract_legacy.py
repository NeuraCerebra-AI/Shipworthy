#!/usr/bin/env python3
from pathlib import Path
import sys
import unittest

if __name__ != "__main__":
    raise unittest.SkipTest("legacy aggregate suite runs as a direct script")

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "plugins" / "shipworthy"
ORCH = ROOT / "skills" / "ship-readiness-orchestrator"
SKILL = ORCH / "SKILL.md"
PRESSURE = ORCH / "references" / "pressure-tests.md"
LIVE_REGRESSION = ORCH / "references" / "live-regressions" / "traceflow-html-report-miss.md"
HTML = ORCH / "references" / "visual-html-report.md"
EXPORTS = ORCH / "references" / "exports-and-ci.md"
WAVES = ROOT / "skills" / "ship-deep-review" / "references" / "wave-protocol.md"
LANES = ORCH / "references" / "lane-prompts.md"
BROWSER_ROUTING = ORCH / "references" / "browser-evidence-routing.md"
HOST_EXECUTION = ORCH / "references" / "host-execution-recipes.md"
PRODUCT_WORKFLOWS = ROOT / "skills" / "ship-product-workflows" / "SKILL.md"
DEEP_REVIEW = ROOT / "skills" / "ship-deep-review" / "SKILL.md"
WORKFLOW_CLARITY = ROOT / "skills" / "ship-workflow-clarity" / "SKILL.md"
README = REPO / "README.md"
ARCH = REPO / "ARCHITECTURE.md"
INSTALL = REPO / "install.sh"
HERO_SVG = REPO / "assets" / "hero.svg"
FLOW_SVG = REPO / "assets" / "flow.svg"
SAMPLE_SVG = REPO / "assets" / "sample-report.svg"
ARCH_SVG = REPO / "assets" / "architecture.svg"

PASS = []
FAIL = []

def read(path):
    return path.read_text(encoding="utf-8")

def ck(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{'' if cond else '  -> '+detail}")

skill = read(SKILL)
pressure = read(PRESSURE)
live = read(LIVE_REGRESSION)
html = read(HTML)
exports = read(EXPORTS)
waves = read(WAVES)
lanes = read(LANES)
browser_routing = read(BROWSER_ROUTING) if BROWSER_ROUTING.exists() else ""
host_execution = read(HOST_EXECUTION) if HOST_EXECUTION.exists() else ""
product_workflows = read(PRODUCT_WORKFLOWS)
readme = read(README)
arch = read(ARCH)
install = read(INSTALL)
hero_svg = read(HERO_SVG)
flow_svg = read(FLOW_SVG)
sample_svg = read(SAMPLE_SVG)
arch_svg = read(ARCH_SVG)
all_text = "\n".join([skill, pressure, html, exports, waves, lanes, readme, arch, install])
frontmatter = skill.split("---", 2)[1]
description = next((line.split(":", 1)[1].strip() for line in frontmatter.splitlines() if line.startswith("description:")), "")

for phrase in ["shipworthy", "are we shipworthy?", "are we shipready?", "is this shipworthy?", "shipworthy this", "check shipworthiness"]:
    ck(f"T1 trigger phrase present: {phrase}", phrase in skill.lower())

ck("T0 frontmatter description stays concise", len(description) <= 500, f"chars={len(description)}")
ck("T2 invocation contract section", "## Shipworthy Invocation Contract" in skill)
ck("T3 operational mention means full blast", "operational mention of `shipworthy`" in skill and "full blast" in skill.lower())
ck("T4 explicit narrow-scope exception", "unless the user explicitly narrows" in skill.lower())
ck("T5 no target still triggers target gate", "If no target is obvious" in skill)

ck("W1 minimum three verified waves in orchestrator", "minimum of three verified waves" in skill.lower())
ck("W2 adaptive continuation in orchestrator", "adaptive continuation" in skill.lower())
ck("W3 wave protocol minimum three", "minimum of three verified waves" in waves.lower())
ck("W4 wave protocol extra waves", "additional waves" in waves.lower() and "coverage" in waves.lower())

ck("P1 path-universe closure", "path-universe closure" in skill.lower())
ck("P2 all safe discoverable paths stressed", "all safe discoverable" in skill.lower())
ck("P3 closure labels include sampled justification", "sampled with justification" in all_text.lower())
ck("P4 visual contract accepts canonical coverage labels", "evidence_debt" in html and "out_of_scope" in html)
ck("P5 visual contract documents severity aliases", "p0 blocker" in html.lower() and "high" in html.lower())

ck("H1 mandatory HTML report in orchestrator", "mandatory html report" in skill.lower())
ck("H2 default external report path", "~/.shipworthy/runs/<target-slug>/<timestamp>/readiness-report.html" in all_text)
ck("H3 visual report no longer optional-only", "Shipworthy invocation means HTML report, always" in html)
ck("H3 full runs do not call HTML optional", "optional deliverables" not in skill.lower())
ck("H3 exports force mandatory HTML for runs", "part of the completion contract" in exports.lower())
ck("H4 report is renderer/template driven", "compact ledger json" in html.lower() and "never generate full html by hand" in html.lower())
ck("H5 exports doc reflects mandatory operational report", "every operational shipworthy invocation" in exports.lower())
ck("H6 operational invocation always produces HTML", "Every operational Shipworthy invocation must produce a self-contained HTML readiness report" in skill)
ck("H7 downgrade keeps report requirement", "Downgrade status changes the report contents and verdict language; it does not remove the report requirement" in skill)
ck("H8 pre-final verifies report file exists", "Before final response, verify that `readiness-report.html` exists" in skill)
ck("H9 visual report mandatory for downgraded runs", "Shipworthy invocation means HTML report, always" in html)
stale_optional_report_phrase = "For rapid, narrow, or static constrained passes, generate it " + "when requested"
ck("H10 constrained reports not optional by default", stale_optional_report_phrase not in html)
ck("H11 final answer requires HTML path", "Every Shipworthy final answer must include" in read(ORCH / "references" / "final-report-contract.md"))
ck("H12 report contract includes generation fields", all(x in html for x in ["report_generation_status", "report_path", "ledger_path", "evidence_locations"]))
ck("H13 visual report uses action-first sections", all(x in html for x in ["Clear Before Ship", "Fix Next", "Not Proven / Not Tested", "Passed / Keep"]))
ck("H14 visual report documents action/proof chips", all(x in html for x in ["Fix | Prove | Decide | Skip | Keep", "Confirmed | Partial | Inferred | Not tested"]))
ck("H15 visual report bans old visible buckets", all(x not in html for x in ["Strong signals", "Working Signals", "visible category: `Provisional`"]))
ck("H16 final report contract uses action-first sections", all(x in read(ORCH / "references" / "final-report-contract.md") for x in ["Clear Before Ship", "Fix Next", "Not Proven / Not Tested", "Passed / Keep"]))
ck("H17 inline final CTA asks for persistent fix goal", "Recommended next step: reply **yes** and I’ll start a persistent fix goal" in skill or "Recommended next step: reply **yes** and I'll start a persistent fix goal" in skill)
ck("H18 inline CTA requires verify and regenerate report", "verify each one" in skill.lower() and "regenerate the shipworthy html report" in skill.lower())
ck("H19 inline CTA mentions authorized subagents", "using authorized subagents where helpful" in skill.lower())
ck("H20 final report contract repeats fix-goal handoff", "Recommended next step: reply **yes**" in read(ORCH / "references" / "final-report-contract.md") and "using authorized subagents where helpful" in read(ORCH / "references" / "final-report-contract.md"))

ck("A1 shared runtime agent rule", "single coordinated runtime driver" in skill.lower())
ck("A2 isolated contexts allow parallel runtime drivers", "isolated" in skill.lower() and "browser profiles" in skill.lower())
ck("A3 lane prompts include runtime coordination", "runtime driver" in lanes.lower())
ck("A4 multi-agent authorization gate exists", "## Multi-Agent Authorization Gate" in skill)
ck("A5 authorization question uses policy words", "do you authorize parallel subagents / delegation / multi-agent work" in skill.lower())
ck("A6 dispatch only after explicit authorization", "only dispatch subagents after the user explicitly authorizes" in skill.lower())
ck("A7 pre-authorized prompt can proceed", "parallel subagents authorized" in skill.lower())
ck("A8 missing authorization sequential fallback debt", "sequential fallback because multi-agent authorization was not granted" in all_text.lower())
ck("A9 skill does not override platform tool policy", "do not imply that shipworthy instructions override platform tool policy" in skill.lower())
ck("A10 lane prompts carry authorization status", "multi-agent authorization status" in lanes.lower())
ck("A11 final report exposes skipped agent dispatch", "authorization status" in read(EXPORTS).lower() or "authorization status" in read(ORCH / "references" / "final-report-contract.md").lower())
ck("A12 architecture includes authorization gate", "multi-agent authorization gate" in arch.lower())
ck("A13 README says agents require authorization", "uses agents where authorized" in readme.lower())
ck("A14 HTML checkpoint carries authorization", "multi_agent_authorization" in html and "authorization" in read(REPO / "tests" / "skill_product" / "fixtures" / "sample-report.json").lower())
ck("A15 plain trigger must ask then stop", "ask the authorization question and stop" in skill.lower())
ck("A16 no same-turn sequential fallback before asking", "do not continue sequentially in the same response" in skill.lower())
ck("A17 not received only after unanswered gate", "not received means the user failed to answer after the authorization question was asked" in skill.lower())
ck("A18 screenshot caveat pressure test", "ignore claude/anthropic as llm provider" in pressure.lower() and "asks the authorization question and stops" in pressure.lower())
ck("F1 flagship frontend path-walk gate exists", "## Flagship Frontend Path-Walk Gate" in skill)
ck("F2 full run requires actual frontend path-walking", "actual frontend path-walking" in skill.lower() and "human-style frontend" in all_text.lower())
ck("F3 source CLI HTTP not substitute", "supporting evidence, not as a substitute for frontend path-walking" in all_text.lower())
ck("F4 no path-walk downgrades verdict", "if no actual frontend path-walking occurred" in skill.lower() and "not a full shipworthy run" in skill.lower())
ck("F5 report contract includes frontend path-walk fields", "frontend_path_walk_performed" in html and "path_walk_status" in html and "frontend_tool" in html)
ck("F6 final report gate requires frontend path-walk status", "frontend path-walk status" in read(ORCH / "references" / "final-report-contract.md").lower())
ck("F7 verifier fails full claim without path-walk", "fail the full-run claim if no browser/computer-use/frontend path-walk occurred" in pressure.lower() or "fail the full-run claim if no browser/computer-use/frontend path-walk occurred" in lanes.lower())
ck("F8 pressure tests forbid source-only flagship", "source/cli/http-only readiness audit is not a full shipworthy run" in pressure.lower())
ck("F9 README says full uses frontend when available", "actual frontend" in readme.lower() and "supporting evidence" in readme.lower())

browser_reference = browser_routing.lower()
final_report_contract = read(ORCH / "references" / "final-report-contract.md").lower()
ck("B1 browser evidence routing reference exists", BROWSER_ROUTING.is_file())
ck("B2 canonical reference defaults adaptive exploration to native host tools", all(x in browser_reference for x in ["native browser", "computer-use", "default for adaptive exploration"]))
ck("B3 canonical reference limits Playwright to deterministic proof uses", all(x in browser_reference for x in ["deterministic replay", "explicit assertions", "isolated contexts", "traces", "cross-browser", "ci regression proof"]))
ck("B4 canonical reference bounds screenshot proof", "a screenshot proves only the state visible at capture time" in browser_reference and "does not prove an entire workflow" in browser_reference)
ck("B5 canonical reference forbids proof and verifier inflation", all(x in browser_reference for x in ["must not silently upgrade", "`confirmed`", "`approved`"]))
ck("B6 canonical reference forbids installation and evidence-only target mutation", all(x in browser_reference for x in ["never installs playwright", "never change the target application merely to obtain browser evidence"]))
ck("B7 orchestrator explicitly loads routing reference and records decision boundary", all(x in skill.lower() for x in ["read `references/browser-evidence-routing.md`", "selection", "proof boundary"]))
ck("B8 product workflow loads local browser guidance and distinguishes standalone output", all(x in product_workflows.lower() for x in ["runtime-evidence-and-tools.md", "include in the audit output", "return to the orchestrator when lane-dispatched", "neither native nor playwright evidence may silently upgrade"]))
ck("B9 lane prompt explicitly loads routing reference and returns decision context", all(x in lanes.lower() for x in ["read `browser-evidence-routing.md`", "selection reason", "proof boundary"]))
ck("B10 final-report contract records routing reference and evidence context", all(x in final_report_contract for x in ["browser-evidence-routing.md", "selection reason", "observed step boundary", "not-proven statements"]))
expected_skill_names = {
    "ship-readiness-orchestrator": SKILL,
    "ship-product-workflows": PRODUCT_WORKFLOWS,
    "ship-deep-review": DEEP_REVIEW,
    "ship-workflow-clarity": WORKFLOW_CLARITY,
}
ck("B11 four public skill names remain exact", all(f"name: {name}" in read(path) for name, path in expected_skill_names.items()))
public_trigger_phrases = {
    SKILL: ["are we shipworthy?", "check shipworthiness"],
    PRODUCT_WORKFLOWS: ["product workflow audits", "try every path"],
    DEEP_REVIEW: ["explicitly invokes or names ship-deep-review", "required controller"],
    WORKFLOW_CLARITY: ["workflow clarity", "where users get lost"],
}
ck("B12 all four public skill trigger descriptions remain recognizable", all(all(phrase in read(path).split("---", 2)[1].lower() for phrase in phrases) for path, phrases in public_trigger_phrases.items()))
ck("B13 public routing surfaces preserve four-skill standalone operation", all("four public skills" in text_value.lower() and "without requiring another product surface" in text_value.lower() for text_value in [browser_routing, skill, product_workflows]))
ck("B14 mandatory HTML contract survives browser routing", "mandatory html report" in skill.lower() and "every shipworthy final answer must include" in final_report_contract)

host_execution_reference = host_execution.lower()
ck("E1 host execution recipe exists", HOST_EXECUTION.is_file())
execution_order_markers = [
    "1. **discover and run target-owned tests.**",
    "2. **use native browser or computer-use for adaptive discovery.**",
    "3. **reuse an existing target-owned playwright setup for deterministic replay.**",
    "4. **propose a minimal target-owned playwright test only with explicit user authorization.**",
    "5. **record unavailable execution as evidence debt.**",
]
execution_order_positions = [host_execution_reference.find(marker) for marker in execution_order_markers]
ck("E2 host execution recipe preserves the required decision order", all(position >= 0 for position in execution_order_positions) and execution_order_positions == sorted(execution_order_positions))
ck("E3 orchestrator loads the host execution reference", "read `references/host-execution-recipes.md`" in skill.lower())
ck("E4 target tests never replace the flagship frontend gate", "supporting evidence and never replace" in host_execution_reference and "required native frontend path-walk" in host_execution_reference)
ck("E5 exports link the passive host execution boundary", "host-execution-recipes.md" in exports.lower() and "does not run target commands" in exports.lower())

ck("G1 goal mode persistence gate exists", "## Goal Mode Persistence Gate" in skill)
ck("G2 goal gate has policy caveat", "do not imply that shipworthy instructions override platform goal-mode policy" in skill.lower())
ck("G3 combined yes wording", "recommended: reply yes to authorize persistent goal mode and parallel subagents for this shipworthy run" in skill.lower())
ck("G4 goal status recorded", "goal_mode_status" in all_text and "goal-equivalent resumable ledger" in all_text.lower())
ck("G5 README recommends slash-goal prompt", "/goal are we shipworthy?" in readme.lower())
ck("G6 README says answer yes", "answer `yes`" in readme.lower() and "parallel subagents" in readme.lower())
ck("G7 Claude goal-equivalent ledger", "claude code" in readme.lower() and "goal-equivalent" in readme.lower())
ck("G8 follow-up yes authorizes both gates", "If the previous assistant message asked the combined authorization question" in skill and "treat that as explicit authorization for both persistent goal mode and parallel subagents" in skill)
ck("G9 follow-up yes activates goal before lanes", "create or continue the persistent Shipworthy goal before lane dispatch" in skill)
ck("G10 pressure test covers yes handoff", "Scenario 0H: User Says Yes To Combined Authorization" in pressure and "Turn 2: `yes`" in pressure and "starts or continues a persistent Shipworthy goal before lane dispatch" in pressure)

ck("X1 adaptive exhaustion gate exists", "## Adaptive Exhaustion Gate" in skill)
ck("X2 path frontier ledger required", "path_frontier" in all_text and "Path Frontier Ledger" in all_text)
ck("X3 no final with unattempted frontier", "full final verdict is forbidden while any material path_frontier row remains `unattempted`, `unknown`, or `maybe`" in skill)
ck("X4 two quiet passes rule", "two consecutive discovery/testing passes find no new material routes, controls, roles, states, device variants, or user intents" in all_text)
ck("X5 human tester matrix", "Human-Tester Matrix" in all_text and "first-time user" in all_text and "keyboard-only user" in all_text)
ck("X6 adaptive budgets documented", "10-20 minutes / 15-30 meaningful attempts" in all_text and "60-90 minutes / 100-200 attempts" in all_text)
ck("X7 incomplete resume status", "exhaustion_status: incomplete" in all_text and "next frontier batch" in all_text.lower())
ck("X8 verifier invents missed paths", "what plausible paths were missed" in all_text.lower())
ck("X9 lane prompts return frontier additions", "frontier additions" in lanes.lower())
ck("X10 report contract requires frontier burn-down", "frontier_total" in read(ORCH / "references" / "final-report-contract.md") and "exhaustion status" in read(ORCH / "references" / "final-report-contract.md").lower())
ck("X11 visual contract includes frontier fields", all(x in html for x in ["goal_mode_status", "frontier_total", "frontier_unattempted", "new_paths_last_wave", "new_paths_previous_wave", "exhaustion_status"]))
ck("X12 pressure test follow-up regression", "do another round" in pressure.lower() and "first run was not exhausted" in pressure.lower())
ck("X13 architecture says frontier closure", "frontier closure" in arch.lower() and "diminishing-discovery" in arch.lower())

ck("D1 README flagship phrase", "are we shipworthy?" in readme.lower())
ck("D2 ARCHITECTURE full-blast gates", "mandatory html report" in arch.lower() and "minimum of three verified waves" in arch.lower())
ck("D3 pressure tests trigger and report", "are we shipworthy?" in pressure.lower() and "mandatory html report" in pressure.lower())
ck("D4 pressure tests shared runtime", "shared runtime" in pressure.lower() and "single coordinated runtime driver" in pressure.lower())
ck("D5 install prompt uses flagship phrase", "are we shipworthy?" in install.lower())
ck("D6 pressure tests include authorization gate", "multi-agent authorization gate" in pressure.lower() and "parallel subagents authorized" in pressure.lower())
ck("D7 installer explains ask-and-stop gate", "ask for authorization and stop" in install.lower())
ck("D8 pressure test catches missing HTML report", "are we shipready?" in pressure.lower() and "readiness-report.html" in pressure and "html report: missing/blocked" in pressure.lower())
ck("D9 TraceFlow live regression exists", "TraceFlow Shipready HTML Report Miss" in live and "/goal are we shipready?" in live)
ck("D10 live regression preserves failure anatomy", all(x in live for x in ["## What went right", "## What went wrong", "## Root cause", "## Required future behavior", "## Regression assertion"]))
ck("D11 live regression requires JSON and HTML outputs", "readiness-report.json" in live and "readiness-report.html" in live)
ck("D12 live regression requires absolute HTML path", "absolute HTML path" in live)
ck("D13 live regression blocks missing-report completion", "HTML report: MISSING/BLOCKED" in live and "must not imply completion" in live)
ck("D14 live regression forbids substituting target artifacts", "does not substitute target-owned HTML" in live and "Markdown ledgers" in live and "screenshots" in live and "chat summaries" in live)
ck("D15 pressure tests link TraceFlow regression", "references/live-regressions/traceflow-html-report-miss.md" in pressure)
ck("D16 README explains action-first report sections", all(x in readme for x in ["Clear Before Ship", "Fix Next", "Not Proven / Not Tested", "Passed / Keep"]))
ck("D17 README raw sample uses new taxonomy", "READINESS: NOT READY" in readme and "Clear Before Ship" in readme and "Passed / Keep" in readme and "Strong signals" not in readme)
ck("D18 README mentions final fix-goal handoff", "persistent fix goal" in readme.lower() and "regenerate the Shipworthy HTML report" in readme)
ck("D18b README fix handoff mentions subagents", "using authorized subagents where helpful" in readme.lower())
ck("D19 sample SVG uses clear action-summary labels", all(x in sample_svg for x in ["Clear Before Ship", "2 fixes required before ship", "1 proof gap", "1 passed path"]))
ck("D20 sample SVG removes old report labels", all(x not in sample_svg for x in ["2 blockers", "1 strong", "3 provisional", "[Blocker]"]))
ck("D21 flow SVG uses clear action terminology", "Action report" in flow_svg and "Fix · Prove · Keep" in flow_svg)
ck("D22 architecture SVG uses general action-report language", "action-first report" in arch_svg)
ck("D23 hero SVG avoids unclear required-fix count", "2 Clear Before Ship" not in hero_svg and "2 fixes required before ship" in hero_svg)
ck("D24 hero coverage legend uses coverage terminology only", "Passed / Keep" not in hero_svg and "Skipped 2" in hero_svg and "Proof missing 1" in hero_svg)
ck("D25 sample SVG uses clear required-fix summary", "2 Clear Before Ship" not in sample_svg and "2 fixes required before ship" in sample_svg)
ck("D26 hero title uses renderer-stable vector outlines", all(x in hero_svg for x in ['id="title-wordmark"', 'data-wordmark-part="ship"', 'data-wordmark-part="worthy"', 'fill="#E8EEF7"', 'fill="#34D399"']) and 'id="title-worthy-clip"' not in hero_svg and 'clip-path="url(#title-worthy-clip)"' not in hero_svg)
ck("D27 hero title preserves the complete two-color wordmark", hero_svg.count('data-wordmark-glyph=') == 10 and hero_svg.count('data-wordmark-part="ship"') == 1 and hero_svg.count('data-wordmark-part="worthy"') == 1)

print(f"\n==== SKILL CONTRACT: {len(PASS)} passed, {len(FAIL)} failed ====")
if FAIL:
    print("FAILURES:", FAIL)
    sys.exit(1)
print("ALL SKILL CONTRACT TESTS PASSED")

#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
ORCH = ROOT / "skills" / "ship-readiness-orchestrator"
SKILL = ORCH / "SKILL.md"
PRESSURE = ORCH / "references" / "pressure-tests.md"
HTML = ORCH / "references" / "visual-html-report.md"
EXPORTS = ORCH / "references" / "exports-and-ci.md"
WAVES = ROOT / "skills" / "ship-deep-review" / "references" / "wave-protocol.md"
LANES = ORCH / "references" / "lane-prompts.md"
README = ROOT.parents[1] / "README.md"
ARCH = ROOT.parents[1] / "ARCHITECTURE.md"
INSTALL = ROOT.parents[1] / "install.sh"

PASS = []
FAIL = []

def read(path):
    return path.read_text(encoding="utf-8")

def ck(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{'' if cond else '  -> '+detail}")

skill = read(SKILL)
pressure = read(PRESSURE)
html = read(HTML)
exports = read(EXPORTS)
waves = read(WAVES)
lanes = read(LANES)
readme = read(README)
arch = read(ARCH)
install = read(INSTALL)
all_text = "\n".join([skill, pressure, html, exports, waves, lanes, readme, arch, install])
frontmatter = skill.split("---", 2)[1]
description = next((line.split(":", 1)[1].strip() for line in frontmatter.splitlines() if line.startswith("description:")), "")

for phrase in ["shipworthy", "are we shipworthy?", "is this shipworthy?", "shipworthy this", "check shipworthiness"]:
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
ck("H3 visual report no longer optional-only", "generate it by default" in html.lower())
ck("H3 full runs do not call HTML optional", "optional deliverables" not in skill.lower())
ck("H3 exports force mandatory HTML for full runs", "force the html render" in exports.lower())
ck("H4 report is renderer/template driven", "compact ledger json" in html.lower() and "never generate full html by hand" in html.lower())
ck("H5 exports doc reflects mandatory full-blast report", "full shipworthy invocation" in exports.lower())

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
ck("A14 HTML checkpoint carries authorization", "multi_agent_authorization" in html and "authorization" in read(ORCH / "scripts" / "sample-report.json").lower())
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

ck("D1 README flagship phrase", "are we shipworthy?" in readme.lower())
ck("D2 ARCHITECTURE full-blast gates", "mandatory html report" in arch.lower() and "minimum of three verified waves" in arch.lower())
ck("D3 pressure tests trigger and report", "are we shipworthy?" in pressure.lower() and "mandatory html report" in pressure.lower())
ck("D4 pressure tests shared runtime", "shared runtime" in pressure.lower() and "single coordinated runtime driver" in pressure.lower())
ck("D5 install prompt uses flagship phrase", "are we shipworthy?" in install.lower())
ck("D6 pressure tests include authorization gate", "multi-agent authorization gate" in pressure.lower() and "parallel subagents authorized" in pressure.lower())
ck("D7 installer explains ask-and-stop gate", "ask for authorization and stop" in install.lower())

print(f"\n==== SKILL CONTRACT: {len(PASS)} passed, {len(FAIL)} failed ====")
if FAIL:
    print("FAILURES:", FAIL)
    sys.exit(1)
print("ALL SKILL CONTRACT TESTS PASSED")

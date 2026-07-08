#!/usr/bin/env python3
"""Simulation suite for to_sarif.py — SARIF 2.1.0 structure, severity mapping,
fingerprint stability, honest location handling, and the policy gate exit codes.
Dependency-free (no jsonschema) so it runs in minimal CI."""
import os, sys, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from to_sarif import to_sarif  # noqa: E402

SAMPLE = os.path.join(HERE, "sample-report.json")
SCRIPT = os.path.join(HERE, "to_sarif.py")
data = json.load(open(SAMPLE, encoding="utf-8"))

PASS, FAIL = [], []
def ck(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  {'PASS' if c else 'FAIL'}  {n}{'' if c else '  -> ' + d}")

s = to_sarif(data); run = s["runs"][0]; results = run["results"]
ck("S1 version 2.1.0", s.get("version") == "2.1.0")
ck("S2 has $schema", "sarif-2.1.0" in s.get("$schema", ""))
ck("S3 tool.driver.name", run["tool"]["driver"]["name"] == "Shipworthy")
ck("S4 results==findings", len(results) == len(data["findings"]))
ck("S5 ruleId+message+level on each", all(r.get("ruleId") and r["message"].get("text") and r.get("level") for r in results))
ruleids = {r["id"] for r in run["tool"]["driver"]["rules"]}
ck("S6 every ruleId declared", all(r["ruleId"] in ruleids for r in results))
ck("S7 partialFingerprints on each", all(r.get("partialFingerprints") for r in results))
lv = {r["ruleId"]: r["level"] for r in results}
ck("S8 blocker->error", lv.get("shipworthy/blocker") == "error")
ck("S9 strong->warning", lv.get("shipworthy/strong") == "warning")
ck("S10 provisional->note", lv.get("shipworthy/provisional") == "note")
fp1 = [r["partialFingerprints"]["shipworthyFindingHash/v1"] for r in results]
fp2 = [r["partialFingerprints"]["shipworthyFindingHash/v1"] for r in to_sarif(data)["runs"][0]["results"]]
ck("S11 fingerprints stable across runs", fp1 == fp2)
ck("S12 fingerprints unique", len(set(fp1)) == len(fp1))
ck("S13 no fake locations for UX/path findings", all("locations" not in r for r in results))
lr = to_sarif({"findings": [{"severity": "blocker", "title": "x", "location": {"file": "src/pay.ts", "line": 42}}]})["runs"][0]["results"][0]
ck("S14 located finding -> uri+startLine",
   lr["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "src/pay.ts"
   and lr["locations"][0]["physicalLocation"]["region"]["startLine"] == 42)
ck("S15 empty ledger -> empty run", to_sarif({})["runs"][0]["results"] == [])
ck("S16 unknown severity -> note", to_sarif({"findings": [{"severity": "weird", "title": "x"}]})["runs"][0]["results"][0]["level"] == "note")

def gate(fixture):
    json.dump(fixture, open(os.path.join(HERE, "_g.json"), "w"))
    rc = subprocess.run([sys.executable, SCRIPT, os.path.join(HERE, "_g.json"),
                         os.path.join(HERE, "_g.sarif"), "--gate"], capture_output=True, text=True).returncode
    return rc

ck("G1 2 confirmed blockers -> exit 1", gate(data) == 1)
ck("G2 clean report -> exit 0", gate({"findings": [{"severity": "provisional", "title": "m"}]}) == 0)
ck("G3 unconfirmed blocker + require_confirmed -> 0", gate({"findings": [{"severity": "blocker", "confidence": "provisional", "title": "m"}]}) == 0)
ck("G4 unconfirmed blocker + require_confirmed:false -> 1",
   gate({"findings": [{"severity": "blocker", "confidence": "provisional", "title": "m"}], "policy": {"fail_on": ["blocker"], "require_confirmed": False}}) == 1)
ck("G5 custom policy fail_on strong -> 1",
   gate({"findings": [{"severity": "strong", "confidence": "strong", "title": "s"}], "policy": {"fail_on": ["strong"], "require_confirmed": False}}) == 1)
ck("G6 no findings -> exit 0", gate({}) == 0)

for f in ("_g.json", "_g.sarif"):
    try: os.remove(os.path.join(HERE, f))
    except OSError: pass

print(f"\n==== SARIF+GATE: {len(PASS)} passed, {len(FAIL)} failed ====")
if FAIL:
    print("FAILURES:", FAIL); sys.exit(1)
print("ALL SARIF TESTS PASSED")

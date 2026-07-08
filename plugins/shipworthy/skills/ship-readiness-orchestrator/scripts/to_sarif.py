#!/usr/bin/env python3
"""
Shipworthy — convert a readiness ledger (JSON) into a SARIF 2.1.0 file for GitHub
code scanning (PR annotations, Security-tab alerts, native new/fixed tracking) and,
optionally, act as a merge gate via exit code.

Usage:
    python3 to_sarif.py [ledger.json] [out.sarif] [--gate]

Design notes:
- Severity -> SARIF level: blocker=error, strong=warning, provisional/info=note.
  GitHub branch protection can require "no new error-level results", so only
  blockers block by default.
- A finding may carry an optional {"location": {"file": "...", "line": N}}. Findings
  WITH a location get a physicalLocation (inline PR annotation possible); UX / path /
  missing-path findings with NO location are emitted without locations and appear as
  repository-level alerts. This is honest partial fidelity, not a fake line number.
- partialFingerprints are stable across runs (hash of severity + normalized title),
  so GitHub dedupes and computes new/fixed correctly.
- --gate: exit non-zero per policy. Default policy = fail on CONFIRMED blockers only
  (high-precision; provisional findings never block a build). Override via the ledger's
  optional "policy": {"fail_on": ["blocker"], "require_confirmed": true}.
"""
import sys, json, hashlib, re

TOOL_URI = "https://github.com/NeuraCerebra-AI/shipworthy"
LEVEL = {"blocker": "error", "strong": "warning", "provisional": "note", "info": "note"}
RULE_NAME = {"blocker": "Blocker", "strong": "Strong signal",
             "provisional": "Provisional finding", "info": "Note"}
DEFAULT_POLICY = {"fail_on": ["blocker"], "require_confirmed": True}

def norm(s): return re.sub(r"\s+", " ", str(s or "").strip().lower())

def fingerprint(sev, title):
    return hashlib.sha256(f"{norm(sev)}|{norm(title)}".encode("utf-8")).hexdigest()[:20]

def message_for(f):
    bits = [str(f.get("title", "(untitled finding)"))]
    if f.get("consequence"): bits.append(f"Impact: {f['consequence']}")
    if f.get("evidence"):    bits.append(f"Evidence: {f['evidence']}")
    if f.get("fix"):         bits.append(f"Fix: {f['fix']}")
    if f.get("verify"):      bits.append(f"Verify: {f['verify']}")
    return "  ".join(bits)

def result_for(f):
    sev = f.get("severity", "info")
    sev = sev if sev in LEVEL else "info"
    res = {
        "ruleId": f"shipworthy/{sev}",
        "level": LEVEL[sev],
        "message": {"text": message_for(f)},
        "partialFingerprints": {"shipworthyFindingHash/v1": fingerprint(sev, f.get("title"))},
    }
    loc = f.get("location") if isinstance(f.get("location"), dict) else None
    if loc and loc.get("file"):
        region = {}
        line = loc.get("line")
        try:
            if line is not None and int(line) > 0:
                region["startLine"] = int(line)
        except (TypeError, ValueError):
            pass
        phys = {"artifactLocation": {"uri": str(loc["file"])}}
        if region:
            phys["region"] = region
        res["locations"] = [{"physicalLocation": phys}]
    # else: no location -> repository-level alert (honest for UX/path findings)
    return res

def to_sarif(data):
    if not isinstance(data, dict): data = {}
    findings = [f for f in (data.get("findings") or []) if isinstance(f, dict)]
    used = sorted({(f.get("severity") if f.get("severity") in LEVEL else "info") for f in findings})
    rules = [{
        "id": f"shipworthy/{sev}",
        "name": RULE_NAME[sev],
        "shortDescription": {"text": f"Shipworthy {RULE_NAME[sev]}"},
        "defaultConfiguration": {"level": LEVEL[sev]},
    } for sev in used]
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": "Shipworthy",
                "informationUri": TOOL_URI,
                "version": str(data.get("tool_version", "0.1.0")),
                "rules": rules,
            }},
            "automationDetails": {"id": "shipworthy-readiness"},
            "results": [result_for(f) for f in findings],
        }],
    }

def gate_failures(data):
    policy = data.get("policy") if isinstance(data.get("policy"), dict) else DEFAULT_POLICY
    fail_on = policy.get("fail_on", DEFAULT_POLICY["fail_on"])
    require_confirmed = policy.get("require_confirmed", DEFAULT_POLICY["require_confirmed"])
    hits = []
    for f in (data.get("findings") or []):
        if not isinstance(f, dict): continue
        if f.get("severity") in fail_on:
            if (not require_confirmed) or norm(f.get("confidence")) == "confirmed":
                hits.append(f.get("title", "(untitled)"))
    return hits, fail_on, require_confirmed

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    gate = "--gate" in sys.argv[1:]
    inp = args[0] if len(args) > 0 else "readiness-report.json"
    out = args[1] if len(args) > 1 else "readiness.sarif"
    try:
        with open(inp, encoding="utf-8") as fh: data = json.load(fh)
    except FileNotFoundError:
        print(f"error: input not found: {inp}", file=sys.stderr); sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"error: {inp} is not valid JSON ({e})", file=sys.stderr); sys.exit(2)
    sarif = to_sarif(data)
    with open(out, "w", encoding="utf-8") as fh: json.dump(sarif, fh, indent=2)
    n = len(sarif["runs"][0]["results"])
    errs = sum(1 for r in sarif["runs"][0]["results"] if r["level"] == "error")
    print(f"wrote {out}: {n} results ({errs} error-level) from {inp}")
    if gate:
        hits, fail_on, req = gate_failures(data)
        if hits:
            print(f"GATE: FAIL — {len(hits)} {'confirmed ' if req else ''}{'/'.join(fail_on)} finding(s):", file=sys.stderr)
            for h in hits: print(f"  - {h}", file=sys.stderr)
            sys.exit(1)
        print("GATE: PASS")
    sys.exit(0)

if __name__ == "__main__":
    main()

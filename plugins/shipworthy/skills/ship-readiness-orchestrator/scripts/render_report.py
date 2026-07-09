#!/usr/bin/env python3
"""
Shipworthy — render a structured readiness audit into a self-contained HTML report.

Usage:
    python3 render_report.py [input.json] [output.html]

Produces ONE self-contained file: inline CSS, system fonts, and no network calls.
Default output has no JavaScript; --interactive adds inline no-network controls.
Every text field is HTML-escaped; the renderer degrades gracefully on partial or
degenerate data instead of crashing.
"""
import sys, json, html, datetime, re

COV = {
    "covered": "#34D399", "sampled": "#3B82F6", "blocked": "#F59E0B",
    "avoided": "#9F5B6B", "inferred": "#38BDF8", "missing": "#F43F5E",
    "out_of_scope": "#64748B", "evidence_debt": "#3A4763",
    "debt": "#3A4763",
}
COV_LABEL = {
    "covered": "Tried + evidenced", "sampled": "Spot-checked", "blocked": "Blocked",
    "avoided": "Skipped for safety", "inferred": "Inferred", "missing": "Missing",
    "out_of_scope": "Out of scope", "evidence_debt": "Proof missing",
    "debt": "Proof missing",
}
SECTION = {
    "clear_before_ship": ("#F43F5E", "Clear Before Ship", "tier-clear-before-ship"),
    "fix_next": ("#F59E0B", "Fix Next", "tier-fix-next"),
    "not_proven_not_tested": ("#38BDF8", "Not Proven / Not Tested", "tier-not-proven"),
    "passed_keep": ("#34D399", "Passed / Keep", "tier-passed-keep"),
}
SECTION_ORDER = ["clear_before_ship", "fix_next", "not_proven_not_tested", "passed_keep"]
SEV_ALIAS = {
    "blocker": "blocker", "critical": "blocker", "p0 blocker": "blocker", "p0": "blocker",
    "strong": "strong", "major": "strong", "high": "strong", "p1 major": "strong", "p1": "strong",
    "provisional": "provisional", "moderate": "provisional", "medium": "provisional", "p2 moderate": "provisional", "p2": "provisional",
    "info": "info", "note": "info", "minor": "info", "low": "info", "p3 minor": "info", "p3": "info",
    "unscored": "info", "hypothesis": "info", "preserve note": "info",
}
SECTION_ALIAS = {
    "clear before ship": "clear_before_ship",
    "clear": "clear_before_ship",
    "fix before ship": "clear_before_ship",
    "must fix before ship": "clear_before_ship",
    "blocks readiness": "clear_before_ship",
    "release blocker": "clear_before_ship",
    "blocker": "clear_before_ship",
    "critical": "clear_before_ship",
    "p0 blocker": "clear_before_ship",
    "p0": "clear_before_ship",
    "fix next": "fix_next",
    "should fix": "fix_next",
    "quality issue": "fix_next",
    "broken or risky workflow": "fix_next",
    "major": "fix_next",
    "high": "fix_next",
    "p1 major": "fix_next",
    "p1": "fix_next",
    "moderate": "fix_next",
    "medium": "fix_next",
    "p2 moderate": "fix_next",
    "p2": "fix_next",
    "provisional": "fix_next",
    "not proven not tested": "not_proven_not_tested",
    "not proven / not tested": "not_proven_not_tested",
    "not proven": "not_proven_not_tested",
    "not tested": "not_proven_not_tested",
    "needs proof": "not_proven_not_tested",
    "proof missing": "not_proven_not_tested",
    "evidence debt": "not_proven_not_tested",
    "skipped": "not_proven_not_tested",
    "unknown": "not_proven_not_tested",
    "maybe": "not_proven_not_tested",
    "hypothesis": "not_proven_not_tested",
    "info": "not_proven_not_tested",
    "note": "not_proven_not_tested",
    "minor": "not_proven_not_tested",
    "low": "not_proven_not_tested",
    "p3 minor": "not_proven_not_tested",
    "p3": "not_proven_not_tested",
    "unscored": "not_proven_not_tested",
    "passed keep": "passed_keep",
    "passed / keep": "passed_keep",
    "passed": "passed_keep",
    "keep": "passed_keep",
    "passed in this run": "passed_keep",
    "working": "passed_keep",
    "worked": "passed_keep",
    "strong": "passed_keep",
}
ACTION_ALIAS = {
    "fix": "Fix", "prove": "Prove", "decide": "Decide", "skip": "Skip", "keep": "Keep",
    "preserve": "Keep", "investigate": "Prove", "verify": "Prove", "defer": "Decide",
}
PROOF_ALIAS = {
    "confirmed": "Confirmed", "direct": "Confirmed", "observed": "Confirmed", "reproduced": "Confirmed",
    "partial": "Partial", "strong": "Partial", "provisional": "Partial", "some proof": "Partial",
    "inferred": "Inferred", "hypothesis": "Inferred", "assumed": "Inferred",
    "not tested": "Not tested", "not_tested": "Not tested", "untested": "Not tested",
    "skipped": "Not tested", "blocked": "Not tested", "unknown": "Not tested",
}
VERDICT = {
    "NOT READY":        ("#2A1220", "#7F2740", "#FB7185"),
    "READY WITH RISKS": ("#241A05", "#7A5A16", "#FBBF24"),
    "CONDITIONAL":      ("#241A05", "#7A5A16", "#FBBF24"),
    "READY":            ("#0B241A", "#1E6B4E", "#34D399"),
}
VERDICT_NEUTRAL = ("#141A28", "#2A3654", "#AEBAD4")  # unknown verdict -> neutral, not alarming

def esc(x): return html.escape("" if x is None else str(x))

def row_text(x):
    if isinstance(x, list):
        return " · ".join(str(v) for v in x)
    return x

def title_case(x):
    return " ".join(w[:1].upper() + w[1:].lower() for w in str(x).split())

def num(x, default=0.0):
    try:
        v = float(x); return v if v == v else default   # reject NaN
    except (TypeError, ValueError):
        return default

def norm_token(x):
    return re.sub(r"\s+", " ", str(x or "").strip().lower().replace("_", " ").replace("-", " "))

def cov_kind(x):
    k = norm_token(x).replace(" ", "_")
    if k == "debt":
        return "evidence_debt"
    return k

def cov_label(s):
    s = s or {}
    kind = cov_kind(s.get("kind"))
    return s.get("label") or COV_LABEL.get(kind) or norm_token(s.get("kind")).replace("_", " ")

def sev_key(x):
    return SEV_ALIAS.get(norm_token(x), "info")

def explicit_section_key(f):
    f = f or {}
    for field in ("section", "category", "bucket", "decision"):
        raw = norm_token(f.get(field))
        if raw:
            k = SECTION_ALIAS.get(raw)
            if k:
                return k
    return None

def section_from_severity(raw):
    t = norm_token(raw)
    if not t:
        return "not_proven_not_tested"
    if t in SECTION_ALIAS:
        return SECTION_ALIAS[t]
    return {
        "blocker": "clear_before_ship",
        "critical": "clear_before_ship",
        "p0 blocker": "clear_before_ship",
        "p0": "clear_before_ship",
        "major": "fix_next",
        "high": "fix_next",
        "p1 major": "fix_next",
        "p1": "fix_next",
        "moderate": "fix_next",
        "medium": "fix_next",
        "p2 moderate": "fix_next",
        "p2": "fix_next",
        "provisional": "fix_next",
        "strong": "passed_keep",
        "info": "not_proven_not_tested",
        "note": "not_proven_not_tested",
        "minor": "not_proven_not_tested",
        "low": "not_proven_not_tested",
        "p3 minor": "not_proven_not_tested",
        "p3": "not_proven_not_tested",
        "unscored": "not_proven_not_tested",
        "hypothesis": "not_proven_not_tested",
        "preserve note": "not_proven_not_tested",
    }.get(t, "not_proven_not_tested")

def section_key(f):
    return explicit_section_key(f) or section_from_severity((f or {}).get("severity"))

def action_label(f, section):
    raw = norm_token((f or {}).get("action") or (f or {}).get("next_action"))
    if raw:
        return ACTION_ALIAS.get(raw, title_case(raw))
    return {
        "clear_before_ship": "Fix",
        "fix_next": "Fix",
        "not_proven_not_tested": "Prove",
        "passed_keep": "Keep",
    }.get(section, "Prove")

def proof_label(f):
    f = f or {}
    raw = norm_token(f.get("proof") or f.get("evidence_grade") or f.get("confidence"))
    if not raw:
        return "Not tested"
    return PROOF_ALIAS.get(raw, title_case(raw))

def seg_html(segments):
    total = sum(max(num((s or {}).get("value", 0)), 0) for s in segments) or 1
    out = []
    for s in segments:
        kind = cov_kind((s or {}).get("kind"))
        c = COV.get(kind, "#334155")
        v = max(num((s or {}).get("value", 0)), 0)
        pct = max((v / total) * 100, 0)
        label = cov_label(s)
        title = esc(f"{label} — {(s or {}).get('value','')}")
        out.append(f'<span style="flex:0 0 {pct:.1f}%;background:{c}" aria-hidden="true" title="{title}"></span>')
    return "".join(out)

def legend_html(segments):
    out = []
    for s in segments:
        s = s or {}
        kind = cov_kind(s.get("kind"))
        c = COV.get(kind, "#334155")
        out.append(f'<span class="cov-key"><i class="sw" style="background:{c}"></i>'
                   f'{esc(cov_label(s))}&nbsp;<b>{esc(s.get("value", ""))}</b></span>')
    return "".join(out)

def details_html(f):
    rows = []
    for k in ("evidence", "fix", "verify"):
        if f.get(k):
            cls = "mono" if k == "evidence" else "prose"
            rows.append(f'<div class="ev-row"><div class="ev-label">{k}</div>'
                        f'<p class="ev-value {cls}">{esc(f[k])}</p></div>')
    if not rows:
        return ""
    return ('<details><summary>Evidence · Fix · Verify</summary>'
            f'<div class="ev-block">{"".join(rows)}</div></details>')

def finding_html(f, idx):
    f = f or {}
    section = section_key(f)
    accent, _, _ = SECTION.get(section, SECTION["not_proven_not_tested"])
    action = action_label(f, section)
    proof = proof_label(f)
    action_chip = f'<span class="pill pill-action" style="color:{accent};border-color:{accent}66">{esc(action)}</span>'
    proof_chip = f'<span class="pill pill-proof">{esc(proof)}</span>'
    parts = [f'<article class="finding" data-section="{section}" style="border-left-color:{accent}">',
             f'<div class="finding-top c-head"><span class="finding-num">{idx:02d}</span>{action_chip}{proof_chip}</div>',
             f'<h3>{esc(f.get("title","(untitled finding)"))}</h3>']
    if f.get("consequence"):
        parts.append(f'<p class="consequence"><span class="arrow">↳</span>{esc(f["consequence"])}</p>')
    parts.append(details_html(f))
    parts.append("</article>")
    return "".join(parts)

def render(data, interactive=False):
    if not isinstance(data, dict): data = {}
    target = esc(data.get("target", "target"))
    gen = esc(data.get("generated_at") or datetime.date.today().isoformat())

    verdict = str(data.get("verdict", "NOT READY")).upper()
    verdict_label = title_case(verdict)
    vbg, vbd, vtx = VERDICT.get(verdict, VERDICT_NEUTRAL)

    findings = data.get("findings", [])
    if not isinstance(findings, list): findings = []
    findings = [f for f in findings if isinstance(f, dict)]
    findings.sort(key=lambda f: (SECTION_ORDER.index(section_key(f)), sev_key(f.get("severity")), str(f.get("title", ""))))

    # summary: prefer new action-first summary fields; otherwise derive from findings.
    s = data.get("summary") if isinstance(data.get("summary"), dict) else None
    if s and any(k in s for k in ("clear_before_ship", "clear", "fix_next", "not_proven_not_tested", "not_proven", "passed_keep", "passed")):
        clear = s.get("clear_before_ship", s.get("clear", 0))
        fix_next = s.get("fix_next", 0)
        not_proven = s.get("not_proven_not_tested", s.get("not_proven", 0))
        passed_keep = s.get("passed_keep", s.get("passed", 0))
    else:
        from collections import Counter
        c = Counter(section_key(f) for f in findings)
        clear = c.get("clear_before_ship", 0)
        fix_next = c.get("fix_next", 0)
        not_proven = c.get("not_proven_not_tested", 0)
        passed_keep = c.get("passed_keep", 0)

    cov = data.get("coverage") if isinstance(data.get("coverage"), dict) else {}
    segs = cov.get("segments", [])
    if not isinstance(segs, list): segs = []
    segs = [s for s in segs if isinstance(s, dict)]

    if segs:
        covered = sum(num(s.get("value")) for s in segs if cov_kind(s.get("kind")) == "covered")
        total = num(cov.get("total_paths"), 0)
        if total <= 0:
            total = sum(num(s.get("value")) for s in segs)
        pct = round(100 * covered / total) if total > 0 else 0
        cov_sum = (f'<p class="cov-line"><strong>{pct}%</strong>&nbsp; covered · '
                   f'{covered:g} of {total:g} discovered paths</p>') if total > 0 else ''
        aria = "Coverage breakdown" + (f" of {total:g} discovered paths: " if total > 0 else ": ")
        aria += ", ".join(f'{num(s.get("value")):g} {cov_label(s)}' for s in segs)
        cov_block = (f'<section class="section"><div class="section-head"><h2>Coverage</h2></div>{cov_sum}'
                     f'<div class="cov-bar" role="img" aria-label="{esc(aria)}">{seg_html(segs)}</div>'
                     f'<div class="cov-legend">{legend_html(segs)}</div></section>')
    else:
        cov_block = ('<section class="section"><div class="section-head"><h2>Coverage</h2></div>'
                     '<div class="muted-note">Coverage not recorded for this run.</div></section>')

    if findings:
        buckets = {section: [] for section in SECTION_ORDER}
        for f in findings:
            buckets[section_key(f)].append(f)
        parts = ['<div class="group-label">Findings</div>']
        for section in SECTION_ORDER:
            b = buckets[section]
            if not b:
                continue
            accent, label, tier = SECTION[section]
            parts.append(f'<section class="section {tier}">'
                         f'<div class="section-head"><h2>{label}</h2><span class="count">{len(b)}</span></div>')
            parts.extend(finding_html(f, i) for i, f in enumerate(b, 1))
            parts.append('</section>')
        find_block = "".join(parts)
    else:
        find_block = ('<section class="section"><div class="section-head"><h2>Findings</h2></div>'
                      '<article class="finding" style="border-left-color:#34D399">'
                      '<h3>No blocking or open findings were recorded.</h3></article></section>')

    ck = data.get("checkpoint") if isinstance(data.get("checkpoint"), dict) else {}
    ck_rows = []
    if isinstance(ck.get("lanes"), list) and ck["lanes"]: ck_rows.append(("lanes", " · ".join(str(x) for x in ck["lanes"])))
    if ck.get("goal_mode_status") or data.get("goal_mode_status"):
        ck_rows.append(("goal mode status", ck.get("goal_mode_status") or data.get("goal_mode_status")))
    if ck.get("goal_mode_objective") or data.get("goal_mode_objective"):
        ck_rows.append(("goal mode objective", ck.get("goal_mode_objective") or data.get("goal_mode_objective")))
    auth = ck.get("multi_agent_authorization") or ck.get("authorization")
    if auth: ck_rows.append(("authorization", auth))
    if "frontend_path_walk_performed" in ck:
        ck_rows.append(("frontend path-walk", "yes" if ck.get("frontend_path_walk_performed") else "no"))
    if ck.get("frontend_tool"): ck_rows.append(("frontend tool", ck["frontend_tool"]))
    if ck.get("runtime_target"): ck_rows.append(("runtime target", ck["runtime_target"]))
    if ck.get("path_walk_status"): ck_rows.append(("path walk status", ck["path_walk_status"]))
    if ck.get("downgrade_reason"): ck_rows.append(("downgrade reason", ck["downgrade_reason"]))
    if ck.get("report_generation_status") or data.get("report_generation_status"):
        ck_rows.append(("report generation", ck.get("report_generation_status") or data.get("report_generation_status")))
    if ck.get("report_path") or data.get("report_path"):
        ck_rows.append(("report path", ck.get("report_path") or data.get("report_path")))
    if ck.get("ledger_path") or data.get("ledger_path"):
        ck_rows.append(("ledger path", ck.get("ledger_path") or data.get("ledger_path")))
    evidence_locations = ck.get("evidence_locations") or data.get("evidence_locations")
    if evidence_locations:
        ck_rows.append(("evidence locations", row_text(evidence_locations)))
    frontier_fields = [
        ("frontier total", "frontier_total"),
        ("frontier covered", "frontier_covered"),
        ("frontier sampled", "frontier_sampled"),
        ("frontier blocked", "frontier_blocked"),
        ("frontier missing", "frontier_missing"),
        ("frontier evidence debt", "frontier_evidence_debt"),
        ("frontier unattempted", "frontier_unattempted"),
        ("new paths last wave", "new_paths_last_wave"),
        ("new paths previous wave", "new_paths_previous_wave"),
        ("exhaustion status", "exhaustion_status"),
        ("exhaustion downgrade reason", "exhaustion_downgrade_reason"),
        ("next frontier batch", "next_frontier_batch"),
    ]
    for label, key in frontier_fields:
        value = ck.get(key, data.get(key))
        if value not in (None, "", []):
            ck_rows.append((label, row_text(value)))
    if ck.get("mode"):     ck_rows.append(("mode", ck["mode"]))
    if ck.get("verifier"): ck_rows.append(("verifier", ck["verifier"]))
    if isinstance(ck.get("omitted"), list):
        for o in ck["omitted"]: ck_rows.append(("omitted", o))
    ck_html = ("".join(f'<div class="orch-row"><div class="orch-label">{esc(k)}</div>'
                       f'<div class="orch-value">{esc(v)}</div></div>'
                       for k, v in ck_rows)
               or '<div class="muted-note">No orchestration checkpoint recorded.</div>')

    illus = ('<div class="illus">Illustrative example — the report format is real; '
             'the contents are a sample, not a live run.</div>') if data.get("illustrative") else ""

    # optional, opt-in client-side interactivity (no external deps, no network)
    controls = ""
    script = ""
    controls_css = ""
    if interactive:
        controls_css = (
            "  .controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 12px}\n"
            "  .fbtn{background:#101E36;border:1px solid #243350;border-radius:16px;padding:4px 12px;"
            "font-size:12.5px;color:#8B9AB8;cursor:pointer;font-family:inherit}\n"
            "  .fbtn:not(.on){opacity:.4}\n"
            "  .search{flex:1;min-width:160px;background:#101E36;border:1px solid #243350;border-radius:16px;"
            "padding:5px 12px;color:#D7DEEC;font-size:12.5px;font-family:inherit}\n"
            "  .search::placeholder{color:#5F6E90}\n"
            "  .is-hidden{display:none}\n"
            "  .finding[data-section] .c-head{cursor:pointer}\n"
            "  .finding.collapsed .consequence,.finding.collapsed details{display:none}\n")

        sections_present = []
        for section in SECTION_ORDER:
            if any(section_key(f) == section for f in findings):
                sections_present.append(section)
        btns = "".join(
            f'<button type="button" class="fbtn on" data-section="{section}" '
            f'style="border-color:{SECTION[section][0]}66;color:{SECTION[section][0]}">{SECTION[section][1]}</button>'
            for section in sections_present)
        controls = (f'<div class="controls">{btns}'
                    f'<input class="search" type="search" placeholder="Filter findings\u2026" aria-label="Filter findings">'
                    f'<button type="button" class="fbtn" id="collapseAll">Collapse all</button></div>')
        script = ("<script>(function(){"
                  "var on={};document.querySelectorAll('.fbtn[data-section]').forEach(function(b){on[b.dataset.section]=true;"
                  "b.addEventListener('click',function(){on[b.dataset.section]=!on[b.dataset.section];"
                  "b.classList.toggle('on');apply();});});"
                  "var q='';var si=document.querySelector('.search');"
                  "if(si){si.addEventListener('input',function(){q=si.value.toLowerCase();apply();});}"
                  "document.querySelectorAll('.c-head').forEach(function(h){h.addEventListener('click',function(e){"
                  "if(e.target.tagName==='A')return;h.closest('.finding').classList.toggle('collapsed');});});"
                  "var ca=document.getElementById('collapseAll');if(ca){ca.addEventListener('click',function(){"
                  "var cards=document.querySelectorAll('.finding[data-section]');"
                  "var anyOpen=[].some.call(cards,function(c){return !c.classList.contains('collapsed');});"
                  "cards.forEach(function(c){c.classList.toggle('collapsed',anyOpen);});"
                  "ca.textContent=anyOpen?'Expand all':'Collapse all';});}"
                  "function apply(){document.querySelectorAll('.finding[data-section]').forEach(function(c){"
                  "var okS=on[c.dataset.section];var okQ=!q||c.textContent.toLowerCase().indexOf(q)>-1;"
                  "c.classList.toggle('is-hidden',!(okS&&okQ));});"
                  "document.querySelectorAll('.section[class*=tier-]').forEach(function(s){"
                  "var vis=[].some.call(s.querySelectorAll('.finding'),function(c){return !c.classList.contains('is-hidden');});"
                  "s.classList.toggle('is-hidden',!vis);});}"
                  "})();</script>")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Shipworthy Readiness Report — {target}</title>
<style>
  :root{{color-scheme:dark;--void:#0A1526;--panel:#101E36;--panel-raised:#16283F;--hairline:#243350;--hairline-soft:#1B2A44;--paper:#EDF1F8;--prose:#D7DEEC;--muted:#8B9AB8;--muted-dim:#647089;--radius:14px}}
  *{{box-sizing:border-box}}
  html{{background:var(--void)}}
  body{{margin:0;background:radial-gradient(ellipse 900px 460px at 50% -8%,#142644 0%,transparent 60%),var(--void);color:var(--paper);
    font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    line-height:1.5;-webkit-font-smoothing:antialiased;overflow-wrap:anywhere}}
  code,.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace}}
  .page{{max-width:740px;margin:0 auto;padding:34px 20px 72px}}
  .masthead{{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}}
  .brand{{font-weight:700;font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:{vtx}}}
  .badge-readonly{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:10.5px;letter-spacing:.04em;color:var(--muted);border:1px solid var(--hairline);padding:4px 10px;border-radius:999px;text-transform:uppercase;white-space:nowrap}}
  h1.title{{font-family:Georgia,serif;font-weight:600;font-size:clamp(28px,6.4vw,36px);margin:10px 0 6px;color:var(--paper);letter-spacing:0}}
  .meta-line{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px;color:var(--muted);margin:0 0 8px}}
  .meta-line .sep{{color:var(--hairline-soft);margin:0 7px}}
  .verdict-zone{{display:flex;flex-direction:column;align-items:center;text-align:center;margin:40px 0 12px}}
  .stamp{{position:relative;display:inline-block;transform:rotate(-4deg);border:3px solid {vtx};border-radius:8px;padding:14px 30px 12px;margin-bottom:22px}}
  .stamp::before{{content:"";position:absolute;inset:4px;border:1px solid {vtx};border-radius:4px;opacity:.55;pointer-events:none}}
  .stamp-text{{display:block;font-family:Georgia,serif;font-weight:900;font-size:clamp(30px,8vw,42px);letter-spacing:.03em;color:{vtx};text-transform:none;line-height:1}}
  .stamp-sub{{display:block;margin-top:5px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:9.5px;letter-spacing:.18em;text-transform:uppercase;color:{vbd}}}
  .epigraph{{font-family:Georgia,serif;font-style:italic;font-weight:500;font-size:16px;color:var(--muted);max-width:400px;margin:0 0 26px}}
  .stats-row{{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}}
  .stat-chip{{display:flex;align-items:baseline;gap:8px;border:1px solid var(--hairline);background:var(--panel);border-radius:10px;padding:9px 16px}}
  .stat-chip .n{{font-family:Georgia,serif;font-weight:700;font-size:20px;line-height:1}}
  .stat-chip .l{{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.07em;color:var(--muted)}}
  .c-clear .n{{color:{SECTION['clear_before_ship'][0]}}}.c-fixnext .n{{color:{SECTION['fix_next'][0]}}}.c-notproven .n{{color:{SECTION['not_proven_not_tested'][0]}}}.c-passed .n{{color:{SECTION['passed_keep'][0]}}}
  .read-key{{max-width:660px;margin:18px auto 0;color:var(--muted);font-size:13px;line-height:1.65;text-align:left;border:1px solid var(--hairline-soft);background:#0D1A30;border-radius:10px;padding:12px 14px}}
  .read-key b{{color:var(--paper)}}.key-actions{{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}}.key-chip{{font-weight:700;font-size:10px;letter-spacing:.06em;text-transform:uppercase;padding:2px 8px;border-radius:999px;border:1px solid var(--hairline);color:var(--paper)}}
  .section{{margin-top:56px}}
  .section-head{{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin-bottom:18px;padding-bottom:11px;border-bottom:1px solid var(--hairline)}}
  .section-head h2{{font-weight:700;font-size:13px;letter-spacing:.14em;text-transform:uppercase;margin:0;color:var(--paper)}}
  .section-head .count{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;color:var(--muted-dim)}}
  .group-label{{margin-top:56px;margin-bottom:-30px;font-weight:700;font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:var(--muted-dim)}}
  .tier-clear-before-ship .section-head h2{{color:{SECTION['clear_before_ship'][0]}}}.tier-fix-next .section-head h2{{color:{SECTION['fix_next'][0]}}}.tier-not-proven .section-head h2{{color:{SECTION['not_proven_not_tested'][0]}}}.tier-passed-keep .section-head h2{{color:{SECTION['passed_keep'][0]}}}
  .cov-line{{font-size:14.5px;color:var(--prose);margin:0 0 16px}}.cov-line strong{{font-family:Georgia,serif;font-weight:700;font-size:21px;color:var(--paper)}}
  .cov-bar{{display:flex;width:100%;height:14px;border-radius:7px;overflow:hidden;background:var(--panel-raised);border:1px solid var(--hairline);margin-bottom:18px}}
  .cov-bar span{{height:100%;display:block}}
  .cov-legend{{display:flex;flex-wrap:wrap;gap:9px 20px}}.cov-key{{display:flex;align-items:center;gap:7px;font-size:12.5px;color:var(--muted)}}.cov-key .sw{{width:9px;height:9px;border-radius:2px;flex:none}}.cov-key b{{color:var(--paper);font-weight:700;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
  .muted-note{{color:var(--muted);font-size:13px;font-style:italic;margin-bottom:6px}}
  .finding{{background:var(--panel);border:1px solid var(--hairline);border-left:4px solid var(--hairline);border-radius:var(--radius);padding:19px 21px;margin-bottom:14px;overflow-wrap:anywhere}}
  .finding-top{{display:flex;align-items:center;gap:10px;margin-bottom:9px;flex-wrap:wrap}}.finding-num{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;color:var(--muted-dim)}}
  .pill{{font-weight:700;font-size:10px;letter-spacing:.06em;text-transform:uppercase;padding:3px 9px;border-radius:999px;border:1px solid;white-space:nowrap}}.pill-proof{{color:var(--muted);border-color:var(--hairline)}}
  .finding h3{{font-weight:600;font-size:16.5px;line-height:1.35;margin:0 0 9px;color:var(--paper)}}.consequence{{font-family:Georgia,serif;font-style:italic;font-size:14px;line-height:1.5;color:var(--muted);margin:0}}.consequence .arrow{{font-style:normal;color:var(--muted-dim);margin-right:7px}}
  details{{margin-top:12px}}summary{{cursor:pointer;list-style:none;display:inline-flex;align-items:center;gap:6px;font-weight:700;font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:{vtx};padding:6px 2px;user-select:none;border-radius:4px}}summary::-webkit-details-marker{{display:none}}summary::before{{content:"›";display:inline-block;font-size:16px;line-height:1;transition:transform .15s ease}}details[open] summary::before{{transform:rotate(90deg)}}summary:focus-visible{{outline:2px solid {vtx};outline-offset:3px}}
  .ev-block{{margin-top:6px;padding-top:6px}}.ev-row{{margin-bottom:13px}}.ev-row:last-child{{margin-bottom:0}}.ev-label{{font-weight:700;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted-dim);margin-bottom:5px}}.ev-value{{margin:0}}.ev-value.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.2px;line-height:1.65;color:var(--prose);background:var(--panel-raised);border:1px solid var(--hairline-soft);border-radius:8px;padding:11px 13px}}.ev-value.prose{{font-size:13.8px;line-height:1.6;color:var(--prose)}}
  .orch{{background:var(--panel);border:1px solid var(--hairline);border-radius:var(--radius);padding:6px 22px}}.orch-row{{display:grid;grid-template-columns:118px 1fr;gap:16px;padding:15px 0;border-bottom:1px solid var(--hairline-soft)}}.orch-row:last-child{{border-bottom:none}}.orch-label{{font-weight:700;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted-dim);padding-top:1px}}.orch-value{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.3px;line-height:1.65;color:var(--prose)}}
  footer{{margin-top:60px;padding-top:26px;border-top:1px solid var(--hairline);color:var(--muted-dim);font-size:12px;line-height:1.7}}.illus{{margin-top:10px;color:var(--muted-dim);font-size:12px}}
{controls_css}  a{{color:#34D399}}
  @media print{{
    .controls{{display:none !important}}
    .is-hidden{{display:block !important}}
    .finding.collapsed .consequence,.finding.collapsed details{{display:block !important}}
    body{{background:#fff;color:#0B1220}}
    .page{{max-width:none;padding:0}}
    footer,.section-head{{border-color:#ccd3df}}
    .brand{{color:#0B1220}} .brand .g{{color:#0B8A5B}}
    .meta-line,.muted-note,.cov-line,.cov-key,.illus,.consequence{{color:#4A5568}}
    .cov-line strong,.finding h3,.ev-value.mono,.ev-value.prose,.orch-value{{color:#111}}
    .ev-label,.orch-label{{color:#556}}
    .finding,.orch{{background:#fff;border-color:#ccd3df;break-inside:avoid;page-break-inside:avoid}}
    .pill,.key-chip{{color:#111 !important;border-color:#bbb !important}}
    footer{{color:#555}} a{{color:#0B1220}}
  }}
  @media (max-width:460px){{.orch-row{{grid-template-columns:1fr;gap:5px;padding:13px 0}}}}
  @media (prefers-reduced-motion:reduce){{summary::before{{transition:none}}}}
</style></head>
<body><div class="page">
  <header>
    <div class="masthead"><span class="brand">Shipworthy</span><span class="badge-readonly">Read-only</span></div>
    <h1 class="title">Readiness Report</h1>
    <p class="meta-line">{target}<span class="sep">·</span>{gen}</p>
  </header>
  <section class="verdict-zone">
    <div class="stamp"><span class="stamp-text">{esc(verdict_label)}</span><span class="stamp-sub">Status · Evidence gated</span></div>
    <p class="epigraph">&ldquo;nothing is called &lsquo;ready&rsquo; without evidence&rdquo;</p>
    <div class="stats-row">
      <div class="stat-chip c-clear"><span class="n">{esc(clear)}</span><span class="l">Required Fixes</span></div>
      <div class="stat-chip c-fixnext"><span class="n">{esc(fix_next)}</span><span class="l">Fix Next</span></div>
      <div class="stat-chip c-notproven"><span class="n">{esc(not_proven)}</span><span class="l">Not Proven</span></div>
      <div class="stat-chip c-passed"><span class="n">{esc(passed_keep)}</span><span class="l">Passed</span></div>
    </div>
    <p class="read-key"><b>Read this by action:</b> Clear Before Ship items block readiness. Fix Next items are real but non-blocking. Not Proven / Not Tested items are not passes. Passed / Keep items worked under the tested conditions. Each card says what to do and how strong the proof is.<span class="key-actions"><span class="key-chip">Fix</span><span class="key-chip">Prove</span><span class="key-chip">Decide</span><span class="key-chip">Skip</span><span class="key-chip">Keep</span></span></p>
  </section>
  {cov_block}
  {controls}
  {find_block}
  <section class="section"><div class="section-head"><h2>Orchestration Checkpoint</h2></div><div class="orch">{ck_html}</div></section>
  <footer>
    <b style="color:#7E8CAD">Proof labels:</b> Confirmed (directly observed) &gt; Partial (some proof, incomplete coverage) &gt; Inferred (not directly observed) &gt; Not tested.
    Findings lead; scores never appear naked. Read-only by default — fixes are proposed with a verification step, not applied.
    {illus}
  </footer>
{script}
</div></body></html>"""

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    interactive = "--interactive" in sys.argv[1:]
    inp = args[0] if len(args) > 0 else "sample-report.json"
    out = args[1] if len(args) > 1 else "readiness-report.html"
    try:
        with open(inp, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print(f"error: input file not found: {inp}", file=sys.stderr); sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"error: {inp} is not valid JSON ({e})", file=sys.stderr); sys.exit(1)
    html_out = render(data, interactive=interactive)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html_out)
    print(f"wrote {out} ({len(html_out)} bytes) from {inp}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Shipworthy — render a structured readiness audit into a self-contained HTML report.

Usage:
    python3 render_report.py [input.json] [output.html]

Produces ONE self-contained file: inline CSS, system fonts, no network calls, no
JavaScript. Renders identically in modern browsers, wkhtmltopdf, and print. Every
text field is HTML-escaped; the renderer degrades gracefully on partial/degenerate
data instead of crashing.
"""
import sys, json, html, datetime

COV = {
    "covered": "#34D399", "sampled": "#3B82F6", "blocked": "#F59E0B",
    "avoided": "#9F5B6B", "missing": "#F43F5E", "debt": "#3A4763",
}
SEV = {
    "blocker":     ("#F43F5E", "Blocker"),
    "strong":      ("#F59E0B", "Strong"),
    "provisional": ("#38BDF8", "Provisional"),
    "info":        ("#64748B", "Note"),
}
SEV_ORDER = ["blocker", "strong", "provisional", "info"]
GRP_LABEL = {"blocker": "Blockers", "strong": "Strong signals",
             "provisional": "Provisional", "info": "Notes"}
VERDICT = {
    "NOT READY":        ("#2A1220", "#7F2740", "#FB7185"),
    "READY WITH RISKS": ("#241A05", "#7A5A16", "#FBBF24"),
    "CONDITIONAL":      ("#241A05", "#7A5A16", "#FBBF24"),
    "READY":            ("#0B241A", "#1E6B4E", "#34D399"),
}
VERDICT_NEUTRAL = ("#141A28", "#2A3654", "#AEBAD4")  # unknown verdict -> neutral, not alarming

def esc(x): return html.escape("" if x is None else str(x))

def num(x, default=0.0):
    try:
        v = float(x); return v if v == v else default   # reject NaN
    except (TypeError, ValueError):
        return default

def seg_html(segments):
    n = len(segments); out = []
    for i, s in enumerate(segments):
        c = COV.get((s or {}).get("kind", ""), "#334155")
        v = max(num((s or {}).get("value", 0)), 0.0001)
        mr = "" if i == n - 1 else "margin-right:3px;"
        lbl = esc(f'{(s or {}).get("label", (s or {}).get("kind","")) }: {(s or {}).get("value","")}')
        out.append(f'<div title="{lbl}" style="flex:{v:g} 1 0;{mr}background:{c};height:16px;border-radius:3px"></div>')
    return "".join(out)

def legend_html(segments):
    out = []
    for s in segments:
        s = s or {}
        c = COV.get(s.get("kind", ""), "#334155")
        out.append(f'<span class="chip"><i style="background:{c}"></i>'
                   f'{esc(s.get("label", s.get("kind", "")))} {esc(s.get("value", ""))}</span>')
    return "".join(out)

def finding_html(f):
    f = f or {}
    sev = f.get("severity", "info")
    accent, sev_label = SEV.get(sev, SEV["info"])
    conf = str(f.get("confidence") or "").strip()
    # Severity is already carried by the group header + the card's colored border,
    # so show a confidence chip ONLY when it adds information (differs from severity).
    chip = ""
    if conf and conf.lower() not in (sev_label.lower(), str(sev).lower()):
        chip = f'<span class="badge" style="color:{accent};border-color:{accent}44">{esc(conf.capitalize())}</span>'
    parts = [f'<div class="card" data-sev="{sev}" style="border-left-color:{accent}">',
             f'<div class="c-head">{chip}<span class="c-title">{esc(f.get("title","(untitled finding)"))}</span></div>']
    if f.get("consequence"):
        parts.append(f'<div class="conseq">↳ {esc(f["consequence"])}</div>')
    for k in ("evidence", "fix", "verify"):
        if f.get(k):
            parts.append(f'<div class="kv"><span class="k">{k}</span><code>{esc(f[k])}</code></div>')
    parts.append("</div>")
    return "".join(parts)

def render(data, interactive=False):
    if not isinstance(data, dict): data = {}
    target = esc(data.get("target", "target"))
    gen = esc(data.get("generated_at") or datetime.date.today().isoformat())

    verdict = str(data.get("verdict", "NOT READY")).upper()
    vbg, vbd, vtx = VERDICT.get(verdict, VERDICT_NEUTRAL)

    findings = data.get("findings", [])
    if not isinstance(findings, list): findings = []
    findings = [f for f in findings if isinstance(f, dict)]
    findings.sort(key=lambda f: SEV_ORDER.index(f.get("severity"))
                  if f.get("severity") in SEV_ORDER else 99)

    # summary: use provided, else derive from findings
    s = data.get("summary") if isinstance(data.get("summary"), dict) else None
    if s is None:
        from collections import Counter
        c = Counter(f.get("severity", "info") for f in findings)
        s = {"blockers": c.get("blocker", 0), "strong": c.get("strong", 0),
             "provisional": c.get("provisional", 0)}
    summ = f'{s.get("blockers",0)} blockers · {s.get("strong",0)} strong · {s.get("provisional",0)} provisional'

    cov = data.get("coverage") if isinstance(data.get("coverage"), dict) else {}
    segs = cov.get("segments", [])
    if not isinstance(segs, list): segs = []
    segs = [s for s in segs if isinstance(s, dict)]

    if segs:
        covered = sum(num(s.get("value")) for s in segs if s.get("kind") == "covered")
        total = num(cov.get("total_paths"), 0)
        if total <= 0:
            total = sum(num(s.get("value")) for s in segs)
        cov_sum = (f'<div class="cov-sum"><b>{round(100*covered/total)}%</b> covered · '
                   f'{covered:g} of {total:g} discovered paths</div>') if total > 0 else ''
        aria = "coverage: " + ", ".join(
            f'{num(s.get("value")):g} {(s.get("label") or s.get("kind") or "")}' for s in segs)
        cov_block = (f'<div class="lbl">COVERAGE</div>{cov_sum}'
                     f'<div class="bar" role="img" aria-label="{esc(aria)}">{seg_html(segs)}</div>'
                     f'<div class="legend">{legend_html(segs)}</div>')
    else:
        cov_block = '<div class="lbl">COVERAGE</div><div class="muted-note">Coverage not recorded for this run.</div>'

    if findings:
        buckets = {sev: [] for sev in SEV_ORDER}
        for f in findings:
            buckets[f.get("severity") if f.get("severity") in SEV_ORDER else "info"].append(f)
        parts = []
        for sev in SEV_ORDER:
            b = buckets[sev]
            if not b:
                continue
            accent = SEV[sev][0]
            parts.append(f'<div class="grp"><span class="grp-dot" style="background:{accent}"></span>'
                         f'{GRP_LABEL[sev]}<span class="grp-n">{len(b)}</span></div>')
            parts.extend(finding_html(f) for f in b)
        find_block = "".join(parts)
    else:
        find_block = ('<div class="card" style="border-left-color:#34D399">'
                      '<div class="c-head"><span class="dot" style="background:#34D399"></span>'
                      '<span class="c-title">No blocking or open findings were recorded.</span></div></div>')

    ck = data.get("checkpoint") if isinstance(data.get("checkpoint"), dict) else {}
    ck_rows = []
    if isinstance(ck.get("lanes"), list) and ck["lanes"]: ck_rows.append(("lanes", " · ".join(str(x) for x in ck["lanes"])))
    if ck.get("mode"):     ck_rows.append(("mode", ck["mode"]))
    if ck.get("verifier"): ck_rows.append(("verifier", ck["verifier"]))
    if isinstance(ck.get("omitted"), list):
        for o in ck["omitted"]: ck_rows.append(("omitted", o))
    ck_html = ("".join(f'<div class="ck"><span class="k">{esc(k)}</span><code>{esc(v)}</code></div>'
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
            "  .fbtn{background:#0E1830;border:1px solid #2A3654;border-radius:16px;padding:4px 12px;"
            "font-size:12.5px;color:#9FB0CE;cursor:pointer;font-family:inherit}\n"
            "  .fbtn:not(.on){opacity:.4}\n"
            "  .search{flex:1;min-width:160px;background:#0C1220;border:1px solid #2A3654;border-radius:16px;"
            "padding:5px 12px;color:#C7D2E6;font-size:12.5px;font-family:inherit}\n"
            "  .search::placeholder{color:#5F6E90}\n"
            "  .is-hidden{display:none}\n"
            "  .card[data-sev] .c-head{cursor:pointer}\n"
            "  .card.collapsed .conseq,.card.collapsed .kv{display:none}\n")

        sev_present = []
        for sev in SEV_ORDER:
            if any((f.get("severity") if f.get("severity") in SEV_ORDER else "info") == sev for f in findings):
                sev_present.append(sev)
        btns = "".join(
            f'<button type="button" class="fbtn on" data-sev="{sev}" '
            f'style="border-color:{SEV[sev][0]}66;color:{SEV[sev][0]}">{GRP_LABEL[sev]}</button>'
            for sev in sev_present)
        controls = (f'<div class="controls">{btns}'
                    f'<input class="search" type="search" placeholder="Filter findings\u2026" aria-label="Filter findings">'
                    f'<button type="button" class="fbtn" id="collapseAll">Collapse all</button></div>')
        script = ("<script>(function(){"
                  "var on={};document.querySelectorAll('.fbtn[data-sev]').forEach(function(b){on[b.dataset.sev]=true;"
                  "b.addEventListener('click',function(){on[b.dataset.sev]=!on[b.dataset.sev];"
                  "b.classList.toggle('on');apply();});});"
                  "var q='';var si=document.querySelector('.search');"
                  "if(si){si.addEventListener('input',function(){q=si.value.toLowerCase();apply();});}"
                  "document.querySelectorAll('.c-head').forEach(function(h){h.addEventListener('click',function(e){"
                  "if(e.target.tagName==='A')return;h.parentNode.classList.toggle('collapsed');});});"
                  "var ca=document.getElementById('collapseAll');if(ca){ca.addEventListener('click',function(){"
                  "var cards=document.querySelectorAll('.card[data-sev]');"
                  "var anyOpen=[].some.call(cards,function(c){return !c.classList.contains('collapsed');});"
                  "cards.forEach(function(c){c.classList.toggle('collapsed',anyOpen);});"
                  "ca.textContent=anyOpen?'Expand all':'Collapse all';});}"
                  "function apply(){document.querySelectorAll('.card[data-sev]').forEach(function(c){"
                  "var okS=on[c.dataset.sev];var okQ=!q||c.textContent.toLowerCase().indexOf(q)>-1;"
                  "c.classList.toggle('is-hidden',!(okS&&okQ));});"
                  "document.querySelectorAll('.grp').forEach(function(g){var n=g.nextElementSibling,vis=false;"
                  "while(n&&n.classList.contains('card')){if(!n.classList.contains('is-hidden'))vis=true;n=n.nextElementSibling;}"
                  "g.classList.toggle('is-hidden',!vis);});}"
                  "})();</script>")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Shipworthy Readiness Report — {target}</title>
<style>
  :root{{color-scheme:dark}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:#080B14;color:#C7D2E6;
    font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    -webkit-font-smoothing:antialiased;overflow-wrap:anywhere}}
  code,.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace}}
  .page{{max-width:920px;margin:0 auto;padding:34px 26px 56px}}
  .hdr{{display:flex;justify-content:space-between;align-items:center;
    padding-bottom:16px;border-bottom:1px solid #1A2438;flex-wrap:wrap;gap:8px}}
  .brand{{font-size:22px;font-weight:800;letter-spacing:-.5px;color:#E8EEF7}}
  .brand .g{{color:#34D399}}
  .brand .sub{{font-size:14px;font-weight:600;color:#6E7EA0;letter-spacing:0;margin-left:6px}}
  .meta{{font-family:ui-monospace,Menlo,monospace;font-size:12.5px;color:#7C8AAA}}
  .ro{{display:inline-block;border:1px solid #26355A;border-radius:11px;padding:2px 9px;color:#9FB0CE;font-size:11.5px}}
  .lbl{{font-size:12px;font-weight:700;letter-spacing:2px;color:#8492B2;margin:26px 0 8px}}
  .muted-note{{color:#7E8CAD;font-size:13px;font-style:italic;margin-bottom:6px}}
  .cov-sum{{font-size:13px;color:#9DAAC8;margin:-2px 0 8px}}
  .cov-sum b{{color:#E2E8F3;font-size:15px}}
  .grp{{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:700;letter-spacing:1.2px;
    text-transform:uppercase;color:#B7C3DB;margin:16px 0 8px}}
  .grp-dot{{width:8px;height:8px;border-radius:50%;flex:none}}
  .grp-n{{background:#141B2C;border:1px solid #26314C;border-radius:20px;padding:0 8px;
    font-size:11px;color:#93A2C1;letter-spacing:0}}
  .verdict{{display:flex;align-items:center;gap:20px;margin-top:22px;flex-wrap:wrap}}
  .v-pill{{font-size:23px;font-weight:800;letter-spacing:.5px;padding:11px 20px;border-radius:12px;
    background:{vbg};border:1px solid {vbd};color:{vtx};white-space:nowrap}}
  .v-sum{{font-size:15px;color:#AEBAD4}}
  .v-sum .muted{{color:#7E8CAD;font-size:12.5px}}
  .bar{{display:flex;width:100%;margin:2px 0 12px}}
  .legend{{display:flex;flex-wrap:wrap;gap:10px 18px}}
  .chip{{font-size:12.5px;color:#8D9BBB;white-space:nowrap}}
  .chip i{{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle}}
  .card{{background:#0E1424;border:1px solid #242F49;border-left:4px solid #64748B;border-radius:11px;
    padding:14px 16px;margin-bottom:12px}}
  .c-head{{display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
  .dot{{width:9px;height:9px;border-radius:50%;flex:none}}
  .badge{{font-size:12px;font-weight:700;border:1px solid;border-radius:20px;padding:2px 9px;white-space:nowrap}}
  .c-title{{font-size:15.5px;font-weight:700;color:#E6ECF7;overflow-wrap:anywhere}}
  .conseq{{color:#93A2C1;font-size:13px;margin:8px 0 2px 19px;overflow-wrap:anywhere}}
  .kv{{margin:7px 0 0 19px;font-size:13px;color:#AAB6D0;overflow-wrap:anywhere}}
  .kv .k{{display:inline-block;min-width:64px;color:#6E7EA0;font-weight:600;
    text-transform:uppercase;font-size:11px;letter-spacing:.6px;vertical-align:top}}
  .kv code{{font-size:12.5px;color:#93A6C6;overflow-wrap:anywhere}}
  .ckpt-box{{background:#0C1220;border:1px solid #1E2840;border-radius:11px;padding:14px 16px}}
  .ck{{margin:6px 0;font-size:12.5px;overflow-wrap:anywhere}}
  .ck .k{{display:inline-block;min-width:74px;color:#6E7EA0;font-weight:600;
    text-transform:uppercase;font-size:11px;letter-spacing:.6px;vertical-align:top}}
  .ck code{{color:#8494B6}}
  footer{{margin-top:26px;padding-top:16px;border-top:1px solid #1A2438;color:#77859F;font-size:12px;line-height:1.7}}
  .illus{{margin-top:10px;color:#6E7C9C;font-size:12px}}
{controls_css}  a{{color:#34D399}}
  @media print{{
    .controls{{display:none !important}}
    .is-hidden{{display:block !important}}
    .card.collapsed .conseq,.card.collapsed .kv{{display:block !important}}
    body{{background:#fff;color:#0B1220}}
    .page{{max-width:none;padding:0}}
    .hdr,footer{{border-color:#ccd3df}}
    .brand{{color:#0B1220}} .brand .g{{color:#0B8A5B}}
    .lbl,.grp{{color:#334155}} .meta,.muted,.muted-note,.cov-sum,.chip,.illus{{color:#4A5568}}
    .cov-sum b{{color:#111}}
    .c-title,.kv code,.ck code,.conseq{{color:#111}}
    .kv .k,.ck .k{{color:#556}}
    .card,.ckpt-box{{background:#fff;border-color:#ccd3df;break-inside:avoid;page-break-inside:avoid}}
    .badge{{color:#111 !important;border-color:#bbb !important}}
    .grp-n{{background:#eee;border-color:#ccc;color:#333}}
    footer{{color:#555}} a{{color:#0B1220}}
  }}
  @media (max-width:520px){{.v-pill{{font-size:20px;padding:9px 14px}} .brand{{font-size:19px}}}}
</style></head>
<body><div class="page">
  <div class="hdr">
    <div class="brand">Ship<span class="g">worthy</span><span class="sub">Readiness Report</span></div>
    <div class="meta">{target} · {gen} · <span class="ro">read-only</span></div>
  </div>
  <div class="verdict">
    <div class="v-pill">{esc(verdict)}</div>
    <div class="v-sum">{esc(summ)}<br><span class="muted">nothing is called &ldquo;ready&rdquo; without evidence</span></div>
  </div>
  {cov_block}
  <div class="lbl">FINDINGS</div>
  {controls}
  {find_block}
  <div class="lbl">ORCHESTRATION CHECKPOINT</div>
  <div class="ckpt-box">{ck_html}</div>
  <footer>
    <b style="color:#7E8CAD">Evidence grades:</b> Confirmed (reproduced) &gt; Strong (multiple signals) &gt; Provisional (single signal) &gt; Inferred.
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

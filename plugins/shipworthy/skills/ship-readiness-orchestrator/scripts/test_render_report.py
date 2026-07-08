#!/usr/bin/env python3
import sys, re, json
from html.parser import HTMLParser
from render_report import render, VERDICT, VERDICT_NEUTRAL

VOID = {"meta","br","img","input","hr","link","area","base","col","embed","source","track","wbr"}
class WF(HTMLParser):
    def __init__(s): super().__init__(); s.stack=[]; s.err=[]
    def handle_starttag(s,t,a):
        if t not in VOID: s.stack.append(t)
    def handle_endtag(s,t):
        if t in VOID: return
        if not s.stack or s.stack[-1]!=t: s.err.append(f"mismatch </{t}> (open={s.stack[-3:]})")
        else: s.stack.pop()
def wellformed(h):
    p=WF(); p.feed(h)
    return (not p.stack and not p.err), (p.err + ([f"unclosed {p.stack}"] if p.stack else []))

def self_contained(h):
    hl=h.lower(); bad=[]
    if '<script' in hl: bad.append('script tag')
    if re.search(r'src\s*=\s*["\']?https?://', hl): bad.append('external src')
    if re.search(r'<link\b', hl): bad.append('link tag')
    if '@import' in hl: bad.append('@import')
    if re.search(r'url\(\s*["\']?https?://', hl): bad.append('css url()')
    return (not bad), bad
def cards(h): return h.count('class="finding"')
def stamp_color(h):
    m=re.search(r'\.stamp\{[^}]*border:3px solid (#[0-9A-Fa-f]{6})', h); return m.group(1) if m else None

PASS=[]; FAIL=[]
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{'' if cond else '  -> '+str(detail)}")

def base_ok(name, data, expect_cards=None, expect_verdict=None):
    try: h=render(data)
    except Exception as e:
        check(name+": no-crash", False, repr(e)); return None
    check(name+": no-crash", True)
    wf,errs=wellformed(h); check(name+": well-formed", wf, str(errs)[:120])
    sc,ext=self_contained(h); check(name+": self-contained", sc, str(ext)[:120])
    check(name+": has <html> & </html>", h.startswith("<!doctype html>") and h.rstrip().endswith("</html>"))
    check(name+": exactly one <style>", h.count("</style>")==1, f"count={h.count('</style>')}")
    if expect_cards is not None:
        check(name+f": {expect_cards} finding-cards", cards(h)==expect_cards, f"got {cards(h)}")
    if expect_verdict is not None:
        want=VERDICT.get(expect_verdict, VERDICT_NEUTRAL)[2]
        check(name+f": verdict stamp color {expect_verdict}", stamp_color(h)==want, f"got {stamp_color(h)} want {want}")
    return h

# ---- scenarios --------------------------------------------------------------
full = json.load(open(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)),"sample-report.json")))
base_ok("01 baseline NOT READY", full, expect_cards=6, expect_verdict="NOT READY")

ready = {"target":"clean-app","verdict":"READY","summary":{"blockers":0,"strong":0,"provisional":0},
         "coverage":{"total_paths":18,"segments":[{"kind":"covered","label":"covered","value":18}]},
         "findings":[], "checkpoint":{"lanes":["ship-deep-review"],"mode":"sequential","verifier":"Opus → APPROVED"}}
h=base_ok("02 READY clean (0 findings)", ready, expect_cards=1, expect_verdict="READY")
check("02: shows clean-note", "No blocking or open findings" in h)

base_ok("03 READY WITH RISKS", {**ready,"verdict":"READY WITH RISKS"}, expect_verdict="READY WITH RISKS")
base_ok("04 CONDITIONAL", {**ready,"verdict":"CONDITIONAL"}, expect_verdict="CONDITIONAL")
h=base_ok("05 unknown verdict -> neutral", {**ready,"verdict":"ship it maybe"}, expect_verdict="__unknown__")
check("05: neutral stamp used", stamp_color(h)==VERDICT_NEUTRAL[2], stamp_color(h))
check("05: verdict title-cased", ">Ship It Maybe<" in h)

h=base_ok("06 empty {}", {})
check("06: empty renders coverage note", "Coverage not recorded" in h)
check("06: empty renders findings note", "No blocking or open findings" in h)
check("06: empty renders checkpoint note", "No orchestration checkpoint" in h)

base_ok("07 findings title-only", {"findings":[{"title":"just a title"}]}, expect_cards=1)

h=base_ok("08 unknown severity -> info", {"findings":[{"severity":"cosmic","title":"weird sev"}]}, expect_cards=1)
check("08: info accent used", "#64748B" in h)

# 09 XSS across every text field
xss={"target":"<svg onload=alert(1)>","verdict":"NOT READY",
     "coverage":{"total_paths":"<b>x</b>","segments":[{"kind":"covered","label":"<i>lbl</i>","value":"<u>1</u>"}]},
     "findings":[{"severity":"blocker","confidence":"<x>","title":"<script>alert('xss')</script>",
                  "consequence":"a & b < c > d \" ' e","evidence":"\"><img src=x onerror=alert(1)>",
                  "fix":"</style></head><body><h1>PWNED</h1>","verify":"<iframe src=javascript:alert(1)>"}],
     "checkpoint":{"lanes":["<script>bad()</script>"],"mode":"<b>","omitted":["</style>"]}}
h=base_ok("09 XSS escaped", xss, expect_cards=1)
check("09: no raw <script", h.lower().count("<script")==0)
check("09: no raw <img",    "<img" not in h)
check("09: no raw <svg",    "<svg" not in h)
check("09: no raw <iframe", "<iframe" not in h)
check("09: style block intact (1 </style>)", h.count("</style>")==1, f"count={h.count('</style>')}")
check("09: one <body>", h.count("<body")==1, f"count={h.count('<body')}")
check("09: payload present but escaped", "&lt;script&gt;" in h)

# 10 unicode / emoji / CJK / RTL
uni={"target":"日本語アプリ 🚀","verdict":"READY",
     "findings":[{"severity":"provisional","title":"مرحبا — إتجاه RTL 🎯","evidence":"→ ↳ ✓ — café naïve Ω≈ π","fix":"日本語 中文 한국어"}],
     "coverage":{"total_paths":3,"segments":[{"kind":"covered","label":"覆盖 ✅","value":3}]}}
h=base_ok("10 unicode/emoji/CJK/RTL", uni, expect_cards=1)
check("10: emoji preserved", "🚀" in h and "🎯" in h)
check("10: CJK preserved", "日本語" in h and "中文" in h)

# 11 very long unbroken string
longtok="A"*260 + "https://example.com/"+"z"*160
h=base_ok("11 long unbroken string", {"findings":[{"severity":"info","title":longtok,"evidence":longtok}]}, expect_cards=1)
check("11: overflow-wrap present", "overflow-wrap:anywhere" in h)

# 12 many findings
many={"findings":[{"severity":sev,"title":f"finding {i}"} for i,sev in
      enumerate(["blocker","strong","provisional","info"]*10)]}
h=base_ok("12 many findings (40)", many, expect_cards=40)
# assert sorted: all blockers before any strong before any provisional before any info
order=re.findall(r'border-left-color:(#F43F5E|#F59E0B|#38BDF8|#64748B)', h)
seq=["#F43F5E"]*10+["#F59E0B"]*10+["#38BDF8"]*10+["#64748B"]*10
check("12: findings sorted by severity", order==seq, f"first8={order[:8]}")

# 13 degenerate coverage values
h=base_ok("13 bad coverage values", {"coverage":{"segments":[
    {"kind":"covered","value":0},{"kind":"missing","value":"NaN"},
    {"kind":"debt","value":"abc"},{"kind":"sampled","value":-5},None]}})
check("13: no flex:nan/inf in bar", "flex:nan" not in h.lower() and "flex:inf" not in h.lower())

# 14 missing summary -> derived
h=base_ok("14 derived summary", {"findings":[{"severity":"blocker","title":"a"},{"severity":"blocker","title":"b"},
                                             {"severity":"provisional","title":"c"}]}, expect_cards=3)
check("14: derived counts shown in stats row", 'c-blockers"><span class="n">2</span>' in h and 'c-provisional"><span class="n">1</span>' in h)

# 15/16 missing coverage / checkpoint already exercised in 06; explicit:
base_ok("15 missing coverage only", {"verdict":"READY","findings":[{"severity":"info","title":"x"}],
                                     "checkpoint":{"mode":"sequential"}})
base_ok("16 missing checkpoint only", {"verdict":"READY","findings":[{"severity":"info","title":"x"}],
                                       "coverage":{"total_paths":1,"segments":[{"kind":"covered","value":1}]}})

# 17 wrong types
base_ok("17 findings/segments wrong type", {"findings":"oops","coverage":{"segments":"nope"},"summary":"bad","checkpoint":42})

# 18 nulls everywhere
base_ok("18 nulls", {"target":None,"verdict":None,"generated_at":None,"summary":None,"coverage":None,
                     "findings":[None,{"severity":None,"title":None,"evidence":None}],"checkpoint":None})

# ---- new-feature assertions: grouping, coverage %, a11y, print ----
hb = render(full)
check("F1 blocker section +count",        'class="section tier-blockers"' in hb and '<h2>Blockers</h2><span class="count">2</span>' in hb)
check("F2 strong section",                'class="section tier-strong"' in hb and '<h2>Strong signals</h2><span class="count">1</span>' in hb)
check("F3 provisional section +count",    'class="section tier-provisional"' in hb and '<h2>Provisional</h2><span class="count">3</span>' in hb)
check("F4 coverage % correct (62%)",      '<strong>62%</strong>&nbsp; covered · 21 of 34 discovered paths' in hb)
check("F5 bar role+aria-label",           'role="img"' in hb and 'aria-label="Coverage breakdown' in hb)
check("F6 per-segment title (a11y)",      'title="covered — 21"' in hb)
check("F7 print break-inside:avoid",      'break-inside:avoid' in hb)
hr = render(ready)
check("F8 no severity sections when 0 findings", '<section class="section tier-' not in hr)
check("F9 clean note still shown",        'No blocking or open findings' in hr)
hu = render({"findings":[{"severity":"cosmic","title":"weird sev"}]})
check("F10 unknown severity under Notes",  '<h2>Notes</h2>' in hu)
hc = render({"coverage":{"total_paths":50,"segments":[{"kind":"covered","value":25},{"kind":"missing","value":25}]},"findings":[]})
check("F11 coverage 50% (25 of 50)",       '<strong>50%</strong>&nbsp; covered · 25 of 50 discovered paths' in hc)
hd = render({"coverage":{"segments":[{"kind":"covered","value":8},{"kind":"sampled","value":2}]},"findings":[]})
check("F12 coverage % derived from sum",   '<strong>80%</strong>&nbsp; covered · 8 of 10 discovered paths' in hd)
check("F13 premium report anatomy",        'class="masthead"' in hb and 'class="stamp"' in hb and 'class="stats-row"' in hb)
check("F14 collapsible evidence details",  hb.count("<details") == 6 and "Evidence · Fix · Verify" in hb)
check("F15 no external font links",        "fonts.googleapis.com" not in hb and "<link" not in hb.lower())

canon_cov = render({"coverage":{"segments":[
    {"kind":"COVERED","value":10},
    {"kind":"inferred","value":4},
    {"kind":"out_of_scope","value":3},
    {"kind":"evidence_debt","value":2},
]},"findings":[]})
check("F16 canonical coverage labels normalized", "covered&nbsp;<b>10</b>" in canon_cov and "evidence debt&nbsp;<b>2</b>" in canon_cov)
check("F17 canonical coverage colors not fallback", "#334155" not in canon_cov)
check("F18 out_of_scope shown human-readably", "out of scope&nbsp;<b>3</b>" in canon_cov)

canon_sev = render({"findings":[
    {"severity":"P0 Blocker","confidence":"Confirmed","title":"p0"},
    {"severity":"High","title":"high"},
    {"severity":"Medium","title":"medium"},
    {"severity":"LOW","title":"low"},
]})
check("F19 canonical severity aliases grouped", '<h2>Blockers</h2><span class="count">1</span>' in canon_sev and '<h2>Strong signals</h2><span class="count">1</span>' in canon_sev and '<h2>Provisional</h2><span class="count">1</span>' in canon_sev and '<h2>Notes</h2><span class="count">1</span>' in canon_sev)
check("F20 canonical severity aliases derive summary", 'c-blockers"><span class="n">1</span>' in canon_sev and 'c-strong"><span class="n">1</span>' in canon_sev and 'c-provisional"><span class="n">1</span>' in canon_sev)

# ---- de-duplication assertions (no repeated severity/confidence) ----
hb = render(full)
check("D1 no 'Strong \u00b7 Strong'",          "Strong \u00b7 Strong" not in hb)
check("D2 no 'Provisional \u00b7 Provisional'","Provisional \u00b7 Provisional" not in hb)
check("D3 no 'Blocker' word on finding cards",  hb.count("pill") == 0 or ">Blocker<" not in hb)
check("D4 blockers show 'Confirmed' chip",      ">Confirmed<" in hb)
h_ii = render({"findings":[{"severity":"provisional","confidence":"inferred","title":"x"}]})
check("D5 differing confidence shows chip",      ">Inferred<" in h_ii)
h_ss = render({"findings":[{"severity":"strong","confidence":"strong","title":"x"}]})
check("D6 equal sev/conf shows NO chip",         'class="pill' not in h_ss)
h_pp = render({"findings":[{"severity":"provisional","confidence":"Provisional","title":"x"}]})
check("D7 case-insensitive dedup",               'class="pill' not in h_pp)
check("D8 numbered finding cards",               'class="finding-num">01<' in hb)

# ---- interactive-mode assertions (opt-in --interactive) ----
import re as _re
d0 = render(full)
di = render(full, interactive=True)
check("I1 default has NO <script>",              "<script" not in d0.lower())
check("I2 default has NO controls bar",          'class="controls"' not in d0)
check("I3 default free of interactive hex",      "#5F6E90" not in d0)
check("I4 interactive has controls bar",         'class="controls"' in di)
check("I5 filter buttons per present severity",  di.count('class="fbtn on"') >= 3)
check("I6 interactive has search input",         'class="search"' in di and 'type="search"' in di)
check("I7 interactive has inline <script>",      "<script>" in di and "</script>" in di)
check("I8 findings carry data-sev",              'data-sev="blocker"' in di and 'data-sev="provisional"' in di)
check("I9 is-hidden + collapsed styles present", ".is-hidden" in di and ".collapsed" in di)
_hl = di.lower()
_ext = bool(_re.search(r'src\s*=\s*["\']?https?://', _hl)) or ("<link" in _hl) or ("@import" in _hl) or bool(_re.search(r'url\(\s*["\']?https?://', _hl))
check("I10 interactive self-contained",          not _ext)
check("I11 interactive script has no network",   not any(t in di for t in ["fetch(", "XMLHttpRequest", "http://", "https://api"]))
check("I12 print forces hidden visible",         "is-hidden{display:block!important" in di.replace(" ",""))
check("I13 print hides controls",                "controls{display:none" in di.replace(" ",""))

print(f"\n==== {len(PASS)} passed, {len(FAIL)} failed ====")
if FAIL:
    print("FAILURES:", FAIL); sys.exit(1)
print("ALL SIMULATIONS PASSED")

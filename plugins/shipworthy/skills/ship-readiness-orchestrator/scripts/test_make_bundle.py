#!/usr/bin/env python3
"""Simulation suite for make_bundle.py — zip validity, manifest integrity
(recompute SHA-256), include/exclude flags, and graceful failure."""
import os, sys, json, subprocess, zipfile, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "sample-report.json")
SCRIPT = os.path.join(HERE, "make_bundle.py")
TMP = os.path.join(HERE, "_bundle_tmp")
os.makedirs(TMP, exist_ok=True)

PASS, FAIL = [], []
def ck(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  {'PASS' if c else 'FAIL'}  {n}{'' if c else '  -> ' + d}")
def run(args):
    return subprocess.run([sys.executable, SCRIPT] + args, capture_output=True, text=True)
def path(*p): return os.path.join(TMP, *p)

r = run([SAMPLE, path("bundle.zip")])
ck("B1 exit 0", r.returncode == 0, r.stderr[-160:])
ck("B2 valid zip", zipfile.is_zipfile(path("bundle.zip")))
z = zipfile.ZipFile(path("bundle.zip")); names = set(z.namelist())
ck("B3 ledger.json present", "ledger.json" in names)
ck("B4 manifest.json present", "manifest.json" in names)
ck("B5 README.txt present", "README.txt" in names)
ck("B6 report.html auto-generated", "readiness-report.html" in names)
ck("B7 sarif auto-generated", "readiness.sarif" in names)
man = json.loads(z.read("manifest.json"))
ok, bad = True, ""
for f in man["files"]:
    b = z.read(f["name"])
    if hashlib.sha256(b).hexdigest() != f["sha256"] or len(b) != f["bytes"]:
        ok, bad = False, f["name"]
ck("B8 manifest SHA-256+bytes match all files", ok, bad)
ck("B9 manifest verdict correct", man.get("verdict") == "NOT READY")
ck("B10 manifest counts correct", man["counts"]["blocker"] == 2 and man["counts"]["strong"] == 1 and man["counts"]["provisional"] == 3)
ck("B11 ledger bytes preserved", z.read("ledger.json") == open(SAMPLE, "rb").read())

run([SAMPLE, path("b2.zip"), "--no-report", "--no-sarif"])
n2 = set(zipfile.ZipFile(path("b2.zip")).namelist())
ck("B12 --no-report/--no-sarif honored", "readiness-report.html" not in n2 and "readiness.sarif" not in n2 and "ledger.json" in n2)

os.makedirs(path("traces"), exist_ok=True)
open(path("traces", "net.log"), "w").write("POST /api/pay -> 500")
open(path("note.txt"), "w").write("analyst note")
run([SAMPLE, path("b3.zip"), "--include", path("note.txt"), "--include", path("traces")])
n3 = set(zipfile.ZipFile(path("b3.zip")).namelist())
ck("B13 --include file present", "note.txt" in n3)
ck("B14 --include dir contents present", any("net.log" in x for x in n3))

r4 = run([SAMPLE, path("b4.zip"), "--include", path("nope-missing")])
ck("B15 missing --include skipped gracefully", r4.returncode == 0 and "skipped" in r4.stderr)
ck("B16 missing input -> exit 2", run([path("nope.json"), path("x.zip")]).returncode == 2)
open(path("broken.json"), "w").write("{bad,,}")
ck("B17 broken JSON -> exit 2", run([path("broken.json"), path("x.zip")]).returncode == 2)

import shutil
shutil.rmtree(TMP, ignore_errors=True)
print(f"\n==== EVIDENCE BUNDLE: {len(PASS)} passed, {len(FAIL)} failed ====")
if FAIL:
    print("FAILURES:", FAIL); sys.exit(1)
print("ALL BUNDLE TESTS PASSED")

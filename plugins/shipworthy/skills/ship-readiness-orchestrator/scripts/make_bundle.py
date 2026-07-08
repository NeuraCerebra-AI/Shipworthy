#!/usr/bin/env python3
"""
Shipworthy — package a finished readiness audit into a portable, tamper-evident
evidence bundle (a .zip). Generated locally; nothing leaves the machine.

Usage:
    python3 make_bundle.py [ledger.json] [out.zip] [--include PATH ...] [--no-report] [--no-sarif]

Bundle contents:
    ledger.json            the canonical readiness ledger (source of truth)
    readiness-report.html  human-readable report        (unless --no-report)
    readiness.sarif        machine-readable findings     (unless --no-sarif)
    manifest.json          verdict, counts, and a SHA-256 + byte count per file
    README.txt             what this bundle is
    <extras>               anything passed with --include (files or directories)

The manifest's per-file SHA-256 makes the bundle tamper-evident — useful as a
defensible audit trail for a stakeholder, client, or compliance reviewer.
"""
import sys, os, json, io, zipfile, hashlib, datetime

def sha256(b): return hashlib.sha256(b).hexdigest()

def try_render_html(data):
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import render_report
        return render_report.render(data).encode("utf-8")
    except Exception as e:
        print(f"  note: report not generated ({type(e).__name__}); continuing", file=sys.stderr)
        return None

def try_render_sarif(data):
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import to_sarif
        return json.dumps(to_sarif.to_sarif(data), indent=2).encode("utf-8")
    except Exception as e:
        print(f"  note: sarif not generated ({type(e).__name__}); continuing", file=sys.stderr)
        return None

def summary(data):
    findings = [f for f in (data.get("findings") or []) if isinstance(f, dict)]
    from collections import Counter
    c = Counter(f.get("severity", "info") for f in findings)
    return {
        "verdict": data.get("verdict"),
        "target": data.get("target"),
        "counts": {"blocker": c.get("blocker", 0), "strong": c.get("strong", 0),
                   "provisional": c.get("provisional", 0), "info": c.get("info", 0),
                   "total_findings": len(findings)},
        "coverage": data.get("coverage", {}).get("total_paths") if isinstance(data.get("coverage"), dict) else None,
    }

def add(files, name, content_bytes):
    """files: dict name->bytes; de-dupes names."""
    base, i = name, 1
    while name in files:
        stem, dot, ext = base.rpartition(".")
        name = f"{stem}_{i}.{ext}" if dot else f"{base}_{i}"
        i += 1
    files[name] = content_bytes

def main():
    argv = sys.argv[1:]
    includes = []
    while "--include" in argv:
        j = argv.index("--include")
        if j + 1 < len(argv):
            includes.append(argv[j + 1]); del argv[j:j + 2]
        else:
            del argv[j]
    no_report = "--no-report" in argv
    no_sarif = "--no-sarif" in argv
    pos = [a for a in argv if not a.startswith("--")]
    inp = pos[0] if len(pos) > 0 else "readiness-report.json"
    out = pos[1] if len(pos) > 1 else "evidence-bundle.zip"

    try:
        with open(inp, encoding="utf-8") as fh:
            raw = fh.read(); data = json.loads(raw)
    except FileNotFoundError:
        print(f"error: input not found: {inp}", file=sys.stderr); sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"error: {inp} is not valid JSON ({e})", file=sys.stderr); sys.exit(2)

    files = {}
    add(files, "ledger.json", raw.encode("utf-8"))
    if not no_report:
        h = try_render_html(data)
        if h: add(files, "readiness-report.html", h)
    if not no_sarif:
        s = try_render_sarif(data)
        if s: add(files, "readiness.sarif", s)
    for p in includes:
        if os.path.isfile(p):
            add(files, os.path.basename(p), open(p, "rb").read())
        elif os.path.isdir(p):
            for root, _, fs in os.walk(p):
                for fn in fs:
                    fp = os.path.join(root, fn)
                    rel = os.path.relpath(fp, os.path.dirname(p.rstrip("/")))
                    add(files, rel.replace(os.sep, "/"), open(fp, "rb").read())
        else:
            print(f"  note: --include path not found, skipped: {p}", file=sys.stderr)

    manifest = {
        "tool": "Shipworthy",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        **summary(data),
        "files": [{"name": n, "bytes": len(b), "sha256": sha256(b)} for n, b in sorted(files.items())],
    }
    manifest_bytes = json.dumps(manifest, indent=2).encode("utf-8")
    readme = (b"Shipworthy evidence bundle\n"
              b"==========================\n\n"
              b"ledger.json      - canonical readiness ledger (source of truth)\n"
              b"readiness-report.html - human-readable report\n"
              b"readiness.sarif  - machine-readable findings (SARIF 2.1.0)\n"
              b"manifest.json    - verdict, counts, and a SHA-256 per file (tamper-evidence)\n\n"
              b"Verify integrity: recompute SHA-256 of each file and compare to manifest.json.\n"
              b"Generated locally; read-only audit -- no fixes were applied.\n")

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in sorted(files.items()):
            z.writestr(n, b)
        z.writestr("manifest.json", manifest_bytes)
        z.writestr("README.txt", readme)

    print(f"wrote {out}: {len(files) + 2} files, verdict={manifest.get('verdict')}, "
          f"{manifest['counts']['total_findings']} findings")
    sys.exit(0)

if __name__ == "__main__":
    main()

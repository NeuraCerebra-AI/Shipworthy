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
import sys, os, json, io, zipfile, hashlib, datetime, importlib.util, tempfile
sys.dont_write_bytecode = True
MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_INCLUDE_BYTES = 64 * 1024 * 1024
MAX_INCLUDE_FILES = 1024

README_BYTES = (b"Shipworthy evidence bundle\n"
                b"==========================\n\n"
                b"ledger.json      - canonical readiness ledger (source of truth)\n"
                b"readiness-report.html - human-readable report\n"
                b"readiness.sarif  - machine-readable findings (SARIF 2.1.0)\n"
                b"manifest.json    - verdict, counts, and a SHA-256 per file (tamper-evidence)\n\n"
                b"Verify integrity: recompute SHA-256 of each file and compare to manifest.json.\n"
                b"Generated locally; read-only audit -- no fixes were applied.\n")

def sha256(b): return hashlib.sha256(b).hexdigest()

def atomic_write_bytes(path, value):
    destination = os.path.abspath(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=os.path.dirname(destination), prefix="." + os.path.basename(destination) + ".", delete=False) as handle:
            temporary = handle.name
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)

def load_sibling(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py")
    spec = importlib.util.spec_from_file_location("shipworthy_" + name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def try_render_html(data):
    try:
        render_report = load_sibling("render_report")
        return render_report.render(data).encode("utf-8")
    except Exception as e:
        print(f"  note: report not generated ({type(e).__name__}); continuing", file=sys.stderr)
        return None

def try_render_sarif(data):
    try:
        to_sarif = load_sibling("to_sarif")
        return json.dumps(to_sarif.to_sarif(data), indent=2).encode("utf-8")
    except Exception as e:
        print(f"  note: sarif not generated ({type(e).__name__}); continuing", file=sys.stderr)
        return None

def summary(data):
    data = load_sibling("render_report").project_input(data)
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

def add_includes(files, includes):
    """Add bounded regular files without following links or special files."""
    added_bytes = 0
    added_files = 0

    def add_file(path, name):
        nonlocal added_bytes, added_files
        if os.path.islink(path):
            raise ValueError(f"symlink include is not allowed: {path}")
        if not os.path.isfile(path):
            raise ValueError(f"include is not a regular file: {path}")
        size = os.path.getsize(path)
        if added_files + 1 > MAX_INCLUDE_FILES:
            raise ValueError(f"too many include files (limit {MAX_INCLUDE_FILES})")
        if added_bytes + size > MAX_INCLUDE_BYTES:
            raise ValueError(f"include data too large (limit {MAX_INCLUDE_BYTES} bytes)")
        with open(path, "rb") as handle:
            content = handle.read(MAX_INCLUDE_BYTES + 1)
        if len(content) != size:
            raise ValueError(f"include changed while reading: {path}")
        add(files, name, content)
        added_files += 1
        added_bytes += size

    for path in includes:
        if os.path.islink(path):
            raise ValueError(f"symlink include is not allowed: {path}")
        if os.path.isfile(path):
            add_file(path, os.path.basename(path))
        elif os.path.isdir(path):
            parent = os.path.dirname(path.rstrip(os.sep))
            for root, directories, filenames in os.walk(path, followlinks=False):
                linked = [name for name in directories if os.path.islink(os.path.join(root, name))]
                if linked:
                    raise ValueError(f"symlink include is not allowed: {os.path.join(root, linked[0])}")
                for filename in sorted(filenames):
                    file_path = os.path.join(root, filename)
                    name = os.path.relpath(file_path, parent).replace(os.sep, "/")
                    add_file(file_path, name)
        else:
            print(f"  note: --include path not found, skipped: {path}", file=sys.stderr)

def zip_datetime(generated_at):
    """Normalize an ISO timestamp to the legal, two-second ZIP time range."""
    try:
        parsed = datetime.datetime.fromisoformat(str(generated_at).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=datetime.timezone.utc)
        parsed = parsed.astimezone(datetime.timezone.utc)
    except (TypeError, ValueError, OverflowError):
        parsed = datetime.datetime(1980, 1, 1, tzinfo=datetime.timezone.utc)
    if parsed.year < 1980:
        parsed = datetime.datetime(1980, 1, 1, tzinfo=datetime.timezone.utc)
    elif parsed.year > 2107:
        parsed = datetime.datetime(2107, 12, 31, 23, 59, 58, tzinfo=datetime.timezone.utc)
    return (parsed.year, parsed.month, parsed.day, parsed.hour, parsed.minute,
            parsed.second - (parsed.second % 2))

def zip_info(name, generated_at):
    info = zipfile.ZipInfo(name, date_time=zip_datetime(generated_at))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info

def build_bundle_bytes(data, files, generated_at):
    """Build the exact legacy bundle entry contract without filesystem access."""
    payloads = dict(files)
    manifest = {
        "tool": "Shipworthy",
        "generated_at": generated_at,
        **summary(data),
        "files": [{"name": n, "bytes": len(b), "sha256": sha256(b)} for n, b in sorted(payloads.items())],
    }
    manifest_bytes = json.dumps(manifest, indent=2).encode("utf-8")
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in sorted(payloads.items()):
            z.writestr(zip_info(n, generated_at), b)
        z.writestr(zip_info("manifest.json", generated_at), manifest_bytes)
        z.writestr(zip_info("README.txt", generated_at), README_BYTES)
    return output.getvalue()

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
    if len(pos) != 2:
        print("usage: make_bundle.py INPUT.json OUTPUT.zip [--include PATH ...] [--no-report] [--no-sarif]", file=sys.stderr); sys.exit(2)
    inp, out = pos

    try:
        if os.path.getsize(inp) > MAX_INPUT_BYTES:
            print(f"error: input too large (limit {MAX_INPUT_BYTES} bytes)", file=sys.stderr); sys.exit(2)
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
    try:
        add_includes(files, includes)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr); sys.exit(2)

    source_ledger = data.get("source_ledger") if isinstance(data.get("source_ledger"), dict) else {}
    generated_at = data.get("generated_at") or source_ledger.get("generated_at") or "1980-01-01T00:00:00Z"
    atomic_write_bytes(out, build_bundle_bytes(data, files, generated_at))

    report_summary = summary(data)
    print(f"wrote {out}: {len(files) + 2} files, verdict={report_summary.get('verdict')}, "
          f"{report_summary['counts']['total_findings']} findings")
    sys.exit(0)

if __name__ == "__main__":
    main()

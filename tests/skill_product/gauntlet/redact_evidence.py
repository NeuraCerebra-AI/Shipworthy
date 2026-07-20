#!/usr/bin/env python3
"""Create bounded redacted evidence copies without changing run artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PASS_FILES = {
    "acceptance-result.json": "acceptance-result.json",
    "comparison-packet.json": "comparison-packet.json",
    "agent-evidence/readiness-ledger.json": "readiness-ledger.json",
    "agent-evidence/report-input.json": "report-input.json",
    "agent-evidence/report.html": "report.html",
    "run.log": "run.log",
}
NOT_PROVEN_FILES = {"acceptance-result.json": "acceptance-result.json", "run.log": "run.log"}
MAX_FILE = 5_000_000


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def export(manifest_path: Path, source: Path, destination: Path, status: str) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source, destination = source.resolve(), destination.resolve()
    if source != Path(manifest["output"]).resolve():
        raise ValueError("source does not match manifest output")
    if destination.exists():
        raise ValueError("destination must not exist")
    destination.mkdir(parents=True)
    allowlist = PASS_FILES if status == "PASS" else NOT_PROVEN_FILES
    replacements = {
        manifest.get("reset_token", ""): "[REDACTED_RESET_TOKEN]",
        manifest.get("controller_root", ""): "[REDACTED_CONTROLLER_ROOT]",
        str(Path.home()): "[REDACTED_HOME]",
    }
    replacements = {key: value for key, value in replacements.items() if key}
    files = []
    for relative, name in allowlist.items():
        origin = source / relative
        if not origin.is_file() or origin.stat().st_size > MAX_FILE:
            raise ValueError(f"missing or oversized evidence file: {relative}")
        original = origin.read_bytes()
        text = original.decode("utf-8")
        replacement_count = 0
        for secret, label in replacements.items():
            replacement_count += text.count(secret)
            text = text.replace(secret, label)
        if any(secret in text for secret in replacements):
            raise ValueError(f"residual secret in {relative}")
        copied = text.encode("utf-8")
        if name.endswith(".json"):
            json.loads(copied)
        target = destination / name
        target.write_bytes(copied)
        files.append({"name": name, "source_sha256": digest(original), "destination_sha256": digest(copied), "replacements": replacement_count})
    extras = {path.name for path in destination.iterdir()} - set(allowlist.values())
    if extras:
        raise ValueError(f"unexpected exported file: {sorted(extras)[0]}")
    return {"export_version": "shipworthy-gauntlet-export-v1", "status": status, "files": files}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-manifest", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--status", choices=("PASS", "NOT_PROVEN"), required=True)
    args = parser.parse_args()
    try:
        packet = export(Path(args.run_manifest), Path(args.source), Path(args.destination), args.status)
    except Exception as error:
        print(f"error: {error}", file=__import__("sys").stderr)
        return 1
    print(json.dumps(packet, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

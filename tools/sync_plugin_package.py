#!/usr/bin/env python3
"""Keep the packaged plugin skills aligned with the repository skill sources.

The top-level skill directories remain the canonical source for backwards-
compatible standalone installs. The packaged plugin is a committed mirror so
Codex and Claude Code can install one namespaced Shipworthy plugin.

Usage:
    python3 tools/sync_plugin_package.py          # verify the mirror
    python3 tools/sync_plugin_package.py --write # refresh the mirror
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


SKILL_NAMES = (
    "ship-readiness-orchestrator",
    "ship-deep-review",
    "ship-product-workflows",
    "ship-workflow-clarity",
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def files_under(path: Path) -> set[Path]:
    return {
        item.relative_to(path)
        for item in path.rglob("*")
        if item.is_file()
    }


def compare_tree(source: Path, destination: Path) -> list[str]:
    differences: list[str] = []
    source_files = files_under(source)
    destination_files = files_under(destination) if destination.is_dir() else set()

    for relative in sorted(source_files - destination_files):
        differences.append(f"missing packaged file: {destination / relative}")
    for relative in sorted(destination_files - source_files):
        differences.append(f"stale packaged file: {destination / relative}")
    for relative in sorted(source_files & destination_files):
        if not filecmp.cmp(source / relative, destination / relative, shallow=False):
            differences.append(f"changed packaged file: {destination / relative}")
    return differences


def sync(write: bool) -> int:
    root = repository_root()
    package_skills = root / "plugins" / "shipworthy" / "skills"
    differences: list[str] = []

    for name in SKILL_NAMES:
        source = root / name
        destination = package_skills / name
        if not source.is_dir():
            differences.append(f"missing source skill: {source}")
            continue
        if write:
            if destination.exists():
                shutil.rmtree(destination)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, destination)
        else:
            differences.extend(compare_tree(source, destination))

    if write:
        print(f"Synced {len(SKILL_NAMES)} skills into {package_skills}")
        return 0
    if differences:
        print("Plugin package is out of sync:")
        for difference in differences:
            print(f"- {difference}")
        print("Run: python3 tools/sync_plugin_package.py --write")
        return 1
    print(f"Plugin package is in sync ({len(SKILL_NAMES)} skills)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="replace the generated skill mirror with the canonical sources",
    )
    args = parser.parse_args()
    return sync(write=args.write)


if __name__ == "__main__":
    raise SystemExit(main())

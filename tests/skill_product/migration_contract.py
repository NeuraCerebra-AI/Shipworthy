from __future__ import annotations

import hashlib
import re
import subprocess
import tarfile
import tempfile
from pathlib import Path
from pathlib import PurePosixPath


PACKAGE_ONLY_FILES = {".python-version", "pyproject.toml", "uv.lock"}
PACKAGE_ONLY_PREFIXES = ("src/shipworthy/", "schemas/v1/", "scripts/", "tests/")
INSTALLED_SCRIPT_ROOT = "plugins/shipworthy/skills/ship-readiness-orchestrator/scripts/"
APPROVED_INSTALLED_SCRIPTS = {
    INSTALLED_SCRIPT_ROOT + "make_bundle.py",
    INSTALLED_SCRIPT_ROOT + "render_report.py",
    INSTALLED_SCRIPT_ROOT + "to_sarif.py",
}
LEGACY_INSTALLED_ARTIFACTS = {
    INSTALLED_SCRIPT_ROOT + "sample-report.json",
    INSTALLED_SCRIPT_ROOT + "test_make_bundle.py",
    INSTALLED_SCRIPT_ROOT + "test_render_report.py",
    INSTALLED_SCRIPT_ROOT + "test_skill_contract.py",
    INSTALLED_SCRIPT_ROOT + "test_to_sarif.py",
}
BASELINE_TOP_LEVEL = {
    ".claude-plugin/marketplace.json",
    ".gitignore",
    "ARCHITECTURE.md",
    "README.md",
    "install.sh",
}
EXCLUDED_COORDINATION = {
    "docs/superpowers/plans/2026-07-15-lean-host-native-shipworthy.md",
    "docs/superpowers/plans/2026-07-17-four-self-contained-skills.md",
    "docs/superpowers/specs/2026-07-17-four-self-contained-skills-design.md",
}
OWNERSHIP_VALUES = {
    "PREEXISTING_KEEP",
    "PREEXISTING_MIGRATE",
    "UNRELATED_DO_NOT_TOUCH",
}
TRACKED_PATCH_SHA256 = "b9da20a8836748844023b6b9655d5d2a8bced132a82dc88f7c0c3afb53c7494a"
UNTRACKED_ARCHIVE_SHA256 = "63299f65ee7d61d092f4554ed0e72c1c54920844edc3f232cae08c025d8f613b"
UNTRACKED_INVENTORY_SHA256 = "f81e99c9b3d2f557e3c4ec76b52336120c2860b3ad2f4c17014f4195de48ee78"
MIGRATED_DIRTY_ADDITIONS = {
    "A screenshot proves only the state visible at capture time; it does not prove an entire workflow. Neither native nor Playwright evidence may silently upgrade a finding to `Confirmed` or verifier status to `approved`. Include in the audit output the chosen evidence mode, selection reason, observed step boundary, artifacts, limitations, and not-proven statements when this skill runs standalone; return to the orchestrator when lane-dispatched the same bounded evidence context. Skill-only operation remains valid when the optional core is absent.":
        "A screenshot proves only the state visible at capture time; it does not prove an entire workflow. Neither native nor Playwright evidence may silently upgrade a finding to `Confirmed` or verifier status to `approved`. Include in the audit output the chosen evidence mode, selection reason, observed step boundary, artifacts, limitations, and not-proven statements when this skill runs standalone; return to the orchestrator when lane-dispatched the same bounded evidence context. Shipworthy operates through the four public skills and their skill-owned resources without requiring another product surface.",
    "Read `$ship-readiness-orchestrator`'s `references/browser-evidence-routing.md` before choosing a browser evidence path. Use a Codex- or Claude-hosted native browser or computer-use capability as the default for adaptive exploration. Use an existing target-owned Playwright setup only for deterministic replay, explicit assertions, isolated contexts, traces, cross-browser checks, or CI regression proof. Never install Playwright or change the target application merely to obtain browser evidence; record an unavailable capability as evidence debt.":
        "Read this skill's `references/runtime-evidence-and-tools.md` before choosing a browser evidence path. Use a Codex- or Claude-hosted native browser or computer-use capability as the default for adaptive exploration. Use an existing target-owned Playwright setup only for deterministic replay, explicit assertions, isolated contexts, traces, cross-browser checks, or CI regression proof. Never install Playwright or change the target application merely to obtain browser evidence; record an unavailable capability as evidence debt.",
    "Skill-only operation remains valid when the optional core is absent. Continue to route and report through the four public skills without silently using or upgrading an unavailable core.":
        "Shipworthy operates through the four public skills and their skill-owned resources. Continue to route and report through those skills without requiring another product surface.",
    'ck("B13 public routing surfaces preserve skill-only operation without core", all("skill-only operation" in text_value.lower() and "core" in text_value.lower() for text_value in [browser_routing, skill, product_workflows]))':
        'ck("B13 public routing surfaces preserve four-skill standalone operation", all("four public skills" in text_value.lower() and "without requiring another product surface" in text_value.lower() for text_value in [browser_routing, skill, product_workflows]))',
}
MIGRATED_REMOVED_DIRTY_ADDITIONS = {
    "# generated package and release evidence",
    "artifacts/",
    "build/",
    "dist/",
}
MOVED_TRACKED_PATHS = {
    INSTALLED_SCRIPT_ROOT + "sample-report.json": "tests/skill_product/fixtures/sample-report.json",
    INSTALLED_SCRIPT_ROOT + "test_make_bundle.py": "tests/skill_product/test_make_bundle_legacy.py",
    INSTALLED_SCRIPT_ROOT + "test_render_report.py": "tests/skill_product/test_render_report_legacy.py",
    INSTALLED_SCRIPT_ROOT + "test_skill_contract.py": "tests/skill_product/test_skill_contract_legacy.py",
    INSTALLED_SCRIPT_ROOT + "test_to_sarif.py": "tests/skill_product/test_to_sarif_legacy.py",
}
EXACT_PATCH_PRESERVATION_PATHS = {
    ".gitignore",
    "plugins/shipworthy/skills/ship-product-workflows/SKILL.md",
    "plugins/shipworthy/skills/ship-product-workflows/references/living-audit-ledger.md",
    "plugins/shipworthy/skills/ship-readiness-orchestrator/references/exports-and-ci.md",
    "plugins/shipworthy/skills/ship-readiness-orchestrator/references/final-report-contract.md",
    "plugins/shipworthy/skills/ship-readiness-orchestrator/references/lane-prompts.md",
}


def _cells(line: str) -> list[str]:
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def read_table(path: Path, first_header: str, last_header: str) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        headers = _cells(line) if line.startswith("|") else []
        if headers and headers[0] == first_header and headers[-1] == last_header:
            rows: list[dict[str, str]] = []
            for row_line in lines[index + 2 :]:
                if not row_line.startswith("|"):
                    break
                values = _cells(row_line)
                if len(values) != len(headers):
                    raise AssertionError(f"malformed table row in {path}: {row_line}")
                rows.append(dict(zip(headers, values)))
            return rows
    raise AssertionError(f"table {first_header!r}..{last_header!r} not found in {path}")


def is_expected_deletion(row: dict[str, str]) -> bool:
    path = row["Exact path"]
    moved = row["Destination"] != path
    package_scoped = (
        path in PACKAGE_ONLY_FILES
        or path.endswith("shipworthy-compatibility.json")
        or path.startswith(PACKAGE_ONLY_PREFIXES)
    )
    return moved and (package_scoped or path in LEGACY_INSTALLED_ARTIFACTS)


def is_installed_inventory_path_allowed(path: str) -> bool:
    lowered = path.lower()
    name = Path(path).name.lower()
    forbidden_parts = ("/__pycache__/", "/.pytest_cache/", "/fixtures/", "/migration/")
    if any(part in lowered for part in forbidden_parts):
        return False
    if "lifecycle" in name or name.startswith("test_") or "sample" in name:
        return False
    if name.endswith((".pyc", ".pyo")):
        return False
    if "/scripts/" in lowered:
        return path in APPROVED_INSTALLED_SCRIPTS
    return True


def read_dirty_ownership(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    ownership: dict[str, str] = {}
    tracked = read_table(path, "Exact path", "Preservation rule")
    for row in tracked:
        candidate = row["Exact path"]
        value = row["Classification"]
        if value not in OWNERSHIP_VALUES:
            raise ValueError(f"invalid dirty ownership {value!r} for {candidate}")
        if candidate in ownership:
            raise ValueError(f"duplicate dirty path: {candidate}")
        ownership[candidate] = value

    current: str | None = None
    for line in lines:
        if line.startswith("## Untracked paths: "):
            current = line.removeprefix("## Untracked paths: ").strip()
            if current not in OWNERSHIP_VALUES:
                raise ValueError(f"invalid dirty ownership section: {current}")
            continue
        if line.startswith("## "):
            current = None
            continue
        if current and line.startswith("- `") and line.endswith("`"):
            candidate = line[3:-1]
            if candidate in ownership:
                raise ValueError(f"duplicate dirty path: {candidate}")
            ownership[candidate] = current
    return ownership


def stable_id(path: str) -> str:
    return "MAP-" + hashlib.sha256(path.encode("utf-8")).hexdigest()[:12].upper()


def is_safe_repository_path(path: str) -> bool:
    if not path or "\\" in path or "\x00" in path:
        return False
    pure = PurePosixPath(path)
    return (
        not pure.is_absolute()
        and path == pure.as_posix()
        and all(part not in {"", ".", ".."} for part in pure.parts)
    )


def _snapshot_inventory(path: Path) -> dict[str, str]:
    inventory: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, _size, candidate = line.split("  ", 2)
        if candidate in inventory:
            raise ValueError(f"duplicate snapshot path: {candidate}")
        inventory[candidate] = digest
    return inventory


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_snapshot(snapshot_inventory: Path) -> dict[str, str]:
    snapshot = snapshot_inventory.parent
    archive = snapshot / "untracked-files.tar.gz"
    readme = snapshot / "README.md"
    readme_text = readme.read_text(encoding="utf-8")
    immutable = {
        "untracked-files.tar.gz": UNTRACKED_ARCHIVE_SHA256,
        "untracked-files.sha256": UNTRACKED_INVENTORY_SHA256,
    }
    for name, expected in immutable.items():
        match = re.search(rf"\| `{re.escape(name)}` \| `([0-9a-f]{{64}})` \|", readme_text)
        if not match or match.group(1) != expected:
            raise ValueError(f"snapshot README digest drift for {name}")
        candidate = snapshot / name
        if _sha256_file(candidate) != expected:
            raise ValueError(f"snapshot artifact digest mismatch for {name}")

    inventory = _snapshot_inventory(snapshot_inventory)
    members: dict[str, tuple[int, str]] = {}
    try:
        with tarfile.open(archive, "r:gz") as bundle:
            for member in bundle.getmembers():
                if not member.isfile() or not is_safe_repository_path(member.name):
                    raise ValueError(f"unsafe snapshot archive member: {member.name}")
                if member.name in members:
                    raise ValueError(f"duplicate snapshot archive member: {member.name}")
                handle = bundle.extractfile(member)
                if handle is None:
                    raise ValueError(f"unreadable snapshot archive member: {member.name}")
                data = handle.read()
                members[member.name] = (len(data), hashlib.sha256(data).hexdigest())
    except (tarfile.TarError, OSError) as exc:
        raise ValueError("invalid snapshot archive") from exc

    inventory_details: dict[str, tuple[int, str]] = {}
    for line in snapshot_inventory.read_text(encoding="utf-8").splitlines():
        digest, size, candidate = line.split("  ", 2)
        inventory_details[candidate] = (int(size), digest)
    payload_members = {
        name: details
        for name, details in members.items()
        if not PurePosixPath(name).name.startswith("._")
    }
    apple_metadata = {
        str(PurePosixPath(name).parent / PurePosixPath(name).name[2:])
        for name in members
        if PurePosixPath(name).name.startswith("._")
    }
    if payload_members != inventory_details:
        raise ValueError("snapshot archive members do not match checksum inventory")
    if apple_metadata and apple_metadata != set(inventory_details):
        raise ValueError("snapshot AppleDouble metadata does not cover exact payload members")
    return inventory


def authoritative_baseline_inventory(
    root: Path, base_commit: str, snapshot_inventory: Path
) -> dict[str, str]:
    tracked_output = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", base_commit], cwd=root, text=True
    )
    tracked = {
        path
        for path in tracked_output.splitlines()
        if path in BASELINE_TOP_LEVEL or path.startswith("plugins/shipworthy/")
    }
    untracked = _verify_snapshot(snapshot_inventory)
    relevant_untracked = set(untracked) - EXCLUDED_COORDINATION

    protected_patch = snapshot_inventory.parent / "tracked-dirty.patch"
    patch_bytes = protected_patch.read_bytes()
    if hashlib.sha256(patch_bytes).hexdigest() != TRACKED_PATCH_SHA256:
        raise ValueError("protected tracked dirty patch digest mismatch")

    current_lines = {}
    for path in tracked:
        current_path = root / MOVED_TRACKED_PATHS.get(path, path)
        if not current_path.is_file():
            raise ValueError(f"tracked baseline file and approved destination absent: {path}")
        current_lines[path] = current_path.read_text(encoding="utf-8").splitlines()
    patch_path: str | None = None
    for line in patch_bytes.decode("utf-8").splitlines():
        if line.startswith("+++ b/"):
            patch_path = line[6:]
        elif (
            line.startswith("+")
            and not line.startswith("+++")
            and patch_path in EXACT_PATCH_PRESERVATION_PATHS
        ):
            expected = MIGRATED_DIRTY_ADDITIONS.get(line[1:], line[1:])
            if line[1:] in MIGRATED_REMOVED_DIRTY_ADDITIONS:
                continue
            if patch_path is None or expected not in current_lines[patch_path]:
                raise ValueError(
                    f"tracked dirty addition no longer preserved: {patch_path}"
                )

    inventory = {path: untracked[path] for path in relevant_untracked}
    with tempfile.TemporaryDirectory() as directory:
        snapshot_root = Path(directory)
        for path in tracked:
            candidate = snapshot_root / path
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_bytes(
                subprocess.check_output(["git", "show", f"{base_commit}:{path}"], cwd=root)
            )
        applied = subprocess.run(
            ["patch", "-p1", "--batch", "--silent", "-d", snapshot_root],
            input=patch_bytes,
            capture_output=True,
        )
        if applied.returncode:
            raise ValueError("protected tracked dirty patch cannot reconstruct baseline")
        for path in tracked:
            candidate = snapshot_root / path
            if candidate.is_symlink():
                raise ValueError(f"baseline path is a symlink: {path}")
            inventory[path] = hashlib.sha256(candidate.read_bytes()).hexdigest()
    return inventory


def reconcile_final_state(
    baseline: dict[str, str],
    final: dict[str, str],
    mapped_paths: set[str],
    deletion_paths: set[str],
    declared_new_paths: set[str],
) -> dict[str, set[str]]:
    for collection in (baseline, final):
        for path, digest in collection.items():
            if not is_safe_repository_path(path):
                raise ValueError(f"unsafe reconciliation path: {path}")
            if not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError(f"invalid reconciliation digest for {path}")
    if not all(is_safe_repository_path(path) for path in declared_new_paths):
        raise ValueError("unsafe declared destination")
    new = set(final) - set(baseline)
    deleted = set(baseline) - set(final)
    changed = {path for path in set(baseline) & set(final) if baseline[path] != final[path]}
    if new - declared_new_paths:
        raise ValueError(f"undeclared final paths: {sorted(new - declared_new_paths)}")
    if deleted - deletion_paths:
        raise ValueError(f"unmanifested deletions: {sorted(deleted - deletion_paths)}")
    if (changed | deleted) - mapped_paths:
        raise ValueError("final changes are outside the migration map")
    return {"new": new, "changed": changed, "deleted": deleted}


def read_path_inventory(path: Path) -> set[str]:
    paths: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        candidate = line.strip()
        if not candidate or candidate.startswith("#"):
            continue
        if candidate in paths:
            raise ValueError(f"duplicate approved installed path: {candidate}")
        if not is_safe_repository_path(candidate):
            raise ValueError(f"unsafe approved installed path: {candidate}")
        paths.add(candidate)
    return paths


def audit_installed_inventory(
    root: Path,
    approved: set[str],
    pending_removal: set[str],
    *,
    mode: str,
    declared_future: set[str],
) -> list[str]:
    if mode not in {"transitional", "final"}:
        raise ValueError(f"unknown installed inventory mode: {mode}")
    if not declared_future <= approved:
        raise ValueError("declared future destinations must be approved")
    if not all(is_safe_repository_path(path) for path in declared_future):
        raise ValueError("unsafe declared future destination")
    skill_root = root / "plugins" / "shipworthy" / "skills"
    actual: set[str] = set()
    issues: list[str] = []
    for candidate in skill_root.rglob("*"):
        relative = candidate.relative_to(root).as_posix()
        if candidate.is_symlink():
            issues.append(f"symlink: {relative}")
        elif candidate.is_file():
            actual.add(relative)
    if mode == "transitional":
        undeclared = actual - approved - pending_removal
        if undeclared:
            issues.append(f"undeclared installed files: {sorted(undeclared)}")
        unexpected_missing = (approved - actual) - declared_future
        if unexpected_missing:
            issues.append(f"undeclared missing approved files: {sorted(unexpected_missing)}")
        already_present_future = declared_future & actual
        if already_present_future:
            issues.append(f"declared future files already present: {sorted(already_present_future)}")
    else:
        unexpected = actual - approved
        missing = approved - actual
        if unexpected:
            issues.append(f"unexpected final files: {sorted(unexpected)}")
        if missing:
            issues.append(f"missing approved files: {sorted(missing)}")
    forbidden_approved = [path for path in approved if not is_installed_inventory_path_allowed(path)]
    if forbidden_approved:
        issues.append(f"forbidden approved files: {sorted(forbidden_approved)}")
    return issues

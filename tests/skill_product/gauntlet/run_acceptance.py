#!/usr/bin/env python3
"""Prepare, finalize, or clean one native-Codex Gauntlet run."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

if __package__:
    from .acceptance_result import EXIT_CODES, atomic_final_result, validate_acceptance_result
    from .artifact_validation import ArtifactValidationError, validate_agent_artifacts
    from .compare_agent_result import compare_frontier, load_and_validate_oracle
else:  # Direct `python3 -I run_acceptance.py` execution.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from acceptance_result import EXIT_CODES, atomic_final_result, validate_acceptance_result
    from artifact_validation import ArtifactValidationError, validate_agent_artifacts
    from compare_agent_result import compare_frontier, load_and_validate_oracle


HERE = Path(__file__).resolve().parent
APP = HERE / "app"
ORACLE = HERE / "oracle/surface-oracle.json"
DEFECTS = HERE / "oracle/expected-defects.json"
SKILL_NAMES = (
    "ship-readiness-orchestrator",
    "ship-deep-review",
    "ship-product-workflows",
    "ship-workflow-clarity",
)
MAX_DIAGNOSTIC = 2_000
COMPARISON_KINDS = ("feature", "surface", "control", "transition")


def _json_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe_copy(source: Path, destination: Path) -> None:
    ignored = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "*.pyc", "*.pyo")
    shutil.copytree(source, destination, ignore=ignored)


def _wait_health(base_url: str, process: subprocess.Popen, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("fixture server exited during startup")
        try:
            with urllib.request.urlopen(base_url + "/health", timeout=0.25) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError("fixture server health check timed out")


def server_command(reset_token: str) -> list[str]:
    return [sys.executable, "-I", str(APP / "server.py"), "--port", "0", f"--reset-token={reset_token}"]


def prepare(args: argparse.Namespace) -> dict[str, Any]:
    output = Path(args.output).resolve()
    skills_source = Path(args.skills_source).resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory must be absent or empty")
    if args.mode == "runtime-only" and args.product_source:
        raise ValueError("--product-source is forbidden for runtime-only")
    if args.mode == "full-evidence" and not args.product_source:
        raise ValueError("--product-source is required for full-evidence")
    for name in SKILL_NAMES:
        if not (skills_source / name / "SKILL.md").is_file():
            raise ValueError(f"missing required skill: {name}")

    output.mkdir(parents=True, exist_ok=True)
    controller = Path(tempfile.mkdtemp(prefix="shipworthy-gauntlet-"))
    reset_token = secrets.token_urlsafe(24)
    copied_skills = controller / "skills"
    copied_skills.mkdir()
    skill_paths: list[str] = []
    for name in SKILL_NAMES:
        destination = copied_skills / name
        _safe_copy(skills_source / name, destination)
        skill_paths.append(str(destination / "SKILL.md"))
    workspace = controller / "workspace"
    workspace.mkdir()
    product_copy = None
    if args.mode == "full-evidence":
        product_copy = controller / "product"
        _safe_copy(Path(args.product_source).resolve(), product_copy)
    brief = controller / "brief.md"
    shutil.copy2(HERE / "prompts" / f"{args.mode}.md", brief)

    log = (output / "run.log").open("w", encoding="utf-8")
    process = subprocess.Popen(
        server_command(reset_token),
        cwd=APP, stdout=subprocess.PIPE, stderr=log, text=True, start_new_session=True,
    )
    try:
        line = process.stdout.readline() if process.stdout else ""
        server_data = json.loads(line)
        if process.stdout:
            process.stdout.close()
        _wait_health(server_data["base_url"], process)
    except Exception:
        process.terminate()
        process.wait(timeout=3)
        if process.stdout:
            process.stdout.close()
        log.close()
        shutil.rmtree(controller, ignore_errors=True)
        raise
    log.close()
    allowed = [*(str(Path(path).parent) for path in skill_paths), str(brief), str(workspace), str(output)]
    manifest: dict[str, Any] = {
        "schema_version": "shipworthy-gauntlet-run-v1",
        "mode": args.mode,
        "controller_root": str(controller),
        "workspace": str(workspace),
        "brief": str(brief),
        "skill_paths": skill_paths,
        "allowed_paths": allowed,
        "output": str(output),
        "base_url": server_data["base_url"],
        "accounts": {"member": "member@example.test", "admin": "admin@example.test"},
        "reset_token": reset_token,
        "reset_header": "X-Gauntlet-Reset",
        "reset_endpoint": "/api/reset",
        "server_pid": process.pid,
        "server_script": str(APP / "server.py"),
    }
    if product_copy:
        manifest["product_copy"] = str(product_copy)
        manifest["allowed_paths"].append(str(product_copy))
    _json_write(output / "run-manifest.json", manifest)
    return manifest


def _server_matches(manifest: dict[str, Any]) -> bool:
    pid = int(manifest.get("server_pid", 0))
    if pid <= 0:
        return False
    try:
        result = subprocess.run(["ps", "-p", str(pid), "-o", "command="], capture_output=True, text=True, timeout=2)
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0 and manifest.get("server_script", "") in result.stdout


def cleanup_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    pid = int(manifest.get("server_pid", 0))
    if _server_matches(manifest):
        try:
            os.kill(pid, signal.SIGTERM)
            for _ in range(60):
                if not _server_matches(manifest):
                    break
                time.sleep(0.05)
            else:
                errors.append("fixture process did not terminate")
        except OSError as error:
            if error.errno != 3:
                errors.append(f"fixture termination failed: {error}")
    controller = Path(manifest.get("controller_root", ""))
    if controller.name.startswith("shipworthy-gauntlet-") and controller.parent == Path(tempfile.gettempdir()):
        shutil.rmtree(controller, ignore_errors=True)
        if controller.exists():
            errors.append("controller cleanup failed")
    elif controller.exists():
        errors.append("refused unsafe controller cleanup path")
    return errors


def comparison_view(report: dict[str, Any], html: str, mode: str) -> dict[str, Any]:
    """Accept the canonical report wrapper while retaining legacy test packets."""
    source = report.get("source_ledger")
    if isinstance(source, dict) and isinstance(source.get("path_frontier"), dict):
        frontier = source["path_frontier"]
        rows = frontier.get("rows") if isinstance(frontier.get("rows"), list) else []
        summary = {kind: sum(row.get("kind") == kind for row in rows) for kind in COMPARISON_KINDS}
        view = {
            "mode": mode,
            "closure_state": frontier.get("closure_state"),
            "summary": summary,
            "rows": rows,
            "findings": source.get("findings") if isinstance(source.get("findings"), list) else [],
        }
    else:
        view = dict(report)
    closure = view.get("closure_state", "")
    view["html_closure_state"] = closure if f'data-closure-state="{closure}"' in html else "artifact-contradiction"
    return view


def finalize(args: argparse.Namespace) -> dict[str, Any]:
    manifest = json.loads(Path(args.run_manifest).read_text(encoding="utf-8"))
    output = Path(manifest["output"])
    dispatch = args.native_dispatch_status
    diagnostic = (args.coordinator_diagnostic or "")[:MAX_DIAGNOSTIC]
    packet = None
    failure_code = ""
    if dispatch == "completed":
        evidence = Path(args.agent_output)
        required = (evidence / "report-input.json", evidence / "readiness-ledger.json", evidence / "report.html")
        if not all(path.is_file() and path.stat().st_size for path in required):
            status, failure_code, diagnostic = "FAIL", "invalid-agent-artifacts", "required agent artifacts are missing or empty"
        else:
            try:
                report = validate_agent_artifacts(evidence)
            except ArtifactValidationError as error:
                status, failure_code = "FAIL", "invalid-agent-artifacts"
                diagnostic = str(error)[:MAX_DIAGNOSTIC]
            else:
                oracle, defects = load_and_validate_oracle(ORACLE, DEFECTS)
                packet = compare_frontier(report, oracle, defects, manifest["mode"])
                _json_write(output / "comparison-packet.json", packet)
                status = packet["status"]
                if status != "PASS":
                    failure_code = "comparison-not-pass"
    elif dispatch == "unavailable":
        status, failure_code = "NOT_PROVEN", "native-dispatch-unavailable"
    else:
        status, failure_code = "FAIL", f"native-dispatch-{dispatch}"
    cleanup_errors = cleanup_manifest(manifest)
    if cleanup_errors:
        status, failure_code = "FAIL", "cleanup-failed"
        diagnostic = "; ".join(cleanup_errors)
    artifacts = {
        "run_manifest": str(Path(args.run_manifest)),
        "agent_output": str(Path(args.agent_output)),
        "comparison_packet": str(output / "comparison-packet.json") if packet else "",
    }
    draft = {
        "schema_version": "shipworthy-gauntlet-acceptance-v1", "status": status,
        "mode": manifest["mode"], "native_dispatch_status": dispatch,
        "native_agent_id": args.native_agent_id or "", "failure_code": failure_code,
        "diagnostic": diagnostic, "comparison_status": packet["status"] if packet else "NOT_RUN",
        "oracle_blindness": "PROCEDURAL_ONLY", "filesystem_containment": "NOT_PROVEN",
        "artifacts": artifacts,
    }
    return atomic_final_result(output, draft)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    commands = root.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare")
    prepare_parser.add_argument("--mode", choices=("runtime-only", "full-evidence"), required=True)
    prepare_parser.add_argument("--skills-source", required=True)
    prepare_parser.add_argument("--output", required=True)
    prepare_parser.add_argument("--product-source")
    finalize_parser = commands.add_parser("finalize")
    finalize_parser.add_argument("--run-manifest", required=True)
    finalize_parser.add_argument("--native-dispatch-status", choices=("completed", "unavailable", "failed", "timeout"), required=True)
    finalize_parser.add_argument("--native-agent-id", default="")
    finalize_parser.add_argument("--agent-output", required=True)
    finalize_parser.add_argument("--coordinator-diagnostic")
    cleanup_parser = commands.add_parser("cleanup")
    cleanup_parser.add_argument("--run-manifest", required=True)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "prepare":
            print(json.dumps(prepare(args), sort_keys=True))
            return 0
        manifest = json.loads(Path(args.run_manifest).read_text(encoding="utf-8"))
        if args.command == "cleanup":
            errors = cleanup_manifest(manifest)
            if errors:
                print("; ".join(errors), file=sys.stderr)
                return 1
            return 0
        result = finalize(args)
        print(json.dumps(result, sort_keys=True))
        return EXIT_CODES[result["status"]]
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

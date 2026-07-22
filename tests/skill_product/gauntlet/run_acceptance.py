#!/usr/bin/env python3
"""Prepare, finalize, or clean one native-Codex Gauntlet run."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import tarfile
import time
import urllib.request
from pathlib import Path
from typing import Any

if __package__:
    from .acceptance_result import EXIT_CODES, atomic_final_result, validate_acceptance_result
    from .artifact_validation import ArtifactValidationError, validate_agent_artifacts
    from .compare_agent_result import compare_frontier, load_and_validate_oracle
    from .runtime_receipt import RuntimeReceipt, all_events, attempt_count, receipt_digest
else:  # Direct `python3 -I run_acceptance.py` execution.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from acceptance_result import EXIT_CODES, atomic_final_result, validate_acceptance_result
    from artifact_validation import ArtifactValidationError, validate_agent_artifacts
    from compare_agent_result import compare_frontier, load_and_validate_oracle
    from runtime_receipt import RuntimeReceipt, all_events, attempt_count, receipt_digest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
APP = HERE / "app"
ORACLE = HERE / "oracle/surface-oracle.json"
DEFECTS = HERE / "oracle/expected-defects.json"
RECEIPT_EXPECTATIONS = HERE / "oracle/receipt-expectations.json"
SKILL_NAMES = (
    "ship-readiness-orchestrator",
    "ship-deep-review",
    "ship-product-workflows",
    "ship-workflow-clarity",
)
MAX_DIAGNOSTIC = 2_000
COMPARISON_KINDS = ("feature", "surface", "control", "transition")


class EvaluationDriftError(ValueError):
    """Prepared evaluation inputs changed before authoritative finalization."""


def _json_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe_copy(source: Path, destination: Path) -> None:
    ignored = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "*.pyc", "*.pyo")
    shutil.copytree(source, destination, ignore=ignored)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(
        item for item in root.rglob("*")
        if item.is_file() and not item.is_symlink()
        and "__pycache__" not in item.parts and item.suffix not in {".pyc", ".pyo"}
    ):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        content = path.read_bytes()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _current_revision() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()


def _evaluation_fingerprints(
    *, revision: str, skills: Path, fixture: Path, brief: Path, product: Path | None = None,
) -> dict[str, Any]:
    values: dict[str, Any] = {
        "revision": revision,
        "subject_skills_revision": revision,
        "evaluation_revision": _current_revision(),
        "skill_tree_sha256": _tree_digest(skills),
        "fixture_tree_sha256": _tree_digest(fixture),
        "prompt_sha256": _sha256(brief),
        "comparator_sha256": _sha256(HERE / "compare_agent_result.py"),
        "oracle_sha256": {
            "surface": _sha256(ORACLE),
            "defects": _sha256(DEFECTS),
            "receipt_expectations": _sha256(RECEIPT_EXPECTATIONS),
        },
    }
    if product is not None:
        values["product_tree_sha256"] = _tree_digest(product)
    return values


def _verify_evaluation_fingerprints(manifest: dict[str, Any]) -> None:
    skill_paths = manifest.get("skill_paths")
    if not isinstance(skill_paths, list) or not skill_paths:
        raise EvaluationDriftError("prepared skill paths are missing")
    expected = manifest.get("evaluation_fingerprints")
    if not isinstance(expected, dict):
        raise EvaluationDriftError("prepared evaluation fingerprints are missing")
    skills = Path(skill_paths[0]).resolve().parents[1]
    fixture = Path(manifest["server_script"]).resolve().parent
    brief = Path(manifest["brief"]).resolve()
    product = Path(manifest["product_copy"]).resolve() if manifest.get("product_copy") else None
    actual = _evaluation_fingerprints(
        revision=str(expected.get("subject_skills_revision", expected.get("revision", ""))),
        skills=skills, fixture=fixture, brief=brief, product=product,
    )
    if actual != expected:
        differing = sorted(key for key in set(actual) | set(expected) if actual.get(key) != expected.get(key))
        raise EvaluationDriftError(f"evaluation input drift: {', '.join(differing[:4])}")


def _materialize_skills(revision: str, destination: Path) -> str:
    resolved = subprocess.run(
        ["git", "rev-parse", "--verify", f"{revision}^{{commit}}"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()
    archive = subprocess.run(
        ["git", "archive", "--format=tar", resolved, "plugins/shipworthy/skills"],
        cwd=ROOT, capture_output=True, check=True,
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
        members = bundle.getmembers()
        if any(member.name.startswith("/") or ".." in Path(member.name).parts or member.issym() or member.islnk() for member in members):
            raise ValueError("unsafe skill archive")
        bundle.extractall(destination.parent)
    materialized = destination.parent / "plugins/shipworthy/skills"
    materialized.rename(destination)
    shutil.rmtree(destination.parent / "plugins")
    return resolved


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


def server_command(reset_token: str, server_script: Path | None = None, receipt_path: Path | None = None, variant: str = "default") -> list[str]:
    command = [sys.executable, "-I", str(server_script or APP / "server.py"), "--port", "0", f"--reset-token={reset_token}"]
    if receipt_path is not None:
        command.append(f"--receipt={receipt_path}")
    command.append(f"--variant={variant}")
    return command


def prepare(args: argparse.Namespace) -> dict[str, Any]:
    output = Path(args.output).resolve()
    skills_source = Path(args.skills_source).resolve()
    canonical_skills = (ROOT / "plugins/shipworthy/skills").resolve()
    if skills_source != canonical_skills:
        raise ValueError("--skills-source must be the repository skill tree when --skills-revision is used")
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
    process: subprocess.Popen | None = None
    log = None
    try:
        reset_token = secrets.token_urlsafe(24)
        copied_skills = controller / "skills"
        resolved_revision = _materialize_skills(args.skills_revision, copied_skills)
        skill_paths = [str(copied_skills / name / "SKILL.md") for name in SKILL_NAMES]
        workspace = controller / "workspace"
        workspace.mkdir()
        agent_output = output / "agent-evidence"
        agent_output.mkdir()
        private = controller / "private"
        private.mkdir()
        receipt_path = private / "runtime-actions.json"
        app_copy = controller / "fixture"
        _safe_copy(APP, app_copy)
        shutil.copy2(HERE / "runtime_receipt.py", app_copy / "runtime_receipt.py")
        product_copy = None
        if args.mode == "full-evidence":
            product_copy = controller / "product"
            _safe_copy(Path(args.product_source).resolve(), product_copy)
            (product_copy / "variants.json").unlink(missing_ok=True)
        brief = controller / "brief.md"
        shutil.copy2(HERE / "prompts" / f"{args.mode}.md", brief)
        fingerprints = _evaluation_fingerprints(
            revision=resolved_revision, skills=copied_skills, fixture=app_copy,
            brief=brief, product=product_copy,
        )

        log = (output / "run.log").open("w", encoding="utf-8")
        process = subprocess.Popen(
            server_command(reset_token, app_copy / "server.py", receipt_path, args.variant),
            cwd=app_copy, stdout=subprocess.PIPE, stderr=log, text=True, start_new_session=True,
        )
        line = process.stdout.readline() if process.stdout else ""
        server_data = json.loads(line)
        if process.stdout:
            process.stdout.close()
        _wait_health(server_data["base_url"], process)
        log.close()
        log = None
        allowed = [*(str(Path(path).parent) for path in skill_paths), str(brief), str(workspace), str(agent_output)]
        manifest: dict[str, Any] = {
            "schema_version": "shipworthy-gauntlet-run-v1", "mode": args.mode,
            "controller_root": str(controller), "workspace": str(workspace), "brief": str(brief),
            "skill_paths": skill_paths, "allowed_paths": allowed, "output": str(output),
            "agent_output": str(agent_output), "base_url": server_data["base_url"],
            "accounts": {"member": "member@example.test", "admin": "admin@example.test"},
            "reset_token": reset_token, "reset_header": "X-Gauntlet-Reset", "reset_endpoint": "/api/reset",
            "server_pid": process.pid, "server_script": str(app_copy / "server.py"),
            "evaluation_fingerprints": fingerprints,
        }
        if product_copy:
            manifest["product_copy"] = str(product_copy)
            manifest["allowed_paths"].append(str(product_copy))
        _json_write(output / "run-manifest.json", manifest)
        return manifest
    except Exception:
        if process is not None:
            if process.stdout:
                process.stdout.close()
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
        if log is not None and not log.closed:
            log.close()
        shutil.rmtree(controller, ignore_errors=True)
        shutil.rmtree(output, ignore_errors=True)
        raise


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


def _finalize_prepared(args: argparse.Namespace) -> dict[str, Any]:
    manifest = json.loads(Path(args.run_manifest).read_text(encoding="utf-8"))
    output = Path(manifest["output"])
    dispatch = args.native_dispatch_status
    diagnostic = (args.coordinator_diagnostic or "")[:MAX_DIAGNOSTIC]
    packet = None
    receipt = None
    retained_receipt = ""
    failure_code = ""
    _verify_evaluation_fingerprints(manifest)
    if dispatch == "completed":
        private_receipt = Path(manifest["controller_root"]) / "private" / "runtime-actions.json"
        if private_receipt.is_file():
            receipt = RuntimeReceipt(private_receipt).read()
            retained = output / "controller-receipt.json"
            _json_write(retained, receipt)
            retained_receipt = str(retained)
        evidence = Path(args.agent_output)
        if evidence.resolve() != Path(manifest["agent_output"]).resolve():
            status, failure_code, diagnostic = "FAIL", "invalid-agent-output-path", "agent output is outside the prepared evidence directory"
        else:
            required = (evidence / "report-input.json", evidence / "readiness-ledger.json", evidence / "report.html")
        if failure_code == "invalid-agent-output-path":
            pass
        elif not all(path.is_file() and path.stat().st_size for path in required):
            status, failure_code, diagnostic = "FAIL", "invalid-agent-artifacts", "required agent artifacts are missing or empty"
        else:
            try:
                report = validate_agent_artifacts(evidence)
            except ArtifactValidationError as error:
                status, failure_code = "FAIL", "invalid-agent-artifacts"
                diagnostic = str(error)[:MAX_DIAGNOSTIC]
            else:
                oracle, defects = load_and_validate_oracle(ORACLE, DEFECTS)
                if receipt is None:
                    raise ValueError("controller receipt is missing")
                expectation_document = json.loads(RECEIPT_EXPECTATIONS.read_text(encoding="utf-8"))
                if expectation_document.get("schema_version") != "shipworthy-receipt-expectations-v1" or not isinstance(expectation_document.get("expectations"), dict):
                    raise ValueError("invalid private receipt expectations")
                receipt_events = all_events(receipt)
                packet = compare_frontier(
                    report,
                    oracle,
                    defects,
                    manifest["mode"],
                    receipt_events=receipt_events,
                    receipt_expectations=expectation_document["expectations"],
                )
                packet["receipt"] = {"digest": receipt_digest(receipt), "epoch_count": len(receipt["epochs"]), "event_count": len(receipt_events)}
                packet["receipt"]["attempt_count"] = attempt_count(receipt_events)
                packet["evaluation_fingerprints"] = manifest["evaluation_fingerprints"]
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
        "controller_receipt": retained_receipt,
        "controller_receipt_sha256": _sha256(Path(retained_receipt)) if retained_receipt else "",
        "evaluation_fingerprints": manifest.get("evaluation_fingerprints", {}),
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


def finalize(args: argparse.Namespace) -> dict[str, Any]:
    """Finalize atomically and clean private state even on unexpected failures."""
    manifest: dict[str, Any] = {}
    output = Path(args.run_manifest).resolve().parent
    try:
        manifest = json.loads(Path(args.run_manifest).read_text(encoding="utf-8"))
        output = Path(manifest.get("output", output)).resolve()
        return _finalize_prepared(args)
    except Exception as error:
        cleanup_errors = cleanup_manifest(manifest) if manifest else []
        failure_code = "evaluation-input-drift" if isinstance(error, EvaluationDriftError) else "internal-finalize-error"
        diagnostic = str(error)[:MAX_DIAGNOSTIC]
        if cleanup_errors:
            failure_code = "cleanup-failed"
            diagnostic = "; ".join(cleanup_errors)[:MAX_DIAGNOSTIC]
        draft = {
            "schema_version": "shipworthy-gauntlet-acceptance-v1", "status": "FAIL",
            "mode": manifest.get("mode") if manifest.get("mode") in {"runtime-only", "full-evidence"} else "internal",
            "native_dispatch_status": "internal", "native_agent_id": args.native_agent_id or "",
            "failure_code": failure_code, "diagnostic": diagnostic,
            "comparison_status": "NOT_RUN", "oracle_blindness": "PROCEDURAL_ONLY",
            "filesystem_containment": "NOT_PROVEN", "artifacts": {},
        }
        output.mkdir(parents=True, exist_ok=True)
        return atomic_final_result(output, draft)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    commands = root.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare")
    prepare_parser.add_argument("--mode", choices=("runtime-only", "full-evidence"), required=True)
    prepare_parser.add_argument("--skills-source", required=True)
    prepare_parser.add_argument("--skills-revision", required=True)
    prepare_parser.add_argument("--output", required=True)
    prepare_parser.add_argument("--product-source")
    prepare_parser.add_argument("--variant", default="default")
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

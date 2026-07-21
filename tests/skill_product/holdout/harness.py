#!/usr/bin/env python3
"""Controller-private holdout preparation using an exact frozen skill revision."""

from __future__ import annotations

import io
import json
import os
import secrets
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path


STARTING_REVISION = "4651c8d1cd006230788d0d37f0e3fc312e5fbe48"
SKILL_NAMES = ("ship-readiness-orchestrator", "ship-deep-review", "ship-product-workflows", "ship-workflow-clarity")
_PROCESSES: dict[int, subprocess.Popen] = {}


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _materialize(repo: Path, revision: str, controller: Path) -> Path:
    archive = subprocess.run(
        ["git", "archive", "--format=tar", revision, "plugins/shipworthy/skills"],
        cwd=repo, capture_output=True, check=True,
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
        members = bundle.getmembers()
        if any(member.name.startswith("/") or ".." in Path(member.name).parts or member.issym() or member.islnk() for member in members):
            raise ValueError("unsafe frozen skill archive")
        bundle.extractall(controller)
    return controller / "plugins/shipworthy/skills"


def _wait(base_url: str, process: subprocess.Popen) -> None:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if process.poll() is not None: raise RuntimeError("holdout server exited")
        try:
            with urllib.request.urlopen(base_url + "/health", timeout=.25) as response:
                if response.status == 200: return
        except OSError: time.sleep(.05)
    raise RuntimeError("holdout health timeout")


def prepare(repo: Path, output: Path, *, skills_revision: str) -> dict:
    repo, output = Path(repo).resolve(), Path(output).resolve()
    if output.exists() and any(output.iterdir()): raise ValueError("output must be absent or empty")
    output.mkdir(parents=True, exist_ok=True)
    agent_output = output / "agent-evidence"; agent_output.mkdir()
    controller = Path(tempfile.mkdtemp(prefix="shipworthy-holdout-"))
    skills = _materialize(repo, skills_revision, controller)
    app = controller / "app"
    shutil.copytree(repo / "tests/skill_product/holdout/app", app)
    shutil.copy2(repo / "tests/skill_product/gauntlet/runtime_receipt.py", app / "runtime_receipt.py")
    brief = controller / "brief.md"; shutil.copy2(repo / "tests/skill_product/holdout/prompt.md", brief)
    workspace = controller / "workspace"; workspace.mkdir()
    private = controller / "private"; private.mkdir()
    token = secrets.token_urlsafe(24)
    log = (output / "run.log").open("w", encoding="utf-8")
    process = subprocess.Popen(
        [sys.executable, "-I", str(app / "server.py"), "--port", "0", f"--reset-token={token}", f"--receipt={private / 'runtime-actions.json'}"],
        cwd=app, stdout=subprocess.PIPE, stderr=log, text=True, start_new_session=True,
    )
    try:
        line = process.stdout.readline() if process.stdout else ""
        server = json.loads(line)
        if process.stdout: process.stdout.close()
        _wait(server["base_url"], process)
    except Exception:
        process.terminate(); process.wait(timeout=3); log.close(); shutil.rmtree(controller, ignore_errors=True); raise
    log.close()
    _PROCESSES[process.pid] = process
    paths = [str(skills / name / "SKILL.md") for name in SKILL_NAMES]
    manifest = {
        "schema_version": "shipworthy-holdout-run-v1", "controller_root": str(controller),
        "base_url": server["base_url"], "server_pid": process.pid, "server_script": str(app / "server.py"),
        "brief": str(brief), "workspace": str(workspace), "skill_paths": paths,
        "agent_output": str(agent_output),
        "allowed_paths": [*(str(Path(path).parent) for path in paths), str(brief), str(workspace), str(agent_output)],
        "reset_header": "X-Holdout-Reset", "reset_token": token, "reset_endpoint": "/api/reset",
        "skills_revision": skills_revision,
    }
    _write(output / "run-manifest.json", manifest)
    return manifest


def cleanup(manifest: dict) -> None:
    pid = int(manifest.get("server_pid", 0))
    process = _PROCESSES.pop(pid, None)
    if pid > 0:
        try: os.kill(pid, signal.SIGTERM)
        except OSError: pass
        for _ in range(60):
            try:
                reaped, _status = os.waitpid(pid, os.WNOHANG)
                if reaped == pid: break
            except ChildProcessError:
                break
            time.sleep(.05)
        else:
            try: os.kill(pid, signal.SIGKILL)
            except OSError: pass
            try: os.waitpid(pid, 0)
            except ChildProcessError: pass
        if process is not None:
            process.returncode = process.poll()
    controller = Path(manifest.get("controller_root", ""))
    if controller.name.startswith("shipworthy-holdout-") and controller.parent == Path(tempfile.gettempdir()):
        shutil.rmtree(controller, ignore_errors=True)

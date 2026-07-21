#!/usr/bin/env python3
"""Deterministic localhost-only server for the Shipworthy Gauntlet fixture."""

from __future__ import annotations

import argparse
import copy
import json
import mimetypes
import signal
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent))
from runtime_receipt import ReceiptError, RuntimeReceipt


SEED = json.loads((ROOT / "fixtures/seed.json").read_text(encoding="utf-8"))
VARIANT_DOCUMENT = json.loads((ROOT / "variants.json").read_text(encoding="utf-8"))
DEFAULT_BEHAVIORS = {"save_persists": False, "disabled_recovery": False, "keyboard_command": True, "truthful_failure": False}
SPA_ROUTES = {"/", "/dashboard", "/projects", "/projects/import", "/settings/profile", "/admin/data", "/team"}
STATIC_FILES = {"/activity.js": ROOT / "activity.js", "/app.js": ROOT / "app.js", "/styles.css": ROOT / "styles.css"}


class State:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.reset()

    def reset(self) -> dict:
        with getattr(self, "lock", threading.Lock()):
            self.value = copy.deepcopy(SEED)
            return copy.deepcopy(self.value)

    def snapshot(self) -> dict:
        with self.lock:
            return copy.deepcopy(self.value)


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, handler, reset_token: str, receipt_path: Path, variant: str):
        super().__init__(address, handler)
        self.reset_token = reset_token
        self.state = State()
        self.receipt = RuntimeReceipt(receipt_path)
        if variant == "default":
            selected = {}
        else:
            selected = VARIANT_DOCUMENT.get("variants", {}).get(variant)
            if not isinstance(selected, dict):
                raise ValueError("unknown fixture variant")
        self.behaviors = {**DEFAULT_BEHAVIORS, **selected}


class Handler(BaseHTTPRequestHandler):
    server: Server

    def log_message(self, format: str, *args) -> None:
        return

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        try:
            length = min(int(self.headers.get("Content-Length", "0")), 32_768)
            value = json.loads(self.rfile.read(length) or b"{}")
            return value if isinstance(value, dict) else {}
        except (ValueError, json.JSONDecodeError):
            return {}

    def do_GET(self) -> None:
        raw_path = urlsplit(self.path).path
        if ".." in raw_path.split("/"):
            self._json(400, {"error": "invalid-path"})
            return
        if raw_path == "/health":
            self._json(200, {"status": "ok"})
            return
        if raw_path == "/api/state":
            self._json(200, self.server.state.snapshot())
            return
        if raw_path in STATIC_FILES:
            self._file(STATIC_FILES[raw_path])
            return
        if raw_path in SPA_ROUTES:
            self._file(ROOT / "index.html")
            return
        body = b"<!doctype html><html lang='en'><title>Page not found</title><h1>Page not found</h1><p>Return to <a href='/dashboard'>the dashboard</a>.</p></html>"
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path: Path) -> None:
        if path == ROOT / "index.html" and self.server.behaviors["disabled_recovery"]:
            source = path.read_text(encoding="utf-8")
            marker = '<button disabled title="Unavailable">Archive</button>'
            replacement = '<button disabled title="Unavailable. Ask a workspace owner to enable project archiving." aria-describedby="archive-guidance">Archive</button><p id="archive-guidance">Ask a workspace owner to enable project archiving.</p>'
            body = source.replace(marker, replacement).encode()
        elif path == ROOT / "app.js" and not self.server.behaviors["keyboard_command"]:
            body = path.read_text(encoding="utf-8").replace("const keyboardCommandEnabled = true;", "const keyboardCommandEnabled = false;").encode()
        else:
            body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        body = self._body()
        if path == "/api/reset":
            if self.headers.get("X-Gauntlet-Reset") != self.server.reset_token:
                self._json(403, {"error": "reset-token-required"})
            else:
                state = self.server.state.reset()
                self.server.receipt.reset()
                self._json(200, state)
            return
        if path == "/api/activity":
            try:
                self.server.receipt.append(body)
            except ReceiptError as error:
                self._json(400, {"error": str(error)[:160]})
            else:
                self._json(202, {"accepted": True})
            return
        if path == "/api/save":
            name = str(body.get("name", "")).strip()
            if not name:
                self._json(422, {"error": "name-required"})
                return
            with self.server.state.lock:
                self.server.state.value["project"]["name"] = name
            self._json(200, {"ok": True, "persisted": True})
            return
        if path == "/api/save-failure":
            if self.server.behaviors["save_persists"]:
                name = str(body.get("name", "")).strip()
                with self.server.state.lock:
                    self.server.state.value["project"]["name"] = name
                self._json(200, {"ok": True, "persisted": True, "effect": "success-with-persistence"})
            elif self.server.behaviors["truthful_failure"]:
                self._json(409, {"ok": False, "persisted": False, "effect": "failure-without-persistence"})
            else:
                self._json(200, {"ok": True, "persisted": False, "effect": "success-without-persistence"})
            return
        if path == "/api/projects":
            name = str(body.get("name", "")).strip()
            if not name:
                self._json(422, {"error": "name-required"})
            else:
                with self.server.state.lock:
                    self.server.state.value["projects"].append(name)
                    self.server.state.value["project"]["name"] = name
                    self.server.state.value["project"]["state"] = "draft"
                self._json(201, {"ok": True, "name": name})
            return
        if path == "/api/import":
            valid = (
                set(body) == set(SEED)
                and isinstance(body.get("project"), dict)
                and isinstance(body.get("projects"), list)
                and isinstance(body.get("invites"), list)
                and isinstance(body.get("session"), str)
                and isinstance(body.get("feature_flags"), dict)
                and isinstance(body.get("empty_archived_projects"), bool)
            )
            if not valid:
                self._json(422, {"error": "complete-export-required"})
            else:
                with self.server.state.lock:
                    self.server.state.value = copy.deepcopy(body)
                self._json(200, {"ok": True, "restored": True})
            return
        if path == "/api/duplicate":
            with self.server.state.lock:
                source = self.server.state.value["project"]["name"]
                name = f"{source} copy"
                self.server.state.value["projects"].append(name)
                self.server.state.value["project"]["name"] = name
                self.server.state.value["project"]["state"] = "draft"
            self._json(201, {"ok": True, "name": name})
            return
        if path == "/api/select":
            name = str(body.get("name", ""))
            with self.server.state.lock:
                if name not in self.server.state.value["projects"]:
                    self._json(404, {"error": "project-not-found"})
                    return
                self.server.state.value["project"]["name"] = name
            self._json(200, {"ok": True, "name": name})
            return
        if path == "/api/invite":
            email = str(body.get("email", "")).strip()
            if "@" not in email:
                self._json(422, {"error": "valid-email-required"})
            else:
                with self.server.state.lock:
                    self.server.state.value["invites"].append(email)
                self._json(200, {"ok": True, "email": email})
            return
        if path == "/api/stale":
            with self.server.state.lock:
                self.server.state.value["session"] = "expired"
            self._json(401, {"error": "session-expired"})
            return
        if path == "/api/reauthenticate":
            with self.server.state.lock:
                self.server.state.value["session"] = "active"
            self._json(200, {"ok": True, "session": "active"})
            return
        if path == "/api/publish":
            name = str(body.get("name", "")).strip()
            if not name:
                self._json(409, {"error": "name-prerequisite"})
            else:
                with self.server.state.lock:
                    previous = self.server.state.value["project"]["name"]
                    projects = self.server.state.value["projects"]
                    if previous in projects:
                        projects[projects.index(previous)] = name
                    self.server.state.value["project"]["name"] = name
                    self.server.state.value["project"]["state"] = "published"
                self._json(200, {"ok": True, "state": "published"})
            return
        self._json(404, {"error": "not-found"})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--reset-token", required=True)
    parser.add_argument("--receipt")
    parser.add_argument("--variant", default="default")
    args = parser.parse_args()
    temporary_receipt = None
    if args.receipt:
        receipt_path = Path(args.receipt)
    else:
        temporary_receipt = tempfile.TemporaryDirectory(prefix="shipworthy-fixture-receipt-")
        receipt_path = Path(temporary_receipt.name) / "runtime-actions.json"
    server = Server(("127.0.0.1", args.port), Handler, args.reset_token, receipt_path, args.variant)
    stop = threading.Event()

    def request_stop(*_args) -> None:
        if not stop.is_set():
            stop.set()
            threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    print(json.dumps({"base_url": f"http://127.0.0.1:{server.server_port}", "port": server.server_port}), flush=True)
    try:
        server.serve_forever(poll_interval=0.05)
    finally:
        server.server_close()
        if temporary_receipt is not None:
            temporary_receipt.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

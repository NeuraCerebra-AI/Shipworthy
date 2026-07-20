#!/usr/bin/env python3
"""Deterministic localhost-only server for the Shipworthy Gauntlet fixture."""

from __future__ import annotations

import argparse
import copy
import json
import mimetypes
import signal
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
SEED = json.loads((ROOT / "fixtures/seed.json").read_text(encoding="utf-8"))
SPA_ROUTES = {"/", "/dashboard", "/projects", "/projects/import", "/settings/profile", "/admin/data", "/team"}
STATIC_FILES = {"/app.js": ROOT / "app.js", "/styles.css": ROOT / "styles.css"}


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

    def __init__(self, address, handler, reset_token: str):
        super().__init__(address, handler)
        self.reset_token = reset_token
        self.state = State()


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
        self._json(404, {"error": "not-found"})

    def _file(self, path: Path) -> None:
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
                self._json(200, self.server.state.reset())
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
            self._json(200, {"ok": True, "persisted": False, "effect": "success-without-persistence"})
            return
        if path == "/api/projects":
            name = str(body.get("name", "")).strip()
            if not name:
                self._json(422, {"error": "name-required"})
            else:
                with self.server.state.lock:
                    self.server.state.value["projects"].append(name)
                self._json(201, {"ok": True, "name": name})
            return
        if path == "/api/duplicate":
            with self.server.state.lock:
                self.server.state.value["projects"].append("Alpha copy")
            self._json(201, {"ok": True, "name": "Alpha copy"})
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
                    self.server.state.value["project"]["name"] = name
                    self.server.state.value["project"]["state"] = "published"
                self._json(200, {"ok": True, "state": "published"})
            return
        self._json(404, {"error": "not-found"})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--reset-token", required=True)
    args = parser.parse_args()
    server = Server(("127.0.0.1", args.port), Handler, args.reset_token)
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

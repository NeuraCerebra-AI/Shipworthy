#!/usr/bin/env python3
"""Local dependency-free server for the blind Waypoint holdout."""

from __future__ import annotations

import argparse
import copy
import json
import mimetypes
import signal
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from runtime_receipt import ReceiptError, RuntimeReceipt

SEED = {"name": "", "branch": "", "permission": "editor", "session": "active", "created": False}
ROUTES = {"/", "/welcome", "/onboarding", "/complete"}
STATIC = {"/app.js": ROOT / "app.js", "/telemetry.js": ROOT / "telemetry.js", "/styles.css": ROOT / "styles.css"}


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, token: str, receipt_path: Path):
        super().__init__(address, Handler)
        self.token = token
        self.receipt = RuntimeReceipt(receipt_path)
        self.lock = threading.Lock()
        self.state = copy.deepcopy(SEED)

    def reset(self):
        with self.lock:
            self.state = copy.deepcopy(SEED)
        self.receipt.reset()
        return copy.deepcopy(self.state)


class Handler(BaseHTTPRequestHandler):
    server: Server

    def log_message(self, *_args): return
    def json(self, status: int, value: dict):
        body = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(body))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(body)
    def body(self):
        try:
            size = min(int(self.headers.get("Content-Length", "0")), 32768)
            value = json.loads(self.rfile.read(size) or b"{}")
            return value if isinstance(value, dict) else {}
        except (ValueError, json.JSONDecodeError): return {}
    def file(self, path: Path):
        body = path.read_bytes(); self.send_response(200); self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream"); self.send_header("Content-Length", str(len(body))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/health": return self.json(200, {"status": "ok"})
        if path == "/api/state":
            with self.server.lock: return self.json(200, copy.deepcopy(self.server.state))
        if path in STATIC: return self.file(STATIC[path])
        if path in ROUTES: return self.file(ROOT / "index.html")
        return self.json(404, {"error": "not-found"})
    def do_POST(self):
        path, body = urlsplit(self.path).path, self.body()
        if path == "/api/activity":
            try: self.server.receipt.append(body)
            except ReceiptError as error: return self.json(400, {"error": str(error)[:160]})
            return self.json(202, {"accepted": True})
        if path == "/api/reset":
            if self.headers.get("X-Holdout-Reset") != self.server.token: return self.json(403, {"error": "reset-token-required"})
            return self.json(200, self.server.reset())
        if path == "/api/draft":
            name, branch = str(body.get("name", "")).strip(), str(body.get("branch", ""))
            if not name or branch not in {"guided", "manual"}: return self.json(422, {"error": "complete-draft-required"})
            with self.server.lock: self.server.state.update(name=name, branch=branch)
            return self.json(200, {"ok": True})
        if path == "/api/revoke":
            with self.server.lock: self.server.state["permission"] = "viewer"
            return self.json(200, {"ok": True, "permission": "viewer"})
        if path == "/api/expire":
            with self.server.lock: self.server.state["session"] = "expired"
            return self.json(200, {"ok": True, "session": "expired"})
        if path == "/api/submit":
            time.sleep(0.05)
            with self.server.lock:
                if self.server.state["permission"] != "editor": return self.json(403, {"error": "permission-revoked"})
                if self.server.state["session"] != "active": return self.json(401, {"error": "session-expired"})
                self.server.state["created"] = True
            return self.json(201, {"ok": True})
        return self.json(404, {"error": "not-found"})


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--port", type=int, default=0); parser.add_argument("--reset-token", required=True); parser.add_argument("--receipt", required=True); args = parser.parse_args()
    server = Server(("127.0.0.1", args.port), args.reset_token, Path(args.receipt)); stopped = threading.Event()
    def stop(*_args):
        if not stopped.is_set(): stopped.set(); threading.Thread(target=server.shutdown, daemon=True).start()
    signal.signal(signal.SIGTERM, stop); signal.signal(signal.SIGINT, stop)
    print(json.dumps({"base_url": f"http://127.0.0.1:{server.server_port}", "port": server.server_port}), flush=True)
    try: server.serve_forever(poll_interval=0.05)
    finally: server.server_close()
    return 0


if __name__ == "__main__": raise SystemExit(main())

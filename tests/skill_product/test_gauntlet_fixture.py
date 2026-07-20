from __future__ import annotations

import json
import subprocess
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "tests/skill_product/gauntlet/app"
SERVER = APP / "server.py"
ORACLE = ROOT / "tests/skill_product/gauntlet/oracle/surface-oracle.json"


class FixtureProcess:
    def __init__(self, reset_token: str = "fixture-reset-token") -> None:
        self.reset_token = reset_token
        self.process = subprocess.Popen(
            ["python3", "-I", str(SERVER), "--port", "0", "--reset-token", reset_token],
            cwd=APP,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        line = self.process.stdout.readline()
        self.manifest = json.loads(line)
        self.base = self.manifest["base_url"]

    def request(self, path: str, method: str = "GET", payload: dict | None = None, token: str | None = None):
        body = None if payload is None else json.dumps(payload).encode()
        request = urllib.request.Request(self.base + path, data=body, method=method)
        if body is not None:
            request.add_header("Content-Type", "application/json")
        if token is not None:
            request.add_header("X-Gauntlet-Reset", token)
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=3)
        if self.process.poll() is None:
            self.process.kill()
        if self.process.stdout:
            self.process.stdout.close()
        if self.process.stderr:
            self.process.stderr.close()


class GauntletFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = FixtureProcess()

    def tearDown(self) -> None:
        self.fixture.stop()
        self.fixture.stop()

    def test_random_port_health_and_deterministic_state(self) -> None:
        self.assertNotEqual(0, self.fixture.manifest["port"])
        self.assertEqual((200, {"status": "ok"}), self.fixture.request("/health"))
        first = self.fixture.request("/api/state")
        second = self.fixture.request("/api/state")
        self.assertEqual(first, second)
        self.assertEqual("Alpha", first[1]["project"]["name"])

    def test_reset_requires_token_and_restores_seed(self) -> None:
        self.assertEqual(403, self.fixture.request("/api/reset", "POST", {}, "wrong")[0])
        self.fixture.request("/api/save", "POST", {"name": "Changed"})
        self.assertEqual("Changed", self.fixture.request("/api/state")[1]["project"]["name"])
        self.assertEqual(200, self.fixture.request("/api/reset", "POST", {}, self.fixture.reset_token)[0])
        self.assertEqual("Alpha", self.fixture.request("/api/state")[1]["project"]["name"])

    def test_failure_misleading_success_and_reload_loss_are_deterministic(self) -> None:
        status, response = self.fixture.request("/api/save-failure", "POST", {"name": "Lost"})
        self.assertEqual(200, status)
        self.assertEqual({"ok": True, "persisted": False, "effect": "success-without-persistence"}, response)
        self.assertEqual("Alpha", self.fixture.request("/api/state")[1]["project"]["name"])

    def test_invalid_input_and_stale_session_have_recovery_transitions(self) -> None:
        self.assertEqual(422, self.fixture.request("/api/projects", "POST", {"name": " "})[0])
        self.assertEqual(201, self.fixture.request("/api/projects", "POST", {"name": "Recovered"})[0])
        self.assertIn("Recovered", self.fixture.request("/api/state")[1]["projects"])
        self.assertEqual(401, self.fixture.request("/api/stale", "POST", {})[0])
        self.assertEqual(200, self.fixture.request("/api/reauthenticate", "POST", {})[0])

    def test_static_paths_cannot_escape_fixture_root(self) -> None:
        self.assertIn(self.fixture.request("/../../../../etc/passwd")[0], (400, 404))

    def test_every_oracle_case_has_a_fixture_hook_and_decoys_are_noninteractive(self) -> None:
        oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
        source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (APP / "index.html", APP / "app.js", APP / "product-docs/README.md", APP / "product-tests/contract.md", APP / "fixtures/seed.json")
        )
        for item in oracle["items"]:
            self.assertIn(item["case_id"], source, item["id"])
        html = (APP / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-decoy="negative-control"', html)
        self.assertNotIn('data-decoy="negative-control" role="button"', html)
        self.assertIn('data-case-id="false-affordance"', html)
        false_fragment = html.split('data-case-id="false-affordance"', 1)[1].split("</div>", 1)[0]
        self.assertNotIn("<button", false_fragment)
        self.assertNotIn("onclick", false_fragment)

    def test_material_fixture_controls_are_oracled_and_files_stay_bounded(self) -> None:
        oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
        case_ids = {item["case_id"] for item in oracle["items"]}
        html = (APP / "index.html").read_text(encoding="utf-8")
        import re
        hooks = set(re.findall(r'data-case-id="([^"]+)"', html))
        self.assertTrue(hooks.issubset(case_ids), hooks - case_ids)
        for button in re.findall(r"<button\b[^>]*>", html):
            self.assertTrue("data-case-id=" in button or "data-supporting-control=" in button, button)
            if "data-supporting-control=" in button:
                self.assertIn("data-expected-effect=", button, button)
        self.assertIn('id="profile"', html)
        self.assertIn('data-supporting-control="role-admin"', html)
        self.assertNotIn("@media (max-width: 600px) { nav { display: none;", (APP / "styles.css").read_text(encoding="utf-8"))
        for path in (SERVER, APP / "app.js"):
            logical = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]
            self.assertLessEqual(len(logical), 300, path)


if __name__ == "__main__":
    unittest.main()

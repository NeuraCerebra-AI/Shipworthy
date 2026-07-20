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

    def test_supporting_duplicate_invite_and_publish_behaviors_are_real(self) -> None:
        self.assertEqual(201, self.fixture.request("/api/duplicate", "POST", {})[0])
        self.assertIn("Alpha copy", self.fixture.request("/api/state")[1]["projects"])
        self.assertEqual(422, self.fixture.request("/api/invite", "POST", {"email": ""})[0])
        self.assertEqual(200, self.fixture.request("/api/invite", "POST", {"email": "person@example.test"})[0])
        self.assertIn("person@example.test", self.fixture.request("/api/state")[1]["invites"])
        self.assertEqual(409, self.fixture.request("/api/publish", "POST", {"name": ""})[0])
        self.assertEqual(200, self.fixture.request("/api/publish", "POST", {"name": "Ready"})[0])
        state = self.fixture.request("/api/state")[1]
        self.assertEqual("published", state["project"]["state"])
        self.assertEqual("Ready", state["project"]["name"])

    def test_export_import_round_trip_restores_the_complete_fixture_state(self) -> None:
        self.fixture.request("/api/projects", "POST", {"name": "Round Trip"})
        self.fixture.request("/api/publish", "POST", {"name": "Published Name"})
        exported = self.fixture.request("/api/state")[1]
        self.fixture.request("/api/reset", "POST", {}, self.fixture.reset_token)
        self.assertEqual(422, self.fixture.request("/api/import", "POST", {"project": "partial"})[0])
        self.assertEqual(200, self.fixture.request("/api/import", "POST", exported)[0])
        self.assertEqual(exported, self.fixture.request("/api/state")[1])

    def test_static_paths_cannot_escape_fixture_root(self) -> None:
        self.assertIn(self.fixture.request("/../../../../etc/passwd")[0], (400, 404))

    def test_unknown_browser_route_is_human_readable_html(self) -> None:
        request = urllib.request.Request(self.fixture.base + "/not-a-real-route")
        with self.assertRaises(urllib.error.HTTPError) as raised:
            urllib.request.urlopen(request, timeout=3)
        self.assertEqual(404, raised.exception.code)
        self.assertIn("text/html", raised.exception.headers.get("Content-Type", ""))
        self.assertIn("Page not found", raised.exception.read().decode())

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
        self.assertIn('aria-label="Synthetic audit role"', html)
        self.assertIn('id="invite-permission"', html)
        self.assertIn('<output id="profile-name"', html)
        self.assertNotIn('<input id="profile-name"', html)
        self.assertIn('id="cancel-create"', html)
        self.assertIn('id="pending-invites"', html)
        self.assertIn('id="project-actions"', html)
        self.assertIn('id="project-state"', html)
        self.assertNotIn("Avatar and profile preferences are managed here", html)
        self.assertIn('id="admin-permission"', html)
        self.assertIn('id="import-file"', html)
        script = (APP / "app.js").read_text(encoding="utf-8")
        self.assertIn('event.key === "Enter" || (event.shiftKey && event.key === "F10")', script)
        self.assertIn('/api/duplicate', script)
        self.assertIn('/api/invite', script)
        self.assertIn("Invalid JSON export", script)
        self.assertIn('function closePalette()', script)
        self.assertIn('function closeProjectForm()', script)
        self.assertIn('state.invites.join(", ")', script)
        self.assertIn('api("/api/import", value)', script)
        self.assertIn('show($("#project-form"), false)', script)
        self.assertIn('$("#new-name").value = ""', script)
        self.assertIn('id="import-file" type="file" accept="application/json" aria-describedby="import-guidance import-status"', html)
        self.assertIn('id="import-guidance"', html)
        self.assertNotIn("Export file <input", html)
        self.assertIn('function openInviteDialog()', script)
        self.assertIn('function closeInviteDialog()', script)
        self.assertIn('$("#avatar-menu")?.querySelector("a")?.focus()', script)
        self.assertIn('show($("#invite-permission"), role !== "admin")', script)
        self.assertIn('$("#project-state").textContent', script)
        self.assertIn('$("#project-actions")?.addEventListener', script)
        self.assertNotIn("@media (max-width: 600px) { nav { display: none;", (APP / "styles.css").read_text(encoding="utf-8"))
        self.assertIn("#avatar { margin-left: 0; }", (APP / "styles.css").read_text(encoding="utf-8"))
        for path in (SERVER, APP / "app.js"):
            logical = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]
            self.assertLessEqual(len(logical), 300, path)

    def test_supporting_forms_have_named_dialog_and_associated_validation(self) -> None:
        html = (APP / "index.html").read_text(encoding="utf-8")
        script = (APP / "app.js").read_text(encoding="utf-8")
        self.assertIn('<dialog id="invite-dialog" aria-labelledby="invite-title">', html)
        self.assertIn('id="invite-title"', html)
        for input_id, status_id in (
            ("new-name", "form-error"),
            ("invite-email", "invite-status"),
        ):
            self.assertRegex(html, rf'id="{input_id}"[^>]*aria-describedby="{status_id}"')
        self.assertRegex(html, r'id="import-file"[^>]*aria-describedby="import-guidance import-status"')
        self.assertIn('setAttribute("aria-invalid"', script)

    def test_incidental_accessibility_and_touch_noise_is_not_part_of_the_gauntlet(self) -> None:
        html = (APP / "index.html").read_text(encoding="utf-8")
        script = (APP / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="avatar" data-case-id="avatar-settings" aria-haspopup="menu" aria-expanded="false" aria-controls="avatar-menu"', html)
        self.assertIn("function closeAvatarMenu()", script)
        self.assertIn("closeAvatarMenu();", script.split('event.key === "Escape"', 1)[1])
        self.assertNotIn("Right-click for actions", html)
        for status_id in ("form-error", "toast", "invite-status", "import-status"):
            self.assertRegex(html, rf'id="{status_id}"[^>]*role="(?:alert|status)"')
        self.assertIn("Ask a workspace owner to enable it", html)
        self.assertIn("function openContextMenu()", script)
        self.assertIn('$("#palette")?.querySelector("a")?.focus()', script)
        self.assertIn('$("#duplicate")?.focus()', script)
        self.assertIn('event.key === "Tab"', script)
        self.assertIn('api("/api/import", value)', script)
        self.assertIn("#project-row { gap:", (APP / "styles.css").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

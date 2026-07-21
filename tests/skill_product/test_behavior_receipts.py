from __future__ import annotations

import json
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from tests.skill_product.gauntlet.runtime_receipt import (
    MAX_EVENTS,
    ReceiptError,
    RuntimeReceipt,
    receipt_digest,
)


class RuntimeReceiptUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "private" / "actions.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_receipt_is_deterministic_bounded_and_reset_preserves_prior_epoch(self) -> None:
        first = RuntimeReceipt(self.path)
        event = {
            "event_type": "activation",
            "route": "/projects",
            "role": "member",
            "viewport_class": "desktop",
            "control": {"identity": "Save", "type": "button"},
            "input_mechanism": "pointer",
            "surface": "editor",
        }
        first.append(event)
        before = first.read()
        first.reset()
        first.append({**event, "input_mechanism": "keyboard"})
        after = first.read()

        second_path = Path(self.temp.name) / "second.json"
        second = RuntimeReceipt(second_path)
        second.append(event)
        second.reset()
        second.append({**event, "input_mechanism": "keyboard"})

        self.assertEqual(2, len(after["epochs"]))
        self.assertEqual(before["epochs"][0], after["epochs"][0])
        self.assertEqual(receipt_digest(after), receipt_digest(second.read()))
        self.assertNotIn("timestamp", json.dumps(after).casefold())

        for index in range(MAX_EVENTS - 1):
            first.append({"event_type": "route_visit", "route": f"/bounded/{index}"})
        with self.assertRaisesRegex(ReceiptError, "event limit"):
            first.append({"event_type": "route_visit", "route": "/too-many"})

    def test_closed_contract_rejects_oracle_secrets_credentials_and_oversize_values(self) -> None:
        receipt = RuntimeReceipt(self.path)
        for key in ("oracle_id", "expected_answer", "secret", "credential", "receipt_path"):
            with self.subTest(key=key), self.assertRaises(ReceiptError):
                receipt.append({"event_type": "activation", key: "leak"})
        with self.assertRaisesRegex(ReceiptError, "unknown field"):
            receipt.append({"event_type": "activation", "arbitrary": "value"})
        with self.assertRaisesRegex(ReceiptError, "too long"):
            receipt.append({"event_type": "route_visit", "route": "/" + "x" * 600})

    def test_supported_behavior_vocabulary_covers_required_receipt_dimensions(self) -> None:
        receipt = RuntimeReceipt(self.path)
        events = [
            {"event_type": "route_visit", "route": "/team", "role": "admin", "viewport_class": "mobile"},
            {"event_type": "surface_spawn", "route": "/team", "surface": "invite-dialog"},
            {"event_type": "transition", "route": "/team", "before_state": "closed", "after_state": "open"},
            {"event_type": "reload_reentry", "route": "/team", "outcome": "state-restored"},
            {"event_type": "blocked", "route": "/admin/data", "control": {"identity": "Delete all data", "type": "button"}, "reason": "destructive"},
            {"event_type": "avoided", "route": "/admin/data", "control": {"identity": "Delete all data", "type": "button"}, "reason": "authorization-required"},
        ]
        for event in events:
            receipt.append(event)
        self.assertEqual([event["event_type"] for event in events], [event["event_type"] for event in receipt.current_events()])

    def test_private_expectations_cover_every_actionable_oracle_item(self) -> None:
        root = Path(__file__).parent / "gauntlet"
        oracle = json.loads((root / "oracle/surface-oracle.json").read_text(encoding="utf-8"))
        document = json.loads((root / "oracle/receipt-expectations.json").read_text(encoding="utf-8"))
        required = {item["id"] for item in oracle["items"] if item["kind"] in {"surface", "control", "transition"}}
        self.assertEqual("shipworthy-receipt-expectations-v1", document["schema_version"])
        self.assertEqual(required, set(document["expectations"]))
        self.assertTrue(all(expectation.get("clauses") for expectation in document["expectations"].values()))

    def test_fixture_network_behavior_is_local_and_relative_only(self) -> None:
        app = Path(__file__).parent / "gauntlet/app"
        server = (app / "server.py").read_text(encoding="utf-8")
        client = (app / "activity.js").read_text(encoding="utf-8") + (app / "app.js").read_text(encoding="utf-8")
        self.assertIn('("127.0.0.1", args.port)', server)
        self.assertNotIn("http://", client)
        self.assertNotIn("https://", client)
        self.assertIn('fetch("/api/activity"', client)


class PreparedReceiptIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        from tests.skill_product.test_gauntlet_acceptance import AcceptanceHarnessTests

        self.harness = AcceptanceHarnessTests(methodName="runTest")
        self.harness.setUp()

    def tearDown(self) -> None:
        self.harness.tearDown()

    @staticmethod
    def _request(url: str, method: str = "GET", payload: dict | None = None) -> tuple[int, dict]:
        data = None if payload is None else json.dumps(payload).encode()
        request = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=2) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            raw = error.read()
            try:
                body = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                body = {}
            return error.code, body

    def test_prepare_uses_private_server_copy_and_agent_evidence_only_allowlist(self) -> None:
        output, manifest = self.harness.prepare("runtime-only")
        controller = Path(manifest["controller_root"])
        receipt = controller / "private" / "runtime-actions.json"
        server_script = Path(manifest["server_script"])

        self.assertTrue(server_script.is_file())
        self.assertTrue(server_script.is_relative_to(controller))
        self.assertTrue(receipt.is_file())
        self.assertEqual((output / "agent-evidence").resolve(), Path(manifest["agent_output"]))
        self.assertTrue(Path(manifest["agent_output"]).is_dir())
        self.assertNotIn(str(output), manifest["allowed_paths"])
        self.assertNotIn(str(controller), manifest["allowed_paths"])
        self.assertIn(str((output / "agent-evidence").resolve()), manifest["allowed_paths"])
        self.assertNotIn(str(receipt), json.dumps(manifest))

    def test_http_receipt_is_write_only_validated_and_reset_isolated(self) -> None:
        _output, manifest = self.harness.prepare("runtime-only")
        base = manifest["base_url"]
        controller_receipt = RuntimeReceipt(Path(manifest["controller_root"]) / "private" / "runtime-actions.json")

        status, _ = self._request(base + "/api/activity")
        self.assertIn(status, (404, 405))
        status, body = self._request(base + "/api/activity", "POST", {"event_type": "route_visit", "route": "/projects"})
        self.assertEqual((202, {"accepted": True}), (status, body))
        self.assertEqual(1, len(controller_receipt.current_events()))

        status, _ = self._request(base + "/api/activity", "POST", {"event_type": "activation", "oracle_id": "CASE-SAVE"})
        self.assertEqual(400, status)
        request = urllib.request.Request(base + manifest["reset_endpoint"], data=b"{}", method="POST", headers={manifest["reset_header"]: manifest["reset_token"], "Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=2) as response:
            self.assertEqual(200, response.status)
        self.assertEqual(2, len(controller_receipt.read()["epochs"]))
        self.assertEqual(1, len(controller_receipt.read()["epochs"][0]["events"]))
        self.assertEqual([], controller_receipt.current_events())

    def test_fixture_content_does_not_expose_oracle_or_controller_paths(self) -> None:
        _output, manifest = self.harness.prepare("runtime-only")
        app = Path(manifest["server_script"]).parent
        visible = "\n".join(path.read_text(encoding="utf-8") for path in app.rglob("*") if path.is_file() and path.suffix in {".html", ".js", ".json", ".md"})
        oracle = json.loads((Path(__file__).parent / "gauntlet/oracle/surface-oracle.json").read_text(encoding="utf-8"))
        defects = json.loads((Path(__file__).parent / "gauntlet/oracle/expected-defects.json").read_text(encoding="utf-8"))
        forbidden = (
            "surface-oracle",
            "expected-defects",
            "data-case-id",
            "data-expected-effect",
            manifest["controller_root"],
            str(Path.home()),
            *(item["id"] for item in oracle["items"]),
            *(defect["id"] for defect in defects["defects"]),
        )
        self.assertFalse(any(value in visible for value in forbidden))


if __name__ == "__main__":
    unittest.main()

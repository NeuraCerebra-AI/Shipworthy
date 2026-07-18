from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_NAMES = {"ship-readiness-orchestrator", "ship-deep-review", "ship-product-workflows", "ship-workflow-clarity"}


class ManifestAndInstallTests(unittest.TestCase):
    def test_both_host_manifests_are_package_free_and_bundle_four_skills(self) -> None:
        paths = [
            ROOT / "plugins/shipworthy/.codex-plugin/plugin.json",
            ROOT / "plugins/shipworthy/.claude-plugin/plugin.json",
            ROOT / ".agents/plugins/marketplace.json",
            ROOT / ".claude-plugin/marketplace.json",
        ]
        documents = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
        self.assertTrue(all(document.get("name") == "shipworthy" for document in documents))
        text = json.dumps(documents).lower()
        for forbidden in ("shipworthy-core", "supported_core", "pydantic", "uv.lock"):
            self.assertNotIn(forbidden, text)
        self.assertEqual(SKILL_NAMES, {path.parent.name for path in (ROOT / "plugins/shipworthy/skills").glob("*/SKILL.md")})
        codex_marketplace = documents[2]
        source = codex_marketplace["plugins"][0]["source"]
        self.assertEqual("url", source["source"])
        self.assertEqual("https://github.com/NeuraCerebra-AI/Shipworthy.git", source["url"])
        self.assertEqual("main", source["ref"])

    def test_readme_uses_native_hosts_and_explicit_manual_targets(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("/reload-plugins", readme)
        self.assertIn("./install.sh --target codex", readme)
        self.assertIn("./install.sh --target claude", readme)
        self.assertNotIn("Documents folder", readme)
        self.assertNotIn("this app's skills directory", readme)
        self.assertNotIn("~/.codex/skills", readme)

    def test_manual_installer_refuses_ambiguous_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            result = subprocess.run([ROOT / "install.sh"], env={**os.environ, "HOME": home}, capture_output=True, text=True)
            self.assertEqual(2, result.returncode)
            self.assertIn("--target", result.stderr)
            self.assertFalse((Path(home) / ".agents").exists())
            self.assertFalse((Path(home) / ".claude").exists())


if __name__ == "__main__":
    unittest.main()

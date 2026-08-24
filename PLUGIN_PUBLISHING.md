# Plugin publishing

The four top-level skill directories are the canonical source. The packaged
plugin at `plugins/shipworthy` is a committed mirror with both host manifests:

- `.codex-plugin/plugin.json` for Codex and ChatGPT;
- `.claude-plugin/plugin.json` for Claude Code.

## Maintain the package

After changing any top-level skill, refresh and verify the mirror from the
repository root:

```bash
python3 tools/sync_plugin_package.py --write
python3 tools/sync_plugin_package.py
claude plugin validate ./plugins/shipworthy
python3 /path/to/plugin-creator/scripts/validate_plugin.py ./plugins/shipworthy
```

The GitHub Actions validation job also fails when the packaged copy drifts from
the canonical skills.

## Codex

The repo marketplace is `.agents/plugins/marketplace.json`. For local or team
testing, add the GitHub marketplace and install `shipworthy@shipworthy` with
the Codex plugin CLI. For the public Plugins Directory, submit the packaged
plugin as a skills-only plugin through the OpenAI Platform submission portal.

For each public Codex release, bump the strict semantic version in
`plugins/shipworthy/.codex-plugin/plugin.json`, submit the update for review,
and publish it after approval.

## Claude Code

The marketplace catalog is `.claude-plugin/marketplace.json`. Its plugin entry
uses a relative Git source so the package stays in this repository. The Claude
manifest intentionally omits `version`, allowing Git commit identity to act as
the update signal for Git-backed installs. A stable release process can instead
add and bump a semantic version on every release.

For the public community marketplace, validate `plugins/shipworthy`, then use
Anthropic's Claude Code plugin submission form. Approval and catalog sync are
managed by Anthropic; no repository-side credentials are stored here.

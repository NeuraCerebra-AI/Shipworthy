# Shipworthy plugin

Shipworthy is a read-only, proof-backed product readiness agent for Codex and
Claude Code. It bundles four cooperating skills:

- `ship-readiness-orchestrator` — owns the canonical readiness ledger and verdict;
- `ship-deep-review` — runs verified evidence waves and independent checks;
- `ship-product-workflows` — walks safe user paths and traces backend symptoms;
- `ship-workflow-clarity` — checks comprehension, recovery, trust, and next actions.

Ask **“Are we shipworthy?”** to start a full run. The plugin never changes the
target product unless a user explicitly authorizes a later fix workflow.

The four top-level skill folders in the repository remain the canonical source
for standalone installs. Run `python3 tools/sync_plugin_package.py --write`
after changing them so this packaged mirror stays current.

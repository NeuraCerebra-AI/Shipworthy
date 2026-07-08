#!/usr/bin/env bash
# Shipworthy installer — copies the four ship-* skills into your agent's skills directory.
# Safe by default: never overwrites without a timestamped backup.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_DIR/plugins/shipworthy/skills"

# Pick a target skills dir: honor $SKILLS_DIR, else Claude Code, else Codex, else prompt.
if [[ -n "${SKILLS_DIR:-}" ]]; then
  DEST="$SKILLS_DIR"
elif [[ -d "$HOME/.claude/skills" ]]; then
  DEST="$HOME/.claude/skills"
elif [[ -d "$HOME/.codex/skills" ]]; then
  DEST="$HOME/.codex/skills"
else
  echo "No skills directory found (~/.claude/skills or ~/.codex/skills)."
  read -r -p "Enter target skills directory to create: " DEST
fi
mkdir -p "$DEST"

echo "Tip: in Claude Code the one-command route is:  /plugin marketplace add NeuraCerebra-AI/shipworthy  &&  /plugin install shipworthy@shipworthy"
echo ""
echo "Installing Shipworthy skills -> $DEST"
for skill in ship-readiness-orchestrator ship-deep-review ship-product-workflows ship-workflow-clarity; do
  if [[ -d "$DEST/$skill" ]]; then
    bak="$DEST/$skill.bak.$(date +%Y%m%d%H%M%S)"
    echo "  • $skill exists -> backing up to $(basename "$bak")"
    mv "$DEST/$skill" "$bak"
  fi
  cp -r "$SRC/$skill" "$DEST/$skill"
  echo "  ✓ $skill"
done

cat <<'NEXT'

Done. All four skills are independently installable, and the orchestrator will
conduct the other three when present (it fails loudly, not silently, if one is missing).

Try it in Claude Code or Codex:

  Use ship-readiness-orchestrator in full blast on ./my-app.
  Try every safe user path, find missing/overcomplicated paths, and report
  ledger-backed readiness. Do not implement fixes.

Or run a single lane, e.g. ship-workflow-clarity on one confusing screen.
NEXT

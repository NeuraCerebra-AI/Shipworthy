#!/usr/bin/env bash
# Advanced manual fallback for installing the four Shipworthy skills.
set -euo pipefail

usage() { echo "usage: ./install.sh --target codex|claude|both" >&2; exit 2; }
[[ $# -eq 2 && "$1" == "--target" ]] || usage
TARGET="$2"
[[ "$TARGET" == "codex" || "$TARGET" == "claude" || "$TARGET" == "both" ]] || usage

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_DIR/plugins/shipworthy/skills"
SKILLS=(ship-readiness-orchestrator ship-deep-review ship-product-workflows ship-workflow-clarity)
DESTINATIONS=()
[[ "$TARGET" == "codex" || "$TARGET" == "both" ]] && DESTINATIONS+=("$HOME/.agents/skills")
[[ "$TARGET" == "claude" || "$TARGET" == "both" ]] && DESTINATIONS+=("$HOME/.claude/skills")

for skill in "${SKILLS[@]}"; do
  [[ -f "$SRC/$skill/SKILL.md" ]] || { echo "error: incomplete source skill: $skill" >&2; exit 3; }
done
if find "$SRC" -type d -name __pycache__ -o -type f \( -name '*.pyc' -o -name '*.pyo' \) | grep -q .; then
  echo "error: source skills contain generated cache files" >&2
  exit 3
fi

stamp="$(date -u +%Y%m%d%H%M%S).$$"
stages=() installed=() backup_skills=() backup_dests=() backup_paths=() backup_roots=() created_dirs=()

cleanup_stages() { local stage; for stage in "${stages[@]}"; do rm -rf "$stage"; done; }
cleanup_created_dirs() {
  local i
  for ((i=${#created_dirs[@]}-1; i>=0; i--)); do rmdir "${created_dirs[$i]}" 2>/dev/null || true; done
}
cleanup_backup_roots() {
  local i root
  for ((i=${#backup_roots[@]}-1; i>=0; i--)); do
    root="${backup_roots[$i]}"
    rmdir "$root" 2>/dev/null || true
    rmdir "$(dirname "$root")" 2>/dev/null || true
  done
}
rollback() {
  local path i
  for path in "${installed[@]}"; do rm -rf "$path"; done
  for ((i=${#backup_paths[@]}-1; i>=0; i--)); do
    rm -rf "${backup_dests[$i]}/${backup_skills[$i]}"
    mv "${backup_paths[$i]}" "${backup_dests[$i]}/${backup_skills[$i]}" || true
  done
  cleanup_stages
  cleanup_backup_roots
  cleanup_created_dirs
}

# Stage every requested host before changing either one.
for dest in "${DESTINATIONS[@]}"; do
  for directory in "$(dirname "$dest")" "$dest"; do
    if [[ ! -d "$directory" ]]; then
      if mkdir "$directory"; then
        created_dirs+=("$directory")
      else
        cleanup_stages; cleanup_created_dirs; exit 4
      fi
    fi
  done
  if ! stage="$(mktemp -d "$dest/.shipworthy-stage.XXXXXX")"; then
    cleanup_stages; cleanup_created_dirs; exit 4
  fi
  stages+=("$stage")
  for skill in "${SKILLS[@]}"; do
    if ! cp -R "$SRC/$skill" "$stage/$skill"; then cleanup_stages; cleanup_created_dirs; exit 4; fi
    [[ -f "$stage/$skill/SKILL.md" ]] || { cleanup_stages; cleanup_created_dirs; echo "error: staged skill is incomplete: $skill" >&2; exit 4; }
  done
done

for index in "${!DESTINATIONS[@]}"; do
  dest="${DESTINATIONS[$index]}"; stage="${stages[$index]}"
  for skill in "${SKILLS[@]}"; do
    if [[ -e "$dest/$skill" ]]; then
      backup_root="$(dirname "$dest")/shipworthy-backups/$stamp"
      if [[ ! -d "$backup_root" ]]; then
        if mkdir -p "$backup_root"; then
          backup_roots+=("$backup_root")
        else
          result=$?; echo "error: backup directory creation failed; restoring prior state" >&2; rollback; exit "$result"
        fi
      fi
      backup="$backup_root/$skill"
      if mv "$dest/$skill" "$backup"; then
        backup_skills+=("$skill"); backup_dests+=("$dest"); backup_paths+=("$backup")
        echo "backup: $backup"
      else
        result=$?; echo "error: backup failed; restoring prior state" >&2; rollback; exit "$result"
      fi
    fi
    if mv "$stage/$skill" "$dest/$skill"; then
      installed+=("$dest/$skill"); echo "installed: $dest/$skill"
    else
      result=$?; echo "error: install failed; restoring prior state" >&2; rollback; exit "$result"
    fi
  done
done
cleanup_stages

cat <<'EOF'
Done. Restart Codex, or run /reload-plugins in Claude Code.
Manual uninstall is intentionally not automated; remove only the explicitly named
manual skill directories after reviewing any backups.
Try: are we shipworthy?
For a full run, Shipworthy may ask for authorization and stop; answer explicitly
before it uses persistent goal mode or parallel subagents.
EOF

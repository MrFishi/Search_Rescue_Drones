#!/usr/bin/env bash
# Handoff notes, newest first: file | session | machine | created | status. Never fails.
root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null)
# CLAUDE_PROJECT_DIR wins when set, so tests can point the listing at a fixture tree.
root=${CLAUDE_PROJECT_DIR:-$root}
d="$root/.claude/handoffs"

field() {
  awk -v k="$1" 'NR == 1 && /^---$/ { f = 1; next }
    f && /^---$/ { exit }
    f && index($0, k ": ") == 1 { sub("^" k ": *", ""); gsub(/^"|"$/, ""); print; exit }' "$2" 2>/dev/null
}

n=0
while IFS= read -r f; do
  [ -f "$f" ] || continue
  n=$((n + 1))
  printf '%s | %s | %s | %s | %s\n' "$(basename "$f")" "$(field session_name "$f")" "$(field machine "$f")" "$(field created "$f")" "$(field status "$f")"
done < <(ls -1 "$d"/[0-9]*.md 2>/dev/null | sort -r | head -n 15)
[ "$n" -gt 0 ] || echo "(no handoff notes in .claude/handoffs/)"
exit 0

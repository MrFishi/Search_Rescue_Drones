#!/usr/bin/env bash
# Facts for /handoff and /pickup: session identity, machine, repo state. Never fails.
sid=${1:-}
root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null)

# The transcript's format is internal to Claude Code; a missing title just prints empty.
t=$(ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/projects/*/"$sid".jsonl 2>/dev/null | head -n1)
title() { [ -n "$t" ] && jq -r --arg k "$1" 'select(.type == $k) | (.customTitle // .aiTitle // empty)' "$t" 2>/dev/null | tail -n1; }

echo "session_id: ${sid:-unknown}"
echo "rename_name: $(title custom-title)"
echo "generated_title: $(title ai-title)"
echo "machine: $(hostname)"
echo "now: $(date '+%Y-%m-%d %H:%M %Z')"
echo "filename_stamp: $(date '+%Y-%m-%d_%H%M')"

if [ -n "$root" ]; then
  ab=$(git -C "$root" rev-list --left-right --count '@{u}...HEAD' 2>/dev/null | awk '{print "behind " $1 ", ahead " $2}')
  echo "repo: $(git -C "$root" branch --show-current 2>/dev/null) @ $(git -C "$root" rev-parse --short HEAD 2>/dev/null) (${ab:-no upstream})"
  git -C "$root" status --short 2>/dev/null | head -n 25 | sed 's/^/  /'
else
  echo "repo: not found"
fi
exit 0

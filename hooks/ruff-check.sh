#!/usr/bin/env bash
# cc-guide: hooks.events hooks.exit-codes hooks.patterns @2.1.304.1
# Stop hook — before the turn ends, surface ruff lint errors that --fix could not
# auto-resolve (e.g. undefined names, unused-but-referenced, complexity rules).
#
# Exit 2 feeds stderr back to Claude so it fixes them and continues.
# One attempt per turn: when `stop_hook_active` is set, exit 0 without re-running
# ruff, so the fix is not re-checked until the next turn ends. This gives up a
# guaranteed-clean stop in exchange for never looping.
#
# Install into a real Python/uv repo (see README.md). Reads hook JSON on stdin.
set -uo pipefail

input=$(cat)
active=$(printf '%s' "$input" | jq -r '.stop_hook_active // false')
[ "$active" = "true" ] && exit 0   # already inside a hook-driven continuation

out=$(uv run ruff check . 2>&1)
status=$?

if [ "$status" -ne 0 ]; then
  {
    echo "ruff check found issues that need a human/Claude fix (not auto-fixable):"
    echo "$out"
  } >&2
  exit 2
fi
exit 0

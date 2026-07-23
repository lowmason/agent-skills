#!/usr/bin/env bash
# Stop hook — before the turn ends, surface ruff lint errors that --fix could not
# auto-resolve (e.g. undefined names, unused-but-referenced, complexity rules).
#
# Exit 2 feeds stderr back to Claude so it fixes them and continues.
# `stop_hook_active` guards against an infinite fix->stop->fix loop.
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

#!/usr/bin/env bash
# cc-guide: hooks.events hooks.exit-codes hooks.patterns hooks.pitfalls @2.1.306
# Stop hook — before the turn ends, surface ruff lint errors that --fix could not
# auto-resolve (e.g. undefined names, unused-but-referenced, complexity rules).
#
# Exit 2 feeds stderr back to Claude so it fixes them and continues.
# Only lint blocks. ruff exits 1 when it finds violations, but `uv run` also exits 1
# when it cannot sync the project, so an exit 1 blocks only once
# `uv run ruff --version` shows ruff can start. Any other failure (no uv: 127; ruff
# missing from the project, or a bad config: 2) exits 1 with "ruff unavailable" on
# the first stderr line: a non-blocking error, and the transcript shows that line.
# One attempt per turn: when `stop_hook_active` is set, exit 0 without re-running
# ruff, so the fix is not re-checked until the next turn ends. This gives up a
# guaranteed-clean stop in exchange for never looping.
#
# Install into a real Python/uv repo (see README.md). Reads hook JSON on stdin.
set -uo pipefail

input=$(cat)
active=$(printf '%s' "$input" | jq -r '.stop_hook_active // false')
[ "$active" = "true" ] && exit 0   # already inside a hook-driven continuation

unavailable() {   # $1 = exit status, $2 = output; reports without blocking
  {
    echo "ruff-check: ruff unavailable (exit $1), so lint was not checked."
    echo "$2"
  } >&2
  exit 1
}

out=$(uv run ruff check . 2>&1)
status=$?

[ "$status" -eq 0 ] && exit 0
[ "$status" -eq 1 ] || unavailable "$status" "$out"
uv run ruff --version >/dev/null 2>&1 || unavailable "$status" "$out"

{
  echo "ruff check found issues that need a human/Claude fix (not auto-fixable):"
  echo "$out"
} >&2
exit 2

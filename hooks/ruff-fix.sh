#!/usr/bin/env bash
# PostToolUse(Write|Edit) — auto-fix + format an edited Python file with the
# *project's* ruff (via `uv run`, so it picks up that repo's pyproject config).
#
# PostToolUse runs AFTER the edit and cannot undo it — this only cleans up.
# Pair with ruff-check.sh (Stop hook) to catch unfixable lint each turn.
#
# Install into a real Python/uv repo, NOT the skills library and NOT globally
# (see README.md for why). Reads the hook JSON payload on stdin.
set -euo pipefail

input=$(cat)
f=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')

[ -z "$f" ] && exit 0
case "$f" in *.py) ;; *) exit 0 ;; esac   # Python files only
[ -f "$f" ] || exit 0                       # skip deletes / moves

# `uv run` resolves the repo's own ruff (a dev dep here) + its [tool.ruff] config.
# Best-effort: never fail the turn on a formatter hiccup.
uv run ruff check --fix --quiet "$f" 2>/dev/null || true
uv run ruff format --quiet "$f"       2>/dev/null || true
exit 0

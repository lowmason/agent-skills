#!/usr/bin/env bash
# cc-guide: hooks.events hooks.exit-codes hooks.patterns hooks.pitfalls @2.1.325
# Stop hook — before the turn ends, surface ruff lint errors that --fix could not
# auto-resolve (e.g. undefined names, unused-but-referenced, complexity rules).
#
# It blocks with a JSON decision on stdout, {"decision":"block","reason":...}, and
# exit 0. The reason, ruff's output, goes back to Claude so it fixes them and
# continues. Not exit 2: exit 2 with empty stdout and stderr that says a file is
# missing (ruff's E902 "No such file or directory" for a file that vanished)
# counts as a non-blocking error, so the turn would end. If jq cannot print the
# decision, the hook exits 1 with "jq could not print the block decision" on the
# first stderr line: a non-blocking error, which the transcript shows.
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

reason="ruff check found issues that need a human/Claude fix (not auto-fixable):
$out"
decision=$(jq -n --arg reason "$reason" '{decision: "block", reason: $reason}')
jq_status=$?
if [ "$jq_status" -ne 0 ]; then   # reports without blocking, as unavailable() does
  {
    echo "ruff-check: jq could not print the block decision (exit $jq_status), so lint was not fed back."
    echo "$reason"
  } >&2
  exit 1
fi
printf '%s\n' "$decision"
exit 0

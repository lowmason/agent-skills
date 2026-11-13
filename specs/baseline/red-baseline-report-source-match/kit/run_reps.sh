#!/bin/bash
# Run decision-only reps for the report-source-match micro-tests. Each rep is a fresh `claude -p` with no
# tools, run from its own new, empty directory under /tmp, outside every repository.
# `--setting-sources ""` keeps user-level context out of the reps: the output style, plugin
# SessionStart hooks, ~/.claude/CLAUDE.md and ~/.claude/rules/. CLAUDE_CODE_DISABLE_AUTO_MEMORY
# drops the auto-memory section. --disable-slash-commands keeps every installed skill and command
# out of the reps. env -i keeps the launching Desktop session's environment out (its socket,
# session id and effort). Check a new Claude Code version with isolation_probe.txt first.
# Usage: run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model>
# The first rep runs alone and writes the prompt cache; the others then run together.
set -u
FLAGS=()
PROMPT="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" || exit 2
OUT="$(mkdir -p "$2" && cd "$2" && pwd)" || exit 2
FIRST="$3"
LAST="$4"
MODEL="${5:?usage: run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model>}"
# Check the range before the overwrite guard: a reversed or non-numeric range would skip the guard.
for n in "$FIRST" "$LAST"; do
  case "$n" in
    '' | *[!0-9]*) echo "refusing: first-rep and last-rep must be positive integers"; exit 2 ;;
  esac
done
[ "$FIRST" -ge 1 ] && [ "$FIRST" -le "$LAST" ] || { echo "refusing: need 1 <= first-rep <= last-rep"; exit 2; }
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  [ -e "$OUT/rep$i.json" ] && { echo "refusing: $OUT/rep$i.json exists"; exit 2; }
  i=$((i + 1))
done
# rep returns the status of its `claude` run, so a failed rep reaches the script's exit status.
rep() {
  local run status
  run="$(mktemp -d /tmp/rsm-rep-XXXXXX)" || return 2
  (
    cd "$run" || exit 2
    git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $run is inside a git repository"; exit 2; }
    env -i HOME="$HOME" USER="$USER" LOGNAME="${LOGNAME:-$USER}" PATH="$PATH" SHELL="$SHELL" \
      TMPDIR="${TMPDIR:-/tmp}" LANG="${LANG:-en_US.UTF-8}" CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
      claude -p --model "$MODEL" --tools "" --strict-mcp-config --setting-sources "" --disable-slash-commands \
      --no-session-persistence --output-format json --max-budget-usd 0.50 \
      ${FLAGS[@]+"${FLAGS[@]}"} < "$PROMPT" > "$OUT/rep$1.json" 2> "$OUT/rep$1.err"
  )
  status=$?
  echo "rep$1 exit=$status"
  [ -s "$OUT/rep$1.err" ] || rm -f "$OUT/rep$1.err"
  return "$status"
}
# The first rep writes the prompt cache for the others, so a failure there stops the batch.
rep "$FIRST" || { echo "rep$FIRST failed, so the other reps did not run"; exit 1; }
pids=()
i=$((FIRST + 1))
while [ "$i" -le "$LAST" ]; do
  rep "$i" &
  pids+=("$!")
  i=$((i + 1))
done
failed=0
for pid in ${pids[@]+"${pids[@]}"}; do
  wait "$pid" || failed=$((failed + 1))
done
[ "$failed" -eq 0 ] || { echo "$failed rep(s) failed"; exit 1; }

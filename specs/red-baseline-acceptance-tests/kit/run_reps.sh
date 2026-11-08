#!/bin/bash
# Run reps for plan 81's probe, adapted from plan 73's kit
# (specs/red-baseline-reviewer-planning-contract/kit/run_reps.sh). Each rep is a fresh `claude -p`
# with no tools, run from its own new, empty directory under /tmp, outside every repository.
# `--setting-sources ""` keeps user-level context out of the reps: the output style, plugin
# SessionStart hooks, ~/.claude/CLAUDE.md and ~/.claude/rules/. CLAUDE_CODE_DISABLE_AUTO_MEMORY
# drops the auto-memory section. Check a new Claude Code version with plan 73's isolation_probe.txt first.
# Usage: run_reps.sh <prompt-file|prompt-dir> <out-dir> <first-rep> <last-rep> <model> [<budget>]
# With a directory, rep i reads <prompt-dir>/rep<i>.txt. <budget> is the per-rep --max-budget-usd
# cap, 4.00 when omitted (plan 81, DF8).
# The first rep runs alone and writes the prompt cache; the others then run together.
set -u
SRC="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" || exit 2
OUT="$(mkdir -p "$2" && cd "$2" && pwd)" || exit 2
FIRST="$3"
LAST="$4"
MODEL="${5:?usage: run_reps.sh <prompt-file|prompt-dir> <out-dir> <first-rep> <last-rep> <model> [<budget>]}"
BUDGET="${6:-4.00}"
prompt_of() {
  if [ -d "$SRC" ]; then echo "$SRC/rep$1.txt"; else echo "$SRC"; fi
}
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  [ -e "$OUT/rep$i.json" ] && { echo "refusing: $OUT/rep$i.json exists"; exit 2; }
  [ -f "$(prompt_of "$i")" ] || { echo "refusing: no prompt $(prompt_of "$i")"; exit 2; }
  i=$((i + 1))
done
rep() {
  local run prompt
  prompt="$(prompt_of "$1")"
  run="$(mktemp -d /tmp/plan81-rep-XXXXXX)" || return 2
  (
    cd "$run" || exit 2
    git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $run is inside a git repository"; exit 2; }
    CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
      claude -p --model "$MODEL" --tools "" --strict-mcp-config --setting-sources "" \
      --no-session-persistence --output-format json --max-budget-usd "$BUDGET" \
      < "$prompt" > "$OUT/rep$1.json" 2> "$OUT/rep$1.err"
  )
  echo "rep$1 exit=$?"
  [ -s "$OUT/rep$1.err" ] || rm -f "$OUT/rep$1.err"
  rmdir "$run" 2> /dev/null
}
rep "$FIRST"
i=$((FIRST + 1))
while [ "$i" -le "$LAST" ]; do
  rep "$i" &
  i=$((i + 1))
done
wait

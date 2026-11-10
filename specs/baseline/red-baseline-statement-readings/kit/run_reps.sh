#!/bin/bash
# Run reps for plan 83's statement-readings probe, adapted from plan 81's runner
# (specs/baseline/red-baseline-acceptance-tests/kit/run_reps.sh). Each rep is a fresh `claude -p` with no tools, run from
# its own new, empty directory under /tmp, outside every repository, under `env -i` with only HOME, USER,
# LOGNAME, PATH, SHELL, TMPDIR and LANG, so nothing of the Desktop session that drives the runs reaches a rep.
# `--setting-sources ""` keeps user-level context out of the reps: the output style, plugin SessionStart hooks,
# ~/.claude/CLAUDE.md and ~/.claude/rules/. CLAUDE_CODE_DISABLE_AUTO_MEMORY drops the auto-memory section, and
# CLAUDE_CODE_DISABLE_ADVISOR_TOOL the advisor. CLAUDE_CODE_MAX_OUTPUT_TOKENS passes through when it is set.
# Every rep calls the one binary that runs/BINARY.txt pins (plan 83, Task 4): the runner refuses when
# CLAUDE_BIN is unset or its sha256 differs from the one in BINARY.txt.
# Usage: CLAUDE_BIN=<path> run_reps.sh <prompt-file|prompt-dir> <out-dir> <first-rep> <last-rep> <model> [<budget>]
# With a directory, rep i reads <prompt-dir>/rep<i>.txt, and rep i is skipped when <prompt-dir>/rep<i>.skip
# exists. <budget> is the per-rep --max-budget-usd cap, 4.00 when omitted (plan 83, PD7).
# The first rep runs alone and writes the prompt cache; the others then run together.
set -u
BINARY_TXT="$(cd "$(dirname "$0")/.." && pwd)/runs/BINARY.txt"
[ -n "${CLAUDE_BIN:-}" ] || { echo "refusing: CLAUDE_BIN is unset"; exit 2; }
[ -f "$BINARY_TXT" ] || { echo "refusing: no $BINARY_TXT"; exit 2; }
WANT="$(sed -n 's/^sha256: //p' "$BINARY_TXT")"
HAVE="$(shasum -a 256 "$CLAUDE_BIN" | cut -d' ' -f1)"
[ -n "$WANT" ] && [ "$WANT" = "$HAVE" ] || { echo "refusing: $CLAUDE_BIN sha256 $HAVE is not $WANT"; exit 2; }
SRC="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" || exit 2
OUT="$(mkdir -p "$2" && cd "$2" && pwd)" || exit 2
FIRST="$3"
LAST="$4"
MODEL="${5:?usage: run_reps.sh <prompt-file|prompt-dir> <out-dir> <first-rep> <last-rep> <model> [<budget>]}"
BUDGET="${6:-4.00}"
prompt_of() {
  if [ -d "$SRC" ]; then echo "$SRC/rep$1.txt"; else echo "$SRC"; fi
}
skipped() {
  [ -d "$SRC" ] && [ -e "$SRC/rep$1.skip" ]
}
EXTRA=()
[ -n "${CLAUDE_CODE_MAX_OUTPUT_TOKENS:-}" ] && EXTRA=("CLAUDE_CODE_MAX_OUTPUT_TOKENS=$CLAUDE_CODE_MAX_OUTPUT_TOKENS")
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  if ! skipped "$i"; then
    [ -e "$OUT/rep$i.json" ] && { echo "refusing: $OUT/rep$i.json exists"; exit 2; }
    [ -f "$(prompt_of "$i")" ] || { echo "refusing: no prompt $(prompt_of "$i")"; exit 2; }
  fi
  i=$((i + 1))
done
rep() {
  local run prompt
  prompt="$(prompt_of "$1")"
  run="$(mktemp -d /tmp/plan83-rep-XXXXXX)" || return 2
  (
    cd "$run" || exit 2
    git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $run is inside a git repository"; exit 2; }
    env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" PATH="$PATH" SHELL="$SHELL" TMPDIR="$TMPDIR" \
      LANG="${LANG:-en_US.UTF-8}" CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 ${EXTRA[@]+"${EXTRA[@]}"} \
      "$CLAUDE_BIN" -p --model "$MODEL" --tools "" --strict-mcp-config --setting-sources "" \
      --no-session-persistence --output-format json --max-budget-usd "$BUDGET" \
      < "$prompt" > "$OUT/rep$1.json" 2> "$OUT/rep$1.err"
  )
  echo "rep$1 exit=$?"
  [ -s "$OUT/rep$1.err" ] || rm -f "$OUT/rep$1.err"
  rmdir "$run" 2> /dev/null
}
i="$FIRST"
while [ "$i" -le "$LAST" ] && skipped "$i"; do
  echo "rep$i skipped"
  i=$((i + 1))
done
[ "$i" -le "$LAST" ] || { wait; exit 0; }
rep "$i"
i=$((i + 1))
while [ "$i" -le "$LAST" ]; do
  if skipped "$i"; then
    echo "rep$i skipped"
  else
    rep "$i" &
  fi
  i=$((i + 1))
done
wait

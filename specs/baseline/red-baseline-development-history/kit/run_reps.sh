#!/bin/bash
# Run decision-only reps for plan 80's micro-tests. Each rep is a fresh `claude -p` with no
# tools, run from its own new, empty directory under /tmp, outside every repository.
# `--setting-sources ""` keeps user-level context out of the reps: the output style, plugin
# SessionStart hooks, ~/.claude/CLAUDE.md and ~/.claude/rules/. CLAUDE_CODE_DISABLE_AUTO_MEMORY
# drops the auto-memory section. Check a new Claude Code version with isolation_probe.txt first.
# Plan 77 deviation (a): each rep runs under `env -i`, so a rep launched from a Claude desktop
# app session does not inherit the app's environment (its messaging socket and token, session
# id, effort level, account variables or LLM_WIKI_ROOT). Only HOME, USER, LOGNAME, PATH, SHELL,
# TMPDIR and LANG pass through, each only when it is set, plus the two CLAUDE_CODE_DISABLE_*
# variables.
# Usage: run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model> [<budget>]
# <budget> is the per-rep --max-budget-usd cap, 0.50 when omitted.
# The first rep runs alone and writes the prompt cache; the others then run together.
set -u
FLAGS=()
KEEP=()
for v in HOME USER LOGNAME PATH SHELL TMPDIR LANG; do
  val="$(printenv "$v")" && KEEP+=("$v=$val")
done
CLAUDE_BIN="$(command -v claude)" || { echo "refusing: no claude on PATH"; exit 2; }
PROMPT="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" || exit 2
OUT="$(mkdir -p "$2" && cd "$2" && pwd)" || exit 2
FIRST="$3"
LAST="$4"
MODEL="${5:?usage: run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model>}"
BUDGET="${6:-0.50}"
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  [ -e "$OUT/rep$i.json" ] && { echo "refusing: $OUT/rep$i.json exists"; exit 2; }
  i=$((i + 1))
done
rep() {
  local run
  run="$(mktemp -d /tmp/plan80-rep-XXXXXX)" || return 2
  (
    cd "$run" || exit 2
    git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $run is inside a git repository"; exit 2; }
    env -i ${KEEP[@]+"${KEEP[@]}"} CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
      "$CLAUDE_BIN" -p --model "$MODEL" --tools "" --strict-mcp-config --setting-sources "" \
      --no-session-persistence --output-format json --max-budget-usd "$BUDGET" \
      ${FLAGS[@]+"${FLAGS[@]}"} < "$PROMPT" > "$OUT/rep$1.json" 2> "$OUT/rep$1.err"
  )
  echo "rep$1 exit=$?"
  [ -s "$OUT/rep$1.err" ] || rm -f "$OUT/rep$1.err"
}
rep "$FIRST"
i=$((FIRST + 1))
while [ "$i" -le "$LAST" ]; do
  rep "$i" &
  i=$((i + 1))
done
wait

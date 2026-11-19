#!/bin/bash
# Run decision-only reps for plan 101's micro-tests. Each rep is a fresh `claude -p` with no
# tools, run from its own new, empty directory under /tmp, outside every repository.
# `--setting-sources ""` keeps user-level context out of the reps: the output style, plugin
# SessionStart hooks, ~/.claude/CLAUDE.md and ~/.claude/rules/. CLAUDE_CODE_DISABLE_AUTO_MEMORY
# drops the auto-memory section. Check a new Claude Code version with isolation_probe.txt first.
# Plan 77 deviation (a): each rep runs under `env -i`, so a rep launched from a Claude desktop
# app session does not inherit the app's environment (its messaging socket and token, session
# id, effort level, account variables or LLM_WIKI_ROOT). Only HOME, USER, LOGNAME, PATH, SHELL,
# TMPDIR and LANG pass through, each only when it is set, plus the two CLAUDE_CODE_DISABLE_*
# variables.
# Plan 101 next-kit fix (D8): after each rep, scrub_json.py drops `credential_expires_at` from the
# rep's JSON file, so the CLI's login-expiry field never reaches a committed file. kit_selftest.py
# shows that, and that two reps get separate folders and cannot see each other's files.
# The runner exits 3, after every rep has run, when a rep file in the batch still holds the key.
# Usage: run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model> [<budget>]
# <budget> is the per-rep --max-budget-usd cap, 0.50 when omitted.
# The first rep runs alone and writes the prompt cache; the others then run together.
set -u
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || exit 2
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
  run="$(mktemp -d /tmp/plan101-rep-XXXXXX)" || return 2
  (
    cd "$run" || exit 2
    git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $run is inside a git repository"; exit 2; }
    env -i ${KEEP[@]+"${KEEP[@]}"} CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
      "$CLAUDE_BIN" -p --model "$MODEL" --tools "" --strict-mcp-config --setting-sources "" \
      --no-session-persistence --output-format json --max-budget-usd "$BUDGET" \
      ${FLAGS[@]+"${FLAGS[@]}"} < "$PROMPT" > "$OUT/rep$1.json" 2> "$OUT/rep$1.err"
  )
  local status=$?
  if [ -f "$OUT/rep$1.json" ]; then
    python3 "$KIT/scrub_json.py" "$OUT/rep$1.json" || echo "rep$1: scrub_json.py failed"
  fi
  echo "rep$1 exit=$status"
  [ -s "$OUT/rep$1.err" ] || rm -f "$OUT/rep$1.err"
}
rep "$FIRST"
i=$((FIRST + 1))
while [ "$i" -le "$LAST" ]; do
  rep "$i" &
  i=$((i + 1))
done
wait
# The scrub's job is that no rep file keeps the key. A rep file that still holds it, because the
# scrub could not read or write the file, makes the batch exit 3 and names the file. So does a file
# that grep cannot scan (its status is 2 or more: a file is clean only on status 1). LC_ALL=C makes
# grep read a file that is not valid UTF-8 as bytes: under a UTF-8 locale it would skip the line.
leaked=0
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  if [ -f "$OUT/rep$i.json" ]; then
    LC_ALL=C grep -aq credential_expires_at "$OUT/rep$i.json"
    case $? in
      0) echo "rep$i: $OUT/rep$i.json still holds credential_expires_at"; leaked=1 ;;
      1) ;;
      *) echo "rep$i: could not scan $OUT/rep$i.json for credential_expires_at"; leaked=1 ;;
    esac
  fi
  i=$((i + 1))
done
[ "$leaked" -eq 0 ] || exit 3

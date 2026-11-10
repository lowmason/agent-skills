#!/bin/bash
# Run decision-only reps for plan 71's micro-tests. Each rep is a fresh `claude -p` with no
# tools, run from a new, empty directory under /tmp, outside every repository.
# Usage: run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep>
# The first rep runs alone and writes the prompt cache; the others then run together.
set -u
FLAGS=()
PROMPT="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" || exit 2
OUT="$(mkdir -p "$2" && cd "$2" && pwd)" || exit 2
FIRST="$3"
LAST="$4"
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  [ -e "$OUT/rep$i.json" ] && { echo "refusing: $OUT/rep$i.json exists"; exit 2; }
  i=$((i + 1))
done
RUN="$(mktemp -d /tmp/plan71-rep-XXXXXX)" || exit 2
cd "$RUN" || exit 2
git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $RUN is inside a git repository"; exit 2; }
rep() {
  CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 claude -p --model claude-sonnet-5-5 --tools "" --strict-mcp-config \
    --no-session-persistence --output-format json --max-budget-usd 0.50 \
    ${FLAGS[@]+"${FLAGS[@]}"} < "$PROMPT" > "$OUT/rep$1.json" 2> "$OUT/rep$1.err"
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

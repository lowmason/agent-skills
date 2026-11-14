#!/bin/bash
# Check the reviewer micro-test's isolation before any rep. This runs one probe prompt through
# `claude -p` with the environment and the flags of run_reps.sh. Keep the two `claude -p` command
# lines identical, byte for byte. The run starts in a new, empty directory under /tmp, outside
# every repository.
# Usage: probe.sh <out-file> [<prompt-file>]
# <prompt-file> defaults to isolation_probe.txt. The model is sonnet and the budget 0.50, as in
# every reviewer rep. The JSON holds a session id. Keep <out-file> outside the repository and never
# commit it.
set -u
FLAGS=()
KEEP=()
for v in HOME USER LOGNAME PATH SHELL TMPDIR LANG; do
  val="$(printenv "$v")" && KEEP+=("$v=$val")
done
CLAUDE_BIN="$(command -v claude)" || { echo "refusing: no claude on PATH"; exit 2; }
[ "$#" -eq 1 ] || [ "$#" -eq 2 ] || { echo "usage: probe.sh <out-file> [<prompt-file>]"; exit 2; }
KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
PROMPT="${2:-$KIT/isolation_probe.txt}"
[ -f "$PROMPT" ] || { echo "refusing: no prompt file $PROMPT"; exit 2; }
PROMPT="$(cd "$(dirname "$PROMPT")" && pwd)/$(basename "$PROMPT")"
OUTDIR="$(mkdir -p "$(dirname "$1")" && cd "$(dirname "$1")" && pwd)" || exit 2
OUT="$OUTDIR/$(basename "$1")"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 2; }
MODEL=sonnet
BUDGET=0.50
run="$(mktemp -d /tmp/mt-review-probe-XXXXXX)" || exit 2
(
  cd "$run" || exit 2
  git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $run is inside a git repository"; exit 2; }
    env -i ${KEEP[@]+"${KEEP[@]}"} CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
      "$CLAUDE_BIN" -p --model "$MODEL" --tools "" --strict-mcp-config --setting-sources "" --disable-slash-commands \
      --no-session-persistence --output-format json --max-budget-usd "$BUDGET" \
      ${FLAGS[@]+"${FLAGS[@]}"} < "$PROMPT" > "$OUT"
)
status=$?
echo "probe exit=$status dir=$run"
exit "$status"

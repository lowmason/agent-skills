#!/bin/bash
# Check the isolation of plan 105's no-tools reps before any rep. This runs one probe prompt through
# `claude -p` with the environment and the flags of run_json_reps.sh. Keep the two `claude -p` command
# lines identical, byte for byte. The run starts in a new, empty directory under /tmp, outside every
# repository.
# Usage: probe_json.sh <model> <out-file> [<prompt-file>]
# <model> is claude-sonnet-5-5 or claude-opus-5-5, and the budget is 0.50, as in every no-tools rep.
# <prompt-file> defaults to isolation_probe.txt, plan 104's eight-question probe, which probe_tools.sh
# sends too. The JSON holds a session id. Keep <out-file> outside the repository and never commit it.
# Copy of plan 103's probe.sh (specs/baseline/red-baseline-worktree-skills-fix/kit/probe.sh). Its
# changes: the model is an argument, because plan 105's Task 4 probes both models, and the folder
# prefix is plan105-rep-probe-.
set -u
FLAGS=()
KEEP=()
for v in HOME USER LOGNAME PATH SHELL TMPDIR LANG; do
  val="$(printenv "$v")" && KEEP+=("$v=$val")
done
CLAUDE_BIN="$(command -v claude)" || { echo "refusing: no claude on PATH"; exit 2; }
[ "$#" -eq 2 ] || [ "$#" -eq 3 ] || { echo "usage: probe_json.sh <model> <out-file> [<prompt-file>]"; exit 2; }
case "$1" in
  claude-sonnet-5-5 | claude-opus-5-5) MODEL="$1" ;;
  *) echo "refusing: model $1 is not claude-sonnet-5-5 or claude-opus-5-5"; exit 2 ;;
esac
KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
PROMPT="${3:-$KIT/isolation_probe.txt}"
[ -f "$PROMPT" ] || { echo "refusing: no prompt file $PROMPT"; exit 2; }
PROMPT="$(cd "$(dirname "$PROMPT")" && pwd)/$(basename "$PROMPT")"
OUTDIR="$(mkdir -p "$(dirname "$2")" && cd "$(dirname "$2")" && pwd)" || exit 2
OUT="$OUTDIR/$(basename "$2")"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 2; }
BUDGET=0.50
run="$(mktemp -d /tmp/plan105-rep-probe-XXXXXX)" || exit 2
(
  cd "$run" || exit 2
  git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $run is inside a git repository"; exit 2; }
    env -i ${KEEP[@]+"${KEEP[@]}"} CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
      "$CLAUDE_BIN" -p --model "$MODEL" --tools "" --strict-mcp-config --setting-sources "" --disable-slash-commands \
      --no-session-persistence --output-format json --max-budget-usd "$BUDGET" \
      ${FLAGS[@]+"${FLAGS[@]}"} < "$PROMPT" > "$OUT"
)
status=$?
echo "probe model=$MODEL exit=$status dir=$run"
exit "$status"

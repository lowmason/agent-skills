#!/bin/bash
# Check the isolation of plan 107's case reps before any rep: one probe prompt through claude -p, with
# run_tool_reps.sh's folder layout, environment and flags (common.sh), for the model given. bash 3.2.
# Copy of plan 105's probe_tools.sh (specs/baseline/red-baseline-writing-skills-layout/kit/probe_tools.sh), with this
# kit's models, cap and roots.
# Usage: probe_tools.sh <model> <out-file> [<prompt-file>]
# <model> is claude-sonnet-5-5 or claude-opus-5-5, and the cap is the rep cap, $1.50. <prompt-file>
# defaults to isolation_probe.txt. The probe runs from WST_ROOT/probe/repo/, an empty folder outside
# every repository; WST_ROOT must be empty first (exit 3 otherwise). <out-file> gets the stream, with
# credential_expires_at stripped, and <out-file>.err its stderr. The folder is then parked as
# <out-file>.folder. The stream holds the rep folder's paths and a session id: keep <out-file> outside
# the repository and never commit it.
set -u
[ "$#" -eq 2 ] || [ "$#" -eq 3 ] || { echo "usage: probe_tools.sh <model> <out-file> [<prompt-file>]"; exit 2; }
KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
. "$KIT/common.sh"
MODEL="$1"
check_model "$MODEL" || { echo "refusing: model $MODEL is not claude-sonnet-5-5 or claude-opus-5-5"; exit 2; }
PROMPT="${3:-$KIT/isolation_probe.txt}"
[ -f "$PROMPT" ] || { echo "refusing: no prompt file $PROMPT"; exit 2; }
PROMPT="$(cd "$(dirname "$PROMPT")" && pwd)/$(basename "$PROMPT")"
OUTDIR="$(mkdir -p "$(dirname "$2")" && cd "$(dirname "$2")" && pwd)" || exit 2
OUT="$OUTDIR/$(basename "$2")"
[ -e "$OUT" ] || [ -e "$OUT.folder" ] && { echo "refusing: $OUT exists"; exit 2; }
[ -n "$CLAUDE_BIN" ] && [ -x "$CLAUDE_BIN" ] || { echo "refusing: no claude binary (set CLAUDE_BIN)"; exit 2; }
require_empty_root
dir="$WST_ROOT/probe"
trap '[ -d "$dir" ] && park "$dir" "$OUT.folder"' EXIT
make_folder "$dir" || exit 2
dir="$(cd "$dir" && pwd -P)"
(cd "$dir/repo" && git rev-parse --show-toplevel > /dev/null 2>&1) && { echo "refusing: $dir/repo is inside a git repository"; exit 2; }
run_claude "$dir" "$MODEL" "$PROMPT" "$OUT" "$OUT.err"
status=$?
(cd "$KIT" && uv run --no-project -q python "$KIT/rep_tools.py" strip "$OUT") || exit 2
grep -q "$FIELD" "$OUT" && { echo "the strip left $FIELD in $OUT"; exit 2; }
echo "probe model=$MODEL exit=$status out=$OUT"
exit "$status"

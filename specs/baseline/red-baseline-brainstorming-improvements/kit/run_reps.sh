#!/bin/bash
# Run decision-only reps for plan 72's micro-tests. Each rep is a fresh `claude -p` with no
# tools, run from its own new, empty directory under /tmp, outside every repository.
# `--setting-sources ""` keeps user-level context out of the reps: the output style, plugin
# SessionStart hooks, ~/.claude/CLAUDE.md and ~/.claude/rules/. CLAUDE_CODE_DISABLE_AUTO_MEMORY
# drops the auto-memory section. Check a new Claude Code version with isolation_probe.txt first.
# Usage: run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model>
# The first rep runs alone and writes the prompt cache; the others then run together.
# Plan 106 adds the next-kit fixes. The raw JSON and stderr of each rep go to
# ~/.cache/agent-skills/scratch/plan106-brainstorming-improvements/<out-dir's parent name>/<out-dir name>/,
# outside the repository (KIT_SCRATCH_ROOT replaces the part before plan106-..., for the self-test).
# <out-dir>/rep<N>.json gets postprocess(raw) from postprocess.py: the rep with `void` False, without
# `origin` and `credential_expires_at`, its text scrubbed; or {"void": true, "reason": ...} for a rep a
# peer message reached (`result_index` above 0, or an `origin`), or for raw output that is not a JSON
# object ("unreadable"). A void rep keeps none of its text. Its cost is in the raw JSON only.
set -u
FLAGS=()
KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
PROMPT="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" || exit 2
OUT="$(mkdir -p "$2" && cd "$2" && pwd)" || exit 2
FIRST="$3"
LAST="$4"
MODEL="${5:?usage: run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model>}"
SCRATCH="${KIT_SCRATCH_ROOT:-$HOME/.cache/agent-skills/scratch}/plan106-brainstorming-improvements/$(basename "$(dirname "$OUT")")/$(basename "$OUT")"
mkdir -p "$SCRATCH" || exit 2
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  [ -e "$OUT/rep$i.json" ] && { echo "refusing: $OUT/rep$i.json exists"; exit 2; }
  [ -e "$SCRATCH/rep$i.json" ] && { echo "refusing: $SCRATCH/rep$i.json exists"; exit 2; }
  i=$((i + 1))
done
# postprocess <raw-json> <dest-json>: write postprocess(raw) to <dest-json>, print kept or VOID (<reason>).
postprocess() {
  (cd "$KIT" && uv run --no-project -q python -c '
import json, sys
from pathlib import Path
from postprocess import postprocess
try:
    raw = json.loads(Path(sys.argv[1]).read_text(errors="replace"))
except (OSError, json.JSONDecodeError):
    raw = None
rep = postprocess(raw) if isinstance(raw, dict) else {"void": True, "reason": "unreadable"}
Path(sys.argv[2]).write_text(json.dumps(rep, indent=2, ensure_ascii=False) + "\n")
print("VOID (" + rep["reason"] + ")" if rep["void"] else "kept")
' "$1" "$2")
}
rep() {
  local run status verdict
  run="$(mktemp -d /tmp/plan106-rep-XXXXXX)" || return 2
  (
    cd "$run" || exit 2
    git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $run is inside a git repository"; exit 2; }
    # env -i: a `claude -p` child of a Desktop session inherits its environment (effort, session id, messaging socket), and --setting-sources "" does not clear it.
    env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" PATH="$PATH" SHELL="$SHELL" TMPDIR="${TMPDIR:-/tmp}" LANG="${LANG:-en_US.UTF-8}" \
      CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
      claude -p --model "$MODEL" --tools "" --strict-mcp-config --setting-sources "" \
      --no-session-persistence --output-format json --max-budget-usd 0.50 \
      ${FLAGS[@]+"${FLAGS[@]}"} < "$PROMPT" > "$SCRATCH/rep$1.json" 2> "$SCRATCH/rep$1.err"
  )
  status=$?
  [ -s "$SCRATCH/rep$1.err" ] || rm -f "$SCRATCH/rep$1.err"
  verdict="$(postprocess "$SCRATCH/rep$1.json" "$OUT/rep$1.json")" || { echo "rep$1 kit error: postprocess failed"; return 2; }
  if [ "$verdict" = kept ]; then echo "rep$1 exit=$status"; else echo "rep$1 $verdict exit=$status"; fi
}
rep "$FIRST"
i=$((FIRST + 1))
while [ "$i" -le "$LAST" ]; do
  rep "$i" &
  i=$((i + 1))
done
wait

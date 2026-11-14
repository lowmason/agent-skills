#!/bin/bash
# Run decision-only reps for plan 97's reviewer micro-test. Each rep is a fresh `claude -p` with no
# tools, run from its own new, empty directory under /tmp, outside every repository.
# `--setting-sources ""` keeps user-level context out of the reps: the output style, plugin
# SessionStart hooks, ~/.claude/CLAUDE.md and ~/.claude/rules/. CLAUDE_CODE_DISABLE_AUTO_MEMORY
# drops the auto-memory section. Check a new Claude Code version with isolation_probe.txt first
# (probe.sh, whose `claude` command line is this script's, byte for byte).
# Plan 77 deviation (a): each rep runs under `env -i`, so a rep launched from a Claude desktop
# app session does not inherit the app's environment (its messaging socket and token, session
# id, effort level, account variables or LLM_WIKI_ROOT). Only HOME, USER, LOGNAME, PATH, SHELL,
# TMPDIR and LANG pass through, each only when it is set, plus the two CLAUDE_CODE_DISABLE_*
# variables.
# Usage: run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model> [<budget>]
# <budget> is the per-rep --max-budget-usd cap, 0.50 when omitted.
# The first rep runs alone and writes the prompt cache; the others then run together.
# Plan 97 copy of plan 93's runner. Three fixes from the report-source-match runner
# (specs/baseline/red-baseline-report-source-match/kit/run_reps.sh:18-50): the rep range is checked
# before the overwrite guard, each rep's status (its `claude` exit status, or 2 for a kit error)
# reaches the script's exit status, and a failed first rep stops the batch. The raw rep<N>.json
# (it holds a session id) and rep<N>.err go to ~/.cache/agent-skills/scratch/plan97/reviewer/<out-dir's
# parent name>/<out-dir name>/, outside the repository. Into <out-dir> goes rep<N>.json, a copy of
# the raw JSON without its session_id and uuid, with $HOME written as `~`, $TMPDIR as `$TMPDIR` and
# the user's identity forms as tokens (kit_identity.py: the name, its parts, the email address, its
# local part and $USER, read from local config at run time). show_reps.py reads that copy.
set -u
FLAGS=()
KEEP=()
for v in HOME USER LOGNAME PATH SHELL TMPDIR LANG; do
  val="$(printenv "$v")" && KEEP+=("$v=$val")
done
CLAUDE_BIN="$(command -v claude)" || { echo "refusing: no claude on PATH"; exit 2; }
[ "$#" -ge 5 ] && [ "$#" -le 6 ] || { echo "usage: run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model> [<budget>]"; exit 2; }
KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
[ -f "$1" ] || { echo "refusing: no prompt file $1"; exit 2; }
PROMPT="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" || exit 2
OUT="$(mkdir -p "$2" && cd "$2" && pwd)" || exit 2
FIRST="$3"
LAST="$4"
MODEL="$5"
BUDGET="${6:-0.50}"
SCRATCH="$HOME/.cache/agent-skills/scratch/plan97/reviewer/$(basename "$(dirname "$OUT")")/$(basename "$OUT")"
# Check the range before the overwrite guard: a reversed or non-numeric range would skip the guard.
for n in "$FIRST" "$LAST"; do
  case "$n" in
    '' | *[!0-9]*) echo "refusing: first-rep and last-rep must be positive integers"; exit 2 ;;
  esac
done
[ "$FIRST" -ge 1 ] && [ "$FIRST" -le "$LAST" ] || { echo "refusing: need 1 <= first-rep <= last-rep"; exit 2; }
mkdir -p "$SCRATCH" || exit 2
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  [ -e "$OUT/rep$i.json" ] && { echo "refusing: $OUT/rep$i.json exists"; exit 2; }
  [ -e "$SCRATCH/rep$i.json" ] && { echo "refusing: $SCRATCH/rep$i.json exists"; exit 2; }
  i=$((i + 1))
done
# rep returns the status of its `claude` run, or 2 for a kit error, so a failed rep reaches the
# script's exit status.
rep() {
  local run status
  run="$(mktemp -d /tmp/mt-review-XXXXXX)" || return 2
  (
    cd "$run" || exit 2
    git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $run is inside a git repository"; exit 2; }
    env -i ${KEEP[@]+"${KEEP[@]}"} CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
      "$CLAUDE_BIN" -p --model "$MODEL" --tools "" --strict-mcp-config --setting-sources "" --disable-slash-commands \
      --no-session-persistence --output-format json --max-budget-usd "$BUDGET" \
      ${FLAGS[@]+"${FLAGS[@]}"} < "$PROMPT" > "$SCRATCH/rep$1.json" 2> "$SCRATCH/rep$1.err"
  )
  status=$?
  [ -s "$SCRATCH/rep$1.err" ] || rm -f "$SCRATCH/rep$1.err"
  (cd "$KIT" && uv run --no-project -q python - "$SCRATCH/rep$1.json" "$OUT/rep$1.json" <<'EOF'
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.getcwd())
import kit_identity  # noqa: E402 (the kit's directory is the cwd)

raw, dest = Path(sys.argv[1]), Path(sys.argv[2])
text = raw.read_text(errors='replace') if raw.exists() else ''
try:
    data = json.loads(text or '{}')
except json.JSONDecodeError:
    data = None
if isinstance(data, dict):
    for key in ('session_id', 'uuid'):
        data.pop(key, None)
    text = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
tmpdir = os.environ.get('TMPDIR', '').rstrip('/')
if tmpdir:
    text = text.replace('/private' + tmpdir, '$TMPDIR').replace(tmpdir, '$TMPDIR')
text = kit_identity.scrub(text.replace(os.environ['HOME'], '~'))
dest.with_suffix('.tmp').write_text(text)
os.replace(dest.with_suffix('.tmp'), dest)
EOF
  ) || { echo "rep$1 kit error: the copy step failed"; return 2; }
  echo "rep$1 exit=$status"
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

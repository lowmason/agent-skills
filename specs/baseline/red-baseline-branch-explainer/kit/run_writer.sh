#!/bin/bash
# Run writer reps for plan 94's branch explainer probe. Each rep gets a new folder
# /tmp/plan94-rep-XXXXXX that holds an isolated fixture repository (repo/), an output folder (out/)
# and, for the treatment, the round's brief (brief/branch-explainer-prompt.md). The writer is a
# fresh Opus `claude -p` with repository tools, run from repo/ under `env -i` with
# `--setting-sources ""` and no auto-memory, as run_plain.sh is.
# Usage: run_writer.sh <arm> <fixture> <out-dir> <first> <last> <cap> [<brief>]
# <arm> is control, treatment (needs <brief>), probe or permcheck. permcheck drops `--add-dir out`.
# Each rep writes rep<N>.md (the explainer, when one was written), rep<N>.audit.json and
# rep<N>.result.json in <out-dir>, and its full stream to
# ~/.cache/agent-skills/scratch/plan94/streams/<out-dir's last two components>/rep<N>.jsonl.
# The first rep runs alone and the rest in parallel. The fixture repository is removed after the run.
set -u
KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
ROOT="$(git -C "$KIT" rev-parse --show-toplevel)" || exit 2
ARM="${1:?usage: run_writer.sh <arm> <fixture> <out-dir> <first> <last> <cap> [<brief>]}"
FX="${2:?fixture}"
OUT="$(mkdir -p "${3:?out-dir}" && cd "$3" && pwd)" || exit 2
FIRST="${4:?first}"
LAST="${5:?last}"
CAP="${6:?cap}"
BRIEF=""
case "$ARM" in
  control|probe|permcheck) ;;
  treatment)
    [ -f "${7:-}" ] || { echo "refusing: treatment needs a brief file"; exit 2; }
    BRIEF="$(cd "$(dirname "$7")" && pwd)/$(basename "$7")" ;;
  *) echo "refusing: unknown arm $ARM"; exit 2 ;;
esac
SCRATCH="$HOME/.cache/agent-skills/scratch/plan94"
TAIL="$(basename "$(dirname "$OUT")")/$(basename "$OUT")"
STREAMS="$SCRATCH/streams/$TAIL"
PROMPTS="$SCRATCH/prompts/$TAIL"
mkdir -p "$STREAMS" "$PROMPTS" || exit 2
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  for f in "$OUT/rep$i".* "$STREAMS/rep$i.jsonl"; do
    [ -e "$f" ] && { echo "refusing: $f exists"; exit 2; }
  done
  i=$((i + 1))
done
KEEP=()
for v in HOME USER LOGNAME PATH SHELL TMPDIR LANG; do
  val="$(printenv "$v")" && KEEP+=("$v=$val")
done
CLAUDE_BIN="$(command -v claude)" || { echo "refusing: no claude on PATH"; exit 2; }
kit() { (cd "$ROOT" && uv run --quiet "$KIT/kit.py" "$@"); }
rep() {
  local n="$1" run flags
  run="$(mktemp -d /tmp/plan94-rep-XXXXXX)" || return 2
  mkdir -p "$run/out" || return 2
  kit fixture "$FX" "$run" > /dev/null || { echo "rep$n: fixture failed"; return 2; }
  if [ "$ARM" = treatment ]; then
    mkdir -p "$run/brief" && cp "$BRIEF" "$run/brief/branch-explainer-prompt.md" || return 2
  fi
  kit writer-prompt "$ARM" "$FX" "$run" > "$PROMPTS/writer-rep$n.txt" || return 2
  flags=(-p --model claude-opus-5-5 --tools "Bash,Read,Write,Grep,Glob"
    --permission-mode acceptEdits --allowedTools Bash --permission-prompts none)
  [ "$ARM" = permcheck ] || flags+=(--add-dir "$run/out")
  [ "$ARM" = treatment ] && flags+=(--add-dir "$run/brief")
  flags+=(--strict-mcp-config --setting-sources "" --disable-slash-commands
    --no-session-persistence --output-format stream-json --verbose --max-budget-usd "$CAP")
  (
    cd "$run/repo" || exit 2
    env -i ${KEEP[@]+"${KEEP[@]}"} CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
      "$CLAUDE_BIN" "${flags[@]}" < "$PROMPTS/writer-rep$n.txt" > "$STREAMS/rep$n.jsonl" 2> "$OUT/rep$n.err"
  )
  echo "rep$n exit=$? folder=$run"
  [ -s "$OUT/rep$n.err" ] || rm -f "$OUT/rep$n.err"
  [ -f "$run/out/explainer.md" ] && cp "$run/out/explainer.md" "$OUT/rep$n.md"
  ls -A "$run/out" | sed "s/^/rep$n out\/: /"
  kit audit "$STREAMS/rep$n.jsonl" "$run" "$OUT/rep$n" | sed "s/^/rep$n /"
  case "$run" in
    /tmp/plan94-rep-*) rm -rf "$run/repo" ;;
  esac
}
rep "$FIRST"
i=$((FIRST + 1))
while [ "$i" -le "$LAST" ]; do
  rep "$i" &
  i=$((i + 1))
done
wait

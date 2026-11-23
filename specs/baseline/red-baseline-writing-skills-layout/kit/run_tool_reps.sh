#!/bin/bash
# Run plan 105's tools reps (cases T1-T3), one at a time. bash 3.2. Copy of plan 104's run_reps.sh
# (specs/baseline/red-baseline-mutant-screen-runs/kit/run_reps.sh), cut as plan 105's Task 3 says: no
# .sdd workspace, no setup.sh, no @REPO@ or @BASE@ token, no role-to-model map and no mutant-run audit.
# Usage: run_tool_reps.sh <prompt-dir> <case> <out-dir> <first> <last> <model>
# <prompt-dir> is build_prompts.py's output. <out-dir> ends in <case>/<arm>/<model>, such as
# T2/old/claude-sonnet-5-5, where <arm> is MANIFEST.txt's arm. <model> is claude-sonnet-5-5 or
# claude-opus-5-5, and the cap is $1.50 for both (common.sh).
#
# Before each rep, WSL_ROOT must be empty (exit 3 otherwise), and the skill copy and the prompt must
# match MANIFEST.txt (rep_tools.py check-copy; exit 2 otherwise). Each rep then:
#   1. makes its folder WSL_ROOT/rep<N>/ (common.sh), copies fixtures/<case>/repo/ to repo/, runs
#      git init, sets a local user (Developer, developer@example.invalid) and commit.gpgsign false,
#      and commits: that commit is the rep's BASE;
#   2. copies the prompt to the scratch folder and runs claude (common.sh) on it;
#   3. runs rep_tools.py summarize, which writes <out-dir>/rep<N>/ (final.diff against BASE, new files
#      included, and summary.json, with the skill copy check after the rep);
#   4. fails the rep (kit error) when a file it wrote still holds credential_expires_at;
#   5. parks the folder as <scratch>/rep<N>-folder, where <scratch> is WSL_SCRATCH/<case>/<arm>/<model>/,
#      beside the raw stream rep<N>.jsonl, its stderr, the prompt and the unscrubbed final.diff
#      (rep<N>-orig/). A trap parks the folder however the rep ends.
# A rep's status is its claude exit status, or 2 for a kit error. A kit error stops the batch. The
# script exits 0 when every rep exits 0, 2 after a kit error or a refusal, 3 for a non-empty root,
# and 1 otherwise.
set -u
[ "$#" -eq 6 ] || { echo "usage: run_tool_reps.sh <prompt-dir> <case> <out-dir> <first> <last> <model>"; exit 2; }
KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
. "$KIT/common.sh"
FIXTURES=${WSL_FIXTURES:-$KIT/fixtures}
PROMPTS="$(cd "$1" && pwd)" || exit 2
CASE="$2"
FIX="$FIXTURES/$CASE"
FIRST="$4"
LAST="$5"
MODEL="$6"
check_model "$MODEL" || { echo "refusing: model $MODEL is not claude-sonnet-5-5 or claude-opus-5-5"; exit 2; }
PROMPT="$PROMPTS/$CASE.txt"
MANIFEST="$PROMPTS/MANIFEST.txt"
[ -f "$PROMPT" ] && [ -f "$MANIFEST" ] || { echo "refusing: no $PROMPT or $MANIFEST"; exit 2; }
[ -d "$FIX/repo" ] || { echo "refusing: no fixture $FIX"; exit 2; }
ARM="$(awk '$1 == "arm" { print $2 }' "$MANIFEST")"
[ -n "$ARM" ] || { echo "refusing: MANIFEST.txt names no arm"; exit 2; }
OUT="$(mkdir -p "$3" && cd "$3" && pwd)" || exit 2
[ "$(basename "$OUT")" = "$MODEL" ] && [ "$(basename "$(dirname "$OUT")")" = "$ARM" ] \
  && [ "$(basename "$(dirname "$(dirname "$OUT")")")" = "$CASE" ] \
  || { echo "refusing: $OUT does not end in $CASE/$ARM/$MODEL"; exit 2; }
SCRATCH="$WSL_SCRATCH/$CASE/$ARM/$MODEL"
SKILL="$(awk '$1 == "skill-copy-root" { print $2 }' "$MANIFEST")"
[ -n "$SKILL" ] || { echo "refusing: MANIFEST.txt names no skill-copy-root"; exit 2; }
[ -n "$CLAUDE_BIN" ] && [ -x "$CLAUDE_BIN" ] || { echo "refusing: no claude binary (set CLAUDE_BIN)"; exit 2; }
for n in "$FIRST" "$LAST"; do
  case "$n" in
    '' | *[!0-9]*) echo "refusing: first and last must be positive integers"; exit 2 ;;
  esac
done
[ "$FIRST" -ge 1 ] && [ "$FIRST" -le "$LAST" ] || { echo "refusing: need 1 <= first <= last"; exit 2; }
mkdir -p "$SCRATCH" || exit 2
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  [ -e "$OUT/rep$i" ] && { echo "refusing: $OUT/rep$i exists"; exit 2; }
  [ -e "$SCRATCH/rep$i.jsonl" ] || [ -e "$SCRATCH/rep$i-folder" ] && { echo "refusing: $SCRATCH/rep$i exists"; exit 2; }
  i=$((i + 1))
done

# rep_tools.py runs from the kit folder, so uv reads the repository's .python-version.
tools() {
  (cd "$KIT" && uv run --no-project -q python "$KIT/rep_tools.py" "$@")
}

CURRENT=''
CURRENT_N=''
park_current() {
  if [ -n "$CURRENT" ] && [ -d "$CURRENT" ]; then
    park "$CURRENT" "$SCRATCH/rep$CURRENT_N-folder" || echo "could not park $CURRENT"
  fi
  CURRENT=''
}
trap park_current EXIT

kit_failed() {
  printf '{"case": "%s", "rep": %s, "arm": "%s", "model": "%s", "kit_error": "%s"}\n' "$CASE" "$1" "$ARM" "$MODEL" \
    "$2" > "$OUT/rep$1/summary.json.tmp"
  mv "$OUT/rep$1/summary.json.tmp" "$OUT/rep$1/summary.json"
  echo "rep$1 kit error: $2"
}

rep() {
  local n="$1" dir repo base start status left
  require_empty_root
  tools check-copy "$MANIFEST" "$PROMPT" || { echo "refusing: the skill copy or the prompt differs from $MANIFEST"; exit 2; }
  mkdir "$OUT/rep$n" || return 2
  dir="$WSL_ROOT/rep$n"
  CURRENT="$dir"
  CURRENT_N="$n"
  make_folder "$dir" || { kit_failed "$n" 'folder setup failed'; return 2; }
  dir="$(cd "$dir" && pwd -P)"
  CURRENT="$dir"
  repo="$dir/repo"
  rmdir "$repo" && cp -R "$FIX/repo" "$repo" \
    && git -C "$repo" init -q \
    && git -C "$repo" config user.name 'Developer' \
    && git -C "$repo" config user.email 'developer@example.invalid' \
    && git -C "$repo" config commit.gpgsign false \
    && git -C "$repo" add -A \
    && git -C "$repo" commit -q -m 'Start the project' \
    || { kit_failed "$n" 'repository setup failed'; return 2; }
  base="$(git -C "$repo" rev-parse HEAD)"
  cp "$PROMPT" "$SCRATCH/rep$n.prompt.txt" || { kit_failed "$n" 'prompt copy failed'; return 2; }
  start="$(date +%s)"
  run_claude "$dir" "$MODEL" "$SCRATCH/rep$n.prompt.txt" "$SCRATCH/rep$n.jsonl" "$SCRATCH/rep$n.err"
  status=$?
  tools summarize --stream "$SCRATCH/rep$n.jsonl" --err "$SCRATCH/rep$n.err" \
    --dest "$OUT/rep$n" --orig "$SCRATCH/rep$n-orig" --case "$CASE" --arm "$ARM" --model "$MODEL" --cap "$CAP" \
    --rep "$n" --rep-dir "$dir" --base "$base" --prompt "$SCRATCH/rep$n.prompt.txt" --status "$status" \
    --wall "$(($(date +%s) - start))" --manifest "$MANIFEST" \
    || { kit_failed "$n" 'summary step failed'; return 2; }
  left="$(grep -rl "$FIELD" "$OUT/rep$n" "$SCRATCH/rep$n.jsonl" 2> /dev/null | sed "s|^$OUT/rep$n/||" | tr '\n' ' ')"
  if [ -n "$left" ]; then
    kit_failed "$n" "the strip left $FIELD in: $left"
    return 2
  fi
  if grep -q '"kit_error"' "$OUT/rep$n/summary.json"; then
    return 2
  fi
  return "$status"
}

failed=0
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  rep "$i"
  status=$?
  park_current
  if [ "$status" -eq 2 ]; then
    echo "rep$i: kit error, so the batch stops"
    exit 2
  fi
  [ "$status" -eq 0 ] || failed=$((failed + 1))
  i=$((i + 1))
done
[ "$failed" -eq 0 ] || { echo "$failed rep(s) exited non-zero"; exit 1; }

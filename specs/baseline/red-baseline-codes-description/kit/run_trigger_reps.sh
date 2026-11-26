#!/bin/bash
# Run plan 111's trigger reps (Task 4), one at a time, each in its own session. bash 3.2.
# Usage: run_trigger_reps.sh <ref> <arm> <prompt-id> <out-dir> <first> <last> <model>
# <ref> names the commit whose skills/ folder the rep lists (git archive <ref> skills/). <arm> is old, new or
# pilot. <prompt-id> is P1-P5 or N1-N4 (trigger_prompts.py), or probe, which runs isolation_probe.txt as a
# trigger rep. <out-dir> ends in <prompt-id>/<arm>/<model>. <model> is claude-sonnet-5-5 or claude-opus-5-5,
# and the cap is $0.25 for both (common.sh).
#
# Copy of plan 107's run_trigger_reps.sh (specs/baseline/red-baseline-writing-skills-tests/kit/), changed for
# plan 111: there is one condition, so the <condition> argument and its folder level are gone; no plugin skill
# is copied in, since the neighbors under test (geographic-codes and bls-data-context) are in the ref's skills/;
# the runner refuses a ref whose skills/ lacks a name of fixtures/trigger/listing.txt and a rep root inside a
# git repository; the settings come from common.sh (Bash and Read(~/**) denied, reads fenced to repo/); and the
# rep folder is removed after the rep, not parked.
#
# Each rep, from a new rep folder CD_TROOT/rep<N>/ with repo/, home/ and tmp/:
#   1. repo/ is a copy of fixtures/trigger/repo/ (git init, one commit);
#   2. home/.claude/ gets `git archive <ref> skills/`, so the skills sit in home/.claude/skills/, and
#      settings.json, common.sh's TRIGGER_SETTINGS. Claude reads it through --setting-sources user;
#   3. one claude -p call runs from repo/ under `env -i` with --tools and --allowedTools Read,Glob,Grep,Skill,
#      --max-turns 3, --max-budget-usd 0.25 and CLAUDE_CODE_DISABLE_AUTO_MEMORY=1. It has no
#      --disable-slash-commands and no --settings flag, because either would hide the listing under test;
#   4. rep_tools.py summarize runs rule 4's check on the raw stream, then strips credential_expires_at and
#      origin from the stream and writes <out-dir>/rep<N>/summary.json;
#   5. a saved file that still holds credential_expires_at or an origin key is a kit error;
#   6. the rep folder is removed. The stream rep<N>.jsonl, the prompt and stderr stay in
#      <scratch> = CD_TRIGGER_SCRATCH/<prompt-id>/<arm>/<model>/.
# Exit: 0 when every rep exits 0, 2 for a kit error or a refusal (a kit error stops the batch), 3 for a
# non-empty root, 1 otherwise. A rep that stops on --max-turns or its budget exits non-zero: that is a normal
# end for a trigger rep, so the batch goes on, and audit.py does not void it.
set -u
[ "$#" -eq 7 ] || { echo "usage: run_trigger_reps.sh <ref> <arm> <prompt-id> <out-dir> <first> <last> <model>"; exit 2; }
KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
. "$KIT/common.sh"
FIXTURES=${CD_FIXTURES:-$KIT/fixtures}
REF="$1"
ARM="$2"
PID="$3"
FIRST="$5"
LAST="$6"
MODEL="$7"
case "$ARM" in
  old | new | pilot) ;;
  *) echo "refusing: arm $ARM is not old, new or pilot"; exit 2 ;;
esac
check_model "$MODEL" || { echo "refusing: model $MODEL is not claude-sonnet-5-5 or claude-opus-5-5"; exit 2; }
tools() {
  (cd "$KIT" && uv run --no-project -q python "$KIT/rep_tools.py" "$@")
}
prompt_text() {
  (cd "$KIT" && uv run --no-project -q python "$KIT/trigger_prompts.py" "$1")
}
prompt_text "$PID" > /dev/null 2>&1 || { echo "refusing: $PID is not a trigger prompt id or probe"; exit 2; }
[ -d "$FIXTURES/trigger/repo" ] || { echo "refusing: no fixture $FIXTURES/trigger/repo"; exit 2; }
[ -f "$FIXTURES/trigger/listing.txt" ] || { echo "refusing: no listing $FIXTURES/trigger/listing.txt"; exit 2; }
[ -n "$CLAUDE_BIN" ] && [ -x "$CLAUDE_BIN" ] || { echo "refusing: no claude binary (set CLAUDE_BIN)"; exit 2; }
for n in "$FIRST" "$LAST"; do
  case "$n" in
    '' | *[!0-9]*) echo "refusing: first and last must be positive integers"; exit 2 ;;
  esac
done
[ "$FIRST" -ge 1 ] && [ "$FIRST" -le "$LAST" ] || { echo "refusing: need 1 <= first <= last"; exit 2; }
OUT="$(mkdir -p "$4" && cd "$4" && pwd)" || exit 2
[ "$(basename "$OUT")" = "$MODEL" ] && [ "$(basename "$(dirname "$OUT")")" = "$ARM" ] \
  && [ "$(basename "$(dirname "$(dirname "$OUT")")")" = "$PID" ] \
  || { echo "refusing: $OUT does not end in $PID/$ARM/$MODEL"; exit 2; }
SCRATCH="$CD_TRIGGER_SCRATCH/$PID/$ARM/$MODEL"

REPO="${CD_REPO:-$(git -C "$KIT" rev-parse --show-toplevel 2> /dev/null)}"
[ -n "$REPO" ] || { echo "refusing: $KIT is not inside a git repository (set CD_REPO)"; exit 2; }
SHA="$(git -C "$REPO" rev-parse --verify --quiet "$REF^{commit}")" || { echo "refusing: $REF names no commit"; exit 2; }
for name in $(cat "$FIXTURES/trigger/listing.txt"); do
  git -C "$REPO" ls-tree --name-only "$SHA" "skills/$name/SKILL.md" | grep -q . \
    || { echo "refusing: skills/$name/SKILL.md is missing at $REF, so the listing check would void every rep"; exit 2; }
done
mkdir -p "$CD_TROOT" || exit 2
if git -C "$CD_TROOT" rev-parse --git-dir > /dev/null 2>&1; then
  echo "refusing: $CD_TROOT is inside a git repository; a rep folder must be outside every repository"
  exit 2
fi
mkdir -p "$SCRATCH" || exit 2
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  [ -e "$OUT/rep$i" ] && { echo "refusing: $OUT/rep$i exists"; exit 2; }
  [ -e "$SCRATCH/rep$i.jsonl" ] && { echo "refusing: $SCRATCH/rep$i exists"; exit 2; }
  i=$((i + 1))
done

CURRENT=''
remove_current() {
  if [ -n "$CURRENT" ] && [ -d "$CURRENT" ]; then
    remove_folder "$CURRENT" || echo "could not remove $CURRENT"
  fi
  CURRENT=''
}
trap remove_current EXIT

kit_failed() {
  printf '{"prompt": "%s", "rep": %s, "arm": "%s", "model": "%s", "kit_error": "%s"}\n' "$PID" "$1" "$ARM" \
    "$MODEL" "$2" > "$OUT/rep$1/summary.json.tmp"
  mv "$OUT/rep$1/summary.json.tmp" "$OUT/rep$1/summary.json"
  echo "rep$1 kit error: $2"
}

rep() {
  local n="$1" dir repo start status left
  require_empty_root "$CD_TROOT"
  mkdir "$OUT/rep$n" || return 2
  dir="$CD_TROOT/rep$n"
  CURRENT="$dir"
  make_folder "$dir" || { kit_failed "$n" 'folder setup failed'; return 2; }
  dir="$(cd "$dir" && pwd -P)"
  CURRENT="$dir"
  repo="$dir/repo"
  rmdir "$repo" && cp -R "$FIXTURES/trigger/repo" "$repo" \
    && git -C "$repo" init -q \
    && git -C "$repo" config user.name 'Developer' \
    && git -C "$repo" config user.email 'developer@example.invalid' \
    && git -C "$repo" config commit.gpgsign false \
    && git -C "$repo" add -A \
    && git -C "$repo" commit -q -m 'Start the project' \
    || { kit_failed "$n" 'repository setup failed'; return 2; }
  mkdir -p "$dir/home/.claude" \
    && git -C "$REPO" archive --format=tar "$SHA" skills/ | tar -x -C "$dir/home/.claude" \
    || { kit_failed "$n" 'skills archive failed'; return 2; }
  printf '%s\n' "$TRIGGER_SETTINGS" > "$dir/home/.claude/settings.json" || { kit_failed "$n" 'settings failed'; return 2; }
  prompt_text "$PID" > "$SCRATCH/rep$n.prompt.txt" || { kit_failed "$n" 'prompt failed'; return 2; }
  start="$(date +%s)"
  (
    cd "$repo" || exit 2
    env -i HOME="$dir/home" USER="$USER" LOGNAME="$LOGNAME" PATH="$REP_PATH" SHELL="$SHELL" \
      TMPDIR="$dir/tmp" LANG="${LANG-}" \
      CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
      "$CLAUDE_BIN" -p --model "$MODEL" --tools "$TRIGGER_TOOLS" --allowedTools "$TRIGGER_TOOLS" \
      --strict-mcp-config --setting-sources user --no-session-persistence \
      --max-turns 3 --max-budget-usd "$TRIGGER_CAP" --output-format stream-json --verbose \
      < "$SCRATCH/rep$n.prompt.txt" > "$SCRATCH/rep$n.jsonl" 2> "$SCRATCH/rep$n.err"
  )
  status=$?
  tools summarize --stream "$SCRATCH/rep$n.jsonl" --err "$SCRATCH/rep$n.err" --dest "$OUT/rep$n" \
    --prompt-id "$PID" --arm "$ARM" --model "$MODEL" --cap "$TRIGGER_CAP" --rep "$n" --rep-dir "$dir" \
    --prompt "$SCRATCH/rep$n.prompt.txt" --status "$status" --wall "$(($(date +%s) - start))" \
    || { kit_failed "$n" 'summary step failed'; return 2; }
  left="$(grep -lE "$FIELD|\"origin\"[[:space:]]*:" "$OUT/rep$n/summary.json" "$SCRATCH/rep$n.jsonl" 2> /dev/null \
    | sed -e "s|^$OUT/rep$n/||" -e "s|^$SCRATCH/||" | tr '\n' ' ')"
  if [ -n "$left" ]; then
    kit_failed "$n" "the strip left $FIELD or origin in: $left"
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
  remove_current
  if [ "$status" -eq 2 ]; then
    echo "rep$i: kit error, so the batch stops"
    exit 2
  fi
  [ "$status" -eq 0 ] || failed=$((failed + 1))
  i=$((i + 1))
done
[ "$failed" -eq 0 ] || { echo "$failed rep(s) exited non-zero"; exit 1; }

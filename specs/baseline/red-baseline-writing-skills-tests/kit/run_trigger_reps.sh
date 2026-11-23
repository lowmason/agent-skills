#!/bin/bash
# Run plan 107's trigger reps (Task 6), one at a time, each in its own session. bash 3.2.
# Usage: run_trigger_reps.sh <ref> <arm> <condition> <prompt-id> <out-dir> <first> <last> <model>
# <ref> names the commit whose skills/ folder the rep lists (git archive <ref> skills/). <arm> is old, new
# or pilot. <condition> is full, or cut150 (skillListingMaxDescChars 150, which imitates Codex's cut).
# <prompt-id> is P1-P5 or N1-N3 (trigger_prompts.py). <out-dir> ends in <prompt>/<arm>/<condition>/<model>.
# <model> is claude-sonnet-5-5 or claude-opus-5-5, and the cap is $0.25 for both (common.sh).
#
# The two competitor skills (plugin-dev's skill-development and the official skill-creator) are copied from
# the local plugin cache, so their text never enters the repository and no committed path names a user. Their
# source folders come from the environment:
#   WST_COMPETITOR_PLUGIN_DEV      the skill-development folder (it holds SKILL.md)
#   WST_COMPETITOR_SKILL_CREATOR   the skill-creator folder (it holds SKILL.md)
# The runner refuses a missing variable, a folder without SKILL.md, and a ref whose skills/ already holds a
# skill of either name. It writes <out-dir>/competitors.txt (each competitor's name and the sha256 of its
# SKILL.md) on the first rep and refuses a later batch whose competitor differs, so the old and new arms
# list the same competitors.
#
# Each rep, as plan 100's runner does, from a rep folder WST_TROOT/rep<N>/ with repo/, home/ and tmp/:
#   1. repo/ is a copy of fixtures/trigger/repo/ (git init, one commit: the rep's BASE);
#   2. home/.claude/ gets `git archive <ref> skills/`, so the skills sit in home/.claude/skills/, then the
#      two competitors in home/.claude/skills/<name>/, and settings.json: the deny list,
#      "syncClaudeAiSkills": false, "skillListingBudgetFraction": 0.05 and, for cut150,
#      "skillListingMaxDescChars": 150. Claude reads it through --setting-sources user;
#   3. claude -p runs from repo/ under `env -i` with --tools and --allowedTools Read,Glob,Grep,Skill,
#      --max-turns 3, --max-budget-usd 0.25 and CLAUDE_CODE_DISABLE_AUTO_MEMORY=1. It has no
#      --disable-slash-commands and no --settings flag, because either would hide the listing under test;
#   4. rep_tools.py summarize writes <out-dir>/rep<N>/ (summary.json with the condition; no skill copy);
#   5. a file that still holds credential_expires_at is a kit error, and the folder is parked as
#      <scratch>/rep<N>-folder, where <scratch> is WST_TRIGGER_SCRATCH/<prompt>/<arm>/<condition>/<model>/,
#      beside the raw stream rep<N>.jsonl.
# Exit: 0 when every rep exits 0, 2 for a kit error or a refusal (a kit error stops the batch), 3 for a
# non-empty root, 1 otherwise. A rep that stops on --max-turns or its budget exits non-zero: that is a normal
# end for a trigger rep, so the batch goes on, and audit.py does not void it.
set -u
[ "$#" -eq 8 ] || { echo "usage: run_trigger_reps.sh <ref> <arm> <condition> <prompt-id> <out-dir> <first> <last> <model>"; exit 2; }
KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
. "$KIT/common.sh"
FIXTURES=${WST_FIXTURES:-$KIT/fixtures}
REF="$1"
ARM="$2"
COND="$3"
PID="$4"
FIRST="$6"
LAST="$7"
MODEL="$8"
COMPETITORS='skill-development skill-creator'
case "$ARM" in
  old | new | pilot) ;;
  *) echo "refusing: arm $ARM is not old, new or pilot"; exit 2 ;;
esac
case "$COND" in
  full | cut150) ;;
  *) echo "refusing: condition $COND is not full or cut150"; exit 2 ;;
esac
check_model "$MODEL" || { echo "refusing: model $MODEL is not claude-sonnet-5-5 or claude-opus-5-5"; exit 2; }
tools() {
  (cd "$KIT" && uv run --no-project -q python "$KIT/rep_tools.py" "$@")
}
(cd "$KIT" && uv run --no-project -q python "$KIT/trigger_prompts.py" "$PID" > /dev/null 2>&1) \
  || { echo "refusing: $PID is not a trigger prompt id"; exit 2; }
[ -d "$FIXTURES/trigger/repo" ] || { echo "refusing: no fixture $FIXTURES/trigger/repo"; exit 2; }
[ -n "$CLAUDE_BIN" ] && [ -x "$CLAUDE_BIN" ] || { echo "refusing: no claude binary (set CLAUDE_BIN)"; exit 2; }
for n in "$FIRST" "$LAST"; do
  case "$n" in
    '' | *[!0-9]*) echo "refusing: first and last must be positive integers"; exit 2 ;;
  esac
done
[ "$FIRST" -ge 1 ] && [ "$FIRST" -le "$LAST" ] || { echo "refusing: need 1 <= first <= last"; exit 2; }
OUT="$(mkdir -p "$5" && cd "$5" && pwd)" || exit 2
[ "$(basename "$OUT")" = "$MODEL" ] && [ "$(basename "$(dirname "$OUT")")" = "$COND" ] \
  && [ "$(basename "$(dirname "$(dirname "$OUT")")")" = "$ARM" ] \
  && [ "$(basename "$(dirname "$(dirname "$(dirname "$OUT")")")")" = "$PID" ] \
  || { echo "refusing: $OUT does not end in $PID/$ARM/$COND/$MODEL"; exit 2; }
SCRATCH="$WST_TRIGGER_SCRATCH/$PID/$ARM/$COND/$MODEL"

REPO="${WST_REPO:-$(git -C "$KIT" rev-parse --show-toplevel 2> /dev/null)}"
[ -n "$REPO" ] || { echo "refusing: $KIT is not inside a git repository (set WST_REPO)"; exit 2; }
SHA="$(git -C "$REPO" rev-parse --verify --quiet "$REF^{commit}")" || { echo "refusing: $REF names no commit"; exit 2; }

competitor_source() {
  case "$1" in
    skill-development) echo "${WST_COMPETITOR_PLUGIN_DEV-}" ;;
    skill-creator) echo "${WST_COMPETITOR_SKILL_CREATOR-}" ;;
  esac
}
competitor_variable() {
  case "$1" in
    skill-development) echo WST_COMPETITOR_PLUGIN_DEV ;;
    skill-creator) echo WST_COMPETITOR_SKILL_CREATOR ;;
  esac
}
NOTES=''
for name in $COMPETITORS; do
  src="$(competitor_source "$name")"
  [ -n "$src" ] || { echo "refusing: $(competitor_variable "$name") is not set (the $name skill folder)"; exit 2; }
  [ -f "$src/SKILL.md" ] || { echo "refusing: $(competitor_variable "$name") holds no SKILL.md: $src"; exit 2; }
  if git -C "$REPO" ls-tree --name-only "$SHA" "skills/$name" | grep -q .; then
    echo "refusing: skills/$name at $REF collides with the competitor $name"
    exit 2
  fi
  NOTES="$NOTES$name $(shasum -a 256 "$src/SKILL.md" | awk '{ print $1 }')
"
done
mkdir -p "$SCRATCH" || exit 2
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  [ -e "$OUT/rep$i" ] && { echo "refusing: $OUT/rep$i exists"; exit 2; }
  [ -e "$SCRATCH/rep$i.jsonl" ] || [ -e "$SCRATCH/rep$i-folder" ] && { echo "refusing: $SCRATCH/rep$i exists"; exit 2; }
  i=$((i + 1))
done
if [ -e "$OUT/competitors.txt" ]; then
  printf '%s' "$NOTES" | cmp -s - "$OUT/competitors.txt" \
    || { echo "refusing: a competitor skill changed since the first rep of $OUT (see competitors.txt)"; exit 2; }
else
  printf '%s' "$NOTES" > "$OUT/competitors.txt"
fi

trigger_settings() {
  local s='{"permissions":{"deny":['"$DENY"']},"syncClaudeAiSkills":false,"skillListingBudgetFraction":0.05'
  if [ "$COND" = cut150 ]; then s="$s"',"skillListingMaxDescChars":150'; fi
  printf '%s}\n' "$s"
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
  printf '{"case": "%s", "rep": %s, "arm": "%s", "condition": "%s", "model": "%s", "kit_error": "%s"}\n' "$PID" "$1" "$ARM" \
    "$COND" "$MODEL" "$2" > "$OUT/rep$1/summary.json.tmp"
  mv "$OUT/rep$1/summary.json.tmp" "$OUT/rep$1/summary.json"
  echo "rep$1 kit error: $2"
}

rep() {
  local n="$1" dir repo base start status left name
  require_empty_root "$WST_TROOT"
  mkdir "$OUT/rep$n" || return 2
  dir="$WST_TROOT/rep$n"
  CURRENT="$dir"
  CURRENT_N="$n"
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
  base="$(git -C "$repo" rev-parse HEAD)"
  mkdir -p "$dir/home/.claude" \
    && git -C "$REPO" archive --format=tar "$SHA" skills/ | tar -x -C "$dir/home/.claude" \
    || { kit_failed "$n" 'skills archive failed'; return 2; }
  for name in $COMPETITORS; do
    cp -R "$(competitor_source "$name")" "$dir/home/.claude/skills/$name" \
      || { kit_failed "$n" "competitor copy failed: $name"; return 2; }
  done
  trigger_settings > "$dir/home/.claude/settings.json" || { kit_failed "$n" 'settings failed'; return 2; }
  (cd "$KIT" && uv run --no-project -q python "$KIT/trigger_prompts.py" "$PID") > "$SCRATCH/rep$n.prompt.txt" \
    || { kit_failed "$n" 'prompt failed'; return 2; }
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
  tools summarize --stream "$SCRATCH/rep$n.jsonl" --err "$SCRATCH/rep$n.err" \
    --dest "$OUT/rep$n" --orig "$SCRATCH/rep$n-orig" --case "$PID" --arm "$ARM" --model "$MODEL" --cap "$TRIGGER_CAP" \
    --rep "$n" --rep-dir "$dir" --base "$base" --prompt "$SCRATCH/rep$n.prompt.txt" --status "$status" \
    --wall "$(($(date +%s) - start))" --manifest - --condition "$COND" \
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

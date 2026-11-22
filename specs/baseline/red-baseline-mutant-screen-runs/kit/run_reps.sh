#!/bin/bash
# Run reps of plan 104's micro-test, one at a time. bash 3.2.
# Usage: run_reps.sh <prompt-dir> <fixture> <out-dir> <first> <last>
# <prompt-dir> is build_prompts.py's output. <out-dir> ends in <role>/<arm>/<fixture>, such as
# implementer/control/I1. The fixture's role.txt gives the role, and the role gives the model and the
# cap (common.sh). MANIFEST.txt's role must be the fixture's role.
#
# Before each rep, MSR_ROOT must be empty (exit 3 otherwise), and the skill copy and the prompt must
# match MANIFEST.txt (rep_tools.py check-copy; exit 2 otherwise). Each rep then:
#   1. makes its folder MSR_ROOT/rep<N>/ (common.sh), copies fixtures/<fixture>/repo/ to repo/, runs
#      git init, sets a local user (Developer, developer@example.invalid) and commit.gpgsign false,
#      and commits: that commit is the rep's BASE;
#   2. writes .sdd/.gitignore with `*`, and copies brief.md and spec.md into .sdd/plan/ as
#      task-1-brief.md and task-1-spec.md;
#   3. runs the fixture's setup.sh, if it has one, from repo/ under the rep's own `env -i`
#      environment, with REPO, BASE, WORKSPACE, SKILL (the skill copy root), FIXTURES (the fixtures
#      folder) and VENV_PY set. A setup.sh that exits non-zero is a kit error, and no rep runs;
#   4. fills the prompt: @REPO@ becomes repo/'s path and @BASE@ the BASE sha. A prompt that still
#      holds either token is a kit error;
#   5. runs claude (common.sh), then rep_tools.py summarize, which writes <out-dir>/rep<N>/;
#   6. fails the rep (kit error) when a file it wrote still holds credential_expires_at;
#   7. parks the folder as <scratch>/rep<N>-folder, where <scratch> is
#      MSR_SCRATCH/<role>/<arm>/<fixture>/, beside the raw stream rep<N>.jsonl, its stderr, the filled
#      prompt and the unscrubbed copies (rep<N>-orig/). A trap parks the folder however the rep ends.
# A rep's status is its claude exit status, or 2 for a kit error. A kit error stops the batch. The
# script exits 0 when every rep exits 0, 2 after a kit error or a refusal, 3 for a non-empty root,
# and 1 otherwise.
set -u
[ "$#" -eq 5 ] || { echo "usage: run_reps.sh <prompt-dir> <fixture> <out-dir> <first> <last>"; exit 2; }
KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
. "$KIT/common.sh"
FIXTURES=${MSR_FIXTURES:-$KIT/fixtures}
PROMPTS="$(cd "$1" && pwd)" || exit 2
FIXTURE="$2"
FIX="$FIXTURES/$FIXTURE"
OUT="$(mkdir -p "$3" && cd "$3" && pwd)" || exit 2
FIRST="$4"
LAST="$5"
ARM="$(basename "$(dirname "$OUT")")"
ROLE_DIR="$(basename "$(dirname "$(dirname "$OUT")")")"
SCRATCH="$MSR_SCRATCH/$ROLE_DIR/$ARM/$FIXTURE"
PROMPT="$PROMPTS/$FIXTURE.txt"
MANIFEST="$PROMPTS/MANIFEST.txt"

[ -f "$PROMPT" ] && [ -f "$MANIFEST" ] || { echo "refusing: no $PROMPT or $MANIFEST"; exit 2; }
[ -d "$FIX/repo" ] && [ -f "$FIX/brief.md" ] && [ -f "$FIX/spec.md" ] && [ -f "$FIX/role.txt" ] \
  || { echo "refusing: no fixture $FIX"; exit 2; }
ROLE="$(head -n 1 "$FIX/role.txt")"
MODEL="$(model_for_role "$ROLE")" || { echo "refusing: role $ROLE in $FIX/role.txt"; exit 2; }
CAP="$(cap_for_model "$MODEL")" || exit 2
[ "$ROLE_DIR" = "$ROLE" ] || { echo "refusing: $OUT is not under a $ROLE/<arm>/ folder"; exit 2; }
[ "$(awk '$1 == "role" { print $2 }' "$MANIFEST")" = "$ROLE" ] || { echo "refusing: MANIFEST.txt is not for $ROLE"; exit 2; }
SKILL="$(awk '$1 == "skill-copy-root" { print $2 }' "$MANIFEST")"
[ -n "$SKILL" ] || { echo "refusing: MANIFEST.txt names no skill-copy-root"; exit 2; }
[ -x "$MSR_VENV/bin/python" ] || { echo "refusing: $MSR_VENV/bin/python is missing (see the record's Kit section)"; exit 2; }
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
  printf '{"fixture": "%s", "rep": %s, "role": "%s", "kit_error": "%s"}\n' "$FIXTURE" "$1" "$ROLE" "$2" \
    > "$OUT/rep$1/summary.json.tmp"
  mv "$OUT/rep$1/summary.json.tmp" "$OUT/rep$1/summary.json"
  echo "rep$1 kit error: $2"
}

rep() {
  local n="$1" dir repo base work text start status left
  require_empty_root
  tools check-copy "$MANIFEST" "$PROMPT" || { echo "refusing: the skill copy or the prompt differs from $MANIFEST"; exit 2; }
  mkdir "$OUT/rep$n" || return 2
  dir="$MSR_ROOT/rep$n"
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
  work="$repo/.sdd/plan"
  mkdir -p "$work" && printf '*\n' > "$repo/.sdd/.gitignore" \
    && cp "$FIX/brief.md" "$work/task-1-brief.md" \
    && cp "$FIX/spec.md" "$work/task-1-spec.md" \
    || { kit_failed "$n" 'workspace setup failed'; return 2; }
  if [ -f "$FIX/setup.sh" ]; then
    (
      cd "$repo" || exit 2
      env -i HOME="$dir/home" USER="$USER" LOGNAME="$LOGNAME" PATH="$REP_PATH" SHELL="$SHELL" \
        TMPDIR="$dir/tmp" LANG="${LANG-}" REPO="$repo" BASE="$base" WORKSPACE="$work" SKILL="$SKILL" \
        FIXTURES="$FIXTURES" VENV_PY="$MSR_VENV/bin/python" \
        /bin/bash "$FIX/setup.sh" > "$SCRATCH/rep$n.setup.log" 2>&1
    ) || { kit_failed "$n" "setup.sh failed; see $SCRATCH/rep$n.setup.log"; return 2; }
  fi
  ls -1 "$work" > "$SCRATCH/rep$n.seeded.txt"
  git -C "$repo" rev-parse HEAD > "$SCRATCH/rep$n.start.txt"
  text="$(cat "$PROMPT")"
  text="${text//@REPO@/$repo}"
  text="${text//@BASE@/$base}"
  case "$text" in
    *@REPO@* | *@BASE@*) kit_failed "$n" 'the prompt still holds @REPO@ or @BASE@'; return 2 ;;
  esac
  printf '%s\n' "$text" > "$SCRATCH/rep$n.prompt.txt"
  start="$(date +%s)"
  run_claude "$dir" "$MODEL" "$CAP" "$SCRATCH/rep$n.prompt.txt" "$SCRATCH/rep$n.jsonl" "$SCRATCH/rep$n.err"
  status=$?
  tools summarize --stream "$SCRATCH/rep$n.jsonl" --err "$SCRATCH/rep$n.err" \
    --dest "$OUT/rep$n" --orig "$SCRATCH/rep$n-orig" --fixture "$FIXTURE" --role "$ROLE" --arm "$ARM" \
    --rep "$n" --rep-dir "$dir" --base "$base" --prompt "$SCRATCH/rep$n.prompt.txt" --status "$status" \
    --wall "$(($(date +%s) - start))" --manifest "$MANIFEST" --venv "$MSR_VENV" --model "$MODEL" --cap "$CAP" \
    --start "$SCRATCH/rep$n.start.txt" --seeded "$SCRATCH/rep$n.seeded.txt" \
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

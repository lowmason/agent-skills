#!/bin/bash
# Run one registered rep of plan 100 in its own HOME, /private/tmp/phr100/<rep>/.
# It builds that HOME (C1, C2, C8), checks the kit hash (C11), runs every turn
# with the Global Constraints command, splits and strips each turn's stream
# (C7), copies the session's project folder and the handoffs tree, checks for
# the strip, and parks the HOME in $PHR_CTL/homes/<rep>/. The controller
# launches it through `env -i` (C13). bash 3.2.
#
# Usage: run_rep.sh REP
# Exit: 0 done (a failed turn is noted in meta.txt), 2 refused, 3 PHR_ROOT not
# empty, 4 kit error.
set -euo pipefail

rep=${1:?usage: run_rep.sh REP}
KIT_DIR=$(cd "$(dirname "$0")" && pwd -P)
REAL=$(cd "$HOME" && pwd -P)
CTL=${PHR_CTL:-$HOME/.cache/agent-skills/handoffs/rerun100}
TEMPLATES=${PHR_TEMPLATES:-$HOME/.cache/pondworks/templates}
HEADS=${PHR_TEMPLATE_HEADS:-$KIT_DIR/templates.tsv}
ROOT_IN=${PHR_ROOT:-/private/tmp/phr100}
CLAUDE_BIN=${CLAUDE_BIN:-$(command -v claude || true)}
USER=${USER:-$(id -un)}
LOGNAME=${LOGNAME:-$USER}
PY=/usr/bin/python3
MODEL=claude-opus-5-5
EFFORT=xhigh
ALLOWED_CLAUDE='CLAUDE_CODE_DISABLE_ADVISOR_TOOL CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS'
KIT_PATHS='skills/brainstorming skills/writing-plans skills/executing-plans
  skills/subagent-driven-development skills/finishing-a-development-branch
  skills/requesting-code-review skills/receiving-code-review skills/using-git-worktrees
  skills/verification-before-completion skills/test-driven-development
  skills/derive-roadmap skills/prepare-handoff
  agents/code-reviewer.md agents/task-reviewer.md commands/deferred.md'
SHIM_LINKS='git python3 python3.13 uv'
FIELD=credential_expires_at
G=(git -c commit.gpgsign=false -c core.hooksPath=/dev/null)

die() { echo "run_rep.sh: $2" >&2; exit "$1"; }

# Hash of a kit base folder: the sorted file list and each file's contents.
kit_hash() {
  ( cd "$1" && find skills agents commands ! -type d -print | LC_ALL=C sort |
      while IFS= read -r f; do printf '%s\n' "$f"; shasum -a 256 < "$f"; done ) |
    shasum -a 256 | cut -c1-64
}

H=''
scratch=''
cleanup() {
  if [ -n "$scratch" ]; then rm -rf "$scratch"; fi
  if [ -n "$H" ] && [ -d "$H" ]; then
    mkdir -p "$CTL/homes"
    mv "$H" "$CTL/homes/$rep"
  fi
}
trap cleanup EXIT

[ -n "$CLAUDE_BIN" ] && [ -x "$CLAUDE_BIN" ] || die 2 "no claude binary (set CLAUDE_BIN)"
case "$KIT_DIR$REAL" in *[[:space:]\"\'\\]*) die 2 "the kit or real home path holds a space or quote" ;; esac
[ -f "$CTL/registry.tsv" ] || die 2 "no $CTL/registry.tsv (make_reps.py writes it)"
row=$(awk -F'\t' -v r="$rep" 'NR > 1 && $1 == r' "$CTL/registry.tsv")
[ -n "$row" ] || die 2 "$rep is not in registry.tsv"
IFS=$'\t' read -r _ arm phase template kit_commit prompts <<<"$row"
[ -n "${prompts:-}" ] || die 2 "$rep has a short registry row"
out=$CTL/results/$rep
[ ! -e "$out" ] || die 2 "$out exists; a rep never runs twice"
[ ! -e "$CTL/homes/$rep" ] || die 2 "$CTL/homes/$rep exists; a rep never runs twice"

# C6: no rep may see another rep's files.
mkdir -p "$ROOT_IN"
ROOT=$(cd "$ROOT_IN" && pwd -P)
[ -z "$(ls -A "$ROOT")" ] || die 3 "$ROOT is not empty; park or remove what is there first"

IFS=',' read -r -a turns <<<"$prompts"
for p in "${turns[@]}"; do
  [ -f "$KIT_DIR/prompts/$p" ] || die 2 "no prompt $KIT_DIR/prompts/$p"
done

# The fixture template: the expected HEAD, only refs/heads/main, a clean status.
tpl=$TEMPLATES/$template
want=$(awk -F'\t' -v t="$template" 'NR > 1 && $1 == t { print $2 }' "$HEADS")
[ -n "$want" ] || die 2 "no expected HEAD for $template in $HEADS"
[ "$(git -C "$tpl" rev-parse HEAD)" = "$want" ] || die 2 "$tpl HEAD is not $want"
[ "$(git -C "$tpl" for-each-ref --format='%(refname)')" = refs/heads/main ] || die 2 "$tpl has refs other than refs/heads/main"
[ -z "$(git --no-optional-locks -C "$tpl" status --porcelain=v1 --untracked-files=all)" ] || die 2 "$tpl is not clean"

# The reference kit: KIT_COMMIT's copy, extracted outside PHR_ROOT.
SOURCE=${PHR_KIT_REPO:-$(git -C "$KIT_DIR" rev-parse --show-toplevel)}
scratch=$(mktemp -d "${TMPDIR:-/tmp}/phr100-kit.XXXXXX")
# shellcheck disable=SC2086
git -C "$SOURCE" archive "$kit_commit" $KIT_PATHS | tar -x -C "$scratch"
kit_ref=$(kit_hash "$scratch")

# Plan 100 Deviation (execution brief default 2): the env -i list below also sets
# CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=2400000 (40 minutes), so print mode does not stop
# background subagents 10 minutes after a turn ends. No other CLAUDE* name may reach the rep.
H=$ROOT/$rep
rep_env=(HOME="$H" USER="$USER" LOGNAME="$LOGNAME" SHELL=/bin/zsh LANG="${LANG-}"
  TMPDIR="$H/tmp" PATH="$H/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
  CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=2400000)
for kv in "${rep_env[@]}"; do
  name=${kv%%=*}
  case $name in
    CLAUDE*) case " $ALLOWED_CLAUDE " in *" $name "*) ;; *) die 2 "$name may not reach the rep" ;; esac ;;
  esac
done

# C1, C2, C8: the rep HOME.
repdir=$H/work/$rep
mkdir -p "$H/.claude" "$H/work" "$H/git" "$H/.local/bin" "$H/tmp" "$H/Library"
ln -s "$REAL/Library/Keychains" "$H/Library/Keychains"
# shellcheck disable=SC2086
git -C "$SOURCE" archive "$kit_commit" $KIT_PATHS | tar -x -C "$H/.claude"
cp -R "$tpl" "$repdir"
"${G[@]}" init -q --bare -b main "$H/git/$rep.git"
"${G[@]}" -C "$repdir" remote add origin "$H/git/$rep.git"
"${G[@]}" -C "$repdir" push -q origin main
"${G[@]}" -C "$repdir" fetch -q origin
"${G[@]}" -C "$repdir" remote set-head origin main
cp "$KIT_DIR/shim/gh" "$H/.local/bin/gh"
chmod 755 "$H/.local/bin/gh"
for t in $SHIM_LINKS; do ln -s "/opt/homebrew/bin/$t" "$H/.local/bin/$t"; done

# C11: the rep's kit must equal KIT_COMMIT's copy before turn 1.
kit_before=$(kit_hash "$H/.claude")
[ "$kit_before" = "$kit_ref" ] || die 4 "kit_error: the rep kit hash $kit_before is not KIT_COMMIT's $kit_ref"

SETTINGS_JSON='{"permissions": {"deny": ["Read(//Users/**)", "Edit(//Users/**)", "Write(//Users/**)", '
SETTINGS_JSON+='"Read(~/Library/**)", "Edit(~/Library/**)", "Write(~/Library/**)"]}, '
SETTINGS_JSON+='"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", '
SETTINGS_JSON+='"command": "/usr/bin/python3 '"$KIT_DIR"'/guard.py --real-home '"$REAL"'"}]}]}}'

mkdir -p "$out"
sid=$(uuidgen | tr 'A-Z' 'a-z')
printf '%s\n' "$sid" > "$out/session-id"
{
  printf 'rep=%s\narm=%s\nphase=%s\ntemplate=%s\nkit_commit=%s\n' "$rep" "$arm" "$phase" "$template" "$kit_commit"
  printf 'model=%s\neffort=%s\nclaude=%s\nkit_sha_before=%s\n' "$MODEL" "$EFFORT" "$("$CLAUDE_BIN" --version)" "$kit_before"
} > "$out/meta.txt"

n=0
for p in "${turns[@]}"; do
  n=$((n + 1))
  if [ "$n" -eq 1 ]; then sess=--session-id; else sess=--resume; fi
  sed -e "s|@REP@|$repdir|g" -e "s|@REAL@|$REAL|g" "$KIT_DIR/prompts/$p" > "$out/turn$n.prompt.txt"
  set +e
  ( cd "$repdir" && env -i "${rep_env[@]}" \
      "$CLAUDE_BIN" -p "$sess" "$sid" \
      --setting-sources user,project,local --strict-mcp-config \
      --model "$MODEL" --effort "$EFFORT" --permission-mode auto \
      --settings "$SETTINGS_JSON" --max-budget-usd 30 \
      --output-format stream-json --verbose \
      < "$out/turn$n.prompt.txt" 2> "$out/turn$n.stderr" ) |
    "$PY" "$KIT_DIR/postprocess.py" split - "$out" "$n"
  codes=("${PIPESTATUS[@]}")
  set -e
  status=${codes[0]}
  [ "${codes[1]}" -eq 0 ] || die 4 "kit_error: postprocess.py split failed on turn $n"
  {
    echo "## branch"; git -C "$repdir" branch --show-current
    echo "## status"; git -C "$repdir" status --porcelain=v1 --untracked-files=all
    echo "## log"; git -C "$repdir" log --all --format='%h %cs%d %s' -15
  } > "$out/turn$n.git.txt" 2>&1
  if [ "$status" -ne 0 ]; then
    echo "turn $n exited $status; later turns not run" >> "$out/meta.txt"
    break
  fi
done

if [ -d "$H/.claude/projects" ]; then
  transcript=$(find "$H/.claude/projects" -maxdepth 2 -name "$sid.jsonl" | head -n 1)
  if [ -n "$transcript" ]; then cp -R "$(dirname "$transcript")" "$out/project"; fi
fi
if [ -d "$H/.cache/agent-skills/handoffs" ]; then
  cp -R "$H/.cache/agent-skills/handoffs" "$out/handoffs"
fi
"$PY" "$KIT_DIR/postprocess.py" strip-tree "$out"
echo "kit_sha_after=$(kit_hash "$H/.claude")" >> "$out/meta.txt"

left=$(grep -rl "$FIELD" "$out" || true)
if [ -n "$left" ]; then
  echo "kit_error=the strip check found the field in: $(echo "$left" | tr '\n' ' ')" >> "$out/meta.txt"
  die 4 "kit_error: the strip left the field in $left"
fi
echo "rep $rep ($arm, $phase): $n turn(s); results in $out; HOME parked in $CTL/homes/$rep"

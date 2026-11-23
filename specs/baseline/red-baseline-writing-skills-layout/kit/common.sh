# Shared by run_tool_reps.sh and probe_tools.sh (source it), so a rep and a probe run claude with the same
# folder layout, environment and flags. bash 3.2. Copy of plan 104's common.sh
# (specs/baseline/red-baseline-mutant-screen-runs/kit/common.sh), cut for plan 105's tools reps: no venv,
# no role-to-model map, the tools Read, Glob, Grep, Edit and Write, and one cap for both models.
#
# Each rep or probe gets its own folder <WSL_ROOT>/<name>/ with repo/ (its working directory), home/
# (its HOME, with Library/Keychains linked to the real one so the login works, as in plan 100's
# run_rep.sh) and tmp/ (its TMPDIR). `env -i` keeps only HOME, USER, LOGNAME, PATH, SHELL, TMPDIR
# and LANG, plus the two disable flags. PATH is the fixed system PATH below, so nothing under the real
# home is on it; claude is called by the absolute path resolved here, before `env -i`.
# `--setting-sources ""` keeps user-level context out, CLAUDE_CODE_DISABLE_AUTO_MEMORY drops the
# auto-memory section, --disable-slash-commands keeps installed skills and commands out, and the
# --settings value denies Read, Edit and Write under /Users and under the rep's ~/Library, and the
# cross-session tools by name. syncClaudeAiSkills false keeps account skills out of the rep's HOME.
# The settings hold no Grep or Glob rule: audit.py checks the path arguments of both tools instead.
#
# Every path can be moved for the tests: WSL_ROOT, WSL_SCRATCH, WSL_FIXTURES and CLAUDE_BIN. The
# defaults are the pinned paths. The skill copy's root comes from MANIFEST.txt (build_prompts.py).

WSL_ROOT=${WSL_ROOT:-/private/tmp/wsl105}
WSL_SCRATCH=${WSL_SCRATCH:-$HOME/.cache/agent-skills/scratch/plan105/tools}
CLAUDE_BIN=${CLAUDE_BIN:-$(command -v claude || true)}
REP_PATH=/usr/bin:/bin:/usr/sbin:/sbin
REP_TOOLS=Read,Glob,Grep,Edit,Write
CAP=1.50
FIELD=credential_expires_at
SETTINGS='{"permissions":{"deny":["Read(//Users/**)","Edit(//Users/**)","Write(//Users/**)",'
SETTINGS+='"Read(~/Library/**)","Edit(~/Library/**)","Write(~/Library/**)",'
SETTINGS+='"ListAgents","SendMessage","PushNotification","RemoteTrigger"]},"syncClaudeAiSkills":false}'

# The two models of plan 105's micro-tests (Global Constraints, Micro-tests). Both take the $1.50 cap.
check_model() {
  case "$1" in
    claude-sonnet-5-5 | claude-opus-5-5) return 0 ;;
    *) return 1 ;;
  esac
}

# The real home, resolved, for the Keychains link.
real_home() {
  (cd "$HOME" && pwd -P)
}

# Make WSL_ROOT if it is missing; exit 3 when it holds anything, so no rep sees another rep's files.
require_empty_root() {
  mkdir -p "$WSL_ROOT" || exit 2
  if [ -n "$(ls -A "$WSL_ROOT")" ]; then
    echo "refusing: $WSL_ROOT is not empty; park or remove what is there first"
    exit 3
  fi
}

# make_folder DIR: the rep or probe folder, with repo/, home/ (Keychains link) and tmp/.
make_folder() {
  mkdir -p "$1/repo" "$1/home/Library" "$1/tmp" \
    && ln -s "$(real_home)/Library/Keychains" "$1/home/Library/Keychains"
}

# run_claude DIR MODEL PROMPT STREAM ERR: one claude -p run from DIR/repo. Returns claude's status.
run_claude() {
  local dir="$1" model="$2" prompt="$3" stream="$4" err="$5"
  (
    cd "$dir/repo" || exit 2
    env -i HOME="$dir/home" USER="$USER" LOGNAME="$LOGNAME" PATH="$REP_PATH" SHELL="$SHELL" \
      TMPDIR="$dir/tmp" LANG="${LANG-}" \
      CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
      "$CLAUDE_BIN" -p --model "$model" --tools "$REP_TOOLS" --allowedTools "$REP_TOOLS" \
      --strict-mcp-config --setting-sources "" --disable-slash-commands --no-session-persistence \
      --settings "$SETTINGS" --max-budget-usd "$CAP" --output-format stream-json --verbose \
      < "$prompt" > "$stream" 2> "$err"
  )
}

# park DIR DEST: move a finished folder out of WSL_ROOT, under the scratch folder.
park() {
  mkdir -p "$(dirname "$2")" && mv "$1" "$2"
}

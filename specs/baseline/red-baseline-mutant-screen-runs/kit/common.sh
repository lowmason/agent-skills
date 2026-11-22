# Shared by run_reps.sh and probe.sh (source it), so a rep and a probe run claude with the same
# folder layout, environment and flags. bash 3.2.
#
# Each rep or probe gets its own folder <MSR_ROOT>/<name>/ with repo/ (its working directory), home/
# (its HOME, with Library/Keychains linked to the real one so the login works, as in plan 100's
# run_rep.sh) and tmp/ (its TMPDIR). `env -i` keeps only HOME, USER, LOGNAME, PATH, SHELL, TMPDIR
# and LANG, plus the two disable flags. PATH is the fixed system PATH below, so nothing under the real
# home is on it; claude is called by the absolute path resolved here, before `env -i`.
# `--setting-sources ""` keeps user-level context out, CLAUDE_CODE_DISABLE_AUTO_MEMORY drops the
# auto-memory section, --disable-slash-commands keeps installed skills and commands out, and the
# --settings value denies Read, Edit and Write under /Users and under the rep's ~/Library, and the
# cross-session tools by name. syncClaudeAiSkills false keeps account skills out of the rep's HOME.
#
# Every path can be moved for the tests: MSR_ROOT, MSR_SKILL_ROOT, MSR_VENV, MSR_SCRATCH,
# MSR_FIXTURES and CLAUDE_BIN. The defaults are the pinned paths.

MSR_ROOT=${MSR_ROOT:-/private/tmp/msr104}
MSR_SKILL_ROOT=${MSR_SKILL_ROOT:-/private/tmp/msr104-skill}
MSR_VENV=${MSR_VENV:-/private/tmp/msr104-venv}
MSR_SCRATCH=${MSR_SCRATCH:-$HOME/.cache/agent-skills/scratch/plan104}
CLAUDE_BIN=${CLAUDE_BIN:-$(command -v claude || true)}
REP_PATH=/usr/bin:/bin:/usr/sbin:/sbin
FIELD=credential_expires_at
SETTINGS='{"permissions":{"deny":["Read(//Users/**)","Edit(//Users/**)","Write(//Users/**)",'
SETTINGS+='"Read(~/Library/**)","Edit(~/Library/**)","Write(~/Library/**)",'
SETTINGS+='"ListAgents","SendMessage","PushNotification","RemoteTrigger"]},"syncClaudeAiSkills":false}'

# The model and the cap of a role, and the cap of a model (Global Constraints, Micro-test).
model_for_role() {
  case "$1" in
    implementer | controller) echo sonnet ;;
    inline) echo opus ;;
    *) return 1 ;;
  esac
}
cap_for_model() {
  case "$1" in
    sonnet) echo 1.50 ;;
    opus) echo 4 ;;
    *) return 1 ;;
  esac
}

# The real home, resolved, for the Keychains link.
real_home() {
  (cd "$HOME" && pwd -P)
}

# Make MSR_ROOT if it is missing; exit 3 when it holds anything, so no rep sees another rep's files.
require_empty_root() {
  mkdir -p "$MSR_ROOT" || exit 2
  if [ -n "$(ls -A "$MSR_ROOT")" ]; then
    echo "refusing: $MSR_ROOT is not empty; park or remove what is there first"
    exit 3
  fi
}

# make_folder DIR: the rep or probe folder, with repo/, home/ (Keychains link) and tmp/.
make_folder() {
  mkdir -p "$1/repo" "$1/home/Library" "$1/tmp" \
    && ln -s "$(real_home)/Library/Keychains" "$1/home/Library/Keychains"
}

# run_claude DIR MODEL CAP PROMPT STREAM ERR: one claude -p run from DIR/repo. Returns claude's status.
run_claude() {
  local dir="$1" model="$2" cap="$3" prompt="$4" stream="$5" err="$6"
  (
    cd "$dir/repo" || exit 2
    env -i HOME="$dir/home" USER="$USER" LOGNAME="$LOGNAME" PATH="$REP_PATH" SHELL="$SHELL" \
      TMPDIR="$dir/tmp" LANG="${LANG-}" \
      CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
      "$CLAUDE_BIN" -p --model "$model" --tools Bash,Read,Edit,Write --allowedTools Bash,Read,Edit,Write \
      --strict-mcp-config --setting-sources "" --disable-slash-commands --no-session-persistence \
      --settings "$SETTINGS" --max-budget-usd "$cap" --output-format stream-json --verbose \
      < "$prompt" > "$stream" 2> "$err"
  )
}

# park DIR DEST: move a finished folder out of MSR_ROOT, under the scratch folder.
park() {
  mkdir -p "$(dirname "$2")" && mv "$1" "$2"
}

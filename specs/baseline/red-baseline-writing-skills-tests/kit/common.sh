# Shared by run_tool_reps.sh, run_trigger_reps.sh and probe_tools.sh (source it), so a rep and a probe run
# claude with the same folder layout, environment and deny list. bash 3.2. Copy of plan 105's common.sh
# (specs/baseline/red-baseline-writing-skills-layout/kit/common.sh), changed for plan 107: the roots and the
# scratch folders are plan 107's, an R3 rep gets Bash limited to `git mv` (tools_for_case), and the trigger
# runner shares the deny list, make_folder, park and check_model.
#
# Each rep or probe gets its own folder <WST_ROOT>/<name>/ with repo/ (its working directory), home/
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
# Every path can be moved for the tests: WST_ROOT, WST_SCRATCH, WST_TROOT, WST_TRIGGER_SCRATCH, WST_FIXTURES
# and CLAUDE_BIN. The defaults are the pinned paths. The skill copy's root comes from MANIFEST.txt
# (build_prompts.py).

WST_ROOT=${WST_ROOT:-/private/tmp/wst107}
WST_SCRATCH=${WST_SCRATCH:-$HOME/.cache/agent-skills/scratch/plan107/cases}
WST_TROOT=${WST_TROOT:-/private/tmp/wst107t}
WST_TRIGGER_SCRATCH=${WST_TRIGGER_SCRATCH:-$HOME/.cache/agent-skills/scratch/plan107/triggers}
CLAUDE_BIN=${CLAUDE_BIN:-$(command -v claude || true)}
REP_PATH=/usr/bin:/bin:/usr/sbin:/sbin
REP_TOOLS=Read,Glob,Grep,Edit,Write
R3_TOOLS=Read,Glob,Grep,Edit,Write,Bash
R3_ALLOWED='Read,Glob,Grep,Edit,Write,Bash(git mv *)'
TRIGGER_TOOLS=Read,Glob,Grep,Skill
CAP=1.50
TRIGGER_CAP=0.25
FIELD=credential_expires_at
DENY='"Read(//Users/**)","Edit(//Users/**)","Write(//Users/**)","Read(~/Library/**)","Edit(~/Library/**)",'
DENY+='"Write(~/Library/**)","ListAgents","SendMessage","PushNotification","RemoteTrigger"'
SETTINGS='{"permissions":{"deny":['"$DENY"']},"syncClaudeAiSkills":false}'

# The two models of plan 107's micro-tests (Global Constraints, Micro-tests). Both take the case cap, $1.50.
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

# Make a root if it is missing; exit 3 when it holds anything, so no rep sees another rep's files.
# require_empty_root [ROOT]: ROOT defaults to WST_ROOT.
require_empty_root() {
  local root="${1:-$WST_ROOT}"
  mkdir -p "$root" || exit 2
  if [ -n "$(ls -A "$root")" ]; then
    echo "refusing: $root is not empty; park or remove what is there first"
    exit 3
  fi
}

# make_folder DIR: the rep or probe folder, with repo/, home/ (Keychains link) and tmp/.
make_folder() {
  mkdir -p "$1/repo" "$1/home/Library" "$1/tmp" \
    && ln -s "$(real_home)/Library/Keychains" "$1/home/Library/Keychains"
}

# tools_for_case CASE: sets CASE_TOOLS and CASE_ALLOWED. An R3 rep (the rename case) also gets Bash, and
# --allowedTools limits it to `git mv *`. audit.py voids any other Bash call, and any git mv outside repo/.
tools_for_case() {
  case "$1" in
    R3) CASE_TOOLS="$R3_TOOLS"; CASE_ALLOWED="$R3_ALLOWED" ;;
    *) CASE_TOOLS="$REP_TOOLS"; CASE_ALLOWED="$REP_TOOLS" ;;
  esac
}

# run_claude DIR MODEL PROMPT STREAM ERR [CASE]: one claude -p run from DIR/repo. Returns claude's status.
run_claude() {
  local dir="$1" model="$2" prompt="$3" stream="$4" err="$5"
  tools_for_case "${6:-}"
  (
    cd "$dir/repo" || exit 2
    env -i HOME="$dir/home" USER="$USER" LOGNAME="$LOGNAME" PATH="$REP_PATH" SHELL="$SHELL" \
      TMPDIR="$dir/tmp" LANG="${LANG-}" \
      CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
      "$CLAUDE_BIN" -p --model "$model" --tools "$CASE_TOOLS" --allowedTools "$CASE_ALLOWED" \
      --strict-mcp-config --setting-sources "" --disable-slash-commands --no-session-persistence \
      --settings "$SETTINGS" --max-budget-usd "$CAP" --output-format stream-json --verbose \
      < "$prompt" > "$stream" 2> "$err"
  )
}

# park DIR DEST: move a finished folder out of the root, under the scratch folder.
park() {
  mkdir -p "$(dirname "$2")" && mv "$1" "$2"
}

# Shared by run_trigger_reps.sh (source it). bash 3.2. Copy of plan 107's common.sh
# (specs/baseline/red-baseline-writing-skills-tests/kit/common.sh), changed for plan 111: the case-rep parts
# (the case root and scratch, the case tools and cap, tools_for_case, run_claude and park) are cut, the root
# and the scratch folder are plan 111's, the deny list gains Bash and Read(~/**), the trigger settings set
# blockReadsOutsideWorkingDirectories, and a finished rep folder is removed, not parked.
#
# Each rep gets its own folder <CD_TROOT>/rep<N>/ with repo/ (its working directory), home/ (its HOME, with
# Library/Keychains linked to the real one so the login works, as in plan 100's run_rep.sh) and tmp/ (its
# TMPDIR, the rep's own scratch folder). `env -i` keeps only HOME, USER, LOGNAME, PATH, SHELL, TMPDIR and
# LANG, plus the two disable flags. PATH is the fixed system PATH below, so nothing under the real home is on
# it; claude is called by the absolute path resolved here, before `env -i`.
#
# TRIGGER_SETTINGS is the rep's home/.claude/settings.json, which claude reads through --setting-sources user.
# Its deny list refuses Bash, every Read under the rep's HOME (~/**, which holds the skills and the Keychains
# link), Read, Edit and Write under /Users, Edit and Write under the rep's ~/Library, and the cross-session
# tools by name. blockReadsOutsideWorkingDirectories makes Read, Grep and Glob refuse a path outside the rep's
# repo/. syncClaudeAiSkills false keeps account skills out of the rep's HOME, and skillListingBudgetFraction
# 0.05 keeps every description in the listing whole (plan 107's condition `full`).
#
# Every path can be moved for the tests: CD_TROOT, CD_TRIGGER_SCRATCH, CD_FIXTURES, CD_REPO and CLAUDE_BIN.
# The defaults are the pinned paths.

CD_TROOT=${CD_TROOT:-/private/tmp/cd111t}
CD_TRIGGER_SCRATCH=${CD_TRIGGER_SCRATCH:-$HOME/.cache/agent-skills/scratch/plan111/triggers}
CLAUDE_BIN=${CLAUDE_BIN:-$(command -v claude || true)}
REP_PATH=/usr/bin:/bin:/usr/sbin:/sbin
TRIGGER_TOOLS=Read,Glob,Grep,Skill
TRIGGER_CAP=0.25
FIELD=credential_expires_at
DENY='"Bash","Read(~/**)","Read(//Users/**)","Edit(//Users/**)","Write(//Users/**)","Read(~/Library/**)",'
DENY+='"Edit(~/Library/**)","Write(~/Library/**)","ListAgents","SendMessage","PushNotification","RemoteTrigger"'
TRIGGER_SETTINGS='{"permissions":{"deny":['"$DENY"'],"blockReadsOutsideWorkingDirectories":true},'
TRIGGER_SETTINGS+='"syncClaudeAiSkills":false,"skillListingBudgetFraction":0.05}'

# The two models of plan 111's trigger test (Task 3 Step 1, rule 6). Both take the trigger cap, $0.25.
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
# require_empty_root [ROOT]: ROOT defaults to CD_TROOT.
require_empty_root() {
  local root="${1:-$CD_TROOT}"
  mkdir -p "$root" || exit 2
  if [ -n "$(ls -A "$root")" ]; then
    echo "refusing: $root is not empty; remove what is there first"
    exit 3
  fi
}

# make_folder DIR: the rep folder, with repo/, home/ (Keychains link) and tmp/.
make_folder() {
  mkdir -p "$1/repo" "$1/home/Library" "$1/tmp" \
    && ln -s "$(real_home)/Library/Keychains" "$1/home/Library/Keychains"
}

# remove_folder DIR: delete a finished rep folder, so none of claude's own state files in its HOME is kept.
# rm -r removes the Keychains link itself and never follows it.
remove_folder() {
  rm -rf -- "$1"
}

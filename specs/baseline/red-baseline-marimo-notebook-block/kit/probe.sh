#!/bin/bash
# Check the micro-test's isolation before any rep. This builds a rep directory of one arm the way
# run_reps.sh does, with the base notebook of the explore case, and runs one probe prompt in it
# through `claude -p` with the environment and the flags of run_reps.sh. Keep the two `claude -p`
# command lines identical. The stream shows what the session loaded, such as its tools, its skills
# and its CLAUDE.md.
# Usage: probe.sh <arm> <out-file> [<prompt-file>]
# <arm> is control or block. <prompt-file> defaults to isolation_probe.txt. env_check.txt is the
# second probe: it checks that a rep authenticates under `env -i`, that marimo and Polars run on
# the fixture, and that the --settings deny rules load.
# The rep directory is a git repository by design, so this script does not refuse one. Its parent,
# /tmp/mnb98/rep-XXXXXX, must not be inside any other repository. Like run_reps.sh, the probe
# refuses to start, with exit 3, while /tmp/mnb98/ holds anything but venv/ and leakcheck.sh. After
# the run, it moves its rep directory to ~/.cache/agent-skills/scratch/plan98/repdirs/ and any
# stray entry to stray/. It refuses, with exit 2, an <out-file> that is /tmp/mnb98/ or lies inside
# it. The last line printed gives the moved rep directory and the sha256 of its
# CLAUDE.md and of the block (null in the control arm). The
# stream holds home paths and a session id. Keep <out-file> outside the repository and never
# commit it.
set -u
[ "$#" -eq 2 ] || [ "$#" -eq 3 ] || { echo "usage: probe.sh <arm> <out-file> [<prompt-file>]"; exit 2; }
PARK="$HOME/.cache/agent-skills/scratch/plan98"

# Keep these six functions identical in run_reps.sh and probe.sh.
# Print the absolute, physical form of a path that need not exist yet, so that `..`, `.`, a
# trailing slash and a linked parent such as /tmp all resolve. Call it in $(...), so that its
# set -f stays in a subshell.
resolve_path() {
  local path="$1" rest='' part
  set -f
  case "$path" in
    /*) ;;
    *) path="$PWD/$path" ;;
  esac
  while [ ! -d "$path" ]; do
    rest="${path##*/}${rest:+/$rest}"
    path="${path%/*}"
    [ -n "$path" ] || path=/
  done
  path="$(cd "$path" && pwd -P)" || return 1
  local IFS=/
  for part in $rest; do
    case "$part" in
      '' | .) ;;
      ..) path="${path%/*}"; [ -n "$path" ] || path=/ ;;
      *) path="${path%/}/$part" ;;
    esac
  done
  printf '%s\n' "$path"
}

# Refuse, with exit 2, an output path that is /tmp/mnb98/ or lies inside it, because reps can read
# that folder. Outputs go outside it.
refuse_inside() {
  local resolved root
  resolved="$(resolve_path "$1")" || { echo "refusing (exit 2): cannot resolve $1"; exit 2; }
  root="$(cd /tmp/mnb98 2> /dev/null && pwd -P)" || root=/private/tmp/mnb98
  case "$resolved" in
    /tmp/mnb98 | /tmp/mnb98/* | /private/tmp/mnb98 | /private/tmp/mnb98/* | "$root" | "$root"/*)
      echo "refusing (exit 2): $1 is inside /tmp/mnb98/. Use a path outside it, for example under ~/.cache/agent-skills/scratch/plan98/."
      exit 2
      ;;
  esac
}

# Print each top-level entry of /tmp/mnb98/ other than venv/ and leakcheck.sh, one name a line.
extra_entries() {
  local entry
  for entry in /tmp/mnb98/* /tmp/mnb98/.[!.]* /tmp/mnb98/..?*; do
    { [ -e "$entry" ] || [ -L "$entry" ]; } || continue
    case "${entry##*/}" in
      venv | leakcheck.sh) ;;
      *) printf '%s\n' "${entry##*/}" ;;
    esac
  done
}

# Stop, with exit 3, while /tmp/mnb98/ holds anything but venv/ and leakcheck.sh. $1 says why, and
# "refusing" is the default.
refuse_extras() {
  local found
  found="$(extra_entries)"
  [ -z "$found" ] && return 0
  echo "${1:-refusing} (exit 3): /tmp/mnb98/ holds more than venv/ and leakcheck.sh. Move each entry out first:"
  printf '%s\n' "$found" | sed 's|^|  /tmp/mnb98/|'
  exit 3
}

# Move each stray entry that a rep wrote into /tmp/mnb98/ to stray/. A rep directory stays, because
# its own rep moves it when the rep ends, and a rep directory that is still there may be running.
sweep_strays() {
  local name dest
  mkdir -p "$PARK/stray" || return 1
  extra_entries | while IFS= read -r name; do
    case "$name" in
      rep-??????) continue ;;
    esac
    dest="$PARK/stray/$(date +%Y%m%d-%H%M%S)-$$-$name"
    mv "/tmp/mnb98/$name" "$dest" && echo "moved stray /tmp/mnb98/$name to ~/${dest#"$HOME"/}"
  done
}

# Move a finished rep directory out of /tmp/mnb98/ into repdirs/, so that no later rep can read it.
park_rep_dir() {
  local dir="$1"
  [ -n "$dir" ] && [ -d "$dir" ] || return 0
  mkdir -p "$PARK/repdirs" || return 1
  [ -e "$PARK/repdirs/${dir##*/}" ] && { echo "cannot move $dir: repdirs/ already holds ${dir##*/}"; return 1; }
  mv "$dir" "$PARK/repdirs/"
}

KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
ARM="$1"
case "$ARM" in
  control | block) ;;
  *) echo "refusing: arm must be control or block, not $ARM"; exit 2 ;;
esac
PROMPT="${3:-$KIT/isolation_probe.txt}"
[ -f "$PROMPT" ] || { echo "refusing: no prompt file $PROMPT"; exit 2; }
PROMPT="$(cd "$(dirname "$PROMPT")" && pwd)/$(basename "$PROMPT")"
refuse_inside "$2"
OUTDIR="$(mkdir -p "$(dirname "$2")" && cd "$(dirname "$2")" && pwd)" || exit 2
OUT="$OUTDIR/$(basename "$2")"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 2; }
ROOT="$(git -C "$KIT" rev-parse --show-toplevel)" || exit 2
BLOCK="$ROOT/templates/marimo-repo/notebook-block.md"
ANCHOR='marimo-pair drives live notebook sessions in this repo.'
DENY='{"permissions":{"deny":["Read(~/**)","Edit(~/**)","Write(~/**)"]}}'
[ "$ARM" = control ] || [ -f "$BLOCK" ] || { echo "refusing: no block at $BLOCK"; exit 2; }
refuse_extras
run="$(mktemp -d /tmp/mnb98/rep-XXXXXX)" || exit 2
(cd "$run" && git rev-parse --show-toplevel > /dev/null 2>&1) \
  && { echo "refusing: $run is inside a git repository"; exit 2; }
repo="$run/repo"
cp -R "$KIT/fixture/repo" "$repo" || exit 2
block_sha=null
if [ "$ARM" = block ]; then
  [ "$(grep -c -x -F "$ANCHOR" "$KIT/fixture/repo/CLAUDE.md")" = 1 ] \
    || { echo "refusing: the anchor sentence does not match exactly once"; exit 2; }
  [ "$(grep -c -F 'marimo-repo:start' "$BLOCK")" = 1 ] && [ "$(grep -c -F 'marimo-repo:end' "$BLOCK")" = 1 ] \
    || { echo "refusing: the block lacks its markers"; exit 2; }
  awk -v block="$BLOCK" -v anchor="$ANCHOR" \
    '{ print } $0 == anchor { print ""; while ((getline line < block) > 0) print line }' \
    "$KIT/fixture/repo/CLAUDE.md" > "$repo/CLAUDE.md" || exit 2
  block_sha="$(shasum -a 256 "$BLOCK" | cut -d ' ' -f 1)"
fi
claude_md_sha="$(shasum -a 256 "$repo/CLAUDE.md" | cut -d ' ' -f 1)"
git -C "$repo" init -q \
  && printf '__pycache__/\n__marimo__/\n.ruff_cache/\n*.html\n' >> "$repo/.git/info/exclude" \
  && git -C "$repo" config user.name 'Developer' \
  && git -C "$repo" config user.email 'developer@example.invalid' \
  && git -C "$repo" config commit.gpgsign false \
  && git -C "$repo" add -A \
  && git -C "$repo" commit -q -m 'Start the project' \
  || { echo "repository setup failed in $repo"; exit 2; }
(
  cd "$repo" || exit 2
  env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" PATH="$PATH" SHELL="$SHELL" TMPDIR="$TMPDIR" LANG="${LANG-}" \
    CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
    claude -p --model claude-opus-5-5 --tools Bash,Read,Edit,Write --allowedTools Bash,Read,Edit,Write \
    --strict-mcp-config --setting-sources project --disable-slash-commands --no-session-persistence \
    --settings "$DENY" --max-budget-usd 2.00 --output-format stream-json --verbose \
    < "$PROMPT" > "$OUT"
)
status=$?
park_rep_dir "$run" && repo="$PARK/repdirs/${run##*/}/repo"
sweep_strays
echo "probe exit=$status dir=$repo claude_md_sha256=$claude_md_sha block_sha256=$block_sha"
exit "$status"

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
# /tmp/mnb98/rep-XXXXXX, must not be inside any other repository. The last line printed gives the
# rep directory and the sha256 of its CLAUDE.md and of the block (null in the control arm). The
# stream holds home paths and a session id. Keep <out-file> outside the repository and never
# commit it.
set -u
[ "$#" -eq 2 ] || [ "$#" -eq 3 ] || { echo "usage: probe.sh <arm> <out-file> [<prompt-file>]"; exit 2; }
KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
ARM="$1"
case "$ARM" in
  control | block) ;;
  *) echo "refusing: arm must be control or block, not $ARM"; exit 2 ;;
esac
PROMPT="${3:-$KIT/isolation_probe.txt}"
[ -f "$PROMPT" ] || { echo "refusing: no prompt file $PROMPT"; exit 2; }
PROMPT="$(cd "$(dirname "$PROMPT")" && pwd)/$(basename "$PROMPT")"
OUTDIR="$(mkdir -p "$(dirname "$2")" && cd "$(dirname "$2")" && pwd)" || exit 2
OUT="$OUTDIR/$(basename "$2")"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 2; }
ROOT="$(git -C "$KIT" rev-parse --show-toplevel)" || exit 2
BLOCK="$ROOT/templates/marimo-repo/notebook-block.md"
ANCHOR='marimo-pair drives live notebook sessions in this repo.'
DENY='{"permissions":{"deny":["Read(~/**)","Edit(~/**)","Write(~/**)"]}}'
[ "$ARM" = control ] || [ -f "$BLOCK" ] || { echo "refusing: no block at $BLOCK"; exit 2; }
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
echo "probe exit=$status dir=$repo claude_md_sha256=$claude_md_sha block_sha256=$block_sha"
exit "$status"

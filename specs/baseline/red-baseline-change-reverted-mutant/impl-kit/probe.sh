#!/bin/bash
# Check the implementer micro-test's isolation before any rep. This runs one probe prompt through
# `claude -p` with the environment and the flags of run_reps.sh. Keep the two `claude -p` command
# lines identical. The stream shows what the session loaded, such as its tools and its skills.
# The run starts in a new, empty directory under /tmp, outside every repository.
# Usage: probe.sh <out-file> [<prompt-file>]
# <prompt-file> defaults to isolation_probe.txt. env_check.txt is the second probe: it checks that
# a rep authenticates under `env -i`, that the venv runs, and that the --settings deny rules load.
# The stream holds home paths and a session id. Keep <out-file> outside the repository and never
# commit it.
set -u
[ "$#" -eq 1 ] || [ "$#" -eq 2 ] || { echo "usage: probe.sh <out-file> [<prompt-file>]"; exit 2; }
KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
PROMPT="${2:-$KIT/isolation_probe.txt}"
[ -f "$PROMPT" ] || { echo "refusing: no prompt file $PROMPT"; exit 2; }
PROMPT="$(cd "$(dirname "$PROMPT")" && pwd)/$(basename "$PROMPT")"
OUTDIR="$(mkdir -p "$(dirname "$1")" && cd "$(dirname "$1")" && pwd)" || exit 2
OUT="$OUTDIR/$(basename "$1")"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 2; }
DENY='{"permissions":{"deny":["Read(~/**)","Edit(~/**)","Write(~/**)"]}}'
run="$(mktemp -d /tmp/mt-probe-XXXXXX)" || exit 2
(
  cd "$run" || exit 2
  git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $run is inside a git repository"; exit 2; }
  env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" PATH="$PATH" SHELL="$SHELL" TMPDIR="$TMPDIR" LANG="${LANG-}" \
    CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
    claude -p --model sonnet --tools Bash,Read,Edit,Write --allowedTools Bash,Read,Edit,Write \
    --strict-mcp-config --setting-sources "" --disable-slash-commands --no-session-persistence \
    --settings "$DENY" --max-budget-usd 1.50 --output-format stream-json --verbose \
    < "$PROMPT" > "$OUT"
)
status=$?
echo "probe exit=$status dir=$run"
exit "$status"

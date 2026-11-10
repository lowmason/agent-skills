#!/bin/bash
# Run the Codex reader for plan 83's statement-readings probe, adapted from plan 81's runner
# (specs/baseline/red-baseline-acceptance-tests/kit/run_codex.sh), on the owner's machine (DF-ARMS). Each rep runs
# `codex exec` from a fresh empty directory under /tmp, outside every repository, under `env -i` with only
# HOME, USER, LOGNAME, PATH, SHELL, TMPDIR and LANG, with the prompt on stdin and a read-only sandbox.
# rep<i>.md holds the last message, rep<i>.log the whole log, whose header names the model that ran
# (measure.py makes a rep on another model VOID).
# Isolation (Task 4): the flags drop the user's config.toml (its plugins and their SessionStart
# hooks, its MCP servers, personality and effort), the execpolicy rules and session persistence,
# and they disable the tools that runs/pilot/codex-isolation/ found, the shell included, so that a
# rep reads only its prompt, as the Claude reader's `--tools ""` does. `read-only` alone blocks
# writes, not reads. The effort is pinned (ultra by default, the config's value at the spec's
# check), so a rewrite of the config's effort line cannot move it within an arm. Each call appends
# its settings and the prompt's sha256 to <out-dir>/SOURCES.txt.
# Usage: run_codex.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model> [<effort>]
set -u
PROMPT="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" || exit 2
OUT="$(mkdir -p "$2" && cd "$2" && pwd)" || exit 2
FIRST="$3"
LAST="$4"
MODEL="${5:?usage: run_codex.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model> [<effort>]}"
EFFORT="${6:-ultra}"
ISOLATION=(--ignore-user-config --ignore-rules --ephemeral --enable skip_host_skill_discovery -c web_search="disabled"
  --disable shell_tool --disable unified_exec --disable code_mode_host --disable plugins --disable apps
  --disable hooks --disable skill_search --disable tool_suggest --disable multi_agent --disable goals
  --disable browser_use --disable computer_use --disable in_app_browser --disable image_generation
  --disable view_image --disable sleep_tool)
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  for f in "$OUT/rep$i.md" "$OUT/rep$i.log"; do
    [ -e "$f" ] && { echo "refusing: $f exists"; exit 2; }
  done
  i=$((i + 1))
done
echo "reps $FIRST-$LAST: prompt $1 sha256 $(shasum -a 256 < "$PROMPT" | cut -d' ' -f1), $(codex --version)," \
  "model $MODEL, effort $EFFORT, flags ${ISOLATION[*]}" >> "$OUT/SOURCES.txt"
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  run="$(mktemp -d /tmp/plan83-codex-XXXXXX)" || exit 2
  (
    cd "$run" || exit 2
    git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $run is inside a git repository"; exit 2; }
    env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" PATH="$PATH" SHELL="$SHELL" TMPDIR="$TMPDIR" \
      LANG="${LANG:-en_US.UTF-8}" \
      codex exec -m "$MODEL" -c sandbox_mode=read-only -c "model_reasoning_effort=\"$EFFORT\"" "${ISOLATION[@]}" \
      --skip-git-repo-check -C "$run" -o "$OUT/rep$i.md" - < "$PROMPT" > "$OUT/rep$i.log" 2>&1
  )
  echo "rep$i exit=$?"
  rmdir "$run" 2> /dev/null
  i=$((i + 1))
done

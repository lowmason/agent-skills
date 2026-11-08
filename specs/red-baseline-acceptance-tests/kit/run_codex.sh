#!/bin/bash
# Run the Codex reader for plan 81's probe (Task 4, on the owner's machine). Each rep runs
# `codex exec` from a fresh empty directory under /tmp, outside every repository, with the prompt
# on stdin and a read-only sandbox. rep<i>.md holds the last message, rep<i>.log the whole log,
# whose header names the model that ran (measure.py refuses a rep on another model).
# Usage: run_codex.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model>
set -u
PROMPT="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" || exit 2
OUT="$(mkdir -p "$2" && cd "$2" && pwd)" || exit 2
FIRST="$3"
LAST="$4"
MODEL="${5:?usage: run_codex.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model>}"
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  for f in "$OUT/rep$i.md" "$OUT/rep$i.log"; do
    [ -e "$f" ] && { echo "refusing: $f exists"; exit 2; }
  done
  i=$((i + 1))
done
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  run="$(mktemp -d /tmp/plan81-codex-XXXXXX)" || exit 2
  (
    cd "$run" || exit 2
    git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $run is inside a git repository"; exit 2; }
    codex exec -m "$MODEL" -c sandbox_mode=read-only --skip-git-repo-check -C "$run" \
      -o "$OUT/rep$i.md" - < "$PROMPT" > "$OUT/rep$i.log" 2>&1
  )
  echo "rep$i exit=$?"
  rmdir "$run" 2> /dev/null
  i=$((i + 1))
done

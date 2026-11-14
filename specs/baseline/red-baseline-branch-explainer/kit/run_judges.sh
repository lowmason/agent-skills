#!/bin/bash
# Run the reader, then the adjudicator, for each writer rep of plan 94's branch explainer probe.
# Usage: run_judges.sh <arm> <fixture> <out-dir> <rep> [<rep> ...]
# <arm> is control or treatment. For each rep: the reader runs into <out-dir>/reader/rep<N>.json
# (cap $0.50), unless that file already passes `kit.py result-ok`, so a retry keeps the synopsis
# under score. A reader file that fails result-ok moves to reader/rep<N>.bad<k>.json (with its
# .err) before the rerun; after two bad readers on one rep the script stops (exit 3): ask the
# owner. The adjudicator runs into <out-dir>/adj/rep<N>.json with the cap ADJ_CAP (default 2.00);
# an existing adj file is never overwritten. Both run tool-less on claude-opus-5-5 through
# run_plain.sh. Prompts go to ~/.cache/agent-skills/scratch/plan94/prompts/.
set -u
KIT="$(cd "$(dirname "$0")" && pwd)" || exit 2
ROOT="$(git -C "$KIT" rev-parse --show-toplevel)" || exit 2
ARM="${1:?usage: run_judges.sh <arm> <fixture> <out-dir> <rep> [<rep> ...]}"
FX="${2:?fixture}"
OUT="$(cd "${3:?out-dir}" && pwd)" || exit 2
shift 3
case "$ARM" in
  control|treatment) ;;
  *) echo "refusing: arm must be control or treatment"; exit 2 ;;
esac
[ "$#" -ge 1 ] || { echo "refusing: no reps named"; exit 2; }
ADJ_CAP="${ADJ_CAP:-2.00}"
MODEL=claude-opus-5-5
READER_CAP=0.50
PROMPTS="$HOME/.cache/agent-skills/scratch/plan94/prompts/$(basename "$(dirname "$OUT")")/$(basename "$OUT")"
mkdir -p "$PROMPTS" "$OUT/reader" "$OUT/adj" || exit 2
kit() { (cd "$ROOT" && uv run --quiet "$KIT/kit.py" "$@"); }
for n in "$@"; do
  explainer="$OUT/rep$n.md"
  [ -f "$explainer" ] || { echo "rep$n: no explainer file, skipped"; continue; }
  reader="$OUT/reader/rep$n.json"
  if kit result-ok "$reader" > /dev/null; then
    echo "rep$n: reader kept"
  else
    if [ -e "$reader" ]; then
      k=1
      while [ -e "$OUT/reader/rep$n.bad$k.json" ]; do k=$((k + 1)); done
      mv "$reader" "$OUT/reader/rep$n.bad$k.json"
      [ -e "$OUT/reader/rep$n.err" ] && mv "$OUT/reader/rep$n.err" "$OUT/reader/rep$n.bad$k.err"
    fi
    bad=0
    for f in "$OUT/reader/rep$n".bad*.json; do [ -e "$f" ] && bad=$((bad + 1)); done
    if [ "$bad" -ge 2 ]; then
      echo "rep$n: two bad readers: stop and ask the owner"
      exit 3
    fi
    kit reader-prompt "$ARM" "$explainer" > "$PROMPTS/reader-rep$n.txt" || exit 2
    bash "$KIT/run_plain.sh" "$PROMPTS/reader-rep$n.txt" "$OUT/reader" "$n" "$n" "$MODEL" "$READER_CAP" \
      | sed "s/^/reader /"
    if ! problem="$(kit result-ok "$reader")"; then
      echo "rep$n: reader failed ($problem): no adjudicator"
      continue
    fi
  fi
  adjudication="$OUT/adj/rep$n.json"
  if [ -e "$adjudication" ]; then
    echo "rep$n: adj/rep$n.json exists, skipped (move it to adj/rep$n.bad<k>.json to rerun)"
    continue
  fi
  kit adjudicator-prompt "$ARM" "$FX" "$explainer" "$reader" > "$PROMPTS/adj-rep$n.txt" || exit 2
  bash "$KIT/run_plain.sh" "$PROMPTS/adj-rep$n.txt" "$OUT/adj" "$n" "$n" "$MODEL" "$ADJ_CAP" | sed "s/^/adj /"
  if problem="$(kit result-ok "$adjudication")"; then
    echo "rep$n: adjudication ok"
  else
    echo "rep$n: adjudication failed ($problem)"
  fi
done

#!/bin/bash
# Run the reps listed in $PHR_CTL/batches/BATCH.txt one at a time, skipping any
# rep that already has results, so an interrupted batch resumes where it
# stopped. It stops at the first rep that run_rep.sh refuses or fails. bash 3.2.
#
# Usage: run_batch.sh BATCH
set -euo pipefail

KIT_DIR=$(cd "$(dirname "$0")" && pwd -P)
CTL=${PHR_CTL:-$HOME/.cache/agent-skills/handoffs/guard101}
batch=${1:?usage: run_batch.sh BATCH}
list=$CTL/batches/$batch.txt
[ -f "$list" ] || { echo "run_batch.sh: no $list" >&2; exit 2; }

while IFS= read -r rep <&3; do
  case $rep in ''|'#'*) continue ;; esac
  if [ -e "$CTL/results/$rep" ]; then echo "skip $rep: has results" >&2; continue; fi
  status=0
  /bin/bash "$KIT_DIR/run_rep.sh" "$rep" < /dev/null || status=$?
  if [ "$status" -ne 0 ]; then
    echo "run_batch.sh: run_rep.sh $rep exited $status; batch $batch stopped" >&2
    exit "$status"
  fi
done 3< "$list"

#!/bin/bash
# C1: the task reaches review. The implementer's screens 1 and 2 and its report, which cites screen 2.
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/../seed_lib.sh"
. "$HERE/../bands/seed.sh"
bands_implementer

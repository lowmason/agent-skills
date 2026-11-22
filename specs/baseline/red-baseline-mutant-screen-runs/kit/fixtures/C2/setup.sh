#!/bin/bash
# C2: C1's state, the controller's test run and first mutant run, then fix round 1: the fix commit,
# mutant 4, screen 3 and the fix report.
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/../seed_lib.sh"
. "$HERE/../bands/seed.sh"
bands_implementer
bands_controller_run
bands_fix

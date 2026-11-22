#!/bin/bash
# I2: C1's state and the controller's clean mutant run (no --screen), before fix round 4.
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/../seed_lib.sh"
. "$HERE/../bands/seed.sh"
bands_implementer
bands_controller_run

'''The case of plan 111's trigger test: the skill under test, the listing check, the quarantine, the arms and
the models. audit.py and triggers.py read it.

Plan 107's cases.py (specs/baseline/red-baseline-writing-skills-tests/kit/cases.py) held that kit's frozen
conversations, and its audit imported it. This kit runs the trigger test only, so the file keeps its name and
the import and holds the facts that the audit and the tally share.
'''
from pathlib import Path

KIT = Path(__file__).resolve().parent
SKILL = 'classification-codes'
# The listing check: a rep whose init record lacks one of these names is void. fixtures/trigger/listing.txt
# holds them, so run_trigger_reps.sh, which refuses a ref whose skills/ lacks one, reads the same list.
REQUIRED_LISTING = tuple((KIT / 'fixtures' / 'trigger' / 'listing.txt').read_text().split())
ARMS = ('old', 'new')
MODELS = ('claude-opus-5-5', 'claude-sonnet-5-5')
REPS_PER_CELL = 3
# Rule 5: a rep that reads one of these is void (audit.quarantine_hits). They name this plan, the kit and its
# write-up (red-baseline-codes-description covers both) and the backlog, matched in any case.
QUARANTINE = ('111-codes-and-bls-reference-skills', 'red-baseline-codes-description', 'deferred_items.md')
# Where those files sit in a checkout of this repository. A search rooted at a folder that holds one of them is a
# rule 5 hit. The plan is listed at both places it lives: specs/plans/ now, specs/plans/completed/ once retired.
QUARANTINED_PATHS = ('specs/plans/111-codes-and-bls-reference-skills.md',
                     'specs/plans/completed/111-codes-and-bls-reference-skills.md',
                     'specs/baseline/red-baseline-codes-description',
                     'specs/baseline/red-baseline-codes-description.md', 'specs/deferred_items.md')

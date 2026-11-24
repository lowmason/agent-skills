# Proposal: reword step 2 of `changelog-entry`

## The old line

In `skills/changelog-entry/SKILL.md`, step 2 of The Technique reads:

> 2. Start the line with the verb that names the change: Add, Fix, Remove or Change.

## The proposed line

> 2. Start the line with what a reader can now do or no longer suffers: "Export reports as CSV", "Stop losing the cursor on save".

## Why

Entries that start with "Fix" or "Change" often stop at the verb and then name an internal part:
"Fix handler", "Change parser". A reader learns nothing from them. The proposed line moves the
reader's outcome to the front, so the entry cannot be written without it.

## Risk

An agent may drop the leading verb altogether and write a sentence that is longer than 100 characters.

## Merge

The partner merges the change after the check of the new wording.

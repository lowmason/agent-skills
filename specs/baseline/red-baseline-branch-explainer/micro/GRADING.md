# Grading: plan 94's Step 3b micro-test

Each rep is one tool-less `claude -p` answer on `claude-sonnet-5-5`, run by `kit/run_plain.sh` from a prompt that
`build_micro.py` builds. The answer is a numbered list of `RUN`, `TOOL`, `EDIT`, `ASK` and `REPORT` actions, with `IF`
lines for outcomes the agent has not seen. The executor grades every answer by hand and quotes the deciding words.

## Rules for every scenario

**Read rule.** A TOOL Read of a file under references/ is an allowed read-only step. Grade the actions after it, IF lines included. An answer that ends at the Read, with no action after it, is NEITHER, which does not count as PASS, except in M6.

**VOID rule.** A rep is VOID when `kit.py result-ok` fails on its JSON (no file, not JSON, an error, a budget stop or
an empty result), or when its result shows a tool, an advisor iteration or a second model. Rerun a VOID rep under the
next free rep number. A scenario's scored reps are its first 5 reps that are not VOID, and only scored reps count
toward the bar.

The screen for the second half of the VOID rule is plan 60's `exclusion_reason`: the JSON's `usage.iterations` holds a
type other than `message`, or `modelUsage` names more than one model, or either record is missing. A `num_turns`
above 1 or a non-empty `permission_denials` also shows a tool.

**Bar.** Each treatment scenario passes in at least 4 of 5 scored reps. The control arms of M1 and M2 are recorded
and have no bar.

## Scenarios

Task 5 adds one row per scenario.

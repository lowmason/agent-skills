# Plan 101 micro-tests: completion triage and gate revert

This record holds the micro-tests for plan 101 (`specs/plans/101-plan-completion-triage-and-gate-revert.md`). A
micro-test runs one decision many times through a fresh `claude -p` with no tools, then reads each reply by a rule
fixed in advance. One run is a rep. Plan 101 changes the wording of five texts, and each change gets cases:

- `triage-narrow` and `triage-aged`: at step 4 of the writing-plans Plan Completion Protocol, the agent reports
  backlog health. The wording change limits the grouped disposition proposal to a backlog with an aged tail. A backlog
  with 20 or more open items and no aged tail gets the summary line and a pointer to `/deferred`. The texts under test
  are `skills/writing-plans/SKILL.md` and `skills/writing-plans/references/deferred-backlog.md`.
- `gate-revert-sdd`, `gate-revert-ep` and `gate-revert-untagged`: at the plan-completion gate, the partner reverts
  a ruling that the gate listed. The wording change makes the revert a task that runs now, before plan markup, with a
  ledger line `Reverted at the gate: <task> ruling — <its first words>` and no backlog item. The texts under test are
  the `references/final-review.md` files of subagent-driven-development and executing-plans.
- `history-revert`: at protocol step 5, after a `/clear`, the history entry leaves out a ruling that a
  `Reverted at the gate:` ledger line names. The texts under test are `skills/writing-plans/SKILL.md` and
  `skills/writing-plans/references/histor*.md`.
- `gate-declined`: this is protocol step 1, run from writing-plans alone after a `/clear`. The gate message puts the
  Declined to judge lines and an unfixed finding to the partner in one batch. The text under test is
  `skills/writing-plans/SKILL.md`.
- `gate-tag-ep`: plan 80's `gate-tag` fixture, recast as an executing-plans run. No case tested the
  executing-plans copy of the gate paragraph before.

Two regression cases are re-runs of plan 80's `gate-tag` and `history-filter`. They use plan 80's fixtures and pass
rules unchanged, which `specs/baseline/red-baseline-development-history.md` holds. They get no case here.

| Case | Kind | Model | Budget |
|---|---|---|---|
| `triage-narrow` | RED | `claude-sonnet-5-5` | $0.75 |
| `triage-aged` | guard | `claude-sonnet-5-5` | $0.75 |
| `gate-revert-sdd` | RED | `claude-opus-5-5` | $1.00 |
| `gate-revert-ep` | RED | `claude-opus-5-5` | $1.00 |
| `gate-revert-untagged` | guard | `claude-opus-5-5` | $1.00 |
| `history-revert` | RED | `claude-opus-5-5` | $1.00 |
| `gate-tag-ep` | guard | `claude-opus-5-5` | $1.00 |
| `gate-declined` | RED | `claude-opus-5-5` | $1.00 |
| `gate-tag` (re-run) | regression | `claude-opus-5-5` | $1.00 |
| `history-filter` (re-run) | regression | `claude-opus-5-5` | $1.00 |

Task 2 builds the kit, registers the rules and runs the control arms. Task 8 runs the treatment arms and the two
re-runs with the same kit.

## Base

`BASE101` is the commit at the start of plan 101's execution. It is the commit that the control arm reads its texts
from: `72d08bf` (`72d08bf0e6b6cb0e4f40ec4e0e36a5dcbb0a6a29`).

Task 1's spec amendment sits after it, at `e36ceff`. One check ran when this record was written:
`git diff --stat 72d08bf HEAD -- skills commands` printed nothing. So no skill or command text changed between
`BASE101` and the commit that registers this kit. The one file that changed is the spec,
`specs/plan-completion-triage-and-gate-revert.md`.

## Kit

Kit: `specs/baseline/red-baseline-completion-triage/kit/`. Four files are copies of plan 80's kit
(`specs/baseline/red-baseline-development-history/kit/`), made with `cp -p`. No file of plan 80's kit was edited.

- `run_reps.sh` changes the plan number in its first comment line (80 to 101) and its temp prefix, from
  `/tmp/plan80-rep-` to `/tmp/plan101-rep-`. The comment `Plan 77 deviation (a)` keeps its number, as in plan 80's
  record. The file mode stays executable. It also carries the next-kit fix below.
- `isolation_probe.txt` is an unchanged copy.
- `show_reps.py` changes the plan number in its docstring. Its five reading aids flag `/deferred` (`deferred-cmd`),
  `Reverted at the gate` (`reverted`), `Declined` (`declined`), `deferred item` (`deferred-item`) and a question
  mark (`question`). Each aid ignores case. An aid only points the reader at a reply. It is never a verdict.
- `build_prompts.py` changes only the plan number in its docstring.
- `cases.py` is new. Its shape is plan 80's: `case(texts, fixture, task, pass_rule, leak, bar)`, a `VOID` rule and
  constants. It adds two keyword arguments, `model` and `budget`, with the Opus values as defaults, because the two
  triage cases run on Sonnet. It holds the eight cases above.

**Next-kit fixes (owner, plan 101, 2026-11-17).** Two files are new, and `run_reps.sh` calls the first.

- `scrub_json.py` has `scrub(text: str) -> str`. It parses the text as JSON, drops every `credential_expires_at` key at
  any depth, and returns the JSON dumped with `ensure_ascii=False`. When the text does not parse, it returns the text
  without each line that holds the key. So `show_reps.py` still reads an unreadable rep as VOID. As a script,
  `python3 scrub_json.py <file>` rewrites the file in place.
- `run_reps.sh` sets `KIT` to its own folder, as an absolute path, before any `cd`. After each rep's subshell it
  saves the rep's exit status, runs `python3 "$KIT/scrub_json.py" "$OUT/rep<N>.json"`, and then prints
  `rep<N> exit=<status>`. The scrub never changes the exit line.
- `kit_selftest.py` is the no-model self-test, run as `uv run python <kit>/kit_selftest.py`. It writes a stub
  `claude` that ignores its arguments, writes `marker-<its pid>` into its working directory, and prints one JSON object
  with `credential_expires_at` at the top level and inside `usage`. It puts the stub first on a PATH built from scratch,
  so the real CLI can never run. It runs `run_reps.sh` for reps 1 and 2 and checks three things. Neither rep file holds
  `credential_expires_at`, and both still parse with `type`, `result` and `total_cost_usd`. Each rep lists exactly one
  name, a `marker-` file, and the two markers differ, so each rep sees only its own folder. The two working directories
  differ, and both sit under `/tmp/plan101-rep-` or `/private/tmp/plan101-rep-`. The test removes the two folders by
  their exact paths when it ends.

The self-test went RED first. Run against the copied runner, before `scrub_json.py` existed, it stopped with
`AssertionError: rep1.json still holds credential_expires_at`. After the fix it printed `kit self-test passed`. Two
throwaway mutants of the runner were also run, and the test caught both. A runner that shares one folder between reps
stopped at the one-name check (`rep2 should list exactly one marker- name in its folder`). A scrub that does nothing
stopped at the same `credential_expires_at` check as the RED run.

No file in `kit/` is named `test_*.py`. `uv run python build/run_suites.py --check` prints `suite registry ok` with
`kit_selftest.py` in place.

A script checked the registered text against its sources. The pass rules of the five cases whose table cells give
one in full (`triage-narrow`, `triage-aged`, `gate-revert-sdd`, `history-revert` and `gate-declined`) match the cells
word for word. So do the leak patterns of the four cases whose cells give one in full. The strings that plan 80 and
plan 74 own match their sources byte for byte. From plan 80 they are `VOID`, `BAR`, `GATE_PASS`, `GATE_TASK`,
`GATE_LEAK`, its gate fixture, its gate list, its four ledger rulings, its spec sections and its history draft. From
plan 74 it is `TASK_TAIL`.
The three cells that point at a rule elsewhere are read as the Reading rules section says.

`build_prompts.py <sha> <out-dir> [<case> ...]` builds the prompts at a sha and writes `MANIFEST.txt`.
`build_prompts.py leakview <out-dir>` puts a placeholder in place of every text under test, for the leak grep.
`run_reps.sh <prompt> <out-dir> <first> <last> <model> <budget>` runs the reps.

Each rep is a fresh
`claude -p --model <case model> --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json --max-budget-usd <case budget>`
with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, under `env -i`. Only `HOME`,
`USER`, `LOGNAME`, `PATH`, `SHELL`, `TMPDIR` and `LANG` pass through, each only when it is set. The rep runs from a
new, empty directory `/tmp/plan101-rep-XXXXXX`, outside every repository. Work files go under `/tmp/plan101-work/`.
There are 5 scored reps per case and arm. Every verdict is read by hand from the full reply.

## Arms

- `control`: each text at `BASE101` (`72d08bf`). At `72d08bf`, the `histor*.md` glob matches
  `skills/writing-plans/references/history.md`, so the `history-revert` control prompt carries that file and the
  writing-plans `SKILL.md` body.
- `treatment`: each text at `<T7>`, the last commit of Task 7. Task 8 runs it and fills in the sha here.
- Wording round: a case below its bar gets one wording round, at its own commit, `<T8>`. Task 8 fills in the sha
  here when a round happens.
- The `gate-tag` and `history-filter` re-runs build their prompts with plan 80's kit, unchanged, and run them through
  this kit's `run_reps.sh`. Task 8 appends their results to `specs/baseline/red-baseline-development-history.md`.
- `gate-tag-ep` also has a control arm at `BASE101`, for reading only. The control shows whether a failure is old or
  new.

Both arms use the same frame, fixture and task. Only the sha of the texts differs. A `SKILL.md` text is its body with
the frontmatter removed. A reference file is the whole file. Texts are read with `git show <sha>:<path>`, never
through `~/.claude/skills/`.

## Bars

A RED case needs `treatment 5/5; control fails at least 1 of 5`. The treatment arm must pass all 5 scored reps. The
control arm must fail at least 1 of its 5 scored reps, or the wording change has nothing to fix.

A guard or regression case needs `treatment 5/5`.

- RED: `triage-narrow`, `gate-revert-sdd`, `gate-revert-ep`, `history-revert`, `gate-declined`.
- Guard: `triage-aged`, `gate-revert-untagged`, `gate-tag-ep`.
- Regression: the `gate-tag` and `history-filter` re-runs.

A case below its bar gets one wording round. The `gate-tag` re-run meeting its bar closes the second item's
`Done when:` in the spec.

## Spend stops

The whole kit stops at $30. The sum is `total_cost_usd` over every `rep<N>.json` in this record's folders and in plan
80's re-run folders, and `show_reps.py` prints it. If the control arms alone pass $12, the run stops and asks the
owner. Task 9's guard kit has its own stop, in its own record.

## Stop rule

A RED case whose control fails 0 of 5 has nothing to fix in wording. Record it and put it to the owner in the
completion gate's batch. The spec-required wording still lands.

## Leak check

`build_prompts.py leakview /tmp/plan101-work/leak` wrote the eight leak-view prompts. Each was grepped with
`/usr/bin/grep -nE` for its own case's leak pattern, first with the case as written and then with `-i`. The two
passes gave the same hits. Then each distinct pattern was also grepped, with `-i`, over every prompt.

| Case | Own pattern | Hits |
|---|---|---|
| `triage-narrow`, `triage-aged` | `Backlog report\|full triage\|waits for` | none |
| `gate-revert-sdd`, `gate-revert-ep`, `gate-revert-untagged` | `Reverted at the gate\|follow-up task\|protocol step 1` | none |
| `history-revert` | `changed the build\|kept the plan as written\|rule 3` | none |
| `gate-tag-ep` | `contradicts spec\|spec section\|changed the build` | none |
| `gate-declined` | `Declined to judge` | lines 23 and 24 |

The two hits in `gate-declined` are the final review's two Declined to judge lines in the fixture. The table names
them as expected. The case tests whether the gate message puts those lines to the partner, so the lines have to be in
the fixture. The hits stand. No hit comes from the frame, the task line or the rest of the fixture.

The cross-grep found hits in other cases. Each stands for the same reason: the fixture shows a state that the
tested text acts on, and the pattern belongs to a different case.

- `Declined to judge` in the four gate cases `gate-revert-sdd`, `gate-revert-ep`, `gate-revert-untagged` and
  `gate-tag-ep` (line 14 of each). Plan 80's gate fixture has one such line, and the recast keeps it. These four
  cases do not test the Declined to judge wording.
- `Reverted at the gate` in `history-revert` (line 34). It is the ledger line that the case shows on purpose. The
  case tests whether the entry leaves out the ruling that this line names, not whether the agent finds the line.
- `protocol step 1` in `gate-declined` (line 28). The task line names the step, as the plan's table says: "write the
  message you send your partner at protocol step 1". The case's own pattern is `Declined to judge`.
- `contradicts spec` in `gate-revert-sdd`, `gate-revert-ep` and `gate-revert-untagged` (line 33). It is the tag on
  the Task 2 ruling in the gate message that already went out. The case's fixture says so on purpose.

## Reading rules

These rules were registered and committed before any rep ran. Fixtures and rules are not edited after any rep
output is seen.

**VOID (every case).** VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no dispatch, no paragraph and no instruction).

This VOID rule is plan 80's, word for word. Its last parenthetical names plan 76's task outputs. This record reads
its main clause. A reply that writes no message, no ledger line, no edit, no command and no entry does no part of the
task. A rerun happens only within the spend stop. The scored reps of a case are its first 5 reps that are not VOID.

**The three cells that point at a rule elsewhere.** The plan's table gives `gate-revert-ep` and
`gate-revert-untagged` a pass rule by reference to `gate-revert-sdd`. This record registers each as one text
substitution into the `gate-revert-sdd` rule, made in `cases.py`:

- `gate-revert-ep`: "as a task before plan markup" becomes "inline, before plan markup".
- `gate-revert-untagged`: "the Task 2 ruling" becomes "the Task 3 module-name ruling".

The table gives `gate-tag-ep` plan 80's `GATE_PASS`, `GATE_TASK` and `GATE_LEAK` by name. The `gate-tag-ep` rule and
leak pattern below are those strings, copied word for word. The `triage-aged` cell for texts and leak pattern says "as
`triage-narrow`", and the `gate-revert-untagged` cell for texts says "as `gate-revert-sdd`". Both read as the same
values.

**triage-narrow** (texts: `skills/writing-plans/SKILL.md` and `skills/writing-plans/references/deferred-backlog.md`).
Model `claude-sonnet-5-5`, budget 0.75. Bar: `treatment 5/5; control fails at least 1 of 5`.

Fixture: the agent controls a subagent-driven run of a bike-share dock-status service. Steps 1 to 3 of the
protocol are done. Step 3 appended two items to a new section `12-dock-alerts`, each with its title and `Size:`. The fixture
shows the real output of `deferred_stats.py` at `72d08bf`: `Deferred backlog: 26 open, 51 ever closed (closure rate
66%), aged >45d: 0.`, then the oldest-open, age-spread and volume lines. It lists the 26 open items, one line each, in
9 sections. The oldest section is 35 days old. The listing is enough for a triage. Task: finish step 4 and write what
you would do and the message to the partner.

PASS = the reply shows the summary line and both new items; it presents no disposition proposal over the backlog (no grouped or sorted list of the older items with a proposed action); and it goes on to step 5 or names /deferred for the full triage. FAIL = any of these does not hold.

**triage-aged** (the same texts). Model `claude-sonnet-5-5`, budget 0.75. Bar: `treatment 5/5`.

Fixture: the same, with `aged >45d: 2.` Sections `3-station-geocoding` and `4-api-limits` hold one item each. They
carry the dates 2026-09-09 and 2026-09-20. So two items are 61 and 50 days old on 2026-11-09, and no other item ages.
The stats lines are the script's real output for that listing. Task: the same.

PASS = the reply shows the summary line and both new items; it presents a read-only grouped disposition proposal over the backlog; it edits no file for the proposal; and it does not stop the protocol on it (it goes on to step 5, or says that it does). FAIL = any of these does not hold.

**gate-revert-sdd** (text: `skills/subagent-driven-development/references/final-review.md`). Model `claude-opus-5-5`,
budget 1.00. Bar: `treatment 5/5; control fails at least 1 of 5`.

Fixture: plan 80's gate fixture, word for word. The gate message already went out. It lists the four rulings, the
Task 2 ruling tagged, and puts the final review's Declined to judge line to the partner. The partner answers: revert
the Task 2 ruling, the other three stand, and email at night is fine. The partner's answer to the Declined to judge
line leaves nothing open, so a reply cannot stop to ask about it. Task: act on the partner's answer, with plan 74's
`TASK_TAIL`.

PASS = the next action implements the revert now, as a task before plan markup; the reply writes a ledger line that names the Task 2 ruling; and it writes no backlog item for the revert. FAIL = any of these does not hold.

**gate-revert-ep** (text: `skills/executing-plans/references/final-review.md`). Model `claude-opus-5-5`, budget 1.00.
Bar: `treatment 5/5; control fails at least 1 of 5`.

Fixture: the same run, recast as an executing-plans run. The agent executes the plan inline. The whole-plan review has
two seats, the code-reviewer and Codex. The ledger's task lines take executing-plans' form, `complete (commits
<base7>..<head7>, mutants: <caught>/<total>, tests: <command> → <result>)`. The four ruling lines are plan 80's, word
for word. The gate message and the partner's answer are the same as in `gate-revert-sdd`.

PASS = the next action implements the revert now, inline, before plan markup; the reply writes a ledger line that names the Task 2 ruling; and it writes no backlog item for the revert. FAIL = any of these does not hold.

**gate-revert-untagged** (text: `skills/subagent-driven-development/references/final-review.md`). Model
`claude-opus-5-5`, budget 1.00. Bar: `treatment 5/5`.

Fixture: as `gate-revert-sdd`, but the partner reverts the Task 3 module-name ruling, which the gate did not tag, and
the other three rulings stand.

PASS = the next action implements the revert now, as a task before plan markup; the reply writes a ledger line that names the Task 3 module-name ruling; and it writes no backlog item for the revert. FAIL = any of these does not hold.

**history-revert** (texts: `skills/writing-plans/SKILL.md` and `skills/writing-plans/references/histor*.md`). Model
`claude-opus-5-5`, budget 1.00. Bar: `treatment 5/5; control fails at least 1 of 5`.

Fixture: plan 80's history fixture, after a `/clear`. The gate message is not in context, and the fixture shows the
spec's three sections instead. The ledger is shown in full. It holds the four rulings, the line
`Reverted at the gate: Task 2 ruling — alert at 3 or fewer free slots`, and a ledger line for the revert's task. The
revert's commits are in. The draft that `history_entry.py draft` printed is plan 80's draft: it still lists the Task 2
ruling, because the script lists every `Ruling:` ledger line. The base script's ledger warning looks for `Ruling:` and does
not match the `Reverted at the gate:` line, so the draft carries no warning line. Task: write the exact text appended
to `specs/history.md`.

PASS = the entry leaves out the Task 2 ruling; keeps the module-name ruling labelled "Ruling (Task 3)" with its what, why and cost parts; leaves out the batch-email and retry-jitter rulings; keeps the Deviation line with a Source pointer and the closed-item line with its quoted title and "(deferred by 9-dock-status)" unchanged; and leaves the heading and Plan line unchanged. FAIL = any of these does not hold.

**gate-tag-ep** (text: `skills/executing-plans/references/final-review.md`). Model `claude-opus-5-5`, budget 1.00.
Bar: `treatment 5/5`.

Fixture: plan 80's `GATE_FIXTURE`, recast as an executing-plans run, as in `gate-revert-ep`. It is the state before
the gate message. Task: plan 80's `GATE_TASK`.

PASS = the message lists all four rulings; the Task 2 ruling's entry contains the literal text "contradicts spec" followed by "§ 2" or "Alert threshold"; no other ruling's entry contains "contradicts spec"; and no ruling is put to the partner as a question to approve. FAIL = any of these does not hold.

**gate-declined** (text: `skills/writing-plans/SKILL.md`). Model `claude-opus-5-5`, budget 1.00. Bar: `treatment 5/5; control fails at least 1 of 5`.

Fixture: after a `/clear`, the partner says "complete the plan". Only writing-plans is loaded. All four tasks are done.
The ledger has no ruling. The final review's report shows one Important finding that is not fixed (`send_alert`
retries forever on a 5xx) and two Declined to judge lines: "Whether email is the right channel for alerts sent at
night." and "Whether 2 free slots is the right threshold for docks next to stations." The report gives a reason for the
open finding: the fix needs a retry cap, and the reviewer left the cap to the partner. So the finding stalled on the
partner's input, which is the case where protocol step 1 sends a leftover to the partner. Without a reason, step 1 would
send the finding to the "defer" branch, and a rep that followed the text would fail the rule in both arms. Task: write
the message you send your partner at protocol step 1.

PASS = the message puts both Declined to judge lines and the unfixed finding to the partner, each for a ruling, in one message; and it files neither Declined line as a deferred item without asking. FAIL = any of these does not hold.

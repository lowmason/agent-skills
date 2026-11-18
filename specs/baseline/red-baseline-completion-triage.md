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
- `treatment`: each text at `T7`, the last commit of Task 7: `4bf95a0` (`4bf95a004637b4cc16859fa06593b664bb02a8f3`).
- Wording round: a case below its bar gets one wording round, at its own commit. `triage-aged` was below its bar at
  4 of 5, so one round ran at `8b44d34` (`8b44d342b782f8ef5df3c5db63496acf549022de`), `T8`. The cases that read the
  writing-plans `SKILL.md` ran again at `T8` into `treatment-r1/`. See `## Treatment, wording round 1`.
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

## Isolation probe

The controller ran the probe with this command:
`bash specs/baseline/red-baseline-completion-triage/kit/run_reps.sh specs/baseline/red-baseline-completion-triage/kit/isolation_probe.txt /tmp/plan101-work/probe 1 1 claude-opus-5-5`.
It ran on Claude Code 2.1.323 (`claude --version` printed `2.1.323 (Claude Code)`), under `env -i`, with the
default per-rep cap of $0.50. The CLI signed in with its stored login. The expected result is all five lines `NO`,
and the probe met it: no `CLAUDE.md` text, no output style, no rule, no SessionStart context and no memory. The
reply, in full:

```text
1. NO
2. NO
3. NO
4. NO
5. NO
```

`show_reps.py` shows one turn, no extra iterations, one model (`claude-opus-5-5`), `success`, and a cost of $0.018.
The rep JSON holds no `credential_expires_at`. The probe output sits in `/tmp/plan101-work/probe` and is not
committed, so its cost is not in the kit's sum.

## Control

Arm `control`: the texts at `BASE101` (`72d08bf`). The prompts were built with
`build_prompts.py 72d08bf0e6b6cb0e4f40ec4e0e36a5dcbb0a6a29 /tmp/plan101-work/control`. `MANIFEST.txt` gives these
prompt hashes, and `shasum -a 256` on the eight prompt files prints the same values:

| Prompt | sha256 |
|---|---|
| `triage-narrow.txt` | `d026e91c177cca58a09bc80178644ac0d29bcf6412e4c50f12fbfe15ed9aa141` |
| `triage-aged.txt` | `38070566908f452b32cd6a4433c174bdd4d494552b6442ccdc130defea05e9ac` |
| `gate-revert-sdd.txt` | `79a61087cf2a681cb5637451854bf44d5c85eda3389c81151b03013795ffd86f` |
| `gate-revert-ep.txt` | `25f284f474a5de643274843a5345da85849f1de3a48911f667b3444305f7da50` |
| `gate-revert-untagged.txt` | `02362e4f0044d48dfbe80addf5b1f7bb6920c6b52369b1b98dfe95bed5d07fd2` |
| `history-revert.txt` | `585885f9dd962d2f2953a0abe8e1245ba7898b26b208fcdb84947a89f3403280` |
| `gate-tag-ep.txt` | `f4fb44f98c83a7cc3474bc0d3da7157436b3990c5e3c7f57ae0e964fa6330aa7` |
| `gate-declined.txt` | `e5c486f98413f162ae8f527b6a61035202c32401943eedff5daa2c11c56990c8` |

Each case ran 5 reps on Claude Code 2.1.323, with this command and the case's model and budget from the table at the
top of this record:
`run_reps.sh /tmp/plan101-work/control/<case>.txt specs/baseline/red-baseline-completion-triage/control/<case> 1 5 <model> <budget>`.
So there are 40 rep files. The two triage cases ran on `claude-sonnet-5-5` and the other six on `claude-opus-5-5`.
No rep was VOID: every rep ran one turn, no tool and one model, and ended with `success`. No rep wrote an error
file, so no rep was rerun. Every reply was read in full with `show_reps.py`, and every verdict was read by hand by
the committed rules. The aids only pointed at replies.

A quote from a reply has at most 12 words. A quote sits in double quotes, except a quote that holds a deferral phrase,
which sits in backticks so that the deferral lint reads it as quoted text when this record retires. Several replies
date their edits 2026-11-18, the day of the run, and not the fixture's 2026-11-09. No rule scores a date.

| Case | Kind | Bar | Passing reps | Failing reps |
|---|---|---|---|---|
| `triage-narrow` | RED | `treatment 5/5; control fails at least 1 of 5` | 0/5 | 5/5 |
| `triage-aged` | guard | `treatment 5/5` | 5/5 | 0/5 |
| `gate-revert-sdd` | RED | `treatment 5/5; control fails at least 1 of 5` | 0/5 | 5/5 |
| `gate-revert-ep` | RED | `treatment 5/5; control fails at least 1 of 5` | 1/5 | 4/5 |
| `gate-revert-untagged` | guard | `treatment 5/5` | 3/5 | 2/5 |
| `history-revert` | RED | `treatment 5/5; control fails at least 1 of 5` | 5/5 | 0/5 |
| `gate-tag-ep` | guard | `treatment 5/5` | 5/5 | 0/5 |
| `gate-declined` | RED | `treatment 5/5; control fails at least 1 of 5` | 5/5 | 0/5 |

A guard case's control is for reading only. It sets no bar.

### triage-narrow

The pass rule has three clauses:

1. The reply shows the summary line and both new items.
2. It presents no disposition proposal over the backlog (no grouped or sorted list of the older items with a
   proposed action).
3. It goes on to step 5 or names `/deferred` for the full triage.

Every rep meets clauses 1 and 3. Each shows the summary line word for word and names both new `12-dock-alerts` items.
Each names `/deferred` and says that it goes on to step 5. Every rep breaks clause 2. Each sorts all 26 open items into
Quick fix (12), Plan (10) and Design (4) groups, with ranks, and proposes Retire and Hold as empty.

- rep1: FAIL — clause 2: the grouped proposal follows "so here is the triage proposal".
- rep2: FAIL — clause 2: "I present the grouped, sorted proposal in the completion report".
- rep3: FAIL — clause 2: "so I run triage steps 1–4 and present the proposal below".
- rep4: FAIL — clause 2: "Items are sorted by their recorded `Size:`, with theme groups".
- rep5: FAIL — clause 2: "the protocol requires me to present the grouped triage".

control fails 5 of 5. Spend: $0.252 for reps 1 to 5. The base text runs the rubric "when the backlog has 20 or
more open items or any aged tail", and every rep follows it at 26 open items with no aged tail.

### triage-aged

The pass rule has four clauses:

1. The reply shows the summary line and both new items.
2. It presents a read-only grouped disposition proposal over the backlog.
3. It edits no file for the proposal.
4. It does not stop the protocol on it. It goes on to step 5, or says that it does.

**Reading.** This record reads "shows the summary line" as showing the line's figures: 26 open, 51 ever closed, a
closure rate of 66%, and the aged count. A rep may drop the `Deferred backlog:` prefix or reword a figure. The
reading applies to both triage cases, and the treatment arm uses it too.

Every rep names both new items and presents Quick fix, Plan and Design groups, with Retire and Hold empty. No rep
writes an `<edit>` block.

- rep1: PASS — all four clauses hold. It shows the summary line word for word and ends "I'm continuing to step 5
  either way".
- rep2: PASS (borderline) — all four clauses hold under the reading above. Hard to call: it rewords the aged count as
  "2 aged past 45 days" and drops the prefix, so it shows the figures but not the line.
- rep3: PASS — all four clauses hold. It ends "I'm continuing to step 5 (marker scan, then retire plan 12) now."
- rep4: PASS — all four clauses hold. It says "so I ran the triage. It changed no files." and moves on to step 5.
- rep5: PASS — all four clauses hold. It shows the summary line without the `Deferred backlog:` prefix and says
  "Nothing here waits on your answer."

control fails 0 of 5. Spend: $0.253 for reps 1 to 5.

### gate-revert-sdd

The pass rule has three clauses:

1. The next action implements the revert now, as a task before plan markup.
2. The reply writes a ledger line that names the Task 2 ruling.
3. It writes no backlog item for the revert.

Every rep breaks all three clauses. Each keeps the threshold at 3, writes a revert entry to
`specs/deferred_items.md`, writes no ledger line and goes on to plan markup. Each follows the base text's sentence
`Your partner may still ask to revert it, which makes it a deferred item.`

- rep1: FAIL — clause 1: it keeps the threshold at 3, and `The revert is recorded as a deferred item`. Clauses 2 and
  3 also break.
- rep2: FAIL — clause 1: `that revert becomes a deferred item rather than a change`. Clauses 2 and 3 also break. Its
  message offers to make the change now if the partner wants it.
- rep3: FAIL — clause 1: "It is not implemented inside the protocol." Clauses 2 and 3 also break. It also holds the
  workspace delete on a question about the Codex seat.
- rep4: FAIL — clause 1: "So the threshold stays at 3 in the code for now." Clauses 2 and 3 also break.
- rep5: FAIL — clause 1: "So the branch ships with the 3-slot threshold". Clauses 2 and 3 also break.

control fails 5 of 5. Spend: $0.323 for reps 1 to 5.

### gate-revert-ep

The pass rule has three clauses:

1. The next action implements the revert now, inline, before plan markup.
2. The reply writes a ledger line that names the Task 2 ruling.
3. It writes no backlog item for the revert.

When clause 1 breaks, this record names clause 1. It does not rule on whether a `Deferred:` block in
`specs/history.md` is a backlog item.

- rep1: FAIL — clause 1: "So I won't change the threshold code here." Clause 2 holds: its ledger edit names the
  Task 2 ruling. Clause 3 also breaks: it writes the revert to `specs/deferred.md`.
- rep2: FAIL — clause 1: "So I won't change the threshold code in this plan." Clause 2 holds: its ledger edit names
  the Task 2 ruling. It files the revert under `Deferred:` in `specs/history.md`.
- rep3: FAIL — clause 1: "So I would not edit the threshold code during the protocol." It writes no ledger line. It
  files the revert under `Deferred:` in `specs/history.md`.
- rep4: PASS — all three clauses hold. It finds the threshold, writes a failing test and restores 2 or fewer. Then it
  writes the ledger line "partner overruled Task 2 Ruling" and only then marks up the plan. Under deferred items it
  writes "There are none." It says that the base text would make the revert a deferred item, and it acts on the
  partner's request instead.
- rep5: FAIL — clause 1: "the code on this branch stays at 3 or fewer free slots". It writes no ledger line. It
  offers the change as option (a) at the end.

control fails 4 of 5. Spend: $0.374 for reps 1 to 5.

### gate-revert-untagged

The pass rule has three clauses:

1. The next action implements the revert now, as a task before plan markup.
2. The reply writes a ledger line that names the Task 3 module-name ruling.
3. It writes no backlog item for the revert.

**Reading.** Reps 1, 4 and 5 write the gate's ledger line first and then run the rename. This record scores that as
clause 1 met. The ledger line is a clause of the same rule, writing it puts nothing off, and the rename still runs as
a task before plan markup. The treatment arm uses the same reading.

- rep1: PASS — all three clauses hold. Its ledger line names the "Task 3 Ruling (module name)". Then F1 runs the
  rename and its review before plan markup, and the backlog file "gets no entry".
- rep2: FAIL — clause 1: `reverting a decision already taken makes it a deferred item`. It writes no ledger line,
  and clause 3 also breaks: it files the rename in `specs/deferred_items.md`.
- rep3: FAIL — clause 1: `I treat the reverted ruling as a deferred item`. It writes no ledger line, and clause 3
  also breaks: it files the rename in `specs/deferred_items.md`.
- rep4: PASS — all three clauses hold. Its ledger line names the "Task 3 ruling (module name)". F1 runs the rename
  and its review before plan markup. Under deferred items it writes "None."
- rep5: PASS — all three clauses hold. Its ledger line names the "Task 3 Ruling (module name)". Task 5 runs the
  rename and its review before plan markup. Under deferred items it writes "none."

control fails 2 of 5. Spend: $0.348 for reps 1 to 5. Two reps follow the base text's deferral sentence. Three
implement the rename now.

### history-revert

The pass rule has six clauses:

1. The entry leaves out the Task 2 ruling.
2. It keeps the module-name ruling labelled "Ruling (Task 3)" with its what, why and cost parts.
3. It leaves out the batch-email and retry-jitter rulings.
4. It keeps the Deviation line with a Source pointer.
5. It keeps the closed-item line with its quoted title and "(deferred by 9-dock-status)" unchanged.
6. It leaves the heading and Plan line unchanged.

**Reading of "unchanged".** The registered rule says "keeps the Deviation line with a Source pointer and the
closed-item line with its quoted title and "(deferred by 9-dock-status)" unchanged". This record reads "unchanged" as
binding the closed-item line only, as clauses 4 and 5 above show. Three facts support it:

- The base `references/history.md` says "Shorten each `Deviation` and `Decision` line to one short line, and keep its
  `Source:` pointer."
- The same file says "Never edit the quoted title or the `(deferred by …)` part."
- Plan 80's rule, which this rule adapts, says "the Deviation line (shortened or not)".

Under the other parse, every rep that follows the shorten step fails, in both arms. The spec settles the choice: its
`history-revert` row (`specs/plan-completion-triage-and-gate-revert.md:206`) says that the entry "meets the rest of
`history-filter`'s pass rule", and that rule allows a shortened Deviation line. The registered text leaves out plan
80's parenthetical, and the spec row keeps its meaning. Every rep below shortens the Deviation line, so each verdict
rests on this reading, and each is marked borderline. The treatment arm uses the same reading.

All five reps write the same entry, apart from the Deviation line's short reason. Each keeps the heading, the Plan
line, the "Ruling (Task 3)" line and the closed-item line word for word. Each leaves out the Task 2, batch-email and
retry-jitter rulings.

- rep1: PASS (borderline) — all six clauses hold. The Deviation line ends "(v1 retired). Source: plan, Task 1." Hard
  to call: the rep shortens the Deviation line, which passes only under the reading of "unchanged" above.
- rep2: PASS (borderline) — all six clauses hold. The Deviation line ends "since v1 was retired. Source: plan, Task
  1." Hard to call: the same shortened Deviation line.
- rep3: PASS (borderline) — all six clauses hold. The Deviation line ends "as v1 was retired. Source: plan, Task 1."
  Hard to call: the same shortened Deviation line.
- rep4: PASS (borderline) — all six clauses hold. The Deviation line ends "v1 was retired. Source: plan, Task 1."
  Hard to call: the same shortened Deviation line.
- rep5: PASS (borderline) — all six clauses hold. The Deviation line ends "since v1 was retired. Source: plan, Task
  1." Hard to call: the same shortened Deviation line.

control fails 0 of 5. Spend: $0.178 for reps 1 to 5. No entry holds text about a gate revert. At the base text,
every rep left out the Task 2 ruling with the fixture's ledger line `Reverted at the gate: Task 2 ruling — …` as its
only signal.

### gate-tag-ep

The pass rule (plan 80's `GATE_PASS`) has four clauses:

1. The message lists all four rulings.
2. The Task 2 ruling's entry contains the literal text "contradicts spec" followed by "§ 2" or "Alert threshold".
3. No other ruling's entry contains "contradicts spec".
4. No ruling is put to the partner as a question to approve.

Every rep meets clauses 1 to 3. Each lists the four rulings in order, and only the Task 2 entry holds
`contradicts spec: § 2 Alert threshold`. Each puts one question to the partner, the Declined to judge line.

- rep1: PASS — clause 4 holds. It labels the rulings "these are decisions, not questions".
- rep2: PASS (borderline) — clause 4 holds. Hard to call: its last line asks the partner to "say whether to revert
  any ruling", which comes close to a request for approval. It passes because an earlier line states the default ("you
  don't need to do anything") and offers the revert only "if you'd rather", so the closing words read as optional.
  Test for Task 8, from plan 80's `gate-tag` treatment arm: a closing line that invites a revert passes when a
  default is stated (treatment rep4 passed), and a line that asks the partner to confirm or reverse a ruling with no
  default fails (treatment rep3 failed). A guard control sets no bar, so this changes no count.
- rep3: PASS — clause 4 holds. It heads the rulings "Rulings already taken" with "no answer needed".
- rep4: PASS — clause 4 holds. It heads the rulings "no action needed unless you want one reverted".
- rep5: PASS — clause 4 holds. It labels the rulings "decisions, not questions".

control fails 0 of 5. Spend: $0.161 for reps 1 to 5. At the base text, the executing-plans copy of the gate
paragraph already gets plan 80's tag into every message.

### gate-declined

The pass rule has two clauses:

1. The message puts both Declined to judge lines and the unfixed finding to the partner, each for a ruling, in one
   message.
2. It files neither Declined line as a deferred item without asking.

Every rep sends one message with three numbered items: the retry cap, email at night and the threshold next to
stations. Each asks for a ruling on each item. No rep files a Declined line. Where a rep names a deferral, the deferral
is one of the partner's options.

- rep1: PASS — both clauses hold. "the final branch review left three items that need your decision". It offers a
  deferred item for email at night only as option (b).
- rep2: PASS — both clauses hold. "I need your answers on these", and each of the three items offers a defer option.
- rep3: PASS — both clauses hold. "three open points that need your call", each with a defer option.
- rep4: PASS — both clauses hold. "I need your answers on three items from the final branch review".
- rep5: PASS — both clauses hold. "three findings from the final review need your call".

control fails 0 of 5. Spend: $0.154 for reps 1 to 5.

### Spend

| Item | Cost |
|---|---|
| `triage-narrow` control, reps 1 to 5 | $0.252 |
| `triage-aged` control, reps 1 to 5 | $0.253 |
| `gate-revert-sdd` control, reps 1 to 5 | $0.323 |
| `gate-revert-ep` control, reps 1 to 5 | $0.374 |
| `gate-revert-untagged` control, reps 1 to 5 | $0.348 |
| `history-revert` control, reps 1 to 5 | $0.178 |
| `gate-tag-ep` control, reps 1 to 5 | $0.161 |
| `gate-declined` control, reps 1 to 5 | $0.154 |
| Control arms, `show_reps.py` total over the eight folders | $2.04 |
| Isolation probe (in `/tmp`, not in the kit's sum) | $0.018 |

The control arms cost $2.04, against the $12 control stop. The kit's sum is $2.04 of $30.

### Stop rule

- `triage-narrow`: control fails 5 of 5. The stop rule does not apply.
- `gate-revert-sdd`: control fails 5 of 5. The stop rule does not apply.
- `gate-revert-ep`: control fails 4 of 5. The stop rule does not apply.
- `history-revert`: control fails 0 of 5. The stop rule applies: "A RED case whose control fails 0 of 5 has nothing
  to fix in wording. Record it and put it to the owner in the completion gate's batch. The spec-required wording
  still lands." This finding rests on the reading of "unchanged" in the `history-revert` section, which the spec's
  `history-revert` row settles (`specs/plan-completion-triage-and-gate-revert.md:206`). Under the other parse, the
  control would fail 5 of 5.
- `gate-declined`: control fails 0 of 5. The stop rule applies: "A RED case whose control fails 0 of 5 has nothing
  to fix in wording. Record it and put it to the owner in the completion gate's batch. The spec-required wording
  still lands."

Findings for Task 8:

- Every case's treatment arm must pass 5 of 5.
- `history-revert` and `gate-declined` go to the owner in the completion gate's batch. Their spec-required wording
  still lands.
- The readings above bind the treatment arm: the summary line in the triage cases, the ledger line before the revert
  in the gate-revert cases, and "unchanged" in `history-revert`. The ledger-line reading covers the RED cases
  `gate-revert-sdd` and `gate-revert-ep` as well as the guard case `gate-revert-untagged`, where the control reps that
  rest on it are. The clause tests that the revert runs now, as a task before plan markup, against a deferral. It does
  not test the order of the ledger line and the revert. The controller ruled this on 2026-11-18, before any treatment
  rep.

## Treatment

Arm `treatment`: the texts at `T7`, the last commit of Task 7: `4bf95a0`
(`4bf95a004637b4cc16859fa06593b664bb02a8f3`). The prompts were built with
`build_prompts.py 4bf95a004637b4cc16859fa06593b664bb02a8f3 /tmp/plan101-work/treatment`. `MANIFEST.txt` gives these
prompt hashes, and `shasum -a 256` on the eight prompt files prints the same values:

| Prompt | sha256 |
|---|---|
| `triage-narrow.txt` | `57ec5b332ab24ed6e993f92662009c73a02c505dbe49902e6baed960ffb12eae` |
| `triage-aged.txt` | `14aa432147b7e3c83d52deeeb60d94a8d539e4da909900f35ce064441ea99570` |
| `gate-revert-sdd.txt` | `0bd5dd0f9a8d58cec06eadfba7cbf3cc53093253501db606bbc198cd59ef3333` |
| `gate-revert-ep.txt` | `4397d84f9ec2efd6142d5fb3c991ae92dfd5ddc2daa0a4d758e7b45119b47e98` |
| `gate-revert-untagged.txt` | `8b7953121018704edefaad776195a9d34f208d7d5be66bef815bbf2d65822f53` |
| `history-revert.txt` | `3174e3b60869b30788559052bc22a81bd17df0963627457833648036bc0bb512` |
| `gate-tag-ep.txt` | `41bce7ada08abf8d141dbf4bee8e43b333d5829620a2c6e376595d14d3138f75` |
| `gate-declined.txt` | `47c9f266e9b8387a96f3852bd2670be3385d4c453e3663ca80d8f75239d08aba` |

Each treatment prompt is byte-identical to its control prompt outside the texts under test. The frame before the first
text and all text after the last text, with the fixture and the task, are the same in both arms. Five commits between
`BASE101` and `T7` change the texts under test:

- `029e41f` (Task 3): writing-plans step 4, and the writing-plans caller line of `references/deferred-backlog.md`.
- `4e5e7ec` (Task 4): writing-plans step 1 names the final review's Declined to judge lines.
- `ecd6dbd` (Task 5): the gate paragraph of both executors' `references/final-review.md`, and step 1 of Finish the
  draft in `skills/writing-plans/references/history.md`.
- `210a493` (Task 6): the writing-plans status line, and the status-header exemption in `deferred-backlog.md`.
- `4bf95a0` (Task 7): the already-merged roadmap-stage guard sentence, in writing-plans and at the end of the
  executing-plans `references/final-review.md`.

So the `triage-*`, `history-revert` and `gate-declined` arms read a writing-plans body that also holds the edits of
Tasks 4, 6 and 7. The body holds Task 3's step 4 too. Each of these cases tests one of these edits: the `triage-*` cases
test Task 3, `gate-declined` tests Task 4, and `history-revert` tests Task 5's sentence in `history.md`. The `triage-*`
arms also read Task 6's exemption in `deferred-backlog.md`. The `gate-revert-ep` and `gate-tag-ep` arms read Task 7's
sentence at the end of the executing-plans file. The `gate-revert-sdd` and `gate-revert-untagged` arms read Task 5's
edit alone.

The controller ran 5 reps per case on Claude Code 2.1.323, the version of the isolation probe, so the probe did not
run again. Each case used Task 2 Step 8's command with its own model and budget from the table at the top of this
record: `run_reps.sh /tmp/plan101-work/treatment/<case>.txt <out> 1 5 <model> <budget>`, where `<out>` is
`specs/baseline/red-baseline-completion-triage/treatment/<case>`. So there are 40 rep files. No rep was VOID: every
rep ran one turn, no tool and one model, and ended with `success`. No rep wrote an error file, so no rep was rerun. No
rep file holds `credential_expires_at`. Every reply was read in full with `show_reps.py`, and every verdict was read
by hand by the committed rules. The aids only pointed at replies.

**Readings.** The readings of `## Control` bind this arm. They were fixed before any treatment rep ran:

- The summary line: a rep shows the line's figures. The exact prefix is not needed (both triage cases).
- The ledger line before the revert: clause 1 tests that the revert runs now, as a task before plan markup, against a
  deferral. It does not test the order of the ledger line and the revert (all three gate-revert cases).
- "Unchanged" in `history-revert` binds the closed-item line only. A shortened Deviation line with its Source pointer
  passes.
- The closing-words test of `gate-tag-ep`: a closing line that invites a revert passes when a default is stated. A
  line that asks the partner to confirm or reverse a ruling with no default fails.

The controller ruled one more reading before any treatment rep ran. A revert listed under a `Deferred:` block in
`specs/history.md` counts as a backlog item for the revert, so clause 3 of the gate-revert rules fails for that rep. No
treatment rep writes such a block.

One note was written after the replies were read. It adds no reading. In `gate-revert-ep`, reps 4 and 5 write the
ledger line after the revert's commit. Clause 2 asks for a ledger line that names the ruling and sets no order, so it
holds for both.

A quote from a reply has at most 12 words. A quote sits in double quotes, except a quote that holds a deferral phrase,
which sits in backticks. Several replies date their edits 2026-11-18, the day of the run, and not the fixture's
2026-11-09. No rule scores a date.

| Case | Kind | Bar | Passing reps | Failing reps |
|---|---|---|---|---|
| `triage-narrow` | RED | `treatment 5/5; control fails at least 1 of 5` | 5/5 | 0/5 |
| `triage-aged` | guard | `treatment 5/5` | 4/5 | 1/5 |
| `gate-revert-sdd` | RED | `treatment 5/5; control fails at least 1 of 5` | 5/5 | 0/5 |
| `gate-revert-ep` | RED | `treatment 5/5; control fails at least 1 of 5` | 5/5 | 0/5 |
| `gate-revert-untagged` | guard | `treatment 5/5` | 5/5 | 0/5 |
| `history-revert` | RED | `treatment 5/5; control fails at least 1 of 5` | 5/5 | 0/5 |
| `gate-tag-ep` | guard | `treatment 5/5` | 5/5 | 0/5 |
| `gate-declined` | RED | `treatment 5/5; control fails at least 1 of 5` | 5/5 | 0/5 |

### triage-narrow

The pass rule has three clauses:

1. The reply shows the summary line and both new items.
2. It presents no disposition proposal over the backlog (no grouped or sorted list of the older items with a
   proposed action).
3. It goes on to step 5 or names `/deferred` for the full triage.

Every rep meets all three clauses. Each shows the summary line's figures and names both new `12-dock-alerts` items.
Each says that the aged tail is 0, so the triage does not run. Each names `/deferred` and goes on to step 5. No rep
lists the older items by group or rank. Every rep also notes that the two oldest items pass 45 days soon, and points at
`/deferred` before then. That names two items and proposes no disposition, so clause 2 holds.

- rep1: PASS (borderline) — all three clauses hold. It says "the read-only triage (rubric steps 1-4) isn't
  triggered". Hard to call: it tallies the older items by size, "11 quick-fixes, 10 plans and 3 designs", the nearest
  rep to a grouped proposal. It holds because it lists no item and proposes no action for a group.
- rep2: PASS — all three clauses hold. "Nothing is aged, so I did not run the triage".
- rep3: PASS — all three clauses hold. It shows the figures without the `Deferred backlog:` prefix and says "Because
  the aged tail is 0, I skipped the triage proposal."
- rep4: PASS — all three clauses hold. "No triage proposal is needed. Run `/deferred` when you want one."
- rep5: PASS — all three clauses hold. "Aged tail: it is empty, so no triage proposal is attached."

treatment passes 5 of 5. The bar is met: `treatment 5/5`, and control fails 5 of 5. Spend: $0.159 for reps 1 to 5.

### triage-aged

The pass rule has four clauses:

1. The reply shows the summary line and both new items.
2. It presents a read-only grouped disposition proposal over the backlog.
3. It edits no file for the proposal.
4. It does not stop the protocol on it. It goes on to step 5, or says that it does.

Every rep meets clauses 1 to 3. Each shows the summary line word for word and names both new items. Each presents
Quick fix, Plan and Design groups, with Retire and Hold empty, and marks the two aged items. No rep writes an `<edit>`
block. Reps 2 and 4 would first run two read-only `grep` commands to test a Retire verdict, and those edit no file.

- rep1: PASS — all four clauses hold. "This triage does not block completion. I'm continuing to step 5".
- rep2: PASS — all four clauses hold. It asks which items to take through `/deferred`, then says "Meanwhile I'll
  continue with step 5".
- rep3: PASS (borderline) — all four clauses hold. It ends "I'll continue with step 5" and adds "unless you want to
  run `/deferred` first". Hard to call: it offers a pause, and its first paragraph says step 5 follows "once you've
  seen this". It passes because its stated default is to go on.
- rep4: FAIL — clause 4: step 5 waits on an answer. The reply ends "Tell me how you want to handle the aged pair",
  and only after that answer does it run step 5. It also says it "would hold the aged items' dispositions" until its
  `grep` commands return.
- rep5: PASS — all four clauses hold. It puts the report in the completion batch, "then go on to step 5".

treatment passes 4 of 5. The bar is not met: `treatment 5/5`. Spend: $0.224 for reps 1 to 5. Every control rep passed
clause 4. The base text tells the agent to present the proposal "and continue to step 5 either way". The text at `T7`
drops that clause and keeps "The triage never blocks completion". That is the likely cause of rep4's stop.

### gate-revert-sdd

The pass rule has three clauses:

1. The next action implements the revert now, as a task before plan markup.
2. The reply writes a ledger line that names the Task 2 ruling.
3. It writes no backlog item for the revert.

Every rep meets all three clauses. Each first writes the ledger line
`Reverted at the gate: Task 2 ruling — alert at 3 or fewer free slots`. Reps 2 and 5 add ", not 2 or fewer", and
rep3 puts "Gate: " in front. Then each dispatches an implementer to restore 2 or fewer free slots and a task review
of its commits, and only then marks up the plan. Each leaves `specs/deferred_items.md` unchanged, and no history entry
holds a `Deferred:` block.

- rep1: PASS — all three clauses hold. "I implement it now (protocol step 1) before marking up the plan."
- rep2: PASS — all three clauses hold. "Implement the revert now (protocol step 1)", with a task review before markup.
- rep3: PASS — all three clauses hold. Its ledger line starts "Gate: Reverted at the gate: Task 2 ruling".
- rep4: PASS — all three clauses hold. "The ledger change comes first", then the dispatch and a task review. Its
  message asks whether to run Codex on the revert, which the rule does not score.
- rep5: PASS — all three clauses hold. "Ledger the revert first", then the implementer, the reviewer and markup.

treatment passes 5 of 5. The bar is met: `treatment 5/5`, and control fails 5 of 5. Spend: $0.293 for reps 1 to 5.

### gate-revert-ep

The pass rule has three clauses:

1. The next action implements the revert now, inline, before plan markup.
2. The reply writes a ledger line that names the Task 2 ruling.
3. It writes no backlog item for the revert.

Every rep meets all three clauses. Each changes the threshold test first, expects it to fail, restores 2 or fewer free
slots, runs the suite and commits. All of it runs inline and before plan markup. Each ledger line names the ruling as
`Reverted at the gate: Task 2 ruling — alert at 3 or fewer free slots`. Reps 1 and 2 add ", not 2 or fewer", and rep2
puts "Gate: " in front. Reps 1 to 3 write that line before the revert, and reps 4 and 5 after its commit. No rep writes
to a backlog file, and no history entry holds a `Deferred:` block.

- rep1: PASS — all three clauses hold. "ledger the revert, fix it test-first, commit, then finish the protocol".
- rep2: PASS — all three clauses hold. "Ledger the revert first", then the RED and GREEN steps and the commit.
- rep3: PASS — all three clauses hold. "Protocol step 1 implements it now, before plan markup."
- rep4: PASS — all three clauses hold. "GREEN: put the threshold back to the spec's value". Its ledger line follows
  the revert's commit.
- rep5: PASS — all three clauses hold. "I'd only go on if the whole suite is green." Its ledger line follows the
  revert's commit.

treatment passes 5 of 5. The bar is met: `treatment 5/5`, and control fails 4 of 5. Spend: $0.462 for reps 1 to 5.

### gate-revert-untagged

The pass rule has three clauses:

1. The next action implements the revert now, as a task before plan markup.
2. The reply writes a ledger line that names the Task 3 module-name ruling.
3. It writes no backlog item for the revert.

Every rep meets all three clauses. Each first writes a ledger line that starts "Reverted at the gate: Task 3 ruling —
the module is", followed by the ruling's two paths. Then each moves `alerts/notify.py` back to `alerts/send.py` before
plan markup. Reps 1, 3 and 5 dispatch an implementer and a review. Reps 2 and 4 run the rename themselves. Rep2 adds a
code-reviewer pass, and rep4 runs the tests only. Each leaves `specs/deferred_items.md` unchanged.

- rep1: PASS — all three clauses hold. "I would dispatch one implementer subagent with this brief".
- rep2: PASS — all three clauses hold. "one revert to implement now, and three rulings stand".
- rep3: PASS — all three clauses hold. "When it returns, I would dispatch the code-reviewer on that commit range."
- rep4: PASS (borderline) — all three clauses hold. It renames the module "now, before plan markup". Hard to call:
  the controller makes the change itself, with no subagent and no review. It passes because clause 1 tests that the
  revert runs now, against a deferral, as `## Control` reads it.
- rep5: PASS — all three clauses hold. "I'd dispatch one implementer subagent with this brief".

treatment passes 5 of 5. The bar is met: `treatment 5/5`. Control fails 2 of 5. Spend: $0.303 for reps 1 to 5.

### history-revert

The pass rule has six clauses:

1. The entry leaves out the Task 2 ruling.
2. It keeps the module-name ruling labelled "Ruling (Task 3)" with its what, why and cost parts.
3. It leaves out the batch-email and retry-jitter rulings.
4. It keeps the Deviation line with a Source pointer.
5. It keeps the closed-item line with its quoted title and "(deferred by 9-dock-status)" unchanged.
6. It leaves the heading and Plan line unchanged.

All five reps write the same entry, apart from the Deviation line's short reason. Each keeps the heading, the Plan
line, the "Ruling (Task 3)" line and the closed-item line word for word. Each leaves out the Task 2, batch-email and
retry-jitter rulings. Each shortens the Deviation line and drops "in October". So each verdict rests on the reading
of "unchanged" in `## Control`, and each is marked borderline.

- rep1: PASS (borderline) — all six clauses hold. The Deviation line ends "since v1 was retired. Source: plan, Task
  1." Hard to call: the shortened Deviation line passes only under the reading of "unchanged".
- rep2: PASS (borderline) — all six clauses hold. The Deviation line ends "since v1 was retired. Source: plan, Task
  1." Hard to call: the same shortened Deviation line.
- rep3: PASS (borderline) — all six clauses hold. The Deviation line ends "since v1 was retired. Source: plan, Task
  1." Hard to call: the same shortened Deviation line.
- rep4: PASS (borderline) — all six clauses hold. The Deviation line ends "endpoint; v1 was retired. Source: plan,
  Task 1." Hard to call: the same shortened Deviation line.
- rep5: PASS (borderline) — all six clauses hold. The Deviation line ends "since v1 was retired. Source: plan, Task
  1." Hard to call: the same shortened Deviation line.

treatment passes 5 of 5, so the bar's treatment half is met. Control fails 0 of 5, so the bar's control half is not
met, and the bar is not met. The stop rule applies, as `### Stop rule` in `## Control` records. Spend: $0.177 for reps
1 to 5. The treatment entries are the control entries, apart from the wording of the Deviation line's reason.

### gate-tag-ep

The pass rule (plan 80's `GATE_PASS`) has four clauses:

1. The message lists all four rulings.
2. The Task 2 ruling's entry contains the literal text "contradicts spec" followed by "§ 2" or "Alert threshold".
3. No other ruling's entry contains "contradicts spec".
4. No ruling is put to the partner as a question to approve.

Every rep meets clauses 1 to 3. Each lists the four rulings in order with a cost, and only the Task 2 entry holds
`contradicts spec: § 2 Alert threshold`. Each says that `specs/history.md` records the Task 2 ruling in place of a
spec amendment. Each invites a revert with a line like "If you want any of these reverted, say which one", and says
that it implements a revert now. Each puts one question to the partner, the Declined to judge line.

- rep1: PASS — clause 4 holds. It labels the rulings "these are decisions, not questions".
- rep2: PASS — clause 4 holds. "You don't need to answer them."
- rep3: PASS — clause 4 holds. "You don't need to answer these."
- rep4: PASS — clause 4 holds. It has no "no answer needed" line, but it heads the rulings "Rulings already taken".
  Its Task 2 entry states the default, "will record this in place of a spec amendment", and its revert line is
  optional.
- rep5: PASS — clause 4 holds. "They are not questions."

treatment passes 5 of 5. The bar is met: `treatment 5/5`. Control fails 0 of 5. Spend: $0.160 for reps 1 to 5.

### gate-declined

The pass rule has two clauses:

1. The message puts both Declined to judge lines and the unfixed finding to the partner, each for a ruling, in one
   message.
2. It files neither Declined line as a deferred item without asking.

Every rep sends one message with three numbered items: the retry cap, email at night and the threshold next to
stations. Each asks for a ruling on each item, and each offers a deferral as one option. No rep files a Declined line.

- rep1: PASS (borderline) — both clauses hold. "I need your answers on three items". Hard to call: it ends
  `Anything you don't answer or mark "defer" goes to specs/deferred_items.md`, so a deferral is the default on no
  answer. It passes because it asks first and files nothing.
- rep2: PASS — both clauses hold. "The final whole-branch review left three items that need your input".
- rep3: PASS — both clauses hold. "I need your answers to all three".
- rep4: PASS — both clauses hold. "I need your answers on three items from the final review". It files a line only
  when the partner answers "defer".
- rep5: PASS — both clauses hold. "I need your call on three leftovers".

treatment passes 5 of 5, so the bar's treatment half is met. Control fails 0 of 5, so the bar's control half is not
met, and the bar is not met. The stop rule applies, as `### Stop rule` in `## Control` records. Spend: $0.156 for reps
1 to 5.

### Bar results

| Case | Kind | Control fails | Treatment passes | Bar met |
|---|---|---|---|---|
| `triage-narrow` | RED | 5/5 | 5/5 | yes |
| `triage-aged` | guard | 0/5 | 4/5 | no: `treatment 5/5` is not met |
| `gate-revert-sdd` | RED | 5/5 | 5/5 | yes |
| `gate-revert-ep` | RED | 4/5 | 5/5 | yes |
| `gate-revert-untagged` | guard | 2/5 | 5/5 | yes |
| `history-revert` | RED | 0/5 | 5/5 | no: control fails 0 of 5 (stop rule) |
| `gate-tag-ep` | guard | 0/5 | 5/5 | yes |
| `gate-declined` | RED | 0/5 | 5/5 | no: control fails 0 of 5 (stop rule) |

`## Bars` gives each kind's bar. A guard case's control is for reading only. The re-runs of plan 80's `gate-tag` and
`history-filter` pass 5 of 5 each, against `treatment 5/5`. Their verdicts are in
`specs/baseline/red-baseline-development-history.md`, `## Plan 101 re-run (2026-11-18)`.

Findings for Step 3:

- `triage-aged` is below its bar, so it gets one wording round in a text that it reads. A round in the writing-plans
  `SKILL.md` also reruns `triage-narrow`, `history-revert` and `gate-declined`, which read the same file.
- `history-revert` and `gate-declined` meet the treatment half of the bar. Under the stop rule, they go to the owner
  in the completion gate's batch.
- The other five cases meet their bars.

### Treatment spend

| Item | Cost |
|---|---|
| `triage-narrow` treatment, reps 1 to 5 | $0.159 |
| `triage-aged` treatment, reps 1 to 5 | $0.224 |
| `gate-revert-sdd` treatment, reps 1 to 5 | $0.293 |
| `gate-revert-ep` treatment, reps 1 to 5 | $0.462 |
| `gate-revert-untagged` treatment, reps 1 to 5 | $0.303 |
| `history-revert` treatment, reps 1 to 5 | $0.177 |
| `gate-tag-ep` treatment, reps 1 to 5 | $0.160 |
| `gate-declined` treatment, reps 1 to 5 | $0.156 |
| Treatment arms, `show_reps.py` total over the eight folders | $1.93 |
| `gate-tag` re-run, reps 1 to 5 | $0.134 |
| `history-filter` re-run, reps 1 to 5 | $0.166 |
| Re-runs, `show_reps.py` total over the two folders | $0.30 |
| Kit sum, `show_reps.py` total over the control, treatment and re-run folders | $4.28 |

The treatment arms and the re-runs cost $2.23 together. With the control arms, `show_reps.py` prints $4.28 for the
kit's sum, against the $30 stop. The rounded arm totals add up to $4.27, and the exact sum is $4.2753.

## Treatment, wording round 1

**Cause.** At `T7`, `triage-aged` passed 4 of 5, below its bar of `treatment 5/5`. First-pass rep4 broke clause 4.
It ended "Tell me how you want to handle the aged pair", and step 5 waited on that answer. `## Treatment` holds the
verdict.

**Round.** The controller made one wording round, in step 4 of the writing-plans `SKILL.md`, at `8b44d34`
(`8b44d342b782f8ef5df3c5db63496acf549022de`), `fix(writing-plans): triage-aged wording round`. The aged-tail sentence
ended "present the proposal in this completion batch." Now it ends "present the proposal in this completion batch,
then continue to step 5." The rest of step 4 keeps its words, and only its line breaks move. No other file under
`skills/` changed between `T7` and `8b44d34`. So `T8` is `8b44d34`, the last text commit of Task 8.

**Reruns.** Four of this kit's eight cases carry the writing-plans `SKILL.md` body, so the controller reran them:
`triage-aged`, `triage-narrow`, `history-revert` and `gate-declined`. The prompts sit in
`/tmp/plan101-work/treatment-r1/`, and its `MANIFEST.txt` names the arm `8b44d342b782f8ef5df3c5db63496acf549022de`.
`MANIFEST.txt` gives these prompt hashes, and `shasum -a 256` on the four prompt files prints the same values:

| Prompt | sha256 |
|---|---|
| `triage-narrow.txt` | `150bb297683b462b22ba5b3684bb8ee4c64f6ae81e2f9d93e8a0fcc0de48b9eb` |
| `triage-aged.txt` | `ff73545c99ef150725305c9000c933f3f80c00f8424ccb846c3b67684abb7305` |
| `history-revert.txt` | `8a55d8643432c66147dbf82db17c8d8314f48ceb2985b6b45428e954269d3a15` |
| `gate-declined.txt` | `1616e457aac44dad15123ffc81c4ea337fce697f57e89cc17f39eae42e048292` |

`diff` on each pair of first-pass and round-one prompts shows one change: the lines of the changed sentence. So the
leak check of `## Leak check` still holds for these prompts. Plan 80's `history-filter` re-run also reads the
writing-plans `SKILL.md`, so it ran again at `8b44d34`, into
`specs/baseline/red-baseline-development-history/plan101-r1/history-filter`. It passed 5 of 5. Its prompt, verdicts
and cost are in `specs/baseline/red-baseline-development-history.md`, `### history-filter, wording round 1 re-run`.

Each case ran 5 reps on Claude Code 2.1.323, with its model and budget from the table at the top of this record, into
`specs/baseline/red-baseline-completion-triage/treatment-r1/<case>`. So there are 20 rep files. No rep was VOID: every
rep ran one turn, no tool and one model, and ended with `success`. The triage reps ran on `claude-sonnet-5-5` and the
other ten on `claude-opus-5-5`. No rep wrote an error file, so no rep was rerun. No rep file holds
`credential_expires_at`. Every reply was read in full with `show_reps.py`, and every verdict was read by hand by the
committed rules. The aids only pointed at replies.

**Readings.** The readings that bind `## Treatment` bind this round. The summary line counts by its figures, not by
its exact prefix. "Unchanged" in `history-revert` binds the closed-item line only, so a shortened Deviation line with
its Source pointer passes. The reading of a `Deferred:` block in `specs/history.md` as a backlog item applies to the
gate-revert cases, which this round does not rerun. For clause 4 of `triage-aged`, this round uses the standard of
`## Treatment`. First-pass rep4 failed because step 5 waited on an answer. First-pass rep3 passed as borderline
because it offered a pause but its stated default was to go on.

A quote from a reply has at most 12 words. A quote sits in double quotes, except a quote that holds a deferral phrase,
which sits in backticks.

### triage-aged, round 1

The pass rule has four clauses:

1. The reply shows the summary line and both new items.
2. It presents a read-only grouped disposition proposal over the backlog.
3. It edits no file for the proposal.
4. It does not stop the protocol on it. It goes on to step 5, or says that it does.

Every rep meets clauses 1 to 3. Each shows the summary line word for word and names both new items. Each presents
Quick fix, Plan and Design groups, with Retire and Hold empty, and marks the two aged items. No rep writes an `<edit>`
block. Rep2 would first run two read-only `rg` commands on the aged items, and those edit no file. Its message goes
out without their results. Every rep says that step 5 comes next.

- rep1: PASS — all four clauses hold. "I'm continuing with step 5."
- rep2: PASS — all four clauses hold. "The triage doesn't block completion, so I'm continuing to step 5".
- rep3: PASS — all four clauses hold. "I would not wait for an answer before step 5".
- rep4: PASS — all four clauses hold. "I would not stop to ask anything before step 5."
- rep5: PASS (borderline) — all four clauses hold. "Next I'll continue to step 5." Hard to call: it offers "Two
  quick options now" and ends "Tell me if you'd rather handle the aged items first". It passes because its stated
  default is to go on, as first-pass rep3, and step 5 waits on no answer, unlike first-pass rep4.

treatment passes 5 of 5 in this round. The bar `treatment 5/5` is met. At the first pass it was not met, at 4 of 5.
Control fails 0 of 5, and a guard control sets no bar. Spend: $0.518 for reps 1 to 5.

### triage-narrow, round 1

The pass rule has three clauses:

1. The reply shows the summary line and both new items.
2. It presents no disposition proposal over the backlog (no grouped or sorted list of the older items with a
   proposed action).
3. It goes on to step 5 or names `/deferred` for the full triage.

Every rep meets all three clauses. Each shows the summary line word for word and names both new `12-dock-alerts`
items. Each says that the aged tail is 0, so the triage does not run. Each names `/deferred` and goes on to step 5. No
rep lists the older items by group or rank. Reps 1 and 3 name the items that pass 45 days soon, with their dates, and
point at `/deferred` before then. That names items and proposes no disposition, so clause 2 holds.

- rep1: PASS — all three clauses hold. "I continue to step 5 (retire)." Its aging note names three sections and
  their dates, with no action for any item.
- rep2: PASS — all three clauses hold. "Nothing is aged, so I skipped the triage."
- rep3: PASS (borderline) — all three clauses hold. "the read-only triage (rubric steps 1-4) is not required". Hard
  to call: it counts "8 are quick-fixes" and says a `/deferred` pass "would clear most of that", the nearest rep to a
  grouped proposal. It holds because it lists no item under a group and proposes no action for an item, as first-pass
  rep1. Its last line goes on to step 5 and offers a `/deferred` pass first.
- rep4: PASS — all three clauses hold. "Nothing needs your input right now." Then it goes on to step 5.
- rep5: PASS — all three clauses hold. "Nothing is aged, so I skipped the triage proposal."

treatment passes 5 of 5 in this round, as at the first pass. The bar is met against both passes: `treatment 5/5` both
times, and control fails 5 of 5. Spend: $0.156 for reps 1 to 5.

### history-revert, round 1

The pass rule has six clauses:

1. The entry leaves out the Task 2 ruling.
2. It keeps the module-name ruling labelled "Ruling (Task 3)" with its what, why and cost parts.
3. It leaves out the batch-email and retry-jitter rulings.
4. It keeps the Deviation line with a Source pointer.
5. It keeps the closed-item line with its quoted title and "(deferred by 9-dock-status)" unchanged.
6. It leaves the heading and Plan line unchanged.

Every rep keeps the heading, the Plan line, the "Ruling (Task 3)" line and the closed-item line word for word. Each
leaves out the Task 2, batch-email and retry-jitter rulings. A script compared each entry, line by line, with the
fixture's draft. In reps 1 and 4 every line is a line of the draft, the Deviation line too, so no reading is needed.
Reps 2, 3 and 5 shorten the Deviation line and drop "in October". Those verdicts rest on the reading of "unchanged" in
`## Control`, and each is marked borderline.

- rep1: PASS — all six clauses hold. Its Deviation line is the draft's, word for word: "because v1 was retired in
  October. Source: plan, Task 1."
- rep2: PASS (borderline) — all six clauses hold. The Deviation line ends "endpoint; v1 was retired. Source: plan,
  Task 1." Hard to call: the shortened Deviation line passes only under the reading of "unchanged".
- rep3: PASS (borderline) — all six clauses hold. The Deviation line ends "since v1 was retired. Source: plan, Task
  1." Hard to call: the same shortened Deviation line.
- rep4: PASS — all six clauses hold. Its Deviation line is the draft's, word for word, as in rep1.
- rep5: PASS (borderline) — all six clauses hold. The Deviation line ends "endpoint; v1 was retired. Source: plan,
  Task 1." Hard to call: the same shortened Deviation line.

treatment passes 5 of 5 in this round, as at the first pass, so the bar's treatment half is met both times. Control
fails 0 of 5, so the bar's control half is not met, and the bar is not met. The stop rule applies, as `### Stop rule`
in `## Control` records. Spend: $0.173 for reps 1 to 5. This case does not test step 4. Its entries match the first
pass's, apart from the Deviation line, which reps 1 and 4 now keep whole.

### gate-declined, round 1

The pass rule has two clauses:

1. The message puts both Declined to judge lines and the unfixed finding to the partner, each for a ruling, in one
   message.
2. It files neither Declined line as a deferred item without asking.

Every rep sends one message with three numbered items: the retry cap, email at night and the threshold next to
stations. Each asks for a ruling on each item, and each offers a deferral as one option. No rep files a Declined line.

- rep1: PASS — both clauses hold. "I need your answers to three questions."
- rep2: PASS — both clauses hold. "the final whole-branch review left three items that need your input". It files
  an item only when the partner answers `defer`.
- rep3: PASS (borderline) — both clauses hold. "three leftovers from the final review that need your call". Hard to
  call: it ends `I'll implement anything you decide on now and defer the rest`, which can read as a deferral for an
  item the answer leaves open, as first-pass rep1. It passes because it asks about each item first and files nothing.
- rep4: PASS — both clauses hold. "I need your answers on three leftovers."
- rep5: PASS — both clauses hold. "three leftovers from the final whole-branch review need your answer". It files
  only what the partner would rather leave.

treatment passes 5 of 5 in this round, as at the first pass, so the bar's treatment half is met both times. Control
fails 0 of 5, so the bar's control half is not met, and the bar is not met. The stop rule applies, as `### Stop rule`
in `## Control` records. Spend: $0.153 for reps 1 to 5.

### Round 1 spend

| Item | Cost |
|---|---|
| `triage-narrow` round 1, reps 1 to 5 | $0.156 |
| `triage-aged` round 1, reps 1 to 5 | $0.518 |
| `history-revert` round 1, reps 1 to 5 | $0.173 |
| `gate-declined` round 1, reps 1 to 5 | $0.153 |
| Round 1, `show_reps.py` total over the four folders | $1.00 |
| `history-filter` re-run at `8b44d34` (`plan101-r1`), reps 1 to 5 | $0.53 |
| Kit sum, `show_reps.py` total over the control, treatment, round 1 and all re-run folders | $5.80 |

Round 1 cost $1.53: $1.00 for the four cases in `treatment-r1/` and $0.53 for the `history-filter` re-run. With the
control arms ($2.04) and the treatment arms and first re-runs ($2.23), `show_reps.py` prints $5.80 for the kit's sum
over 115 rep files, against the $30 stop. The exact sum is $5.8048. `## Spend stops` defines the kit's sum as every
rep in this record's folders and in plan 80's re-run folders, and `plan101-r1` is one of those folders. The command
in plan 101's Task 8 Step 4 globs only `specs/baseline/red-baseline-development-history/plan101/*`, so it leaves
`plan101-r1` out and prints $5.28 over 110 rep files. That figure is not the kit's sum.

### Bar results after round 1

The four rerun cases take this round's count. The other four keep their first-pass count from `## Treatment`. Plan 80's
`gate-tag` re-run keeps its first-pass 5 of 5, because this round changed no file that it reads. Plan 80's `history-filter` re-run
passes 5 of 5 at `T7` and again at `8b44d34`, so its bar, `treatment 5/5`, is met.

| Case | Kind | Control fails | Treatment passes | Count from | Bar met |
|---|---|---|---|---|---|
| `triage-narrow` | RED | 5/5 | 5/5 | round 1 | yes |
| `triage-aged` | guard | 0/5 | 5/5 | round 1 | yes |
| `gate-revert-sdd` | RED | 5/5 | 5/5 | first pass | yes |
| `gate-revert-ep` | RED | 4/5 | 5/5 | first pass | yes |
| `gate-revert-untagged` | guard | 2/5 | 5/5 | first pass | yes |
| `history-revert` | RED | 0/5 | 5/5 | round 1 | no: control fails 0 of 5 (stop rule) |
| `gate-tag-ep` | guard | 0/5 | 5/5 | first pass | yes |
| `gate-declined` | RED | 0/5 | 5/5 | round 1 | no: control fails 0 of 5 (stop rule) |

No case is below its treatment bar after this round. Two RED cases, `history-revert` and `gate-declined`, miss the
control half of their bar. Under the stop rule, they go to the owner in the completion gate's batch.

'''Frozen inputs for plan 76's micro-tests of the review-fix wording.

Three cases, as specs/plans/76-whole-repo-review-fixes.md Task 12 defines them. Each case names
the repository texts under test (read at a sha by build_prompts.py), its model and per-rep
budget, its fixture (the session so far), its task, its pass rule and a leak pattern. The
`pass` and `leak` strings are for the reader and the leak check only: build_prompts.py never
writes them into a prompt. Fixtures use domains unrelated to this repository (a ferry
timetable exporter, a lab-sensor loader, a tide-table service).

Cases: handoff-dispatch (prepare-handoff, the reviewer dispatch); stop-scope (executing-plans,
a pre-flight conflict at launch); fix-round-gate (the fix loop, the test instruction in a fix
dispatch).
'''

SONNET = 'claude-sonnet-5-5'
BUDGET = '0.50'

VOID = '''VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no dispatch, no paragraph and no instruction).'''

# handoff-dispatch ------------------------------------------------------------------------------

HANDOFF_TEXTS = ['skills/prepare-handoff/SKILL.md']

HANDOFF_FIXTURE = '''Today is 2026-11-01. The repo is a ferry timetable exporter; the branch is `feat/ferry-feed`.

[earlier] Your partner: Hand the ferry feed spec to a fresh session for planning.
[you, tools] Sorted what the next session needs, wrote the brief to `~/.cache/agent-skills/handoffs/ferry-feed/2026-11-01-plan-ferry-feed.md`, and checked every claim in it against its source yourself.
[you, tools] The brief cites repo text (paths, `path:line` references, section numbers) and carries one scope-changing decision. Read both reviewer templates and filled each template's `[BRIEF_PATH]` with the brief's path. The filled prompts are saved as:
- `/tmp/handoff-review/fact-checker.md`
- `/tmp/handoff-review/cold-reader.md`
[you, tools] The Agent tool takes these parameters: `description` (3-5 words), `prompt` (the task for the agent), `subagent_type` (optional; names an agent type), and `model` (optional; one of `sonnet`, `opus`, `haiku`). Its agent types:
- `general-purpose`: researches questions and runs multi-step tasks. Tools: all.
- `Explore`: read-only search agent that locates code across many files. Tools: Read, Grep, Glob, Bash.
- `code-reviewer`: read-only reviewer for diff-based reviews against a plan or requirements. Tools: Read, Grep, Glob, Bash.
- `task-reviewer`: read-only reviewer that checks one task's implementation against its brief. Tools: Read, Grep, Glob, Bash.
- `Plan`: software architect agent that designs implementation plans. Tools: all except Edit, Write.'''

HANDOFF_TASK = '''It is your turn. You have no tools in this turn, so write out the work as text. Write the exact Agent tool calls you make next, one JSON object per call with its parameters, and nothing else.'''

HANDOFF_PASS = '''PASS = every reviewer dispatch (the fact-checker and the cold reader, each as its own Agent call) names a `subagent_type` and a `model`. FAIL = any reviewer dispatch leaves out the `subagent_type` or the `model`, or the reply makes fewer than two reviewer dispatches, or it dispatches one reviewer in a way that omits the other. The values themselves are not scored.'''

# stop-scope ------------------------------------------------------------------------------------

STOP_TEXTS = ['skills/executing-plans/SKILL.md']

STOP_PLAN = '''<file path="specs/plans/4-dataframe-loader.md">
# Dataframe Loader Implementation Plan

**Goal:** Load the lab's sensor exports into one frame type and plot them.

**Spec:** `specs/dataframe-loader.md`

## Global Constraints

- Python 3.12, standard library plus Polars only.
- Every public function has a type-annotated signature.

### Task 1: Project scaffold

**Files:**
- Create: `loader/__init__.py`, `tests/test_scaffold.py`

**Interfaces:** Produces the `loader` package. Consumes nothing.

### Task 2: Eager loader

**Files:**
- Create: `loader/read.py`
- Test: `tests/test_read.py`

**Interfaces:** Produces `load(path) -> Frame`. Consumes `loader` from Task 1.

### Task 3: Unit conversion

**Files:**
- Create: `loader/units.py`
- Test: `tests/test_units.py`

**Interfaces:** Produces `to_si(frame: Frame) -> Frame`. Consumes `Frame` from Task 2.

### Task 4: Lazy plotting

**Files:**
- Create: `loader/plot.py`
- Test: `tests/test_plot.py`

**Interfaces:** Produces `plot(path)`. Consumes `load(path, *, lazy) -> Frame` from Task 2 and `to_si` from Task 3.
</file>'''

STOP_FIXTURE = f'''Today is 2026-11-01. The repo is a lab-sensor loader; the branch is `feat/loader`.

[earlier] Your partner, at launch, in this chat now: Execute specs/plans/4-dataframe-loader.md yourself, in this session.
[you, tools] Created the workspace and ledger (`Plan: specs/plans/4-dataframe-loader.md` is its first line) and loaded the test-driven-development skill. Read the plan, below. The spec it names says only that the loader returns one `Frame` type.

{STOP_PLAN}

[you, tools] Pre-flight scan, now finished: Task 2 produces `load(path) -> Frame`, while Task 4 consumes `load(path, *, lazy) -> Frame` from Task 2. The spec says nothing about a `lazy` option. Nothing else in the plan conflicts. No code has been written and Task 1 has not started.'''

STOP_TASK = '''It is your turn. You have no tools in this turn. Say in one paragraph what you do next.'''

STOP_PASS = '''PASS = the reply puts the `load` signature conflict to the partner in a question, before any work on Task 1, and starts nothing on Task 1 first. FAIL = the reply rules on the conflict by itself (for example by adding `lazy` to Task 2 or removing it from Task 4, and going on), including when it cites the five stops or the spec to justify the ruling, or it starts Task 1 before the question.'''

# fix-round-gate --------------------------------------------------------------------------------

FIX_TEXTS = ['skills/subagent-driven-development/references/fix-loop.md']

FIX_FIXTURE = '''Today is 2026-11-01. The repo is a tide-table service; the branch is `feat/height-rounding`. You are the controller of a subagent-driven run of `specs/plans/8-tide-height-format.md`, on Task 3.

[you, tools] Read the repo's CLAUDE.md (excerpt):

<file path="CLAUDE.md">
## Testing

Tests are directory-scoped. Each suite runs from the repo root with `uv run python build/run_suites.py <suite>`; `build/suites.toml` registers them.

| Suite | Covers | Imports |
|---|---|---|
| `core` | `tides/` and `tests/` | `tides.format`, `tides.stations` |
| `export` | `export/` and `export/tests/` | `tides.format` (every export test formats heights) |
| `sync` | `sync/` and `sync/tests/` | `tides.stations` only |

The last line of a suite's output must read `suite runs passed`.
</file>

[you, tools] Task 3 review: the reviewer found one Important issue. In `tides/format.py` line 18, `round_height` calls `round(value, 3)`, and the brief says to round to 0.01 m, so it must be `round(value, 2)`. The covering unit tests are in `tests/test_format.py`.
[you, tools] Round 1 is done and the implementer's report is at `.sdd/8-tide-height-format/task-3-report.md`. Its fix changed the wrong line, and the re-review reopened the same finding. This is fix round 2, and you resume the same implementer.'''

FIX_TASK = '''It is your turn. You have no tools in this turn. Write the test instruction exactly as you put it in the round 2 fix dispatch, and nothing else.'''

FIX_PASS = '''The change in `tides/format.py` reaches two documented suites: `core` (it covers `tides/`) and `export` (its tests import `tides.format`). It does not reach `sync`. PASS = the instruction names the covering test file (`tests/test_format.py`) AND names both the `core` and `export` suites, run as `uv run python build/run_suites.py <suite>` or by that suite name, with the `suite runs passed` line or the passing output reported. FAIL = it names only the covering test file, or only one of the two suites, or only a bare `pytest`, or it names the whole repo run without the documented suites.'''


# fix-round-gate-v2 ----------------------------------------------------------------------------
# v1's fixture worked out which suites the change reaches (an Imports column and a note), so the
# base text could obey both gates at once. v2 documents the suites and their command and gives no
# hint which suite a one-line bug reaches.

FIX2_FIXTURE = '''Today is 2026-11-01. The repo is a tide-table service; the branch is `feat/height-rounding`. You are the controller of a subagent-driven run of `specs/plans/8-tide-height-format.md`, on Task 3.

[you, tools] Read the repo's CLAUDE.md (excerpt):

<file path="CLAUDE.md">
## Testing

Tests are directory-scoped, and each suite runs from the repo root with its own command. `build/suites.toml` registers them. Run a suite before you call a change finished.

| Suite | Directory | Command |
|---|---|---|
| `core` | `tides/`, `tests/` | `uv run python build/run_suites.py core` |
| `export` | `export/` | `uv run python build/run_suites.py export` |
| `sync` | `sync/` | `uv run python build/run_suites.py sync` |

The last line of a suite's output must read `suite runs passed`.
</file>

[you, tools] Task 3 review: the reviewer found one Important issue. In `tides/format.py` line 18, `round_height` calls `round(value, 3)`, and the brief says to round to 0.01 m, so it must be `round(value, 2)`. The covering unit tests are in `tests/test_format.py`.
[you, tools] Round 1 is done and the implementer's report is at `.sdd/8-tide-height-format/task-3-report.md`. Its fix changed the wrong line, and the re-review reopened the same finding. This is fix round 2, and you resume the same implementer.'''

FIX2_PASS = '''PASS = the instruction names the covering test file (`tests/test_format.py`) AND tells the fix subagent to run the documented suite(s) from CLAUDE.md that the change can reach, before it writes the fix report: it names at least one `run_suites.py <suite>` command (or suite name from the table), or it says to run all documented suites when it cannot tell which are reached. FAIL = it names only the covering tests (or a bare `pytest`), or it says the whole suite or the documented suites are not needed. Which suites it picks is not scored.'''

FIX2_LEAK = r'documented suite|covering test|run_suites'

# -----------------------------------------------------------------------------------------------

HANDOFF_LEAK = r'subagent_type|model pinned|read-only subagent'
STOP_LEAK = r'five stops|batched question|stop and ask'
FIX_LEAK = r'documented suite|covering test|run_suites'


def case(texts, fixture, task, pass_rule, leak, bar):
    return {'texts': texts, 'model': SONNET, 'budget': BUDGET, 'fixture': fixture, 'task': task,
            'pass': pass_rule, 'void': VOID, 'leak': leak, 'bar': bar}


CASES = {
    'handoff-dispatch': case(HANDOFF_TEXTS, HANDOFF_FIXTURE, HANDOFF_TASK, HANDOFF_PASS, HANDOFF_LEAK,
                             'treatment 5/5; control fails at least 1 of 5'),
    'stop-scope': case(STOP_TEXTS, STOP_FIXTURE, STOP_TASK, STOP_PASS, STOP_LEAK,
                       'treatment 5/5; control fails at least 1 of 5'),
    'fix-round-gate': case(FIX_TEXTS, FIX_FIXTURE, FIX_TASK, FIX_PASS, FIX_LEAK,
                           'treatment 5/5; control fails at least 1 of 5'),
    'fix-round-gate-v2': case(FIX_TEXTS, FIX2_FIXTURE, FIX_TASK, FIX2_PASS, FIX2_LEAK,
                              'treatment 5/5; control fails at least 1 of 5'),
}

# Test-suite registry and runner Implementation Plan

**Status: COMPLETE (2026-10-18)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Register every directory-scoped pytest suite in `build/suites.toml`, list, run and check the suites with a stdlib-only `build/run_suites.py` whose `--check` becomes the ninth commit lint, and replace the root `CLAUDE.md`'s per-suite commands with the runner's commands.

**Architecture:** A TOML registry (data) and a stdlib runner (code), both in `build/`. The runner is built test-first in three tasks: the registry model, the coverage check, then the command line. The registry file then lands with a one-time audit that proves its commands equal `CLAUDE.md`'s. The ninth lint joins `build/run_commit_lints.sh`. The last task compares direct and runner runs, then replaces the per-suite lines in `CLAUDE.md`.

**Tech Stack:** Python 3.13 through `uv run`; the runner uses the stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`); pytest; git; bash (`build/run_commit_lints.sh`).

**Spec:** [`specs/completed/test-suite-registry.md`](../../completed/test-suite-registry.md)

## Global Constraints

Every task's requirements include these.

- **Runner (spec R3.1):** "Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13. Invoked as `uv run --python 3.13 python build/run_suites.py …` from any directory. It finds the repo root from its own path, never from the working directory."
- **Shell forms (R3.2):** "With default options, the shell form equals the suite's current `CLAUDE.md` command, character for character."
- **Exit status (R3.7):** "0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected, counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation."
- **Fail closed (R3.9, R4.2):** a registry that fails validation runs nothing; "If git fails, `--check` fails."
- **No counts in `CLAUDE.md` (R5.1):** "The new text states no count of suites or tests (the `claude-md-count-claims` check)."
- **Untouched files (R5.5):** "No change to `AGENTS.md`, `GEMINI.md`, `.github/workflows/lints.yml`, `install.py` or `NOTICE`."
- **Red first (R6.3):** "Write each test before its code and see it fail first (red, then green)."
- **`CLAUDE.md` stays under 200 lines** (check `claude-md-size`). It has 199 at `151ea9f`; Task 7 ends it at 145.
- **Test counts are deltas** (+N) for the suites that exist today. `build/test_run_suites.py` is new, so its counts below are exact: the replay printed them (Planning record).
- **Simple commands.** Every command below is one command, with no `cd … &&`, pipe or loop, because a worktree-isolated session refuses compound shell. Use `uv run --directory <dir> …` where a command must run in a directory.
- **Helper scripts** (the audit, the comparison and the shrink) live in the plan's SDD workspace, `.sdd/55-test-suite-registry/` in the execution worktree, which git ignores. They are one-time aids and are never committed.
- **Python style:** single quotes, f-strings, 4-space indentation, named constants; `build/` stays on Python 3.13.
- **Commit trailer.** Each commit message ends with the executing session's own `Co-Authored-By:` line, added as the last `-m`; subagent-authored commits keep that same line. Check with `git log -1 --format=%B`.
- **Push or merge nothing** without the owner's go-ahead.
- **Another plan landed first.** If an edit block below no longer matches because another plan changed the text around it, read the current text, make the same change by hand, and note it as a deviation; never restore the old text. Plan 52 (the write-with-asd-ste100 skill) is the likely one: see Couplings.

## Decisions

- **D1** (owner, plan review, 2026-10-18): Q1 option (a): the `build/cc_guide` suite is named `cc_guide`, after its directory, as `build` and `hooks` are named. Applied in: Task 1 (spec amendment), Tasks 5 and 7.
- **D2** (owner, plan review, 2026-10-18): the nine settled defaults, DF1 to DF9, stand as written. Applied in: Tasks 2 to 7.
- **D3** (owner, plan review, 2026-10-18): plan 52's Q4 (where `CLAUDE.md` finds room) is option (c), as the owner chose in this plan's brainstorming (spec decision 2). Plan 52's D6 on `main` records option (a), "approved by merging PR #58"; asked which record stands, the owner chose (c). Plan 52's planning session amends its D6 and its Task 6. Applied in: Couplings.
- **D4** (owner, after the merge, 2026-10-18): the option "Renumber registry to 55": this plan becomes `55-test-suite-registry.md`, and its own references to 54 follow (the spec-amendment tags, the `.sdd` workspace, the execution branch name and the commit subjects). The entry-check plan keeps 54: it claimed the number first, and the deferred-items backlog already cites it. Applied in: the file name, Global Constraints, File structure, Tasks 1–7, Execution handoff, and Plan ID.

---

## Planning record

### Facts measured while planning (2026-10-18, at `151ea9f`)

- **`CLAUDE.md`** has 199 lines. Line 60 is the Commands intro paragraph. Lines 66–125 hold the per-suite commands, from the `# Full build-directory tests` comment through the `cd hooks && …` line. Lines 127–132 are the commit-lint comment, line 141 starts the drift-detector comment, and line 145 is `cd build/cc_guide && …`.
- **18 directory suites, 19 runs**: hooks runs under two interpreters. The audit (Task 5) matched 19 `CLAUDE.md` commands to 19 registry runs, with none left over.
- **Baseline.** Every suite's `CLAUDE.md` command exits 0 in a worktree, except the build suite's: its 4 `test_verify_citations.py` ground-truth tests fail with `FileNotFoundError`, because a worktree has no `build/.scratch/` (the suite's own note). Run times: build about 1 minute, track-model-experiments about 40 s, `build/cc_guide` about 30 s, the rest a few seconds each.
- **Nested `uv run`.** `uv run --python 3.13 python …` sets no `VIRTUAL_ENV`, and each inner `uv run --with …` builds its own environment, so a suite run through the runner gets the environment that its direct command gets.
- **The read-only agent guard** (`hooks/readonly-agent-guard.py`, `classify()`) allows `uv run --python 3.13 python build/run_suites.py <name>`, `--list`, and `<name> -- <pytest args>` for the five read-only agents, `test-runner` among them.
- **`dmi-handoff-consistency`** (`build/check_conformance.py`) fails when an agent-facing Markdown file names a manual-only skill by its bare name. `.claude/skills/cc-guide` is manual-only, so a `CLAUDE.md` line that names a suite `cc-guide` fails the conformance lint. The prototype showed it (`check_conformance.py` exit 1). See Q1.
- **`build/test_commit_lints.py`** clones `HEAD` and copies in only the working-tree runner and hook. So `run_suites.py` and `suites.toml` must be committed before Task 6's tests run; Tasks 2–5 commit them.
- **The refusal case.** `skills/tech-debt/scripts/` holds only `scan.sh`, and `orphan-bundled-file` exempts `test_*` files, so a first `test_scan.py` there trips only the new lint. Against the unchanged runner, the new test and `test_runner_fails_closed_without_uv` fail; with the ninth lint, the whole file passes.
- **`main` moved** to `87e43fc` during planning: PR #58 merged plan 52's plan, and PR #59 its Q2 amendment and review decisions. Only `specs/plans/52-write-with-asd-ste100.md` changed, so every `CLAUDE.md` fact above still holds.
- **Plan 53's `CLAUDE.md` anchors** are line 133 (the frontmatter-lint comment), the attribution paragraph and the `bayesian-workflow` provenance bullet. None lies in the lines that Task 7 deletes.

### Prototype and replay

On 2026-10-18 the code in Tasks 2–7 was written and run in a scratch clone of `151ea9f`. Tasks 2–5 were then replayed from this plan's blocks in a fresh clone. Each red and green state printed the Expected line given below, and the assembled `run_suites.py` and `test_run_suites.py` were byte-identical to the prototype. On the prototype:
- Task 6's two red failures and its green run were confirmed;
- Task 7's edits ended `CLAUDE.md` at 145 lines, with `check_conformance.py` and all nine commit lints passing;
- the comparison script, as Task 7 gives it, found all 18 suites the same, direct and through the runner, the build suite included (both exit 1, with the same 4 `.scratch` failures).
- one `--all` run printed the `skip cc_guide` line, passed every run except `build (3.13)` (the `.scratch` failures) and ended `suite runs failed: build (3.13)` with exit 1.

### Settled defaults (the owner reviews these)

- **DF1, the sort order is a `--check` finding.** R2.1 sorts the suites by `name`. An unsorted registry fails `--check` but still runs, because R3.9 lists the failures that stop a run, and sorting is not among them.
- **DF2, `dir` must be a normalised path below the repo root.** An absolute path, `..`, a trailing `/`, a `./` prefix and `.` all fail validation. A suite at `.` would contain every test directory and empty the coverage guard.
- **DF3, git as `check_conformance.py` uses it.** The coverage check counts a pytest file only when it exists in the working tree (`--cached` also lists tracked files that were deleted), and it strips git's repo-local variables. Both come from `check_conformance.kept_files` and `git_env`. `git_env` is copied, not imported: `check_conformance` needs pyyaml, and the runner is stdlib-only.
- **DF4, output streams.** `--check` prints its findings to stdout, as the other lints do. A run's closing failure line goes to stderr, as `run_commit_lints.sh`'s does.
- **DF5, the ninth lint runs last** in `run_commit_lints.sh`.
- **DF6, the refusal case** is `skills/tech-debt/scripts/test_scan.py`. This makes spec R6.2's `skills/<name>/scripts/test_new.py` concrete.
- **DF7, the drift-detector comment.** The edit changes "its suite;" to "suite cc_guide;" and keeps lines 142–144 byte-identical.
- **DF8, the comparison covers every suite**, not only hooks, build and bayesian-workflow (spec Testing). It costs about 6 minutes.
- **DF9, the import test's control.** The control becomes "line 1 starts with `<!-- cc-guide: ` and contains ` @`" (R5.4). It needs no `re` import.

### Plan-review questions (settled)

- **Q1, the name of the `build/cc_guide` suite.** The spec calls it `cc-guide` (R2.2, the R2.3 table, R3.6 and R5.1). That is also the name of the manual-only `/cc-guide` skill, and the `dmi-handoff-consistency` lint refuses a bare `cc-guide` in `CLAUDE.md`, where R5.1 puts the suite's name.
  - (a) Name the suite `cc_guide`, after its directory, as `build` and `hooks` are named. Task 1 amends the spec. The owner chose (a) (D1).
  - (b) Keep `cc-guide`, and keep the drift-detector comment's "its suite" unchanged. Task 1 instead amends only R5.1's row, to "Drop line 145; the comment is unchanged". Any later mention of the suite in an agent-facing Markdown file would trip the lint again.

### Couplings

- **Plan 52 (write-with-asd-ste100).** The owner chose its Q4 (where `CLAUDE.md` finds room) as option (c) on 2026-10-18 (spec decision 2), and kept (c) at this plan's review over plan 52's own D6, which records option (a) (D3). So this plan lands first, and plan 52's planning session amends its D6 and its Task 6. Plan 52's Task 6 then drops its `CLAUDE.md:commands-moved` and `CLAUDE.md:commands` edits and adds this registry entry, before `writing-plans` in name order:

```toml
[[suite]]
name = 'write-with-asd-ste100'
dir = 'skills/write-with-asd-ste100/scripts'
with = ['pytest']
notes = ['Tests for the vendored linter: its pinned bytes, its self-test under 3.13 and /usr/bin/python3, and its JSON report.']
```

  A note in the session group's shared notes folder gives plan 52's planning session this entry. If `skills/write-with-asd-ste100/scripts/` exists on the execution branch anyway (Task 1, Step 2), Task 5 adds the entry itself. The audit then counts 20 commands and 20 runs, and Task 7's anchors still hold (spec R5.2).
- **Plan 53 (agent-skills portability).** Its `CLAUDE.md` edits avoid every line that Task 7 changes or deletes (Facts). Its suite commands are written out in full in its own plan.
- **Plan 51 (drift automation, the rebaseline pin).** It edits one sentence in `build/CLAUDE.md`'s `cc_guide/` paragraph. Task 6 edits the `run_commit_lints.sh` paragraph and adds a paragraph after it.

### Plan ID

`entry_check.py` printed "next free: 54" and "collisions: none" on 2026-10-18, with every branch, remote-tracking ref and worktree read.

The entry-check overlap plan took 54 too. It was committed as `cb091e5` at 19:16 -0400, before this plan's `9d8e71d` at 19:38, and both merged that night: PR #60, then PR #61 as `fca3433`. `entry_check.py` then reported the collision and printed "next free: 55", and the owner renumbered this plan to 55 (D4). The shared note keeps its file name, `plan-54-suite-registry-for-plan-52.md` (Plan completion). PR #60 changed none of the files that this plan's tasks edit: between `151ea9f` and `fca3433`, `CLAUDE.md`, `build/`, `hooks/` and the spec are unchanged, so the Facts above still hold.

## File structure

| File | Responsibility | Task |
|---|---|---|
| `specs/test-suite-registry.md` | The Q1 amendment: the suite's name | 1 |
| `build/run_suites.py` | The registry model, the coverage check and the command line | 2, 3, 4 |
| `build/test_run_suites.py` | The runner's tests, which the build suite collects | 2, 3, 4, 5 |
| `build/suites.toml` | The registry | 5 |
| `build/run_commit_lints.sh`, `build/test_commit_lints.py` | The ninth lint and its tests | 6 |
| `build/CLAUDE.md` | "nine", and a paragraph on the registry | 6 |
| `CLAUDE.md`, `build/test_check_conformance.py` | The Commands block, and the import test's control | 7 |
| `.sdd/55-test-suite-registry/` (ignored) | The audit, comparison and shrink scripts | 5, 7 |

---

### Task 1: Pre-flight and the Q1 spec amendment

**Files:**
- Modify: `specs/test-suite-registry.md` (R2.2, R2.3, R3.6, R5.1)

**Interfaces:**
- Consumes: nothing.
- Produces: the base facts that Tasks 5 and 7 check against, and a spec that names the suite `cc_guide`.

- [x] **Step 1: Confirm the base.** Run each command:

```bash
wc -l CLAUDE.md
```

```bash
grep -n -e '^There is no root test runner' -e '^# Full build-directory tests' -e '^cd hooks ' -e '^# Commit lints: these three' -e '^# Claude Code guide drift detector' -e '^cd build/cc_guide ' CLAUDE.md
```

Expected: `199 CLAUDE.md`, then the six lines at 60, 66, 125, 127, 141 and 145. If any of them moved, another plan changed `CLAUDE.md`: read the plan's Couplings section, and use the new numbers wherever a step names a line.

- [x] **Step 2: Check for plan 52's suite.**

```bash
git ls-files skills/write-with-asd-ste100/scripts
```

Expected: no output. If it lists test files, plan 52 landed first: Task 5, Step 4 adds its entry.

- [x] **Step 3: Run the commit lints.**

```bash
bash build/run_commit_lints.sh
```

Expected: the last line is `commit lints passed`.

- [x] **Step 4: Record the build suite's baseline.** It takes about a minute.

```bash
uv run --directory build --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q -rf
```

Expected: a summary line to write down for Task 7. In a worktree there is no `build/.scratch/`, so it reads `4 failed, … passed, … skipped`, and the four `FAILED` lines are `test_verify_citations.py`'s ground-truth tests (`FileNotFoundError`). Where `build/.scratch/` exists, no test fails.

- [x] **Step 5: Amend the spec (D1).** Make four replacements in `specs/test-suite-registry.md`.

Replace

````markdown
| `name` | string | yes | The name that the runner takes. A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`. |
````

with

````markdown
| `name` | string | yes | The name that the runner takes. A skill's suite uses the skill's name; the others take their directory's name: `build`, `cc_guide` and `hooks` (owner, plan 55, 2026-10-18). |
````

Replace

````markdown
| `cc-guide` | `build/cc_guide` | — | — | default |
````

with

````markdown
| `cc_guide` (owner, plan 55, 2026-10-18) | `build/cc_guide` | — | — | default |
````

Replace

````markdown
R3.6 **`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`. Today that is
`cc-guide`: `cd build && pytest` collects `build/cc_guide` already.
````

with

````markdown
R3.6 **`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`. Today that is
`cc_guide` (owner, plan 55, 2026-10-18): `cd build && pytest` collects `build/cc_guide` already.
````

Replace

````markdown
| 141–145 | Drop line 145, the `cd build/cc_guide && …` command. The comment names the suite `run_suites.py cc-guide` instead of "its suite". |
````

with

````markdown
| 141–145 | Drop line 145, the `cd build/cc_guide && …` command. The comment names the suite `cc_guide` instead of "its suite" (owner, plan 55, 2026-10-18): a bare `cc-guide` in `CLAUDE.md` names the manual-only `/cc-guide` skill, which the `dmi-handoff-consistency` check refuses. |
````

Then confirm that no stale name is left:

```bash
grep -n -e 'cc-guide' specs/test-suite-registry.md
```

Expected: only lines that name the `/cc-guide` skill, the `<!-- cc-guide: … -->` stamp, or the amendment's own reason. No line names a suite `cc-guide`.

- [x] **Step 6: Commit.**

```bash
git add specs/test-suite-registry.md
```

```bash
git commit -m "docs(specs): name the build/cc_guide suite cc_guide (plan 55, D1)" -m "A bare cc-guide in CLAUDE.md names the manual-only /cc-guide skill, which dmi-handoff-consistency refuses, so the suite takes its directory's name, as build and hooks do."
```

### Task 2: The registry model

**Files:**
- Create: `build/run_suites.py`, `build/test_run_suites.py`

**Interfaces:**
- Consumes: nothing.
- Produces, in `build/run_suites.py`:
  - constants `REPO: Path` (the repo root), `REGISTRY = 'build/suites.toml'`, `DEFAULT_PYTHONS = ('3.13',)`, `TEST_FILE_PATTERNS`;
  - `@dataclass(frozen=True) class Suite(name: str, dir: str, deps: tuple[str, ...], extras=(), pythons=DEFAULT_PYTHONS, notes=())`;
  - `@dataclass(frozen=True) class Run(suite: Suite, python: str, argv: tuple[str, ...])`, with `.label -> str` (`'<name> (<python>)'`) and `.shell() -> str`;
  - `validate(data: dict) -> list[str]`, `parse(data: dict) -> list[Suite]`, `runs(suite, extras=False, pytest_args=()) -> list[Run]`, `container(suite, suites) -> Suite | None`.
- In `build/test_run_suites.py`: `FIXTURE` (a three-suite registry text), `ONE`, `problems(text)`, `fixture_suites()`. Tasks 3–5 append to this file.

The module docstring describes the finished module. Tasks 3 and 4 add the functions it names, and some constants wait for them too.

- [x] **Step 1: Write the failing tests.** Create `build/test_run_suites.py`:

```python
'''Tests for run_suites.py, the runner and commit lint for build/suites.toml.

The run tests inject a fake run function, so no test starts uv; the --check tests
build throwaway git repositories.
'''
import tomllib

import pytest

import run_suites as rs

FIXTURE = '''\
[[suite]]
name = 'alpha'
dir = 'skills/alpha/scripts'
with = ['pytest', 'polars']
extras = ['arviz>=1.0']
notes = ['Reads a pilot wiki, else skips.']

[[suite]]
name = 'outer'
dir = 'tools'
with = ['pytest']

[[suite]]
name = 'tools-inner'
dir = 'tools/inner'
with = ['pytest']
pythons = ['3.13', '/usr/bin/python3']
'''
ONE = "[[suite]]\nname = 'a'\ndir = 'x'\n"  # a suite table without its `with` line


def problems(text):
    return rs.validate(tomllib.loads(text))


def fixture_suites():
    return rs.parse(tomllib.loads(FIXTURE))


# --- the registry: validation, runs, nesting ---

def test_the_fixture_registry_is_valid():
    assert problems(FIXTURE) == []


@pytest.mark.parametrize('text, problem', [
    (ONE + "with = ['pytest']\nwtih = ['polars']\n", "suite 1 (a): unknown key 'wtih'"),
    ("[[suite]]\nname = 'a'\nwith = ['pytest']\n", "suite 1 (a): missing key 'dir'"),
    (ONE + "with = 'pytest'\n", "suite 1 (a): 'with' must be a list of non-empty strings"),
    (ONE + "with = ['pytest', '']\n", "suite 1 (a): 'with' must be a list of non-empty strings"),
    (ONE + "with = ['polars']\n", "suite 1 (a): 'with' must include 'pytest'"),
    (ONE + "with = ['pytest']\npythons = []\n", "suite 1 (a): 'pythons' must not be empty"),
    (ONE + "with = ['pytest']\nnotes = 'one note'\n", "suite 1 (a): 'notes' must be a list of non-empty strings"),
    ("[[suite]]\nname = ''\ndir = 'x'\nwith = ['pytest']\n", "suite 1: 'name' must be a non-empty string"),
    ("[[suite]]\nname = 'a'\ndir = '../x'\nwith = ['pytest']\n",
     "suite 1 (a): 'dir' must be a normalised path below the repo root"),
    ("[[suite]]\nname = 'a'\ndir = 'x/'\nwith = ['pytest']\n",
     "suite 1 (a): 'dir' must be a normalised path below the repo root"),
    ("[[suite]]\nname = 'a'\ndir = '.'\nwith = ['pytest']\n",
     "suite 1 (a): 'dir' must be a normalised path below the repo root"),
    (ONE + "with = ['pytest']\n" + ONE.replace('x', 'y') + "with = ['pytest']\n", 'suite 2 (a): duplicate name'),
    (ONE + "with = ['pytest']\n" + ONE.replace("'a'", "'b'") + "with = ['pytest']\n",
     "suite 2 (b): duplicate dir 'x'"),
    ("title = 'suites'\n" + ONE + "with = ['pytest']\n", "unknown top-level key 'title'"),
    ('', 'no [[suite]] tables'),
])
def test_validate_refuses(text, problem):
    assert problem in problems(text)


def test_a_default_run_has_the_form_claude_md_used():
    [run] = rs.runs(fixture_suites()[0])
    assert run.label == 'alpha (3.13)'
    assert run.argv == ('uv', 'run', '--python', '3.13', '--with', 'pytest', '--with', 'polars',
                        'python', '-m', 'pytest', '-q')
    assert run.shell() == ('cd skills/alpha/scripts && uv run --python 3.13 --with pytest '
                           '--with polars python -m pytest -q')


def test_extras_and_pytest_args_follow_the_deps_and_are_quoted():
    [run] = rs.runs(fixture_suites()[0], extras=True, pytest_args=('-k', 'a and b'))
    assert run.shell() == ("cd skills/alpha/scripts && uv run --python 3.13 --with pytest "
                           "--with polars --with 'arviz>=1.0' python -m pytest -q -k 'a and b'")


def test_each_python_gets_its_own_run_in_order():
    first, second = rs.runs(fixture_suites()[2])
    assert (first.python, second.python) == ('3.13', '/usr/bin/python3')
    assert second.shell() == 'cd tools/inner && uv run --python /usr/bin/python3 --with pytest python -m pytest -q'


def test_container_is_the_suite_whose_directory_holds_this_one():
    alpha, outer, inner = suites = fixture_suites()
    assert rs.container(inner, suites) == outer
    assert rs.container(outer, suites) is None
    assert rs.container(alpha, suites) is None


def test_container_compares_path_parts_not_string_prefixes():
    build = rs.Suite('build', 'build', ('pytest',))
    other = rs.Suite('other', 'build_extra', ('pytest',))
    assert rs.container(other, [build, other]) is None
```

- [x] **Step 2: Run them to see them fail.**

```bash
uv run --directory build --python 3.13 --with pytest python -m pytest -q test_run_suites.py
```

Expected: `1 error`, a collection error: `ModuleNotFoundError: No module named 'run_suites'`.

- [x] **Step 3: Write the module.** Create `build/run_suites.py`:

```python
'''Run the repo's directory-scoped pytest suites from their registry, build/suites.toml.

Each suite runs pytest from its own directory through uv, with its own inline deps;
the root CLAUDE.md says why. From any directory in the repo:

    uv run --python 3.13 python build/run_suites.py --list [NAME ...]
    uv run --python 3.13 python build/run_suites.py NAME [NAME ...] [--extras] [-- PYTEST_ARGS]
    uv run --python 3.13 python build/run_suites.py --all [--extras] [-- PYTEST_ARGS]
    uv run --python 3.13 python build/run_suites.py --check

--list prints each suite's exact shell commands, its extras and its notes; --extras and
the arguments after -- apply there too. A run prints its suite's notes after its first
header and keeps going after a failure. --all skips a suite whose directory lies inside
another suite's, since pytest collects it there. --check is a commit lint: it validates
the registry and fails when a directory that holds pytest files lies inside no
registered suite directory.

Exit status: 0 when everything passes; 1 when a run fails or --check finds a problem;
2 for a usage error, an unknown suite name or an invalid registry.
Design: specs/test-suite-registry.md.
'''
import shlex
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

REPO = Path(__file__).resolve().parent.parent
REGISTRY = 'build/suites.toml'  # relative to the repo root
DEFAULT_PYTHONS = ('3.13',)
TEST_FILE_PATTERNS = ('test_*.py', '*_test.py')  # pytest's default python_files
REQUIRED_KEYS = ('name', 'dir', 'with')
OPTIONAL_KEYS = ('extras', 'pythons', 'notes')
STRING_KEYS = ('name', 'dir')
LIST_KEYS = ('with', 'extras', 'pythons', 'notes')


@dataclass(frozen=True)
class Suite:
    name: str
    dir: str
    deps: tuple[str, ...]  # the registry's `with` list
    extras: tuple[str, ...] = ()
    pythons: tuple[str, ...] = DEFAULT_PYTHONS
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Run:
    '''One interpreter's pytest run of one suite.'''
    suite: Suite
    python: str
    argv: tuple[str, ...]

    @property
    def label(self) -> str:
        return f'{self.suite.name} ({self.python})'

    def shell(self) -> str:
        '''The run as one shell line, in the form the root CLAUDE.md used.'''
        return f'cd {shlex.quote(self.suite.dir)} && {shlex.join(self.argv)}'


def _is_string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) and v for v in value)


def _dir_problem(value: str) -> str | None:
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or str(path) != value or value == '.':
        return "'dir' must be a normalised path below the repo root"
    return None


def validate(data: dict) -> list[str]:
    '''Every problem that keeps the registry from being used; empty when it is valid.'''
    problems = [f'unknown top-level key {key!r}' for key in data if key != 'suite']
    tables = data.get('suite')
    if not isinstance(tables, list) or not tables:
        return [*problems, 'no [[suite]] tables']
    names: set[str] = set()
    dirs: set[str] = set()
    for i, table in enumerate(tables, start=1):
        if not isinstance(table, dict):
            problems.append(f'suite {i}: not a table')
            continue
        name = table.get('name')
        where = f'suite {i} ({name})' if isinstance(name, str) and name else f'suite {i}'
        problems += [f'{where}: unknown key {key!r}' for key in table
                     if key not in REQUIRED_KEYS + OPTIONAL_KEYS]
        problems += [f'{where}: missing key {key!r}' for key in REQUIRED_KEYS if key not in table]
        problems += [f'{where}: {key!r} must be a non-empty string' for key in STRING_KEYS
                     if key in table and not (isinstance(table[key], str) and table[key])]
        problems += [f'{where}: {key!r} must be a list of non-empty strings' for key in LIST_KEYS
                     if key in table and not _is_string_list(table[key])]
        if _is_string_list(table.get('with')) and 'pytest' not in table['with']:
            problems.append(f"{where}: 'with' must include 'pytest'")
        if table.get('pythons') == []:
            problems.append(f"{where}: 'pythons' must not be empty")
        if isinstance(name, str) and name:
            if name in names:
                problems.append(f'{where}: duplicate name')
            names.add(name)
        dir_ = table.get('dir')
        if isinstance(dir_, str) and dir_:
            if problem := _dir_problem(dir_):
                problems.append(f'{where}: {problem}')
            if dir_ in dirs:
                problems.append(f'{where}: duplicate dir {dir_!r}')
            dirs.add(dir_)
    return problems


def parse(data: dict) -> list[Suite]:
    '''The suites of a registry that validate() passes, in file order.'''
    return [Suite(name=t['name'], dir=t['dir'], deps=tuple(t['with']),
                  extras=tuple(t.get('extras', ())),
                  pythons=tuple(t.get('pythons', DEFAULT_PYTHONS)),
                  notes=tuple(t.get('notes', ())))
            for t in data['suite']]


def runs(suite: Suite, extras: bool = False, pytest_args: Sequence[str] = ()) -> list[Run]:
    '''One run per interpreter, in the suite's order; --extras adds the extras.'''
    deps = suite.deps + (suite.extras if extras else ())
    withs = tuple(word for dep in deps for word in ('--with', dep))
    return [Run(suite, python, ('uv', 'run', '--python', python, *withs,
                                'python', '-m', 'pytest', '-q', *pytest_args))
            for python in suite.pythons]


def container(suite: Suite, suites: Sequence[Suite]) -> Suite | None:
    '''The other suite whose directory holds this suite's directory, if any.'''
    path = PurePosixPath(suite.dir)
    return next((other for other in suites
                 if other.dir != suite.dir and path.is_relative_to(other.dir)), None)
```

- [x] **Step 4: Run the tests.** Same command as Step 2. Expected: `21 passed`.

- [x] **Step 5: Gates and commit.**

```bash
bash build/run_commit_lints.sh
```

```bash
git add build/run_suites.py build/test_run_suites.py
```

```bash
git commit -m "feat(build): the test-suite registry's model: validation, runs and nesting (plan 55)"
```

### Task 3: The coverage check

**Files:**
- Modify: `build/run_suites.py` (the import block; append after `container()`)
- Modify: `build/test_run_suites.py` (the import block; append at the end)

**Interfaces:**
- Consumes: `validate`, `parse`, `REGISTRY`, `TEST_FILE_PATTERNS` (Task 2).
- Produces: `git_env() -> dict[str, str]`, `pytest_dirs(root: Path) -> set[str] | None`, and `check(root: Path, data: dict) -> list[str]`, which returns finished finding lines. Each registry problem starts `build/suites.toml: `; an uncovered directory reads `<dir>: holds pytest files, but no suite in build/suites.toml contains it`. The tests gain `git_repo(root, files)`, `findings(root)` and `COVERED`.

- [x] **Step 1: Write the failing tests.** In `build/test_run_suites.py`, replace the line `import tomllib` with these two lines:

```python
import subprocess
import tomllib
```

Then append this block to the end of the file, with two blank lines before it:

```python
# --- --check: the registry and its coverage ---

COVERED = {
    'build/suites.toml': FIXTURE,
    'skills/alpha/scripts/test_a.py': '',
    'tools/test_t.py': '',
    'tools/inner/test_i.py': '',
}


def git_repo(root, files):
    '''Write files under root and git-init it, so `git ls-files --others` lists them.'''
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    subprocess.run(['git', 'init', '-q'], cwd=root, env=rs.git_env(), check=True)
    return root


def findings(root):
    return rs.check(root, tomllib.loads((root / 'build' / 'suites.toml').read_text()))


def test_check_passes_when_every_test_directory_is_registered(tmp_path):
    assert findings(git_repo(tmp_path, COVERED)) == []


def test_check_flags_a_test_directory_outside_every_suite(tmp_path):
    root = git_repo(tmp_path, {**COVERED, 'skills/beta/scripts/test_b.py': ''})
    assert findings(root) == [
        'skills/beta/scripts: holds pytest files, but no suite in build/suites.toml contains it']


def test_check_knows_both_pytest_file_patterns(tmp_path):
    root = git_repo(tmp_path, {**COVERED, 'misc/smoke_test.py': '', 'misc/helper.py': '',
                               'docs/test_notes.md': ''})
    assert findings(root) == ['misc: holds pytest files, but no suite in build/suites.toml contains it']


def test_check_flags_a_registered_directory_that_is_missing(tmp_path):
    files = {rel: text for rel, text in COVERED.items() if not rel.startswith('skills/alpha/')}
    assert findings(git_repo(tmp_path, files)) == [
        'build/suites.toml: alpha: skills/alpha/scripts is not a directory']


def test_check_flags_a_registered_directory_without_tests(tmp_path):
    files = {rel: text for rel, text in COVERED.items() if not rel.startswith('skills/alpha/')}
    root = git_repo(tmp_path, {**files, 'skills/alpha/scripts/tool.py': ''})
    assert findings(root) == ['build/suites.toml: alpha: skills/alpha/scripts holds no pytest file']


def test_check_ignores_gitignored_trees(tmp_path):
    root = git_repo(tmp_path, {**COVERED, '.gitignore': 'wt/\n', 'wt/skills/beta/test_b.py': ''})
    assert findings(root) == []


def test_check_reports_registry_problems_alone(tmp_path):
    root = git_repo(tmp_path, {**COVERED, 'build/suites.toml': FIXTURE.replace('with', 'wtih', 1),
                               'skills/beta/scripts/test_b.py': ''})
    assert findings(root) == ["build/suites.toml: suite 1 (alpha): unknown key 'wtih'",
                              "build/suites.toml: suite 1 (alpha): missing key 'with'"]


def test_check_flags_suites_out_of_name_order(tmp_path):
    swapped = FIXTURE.replace("name = 'alpha'", "name = 'zulu'")
    root = git_repo(tmp_path, {**COVERED, 'build/suites.toml': swapped})
    assert findings(root) == ["build/suites.toml: suites are not sorted by name: 'outer' comes after 'zulu'"]


def test_check_fails_closed_outside_a_git_repository(tmp_path):
    (tmp_path / 'build').mkdir()
    (tmp_path / 'build' / 'suites.toml').write_text(FIXTURE)
    assert findings(tmp_path) == ['build/suites.toml: git ls-files failed, so the test directories are unknown']
```

- [x] **Step 2: Run them to see them fail.**

```bash
uv run --directory build --python 3.13 --with pytest python -m pytest -q test_run_suites.py
```

Expected: `9 failed, 21 passed`. Eight fail with `AttributeError: module 'run_suites' has no attribute 'git_env'`, and one with `… no attribute 'check'`.

- [x] **Step 3: Write the check.** In `build/run_suites.py`, replace the import block (from `import shlex` through `from pathlib import Path, PurePosixPath`) with:

```python
import os
import shlex
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath
```

Then append this block after `container()`, with two blank lines between:

```python
def git_env() -> dict[str, str]:
    '''os.environ without git's repo-local variables, as check_conformance.git_env:
    a hook may export GIT_DIR or GIT_INDEX_FILE for another repository.'''
    local = subprocess.run(['git', 'rev-parse', '--local-env-vars'],
                           capture_output=True, text=True, check=True).stdout.split()
    return {name: value for name, value in os.environ.items() if name not in local}


def pytest_dirs(root: Path) -> set[str] | None:
    '''The directories that hold a pytest file, among the files git keeps under root
    (tracked, or untracked and not ignored); None when git fails.'''
    try:
        listing = subprocess.run(
            ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
            cwd=root, env=git_env(), capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    paths = [os.fsdecode(entry) for entry in listing.split(b'\0') if entry]
    # --cached also lists tracked files deleted from the working tree.
    return {str(PurePosixPath(p).parent) for p in paths
            if any(fnmatchcase(PurePosixPath(p).name, pattern) for pattern in TEST_FILE_PATTERNS)
            and (root / p).is_file()}


def check(root: Path, data: dict) -> list[str]:
    '''The --check findings: the registry's problems, then any test directory that
    no registered suite directory contains.'''
    problems = [f'{REGISTRY}: {p}' for p in validate(data)]
    if problems:
        return problems
    suites = parse(data)
    names = [s.name for s in suites]
    problems += [f'{REGISTRY}: suites are not sorted by name: {b!r} comes after {a!r}'
                 for a, b in zip(names, names[1:]) if a > b][:1]
    found = pytest_dirs(root)
    if found is None:
        return [*problems, f'{REGISTRY}: git ls-files failed, so the test directories are unknown']
    for suite in suites:
        if not (root / suite.dir).is_dir():
            problems.append(f'{REGISTRY}: {suite.name}: {suite.dir} is not a directory')
        elif not any(PurePosixPath(d).is_relative_to(suite.dir) for d in found):
            problems.append(f'{REGISTRY}: {suite.name}: {suite.dir} holds no pytest file')
    problems += [f'{d}: holds pytest files, but no suite in {REGISTRY} contains it'
                 for d in sorted(found)
                 if not any(PurePosixPath(d).is_relative_to(s.dir) for s in suites)]
    return problems
```

- [x] **Step 4: Run the tests.** Same command as Step 2. Expected: `30 passed`.

- [x] **Step 5: Gates and commit.**

```bash
bash build/run_commit_lints.sh
```

```bash
git add build/run_suites.py build/test_run_suites.py
```

```bash
git commit -m "feat(build): the registry's coverage check over the files git keeps (plan 55)"
```

### Task 4: The command line

**Files:**
- Modify: `build/run_suites.py` (the import block; append at the end)
- Modify: `build/test_run_suites.py` (append at the end)

**Interfaces:**
- Consumes: everything in Tasks 2 and 3.
- Produces: `RunOne = Callable[[Path, Run], int]`, `run_subprocess(root, run) -> int`, `execute(root, suites, extras, pytest_args, run_one) -> int`, `list_suites(suites, extras, pytest_args) -> None`, `parse_args(argv) -> (Namespace, tuple[str, ...])`, and `main(argv=None, root=REPO, run_one=run_subprocess) -> int`. The output lines are `== <label>`, `note: <text>`, `suite runs passed` (stdout), `suite runs failed: <labels>` (stderr), `skip <name>: the <outer> suite collects <dir>`, and `suite registry ok`.

- [x] **Step 1: Write the failing tests.** Append this block to the end of `build/test_run_suites.py`, with two blank lines before it:

```python
# --- the command line ---

class FakeRuns:
    '''Records each run's label and returns its exit code (0 unless given).'''

    def __init__(self, codes=None):
        self.codes = codes or {}
        self.labels = []
        self.argvs = []

    def __call__(self, root, run):
        self.labels.append(run.label)
        self.argvs.append(run.argv)
        return self.codes.get(run.label, 0)


@pytest.fixture
def repo(tmp_path):
    (tmp_path / 'build').mkdir()
    (tmp_path / 'build' / 'suites.toml').write_text(FIXTURE)
    return tmp_path


def test_a_named_suite_runs_once_per_python(repo, capsys):
    fake = FakeRuns()
    assert rs.main(['tools-inner'], root=repo, run_one=fake) == 0
    assert fake.labels == ['tools-inner (3.13)', 'tools-inner (/usr/bin/python3)']
    assert capsys.readouterr().out.splitlines()[-1] == 'suite runs passed'


def test_a_failed_run_does_not_stop_the_next(repo, capsys):
    fake = FakeRuns({'tools-inner (3.13)': 1})
    assert rs.main(['tools-inner', 'alpha'], root=repo, run_one=fake) == 1
    assert fake.labels == ['tools-inner (3.13)', 'tools-inner (/usr/bin/python3)', 'alpha (3.13)']
    assert capsys.readouterr().err.splitlines()[-1] == 'suite runs failed: tools-inner (3.13)'


def test_no_tests_collected_counts_as_a_failure(repo):
    assert rs.main(['alpha'], root=repo, run_one=FakeRuns({'alpha (3.13)': 5})) == 1


def test_the_notes_follow_the_first_header(repo, capsys):
    rs.main(['alpha'], root=repo, run_one=FakeRuns())
    assert capsys.readouterr().out.splitlines()[:2] == ['== alpha (3.13)', 'note: Reads a pilot wiki, else skips.']


def test_extras_and_pytest_args_reach_the_run(repo):
    fake = FakeRuns()
    rs.main(['alpha', '--extras', '--', '-k', 'x'], root=repo, run_one=fake)
    assert fake.argvs == [('uv', 'run', '--python', '3.13', '--with', 'pytest', '--with', 'polars',
                           '--with', 'arviz>=1.0', 'python', '-m', 'pytest', '-q', '-k', 'x')]


def test_all_skips_a_suite_inside_another(repo, capsys):
    fake = FakeRuns()
    assert rs.main(['--all'], root=repo, run_one=fake) == 0
    assert fake.labels == ['alpha (3.13)', 'outer (3.13)']
    assert 'skip tools-inner: the outer suite collects tools/inner' in capsys.readouterr().out


def test_list_prints_commands_extras_and_notes_and_runs_nothing(repo, capsys):
    fake = FakeRuns()
    assert rs.main(['--list', 'alpha'], root=repo, run_one=fake) == 0
    assert fake.labels == []
    assert capsys.readouterr().out.splitlines() == [
        'alpha: skills/alpha/scripts',
        '  cd skills/alpha/scripts && uv run --python 3.13 --with pytest --with polars python -m pytest -q',
        '  extras: arviz>=1.0',
        '  note: Reads a pilot wiki, else skips.',
    ]


def test_an_unknown_suite_exits_2(repo, capsys):
    assert rs.main(['nope'], root=repo, run_one=FakeRuns()) == 2
    assert 'unknown suite: nope' in capsys.readouterr().err


def test_an_invalid_registry_stops_a_run_with_exit_2(repo, capsys):
    (repo / 'build' / 'suites.toml').write_text(FIXTURE.replace('with', 'wtih', 1))
    fake = FakeRuns()
    assert rs.main(['outer'], root=repo, run_one=fake) == 2
    assert fake.labels == []
    assert "build/suites.toml: suite 1 (alpha): unknown key 'wtih'" in capsys.readouterr().err


def test_a_missing_registry_exits_2_for_a_run_and_1_for_check(tmp_path):
    assert rs.main(['alpha'], root=tmp_path, run_one=FakeRuns()) == 2
    assert rs.main(['--check'], root=tmp_path) == 1


@pytest.mark.parametrize('argv', [
    [], ['--', '-x'], ['--check', 'alpha'], ['--check', '--extras'], ['--check', '--', '-x'],
    ['--all', 'alpha'], ['--list', '--all'],
])
def test_usage_errors_exit_2(repo, argv):
    with pytest.raises(SystemExit) as stop:
        rs.main(argv, root=repo, run_one=FakeRuns())
    assert stop.value.code == 2


def test_check_mode_prints_ok_and_exits_0(tmp_path, capsys):
    assert rs.main(['--check'], root=git_repo(tmp_path, COVERED)) == 0
    assert capsys.readouterr().out == 'suite registry ok\n'


def test_check_mode_prints_each_finding_and_exits_1(tmp_path, capsys):
    root = git_repo(tmp_path, {**COVERED, 'skills/beta/scripts/test_b.py': ''})
    assert rs.main(['--check'], root=root) == 1
    assert capsys.readouterr().out == (
        'skills/beta/scripts: holds pytest files, but no suite in build/suites.toml contains it\n')


def test_a_run_that_cannot_start_fails(tmp_path, capsys):
    [run] = rs.runs(rs.Suite('ghost', 'missing', ('pytest',)))
    assert rs.run_subprocess(tmp_path, run) == 1
    assert 'ghost (3.13): cannot start' in capsys.readouterr().err
```

- [x] **Step 2: Run them to see them fail.**

```bash
uv run --directory build --python 3.13 --with pytest python -m pytest -q test_run_suites.py
```

Expected: `20 failed, 30 passed`. Nineteen fail with `AttributeError: module 'run_suites' has no attribute 'main'`, and one with `… no attribute 'run_subprocess'`.

- [x] **Step 3: Write the command line.** In `build/run_suites.py`, replace the import block with:

```python
import argparse
import os
import shlex
import subprocess
import sys
import tomllib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath
```

Then append this block to the end of the file, with two blank lines before it:

```python
RunOne = Callable[[Path, Run], int]


def run_subprocess(root: Path, run: Run) -> int:
    '''Start one run in its suite's directory, with this process's environment.'''
    try:
        return subprocess.run(run.argv, cwd=root / run.suite.dir).returncode
    except OSError as exc:
        print(f'{run.label}: cannot start: {exc}', file=sys.stderr, flush=True)
        return 1


def execute(root: Path, suites: Sequence[Suite], extras: bool, pytest_args: Sequence[str],
            run_one: RunOne) -> int:
    '''Every run of every suite, in order; a failure does not stop the next run.'''
    failed: list[str] = []
    for suite in suites:
        for i, run in enumerate(runs(suite, extras, pytest_args)):
            print(f'== {run.label}', flush=True)
            if i == 0:
                for note in suite.notes:
                    print(f'note: {note}', flush=True)
            if run_one(root, run) != 0:
                failed.append(run.label)
    if failed:
        print(f'suite runs failed: {", ".join(failed)}', file=sys.stderr)
        return 1
    print('suite runs passed')
    return 0


def list_suites(suites: Sequence[Suite], extras: bool, pytest_args: Sequence[str]) -> None:
    for suite in suites:
        print(f'{suite.name}: {suite.dir}')
        for run in runs(suite, extras, pytest_args):
            print(f'  {run.shell()}')
        if suite.extras:
            print(f'  extras: {" ".join(suite.extras)}')
        for note in suite.notes:
            print(f'  note: {note}')


def parse_args(argv: list[str]) -> tuple[argparse.Namespace, tuple[str, ...]]:
    '''The options, and the pytest arguments that follow a `--`.'''
    pytest_args: tuple[str, ...] = ()
    if '--' in argv:
        cut = argv.index('--')
        argv, pytest_args = argv[:cut], tuple(argv[cut + 1:])
    parser = argparse.ArgumentParser(
        prog='run_suites.py', epilog='Arguments after -- go to pytest in every run.',
        description="Run the repo's pytest suites from build/suites.toml.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--list', action='store_true',
                      help="print each suite's commands, extras and notes; runs nothing")
    mode.add_argument('--all', action='store_true',
                      help="run every suite, except one inside another suite's directory")
    mode.add_argument('--check', action='store_true',
                      help='validate the registry and its coverage (a commit lint)')
    parser.add_argument('--extras', action='store_true',
                        help='add the deps that unlock skips')
    parser.add_argument('names', nargs='*', metavar='NAME', help='a suite to run or list')
    args = parser.parse_args(argv)
    if args.check and (args.names or args.extras or pytest_args):
        parser.error('--check takes no suite names, --extras or pytest arguments')
    if args.all and args.names:
        parser.error('--all takes no suite names')
    if not (args.list or args.all or args.check or args.names):
        parser.error('name a suite, or use --list, --all or --check')
    return args, pytest_args


def main(argv: Sequence[str] | None = None, root: Path = REPO,
         run_one: RunOne = run_subprocess) -> int:
    args, pytest_args = parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        data = tomllib.loads((root / REGISTRY).read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f'{REGISTRY}: cannot read: {exc}', file=sys.stderr)
        return 1 if args.check else 2
    if args.check:
        problems = check(root, data)
        for problem in problems:
            print(problem)
        if problems:
            return 1
        print('suite registry ok')
        return 0
    problems = validate(data)
    if problems:
        for problem in problems:
            print(f'{REGISTRY}: {problem}', file=sys.stderr)
        return 2
    suites = parse(data)
    by_name = {suite.name: suite for suite in suites}
    unknown = [name for name in args.names if name not in by_name]
    if unknown:
        print(f'unknown suite: {", ".join(unknown)} (--list names them all)', file=sys.stderr)
        return 2
    chosen = [by_name[name] for name in args.names] or suites
    if args.list:
        list_suites(chosen, args.extras, pytest_args)
        return 0
    if args.all:
        chosen = []
        for suite in suites:
            if outer := container(suite, suites):
                print(f'skip {suite.name}: the {outer.name} suite collects {suite.dir}')
            else:
                chosen.append(suite)
    return execute(root, chosen, args.extras, pytest_args, run_one)


if __name__ == '__main__':
    sys.exit(main())
```

- [x] **Step 4: Run the tests.** Same command as Step 2. Expected: `50 passed`. Then:

```bash
uv run --python 3.13 python build/run_suites.py --list
```

Expected: exit 2 and `build/suites.toml: cannot read: …`, because the registry arrives in Task 5.

- [x] **Step 5: Gates and commit.**

```bash
bash build/run_commit_lints.sh
```

```bash
git add build/run_suites.py build/test_run_suites.py
```

```bash
git commit -m "feat(build): run_suites.py's command line: --list, named runs, --all and --check (plan 55)"
```

### Task 5: The registry and the command audit

**Files:**
- Create: `build/suites.toml`
- Modify: `build/test_run_suites.py` (append at the end)
- Scratch: `.sdd/55-test-suite-registry/audit_commands.py` (never committed)

**Interfaces:**
- Consumes: `check`, `REPO`, `REGISTRY` (Tasks 2–4).
- Produces: the registry that Tasks 6 and 7 rely on, with suite names `bayesian-workflow`, `brainstorming`, `build`, `cc_guide`, `classification-codes`, `describe-critique-methodology`, `design-architecture`, `explore-data`, `geographic-codes`, `hooks`, `llm-wiki`, `recommend-probabilistic-model`, `recommend-visualization`, `subagent-driven-development`, `systematic-debugging`, `track-model-experiments`, `tune-hyperparameters` and `writing-plans`.

- [x] **Step 1: Write the failing test.** Append this block to the end of `build/test_run_suites.py`, with two blank lines before it:

```python
# --- the real registry ---

def test_the_real_registry_passes_check():
    data = tomllib.loads((rs.REPO / rs.REGISTRY).read_text(encoding='utf-8'))
    assert rs.check(rs.REPO, data) == []
```

- [x] **Step 2: Run it to see it fail.**

```bash
uv run --directory build --python 3.13 --with pytest python -m pytest -q test_run_suites.py
```

Expected: `1 failed, 50 passed`. The failure is `FileNotFoundError: … build/suites.toml`.

- [x] **Step 3: Write the registry.** Create `build/suites.toml`. Each entry carries its `CLAUDE.md` command and comment (spec R2.3).

```toml
# Test-suite registry: one [[suite]] table for each directory-scoped pytest suite,
# sorted by name. build/run_suites.py reads it, and `run_suites.py --check`, a
# commit lint, fails when a directory that holds pytest files lies inside no
# registered suite directory. Design: specs/test-suite-registry.md (R2).
#
#   name     the name run_suites.py takes
#   dir      the repo-relative directory pytest runs from
#   with     the default --with deps, in the order a run passes them; includes pytest
#   extras   optional: the deps that unlock skips, added only by --extras
#   pythons  optional: one run per interpreter, in order (default ['3.13'])
#   notes    optional: what the suite covers or needs; --list prints them, and a run
#            prints them after its first header

[[suite]]
name = 'bayesian-workflow'
dir = 'skills/bayesian-workflow/scripts'
with = ['pytest', 'arviz', 'arviz-stats', 'numpy', 'xarray']
extras = ['matplotlib']
notes = [
    'Script tests: MCSE precision, divergence-gate and calibration next steps and verdicts, figures, --ci-prob, --loo-pit group checks.',
    '--extras (matplotlib) runs the figure test.',
    'CALIBRATION_SWEEP=1 runs the pre-registered acceptance sweep over both paths (seeds 0-99, about 1.5 min; -s prints its counts).',
    "arviz's \"invalid value encountered in scalar divide\" warnings on the constant-parameter fixture are expected, not silenced.",
]

[[suite]]
name = 'brainstorming'
dir = 'skills/brainstorming/scripts'
with = ['pytest']
notes = ['Server tests (stdlib only); they need node, else skip.']

[[suite]]
name = 'build'
dir = 'build'
with = ['pytest', 'numpy', 'polars', 'pyyaml']
extras = ['arviz>=1.0', 'arviz-base', 'arviz-stats', 'arviz-plots', 'numpyro', 'jax', 'matplotlib']
notes = [
    'Every build-directory test, build/cc_guide/ included. Without --extras, the snippet tests that need the stack skip.',
    "A fresh clone or worktree lacks the gitignored build/.scratch/, so test_verify_citations.py's ground-truth tests fail or skip there.",
]

[[suite]]
name = 'cc_guide'
dir = 'build/cc_guide'
with = ['pytest']
notes = ["The Claude Code guide drift detector's tests. The build suite collects them too, so --all runs them there."]

[[suite]]
name = 'classification-codes'
dir = 'skills/classification-codes/scripts'
with = ['pytest', 'polars']
notes = ['Build tests (fixtures are in-memory frames, so no workbook reader is needed).']

[[suite]]
name = 'describe-critique-methodology'
dir = 'skills/describe-critique-methodology/scripts'
with = ['pytest']
notes = ['Decoupling-check tests.']

[[suite]]
name = 'design-architecture'
dir = 'skills/design-architecture/scripts'
with = ['pytest']
notes = ['ADR-scaffolder tests (stdlib only).']

[[suite]]
name = 'explore-data'
dir = 'skills/explore-data/scripts'
with = ['pytest', 'polars']
notes = [
    "profile.py tests (its --json contract is recommend-visualization's input).",
    "profile.py shadows the stdlib profile module, but the repo-wide reason in CLAUDE.md's Commands section is why it runs from its own directory.",
]

[[suite]]
name = 'geographic-codes'
dir = 'skills/geographic-codes/scripts'
with = ['pytest', 'polars', 'fastexcel']
notes = ['Build tests; the per-vintage workbook tests read the committed sources/.']

[[suite]]
name = 'hooks'
dir = 'hooks'
with = ['pytest']
pythons = ['3.13', '/usr/bin/python3']
notes = [
    'Read-only agent guard tests (Gate A: classifier units, payload contract).',
    "The guard is stdlib only and must stay 3.9-compatible, so both runs matter: the 3.13 run tests each contract through the hook's shebang on the test's PATH and on launchd's /usr/bin-first PATH (under uv run the shebang resolves to uv's pinned python); the /usr/bin/python3 run tests the whole suite under the 3.9 floor.",
    'Where /usr/bin/python3 is missing or not 3.9, the launchd-PATH runs skip (-rs shows why) and the floor goes untested.',
    'Gate B is the live probe, ./hooks/probe-readonly-guard.sh, which spawns claude -p.',
]

[[suite]]
name = 'llm-wiki'
dir = 'skills/llm-wiki/scripts'
with = ['pytest']
notes = [
    'Bundled wiki-script tests (bootstrap, lint, session and specs distillers; stdlib only).',
    'The @needs_pilot tests read a pilot wiki at $LLM_WIKI_ROOT (default ~/research-wiki) and skip without one.',
]

[[suite]]
name = 'recommend-probabilistic-model'
dir = 'skills/recommend-probabilistic-model/scripts'
with = ['pytest', 'numpy', 'polars']
notes = ['Signal-extractor tests.']

[[suite]]
name = 'recommend-visualization'
dir = 'skills/recommend-visualization/scripts'
with = ['pytest', 'numpy', 'polars']
notes = ['Router tests.']

[[suite]]
name = 'subagent-driven-development'
dir = 'skills/subagent-driven-development/scripts'
with = ['pytest']
notes = ['Dispatch-script tests (stdlib only; they drive its bash scripts).']

[[suite]]
name = 'systematic-debugging'
dir = 'skills/systematic-debugging'
with = ['pytest']
notes = ['find-polluter.sh tests (stdlib only).']

[[suite]]
name = 'track-model-experiments'
dir = 'skills/track-model-experiments/scripts'
with = ['pytest', 'numpy', 'polars', 'arviz', 'numpyro', 'h5netcdf', 'h5py']
notes = [
    'Ledger/compare tests (~20–50 s, depending on the uv cache).',
    'They round-trip InferenceData to .nc, so they need the full numpyro + NetCDF-writer chain.',
]

[[suite]]
name = 'tune-hyperparameters'
dir = 'skills/tune-hyperparameters/scripts'
with = ['pytest', 'numpy', 'polars']
extras = ['scikit-learn', 'optuna']
notes = [
    'CV-splitter tests; --extras (scikit-learn, optuna) runs their skips.',
    'The package is scikit-learn: --with sklearn fails.',
]

[[suite]]
name = 'writing-plans'
dir = 'skills/writing-plans/scripts'
with = ['pytest']
notes = ['Deferred-backlog stats and entry-check tests (stdlib only; the entry-check tests build throwaway git repos).']
```

- [x] **Step 4: Plan 52's entry, only if Task 1, Step 2 listed files.** Add this entry just before the `writing-plans` entry, which keeps the name order:

```toml
[[suite]]
name = 'write-with-asd-ste100'
dir = 'skills/write-with-asd-ste100/scripts'
with = ['pytest']
notes = ['Tests for the vendored linter: its pinned bytes, its self-test under 3.13 and /usr/bin/python3, and its JSON report.']
```

> Deviation: Task 1, Step 2 listed no files, so Task 5 skipped this step. Plan 52 then merged to `main` (PR #64, `7731167`). The entry went in after that, as its own commit, `1694542`, before Task 7.

- [x] **Step 5: Run the tests and the check.** Same command as Step 2. Expected: `51 passed`. Then:

```bash
uv run --python 3.13 python build/run_suites.py --check
```

Expected: `suite registry ok`, exit 0.

- [x] **Step 6: Write and run the audit.** Create `.sdd/55-test-suite-registry/audit_commands.py`:

```python
'''Plan 55 Stage 2 audit (scratch, never committed).

Run from the worktree root, before CLAUDE.md loses its per-suite commands:
    uv run --no-project --python 3.13 python <path to this file>

Check 1: the suite commands in CLAUDE.md (from the `# Full build-directory tests`
comment through the `cd hooks && ` line, plus the `cd build/cc_guide && ` line;
hooks' `&&` chain split into one command per run) equal the default shell forms
that `run_suites.py --list` prints, with nothing left over on either side.
Check 2: the deps that each suite's comment names after `--with` are that suite's
extras, apart from tune-hyperparameters' "--with sklearn fails" warning.
Then it prints each suite's comment beside its registry notes, for a reader to
confirm that no clause was lost. Exit 0 when checks 1 and 2 pass.
'''
import re
import subprocess
import sys
import tomllib
from pathlib import Path

lines = Path('CLAUDE.md').read_text(encoding='utf-8').split('\n')
start = next(i for i, line in enumerate(lines) if line.startswith('# Full build-directory tests'))
end = next(i for i, line in enumerate(lines) if line.startswith('cd hooks && '))
cc_guide = next(i for i, line in enumerate(lines) if line.startswith('cd build/cc_guide && '))

commands: list[str] = []
comments: dict[str, list[str]] = {}  # suite dir -> the comment lines above its command
pending: list[str] = []
for line in [*lines[start:end + 1], lines[cc_guide]]:
    if line.startswith('#'):
        pending.append(line.removeprefix('# '))
    elif line.startswith('cd '):
        cd, rest = line.split(' && ', 1)
        commands += [f'{cd} && {part}' for part in rest.split(' && ')]
        comments.setdefault(cd.removeprefix('cd '), []).extend(pending)
        pending = []
    elif line.strip():
        sys.exit(f'unexpected line in the suite region: {line!r}')

listed = subprocess.run(['uv', 'run', '--python', '3.13', 'python', 'build/run_suites.py', '--list'],
                        capture_output=True, text=True, check=True).stdout
forms = [line.strip() for line in listed.splitlines() if line.startswith('  cd ')]
missing = sorted(set(commands) - set(forms))
extra = sorted(set(forms) - set(commands))
print(f'check 1: {len(commands)} CLAUDE.md commands, {len(forms)} registry runs')
for command in missing:
    print(f'  only in CLAUDE.md: {command}')
for form in extra:
    print(f'  only in the registry: {form}')

registry = tomllib.loads(Path('build/suites.toml').read_text(encoding='utf-8'))['suite']
by_dir = {suite['dir']: suite for suite in registry}
# The comment for the systematic-debugging line also covers the brainstorming line below it.
comments.setdefault('skills/brainstorming/scripts', []).extend(comments.get('skills/systematic-debugging', []))
wrong_extras = []
for dir_, text in comments.items():
    named = {w.strip('"\'.,;') for w in re.findall(r'--with (\S+)', ' '.join(text))} - {'sklearn'}
    if named != set(by_dir[dir_].get('extras', [])):
        wrong_extras.append(f'  {dir_}: comment names {sorted(named)}, extras are {by_dir[dir_].get("extras", [])}')
print(f'check 2: {len(wrong_extras)} suites whose comment deps differ from their extras')
print('\n'.join(wrong_extras))

for dir_, text in comments.items():
    suite = by_dir[dir_]
    print(f'\n== {suite["name"]} ({dir_})')
    for line in text:
        print(f'  comment: {line}')
    for note in suite.get('notes', []):
        print(f'  note:    {note}')
    if suite.get('pythons'):
        print(f'  pythons: {suite["pythons"]}')

sys.exit(1 if missing or extra or wrong_extras else 0)
```

```bash
uv run --no-project --python 3.13 python .sdd/55-test-suite-registry/audit_commands.py
```

Expected: exit 0, `check 1: 19 CLAUDE.md commands, 19 registry runs` with no `only in` line, and `check 2: 0 suites whose comment deps differ from their extras`. With plan 52's entry, the counts are 20. Then read each printed `== <suite>` group. Every clause of each `comment:` line must appear in that suite's `note:` lines, its extras or its `pythons`, apart from the suite's own name. The comment of `systematic-debugging` also covers `brainstorming`, and `cc_guide` has no comment of its own. A missing clause fails the step: add it to the notes, and run Step 5 again.

> Deviation: after plan 52's entry, the audit found 20 commands and 20 runs. Task 5 had found 19 and 19. Plan 52's `CLAUDE.md` comment is headed "Stdlib-only suites". The notes of `describe-critique-methodology` and `write-with-asd-ste100` do not say "stdlib only". The plan's text for both notes is verbatim, and `with = ['pytest']` shows the fact. The task reviewer accepted this.

- [x] **Step 7: Gates and commit.**

```bash
bash build/run_commit_lints.sh
```

```bash
git add build/suites.toml build/test_run_suites.py
```

```bash
git commit -m "feat(build): register the directory suites in build/suites.toml (plan 55)" -m "Each entry carries its CLAUDE.md command and comment. A one-time audit matched every CLAUDE.md suite command to a registry run, with none left over."
```

### Task 6: The ninth commit lint

**Files:**
- Modify: `build/test_commit_lints.py` (`CHECKS`; a new test before `test_hook_fails_open_without_uv`)
- Modify: `build/run_commit_lints.sh` (the header comment; a new last `run` line)
- Modify: `build/CLAUDE.md` ("eight" becomes "nine"; a new paragraph)

**Interfaces:**
- Consumes: `run_suites.py --check` and the committed registry (Tasks 4 and 5).
- Produces: the lint named `suite_registry`, which Task 7's `CLAUDE.md` text names.

- [x] **Step 1: Write the failing tests.** In `build/test_commit_lints.py`, replace

```python
          'critical_placement'}
```

with

```python
          'critical_placement', 'suite_registry'}
```

Then insert this test just before `def test_hook_fails_open_without_uv(clone, tmp_path):`, followed by two blank lines:

```python
def test_unregistered_suite_is_refused(clone):
    '''The ninth lint keeps build/suites.toml complete: a first test file in
    tech-debt's scripts directory needs a [[suite]] entry before it can be committed.'''
    test = clone / 'skills' / 'tech-debt' / 'scripts' / 'test_scan.py'
    test.write_text('def test_scan():\n    assert True\n')
    git(clone, 'add', 'skills/tech-debt/scripts/test_scan.py')
    before = head(clone)
    result = commit(clone, '-m', 'unregistered suite')
    assert result.returncode != 0, result.stderr
    assert head(clone) == before
    assert failed_names(result) == {'suite_registry'}, result.stderr
    assert ('skills/tech-debt/scripts: holds pytest files, but no suite in build/suites.toml '
            'contains it') in result.stderr, result.stderr
```

- [x] **Step 2: Run them to see them fail.** It takes about 20 seconds.

```bash
uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_commit_lints.py -k "unregistered_suite or fails_closed_without_uv"
```

Expected: `2 failed`. `test_unregistered_suite_is_refused` fails at `assert result.returncode != 0` (`assert 0 != 0`: the commit went through), and `test_runner_fails_closed_without_uv` fails because `suite_registry` is missing from the failed set.

- [x] **Step 3: Add the lint.** In `build/run_commit_lints.sh`, replace

```bash
# The eight commit lints that CLAUDE.md lists under Commands. Fails closed: exit 1
```

with

```bash
# The nine commit lints that CLAUDE.md lists under Commands. Fails closed: exit 1
```

Then, after the `run critical_placement …` line, add:

```bash
run suite_registry uv run --python 3.13 python build/run_suites.py --check
```

- [x] **Step 4: Run the tests.**

```bash
uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_commit_lints.py
```

Expected: every test passes, +1 on the Task 1 base.

- [x] **Step 5: Update `build/CLAUDE.md`.** Replace

````markdown
`run_commit_lints.sh` runs the eight commit lints that the root `CLAUDE.md`
````

with

````markdown
`run_commit_lints.sh` runs the nine commit lints that the root `CLAUDE.md`
````

Then replace

````markdown
CI. `test_commit_lints.py` drives the runner and hook through throwaway
clones and checks the workflow's triggers and pins.
````

with

````markdown
CI. `test_commit_lints.py` drives the runner and hook through throwaway
clones and checks the workflow's triggers and pins.

`suites.toml` registers every directory-scoped pytest suite, and
`run_suites.py` lists, runs and checks them; its docstring gives the options.
`run_suites.py --check` is a commit lint: it fails when a directory that holds
pytest files is not registered, so a new suite adds its `[[suite]]` entry in
the same change.
````

- [x] **Step 6: Gates and commit.**

```bash
bash build/run_commit_lints.sh
```

Expected: `== suite_registry`, then `suite registry ok`, and the last line `commit lints passed`.

```bash
git add build/run_commit_lints.sh build/test_commit_lints.py build/CLAUDE.md
```

```bash
git commit -m "feat(build): run_suites.py --check is the ninth commit lint (plan 55)" -m "A directory that holds pytest files cannot be committed until build/suites.toml registers it."
```

### Task 7: The `CLAUDE.md` Commands block

**Files:**
- Modify: `CLAUDE.md` (line 60; lines 66–125; lines 127–132; lines 141 and 145)
- Modify: `build/test_check_conformance.py` (`test_claude_md_import_resolves_passes_on_the_repo`)
- Scratch: `.sdd/55-test-suite-registry/compare_runs.py` and `shrink_claude_md.py` (never committed)

**Interfaces:**
- Consumes: the registry (Task 5), `run_suites.py` (Task 4), the lint named `suite_registry` (Task 6), and the build baseline (Task 1, Step 4).
- Produces: the finished Commands block.

- [x] **Step 1: Re-run the audit.** `CLAUDE.md` must not have changed since Task 5.

```bash
uv run --no-project --python 3.13 python .sdd/55-test-suite-registry/audit_commands.py
```

Expected: exit 0, with the same counts as Task 5.

> Deviation: `CLAUDE.md` had changed since Task 5. Plan 52 had merged and folded seven suites under one comment, so the file had 197 lines, not 199. The audit ran after the registry gained plan 52's entry. It printed 20 commands and 20 runs, where Task 5 printed 19 and 19.

- [x] **Step 2: Compare direct and runner runs.** Create `.sdd/55-test-suite-registry/compare_runs.py`:

```python
'''Plan 55, Task 7: compare direct and runner runs (scratch, never committed).

Run from the worktree root while CLAUDE.md still lists the per-suite commands:
    uv run --no-project --python 3.13 python <path to this file> [NAME ...]

For each named suite (default: every registered suite) it runs the suite's
CLAUDE.md command line through bash, from the repo root, and then
`run_suites.py NAME`; keeps pytest's summary lines with the timing removed; and
prints both lists. Exit 0 when every suite's two lists, and the two exit
statuses' pass or fail, match.
'''
import re
import subprocess
import sys
import tomllib
from pathlib import Path

SUMMARY = re.compile(r'^\d+ (?:passed|failed|skipped|errors?|xfailed|xpassed|deselected|warnings?)\b.* in [\d.]+s')
registry = {s['name']: s for s in tomllib.loads(Path('build/suites.toml').read_text(encoding='utf-8'))['suite']}
lines = Path('CLAUDE.md').read_text(encoding='utf-8').split('\n')


def summaries(output: str) -> list[str]:
    return [re.sub(r' in [\d.]+s.*$', '', line) for line in output.splitlines() if SUMMARY.match(line)]


mismatched = []
for name in sys.argv[1:] or list(registry):
    prefix = f'cd {registry[name]["dir"]} && '
    # The directory-suite line, not a selection such as `cd build && … pytest -q test_x.py`.
    [direct] = [line for line in lines if line.startswith(prefix) and line.endswith(' python -m pytest -q')]
    old = subprocess.run(['bash', '-c', direct], capture_output=True, text=True)
    new = subprocess.run(['uv', 'run', '--python', '3.13', 'python', 'build/run_suites.py', name],
                         capture_output=True, text=True)
    old_s, new_s = summaries(old.stdout + old.stderr), summaries(new.stdout + new.stderr)
    same = old_s == new_s and (old.returncode == 0) == (new.returncode == 0)
    print(f'{name}: {"same" if same else "DIFFERENT"}', flush=True)
    print(f'  direct (exit {old.returncode}): {old_s}', flush=True)
    print(f'  runner (exit {new.returncode}): {new_s}', flush=True)
    if not same:
        mismatched.append(name)
sys.exit(1 if mismatched else 0)
```

Run it in the background, because it takes about 6 minutes:

```bash
uv run --no-project --python 3.13 python .sdd/55-test-suite-registry/compare_runs.py
```

Expected: exit 0, and `<suite>: same` for every suite, the build suite included. The build suite's `direct` and `runner` lines show the same summary as Task 1, Step 4, plus the passes from this plan's new tests. Write the 18 result pairs down for the completion report.

> Deviation: there are 19 result pairs, not 18, because plan 52's suite is registered. All 19 read `same`.

- [x] **Step 3: Run `--all` once.** It takes about 3 minutes; run it in the background.

```bash
uv run --python 3.13 python build/run_suites.py --all
```

Expected: a `skip cc_guide: the build suite collects build/cc_guide` line. Then one `== <suite> (<python>)` header per run, with each suite's notes after its first header. The last line is `suite runs passed`. In a worktree without `build/.scratch/`, it is instead `suite runs failed: build (3.13)` on stderr, with exit 1, matching Step 2.

- [x] **Step 4: Replace the per-suite commands.** Create `.sdd/55-test-suite-registry/shrink_claude_md.py`:

```python
'''Plan 55, Task 7: replace CLAUDE.md's per-suite commands (scratch, never committed).

Run from the worktree root, after the Stage 2 audit passes:
    uv run --no-project --python 3.13 python <path to this file>

Replaces every line from the `# Full build-directory tests` comment through the
`cd hooks && ` command with BLOCK, and deletes the `cd build/cc_guide && ` command.
Anchoring on those lines, not on the text between them, makes the edit work in
either landing order with plan 52 (spec R5.2).
'''
from pathlib import Path

BLOCK = '''\
# Directory suites (build/suites.toml): --list prints each suite's exact command, extras and notes; name one or more
# suites to run them (--extras adds the deps that unlock skips; arguments after -- go to pytest, e.g. a test node ID),
# or --all for every suite. --check, a commit lint, fails when a directory holding tests is not registered
uv run --python 3.13 python build/run_suites.py --list
uv run --python 3.13 python build/run_suites.py <name> [--extras] [-- <pytest args>]
uv run --python 3.13 python build/run_suites.py --all
uv run --python 3.13 python build/run_suites.py --check'''

path = Path('CLAUDE.md')
lines = path.read_text(encoding='utf-8').split('\n')


def only(prefix: str) -> int:
    found = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    assert len(found) == 1, f'{prefix!r} starts {len(found)} lines, not 1'
    return found[0]


start, end, cc_guide = only('# Full build-directory tests'), only('cd hooks && '), only('cd build/cc_guide && ')
assert start < end < cc_guide, (start, end, cc_guide)
del lines[cc_guide]
lines[start:end + 1] = BLOCK.split('\n')
path.write_text('\n'.join(lines), encoding='utf-8')
print(f'replaced lines {start + 1}-{end + 1} with {len(BLOCK.splitlines())}; deleted line {cc_guide + 1}')
```

```bash
uv run --no-project --python 3.13 python .sdd/55-test-suite-registry/shrink_claude_md.py
```

Expected: `replaced lines 66-125 with 7; deleted line 145`.

> Deviation: the script printed `replaced lines 67-123 with 7; deleted line 143`, not `66-125` and `145`. Plan 52's merge had moved the anchors, and the replacement also removed plan 52's fold (spec R5.2). The script needed no change.

- [x] **Step 5: Edit the rest of the Commands block.** Make three replacements in `CLAUDE.md`.

Replace

````markdown
There is no root test runner or repo-wide `pyproject`, and the scientific deps (numpy, polars, pytest) aren't installed into the interpreter directly. Run everything through `uv run` pinned to the Homebrew Python 3.13, supplying deps inline. Tests use **bare imports** and are **directory-scoped** — run pytest from inside the relevant directory, not the repo root: each suite pins its own inline deps, and a repo-root collection fails outright anyway, since `geographic-codes` and `classification-codes` both ship a `test_build.py` whose basenames collide under pytest's prepend import mode with no `__init__.py`. Comments name the extra `--with` deps that unlock a suite's skips; pytest's summary line gives the counts.
````

with

````markdown
There is no repo-wide `pyproject`, and the scientific deps (numpy, polars, pytest) aren't installed into the interpreter directly. Run everything through `uv run` pinned to the Homebrew Python 3.13, supplying deps inline. Tests use **bare imports** and are **directory-scoped** — each suite runs pytest from inside its own directory with its own inline deps, never from the repo root: a repo-root collection fails outright, since `geographic-codes` and `classification-codes` both ship a `test_build.py` whose basenames collide under pytest's prepend import mode with no `__init__.py`. `build/suites.toml` registers each suite (its directory, its `--with` deps, the extras that unlock its skips, and its notes), and `build/run_suites.py` runs them, printing a suite's notes before its output; pytest's summary line gives the counts.
````

Replace

````markdown
# Commit lints: these three, the dependency-drift test, snippet Tier 1, sync_runtime_assets.py --check, the drift
# lint (cli.py lint, below) and the placement tests (below) make eight. build/run_commit_lints.sh runs all eight;
# build/githooks/pre-commit runs it on each commit once enabled (an owner step: git config core.hooksPath build/githooks
# writes repo config every worktree reads); the hook lints the working tree, untracked drafts included except by the
# drift lint, which reads tracked files only. .github/workflows/lints.yml runs them on PRs and main as an advisory
# check; the hook is the gate.
````

with

````markdown
# Commit lints: these three, the suite-registry check (run_suites.py --check, above), the dependency-drift test,
# snippet Tier 1, sync_runtime_assets.py --check, the drift lint (cli.py lint, below) and the placement tests (below)
# make nine. build/run_commit_lints.sh runs all nine; build/githooks/pre-commit runs it on each commit once enabled
# (an owner step: git config core.hooksPath build/githooks writes repo config every worktree reads); the hook lints
# the working tree, untracked drafts included except by the drift lint, which reads tracked files only.
# .github/workflows/lints.yml runs them on PRs and main as an advisory check; the hook is the gate.
````

Replace

````markdown
# Claude Code guide drift detector (build/cc_guide/): its suite; lint, run before committing a change to the guide, to
````

with

````markdown
# Claude Code guide drift detector (build/cc_guide/): suite cc_guide; lint, run before committing a change to the guide, to
````

- [x] **Step 6: See the import test fail.** Step 4 removed the llm-wiki note, and with it the test's `@needs_pilot` control.

```bash
uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k claude_md_import_resolves_passes_on_the_repo
```

Expected: `1 failed`, at `assert '@needs_pilot' in text`.

- [x] **Step 7: Move the control to the stamp.** In `build/test_check_conformance.py`, replace

```python
def test_claude_md_import_resolves_passes_on_the_repo():
    text = (cc.REPO / 'CLAUDE.md').read_text()
    assert '@needs_pilot' in text  # a naive scan would flag this, so the test means something
    assert real_check('claude-md-import-resolves') == []
```

with

```python
def test_claude_md_import_resolves_passes_on_the_repo():
    first = (cc.REPO / 'CLAUDE.md').read_text().split('\n', 1)[0]
    # A naive scan would read the cc-guide stamp's @<version> as an import, so the test
    # means something; a restamp changes the version but not the form.
    assert first.startswith('<!-- cc-guide: ') and ' @' in first, first
    assert real_check('claude-md-import-resolves') == []
```

Then run Step 6's command again. Expected: `1 passed`.

- [x] **Step 8: Gates.** Run each command.

```bash
wc -l CLAUDE.md
```

Expected: `145 CLAUDE.md`, or 145 plus whatever another plan added (Task 1, Step 1). It must stay under 200.

```bash
uv run --python 3.13 --with pyyaml python build/check_conformance.py
```

Expected: exit 0. A `dmi-handoff-consistency` finding that names `cc-guide` means that a bare `cc-guide` is left in `CLAUDE.md` (D1).

```bash
uv run --directory build --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q -rf
```

Expected: the same failures as Task 1, Step 4 (none, or the 4 `.scratch` ones), with +52 passes on that baseline: +51 in `test_run_suites.py` and +1 in `test_commit_lints.py`.

```bash
bash build/run_commit_lints.sh
```

Expected: the last line is `commit lints passed`.

> Deviation: the build suite printed `4 failed, 1146 passed, 13 skipped`. The step expected the Task 1 baseline plus 52 passes, which is 1135. Plan 52's merge added 11 passing tests. The baseline was measured again at `1694542`, and Task 7 added no test. `CLAUDE.md` has 146 lines, which the step allows ("145 plus whatever another plan added").

- [x] **Step 9: Commit.**

```bash
git add CLAUDE.md build/test_check_conformance.py
```

```bash
git commit -m "docs: CLAUDE.md points at run_suites.py instead of listing each suite (plan 55)" -m "build/suites.toml now carries each suite's command and notes. The one-time audit matched every removed command to a registry run, and every suite gave the same result direct and through the runner. CLAUDE.md drops from 199 lines to 145."
```

> Deviation: the commit also stages `build/githooks/pre-commit`. Its line 2 said "run the eight commit lints" and now says "nine". That file is not on the plan's list, and the owner chose to fix it here. The commit message says that `CLAUDE.md` drops from 197 lines to 146.

---

## Self-review

- **Spec coverage.**
  - R1, the scope: Task 5's registry and Task 7's deletion. R1.2's literal commands stay, because Task 7 deletes only the region between the two anchors and line 145.
  - R2, the registry: Task 5, with Task 2's validation.
  - R3, the runner: Tasks 2 and 4.
  - R4, the guard: Task 3 (`check`), Task 4 (`--check`) and Task 6 (the lint).
  - R5.1 and R5.2: Task 7. R5.3: Task 6. R5.4: Task 7, Steps 6–7. R5.5: no task touches those files.
  - R6.1: Tasks 2–5. R6.2: Task 6. R6.3: every task's red step.
  - R7.1: Couplings, Task 5, Step 4, and the completion steps' shared note. R7.2 and R7.3: Couplings.
  - The spec's Testing: Task 5, Step 6 (the audit), and Task 7, Steps 2–3 (behaviour) and Step 8 (gates).
  - Done when: items 1–2 are Tasks 2–6, item 3 is Task 5, Step 6 and Task 7, Steps 1–3, items 4–5 are Task 7, Step 8, and item 6 is the completion steps.
- **Placeholders.** None. Each code step shows the code, and each run step shows the command and its expected output.
- **Names.** `Suite`, `Run`, `validate`, `parse`, `runs`, `container`, `git_env`, `pytest_dirs`, `check`, `run_subprocess`, `execute`, `list_suites`, `parse_args`, `main`, `REGISTRY`, `REPO` and the lint name `suite_registry` are the same in every task and test.

## Execution handoff

Execute in a fresh session on Sonnet (the owner's routing: plan on Opus, execute on Sonnet), with this plan file as the handoff. Make the worktree from an up-to-date `main` after the plan merges, on a branch such as `feat/plan-55-suite-registry`. Subagent-driven development fits: each task has its own red and green cycle and its own commit, and only Task 7's comparison step runs long. Tasks 2–4 grow the same two files in order, so run them one at a time.

## Plan completion

Run the writing-plans Plan Completion Protocol after the final review, then:

- Check that the shared notes folder of this plan's session group still has `plan-54-suite-registry-for-plan-52.md`, with plan 52's entry (Couplings). If plan 52's Task 6 already landed and registered the suite, say so in the completion report instead.
- Append the spec's three out-of-scope items to `specs/deferred_items.md`, in this plan's section: CI running the suites, parallel runs with timeouts and machine-readable output, and moving the lint and tool commands into the runner. Each item gets its `Size:` and `Revisit if:` from the spec.
- Retire this plan, and the spec with it: no other live plan implements `specs/test-suite-registry.md`. In the same
  commit, re-point the two `Design:` citations to the retired path, as `build/check_conformance.py` cites its spec:
  `build/run_suites.py`'s docstring line `Design: specs/test-suite-registry.md.` and `build/suites.toml`'s header
  line `# registered suite directory. Design: specs/test-suite-registry.md (R2).` both become
  `specs/completed/test-suite-registry.md`.

> Deviation: the retire commit also changes "eight" to "nine" on line 19 of `specs/plans/53-agent-skills-portability.md`. That line is the Global Constraint "Gates before every commit". The file is not on this plan's list, and the owner chose this change at the completion gate on 2026-10-18. Lines 75 and 81 of that plan are history and stay as written.

> Deviation: the merge commit `ed4426f` has the app's default message and no `Co-Authored-By:` line. The app made it when it synced `main`, which brought in plan 52. At that commit, `run_suites.py --check` fails. Plan 52's suite is not registered until `1694542`.

'''Build plan 97's reviewer micro-test packages R4, R5 and R6, or check built ones.

Usage, from the repository root:
  uv run python <kit>/build_packages.py <out-dir>
  uv run python <kit>/build_packages.py --check <packages-dir>

A package is the seven files a task reviewer reads for one task: the brief, the implementer's
report, the controller's test run, the review package (the diff), the spec excerpts, the mutants
file and the controller's mutant run. Each package is made the way a real run makes it, with the
scripts of skills/subagent-driven-development/scripts/ at cases.SCRIPT_SHA, read with git show
into a scratch directory:

1. A new git repository under /tmp, outside every other repository, holds the package's first
   commit, the task's BASE: plan.md, the spec under specs/, the pre-change code (R4 and R5) and a
   .gitignore.
2. task-brief writes the brief from plan.md, Task 1. The excerpts file is written in the pinned
   form, and each excerpt is checked against its spec line.
3. As the implementer: RED, the fix or the new code, GREEN and the commits, then the patches and
   the mutants file, then mutant-run with BASE (run 1).
4. The implementer's report, written from the runs' real output.
5. As the controller: test-run on the brief's focused command and the documented suite, then
   mutant-run with BASE on the focused command (run 2), then review-package from BASE to HEAD.

Each commit has a fixed author, committer and date, so a rebuild makes the same shas. pytest's
timing lines differ from run to run, so a rebuild does not make byte-identical files. The seven
files are copied into <out-dir>/R<n>/ with the scratch repository's path written as /work/project
(cases.REPO) and $HOME written as `~`. <out-dir>/MANIFEST.txt gives each file's sha256, the base and
head of each package, and the sha256 of each script used. The scratch repositories stay under /tmp
for a hand check, and the script prints their paths.

Refuses an existing <out-dir>. Stops when a step does not give the result the package needs: a
script's exit status, a test count, a mutant's verdict, or a line of the revert section. Stops when
a copied file still names the scratch path, $HOME or its parent directory, $TMPDIR, the OS user name or one of
kit_identity.py's identity forms.

check_package() refuses a package whose diff name, run heads and tree lines disagree (plan 93's
refusal) or whose mutant run's base: line is not the diff's BASE. The build runs it on each package
before it writes any file, build_prompts.py runs it on each package it reads, and --check runs it
on each R<n>/ directory of an existing packages directory (exit 1 on a refusal).
'''
import getpass
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402
import kit_identity  # noqa: E402

SCRIPT_DIR = 'skills/subagent-driven-development/scripts'
SCRIPT_NAMES = ('sdd-repo', 'sdd-workspace', 'task-brief', 'test-run', 'mutant-run', 'review-package')
DATES = ('2026-11-02T09:00:00+0000', '2026-11-02T09:20:00+0000', '2026-11-02T09:40:00+0000')
VENV_PYTHON = '/tmp/mt-venv/bin/python'
GITIGNORE = '__pycache__/\n.pytest_cache/\n'

# ---------------------------------------------------------------- R4 and R5: the date window

WINDOW_SPEC = '''# Date windows

A window runs from a start date to an end date. The end date is never before the start date.

## Rules

A window starts on its start date: a day before the start date is outside it.
A window includes its end date: a day after the end date is outside it.
'''
WINDOW_EXCERPTS = ((8, 'A window includes its end date: a day after the end date is outside it.'),)
WINDOW_FOCUSED = f'{VENV_PYTHON} -m pytest -q tests/test_window.py'

WINDOW_BASE_CODE = '''from datetime import date


def in_window(day: date, start: date, end: date) -> bool:
    return start <= day < end
'''
WINDOW_CODE = WINDOW_BASE_CODE.replace('start <= day < end', 'start <= day <= end')

# The plan's Task 1. R4's plan test checks the day before the end date, so it passes on the
# pre-change code. R5's checks the end date itself. Nothing else in the plan differs.
WINDOW_PLAN = '''# Date Window Fix Plan

**Goal:** Make `in_window` include a day on the window's end date.

**Spec:** `specs/window.md`

**Tests:** `/tmp/mt-venv/bin/python -m pytest -q`

---

### Task 1: Include the end date in the window

**Files:**
- Modify: `window.py`
- Create: `tests/test_window.py`

**Interfaces:**
- Changes: `in_window(day: date, start: date, end: date) -> bool` in `window.py`.

`in_window` has a boundary bug. It leaves out a day on the window's end date, but the window includes its end date.

- [ ] **Step 1: Write the regression test**

Create `tests/test_window.py`:

```python
{plan_test}```

`test_window_includes_end_date` is the regression test for the bug: the window includes its end date.

- [ ] **Step 2: Fix `in_window`**

In `window.py`, make `in_window` follow the spec's rule.

- [ ] **Step 3: Run the test to see it pass**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests/test_window.py`
Expected: PASS (1 passed).

- [ ] **Step 4: Commit**

```bash
git add window.py tests/test_window.py
git commit -m "Include the end date in the window"
```
'''
WINDOW_PLAN_TEST = '''from datetime import date

from window import in_window


def test_window_includes_end_date():
    start, end = date(2026, 3, 1), date(2026, 3, 31)
    assert in_window(date(2026, 3, {day}), start, end) is True
    assert in_window(date(2026, 4, 1), start, end) is False
'''
R4_PLAN_TEST = WINDOW_PLAN_TEST.format(day=30)
R5_PLAN_TEST = WINDOW_PLAN_TEST.format(day=31)

R4_ADDED = '''

def test_window_holds_its_start_and_end_dates():
    start, end = date(2026, 3, 1), date(2026, 3, 31)
    assert in_window(date(2026, 2, 28), start, end) is False
    assert in_window(start, start, end) is True
    assert in_window(end, start, end) is True
    assert in_window(date(2026, 5, 4), date(2026, 5, 4), date(2026, 5, 4)) is True
    assert in_window(date(2027, 1, 5), date(2026, 12, 20), date(2027, 1, 5)) is True
'''
R5_ADDED = '''

def test_window_holds_its_end_date_in_other_windows():
    assert in_window(date(2026, 5, 4), date(2026, 5, 4), date(2026, 5, 4)) is True
    assert in_window(date(2027, 1, 5), date(2026, 12, 20), date(2027, 1, 5)) is True


def test_window_starts_on_start_date():
    start, end = date(2026, 3, 1), date(2026, 3, 31)
    assert in_window(start, start, end) is True
    assert in_window(date(2026, 2, 28), start, end) is False
'''

W8 = 'specs/window.md:8'
R4_HOLD = 'test_window_holds_its_start_and_end_dates'
R5_OTHER = 'test_window_holds_its_end_date_in_other_windows'
START_TEST = 'test_window_starts_on_start_date'
END_TEST = 'test_window_includes_end_date'

# ---------------------------------------------------------------- R6: byte sizes

SIZES_SPEC = '''# Sizes

A size names a number of bytes, such as `3KB`.

## Rules

`to_bytes` reads a size: a number of one or more digits `0` to `9`, then a unit, `B`, `KB` or `MB`, with nothing between them.
1 KB is 1024 B, and 1 MB is 1024 KB.
`to_bytes` raises `ValueError` for any other text.
'''
SIZES_EXCERPTS = (
    (7, '`to_bytes` reads a size: a number of one or more digits `0` to `9`, then a unit, `B`, `KB` or `MB`, '
        'with nothing between them.'),
    (8, '1 KB is 1024 B, and 1 MB is 1024 KB.'),
    (9, '`to_bytes` raises `ValueError` for any other text.'),
)
SIZES_FOCUSED = f'{VENV_PYTHON} -m pytest -q tests'

SIZES_PLAN = '''# Size Parser Implementation Plan

**Goal:** Add `to_bytes`, which reads a size such as `3KB` as a number of bytes.

**Spec:** `specs/sizes.md`

**Tests:** `/tmp/mt-venv/bin/python -m pytest -q`

---

### Task 1: `to_bytes`

**Files:**
- Create: `units.py`
- Create: `tests/test_units.py`

**Interfaces:**
- Produces: `to_bytes(text: str) -> int` in `units.py`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_units.py`:

```python
{plan_test}```

- [ ] **Step 2: Run the tests to see them fail**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests`
Expected: FAIL, with a `ModuleNotFoundError` for `units`.

- [ ] **Step 3: Write `to_bytes`**

Create `units.py`, and write `to_bytes` as the spec's rules say.

- [ ] **Step 4: Run the tests to see them pass**

Run: `/tmp/mt-venv/bin/python -m pytest -q tests`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add units.py tests/test_units.py
git commit -m "Add to_bytes"
```
'''
# F8's plan tests (../impl-kit/fixtures/F8/brief.md), byte for byte.
SIZES_PLAN_TEST = '''from units import to_bytes


def test_to_bytes_reads_each_unit():
    assert to_bytes('7B') == 7
    assert to_bytes('2KB') == 2048
    assert to_bytes('3MB') == 3145728


def test_to_bytes_reads_a_number_of_several_digits():
    assert to_bytes('15KB') == 15360
'''
SIZES_CODE = '''import re

UNITS = {'B': 1, 'KB': 1024, 'MB': 1024 * 1024}
SIZE = re.compile(r'([0-9]+)(B|KB|MB)')


def to_bytes(text: str) -> int:
    match = SIZE.fullmatch(text)
    if match is None:
        raise ValueError(f'not a size: {text!r}')
    digits, unit = match.groups()
    return int(digits) * UNITS[unit]
'''
# The implementer's added tests import units inside each test body, in a file of their own.
SIZES_ADDED = r"""import pytest


def test_to_bytes_reads_zero_and_leading_zeros():
    from units import to_bytes

    assert to_bytes('0B') == 0
    assert to_bytes('007KB') == 7168


def test_to_bytes_rejects_any_other_text():
    from units import to_bytes

    for text in ('', '12', 'KB', '3GB', '3kb', '3Kb', '3 KB', ' 3KB', '3KB ', '3KB\n', '3KBs', '-3KB', '+3KB',
                 '1.5KB', '1_0KB', '\u0663KB'):
        with pytest.raises(ValueError):
            to_bytes(text)
"""
S7, S8, S9 = 'specs/sizes.md:7', 'specs/sizes.md:8', 'specs/sizes.md:9'
EACH_UNIT = 'test_to_bytes_reads_each_unit'
DIGITS = 'test_to_bytes_reads_a_number_of_several_digits'
ZEROS = 'test_to_bytes_reads_zero_and_leading_zeros'
REJECTS = 'test_to_bytes_rejects_any_other_text'

# ---------------------------------------------------------------- the packages

# Each package: its files at BASE, the implementer's steps, the Inputs table, the mutants and the
# lines its revert section must hold. A mutant is (number, targets, the wrong version, (old, new)).
PACKAGES = {
    'R4': {
        'base_files': {'plan.md': WINDOW_PLAN.format(plan_test=R4_PLAN_TEST), 'specs/window.md': WINDOW_SPEC,
                       'window.py': WINDOW_BASE_CODE},
        'spec_path': 'specs/window.md', 'spec': WINDOW_SPEC, 'excerpts': WINDOW_EXCERPTS, 'focused': WINDOW_FOCUSED,
        'red': {'files': {'tests/test_window.py': R4_PLAN_TEST + R4_ADDED},
                'command': f'{WINDOW_FOCUSED}::{R4_HOLD}', 'exit': 1, 'expect': '1 failed'},
        'commits': (
            ({'window.py': WINDOW_CODE, 'tests/test_window.py': R4_PLAN_TEST + R4_ADDED},
             'Include the end date in the window', '2 passed'),
        ),
        'inputs': (
            (W8, 'a day on the end date', R4_HOLD),
            (W8, 'a window of one day, whose start date is its end date', R4_HOLD),
            (W8, 'a window that runs across a year end, on its end date', R4_HOLD),
            (W8, 'the day after the end date', END_TEST),
        ),
        'code_path': 'window.py', 'code': WINDOW_CODE,
        'mutants': (
            (1, (W8, R4_HOLD), 'leaves out the end date (`start <= day < end`)',
             ('start <= day <= end', 'start <= day < end')),
            (2, (W8, END_TEST), 'drops the end check, so a day after the end date is in the window (`start <= day`)',
             ('start <= day <= end', 'start <= day')),
        ),
        'lines': (),
        'revert': (f'passed tests.test_window::{END_TEST}', f'failed tests.test_window::{R4_HOLD}: '),
        'revert_line': 'revert: ran, exit 1, failed 1, not loaded 0, skipped 0, passed 1',
        'report': {
            'implemented': ('`in_window` in `window.py` now checks `start <= day <= end`, so a day on the window\'s end '
                            'date is in the window. A day after the end date, and a day before the start date, stay '
                            'outside it.'),
            'added': (f'The plan\'s test is unchanged. I added `{R4_HOLD}`: a day before the start date, the start '
                      'date, the end date, a window of one day and a window across a year end.'),
            'red_why': 'The failure was expected: `in_window` left out the end date.',
            'files': ('window.py', 'tests/test_window.py'),
        },
    },
    'R5': {
        'base_files': {'plan.md': WINDOW_PLAN.format(plan_test=R5_PLAN_TEST), 'specs/window.md': WINDOW_SPEC,
                       'window.py': WINDOW_BASE_CODE},
        'spec_path': 'specs/window.md', 'spec': WINDOW_SPEC, 'excerpts': WINDOW_EXCERPTS, 'focused': WINDOW_FOCUSED,
        'red': {'files': {'tests/test_window.py': R5_PLAN_TEST}, 'command': WINDOW_FOCUSED, 'exit': 1,
                'expect': '1 failed'},
        'commits': (
            ({'window.py': WINDOW_CODE, 'tests/test_window.py': R5_PLAN_TEST}, 'Include the end date in the window',
             '1 passed'),
            ({'tests/test_window.py': R5_PLAN_TEST + R5_ADDED}, 'Test the end date in other windows, and the start date',
             '3 passed'),
        ),
        'inputs': (
            (W8, 'a day on the end date', END_TEST),
            (W8, 'the day after the end date', END_TEST),
            (W8, 'a window of one day, whose start date is its end date', R5_OTHER),
            (W8, 'a window that runs across a year end, on its end date', R5_OTHER),
        ),
        'code_path': 'window.py', 'code': WINDOW_CODE,
        'mutants': (
            (1, (W8, END_TEST, R5_OTHER), 'leaves out the end date (`start <= day < end`)',
             ('start <= day <= end', 'start <= day < end')),
            (2, (W8, END_TEST), 'drops the end check, so a day after the end date is in the window (`start <= day`)',
             ('start <= day <= end', 'start <= day')),
            (3, (START_TEST,), 'leaves out the start date (`start < day <= end`)',
             ('start <= day <= end', 'start < day <= end')),
        ),
        'lines': (f'Keeps: {START_TEST} — the window starts on its start date',),
        'revert': (f'failed tests.test_window::{END_TEST}: ', f'failed tests.test_window::{R5_OTHER}: ',
                   f'passed tests.test_window::{START_TEST}'),
        'revert_line': 'revert: ran, exit 1, failed 2, not loaded 0, skipped 0, passed 1',
        'report': {
            'implemented': ('`in_window` in `window.py` now checks `start <= day <= end`, so a day on the window\'s end '
                            'date is in the window. A day after the end date, and a day before the start date, stay '
                            'outside it.'),
            'added': (f'The plan\'s test is unchanged. In a second commit I added `{R5_OTHER}` and `{START_TEST}`.'),
            'red_why': 'The failure was expected: `in_window` left out the end date.',
            'files': ('window.py', 'tests/test_window.py'),
        },
    },
    'R6': {
        'base_files': {'plan.md': SIZES_PLAN.format(plan_test=SIZES_PLAN_TEST), 'specs/sizes.md': SIZES_SPEC},
        'spec_path': 'specs/sizes.md', 'spec': SIZES_SPEC, 'excerpts': SIZES_EXCERPTS, 'focused': SIZES_FOCUSED,
        'red': {'files': {'tests/test_units.py': SIZES_PLAN_TEST}, 'command': SIZES_FOCUSED, 'exit': 2,
                'expect': "No module named 'units'"},
        'commits': (
            ({'units.py': SIZES_CODE, 'tests/test_units.py': SIZES_PLAN_TEST}, 'Add to_bytes', '2 passed'),
            ({'tests/test_units_shapes.py': SIZES_ADDED}, 'Test zero, leading zeros and any other text', '4 passed'),
        ),
        'inputs': (
            (S7, 'each unit: `B`, `KB` and `MB`', EACH_UNIT),
            (S7, 'a number of several digits', DIGITS),
            (S7, 'zero (`0B`), and a number with leading zeros (`007KB`)', ZEROS),
            (S8, '1 KB = 1024 B and 1 MB = 1024 KB', EACH_UNIT),
            (S9, 'empty text', REJECTS),
            (S9, 'a number with no unit (`12`), and a unit with no number (`KB`)', REJECTS),
            (S9, 'a unit that is not `B`, `KB` or `MB` (`3GB`)', REJECTS),
            (S9, 'a unit not in capitals (`3kb`, `3Kb`)', REJECTS),
            (S9, 'a blank between, before or after (`3 KB`, ` 3KB`, `3KB `, `3KB\\n`)', REJECTS),
            (S9, 'other text after the unit (`3KBs`)', REJECTS),
            (S9, 'a sign, a decimal point or an underscore (`-3KB`, `+3KB`, `1.5KB`, `1_0KB`)', REJECTS),
            (S9, 'a digit outside `0` to `9` (`\\u0663KB`, the Arabic-Indic three)', REJECTS),
        ),
        'code_path': 'units.py', 'code': SIZES_CODE,
        'mutants': (
            (1, (S8, EACH_UNIT, DIGITS, ZEROS), '1 KB is 1000 B (`\'KB\': 1000`)', ("'KB': 1024", "'KB': 1000")),
            (2, (S8, EACH_UNIT), '1 MB is 1000 KB (`\'MB\': 1000 * 1024`)', ("'MB': 1024 * 1024", "'MB': 1000 * 1024")),
            (3, (S7, DIGITS, ZEROS), 'reads a number of one digit only (`[0-9]` for `[0-9]+`)',
             ("r'([0-9]+)(B|KB|MB)'", "r'([0-9])(B|KB|MB)'")),
            (4, (S9, REJECTS), 'matches a size at the start of the text only, so text after it gets through '
                               '(`match` for `fullmatch`)', ('SIZE.fullmatch(text)', 'SIZE.match(text)')),
            (5, (S9, REJECTS), 'takes any Unicode digit (`\\d` for `[0-9]`)',
             ("r'([0-9]+)(B|KB|MB)'", "r'(\\d+)(B|KB|MB)'")),
        ),
        'lines': (),
        'revert': ("not loaded tests.test_units: ModuleNotFoundError: No module named 'units'",
                   f"failed tests.test_units_shapes::{ZEROS}: ModuleNotFoundError: No module named 'units'",
                   f"failed tests.test_units_shapes::{REJECTS}: ModuleNotFoundError: No module named 'units'"),
        'revert_line': 'revert: ran, exit 1, failed 2, not loaded 1, skipped 0, passed 0',
        'report': {
            'implemented': ('`to_bytes(text: str) -> int` in `units.py`. A regular expression must match the whole '
                            'text: one or more digits `0` to `9`, then `B`, `KB` or `MB`. The number is multiplied by '
                            '1, 1024 or 1024 * 1024. Any other text raises `ValueError`.'),
            'added': ('The plan\'s tests are unchanged. In a second commit I added `tests/test_units_shapes.py`, with '
                      f'`{ZEROS}` and `{REJECTS}`.'),
            'red_why': 'The failure was expected: `units.py` did not exist yet.',
            'files': ('units.py', 'tests/test_units.py', 'tests/test_units_shapes.py'),
        },
    },
}

REPORT = '''# Task 1 report

## What I implemented

{implemented}

## What I tested

- `{focused}`: {focused_last}
- `{suite}`: {suite_last}

{added}

## TDD Evidence

- RED: `{red_command}`

  ```
{red}
  ```

  {red_why}

- GREEN: `{focused}`

  ```
{green}
  ```

## Mutants

`{run}`: {result}. `{revert}`.

## Files changed

{files}

## Self-review findings

None.

## Issues or concerns

None.
'''


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(('GIT_', 'PYTEST', 'PYTHON', 'VIRTUAL_ENV', 'UV_', 'MUTANT_'))}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return env


def run(cmd: list[str], cwd: Path, expect: int | None = 0, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    done = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env or clean_env())
    if expect is not None and done.returncode != expect:
        raise SystemExit(f'{" ".join(cmd)} exited {done.returncode}, not {expect}:\n{done.stdout}{done.stderr}')
    return done


def git(repo: Path, *args: str, date: str | None = None) -> str:
    env = clean_env()
    if date:
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    return run(['git', '-C', str(repo), *args], repo, env=env).stdout.strip()


def write(repo: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def scripts(scratch: Path) -> tuple[Path, list[str]]:
    '''Write the scripts at cases.SCRIPT_SHA into <scratch>/scripts, executable.'''
    target = scratch / 'scripts'
    target.mkdir()
    notes = []
    for name in SCRIPT_NAMES:
        shown = subprocess.run(['git', 'show', f'{cases.SCRIPT_SHA}:{SCRIPT_DIR}/{name}'], capture_output=True)
        if shown.returncode != 0:
            raise SystemExit(f'missing {SCRIPT_DIR}/{name} at {cases.SCRIPT_SHA}')
        (target / name).write_bytes(shown.stdout)
        (target / name).chmod(0o755)
        notes.append(f'script {name} sha256 {sha256(shown.stdout)}')
    return target, notes


def excerpts_text(spec: dict) -> str:
    lines = spec['spec'].splitlines()
    out = [f'Spec: {spec["spec_path"]}', '']
    for number, text in spec['excerpts']:
        if lines[number - 1] != text:
            raise SystemExit(f'{spec["spec_path"]}:{number} is not the excerpt {text!r}')
        out.append(f'{spec["spec_path"]}:{number}: {text}')
    return '\n'.join(out) + '\n'


def mutants_text(spec: dict) -> str:
    rows = [f'| {rule} | {shape} | {test} |' for rule, shape, test in spec['inputs']]
    lines = ['# Task 1 mutants', '', '## Inputs', '', '| Rule | Shape | Test |', '|---|---|---|', *rows, '', '## Mutants', '']
    for number, targets, wrong, _ in spec['mutants']:
        lines.append(f'Mutant {number}: {", ".join(targets)} — {wrong} — task-1-mutant-{number}.patch')
    lines.extend(spec['lines'])
    return '\n'.join(lines) + '\n'


def last_line(text: str) -> str:
    return text.strip().splitlines()[-1].strip()


def indent(text: str) -> str:
    return '\n'.join(f'  {line}' if line else '' for line in text.strip('\n').splitlines())


def stdout_line(out: str, prefix: str) -> str:
    return next(line for line in out.splitlines() if line.startswith(prefix))


def run_path(out: str) -> Path:
    return Path(out.strip().splitlines()[-1].split('run: ', 1)[1])


def header(text: str) -> dict[str, str]:
    '''A run file's header lines after line 1 and before the first --- line, as {key: value}.'''
    fields = {}
    for line in text.splitlines()[1:]:
        if line.startswith('---'):
            break
        key, sep, value = line.partition(': ')
        if sep and key not in fields:
            fields[key] = value
    return fields


def check_package(name: str, files: dict[str, tuple[str, str]]) -> tuple[str, str]:
    '''Refuse a package whose diff name, run heads, tree lines and mutant-run base disagree.

    files maps 'test run', 'mutant run' and 'diff' to (file name, text). Returns the diff's base and
    head short shas.
    '''
    match = re.fullmatch(r'review-([0-9a-f]{7})\.\.([0-9a-f]{7})\.diff', files['diff'][0])
    if not match:
        raise SystemExit(f'refusing: {name} diff name {files["diff"][0]}')
    base, head = match.groups()
    for role in ('test run', 'mutant run'):
        fields = header(files[role][1])
        if not fields.get('head', '').startswith(head) or fields.get('tree') != 'clean':
            raise SystemExit(f'refusing: {name} {role} is not at head {head} on a clean tree')
    fields = header(files['mutant run'][1])
    run_base = fields.get('base', '')
    if not re.fullmatch(r'[0-9a-f]{40}', run_base) or not run_base.startswith(base):
        raise SystemExit(f'refusing: {name} mutant run base {run_base or "(none)"} is not the diff\'s BASE {base}')
    if 'revert' not in fields:
        raise SystemExit(f'refusing: {name} mutant run has no revert: line')
    return base, head


def build(name: str, spec: dict, scratch: Path, script_dir: Path) -> tuple[Path, str, str, list[Path]]:
    def script(script_name: str, *args: str, expect: int | None = 0) -> subprocess.CompletedProcess:
        return run([str(script_dir / script_name), *args], repo, expect=expect)

    def pytest(command: str, expect: int, want: str) -> subprocess.CompletedProcess:
        done = run(command.split(), repo, expect=expect)
        if want not in done.stdout:
            raise SystemExit(f'{name}: `{command}` does not show {want!r}:\n{done.stdout}')
        return done

    repo = scratch / 'project'
    repo.mkdir()
    write(repo, {**spec['base_files'], '.gitignore': GITIGNORE})
    git(repo, 'init', '-q', '-b', 'main')
    git(repo, 'config', 'user.name', 'Developer')
    git(repo, 'config', 'user.email', 'developer@example.invalid')
    git(repo, 'config', 'commit.gpgsign', 'false')
    git(repo, 'add', '-A')
    git(repo, 'commit', '-q', '-m', 'Start the project', date=DATES[0])
    base = git(repo, 'rev-parse', 'HEAD')
    workspace = Path(script('sdd-workspace', cases.PLAN_FILE).stdout.strip())
    script('task-brief', cases.PLAN_FILE, '1')
    brief = (workspace / 'task-1-brief.md').read_text()
    plan = spec['base_files']['plan.md']
    if brief != plan[plan.index('### Task 1:'):]:
        raise SystemExit(f'{name}: the brief is not the plan\'s Task 1 section')
    (workspace / 'task-1-spec.md').write_text(excerpts_text(spec))

    # The implementer: RED, then each commit with its focused run.
    write(repo, spec['red']['files'])
    red = pytest(spec['red']['command'], spec['red']['exit'], spec['red']['expect'])
    greens = []
    for index, (files, message, want) in enumerate(spec['commits'], 1):
        write(repo, files)
        greens.append(pytest(spec['focused'], 0, want))
        git(repo, 'add', '-A')
        git(repo, 'commit', '-q', '-m', message, date=DATES[index])
    head = git(repo, 'rev-parse', 'HEAD')
    if (repo / spec['code_path']).read_text() != spec['code']:
        raise SystemExit(f'{name}: the code at HEAD is not the package code')

    for number, _, _, (old, new) in spec['mutants']:
        if spec['code'].count(old) != 1:
            raise SystemExit(f'{name}: mutant {number} does not match the code once')
        (repo / spec['code_path']).write_text(spec['code'].replace(old, new))
        patch = run(['git', '-C', str(repo), 'diff', '--', spec['code_path']], repo).stdout
        if not patch.strip():
            raise SystemExit(f'{name}: mutant {number} made an empty patch')
        (workspace / f'task-1-mutant-{number}.patch').write_text(patch)
        git(repo, 'checkout', '--', spec['code_path'])
    (workspace / 'task-1-mutants.md').write_text(mutants_text(spec))
    focused = spec['focused'].split()
    impl = script('mutant-run', cases.PLAN_FILE, '1', base, '--', *focused)

    # The report, from the real output.
    suite_out = run(cases.SUITE_COMMAND.split(), repo)
    focused_out = run(focused, repo)
    report = REPORT.format(
        implemented=spec['report']['implemented'], focused=spec['focused'], suite=cases.SUITE_COMMAND,
        focused_last=last_line(focused_out.stdout), suite_last=last_line(suite_out.stdout),
        added=spec['report']['added'], red_command=spec['red']['command'],
        red=indent('\n'.join(red.stdout.strip().splitlines()[-6:])), red_why=spec['report']['red_why'],
        green=indent(greens[0].stdout), run=run_path(impl.stdout), result=stdout_line(impl.stdout, 'result: ')[8:],
        revert=stdout_line(impl.stdout, 'revert: '), files='\n'.join(f'- {f}' for f in spec['report']['files']))
    (workspace / 'task-1-report.md').write_text(report)

    # The controller: test-run, mutant-run with BASE, review-package.
    combined = f'({spec["focused"]}) && ({cases.SUITE_COMMAND})'
    test_run = run_path(script('test-run', cases.PLAN_FILE, '1', '--', 'sh', '-c', combined).stdout)
    controller = script('mutant-run', cases.PLAN_FILE, '1', base, '--', *focused)
    mutant_run = run_path(controller.stdout)
    for out in (impl.stdout, controller.stdout):
        if stdout_line(out, 'revert: ') != spec['revert_line']:
            raise SystemExit(f'{name}: the revert line is not {spec["revert_line"]!r}:\n{out}')
        if stdout_line(out, 'result: ') != f'result: caught {len(spec["mutants"])}, survived 0, invalid 0':
            raise SystemExit(f'{name}: not every mutant was caught:\n{out}')
    section = mutant_run.read_text().split('\n--- revert ---\n', 1)[1].split('\n--- output: ', 1)[0].splitlines()
    for want in spec['revert']:
        if not any(line.startswith(want) for line in section):
            raise SystemExit(f'{name}: the revert section has no line {want!r}:\n' + '\n'.join(section))
    wrote = script('review-package', cases.PLAN_FILE, base, head).stdout
    diff = Path(re.match(r'wrote (.+\.diff): ', wrote).group(1))
    files = [workspace / 'task-1-brief.md', workspace / 'task-1-report.md', test_run, diff,
             workspace / 'task-1-spec.md', workspace / 'task-1-mutants.md', mutant_run]
    return repo, base, head, files


def check_copy(name: str, text: str, scratch: Path) -> None:
    home = str(Path.home())
    tmpdir = os.environ.get('TMPDIR', '').rstrip('/')
    homes = str(Path.home().parent).rstrip('/') + '/'
    banned = [str(scratch), str(scratch.resolve()), homes, home, getpass.getuser(), '/private/var', '/var/folders']
    if tmpdir:
        banned.append(tmpdir)
    hits = sorted({b for b in banned if b and b in text})
    hits += sorted({token for value, token in kit_identity.forms() if kit_identity.pattern(value).search(text)})
    if hits:
        raise SystemExit(f'{name}: a copied file still names {len(hits)} banned form(s): '
                         f'{[h for h in hits if h.startswith(("<", "$"))] or "paths"}')


def copy_text(path: Path, repo: Path) -> str:
    text = path.read_text()
    for form in (str(repo), str(repo).replace('/private/tmp/', '/tmp/', 1)):
        text = text.replace(form, cases.REPO)
    return text.replace(str(Path.home()), '~')


def role_files(directory: Path) -> dict[str, tuple[str, str]]:
    found = {}
    for role, pattern in (('test run', 'task-1-tests.log'), ('mutant run', 'task-1-mutants*.log'), ('diff', 'review-*.diff')):
        matches = sorted(directory.glob(pattern))
        if len(matches) != 1:
            raise SystemExit(f'refusing: {len(matches)} files in {directory} match {pattern}')
        found[role] = (matches[0].name, matches[0].read_text())
    return found


def check_dir(packages: Path) -> None:
    names = sorted(p.name for p in packages.iterdir() if p.is_dir())
    if not names:
        raise SystemExit(f'refusing: no package directory in {packages}')
    for name in names:
        base, head = check_package(name, role_files(packages / name))
        print(f'{name}: base {base} head {head}: diff name, run heads, tree lines and mutant-run base agree')


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == '--check':
        check_dir(Path(sys.argv[2]))
        return
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    out_dir = Path(sys.argv[1])
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    if not os.access(VENV_PYTHON, os.X_OK):
        raise SystemExit(f'refusing: no {VENV_PYTHON}')
    tools = Path(tempfile.mkdtemp(prefix='mt-review-scripts-', dir='/tmp')).resolve()
    script_dir, notes = scripts(tools)
    built = {}
    for name, spec in PACKAGES.items():
        scratch = Path(tempfile.mkdtemp(prefix='mt-review-build-', dir='/tmp')).resolve()
        if run(['git', 'rev-parse', '--show-toplevel'], scratch, expect=None).returncode == 0:
            raise SystemExit(f'refusing: {scratch} is inside a git repository')
        repo, base, head, files = build(name, spec, scratch, script_dir)
        copies = {}
        for path in files:
            text = copy_text(path, repo)
            check_copy(name, text, scratch)
            copies[path.name] = text
        if len(copies) != 7:
            raise SystemExit(f'{name}: {len(copies)} files, not 7')
        test_run, diff, mutant_run = files[2].name, files[3].name, files[6].name
        check_package(name, {'test run': (test_run, copies[test_run]), 'diff': (diff, copies[diff]),
                             'mutant run': (mutant_run, copies[mutant_run])})
        built[name] = (copies, base, head, repo)
    for name, (copies, base, head, repo) in built.items():
        target = out_dir / name
        target.mkdir(parents=True)
        notes.append(f'{name} base {base} head {head}')
        for file_name, text in copies.items():
            (target / file_name).write_text(text)
            notes.append(f'{name}/{file_name} sha256 {sha256(text.encode())}')
    manifest = '\n'.join(notes) + '\n'
    check_copy('MANIFEST.txt', manifest, Path('/tmp/mt-review-build-'))
    (out_dir / 'MANIFEST.txt').write_text(manifest)
    print(f'wrote {len(built)} packages to {out_dir}')
    for name, (_, _, _, repo) in built.items():
        print(f'{name} scratch repository: {repo}')


if __name__ == '__main__':
    main()

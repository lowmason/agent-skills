# Hook Template Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the three project tooling hook templates tell lint from a ruff that cannot run, close `uv-guard.sh`'s leaks past prefixes, versioned names and paths, and drive all three templates from subprocess tests on both interpreters.

**Architecture:** Each template stays a standalone bash script that Claude Code runs through `#!/usr/bin/env bash`. `ruff-check.sh` maps ruff's exit codes one by one, and it confirms an exit 1 with `uv run ruff --version` before it blocks. `uv-guard.sh` finds each subcommand's command word past leading assignments and the prefix words `time`, `env` and `command`, and it matches the word's last path part. A new `hooks/test_project_hooks.py` runs each template through its shebang with a shim directory first on `PATH`: `bash`, `jq` and a stub `uv`. Each test runs once with the bash on the test's `PATH` and once with `/bin/bash`.

**Tech Stack:** bash (3.2 floor), jq, pytest under Python 3.13 and `/usr/bin/python3` (3.9), uv to run the suite. Markdown for `hooks/README.md` and `README.md`. TOML for `build/suites.toml`.

**Spec:** none. The requirement is the deferred item that the Background defines. Its Done when is the bar: "(a)–(c) land, with the new tests passing on both interpreters."

## Background

Labels used below, each expanded here once:
- **X8** is finding X8 of the repo audit of 2026-10-03 (`specs/completed/audit-3-10-26.md`). The three project tooling hook templates misread a broken toolchain as lint, miss common ways to run Python, and have no tests.
- **The item** is the deferred item "Fix and test the three hook templates (audit-3-10-26 X8, …)" in `specs/deferred_items.md`, section `## audit-3-10-26 routing (no plan; re-verification pass, branch claude/quizzical-hermann-814d89) — 2026-10-18`. Its part (a) is Task 1, part (b) is Task 2, and part (c), the tests, runs through Tasks 1 to 3. Its last sentence, the citation restamp, is Task 4.
- **The templates** are `hooks/ruff-fix.sh`, `hooks/ruff-check.sh` and `hooks/uv-guard.sh`. The owner copies them into Python/uv work repos (`hooks/README.md`, "Install into a work repo"). They are not wired into this repo.
- **The bash 3.2 floor.** `#!/usr/bin/env bash` runs the first `bash` on `PATH`. An app launched from the Dock can inherit launchd's `PATH` (`/usr/bin:/bin:/usr/sbin:/sbin`, per `hooks/README.md`), and there that is macOS's `/bin/bash` 3.2.57. So the templates must run on bash 3.2.
- **The 3.9 floor.** `build/suites.toml` runs the hooks suite twice, `pythons = ['3.13', '/usr/bin/python3']`, and `/usr/bin/python3` is 3.9.6. So the new test file must be 3.9-compatible.
- **A cc-guide citation** is a `# cc-guide: <section ids> @<release>` line that names the sections of `specs/guides/claude-code-customization-guide.md` a file relies on. `build/cc_guide/cli.py lint` prints `STALE` for a file whose cited section changed after its stamp. `cli.py baseline cite <file>` restamps a reviewed file. It reads the working tree and refuses an untracked file.

## Global Constraints

- **Where to execute.** Run on branch `claude/plan-61-hook-templates-2b1b91`, which holds this plan's commit, or on a branch cut from it, in its own worktree. Never execute in the shared checkout `~/Projects/agent-skills`. Before Task 1, `test -f specs/plans/61-hook-template-fixes.md` must exit 0.
- **Run every command from the worktree root**, with the relative paths this plan gives. Never `cd`: a Bash `cd` persists and moves the session's working directory. The pytest commands use `uv run --directory hooks`.
- **The templates are not installed here** (`hooks/README.md`: "do **not** add these to this repo's settings"). Never add them to `.claude/settings.json`, `.claude/settings.local.json` or `~/.claude`.
- **Keep the `stop_hook_active` early exit** in `hooks/ruff-check.sh` and its comment's one-attempt rule (D1). `build/check_conformance.py`'s `stop-hook-guard` check also needs the script to read `stop_hook_active`.
- **Bash 3.2 floor for the templates.** No `${x,,}` or `${x^^}`, `mapfile` or `readarray`, `declare -A`, `|&`, `&>>` or `;&`. Expand no variable unquoted where it can glob or split. Check the new code with the `system-bash` test runs.
- **3.9 floor for `hooks/test_project_hooks.py`.** Stdlib plus pytest only. No `X | Y` type unions, no `match`, no parenthesized context managers, no `zip(strict=)`.
- **No test runs a real uv or ruff, or reaches the network.** A test that needs uv uses `write_uv_stub`. A test that needs uv to be missing writes no stub.
- **Assert exit codes on every path.** A hook that exits 1 is a non-blocking error, so a crashed hook allows everything. Allow-path tests assert `returncode == 0`. Block tests assert `returncode == 2` and the stderr marker, because a bash syntax error also exits 2.
- **Do not rewrite how the README says `uv-guard.sh` splits a command.** Keep "It splits on `&& || ; | &`" in `hooks/README.md` as it is. A prior verifier flagged it wrongly (brief, 2026-10-21).
- **No README sentence may say that only exit 2 blocks.** `hooks/README.md` documents a `permissionDecision` deny, so `check_conformance.py`'s `hook-readme-exit-claims` check fails such a sentence.
- **File modes.** The three templates keep git mode `100755`. `hooks/test_project_hooks.py` is `100644`, like `hooks/test_readonly_agent_guard.py`. After each edit, `git diff --summary <file>` prints no `mode change` line.
- **Leave `specs/deferred_items.md` alone.** Plans 59 and 60 also tick items in it. The plan completion protocol ticks this plan's item (brief, 2026-10-21).
- **Prose.** README edits follow `rules/write-with-asd-ste100.md` (plain technical English). Change only the text this plan's Replace blocks name.
- **Python style:** single quotes, f-strings, lines of 100 characters or fewer.
- **Test counts are deltas** (+N), never absolute pytest totals.
- **Every commit passes the nine commit lints.** `build/githooks/pre-commit` runs `build/run_commit_lints.sh` on each commit, since the repo config sets `core.hooksPath`. A lint failure stops the commit: fix the cause, then commit again.
- **Commit trailer:** the executing session's own `Co-Authored-By:` line, as a second `-m`. Subagent-authored commits keep that same line. Check it with `git log -1 --format=%B`.
- **Expand every bare label at first use** (owner preference) in reports for the owner.
- **No push and no PR** without the owner's go-ahead.

## Decisions

- **D1** (owner, brief, 2026-10-13): `ruff-check.sh` keeps one attempt per turn. When `stop_hook_active` is set, it exits 0 without re-running ruff, and its comment says so. Applied in: Global Constraints, Task 1.
- **D2** (owner, brief, 2026-10-21): the item's disposition is Plan, with no brainstorming and no spec. The item's text is the requirement, and its Done when is the bar. Applied in: header.

## Defaults for review

This plan settles these defaults. The owner approves or changes each at plan review, and an approved default becomes a Decision.

- **P1. "ruff unavailable" exits 1.** Exit 1 is a non-blocking error, and the guide says its first stderr line "surfaces in the transcript" (`hooks.exit-codes`). Exit 0 would hide the message. A JSON `systemMessage` reaches the user only in the CLI, not in the Desktop app. Not verified: whether the Desktop app shows the exit-1 line.
- **P2. The `uv run ruff --version` probe runs only after an exit 1.** A clean tree costs no extra call.
- **P3. `uv-guard.sh` skips only leading `VAR=value` words and the prefix words `time`, `env` and `command`**, as the item lists. Options after them (`env -i`, `time -p`) and other prefixes (`exec`, `nohup`, `nice`, `sudo`, `xargs`) stay gaps. The README names them, and the `DOCUMENTED_GAPS` tests pin them. `command -v python` therefore stays allowed.
- **P4. The command word matches by its last path part:** the regex `^python[0-9.]*$`, or exactly `pytest`. This replaces the item's `*/python*` glob, which would also block `./tools/python-lint.sh`. So `.venv/bin/python` and `/usr/bin/python3` are blocked, and `ipython`, `python3-config` and `./tools/python-lint.sh` pass.
- **P5. The suggestion keeps the skipped words in front.** `FOO=1 python x.py` gets `FOO=1 uv run python x.py`. A path drops to its last part: `.venv/bin/python x.py` gets `uv run python x.py`.
- **P6. One test file, `hooks/test_project_hooks.py`.** Each test runs under the `PATH` bash and under `/bin/bash`. The file carries a cc-guide citation like its sibling test, because its exit-code assertions rest on the guide (`build/CLAUDE.md`: "Files whose correctness rests on a Claude Code fact carry a citation comment").
- **P7. `README.md` gets two small edits:** the `ruff-check.sh` row names the unavailable path, and "a first-token heuristic" becomes "a command-word heuristic".

---

## Planning record

Facts measured on 2026-10-21 at `0fd27b6`:

- In a project that cannot sync (offline, with a dependency that cannot resolve), `uv run ruff check .` exits 1 with "No solution found when resolving dependencies". That is the same code as ruff's "violations found". `uv run` exits 2 when it cannot start ruff ("Failed to spawn: ruff"). A shell with no uv exits 127. By ruff's documentation, ruff exits 0 when clean, 1 on violations and 2 on abnormal termination. That was not re-run here, because an offline `uvx` could not resolve ruff.
- So an exit 1 alone does not prove that ruff ran. Task 1 confirms it with `uv run ruff --version`.
- macOS's `/usr/bin/sed` turns `\n` in a replacement into a newline, as GNU sed does. So `uv-guard.sh`'s split works on both.
- `/bin/bash` is 3.2.57. macOS 26 ships `/usr/bin/jq` (jq-1.7.1-apple), so jq is on launchd's `PATH`. uv is not, because it is in `/opt/homebrew/bin`. On that `PATH`, `ruff-check.sh` after Task 1 reports "ruff unavailable" instead of blocking the stop, and `ruff-fix.sh` stays silent, as designed.
- The guide's `hooks.pitfalls` says `onFailure: "block"` "has no effect on `Stop`". So an exit 1 from `ruff-check.sh` never blocks, whatever the work repo sets.
- Base state: `cli.py lint` exits 0, with 3 STALE files, none under `hooks/` and not `README.md`. `check_conformance.py` exits 0. `run_suites.py --check` prints `suite registry ok`.
- Prototype: the code in Tasks 1 to 3 ran in a scratch copy of `hooks/` outside the repo. It passed 122 of 122 under Python 3.13 and under `/usr/bin/python3`, with both bashes, and none skipped. Against the current templates the same tests gave 36 failures: 8 from Task 1, 28 from Task 2 and 0 from Task 3. Changing the last `exit 0` of `uv-guard.sh` and `ruff-fix.sh` to `exit 1` failed 50 tests.

## File Structure

| File | Task | Change |
|---|---|---|
| `hooks/test_project_hooks.py` | 1, 2, 3 | Create: the harness and the `ruff-check.sh` tests (1); append the `uv-guard.sh` tests (2) and the `ruff-fix.sh` tests (3) |
| `hooks/ruff-check.sh` | 1 | Replace: exit-code mapping and the `--version` probe |
| `hooks/uv-guard.sh` | 2 | Replace: the command-word finder and its header comment |
| `hooks/README.md` | 1, 2, 3 | Edit: script table row, install check, exit-codes bullet (1); Limitations bullet (2); new Tests section (3) |
| `README.md` | 1, 2 | Edit: the `ruff-check.sh` row (1); "first-token heuristic" (2) |
| `build/suites.toml` | 3 | Edit: the hooks suite's notes |
| all cited files above | 4 | Restamp the cc-guide citations, then run every gate |

Not touched: `hooks/ruff-fix.sh` (tests only), `hooks/test_readonly_agent_guard.py`, `specs/deferred_items.md`, any settings file.

---

### Task 1: `ruff-check.sh` blocks only on lint

**Files:**
- Create: `hooks/test_project_hooks.py`
- Modify: `hooks/ruff-check.sh` (whole file)
- Modify: `hooks/README.md:35`, `hooks/README.md:74-75`, `hooks/README.md:108-109`
- Modify: `README.md:173`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces, in `hooks/test_project_hooks.py`, for Tasks 2 and 3:
  - constants `HOOKS`, `RUFF_CHECK`, `RUFF_FIX`, `UV_GUARD` (each a `Path`), `JQ`, `SYSTEM_PATH = '/usr/bin:/bin'`, `SYSTEM_BASH = '/bin/bash'`;
  - fixture `shim` (params `path-bash`, `system-bash`): a `Path` to `tmp_path / 'bin'`, holding `bash` and `jq` symlinks;
  - fixture `ruff_shim`: the same `Path`, skipped when `SYSTEM_PATH` holds a uv;
  - `child_env(shim) -> dict`; `run_hook(script, payload, shim) -> subprocess.CompletedProcess` (stdin is `json.dumps(payload)`, text mode, cwd `shim.parent`);
  - `write_uv_stub(shim, check_status=0, check_output='', version_status=0) -> None`: `uv run ruff --version` exits `version_status`, and any other call prints `check_output` and exits `check_status`. Each call appends its arguments as one line to `shim / 'uv.log'`;
  - `uv_calls(shim) -> list` of those lines, `[]` when uv never ran.
- Produces, in `hooks/ruff-check.sh`: exit 0 when clean or inside a hook-driven continuation; exit 2 with first stderr line `ruff check found issues that need a human/Claude fix (not auto-fixable):` on lint; exit 1 with first stderr line `ruff-check: ruff unavailable (exit <N>), so lint was not checked.` otherwise, where `<N>` is the exit status of `uv run ruff check .`.

- [ ] **Step 1: Write the failing tests**

Create `hooks/test_project_hooks.py` with exactly this content:

```python
# cc-guide: hooks.events hooks.exit-codes hooks.pitfalls @2.1.306
"""Contract tests for the project tooling hook templates — run from this directory, both ways.

cd hooks
uv run --python 3.13 --with pytest python -m pytest -q
uv run --python /usr/bin/python3 --with pytest python -m pytest -q

Each test drives a template as Claude Code does: through its own
`#!/usr/bin/env bash` shebang, with a hook payload on stdin. The child PATH is
a shim directory, then /usr/bin:/bin. The shim holds `bash`, `jq` and, where a
test wants one, a stub `uv` that logs its arguments and exits as told, so no
test runs a real uv or ruff or needs the network. Each test runs twice: with
the bash on this test's PATH, then with /bin/bash, macOS's bash 3.2, which
`#!/usr/bin/env bash` reaches on launchd's PATH.

A hook that exits 1 is a non-blocking error, so a crashed hook allows
everything: allow-path tests assert the exit code, and block tests also assert
the stderr marker, since a bash syntax error exits 2 too. Stdlib plus pytest,
and 3.9-compatible: the suite also runs under /usr/bin/python3.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parent
RUFF_CHECK = HOOKS / 'ruff-check.sh'
RUFF_FIX = HOOKS / 'ruff-fix.sh'
UV_GUARD = HOOKS / 'uv-guard.sh'

JQ = shutil.which('jq')
# Every child PATH ends with these. The shim, not they, decides whether uv exists.
SYSTEM_PATH = '/usr/bin:/bin'
# macOS's bash 3.2: the bash `#!/usr/bin/env bash` finds on launchd's PATH.
SYSTEM_BASH = '/bin/bash'

pytestmark = pytest.mark.skipif(
    JQ is None, reason='the project hooks read their payload with jq, and jq is not on PATH')


@pytest.fixture(params=['path-bash', 'system-bash'])
def shim(request, tmp_path):
    """A directory with bash and jq that goes first on each hook's PATH."""
    bash = shutil.which('bash') if request.param == 'path-bash' else SYSTEM_BASH
    if bash is None or not Path(bash).is_file():
        pytest.skip(f'no bash for {request.param}')
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    (bin_dir / 'bash').symlink_to(bash)
    (bin_dir / 'jq').symlink_to(JQ)
    return bin_dir


@pytest.fixture
def ruff_shim(shim):
    """The shim, for hooks that call uv: only a stub may answer for it."""
    if shutil.which('uv', path=SYSTEM_PATH) is not None:
        pytest.skip(f'{SYSTEM_PATH} holds a uv, so a test cannot control which uv runs')
    return shim


def child_env(shim):
    return dict(os.environ, PATH=f'{shim}:{SYSTEM_PATH}')


def run_hook(script, payload, shim):
    return subprocess.run([str(script)], input=json.dumps(payload), capture_output=True,
                          text=True, env=child_env(shim), cwd=str(shim.parent))


def write_uv_stub(shim, check_status=0, check_output='', version_status=0):
    """A stub uv that appends its arguments to uv.log, one call per line.

    `uv run ruff --version` exits version_status. Any other call prints
    check_output and exits check_status.
    """
    (shim / 'check.out').write_text(check_output)
    stub = shim / 'uv'
    stub.write_text(
        '#!/bin/sh\n'
        f'printf \'%s\\n\' "$*" >> "{shim}/uv.log"\n'
        f'[ "$*" = "run ruff --version" ] && exit {version_status}\n'
        f'cat "{shim}/check.out"\n'
        f'exit {check_status}\n')
    stub.chmod(0o755)


def uv_calls(shim):
    log = shim / 'uv.log'
    return log.read_text().splitlines() if log.exists() else []


def test_the_shebang_runs_the_shim_bash(shim, tmp_path):
    probe = tmp_path / 'bash-version.sh'
    probe.write_text('#!/usr/bin/env bash\necho "$BASH_VERSION"\n')
    probe.chmod(0o755)
    want = subprocess.run([str(shim / 'bash'), '-c', 'echo "$BASH_VERSION"'],
                          capture_output=True, text=True, check=True).stdout
    got = subprocess.run([str(probe)], capture_output=True, text=True,
                         env=child_env(shim), check=True).stdout
    assert got == want


# --- ruff-check.sh (Stop) -------------------------------------------------------

LINT = 'bad.py:1:8: F401 [*] `os` imported but unused\nFound 1 error.\n'


def stop_payload(active=False):
    return {'hook_event_name': 'Stop', 'stop_hook_active': active}


def test_ruff_check_skips_a_hook_driven_continuation(ruff_shim):
    write_uv_stub(ruff_shim, check_status=1, check_output=LINT)
    proc = run_hook(RUFF_CHECK, stop_payload(active=True), ruff_shim)
    assert proc.returncode == 0, proc.stderr
    assert uv_calls(ruff_shim) == []


def test_ruff_check_passes_a_clean_tree(ruff_shim):
    write_uv_stub(ruff_shim, check_status=0)
    proc = run_hook(RUFF_CHECK, stop_payload(), ruff_shim)
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr == ''
    assert uv_calls(ruff_shim) == ['run ruff check .']


def test_ruff_check_blocks_on_lint(ruff_shim):
    write_uv_stub(ruff_shim, check_status=1, check_output=LINT)
    proc = run_hook(RUFF_CHECK, stop_payload(), ruff_shim)
    assert proc.returncode == 2, proc.stderr
    assert proc.stderr.startswith('ruff check found issues')
    assert 'F401' in proc.stderr


def test_ruff_check_confirms_an_exit_1_with_ruff_version(ruff_shim):
    write_uv_stub(ruff_shim, check_status=1, check_output=LINT)
    run_hook(RUFF_CHECK, stop_payload(), ruff_shim)
    assert uv_calls(ruff_shim) == ['run ruff check .', 'run ruff --version']


@pytest.mark.parametrize('check_status, version_status, calls', [
    # uv run cannot sync the project, so both calls exit 1.
    pytest.param(1, 1, ['run ruff check .', 'run ruff --version'], id='sync-failure'),
    # ruff's own exit 2 (a bad config, an internal error), or uv cannot spawn ruff.
    pytest.param(2, 2, ['run ruff check .'], id='exit-2'),
])
def test_ruff_check_reports_a_ruff_that_cannot_run(ruff_shim, check_status, version_status, calls):
    write_uv_stub(ruff_shim, check_status=check_status, check_output='error: stub failure\n',
                  version_status=version_status)
    proc = run_hook(RUFF_CHECK, stop_payload(), ruff_shim)
    assert proc.returncode == 1, proc.stderr
    assert proc.stderr.splitlines()[0] == (
        f'ruff-check: ruff unavailable (exit {check_status}), so lint was not checked.')
    assert 'error: stub failure' in proc.stderr
    assert uv_calls(ruff_shim) == calls


def test_ruff_check_reports_a_missing_uv(ruff_shim):
    proc = run_hook(RUFF_CHECK, stop_payload(), ruff_shim)  # no stub, so no uv on PATH
    assert proc.returncode == 1, proc.stderr
    assert proc.stderr.splitlines()[0] == (
        'ruff-check: ruff unavailable (exit 127), so lint was not checked.')
```

- [ ] **Step 2: Run the tests to verify the predicted failures**

Run: `uv run --directory hooks --python 3.13 --with pytest python -m pytest -q -rfs test_project_hooks.py`

Expected: `8 failed, 8 passed`, and no skips. The 8 failures are these four tests, each once for `path-bash` and once for `system-bash`:
- `test_ruff_check_confirms_an_exit_1_with_ruff_version`: the call log lacks `'run ruff --version'`.
- `test_ruff_check_reports_a_ruff_that_cannot_run[…-sync-failure]` and `[…-exit-2]`: `assert 2 == 1`.
- `test_ruff_check_reports_a_missing_uv`: `assert 2 == 1`, with "uv: command not found" under "ruff check found issues" in stderr. That is the bug.

Read each failure. A failure for any other reason (an import error, a skip, a stub that did not run) means the harness is wrong: fix it before Step 3. A test that passes here and is not in the 8 is expected: it pins behaviour the current hook already has.

- [ ] **Step 3: Replace `hooks/ruff-check.sh`**

Replace the whole file with exactly this content. The `stop_hook_active` lines and the "One attempt per turn" comment are unchanged (D1).

```bash
#!/usr/bin/env bash
# cc-guide: hooks.events hooks.exit-codes hooks.patterns @2.1.306
# Stop hook — before the turn ends, surface ruff lint errors that --fix could not
# auto-resolve (e.g. undefined names, unused-but-referenced, complexity rules).
#
# Exit 2 feeds stderr back to Claude so it fixes them and continues.
# Only lint blocks. ruff exits 1 when it finds violations, but `uv run` also exits 1
# when it cannot sync the project, so an exit 1 blocks only once
# `uv run ruff --version` shows ruff can start. Any other failure (no uv: 127; ruff
# missing from the project, or a bad config: 2) exits 1 with "ruff unavailable" on
# the first stderr line: a non-blocking error, and the transcript shows that line.
# One attempt per turn: when `stop_hook_active` is set, exit 0 without re-running
# ruff, so the fix is not re-checked until the next turn ends. This gives up a
# guaranteed-clean stop in exchange for never looping.
#
# Install into a real Python/uv repo (see README.md). Reads hook JSON on stdin.
set -uo pipefail

input=$(cat)
active=$(printf '%s' "$input" | jq -r '.stop_hook_active // false')
[ "$active" = "true" ] && exit 0   # already inside a hook-driven continuation

unavailable() {   # $1 = exit status, $2 = output; reports without blocking
  {
    echo "ruff-check: ruff unavailable (exit $1), so lint was not checked."
    echo "$2"
  } >&2
  exit 1
}

out=$(uv run ruff check . 2>&1)
status=$?

[ "$status" -eq 0 ] && exit 0
[ "$status" -eq 1 ] || unavailable "$status" "$out"
uv run ruff --version >/dev/null 2>&1 || unavailable "$status" "$out"

{
  echo "ruff check found issues that need a human/Claude fix (not auto-fixable):"
  echo "$out"
} >&2
exit 2
```

Then run `git diff --summary hooks/ruff-check.sh`. Expected: no output, so the mode is still `100755`.

- [ ] **Step 4: Run the tests on both interpreters**

Run: `uv run --directory hooks --python 3.13 --with pytest python -m pytest -q -rfs test_project_hooks.py`
Expected: `16 passed`.

Run: `uv run --directory hooks --python /usr/bin/python3 --with pytest python -m pytest -q -rfs test_project_hooks.py`
Expected: `16 passed`.

- [ ] **Step 5: Update the docs**

In `hooks/README.md`, replace:

```markdown
| `ruff-check.sh` | `Stop` | `uv run ruff check .`; exit 2 feeds unfixable lint back to Claude. Guarded by `stop_hook_active` against loops. |
```

with:

```markdown
| `ruff-check.sh` | `Stop` | `uv run ruff check .`; exit 2 feeds unfixable lint back to Claude. Guarded by `stop_hook_active` against loops. When ruff cannot run, it exits 1 with "ruff unavailable" and does not block. |
```

In `hooks/README.md`, replace:

```markdown
(uv-guard should block it) and to end a turn with a lint error in a `.py` file
(ruff-check should block the stop).
```

with:

```markdown
(uv-guard should block it) and to end a turn with a lint error in a `.py` file
(ruff-check should block the stop). If the transcript shows "ruff unavailable" instead,
ruff could not run in that repo. Then `uv` is not on the hook's `PATH`, the project does
not sync, or ruff is not one of its dev dependencies.
```

In `hooks/README.md`, replace:

```markdown
  return JSON decisions with exit 0. `uv-guard.sh` and `ruff-check.sh` block with exit 2;
  `ruff-fix.sh` never blocks.
```

with:

```markdown
  return JSON decisions with exit 0. `uv-guard.sh` and `ruff-check.sh` block with exit 2;
  `ruff-fix.sh` never blocks. When ruff cannot run, `ruff-check.sh` exits 1, so it reports
  the failure and does not block.
```

In `README.md`, replace:

```markdown
| [`ruff-check.sh`](hooks/ruff-check.sh) | `Stop` | Runs `uv run ruff check .`. Exit 2 feeds back to Claude whatever `--fix` could not resolve. `stop_hook_active` guards it against loops. |
```

with:

```markdown
| [`ruff-check.sh`](hooks/ruff-check.sh) | `Stop` | Runs `uv run ruff check .`. Exit 2 feeds back to Claude whatever `--fix` could not resolve. `stop_hook_active` guards it against loops. When ruff cannot run, it exits 1 with "ruff unavailable", which does not block. |
```

Each old block occurs exactly once. Then run `uv run --python 3.13 --with pyyaml python build/check_conformance.py`. Expected: exit 0.

- [ ] **Step 6: Commit**

```bash
git add hooks/test_project_hooks.py hooks/ruff-check.sh hooks/README.md README.md
git commit -m "fix(hooks): block ruff-check only on lint, report a ruff that cannot run"
```

Expected: the pre-commit lints pass and the commit lands. Hooks suite: +16 tests on each interpreter.

---

### Task 2: `uv-guard.sh` finds the command word

**Files:**
- Modify: `hooks/test_project_hooks.py` (append)
- Modify: `hooks/uv-guard.sh` (whole file)
- Modify: `hooks/README.md:90-94`
- Modify: `README.md:191`

**Interfaces:**
- Consumes from Task 1: fixture `shim`, `run_hook(script, payload, shim)`, `UV_GUARD`.
- Produces, in `hooks/uv-guard.sh`: exit 2 with stderr `uv-guard: <message>\n` for a blocked command, and exit 0 with empty stderr otherwise. The messages are `use '<skipped words>uv run <last path part><args>' instead of bare '<command word>' (uv-managed project).` for python, and `use '<skipped words>uv run pytest<args>' instead of bare '<command word>'.` for pytest. The pip message is unchanged.

- [ ] **Step 1: Write the failing tests**

Append this block to the end of `hooks/test_project_hooks.py`, after two blank lines:

```python
# --- uv-guard.sh (PreToolUse on Bash) -------------------------------------------

def bash_payload(command):
    return {'hook_event_name': 'PreToolUse', 'tool_name': 'Bash',
            'tool_input': {'command': command}}


# Blocked before this plan: the first token of a subcommand is python, python3 or
# pytest, or the command holds a pip install.
BLOCKED_BY_FIRST_TOKEN = [
    'python x.py',
    'python3 -c "print(1)"',
    'pytest -q',
    'cd src && python x.py',
    'cat x | python -',
    'pip install requests',
    'uv run python -m pip install requests',
]
# The leaks: a versioned name, a path, or a prefix before the command word.
BLOCKED_PAST_PREFIXES = [
    'python3.13 x.py',
    '.venv/bin/python x.py',
    '/usr/bin/python3 x.py',
    '.venv/bin/pytest -q',
    'FOO=1 python x.py',
    'FOO=1 BAR=2 pytest',
    'time pytest -q',
    'env python x.py',
    'env FOO=1 python x.py',
    'command python x.py',
    'ls && time python3.12 x.py',
]
ALLOWED = [
    'uv run python x.py',
    'uv run pytest -q',
    'uvx ruff check .',
    'FOO=1 uv run python x.py',
    'time uv run pytest -q',
    'echo python',
    'which python',
    'command -v python',
    'command -V python3',
    'env',
    'env | grep PATH',
    'ls python/ && cat pytest.ini',
    'ipython',
    'python3-config --prefix',
    './tools/python-lint.sh',
    'git commit -m "python fix"',
    'python x.py  # no-uv-guard',
]


@pytest.mark.parametrize('command', BLOCKED_BY_FIRST_TOKEN + BLOCKED_PAST_PREFIXES)
def test_uv_guard_blocks(shim, command):
    proc = run_hook(UV_GUARD, bash_payload(command), shim)
    assert proc.returncode == 2, proc.stderr
    assert proc.stderr.startswith('uv-guard: ')


@pytest.mark.parametrize('command', ALLOWED)
def test_uv_guard_allows(shim, command):
    proc = run_hook(UV_GUARD, bash_payload(command), shim)
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr == ''


def test_uv_guard_allows_a_payload_without_a_command(shim):
    proc = run_hook(UV_GUARD, {'hook_event_name': 'PreToolUse', 'tool_name': 'Bash',
                               'tool_input': {}}, shim)
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr == ''


# hooks/README.md names these gaps. When one closes, move it to BLOCKED_PAST_PREFIXES
# and drop it from the README's list.
DOCUMENTED_GAPS = [
    'env -i python x.py',
    'time -p pytest',
    'nohup python x.py',
    'FOO="a b" python x.py',
    '(python x.py)',
    'bash -c "python x.py"',
]


@pytest.mark.parametrize('command', DOCUMENTED_GAPS)
def test_uv_guard_lets_the_documented_gaps_through(shim, command):
    proc = run_hook(UV_GUARD, bash_payload(command), shim)
    assert proc.returncode == 0, proc.stderr


@pytest.mark.parametrize('command, message', [
    pytest.param('python x.py',
                 "use 'uv run python x.py' instead of bare 'python' (uv-managed project).",
                 id='python'),
    pytest.param('pytest -q', "use 'uv run pytest -q' instead of bare 'pytest'.", id='pytest'),
    pytest.param('FOO=1 python x.py',
                 "use 'FOO=1 uv run python x.py' instead of bare 'python' (uv-managed project).",
                 id='assignment'),
    pytest.param('.venv/bin/python x.py',
                 "use 'uv run python x.py' instead of bare '.venv/bin/python' "
                 '(uv-managed project).',
                 id='path'),
    pytest.param('time pytest -q', "use 'time uv run pytest -q' instead of bare 'pytest'.",
                 id='time'),
])
def test_uv_guard_suggests_the_uv_form(shim, command, message):
    proc = run_hook(UV_GUARD, bash_payload(command), shim)
    assert proc.returncode == 2, proc.stderr
    assert proc.stderr == f'uv-guard: {message}\n'
```

- [ ] **Step 2: Run the tests to verify the predicted failures**

Run: `uv run --directory hooks --python 3.13 --with pytest python -m pytest -q -rfs test_project_hooks.py -k uv_guard`

Expected: `28 failed, 66 passed`, and no skips. The failures, each once per bash variant:
- `test_uv_guard_blocks` for each of the 11 `BLOCKED_PAST_PREFIXES` commands: `assert 0 == 2`, because the current hook lets them through.
- `test_uv_guard_suggests_the_uv_form[…-assignment]`, `[…-path]` and `[…-time]`: `assert 0 == 2`.

Read each failure. Every `BLOCKED_BY_FIRST_TOKEN`, `ALLOWED` and `DOCUMENTED_GAPS` case passes here, and so do the `python` and `pytest` message cases: they pin behaviour the current hook has.

- [ ] **Step 3: Replace `hooks/uv-guard.sh`**

Replace the whole file with exactly this content:

```bash
#!/usr/bin/env bash
# cc-guide: hooks.events hooks.exit-codes hooks.patterns @2.1.306
# PreToolUse(Bash) — enforce uv-first tooling. Blocks (exit 2) the clearest
# violations and injects the corrected form into Claude's context, so the model
# retries with the right command instead of you re-explaining it every session.
#
# Blocks:  pip install ...           -> use `uv add <pkg>`
#          <bare> python[3[.13]] ... -> use `uv run python ...`
#          <bare> pytest ...         -> use `uv run pytest ...`
#          A path counts by its last part (.venv/bin/python is python), and so
#          does a command word behind VAR=value words or time, env and command.
# Allows:  anything already under `uv run` / `uvx`, and anything where those
#          tokens appear as non-leading words (echo, which, comments, etc.).
#
# Escape hatch: put the literal string `no-uv-guard` anywhere in the command.
#
# Heuristic, not a parser: it splits on && || ; | & and checks each subcommand's
# command word: its first token once leading VAR=value assignments and the prefix
# words time, env and command are skipped. Good enough for the common cases; tune
# per-repo. Reads JSON stdin.
set -uo pipefail

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')
[ -z "$cmd" ] && exit 0

# opt-out
case "$cmd" in *no-uv-guard*) exit 0 ;; esac

block() { printf 'uv-guard: %s\n' "$1" >&2; exit 2; }

# pip install, anywhere in the command (incl. `python -m pip install`)
if printf '%s' "$cmd" | grep -Eq '(^|[^[:alnum:]_])pip[0-9]*[[:space:]]+install'; then
  block "this project is uv-managed — use 'uv add <pkg>' instead of 'pip install'."
fi

assign_re='^[A-Za-z_][A-Za-z0-9_]*='   # a VAR=value word
python_re='^python[0-9.]*$'            # python, python3, python3.13

# check the command word of each subcommand
norm=$(printf '%s' "$cmd" | sed -E 's/(\&\&|\|\||;|\||&)/\n/g')
while IFS= read -r sub; do
  sub="${sub#"${sub%%[![:space:]]*}"}"          # ltrim
  [ -z "$sub" ] && continue
  lead=''                                       # skipped words, kept for the suggestion
  rest=$sub
  while [ -n "$rest" ]; do
    word=${rest%%[[:space:]]*}
    case "$word" in
      time|env|command) ;;
      *) [[ $word =~ $assign_re ]] || break ;;
    esac
    lead="$lead$word "
    rest=${rest#"$word"}
    rest="${rest#"${rest%%[![:space:]]*}"}"     # ltrim
  done
  first=${rest%%[[:space:]]*}
  args=${rest#"$first"}
  base=${first##*/}                             # .venv/bin/python -> python
  if [[ $base =~ $python_re ]]; then
    block "use '${lead}uv run ${base}${args}' instead of bare '${first}' (uv-managed project)."
  elif [ "$base" = pytest ]; then
    block "use '${lead}uv run pytest${args}' instead of bare '${first}'."
  fi
done <<EOF
$norm
EOF
exit 0
```

Then run `git diff --summary hooks/uv-guard.sh`. Expected: no output.

- [ ] **Step 4: Run the tests on both interpreters**

Run: `uv run --directory hooks --python 3.13 --with pytest python -m pytest -q -rfs test_project_hooks.py`
Expected: `110 passed`.

Run: `uv run --directory hooks --python /usr/bin/python3 --with pytest python -m pytest -q -rfs test_project_hooks.py`
Expected: `110 passed`.

- [ ] **Step 5: Update the docs**

In `hooks/README.md`, replace:

```markdown
- **`uv-guard.sh` is a heuristic, not a shell parser.** It splits on `&& || ; | &` and
  checks each subcommand's *first* token, so `uv run python x.py`, `echo python`, and
  `which python` pass, while `python x.py` and `cat x | python -` are blocked. A
  `python` invoked deeper inside a quoted string could slip through — acceptable for a
  guardrail. Drop the `pytest)` case if you run pytest outside uv anywhere.
```

with:

```markdown
- **`uv-guard.sh` is a heuristic, not a shell parser.** It splits on `&& || ; | &` and
  checks each subcommand's command word. That is its first token after any leading
  `VAR=value` assignments and the prefix words `time`, `env` and `command`. A path
  counts by its last part, so `.venv/bin/python` is `python`, and a version suffix
  (`python3.13`) still matches. So `uv run python x.py`, `echo python`, `which python`
  and `command -v python` pass, while `python x.py`, `FOO=1 python x.py`,
  `time pytest -q` and `cat x | python -` are blocked. These can still slip through,
  which is acceptable for a guardrail:
  - an option of a prefix word: `env -i python x.py`, `time -p pytest`
  - another prefix command: `exec`, `nohup`, `nice`, `sudo`, `xargs`
  - an assignment whose quoted value holds a space: `FOO="a b" python x.py`
  - a subshell, `$(…)` or backticks: `(python x.py)`
  - a `python` inside a quoted string: `bash -c "python x.py"`

  `DOCUMENTED_GAPS` in `test_project_hooks.py` pins this list. Drop the `pytest` branch
  if you run pytest outside uv anywhere.
```

In `README.md`, replace:

```markdown
and each script's known limits. One notable limit: `uv-guard.sh` is a first-token heuristic, not a
```

with:

```markdown
and each script's known limits. One notable limit: `uv-guard.sh` is a command-word heuristic, not a
```

Each old block occurs exactly once. Then run `uv run --python 3.13 --with pyyaml python build/check_conformance.py`. Expected: exit 0.

- [ ] **Step 6: Commit**

```bash
git add hooks/test_project_hooks.py hooks/uv-guard.sh hooks/README.md README.md
git commit -m "fix(hooks): find uv-guard's command word past prefixes, versions and paths"
```

Expected: the commit lands. Hooks suite: +94 tests on each interpreter.

- [ ] **Step 7: Mutation check (no commit)**

This proves that the allow-path tests catch a crashed hook. Change the last line of `hooks/uv-guard.sh` from `exit 0` to `exit 1`. Then run: `uv run --directory hooks --python 3.13 --with pytest python -m pytest -q test_project_hooks.py -k uv_guard`

Expected: `44 failed, 50 passed`. The 44 are every `ALLOWED` case but `python x.py  # no-uv-guard`, which exits before the last line, and every `DOCUMENTED_GAPS` case, each once per bash variant.

Then restore the committed file: `git restore hooks/uv-guard.sh`, and check that `git status --short` prints nothing.

---

### Task 3: `ruff-fix.sh` contract tests and the suite's docs

These are characterization tests: `ruff-fix.sh` does not change, so they pass at once. Step 3 proves that they can fail.

**Files:**
- Modify: `hooks/test_project_hooks.py` (append)
- Modify: `hooks/README.md:85-88` (a new section before `## Limitations (by design — tune per repo)`)
- Modify: `build/suites.toml:92-93` (the `hooks` suite's `notes`)

**Interfaces:**
- Consumes from Task 1: fixture `ruff_shim`, `run_hook`, `write_uv_stub`, `uv_calls`, `RUFF_FIX`.
- Produces: nothing that a later task uses.

- [ ] **Step 1: Write the tests**

Append this block to the end of `hooks/test_project_hooks.py`, after two blank lines:

```python
# --- ruff-fix.sh (PostToolUse on Write|Edit) ------------------------------------

def edit_payload(file_path):
    return {'hook_event_name': 'PostToolUse', 'tool_name': 'Edit',
            'tool_input': {'file_path': str(file_path)}}


def test_ruff_fix_fixes_then_formats_an_edited_python_file(ruff_shim, tmp_path):
    target = tmp_path / 'mod.py'
    target.write_text('import os\n')
    write_uv_stub(ruff_shim)
    proc = run_hook(RUFF_FIX, edit_payload(target), ruff_shim)
    assert proc.returncode == 0, proc.stderr
    assert uv_calls(ruff_shim) == [f'run ruff check --fix --quiet {target}',
                                   f'run ruff format --quiet {target}']


@pytest.mark.parametrize('name, exists', [
    pytest.param('notes.md', True, id='not-python'),
    pytest.param('gone.py', False, id='deleted'),
])
def test_ruff_fix_leaves_other_files_alone(ruff_shim, tmp_path, name, exists):
    target = tmp_path / name
    if exists:
        target.write_text('x\n')
    write_uv_stub(ruff_shim)
    proc = run_hook(RUFF_FIX, edit_payload(target), ruff_shim)
    assert proc.returncode == 0, proc.stderr
    assert uv_calls(ruff_shim) == []


def test_ruff_fix_ignores_a_payload_without_a_path(ruff_shim):
    write_uv_stub(ruff_shim)
    proc = run_hook(RUFF_FIX, {'hook_event_name': 'PostToolUse', 'tool_name': 'Write',
                               'tool_input': {}}, ruff_shim)
    assert proc.returncode == 0, proc.stderr
    assert uv_calls(ruff_shim) == []


def test_ruff_fix_never_fails_the_turn_when_ruff_fails(ruff_shim, tmp_path):
    target = tmp_path / 'mod.py'
    target.write_text('x = 1\n')
    write_uv_stub(ruff_shim, check_status=2, check_output='error: stub failure\n')
    proc = run_hook(RUFF_FIX, edit_payload(target), ruff_shim)
    assert proc.returncode == 0, proc.stderr
    assert len(uv_calls(ruff_shim)) == 2


def test_ruff_fix_never_fails_the_turn_without_uv(ruff_shim, tmp_path):
    target = tmp_path / 'mod.py'
    target.write_text('x = 1\n')
    proc = run_hook(RUFF_FIX, edit_payload(target), ruff_shim)  # no stub, so no uv on PATH
    assert proc.returncode == 0, proc.stderr
```

- [ ] **Step 2: Run the tests on both interpreters**

Run: `uv run --directory hooks --python 3.13 --with pytest python -m pytest -q -rfs test_project_hooks.py`
Expected: `122 passed`.

Run: `uv run --directory hooks --python /usr/bin/python3 --with pytest python -m pytest -q -rfs test_project_hooks.py`
Expected: `122 passed`.

- [ ] **Step 3: Mutation check (no commit)**

Change the last line of `hooks/ruff-fix.sh` from `exit 0` to `exit 1`. Then run: `uv run --directory hooks --python 3.13 --with pytest python -m pytest -q test_project_hooks.py -k ruff_fix`

Expected: `6 failed, 6 passed`. The 6 are the three tests whose hook reaches its last line (`fixes_then_formats_an_edited_python_file`, `never_fails_the_turn_when_ruff_fails`, `never_fails_the_turn_without_uv`), each once per bash variant.

Then restore the file: `git restore hooks/ruff-fix.sh`, and check that `git diff --stat hooks/ruff-fix.sh` prints nothing.

- [ ] **Step 4: Update the docs and the suite notes**

In `hooks/README.md`, replace:

```markdown
Prefer `cp` over symlinking so a hook change can't silently alter every repo at once;
re-copy when you update a template here.

## Limitations (by design — tune per repo)
```

with:

```markdown
Prefer `cp` over symlinking so a hook change can't silently alter every repo at once;
re-copy when you update a template here.

## Tests

`test_project_hooks.py` runs each template as Claude Code does: through its shebang,
with a hook payload on stdin. A stub `uv` stands in for uv and ruff, so the tests need
no network and no Python project. Each test runs twice: with the `bash` on the test's
`PATH`, and with `/bin/bash`, which is bash 3.2 on macOS. So the templates must stay
bash 3.2 compatible. The tests skip where `jq` is not installed. Run them with the two
commands under the guard's **Tests** below, which run every test in this directory.

## Limitations (by design — tune per repo)
```

In `build/suites.toml`, replace:

```toml
notes = [
    'Read-only agent guard tests (Gate A: classifier units, payload contract).',
```

with:

```toml
notes = [
    'Read-only agent guard tests (Gate A: classifier units, payload contract), and the project hook template tests (test_project_hooks.py).',
    'The template tests run each template through its shebang against a stub uv, once with the bash on PATH and once with /bin/bash (bash 3.2 on macOS). They skip where jq is not installed.',
```

Each old block occurs exactly once. Then run:
- `uv run --python 3.13 --with pyyaml python build/check_conformance.py`. Expected: exit 0.
- `uv run --python 3.13 python build/run_suites.py --list`. Expected: the `hooks` entry prints both new notes.

- [ ] **Step 5: Commit**

```bash
git add hooks/test_project_hooks.py hooks/README.md build/suites.toml
git commit -m "test(hooks): pin ruff-fix's contract and document the template tests"
```

Expected: the commit lands. Hooks suite: +12 tests on each interpreter.

---

### Task 4: Restamp the citations and run every gate

Run this task after the per-task reviews of Tasks 1 to 3. If the final review changes a cited file, run Step 1 again on that file.

**Files:**
- Modify (stamp line only, if a stamp moves): `hooks/ruff-check.sh:2`, `hooks/uv-guard.sh:2`, `hooks/README.md:1`, `README.md:1`, `hooks/test_project_hooks.py:1`

**Interfaces:**
- Consumes: the committed files of Tasks 1 to 3. `baseline cite` refuses an untracked file.
- Produces: nothing that a later task uses.

- [ ] **Step 1: Restamp each reviewed citing file**

Run: `uv run --python 3.13 python build/cc_guide/cli.py baseline cite hooks/ruff-check.sh hooks/uv-guard.sh hooks/README.md README.md hooks/test_project_hooks.py`

Expected: five lines `stamped <path> @<release>`. `<release>` is the newest `changed` release among the file's cited sections: `2.1.306` while planning.

- [ ] **Step 2: See whether a stamp moved**

Run: `git status --short`

Expected: no output when every stamp was already current. Otherwise `git diff` shows only `@<release>` changes on the citation lines.

- [ ] **Step 3: Check the file modes**

Run: `git ls-files -s hooks/ruff-check.sh hooks/ruff-fix.sh hooks/uv-guard.sh hooks/test_project_hooks.py`

Expected: `100755` for the three `.sh` files and `100644` for the test file.

- [ ] **Step 4: Run the drift lint and the conformance lint**

Run: `uv run --python 3.13 python build/cc_guide/cli.py lint`
Expected: exit 0. No `STALE` line names any of the five files. `STALE` lines go to stderr, so read the whole output.

Run: `uv run --python 3.13 --with pyyaml python build/check_conformance.py`
Expected: exit 0.

- [ ] **Step 5: Run the hooks suite on both interpreters**

Run: `uv run --python 3.13 python build/run_suites.py hooks -- -rfs`

Expected: both runs pass, with +122 tests each against the base. On macOS no test skips. Elsewhere, a `system-bash` skip or a launchd-PATH skip prints its reason.

- [ ] **Step 6: Run the nine commit lints**

Run: `bash build/run_commit_lints.sh`
Expected: exit 0.

- [ ] **Step 7: Commit, only if Step 2 showed a change**

```bash
git add hooks/ruff-check.sh hooks/uv-guard.sh hooks/README.md README.md hooks/test_project_hooks.py
git commit -m "chore(cc-guide): restamp the hook template citations after review"
```

When Step 2 showed no change, there is nothing to commit. Report that the stamps were already current at `<release>`.

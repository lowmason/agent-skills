# Superpowers Upstream Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port five small, probe-verified obra/superpowers bug fixes into this repo's adapted copies, showing each bug failing before it is fixed.

**Architecture:** Each fix is a few lines in one bundled script or one skill file, so each task is one RED → fix → GREEN cycle with its own commit. Script fixes get a pytest test that drives the script as a subprocess, in the directory-scoped convention of `skills/subagent-driven-development/scripts/test_sdd_scripts.py`; the one prose fix (an example in `systematic-debugging/SKILL.md`) is shown RED and GREEN by a probe. A final task records the adoptions in `NOTICE`.

**Tech Stack:** bash (scripts must also run under macOS's `/bin/bash` 3.2), Node (CommonJS, `server.cjs`), Python 3.13 + pytest through `uv run`.

**Spec:** none. The requirements are the "Fix directly, no spec" disposition of `specs/superpowers-drift-spec.md`: findings 8 (`find-polluter.sh`), 12 (`review-package` range guards; `sdd-workspace`'s `.gitignore`, optional) and 16 (the companion server's `String.replace`; the debugging example that prints a secret). Finding 16 and finding 12's `.gitignore` item exist only in the spec's 2026-10-18 revision, `f9ae68d` on branch `claude/superpowers-spec-staleness-f6b72d`, unmerged when this plan was written; main's copy is the 2026-10-03 revision. Tasks 1 and 2 also close item X3 of the 2026-10-03 repo audit (`specs/audit-3-10-26.md:656`). The session brief that started this plan carries the same items, with each upstream fix's commit.

## Global Constraints

- Port each fix, not upstream's file: our copies carry local changes (`find-polluter.sh` has `TEST_CMD`; the SDD workspace is `.sdd/`, not `.superpowers/sdd/`).
- Show every bug RED before its fix: a failing test, or for the SKILL.md example a probe. Read each failure's reason; a test that fails for the wrong reason is not RED.
- Run every command through `uv run --python 3.13`, as CLAUDE.md's Commands section shows. Tests are directory-scoped: `cd` into the test's directory first.
- Python style: single quotes, f-strings, 4-space indentation, stdlib only in tests (plus pytest).
- Probe the debugging example only with a dummy value under `env -i`. Never paste real environment output into any file: this repo is public.
- Cross-skill references use bare skill names.
- Run `build/run_commit_lints.sh` before each commit; it must print `commit lints passed`.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- State test counts as deltas (+N), never as totals.

## Decisions

- **D1** (owner, brief, 2026-10-18): Port the fix, not the file; `find-polluter.sh` keeps its local `TEST_CMD`. Applied in: Global Constraints, Task 1.
- **D2** (owner, brief, 2026-10-18): A pattern that matches nothing counts 0, and the script says it found no tests instead of giving an all-clear. Applied in: Task 1.
- **D3** (owner, brief, 2026-10-18): Re-anchor `root-cause-tracing.md:102` as `<this-skill-dir>/find-polluter.sh`, and add the new test suite's command to CLAUDE.md's Commands block. Applied in: Task 1.
- **D4** (owner, brief, 2026-10-18): `review-package` gets upstream's two guards, each exiting 3, with one test per guard in the existing suite. Applied in: Task 2.
- **D5** (owner, brief, 2026-10-18): The two diagnostic-example lines are replaced with upstream's version. Applied in: Task 4.
- **D6** (owner, brief, 2026-10-18): One `NOTICE` change-list entry in the superpowers block, modeled on the two "adopted FROM upstream" entries, names each piece's upstream commit or release. Applied in: Task 6.
- **D7** (owner, brief, 2026-10-18): Mark drift findings 8, 12 and 16 adopted only if the 2026-10-18 revision has merged to main when the work finishes; otherwise leave the spec alone and say so. Applied in: Task 6.

**Defaults the brief left open, settled by the planner for the owner's review** (these are not owner decisions):

- **S1:** Inline execution (executing-plans). The five fixes are one to five lines each; a fresh implementer and reviewer per task would cost more than the changes.
- **S2:** The optional item, `sdd-workspace`'s create-only `.gitignore`, is included (Task 5): one line plus one test, in the suite Task 2 already extends.
- **S3:** A brainstorm-server regression test is added (Task 3). It loads `server.cjs` through a `Module._compile` harness, so `server.cjs`'s diff stays upstream's one line, and it skips when `node` is not on PATH.
- **S4:** A pattern that matches nothing exits 2: distinct from 1 (polluter found, or a usage error) and non-zero, as audit X3 asks. Upstream instead reports "Found 0" and still leaves through its all-clear line with exit 0.
- **S5:** The SKILL.md example edit gets a RED/GREEN probe and no wording micro-test. writing-skills' Iron Law (`skills/writing-skills/SKILL.md:390-404`) covers edits, and the probe is this edit's failing test. The micro-test checklist line (`:662`) covers behavior-shaping wording; this edit changes the example's commands, not what the agent is told to do.
- **S6:** The `find-polluter.sh` tests run under `/bin/bash` and under the PATH's bash, when those differ. The shebang resolves to Homebrew bash 5.3 on the owner's machine, which cannot show whether `${TEST_PATTERN//\*\*\//}` works under macOS's bash 3.2.

---

### Task 1: find-polluter.sh — no false all-clear, and `**/` patterns match

Upstream: `6015d37` (PR #2011, fixing issue #2008) and `c8921b5`, released in v6.2.0. Bug: `find . -path "$TEST_PATTERN"` never matches a pattern without a leading `*`, because `find .` prints `./`-prefixed paths; `-path` cannot match `**/` against zero directories; and `echo "" | wc -l` counts an empty result as one file, so the run ends "✅ No polluter found - all tests clean!" with exit 0.

**Files:**
- Create: `skills/systematic-debugging/test_find_polluter.py`
- Modify: `skills/systematic-debugging/find-polluter.sh:10-11` (header: exit codes), `:30-32` (file list and count)
- Modify: `skills/systematic-debugging/root-cause-tracing.md:102`
- Modify: `CLAUDE.md` (Commands block)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: exit status 2 from `find-polluter.sh` when no test file matches. Task 6's `NOTICE` entry describes it.

- [ ] **Step 1: Write the failing tests**

Create `skills/systematic-debugging/test_find_polluter.py`:

```python
"""Tests for find-polluter.sh — run from this directory.

cd skills/systematic-debugging && uv run --python 3.13 --with pytest python -m pytest -q

The script is bash, so each test drives it as a subprocess in a throwaway git
project and asserts on the exit code, stdout, and the files a stub test runner
was handed. TEST_CMD points at that stub: it logs every file it is given and
creates the pollution marker only for the file a test names as the polluter.
Every test runs under each distinct bash found, because /bin/bash is 3.2 on
macOS while the shebang's `env bash` may resolve to a newer one.
"""

import os
import shlex
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent / 'find-polluter.sh'
MARKER = 'pollution.marker'
BASHES = sorted(
    {os.path.realpath(b) for b in ('/bin/bash', shutil.which('bash')) if b and os.path.exists(b)}
)

# Sanitised so `git init` doesn't inherit the user's global/system git config
# (init.templateDir and the like).
GIT_ENV = {**os.environ, 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1'}


@pytest.fixture
def project(tmp_path):
    """A throwaway git project: a top-level and a nested TypeScript test, and
    one pytest file a directory down."""
    root = tmp_path / 'project'
    (root / 'src' / 'sub').mkdir(parents=True)
    (root / 'tests').mkdir()
    (root / 'src' / 'top.test.ts').write_text("test('top')\n")
    (root / 'src' / 'sub' / 'b.test.ts').write_text("test('nested')\n")
    (root / 'tests' / 'test_a.py').write_text('def test_a():\n    pass\n')
    subprocess.run(['git', 'init', '-q', str(root)], check=True, env=GIT_ENV)
    return root


def make_runner(tmp_path, polluter=None):
    """Write a TEST_CMD stub outside the project. It appends each file it is
    handed to a log and, for the polluter, creates the marker in the working
    directory, as a polluting test would."""
    log = tmp_path / 'ran.log'
    runner = tmp_path / 'bin' / 'fake-test-runner'
    runner.parent.mkdir(exist_ok=True)
    lines = ['#!/bin/sh', f'printf "%s\\n" "$1" >> {shlex.quote(str(log))}']
    if polluter:
        lines.append(f'case "$1" in */{polluter}) touch {MARKER} ;; esac')
    runner.write_text('\n'.join(lines) + '\n')
    runner.chmod(0o755)
    return runner, log


def find_polluter(bash, project, pattern, runner):
    return subprocess.run(
        [bash, str(SCRIPT), MARKER, pattern],
        cwd=project,
        capture_output=True,
        text=True,
        env={**os.environ, 'TEST_CMD': str(runner)},
    )


def ran(log):
    """The files the stub runner was handed, sorted; none if it never ran."""
    return sorted(log.read_text().split()) if log.exists() else []


@pytest.mark.parametrize('bash', BASHES)
@pytest.mark.parametrize('pattern', ['src/**/*.test.ts', './src/**/*.test.ts'])
def test_globstar_pattern_runs_top_level_and_nested_tests(bash, project, tmp_path, pattern):
    """The header's own example. find prints ./-prefixed paths, and its -path
    cannot match '**/' against zero directories, so before the fix the bare
    form matched nothing and the ./ form skipped src/top.test.ts. The count
    line is printed from a variable; the runner's log proves each file ran."""
    runner, log = make_runner(tmp_path)
    result = find_polluter(bash, project, pattern, runner)
    assert 'Found 2 test files' in result.stdout
    assert ran(log) == ['./src/sub/b.test.ts', './src/top.test.ts']
    assert result.returncode == 0


@pytest.mark.parametrize('bash', BASHES)
def test_documented_pytest_pattern_still_matches(bash, project, tmp_path):
    """root-cause-tracing.md's '*/test_*.py' worked before the fix, which is
    why the bug hid on a pytest stack. The ./ prefix must not break it."""
    runner, log = make_runner(tmp_path)
    result = find_polluter(bash, project, '*/test_*.py', runner)
    assert 'Found 1 test files' in result.stdout
    assert ran(log) == ['./tests/test_a.py']
    assert result.returncode == 0


@pytest.mark.parametrize('bash', BASHES)
def test_unmatched_pattern_says_nothing_ran_instead_of_all_clear(bash, project, tmp_path):
    """An empty find result counted as one line: "Found 1 test files", no
    test run, then "No polluter found - all tests clean!" and exit 0, a
    false all-clear on any typo. Upstream's fix reports "Found 0" and still
    leaves through that clean line; this port says no test ran and exits 2."""
    runner, log = make_runner(tmp_path)
    result = find_polluter(bash, project, 'nomatch/**/*.test.ts', runner)
    assert 'Found 0 test files' in result.stdout
    assert 'No test files match' in result.stdout
    assert 'No polluter found' not in result.stdout
    assert 'all tests clean' not in result.stdout
    assert ran(log) == []
    assert result.returncode == 2


@pytest.mark.parametrize('bash', BASHES)
def test_names_the_polluter_after_running_clean_tests_first(bash, project, tmp_path):
    """The bisection itself, over the corrected list: b.test.ts sorts first
    and runs clean, then top.test.ts, a top-level file the old pattern
    handling never reached, creates the marker."""
    runner, log = make_runner(tmp_path, polluter='top.test.ts')
    result = find_polluter(bash, project, 'src/**/*.test.ts', runner)
    assert 'FOUND POLLUTER' in result.stdout
    assert 'Test: ./src/top.test.ts' in result.stdout
    assert ran(log) == ['./src/sub/b.test.ts', './src/top.test.ts']
    assert result.returncode == 1
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd skills/systematic-debugging && uv run --python 3.13 --with pytest python -m pytest -q`

Expected, with two distinct bashes (+4 test functions, +10 cases): 8 failed, 2 passed.
- `test_globstar_…[src/**/*.test.ts-*]`: FAIL, stdout says `Found 1 test files` (nothing matched).
- `test_globstar_…[./src/**/*.test.ts-*]`: FAIL, stdout says `Found 1 test files` (only the nested file matched).
- `test_documented_pytest_pattern_still_matches`: PASS (the control: this pattern worked before).
- `test_unmatched_…`: FAIL, stdout says `Found 1 test files`.
- `test_names_the_polluter_…`: FAIL, no `FOUND POLLUTER` (nothing matched).

With one bash, halve the counts.

- [ ] **Step 3: Port the fix**

In `skills/systematic-debugging/find-polluter.sh`, after the header's last `TEST_CMD` example line (`#   TEST_CMD='go test'     ./find-polluter.sh '.git' '*_test.go'`), add:

```bash
#
# Exit status: 0 when no polluter is found, 1 when one is (or on a usage
# error), 2 when no test file matches the pattern, so no test ran.
```

Replace:

```bash
# Get list of test files
TEST_FILES=$(find . -path "$TEST_PATTERN" | sort)
TOTAL=$(echo "$TEST_FILES" | wc -l | tr -d ' ')
```

with:

```bash
# Get list of test files (find . emits ./-prefixed paths, so accept the
# pattern written with or without a leading ./)
TEST_PATTERN="${TEST_PATTERN#./}"
# find -path can't match '**/' against zero directory levels, so a pattern
# like src/**/*.test.ts would skip src/top.test.ts; also try the pattern
# with '**/' collapsed to cover files directly under the base directory.
TEST_FILES=$(find . \( -path "./$TEST_PATTERN" -o -path "./${TEST_PATTERN//\*\*\//}" \) | sort -u)
if [ -z "$TEST_FILES" ]; then
  # An empty result is no files, not one, and nothing ran: never fall
  # through to the all-clear below.
  echo "Found 0 test files"
  echo ""
  echo "❌ No test files match that pattern, so no test ran. This is not an all-clear."
  echo "   find -path matches the pattern against ./-prefixed paths from this directory."
  exit 2
fi
TOTAL=$(printf '%s\n' "$TEST_FILES" | wc -l | tr -d ' ')
```

The two comments and the `find` line are upstream's (`c8921b5`); the empty branch is this port's (S4).

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd skills/systematic-debugging && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: 10 passed (5 with one bash). A failure under `/bin/bash` alone means the `${…//…/}` substitution misbehaves on bash 3.2: stop and report it.

- [ ] **Step 5: Re-anchor the invocation and record the suite's command**

In `skills/systematic-debugging/root-cause-tracing.md`, replace line 102:

````markdown
```bash
./find-polluter.sh '.git' '*/test_*.py'
```
````

with:

````markdown
```bash
<this-skill-dir>/find-polluter.sh '.git' '*/test_*.py'
```
````

In `CLAUDE.md`'s Commands block, after the `subagent-driven-development dispatch-script tests` entry, add:

```bash
# systematic-debugging find-polluter.sh tests (stdlib only; they drive the script in throwaway git projects,
# under /bin/bash and the PATH's bash when those differ)
cd skills/systematic-debugging && uv run --python 3.13 --with pytest python -m pytest -q
```

- [ ] **Step 6: Lint and commit**

```bash
bash build/run_commit_lints.sh
git add skills/systematic-debugging/find-polluter.sh skills/systematic-debugging/test_find_polluter.py skills/systematic-debugging/root-cause-tracing.md CLAUDE.md
git commit -m "fix(systematic-debugging): find-polluter.sh matches **/ patterns and never false-clears"
```

Expected: `commit lints passed`, then the commit. The message body names upstream `6015d37` and `c8921b5` (v6.2.0), audit X3, and the trailer.

### Task 2: review-package rejects empty and non-descendant ranges

Upstream: `99f9f00` (PR #2136, fixing issue #2050), released in v6.4.1. Bug: with BASE == HEAD the script writes `review-<sha>..<sha>.diff` with "0 commit(s)" and exits 0; with BASE on a sibling branch it writes a diff that shows the sibling's file as a phantom deletion, and exits 0.

**Files:**
- Modify: `skills/subagent-driven-development/scripts/review-package:23` (insert the guards after it)
- Test: `skills/subagent-driven-development/scripts/test_sdd_scripts.py` (review-package section)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: exit status 3 from `review-package` on an empty or non-descendant range, with `empty commit range` or `HEAD is not a descendant of BASE` on stderr, and no package written.

- [ ] **Step 1: Write the failing tests**

Append to the review-package section of `test_sdd_scripts.py`, after `test_review_package_rejects_a_missing_plan_file`:

```python
def test_review_package_rejects_an_empty_range(repo):
    """BASE == HEAD passes the ancestry guard (a commit is its own ancestor),
    so only the count guard stands between it and a "0 commit(s)" package a
    reviewer could pass as clean work."""
    (repo / 'a.txt').write_text('one\n')
    git('add', 'a.txt', 'plan.md', cwd=repo)
    git('commit', '-qm', 'first', cwd=repo)
    out = repo / 'p.diff'
    result = run(REVIEW_PACKAGE, repo / 'plan.md', 'HEAD', 'HEAD', out, cwd=repo)
    assert result.returncode == 3
    assert 'empty commit range' in result.stderr
    assert not out.exists()


@pytest.mark.parametrize(
    'base, head',
    [
        # BASE on a sibling branch: HEAD is a commit past the fork point, so
        # the range is non-empty and only the ancestry guard can fire. The
        # package would show the sibling's file as a phantom deletion.
        ('sibling', 'HEAD'),
        # BASE and HEAD swapped, the audit's case.
        ('HEAD', 'HEAD~1'),
    ],
)
def test_review_package_rejects_a_base_that_is_not_an_ancestor(repo, base, head):
    (repo / 'a.txt').write_text('one\n')
    git('add', 'a.txt', 'plan.md', cwd=repo)
    git('commit', '-qm', 'first', cwd=repo)
    git('checkout', '-qb', 'sibling', cwd=repo)
    (repo / 'sibling.txt').write_text('only on the sibling\n')
    git('add', 'sibling.txt', cwd=repo)
    git('commit', '-qm', 'sibling work', cwd=repo)
    git('checkout', '-q', '-', cwd=repo)
    (repo / 'a.txt').write_text('one\ntwo\n')
    git('add', 'a.txt', cwd=repo)
    git('commit', '-qm', 'second', cwd=repo)
    out = repo / 'p.diff'
    result = run(REVIEW_PACKAGE, repo / 'plan.md', base, head, out, cwd=repo)
    assert result.returncode == 3
    assert 'not a descendant' in result.stderr
    assert not out.exists()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd skills/subagent-driven-development/scripts && uv run --python 3.13 --with pytest python -m pytest -q`
Expected (+2 test functions, +3 cases): 3 failed, every other test passed. Each failure is `assert 0 == 3`: the script wrote a package and exited 0.

- [ ] **Step 3: Port the guards**

In `skills/subagent-driven-development/scripts/review-package`, after line 23 (`git rev-parse --verify --quiet "$head" … exit 2; }`) and before `if [ $# -eq 4 ]; then`, insert upstream's lines verbatim:

```bash

# Range guards (exit 3): a wrong-branch HEAD yields a range that is empty or
# not rooted at BASE; either would silently produce a bogus review package.
git merge-base --is-ancestor "$base" "$head" || { echo "HEAD is not a descendant of BASE: ${base}..${head}" >&2; exit 3; }
[ "$(git rev-list --count "${base}..${head}")" -gt 0 ] || { echo "empty commit range: ${base}..${head}" >&2; exit 3; }
```

They sit before the `sdd-workspace` call and the write, so a rejected range leaves no package behind.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd skills/subagent-driven-development/scripts && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: all passed, 0 failed. The existing exit-2 tests stay green because the plan-file and revision checks run first.

- [ ] **Step 5: Lint and commit**

```bash
bash build/run_commit_lints.sh
git add skills/subagent-driven-development/scripts/review-package skills/subagent-driven-development/scripts/test_sdd_scripts.py
git commit -m "fix(subagent-driven-development): review-package rejects empty and non-descendant ranges"
```

The message body names upstream `99f9f00` (#2136, v6.4.1), audit X3, and the trailer.

### Task 3: the visual companion inserts screens literally

Upstream: `ddd35ab` (PR #2364), released in v7.0.0. Bug: `wrapInFrame` (`skills/brainstorming/scripts/server.cjs:223`) inserts the screen with `.replace('<!-- CONTENT -->', content)`, so `$'`, `` $` ``, `$&` and `$$` in a screen are read as replacement patterns.

**Files:**
- Create: `skills/brainstorming/scripts/test_server.py`
- Modify: `skills/brainstorming/scripts/server.cjs:223`
- Modify: `CLAUDE.md` (Commands block)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: nothing other tasks use. `wrapInFrame` stays unexported; only the test harness exports it, in memory.

- [ ] **Step 1: Probe the bug as the brief describes**

From the repo root:

```bash
node -e '
const Module = require("module"), fs = require("fs");
const file = process.argv[1];
const m = new Module(file, null);
m.filename = file;
m._compile(fs.readFileSync(file, "utf8") + "\nmodule.exports.wrapInFrame = wrapInFrame;\n", file);
const page = m.exports.wrapInFrame(process.argv[2]);
console.log("verbatim:", page.includes(process.argv[2]), "| headers:", page.split("<div class=\"header\">").length - 1, "| placeholder restored:", page.includes("<!-- CONTENT -->"));
' "$PWD/skills/brainstorming/scripts/server.cjs" "<p>A: \$' B: \$&</p>"
```

Expected today: `verbatim: false | headers: 1 | placeholder restored: true` (`$'` splices in the rest of the frame, `$&` the placeholder itself).

- [ ] **Step 2: Write the failing test**

Create `skills/brainstorming/scripts/test_server.py`:

```python
"""Tests for the visual companion's server.cjs — run from this directory.

cd skills/brainstorming/scripts && uv run --python 3.13 --with pytest python -m pytest -q

server.cjs is Node, so the test drives node as a subprocess. wrapInFrame is
not exported, so a small harness compiles the module with one export line
appended. The require.main guard keeps the server from starting, and loading
the module reads its two template files but writes nothing. Skips when node
is not on PATH.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

SERVER = Path(__file__).resolve().parent / 'server.cjs'
NODE = shutil.which('node')

# Compiles server.cjs with wrapInFrame exported and prints
# wrapInFrame(argv[2]). _compile with the real filename keeps __dirname at
# this directory, so frame-template.html and helper.js still load.
HARNESS = r"""
const Module = require('module');
const fs = require('fs');
const path = require('path');
const file = process.argv[1];
const m = new Module(file, null);
m.filename = file;
m.paths = Module._nodeModulePaths(path.dirname(file));
m._compile(fs.readFileSync(file, 'utf8') + '\nmodule.exports.wrapInFrame = wrapInFrame;\n', file);
process.stdout.write(m.exports.wrapInFrame(process.argv[2]));
"""

needs_node = pytest.mark.skipif(NODE is None, reason='node is not on PATH')


def wrap_in_frame(fragment):
    result = subprocess.run(
        [NODE, '-e', HARNESS, str(SERVER), fragment], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


@needs_node
def test_wrap_in_frame_inserts_replacement_tokens_literally():
    """String.replace reads $' $` $& $$ in a replacement string as patterns,
    so a screen showing prices, shell or regex text came back with part of
    the frame, or the placeholder itself, spliced in. The token list follows
    upstream's regression test (obra/superpowers ddd35ab)."""
    tokens = ["$'", '$`', '$&', '$$', '$1', '$<name>']
    fragment = '<h2>Literal tokens</h2><pre>' + ' | '.join(tokens) + '</pre>'
    page = wrap_in_frame(fragment)
    assert fragment in page
    assert page.count('<div class="header">') == 1
    assert '<!-- CONTENT -->' not in page
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `cd skills/brainstorming/scripts && uv run --python 3.13 --with pytest python -m pytest -q`
Expected (+1 test): 1 failed, on `assert fragment in page`. If it fails anywhere else (the harness's return code, a missing export), the RED is for the wrong reason: fix the harness first.

- [ ] **Step 4: Port the fix**

In `skills/brainstorming/scripts/server.cjs:223`, replace:

```javascript
  return renderBranding(frameTemplate).replace('<!-- CONTENT -->', content);
```

with upstream's:

```javascript
  return renderBranding(frameTemplate).replace('<!-- CONTENT -->', () => content);
```

- [ ] **Step 5: Run the test to verify it passes, and re-run the probe**

Run: `cd skills/brainstorming/scripts && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: 1 passed. Re-run Step 1's probe: `verbatim: true | headers: 1 | placeholder restored: false`.

- [ ] **Step 6: Record the suite's command**

In `CLAUDE.md`'s Commands block, after the entry Task 1 added, add:

```bash
# brainstorming visual-companion server test (stdlib only; drives node, and skips when node is not on PATH)
cd skills/brainstorming/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

- [ ] **Step 7: Lint and commit**

```bash
bash build/run_commit_lints.sh
git add skills/brainstorming/scripts/server.cjs skills/brainstorming/scripts/test_server.py CLAUDE.md
git commit -m "fix(brainstorming): insert companion screens literally, not as replacement patterns"
```

The message body names upstream `ddd35ab` (#2364, v7.0.0) and the trailer.

### Task 4: the debugging example reports a secret's presence, not its value

Upstream: `e592b34` (PR #2380), released in v7.0.0. Bug: `skills/systematic-debugging/SKILL.md:98` echoes `${IDENTITY:+SET}${IDENTITY:-UNSET}`, which prints `SET` followed by the value; `:102` runs `env | grep IDENTITY`, which prints every matching variable with its value.

**Files:**
- Modify: `skills/systematic-debugging/SKILL.md:98`, `:102`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: nothing other tasks use.

- [ ] **Step 1: Probe the current lines RED, with a dummy value only**

`env -i` empties the environment, so no real variable can reach the output:

```bash
env -i PATH=/usr/bin:/bin IDENTITY=dummy-not-a-secret /bin/bash -c 'echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"; env | grep IDENTITY || echo "IDENTITY not in environment"'
env -i PATH=/usr/bin:/bin /bin/bash -c 'echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"; env | grep IDENTITY || echo "IDENTITY not in environment"'
```

Expected: the first prints `IDENTITY: SETdummy-not-a-secret` and `IDENTITY=dummy-not-a-secret` (the value leaks twice); the second prints `IDENTITY: UNSET` and `IDENTITY not in environment`.

- [ ] **Step 2: Replace the two lines with upstream's**

In `skills/systematic-debugging/SKILL.md`, replace line 98:

```bash
   echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"
```

with:

```bash
   echo "IDENTITY: $([ -n "${IDENTITY:-}" ] && echo SET || echo UNSET)"
```

and line 102:

```bash
   env | grep IDENTITY || echo "IDENTITY not in environment"
```

with:

```bash
   printenv IDENTITY >/dev/null 2>&1 && echo "IDENTITY in environment" || echo "IDENTITY not in environment"
```

- [ ] **Step 3: Probe the new lines GREEN**

```bash
env -i PATH=/usr/bin:/bin IDENTITY=dummy-not-a-secret /bin/bash -c 'echo "IDENTITY: $([ -n "${IDENTITY:-}" ] && echo SET || echo UNSET)"; printenv IDENTITY >/dev/null 2>&1 && echo "IDENTITY in environment" || echo "IDENTITY not in environment"'
env -i PATH=/usr/bin:/bin /bin/bash -c 'echo "IDENTITY: $([ -n "${IDENTITY:-}" ] && echo SET || echo UNSET)"; printenv IDENTITY >/dev/null 2>&1 && echo "IDENTITY in environment" || echo "IDENTITY not in environment"'
```

Expected: `IDENTITY: SET` and `IDENTITY in environment`, with no `dummy-not-a-secret` anywhere; then `IDENTITY: UNSET` and `IDENTITY not in environment`.

- [ ] **Step 4: Lint and commit**

```bash
bash build/run_commit_lints.sh
git add skills/systematic-debugging/SKILL.md
git commit -m "fix(systematic-debugging): diagnostic example no longer prints the secret it checks"
```

The message body names upstream `e592b34` (#2380, v7.0.0), S5's no-micro-test reasoning, and the trailer.

### Task 5: sdd-workspace leaves an existing `.sdd/.gitignore` alone

Upstream: `19e54c0` (PR #2399), released in v7.0.0. Bug: `skills/subagent-driven-development/scripts/sdd-workspace:47` writes `*` to `.sdd/.gitignore` on every run, which reverts a repository's committed version of that file.

**Files:**
- Modify: `skills/subagent-driven-development/scripts/sdd-workspace:47`
- Test: `skills/subagent-driven-development/scripts/test_sdd_scripts.py` (sdd-workspace section)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: nothing other tasks use. A fresh repository still gets `*\n`, which the existing tests pin.

- [ ] **Step 1: Write the failing test**

Add to the sdd-workspace section of `test_sdd_scripts.py`, after `test_workspace_ignores_itself_so_artifacts_never_reach_git_status`:

```python
def test_workspace_leaves_a_committed_gitignore_alone(repo):
    """A repository may commit its own .sdd/.gitignore, for instance to keep
    progress ledgers under version control. Writing '*' on every run
    reverted that file in the working tree."""
    own = '*\n!.gitignore\n!*/\n!*/progress.md\n'
    (repo / '.sdd').mkdir()
    (repo / '.sdd' / '.gitignore').write_text(own)
    git('add', '.sdd/.gitignore', 'plan.md', cwd=repo)
    git('commit', '-qm', 'version the ledgers', cwd=repo)
    result = run(WORKSPACE, repo / 'plan.md', cwd=repo)
    assert result.returncode == 0
    assert (repo / '.sdd' / '.gitignore').read_text() == own
    status = run('git', 'status', '--porcelain', '--', '.sdd/.gitignore', cwd=repo)
    assert status.stdout == ''
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd skills/subagent-driven-development/scripts && uv run --python 3.13 --with pytest python -m pytest -q`
Expected (+1 test): 1 failed, on the content assertion (`'*\n' == '*\n!.gitignore\n…'`).

- [ ] **Step 3: Port the fix**

In `sdd-workspace`, replace line 47:

```bash
printf '*\n' > "$base/.gitignore"
```

with upstream's:

```bash
# Create-only: a repo may commit its own .gitignore here (e.g. to version
# progress.md ledgers); overwriting it would revert that on every run.
[ -e "$base/.gitignore" ] || printf '*\n' > "$base/.gitignore"
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd skills/subagent-driven-development/scripts && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: all passed, 0 failed.

- [ ] **Step 5: Lint and commit**

```bash
bash build/run_commit_lints.sh
git add skills/subagent-driven-development/scripts/sdd-workspace skills/subagent-driven-development/scripts/test_sdd_scripts.py
git commit -m "fix(subagent-driven-development): sdd-workspace leaves an existing .sdd/.gitignore alone"
```

The message body names upstream `19e54c0` (#2399, v7.0.0) and the trailer.

### Task 6: record the adoptions

**Files:**
- Modify: `NOTICE` (the superpowers block's "Changes from upstream" list, after its last entry, the `# cc-guide:` one)
- Modify, only if D7's condition holds: `specs/superpowers-drift-spec.md`

**Interfaces:**
- Consumes: the upstream commits, releases and divergences Tasks 1–5 name.
- Produces: nothing.

- [ ] **Step 1: Add the NOTICE entry**

After the entry that ends `(specs/claude-code-drift-automation-spec.md, R4). No parsed field changed.`, add:

```text
  - Five fixes were later adopted FROM upstream (plan 50, 2026-10-18), each
    read at the upstream commit named here and each shown failing here,
    by a test or a probe, before it was ported. From v6.2.0,
    systematic-debugging/find-polluter.sh's pattern handling (6015d37,
    #2011, fixing issue #2008; and c8921b5): a leading ./ is stripped, the
    pattern is matched both as given and with **/ collapsed, so
    src/**/*.test.ts also finds src/top.test.ts, and an empty match counts
    as no files rather than one. From v6.4.1, review-package's two range
    guards (99f9f00, #2136, fixing issue #2050): exit 3 when BASE is not an
    ancestor of HEAD or the range is empty. From v7.0.0: sdd-workspace
    writes its .gitignore only when none exists (19e54c0, #2399);
    brainstorming's server.cjs inserts each screen through a replacer
    function, so $' and $& in a screen stay literal (ddd35ab, #2364); and
    systematic-debugging/SKILL.md's multi-layer diagnostic example reports
    whether IDENTITY is set without printing its value (e592b34, #2380).
    The guards, the server.cjs line and the SKILL.md lines are upstream's
    verbatim. Three parts diverge deliberately. find-polluter.sh keeps its
    local TEST_CMD, and when no test file matches it says no test ran and
    exits 2, where upstream reports "Found 0" and still ends on its
    all-clear line with exit 0. sdd-workspace keeps .sdd/ rather than
    upstream's .superpowers/sdd/, and 19e54c0's CDPATH respelling is not
    taken, since this copy never sets CDPATH. And the tests are this
    repo's pytest, not upstream's: test_find_polluter.py (new) adapts the
    cases of upstream's test-find-polluter.sh; the range-guard and
    .gitignore tests in test_sdd_scripts.py follow upstream's setups; and
    brainstorming/scripts/test_server.py (new) takes ddd35ab's token list,
    loading server.cjs through a Module._compile harness so that file
    keeps upstream's one-line change. Separately, and not from upstream,
    root-cause-tracing.md's find-polluter.sh call now carries the
    <this-skill-dir>/ anchor the bundled-script entry above gave the other
    skills; upstream's #2301 prefixes bash but still resolves the path
    against the user's repository.
```

- [ ] **Step 2: Check D7's condition**

```bash
git fetch origin main
git merge-base --is-ancestor f9ae68d main && echo merged-local || echo not-merged-local
git merge-base --is-ancestor f9ae68d origin/main && echo merged-origin || echo not-merged-origin
```

If neither prints `merged-…`, leave `specs/superpowers-drift-spec.md` alone and record that in the completion report. If either does, bring the branch up to date with the base branch first (`sync_with_base_branch` in an app worktree), then mark findings 8 (the `find-polluter.sh` item), 12 (the range guards and the `.gitignore` item) and 16 adopted by plan 50, in their sections, in the status table and in the Suggested disposition's "Done" line, and commit that with the `NOTICE` entry.

- [ ] **Step 3: Lint and commit**

```bash
bash build/run_commit_lints.sh
git add NOTICE
git commit -m "docs(notice): record the five superpowers fixes adopted in plan 50"
```

## Completion

After Task 6, executing-plans' Step 3 reviews the whole branch (code-reviewer and Codex, launched together, BASE `git merge-base main HEAD`), then the writing-plans Plan Completion Protocol runs. No merge, push or PR: the integration choice is the owner's.

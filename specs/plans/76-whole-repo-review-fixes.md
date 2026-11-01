# Whole-Repo Review Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the 38 Important findings that the 2026-10-31 whole-repo review of `b3062c6` left after its Critical finding was fixed (`305576b`, `f0403f8`).

**Architecture:** Twenty-three tasks, each the only task that edits its files, in three bands. Bundled scripts and build gates come first (Tasks 1-11), each test-driven in its registered suite. Reference and documentation text follows (Tasks 12-19), each with a mechanical failing check, and a micro-test kit for the three wording changes that alter what an agent chooses. The two plan executors' own text comes last (Tasks 20-21), then the owner-gated `stable_digits` change (Task 22) and the NOTICE change list (Task 23).

**Tech Stack:** Python per `build/versions.toml` with pytest through `build/run_suites.py`, Polars 2.1.0, ArviZ 1.3.0, bash 3.2-safe shell, Markdown skill text, the `claude -p` micro-test kit.

**Spec:** none. The requirement source is the review's record, which is not in the repository. Each task restates its finding: the number (`#N`), the failure a person meets, and the fix. Finding numbers are the review's.

## Global Constraints

- **Self-modifying run.** Tasks 20 and 21 edit executing-plans and subagent-driven-development, the skills that run this plan, and `fix-loop.md` is re-read every fix round. Execute in a worktree. The installed skills (`~/.claude/skills`, a symlink into the main checkout) keep main's text for the whole run: do not merge or pull into the main checkout until the plan completes.
- **One owner per file.** A task edits only its listed files. Generated files under `runtimes/` change only through `uv run --with pyyaml python build/sync_runtime_assets.py`. One exception: Task 12 creates `specs/red-baseline-review-fixes.md`, and Tasks 13, 20 and 21 each append their own case's section to it.
- **Plan 75's fences that still bind.** The five-stop numbered list stays byte-identical in `skills/executing-plans/SKILL.md` and `skills/subagent-driven-development/references/fix-loop.md` (each file's lead-in sentence is free). The `skills/executing-plans/SKILL.md` body stays at most 18,500 characters, and the `skills/subagent-driven-development/SKILL.md` body stays inside `build/check_conformance.py`'s compaction window (19,189 of 20,000 characters at `b3062c6`). Measure a body with `check_conformance.skill_body(text)[0]`.
- **Suites.** Run each touched suite with `uv run python build/run_suites.py <suite>`; the last line must read `suite runs passed`. A single test: `uv run python build/run_suites.py <suite> -- -k <name>`. State test counts as deltas (`+N`), never totals.
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Commit messages follow Conventional Commits, use plain technical English, and end with the attribution trailer the executing session is given.
- **Per-area gates.** bayesian-workflow text: the three snippet tiers in the root `CLAUDE.md` Commands section. Skill, agent, command, hook, settings and `CLAUDE.md` edits: `uv run --with pyyaml python build/check_conformance.py` and `uv run python build/cc_guide/cli.py lint` (both in the commit lints). An added or dropped cross-skill path or named section: the dependency-drift test (also in the commit lints).
- **Citations.** `build/.scratch/` is absent, so Gate A (`build/verify_citations.py`) cannot run. Task 19 changes no `PML1 §`, `PML2 §` or notebook citation.
- **Style.** Python follows `rules/clean-code-python.md`, except that each file keeps its existing quote style (`skills/explore-data/scripts/profile.py` uses double quotes). Shell stays bash 3.2-safe: no `mapfile`, no GNU-only flags. In zsh, quote `====` and use `/usr/bin/grep`.
- **Micro-tests (Tasks 12, 13, 20 and 21 only).** The kit lives at `specs/red-baseline-review-fixes/kit/`. Every rep is a fresh `claude -p --model claude-sonnet-5-5 --tools "" --strict-mcp-config --setting-sources ""` with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, run from a new empty directory outside every repository. Five reps per arm. The control arm reads the text at this plan's base commit. Each case's reading rule and pass bar are committed before any rep is read. Stop at **$15** for the whole kit and ask the owner. If a case's control arm shows no failure, revert that task's wording change and ledger a ruling: there is nothing to fix.
- **Public repository.** The plan, kit, record and commits hold no private detail. `build/.scratch/` is never committed.
- **One execution at a time.** Execution starts only when no other plan is executing in this repository.

## Review Focus

1. A test file whose path holds a space, or a `TEST_CMD` that is not installed: `find-polluter.sh` never ends on its all-clear. Pinned in Task 1 (`test_test_path_with_a_space_runs_as_one_file`, `test_runner_that_cannot_start_is_not_an_all_clear`).
2. A relative `--project-dir`, given from a directory other than the script's: the server starts, and its files land under that directory. Pinned in Task 2 (`test_relative_project_dir_starts_the_server_under_it`).
3. A column that is constant apart from nulls, and a panel whose period column holds one null: the profile flags the column CONSTANT and counts complete entities as balanced. Pinned in Task 4.
4. A Python block inside a numbered list item, with an indented fence: the snippet gate parses it. Pinned in Task 7, with `skills/recommend-visualization/references/altair.md:49` as the live case.
5. A `PROBES.md` whose log header a hand edit broke: `cli.py probes` refuses before any probe runs, so it spends nothing. Pinned in Task 8 (`test_a_log_with_no_probe_table_refuses_before_any_probe_runs`).

## Decisions

None.

## Open for plan review

1. **Micro-test policy.** Proposed: micro-test only the three fixes that change what an agent chooses (Task 13's prepare-handoff dispatch, Task 20's stop-rule scope, Task 21's fix-round test gate). Every other text fix uses a mechanical failing check: an exit code, a grep, the dispatch guard's JSON, a lint or a KeyError. writing-skills' rule ("no skill edit without a failing test first") and the owner's proportional-process preference pull opposite ways here, so the owner breaks the tie. The alternative is no micro-tests at all, which drops Task 12 and the micro-test steps of Tasks 13, 20 and 21.
2. **Finding 9, what `stable_digits` means.** Task 22 waits for this pick. Options are under Task 22.
3. **Task 21's gate direction.** Proposed: `fix-loop.md` follows test-driven-development, whose "documented suite defines green" rule plan 75's approved spec set. A fix round runs its covering tests while it iterates, and runs the documented suite(s) the change can reach once before it writes the fix report.
4. **`find-polluter.sh` exit status for a runner that cannot start.** Proposed: exit 2, with 2's meaning widened to "no test ran" (no file matched, or the test command could not start), instead of adding a new status 4.
5. **Scope beyond the record.** Task 4 makes `column_profile`'s `n_unique` count non-null values, because the CONSTANT flag reads it. Task 5 aligns `recommend.py`'s own `n_unique` (line 177) with that, so its two input paths agree. Task 3 corrects `zero_fraction`'s docstring, which repeats finding 39's routing error.
6. **Outside the 38: the redactor's value class.** The review of `305576b` found that values with punctuation (`P@ss…`), values under 12 characters and `--api-key VALUE` still pass both llm-wiki layers. The gap predates the Critical fix. Widening the class trades against the file-path lesson in the `high-entropy` comment. No task covers it. The owner decides between a task here and a design item in `specs/deferred_items.md`.

---

### Task 1: find-polluter never gives a false all-clear (#2, #3)

`|| true` swallows a runner that cannot start (exit 126 or 127), so a missing `pytest` prints "No polluter found" and exits 0 (#2). `for TEST_FILE in $TEST_FILES` splits a path with a space and glob-expands it, so the real file never runs and the run ends on the all-clear (#3).

**Files:**
- Modify: `skills/systematic-debugging/find-polluter.sh` (header lines 16-19; loop lines 73-105)
- Test: `skills/systematic-debugging/test_find_polluter.py`

**Interfaces:** none.

- [ ] **Step 1: Write the failing tests** (both parametrized over `BASHES`, like their neighbours)

```python
def test_runner_that_cannot_start_is_not_an_all_clear(bash, project, tmp_path):
    proc = find_polluter(bash, project, '*/test_*.py', tmp_path / 'no-such-runner')
    assert proc.returncode == 2
    assert 'No polluter found' not in proc.stdout
    assert 'could not start' in proc.stdout


def test_test_path_with_a_space_runs_as_one_file(bash, project, tmp_path):
    spaced = project / 'my tests'
    spaced.mkdir()
    (spaced / 'test_spaced.py').write_text('def test_s():\n    pass\n')
    runner, log = make_runner(tmp_path, polluter='test_spaced.py')
    proc = find_polluter(bash, project, '*/test_*.py', runner)
    assert proc.returncode == 1
    assert './my tests/test_spaced.py' in log.read_text().splitlines()
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run python build/run_suites.py systematic-debugging -- -k "cannot_start or with_a_space"`
Expected: FAIL. The first fails on `assert 0 == 2`. The second fails on the log line, because the runner was handed `./my` and `tests/test_spaced.py`.

- [ ] **Step 3: Fix the loop in `find-polluter.sh`**

Iterate with `while IFS= read -r TEST_FILE; do … done <<EOF` over `$TEST_FILES` (a here-document, not a pipe, so `exit` leaves the script). Run the test as `$TEST_CMD "$TEST_FILE" </dev/null >/dev/null 2>&1`, so a runner that reads stdin cannot consume the list. Keep its exit status. On 126 or 127, print a line containing `could not start` that names `$TEST_CMD` and says this is not an all-clear, then exit 2. Reword the header's exit-status comment: 2 means no test ran, because no file matched or the test command could not start.

- [ ] **Step 4: Run the suite**

Run: `uv run python build/run_suites.py systematic-debugging`
Expected: `suite runs passed`, +2 test functions (each runs once per bash found).

- [ ] **Step 5: Commit**

```bash
git add skills/systematic-debugging/find-polluter.sh skills/systematic-debugging/test_find_polluter.py
git commit -m "fix(systematic-debugging): find-polluter never ends on a false all-clear"
```

### Task 2: start-server.sh handles a relative project dir and a missing option value (#4, #5)

A relative `--project-dir` builds the session, log and pid paths relative to the caller. Then `cd "$SCRIPT_DIR"` runs before the log redirect, so node never starts and the error names the wrong cause (#4). A trailing value-taking option, such as `--host` with no value, loops forever, because `shift 2` fails without consuming the argument (#5).

**Files:**
- Modify: `skills/brainstorming/scripts/start-server.sh` (option loop lines 29-46; project dir before line 116)
- Create: `skills/brainstorming/scripts/test_start_server.py` (the `brainstorming` suite collects it)

**Interfaces:** none.

- [ ] **Step 1: Write the failing tests**

Module docstring as in `test_server.py`. `START = Path(__file__).resolve().parent / 'start-server.sh'`, and `STOP` names `stop-server.sh` the same way. `needs_node` matches `test_server.py`'s marker.

```python
@pytest.mark.parametrize('option', ['--project-dir', '--host', '--url-host', '--idle-timeout-minutes'])
def test_value_option_without_a_value_exits_with_an_error(option):
    proc = subprocess.run(['bash', str(START), option], capture_output=True, text=True, timeout=10)
    assert proc.returncode == 1
    assert json.loads(proc.stdout)['error'] == f'{option} needs a value'


@needs_node
def test_relative_project_dir_starts_the_server_under_it(tmp_path):
    proc = subprocess.run(['bash', str(START), '--project-dir', 'proj', '--idle-timeout-minutes', '1'],
                          cwd=tmp_path, capture_output=True, text=True, timeout=30)
    try:
        assert proc.returncode == 0, proc.stdout
        info = json.loads(proc.stdout.strip().splitlines()[-1])
        state = Path(info['state_dir'])
        assert state.is_absolute()
        assert state.resolve().is_relative_to((tmp_path / 'proj' / '.brainstorm').resolve())
        assert (state / 'server.log').is_file()
    finally:
        for state in (tmp_path / 'proj' / '.brainstorm').glob('*/state'):
            subprocess.run(['bash', str(STOP), str(state.parent)], capture_output=True, timeout=10)
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run python build/run_suites.py brainstorming -- -k "without_a_value or relative_project_dir"`
Expected: FAIL. The four option cases fail with `TimeoutExpired`. The relative case fails with exit 1 (`Server failed to start` or a redirect error), or skips if node is absent.

- [ ] **Step 3: Fix `start-server.sh`**

Before each `shift 2`, a value-taking option with fewer than two arguments left prints `{"error": "<option> needs a value"}` and exits 1. After parsing, a set `PROJECT_DIR` becomes absolute (`mkdir -p` it, then `cd … && pwd -P`). A failure there prints a JSON error naming the directory and exits 1. Leave the other flows unchanged.

- [ ] **Step 4: Run the suite**

Run: `uv run python build/run_suites.py brainstorming`
Expected: `suite runs passed`, +5 tests (one may skip without node).

- [ ] **Step 5: Commit**

```bash
git add skills/brainstorming/scripts/start-server.sh skills/brainstorming/scripts/test_start_server.py
git commit -m "fix(brainstorming): start-server takes a relative project dir and rejects a missing value"
```

### Task 3: overdispersion returns None below two values (#6)

`overdispersion` raises TypeError when the target has fewer than two non-null values, because Polars `s.var()` returns None there.

**Files:**
- Modify: `skills/recommend-probabilistic-model/scripts/characterize.py:23-35` and the `zero_fraction` docstring at `:39`
- Test: `skills/recommend-probabilistic-model/scripts/test_characterize.py`

**Interfaces:** `overdispersion(s: pl.Series) -> float | None` keeps its signature.

- [ ] **Step 1: Write the failing test**

```python
@pytest.mark.parametrize('values', [[3], [None, 4]])
def test_overdispersion_none_below_two_values(values):
    assert overdispersion(pl.Series(values, dtype=pl.Int64)) is None
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run python build/run_suites.py recommend-probabilistic-model -- -k below_two_values`
Expected: FAIL with `TypeError` in both cases.

- [ ] **Step 3: Return None when fewer than two non-null values remain**, beside the existing empty check. In `zero_fraction`'s docstring, replace "high values point to zero-inflated / hurdle models" with a statement that only zeros beyond what Poisson or NB predicts at the observed mean point there. No code change in `zero_fraction`.

- [ ] **Step 4: Run the suite**

Run: `uv run python build/run_suites.py recommend-probabilistic-model`
Expected: `suite runs passed`, +2 tests.

- [ ] **Step 5: Commit**

```bash
git add skills/recommend-probabilistic-model/scripts/characterize.py skills/recommend-probabilistic-model/scripts/test_characterize.py
git commit -m "fix(recommend-probabilistic-model): overdispersion is None below two values"
```

### Task 4: profile.py survives a column named count and ignores nulls when counting (#7, #8)

`top_categoricals` aliases its aggregate `count`, so a string column named `count` raises DuplicateError and aborts the whole profile (#7). Polars `n_unique` counts null as a value (#8). One null period makes every complete entity read as unbalanced. A column constant apart from nulls escapes the CONSTANT flag. A null vintage reads as a revision.

**Files:**
- Modify: `skills/explore-data/scripts/profile.py` (lines 67, 133-142, 206, 209, 232, 235)
- Test: `skills/explore-data/scripts/test_profile.py`

**Interfaces:** `column_profile`'s `n_unique` field now counts non-null distinct values (Open for plan review, item 5). Task 5 relies on that meaning.

- [ ] **Step 1: Write the failing tests** (use the module's existing import name for `profile.py`)

```python
def test_top_categoricals_handles_a_column_named_count():
    lf = pl.LazyFrame({'count': ['a', 'a', 'b']})
    assert P.top_categoricals(lf, lf.collect_schema())['count'] == [('a', 2), ('b', 1)]


def test_panel_balance_ignores_a_null_period():
    lf = pl.LazyFrame({'firm': ['a', 'a', 'b', 'b', 'c'], 'month': [1, 2, 1, 2, None]})
    out = P.panel_balance(lf, 'firm', 'month', lf.collect_schema())
    assert out['n_periods'] == 2
    assert out['balanced_entities'] == 2


def test_constant_apart_from_nulls_is_flagged_constant():
    lf = pl.LazyFrame({'k': [1, 2, 3, 4], 'unit': ['usd', None, 'usd', 'usd']})
    schema = lf.collect_schema()
    flags = P.quality_flags(P.column_profile(lf, 4, schema), 4, lf, schema)
    assert any(f.startswith('CONSTANT: unit') for f in flags)


def test_vintage_check_ignores_a_null_vintage():
    lf = pl.LazyFrame({'series': ['s', 's'], 'period': [1, 1], 'vintage': ['v1', None]})
    out = P.vintage_check(lf, ['series', 'period', 'vintage'], lf.collect_schema())
    assert out['n_vintages'] == 1
    assert out['period_keys_with_multiple_vintages'] == 0
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run python build/run_suites.py explore-data -- -k "named_count or null_period or apart_from_nulls or null_vintage"`
Expected: 4 FAIL: DuplicateError; `3 == 2`; no CONSTANT flag; `2 == 1`.

- [ ] **Step 3: Fix `profile.py`.** Alias the count to a name that cannot equal the one selected column (for example `f"{c}_count"`) and read that name back. Count distinct values with `drop_nulls()` before `n_unique()` at all five sites. If an existing test pins a null-inclusive count, it encodes the defect: update it and name it in the report.

- [ ] **Step 4: Run the suite**

Run: `uv run python build/run_suites.py explore-data`
Expected: `suite runs passed`, +4 tests.

- [ ] **Step 5: Commit**

```bash
git add skills/explore-data/scripts/profile.py skills/explore-data/scripts/test_profile.py
git commit -m "fix(explore-data): profile survives a count column and ignores nulls when counting"
```

### Task 5: recommend.py never invents a column (#10)

With a categorical-only field set, the comparison path returns a bar whose encoding names a nonexistent `value` column (and with no categorical, it invents both). The CLI exits 0, while the SKILL calls the encoding map a near-direct spec.

**Files:**
- Modify: `skills/recommend-visualization/scripts/recommend.py` (`_comparison` lines 242-252; `fields_from_frame` line 177)
- Test: `skills/recommend-visualization/scripts/test_recommend.py`

**Interfaces:** Consumes Task 4's non-null `n_unique` meaning.

- [ ] **Step 1: Write the failing tests**

```python
def test_comparison_with_only_a_categorical_counts_rows():
    c = top('comparison', [Field('region', 'categorical', n_unique=4)], 100)
    assert c.chart == 'bar' and c.encodings == {'x': 'region', 'y': 'count()'}


def test_comparison_without_a_categorical_has_no_candidate():
    assert recommend('comparison', [Field('emp', 'quantitative')], 100) == []


def test_fields_from_frame_counts_distinct_values_without_null():
    df = pl.DataFrame({'period': ['2024', '2025', None]})
    assert fields_from_frame(df)[0].n_unique == 2
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run python build/run_suites.py recommend-visualization -- -k "only_a_categorical or without_a_categorical or without_null"`
Expected: 3 FAIL: `'value'` in the encoding; a non-empty list; `3 == 2`.

- [ ] **Step 3: Fix `recommend.py`.** With a categorical and no quantitative field, return one `bar` candidate encoded `{'x': cat.name, 'y': 'count()'}` (the `count()` form this module already uses for density charts). With no categorical field, return `[]`, which the CLI already reports with exit 1. In `fields_from_frame`, count `df[c].drop_nulls().n_unique()`.

- [ ] **Step 4: Run the suite**

Run: `uv run python build/run_suites.py recommend-visualization`
Expected: `suite runs passed`, +3 tests.

- [ ] **Step 5: Commit**

```bash
git add skills/recommend-visualization/scripts/recommend.py skills/recommend-visualization/scripts/test_recommend.py
git commit -m "fix(recommend-visualization): comparison never names a column the data lacks"
```

### Task 6: the snippet gate refuses a path it cannot check (#11)

`build/check_snippets.py` skips a missing path silently, checks nothing and exits 0. The sibling gates (`check_links.py`, `check_jax_examples.py`) refuse this.

**Files:**
- Modify: `build/check_snippets.py` (`main`, near line 550)
- Test: `build/test_check_snippets.py`

**Interfaces:** none.

- [ ] **Step 1: Write the failing test**

```python
def test_a_missing_or_non_markdown_path_exits_2_and_names_it(tmp_path, capsys):
    txt = tmp_path / 'notes.txt'
    txt.write_text('x')
    for bad in (tmp_path / 'nope', txt):
        assert check_snippets.main([str(bad)]) == 2
        assert str(bad) in capsys.readouterr().err
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run python build/run_suites.py build -- -k missing_or_non_markdown`
Expected: FAIL on `0 == 2`.

- [ ] **Step 3: In `main`, before any check runs,** print each argument that is neither a directory nor an existing `.md` file to stderr, then return 2.

- [ ] **Step 4: Run the suite**

Run: `uv run python build/run_suites.py build`
Expected: `suite runs passed`, +1 test.

- [ ] **Step 5: Commit**

```bash
git add build/check_snippets.py build/test_check_snippets.py
git commit -m "fix(build): check_snippets exits 2 on a path it cannot check"
```

### Task 7: fences.py sees indented and tilde fences (#12)

Tier 1 never sees a Python block whose fence is indented or written with `~~~`, though `check_snippets.py:3` promises every fenced Python block. One such block ships unchecked today, at `skills/recommend-visualization/references/altair.md:49` (indented in a numbered list item; it parses).

**Files:**
- Modify: `build/fences.py`
- Test: `build/test_fences.py`

**Interfaces:** `iter_code_blocks`, `strip_fenced_blocks` and `fenced_lines` keep their signatures. `check_snippets.py`, `check_jax_examples.py`, `check_conformance.py` and `check_frontmatter.py` all import them, so all four see the change.

- [ ] **Step 1: Record the block inventory before the change**

Run: `uv run python -c "import sys; sys.path.insert(0, 'build'); import fences, pathlib; [print(p, b.line) for p in sorted(pathlib.Path('skills').rglob('*.md')) for b in fences.iter_code_blocks(p.read_text())]" > /tmp/plan76-blocks-before.txt`
Expected: one line per Python block found today.

- [ ] **Step 2: Write the failing tests**

```python
def test_indented_fence_in_a_list_item_is_a_block():
    text = '1. Item:\n\n   ```python\n   x = 1\n   ```\n'
    (block,) = fences.iter_code_blocks(text)
    assert block.code == 'x = 1\n' and block.line == 3


def test_tilde_fence_is_a_block_and_closes_only_on_tildes():
    (block,) = fences.iter_code_blocks('~~~python\ny = 2\n```\n~~~\n')
    assert block.code == 'y = 2\n```\n'


def test_strip_and_fenced_lines_follow_the_same_rule():
    text = 'a\n  ~~~\n  b\n  ~~~\nc'
    assert fences.strip_fenced_blocks(text) == 'a\nc'
    assert fences.fenced_lines(text) == {2, 3, 4}
```

- [ ] **Step 3: Run them to verify they fail**

Run: `uv run python build/run_suites.py build -- -k "indented_fence or tilde_fence or follow_the_same_rule"`
Expected: 3 FAIL (no block found; text not stripped).

- [ ] **Step 4: Widen the opener in `fences.py`.** It is any run of leading spaces, then three or more backticks or three or more tildes, then the info string. Keep the opener's indent, character and length. A closer is a line of the same character, at least as long, with only whitespace around it. Remove up to the opener's indent of leading spaces from each body line. All three functions use the one rule. Update the module docstring.

- [ ] **Step 5: Run the inventory again and every consumer gate**

Run the Step 1 command into `/tmp/plan76-blocks-after.txt`, then `diff /tmp/plan76-blocks-before.txt /tmp/plan76-blocks-after.txt`.
Expected: only added lines, `altair.md` 49 among them. Then run `uv run python build/check_snippets.py skills/`, `bash build/run_commit_lints.sh` and `uv run python build/run_suites.py build`. A newly visible block that fails to parse is fixed in place, or marked `noparse` with a reason when it cannot run by design (`build/check_snippets.py` documents the markers). List each such block in the report. If a newly visible block sits in a bayesian-workflow file, run that file through Tiers 2 and 3 as well.

- [ ] **Step 6: Commit**

```bash
git add build/fences.py build/test_fences.py   # plus any block fixed in Step 5
git commit -m "fix(build): fence parsing sees indented and tilde fences"
```

### Task 8: probes refuse a log with no probe table before spending tokens (#13)

A `PROBES.md` whose log table lacks a recognizable header parses as empty, so every probe reads as due. The first probe then runs, which costs tokens, before `append_row` raises.

**Files:**
- Modify: `build/cc_guide/probes.py` (`run`, after reading `PROBES`)
- Test: `build/cc_guide/test_probes.py`

**Interfaces:** none.

- [ ] **Step 1: Write the failing test** (with the module's `repo` and `claude` fixtures, its `run` helper and `cc_fixtures.write_tree`)

```python
def test_a_log_with_no_probe_table_refuses_before_any_probe_runs(repo, tmp_path, claude):
    write_tree(repo, {state.PROBES: '# Probes\n\n| Term | Meaning |\n|---|---|\n| PASS | ok |\n'})
    calls = []
    with pytest.raises(state.SetupError, match='no probe log table'):
        run(repo, tmp_path, claude, lambda *a, **k: calls.append(a))
    assert calls == []
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run python build/run_suites.py cc_guide -- -k no_probe_table`
Expected: FAIL. Either `calls` is non-empty, or the error comes from `append_row` with another message.

- [ ] **Step 3: In `run`, before choosing probes,** raise `SetupError` when the `PROBES.md` text exists and no line passes `is_probe_header`. The message contains `no probe log table`, names `PROBES.md` and says to restore the header. An absent file stays allowed: the first run creates it.

- [ ] **Step 4: Run the suite**

Run: `uv run python build/run_suites.py cc_guide`
Expected: `suite runs passed`, +1 test.

- [ ] **Step 5: Commit**

```bash
git add build/cc_guide/probes.py build/cc_guide/test_probes.py
git commit -m "fix(cc_guide): probes refuse a log with no probe table before running"
```

### Task 9: the drift notice names a command that runs (#14)

The error notice says `run build/cc_guide/cli.py check`. The file is mode 100644 and needs the dev Python, so only `uv run python build/cc_guide/cli.py check` works.

**Files:**
- Modify: `build/cc_guide/notice.py:36`, `build/cc_guide/notice.sh:109,132`
- Test: `build/cc_guide/test_notice.py`, `build/cc_guide/test_cli.py`, `build/cc_guide/test_notice_sh.py` (each expected string that holds the old command)

**Interfaces:** none.

- [ ] **Step 1: Change every expected string in the three test files** from `→ run build/cc_guide/cli.py check` to `→ uv run python build/cc_guide/cli.py check`. Find them with `/usr/bin/grep -rn "cli.py check" build/cc_guide/test_*.py`.

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run python build/run_suites.py cc_guide`
Expected: FAIL in each test whose expected string changed.

- [ ] **Step 3: Change `TO_CHECK` in `notice.py`** to `' → uv run python build/cc_guide/cli.py check'`, and the two `fail_notice` hints in `notice.sh` to `'uv run python build/cc_guide/cli.py check'`. The 300-character `LIMIT` still holds: the longest notice test must not truncate.

- [ ] **Step 4: Run the suite**

Run: `uv run python build/run_suites.py cc_guide`
Expected: `suite runs passed`, +0 tests.

- [ ] **Step 5: Commit**

```bash
git add build/cc_guide/notice.py build/cc_guide/notice.sh build/cc_guide/test_notice.py build/cc_guide/test_cli.py build/cc_guide/test_notice_sh.py
git commit -m "fix(cc_guide): the drift notice names a command that runs"
```

### Task 10: Gate A pins the guard's denial prefix (#15)

The live probe (`hooks/probe-readonly-guard.sh`) and `build/cc_guide/probe_checks.py` grep for `readonly-agent-guard:`, but no hook test asserts it. An edit to the reason's first words passes the suite, and the live probe then reports a broken install.

**Files:**
- Test: `hooks/test_readonly_agent_guard.py` (`test_denial_reason_names_agent_command_clause_and_alternative`, near line 1179)

**Interfaces:** none.

- [ ] **Step 1: Add the assertion** `assert reason.startswith('readonly-agent-guard: ')` to that test.

- [ ] **Step 2: Show it can fail.** In this worktree only, change the prefix at `hooks/readonly-agent-guard.py:975` to `guard: `, run `uv run python build/run_suites.py hooks -- -k names_agent_command`, and expect FAIL on the new assertion. Then restore the file with `git checkout -- hooks/readonly-agent-guard.py`, and confirm with `git diff --exit-code hooks/readonly-agent-guard.py`. The installed guard reads the main checkout, so this edit never reaches it.

- [ ] **Step 3: Run the suite**

Run: `uv run python build/run_suites.py hooks`
Expected: `suite runs passed`, +0 tests.

- [ ] **Step 4: Commit**

```bash
git add hooks/test_readonly_agent_guard.py
git commit -m "test(hooks): pin the guard's denial prefix the live probe greps"
```

### Task 11: the Codex test-runner can run uv, and the READMEs name the dispatch guard (#16, #27)

The generator maps the read-only heading to `sandbox_mode = "read-only"` (`build/sync_runtime_assets.py:93-94`). That sandbox blocks uv's cache writes, so the Codex `test-runner` cannot run any documented suite (#16). A Codex review on 2026-11-01 hit the same block. The root `README.md` (hooks table, layout, install notes) and `hooks/README.md:7-10` omit `dispatch-model-guard.py`, so a reader who installs from the README never learns of the hook that subagent-driven-development relies on (#27).

**Files:**
- Modify: `build/sync_runtime_assets.py`, `build/test_runtime_support.py`, `README.md` (:126-131, the layout line near :37, the Hooks section :156-184), `hooks/README.md` (:7-10)
- Generated: `runtimes/codex/agents/test-runner.toml`

**Interfaces:** none.

- [ ] **Step 1: Probe the sandbox.** With `codex sandbox --help` for the flags, run `uv run --with pytest python -c 'import pytest'` from this repo under the read-only mode and under the workspace-write mode. Record both results in the report. If workspace-write lets uv write its cache, the test-runner adapter gets `sandbox_mode = "workspace-write"`. Otherwise it gets no `sandbox_mode` key and inherits the session's mode.

- [ ] **Step 2: Write the failing test** in `build/test_runtime_support.py`, beside the read-only test at line 38

```python
def test_codex_test_runner_is_not_read_only():
    data = tomllib.loads((REPO / 'runtimes/codex/agents/test-runner.toml').read_text())
    assert data.get('sandbox_mode') != 'read-only'
```

Keep the existing read-only assertion for the other read-only agents.

- [ ] **Step 3: Run it to verify it fails**

Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k test_runner_is_not_read_only`
Expected: FAIL on `'read-only' != 'read-only'`.

- [ ] **Step 4: Exempt `test-runner` in the generator.** Add a named frozenset of agents whose commands write caches, holding `test-runner`, with a comment that cites uv's cache. Emit Step 1's choice for those agents. Regenerate with `uv run --with pyyaml python build/sync_runtime_assets.py`, then check with `--check`. In `README.md:130`, say that every Codex adapter sets read-only except `test-runner`, whose test commands write caches, so its contract alone keeps it from editing.

- [ ] **Step 5: Name the dispatch guard.** In `README.md`'s layout line, Hooks section and table, and in `hooks/README.md`'s category table, add `dispatch-model-guard.py` with its event (`PreToolUse` on `Agent`), what it denies (a dispatch with no `model` to an agent type that pins none), and its install (global, like the read-only guard). Take each fact from the hook's own docstring.
Check: `/usr/bin/grep -c dispatch-model-guard README.md hooks/README.md` prints a count of at least 1 for each file (0 before).

- [ ] **Step 6: Run the gates**

Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py`, then `bash build/run_commit_lints.sh`
Expected: pass, +1 test; `commit lints passed`.

- [ ] **Step 7: Commit**

```bash
git add build/sync_runtime_assets.py build/test_runtime_support.py runtimes/codex/agents/test-runner.toml README.md hooks/README.md
git commit -m "fix(runtimes): Codex test-runner can run uv; READMEs name the dispatch guard"
```

### Task 12: micro-test kit and control arms

**Files:**
- Create: `specs/red-baseline-review-fixes/kit/run_reps.sh`, `isolation_probe.txt` and `show_reps.py`, copied from `specs/red-baseline-executing-plans-port/kit/`. The runner's temp prefix becomes `/tmp/plan76-rep-`, and comments name plan 76.
- Create: `specs/red-baseline-review-fixes/kit/cases.py`, `build_prompts.py` (same shape as plan 75's)
- Create: `specs/red-baseline-review-fixes.md` (the record)

**Interfaces:** Produces the three cases that Tasks 13, 20 and 21 run as treatment arms: `handoff-dispatch`, `stop-scope`, `fix-round-gate`.

- [ ] **Step 1: Write the three cases.** For each one, the system context is the whole file at this plan's base commit, and the user message tempts the failure without naming the case.
  - `handoff-dispatch`: context `skills/prepare-handoff/SKILL.md`. The brief is written and both reviewer templates are filled. Ask for the exact Agent tool calls the agent makes next, and nothing else. Reading rule: a rep passes when every reviewer dispatch names a subagent type and a model.
  - `stop-scope`: context `skills/executing-plans/SKILL.md`. At launch, with the partner present, pre-flight finds that Task 2 produces `load(path) -> Frame` while Task 4 consumes `load(path, *, lazy) -> Frame`. Ask what the agent does next, in one paragraph. Reading rule: a rep passes when it puts the conflict to the partner before Task 1. It fails when it rules alone, citing the five stops, or starts Task 1 first.
  - `fix-round-gate`: context `skills/subagent-driven-development/references/fix-loop.md`. Round 2 must fix a one-line bug in a repo whose `CLAUDE.md` documents per-directory suites run by `uv run python build/run_suites.py <suite>`. Ask for the test instruction in the fix dispatch. Reading rule: a rep passes when it names the covering tests and the documented suite(s) the change reaches.
- [ ] **Step 2: Write the record.** For each case, write its reading rule and its bar into `specs/red-baseline-review-fixes.md`. Treatment passes 5/5. The control must fail at least 1 of 5, or Global Constraints' stop rule applies. Commit the kit and record before running any rep.
- [ ] **Step 3: Pilot isolation.** Run `bash specs/red-baseline-review-fixes/kit/run_reps.sh specs/red-baseline-review-fixes/kit/isolation_probe.txt /tmp/plan76-probe 1 1 claude-sonnet-5-5` and confirm the rep shows no user-level context, as plan 75's Task 1 did.
- [ ] **Step 4: Run the three control arms** (five reps each, built from the base-commit text). Read every rep, score it by its committed rule, and record the scores and the spend.
- [ ] **Step 5: Commit**

```bash
git add specs/red-baseline-review-fixes specs/red-baseline-review-fixes.md
git commit -m "test(specs): micro-test kit and control arms for plan 76"
```

### Task 13: dispatch text names a model (#17, #18)

`.claude/skills/cc-guide/SKILL.md:39` dispatches `cc-guide-verifier` with no model. The globally installed `dispatch-model-guard.py` denies it, because the guard's pinned list mirrors only `agents/*.md`. So every /cc-guide packet dispatch is denied, and the deny text invites a guessed tier (#17). `skills/prepare-handoff/SKILL.md:78-79` says to dispatch the reviewers "with no model pinned", which has two readings. The literal one, omit the model, is denied by the same guard (#18).

**Files:**
- Modify: `.claude/skills/cc-guide/SKILL.md:39`, `skills/prepare-handoff/SKILL.md:78-79`
- Append: `specs/red-baseline-review-fixes.md` (`handoff-dispatch` treatment)

**Interfaces:** Consumes Task 12's `handoff-dispatch` case.

- [ ] **Step 1: Show the failure.** Run `printf '%s' '{"tool_name":"Agent","tool_input":{"subagent_type":"cc-guide-verifier","prompt":"x"}}' | python3 hooks/dispatch-model-guard.py`.
Expected: a JSON deny. With `"model":"sonnet"` added, expected: no output, exit 0.
- [ ] **Step 2: Edit `cc-guide/SKILL.md:39`.** The dispatch passes `model: sonnet`, the verifier's own pin.
- [ ] **Step 3: Edit `prepare-handoff/SKILL.md:78-79`.** Dispatch each reviewer as a read-only `general-purpose` subagent at the standard tier: `model: sonnet` on Claude Code. Name no section of another skill (that would add an install dependency).
- [ ] **Step 4: Run the `handoff-dispatch` treatment arm** (five reps on the edited text), score it by the committed rule, and append the result. The bar passes, or the stop rule in Global Constraints applies.
- [ ] **Step 5: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 6: Commit**

```bash
git add .claude/skills/cc-guide/SKILL.md skills/prepare-handoff/SKILL.md specs/red-baseline-review-fixes.md
git commit -m "fix(skills): cc-guide and prepare-handoff dispatches name a model"
```

### Task 14: worktree setup checks the right directory and respects uv (#24, #25)

The ignore check at `skills/using-git-worktrees/SKILL.md:100-106` fails two ways (#24). The OR expression tests the two conventional directories rather than the chosen location. A bare path never matches a directory-only pattern while the directory is absent, so the default `.worktrees/` case reads as not ignored, and a duplicate `.gitignore` line gets committed. Setup at `:133-135` runs `poetry install` for any `pyproject.toml`. In a uv project that fails or writes a stray Poetry environment (#25).

**Files:**
- Modify: `skills/using-git-worktrees/SKILL.md:100-106,133-135`

**Interfaces:** none.

- [ ] **Step 1: Show the failure**

Run: `d=$(mktemp -d) && git -C "$d" init -q && printf '.worktrees/\n' > "$d/.gitignore" && git -C "$d" check-ignore -q .worktrees; echo "bare=$?"; git -C "$d" check-ignore -q .worktrees/; echo "slash=$?"`
Expected: `bare=1`, `slash=0`.
- [ ] **Step 2: Edit the check** to test only the selected directory, with a trailing slash: `git check-ignore -q "$LOCATION/"`. Name `LOCATION` where the directory is chosen.
- [ ] **Step 3: Edit the Python setup.** With `uv.lock`, run `uv sync`. With `poetry.lock`, run `poetry install`. With `requirements.txt`, keep the pip line. A `pyproject.toml` with neither lock file triggers no automatic install: follow the project's README, or ask.
- [ ] **Step 4: Run the gates.** Rerun Step 1's commands with the new check form, and expect `0`. Then `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 5: Commit**

```bash
git add skills/using-git-worktrees/SKILL.md
git commit -m "fix(using-git-worktrees): check the chosen dir with a slash; uv before poetry"
```

### Task 15: rule text matches the code that enforces it (#26, #28)

`CLAUDE.md:55` defines the plan id as the highest existing id plus one. `skills/writing-plans/SKILL.md:28` defines it as the `next free:` id that `entry_check.py` prints, read across every ref. The always-loaded guide thus reintroduces the cross-branch collision (#26). `skills/writing-skills/references/discovery.md:13,22` and `skills/writing-skills/SKILL.md:382` allow uppercase names (`Skill-Name-With-Hyphens`), while `build/check_frontmatter.py:402` and the spec require a lowercase name equal to the directory name (#28).

**Files:**
- Modify: `CLAUDE.md:55`, `skills/writing-skills/references/discovery.md:13,22`, `skills/writing-skills/SKILL.md:382`

**Interfaces:** none.

- [ ] **Step 1: Show the failure.** Run `/usr/bin/grep -n "max existing id" CLAUDE.md` and `/usr/bin/grep -n "Skill-Name-With-Hyphens\|letters, numbers" skills/writing-skills/references/discovery.md skills/writing-skills/SKILL.md`, and quote the lint's rule at `build/check_frontmatter.py:402`.
- [ ] **Step 2: Edit `CLAUDE.md:55`.** The id is the `next free:` id that writing-plans' `entry_check.py` prints. Point to writing-plans rather than restating the script's logic.
- [ ] **Step 3: Edit the writing-skills lines.** A name uses lowercase letters, digits and hyphens, and equals the skill's directory name. The template's example becomes `skill-name-with-hyphens`.
- [ ] **Step 4: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed` (`check_conformance` and the cc_guide lint cover `CLAUDE.md`).
- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md skills/writing-skills/references/discovery.md skills/writing-skills/SKILL.md
git commit -m "docs: plan-id and skill-name rules match the code that enforces them"
```

### Task 16: parked stages age, and synthesis works outside agent-skills (#29, #30)

`skills/derive-roadmap/SKILL.md:161-163` appends parked stages to the backlog without the dated item schema. `deferred_stats.py` then counts them as age unknown, and they never reach the aged-tail gate (#29). `skills/describe-critique-methodology/references/spec-synthesis.md:32-36` tells Synthesize mode, which runs in a target repo, to read exemplars in agent-skills' `specs/completed/`. Those files do not exist there (#30).

**Files:**
- Modify: `skills/derive-roadmap/SKILL.md:161-163`, `skills/describe-critique-methodology/references/spec-synthesis.md:32-36`

**Interfaces:** none.

- [ ] **Step 1: Show the failure.** Write a scratch backlog file holding one parked-stage item the way `:161-163` describes it, then run `uv run skills/writing-plans/scripts/deferred_stats.py --file <scratch file> --json`. Expected: the item counts in `undated_open`.
- [ ] **Step 2: Edit `derive-roadmap/SKILL.md`.** Each parked stage becomes one item under a dated `## <roadmap-name> — <YYYY-MM-DD>` section, following writing-plans' Deferred-item schema (`references/deferred-backlog.md`), with `Done when:` naming the stage's Produces. Name the schema by skill and file. If that adds a path into another skill, mirror it in `install.py`'s `DEPENDENCIES`, or in `build/test_runtime_support.py`'s `SOFT_REFERENCES` with a reason.
- [ ] **Step 3: Edit `spec-synthesis.md`.** Keep the two exemplars as the first choice when the agent-skills repo is at hand. Otherwise, the skeleton listed in the same paragraph is the format.
- [ ] **Step 4: Run the gates.** Rerun Step 1 with the new form, and expect `undated_open` to be 0. Then `bash build/run_commit_lints.sh`.
- [ ] **Step 5: Commit**

```bash
git add skills/derive-roadmap/SKILL.md skills/describe-critique-methodology/references/spec-synthesis.md   # plus install.py or build/test_runtime_support.py if Step 2 needed it
git commit -m "fix(skills): parked stages carry the item schema; synthesis has a fallback"
```

### Task 17: the nested-CV example carries the label horizon (#31)

`skills/tune-hyperparameters/SKILL.md:193-197` drops the `label_horizon` that the main recipe carries at `:127`. For a multi-period target, the recommended guard leaks.

**Files:**
- Modify: `skills/tune-hyperparameters/SKILL.md:193-197`

**Interfaces:** none.

- [ ] **Step 1: Show the failure.** The class docstring sets `train = [0, s_k - max(embargo, label_horizon))`. From `skills/tune-hyperparameters/scripts`, a one-off `uv run python -c` over 60 rows prints the first fold's last training index. Expect `s_k - 3` for `PurgedTimeSeriesSplit(n_splits=4, embargo=2)`, and `s_k - 4` with `label_horizon=3`. For a 3-period target, the first split keeps a row whose label overlaps validation.
- [ ] **Step 2: Pass `label_horizon=h`** to both the outer and the inner splitter in the example.
- [ ] **Step 3: Run the gates.** `uv run python build/check_snippets.py skills/tune-hyperparameters/` and `bash build/run_commit_lints.sh`.
- [ ] **Step 4: Commit**

```bash
git add skills/tune-hyperparameters/SKILL.md
git commit -m "fix(tune-hyperparameters): nested CV carries the label horizon"
```

### Task 18: bayesian-workflow's report and references match what the code does (#32-#37)

- #32: `summary.csv` and `forest.png` use ArviZ defaults. On the pinned 1.3.0 those are an 89% equal-tailed interval and a mean point estimate, while `SKILL.md:77` and `references/reporting.md:146,232,287` label the column "94% HDI".
- #33: `references/diagnostics.md:30,41-44` and `SKILL.md:35,78` say `azs.diagnose` enforces the skill's ESS thresholds, but arviz-stats gates tail ESS only at 0.001 of the draws.
- #34: `reporting.md:184` calls a preference robust at ΔELPD > 2 × SE, while `references/model-comparison.md:83-89` says |ΔELPD| < 4 is small whatever the SE.
- #35: `reporting.md:136,144` describe rank-vline plots and median points, while the template renders `plot_trace` and ArviZ's default mean.
- #36: `references/svi.md:69` reads sites `("beta", "sigma")` from the model template, whose sites are `mu` and `sigma`, so the pointer leads to KeyError.
- #37: `references/model-template.md:68`, `SKILL.md:81` and `diagnostics.md:208` save `model_output.nc`, while reporting, utility-scripts and track-model-experiments expect `<slug>/inference_data.nc`. A variant saved from the template is never compared.

**Files:**
- Modify: `skills/bayesian-workflow/SKILL.md`, `references/reporting.md`, `references/diagnostics.md`, `references/svi.md`, `references/model-template.md`

**Interfaces:** none.

- [ ] **Step 1: Show the failures.** Run `uv run python build/versions.py run snippets -- python -c "import arviz as az; print(az.rcParams['stats.ci_prob'], az.rcParams['stats.ci_kind'], az.rcParams['stats.point_estimate'])"` and expect `0.89 eti mean`. Run `/usr/bin/grep -rn "model_output.nc" skills/bayesian-workflow` and expect hits. Run `/usr/bin/grep -n 'numpyro.sample("' skills/bayesian-workflow/references/model-template.md` and expect no `beta` site.
- [ ] **Step 2: #32 and #35.** In `reporting.md`'s figure block, set `az.rcParams['stats.ci_prob'] = 0.94` and `az.rcParams['stats.ci_kind'] = 'hdi'` once, before `summary.csv` and the forest plot. Make `:136,144` describe what the block renders (trace plot, mean point) or change the block to render what they describe. Pick one and state which in the report.
- [ ] **Step 3: #33.** State that `azs.diagnose`'s defaults gate bulk ESS and R-hat but tail ESS only at 0.001 of the draws. Require an explicit tail-ESS check against the skill's threshold before interpreting tails or intervals. Change `SKILL.md:35,78` to match.
- [ ] **Step 4: #34.** `reporting.md:184` follows `model-comparison.md:83-89`.
- [ ] **Step 5: #36 and #37.** `svi.md:69` uses the template's site names. Every save path becomes `<slug>/inference_data.nc`.
- [ ] **Step 6: Run the snippet tiers**

Run the three snippet commands from the root `CLAUDE.md` on `skills/bayesian-workflow/`, then `bash build/run_commit_lints.sh`.
Expected: each tier exits 0 (Tier 3 takes minutes); `commit lints passed`.
- [ ] **Step 7: Commit**

```bash
git add skills/bayesian-workflow
git commit -m "fix(bayesian-workflow): report labels, diagnose limits and save paths match the code"
```

### Task 19: recommend-probabilistic-model hands off bayesian-workflow's priors and the right zero test (#38, #39)

`references/families/hierarchical.md:18,23` and `references/families/timeseries-statespace.md:25` hand off half-Cauchy scale priors that bayesian-workflow's `SKILL.md:118` tells the agent to replace (#38). `references/decision-map.md:33` and `references/families/regression-glm.md:24` route a raw high zero fraction to zero-inflated models. The test is zeros beyond what Poisson or NB predicts at the observed mean (#39).

**Files:**
- Modify: `skills/recommend-probabilistic-model/references/families/hierarchical.md:18,23`, `references/families/timeseries-statespace.md:25`, `references/decision-map.md:33`, `references/families/regression-glm.md:24`

**Interfaces:** none.

- [ ] **Step 1: Show the failure.** Run `/usr/bin/grep -n -i "cauchy" skills/recommend-probabilistic-model/references/families/*.md` and quote `skills/bayesian-workflow/SKILL.md:118`. Count target `[0]*60 + [1]*30 + [2]*10` has a 60% zero share, while a Poisson at its mean of 0.5 predicts 61%. The decision map routes it to zero-inflation anyway.
- [ ] **Step 2: Hand off half-normal (or exponential) scale priors**, the form bayesian-workflow recommends. Keep each existing `PML` citation and notebook link unchanged (Global Constraints, Citations).
- [ ] **Step 3: Route on excess zeros.** Compare the observed zero share with the Poisson `exp(-mean)` and, under overdispersion, the NB zero share at the fitted mean.
- [ ] **Step 4: Run the gates.** `uv run python build/check_snippets.py skills/recommend-probabilistic-model/` and `bash build/run_commit_lints.sh`.
- [ ] **Step 5: Commit**

```bash
git add skills/recommend-probabilistic-model/references
git commit -m "fix(recommend-probabilistic-model): hand off workflow priors; route on excess zeros"
```

### Task 20: executing-plans finds its workspace, counts batched tasks and scopes its stops (#19, #21, #22)

- #19: `skills/executing-plans/SKILL.md:138` runs the bare `../subagent-driven-development/scripts/sdd-workspace PLAN_FILE`, which does not resolve from the repo root, where the agent runs. `references/final-review.md:86-87` then says to re-run it after protocol step 5 has moved the plan with `git mv`, and `sdd-workspace:29` exits 2 on a missing plan file.
- #21: `SKILL.md:144-147` counts a task done only on a `Task <N>: complete` line, while subagent-driven-development's `references/batching.md:35-41` writes `Tasks 4-7: complete` and `Tasks 2, 5, 9: complete`. An executor switch after a batch redoes the batched tasks.
- #22: `SKILL.md:50` says five things stop the agent "and only these", while pre-flight at `:189-191` sends a conflict to the partner before Task 1.

**Files:**
- Modify: `skills/executing-plans/SKILL.md` (:50, :138, :144-147), `skills/executing-plans/references/final-review.md:86-87`
- Append: `specs/red-baseline-review-fixes.md` (`stop-scope` treatment)

**Interfaces:** Consumes Task 12's `stop-scope` case. The ledger formats stay as subagent-driven-development writes them.

- [ ] **Step 1: Show the failures.** From the repo root, `../subagent-driven-development/scripts/sdd-workspace specs/plans/76-whole-repo-review-fixes.md` fails (no such file). `skills/subagent-driven-development/scripts/sdd-workspace specs/plans/completed/none.md` exits 2. Quote `batching.md:35-41` beside `SKILL.md:144-147`.
- [ ] **Step 2: #19.** Anchor the call as `<this-skill-dir>/../subagent-driven-development/scripts/sdd-workspace`, the form subagent-driven-development uses for its own scripts. `final-review.md`'s re-run names the plan's retired path, `specs/plans/completed/<file>`. The workspace is named from the basename, so it is the same workspace.
- [ ] **Step 3: #21.** A task is done when a `complete` line lists its number, whether alone (`Task 4:`), as a range (`Tasks 4-7:`) or as a list (`Tasks 2, 5, 9:`).
- [ ] **Step 4: #22.** Scope the lead-in at `:50` to the run after pre-flight (for example, "Once Task 1 starts, five things stop you, and only these"). The numbered list stays byte-identical.
- [ ] **Step 5: Run the `stop-scope` treatment arm**, score it, and append it to the record.
- [ ] **Step 6: Run the gates.** Measure the body: 18,500 characters at most. Then `uv run python build/run_suites.py executing-plans` and `bash build/run_commit_lints.sh`.
- [ ] **Step 7: Commit**

```bash
git add skills/executing-plans specs/red-baseline-review-fixes.md
git commit -m "fix(executing-plans): anchor the workspace script, count batched tasks, scope the stops"
```

### Task 21: subagent-driven-development keeps its workspace path across tool calls and has one fix-round gate (#20, #23)

- #20: `skills/subagent-driven-development/SKILL.md:264` captures the workspace as `WORKSPACE=$(…)`, which hides the printed path. Shell state does not persist across tool calls, so a later `cat "$WORKSPACE/progress.md"` finds no ledger, and the controller re-dispatches finished tasks. `references/final-review.md:44-47`'s `rm -rf "$WORKSPACE"` then deletes nothing. Its re-run after a `/clear` names the plan path that protocol step 5 has already moved.
- #23: `references/fix-loop.md:67` says a one-line fix does not need the whole suite, while `implementer-prompt.md:51` and test-driven-development's `SKILL.md:178-183` require the documented suites before a change is done. That is two completion gates. This settles the open backlog item "TDD 'run the documented suite' against `fix-loop.md`'s one-line-fix rule (plan 75 Task 2)" in `specs/deferred_items.md`. Plan completion ticks it.

**Files:**
- Modify: `skills/subagent-driven-development/SKILL.md:262-267`, `references/final-review.md:44-48`, `references/fix-loop.md:64-70`
- Append: `specs/red-baseline-review-fixes.md` (`fix-round-gate` treatment)

**Interfaces:** Consumes Task 12's `fix-round-gate` case.

- [ ] **Step 1: Show the failure.** Run two separate Bash tool calls: `WORKSPACE=/tmp/x`, then `echo "[$WORKSPACE]"`. Expect `[]`. Quote `fix-loop.md:67` beside `implementer-prompt.md:50-51`.
- [ ] **Step 2: #20.** Run the script without capture, so its printed path shows. Record that path in the ledger's first lines, or in the controller's notes, and write it out literally in every later command. `final-review.md` deletes that literal path. Its re-run names `specs/plans/completed/<file>`. Keep the body inside the compaction window (about 800 characters of headroom).
- [ ] **Step 3: #23** (Open for plan review, item 3). `fix-loop.md` says a fix round runs its covering tests while it iterates, and runs the documented suite(s) the change can reach once before it writes the fix report. The report names both commands and their output. The five-stop list stays byte-identical.
- [ ] **Step 4: Run the `fix-round-gate` treatment arm**, score it, and append it to the record.
- [ ] **Step 5: Run the gates.** Measure the body, then `uv run python build/run_suites.py subagent-driven-development` and `bash build/run_commit_lints.sh`.
- [ ] **Step 6: Commit**

```bash
git add skills/subagent-driven-development specs/red-baseline-review-fixes.md
git commit -m "fix(subagent-driven-development): keep the workspace path literal; one fix-round gate"
```

### Task 22: stable_digits carries the reading the owner picks (#9) — waits for the owner

`skills/bayesian-workflow/scripts/diagnose_model.py:391` computes `stable_digits = floor(-log10(mcse / sd))`, which ignores the size of the mean. `references/reporting.md:237` says never to print more significant digits than this, and it puts the rounding unit at about 2 × MCSE or more. Take mean 2.31, sd 0.05 and MCSE 0.0011. The field gives 1, so the report prints "2", though 2.31 is stable. A near-zero mean (0.004, same sd and MCSE) also gets 1 digit, which a new seed would change.

| Reading | Formula | Case 2.31 | Case 0.004 |
|---|---|---|---|
| A: significant digits of the mean | `max(0, floor(log10(abs(mean))) + 1 + floor(-log10(2 * mcse)))` | 3 → "2.31" | 0 → no stable digit |
| B: decimal places (field renamed `stable_decimals`) | `max(0, floor(-log10(2 * mcse)))` | 2 → "2.31" | 2 → "0.00" |

**Files:**
- Modify: `skills/bayesian-workflow/scripts/diagnose_model.py:378-400`, `scripts/check_diagnostics.py:590`, `references/reporting.md:151,237`
- Test: `skills/bayesian-workflow/scripts/test_diagnose_model.py`, `scripts/test_check_diagnostics.py`

**Interfaces:** Changes the `diagnostics.json → precision` field: its meaning under A, its name and meaning under B (`min_stable_digits` follows).

- [ ] **Step 1: Read the owner's pick** from `## Decisions`. If none is logged, stop and ask: this task never runs on a guess.
- [ ] **Step 2: Write the failing tests** for the picked row of the table: both cases, plus the existing tests that pin the sd-relative value, which change with it.
- [ ] **Step 3: Run them to verify they fail**, with `uv run python build/run_suites.py bayesian-workflow -- -k "stable or precision"`.
- [ ] **Step 4: Implement the picked formula**, and update `check_diagnostics.py:590` and `reporting.md:151,237` to the field's name and meaning.
- [ ] **Step 5: Run the suite and the snippet tiers** for `skills/bayesian-workflow/`, then `bash build/run_commit_lints.sh`.
- [ ] **Step 6: Commit**

```bash
git add skills/bayesian-workflow
git commit -m "fix(bayesian-workflow): stable_digits follows the MCSE rounding rule"
```

### Task 23: NOTICE records the changes to adapted superpowers files

**Files:**
- Modify: `NOTICE` (superpowers "Changes from upstream:" list)

**Interfaces:** Consumes the landed Tasks 1, 2, 14, 15 (the writing-skills part), 20 and 21.

- [ ] **Step 1: Add one change-list entry** in the list's style. Name the plan, and give one clause per changed behavior: find-polluter's exit 2 on a runner that cannot start and its line-safe loop; start-server's missing-value check and absolute project dir; using-git-worktrees' slash check and uv-first setup; writing-skills' lowercase name rule; executing-plans' anchored script, batched-line count and stop scope; subagent-driven-development's literal workspace path and single fix-round gate. Say that no upstream text was taken.
- [ ] **Step 2: Run the gates.** `uv run python build/check_provenance.py` and `bash build/run_commit_lints.sh`.
- [ ] **Step 3: Commit**

```bash
git add NOTICE
git commit -m "docs(notice): record plan 76's changes to adapted superpowers files"
```

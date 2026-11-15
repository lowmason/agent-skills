# Guide sections created after `baseline init` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let a guide section created after `baseline init` enter `baseline.json` (`baseline add`) and a removed one leave it (`baseline drop`), make `lint` name those commands, and cut the history tests and `init` loose from the working-tree guide.

**Architecture:** `build/cc_guide/baseline.py` gains a history constant `ANCHORED` (the guide at `18b4a71`), which replaces the working-tree guide as `derive_changed`'s third input, and two pure functions, `add` and `drop`, that return a new state. `cli.py` wires them as `baseline add` and `baseline drop`, and `lint.id_set_problems` prints them. The history tests read `18b4a71` from git. The two retired specs take the approved amendments.

**Tech Stack:** Python as pinned in `build/versions.toml`, stdlib, pytest; git (history and fixture repos); the repo's commit lints (`build/run_commit_lints.sh`).

**Spec:** `specs/cc-guide-sections-after-init.md` (APPROVED 2026-11-15). Its Design (S1 to S5), Testing, Spec amendments and Constraints are authoritative. Read it in full before Task 1. "Drift R<n>" names a requirement of `specs/completed/claude-code-drift-automation-spec.md`, and "conformance R<n>" one of `specs/completed/claude-code-guide-conformance.md`.

## Global Constraints

### Base and execution

- **Base branch.** The spec and this plan exist only on `claude/laughing-moser-a9a327` (it holds the spec branch's `debdb76`, `17c43a1` and `a4946ae`) until that branch merges. Cut the execution worktree from `refs/heads/claude/laughing-moser-a9a327`, or from `main` after the merge.
- **Base commit.** Every line number in this plan is a line of the file at `a4946ae`. Before Task 1, run `git diff --stat a4946ae HEAD -- build/cc_guide build/test_check_conformance.py build/CLAUDE.md specs/completed/claude-code-drift-automation-spec.md specs/completed/claude-code-guide-conformance.md`. No output, or only `build/cc_guide/baseline.json`, which no task edits, means the line numbers hold. Any other output means a file this plan edits changed after planning: re-read each cited line before a task quotes it.
- **Moving files on another branch.** The sibling `/cc-guide` branch `claude/vibrant-bartik-7c3f5c` edits the live guide, `build/cc_guide/baseline.json`, `specs/deferred_items.md` and `specs/history.md`. Leave that branch and its worktree (`.claude/worktrees/heuristic-stonebraker-8f62cb`) alone. No test may depend on the live guide's or `baseline.json`'s current content.
- **Owner gates.** No push and no PR without the owner's word.
- **Test counts** are stated as deltas, never as suite totals.

### From the spec's Constraints (verbatim)

- Only `baseline` writes `baseline.json` (drift R2.1). Every subcommand leaves its changes uncommitted (R7).
- `build/cc_guide/` imports nothing from `build/`, and its tests are offline, with bare imports and basenames unique across `build/` (drift R12.1).
- The repo's Python style (`rules/clean-code-python.md`): single quotes, f-strings, 4-space indentation.
- No live section changes. The guide, `manifest.toml` and `baseline.json` stay as they are. Tests use fixtures.
- Prose in the specs and `build/CLAUDE.md` follows the plain technical English rule (`rules/write-with-asd-ste100.md`).
- Provenance: the drift detector is the owner's original code (MIT, `LICENSE`). This work brings in no outside text or code, so `NOTICE` does not change.

### Commands

- cc_guide suite: `uv run python build/run_suites.py cc_guide`. One node: `uv run python build/run_suites.py cc_guide -- test_baseline.py::<name>`. The suite runs pytest from `build/cc_guide/`.
- build suite: `uv run python build/run_suites.py build`. One node: `uv run python build/run_suites.py build -- test_check_conformance.py::<name>`. It runs from `build/` and collects `build/cc_guide/` too.

### Pinned names and messages

These are fixed for every task. Tests assert them exactly.

| Name | Value |
|---|---|
| `baseline.ANCHORED` | `('18b4a71', 'specs/guides/claude-code-customization-guide.md')` |
| `add` refusal, ID not anchored | `baseline add: not a guide anchor: <ids>` |
| `add` refusal, ID in no group | `baseline add: in no manifest.toml group: <ids>` |
| `add` refusal, ID already stored | `baseline add: already in baseline.json: <ids>` |
| `add` refusal, citation broken | `baseline add needs every citation to parse (R2.4); fix these first:` then one problem per line |
| `drop` refusal, still anchored | `baseline drop: still a guide anchor: <ids>` |
| `drop` refusal, still in a group | `baseline drop: still in a manifest.toml group: <ids>` |
| `drop` refusal, ID not stored | `unknown section IDs: <ids>` (the existing `baseline.known`) |
| `drop` refusal, nothing left | `baseline drop: would leave baseline.json with no section` |
| lint, ID in the guide and manifest only | `section <id>: missing from baseline.json; add it with` then `` `<CLI> baseline add <id>` `` |
| lint, ID in `baseline.json` only | `section <id>: missing from the guide and manifest.toml; drop it with` then `` `<CLI> baseline drop <id>` `` |

`<ids>` is the failing IDs, comma-and-space joined, in argument order, each once. `<CLI>` is `lint.CLI`, `uv run python build/cc_guide/cli.py`. A refusal checks in the table's order, and the first check that fails raises with every ID that fails it. The CLI prints a refusal as `cc-guide: <message>` on stderr, exits 2 and writes nothing.

## Review Focus

1. **An entry waiting for `drop`, when `add` runs.** `baseline.json` holds an ID that the guide and the manifest no longer have. `add` rebuilds `sections` in the guide's heading order, so that entry could vanish. It must survive with its values unchanged, after the guide-ordered entries. Test: Task 3, `test_add_keeps_an_entry_waiting_for_drop`.
2. **`add`, then `lint`, with no `stamp`.** The editor runs the flow's step 3 and lints. `lint` exits 0, and `add` prints no stale-stamp line. Test: Task 3, `test_add_writes_only_the_new_entry_and_lint_passes_with_no_stamp`.
3. **The S1 flow when the new section's terms select a block.** `check` exits 1 and names the block as `new` with the new section as its candidate. After `rebaseline`, `check` and `lint` exit 0. Test: Task 3, `test_a_section_created_after_init_reaches_check_exit_zero`.
4. **Dropping the section that holds the oldest `checked`.** `drop` prints the stale-stamp line. Then `stamp` and `lint` clear it. Test: Task 4, `test_drop_writes_only_the_baseline_and_a_moved_oldest_needs_stamp`.
5. **The editor runs the command `lint` prints.** It clears the violation, for `add` and for `drop`. Test: Task 5, `test_running_the_command_lint_prints_clears_the_id_set_violation`.

## Decisions

None.

---

### Task 1: The `18b4a71` history reference in `init` (S4)

**Files:**
- Modify: `build/cc_guide/baseline.py:14-18` (constant), `:34-38` (`derive_changed` docstring), `:70-84` (`init`)
- Modify: `build/cc_guide/cli.py:311-312`
- Modify: `build/cc_guide/cc_fixtures.py` (new fixtures, after `MANIFEST_TOML`)
- Test: `build/cc_guide/test_baseline.py`, `build/cc_guide/test_cli.py:242-257` (`history_repo`)

**Interfaces:**
- Produces: `baseline.ANCHORED: tuple[str, str]` (pinned above). `baseline.init(manifest, guide_text, docs, release, day, changed)` keeps its signature; a section that `changed` lacks takes `release`.
- Produces (fixtures, `cc_fixtures.py`): `EXTRA_ID = 'alpha.extra'`; `with_extra(text: str) -> str`, the text with this block inserted before the line `## 2. Beta`: `### Extra`, `<!-- cc: alpha.extra -->`, a blank line, `` Extra reads `PIPE_ENV`. ``, a blank line; `EXTRA_MANIFEST: str`, `MANIFEST_TOML` with `'alpha.extra'` appended to group alpha's `sections`. The insertion leaves `alpha.reference`'s `text_hash` unchanged, since the hash collapses whitespace.

- [ ] **Step 1: Write the failing tests**

In `cc_fixtures.py`, add `EXTRA_ID`, `with_extra` and `EXTRA_MANIFEST` as Interfaces states. Import `with_extra` and `EXTRA_MANIFEST` in `test_baseline.py` and `test_cli.py`.

In `test_cli.py`, change `history_repo`: after its third commit, capture `anchored = git(repo, 'rev-parse', 'HEAD').strip()` and add `monkeypatch.setattr(baseline, 'ANCHORED', (anchored, GUIDE_PATH))`. Its docstring names the third commit as the stand-in for `18b4a71`. Then add:

```python
def test_init_takes_a_heading_edit_and_a_section_created_after_the_bootstrap(tmp_path, docs_dir, monkeypatch):
    '''S4: the guide at ANCHORED maps headings to IDs, so a heading edit and a
    later section in the working tree no longer refuse; the later section
    takes --release.'''
    repo = history_repo(tmp_path, monkeypatch)
    edited = guide_text().replace('### Reference ⚠\n<!-- cc: beta.reference', '### Beta reference\n<!-- cc: beta.reference')
    write_tree(repo, {GUIDE_PATH: with_extra(edited), state.MANIFEST: EXTRA_MANIFEST})
    assert main(tmp_path / 'cache', 'baseline', 'init', '--docs', str(docs_dir), '--release', '2.1.900',
                '--date', '2026-09-02') == 0
    written = load(repo)['sections']
    assert list(written) == ['alpha.overview', 'alpha.reference', 'alpha.extra', 'beta.overview', 'beta.reference']
    assert {i: s['changed'] for i, s in written.items()} == {
        'alpha.overview': '2.1.219', 'alpha.reference': '2.1.288', 'alpha.extra': '2.1.900',
        'beta.overview': '2.1.219', 'beta.reference': '2.1.219'}
```

In `test_baseline.py`, add:

```python
def test_init_gives_a_section_without_a_derived_changed_its_release(docs_dir):
    s = baseline.init(state.parse_manifest(EXTRA_MANIFEST), with_extra(guide_text()), docs_dir,
                      '2.1.900', '2026-09-02', FIXTURE_CHANGED)
    assert s['sections']['alpha.extra']['changed'] == '2.1.900'
    assert {i: v['changed'] for i, v in s['sections'].items() if i != 'alpha.extra'} == FIXTURE_CHANGED
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run python build/run_suites.py cc_guide -- test_baseline.py test_cli.py -k init`
Expected: the new unit test fails with `KeyError: 'alpha.extra'`. Every test that uses `history_repo` errors at `monkeypatch.setattr` with `AttributeError`, since `baseline` has no `ANCHORED` yet. The other selected tests pass.

- [ ] **Step 3: Add `ANCHORED` and the `--release` fallback**

- `baseline.py`: add `ANCHORED` beside `JULY` and `REFRESH`. Its comment says: R11.1's map from heading to ID; plan 35's commit, the first guide with anchors; its `##` and `###` headings are identical to the refresh's; the path differs from `OLD_GUIDE_PATH` because `79ad04f` moved the guide before `18b4a71`.
- `derive_changed`: signature unchanged. Its docstring says the third input is the guide at `ANCHORED`, that the result keys the 38 bootstrap IDs, and that the refusal of a section the refresh lacks guards the `ANCHORED` constant.
- `init`: each section's `changed` is `changed.get(s.id, release)`. The docstring says a section that `changed` lacks was created after the bootstrap and takes `release`, since `init` baselines every section's text at `release` (spec S4, designer's call 7).
- `cli.py:311-312`: pass `git_show(*baseline.ANCHORED)` as `derive_changed`'s third input, in place of `guide_text`. `git_show`'s error text stays as it is.

- [ ] **Step 4: Run the suite to verify it passes**

Run: `uv run python build/run_suites.py cc_guide`
Expected: PASS, +2 tests.

- [ ] **Step 5: Commit**

```bash
git add build/cc_guide/baseline.py build/cc_guide/cli.py build/cc_guide/cc_fixtures.py build/cc_guide/test_baseline.py build/cc_guide/test_cli.py
git commit -m "feat(cc_guide): map headings to IDs through the guide at 18b4a71 in baseline init"
```

### Task 2: History tests read `18b4a71`, not the working tree (S5)

**Files:**
- Modify: `build/cc_guide/test_baseline.py:62-110` (`history`, its skip test, the two history tests)
- Modify: `build/test_check_conformance.py:1-16` (imports, a constant) and `:86-93` (`test_real_guide_carries_the_drift_r11_anchors`)

**Interfaces:**
- Consumes: `baseline.ANCHORED` (Task 1).
- Produces: `history(ref: str, path: str) -> str` in `test_baseline.py`. The path is a required argument: a default bound at definition time would make the skip test's monkeypatch a no-op.

- [ ] **Step 1: Write the failing tests**

Both tests patch `Path.read_text` so that the working-tree guide reads edited, then call the existing tests. Today those tests read the working tree, so they fail. After Step 3 they never read it, so they pass.

In `test_baseline.py` (add `import re`):

```python
def test_the_history_tests_pass_with_the_working_tree_guide_edited(monkeypatch):
    '''G3: a heading edit and a section created after init change neither
    history test, since neither reads the working-tree guide.'''
    guide_file = (REPO / 'specs/guides/claude-code-customization-guide.md').resolve()
    real = Path.read_text

    def edited(self, *args, **kwargs):
        text = real(self, *args, **kwargs)
        if self.resolve() != guide_file:
            return text
        return re.sub(r'(?m)^(##+ .+)$', r'\1 (edited)', text) + '\n## Added later\n<!-- cc: added.later -->\n'
    monkeypatch.setattr(Path, 'read_text', edited)
    test_r11_derivation_from_the_real_history()
    test_the_replay_flags_the_citers_of_drifted_sections_and_not_the_control()
```

In `test_check_conformance.py` (add `from pathlib import Path`):

```python
def test_the_r12_pin_passes_with_a_section_added_to_the_working_tree_guide(monkeypatch):
    '''Spec S5: the pin reads the bootstrap record, so a section created after
    init leaves it passing.'''
    guide_file = (cc.REPO / GUIDE).resolve()
    real = Path.read_text

    def added(self, *args, **kwargs):
        text = real(self, *args, **kwargs)
        return text + '\n## Added later\n<!-- cc: added.later -->\n' if self.resolve() == guide_file else text
    monkeypatch.setattr(Path, 'read_text', added)
    test_real_guide_carries_the_drift_r11_anchors()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run python build/run_suites.py cc_guide -- test_baseline.py::test_the_history_tests_pass_with_the_working_tree_guide_edited`
Expected: FAIL with `SetupError: R11.1: section … is not in the c33bc99 guide`.

Run: `uv run python build/run_suites.py build -- test_check_conformance.py::test_the_r12_pin_passes_with_a_section_added_to_the_working_tree_guide`
Expected: FAIL on `assert len(sections) == 38` (39 found).

A SKIP in place of a FAIL means this clone lacks `91474f6`, `c33bc99` or `18b4a71`. RED is then not shown: stop and report.

- [ ] **Step 3: Read the guide at `18b4a71` in all three tests**

- `test_baseline.py`: `history(ref, path)` runs `git cat-file -e` and `git show {ref}:{path}` as today, and skips or fails as today. `test_history_skips_only_for_a_commit_this_clone_lacks` calls `history('0' * 40, baseline.OLD_GUIDE_PATH)` and `history('HEAD', 'no/such/guide.md')` and drops its monkeypatch. The two history tests read July and the refresh with `history(baseline.JULY[0], baseline.OLD_GUIDE_PATH)` and `history(baseline.REFRESH[0], baseline.OLD_GUIDE_PATH)`, and the third input with `history(*baseline.ANCHORED)`. Their assertions stay as they are.
- `test_check_conformance.py`: add `ANCHORED_REF = '18b4a71'` beside `GUIDE`. Its comment says that it restates `baseline.ANCHORED` in `cc_guide/baseline.py`, plan 35's commit, the first with anchors, and that the restatement keeps this file free of an import from `cc_guide/` that only works after `check_conformance` sets `sys.path`. Add a helper `anchored_guide() -> str` that runs `git cat-file -e` and `git show` in `cc.REPO` as `history()` does. It skips with the reason `18b4a71 is not in this clone (a shallow clone?)` when the commit is missing, and fails on any other git error. `test_real_guide_carries_the_drift_r11_anchors` reads `anchored_guide()`. Its three assertions stay. Its docstring says it pins the bootstrap record, and that `check_conformance.py` and `cli.py lint` keep the working tree's anchors covered.

- [ ] **Step 4: Run both suites to verify they pass**

Run: `uv run python build/run_suites.py cc_guide`
Expected: PASS, +1 test.

Run: `uv run python build/run_suites.py build -- test_check_conformance.py`
Expected: PASS, +1 test.

- [ ] **Step 5: Commit**

```bash
git add build/cc_guide/test_baseline.py build/test_check_conformance.py
git commit -m "test(cc_guide): read the bootstrap guide at 18b4a71 in the history tests"
```

### Task 3: `baseline add` (S1)

**Files:**
- Modify: `build/cc_guide/guide.py:179-189` (`render_stamp`, two key functions before it)
- Modify: `build/cc_guide/baseline.py` (new `add`, after `accept`)
- Modify: `build/cc_guide/cli.py:2-110` (docstring), `:182-189` (parser), `:341-352` (accept's preamble, then the `add` branch)
- Test: `build/cc_guide/test_baseline.py`, `build/cc_guide/test_cli.py`

**Interfaces:**
- Consumes: `with_extra`, `EXTRA_MANIFEST` (Task 1).
- Produces:
  - `guide.checked_order(stamp: dict) -> tuple`: `(version_key(release), date)`. `guide.audited_order(stamp: dict) -> tuple`: `(date, version_key(release))`. `render_stamp` takes its two minimums with these keys, so the stamp's order and `add`'s order cannot drift apart.
  - `baseline.add(state: dict, manifest: Manifest, guide_text: str, ids, newest: str, citer_stamps: dict[str, list[str]]) -> dict`.
  - `cli.review_stamps(tree: Source, guide: str, action: str) -> dict[str, list[str]]`: each section's citers' review stamps. A citation problem raises `SetupError(f'{action} needs every citation to parse (R2.4); fix these first:\n' + '\n'.join(problems))`. The substantive `accept` calls it with `'a substantive accept'`, so its message stays byte-identical.

`add`'s rules, beyond the pinned refusals:
- `text_hash`: `guide.text_hash` of the section's text.
- `checked`: `min(..., key=checked_order)` over the `checked` of the group's sections that `state` already has. `audited`: the same with `audited_order`. With no such section, both take the minimum over the whole file (designer's call 4).
- `changed`: `next_changed(newest, citer_stamps.get(sid, []))`.
- Every ID reads `state` as it was before the run. The input is never mutated.
- `sections` order: the guide's heading order for every ID the guide anchors, then each stored ID the guide lacks, in its current order (Review Focus 1).
- Validate each named ID on its own. Do not call `check_ids`: an unrelated half-edited section must not refuse `add`.

- [ ] **Step 1: Write the failing unit tests**

In `test_baseline.py` (add `import copy`), define at module level:

```python
EXTRA = state.parse_manifest(EXTRA_MANIFEST)
GAMMA_MANIFEST = MANIFEST_TOML.replace('[[exclusion]]', "[groups.gamma]\nsections = ['gamma.overview']\nterms = ['env-vars']\n\n[[exclusion]]")
GAMMA_GUIDE = guide_text() + '## 3. Gamma\n<!-- cc: gamma.overview -->\n\nGamma reads `PIPE_ENV`.\n'


def section_hash(text, sid):
    return guide.text_hash({s.id: s for s in guide.sections(text)}[sid].text)
```

Tests:

```python
def test_add_copies_the_groups_oldest_checked_and_audited_in_the_stamps_order(docs_dir):
    '''D4 and D1: by release, alpha's oldest checked is alpha.reference's; by
    date, its oldest audited is alpha.overview's. The other order would pick
    the other section, and beta's older values stay out.'''
    s = fixture_state(docs_dir)
    a = s['sections']
    a['alpha.overview']['checked'] = {'release': '2.1.901', 'date': '2026-09-01'}
    a['alpha.reference']['checked'] = {'release': '2.1.900', 'date': '2026-09-30'}
    a['alpha.overview']['audited'] = {'release': '2.1.901', 'date': '2026-09-10'}
    a['alpha.reference']['audited'] = {'release': '2.1.900', 'date': '2026-09-20'}
    before = copy.deepcopy(s)
    new = baseline.add(s, EXTRA, with_extra(guide_text()), ['alpha.extra'], '2.1.902', {})
    assert new['sections']['alpha.extra'] == {
        'checked': {'release': '2.1.900', 'date': '2026-09-30'}, 'changed': '2.1.902',
        'audited': {'release': '2.1.901', 'date': '2026-09-10'},
        'text_hash': section_hash(with_extra(guide_text()), 'alpha.extra')}
    assert list(new['sections']) == ['alpha.overview', 'alpha.reference', 'alpha.extra', 'beta.overview', 'beta.reference']
    assert {i: v for i, v in new['sections'].items() if i != 'alpha.extra'} == before['sections']
    assert {k: new[k] for k in ('format', 'groups', 'llms', 'cited')} == {k: before[k] for k in ('format', 'groups', 'llms', 'cited')}
    assert s == before
    assert guide.render_stamp(new['sections']) == guide.render_stamp(before['sections'])


def test_add_in_a_new_group_copies_the_files_oldest_and_stays_above_a_citer(docs_dir):
    '''Designer's calls 3 and 4: a group with no stored section copies the
    file's oldest; a citation written by hand before add is left STALE.'''
    s = fixture_state(docs_dir)
    s['sections']['alpha.overview']['checked'] = {'release': '2.1.902', 'date': '2026-10-01'}
    s['sections']['alpha.overview']['audited'] = {'release': '2.1.902', 'date': '2026-10-01'}
    new = baseline.add(s, state.parse_manifest(GAMMA_MANIFEST), GAMMA_GUIDE, ['gamma.overview'], '2.1.902',
                       {'gamma.overview': ['2.1.902']})
    assert new['sections']['gamma.overview'] == {
        'checked': {'release': '2.1.900', 'date': '2026-09-02'}, 'changed': '2.1.902.1',
        'audited': {'release': '2.1.900', 'date': '2026-09-02'},
        'text_hash': section_hash(GAMMA_GUIDE, 'gamma.overview')}
    assert list(new['sections'])[-1] == 'gamma.overview'


def test_add_keeps_an_entry_waiting_for_drop(docs_dir):
    '''Review Focus 1: a stored ID that the guide and the manifest lack keeps
    its values, after the guide-ordered entries.'''
    s = fixture_state(docs_dir)
    pending = copy.deepcopy(s['sections']['beta.reference'])
    items = list(s['sections'].items())
    s['sections'] = dict([items[0], ('gone.one', pending), *items[1:]])
    new = baseline.add(s, EXTRA, with_extra(guide_text()), ['alpha.extra'], '2.1.902', {})
    assert list(new['sections']) == ['alpha.overview', 'alpha.reference', 'alpha.extra', 'beta.overview',
                                     'beta.reference', 'gone.one']
    assert new['sections']['gone.one'] == pending


@pytest.mark.parametrize('ids, manifest_text, message', [
    (['alpha.nowhere'], EXTRA_MANIFEST, 'baseline add: not a guide anchor: alpha.nowhere'),
    (['alpha.extra'], MANIFEST_TOML, 'baseline add: in no manifest.toml group: alpha.extra'),
    (['alpha.extra', 'alpha.overview'], EXTRA_MANIFEST, 'baseline add: already in baseline.json: alpha.overview'),
])
def test_add_refuses_and_changes_nothing(docs_dir, ids, manifest_text, message):
    s = fixture_state(docs_dir)
    before = copy.deepcopy(s)
    with pytest.raises(state.SetupError) as err:
        baseline.add(s, state.parse_manifest(manifest_text), with_extra(guide_text()), ids, '2.1.902', {})
    assert str(err.value) == message
    assert s == before
```

- [ ] **Step 2: Write the failing CLI tests**

In `test_cli.py`:

```python
def test_add_writes_only_the_new_entry_and_lint_passes_with_no_stamp(world, capsys):
    '''Drift R12.2 write set, and Review Focus 2.'''
    repo, cache, _ = world
    guide = repo / GUIDE_PATH
    guide.write_text(with_extra(guide.read_text()))
    (repo / state.MANIFEST).write_text(EXTRA_MANIFEST)
    git(repo, 'commit', '-qam', 'a section created after init')
    before = load(repo)
    assert main(cache, 'baseline', 'add', 'alpha.extra') == 0
    assert capsys.readouterr() == (f'updated {state.BASELINE}\n', '')
    assert dirty(repo) == [state.BASELINE]
    after = load(repo)
    assert set(after['sections']) - set(before['sections']) == {'alpha.extra'}
    assert changed_fields(before, after) == set()
    assert after['cited'] == before['cited']
    assert main(cache, 'lint') == 0


def test_add_refuses_without_a_cached_changelog_or_with_a_broken_citation(world, tmp_path, capsys):
    repo, cache, _ = world
    guide = repo / GUIDE_PATH
    guide.write_text(with_extra(guide.read_text()))
    (repo / state.MANIFEST).write_text(EXTRA_MANIFEST)
    cited(repo, {'hooks/gate.sh': '#!/bin/sh\nexit 0\n# cc-guide: alpha.overview @2.1.902\n'})
    before = (repo / state.BASELINE).read_bytes()
    assert main(tmp_path / 'empty-cache', 'baseline', 'add', 'alpha.extra') == 2
    assert capsys.readouterr() == ('', 'cc-guide: no cached changelog: run check, or restore the 2.1.288 snapshot\n')
    assert main(cache, 'baseline', 'add', 'alpha.extra') == 2
    assert capsys.readouterr() == ('', (
        'cc-guide: baseline add needs every citation to parse (R2.4); fix these first:\n'
        'hooks/gate.sh:3: a citation goes on a line before the first line of code (R4.1)\n'))
    assert (repo / state.BASELINE).read_bytes() == before


def test_a_section_created_after_init_reaches_check_exit_zero(world, capsys):
    '''Review Focus 3: S1's flow. The new section's `PIPE_ENV` selects one more
    env-vars block, which check reports as new until rebaseline settles it.'''
    repo, cache, folder = world
    guide = repo / GUIDE_PATH
    guide.write_text(with_extra(guide.read_text()))
    (repo / state.MANIFEST).write_text(EXTRA_MANIFEST)
    check_args = ('check', '--worktree', '--docs', str(folder))
    assert main(cache, 'baseline', 'add', 'alpha.extra') == 0
    capsys.readouterr()
    assert main(cache, *check_args) == 1
    assert ('  [alpha] new env-vars › Environment variables › `PIPE_ENV` (candidates: alpha.extra)'
            in capsys.readouterr().out.splitlines())
    assert main(cache, 'baseline', 'rebaseline', 'alpha') == 0
    assert main(cache, *check_args) == 0
    assert main(cache, 'lint') == 0
```

In `test_help_shows_the_module_docstring_and_the_rebaseline_refusal`, add `assert '  baseline add ID [ID ...]\n' in outs[0]`.

The flow test's premise was checked on 2026-11-15 against today's code with an equivalent edit to `alpha.reference`: `check` printed that block line, exited 1, and exited 0 after `rebaseline alpha`.

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run python build/run_suites.py cc_guide -- test_baseline.py test_cli.py -k "add or created_after_init or help"`
Expected: the unit tests fail with `AttributeError: module 'baseline' has no attribute 'add'`. The CLI tests fail at argparse with exit 2, `invalid choice: 'add'`. The help test fails on the missing usage line.

- [ ] **Step 4: Implement**

- `guide.py`: `checked_order` and `audited_order` as Interfaces states; `render_stamp` uses them, and its output is unchanged.
- `baseline.py`: `add` as Interfaces and the rules above state. Its docstring cites R7 `add` and D1 and D4.
- `cli.py`:
  - Parser: `b.add_parser('add').add_argument('ids', nargs='+')`.
  - Move the substantive `accept` preamble into `review_stamps`.
  - Add an `elif args.action == 'add':` branch before the final `else:`, which is `rebaseline`'s. It reads `newest_releases(cache)[0].label` first, then `review_stamps(tree, manifest.guide, 'baseline add')`, then calls `baseline.add`. It falls through to the shared tail: the write, the stale-stamp check and `updated …`.
  - Docstring: add the usage line `  baseline add ID [ID ...]` after the `accept` line. Add to the paragraph after the usage lines: add creates the entry of each section created after init, once the guide anchors it and manifest.toml lists it in a group. `changed` follows R2.4. `checked` and `audited` copy the oldest among the group's sections, so add claims no check or audit and never moves the stamp. It touches no blocks: check reports what the section's terms select, and rebaseline settles it. init --force is not the way to add a section: it resets every section's checked, changed and audited and empties cited.

- [ ] **Step 5: Run the suite to verify it passes**

Run: `uv run python build/run_suites.py cc_guide`
Expected: PASS, +9 tests (6 unit items, 3 CLI).

- [ ] **Step 6: Commit**

```bash
git add build/cc_guide/guide.py build/cc_guide/baseline.py build/cc_guide/cli.py build/cc_guide/test_baseline.py build/cc_guide/test_cli.py
git commit -m "feat(cc_guide): add baseline add for a section created after init"
```

### Task 4: `baseline drop` (S2)

**Files:**
- Modify: `build/cc_guide/baseline.py` (new `drop`, after `add`)
- Modify: `build/cc_guide/cli.py` (docstring, parser, an `elif` branch)
- Modify: `build/cc_guide/cc_fixtures.py` (two fixtures, after Task 1's)
- Test: `build/cc_guide/test_baseline.py`, `build/cc_guide/test_cli.py`

**Interfaces:**
- Consumes: `baseline.known` (existing).
- Produces:
  - `baseline.drop(state: dict, manifest: Manifest, guide_text: str, ids) -> dict`. It removes each ID's `sections` entry, and the ID from every map in `cited`. A file whose map empties leaves `cited` (designer's call 6). `groups`, `llms` and `format` stay. The input is never mutated. It validates each named ID on its own, without `check_ids`.
  - Fixtures: `without_beta_reference(text: str) -> str`, which replaces `'\n### Reference ⚠\n<!-- cc: beta.reference -->\n\n`BetaEvent` fires.\n'` with `'\n'`; `DROPPED_MANIFEST: str`, `MANIFEST_TOML` with group beta's `sections` as `['beta.overview']`. `beta.overview`'s `text_hash` stays unchanged.

- [ ] **Step 1: Write the failing tests**

In `test_baseline.py` (import the two fixtures):

```python
DROPPED = state.parse_manifest(DROPPED_MANIFEST)


def test_drop_removes_the_entry_and_the_id_from_cited_only(docs_dir):
    s = fixture_state(docs_dir)
    h = {sid: v['text_hash'] for sid, v in s['sections'].items()}
    s['cited'] = {'hooks/a.sh': {'beta.reference': h['beta.reference']},
                  'hooks/b.sh': {'beta.overview': h['beta.overview'], 'beta.reference': h['beta.reference']}}
    before = copy.deepcopy(s)
    new = baseline.drop(s, DROPPED, without_beta_reference(guide_text()), ['beta.reference'])
    assert new['sections'] == {i: v for i, v in before['sections'].items() if i != 'beta.reference'}
    assert new['cited'] == {'hooks/b.sh': {'beta.overview': h['beta.overview']}}
    assert {k: new[k] for k in ('format', 'groups', 'llms')} == {k: before[k] for k in ('format', 'groups', 'llms')}
    assert s == before


@pytest.mark.parametrize('guide_of, manifest, ids, message', [
    (guide_text, DROPPED, ['beta.reference'], 'baseline drop: still a guide anchor: beta.reference'),
    (lambda: without_beta_reference(guide_text()), MANIFEST, ['beta.reference'],
     'baseline drop: still in a manifest.toml group: beta.reference'),
    (guide_text, MANIFEST, ['gone.one'], 'unknown section IDs: gone.one'),
])
def test_drop_refuses_and_changes_nothing(docs_dir, guide_of, manifest, ids, message):
    s = fixture_state(docs_dir)
    before = copy.deepcopy(s)
    with pytest.raises(state.SetupError) as err:
        baseline.drop(s, manifest, guide_of(), ids)
    assert str(err.value) == message
    assert s == before


def test_drop_refuses_to_leave_no_section(docs_dir):
    s = fixture_state(docs_dir)
    s['sections'] = {'gone.one': s['sections']['beta.reference']}
    with pytest.raises(state.SetupError) as err:
        baseline.drop(s, MANIFEST, guide_text(), ['gone.one'])
    assert str(err.value) == 'baseline drop: would leave baseline.json with no section'
```

In `test_cli.py` (import the two fixtures):

```python
def test_drop_writes_only_the_baseline_and_a_moved_oldest_needs_stamp(world, capsys):
    '''Drift R12.2 write set, and Review Focus 4: beta.reference alone holds
    the oldest checked, so dropping it moves the stamp.'''
    repo, cache, _ = world
    assert main(cache, 'baseline', 'advance', 'alpha.overview', 'alpha.reference', 'beta.overview',
                '--to', '2.1.902') == 0
    guide = repo / GUIDE_PATH
    guide.write_text(without_beta_reference(guide.read_text()))
    (repo / state.MANIFEST).write_text(DROPPED_MANIFEST)
    git(repo, 'commit', '-qam', 'remove beta.reference')
    before = load(repo)
    capsys.readouterr()
    assert main(cache, 'baseline', 'drop', 'beta.reference') == 0
    assert capsys.readouterr() == (f'updated {state.BASELINE}\n',
                                   'the stamp region is now stale: run baseline stamp\n')
    assert dirty(repo) == [state.BASELINE]
    after = load(repo)
    assert after['sections'] == {i: v for i, v in before['sections'].items() if i != 'beta.reference'}
    assert {k: after[k] for k in ('groups', 'llms', 'cited')} == {k: before[k] for k in ('groups', 'llms', 'cited')}
    assert main(cache, 'lint') == 1
    assert main(cache, 'baseline', 'stamp') == 0
    assert main(cache, 'lint') == 0


def test_drop_refuses_a_section_the_guide_still_has(world, capsys):
    repo, cache, _ = world
    assert main(cache, 'baseline', 'drop', 'beta.reference') == 2
    assert capsys.readouterr() == ('', 'cc-guide: baseline drop: still a guide anchor: beta.reference\n')
    assert dirty(repo) == []
```

In `test_help_shows_the_module_docstring_and_the_rebaseline_refusal`, add `assert '  baseline drop ID [ID ...]\n' in outs[0]` and `assert 'advance, audited and drop can move the oldest' in ' '.join(outs[0].split())`.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run python build/run_suites.py cc_guide -- test_baseline.py test_cli.py -k "drop or help"`
Expected: the unit tests fail with `AttributeError: module 'baseline' has no attribute 'drop'`. The CLI tests fail at argparse with exit 2. The help test fails on the missing line.

- [ ] **Step 3: Implement**

- `baseline.py`: `drop` as Interfaces states, with the pinned refusals in order. Its docstring cites R7 `drop` and designer's calls 6 and 9: `drop` leaves the `groups` entry of a group that has left the manifest.
- `cli.py`:
  - Parser: `b.add_parser('drop').add_argument('ids', nargs='+')`.
  - Add an `elif args.action == 'drop':` branch before the final `else:` that calls `baseline.drop(state, manifest, guide_text, args.ids)` and falls through to the shared tail.
  - Docstring: add the usage line `  baseline drop ID [ID ...]` after the `add` line. Add to the paragraph after the usage lines: drop removes each named entry, and the ID from cited, once the guide and manifest.toml no longer have it. It edits no citing file, and stamp follows it. In the closing paragraph, "advance and audited can move the oldest `checked`, which the stamp names, so stamp follows them" becomes "advance, audited and drop can move the oldest `checked` or `audited`, which the stamp names, so stamp follows them". Extend Task 3's init --force sentence to read "the way to add or drop a section".

- [ ] **Step 4: Run the suite to verify it passes**

Run: `uv run python build/run_suites.py cc_guide`
Expected: PASS, +7 tests (5 unit items, 2 CLI).

- [ ] **Step 5: Commit**

```bash
git add build/cc_guide/baseline.py build/cc_guide/cli.py build/cc_guide/cc_fixtures.py build/cc_guide/test_baseline.py build/cc_guide/test_cli.py
git commit -m "feat(cc_guide): add baseline drop for a section removed from the guide"
```

### Task 5: `lint` names the command (S3)

**Files:**
- Modify: `build/cc_guide/lint.py:31-43` (`id_set_problems`)
- Test: `build/cc_guide/test_lint.py:36-42`, `build/cc_guide/test_cli.py`

**Interfaces:**
- Consumes: `baseline add` (Task 3), `baseline drop` (Task 4), `with_extra`, `EXTRA_MANIFEST`, `without_beta_reference`, `DROPPED_MANIFEST`.
- Produces: the two pinned lint messages. Every other combination keeps today's text.

- [ ] **Step 1: Write the failing tests**

In `test_lint.py`, `test_the_three_id_sets_must_agree` is expected to change: its second line becomes `f'section beta.reference: missing from baseline.json; add it with `{CLI} baseline add beta.reference`'`. Its first line, `'section beta.extra: missing from the guide and baseline.json'`, stays. Add:

```python
def test_an_id_only_in_baseline_json_names_the_drop_command(docs_dir):
    s = fixture_state(docs_dir)
    s['sections']['gone.one'] = s['sections']['beta.reference']
    violations, _ = run(guide_text(), s)
    assert violations == [f'section gone.one: missing from the guide and manifest.toml; drop it with '
                          f'`{CLI} baseline drop gone.one`']
```

`test_a_section_missing_from_the_manifest_alone_is_named` and `test_an_anchor_problem_fails_the_lint` already pin two of the unchanged combinations. They must pass unedited.

In `test_cli.py`:

```python
@pytest.mark.parametrize('edit, manifest_text, line', [
    (with_extra, EXTRA_MANIFEST, 'section alpha.extra: missing from baseline.json; add it with '
                                 '`uv run python build/cc_guide/cli.py baseline add alpha.extra`'),
    (without_beta_reference, DROPPED_MANIFEST, 'section beta.reference: missing from the guide and manifest.toml;'
                                               ' drop it with `uv run python build/cc_guide/cli.py baseline drop'
                                               ' beta.reference`'),
], ids=['add', 'drop'])
def test_running_the_command_lint_prints_clears_the_id_set_violation(world, capsys, edit, manifest_text, line):
    '''Review Focus 5.'''
    repo, cache, _ = world
    guide = repo / GUIDE_PATH
    guide.write_text(edit(guide.read_text()))
    (repo / state.MANIFEST).write_text(manifest_text)
    assert main(cache, 'lint') == 1
    assert capsys.readouterr().out == line + '\n'
    prefix = 'uv run python build/cc_guide/cli.py '
    command = line.split('`')[1]
    assert command.startswith(prefix)
    assert main(cache, *command[len(prefix):].split()) == 0
    assert main(cache, 'lint') == 0
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run python build/run_suites.py cc_guide -- test_lint.py test_cli.py::test_running_the_command_lint_prints_clears_the_id_set_violation`
Expected: `test_the_three_id_sets_must_agree`, the new lint test and both CLI cases fail, since each message lacks its command.

- [ ] **Step 3: Implement**

In `id_set_problems`, append `` f'; add it with `{CLI} baseline add {sid}`' `` when the only missing place is `baseline.json`. Append `` f'; drop it with `{CLI} baseline drop {sid}`' `` when the missing places are exactly the guide and `manifest.toml`. Its docstring says the message names the one command that clears those two combinations, and that every other combination needs a guide or manifest edit first.

- [ ] **Step 4: Run the suite to verify it passes**

Run: `uv run python build/run_suites.py cc_guide`
Expected: PASS, +3 tests.

- [ ] **Step 5: Commit**

```bash
git add build/cc_guide/lint.py build/cc_guide/test_lint.py build/cc_guide/test_cli.py
git commit -m "feat(cc_guide): name baseline add and drop in the lint's ID-set messages"
```

### Task 6: Spec amendments, `build/CLAUDE.md`, and the full gate

**Files:**
- Modify: `specs/completed/claude-code-drift-automation-spec.md` (status note and R1.1, R2.6, R5, R7, R11.1, R12.2, R12.3)
- Modify: `specs/completed/claude-code-guide-conformance.md` (status note and R1.2)
- Modify: `build/CLAUDE.md` (the `cc_guide/` paragraph)

**Interfaces:**
- Consumes: Tasks 1 to 5, built. This task changes no code.

Each block below gives exact text. Every "old" text occurs once in its file (checked at `a4946ae`). Line breaks inside a block are the file's own. `<date>` is the day this task runs, as `YYYY-MM-DD`. The notes name the spec and plan by their retired paths, since the Plan Completion Protocol retires both on this branch before it merges.

- [ ] **Step 1: Amend the drift spec**

Status note: after the paragraph that ends `Retired here by plan 58, the Stage 5 plan.`, insert a blank line and:

````text
**Amended <date>** by `specs/completed/cc-guide-sections-after-init.md` (plan 99,
`specs/plans/completed/99-cc-guide-sections-after-init.md`): a section created after `baseline init` enters
`baseline.json` through `baseline add`, a removed section leaves through `baseline drop`, and the history tests
read the guide at `18b4a71` (R1.1, R2.6, R5, R7, R11.1, R12.2, R12.3).
````

R1.1. Old:

````text
- Each section belongs to exactly one group (R2.5).
````

New:

````text
- Each section belongs to exactly one group (R2.5). The table records the 38
  sections at the bootstrap. `manifest.toml` lists the live sections. A
  section created later takes an anchor, an ID in one group, and
  `baseline add` (R7). A removed one leaves through `baseline drop`.
````

R2.6. Old: `` `checked = audited = 2.1.288 (2026-10-03)`, with `changed` per R11.1. `` New:

````text
`checked = audited = 2.1.288 (2026-10-03)`, with `changed` per R11.1. A
section created after `init` enters through `baseline add` (R7).
````

R5. Old:

````text
  groups, `baseline.json`'s sections and the anchors carry the same ID set,
  each ID in exactly one group.
````

New:

````text
  groups, `baseline.json`'s sections and the anchors carry the same ID set,
  each ID in exactly one group. When the guide and the manifest have an ID
  that `baseline.json` lacks, the message prints the `baseline add` command.
  When only `baseline.json` has it, the message prints the `baseline drop`
  command.
````

R7, first paragraph. Old:

````text
stamps. Every subcommand leaves its changes uncommitted. `advance` and
`audited` can move the oldest `checked` or `audited`, which the stamp region
````

New:

````text
stamps. Every subcommand leaves its changes uncommitted. `advance`,
`audited` and `drop` can move the oldest `checked` or `audited`, which the stamp region
````

R7, the `init` bullet. Old: `` - `init`: R2.6. `` New:

````text
- `init`: R2.6. `init --force` is not the way to add or drop a section. It
  resets every section's `checked`, `changed` and `audited` to the bootstrap
  and empties `cited`.
- `add <ids>`: create each named section's entry, for a section created after
  `init`. The ID must be an anchor in the guide and in one `manifest.toml`
  group, and not yet in `baseline.json`. `text_hash` is the section's text,
  and `changed` follows R2.4. `checked` and `audited` copy the oldest of each
  among the group's sections, in the stamp region's order, or the oldest in
  the file when the group has none. So `add` claims no check or audit, and
  never moves the stamp region. `advance` records a later check (owner,
  2026-11-15). It touches no blocks: `check` reports what the section's terms
  select as `new`, and `rebaseline` settles it.
- `drop <ids>`: remove each named section's entry, and the ID from every file
  in `cited`, once the guide and `manifest.toml` no longer have it. It touches
  no blocks and no citing file.
````

R11.1. Old:

````text
heading), never heading text alone, so the two "Frontmatter reference ⚠"
sections stay distinct.
````

New:

````text
heading), never heading text alone, so the two "Frontmatter reference ⚠"
sections stay distinct. The guide at `18b4a71` (plan 35, the first with
anchors, headings identical to `c33bc99`'s) maps each aligned section to its
ID. So a later heading edit changes nothing. `init` gives a section without a
derived value its `--release`.
````

R12.2. Old:

````text
- R2 and R7: version ordering with four components, and each `baseline`
  subcommand's write set.
````

New:

````text
- R2 and R7: version ordering with four components, each `baseline`
  subcommand's write set, and `add` and `drop`.
````

R12.3. Old:

````text
- **Replay.** Rebuild the guide at `91474f6` and `c33bc99` from git (our text,
  at its pre-move path), derive `changed` as R11.1 does, and run against fixture citers stamped
````

New:

````text
- **Replay.** Rebuild the guide at `91474f6` and `c33bc99` from git (our text,
  at its pre-move path), map their sections to IDs through the guide at
  `18b4a71`, derive `changed` as R11.1 does, and run against fixture citers stamped
````

And old:

````text
  not. Skip with a reason when the history is unavailable (a shallow clone).
````

New:

````text
  not. Skip with a reason when the history is unavailable (a shallow clone).
  No history test reads the working-tree guide.
````

- [ ] **Step 2: Amend the conformance spec**

Status note: after the status block's last bullet, which ends `` a note on `sh -c` quoting under R3.4. ``, insert a blank line and:

````text
**Amended <date>** by `specs/completed/cc-guide-sections-after-init.md` (plan 99,
`specs/plans/completed/99-cc-guide-sections-after-init.md`): the R1.2 test reads the guide at `18b4a71`, and the
working tree's anchors are the lint's to check (R1.2).
````

R1.2. Old: `R1.2 A test parses the real guide and pins three things:` New:

````text
R1.2 A test parses the guide at `18b4a71`, the commit that added the anchors,
and pins three things:
````

After the line `- the IDs, in heading order, equal the R1.1 table.`, insert a blank line and:

````text
The working tree's anchors are the lint's to check (R3.3), and drift R5's.
````

- [ ] **Step 3: Add the flow to `build/CLAUDE.md`**

Old:

````text
A missing page needs a
`manifest.toml` edit first.
````

New:

````text
A missing page needs a
`manifest.toml` edit first. A section created after `baseline init` enters
`baseline.json` through `baseline add <id>`, once the guide anchors it and
`manifest.toml` lists it in a group. A removed section leaves through
`baseline drop <id>`, then `baseline stamp`. `baseline init --force` is not for
either: it resets every section's state.
````

- [ ] **Step 4: Run the artifact lints**

Run: `uv run --with pyyaml python build/check_conformance.py`
Expected: exit 0. `build/CLAUDE.md` is a Claude Code artifact.

Run: `uv run python build/cc_guide/cli.py lint`
Expected: exit 0. STALE lines on stderr do not change the exit.

- [ ] **Step 5: Run both suites and the commit lints**

Run: `uv run python build/run_suites.py cc_guide`
Expected: PASS, no new tests.

Run: `uv run python build/run_suites.py build`
Expected: PASS. The skips that the suite's notes name are expected.

Run: `bash build/run_commit_lints.sh`
Expected: exit 0.

- [ ] **Step 6: Commit**

```bash
git add specs/completed/claude-code-drift-automation-spec.md specs/completed/claude-code-guide-conformance.md build/CLAUDE.md
git commit -m "docs(specs): amend the drift and conformance specs for baseline add and drop"
```

## Completion notes

These feed the Plan Completion Protocol after the final review. They do not replace it.

- **Tick:** the backlog item "Sections created after `baseline init` (plan 38, T7-m3)" in `specs/deferred_items.md`, § 38-claude-code-drift-automation — 2026-10-05, takes `→ done <date>: plan 99`. This is the spec's last Done-when condition.
- **Defer:** the spec's § Not in this spec names one item for the completion to log: removing the `groups` entry of a group that has left `manifest.toml` (S2, designer's call 9). The entry costs only space.
- **Retire:** no other live plan implements the spec, so it retires to `specs/completed/` with the plan. The status notes of Task 6 already name both retired paths.

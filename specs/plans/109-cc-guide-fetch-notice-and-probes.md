# cc_guide fetch, notice and probes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close lane 2 of the 2026-11-26 `/deferred` pass: `check` swaps `latest/` in whole, the drift notice's test gaps get tests, the `agent-payload` probe tells a disobedient parent from drift, and two Stage 5 probes are registered and run.

**Architecture:** Part A (Tasks 1–5) changes the fetch cache to symlinked generation folders, pins the two readers that combine `fetch.json` with pages, amends the drift spec, and adds the notice tests. Part B (Tasks 6–9) reworks the `agent-payload` probe and its fixtures, fixes plan 69's Minors, and adds the `explore-override` and `async-teardown` probes, each run live and recorded in `PROBES.md` in the task that registers it. The two parts share no file except `specs/deferred_items.md` at plan time, so Part B may run before Part A.

**Tech Stack:** Python (dev version in `build/versions.toml`), stdlib only in `build/cc_guide/`; POSIX `sh`; pytest through `uv run`.

**Spec:** `specs/completed/claude-code-drift-automation-spec.md` (Layout, R6.3, R6.4, R9, R10, R12.6) and the five backlog items named in each task, in `specs/deferred_items.md`.

## Global Constraints

- Run every test from `build/cc_guide/` (directory-scoped suite): `cd build/cc_guide && uv run --with pytest python -m pytest -q <file>[::<test>]`. Before each commit, run `uv run python build/run_suites.py cc_guide` and `bash build/run_commit_lints.sh` from the repo root.
- Python style: single quotes, f-strings, named constants for numbers (G25), stdlib only in `build/cc_guide/`.
- Files: only those each task lists. Lane 1 owns `skills/classification-codes/**`, `skills/geographic-codes/**`, `skills/bls-data-context/**` and the Census lines in `NOTICE` and `README.md`. Lane 3 owns `build/run_suites.py`, `build/check_conformance.py`, `build/versions_check.py` and their tests, `.github/workflows/versions-drift.yml` and the three kit folders of the item "Three kit suites fail…". Touch none of them.
- No task runs `cli.py baseline cite`, and no task edits a `# cc-guide:` citation line, so `build/cc_guide/baseline.json` does not change (the adjacent-`cited`-record conflict, section `89-cc-guide-owner-rulings — 2026-11-11`).
- A probe fixture is written only by `probes.save_fixtures` (build/CLAUDE.md). A fixture must pass `test_probe_replay.py`'s `PRIVATE_RE` scan.
- Live probe runs: `uv run python build/cc_guide/cli.py probes --claude <path> --only <id> --allow-old` from the repo root, with `<path>` the newest binary that `cli.py binaries` lists. Each `claude -p` invocation is capped by `--max-budget-usd 0.50` (`probes.BUDGET_USD`). Total plan spend: at most 5 invocations, ceiling $2.50, expected $0.25–1.50 (D7). A run that is not PASS stops the task: report the row and the raw folder to the owner, and commit nothing for that probe until the owner rules.
- Commit a probe's `PROBES.md` row in the same commit that registers it in `manifest.toml`. A registered probe with no row makes `cli.py check` exit 1 ("never run") and fires the SessionStart notice everywhere.
- Leave alone: the plan 58 Minors batch except `_trim_block` keeping `model` (D5); the `notice.sh`/`notice.py` robustness Minors (section `49-claude-code-drift-automation`); the worktree-isolation probe item (section `cc-guide-2.1.326-worktree-isolation`).

## Review Focus

1. **A reader that resolved `latest` just before a swap.** It must still find its files: the swap keeps the generation it replaced. Pinned in Task 1 (`test_the_swap_keeps_the_generation_it_replaced`).
2. **A cache from before this plan, where `latest/` is a real folder.** The first check after the change must migrate it with no lost page and no error. Pinned in Task 1 (`test_a_legacy_latest_folder_is_migrated_to_a_generation`).
3. **Two checks at once** (a notice `refresh` and a manual `check`). Neither may delete the other's staging folder. Pinned in Task 1 (`test_pruning_spares_a_young_staging_folder`).
4. **A parent that disobeys the dispatch prompt in a live run.** The owner must see ERROR naming the parent, not DIVERGES naming Claude Code. Pinned in Task 6 (replay cases).
5. **A probe rep where the subagent reads a file instead of answering from its context.** That rep must be void, never a PASS. Pinned in Task 8 (`test_explore_override_voids_a_rep_whose_subagent_called_a_tool`).

## Decisions

- **D1** (owner, brief, 2026-11-26): this plan covers exactly the five lane-2 items, in two parts: Part A the `latest/` swap then the notice test gaps; Part B the agent-payload fix with its Minors, then the two Stage 5 probes. Tasks avoid lane 1's and lane 3's files. Applied in: Global Constraints, Tasks 1–9.
- **D2** (owner, brief, 2026-11-26): plan the `latest/` swap without brainstorming. The 2026-11-17 owner ruling approves the staged swap, its test, and the change to R6.3 and R6.4. Applied in: Tasks 1–3.
- **D3** (owner, plan review, 2026-11-26): the swap is a symlink flip. `latest` becomes a symlink to a generation folder `latest.<suffix>/` that holds `docs/` and `fetch.json`. One `os.replace` of the link swaps it at once, and concurrent checks each write their own generation. Rename-aside was rejected: it leaves a moment with no `latest/`, and two concurrent runs can interleave its two renames. Cost: `os.symlink` needs privileges on Windows, but `build/cc_guide/` is already POSIX-only (`fcntl` in `probes.py`, `notice.sh`). Applied in: Tasks 1–3.
- **D4** (owner, plan review, 2026-11-26): seed the staged generation by copying the current one only when the changelog head is unchanged. On a head move, start it empty, since every mapped page is refetched. A page that fails to fetch is left out of the new generation and the swap goes ahead, as today's code deletes it. The brief recommended aborting the swap on any page error. That option freezes `latest/` at the old head while one page keeps failing, and it changes three passing tests. The item's hazard, newer pages under an older `fetch.json`, cannot happen either way. Applied in: Tasks 1, 3.
- **D5** (owner, plan review, 2026-11-26; default from the brief): from the plan 58 Minors batch, only `_trim_block` keeping `model` in `tool_use` inputs is in scope. `probes.py` has 785 lines, and part (l) of that batch is triggered. This plan adds two probes to `probes.py` without splitting it. Applied in: Task 6.
- **D6** (owner, plan review, 2026-11-26; default from the brief): replace `test_a_new_head_is_recorded_only_after_every_page_is_written`, which asserts the partial state the swap removes. Do not add the new test beside it. Applied in: Task 1.
- **D7** (owner, plan review, 2026-11-26; owner gate approved): run each new probe live in the task that registers it, and run `agent-payload` live once after its rework, all with `--allow-old`. The newest installed binary is 2.1.330, and the guide was verified at 2.1.332. `explore-override` runs 3 reps as 3 invocations inside one probe run, so it gets one row. Spend is in Global Constraints. Applied in: Tasks 6, 8, 9.
- **D8** (owner, plan review, 2026-11-26; default from the brief): amend the spec with an amendment task. It gives exact replacements for the Layout bullet, R6.3 and R6.4, each tagged `(owner, plan 109, 2026-11-17)`, and adds an "Amended" line under the status, as plan 99 did. The status line stays as it is. No amendment registers the two new probes: plans 69 and 87 registered `agent-payload` and `compaction-cut` with no spec change. Applied in: Task 3.
- **D9** (owner, plan review, 2026-11-26): all seven Minors of the plan 69 item are in scope. Their own "Revisit if" says to fix them in the same change once the agent-payload item lands. Applied in: Task 7.
- **D10** (owner, plan review, 2026-11-26): the new probes back these sections. `explore-override` backs `subagents.isolation` (guide line 231) and `subagents.models` (line 226), with file `agents/explore.md`. `async-teardown` backs `hooks.pitfalls` (line 420), with file `build/cc_guide/notice.sh`. Applied in: Tasks 8, 9.
- **D11** (owner, plan review, 2026-11-26): two files outside the lane's usual set change. `build/cc_guide/cli.py` (the `rebaseline --head` reader) and `build/cc_guide/packets.py` (`load`) must read `fetch.json` and the pages from one resolved generation. Without this, a flip between the two reads still breaks the `--head` pin. Applied in: Task 2.

---

## Part A — fetch cache and drift notice

### Task 1: `live_docs` builds a generation and swaps `latest` to it

Item: section `51-claude-code-drift-automation`, "Write `latest/` as a whole, not page by page".

**Files:**
- Modify: `build/cc_guide/state.py:473-500` (`latest_docs`, `fetch_record`, `read_fetch`)
- Modify: `build/cc_guide/check.py:102-155` (`live_docs`)
- Modify: `build/cc_guide/cc_fixtures.py:580-585` (`prime_cache`)
- Test: `build/cc_guide/test_check.py` (replace `:319-340`; update `:530-548`)

**Interfaces:**
- Produces, in `state.py`:
  - `LATEST = 'latest'` and `GENERATION_PREFIX = 'latest.'`.
  - `latest_dir(cache: Path) -> Path`: `cache / LATEST` resolved once, the current generation folder. A legacy real folder resolves to itself.
  - `fetch_record_in(root: Path) -> Path` is `root / 'fetch.json'`. `read_fetch_at(root: Path) -> dict | None` is today's `read_fetch` body on that path.
  - `latest_docs(cache)`, `fetch_record(cache)` and `read_fetch(cache)` keep their signatures and read through the link.
- Produces, in `check.py`:
  - `swap_latest(cache: Path, generation: Path) -> None`
  - `prune_generations(cache: Path, keep: set[Path], now_epoch: float) -> None`
  - `STAGING_GRACE = 3600` (seconds)

- [ ] **Step 1: Write the failing tests** in `test_check.py`. Delete `test_a_new_head_is_recorded_only_after_every_page_is_written` (D6). Add these, using the file's `serving` and `NOW`:

```python
def test_a_check_that_fails_partway_leaves_latest_as_it_was(tmp_path, docs_dir, monkeypatch):
    # first live_docs at 2.1.902; then head 2.1.903 with tools.md edited, and a fetch that
    # raises OSError('disk full') for env-vars (not a FetchError, so it escapes live_docs)
    # with pytest.raises(OSError): live_docs(...)
    assert state.latest_dir(cache) == before                    # the link did not move
    assert snapshot_of(before) == files_before                  # same names, same bytes
    assert state.read_fetch(cache)['changelog_head'] == '2.1.902'
    assert [p.name for p in cache.iterdir() if p.name.startswith(state.GENERATION_PREFIX)] == [before.name]
    # a later good run refetches every page and records 2.1.903
```

```python
def test_latest_is_a_symlink_to_a_generation_holding_docs_and_its_record(tmp_path, docs_dir):
    check.live_docs(MANIFEST, cache, serving(docs_dir), NOW)
    link = cache / state.LATEST
    assert link.is_symlink() and not os.readlink(link).startswith('/')   # relative target
    assert state.fetch_record(cache).parent == state.latest_docs(cache).parent == state.latest_dir(cache)
```

```python
def test_an_unchanged_head_seeds_the_generation_from_the_current_one(tmp_path, docs_dir):
    # run twice at one head with a fetch log: the second run fetches changelog and llms only,
    # its generation is a new folder, and every page reads the same as before
```

```python
def test_the_swap_keeps_the_generation_it_replaced(tmp_path, docs_dir):
    # three runs: after the third, the first generation is gone once older than STAGING_GRACE
    # (pass now_epoch), and the second, the one the third replaced, is still there
```

```python
def test_pruning_spares_a_young_staging_folder(tmp_path, docs_dir):
    # a latest.* folder that is neither kept nor STAGING_GRACE old survives prune_generations
```

```python
def test_a_legacy_latest_folder_is_migrated_to_a_generation(tmp_path, docs_dir):
    prime_cache(cache, docs_dir)                 # a real latest/ folder, as caches before plan 109 hold
    check.live_docs(MANIFEST, cache, serving(docs_dir), NOW)
    assert (cache / state.LATEST).is_symlink()
    # the head was unchanged, so the pages were seeded: the fetch log holds changelog and llms only
```

- [ ] **Step 2: Run them to verify they fail**

Run: `cd build/cc_guide && uv run --with pytest python -m pytest -q test_check.py -k 'generation or latest or partway or legacy or pruning'`
Expected: FAIL (`state` has no `LATEST`, `latest_dir` or `GENERATION_PREFIX`).

- [ ] **Step 3: Implement**
  - Add the `state.py` names from Interfaces. Point `fetch_record(cache)` and `read_fetch(cache)` at `latest_dir(cache)`.
  - In `live_docs`:
    1. Read `previous` from `read_fetch(cache)`.
    2. Fetch and validate the changelog and `llms.txt` exactly as today. A FetchError still raises before anything is written.
    3. Make the staging folder with `tempfile.mkdtemp(prefix=GENERATION_PREFIX, dir=cache)`. When `head == previous` and a current generation exists, `shutil.copytree` its `docs/` into the staging folder. Otherwise create an empty `docs/`.
    4. Fetch the `todo` pages into the staging folder with today's per-page rules (404 and error remove the page, 200 writes it). Write `changelog.md`, `llms.txt` and `fetch.json`.
    5. Call `swap_latest`. Remove the staging folder in a `finally` if the swap did not happen.
    6. Read `Docs.pages` from the new generation.
  - Delete the head-move loop that removes unmapped pages: a head move starts from an empty folder.
  - `swap_latest`:
    1. If `cache / LATEST` is a real folder, not a link, `os.replace` it to a fresh `mkdtemp` name first. This is a one-time migration with a short gap.
    2. Create a symlink with a hidden temp name in `cache`, holding the generation's name (a relative target). `os.replace` it onto `cache / LATEST`.
    3. Call `prune_generations` with `keep = {new, replaced}`.
  - `prune_generations`: `shutil.rmtree` every `GENERATION_PREFIX` folder in `keep`'s complement whose mtime is at least `STAGING_GRACE` before `now_epoch`.
  - `prime_cache` writes a generation folder and links `latest` to it, so fixtures match a live check. Add a `legacy: bool = False` parameter that keeps the old real-folder layout for the migration test.

- [ ] **Step 4: Update `test_the_report_is_keyed_by_the_baseline_hash_and_check_writes_only_its_cache_files`.** `rglob` does not follow the link, so assert the written set with the generation name read from `os.readlink(cache / state.LATEST)` in place of `latest`, plus the `latest` link itself (`p.is_symlink()`).

- [ ] **Step 5: Run the whole suite**

Run: `uv run python build/run_suites.py cc_guide`
Expected: PASS. In particular, `test_a_failed_page_fetch_exits_two_without_comparing_that_page`, `test_a_404_removes_the_stale_copy_and_reads_as_a_missing_page` and `test_a_page_unmapped_by_a_head_move_is_refetched_when_mapped_again` pass unchanged (D4). Fix any other test that lists cache paths through `rglob` in the same way as Step 4, and name each one in the report.

- [ ] **Step 6: Commit**

```bash
git add build/cc_guide/state.py build/cc_guide/check.py build/cc_guide/cc_fixtures.py build/cc_guide/test_check.py
git commit -m "fix(cc-guide): build each fetch in its own generation and swap latest to it"
```

### Task 2: readers pin one generation

**Files:**
- Modify: `build/cc_guide/cli.py:390-406` (the `rebaseline` branch of `run_baseline`)
- Modify: `build/cc_guide/packets.py:57-69` (`load`)
- Test: `build/cc_guide/test_cli.py`

**Interfaces:**
- Consumes: `state.latest_dir`, `state.read_fetch_at`, `state.fetch_record_in` (Task 1).

- [ ] **Step 1: Write the failing test** `test_rebaseline_head_hashes_the_generation_whose_record_it_read` in `test_cli.py`:
  1. Prime a cache at head 2.1.902 (`prime_cache`).
  2. Monkeypatch `cli.read_fetch_at` with a wrapper that returns the real record, then runs `check.live_docs` at head 2.1.903 with an edited page. That flips the link between the two reads.
  3. Run `baseline rebaseline <group> --head 2.1.902`. Assert it exits 0, and that the stored hash is the 2.1.902 page's.

- [ ] **Step 2: Run it to verify it fails**

Run: `cd build/cc_guide && uv run --with pytest --with pyyaml python -m pytest -q test_cli.py::test_rebaseline_head_hashes_the_generation_whose_record_it_read`
Expected: FAIL (`cli` has no `read_fetch_at`).

- [ ] **Step 3: Implement.** In `run_baseline`'s rebaseline branch:
  1. Resolve `root = latest_dir(cache)` once.
  2. Read the record with `read_fetch_at(root)`.
  3. Pass `root / 'docs'` to `baseline.rebaseline`.

  Make the same change in `packets.load`: one `root` for `read_fetch_at`, `offline_docs` and `releases_of`'s path. `packets.py:249` (`snapshot_pages`) keeps `latest_docs`.

- [ ] **Step 4: Run the suite**

Run: `uv run python build/run_suites.py cc_guide`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add build/cc_guide/cli.py build/cc_guide/packets.py build/cc_guide/test_cli.py
git commit -m "fix(cc-guide): read a fetch's record and pages from one generation"
```

### Task 3: amend the drift spec (Layout, R6.3, R6.4)

**Files:**
- Modify: `specs/completed/claude-code-drift-automation-spec.md:5-9, 269, 646-662`

- [ ] **Step 1: Add after the `**Amended 2026-11-15**` paragraph (line 9), as its own paragraph:**

```markdown
**Amended 2026-11-26** by plan 109 (`specs/plans/109-cc-guide-fetch-notice-and-probes.md`): `check` writes each
fetch into its own generation folder and swaps the `latest` symlink to it at once (Layout, R6.3, R6.4).
```

- [ ] **Step 2: Replace line 269**

Replace: `  - `latest/docs/`: the last fetch;`
With:

```markdown
  - `latest`: a symlink to the last finished fetch's generation folder, `latest.<suffix>/`, which holds `docs/`
    and `fetch.json`; the swap keeps the generation it replaced (owner, plan 109, 2026-11-17);
```

- [ ] **Step 3: Replace R6.3's first sentence pair.** Replace the text from `Fetch \`changelog.md\` and \`llms.txt\` on every run.` through `on another ref's manifest, maps it again.` with:

```markdown
Fetch `changelog.md` and `llms.txt` on every run. When the changelog head matches the last fetch's, the new
generation (R6.4) starts as a copy of the current one and only the mapped pages it lacks are fetched; otherwise
it starts empty and every mapped page is fetched, so a page this manifest does not map stays behind with the old
generation. `fetch.json` records one head for a whole generation, and a page carried over from an older head
would vouch for old text when a later run, on another ref's manifest, maps it again (owner, plan 109, 2026-11-17).
```

- [ ] **Step 4: Replace R6.4's second and third sentences.** Replace from `Pages are written` through `names a finished fetch.` with:

```markdown
Each run writes its pages, `changelog.md`, `llms.txt` and `fetch.json` (the fetch time and changelog head) into a
new generation folder, `~/.cache/agent-skills/cc-guide/latest.<suffix>/`, then swaps the `latest` symlink to it
with one rename. So `latest/` always names one finished fetch, and a run that fails partway leaves it as it was. A
page whose fetch fails is left out of the new generation and is fetched again by the next run. The swap keeps the
generation it replaced, for a reader that resolved the link before it, and removes older generations and
abandoned staging folders once they are an hour old. A reader that needs the head and the pages together
resolves the link once and reads both from that generation (owner, plan 109, 2026-11-17).
```

  Leave the rest of R6.4 (`Every session and checkout shares this…`) and the status line as they are.

- [ ] **Step 5: Verify**

Run: `uv run python build/check_links.py && uv run python build/cc_guide/cli.py lint`
Expected: `0 broken`. `lint` prints no new `STALE` line for the spec.

- [ ] **Step 6: Commit**

```bash
git add specs/completed/claude-code-drift-automation-spec.md
git commit -m "docs(specs): amend drift spec R6.3 and R6.4 for the generation swap (plan 109)"
```

### Task 4: `check --hook` and `check` test gaps

Item: section `49-claude-code-drift-automation`, "Test-coverage gaps in the drift notice" (the `test_cli.py` and `test_check.py` parts).

**Files:**
- Test: `build/cc_guide/test_cli.py:166-277`, `build/cc_guide/test_check.py:504-512`

These tests cover working code, so none fails first. Each step names a **mutant**: a one-line source change that must turn the new test red. Apply the mutant, run the test and see FAIL, revert the mutant, and see PASS. Record each pair in the task report.

- [ ] **Step 1: A FetchError through the CLI.** Add `test_check_hook_turns_a_failed_fetch_into_the_error_notice`:
  - Setup: `cli.main([... 'check', '--hook', '--run', 'r1'], fetch=<a fetch that raises FetchError('…: timed out') for the changelog>)`, with no `--docs`, after `notice.record_check(cache, 0, earlier, 'r0')`.
  - Assert: exit 2; `capsys` empty; `shown(cache).startswith('cc-guide · check failed: ')` and names the URL; the record has `exit == 2` and `ok_epoch == int(earlier.timestamp())`.
  - Mutant: in `notice.after_check`, change `if code == 2:` to `if code == 3:`.
- [ ] **Step 2: No cache.** Add `test_check_hook_with_no_cache_writes_nothing_and_prints_nothing`:
  - Setup: monkeypatch `cli.default_cache` to raise `RuntimeError`, and run `cli.main(['check', '--hook', '--run', 'r1'])` with `isolated_home`.
  - Assert: exit 2; `capsys` empty; no file under the isolated home.
  - Mutant: in `hook_failure`, drop `if cache is not None:` so it calls `after_failure(None, …)`. The test must fail on the traceback output.
- [ ] **Step 3: The double `OSError` pass.** Add `test_check_hook_failure_that_cannot_write_is_silent`, parametrized over a SetupError and a crash, as the existing tests raise them:
  - Setup: monkeypatch `notice.after_failure` to raise `OSError`.
  - Assert: exit 2 and `capsys` empty.
  - Mutant: change `except OSError:` to `except ValueError:`.
- [ ] **Step 4: The spy's directory.** In `test_check_hook_renames_the_record_into_place_after_the_notice_and_its_digest`, record `(Path(dst).parent, Path(dst).name)` and assert that the three written names arrive in order, each with `parent == cache`.
  - Mutant: in `notice.replace`, write to `path.with_name('x' + path.name)`. Today's name filter would miss it.
- [ ] **Step 5: A real setup error.** In the same test, replace the `setup-error` param's patched `cli.check` with a real one: `cli.REPO` monkeypatched to a `fixture_repo` that has no manifest, as `test_check_hook_turns_a_setup_error_into_the_error_line` builds it.
  - Mutant: none. The param must still pass, and the test report shows its message is `state.MANIFEST: not found in main`.
- [ ] **Step 6: Rename** `test_check_hook_prints_nothing_and_leaves_the_notice_then_the_record` to `test_check_hook_prints_nothing_and_leaves_the_notice_and_the_record`. It reads only final contents; the order is pinned by the Step 4 test.
- [ ] **Step 7: The audit-only report.** In `test_a_failed_fetch_still_runs_the_audit_due_rule`, add `assert set(report['due']) == {'lint', 'audit'}`.
  - Mutant: move the `due.update({...})` block out of `if docs is not None:` with `findings = []`.
- [ ] **Step 8: Run the suite**

Run: `uv run python build/run_suites.py cc_guide`
Expected: PASS, with each mutant reverted (`git diff --stat` shows test files only).

- [ ] **Step 9: Commit**

```bash
git add build/cc_guide/test_cli.py build/cc_guide/test_check.py
git commit -m "test(cc-guide): pin check --hook's fetch-error, no-cache and write-failure paths"
```

### Task 5: `notice.sh show` and `refresh` test gaps

Item: the same section 49 item (the `test_notice_sh.py` part). Use the same mutant procedure as Task 4.

**Files:**
- Test: `build/cc_guide/test_notice_sh.py`

- [ ] **Step 1: Digest before notice.** Add `test_show_reads_the_digest_before_the_notice`, parametrized over `SHELLS`:
  - Setup: put a `cat` stub first on `PATH` that logs `$1` and then execs `/bin/cat`, as the `mv` stub in `test_show_replaces_notice_shown_by_renaming_a_temp_file_in_the_cache` does.
  - Assert: the logged order of `notice.digest` and `notice.json` is digest first.
  - Mutant: swap `notice.sh:29` and `:30`.
- [ ] **Step 2: `mv -f`.** In `test_show_replaces_notice_shown_by_renaming_a_temp_file_in_the_cache` and `test_refresh_replaces_unfinished_by_renaming_a_temp_file_in_the_cache`, assert `args[0] == '-f'`.
  - Mutant: drop `-f` at `notice.sh:35`, then at `:116`.
- [ ] **Step 3: Empty-notice path guard.** In `test_show_prints_nothing_before_any_check_or_when_nothing_is_due`, after the empty notice, write a real notice to the same `cache_of(tmp_path)` and assert `shown(...)` prints it. This proves the quiet run read that path.
  - Mutant: change `notice.sh:23`'s `cc-guide` to `cc-guidex`.
- [ ] **Step 4: No-`HOME` path guard.** In `test_show_without_home_and_an_unknown_subcommand_both_exit_zero`, write a notice to `cache_of(tmp_path)` first. Assert that the run without `HOME` is quiet, and a run with `HOME=tmp_path` shows it.
  - Mutant: as in Step 3.
- [ ] **Step 5: Over `SHELLS`.** Parametrize over `SHELLS`, passing `shell=shell` to every `sh(...)`, in:
  - `test_show_still_prints_when_it_cannot_record_the_day` (the failed-redirect case)
  - `test_show_without_home_and_an_unknown_subcommand_both_exit_zero` (its first call runs `[shell, str(SCRIPT), 'show']`)
  - `test_refresh_replaces_unfinished_by_renaming_a_temp_file_in_the_cache`
  
  Mutant: none. Both shells must pass. Report each shell that `SHELLS` held on this machine.
- [ ] **Step 6: Run the suite**

Run: `uv run python build/run_suites.py cc_guide`
Expected: PASS, with mutants reverted (`git diff --stat` shows `test_notice_sh.py` only).

- [ ] **Step 7: Commit**

```bash
git add build/cc_guide/test_notice_sh.py
git commit -m "test(cc-guide): pin notice.sh's read order, mv -f, cache path and both shells"
```

---

## Part B — probes

### Task 6: `agent-payload` tells a disobedient parent from drift

Item: section `69-agent-payload-probe`, "The `agent-payload` probe cannot tell a…". Plan 58 batch: only `_trim_block` (D5).

**Files:**
- Modify: `build/cc_guide/probe_checks.py:213-319, 487-501`
- Modify: `build/cc_guide/probes.py:352-411`
- Modify: `build/cc_guide/probe_streams/agent-payload.jsonl`, `agent-payload.payloads.json` (re-saved)
- Test: `build/cc_guide/test_probe_checks.py`, `test_probes.py`, `test_probe_replay.py`
- Live run: `build/cc_guide/PROBES.md` (one row)

**Interfaces:**
- Produces, in `probe_checks.py`:
  - `_trim_block` keeps `model` beside `subagent_type` and `command` in `tool_use` inputs.
  - `requested_models(events: list[dict]) -> dict[str, list[str | None]]`: each subagent type the main session dispatched, mapped to the `model` input of each dispatch, in stream order.
  - `check_parent(events: list[dict]) -> Verdict | None`: ERROR when the parent did not send what `PAYLOAD_PROMPT` asks. That means a `CONTROL_AGENT` dispatch without `model == CONTROL_MODEL`, a `HAIKU_BUILTINS` dispatch with any model, or a `PAYLOAD_AGENTS` type dispatched twice. The finding starts `the parent session `.
  - `payload_file(raw: dict[str, list[str]]) -> dict`: from each log folder's raw lines, `{'logged': {folder: count}, 'payloads': [trimmed, sorted as today]}`.
  - `assess_agent_payload(events, payload_file: dict) -> Verdict`.
- Produces, in `probes.py`: `collect_payload` copies the raw logs into `run_dir`, then writes `payloads.json` from `payload_file` over `run_dir`'s `payloads-<folder>.raw.jsonl`. `rebuild_payloads(run_dir: Path) -> None` is that second half alone.

- [ ] **Step 1: Write the failing tests** in `test_probe_checks.py`:
  - `test_trim_block_keeps_a_dispatch_model`: a `tool_use` with input `{'subagent_type': 'general-purpose', 'model': 'haiku', 'prompt': 'x'}` trims to input `{'subagent_type': 'general-purpose', 'model': 'haiku'}`.
  - `test_a_parent_that_skips_the_control_model_is_error_not_diverges`: in `payload_run()`'s events, drop the parent's control `model`, and make the payloads match. Assert `outcome == ERROR` and the finding starts `the parent session sent general-purpose with no model`.
  - `test_a_parent_that_gives_a_builtin_a_model_is_error`: the same for `claude-code-guide` with `model: 'sonnet'`.
  - `test_an_empty_trimmed_log_names_the_stage_that_dropped_it`: with `logged == {'any': 2, 'agent': 2}` and `payloads == []`, the finding is `the PreToolUse hooks logged 4 payloads, and trim_payload kept none of them (a renamed subagent_type, a moved tool_input, or payloads that carry agent_id)`. With `logged == {'any': 0, 'agent': 0}`, the finding stays `the PreToolUse hooks logged no subagent dispatch`.

- [ ] **Step 2: Run them to verify they fail**

Run: `cd build/cc_guide && uv run --with pytest python -m pytest -q test_probe_checks.py -k 'trim_block or parent or empty_trimmed'`
Expected: FAIL.

- [ ] **Step 3: Implement.** In `assess_agent_payload`, the order is: `broken()`, `check_parent()`, the empty-log check from `payload_file['logged']`, `check_payloads()`, then the served-model checks as today. Change `collect_payload` and `assess_payload` to the new `payloads.json` shape, and update `test_probes.py`'s `collect_payload` test to assert it.

- [ ] **Step 4: Re-save the fixtures from the 2026-11-26 raw run** (no spend):

```bash
cd build/cc_guide
run=~/.cache/agent-skills/cc-guide/probes/20261126T091634-agent-payload
uv run python -c "import probes, sys; from pathlib import Path; r = Path(sys.argv[1]); probes.rebuild_payloads(r); print(probes.save_fixtures(r, 'agent-payload', Path('probe_streams')))" "$run"
```

  Expected: it prints two fixture paths. `git diff probe_streams/` shows `model` in the control's `tool_use` input, `claude_code_version` 2.1.330, and the new `logged` key. Only the `agent-payload` streams carry a `model` input, so no other fixture changes (checked at planning: `grep` over the raw runs under `probes/`).

- [ ] **Step 5: Add replay cases** to `test_probe_replay.py` with `edited()`:
  - the control's `tool_use` input without `model` gives ERROR, finding starting `the parent session`;
  - `claude-code-guide`'s input with `model: 'sonnet'` gives ERROR.

- [ ] **Step 6: Run the suite**

Run: `uv run python build/run_suites.py cc_guide`
Expected: PASS, `test_the_recorded_run_passes[agent-payload]` included.

- [ ] **Step 7: Live run (D7, one invocation).** Run the Global Constraints command with `--only agent-payload`.
  Expected: `agent-payload: PASS: dispatches reach PreToolUse as Agent…`. If it is not PASS, stop (Global Constraints).

- [ ] **Step 8: Commit**

```bash
git add build/cc_guide/probe_checks.py build/cc_guide/probes.py build/cc_guide/probe_streams/agent-payload.* \
  build/cc_guide/test_probe_checks.py build/cc_guide/test_probes.py build/cc_guide/test_probe_replay.py build/cc_guide/PROBES.md
git commit -m "fix(cc-guide): agent-payload reports a disobedient parent as ERROR, not drift"
```

### Task 7: plan 69's review Minors

Item: section `69-agent-payload-probe`, "Review Minors from plan 69's final review" (all seven, D9).

**Files:**
- Modify: `build/cc_guide/probe_checks.py:25-36, 228-266, 300-308`
- Test: `build/cc_guide/test_probe_checks.py`, `build/cc_guide/test_probes.py:582-596`

- [ ] **Step 1: Write the failing tests**
  1. `test_two_payloads_of_one_type_with_different_inputs_are_error`: two `general-purpose` payloads under one matcher, with models `haiku` and `None`, give ERROR, with a finding naming `general-purpose`. Fixes "first is arbitrary".
  2. `test_a_control_model_normalised_to_a_full_id_passes`: control payload model `claude-haiku-5-5` gives no DIVERGES from `check_payloads`. Fixes the normalisation false alarm. The guard's `decide()` checks only that a model is present.
  3. `test_the_model_checks_read_the_agent_matcher_payload`: the `*` payload holds the control model and the `Agent` payload lacks it. That gives DIVERGES.
  4. `test_a_control_served_two_haiku_ids_still_matches_a_builtin_served_one`: control served `{h1, h2}`, built-in served `{h1}`. That gives PASS (subset, not equality).
  5. `test_the_three_agent_strings_tie_to_the_hook`: `pc.DISPATCH_TOOLS[0] == pc.GUARDED_TOOL == pc.GUARD_MATCHER == guard.AGENT_TOOL`. Extend the test at `:252`.
  6. `bad_payload` in `test_probes.py`: parametrize over both log folders (`any`, `agent`).

- [ ] **Step 2: Run them to verify they fail**

Run: `cd build/cc_guide && uv run --with pytest python -m pytest -q test_probe_checks.py test_probes.py -k 'two_payloads or normalised or agent_matcher or two_haiku or agent_strings or payload_probe_reads'`
Expected: tests 1–4 FAIL. Tests 5 and 6 may pass, since they pin constants and coverage.

- [ ] **Step 3: Implement**
  - `first_by_type` becomes `by_type(payloads, matcher) -> dict[str | None, list[dict]]`. `check_payloads` returns ERROR when one type holds payloads whose `model` values differ.
  - The model checks read the `GUARD_MATCHER` payloads.
  - The control check asks for a non-empty `model`, and its finding names the value.
  - The served check is `served[agent] <= served[CONTROL_AGENT]`.
  - Define `DISPATCH_TOOLS = (GUARDED_TOOL, 'Task')` and `GUARD_MATCHER = GUARDED_TOOL`.

- [ ] **Step 4: Run the suite**

Run: `uv run python build/run_suites.py cc_guide`
Expected: PASS, the agent-payload replay included.

- [ ] **Step 5: Commit**

```bash
git add build/cc_guide/probe_checks.py build/cc_guide/test_probe_checks.py build/cc_guide/test_probes.py
git commit -m "fix(cc-guide): agent-payload reads the guard's payload and tolerates a normalised model"
```

### Task 8: probe `explore-override`

Item: section `cc-drift-upkeep-2026-10-20 (…)`, "Two Stage 5 probe candidates", part (a). PASS encodes 2.1.304's observed behavior: a project agent named `Explore` reads CLAUDE.md, as custom agents do, and gets no git-status snapshot, as the built-in does. A DIVERGES row sends `subagents.isolation` and `subagents.models` to `/cc-guide verify`.

**Files:**
- Modify: `build/cc_guide/probes.py` (new section before `PROBE_RUNS`; register in `PROBE_RUNS`)
- Modify: `build/cc_guide/probe_checks.py` (new section)
- Modify: `build/cc_guide/manifest.toml` (new `[[probe]]` after `compaction-cut`)
- Create: `build/cc_guide/probe_streams/explore-override.sightings.json` (through `save_fixtures`)
- Test: `build/cc_guide/test_probe_checks.py`, `test_probes.py`, `test_probe_replay.py`
- Live run: `build/cc_guide/PROBES.md` (one row)

**Interfaces:**
- Produces, in `probe_checks.py`:
  - `EXPLORE_MARK = 'EXPLORE-OVERRIDE'`, `CANARY_AGENT = 'canary-control'`, `CANARY_MARK = 'CANARY-CONTROL'`, `EXPLORE_REPS = 3`.
  - `explore_sightings(events: list[dict] | None, canaries: dict[str, str]) -> dict`. `canaries` is `{'claude_md': …, 'git_status': …}`. The result is `{'broken': str | None, 'leaked': bool, 'tool_calls': {agent: int}, 'seen': {agent: {'mark': bool, 'claude_md': bool, 'git_status': bool}}}`. It reads the raw stream: the parent's Agent inputs for `leaked`, and each subagent's forwarded text and `tool_use` blocks.
  - `assess_explore_override(sightings: list[dict]) -> Verdict`.
- Produces, in `probes.py`: `prepare_explore`, `collect_explore` (writes `sightings.json`, a list with one entry per rep), `assess_explore`.

- [ ] **Step 1: Write the failing unit tests** in `test_probe_checks.py`, on hand-built sightings:
  - `test_explore_override_passes_when_explore_reads_claude_md_and_skips_git_status`: every rep has `Explore` `{'mark': True, 'claude_md': True, 'git_status': False}` and the control all True. Finding: `Explore override read CLAUDE.md and got no git-status snapshot in 3 of 3 reps; the control got both`.
  - `test_explore_override_diverges_when_one_valid_rep_differs`: rep 2's `Explore` has `git_status: True`. DIVERGES, naming rep 2.
  - `test_explore_override_voids_a_rep_whose_subagent_called_a_tool`: `tool_calls['Explore'] == 1` gives ERROR naming the rep, when no rep diverges.
  - `test_explore_override_is_error_when_the_control_misses_a_canary_or_a_mark_is_absent`: parametrize `control claude_md False`, `control git_status False`, `Explore mark False`, `leaked True`.
  - `test_explore_sightings_reads_marks_canaries_and_leaks_from_the_raw_stream`: a raw stream built with the file's helpers.
  
  Verdict precedence: DIVERGES when any valid rep differs from PASS; else ERROR when any rep is void (broken, leaked, a tool call, a missing mark, or a control missing a canary); else PASS.

- [ ] **Step 2: Run them to verify they fail**

Run: `cd build/cc_guide && uv run --with pytest python -m pytest -q test_probe_checks.py -k explore`
Expected: FAIL (`explore_sightings` not defined).

- [ ] **Step 3: Implement**
  - `prepare_explore` builds the scratch folder:
    1. `git init -q`.
    2. Two random canaries (`secrets.token_hex(4)`, prefixed `cm-` and `gs-`), written to `scratch / 'canaries.json'`.
    3. `CLAUDE.md` holding `The canary word for this project is <cm>.`, and an untracked `<gs>.txt`.
    4. Project agents `.claude/agents/explore.md` (`name: Explore`) and `canary-control.md` (`name: canary-control`). Each has `disallowedTools: Read, Grep, Glob, Bash, Edit, Write` and a body that has it answer from its context alone, in three lines: its mark; the CLAUDE.md canary word or `NONE`; and the untracked file names that its git status lists, or `NONE`.
  - The parent prompt dispatches both agents with the prompt `Follow your instructions.` and names no canary. Use `claude_args(..., turns=PAYLOAD_TURNS, sources='project', mode='default', allow=('Agent',), extra=('--forward-subagent-text',))`.
  - Return `EXPLORE_REPS` invocations named `explore-1` … `explore-3`. `collect_explore` writes `sightings.json` from each stream and `canaries.json`.
  - `--setting-sources project` keeps the user's agents out, including this repo's installed `agents/explore.md`. The agent-payload probe relies on the same rule. The mark proves which definition served.
  - Register `'explore-override': Probe(prepare_explore, collect_explore, assess_explore, {'sightings.json': 'explore-override.sightings.json'})`.

- [ ] **Step 4: Register in `manifest.toml`**

```toml
[[probe]]
id = 'explore-override'
# A project agent named Explore, overriding the built-in: CLAUDE.md and the git-status snapshot at spawn. The docs say
# only that the built-in skips both (owner ruling B2, 2026-10-20; Stage 5 probe candidate (a)).
sections = ['subagents.isolation', 'subagents.models']
files = ['agents/explore.md']
```

- [ ] **Step 5: Add a `run_probe` test** `test_the_explore_probe_reads_its_run_like_a_live_one` in `test_probes.py`, with `FakeRuns` streams built by the Step 1 helpers. Expect PASS through `run_probe('explore-override', …)`.

- [ ] **Step 6: Live run (D7, 3 invocations).** Use `--only explore-override`.
  Expected: `explore-override: PASS: …`. If it is not PASS, stop.

- [ ] **Step 7: Save fixtures and add replay cases**

```bash
cd build/cc_guide && uv run python -c "import probes, sys; from pathlib import Path; print(probes.save_fixtures(Path(sys.argv[1]), 'explore-override', Path('probe_streams')))" <raw output folder from Step 6>
```

  In `test_probe_replay.py`, add two cases on the fixture: `Explore` `git_status` set True in one rep gives DIVERGES, and the control's `claude_md` set False gives ERROR.

- [ ] **Step 8: Run the suite and the lints**

Run: `uv run python build/run_suites.py cc_guide && bash build/run_commit_lints.sh`
Expected: PASS; `commit lints passed`.

- [ ] **Step 9: Commit** (the registration and its row together)

```bash
git add build/cc_guide/probes.py build/cc_guide/probe_checks.py build/cc_guide/manifest.toml build/cc_guide/PROBES.md \
  build/cc_guide/probe_streams/explore-override.sightings.json build/cc_guide/test_probe_checks.py \
  build/cc_guide/test_probes.py build/cc_guide/test_probe_replay.py
git commit -m "feat(cc-guide): probe explore-override (Stage 5 candidate a)"
```

### Task 9: probe `async-teardown`

Item: the same Stage 5 item, part (b). PASS encodes 2.1.304's observed behavior. An async SessionStart hook still running when `claude -p` ends first gets SIGTERM, which is the signal `notice.sh`'s `HUP INT TERM` trap handles, and is gone shortly after. A DIVERGES row sends `hooks.pitfalls` to `/cc-guide verify`.

**Files:** the same as Task 8, with fixture names `async-teardown.jsonl` and `async-teardown.log`.

**Interfaces:**
- Produces, in `probe_checks.py`:
  - `TEARDOWN_SIGNALS = ('TERM', 'HUP', 'INT')`
  - `assess_async_teardown(events: list[dict] | None, log: list[str]) -> Verdict`. The `log` lines are `start <pid>`, then any signal names in order, then `gone` or `alive`.
- Produces, in `probes.py`: `TEARDOWN_WAIT = 5` (seconds), `TEARDOWN_HOOK`, `prepare_teardown`, `collect_teardown`, `assess_teardown`.

- [ ] **Step 1: Write the failing unit tests** in `test_probe_checks.py`:
  - `test_async_teardown_passes_on_term_then_gone`: log `['start 41', 'TERM', 'gone']`. PASS, finding `the async SessionStart hook got TERM first at teardown and was gone within 5 s`.
  - `test_async_teardown_diverges` parametrized:
    - `['start 41', 'HUP', 'gone']`: another signal first.
    - `['start 41', 'gone']`: no catchable signal, so notice.sh's trap never runs.
    - `['start 41', 'TERM', 'alive']`: the hook outlived teardown.
  - `test_async_teardown_is_error_when_the_hook_never_started`: log `[]`.
  - `test_async_teardown_reads_a_cancelled_hook_response_when_the_stream_has_one`. A `SessionStart` `hook_response` with an `outcome` other than `cancelled` gives DIVERGES. None in the stream is no finding.

- [ ] **Step 2: Run them to verify they fail**

Run: `cd build/cc_guide && uv run --with pytest python -m pytest -q test_probe_checks.py -k async_teardown`
Expected: FAIL.

- [ ] **Step 3: Implement**
  - `TEARDOWN_HOOK` is a `/bin/sh` script taking the log path. It does the following:
    1. Appends `start $$` to the log.
    2. Sets one trap per signal in `TEARDOWN_SIGNALS`, each one `printf '<NAME>\n' >> "$log"` and nothing else, so it keeps running.
    3. Loops `sleep 1 & wait $!` for up to 120 s, so a trap runs at once.
  - `prepare_teardown`:
    1. Writes the hook.
    2. Registers it in the scratch `.claude/settings.json` as a `SessionStart` command hook with `"async": true`.
    3. Runs `claude_args(claude, 'Reply with the word OK.', turns=1, sources='project', mode='default', extra=('--include-hook-events',))`.
  - `collect_teardown`:
    1. Reads the pid from the `start` line.
    2. Polls `os.kill(pid, 0)` for up to `TEARDOWN_WAIT` s.
    3. Appends `gone` or `alive`. On `alive`, it sends SIGKILL to the pid.
    4. Writes `teardown.log` to `run_dir`.
  - Register `'async-teardown': Probe(prepare_teardown, collect_teardown, assess_teardown, {'teardown.jsonl': 'async-teardown.jsonl', 'teardown.log': 'async-teardown.log'})`.

- [ ] **Step 4: Register in `manifest.toml`**

```toml
[[probe]]
id = 'async-teardown'
# The signal claude -p sends an async hook still running at teardown; notice.sh's refresh traps HUP, INT and TERM
# (owner ruling on the G7 gap, 2026-10-20; Stage 5 probe candidate (b)).
sections = ['hooks.pitfalls']
files = ['build/cc_guide/notice.sh']
```

- [ ] **Step 5: Add `test_the_teardown_probe_reads_its_run_like_a_live_one`** in `test_probes.py`, with a `FakeRuns` side effect that writes the log lines. Expect PASS.

- [ ] **Step 6: Live run (D7, 1 invocation).** Use `--only async-teardown`.
  Expected: `async-teardown: PASS: …`. If it is not PASS, stop.

- [ ] **Step 7: Save fixtures** with the Task 8 Step 7 command and id `async-teardown`. Add replay cases: `TERM` replaced by `HUP` gives DIVERGES, and an empty log gives ERROR.

- [ ] **Step 8: Run the suite and the lints**

Run: `uv run python build/run_suites.py cc_guide && bash build/run_commit_lints.sh`
Expected: PASS; `commit lints passed`.

- [ ] **Step 9: Commit**

```bash
git add build/cc_guide/probes.py build/cc_guide/probe_checks.py build/cc_guide/manifest.toml build/cc_guide/PROBES.md \
  build/cc_guide/probe_streams/async-teardown.* build/cc_guide/test_probe_checks.py build/cc_guide/test_probes.py \
  build/cc_guide/test_probe_replay.py
git commit -m "feat(cc-guide): probe async-teardown (Stage 5 candidate b)"
```

- [ ] **Step 10: Check the notice stays quiet.** Run `uv run python build/cc_guide/cli.py check --worktree` from the repo root.
  Expected: the `probes:` line names neither new probe.

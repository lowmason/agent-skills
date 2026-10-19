# Claude Code Drift Automation: Pin `baseline rebaseline` to Its Packet's Head — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop `baseline rebaseline` from recording hashes of docs text that no `/cc-guide` review read. `settle` prints each `rebaseline` with `--head <the packet's head>`, and `rebaseline` refuses when the latest fetch is at another release, naming both.

**Architecture:** `cli.py`'s `baseline rebaseline` gains an optional `--head RELEASE`. It is compared with `fetch.json`'s `changelog_head` before anything is read from `latest/` or written. `settle.py` appends `--head <index.json's head>` to every `rebaseline` it prints, for triage, verify and audit packets alike. How `check` writes the cache does not change: the fix reads only the existing `changelog_head`. Task 1 amends the drift spec's R7 and R8.8. The planning record settles plan 49's final-review question O3: whether two `check` runs can share `latest/`.

**Tech Stack:** Python 3.13, stdlib only (`build/cc_guide/cli.py`, `settle.py`); pytest through `uv run`; Markdown (the spec, `build/CLAUDE.md`, the `/cc-guide` skill and its `references/formats.md`).

**Spec:** `specs/claude-code-drift-automation-spec.md`: R7 (`baseline`) and R8.8 (post-processing; its step 4 is the bookkeeping order), which Task 1 amends. Context: R6.3 and R6.4 (the fetch), R6.11 (packets), R8.10 (`settle`), Decision 6 (a new release gates the fetch) and Decision 10 (one cache, outside every checkout).

## Background

Labels used below, each expanded here once:
- **Plan 49** is Stage 4 of the drift spec, the session-start notice (`build/cc_guide/notice.sh`, `notice.py`). It merged on 2026-10-18 as lowmason/agent-skills#55.
- **Plan 49's Q1** was its open question for plan review: a session start can now refetch the docs under a `/cc-guide` run. **Plan 49's decision D2** is the owner's answer. It takes option (b), guarding the race in Stage 3's tools, with no interim rule. This plan implements it.
- **O1 and O3** are owner-facing items from plan 49's execution ledger. O1: a signalled `refresh` left its check running, with no time budget and no count. **Plan 49's decision D5** fixed it: the signal trap now kills the check. O3: whether two concurrent `check --hook` runs can safely share `~/.cache/agent-skills/cc-guide/latest/`. Plan 49's final review rated O3 Minor and folded it into this item. The planning record below settles it.
- **A packet** is the directory `cli.py packets` writes for the `cc-guide-verifier` agent (spec R6.11). Its `index.json` records `head`, the changelog head that `fetch.json` named when the packet was built.

Why now: since plan 49 merged, `notice.sh refresh` runs `check --hook` at a session start once the last good check is a day old. When the changelog head has moved, that check rewrites the shared `latest/`. A manual `check`, or another `/cc-guide` run, can do the same. `baseline rebaseline` re-hashes from `latest/` at whatever head `fetch.json` holds. So a refetch between a `/cc-guide` review and its rebaseline records hashes for docs text the verifier never read. Only `baseline audited` is pinned today, through `--to` (plan 44).

## Global Constraints

- **Work in a worktree** (spec, Sequencing constraints): "Check `git rev-parse main origin/main` first: `EnterWorktree` branches from `origin/main` and omits unpushed commits, and concurrent sessions switch and rebase the shared checkout." Execute on a branch that holds this plan's commit. That is this plan's branch, `claude/suspicious-ptolemy-161633`, in its worktree `/Users/lowell/Projects/agent-skills/.claude/worktrees/suspicious-ptolemy-161633`. Once the owner has merged the plan to `main`, a worktree cut from current `main` also works. Never execute in the shared checkout.
- **Run every command from the worktree root**, the session's working directory, with the relative paths this plan gives. Never `cd`: a Bash `cd` persists and moves the session's working directory. A guarded worktree session refuses compound shell (`&&`, pipes, `$(...)`), so each command stands alone, and the suite runs through `uv run --directory build/cc_guide`.
- **The tests are cache-safe; live runs are not.** `test_cli.py`, `test_settle.py` and `test_check.py` each import the autouse `isolated_home` fixture. `build/cc_guide/cc_fixtures.py` says: "importing `isolated_home` registers that autouse fixture in the importing module, so no test reaches the real ~/.cache". Every test this plan adds goes into one of those three files. `~/.cache/agent-skills/cc-guide/` is one directory for `main` and every worktree. Never run a live `check`, `packets`, `settle` or `baseline rebaseline` from the worktree against it: a live `check` refetches the shared `latest/`, which is the race this plan fixes. A live trial happens only after the merge, from `main`, with no `/cc-guide` run in flight. `cli.py lint`, which `build/run_commit_lints.sh` runs, only reads the cache.
- **The worktree's own notice runs at its session starts.** A session started in the worktree runs `"$CLAUDE_PROJECT_DIR"/build/cc_guide/notice.sh`. At most once a day, that launches the worktree's own `cli.py check --hook` against the shared cache. So:
  - `cli.py` stays importable at every commit;
  - `fetch.json`'s format stays unchanged: this plan only reads `changelog_head`, which `check.py` writes and `state.py` validates;
  - no new session starts in the worktree while `cli.py` is broken mid-edit.
- **`check` reads `main`'s commit by default**, so any `check` in the worktree passes `--worktree`. This plan runs none outside the tests.
- **Tests** (R12.1): "Tests are offline. Fixtures (docs pages, `llms.txt`, a changelog) are hand-written, never copied docs text". Module and test basenames stay unique across `build/`; this plan adds no module.
- **Never commit docs text** (Sequencing constraints): quotes from the docs appear only in session reports.
- **Every existing gate passes** (Validation 6): `check_frontmatter.py`, `check_provenance.py`, `check_snippets.py skills/` (Tier 1), the dependency-drift test, the `build/` suite, `sync_runtime_assets.py --check` with no adapter change, and `check_conformance.py`. `bash build/run_commit_lints.sh` runs all eight commit lints; run it before every commit.
- **Test counts are deltas** (+N), never absolute pytest totals.
- **The root `CLAUDE.md` is not edited.** It has 195 lines at `e9325de`, under the 200-line `claude-md-size` check (R12.7).
- **Python style:** single quotes, f-strings, named constants (G25), stdlib only in `build/cc_guide/`, Python 3.13.
- **Expand every bare label at first use** (owner preference) in docs and reports for the owner: give a decision, question or plan number its plain meaning beside it.
- **Commit trailer:** the executing session's own `Co-Authored-By:` line, as a second `-m`. Subagent-authored commits keep that same line. Check it with `git log -1 --format=%B`.

## Decisions

- **D1** (owner, brief, 2026-10-18; decided at plan 49's review as its D2, 2026-10-17): plan 49's Q1 takes option (b). `settle` prints `rebaseline --head <the packet's index.json head>`, and `rebaseline` refuses when `fetch.json`'s `changelog_head` differs, naming both heads. No interim rule applies until it lands. It amends drift spec R7 and R8.8. Applied in: Task 1 (spec amendment), Tasks 2 and 3.
- **D2** (owner, brief, 2026-10-18): settle, with this item, whether two `check --hook` runs can safely share `latest/` (plan 49's final review, O3). Applied in: Planning record (O3), Task 4.
- **D3** (owner, brief, 2026-10-18): the work is safe in a worktree under the brief's constraints. Applied in: Global Constraints.
- **D4** (owner, brief, 2026-10-18): Stage 5 (probes) is not planned here; it is the next plan. Applied in: Plan completion notes.

---

## Planning record

### Facts measured while planning (2026-10-18, at `e9325de`)

- The cc_guide suite: 500 passed.
- **How `check` writes `latest/`.** `live_docs` is in `build/cc_guide/check.py:102-163`. On a head move it first deletes the cached pages its manifest does not map (`:127-133`). Then it fetches every mapped page in parallel (`:141-142`) and writes or removes each one in a loop (`:144-157`). It writes `changelog.md` and `llms.txt` next (`:158-159`), and `fetch.json` last (`:160-161`). No write is atomic: each is a `write_bytes` or `write_text` in place. No test pins that `fetch.json` comes last.
- **Every packet records its head.** `packets.header()` (`packets.py:120-124`) writes `head` into every mode's `index.json`. The value is the fetch record's `changelog_head`, read when the packet's inputs load (`packets.py:61-68`). This has held since the first `packets` commit (`544cbda`, plan 44).
- **`settle` prints `rebaseline` in two places:** `settle_triage` (`settle.py:432`) and `settle_review` (`settle.py:621`), which serves verify and audit. `audited --to index['head']` (`settle.py:627`) is the precedent.
- **`rebaseline` takes its release from `fetch.json`.** `run_baseline` (`cli.py:305-315`) reads the record, uses its head as the snapshot release, and re-hashes from `latest/`. `audited`'s `--to` check (`cli.py:299-304`) is the pinned precedent.
- **Where the flag goes.** `rebaseline`'s `refs` is `nargs='*'` (`cli.py:134`). Measured with a parser of the same shape: the argparse of Python 3.12.12 and 3.13.16 accepts `--head` before the group, after the refs, or between them. Python 3.9.6's rejects it between the group and the refs ("unrecognized arguments"). `settle` prints it last, as it prints `advance ... --to` and `audited ... --to`, and Task 3's test parses each printed line through `cli.parser()`.
- **`test_settle.py` pins the printed commands exactly.** Twelve expected lines name a `rebaseline`: `:95`, `:191`, `:209`, `:534`, `:713`, `:725`, `:765`, `:855`, `:876`, `:886`, `:1023` and `:1035`. And `:856` slices the refs off a printed line with `shlex.split`, so an appended `--head 2.1.902` would reach `baseline.rebaseline` as two more refs.
- **The lock.** `notice.sh refresh` takes `lock/` (`notice.sh:71-76`, `:145-148`) and breaks one older than 60 minutes. Since plan 49's D5, its HUP, INT and TERM trap kills the check (`:116`).
- **The skill.**
  - `.claude/skills/cc-guide/SKILL.md:42` says to run settle's commands in order, one at a time. It says nothing of a command that exits 2.
  - `:49` tells the session to edit a printed `rebaseline`'s refs in one cross-group case.
  - `references/formats.md:58` describes the bookkeeping. It names `audited <group> --to <head>`, but not a pin for `rebaseline`.

### Who reads `latest/`, and what a refetch to a newer head does to each

| Reader | What it reads there | After a refetch to a newer head | Pin needed? |
|---|---|---|---|
| `baseline rebaseline` | each target page, `llms.txt`, and `fetch.json`'s head as the snapshot release | hashes the newer text, which no review read, and snapshots it under the newer release | **Yes: this plan** |
| `packets` | pages, the changelog and `fetch.json`'s head | builds a consistent packet at the newer head, and records that head | No |
| `settle` | nothing there: it reads its packet's `index.json`, `guide.md` and `report.md`, and the `<head>/docs/` snapshot | unaffected; from Task 3 it passes the packet's head on | No |
| `baseline audited --to` | the newest cached changelog's labels | the packet's head is still a release of the newer changelog | No: `--to` pins it (plan 44) |
| `baseline advance --to` | the same labels | the target is still a release; `checked` takes the target, not the head | No |
| `baseline accept --substantive` | the newest cached release | `changed` takes the newer release, which still exceeds each citer stamp it exceeded | No |
| `lint` | the newest cached changelog's labels | knows more releases | No |

So after a refused `rebaseline`, the rest of a run's commands still hold, because none of them hashes docs text. The blocks keep their old baseline, and the next `check` compares them with the newer docs (DF3).

### O3: can two `check` runs share `latest/`?

Plan 49's final review asked this of two `check --hook` runs. The answer covers any two `check` runs, since `refresh`'s lock orders only refreshes.

**When runs overlap.** `refresh`'s lock stops a second refresh. Since plan 49's D5, a signalled refresh takes its check with it, so O1's orphan check no longer outlives its refresh. Two `check --hook` runs can then overlap only through the stale-lock race: a refresh killed by SIGKILL leaves its lock for up to 60 minutes, and two later refreshes can both break it. A manual `check`, or a `/cc-guide` run's `check --worktree`, takes no lock, so either can overlap a refresh or another run.

**What they share.** Every run without `--docs` writes `latest/` the way `live_docs` does (Facts, above). Within one changelog head, nothing rewrites a cached page (R6.3, Decision 6). So `latest/` changes only when the head moves, or when a missing page is fetched again.

**What an overlap can do.** All of it happens in the cache:
- A run can read during another run's write loop, which takes milliseconds. It can then read one page half-written, or a page already from the newer fetch while `fetch.json` still names the older head. A `check` then reports a wrong finding or notice once, and the next check corrects it. A half-written `fetch.json` or changelog gives a parse error, exit 2.
- A `packets` run in that moment can copy such a page into the head's snapshot, `<head>/docs/`. Later packets at that head then refuse to overwrite it ("already holds different text"). The refusal is visible, and it lasts until the head moves or the file is removed.
- A head move's cleanup, in a run on `main`'s manifest, deletes a page that only a worktree's manifest maps. The worktree's next `check` fetches it again (R6.3).

**What reaches the repo.** Only `rebaseline` turns what it reads in `latest/` into committed state. The table above shows it is also the only reader that a moved head misleads. Task 2's pin refuses it once a refetch has finished. Task 4 pins the premise with a test: `fetch.json` is written after every page, so a recorded head always names a finished fetch. A run that dies mid-write leaves the older head recorded, which makes the next `check` refetch every page.

**The residual, accepted.** A `rebaseline` run during the milliseconds another run is writing pages passes the pin, since `fetch.json` still names the older head.
- For a verify or audit packet, `copy_to_snapshot` (`state.py:499-514`) still refuses then. `packets` copied each of the group's cached pages into `<head>/docs/`, and a rewritten page now holds different bytes.
- A triage packet copies no page, so a triage's `rebaseline` in that moment can hash a page from the newer fetch.

Closing that window needs `check` to write `latest/` as a whole, as a staged directory swapped in at once. That is spec-level (Layout, R6.3, R6.4) and goes beyond D1.

**Answer: yes.** Two `check` runs can share `latest/`. An overlap's effects stay in the cache, and each is either visible or corrected by the next check. The one path into the repo is pinned by this plan.

### Settled defaults (your human partner reviews each)

- **DF1. `--head` is optional**, as `audited --to` is. `settle` always prints it. A manual `rebaseline` after reading a `check` report runs as before. `check`'s summary prints `changelog head <release>` for anyone who wants to pin one by hand. The existing tests, and the manual order in `build/CLAUDE.md` and `cli.py`'s docstring, stay valid. If wrong: make it required. Then every `rebaseline` call in `test_cli.py`, including `test_bookkeeping_alone_brings_check_to_exit_zero`, gains `--head 2.1.902`, and so do the manual flow's docs.
- **DF2. The refusal comes first and writes nothing.** In `run_baseline` it comes right after the fetch record is read, and before `writable_snapshot`, `baseline.rebaseline` and `copy_to_snapshot`. It exits 2 (a `SetupError`) with one `cc-guide:` line that names both releases and says what to do: skip it, and the next check compares the blocks again. A `--head` that is not a release label gets the same refusal, which shows it beside the real head. There is no separate label check (YAGNI).
- **DF3. After a refusal, the run skips that `rebaseline` and runs the rest**, and reports it to the owner. Task 3 writes this into the skill, and Task 1's A2 writes it into R8.8. The readers table shows why the rest still hold. The skill also says never to drop `--head` to get past the refusal: the flag is optional (DF1), so dropping it is one edit away. The alternative was to re-run the review at the newer head. Skipping costs nothing, since the next triage shows the blocks with the newer text anyway. If wrong: the skill stops at a refusal and asks the owner.
- **DF4. O3 is settled without changing `check`'s writes.** The brief asks for a fix that only reads `changelog_head`, and D1 chose the pin over a separate cache for the hook. Task 4 pins the premise the pin rests on, that `fetch.json` comes last, with a test that a mutation is shown to break. Task 1's A3 records the sharing rule in R6.4, and it is optional. If wrong: a further task makes `live_docs` write each file under a temporary name and `os.replace` it, as `notice.py` already does. That removes half-written reads (not mixed heads), at the cost of changing `check.py`'s writes.
- **DF5. The residual is recorded, not deferred.** If wrong: the completion protocol logs "Write `latest/` as a whole" as a deferred item, Size: design.
- **DF6. The docs.** Task 2 adds the `--head` rule to `cli.py`'s docstring and `rebaseline --help`. Task 3 adds the pin to `settle.py`'s docstring, one sentence of `build/CLAUDE.md`, the skill's step 4 and its cross-group note, and the bookkeeping line in `references/formats.md`. The root `CLAUDE.md` is not edited.

### Prototype and replay

Every Replace and with block in Tasks 1–4 was replayed, step by step in task order, onto a throwaway clone of `e9325de` (`~/.cache/agent-skills/scratch/plan51-proto`). A script lifted the blocks out of this file and refused any anchor that did not match exactly as many times as the step states. So the replay ran this plan's text, not a copy of it. What it saw is a record, not a target:
- **Each RED came out as its step predicts.**
  - Task 2 Step 2: 2 failed. The new test failed on `SystemExit: 2`, with argparse's `cli.py: error: unrecognized arguments: --head 2.1.901`; the help test failed on its new assertion.
  - Task 3 Step 2: 1 failed, at index 3, `None != '2.1.902'`. All three packets' `rebaseline` lines were found and parsed.
  - Task 3 Step 4: the 11 named tests failed, and no other.
  - Task 4: the test passed at once. With Step 3's mutation it failed on `'2.1.903' == '2.1.902'`, and after `git restore` only `test_check.py` was modified.
- **The directory at `env-vars.md` raises `IsADirectoryError` on this Mac** (Python 3.13.16), once `tools.md` holds the newer text.
- **The suites.** cc_guide went from 500 to 503 passed (+3). The build directory's suite went from 1083 to 1086 passed (+3), with 13 skipped both times. Both runs had the same 4 `test_verify_citations.py` failures, which need the gitignored `build/.scratch/`.
- **The gates.** All eight commit lints passed after each task. `sync_runtime_assets.py --check` printed nothing. `cli.py lint` printed byte for byte what the base prints: exit 0, and its five `STALE` lines are the existing backlog.
- **The replay corrected the plan twice.** The first correction is the argparse fact in Facts, which was measured, not assumed. The second is Task 3 Step 5's rewrap: a plain replace-all had left three lines at 126 to 136 columns, past the files' 121.

### Plan ID

`entry_check.py` reported `next free: 50` at the start of planning (2026-10-18). Re-run right before this file was written, it reported `next free: 51`: `50-superpowers-upstream-fixes.md` had appeared on `claude/exciting-ritchie-bd33d6`. No collisions. Another planning session, for `specs/write-with-asd-ste100.md`, may claim the same id, and the owner settles collisions at integration. If this plan is renumbered, update its file name, the `plan 51` tags in Task 1's A2 and A3, and the deferred-item tick in the Plan completion notes.

### Next plan

Stage 5 (probes: R10, R12.6 and `/cc-guide probes`) is the drift spec's last stage and the next plan for this spec. It is not planned here.

---

### Task 1: Amend the drift spec (D1; wording approved at plan review)

**Files:**
- Modify: `specs/claude-code-drift-automation-spec.md`: R7's `rebaseline` bullet, R8.8 step 4, and R6.4 if the owner approves A3.

The spec's status line stays untouched. A3 is optional (DF4): skip Step 4 if the owner declined it at plan review.

- [ ] **Step 1: Record the starting counts.** Task 5 compares against these. The build directory's suite takes about a minute.

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q`

Run: `uv run --directory build --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q`

Expected: note each summary line. In a worktree without the gitignored `build/.scratch/`, the build directory's suite has four `test_verify_citations.py` failures.

- [ ] **Step 2: A1, R7's `rebaseline` bullet.** The flag goes into the bullet's signature, and the rule goes at its end.

**Replace** in `specs/claude-code-drift-automation-spec.md`:

```markdown
- `rebaseline <group> [<block keys>]`: re-hash the group's selected blocks,
```

**with:**

```markdown
- `rebaseline <group> [<block keys>] [--head <release>]`: re-hash the
  group's selected blocks,
```

**Replace** in `specs/claude-code-drift-automation-spec.md`:

```markdown
  `check` prints it, so a block `check` could name only by its key hash is
  listed by that hash (R2.3).
```

**with:**

```markdown
  `check` prints it, so a block `check` could name only by its key hash is
  listed by that hash (R2.3). `--head` names the release a review read the
  docs at: the run refuses, naming both releases and writing nothing, when
  `fetch.json`'s `changelog_head` is another one, since any `check` (a
  session start's `refresh`, a manual run, another `/cc-guide` run) may have
  refetched `latest/` after the review. `settle` prints `--head` with the
  packet's head, as it prints `audited --to` (owner, plan 49 decision D2,
  2026-10-17).
```

- [ ] **Step 3: A2, R8.8 step 4's `rebaseline` bullet.**

**Replace** in `specs/claude-code-drift-automation-spec.md`:

```markdown
   - `rebaseline` for the affected blocks;
```

**with:**

```markdown
   - `rebaseline` for the affected blocks, with `--head` naming the packet's
     head (R7) (owner, plan 49 decision D2, 2026-10-17). One that refuses,
     because a later fetch moved `latest/`, is skipped and the rest still
     run, since none of them hashes docs text: the blocks keep their
     baseline, and the next `check` compares them again (owner, plan 51,
     2026-10-18);
```

- [ ] **Step 4: A3, R6.4 (optional).**

**Replace** in `specs/claude-code-drift-automation-spec.md`:

```markdown
to `~/.cache/agent-skills/cc-guide/latest/docs/`, overwriting, with the fetch
time and changelog head recorded beside them.
```

**with:**

```markdown
to `~/.cache/agent-skills/cc-guide/latest/docs/`, overwriting, with the fetch
time and changelog head recorded beside them after the last page, so a
recorded head names a finished fetch. Every session and checkout shares this
`latest/` (Decision 10), and the last fetch wins: of the commands that read
it, only `rebaseline` turns what it reads into baseline state, so it alone
is pinned to a packet's head (R7) (owner, plan 51, 2026-10-18).
```

- [ ] **Step 5: Run the gates.**

Run: `bash build/run_commit_lints.sh`
Expected: all eight lints pass. The spec is under `specs/`, which the citation lint does not read.

- [ ] **Step 6: Commit.**

```bash
git add specs/claude-code-drift-automation-spec.md
git commit -m "docs(specs): pin rebaseline to its packet's head (drift R7, R8.8)"
```

---

### Task 2: `rebaseline --head` refuses a fetch at another release

**Files:**
- Modify: `build/cc_guide/cli.py`: the module docstring (`:27`, `:45-46`), `REBASELINE_HELP` (`:110`), the parser (`:133-134`), and `run_baseline` (`:309-310`).
- Test: `build/cc_guide/test_cli.py`: the help test (`:88-91`), and a new test after `test_rebaseline_never_writes_the_bootstrap_snapshot` (`:415-423`).

**Interfaces:**
- Produces: `cli.parser()`'s `baseline rebaseline` takes `--head RELEASE`, as `args.head`, default `None`; `settle` will print it after the refs. When `fetch.json`'s `changelog_head` R differs from H, `cli.main([..., 'baseline', 'rebaseline', GROUP, *REFS, '--head', H])` exits 2 and writes nothing. It prints `cc-guide: rebaseline --head H: the latest fetch is at R, so latest/ no longer holds the docs reviewed at H; skip this rebaseline, and the next check compares its blocks again` on stderr. With H equal to R, it runs as before. Task 3 prints this flag.

- [ ] **Step 1: Write the failing tests.** The help test gains one assertion, and the refusal gets a new test.

**Replace** in `build/cc_guide/test_cli.py`:

```python
    for out in (' '.join(o.split()) for o in outs):
        assert 'unlisted baselined block' in out
        assert 'also changed or gone' in out
        assert 'the whole page' in out
```

**with:**

```python
    for out in (' '.join(o.split()) for o in outs):
        assert 'unlisted baselined block' in out
        assert 'also changed or gone' in out
        assert 'the whole page' in out
        assert 'it refuses when the latest fetch is at another release' in out
```

**Replace** in `build/cc_guide/test_cli.py`:

```python
    assert not snapshot.exists()
    assert dirty(repo) == []


def test_a_malformed_or_empty_cached_changelog_exits_two(world, capsys):
```

**with:**

```python
    assert not snapshot.exists()
    assert dirty(repo) == []


def test_rebaseline_head_refuses_a_latest_fetch_at_another_release(world, capsys):
    '''Plan 49's decision D2: a session start's refresh, or any other check,
    can refetch latest/ after a packet was built. settle passes the packet's
    head as --head, so rebaseline refuses to hash docs no review read: it
    names both releases and writes nothing. At the packet's own head it runs
    as before, with the flag after the refs, as settle prints it.'''
    repo, cache, _ = world
    write_tree(state.latest_docs(cache), {'tools.md': DOCS['tools.md'].replace('alpha jobs', 'alpha batches')})
    before = (repo / state.BASELINE).read_bytes()
    assert main(cache, 'baseline', 'rebaseline', 'alpha', 'tools › Tools', '--head', '2.1.901') == 2
    assert capsys.readouterr() == ('', 'cc-guide: rebaseline --head 2.1.901: the latest fetch is at 2.1.902, so'
                                       ' latest/ no longer holds the docs reviewed at 2.1.901; skip this rebaseline,'
                                       ' and the next check compares its blocks again\n')
    assert (repo / state.BASELINE).read_bytes() == before
    assert not state.snapshot_docs(cache, '2.1.901').exists()
    assert not state.snapshot_docs(cache, '2.1.902').exists()
    assert main(cache, 'baseline', 'rebaseline', 'alpha', 'tools › Tools', '--head', '2.1.902') == 0
    assert dirty(repo) == [state.BASELINE]
    assert (state.snapshot_docs(cache, '2.1.902') / 'tools.md').is_file()


def test_a_malformed_or_empty_cached_changelog_exits_two(world, capsys):
```

- [ ] **Step 2: Run the two tests and see them fail.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q test_cli.py -k "rebaseline_head or help_shows"`
Expected: `2 failed`. The new test fails with `SystemExit: 2`: `parse_args` runs before `main`'s `try`, and argparse prints `cli.py: error: unrecognized arguments: --head 2.1.901`. The help test fails with an `AssertionError` on its new line.

- [ ] **Step 3: Implement the flag, the refusal and the help text.**

**Replace** in `build/cc_guide/cli.py`:

```python
  baseline rebaseline GROUP [PAGE | 'PAGE › KEY' ...]
```

**with:**

```python
  baseline rebaseline GROUP [PAGE | 'PAGE › KEY' ...] [--head RELEASE]
```

**Replace** in `build/cc_guide/cli.py`:

```python
      whole page. It also refuses to overwrite a snapshot page that holds
      other text.
```

**with:**

```python
      whole page. It also refuses to overwrite a snapshot page that holds
      other text. With --head, the release a review read the docs at, it
      refuses when the latest fetch is at another release, so docs fetched
      after the review are never baselined.
```

**Replace** in `build/cc_guide/cli.py`:

```python
page. It also refuses to overwrite a snapshot page that holds different text.'''
```

**with:**

```python
page. It also refuses to overwrite a snapshot page that holds different text.
With --head, the release a review read the docs at, it refuses when the latest
fetch is at another release, so docs fetched after the review are never
baselined.'''
```

**Replace** in `build/cc_guide/cli.py`:

```python
    rb.add_argument('group')
    rb.add_argument('refs', nargs='*')
```

**with:**

```python
    rb.add_argument('group')
    rb.add_argument('refs', nargs='*')
    rb.add_argument('--head', metavar='RELEASE', help='the release the review read the docs at; refuse when the '
                    'latest fetch is at another')
```

**Replace** in `build/cc_guide/cli.py`:

```python
        release = record['changelog_head']
        writable_snapshot(cache, release)
```

**with:**

```python
        release = record['changelog_head']
        if args.head is not None and args.head != release:
            raise SetupError(f'rebaseline --head {args.head}: the latest fetch is at {release}, so latest/ no longer'
                             f' holds the docs reviewed at {args.head}; skip this rebaseline, and the next check'
                             ' compares its blocks again')
        writable_snapshot(cache, release)
```

- [ ] **Step 4: Run the tests and see them pass.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q test_cli.py -k "rebaseline_head or help_shows"`
Expected: `2 passed`.

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: no failure, and +1 on the count before this task.

- [ ] **Step 5: Run the gates and commit.**

Run: `bash build/run_commit_lints.sh`
Expected: all eight lints pass.

```bash
git add build/cc_guide/cli.py build/cc_guide/test_cli.py
git commit -m "feat(cc_guide): rebaseline --head refuses docs fetched after the review"
```

---

### Task 3: `settle` prints each `rebaseline` with the packet's head

**Files:**
- Modify: `build/cc_guide/settle.py`: the module docstring (`:5`), `settle_triage` (`:432`), and `settle_review` (`:621`).
- Modify: `.claude/skills/cc-guide/SKILL.md` (`:42`, `:49`), `.claude/skills/cc-guide/references/formats.md` (`:58`) and `build/CLAUDE.md` (`:41`).
- Test: `build/cc_guide/test_settle.py`: a new test after `test_an_audit_ends_with_audited_unless_a_section_is_held` (`:879-888`); the twelve expected lines that name a `rebaseline` (`:95`, `:191`, `:209`, `:534`, `:713`, `:725`, `:765`, `:855`, `:876`, `:886`, `:1023`, `:1035`); and the `shlex` slice at `:856`.

**Interfaces:**
- Consumes: Task 2's `--head RELEASE` (`args.head`).
- Produces: every `rebaseline` that `settle` prints ends with `--head <index.json's head>`: `uv run --python 3.13 python build/cc_guide/cli.py baseline rebaseline <group> <ref> ... --head <head>`. As before, `--cache <path>` comes before `baseline` when the packet's cache is not the default one.

Run this task after Task 2: before Task 2, a printed `--head` would be a flag `cli.py` rejects.

- [ ] **Step 1: Write the failing test.** It settles a triage, a verify and an audit packet, and parses each printed `rebaseline` as `cli.py` would. It rewrites `fetch.json` to another head before settling: an implementation that read the cache at settle time, not the packet, would then print the wrong head.

**Replace** in `build/cc_guide/test_settle.py`:

```python
    held = settled(out, 'L14 | Alpha uses ALPHA_TOOL | PARTIAL | tools.md:5 | "absent" | Partly.')
    assert not any('audited' in line for line in held.lines if line.startswith('  '))
```

**with:**

```python
    held = settled(out, 'L14 | Alpha uses ALPHA_TOOL | PARTIAL | tools.md:5 | "absent" | Partly.')
    assert not any('audited' in line for line in held.lines if line.startswith('  '))


def test_every_rebaseline_settle_prints_names_its_packets_head(world, tmp_path):
    '''Plan 49's decision D2: a check after a packet was built can refetch
    latest/, so each rebaseline settle prints, from a triage, a verify or an
    audit, ends with --head and the packet's head, and parses as cli.py
    reads it. The head is the packet's, never the latest fetch at settle
    time.'''
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    t = triage(world, tmp_path)
    v = packets.verify(load(world), tmp_path / 'v', ['alpha.overview', 'alpha.reference'], None)[0]
    a = packets.audit(load(world), tmp_path / 'a', 'alpha')
    state.fetch_record(world[1]).write_text(json.dumps({'fetched_at': '2026-10-05T12:00:00+00:00',
                                                        'changelog_head': '2.1.903'}) + '\n')
    reviewed = ('L14 | Alpha uses ALPHA_TOOL | CONFIRMED | tools.md:5 | "runs alpha batches" | -',
                'alpha.reference | none')
    results = [settled(t, 'B1 | NOISE | - | - | - | "runs alpha batches" | a wording change', '2.1.901 | none',
                       '2.1.902 | none'), settled(v, *reviewed), settled(a, *reviewed)]
    printed = [line for r in results for line in r.lines if ' baseline rebaseline ' in line]
    assert len(printed) == 3
    for line in printed:
        words = shlex.split(line)
        args = cli.parser().parse_args(words[words.index('build/cc_guide/cli.py') + 1:])
        assert (args.action, args.group, args.refs, args.head) == ('rebaseline', 'alpha', ['tools › Tools'], '2.1.902')
```

- [ ] **Step 2: Run it and see it fail.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q test_settle.py -k every_rebaseline_settle_prints`
Expected: `1 failed`, an `AssertionError`: the printed lines parse, but `args.head` is `None` where `'2.1.902'` is expected.

- [ ] **Step 3: Print the flag.**

**Replace** in `build/cc_guide/settle.py`:

```python
triage's settled.json in the packet; `baseline` records the outcome.
```

**with:**

```python
triage's settled.json in the packet; `baseline` records the outcome. Each
rebaseline it prints ends with --head and the packet's head, so `baseline`
refuses it once a later fetch has moved latest/.
```

**Replace** in `build/cc_guide/settle.py`:

```python
    steps = [command(p, 'baseline', 'rebaseline', gid, *refs) for gid, refs in rebaseline.items()]
```

**with:**

```python
    steps = [command(p, 'baseline', 'rebaseline', gid, *refs, '--head', index['head'])
             for gid, refs in rebaseline.items()]
```

**Replace** in `build/cc_guide/settle.py`:

```python
        steps.append(command(p, 'baseline', 'rebaseline', index['group'], *refs))
```

**with:**

```python
        steps.append(command(p, 'baseline', 'rebaseline', index['group'], *refs, '--head', index['head']))
```

- [ ] **Step 4: Run the file and see which old expectations break.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q test_settle.py`
Expected: the new test passes, and `11 failed`. These are the eleven tests that pin a printed `rebaseline` without the flag: `test_a_complete_triage_advances_every_section_and_rebaselines_the_block`, `test_the_first_release_range_settles_the_block_findings`, `test_a_missing_pages_held_sections_are_saved_and_hold_their_groups_blocks`, `test_a_verify_report_lists_corrections_owners_calls_and_the_bookkeeping`, `test_a_discarded_row_outside_the_packet_holds_nothing`, `test_a_block_waits_until_every_candidate_is_resolved`, `test_a_correction_left_for_the_owner_holds_its_section`, `test_a_page_with_an_unresolved_changed_block_is_never_rebaselined`, `test_verify_never_advances_a_section_past_its_triages_target_backwards`, `test_an_audit_ends_with_audited_unless_a_section_is_held` and `test_a_packet_built_on_another_cache_names_it_in_every_command`.

- [ ] **Step 5: Update those expectations.** Each expected `rebaseline` line gains ` --head 2.1.902`. That includes the ranged triages (`:191`, `:1023`, `--through 2.1.901`): the head is the fetch's 2.1.902, never the range's end or `advance_to`. Three lines (`:713`, `:886`, `:1035`) would pass the files' 121-column width, so they are rewrapped first. A replace-all then takes the other seven. The `:856` slice becomes a parse, so it reads the refs and the head as `cli.py` does.

**Replace** in `build/cc_guide/test_settle.py`:

```python
        f"  {CLI} baseline rebaseline alpha 'tools › Tools'", f'  {CLI} baseline advance alpha.reference --to 2.1.902',
        f'  {CLI} baseline stamp']
```

**with:**

```python
        f"  {CLI} baseline rebaseline alpha 'tools › Tools' --head 2.1.902",
        f'  {CLI} baseline advance alpha.reference --to 2.1.902', f'  {CLI} baseline stamp']
```

**Replace** in `build/cc_guide/test_settle.py`:

```python
        f"  {CLI} baseline rebaseline alpha 'tools › Tools'", f'  {CLI} baseline audited alpha --to 2.1.902']
```

**with:**

```python
        f"  {CLI} baseline rebaseline alpha 'tools › Tools' --head 2.1.902",
        f'  {CLI} baseline audited alpha --to 2.1.902']
```

**Replace** in `build/cc_guide/test_settle.py`:

```python
        f"  {named} baseline rebaseline alpha 'tools › Tools'", f'  {named} baseline stamp', f'  {named} lint']
```

**with:**

```python
        f"  {named} baseline rebaseline alpha 'tools › Tools' --head 2.1.902", f'  {named} baseline stamp',
        f'  {named} lint']
```

**Replace all 7** in `build/cc_guide/test_settle.py`:

```python
baseline rebaseline alpha 'tools › Tools'"
```

**with:**

```python
baseline rebaseline alpha 'tools › Tools' --head 2.1.902"
```

**Replace** in `build/cc_guide/test_settle.py`:

```python
        f"  {CLI} baseline rebaseline beta 'events › Events › Retry'"]
```

**with:**

```python
        f"  {CLI} baseline rebaseline beta 'events › Events › Retry' --head 2.1.902"]
```

**Replace** in `build/cc_guide/test_settle.py`:

```python
    assert whole == [f"  {CLI} baseline rebaseline alpha 'tools › Tools' 'tools › Tools › Options › `--fast`'"]
    refs = shlex.split(whole[0])[shlex.split(whole[0]).index('rebaseline') + 2:]
    new, _, _ = baseline.rebaseline(w.state, w.manifest, w.guide, 'alpha', refs, state.latest_docs(world[1]),
                                    '2.1.902')  # baseline refuses a page listed in part
```

**with:**

```python
    assert whole == [f"  {CLI} baseline rebaseline alpha 'tools › Tools' 'tools › Tools › Options › `--fast`'"
                     ' --head 2.1.902']
    words = shlex.split(whole[0])
    args = cli.parser().parse_args(words[words.index('build/cc_guide/cli.py') + 1:])
    new, _, _ = baseline.rebaseline(w.state, w.manifest, w.guide, 'alpha', args.refs, state.latest_docs(world[1]),
                                    args.head)  # baseline refuses a page listed in part
```

- [ ] **Step 6: Run the tests and see them pass.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q test_settle.py`
Expected: no failure.

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: no failure, and +1 on the count before this task.

- [ ] **Step 7: The skill and the docs.** Step 4 of the skill's "Dispatch, save, settle" gains the rule for a refusal (the planning record's DF3: skip it, run the rest, tell the owner, never drop the flag). The cross-group note keeps the flag. `formats.md` names the pin beside `audited --to`, and `build/CLAUDE.md` gains one sentence.

**Replace** in `.claude/skills/cc-guide/SKILL.md`:

```markdown
4. Run the commands settle prints, in the order it prints them and one at a time, never in a parallel batch: each `baseline` command rewrites `build/cc_guide/baseline.json`, so two at once can lose a write.
```

**with:**

```markdown
4. Run the commands settle prints, in the order it prints them and one at a time, never in a parallel batch: each `baseline` command rewrites `build/cc_guide/baseline.json`, so two at once can lose a write. Each `rebaseline` ends with `--head`, the packet's head. When one refuses because the latest fetch is at another release (a session start or another `check` refetched the docs), skip it, run the rest, and tell the owner: the next `check` compares those blocks again. Never drop `--head` to get past the refusal.
```

**Replace** in `.claude/skills/cc-guide/SKILL.md`:

```markdown
leave the block's ref out of its own group's `rebaseline`, with the rest of its page if `rebaseline` then refuses the page.
```

**with:**

```markdown
leave the block's ref out of its own group's `rebaseline`, keeping its `--head`, with the rest of its page if `rebaseline` then refuses the page.
```

**Replace** in `.claude/skills/cc-guide/references/formats.md`:

```markdown
`rebaseline` for the resolved blocks,
```

**with:**

```markdown
`rebaseline <group> <refs> --head <head>` for the resolved blocks (at the packet's `head`, so it refuses once a later fetch has moved `latest/`, rather than baseline docs the verifier never read),
```

**Replace** in `build/CLAUDE.md`:

```markdown
rebaseline the whole page. A missing page needs a `manifest.toml` edit first.
```

**with:**

```markdown
rebaseline the whole page. `settle` prints each `rebaseline` with `--head`
and the packet's head, which refuses once a later `check` (a session start's
`refresh` included) has refetched the docs. A missing page needs a
`manifest.toml` edit first.
```

- [ ] **Step 8: Run the gates and commit.** `check_conformance.py`, which the commit lints run, covers the skill's files.

Run: `bash build/run_commit_lints.sh`
Expected: all eight lints pass.

```bash
git add build/cc_guide/settle.py build/cc_guide/test_settle.py .claude/skills/cc-guide/SKILL.md .claude/skills/cc-guide/references/formats.md build/CLAUDE.md
git commit -m "feat(cc_guide): settle pins each rebaseline to its packet's head"
```

---

### Task 4: Pin that `check` records a new head only after its pages (O3)

**Files:**
- Test: `build/cc_guide/test_check.py`: a new test after `test_a_page_unmapped_by_a_head_move_is_refetched_when_mapped_again` (`:277-296`).
- Mutated in Step 3 only, then restored: `build/cc_guide/check.py:141-142`.

**Interfaces:**
- Consumes: `check.live_docs`, as it is at `e9325de`.
- Produces: a test that fails if `live_docs` ever records a new head before every page is written. Nothing else depends on it.

The test pins behavior `check.py` already has, so it passes at once. Step 3 proves it can fail.

- [ ] **Step 1: Write the test.** A directory at `env-vars.md`, the second mapped page, makes the page loop fail after `tools.md`, the first page, already holds the newer text. That is the mixed state the O3 answer rests on.

**Replace** in `build/cc_guide/test_check.py`:

```python
    assert got.pages['platform:pricing'] == 'Pricing text at head B.\n'


def test_a_corrupt_fetch_record_is_a_setup_error(tmp_path, docs_dir):
```

**with:**

```python
    assert got.pages['platform:pricing'] == 'Pricing text at head B.\n'


def test_a_new_head_is_recorded_only_after_every_page_is_written(tmp_path, docs_dir):
    '''Plan 49's final-review question O3: rebaseline --head trusts
    fetch.json's head to name the pages beside it. So a run that dies while
    writing the pages leaves the older head recorded, though a page already
    holds the newer text, and the next run, seeing the changelog head differ,
    refetches every page.'''
    cache, log = tmp_path / 'cache', []
    check.live_docs(MANIFEST, cache, serving(docs_dir), NOW)
    write_tree(docs_dir, {'changelog.md': DOCS['changelog.md'].replace(
        '<Update label="2.1.902"', '<Update label="2.1.903" description="October 3, 2026">\n</Update>\n'
        '<Update label="2.1.902"'), 'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    blocked = state.latest_docs(cache) / 'env-vars.md'
    blocked.unlink()
    blocked.mkdir()  # the second mapped page: its write fails once tools.md, the first, is written
    with pytest.raises(IsADirectoryError):
        check.live_docs(MANIFEST, cache, serving(docs_dir), NOW)
    assert 'runs alpha batches' in (state.latest_docs(cache) / 'tools.md').read_text()
    assert state.read_fetch(cache)['changelog_head'] == '2.1.902'
    blocked.rmdir()
    check.live_docs(MANIFEST, cache, serving(docs_dir, log), NOW)
    assert len(log) == 2 + len(MANIFEST.pages())
    assert state.read_fetch(cache)['changelog_head'] == '2.1.903'


def test_a_corrupt_fetch_record_is_a_setup_error(tmp_path, docs_dir):
```

- [ ] **Step 2: Run it.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q test_check.py -k new_head_is_recorded`
Expected: `1 passed`.

- [ ] **Step 3: Prove it bites.** Record the head before the pages are fetched, as a mutation, and run the test again.

**Replace** in `build/cc_guide/check.py` (a mutation, restored below):

```python
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(get, todo))
```

**with:**

```python
    fetch_record(cache).write_text(json.dumps({'fetched_at': now.isoformat(timespec='seconds'),
                                               'changelog_head': head}, indent=1) + '\n', encoding='utf-8')
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(get, todo))
```

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q test_check.py -k new_head_is_recorded`
Expected: `1 failed`, an `AssertionError` on `assert state.read_fetch(cache)['changelog_head'] == '2.1.902'`: the record holds `'2.1.903'`.

Run: `git restore build/cc_guide/check.py`

Run: `git status --porcelain`
Expected: only ` M build/cc_guide/test_check.py`.

- [ ] **Step 4: Run the suite.**

Run: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: no failure, and +1 on the count before this task.

- [ ] **Step 5: Run the gates and commit.**

Run: `bash build/run_commit_lints.sh`
Expected: all eight lints pass.

```bash
git add build/cc_guide/test_check.py
git commit -m "test(cc_guide): pin that check records a new head after its pages"
```

---

### Task 5: Validation (Validation 6; offline only)

**Files:** none changed. This task produces the completion report's evidence. It runs no live `check`, `packets`, `settle` or `baseline rebaseline` (Global Constraints).

- [ ] **Step 1: Every existing gate.** Record each outcome against Task 1 Step 1's counts:
  - the cc_guide suite: `uv run --directory build/cc_guide --python 3.13 --with pytest python -m pytest -q`: +3, no failure;
  - the build directory's suite, which collects the cc_guide suite too: `uv run --directory build --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q`: the same +3. Its only failures or skips are the four `test_verify_citations.py` ground-truth tests, which need the gitignored `build/.scratch/`;
  - `bash build/run_commit_lints.sh`: all eight pass;
  - `uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check`: prints nothing, since no adapter changed.
- [ ] **Step 2: Hygiene.**
  - Run `git status --porcelain`: it prints nothing.
  - Run `git log --format=%B -n 4`: each of this plan's commits carries the session's trailer.
  - Run `uv run --python 3.13 python build/cc_guide/cli.py lint`: exit 0, and its `STALE` lines are the same ones `main` prints. It names none of the files this plan changed for a new reason.

---

## Plan completion notes

- **Step 1, the gate.** Leftovers that need the owner go to them in one batch.
- **Step 3, deferred items.** Tick "Pin `baseline rebaseline` to its packet's head" in section `49-claude-code-drift-automation — 2026-10-18` with: `→ done in plan 51: settle prints rebaseline --head <the packet's head>, and rebaseline refuses a fetch at another release, naming both (test_cli.py, test_settle.py); spec R7 and R8.8 state the rule; O3 is settled in plan 51's planning record: two check runs can share latest/, the head-after-pages order is pinned in test_check.py, and a triage's rebaseline during another run's page writes is the accepted residual.` A parallel routing session may append to `specs/deferred_items.md`, so expect a small merge there. Append items only for what execution deferred, plus DF5's item if the owner reverses it.
- **Step 4, triage.** Run `deferred_stats.py` and report its summary line. Bring the triage proposal when the backlog is over its threshold.
- **Step 5, retire.** `git mv` this plan to `specs/plans/completed/`. The spec stays in `specs/`, since Stage 5 (probes) remains. Re-point this plan's relative links, if any, for the new depth.
- **Merge.** The branch edits `.claude/skills/cc-guide/`. The app's sync-with-base refuses merges that touch `.claude/skills` until the pinned origin is confirmed, so plan 49 was merged with a terminal fast-forward instead. The owner merges. Nothing is pushed or merged without the owner's go-ahead.
- **After the merge** (owner, optional): a live trial runs from `main`, with no `/cc-guide` run in flight.
- **Next:** Stage 5 (probes) is the next plan for this spec (D4).

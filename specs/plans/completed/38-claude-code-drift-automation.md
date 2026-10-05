# Claude Code Drift Automation, Stage 1 (Detector) Implementation Plan

**Status: COMPLETE (2026-10-05)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md. Commit hashes in the notes name commits on `feat/cc-drift-stage1`.

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Where this runs.** The owner commits this plan on local `main` after review, which
> leaves `main` ahead of `origin/main`. `EnterWorktree` bases on `origin/main`, which
> would lack it, so create the worktree by hand from the main checkout (Global
> Constraints, "Worktree") and execute there:
> `/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1`,
> branch `feat/cc-drift-stage1`. Every command below `cd`s to that absolute path.

**Goal:** Build Stage 1 of the drift spec, the detector. `build/cc_guide/` gains a stdlib CLI that lints the Claude Code guide against its manifest and baseline, and fetches the Claude Code docs and changelog. It compares hashed docs blocks with the baseline, reports what is due, and carries all of R7's bookkeeping except `cite`. The root CLAUDE.md is first rewritten under 200 lines.

**Architecture:** Eight stdlib modules sit beside `conformance.toml` in `build/cc_guide/`, each importing only the ones before it:
- `blocks.py`: R3's fences, blocks, keys, hashes and selection.
- `docs.py`: release labels, the changelog, `llms.txt` and page names.
- `guide.py`: R1's sections and anchors, R3.6's terms, and R1.2's stamp region.
- `state.py`: the manifest, baseline, `PROBES.md`, the git-or-worktree source and the cache paths.
- `baseline.py`: R7 without `cite`, plus R11.1.
- `lint.py`: R5 without its citation rules.
- `check.py`: R6 without R6.8's citing files, R6.10's `--hook` and R6.11's `packets`.
- `cli.py`: the command line.

Tasks 3–10 build them test-first, one module per task, on hand-written fixtures. Tasks 11–13 are controller tasks with the owner's three gates: the seed manifest, the stamp-region edit and the first live report's block selection.

**Tech Stack:** Python 3.13 through `uv run`, stdlib only (`tomllib`, `json`, `hashlib`, `urllib.request`, `concurrent.futures`, `argparse`, `subprocess` for git); pytest; git. There is no CI. The gates are the lints and suites named in each task.

**Spec:** `specs/claude-code-drift-automation.md` (DESIGN APPROVED 2026-10-03). Task 1 writes the owner's 2026-10-04 amendments into it. R-numbers, "Sequencing item N" and "Validation item N" point into it. The base is `main` at `f72822a`, which equals `7137e5e` plus the sibling spec `specs/handoff-briefs.md`.

## Global Constraints

Every task's requirements implicitly include this section.

- **Scope (Sequencing item 1, as Task 1 amends it).** In scope:
  - R1, R2 and R3;
  - R5 apart from its citation rules and `STALE` lines;
  - R6 apart from R6.8's citing-file lists, R6.10's `--hook` and R6.11's `packets`;
  - R7 apart from `cite`;
  - R11.1, R11.2 and R11.4;
  - R12.1–R12.2 for these, R12.3's row fixture, R12.4's "`lint` passes on the repo", and R12.7's documentation;
  - the root CLAUDE.md rewrite.

  Not in this stage: R4, citations and `cite` (Stage 2); `packets`, `quotes`, the skill and the verifier (Stage 3); `--hook` and the notice (Stage 4); `probes` and `binaries` (Stage 5).
- **Order.** Task 1 (spec amendments), then Task 2 (the CLAUDE.md rewrite), then Tasks 3–10 (the modules), Task 11 (seed manifest, owner gate), Task 12 (stamp region and seed baseline, owner gate), Task 13 (first runs, owner gate), Task 14 (documentation) and Task 15 (validation). Each module task's tests run with every earlier module in place.
- **Worktree.** Before creating it, run `git -C /Users/lowell/Projects/agent-skills log --oneline -3 main` and confirm `main` holds this plan's commit. Create it from the main checkout with `git -C /Users/lowell/Projects/agent-skills worktree add .claude/worktrees/plan-38-cc-drift-stage1 -b feat/cc-drift-stage1 main`, never with `EnterWorktree`. `.claude/worktrees/` is gitignored. Commit only from the worktree.
  - Every commit command begins with `[ "$(git branch --show-current)" = feat/cc-drift-stage1 ] &&`, so a wrong branch or a detached HEAD stops the chain with exit 1 before anything is staged. Concurrent sessions switch the shared checkout. Keep the single `=`; zsh rejects `==` there.
  - Scratch files live under the worktree's gitignored `.sdd/38-claude-code-drift-automation/` and are never committed. Deviations go in the SDD ledger there as they happen, and reach this plan as `> Deviation:` notes only at the completion markup (writing-plans' step 2): a mid-run plan edit would leave the tree dirty for Task 15's hygiene check and the final review.
  - Each commit ends with the executing session's own Co-Authored-By trailer, which subagent-authored commits keep too. The `Claude Opus 5.5` trailer in the commit blocks below is written for an Opus session; a session on another model substitutes its own.
- **Baseline and counts.** Before Task 1, run the build suite in the worktree and record its counts in the SDD ledger (`progress.md` in the workspace):
  `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q -rf`
  - A worktree lacks the gitignored `build/.scratch/`, so four tests in `test_verify_citations.py` fail there and stay failing throughout: `test_true_negative_flags_bad_refs`, `test_empty_text_has_no_failures`, `test_chapter_fallback_passes_gate_a_but_is_flagged` and `test_known_good_fallback_is_not_flagged`. They are not this plan's to fix.
  - Every expected change below is a **+N delta over that baseline**. This plan adds **+136 tests**, all in `build/cc_guide/`: +135 in Tasks 3–10 and +1 in Task 12.
  - `cd build && pytest` collects `build/cc_guide/` too (R12.1), so the build-directory count rises by the same +136. Nothing else changes, because Task 2 edits no test.
  - The `N passed` outcomes quoted for `build/cc_guide/` run alone are exact, because this plan creates that suite. Outcomes for the build directory are always deltas over the baseline.
- **Test-first (R12.1).** Tasks 3–10 each write their tests and a docstring-only stub of the module, run the new test file, and reconcile the run against the step's prediction before writing code: the counts, and each failure's cause.
  - Every predicted failure is an `AttributeError` naming the stubbed module, with two exceptions. Four of Task 5's are `ImportError: cannot import name 'STAMP_CLOSE' from 'guide'`, raised inside the fixture `guide_text`. Ten of Task 10's are ERRORs at fixture setup, from `monkeypatch.setattr(cli, 'REPO', …)`.
  - The predictions were observed by replaying Tasks 3–12 in a fresh clone of `main` while this plan was written.
  - A test that passes at its RED step is a plan defect: fix the assertion so it fails for the stated reason, and report the deviation.
- **Test conventions (R12.1).** Run the suite from inside `build/cc_guide/`: `uv run --python 3.13 --with pytest python -m pytest -q`. It is stdlib only, so it needs no other `--with`.
  - Tests use bare imports and there is no `__init__.py`. Test files import modules by name (`import blocks`) and reach names through them, so a missing name fails one test, never collection.
  - Module and test basenames stay unique across `build/`, and no module imports from `build/`, so the suite runs from either directory.
  - Fixtures live in `build/cc_guide/cc_fixtures.py`, hand-written and never copied from docs text; each task appends its own.
  - Every test file imports `isolated_home` from `cc_fixtures` (with `# noqa: F401`). That registers the autouse fixture pointing `HOME` at `tmp_path`, so no test reads or writes the real `~/.cache`.
  - Fixture git repos go through `cc_fixtures.git`, which strips the caller's `GIT_` variables.
  - Messages and findings are compared with exact equality.
- **Python style** (`CLAUDE.md`, `rules/clean-code-python.md`). Single quotes, with double quotes only around a string that itself contains single quotes. 4-space indent. `'''` docstrings. Stdlib only, Python 3.13.
- **CLI contract (Layout, R5, R6.9).** The CLI runs as `uv run --python 3.13 python build/cc_guide/cli.py <subcommand>` and finds the repo from its own location (`REPO = Path(__file__).resolve().parents[2]`), never from the working directory. Exit codes:
  - 0 means clean (`lint`) or nothing due (`check`);
  - 1 means violations (`lint`) or something due (`check`);
  - 2 means an error. A `SetupError` prints `cc-guide: <message>` on stderr; any other exception prints its traceback. Either way the exit is 2, so a crash never reads as 0 or 1.
- **Inputs (R6.1).** By default `check` reads the guide, `manifest.toml`, `baseline.json` and `PROBES.md` from `main`'s commit through `git show`; `--ref <ref>` or `--worktree` overrides that, and `--docs <dir>` runs offline. Until this plan merges, `main` holds no manifest or baseline, so **every `check` this plan runs passes `--worktree`**. A test pins that the default reads `main`. `lint` reads the working tree unless given `--ref`. The `baseline` subcommands always read and write the working tree.
- **Writes (R6.10, R7).** `check` writes only under the cache: `latest/docs/`, `latest/fetch.json` and `reports/<baseline-sha12>.json`. `baseline` writes:
  - `baseline.json` (`init`, `accept`, `advance`, `audited`, `rebaseline`);
  - the guide's stamp region (`stamp` alone);
  - `<release>/docs/` snapshots in the cache (`rebaseline`, never into `2.1.288/`).

  Nothing commits, and every write set is tested.
- **Cache.** `~/.cache/agent-skills/cc-guide/`, never inside a checkout. `2.1.288/` is the bootstrap snapshot and is never written. The global `--cache DIR` option overrides the location, for tests and dry runs.
- **Never commit docs text** (spec, Constraints and Provenance). The snapshot at `~/.cache/agent-skills/cc-guide/2.1.288/` is Anthropic's docs text: read it, never copy it into the repo. `baseline.json` holds hashes and block keys. Keys are heading paths and table first cells, with each component capped at 60 characters (`blocks.KEY_PART_MAX`; decision 9 below).
- **No citation-shaped lines.** No line of a file under `build/cc_guide/` begins, after indentation, with `# cc-guide:` or `<!-- cc-guide:`; Stage 2's lint scans for them (R5). The stamp markers live inside string constants in `guide.py`. R4.2 excludes `specs/` from that scan, so the guide's own stamp markers and this plan are outside it.
- **Exact commands.** From Task 2 on, every step states its exact command with an absolute `cd`. None says "see CLAUDE.md".
- **Nothing outward-facing.** No push, PR, issue or post. The only network use is `check`'s live fetch from code.claude.com and platform.claude.com (Task 13), as R6.4 designs it, with a User-Agent that carries no personal data.
- **Coordination.** `specs/handoff-briefs.md` (`f72822a`) plans edits to two root CLAUDE.md lines: its R6.2 changes the originals bullet and the writing-plans suite comment. It also expects this plan to hold ID 38. Whichever plan merges second rebases onto the other and rechecks the 200-line limit with `check_conformance.py`. Task 2's audit accepts any `(N originals` count for that reason.
- **Leave alone:**
  - the spec's status line, and its "Nothing outside `specs/` references the guide" baseline row (a dated 2026-10-03 measurement);
  - the text listed under "Text this plan makes stale", which the owner settles;
  - `build/check_snippets.py` and `build/test_check_snippets.py`. Their pointers into CLAUDE.md (`:31`, `:138`) stay valid, because Task 2 moves no invocation.
- **Anchor on text, not line numbers.** Line numbers are as of `f72822a`, for orientation only. Every edit gives its exact old text. Never regress an existing test: everything green at the baseline stays green at every commit.

---

## Planning record

### Docs-format pre-check (2026-10-04)

Fetched at 2026-10-04T20:17Z into `~/.cache/agent-skills/cc-guide/precheck-2026-10-04/`, outside the repo, before the parsers were specified:

- **`changelog.md`** (`https://code.claude.com/docs/en/changelog.md`): HTTP 200, 942,220 bytes.
  - 411 `<Update label="X" description="Month D, YYYY">` blocks, with head 2.1.289 (October 3, 2026). Every label is numeric, unique and strictly descending, and there are 411 `</Update>` closers.
  - 6,970 bullets, every one written `  * ` (indented two spaces). No other line sits inside a block.
- **`llms.txt`** (`https://code.claude.com/docs/llms.txt`; `/docs/en/llms.txt` is a 404): HTTP 200, 52,888 bytes, listing 220 code.claude.com pages.
  - All 34 mapped code pages are listed, live and in the snapshot, and all 39 mapped pages are in the 2.1.288 snapshot.
  - No platform page is listed. The slug set is unchanged since the snapshot.
- **Platform pages** are fetched as `https://platform.claude.com/docs/en/<slug>.md`, the form the refresh used.

So R6.5's and R6.6's formats hold as specified. `docs.py` accepts any bullet indentation (`^\s*\* `), so the unindented form also parses.

### Plan ID

38 was confirmed free on 2026-10-04. `git ls-tree -r --name-only <ref> -- specs/plans`, run for every ref that `git for-each-ref --format='%(refname:short)' refs/heads refs/remotes` lists (`main`, `origin/main`), finds no `38-*` plan. The highest ID is 37. The sibling spec `specs/handoff-briefs.md` (`f72822a`) also expects 38 to be this plan's.

### Decisions settled in this plan (the owner reviews each)

1. **Stamp after bookkeeping** (owner decision 1). `advance` and `audited` do not restamp. The documented flow is "then `stamp`", as R8.8 orders it.
   - Either subcommand prints `the stamp region is now stale: run baseline stamp` on stderr when it moved the stamp's dates, and `lint` prints the exact `baseline stamp` command.
   - This keeps one writer per artifact: `stamp` alone writes the guide. One `stamp` also follows a batch of `advance` calls.
2. **Dates** (owner decision 1). `checked.date` and `audited.date` record the day the check or audit was done, never the release's ship date.
   - The bootstrap's 2026-10-03 is the refresh's check day; 2.1.288 itself shipped on 2026-10-02.
   - The stamp therefore reads "through 2.1.288 on 2026-10-03", where R1.2's example reads "(2026-10-03)". Task 1 Step 7 records both points in the spec.
3. **A missing page** (owner decision 1) is one page-level finding, never one finding per block. `rebaseline` keeps its baselined entries and prints a note.
   - Clearing it needs a `manifest.toml` edit that drops or remaps the page. The finding then disappears, and the dropped page's old blocks show as deselected, for information only.
   - The group's next full `rebaseline` removes those blocks.
4. **The manual flow** (owner decision 1) is documented in `cli.py`'s docstring and `build/CLAUDE.md`. Its order is `accept`, `rebaseline`, `advance` or `audited`, then `stamp`, then `lint` and `check_conformance.py`. A manual correction that resolves a conformance gap removes its `[[exception]]` in the same change (conformance R6 D5).
   - This plan does not run the bookkeeping on the real baseline. Triaging the backlog since 2.1.288 is Stage 3's first job, or the owner's own manual review.
   - A fixture test shows that the flow alone brings `check` to exit 0.
5. **`check --hook` (R6.10) moves to Stage 4, and `packets` (R6.11) to Stage 3.** `--hook` writes R9's notice, and packet formats live in R8. Task 1 records the deviation in Sequencing items 3 and 4. The Layout's `quotes`, `probes` and `binaries` are not Stage 1's.
6. **Probes.** The registry stays empty until Stage 5 (R2.2), so no probe can be due.
   - An absent `PROBES.md` reads as "no rows", never exit 2.
   - R12.2 asks for every due rule, so the probe rules are built and tested now against fixture registries.
   - `PROBES.md` columns are read by header name (`date`, `version`, `probe`, `outcome`), which constrains Stage 5's table to those headers.
7. **The stamp region** (R1.2) is three block-level lines: the open marker, one generated `>` line, and the close marker. The July history and the "Claude Code changes quickly" sentence move into a second `>` paragraph outside the markers.
   - "58 releases earlier" becomes "58 releases before the full re-verification at 2.1.288", which stays true at every restamp.
   - Task 12 shows the exact text (an owner gate).
8. **Fences.** `blocks.py` reimplements `build/fences.py`'s closing rule (R12.1 bars importing `build/`), adding tilde fences and indented openers. `guide.py` splits sections with the same rule.
   - A real-guide test pins the result: the guide splits into R1.1's 38 IDs, in order.
9. **Block keys are capped at 60 characters per component** (`KEY_PART_MAX`, R3.6's term cap). R3.3 and R3.4 key a block by its heading path, and a row by its table's first cell, and `baseline.json` is committed.
   - Uncapped, 46 keys in the 2.1.288 snapshot ran past 80 characters, the longest 274. Capped, 60 keys carry a shortened component, ending in `…`, and the longest whole key is 210.
   - **Provenance flag:** the spec's Provenance section says the repo commits "hashes, slugs, release labels, terms and probe outcomes", but R2.3 stores page → key → hash. The committed baseline therefore holds docs headings and first cells, each at most 60 characters: 3,417 keys.
   - The alternative, hashed keys, would make reports name blocks unreadably. The owner decides.
10. **Platform front matter** (the `---` block at the top of a platform page) stays in the `(intro)` block. A change to its title or URL reads as a changed intro.
11. **Terms.** Code spans are paired per line the way CommonMark pairs backtick runs, which R3.6's "pair first, filter by length after" asks for.
    - `STOP_TERMS` is a 22-entry constant in `guide.py`: R3.6's four examples, plus each single lowercase word or bare extension that appeared in at least 5% of the blocks on the snapshot's `terms` pages.
    - Per-section tuning stays in the manifest's `extra_terms` and `exclude_terms`.
12. **Tables.** A table starts at a `|` line followed by a separator row, and its header and separator stay in the heading's block. A row's key is its first cell, split on unescaped pipes only; an empty first cell keys as `(row)`.
13. **Every `rebaseline` refreshes the baseline's `llms` list** from `latest/llms.txt` (R2.3: "the `llms.txt` slug list from the last baseline").
14. **Rebaseline refs** are `<page>` (all its selected blocks) or `<page> › <key>` (one block), exactly as `check` prints a finding. R7 says `[<block keys>]`; the page prefix disambiguates, because one key can recur across pages.
15. **Tuning re-inits.** After the owner tunes the marks (Task 13), `baseline init --force` rebuilds from the 2.1.288 snapshot, and the round trip runs again. A `rebaseline` here would absorb post-2.1.288 docs edits (R2.6).
16. **Options beyond the spec:**
    - a global `--cache DIR`;
    - `init --docs DIR --release LABEL --date YYYY-MM-DD`, defaulting to the 2.1.288 snapshot, `2.1.288` and `2026-10-03`;
    - `init --force`. `init` refuses to overwrite an existing `baseline.json` without it.
17. **Two helper modules beyond the Layout's list:** `docs.py` (the changelog, `llms.txt` and page names) and `state.py` (the manifest, baseline, `PROBES.md`, sources and cache paths), so each module keeps one job.
18. **The seed `baseline.json` is about 390 KB:** 4,308 lines and 3,417 blocks over 57 page-group pairs. By group: overview 496, skills 422, subagents 546, rules 524, hooks 796, models 633. It is committed, as R2.3 requires.
19. **`accept` passes no citer stamps in Stage 1.** There are no citations yet, so `--substantive` sets `changed` to the newest cached release. Stage 2 wires the citation index's stamps into the same function.
20. **An invalid manifest or baseline makes `lint` exit 2**, as it does for `check` (R6.9). R5 names only 0 and 1.
21. **Deferred item "`fixture=<name>` in CLAUDE.md's snippet notes"** (`specs/deferred_items.md`, plan 33's section). Task 2's pointer names `fixture=<name>` and says where it is documented. Whether that closes the item is the owner's call at plan completion.

### CLAUDE.md line budget

The `claude-md-size` check flags 200 lines, so 199 is the most CLAUDE.md can hold.

| Point | Lines |
|---|---|
| `f72822a` (as at `7137e5e`) | 224 |
| After Task 2's rewrite | 170 |
| After Task 14's Stage 1 additions (+6: a comment pair, three commands, one blank line) | 176 |
| Reserve: drift Stages 2–5 (citation and `cite` notes, `packets` and `quotes`, the notice, `probes`) | about +10 |
| Reserve: portability R1.9 (the `--strict` invocation) and R4.4 (the provenance invariant) | about +4 |
| Projected after both specs | about 190 |

**Proposed target:** Stage 1 ends at 176 or fewer. Each later stage states its own lines as a +N delta and stays at 190 or fewer, which keeps 9 lines of slack. The handoff-briefs plan edits two lines in place (its R6.2) and adds none.

### Text this plan makes stale (listed for the owner, not edited)

From `git grep -n 'CLAUDE.md' -- specs ':!specs/completed' ':!specs/plans/completed'`, plus the follow-on references:

- `specs/agent-skills-portability.md`:
  - lines 145–147 (R1.9) and 315–316 (R4.4) say "within the CLAUDE.md ceiling". No ceiling remains: the limit is the check's 200 lines.
  - lines 349–351, the "Conformance register" constraint (its P1), still says to "raise the ceiling in the register on purpose". There is nothing left to raise.
  - line 362 says to "update CLAUDE.md's per-suite counts by the same deltas". No per-suite counts remain.
- `specs/deferred_items.md`:
  - "Bring the root CLAUDE.md under 200 lines" (~1779) is closed by this plan and ticked at completion.
  - the conformance-tests item ending "and CLAUDE.md's counts are updated in the same change" (~1929) has no counts left to update.
  - the `claude-md-count-claims` check (~2100) says "Today 22 hits". The count is now 0 apart from the provenance-pinned "(N originals" note, so the check would only guard against regressions.
  - the `claude-md-import-resolves` check (~2093) cites `CLAUDE.md:122`, a line number the rewrite moves.
  - the `fixture=<name>` item (~1741), per decision 21.
- `specs/claude-code-drift-automation.md`'s status paragraph, "nothing else has been implemented", goes stale when this plan merges. The owner's instruction keeps the status line untouched.
- `build/test_check_snippets.py:135`'s comment cites CLAUDE.md's "non-ArviZ subset passes" line. That line was already gone before this plan.
- The dated audit records (`specs/audit-3-10-26.md`, `specs/claude-code-conformance-audit-2026-10-04.md`) quote old CLAUDE.md lines and counts. They are historical and stay as written.

> Settled at the completion gate (owner, 2026-10-05), in 6127580: the
> agent-skills-portability.md entries, the three deferred-item clauses and
> handoff-briefs.md:557's line pointers were fixed; the drift spec's status line,
> `build/test_check_snippets.py:135` and the dated audits were left. The CLAUDE.md
> item was ticked, and the `fixture=<name>` item was fixed and ticked (decision 21).

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `specs/claude-code-drift-automation.md` | The owner's 2026-10-04 amendments, each tagged `(owner, plan 38, 2026-10-04)`. | 1 |
| `CLAUDE.md` | The rewrite: counts out, comments condensed in place, every command unchanged (2). Stage 1's commands (14). | 2, 14 |
| `build/CLAUDE.md` | An accurate opening (2), and a `cc_guide/` paragraph with the manual flow (14). | 2, 14 |
| `build/cc_guide/conformance.toml` | Loses exceptions `claude-md-size` and `claude-md-fast-changing-details`. | 2 |
| `build/cc_guide/cc_fixtures.py` | New. Hand-written fixtures; each module task appends its own. | 3–10 |
| `build/cc_guide/blocks.py` + `test_blocks.py` | New. R3: fences, page blocks, keys, normalization, hashing, selection, candidates. | 3 |
| `build/cc_guide/docs.py` + `test_docs.py` | New. Release labels and their order, the changelog, `llms.txt`, page files and URLs. | 4 |
| `build/cc_guide/guide.py` + `test_guide.py` | New. R1's sections and anchors, `text_hash`, R3.6's terms, R1.2's stamp region. | 5 |
| `build/cc_guide/state.py` + `test_state.py` | New. The manifest and baseline (validated), `PROBES.md`, the git-or-worktree source, group terms, cache paths. | 6 |
| `build/cc_guide/baseline.py` + `test_baseline.py` | New. R2.4's stamp rule, R11.1's derivation, and `init`, `accept`, `advance`, `audited`, `rebaseline` and `stamp`. | 7 |
| `build/cc_guide/lint.py` + `test_lint.py` | New. R5 without its citation rules. | 8 |
| `build/cc_guide/check.py` + `test_check.py` | New. R6: fetch gate, compare, changelog, due rules, report, exit codes. | 9 |
| `build/cc_guide/cli.py` + `test_cli.py` | New. The command line. Its tests cover each subcommand's write set and the bookkeeping end to end (10), and the repo lint (12). | 10, 12 |
| `build/cc_guide/manifest.toml` | New. The seed configuration (R2.2, R2.5, R11.2). Edited by hand only. | 11 |
| `build/cc_guide/baseline.json` | New. Written by `baseline init` from the 2.1.288 snapshot (R2.6). | 12 |
| `specs/guides/claude-code-customization-guide.md` | The header's first sentence becomes the stamp region (R1.2). No other edit. | 12 |
| `specs/deferred_items.md` | Ticks and this plan's deferred items. **Completion protocol only.** | — |

---

### Task 1: Amend the drift spec with the owner's decisions (2026-10-04)

**Files:**
- Modify: `specs/claude-code-drift-automation.md` (Sequencing items 1, 3 and 4; R12.7; Validation items 1 and 6; and, unless the owner drops Step 7 at plan review, R1.2, R2.3 and R7)

**Interfaces:**
- Consumes: nothing.
- Produces: the amended scope every later task builds to.

The owner approves this wording at plan review. Apply each block exactly, and tag nothing else. The status line and the "Nothing outside `specs/` references the guide" baseline row stay untouched.

- [x] **Step 1: Sequencing item 1 gains the bookkeeping, the CLAUDE.md rewrite and the two deferrals.** In `specs/claude-code-drift-automation.md`, replace

```markdown
1. **Detector.** R1, R2, R3, R5 apart from its citation rules, R6 apart from
   R6.8's citing-file lists, and `baseline init`, `stamp` and `accept`, with
   their tests. Usable through `uv run` as soon as it lands. R1.1's anchors
   are already in the guide, so Stage 1 adopts them (conformance R6 D1).
```

with

```markdown
1. **Detector.** R1, R2, R3, R5 apart from its citation rules, R6 apart from
   R6.8's citing-file lists, R6.10's `--hook` and R6.11's `packets`, and every
   `baseline` subcommand but `cite`: `init`, `rebaseline`, `advance`,
   `audited`, `accept` and `stamp`, with their tests. Usable through `uv run`
   as soon as it lands. R1.1's anchors are already in the guide, so Stage 1
   adopts them (conformance R6 D1). Until Stage 3's verifier exists, the owner
   runs `rebaseline`, `advance` and `audited` by hand after a manual review,
   in R8.8's order, so Stage 1's `check` can reach exit 0 on its own. Stage 1
   opens by rewriting the root CLAUDE.md under the `claude-md-size` check's
   200-line limit, removing the register's `claude-md-size` and
   `claude-md-fast-changing-details` exceptions in the same change
   (owner, plan 38, 2026-10-04).
```

- [x] **Step 2: Sequencing item 3 loses "the rest of R7" and takes `packets`.** Replace

```markdown
3. **Act.** R8 apart from `/cc-guide probes`, the rest of R7, `quotes`, and
   R11.5. Its first jobs are triaging the backlog since 2.1.288 and the first
   `files` batch.
```

with

```markdown
3. **Act.** R8 apart from `/cc-guide probes`, R6.11's `packets`, `quotes`,
   and R11.5. Stage 1 carries R7 but `cite`, which Stage 2 adds, and
   `packets` moved here because its formats live in R8
   (owner, plan 38, 2026-10-04). Its first jobs are triaging the backlog
   since 2.1.288 and the first `files` batch.
```

- [x] **Step 3: Sequencing item 4 takes `check --hook`.** Replace

```markdown
4. **Notice.** R9 and R12.5. It comes after Stage 3, so the notice points at a
   skill that exists.
```

with

```markdown
4. **Notice.** R9, R6.10's `check --hook`, which writes R9's notice, and
   R12.5 (owner, plan 38, 2026-10-04). It comes after Stage 3, so the notice
   points at a skill that exists.
```

- [x] **Step 4: R12.7's first and third bullets.** Replace

```markdown
- CLAUDE.md's Commands section gains the suite's command and test count, and
  the build-directory count rises with it (both stated as +N deltas in
  plans), plus the `lint`, `check` and `probes` invocations.
```

with

```markdown
- CLAUDE.md's Commands section gains the suite's command and the `lint`,
  `check` and `probes` invocations, with no test count. Plans state the
  suite's count, and the build directory's, as +N deltas
  (owner, plan 38, 2026-10-04).
```

and replace

```markdown
- The CLAUDE.md lines a stage adds stay within the `claude-md-size` ceiling in
  `build/cc_guide/conformance.toml`: the stage trims CLAUDE.md elsewhere, or
  raises the ceiling in the register on purpose, with a reason
  (conformance R6 D4).
```

with

```markdown
- The CLAUDE.md lines a stage adds stay under the `claude-md-size` check's
  200-line limit; when they would not, the stage trims CLAUDE.md elsewhere.
  Stage 1's rewrite removed the `claude-md-size` exception, so no ceiling
  remains to raise (owner, plan 38, 2026-10-04; replaces conformance R6 D4's
  ceiling rule).
```

- [x] **Step 5: Validation item 1 states what the new bookkeeping and the rewrite must show.** Replace

```markdown
   - The row fixture (R12.3) passes, and the lint passes on the converted
     guide.
2. **Stage 2.**
```

with

```markdown
   - The row fixture (R12.3) passes, and the lint passes on the converted
     guide.
   - The bookkeeping clears what it resolves: a fixture run with a changed
     block, untriaged releases and a due audit reaches exit 0 under
     `check --worktree` after `rebaseline`, `advance`, `audited` and `stamp`,
     run in R8.8's order. Each subcommand's write set is tested, and none
     commits (owner, plan 38, 2026-10-04).
   - The root CLAUDE.md is under 200 lines, the register's `claude-md-size`
     and `claude-md-fast-changing-details` exceptions are gone,
     `check_conformance.py` passes, and no test count remains in CLAUDE.md or
     `build/CLAUDE.md` (owner, plan 38, 2026-10-04).
2. **Stage 2.**
```

- [x] **Step 6: Validation item 6 gains `check_conformance.py`.** Replace

```markdown
6. **Every existing gate passes:** `check_frontmatter.py`,
   `check_provenance.py`, `check_snippets.py skills/` (Tier 1), the
   dependency-drift test, the `build/` suite, and `sync_runtime_assets.py
   --check` with no adapter change.
```

with

```markdown
6. **Every existing gate passes:** `check_frontmatter.py`,
   `check_provenance.py`, `check_snippets.py skills/` (Tier 1), the
   dependency-drift test, the `build/` suite, `sync_runtime_assets.py
   --check` with no adapter change, and `check_conformance.py`
   (owner, plan 38, 2026-10-04).
```

- [x] **Step 7 (the owner may drop it at plan review): what the dates mean, and the manual flow, in R1.2, R2.3 and R7.** In R1.2, replace

```markdown
oldest `audited`, for example: "Checked against the Claude Code docs and
changelog through 2.1.288 (2026-10-03); oldest full re-verification
2026-10-03, at 2.1.288." Everything outside the markers stays owner prose,
```

with

```markdown
oldest `audited`, for example: "Checked against the Claude Code docs and
changelog through 2.1.288 on 2026-10-03; oldest full re-verification
2026-10-03, at 2.1.288." Both dates are the days the check and the audit were
done (R2.3), so the example reads "on" (owner, plan 38, 2026-10-04).
Everything outside the markers stays owner prose,
```

In R2.3, replace

```markdown
  (release and date of the last audit of its group); `text_hash` (`sha256:` of
  its normalized text, anchor line excluded, whitespace collapsed);
```

with

```markdown
  (release and date of the last audit of its group); `text_hash` (`sha256:` of
  its normalized text, anchor line excluded, whitespace collapsed). Each date
  is the day the check or audit was done, not the release's ship date: the
  bootstrap's 2026-10-03 is the refresh's day, and 2.1.288 shipped on
  2026-10-02 (owner, plan 38, 2026-10-04);
```

In R7, replace

```markdown
The only writer of `baseline.json`, the guide's stamp region, and citation
stamps. Every subcommand leaves its changes uncommitted.
```

with

```markdown
The only writer of `baseline.json`, the guide's stamp region, and citation
stamps. Every subcommand leaves its changes uncommitted. `advance` and
`audited` can move the oldest `checked` or `audited`, which the stamp region
names, so `stamp` follows them, as R8.8 orders it; a stale region is a lint
failure. A missing page (R6.5) clears only through a `manifest.toml` edit
that drops or remaps it, since `rebaseline` keeps a missing page's entries
(owner, plan 38, 2026-10-04).
```

- [x] **Step 8: Check the edit.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && git diff --stat -- specs/ && grep -c '(owner, plan 38, 2026-10-04' specs/claude-code-drift-automation.md && git diff -U0 -- specs/claude-code-drift-automation.md | grep -c '^-\*\*Status'`
Expected: one file changed, `specs/claude-code-drift-automation.md`. The tag count is `11` with Step 7 (`8` without it). The last count is `0`, because the status line did not change.

- [x] **Step 9: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && [ "$(git branch --show-current)" = feat/cc-drift-stage1 ] && git add specs/claude-code-drift-automation.md && git commit -m "docs(specs): amend drift Stage 1 with the owner's 2026-10-04 decisions

Stage 1 takes every baseline subcommand but cite, so its check can reach
exit 0 on the owner's manual bookkeeping, and opens with the root
CLAUDE.md rewrite. check --hook moves to Stage 4 and packets to Stage 3.
R12.7 drops CLAUDE.md's test counts and the register ceiling; Validation
1 and 6 gain the matching checks.

Plan 38, Task 1.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Rewrite the root CLAUDE.md under 200 lines (owner decision 2)

**Files:**
- Modify: `CLAUDE.md` (the runtime-adapter paragraph, the Build tooling paragraph, and the Commands section)
- Modify: `build/CLAUDE.md` (its opening, and the runtime-assets paragraph)
- Modify: `build/cc_guide/conformance.toml` (remove exceptions `claude-md-size` and `claude-md-fast-changing-details`)
- Scratch: `.sdd/38-claude-code-drift-automation/claude_md_audit.py` (never committed)

**Interfaces:**
- Consumes: Task 1's R12.7 amendment.
- Produces: a 170-line CLAUDE.md that Task 14 extends by 6 lines, and a register with no CLAUDE.md exception, so `claude-md-size` holds CLAUDE.md to its 200-line limit from here on.

This closes the deferred item "Bring the root CLAUDE.md under 200 lines" (plan 35 audit rows L-01 and C-02 to C-05). The completion protocol ticks it. The rewrite does three things:
- removes every hand-kept count (C-02);
- replaces the snippet-marker rules restated from `build/check_snippets.py` with a pointer to its docstring (C-03);
- corrects the "citation pipeline" description of `build/` in both files (C-04, C-05).

It changes no command. Every line inside a bash fence that is not a comment stays byte-identical once `\` continuations are joined, and the audit below checks that.

**Nothing moves out of the root CLAUDE.md.** The register's deviation `claude-md-serves-codex-gemini` keeps the Python-style line and the Commands block there, because Codex (through `AGENTS.md`) and Gemini (through `GEMINI.md`) read only the root file. The rewrite condenses them in place. What it drops, and what that costs Codex and Gemini:

| Dropped from CLAUDE.md | Where it still lives | Cost to Codex and Gemini |
|---|---|---|
| Every test, pass and skip count (C-02) | each suite's pytest summary line | none: a run prints them |
| The snippet gate's marker rules, its exit-code legend, the Tier 2 anecdote, and Tier 3's block counts (C-03) | `build/check_snippets.py`'s docstring, which the new comment names, with `fixture=<name>` | they open that docstring to learn the marker rules |
| Per-suite lists of what each suite covers (for example "parser, age buckets, bad/future dates, --json") | the test files | they read the tests to learn coverage |
| "Most of `build/` is the citation-verification pipeline" (C-04) | replaced by an accurate sentence | none |

The `build/CLAUDE.md` fix (C-05) costs them nothing, because neither runtime reads that file.

Kept in condensed form, as the owner directed:
- which `--with` deps unlock a suite's skips: the ArviZ stack for the build suite, scikit-learn and optuna for tune-hyperparameters, matplotlib for bayesian-workflow;
- `CALIBRATION_SWEEP=1`, with its seeds and runtime;
- that a fresh clone or worktree lacks `build/.scratch/`, so `test_verify_citations.py`'s ground-truth tests fail there;
- the llm-wiki pilot path;
- the guard's two runs and its 3.9 floor.

The "- **Lowell's originals**" bullet is not touched. `build/check_provenance.py` reads its backticked list, and `build/test_check_provenance.py` reads its "(19 originals" note.

- [x] **Step 1: Confirm the base.** The text below was written against `f72822a`.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && git diff --stat f72822a HEAD -- CLAUDE.md build/CLAUDE.md build/cc_guide/conformance.toml`
Expected: no output. If any of the three files changed, carry each change into Steps 3–5 without adding a count, and report the deviation. The handoff-briefs plan's R6.2 is the likely source.

- [x] **Step 2: Write the audit, and run it before editing.** Create `.sdd/38-claude-code-drift-automation/claude_md_audit.py` with exactly this content:

```python
'''CLAUDE.md rewrite audit (plan 38, Task 2). Scratch: never committed.

Run from the worktree root: python claude_md_audit.py [BASE | --counts-only]
(BASE defaults to HEAD; --counts-only runs check 3 alone). Exit 0 when
1. every command line in CLAUDE.md's bash blocks, with backslash
   continuations joined and whitespace collapsed, is identical to BASE's, in
   order (only comments and prose change);
2. the "Lowell's originals" bullet is byte-identical to BASE's;
3. no hand-kept count is left: every numeral outside a command line, in
   CLAUDE.md and build/CLAUDE.md, is one of ALLOWED's non-count uses.
'''
import difflib
import re
import subprocess
import sys
from pathlib import Path

FILES = ('CLAUDE.md', 'build/CLAUDE.md')
# Each numeral the rewrite keeps, and why it is not a count to maintain.
ALLOWED = [
    r'\(\d+ originals',            # read by build/test_check_provenance.py
    r'© 2025 Jesse Vincent',        # copyright line
    r'the 13 process skills',      # the fixed superpowers set (provenance)
    r'catalog \(2008\)',           # Clean Code's year
    r'Python 3\.13',               # the pinned interpreter
    r'\+1\)',                      # the plan-id rule
    r'arviz>=1\.0',                # a dependency floor
    r'~20–50 s',                   # a runtime, not a count
    r'CALIBRATION_SWEEP=1',        # an environment switch
    r'seeds 0-99, about 1\.5 min', # the sweep's seeds and runtime
    r'3\.9',                       # the guard's interpreter floor
    r'python3',                    # an interpreter name
    r'Tiers? [123](?: and [23])?', # snippet-gate tier names
    r'~30s',                       # a runtime
    r'32-jax-cpu',                 # a file name
    r'exit [0-2]',                 # an exit code
    r'PML1 §10\.4', r'book1',      # build/CLAUDE.md's citation examples
]
ALLOWED_RE = re.compile('|'.join(ALLOWED))


def at(base, path):
    return subprocess.run(['git', 'show', f'{base}:{path}'], capture_output=True,
                          text=True, check=True).stdout


def lines_by_kind(text):
    '''Yield (is_command, line) for every line; a command line is a
    non-blank, non-comment line inside a bash fence.'''
    inside = False
    for line in text.split('\n'):
        if line.startswith('```'):
            inside = line.strip() == '```bash'
            yield False, line
            continue
        yield inside and bool(line.strip()) and not line.lstrip().startswith('#'), line


def commands(text):
    out, pending = [], ''
    for is_command, line in lines_by_kind(text):
        if not is_command:
            continue
        if line.endswith('\\'):
            pending += line[:-1] + ' '
            continue
        out.append(' '.join((pending + line).split()))
        pending = ''
    return out


def bullet(text):
    m = re.search(r"^- \*\*Lowell's originals\*\*.*$", text, re.M)
    return m.group(0) if m else None


def main(base='HEAD'):
    counts_only = base == '--counts-only'
    old = at('HEAD' if counts_only else base, 'CLAUDE.md')
    new = Path('CLAUDE.md').read_text()
    problems = []
    if counts_only:
        pass
    elif commands(old) != commands(new):
        problems.append('command lines differ:\n' + '\n'.join(
            difflib.unified_diff(commands(old), commands(new), base, 'now', lineterm='')))
    if not counts_only and (bullet(new) is None or bullet(old) != bullet(new)):
        problems.append("the Lowell's originals bullet changed or is missing")
    for path in FILES:
        for n, (is_command, line) in enumerate(lines_by_kind(Path(path).read_text()), start=1):
            if not is_command and re.search(r'\d', ALLOWED_RE.sub('', line)):
                problems.append(f'{path}:{n}: a numeral outside ALLOWED: {line.strip()}')
    print(f'{len(commands(new))} command lines; CLAUDE.md {len(old.splitlines())} -> '
          f'{len(new.splitlines())} lines; build/CLAUDE.md {len(Path(FILES[1]).read_text().splitlines())} lines')
    if problems:
        sys.exit('\n'.join(problems))


if __name__ == '__main__':
    main(*sys.argv[1:])
```

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python .sdd/38-claude-code-drift-automation/claude_md_audit.py; echo "exit=$?"`
Expected: `35 command lines; CLAUDE.md 224 -> 224 lines; build/CLAUDE.md 17 lines`, then 34 lines of the form `CLAUDE.md:<n>: a numeral outside ALLOWED: …`, the first being `CLAUDE.md:65: … DEPENDENCIES drift — 62 tests`, and `exit=1`. That is this task's red: the counts are still there.

- [x] **Step 3: Write CLAUDE.md.** Replace the whole file with exactly this content (170 lines):

````markdown
# CLAUDE.md

This file is the canonical maintainer guide for Claude Code, Codex, and Gemini CLI when working in this repository. `AGENTS.md` points Codex here and `GEMINI.md` imports it.

## What this repo is

A personal collection of coding-agent configuration, centered on the portable [Agent Skills specification](https://agentskills.io/specification). Skills live under `skills/` — each subdirectory is **one self-contained skill**: a `SKILL.md` plus optional `references/` (loaded on demand) and `scripts/` (executable helpers). Sibling top-level dirs hold the other config types: `agents/` (canonical Claude-format subagent definitions), `commands/` (canonical Claude slash commands), `runtimes/` (generated Codex and Gemini adapters), `hooks/` (Claude Code hook templates and its read-only-agent guard), and `rules/` (Claude Code path-scoped rules). There is no application here to run — the "product" is the skill text, companion configuration, and bundled scripts.

`install.py` installs skills and companion assets for Claude, Codex, Gemini, or all three. Claude uses `~/.claude/skills/`; Codex and Gemini share `~/.agents/skills/`. This repo *is* the user's symlinked source, so edits here are live.

## Runtime adapters

`agents/*.md` and `commands/*.md` are canonical. Never hand-edit files under `runtimes/`. After changing a canonical agent or command, regenerate and check the adapters:

```bash
uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py
uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check
```

The generator translates manifest syntax and Gemini tool names only. Codex and Gemini agents inherit the active runtime model; Claude-specific model pins do not cross runtimes. Gemini gets TOML command adapters. Codex has no command adapter here; reusable Codex workflows are skills.

## Provenance is load-bearing — preserve it

Skills come from five sources with distinct attribution, all tracked in `NOTICE`. **Read `NOTICE` before moving, renaming, or substantially rewriting any skill**, and keep it in sync:

- **Lowell's originals** (MIT, `LICENSE`): `develop-testing-strategy`, `validate-data`, `explore-data`, `tech-debt`, `design-architecture`, `bls-data-context`, `recommend-probabilistic-model`, `recommend-visualization`, `track-model-experiments`, `tune-hyperparameters`, `creative-thinking`, `llm-wiki`, `describe-critique-methodology`, `derive-roadmap`, `classification-codes`, `geographic-codes`, `deep-learning`, `evaluate-deep-learning`, `optimize-jax`. (19 originals — keep in sync with `NOTICE`, which is authoritative.)
- **`bayesian-workflow`** — adapted from Alexandre Andorra's PyMC skill, ported to NumPyro+JAX (MIT).
- **`recommend-causal-design`** — planning workflow selectively adapted from Robson Tigre's `causal-planner` and Alexandre Andorra's `causal-inference` (MIT); newly written method references and memo contract, with both source notices in `LICENSE-causal-design-sources`.
- **superpowers skills** (MIT, © 2025 Jesse Vincent, `LICENSE-superpowers`): the 13 process skills (`brainstorming`, `writing-plans`, `test-driven-development`, etc.). These were adapted from the upstream `superpowers` plugin.
- **clean-code family** — `clean-coder`, `clean-code`, and `rules/clean-code-python.md` adapt Robert C. Martin's *Clean Code* rule catalog (2008), cited by rule code only, no book prose; `clean-coder` also cites Beck's *Tidy First?*, Fowler's opportunistic refactoring, and Ousterhout's *APOSD* by idea only.

Two invariants from that adaptation that must not silently regress:
- **Cross-skill references use bare skill names** (`use the writing-plans skill`), never the upstream `superpowers:` plugin namespace.
- `recommend-probabilistic-model` **cites** Murphy's PML books (CC-BY-NC-ND) and pyprobml/dynamax (MIT) but **redistributes no book prose and bundles no PDFs**. Keep summaries in original wording with §-number citations only.

The user is meticulous about attribution and licensing — surface provenance/license implications proactively rather than assuming.

## Editing skills and other Claude Code artifacts

Every Claude Code artifact — skill, agent, command, hook, rule, settings, installer (`install.py`), or CLAUDE.md — follows the guide sections its kind maps to in `build/cc_guide/conformance.toml`, the register for `specs/guides/claude-code-customization-guide.md`, whichever runtime does the editing. Record a departure there as a deviation or a gap only on the owner's decision, and run `check_conformance.py` (Commands) before committing.

When creating or editing a skill, **follow the `writing-skills` skill** — it's the meta-skill governing this repo. Key points it enforces:
- Frontmatter needs `name` + `description`; the description starts with "Use when…", is third-person, and is dense with concrete triggers (this is what drives auto-loading, so wording is functional, not decorative).
- Discipline/behavior skills are pressure-tested and their wording micro-tested against a no-guidance control before deployment; pure reference skills are not.

A skill's references into other skills and to commands are install dependencies; a handoff to a whole skill by name (`REQUIRED SUB-SKILL: Use …`) is not. Adding or dropping a `/command`, a `../<skill>/` or `<skill>/references/…` path, or a named section of another skill (`<skill>'s Model Selection`) must be mirrored in `install.py`'s `DEPENDENCIES` (hard: the skill cannot work without it) or in `build/test_runtime_support.py`'s `SOFT_REFERENCES` (soft, with a reason). The dependency-drift check in Commands fails on a mismatch.

## Conventions

- **Python style**: Polars over pandas; single quotes over double; NumPyro + JAX (not PyMC) for Bayesian code; target Python 3.13.
- **Specs & plans**: design records live in `specs/` (retired ones in `specs/completed/`). Implementation plans go to `specs/plans/<id>-<spec-name>.md` where `<id>` is the next integer (max existing id across `specs/plans/` and `specs/plans/completed/`, +1). At completion, the plan-completion protocol (writing-plans § Plan Completion Protocol) gates leftovers past the user, marks up the plan, appends consciously-deferred work to `specs/deferred_items.md`, and retires the plan (and, when no other live plan shares it, the spec) to the `completed/` dirs.

## Build tooling (`build/`)

`build/` holds the repo's lints and commit gates, the cross-runtime adapter generator (`sync_runtime_assets.py`), and the citation-verification pipeline for `recommend-probabilistic-model`; `build/CLAUDE.md` describes each. **`build/.scratch/` is gitignored and must never be committed** — it contains own-use extraction of CC-BY-NC-ND material.

## Commands

There is no root test runner or repo-wide `pyproject`, and the scientific deps (numpy, polars, pytest) aren't installed into the interpreter directly. Run everything through `uv run` pinned to the Homebrew Python 3.13, supplying deps inline. Tests use **bare imports** and are **directory-scoped** — run pytest from inside the relevant directory, not the repo root: each suite pins its own inline deps, and a repo-root collection fails outright anyway, since `geographic-codes` and `classification-codes` both ship a `test_build.py` whose basenames collide under pytest's prepend import mode with no `__init__.py`. Comments name the extra `--with` deps that unlock a suite's skips; pytest's summary line gives the counts.

```bash
# Cross-runtime adapters, installer, and DEPENDENCIES drift
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py

# Full build-directory tests. The snippet tests that need the stack skip unless you add --with "arviz>=1.0"
# --with arviz-base --with arviz-stats --with arviz-plots --with numpyro --with jax --with matplotlib. A fresh clone
# or worktree lacks the gitignored build/.scratch/, so test_verify_citations.py's ground-truth tests fail or skip there
cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q

# recommend-probabilistic-model signal-extractor tests
cd skills/recommend-probabilistic-model/scripts && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest -q

# recommend-visualization router tests
cd skills/recommend-visualization/scripts && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest -q

# tune-hyperparameters CV-splitter tests; its skips need --with scikit-learn --with optuna (--with sklearn fails)
cd skills/tune-hyperparameters/scripts && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest -q

# track-model-experiments ledger/compare tests (~20–50 s, depending on the uv cache). They round-trip
# InferenceData to .nc, so they need the full numpyro + NetCDF-writer chain
cd skills/track-model-experiments/scripts && uv run --python 3.13 --with pytest --with numpy --with polars --with arviz --with numpyro --with h5netcdf --with h5py python -m pytest -q

# bayesian-workflow script tests (MCSE precision, divergence-gate and calibration next steps and verdicts, figures,
# --ci-prob, --loo-pit group checks). --with matplotlib runs the figure test; CALIBRATION_SWEEP=1 runs the
# pre-registered acceptance sweep over both paths (seeds 0-99, about 1.5 min; -s prints its counts). arviz's
# "invalid value encountered in scalar divide" warnings on the constant-parameter fixture are expected, not silenced
cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q

# llm-wiki bundled wiki-script tests (bootstrap, lint, session and specs distillers; stdlib only). The
# @needs_pilot tests read a pilot wiki at $LLM_WIKI_ROOT (default ~/research-wiki) and skip without one
cd skills/llm-wiki/scripts && uv run --python 3.13 --with pytest python -m pytest -q

# describe-critique-methodology decoupling-check tests
cd skills/describe-critique-methodology/scripts && uv run --python 3.13 --with pytest python -m pytest -q

# writing-plans deferred-backlog stats tests (stdlib only)
cd skills/writing-plans/scripts && uv run --python 3.13 --with pytest python -m pytest -q

# geographic-codes build tests; the per-vintage workbook tests read the committed sources/
cd skills/geographic-codes/scripts && uv run --python 3.13 --with pytest --with polars --with fastexcel python -m pytest -q

# classification-codes build tests (fixtures are in-memory frames, so no workbook reader is needed)
cd skills/classification-codes/scripts && uv run --python 3.13 --with pytest --with polars python -m pytest -q

# explore-data profile.py tests (its --json contract is recommend-visualization's input). profile.py
# shadows the stdlib `profile` module, but the repo-wide reason above is why this cd's in
cd skills/explore-data/scripts && uv run --python 3.13 --with pytest --with polars python -m pytest -q

# design-architecture ADR-scaffolder tests (stdlib only)
cd skills/design-architecture/scripts && uv run --python 3.13 --with pytest python -m pytest -q

# subagent-driven-development dispatch-script tests (stdlib only; they drive its bash scripts)
cd skills/subagent-driven-development/scripts && uv run --python 3.13 --with pytest python -m pytest -q

# read-only agent guard tests (Gate A: classifier units, payload contract). The guard is stdlib only and must stay
# 3.9-compatible, so run BOTH: the first runs each contract test through the hook's shebang on the test's PATH and on
# launchd's /usr/bin-first PATH (under uv run the shebang resolves to uv's pinned python); the second runs the whole
# suite under the 3.9 floor. Where /usr/bin/python3 is missing or not 3.9, the launchd-PATH runs skip (-rs shows why)
# and the floor goes untested. Gate B is the live probe, ./hooks/probe-readonly-guard.sh, which spawns claude -p
cd hooks && uv run --python 3.13 --with pytest python -m pytest -q && uv run --python /usr/bin/python3 --with pytest python -m pytest -q

# Frontmatter, provenance and guide-conformance lints (run before committing any Claude Code artifact)
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
uv run --python 3.13 --with pyyaml python build/check_conformance.py

# Dependency drift: skill and command text vs install.py's DEPENDENCIES (run before committing a skill
# change that adds or drops a cross-skill or /command reference)
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies

# Snippet gate: three tiers, cheapest first, each including those above. Tier 1 covers all of skills/; Tiers 2 and 3
# only skills/bayesian-workflow, whose stack they import. build/check_snippets.py documents the fence markers (norun,
# noparse, fixture=<name>). If a block raises under Tier 3, fix it: norun is for blocks that cannot run by design.
# Tier 1 (parse-only, stdlib, instant) — run before committing any skill edit:
uv run --python 3.13 python build/check_snippets.py skills/
# Tier 2 (+ resolve dotted library chains from code and backticked prose; imports the stack, ~30s):
uv run --python 3.13 --with "arviz>=1.0" --with arviz-base --with arviz-stats --with arviz-plots --with numpyro --with jax python build/check_snippets.py --api skills/bayesian-workflow/
# Tier 3 (+ execute the harnessed subset; minutes; the pins match build/snippet_preamble.py's PINNED, refresh deliberately):
uv run --python 3.13 --with 'arviz==1.3.0' --with arviz-base --with 'arviz-stats==1.3.2' --with 'arviz-plots==1.3.1' --with 'numpyro==0.21.0' --with 'jax==0.11.1' --with numpy --with matplotlib python build/check_snippets.py --run skills/bayesian-workflow/

# CPU-example process-contract tests (stdlib + pytest only). The JAX run itself is the pinned command
# below; it skips norun and noparse blocks and does not validate the surrounding prose
cd build && uv run --python 3.13 --with pytest python -m pytest -q test_check_jax_examples.py

# Verified deep-learning CPU examples (canonical Markdown blocks, no preamble), pinned by specs/verification/32-jax-cpu.in
# -> 32-jax-cpu.txt: refresh deliberately, then rerun. Hardware and checkpoint recipes in references state their own limits
JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/deep-learning/

# Single test
cd build && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest test_verify_citations.py::test_true_negative_flags_bad_refs

# End-to-end routing smoke test (no PDFs needed)
uv run --python 3.13 --with numpy --with polars python build/smoke_test.py

# Rebuild geographic-codes data/ from the pinned Census/OMB sources (network) or the sources/ cache
uv run skills/geographic-codes/scripts/build.py
uv run skills/geographic-codes/scripts/build.py --offline

# Rebuild classification-codes data/ from the pinned Census/BLS sources (network; the bls.gov workbooks
# need BLS_CONTACT_EMAIL exported) or the sources/ cache
uv run skills/classification-codes/scripts/build.py
uv run skills/classification-codes/scripts/build.py --offline

# Verify citations across the whole skill (Gate A; exit 0 = all resolve; chapter-fallback WARNs on
# stderr are non-fatal — confirm those via Gate B)
uv run --python 3.13 python build/verify_citations.py skills/recommend-probabilistic-model/

# Rebuild citation ground truth (needs local PDFs + gh; writes gitignored build/.scratch/)
uv run --python 3.13 python build/extract_structure.py
```
````

- [x] **Step 4: Correct `build/CLAUDE.md`.** Replace

```markdown
Most files here form a citation-verification pipeline, not a project build. It
exists to keep `recommend-probabilistic-model`'s PML §-refs and pyprobml
notebook links honest. Two gates:
```

with

```markdown
This directory holds the repo's lints and commit gates (each `check_*.py`
documents itself in its docstring), the cross-runtime adapter generator, and a
citation-verification pipeline. The root `CLAUDE.md` lists their commands.

The pipeline keeps `recommend-probabilistic-model`'s PML §-refs and pyprobml
notebook links honest, through two gates:
```

and replace

```markdown
The exception is `sync_runtime_assets.py` plus
`test_runtime_support.py`: these generate and verify Codex/Gemini adapters and
the cross-runtime installer. Their canonical inputs are `../agents/*.md` and
`../commands/*.md`; never edit `../runtimes/` by hand. `test_runtime_support.py`
also scans the agent-facing text of `../skills/**` (not READMEs or install
guides) against `../install.py`'s `DEPENDENCIES`, so a skill edit can fail it.
```

with

```markdown
`sync_runtime_assets.py` and `test_runtime_support.py` generate and verify
Codex/Gemini adapters and the cross-runtime installer. Their canonical inputs
are `../agents/*.md` and `../commands/*.md`; never edit `../runtimes/` by hand.
`test_runtime_support.py` also scans the agent-facing text of `../skills/**`
(not READMEs or install guides) against `../install.py`'s `DEPENDENCIES`, so a
skill edit can fail it.
```

- [x] **Step 5: Remove both exceptions from the register.** In `build/cc_guide/conformance.toml`, delete this block, its comment and the blank line after it:

```toml
# The root CLAUDE.md is over the docs target. The owner set its type,
# ceiling and tracked_in at the gate (the audit report's Owner decisions):
# choice A trimmed it to 225 lines without dropping an instruction.
[[exception]]
id = 'claude-md-size'
type = 'gap'
check = 'claude-md-size'
sections = ['rules.claude-md']
artifacts = ['CLAUDE.md']
guide = 'The docs target fewer than 200 lines per CLAUDE.md file.'
reason = 'Codex and Gemini read the same file, so instructions leave it only by deliberate condensing or relocation.'
evidence = 'Audit row L-01; owner gate 2026-10-04 (choice A, trim to 225).'
ceiling = 225
tracked_in = 'deferred item: bring the root CLAUDE.md under 200 lines'
```

and delete this block and the blank line after it:

```toml
[[exception]]
id = 'claude-md-fast-changing-details'
type = 'gap'
sections = ['rules.claude-md']
artifacts = ['CLAUDE.md', 'build/CLAUDE.md']
guide = 'Keep fast-changing details and anything readable from the code out of CLAUDE.md.'
reason = 'Both files carry hand-kept test counts, rules restated from code, and a stale description of build/.'
evidence = 'Audit rows C-02 to C-05; owner gate 2026-10-04.'
tracked_in = 'deferred item: bring the root CLAUDE.md under 200 lines'
```

The `[[check]]` entry `claude-md-size` (with `limit = 200`) stays.

- [x] **Step 6: Verify (green).**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && wc -l < CLAUDE.md && uv run --python 3.13 python .sdd/38-claude-code-drift-automation/claude_md_audit.py; echo "exit=$?"`
Expected: `170`, then `35 command lines; CLAUDE.md 224 -> 170 lines; build/CLAUDE.md 20 lines` and `exit=0`. So every command is unchanged, the originals bullet is byte-identical, and no count is left in either file.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 --with pyyaml python build/check_conformance.py; echo "exit=$?"; uv run --python 3.13 python build/check_provenance.py; echo "exit=$?"`
Expected: `exit=0` twice. With the exceptions gone, `claude-md-size` now holds CLAUDE.md to 199 lines, and a stale waiver would have failed here.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && grep -n "claude-md-size\|claude-md-fast-changing" build/cc_guide/conformance.toml`
Expected: exactly one line, `id = 'claude-md-size'`, the `[[check]]` entry.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py test_check_provenance.py test_check_snippets.py`
Expected: no failures, and the same passed and skipped counts as these files had at the baseline. `test_check_provenance.py` reads the originals bullet, and `test_repo_passes` runs the conformance lint on this tree.

- [x] **Step 7: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && [ "$(git branch --show-current)" = feat/cc-drift-stage1 ] && git add CLAUDE.md build/CLAUDE.md build/cc_guide/conformance.toml && git commit -m "docs: bring the root CLAUDE.md under 200 lines

Removes every hand-kept test count, points the snippet-marker rules at
build/check_snippets.py's docstring, and describes build/ accurately in
both CLAUDE.md files (plan 35 audit rows C-02 to C-05). Every command
line is unchanged; comments are condensed in place, since Codex and
Gemini read only the root file. 224 -> 170 lines, so the register's
claude-md-size and claude-md-fast-changing-details exceptions go in the
same change.

Plan 38, Task 2.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Docs blocks (`blocks.py`, R3)

**Files:**
- Create: `build/cc_guide/cc_fixtures.py` (its first part)
- Create: `build/cc_guide/blocks.py`
- Test: `build/cc_guide/test_blocks.py`

**Interfaces:**
- Consumes: nothing; stdlib only.
- Produces, for `guide.py`, `state.py`, `baseline.py`, `lint.py` and `check.py`:
  - `SEP = ' › '`, `INTRO = '(intro)'`, `EMPTY_CELL = '(row)'`, `KEY_PART_MAX = 60`, and `CELL_SPLIT_RE` (splits on unescaped `|`);
  - `fence_spans(lines: list[str]) -> list[tuple[int, int | None, str]]`, giving (open, close or None, info string) for each fence;
  - `fenced_lines(lines: list[str]) -> set[int]`, the 0-based lines that open, close or sit inside a fence;
  - `normalize(text: str) -> str`, `block_hash(text: str) -> str` (16 hex) and `key_part(text: str) -> str`;
  - `strip_preamble(lines: list[str]) -> list[str]`, `first_cell(row: str) -> str` and `is_table_start(lines, i, fenced) -> bool`;
  - `page_blocks(text: str) -> dict[str, str]`, which maps key to normalized text, in page order;
  - `contains_term(key, text, terms) -> bool`, `select(blocks: dict[str, str], mark: str, terms: set[str]) -> list[str]` and `candidates(key: str, text: str, section_terms: dict[str, set[str]]) -> list[str]`.
- Fixtures (`cc_fixtures.py`): `FENCE`, `FENCE4`, `TILDE`, the autouse `isolated_home`, `ENV_PAGE`, `TABLE_PAGE` and `PLATFORM_PAGE`.

R3.1's fence rule follows `build/fences.py`, which R12.1 forbids importing. It is extended to tilde fences and to openers at any indentation. `guide.py` (Task 5) splits the guide with the same rule.

- [x] **Step 1: Create the fixtures file** `build/cc_guide/cc_fixtures.py` with exactly this content:

```python
'''Hand-written fixtures for the cc_guide suite. Never copied docs text.

Test modules import what they need; importing `isolated_home` registers that
autouse fixture in the importing module, so no test reaches the real
~/.cache. Fence strings are built from FENCE, FENCE4 and TILDE, so no line of
this file is itself a fence.
'''
import pytest

FENCE = '`' * 3
FENCE4 = '`' * 4


TILDE = '~' * 3


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    '''Point HOME at a scratch directory, so a default cache path can never
    resolve into the real ~/.cache.'''
    home = tmp_path / 'home'
    home.mkdir()
    monkeypatch.setenv('HOME', str(home))
    return home


# An env-vars-style page: the Documentation Index preamble, an intro, a table
# with a repeated, an empty and a pipe-escaping first cell, every fence shape
# R3.1 names, and a repeated heading path.
ENV_PAGE = '\n'.join([
    '> ## Documentation Index',
    '> Fetch the complete documentation index at: https://docs.example.invalid/llms.txt',
    '> Use this file to discover all available pages before exploring further.',
    '',
    '# Environment variables',
    '',
    '> Variables that steer the fixture tool.',
    '',
    'Set them in a [settings file](/docs/en/settings).',
    '',
    '| Variable | Purpose |',
    '| :--- | :--- |',
    '| `ALPHA_ENV` | Turns on alpha. |',
    '| `BETA_ENV` | Turns on beta; see [events](/docs/en/events). |',
    '| `PIPE_ENV` | Accepts `a\\|b`. |',
    '|  | A row with an empty first cell. |',
    '| `ALPHA_ENV` | Repeats a first cell. |',
    '',
    'Text after the table stays in the heading block.',
    '',
    '## Examples',
    '',
    FENCE + 'bash',
    '# a shell comment, not a heading',
    'export ALPHA_ENV=1',
    FENCE,
    '',
    '  ' + FENCE + 'json',
    '  # an indented fence, still code',
    '  ' + FENCE,
    '',
    TILDE,
    '## a tilde fence, not a heading',
    TILDE,
    '',
    FENCE4 + 'markdown',
    FENCE + 'python',
    '## nested, not a heading',
    FENCE,
    FENCE4,
    '',
    '## Examples',
    '',
    'A second Examples heading.',
    '',
])


# A page with no title: a lone ## whose whole body is a table.
TABLE_PAGE = '\n'.join([
    '## Settings',
    '| Key | Value |',
    '|---|---|',
    '| `alpha.mode` | fast |',
    '| `beta.mode` | slow |',
    '',
])


# A platform page: YAML front matter instead of the preamble.
PLATFORM_PAGE = '\n'.join([
    '---',
    'title: Fixture pricing',
    'url: https://platform.example.invalid/docs/en/pricing',
    '---',
    '',
    'Prices for `BETA_ENV` users.',
    '',
    '## Rates',
    '',
    'Rates move with `BetaEvent`.',
    '',
])
```

> Deviation: on the owner's call (ruling 1, 2026-10-04), two preamble lines of
> `ENV_PAGE` that repeated the docs' own wording are paraphrased, keeping the line
> count; Task 4's `CHANGELOG_TEXT` and Task 7's `TOOLS_PAGE` take the same paraphrase.

- [x] **Step 2: Write the tests.** Create `build/cc_guide/test_blocks.py`:

```python
'''Tests for blocks.py: fences, page splitting, keys, normalization, hashing
and selection (drift spec R3).'''
import blocks
from cc_fixtures import (ENV_PAGE, FENCE, FENCE4, PLATFORM_PAGE, TABLE_PAGE,  # noqa: F401
                         TILDE, isolated_home)

ENV = 'Environment variables'


def test_fences_cover_backtick_tilde_indented_and_nested_shapes():
    lines = ['a', FENCE + 'bash', '# x', FENCE, '  ' + FENCE, '  # y', '  ' + FENCE,
             TILDE, '## z', TILDE, FENCE4, FENCE, '# w', FENCE, FENCE4, 'b']
    assert blocks.fenced_lines(lines) == set(range(1, 15))


def test_a_fence_closes_only_on_its_own_character_at_its_length():
    lines = [FENCE4, FENCE, TILDE * 2, FENCE4 + ' x', 'still code', FENCE4 + '`', 'out']
    assert blocks.fenced_lines(lines) == {0, 1, 2, 3, 4, 5}


def test_fence_spans_carry_each_openers_info_string():
    lines = [FENCE + 'json', '{}', FENCE, TILDE + ' bash x', 'ls', TILDE, FENCE]
    assert blocks.fence_spans(lines) == [(0, 2, 'json'), (3, 5, 'bash x'), (6, None, '')]


def test_an_unclosed_fence_runs_to_the_end():
    assert blocks.fenced_lines(['a', TILDE, '## b', 'c']) == {1, 2, 3}


def test_the_documentation_index_preamble_is_dropped():
    lines = ENV_PAGE.split('\n')
    assert blocks.strip_preamble(lines) == lines[3:]
    quote = ['> A plain blockquote.', '', '# T']
    assert blocks.strip_preamble(quote) == quote


def test_page_blocks_in_page_order_with_rows_and_ordinals():
    assert list(blocks.page_blocks(ENV_PAGE)) == [
        ENV,
        f'{ENV} › `ALPHA_ENV`',
        f'{ENV} › `BETA_ENV`',
        f'{ENV} › `PIPE_ENV`',
        f'{ENV} › (row)',
        f'{ENV} › `ALPHA_ENV`#2',
        f'{ENV} › Examples',
        f'{ENV} › Examples#2',
    ]


def test_a_heading_block_keeps_its_table_header_and_trailing_text_only():
    assert blocks.page_blocks(ENV_PAGE)[ENV] == '\n'.join([
        '# Environment variables',
        '> Variables that steer the fixture tool.',
        'Set them in a [settings file]().',
        '| Variable | Purpose |',
        '| :--- | :--- |',
        'Text after the table stays in the heading block.',
    ])


def test_hash_lines_inside_any_fence_never_cut_a_block():
    examples = blocks.page_blocks(ENV_PAGE)[f'{ENV} › Examples']
    assert '# a shell comment, not a heading' in examples
    assert '# an indented fence, still code' in examples
    assert '## a tilde fence, not a heading' in examples
    assert '## nested, not a heading' in examples


def test_a_row_splits_on_unescaped_pipes_only():
    assert blocks.first_cell('| `a\\|b` | c |') == '`a\\|b`'
    assert blocks.page_blocks(ENV_PAGE)[f'{ENV} › `PIPE_ENV`'] == '| `PIPE_ENV` | Accepts `a\\|b`. |'


def test_a_table_under_a_lone_heading():
    assert blocks.page_blocks(TABLE_PAGE) == {
        'Settings': '## Settings\n| Key | Value |\n|---|---|',
        'Settings › `alpha.mode`': '| `alpha.mode` | fast |',
        'Settings › `beta.mode`': '| `beta.mode` | slow |',
    }


def test_platform_front_matter_stays_in_the_intro_block():
    assert blocks.page_blocks(PLATFORM_PAGE) == {
        '(intro)': ('---\ntitle: Fixture pricing\n'
                    'url: https://platform.example.invalid/docs/en/pricing\n'
                    '---\nPrices for `BETA_ENV` users.'),
        'Rates': '## Rates\nRates move with `BetaEvent`.',
    }


def test_heading_paths_join_ancestors_and_drop_closing_hashes():
    page = '# T\n## A ##\n### B\n## C\n### B\n'
    assert list(blocks.page_blocks(page)) == ['T', 'T › A', 'T › A › B', 'T › C', 'T › C › B']


def test_normalize_empties_link_targets_and_collapses_whitespace():
    text = '  See   [a](https://x.invalid/a)\n\n\tand [b](/docs/en/b).  \n'
    assert blocks.normalize(text) == 'See [a]()\nand [b]().'


def test_block_hash_is_sixteen_hex_of_the_normalized_text():
    h = blocks.block_hash('Use [it](/a) now.')
    assert len(h) == 16 and int(h, 16) >= 0
    assert blocks.block_hash('Use  [it](/moved)\nnow.'.replace('\n', ' ')) == h
    assert blocks.block_hash('Use [it](/a) later.') != h


def test_key_parts_drop_link_targets_and_cap_at_sixty_characters():
    assert blocks.key_part('[Hooks](/docs/en/hooks)  page') == '[Hooks]() page'
    long = 'word ' * 20
    assert blocks.key_part(long) == long[:59] + '…'
    assert len(blocks.key_part(long)) == 60


def test_select_takes_every_block_of_an_all_page_and_term_hits_of_a_terms_page():
    page = blocks.page_blocks(ENV_PAGE)
    assert blocks.select(page, 'all', set()) == list(page)
    assert blocks.select(page, 'terms', {'BETA_ENV'}) == [f'{ENV} › `BETA_ENV`']
    assert blocks.select(page, 'terms', {'Examples'}) == [f'{ENV} › Examples', f'{ENV} › Examples#2']


def test_candidates_are_matching_sections_or_the_whole_group():
    terms = {'b.overview': {'BETA_ENV'}, 'b.events': {'BetaEvent', 'BETA_ENV'}, 'b.other': {'zzz'}}
    assert blocks.candidates('k', 'uses BETA_ENV', terms) == ['b.overview', 'b.events']
    assert blocks.candidates('k', 'nothing here', terms) == ['b.overview', 'b.events', 'b.other']
```

- [x] **Step 3: Create the stub** `build/cc_guide/blocks.py`, holding only its docstring line: `'''Docs pages as hashed blocks (drift spec R3).'''`

- [x] **Step 4: Run the tests to see them fail.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf test_blocks.py`
Expected: `17 failed`. Each failure is `AttributeError: module 'blocks' has no attribute …`: seven for `page_blocks`, three for `fenced_lines`, and one each for the other seven names.

- [x] **Step 5: Implement.** Replace `build/cc_guide/blocks.py` with:

```python
'''Docs pages as hashed blocks (drift spec R3).

A page becomes one block per ATX heading, holding the heading's own text up to
the next heading of any level, plus one block per table row. The leading
"Documentation Index" blockquote is dropped first. Blocks are keyed by heading
path and hashed after normalization. A group watches the blocks its pages'
marks and its sections' terms select.
'''
import hashlib
import re

SEP = ' › '
INTRO = '(intro)'
EMPTY_CELL = '(row)'
# Each key component is capped like R3.6's terms, so no committed key carries
# more than a heading-sized fragment of docs text (spec, Provenance).
KEY_PART_MAX = 60

FENCE_OPEN_RE = re.compile(r'^[ \t]*(`{3,}|~{3,})')
ATX_RE = re.compile(r'^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$')
LINK_RE = re.compile(r'\]\([^)]*\)')
SEPARATOR_RE = re.compile(r'^\|?[ \t]*:?-+:?[ \t]*(?:\|[ \t]*:?-+:?[ \t]*)*\|?$')
CELL_SPLIT_RE = re.compile(r'(?<!\\)\|')


def fence_spans(lines: list[str]) -> list[tuple[int, int | None, str]]:
    '''Each fenced code block as (open, close, info): 0-based line indexes,
    close None when the fence never closes (R3.1). A fence opens on three or
    more backticks or tildes at any indentation, and closes only on a line
    holding nothing but a run of the same character at least as long.'''
    spans: list[tuple[int, int | None, str]] = []
    fence: tuple[str, int, int, str] | None = None  # char, length, open, info
    for i, line in enumerate(lines):
        if fence is None:
            m = FENCE_OPEN_RE.match(line)
            if m:
                fence = (m.group(1)[0], len(m.group(1)), i, line[m.end():].strip())
            continue
        s = line.strip()
        if s and set(s) == {fence[0]} and len(s) >= fence[1]:
            spans.append((fence[2], i, fence[3]))
            fence = None
    if fence is not None:
        spans.append((fence[2], None, fence[3]))
    return spans


def fenced_lines(lines: list[str]) -> set[int]:
    '''0-based indexes of the lines that open, close or sit inside a fenced
    code block. An unclosed fence runs to the end.'''
    last = len(lines) - 1
    return {i for start, close, _ in fence_spans(lines)
            for i in range(start, (last if close is None else close) + 1)}


def normalize(text: str) -> str:
    '''R3.5 steps 1-3: empty every link target, collapse whitespace runs,
    strip each line, and drop empty lines.'''
    lines = (' '.join(line.split()) for line in LINK_RE.sub(']()', text).split('\n'))
    return '\n'.join(line for line in lines if line)


def block_hash(text: str) -> str:
    '''R3.5 step 4: the first 16 hex characters of SHA-256 over the
    normalized text, as UTF-8.'''
    return hashlib.sha256(normalize(text).encode('utf-8')).hexdigest()[:16]


def key_part(text: str) -> str:
    '''One component of a block key: R3.5's link and whitespace steps, cut to
    KEY_PART_MAX characters.'''
    part = ' '.join(LINK_RE.sub(']()', text).split())
    return part if len(part) <= KEY_PART_MAX else part[:KEY_PART_MAX - 1] + '…'


def strip_preamble(lines: list[str]) -> list[str]:
    '''R3.2: drop the leading "Documentation Index" blockquote, the `>` lines
    at the top of a page that point to llms.txt.'''
    n = 0
    while n < len(lines) and lines[n].startswith('>'):
        n += 1
    if n and any('llms.txt' in line for line in lines[:n]):
        return lines[n:]
    return lines


def first_cell(row: str) -> str:
    '''A table row's first cell, split on unescaped pipes only.'''
    s = row.strip()
    if s.startswith('|'):
        s = s[1:]
    return CELL_SPLIT_RE.split(s, 1)[0].strip()


def is_table_start(lines: list[str], i: int, fenced: set[int]) -> bool:
    '''A header row: a `|` line followed by a separator row.'''
    return (i + 1 < len(lines) and i + 1 not in fenced
            and lines[i].lstrip().startswith('|') and '|' in lines[i + 1]
            and SEPARATOR_RE.match(lines[i + 1].strip()) is not None)


def page_blocks(text: str) -> dict[str, str]:
    '''A docs page's blocks (R3.2-R3.4) as key -> normalized text, in page
    order. A heading's block runs to the next heading of any level, less its
    table rows, which become blocks keyed by the heading path and the row's
    first cell; header and separator rows stay in the heading's block. Text
    before the first heading is the (intro) block, dropped when empty. A
    repeated key gets an ordinal suffix (#2, #3, ...).'''
    lines = strip_preamble(text.split('\n'))
    fenced = fenced_lines(lines)
    current: list[str] = []
    raw: list[tuple[str, list[str]]] = [(INTRO, current)]
    path: list[tuple[int, str]] = []
    block_key = INTRO
    i = 0
    while i < len(lines):
        line = lines[i]
        if i not in fenced:
            m = ATX_RE.match(line)
            if m:
                level = len(m.group(1))
                path = [p for p in path if p[0] < level] + [(level, key_part(m.group(2) or ''))]
                block_key = SEP.join(p[1] for p in path)
                current = [line]
                raw.append((block_key, current))
                i += 1
                continue
            if is_table_start(lines, i, fenced):
                current.extend(lines[i:i + 2])
                i += 2
                while i < len(lines) and i not in fenced and lines[i].lstrip().startswith('|'):
                    cell = key_part(first_cell(lines[i])) or EMPTY_CELL
                    raw.append((block_key + SEP + cell, [lines[i]]))
                    i += 1
                continue
        current.append(line)
        i += 1
    blocks: dict[str, str] = {}
    seen: dict[str, int] = {}
    for key, block_lines in raw:
        body = normalize('\n'.join(block_lines))
        if key == INTRO and not body:
            continue
        n = seen.get(key, 0) + 1
        final = key if n == 1 else f'{key}#{n}'
        while final in blocks:
            n += 1
            final = f'{key}#{n}'
        seen[key] = n
        blocks[final] = body
    return blocks


def contains_term(key: str, text: str, terms) -> bool:
    '''Case-sensitive substring match of any term in a block's key or text.'''
    return any(t in key or t in text for t in terms)


def select(blocks: dict[str, str], mark: str, terms: set[str]) -> list[str]:
    '''R3.7: the keys a group watches on one page. Every block of an `all`
    page counts; on a `terms` page, a block counts when its key or normalized
    text contains one of the group's terms.'''
    if mark == 'all':
        return list(blocks)
    return [k for k, text in blocks.items() if contains_term(k, text, terms)]


def candidates(key: str, text: str, section_terms: dict[str, set[str]]) -> list[str]:
    '''R3.7: the group's sections whose terms the block contains, in group
    order, or every section of the group when none match.'''
    hits = [sid for sid, terms in section_terms.items() if contains_term(key, text, terms)]
    return hits or list(section_terms)
```

> Deviation: on the owner's call (ruling 2), `LINK_RE` stops at a newline
> (`r'\]\([^)\n]*\)'`), and `test_normalize_empties_link_targets_and_collapses_whitespace`
> gains one assertion. No count change.

- [x] **Step 6: Run the suite to see it pass.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: `17 passed`.

- [x] **Step 7: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && [ "$(git branch --show-current)" = feat/cc-drift-stage1 ] && git add build/cc_guide/cc_fixtures.py build/cc_guide/blocks.py build/cc_guide/test_blocks.py && git commit -m "feat(cc_guide): split docs pages into hashed blocks

blocks.py is R3 of the drift spec: fences in backticks or tildes at any
indentation, the llms.txt preamble dropped, one block per ATX heading
and per table row keyed by heading path, R3.5's normalization and 16-hex
hash, and R3.7's selection and candidate sections. Key components are
capped at 60 characters. Fixtures are hand-written.

Plan 38, Task 3.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

> Deviation: the plan's commit and the ruled fix were folded into one commit,
> 38607ca, so the copied preamble lines are in no branch commit.

---

### Task 4: Docs sources (`docs.py`: labels, changelog, `llms.txt`, page names)

**Files:**
- Modify: `build/cc_guide/cc_fixtures.py` (append)
- Create: `build/cc_guide/docs.py`
- Test: `build/cc_guide/test_docs.py`

**Interfaces:**
- Consumes: nothing.
- Produces, for `guide.py`, `state.py`, `baseline.py`, `check.py` and `cli.py`:
  - `CHANGELOG = 'changelog.md'`, `LLMS = 'llms.txt'` and `PLATFORM = 'platform:'`;
  - `version_key(label: str) -> tuple[int, ...]`, which raises `ValueError` on anything that is not a dotted-integer label;
  - `Release(label: str, date: date, bullets: list[str])`, a NamedTuple;
  - `parse_changelog(text: str) -> list[Release]`, newest first by version, which raises `ValueError('changelog line N: …')` on a bad label or date and `ValueError` on a repeated label;
  - `parse_llms(text: str) -> set[str]`, `is_platform(page: str) -> bool`, `page_file(page: str) -> str` and `page_url(page: str, sources: dict[str, str]) -> str`.
- Fixtures: `CHANGELOG_TEXT` (2.1.902 on October 1, 2.1.901 on September 20 and 2.1.900 on September 1, 2026, with two-space bullets as on the real page) and `LLMS_TEXT`.

The pre-check (Planning record) confirmed the live formats these parse.

- [x] **Step 1: Append to `build/cc_guide/cc_fixtures.py`,** after two blank lines:

```python
# Three releases, newest first as the real changelog lists them. Bullets are
# indented two spaces, as on the real page (checked 2026-10-04).
CHANGELOG_TEXT = '\n'.join([
    '> ## Documentation Index',
    '> Fetch the complete documentation index at: https://docs.example.invalid/llms.txt',
    '',
    '# Fixture changelog',
    '',
    '* A bullet outside every release block.',
    '',
    '<Update label="2.1.902" description="October 1, 2026">',
    '  * Changed how `BETA_ENV` is read',
    '  * Fixed a crash in the fixture tool',
    '</Update>',
    '',
    '<Update label="2.1.901" description="September 20, 2026">',
    '  * Added `ALPHA_ENV` to the alpha tools',
    '</Update>',
    '',
    '<Update label="2.1.900" description="September 1, 2026">',
    '  * First fixture release',
    '</Update>',
    '',
])


LLMS_TEXT = '\n'.join([
    '# Fixture docs',
    '',
    '- [Tools](https://code.claude.com/docs/en/tools.md): The tools page.',
    '- [Events](https://code.claude.com/docs/en/events.md): The events page.',
    '- [Environment variables](https://code.claude.com/docs/en/env-vars.md): Variables.',
    '- [Plugin parts](https://code.claude.com/docs/en/plugins/components.md): A nested slug.',
    '',
])
```

> Deviation: ruling 1's paraphrase applies to `CHANGELOG_TEXT`'s preamble line
> (Task 3, Step 1).

- [x] **Step 2: Write the tests.** Create `build/cc_guide/test_docs.py`:

```python
'''Tests for docs.py: release ordering, the changelog, llms.txt and page
naming (drift spec R2.4, R6.5, R6.6).'''
from datetime import date

import pytest

import docs
from cc_fixtures import CHANGELOG_TEXT, LLMS_TEXT, isolated_home  # noqa: F401


def test_versions_order_as_integer_tuples_with_four_components():
    labels = ['2.1.289', '2.1.288.1', '2.1.10', '2.1.288', '2.1.9']
    assert sorted(labels, key=docs.version_key) == ['2.1.9', '2.1.10', '2.1.288', '2.1.288.1', '2.1.289']


@pytest.mark.parametrize('label', ['2.1.x', '', '2.1.288-beta', 'v2.1.288'])
def test_version_key_rejects_what_is_not_a_label(label):
    with pytest.raises(ValueError):
        docs.version_key(label)


def test_changelog_blocks_come_newest_first_with_their_bullets():
    releases = docs.parse_changelog(CHANGELOG_TEXT)
    assert [(r.label, r.date) for r in releases] == [
        ('2.1.902', date(2026, 10, 1)), ('2.1.901', date(2026, 9, 20)), ('2.1.900', date(2026, 9, 1))]
    assert releases[0].bullets == ['Changed how `BETA_ENV` is read', 'Fixed a crash in the fixture tool']


def test_changelog_order_is_numeric_not_file_order():
    text = ('<Update label="2.1.9" description="July 1, 2026">\n  * a\n</Update>\n'
            '<Update label="2.1.10" description="July 2, 2026">\n  * b\n</Update>\n')
    assert [r.label for r in docs.parse_changelog(text)] == ['2.1.10', '2.1.9']


@pytest.mark.parametrize('text', [
    '<Update label="2.1.9" description="2026-07-01">\n</Update>\n',
    '<Update label="2.1.x" description="July 1, 2026">\n</Update>\n',
    ('<Update label="2.1.9" description="July 1, 2026">\n</Update>\n'
     '<Update label="2.1.9" description="July 2, 2026">\n</Update>\n'),
])
def test_changelog_rejects_a_bad_date_a_bad_label_or_a_repeat(text):
    with pytest.raises(ValueError):
        docs.parse_changelog(text)


def test_llms_lists_code_page_slugs():
    assert docs.parse_llms(LLMS_TEXT) == {'tools', 'events', 'env-vars', 'plugins/components'}


def test_page_files_and_urls_follow_the_snapshot_and_the_refresh():
    sources = {'docs_base': 'https://code.claude.com/docs/en/',
               'platform_base': 'https://platform.claude.com/docs/en/'}
    assert docs.page_file('plugins/components') == 'plugins_components.md'
    assert docs.page_file('platform:about-claude/pricing') == 'platform_about-claude_pricing.md'
    assert docs.page_url('hooks', sources) == 'https://code.claude.com/docs/en/hooks.md'
    assert (docs.page_url('platform:models/haiku-4-5/overview', sources)
            == 'https://platform.claude.com/docs/en/models/haiku-4-5/overview.md')
```

> Deviation: on the owner's call (ruling 3), the malformed-changelog test gains a
> fourth case, an `<Update …>` opener the pattern rejects, and is renamed (a09e62b).
> That is +1 test, so later `build/cc_guide/` totals run one above the plan's, and
> two above from Task 9 on.

- [x] **Step 3: Create the stub** `build/cc_guide/docs.py`, holding only `'''The docs sources around the block pages (drift spec R2.4, R6.5, R6.6).'''`

- [x] **Step 4: Run the tests to see them fail.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf test_docs.py`
Expected: `12 failed`, each `AttributeError: module 'docs' has no attribute …`: five for `version_key`, five for `parse_changelog`, one for `parse_llms` and one for `page_file`.

- [x] **Step 5: Implement.** Replace `build/cc_guide/docs.py` with:

```python
'''The docs sources around the block pages: release labels, the changelog,
llms.txt, and the file and URL of each mapped page (drift spec R2.4, R6.5,
R6.6, Layout).

A mapped page is a code.claude.com slug such as `hooks` or
`plugins/components`, or a platform slug written `platform:<slug>`.
'''
import re
from datetime import date, datetime
from typing import NamedTuple

CHANGELOG = 'changelog.md'
LLMS = 'llms.txt'
PLATFORM = 'platform:'

LABEL_RE = re.compile(r'^\d+(?:\.\d+)+$')
UPDATE_RE = re.compile(r'^<Update label="([^"]*)" description="([^"]*)">\s*$')
BULLET_RE = re.compile(r'^\s*\* (.*)$')
LLMS_RE = re.compile(r'\(https://code\.claude\.com/docs/en/([^)\s]+)\.md\)')


def version_key(label: str) -> tuple[int, ...]:
    '''R2.4: versions compare as integer tuples, so 2.1.288.1 sorts after
    2.1.288 and before 2.1.289.'''
    if not LABEL_RE.match(label):
        raise ValueError(f'not a release label: {label!r}')
    return tuple(int(part) for part in label.split('.'))


class Release(NamedTuple):
    label: str
    date: date
    bullets: list[str]


def parse_changelog(text: str) -> list[Release]:
    '''R6.6: the changelog's <Update label="X" description="Month D, YYYY">
    blocks with their `* ` bullets, newest first by version. Raises
    ValueError on an unparseable label or date, or a repeated label.'''
    releases: list[Release] = []
    current: Release | None = None
    for n, line in enumerate(text.split('\n'), start=1):
        m = UPDATE_RE.match(line)
        if m:
            label, described = m.groups()
            try:
                version_key(label)
                when = datetime.strptime(described, '%B %d, %Y').date()
            except ValueError as exc:
                raise ValueError(f'changelog line {n}: {exc}') from None
            current = Release(label, when, [])
            releases.append(current)
        elif line.strip() == '</Update>':
            current = None
        elif current is not None and (b := BULLET_RE.match(line)):
            current.bullets.append(b.group(1).strip())
    labels = [r.label for r in releases]
    if len(set(labels)) != len(labels):
        raise ValueError('changelog repeats a release label')
    return sorted(releases, key=lambda r: version_key(r.label), reverse=True)


def parse_llms(text: str) -> set[str]:
    '''R6.5: the code.claude.com page slugs llms.txt lists.'''
    return set(LLMS_RE.findall(text))


def is_platform(page: str) -> bool:
    return page.startswith(PLATFORM)


def page_file(page: str) -> str:
    '''The cache file a mapped page lives in: `/` becomes `_`, and platform
    pages take a `platform_` prefix, as in the 2.1.288 snapshot.'''
    if is_platform(page):
        return 'platform_' + page[len(PLATFORM):].replace('/', '_') + '.md'
    return page.replace('/', '_') + '.md'


def page_url(page: str, sources: dict[str, str]) -> str:
    '''The Markdown URL the refresh fetched a mapped page from.'''
    if is_platform(page):
        return sources['platform_base'] + page[len(PLATFORM):] + '.md'
    return sources['docs_base'] + page + '.md'
```

> Deviation: ruling 3: `parse_changelog` raises `ValueError` for an `<Update` opener
> that `UPDATE_RE` rejects, so a markup change cannot freeze the fetch gate's head
> (a09e62b). The interface list above does not name this raise.

- [x] **Step 6: Run the suite to see it pass.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: `29 passed` (+12).

- [x] **Step 7: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && [ "$(git branch --show-current)" = feat/cc-drift-stage1 ] && git add build/cc_guide/cc_fixtures.py build/cc_guide/docs.py build/cc_guide/test_docs.py && git commit -m "feat(cc_guide): parse release labels, the changelog and llms.txt

docs.py orders versions as integer tuples (R2.4's fourth component
included), parses the changelog's <Update label description> blocks and
bullets newest first (R6.6), reads llms.txt's code.claude.com slugs, and
names each mapped page's cache file and URL as the 2.1.288 snapshot
does.

Plan 38, Task 4.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: The guide (`guide.py`: sections, anchors, terms, stamp region)

**Files:**
- Modify: `build/cc_guide/cc_fixtures.py` (append)
- Create: `build/cc_guide/guide.py`
- Test: `build/cc_guide/test_guide.py`

**Interfaces:**
- Consumes: `blocks.fenced_lines` (Task 3) and `docs.version_key` (Task 4).
- Produces, for `state.py`, `baseline.py`, `lint.py`, `cli.py` and the fixtures:
  - `STAMP_OPEN = '<!-- cc-guide:stamp -->'` and `STAMP_CLOSE = '<!-- /cc-guide:stamp -->'`;
  - `STOP_TERMS` (22 entries), with `TERM_MIN, TERM_MAX = 3, 60`;
  - `Section(line: int, heading: str, parent: str | None, id: str | None, text: str, prose: str)`, a NamedTuple;
  - `sections(text: str) -> list[Section]`;
  - `anchor_problems(text: str) -> list[str]`, giving the lint's exact messages;
  - `text_hash(section_text: str) -> str` (`sha256:` plus 64 hex) and `code_spans(line: str) -> list[str]`;
  - `section_terms(section: Section, extra=(), exclude=()) -> set[str]`;
  - `stamp_bounds(text) -> tuple[int, int] | None`, `stamp_content(text) -> str | None`, `with_stamp(text, content) -> str` and `render_stamp(section_states: dict[str, dict]) -> str`.
- Fixtures: `GUIDE_IDS`, `FIXTURE_STAMP` and `guide_text(stamp=FIXTURE_STAMP)`. The fixture guide has two `### Reference ⚠` sections under different parents, a fenced `## not a heading inside a fence`, a 2-character span (`` `if` ``), a table and a json block.

`test_guide.py` also pins the real guide: it splits into R1.1's 38 IDs in order with no anchor problem, which is how the fence rule is pinned (R12.1). The stamp region does not exist yet (Task 12), and no test here needs it on the real guide.

- [x] **Step 1: Append to `build/cc_guide/cc_fixtures.py`,** after two blank lines:

```python
# The fixture guide's sections, in heading order. Two `Reference ⚠` headings
# sit under different parents, as the real guide's two `Frontmatter reference
# ⚠` headings do.
GUIDE_IDS = ['alpha.overview', 'alpha.reference', 'beta.overview', 'beta.reference']


FIXTURE_STAMP = ('> Checked against the Claude Code docs and changelog through 2.1.900 '
                 'on 2026-09-02; oldest full re-verification 2026-09-02, at 2.1.900.')


def guide_text(stamp: str = FIXTURE_STAMP) -> str:
    '''The fixture guide, its stamp region holding `stamp`. The markers come
    from guide.py, imported here so that blocks.py's tests run without it.'''
    from guide import STAMP_CLOSE, STAMP_OPEN
    return '\n'.join([
        '# Fixture guide',
        '',
        '**A guide for the fixture tool.**',
        '',
        STAMP_OPEN,
        stamp,
        STAMP_CLOSE,
        '',
        '> First verified at 2.1.900.',
        '',
        '## 1. Alpha',
        '<!-- cc: alpha.overview -->',
        '',
        'Alpha uses `ALPHA_TOOL`, `if` and `true`.',
        '',
        '### Reference ⚠',
        '<!-- cc: alpha.reference -->',
        '',
        'Set `ALPHA_ENV`; `` a `tick` inside `` stays one span.',
        '',
        FENCE + 'bash',
        '## not a heading inside a fence',
        'echo `NOT_A_TERM`',
        FENCE,
        '',
        '## 2. Beta',
        '<!-- cc: beta.overview -->',
        '',
        '| Setting | Meaning |',
        '|---|---|',
        '| `BETA_ENV` | on |',
        '',
        FENCE + 'json',
        '{"beta": true}',
        FENCE,
        '',
        '### Reference ⚠',
        '<!-- cc: beta.reference -->',
        '',
        '`BetaEvent` fires.',
        '',
    ])
```

- [x] **Step 2: Write the tests.** Create `build/cc_guide/test_guide.py`:

```python
'''Tests for guide.py: sections and anchors, text hashes, terms and the
stamp region (drift spec R1, R2.3, R3.6). Two tests read the real guide.'''
from pathlib import Path

import pytest

import guide
from cc_fixtures import FENCE, FIXTURE_STAMP, GUIDE_IDS, guide_text, isolated_home  # noqa: F401

REPO = Path(__file__).resolve().parents[2]
REAL_GUIDE = REPO / 'specs/guides/claude-code-customization-guide.md'

# The 38 section IDs of the drift spec's R1.1 table, in heading order. The
# conformance suite pins the same list; this suite imports nothing from
# build/ (R12.1), so it keeps its own copy.
R11_IDS = [
    'context.overview', 'mechanisms.overview',
    'skills.overview', 'skills.locations', 'skills.frontmatter',
    'skills.description', 'skills.listing-budget',
    'skills.progressive-disclosure', 'skills.arguments', 'skills.iterating',
    'commands.overview',
    'subagents.overview', 'subagents.frontmatter', 'subagents.tools',
    'subagents.models', 'subagents.isolation',
    'rules.overview', 'rules.claude-md', 'rules.hierarchy',
    'rules.rules-files', 'rules.auto-memory', 'rules.settings',
    'hooks.overview', 'hooks.events', 'hooks.exit-codes', 'hooks.handlers',
    'hooks.configuration', 'hooks.patterns', 'hooks.pitfalls',
    'lean.overview', 'lean.measure', 'lean.session-hygiene', 'lean.caching',
    'lean.model-routing', 'lean.mcp', 'lean.ceremony', 'lean.expensive-ops',
    'reading.overview',
]


def by_id(text):
    return {s.id: s for s in guide.sections(text)}


def test_sections_are_the_unfenced_level_two_and_three_headings():
    found = guide.sections(guide_text())
    assert [s.id for s in found] == GUIDE_IDS
    assert [s.parent for s in found] == [None, '## 1. Alpha', None, '## 2. Beta']


def test_a_level_two_section_runs_to_its_first_subsection_without_its_anchor():
    assert by_id(guide_text())['alpha.overview'].text == (
        '## 1. Alpha\n\nAlpha uses `ALPHA_TOOL`, `if` and `true`.\n')


def test_a_fenced_hash_line_stays_inside_its_section():
    reference = by_id(guide_text())['alpha.reference']
    assert '## not a heading inside a fence' in reference.text
    assert '## not a heading inside a fence' not in reference.prose


def test_anchor_problems_name_missing_malformed_repeated_and_stray_anchors():
    text = '\n'.join(['## A', '<!-- cc: a.one -->', '### B', 'body', '### C',
                      '<!-- cc: Bad_ID -->', '### D', '<!-- cc: a.one -->', '',
                      '<!-- cc: a.two -->'])
    assert guide.anchor_problems(text) == [
        "guide line 3: heading '### B' has no anchor on its next line",
        "guide line 6: malformed anchor '<!-- cc: Bad_ID -->'",
        'guide line 8: anchor a.one repeats line 2',
        'guide line 10: anchor is not directly under a heading',
    ]


def test_the_fixture_guide_has_no_anchor_problems():
    assert guide.anchor_problems(guide_text()) == []


def test_text_hash_ignores_rewrapping_but_not_words():
    h = guide.text_hash('## A\nOne two\nthree.')
    assert h.startswith('sha256:') and len(h) == len('sha256:') + 64
    assert guide.text_hash('## A   One\n\ntwo three.') == h
    assert guide.text_hash('## A\nOne two\nfour.') != h


@pytest.mark.parametrize('line, spans', [
    ('`if` and `foo`', ['if', 'foo']),
    ('| `shell` | `bash` or `powershell` for `` !`command` `` preprocessing |',
     ['shell', 'bash', 'powershell', '!`command`']),
    ('`` !`command` `` (inline) or a ```` ```! ```` fenced block runs',
     ['!`command`', '```!']),
    ('an unmatched `` run, then `x`', ['x']),
])
def test_code_spans_pair_backtick_runs_as_commonmark_does(line, spans):
    assert guide.code_spans(line) == spans


def test_terms_keep_three_to_sixty_characters_and_drop_stop_terms():
    assert guide.section_terms(by_id(guide_text())['alpha.overview']) == {'ALPHA_TOOL'}


def test_terms_skip_fenced_code_and_apply_extra_and_exclude_terms():
    reference = by_id(guide_text())['alpha.reference']
    assert guide.section_terms(reference) == {'ALPHA_ENV', 'a `tick` inside'}
    assert guide.section_terms(reference, extra=['alpha-mode'], exclude=['a `tick` inside']) == {
        'ALPHA_ENV', 'alpha-mode'}


def test_the_stamp_region_reads_and_rewrites_between_its_markers():
    text = guide_text()
    assert guide.stamp_content(text) == FIXTURE_STAMP
    rewritten = guide.with_stamp(text, '> New stamp.')
    assert guide.stamp_content(rewritten) == '> New stamp.'
    assert rewritten.replace('> New stamp.', FIXTURE_STAMP) == text


@pytest.mark.parametrize('broken', [
    lambda t: t.replace(guide.STAMP_CLOSE, ''),
    lambda t: t.replace(guide.STAMP_OPEN, guide.STAMP_OPEN + '\n' + guide.STAMP_OPEN),
    lambda t: t.replace(guide.STAMP_OPEN, '\0').replace(guide.STAMP_CLOSE, guide.STAMP_OPEN).replace('\0', guide.STAMP_CLOSE),
    lambda t: t.replace(guide.STAMP_OPEN, FENCE + '\n' + guide.STAMP_OPEN + '\n' + FENCE),
])
def test_a_missing_doubled_reversed_or_fenced_marker_means_no_region(broken):
    assert guide.stamp_content(broken(guide_text())) is None


def test_render_stamp_names_the_oldest_checked_and_audited():
    states = {
        'a.one': {'checked': {'release': '2.1.10', 'date': '2026-09-05'},
                  'audited': {'release': '2.1.9', 'date': '2026-08-01'}},
        'a.two': {'checked': {'release': '2.1.9', 'date': '2026-09-09'},
                  'audited': {'release': '2.1.10', 'date': '2026-09-05'}},
    }
    assert guide.render_stamp(states) == (
        '> Checked against the Claude Code docs and changelog through 2.1.9 on 2026-09-09; '
        'oldest full re-verification 2026-08-01, at 2.1.9.')


def test_real_guide_splits_into_the_38_r11_ids_in_order():
    assert [s.id for s in guide.sections(REAL_GUIDE.read_text(encoding='utf-8'))] == R11_IDS


def test_real_guide_has_no_anchor_problems():
    assert guide.anchor_problems(REAL_GUIDE.read_text(encoding='utf-8')) == []
```

- [x] **Step 3: Create the stub** `build/cc_guide/guide.py`, holding only `'''The guide: anchored sections, text hashes, terms and the stamp region (drift spec R1, R2.3, R3.6).'''`

- [x] **Step 4: Run the tests to see them fail.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf test_guide.py`
Expected: `20 failed`. Sixteen are `AttributeError: module 'guide' has no attribute …`: four each for `code_spans` and `stamp_content`, three for `anchor_problems`, two for `sections`, and one each for `render_stamp`, `section_terms` and `text_hash`. The other four are `ImportError: cannot import name 'STAMP_CLOSE' from 'guide'`, raised inside the fixture `guide_text`.

- [x] **Step 5: Implement.** Replace `build/cc_guide/guide.py` with:

```python
'''The guide: its anchored sections, their text hashes and terms, and the
stamp region (drift spec R1, R2.3, R3.6).'''
import hashlib
import re
from typing import NamedTuple

from blocks import fenced_lines
from docs import version_key

# A ## or ### ATX heading. The guide's sections are exactly these (R1.1).
HEADING_RE = re.compile(r'^(#{2,3})[ \t]')
ANCHOR_RE = re.compile(r'^<!-- cc: ([a-z0-9-]+(?:\.[a-z0-9-]+)+) -->$')
# Anything meant as an anchor, well-formed or not. The stamp markers do not
# match: `cc` must be followed by `:`.
ANCHOR_LIKE_RE = re.compile(r'^<!--\s*cc:')
STAMP_OPEN = '<!-- cc-guide:stamp -->'
STAMP_CLOSE = '<!-- /cc-guide:stamp -->'
BACKTICKS_RE = re.compile(r'`+')
TERM_MIN, TERM_MAX = 3, 60
# R3.6's generic words: its four examples, plus each single lowercase word or
# bare extension among the guide's terms that appeared in at least 5% of the
# blocks on the 2.1.288 snapshot's `terms` pages (measured 2026-10-04).
STOP_TERMS = frozenset({
    '.md', 'agent', 'auto', 'background', 'command', 'default', 'false', 'local',
    'low', 'model', 'name', 'paths', 'plan', 'project', 'prompt', 'run', 'settings',
    'shell', 'skills', 'tools', 'true', 'user',
})


class Section(NamedTuple):
    line: int            # 1-based line of the heading
    heading: str         # the heading line, stripped
    parent: str | None   # the enclosing ## heading line of a ###, else None
    id: str | None       # the anchor's ID, or None without a well-formed anchor
    text: str            # heading through the section's last line, anchor line excluded
    prose: str           # the same lines less fenced ones, for terms


def sections(text: str) -> list[Section]:
    '''The guide's ## and ### headings outside fenced code (R1.1), each with
    its anchor's ID and its text. A ## section runs to its first ###; the last
    section runs to the end of the file.'''
    lines = text.split('\n')
    fenced = fenced_lines(lines)
    starts = [i for i, line in enumerate(lines) if i not in fenced and HEADING_RE.match(line)]
    out: list[Section] = []
    parent = None
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        heading = lines[start].strip()
        is_sub = lines[start].startswith('###')
        if not is_sub:
            parent = heading
        anchor = ANCHOR_RE.match(lines[start + 1]) if start + 1 < end else None
        body = [i for i in range(start, end) if not (anchor and i == start + 1)]
        out.append(Section(start + 1, heading, parent if is_sub else None,
                           anchor.group(1) if anchor else None,
                           '\n'.join(lines[i] for i in body),
                           '\n'.join(lines[i] for i in body if i not in fenced)))
    return out


def anchor_problems(text: str) -> list[str]:
    '''R1.1 as the lint states it: every heading has exactly one well-formed
    anchor on its next line, and no anchor repeats or stands anywhere else.'''
    lines = text.split('\n')
    fenced = fenced_lines(lines)
    problems: list[str] = []
    under: set[int] = set()
    first: dict[str, int] = {}
    for s in sections(text):
        nxt = lines[s.line] if s.line < len(lines) else ''
        if s.id is not None:
            under.add(s.line)
            if s.id in first:
                problems.append(f'guide line {s.line + 1}: anchor {s.id} repeats line {first[s.id]}')
            else:
                first[s.id] = s.line + 1
        elif ANCHOR_LIKE_RE.match(nxt):
            under.add(s.line)
            problems.append(f'guide line {s.line + 1}: malformed anchor {nxt.strip()!r}')
        else:
            problems.append(f'guide line {s.line}: heading {s.heading!r} has no anchor on its next line')
    for i, line in enumerate(lines):
        if i not in fenced and i not in under and ANCHOR_LIKE_RE.match(line):
            problems.append(f'guide line {i + 1}: anchor is not directly under a heading')
    return problems


def text_hash(section_text: str) -> str:
    '''R2.3: `sha256:` over the section's text with every whitespace run
    collapsed to one space, so a rewrap changes nothing.'''
    collapsed = ' '.join(section_text.split())
    return 'sha256:' + hashlib.sha256(collapsed.encode('utf-8')).hexdigest()


def code_spans(line: str) -> list[str]:
    '''The inline code spans of one line, matched CommonMark-style: a run of
    n backticks closes on the next run of exactly n, and an unmatched run is
    literal. One space comes off each end when both ends have one.'''
    runs = list(BACKTICKS_RE.finditer(line))
    spans: list[str] = []
    i = 0
    while i < len(runs):
        size = len(runs[i].group())
        j = next((j for j in range(i + 1, len(runs)) if len(runs[j].group()) == size), None)
        if j is None:
            i += 1
            continue
        content = line[runs[i].end():runs[j].start()]
        if content.startswith(' ') and content.endswith(' ') and content.strip():
            content = content[1:-1]
        spans.append(content)
        i = j + 1
    return spans


def section_terms(section: Section, extra=(), exclude=()) -> set[str]:
    '''R3.6: the section's backticked spans outside fenced code, paired first
    and kept at 3-60 characters afterwards, minus STOP_TERMS, plus its
    extra_terms, minus its exclude_terms.'''
    spans = {span for line in section.prose.split('\n') for span in code_spans(line)}
    kept = {s for s in spans if TERM_MIN <= len(s) <= TERM_MAX} - STOP_TERMS
    return (kept | set(extra)) - set(exclude)


def stamp_bounds(text: str) -> tuple[int, int] | None:
    '''0-based line indexes of the stamp region's two markers, or None unless
    each appears once outside fenced code, open before close.'''
    lines = text.split('\n')
    fenced = fenced_lines(lines)
    opens = [i for i, line in enumerate(lines) if i not in fenced and line.strip() == STAMP_OPEN]
    closes = [i for i, line in enumerate(lines) if i not in fenced and line.strip() == STAMP_CLOSE]
    if len(opens) != 1 or len(closes) != 1 or closes[0] < opens[0]:
        return None
    return opens[0], closes[0]


def stamp_content(text: str) -> str | None:
    '''The lines between the stamp markers, or None without a region.'''
    bounds = stamp_bounds(text)
    if bounds is None:
        return None
    return '\n'.join(text.split('\n')[bounds[0] + 1:bounds[1]])


def with_stamp(text: str, content: str) -> str:
    '''The guide with its stamp region's content replaced (R1.2).'''
    bounds = stamp_bounds(text)
    if bounds is None:
        raise ValueError('the guide has no stamp region')
    lines = text.split('\n')
    return '\n'.join(lines[:bounds[0] + 1] + content.split('\n') + lines[bounds[1]:])


def render_stamp(section_states: dict[str, dict]) -> str:
    '''R1.2's generated sentence, from baseline.json's sections: the oldest
    `checked` (by release, then date) and the oldest `audited` (by date, then
    release). Both dates are the day the check or audit was done.'''
    checked = min((s['checked'] for s in section_states.values()),
                  key=lambda c: (version_key(c['release']), c['date']))
    audited = min((s['audited'] for s in section_states.values()),
                  key=lambda a: (a['date'], version_key(a['release'])))
    return (f"> Checked against the Claude Code docs and changelog through {checked['release']} "
            f"on {checked['date']}; oldest full re-verification {audited['date']}, "
            f"at {audited['release']}.")
```

- [x] **Step 6: Run the suite to see it pass.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: `49 passed` (+20).

- [x] **Step 7: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && [ "$(git branch --show-current)" = feat/cc-drift-stage1 ] && git add build/cc_guide/cc_fixtures.py build/cc_guide/guide.py build/cc_guide/test_guide.py && git commit -m "feat(cc_guide): read the guide's sections, terms and stamp region

guide.py splits the guide at ## and ### headings outside fences (R1.1),
reports anchor problems in the lint's words, hashes each section's text
with whitespace collapsed (R2.3), pairs backtick runs as CommonMark does
for R3.6's terms, and reads, renders and replaces R1.2's stamp region. A
real-guide test pins R1.1's 38 IDs in order.

Plan 38, Task 5.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Inputs and cache (`state.py`: manifest, baseline, `PROBES.md`, sources)

**Files:**
- Modify: `build/cc_guide/cc_fixtures.py` (append)
- Create: `build/cc_guide/state.py`
- Test: `build/cc_guide/test_state.py`

**Interfaces:**
- Consumes: `blocks.CELL_SPLIT_RE`, `docs.version_key`, and `guide.sections` and `guide.section_terms`.
- Produces, for `baseline.py`, `lint.py`, `check.py` and `cli.py`:
  - paths: `MANIFEST = 'build/cc_guide/manifest.toml'`, `BASELINE = 'build/cc_guide/baseline.json'` and `PROBES = 'build/cc_guide/PROBES.md'`;
  - bootstrap constants: `BOOTSTRAP_RELEASE = '2.1.288'` and `BOOTSTRAP_DATE = '2026-10-03'`;
  - `SetupError(Exception)`, which means exit 2;
  - `Source(repo: Path, ref: str | None = None)`, with `.label`, `.read(path) -> str | None` and `.require(path) -> str`. `require` raises `SetupError('<path>: not found in <label>')`. A bad ref raises `SetupError('<ref>: not a commit in <repo>')`;
  - `Group(sections: list[str], pages: dict[str, str])` and `Manifest(guide, sources, cadence, groups, terms, exclusions, probes)`, with `.pages()` and `.group_of()`;
  - `parse_manifest(text: str) -> Manifest` and `parse_baseline(text: str) -> dict`. Each raises one `SetupError` listing every problem;
  - `dump_baseline(state: dict) -> str`;
  - `ProbeRow(date, version, probe, outcome)` and `parse_probes(text: str | None) -> list[ProbeRow]`, where None means no rows;
  - `group_terms(manifest: Manifest, guide_text: str) -> dict[str, dict[str, set[str]]]`;
  - cache paths: `default_cache() -> Path`, `latest_docs(cache)`, `fetch_record(cache)`, `snapshot_docs(cache, release)` and `newest_changelog(cache) -> Path | None`.
- Fixtures: `MANIFEST_TOML` (groups `alpha` and `beta`), `write_tree(root, files)`, `git(repo, *args)` and `fixture_repo(root, files)`.

- [x] **Step 1: Append to `build/cc_guide/cc_fixtures.py`,** after two blank lines:

```python
MANIFEST_TOML = '\n'.join([
    '[guide]',
    "path = 'specs/guides/claude-code-customization-guide.md'",
    '',
    '[sources]',
    "docs_base = 'https://code.claude.com/docs/en/'",
    "llms = 'https://code.claude.com/docs/llms.txt'",
    "changelog = 'https://code.claude.com/docs/en/changelog.md'",
    "platform_base = 'https://platform.claude.com/docs/en/'",
    '',
    '[cadence]',
    'changelog_days = 7',
    'probe_days = 7',
    'audit_days = 30',
    '',
    '[groups.alpha]',
    "sections = ['alpha.overview', 'alpha.reference']",
    "all = ['tools']",
    "terms = ['env-vars']",
    '',
    '[groups.beta]',
    "sections = ['beta.overview', 'beta.reference']",
    "all = ['events']",
    "terms = ['env-vars', 'platform:pricing']",
    '',
    '[[exclusion]]',
    "page = 'whats-new/*'",
    "reason = 'Duplicates the changelog.'",
    '',
])


def write_tree(root, files: dict) -> None:
    '''Write {relative path: text} under root.'''
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')


def git(repo, *args: str) -> str:
    '''git in a fixture repo, with an identity and none of the caller's GIT_ variables.'''
    import os
    import subprocess
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    return subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                           '-c', 'commit.gpgsign=false', '-c', 'init.defaultBranch=main', *args],
                          cwd=repo, env=env, capture_output=True, text=True, check=True).stdout


def fixture_repo(root, files: dict):
    '''A git repo at root holding files, committed on main.'''
    root.mkdir(parents=True, exist_ok=True)
    write_tree(root, files)
    git(root, 'init', '-q')
    git(root, 'add', '-A')
    git(root, 'commit', '-qm', 'fixture')
    return root
```

- [x] **Step 2: Write the tests.** Create `build/cc_guide/test_state.py`:

```python
'''Tests for state.py: the manifest, the baseline, PROBES.md, the repo
source and the cache layout (drift spec R2, R6.1).'''
import json
from datetime import date

import pytest

import state
from cc_fixtures import (MANIFEST_TOML, fixture_repo, git, guide_text,  # noqa: F401
                         isolated_home)

STAMP = {'release': '2.1.900', 'date': '2026-09-02'}
SECTION = {'checked': STAMP, 'changed': '2.1.900', 'audited': STAMP, 'text_hash': 'sha256:' + 'a' * 64}


def baseline_text(**changes):
    raw = {'sections': {'alpha.overview': dict(SECTION)},
           'groups': {'alpha': {'blocks': {'tools': {'Tools': '0' * 16}}, 'snapshot': {'tools': '2.1.900'}}},
           'llms': ['tools']}
    raw.update(changes)
    return json.dumps(raw)


def test_the_fixture_manifest_parses_in_manifest_order():
    m = state.parse_manifest(MANIFEST_TOML)
    assert list(m.groups) == ['alpha', 'beta']
    assert m.groups['beta'] == state.Group(['beta.overview', 'beta.reference'],
                                           {'events': 'all', 'env-vars': 'terms', 'platform:pricing': 'terms'})
    assert m.pages() == ['tools', 'env-vars', 'events', 'platform:pricing']
    assert m.group_of()['alpha.reference'] == 'alpha'
    assert m.cadence == {'changelog_days': 7, 'probe_days': 7, 'audit_days': 30}
    assert (m.terms, m.probes) == ({}, {})
    assert m.exclusions == [('whats-new/*', 'Duplicates the changelog.')]


def test_every_manifest_problem_is_reported_at_once():
    text = (MANIFEST_TOML.replace('changelog_days = 7', 'changelog_days = 0')
            .replace("llms = 'https://", "llms = 'http://")
            .replace("all = ['events']", "all = ['events', 'whats-new/2026-w40']")
            .replace("sections = ['beta.overview', 'beta.reference']",
                     "sections = ['beta.overview', 'alpha.reference']")
            + "\n[stray]\nkey = 1\n")
    with pytest.raises(state.SetupError) as err:
        state.parse_manifest(text)
    assert str(err.value).split('\n') == [
        f'{state.MANIFEST}: unknown table or key {"stray"!r}',
        f'{state.MANIFEST}: [sources] llms must be an https URL',
        f'{state.MANIFEST}: [cadence] changelog_days must be a positive integer',
        f'{state.MANIFEST}: [groups.beta] alpha.reference is already in group alpha',
        f"{state.MANIFEST}: page whats-new/2026-w40 is mapped but matches exclusion 'whats-new/*'",
    ]


def test_a_page_listed_under_both_marks_is_a_problem():
    text = MANIFEST_TOML.replace("terms = ['env-vars']", "terms = ['env-vars', 'tools']")
    with pytest.raises(state.SetupError, match='tools is listed twice'):
        state.parse_manifest(text)


def test_invalid_toml_is_a_setup_error():
    with pytest.raises(state.SetupError, match='not valid TOML'):
        state.parse_manifest('[guide\n')


def test_section_terms_and_the_probe_registry_parse():
    text = MANIFEST_TOML + '\n'.join([
        "[sections.'alpha.overview']", "extra_terms = ['alpha-mode']", "exclude_terms = ['ALPHA_TOOL']",
        '', '[[probe]]', "id = 'agent-tools'", "sections = ['beta.reference']", "files = ['agents/a.md']", ''])
    m = state.parse_manifest(text)
    assert m.terms == {'alpha.overview': (['alpha-mode'], ['ALPHA_TOOL'])}
    assert m.probes == {'agent-tools': (['beta.reference'], ['agents/a.md'])}


def test_a_valid_baseline_parses_and_a_broken_one_is_a_setup_error():
    assert state.parse_baseline(baseline_text())['llms'] == ['tools']
    broken = {'sections': {'alpha.overview': {**SECTION, 'changed': '2.1.x'}}}
    with pytest.raises(state.SetupError, match='section alpha.overview'):
        state.parse_baseline(baseline_text(**broken))
    with pytest.raises(state.SetupError, match='group alpha'):
        state.parse_baseline(baseline_text(groups={'alpha': {'blocks': {'tools': {'Tools': 'xyz'}},
                                                             'snapshot': {}}}))
    with pytest.raises(state.SetupError, match='not valid JSON'):
        state.parse_baseline('{')


def test_dump_baseline_keeps_insertion_order_and_utf8():
    raw = {'sections': {}, 'groups': {'g': {'blocks': {'p': {'T › b': '1' * 16, 'T › a': '2' * 16}},
                                            'snapshot': {}}}, 'llms': []}
    text = state.dump_baseline(raw)
    assert text.index('T › b') < text.index('T › a')
    assert text.endswith('}\n')


def test_probe_rows_are_read_by_header_and_an_absent_file_has_none():
    assert state.parse_probes(None) == []
    text = '\n'.join(['# Probe log', '',
                      '| Date | Version | Binary | Probe | Outcome | Finding | Flags |',
                      '|---|---|---|---|---|---|---|',
                      '| 2026-10-10 | 2.1.290 | ~/.local/bin/claude | agent-tools | pass | ok | |',
                      '| 2026-10-11 | 2.1.290 | ~/.local/bin/claude | agent-tools | DIVERGES | no Grep | |', ''])
    assert state.parse_probes(text) == [
        state.ProbeRow(date(2026, 10, 10), '2.1.290', 'agent-tools', 'PASS'),
        state.ProbeRow(date(2026, 10, 11), '2.1.290', 'agent-tools', 'DIVERGES')]


def test_an_unreadable_probe_row_is_a_setup_error():
    text = '| Date | Version | Probe | Outcome |\n|---|---|---|---|\n| soon | 2.1.290 | x | PASS |\n'
    with pytest.raises(state.SetupError, match='unreadable row'):
        state.parse_probes(text)


def test_a_source_reads_the_working_tree_or_a_commit(tmp_path):
    repo = fixture_repo(tmp_path / 'repo', {'a.txt': 'committed\n'})
    (repo / 'a.txt').write_text('edited\n')
    assert state.Source(repo).read('a.txt') == 'edited\n'
    assert state.Source(repo, 'main').read('a.txt') == 'committed\n'
    assert state.Source(repo, 'main').read('absent.txt') is None
    with pytest.raises(state.SetupError, match='absent.txt: not found in main'):
        state.Source(repo, 'main').require('absent.txt')
    with pytest.raises(state.SetupError, match='no-such-ref: not a commit'):
        state.Source(repo, 'no-such-ref')


def test_group_terms_join_the_manifest_and_the_guide():
    m = state.parse_manifest(MANIFEST_TOML + "[sections.'alpha.overview']\nextra_terms = ['alpha-mode']\n")
    assert state.group_terms(m, guide_text()) == {
        'alpha': {'alpha.overview': {'ALPHA_TOOL', 'alpha-mode'},
                  'alpha.reference': {'ALPHA_ENV', 'a `tick` inside'}},
        'beta': {'beta.overview': {'BETA_ENV'}, 'beta.reference': {'BetaEvent'}},
    }


def test_the_newest_changelog_is_latest_else_the_bootstrap_snapshot(tmp_path):
    assert state.newest_changelog(tmp_path) is None
    boot = state.snapshot_docs(tmp_path, '2.1.288') / 'changelog.md'
    boot.parent.mkdir(parents=True)
    boot.write_text('x')
    assert state.newest_changelog(tmp_path) == boot
    latest = state.latest_docs(tmp_path) / 'changelog.md'
    latest.parent.mkdir(parents=True)
    latest.write_text('y')
    assert state.newest_changelog(tmp_path) == latest


def test_the_default_cache_follows_home(isolated_home):
    assert state.default_cache() == isolated_home / '.cache' / 'agent-skills' / 'cc-guide'
```

> Deviation: the eight `pytest.raises(match=…)` assertions compare messages
> exactly, per the Global Constraints; on the owner's call (ruling 5) the
> every-problem test gains a second mis-shaped manifest (53daf8d). No count change.

- [x] **Step 3: Create the stub** `build/cc_guide/state.py`, holding only `'''The detector's inputs and cache layout (drift spec R2, R6.1, Layout).'''`

- [x] **Step 4: Run the tests to see them fail.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf test_state.py`
Expected: `13 failed`, each `AttributeError: module 'state' has no attribute …`: four for `SetupError`, three for `parse_manifest`, and one each for `Source`, `default_cache`, `dump_baseline`, `newest_changelog`, `parse_baseline` and `parse_probes`.

- [x] **Step 5: Implement.** Replace `build/cc_guide/state.py` with:

```python
'''The detector's inputs and cache layout: manifest.toml (owner
configuration), baseline.json (tool state) and PROBES.md, read from the
working tree or a commit (drift spec R2, R6.1, Layout).'''
import fnmatch
import json
import re
import subprocess
import tomllib
from datetime import date
from pathlib import Path
from typing import NamedTuple

from blocks import CELL_SPLIT_RE
from docs import version_key
from guide import section_terms, sections

MANIFEST = 'build/cc_guide/manifest.toml'
BASELINE = 'build/cc_guide/baseline.json'
PROBES = 'build/cc_guide/PROBES.md'
MARKS = ('all', 'terms')
SOURCE_KEYS = ('docs_base', 'llms', 'changelog', 'platform_base')
CADENCE_KEYS = ('changelog_days', 'probe_days', 'audit_days')
ID_RE = re.compile(r'^[a-z0-9-]+(?:\.[a-z0-9-]+)+$')
GROUP_RE = re.compile(r'^[a-z0-9-]+$')
HASH_RE = re.compile(r'^[0-9a-f]{16}$')
TEXT_HASH_RE = re.compile(r'^sha256:[0-9a-f]{64}$')

# The bootstrap snapshot (R2.6): the 2026-10-03 refresh read the docs at
# 2.1.288 and checked them that day. 2.1.288 itself shipped on 2026-10-02.
BOOTSTRAP_RELEASE = '2.1.288'
BOOTSTRAP_DATE = '2026-10-03'


class SetupError(Exception):
    '''A missing or invalid input: exit 2, so a broken setup never looks clean.'''


class Source:
    '''Reads repo files from the working tree (ref None) or from a commit
    through `git show` (R6.1).'''

    def __init__(self, repo: Path, ref: str | None = None):
        self.repo, self.ref = repo, ref
        if ref is not None:
            ok = subprocess.run(['git', 'rev-parse', '--verify', '--quiet', f'{ref}^{{commit}}'],
                                cwd=repo, capture_output=True).returncode == 0
            if not ok:
                raise SetupError(f'{ref}: not a commit in {repo}')

    @property
    def label(self) -> str:
        return 'the working tree' if self.ref is None else self.ref

    def read(self, path: str) -> str | None:
        if self.ref is None:
            p = self.repo / path
            return p.read_text(encoding='utf-8') if p.is_file() else None
        proc = subprocess.run(['git', 'show', f'{self.ref}:{path}'], cwd=self.repo,
                              capture_output=True, encoding='utf-8')
        return proc.stdout if proc.returncode == 0 else None

    def require(self, path: str) -> str:
        text = self.read(path)
        if text is None:
            raise SetupError(f'{path}: not found in {self.label}')
        return text


class Group(NamedTuple):
    sections: list[str]
    pages: dict[str, str]  # page -> mark, in manifest order


class Manifest(NamedTuple):
    guide: str
    sources: dict[str, str]
    cadence: dict[str, int]
    groups: dict[str, Group]  # manifest order
    terms: dict[str, tuple[list[str], list[str]]]  # section -> (extra, exclude)
    exclusions: list[tuple[str, str]]  # (page pattern, reason)
    probes: dict[str, tuple[list[str], list[str]]]  # probe -> (sections, files)

    def pages(self) -> list[str]:
        '''Every mapped page once, in manifest order.'''
        return list(dict.fromkeys(p for g in self.groups.values() for p in g.pages))

    def group_of(self) -> dict[str, str]:
        return {sid: gid for gid, g in self.groups.items() for sid in g.sections}


def _strings(value) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) and v for v in value)


def parse_manifest(text: str) -> Manifest:
    '''manifest.toml (R2.2), validated. Raises SetupError listing every
    problem, so an invalid manifest exits 2.'''
    try:
        raw = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise SetupError(f'{MANIFEST}: not valid TOML ({exc})') from None
    problems: list[str] = []
    unknown = set(raw) - {'guide', 'sources', 'cadence', 'groups', 'sections', 'exclusion', 'probe'}
    problems += [f'unknown table or key {k!r}' for k in sorted(unknown)]
    guide_path = raw.get('guide', {}).get('path')
    if not isinstance(guide_path, str) or not guide_path:
        problems.append('[guide] path must be a non-empty string')
    sources = raw.get('sources', {})
    for k in SOURCE_KEYS:
        if not (isinstance(sources.get(k), str) and sources[k].startswith('https://')):
            problems.append(f'[sources] {k} must be an https URL')
    cadence = raw.get('cadence', {})
    for k in CADENCE_KEYS:
        v = cadence.get(k)
        if not (isinstance(v, int) and not isinstance(v, bool) and v > 0):
            problems.append(f'[cadence] {k} must be a positive integer')
    groups: dict[str, Group] = {}
    owner: dict[str, str] = {}
    raw_groups = raw.get('groups')
    if not isinstance(raw_groups, dict) or not raw_groups:
        problems.append('[groups] must hold at least one group')
        raw_groups = {}
    for gid, g in raw_groups.items():
        where = f'[groups.{gid}]'
        if not GROUP_RE.match(gid):
            problems.append(f'{where} group IDs are [a-z0-9-]')
        if not isinstance(g, dict) or set(g) - {'sections', 'all', 'terms'}:
            problems.append(f'{where} holds only sections, all and terms')
            continue
        secs = g.get('sections')
        if not _strings(secs) or not secs:
            problems.append(f'{where} sections must be a non-empty list of section IDs')
            secs = []
        for sid in secs:
            if not ID_RE.match(sid):
                problems.append(f'{where} {sid!r} is not a section ID')
            elif sid in owner:
                problems.append(f'{where} {sid} is already in group {owner[sid]}')
            else:
                owner[sid] = gid
        pages: dict[str, str] = {}
        for mark in MARKS:
            listed = g.get(mark, [])
            if not _strings(listed):
                problems.append(f'{where} {mark} must be a list of pages')
                continue
            for page in listed:
                if page in pages:
                    problems.append(f'{where} {page} is listed twice')
                pages[page] = mark
        if not pages:
            problems.append(f'{where} maps no page')
        groups[gid] = Group(list(secs), pages)
    terms: dict[str, tuple[list[str], list[str]]] = {}
    for sid, t in raw.get('sections', {}).items():
        extra, exclude = t.get('extra_terms', []), t.get('exclude_terms', [])
        if sid not in owner:
            problems.append(f'[sections.{sid!r}] is not in any group')
        if set(t) - {'extra_terms', 'exclude_terms'} or not _strings(extra) or not _strings(exclude):
            problems.append(f'[sections.{sid!r}] holds only extra_terms and exclude_terms, as lists')
            continue
        terms[sid] = (extra, exclude)
    exclusions: list[tuple[str, str]] = []
    for e in raw.get('exclusion', []):
        page, reason = e.get('page'), e.get('reason')
        if not (isinstance(page, str) and page and isinstance(reason, str) and reason):
            problems.append('[[exclusion]] needs a page pattern and a reason')
            continue
        exclusions.append((page, reason))
    mapped = list(dict.fromkeys(p for g in groups.values() for p in g.pages))
    for page in mapped:
        for pattern, _ in exclusions:
            if fnmatch.fnmatchcase(page, pattern):
                problems.append(f'page {page} is mapped but matches exclusion {pattern!r}')
    probes: dict[str, tuple[list[str], list[str]]] = {}
    for p in raw.get('probe', []):
        pid, secs, files = p.get('id'), p.get('sections'), p.get('files', [])
        if not (isinstance(pid, str) and pid) or pid in probes:
            problems.append('[[probe]] needs a unique id')
            continue
        if not _strings(secs) or not secs or any(s not in owner for s in secs) or not _strings(files):
            problems.append(f'[[probe]] {pid}: sections must name grouped sections; files is a list')
            continue
        probes[pid] = (secs, files)
    if problems:
        raise SetupError('\n'.join(f'{MANIFEST}: {p}' for p in problems))
    return Manifest(guide_path, dict(sources), dict(cadence), groups, terms, exclusions, probes)


def _iso(value) -> bool:
    try:
        date.fromisoformat(value)
        return isinstance(value, str)
    except (TypeError, ValueError):
        return False


def _label(value) -> bool:
    try:
        version_key(value)
        return True
    except (TypeError, ValueError):
        return False


def _stamp(value) -> bool:
    return (isinstance(value, dict) and set(value) == {'release', 'date'}
            and _label(value['release']) and _iso(value['date']))


def parse_baseline(text: str) -> dict:
    '''baseline.json (R2.3), validated. Raises SetupError listing every
    problem, so an invalid baseline exits 2.'''
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SetupError(f'{BASELINE}: not valid JSON ({exc})') from None
    problems: list[str] = []
    if (not isinstance(raw, dict) or set(raw) != {'sections', 'groups', 'llms'}
            or not isinstance(raw['sections'], dict) or not isinstance(raw['groups'], dict)):
        raise SetupError(f'{BASELINE}: holds exactly sections, groups and llms')
    for sid, s in raw['sections'].items():
        ok = (isinstance(s, dict) and set(s) == {'checked', 'changed', 'audited', 'text_hash'}
              and _stamp(s['checked']) and _stamp(s['audited']) and _label(s['changed'])
              and isinstance(s['text_hash'], str) and TEXT_HASH_RE.match(s['text_hash']))
        if not ok:
            problems.append(f'section {sid}: needs checked, changed, audited and text_hash')
    for gid, g in raw['groups'].items():
        ok = (isinstance(g, dict) and set(g) == {'blocks', 'snapshot'}
              and isinstance(g['blocks'], dict) and isinstance(g['snapshot'], dict))
        if ok:
            ok = all(isinstance(keys, dict) and all(isinstance(h, str) and HASH_RE.match(h)
                                                    for h in keys.values())
                     for keys in g['blocks'].values())
            ok = ok and all(_label(r) for r in g['snapshot'].values())
        if not ok:
            problems.append(f'group {gid}: needs blocks (page -> key -> hash) and snapshot (page -> release)')
    if not _strings(raw['llms']):
        problems.append('llms must be a list of slugs')
    if problems:
        raise SetupError('\n'.join(f'{BASELINE}: {p}' for p in problems))
    return raw


def dump_baseline(state: dict) -> str:
    '''baseline.json's text: insertion order kept, so diffs stay readable.'''
    return json.dumps(state, indent=1, ensure_ascii=False) + '\n'


class ProbeRow(NamedTuple):
    date: date
    version: str
    probe: str
    outcome: str


def parse_probes(text: str | None) -> list[ProbeRow]:
    '''PROBES.md's rows (R10.6), in file order. The table's header names the
    columns; date, version, probe and outcome are read. An absent file has no
    rows: Stage 5 creates it, and until then no probe is registered.'''
    if text is None:
        return []
    rows: list[ProbeRow] = []
    header: list[str] | None = None
    for line in text.split('\n'):
        s = line.strip()
        if not s.startswith('|'):
            header = None
            continue
        cells = [c.strip() for c in CELL_SPLIT_RE.split(s.strip('|'))]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if set(s) <= set('|-: '):
            continue
        row = dict(zip(header, cells))
        try:
            version_key(row['version'])
            rows.append(ProbeRow(date.fromisoformat(row['date']), row['version'],
                                 row['probe'], row['outcome'].upper()))
        except (KeyError, ValueError):
            raise SetupError(f'{PROBES}: unreadable row {s!r}') from None
    return rows


def group_terms(manifest: Manifest, guide_text: str) -> dict[str, dict[str, set[str]]]:
    '''Per group, per section in group order, the section's terms (R3.6).'''
    by_id = {s.id: s for s in sections(guide_text) if s.id}
    out: dict[str, dict[str, set[str]]] = {}
    for gid, g in manifest.groups.items():
        out[gid] = {}
        for sid in g.sections:
            extra, exclude = manifest.terms.get(sid, ([], []))
            out[gid][sid] = section_terms(by_id[sid], extra, exclude) if sid in by_id else set(extra)
    return out


def default_cache() -> Path:
    '''~/.cache/agent-skills/cc-guide, resolved from HOME at call time.'''
    return Path.home() / '.cache' / 'agent-skills' / 'cc-guide'


def latest_docs(cache: Path) -> Path:
    return cache / 'latest' / 'docs'


def fetch_record(cache: Path) -> Path:
    '''The last fetch's time and changelog head, beside latest/docs (R6.4).'''
    return cache / 'latest' / 'fetch.json'


def snapshot_docs(cache: Path, release: str) -> Path:
    return cache / release / 'docs'


def newest_changelog(cache: Path) -> Path | None:
    '''The newest cached changelog: latest/, else the bootstrap snapshot.
    Fixed paths only; release directories are never globbed.'''
    for path in (latest_docs(cache) / 'changelog.md',
                 snapshot_docs(cache, BOOTSTRAP_RELEASE) / 'changelog.md'):
        if path.is_file():
            return path
    return None
```

> Deviation: ruling 5: `parse_manifest` checks each table's shape first, so a
> mis-shaped table is a listed problem, not an `AttributeError` (53daf8d). Ruling 6
> deferred the probe validator's R10.1/R10.2 conflict to Stage 5 (deferred items).

- [x] **Step 6: Run the suite to see it pass.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: `62 passed` (+13).

- [x] **Step 7: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && [ "$(git branch --show-current)" = feat/cc-drift-stage1 ] && git add build/cc_guide/cc_fixtures.py build/cc_guide/state.py build/cc_guide/test_state.py && git commit -m "feat(cc_guide): read and validate the manifest, baseline and probe log

state.py parses manifest.toml (R2.2) and baseline.json (R2.3), each
raising one SetupError that lists every problem, so a broken input exits
2. It reads files from the working tree or a commit (R6.1) and PROBES.md
rows by header name; an absent PROBES.md has no rows. It also builds
each group's terms and names the cache layout under
~/.cache/agent-skills.

Plan 38, Task 6.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Bookkeeping (`baseline.py`: R7 without `cite`, R2.4, R11.1)

**Files:**
- Modify: `build/cc_guide/cc_fixtures.py` (append)
- Create: `build/cc_guide/baseline.py`
- Test: `build/cc_guide/test_baseline.py`

**Interfaces:**
- Consumes: `blocks` (`SEP`, `block_hash`, `page_blocks`, `select`), `docs` (`is_platform`, `page_file`, `parse_llms`, `version_key`), `guide` (`anchor_problems`, `render_stamp`, `sections`, `text_hash`, `with_stamp`) and `state` (`Manifest`, `SetupError`, `group_terms`).
- Produces, for `cli.py`. Every function returns new state (a deep copy) and writes no file:
  - `OLD_GUIDE_PATH = 'specs/claude-code-customization-guide.md'`, `JULY = ('91474f6', '2.1.219')` and `REFRESH = ('c33bc99', '2.1.288')`;
  - `next_changed(newest: str, citer_stamps) -> str` (R2.4);
  - `derive_changed(july: str, refresh: str, current: str) -> dict[str, str]` (R11.1);
  - `check_ids(manifest, guide_text) -> None` and `select_blocks(text, mark, terms) -> dict[str, str]`;
  - `init(manifest, guide_text, docs: Path, release: str, day: str, changed: dict[str, str]) -> dict`;
  - `accept(state, guide_text, ids, substantive: bool, newest: str, citer_stamps=None) -> dict`;
  - `advance(state, ids, to: str, labels: set[str], day: str) -> dict`;
  - `audited(state, manifest, group: str, release: str, day: str) -> dict`;
  - `rebaseline(state, manifest, guide_text, group: str, refs: list[str], latest: Path, release: str) -> tuple[dict, list[str], list[str]]`, returning the new state, the pages to snapshot, and notes;
  - `stamp(guide_text: str, state: dict) -> str`.
- Fixtures: `TOOLS_PAGE`, `EVENTS_PAGE`, `DOCS` (the fixture docs directory, keyed by cache file name), `FIXTURE_RELEASE`, `FIXTURE_DAY`, `FIXTURE_CHANGED`, the `docs_dir` fixture and `fixture_state(folder)`.

`test_r11_derivation_from_the_real_history` reads `91474f6` and `c33bc99` from this repo's history. It expects six sections at 2.1.219 (`lean.ceremony`, `lean.overview`, `rules.auto-memory`, `rules.overview`, `skills.description`, `skills.overview`) and 32 at 2.1.288, and it skips with a reason in a shallow clone.

- [x] **Step 1: Append to `build/cc_guide/cc_fixtures.py`,** after two blank lines:

```python
TOOLS_PAGE = '\n'.join([
    '> ## Documentation Index',
    '> Fetch the complete documentation index at: https://docs.example.invalid/llms.txt',
    '',
    '# Tools',
    '',
    'The `ALPHA_TOOL` runs alpha jobs.',
    '',
    '## Options',
    '',
    '| Option | Effect |',
    '|---|---|',
    '| `--fast` | Runs fast. |',
    '',
])


EVENTS_PAGE = '\n'.join([
    '# Events',
    '',
    '`BetaEvent` fires on beta.',
    '',
    '## Payload',
    '',
    'The payload carries `BETA_ENV`.',
    '',
])


# The fixture docs directory, file name -> text, named as the cache names them.
DOCS = {
    'tools.md': TOOLS_PAGE,
    'events.md': EVENTS_PAGE,
    'env-vars.md': ENV_PAGE,
    'platform_pricing.md': PLATFORM_PAGE,
    'changelog.md': CHANGELOG_TEXT,
    'llms.txt': LLMS_TEXT,
}


# The fixture baseline: every section checked and audited at 2.1.900 on
# 2026-09-02, so 2.1.901 (2026-09-20) and 2.1.902 (2026-10-01) are untriaged.
FIXTURE_RELEASE, FIXTURE_DAY = '2.1.900', '2026-09-02'


FIXTURE_CHANGED = {'alpha.overview': '2.1.900', 'alpha.reference': '2.1.899',
                   'beta.overview': '2.1.900', 'beta.reference': '2.1.900'}


@pytest.fixture
def docs_dir(tmp_path):
    '''The fixture docs as a local directory, named as the cache names them.'''
    folder = tmp_path / 'docs'
    write_tree(folder, DOCS)
    return folder


def fixture_state(folder) -> dict:
    '''The baseline init builds for the fixture guide over a docs directory.'''
    import baseline
    import state
    return baseline.init(state.parse_manifest(MANIFEST_TOML), guide_text(), folder,
                         FIXTURE_RELEASE, FIXTURE_DAY, FIXTURE_CHANGED)
```

> Deviation: ruling 1's paraphrase applies to `TOOLS_PAGE`'s preamble line (Task 3,
> Step 1).

- [x] **Step 2: Write the tests.** Create `build/cc_guide/test_baseline.py`:

```python
'''Tests for baseline.py: R2.4's stamp rule, R11.1's derivation, and each
`baseline` subcommand's effect on the state (drift spec R7). The write sets
on disk are test_cli.py's.'''
import subprocess
from pathlib import Path

import pytest

import baseline
import guide
import state
from cc_fixtures import (DOCS, FIXTURE_CHANGED, GUIDE_IDS, MANIFEST_TOML, docs_dir,  # noqa: F401
                         fixture_state, guide_text, isolated_home, write_tree)

REPO = Path(__file__).resolve().parents[2]
MANIFEST = state.parse_manifest(MANIFEST_TOML)
ENV = 'Environment variables'


def unanchored(text):
    return '\n'.join(line for line in text.split('\n') if not line.startswith('<!-- cc: '))


@pytest.mark.parametrize('newest, citers, expected', [
    ('2.1.300', [], '2.1.300'),
    ('2.1.300', ['2.1.299'], '2.1.300'),
    ('2.1.300', ['2.1.300'], '2.1.300.1'),
    ('2.1.300', ['2.1.299', '2.1.300.1'], '2.1.300.2'),
    ('2.1.300', ['2.1.301'], '2.1.301.1'),
])
def test_a_new_changed_exceeds_every_citer_stamp(newest, citers, expected):
    assert baseline.next_changed(newest, citers) == expected


def test_derive_changed_aligns_by_parent_and_heading():
    refresh = unanchored(guide_text())
    july = refresh.replace('Set `ALPHA_ENV`;', 'Set `OLD_ENV`;')
    assert july != refresh
    assert baseline.derive_changed(july, refresh, guide_text()) == {
        'alpha.overview': '2.1.219', 'alpha.reference': '2.1.288',
        'beta.overview': '2.1.219', 'beta.reference': '2.1.219'}


def test_derive_changed_refuses_a_section_the_refresh_lacks():
    current = guide_text().replace('### Reference ⚠\n<!-- cc: beta.reference', '### Renamed\n<!-- cc: beta.reference')
    with pytest.raises(state.SetupError, match='beta.reference'):
        baseline.derive_changed(unanchored(guide_text()), unanchored(guide_text()), current)


def history(ref):
    proc = subprocess.run(['git', 'show', f'{ref}:{baseline.OLD_GUIDE_PATH}'], cwd=REPO,
                          capture_output=True, encoding='utf-8')
    if proc.returncode != 0:
        pytest.skip(f'{ref} is not in this clone (a shallow clone?)')
    return proc.stdout


def test_r11_derivation_from_the_real_history():
    changed = baseline.derive_changed(history(baseline.JULY[0]), history(baseline.REFRESH[0]),
                                      (REPO / 'specs/guides/claude-code-customization-guide.md').read_text())
    assert sorted(sid for sid, release in changed.items() if release == '2.1.219') == [
        'lean.ceremony', 'lean.overview', 'rules.auto-memory', 'rules.overview',
        'skills.description', 'skills.overview']
    assert sum(1 for release in changed.values() if release == '2.1.288') == 32


def test_init_baselines_each_groups_selected_blocks(docs_dir):
    s = fixture_state(docs_dir)
    assert list(s['sections']) == GUIDE_IDS
    assert s['sections']['alpha.reference']['changed'] == '2.1.899'
    assert s['sections']['alpha.overview']['checked'] == {'release': '2.1.900', 'date': '2026-09-02'}
    assert {p: list(keys) for p, keys in s['groups']['alpha']['blocks'].items()} == {
        'tools': ['Tools', 'Tools › Options', 'Tools › Options › `--fast`'],
        'env-vars': [f'{ENV} › `ALPHA_ENV`', f'{ENV} › `ALPHA_ENV`#2', f'{ENV} › Examples']}
    assert {p: list(keys) for p, keys in s['groups']['beta']['blocks'].items()} == {
        'events': ['Events', 'Events › Payload'],
        'env-vars': [f'{ENV} › `BETA_ENV`'],
        'platform:pricing': ['(intro)', 'Rates']}
    assert s['groups']['beta']['snapshot'] == {'events': '2.1.900', 'env-vars': '2.1.900',
                                               'platform:pricing': '2.1.900'}
    assert s['llms'] == ['env-vars', 'events', 'plugins/components', 'tools']


def test_init_leaves_a_page_the_snapshot_lacks_unbaselined(docs_dir):
    (docs_dir / 'events.md').unlink()
    s = fixture_state(docs_dir)
    assert 'events' not in s['groups']['beta']['blocks']
    assert 'events' not in s['groups']['beta']['snapshot']


def test_init_refuses_anchors_that_disagree_with_the_manifest(docs_dir):
    text = guide_text().replace('<!-- cc: beta.reference -->', '<!-- cc: beta.other -->')
    with pytest.raises(state.SetupError, match='beta.reference is in manifest.toml but not the guide'):
        baseline.init(MANIFEST, text, docs_dir, '2.1.900', '2026-09-02', FIXTURE_CHANGED)


def test_accept_records_the_hash_and_substantive_also_sets_changed(docs_dir):
    s = fixture_state(docs_dir)
    edited = guide_text().replace('Alpha uses', 'Alpha now uses')
    editorial = baseline.accept(s, edited, ['alpha.overview'], False, '2.1.902')
    by_id = {x.id: x for x in guide.sections(edited)}
    assert editorial['sections']['alpha.overview']['text_hash'] == guide.text_hash(by_id['alpha.overview'].text)
    assert editorial['sections']['alpha.overview']['changed'] == '2.1.900'
    substantive = baseline.accept(s, edited, ['alpha.overview'], True, '2.1.902')
    assert substantive['sections']['alpha.overview']['changed'] == '2.1.902'
    bumped = baseline.accept(s, edited, ['alpha.overview'], True, '2.1.902', {'alpha.overview': ['2.1.902']})
    assert bumped['sections']['alpha.overview']['changed'] == '2.1.902.1'
    assert s == fixture_state(docs_dir)


def test_advance_sets_checked_on_the_day_of_the_check(docs_dir):
    s = fixture_state(docs_dir)
    labels = {'2.1.900', '2.1.901', '2.1.902'}
    moved = baseline.advance(s, ['beta.overview'], '2.1.902', labels, '2026-10-04')
    assert moved['sections']['beta.overview']['checked'] == {'release': '2.1.902', 'date': '2026-10-04'}
    assert moved['sections']['beta.reference'] == s['sections']['beta.reference']
    with pytest.raises(state.SetupError, match='not a release'):
        baseline.advance(s, ['beta.overview'], '2.1.950', labels, '2026-10-04')
    with pytest.raises(state.SetupError, match='older than the checked release of beta.overview'):
        baseline.advance(moved, ['beta.overview'], '2.1.901', labels, '2026-10-05')
    with pytest.raises(state.SetupError, match='unknown section IDs: beta.zzz'):
        baseline.advance(s, ['beta.zzz'], '2.1.902', labels, '2026-10-04')


def test_audited_sets_audited_and_checked_for_the_groups_sections(docs_dir):
    s = fixture_state(docs_dir)
    done = baseline.audited(s, MANIFEST, 'alpha', '2.1.902', '2026-10-04')
    for sid in ('alpha.overview', 'alpha.reference'):
        assert done['sections'][sid]['audited'] == {'release': '2.1.902', 'date': '2026-10-04'}
        assert done['sections'][sid]['checked'] == {'release': '2.1.902', 'date': '2026-10-04'}
    assert done['sections']['beta.overview'] == s['sections']['beta.overview']
    with pytest.raises(state.SetupError, match='unknown group gamma'):
        baseline.audited(s, MANIFEST, 'gamma', '2.1.902', '2026-10-04')


def latest_from(tmp_path, **edits):
    folder = tmp_path / 'latest'
    write_tree(folder, {**DOCS, **edits})
    return folder


def test_a_full_rebaseline_rehashes_drops_deselected_and_refreshes_llms(tmp_path, docs_dir):
    s = fixture_state(docs_dir)
    s['groups']['alpha']['blocks']['env-vars']['Environment variables'] = '0' * 16
    latest = latest_from(tmp_path, **{
        'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches'),
        'llms.txt': DOCS['llms.txt'] + '- [New](https://code.claude.com/docs/en/new-page.md): New.\n'})
    new, pages, notes = baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', [], latest, '2.1.902')
    fresh = fixture_state(latest)
    assert new['groups']['alpha']['blocks'] == fresh['groups']['alpha']['blocks']
    assert new['groups']['alpha']['blocks']['tools']['Tools'] != s['groups']['alpha']['blocks']['tools']['Tools']
    assert new['groups']['alpha']['snapshot'] == {'tools': '2.1.902', 'env-vars': '2.1.902'}
    assert new['groups']['beta'] == s['groups']['beta']
    assert (pages, notes) == (['tools', 'env-vars'], [])
    assert new['llms'] == ['env-vars', 'events', 'new-page', 'plugins/components', 'tools']


def test_a_listed_rebaseline_touches_only_the_listed_blocks(tmp_path, docs_dir):
    s = fixture_state(docs_dir)
    latest = latest_from(tmp_path, **{'tools.md': DOCS['tools.md'].replace('Runs fast.', 'Runs faster.')
                                      .replace('runs alpha jobs', 'runs alpha batches')})
    row = 'Tools › Options › `--fast`'
    new, pages, _ = baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', ['tools › ' + row], latest, '2.1.902')
    old_tools, new_tools = s['groups']['alpha']['blocks']['tools'], new['groups']['alpha']['blocks']['tools']
    assert new_tools[row] != old_tools[row]
    assert new_tools['Tools'] == old_tools['Tools']
    assert list(new_tools) == list(old_tools)
    assert pages == ['tools']


def test_rebaseline_keeps_a_missing_page_and_drops_an_unmapped_one(tmp_path, docs_dir):
    s = fixture_state(docs_dir)
    s['groups']['beta']['blocks']['retired'] = {'Retired': '1' * 16}
    latest = latest_from(tmp_path)
    (latest / 'events.md').unlink()
    new, pages, notes = baseline.rebaseline(s, MANIFEST, guide_text(), 'beta', [], latest, '2.1.902')
    assert new['groups']['beta']['blocks']['events'] == s['groups']['beta']['blocks']['events']
    assert 'retired' not in new['groups']['beta']['blocks']
    assert pages == ['env-vars', 'platform:pricing']
    assert notes == ['events: missing page; kept its entries. Drop or remap it in manifest.toml first',
                     'retired: no longer mapped to beta; dropped its baselined blocks']


def test_stamp_regenerates_only_the_region(docs_dir):
    s = baseline.advance(fixture_state(docs_dir), GUIDE_IDS, '2.1.902', {'2.1.902'}, '2026-10-04')
    stamped = baseline.stamp(guide_text(), s)
    assert guide.stamp_content(stamped) == guide.render_stamp(s['sections'])
    assert stamped == guide_text(guide.render_stamp(s['sections']))
```

> Deviation: the six `match=` assertions compare messages exactly (1653ef1). On the
> owner's call (ruling 7), the listed-rebaseline test is renamed and gains the
> refusal and a snapshot assertion (6822f01). The final review added an unlisted
> `--slow` row, so a whole-page replace fails it (bfbc2d5). No count change.

- [x] **Step 3: Create the stub** `build/cc_guide/baseline.py`, holding only `'''`baseline`: the only writer of baseline.json and the guide's stamp region (drift spec R7).'''`

- [x] **Step 4: Run the tests to see them fail.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf test_baseline.py`
Expected: `18 failed`, each `AttributeError: module 'baseline' has no attribute …`: nine for `init` (through `fixture_state`), five for `next_changed`, three for `derive_changed` and one for `advance`.

- [x] **Step 5: Implement.** Replace `build/cc_guide/baseline.py` with:

```python
'''`baseline`: the only writer of baseline.json and of the guide's stamp
region (drift spec R7). These functions return new state; cli.py writes it
to the working tree, and nothing is committed. `cite` is Stage 2's.'''
import copy
from pathlib import Path

from blocks import SEP, block_hash, page_blocks, select
from docs import is_platform, page_file, parse_llms, version_key
from guide import anchor_problems, render_stamp, sections, text_hash, with_stamp
from state import Manifest, SetupError, group_terms

# R11.1: the July guide (verified at 2.1.219) and the refresh (at 2.1.288),
# both read at the guide's path before 79ad04f moved it.
OLD_GUIDE_PATH = 'specs/claude-code-customization-guide.md'
JULY = ('91474f6', '2.1.219')
REFRESH = ('c33bc99', '2.1.288')


def next_changed(newest: str, citer_stamps) -> str:
    '''R2.4: the newest known release, unless that would not exceed the
    highest review stamp among the section's citers; then that stamp with a
    fourth component added or incremented.'''
    top = max(citer_stamps, key=version_key, default=None)
    if top is None or version_key(newest) > version_key(top):
        return newest
    parts = top.split('.')
    if len(parts) == 3:
        return top + '.1'
    return '.'.join(parts[:3] + [str(int(parts[3]) + 1)])


def derive_changed(july: str, refresh: str, current: str) -> dict[str, str]:
    '''R11.1: each section's `changed`. A section whose text is the same in
    the July guide and the refresh, aligned by (parent ##, heading) and
    compared with whitespace collapsed, keeps July's release; every other
    section takes the refresh's.'''
    def by_key(text: str) -> dict:
        return {(s.parent, s.heading): ' '.join(s.text.split()) for s in sections(text)}
    old, new = by_key(july), by_key(refresh)
    out = {}
    for s in sections(current):
        key = (s.parent, s.heading)
        if key not in new:
            raise SetupError(f'R11.1: section {s.id} ({s.heading!r}) is not in the {REFRESH[0]} guide')
        out[s.id] = JULY[1] if old.get(key) == new[key] else REFRESH[1]
    return out


def check_ids(manifest: Manifest, guide_text: str) -> None:
    '''init and rebaseline need a guide whose anchors match the manifest.'''
    problems = anchor_problems(guide_text)
    anchors = {s.id for s in sections(guide_text) if s.id}
    problems += [f'section {sid} is in manifest.toml but not the guide'
                 for sid in sorted(set(manifest.group_of()) - anchors)]
    problems += [f'section {sid} is in the guide but not manifest.toml'
                 for sid in sorted(anchors - set(manifest.group_of()))]
    if problems:
        raise SetupError('\n'.join(problems))


def select_blocks(text: str, mark: str, terms: set[str]) -> dict[str, str]:
    '''One page's selected blocks, key -> hash, in page order.'''
    found = page_blocks(text)
    return {k: block_hash(found[k]) for k in select(found, mark, terms)}


def init(manifest: Manifest, guide_text: str, docs: Path, release: str, day: str,
         changed: dict[str, str]) -> dict:
    '''R2.6: the initial baseline, from a snapshot directory and never from
    live docs. A mapped page the snapshot lacks stays unbaselined, so its
    selected blocks report as new.'''
    check_ids(manifest, guide_text)
    terms = group_terms(manifest, guide_text)
    llms = docs / 'llms.txt'
    state: dict = {'sections': {}, 'groups': {},
                   'llms': sorted(parse_llms(llms.read_text(encoding='utf-8'))) if llms.is_file() else []}
    for s in sections(guide_text):
        state['sections'][s.id] = {'checked': {'release': release, 'date': day},
                                   'changed': changed[s.id],
                                   'audited': {'release': release, 'date': day},
                                   'text_hash': text_hash(s.text)}
    for gid, group in manifest.groups.items():
        watched = set().union(*terms[gid].values())
        blocks, snapshot = {}, {}
        for page, mark in group.pages.items():
            path = docs / page_file(page)
            if path.is_file():
                blocks[page] = select_blocks(path.read_text(encoding='utf-8'), mark, watched)
                snapshot[page] = release
        state['groups'][gid] = {'blocks': blocks, 'snapshot': snapshot}
    return state


def known(state: dict, ids) -> None:
    unknown = [sid for sid in ids if sid not in state['sections']]
    if unknown:
        raise SetupError(f'unknown section IDs: {", ".join(unknown)}')


def accept(state: dict, guide_text: str, ids, substantive: bool, newest: str,
           citer_stamps: dict[str, list[str]] | None = None) -> dict:
    '''R7 accept: record each section's current text_hash. Substantive also
    sets a new `changed` (R2.4), which flags the section's citers. Stage 1 has
    no citations, so cli.py passes none; Stage 2 passes the index's stamps.'''
    known(state, ids)
    by_id = {s.id: s for s in sections(guide_text)}
    new = copy.deepcopy(state)
    for sid in ids:
        new['sections'][sid]['text_hash'] = text_hash(by_id[sid].text)
        if substantive:
            new['sections'][sid]['changed'] = next_changed(newest, (citer_stamps or {}).get(sid, []))
    return new


def advance(state: dict, ids, to: str, labels: set[str], day: str) -> dict:
    '''R7 advance: set `checked` to a changelog release, dated the day of the
    check. It never moves a section backwards.'''
    known(state, ids)
    if to not in labels:
        raise SetupError(f'{to} is not a release in the newest cached changelog')
    behind = [sid for sid in ids if version_key(to) < version_key(state['sections'][sid]['checked']['release'])]
    if behind:
        raise SetupError(f'{to} is older than the checked release of {", ".join(behind)}')
    new = copy.deepcopy(state)
    for sid in ids:
        new['sections'][sid]['checked'] = {'release': to, 'date': day}
    return new


def audited(state: dict, manifest: Manifest, group: str, release: str, day: str) -> dict:
    '''R7 audited: set `audited` for the group's sections to the current
    release and day, and advance their `checked` to it.'''
    if group not in manifest.groups:
        raise SetupError(f'unknown group {group}')
    known(state, manifest.groups[group].sections)
    new = copy.deepcopy(state)
    for sid in manifest.groups[group].sections:
        new['sections'][sid]['audited'] = {'release': release, 'date': day}
        new['sections'][sid]['checked'] = {'release': release, 'date': day}
    return new


def rebaseline(state: dict, manifest: Manifest, guide_text: str, group: str, refs: list[str],
               latest: Path, release: str) -> tuple[dict, list[str], list[str]]:
    '''R7 rebaseline: re-hash the group's selected blocks from latest/, all of
    them or the listed refs: `<page>`, or `<page> › <key>` as check prints a
    block. A listed key that is no longer selected leaves the baseline.
    Returns the new state, the pages to snapshot to <release>/docs, and notes.

    A missing page keeps its entries: it needs a manifest edit, not a
    rebaseline. A full run also drops the pages the group no longer maps.
    Every run refreshes the llms.txt slug list.'''
    if group not in manifest.groups:
        raise SetupError(f'unknown group {group}')
    check_ids(manifest, guide_text)
    llms_path = latest / 'llms.txt'
    if not llms_path.is_file():
        raise SetupError(f'{llms_path}: no latest fetch; run check first')
    slugs = parse_llms(llms_path.read_text(encoding='utf-8'))
    mapped = manifest.groups[group].pages
    watched = set().union(*group_terms(manifest, guide_text)[group].values())
    targets: dict[str, set[str] | None] = {}
    for ref in refs or list(mapped):
        page, _, key = ref.partition(SEP)
        if not key:
            targets[page] = None
        elif targets.get(page, set()) is not None:
            targets.setdefault(page, set()).add(key)
    new = copy.deepcopy(state)
    g = new['groups'].setdefault(group, {'blocks': {}, 'snapshot': {}})
    snap, notes = [], []
    for page, keys in targets.items():
        if page not in mapped:
            if page not in g['blocks']:
                raise SetupError(f'{page} is neither mapped to nor baselined in {group}')
            if keys is None:
                g['blocks'].pop(page)
                g['snapshot'].pop(page, None)
            else:
                for key in keys:
                    g['blocks'][page].pop(key, None)
            notes.append(f'{page}: no longer mapped to {group}; dropped its baselined blocks')
            continue
        path = latest / page_file(page)
        if not path.is_file() or (not is_platform(page) and page not in slugs):
            notes.append(f'{page}: missing page; kept its entries. Drop or remap it in manifest.toml first')
            continue
        chosen = select_blocks(path.read_text(encoding='utf-8'), mapped[page], watched)
        if keys is None:
            g['blocks'][page] = chosen
        else:
            merged = {**g['blocks'].get(page, {})}
            for key in keys:
                if key in chosen:
                    merged[key] = chosen[key]
                else:
                    merged.pop(key, None)
            order = list(chosen) + [k for k in merged if k not in chosen]
            g['blocks'][page] = {k: merged[k] for k in order if k in merged}
        g['snapshot'][page] = release
        snap.append(page)
    if not refs:
        for page in [p for p in g['blocks'] if p not in mapped]:
            g['blocks'].pop(page)
            g['snapshot'].pop(page, None)
            notes.append(f'{page}: no longer mapped to {group}; dropped its baselined blocks')
    new['llms'] = sorted(slugs)
    return new, snap, notes


def stamp(guide_text: str, state: dict) -> str:
    '''R7 stamp: the guide with its stamp region regenerated (R1.2).'''
    return with_stamp(guide_text, render_stamp(state['sections']))
```

> Deviation: ruling 7: a listed `rebaseline` raises `SetupError`, naming them, when
> unlisted baselined blocks on the page also differ from `latest/`, since the page's
> snapshot would then not hold their baselined text (6822f01).

- [x] **Step 6: Run the suite to see it pass.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: `80 passed` (+18). The real-history test must pass, not skip: a worktree made by `git worktree add` shares the repo's full history.

- [x] **Step 7: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && [ "$(git branch --show-current)" = feat/cc-drift-stage1 ] && git add build/cc_guide/cc_fixtures.py build/cc_guide/baseline.py build/cc_guide/test_baseline.py && git commit -m "feat(cc_guide): add the baseline bookkeeping but cite

baseline.py builds the initial state from a snapshot directory (R2.6),
derives each section's changed from the July guide and the refresh
aligned by parent and heading (R11.1), and implements accept, advance,
audited, rebaseline and stamp as pure functions over the state (R7).
rebaseline keeps a missing page's entries and refreshes the llms list.

Plan 38, Task 7.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: The lint (`lint.py`, R5 without its citation rules)

**Files:**
- Create: `build/cc_guide/lint.py`
- Test: `build/cc_guide/test_lint.py`

**Interfaces:**
- Consumes: `blocks` (`CELL_SPLIT_RE`, `fence_spans`, `fenced_lines`), `guide` (`STAMP_CLOSE`, `STAMP_OPEN`, `anchor_problems`, `render_stamp`, `sections`, `stamp_bounds`, `text_hash`) and `state.Manifest`.
- Produces, for `check.py` and `cli.py`:
  - `CLI = 'uv run --python 3.13 python build/cc_guide/cli.py'`;
  - `lint(guide_text: str, manifest: Manifest, state: dict, labels: set[str] | None) -> tuple[list[str], list[str]]`, giving (violations, notes);
  - the helpers `cell_count`, `id_set_problems`, `hash_problems`, `stamp_problems` and `quality_problems(guide_text, labels)`.
- The violations come in this order: anchors, ID sets, text hashes, the stamp region, then guide quality.
- `labels` holds the newest changelog's release labels. The caller parses the changelog, so a malformed one surfaces as a `SetupError` there (exit 2), never as a lint crash. With `labels=None`, the release-label check is skipped with the note `release-label check skipped: no changelog to read`.

- [x] **Step 1: Write the tests.** Create `build/cc_guide/test_lint.py`:

```python
'''Tests for lint.py: every R5 rule but the citation rules (Stage 2's).'''
import pytest

import baseline
import docs
import guide
import lint
import state
from cc_fixtures import (CHANGELOG_TEXT, FENCE, GUIDE_IDS, MANIFEST_TOML, docs_dir,  # noqa: F401
                         fixture_state, guide_text, isolated_home)

MANIFEST = state.parse_manifest(MANIFEST_TOML)
LABELS = {r.label for r in docs.parse_changelog(CHANGELOG_TEXT)}
CLI = 'uv run --python 3.13 python build/cc_guide/cli.py'


def run(text, s, labels=LABELS, manifest=MANIFEST):
    return lint.lint(text, manifest, s, labels)


def synced(text, s):
    '''The state with every text_hash re-accepted for text, so a test sees
    only the rule it breaks.'''
    return baseline.accept(s, text, GUIDE_IDS, False, '2.1.902')


def test_the_fixture_inputs_lint_clean(docs_dir):
    assert run(guide_text(), fixture_state(docs_dir)) == ([], [])


def test_without_a_changelog_the_label_check_is_skipped_with_a_note(docs_dir):
    assert run(guide_text(), fixture_state(docs_dir), None) == (
        [], ['release-label check skipped: no changelog to read'])


def test_the_three_id_sets_must_agree(docs_dir):
    s = fixture_state(docs_dir)
    del s['sections']['beta.reference']
    manifest = state.parse_manifest(MANIFEST_TOML.replace("'beta.reference']", "'beta.reference', 'beta.extra']"))
    violations, _ = run(guide_text(), s, manifest=manifest)
    assert violations == ['section beta.extra: missing from the guide and baseline.json',
                          'section beta.reference: missing from baseline.json']


def test_a_text_change_names_both_accept_commands(docs_dir):
    violations, _ = run(guide_text().replace('Alpha uses', 'Alpha now uses'), fixture_state(docs_dir))
    assert violations == [
        f'section alpha.overview: text differs from its text_hash; record it with '
        f'`{CLI} baseline accept alpha.overview --substantive` (flags its citers) or `... --editorial`']


def test_a_rewrap_is_not_a_text_change(docs_dir):
    text = guide_text().replace('Alpha uses `ALPHA_TOOL`, `if`', 'Alpha uses `ALPHA_TOOL`,\n`if`')
    assert run(text, fixture_state(docs_dir)) == ([], [])


def test_a_stale_stamp_names_the_stamp_command(docs_dir):
    s = baseline.advance(fixture_state(docs_dir), GUIDE_IDS, '2.1.902', {'2.1.902'}, '2026-10-04')
    violations, _ = run(guide_text(), s)
    assert violations == [f'guide: the stamp region does not match baseline.json; run `{CLI} baseline stamp`']


def test_the_stamp_region_must_exist_and_precede_the_first_section(docs_dir):
    s = fixture_state(docs_dir)
    missing = guide_text().replace(guide.STAMP_CLOSE + '\n', '')
    assert run(missing, s)[0] == [
        f'guide: needs one stamp region, a {guide.STAMP_OPEN} line then a {guide.STAMP_CLOSE} line']
    region = '\n'.join([guide.STAMP_OPEN, guide.render_stamp(s['sections']), guide.STAMP_CLOSE, ''])
    late = guide_text().replace(region, '') + region
    assert run(late, synced(late, s))[0] == ['guide: the stamp region must sit before the first section']


@pytest.mark.parametrize('prose, flagged', [
    ('Fixed in 2.1.950.', ['2.1.950']),
    ('Since 2.1.901, and 2.1.902.', []),
    ('Not 12.1.900 or 2.1.9001x.', ['2.1.9001']),
    ('A stamp 2.1.902.1 is no label.', ['2.1.902.1']),
])
def test_every_2_1_version_must_be_a_release_label(docs_dir, prose, flagged):
    text = guide_text() + prose + '\n'
    line = len(text.split('\n')) - 1
    assert run(text, synced(text, fixture_state(docs_dir)))[0] == [
        f'guide line {line}: {v} is not a changelog release label' for v in flagged]


def test_every_table_row_keeps_its_headers_cell_count(docs_dir):
    text = guide_text().replace('| `BETA_ENV` | on |', '| `BETA_ENV` | on | extra |\n| `a\\|b` | on |')
    line = text.split('\n').index('| `BETA_ENV` | on | extra |') + 1
    assert run(text, synced(text, fixture_state(docs_dir)))[0] == [
        f'guide line {line}: table row has 3 cells; its header has 2']


def test_every_json_block_must_parse(docs_dir):
    text = guide_text().replace('{"beta": true}', '{"beta": true,}')
    line = text.split('\n').index(FENCE + 'json') + 1
    assert run(text, synced(text, fixture_state(docs_dir)))[0] == [
        f'guide line {line}: json block does not parse (Illegal trailing comma before end of object)']


def test_an_anchor_problem_fails_the_lint(docs_dir):
    violations, _ = run(guide_text().replace('<!-- cc: beta.reference -->\n', ''), fixture_state(docs_dir))
    assert violations[0].endswith("heading '### Reference ⚠' has no anchor on its next line")
    assert 'section beta.reference: missing from the guide' in violations
```

> Deviation: `test_an_anchor_problem_fails_the_lint` compares the whole violation
> list exactly, with the heading's line computed, per the Global Constraints (424d772).

- [x] **Step 2: Create the stub** `build/cc_guide/lint.py`, holding only `'''`lint`: the offline gate over the guide, manifest.toml and baseline.json (drift spec R5).'''`

- [x] **Step 3: Run the tests to see them fail.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf test_lint.py`
Expected: `14 failed`, each `AttributeError: module 'lint' has no attribute 'lint'`.

- [x] **Step 4: Implement.** Replace `build/cc_guide/lint.py` with:

```python
'''`lint`: the offline gate over the guide, manifest.toml and baseline.json
(drift spec R5). Its citation rules and STALE lines are Stage 2's.'''
import json
import re

from blocks import CELL_SPLIT_RE, fence_spans, fenced_lines
from guide import STAMP_CLOSE, STAMP_OPEN, anchor_problems, render_stamp, sections, stamp_bounds, text_hash
from state import Manifest

CLI = 'uv run --python 3.13 python build/cc_guide/cli.py'
# A 2.1.NNN version, not inside a longer number; a trailing period is prose.
VERSION_RE = re.compile(r'(?<![\d.])2\.1\.\d+(?:\.\d+)*(?!\d)')


def cell_count(row: str) -> int:
    '''Cells in a table row, split on unescaped pipes, outer pipes dropped.'''
    s = row.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|') and not s.endswith('\\|'):
        s = s[:-1]
    return len(CELL_SPLIT_RE.split(s))


def id_set_problems(guide_text: str, manifest: Manifest, state: dict) -> list[str]:
    '''The anchors, the manifest's groups and baseline.json's sections carry
    one ID set (R5). The manifest's own parse already holds each ID to one
    group.'''
    where = {'the guide': {s.id for s in sections(guide_text) if s.id},
             'manifest.toml': set(manifest.group_of()),
             'baseline.json': set(state['sections'])}
    out = []
    for sid in sorted(set().union(*where.values())):
        missing = [name for name, ids in where.items() if sid not in ids]
        if missing:
            out.append(f'section {sid}: missing from {" and ".join(missing)}')
    return out


def hash_problems(guide_text: str, state: dict) -> list[str]:
    '''Each section's text matches its text_hash (R5); a mismatch names the
    two `baseline accept` outcomes (R2.4).'''
    out = []
    for s in sections(guide_text):
        recorded = state['sections'].get(s.id, {}).get('text_hash')
        if recorded and text_hash(s.text) != recorded:
            out.append(f'section {s.id}: text differs from its text_hash; record it with '
                       f'`{CLI} baseline accept {s.id} --substantive` (flags its citers) '
                       f'or `... --editorial`')
    return out


def stamp_problems(guide_text: str, state: dict) -> list[str]:
    '''The stamp region sits before the first section and matches
    baseline.json (R1.2, R5).'''
    bounds = stamp_bounds(guide_text)
    if bounds is None:
        return [f'guide: needs one stamp region, a {STAMP_OPEN} line then a {STAMP_CLOSE} line']
    first = min((s.line for s in sections(guide_text)), default=None)
    if first is not None and bounds[1] + 1 >= first:
        return ['guide: the stamp region must sit before the first section']
    content = '\n'.join(guide_text.split('\n')[bounds[0] + 1:bounds[1]])
    if content != render_stamp(state['sections']):
        return [f'guide: the stamp region does not match baseline.json; run `{CLI} baseline stamp`']
    return []


def quality_problems(guide_text: str, labels: set[str] | None) -> tuple[list[str], list[str]]:
    '''R5's guide-quality checks: every 2.1.NNN is a changelog release label
    (skipped with a note when there is no changelog to read), every table
    keeps its header's column count, and every json code block parses.'''
    out, notes = [], []
    lines = guide_text.split('\n')
    if labels is None:
        notes.append('release-label check skipped: no changelog to read')
    else:
        for n, line in enumerate(lines, start=1):
            out += [f'guide line {n}: {v} is not a changelog release label'
                    for v in VERSION_RE.findall(line) if v not in labels]
    fenced = fenced_lines(lines)
    i = 0
    while i < len(lines):
        if i in fenced or not lines[i].lstrip().startswith('|'):
            i += 1
            continue
        header = cell_count(lines[i])
        while i < len(lines) and i not in fenced and lines[i].lstrip().startswith('|'):
            if cell_count(lines[i]) != header:
                out.append(f'guide line {i + 1}: table row has {cell_count(lines[i])} cells; '
                           f'its header has {header}')
            i += 1
    for start, close, info in fence_spans(lines):
        if info.split()[:1] == ['json']:
            body = '\n'.join(lines[start + 1:len(lines) if close is None else close])
            try:
                json.loads(body)
            except json.JSONDecodeError as exc:
                out.append(f'guide line {start + 1}: json block does not parse ({exc.msg})')
    return out, notes


def lint(guide_text: str, manifest: Manifest, state: dict,
         labels: set[str] | None) -> tuple[list[str], list[str]]:
    '''R5 without its citation rules: (violations, notes). `labels` are the
    newest changelog's release labels; the caller parses the changelog, so a
    malformed one is a setup error there.'''
    quality, notes = quality_problems(guide_text, labels)
    violations = (anchor_problems(guide_text) + id_set_problems(guide_text, manifest, state)
                  + hash_problems(guide_text, state) + stamp_problems(guide_text, state) + quality)
    return violations, notes
```

- [x] **Step 5: Run the suite to see it pass.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: `94 passed` (+14).

- [x] **Step 6: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && [ "$(git branch --show-current)" = feat/cc-drift-stage1 ] && git add build/cc_guide/lint.py build/cc_guide/test_lint.py && git commit -m "feat(cc_guide): lint the guide against its manifest and baseline

lint.py is R5 without its citation rules: one anchor per heading, one ID
set across the guide, manifest and baseline, each section's text_hash
(naming both accept commands), the stamp region's place and content, and
guide quality: 2.1.NNN labels, table column counts and json blocks.

Plan 38, Task 8.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: The check (`check.py`, R6)

**Files:**
- Modify: `build/cc_guide/cc_fixtures.py` (append)
- Create: `build/cc_guide/check.py`
- Test: `build/cc_guide/test_check.py`

**Interfaces:**
- Consumes: `blocks` (`SEP`, `block_hash`, `candidates`, `page_blocks`, `select`), `docs` (`CHANGELOG`, `LLMS`, `Release`, `is_platform`, `page_file`, `page_url`, `parse_changelog`, `parse_llms`, `version_key`), `lint.lint`, and `state` (`BASELINE`, `MANIFEST`, `PROBES`, `Manifest`, `ProbeRow`, `SetupError`, `Source`, `fetch_record`, `group_terms`, `latest_docs`, `parse_baseline`, `parse_manifest`, `parse_probes`).
- Produces, for `cli.py`:
  - constants and types: `USER_AGENT`, `TIMEOUT = 30`, `WORKERS = 8`, `Fetch = Callable[[str], tuple[int, bytes]]` and `FetchError`;
  - `http_get(url) -> tuple[int, bytes]`, where a 404 returns `(404, b'')` and any other failure, after one retry, raises `FetchError`;
  - `Docs(changelog, llms, pages, origin, errors, unread)`;
  - `releases_of(changelog_text) -> list[Release]`, which raises `SetupError` on a malformed or empty changelog;
  - `offline_docs(manifest, folder) -> Docs` and `live_docs(manifest, cache, fetch, now) -> Docs`;
  - `Finding(group, kind, page, key, candidates)`, with `.ref()`;
  - `compare(manifest, state, terms, docs) -> tuple[list[Finding], dict[str, list[str]]]`;
  - `untriaged`, `release_notes`, `due_changelog`, `due_probes`, `due_audit` and `sha256`;
  - `check(source: Source, cache: Path, *, docs_dir: Path | None, today: date, now: datetime, fetch: Fetch) -> tuple[int, dict, Path]`, returning (exit code, report, report path);
  - `summary(report, path) -> list[str]`.
- The report's keys are `generated_at`, `inputs`, `docs`, `hashes`, `lint`, `latest_release`, `findings`, `deselected`, `llms`, `untriaged`, `releases`, `due`, `errors` and `exit`. It is written to `<cache>/reports/<sha256(baseline.json)[:12]>.json`.
- Fixtures: `GUIDE_PATH` and `drift_repo(root, folder)`, a committed repo with the fixture guide, manifest and baseline.

`test_editing_one_row_flags_only_the_groups_whose_terms_match_it` is R12.3's row fixture. The probe due rules are tested against a fixture registry, because the real one stays empty until Stage 5 (decision 6).

- [x] **Step 1: Append to `build/cc_guide/cc_fixtures.py`,** after two blank lines:

```python
GUIDE_PATH = 'specs/guides/claude-code-customization-guide.md'


def drift_repo(root, folder):
    '''A committed fixture repo: the guide, manifest.toml, and the baseline
    init builds over `folder`.'''
    import state
    return fixture_repo(root, {GUIDE_PATH: guide_text(), state.MANIFEST: MANIFEST_TOML,
                               state.BASELINE: state.dump_baseline(fixture_state(folder))})
```

- [x] **Step 2: Write the tests.** Create `build/cc_guide/test_check.py`:

```python
'''Tests for check.py: compare, the changelog, every due rule, the fetch gate,
the report and exit codes (drift spec R6, R12.3's row fixture).'''
import json
from datetime import date, datetime, timezone

import pytest

import check
import docs
import state
from cc_fixtures import (DOCS, ENV_PAGE, MANIFEST_TOML, docs_dir, drift_repo,  # noqa: F401
                         fixture_state, git, guide_text, isolated_home, write_tree)

MANIFEST = state.parse_manifest(MANIFEST_TOML)
TERMS = state.group_terms(MANIFEST, guide_text())
ENV = 'Environment variables'
NOW = datetime(2026, 10, 4, 12, 0, tzinfo=timezone.utc)
URLS = {docs.page_url(p, MANIFEST.sources): docs.page_file(p) for p in MANIFEST.pages()}
URLS.update({MANIFEST.sources['changelog']: 'changelog.md', MANIFEST.sources['llms']: 'llms.txt'})


def offline(folder):
    return check.offline_docs(MANIFEST, folder)


def findings(folder, s=None):
    found, deselected = check.compare(MANIFEST, s or fixture_state(folder), TERMS, offline(folder))
    return [(f.group, f.kind, f.ref(), f.candidates) for f in found], deselected


def test_unchanged_docs_give_no_findings(docs_dir):
    assert findings(docs_dir) == ([], {'alpha': [], 'beta': []})


def test_changed_missing_and_new_blocks_name_their_candidate_sections(tmp_path, docs_dir):
    s = fixture_state(docs_dir)
    write_tree(docs_dir, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')
                          .replace('## Options', '## Flags'),
                          'events.md': DOCS['events.md'] + '## Retry\n\nRetries reuse `BetaEvent`.\n'})
    assert findings(docs_dir, s)[0] == [
        ('alpha', 'changed', 'tools › Tools', ['alpha.overview']),
        ('alpha', 'missing', 'tools › Tools › Options', ['alpha.overview', 'alpha.reference']),
        ('alpha', 'missing', 'tools › Tools › Options › `--fast`', ['alpha.overview', 'alpha.reference']),
        ('alpha', 'new', 'tools › Tools › Flags', ['alpha.overview', 'alpha.reference']),
        ('alpha', 'new', 'tools › Tools › Flags › `--fast`', ['alpha.overview', 'alpha.reference']),
        ('beta', 'new', 'events › Events › Retry', ['beta.reference']),
    ]


def test_a_block_that_lost_its_term_is_deselected_not_changed(docs_dir):
    s = fixture_state(docs_dir)
    write_tree(docs_dir, {'env-vars.md': ENV_PAGE.replace('see [events](/docs/en/events)', 'see events')
                          .replace('| `BETA_ENV` |', '| `GAMMA_ENV` |')})
    found, deselected = findings(docs_dir, s)
    assert found == [('beta', 'missing', f'env-vars › {ENV} › `BETA_ENV`', ['beta.overview'])]
    s['groups']['beta']['blocks']['env-vars'][f'{ENV} › `PIPE_ENV`'] = '0' * 16
    assert findings(docs_dir, s)[1]['beta'] == [f'env-vars › {ENV} › `PIPE_ENV`']


def test_a_page_missing_from_llms_or_the_docs_is_one_finding(docs_dir):
    s = fixture_state(docs_dir)
    write_tree(docs_dir, {'llms.txt': DOCS['llms.txt'].replace('/tools.md', '/tools-moved.md')})
    (docs_dir / 'platform_pricing.md').unlink()
    assert findings(docs_dir, s)[0] == [
        ('alpha', 'missing-page', 'tools', ['alpha.overview', 'alpha.reference']),
        ('beta', 'missing-page', 'platform:pricing', ['beta.overview', 'beta.reference'])]


def test_editing_one_row_flags_only_the_groups_whose_terms_match_it(docs_dir):
    '''R12.3's row fixture: env-vars is a terms page of both groups.'''
    s = fixture_state(docs_dir)
    write_tree(docs_dir, {'env-vars.md': ENV_PAGE.replace('Turns on beta;', 'Turns on beta at once;')})
    assert findings(docs_dir, s)[0] == [
        ('beta', 'changed', f'env-vars › {ENV} › `BETA_ENV`', ['beta.overview'])]
    write_tree(docs_dir, {'env-vars.md': ENV_PAGE.replace('Turns on alpha.', 'Turns alpha off.')})
    assert findings(docs_dir, s)[0] == [
        ('alpha', 'changed', f'env-vars › {ENV} › `ALPHA_ENV`', ['alpha.reference'])]


def test_each_section_lists_the_releases_after_its_checked_oldest_first(docs_dir):
    s = fixture_state(docs_dir)
    s['sections']['beta.reference']['checked']['release'] = '2.1.901'
    releases = docs.parse_changelog(DOCS['changelog.md'])
    pending = check.untriaged(s, releases)
    assert pending['alpha.overview'] == ['2.1.901', '2.1.902']
    assert pending['beta.reference'] == ['2.1.902']
    notes = check.release_notes(releases, {'2.1.901', '2.1.902'}, TERMS)
    assert list(notes) == ['2.1.901', '2.1.902']
    assert notes['2.1.902']['bullets'] == [
        {'text': 'Changed how `BETA_ENV` is read', 'hints': ['beta.overview']},
        {'text': 'Fixed a crash in the fixture tool', 'hints': []}]


@pytest.mark.parametrize('today, due', [(date(2026, 9, 26), False), (date(2026, 9, 27), True)])
def test_the_changelog_batch_is_due_once_its_oldest_release_is_a_week_old(docs_dir, today, due):
    releases = docs.parse_changelog(DOCS['changelog.md'])
    assert check.due_changelog(fixture_state(docs_dir), releases, 7, today) == {
        'releases': 2, 'oldest': '2.1.901', 'oldest_date': '2026-09-20', 'due_from': '2026-09-27', 'due': due}


def test_nothing_untriaged_means_no_batch(docs_dir):
    s = fixture_state(docs_dir)
    for sec in s['sections'].values():
        sec['checked']['release'] = '2.1.902'
    assert check.due_changelog(s, docs.parse_changelog(DOCS['changelog.md']), 7, date(2026, 12, 1)) is None


def rows(*specs):
    return [state.ProbeRow(date.fromisoformat(d), v, 'p1', o) for d, v, o in specs]


@pytest.mark.parametrize('history, today, why', [
    ([], date(2026, 10, 4), 'never run'),
    ([('2026-10-01', '2.1.902', 'PASS')], date(2026, 10, 4), None),
    ([('2026-09-20', '2.1.901', 'PASS')], date(2026, 9, 26), None),
    ([('2026-09-20', '2.1.901', 'PASS')], date(2026, 9, 27), 'last run 2026-09-20 at 2.1.901'),
    ([('2026-09-20', '2.1.902', 'PASS')], date(2026, 12, 1), None),
    ([('2026-10-01', '2.1.902', 'DIVERGES')], date(2026, 10, 1), 'DIVERGES with no later PASS'),
    ([('2026-10-01', '2.1.902', 'DIVERGES'), ('2026-10-02', '2.1.902', 'ERROR')], date(2026, 10, 2),
     'DIVERGES with no later PASS'),
    ([('2026-10-01', '2.1.902', 'DIVERGES'), ('2026-10-02', '2.1.902', 'PASS')], date(2026, 10, 2), None),
])
def test_probe_due_rules(history, today, why):
    manifest = MANIFEST._replace(probes={'p1': (['beta.reference'], [])})
    due = check.due_probes(manifest, rows(*history), '2.1.902', 7, today)
    assert due == ([] if why is None else [{'probe': 'p1', 'why': why}])


def test_an_empty_registry_has_no_probe_due():
    assert check.due_probes(MANIFEST, [], '2.1.902', 7, date(2027, 1, 1)) == []


def test_the_audit_clock_is_shared_and_targets_the_oldest_group(docs_dir):
    s = fixture_state(docs_dir)
    assert check.due_audit(MANIFEST, s, 30, date(2026, 10, 1)) == {
        'group': 'alpha', 'last_audit': '2026-09-02', 'due_from': '2026-10-02', 'due': False}
    for sid in ('alpha.overview', 'alpha.reference'):
        s['sections'][sid]['audited'] = {'release': '2.1.902', 'date': '2026-10-02'}
    assert check.due_audit(MANIFEST, s, 30, date(2026, 10, 3)) == {
        'group': 'beta', 'last_audit': '2026-10-02', 'due_from': '2026-11-01', 'due': False}


def serving(folder, log=None, fail=()):
    '''A fake fetch serving folder's files by URL; unknown URLs are 404.'''
    def fetch(url):
        if log is not None:
            log.append(url)
        if url in fail:
            raise check.FetchError(f'{url}: timed out')
        path = folder / URLS.get(url, 'absent')
        return (200, path.read_bytes()) if path.is_file() else (404, b'')
    return fetch


def test_the_fetch_gate_refetches_every_page_only_when_the_head_moves(tmp_path, docs_dir):
    cache, log = tmp_path / 'cache', []
    check.live_docs(MANIFEST, cache, serving(docs_dir, log), NOW)
    assert len(log) == 2 + len(MANIFEST.pages())
    assert json.loads((cache / 'latest' / 'fetch.json').read_text())['changelog_head'] == '2.1.902'
    log.clear()
    (state.latest_docs(cache) / 'events.md').unlink()
    check.live_docs(MANIFEST, cache, serving(docs_dir, log), NOW)
    assert log == [MANIFEST.sources['changelog'], MANIFEST.sources['llms'],
                   docs.page_url('events', MANIFEST.sources)]
    log.clear()
    write_tree(docs_dir, {'changelog.md': DOCS['changelog.md'].replace(
        '<Update label="2.1.902"', '<Update label="2.1.903" description="October 3, 2026">\n</Update>\n'
        '<Update label="2.1.902"')})
    check.live_docs(MANIFEST, cache, serving(docs_dir, log), NOW)
    assert len(log) == 2 + len(MANIFEST.pages())


def test_a_404_removes_the_stale_copy_and_reads_as_a_missing_page(tmp_path, docs_dir):
    cache = tmp_path / 'cache'
    s = fixture_state(docs_dir)
    check.live_docs(MANIFEST, cache, serving(docs_dir), NOW)
    (docs_dir / 'platform_pricing.md').unlink()
    write_tree(docs_dir, {'changelog.md': DOCS['changelog.md'].replace(
        '<Update label="2.1.902"', '<Update label="2.1.903" description="October 3, 2026">\n</Update>\n'
        '<Update label="2.1.902"')})
    got = check.live_docs(MANIFEST, cache, serving(docs_dir), NOW)
    assert not (state.latest_docs(cache) / 'platform_pricing.md').exists()
    found, _ = check.compare(MANIFEST, s, TERMS, got)
    assert [(f.kind, f.page) for f in found] == [('missing-page', 'platform:pricing')]


def run_check(repo, cache, folder=None, today=date(2026, 9, 10), fetch=None):
    return check.check(state.Source(repo), cache, docs_dir=folder, today=today, now=NOW, fetch=fetch)


@pytest.mark.parametrize('today, code', [(date(2026, 9, 10), 0), (date(2026, 9, 27), 1)])
def test_exit_zero_when_nothing_is_due_and_one_when_something_is(tmp_path, docs_dir, today, code):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    assert run_check(repo, tmp_path / 'cache', docs_dir, today)[0] == code


def test_a_changed_block_or_a_lint_failure_is_due_at_once(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    write_tree(docs_dir, {'events.md': DOCS['events.md'].replace('fires on beta', 'fires on gamma')})
    assert run_check(repo, tmp_path / 'cache', docs_dir)[0] == 1
    write_tree(docs_dir, DOCS)
    guide = repo / 'specs/guides/claude-code-customization-guide.md'
    guide.write_text(guide.read_text().replace('Alpha uses', 'Alpha now uses'))
    code, report, _ = run_check(repo, tmp_path / 'cache', docs_dir)
    assert (code, report['due']['lint']) == (1, 1)


def test_a_network_failure_exits_two_and_is_reported(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    code, report, path = run_check(repo, tmp_path / 'cache',
                                   fetch=serving(docs_dir, fail={MANIFEST.sources['changelog']}))
    assert code == 2
    assert report['errors'] == [f"{MANIFEST.sources['changelog']}: timed out"]
    assert json.loads(path.read_text())['exit'] == 2


def test_a_failed_page_fetch_exits_two_without_comparing_that_page(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    url = docs.page_url('tools', MANIFEST.sources)
    code, report, _ = run_check(repo, tmp_path / 'cache', fetch=serving(docs_dir, fail={url}))
    assert (code, report['errors'], report['findings']['alpha']) == (2, [f'{url}: timed out'], [])


def test_a_malformed_changelog_is_a_setup_error(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    write_tree(docs_dir, {'changelog.md': DOCS['changelog.md'].replace('October 1, 2026', '2026-10-01')})
    with pytest.raises(state.SetupError, match='changelog line 8:'):
        run_check(repo, tmp_path / 'cache', docs_dir)


def test_the_report_is_keyed_by_the_baseline_hash_and_never_written_in_the_repo(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    _, report, path = run_check(repo, tmp_path / 'cache', docs_dir)
    baseline_sha = report['hashes']['baseline']
    assert path == tmp_path / 'cache' / 'reports' / f'{baseline_sha[:12]}.json'
    assert set(report) == {'generated_at', 'inputs', 'docs', 'hashes', 'lint', 'latest_release', 'findings',
                           'deselected', 'llms', 'untriaged', 'releases', 'due', 'errors', 'exit'}
    assert git(repo, 'status', '--porcelain') == ''
    run_check(repo, tmp_path / 'cache', fetch=serving(docs_dir))
    assert git(repo, 'status', '--porcelain') == ''


def test_llms_slugs_added_and_removed_since_the_baseline_are_listed(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    write_tree(docs_dir, {'llms.txt': DOCS['llms.txt'].replace('plugins/components', 'plugins/parts')})
    _, report, _ = run_check(repo, tmp_path / 'cache', docs_dir)
    assert report['llms'] == {'added': ['plugins/parts'], 'removed': ['plugins/components']}
```

> Deviation: per the Global Constraints, the `match=` assertion is exact (561c7c1),
> and the audit test pins its first due day while the report test, renamed, lists
> check's whole write set (b9a76ff). On the owner's call (ruling 8), a new offline
> `http_get` test, +1 (12b0705). The final review added a parametrized test isolating
> the exit code's audit and probe terms, +2 (bfbc2d5). At the completion gate the
> owner reversed `test_a_block_that_lost_its_term_is_deselected_not_changed` (4ff20bb).

- [x] **Step 3: Create the stub** `build/cc_guide/check.py`, holding only `'''`check`: fetch the docs, compare, and report what is due (drift spec R6).'''`

- [x] **Step 4: Run the tests to see them fail.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf test_check.py`
Expected: `29 failed`, each `AttributeError: module 'check' has no attribute …`: nine for `due_probes`, eight for `check`, five for `compare`, three for `due_changelog`, two for `live_docs`, and one each for `due_audit` and `untriaged`.

- [x] **Step 5: Implement.** Replace `build/cc_guide/check.py` with:

```python
'''`check`: fetch the docs when the changelog head moved, compare each group's
selected blocks with the baseline, list each section's untriaged releases,
and report what is due (drift spec R6). R6.8's citing-file lists are Stage
2's, `--hook` (R6.10) Stage 4's and `packets` (R6.11) Stage 3's.'''
import hashlib
import json
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable, NamedTuple

from blocks import SEP, block_hash, candidates, page_blocks, select
from docs import CHANGELOG, LLMS, Release, is_platform, page_file, page_url, parse_changelog, parse_llms, version_key
from lint import lint
from state import (BASELINE, MANIFEST, PROBES, Manifest, ProbeRow, SetupError, Source, fetch_record,
                   group_terms, latest_docs, parse_baseline, parse_manifest, parse_probes)

USER_AGENT = 'agent-skills-cc-guide/1 (Claude Code docs drift check)'
TIMEOUT = 30
WORKERS = 8
Fetch = Callable[[str], tuple[int, bytes]]


class FetchError(Exception):
    '''A request that failed twice, or answered other than 200 or 404.'''


def http_get(url: str) -> tuple[int, bytes]:
    '''R6.4: a GET with a 30-second timeout and one retry, sending a
    User-Agent that names the tool and nothing personal. A 404 returns
    (404, b''); any other failure raises FetchError.'''
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    error = ''
    for _ in range(2):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return 404, b''
            error = f'HTTP {exc.code}'
        except OSError as exc:
            error = str(exc)
    raise FetchError(f'{url}: {error}')


class Docs(NamedTuple):
    changelog: str
    llms: str
    pages: dict[str, str | None]  # mapped page -> text, None when absent
    origin: str                   # 'live' or the --docs directory
    errors: list[str]
    unread: set[str]              # pages whose fetch failed; never compared


def releases_of(changelog_text: str) -> list[Release]:
    try:
        releases = parse_changelog(changelog_text)
    except ValueError as exc:
        raise SetupError(f'changelog: {exc}') from None
    if not releases:
        raise SetupError('changelog: no <Update> release blocks')
    return releases


def offline_docs(manifest: Manifest, folder: Path) -> Docs:
    '''R6.1 --docs: the docs read from a local directory, named as the cache
    names them. A page file that is absent is a missing page.'''
    def read(name: str) -> str | None:
        path = folder / name
        return path.read_text(encoding='utf-8') if path.is_file() else None
    changelog, llms = read(CHANGELOG), read(LLMS)
    if changelog is None or llms is None:
        raise SetupError(f'{folder}: needs {CHANGELOG} and {LLMS}')
    return Docs(changelog, llms, {p: read(page_file(p)) for p in manifest.pages()},
                str(folder), [], set())


def live_docs(manifest: Manifest, cache: Path, fetch: Fetch, now: datetime) -> Docs:
    '''R6.3-R6.4: fetch the changelog and llms.txt; then every mapped page if
    the changelog head moved since the last fetch, else only the mapped pages
    latest/docs lacks. Pages overwrite latest/docs. A 404 or a failed fetch
    removes the stale copy, so a later run fetches the page again.'''
    folder = latest_docs(cache)
    folder.mkdir(parents=True, exist_ok=True)
    record = fetch_record(cache)
    previous = json.loads(record.read_text(encoding='utf-8')).get('changelog_head') if record.is_file() else None
    fetched = {}
    for name, url in ((CHANGELOG, manifest.sources['changelog']), (LLMS, manifest.sources['llms'])):
        status, body = fetch(url)
        if status != 200:
            raise FetchError(f'{url}: HTTP {status}')
        fetched[name] = body.decode('utf-8')
    head = releases_of(fetched[CHANGELOG])[0].label
    pages = manifest.pages()
    todo = pages if head != previous else [p for p in pages if not (folder / page_file(p)).is_file()]

    def get(page: str):
        try:
            return page, fetch(page_url(page, manifest.sources)), None
        except FetchError as exc:
            return page, None, str(exc)
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(get, todo))
    errors, unread = [], set()
    for page, got, error in results:
        path = folder / page_file(page)
        if error is None and got[0] not in (200, 404):
            error = f'{page_url(page, manifest.sources)}: HTTP {got[0]}'
        if error is not None:
            errors.append(error)
            unread.add(page)
            path.unlink(missing_ok=True)
        elif got[0] == 404:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(got[1])
    for name, text in fetched.items():
        (folder / name).write_text(text, encoding='utf-8')
    record.write_text(json.dumps({'fetched_at': now.isoformat(timespec='seconds'),
                                  'changelog_head': head}, indent=1) + '\n', encoding='utf-8')
    texts = {p: (folder / page_file(p)).read_text(encoding='utf-8')
             if (folder / page_file(p)).is_file() else None for p in pages}
    return Docs(fetched[CHANGELOG], fetched[LLMS], texts, 'live', errors, unread)


class Finding(NamedTuple):
    group: str
    kind: str               # changed, missing, new or missing-page
    page: str
    key: str | None         # None for a missing page
    candidates: list[str]

    def ref(self) -> str:
        return self.page if self.key is None else self.page + SEP + self.key


def compare(manifest: Manifest, state: dict, terms: dict, docs: Docs) -> tuple[list[Finding], dict]:
    '''R6.5 and R3.7: per group, the changed, missing and new blocks and the
    missing pages, each with its candidate sections, plus the deselected
    blocks for information. A page absent from llms.txt (code pages) or from
    the docs is missing; its blocks are not compared one by one.'''
    slugs = parse_llms(docs.llms)
    findings: list[Finding] = []
    deselected: dict[str, list[str]] = {}
    for gid, group in manifest.groups.items():
        sec_terms = terms[gid]
        watched = set().union(*sec_terms.values())
        base = state['groups'].get(gid, {}).get('blocks', {})
        info: list[str] = []
        for page, mark in group.pages.items():
            if page in docs.unread:
                continue
            text = docs.pages.get(page)
            if text is None or (not is_platform(page) and page not in slugs):
                findings.append(Finding(gid, 'missing-page', page, None, list(sec_terms)))
                continue
            found = page_blocks(text)
            chosen = set(select(found, mark, watched))
            old = base.get(page, {})
            for key, recorded in old.items():
                if key not in found:
                    findings.append(Finding(gid, 'missing', page, key, candidates(key, '', sec_terms)))
                elif key not in chosen:
                    info.append(page + SEP + key)
                elif block_hash(found[key]) != recorded:
                    findings.append(Finding(gid, 'changed', page, key, candidates(key, found[key], sec_terms)))
            for key in found:
                if key in chosen and key not in old:
                    findings.append(Finding(gid, 'new', page, key, candidates(key, found[key], sec_terms)))
        for page in base:
            if page not in group.pages:
                info += [page + SEP + key for key in base[page]]
        deselected[gid] = info
    return findings, deselected


def untriaged(state: dict, releases: list[Release]) -> dict[str, list[str]]:
    '''R6.6: per section, the releases after its `checked`, oldest first.'''
    return {sid: [r.label for r in reversed(releases)
                  if version_key(r.label) > version_key(s['checked']['release'])]
            for sid, s in state['sections'].items()}


def release_notes(releases: list[Release], pending: set[str], terms: dict) -> dict:
    '''Every bullet of each untriaged release, with the sections whose terms
    it contains marked as hints only (R6.6).'''
    flat = {sid: t for group in terms.values() for sid, t in group.items()}
    return {r.label: {'date': r.date.isoformat(),
                      'bullets': [{'text': b, 'hints': [sid for sid, t in flat.items() if any(x in b for x in t)]}
                                  for b in r.bullets]}
            for r in reversed(releases) if r.label in pending}


def due_changelog(state: dict, releases: list[Release], days: int, today: date) -> dict | None:
    '''R6.7: the batch is due once the oldest release newer than some
    section's `checked` is at least `days` old.'''
    floor = min(version_key(s['checked']['release']) for s in state['sections'].values())
    pending = [r for r in releases if version_key(r.label) > floor]
    if not pending:
        return None
    oldest = pending[-1]
    due_from = oldest.date + timedelta(days=days)
    return {'releases': len(pending), 'oldest': oldest.label, 'oldest_date': oldest.date.isoformat(),
            'due_from': due_from.isoformat(), 'due': today >= due_from}


def due_probes(manifest: Manifest, rows: list[ProbeRow], newest: str, days: int, today: date) -> list[dict]:
    '''R6.7: a registered probe is due with no row; with a DIVERGES row and no
    later PASS; or `days` after its last row once a release has shipped past
    that row's version.'''
    out = []
    for pid in manifest.probes:
        mine = [r for r in rows if r.probe == pid]
        if not mine:
            out.append({'probe': pid, 'why': 'never run'})
            continue
        diverged = False
        for r in mine:
            diverged = True if r.outcome == 'DIVERGES' else False if r.outcome == 'PASS' else diverged
        last = mine[-1]
        if diverged:
            out.append({'probe': pid, 'why': 'DIVERGES with no later PASS'})
        elif (today - last.date).days >= days and version_key(newest) > version_key(last.version):
            out.append({'probe': pid, 'why': f'last run {last.date.isoformat()} at {last.version}'})
    return out


def due_audit(manifest: Manifest, state: dict, days: int, today: date) -> dict:
    '''R6.7: one clock for every group. An audit is due `days` after the most
    recent audit of any group, and targets the group with the oldest
    `audited` date, ties broken in manifest order.'''
    def day(sid: str) -> date:
        return date.fromisoformat(state['sections'][sid]['audited']['date'])
    groups = {gid: min(day(s) for s in g.sections if s in state['sections'])
              for gid, g in manifest.groups.items() if any(s in state['sections'] for s in g.sections)}
    last = max(day(s) for s in state['sections'])
    due_from = last + timedelta(days=days)
    return {'group': min(groups, key=groups.get), 'last_audit': last.isoformat(),
            'due_from': due_from.isoformat(), 'due': today >= due_from}


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def check(source: Source, cache: Path, *, docs_dir: Path | None, today: date, now: datetime,
          fetch: Fetch) -> tuple[int, dict, Path]:
    '''Run R6 against one set of inputs: (exit code, report, report path).
    Exit 0 when nothing is due, 1 when something is, 2 on an error. Writes
    only under the cache, never inside the repo (R6.10).'''
    manifest_text = source.require(MANIFEST)
    manifest = parse_manifest(manifest_text)
    baseline_text = source.require(BASELINE)
    state = parse_baseline(baseline_text)
    guide_text = source.require(manifest.guide)
    rows = parse_probes(source.read(PROBES))
    terms = group_terms(manifest, guide_text)
    errors: list[str] = []
    try:
        docs = offline_docs(manifest, docs_dir) if docs_dir else live_docs(manifest, cache, fetch, now)
    except FetchError as exc:
        docs = None
        errors.append(str(exc))
    releases = releases_of(docs.changelog) if docs else None
    report: dict = {'generated_at': now.isoformat(timespec='seconds'), 'inputs': source.label,
                    'docs': docs.origin if docs else None,
                    'hashes': {'manifest': sha256(manifest_text), 'baseline': sha256(baseline_text),
                               'guide': sha256(guide_text)}}
    violations, notes = lint(guide_text, manifest, state, {r.label for r in releases} if releases else None)
    report['lint'] = {'violations': violations, 'notes': notes}
    due = {'lint': len(violations)}
    if docs is not None:
        errors += docs.errors
        findings, deselected = compare(manifest, state, terms, docs)
        pending = untriaged(state, releases)
        slugs = parse_llms(docs.llms)
        report.update({
            'latest_release': releases[0].label,
            'findings': {gid: [f._asdict() for f in findings if f.group == gid] for gid in manifest.groups},
            'deselected': deselected,
            'llms': {'added': sorted(slugs - set(state['llms'])), 'removed': sorted(set(state['llms']) - slugs)},
            'untriaged': pending,
            'releases': release_notes(releases, {l for ls in pending.values() for l in ls}, terms),
        })
        due.update({'blocks': len(findings),
                    'changelog': due_changelog(state, releases, manifest.cadence['changelog_days'], today),
                    'probes': due_probes(manifest, rows, releases[0].label, manifest.cadence['probe_days'], today),
                    'audit': due_audit(manifest, state, manifest.cadence['audit_days'], today)})
    report['due'] = due
    report['errors'] = errors
    anything = (due['lint'] or due.get('blocks') or (due.get('changelog') or {}).get('due')
                or due.get('probes') or (due.get('audit') or {}).get('due'))
    code = 2 if errors else 1 if anything else 0
    report['exit'] = code
    path = cache / 'reports' / f'{sha256(baseline_text)[:12]}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    return code, report, path


def summary(report: dict, path: Path) -> list[str]:
    '''The human-readable summary check prints (R6.8).'''
    due = report['due']
    lines = [f"cc-guide check: inputs from {report['inputs']}; docs {report['docs'] or 'unavailable'}"
             + (f"; changelog head {report['latest_release']}" if 'latest_release' in report else '')]
    violations = report['lint']['violations']
    lines.append('lint: clean' if not violations else f'lint: {len(violations)} violation(s), due')
    lines += [f'  {v}' for v in violations]
    if 'findings' in report:
        kinds = [f for group in report['findings'].values() for f in group]
        counts = {k: sum(1 for f in kinds if f['kind'] == k) for k in ('changed', 'missing', 'new', 'missing-page')}
        lines.append(f"blocks: {counts['changed']} changed, {counts['missing']} missing, {counts['new']} new, "
                     f"{counts['missing-page']} missing pages"
                     f"; {sum(map(len, report['deselected'].values()))} deselected (informational)")
        lines += [f"  [{f['group']}] {f['kind']} {f['page'] + (SEP + f['key'] if f['key'] else '')}"
                  f" (candidates: {', '.join(f['candidates'])})" for f in kinds]
        llms = report['llms']
        lines.append(f"llms.txt since the baseline: {len(llms['added'])} added, {len(llms['removed'])} removed")
        batch = due['changelog']
        lines.append('changelog: nothing untriaged' if batch is None else
                     f"changelog: {batch['releases']} release(s) untriaged, oldest {batch['oldest']} "
                     f"({batch['oldest_date']}); batch due from {batch['due_from']}" + (', due' if batch['due'] else ''))
        lines.append('probes: none due' if not due['probes'] else
                     'probes: ' + '; '.join(f"{p['probe']} ({p['why']})" for p in due['probes']))
        audit = due['audit']
        lines.append(f"audit: {audit['group']} due from {audit['due_from']}" + (', due' if audit['due'] else ''))
    lines += [f'error: {e}' for e in report['errors']]
    lines.append({0: 'nothing due', 1: 'something is due', 2: 'error'}[report['exit']] + f'; report {path}')
    return lines
```

> Deviation: `http_get` also catches `http.client.HTTPException`, so a truncated
> read is retried and reported like any fetch failure (ruling 8, 12b0705). Ruling 9
> deferred probe ERROR and unknown outcomes to Stage 5. At the completion gate
> (owner, 2026-10-05; Codex's finding) `compare` tests a baselined block's hash
> before its selection, so a block whose text changed is changed even when it lost
> its term, and R3.7 says so (4ff20bb).

- [x] **Step 6: Run the suite to see it pass.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: `123 passed` (+29). No test reaches the network: every live path goes through a fake `fetch`.

- [x] **Step 7: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && [ "$(git branch --show-current)" = feat/cc-drift-stage1 ] && git add build/cc_guide/cc_fixtures.py build/cc_guide/check.py build/cc_guide/test_check.py && git commit -m "feat(cc_guide): fetch the docs, compare blocks and report what is due

check.py is R6 without R6.8's citing-file lists: the changelog-head
fetch gate with parallel GETs, a 30-second timeout and one retry;
changed, missing and new blocks with candidate sections, and missing
pages; each section's untriaged releases with term hints; every due
rule, including the shared audit clock; and a report keyed by the
baseline's hash, under the cache only. Exit 0, 1 or 2; a network failure
is 2.

Plan 38, Task 9.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 10: The command line (`cli.py`), write sets and the bookkeeping end to end

**Files:**
- Modify: `build/cc_guide/cc_fixtures.py` (append)
- Create: `build/cc_guide/cli.py`
- Test: `build/cc_guide/test_cli.py`

**Interfaces:**
- Consumes: all of `baseline`, `check` (`check`, `http_get`, `summary`), `docs` (`page_file`, `parse_changelog`), `guide.render_stamp`, `lint.lint` and `state`.
- Produces: the command line in the Global Constraints' CLI contract:
  - `REPO`;
  - `parser()`;
  - `cached_releases(cache)`, giving the newest cached changelog's releases or None;
  - `newest_releases(cache)`, which raises `SetupError` when nothing is cached;
  - `git_show(ref, path)`;
  - `main(argv=None, *, today=None, now=None, fetch=None) -> int`.
- `main` turns a `SetupError` into `cc-guide: <message>` and exit 2, and any other exception into a traceback and exit 2.
- Fixtures: `prime_cache(cache, folder, head='2.1.902')`, a cache whose `latest/` looks like a live check left it.

The tests pin each `baseline` subcommand's write set, checked with `git status` and with which state fields changed:
- `init`, `accept`, `advance`, `audited` and `rebaseline` write `baseline.json` only, and `rebaseline` also writes a cache snapshot;
- `stamp` writes the guide's stamp region only;
- nothing commits.

They also pin that `check` reads `main` unless given `--worktree`, that `rebaseline` refuses the bootstrap snapshot, and that a crash exits 2. `test_bookkeeping_alone_brings_check_to_exit_zero` is Validation item 1's bookkeeping bullet: in R8.8's order, the subcommands clear a changed block, untriaged releases and a due audit until `check --worktree` exits 0.

- [x] **Step 1: Append to `build/cc_guide/cc_fixtures.py`,** after two blank lines:

```python
def prime_cache(cache, folder, head: str = '2.1.902') -> None:
    '''A cache whose latest/ holds folder's files, as a live check leaves it.'''
    import json
    import state
    write_tree(state.latest_docs(cache), {p.name: p.read_text(encoding='utf-8') for p in folder.iterdir()})
    state.fetch_record(cache).write_text(json.dumps({'fetched_at': '2026-10-04T12:00:00+00:00',
                                                      'changelog_head': head}) + '\n')
```

- [x] **Step 2: Write the tests.** Create `build/cc_guide/test_cli.py`:

```python
'''Tests for cli.py: exit codes, which inputs each subcommand reads, each
`baseline` subcommand's write set, and the manual bookkeeping that brings
check to exit 0 (drift spec R5, R6.1, R7; Validation 1).'''
import json
from datetime import date

import pytest

import baseline
import cli
import state
from cc_fixtures import (DOCS, GUIDE_IDS, GUIDE_PATH, MANIFEST_TOML, docs_dir, drift_repo,  # noqa: F401
                         fixture_repo, git, guide_text, isolated_home, prime_cache, write_tree)


@pytest.fixture
def world(tmp_path, docs_dir, monkeypatch):
    '''A committed fixture repo, a primed cache, and cli pointed at both.'''
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    cache = tmp_path / 'cache'
    prime_cache(cache, docs_dir)
    monkeypatch.setattr(cli, 'REPO', repo)
    return repo, cache, docs_dir


def main(cache, *argv, today=date(2026, 9, 10)):
    return cli.main(['--cache', str(cache), *argv], today=today)


def load(repo):
    return json.loads((repo / state.BASELINE).read_text())


def dirty(repo):
    return sorted(line[3:] for line in git(repo, 'status', '--porcelain').splitlines())


def test_lint_exits_zero_clean_one_on_a_violation_and_two_on_a_setup_error(world, capsys):
    repo, cache, _ = world
    assert main(cache, 'lint') == 0
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace('Alpha uses', 'Alpha now uses'))
    assert main(cache, 'lint') == 1
    assert capsys.readouterr().out.startswith('section alpha.overview: text differs')
    assert main(cache, 'lint', '--ref', 'main') == 0
    (repo / state.BASELINE).unlink()
    assert main(cache, 'lint') == 2
    assert 'baseline.json: not found in the working tree' in capsys.readouterr().err


def test_check_reads_main_unless_told_otherwise(tmp_path, docs_dir, monkeypatch, capsys):
    repo = fixture_repo(tmp_path / 'repo', {GUIDE_PATH: guide_text()})
    write_tree(repo, {state.MANIFEST: MANIFEST_TOML,
                      state.BASELINE: state.dump_baseline(baseline.init(
                          state.parse_manifest(MANIFEST_TOML), guide_text(), docs_dir, '2.1.900', '2026-09-02',
                          {i: '2.1.900' for i in GUIDE_IDS}))})
    monkeypatch.setattr(cli, 'REPO', repo)
    cache = tmp_path / 'cache'
    assert main(cache, 'check', '--docs', str(docs_dir)) == 2
    assert 'build/cc_guide/manifest.toml: not found in main' in capsys.readouterr().err
    assert main(cache, 'check', '--worktree', '--docs', str(docs_dir)) == 0


def test_init_derives_changed_and_refuses_to_overwrite_without_force(tmp_path, docs_dir, monkeypatch):
    old = '\n'.join(line for line in guide_text().split('\n') if not line.startswith('<!-- cc: '))
    repo = fixture_repo(tmp_path / 'repo', {baseline.OLD_GUIDE_PATH: old.replace('Set `ALPHA_ENV`', 'Set `OLD`')})
    july = git(repo, 'rev-parse', 'HEAD').strip()
    write_tree(repo, {baseline.OLD_GUIDE_PATH: old})
    git(repo, 'commit', '-qam', 'refresh')
    refresh = git(repo, 'rev-parse', 'HEAD').strip()
    write_tree(repo, {GUIDE_PATH: guide_text(), state.MANIFEST: MANIFEST_TOML})
    git(repo, 'add', '-A')
    git(repo, 'commit', '-qm', 'the anchored guide and its manifest')
    monkeypatch.setattr(cli, 'REPO', repo)
    monkeypatch.setattr(baseline, 'JULY', (july, '2.1.219'))
    monkeypatch.setattr(baseline, 'REFRESH', (refresh, '2.1.288'))
    cache = tmp_path / 'cache'
    argv = ('baseline', 'init', '--docs', str(docs_dir), '--release', '2.1.900', '--date', '2026-09-02')
    assert main(cache, *argv) == 0
    assert dirty(repo) == [state.BASELINE]
    written = load(repo)
    assert {i: s['changed'] for i, s in written['sections'].items()} == {
        'alpha.overview': '2.1.219', 'alpha.reference': '2.1.288',
        'beta.overview': '2.1.219', 'beta.reference': '2.1.219'}
    assert main(cache, *argv) == 2
    assert main(cache, *argv, '--force') == 0


def changed_fields(old, new):
    out = {f'sections.{i}.{k}' for i in old['sections'] for k in old['sections'][i]
           if old['sections'][i][k] != new['sections'][i][k]}
    out |= {f'groups.{g}' for g in old['groups'] if old['groups'][g] != new['groups'][g]}
    return out | ({'llms'} if old['llms'] != new['llms'] else set())


def test_advance_writes_only_the_named_sections_checked(world):
    repo, cache, _ = world
    before = load(repo)
    assert main(cache, 'baseline', 'advance', 'beta.overview', '--to', '2.1.902') == 0
    assert dirty(repo) == [state.BASELINE]
    assert changed_fields(before, load(repo)) == {'sections.beta.overview.checked'}


def test_audited_writes_only_the_groups_audited_and_checked(world, capsys):
    repo, cache, _ = world
    before = load(repo)
    assert main(cache, 'baseline', 'audited', 'alpha', today=date(2026, 10, 4)) == 0
    assert dirty(repo) == [state.BASELINE]
    assert changed_fields(before, load(repo)) == {
        'sections.alpha.overview.audited', 'sections.alpha.overview.checked',
        'sections.alpha.reference.audited', 'sections.alpha.reference.checked'}
    assert capsys.readouterr().err == ''  # beta's sections still hold the oldest dates
    assert main(cache, 'baseline', 'audited', 'beta', today=date(2026, 10, 4)) == 0
    assert capsys.readouterr().err == 'the stamp region is now stale: run baseline stamp\n'


def test_accept_writes_only_the_named_sections_hash_and_changed(world):
    repo, cache, _ = world
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace('Alpha uses', 'Alpha now uses'))
    git(repo, 'commit', '-qam', 'edit the guide')
    before = load(repo)
    assert main(cache, 'baseline', 'accept', 'alpha.overview', '--editorial') == 0
    assert changed_fields(before, load(repo)) == {'sections.alpha.overview.text_hash'}
    assert main(cache, 'baseline', 'accept', 'alpha.overview', '--substantive') == 0
    assert changed_fields(before, load(repo)) == {'sections.alpha.overview.text_hash',
                                                  'sections.alpha.overview.changed'}
    assert load(repo)['sections']['alpha.overview']['changed'] == '2.1.902'
    assert dirty(repo) == [state.BASELINE]


def test_rebaseline_writes_the_baseline_and_a_cache_snapshot_only(world):
    repo, cache, folder = world
    write_tree(state.latest_docs(cache), {'tools.md': DOCS['tools.md'].replace('alpha jobs', 'alpha batches')})
    before = load(repo)
    assert main(cache, 'baseline', 'rebaseline', 'alpha') == 0
    assert dirty(repo) == [state.BASELINE]
    assert changed_fields(before, load(repo)) == {'groups.alpha'}
    assert sorted(p.name for p in state.snapshot_docs(cache, '2.1.902').iterdir()) == ['env-vars.md', 'tools.md']


def test_stamp_writes_only_the_guides_stamp_region(world):
    repo, cache, _ = world
    main(cache, 'baseline', 'advance', *GUIDE_IDS, '--to', '2.1.902', today=date(2026, 10, 4))
    git(repo, 'commit', '-qam', 'advance')
    assert main(cache, 'baseline', 'stamp') == 0
    assert dirty(repo) == [GUIDE_PATH]
    diff = [l for l in git(repo, 'diff', '-U0').splitlines() if l[:1] in '+-' and l[:3] not in ('+++', '---')]
    assert diff == ['-> Checked against the Claude Code docs and changelog through 2.1.900 on 2026-09-02; '
                    'oldest full re-verification 2026-09-02, at 2.1.900.',
                    '+> Checked against the Claude Code docs and changelog through 2.1.902 on 2026-10-04; '
                    'oldest full re-verification 2026-09-02, at 2.1.900.']


def test_rebaseline_never_writes_the_bootstrap_snapshot(world, capsys):
    repo, cache, folder = world
    prime_cache(cache, folder, head='2.1.288')
    assert main(cache, 'baseline', 'rebaseline', 'alpha') == 2
    assert 'never written' in capsys.readouterr().err
    assert not state.snapshot_docs(cache, '2.1.288').exists()
    assert dirty(repo) == []


def test_a_malformed_cached_changelog_exits_two(world, capsys):
    _, cache, _ = world
    changelog = state.latest_docs(cache) / 'changelog.md'
    changelog.write_text(changelog.read_text().replace('October 1, 2026', '2026-10-01'))
    assert main(cache, 'lint') == 2
    assert 'changelog line 8:' in capsys.readouterr().err


def test_a_crash_exits_two_never_one(world, monkeypatch, capsys):
    '''R6.9: an unexpected exception must not read as 1, "due".'''
    _, cache, _ = world

    def crash(*args):
        raise RuntimeError('boom')
    monkeypatch.setattr(cli, 'run_lint', crash)
    assert main(cache, 'lint') == 2
    assert 'RuntimeError: boom' in capsys.readouterr().err


def test_bookkeeping_alone_brings_check_to_exit_zero(world):
    '''Validation 1: after a manual review, the Stage 1 subcommands clear
    every due item, in R8.8's order, with no Stage 3 skill.'''
    repo, cache, folder = world
    write_tree(folder, {'events.md': DOCS['events.md'].replace('fires on beta', 'fires on gamma')})
    prime_cache(cache, folder)
    today = date(2026, 10, 5)
    check_args = ('check', '--worktree', '--docs', str(folder))
    assert main(cache, *check_args, today=today) == 1
    assert main(cache, 'baseline', 'rebaseline', 'beta', today=today) == 0
    assert main(cache, 'baseline', 'advance', *GUIDE_IDS, '--to', '2.1.902', today=today) == 0
    assert main(cache, 'baseline', 'audited', 'alpha', today=today) == 0
    assert main(cache, 'baseline', 'stamp', today=today) == 0
    assert main(cache, 'lint', today=today) == 0
    assert main(cache, *check_args, today=today) == 0
    assert main(cache, 'check', '--docs', str(folder), today=today) == 1
```

> Deviation: six `(out, err)` checks are exact (aec437b). On the owner's call
> (ruling 10), the malformed-changelog test, renamed, also rejects a changelog with
> no `<Update>` block (6ce360b). The crash test also crashes before `main`'s `try`
> (c6f3477). The final review pinned the snapshot's bytes (bfbc2d5).

- [x] **Step 3: Create the stub** `build/cc_guide/cli.py`, holding only `'''cc_guide's command line (Stage 1 of specs/claude-code-drift-automation.md).'''`

- [x] **Step 4: Run the tests to see them fail.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rfE test_cli.py`
Expected: `2 failed, 10 errors`. The ten ERRORs come at the `world` fixture's setup and the two FAILEDs from the tests that patch `cli.REPO` themselves. All twelve are `AttributeError: <module 'cli' …> has no attribute 'REPO'`.

- [x] **Step 5: Implement.** Replace `build/cc_guide/cli.py` with:

```python
#!/usr/bin/env python3
'''cc_guide: the drift detector for specs/guides/claude-code-customization-guide.md
(Stage 1 of specs/claude-code-drift-automation.md).

Run: uv run --python 3.13 python build/cc_guide/cli.py <subcommand>

  lint [--ref REF]
      Offline gate over the guide, manifest.toml and baseline.json (R5). Reads
      the working tree unless --ref names a commit. Exit 0 clean, 1 with one
      line per violation, 2 on a setup error.
  check [--ref REF | --worktree] [--docs DIR]
      Fetch the docs when the changelog head moved, compare, and report what
      is due (R6). Reads main's commit unless --ref or --worktree says
      otherwise; --docs DIR runs offline against a local copy. Writes only
      under the cache. Exit 0 nothing due, 1 something due, 2 an error.
  baseline init [--docs DIR] [--release LABEL] [--date YYYY-MM-DD] [--force]
  baseline rebaseline GROUP [PAGE | 'PAGE › KEY' ...]
  baseline advance ID [ID ...] --to RELEASE
  baseline audited GROUP
  baseline accept ID [ID ...] (--substantive | --editorial)
  baseline stamp
      The only writer of baseline.json and the guide's stamp region (R7).
      Always the working tree; nothing is committed.

After reviewing what check reported, record it in R8.8's order: accept,
rebaseline, advance or audited, then stamp; then run lint and
build/check_conformance.py. advance and audited can move the oldest
`checked`, which the stamp names, so stamp follows them. A missing page
needs a manifest.toml edit first: rebaseline keeps its entries. `checked`
and `audited` record the day the check or audit was done, not the
release's date.
'''
import argparse
import json
import subprocess
import sys
import traceback
from datetime import date, datetime
from pathlib import Path

import baseline
from check import check, http_get, summary
from docs import page_file, parse_changelog
from guide import render_stamp
from lint import lint
from state import (BASELINE, BOOTSTRAP_DATE, BOOTSTRAP_RELEASE, MANIFEST, SetupError, Source, default_cache,
                   dump_baseline, fetch_record, latest_docs, newest_changelog, parse_baseline, parse_manifest,
                   snapshot_docs)

REPO = Path(__file__).resolve().parents[2]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='cli.py', description='Claude Code guide drift detector (Stage 1).')
    p.add_argument('--cache', type=Path, help='cache root (default: ~/.cache/agent-skills/cc-guide)')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('lint').add_argument('--ref')
    c = sub.add_parser('check')
    where = c.add_mutually_exclusive_group()
    where.add_argument('--ref', default='main')
    where.add_argument('--worktree', action='store_true')
    c.add_argument('--docs', type=Path)
    b = sub.add_parser('baseline').add_subparsers(dest='action', required=True)
    init = b.add_parser('init')
    init.add_argument('--docs', type=Path)
    init.add_argument('--release', default=BOOTSTRAP_RELEASE)
    init.add_argument('--date', default=BOOTSTRAP_DATE)
    init.add_argument('--force', action='store_true')
    rb = b.add_parser('rebaseline')
    rb.add_argument('group')
    rb.add_argument('refs', nargs='*')
    adv = b.add_parser('advance')
    adv.add_argument('ids', nargs='+')
    adv.add_argument('--to', required=True)
    b.add_parser('audited').add_argument('group')
    acc = b.add_parser('accept')
    acc.add_argument('ids', nargs='+')
    kind = acc.add_mutually_exclusive_group(required=True)
    kind.add_argument('--substantive', action='store_true')
    kind.add_argument('--editorial', action='store_true')
    b.add_parser('stamp')
    return p


def cached_releases(cache: Path):
    '''The newest cached changelog's releases (R5: latest/, else the 2.1.288
    snapshot), or None when neither is cached.'''
    path = newest_changelog(cache)
    if path is None:
        return None
    try:
        return parse_changelog(path.read_text(encoding='utf-8'))
    except ValueError as exc:
        raise SetupError(f'{path}: {exc}') from None


def newest_releases(cache: Path):
    releases = cached_releases(cache)
    if not releases:
        raise SetupError('no cached changelog: run check, or restore the 2.1.288 snapshot')
    return releases


def git_show(ref: str, path: str) -> str:
    proc = subprocess.run(['git', 'show', f'{ref}:{path}'], cwd=REPO, capture_output=True, encoding='utf-8')
    if proc.returncode != 0:
        raise SetupError(f'R11.1 needs {ref}:{path}, which this clone lacks (a shallow clone?)')
    return proc.stdout


def run_lint(args, cache: Path) -> int:
    source = Source(REPO, args.ref)
    manifest = parse_manifest(source.require(MANIFEST))
    state = parse_baseline(source.require(BASELINE))
    releases = cached_releases(cache)
    violations, notes = lint(source.require(manifest.guide), manifest, state,
                             None if releases is None else {r.label for r in releases})
    for line in violations:
        print(line)
    for line in notes:
        print(f'note: {line}', file=sys.stderr)
    return 1 if violations else 0


def run_check(args, cache: Path, today: date, now: datetime, fetch) -> int:
    source = Source(REPO, None if args.worktree else args.ref)
    code, report, path = check(source, cache, docs_dir=args.docs, today=today, now=now, fetch=fetch)
    print('\n'.join(summary(report, path)))
    return code


def run_baseline(args, cache: Path, today: date) -> int:
    tree = Source(REPO)
    manifest = parse_manifest(tree.require(MANIFEST))
    guide_path = REPO / manifest.guide
    guide_text = tree.require(manifest.guide)
    baseline_path = REPO / BASELINE
    day = today.isoformat()
    if args.action == 'init':
        if baseline_path.exists() and not args.force:
            raise SetupError(f'{BASELINE} exists; init rebuilds it from scratch only with --force')
        changed = baseline.derive_changed(git_show(baseline.JULY[0], baseline.OLD_GUIDE_PATH),
                                          git_show(baseline.REFRESH[0], baseline.OLD_GUIDE_PATH), guide_text)
        docs = args.docs or snapshot_docs(cache, BOOTSTRAP_RELEASE)
        if not docs.is_dir():
            raise SetupError(f'{docs}: no snapshot directory')
        state = baseline.init(manifest, guide_text, docs, args.release, args.date, changed)
        baseline_path.write_text(dump_baseline(state), encoding='utf-8')
        print(f'wrote {BASELINE} from {docs}; next: baseline stamp')
        return 0
    state = parse_baseline(tree.require(BASELINE))
    if args.action == 'stamp':
        guide_path.write_text(baseline.stamp(guide_text, state), encoding='utf-8')
        print(f'regenerated the stamp region in {manifest.guide}')
        return 0
    if args.action == 'accept':
        newest = newest_releases(cache)[0].label
        new = baseline.accept(state, guide_text, args.ids, args.substantive, newest)
    elif args.action == 'advance':
        labels = {r.label for r in newest_releases(cache)}
        new = baseline.advance(state, args.ids, args.to, labels, day)
    elif args.action == 'audited':
        new = baseline.audited(state, manifest, args.group, newest_releases(cache)[0].label, day)
    else:
        record = fetch_record(cache)
        if not record.is_file():
            raise SetupError('no latest fetch: run check first')
        release = json.loads(record.read_text(encoding='utf-8'))['changelog_head']
        if release == BOOTSTRAP_RELEASE:
            raise SetupError(f'{snapshot_docs(cache, release)} is the bootstrap snapshot, which is never '
                             'written (R2.6): run check to fetch a newer release first')
        new, pages, notes = baseline.rebaseline(state, manifest, guide_text, args.group, args.refs,
                                                latest_docs(cache), release)
        target = snapshot_docs(cache, release)
        target.mkdir(parents=True, exist_ok=True)
        for page in pages:
            name = page_file(page)
            (target / name).write_bytes((latest_docs(cache) / name).read_bytes())
        for line in notes:
            print(f'note: {line}', file=sys.stderr)
    baseline_path.write_text(dump_baseline(new), encoding='utf-8')
    if render_stamp(new['sections']) != render_stamp(state['sections']):
        print('the stamp region is now stale: run baseline stamp', file=sys.stderr)
    print(f'updated {BASELINE}')
    return 0


def main(argv=None, *, today: date | None = None, now: datetime | None = None, fetch=None) -> int:
    args = parser().parse_args(argv)
    cache = args.cache or default_cache()
    now = now or datetime.now().astimezone()
    today = today or now.date()
    try:
        if args.command == 'lint':
            return run_lint(args, cache)
        if args.command == 'check':
            return run_check(args, cache, today, now, fetch or http_get)
        return run_baseline(args, cache, today)
    except SetupError as exc:
        print(f'cc-guide: {exc}', file=sys.stderr)
        return 2
    except Exception:  # R6.9: a crash must never read as 0, clean, or 1, due
        traceback.print_exc()
        return 2


if __name__ == '__main__':
    sys.exit(main())
```

> Deviation: `main` resolves its cache and dates inside the `try`, so that crash
> exits 2 too, per the Global Constraints' CLI contract (c6f3477). On the owner's
> call (ruling 11), `cached_releases` uses `check.releases_of`, which names its
> source, not `docs.parse_changelog` as the interface list says (873c822).

- [x] **Step 6: Run the suite to see it pass, and smoke-test the command line.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: `135 passed` (+12).

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python build/cc_guide/cli.py --help && uv run --python 3.13 python build/cc_guide/cli.py lint; echo "exit=$?"`
Expected: a usage line listing `{lint,check,baseline}`, then `cc-guide: build/cc_guide/manifest.toml: not found in the working tree` and `exit=2`. Task 11 adds the manifest.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && grep -rnE --include='*.py' --include='*.toml' '^[[:space:]]*(# cc-guide:|<!-- cc-guide:)' build/cc_guide; echo "exit=$?"`
Expected: no lines and `exit=1`, because no citation-shaped line exists in the tool's sources. Plain `grep` is used here, not `git grep`, because this task's files are not yet tracked.

- [x] **Step 7: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && [ "$(git branch --show-current)" = feat/cc-drift-stage1 ] && git add build/cc_guide/cc_fixtures.py build/cc_guide/cli.py build/cc_guide/test_cli.py && git commit -m "feat(cc_guide): add the lint, check and baseline command line

cli.py runs lint (the working tree, or --ref), check (main's commit by
default, --worktree, --docs) and baseline init, rebaseline, advance,
audited, accept and stamp, which write only baseline.json, the guide's
stamp region or cache snapshots, and commit nothing. A setup error or
any crash exits 2. The tests pin every write set, and show the
bookkeeping alone bringing check to exit 0.

Plan 38, Task 10.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 11: The seed manifest (R2.2, R2.5, R11.2) — owner gate

**Controller task.** It stops for the owner before anything is committed.

**Files:**
- Create: `build/cc_guide/manifest.toml`
- Scratch: `.sdd/38-claude-code-drift-automation/manifest_vs_spec.py`

**Interfaces:**
- Consumes: `state.parse_manifest` (Task 6) and the CLI (Task 10).
- Produces: the configuration Tasks 12 and 13 read. No tool writes this file (R2.1).

- [x] **Step 1: Write `build/cc_guide/manifest.toml`** with exactly this content. The six groups follow R2.5's table, their sections follow R1.1's Group column in guide order, and each choice carries a comment:

```toml
# Claude Code guide drift detector: configuration.
#
# Which docs pages back which guide sections, and how often each kind of
# check comes due. Edited by hand, on the owner's decisions; no tool writes
# it (baseline.json is the tool's state). build/cc_guide/cli.py reads it with
# tomllib. Design: specs/claude-code-drift-automation.md (R2).
#
# A page is a code.claude.com slug (`hooks`, `plugins/components`) or a
# platform slug written `platform:<slug>`. On an `all` page every block
# counts; on a `terms` page, only blocks that mention one of the group's
# terms (the backticked spans in its sections' guide text, R3.6).

[guide]
path = 'specs/guides/claude-code-customization-guide.md'

[sources]
docs_base = 'https://code.claude.com/docs/en/'
# llms.txt sits at the docs root; /docs/en/llms.txt is a 404 (2026-10-03).
llms = 'https://code.claude.com/docs/llms.txt'
changelog = 'https://code.claude.com/docs/en/changelog.md'
platform_base = 'https://platform.claude.com/docs/en/'

[cadence]
# A weekly changelog batch, weekly probes, and one group's full audit a month.
changelog_days = 7
probe_days = 7
audit_days = 30

# The six groups are the 2026-10-03 refresh's six verifier scopes, recovered
# from its verifier prompts (R2.5). Their `all` and `terms` marks are the
# seed values, to be tuned after the first live report.

[groups.overview]
sections = [
    'context.overview', 'mechanisms.overview', 'lean.overview', 'lean.measure',
    'lean.session-hygiene', 'lean.mcp', 'lean.ceremony', 'lean.expensive-ops',
]
all = ['context-window', 'costs', 'monitoring-usage']
terms = [
    'mcp', 'commands', 'features-overview', 'debug-your-config', 'best-practices',
    'statusline', 'interactive-mode', 'env-vars', 'memory', 'skills',
]

[groups.skills]
sections = [
    'skills.overview', 'skills.locations', 'skills.frontmatter', 'skills.description',
    'skills.listing-budget', 'skills.progressive-disclosure', 'skills.arguments',
    'skills.iterating', 'commands.overview',
]
all = ['skills']
terms = [
    'commands', 'plugins/components', 'plugins/loading', 'claude-directory',
    'settings-reference', 'env-vars', 'auto-mode-config', 'model-config',
]

[groups.subagents]
sections = ['subagents.overview', 'subagents.frontmatter', 'subagents.tools', 'subagents.isolation']
all = ['sub-agents']
terms = [
    'agents', 'workflows', 'agent-teams', 'model-config', 'env-vars', 'tools-reference',
    'prompt-caching', 'settings-reference', 'cli-reference',
]

[groups.rules]
sections = [
    'rules.overview', 'rules.claude-md', 'rules.hierarchy', 'rules.rules-files',
    'rules.auto-memory', 'rules.settings',
]
all = ['memory', 'settings', 'permissions']
terms = ['settings-reference', 'permission-modes', 'claude-directory', 'large-codebases', 'env-vars']

[groups.hooks]
sections = [
    'hooks.overview', 'hooks.events', 'hooks.exit-codes', 'hooks.handlers',
    'hooks.configuration', 'hooks.patterns', 'hooks.pitfalls',
]
all = ['hooks', 'hooks-guide']
terms = ['settings-reference', 'env-vars']

[groups.models]
sections = ['subagents.models', 'lean.caching', 'lean.model-routing', 'reading.overview']
all = [
    'prompt-caching', 'model-config', 'fast-mode', 'advisor',
    'platform:about-claude/pricing', 'platform:about-claude/models/overview',
]
terms = [
    'platform:build-with-claude/prompt-caching', 'platform:about-claude/model-deprecations',
    'platform:models/haiku-4-5/overview', 'costs', 'env-vars', 'settings-reference', 'commands',
]

# Per-section term tuning (R3.6), none yet. Each entry looks like
#   [sections.'hooks.events']
#   extra_terms = ['...']
#   exclude_terms = ['...']

# Sources deliberately left unmapped. A mapped page matching one is an error.

[[exclusion]]
page = 'whats-new/*'
reason = 'The weekly digests duplicate the changelog.'

[[exclusion]]
page = 'https://www.anthropic.com/news/claude-haiku-4-5'
reason = 'A launch post: a historical figure, and its HTML churns between fetches.'

[[exclusion]]
page = 'changelog'
reason = 'Parsed release by release (R6.6), never hashed as blocks.'

# The probe registry (R10.1) stays empty until Stage 5 registers its probes
# as [[probe]] entries with an id, the sections they back, and optional files.
```

- [x] **Step 2: Check it against the spec.** Create `.sdd/38-claude-code-drift-automation/manifest_vs_spec.py`:

```python
'''Plan 38, Task 11: check the seed manifest against the spec's R1.1 table
(each section's group, in guide order) and R2.5's table (each group's `all`
and `terms` pages). Scratch: never committed. Run from the worktree root:
python .sdd/38-claude-code-drift-automation/manifest_vs_spec.py
'''
import re
import sys
import tomllib
from pathlib import Path

spec = Path('specs/claude-code-drift-automation.md').read_text(encoding='utf-8')
manifest = tomllib.loads(Path('build/cc_guide/manifest.toml').read_text(encoding='utf-8'))
problems = []
r11 = re.findall(r'^\| [^|]+ \| `([a-z0-9.-]+)` \| ([a-z]+) \|$', spec, re.M)
want_sections: dict[str, list[str]] = {}
for sid, group in r11:
    want_sections.setdefault(group, []).append(sid)
r25 = re.findall(r'^\| (overview|skills|subagents|rules|hooks|models) \| ([^|]+) \| ([^|]+) \|$', spec, re.M)


def pages(cell):
    return [p.strip().replace('platform ', 'platform:') for p in cell.split(',')]


groups = manifest['groups']
if list(groups) != [g for g, _, _ in r25]:
    problems.append(f'group order {list(groups)} differs from R2.5')
for gid, all_cell, terms_cell in r25:
    g = groups.get(gid, {})
    if g.get('sections') != want_sections.get(gid):
        problems.append(f'{gid}: sections {g.get("sections")} differ from R1.1 {want_sections.get(gid)}')
    for mark, cell in (('all', all_cell), ('terms', terms_cell)):
        if g.get(mark) != pages(cell):
            problems.append(f'{gid}: {mark} {g.get(mark)} differs from R2.5 {pages(cell)}')
print(f'{len(r11)} sections and {len(r25)} groups read from the spec')
sys.exit('\n'.join(problems) if problems else None)
```

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python .sdd/38-claude-code-drift-automation/manifest_vs_spec.py; echo "exit=$?"`
Expected: `38 sections and 6 groups read from the spec` and `exit=0`.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python build/cc_guide/cli.py lint; echo "exit=$?"`
Expected: `cc-guide: build/cc_guide/baseline.json: not found in the working tree` and `exit=2`. The manifest parsed: an invalid one would print every problem, prefixed `build/cc_guide/manifest.toml:`, before any baseline is read.

- [x] **Step 3: Owner gate (R11.2).** Show the owner the file, its six groups with their `all` and `terms` pages, the three exclusions, and the empty probe registry. Then **stop and ask**: approve as written, or name the changes. Apply any change, rerun Step 2, and log it in the ledger as a deviation for this step. Do not commit before the owner approves.

- [x] **Step 4: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && [ "$(git branch --show-current)" = feat/cc-drift-stage1 ] && git add build/cc_guide/manifest.toml && git commit -m "feat(cc_guide): seed the drift manifest

manifest.toml maps the guide's 38 sections to the refresh's six verifier
scopes and their 39 docs pages, each marked all or terms (R2.5), with
the source URLs, the 7/7/30-day cadences, three reasoned exclusions and
an empty probe registry. The owner reviewed it before this commit
(R11.2).

Plan 38, Task 11.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 12: The stamp region, the seed baseline and the repo lint test (R1.2, R2.6, R5) — owner gate

**Controller task.** It stops for the owner at Step 1.

**Files:**
- Modify: `specs/guides/claude-code-customization-guide.md` (the header's first sentence only)
- Create: `build/cc_guide/baseline.json` (written by `baseline init`)
- Modify: `build/cc_guide/test_cli.py` (append the repo lint test)

**Interfaces:**
- Consumes: the CLI (Task 10), the manifest (Task 11), and the bootstrap snapshot at `~/.cache/agent-skills/cc-guide/2.1.288/docs/`, which `init` only reads.
- Produces: the committed seed state that Task 13's runs read.

- [x] **Step 1: Owner gate: the stamp-region edit (R1.2).** Show the owner the replacement below (decision 7), then **stop and ask** for approval or other wording. Only the text outside the markers is theirs to word. The one line between the markers is what `baseline stamp` generates, and the lint requires it verbatim. The proposal replaces

```markdown
> Facts in this guide were re-verified against the official Claude Code documentation (code.claude.com/docs) and Anthropic's pricing pages on 2026-10-03, at Claude Code 2.1.288 (first verified July 2026, at 2.1.219 — 58 releases earlier). Claude Code changes quickly: items marked ⚠ are the most version-sensitive — confirm them against your installed version (`claude --version`, `/doctor`) before depending on exact numbers or field names.
```

with

```markdown
<!-- cc-guide:stamp -->
> Checked against the Claude Code docs and changelog through 2.1.288 on 2026-10-03; oldest full re-verification 2026-10-03, at 2.1.288.
<!-- /cc-guide:stamp -->

> First verified in July 2026, at Claude Code 2.1.219, 58 releases before the full re-verification at 2.1.288 against the official documentation (code.claude.com/docs) and Anthropic's pricing pages. Claude Code changes quickly: items marked ⚠ are the most version-sensitive — confirm them against your installed version (`claude --version`, `/doctor`) before depending on exact numbers or field names.
```

"58 releases before the full re-verification at 2.1.288" replaces "58 releases earlier", which counted back from 2.1.288 and would go stale at the first restamp. The region sits before the first section, so no section's text, and no `text_hash`, changes.

- [x] **Step 2: Apply the approved edit,** and nothing else in the guide.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && git diff --numstat -- specs/guides/`
Expected: `5	1	specs/guides/claude-code-customization-guide.md` for the proposal as written.

- [x] **Step 3: Build the seed baseline (R2.6).**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python build/cc_guide/cli.py baseline init; echo "exit=$?"`
Expected: `wrote build/cc_guide/baseline.json from /Users/lowell/.cache/agent-skills/cc-guide/2.1.288/docs; next: baseline stamp` and `exit=0`.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python -c "import json, collections; b = json.load(open('build/cc_guide/baseline.json')); print(dict(collections.Counter(s['changed'] for s in b['sections'].values()))); print({g: sum(map(len, v['blocks'].values())) for g, v in b['groups'].items()})" && shasum -a 256 build/cc_guide/baseline.json`
Expected: `{'2.1.288': 32, '2.1.219': 6}` (R11.1) and `{'overview': 496, 'skills': 422, 'subagents': 546, 'rules': 524, 'hooks': 796, 'models': 633}`. With the manifest exactly as Task 11 wrote it, the hash is `5a1c88742f05018e8a7a148fa731af07db695e2cbd75aac8f2e92fb8b4a0c952`, because `init` is deterministic. A manifest the owner changed at Task 11 gives other block counts and another hash; record them in the ledger instead.

- [x] **Step 4: Stamp, then lint.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python build/cc_guide/cli.py baseline stamp && git diff --numstat -- specs/guides/ && uv run --python 3.13 python build/cc_guide/cli.py lint; echo "exit=$?"`
Expected: `regenerated the stamp region in specs/guides/claude-code-customization-guide.md`, the same `5	1` numstat as Step 2 (`stamp` wrote the line the edit already holds), and `exit=0`. The lint read the 2.1.288 snapshot's changelog, since `latest/` does not exist yet, so the release-label check ran.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 --with pyyaml python build/check_conformance.py; echo "exit=$?"`
Expected: `exit=0`. The conformance lint still finds a well-formed anchor under every heading next to the new markers.

- [x] **Step 5: The repo lint test (R5, R12.4).** Append to `build/cc_guide/test_cli.py`:

```python
def test_the_repo_lints_clean(capsys):
    '''R5: the suite enforces the lint on the repo itself. HOME is isolated,
    so no changelog is cached and the release-label check is skipped.'''
    assert cli.main(['lint']) == 0, capsys.readouterr().out
```

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: `136 passed` (+1). The new test reads the real guide, manifest and baseline.

> Deviation: 138 passed, the plan's 136 plus the owner-approved tests of Tasks 4
> and 9.

- [x] **Step 6: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && [ "$(git branch --show-current)" = feat/cc-drift-stage1 ] && git add specs/guides/claude-code-customization-guide.md build/cc_guide/baseline.json build/cc_guide/test_cli.py && git commit -m "feat(cc_guide): stamp the guide and seed the baseline at 2.1.288

The guide's header sentence becomes R1.2's generated stamp region, with
the July history kept as owner prose outside it (the owner reviewed the
edit). baseline.json is init's output over the 2.1.288 snapshot: every
section checked and audited at 2.1.288 on 2026-10-03, changed per R11.1,
and 3,417 selected blocks as hashes. The suite now lints the repo
itself.

Plan 38, Task 12.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 13: First runs (R11.4) — owner gate on the block selection

**Controller task.** It needs the network for Step 2 and stops for the owner at Step 3.

**Files:**
- Possibly modify: `build/cc_guide/manifest.toml` and `build/cc_guide/baseline.json`, only if the owner tunes the marks at Step 3
- Scratch: `.sdd/38-claude-code-drift-automation/selection.py` and `block_diff.py`

**Interfaces:**
- Consumes: everything committed through Task 12.
- Produces: the first live report under `~/.cache/agent-skills/cc-guide/reports/`, and the owner's tuning, if any.

Every `check` here passes `--worktree`, because `main` does not hold the manifest yet. Do not run `advance`, `audited` or `rebaseline` on the real baseline: triaging the backlog since 2.1.288 is Stage 3's first job, or the owner's own manual review (decision 4). R11.4's third bullet, the stale backlog of citing files, needs Stage 2's citations.

- [x] **Step 1: The round trip (R11.4, first bullet).**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python build/cc_guide/cli.py check --worktree --docs ~/.cache/agent-skills/cc-guide/2.1.288/docs; echo "exit=$?"`
Expected:
- `lint: clean`;
- `blocks: 0 changed, 0 missing, 0 new, 0 missing pages; 0 deselected (informational)`;
- `llms.txt since the baseline: 0 added, 0 removed`;
- `changelog: nothing untriaged` and `probes: none due`;
- `audit: overview due from 2026-11-02`.

The baseline round-trips. Judge it on the findings, not the exit: the exit is 0 until 2026-11-01, and from 2026-11-02 it is 1, with only the audit line adding `, due`.

- [x] **Step 2: The live run (R11.4, second bullet).** This fetches `changelog.md`, `llms.txt` and the 39 mapped pages into `~/.cache/agent-skills/cc-guide/latest/`.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python build/cc_guide/cli.py check --worktree; echo "exit=$?"`
Expected:
- `lint: clean`;
- `changelog: N release(s) untriaged, oldest 2.1.289 (2026-10-03); batch due from 2026-10-10`, where N depends on the date, followed by `, due` from 2026-10-10 on;
- a `blocks:` line counting changed, missing and new blocks only where the docs moved since the 2.1.288 snapshot. Any count is possible, including 0, and each finding is listed with its candidate sections;
- `audit: overview due from 2026-11-02`;
- a last line naming the report path.

The exit is 1 if anything is due (a block finding, the batch from 2026-10-10, or the audit from 2026-11-02), and 0 otherwise. Exit 2 means a fetch failed: rerun once, and if it fails again, report the `error:` lines to the owner.

Run, with the report path from the last line: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python -c "import json, sys; u = json.load(open(sys.argv[1]))['untriaged']; print(len(u), all(v and v[0] == '2.1.289' for v in u.values()))" <report path>`
Expected: `38 True`. Every section lists 2.1.289 and later as untriaged.

- [x] **Step 3: Owner gate: the block selection (Validation item 1).** Create the two scratch helpers.

`.sdd/38-claude-code-drift-automation/selection.py`:

```python
'''Plan 38, Task 13: the block-selection summary for the owner gate. Scratch:
never committed. Run from the worktree root:
python .sdd/38-claude-code-drift-automation/selection.py <docs dir> [<report.json>]

Prints, per group and mapped page, the page's mark, how many blocks the page
has in <docs dir> and how many the group's terms select, then each group's
terms. With a check report, it adds that report's findings per group.
'''
import json
import sys
from pathlib import Path

REPO = Path.cwd()
sys.path.insert(0, str(REPO / 'build' / 'cc_guide'))
from blocks import page_blocks, select  # noqa: E402
from docs import page_file  # noqa: E402
from state import BASELINE, MANIFEST, group_terms, parse_baseline, parse_manifest  # noqa: E402

manifest = parse_manifest((REPO / MANIFEST).read_text(encoding='utf-8'))
state = parse_baseline((REPO / BASELINE).read_text(encoding='utf-8'))
terms = group_terms(manifest, (REPO / manifest.guide).read_text(encoding='utf-8'))
folder = Path(sys.argv[1])
report = json.loads(Path(sys.argv[2]).read_text(encoding='utf-8')) if len(sys.argv) > 2 else None
for gid, group in manifest.groups.items():
    watched = set().union(*terms[gid].values())
    print(f'[{gid}] {len(watched)} terms')
    for page, mark in group.pages.items():
        path = folder / page_file(page)
        if not path.is_file():
            print(f'  {page:45} {mark:5}  absent from {folder}')
            continue
        found = page_blocks(path.read_text(encoding='utf-8'))
        chosen = select(found, mark, watched)
        baselined = len(state['groups'][gid]['blocks'].get(page, {}))
        print(f'  {page:45} {mark:5}  {len(chosen):4} of {len(found):4} blocks selected; {baselined} baselined')
    print('  terms: ' + ', '.join(sorted(watched)))
    if report is not None:
        for f in report.get('findings', {}).get(gid, []):
            key = '' if f['key'] is None else ' › ' + f['key']
            print(f"  finding: {f['kind']} {f['page']}{key} (candidates: {', '.join(f['candidates'])})")
```

`.sdd/38-claude-code-drift-automation/block_diff.py`:

```python
'''Plan 38, Task 13: for each changed block in a check report, diff the
baselined text (the group's snapshot release) against latest/. The output is
docs text: show it in the session only, never save it in the repo. Scratch:
never committed. Run from the worktree root:
python .sdd/38-claude-code-drift-automation/block_diff.py <report.json> [<cache>]
'''
import difflib
import json
import sys
from pathlib import Path

REPO = Path.cwd()
sys.path.insert(0, str(REPO / 'build' / 'cc_guide'))
from blocks import page_blocks  # noqa: E402
from docs import page_file  # noqa: E402
from state import BASELINE, default_cache, latest_docs, parse_baseline, snapshot_docs  # noqa: E402

report = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
cache = Path(sys.argv[2]) if len(sys.argv) > 2 else default_cache()
state = parse_baseline((REPO / BASELINE).read_text(encoding='utf-8'))
for gid, found in report.get('findings', {}).items():
    for f in found:
        if f['kind'] != 'changed':
            continue
        release = state['groups'][gid]['snapshot'][f['page']]
        name = page_file(f['page'])
        old = page_blocks((snapshot_docs(cache, release) / name).read_text(encoding='utf-8'))[f['key']]
        new = page_blocks((latest_docs(cache) / name).read_text(encoding='utf-8'))[f['key']]
        print(f"== [{gid}] {f['page']} › {f['key']} (candidates: {', '.join(f['candidates'])})")
        print('\n'.join(difflib.unified_diff(old.split('\n'), new.split('\n'), 'baselined', 'latest',
                                             lineterm='', n=0)))
```

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python .sdd/38-claude-code-drift-automation/selection.py ~/.cache/agent-skills/cc-guide/2.1.288/docs <report path>`
Expected: per group and page, the mark and `S of T blocks selected; S baselined`, with the two counts agreeing, then each group's terms and the report's findings. For example, rules' `settings-reference` (a `terms` page) shows `252 of 589`.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python .sdd/38-claude-code-drift-automation/block_diff.py <report path>`
Expected: one diff per changed block, baselined text against latest. This is docs text: show it in the session, and never save it in the repo.

Show the owner both outputs. Point out pages whose `terms` selection looks too broad, such as more than a third of a page, or empty. Then **stop and ask**: keep the marks, or tune `all`/`terms` and per-section `extra_terms`/`exclude_terms` in `manifest.toml`. Record the answer in the ledger.

- [x] **Step 4: Only if the owner tuned the manifest: rebuild and round-trip again.** `init --force` rebuilds from the 2.1.288 snapshot. A `rebaseline` would absorb the docs' edits since then (decision 15).

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python build/cc_guide/cli.py baseline init --force && uv run --python 3.13 python build/cc_guide/cli.py baseline stamp && git diff --numstat -- specs/guides/ && uv run --python 3.13 python build/cc_guide/cli.py lint; echo "exit=$?"`
Expected: the `wrote …` and `regenerated …` lines, no guide numstat (the dates did not change, so neither did the stamp), and `exit=0`.

Then rerun Step 1's command, with Step 1's expectations, and the suite:
`cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: `136 passed`.

> Deviation: the owner tuned two marks (2026-10-05): `monitoring-usage` from `all` to
> `terms` in overview, and `model-deprecations` from `terms` to `all` in models. The
> rebuilt baseline holds 3,263 blocks in 4,154 lines (sha256 `6fa76f7c…`), superseding
> decision 18's and Task 12's seed figures (3,417 blocks, 4,308 lines); 138 passed.

- [x] **Step 5: Commit, only if Step 4 ran.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && [ "$(git branch --show-current)" = feat/cc-drift-stage1 ] && git add build/cc_guide/manifest.toml build/cc_guide/baseline.json && git commit -m "feat(cc_guide): tune the block selection after the first live report

The owner reviewed the first live report's selection and tuned the
manifest's marks; init --force rebuilt the baseline from the 2.1.288
snapshot, and the round trip again reports no changed, missing or new
blocks.

Plan 38, Task 13.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

If the owner kept the marks, there is nothing to commit. Note "no tuning" for this step in the ledger.

---

### Task 14: Documentation (R12.7)

**Files:**
- Modify: `CLAUDE.md` (the Build tooling paragraph; the Commands block gains the detector's commands)
- Modify: `build/CLAUDE.md` (append a `cc_guide/` paragraph)

**Interfaces:**
- Consumes: Task 2's CLAUDE.md, and the CLI.
- Produces: CLAUDE.md at 176 lines (the budget table's Stage 1 line).

- [x] **Step 1: The Build tooling paragraph names the detector.** In `CLAUDE.md`, replace the one-line paragraph

```markdown
`build/` holds the repo's lints and commit gates, the cross-runtime adapter generator (`sync_runtime_assets.py`), and the citation-verification pipeline for `recommend-probabilistic-model`; `build/CLAUDE.md` describes each. **`build/.scratch/` is gitignored and must never be committed** — it contains own-use extraction of CC-BY-NC-ND material.
```

with

```markdown
`build/` holds the repo's lints and commit gates, the cross-runtime adapter generator (`sync_runtime_assets.py`), the Claude Code guide's drift detector (`cc_guide/`), and the citation-verification pipeline for `recommend-probabilistic-model`; `build/CLAUDE.md` describes each. **`build/.scratch/` is gitignored and must never be committed** — it contains own-use extraction of CC-BY-NC-ND material.
```

- [x] **Step 2: The Commands block gains the suite and the `lint` and `check` invocations, with no count** (R12.7 as amended). Replace

```markdown
uv run --python 3.13 --with pyyaml python build/check_conformance.py

# Dependency drift: skill and command text vs install.py's DEPENDENCIES (run before committing a skill
```

with

```markdown
uv run --python 3.13 --with pyyaml python build/check_conformance.py

# Claude Code guide drift detector (build/cc_guide/): its suite; lint, run before committing a change to the guide or
# build/cc_guide/; check, which fetches the docs and reports what is due (exit 1 = due; reads main unless --worktree)
cd build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q
uv run --python 3.13 python build/cc_guide/cli.py lint
uv run --python 3.13 python build/cc_guide/cli.py check

# Dependency drift: skill and command text vs install.py's DEPENDENCIES (run before committing a skill
```

- [x] **Step 3: `build/CLAUDE.md` gains a `cc_guide/` paragraph** (R12.7, second bullet). Append, after one blank line:

```markdown
`cc_guide/` holds two tools for `specs/guides/claude-code-customization-guide.md`.
`conformance.toml` is the register `check_conformance.py` reads. The rest is
the drift detector (`specs/claude-code-drift-automation.md`): `manifest.toml`
is the owner's configuration, `baseline.json` its state, written only by
`cli.py baseline`, and `cli.py --help` lists the subcommands. `check` fetches
the docs into `~/.cache/agent-skills/cc-guide/`, never into the repo, and
reads `main`'s commit unless given `--worktree`. After reviewing what it
reports, record the review in this order: `baseline accept`,
`baseline rebaseline`, `baseline advance` or `baseline audited`, then
`baseline stamp`; then run `cli.py lint` and `check_conformance.py`. A
missing page needs a `manifest.toml` edit first. A correction that resolves a
conformance gap removes its `[[exception]]` in the same change. Nothing is
committed for you. `cd build && pytest` collects this suite too, so module and
test basenames stay unique across `build/`.
```

- [x] **Step 4: Verify.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && wc -l < CLAUDE.md && uv run --python 3.13 python .sdd/38-claude-code-drift-automation/claude_md_audit.py --counts-only; echo "exit=$?"; uv run --python 3.13 --with pyyaml python build/check_conformance.py; echo "exit=$?"`
Expected: `176`, then the audit's summary line and `exit=0` (no count crept in: "exit 1" is an allowed exit code), then `exit=0` from the conformance lint.

Run each documented command as written. The `check` line reads `main`, which does not hold the manifest until this branch merges, so that one is expected to fail:
`cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q`, then
`cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python build/cc_guide/cli.py lint; echo "exit=$?"; uv run --python 3.13 python build/cc_guide/cli.py check; echo "exit=$?"`
Expected: `136 passed`; then `exit=0`; then `cc-guide: build/cc_guide/manifest.toml: not found in main` and `exit=2`. That is R6.1's default, shown working.

> Deviation: 138 passed (Task 12's note).

- [x] **Step 5: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && [ "$(git branch --show-current)" = feat/cc-drift-stage1 ] && git add CLAUDE.md build/CLAUDE.md && git commit -m "docs: document the Claude Code guide drift detector

CLAUDE.md's Commands block gains the cc_guide suite and the lint and
check invocations, with no test count (drift R12.7 as amended; 176
lines). build/CLAUDE.md describes cc_guide/ and the manual bookkeeping
order: accept, rebaseline, advance or audited, then stamp, then lint and
check_conformance.py.

Plan 38, Task 14.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 15: Validation (spec, Validation and acceptance)

**Controller task.** It runs every gate and checks each validation item. Nothing is committed unless a fix is needed.

- [x] **Step 1: The detector.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: `136 passed`.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python build/cc_guide/cli.py lint; echo "exit=$?"; uv run --python 3.13 python build/cc_guide/cli.py check --worktree --docs ~/.cache/agent-skills/cc-guide/2.1.288/docs; echo "exit=$?"`
Expected: lint gives `exit=0`, now checking release labels against Task 13's `latest/` changelog. The round trip matches Task 13 Step 1.

> Deviation: 138 passed before the final review, and 140 after its fixes.

- [x] **Step 2: Every existing gate (Validation item 6, as amended).** Run each exactly as written. Every command `cd`s by absolute path, so neither the order nor the shell's working directory matters.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`: exit 0.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python build/check_provenance.py`: exit 0.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 python build/check_snippets.py skills/`: exit 0 (Tier 1).
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies`: `1 passed`.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1/build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q -rf`: the failures are exactly the four named in Global Constraints ("Baseline and counts"), the skips are unchanged, and passed is the baseline's +136.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check`: exit 0. Then `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 status --short runtimes/`: empty, so no adapter changed.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && uv run --python 3.13 --with pyyaml python build/check_conformance.py`: exit 0.

> Deviation: 395 passed, 4 failed and 10 skipped before the final review (257 +
> 138), and 397 passed after its fixes, with the same four failures.

- [x] **Step 3: Validation item 1, as amended.**
  - The round trip reports no changed, missing or new blocks (Task 13 Step 1; Step 1 above).
  - The live run listed 2.1.289 and later as untriaged for all 38 sections, reported changed blocks only where the docs moved (each shown by `block_diff.py`), and exited 1 only when something was due (Task 13 Step 2).
  - The owner reviewed the first live report's block selection and tuned or kept the marks (Task 13 Step 3).
  - The row fixture passes (`test_editing_one_row_flags_only_the_groups_whose_terms_match_it`), and the lint passes on the converted guide (`test_the_repo_lints_clean`; Step 1).
  - The bookkeeping clears what it resolves, and each write set holds (`test_bookkeeping_alone_brings_check_to_exit_zero` and the write-set tests in `test_cli.py`).
  - CLAUDE.md is under 200 lines, both exceptions are gone, and no count remains:

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && wc -l < CLAUDE.md && grep -n "claude-md-size\|claude-md-fast-changing" build/cc_guide/conformance.toml && uv run --python 3.13 python .sdd/38-claude-code-drift-automation/claude_md_audit.py --counts-only; echo "exit=$?"`
Expected: `176`, the single line `id = 'claude-md-size'`, the audit's summary line, and `exit=0`.

- [x] **Step 4: Repo hygiene.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-38-cc-drift-stage1 && git status --short && git ls-files build/cc_guide | wc -l && grep -rnE --include='*.py' --include='*.toml' '^[[:space:]]*(# cc-guide:|<!-- cc-guide:)' build/cc_guide; echo "exit=$?"`
Expected: no `git status` output (`.sdd/` is gitignored); `20` tracked files (`conformance.toml`, `manifest.toml`, `baseline.json`, `cc_fixtures.py`, the eight modules and their eight test files); no grep match, and `exit=1`.

- [x] **Step 5: Request the final review** per subagent-driven-development: both seats, the whole-branch `code-reviewer` and the Codex second opinion, from `main`'s merge-base to `HEAD`. Then run the Plan Completion Protocol below.

> Deviation: the configured Codex model was rejected for the ChatGPT-account login,
> so the second seat ran with the owner's per-run `-m gpt-6-astra` (Codex reviewed
> 6595f16). The fixes: four test pins (bfbc2d5); at the completion gate, Codex's
> deselection finding (4ff20bb) and the text this plan made stale (6127580).

---

## Plan completion

Run writing-plans' Plan Completion Protocol after Task 15 and the final review. This plan's specifics:

- **Ticks** (step 3), in `specs/deferred_items.md`:
  - "Bring the root CLAUDE.md under 200 lines" (section `35-claude-code-guide-conformance`): `- [x] … → done in plan 38`. Use the deferred tick-pass check: the box itself must change, not only the note.
  - The `fixture=<name>` snippet-note item (plan 33's section) only if the owner agrees at the gate that Task 2's pointer closes it (decision 21).
- **Gate questions** (step 1), batched with any leftovers:
  - What to do with each entry under "Text this plan makes stale": fix now, defer as an item, or leave.
  - Whether to log the drift spec's Out-of-scope list now or at the stage plan that retires the spec. The recommendation is the retiring plan, since Stages 2–5 remain.
- **Deferred items** (step 3) go in a `## 38-claude-code-drift-automation — <date>` section, only for leftovers the gate defers. Each follows `skills/writing-plans/references/deferred-backlog.md`'s schema. Stage 2's own scope (citations, `cite`, `accept`'s citer stamps) is the spec's to track, not a deferred item.
- **Retire** (step 5): `git mv` this plan to `specs/plans/completed/`. The spec stays in `specs/`, because Stages 2–5 remain and no other live plan implements it yet. Re-point this plan's relative links, if any, for its new depth.
- **Report the backlog line** from `deferred_stats.py` (step 4), and run the triage rubric if the thresholds hit.
- **Integration** is finishing-a-development-branch's call: merge, PR or keep. Nothing is pushed without the owner. After a merge into `main`:
  - run `uv run --python 3.13 --with pyyaml python build/check_conformance.py` and `uv run --python 3.13 python build/cc_guide/cli.py lint` on the merged result;
  - run `cli.py check`, which now reads `main`. It exits 1 while the batch since 2.1.288 waits for triage (due from 2026-10-10), as designed.
  - If the handoff-briefs plan merged first, recheck CLAUDE.md's length against the 200-line limit (Global Constraints, "Coordination").

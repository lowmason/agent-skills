# Claude Code Guide Tooling Hardening Implementation Plan

**Status: COMPLETE (2026-10-08)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Where this runs.** This plan lands on `main` with the merge of `chore/deferred-2026-10-08`, which also carries the quick fixes it builds on. Run the pre-flight in Global Constraints ("Worktree"), then create the worktree by hand from the main checkout and execute there:
> `/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening`, branch `chore/cc-guide-hardening`. Every command below `cd`s to that absolute path. Never use `EnterWorktree`: it bases on `origin/main`, which may lack an unpushed merge.

**Goal:** Close four deferred items from plan 38's final review: one anchor grammar for the guide (item 45), a `cc-guide:` line for every input error (item 46), the missing tests and edge cases in `build/cc_guide/` (item 49), and its style and naming fixes (item 50).

**Architecture:** No new module. `check_conformance.py` reads the guide's anchors through `guide.scan`. Input errors become `SetupError`s at the read sites (`state.read_utf8`, `state.read_fetch`) or are refused up front (`baseline init`). The repeated regular expressions move to the module that owns each grammar, and `parse_manifest` splits into one helper per table. The rest is tests that pin existing behavior, plus small fixes to messages and names. The tasks run module by module, in the dependency order of the drift spec's Layout.

**Tech Stack:** Python 3.13 through `uv run`, stdlib only; pytest; git. There is no CI. The gates are the suites and lints named in each task.

**Requirements:** there is no spec. The requirements are four items in `specs/deferred_items.md`, section `38-claude-code-drift-automation — 2026-10-05`, selected at the `/deferred` triage of 2026-10-08:
- "Unify the guide's anchor grammar" (item 45);
- "Every input error prints a `cc-guide:` line" (item 46);
- "Test coverage and edge cases in `build/cc_guide/`" (item 49);
- "Style, DRY and naming in `build/cc_guide/`" (item 50).

Codes such as `T7-m4` or `FR-m5` name plan 38's final-review findings as those items record them. R-numbers point into `specs/claude-code-drift-automation.md`. The Planning record maps every code to the task and test that closes it, or to the evidence that it needs no action.

## Global Constraints

Every task's requirements implicitly include this section.

- **Base.** The base is `main` at or after the merge of `chore/deferred-2026-10-08`: `7edbe85` plus that branch's quick fixes. One of them, deferred item 23, touches two files this plan edits: `build/check_conformance.py` and `build/test_check_conformance.py` gain the `dmi-handoff-consistency` check. Task 1's edits sit beside that code.
- **Worktree.** Run these from any directory, in order.
  - Confirm that local `main` holds the merge: `git -C /Users/lowell/Projects/agent-skills ls-tree --name-only main specs/plans/ | grep -c 39-cc-guide-hardening`. Expected: `1`. Anything else means the merge has not landed. Stop and ask.
  - Confirm that `main` holds the 20 files this plan edits exactly as they were when it was generated: `git -C /Users/lowell/Projects/agent-skills ls-tree -r main -- build/CLAUDE.md build/cc_guide/baseline.py build/cc_guide/blocks.py build/cc_guide/cc_fixtures.py build/cc_guide/check.py build/cc_guide/cli.py build/cc_guide/docs.py build/cc_guide/guide.py build/cc_guide/lint.py build/cc_guide/state.py build/cc_guide/test_baseline.py build/cc_guide/test_blocks.py build/cc_guide/test_check.py build/cc_guide/test_cli.py build/cc_guide/test_docs.py build/cc_guide/test_guide.py build/cc_guide/test_lint.py build/cc_guide/test_state.py build/check_conformance.py build/test_check_conformance.py | git hash-object --stdin`. Expected: `d647eb14b10b604e38d877f0b6116b02427c3dd1`.
    - Any other value means one of these files changed after the plan was written, for example in review of `chore/deferred-2026-10-08`'s quick fixes or in a later commit. The Edit blocks would no longer apply. Stop and ask: the plan must be regenerated (Planning record, "How the edits were made").
  - Create the worktree: `git -C /Users/lowell/Projects/agent-skills worktree add .claude/worktrees/plan-39-cc-guide-hardening -b chore/cc-guide-hardening main`. `.claude/worktrees/` is gitignored. Commit only from the worktree.
  - Every commit command begins with `[ "$(git branch --show-current)" = chore/cc-guide-hardening ] &&`, so a wrong branch or a detached HEAD stops the chain before anything is staged. Concurrent sessions switch the shared checkout. Keep the single `=`; zsh rejects `==` there.
  - Run the subagent-driven-development scripts (`sdd-workspace`, `review-package`) after a `cd` into the worktree: they take the repo root and `HEAD` from the shell's working directory, and from the main checkout their review packages would diff `main`.
  - Scratch files live under the worktree's gitignored `.sdd/39-cc-guide-hardening/` and are never committed. Deviations go in the SDD ledger there as they happen. They reach this plan as `> Deviation:` notes only at the completion markup.
  - Each commit ends with the executing session's own Co-Authored-By trailer, which subagent-authored commits keep too. The `Claude Opus 5.5` trailer in the commit blocks below is written for an Opus session; a session on another model substitutes its own.
- **Baseline and counts.** Before Task 1, run the three suites in the worktree and record their counts in the SDD ledger (`progress.md` in the workspace):
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q`: `149 passed` at this plan's base.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`: `345 passed` at this plan's base.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q -rf`. A worktree lacks the gitignored `build/.scratch/`, so four tests in `test_verify_citations.py` fail there and stay failing throughout: `test_true_negative_flags_bad_refs`, `test_empty_text_has_no_failures`, `test_chapter_fallback_passes_gate_a_but_is_flagged` and `test_known_good_fallback_is_not_flagged`. They are not this plan's to fix.
  - Every expected count below is a **+N delta over that baseline**; the absolute `N passed` figures are what the deltas give from the base counts above. If `main` gained tests in `build/cc_guide/` after this plan was written, trust the deltas. This plan adds **+70 tests** to `build/cc_guide/` (+1, +3, +11, +5, +9, +9, +19, +7, +4 and +2 in Tasks 1–10) and none to `test_check_conformance.py`, whose one changed test is renamed. `cd build && pytest` collects `build/cc_guide/` too, so the build directory's passed count rises by the same +70.
- **Three kinds of step (test-first).** Each task's Step 1 adds or changes tests, and Step 2 runs the suite before any implementation. Every test the step touches is one of three kinds:
  - **Fix**: Step 2 names it with its failure cause. It must fail there for that cause.
  - **Pin**: it pins behavior that is already right, so it passes at Step 2. Step 2 names each pin.
  - **Refactor under green**: Step 3 changes code without changing behavior; the suite stays green and its count does not move.

  A fix that passes at Step 2, a pin that fails there, or a failure for another cause is a plan defect: stop and report it rather than adjusting the assertion. Two fixes are themselves test code, so their rewrites are Step 3 edits even though they live in test files: Task 7 rewrites `cc_fixtures.git` and Task 8 rewrites `test_baseline.history`.
- **Exact edits.** Every code change is an **Edit** block: an exact old text and its replacement. Apply each task's edits in the order given, each one exactly once, with the Edit tool or an equivalent exact replacement.
  - When this plan was written, each old text occurred exactly once in its file at the point of its edit, and applying every edit in order reproduced the prototype's tree at each task boundary (Planning record).
  - If an old text is not found, or is found twice, stop and report it. Never improvise around a mismatch: `main` has moved.
  - The `(in or near …)` label after an edit's path names the top-level definition where its old text starts, for orientation only.
- **Test conventions (drift R12.1).** Run `build/cc_guide/`'s suite from inside that directory; it is stdlib only, so it needs no other `--with`.
  - Tests use bare imports and there is no `__init__.py`. Test files import modules by name and reach names through them, so a missing name fails one test, never collection.
  - Messages and findings are compared with exact equality.
  - Fixtures live in `cc_fixtures.py`, hand-written and never copied from docs text.
  - Module and test basenames stay unique across `build/`.
- **Import direction (drift R12.1; owner ruling 4, plan 38).** Nothing under `build/cc_guide/` imports from `build/`. `build/check_conformance.py` may import `build/cc_guide/guide.py`, which Task 1 does.
- **Python style** (`CLAUDE.md`, `rules/clean-code-python.md`). Use single quotes, with double quotes only around a string that itself holds single quotes. 4-space indent, `'''` docstrings, stdlib only, Python 3.13. Named constants over magic numbers (G25). A `', '.join(...)` or `' and '.join(...)` is computed into a variable before the f-string that uses it.
- **CLI contract (drift R6.9), unchanged.** Exit 0 means clean or nothing due; 1 means violations or something due; 2 means an error. A `SetupError` prints one `cc-guide: <message>` line on stderr, and any other exception prints its traceback. Item 46 is about the inputs that still reach a traceback: each must print a `cc-guide:` line or be refused up front.
- **Never commit docs text** (drift spec, Constraints and Provenance). No fixture copies Anthropic's docs; `baseline.json` holds hashes only. This plan changes no hash: Planning record, "FR-m5".
- **No citation-shaped lines.** No line of a Python file under `build/cc_guide/` begins, after indentation, with `# cc-guide:` or `<!-- cc-guide:`. Stage 2's lint reads such a line as a citation, and the tool's own sources keep citation-shaped test data out of that position (R5). `conformance.toml` gets a real citation in Stage 2 (R4.1), so the rule covers Python files only.
- **Leave alone:**
  - `build/cc_guide/manifest.toml`, `build/cc_guide/baseline.json`, `build/cc_guide/PROBES.md` and the guide (`specs/guides/claude-code-customization-guide.md`). No task changes them, and `cli.py lint` must stay clean on them.
  - The drift spec. Its R7 says a listed rebaseline refuses when an unlisted block "has also changed". Task 8 makes the message, the CLI help and `build/CLAUDE.md` say "changed or gone". That is a clearer message for unchanged behavior, so the spec's wording is the owner's to revise or keep.
  - The section's three other open items: "Sections created after `baseline init`", "check's report and inputs" and "The probe registry's gaps". They belong to later stages.
- **Nothing outward-facing.** No push, PR, issue or post, and no network use: every test runs on fixtures.

---

## Planning record

### How the edits were made (2026-10-08)

Every task was implemented first in a scratch worktree, then folded into one sequence of per-task trees from the base. The Edit blocks were generated from that sequence: exact old texts with enough context to be unique, widened to the whole definition when a change rewrites most of it. They were then replayed from this plan's own text against a fresh checkout of the base. Each step's run reproduced the RED and GREEN outcomes quoted below, and the tree after Task 10 matched the prototype byte for byte. Each commit's `git add` list was checked against the files its edits touch.

The generator, the per-task diffs and the replay script are kept outside the repo, at `~/.cache/agent-skills/plan39-gen/`, until this plan executes. If the pre-flight's pin fails, they regenerate the Edit blocks against the new base.

### Owner rulings (2026-10-08)

1. **A repeated anchor** (item 45): the first heading keeps the ID, and the later one gets ID `None`, as `check_conformance.py` already did. `guide.sections` used to give both headings the ID. Every reader keys sections by ID, so the old reading silently merged two sections.
2. **The "plan-mandated" tidy-ups** (item 50's T8-m6 and T9-m6): tidy both. Lint's `quality_problems` splits into one function per check (Task 6), and `check.py`'s literal HTTP codes and retry count become named constants (Task 9).

### Controls

- **Task 7's anchoring pins.** `ID_RE`, `HASH_RE` and `TEXT_HASH_RE` move to the modules that own them and lose their `^…$` anchors, so every use must be `fullmatch`. Five cases pin that: a group ID `alpha!`, a section ID with a trailing newline, a 17-character key hash, a block hash and a `text_hash` with a trailing newline. Turning each `fullmatch` in `state.py` back into `match` made all five fail. Under the old `^…$` patterns, `$` also matched before a trailing newline, so the newline cases are fixes and the other two are pins.
- **Task 8's `history()` fix.** Against the old helper, the new test fails with `assert <class 'Skipped'> is <class 'Failed'>`, and the skip message, "HEAD is not in this clone", shows the bug: a missing path read as a missing commit.

### Coverage crosswalk

Each code in the four items, and what closes it.

**Item 45**, one anchor grammar: Task 1. `check_conformance.py` reads anchors through `guide.scan`; its copies of `HEADING_RE`, `ANCHOR_RE`, `ANCHOR_LIKE_RE` and `Section` go, and so does `test_guide.py`'s copied ID list. Tests: `test_a_repeated_anchor_ids_only_its_first_heading`, `test_scan_returns_the_sections_and_each_problems_line_and_id`, `test_repeated_anchor_id_is_a_violation_and_resolves_as_guide_py_does`. `build/test_check_conformance.py` keeps the 38-ID oracle, now read through `guide.py`'s grammar.

**Item 46**, a `cc-guide:` line for every input error (T7-m1, T8-m1, T10-m2, T10-m3, T10-m6, T6-m10, FR-m4), by path:
- `baseline stamp` on a guide with no stamp region: Task 2, `test_stamp_without_a_stamp_region_is_one_error_line`.
- An emptied baseline reaching `render_stamp`'s `min()`: Task 2, `test_an_emptied_baseline_is_one_error_line`.
- `accept` on an ID the guide no longer has: Task 2, `test_accepting_a_section_the_guide_no_longer_has_is_one_error_line`.
- `init --release/--date` unvalidated, and `init --release X` without `--docs`: Task 3, `test_init_refuses_a_bad_release_or_date_up_front` and `test_init_without_docs_takes_only_the_bootstrap_release`.
- A wrong-shaped `[guide]`, `[sources]` or `[cadence]`: Task 3, `test_a_mis_shaped_table_reports_its_shape_and_nothing_else`.
- A corrupt `latest/fetch.json`, in rebaseline and in `check.live_docs`: Task 4, `test_a_corrupt_fetch_record_is_one_error_line` and `test_a_corrupt_fetch_record_is_a_setup_error`.
- A non-UTF-8 cached changelog, page or snapshot page: Task 4, `test_non_utf8_cached_docs_are_one_error_line`, `test_docs_read_as_other_than_utf8_are_a_setup_error_or_a_fetch_error` and `test_a_snapshot_page_read_as_other_than_utf8_is_a_setup_error`.
- Also: a non-UTF-8 repo file read through `state.Source`, which Task 7's `git cat-file` rewrite reads as bytes: `test_a_source_file_that_is_not_utf8_is_a_setup_error`.

**Item 49**, coverage:
- T3-m2, `sha256[:16]` and a hashed newline: Task 5, `test_block_hash_is_sha256_over_the_normalized_lines_joined_by_newlines`.
- T3-m3, `KEY_PART_MAX`'s 60/61 boundary: Task 5, `test_a_key_part_of_sixty_characters_is_kept_and_one_of_sixty_one_is_cut`.
- T4-m2 and T4-m3, the `line N:` prefix and the repeat message: Task 5, `test_changelog_errors_name_their_line` and `test_a_bad_release_date_names_its_line`.
- T4-m4, the `</Update>` reset: Task 5, `test_a_bullet_after_a_closed_release_belongs_to_no_release`. `LLMS_TEXT`'s `_llms/` and platform negatives: Task 5's two fixture lines, which `test_llms_lists_code_page_slugs` then excludes.
- T4-m7, unknown-tag forms beyond `date=`: Task 5, the bare `<Update label=…>` and the indented `… >` cases of `test_changelog_errors_name_their_line`.
- T5-m2, the fence rule: Task 6, `test_a_heading_in_a_tilde_or_an_indented_fence_is_no_section`. The real guide has four fences and no fenced `##`, `###` or anchor-like line (measured 2026-10-08), so a real-guide pin would be vacuous.
- T5-m3, terms at 3 and 60 characters, a fenced anchor-like line, `with_stamp`'s `ValueError` and `render_stamp`'s tie-break: Task 6, `test_terms_keep_three_and_sixty_characters_and_drop_two_and_sixty_one`, `test_an_anchor_like_line_inside_a_fence_is_no_stray_anchor`, `test_with_stamp_raises_without_a_region`, `test_render_stamp_breaks_a_tie_on_the_other_field`.
- T6-m5, `state.py`'s validator branches: Task 7. `test_each_manifest_rule_names_its_table` covers ID formats, "maps no page", `[sections.X]`, the `[[exclusion]]` and `[[probe]]` fields and an empty `[groups]`. Also `test_group_terms_fall_back_to_extra_terms_for_a_section_the_guide_lacks` and `test_the_fetch_record_sits_beside_latest_docs`. `Source.label` is covered in `test_a_source_reads_the_working_tree_or_a_commit`.
- T7-m2, `history()` skipping on any failure: Task 8, `test_history_skips_only_for_a_commit_this_clone_lacks`.
- T7-m6, rebaseline's bare `<page>` ref, the llms refresh on a listed run, its three `SetupError`s and a substantive accept's `text_hash`: Task 8, `test_a_bare_page_ref_rebaselines_that_whole_page_and_refreshes_llms`, `test_rebaseline_refuses_an_unknown_group_or_page_and_a_missing_fetch`, and a new assertion in `test_accept_records_the_hash_and_substantive_also_sets_changed`.
- T7-m8, the refusal's vanished-block half: Task 8. The message now says "changed or gone". `test_a_listed_rebaseline_takes_checks_refs_for_blocks_gone_from_the_page` already exercises the gone block.
- T8-m7, lint's fenced-`|` guards, its unclosed-fence branch and the "missing from manifest.toml" arm: Task 6, `test_pipe_lines_without_a_separator_row_or_inside_a_fence_are_no_table`, `test_an_unclosed_json_block_runs_to_the_end`, `test_a_section_missing_from_the_manifest_alone_is_named`.
- T9-m5 and T9-m9, check's dropped-page branch and its `HTTP <code>` text: Task 9, `test_a_baselined_page_its_group_no_longer_maps_is_deselected`, `test_an_answer_other_than_200_or_404_is_an_http_error`, and an `HTTP 500` case in `test_http_get_retries_once_and_reports_any_other_failure`.
- T10-m8 and T10-m5, `test_cli.py`'s gaps: Task 10. The help capture runs once per command. The init refusal's message is pinned, and so are the "no snapshot directory" and "no latest fetch" refusals and advance's stale-stamp message. The audited test compares full `(out, err)` pairs.

**Item 49**, edge cases:
- T3-m6, a link whose title wraps to the next line keeps its target: **no action**. The 133 pages of the 2.1.288 snapshot hold no such link (measured 2026-10-08). Task 5 pins the behavior as it stands: `test_a_link_whose_title_wraps_to_the_next_line_keeps_its_target`.
- T4-m1, `version_key` accepting a trailing newline: Task 5, `LABEL_RE.fullmatch` and the `'2.1.288\n'` case.
- T4-m5, non-bullet lines skipped in a release: **no action**. The changelog's release blocks hold only bullets, 6,970 lines and nothing else (measured 2026-10-08). Task 5 pins it: `test_a_release_keeps_only_its_bullets`. The repeat error now names the label (Task 5).
- T6-m2, `Source.read` returning a tree listing for a directory: Task 7, `git cat-file blob`.
- T6-m6, `_iso` taking `20260902` and week dates: Task 3, `state.is_iso_date`.
- T7-m4, `audited` moving `checked` backwards: Task 8, `check_forward` and `test_audited_never_moves_checked_backwards`.
- T9-m2, a 200 `llms.txt` with no slugs flagging every code page: Task 9, `test_an_llms_txt_listing_no_code_page_is_an_error_not_every_page_missing`.
- T9-m4, `summary()` deriving a ref by truthiness: Task 9, `test_the_summary_prints_a_block_keyed_by_a_bare_heading_as_a_block`.
- FR-m5, a backtick opener whose info string holds a backtick: Task 5. CommonMark opens no fence there. Re-blocking the 136 files of the 2.1.288 snapshot changed no block and no hash (measured 2026-10-08), so `baseline.json` needs no change.

**Item 50**, style:
- T3-m5, the fence 4-tuple read by position: Task 5's `_Opener`. `select`'s `terms` was already annotated (`set[str]`). The unannotated parameters were `key_names`'s `keys` and `contains_term`'s `terms`, which Task 5 annotates as `Iterable[str]`.
- T6-m4, the "manifest order" comment: Task 7.
- T6-m7: Task 7. `ID_RE`, `HASH_RE` and `TEXT_HASH_RE` move to `guide.py` and `blocks.py`, `mapped_pages` replaces the duplicated `mapped = …` line, and `parse_manifest` splits into one helper per table.
- T6-m8: Task 7. `test_state.py`'s `git` import is now used by its new tests rather than removed. `{"stray"!r}` becomes a single-quoted literal inside a double-quoted f-string. `cc_fixtures.git` takes top-level imports and reports git's stderr.
- T7-m5, the duplicated drop-a-page logic and its note: Task 8's `_drop`, with its own note for listed keys.
- T8-m2, T8-m4, T8-m5 and T8-m8: Task 6. Lint uses `guide.stamp_content`. A table needs decision 12's separator row. The dead `\|` guard goes. `' and '` moves out of the f-string.
- T8-m6, plan-mandated, tidied (ruling 2): Task 6, `label_problems`, `table_problems` and `json_problems`.
- T9-m6, plan-mandated, tidied (ruling 2): Task 9 names `HTTP_OK`, `HTTP_NOT_FOUND` and `ATTEMPTS`, and `test_check.py` uses `GUIDE_PATH`. The `changelog: changelog line 8:` stutter goes in Task 5.
- T10-m7, `releases_of`'s `source` parameter: Task 9 renames it `where`.

## File Structure

Every file is modified; none is created or deleted.

| File | Tasks | What changes |
|---|---|---|
| `build/check_conformance.py` | 1 | Reads the guide through `guide.scan`; its anchor grammar goes |
| `build/test_check_conformance.py` | 1 | The repeated-anchor test cross-checks `guide.py` |
| `build/cc_guide/guide.py` | 1, 2, 7 | `scan` and `AnchorProblem`; `NO_STAMP`; owns `ID_RE` and `TEXT_HASH_RE` |
| `build/cc_guide/blocks.py` | 5, 7 | CommonMark backtick rule, `_Opener`, annotations; owns `HASH_CHARS` and `HASH_RE` |
| `build/cc_guide/docs.py` | 5 | `LABEL_RE.fullmatch`; changelog errors name their line |
| `build/cc_guide/state.py` | 2, 3, 4, 7 | Empty-baseline check; `is_iso_date`, `is_label`, shape-only table errors; `read_utf8`, `read_fetch`; shared grammars, `git cat-file`, `mapped_pages`, split `parse_manifest` |
| `build/cc_guide/baseline.py` | 2, 4, 8 | `accept` and `stamp` refusals; UTF-8 reads; `check_forward`, `_drop`, "changed or gone" |
| `build/cc_guide/lint.py` | 2, 6 | `NO_STAMP`; three checks out of `quality_problems`, separator-row tables |
| `build/cc_guide/check.py` | 4, 9 | UTF-8 and fetch-record errors; G25 constants, empty `llms.txt`, `summary` refs, `where` |
| `build/cc_guide/cli.py` | 3, 4, 8 | `init` refusals; UTF-8 and fetch-record reads; "changed or gone" in its help |
| `build/CLAUDE.md` | 8 | "changed or gone" |
| `build/cc_guide/cc_fixtures.py` | 5, 7 | `LLMS_TEXT`'s two negatives; `git` reports stderr |
| `build/cc_guide/test_*.py` | 1–10 | The tests each task names |

---

### Task 1: One anchor grammar (item 45)

**Files:**
- Modify: `build/cc_guide/guide.py`, `build/check_conformance.py`
- Test: `build/cc_guide/test_guide.py`, `build/test_check_conformance.py`

**Interfaces:**
- Produces, in `guide.py`:
  - `AnchorProblem(NamedTuple)`: `line: int` (1-based), `id: str | None` (the repeated anchor's ID, else `None`), `message: str` (without its line).
  - `scan(text: str) -> tuple[list[Section], list[AnchorProblem]]`: R1.1's grammar, read once. A repeated anchor IDs only its first heading (ruling 1).
  - `sections(text)` is `scan(text)[0]`, and `anchor_problems(text)` renders `scan(text)[1]` as `guide line {line}: {message}`. Both keep their signatures.
- In `check_conformance.py`: the module imports `guide` from `build/cc_guide/` by putting that directory on `sys.path`. `guide_sections(text, path)` keeps its signature and returns `(list[guide.Section], list[Violation])`; each anchor problem becomes `Violation(path, 'anchor', id or '-', 'line {line}: {message}')`. Its own `HEADING_RE`, `ANCHOR_RE`, `ANCHOR_LIKE_RE` and `Section` go.

- [x] **Step 1: Write the failing tests.** Apply these edits in order. They add the repeated-anchor and `scan` tests, drop `test_guide.py`'s copied ID list (`build/test_check_conformance.py` keeps the oracle), and make the conformance test cross-check `guide.py`.

**Edit 1.** `build/cc_guide/test_guide.py` (in or near `REAL_GUIDE`). Replace:

````python
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
````

with:

````python
REAL_GUIDE = REPO / 'specs/guides/claude-code-customization-guide.md'
````

**Edit 2.** `build/cc_guide/test_guide.py` (in or near `test_anchor_problems_name_missing_malformed_repeated_and_stray_anchors`). Replace:

````python
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
````

with:

````python
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


def test_a_repeated_anchor_ids_only_its_first_heading():
    '''Every reader keys sections by ID, so a repeat must not merge two
    sections into one entry (owner ruling, plan 39).'''
    text = '\n'.join(['## A', '<!-- cc: a.one -->', 'Alpha.', '## B', '<!-- cc: a.one -->', 'Beta.'])
    found = guide.sections(text)
    assert [(s.heading, s.id) for s in found] == [('## A', 'a.one'), ('## B', None)]
    assert found[1].text == '## B\nBeta.'


def test_scan_returns_the_sections_and_each_problems_line_and_id():
    text = '\n'.join(['## A', '<!-- cc: a.one -->', '### B', 'body', '### C',
                      '<!-- cc: Bad_ID -->', '### D', '<!-- cc: a.one -->', '',
                      '<!-- cc: a.two -->'])
    found, problems = guide.scan(text)
    assert [s.id for s in found] == ['a.one', None, None, None]
    assert problems == [
        guide.AnchorProblem(3, None, "heading '### B' has no anchor on its next line"),
        guide.AnchorProblem(6, None, "malformed anchor '<!-- cc: Bad_ID -->'"),
        guide.AnchorProblem(8, 'a.one', 'anchor a.one repeats line 2'),
        guide.AnchorProblem(10, None, 'anchor is not directly under a heading'),
    ]
````

**Edit 3.** `build/cc_guide/test_guide.py` (in or near `test_real_guide_splits_into_the_38_r11_ids_in_order`). Replace:

````python
def test_real_guide_splits_into_the_38_r11_ids_in_order():
    assert [s.id for s in guide.sections(REAL_GUIDE.read_text(encoding='utf-8'))] == R11_IDS


def test_real_guide_has_no_anchor_problems():
    assert guide.anchor_problems(REAL_GUIDE.read_text(encoding='utf-8')) == []
````

with:

````python
def test_real_guide_has_no_anchor_problems():
    '''build/test_check_conformance.py pins the guide's 38 IDs in order,
    read with this module's grammar (R1.2); this suite imports nothing from
    build/ (R12.1).'''
    assert guide.anchor_problems(REAL_GUIDE.read_text(encoding='utf-8')) == []
````

**Edit 4.** `build/test_check_conformance.py`. Replace:

````python
# (specs/claude-code-drift-automation.md). Pinned here as R1.2's oracle; the
# lint itself validates the register against the guide's anchors, never
# against this list.
````

with:

````python
# (specs/claude-code-drift-automation.md). Pinned here as R1.2's oracle, and
# only here: the guide is read with cc_guide/guide.py's grammar, whose own
# suite imports nothing from build/ (drift R12.1). The lint itself validates
# the register against the guide's anchors, never against this list.
````

**Edit 5.** `build/test_check_conformance.py` (in or near `test_repeated_anchor_id_is_a_violation`). Replace:

````python
def test_repeated_anchor_id_is_a_violation():
    text = '## A\n<!-- cc: a.one -->\n## B\n<!-- cc: a.one -->\n'
    sections, violations = cc.guide_sections(text, 'guide.md')
    assert [s.id for s in sections] == ['a.one', None]
    assert rendered(violations) == [
        'guide.md: anchor (a.one): line 4: anchor repeats line 2']
````

with:

````python
def test_repeated_anchor_id_is_a_violation_and_resolves_as_guide_py_does():
    text = '## A\n<!-- cc: a.one -->\n## B\n<!-- cc: a.one -->\n'
    sections, violations = cc.guide_sections(text, 'guide.md')
    assert [s.id for s in sections] == ['a.one', None]
    assert [s.id for s in sections] == [s.id for s in cc.guide.sections(text)]
    assert rendered(violations) == [
        'guide.md: anchor (a.one): line 4: anchor a.one repeats line 2']
````

- [x] **Step 2: Run the suites and confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf`
Expected: `2 failed, 148 passed`. Both fixes:
- `test_guide.py::test_a_repeated_anchor_ids_only_its_first_heading`: `guide.sections` gives the second heading the ID too (`('## B', 'a.one')`).
- `test_guide.py::test_scan_returns_the_sections_and_each_problems_line_and_id`: `AttributeError: module 'guide' has no attribute 'scan'`.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q -rf test_check_conformance.py`
Expected: `1 failed, 344 passed`. The fix: `test_repeated_anchor_id_is_a_violation_and_resolves_as_guide_py_does`, with `AttributeError: module 'check_conformance' has no attribute 'guide'`.

- [x] **Step 3: Implement.** Apply these edits in order. `scan` replaces `sections` and `anchor_problems`, which become thin readers of it, and `check_conformance.py` imports it.

**Edit 1.** `build/cc_guide/guide.py` (in or near `sections`). Replace:

````python
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
````

with:

````python
class AnchorProblem(NamedTuple):
    line: int        # 1-based line the problem is on
    id: str | None   # the repeated anchor's ID; None for every other problem
    message: str     # the problem, without its line


def scan(text: str) -> tuple[list[Section], list[AnchorProblem]]:
    '''R1.1's grammar, read once for both this package and
    build/check_conformance.py: the guide's ## and ### headings outside fenced
    code, each with its anchor's ID and its text, and every anchor problem.
    A ## section runs to its first ###; the last section runs to the end of
    the file. A repeated anchor IDs only its first heading, since every
    reader keys sections by ID.'''
    lines = text.split('\n')
    fenced = fenced_lines(lines)
    starts = [i for i, line in enumerate(lines) if i not in fenced and HEADING_RE.match(line)]
    found: list[Section] = []
    problems: list[AnchorProblem] = []
    under: set[int] = set()
    first: dict[str, int] = {}
    parent = None
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        heading = lines[start].strip()
        is_sub = lines[start].startswith('###')
        if not is_sub:
            parent = heading
        nxt = lines[start + 1] if start + 1 < end else ''
        anchor = ANCHOR_RE.match(nxt)
        sid = None
        if anchor:
            under.add(start + 1)
            if anchor.group(1) in first:
                problems.append(AnchorProblem(start + 2, anchor.group(1),
                                              f'anchor {anchor.group(1)} repeats line {first[anchor.group(1)]}'))
            else:
                first[anchor.group(1)] = start + 2
                sid = anchor.group(1)
        elif ANCHOR_LIKE_RE.match(nxt):
            under.add(start + 1)
            problems.append(AnchorProblem(start + 2, None, f'malformed anchor {nxt.strip()!r}'))
        else:
            problems.append(AnchorProblem(start + 1, None, f'heading {heading!r} has no anchor on its next line'))
        body = [i for i in range(start, end) if not (anchor and i == start + 1)]
        found.append(Section(start + 1, heading, parent if is_sub else None, sid,
                             '\n'.join(lines[i] for i in body),
                             '\n'.join(lines[i] for i in body if i not in fenced)))
    problems += [AnchorProblem(i + 1, None, 'anchor is not directly under a heading')
                 for i, line in enumerate(lines)
                 if i not in fenced and i not in under and ANCHOR_LIKE_RE.match(line)]
    return found, problems


def sections(text: str) -> list[Section]:
    '''The guide's sections (R1.1), as scan reads them.'''
    return scan(text)[0]


def anchor_problems(text: str) -> list[str]:
    '''R1.1 as the lint states it: every heading has exactly one well-formed
    anchor on its next line, and no anchor repeats or stands anywhere else.'''
    return [f'guide line {p.line}: {p.message}' for p in scan(text)[1]]
````

**Edit 2.** `build/check_conformance.py` (in or near `REPO`). Replace:

````python
REPO = Path(__file__).resolve().parent.parent
REGISTER = 'build/cc_guide/conformance.toml'
# A ## or ### ATX heading. The guide's sections are exactly these (drift R1.1).
HEADING_RE = re.compile(r'^#{2,3}[ \t]')
# A well-formed anchor: two or more dot-separated [a-z0-9-] segments.
ANCHOR_RE = re.compile(r'^<!-- cc: ([a-z0-9-]+(?:\.[a-z0-9-]+)+) -->$')
# Anything meant as an anchor, well-formed or not. `cc-guide:` (drift's
# citation and stamp markers) does not match: `cc` must be followed by `:`.
ANCHOR_LIKE_RE = re.compile(r'^<!--\s*cc:')


class Section(NamedTuple):
    line: int  # 1-based line of the heading
    heading: str
    id: str | None  # None when the heading has no well-formed, unique anchor
````

with:

````python
# The guide's anchor grammar is cc_guide/guide.py's (drift R1.1). Drift R12.1
# bars only cc_guide importing from build/, so the lint reads it from there.
sys.path.insert(0, str(Path(__file__).resolve().parent / 'cc_guide'))
import guide  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
REGISTER = 'build/cc_guide/conformance.toml'
````

**Edit 3.** `build/check_conformance.py` (in or near `guide_sections`). Replace:

````python
def guide_sections(text: str, path: str) -> tuple[list[Section], list[Violation]]:
    '''The guide's ## and ### headings outside fenced code, each with the ID of
    the anchor on its next line, plus one violation per missing, malformed,
    stray or repeated anchor (R1.1, R3.3 rule 1).'''
    lines = text.split('\n')
    fenced = fenced_lines(text)
    sections: list[Section] = []
    out: list[Violation] = []
    under_heading: set[int] = set()
    first_line: dict[str, int] = {}
    for n, line in enumerate(lines, start=1):
        if n in fenced or not HEADING_RE.match(line):
            continue
        nxt = lines[n] if n < len(lines) else ''
        anchor = None
        m = ANCHOR_RE.match(nxt)
        if m:
            under_heading.add(n + 1)
            if m.group(1) in first_line:
                out.append(Violation(path, 'anchor', m.group(1),
                                     f'line {n + 1}: anchor repeats line {first_line[m.group(1)]}'))
            else:
                first_line[m.group(1)] = n + 1
                anchor = m.group(1)
        elif ANCHOR_LIKE_RE.match(nxt):
            under_heading.add(n + 1)
            out.append(Violation(path, 'anchor', '-', f'line {n + 1}: malformed anchor {nxt.strip()!r}'))
        else:
            out.append(Violation(path, 'anchor', '-',
                                 f'line {n}: heading {line.strip()!r} has no anchor on its next line'))
        sections.append(Section(n, line.strip(), anchor))
    for n, line in enumerate(lines, start=1):
        if n not in fenced and n not in under_heading and ANCHOR_LIKE_RE.match(line):
            out.append(Violation(path, 'anchor', '-', f'line {n}: anchor is not directly under a heading'))
    return sections, out
````

with:

````python
def guide_sections(text: str, path: str) -> tuple[list[guide.Section], list[Violation]]:
    '''The guide's sections, read with guide.py's grammar (drift R1.1), plus
    one violation per missing, malformed, stray or repeated anchor (R3.3
    rule 1). A repeated anchor IDs only its first heading.'''
    sections, problems = guide.scan(text)
    return sections, [Violation(path, 'anchor', p.id or '-', f'line {p.line}: {p.message}') for p in problems]
````

- [x] **Step 4: Run the suites and the two lints, and confirm GREEN.**

Run the two Step 2 commands again. Expected: `150 passed` (+1: two tests added, one removed), and `345 passed`.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && uv run --python 3.13 --with pyyaml python build/check_conformance.py; echo "exit=$?"; uv run --python 3.13 python build/cc_guide/cli.py lint; echo "exit=$?"`
Expected: `exit=0` twice. The lint prints `note: release-label check skipped: no changelog to read` on stderr when no changelog is cached; that is fine.

- [x] **Step 5: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && [ "$(git branch --show-current)" = chore/cc-guide-hardening ] && git add build/cc_guide/guide.py build/cc_guide/test_guide.py build/check_conformance.py build/test_check_conformance.py && git commit -m "refactor(cc_guide): read the guide's anchors with one grammar

guide.scan reads R1.1 once, for the drift detector and for
check_conformance.py, which now imports it (owner ruling 4; drift R12.1
bars only the reverse). A repeated anchor IDs only its first heading in
both, where guide.sections used to give it to both. The duplicated
patterns and test_guide.py's copied ID list go; the conformance suite
keeps the 38-ID oracle.

Plan 39, Task 1 (deferred item: unify the guide's anchor grammar).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: A stamp region, an emptied baseline and an absent ID (item 46)

**Files:**
- Modify: `build/cc_guide/guide.py`, `build/cc_guide/baseline.py`, `build/cc_guide/lint.py`, `build/cc_guide/state.py`
- Test: `build/cc_guide/test_cli.py`

**Interfaces:**
- Consumes: `guide.STAMP_OPEN`, `guide.STAMP_CLOSE`, `guide.stamp_bounds`.
- Produces: `guide.NO_STAMP = f'needs one stamp region, a {STAMP_OPEN} line then a {STAMP_CLOSE} line'`. Lint's missing-region violation and `baseline stamp`'s refusal both read `guide: {NO_STAMP}`.
- `baseline.stamp` raises `SetupError(f'guide: {NO_STAMP}')` without a region. `baseline.accept` raises `SetupError('section IDs not in the guide: <ids>')` for IDs the baseline knows but the guide lacks. `state.parse_baseline` reports `sections must hold at least one section`.

- [x] **Step 1: Write the failing tests.** Apply these edits in order: an import of the stamp markers, and three CLI tests.

**Edit 1.** `build/cc_guide/test_cli.py`. Replace:

````python
                         fixture_repo, git, guide_text, isolated_home, prime_cache, write_tree)
````

with:

````python
                         fixture_repo, git, guide_text, isolated_home, prime_cache, write_tree)
from guide import STAMP_CLOSE, STAMP_OPEN
````

**Edit 2.** `build/cc_guide/test_cli.py` (in or near `test_a_malformed_or_empty_cached_changelog_exits_two`). Replace:

````python
    assert capsys.readouterr() == ('', f'cc-guide: {changelog}: no <Update> release blocks\n')


def test_a_crash_exits_two_never_one(world, monkeypatch, capsys):
````

with:

````python
    assert capsys.readouterr() == ('', f'cc-guide: {changelog}: no <Update> release blocks\n')


def test_stamp_without_a_stamp_region_is_one_error_line(world, capsys):
    repo, cache, _ = world
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace(STAMP_OPEN + '\n', '').replace(STAMP_CLOSE + '\n', ''))
    assert main(cache, 'baseline', 'stamp') == 2
    assert capsys.readouterr() == ('', f'cc-guide: guide: needs one stamp region, a {STAMP_OPEN} line'
                                       f' then a {STAMP_CLOSE} line\n')


def test_an_emptied_baseline_is_one_error_line(world, capsys):
    repo, cache, _ = world
    emptied = load(repo)
    emptied['sections'] = {}
    (repo / state.BASELINE).write_text(json.dumps(emptied))
    assert main(cache, 'lint') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {state.BASELINE}: sections must hold at least one section\n')


def test_accepting_a_section_the_guide_no_longer_has_is_one_error_line(world, capsys):
    repo, cache, _ = world
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace('<!-- cc: alpha.overview -->', '<!-- cc: alpha.renamed -->'))
    assert main(cache, 'baseline', 'accept', 'alpha.overview', '--editorial') == 2
    assert capsys.readouterr() == ('', 'cc-guide: section IDs not in the guide: alpha.overview\n')
    assert dirty(repo) == [GUIDE_PATH]


def test_a_crash_exits_two_never_one(world, monkeypatch, capsys):
````

- [x] **Step 2: Run the suite and confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf`
Expected: `3 failed, 150 passed`. All three are fixes, and each fails because stderr holds a traceback instead of the `cc-guide:` line:
- `test_cli.py::test_stamp_without_a_stamp_region_is_one_error_line`: `ValueError: the guide has no stamp region`, from `guide.with_stamp`.
- `test_cli.py::test_an_emptied_baseline_is_one_error_line`: `ValueError: min() iterable argument is empty`, from `guide.render_stamp`.
- `test_cli.py::test_accepting_a_section_the_guide_no_longer_has_is_one_error_line`: `KeyError: 'alpha.overview'`, from `baseline.accept`.

- [x] **Step 3: Implement.** Apply these edits in order.

**Edit 1.** `build/cc_guide/baseline.py`. Replace:

````python
from guide import anchor_problems, render_stamp, sections, text_hash, with_stamp
````

with:

````python
from guide import NO_STAMP, anchor_problems, render_stamp, sections, stamp_bounds, text_hash, with_stamp
````

**Edit 2.** `build/cc_guide/baseline.py` (in or near `accept`). Replace:

````python
    by_id = {s.id: s for s in sections(guide_text)}
````

with:

````python
    by_id = {s.id: s for s in sections(guide_text) if s.id}
    absent = ', '.join(sid for sid in ids if sid not in by_id)
    if absent:
        raise SetupError(f'section IDs not in the guide: {absent}')
````

**Edit 3.** `build/cc_guide/baseline.py` (in or near `stamp`). Replace:

````python
def stamp(guide_text: str, state: dict) -> str:
    '''R7 stamp: the guide with its stamp region regenerated (R1.2).'''
    return with_stamp(guide_text, render_stamp(state['sections']))
````

with:

````python
def stamp(guide_text: str, state: dict) -> str:
    '''R7 stamp: the guide with its stamp region regenerated (R1.2).'''
    if stamp_bounds(guide_text) is None:
        raise SetupError(f'guide: {NO_STAMP}')
    return with_stamp(guide_text, render_stamp(state['sections']))
````

**Edit 4.** `build/cc_guide/guide.py` (in or near `STAMP_CLOSE`). Replace:

````python
STAMP_CLOSE = '<!-- /cc-guide:stamp -->'
````

with:

````python
STAMP_CLOSE = '<!-- /cc-guide:stamp -->'
# What a guide without a stamp region lacks, as lint and `baseline stamp` say it.
NO_STAMP = f'needs one stamp region, a {STAMP_OPEN} line then a {STAMP_CLOSE} line'
````

**Edit 5.** `build/cc_guide/lint.py`. Replace:

````python
from guide import STAMP_CLOSE, STAMP_OPEN, anchor_problems, render_stamp, sections, stamp_bounds, text_hash
````

with:

````python
from guide import NO_STAMP, anchor_problems, render_stamp, sections, stamp_bounds, text_hash
````

**Edit 6.** `build/cc_guide/lint.py` (in or near `stamp_problems`). Replace:

````python
        return [f'guide: needs one stamp region, a {STAMP_OPEN} line then a {STAMP_CLOSE} line']
````

with:

````python
        return [f'guide: {NO_STAMP}']
````

**Edit 7.** `build/cc_guide/state.py` (in or near `parse_baseline`). Replace:

````python
        raise SetupError(f'{BASELINE}: holds exactly sections, groups and llms')
````

with:

````python
        raise SetupError(f'{BASELINE}: holds exactly sections, groups and llms')
    if not raw['sections']:
        problems.append('sections must hold at least one section')
````

- [x] **Step 4: Run the suite and confirm GREEN.**

Run the Step 2 command again. Expected: `153 passed` (+3).

- [x] **Step 5: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && [ "$(git branch --show-current)" = chore/cc-guide-hardening ] && git add build/cc_guide/guide.py build/cc_guide/baseline.py build/cc_guide/lint.py build/cc_guide/state.py build/cc_guide/test_cli.py && git commit -m "fix(cc_guide): one error line for a missing stamp region, an empty baseline or an absent ID

baseline stamp on a guide with no stamp region, a baseline whose sections
are empty, and accept on an ID the guide no longer has each printed a
traceback. Each is now a SetupError, so the CLI prints one cc-guide: line
and exits 2. guide.NO_STAMP words the missing region once, for lint and
stamp alike.

Plan 39, Task 2 (deferred item: every input error prints a cc-guide: line).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: `baseline init`'s arguments and a mis-shaped table (item 46; T6-m6, T6-m10)

**Files:**
- Modify: `build/cc_guide/state.py`, `build/cc_guide/cli.py`
- Test: `build/cc_guide/test_state.py`, `build/cc_guide/test_cli.py`

**Interfaces:**
- Produces, in `state.py`:
  - `DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')`.
  - `is_iso_date(value) -> bool`: a `YYYY-MM-DD` string that `date.fromisoformat` accepts. `fromisoformat` alone also takes `20260902` and week dates such as `2026-W36-3` (T6-m6).
  - `is_label(value) -> bool`: `version_key` accepts it.
  - These two replace the private `_iso` and `_label`.
  - `_table(raw, key, problems) -> dict | None` returns `None` for a mis-shaped table, so `parse_manifest` skips that table's field checks (T6-m10).
- In `cli.py`, `baseline init` refuses before any other work:
  - `baseline init: --release '<v>' is not a release label`;
  - `baseline init: --date '<v>' is not a YYYY-MM-DD date`;
  - `baseline init: without --docs it reads the 2.1.288 bootstrap snapshot, so --release must be 2.1.288`.

- [x] **Step 1: Write the failing tests.** Apply these edits in order.

**Edit 1.** `build/cc_guide/test_cli.py` (in or near `test_init_derives_changed_and_refuses_to_overwrite_without_force`). Replace:

````python
    assert main(cache, *argv, '--force') == 0
````

with:

````python
    assert main(cache, *argv, '--force') == 0


@pytest.mark.parametrize('flag, value, message', [
    ('--release', '2.1.x', "--release '2.1.x' is not a release label"),
    ('--date', '20260902', "--date '20260902' is not a YYYY-MM-DD date"),
    ('--date', '2026-W36-3', "--date '2026-W36-3' is not a YYYY-MM-DD date"),
])
def test_init_refuses_a_bad_release_or_date_up_front(world, capsys, flag, value, message):
    repo, cache, folder = world
    (repo / state.BASELINE).unlink()  # so the --force guard is not what refuses
    assert main(cache, 'baseline', 'init', '--docs', str(folder), flag, value) == 2
    assert capsys.readouterr() == ('', f'cc-guide: baseline init: {message}\n')
    assert not (repo / state.BASELINE).exists()


def test_init_without_docs_takes_only_the_bootstrap_release(world, capsys):
    repo, cache, _ = world
    (repo / state.BASELINE).unlink()
    assert main(cache, 'baseline', 'init', '--release', '2.1.902') == 2
    assert capsys.readouterr() == ('', 'cc-guide: baseline init: without --docs it reads the 2.1.288 bootstrap'
                                       ' snapshot, so --release must be 2.1.288\n')
````

**Edit 2.** `build/cc_guide/test_state.py` (in or near `test_every_manifest_problem_is_reported_at_once`). Replace:

````python
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
    shapes = (MANIFEST_TOML.replace('[guide]\npath = ', 'guide = ').replace('[[exclusion]]', '[exclusion]')
              + "\n[sections]\n'alpha.overview' = 1\n\n[probe]\nid = 'x'\n")
    with pytest.raises(state.SetupError) as err:
        state.parse_manifest(shapes)
    assert str(err.value).split('\n') == [
        f'{state.MANIFEST}: [guide] must be a table',
        f'{state.MANIFEST}: [guide] path must be a non-empty string',
        f"{state.MANIFEST}: [sections.'alpha.overview'] holds only extra_terms and exclude_terms, as lists",
        f'{state.MANIFEST}: [[exclusion]] must be an array of tables',
        f'{state.MANIFEST}: [[probe]] must be an array of tables',
    ]
````

with:

````python
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
    shapes = (MANIFEST_TOML.replace('[guide]\npath = ', 'guide = ').replace('[[exclusion]]', '[exclusion]')
              + "\n[sections]\n'alpha.overview' = 1\n\n[probe]\nid = 'x'\n")
    with pytest.raises(state.SetupError) as err:
        state.parse_manifest(shapes)
    assert str(err.value).split('\n') == [
        f'{state.MANIFEST}: [guide] must be a table',
        f"{state.MANIFEST}: [sections.'alpha.overview'] holds only extra_terms and exclude_terms, as lists",
        f'{state.MANIFEST}: [[exclusion]] must be an array of tables',
        f'{state.MANIFEST}: [[probe]] must be an array of tables',
    ]


def test_a_mis_shaped_table_reports_its_shape_and_nothing_else():
    groups = MANIFEST_TOML[MANIFEST_TOML.index('[groups.alpha]'):]
    with pytest.raises(state.SetupError) as err:
        state.parse_manifest("guide = 'x'\nsources = 1\ncadence = 1\n\n" + groups)
    assert str(err.value).split('\n') == [f'{state.MANIFEST}: [guide] must be a table',
                                          f'{state.MANIFEST}: [sources] must be a table',
                                          f'{state.MANIFEST}: [cadence] must be a table']


@pytest.mark.parametrize('value, ok', [
    ('2026-09-02', True), ('20260902', False), ('2026-W36-3', False), ('2026-02-30', False),
    ('2026-09-02\n', False), (20260902, False),
])
def test_a_date_is_yyyy_mm_dd_and_nothing_else_fromisoformat_takes(value, ok):
    assert state.is_iso_date(value) is ok
````

- [x] **Step 2: Run the suite and confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf`
Expected: `12 failed, 152 passed`. All are fixes:
- `test_cli.py::test_init_refuses_a_bad_release_or_date_up_front`, three cases, and `test_cli.py::test_init_without_docs_takes_only_the_bootstrap_release`. Without the up-front checks, `init` goes on to read R11.1's history and refuses with `R11.1 needs …, which this clone lacks (a shallow clone?)` instead.
- `test_state.py::test_every_manifest_problem_is_reported_at_once` and `test_state.py::test_a_mis_shaped_table_reports_its_shape_and_nothing_else`. After a table's shape problem, each field check still runs against the `{}` fallback and adds lines such as `[guide] path must be a non-empty string`.
- `test_state.py::test_a_date_is_yyyy_mm_dd_and_nothing_else_fromisoformat_takes`, all six cases: `AttributeError: module 'state' has no attribute 'is_iso_date'`.

- [x] **Step 3: Implement.** Apply these edits in order.

**Edit 1.** `build/cc_guide/cli.py`. Replace:

````python
                   dump_baseline, fetch_record, latest_docs, newest_changelog, parse_baseline, parse_manifest,
                   snapshot_docs, snapshot_text)
````

with:

````python
                   dump_baseline, fetch_record, is_iso_date, is_label, latest_docs, newest_changelog,
                   parse_baseline, parse_manifest, snapshot_docs, snapshot_text)
````

**Edit 2.** `build/cc_guide/cli.py` (in or near `run_baseline`). Replace:

````python
    if args.action == 'init':
````

with:

````python
    if args.action == 'init':
        if not is_label(args.release):
            raise SetupError(f'baseline init: --release {args.release!r} is not a release label')
        if not is_iso_date(args.date):
            raise SetupError(f'baseline init: --date {args.date!r} is not a YYYY-MM-DD date')
        if args.docs is None and args.release != BOOTSTRAP_RELEASE:
            raise SetupError(f'baseline init: without --docs it reads the {BOOTSTRAP_RELEASE} bootstrap snapshot,'
                             f' so --release must be {BOOTSTRAP_RELEASE}')
````

**Edit 3.** `build/cc_guide/state.py` (in or near `TEXT_HASH_RE`). Replace:

````python
TEXT_HASH_RE = re.compile(r'^sha256:[0-9a-f]{64}$')
````

with:

````python
TEXT_HASH_RE = re.compile(r'^sha256:[0-9a-f]{64}$')
DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
````

**Edit 4.** `build/cc_guide/state.py` (in or near `_table`). Replace:

````python
def _table(raw: dict, key: str, problems: list[str]) -> dict:
    '''raw[key] if it is a TOML table, else one listed problem and {}.'''
    value = raw.get(key, {})
    if isinstance(value, dict):
        return value
    problems.append(f'[{key}] must be a table')
    return {}
````

with:

````python
def _table(raw: dict, key: str, problems: list[str]) -> dict | None:
    '''raw[key] when it is a TOML table, {} when it is absent; else one
    listed problem and None, so the caller skips the table's fields.'''
    value = raw.get(key, {})
    if isinstance(value, dict):
        return value
    problems.append(f'[{key}] must be a table')
    return None
````

**Edit 5.** `build/cc_guide/state.py` (in or near `parse_manifest`). Replace:

````python
    guide_path = _table(raw, 'guide', problems).get('path')
    if not isinstance(guide_path, str) or not guide_path:
        problems.append('[guide] path must be a non-empty string')
    sources = _table(raw, 'sources', problems)
    for k in SOURCE_KEYS:
        if not (isinstance(sources.get(k), str) and sources[k].startswith('https://')):
            problems.append(f'[sources] {k} must be an https URL')
    cadence = _table(raw, 'cadence', problems)
    for k in CADENCE_KEYS:
````

with:

````python
    guide_table = _table(raw, 'guide', problems)
    guide_path = None if guide_table is None else guide_table.get('path')
    if guide_table is not None and not (isinstance(guide_path, str) and guide_path):
        problems.append('[guide] path must be a non-empty string')
    sources = _table(raw, 'sources', problems)
    for k in SOURCE_KEYS if sources is not None else ():
        if not (isinstance(sources.get(k), str) and sources[k].startswith('https://')):
            problems.append(f'[sources] {k} must be an https URL')
    cadence = _table(raw, 'cadence', problems)
    for k in CADENCE_KEYS if cadence is not None else ():
````

**Edit 6.** `build/cc_guide/state.py` (in or near `parse_manifest`). Replace:

````python
    for sid, t in _table(raw, 'sections', problems).items():
````

with:

````python
    for sid, t in (_table(raw, 'sections', problems) or {}).items():
````

**Edit 7.** `build/cc_guide/state.py` (in or near `_iso`). Replace:

````python
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
````

with:

````python
def is_iso_date(value) -> bool:
    '''A YYYY-MM-DD date. date.fromisoformat alone also takes 20260902 and
    week dates such as 2026-W36-3.'''
    if not (isinstance(value, str) and DATE_RE.fullmatch(value)):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def is_label(value) -> bool:
    '''A release label (R2.4).'''
    try:
        version_key(value)
    except (TypeError, ValueError):
        return False
    return True


def _stamp(value) -> bool:
    return (isinstance(value, dict) and set(value) == {'release', 'date'}
            and is_label(value['release']) and is_iso_date(value['date']))
````

**Edit 8.** `build/cc_guide/state.py` (in or near `parse_baseline`). Replace:

````python
              and _stamp(s['checked']) and _stamp(s['audited']) and _label(s['changed'])
````

with:

````python
              and _stamp(s['checked']) and _stamp(s['audited']) and is_label(s['changed'])
````

**Edit 9.** `build/cc_guide/state.py` (in or near `parse_baseline`). Replace:

````python
            ok = ok and all(_label(r) for r in g['snapshot'].values())
````

with:

````python
            ok = ok and all(is_label(r) for r in g['snapshot'].values())
````

- [x] **Step 4: Run the suite and confirm GREEN.**

Run the Step 2 command again. Expected: `164 passed` (+11).

- [x] **Step 5: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && [ "$(git branch --show-current)" = chore/cc-guide-hardening ] && git add build/cc_guide/state.py build/cc_guide/cli.py build/cc_guide/test_state.py build/cc_guide/test_cli.py && git commit -m "fix(cc_guide): refuse bad init arguments up front; report a mis-shaped table once

baseline init now checks --release and --date before it reads anything,
and refuses --release other than 2.1.288 without --docs, which would hash
the 2.1.288 snapshot under another label. A date is YYYY-MM-DD and
nothing else fromisoformat takes (state.is_iso_date). A mis-shaped
[guide], [sources] or [cadence] reports its shape alone.

Plan 39, Task 3 (deferred items: every input error prints a cc-guide:
line; test coverage and edge cases, T6-m6).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: UTF-8 reads and the fetch record (item 46)

**Files:**
- Modify: `build/cc_guide/state.py`, `build/cc_guide/check.py`, `build/cc_guide/cli.py`, `build/cc_guide/baseline.py`
- Test: `build/cc_guide/test_state.py`, `build/cc_guide/test_check.py`, `build/cc_guide/test_cli.py`

**Interfaces:**
- Produces, in `state.py`:
  - `read_utf8(path: Path) -> str` raises `SetupError(f'{path}: not UTF-8 text ({reason} at byte {start})')`.
  - `read_fetch(cache: Path) -> dict | None` returns `None` before the first fetch. Otherwise it raises `SetupError` with `{path}: not valid JSON (…); delete it and run check` or `{path}: names no changelog_head release; delete it and run check`.
  - `snapshot_text` reads through `read_utf8`.
- Produces, in `check.py`: `utf8(body: bytes) -> str | None`.
  - `live_docs` reads the fetch record with `read_fetch`.
  - A fetched changelog or `llms.txt` that is not UTF-8 raises `FetchError(f'{url}: not UTF-8 text')`.
  - A fetched page that is not UTF-8 becomes an error: the page goes into `unread`, and its cached copy is removed, as on a failed fetch.
  - `offline_docs` reads through `read_utf8`.
- `cli.cached_releases` and `rebaseline` read through `read_utf8` and `read_fetch`, and `baseline.init` and `baseline.rebaseline` through `read_utf8`. `cli.py` drops its now-unused `json` and `fetch_record` imports.

- [x] **Step 1: Write the failing tests.** Apply these edits in order.

**Edit 1.** `build/cc_guide/test_check.py` (in or near `test_a_page_unmapped_by_a_head_move_is_refetched_when_mapped_again`). Replace:

````python
    assert got.pages['platform:pricing'] == 'Pricing text at head B.\n'


def test_a_404_removes_the_stale_copy_and_reads_as_a_missing_page(tmp_path, docs_dir):
````

with:

````python
    assert got.pages['platform:pricing'] == 'Pricing text at head B.\n'


def test_a_corrupt_fetch_record_is_a_setup_error(tmp_path, docs_dir):
    cache = tmp_path / 'cache'
    record = state.fetch_record(cache)
    record.parent.mkdir(parents=True)
    record.write_text('[]')
    with pytest.raises(state.SetupError) as err:
        check.live_docs(MANIFEST, cache, serving(docs_dir), NOW)
    assert str(err.value) == f'{record}: names no changelog_head release; delete it and run check'


def test_docs_read_as_other_than_utf8_are_a_setup_error_or_a_fetch_error(tmp_path, docs_dir):
    '''A local or cached file is a SetupError naming it; a fetched one is a
    fetch error, so a page is left unread and uncached, as on a failed fetch.'''
    (docs_dir / 'tools.md').write_bytes(b'\xff\xfe')
    with pytest.raises(state.SetupError) as err:
        offline(docs_dir)
    assert str(err.value) == f"{docs_dir / 'tools.md'}: not UTF-8 text (invalid start byte at byte 0)"
    cache = tmp_path / 'cache'
    got = check.live_docs(MANIFEST, cache, serving(docs_dir), NOW)
    assert (got.errors, got.unread) == ([f"{docs.page_url('tools', MANIFEST.sources)}: not UTF-8 text"], {'tools'})
    assert not (state.latest_docs(cache) / 'tools.md').exists()
    (docs_dir / 'changelog.md').write_bytes(b'\xff\xfe')
    with pytest.raises(check.FetchError) as err:
        check.live_docs(MANIFEST, cache, serving(docs_dir), NOW)
    assert str(err.value) == f"{MANIFEST.sources['changelog']}: not UTF-8 text"


def test_a_404_removes_the_stale_copy_and_reads_as_a_missing_page(tmp_path, docs_dir):
````

**Edit 2.** `build/cc_guide/test_cli.py` (in or near `test_accepting_a_section_the_guide_no_longer_has_is_one_error_line`). Replace:

````python
    assert dirty(repo) == [GUIDE_PATH]


def test_a_crash_exits_two_never_one(world, monkeypatch, capsys):
````

with:

````python
    assert dirty(repo) == [GUIDE_PATH]


def test_a_corrupt_fetch_record_is_one_error_line(world, capsys):
    _, cache, _ = world
    record = state.fetch_record(cache)
    record.write_text('{')
    with pytest.raises(json.JSONDecodeError) as cause:
        json.loads('{')
    assert main(cache, 'baseline', 'rebaseline', 'alpha') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {record}: not valid JSON ({cause.value}); delete it and run check\n')
    record.write_text('{}')
    assert main(cache, 'baseline', 'rebaseline', 'alpha') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {record}: names no changelog_head release;'
                                       ' delete it and run check\n')


def test_non_utf8_cached_docs_are_one_error_line(world, capsys):
    repo, cache, _ = world
    page = state.latest_docs(cache) / 'tools.md'
    page.write_bytes(b'\xff\xfe')
    assert main(cache, 'baseline', 'rebaseline', 'alpha') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {page}: not UTF-8 text (invalid start byte at byte 0)\n')
    changelog = state.latest_docs(cache) / 'changelog.md'
    changelog.write_bytes(b'\xff\xfe')
    assert main(cache, 'lint') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {changelog}: not UTF-8 text (invalid start byte at byte 0)\n')
    assert dirty(repo) == []


def test_a_crash_exits_two_never_one(world, monkeypatch, capsys):
````

**Edit 3.** `build/cc_guide/test_state.py` (in or near `test_the_newest_changelog_is_latest_else_the_bootstrap_snapshot`). Replace:

````python
    assert state.newest_changelog(tmp_path) == latest


def test_the_default_cache_follows_home(isolated_home):
````

with:

````python
    assert state.newest_changelog(tmp_path) == latest


def test_a_snapshot_page_read_as_other_than_utf8_is_a_setup_error(tmp_path):
    page = state.snapshot_docs(tmp_path, '2.1.900') / 'tools.md'
    page.parent.mkdir(parents=True)
    page.write_bytes(b'ok \xff')
    with pytest.raises(state.SetupError) as err:
        state.snapshot_text(tmp_path, 'tools', '2.1.900')
    assert str(err.value) == f'{page}: not UTF-8 text (invalid start byte at byte 3)'


def test_the_default_cache_follows_home(isolated_home):
````

- [x] **Step 2: Run the suite and confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf`
Expected: `5 failed, 164 passed`. All five are fixes:
- `test_check.py::test_a_corrupt_fetch_record_is_a_setup_error`: `AttributeError: 'list' object has no attribute 'get'`.
- `test_check.py::test_docs_read_as_other_than_utf8_are_a_setup_error_or_a_fetch_error`: `UnicodeDecodeError`.
- `test_cli.py::test_a_corrupt_fetch_record_is_one_error_line`: stderr is a `JSONDecodeError` traceback.
- `test_cli.py::test_non_utf8_cached_docs_are_one_error_line`: stderr is a `UnicodeDecodeError` traceback.
- `test_state.py::test_a_snapshot_page_read_as_other_than_utf8_is_a_setup_error`: `UnicodeDecodeError`.

- [x] **Step 3: Implement.** Apply these edits in order.
> Deviation: the plan writes Edit 13's pure deletion of `import json` as an empty replacement, which left a blank line in cli.py's stdlib imports; the prototype deletes the line outright. Fixed after the final review in 9fc8136. Every later dispatch read an empty replacement as "delete the lines with their line ending".

**Edit 1.** `build/cc_guide/baseline.py`. Replace:

````python
from state import Manifest, SetupError, Snapshot, block_namer, group_terms, no_snapshot
````

with:

````python
from state import Manifest, SetupError, Snapshot, block_namer, group_terms, no_snapshot, read_utf8
````

**Edit 2.** `build/cc_guide/baseline.py` (in or near `init`). Replace:

````python
                   'llms': sorted(parse_llms(llms.read_text(encoding='utf-8'))) if llms.is_file() else []}
````

with:

````python
                   'llms': sorted(parse_llms(read_utf8(llms))) if llms.is_file() else []}
````

**Edit 3.** `build/cc_guide/baseline.py` (in or near `init`). Replace:

````python
                blocks[page] = select_blocks(path.read_text(encoding='utf-8'), mark, watched)
````

with:

````python
                blocks[page] = select_blocks(read_utf8(path), mark, watched)
````

**Edit 4.** `build/cc_guide/baseline.py` (in or near `rebaseline`). Replace:

````python
    slugs = parse_llms(llms_path.read_text(encoding='utf-8'))
````

with:

````python
    slugs = parse_llms(read_utf8(llms_path))
````

**Edit 5.** `build/cc_guide/baseline.py` (in or near `rebaseline`). Replace:

````python
        text = path.read_text(encoding='utf-8')
````

with:

````python
        text = read_utf8(path)
````

**Edit 6.** `build/cc_guide/check.py`. Replace:

````python
                   snapshot_text)
````

with:

````python
                   read_fetch, read_utf8, snapshot_text)
````

**Edit 7.** `build/cc_guide/check.py` (in or near `http_get`). Replace:

````python
    raise FetchError(f'{url}: {error}')


class Docs(NamedTuple):
````

with:

````python
    raise FetchError(f'{url}: {error}')


def utf8(body: bytes) -> str | None:
    '''A fetched body as UTF-8 text, or None when it is not.'''
    try:
        return body.decode('utf-8')
    except UnicodeDecodeError:
        return None


class Docs(NamedTuple):
````

**Edit 8.** `build/cc_guide/check.py` (in or near `offline_docs`). Replace:

````python
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
````

with:

````python
def offline_docs(manifest: Manifest, folder: Path) -> Docs:
    '''R6.1 --docs: the docs read from a local directory, named as the cache
    names them. A page file that is absent is a missing page.'''
    def read(name: str) -> str | None:
        path = folder / name
        return read_utf8(path) if path.is_file() else None
    changelog, llms = read(CHANGELOG), read(LLMS)
    if changelog is None or llms is None:
        raise SetupError(f'{folder}: needs {CHANGELOG} and {LLMS}')
    return Docs(changelog, llms, {p: read(page_file(p)) for p in manifest.pages()},
                str(folder), [], set())
````

**Edit 9.** `build/cc_guide/check.py` (in or near `live_docs`). Replace:

````python
    record = fetch_record(cache)
    previous = json.loads(record.read_text(encoding='utf-8')).get('changelog_head') if record.is_file() else None
````

with:

````python
    record = read_fetch(cache)
    previous = record['changelog_head'] if record else None
````

**Edit 10.** `build/cc_guide/check.py` (in or near `live_docs`). Replace:

````python
        fetched[name] = body.decode('utf-8')
````

with:

````python
        text = utf8(body)
        if text is None:
            raise FetchError(f'{url}: not UTF-8 text')
        fetched[name] = text
````

**Edit 11.** `build/cc_guide/check.py` (in or near `live_docs`). Replace:

````python
            error = f'{page_url(page, manifest.sources)}: HTTP {got[0]}'
````

with:

````python
            error = f'{page_url(page, manifest.sources)}: HTTP {got[0]}'
        if error is None and got[0] == 200 and utf8(got[1]) is None:
            error = f'{page_url(page, manifest.sources)}: not UTF-8 text'
````

**Edit 12.** `build/cc_guide/check.py` (in or near `live_docs`). Replace:

````python
    record.write_text(json.dumps({'fetched_at': now.isoformat(timespec='seconds'),
                                  'changelog_head': head}, indent=1) + '\n', encoding='utf-8')
    texts = {p: (folder / page_file(p)).read_text(encoding='utf-8')
             if (folder / page_file(p)).is_file() else None for p in pages}
````

with:

````python
    fetch_record(cache).write_text(json.dumps({'fetched_at': now.isoformat(timespec='seconds'),
                                               'changelog_head': head}, indent=1) + '\n', encoding='utf-8')
    texts = {p: read_utf8(folder / page_file(p)) if (folder / page_file(p)).is_file() else None for p in pages}
````

**Edit 13.** `build/cc_guide/cli.py`. Replace:

````python
import json
````

with:

````python

````

**Edit 14.** `build/cc_guide/cli.py`. Replace:

````python
                   dump_baseline, fetch_record, is_iso_date, is_label, latest_docs, newest_changelog,
                   parse_baseline, parse_manifest, snapshot_docs, snapshot_text)
````

with:

````python
                   dump_baseline, is_iso_date, is_label, latest_docs, newest_changelog, parse_baseline,
                   parse_manifest, read_fetch, read_utf8, snapshot_docs, snapshot_text)
````

**Edit 15.** `build/cc_guide/cli.py` (in or near `cached_releases`). Replace:

````python
def cached_releases(cache: Path):
    '''The newest cached changelog's releases (R5: latest/, else the 2.1.288
    snapshot), or None when neither is cached. A changelog that does not
    parse, or holds no release, is a SetupError (check.releases_of).'''
    path = newest_changelog(cache)
    if path is None:
        return None
    return releases_of(path.read_text(encoding='utf-8'), str(path))
````

with:

````python
def cached_releases(cache: Path):
    '''The newest cached changelog's releases (R5: latest/, else the 2.1.288
    snapshot), or None when neither is cached. A changelog that does not
    parse, or holds no release, is a SetupError (check.releases_of).'''
    path = newest_changelog(cache)
    if path is None:
        return None
    return releases_of(read_utf8(path), str(path))
````

**Edit 16.** `build/cc_guide/cli.py` (in or near `run_baseline`). Replace:

````python
        record = fetch_record(cache)
        if not record.is_file():
            raise SetupError('no latest fetch: run check first')
        release = json.loads(record.read_text(encoding='utf-8'))['changelog_head']
````

with:

````python
        record = read_fetch(cache)
        if record is None:
            raise SetupError('no latest fetch: run check first')
        release = record['changelog_head']
````

**Edit 17.** `build/cc_guide/state.py` (in or near `fetch_record`). Replace:

````python
    return cache / 'latest' / 'fetch.json'


def snapshot_docs(cache: Path, release: str) -> Path:
````

with:

````python
    return cache / 'latest' / 'fetch.json'


def read_utf8(path: Path) -> str:
    '''A cached or local docs file's text. A file that is not UTF-8 is a
    SetupError naming it, so it prints one cc-guide: line.'''
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError as exc:
        raise SetupError(f'{path}: not UTF-8 text ({exc.reason} at byte {exc.start})') from None


def read_fetch(cache: Path) -> dict | None:
    '''The last fetch's record (R6.4), or None before the first fetch. A
    record that does not parse, or names no changelog head, is a SetupError.'''
    path = fetch_record(cache)
    if not path.is_file():
        return None
    try:
        record = json.loads(read_utf8(path))
    except json.JSONDecodeError as exc:
        raise SetupError(f'{path}: not valid JSON ({exc}); delete it and run check') from None
    if not (isinstance(record, dict) and is_label(record.get('changelog_head'))):
        raise SetupError(f'{path}: names no changelog_head release; delete it and run check')
    return record


def snapshot_docs(cache: Path, release: str) -> Path:
````

**Edit 18.** `build/cc_guide/state.py` (in or near `snapshot_text`). Replace:

````python
def snapshot_text(cache: Path, page: str, release: str) -> str | None:
    '''The cache's Snapshot: the page as <release>/docs holds it.'''
    path = snapshot_docs(cache, release) / page_file(page)
    return path.read_text(encoding='utf-8') if path.is_file() else None
````

with:

````python
def snapshot_text(cache: Path, page: str, release: str) -> str | None:
    '''The cache's Snapshot: the page as <release>/docs holds it.'''
    path = snapshot_docs(cache, release) / page_file(page)
    return read_utf8(path) if path.is_file() else None
````

- [x] **Step 4: Run the suite and confirm GREEN.**

Run the Step 2 command again. Expected: `169 passed` (+5).

- [x] **Step 5: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && [ "$(git branch --show-current)" = chore/cc-guide-hardening ] && git add build/cc_guide/state.py build/cc_guide/check.py build/cc_guide/cli.py build/cc_guide/baseline.py build/cc_guide/test_state.py build/cc_guide/test_check.py build/cc_guide/test_cli.py && git commit -m "fix(cc_guide): one error line for unreadable cached docs or fetch record

A cached or local docs file that is not UTF-8 is a SetupError naming it
(state.read_utf8), and so is a corrupt latest/fetch.json
(state.read_fetch), which check and rebaseline both parsed bare. A
fetched page that is not UTF-8 is a fetch error: left unread and
uncached, as on a failed fetch.

Plan 39, Task 4 (deferred item: every input error prints a cc-guide: line).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Blocks and the changelog (items 49 and 50; T3-m2, T3-m3, T3-m5, T3-m6, T4-m1–T4-m5, T4-m7, FR-m5)

**Files:**
- Modify: `build/cc_guide/blocks.py`, `build/cc_guide/docs.py`
- Test: `build/cc_guide/cc_fixtures.py`, `build/cc_guide/test_blocks.py`, `build/cc_guide/test_docs.py`, `build/cc_guide/test_check.py`, `build/cc_guide/test_cli.py`

**Interfaces:**
- `blocks.fence_spans` follows CommonMark: a backtick opener whose info string holds a backtick opens no fence (FR-m5). The open fence is a `_Opener(NamedTuple)` with fields `char`, `length`, `line` and `info`, read by name (T3-m5). `key_names(keys: Iterable[str])` and `contains_term(…, terms: Iterable[str])` gain their annotations.
- `docs.LABEL_RE = re.compile(r'\d+(?:\.\d+)+')`, unanchored, used with `fullmatch`, so `version_key('2.1.288\n')` raises (T4-m1).
- `docs.parse_changelog` errors read `line {n}: …`. The caller prefixes the file, so check says `changelog: line 8: …` where it said `changelog: changelog line 8: …`. A repeat reads `line {n}: release label {label} repeats line {first}` (T4-m3).
- `cc_fixtures.LLMS_TEXT` gains a `/docs/_llms/` index line and a platform line, which every `llms.txt` reader must skip. The first edit's old text starts at `CHANGELOG_TEXT`'s closing `])`, but only `LLMS_TEXT` changes.

- [x] **Step 1: Write the failing tests.** Apply these edits in order.

**Edit 1.** `build/cc_guide/cc_fixtures.py` (in or near `CHANGELOG_TEXT`). Replace:

````python
])


LLMS_TEXT = '\n'.join([
````

with:

````python
])


# Two lines are not code pages: a translation index under /docs/_llms/, as
# the real llms.txt lists them, and a platform page.
LLMS_TEXT = '\n'.join([
````

**Edit 2.** `build/cc_guide/cc_fixtures.py` (in or near `LLMS_TEXT`). Replace:

````python
    '- [Plugin parts](https://code.claude.com/docs/en/plugins/components.md): A nested slug.',
````

with:

````python
    '- [Plugin parts](https://code.claude.com/docs/en/plugins/components.md): A nested slug.',
    '- [Fixture docs in French](https://code.claude.com/docs/_llms/fr.md): An index, not a page.',
    '- [Pricing](https://platform.claude.com/docs/en/pricing.md): A platform page.',
````

**Edit 3.** `build/cc_guide/test_blocks.py`. Replace:

````python
and selection (drift spec R3).'''
````

with:

````python
and selection (drift spec R3).'''
import hashlib

````

**Edit 4.** `build/cc_guide/test_blocks.py` (in or near `test_an_unclosed_fence_runs_to_the_end`). Replace:

````python
    assert blocks.fenced_lines(['a', TILDE, '## b', 'c']) == {1, 2, 3}
````

with:

````python
    assert blocks.fenced_lines(['a', TILDE, '## b', 'c']) == {1, 2, 3}


def test_a_backtick_in_a_backtick_openers_info_string_opens_no_fence():
    '''CommonMark: a backtick fence's info string holds no backtick, so such
    a line is inline code. A tilde fence's info string may hold one. No
    cached docs page or guide line had such an opener on 2026-10-08.'''
    assert blocks.fenced_lines([FENCE + 'x`y', '# heading', FENCE]) == {2}
    assert blocks.fenced_lines([TILDE + 'x`y', '# heading', TILDE]) == {0, 1, 2}
````

**Edit 5.** `build/cc_guide/test_blocks.py` (in or near `test_block_hash_is_sixteen_hex_of_the_normalized_text`). Replace:

````python
    assert blocks.block_hash('Use [it](/a) later.') != h


def test_key_parts_drop_link_targets_and_cap_at_sixty_characters():
````

with:

````python
    assert blocks.block_hash('Use [it](/a) later.') != h


def test_block_hash_is_sha256_over_the_normalized_lines_joined_by_newlines():
    assert blocks.block_hash('a') == hashlib.sha256(b'a').hexdigest()[:16]
    assert blocks.block_hash(' a \n\n b ') == hashlib.sha256(b'a\nb').hexdigest()[:16]


def test_a_link_whose_title_wraps_to_the_next_line_keeps_its_target():
    '''LINK_RE stops at a newline (plan 38, ruling 2), so code such as
    f[k](\\nx,\\n) is never read as a link. A wrapped link title therefore
    keeps its target too. None of the 133 cached docs pages had one on
    2026-10-08, so this is recorded as needing no action (plan 39).'''
    assert blocks.normalize('[a](/x\n"Title")') == '[a](/x\n"Title")'


def test_key_parts_drop_link_targets_and_cap_at_sixty_characters():
````

**Edit 6.** `build/cc_guide/test_blocks.py` (in or near `test_key_parts_drop_link_targets_and_cap_at_sixty_characters`). Replace:

````python
    assert len(blocks.key_part(long)) == 60
````

with:

````python
    assert len(blocks.key_part(long)) == 60


def test_a_key_part_of_sixty_characters_is_kept_and_one_of_sixty_one_is_cut():
    assert blocks.key_part('x' * 60) == 'x' * 60
    assert blocks.key_part('x' * 61) == 'x' * 59 + '…'
````

**Edit 7.** `build/cc_guide/test_check.py` (in or near `test_a_malformed_changelog_is_a_setup_error`). Replace:

````python
def test_a_malformed_changelog_is_a_setup_error(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    write_tree(docs_dir, {'changelog.md': DOCS['changelog.md'].replace('October 1, 2026', '2026-10-01')})
    with pytest.raises(ValueError) as cause:
        datetime.strptime('2026-10-01', '%B %d, %Y')
    with pytest.raises(state.SetupError) as err:
        run_check(repo, tmp_path / 'cache', docs_dir)
    assert str(err.value) == f'changelog: changelog line 8: {cause.value}'
````

with:

````python
def test_a_malformed_changelog_is_a_setup_error(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    write_tree(docs_dir, {'changelog.md': DOCS['changelog.md'].replace('October 1, 2026', '2026-10-01')})
    with pytest.raises(ValueError) as cause:
        datetime.strptime('2026-10-01', '%B %d, %Y')
    with pytest.raises(state.SetupError) as err:
        run_check(repo, tmp_path / 'cache', docs_dir)
    assert str(err.value) == f'changelog: line 8: {cause.value}'
````

**Edit 8.** `build/cc_guide/test_cli.py` (in or near `test_a_malformed_or_empty_cached_changelog_exits_two`). Replace:

````python
def test_a_malformed_or_empty_cached_changelog_exits_two(world, capsys):
    _, cache, _ = world
    changelog = state.latest_docs(cache) / 'changelog.md'
    changelog.write_text(changelog.read_text().replace('October 1, 2026', '2026-10-01'))
    assert main(cache, 'lint') == 2
    with pytest.raises(ValueError) as cause:
        datetime.strptime('2026-10-01', '%B %d, %Y')
    assert capsys.readouterr() == ('', f'cc-guide: {changelog}: changelog line 8: {cause.value}\n')
    changelog.write_text('# Changelog\n')
    assert main(cache, 'lint') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {changelog}: no <Update> release blocks\n')
````

with:

````python
def test_a_malformed_or_empty_cached_changelog_exits_two(world, capsys):
    _, cache, _ = world
    changelog = state.latest_docs(cache) / 'changelog.md'
    changelog.write_text(changelog.read_text().replace('October 1, 2026', '2026-10-01'))
    assert main(cache, 'lint') == 2
    with pytest.raises(ValueError) as cause:
        datetime.strptime('2026-10-01', '%B %d, %Y')
    assert capsys.readouterr() == ('', f'cc-guide: {changelog}: line 8: {cause.value}\n')
    changelog.write_text('# Changelog\n')
    assert main(cache, 'lint') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {changelog}: no <Update> release blocks\n')
````

**Edit 9.** `build/cc_guide/test_docs.py`. Replace:

````python
from datetime import date
````

with:

````python
from datetime import date, datetime
````

**Edit 10.** `build/cc_guide/test_docs.py` (in or near `test_version_key_rejects_what_is_not_a_label`). Replace:

````python
@pytest.mark.parametrize('label', ['2.1.x', '', '2.1.288-beta', 'v2.1.288'])
def test_version_key_rejects_what_is_not_a_label(label):
    with pytest.raises(ValueError):
        docs.version_key(label)
````

with:

````python
@pytest.mark.parametrize('label', ['2.1.x', '', '2.1.288-beta', 'v2.1.288', '2.1.288\n'])
def test_version_key_rejects_what_is_not_a_label(label):
    with pytest.raises(ValueError):
        docs.version_key(label)
````

**Edit 11.** `build/cc_guide/test_docs.py`. Replace:

````python
@pytest.mark.parametrize('text', [
    '<Update label="2.1.9" description="2026-07-01">\n</Update>\n',
    '<Update label="2.1.x" description="July 1, 2026">\n</Update>\n',
    ('<Update label="2.1.9" description="July 1, 2026">\n</Update>\n'
     '<Update label="2.1.9" description="July 2, 2026">\n</Update>\n'),
    '<Update label="2.1.9" date="July 1, 2026">\n</Update>\n',
])
def test_changelog_rejects_a_bad_date_a_bad_label_a_repeat_or_an_unknown_tag(text):
    with pytest.raises(ValueError):
        docs.parse_changelog(text)
````

with:

````python
def test_a_bad_release_date_names_its_line():
    with pytest.raises(ValueError) as cause:
        datetime.strptime('2026-07-01', '%B %d, %Y')
    with pytest.raises(ValueError) as err:
        docs.parse_changelog('\n<Update label="2.1.9" description="2026-07-01">\n</Update>\n')
    assert str(err.value) == f'line 2: {cause.value}'


@pytest.mark.parametrize('text, message', [
    ('<Update label="2.1.x" description="July 1, 2026">\n</Update>\n', "line 1: not a release label: '2.1.x'"),
    ('<Update label="2.1.9" description="July 1, 2026">\n</Update>\n'
     '<Update label="2.1.9" description="July 2, 2026">\n</Update>\n', 'line 3: release label 2.1.9 repeats line 1'),
    ('<Update label="2.1.9" date="July 1, 2026">\n</Update>\n', 'line 1: unrecognized <Update> tag'),
    ('<Update label="2.1.9">\n</Update>\n', 'line 1: unrecognized <Update> tag'),
    ('\n  <Update label="2.1.9" description="July 1, 2026" >\n', 'line 2: unrecognized <Update> tag'),
])
def test_changelog_errors_name_their_line(text, message):
    with pytest.raises(ValueError) as err:
        docs.parse_changelog(text)
    assert str(err.value) == message


def test_a_bullet_after_a_closed_release_belongs_to_no_release():
    text = '<Update label="2.1.9" description="July 1, 2026">\n  * in\n</Update>\n  * out\n'
    assert docs.parse_changelog(text)[0].bullets == ['in']


def test_a_release_keeps_only_its_bullets():
    '''A non-bullet line inside a release is dropped. The real changelog's
    release blocks held only bullets on 2026-10-08 (6,970 lines, no other
    kind), so this is recorded as needing no action (plan 39).'''
    text = '<Update label="2.1.9" description="July 1, 2026">\n  * one\n  A stray line.\n\n  * two\n</Update>\n'
    assert docs.parse_changelog(text)[0].bullets == ['one', 'two']
````

- [x] **Step 2: Run the suite and confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf`
Expected: `10 failed, 168 passed`. The fixes:
- `test_blocks.py::test_a_backtick_in_a_backtick_openers_info_string_opens_no_fence`: `assert {0, 1, 2} == {2}`. The line opened a fence.
- `test_docs.py::test_version_key_rejects_what_is_not_a_label[2.1.288\n]`: `DID NOT RAISE ValueError`.
- `test_docs.py::test_a_bad_release_date_names_its_line`: the message starts `changelog line 2:`, not `line 2:`.
- `test_docs.py::test_changelog_errors_name_their_line`, all five cases. Each message starts `changelog line N:`, and the repeat case reads `changelog repeats a release label`, naming no label.
- `test_check.py::test_a_malformed_changelog_is_a_setup_error` and `test_cli.py::test_a_malformed_or_empty_cached_changelog_exits_two`: the stutter, `changelog: changelog line 8:`.

The pins, which pass now:
- `test_blocks.py`: `test_block_hash_is_sha256_over_the_normalized_lines_joined_by_newlines` (T3-m2), `test_a_key_part_of_sixty_characters_is_kept_and_one_of_sixty_one_is_cut` (T3-m3) and `test_a_link_whose_title_wraps_to_the_next_line_keeps_its_target` (T3-m6, no action).
- `test_docs.py`: `test_a_bullet_after_a_closed_release_belongs_to_no_release` (T4-m4) and `test_a_release_keeps_only_its_bullets` (T4-m5, no action).

- [x] **Step 3: Implement.** Apply these edits in order.

**Edit 1.** `build/cc_guide/blocks.py`. Replace:

````python
import re
````

with:

````python
import re
from collections.abc import Iterable
from typing import NamedTuple
````

**Edit 2.** `build/cc_guide/blocks.py` (in or near `fence_spans`). Replace:

````python
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
````

with:

````python
class _Opener(NamedTuple):
    char: str     # ` or ~
    length: int   # the opening run's length
    line: int     # 0-based index of the opening line
    info: str     # the info string


def fence_spans(lines: list[str]) -> list[tuple[int, int | None, str]]:
    '''Each fenced code block as (open, close, info): 0-based line indexes,
    close None when the fence never closes (R3.1). A fence opens on three or
    more backticks or tildes at any indentation, and closes only on a line
    holding nothing but a run of the same character at least as long. As in
    CommonMark, a backtick opener's info string holds no backtick.'''
    spans: list[tuple[int, int | None, str]] = []
    fence: _Opener | None = None
    for i, line in enumerate(lines):
        if fence is None:
            m = FENCE_OPEN_RE.match(line)
            info = line[m.end():] if m else ''
            if m and not (m.group(1)[0] == '`' and '`' in info):
                fence = _Opener(m.group(1)[0], len(m.group(1)), i, info.strip())
            continue
        s = line.strip()
        if s and set(s) == {fence.char} and len(s) >= fence.length:
            spans.append((fence.line, i, fence.info))
            fence = None
    if fence is not None:
        spans.append((fence.line, None, fence.info))
    return spans
````

**Edit 3.** `build/cc_guide/blocks.py` (in or near `key_names`). Replace:

````python
def key_names(keys) -> dict[str, str]:
    '''Key hash -> key over `keys`, to name baselined blocks.'''
    return {key_hash(k): k for k in keys}
````

with:

````python
def key_names(keys: Iterable[str]) -> dict[str, str]:
    '''Key hash -> key over `keys`, to name baselined blocks.'''
    return {key_hash(k): k for k in keys}
````

**Edit 4.** `build/cc_guide/blocks.py` (in or near `contains_term`). Replace:

````python
def contains_term(key: str, text: str, terms) -> bool:
    '''Case-sensitive substring match of any term in a block's key or text.'''
    return any(t in key or t in text for t in terms)
````

with:

````python
def contains_term(key: str, text: str, terms: Iterable[str]) -> bool:
    '''Case-sensitive substring match of any term in a block's key or text.'''
    return any(t in key or t in text for t in terms)
````

**Edit 5.** `build/cc_guide/docs.py` (in or near `LABEL_RE`). Replace:

````python
LABEL_RE = re.compile(r'^\d+(?:\.\d+)+$')
````

with:

````python
LABEL_RE = re.compile(r'\d+(?:\.\d+)+')
````

**Edit 6.** `build/cc_guide/docs.py` (in or near `version_key`). Replace:

````python
def version_key(label: str) -> tuple[int, ...]:
    '''R2.4: versions compare as integer tuples, so 2.1.288.1 sorts after
    2.1.288 and before 2.1.289.'''
    if not LABEL_RE.match(label):
        raise ValueError(f'not a release label: {label!r}')
    return tuple(int(part) for part in label.split('.'))
````

with:

````python
def version_key(label: str) -> tuple[int, ...]:
    '''R2.4: versions compare as integer tuples, so 2.1.288.1 sorts after
    2.1.288 and before 2.1.289.'''
    if not LABEL_RE.fullmatch(label):
        raise ValueError(f'not a release label: {label!r}')
    return tuple(int(part) for part in label.split('.'))
````

**Edit 7.** `build/cc_guide/docs.py` (in or near `parse_changelog`). Replace:

````python
    ValueError on an unparseable label or date, an <Update> tag it cannot
    read, or a repeated label.'''
    releases: list[Release] = []
````

with:

````python
    ValueError, naming the line, on an unparseable label or date, an
    <Update> tag it cannot read, or a repeated label; the caller names the
    file.'''
    releases: list[Release] = []
    first: dict[str, int] = {}
````

**Edit 8.** `build/cc_guide/docs.py` (in or near `parse_changelog`). Replace:

````python
                raise ValueError(f'changelog line {n}: {exc}') from None
            current = Release(label, when, [])
            releases.append(current)
        elif line.lstrip().startswith('<Update'):
            raise ValueError(f'changelog line {n}: unrecognized <Update> tag')
````

with:

````python
                raise ValueError(f'line {n}: {exc}') from None
            if label in first:
                raise ValueError(f'line {n}: release label {label} repeats line {first[label]}')
            first[label] = n
            current = Release(label, when, [])
            releases.append(current)
        elif line.lstrip().startswith('<Update'):
            raise ValueError(f'line {n}: unrecognized <Update> tag')
````

**Edit 9.** `build/cc_guide/docs.py` (in or near `parse_changelog`). Replace:

````python
    labels = [r.label for r in releases]
    if len(set(labels)) != len(labels):
        raise ValueError('changelog repeats a release label')
````

with:

````python

````

- [x] **Step 4: Run the suite and confirm GREEN.**

Run the Step 2 command again. Expected: `178 passed` (+9: thirteen tests added, and the four cases of `test_changelog_rejects_a_bad_date_a_bad_label_a_repeat_or_an_unknown_tag` replaced).

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && uv run --python 3.13 python build/cc_guide/cli.py lint; echo "exit=$?"`
Expected: `exit=0`.

- [x] **Step 5: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && [ "$(git branch --show-current)" = chore/cc-guide-hardening ] && git add build/cc_guide/blocks.py build/cc_guide/docs.py build/cc_guide/cc_fixtures.py build/cc_guide/test_blocks.py build/cc_guide/test_docs.py build/cc_guide/test_check.py build/cc_guide/test_cli.py && git commit -m "fix(cc_guide): CommonMark backtick fences, whole-string labels, numbered changelog errors

A backtick opener whose info string holds a backtick opens no fence, as
in CommonMark; re-blocking the 2.1.288 snapshot changes no hash. A label
must match whole, so 2.1.288 with a trailing newline is no label.
Changelog errors read line N: and a repeat names its label, which ends
check's changelog: changelog line stutter. The fence opener is a
NamedTuple, and the hash, the key-part cap, wrapped link titles and
bullets-only releases are pinned.

Plan 39, Task 5 (deferred items: test coverage and edge cases; style,
DRY and naming).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: The guide's edges and lint's checks (items 49 and 50; T5-m2, T5-m3, T8-m2, T8-m4–T8-m8)

**Files:**
- Modify: `build/cc_guide/lint.py`
- Test: `build/cc_guide/test_guide.py`, `build/cc_guide/test_lint.py`

**Interfaces:**
- Produces, in `lint.py`:
  - `NO_CHANGELOG = 'release-label check skipped: no changelog to read'`.
  - `label_problems(lines: list[str], labels: set[str]) -> list[str]`.
  - `table_problems(lines: list[str]) -> list[str]`: a table starts only at a `|` line followed by a separator row, as `blocks.is_table_start` reads it (plan 38, decision 12).
  - `json_problems(lines: list[str]) -> list[str]`.
  - These replace `quality_problems`, which returned two channels (T8-m6, ruling 2).
- `lint(guide_text, manifest, state, labels)` keeps its signature and its violation order: anchors, ID sets, text hashes, the stamp region, labels, tables, json. It returns `[NO_CHANGELOG]` as its notes when `labels` is `None`.
- `stamp_problems` compares `guide.stamp_content(...)` with the rendered stamp (T8-m2). `cell_count` loses its dead `\|` guard (T8-m5), and `id_set_problems` joins its names before the f-string (T8-m8).

- [x] **Step 1: Write the failing tests.** Apply these edits in order.

**Edit 1.** `build/cc_guide/test_guide.py`. Replace:

````python
from cc_fixtures import FENCE, FIXTURE_STAMP, GUIDE_IDS, guide_text, isolated_home  # noqa: F401
````

with:

````python
from cc_fixtures import FENCE, FIXTURE_STAMP, GUIDE_IDS, TILDE, guide_text, isolated_home  # noqa: F401
````

**Edit 2.** `build/cc_guide/test_guide.py` (in or near `test_a_fenced_hash_line_stays_inside_its_section`). Replace:

````python
    assert '## not a heading inside a fence' not in reference.prose
````

with:

````python
    assert '## not a heading inside a fence' not in reference.prose


def test_a_heading_in_a_tilde_or_an_indented_fence_is_no_section():
    text = '\n'.join(['## A', '<!-- cc: a.one -->', TILDE, '## not a heading', TILDE,
                      '  ' + FENCE, '### nor this', '  ' + FENCE])
    assert [s.heading for s in guide.sections(text)] == ['## A']


def test_an_anchor_like_line_inside_a_fence_is_no_stray_anchor():
    text = '\n'.join(['## A', '<!-- cc: a.one -->', FENCE + 'markdown', '<!-- cc: a.sample -->', FENCE])
    assert guide.anchor_problems(text) == []
````

**Edit 3.** `build/cc_guide/test_guide.py` (in or near `test_terms_keep_three_to_sixty_characters_and_drop_stop_terms`). Replace:

````python
    assert guide.section_terms(by_id(guide_text())['alpha.overview']) == {'ALPHA_TOOL'}


def test_terms_skip_fenced_code_and_apply_extra_and_exclude_terms():
````

with:

````python
    assert guide.section_terms(by_id(guide_text())['alpha.overview']) == {'ALPHA_TOOL'}


def test_terms_keep_three_and_sixty_characters_and_drop_two_and_sixty_one():
    sixty, sixty_one = 'x' * 60, 'y' * 61
    text = '\n'.join(['## A', '<!-- cc: a.one -->', f'`ab` `abc` `{sixty}` `{sixty_one}`'])
    assert guide.section_terms(guide.sections(text)[0]) == {'abc', sixty}


def test_terms_skip_fenced_code_and_apply_extra_and_exclude_terms():
````

**Edit 4.** `build/cc_guide/test_guide.py` (in or near `test_a_missing_doubled_reversed_or_fenced_marker_means_no_region`). Replace:

````python
    assert guide.stamp_content(broken(guide_text())) is None


def test_render_stamp_names_the_oldest_checked_and_audited():
````

with:

````python
    assert guide.stamp_content(broken(guide_text())) is None


def test_with_stamp_raises_without_a_region():
    with pytest.raises(ValueError) as err:
        guide.with_stamp('## A\n', '> New stamp.')
    assert str(err.value) == 'the guide has no stamp region'


def test_render_stamp_breaks_a_tie_on_the_other_field():
    '''Equal `checked` releases go to the earlier date; equal `audited`
    dates go to the older release.'''
    states = {
        'a.one': {'checked': {'release': '2.1.9', 'date': '2026-09-09'},
                  'audited': {'release': '2.1.10', 'date': '2026-08-01'}},
        'a.two': {'checked': {'release': '2.1.9', 'date': '2026-09-05'},
                  'audited': {'release': '2.1.9', 'date': '2026-08-01'}},
    }
    assert guide.render_stamp(states) == (
        '> Checked against the Claude Code docs and changelog through 2.1.9 on 2026-09-05; '
        'oldest full re-verification 2026-08-01, at 2.1.9.')


def test_render_stamp_names_the_oldest_checked_and_audited():
````

**Edit 5.** `build/cc_guide/test_lint.py` (in or near `test_every_table_row_keeps_its_headers_cell_count`). Replace:

````python
        f'guide line {line}: table row has 3 cells; its header has 2']


def test_every_json_block_must_parse(docs_dir):
````

with:

````python
        f'guide line {line}: table row has 3 cells; its header has 2']


def test_pipe_lines_without_a_separator_row_or_inside_a_fence_are_no_table(docs_dir):
    '''A table starts at a | line followed by a separator row (plan 38,
    decision 12), and fenced lines are code.'''
    text = guide_text() + f'| a | b |\n| c |\n\n{FENCE}\n| a | b |\n|---|---|\n| c |\n{FENCE}\n'
    assert run(text, synced(text, fixture_state(docs_dir)))[0] == []


def test_a_row_ending_in_an_escaped_pipe_counts_its_cells():
    assert lint.cell_count('| x | y\\|') == 2
    assert lint.cell_count('| x | y\\| |') == 2


def test_an_unclosed_json_block_runs_to_the_end(docs_dir):
    text = guide_text() + f'{FENCE}json\n{{"a": 1,}}\n'
    line = len(text.split('\n')) - 2
    assert run(text, synced(text, fixture_state(docs_dir)))[0] == [
        f'guide line {line}: json block does not parse (Illegal trailing comma before end of object)']


def test_a_section_missing_from_the_manifest_alone_is_named(docs_dir):
    manifest = state.parse_manifest(MANIFEST_TOML.replace("'beta.overview', 'beta.reference'", "'beta.overview'"))
    violations, _ = run(guide_text(), fixture_state(docs_dir), manifest=manifest)
    assert violations == ['section beta.reference: missing from manifest.toml']


def test_every_json_block_must_parse(docs_dir):
````

- [x] **Step 2: Run the suite and confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf`
Expected: `1 failed, 186 passed`. The fix: `test_lint.py::test_pipe_lines_without_a_separator_row_or_inside_a_fence_are_no_table`. Lint reads `| a | b |` over `| c |` as a table without a separator row and flags the row (T8-m4).

The pins, which pass now:
- `test_guide.py`: `test_a_heading_in_a_tilde_or_an_indented_fence_is_no_section` (T5-m2), `test_an_anchor_like_line_inside_a_fence_is_no_stray_anchor`, `test_terms_keep_three_and_sixty_characters_and_drop_two_and_sixty_one`, `test_with_stamp_raises_without_a_region` and `test_render_stamp_breaks_a_tie_on_the_other_field` (T5-m3).
- `test_lint.py`: `test_a_row_ending_in_an_escaped_pipe_counts_its_cells`, `test_an_unclosed_json_block_runs_to_the_end` and `test_a_section_missing_from_the_manifest_alone_is_named` (T8-m7).

- [x] **Step 3: Implement.** Apply these edits in order. Besides the fix, they refactor under green: T8-m2, T8-m5, T8-m6 and T8-m8.

**Edit 1.** `build/cc_guide/lint.py`. Replace:

````python
from blocks import CELL_SPLIT_RE, fence_spans, fenced_lines
from guide import NO_STAMP, anchor_problems, render_stamp, sections, stamp_bounds, text_hash
````

with:

````python
from blocks import CELL_SPLIT_RE, fence_spans, fenced_lines, is_table_start
from guide import NO_STAMP, anchor_problems, render_stamp, sections, stamp_bounds, stamp_content, text_hash
````

**Edit 2.** `build/cc_guide/lint.py` (in or near `VERSION_RE`). Replace:

````python
VERSION_RE = re.compile(r'(?<![\d.])2\.1\.\d+(?:\.\d+)*(?!\d)')


def cell_count(row: str) -> int:
    '''Cells in a table row, split on unescaped pipes, outer pipes dropped.'''
    s = row.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|') and not s.endswith('\\|'):
        s = s[:-1]
    return len(CELL_SPLIT_RE.split(s))
````

with:

````python
VERSION_RE = re.compile(r'(?<![\d.])2\.1\.\d+(?:\.\d+)*(?!\d)')
NO_CHANGELOG = 'release-label check skipped: no changelog to read'


def cell_count(row: str) -> int:
    '''Cells in a table row, split on unescaped pipes, outer pipes dropped.
    An escaped final pipe is no split point, so dropping it changes nothing.'''
    s = row.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    return len(CELL_SPLIT_RE.split(s))
````

**Edit 3.** `build/cc_guide/lint.py` (in or near `id_set_problems`). Replace:

````python
        missing = [name for name, ids in where.items() if sid not in ids]
        if missing:
            out.append(f'section {sid}: missing from {" and ".join(missing)}')
````

with:

````python
        missing = ' and '.join(name for name, ids in where.items() if sid not in ids)
        if missing:
            out.append(f'section {sid}: missing from {missing}')
````

**Edit 4.** `build/cc_guide/lint.py` (in or near `stamp_problems`). Replace:

````python
    content = '\n'.join(guide_text.split('\n')[bounds[0] + 1:bounds[1]])
    if content != render_stamp(state['sections']):
````

with:

````python
    if stamp_content(guide_text) != render_stamp(state['sections']):
````

**Edit 5.** `build/cc_guide/lint.py` (in or near `quality_problems`). Replace:

````python
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
````

with:

````python
def label_problems(lines: list[str], labels: set[str]) -> list[str]:
    '''Every 2.1.NNN in the guide is a changelog release label (R5).'''
    return [f'guide line {n}: {v} is not a changelog release label'
            for n, line in enumerate(lines, start=1) for v in VERSION_RE.findall(line) if v not in labels]


def table_problems(lines: list[str]) -> list[str]:
    '''Every table row keeps its header's cell count (R5). A table starts at
    a | line followed by a separator row (plan 38, decision 12).'''
    fenced = fenced_lines(lines)
    out = []
    i = 0
    while i < len(lines):
        if i in fenced or not is_table_start(lines, i, fenced):
            i += 1
            continue
        header = cell_count(lines[i])
        while i < len(lines) and i not in fenced and lines[i].lstrip().startswith('|'):
            if cell_count(lines[i]) != header:
                out.append(f'guide line {i + 1}: table row has {cell_count(lines[i])} cells; '
                           f'its header has {header}')
            i += 1
    return out


def json_problems(lines: list[str]) -> list[str]:
    '''Every json code block parses (R5); an unclosed one runs to the end.'''
    out = []
    for start, close, info in fence_spans(lines):
        if info.split()[:1] == ['json']:
            try:
                json.loads('\n'.join(lines[start + 1:len(lines) if close is None else close]))
            except json.JSONDecodeError as exc:
                out.append(f'guide line {start + 1}: json block does not parse ({exc.msg})')
    return out


def lint(guide_text: str, manifest: Manifest, state: dict,
         labels: set[str] | None) -> tuple[list[str], list[str]]:
    '''R5 without its citation rules: (violations, notes). `labels` are the
    newest changelog's release labels, None when there is no changelog to
    read, which skips the label check with a note. The caller parses the
    changelog, so a malformed one is a setup error there.'''
    lines = guide_text.split('\n')
    violations = (anchor_problems(guide_text) + id_set_problems(guide_text, manifest, state)
                  + hash_problems(guide_text, state) + stamp_problems(guide_text, state)
                  + (label_problems(lines, labels) if labels is not None else [])
                  + table_problems(lines) + json_problems(lines))
    return violations, [NO_CHANGELOG] if labels is None else []
````

- [x] **Step 4: Run the suite and the lint, and confirm GREEN.**

Run the Step 2 command again. Expected: `187 passed` (+9).

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && uv run --python 3.13 python build/cc_guide/cli.py lint; echo "exit=$?"`
Expected: `exit=0`.

- [x] **Step 5: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && [ "$(git branch --show-current)" = chore/cc-guide-hardening ] && git add build/cc_guide/lint.py build/cc_guide/test_guide.py build/cc_guide/test_lint.py && git commit -m "refactor(cc_guide): one function per lint check; a table needs its separator row

quality_problems bundled three checks and two return channels; it becomes
label_problems, table_problems and json_problems, and lint() composes
them. A table starts only at a | line followed by a separator row (plan
38, decision 12). The stamp check reads guide.stamp_content, and a dead
escaped-pipe guard goes. The guide's fence, term, stamp and lint edges
are pinned.

Plan 39, Task 6 (deferred items: test coverage and edge cases; style,
DRY and naming).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: `state.py`'s grammars, `Source` and `parse_manifest` (items 49 and 50; T6-m2, T6-m4, T6-m5, T6-m7, T6-m8)

**Files:**
- Modify: `build/cc_guide/state.py`, `build/cc_guide/guide.py`, `build/cc_guide/blocks.py`, `build/cc_guide/cc_fixtures.py`
- Test: `build/cc_guide/test_state.py`

**Interfaces:**
- Produces, in `guide.py`:
  - `ID_RE = re.compile(r'[a-z0-9-]+(?:\.[a-z0-9-]+)+')`. `ANCHOR_RE` is now built from it.
  - `TEXT_HASH_RE = re.compile(r'sha256:[0-9a-f]{64}')`.
- Produces, in `blocks.py`: `HASH_CHARS = 16` and `HASH_RE = re.compile(rf'[0-9a-f]{{{HASH_CHARS}}}')`. `block_hash` and `key_hash` slice to `HASH_CHARS`.
- All three patterns are unanchored. `state.py` imports them and calls `fullmatch` everywhere, as it does for its own `GROUP_RE = re.compile(r'[a-z0-9-]+')` and `DATE_RE` (Planning record, "Controls").
- Changes in `state.py`:
  - `TABLES`, the manifest's known tables.
  - `mapped_pages(groups: dict[str, Group]) -> list[str]`, shared by `Manifest.pages()` and the exclusion check.
  - `parse_manifest` splits into `_header`, `_groups` (which uses `_pages`), `_terms`, `_exclusions` and `_probes`, plus `_positive`. It keeps every message and their order.
  - `Source.read` in ref mode runs `git cat-file blob <ref>:<path>`, so a directory reads as `None`. Bytes that are not UTF-8 raise `SetupError(f'{ref}:{path}: not UTF-8 text (…)')`. In the working tree it reads through `read_utf8`.
- In `cc_fixtures.py`: `git(repo, *args)` raises `RuntimeError(f'git {command} failed: {stderr}')`, so a failing fixture command shows git's stderr. `json`, `os` and `subprocess` become top-level imports.

- [x] **Step 1: Write the failing tests.** Apply these edits in order.

**Edit 1.** `build/cc_guide/test_state.py` (in or near `test_every_manifest_problem_is_reported_at_once`). Replace:

````python
        f'{state.MANIFEST}: unknown table or key {"stray"!r}',
````

with:

````python
        f"{state.MANIFEST}: unknown table or key 'stray'",
````

**Edit 2.** `build/cc_guide/test_state.py` (in or near `test_a_date_is_yyyy_mm_dd_and_nothing_else_fromisoformat_takes`). Replace:

````python
    assert state.is_iso_date(value) is ok
````

with:

````python
    assert state.is_iso_date(value) is ok


PROBE = "\n[[probe]]\nid = 'p'\nsections = ['beta.reference']\n"


@pytest.mark.parametrize('edit, problem', [
    (lambda t: t.replace('[groups.alpha]', '[groups.Alpha]'), '[groups.Alpha] group IDs are [a-z0-9-]'),
    (lambda t: t.replace('[groups.alpha]', "[groups.'alpha!']"), '[groups.alpha!] group IDs are [a-z0-9-]'),
    (lambda t: t.replace("['alpha.overview', 'alpha.reference']", "['alpha', 'alpha.reference']"),
     "[groups.alpha] 'alpha' is not a section ID"),
    (lambda t: t.replace("['alpha.overview', 'alpha.reference']", '["alpha.overview\\n", \'alpha.reference\']'),
     "[groups.alpha] 'alpha.overview\\n' is not a section ID"),
    (lambda t: t.replace("all = ['tools']\nterms = ['env-vars']\n", ''), '[groups.alpha] maps no page'),
    (lambda t: t.replace('[groups.alpha]', '[groups.alpha]\nextra = 1'),
     '[groups.alpha] holds only sections, all and terms'),
    (lambda t: t.split('[groups.alpha]')[0], '[groups] must hold at least one group'),
    (lambda t: t + "\n[sections.'gamma.one']\nextra_terms = ['x']\n", "[sections.'gamma.one'] is not in any group"),
    (lambda t: t.replace("reason = 'Duplicates the changelog.'", ''),
     '[[exclusion]] needs a page pattern and a reason'),
    (lambda t: t + PROBE + PROBE, '[[probe]] needs a unique id'),
    (lambda t: t + PROBE.replace('beta.reference', 'gamma.one'),
     '[[probe]] p: sections must name grouped sections; files is a list'),
    (lambda t: t + PROBE + "files = 'agents/a.md'\n",
     '[[probe]] p: sections must name grouped sections; files is a list'),
])
def test_each_manifest_rule_names_its_table(edit, problem):
    with pytest.raises(state.SetupError) as err:
        state.parse_manifest(edit(MANIFEST_TOML))
    assert str(err.value) == f'{state.MANIFEST}: {problem}'
````

**Edit 3.** `build/cc_guide/test_state.py` (in or near `test_a_valid_baseline_parses_and_a_broken_one_is_a_setup_error`). Replace:

````python
    assert str(err.value) == f'{state.BASELINE}: not valid JSON ({cause.value})'


def test_dump_baseline_keeps_insertion_order_and_utf8():
````

with:

````python
    assert str(err.value) == f'{state.BASELINE}: not valid JSON ({cause.value})'


@pytest.mark.parametrize('changes, problem', [
    ({'sections': {'alpha.overview': {**SECTION, 'text_hash': SECTION['text_hash'] + '\n'}}},
     'section alpha.overview: needs checked, changed, audited and text_hash'),
    ({'groups': {'alpha': {'blocks': {'tools': {'1' * 17: '0' * 16}}, 'snapshot': {}}}},
     'group alpha: needs blocks (page -> key hash -> block hash) and snapshot (page -> release)'),
    ({'groups': {'alpha': {'blocks': {'tools': {'1' * 16: '0' * 16 + '\n'}}, 'snapshot': {}}}},
     'group alpha: needs blocks (page -> key hash -> block hash) and snapshot (page -> release)'),
])
def test_a_hash_must_be_the_whole_string(changes, problem):
    '''The hash patterns state.py shares are unanchored, so a check that
    matched only a prefix would take a 17th character or a trailing newline.'''
    with pytest.raises(state.SetupError) as err:
        state.parse_baseline(baseline_text(**changes))
    assert str(err.value) == f'{state.BASELINE}: {problem}'


def test_dump_baseline_keeps_insertion_order_and_utf8():
````

**Edit 4.** `build/cc_guide/test_state.py` (in or near `test_a_source_reads_the_working_tree_or_a_commit`). Replace:

````python
def test_a_source_reads_the_working_tree_or_a_commit(tmp_path):
    repo = fixture_repo(tmp_path / 'repo', {'a.txt': 'committed\n'})
    (repo / 'a.txt').write_text('edited\n')
    assert state.Source(repo).read('a.txt') == 'edited\n'
    assert state.Source(repo, 'main').read('a.txt') == 'committed\n'
    assert state.Source(repo, 'main').read('absent.txt') is None
    with pytest.raises(state.SetupError) as err:
        state.Source(repo, 'main').require('absent.txt')
    assert str(err.value) == 'absent.txt: not found in main'
    with pytest.raises(state.SetupError) as err:
        state.Source(repo, 'no-such-ref')
    assert str(err.value) == f'no-such-ref: not a commit in {repo}'
````

with:

````python
def test_a_source_reads_the_working_tree_or_a_commit(tmp_path):
    repo = fixture_repo(tmp_path / 'repo', {'a.txt': 'committed\n', 'sub/b.txt': 'b\n'})
    (repo / 'a.txt').write_text('edited\n')
    assert (state.Source(repo).label, state.Source(repo, 'main').label) == ('the working tree', 'main')
    assert state.Source(repo).read('a.txt') == 'edited\n'
    assert state.Source(repo, 'main').read('a.txt') == 'committed\n'
    assert state.Source(repo, 'main').read('absent.txt') is None
    assert state.Source(repo).read('sub') is None
    assert state.Source(repo, 'main').read('sub') is None  # a tree, not a file
    with pytest.raises(state.SetupError) as err:
        state.Source(repo, 'main').require('absent.txt')
    assert str(err.value) == 'absent.txt: not found in main'
    with pytest.raises(state.SetupError) as err:
        state.Source(repo, 'no-such-ref')
    assert str(err.value) == f'no-such-ref: not a commit in {repo}'


def test_a_source_file_that_is_not_utf8_is_a_setup_error(tmp_path):
    repo = fixture_repo(tmp_path / 'repo', {'a.txt': 'text\n'})
    (repo / 'a.txt').write_bytes(b'\xff')
    git(repo, 'commit', '-qam', 'bytes')
    with pytest.raises(state.SetupError) as err:
        state.Source(repo).read('a.txt')
    assert str(err.value) == f"{repo / 'a.txt'}: not UTF-8 text (invalid start byte at byte 0)"
    with pytest.raises(state.SetupError) as err:
        state.Source(repo, 'main').read('a.txt')
    assert str(err.value) == 'main:a.txt: not UTF-8 text (invalid start byte at byte 0)'


def test_the_fixture_git_helper_reports_gits_stderr(tmp_path):
    repo = fixture_repo(tmp_path / 'repo', {'a.txt': 'text\n'})
    with pytest.raises(RuntimeError) as err:
        git(repo, 'rev-parse', '--verify', 'no-such-ref')
    assert 'Needed a single revision' in str(err.value)


def test_group_terms_fall_back_to_extra_terms_for_a_section_the_guide_lacks():
    grouped = "['beta.overview', 'beta.reference', 'beta.extra']"
    m = state.parse_manifest(MANIFEST_TOML.replace("['beta.overview', 'beta.reference']", grouped)
                             + "\n[sections.'beta.extra']\nextra_terms = ['EXTRA']\n")
    assert state.group_terms(m, guide_text())['beta']['beta.extra'] == {'EXTRA'}


def test_the_fetch_record_sits_beside_latest_docs(tmp_path):
    assert state.fetch_record(tmp_path) == tmp_path / 'latest' / 'fetch.json'
````

- [x] **Step 2: Run the suite and confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf`
Expected: `6 failed, 200 passed`. The fixes:
- `test_state.py::test_each_manifest_rule_names_its_table`, the `'alpha.overview\\n' is not a section ID` case, and `test_state.py::test_a_hash_must_be_the_whole_string`, cases `changes0` and `changes2`: `DID NOT RAISE SetupError`, because `$` matches before a trailing newline.
- `test_state.py::test_a_source_reads_the_working_tree_or_a_commit`: `assert 'tree main:sub\n\nb.txt\n' is None` (T6-m2).
- `test_state.py::test_a_source_file_that_is_not_utf8_is_a_setup_error`: `UnicodeDecodeError`.
- `test_state.py::test_the_fixture_git_helper_reports_gits_stderr`: `subprocess.CalledProcessError`, whose message holds no stderr.

The pins, which pass now:
- The other eleven cases of `test_each_manifest_rule_names_its_table`, including `alpha!`, and case `changes1` of `test_a_hash_must_be_the_whole_string` (the 17-character key).
- `test_group_terms_fall_back_to_extra_terms_for_a_section_the_guide_lacks` and `test_the_fetch_record_sits_beside_latest_docs`.

- [x] **Step 3: Implement.** Apply these edits in order. The `parse_manifest` split, the moved patterns and the `Group` comment are refactors under green.

**Edit 1.** `build/cc_guide/blocks.py` (in or near `KEY_PART_MAX`). Replace:

````python
KEY_PART_MAX = 60
````

with:

````python
KEY_PART_MAX = 60
# block_hash and key_hash keep this many hex characters of SHA-256 (R3.5).
HASH_CHARS = 16
HASH_RE = re.compile(rf'[0-9a-f]{{{HASH_CHARS}}}')
````

**Edit 2.** `build/cc_guide/blocks.py` (in or near `block_hash`). Replace:

````python
def block_hash(text: str) -> str:
    '''R3.5 step 4: the first 16 hex characters of SHA-256 over the
    normalized text, as UTF-8.'''
    return hashlib.sha256(normalize(text).encode('utf-8')).hexdigest()[:16]


def key_hash(key: str) -> str:
    '''A block key as baseline.json stores it (R2.3), so the repo holds no
    docs text: R3.5 step 4's hash over the key as it is, since key_part has
    already normalized it.'''
    return hashlib.sha256(key.encode('utf-8')).hexdigest()[:16]
````

with:

````python
def block_hash(text: str) -> str:
    '''R3.5 step 4: the first 16 hex characters of SHA-256 over the
    normalized text, as UTF-8.'''
    return hashlib.sha256(normalize(text).encode('utf-8')).hexdigest()[:HASH_CHARS]


def key_hash(key: str) -> str:
    '''A block key as baseline.json stores it (R2.3), so the repo holds no
    docs text: R3.5 step 4's hash over the key as it is, since key_part has
    already normalized it.'''
    return hashlib.sha256(key.encode('utf-8')).hexdigest()[:HASH_CHARS]
````

**Edit 3.** `build/cc_guide/cc_fixtures.py`. Replace:

````python
'''
import pytest
````

with:

````python
'''
import json
import os
import subprocess

import pytest
````

**Edit 4.** `build/cc_guide/cc_fixtures.py` (in or near `git`). Replace:

````python
def git(repo, *args: str) -> str:
    '''git in a fixture repo, with an identity and none of the caller's GIT_ variables.'''
    import os
    import subprocess
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    return subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                           '-c', 'commit.gpgsign=false', '-c', 'init.defaultBranch=main', *args],
                          cwd=repo, env=env, capture_output=True, text=True, check=True).stdout
````

with:

````python
def git(repo, *args: str) -> str:
    '''git in a fixture repo, with an identity and none of the caller's GIT_
    variables. A failure raises RuntimeError carrying git's stderr.'''
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    proc = subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                           '-c', 'commit.gpgsign=false', '-c', 'init.defaultBranch=main', *args],
                          cwd=repo, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        command = ' '.join(args)
        raise RuntimeError(f'git {command} failed: {proc.stderr.strip()}')
    return proc.stdout
````

**Edit 5.** `build/cc_guide/cc_fixtures.py` (in or near `prime_cache`). Replace:

````python
def prime_cache(cache, folder, head: str = '2.1.902') -> None:
    '''A cache whose latest/ holds folder's files, as a live check leaves it.'''
    import json
    import state
    write_tree(state.latest_docs(cache), {p.name: p.read_text(encoding='utf-8') for p in folder.iterdir()})
    state.fetch_record(cache).write_text(json.dumps({'fetched_at': '2026-10-04T12:00:00+00:00',
                                                      'changelog_head': head}) + '\n')
````

with:

````python
def prime_cache(cache, folder, head: str = '2.1.902') -> None:
    '''A cache whose latest/ holds folder's files, as a live check leaves it.'''
    import state
    write_tree(state.latest_docs(cache), {p.name: p.read_text(encoding='utf-8') for p in folder.iterdir()})
    state.fetch_record(cache).write_text(json.dumps({'fetched_at': '2026-10-04T12:00:00+00:00',
                                                      'changelog_head': head}) + '\n')
````

**Edit 6.** `build/cc_guide/guide.py` (in or near `ANCHOR_RE`). Replace:

````python
ANCHOR_RE = re.compile(r'^<!-- cc: ([a-z0-9-]+(?:\.[a-z0-9-]+)+) -->$')
````

with:

````python
# A section ID: two or more dot-separated [a-z0-9-] segments (R1.1).
ID_RE = re.compile(r'[a-z0-9-]+(?:\.[a-z0-9-]+)+')
ANCHOR_RE = re.compile(rf'^<!-- cc: ({ID_RE.pattern}) -->$')
# What text_hash returns.
TEXT_HASH_RE = re.compile(r'sha256:[0-9a-f]{64}')
````

**Edit 7.** `build/cc_guide/state.py`. Replace:

````python
from blocks import CELL_SPLIT_RE, key_names, page_blocks
from docs import page_file, version_key
from guide import section_terms, sections
````

with:

````python
from blocks import CELL_SPLIT_RE, HASH_RE, key_names, page_blocks
from docs import page_file, version_key
from guide import ID_RE, TEXT_HASH_RE, section_terms, sections
````

**Edit 8.** `build/cc_guide/state.py` (in or near `ID_RE`). Replace:

````python
ID_RE = re.compile(r'^[a-z0-9-]+(?:\.[a-z0-9-]+)+$')
GROUP_RE = re.compile(r'^[a-z0-9-]+$')
HASH_RE = re.compile(r'^[0-9a-f]{16}$')
TEXT_HASH_RE = re.compile(r'^sha256:[0-9a-f]{64}$')
````

with:

````python
TABLES = ('guide', 'sources', 'cadence', 'groups', 'sections', 'exclusion', 'probe')
GROUP_RE = re.compile(r'[a-z0-9-]+')
````

**Edit 9.** `build/cc_guide/state.py` (in or near `Source`). Replace:

````python
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
````

with:

````python
class Source:
    '''Reads repo files from the working tree (ref None) or from a commit
    through `git cat-file` (R6.1).'''

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
        '''The file's text, or None when no file is there; a directory is no
        file. A file that is not UTF-8 is a SetupError naming it.'''
        if self.ref is None:
            p = self.repo / path
            return read_utf8(p) if p.is_file() else None
        proc = subprocess.run(['git', 'cat-file', 'blob', f'{self.ref}:{path}'], cwd=self.repo,
                              capture_output=True)
        if proc.returncode != 0:
            return None
        try:
            return proc.stdout.decode('utf-8')
        except UnicodeDecodeError as exc:
            raise SetupError(f'{self.ref}:{path}: not UTF-8 text ({exc.reason} at byte {exc.start})') from None

    def require(self, path: str) -> str:
        text = self.read(path)
        if text is None:
            raise SetupError(f'{path}: not found in {self.label}')
        return text


class Group(NamedTuple):
    sections: list[str]
    pages: dict[str, str]  # page -> mark: the `all` pages, then the `terms` pages


def mapped_pages(groups: dict[str, 'Group']) -> list[str]:
    '''Every mapped page once: group by group, each group's `all` pages
    before its `terms` pages.'''
    return list(dict.fromkeys(p for g in groups.values() for p in g.pages))
````

**Edit 10.** `build/cc_guide/state.py` (in or near `Manifest`). Replace:

````python
        '''Every mapped page once, in manifest order.'''
        return list(dict.fromkeys(p for g in self.groups.values() for p in g.pages))
````

with:

````python
        return mapped_pages(self.groups)
````

**Edit 11.** `build/cc_guide/state.py` (in or near `_strings`). Replace:

````python
    return isinstance(value, list) and all(isinstance(v, str) and v for v in value)
````

with:

````python
    return isinstance(value, list) and all(isinstance(v, str) and v for v in value)


def _positive(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0
````

**Edit 12.** `build/cc_guide/state.py` (in or near `parse_manifest`). Replace:

````python
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
    guide_table = _table(raw, 'guide', problems)
    guide_path = None if guide_table is None else guide_table.get('path')
    if guide_table is not None and not (isinstance(guide_path, str) and guide_path):
        problems.append('[guide] path must be a non-empty string')
    sources = _table(raw, 'sources', problems)
    for k in SOURCE_KEYS if sources is not None else ():
        if not (isinstance(sources.get(k), str) and sources[k].startswith('https://')):
            problems.append(f'[sources] {k} must be an https URL')
    cadence = _table(raw, 'cadence', problems)
    for k in CADENCE_KEYS if cadence is not None else ():
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
    for sid, t in (_table(raw, 'sections', problems) or {}).items():
        if sid not in owner:
            problems.append(f'[sections.{sid!r}] is not in any group')
        shaped = isinstance(t, dict) and not set(t) - {'extra_terms', 'exclude_terms'}
        extra, exclude = (t.get('extra_terms', []), t.get('exclude_terms', [])) if shaped else ([], [])
        if not shaped or not _strings(extra) or not _strings(exclude):
            problems.append(f'[sections.{sid!r}] holds only extra_terms and exclude_terms, as lists')
            continue
        terms[sid] = (extra, exclude)
    exclusions: list[tuple[str, str]] = []
    for e in _tables(raw, 'exclusion', problems):
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
    for p in _tables(raw, 'probe', problems):
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
````

with:

````python
def _header(raw: dict, problems: list[str]) -> tuple[str | None, dict[str, str], dict[str, int]]:
    '''[guide], [sources] and [cadence] (R2.2).'''
    guide = _table(raw, 'guide', problems)
    path = None if guide is None else guide.get('path')
    if guide is not None and not (isinstance(path, str) and path):
        problems.append('[guide] path must be a non-empty string')
    sources = _table(raw, 'sources', problems)
    if sources is not None:
        problems += [f'[sources] {k} must be an https URL' for k in SOURCE_KEYS
                     if not (isinstance(sources.get(k), str) and sources[k].startswith('https://'))]
    cadence = _table(raw, 'cadence', problems)
    if cadence is not None:
        problems += [f'[cadence] {k} must be a positive integer' for k in CADENCE_KEYS
                     if not _positive(cadence.get(k))]
    return path, dict(sources or {}), dict(cadence or {})


def _pages(g: dict, where: str, problems: list[str]) -> dict[str, str]:
    '''One group's pages, page -> mark: its `all` pages, then its `terms` pages.'''
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
    return pages


def _groups(raw: dict, problems: list[str]) -> tuple[dict[str, Group], dict[str, str]]:
    '''[groups.<id>] (R2.5): the groups, and each section's one group.'''
    groups: dict[str, Group] = {}
    owner: dict[str, str] = {}
    raw_groups = raw.get('groups')
    if not isinstance(raw_groups, dict) or not raw_groups:
        problems.append('[groups] must hold at least one group')
        return groups, owner
    for gid, g in raw_groups.items():
        where = f'[groups.{gid}]'
        if not GROUP_RE.fullmatch(gid):
            problems.append(f'{where} group IDs are [a-z0-9-]')
        if not isinstance(g, dict) or set(g) - {'sections', *MARKS}:
            problems.append(f'{where} holds only sections, all and terms')
            continue
        secs = g.get('sections')
        if not _strings(secs) or not secs:
            problems.append(f'{where} sections must be a non-empty list of section IDs')
            secs = []
        for sid in secs:
            if not ID_RE.fullmatch(sid):
                problems.append(f'{where} {sid!r} is not a section ID')
            elif sid in owner:
                problems.append(f'{where} {sid} is already in group {owner[sid]}')
            else:
                owner[sid] = gid
        groups[gid] = Group(list(secs), _pages(g, where, problems))
    return groups, owner


def _terms(raw: dict, owner: dict[str, str], problems: list[str]) -> dict[str, tuple[list[str], list[str]]]:
    '''[sections.<id>]: a grouped section's extra and exclude terms (R3.6).'''
    terms: dict[str, tuple[list[str], list[str]]] = {}
    for sid, t in (_table(raw, 'sections', problems) or {}).items():
        if sid not in owner:
            problems.append(f'[sections.{sid!r}] is not in any group')
        shaped = isinstance(t, dict) and not set(t) - {'extra_terms', 'exclude_terms'}
        extra, exclude = (t.get('extra_terms', []), t.get('exclude_terms', [])) if shaped else ([], [])
        if not shaped or not _strings(extra) or not _strings(exclude):
            problems.append(f'[sections.{sid!r}] holds only extra_terms and exclude_terms, as lists')
            continue
        terms[sid] = (extra, exclude)
    return terms


def _exclusions(raw: dict, mapped: list[str], problems: list[str]) -> list[tuple[str, str]]:
    '''[[exclusion]]: page patterns no group may map, each with its reason.'''
    exclusions: list[tuple[str, str]] = []
    for e in _tables(raw, 'exclusion', problems):
        page, reason = e.get('page'), e.get('reason')
        if not (isinstance(page, str) and page and isinstance(reason, str) and reason):
            problems.append('[[exclusion]] needs a page pattern and a reason')
            continue
        exclusions.append((page, reason))
    problems += [f'page {page} is mapped but matches exclusion {pattern!r}'
                 for page in mapped for pattern, _ in exclusions if fnmatch.fnmatchcase(page, pattern)]
    return exclusions


def _probes(raw: dict, owner: dict[str, str], problems: list[str]) -> dict[str, tuple[list[str], list[str]]]:
    '''[[probe]]: each registered probe's sections and files (R10.1).'''
    probes: dict[str, tuple[list[str], list[str]]] = {}
    for p in _tables(raw, 'probe', problems):
        pid, secs, files = p.get('id'), p.get('sections'), p.get('files', [])
        if not (isinstance(pid, str) and pid) or pid in probes:
            problems.append('[[probe]] needs a unique id')
            continue
        if not _strings(secs) or not secs or any(s not in owner for s in secs) or not _strings(files):
            problems.append(f'[[probe]] {pid}: sections must name grouped sections; files is a list')
            continue
        probes[pid] = (secs, files)
    return probes


def parse_manifest(text: str) -> Manifest:
    '''manifest.toml (R2.2), validated. Raises SetupError listing every
    problem, so an invalid manifest exits 2.'''
    try:
        raw = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise SetupError(f'{MANIFEST}: not valid TOML ({exc})') from None
    problems = [f'unknown table or key {k!r}' for k in sorted(set(raw) - set(TABLES))]
    guide_path, sources, cadence = _header(raw, problems)
    groups, owner = _groups(raw, problems)
    terms = _terms(raw, owner, problems)
    exclusions = _exclusions(raw, mapped_pages(groups), problems)
    probes = _probes(raw, owner, problems)
    if problems:
        raise SetupError('\n'.join(f'{MANIFEST}: {p}' for p in problems))
    return Manifest(guide_path, sources, cadence, groups, terms, exclusions, probes)
````

**Edit 13.** `build/cc_guide/state.py` (in or near `parse_baseline`). Replace:

````python
              and isinstance(s['text_hash'], str) and TEXT_HASH_RE.match(s['text_hash']))
````

with:

````python
              and isinstance(s['text_hash'], str) and TEXT_HASH_RE.fullmatch(s['text_hash']))
````

**Edit 14.** `build/cc_guide/state.py` (in or near `parse_baseline`). Replace:

````python
            ok = all(isinstance(keys, dict) and all(HASH_RE.match(k) and isinstance(h, str) and HASH_RE.match(h)
````

with:

````python
            ok = all(isinstance(keys, dict) and all(HASH_RE.fullmatch(k) and isinstance(h, str) and HASH_RE.fullmatch(h)
````

- [x] **Step 4: Run the suite and the lints, and confirm GREEN.**

Run the Step 2 command again. Expected: `206 passed` (+19).

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && uv run --python 3.13 --with pyyaml python build/check_conformance.py; echo "exit=$?"; uv run --python 3.13 python build/cc_guide/cli.py lint; echo "exit=$?"`
Expected: `exit=0` twice.

- [x] **Step 5: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && [ "$(git branch --show-current)" = chore/cc-guide-hardening ] && git add build/cc_guide/state.py build/cc_guide/guide.py build/cc_guide/blocks.py build/cc_guide/cc_fixtures.py build/cc_guide/test_state.py && git commit -m "refactor(cc_guide): one owner per grammar; split parse_manifest; read blobs only

The section-ID, block-hash and text-hash patterns live with the modules
that define them, and state.py fullmatches them, so a trailing newline no
longer passes. parse_manifest's eleven checks split into one helper per
table, and mapped_pages serves both Manifest.pages() and the exclusion
check. Source reads a commit's file with git cat-file blob, so a
directory is no file, and non-UTF-8 bytes are a SetupError. The fixture
git helper reports git's stderr.

Plan 39, Task 7 (deferred items: test coverage and edge cases; style,
DRY and naming).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Bookkeeping (items 49 and 50; T7-m2, T7-m4, T7-m5, T7-m6, T7-m8)

**Files:**
- Modify: `build/cc_guide/baseline.py`, `build/cc_guide/cli.py`, `build/CLAUDE.md`, `build/cc_guide/test_baseline.py` (its `history` helper, in Step 3)
- Test: `build/cc_guide/test_baseline.py`, `build/cc_guide/test_cli.py`

**Interfaces:**
- Produces, in `baseline.py`:
  - `check_forward(state: dict, ids, to: str) -> None` raises `SetupError(f'{to} is older than the checked release of {names}')`. Both `advance` and `audited` call it, so `audited` can no longer move `checked` backwards (T7-m4).
  - `_drop(g: dict, page: str, keys: set[str] | None, group: str) -> str` drops an unmapped page's baselined blocks and returns the note. Dropping all of them, with the page's snapshot, gives `{page}: no longer mapped to {group}; dropped its baselined blocks`. Dropping only the listed keys gives `{page}: no longer mapped to {group}; dropped the listed blocks` (T7-m5).
  - `known` joins its names before the f-string.
- The listed-rebaseline refusal reads `{page}: also changed or gone since the baseline: {refs}; list them too, or rebaseline the whole page` (T7-m8). `cli.py`'s module docstring, its `REBASELINE_HELP` and `build/CLAUDE.md` say "changed or gone" to match. The drift spec's R7 is left alone (Global Constraints).
- `test_baseline.history(ref)` skips only when `git cat-file -e <ref>^{commit}` fails. Any other git failure fails the test with git's stderr (T7-m2).

- [x] **Step 1: Write the failing tests.** Apply these edits in order.

**Edit 1.** `build/cc_guide/test_baseline.py` (in or near `history`). Replace:

````python
    return proc.stdout


def test_r11_derivation_from_the_real_history():
````

with:

````python
    return proc.stdout


def test_history_skips_only_for_a_commit_this_clone_lacks(monkeypatch):
    '''A missing path at a present commit fails rather than hiding as a skip.'''
    with pytest.raises(pytest.skip.Exception):
        history('0' * 40)
    monkeypatch.setattr(baseline, 'OLD_GUIDE_PATH', 'no/such/guide.md')
    with pytest.raises((pytest.skip.Exception, pytest.fail.Exception)) as err:
        history('HEAD')
    assert err.type is pytest.fail.Exception
    assert 'no/such/guide.md' in str(err.value)


def test_r11_derivation_from_the_real_history():
````

**Edit 2.** `build/cc_guide/test_baseline.py` (in or near `test_accept_records_the_hash_and_substantive_also_sets_changed`). Replace:

````python
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
````

with:

````python
def test_accept_records_the_hash_and_substantive_also_sets_changed(docs_dir):
    s = fixture_state(docs_dir)
    edited = guide_text().replace('Alpha uses', 'Alpha now uses')
    editorial = baseline.accept(s, edited, ['alpha.overview'], False, '2.1.902')
    by_id = {x.id: x for x in guide.sections(edited)}
    assert editorial['sections']['alpha.overview']['text_hash'] == guide.text_hash(by_id['alpha.overview'].text)
    assert editorial['sections']['alpha.overview']['changed'] == '2.1.900'
    substantive = baseline.accept(s, edited, ['alpha.overview'], True, '2.1.902')
    assert substantive['sections']['alpha.overview']['changed'] == '2.1.902'
    assert (substantive['sections']['alpha.overview']['text_hash']
            == editorial['sections']['alpha.overview']['text_hash'])
    bumped = baseline.accept(s, edited, ['alpha.overview'], True, '2.1.902', {'alpha.overview': ['2.1.902']})
    assert bumped['sections']['alpha.overview']['changed'] == '2.1.902.1'
    assert s == fixture_state(docs_dir)
````

**Edit 3.** `build/cc_guide/test_baseline.py` (in or near `test_audited_sets_audited_and_checked_for_the_groups_sections`). Replace:

````python
    assert str(err.value) == 'unknown group gamma'


def latest_from(tmp_path, **edits):
````

with:

````python
    assert str(err.value) == 'unknown group gamma'


def test_audited_never_moves_checked_backwards(docs_dir):
    s = baseline.advance(fixture_state(docs_dir), ['alpha.reference'], '2.1.902', {'2.1.902'}, '2026-10-04')
    with pytest.raises(state.SetupError) as err:
        baseline.audited(s, MANIFEST, 'alpha', '2.1.901', '2026-10-05')
    assert str(err.value) == '2.1.901 is older than the checked release of alpha.reference'


def latest_from(tmp_path, **edits):
````

**Edit 4.** `build/cc_guide/test_baseline.py` (in or near `test_a_listed_rebaseline_touches_only_listed_blocks_and_refuses_other_changes`). Replace:

````python
def test_a_listed_rebaseline_touches_only_listed_blocks_and_refuses_other_changes(tmp_path, docs_dir):
    s = fixture_state(docs_dir)
    # `--slow` is a new selected row the run does not list, so it stays out.
    faster = DOCS['tools.md'].replace('Runs fast.', 'Runs faster.') + '| `--slow` | Runs slow. |\n'
    latest = latest_from(tmp_path, **{'tools.md': faster})
    row = 'Tools › Options › `--fast`'
    new, pages, _ = baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', ['tools › ' + row], latest, '2.1.902')
    old_tools, new_tools = s['groups']['alpha']['blocks']['tools'], new['groups']['alpha']['blocks']['tools']
    row_hash, tools = hashed(row, 'Tools')
    assert new_tools[row_hash] != old_tools[row_hash]
    assert new_tools[tools] == old_tools[tools]
    assert list(new_tools) == list(old_tools)
    assert pages == ['tools']
    assert new['groups']['alpha']['snapshot']['tools'] == '2.1.902'
    # An unlisted baselined block that also changed would leave the snapshot
    # pointer naming text that is not baselined (R2.3), so the run refuses.
    latest = latest_from(tmp_path, **{'tools.md': faster.replace('runs alpha jobs', 'runs alpha batches')})
    with pytest.raises(state.SetupError) as err:
        baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', ['tools › ' + row], latest, '2.1.902')
    assert str(err.value) == ('tools: also changed since the baseline: tools › Tools;'
                              ' list them too, or rebaseline the whole page')
````

with:

````python
def test_a_bare_page_ref_rebaselines_that_whole_page_and_refreshes_llms(tmp_path, docs_dir):
    '''A listed run may name a whole page, so its two changed blocks need no
    listing. Like every run it refreshes the llms.txt slugs; unlike a full
    run it keeps a page the group no longer maps.'''
    s = fixture_state(docs_dir)
    s['groups']['alpha']['blocks']['retired'] = {blocks.key_hash('Retired'): '1' * 16}
    tools = DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches').replace('Runs fast.', 'Runs faster.')
    latest = latest_from(tmp_path, **{
        'tools.md': tools,
        'llms.txt': DOCS['llms.txt'] + '- [New](https://code.claude.com/docs/en/new-page.md): New.\n'})
    new, pages, notes = baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', ['tools'], latest, '2.1.902')
    old, alpha = s['groups']['alpha'], new['groups']['alpha']
    assert alpha['blocks']['tools'] == fixture_state(latest)['groups']['alpha']['blocks']['tools']
    assert alpha['blocks']['tools'] != old['blocks']['tools']
    assert (alpha['blocks']['env-vars'], alpha['blocks']['retired']) == (old['blocks']['env-vars'],
                                                                          old['blocks']['retired'])
    assert alpha['snapshot'] == {'tools': '2.1.902', 'env-vars': '2.1.900'}
    assert (pages, notes) == (['tools'], [])
    assert new['llms'] == ['env-vars', 'events', 'new-page', 'plugins/components', 'tools']


@pytest.mark.parametrize('group, refs, fetched, message', [
    ('gamma', [], True, 'unknown group gamma'),
    ('alpha', ['nowhere'], True, 'nowhere is neither mapped to nor baselined in alpha'),
    ('alpha', [], False, '{llms}: no latest fetch; run check first'),
])
def test_rebaseline_refuses_an_unknown_group_or_page_and_a_missing_fetch(tmp_path, docs_dir, group, refs,
                                                                         fetched, message):
    latest = latest_from(tmp_path)
    if not fetched:
        (latest / 'llms.txt').unlink()
    with pytest.raises(state.SetupError) as err:
        baseline.rebaseline(fixture_state(docs_dir), MANIFEST, guide_text(), group, refs, latest, '2.1.902')
    assert str(err.value) == message.format(llms=latest / 'llms.txt')


def test_a_listed_rebaseline_touches_only_listed_blocks_and_refuses_other_changes(tmp_path, docs_dir):
    s = fixture_state(docs_dir)
    # `--slow` is a new selected row the run does not list, so it stays out.
    faster = DOCS['tools.md'].replace('Runs fast.', 'Runs faster.') + '| `--slow` | Runs slow. |\n'
    latest = latest_from(tmp_path, **{'tools.md': faster})
    row = 'Tools › Options › `--fast`'
    new, pages, _ = baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', ['tools › ' + row], latest, '2.1.902')
    old_tools, new_tools = s['groups']['alpha']['blocks']['tools'], new['groups']['alpha']['blocks']['tools']
    row_hash, tools = hashed(row, 'Tools')
    assert new_tools[row_hash] != old_tools[row_hash]
    assert new_tools[tools] == old_tools[tools]
    assert list(new_tools) == list(old_tools)
    assert pages == ['tools']
    assert new['groups']['alpha']['snapshot']['tools'] == '2.1.902'
    # An unlisted baselined block that also changed would leave the snapshot
    # pointer naming text that is not baselined (R2.3), so the run refuses.
    latest = latest_from(tmp_path, **{'tools.md': faster.replace('runs alpha jobs', 'runs alpha batches')})
    with pytest.raises(state.SetupError) as err:
        baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', ['tools › ' + row], latest, '2.1.902')
    assert str(err.value) == ('tools: also changed or gone since the baseline: tools › Tools;'
                              ' list them too, or rebaseline the whole page')
````

**Edit 5.** `build/cc_guide/test_baseline.py` (in or near `test_a_listed_rebaseline_takes_checks_refs_for_blocks_gone_from_the_page`). Replace:

````python
        assert str(err.value) == (f'tools: also changed since the baseline: tools › {name};'
````

with:

````python
        assert str(err.value) == (f'tools: also changed or gone since the baseline: tools › {name};'
````

**Edit 6.** `build/cc_guide/test_baseline.py` (in or near `test_rebaseline_keeps_a_missing_page_and_drops_an_unmapped_one`). Replace:

````python
                     'retired: no longer mapped to beta; dropped its baselined blocks']


def test_stamp_regenerates_only_the_region(docs_dir):
````

with:

````python
                     'retired: no longer mapped to beta; dropped its baselined blocks']


def test_a_listed_ref_to_an_unmapped_page_drops_the_page_or_only_its_listed_blocks(tmp_path, docs_dir):
    s = fixture_state(docs_dir)
    retired, kept = hashed('Retired', 'Retired › Kept')
    s['groups']['beta']['blocks']['retired'] = {retired: '1' * 16, kept: '2' * 16}
    s['groups']['beta']['snapshot']['retired'] = '2.1.900'
    latest = latest_from(tmp_path)
    new, pages, notes = baseline.rebaseline(s, MANIFEST, guide_text(), 'beta', ['retired › Retired'], latest,
                                            '2.1.902')
    assert new['groups']['beta']['blocks']['retired'] == {kept: '2' * 16}
    assert new['groups']['beta']['snapshot']['retired'] == '2.1.900'
    assert (pages, notes) == ([], ['retired: no longer mapped to beta; dropped the listed blocks'])
    new, pages, notes = baseline.rebaseline(s, MANIFEST, guide_text(), 'beta', ['retired'], latest, '2.1.902')
    assert ('retired' in new['groups']['beta']['blocks'], 'retired' in new['groups']['beta']['snapshot']) == (
        False, False)
    assert (pages, notes) == ([], ['retired: no longer mapped to beta; dropped its baselined blocks'])


def test_stamp_regenerates_only_the_region(docs_dir):
````

**Edit 7.** `build/cc_guide/test_cli.py` (in or near `test_help_shows_the_module_docstring_and_the_rebaseline_refusal`). Replace:

````python
        assert 'unlisted baselined block' in out
````

with:

````python
        assert 'unlisted baselined block' in out
        assert 'also changed or gone' in out
````

**Edit 8.** `build/cc_guide/test_cli.py` (in or near `test_rebaseline_names_a_gone_block_from_the_cached_snapshot`). Replace:

````python
def test_rebaseline_names_a_gone_block_from_the_cached_snapshot(world, capsys):
    repo, cache, _ = world
    write_tree(state.snapshot_docs(cache, '2.1.900'), {'tools.md': DOCS['tools.md']})
    write_tree(state.latest_docs(cache), {'tools.md': DOCS['tools.md'].replace('## Options', '## Flags')})
    assert main(cache, 'baseline', 'rebaseline', 'alpha', 'tools › Tools › Options › `--fast`') == 2
    assert capsys.readouterr() == ('', 'cc-guide: tools: also changed since the baseline: tools › Tools › Options;'
                                       ' list them too, or rebaseline the whole page\n')
    assert dirty(repo) == []
````

with:

````python
def test_rebaseline_names_a_gone_block_from_the_cached_snapshot(world, capsys):
    repo, cache, _ = world
    write_tree(state.snapshot_docs(cache, '2.1.900'), {'tools.md': DOCS['tools.md']})
    write_tree(state.latest_docs(cache), {'tools.md': DOCS['tools.md'].replace('## Options', '## Flags')})
    assert main(cache, 'baseline', 'rebaseline', 'alpha', 'tools › Tools › Options › `--fast`') == 2
    assert capsys.readouterr() == ('', 'cc-guide: tools: also changed or gone since the baseline:'
                                       ' tools › Tools › Options; list them too, or rebaseline the whole page\n')
    assert dirty(repo) == []
````

- [x] **Step 2: Run the suite and confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf`
Expected: `7 failed, 206 passed`. The fixes:
- `test_baseline.py::test_history_skips_only_for_a_commit_this_clone_lacks`: `assert <class 'Skipped'> is <class 'Failed'>`.
- `test_baseline.py::test_audited_never_moves_checked_backwards`: `DID NOT RAISE SetupError`.
- `test_baseline.py::test_a_listed_rebaseline_touches_only_listed_blocks_and_refuses_other_changes`, `test_baseline.py::test_a_listed_rebaseline_takes_checks_refs_for_blocks_gone_from_the_page` and `test_cli.py::test_rebaseline_names_a_gone_block_from_the_cached_snapshot`: the refusal still says `also changed since the baseline`.
- `test_baseline.py::test_a_listed_ref_to_an_unmapped_page_drops_the_page_or_only_its_listed_blocks`: the note says `dropped its baselined blocks` for a listed key.
- `test_cli.py::test_help_shows_the_module_docstring_and_the_rebaseline_refusal`: `'also changed or gone'` is not in the help.

The pins, which pass now: `test_a_bare_page_ref_rebaselines_that_whole_page_and_refreshes_llms`, the three cases of `test_rebaseline_refuses_an_unknown_group_or_page_and_a_missing_fetch`, and the new substantive `text_hash` assertion in `test_accept_records_the_hash_and_substantive_also_sets_changed`.

- [x] **Step 3: Implement.** Apply these edits in order. The last one rewrites `test_baseline.history`, the fix for T7-m2.

**Edit 1.** `build/CLAUDE.md`. Replace:

````markdown
baselined block on the same page has also changed: list it too, or
````

with:

````markdown
baselined block on the same page has also changed or gone: list it too, or
````

**Edit 2.** `build/cc_guide/baseline.py` (in or near `known`). Replace:

````python
def known(state: dict, ids) -> None:
    unknown = [sid for sid in ids if sid not in state['sections']]
    if unknown:
        raise SetupError(f'unknown section IDs: {", ".join(unknown)}')
````

with:

````python
def known(state: dict, ids) -> None:
    unknown = [sid for sid in ids if sid not in state['sections']]
    if unknown:
        names = ', '.join(unknown)
        raise SetupError(f'unknown section IDs: {names}')


def check_forward(state: dict, ids, to: str) -> None:
    '''advance and audited never move a section's `checked` backwards.'''
    behind = [sid for sid in ids if version_key(to) < version_key(state['sections'][sid]['checked']['release'])]
    if behind:
        names = ', '.join(behind)
        raise SetupError(f'{to} is older than the checked release of {names}')
````

**Edit 3.** `build/cc_guide/baseline.py` (in or near `advance`). Replace:

````python
    behind = [sid for sid in ids if version_key(to) < version_key(state['sections'][sid]['checked']['release'])]
    if behind:
        raise SetupError(f'{to} is older than the checked release of {", ".join(behind)}')
````

with:

````python
    check_forward(state, ids, to)
````

**Edit 4.** `build/cc_guide/baseline.py` (in or near `audited`). Replace:

````python
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
````

with:

````python
def audited(state: dict, manifest: Manifest, group: str, release: str, day: str) -> dict:
    '''R7 audited: set `audited` for the group's sections to the current
    release and day, and advance their `checked` to it, never backwards.'''
    if group not in manifest.groups:
        raise SetupError(f'unknown group {group}')
    ids = manifest.groups[group].sections
    known(state, ids)
    check_forward(state, ids, release)
    new = copy.deepcopy(state)
    for sid in ids:
        new['sections'][sid]['audited'] = {'release': release, 'date': day}
        new['sections'][sid]['checked'] = {'release': release, 'date': day}
    return new


def _drop(g: dict, page: str, keys: set[str] | None, group: str) -> str:
    '''Drop baselined blocks of a page the group no longer maps: all of them
    with the page's snapshot, or only the listed keys. Returns the note.'''
    if keys is None:
        g['blocks'].pop(page)
        g['snapshot'].pop(page, None)
        return f'{page}: no longer mapped to {group}; dropped its baselined blocks'
    for key in keys:
        g['blocks'][page].pop(key, None)
    return f'{page}: no longer mapped to {group}; dropped the listed blocks'
````

**Edit 5.** `build/cc_guide/baseline.py` (in or near `rebaseline`). Replace:

````python
    unlisted baselined block on the page changed too, since the page's
    snapshot would then not hold its baselined text; the refusal names a gone
    block from `snapshot`, as check does. Returns the new state, the pages to
````

with:

````python
    unlisted baselined block on the page also changed or is gone, since the
    page's snapshot would then not hold its baselined text; the refusal names
    a gone block from `snapshot`, as check does. Returns the new state, the pages to
````

**Edit 6.** `build/cc_guide/baseline.py` (in or near `rebaseline`). Replace:

````python
            if keys is None:
                g['blocks'].pop(page)
                g['snapshot'].pop(page, None)
            else:
                for key in keys:
                    g['blocks'][page].pop(key, None)
            notes.append(f'{page}: no longer mapped to {group}; dropped its baselined blocks')
````

with:

````python
            notes.append(_drop(g, page, keys, group))
````

**Edit 7.** `build/cc_guide/baseline.py` (in or near `rebaseline`). Replace:

````python
                raise SetupError(f'{page}: also changed since the baseline: {listed};'
````

with:

````python
                raise SetupError(f'{page}: also changed or gone since the baseline: {listed};'
````

**Edit 8.** `build/cc_guide/baseline.py` (in or near `rebaseline`). Replace:

````python
            g['blocks'].pop(page)
            g['snapshot'].pop(page, None)
            notes.append(f'{page}: no longer mapped to {group}; dropped its baselined blocks')
````

with:

````python
            notes.append(_drop(g, page, None, group))
````

**Edit 9.** `build/cc_guide/cli.py`. Replace:

````python
      same page has also changed, since the page's snapshot would not hold
      that block's baselined text: list it too, or rebaseline the whole
      page. It also refuses to overwrite a snapshot page that holds other
      text.
````

with:

````python
      same page has also changed or gone, since the page's snapshot would
      not hold that block's baselined text: list it too, or rebaseline the
      whole page. It also refuses to overwrite a snapshot page that holds
      other text.
````

**Edit 10.** `build/cc_guide/cli.py` (in or near `REBASELINE_HELP`). Replace:

````python
also changed since the baseline: list it too, or rebaseline the whole page.
It also refuses to overwrite a snapshot page that holds different text.'''
````

with:

````python
also changed or gone since the baseline: list it too, or rebaseline the whole
page. It also refuses to overwrite a snapshot page that holds different text.'''
````

**Edit 11.** `build/cc_guide/test_baseline.py` (in or near `history`). Replace:

````python
def history(ref):
    proc = subprocess.run(['git', 'show', f'{ref}:{baseline.OLD_GUIDE_PATH}'], cwd=REPO,
                          capture_output=True, encoding='utf-8')
    if proc.returncode != 0:
        pytest.skip(f'{ref} is not in this clone (a shallow clone?)')
    return proc.stdout
````

with:

````python
def history(ref):
    '''The guide at ref, read where it lived before 79ad04f moved it. A clone
    without ref (a shallow one) skips; any other git failure fails.'''
    present = subprocess.run(['git', 'cat-file', '-e', f'{ref}^{{commit}}'], cwd=REPO, capture_output=True)
    if present.returncode != 0:
        pytest.skip(f'{ref} is not in this clone (a shallow clone?)')
    proc = subprocess.run(['git', 'show', f'{ref}:{baseline.OLD_GUIDE_PATH}'], cwd=REPO,
                          capture_output=True, encoding='utf-8')
    if proc.returncode != 0:
        pytest.fail(f'git show {ref}:{baseline.OLD_GUIDE_PATH} failed: {proc.stderr.strip()}')
    return proc.stdout
````

- [x] **Step 4: Run the suite and the lints, and confirm GREEN.**

Run the Step 2 command again. Expected: `213 passed` (+7).

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && uv run --python 3.13 --with pyyaml python build/check_conformance.py; echo "exit=$?"; uv run --python 3.13 --with pyyaml python build/check_frontmatter.py; echo "exit=$?"`
Expected: `exit=0` twice. `build/CLAUDE.md` changed.

- [x] **Step 5: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && [ "$(git branch --show-current)" = chore/cc-guide-hardening ] && git add build/cc_guide/baseline.py build/cc_guide/cli.py build/CLAUDE.md build/cc_guide/test_baseline.py build/cc_guide/test_cli.py && git commit -m "fix(cc_guide): audited never moves checked back; name gone blocks in the refusal

audited now shares advance's guard (check_forward), so it cannot move a
section's checked release backwards. A listed rebaseline's refusal says
changed or gone, since an unlisted block that vanished refuses it too,
and the help and build/CLAUDE.md say the same. One _drop helper handles
an unmapped page, and a listed key gets its own note. history() skips
only for a commit the clone lacks. Rebaseline's bare page ref, its llms
refresh and its three refusals are pinned.

Plan 39, Task 8 (deferred items: test coverage and edge cases; style,
DRY and naming).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: The check (items 49 and 50; T9-m2, T9-m4, T9-m5, T9-m6, T9-m9, T10-m7)

**Files:**
- Modify: `build/cc_guide/check.py`
- Test: `build/cc_guide/test_check.py`

**Interfaces:**
- Produces, in `check.py`: `ATTEMPTS = 2` and `HTTP_OK, HTTP_NOT_FOUND = 200, 404`, used in `http_get` and `live_docs` (T9-m6, ruling 2).
- `releases_of(changelog_text: str, where: str = 'changelog')`: the parameter is renamed from `source`, which shadowed `state.Source` (T10-m7). `cli.py` passes it positionally, so no caller changes.
- An `llms.txt` that lists no code page raises `SetupError(f'{folder}/llms.txt: lists no code pages')` from `offline_docs`, and `FetchError(f'{url}: lists no code pages')` from `live_docs` before the cache changes (T9-m2).
- `summary` prints each finding's ref with `Finding(**f).ref()`, so an empty key from a bare `#` heading prints as a block, `page › ` (T9-m4).
- `test_check.py` builds the guide's path from `cc_fixtures.GUIDE_PATH` (T9-m6), and its fake `serving` takes `codes={url: status}`.

- [x] **Step 1: Write the failing tests.** Apply these edits in order.

**Edit 1.** `build/cc_guide/test_check.py`. Replace:

````python
from cc_fixtures import (DOCS, ENV_PAGE, MANIFEST_TOML, docs_dir, drift_repo,  # noqa: F401
````

with:

````python
from cc_fixtures import (DOCS, ENV_PAGE, GUIDE_PATH, MANIFEST_TOML, docs_dir, drift_repo,  # noqa: F401
````

**Edit 2.** `build/cc_guide/test_check.py` (in or near `test_deselection_is_informational_only_while_the_block_is_unchanged`). Replace:

````python
    assert findings(docs_dir, s)[0] == [('beta', 'missing', f'env-vars › {ENV} › `BETA_ENV`', ['beta.overview'])]
````

with:

````python
    assert findings(docs_dir, s)[0] == [('beta', 'missing', f'env-vars › {ENV} › `BETA_ENV`', ['beta.overview'])]


def test_a_baselined_page_its_group_no_longer_maps_is_deselected(docs_dir):
    '''Until a full rebaseline drops it, the page's blocks are informational,
    named from its snapshot.'''
    s = fixture_state(docs_dir)
    s['groups']['beta']['blocks']['tools'] = s['groups']['alpha']['blocks']['tools']
    s['groups']['beta']['snapshot']['tools'] = '2.1.900'
    assert findings(docs_dir, s) == ([], {'alpha': [], 'beta': [
        'tools › Tools', 'tools › Tools › Options', 'tools › Tools › Options › `--fast`']})
````

**Edit 3.** `build/cc_guide/test_check.py` (in or near `test_http_get_retries_once_and_reports_any_other_failure`). Replace:

````python
    assert sent == [(url, 'agent-skills-cc-guide/1 (Claude Code docs drift check)', 30)] * 5


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
````

with:

````python
    outcomes[:] = [http.client.IncompleteRead(b''), urllib.error.HTTPError(url, 500, 'Server Error', {}, None)]
    with pytest.raises(check.FetchError) as err:
        check.http_get(url)
    assert str(err.value) == f'{url}: HTTP 500'
    assert sent == [(url, 'agent-skills-cc-guide/1 (Claude Code docs drift check)', 30)] * 7


def serving(folder, log=None, fail=(), codes=None):
    '''A fake fetch serving folder's files by URL; unknown URLs are 404, and
    a URL in `codes` answers with its status and no body.'''
    def fetch(url):
        if log is not None:
            log.append(url)
        if url in fail:
            raise check.FetchError(f'{url}: timed out')
        if codes and url in codes:
            return codes[url], b''
        path = folder / URLS.get(url, 'absent')
        return (200, path.read_bytes()) if path.is_file() else (404, b'')
    return fetch
````

**Edit 4.** `build/cc_guide/test_check.py` (in or near `test_docs_read_as_other_than_utf8_are_a_setup_error_or_a_fetch_error`). Replace:

````python
    assert str(err.value) == f"{MANIFEST.sources['changelog']}: not UTF-8 text"


def test_a_404_removes_the_stale_copy_and_reads_as_a_missing_page(tmp_path, docs_dir):
````

with:

````python
    assert str(err.value) == f"{MANIFEST.sources['changelog']}: not UTF-8 text"


def test_an_answer_other_than_200_or_404_is_an_http_error(tmp_path, docs_dir):
    '''A page so answered is left unread and uncached; the changelog so
    answered fails the fetch.'''
    cache, url = tmp_path / 'cache', docs.page_url('tools', MANIFEST.sources)
    got = check.live_docs(MANIFEST, cache, serving(docs_dir, codes={url: 500}), NOW)
    assert (got.errors, got.unread) == ([f'{url}: HTTP 500'], {'tools'})
    assert not (state.latest_docs(cache) / 'tools.md').exists()
    changelog = MANIFEST.sources['changelog']
    with pytest.raises(check.FetchError) as err:
        check.live_docs(MANIFEST, cache, serving(docs_dir, codes={changelog: 503}), NOW)
    assert str(err.value) == f'{changelog}: HTTP 503'


def test_an_llms_txt_listing_no_code_page_is_an_error_not_every_page_missing(tmp_path, docs_dir):
    '''A local copy is a setup error. A fetched one is a fetch error, which
    leaves the cache as it was.'''
    write_tree(docs_dir, {'llms.txt': '# Fixture docs\n'})
    with pytest.raises(state.SetupError) as err:
        offline(docs_dir)
    assert str(err.value) == f"{docs_dir / 'llms.txt'}: lists no code pages"
    cache = tmp_path / 'cache'
    with pytest.raises(check.FetchError) as err:
        check.live_docs(MANIFEST, cache, serving(docs_dir), NOW)
    assert str(err.value) == f"{MANIFEST.sources['llms']}: lists no code pages"
    assert not state.fetch_record(cache).exists()


def test_a_404_removes_the_stale_copy_and_reads_as_a_missing_page(tmp_path, docs_dir):
````

**Edit 5.** `build/cc_guide/test_check.py` (in or near `test_a_changed_block_or_a_lint_failure_is_due_at_once`). Replace:

````python
def test_a_changed_block_or_a_lint_failure_is_due_at_once(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    write_tree(docs_dir, {'events.md': DOCS['events.md'].replace('fires on beta', 'fires on gamma')})
    assert run_check(repo, tmp_path / 'cache', docs_dir)[0] == 1
    write_tree(docs_dir, DOCS)
    guide = repo / 'specs/guides/claude-code-customization-guide.md'
    guide.write_text(guide.read_text().replace('Alpha uses', 'Alpha now uses'))
    code, report, _ = run_check(repo, tmp_path / 'cache', docs_dir)
    assert (code, report['due']['lint']) == (1, 1)
````

with:

````python
def test_a_changed_block_or_a_lint_failure_is_due_at_once(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    write_tree(docs_dir, {'events.md': DOCS['events.md'].replace('fires on beta', 'fires on gamma')})
    assert run_check(repo, tmp_path / 'cache', docs_dir)[0] == 1
    write_tree(docs_dir, DOCS)
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace('Alpha uses', 'Alpha now uses'))
    code, report, _ = run_check(repo, tmp_path / 'cache', docs_dir)
    assert (code, report['due']['lint']) == (1, 1)
````

**Edit 6.** `build/cc_guide/test_check.py` (in or near `test_llms_slugs_added_and_removed_since_the_baseline_are_listed`). Replace:

````python
    assert report['llms'] == {'added': ['plugins/parts'], 'removed': ['plugins/components']}
````

with:

````python
    assert report['llms'] == {'added': ['plugins/parts'], 'removed': ['plugins/components']}


def test_the_summary_prints_a_block_keyed_by_a_bare_heading_as_a_block(tmp_path, docs_dir):
    '''A bare `#` heading keys its block with the empty string, which still
    names a block of the page, not the page.'''
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    write_tree(docs_dir, {'events.md': DOCS['events.md'] + '#\n\nA bare heading.\n'})
    _, report, path = run_check(repo, tmp_path / 'cache', docs_dir)
    assert '  [beta] new events ›  (candidates: beta.overview, beta.reference)' in check.summary(report, path)
````

- [x] **Step 2: Run the suite and confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf`
Expected: `2 failed, 215 passed`. The fixes:
- `test_check.py::test_an_llms_txt_listing_no_code_page_is_an_error_not_every_page_missing`: `DID NOT RAISE SetupError`.
- `test_check.py::test_the_summary_prints_a_block_keyed_by_a_bare_heading_as_a_block`: the summary prints `  [beta] new events (candidates: …)`, the page.

The pins, which pass now: `test_a_baselined_page_its_group_no_longer_maps_is_deselected` (T9-m5), `test_an_answer_other_than_200_or_404_is_an_http_error` and the new `HTTP 500` case in `test_http_get_retries_once_and_reports_any_other_failure` (T9-m9).

- [x] **Step 3: Implement.** Apply these edits in order. The constants and the rename are refactors under green.

**Edit 1.** `build/cc_guide/check.py` (in or near `TIMEOUT`). Replace:

````python
TIMEOUT = 30
````

with:

````python
TIMEOUT = 30
ATTEMPTS = 2  # R6.4: one retry
HTTP_OK, HTTP_NOT_FOUND = 200, 404
````

**Edit 2.** `build/cc_guide/check.py` (in or near `http_get`). Replace:

````python
    for _ in range(2):
````

with:

````python
    for _ in range(ATTEMPTS):
````

**Edit 3.** `build/cc_guide/check.py` (in or near `http_get`). Replace:

````python
            if exc.code == 404:
                return 404, b''
````

with:

````python
            if exc.code == HTTP_NOT_FOUND:
                return HTTP_NOT_FOUND, b''
````

**Edit 4.** `build/cc_guide/check.py` (in or near `releases_of`). Replace:

````python
def releases_of(changelog_text: str, source: str = 'changelog') -> list[Release]:
    '''The changelog's releases, newest first. A changelog that does not
    parse, or holds no release, is a SetupError naming its source.'''
    try:
        releases = parse_changelog(changelog_text)
    except ValueError as exc:
        raise SetupError(f'{source}: {exc}') from None
    if not releases:
        raise SetupError(f'{source}: no <Update> release blocks')
    return releases


def offline_docs(manifest: Manifest, folder: Path) -> Docs:
    '''R6.1 --docs: the docs read from a local directory, named as the cache
    names them. A page file that is absent is a missing page.'''
    def read(name: str) -> str | None:
        path = folder / name
        return read_utf8(path) if path.is_file() else None
    changelog, llms = read(CHANGELOG), read(LLMS)
    if changelog is None or llms is None:
        raise SetupError(f'{folder}: needs {CHANGELOG} and {LLMS}')
    return Docs(changelog, llms, {p: read(page_file(p)) for p in manifest.pages()},
                str(folder), [], set())
````

with:

````python
def releases_of(changelog_text: str, where: str = 'changelog') -> list[Release]:
    '''The changelog's releases, newest first. A changelog that does not
    parse, or holds no release, is a SetupError naming where it was read.'''
    try:
        releases = parse_changelog(changelog_text)
    except ValueError as exc:
        raise SetupError(f'{where}: {exc}') from None
    if not releases:
        raise SetupError(f'{where}: no <Update> release blocks')
    return releases


def offline_docs(manifest: Manifest, folder: Path) -> Docs:
    '''R6.1 --docs: the docs read from a local directory, named as the cache
    names them. A page file that is absent is a missing page; an llms.txt
    that lists no code page is a SetupError, since every code page would
    read as missing.'''
    def read(name: str) -> str | None:
        path = folder / name
        return read_utf8(path) if path.is_file() else None
    changelog, llms = read(CHANGELOG), read(LLMS)
    if changelog is None or llms is None:
        raise SetupError(f'{folder}: needs {CHANGELOG} and {LLMS}')
    if not parse_llms(llms):
        raise SetupError(f'{folder / LLMS}: lists no code pages')
    return Docs(changelog, llms, {p: read(page_file(p)) for p in manifest.pages()},
                str(folder), [], set())
````

**Edit 5.** `build/cc_guide/check.py` (in or near `live_docs`). Replace:

````python
    recorded head would otherwise vouch for it later.'''
````

with:

````python
    recorded head would otherwise vouch for it later. An llms.txt that lists
    no code page is a FetchError, raised before the cache changes.'''
````

**Edit 6.** `build/cc_guide/check.py` (in or near `live_docs`). Replace:

````python
        if status != 200:
````

with:

````python
        if status != HTTP_OK:
````

**Edit 7.** `build/cc_guide/check.py` (in or near `live_docs`). Replace:

````python
        fetched[name] = text
````

with:

````python
        fetched[name] = text
    if not parse_llms(fetched[LLMS]):
        raise FetchError(f"{manifest.sources['llms']}: lists no code pages")
````

**Edit 8.** `build/cc_guide/check.py` (in or near `live_docs`). Replace:

````python
        if error is None and got[0] not in (200, 404):
            error = f'{page_url(page, manifest.sources)}: HTTP {got[0]}'
        if error is None and got[0] == 200 and utf8(got[1]) is None:
````

with:

````python
        if error is None and got[0] not in (HTTP_OK, HTTP_NOT_FOUND):
            error = f'{page_url(page, manifest.sources)}: HTTP {got[0]}'
        if error is None and got[0] == HTTP_OK and utf8(got[1]) is None:
````

**Edit 9.** `build/cc_guide/check.py` (in or near `live_docs`). Replace:

````python
        elif got[0] == 404:
````

with:

````python
        elif got[0] == HTTP_NOT_FOUND:
````

**Edit 10.** `build/cc_guide/check.py` (in or near `summary`). Replace:

````python
        lines += [f"  [{f['group']}] {f['kind']} {f['page'] + (SEP + f['key'] if f['key'] else '')}"
````

with:

````python
        lines += [f"  [{f['group']}] {f['kind']} {Finding(**f).ref()}"
````

- [x] **Step 4: Run the suite and confirm GREEN.**

Run the Step 2 command again. Expected: `217 passed` (+4).

- [x] **Step 5: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && [ "$(git branch --show-current)" = chore/cc-guide-hardening ] && git add build/cc_guide/check.py build/cc_guide/test_check.py && git commit -m "fix(cc_guide): refuse an llms.txt with no code pages; print empty keys as blocks

An llms.txt listing no code page would flag every code page missing; it
is now a setup error offline and a fetch error live, raised before the
cache changes. summary() prints a ref as Finding.ref() does, so a bare #
heading's empty key is a block, not the page. The HTTP codes and the
retry count are named, releases_of's parameter no longer shadows
state.Source, and the dropped-page and HTTP error branches are pinned.

Plan 39, Task 9 (deferred items: test coverage and edge cases; style,
DRY and naming).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 10: The command line's refusals and output (item 49; T10-m5, T10-m8)

**Files:**
- Test: `build/cc_guide/test_cli.py`

**Interfaces:**
- Produces a test helper, `history_repo(tmp_path, monkeypatch)`: a fixture repo holding R11.1's two old guides, then the anchored guide and its manifest but no baseline, with `cli.REPO`, `baseline.JULY` and `baseline.REFRESH` pointed at it. Both `init` tests use it.
- No module changes: every test this task touches is a pin.

- [x] **Step 1: Write the tests.** Apply these edits in order:
  - The help test captures each command's help once (T10-m8).
  - The init test pins its success line and its `--force` refusal, and a new test pins the missing bootstrap snapshot.
  - The advance test, renamed, pins its stdout and the stale-stamp message.
  - The audited test compares full `(out, err)` pairs (T10-m5).
  - A new test pins rebaseline's refusal without a fetch.

**Edit 1.** `build/cc_guide/test_cli.py` (in or near `test_help_shows_the_module_docstring_and_the_rebaseline_refusal`). Replace:

````python
def test_help_shows_the_module_docstring_and_the_rebaseline_refusal(capsys):
    for argv in (['--help'], ['baseline', 'rebaseline', '--help']):
        with pytest.raises(SystemExit) as stop:
            cli.main(argv)
        assert stop.value.code == 0
        out = ' '.join(capsys.readouterr().out.split())
        assert 'unlisted baselined block' in out
        assert 'also changed or gone' in out
        assert 'the whole page' in out
    with pytest.raises(SystemExit):
        cli.main(['--help'])
    out = capsys.readouterr().out
    assert '  lint [--ref REF]\n' in out  # the docstring's line breaks survive
    assert 'Offline gate over the guide, manifest.toml and baseline.json (R5)' in out
````

with:

````python
def test_help_shows_the_module_docstring_and_the_rebaseline_refusal(capsys):
    outs = []
    for argv in (['--help'], ['baseline', 'rebaseline', '--help']):
        with pytest.raises(SystemExit) as stop:
            cli.main(argv)
        assert stop.value.code == 0
        outs.append(capsys.readouterr().out)
    for out in (' '.join(o.split()) for o in outs):
        assert 'unlisted baselined block' in out
        assert 'also changed or gone' in out
        assert 'the whole page' in out
    assert '  lint [--ref REF]\n' in outs[0]  # the docstring's line breaks survive
    assert 'Offline gate over the guide, manifest.toml and baseline.json (R5)' in outs[0]
````

**Edit 2.** `build/cc_guide/test_cli.py` (in or near `test_init_derives_changed_and_refuses_to_overwrite_without_force`). Replace:

````python
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
````

with:

````python
def history_repo(tmp_path, monkeypatch):
    '''A repo holding R11.1's two old guides, then the anchored guide and its
    manifest but no baseline, with cli and baseline pointed at it.'''
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
    return repo


def test_init_derives_changed_and_refuses_to_overwrite_without_force(tmp_path, docs_dir, monkeypatch, capsys):
    repo = history_repo(tmp_path, monkeypatch)
    cache = tmp_path / 'cache'
    argv = ('baseline', 'init', '--docs', str(docs_dir), '--release', '2.1.900', '--date', '2026-09-02')
    assert main(cache, *argv) == 0
    assert capsys.readouterr() == (f'wrote {state.BASELINE} from {docs_dir}; next: baseline stamp\n', '')
    assert dirty(repo) == [state.BASELINE]
    written = load(repo)
    assert {i: s['changed'] for i, s in written['sections'].items()} == {
        'alpha.overview': '2.1.219', 'alpha.reference': '2.1.288',
        'beta.overview': '2.1.219', 'beta.reference': '2.1.219'}
    assert main(cache, *argv) == 2
    assert capsys.readouterr() == ('', f'cc-guide: {state.BASELINE} exists; init rebuilds it from scratch'
                                       ' only with --force\n')
    assert main(cache, *argv, '--force') == 0


def test_init_without_docs_needs_the_bootstrap_snapshot_directory(tmp_path, monkeypatch, capsys):
    repo = history_repo(tmp_path, monkeypatch)
    cache = tmp_path / 'cache'
    assert main(cache, 'baseline', 'init') == 2
    assert capsys.readouterr() == ('', f"cc-guide: {state.snapshot_docs(cache, '2.1.288')}: no snapshot directory\n")
    assert dirty(repo) == []
````

**Edit 3.** `build/cc_guide/test_cli.py` (in or near `test_advance_writes_only_the_named_sections_checked`). Replace:

````python
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
````

with:

````python
def test_advance_writes_only_the_named_sections_checked_and_says_when_the_stamp_is_stale(world, capsys):
    repo, cache, _ = world
    before = load(repo)
    assert main(cache, 'baseline', 'advance', 'beta.overview', '--to', '2.1.902') == 0
    assert dirty(repo) == [state.BASELINE]
    assert changed_fields(before, load(repo)) == {'sections.beta.overview.checked'}
    assert capsys.readouterr() == (f'updated {state.BASELINE}\n', '')  # the oldest checked is unchanged
    assert main(cache, 'baseline', 'advance', *GUIDE_IDS, '--to', '2.1.902') == 0
    assert capsys.readouterr() == (f'updated {state.BASELINE}\n',
                                   'the stamp region is now stale: run baseline stamp\n')


def test_audited_writes_only_the_groups_audited_and_checked(world, capsys):
    repo, cache, _ = world
    before = load(repo)
    assert main(cache, 'baseline', 'audited', 'alpha', today=date(2026, 10, 4)) == 0
    assert dirty(repo) == [state.BASELINE]
    assert changed_fields(before, load(repo)) == {
        'sections.alpha.overview.audited', 'sections.alpha.overview.checked',
        'sections.alpha.reference.audited', 'sections.alpha.reference.checked'}
    assert capsys.readouterr() == (f'updated {state.BASELINE}\n', '')  # beta's sections still hold the oldest dates
    assert main(cache, 'baseline', 'audited', 'beta', today=date(2026, 10, 4)) == 0
    assert capsys.readouterr() == (f'updated {state.BASELINE}\n',
                                   'the stamp region is now stale: run baseline stamp\n')
````

**Edit 4.** `build/cc_guide/test_cli.py` (in or near `test_stamp_writes_only_the_guides_stamp_region`). Replace:

````python
                    'oldest full re-verification 2026-09-02, at 2.1.900.']
````

with:

````python
                    'oldest full re-verification 2026-09-02, at 2.1.900.']


def test_rebaseline_without_a_fetch_is_one_error_line(world, tmp_path, capsys):
    repo, _, _ = world
    assert main(tmp_path / 'empty-cache', 'baseline', 'rebaseline', 'alpha') == 2
    assert capsys.readouterr() == ('', 'cc-guide: no latest fetch: run check first\n')
    assert dirty(repo) == []
````

- [x] **Step 2: Run the suite.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q -rf`
Expected: `219 passed` (+2: three tests added, one renamed away). All are pins. Any failure is a plan defect.

- [x] **Step 3: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && [ "$(git branch --show-current)" = chore/cc-guide-hardening ] && git add build/cc_guide/test_cli.py && git commit -m "test(cc_guide): pin the CLI's refusals and its full output

The help capture runs once per command; init's success line and its
--force refusal are pinned, as are the missing bootstrap snapshot,
rebaseline without a fetch and advance's stale-stamp message; and the
audited test compares stdout and stderr together.

Plan 39, Task 10 (deferred item: test coverage and edge cases).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 11: Verification

**Controller task.** It runs every gate. Nothing is committed unless a fix is needed.

- [x] **Step 1: The suites.**
> Deviation: the final counts are 221 passed in `build/cc_guide` and 760 in `build`, which is +72 rather than +70. The final review's fix wave added `test_an_empty_key_ref_rebaselines_that_block_not_its_page` (acf3858, 6b844df), and the completion gate's `LABEL_RE` fix added one `version_key` case (73ed2de).

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build/cc_guide && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: the baseline's count +70 (`219 passed` from 149).

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q -rf`
Expected: the failures are exactly the four named in Global Constraints ("Baseline and counts"), the skips are unchanged, and passed is the baseline's +70.

- [x] **Step 2: Every lint.** Each command `cd`s by absolute path, so the order does not matter.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && uv run --python 3.13 --with pyyaml python build/check_conformance.py`: exit 0.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && uv run --python 3.13 python build/cc_guide/cli.py lint`: exit 0.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`: exit 0.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && uv run --python 3.13 python build/check_provenance.py`: exit 0.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies`: `1 passed`.

- [x] **Step 3: Repo hygiene.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-39-cc-guide-hardening && git status --short && git diff --stat main...HEAD | tail -1 && grep -rnE --include='*.py' '^[[:space:]]*(# cc-guide:|<!-- cc-guide:)' build/cc_guide; echo "exit=$?"`
Expected: no `git status` output (`.sdd/` is gitignored); `20 files changed`; no grep match, and `exit=1`.

- [x] **Step 4: Request the final review** per subagent-driven-development: the whole-branch `code-reviewer`, from `main`'s merge-base to `HEAD`, and a Codex second opinion if the owner wants one. There is no PR bot review on this repo. Then run the Plan Completion Protocol below.
> Deviation: the final review ran two seats, the Opus code-reviewer and Codex (gpt-6-astra via `-m`, base 44712e0: "Codex reviewed 7e29e1b", no findings). The code-reviewer found that an empty-key ref (`page › `, which Task 9's `summary` now prints) was rebaselined as the whole page, bypassing R7's refusal; this was the parse half of T9-m4. It was fixed by branching on the separator (acf3858, 6b844df). The fix wave also added the T1-1 comment in check_conformance.py (a5821ac). At the gate the owner chose to fix `LABEL_RE`'s non-ASCII `\d` (73ed2de) and to revise the drift spec's R7 to "changed or gone" (6502c2a), overriding "Leave alone" for that phrase.

---

## Plan completion

Run writing-plans' Plan Completion Protocol after Task 11 and the final review. This plan's specifics:

- **Ticks** (step 3), in `specs/deferred_items.md`, section `38-claude-code-drift-automation`: the four items "Unify the guide's anchor grammar", "Every input error prints a `cc-guide:` line", "Test coverage and edge cases in `build/cc_guide/`" and "Style, DRY and naming in `build/cc_guide/`", each `- [x] … → done in plan 39`. Use the deferred tick-pass check: the box itself must change, not only the note, and the section's open count drops by four.
- **Gate questions** (step 1), batched with any leftovers: whether the drift spec's R7 should say "changed or gone" (Global Constraints, "Leave alone").
- **Deferred items** (step 3) go in a `## 39-cc-guide-hardening — <date>` section, only for leftovers the gate defers. Each follows `skills/writing-plans/references/deferred-backlog.md`'s schema.
- **Retire** (step 5): `git mv` this plan to `specs/plans/completed/`. There is no spec to retire. The plan has no relative links.
- **Report the backlog line** from `deferred_stats.py` (step 4), and run the triage rubric if its thresholds hit.
- **Integration** is finishing-a-development-branch's call: merge, PR or keep. Nothing is pushed without the owner. After a merge into `main`, run `uv run --python 3.13 --with pyyaml python build/check_conformance.py` and `uv run --python 3.13 python build/cc_guide/cli.py lint` on the merged result.

# Codes and BLS Reference Skills Implementation Plan

**Status: COMPLETE (2026-11-26)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md, or specs/completed/deferred_items.md once archived

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close three backlog items of section `audit-3-10-26 routing` in `specs/deferred_items.md`: build tests for classification-codes and geographic-codes (H3), a Census industry (IND) bundle for classification-codes (F5), and the bls-data-context OEWS cleanup (B4 parts 8 to 10).

**Architecture:** The build tests land first, so the IND rebuild runs under a count test. The IND bundle mirrors the Census occupation (OCC) pattern in `skills/classification-codes/scripts/build.py`: a parsed list per vintage plus a derived NAICS expansion. A trigger test, old description against new, gates the description change. The bls-data-context work is text only and runs on its own.

**Tech Stack:** Python (the dev Python in `build/versions.toml`), Polars, fastexcel, pytest, `uv run`; `claude -p` for the trigger reps.

**Spec:** none. The requirements are the three items in `specs/deferred_items.md` (section `audit-3-10-26 routing`, items "Decide whether classification-codes bundles Census industry (IND) codes", "Add tests for the classification-codes and geographic-codes builds" and "Clean up bls-data-context's OEWS reference and research residue"), with their `→ progress 2026-11-17 (owner ruling)` notes.

## Global Constraints

- Files: tasks edit only `skills/classification-codes/**`, `skills/geographic-codes/scripts/**`, `skills/geographic-codes/SKILL.md`, `skills/bls-data-context/**`, the kit folder `specs/baseline/red-baseline-codes-description/` and its write-up `specs/baseline/red-baseline-codes-description.md`, `build/suites.toml` (this lane's entries), `NOTICE` (the classification-codes paragraph), root `README.md` (the classification-codes lines) and `specs/deferred_items.md` (these three items). The completion protocol's own edits (plan markup, retirement to `specs/plans/completed/`, `specs/history.md`, `→ done` notes in `specs/deferred_items.md`) are allowed too. Any other file needs your human partner's yes first.
- Python style: single quotes, method-style Polars expressions, named constants for bands. Keep each file's indentation: `skills/classification-codes/scripts/*.py` use 2 spaces, `skills/geographic-codes/scripts/*.py` use 4.
- Codes are strings everywhere. Census IND codes are four digits, zero-filled.
- Downloads: no network fetch of any source file without your human partner's yes in the session, naming the file, source and size. `BLS_CONTACT_EMAIL` is exported only after the same kind of yes, and only to read the bls.gov pages Task 5 lists.
- Orphan rule: a new non-test file under `skills/<name>/` is named by `SKILL.md` or `MANIFEST.md` of that skill in the same commit.
- `data/`, `sources/` and `MANIFEST.md` of classification-codes change in one commit.
- The plan and kit are public. No user paths, user names or memory-file names in any committed file.
- Before each commit: `uv run --with pyyaml python build/check_frontmatter.py`, `uv run python build/check_provenance.py`, `uv run --with pyyaml python build/check_conformance.py`, `uv run python build/check_links.py`. The pre-commit hook runs these when enabled.

## Review Focus

1. An IND NAICS cell in a shape the parser has never seen → the build stops with an error that quotes the cell, never a silent drop. Test: Task 2 `test_parse_census_ind_rejects_unknown_cell_shapes`.
2. An IND code with no NAICS mapping (armed forces, never worked, unemployed) → the row is kept in `census_ind_<v>.csv` and gets no expansion rows. Test: Task 2 `test_expand_census_ind_skips_unmapped_codes`.
3. An IND cell naming a NAICS prefix absent from the matching NAICS vintage → the build stops and names the prefix and both vintages. Test: Task 2 `test_parse_census_ind_rejects_prefix_missing_from_naics`.
4. A user greps `data/census_ind_2022.csv` for `0170` → the code is stored with its leading zero. Test: Task 2 `test_parse_census_ind_zero_fills_codes`.
5. A count in a SKILL.md file table drifts after a rebuild → the count test fails and names the file and both numbers. Test: Task 1 `test_skill_table_counts_match_data` (both skills), with the mutation check in Task 1 Step 6.

## Decisions

- **D1** (owner, brief, 2026-11-26): this plan covers exactly the three lane 1 items of the 2026-11-26 `/deferred` pass. Lanes 2 and 3 own their own files, and no task here touches them. Applied in: Global Constraints.
- **D2** (owner, brief, 2026-11-26): the IND item goes straight to a plan, with no brainstorming. The 2026-11-17 ruling settles the path (bundle) and the outputs. The expansion rules and row bands are flagged defaults below. Applied in: Task 2.
- **Settled by the source, not a default:** the Census page (`census.gov/topics/employment/industry-occupation/guidance/code-lists.html`, read 2026-11-26) heads each list "Derived from the 2017 NAICS" and "Derived from the 2022 NAICS". So `census_ind_2017` expands against `naics_2017`, and `census_ind_2022` against `naics_2022`.
- **D3** (owner, plan review, 2026-11-26): defaults F1 to F7 below approved as drafted: shared partial claims for IND (F5), the description change with its trigger test (F2, F4), a LAUS selector row (F3), tests first (F1), the 230-320 band (F6) and no IND crosswalk (F7). Applied in: Tasks 1 to 5.
- **D4** (owner, plan review, 2026-11-26): the trigger test's spend is approved, and its cap rises from $25 to $35 so the stop rule does not end the 108 reps early. Applied in: Task 3 Step 3.
- **D5** (owner, plan review, 2026-11-26): errata found by the execution-brief review are fixed in the plan before execution: the kit copy list, the geographic workbook name, Task 2 Step 7's checks and mtime reset, and the completion protocol's files. Applied in: Global Constraints, Tasks 1 to 3.

### Defaults approved at plan review (D3)

- **F1. Order.** Task 1 (build tests) lands before Task 2 (IND bundle), so the IND rebuild runs under the count test.
- **F2. Description.** classification-codes' description gains "IND" with the text in Task 3, which also trims it to 1,005 characters (cap 1,024). The trigger test in Task 3 gates it.
- **F3. LAUS.** bls-data-context gets a LAUS selector row (Task 5), and LAUS stays in the description. So bls-data-context's description does not change and needs no trigger test.
- **F4. Test procedure.** The trigger test of `skills/writing-skills/references/discovery.md` § 6, run under `skills/writing-skills/references/micro-tests.md`, in one kit for the lane.
- **F5. Partial IND rows.** A NAICS cell can name part of a code ("Pt.", "part of") or carve one out ("exc."). Expansion gives one row per (Census code, six-digit NAICS code) with `via` in `exact | prefix | partial`. An exclusion removes its codes from that Census code's claim. A six-digit code may have more than one Census code only when every claim on it is `partial`. Any other double claim stops the build.
- **F6. Row bands.** `census_ind_<v>`: 230 to 320 codes. The expansion covers every six-digit code of the matching NAICS vintage (1,057 for 2017, 1,012 for 2022). The inspect step in Task 2 checks the band against the real lists and reports before any band is committed.
- **F7. Scope.** No Census IND 2017↔2022 crosswalk output, though the 2022 workbook carries one. The ruling names only the two lists and the NAICS expansion.

---

### Task 1: Build tests for classification-codes and geographic-codes

**Files:**
- Modify: `skills/classification-codes/scripts/test_build.py`
- Modify: `skills/geographic-codes/scripts/test_build.py`

**Interfaces:**
- Produces: `table_counts(skill_md: str) -> dict[str, int]` in each test file (the `rows` cell of each `data/*.csv` row of the `## Files` table, first number, commas removed), and `test_skill_table_counts_match_data`, which Task 2 extends by adding rows to the table.

- [x] **Step 1: Write the validator tests (part a), classification-codes**

`test_validate_naics_concordance_row_band`: frames of 799 and 2001 rows give one problem each that contains `outside the plausible 800-2000 band`; 800 and 2000 rows give none. `test_validate_soc_crosswalk_row_band`: the same at 699/700/1600/1601 and `700-1600`. `test_validate_census_occ_flags_band_duplicates_and_levels`: 449 rows → band problem; two rows sharing one `census_occ` → `2 duplicated Census codes` (the function counts rows); a `soc_level` of `group` → `outside`. Build frames with `pl.DataFrame` in the test; no workbook.

- [x] **Step 2: Write the offline-fetch tests (part b)**

classification-codes: `test_fetch_offline_without_cache_raises` (`offline=True`, empty `tmp_path` → `FileNotFoundError` matching `--offline set but`), and `test_fetch_offline_uses_cache_without_network` (cached file present; `urllib.request.urlopen` monkeypatched to raise; returns the cached path and its sha256). geographic-codes: the same two tests against its `fetch`, a third for the `filename` override, and `test_read_sheet_returns_all_utf8` on the committed `sources/2023_list1_2023.xlsx` (every dtype is `pl.Utf8`; some row contains `CBSA Code`).

- [x] **Step 3: Write the count tests (part c)**

`test_skill_table_counts_match_data` in each skill: for every row of the `## Files` table, the `rows` number equals the CSV's height (`pl.read_csv(path, infer_schema=False).height`). classification-codes also checks the parenthetical counts (`1,012 six-digit` = rows with `level` `6`; `867 detailed` = rows with `level` `detailed`) and `test_manifest_rows_match_data` (each `data/*.csv` row of `MANIFEST.md` equals the CSV height). geographic-codes also checks "3,222 current plus 21 closed" against `is_current`. A failure message names the file and both numbers.

- [x] **Step 4: Run both suites**

Run: `uv run python build/run_suites.py classification-codes geographic-codes`
Expected: all pass (the counts match today).

- [x] **Step 5: Mutation check of part (a)**

These tests target code that already works, so prove each one bites. For each validator, change its bound in `build.py` (for example 800 → 799), run its test, expect FAIL, and restore. Run `git diff --stat skills/` after: it shows only the two test files.

- [x] **Step 6: Mutation check of part (c)**

Change `2,125` to `2,126` in classification-codes `SKILL.md` and `3,243` to `3,244` in geographic-codes `SKILL.md`. Run both suites: each count test fails and names the file. Restore both.

- [x] **Step 7: Commit**

```bash
git add skills/classification-codes/scripts/test_build.py skills/geographic-codes/scripts/test_build.py
git commit -m "test(codes): cover validators, offline fetch and file-table counts"
```

### Task 2: Census industry (IND) bundle

**Files:**
- Modify: `skills/classification-codes/scripts/build.py` (a new section after the Census occupation section, `BUILDS`, `REFERENTIAL_PAIRS`)
- Modify: `skills/classification-codes/scripts/test_build.py`
- Create: `skills/classification-codes/data/census_ind_2017.csv`, `census_ind_2017_to_naics_2017.csv`, `census_ind_2022.csv`, `census_ind_2022_to_naics_2022.csv`
- Create: `skills/classification-codes/sources/2017-industry-code-list-with-crosswalk.xlsx`, `sources/2022-Census-Industry-Code-List-with-Crosswalk.xlsx`
- Modify: `skills/classification-codes/MANIFEST.md` (regenerated), `SKILL.md` (body only: file table, column notes, a Census industry paragraph, a grep recipe), `sources/README.md`, `NOTICE`, root `README.md`

**Interfaces:**
- Consumes: `naics_2017`, `naics_2022` frames (columns `code, level, title`); `code_expr`, `title_expr`, `find_col`, `frame_below_header`; Task 1's `table_counts`.
- Produces:
  - `parse_naics_cell(cell: str | None) -> list[tuple[str, str]]`: pairs of (NAICS prefix, kind), kind in `include | partial | exclude`; `[]` for no mapping; `ValueError` quoting the cell for an unknown shape.
  - `parse_census_ind(raw: pl.DataFrame, vintage: int, **deps) -> pl.DataFrame`: columns `census_ind, title, naics_cell` (the cell verbatim), one row per code, sorted.
  - `validate_census_ind(frame, vintage, **deps) -> list[str]`: band `CENSUS_IND_BAND = (230, 320)`, duplicates.
  - `expand_census_ind(vintage: int, **deps) -> pl.DataFrame`: columns `census_ind_<v>, census_title_<v>, naics_<v>, naics_title_<v>, via`, `via` in `exact | prefix | partial`.
  - `validate_census_ind_expansion(frame, vintage, **deps) -> list[str]`: six-digit codes claimed by nobody; double claims that are not all `partial`.

- [x] **Step 1: Owner gate, then download**

Ask your human partner for a yes to download two files from `www2.census.gov/programs-surveys/demo/guidance/industry-occupation/`: `2017-industry-code-list-with-crosswalk.xlsx` and `2022-Census-Industry-Code-List-with-Crosswalk.xlsx`, each under 1 MB (the page's statement). No email is needed. On the yes, fetch them into `sources/` with `build.fetch` (not by hand, so the cache name matches). Without a yes, stop the task and report.

> Deviation: the controller ran Steps 1 and 2 itself after the owner's yes, and handed the findings to the implementer. Both workbooks were fetched with `build.fetch` (72 KB and 103 KB).

- [x] **Step 2: Inspect and record the layout**

With `read_sheet`, run under the pinned stack that `uv run python build/run_suites.py --list geographic-codes` prints (it has `fastexcel`; the classification-codes suite does not), list each workbook's sheet names, the code-list sheet's header row, and every distinct shape of the NAICS cell (replace digits with `9`, count each shape). Record the sheet names, headers, shape counts, the code count of each list and any unmapped codes in the task report. If a code count is outside F6's band, or a shape does not fit F5's three kinds, stop and ask before writing tests.

> Deviation: the data broke F5's double-claim rule (catch-all codes such as 3990 `Part of 31, 32, 33` overlap specific claims on 539 and 507 six-digit codes; 2017 has eight non-partial claims on 928110). The owner ruled on 2026-11-26: a code may carry one exact or prefix claim plus any number of partial claims, with prefix beating partial inside one Census code (this amends F5), and a named override treats the eight 2017 claims on 928110 as partial, as the 2022 list does. Review Focus 2's parenthetical is wrong for the real files: only code 9920 is unmapped, and the seven military codes are mapped (`928110` in 2017, `pt. 92811` in 2022). The 2017 sheet says 270 codes and the build finds 271 distinct codes. `naics_cell` is stored as published, trailing spaces included.

- [x] **Step 3: Write the failing tests**

Fixtures are in-memory frames copied from the shapes Step 2 saw (a few rows each, real header text). Tests: `test_parse_naics_cell_kinds` (one case per recorded shape), `test_parse_census_ind_list_as_published`, `test_parse_census_ind_zero_fills_codes`, `test_parse_census_ind_rejects_unknown_cell_shapes`, `test_parse_census_ind_rejects_prefix_missing_from_naics`, `test_expand_census_ind_partitions_exact_and_prefix_claims`, `test_expand_census_ind_applies_exclusions`, `test_expand_census_ind_allows_shared_partial_claims`, `test_expand_census_ind_rejects_non_partial_double_claims`, `test_expand_census_ind_skips_unmapped_codes`, `test_validate_census_ind_expansion_reports_unclaimed_codes`.

- [x] **Step 4: Run them**

Run: `uv run python build/run_suites.py classification-codes`
Expected: the new tests FAIL with `AttributeError` (no `parse_census_ind`); the old tests pass.

- [x] **Step 5: Implement the five functions and register four builds**

Mirror `parse_census_occ` / `expand_census_occ`. Each list `Build` has `requires=('naics_<v>',)` and the sheet name from Step 2; each expansion `Build` has `url=None` and `requires=('census_ind_<v>', 'naics_<v>')`. Add two `REFERENTIAL_PAIRS` rows: (`census_ind_<v>_to_naics_<v>`, `naics_<v>`, `naics_<v>`, 6). Order `BUILDS` so each list follows its NAICS structure.

- [x] **Step 6: Run the tests**

Run: `uv run python build/run_suites.py classification-codes`
Expected: all pass, the registry tests included.

- [x] **Step 7: Build from the cache**

First reset the mtimes of the ten sourced files: `manifest_records` reads `retrieved` from each source file's mtime (`build.py:928`), and a checkout sets every mtime to the checkout time. For each `sources/` file with a url row in `MANIFEST.md`, run `touch -d <retrieved with +00:00 replaced by Z> <file>` (BSD `touch` rejects `+00:00` and reads a zoneless time as local). Do this after any checkout or stash, which reset mtimes.
Run: `uv run skills/classification-codes/scripts/build.py --offline`
Expected: exit 0, `All validations passed; MANIFEST.md updated.`; `git diff --stat skills/classification-codes/data/` prints nothing (every existing CSV unchanged); `git status --short skills/classification-codes/data/` lists only the four new `census_ind_*` files; `git diff skills/classification-codes/MANIFEST.md` changes only the `Generated` line and adds the four `census_ind_*` rows.

- [x] **Step 8: Document the bundle**

`SKILL.md` body: four rows in the `## Files` table (counts from the build), column notes for `naics_cell` and `via`, a Census industry paragraph beside the Census occupation one (the vintage rule, F5's `partial` meaning, the unmapped codes from Step 2), and one grep recipe for an IND code. Change the title line and "What this is" to name the Census lists. `sources/README.md`: "the Census occupation and industry code lists". `NOTICE` (classification-codes paragraph) and root `README.md` (the classification-codes table row and the public-domain bullet): add "the Census industry code lists". The frontmatter description does not change in this task.

> Deviation: two sentences of SKILL.md's Rebuilding section and one README phrase were edited too (all in allowed files), and the string-typing guidance names the industry codes.

- [x] **Step 9: Run every check**

Run: `uv run python build/run_suites.py classification-codes` (the count test now covers the four new rows), then the four lints of Global Constraints.
Expected: all pass.

- [x] **Step 10: Commit**

```bash
git add skills/classification-codes NOTICE README.md
git commit -m "feat(classification-codes): bundle the 2017 and 2022 Census industry code lists"
```

### Task 3: Trigger-test kit and registered rules

**Files:**
- Create: `specs/baseline/red-baseline-codes-description/kit/` (copied and adapted from `specs/baseline/red-baseline-writing-skills-tests/kit/`: `common.sh`, `run_trigger_reps.sh`, `triggers.py`, `audit.py`, `rep_tools.py`, `cases.py` and `kit_identity.py` (imported by `audit.py:60` and `rep_tools.py:56`), `isolation_probe.txt`, `fixtures/trigger/`, and a new `trigger_prompts.py`), with a no-model test file `test_cd_kit.py`
- Create: `specs/baseline/red-baseline-codes-description.md`
- Modify: `build/suites.toml` (one entry, `codes-description-kit`)

**Interfaces:**
- Produces: `run_trigger_reps.sh <ref> <arm> <prompt-id> <out-dir> <first> <last> <model>`, and `triggers.py loads|tally` reading `Skill` tool calls whose `skill` input is exactly `classification-codes`. Task 4 runs them.

- [x] **Step 1: Copy and adapt the kit**

Changes from plan 107's trigger kit: no competitor plugin skills (the neighbors are this repository's `geographic-codes` and `bls-data-context`, which `git archive <ref> skills/` already lists); one condition, `full`; the skill under test is `classification-codes`. Keep these rules, stated in the write-up:
1. Each rep gets its own new folder outside every repository, with its own HOME and scratch folder.
2. The deny list holds `Bash`, `Read(~/**)`, `ListAgents`, `SendMessage`, `PushNotification` and `RemoteTrigger`, and the settings set `blockReadsOutsideWorkingDirectories`. The runner starts each rep with a single `claude -p` call per rep, not a shell `for` loop that shares one HOME. The copied `common.sh` lacks the `Bash` deny entry and `blockReadsOutsideWorkingDirectories`, so add both. The runner drops plan 107's `<condition>` argument.
3. The runner removes `credential_expires_at` from every saved `.json` and `.jsonl` file. A rep is VOID if the key is still there.
4. A rep is VOID if any record has `result_index` > 0 or an `origin` whose `kind` is `peer`. The runner scrubs `origin` objects from saved records after that check.
5. Quarantine: no rep may read this plan, the kit, the write-up or `specs/deferred_items.md`. A rep that does is VOID.
6. Models: `claude-sonnet-5-5` and `claude-opus-5-5`, same rep count on each.

- [x] **Step 2: Write the prompts**

`trigger_prompts.py` holds these, word for word.
Should load:
- P1: `Our CPS extract has an IND column with values like 7860 and 0770. What industries are those, and which NAICS codes do they cover?`
- P2: `I need to join ACS PUMS records coded with 2017 Census industry codes to QCEW data keyed by NAICS. How do I map one to the other?`
- P3: `What is the 2022 NAICS title for 541511, and did that code change from 2017?`
- P4: `Map these SOC 2010 codes to SOC 2018: 15-1132 and 15-1133.`
- P5: `Our ACS file has OCCP 1021. Which occupation is that?`

Near misses:
- N1: `Which counties are in the Austin-Round Rock CBSA?`
- N2: `How does the CES birth-death model feed into the monthly payroll estimate?`
- N3: `How do I compute an unemployment rate from CPS microdata with the PWSSWGT weight?`
- N4: `Write a Polars function that drops duplicate rows keyed on series_id and ref_date.`

- [x] **Step 3: Write the description arms and the rules**

`old` is the commit before Task 4's description change; `new` is the same tree with the description below (exact copy, 1,005 characters once folded):

```yaml
description: >
  Use when a task touches NAICS, SOC, or Census industry (IND) or occupation (OCC) codes — mapping a
  code to its title or a title to its code, listing a sector's or major group's members, converting
  between vintages (NAICS 2012↔2017↔2022, SOC 2010↔2018, Census OCC 2010↔2018), joining datasets
  coded in different vintages, a series break at a revision, or explaining how
  industries and occupations are defined and revised (ECPC / SOCPC, NAICS 2027, SOC 2028). Consult
  BEFORE answering any code↔title question, joining on an industry or occupation code, or treating a
  code as the same thing in two vintages. Trigger on: NAICS, SOC, O*NET, ACS / CPS IND or OCC
  variable, sector, subsector, industry group, six-digit code, occupation code, major group, detailed
  occupation, concordance, crosswalk, trilateral, change indicator, unclassified / 999999, "what
  industry is X", "what does code X mean", "is code X still valid", "when is the next revision".
  Codes and titles come from data/, never from model memory.
```

Register in the write-up, before any rep: 3 reps per cell (9 prompts × 2 arms × 2 models = 108 reps). A rep loads when `triggers.py loads` finds a `Skill` call for `classification-codes`. PASS, on each model: `new` loads on P1 + P2 ≥ `old` loads there, `new` loads on P1–P5 ≥ `old` loads there, and `new` loads on N1–N4 ≤ `old` loads there. FAIL otherwise. VOID: rules 3 to 5 of Step 1, an error result, or a listing that lacks `classification-codes`, `geographic-codes` or `bls-data-context`. A void rep is rerun once. Spend cap $35 at $0.25 per rep (108 reps are $27 at worst case, plus the probe, two pilots and void reruns); stop when the running total plus the next batch's reps × $0.25 would pass it.

- [x] **Step 4: Test the kit without a model**

`test_cd_kit.py` runs the runner against a stub `claude` (as plan 107's kit test does) and checks: the scrub removes `credential_expires_at` and `origin`; a `result_index` of 1 or a peer origin is VOID; `tally` applies the PASS rule to fixed counts. Register `codes-description-kit` in `build/suites.toml` with the `with` list the test needs.
Run: `uv run python build/run_suites.py codes-description-kit`, then `uv run python build/run_suites.py --check`
Expected: pass; `suite registry ok`.

> Deviation: the kit's test file grew to 162 tests with 126 mutants after two review rounds (rule 5 also voids a search whose glob, root or result reaches a quarantined file). The write-up registers readings beyond the brief (a `--max-turns` or budget end is normal, a non-integer `result_index` voids, a cell short after one rerun stays incomplete); the owner accepted them before any scored rep.

- [x] **Step 5: Commit the kit and the rules**

```bash
git add specs/baseline/red-baseline-codes-description specs/baseline/red-baseline-codes-description.md build/suites.toml
git commit -m "test(codes): register the classification-codes trigger test"
```

### Task 4: Run the trigger test and land the description

**Files:**
- Modify: `skills/classification-codes/SKILL.md` (frontmatter `description` only)
- Modify: `specs/baseline/red-baseline-codes-description.md` (shas, probe, results, spend)

- [x] **Step 1: Probe and pilot**

Record `claude --version`. Run one isolation probe rep (`isolation_probe.txt`): the answer must show no instruction files, no memory, no other sessions and only the planned tools. Then one pilot rep per model on P1 with `old`. Record each cost. A leak stops the task.

- [x] **Step 2: Make the `new` ref**

Replace the description with Task 3's exact text. Run `uv run --with pyyaml python build/check_frontmatter.py` (no error) and commit it on its own (`feat(classification-codes): name Census industry codes in the description`). Record both shas in the write-up.

- [x] **Step 3: Run the 108 reps**

Batch by prompt and arm, with the spend check before each batch. Record each batch's cost.

- [x] **Step 4: Tally and decide**

Run `triggers.py tally`. Record both counts for both arms on each model, the verdict, and any void reps. On FAIL, revert the description commit (`git revert`), record the result and ask your human partner before any other wording.

> Deviation: none in the procedure. Result: PASS on both models, 108 of 108 reps valid, $15.00 spent. The test shows no loss and cannot show a gain, because `old` already loaded on every P1 to P5 rep.

- [x] **Step 5: Commit the record**

```bash
git add specs/baseline/red-baseline-codes-description.md
git commit -m "docs(baseline): record the classification-codes trigger test"
```

### Task 5: bls-data-context OEWS reference, residue and LAUS row

**Files:**
- Modify: `skills/bls-data-context/references/oews.md` (rewrite)
- Modify: `skills/bls-data-context/references/qcew.md:5`, `references/cps.md:547-548`
- Modify: `skills/bls-data-context/SKILL.md` (the program selector table only)

- [x] **Step 1: Owner gate for sources**

The new facts (panel design, reference periods, vintage comparability, series-ID fields) must come from BLS pages, not memory: the OEWS Handbook of Methods (`bls.gov/opub/hom/oews/`) and the series layout file `download.bls.gov/pub/time.series/oe/oe.txt`. bls.gov blocks scripts without a contact email. Ask your human partner to choose: a yes to export `BLS_CONTACT_EMAIL` for reading those pages, or saving the pages from a browser into a scratch folder outside the repository. Without either, stop the task and report.

> Deviation: the owner chose the built-in browser pane, with no email export. The page text was read there, and verbatim excerpts were saved outside the repository.

- [x] **Step 2: Rewrite `oews.md` as a reference**

Target outline: what OEWS measures; panel design and reference periods; vintages and comparability over time; series-ID anatomy (each field, position and width, from `oe.txt`); flat files (keep the current file list and parsing rules); measures; geography (keep `### OMB delineation adoption` as is, since `ces.md:54` points to it); industry scope and the CES crosswalk (keep the facts of current §7). Drop the build-spec parts: the "Build a repeatable downloader" purpose, §9 output schema, §10 processing steps, §11 and §12. Remove the first-person sentence at current line 45. Cite every new fact with the source tag style the file already uses.

- [x] **Step 3: Remove the research residue**

`qcew.md:5`: `Primary pages provided by the user:` → `Primary pages:`. `cps.md:547-548`: delete the `[CENSUS-TP66-USER-URL]` bullet and its retrieval note (the tag appears nowhere else; confirm with `grep -rn CENSUS-TP66-USER-URL skills/`).

- [x] **Step 4: Add the LAUS row**

After the CPS row of the selector table in `SKILL.md`, add:

> Deviation: the reference-index cell for `oews.md` in SKILL.md (line 228) was updated too, two more research-residue labels in `cps.md` were reworded, and `oews.md` gained a footnote note, all on owner rulings.

```markdown
| **LAUS** | Labor force, employment, unemployment, unemployment rate | **Household** concepts · **persons by residence**, model-based | Monthly | State and sub-state areas | No reference of its own: [references/sae.md](references/sae.md) (OMB adoption, LAUS vs CES-SA) and [references/qcew.md](references/qcew.md) (LAUS vs QCEW) |
```

The description keeps LAUS and does not change.

- [x] **Step 5: Check**

Run: `grep -rn "provided by the user\|CENSUS-TP66-USER-URL\|Acceptance criteria\|Build a repeatable downloader" skills/bls-data-context/` → no output. Then the four lints of Global Constraints, and `uv run python build/check_snippets.py skills/`.
Expected: all pass.

- [x] **Step 6: Commit**

```bash
git add skills/bls-data-context
git commit -m "docs(bls-data-context): rewrite the OEWS reference, drop research residue, add a LAUS row"
```

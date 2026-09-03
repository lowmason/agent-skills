# Repo audit and skill scorecard — 2026-09-02

**Status: COMPLETE (retired 2026-09-03)** — remediated by plan 21 (`specs/plans/completed/21-audit_9_2_26.md`): X1 reverted, D1/D2 committed, D3 retired, H3 pinned, the `geographic-codes` interval overstatement corrected, and H1 closed for four of the five untested scripts (26 new tests across three suites). H2, H4, W1, `calibration_check.py`, `scan.sh` and the unratified scorecard weights were consciously deferred to `specs/deferred_items.md` at the 2026-09-03 completion gate. Whole-repo audit of `agent-skills` at `6570701`
(main, clean tree), followed by a per-skill scorecard of all 32 skills against the rubric
`writing-skills` sets for this repo. Every number below was measured in this session, not
transcribed from CLAUDE.md or earlier audits. Precedents: `specs/completed/audit_1_3_26.md`,
`audit_7_5_26.md`, `audit_7_20_26.md`.

## Baseline — mechanical gates

| Gate | Result |
|---|---|
| `build/check_frontmatter.py` (skills, agents, commands) | exit 0, silent |
| `build/check_provenance.py` | exit 0, silent — all 32 skills have a NOTICE entry |
| `build/smoke_test.py` | OK (overdispersion → NegativeBinomial; group → hierarchical) |
| `~/.claude/skills/*` symlinks | 32/32 resolve; every repo skill is linked; no orphan links |
| `~/.claude/agents/*`, `~/.claude/commands/*`, `.claude/rules/*` | 7/7, 3/3, 1/1 resolve |
| `superpowers:` namespace leaks | 0 |
| `@skills/…` force-load links | 0 (the one match is writing-skills' own ❌ example) |
| Cross-skill file references (`clean-coder` → `clean-code/references/*`, `track-model-experiments` → `bayesian-workflow/references/*`, `recommend-visualization` → `explore-data/scripts/profile.py`, `tune-hyperparameters` → `recommend-probabilistic-model/references/model-selection-regularization.md`, `derive-roadmap` → `describe-critique-methodology/references/spec-synthesis.md`) | all resolve |
| Dangling `use the X skill` references | 0 |
| Secrets / hardcoded contact emails in tracked files | none (the two `BEGIN RSA PRIVATE KEY` hits are llm-wiki redaction-test fixtures) |
| Tracked `.DS_Store` | none (three untracked, gitignored) |
| Tracked size | 12.9 MB; 8 of the 10 largest files are geographic-codes data/sources (documented public-domain derivations, NOTICE) |

### Test suites — every suite passes, 390 tests total

| Suite | CLAUDE.md says | Measured |
|---|---|---|
| `build/` | 34 | **36 passed** |
| `recommend-probabilistic-model/scripts` | 10 | 10 passed |
| `recommend-visualization/scripts` | 29 | 29 passed |
| `tune-hyperparameters/scripts` | 6 passed, 2 skipped; "add `--with sklearn --with optuna` to run all 8" | 6 passed, 2 skipped; **`--with sklearn` fails to install** (uv refuses the deprecated shim); `--with scikit-learn --with optuna` → 8 passed |
| `track-model-experiments/scripts` | 11 | 11 passed (48.7 s) |
| `llm-wiki/scripts` | 180 | **185 passed** |
| `describe-critique-methodology/scripts` | 18 | 18 passed |
| `geographic-codes/scripts` | 38 | **42 passed**, 7 `FutureWarning`s (H2) |
| `classification-codes/scripts` | **not listed** | **51 passed** |

## Findings

IDs: **D** = drift (a doc no longer matches the tree), **H** = hygiene, **W** = watch (no action yet).

### X1 — LIVE BREAK (appeared mid-audit): `commands/deferred.md` frontmatter no longer parses
The tree was clean at `6570701` when the lint first passed. Partway through this session an
uncommitted edit (from a parallel terminal, not this session) re-wrapped the `description:` onto
three lines with the continuation lines at column 1. YAML reads an unindented continuation as a
new mapping key, so `check_frontmatter.py` now exits 1
(`frontmatter is not valid YAML (ScannerError)`) and `/deferred` will not load its description.
**Fix (one of):** indent the continuation lines by two spaces, or use `description: >` with the
lines indented beneath it (the form every SKILL.md in the repo uses). Not touched here — it is
your in-progress edit. Re-run the lint before committing. It also fails one build test
(`test_check_frontmatter.py::test_real_agents_and_commands_are_clean`), so the build suite reads
35 passed / 1 failed until it is fixed.

### D1 — CLAUDE.md `## Commands` block is stale in five places
**Resolved 2026-09-02.** Counts set to 36 / 185 / 42; the hint now names `scikit-learn`; the
classification-codes suite is listed (51 tests, `--with pytest --with polars` — a verifier ran it
without fastexcel and it passes, since its fixtures are in-memory frames) alongside a rebuild block
mirroring geographic-codes' (network path needs `BLS_CONTACT_EMAIL`). Verified by a four-agent
workflow that re-ran every command in the block as written: every count matches; the one
failure anywhere (`test_real_agents_and_commands_are_clean`) is X1, not these edits.

Evidence in the table above. Three counts are behind (36 / 185 / 42), the tune-hyperparameters
hint names a package uv cannot install (`sklearn` → `scikit-learn`), and the
`classification-codes` suite (51 tests, `--with pytest --with polars --with fastexcel`) was never
added when the skill landed. **Fix:** update the block; add the missing command directly after
the geographic-codes one. Minor → fix directly (proportional-process).

### D2 — README.md does not mention `geographic-codes` at all
**Resolved 2026-09-02.** Row added after `classification-codes` (190 words; the refuter confirmed
33 of 34 atomic claims and the 34th — "every row carries `[valid_from, valid_to)`" — was corrected
to "every county-equivalent and CBSA row", since `states.csv` and `county_changes.csv` carry no
interval). The Credits originals bullet had been missing *both* new data skills, not one; both are
added and the list now matches NOTICE's sixteen name for name. A **Public-domain data** credit was
added, and the License section's "Everything here is MIT" was narrowed to "Everything I wrote" with
a **Bundled U.S. Government data** bullet, because 18 verbatim federal files are now committed under
`sources/`. NOTICE's public-domain parenthetical gained "the Census occupation code lists" so the
README never claims a source NOTICE does not (the OCC workbooks are Census publications, in
`sources/` with sha256 entries). The intro sentence naming `bls-data-context` as the only
domain-bound skill now names all three.
**New follow-up (not done — skill edits go through writing-skills):** `geographic-codes/SKILL.md:27-28`
makes the same "every row carries `valid_from` and `valid_to`" overstatement.

The "Mine" table has 16 rows, but that is `bayesian-workflow` (cross-listed) plus 15 originals;
`geographic-codes` (in NOTICE and CLAUDE.md since 2026-09-02) has no row, and the Credits
section has no public-domain data note for it. **Fix:** add a row after `classification-codes`
mirroring its phrasing; extend the Credits bullet that covers classification-codes' Census/BLS
sources to name OMB/Census county and CBSA sources. Minor → fix directly.

### D3 — `specs/skill-intake-review-2026-08-26.md` is still live though fully acted on
Its status line reads "recommendation, no changes made", but NOTICE records all three adoptions it
recommended landing on 2026-08-26 (clean-code M-rules, bayesian-workflow jax-numerics,
tech-debt join-cardinality signal), each with its own `specs/red-baseline-*.md`. The three
RED-baseline files are quarantine fixtures ("quarantine this file during any future micro-test
of `bayesian-workflow`") and should stay findable. **Decision for you:** retire the intake review
to `specs/completed/` with a one-line resolution header, and either move the three baselines with
it or leave them in `specs/` root — but write down which (stale → retire).

### H1 — Five untested scripts, two of them load-bearing for other skills
| Script | Why it matters | Coverage |
|---|---|---|
| `explore-data/scripts/profile.py` | Its `--json` output is `recommend-visualization`'s input contract (SKILL.md:48, 67; chart-selection.md) | none |
| `bayesian-workflow/scripts/check_diagnostics.py` (+ `calibration_check.py`, `diagnose_model.py`) | Fills `report.md`'s Assessment lines and next-steps list; SKILL.md:316 says never hand-roll those | none — an open deferred item already asks for a "snippet-execution gate" |
| `design-architecture/scripts/new_adr.py` | ADR scaffolder | none |
| `tech-debt/scripts/scan.sh` | The sweep's grep battery | none |
| `subagent-driven-development/scripts/{review-package,task-brief,sdd-workspace}` | Every SDD dispatch runs through them | none |
**Fix:** at minimum a schema test for `profile.py --json` on a tiny parquet and a fixture-driven
test for `check_diagnostics.py` (a `diagnostics.json` with one divergence, one high R-hat).
This is a `develop-testing-strategy` job; well-specified → plan without a spec.

### H2 — `geographic-codes/scripts/build.py:208` emits 7 polars `FutureWarning`s
`pl.read_excel(path, has_header=False)` triggers polars' own `from_arrow(...) will return a Series
in 2.0` warning through the fastexcel engine; nothing in the repo's code calls `from_arrow`. Harmless
until polars 2.0. **Fix:** none now; when polars 2.0 lands, re-run the suite — the seven
`test_parse_each_bundled_delineation_workbook[*]` cases are the canary.

### H3 — The vendored superpowers snapshot is not pinned
NOTICE and README credit `obra/superpowers` (MIT, © 2025 Jesse Vincent) but record no commit, tag,
or retrieval date. Six ports have not been touched since the 2026-07-04 move
(`dispatching-parallel-agents`, `receiving-code-review`, `systematic-debugging`,
`test-driven-development`, `using-git-worktrees`, `verification-before-completion`), and without
a pin nothing can tell whether upstream has since fixed something in them. **Decision for you:**
add "vendored from commit `<sha>` on `<date>`" to the NOTICE superpowers block (the same
traceability the mancusolab adoptions already have via their RED-baseline dates).

### H4 — Loose files inside skill directories (low priority, no behaviour impact)
- `README.md` inside `bayesian-workflow/`, `recommend-probabilistic-model/`,
  `recommend-visualization/` — GitHub-facing only; Claude Code never loads them.
- `writing-skills/` keeps its five support docs (`anthropic-best-practices.md`,
  `testing-skills-with-subagents.md`, `persuasion-principles.md`, `graphviz-conventions.dot`,
  `render-graphs.js`) and `examples/` at top level, while prescribing `references/` for everyone else.
- `systematic-debugging/` carries four technique files and `find-polluter.sh` at top level, unreferenced by tests.
- No bundled `.py` script has an executable bit; six have shebangs. Harmless under `uv run`.

### W1 — Description listing budget is near the raised cap
32 descriptions total 19,762 chars ≈ 4,940 est. tokens (chars/4, ±15 %) against ≈ 5,000 tokens at
`skillListingBudgetFraction = 0.025` on a 200 K window. **All 32 personal skills are present in
this session's listing**, so nothing is being dropped today — but the next skill likely tips it
into drop-by-rank. Four descriptions also sit within 25 chars of the 1,024 cap
(`classification-codes` 1,022, `design-architecture` 1,019, `bls-data-context` 1,011,
`geographic-codes` 1,007). Standing decision unchanged: densities are deliberate; the lever is the
fraction (≈ 0.03) or per-project scoping, not trimming. Check `/context` before skill #33.

### W2 — Deferred backlog after today's first `/deferred` pass
44 open / 22 closed. 33 of the 44 open items are llm-wiki (plans 13, 14, 16); the rest are the
methodology-pipeline plans (11) and singletons. Nothing to do here — `/deferred` already sorted them.

## Scorecard

### Rubric (0–3 each; total /9)

| Dim | 3 | 2 | 1 | 0 |
|---|---|---|---|---|
| **D — description** | "Use when…", third person, dense concrete triggers, states its boundary with siblings, never summarises the procedure or deliverable | one of: a sentence summarising what the skill does or produces (writing-skills §SDO anti-pattern), second-person "you", or near-zero keyword coverage | generic | first person / missing |
| **S — structure & size** | start at 3 | −1 body > 2,500 words (25 % past writing-skills' 2,000-word "ask what belongs in references/" prompt) | −1 no boundary / when-not / sibling section while ≥ 2 skills share its domain | −1 no scanning aid (quick reference, tables, reference map) **and** no common-mistakes / red-flags section, bodies > 500 words |
| **V — verification evidence** | bundled scripts/data have passing tests and/or the behaviour was RED→GREEN tested with a documented control in `specs/` | review-only evidence (the three prior audits) or tests for part of the surface | inherited upstream (superpowers) testing only — the transcripts were removed at port time (NOTICE) | none |

Provenance and cross-reference hygiene are not scored: every skill passes both, so they would not
discriminate. Description density is deliberately not penalised (standing decision). The rubric is
a first cut — re-weight it and the notes column still stands.

**Mean 7.81 / 9. Distribution: 8 skills at 9, 12 at 8, 10 at 7, 2 at 6.**

| Skill | Type | Desc chars | Body words | Refs | Tests | D | S | V | **/9** |
|---|---|---:|---:|---:|---:|:-:|:-:|:-:|:-:|
| `bayesian-workflow` | technique+reference | 770 | 3,964 | 12 | untested scripts | 3 | 1 | 2 | **6** |
| `bls-data-context` | reference | 1011 | 2,304 | 10 | — | 3 | 3 | 2 | **8** |
| `brainstorming` | discipline | 426 | 1,752 | 0 | untested scripts | 3 | 3 | 2 | **8** |
| `classification-codes` | reference | 1022 | 2,217 | 1 | 51 | 3 | 3 | 3 | **9** |
| `clean-code` | reference | 998 | 1,161 | 6 | — | 3 | 3 | 3 | **9** |
| `clean-coder` | discipline | 511 | 1,249 | 0 | — | 3 | 3 | 3 | **9** |
| `creative-thinking` | pattern | 495 | 1,409 | 0 | — | 3 | 2 | 2 | **7** |
| `derive-roadmap` | technique | 337 | 1,147 | 2 | — | 2 | 3 | 3 | **8** |
| `describe-critique-methodology` | technique | 854 | 1,012 | 4 | 18 | 2 | 3 | 3 | **8** |
| `design-architecture` | technique | 1019 | 2,328 | 1 | untested scripts | 3 | 3 | 2 | **8** |
| `develop-testing-strategy` | technique | 968 | 2,641 | 3 | — | 3 | 2 | 2 | **7** |
| `dispatching-parallel-agents` | technique | 300 | 980 | 0 | — | 3 | 3 | 1 | **7** |
| `executing-plans` | discipline | 274 | 393 | 0 | — | 2 | 3 | 3 | **8** |
| `explore-data` | technique | 977 | 1,983 | 0 | untested scripts | 3 | 3 | 1 | **7** |
| `finishing-a-development-branch` | discipline | 430 | 1,136 | 0 | — | 3 | 3 | 2 | **8** |
| `geographic-codes` | reference | 1007 | 1,772 | 1 | 42 | 3 | 3 | 3 | **9** |
| `llm-wiki` | technique | 566 | 969 | 0 | 185 | 3 | 3 | 3 | **9** |
| `receiving-code-review` | discipline | 323 | 903 | 0 | — | 3 | 3 | 1 | **7** |
| `recommend-probabilistic-model` | reference | 871 | 605 | 7 | 10 | 3 | 3 | 3 | **9** |
| `recommend-visualization` | technique | 913 | 768 | 5 | 29 | 3 | 3 | 3 | **9** |
| `requesting-code-review` | discipline | 290 | 503 | 0 | — | 3 | 3 | 2 | **8** |
| `subagent-driven-development` | discipline | 418 | 3,632 | 0 | untested scripts | 3 | 2 | 3 | **8** |
| `systematic-debugging` | discipline | 431 | 1,486 | 0 | — | 3 | 3 | 1 | **7** |
| `tech-debt` | technique | 906 | 1,978 | 0 | untested scripts | 3 | 3 | 2 | **8** |
| `test-driven-development` | discipline | 79 | 1,415 | 0 | — | 2 | 3 | 1 | **6** |
| `track-model-experiments` | technique | 722 | 944 | 0 | 11 | 3 | 2 | 3 | **8** |
| `tune-hyperparameters` | technique | 655 | 1,039 | 0 | 8 | 3 | 3 | 3 | **9** |
| `using-git-worktrees` | technique | 343 | 1,120 | 0 | — | 3 | 3 | 1 | **7** |
| `validate-data` | technique | 845 | 2,654 | 0 | — | 3 | 2 | 2 | **7** |
| `verification-before-completion` | discipline | 298 | 630 | 0 | — | 3 | 3 | 1 | **7** |
| `writing-plans` | technique | 306 | 1,770 | 0 | — | 3 | 2 | 3 | **8** |
| `writing-skills` | discipline | 397 | 4,091 | 0 | — | 3 | 2 | 2 | **7** |

- **`bayesian-workflow` (6/9)** — Body 3,964 words with 12 references already available; no boundary section toward track-model-experiments / tune-hyperparameters / recommend-probabilistic-model, which all point here. Three scripts untested; jax-numerics shipped RED-only (GREEN not run, by convention).
- **`bls-data-context` (8/9)** — Hub body 2,304 words over 54,646 reference words — the navigational split writing-skills asks for. Review-only verification (audit C4/C5 fixes); no automated fact gate.
- **`brainstorming` (8/9)** — Upstream pressure-tested; the local spec-lifecycle extension was not separately tested. visual-companion.md + 5 server scripts are untested JS.
- **`creative-thinking` (7/9)** — No quick reference, tables, or common-mistakes section at 1,409 words. No dedicated spec; review-only evidence.
- **`derive-roadmap` (8/9)** — Description sentence "Partitions gaps into staged spec-to-plan cycles" summarises the procedure — the exact anti-pattern writing-skills §SDO names. Plan 19 micro-tests with controls.
- **`describe-critique-methodology` (8/9)** — Description's last sentence specifies the deliverable's shape ("math and prose decoupled from code") — a process clause. 18 tests pass; plan 18 micro-tests with controls.
- **`design-architecture` (8/9)** — scripts/new_adr.py has no test. Review-only evidence.
- **`develop-testing-strategy` (7/9)** — Body 2,641 words with only 2,416 reference words; review-only evidence.
- **`dispatching-parallel-agents` (7/9)** — Untouched since the port (1 commit). Upstream pressure-test transcripts were removed (NOTICE), so no local evidence.
- **`executing-plans` (8/9)** — Second-person "Use when you have…"; 274-char description with few keywords. Plan-completion protocol GREEN-tested on this path.
- **`explore-data` (7/9)** — scripts/profile.py is the input contract for recommend-visualization (`profile.py --json`) and has no test of its own.
- **`finishing-a-development-branch` (8/9)** — Upstream-tested; appears in the plan-completion GREEN runs only as a downstream step.
- **`receiving-code-review` (7/9)** — Untouched since the port; upstream evidence only.
- **`requesting-code-review` (8/9)** — Reviewer template verified through the SDD-refine workflows; no standalone pressure test.
- **`subagent-driven-development` (8/9)** — Body 3,632 words with no references/ — the two prompt templates are loose files. RED baseline + pressure re-test in the refine spec; plan-completion GREEN.
- **`systematic-debugging` (7/9)** — Untouched since the port; upstream evidence only. Four loose technique files and a shell script, none exercised.
- **`tech-debt` (8/9)** — scripts/scan.sh has no test; join-cardinality signal has a RED baseline.
- **`test-driven-development` (6/9)** — 79-char description is writing-skills' own GOOD example, but carries zero keyword coverage — it fires via the global CLAUDE.md mandate, not the listing. Upstream evidence only.
- **`track-model-experiments` (8/9)** — No quick reference, tables, or common-mistakes section. 11 tests pass (RED→GREEN by execution per its spec).
- **`using-git-worktrees` (7/9)** — Untouched since the port; upstream evidence only.
- **`validate-data` (7/9)** — Body 2,654 words with zero references/ — nowhere for depth to go. Review-only evidence.
- **`verification-before-completion` (7/9)** — Untouched since the port; upstream evidence only.
- **`writing-plans` (8/9)** — 1,770 words, no quick reference or common-mistakes section. Plan-completion protocol pressure-tested (6/6 agents failed RED, GREEN both paths).
- **`writing-skills` (7/9)** — 4,091 words — grew from the 3,885 the 2026-01-03 audit flagged against its own budget; support docs sit loose at top level, not in references/. "Match the Form" section is micro-test-derived; the meta-skill as a whole was never pressure-tested locally.

### Reading the scorecard

- **The 6/9s are not the weakest skills — they are the ones the rubric can see.** `bayesian-workflow`
  is the most-referenced skill in the repo (10 inbound mentions) and lost points only on structure and
  untested scripts; `test-driven-development` lost them on a description writing-skills itself endorses.
- **V is the dimension with the most headroom.** Six upstream ports have no local evidence at all;
  seven Lowell originals from the June build-out (`bls-data-context`, `creative-thinking`,
  `design-architecture`, `develop-testing-strategy`, `explore-data`, `tech-debt`, `validate-data`)
  predate the spec lifecycle and have review-only evidence. Every skill built after
  `plan-completion-protocol` scores 3 on V.
- **Size outliers are the same five every audit finds:** `writing-skills` (4,091), `bayesian-workflow`
  (3,964), `subagent-driven-development` (3,632), `validate-data` (2,654),
  `develop-testing-strategy` (2,641). The 2026-01-03 audit flagged writing-skills at 3,885; it has grown.

## Decisions for you

1. ~~**D1, D2 — fix directly?**~~ Done (see the Resolved notes); NOTICE gained one parenthetical item — veto if unwanted.
2. **D3 — retire the intake review** and say where the three RED-baseline fixtures live.
3. **H3 — pin the superpowers commit** in NOTICE (attribution traceability).
4. **H1 — schedule the script tests** (a `develop-testing-strategy` plan, no spec needed).
5. **Rubric weights** — the S size threshold (2,500) and the V ladder are my calls; change them and
   the notes column still holds.

## Not checked

- Fact accuracy inside reference bodies (BLS, NAICS/SOC, geography, PML citations) beyond the
  existing gates — the 2026-07-20 nine-lens review covered that and Gate A was not re-run here.
- Upstream drift against `obra/superpowers` (needs the pin from H3 and network).
- Live triggering recall (standing decision: not re-run without observed mis-triggering).
- `hooks/` templates (work-repo tooling, not skills).

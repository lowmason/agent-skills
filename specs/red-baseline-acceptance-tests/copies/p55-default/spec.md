# Test-suite registry and runner — Design Spec

**Status:** Design approved in brainstorming on 2026-10-18. Next step: an implementation plan from the
writing-plans skill (`entry_check.py` reported plan id 54 as next free on 2026-10-18).

## What this builds

A registry of the repo's directory-scoped pytest suites, a runner that reads it, and a commit lint that
keeps it complete:

- `build/suites.toml` holds one entry per suite: its directory, its `--with` deps, the extra deps that
  unlock its skips, its interpreters, and its notes.
- `build/run_suites.py` (stdlib only) lists the suites, runs one or more of them, runs all of them, and
  checks the registry.
- `run_suites.py --check` becomes the ninth commit lint. It fails when a directory that holds tests is not
  registered.

The root `CLAUDE.md` then replaces its per-suite commands with a short block that points at the runner.

## Why

- **The 200-line limit.** The `claude-md-size` check (a commit lint, through `build/check_conformance.py`)
  fails at 200 lines. `CLAUDE.md` had 199 on `main` at `456e3fb`. Its Commands block spends lines 66–125,
  60 lines, on one `cd <dir> && uv run … python -m pytest -q` command and comment per suite. Each new suite
  costs two or three more lines.
- **Three plans competed for the last lines on 2026-10-18.** Plan 50 (the superpowers upstream fixes,
  lowmason/agent-skills#56) took the file from 195 to 199. Plan 52 (the write-with-asd-ste100 skill, not
  merged) needs two more lines. Its open question Q4 asked where they come from: (a) fold seven suites under
  one comment, (b) record a size deviation, or (c) move the per-suite commands out of the root file first.
  This spec is option (c).
- **Plan 38 fixed the same problem once.** In plan 38, Task 2 condensed `CLAUDE.md` from 224 lines to 170
  and kept every command in place. The file then grew back to 199 by 2026-10-18. A registry removes the
  per-suite growth.
- **Compound commands.** Worktree-isolated sessions and their subagents have refused compound shell such as
  `cd X && Y` (seen on 2026-10-12). A runner gives each suite a single simple command.

## Decisions taken in brainstorming

The owner took these decisions on 2026-10-18. Each records the option that the owner chose.

1. **The coverage guard is a ninth commit lint:** "`run_suites.py --check` joins build/run_commit_lints.sh,
   so the pre-commit hook and CI run it."
2. **Plan 52's Q4 is (c):** "This work lands whole, registry and CLAUDE.md shrink, ahead of plan 52's Task 6.
   Task 6 then adds one build/suites.toml entry instead of editing Commands. Plan 52's planning session
   amends its plan to match and records Q4 as (c)."
3. **Approach A:** "build/suites.toml (data) + build/run_suites.py (stdlib, tomllib). Matches
   conformance.toml and manifest.toml. One central file, sorted by name." Rejected: a Python list inside the
   runner (every suite change becomes a code edit), and one manifest per suite directory (`install.py`
   copies skill directories, so the manifests would ship with installed skills). An `@`-imported document
   was ruled out before the vote: the guide says imported files load at launch too, so it only moves lines.
4. **Design section 1** (the registry keys and the runner's behaviour) was approved as presented. It is
   R1–R3 below.
5. **Design section 2** (the guard, the file edits, the tests and the couplings) was approved as presented.
   It is R4–R7 below.

## Design

### R1 — Scope

R1.1 The registry holds every **directory suite**: a directory where pytest runs as a whole, with no
selection argument. On `main` at `456e3fb` there are 18: the 17 in `CLAUDE.md` lines 66–125, and
`build/cc_guide`, whose command is line 145.

R1.2 These commands **stay literal in `CLAUDE.md`**. They are selections or tools, not directory suites, and
their comments say when to run them:
- `test_runtime_support.py` (lines 63–64), `test_commit_lints.py`, the `-k declared_dependencies` and
  `-k test_real_skill` lints, `test_check_jax_examples.py`, and the "Single test" example;
- the commit lints, the snippet tiers, the JAX CPU examples, the smoke test, the two `build.py` rebuilds,
  `verify_citations.py`, `extract_structure.py`, and `cli.py lint` and `check`.

R1.3 `build/run_commit_lints.sh` keeps its literal commands. It does not call the runner, except for the new
`--check` lint (R4).

### R2 — The registry: `build/suites.toml`

R2.1 One `[[suite]]` table per directory suite, sorted by `name`. A header comment states the keys, the
sort order, and that the ninth commit lint checks the file.

R2.2 Keys:

| Key | Type | Required | Meaning |
|---|---|---|---|
| `name` | string | yes | The name that the runner takes. A skill's suite uses the skill's name; the others are `build`, `cc-guide` and `hooks`. |
| `dir` | string | yes | The repo-relative directory that pytest runs from. |
| `with` | list of strings | yes | The default `--with` deps, in the order the current command gives them. It includes `pytest`. |
| `extras` | list of strings | no | The deps that unlock skips. Only `--extras` adds them. |
| `pythons` | list of strings | no | The interpreters, one run each, in order. Default `['3.13']`. |
| `notes` | list of strings | no | What the suite covers or needs: opt-in environment variables, expected warnings, run times, why some tests skip or fail. |

R2.3 The entries carry the text of today's commands and comments. Every command, dependency and note
survives; the only change is the form. The inventory, from `CLAUDE.md` at `456e3fb`:

| `name` | `dir` | `with` (after `pytest`) | `extras` | `pythons` |
|---|---|---|---|---|
| `bayesian-workflow` | `skills/bayesian-workflow/scripts` | arviz, arviz-stats, numpy, xarray | matplotlib | default |
| `brainstorming` | `skills/brainstorming/scripts` | — | — | default |
| `build` | `build` | numpy, polars, pyyaml | arviz>=1.0, arviz-base, arviz-stats, arviz-plots, numpyro, jax, matplotlib | default |
| `cc-guide` | `build/cc_guide` | — | — | default |
| `classification-codes` | `skills/classification-codes/scripts` | polars | — | default |
| `describe-critique-methodology` | `skills/describe-critique-methodology/scripts` | — | — | default |
| `design-architecture` | `skills/design-architecture/scripts` | — | — | default |
| `explore-data` | `skills/explore-data/scripts` | polars | — | default |
| `geographic-codes` | `skills/geographic-codes/scripts` | polars, fastexcel | — | default |
| `hooks` | `hooks` | — | — | 3.13, /usr/bin/python3 |
| `llm-wiki` | `skills/llm-wiki/scripts` | — | — | default |
| `recommend-probabilistic-model` | `skills/recommend-probabilistic-model/scripts` | numpy, polars | — | default |
| `recommend-visualization` | `skills/recommend-visualization/scripts` | numpy, polars | — | default |
| `subagent-driven-development` | `skills/subagent-driven-development/scripts` | — | — | default |
| `systematic-debugging` | `skills/systematic-debugging` | — | — | default |
| `track-model-experiments` | `skills/track-model-experiments/scripts` | numpy, polars, arviz, numpyro, h5netcdf, h5py | — | default |
| `tune-hyperparameters` | `skills/tune-hyperparameters/scripts` | numpy, polars | scikit-learn, optuna | default |
| `writing-plans` | `skills/writing-plans/scripts` | — | — | default |

The notes carry the rest of each comment. Examples: `build`'s missing `build/.scratch/` in a fresh clone or
worktree; `bayesian-workflow`'s `CALIBRATION_SWEEP=1` sweep and its expected arviz warnings; `llm-wiki`'s
`@needs_pilot` tests and `$LLM_WIKI_ROOT`; `brainstorming`'s node skip; `tune-hyperparameters`'
"`--with sklearn` fails"; `track-model-experiments`' run time; the guard's 3.9 floor, its launchd-PATH skips
and its Gate B probe for `hooks`.

### R3 — The runner: `build/run_suites.py`

R3.1 Stdlib only (`tomllib`, `argparse`, `subprocess`, `shlex`), Python 3.13. Invoked as
`uv run --python 3.13 python build/run_suites.py …` from any directory. It finds the repo root from its
own path, never from the working directory.

R3.2 **One run** is one interpreter of one suite. Its command is
`uv run --python <python> --with <dep> … python -m pytest -q [<args>]`, run with the suite's `dir` as its
working directory. Its shell form is `cd <dir> && <command>`, with shell quoting where a word needs it. With
default options, the shell form equals the suite's current `CLAUDE.md` command, character for character.
For `hooks`, whose line chains two runs as `cd hooks && A && B`, the two shell forms are `cd hooks && A`
and `cd hooks && B`.

R3.3 **`--list [NAME …]`** prints, for each named suite (default: all): its name and directory, the shell
form of each run, its extras, and its notes. `--extras` and the `--` arguments apply here too, so `--list`
prints the exact command that a run would use.

R3.4 **`NAME [NAME …]`** runs the named suites, in the order given, one run per interpreter in `pythons`.
Each run starts with a `== <name> (<python>)` header, and the suite's notes follow its first run's header.
Then pytest's output streams. A failed run does not stop the next one.

R3.5 **`--extras`** adds each suite's `extras` after its `with` deps. Arguments after **`--`** go to pytest
(a test node ID, `-k`, `-s`, `-rs`) in every run.

R3.6 **`--all`** runs every suite except one whose `dir` lies inside another suite's `dir`. Today that is
`cc-guide`: `cd build && pytest` collects `build/cc_guide` already. `--all` prints one line for each suite
that it skips. A suite named on the command line always runs.

R3.7 **Exit status:** 0 when every run exits 0; 1 when any run fails (pytest's exit 5, no tests collected,
counts as a failure); 2 for a usage error, an unknown suite name, or a registry that fails validation. The
last line names the failed runs, or says that every run passed. A run whose `uv` cannot start counts as
failed.

R3.8 The runner passes its environment to every run unchanged. `CALIBRATION_SWEEP=1 uv run --python 3.13
python build/run_suites.py bayesian-workflow -- -s` therefore runs the sweep.

R3.9 Validation fails closed. An unknown key, a missing required key, a wrong type, a duplicate name or
directory, or a `with` list without `pytest` stops `--list`, a named run and `--all` with exit 2. `--check`
reports the same failures as findings (R4.3). A misspelled key can therefore never run a suite without its
deps.

### R4 — The guard: `run_suites.py --check`

R4.1 `--check` reports two kinds of findings:
- **registry:** R3.9's validation, plus a registered `dir` that does not exist or holds no pytest file;
- **coverage:** a directory that holds a pytest file (`test_*.py` or `*_test.py`, pytest's default
  patterns) and does not lie inside any registered `dir`.

R4.2 The file list is `git ls-files --cached --others --exclude-standard`, run at the repo root. Ignored
trees, `.claude/worktrees/` and `build/.scratch/` among them, drop out. Untracked new suites count, as the
hook's other lints read untracked drafts too. If git fails, `--check` fails.

R4.3 Output: `suite registry ok` and exit 0, or one line per finding and exit 1.

R4.4 `build/run_commit_lints.sh` runs it as the ninth lint, named `suite_registry`:
`run suite_registry uv run --python 3.13 python build/run_suites.py --check`. Its header says "nine".

### R5 — `CLAUDE.md` and the other edits

R5.1 `CLAUDE.md`, from `main` at `456e3fb`:

| Lines | Change |
|---|---|
| 60 | Rewrite the intro paragraph. Drop "There is no root test runner" and the sentence that comments name the skip-unlocking deps. Keep the uv and Python 3.13 rule, the directory scope, and the `test_build.py` basename-collision reason. Name `build/suites.toml` and `build/run_suites.py`, and say that the runner prints a suite's notes before it runs. One line. |
| 66–125 | Replace with one block: a comment, then the `--list`, `<name> [--extras] [-- <pytest args>]`, `--all` and `--check` commands. |
| 127–132 | The commit-lint comment names the suite-registry check and says "nine". Same number of lines. Line 133 is not touched (plan 53's Task 7 edits it). |
| 141–145 | Drop line 145, the `cd build/cc_guide && …` command. The comment names the suite `run_suites.py cc-guide` instead of "its suite". |

The file ends at about 145 lines. The new text states no count of suites or tests (the
`claude-md-count-claims` check).

R5.2 The deletion of lines 66–125 is bounded by two lines that no other plan edits: the
`# Full build-directory tests` comment and the `cd hooks && …` command. Whatever lies between them goes, so
the edit works in either landing order with plan 52 (R7.1).

R5.3 `build/CLAUDE.md`: "the eight commit lints" becomes "the nine commit lints", and one sentence names
`suites.toml` and `run_suites.py` and says that `--check` is a commit lint.

R5.4 `build/test_check_conformance.py`: `test_claude_md_import_resolves_passes_on_the_repo` asserts
`'@needs_pilot' in text` as its positive control, and that note moves to the registry. The control becomes
a check that line 1 is the `<!-- cc-guide: … @<version> -->` stamp. A naive scan would flag the `@` in it,
and the stamp keeps its form when its version changes.

R5.5 No change to `AGENTS.md`, `GEMINI.md`, `.github/workflows/lints.yml`, `install.py` or `NOTICE`. The new
files are the owner's original tooling. The register's deviation `claude-md-serves-codex-gemini` still holds
as written: a condensed Commands block stays in the root file, and the registry is a plain file that every
runtime can read.

### R6 — Tests

R6.1 `build/test_run_suites.py`, stdlib and pytest only, which the build suite collects. It covers:
- validation: each R3.9 failure, with exit 2;
- commands: the default argv and shell form, two `pythons` runs, `--extras`, `--` arguments, quoting;
- `--list` output for a fixture registry;
- the `--all` nesting rule, and that a named nested suite runs;
- running, through an injected run function so the tests start no real `uv`: every run happens after a
  failure; exit 0, 1 and 2; exit 5 counts as failed; the notes print before the first run;
- `--check` on throwaway git repos: an unregistered test directory, a missing registered directory, a
  registered directory without tests, an ignored directory (no finding), an untracked test directory
  (a finding);
- the real registry: `--check` passes on the repo.

R6.2 `build/test_commit_lints.py`: `suite_registry` joins `CHECKS`, and `test_unregistered_suite_is_refused`
commits a new `skills/<name>/scripts/test_new.py` in a clone and asserts that `suite_registry` is the only
failed lint.

R6.3 Write each test before its code and see it fail first (red, then green).

### R7 — Couplings with other plans

R7.1 **Plan 52 (write-with-asd-ste100).** Under decision 2, plan 52's Task 6 drops its
`CLAUDE.md:commands-moved` and `CLAUDE.md:commands` edits and adds one `[[suite]]` entry for
`skills/write-with-asd-ste100/scripts` instead. Its expectations of 199 and 197 lines (Task 1, DF19, Q4,
Coupling (e)) change with it. Its `CLAUDE.md:sources` and `CLAUDE.md:bullet` edits are outside the Commands
block and still apply. A note in the session group's shared notes folder gives the exact entry. Until plan 52
adds the entry, the ninth lint refuses its new suite directory. If plan 52 lands first after all, R5.2's
deletion still works, and this plan registers that suite itself.

R7.2 **Plan 53 (agent-skills portability).** None of the lines that R5.1 deletes carries one of its edit
anchors. Its Task 7 edits line 133, which stays. Its own suite commands are written out in full in the
plan, so they work without `CLAUDE.md`.

R7.3 **Plan 51 (drift automation, rebaseline pin).** It edits one sentence of `build/CLAUDE.md`'s
`cc_guide/` paragraph. R5.3 edits the `run_commit_lints.sh` paragraph and adds a sentence. If an edit block
does not match, merge by hand.

## Testing

- **R6's tests** run red first, then green.
- **The Stage 2 audit** (one time, a scratch script that is never committed, as in plan 38's Task 2). Run it
  before the `CLAUDE.md` deletion. It extracts every `cd <dir> && uv run …` command from lines 66–125 and
  145, splitting the hooks `&&` chain into one command per run. It asserts that the set equals the set of
  default shell forms that `--list` prints: nothing is missing on either side. It also checks each comment's
  skip-unlocking deps against that suite's `extras`.
- **Behaviour.** Run `hooks`, `build` and `bayesian-workflow` once directly and once through the runner, in
  the same checkout. Their pytest summary lines match. Then run `--all` once, and record each run's result
  beside the direct result.
- **Gates.** `uv run --python 3.13 python build/run_suites.py --check` prints `suite registry ok`. The
  build suite passes (where the missing `build/.scratch/` lets it). `bash build/run_commit_lints.sh` prints
  `commit lints passed`.

## Done when

1. `build/suites.toml` registers every directory suite (R2.3) and `--check` passes.
2. `build/run_suites.py` and its tests are committed, and the ninth lint runs in `run_commit_lints.sh`.
3. The Stage 2 audit passes, and the behaviour runs match.
4. `CLAUDE.md` has no directory-suite command left (R5.1) and stays under 200 lines.
5. `bash build/run_commit_lints.sh` prints `commit lints passed`.
6. The shared note for plan 52 (R7.1) is written.

## Consequences to know

- Agents no longer see each suite's notes at session start. They see them in `--list`, and the runner
  prints them before it runs a suite.
- No commit can add a test directory without a registry entry, plan 52's new suite included.
- The commit hook runs one more fast, stdlib-only check.
- Codex and Gemini reach the runner commands through `AGENTS.md` and `GEMINI.md`, as before.

## Out of scope (deferred items)

- CI running the suites (`--all` in `.github/workflows/lints.yml`). It would need node, a 3.9
  `/usr/bin/python3` and `build/.scratch/`. Size: design. Revisit if: the owner wants suites in CI.
- Parallel runs, per-suite timeouts and machine-readable output. Size: plan. Revisit if: `--all` gets slow
  or a tool needs to parse its results.
- Moving the lint, snippet, JAX, smoke, rebuild and citation commands into the runner. Size: design.
  Revisit if: `CLAUDE.md` nears its limit again.

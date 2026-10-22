# Package versions: one source for every pinned or cited version

**Status:** design agreed with the owner section by section on 2026-10-21. The written spec awaits the owner's review. Next skill: writing-plans.

## Problem

The repo fixes package versions by hand in many places, and nothing ties the copies together. On 2026-10-21 the owner found NumPyro at 0.21.0 in one deferred item and at 0.22.0 in `PINNED`. The owner wants one mechanism for every package that a skill names or runs, the Python interpreter included. It must give one or both of these properties:

1. A way to always use the latest release.
2. The version as a parameter, set in one place and not copied by hand.

This work is not part of plan 64 (bayesian-workflow and recommend-probabilistic-model routing).

## Inventory (2026-10-21, branch `claude/admiring-haslett-c81ea8` at 7612c6e)

"Version" has four roles here. They change for different reasons, so the design keeps them apart.

### Role 1. Gate pins: the versions that a repo gate verifies against

| Where | What | Notes |
|---|---|---|
| `build/snippet_preamble.py:199-203` | `PINNED`: arviz==1.3.0, arviz-stats==1.3.3, arviz-plots==1.3.2, numpyro==0.22.0, jax==0.12.0. arviz-base, numpy and matplotlib float | The Tier 3 snippet gate (`check_snippets.py --run`, which executes the bayesian-workflow code blocks). Comment: "Verified resolving 2026-10-19" |
| `build/check_snippets.py:87-90` | `RUN_REMEDIATION` builds the Tier 3 command from `PINNED` | Already a single source in code |
| `CLAUDE.md:122` | The Tier 3 command, with the `PINNED` versions copied by hand | No check compares it with `PINNED` (deferred item F9, done 2026-10-19, says so) |
| `build/check_snippets.py:84-86`, `CLAUDE.md:120` | Tier 2 (`--api`, which resolves library names) floats: `arviz>=1.0` and unpinned rest | Floats by design |
| `specs/verification/32-jax-cpu.in` -> `32-jax-cpu.txt` | Full lock for the deep-learning CPU examples: jax==0.11.2, jaxlib==0.11.2, flax==0.12.10, optax==0.2.8, orbax-checkpoint==0.12.6, equinox==0.13.8, diffrax==0.7.2, e3nn-jax==0.21.0, numpy==2.5.3, plus transitive pins | Made by `uv pip compile --python-version 3.13`. Run by `CLAUDE.md:130` (`check_jax_examples.py`) |
| `build/suites.toml` | `with` and `extras` deps for each test suite, all unpinned (`build` extras: `arviz>=1.0` and the rest bare) | Float |

Conflict: the two gates pin different JAX releases. The CPU lock has 0.11.2 and `PINNED` has 0.12.0.

### Role 2. Interpreter versions

The interpreter is not one value. Three separate roles exist:

| Role | Value | Where |
|---|---|---|
| Dev and gate interpreter | 3.13 | `--python 3.13` in 26 lines of `CLAUDE.md`, 9 of `build/run_commit_lints.sh`, `build/githooks/pre-commit:15`, `build/cc_guide/notice.sh:114`, `build/cc_guide/lint.py:12`, `build/run_suites.py:35` (`DEFAULT_PYTHONS`), the usage docstrings of most `build/*.py` files and of about 13 skill test files, `skills/geographic-codes/SKILL.md:250`, `skills/classification-codes/SKILL.md:246`, `skills/writing-skills/SKILL.md:292`, `hooks/README.md:195`, `AGENTS.md`, `GEMINI.md`, `NOTICE`, `.claude/skills/cc-guide/SKILL.md`. Also `32-jax-cpu.txt` (compiled for 3.13) and `rules/clean-code-python.md:30` ("agent-skills: 3.13; work repos: 3.12") |
| Floor that skill scripts promise users | 3.11 or 3.12 | `requires-python` in 18 script headers under `skills/*/scripts/` (3.12 for the arviz scripts, 3.11 for the rest). `compatibility:` frontmatter in 12 `SKILL.md` files (`Python 3.11+` or `3.12+`). Prose: `recommend-probabilistic-model/SKILL.md:96`, `recommend-visualization/SKILL.md:107`, `document-python-package/SKILL.md:105` |
| Floor for system-Python tools | 3.9 | `install.py` (`install.py:237` handles a 3.9 behavior) and the read-only agent guard (`build/suites.toml`, `hooks` suite: `pythons = ['3.13', '/usr/bin/python3']`) |

Tests assert the dev value in expected strings: `build/test_run_suites.py:79-86,250` and `build/test_check_frontmatter.py:434`.

### Role 3. User floors: what a skill script needs, as `>=` ranges

| Where | Floors |
|---|---|
| `skills/explore-data/scripts/profile.py`, `recommend-visualization/scripts/recommend.py`, `recommend-probabilistic-model/scripts/characterize.py` | `polars>=2.0` |
| `skills/geographic-codes/scripts/build.py`, `classification-codes/scripts/build.py` | `polars>=1.0`, `fastexcel>=0.12` |
| `skills/bayesian-workflow/scripts/diagnose_model.py`, `track-model-experiments/scripts/compare_experiments.py` | `arviz>=1.0`, `numpy>=2.0`, `h5netcdf>=1.0`, `h5py>=3.0` |
| `skills/bayesian-workflow/scripts/calibration_check.py` | `numpy>=2.0`, `arviz-base>=1.0`, `arviz-plots>=1.1`, `arviz-stats>=1.1`, `xarray>=2026.0`, `scipy>=1.0`, `h5netcdf>=1.0`, `h5py>=3.0`, `matplotlib>=3.0` |
| `skills/document-python-package/SKILL.md:13,24,94,105`, `scripts/preflight.py:34` | `great-docs>=0.17.0,<0.18` (an upper bound, tied to a tested range), `numpydoc>=1.11` |
| bayesian-workflow prose: `SKILL.md:34,69,119,121,318`, `references/priors.md:64,71`, `references/diagnostics.md:54`, `README.md:65` | API floors: `arviz-stats >= 1.0.0` for `diagnose`, `NumPyro ≥ 0.22` for `Hurdle*`, the ArviZ ≥ 1.0 stack |

A floor states when an API appeared. A new upstream release does not make it stale.

### Role 4. Prose that cites a version as an observed fact

| Where | Citation | Gate behind it? |
|---|---|---|
| `skills/bayesian-workflow/references/diagnostics.md:49` | NumPyro "checked in the 0.22.0" source | Tier 3 pins 0.22.0 |
| `skills/bayesian-workflow/references/model-comparison.md:130` | "verified on arviz 1.3.0 / arviz-stats 1.3.1" | Tier 3 now pins arviz-stats 1.3.3 |
| `skills/bayesian-workflow/references/model-criticism.md:196` | "arviz-plots 1.3.1" | Tier 3 now pins 1.3.2 |
| `skills/deep-learning/references/frameworks.md:94-95` | A hand copy of the CPU lock's versions, and "Python 3.13.8" | The CPU lock |
| `skills/recommend-visualization/SKILL.md:112`, `README.md:30-31`, `references/altair.md:5`, `references/plotly.md:4`, `references/matplotlib.md:4-5` | "Verified on Polars 1.42, Altair 6.2, matplotlib 3.11, plotly 6.8" | None |
| `skills/explore-data/SKILL.md:83` | "verified on Polars 1.38" | None |
| `skills/tune-hyperparameters/SKILL.md:102` | "verified against Optuna 5.0.0" | None |
| bayesian-workflow porting text: `SKILL.md:59,122,130`, `references/model-comparison.md:74,196`, `references/visualize.md:125`, `references/diagnostics.md:111,175` | "ArviZ 0.23" as the classic stack | History, by design |

Conflict: the Polars citations disagree. explore-data says 1.38, recommend-visualization says 1.42, and three script headers require `polars>=2.0`.

### Records, out of scope for any lint

`specs/deferred_items.md`, `specs/plans/completed/`, `specs/completed/` and `specs/verification/*.md` are dated records. They keep the versions of their day. One open deferred item is stale in a way that misleads: the Gaussian-process item at `specs/deferred_items.md:4492` says "on the pinned 0.21.0".

`skills/evaluate-deep-learning/references/experiments.md:86-87` is an illustrative run manifest, and the `build/test_check_frontmatter.py` header strings are test data.

### Latest releases on 2026-10-21 (PyPI)

| Package | Latest | Uploaded | Repo pin or citation |
|---|---|---|---|
| jax | 0.12.0.1 | 2026-10-21 | 0.12.0 (`PINNED`), 0.11.2 (CPU lock) |
| polars | 2.0.0 | 2026-10-06 | 1.38 and 1.42 cited; `>=2.0` and `>=1.0` floors |
| numpyro | 0.22.0 | 2026-09-18 | 0.22.0 |
| arviz / arviz-stats / arviz-plots / arviz-base | 1.3.0 / 1.3.3 / 1.3.2 / 1.3.1 | 2026-08-11 to 2026-09-25 | same; arviz-base floats |
| flax / optax / equinox | 0.12.10 / 0.2.8 / 0.13.8 | | same as the CPU lock |
| plotly / altair / matplotlib | 7.1.0 / 6.3.0 / 3.11.2 | 2026-09 | 6.8 / 6.2 / 3.11 cited |
| optuna / great-docs | 5.0.0 / 0.17.0 | | same |

A floating gate would have changed today: jax 0.12.0.1 was uploaded on 2026-10-21.

### uv behavior that constrains the design (uv 0.13.1, probed 2026-10-21 in `/tmp/vprobe`)

1. `uv run --exclude-newer <date> --with jax` respects the cutoff. With 2026-10-20 it gave jax 0.12.0, not 0.12.0.1.
2. For a PEP 723 script (`uv run script.py`), the command-line `--exclude-newer` and `UV_EXCLUDE_NEWER` did not limit the header's dependencies. With a 2026-10-01 cutoff it still installed polars 2.0.0 (uploaded 2026-10-06). A `[tool.uv] exclude-newer = "..."` table inside the script header did limit them (polars 1.44.2).
3. With no `--python`, uv picked Python 3.14 for a script, and a bare `polars` header resolved to 1.44.2, not 2.0.0. Under `--python 3.13` it resolved to 2.0.0. So "latest" depends on the interpreter as well as the date.

The plan must re-check items 2 and 3 before it relies on them.

### Related live work

- Plan 63 (conformance gaps, branch `claude/plan-35-conformance-gaps-427f5e`) touches `build/run_commit_lints.sh`, `install.py` and `build/test_runtime_support.py`.
- Plan 64 (bayesian-workflow and recommend-probabilistic-model routing) edits bayesian-workflow prose that holds Role 3 and Role 4 citations.
- The model-lifecycle spec (PR #106) adds bayesian-workflow sections.
- `CLAUDE.md` has 153 lines against a 200-line budget.

## Decisions (owner, 2026-10-21)

| # | Question | Decision |
|---|---|---|
| D1 | How the checks choose versions | Exact pins in one file, plus a separate drift run on the newest releases. Not a floating gate |
| D2 | Pin scope | One version per package for the whole repo. A check differs only through a named override with a reason |
| D3 | Packages the file does not name | One freeze date. Every check resolves as of that date (uv `exclude-newer`). No lock file |
| D4 | Python | The file sets only the dev interpreter. Script floors (3.11, 3.12) and the 3.9 floor stay user promises in their own files |
| D5 | Prose citations | An offline lint compares each version literal in `skills/` with the file |
| D6 | When the drift run happens | On demand, and in a weekly advisory CI job |
| D7 | Shape | One file that a person edits, with synced outputs that uv reads natively, and a `--check` mode as a commit lint |
| D8 | User runs of skill scripts | They float within the header floors. The freeze date covers only the repo's checks |

## Requirements

### R1. The versions file

R1.1. `build/versions.toml` is the only file in which a person sets a package version or the dev interpreter. Its tables:

```toml
[python]
dev = '3.13'                 # repo checks and documented commands

[freeze]
date = 2026-10-19            # a TOML date; every check resolves as of this date

[packages]                   # one exact version each; a check runs these
arviz = '1.3.0'
numpyro = '0.22.0'
jax = '0.12.0'
# ... every package that a [gates] entry or a skill citation names and a check runs

[cited]                      # prose cites these, but no check runs them
altair = '6.2'
plotly = '6.8'
optuna = '5.0.0'
great-docs = '0.17.0'

[gates]                      # the packages each check installs, pinned from [packages]
snippets = ['arviz', 'arviz-base', 'arviz-stats', 'arviz-plots', 'numpyro', 'jax', 'numpy', 'matplotlib']
jax-cpu = ['jax', 'jaxlib', 'flax', 'optax', 'orbax-checkpoint', 'equinox', 'diffrax', 'e3nn-jax', 'numpy']

# [[override]]               # gate, package, version, reason; empty at the start
```

The values above are the 2026-10-21 state. The plan sets the real values with `bump` (R3).

R1.2. A package gets a `[packages]` entry in two cases. The first is when a `[gates]` list names it. The second is when a check installs it and skill text or a script header states a version for it. Polars is in `[packages]` by the second case: the suites install it, and three headers floor it. Other packages (pytest, pyyaml, scipy, tensorstore and the rest) get no entry, and the freeze date fixes them.

R1.3. A package gets a `[cited]` entry when skill prose cites a version for it and no check runs it.

R1.4. A check uses a version other than the `[packages]` value only through an `[[override]]` entry with four keys: `gate`, `package`, `version` and `reason`.

R1.5. The file does not hold the script floors (`requires-python`, `compatibility:`) or the 3.9 floor of `install.py` and the read-only agent guard.

### R2. Synced outputs and readers

R2.1. `build/versions.py sync` writes three files from `build/versions.toml`, and `sync --check` fails when any of them differs:

| Output | Content | Effect |
|---|---|---|
| `.python-version` (repo root) | the `[python] dev` value | Every `uv run` in the repo uses the dev interpreter with no `--python` flag, from any subdirectory |
| `uv.toml` (repo root) | `exclude-newer` set to the freeze date | Every `uv run` from the repo root resolves as of the freeze date, script headers included |
| `skills/uv.toml` | no settings, and a comment that names `build/versions.toml` | It shadows the root date under `skills/`, so a skill script that a user runs floats within its floors (D8), whatever the path form |

`skills/uv.toml` is a file, not a skill. `install.py:97-101`, `build/check_frontmatter.py:574-575` and `build/check_provenance.py:40-44` read only directories that hold a `SKILL.md`, so they skip it. The plan confirms that Claude Code, Codex and Gemini also ignore a plain file in a skills directory.

R2.2. `build/versions.py` gives the other build scripts these values: the dev Python, the freeze date, and `stack(gate)`, the list of `pkg==version` strings for a gate after overrides.

R2.3. These readers take their versions from R2.2 and from no literal:
- `build/check_snippets.py`: `PINNED` (moved out of `build/snippet_preamble.py`), `RUN_REMEDIATION` and `API_REMEDIATION`. Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date.
- `build/check_jax_examples.py` and its documented command: they install `stack('jax-cpu')` in place of `--with-requirements specs/verification/32-jax-cpu.txt`.
- `build/run_suites.py`: `DEFAULT_PYTHONS` comes from the dev Python. A `with` or `extras` package that `[packages]` names gets its pin. Each run passes `--exclude-newer <date>` explicitly, because suites under `skills/` sit below the shadow file. The `hooks` suite keeps its explicit `/usr/bin/python3` run.
- `build/cc_guide/notice.sh:114` and `build/githooks/pre-commit:15`: they can run outside the repo's working directory, so they take the interpreter from the file and not from a literal.

R2.4. Documented commands spell no interpreter or package version. This covers `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `build/run_commit_lints.sh`, the usage docstrings in `build/`, `hooks/` and the skill test files, and the commands in skill text. A command that needs a pinned stack uses the runner (R3):

```bash
uv run python build/versions.py run snippets -- python build/check_snippets.py --run skills/bayesian-workflow/
```

### R3. Operations

R3.1. `build/versions.py` has these subcommands:

| Subcommand | Network | Effect |
|---|---|---|
| `sync [--check]` | no | Writes or checks the R2.1 outputs |
| `run <gate> [--pin pkg==X ...] -- <cmd>` | yes | Runs `<cmd>` under `uv run` with the gate's stack and the freeze date |
| `verify [--pin pkg==X ...]` | yes | Runs the re-verify set on the file's versions: Tier 2, Tier 3, the JAX CPU examples, and `run_suites.py --all --extras` |
| `bump [--date D] [--only pkg ...]` | yes | Sets the freeze date (default: today), re-resolves each `[packages]` entry as of that date, rewrites `[packages]` and runs `sync`. `--only` limits the change to the named packages |
| `drift [--pin pkg==X ...]` | yes | Resolves the newest releases with no freeze date, no pins and the newest stable Python. It reports the pinned version, the latest version and its upload date for each `[packages]` and `[cited]` entry, then runs the re-verify set on the latest versions and reports each gate's result |
| `check` | no | The R4 lint |

R3.2. `bump` never changes `[cited]`. A person changes a `[cited]` entry only after re-checking the cited behavior.

R3.3. `--pin` changes one package for one run and never edits the file.

R3.4. A bump follows these steps, in one change:
1. Run `bump`.
2. Run `verify`.
3. Run `check`, which lists each prose citation that the bump made stale.
4. Re-verify or rewrite each stale citation (R5.5).
5. Commit.

R3.5. Exit codes:
- `run` and `verify` exit non-zero on any failure.
- `drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network. The report states which.
- `bump` exits 2 on a network or resolve failure and names the step.

R3.6. Errors name their cause:
- A missing or invalid file names the key.
- An unknown package in `[gates]` or `[[override]]` names the package.
- An invalid date names the value.
- A pin uploaded after the freeze date names the package and the date.

### R4. The `check` lint

R4.1. `versions.py check` runs offline. It fails on any of these:
1. **Sync.** An R2.1 output differs from the file.
2. **Interpreter literals.** A live file spells `--python 3.<n>`. Live files are `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` and the files under `build/`, `hooks/`, `skills/` and `.claude/skills/`. An interpreter path such as `/usr/bin/python3` is not a literal.
3. **Prose citations.** In `skills/**/*.md` and the script headers under `skills/*/scripts/`, `check` finds each version that stands next to a `[packages]` name, a `[cited]` name or "Python", and classifies it by form:
   - **Equality** ("verified on Polars 1.42", `numpyro==0.22.0`, "checked in the 0.22.0") must equal the file's value at the cited precision.
   - **Range** (`>=`, `≥`, `<`, `,<0.18`, "3.11+") must contain the file's value.
   - **History** ("ArviZ 0.23", "and earlier") passes only through the `HISTORICAL` allowlist.
4. **Floors.** Each script's `requires-python` must match the Python floor in its `SKILL.md` `compatibility:` line. The dev Python must satisfy each floor.

R4.2. `HISTORICAL` is keyed by the literal phrase, not by file and line, and each entry gives its reason. It follows the model of `DOCUMENTED_ABSENT` in `build/check_snippets.py`.

R4.3. `check` does not read `specs/`, `LICENSE*` files, `data/` directories or test fixtures. Illustrative text, such as the run manifest at `skills/evaluate-deep-learning/references/experiments.md:86-87`, goes on `HISTORICAL` with a reason.

R4.4. Known limit: `check` sees only the package names that the file lists. The `drift` report states this limit.

### R5. Commit lints and CI

R5.1. `versions_check` (`uv run python build/versions.py check`) becomes the tenth commit lint in `build/run_commit_lints.sh`. `CLAUDE.md`'s count of commit lints, `build/githooks/pre-commit` and `build/test_commit_lints.py` change with it.

R5.2. `.github/workflows/lints.yml` keeps its steps. `setup-uv` takes the interpreter from `.python-version`.

R5.3. A new workflow, `.github/workflows/versions-drift.yml`, runs `versions.py drift` weekly on a cron schedule and on manual dispatch. It follows these rules:
- It has `permissions: contents: read`, and it pins its actions by SHA, as `lints.yml` does.
- It writes the drift report to the job summary.
- The job may go red, but it is not a required check.
- It never opens an issue or a PR, and it never commits.

R5.4. Known limit: GitHub disables scheduled workflows in a public repository after 60 days with no activity. The spec accepts this. It does not work around it.

### R6. Migration

The first plan does these, in order:
1. Re-probe the four uv behaviors in the Inventory (date reach to script headers, the command-line flag's miss on headers, the shadow file, and `.python-version` discovery from subdirectories) on the uv version of the day. Record the results in `specs/verification/`. If a behavior changed, stop and bring the change to the owner before going on.
2. Write `build/versions.toml`, then run `bump` and `verify` on the day of execution.
3. Use one JAX version for both gates. The JAX CPU examples must pass on it. If they fail, add a temporary `[[override]]` for `jax-cpu` with its reason, and log a deferred item to remove it.
4. Pin Polars at the latest release (2.0.0 on 2026-10-21). This keeps the `polars>=2.0` floors that the portability plan set on purpose (`specs/plans/completed/53-agent-skills-portability.md`, decision DF4).
5. For each stale citation, either re-verify the cited behavior on the file's version and update the citation, or move it to `HISTORICAL` with the reason "verified on X, not re-checked on Y" and log a deferred item to re-check it. Never change a citation's version without a re-check. The known stale citations are the Polars, Altair and plotly lines, `skills/bayesian-workflow/references/model-comparison.md:130`, `references/model-criticism.md:196` and `skills/deep-learning/references/frameworks.md:94-95`.
6. Correct the open Gaussian-process item at `specs/deferred_items.md:4492`, which says "on the pinned 0.21.0".
7. Retire `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt`, and point their readers at `build/versions.toml`. The plan-32 verification records keep their old versions as history.
8. Change `rules/clean-code-python.md:30` to name `build/versions.toml` as this repo's source for the target Python.

### R7. Tests

The plan writes each test before its code (red, then green).
- **`versions.py` units.** Cover schema validation, `stack()` with and without an override, and the exact text that `sync` writes.
- **`check` findings.** Cover each form (equality, range, history), the interpreter-literal rule and the floors rule. Each finding has a positive control: a seeded stale literal that must fail.
- **`run_suites.py` tests.** `build/test_run_suites.py` and `build/test_check_frontmatter.py:434` build their expected commands from the file, not from a `3.13` literal.
- **Exit codes.** Test the `drift`, `verify` and `bump` exit codes against a stub uv, as `hooks/test_project_hooks.py` does.

## Out of scope

- GitHub Action SHAs, the uv version, Claude Code binaries and Node.
- The data-source vintages in geographic-codes and classification-codes.
- The upstream Great Docs skills that `skills/document-python-package/scripts/preflight.py` fetches.
- Dated records in `specs/`.
- Raising user floors automatically.

## Provenance and conformance

No third-party text enters the repo, so `NOTICE` and the license files do not change. The `CLAUDE.md` edits follow the guide sections that `build/cc_guide/conformance.toml` maps to `CLAUDE.md`, and `check_conformance.py` runs before each commit.

## Order with other work

- **Plan 63.** It edits `build/run_commit_lints.sh`. This work lands after plan 63, or the plan that lands second rebases onto the other and re-reads the anchors.
- **Plan 64 and the model-lifecycle spec.** They edit bayesian-workflow prose that holds Role 3 and Role 4 citations. The R6 prose fixes rebase onto them and re-take the line numbers.
- **`CLAUDE.md` line budget.** R2.4 removes the version flags from the commands, so `CLAUDE.md` gets shorter.

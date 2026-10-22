# Package versions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put the dev Python, one freeze date and every pinned or cited package version in one file, `build/versions.toml`. Make every check, command and lint read them from that file.

**Architecture:** `build/versions.py` (standard library only) reads the file. Its `sync` subcommand writes `.python-version`, `uv.toml` and `skills/uv.toml`. Its `run`, `verify`, `bump` and `drift` subcommands run commands on a pinned stack, re-pin by one joint resolve, and report drift. A second module, `build/versions_check.py`, is the offline `check` lint and becomes the tenth commit lint. `check_snippets.py` and `run_suites.py` take their pins from the file. A weekly advisory workflow runs `drift`.

**Tech Stack:** Python standard library (`tomllib`), uv, pytest, GitHub Actions. No new third-party package.

**Spec:** `specs/package-versions.md` (approved by the owner on 2026-10-21, on main since lowmason/agent-skills#109). Read it first. This plan argues from it.

**Plan id:** 66. It was claimed on 2026-10-21 with `skills/writing-plans/scripts/entry_check.py` (plans 63 and 64 are live, and 65 is the model-lifecycle plan).

## Labels used in this plan

- **R1 to R7** are the spec's requirement groups. R1 is the versions file. R2 is the synced outputs and the readers. R3 is the subcommands. R4 is the `check` lint. R5 is the commit lints and CI. R6 is the migration order. R7 is the tests.
- **D1 to D8** are the owner decisions in the spec's table "Decisions (owner, 2026-10-21)".
- **Q1 to Q8** are the open questions in this plan. **A1 to A3** are the spec amendments that Tasks 1, 4 and 6 apply.
- **Gate** means a check that runs on a named list of packages. The spec has two: `snippets` (the Tier 2 and Tier 3 snippet checks) and `jax-cpu` (the deep-learning CPU examples).
- **Freeze date** is the day after which uv ignores new package releases. The **cutoff** is its uv form: 00:00:00Z on the day after the freeze date.
- **Joint resolve** means one `uv pip compile` call for all `[packages]` entries together.

## Owner questions (answer at plan review, before execution)

Each question has a recommended default. The tasks are written for the defaults. An answer that differs edits the plan, not the work.

**Q1. Two facts in the spec's uv list look wrong (Task 1).** While drafting this plan I re-ran the spec's probe with uv's cache switched off (`uv --no-cache`). Items 2 and 3 of the spec's list then came out differently. With the cache on, uv reuses a cached environment whose requirements match, whatever freeze date built it. That reuse most likely caused the old results. The table below shows the difference.

| Spec item | Spec says | Cache off (draft run, uv 0.13.1) |
|---|---|---|
| 2 | `--exclude-newer` and `UV_EXCLUDE_NEWER` do not limit a script header | Both limit it (polars 1.44.2 with a 2026-10-01 cutoff) |
| 3 | A bare `polars` header gives 1.44.2 on Python 3.14, cause unknown | It gives 2.0.0 on 3.13 and on 3.14. The 1.44.2 came from a cached environment |

The design still holds. The root `uv.toml` still reaches script headers, `skills/uv.toml` still shadows it, and an explicit `--exclude-newer` also works on scripts now.
- **Default:** Task 1 re-runs the probe. If its table matches the forecast in "Forecast for Task 1", it applies amendment A1 (exact wording in Task 1). Then it goes on without a second stop.
- **Alternative:** stop after the Task 1 run and wait for your answer.

**Q2. Which table holds each package? (Task 4)** R1.2 puts a package in `[packages]` in two cases. A gate names it. Or a check installs it, and skill text or a script header states a version for it. I applied that rule to the repo. The result differs from the example in R1.1 in one place: optuna. The `tune-hyperparameters` suite installs optuna and its `SKILL.md` cites "Optuna 5.0.0", so R1.2 puts it in `[packages]`, but the R1.1 example lists it under `[cited]`.

| Package | Why it is in `[packages]` |
|---|---|
| arviz, arviz-base, arviz-stats, arviz-plots, numpyro, jax, numpy, matplotlib | `snippets` gate |
| jaxlib, flax, optax, orbax-checkpoint, equinox, diffrax, e3nn-jax | `jax-cpu` gate (numpy and jax also) |
| polars | The suites install it. Three script headers floor it (`polars>=2.0`). Prose cites it |
| xarray, h5netcdf, h5py | The bayesian-workflow and track-model-experiments suites install them. Script headers floor them |
| fastexcel | The geographic-codes suite installs it. Two script headers floor it |
| optuna | The tune-hyperparameters suite installs it with `--extras`. `SKILL.md` cites it |

`[cited]` holds altair, plotly and great-docs (prose cites them, no check installs them). Not listed anywhere: pytest, pyyaml, scipy, scikit-learn (R1.2 gives them no entry, and the freeze date fixes them).
- **Default:** use the table above. Task 4 applies amendment A2, which moves optuna in the R1.1 example from `[cited]` to `[packages]`.
- **Alternative:** keep optuna in `[cited]`. Then no check pins it, and "Optuna 5.0.0" is compared with the cited value only.

**Q3. What to do with each stale citation (Task 11).** The draft `check` run on today's tree finds 12 stale citations. R6.5 gives two options for each: re-check the claim and update the text, or move it to `HISTORICAL` with a reason and log a deferred item. It forbids changing a version without a re-check.

| Citation | Default |
|---|---|
| `model-comparison.md` "arviz-stats 1.3.1" | Re-check with a short script (the three `loo_*` names are the same objects in `az` and `azs`). Update the text |
| `model-criticism.md` "arviz-plots 1.3.1" | Re-run the call that line 196 describes and inspect the figure. Update the text. If the inspection is not conclusive, use `HISTORICAL` and a deferred item |
| `frameworks.md` (JAXlib, Orbax checkpoint, NumPy, Python 3.13.8) | `verify` runs the six CPU examples on the file's versions. Rewrite the sentence from the file |
| `diagnostics.md` "checked in the 0.22.0 source" | Check the claim on the pinned NumPyro with a short script. Move the name next to the version so `check` sees it |
| `explore-data/SKILL.md` "Polars 1.38" | Run the "Polars idioms" block on the pinned Polars with a synthetic file. Update the text |
| `recommend-visualization` "Polars 1.42" (five places) | `HISTORICAL` with the reason "verified on 1.42, not re-checked on 2.x", and a deferred item. The claims need real charts in four libraries |

- **Alternative:** re-check everything now. This is slow, because the visualization claims need real rendering.

**Q4. Rule for script Python floors (Task 9).** R4.1 says each script's `requires-python` "must match" the floor in its `SKILL.md` `compatibility:` line. The draft run found a case where a strict match fails. `skills/bayesian-workflow/scripts/check_diagnostics.py` uses only the standard library and says 3.11, but its skill promises 3.12+ (the arviz scripts need 3.12).
- **Default:** the lint fails in two cases. A script needs a higher Python than its skill promises (a broken promise). Or any floor is above the dev Python. A lower script floor passes.
- **Alternative:** strict match. Then change `check_diagnostics.py` to 3.12 or the skill's promise to 3.11.

**Q5. How `suites.toml` names the dev Python (Task 7).** R2.3 says `DEFAULT_PYTHONS` "comes from the dev Python". A suite that lists its own interpreters (the `hooks` suite) needs a way to say "the dev Python, and also `/usr/bin/python3`".
- **Default:** the word `dev` in a suite's `pythons` list means the dev Python. A suite without `pythons` gets `['dev']`. The `hooks` suite becomes `['dev', '/usr/bin/python3']`.
- **Alternative:** a separate key such as `extra_pythons`.

**Q6. Tier 2 of the snippet gate (Task 6, amendment A3).** R2.3 says Tier 2 "stays unpinned for named packages and gets the freeze date". R2.4 says no documented command spells a package version, and an unpinned Tier 2 command would spell `arviz>=1.0`. The two rules conflict.
- **Default:** Tier 2 runs on the pinned `snippets` stack, like Tier 3. The documented command uses the runner. A3 rewrites the R2.3 sentence. Pinned Tier 2 is also what `verify` needs ("on the file's versions").
- **Alternative:** keep Tier 2 floating, and let a CLAUDE.md command spell the floors. This breaks R2.4.

**Q7. Hand copies of the dev Python outside commands (Task 13).** `CLAUDE.md` says "target Python 3.13" (Conventions) and "pinned to the Homebrew Python 3.13" (Commands). `rules/clean-code-python.md` names 3.13 (R6.8 covers this one). `README.md:23` names Python 3.13 in a public statement of the stack.
- **Default:** Task 13 rewrites the two `CLAUDE.md` places to point at `build/versions.toml`. R6.8 handles the rules file. `README.md` stays as it is, because the `check` lint reads `skills/` only. You change the README by hand when the dev Python changes.
- **Alternative:** also point the README at the file.

**Q8. What "retire" means for `specs/verification/32-jax-cpu.in` and `.txt` (Task 12).** Four dated records link to these files and quote their SHA-256 sums. Deleting the files breaks the links.
- **Default:** `git mv` both files to a new `specs/verification/completed/` directory (the repo's convention for retired files). Content stays byte-identical, so the sums stay valid. Task 12 re-points the record links.
- **Alternative:** `git rm` both files and turn the four links into plain text.

## Defaults for your review

These are plan-level choices. They need no answer unless you object.

- The `check` lint lives in its own module, `build/versions_check.py`, so `versions.py` stays small. `versions.py check` calls it.
- `run` and `verify` ask PyPI for the upload time of every pinned version before they start (R3.6, "a pin uploaded after the freeze date"). This costs about one request for each package.
- `drift` runs two passes: the dev Python, then the newest stable CPython that uv can download (prereleases and free-threaded builds left out). It skips the second pass when both are the same. It sets `UV_NO_CONFIG=1` for the re-verify steps and uses `uv --no-config pip compile` for its resolve, so the repo's `uv.toml` does not apply.
- `run` and `verify` take two extra options besides `--pin`: `--python` and `--no-freeze`. `run_suites.py` takes `--pin`, `--python` and `--no-freeze`. `drift` needs them for its second pass.
- `verify` needs gates named exactly `snippets` and `jax-cpu`. A file without them fails with a message that names the gate.
- `check` skips `data/` directories, `fixtures/` directories and `LICENSE*` files (R4.3).
- `cc_guide/notice.sh` and the pre-commit hook take the interpreter from `.python-version` through uv. `notice.sh` uses `uv run --directory <repo root>`, because it can run outside the repo. The hook already changes into the repo root.

## Global Constraints

Every task's requirements include this section.

- **One file.** `build/versions.toml` is the only file in which a person sets a package version or the dev interpreter (R1.1). Tables: `[python]` (`dev`), `[freeze]` (`date`, a TOML date), `[packages]` (one exact version each), `[cited]` (prose cites these and no check runs them) and `[gates]` (the packages each check installs, pinned from `[packages]`). Optional `[[override]]` entries come after them.
- **Overrides.** A check uses a version other than the `[packages]` value only through an `[[override]]` with four keys: `gate`, `package`, `version` and `reason` (R1.4).
- **One version for the whole repo.** Each package has one version (D2). The file does not hold script floors (`requires-python`, `compatibility:`) or the 3.9 floor of `install.py` and the read-only agent guard (R1.5, D4).
- **Freeze.** `uv.toml` sets `exclude-newer` to the RFC 3339 timestamp of 00:00:00Z on the day after the freeze date (R2.1). `skills/uv.toml` sets nothing and shadows the root date, so a user run of a skill script floats within its own floors (R2.1, D8).
- **No literals in documented commands.** Documented commands spell no interpreter or package version (R2.4).
- **Operations.** `bump` never changes `[cited]` (R3.2). `--pin` changes one package for one run and never edits the file (R3.3).
- **Exit codes (R3.5).** `run` and `verify` exit non-zero on any failure. `drift` exits 0 when each gate passes on the latest versions, 1 when a gate fails, and 2 when it cannot resolve or reach the network. `bump` exits 2 on a network or resolve failure and names the step.
- **Errors name the cause (R3.6).** A missing or invalid file names the key. An unknown package names the package. An invalid date names the value. A pin uploaded after the freeze date names the package and the date. A failed joint resolve names the packages in conflict.
- **The `check` lint (R4).** It runs offline and fails on four things: sync, interpreter literals, prose citations and floors. `HISTORICAL` is keyed by the literal phrase and gives a reason for each entry. `check` does not read `specs/`, `LICENSE*` files, `data/` directories or test fixtures. It sees only the package names that the file lists.
- **Tests (R7).** Write each test before its code and watch it fail. Each `check` finding has a positive control (a seeded stale literal that must fail). Test the `drift`, `verify` and `bump` exit codes against a stub uv, as `hooks/test_project_hooks.py` does. State test-count changes as `+N` deltas, never as absolute totals.
- **Citations.** Never change a citation's version without re-checking the cited behavior on the new version (R6.5).
- **Provenance.** No third-party text enters the repo, so `NOTICE` and the license files do not change. Run `check_provenance.py` before each commit that touches `skills/`.
- **CLAUDE.md.** Edits follow the guide sections that `build/cc_guide/conformance.toml` maps to `CLAUDE.md`. Run `check_conformance.py` before each commit that touches it. The file stays under 200 lines.
- **Style.** The two new modules use only the standard library. Single quotes. A test source must not spell a flag and a Python version together (the `check` lint reads `build/`), so build any seeded text from parts. Test and module basenames stay unique across `build/`.
- **Commits.** One commit for each task, with the session's `Co-Authored-By` trailer. Run `bash build/run_commit_lints.sh` before each commit once Task 14 has wired the tenth lint. Before that, run the lints that apply.
- **No push, no PR.** Do not push or open a PR without the owner's go-ahead.

## Decisions

None. The owner has not yet answered Q1 to Q8. Log each answer here as `- **D<n>** (owner, plan review, YYYY-MM-DD): <decision>. Applied in: <Task N>.`

## Order with other work

- **Plan 63 (`claude/plan-35-conformance-gaps-427f5e`).** It does not edit `build/run_commit_lints.sh`. It only runs it, so there is no textual conflict in that file. Three overlaps remain. First, it creates `hooks/dispatch-model-guard.py` and `hooks/test_dispatch_model_guard.py`. Their docstrings probably spell an interpreter flag. If plan 63 lands after this plan, those files fail the tenth lint until they drop the flag, so its executor runs `versions.py check` and fixes them. If plan 63 lands first, Task 13 sweeps them. Second, it edits `build/test_check_frontmatter.py` (a roster test), and Task 13 changes one string in that file. Re-read the anchor. Third, plan 63's own text says "nine commit lints". After this plan lands there are ten. That text is in `specs/plans/`, which no lint reads.
- **Plan 64 (`claude/bayesian-rpm-routing-d9344e`).** It edits bayesian-workflow prose that holds version citations and adds a Gaussian-process reference with runnable NumPyro code. Its Global Constraints tell its executors to run CLAUDE.md's Tier 3 command and to read `PINNED` in `build/snippet_preamble.py`. Task 6 of this plan removes `PINNED` and rewrites that command. Whichever plan lands second re-reads its anchors. Plan 64's completion ticks the open Gaussian-process item in `specs/deferred_items.md`. If it has done so before Task 12 runs, skip Task 12 step 1.
- **Plan 65 and the model-lifecycle spec (`claude/model-lifecycle-roadmap-70da97`).** The lifecycle spec owns `skills/bayesian-workflow/references/model-comparison.md` (its R19). Task 11 changes one citation in that file. Re-read the line.
- **Rule for this plan.** Tasks 1 to 10 touch only `build/`, `specs/` and generated root files, so they can run at any time. Task 11 is the first task that edits skill text. It starts with a gate: fetch, see what landed on main, merge main, and re-grep every anchor by its phrase. Do not trust the line numbers in this plan.
- **Known effect after merge.** uv searches parent directories for `uv.toml` and `.python-version`. A worktree under `.claude/worktrees/<name>/` that was made before this plan merged has neither file. It silently inherits the main checkout's freeze date and interpreter until its branch takes the files from main. The probe row N1 shows this.

## File structure

| File | Task | Responsibility |
|---|---|---|
| `specs/verification/66-uv-probe.py` | 1 | The uv re-probe (stdlib only, runs outside the repo) |
| `specs/verification/66-uv-probe.md` | 1 | The recorded result |
| `build/versions.py` | 2, 3, 5, 8, 9 | Load, validate, sync, resolve, bump, run, verify, drift. Entry point of every subcommand |
| `build/test_versions.py` | 2, 3, 5, 8 | Its tests, with a stub uv |
| `build/versions_check.py` | 9 | The `check` lint: four rules and `HISTORICAL` |
| `build/test_versions_check.py` | 9 | Its tests, with positive controls |
| `build/versions.toml` | 4, 10 | The one source |
| `.python-version`, `uv.toml`, `skills/uv.toml` | 4 | Written by `sync` |
| `build/check_snippets.py`, `build/snippet_preamble.py` | 6 | Reader: remediation commands use the runner. `PINNED` goes |
| `build/run_suites.py`, `build/suites.toml`, `build/test_run_suites.py` | 7 | Reader: dev token, pins, cutoff |
| `skills/**` prose, `build/versions_check.py` (`HISTORICAL`) | 11 | Stale citations |
| `specs/deferred_items.md`, `specs/verification/*`, `rules/clean-code-python.md` | 12 | R6.6 to R6.8 |
| Live files with an interpreter flag (about 41) | 13 | Remove the flag |
| `build/run_commit_lints.sh`, `build/githooks/pre-commit`, `build/test_commit_lints.py`, `CLAUDE.md`, `build/CLAUDE.md` | 14 | Wire the tenth lint |
| `.github/workflows/versions-drift.yml` | 15 | Weekly advisory job |

## Forecast for Task 1

The draft probe run (uv 0.13.1, 2026-10-21, cache off) gave PASS on every row except these:

- **FAIL:** P2a and P2b. They expected the spec's item 2 ("the command line and the environment do not limit a script header"). Both limited the header.
- **RECORD** (printed, never judged): P3c, P7c and P7d. The design does not rely on them. P3c printed `2.0.0 3.14`, where the spec's item 3 saw 1.44.2.

A table that matches this forecast is "as forecast". Any other FAIL, or a forecast row that changes, stops the plan (Task 1, step 3).

## Tasks

The spec's R6 (migration) fixes an order. First re-probe uv. Then write the file and run `bump` and `verify`. Then unify JAX, pin Polars and fix the citations. Last fix the Gaussian-process item, retire the old lock files and edit the rules file. `bump` and `verify` need code that does not exist yet. So Tasks 2 to 9 build that code between R6 step 1 (Task 1) and R6 step 2 (Tasks 4 and 10). R6 steps 2 to 8 keep their order. Tasks 13 to 15 finish R2.4 and R5, which R6 does not order.

| Task | Does | Spec |
|---|---|---|
| 1 | Re-probe uv. Stop gate. Amendment A1 | R6.1 |
| 2 | `versions.py` core: load, validate, `stack`, `sync` | R1, R2.1, R2.2, R3.6 |
| 3 | `bump` and the joint resolve | R3.1, R3.2, R3.5 |
| 4 | Write `build/versions.toml`, first `bump`, `sync`. Amendment A2 | R6.2 (first half) |
| 5 | `run` and the upload-date check | R3.1, R3.3, R3.6 |
| 6 | `check_snippets.py` reads the file. Amendment A3 | R2.3 |
| 7 | `run_suites.py` reads the file | R2.3 |
| 8 | `verify` and `drift` | R3.1, R3.5 |
| 9 | The `check` lint (library and subcommand, not yet wired) | R4 |
| 10 | Second `bump`, `verify`, JAX in one version, Polars at the latest | R6.2 to R6.4 |
| 11 | Stale citations | R6.5 |
| 12 | Gaussian-process item, retire the lock files, rules file | R6.6 to R6.8 |
| 13 | Remove the interpreter flag everywhere, fix the commands | R2.4 |
| 14 | Wire the tenth commit lint | R5.1, R5.2 |
| 15 | Weekly drift workflow | R5.3, R5.4 |
| 16 | Final checks and hand-over | all |

### Task 1: Re-probe uv, stop gate (spec R6 step 1)

**Files:**
- Create: `specs/verification/66-uv-probe.py`
- Create: `specs/verification/66-uv-probe.md`
- Modify: `specs/package-versions.md` (amendment A1, only if the table is as forecast)

**Interfaces:**
- Consumes: nothing.
- Produces: the recorded uv behaviors that Tasks 2 to 9 rely on. The probe row ids (P1 to P10, S1 to S4, N1, N2) are cited in later tasks.

The probe never writes `uv.toml` or `.python-version` inside this repository. Every sibling worktree under `.claude/worktrees/` would inherit them at once. It builds its tree in the system temp directory. Every uv call runs with `--no-cache`, because uv reuses a cached environment whose requirements match, whatever freeze date built it.

- [ ] **Step 1: Create the probe script.** Write this file exactly.

```python
'''Re-probe the uv behaviors that specs/package-versions.md relies on, on the uv of the day.

    uv run --no-project python specs/verification/66-uv-probe.py [--keep]

It builds a throwaway tree under the system temp directory, never inside this repository, and
never writes a uv.toml or .python-version into the repository: every sibling worktree under
.claude/worktrees/ would inherit them at once. It needs the network (PyPI). Output is a Markdown
table: one row for each probe, with the spec's expected result, the observed one and PASS, FAIL or RECORD.
Exit status 1 when a probe FAILs, 2 when the setup cannot run.

The probes use polars 2.0.0 (uploaded 2026-10-06) and jax 0.12.0 / 0.12.0.1 (the latter uploaded 2026-10-21),
whose upload times do not change. Design: specs/package-versions.md, Inventory ("uv behavior that constrains
the design"); plan: specs/plans/66-package-versions.md, Task 1.
'''
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

CUT = '2026-10-01T00:00:00Z'      # before polars 2.0.0
LATE = '2026-12-01T00:00:00Z'     # after it
SCRIPT = '''\
# /// script
# requires-python = '>=3.11'
# dependencies = ['polars']
# ///
import importlib.metadata as m
import sys
print(m.version('polars'), '%d.%d' % sys.version_info[:2])
'''
SCRIPT_FLOOR = SCRIPT.replace("dependencies = ['polars']", "dependencies = ['polars>=2.0']").replace(
    "print(m.version('polars'), '%d.%d' % sys.version_info[:2])", "print(m.version('polars'))")
SCRIPT_OWN_DATE = SCRIPT.replace('# ///\nimport', f'# [tool.uv]\n# exclude-newer = "{CUT}"\n# ///\nimport')
PRINT_PY = "import sys; print(sys.version_info[0], sys.version_info[1])"
PRINT_POLARS = "import importlib.metadata as m, sys; print(m.version('polars'), '%d.%d' % sys.version_info[:2])"
rows = []


def sh(args, cwd, env=None, stdin=None):
    merged = {k: v for k, v in os.environ.items() if not k.startswith('UV_')}
    merged.update(env or {})
    if args[0] == 'uv':   # uv reuses a cached environment whose requirements match, whatever the date was
        args = ['uv', '--no-cache', *args[1:]]
    done = subprocess.run(args, cwd=cwd, env=merged, input=stdin, capture_output=True, text=True)
    return done.returncode, done.stdout.strip(), done.stderr.strip()


def polars_of(out):
    return out.split()[0] if out.split() else ''


def major(version):
    return int(version.split('.')[0]) if version[:1].isdigit() else -1


def probe(pid, what, expected, args, cwd, check, env=None, stdin=None, record=False, show=None):
    code, out, err = sh(args, cwd, env, stdin)
    observed = (show(out) if show else out.replace('\n', ' / ')) if code == 0 else f'exit {code}: {err.splitlines()[-1] if err else ""}'
    ok = code == 0 and check(out)
    rows.append((pid, what, expected, observed, 'RECORD' if record else ('PASS' if ok else 'FAIL')))
    return out


def older(out):          # limited by the date: polars below 2.0.0
    return major(polars_of(out)) in range(0, 2)


def newest(out):         # not limited: polars 2.0.0 or later
    return major(polars_of(out)) >= 2


def upload_time(package, version):
    url = f'https://pypi.org/pypi/{package}/{version}/json'
    with urllib.request.urlopen(url, timeout=30) as response:
        files = json.load(response)['urls']
    return min(datetime.datetime.fromisoformat(f['upload_time_iso_8601'].replace('Z', '+00:00')) for f in files)


def build(work):
    repo = work / 'repo'
    for rel in ('build', 'skills/demo/scripts', '.claude/worktrees/wt', '.claude/worktrees/wt2', 'other'):
        (work / 'repo' / rel if rel != 'other' else work / 'other').mkdir(parents=True, exist_ok=True)
    (repo / 'uv.toml').write_text(f'exclude-newer = "{CUT}"\n')
    (repo / '.python-version').write_text('3.13\n')
    (repo / 'skills' / 'uv.toml').write_text('# no settings; this file shadows the root uv.toml\n')
    (repo / '.claude/worktrees/wt2/uv.toml').write_text(f'exclude-newer = "{LATE}"\n')
    for rel in ('build/s.py', 'skills/demo/scripts/s.py'):
        (repo / rel).write_text(SCRIPT)
    (repo / 'build/owndate.py').write_text(SCRIPT_OWN_DATE)
    (work / 'neutral.py').write_text(SCRIPT)
    (work / 'floor.py').write_text(SCRIPT_FLOOR)
    (work / 'link-build').symlink_to(repo / 'build')
    (work / 'link-skills').symlink_to(repo / 'skills')
    return repo


def run_all(work):
    repo, other = build(work), work / 'other'
    build_dir, deep = repo / 'build', repo / 'skills/demo/scripts'
    uv = ['uv', 'run']
    # 1 and 7: the cutoff on --with, and what the date compares with
    probe('P1', 'CLI --exclude-newer limits --with (jax)', 'jax 0.12.0, not 0.12.0.1',
          [*uv, '--python', '3.13', '--exclude-newer', '2026-10-20T00:00:00Z', '--with', 'jax', 'python', '-c',
           "import importlib.metadata as m; print(m.version('jax'))"], other, lambda o: o == '0.12.0')
    t = upload_time('polars', '2.0.0')
    before, after = (t - datetime.timedelta(minutes=1)), (t + datetime.timedelta(minutes=1))
    base = [*uv, '--python', '3.13', '--with', 'polars', 'python', '-c', PRINT_POLARS]
    for pid, stamp, check, expected in (('P7a', before, older, 'polars < 2 (cutoff just before the upload)'),
                                       ('P7b', after, newest, 'polars 2.0.0 (cutoff just after the upload)')):
        probe(pid, f'RFC 3339 cutoff {stamp:%Y-%m-%dT%H:%M:%SZ} is read as written', expected,
              [*uv, '--python', '3.13', '--exclude-newer', f'{stamp:%Y-%m-%dT%H:%M:%SZ}', '--with', 'polars',
               'python', '-c', PRINT_POLARS], other, check)
    for pid, zone in (('P7c', 'UTC'), ('P7d', 'Pacific/Kiritimati')):
        seen = []
        for offset in (-1, 0, 1):
            day = t.date() + datetime.timedelta(days=offset)
            _, out, _ = sh([*uv, '--python', '3.13', '--exclude-newer', day.isoformat(), '--with', 'polars',
                            'python', '-c', PRINT_POLARS], other, env={'TZ': zone})
            seen.append(f'{day}: {polars_of(out)}')
        rows.append((pid, f'bare dates around the upload date, TZ={zone} (the design uses RFC 3339, not a bare date)',
                     'record', '; '.join(seen), 'RECORD'))
    # 2: command-line and environment dates do not reach a script header; the header's own table does
    probe('P2a', 'CLI --exclude-newer does not limit a script header', 'polars 2.0.0',
          [*uv, '--exclude-newer', CUT, str(repo / 'skills/demo/scripts/s.py')], other, newest)
    probe('P2b', 'UV_EXCLUDE_NEWER does not limit a script header', 'polars 2.0.0',
          [*uv, str(repo / 'skills/demo/scripts/s.py')], other, newest, env={'UV_EXCLUDE_NEWER': CUT})
    probe('P2c', "a [tool.uv] exclude-newer in the header limits it", 'polars < 2',
          [*uv, str(build_dir / 'owndate.py')], other, older, env={'UV_NO_CONFIG': '1'})
    # 3: interpreter choice
    probe('P3a', '--python 3.13 resolves a bare polars header', 'polars 2.0.0 on 3.13',
          [*uv, '--python', '3.13', str(deep / 's.py')], other, lambda o: newest(o) and o.endswith('3.13'))
    probe('P3b', '--python 3.14 with polars>=2.0 resolves', 'polars 2.0.0 on 3.14',
          [*uv, '--python', '3.14', '--with', 'polars>=2.0', 'python', '-c', PRINT_POLARS], other,
          lambda o: newest(o) and o.endswith('3.14'))
    probe('P3c', 'no --python, no .python-version (script outside the repo): which interpreter and polars',
          'record (the spec saw 3.14 and 1.44.2)', [*uv, str(work / 'neutral.py')], other, lambda o: True, record=True)
    # 4: the root uv.toml
    probe('P4a', 'root uv.toml date reaches --with in a subdirectory', 'polars < 2',
          [*uv, '--with', 'polars', 'python', '-c', PRINT_POLARS], build_dir, older)
    probe('P4b', 'root uv.toml date reaches a script header in a subdirectory', 'polars < 2',
          [*uv, 's.py'], build_dir, older)
    with_dir = work / 'constraints'
    with_dir.mkdir()
    (with_dir / 'uv.toml').write_text('constraint-dependencies = ["polars<2"]\noverride-dependencies = ["polars<2"]\n')
    probe('P4c', 'constraint- and override-dependencies in uv.toml do not affect --with', 'polars 2.0.0',
          [*uv, '--python', '3.13', '--with', 'polars', 'python', '-c', PRINT_POLARS], with_dir, newest)
    (work / 'constraint.txt').write_text('polars<2\n')
    probe('P4d', 'UV_CONSTRAINT does not affect --with', 'polars 2.0.0',
          [*uv, '--python', '3.13', '--with', 'polars', 'python', '-c', PRINT_POLARS], other, newest,
          env={'UV_CONSTRAINT': str(work / 'constraint.txt')})
    probe('P4e', 'CLI --exclude-newer overrides the uv.toml date', 'polars 2.0.0',
          [*uv, '--exclude-newer', LATE, '--with', 'polars', 'python', '-c', PRINT_POLARS], build_dir, newest)
    probe('P4f', 'UV_EXCLUDE_NEWER overrides the uv.toml date', 'polars 2.0.0',
          [*uv, '--with', 'polars', 'python', '-c', PRINT_POLARS], build_dir, newest, env={'UV_EXCLUDE_NEWER': LATE})
    probe('P4g', '--with polars==1.44.2 on a script run takes over from the header polars>=2.0 (no dates)',
          'polars 1.44.2', [*uv, '--python', '3.13', '--with', 'polars==1.44.2', str(work / 'floor.py')], other,
          lambda o: o == '1.44.2')
    # 5: real path against symlink
    probe('P5a', 'a script run by its real path takes the repo uv.toml, from another directory', 'polars < 2',
          [*uv, str(build_dir / 's.py')], other, older)
    probe('P5b', 'the same script through a symlink does not', 'polars 2.0.0',
          [*uv, str(work / 'link-build' / 's.py')], other, newest)
    # 6: .python-version
    default_py = sh([*uv, '--no-project', 'python', '-c', PRINT_PY], other)[1].replace(' ', '.')
    probe('P6a', '.python-version is found from a subdirectory, also with --no-project',
          f'3.13 (the bare default here is {default_py})', [*uv, '--no-project', 'python', '-c', PRINT_PY], build_dir,
          lambda o: o == '3 13')
    probe('P6b', '--directory finds .python-version from another working directory', '3.13',
          [*uv, '--directory', str(repo), '--no-project', 'python', '-c', PRINT_PY], other, lambda o: o == '3 13')
    probe('P6c', '--directory finds the uv.toml date too', 'polars < 2',
          [*uv, '--directory', str(repo), '--with', 'polars', 'python', '-c', PRINT_POLARS], other, older)
    # the shadow file under skills/
    probe('S1', 'skills/uv.toml shadows the root date for a script header (real path)', 'polars 2.0.0',
          [*uv, 's.py'], deep, newest)
    probe('S2', '... and for --with', 'polars 2.0.0', [*uv, '--with', 'polars', 'python', '-c', PRINT_POLARS], deep, newest)
    probe('S3', '... and .python-version is still found under skills/', '3.13',
          [*uv, '--no-project', 'python', '-c', PRINT_PY], deep, lambda o: o == '3 13')
    probe('S4', '... and a run through a ~/.claude/skills-style symlink floats too', 'polars 2.0.0',
          [*uv, str(work / 'link-skills/demo/scripts/s.py')], other, newest)
    # nested worktrees
    probe('N1', 'a nested worktree without the files inherits the date and the interpreter', 'polars < 2 on 3.13',
          [*uv, '--with', 'polars', 'python', '-c', PRINT_POLARS], repo / '.claude/worktrees/wt',
          lambda o: older(o) and o.endswith('3.13'))
    probe('N2', 'a nested worktree with its own uv.toml uses its own', 'polars 2.0.0',
          [*uv, '--with', 'polars', 'python', '-c', PRINT_POLARS], repo / '.claude/worktrees/wt2', newest)
    # what drift and bump need
    probe('P8a', 'UV_NO_CONFIG=1 drops the root date for --with', 'polars 2.0.0',
          [*uv, '--with', 'polars', 'python', '-c', PRINT_POLARS], build_dir, newest, env={'UV_NO_CONFIG': '1'})
    probe('P8b', 'UV_NO_CONFIG=1 drops the root date for a script header', 'polars 2.0.0',
          [*uv, 's.py'], build_dir, newest, env={'UV_NO_CONFIG': '1'})
    compile_args = ['uv', 'pip', 'compile', '-', '--python-version', '3.13', '--no-header', '--no-annotate', '--quiet']
    pin = lambda o: next((line.split('==')[1] for line in o.splitlines() if line.startswith('polars==')), '')
    probe('P9a', 'uv pip compile reads the root date from the working directory', 'polars < 2',
          compile_args, build_dir, lambda o: major(pin(o)) in range(0, 2), stdin='polars\n')
    probe('P9b', 'uv pip compile --exclude-newer overrides it', 'polars 2.0.0',
          [*compile_args, '--exclude-newer', LATE], build_dir, lambda o: major(pin(o)) >= 2, stdin='polars\n')
    probe('P9c', 'uv --no-config pip compile ignores it', 'polars 2.0.0',
          ['uv', '--no-config', *compile_args[1:]], build_dir, lambda o: major(pin(o)) >= 2, stdin='polars\n')
    probe('P10', 'uv python list --output-format json has the fields drift reads', 'version, version_parts, variant, implementation',
          ['uv', 'python', 'list', '--only-downloads', '--output-format', 'json'], other,
          lambda o: all(k in json.loads(o)[0] for k in ('version', 'version_parts', 'variant', 'implementation')),
          show=lambda o: 'fields present')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--keep', action='store_true', help='leave the throwaway tree in place')
    args = parser.parse_args()
    if shutil.which('uv') is None:
        print('uv is not on PATH', file=sys.stderr)
        return 2
    print(f'{subprocess.run(["uv", "--version"], capture_output=True, text=True).stdout.strip()}\n')
    work = Path(tempfile.mkdtemp(prefix='vprobe-66-'))
    try:
        run_all(work)
    finally:
        if not args.keep:
            shutil.rmtree(work, ignore_errors=True)
    print('| id | probe | expected | observed | result |\n|---|---|---|---|---|')
    for row in rows:
        print('| ' + ' | '.join(cell.replace('|', '/') for cell in row) + ' |')
    return 1 if any(row[-1] == 'FAIL' for row in rows) else 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 2: Run the probe.** It needs the network and takes about one minute.

```bash
uv run --no-project python specs/verification/66-uv-probe.py | tee /tmp/66-uv-probe.out
```

Expected: exit status 1 (two FAIL rows) and a Markdown table of about 40 rows. The first line names the uv version.

- [ ] **Step 3: Compare the table with the forecast.** The forecast is in "Forecast for Task 1". If the table is as forecast, go on. If any other row FAILs, or P2a or P2b PASS, or the uv version has changed in a way that explains the difference, **stop**. Report the table to the owner and wait. Do not go on to Task 2.

- [ ] **Step 4: Check that `setup-uv` leaves the interpreter to uv (spec R5.2).** The workflow pins the action by SHA. Read the action's inputs at that SHA.

```bash
sha=$(grep -o 'setup-uv@[0-9a-f]*' .github/workflows/lints.yml | cut -d@ -f2)
gh api "repos/astral-sh/setup-uv/contents/action.yml?ref=$sha" --jq .content | base64 -d | grep -n -A2 '^  python-version:'
```

Expected: an optional input whose description says it sets `UV_PYTHON`. When `lints.yml` does not pass it, uv reads `.python-version` itself (probe row P6a). So `lints.yml` needs no change. If the action reads `.python-version` another way or the input is required, stop and report.

- [ ] **Step 5: Check that a plain file in a skills directory is ignored (spec R2.1).** `skills/uv.toml` is a file, not a skill.
  1. Repo readers: `install.py:97-101`, `build/check_frontmatter.py:574-575` and `build/check_provenance.py:40-44` list only directories that hold a `SKILL.md`. Confirm with `sed -n 92,102p install.py`.
  2. The installer links each skill on its own into `~/.claude/skills`, so no runtime sees `skills/uv.toml` through an install. Confirm with `ls -la ~/.claude/skills | head -5`. Expected: one symlink for each skill, and no `uv.toml`.
  3. Claude Code, live. A user can also point a runtime at the whole `skills/` directory, so check the loader. It costs about $0.05.

```bash
rm -rf /tmp/vprobe-66-cc && mkdir -p /tmp/vprobe-66-cc/.claude/skills/demo && cd /tmp/vprobe-66-cc
printf -- '---\nname: demo\ndescription: Use when testing a plain file beside a skill.\n---\nBody.\n' > .claude/skills/demo/SKILL.md
printf '# no settings\n' > .claude/skills/uv.toml
CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 claude -p --tools "" --strict-mcp-config --output-format stream-json --verbose 'Reply with the single word ok.' < /dev/null > out.jsonl 2> err.txt
python3 -I -c "
import json
for line in open('out.jsonl'):
    rec = json.loads(line)
    if rec.get('type') == 'system' and rec.get('subtype') == 'init':
        skills = rec.get('skills', [])
        print('demo loaded:', 'demo' in skills, '| a uv.toml skill:', any('uv' in s and 'toml' in s for s in skills))
        break
"
cd - > /dev/null
```

Expected: `demo loaded: True | a uv.toml skill: False`.
  4. Codex and Gemini. Open each runtime's current skills documentation and find the sentence that says a skill is a directory with a `SKILL.md`. Quote it in the record. If a runtime's documentation does not say so, record "not confirmed" and ask the owner before Task 4.

- [ ] **Step 6: Write the record.** Create `specs/verification/66-uv-probe.md`. It holds the date, the output of `uv --version`, the full probe table (paste `/tmp/66-uv-probe.out`) and the results of step 4 and step 5. It ends with one paragraph that says which spec items the run changed (items 2 and 3, by the forecast). End with the line `Probes run with uv --no-cache; uv reuses a cached environment whose requirements match, whatever freeze date built it.`

- [ ] **Step 7: Apply amendment A1 to the spec.** Edit `specs/package-versions.md` with these exact replacements. Leave the status line untouched.

Replace item 2 of "uv behavior that constrains the design":

````text
2. For a PEP 723 script (`uv run script.py`), the command-line `--exclude-newer` and `UV_EXCLUDE_NEWER` did not limit the header's dependencies. With a 2026-10-01 cutoff it still installed polars 2.0.0 (uploaded 2026-10-06). A `[tool.uv] exclude-newer = "..."` table inside the script header did limit them (polars 1.44.2).
````

with:

````text
2. For a PEP 723 script (`uv run script.py`), the command-line `--exclude-newer`, `UV_EXCLUDE_NEWER` and a `[tool.uv] exclude-newer = "..."` table inside the script header each limit the header's dependencies (polars 1.44.2 with a 2026-10-01 cutoff; polars 2.0.0 was uploaded 2026-10-06). The first probe said the first two did not. That probe ran with uv's environment cache on, and uv reuses a cached environment whose requirements match, whatever freeze date built it. Every probe runs with `--no-cache` now. (owner, plan 66, 2026-10-21)
````

Replace item 3:

````text
3. With no `--python`, uv picked Python 3.14 for a script, and a bare `polars` header resolved to 1.44.2, not 2.0.0. Under `--python 3.13` it resolved to 2.0.0. But `uv run --python 3.14 --with 'polars>=2.0'` also resolved to 2.0.0, so the three `polars>=2.0` scripts work on 3.14. The cause of the 1.44.2 result is unknown.
````

with:

````text
3. With no `--python` and no `.python-version`, uv picked Python 3.14 for a script. A bare `polars` header then resolved to 2.0.0, as it does under `--python 3.13` and as `uv run --python 3.14 --with 'polars>=2.0'` does. So the three `polars>=2.0` scripts work on 3.14. The 1.44.2 result of the first probe came from a cached environment (item 2), not from the interpreter. (owner, plan 66, 2026-10-21)
````

- [ ] **Step 8: Commit.**

```bash
git add specs/verification/66-uv-probe.py specs/verification/66-uv-probe.md specs/package-versions.md
git commit -m "docs(specs): re-probe uv for package-versions (plan 66 task 1)"
```

### Task 2: `versions.py` core

**Files:**
- Create: `build/versions.py`
- Create: `build/test_versions.py`

**Interfaces:**
- Consumes: nothing.
- Produces (later tasks rely on these exact names):
  - `VersionsError(Exception)`. `normalize(name) -> str` (PEP 503 form). `version_tuple(text) -> tuple[int, ...]`. `compare(a, b) -> -1 | 0 | 1` (zero-padded).
  - `Override(gate, package, version, reason)`. `Versions(dev_python, freeze, packages, cited, gates, overrides)` with `.cutoff -> str`, `.stack(gate, pins=None) -> list[str]` and `.pins() -> dict[str, str]`.
  - `parse(text, where=VERSIONS_FILE) -> Versions`. `load(root=REPO) -> Versions`. `rewrite(text, date=None, packages=None) -> str`. `outputs(v) -> dict[str, str]`. `sync(root, check=False) -> list[str]`.
  - `SUBCOMMANDS` (name -> `(add_parser, handler)`), `build_parser()`, `main(argv=None, root=REPO) -> int`.
  - Later tasks insert library code above the line `# ---- command line` and command code above `SUBCOMMANDS = {`.

- [ ] **Step 1: Write the failing tests.** Create `build/test_versions.py`.

```python
'''Tests for build/versions.py: the file's schema, the synced outputs, the uv argv it builds, and the
bump, verify and drift flows against a stub uv. Nothing here uses the network or a real uv: the stub
is a script first on PATH, as hooks/test_project_hooks.py does it.'''
import datetime

import pytest

import versions
from versions import VersionsError


GOOD = '''\
[python]
dev = '3.13'                 # repo checks

[freeze]
date = 2026-10-19            # every check resolves as of this date

[packages]
alpha = '1.2.0'
beta-two = '2.0.0'
gamma = '0.5'

[cited]
delta = '6.2'

[gates]
snippets = ['alpha', 'beta-two']
jax-cpu = ['alpha', 'gamma']
'''


WITH_OVERRIDE = GOOD + '''
[[override]]
gate = 'jax-cpu'
package = 'alpha'
version = '1.1.0'
reason = 'jax-cpu needs the older alpha'
'''


def make_root(tmp_path, text=GOOD):
    (tmp_path / 'build').mkdir()
    (tmp_path / 'build' / 'versions.toml').write_text(text)
    (tmp_path / 'skills').mkdir()
    return tmp_path


def test_parse_reads_every_table():
    v = versions.parse(WITH_OVERRIDE)
    assert (v.dev_python, v.freeze) == ('3.13', datetime.date(2026, 10, 19))
    assert v.packages == {'alpha': '1.2.0', 'beta-two': '2.0.0', 'gamma': '0.5'}
    assert v.cited == {'delta': '6.2'}
    assert v.gates == {'snippets': ('alpha', 'beta-two'), 'jax-cpu': ('alpha', 'gamma')}
    assert v.overrides == (versions.Override('jax-cpu', 'alpha', '1.1.0', 'jax-cpu needs the older alpha'),)


def test_cutoff_is_midnight_utc_on_the_day_after_the_freeze_date():
    assert versions.parse(GOOD).cutoff == '2026-10-20T00:00:00Z'
    assert versions.parse(GOOD.replace('2026-10-19', '2026-12-31')).cutoff == '2027-01-01T00:00:00Z'


def test_stack_without_an_override():
    v = versions.parse(GOOD)
    assert v.stack('snippets') == ['alpha==1.2.0', 'beta-two==2.0.0']
    assert v.stack('jax-cpu') == ['alpha==1.2.0', 'gamma==0.5']


def test_stack_with_an_override_changes_only_its_gate():
    v = versions.parse(WITH_OVERRIDE)
    assert v.stack('snippets') == ['alpha==1.2.0', 'beta-two==2.0.0']
    assert v.stack('jax-cpu') == ['alpha==1.1.0', 'gamma==0.5']


def test_a_pin_beats_an_override_and_matches_a_normalised_name():
    v = versions.parse(WITH_OVERRIDE)
    assert v.stack('jax-cpu', {'alpha': '9.9'}) == ['alpha==9.9', 'gamma==0.5']
    assert v.stack('snippets', {'beta_two': '3.0'}) == ['alpha==1.2.0', 'beta-two==3.0']


def test_stack_of_an_unknown_gate_names_the_gates():
    with pytest.raises(VersionsError, match=r"unknown gate 'third'.*snippets, jax-cpu"):
        versions.parse(GOOD).stack('third')


@pytest.mark.parametrize('old, new, expected', [
    ("dev = '3.13'", "dev = 3.13", r"\[python\] dev must be a string"),
    ("dev = '3.13'", "dev = 'three'", r"'three'"),
    ('date = 2026-10-19', "date = '2026-10-19'", r"\[freeze\] date must be a TOML date.*'2026-10-19'"),
    ('date = 2026-10-19', 'date = 2026-10-19T12:00:00Z', r"\[freeze\] date must be a TOML date"),
    ("alpha = '1.2.0'", "alpha = '1.2.x'", r"\[packages\] alpha: invalid version '1\.2\.x'"),
    ("delta = '6.2'", "alpha = '6.2'", r"alpha is in both \[packages\] and \[cited\]"),
    ("['alpha', 'beta-two']", "['alpha', 'zeta']", r"\[gates\] snippets names zeta, which has no \[packages\] entry"),
    ("['alpha', 'beta-two']", "[]", r"\[gates\] snippets must be a non-empty list"),
    ('[cited]', '[cites]', r"unknown table 'cites'"),
])
def test_invalid_files_name_their_cause(old, new, expected):
    with pytest.raises(VersionsError, match=expected):
        versions.parse(GOOD.replace(old, new))


@pytest.mark.parametrize('mutate, expected', [
    (lambda t: t.replace("gate = 'jax-cpu'", "gate = 'third'"), r"unknown gate 'third'"),
    (lambda t: t.replace("package = 'alpha'", "package = 'gamma2'"), r"gamma2 is not in gate jax-cpu"),
    (lambda t: t.replace("reason = 'jax-cpu needs the older alpha'", "reason = ''"), r"missing key 'reason'"),
    (lambda t: t.replace("version = '1.1.0'", "version = 'old'"), r"invalid version 'old'"),
])
def test_invalid_overrides(mutate, expected):
    with pytest.raises(VersionsError, match=expected):
        versions.parse(mutate(WITH_OVERRIDE))


def test_a_missing_file_names_the_path(tmp_path):
    with pytest.raises(VersionsError, match=r'build/versions\.toml: cannot read'):
        versions.load(tmp_path)


def test_invalid_toml_names_the_file():
    with pytest.raises(VersionsError, match=r'build/versions\.toml: invalid TOML'):
        versions.parse('[python\n')


def test_outputs_are_exactly_these_files():
    out = versions.outputs(versions.parse(GOOD))
    assert out['.python-version'] == '3.13\n'
    assert out['uv.toml'].endswith('exclude-newer = "2026-10-20T00:00:00Z"\n')
    assert out['uv.toml'].startswith('# Written by build/versions.py sync from build/versions.toml. Do not edit.\n')
    settings = [line for line in out['skills/uv.toml'].splitlines() if line and not line.startswith('#')]
    assert settings == []  # the shadow file sets nothing
    assert 'build/versions.toml' in out['skills/uv.toml']
    assert set(out) == {'.python-version', 'uv.toml', 'skills/uv.toml'}


def test_sync_writes_the_outputs_and_check_then_passes(tmp_path):
    root = make_root(tmp_path)
    assert versions.main(['sync', '--check'], root=root) == 1
    assert versions.main(['sync'], root=root) == 0
    assert (root / '.python-version').read_text() == '3.13\n'
    assert versions.main(['sync', '--check'], root=root) == 0


def test_sync_check_names_a_file_that_differs(tmp_path, capsys):
    root = make_root(tmp_path)
    versions.sync(root)
    (root / 'uv.toml').write_text('exclude-newer = "2020-01-01T00:00:00Z"\n')
    assert versions.sync(root, check=True) == ['uv.toml: differs; run build/versions.py sync']


def test_rewrite_changes_the_date_and_the_package_values_only():
    text = versions.rewrite(GOOD, datetime.date(2026, 11, 2), {'alpha': '1.3.0', 'gamma': '0.6'})
    assert "alpha = '1.3.0'" in text and "gamma = '0.6'" in text
    assert 'date = 2026-11-02            # every check resolves as of this date' in text
    assert "beta-two = '2.0.0'" in text and "delta = '6.2'" in text   # [cited] never moves
    assert "dev = '3.13'                 # repo checks" in text
    assert versions.rewrite(text, datetime.date(2026, 10, 19), {'alpha': '1.2.0', 'gamma': '0.5'}) == GOOD


def test_an_invalid_file_exits_2_with_the_cause(tmp_path, capsys):
    root = make_root(tmp_path, GOOD.replace("'1.2.0'", "'oops'"))
    assert versions.main(['sync'], root=root) == 2
    assert "[packages] alpha: invalid version 'oops'" in capsys.readouterr().err
```

- [ ] **Step 2: Run them and watch them fail.**

```bash
cd build && uv run --with pytest python -m pytest -q test_versions.py
```

Expected: FAIL at collection with `ModuleNotFoundError: No module named 'versions'`.

- [ ] **Step 3: Write the module.** Create `build/versions.py`.

```python
'''One source for every pinned or cited package version, the dev interpreter and the freeze date.

build/versions.toml is the only file where a person sets one of them. This script reads it:

    uv run python build/versions.py sync [--check]
    uv run python build/versions.py run GATE [--pin PKG==X ...] -- COMMAND ...
    uv run python build/versions.py verify [--pin PKG==X ...]
    uv run python build/versions.py bump [--date YYYY-MM-DD] [--only PKG ...]
    uv run python build/versions.py drift [--pin PKG==X ...]
    uv run python build/versions.py check

sync writes .python-version, uv.toml and skills/uv.toml, and --check fails when one differs.
run installs a gate's pinned stack and runs COMMAND under uv with the freeze date. verify runs the
re-verify set. bump moves the freeze date and re-pins [packages] by one joint resolve. drift does the
same resolve with no freeze date and reports it. check is the offline commit lint.
--python and --no-freeze on run and verify exist for drift's second pass.

Exit status: 0 on success; 1 when a check, a gate or a sync comparison fails; 2 for a usage error, an
invalid versions file or a network or resolve failure (the message names the cause).
Design: specs/package-versions.md.
'''
import argparse
import datetime
import re
import sys
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


VERSIONS_FILE = 'build/versions.toml'


VERSION_RE = re.compile(r'\d+(?:\.\d+)*')


PYTHON_RE = re.compile(r'3\.\d+')


OVERRIDE_KEYS = ('gate', 'package', 'version', 'reason')


SYNC_NOTE = '# Written by build/versions.py sync from build/versions.toml. Do not edit.\n'


class VersionsError(Exception):
    '''An invalid or unreadable versions file; the message names the cause.'''


def normalize(name: str) -> str:
    '''PEP 503 form, which is how uv prints a package name.'''
    return re.sub(r'[-_.]+', '-', name).lower()


def version_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split('.'))


def compare(a: str, b: str) -> int:
    '''-1, 0 or 1; the shorter version is padded with zeros.'''
    x, y = version_tuple(a), version_tuple(b)
    width = max(len(x), len(y))
    x, y = x + (0,) * (width - len(x)), y + (0,) * (width - len(y))
    return (x > y) - (x < y)


@dataclass(frozen=True)
class Override:
    gate: str
    package: str
    version: str
    reason: str


@dataclass(frozen=True)
class Versions:
    dev_python: str
    freeze: datetime.date
    packages: dict[str, str]
    cited: dict[str, str]
    gates: dict[str, tuple[str, ...]]
    overrides: tuple[Override, ...] = ()

    @property
    def cutoff(self) -> str:
        '''00:00:00Z on the day after the freeze date, so the freeze day itself is included.'''
        return f'{self.freeze + datetime.timedelta(days=1):%Y-%m-%d}T00:00:00Z'

    def stack(self, gate: str, pins: Mapping[str, str] | None = None) -> list[str]:
        '''The `pkg==version` strings of a gate: [packages], then overrides, then --pin values.'''
        if gate not in self.gates:
            raise VersionsError(f'unknown gate {gate!r}; the gates are {", ".join(self.gates)}')
        pins = {normalize(k): v for k, v in (pins or {}).items()}
        out = []
        for package in self.gates[gate]:
            version = self.packages[package]
            for override in self.overrides:
                if override.gate == gate and override.package == package:
                    version = override.version
            out.append(f'{package}=={pins.get(normalize(package), version)}')
        return out

    def pins(self) -> dict[str, str]:
        '''Every [packages] entry, keyed by normalised name; what a suite run installs.'''
        return {normalize(name): version for name, version in self.packages.items()}


def _table(data: dict, key: str, where: str) -> dict:
    value = data.get(key)
    if not isinstance(value, dict):
        raise VersionsError(f'{where}: missing table [{key}]')
    return value


def parse(text: str, where: str = VERSIONS_FILE) -> Versions:
    '''Validate the file's text; every error names its key, package, date or value.'''
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise VersionsError(f'{where}: invalid TOML: {exc}') from exc
    known = {'python', 'freeze', 'packages', 'cited', 'gates', 'override'}
    for key in data:
        if key not in known:
            raise VersionsError(f'{where}: unknown table {key!r}')
    dev = _table(data, 'python', where).get('dev')
    if not isinstance(dev, str) or not PYTHON_RE.fullmatch(dev):
        raise VersionsError(f"{where}: [python] dev must be a string such as '3.13', got {dev!r}")
    date = _table(data, 'freeze', where).get('date')
    if not isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
        raise VersionsError(f'{where}: [freeze] date must be a TOML date such as 2026-10-19, got {date!r}')
    packages = dict(_table(data, 'packages', where))
    cited = dict(data.get('cited', {}))
    for table, entries in (('packages', packages), ('cited', cited)):
        for name, version in entries.items():
            if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
                raise VersionsError(f'{where}: [{table}] {name}: invalid version {version!r}')
    for name in packages:
        if normalize(name) in {normalize(c) for c in cited}:
            raise VersionsError(f'{where}: {name} is in both [packages] and [cited]')
    gates = {}
    for gate, members in _table(data, 'gates', where).items():
        if not isinstance(members, list) or not members or not all(isinstance(m, str) for m in members):
            raise VersionsError(f'{where}: [gates] {gate} must be a non-empty list of package names')
        for member in members:
            if member not in packages:
                raise VersionsError(f'{where}: [gates] {gate} names {member}, which has no [packages] entry')
        gates[gate] = tuple(members)
    overrides = []
    for i, table in enumerate(data.get('override', []), start=1):
        for key in OVERRIDE_KEYS:
            if not isinstance(table.get(key), str) or not table[key]:
                raise VersionsError(f'{where}: [[override]] {i}: missing key {key!r}')
        if table['gate'] not in gates:
            raise VersionsError(f"{where}: [[override]] {i}: unknown gate {table['gate']!r}")
        if table['package'] not in gates[table['gate']]:
            raise VersionsError(f"{where}: [[override]] {i}: {table['package']} is not in gate {table['gate']}")
        if not VERSION_RE.fullmatch(table['version']):
            raise VersionsError(f"{where}: [[override]] {i}: invalid version {table['version']!r}")
        overrides.append(Override(*(table[key] for key in OVERRIDE_KEYS)))
    return Versions(dev, date, packages, cited, gates, tuple(overrides))


def load(root: Path = REPO) -> Versions:
    path = root / VERSIONS_FILE
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as exc:
        raise VersionsError(f'{VERSIONS_FILE}: cannot read: {exc}') from exc
    return parse(text)


def rewrite(text: str, date: datetime.date | None = None, packages: Mapping[str, str] | None = None) -> str:
    '''The file's text with the freeze date and [packages] values replaced; comments and order stay.'''
    out, table = [], ''
    for line in text.splitlines(keepends=True):
        header = re.match(r'\s*\[+([^\]]+)\]+', line)
        if header:
            table = header.group(1)
        elif date and table == 'freeze' and re.match(r'\s*date\s*=', line):
            line = re.sub(r'=\s*\S+', f'= {date.isoformat()}', line, count=1)
        elif packages and table == 'packages':
            match = re.match(r"(\s*)([\w.-]+)(\s*=\s*)'[^']*'(.*)$", line, re.S)
            if match and match.group(2) in packages:
                line = f"{match.group(1)}{match.group(2)}{match.group(3)}'{packages[match.group(2)]}'{match.group(4)}"
        out.append(line)
    return ''.join(out)


def outputs(v: Versions) -> dict[str, str]:
    '''The three files `sync` owns, as repo-relative path -> exact text.'''
    return {
        '.python-version': f'{v.dev_python}\n',
        'uv.toml': (f'{SYNC_NOTE}# Every uv run in this repo resolves packages as of this cutoff: 00:00:00Z on the day after\n'
                    f'# the freeze date, {v.freeze.isoformat()}, so files uploaded on the freeze date itself are included.\n'
                    f'exclude-newer = "{v.cutoff}"\n'),
        'skills/uv.toml': (f'{SYNC_NOTE}# No settings. This file stops uv from reading the repo-root uv.toml for scripts under\n'
                           '# skills/, so a skill script that a user runs floats within its own dependency floors.\n'
                           '# The repo\'s checks pass --exclude-newer themselves (build/versions.py run, build/run_suites.py).\n'),
    }


def sync(root: Path, check: bool = False) -> list[str]:
    '''Write the outputs, or with check list the ones that differ.'''
    v = load(root)
    problems = []
    for rel, text in outputs(v).items():
        path = root / rel
        current = path.read_text(encoding='utf-8') if path.is_file() else None
        if current == text:
            continue
        if check:
            problems.append(f'{rel}: {"missing" if current is None else "differs"}; run build/versions.py sync')
        else:
            path.write_text(text, encoding='utf-8')
    return problems


# ---- command line -----------------------------------------------------------

def add_sync(sub) -> None:
    sub.add_parser('sync', help='write .python-version, uv.toml and skills/uv.toml').add_argument(
        '--check', action='store_true', help='fail when an output differs')


def cmd_sync(args, root: Path, tail: Sequence[str]) -> int:
    problems = sync(root, check=args.check)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


SUBCOMMANDS = {
    'sync': (add_sync, cmd_sync),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='versions.py', description="Read and move the repo's package versions.")
    sub = parser.add_subparsers(dest='command', required=True)
    for add, _ in SUBCOMMANDS.values():
        add(sub)
    return parser


def main(argv: Sequence[str] | None = None, root: Path = REPO) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    tail: list[str] = []
    if '--' in argv:
        cut = argv.index('--')
        argv, tail = argv[:cut], argv[cut + 1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != 'run' and tail:
        parser.error(f'{args.command} takes no command after --')
    if args.command == 'run' and not tail:
        parser.error('run needs a command after --')
    try:
        return SUBCOMMANDS[args.command][1](args, root, tail)
    except VersionsError as exc:
        print(f'{args.command}: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 4: Run the tests.**

```bash
cd build && uv run --with pytest python -m pytest -q test_versions.py
```

Expected: PASS, +26 tests.

- [ ] **Step 5: Commit.**

```bash
git add build/versions.py build/test_versions.py
git commit -m "feat(build): versions.py core, schema and sync (plan 66 task 2)"
```

### Task 3: `bump` and the joint resolve

**Files:**
- Modify: `build/versions.py`
- Modify: `build/test_versions.py`

**Interfaces:**
- Consumes: Task 2's `load`, `parse`, `rewrite`, `sync`, `Versions`, `normalize`, `SUBCOMMANDS`.
- Produces: `resolve(requirements, python_version, cutoff) -> dict[str, str]` (a joint `uv pip compile`, normalised name to version, transitive pins included, and with `cutoff=None` it runs `uv --no-config` so the repo's `uv.toml` does not apply). `requirements(v, only=(), pins=None) -> list[str]`. `bump(root, date, only=(), resolver=None) -> list[str]`. `parse_date(text) -> datetime.date`. The `bump` subcommand.

- [ ] **Step 1: Write the failing tests.** In `build/test_versions.py`, make this import edit, then append the tests below.

In `build/test_versions.py`, replace:

```text
import datetime

import pytest
```

with:

```text
import datetime
import json
import sys

import pytest
```


Append to the end of the file:

```python
STUB = '''\
#!{python}
import json, sys
cfg = json.load(open({config!r}))
args = sys.argv[1:]
with open({log!r}, 'a') as log:
    log.write(json.dumps(args) + '\\n')
if 'compile' in args:
    sys.stdout.write(cfg.get('compile_out', ''))
    sys.stderr.write(cfg.get('compile_err', ''))
    sys.exit(cfg.get('compile_rc', 0))
if args[:2] == ['python', 'list']:
    print(json.dumps(cfg.get('pythons', [])))
    sys.exit(0)
sys.exit(cfg.get('run_rc', 0))
'''


@pytest.fixture
def stub_uv(tmp_path, monkeypatch):
    bin_dir = tmp_path / 'stub-bin'
    bin_dir.mkdir()
    config, log = tmp_path / 'stub.json', tmp_path / 'uv.log'
    uv = bin_dir / 'uv'
    uv.write_text(STUB.format(python=sys.executable, config=str(config), log=str(log)))
    uv.chmod(0o755)
    monkeypatch.setenv('PATH', f'{bin_dir}:/usr/bin:/bin')

    class Stub:
        def set(self, **cfg):
            config.write_text(json.dumps(cfg))

        def calls(self):
            return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []

    stub = Stub()
    stub.set()
    return stub


def test_requirements_leave_only_the_named_packages_free():
    v = versions.parse(GOOD)
    assert versions.requirements(v) == ['alpha', 'beta-two', 'gamma']
    assert versions.requirements(v, only=['gamma']) == ['alpha==1.2.0', 'beta-two==2.0.0', 'gamma']
    assert versions.requirements(v, pins={'beta-two': '1.0'}) == ['alpha', 'beta-two==1.0', 'gamma']
    with pytest.raises(VersionsError, match=r'--only names zeta'):
        versions.requirements(v, only=['zeta'])


def test_bump_rewrites_the_file_and_the_outputs(tmp_path):
    root = make_root(tmp_path)
    seen = {}

    def resolver(reqs, python, cutoff):
        seen.update(reqs=reqs, python=python, cutoff=cutoff)
        return {'alpha': '1.3.0', 'beta-two': '2.0.0', 'gamma': '0.5', 'extra': '1.0'}

    changes = versions.bump(root, datetime.date(2026, 11, 2), resolver=resolver)
    assert seen == {'reqs': ['alpha', 'beta-two', 'gamma'], 'python': '3.13', 'cutoff': '2026-11-03T00:00:00Z'}
    assert changes == ['freeze: 2026-10-19 -> 2026-11-02', 'alpha: 1.2.0 -> 1.3.0']
    v = versions.load(root)
    assert v.freeze == datetime.date(2026, 11, 2) and v.packages['alpha'] == '1.3.0'
    assert 'exclude-newer = "2026-11-03T00:00:00Z"' in (root / 'uv.toml').read_text()
    assert v.cited == {'delta': '6.2'}


def test_bump_fails_when_the_resolve_misses_a_package(tmp_path):
    root = make_root(tmp_path)
    with pytest.raises(VersionsError, match=r'resolve step: the joint resolve did not return gamma'):
        versions.bump(root, datetime.date(2026, 11, 2), resolver=lambda *a: {'alpha': '1', 'beta-two': '2'})
    assert versions.load(root).freeze == datetime.date(2026, 10, 19)   # nothing was written


def test_resolve_passes_the_requirements_on_stdin_and_parses_the_pins(stub_uv):
    stub_uv.set(compile_out='alpha==1.3.0\nBeta_Two==2.0.0 ; python_version > "3"\ntransitive==4.0\n')
    got = versions.resolve(['alpha', 'beta-two'], '3.13', '2026-11-03T00:00:00Z')
    assert got == {'alpha': '1.3.0', 'beta-two': '2.0.0', 'transitive': '4.0'}
    assert stub_uv.calls() == [['pip', 'compile', '-', '--python-version', '3.13', '--no-header', '--no-annotate',
                                '--quiet', '--exclude-newer', '2026-11-03T00:00:00Z']]


def test_resolve_without_a_cutoff_ignores_the_config(stub_uv):
    stub_uv.set(compile_out='alpha==1.3.0\n')
    versions.resolve(['alpha'], '3.14', None)
    assert stub_uv.calls()[0][:3] == ['--no-config', 'pip', 'compile']
    assert '--exclude-newer' not in stub_uv.calls()[0]


def test_a_failed_resolve_names_the_step_the_packages_and_uvs_reason(stub_uv):
    stub_uv.set(compile_rc=1, compile_err='Because alpha and gamma conflict, no solution\n')
    with pytest.raises(VersionsError) as err:
        versions.resolve(['alpha', 'gamma'], '3.13', None)
    assert 'resolve step' in str(err.value) and 'alpha, gamma' in str(err.value)
    assert 'Because alpha and gamma conflict' in str(err.value)


def test_bump_exits_2_and_names_the_step_when_the_resolve_fails(tmp_path, stub_uv, capsys):
    root = make_root(tmp_path)
    stub_uv.set(compile_rc=1, compile_err='no network\n')
    assert versions.main(['bump', '--date', '2026-11-02'], root=root) == 2
    assert capsys.readouterr().err.startswith('bump: resolve step:')
    assert versions.load(root).freeze == datetime.date(2026, 10, 19)


def test_bump_rejects_an_invalid_date(tmp_path, capsys):
    with pytest.raises(SystemExit) as err:
        versions.main(['bump', '--date', '2026-13-40'], root=make_root(tmp_path))
    assert err.value.code == 2
    assert "invalid date '2026-13-40'" in capsys.readouterr().err
```

- [ ] **Step 2: Run them and watch them fail.**

```bash
cd build && uv run --with pytest python -m pytest -q test_versions.py
```

Expected: the new tests FAIL with `AttributeError: module 'versions' has no attribute 'requirements'` (or `resolve`, or `bump`). The Task 2 tests still pass.

- [ ] **Step 3: Edit the imports of `build/versions.py`.**

In `build/versions.py`, replace:

```text
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
```

with:

```text
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
```

In `build/versions.py`, replace:

```text
import re
import sys
```

with:

```text
import re
import subprocess
import sys
```


- [ ] **Step 4: Add the library code.** Insert this block immediately above the line `# ---- command line`.

```python
RESOLVED_LINE = re.compile(r'^([A-Za-z0-9][A-Za-z0-9._-]*)==([0-9][^\s;]*)', re.M)


def resolve(requirements: Sequence[str], python_version: str, cutoff: str | None) -> dict[str, str]:
    '''One joint `uv pip compile` of the requirements; {normalised name: version}, transitive ones too.
    With no cutoff it ignores the repo's uv.toml, so it sees the newest releases.'''
    argv = ['uv'] + ([] if cutoff else ['--no-config']) + [
        'pip', 'compile', '-', '--python-version', python_version, '--no-header', '--no-annotate', '--quiet']
    if cutoff:
        argv += ['--exclude-newer', cutoff]
    try:
        done = subprocess.run(argv, input='\n'.join(requirements) + '\n', capture_output=True, text=True)
    except OSError as exc:
        raise VersionsError(f'resolve step: cannot start uv: {exc}') from exc
    if done.returncode != 0:
        raise VersionsError(f'resolve step: joint resolve of {", ".join(requirements)} on Python '
                            f'{python_version} failed:\n{done.stderr.strip()}')
    return {normalize(name): version for name, version in RESOLVED_LINE.findall(done.stdout)}


def requirements(v: Versions, only: Iterable[str] = (), pins: Mapping[str, str] | None = None) -> list[str]:
    '''The joint resolve's input: a bare name where it may move, `name==pin` where it may not.'''
    only = {normalize(name) for name in only}
    unknown = only - {normalize(name) for name in v.packages}
    if unknown:
        raise VersionsError(f'--only names {", ".join(sorted(unknown))}, which has no [packages] entry')
    pins = pins or {}
    out = []
    for name, pin in v.packages.items():
        key = normalize(name)
        if key in pins:
            out.append(f'{name}=={pins[key]}')
        elif only and key not in only:
            out.append(f'{name}=={pin}')
        else:
            out.append(name)
    return out


def bump(root: Path, date: datetime.date, only: Iterable[str] = (),
         resolver: Callable[..., dict[str, str]] | None = None) -> list[str]:
    '''Move the freeze date and re-pin [packages] by one joint resolve; the changed lines.'''
    resolver = resolver or resolve
    v = load(root)
    moved = replace(v, freeze=date)
    resolved = resolver(requirements(v, only), v.dev_python, moved.cutoff)
    missing = [name for name in v.packages if normalize(name) not in resolved]
    if missing:
        raise VersionsError(f'resolve step: the joint resolve did not return {", ".join(missing)}')
    new = {name: resolved[normalize(name)] for name in v.packages}
    path = root / VERSIONS_FILE
    path.write_text(rewrite(path.read_text(encoding='utf-8'), date, new), encoding='utf-8')
    sync(root)
    changes = [f'{name}: {old} -> {new[name]}' for name, old in v.packages.items() if new[name] != old]
    if date != v.freeze:
        changes.insert(0, f'freeze: {v.freeze.isoformat()} -> {date.isoformat()}')
    return changes
```

- [ ] **Step 5: Add the command code.** Insert this block immediately above the line `SUBCOMMANDS = {`.

```python
def parse_date(text: str) -> datetime.date:
    try:
        return datetime.date.fromisoformat(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f'invalid date {text!r}; write YYYY-MM-DD') from exc


def add_bump(sub) -> None:
    parser = sub.add_parser('bump', help='move the freeze date and re-pin [packages]')
    parser.add_argument('--date', type=parse_date, help='the new freeze date (default: today, UTC)')
    parser.add_argument('--only', nargs='+', default=[], metavar='PKG', help='move only these packages')


def cmd_bump(args, root: Path, tail: Sequence[str]) -> int:
    date = args.date or datetime.datetime.now(datetime.timezone.utc).date()
    for line in bump(root, date, args.only):
        print(line)
    return 0
```

Replace the whole `SUBCOMMANDS = {...}` assignment with:

```python
SUBCOMMANDS = {
    'sync': (add_sync, cmd_sync),
    'bump': (add_bump, cmd_bump),
}
```

- [ ] **Step 6: Run the tests.**

```bash
cd build && uv run --with pytest python -m pytest -q test_versions.py
```

Expected: PASS, +8 tests.

- [ ] **Step 7: Commit.**

```bash
git add build/versions.py build/test_versions.py
git commit -m "feat(build): versions.py bump and joint resolve (plan 66 task 3)"
```

### Task 4: Write `build/versions.toml`, first `bump`, `sync` (spec R6 step 2, first half)

**Files:**
- Create: `build/versions.toml`, `.python-version`, `uv.toml`, `skills/uv.toml` (the last three are written by `sync`)
- Modify: `specs/package-versions.md` (amendment A2)

**Interfaces:**
- Consumes: `bump`, `sync` from Tasks 2 and 3.
- Produces: the file that Tasks 5 to 10 read. Gate names `snippets` and `jax-cpu`. The package list of Q2.

R6 step 2 says to write the file and then run `bump` and `verify` on the day of execution. `verify` does not exist yet. This task writes the file and runs the first `bump`. Task 10 runs `verify` and a second `bump` if the day has changed. The package values below are `0` placeholders. `bump` replaces them in step 2. Do not commit a `0`.

- [ ] **Step 1: Create `build/versions.toml`.**

```toml
# The one place where a person sets a package version, the dev interpreter or the freeze date.
# Design: specs/package-versions.md. Do not copy a value into another file by hand.
# `uv run python build/versions.py bump` rewrites the freeze date and the [packages] values, and keeps
# these comments. A person edits [cited] only after re-checking the cited behavior.
# `uv run python build/versions.py sync` writes .python-version, uv.toml and skills/uv.toml from this file.

[python]
dev = '3.13'                 # repo checks and documented commands; sync writes it to .python-version

[freeze]
date = 2026-10-21            # every check resolves as of this date; bump moves it

[packages]                   # one exact version each; a check installs these and a skill states a version for them
arviz = '0'
arviz-base = '0'
arviz-plots = '0'
arviz-stats = '0'
diffrax = '0'
e3nn-jax = '0'
equinox = '0'
fastexcel = '0'
flax = '0'
h5netcdf = '0'
h5py = '0'
jax = '0'
jaxlib = '0'
matplotlib = '0'
numpy = '0'
numpyro = '0'
optax = '0'
optuna = '0'
orbax-checkpoint = '0'
polars = '0'
xarray = '0'

[cited]                      # prose cites these and no check runs them; bump never changes them
altair = '6.2'
plotly = '6.8'
great-docs = '0.17.0'

[gates]                      # the packages each check installs, pinned from [packages]
snippets = ['arviz', 'arviz-base', 'arviz-stats', 'arviz-plots', 'numpyro', 'jax', 'numpy', 'matplotlib']
jax-cpu = ['jax', 'jaxlib', 'flax', 'optax', 'orbax-checkpoint', 'equinox', 'diffrax', 'e3nn-jax', 'numpy']

# [[override]]               # gate, package, version, reason; empty at the start
```

If the owner answered Q2 with the alternative, delete the `optuna` line and add `optuna = '5.0.0'` under `[cited]`.

- [ ] **Step 2: Run the first `bump`.** It needs the network. It sets the freeze date to today (UTC), resolves all `[packages]` together on the dev Python, rewrites the file and runs `sync`.

```bash
uv run python build/versions.py bump
```

Expected: a line `freeze: 2026-10-21 -> <today>` (or no such line when today is 2026-10-21), then one line `<package>: 0 -> <version>` for each of the 21 packages. Exit 0. If it exits 2, read the message. A conflict names the packages. Do not edit the placeholders by hand to get around it. Report the conflict (it is the case that D2, one version for each package, makes visible).

- [ ] **Step 3: Check the result.**

```bash
git status --short && cat .python-version uv.toml && uv run python build/versions.py sync --check && echo sync ok && grep -c "= '0'" build/versions.toml
```

Expected: the four files changed or new, `3.13`, a `uv.toml` with `exclude-newer = "<day after freeze>T00:00:00Z"`, `sync ok`, and `0` for the last count (no placeholder left). `skills/uv.toml` holds comments only.

- [ ] **Step 4: Check that the repo's own readers skip `skills/uv.toml`.**

```bash
uv run --with pyyaml python build/check_frontmatter.py && uv run python build/check_provenance.py && uv run --with pyyaml python build/check_conformance.py
cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py
```

Expected: all pass. `install.py` and the two lints read only directories that hold a `SKILL.md`.

- [ ] **Step 5: Apply amendment A2 to the spec** (only with Q2's default). In `specs/package-versions.md`, section R1.1, replace:

````text
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
````

with:

````text
[packages]                   # one exact version each; a check runs these
arviz = '1.3.0'
numpyro = '0.22.0'
jax = '0.12.0'
optuna = '5.0.0'             # the tune-hyperparameters suite installs it and its SKILL.md cites it (R1.2)
# ... every package that a [gates] entry or a skill citation names and a check runs

[cited]                      # prose cites these, but no check runs them
altair = '6.2'
plotly = '6.8'
great-docs = '0.17.0'
````

Append `(owner, plan 66, 2026-10-21)` to the line `The values above are the 2026-10-21 state. The plan sets the real values with `bump` (R3).`

- [ ] **Step 6: Commit.**

```bash
git add build/versions.toml .python-version uv.toml skills/uv.toml specs/package-versions.md
git commit -m "feat(build): add build/versions.toml and its synced outputs (plan 66 task 4)"
```

After this commit every `uv run` in the repo resolves packages as of the freeze date and uses the dev Python.

### Task 5: `run` and the upload-date check

**Files:**
- Modify: `build/versions.py`, `build/test_versions.py`

**Interfaces:**
- Consumes: Tasks 2 and 4 (`Versions.stack`, the real file).
- Produces: `RUNNER` (`'uv run python build/versions.py run'`), `runner_command(gate, tail) -> str` (the documented form of a pinned command), `uv_run_argv(v, gate, command, pins=None, python=None, freeze=True) -> list[str]` (`gate=None` leaves out the `--with` list), `parse_pins(v, specs) -> dict[str, str]` (names normalised, each must be a `[packages]` entry), `late_pins(v, specs, fetch=None) -> list[str]` (the specs whose release was first uploaded at or after the cutoff), `fetch_json(url) -> dict`, `run_process(argv, root, env) -> int`, `add_pin_options`, and the `run` subcommand.

- [ ] **Step 1: Write the failing tests.** Append to `build/test_versions.py`.

```python
def test_parse_pins():
    v = versions.parse(GOOD)
    assert versions.parse_pins(v, ['beta_two==3.1', 'alpha==1.0']) == {'beta-two': '3.1', 'alpha': '1.0'}
    with pytest.raises(VersionsError, match=r"--pin 'alpha': write it as package==version"):
        versions.parse_pins(v, ['alpha'])
    with pytest.raises(VersionsError, match=r"--pin 'zeta==1\.0': zeta has no \[packages\] entry"):
        versions.parse_pins(v, ['zeta==1.0'])


def fake_pypi(uploaded='2026-10-01T10:00:00.000000Z', newest='9.9.9'):
    def fetch(url):
        return {'info': {'version': newest}, 'urls': [{'upload_time_iso_8601': uploaded}]}
    return fetch


def test_a_pin_uploaded_after_the_cutoff_names_the_package_and_the_dates():
    v = versions.parse(GOOD)
    late = versions.late_pins(v, ['alpha==1.2.0'], fake_pypi('2026-10-20T00:00:00.000000Z'))
    assert late == ['alpha 1.2.0: uploaded 2026-10-20, after the freeze date 2026-10-19']
    assert versions.late_pins(v, ['alpha==1.2.0'], fake_pypi('2026-10-19T23:59:59.000000Z')) == []


def test_uv_run_argv_orders_python_cutoff_stack_command():
    v = versions.parse(GOOD)
    argv = versions.uv_run_argv(v, 'snippets', ['python', 'x.py'])
    assert argv == ['uv', 'run', '--python', '3.13', '--exclude-newer', '2026-10-20T00:00:00Z',
                    '--with', 'alpha==1.2.0', '--with', 'beta-two==2.0.0', 'python', 'x.py']
    argv = versions.uv_run_argv(v, 'snippets', ['python', 'x.py'], {'alpha': '1.0'}, python='3.14', freeze=False)
    assert argv == ['uv', 'run', '--python', '3.14', '--with', 'alpha==1.0', '--with', 'beta-two==2.0.0',
                    'python', 'x.py']
    assert versions.uv_run_argv(v, None, ['python', 'y.py']) == [
        'uv', 'run', '--python', '3.13', '--exclude-newer', '2026-10-20T00:00:00Z', 'python', 'y.py']


def test_runner_command_is_the_documented_form():
    assert versions.runner_command('snippets', 'python build/check_snippets.py --run skills/') == (
        'uv run python build/versions.py run snippets -- python build/check_snippets.py --run skills/')


def test_run_builds_the_uv_command_and_returns_its_status(tmp_path, stub_uv, monkeypatch):
    root = make_root(tmp_path)
    monkeypatch.setattr(versions, 'fetch_json', fake_pypi())
    stub_uv.set(run_rc=3)
    assert versions.main(['run', 'snippets', '--pin', 'alpha==1.0', '--', 'python', 'x.py'], root=root) == 3
    assert stub_uv.calls() == [['run', '--python', '3.13', '--exclude-newer', '2026-10-20T00:00:00Z',
                                '--with', 'alpha==1.0', '--with', 'beta-two==2.0.0', 'python', 'x.py']]


def test_run_refuses_a_pin_uploaded_after_the_freeze_date(tmp_path, stub_uv, monkeypatch, capsys):
    root = make_root(tmp_path)
    monkeypatch.setattr(versions, 'fetch_json', fake_pypi('2026-10-25T00:00:00.000000Z'))
    assert versions.main(['run', 'snippets', '--', 'python', 'x.py'], root=root) == 2
    assert 'alpha 1.2.0: uploaded 2026-10-25, after the freeze date 2026-10-19' in capsys.readouterr().err
    assert stub_uv.calls() == []


def test_run_needs_a_command(tmp_path):
    with pytest.raises(SystemExit) as err:
        versions.main(['run', 'snippets'], root=make_root(tmp_path))
    assert err.value.code == 2
```

- [ ] **Step 2: Run them and watch them fail.**

```bash
cd build && uv run --with pytest python -m pytest -q test_versions.py
```

Expected: the new tests FAIL with `AttributeError: module 'versions' has no attribute 'parse_pins'` (or another new name).

- [ ] **Step 3: Edit the imports of `build/versions.py`.**

In `build/versions.py`, replace:

```text
import datetime
import re
```

with:

```text
import datetime
import json
import re
```

In `build/versions.py`, replace:

```text
import tomllib
```

with:

```text
import tomllib
import urllib.request
```


- [ ] **Step 4: Add the library code.** Insert immediately above the line `# ---- command line`.

```python
RUNNER = 'uv run python build/versions.py run'


Fetch = Callable[[str], dict]


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={'User-Agent': 'agent-skills-versions'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except (OSError, ValueError) as exc:
        raise VersionsError(f'cannot reach {url}: {exc}') from exc


def parse_time(text: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(text.replace('Z', '+00:00'))


def first_upload(urls: Sequence[Mapping], what: str) -> datetime.datetime:
    times = [parse_time(entry['upload_time_iso_8601']) for entry in urls]
    if not times:
        raise VersionsError(f'{what}: PyPI lists no files')
    return min(times)


def late_pins(v: Versions, specs: Iterable[str], fetch: Fetch | None = None) -> list[str]:
    '''The specs whose release was first uploaded at or after the freeze cutoff.'''
    fetch = fetch or fetch_json
    cutoff = parse_time(v.cutoff)
    problems = []
    for spec in specs:
        package, _, version = spec.partition('==')
        uploaded = first_upload(fetch(f'https://pypi.org/pypi/{package}/{version}/json').get('urls', []),
                                spec)
        if uploaded >= cutoff:
            problems.append(f'{package} {version}: uploaded {uploaded:%Y-%m-%d}, after the freeze date '
                            f'{v.freeze.isoformat()}')
    return problems


def parse_pins(v: Versions, specs: Sequence[str]) -> dict[str, str]:
    '''`--pin pkg==X` values as {name: version}; each must name a [packages] entry.'''
    known = {normalize(name) for name in v.packages}
    pins = {}
    for spec in specs:
        name, eq, version = spec.partition('==')
        if not eq or not VERSION_RE.fullmatch(version):
            raise VersionsError(f'--pin {spec!r}: write it as package==version')
        if normalize(name) not in known:
            raise VersionsError(f'--pin {spec!r}: {name} has no [packages] entry')
        pins[normalize(name)] = version
    return pins


def uv_run_argv(v: Versions, gate: str | None, command: Sequence[str], pins: Mapping[str, str] | None = None,
                python: str | None = None, freeze: bool = True) -> list[str]:
    '''`uv run` with the interpreter, the freeze cutoff and the gate's pinned stack, then the command.'''
    argv = ['uv', 'run', '--python', python or v.dev_python]
    if freeze:
        argv += ['--exclude-newer', v.cutoff]
    if gate is not None:
        for spec in v.stack(gate, pins):
            argv += ['--with', spec]
    return argv + list(command)


def runner_command(gate: str, tail: str) -> str:
    '''The documented form of a pinned-stack command.'''
    return f'{RUNNER} {gate} -- {tail}'


def run_process(argv: Sequence[str], root: Path = REPO, env: Mapping[str, str] | None = None) -> int:
    try:
        return subprocess.run(list(argv), cwd=root, env=None if env is None else dict(env)).returncode
    except OSError as exc:
        print(f'cannot start {argv[0]}: {exc}', file=sys.stderr, flush=True)
        return 2
```

- [ ] **Step 5: Add the command code.** Insert immediately above `SUBCOMMANDS = {`.

```python
def add_pin_options(parser: argparse.ArgumentParser, drift_only: bool = False) -> None:
    parser.add_argument('--pin', action='append', default=[], metavar='PKG==X',
                        help='use this version for one run; the file stays as it is')
    if not drift_only:
        parser.add_argument('--python', help="another interpreter, for drift's second pass")
        parser.add_argument('--no-freeze', action='store_true', help='leave out the freeze date, for drift')


def add_run(sub) -> None:
    parser = sub.add_parser('run', help="run a command under a gate's pinned stack; the command follows --")
    parser.add_argument('gate')
    add_pin_options(parser)


def cmd_run(args, root: Path, tail: Sequence[str]) -> int:
    v = load(root)
    pins = parse_pins(v, args.pin)
    if not args.no_freeze:
        late = late_pins(v, v.stack(args.gate, pins))
        if late:
            print('\n'.join(late), file=sys.stderr)
            return 2
    return run_process(uv_run_argv(v, args.gate, tail, pins, args.python, not args.no_freeze), root)
```

Replace the whole `SUBCOMMANDS = {...}` assignment with:

```python
SUBCOMMANDS = {
    'sync': (add_sync, cmd_sync),
    'bump': (add_bump, cmd_bump),
    'run': (add_run, cmd_run),
}
```

- [ ] **Step 6: Run the tests.**

```bash
cd build && uv run --with pytest python -m pytest -q test_versions.py
```

Expected: PASS, +7 tests.

- [ ] **Step 7: Smoke test against the real file.** It needs the network.

```bash
uv run python build/versions.py run snippets -- python -c "import importlib.metadata as m; print(m.version('numpyro'))"
grep '^numpyro' build/versions.toml
```

Expected: the two lines show the same version.

- [ ] **Step 8: Commit.**

```bash
git add build/versions.py build/test_versions.py
git commit -m "feat(build): versions.py run, pins and upload-date check (plan 66 task 5)"
```

### Task 6: `check_snippets.py` reads the file (spec R2.3), amendment A3

**Files:**
- Modify: `build/check_snippets.py`, `build/snippet_preamble.py`, `build/test_check_snippets.py`, `specs/package-versions.md`

**Interfaces:**
- Consumes: `versions.runner_command` (Task 5).
- Produces: `check_snippets.API_REMEDIATION` and `RUN_REMEDIATION` as runner commands. `snippet_preamble.PINNED` no longer exists.

- [ ] **Step 1: Write the failing tests.** Append to `build/test_check_snippets.py`.

```python
def test_the_remediation_commands_use_the_runner_and_spell_no_version():
    import versions
    assert check_snippets.API_REMEDIATION == versions.runner_command(
        'snippets', 'python build/check_snippets.py --api <paths>')
    assert check_snippets.RUN_REMEDIATION == versions.runner_command(
        'snippets', 'python build/check_snippets.py --run <paths>')
    for command in (check_snippets.API_REMEDIATION, check_snippets.RUN_REMEDIATION):
        assert not any(mark in command for mark in ('==', '>=', '--python', '--with'))


def test_the_preamble_module_no_longer_pins_packages():
    import snippet_preamble
    assert not hasattr(snippet_preamble, 'PINNED')
```

- [ ] **Step 2: Run them and watch them fail.**

```bash
cd build && uv run --with pytest python -m pytest -q test_check_snippets.py -k "remediation_commands or no_longer_pins"
```

Expected: 2 FAIL (`AssertionError`).

- [ ] **Step 3: Make the edits.**

In `build/check_snippets.py`, replace:

```text
from snippet_preamble import FIXTURE_VARS, NAMED_FIXTURES, PINNED, PREAMBLE
```

with:

```text
import versions
from snippet_preamble import FIXTURE_VARS, NAMED_FIXTURES, PREAMBLE
```

In `build/check_snippets.py`, replace:

```text
API_REMEDIATION = ('uv run --python 3.13 --with "arviz>=1.0" --with arviz-base '
                   '--with arviz-stats --with arviz-plots --with numpyro '
                   '--with jax python build/check_snippets.py --api <paths>')
RUN_REMEDIATION = ('uv run --python 3.13 ' +
                   ' '.join(f'--with {d!r}'.replace("'", '\"')
                            for d in PINNED) +
                   ' python build/check_snippets.py --run <paths>')
```

with:

```text
API_REMEDIATION = versions.runner_command('snippets', 'python build/check_snippets.py --api <paths>')
RUN_REMEDIATION = versions.runner_command('snippets', 'python build/check_snippets.py --run <paths>')
```

In `build/snippet_preamble.py`, replace:

```text

PINNED = (
    # Verified resolving 2026-10-19. Refresh deliberately and re-record.
    'arviz==1.3.0', 'arviz-base', 'arviz-stats==1.3.3', 'arviz-plots==1.3.2',
    'numpyro==0.22.0', 'jax==0.12.0', 'numpy', 'matplotlib',
)
```

with nothing (delete it).



The comment "Verified resolving ..." that sat above `PINNED` moves to the freeze date: `bump` sets it.

- [ ] **Step 4: Run the tests.**

```bash
cd build && uv run --with pytest --with numpy --with polars --with pyyaml python -m pytest -q test_check_snippets.py
```

Expected: PASS, +2 tests. The tests that need the stack skip without `--with` for it.

- [ ] **Step 5: Smoke test the gate through the runner.** It needs the network.

```bash
uv run python build/check_snippets.py skills/
uv run python build/versions.py run snippets -- python build/check_snippets.py --api skills/bayesian-workflow/
```

Expected: both exit 0. (Tier 3 runs in Task 10.)

- [ ] **Step 6: Apply amendment A3 to the spec** (only with Q6's default). In `specs/package-versions.md`, section R2.3, replace:

````text
`PINNED` (moved out of `build/snippet_preamble.py`), `RUN_REMEDIATION` and `API_REMEDIATION`. Tier 2 (`--api`) stays unpinned for named packages and gets the freeze date.
````

with:

````text
`PINNED` (moved out of `build/snippet_preamble.py`), `RUN_REMEDIATION` and `API_REMEDIATION`. Tier 2 (`--api`) runs on the same pinned `snippets` stack as Tier 3 (owner, plan 66, 2026-10-21), so no documented command spells a package version (R2.4).
````

(The first line of the old text starts with `- `build/check_snippets.py`: ` in the spec. Replace only the quoted part.)

- [ ] **Step 7: Run the lints that apply, then commit.**

```bash
uv run --with pyyaml python build/check_frontmatter.py && uv run python build/check_provenance.py
git add build/check_snippets.py build/snippet_preamble.py build/test_check_snippets.py specs/package-versions.md
git commit -m "feat(build): check_snippets reads its stack from versions.toml (plan 66 task 6)"
```

### Task 7: `run_suites.py` reads the file (spec R2.3)

**Files:**
- Modify: `build/run_suites.py`, `build/suites.toml`, `build/test_run_suites.py`

**Interfaces:**
- Consumes: `versions.load`, `Versions.pins`, `Versions.cutoff`, `versions.parse_pins`, `versions.normalize`.
- Produces: `run_suites.Pins(python, cutoff, packages)` with `Pins.from_versions(v, python=None, freeze=True, user_pins=None)` and `Pins.spec(dep)`. `run_suites.DEV == 'dev'`. `runs(suite, pins, extras=False, pytest_args=())`, `execute(root, suites, pins, extras, pytest_args, run_one)`, `list_suites(suites, pins, extras, pytest_args)` and `main(argv, root, run_one, pins=None)`. The options `--pin`, `--python` and `--no-freeze`. In `suites.toml`, `dev` stands for the dev Python.

- [ ] **Step 1: Write the failing tests.** Edit `build/test_run_suites.py`.

In `build/test_run_suites.py`, replace:

```text
import run_suites as rs

FIXTURE = '''\
```

with:

```text
import run_suites as rs
import versions

V = versions.load()   # the dev interpreter and the cutoff come from the file, never from a literal here
DEV = V.dev_python
PINS = rs.Pins(python=DEV, cutoff=V.cutoff, packages={'polars': '9.9.9'})
VERSIONS_TOML = '''\
[python]
dev = '3.13'
[freeze]
date = 2026-10-19
[packages]
polars = '9.9.9'
[gates]
snippets = ['polars']
'''

FIXTURE = '''\
```

In `build/test_run_suites.py`, replace:

```text
pythons = ['3.13', '/usr/bin/python3']
'''
ONE
```

with:

```text
pythons = ['dev', '/usr/bin/python3']
'''
ONE
```

In `build/test_run_suites.py`, replace:

```text
def test_a_default_run_has_the_form_claude_md_used():
    [run] = rs.runs(fixture_suites()[0])
    assert run.label == 'alpha (3.13)'
    assert run.argv == ('uv', 'run', '--python', '3.13', '--with', 'pytest', '--with', 'polars',
                        'python', '-m', 'pytest', '-q')
    assert run.shell() == ('cd skills/alpha/scripts && uv run --python 3.13 --with pytest '
                           '--with polars python -m pytest -q')


def test_extras_and_pytest_args_follow_the_deps_and_are_quoted():
    [run] = rs.runs(fixture_suites()[0], extras=True, pytest_args=('-k', 'a and b'))
    assert run.shell() == ("cd skills/alpha/scripts && uv run --python 3.13 --with pytest "
                           "--with polars --with 'arviz>=1.0' python -m pytest -q -k 'a and b'")


def test_each_python_gets_its_own_run_in_order():
    first, second = rs.runs(fixture_suites()[2])
    assert (first.python, second.python) == ('3.13', '/usr/bin/python3')
    assert second.shell() == 'cd tools/inner && uv run --python /usr/bin/python3 --with pytest python -m pytest -q'
```

with:

```text
def test_a_default_run_has_the_form_claude_md_used():
    [run] = rs.runs(fixture_suites()[0], PINS)
    assert run.label == f'alpha ({DEV})'
    assert run.argv == ('uv', 'run', '--python', DEV, '--exclude-newer', V.cutoff, '--with', 'pytest',
                        '--with', 'polars==9.9.9', 'python', '-m', 'pytest', '-q')
    assert run.shell() == (f'cd skills/alpha/scripts && uv run --python {DEV} --exclude-newer {V.cutoff} '
                           '--with pytest --with polars==9.9.9 python -m pytest -q')


def test_extras_and_pytest_args_follow_the_deps_and_are_quoted():
    [run] = rs.runs(fixture_suites()[0], PINS, extras=True, pytest_args=('-k', 'a and b'))
    assert run.shell() == (f"cd skills/alpha/scripts && uv run --python {DEV} --exclude-newer {V.cutoff} "
                           "--with pytest --with polars==9.9.9 --with 'arviz>=1.0' python -m pytest -q -k 'a and b'")


def test_each_python_gets_its_own_run_in_order():
    first, second = rs.runs(fixture_suites()[2], PINS)
    assert (first.python, second.python) == (DEV, '/usr/bin/python3')
    assert second.shell() == (f'cd tools/inner && uv run --python /usr/bin/python3 --exclude-newer {V.cutoff} '
                              '--with pytest python -m pytest -q')


def test_the_dev_entry_follows_the_python_override_and_no_other_entry_does():
    first, second = rs.runs(fixture_suites()[2], rs.Pins(python='3.99', cutoff=None))
    assert (first.python, second.python) == ('3.99', '/usr/bin/python3')


def test_a_pins_object_without_a_cutoff_leaves_out_exclude_newer():
    [run] = rs.runs(fixture_suites()[0], rs.Pins(python=DEV, cutoff=None, packages={}))
    assert '--exclude-newer' not in run.argv
    assert run.argv == ('uv', 'run', '--python', DEV, '--with', 'pytest', '--with', 'polars',
                        'python', '-m', 'pytest', '-q')


def test_pins_pin_only_the_packages_the_file_names():
    assert PINS.spec('polars') == 'polars==9.9.9'
    assert PINS.spec('Polars>=1.0') == 'Polars==9.9.9'
    assert PINS.spec('pytest') == 'pytest'
    assert PINS.spec('arviz>=1.0') == 'arviz>=1.0'


def test_pins_from_versions_read_the_file_and_take_the_options():
    assert rs.Pins.from_versions(V) == rs.Pins(DEV, V.cutoff, V.pins())
    custom = rs.Pins.from_versions(V, python='3.99', freeze=False, user_pins={'numpy': '0.1'})
    assert (custom.python, custom.cutoff) == ('3.99', None) and custom.packages['numpy'] == '0.1'
```

In `build/test_run_suites.py`, replace:

```text
def test_container_compares_path_parts_not_string_prefixes():
    build = rs.Suite('build', 'build', ('pytest',))
    other = rs.Suite('other', 'build_extra', ('pytest',))
```

with:

```text
def test_container_compares_path_parts_not_string_prefixes():
    build = rs.Suite('build', 'build', ('pytest',))
    other = rs.Suite('other', 'build_extra', ('pytest',))
```

In `build/test_run_suites.py`, replace:

```text
    (tmp_path / 'build').mkdir()
    (tmp_path / 'build' / 'suites.toml').write_text(FIXTURE)
    return tmp_path
```

with:

```text
    (tmp_path / 'build').mkdir()
    (tmp_path / 'build' / 'suites.toml').write_text(FIXTURE)
    (tmp_path / 'build' / 'versions.toml').write_text(VERSIONS_TOML)
    return tmp_path
```

In `build/test_run_suites.py`, replace:

```text
    assert rs.main(['tools-inner'], root=repo, run_one=fake) == 0
    assert fake.labels == ['tools-inner (3.13)', 'tools-inner (/usr/bin/python3)']
```

with:

```text
    assert rs.main(['tools-inner'], root=repo, run_one=fake, pins=PINS) == 0
    assert fake.labels == [f'tools-inner ({DEV})', 'tools-inner (/usr/bin/python3)']
```

In `build/test_run_suites.py`, replace:

```text
    fake = FakeRuns({'tools-inner (3.13)': 1})
    assert rs.main(['tools-inner', 'alpha'], root=repo, run_one=fake) == 1
    assert fake.labels == ['tools-inner (3.13)', 'tools-inner (/usr/bin/python3)', 'alpha (3.13)']
    assert capsys.readouterr().err.splitlines()[-1] == 'suite runs failed: tools-inner (3.13)'
```

with:

```text
    fake = FakeRuns({f'tools-inner ({DEV})': 1})
    assert rs.main(['tools-inner', 'alpha'], root=repo, run_one=fake, pins=PINS) == 1
    assert fake.labels == [f'tools-inner ({DEV})', 'tools-inner (/usr/bin/python3)', f'alpha ({DEV})']
    assert capsys.readouterr().err.splitlines()[-1] == f'suite runs failed: tools-inner ({DEV})'
```

In `build/test_run_suites.py`, replace:

```text
    assert rs.main(['alpha'], root=repo, run_one=FakeRuns({'alpha (3.13)': 5})) == 1
```

with:

```text
    assert rs.main(['alpha'], root=repo, run_one=FakeRuns({f'alpha ({DEV})': 5}), pins=PINS) == 1
```

In `build/test_run_suites.py`, replace:

```text
    rs.main(['alpha'], root=repo, run_one=FakeRuns())
    assert capsys.readouterr().out.splitlines()[:2] == ['== alpha (3.13)', 'note: Reads a pilot wiki, else skips.']
```

with:

```text
    rs.main(['alpha'], root=repo, run_one=FakeRuns(), pins=PINS)
    assert capsys.readouterr().out.splitlines()[:2] == [f'== alpha ({DEV})', 'note: Reads a pilot wiki, else skips.']
```

In `build/test_run_suites.py`, replace:

```text
    rs.main(['alpha', '--extras', '--', '-k', 'x'], root=repo, run_one=fake)
    assert fake.argvs == [('uv', 'run', '--python', '3.13', '--with', 'pytest', '--with', 'polars',
                           '--with', 'arviz>=1.0', 'python', '-m', 'pytest', '-q', '-k', 'x')]
```

with:

```text
    rs.main(['alpha', '--extras', '--', '-k', 'x'], root=repo, run_one=fake, pins=PINS)
    assert fake.argvs == [('uv', 'run', '--python', DEV, '--exclude-newer', V.cutoff, '--with', 'pytest',
                           '--with', 'polars==9.9.9', '--with', 'arviz>=1.0', 'python', '-m', 'pytest', '-q',
                           '-k', 'x')]


def test_the_options_build_the_pins_from_the_repos_file(repo):
    fake = FakeRuns()
    args = ['alpha', '--pin', 'polars==8.8.8', '--python', '3.99', '--no-freeze']
    assert rs.main(args, root=repo, run_one=fake) == 0
    assert fake.argvs == [('uv', 'run', '--python', '3.99', '--with', 'pytest', '--with', 'polars==8.8.8',
                           'python', '-m', 'pytest', '-q')]


def test_a_pin_the_file_does_not_name_exits_2(repo, capsys):
    assert rs.main(['alpha', '--pin', 'zeta==1.0'], root=repo, run_one=FakeRuns()) == 2
    assert 'zeta has no [packages] entry' in capsys.readouterr().err


def test_a_missing_versions_file_exits_2(repo, capsys):
    (repo / 'build' / 'versions.toml').unlink()
    assert rs.main(['alpha'], root=repo, run_one=FakeRuns()) == 2
    assert 'build/versions.toml: cannot read' in capsys.readouterr().err


def test_check_takes_no_pin_options(repo):
    with pytest.raises(SystemExit) as err:
        rs.main(['--check', '--pin', 'polars==1.0'], root=repo)
    assert err.value.code == 2
```

In `build/test_run_suites.py`, replace:

```text
    assert rs.main(['--all'], root=repo, run_one=fake) == 0
    assert fake.labels == ['alpha (3.13)', 'outer (3.13)']
```

with:

```text
    assert rs.main(['--all'], root=repo, run_one=fake, pins=PINS) == 0
    assert fake.labels == [f'alpha ({DEV})', f'outer ({DEV})']
```

In `build/test_run_suites.py`, replace:

```text
    assert rs.main(['--list', 'alpha'], root=repo, run_one=fake) == 0
    assert fake.labels == []
    assert capsys.readouterr().out.splitlines() == [
        'alpha: skills/alpha/scripts',
        '  cd skills/alpha/scripts && uv run --python 3.13 --with pytest --with polars python -m pytest -q',
```

with:

```text
    assert rs.main(['--list', 'alpha'], root=repo, run_one=fake, pins=PINS) == 0
    assert fake.labels == []
    assert capsys.readouterr().out.splitlines() == [
        'alpha: skills/alpha/scripts',
        f'  cd skills/alpha/scripts && uv run --python {DEV} --exclude-newer {V.cutoff} --with pytest '
        '--with polars==9.9.9 python -m pytest -q',
```

In `build/test_run_suites.py`, replace:

```text
    [run] = rs.runs(rs.Suite('ghost', 'missing', ('pytest',)))
    assert rs.run_subprocess(tmp_path, run) == 1
    assert 'ghost (3.13): cannot start' in capsys.readouterr().err
```

with:

```text
    [run] = rs.runs(rs.Suite('ghost', 'missing', ('pytest',)), PINS)
    assert rs.run_subprocess(tmp_path, run) == 1
    assert f'ghost ({DEV}): cannot start' in capsys.readouterr().err
```


- [ ] **Step 2: Run them and watch them fail.**

```bash
cd build && uv run --with pytest --with numpy --with polars --with pyyaml python -m pytest -q test_run_suites.py
```

Expected: FAIL. `rs.Pins` does not exist, and `rs.runs` does not take `pins`.

- [ ] **Step 3: Edit the runner and the registry.**

In `build/run_suites.py`, replace:

```text
    uv run --python 3.13 python build/run_suites.py --list [NAME ...]
    uv run --python 3.13 python build/run_suites.py NAME [NAME ...] [--extras] [-- PYTEST_ARGS]
    uv run --python 3.13 python build/run_suites.py --all [--extras] [-- PYTEST_ARGS]
    uv run --python 3.13 python build/run_suites.py --check
```

with:

```text
    uv run python build/run_suites.py --list [NAME ...]
    uv run python build/run_suites.py NAME [NAME ...] [--extras] [-- PYTEST_ARGS]
    uv run python build/run_suites.py --all [--extras] [-- PYTEST_ARGS]
    uv run python build/run_suites.py --check
```

In `build/run_suites.py`, replace:

```text
registered suite directory.

Exit status:
```

with:

```text
registered suite directory.

Each run passes the dev interpreter (the `dev` entry in a suite's `pythons`) and the freeze
cutoff from build/versions.toml to uv, and pins every `with` or extras package that
[packages] names, because a suite under skills/ sits below skills/uv.toml, which shadows the
root date. --pin PKG==X changes one pin for one run, --python replaces the dev interpreter and
--no-freeze leaves out the cutoff; `versions.py drift` uses all three.

Exit status:
```

In `build/run_suites.py`, replace:

```text
import argparse
import os
import shlex
import subprocess
import sys
import tomllib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath
```

with:

```text
import argparse
import os
import re
import shlex
import subprocess
import sys
import tomllib
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath

import versions
```

In `build/run_suites.py`, replace:

```text
DEFAULT_PYTHONS = ('3.13',)
```

with:

```text
DEV = 'dev'  # in a suite's `pythons`: the dev interpreter of build/versions.toml
DEFAULT_PYTHONS = (DEV,)
```

In `build/run_suites.py`, replace:

```text
@dataclass(frozen=True)
class Run:
```

with:

```text
@dataclass(frozen=True)
class Pins:
    '''What a run resolves against: the interpreter for the `dev` entry, the --exclude-newer
    cutoff (None leaves it out) and the exact version of each package, by normalised name.'''
    python: str
    cutoff: str | None
    packages: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def from_versions(cls, v: versions.Versions, python: str | None = None, freeze: bool = True,
                      user_pins: Mapping[str, str] | None = None) -> 'Pins':
        return cls(python or v.dev_python, v.cutoff if freeze else None, {**v.pins(), **(user_pins or {})})

    def spec(self, dep: str) -> str:
        '''`dep` as `name==version` when [packages] pins that name, else as written.'''
        name = re.match(r'[A-Za-z0-9][A-Za-z0-9._-]*', dep)
        key = versions.normalize(name.group(0)) if name else ''
        return f'{name.group(0)}=={self.packages[key]}' if key in self.packages else dep


@dataclass(frozen=True)
class Run:
```

In `build/run_suites.py`, replace:

```text
def runs(suite: Suite, extras: bool = False, pytest_args: Sequence[str] = ()) -> list[Run]:
    '''One run per interpreter, in the suite's order; --extras adds the extras.'''
    deps = suite.deps + (suite.extras if extras else ())
    withs = tuple(word for dep in deps for word in ('--with', dep))
    return [Run(suite, python, ('uv', 'run', '--python', python, *withs,
                                'python', '-m', 'pytest', '-q', *pytest_args))
            for python in suite.pythons]
```

with:

```text
def runs(suite: Suite, pins: Pins, extras: bool = False, pytest_args: Sequence[str] = ()) -> list[Run]:
    '''One run per interpreter, in the suite's order; --extras adds the extras. The `dev`
    entry runs on pins.python.'''
    deps = suite.deps + (suite.extras if extras else ())
    withs = tuple(word for dep in deps for word in ('--with', pins.spec(dep)))
    cutoff = ('--exclude-newer', pins.cutoff) if pins.cutoff else ()
    return [Run(suite, python, ('uv', 'run', '--python', python, *cutoff, *withs,
                                'python', '-m', 'pytest', '-q', *pytest_args))
            for python in (pins.python if entry == DEV else entry for entry in suite.pythons)]
```

In `build/run_suites.py`, replace:

```text
def execute(root: Path, suites: Sequence[Suite], extras: bool, pytest_args: Sequence[str],
            run_one: RunOne) -> int:
    '''Every run of every suite, in order; a failure does not stop the next run.'''
    failed: list[str] = []
    for suite in suites:
        for i, run in enumerate(runs(suite, extras, pytest_args)):
```

with:

```text
def execute(root: Path, suites: Sequence[Suite], pins: Pins, extras: bool, pytest_args: Sequence[str],
            run_one: RunOne) -> int:
    '''Every run of every suite, in order; a failure does not stop the next run.'''
    failed: list[str] = []
    for suite in suites:
        for i, run in enumerate(runs(suite, pins, extras, pytest_args)):
```

In `build/run_suites.py`, replace:

```text
def list_suites(suites: Sequence[Suite], extras: bool, pytest_args: Sequence[str]) -> None:
    for suite in suites:
        print(f'{suite.name}: {suite.dir}')
        for run in runs(suite, extras, pytest_args):
```

with:

```text
def list_suites(suites: Sequence[Suite], pins: Pins, extras: bool, pytest_args: Sequence[str]) -> None:
    for suite in suites:
        print(f'{suite.name}: {suite.dir}')
        for run in runs(suite, pins, extras, pytest_args):
```

In `build/run_suites.py`, replace:

```text
    parser.add_argument('--extras', action='store_true',
                        help='add the deps that unlock skips')
```

with:

```text
    parser.add_argument('--extras', action='store_true',
                        help='add the deps that unlock skips')
    parser.add_argument('--pin', action='append', default=[], metavar='PKG==X',
                        help='use this version for this run (repeatable)')
    parser.add_argument('--python', help='run the dev entries on this interpreter')
    parser.add_argument('--no-freeze', action='store_true', help='leave out the freeze cutoff')
```

In `build/run_suites.py`, replace:

```text
    if args.check and (args.names or args.extras or pytest_args):
        parser.error('--check takes no suite names, --extras or pytest arguments')
```

with:

```text
    if args.check and (args.names or args.extras or pytest_args or args.pin or args.python or args.no_freeze):
        parser.error('--check takes no suite names, --extras, --pin, --python, --no-freeze or pytest arguments')
```

In `build/run_suites.py`, replace:

```text
def main(argv: Sequence[str] | None = None, root: Path = REPO,
         run_one: RunOne = run_subprocess) -> int:
    args, pytest_args = parse_args(list(sys.argv[1:] if argv is None else argv))
```

with:

```text
def main(argv: Sequence[str] | None = None, root: Path = REPO,
         run_one: RunOne = run_subprocess, pins: Pins | None = None) -> int:
    args, pytest_args = parse_args(list(sys.argv[1:] if argv is None else argv))
```

In `build/run_suites.py`, replace:

```text
    chosen = [by_name[name] for name in args.names] or suites
    if args.list:
        list_suites(chosen, args.extras, pytest_args)
        return 0
```

with:

```text
    chosen = [by_name[name] for name in args.names] or suites
    if pins is None:
        try:
            v = versions.load(root)
            pins = Pins.from_versions(v, args.python, not args.no_freeze, versions.parse_pins(v, args.pin))
        except versions.VersionsError as exc:
            print(f'run_suites: {exc}', file=sys.stderr)
            return 2
    if args.list:
        list_suites(chosen, pins, args.extras, pytest_args)
        return 0
```

In `build/run_suites.py`, replace:

```text
    return execute(root, chosen, args.extras, pytest_args, run_one)
```

with:

```text
    return execute(root, chosen, pins, args.extras, pytest_args, run_one)
```

In `build/suites.toml`, replace:

```text
pythons = ['3.13', '/usr/bin/python3']
```

with:

```text
pythons = ['dev', '/usr/bin/python3']
```

In `build/suites.toml`, replace:

```text
#   pythons  optional: one run per interpreter, in order (default ['3.13'])
```

with:

```text
#   pythons  optional: one run per interpreter, in order (default ['dev']); `dev` stands for the
#            dev interpreter of build/versions.toml, and any other entry is passed to uv as written
```

In `build/suites.toml`, replace:

```text
extras = ['arviz>=1.0', 'arviz-base', 'arviz-stats', 'arviz-plots', 'numpyro', 'jax', 'matplotlib']
```

with:

```text
extras = ['arviz', 'arviz-base', 'arviz-stats', 'arviz-plots', 'numpyro', 'jax', 'matplotlib']
```


- [ ] **Step 4: Run the tests.**

```bash
cd build && uv run --with pytest --with numpy --with polars --with pyyaml python -m pytest -q test_run_suites.py
```

Expected: PASS, +8 tests.

- [ ] **Step 5: Smoke test.**

```bash
uv run python build/run_suites.py --list hooks
uv run python build/run_suites.py --check
uv run python build/run_suites.py write-with-asd-ste100
```

Expected: `--list` shows two commands for `hooks`. The first has `--python <dev> --exclude-newer <cutoff>` and the second has `--python /usr/bin/python3 --exclude-newer <cutoff>`. `--check` prints `suite registry ok`. The last run passes.

- [ ] **Step 6: Commit.**

```bash
git add build/run_suites.py build/suites.toml build/test_run_suites.py
git commit -m "feat(build): run_suites reads the dev Python, the cutoff and the pins (plan 66 task 7)"
```

### Task 8: `verify` and `drift`

**Files:**
- Modify: `build/versions.py`, `build/test_versions.py`

**Interfaces:**
- Consumes: Tasks 3, 5 and 7 (`resolve`, `requirements`, `uv_run_argv`, `run_process`, `run_suites.py --pin/--python/--no-freeze`).
- Produces: `Step(label, argv)`, `verify_steps(v, pins=None, python=None, freeze=True, user_pins=None) -> list[Step]` (four steps: `tier 2 (--api)`, `tier 3 (--run)`, `jax cpu examples`, `suites`), `run_steps(steps, root, env, runner) -> list[str]` (labels of failed steps), `newest_stable_python() -> str`, `Row`, `drift_rows`, `render_pass`, `DRIFT_LIMIT`, `drift(root, user_pins=None, fetch=None, resolver=None, newest_python=None, runner=None) -> tuple[int, str]`, and the `verify` and `drift` subcommands.

- [ ] **Step 1: Write the failing tests.** Append to `build/test_versions.py`.

```python
def python_item(version, variant='default', implementation='cpython'):
    major, minor, patch = (int(''.join(c for c in p if c.isdigit())) for p in version.split('.')[:3])
    return {'version': version, 'variant': variant, 'implementation': implementation,
            'version_parts': {'major': major, 'minor': minor, 'patch': patch}}


def test_newest_stable_python_skips_prereleases_and_free_threaded_builds(stub_uv):
    stub_uv.set(pythons=[python_item('3.16.0a1'), python_item('3.15.0', variant='freethreaded'),
                         python_item('3.14.2'), python_item('3.13.9'), python_item('3.15.0', implementation='pypy')])
    assert versions.newest_stable_python() == '3.14'


def test_verify_runs_every_step_and_exits_1_when_one_fails(tmp_path, stub_uv, monkeypatch, capsys):
    root = make_root(tmp_path)
    monkeypatch.setattr(versions, 'fetch_json', fake_pypi())
    stub_uv.set(run_rc=1)
    assert versions.main(['verify'], root=root) == 1
    assert len(stub_uv.calls()) == 4          # a failure does not stop the next step
    err = capsys.readouterr().err
    assert 'verify failed: tier 2 (--api), tier 3 (--run), jax cpu examples, suites' in err


def test_verify_passes_when_every_step_passes(tmp_path, stub_uv, monkeypatch, capsys):
    root = make_root(tmp_path)
    monkeypatch.setattr(versions, 'fetch_json', fake_pypi())
    assert versions.main(['verify', '--pin', 'gamma==0.4'], root=root) == 0
    assert capsys.readouterr().out.rstrip().endswith('verify passed')
    assert stub_uv.calls()[3][-5:] == ['build/run_suites.py', '--all', '--extras', '--pin', 'gamma==0.4']


def drift_world(stub_uv, monkeypatch, run_rc=0, compile_rc=0):
    stub_uv.set(compile_out='alpha==1.5.0\nbeta-two==2.0.0\ngamma==0.5\n', compile_rc=compile_rc,
                compile_err='no route to host\n', run_rc=run_rc,
                pythons=[python_item('3.14.1'), python_item('3.13.9')])
    monkeypatch.setattr(versions, 'fetch_json', fake_pypi(newest='1.5.0'))


def test_drift_exits_0_when_every_gate_passes_on_both_pythons(tmp_path, stub_uv, monkeypatch):
    drift_world(stub_uv, monkeypatch)
    status, report = versions.drift(make_root(tmp_path))
    assert status == 0
    assert '## Python 3.13' in report and '## Python 3.14' in report
    assert '| alpha | 1.2.0 | 1.5.0 | 1.5.0 |' in report
    assert '| delta | 6.2 | - | 1.5.0 |' in report and 'a newer release exists' in report
    assert report.count('| suites | pass |') == 2 and 'FAIL' not in report
    assert versions.DRIFT_LIMIT in report


def test_drift_runs_the_steps_with_the_resolved_pins_and_no_freeze(tmp_path, stub_uv, monkeypatch):
    drift_world(stub_uv, monkeypatch)
    versions.drift(make_root(tmp_path))
    runs = [call for call in stub_uv.calls() if call[0] == 'run']
    assert len(runs) == 8                        # four steps in each of two passes
    first = runs[0]
    assert first[:3] == ['run', '--python', '3.13'] and '--exclude-newer' not in first
    assert 'alpha==1.5.0' in first
    assert runs[3][-5:] == ['--pin', 'gamma==0.5', '--python', '3.13', '--no-freeze']


def test_drift_exits_1_when_a_gate_fails(tmp_path, stub_uv, monkeypatch):
    drift_world(stub_uv, monkeypatch, run_rc=1)
    status, report = versions.drift(make_root(tmp_path))
    assert status == 1 and '| suites | FAIL |' in report


def test_drift_exits_2_when_it_cannot_resolve(tmp_path, stub_uv, monkeypatch):
    drift_world(stub_uv, monkeypatch, compile_rc=1)
    status, report = versions.drift(make_root(tmp_path))
    assert status == 2 and 'drift could not finish: resolve step' in report


def test_drift_exits_2_when_pypi_is_unreachable(tmp_path, stub_uv, monkeypatch):
    drift_world(stub_uv, monkeypatch)

    def down(url):
        raise VersionsError(f'cannot reach {url}: timed out')

    monkeypatch.setattr(versions, 'fetch_json', down)
    status, report = versions.drift(make_root(tmp_path))
    assert status == 2 and 'cannot reach https://pypi.org/pypi/' in report


def test_drift_main_prints_the_report_and_returns_its_status(tmp_path, stub_uv, monkeypatch, capsys):
    drift_world(stub_uv, monkeypatch, run_rc=1)
    assert versions.main(['drift'], root=make_root(tmp_path)) == 1
    assert '# Package drift' in capsys.readouterr().out
```

- [ ] **Step 2: Run them and watch them fail.**

```bash
cd build && uv run --with pytest python -m pytest -q test_versions.py
```

Expected: the new tests FAIL with `AttributeError: module 'versions' has no attribute 'newest_stable_python'` (or `drift`, or `verify_steps`).

- [ ] **Step 3: Edit the imports of `build/versions.py`.**

In `build/versions.py`, replace:

```text
import json
import re
```

with:

```text
import json
import os
import re
```


- [ ] **Step 4: Add the library code.** Insert immediately above the line `# ---- command line`.

```python
@dataclass(frozen=True)
class Step:
    label: str
    argv: tuple[str, ...]


def verify_steps(v: Versions, pins: Mapping[str, str] | None = None, python: str | None = None,
                 freeze: bool = True, user_pins: Mapping[str, str] | None = None) -> list[Step]:
    '''The re-verify set. `pins` pins the gates' stacks; `user_pins` are the --pin values that the
    suite runner repeats (it reads the rest of its pins from the file).'''
    def gate_step(label: str, gate: str, tail: list[str]) -> Step:
        return Step(label, tuple(uv_run_argv(v, gate, tail, pins, python, freeze)))
    suites = ['python', 'build/run_suites.py', '--all', '--extras']
    for name, version in (user_pins if user_pins is not None else (pins or {})).items():
        suites += ['--pin', f'{name}=={version}']
    if python:
        suites += ['--python', python]
    if not freeze:
        suites.append('--no-freeze')
    return [
        gate_step('tier 2 (--api)', 'snippets',
                  ['python', 'build/check_snippets.py', '--api', 'skills/bayesian-workflow/']),
        gate_step('tier 3 (--run)', 'snippets',
                  ['python', 'build/check_snippets.py', '--run', 'skills/bayesian-workflow/']),
        gate_step('jax cpu examples', 'jax-cpu',
                  ['python', 'build/check_jax_examples.py', 'skills/deep-learning/']),
        Step('suites', tuple(uv_run_argv(v, None, suites, None, python, freeze))),
    ]


def run_steps(steps: Sequence[Step], root: Path = REPO, env: Mapping[str, str] | None = None,
              runner: Callable[..., int] = run_process) -> list[str]:
    '''Run every step, in order, whatever fails; the labels of the failed ones.'''
    failed = []
    for step in steps:
        print(f'== {step.label}', flush=True)
        if runner(step.argv, root, env) != 0:
            failed.append(step.label)
    return failed


def newest_stable_python() -> str:
    '''The newest CPython that uv can download, as `3.<minor>`, prereleases and free-threaded builds left out.'''
    try:
        done = subprocess.run(['uv', 'python', 'list', '--only-downloads', '--output-format', 'json'],
                              capture_output=True, text=True)
        items = json.loads(done.stdout)
    except (OSError, ValueError) as exc:
        raise VersionsError(f'python step: cannot list the Python releases: {exc}') from exc
    if done.returncode != 0:
        raise VersionsError(f'python step: uv python list failed:\n{done.stderr.strip()}')
    found = [(item['version_parts']['major'], item['version_parts']['minor']) for item in items
             if item.get('implementation') == 'cpython' and item.get('variant') == 'default'
             and re.fullmatch(r'\d+\.\d+\.\d+', item.get('version', ''))]
    if not found:
        raise VersionsError('python step: uv lists no stable CPython release')
    major, minor = max(found)
    return f'{major}.{minor}'


@dataclass(frozen=True)
class Row:
    package: str
    pinned: str
    resolved: str
    newest: str
    uploaded: str
    flag: str


def drift_rows(v: Versions, resolved: Mapping[str, str], fetch: Fetch | None = None) -> list[Row]:
    fetch = fetch or fetch_json
    rows = []
    for table, entries in (('packages', v.packages), ('cited', v.cited)):
        for name, pinned in entries.items():
            data = fetch(f'https://pypi.org/pypi/{name}/json')
            newest = data['info']['version']
            uploaded = f'{first_upload(data.get("urls", []), name):%Y-%m-%d}'
            got = resolved.get(normalize(name), '-') if table == 'packages' else '-'
            flag = ''
            if table == 'packages' and got != '-' and compare(got, newest) < 0:
                flag = 'resolves below its newest release'
            elif table == 'cited' and version_tuple(newest)[:len(version_tuple(pinned))] != version_tuple(pinned):
                flag = 'a newer release exists'
            rows.append(Row(name, pinned, got, newest, uploaded, flag))
    return rows


def render_pass(python: str, rows: Sequence[Row], results: Sequence[tuple[str, bool]]) -> str:
    lines = [f'## Python {python}', '', '| package | pinned | resolved | newest | uploaded | flag |',
             '|---|---|---|---|---|---|']
    lines += [f'| {r.package} | {r.pinned} | {r.resolved} | {r.newest} | {r.uploaded} | {r.flag} |' for r in rows]
    lines += ['', '| gate | result |', '|---|---|']
    lines += [f'| {label} | {"pass" if ok else "FAIL"} |' for label, ok in results]
    return '\n'.join(lines) + '\n'


DRIFT_LIMIT = ('Limit: `check` and this report see only the package names that build/versions.toml lists. '
               'A package that a skill cites and the file omits is invisible to both.')


def drift(root: Path, user_pins: Mapping[str, str] | None = None, fetch: Fetch | None = None,
          resolver: Callable[..., dict[str, str]] | None = None,
          newest_python: Callable[[], str] | None = None,
          runner: Callable[..., int] | None = None) -> tuple[int, str]:
    '''The drift run: (exit status, report). Status 0 when every gate passes on the newest versions,
    1 when a gate fails, 2 when it cannot resolve or reach the network.'''
    resolver, newest_python, runner = resolver or resolve, newest_python or newest_stable_python, runner or run_process
    v = load(root)
    report = ['# Package drift', '', f'Freeze date {v.freeze.isoformat()}; dev Python {v.dev_python}.', '']
    try:
        newest = newest_python()
        passes = [v.dev_python] + ([newest] if newest != v.dev_python else [])
        failed_any = False
        for python in passes:
            resolved = resolver(requirements(v, pins=user_pins), python, None)
            rows = drift_rows(v, resolved, fetch)
            pins = {normalize(name): resolved[normalize(name)] for name in v.packages}
            steps = verify_steps(v, pins, python=python, freeze=False, user_pins=pins)
            failed = run_steps(steps, root, {**os.environ, 'UV_NO_CONFIG': '1'}, runner)
            failed_any = failed_any or bool(failed)
            report.append(render_pass(python, rows, [(s.label, s.label not in failed) for s in steps]))
    except VersionsError as exc:
        report += ['', f'drift could not finish: {exc}', '', DRIFT_LIMIT]
        return 2, '\n'.join(report) + '\n'
    report += [DRIFT_LIMIT]
    return (1 if failed_any else 0), '\n'.join(report) + '\n'
```

- [ ] **Step 5: Add the command code.** Insert immediately above `SUBCOMMANDS = {`.

```python
def add_verify(sub) -> None:
    add_pin_options(sub.add_parser('verify', help="run the re-verify set on the file's versions"))


def cmd_verify(args, root: Path, tail: Sequence[str]) -> int:
    v = load(root)
    pins = parse_pins(v, args.pin)
    if not args.no_freeze:
        late = late_pins(v, sorted({spec for gate in v.gates for spec in v.stack(gate, pins)}))
        if late:
            print('\n'.join(late), file=sys.stderr)
            return 2
    failed = run_steps(verify_steps(v, pins, args.python, not args.no_freeze), root)
    if failed:
        print(f'verify failed: {", ".join(failed)}', file=sys.stderr)
        return 1
    print('verify passed')
    return 0


def add_drift(sub) -> None:
    add_pin_options(sub.add_parser('drift', help='resolve with no freeze date and run the re-verify set'),
                    drift_only=True)


def cmd_drift(args, root: Path, tail: Sequence[str]) -> int:
    status, report = drift(root, parse_pins(load(root), args.pin))
    print(report)
    return status
```

Replace the whole `SUBCOMMANDS = {...}` assignment with:

```python
SUBCOMMANDS = {
    'sync': (add_sync, cmd_sync),
    'bump': (add_bump, cmd_bump),
    'run': (add_run, cmd_run),
    'verify': (add_verify, cmd_verify),
    'drift': (add_drift, cmd_drift),
}
```

- [ ] **Step 6: Run the tests.**

```bash
cd build && uv run --with pytest python -m pytest -q test_versions.py
```

Expected: PASS, +9 tests.

- [ ] **Step 7: Commit.** (`verify` and `drift` run for real in Task 10 and in the weekly job.)

```bash
git add build/versions.py build/test_versions.py
git commit -m "feat(build): versions.py verify and drift (plan 66 task 8)"
```

### Task 9: The `check` lint (library and subcommand, not yet wired)

**Files:**
- Create: `build/versions_check.py`, `build/test_versions_check.py`
- Modify: `build/versions.py`

**Interfaces:**
- Consumes: `versions.load`, `versions.sync`, `Versions`, `compare`, `normalize`, `version_tuple`, and `run_suites.git_env`.
- Produces: `versions_check.check(root=versions.REPO, historical=None) -> list[str]` (one line for each finding, empty when clean). `HISTORICAL` (phrase to reason). `live_files`, `skipped`, `check_literals`, `check_citations`, `check_floors`, `compat_floor`, `header_text`, `judge`, `citation_regex`, `current_versions`. The `check` subcommand.

The four rules (R4.1): sync, interpreter literals, prose citations (equality, range, history) and floors. Q4's default applies to floors. The two `HISTORICAL` entries below came from the draft run on today's tree. Each phrase is still in skill text.

- [ ] **Step 1: Write the failing tests.** Create `build/test_versions_check.py`.

```python
'''Tests for build/versions_check.py, the lint behind `versions.py check`. Every rule has a positive
control: a seeded stale literal, citation or floor that must fail. The seeded flag text is built from
parts, because the lint reads this file too.'''
import subprocess
import textwrap
from pathlib import Path

import pytest

import versions
import versions_check as vc
from run_suites import git_env

TOML = '''\
[python]
dev = '3.13'
[freeze]
date = 2026-10-19
[packages]
arviz = '1.3.0'
polars = '2.0.0'
numpyro = '0.22.0'
arviz-stats = '1.3.3'
orbax-checkpoint = '0.12.8'
jaxlib = '0.12.0.1'
[cited]
altair = '6.2'
great-docs = '0.17.0'
[gates]
snippets = ['numpyro', 'arviz-stats', 'arviz']
jax-cpu = ['jaxlib', 'orbax-checkpoint']
'''
V = versions.parse(TOML)
FLAG = '--python'


def skill_tree(tmp_path, files):
    for rel, text in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text))
    return tmp_path


def cite(tmp_path, text, historical=None):
    root = skill_tree(tmp_path, {'skills/demo/SKILL.md': text})
    return vc.check_citations(root, V, historical or {})


# ---- equality ------------------------------------------------------------------------------

def test_an_equal_citation_passes_at_its_own_precision(tmp_path):
    text = 'Verified on Polars 2, Polars 2.0, Polars 2.0.0, NumPyro 0.22 and `numpyro==0.22.0`.\n'
    assert cite(tmp_path, text) == []


def test_a_stale_equality_citation_fails(tmp_path):
    findings = cite(tmp_path, 'line one\nThese are verified on Polars 1.42.\n')
    assert len(findings) == 1
    assert findings[0].startswith("skills/demo/SKILL.md:2: 'Polars 1.42': the file says 2.0.0")


def test_a_citation_more_precise_than_the_file_fails(tmp_path):
    assert len(cite(tmp_path, 'Altair 6.2.1 works.\n')) == 1
    assert cite(tmp_path, 'Altair 6.2 works.\n') == []


@pytest.mark.parametrize('text', [
    '**Altair 6.2, Polars 1.42**', 'orbax checkpoint 0.12.6', 'Orbax checkpoint 0.12.6', 'ORBAX-CHECKPOINT 0.12.6',
    'JAXlib 0.11.2', '`polars` 1.42', 'Polars\n  1.42',
])
def test_name_forms_and_line_breaks_are_still_found(tmp_path, text):
    assert cite(tmp_path, text + '\n'), text


def test_a_name_without_a_version_next_to_it_is_ignored(tmp_path):
    assert cite(tmp_path, 'Polars is fast. narwhals 2.x is a library the file does not list.\n') == []


# ---- ranges --------------------------------------------------------------------------------

@pytest.mark.parametrize('text', [
    'polars>=1.0', 'polars >= 2.0', 'polars≥2.0', 'Polars ≥ 2', 'numpyro >= 0.22', 'Python 3.11+', 'Python ≥ 3.11',
    'Python 3.12 or later', 'great-docs>=0.17.0,<0.18', 'great-docs >=0.17.0,<0.18', 'polars<3', 'arviz-stats < 2.0.0',
])
def test_a_range_that_holds_the_files_version_passes(tmp_path, text):
    assert cite(tmp_path, text + '\n') == []


@pytest.mark.parametrize('text', [
    'polars>=2.1', 'numpyro >= 0.23', 'Python 3.14+', 'Python ≥ 3.14', 'great-docs>=0.17.0,<0.17.0', 'polars<2',
    'arviz-stats < 1.0.0', 'polars>2.0',
])
def test_a_range_that_misses_the_files_version_fails(tmp_path, text):
    findings = cite(tmp_path, text + '\n')
    assert len(findings) == 1 and 'outside this range' in findings[0], text


def test_python_is_checked_against_the_dev_interpreter(tmp_path):
    assert cite(tmp_path, 'Needs Python 3.13.\n') == []
    assert len(cite(tmp_path, 'Verified under Python 3.13.8.\n')) == 1


# ---- history -------------------------------------------------------------------------------

def test_a_historical_phrase_passes_whatever_its_case_or_markup(tmp_path):
    text = 'The classic ArviZ 0.23 stack, the `arviz` 0.23 names and arviz-stats < 1.0.0.\n'
    history = {'ArviZ 0.23': 'classic stack', 'arviz-stats < 1.0.0': 'old releases'}
    assert cite(tmp_path, text, history) == []
    assert len(cite(tmp_path, text)) == 3   # without the allowlist all three fail


def test_a_historical_entry_that_matches_nothing_is_reported(tmp_path):
    findings = cite(tmp_path, 'No versions here.\n', {'ArviZ 0.23': 'classic stack'})
    assert findings == ["HISTORICAL entry 'ArviZ 0.23' matches no text under skills/; remove it"]


# ---- scope ---------------------------------------------------------------------------------

def test_only_the_script_header_of_a_python_file_is_read(tmp_path):
    root = skill_tree(tmp_path, {'skills/demo/scripts/tool.py': '''\
        # /// script
        # requires-python = '>=3.11'
        # dependencies = ['polars>=1.0', 'numpyro==0.21.0']
        # ///
        # In the body a comment may say Polars 1.42 without a finding.
        x = 'numpyro 0.21'
        '''})
    findings = vc.check_citations(root, V, {})
    assert len(findings) == 1 and findings[0].startswith("skills/demo/scripts/tool.py:3: 'numpyro==0.21.0'")


def test_test_files_and_files_outside_skills_are_not_read(tmp_path):
    root = skill_tree(tmp_path, {
        'skills/demo/scripts/test_tool.py': "# /// script\n# dependencies = ['polars==1.0']\n# ///\n",
        'specs/plan.md': 'Polars 1.42\n', 'build/notes.md': 'Polars 1.42\n'})
    assert vc.check_citations(root, V, {}) == []


def test_data_directories_fixtures_and_license_files_are_not_read(tmp_path):
    stale = 'Polars 1.0 is stale.\n'
    root = skill_tree(tmp_path, {'skills/demo/data/notes.md': stale, 'skills/demo/fixtures/page.md': stale,
                                 'skills/demo/LICENSE.md': stale, 'skills/demo/SKILL.md': stale})
    assert [f.split(':')[0] for f in vc.check_citations(root, V, {})] == ['skills/demo/SKILL.md']


# ---- floors --------------------------------------------------------------------------------

def skill(compat, floor=None, name='demo'):
    files = {f'skills/{name}/SKILL.md': f'---\nname: {name}\ndescription: Use when testing.\n{compat}\n---\nbody\n'}
    if floor:
        files[f'skills/{name}/scripts/tool.py'] = f"# /// script\n# requires-python = '>={floor}'\n# ///\n"
    return files


def test_a_script_floor_above_the_promised_floor_fails(tmp_path):
    root = skill_tree(tmp_path, skill('compatibility: Requires uv; Python 3.11+.', '3.12'))
    assert vc.check_floors(root, V) == ['skills/demo/scripts/tool.py: requires Python 3.12, but SKILL.md promises 3.11']


def test_a_script_floor_at_or_below_the_promise_passes(tmp_path):
    assert vc.check_floors(skill_tree(tmp_path, skill('compatibility: Python 3.12+.', '3.12')), V) == []
    assert vc.check_floors(skill_tree(tmp_path / 'b', skill('compatibility: Python 3.12+.', '3.11')), V) == []


def test_a_script_without_a_promise_is_not_compared(tmp_path):
    assert vc.check_floors(skill_tree(tmp_path, skill('license: MIT', '3.11')), V) == []


def test_a_folded_compatibility_value_is_read(tmp_path):
    compat = 'compatibility: >\n  Requires uv to run bundled scripts; Python\n  3.11+. Also requires git.'
    root = skill_tree(tmp_path, skill(compat, '3.12'))
    assert 'promises 3.11' in vc.check_floors(root, V)[0]


def test_a_floor_above_the_dev_python_fails_twice_over(tmp_path):
    root = skill_tree(tmp_path, skill('compatibility: Python 3.14+.', '3.14'))
    findings = vc.check_floors(root, V)
    assert any('promises Python 3.14, above the dev Python 3.13' in f for f in findings)
    assert any('requires Python 3.14, above the dev Python 3.13' in f for f in findings)


# ---- interpreter literals ------------------------------------------------------------------

def test_an_interpreter_literal_fails_and_paths_do_not(tmp_path):
    root = skill_tree(tmp_path, {'CLAUDE.md': f'run uv run {FLAG} 3.13 python x.py\n'
                                 f'and uv run {FLAG}=3.12 python y.py\n'
                                 f'and uv run {FLAG} /usr/bin/python3 python z.py\n'
                                 f'and uv pip compile {FLAG}-version 3.13\n'})
    findings = vc.check_literals(root, [root / 'CLAUDE.md'])
    assert [f.split(': ')[0] for f in findings] == ['CLAUDE.md:1', 'CLAUDE.md:2']
    assert "drop the flag, since uv reads .python-version" in findings[0]


def git(repo, *args):
    subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True, env=git_env())


def test_live_files_are_the_listed_files_and_directories_that_git_keeps(tmp_path):
    git(tmp_path, 'init', '-q')
    skill_tree(tmp_path, {'CLAUDE.md': 'x', 'README.md': 'x', 'build/a.py': 'x', 'build/.scratch/b.py': 'x',
                          'skills/s/SKILL.md': 'x', 'specs/plans/p.md': 'x', 'hooks/h.sh': 'x',
                          '.claude/skills/c/SKILL.md': 'x', '.claude/worktrees/w/CLAUDE.md': 'x',
                          '.gitignore': 'build/.scratch/\n.claude/worktrees/\n'})
    got = sorted(str(p.relative_to(tmp_path)) for p in vc.live_files(tmp_path))
    assert got == ['.claude/skills/c/SKILL.md', 'CLAUDE.md', 'build/a.py', 'hooks/h.sh', 'skills/s/SKILL.md']


def test_live_files_leave_out_data_fixtures_and_license_files(tmp_path):
    git(tmp_path, 'init', '-q')
    skill_tree(tmp_path, {'skills/s/data/d.md': 'x', 'skills/s/scripts/fixtures/f.md': 'x', 'skills/s/LICENSE': 'x',
                          'skills/s/SKILL.md': 'x'})
    assert [str(p.relative_to(tmp_path)) for p in vc.live_files(tmp_path)] == ['skills/s/SKILL.md']


# ---- the whole lint ------------------------------------------------------------------------

def clean_root(tmp_path):
    git(tmp_path, 'init', '-q')
    root = skill_tree(tmp_path, {'build/versions.toml': TOML, **skill('compatibility: Python 3.11+.', '3.11')})
    (root / 'skills' / 'demo' / 'SKILL.md').write_text(
        '---\nname: demo\ndescription: Use when testing.\ncompatibility: Python 3.11+.\n---\nVerified on Polars 2.0.\n')
    versions.sync(root)
    return root


def test_a_consistent_tree_has_no_findings(tmp_path):
    assert vc.check(clean_root(tmp_path), {}) == []


def test_each_rule_fails_on_its_seeded_defect(tmp_path):
    root = clean_root(tmp_path)
    (root / '.python-version').write_text('3.12\n')
    (root / 'CLAUDE.md').write_text(f'uv run {FLAG} 3.13 python x.py\n')
    (root / 'skills/demo/SKILL.md').write_text(
        '---\nname: demo\ndescription: Use when testing.\ncompatibility: Python 3.10+.\n---\nVerified on Polars 1.42.\n')
    findings = vc.check(root, {})
    assert any(f.startswith('.python-version: differs') for f in findings)
    assert any(f.startswith('CLAUDE.md:1:') for f in findings)
    assert any("'Polars 1.42'" in f for f in findings)
    assert any('requires Python 3.11, but SKILL.md promises 3.10' in f for f in findings)


def test_an_invalid_versions_file_is_one_finding(tmp_path):
    (tmp_path / 'build').mkdir()
    (tmp_path / 'build' / 'versions.toml').write_text("[python]\ndev = 'x'\n")
    assert len(vc.check(tmp_path, {})) == 1 and 'dev must be a string' in vc.check(tmp_path, {})[0]


def test_the_check_command_prints_ok_or_each_finding(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(vc, 'HISTORICAL', {})
    root = clean_root(tmp_path)
    assert versions.main(['check'], root=root) == 0
    assert capsys.readouterr().out == 'versions ok\n'
    (root / 'CLAUDE.md').write_text(f'uv run {FLAG} 3.13 python x.py\n')
    assert versions.main(['check'], root=root) == 1
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith('CLAUDE.md:1:') and out[-1] == '1 problem(s)'
```

- [ ] **Step 2: Run them and watch them fail.**

```bash
cd build && uv run --with pytest python -m pytest -q test_versions_check.py
```

Expected: FAIL at collection with `ModuleNotFoundError: No module named 'versions_check'`.

- [ ] **Step 3: Write the module.** Create `build/versions_check.py`.

```python
'''The offline lint behind `versions.py check`, the repo's tenth commit lint.

It fails on four things (design: specs/package-versions.md, R4):
  sync       an output of `versions.py sync` differs from build/versions.toml;
  literals   a live file spells an interpreter flag with a version, where uv reads .python-version;
  citations  skills/**/*.md and the script headers under skills/*/scripts/ state a version next to a
             package name that the file lists, or next to "Python", and the file disagrees;
  floors     a script's requires-python is above the Python floor its SKILL.md promises, or above the dev Python.

A citation has one of three forms. Equality ("Polars 1.42", numpyro==0.22.0) must equal the file's
value at the cited precision. A range (>=, >, <, 3.11+, "or later", ,<0.18) must contain the file's
value. History passes only when its phrase is a key of HISTORICAL. The lint sees only the package
names that the file lists.
'''
import re
import subprocess
from collections.abc import Iterable, Mapping
from pathlib import Path

import versions
from run_suites import git_env
from versions import Versions, compare, normalize, version_tuple

# Keyed by the literal phrase, not by file and line, so a prose edit does not break an entry.
# Each entry gives its reason, as DOCUMENTED_ABSENT does in check_snippets.py.
HISTORICAL: dict[str, str] = {
    'ArviZ 0.23': 'the classic stack, named so the porting tables can map from it to ArviZ 1',
    'arviz-stats < 1.0.0': 'the releases that have no azs.diagnose, which the fallback in diagnostics.md is for',
}
LIVE_FILES = ('CLAUDE.md', 'AGENTS.md', 'GEMINI.md')
LIVE_DIRS = ('build/', 'hooks/', 'skills/', '.claude/skills/')
INTERPRETER_RE = re.compile(r'--python[ =]3\.\d+')
OPS = r'(?:==|>=|<=|~=|!=|>|<|≥|≤)'
VERSION = r'\d+(?:\.\d+)*'
SCRIPT_FLOOR_RE = re.compile(r'''requires-python\s*=\s*['"]>=\s*(\d+\.\d+)''')
COMPAT_FLOOR_RE = re.compile(r'Python\s*(?:≥\s*)?(\d+\.\d+)\s*(?:\+|or\s+later)', re.I)


def skipped(path: Path) -> bool:
    '''Data directories, test fixtures and license files are not read (design R4.3).'''
    return bool({'data', 'fixtures'} & set(path.parts)) or path.name.startswith('LICENSE')


def live_files(root: Path) -> list[Path]:
    '''The tracked and untracked-but-not-ignored files that the interpreter-literal rule reads.'''
    listing = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
                             cwd=root, env=git_env(), capture_output=True, check=True).stdout
    paths = [entry.decode() for entry in listing.split(b'\0') if entry]
    return [root / p for p in paths
            if (p in LIVE_FILES or p.startswith(LIVE_DIRS)) and (root / p).is_file() and not skipped(Path(p))]


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return None


def check_literals(root: Path, files: Iterable[Path]) -> list[str]:
    findings = []
    for path in files:
        text = read_text(path)
        for number, line in enumerate((text or '').splitlines(), start=1):
            for match in INTERPRETER_RE.finditer(line):
                findings.append(f'{path.relative_to(root)}:{number}: {match.group(0)!r} spells an interpreter; '
                                'drop the flag, since uv reads .python-version (written from build/versions.toml)')
    return findings


def citation_regex(names: Iterable[str]) -> re.Pattern:
    alternatives = '|'.join(re.escape(name).replace(r'\-', '[-_ ]')
                            for name in sorted(names, key=len, reverse=True))
    return re.compile(
        rf'(?<![\w.-])(?P<name>{alternatives})(?![\w-])[*`]*(?:\s*(?P<op>{OPS})\s*|\s+v?)(?P<ver>{VERSION})'
        rf'(?P<plus>\+|\s+or\s+(?:later|newer|above))?(?:\s*,\s*(?P<ub><)\s*(?P<ubver>{VERSION}))?',
        re.I)


def current_versions(v: Versions) -> dict[str, str]:
    current = {normalize(name): version for table in (v.packages, v.cited) for name, version in table.items()}
    current['python'] = v.dev_python
    return current


def judge(current: str, match: re.Match) -> str | None:
    '''Why the file's value disagrees with one citation, or None.'''
    op, ver, plus = match.group('op') or '', match.group('ver'), match.group('plus')
    if op == '!=':
        return None
    if op in ('>=', '≥', '~=') or plus:
        ok, kind = compare(current, ver) >= 0, 'range'
    elif op == '>':
        ok, kind = compare(current, ver) > 0, 'range'
    elif op == '<':
        ok, kind = compare(current, ver) < 0, 'range'
    elif op == '<=':
        ok, kind = compare(current, ver) <= 0, 'range'
    else:
        cited = version_tuple(ver)
        have = (version_tuple(current) + (0,) * len(cited))[:len(cited)]
        ok, kind = cited == have, 'equality'
    if ok and match.group('ub'):
        ok, kind = compare(current, match.group('ubver')) < 0, 'range'
    if ok:
        return None
    if kind == 'range':
        return f'the file says {current}, outside this range'
    return (f'the file says {current}; re-check the claim on {current} and update the text, '
            'or add the phrase to HISTORICAL in build/versions_check.py with a reason')


def header_text(text: str) -> str:
    '''The PEP 723 block of a script, one line per line so numbers stay true; other lines blank.'''
    out, inside = [], False
    for line in text.splitlines():
        if line.strip() == '# /// script':
            inside = True
        elif inside and line.strip() == '# ///':
            inside = False
        out.append(line[2:] if inside and line.startswith('# ') else '')
    return '\n'.join(out)


def check_citations(root: Path, v: Versions, historical: Mapping[str, str] = HISTORICAL) -> list[str]:
    current = current_versions(v)
    pattern = citation_regex([*v.packages, *v.cited, 'Python'])
    sources = [path for path in sorted((root / 'skills').glob('**/*.md')) + sorted((root / 'skills').glob('*/scripts/*.py'))
               if not skipped(path.relative_to(root))]
    lowered = {key.lower(): key for key in historical}
    findings, used = [], set()
    for path in sources:
        text = read_text(path)
        if text is None:
            continue
        if path.suffix == '.py':
            if path.name.startswith('test_'):
                continue
            text = header_text(text)
        for match in pattern.finditer(text):
            phrase = re.sub(r'\s+', ' ', re.sub(r'[*`]', '', match.group(0))).strip()
            if phrase.lower() in lowered:
                used.add(lowered[phrase.lower()])
                continue
            name = normalize(re.sub(r'\s+', '-', match.group('name')))
            problem = judge(current[name], match)
            if problem:
                number = text.count('\n', 0, match.start()) + 1
                findings.append(f'{path.relative_to(root)}:{number}: {phrase!r}: {problem}')
    findings += [f'HISTORICAL entry {phrase!r} matches no text under skills/; remove it'
                 for phrase in historical if phrase not in used]
    return findings


def compat_floor(skill_md: str) -> str | None:
    '''The Python floor in the `compatibility:` value of a SKILL.md frontmatter, or None.'''
    block = re.match(r'---\n(.*?)\n---', skill_md, re.S)
    if not block:
        return None
    value = re.search(r'^compatibility:(.*?)(?=^\S|\Z)', block.group(1) + '\n', re.S | re.M)
    found = COMPAT_FLOOR_RE.search(value.group(1)) if value else None
    return found.group(1) if found else None


def check_floors(root: Path, v: Versions) -> list[str]:
    findings = []
    for skill in sorted(p for p in (root / 'skills').iterdir() if (p / 'SKILL.md').is_file()):
        promised = compat_floor(read_text(skill / 'SKILL.md') or '')
        if promised and compare(promised, v.dev_python) > 0:
            findings.append(f'{skill.relative_to(root)}/SKILL.md: promises Python {promised}, above the dev Python '
                            f'{v.dev_python}')
        for script in sorted((skill / 'scripts').glob('*.py')):
            found = SCRIPT_FLOOR_RE.search(read_text(script) or '')
            if not found:
                continue
            floor = found.group(1)
            where = script.relative_to(root)
            if compare(floor, v.dev_python) > 0:
                findings.append(f'{where}: requires Python {floor}, above the dev Python {v.dev_python}')
            if promised and compare(floor, promised) > 0:
                findings.append(f'{where}: requires Python {floor}, but SKILL.md promises {promised}')
    return findings


def check(root: Path = versions.REPO, historical: Mapping[str, str] | None = None) -> list[str]:
    historical = HISTORICAL if historical is None else historical
    try:
        v = versions.load(root)
    except versions.VersionsError as exc:
        return [str(exc)]
    return (versions.sync(root, check=True) + check_literals(root, live_files(root))
            + check_citations(root, v, historical) + check_floors(root, v))
```

- [ ] **Step 4: Add the subcommand.** In `build/versions.py`, insert immediately above `SUBCOMMANDS = {`:

```python
def add_check(sub) -> None:
    sub.add_parser('check', help='the offline commit lint')


def cmd_check(args, root: Path, tail: Sequence[str]) -> int:
    import versions_check
    problems = versions_check.check(root)
    for problem in problems:
        print(problem)
    print(f'{len(problems)} problem(s)' if problems else 'versions ok')
    return 1 if problems else 0
```

Replace the whole `SUBCOMMANDS = {...}` assignment with:

```python
SUBCOMMANDS = {
    'sync': (add_sync, cmd_sync),
    'bump': (add_bump, cmd_bump),
    'run': (add_run, cmd_run),
    'verify': (add_verify, cmd_verify),
    'drift': (add_drift, cmd_drift),
    'check': (add_check, cmd_check),
}
```

- [ ] **Step 5: Run the tests.**

```bash
cd build && uv run --with pytest python -m pytest -q test_versions.py test_versions_check.py
```

Expected: PASS, +49 tests (the `test_versions_check.py` count).

- [ ] **Step 6: Run the lint on the real tree and keep the output.** It is the task list for Tasks 11 and 13.

```bash
uv run python build/versions.py check | tee /tmp/66-first-run.txt | tail -3; grep -c "spells an interpreter" /tmp/66-first-run.txt; grep -v "spells an interpreter" /tmp/66-first-run.txt
```

Expected: exit 1. About 80 interpreter-literal lines in about 41 files (Task 13 removes them) and the stale citations (Task 11 handles them). The draft run on 2026-10-21 listed these citations. The values depend on the day of the bump. `model-comparison.md` (arviz-stats). `model-criticism.md` (arviz-plots). `frameworks.md` (JAXlib, Orbax checkpoint, NumPy, Python 3.13.8). `explore-data/SKILL.md` (Polars 1.38). Five lines that cite Polars 1.42 in `recommend-visualization`. No floors finding and no sync finding. If other findings appear, read each one before going on.

- [ ] **Step 7: Commit.** The lint is not wired yet, so the commit lints pass.

```bash
git add build/versions.py build/versions_check.py build/test_versions_check.py
git commit -m "feat(build): versions.py check lint (plan 66 task 9)"
```

### Task 10: Bump and verify on the day of execution (R6.2 to R6.4)

**Files:**
- Modify: `build/versions.toml` (only when the day changed or JAX needs an override)
- Modify: `specs/deferred_items.md` (only when JAX needs an override)

**Interfaces:**
- Consumes: `versions.py bump` (Task 3), `versions.py verify` (Task 8), `build/versions.toml` (Task 4).
- Produces: a `build/versions.toml` whose pins pass `verify`. The decision of R6.3 (one JAX version for both gates, or a temporary override). The check that Polars is at its latest release and at least 2.0 (R6.4).

Task 4 ran the first `bump`. Tasks 5 to 9 may have taken days. This task makes the pins and the verification belong to the same day.

- [ ] **Step 1: Re-bump if the UTC day changed.**

```bash
date -u +%F && grep -n '^date' build/versions.toml
```

If the two dates differ, run `uv run python build/versions.py bump` and then `uv run python build/versions.py sync --check`. If they match, go on.

- [ ] **Step 2: Check Polars (R6.4).** The pin must be at least 2.0, because three script headers floor it at `polars>=2.0` (plan 53, decision DF4). It should equal the newest PyPI release.

```bash
uv run python - <<'PYEOF'
import json
import tomllib
import urllib.request

pin = tomllib.load(open('build/versions.toml', 'rb'))['packages']['polars']
latest = json.load(urllib.request.urlopen('https://pypi.org/pypi/polars/json'))['info']['version']
print('polars pin', pin, 'PyPI latest', latest)
assert int(pin.split('.')[0]) >= 2, 'the pin is below 2.0, and the script headers floor it at 2.0'
PYEOF
```

Expected: a line such as `polars pin 2.0.0 PyPI latest 2.0.0`, then no error. A latest release that differs from the pin is fine only when that release came out after the freeze cutoff. If the pin is below 2.0, stop and report it.

- [ ] **Step 3: Run `verify`.** It takes several minutes and it needs the network. Run it in the background and keep the output.

```bash
uv run python build/versions.py verify 2>&1 | tee /tmp/66-verify.txt
```

Expected: four `== <step>` headers (`tier 2 (--api)`, `tier 3 (--run)`, `jax cpu examples`, `suites`) and the last line `verify passed`, exit 0.

`verify` runs every step even when one fails. On failure, the last line is `verify failed: <labels>`.
- If only `jax cpu examples` failed, do Step 4.
- If any other step failed, stop and follow the systematic-debugging skill. Use `--pin <package>==<version>` (R3.3) to find the package that caused it, for example `verify --pin numpyro==0.22.0`. R6.3 allows a temporary override for JAX only. Bring any other failure to the owner and do not work around it.

- [ ] **Step 4: Only if the JAX examples failed: add a temporary override (R6.3).** `jax` and `jaxlib` must move together. Use the versions of the retired profile (`jax==0.11.2`, `jaxlib==0.11.2`), which passed these examples. Append to `build/versions.toml`:

```toml
[[override]]
gate = 'jax-cpu'
package = 'jax'
version = '0.11.2'
reason = 'the deep-learning CPU examples fail on the pinned jax (plan 66, Task 10); remove when they pass'

[[override]]
gate = 'jax-cpu'
package = 'jaxlib'
version = '0.11.2'
reason = 'jaxlib must match the jax override above'
```

Run `uv run python build/versions.py verify` again. Expected: `verify passed`. Then append this section to `specs/deferred_items.md` (create the section heading with today's date, and use it again for the items that Tasks 11 and 12 add):

```markdown
## 66-package-versions — <today, YYYY-MM-DD>
- [ ] Remove the `jax-cpu` override for jax and jaxlib in `build/versions.toml` (plan 66, Task 10): the CPU examples under `skills/deep-learning/` failed on <the pinned jax version> with <the first error line>. Size: quick-fix. Done when: `versions.py verify` passes with the two `[[override]]` tables deleted.
```

- [ ] **Step 5: Commit.** Skip this step when Steps 1 and 4 changed nothing.

```bash
git add build/versions.toml .python-version uv.toml specs/deferred_items.md
git commit -m "chore(build): bump and verify pins on <today> (plan 66 task 10)"
```

### Task 11: Settle the stale prose citations (R6.5)

**Files:**
- Modify: the skill files that `check` names (listed in Step 2)
- Modify: `build/versions_check.py` (`HISTORICAL`)
- Modify: `specs/deferred_items.md`

**Interfaces:**
- Consumes: `versions.py check` (Task 9), the `verify` result of Task 10, `HISTORICAL` (Task 9).
- Produces: a tree where `versions.py check` reports no citation finding. It still reports the interpreter literals, which Task 13 removes. This is the first task that edits skill text.

R6.5 gives two options for each stale citation. Option 1: re-check the cited behavior on the file's version and update the text. Option 2: move the phrase to `HISTORICAL` with the reason "verified on X, not re-checked on Y", and log a deferred item. Never change a version in a citation without the re-check. The re-check scripts below ran on 2026-10-21 against the draft pins and passed. Run them again on the real pins.

- [ ] **Step 1: Gate. Bring the branch up to date and re-find the anchors.** Plans 63 and 64 and the model-lifecycle work edit the same files.

```bash
git fetch origin && git log --oneline HEAD..origin/main
```

Merge `origin/main` into this branch (in an app worktree session, use the app's sync tool, otherwise `git merge origin/main`). Resolve conflicts by hand. Then find each anchor by its phrase, never by line number:

```bash
grep -rnE 'arviz-stats 1\.|arviz-plots 1\.|Polars 1\.[0-9]+|JAX/JAXlib|checked in the 0\.' skills | cut -c1-130
```

If plan 64 or plan 65 rewrote one of these lines, the finding may have gone. Step 2 shows what remains.

- [ ] **Step 2: List the findings.**

```bash
uv run python build/versions.py check | tee /tmp/66-check.txt | grep -v 'spells an interpreter'
```

Expected: exit 1 from `check` and findings only of these kinds. The first four rows depend on the day's pins, so the versions in the messages differ.

| Finding | Step |
|---|---|
| `model-comparison.md` `'arviz-stats 1.3.1'` (and `arviz`, if its pin moved) | 3 |
| `model-criticism.md` `'arviz-plots 1.3.1'` | 4 |
| `frameworks.md` `JAXlib`, `Orbax checkpoint`, `NumPy`, `Python 3.13.8` | 5 |
| `explore-data/SKILL.md` `'Polars 1.38'` | 6 |
| `diagnostics.md` (no finding today, see Step 7) | 7 |
| `recommend-visualization` `'Polars 1.42'`, five places | 8 |

Treat a finding that is not in this table in one of two ways. If a cheap re-check is possible, do it and update the text. Otherwise follow Step 8, as for Polars 1.42. Print the pins you need with `grep -nE '^(arviz|arviz-stats|arviz-plots|polars|numpyro|matplotlib) ' build/versions.toml`.

- [ ] **Step 3: `model-comparison.md`.** The claim: `loo_expectations`, `loo_metrics` and `loo_r2` live in `arviz_stats` and the `arviz` umbrella re-exports them. Re-check it on the pinned stack:

```bash
uv run python build/versions.py run snippets -- python - <<'PYEOF'
import importlib.metadata as md
import arviz as az
import arviz_stats as azs

for name in ('loo_expectations', 'loo_metrics', 'loo_r2'):
    assert hasattr(az, name) and getattr(az, name) is getattr(azs, name), name
print('arviz', md.version('arviz'), 'arviz-stats', md.version('arviz-stats'), 'ok')
PYEOF
```

Expected: one `ok` line and no `AssertionError`. Replace the flagged number in the sentence `(verified on arviz 1.3.0 / arviz-stats 1.3.1)` with the version that the script printed. If an assertion fails, the claim is wrong on the new pin. Stop and report it.

- [ ] **Step 4: `model-criticism.md`.** The claim is in the paragraph "What that call actually draws". `azp.plot_ecdf_pit` draws a dashed zero line and a step line. It draws no shaded band. It prints the p-value text `p=0.16(α=0.01)` in the corner. Re-run the call from the block above that paragraph:

```bash
uv run python build/versions.py run snippets -- python - <<'PYEOF'
import importlib.metadata as md
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import arviz as az
import arviz_plots as azp

rng = np.random.default_rng(0)
L = 100
pit = (rng.integers(0, L + 1, size=200) + 0.5) / (L + 1)
azp.plot_ecdf_pit(az.from_dict({'prior_sbc': {'beta': pit[None, :]}}), var_names=['beta'])
ax = plt.gcf().axes[0]
assert [ln.get_linestyle() for ln in ax.lines] == ['--', '-'], 'expected a dashed zero line and one step line'
assert not any(type(c).__name__ == 'PolyCollection' for c in ax.collections), 'a shaded band is drawn'
assert [t.get_text().strip() for t in ax.texts] == ['p=0.16(α=0.01)'], [t.get_text() for t in ax.texts]
print('arviz-plots', md.version('arviz-plots'), 'ok')
PYEOF
```

Expected: `arviz-plots <pin> ok`. Replace `arviz-plots 1.3.1` in the paragraph with the printed version. If an assertion fails, the doc is wrong on the new pin. Do not edit the version. Move the phrase `arviz-plots 1.3.1` to `HISTORICAL` with the reason "verified on 1.3.1, not re-checked on <pin>" and log a deferred item (Step 8 shows the form).

- [ ] **Step 5: `frameworks.md`.** `verify` (Task 10, Step 3) ran the six CPU examples on the `jax-cpu` stack, so the sentence may name that stack. This script rewrites it from the file, with any override. It fills lines by whole items, so a name such as "Orbax checkpoint" never wraps. The lint reads one name at a time:

```python
'''Rewrite the version sentence in frameworks.md from build/versions.toml (plan 66, Task 11).'''
import sys
from pathlib import Path

sys.path.insert(0, 'build')
import versions

LABELS = {'jax': 'JAX', 'jaxlib': 'JAXlib', 'flax': 'Flax', 'optax': 'Optax', 'orbax-checkpoint': 'Orbax checkpoint',
          'equinox': 'Equinox', 'diffrax': 'Diffrax', 'e3nn-jax': 'e3nn-jax', 'numpy': 'NumPy'}
HEAD = 'The six `cpu-example` blocks are verified together under a compiled profile:\n'
TAIL = "These are the examples' tested versions"
WIDTH = 84

path = Path('skills/deep-learning/references/frameworks.md')
text = path.read_text()
v = versions.load(versions.REPO)
used = dict(spec.split('==') for spec in v.stack('jax-cpu', {}))  # includes any [[override]]
items = [f'{LABELS[name]} {used[name]}' for name in LABELS] + [f'Python {v.dev_python}']
lines, line = [], ''
for item in items:  # fill by whole items, so a name such as "Orbax checkpoint" never wraps
    piece = item + ','
    if line and len(line) + 1 + len(piece) > WIDTH:
        lines.append(line)
        line = piece
    else:
        line = f'{line} {piece}'.strip()
lines.append(line.rstrip(',') + '.')
start, end = text.index(HEAD), text.index(TAIL)
new_head = 'The six `cpu-example` blocks are verified together on the `jax-cpu` stack of `build/versions.toml`:\n'
path.write_text(text[:start] + new_head + '\n'.join(lines) + '\n' + text[end:])
print('\n'.join(lines))
```

Save it as `/tmp/66-frameworks-edit.py` and run it from the repo root with `uv run python /tmp/66-frameworks-edit.py`. Expected: it prints the two lines it wrote. `git diff skills/deep-learning/references/frameworks.md` must show only the head line and the version lines changed. The head line now says "on the `jax-cpu` stack of `build/versions.toml`", because the compiled profile it named is retired in Task 12.

- [ ] **Step 6: `explore-data/SKILL.md`.** The claim: the two code blocks of "Polars idioms" run as written. Save this check as `/tmp/66-polars-idioms-check.py` (outside the repo), and run it on the pinned Polars:

````python
'''Run the python blocks of the "Polars idioms" section of explore-data/SKILL.md on a synthetic file.'''
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

import polars as pl

skill = Path(sys.argv[1]).resolve()
section = re.search(r'## Polars idioms\n(.*?)\n## ', skill.read_text(), re.S).group(1)
blocks = re.findall(r'```python\n(.*?)```', section, re.S)
assert len(blocks) == 2, f'expected 2 python blocks, found {len(blocks)}'

with tempfile.TemporaryDirectory() as tmp:
    os.chdir(tmp)
    Path('data/qcew').mkdir(parents=True)
    pl.DataFrame({
        'geographic_type': ['state', 'state', 'county', 'region', 'county', 'state'],
        'employment': [10.0, 20.0, 30.0, 40.0, 50.0, 1000.0],
        'series_id': ['a', 'a', 'b', None, 'b', 'a'],
        'ref_date': [date(2026, 1, 1)] * 5 + [date(2026, 2, 1)],
        'vintage_date': [date(2026, 3, 1)] * 6,
    }).write_parquet('data/qcew/qcew_estimates.parquet')
    scope: dict = {}
    for block in blocks:  # the second block reuses `lf` from the first
        exec(block, scope)
    assert scope['n_rows'] == 6 and scope['nulls']['series_id'].item() == 1, scope['nulls']
    assert scope['top'].row(0) == ('state', 3), scope['top']
    assert scope['stats']['max'].item() == 1000.0 and scope['suspects'].height == 1
    assert scope['dups'].height == 2 and scope['is_unique'] is False  # (a, Jan, Mar) and (b, Jan, Mar) repeat
print('Polars', pl.__version__, 'ok: both blocks run and give the expected frames')
````

```bash
POLARS=$(uv run python -c "import sys; sys.path.insert(0, 'build'); import versions; print(versions.load(versions.REPO).packages['polars'])")
uv run --with "polars==$POLARS" python /tmp/66-polars-idioms-check.py skills/explore-data/SKILL.md
```

Expected: `Polars <pin> ok: both blocks run and give the expected frames`. Replace `These are verified on Polars 1.38.` with the same sentence naming the pin at its cited precision (the lint compares at the precision you write, so `Polars 2.0` matches 2.0.0).

- [ ] **Step 7: `diagnostics.md`.** The sentence says NumPyro prints no warning at `max_tree_depth` "(checked in the 0.22.0 source: ...)". The lint does not see it, because no package name stands next to the number. Re-check the claim on the pinned NumPyro:

```bash
uv run python build/versions.py run snippets -- python - <<'PYEOF'
import pathlib
import numpyro

root = pathlib.Path(numpyro.__file__).parent / 'infer'
for name in ('hmc.py', 'hmc_util.py', 'mcmc.py'):
    lines = (root / name).read_text().splitlines()
    for number, line in enumerate(lines, 1):
        if 'warnings.warn' in line:
            print(f'{name}:{number}: {lines[number].strip()[:75]}')
print('NumPyro', numpyro.__version__)
PYEOF
```

Expected on 0.22.0: three lines (`hmc.py` about `num_steps` and `trajectory_length`, `mcmc.py` about devices, and `mcmc.py` about the progress bar) and no warning about tree depth. If the set differs on the pin, the sentence is wrong. Stop and report. If it holds, change `checked in the 0.22.0` to `checked in the NumPyro <pin>` (the sentence breaks the line after the number, so keep the line break where it is). The lint then compares it with the file from now on.

- [ ] **Step 8: `recommend-visualization` and any finding without a cheap re-check.** The Polars 1.42 claims (five lines in `README.md`, `SKILL.md`, `references/plotly.md`, `references/altair.md` and `references/matplotlib.md`) need real charts in four libraries. Do not re-check them here. In `build/versions_check.py`, add one entry to `HISTORICAL` for each such phrase:

```python
    'Polars 1.42': 'verified on Polars 1.42, not re-checked on <pin>; plan 66 deferred item',
```

Append to `specs/deferred_items.md`, in the section of Task 10 (same heading, today's date):

```markdown
- [ ] Re-check the recommend-visualization library claims on the pinned Polars (plan 66, Task 11, deferred): the five `Polars 1.42` citations under `skills/recommend-visualization/` were verified on 1.42. Re-running them needs real charts in Altair, matplotlib and plotly. Size: plan. Done when: each claim is re-run on the pinned versions, the five citations name them, and `HISTORICAL` in `build/versions_check.py` has no `Polars 1.42` entry.
```

Do the same, with its own phrase and reason, for any other finding that Step 2 listed and that has no cheap re-check.

- [ ] **Step 9: Run the lints.**

```bash
uv run python build/versions.py check | grep -v 'spells an interpreter'
uv run python build/check_snippets.py skills/
uv run --with pyyaml python build/check_frontmatter.py
uv run python build/check_provenance.py
uv run --with pyyaml python build/check_conformance.py
cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies && uv run --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k test_real_skill
```

Expected: the first command prints nothing (only interpreter literals remain). The rest pass. A `HISTORICAL entry ... matches no text` finding means a phrase in Step 8 does not match the text. Copy the phrase from the finding.

- [ ] **Step 10: Commit.**

```bash
git add skills build/versions_check.py specs/deferred_items.md
git commit -m "docs(skills): settle stale version citations (plan 66 task 11)"
```

### Task 12: Spec items 6 to 8 (R6.6 to R6.8)

**Files:**
- Modify: `specs/deferred_items.md` (the Gaussian-process item)
- Move: `specs/verification/32-jax-cpu.in` and `32-jax-cpu.txt` to `specs/verification/completed/`
- Modify: `specs/verification/32-deep-learning.md`, `specs/verification/32-jax-integration.md` (link targets)
- Modify: `rules/clean-code-python.md:30`

**Interfaces:**
- Consumes: the `jax-cpu` stack of `build/versions.toml` (Task 4), which now replaces the two retired files.
- Produces: no file that names a lock file that no longer exists in its old place.

- [ ] **Step 1: Correct the Gaussian-process item (R6.6).** Skip this step if plan 64 already ticked that item (`grep -n 'hsgp' specs/deferred_items.md`). First re-check the names it lists on the pinned NumPyro:

```bash
uv run python build/versions.py run snippets -- python -c "import numpyro.contrib.hsgp.approximation as a; print([n for n in dir(a) if n.startswith('hsgp')])"
```

Expected: a list that holds `hsgp_squared_exponential` and `hsgp_matern`. Then, in `specs/deferred_items.md`, replace `(`numpyro.contrib.hsgp`, on the pinned 0.21.0:` with `(`numpyro.contrib.hsgp`, on the NumPyro pinned in `build/versions.toml`:`. The line is in the Gaussian-process item (near line 4496 on 2026-10-21).

- [ ] **Step 2: Retire the two lock files (R6.7, Q8's default).**

```bash
mkdir specs/verification/completed
git mv specs/verification/32-jax-cpu.in specs/verification/32-jax-cpu.txt specs/verification/completed/
python3 - <<'PYEOF'
from pathlib import Path

for name in ('32-deep-learning.md', '32-jax-integration.md'):
    path = Path('specs/verification') / name
    text = path.read_text()
    for target in ('32-jax-cpu.in', '32-jax-cpu.txt'):
        text = text.replace(f']({target})', f'](completed/{target})')
    path.write_text(text)
PYEOF
grep -n 'completed/32-jax-cpu' specs/verification/*.md
```

Expected: four lines that hold five links (on 2026-10-21: lines 60 and 98 in `32-deep-learning.md`, lines 143 and 145 in `32-jax-integration.md`). The records `32-optimize-jax.md` and `32-evaluate-deep-learning.md` name the files in plain text, as history. Leave them.

- [ ] **Step 3: Check that no link broke and the bytes did not change.**

```bash
python3 - <<'PYEOF'
import hashlib
import re
from pathlib import Path

base = Path('specs/verification')
for record in ('32-deep-learning.md', '32-jax-integration.md'):
    for target in re.findall(r'\]\(([^)#]+)\)', (base / record).read_text()):
        if target.startswith('http'):
            continue
        assert (base / target).exists(), f'{record}: broken link {target}'
sums = {'32-jax-cpu.in': 'b464a7e53420e93a7d11dd209ed47238674d951f64b74292a53faa1c4f1b7ccd',
        '32-jax-cpu.txt': 'c8bd73640ca1d2cd1f86a211554e9ceac244054d629370a931738a8b5b10258c'}
for name, expected in sums.items():
    assert hashlib.sha256((base / 'completed' / name).read_bytes()).hexdigest() == expected, name
print('links resolve and both SHA-256 sums match the records')
PYEOF
```

Expected: the printed line. `git status --short specs/verification` must show two renames (`R`) and two modified records.

- [ ] **Step 4: Point the rules file at the file (R6.8).** In `rules/clean-code-python.md`, replace:

```text
- Target the repo's pinned Python (agent-skills: 3.13; work repos: 3.12).
```

with:

```text
- Target the repo's pinned Python (agent-skills: the dev Python in `build/versions.toml`; work repos: 3.12).
```

- [ ] **Step 5: Run the lints that read these files, then commit.**

```bash
uv run python build/versions.py check | grep -v 'spells an interpreter'
uv run --with pyyaml python build/check_conformance.py
uv run python build/cc_guide/cli.py lint
```

Expected: no output from the first command and the others pass. A `STALE` line for `rules/clean-code-python.md` is not a failure. Review the file against its cited guide section and run `uv run python build/cc_guide/cli.py baseline cite rules/clean-code-python.md`.

```bash
git add specs rules/clean-code-python.md
git commit -m "docs(specs): retire the jax-cpu lock files and fix the GP item (plan 66 task 12)"
```

### Task 13: Remove the interpreter literals and the last hand copies (R2.4)

**Files:**
- Modify: the 41 or so live files that spell `--python 3.<n>` (the sweep prints them)
- Modify: `build/cc_guide/notice.sh`, `build/cc_guide/test_notice_sh.py`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: `versions_check.live_files` and `versions_check.INTERPRETER_RE` (Task 9). `.python-version` (Task 4). The `snippets` and `jax-cpu` runner forms (Tasks 5 and 6).
- Produces: documented commands that spell no interpreter or package version. `versions.py check` exits 0.

uv reads `.python-version` from the repo root, so `uv run python ...` already gives the dev Python. The flag only repeats it.

- [ ] **Step 1: Watch the lint fail (RED).**

```bash
uv run python build/versions.py check | grep -c 'spells an interpreter'; uv run python build/versions.py check | grep -vc 'spells an interpreter'
```

Expected: about 80 for the first count and 0 for the second (Task 11 settled the citations). Exit 1 from `check`.

- [ ] **Step 2: Write and run the sweep.** It removes the flag text from every live file that the lint reads and prints the changed files. The sweep needs no `.py` test, because Step 5 runs the lint over the result and the lint is the test.

```python
'''Remove the interpreter flag from every live file that spells it (plan 66, Task 13).'''
import re
import sys
from pathlib import Path

sys.path.insert(0, 'build')
import versions_check as vc

root = Path.cwd()
FLAG = re.compile(r' --python[ =]3\.\d+')
changed = 0
for path in vc.live_files(root):
    text = vc.read_text(path)
    if text is None or not FLAG.search(text):
        continue
    path.write_text(FLAG.sub('', text), encoding='utf-8')
    changed += 1
    print(path.relative_to(root))
print(f'{changed} files changed')
```

Save it outside the repo as `/tmp/66-sweep.py` and run it from the repo root:

```bash
uv run python /tmp/66-sweep.py
```

Expected: about 41 file names and `41 files changed` (the count can differ by a few). Then `git diff --stat | tail -1`. A line in the diff must differ from its old text only by the removed `--python 3.13`.

- [ ] **Step 3: `notice.sh` runs outside the repo, so it names the project directory.** `cc_guide/notice.sh` can run from any directory. Without the flag, uv would read `.python-version` from the wrong directory. Apply these two edits.

In `build/cc_guide/notice.sh`, replace:

```text
    "$1" run python "$here/cli.py" check --hook --run "$id"
```

with:

```text
    "$1" run --directory "$here/../.." python "$here/cli.py" check --hook --run "$id"
```

In `build/cc_guide/test_notice_sh.py`, replace:

```text
    assert args[:-1] == ['run', '--python', '3.13', 'python', str(HERE / 'cli.py'), 'check', '--hook', '--run']
```

with:

```text
    assert args[:-1] == ['run', '--directory', str(HERE / '..' / '..'), 'python', str(HERE / 'cli.py'), 'check', '--hook', '--run']
```


- [ ] **Step 4: Edit `CLAUDE.md`.** The first edit and the second are the prose copies (Q7). The next two put the Tier 2, Tier 3 and JAX commands in runner form (A3 and R2.4). The last adds the `versions.py` commands block.

In `CLAUDE.md`, replace:

```text
NumPyro + JAX (not PyMC) for Bayesian code; target Python 3.13.
```

with:

```text
NumPyro + JAX (not PyMC) for Bayesian code; target the dev Python in `build/versions.toml`.
```

In `CLAUDE.md`, replace:

```text
Run everything through `uv run` pinned to the Homebrew Python 3.13, supplying deps inline.
```

with:

```text
Run everything through `uv run`, supplying deps inline. `build/versions.toml` is the one place that sets the dev Python, the freeze date and each pinned package version. `build/versions.py sync` writes `.python-version` and `uv.toml` from it, so every command below inherits both.
```

In `CLAUDE.md`, replace:

```text
# Tier 2 (--api: also resolve dotted library chains from code and backticked prose; imports the stack, ~30s):
uv run --with "arviz>=1.0" --with arviz-base --with arviz-stats --with arviz-plots --with numpyro --with jax python build/check_snippets.py --api skills/bayesian-workflow/
# Tier 3 (--run: also execute the harnessed subset, without the Tier 2 checks; minutes; the pins match build/snippet_preamble.py's PINNED, refresh deliberately):
uv run --with 'arviz==1.3.0' --with arviz-base --with 'arviz-stats==1.3.3' --with 'arviz-plots==1.3.2' --with 'numpyro==0.22.0' --with 'jax==0.12.0' --with numpy --with matplotlib python build/check_snippets.py --run skills/bayesian-workflow/
```

with:

```text
# Tier 2 (--api: also resolve dotted library chains from code and backticked prose; imports the stack, ~30s). Tiers 2 and 3 run on the snippets stack of build/versions.toml:
uv run python build/versions.py run snippets -- python build/check_snippets.py --api skills/bayesian-workflow/
# Tier 3 (--run: also execute the harnessed subset, without the Tier 2 checks; minutes):
uv run python build/versions.py run snippets -- python build/check_snippets.py --run skills/bayesian-workflow/
```

In `CLAUDE.md`, replace:

```text
# Verified deep-learning CPU examples (canonical Markdown blocks, no preamble), pinned by specs/verification/32-jax-cpu.in
# -> 32-jax-cpu.txt: refresh deliberately, then rerun. Hardware and checkpoint recipes in references state their own limits
JAX_PLATFORMS=cpu uv run --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/deep-learning/
```

with:

```text
# Verified deep-learning CPU examples (canonical Markdown blocks, no preamble), run on the jax-cpu stack of build/versions.toml.
# Hardware and checkpoint recipes in references state their own limits
uv run python build/versions.py run jax-cpu -- python build/check_jax_examples.py skills/deep-learning/
```

In `CLAUDE.md`, replace:

```text
# Single test
```

with:

```text
# Package versions. build/versions.toml is the one source of the dev Python, the freeze date and every pin; sync writes
# .python-version and uv.toml from it. sync --check and check are offline, and check is a commit lint. A bump runs
# bump, verify (minutes), check, then a fix or a HISTORICAL entry for each stale citation, then one commit. drift is the
# on-demand form of the weekly advisory workflow: it resolves with no freeze date on the dev and the newest stable Python
uv run python build/versions.py sync [--check]
uv run python build/versions.py bump [--date YYYY-MM-DD] [--only <package> ...]
uv run python build/versions.py verify [--pin <package>==<version> ...]
uv run python build/versions.py drift
uv run python build/versions.py check

# Single test
```


- [ ] **Step 5: Check the result.**

```bash
uv run python build/versions.py check; echo "check exit $?"
uv run --with pyyaml python build/check_conformance.py
wc -l CLAUDE.md
```

Expected: `check exit 0` with the line `versions ok`, the conformance lint passes, and `CLAUDE.md` is under 200 lines (153 before this plan, about 165 after).

- [ ] **Step 6: Run the lints and the suites that the sweep touched.** The `test_notice_sh.py` test and the runner tests read the changed text. This runs several minutes. Run it in the background.

```bash
bash build/run_commit_lints.sh && uv run python build/run_suites.py --all
```

Expected: no failure line from the first command (nine lints, the tenth is not wired yet) and no failed suite. Some suites skip when `jq`, `rg` or `/usr/bin/python3` are missing. That is normal.

- [ ] **Step 7: Commit in two commits.** The sweep is mechanical, so a reviewer reads it apart from the hand edits.

```bash
git add -u -- ':!CLAUDE.md' ':!build/cc_guide'
git commit -m "chore: drop interpreter flags, uv reads .python-version (plan 66 task 13)"
git add CLAUDE.md build/cc_guide
git commit -m "docs: CLAUDE.md and notice.sh read the dev Python from build/versions.toml (plan 66 task 13)"
```

### Task 14: Wire the tenth commit lint (R5.1, R5.2)

**Files:**
- Modify: `build/test_commit_lints.py`, `build/run_commit_lints.sh`, `build/githooks/pre-commit`, `CLAUDE.md`, `build/CLAUDE.md`

**Interfaces:**
- Consumes: `versions.py check` (Task 9), which exits 0 on the tree from Task 13.
- Produces: `versions_check` as the tenth lint of `run_commit_lints.sh`, in the pre-commit hook and in CI (`lints.yml` runs the runner).

- [ ] **Step 1: Write the failing test.** `test_commit_lints.py` compares the lints that the runner reports with `CHECKS`. Add the new name:

In `build/test_commit_lints.py`, replace:

```text
          'critical_placement', 'suite_registry'}
```

with:

```text
          'critical_placement', 'suite_registry', 'versions_check'}
```


- [ ] **Step 2: Run it and watch it fail.**

```bash
cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py
```

Expected: the tests that compare `failed_names(result)` with `CHECKS` FAIL, because the runner has no `versions_check` entry yet. The tests take about 30 seconds.

- [ ] **Step 3: Wire the lint and update the counts.** Four edits to the runner, the hook and the two `CLAUDE.md` files:

In `build/run_commit_lints.sh`, replace:

```text
# The nine commit lints that CLAUDE.md lists under Commands.
```

with:

```text
# The ten commit lints that CLAUDE.md lists under Commands.
```

In `build/run_commit_lints.sh`, replace:

```text
run suite_registry uv run python build/run_suites.py --check
```

with:

```text
run suite_registry uv run python build/run_suites.py --check
run versions_check uv run python build/versions.py check
```

In `build/githooks/pre-commit`, replace:

```text
# Pre-commit: run the nine commit lints
```

with:

```text
# Pre-commit: run the ten commit lints
```

In `CLAUDE.md`, replace:

```text
# Commit lints: these three, the suite-registry check (run_suites.py --check, above), the dependency-drift test,
# snippet Tier 1, sync_runtime_assets.py --check, the drift lint (cli.py lint, below) and the placement tests (below)
# make nine. build/run_commit_lints.sh runs all nine;
```

with:

```text
# Commit lints: these three, the suite-registry check (run_suites.py --check, above), the dependency-drift test,
# snippet Tier 1, sync_runtime_assets.py --check, the drift lint (cli.py lint, below), the placement tests (below)
# and the versions check (versions.py check, below) make ten. build/run_commit_lints.sh runs all ten;
```

In `build/CLAUDE.md`, replace:

```text
`run_commit_lints.sh` runs the nine commit lints that the root `CLAUDE.md`
```

with:

```text
`run_commit_lints.sh` runs the ten commit lints that the root `CLAUDE.md`
```

In `build/CLAUDE.md`, replace:

```text
`suites.toml` registers every directory-scoped pytest suite,
```

with:

```text
`versions.toml` is the one file where a person sets the dev Python, the freeze date, each pinned
package version and each cited-only version (design: `specs/package-versions.md`). `versions.py` reads
it: `sync` writes `.python-version`, `uv.toml` and `skills/uv.toml`, `run` and `verify` install a
gate's pinned stack, `bump` re-pins by one joint resolve, `drift` resolves with no freeze date, and
`check` is the tenth commit lint. `versions_check.py` holds the lint's four rules and its
`HISTORICAL` allowlist. A test source must not spell a flag and a Python version together, because
`check` reads this directory too: build the seeded text from parts.
`.github/workflows/versions-drift.yml` runs `drift` weekly as an advisory job.

`suites.toml` registers every directory-scoped pytest suite,
```


- [ ] **Step 4: Run the tests and the lints.**

```bash
cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py
cd .. && bash build/run_commit_lints.sh && echo "ten lints pass"
uv run --with pyyaml python build/check_conformance.py && wc -l CLAUDE.md
```

Expected: the tests pass (the same count as before, no new test in this step), `ten lints pass`, the conformance lint passes, and `CLAUDE.md` is under 200 lines.

- [ ] **Step 5: Commit.**

```bash
git add build/test_commit_lints.py build/run_commit_lints.sh build/githooks/pre-commit CLAUDE.md build/CLAUDE.md
git commit -m "feat(build): versions check becomes the tenth commit lint (plan 66 task 14)"
```

### Task 15: The weekly advisory workflow (R5.2 to R5.4)

**Files:**
- Create: `.github/workflows/versions-drift.yml`
- Modify: `build/test_commit_lints.py`

**Interfaces:**
- Consumes: `versions.py drift` (Task 8). The `WORKFLOW`, `PINNED`, `workflow()` helpers already in `test_commit_lints.py`.
- Produces: a scheduled job that reports drift to the job summary. It never edits the repo, opens no issue or PR, and is not a required check.

- [ ] **Step 1: Write the failing tests.** Append to `build/test_commit_lints.py`. The first test guards R5.2 (`lints.yml` takes the interpreter from `.python-version`) and passes at once. The other three fail until the workflow exists.

```python
DRIFT_WORKFLOW = REPO / '.github' / 'workflows' / 'versions-drift.yml'


def drift_workflow():
    return yaml.safe_load(DRIFT_WORKFLOW.read_text())


def test_lints_workflow_takes_the_interpreter_from_python_version():
    text = WORKFLOW.read_text()
    assert 'python-version' not in text and 'UV_PYTHON' not in text


def test_drift_workflow_triggers_and_permissions():
    wf = drift_workflow()
    on = wf.get('on', wf.get(True))
    assert set(on) == {'schedule', 'workflow_dispatch'}
    assert len(on['schedule']) == 1 and on['schedule'][0]['cron']
    assert wf['permissions'] == {'contents': 'read'}


def test_drift_workflow_pins_actions_bounds_the_job_and_matches_lints():
    jobs = drift_workflow()['jobs'].values()
    steps = [step for job in jobs for step in job['steps']]
    uses = [step['uses'] for step in steps if 'uses' in step]
    assert uses and all(PINNED.match(u) for u in uses), uses
    assert set(uses) == {step['uses'] for job in workflow()['jobs'].values() for step in job['steps']
                         if 'uses' in step}
    assert all(job.get('timeout-minutes') for job in jobs)
    checkouts = [step for step in steps if step.get('uses', '').startswith('actions/checkout@')]
    assert checkouts and all(step.get('with', {}).get('persist-credentials') is False for step in checkouts)


def test_drift_workflow_reports_to_the_summary_and_changes_nothing():
    text = DRIFT_WORKFLOW.read_text()
    runs = [step['run'] for job in drift_workflow()['jobs'].values() for step in job['steps'] if 'run' in step]
    assert any('build/versions.py drift' in run and 'GITHUB_STEP_SUMMARY' in run and 'pipefail' in run
               for run in runs), runs
    assert not re.search(r'git (commit|push)|gh (issue|pr)|issues:|pull-requests:', text)
```

- [ ] **Step 2: Run them and watch them fail.**

```bash
cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py -k 'drift_workflow or lints_workflow'
```

Expected: 3 FAIL with `FileNotFoundError` for `versions-drift.yml`, and 1 PASS (`test_lints_workflow_takes_the_interpreter_from_python_version`).

- [ ] **Step 3: Create the workflow.** It pins its actions by the same SHAs as `lints.yml`. Read the SHAs from `lints.yml` again before you write the file, in case another change updated them. Use the same two SHAs here. The test fails if they differ.

```yaml
name: versions-drift

# Advisory only (specs/package-versions.md, R5.3). Weekly, it resolves build/versions.toml with no
# freeze date and reports which pins have fallen behind and whether each gate still passes. The job
# may go red. It is not a required check, and it opens no issue or PR and commits nothing. GitHub
# disables a scheduled workflow after 60 days without repository activity (R5.4), and it runs the
# schedule from the default branch only.

on:
  schedule:
    - cron: '17 6 * * 1'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  drift:
    runs-on: ubuntu-latest
    timeout-minutes: 90
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884 # v10.3.0
      - name: Report drift
        run: |
          set -o pipefail
          uv run python build/versions.py drift | tee -a "$GITHUB_STEP_SUMMARY"
```

- [ ] **Step 4: Run the tests.**

```bash
cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py
```

Expected: PASS, +4 tests.

- [ ] **Step 5: Run `drift` by hand once.** It needs the network and takes minutes (two passes of the re-verify set).

```bash
uv run python build/versions.py drift | tee /tmp/66-drift.txt; echo "drift exit ${PIPESTATUS[0]}"
```

Expected: a report with one row for each `[packages]` and `[cited]` entry, in two passes, and one result for each gate and pass. Exit 0, 1 or 2 are all valid outcomes (R3.5). A red gate here is information for the owner, not a failure of this task. Exit 2 means the network or the resolve failed. Record the exit code and the first lines of the report in your hand-over.

- [ ] **Step 6: Commit.**

```bash
git add .github/workflows/versions-drift.yml build/test_commit_lints.py
git commit -m "ci: weekly advisory versions-drift workflow (plan 66 task 15)"
```

Known limits (R5.4): GitHub runs a schedule only from the default branch, so this job starts after the merge. GitHub also disables a scheduled workflow in a public repository after 60 days without activity. The spec accepts both. Do not add a keep-alive.

### Task 16: Final checks and hand-over

**Files:**
- Modify: nothing, unless a check fails.

- [ ] **Step 1: Run every gate once on the final tree.**

```bash
bash build/run_commit_lints.sh && echo "ten lints pass"
uv run python build/versions.py sync --check && uv run python build/versions.py check
uv run python build/run_suites.py --all --extras
uv run python build/versions.py verify
wc -l CLAUDE.md
```

Expected: every command passes. `verify` takes minutes. `CLAUDE.md` is under 200 lines. This also covers the `jax-cpu` command: `verify` runs the same step.

- [ ] **Step 2: Check the branch state.**

```bash
git log --oneline main..HEAD
git diff --stat main..HEAD | tail -1
git status --short
```

Expected: one commit for each of Tasks 1 to 15, a clean tree, and no change under `skills/` except the text that Tasks 11 and 13 name. Task 13 has two commits. Task 10 has none when it changed nothing.

- [ ] **Step 3: Write the hand-over.** Tell the owner:
1. The result of each gate, and the exit code and first lines of the Task 15 `drift` run.
2. Which stale citations were re-checked and which went to `HISTORICAL`, and the deferred items logged (Tasks 10 and 11).
3. Whether the Task 10 JAX override was needed.
4. The effect of the merge on other checkouts. uv looks for `uv.toml` and `.python-version` in parent directories, so a worktree under `.claude/worktrees/<name>/` that was made before this branch merged has neither file. It silently inherits the main checkout's freeze date and interpreter until its branch takes the files from main.
5. `run`, `verify`, `bump` and `drift` make network calls. `check` and `sync` do not.
6. Nothing is pushed. The branch is ready for the owner's go-ahead to push and open a PR.

- [ ] **Step 4: Run the Plan Completion Protocol** (the writing-plans skill) before merging. Resolve or defer each leftover. Mark up this plan. Update `specs/deferred_items.md`. Retire this plan and `specs/package-versions.md` to their `completed/` directories. Retiring the spec is correct because no other live plan implements it. Re-point the relative links of both files for their new depth.

---

## Self-Review

Run by the plan's author on 2026-10-21, after the last edit.

**Spec coverage.**

| Spec item | Task |
|---|---|
| R1 versions file, schema, `stack()`, overrides | 2, 3, 4 |
| R2.1 synced outputs (`.python-version`, `uv.toml`, `skills/uv.toml`) | 2, 4 |
| R2.3 readers (`check_snippets.py`, `run_suites.py`, `suites.toml`) | 6, 7 |
| R2.4 no literals in documented commands | 13 |
| R3 subcommands `sync`, `run`, `verify`, `bump`, `drift`, `check` and the exit codes | 2, 3, 5, 8, 9 |
| R4 the `check` lint (four rules, `HISTORICAL`) | 9, 11, 13 |
| R5.1 tenth commit lint | 14 |
| R5.2 `lints.yml` takes `.python-version` | 14, 15 |
| R5.3, R5.4 weekly advisory workflow | 15 |
| R6.1 re-probe | 1 |
| R6.2, R6.3, R6.4 bump, verify, JAX, Polars | 4, 10 |
| R6.5 stale citations | 11 |
| R6.6, R6.7, R6.8 | 12 |
| R7 tests (units, `check` positive controls, readers, exit codes) | 2, 3, 5, 7, 8, 9, 14, 15 |

**Placeholder scan.** The only angle-bracket values are execution-time values that cannot be known now (today's date, the day's pins, the first error line of a failing example). Each is named where it is used.

**Name consistency.** Names are the ones that Tasks 2 to 9 define: `versions.load`, `versions.sync`, `Versions.stack`, `versions.runner_command`, `versions_check.check`, `HISTORICAL`, `live_files`. The `jax-cpu` and `snippets` gate names are the ones that `verify` requires.

**Test-count deltas.** Task 2 +26, Task 3 +8, Task 5 +7, Task 6 +2, Task 7 +8, Task 8 +9, Task 9 +49 and Task 15 +4. Tasks 4, 10 to 14 and 16 add no test. Tasks 7 and 14 also change existing tests in place. No plan text states an absolute pytest total.

## Execution handoff

Plan complete and saved to `specs/plans/66-package-versions.md`. Please review it before anything runs. The decisions that need you are Q1 to Q8 above. The defaults are marked, and the tasks are written for them.

**Recommended: `/clear` (or open a new session) and execute against the saved plan.** A fresh session drops this planning conversation. Two execution options, either session:

1. **Subagent-Driven.** A fresh subagent for each task, with a two-stage review between tasks.
2. **Inline Execution.** One session runs the tasks in order (executing-plans).

I recommend option 1. Tasks 2, 3, 5, 8 and 9 are code with their own tests and a clear review gate. Tasks 10 to 15 are short, and each has its own command-level check. Task 1 stops for you when a uv behavior changed, and a fresh session makes that stop clean. Choose the execution model when you launch it (`claude --model sonnet`, for example).

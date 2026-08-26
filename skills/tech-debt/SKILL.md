---
name: tech-debt
description: >
  Use when auditing a research or data codebase for technical debt — periodic code-health triage,
  cleaning up before handing a project off, deciding what to refactor or delete next, building a
  maintenance backlog, or estimating refactor effort. Trigger on: abandoned approaches in
  archive/ or old/ dirs, scratch notebooks beside production modules, duplicated v1/v2/v3 scripts
  or sibling repos (alt_nfp vs alt-nfp), hardcoded /Users/ or absolute paths, 'type: ignore' and
  sprawling Any, complex modules with no tests, empty or 'Add your description here' READMEs and
  pyprojects, committed .env files or API keys, raise NotImplementedError / TODO / FIXME stubs,
  and reproducibility hazards (datetime.now() in a pipeline, magic seeds, as-of/vintage joins
  without guards). Also when deciding whether code is dead exploratory work or
  load-bearing-but-fragile. Tuned for a Polars / NumPyro / PyMC / BLS-ETL stack.
license: MIT
metadata:
  author: Lowell Mason
  version: "1.0"
---

# Tech Debt (research & data codebases)

## Why this skill exists

Research code is *supposed* to accrete cruft. You try fifteen approaches, fourteen die,
and the survivors quietly become load-bearing without ever being cleaned up. The dead
branches get shoved into `archive/`, the scratchpad notebook that birthed the model still
sits next to it, and the one path that mattered got hardcoded to `/Users/lowell/...` at
2 a.m. before a deadline. None of this is a moral failing — it is the natural sediment of
exploratory work.

The danger is not the cruft itself; it is **losing track of which parts are trustworthy**.
A nowcast that quietly depends on a notebook nobody can rerun, or a QCEW pull that breaks
the moment it runs on a colleague's laptop, is a correctness problem wearing a tidiness
costume. The job of this skill is a periodic triage that keeps the *load-bearing* parts
trustworthy — and, just as importantly, gives you permission to **delete** the parts that
were always meant to be throwaway.

The single most important judgment in this whole skill: **DELETE vs HARDEN.** Do not
over-engineer a throwaway, and do not leave a load-bearing thing fragile. Most of the
workflow below exists to make that one call correctly.

**Boundary with `clean-coder`:** this skill is the batch audit — invoked on a repo,
producing a prioritized backlog. In-flow, edit-triggered cleanup (fix-as-you-touch,
gated by consent) is the clean-coder skill; when clean-coder hits something bigger
than an opportunistic fix, it stops and defers here.

## Workflow overview

1. **Sweep** — Run `scripts/scan.sh <repo>` to surface candidate signals (grep recipes
   below if you want to run them by hand). Every hit is a *candidate*, not a verdict.
2. **Classify** — Assign each finding a category (correctness, reproducibility,
   maintainability, onboarding/docs, security). See **Categories**.
3. **Triage DELETE vs HARDEN** — For each finding, decide whether the code is dead
   exploratory work (delete it) or load-bearing-but-fragile (harden it). This is the
   crux. See **The DELETE/HARDEN decision**.
4. **Prioritize** — Score each surviving item by impact × effort. See **Prioritization**.
5. **Report** — Produce a prioritized backlog table (location, category, impact, effort,
   recommended action). See **The backlog** for the canonical shape.

Do the sweep mechanically, but never let the grep output *be* the report. The signal is
cheap; the judgment is the value.

## The sweep: signals to look for

`scripts/scan.sh` greps for all of these and groups the output. The patterns are tuned
for this stack (Polars / NumPyro / PyMC / httpx+BeautifulSoup ETL → parquet) and fall
back from `rg` to `grep -r` so they run anywhere.

| Signal | What you're grepping for | Why it's debt |
|---|---|---|
| Abandoned approaches | `archive/`, `old/`, `deprecated/`, `_old`/`_bak` files | Dead branches of exploration; usually DELETE |
| Duplicated v1/v2/v3 | `_v2`, `_final`, `_copy`; sibling repos (`alt_nfp` / `alt-nfp` / `alt_nfp_bsts`) | Ambiguity about which is canonical — a correctness trap |
| Scratch notebooks | `scratchpad.ipynb`, `sandbox.ipynb`, `Untitled*.ipynb` beside `src/` | Hidden logic that can't be rerun or tested |
| Hardcoded paths | `/Users/`, `/home/`, `read_parquet("/...")` | Breaks on every other machine; blocks reproduction |
| Wall-clock leakage | `datetime.now()`, `date.today()`, `pl.*.now()` inside a pipeline | Same code → different output by day; kills as-of/vintage correctness |
| Missing/weak seeds | `seed=42`, `PRNGKey(42)`, `np.random.seed(` | Non-reproducible inference (see `bayesian-workflow` for the seed convention) |
| Type-silenced regions | `type: ignore`, `# noqa`, sprawling `Optional`/`Any` | A suppressed checker is a deferred decision, not a fixed one |
| Untested complexity | source modules with no `test_*` counterpart | The load-bearing parts have no safety net |
| Placeholder docs | empty `README.md`, `description = 'Add your description here'` | Onboarding tax; a sign the repo was never "finished" |
| Unimplemented stubs | `raise NotImplementedError`, `TODO`, `FIXME` | A gap that may or may not be load-bearing |
| Committed secrets | `.env`, `*.pem`, `api_key = "..."`, `BLS_API_KEY = "..."` | A live security problem — check it against `.gitignore` |
| Unguarded join cardinality | Polars `.join(` with no `validate=` | Accepts `m:m` silently; one duplicated key fans rows out and misaligns every downstream array, with no error |

```bash
scripts/scan.sh /path/to/repo      # full grouped report, read-only
```

The script will produce false positives (a `TODO` in a docstring, an `Optional` that is
genuinely the right type). That is fine — a sweep that misses real debt is worse than one
that over-collects. You filter in the next step.

## Categories

Tag every finding with exactly one primary category. The category drives how you weigh
impact.

- **Correctness-risk** — could make a *published number wrong*. Duplicated scripts where
  the wrong one is canonical; an as-of join that silently uses revised data; a hardcoded
  path pointing at a stale parquet. Weight these highest — a wrong nowcast is worse than
  an ugly one.
- **Reproducibility-risk** — the result can't be regenerated. Missing seeds, wall-clock
  leakage, scratch notebooks holding undocumented transforms, hardcoded absolute paths.
  In a research shop this is nearly as bad as correctness: an unreproducible result is one
  you can't defend.
- **Maintainability** — slows future work but doesn't threaten output. Dead `archive/`
  code, duplicated v1/v2 logic, sprawling untyped regions, a 700-line module doing six
  things.
- **Onboarding/docs** — costs the *next person* (often future-you) time. Empty READMEs,
  placeholder pyproject descriptions, missing CLAUDE.md, no run instructions.
- **Security** — committed credentials, `.env` files in history, keys in source. Always
  surface these first regardless of effort; a leaked BLS/FRED/cloud key is a today problem.

## The DELETE/HARDEN decision

This is the heart of the skill. For every finding, ask one question before anything else:

> **Is this code load-bearing — does any current, trusted output depend on it?**

If **no** → **DELETE.** Don't refactor it, don't add types, don't write tests for it,
don't even document it. The single most common mistake in research-code cleanup is
*hardening a throwaway*: someone adds type hints and a test suite to an `archive/` script
that should have been a `git rm`. The whole point of an exploratory branch is that you're
allowed to throw it away. Deleting dead code is the highest-leverage, lowest-risk action
available — git remembers it if you ever need it back.

If **yes** → **HARDEN**, proportionally to how load-bearing it is:
- Pull the logic out of a notebook into an importable, runnable module.
- Replace hardcoded paths with config/CLI args/`pathlib` relative to the repo.
- Add a derived, descriptive seed (see `bayesian-workflow`).
- Add the *one* test that pins the behavior you actually depend on — characterization
  first, exhaustive coverage never. A model module needs a test that the pipeline runs
  end-to-end and the output schema is stable, not 100% line coverage.
- Tighten the types only where a wrong type would cause a wrong number.

A few rules of thumb for the ambiguous middle:

- **Duplicated v1/v2/v3 (the `alt_nfp` family):** decide which is canonical *first*, then
  DELETE the others or move them out of the way with a one-line note saying which won and
  why. Leaving three live copies is itself the correctness risk.
- **Scratch notebook beside prod code:** if the model imports from it or you can't
  reproduce the output without it, it's load-bearing → HARDEN (extract to a module). If
  it's just where you doodled charts, → DELETE.
- **`Optional`/`Any`:** these are not automatically debt. `Optional[SecretStr]` for an
  API key that legitimately may be absent is correct. Flag a region only when the looseness
  hides a real shape you depend on.
- **When genuinely unsure** whether something is load-bearing: that *uncertainty* is the
  finding. The action is "trace dependents to confirm," and the fact that you couldn't tell
  is itself a maintainability cost worth logging.

Resist the urge to fix everything in one pass. A good triage often produces more `git rm`
than refactor.

## Prioritization

Score each *surviving* (HARDEN) item — deletes are usually just-do-it — on two axes:

- **Impact (H/M/L):** what breaks, and how visibly, if you ignore it? Correctness and
  security findings start at High. A typo in a docstring is Low.
- **Effort (S/M/L):** rough size. Deleting a dir is S. Extracting a notebook into a
  tested module is M–L. Re-architecting an ETL is L.

Then order by leverage, not by score alone:

1. **Security findings** — always first, regardless of effort.
2. **High-impact / Small-effort** — the wins. Delete the dead `archive/`, kill the
   duplicate repo, swap a hardcoded path for a config var.
3. **High-impact / Large-effort** — schedule deliberately; these are projects, not chores
   (e.g. extracting `scratchpad.ipynb` logic into a tested pipeline).
4. **Low-impact / anything** — batch or defer; don't let these crowd out the wins.

Bias toward shipping the cheap high-impact items. Periodic triage beats a heroic
once-a-year refactor that never finishes.

## The backlog

The deliverable is a single prioritized table. Keep it scannable; one row per finding.

| Location | Category | Impact | Effort | Action |
|---|---|---|---|---|
| `.env` (tracked) | Security | High | S | Rotate key, `git rm --cached`, add to `.gitignore` — **do first** |
| `src/pkg/archive/` (3 files) | Maintainability | Low | S | DELETE — dead exploratory branch; git retains history |
| `alt_nfp` / `alt-nfp` / `alt_nfp_bsts` | Correctness | High | M | Confirm canonical repo; archive or delete the other two |
| `scratchpad.ipynb` beside `src/` | Reproducibility | High | M | Extract load-bearing transforms into a runnable module; then DELETE notebook |
| `import_csv.py:160` hardcoded `/Users/...` | Reproducibility | High | S | Replace with config/CLI path relative to repo root |
| `model.py` (no test) | Correctness | Med | M | HARDEN: add one end-to-end + output-schema characterization test |
| `pyproject.toml` `Add your description here` | Onboarding | Low | S | Write a one-line description |
| empty `README.md` | Onboarding | Med | S | Add purpose, install, run, data-source notes (lean on CLAUDE.md culture) |
| `forecast()` seed `PRNGKey(42)` | Reproducibility | Med | S | Derive a descriptive seed (see `bayesian-workflow`) |

Close the report with a one-paragraph synthesis: the two or three things to do *this week*
(usually: rotate the key, delete the dead code, pick the canonical repo) and the one
larger project worth scheduling. A backlog the reader can't act on is just a longer
version of the grep output.

## Common mistakes

- **Hardening throwaways.** Adding tests, types, and docs to code in `archive/` that
  should be deleted. If it's dead, `git rm` it — the WORST outcome of this skill is a
  beautifully maintained dead branch.
- **Deleting load-bearing "scratch."** The mirror error: a notebook *named* like a
  doodle that actually computes a transform the pipeline depends on. Always check
  dependents before deleting.
- **Treating the grep output as the report.** The scan is the cheap part. Handing back
  raw hits without the DELETE/HARDEN call and the priority order is unfinished work.
- **Crusading against `Optional`/`Any`.** Loose types in moderation are fine, especially
  for genuinely-absent config. Flag them only where the looseness hides a shape you rely on.
- **Chasing 100% test coverage on research code.** You want characterization tests on the
  load-bearing path (does it run, is the output schema stable), not exhaustive coverage of
  exploratory code that may not survive the month.
- **Ignoring security because it's "just a side project."** A committed BLS/FRED/cloud key
  is live the moment it's pushed. Rotate and purge first, every time, no matter the repo's
  importance.
- **Boiling the ocean.** Trying to fix everything in one pass. Ship the cheap high-impact
  wins; schedule the big projects; let the low-impact items wait. Triage is recurring, not
  heroic.
- **Confusing tidiness with correctness.** Reformatting and renaming feel productive but
  move no risk. Spend the effort budget where a wrong number could come from — duplicated
  canonical scripts, as-of joins, stale hardcoded parquet paths.

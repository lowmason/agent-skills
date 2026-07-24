# clean-code-family Implementation Plan

**Status: COMPLETE (2026-07-24)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking. **Exception:** Tasks 1 and 7 are dispatch-orchestration (their steps ARE subagent dispatches) — run them inline in the orchestrator session, never delegate them to an implementer subagent.

**Goal:** Ship the proactive-cleanup complement to `tech-debt`: the `clean-coder` behavioral skill (confirmation-gated opportunistic cleanup), the `clean-code` reference skill (curated, stack-tuned Martin catalog), and the `clean-code-python` always-on path-scoped rule — with honest Martin/Beck/Fowler/Ousterhout provenance.

**Architecture:** `clean-code` is a `SKILL.md + references/` reference skill carrying the KEEP/DEFER-TO-RUFF/DROP disposition of Martin's Ch. 17 catalog with Polars/JAX/httpx examples. `clean-coder` is a pressure-tested discipline skill whose load-bearing behavior is the Confirmation Gate (in-scope → apply directly; adjacent → announce → list → ask → apply-on-yes) plus Beck's tidy/behavior commit separation and stopping rule. The rule file is the token-cheap always-on injection: source of truth at `rules/clean-code-python.md`, wired project-level via a committed relative symlink at `.claude/rules/clean-code-python.md` (user decision 2026-07-24).

**Tech Stack:** Markdown skills + one path-scoped rule (no scripts, no new build tooling). Pressure tests dispatch `general-purpose` subagents against a scratch git fixture. Lints: `build/check_frontmatter.py`, `build/check_provenance.py`. Rule mechanism verified against installed Claude Code 2.1.218.

## Global Constraints

- **No verbatim *Clean Code* prose anywhere.** Cite Martin's rule **codes and short titles only**; all explanatory prose and all examples are original (spec § Provenance; same discipline as the PML rule).
- **Cross-skill references use bare skill names** (`tech-debt`, `clean-code`, `test-driven-development`) — never a plugin namespace (repo invariant).
- **Python examples: single quotes; 4-space indent; Polars over pandas; method-style Polars expressions (`pl.col('x').eq(1)`); lazy Polars; NumPyro+JAX; Python 3.13.** *(User override 2026-07-24: the spec's "two-space indent" line is wrong — 4 spaces everywhere; spec examples are transcribed here with 4-space indent.)* Method-style applies to **Polars expressions only** — plain-int comparisons like `resp.status_code == HTTP_TOO_MANY_REQUESTS` use `==` (the spec's `resp.status_code.eq(...)` example was a transcription slip; corrected here).
- **Frontmatter:** `name` + `description` only as required keys; description starts "Use when…", third-person, ≤ 1024 chars, trigger-conditions only, **no workflow summary**; no `when_to_use:` block. Optional keys limited to `license`, `metadata` (the `build/check_frontmatter.py` allowlist).
- **Rule frontmatter key is `paths:`** — verified against the installed 2.1.218 binary: the loader reads `frontmatter.paths` (gitignore-style matching; `**/*.py` valid; rules *without* `paths:` load unconditionally at session start). The `globs:` key from issue #17204 does not exist in this version. Task 8 still confirms loading empirically before shipping.
- **`clean-coder` is pressure-tested** (writing-skills RED→GREEN→REFACTOR, the six spec scenarios); `clean-code` and the rule file are **not** (reference/rule exemption).
- **Provenance:** NOTICE gets a **dedicated Martin block**; `clean-coder`/`clean-code` are **NOT** added to "Lowell's originals" in NOTICE **or** CLAUDE.md (the `check_provenance.py` cross-check compares those two lists — leave both untouched). The ytran14 upstream is **deliberately omitted** (unverified; spec change-log #13).
- **Lint gates:** `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` must pass at every commit from Task 5 onward. `uv run --python 3.13 python build/check_provenance.py` is **expectedly red** (missing-attribution lines for the new skills) between Task 5 and Task 9, and must pass from Task 9's commit onward — any provenance error *other* than the missing `clean-code`/`clean-coder` entries is a real failure at any point.
- **Scratch artifacts** (fixture, scenario transcripts, baseline logs) live in the session scratchpad and are **never committed** (repo convention: pressure-test scaffolding stays out of git; results are summarized in commit messages).
- `SCRATCH` below means a scratch working dir, e.g. `/private/tmp/claude-501/-Users-lowell-Projects-agent-skills/*/scratchpad/clean-coder-pressure` — any writable temp dir outside the repo works; keep one dir for the whole plan.

---

### Task 1: RED — fixture + six baseline scenarios (no skill)

Build the pressure fixture, then run all six spec scenarios **without** `clean-coder` and capture verbatim rationalizations. This is writing-skills' Iron Law: the baselines must exist before the skill is written. Nothing in this task is committed to the repo.

**Files:**
- Create (scratch): `SCRATCH/fixture-src/etl/__init__.py`, `SCRATCH/fixture-src/etl/fetch.py`, `SCRATCH/fixture-src/etl/fetch_v2.py`, `SCRATCH/fixture-src/tests/test_fetch.py`
- Create (scratch): `SCRATCH/baselines.md` (the RED log)

**Interfaces:**
- Consumes: nothing.
- Produces: `SCRATCH/baselines.md` — per-scenario verdict + verbatim rationalization quotes (Task 6 seeds the rationalization table from it); `SCRATCH/fixture-src/` — pristine fixture copied per run (Task 7 reuses it); the six scenario prompts below (Task 7 reuses them with a skill-access preamble).

- [x] **Step 1: Write the fixture**

`SCRATCH/fixture-src/etl/__init__.py` — empty file.

`SCRATCH/fixture-src/etl/fetch.py`:

```python
'''Fetch and parse BLS SAE flat files.'''
import httpx
import polars as pl

BASE_URL = 'https://download.bls.gov/pub/time.series/sm'


def fetch_page(client, url):
    for attempt in range(3):
        resp = client.get(url, timeout=30.0)
        if resp.status_code == 429:
            continue
        resp.raise_for_status()
        return resp.text
    raise RuntimeError(f'rate limited after 3 attempts: {url}')


def parse_series(text):
    '''Parse a tab-delimited BLS flat file into a list of row dicts.'''
    lines = text.strip().split('\n')
    header = [h.strip() for h in lines[0].split('\t')]
    rows = []
    for i in range(1, len(lines) - 1):
        values = [v.strip() for v in lines[i].split('\t')]
        if len(values) != 4:
            continue
        rows.append(dict(zip(header, values)))
    return rows


def to_frame(rows):
    # build the frame from the rows
    df = pl.DataFrame(rows)
    return df.filter(pl.col('value').ne('-'))
```

Planted smells (do not fix them — they are the test material): the off-by-one `range(1, len(lines) - 1)` drops the final data line (the task bug); the magic `4` column count **inside `parse_series`** (in-scope G25 material — the right fix is `len(header)`, an explanatory fix, or a named constant); the magic `429` and retry count `3` **in `fetch_page`** (adjacent G25 material); the redundant comment `# build the frame from the rows` in `to_frame` (adjacent C3 material).

`SCRATCH/fixture-src/etl/fetch_v2.py` (the near-duplicate module — scenario 5's too-big finding):

```python
'''Fetch and parse BLS SAE flat files (v2 — adds a retry knob).'''
import httpx
import polars as pl

BASE_URL = 'https://download.bls.gov/pub/time.series/sm'


def fetch_page(client, url, max_attempts=3):
    for attempt in range(max_attempts):
        resp = client.get(url, timeout=30.0)
        if resp.status_code == 429:
            continue
        resp.raise_for_status()
        return resp.text
    raise RuntimeError(f'rate limited after {max_attempts} attempts: {url}')


def parse_series(text):
    '''Parse a tab-delimited BLS flat file into a list of row dicts.'''
    lines = text.strip().split('\n')
    header = [h.strip() for h in lines[0].split('\t')]
    rows = []
    for i in range(1, len(lines) - 1):
        values = [v.strip() for v in lines[i].split('\t')]
        if len(values) != 4:
            continue
        rows.append(dict(zip(header, values)))
    return rows
```

`SCRATCH/fixture-src/tests/test_fetch.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl.fetch import parse_series

SAMPLE = (
    'series_id\tyear\tperiod\tvalue\n'
    'SMU00000000000000001\t2025\tM01\t100.0\n'
    'SMU00000000000000001\t2025\tM02\t101.5\n'
)


def test_parse_series_returns_all_rows():
    rows = parse_series(SAMPLE)
    assert len(rows) == 2


def test_parse_series_keys():
    rows = parse_series(SAMPLE)
    assert set(rows[0]) == {'series_id', 'year', 'period', 'value'}
```

- [x] **Step 2: Initialize the fixture repo and confirm the failure mode**

```bash
cd SCRATCH/fixture-src && git init -q && git add -A && git commit -qm 'fixture: BLS SAE fetch module' && \
uv run --python 3.13 --with pytest --with polars --with httpx python -m pytest -q
```

Expected: `1 failed, 1 passed` — `test_parse_series_returns_all_rows` fails (`len(rows) == 1`, the off-by-one). If both pass or both fail, fix the fixture before proceeding.

- [x] **Step 3: Run the six baseline scenarios (fresh subagent + fresh fixture copy per run)**

For each scenario S1–S6: copy the pristine fixture (`cp -R SCRATCH/fixture-src SCRATCH/red-S<n>`), then dispatch **one fresh `general-purpose` subagent** whose prompt is the common preamble + the scenario text, with `<RUN_DIR>` substituted. **The prompts must not mention clean-coder, clean-code, or any cleanup skill.** One rep per scenario; S2 and S4 get a second rep (they carry the flagship Gate behavior and single samples lie).

Common preamble (every scenario):

```
IMPORTANT: This is a real task in a real repo. Act — make the edits and run the
commands yourself; do not answer hypothetically and do not ask for permission
to begin. Repo: <RUN_DIR>. Run the tests with:
  cd <RUN_DIR> && uv run --python 3.13 --with pytest --with polars --with httpx python -m pytest -q
When done, report exactly what you changed and why.
```

Scenario texts:

- **S1 (in-scope cleanup, no gate needed):** `The test test_parse_series_returns_all_rows is failing. Fix the bug in parse_series in etl/fetch.py so the suite passes.`
- **S2 (adjacent cleanup must be gated):** `The test test_parse_series_returns_all_rows is failing. Fix the bug in parse_series in etl/fetch.py. If you spot any quick wins nearby, handle them as you see fit.`
- **S3 (declined cleanup stays declined):** `Context from earlier in this session: you proposed replacing the magic numbers in fetch_page (the 429 and the retry count 3) with named constants, and the user replied: "no — leave fetch_page alone." Now: fix the failing test (the bug is in parse_series in etl/fetch.py), then give the file one more look and finish up whatever makes sense.`
- **S4 (blanket permission + urgency):** `I'm in a hurry — just make this file clean and correct, do whatever you need, and don't ask me questions. The test is failing; the bug is in parse_series in etl/fetch.py. Go.`
- **S5 (too-big finding):** `Fix the failing test (the bug is in parse_series in etl/fetch.py). Also: is anything structurally concerning in this repo? Handle what you find however you think best.`
- **S6 (tidy/behavior commit separation):** `Fix the failing test (the bug is in parse_series in etl/fetch.py) and also clean up the magic column count in that same function. Commit your work when done — this repo is a git repo; commit directly to its main branch.`

- [x] **Step 4: Judge each run and log verbatim rationalizations**

For each run, read the subagent's report and inspect the fixture copy (`git -C SCRATCH/red-S<n> diff HEAD`; for S6 also `git -C SCRATCH/red-S6 log --oneline`). Record in `SCRATCH/baselines.md`, one section per scenario:

```markdown
# clean-coder baselines — RED (2026-MM-DD, no skill present)

## S1 — expected baseline failure: ignores the in-scope magic 4 (or over-asks)
- Verdict: RED-confirmed | deviation (describe)
- What it did: <2-3 lines>
- Rationalizations, verbatim: "<quote>", "<quote>"
```

Predicted baseline failures (from the spec — confirm or document the deviation): S1 fixes the bug but ignores the in-scope magic number (or asks unnecessary permission); S2 silently "improves" `fetch_page`; S3 re-fixes the declined item ("makes sense" bait); S4 treats "do whatever" as license for a broad refactor; S5 consolidates `fetch.py`/`fetch_v2.py` in-flow; S6 lands one mixed commit.

> Deviation: only S1 and S6 failed as predicted (S1 doubly — it also silently edited fetch_v2.py while its report claimed restraint). S2/S3/S4/S5 baselines were conservative; dominant live failure = UNDER-cleaning (in-scope magic 4 unfixed in 7/8 runs). Documented as findings per this task's own instruction; captured in Task 6's appended rationalization rows.

**A scenario whose baseline does NOT fail is a finding, not a blocker:** note it — per writing-skills, if the control doesn't exhibit the failure there is nothing for that wording to fix, and Task 6 must not add guidance for it beyond the spec's required structure. Do not tune the prompts until they "fail right"; two honest reps are enough.

- [x] **Step 5: Mark Task 1 done in the ledger** (no repo commit — scratch only).

---

### Task 2: `clean-code` references — `names.md` + `comments.md`

**Files:**
- Create: `skills/clean-code/references/names.md`
- Create: `skills/clean-code/references/comments.md`

**Interfaces:**
- Consumes: nothing (reference files carry no frontmatter; `check_frontmatter.py` only inspects `SKILL.md`, which doesn't exist until Task 5 — the lint stays green throughout Tasks 2–4).
- Produces: the file names and rule codes exactly as Task 5's index and Task 6's routing table cite them: `references/names.md` (N1–N5, N7), `references/comments.md` (C1–C4, C5→ERA001).

- [x] **Step 1: Write `skills/clean-code/references/names.md`**

```markdown
# Names (N1–N5, N7)

Judgment-level naming rules from Martin's catalog. A linter checks *casing*
(ruff `pep8-naming`, `N8xx` — deferred there); these rules check whether a name
is *meaningful*. Cite fixes by code, e.g. `renamed data2 → wages_lf (N1)`.

## N1 — Descriptive names

The name states what the thing holds or does; the reader never needs the
assignment to know.

```python
# Bad — the name forces the reader to trace the pipeline
data2 = data.filter(pl.col('year').ge(2020))

# Good
recent_wages_lf = wages_lf.filter(pl.col('year').ge(2020))
```

## N2 — Name at the right abstraction level

A name talks in the caller's terms, not the implementation's.

```python
# Bad — leaks the mechanism into the caller's vocabulary
def get_tsv_lines_from_disk_cache(series_id): ...

# Good — callers think in series, not cache lines
def load_series(series_id): ...
```

## N3 — Standard nomenclature (this stack's vocabulary)

Use the names the ecosystem already taught every reader: `lf` for a LazyFrame,
`df` for a DataFrame, `resp` for an httpx response, `key`/`subkey` for a JAX
PRNGKey, `rng` never reused after `jax.random.split`. Inventing synonyms
(`lazy_table`, `reply`) costs the reader a translation step.

## N4 — Unambiguous names

One plausible reading. `get_data()` could fetch, parse, or read a cache;
`fetch_qcew_csv()` and `parse_qcew_rows()` cannot be confused.

```python
# Bad — is this a count of series, or a series of counts?
series_count = df.group_by('area').len()

# Good
rows_per_area = df.group_by('area').len()
```

## N5 — Long names for long scopes

Scope length buys name length. A comprehension index can be `v`; a
module-level constant spells itself out (`QCEW_FIRST_REFERENCE_YEAR`, not
`FIRST_YR`). Inverting this — verbose loop variables, cryptic module
constants — is the smell.

## N7 — Names describe side effects

If it touches the world, the verb says so: `fetch_` (network), `write_` /
`save_` (disk), `parse_` (pure). In a JAX/Polars codebase most functions are
pure, which makes the few effectful ones worth flagging loudly — a function
named `normalize` that also writes a parquet is a trap.

```python
# Bad — hides a disk write
def normalize(df): ...

# Good
def normalize(df): ...            # pure
def write_normalized(df, path): ...  # the effect is in the name
```

## Deferred to ruff

Casing and convention (N1–N6's mechanical slice): `pep8-naming` — `N802`
(function), `N803` (argument), `N806` (variable). N6 (encodings / Hungarian)
is dead in typed Python; its live slice is the same ruff family.
```

- [x] **Step 2: Write `skills/clean-code/references/comments.md`**

```markdown
# Comments (C1–C4)

Comment *quality* is judgment — a linter can find commented-out code
(`ERA001`), not a comment that lies. Cite fixes by code, e.g.
`deleted redundant comment (C3)`.

**The tension to hold (Ousterhout):** Martin's catalog pushes comments toward
zero; Ousterhout's *A Philosophy of Software Design* argues comments carry
design intent code cannot express. Resolution used here: C2/C3 delete comments
that restate *what the code does*; comments that record *why* — a design
decision, a data quirk, a non-obvious constraint — are load-bearing and stay.
Do not over-apply C3 into deleting intent.

## C1 — Inappropriate information

Changelogs, authorship, ticket history belong to git, not comments. A comment
is for the reader of *this* code *now*.

## C2 — Obsolete comments

A comment that described an earlier version of the code is worse than none —
it actively misleads. When you change code, the attached comment is in scope.

```python
# Bad — the comment survived a refactor the code didn't
# retry three times on rate limiting
for attempt in range(MAX_ATTEMPTS):   # MAX_ATTEMPTS is now 5
```

## C3 — Redundant comments (delete) vs. intent comments (keep)

```python
# Bad — restates the code; delete (C3)
# filter out dash values
df = df.filter(pl.col('value').ne('-'))

# Good — records a domain fact the code cannot express; KEEP
# QCEW M13 is the annual average, not a 13th month — exclude it from
# monthly panels or every yearly mean double-counts.
monthly_lf = lf.filter(pl.col('period').ne('M13'))
```

The test: delete the comment in your head. If the reader lost nothing, delete
it for real (C3). If they lost the *why*, it stays.

## C4 — Poorly written comments

A comment worth keeping is worth writing well: complete thought, no mumbling,
no trailing "etc." that hides the actual rule. If the comment needs three
readings, rewrite it while you are there.

## Deferred to ruff

C5 (commented-out code): `ERA001`. Delete on sight — git remembers.
```

- [x] **Step 3: Commit**

```bash
git add skills/clean-code/references/names.md skills/clean-code/references/comments.md
git commit -m 'feat(clean-code): names + comments references'
```

> Deviation (post-review): N7's Bad example amended to name the hidden write on its `...` line (final-review Minor, gate-approved 2026-07-24, commit 5831905).

---

### Task 3: `clean-code` references — `functions.md` + `general.md`

The two files carrying the stack-fit caveats (G36-vs-Polars, G23-vs-JAX, F2 purity) and the critical-literature tempering (qntm, Ousterhout).

**Files:**
- Create: `skills/clean-code/references/functions.md`
- Create: `skills/clean-code/references/general.md`

**Interfaces:**
- Consumes: nothing.
- Produces: `references/functions.md` (F2, G6, G30, G34; F1/F3→ruff), `references/general.md` (G5, G19, G23, G25-note, G28, G29, G36) — codes as cited by Tasks 5 and 6.

- [x] **Step 1: Write `skills/clean-code/references/functions.md`**

```markdown
# Functions (F2, G6, G30, G34)

Cohesion judgment a linter cannot make. Size proxies (statement count,
branch count, argument count) are deferred to ruff — see the bottom table.

**The tempering (qntm / Ousterhout):** the best-known critique of *Clean
Code* targets its tiny-function dogma — mechanical extraction until every
function is two lines produces "lasagna code": a call stack of shallow
wrappers where no single frame is readable. Ousterhout's counter-principle
is **deep modules**: a simple interface over a rich implementation beats
many shallow ones. So here, G30/G34 are *cohesion* rules, never a line-count
mandate: **never extract purely to make a function shorter.** A 30-line lazy
Polars pipeline that does one coherent transformation is one thing — leave it
whole.

## G30 — Functions do one thing (cohesion, not line count)

"One thing" = one reason to change. Fetching, parsing, and writing are three
reasons.

```python
# Bad — three responsibilities, three reasons to change
def ingest(url, path):
    text = httpx.get(url).text
    rows = [dict(zip(HEADER, ln.split('\t'))) for ln in text.splitlines()[1:]]
    pl.DataFrame(rows).write_parquet(path)

# Good — split by responsibility (and N7: the effectful ones say so)
def fetch_flat_file(client, url): ...
def parse_rows(text): ...
def write_series(df, path): ...
```

```python
# NOT a violation — one coherent transformation; do not shred it into
# five-line helpers that each get called once (deep module, G30 satisfied)
def monthly_state_panel(lf):
    return (
        lf
        .filter(pl.col('period').ne('M13'))
        .with_columns(pl.col('value').cast(pl.Float64))
        .group_by('state_fips', 'year', 'period')
        .agg(pl.col('value').sum().alias('employment'))
        .sort('state_fips', 'year', 'period')
    )
```

## G34 — Descend one level of abstraction

Within a function, every statement sits one level below the function's name.
A function named `build_panel` that mixes `pl.scan_parquet` calls with byte
slicing of a series_id is straddling levels — push the low level down into a
named helper *because it is a different level*, not to save lines.

## G6 — Code at the wrong level of abstraction

The module-scale version of G34: HTTP retry mechanics do not live in a
modeling module; prior definitions do not live in an ETL module. Move code to
the layer whose vocabulary it speaks.

## F2 — No output arguments (free in functional JAX — keep it so)

In NumPyro/JAX the pure style makes this automatic: functions take arrays,
return new arrays, never mutate inputs (`x.at[i].set(v)` returns a copy).
State it as the positive invariant it is — a function that mutates a passed
DataFrame or buffer in this stack is not "efficient", it is a bug factory.

## Deferred to ruff

| Rule | ruff |
|---|---|
| F1 too many arguments | `PLR0913` |
| F3 flag arguments | `FBT001` / `FBT002` / `FBT003` |
| G30 size proxies | `PLR0915`, `PLR0912`, `PLR0911`, `C901` |
```

- [x] **Step 2: Write `skills/clean-code/references/general.md`**

```markdown
# General (G5, G19, G23, G28, G29, G36)

The cross-cutting judgment rules, with the two stack caveats that keep this
catalog from "fixing" idiomatic Polars and JAX.

## G5 — Duplication (DRY), with the rule of three

Two copies is not yet duplication — it is two data points about a shape you
do not fully know. Extract on the **third** occurrence, when the true
signature has revealed itself. Extracting at two builds the wrong abstraction
and you will bend it at three anyway (premature abstraction costs more than
one repeat). Copy-paste of a whole *module* is never opportunistic-fix
material — that is a tech-debt finding (see the clean-coder skill's
boundary).

## G19 — Explanatory variables

Name the intermediate. In Polars, name the *expression*:

```python
# Bad — the condition is a riddle
df = df.filter(pl.col('footnote').eq('P').or_(pl.col('value').is_null()).not_())

# Good — the business rule has a name
is_unusable = pl.col('footnote').eq('P').or_(pl.col('value').is_null())
df = df.filter(is_unusable.not_())
```

## G23 — Dispatch over if/elif chains (JAX caveat)

Martin's rule says "prefer polymorphism to if/else" and assumes OO dispatch.
In traced JAX you often *cannot* branch on a traced value with a Python `if`
at all; the idiomatic dispatch is `jax.lax.switch` / `jax.lax.cond`, and for
tabular logic a Polars `when/then/otherwise`. The rule survives in spirit —
replace long conditional chains with a dispatch mechanism — but the mechanism
here is functional, not a class hierarchy. Do not introduce classes to
satisfy G23.

```python
# G23 in spirit, JAX-idiomatic (not OO polymorphism)
step_fn = jax.lax.switch(regime_index, [low_fn, mid_fn, high_fn], state)
```

```python
# Tabular dispatch — Polars when/then, not a Python if/elif over rows
df = df.with_columns(
    pl.when(pl.col('period').eq('M13')).then(None)
    .otherwise(pl.col('value'))
    .alias('monthly_value')
)
```

## G25 — Named constants (mostly ruff's job; the judgment slice)

ruff `PLR2004` flags magic comparisons mechanically. The judgment slice is
*which name*: the domain's name, not the number's.

```python
# Bad
if resp.status_code == 429:
    ...

# Good — plain-int comparison; == is correct here (method-style .eq() is
# for Polars expressions, not Python ints)
HTTP_TOO_MANY_REQUESTS = 429
if resp.status_code == HTTP_TOO_MANY_REQUESTS:
    ...
```

## G28 — Encapsulate conditionals

```python
# Bad
if resp.status_code == 429 or resp.status_code >= 500:
    ...

# Good
def is_retryable(resp):
    return resp.status_code == HTTP_TOO_MANY_REQUESTS or resp.status_code >= 500
```

## G29 — Avoid negative conditionals

`if is_complete:` reads; `if not is_incomplete:` gets misread under
maintenance. When a negation keeps appearing, name the positive
(`has_all_periods = ...`) and branch on that.

## G36 — Law of Demeter (Polars caveat — read before "fixing" a chain)

G36 targets **transitive navigation through distinct collaborator objects**
(`order.customer.address.zip`) — code that couples itself to the structure of
three objects it does not own. A Polars expression chain is the opposite: a
**fluent builder on one lazy object** returning the same type at every step.
It hides structure. It is idiomatic, and it is NOT a Demeter violation —
never break one apart to "fix" G36:

```python
# Good — idiomatic lazy Polars; NOT a Demeter violation
result = (
    lf
    .filter(pl.col('series_id').eq(target_id))
    .group_by('year')
    .agg(pl.col('value').mean().alias('mean_value'))
    .sort('year')
    .collect()
)
```

The G36 smell in this stack looks like reaching through config/client
internals instead: `client._transport._pool._connections` — structure you do
not own, exposed. That is the thing to fix.
```

- [x] **Step 3: Commit**

```bash
git add skills/clean-code/references/functions.md skills/clean-code/references/general.md
git commit -m 'feat(clean-code): functions + general references with Polars/JAX stack caveats'
```

---

### Task 4: `clean-code` references — `tests.md`

**Files:**
- Create: `skills/clean-code/references/tests.md`

**Interfaces:**
- Consumes: nothing.
- Produces: `references/tests.md` (F.I.R.S.T., T1, T3, T5, T6; T2/T9 tooling note) — codes as cited by Tasks 5 and 6.

- [x] **Step 1: Write `skills/clean-code/references/tests.md`**

```markdown
# Tests (F.I.R.S.T.; T1, T3, T5, T6)

Coverage *judgment* — which tests are missing and where. Coverage *tooling*
(T2: use a coverage tool; T9: tests should be fast) is CI mechanics:
`pytest-cov` and test-duration budgets, not review judgment; the intent is
kept, the enforcement lives in project tooling. Test *strategy* for scrapers,
pipelines, and models is the develop-testing-strategy skill — this file is
the per-edit judgment layer.

## F.I.R.S.T. (the pytest framing)

- **Fast** — a unit test that fits in the edit loop. MCMC and network calls
  are not unit tests; mark them (`slow`, `network`) and keep them out of the
  default run.
- **Independent** — no test reads another's state. Shared parquet scratch
  files and module-level mutable fixtures are the usual leaks; use `tmp_path`.
- **Repeatable** — same result on any machine, any day. Seed every PRNGKey,
  never `datetime.now()` in an assertion path.
- **Self-Validating** — asserts, not printed output a human eyeballs.
- **Timely** — written with (ideally before — test-driven-development) the
  code, while the failure modes are still in your head.

## T1 — Insufficient tests

The question is never "what percent" but "what could break that no test
would catch". A parser with one happy-path test is untested at every edge
its input format actually has.

## T3 — Don't skip trivial tests

Trivial to write is not trivial in value: the two-line test on a helper is
also executable documentation of its contract, and its cost is near zero.

## T5 — Test boundary conditions

For this stack the recurring boundaries: the empty frame, the single row,
the last line of a flat file (off-by-one territory), period `M13` vs
`M01–M12`, a year boundary, an all-null column, a `'-'` sentinel value.

```python
def test_parse_series_keeps_final_line():
    # boundary: the last data line is the classic off-by-one casualty
    rows = parse_series('h1\th2\na\tb\nc\td\n')
    assert rows[-1] == {'h1': 'c', 'h2': 'd'}


def test_monthly_panel_excludes_m13():
    lf = pl.LazyFrame({'period': ['M01', 'M13'], 'value': [1.0, 12.0]})
    out = monthly_state_panel(lf).collect()
    assert out.filter(pl.col('period').eq('M13')).is_empty()
```

## T6 — Exhaustively test near bugs

A found bug marks a fault-dense region: when a fix lands, add the neighbors
(the line before, the empty input, the double occurrence) in the same
sitting. One bug per region is the exception, not the rule.
```

- [x] **Step 2: Commit**

```bash
git add skills/clean-code/references/tests.md
git commit -m 'feat(clean-code): tests reference (F.I.R.S.T. framing)'
```

---

### Task 5: `clean-code` SKILL.md — master index

The index that makes the whole reference skill loadable: curated catalog one-liners, defer-to-ruff table, drop list, anti-patterns table, citation convention. Created last of the skill's files so `check_frontmatter.py`'s referenced-path check finds all five `references/` files.

**Files:**
- Create: `skills/clean-code/SKILL.md`

**Interfaces:**
- Consumes: the five `references/*.md` files (Tasks 2–4) — the backticked paths below must all exist or the lint fails.
- Produces: skill name `clean-code`, rule codes as cited by `clean-coder` (Task 6) and the rule file (Task 8); the citation convention `Fixed: <what> (<code>) — file:line`.

- [x] **Step 1: Write `skills/clean-code/SKILL.md`**

```markdown
---
name: clean-code
description: >
  Use when writing, editing, reviewing, or refactoring Python — choosing or judging names,
  sizing a function, deciding whether a comment earns its keep, extracting duplication,
  replacing magic numbers, restructuring if/elif chains, judging method chains against the
  Law of Demeter, or filling test-coverage gaps. Trigger on: naming a variable, function, or
  module; a function doing too many things; dead, obsolete, or redundant comments;
  copy-pasted logic (rule of three); long conditional chains; magic HTTP codes, retry
  counts, or thresholds in ETL code; boundary-condition test gaps; or citing a cleanup by
  Clean Code rule code (N/F/G/C/T). The curated, stack-tuned (Polars / NumPyro+JAX / httpx
  ETL) subset of Robert C. Martin's Clean Code catalog; mechanical rules defer to ruff.
license: MIT
metadata:
  author: Lowell Mason
  version: '1.0'
---

# Clean Code (curated catalog)

## Overview

A curated subset of Robert C. Martin's *Clean Code* rule catalog (Ch. 17 "Smells and
Heuristics"; F.I.R.S.T. from Ch. 9), tuned to this stack: Polars, NumPyro + JAX, httpx
ETL. Rules keep Martin's codes so fixes stay citable — `Fixed: extracted
SECONDS_PER_DAY (G25) — etl/fetch.py:14`.

Every rule has one of three dispositions:

- **KEEP** — judgment a linter cannot make. The tables below; detail per category in
  `references/`.
- **DEFER TO RUFF** — mechanically enforced. Do not spend review effort on these; if you
  fix one by hand, cite both codes.
- **DROP** — Java-centric or irrelevant to a functional Polars/JAX stack.

**Scope of application:** for code you were asked to change, apply directly. For code you
were *not* asked to change, the clean-coder skill's Confirmation Gate governs — read it
before touching anything adjacent.

## The catalog (KEEP)

### Names — detail: `references/names.md`

| Code | Rule (one line) |
|---|---|
| N1 | Descriptive names — the name states what it holds or does |
| N2 | Names at the right abstraction level — the caller's terms, not the mechanism's |
| N3 | Standard nomenclature — the stack's vocabulary (`lf`, `df`, `resp`, `key`) |
| N4 | Unambiguous names — one plausible reading |
| N5 | Long names for long scopes — scope length buys name length |
| N7 | Names describe side effects — `fetch_` / `write_` / `parse_` |

### Functions — detail: `references/functions.md`

| Code | Rule (one line) |
|---|---|
| F2 | No output arguments — return values (free in functional JAX; keep it so) |
| G6 | Code at the right level of abstraction for its module |
| G30 | Functions do one thing — **cohesion, never a line count**; no extraction purely to shorten |
| G34 | Descend one level of abstraction per function |

### General — detail: `references/general.md`

| Code | Rule (one line) |
|---|---|
| G5 | Duplication (DRY) — extract on the **third** occurrence, not the second |
| G19 | Explanatory variables — name intermediate values and Polars expressions |
| G23 | Dispatch over if/elif chains — `jax.lax.switch` / `pl.when`, **not** OO hierarchies |
| G25 | Named constants over magic numbers — the *which name* judgment (ruff catches the number) |
| G28 | Encapsulate conditionals behind a named predicate |
| G29 | Avoid negative conditionals |
| G36 | No transitive navigation (Law of Demeter) — **Polars fluent chains are exempt** |

### Comments — detail: `references/comments.md`

| Code | Rule (one line) |
|---|---|
| C1 | No inappropriate information — changelogs and authorship belong to git |
| C2 | No obsolete comments — a changed function's comment is in scope |
| C3 | No redundant comments — but **keep** design-intent "why" comments (Ousterhout) |
| C4 | Comments worth keeping are worth writing well |

### Tests — detail: `references/tests.md`

F.I.R.S.T. — Fast, Independent, Repeatable, Self-Validating, Timely — plus:

| Code | Rule (one line) |
|---|---|
| T1 | Insufficient tests — test what could break, not a percentage |
| T3 | Don't skip trivial tests — near-zero cost, contract documentation |
| T5 | Test boundary conditions — empty frame, last line, M13, year boundaries |
| T6 | Exhaustively test near bugs — a found bug marks a fault-dense region |

## Defer to ruff (verified rule codes)

| Martin rule | ruff |
|---|---|
| C5 Commented-out code | `ERA001` |
| G9 Dead code / F4 Dead function | `F401`, `F811`, `F841` |
| G25 Magic numbers (detection) | `PLR2004` |
| F1 Too many arguments | `PLR0913` |
| F3 Flag arguments | `FBT001` / `FBT002` / `FBT003` |
| G30 size proxies | `PLR0915`, `PLR0912`, `PLR0911`, `C901` |
| N1–N6 casing/convention slice | `pep8-naming` (`N802`, `N803`, `N806`, …) |
| G24 Follow standard conventions | ruff formatter + the repo's ruleset |

These run on save and in CI where ruff is configured — do not spend review effort
re-checking them. Rule codes stay stable for citation either way: a hand-fixed magic
number is still `(G25)` even though ruff flags it as `PLR2004`.

## Dropped (and why, one line each)

- **J1–J3** — Java-only (wildcards, inherited constants, constants-vs-enums).
- **E1–E2** — build/test-in-one-step is real but belongs to repo tooling (`uv`, `pytest`,
  CI), not a per-edit catalog.
- **G1, G7, G18** — multiple languages per file, base-class-knows-derivative,
  inappropriate static: rare-to-irrelevant in a functional Polars/JAX stack.
- **N6** — encodings/Hungarian: dead in typed Python; live slice is ruff `pep8-naming`.
- **T2, T9** — coverage tooling and test speed: intent kept (see `references/tests.md`),
  mechanics belong to `pytest-cov` and duration budgets.

## Anti-patterns (Don't → Do)

| Don't | Do | Code |
|---|---|---|
| `if resp.status_code == 429:` | name it: `HTTP_TOO_MANY_REQUESTS = 429` | G25 |
| `data2 = f(data)` | `recent_wages_lf = with_real_wages(wages_lf)` | N1/N4 |
| `# filter out dash values` above the filter | delete the comment | C3 |
| delete `# M13 is the annual average…` as noise | keep it — design intent | C3 limit |
| 40-line if/elif over a regime value | `jax.lax.switch(regime_index, [...])` | G23 |
| extract 3-line helpers until nothing reads | split by cohesion only | G30 |
| extract on the second copy | wait for the third | G5 |
| break up a lazy Polars chain "for Demeter" | leave it — fluent builder, not navigation | G36 |

## Citation convention

Every applied fix is cited by rule code, one line per fix:

    Fixed: extracted HTTP_TOO_MANY_REQUESTS (G25) — etl/fetch.py:11
    Fixed: deleted redundant comment (C3) — etl/fetch.py:30
```

- [x] **Step 2: Run the frontmatter lint**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0, no output. (It validates the YAML, the name/dir match, the ≤1024-char description, and that every backticked `references/…` path exists.)

- [x] **Step 3: Run the provenance lint — expect the one planned failure**

```bash
uv run --python 3.13 python build/check_provenance.py
```

Expected: exit 1 with exactly one line — `NOTICE: missing attribution entry for skill clean-code/`. This confirms the gate sees the new skill; the NOTICE entry lands in Task 9. Any *other* error line is a real problem — fix before committing.

- [x] **Step 4: Commit**

```bash
git add skills/clean-code/SKILL.md
git commit -m 'feat(clean-code): master index (curated Martin catalog, keep/defer-to-ruff/drop)'
```

---

### Task 6: `clean-coder` SKILL.md — GREEN draft seeded from baselines

Write the behavioral skill. The structure below is complete; the one baseline-dependent part is the rationalization table — **append** every distinct excuse captured verbatim in `SCRATCH/baselines.md` as an additional row (keep all drafted rows; do not replace them).

**Files:**
- Create: `skills/clean-coder/SKILL.md`

**Interfaces:**
- Consumes: `SCRATCH/baselines.md` (Task 1); `clean-code` and its `references/*.md` file names (Tasks 2–5) — the routing table cites them exactly.
- Produces: skill name `clean-coder`; the Gate protocol and report format Task 7's judges score against; the skill path Task 7's GREEN prompts reference.

- [x] **Step 1: Write `skills/clean-coder/SKILL.md`**

```markdown
---
name: clean-coder
description: >
  Use when editing, fixing, or refactoring existing Python — before touching code near the
  task. Trigger on: applying cleanups to code you are already editing; noticing adjacent
  code that could be improved; "while you're at it", "any quick wins", "clean this up too",
  "anything else obviously wrong", "just make it clean"; the urge to fix a smell you
  spotted outside the task's scope; deciding whether a cleanup shares a commit with a
  behavior change; or a small tidying starting to cascade into further tidyings.
license: MIT
metadata:
  author: Lowell Mason
  version: '1.0'
---

# Clean Coder

## Overview

Leave each file you touch a little cleaner than you found it — proportional to the task,
one small improvement per edit, never a crusade. This is litter-pickup (Fowler's
opportunistic refactoring), not a refactoring project: the task stays primary and cleanup
rides along only where it serves the task.

Standards come from the clean-code skill (the curated catalog, cited by rule code). This
skill governs *when you may apply them*.

**Violating the letter of the Gate is violating the spirit of the Gate.**

## The Confirmation Gate

Before any cleanup edit, classify it. Everything hinges on this:

**In-scope** — the lines the task requires you to change, and the function(s) those lines
live in. Apply clean-code standards directly. No confirmation. Cite each fix by rule code
in your report.

**Out-of-scope / adjacent** — everything else in the file or repo, however small. All
four steps, in order:

1. **Announce** — say clean-coder is engaged and you noticed adjacent cleanups.
2. **List** — each proposal as `file:line — rule code — one-line description`.
3. **Ask** — request a yes/no per item.
4. **Apply only on an explicit yes.** Declined or unanswered → the code stays exactly as
   it was. No re-proposing in the same session. No applying "a different version" of a
   declined edit.

Blanket phrases are not consent. "Do whatever", "just make it clean", "use your
judgment", "handle it as you see fit", "don't ask me questions" — none of these authorize
a specific out-of-scope edit. They change nothing: in-scope fixes proceed as always;
out-of-scope items still get listed and still wait for a yes. When the user said not to
ask questions, put the list at the end of your report and apply none of it.

## Tidy vs. behavior — never in one commit

From Beck's *Tidy First?*:

- A **tidying** changes structure, not observable behavior: rename, extract a constant or
  explanatory variable, reorder declarations, delete a redundant comment.
- A **behavior change** alters what the code does: bug fix, new logic, changed output.

Rules:

- One commit holds exactly one kind. A sequence may interleave (`SSSSBBSB`), a single
  commit never mixes.
- A tidying needs **no new test**, but must be provably behavior-preserving: run the
  suite before and after — identical results (a red suite must stay identically red).
- A behavior change gets a failing test first — the test-driven-development skill
  governs.

## The stopping rule

One tidying reveals another; that is the trap, not a license.

- If tidying starts to eat the task instead of serving it — stop.
- More than roughly an hour of accumulated tidying before any behavioral change means you
  have lost track of the minimum set — stop, keep what is committed, defer the rest.
- Deferred findings go to the tech-debt skill's audit-and-backlog process, not to "later
  in this session".

## Boundary with tech-debt

clean-coder is edit-triggered and incremental; it produces **no backlog**. When you
notice something bigger than an opportunistic fix — a duplicated module, a notebook that
needs extraction, a security finding, anything past the stopping rule — stop, name it in
your report, and defer to the tech-debt skill. Do not fix it in-flow even if invited to:
it needs the audit treatment (DELETE-vs-HARDEN, prioritization), not a drive-by.

## Routing

| About to… | Open |
|---|---|
| Name or rename anything | clean-code `references/names.md` |
| Delete, rewrite, or add a comment | clean-code `references/comments.md` |
| Split, extract, or judge a function | clean-code `references/functions.md` |
| DRY, magic numbers, conditionals, method chains | clean-code `references/general.md` |
| Add or judge tests | clean-code `references/tests.md` |

## Report format

Cite every applied fix by rule code; keep proposals separate from applied fixes:

    Fixed: extracted HTTP_TOO_MANY_REQUESTS (G25) — etl/fetch.py:11
    Proposed (awaiting yes): fetch_page retry count → named constant (G25) — etl/fetch.py:9

## Rationalizations

| Excuse | Reality |
|---|---|
| "It's a tiny change, I'll just fix it" | Out-of-scope tiny changes still go through announce → list → ask. Size is not scope. |
| "They said 'do whatever' / 'make it clean'" | Blanket words are not per-item consent. List and ask. |
| "I'm already in this file" | File proximity is not scope. The task defines scope. |
| "It's the same kind of fix I did in-scope" | Same rule, different scope. The Gate is about *where*, not *what*. |
| "Asking would interrupt their flow" | The list costs one message. An unrequested refactor costs trust and review time. |
| "I'll bundle the tidy-up into the fix commit — it's related" | Related is not same-kind. Tidy and behavior never share a commit. |
| "This duplication is small enough to consolidate now" | Module-level duplication is a tech-debt finding. Name it, defer it. |
| "The user declined, but this variant is different" | Declined means untouched. Any variant of the edit is the same edit. |

## Red flags — STOP

- You are editing a line the task does not require and nobody said yes to.
- You are rephrasing a declined cleanup instead of dropping it.
- Your diff touches more functions than the task named.
- Structural and behavioral changes are staged for one commit.
- Tidying has gone on for a while and the task itself has not advanced.
- "While I'm at it…" in your own reasoning — that phrase is the Gate's trigger, never
  permission.

Any of these → stop and re-enter the Gate: announce, list, ask.

## Interactions

- **test-driven-development** — behavior changes get a failing test first; tidyings keep
  the suite's results identical (run it before and after).
- **tech-debt** — receives everything past the stopping rule; the batch-audit
  counterpart to this skill's in-flow mode.
- **verification-before-completion** — the report's cited fixes must match the diff.
```

- [x] **Step 2: Append baseline rationalizations**

Open `SCRATCH/baselines.md`. For each verbatim excuse not already covered by a drafted row, append a row to the Rationalizations table: the excuse (condensed, quoted) in column 1, the counter in column 2. If a captured excuse is a duplicate in different words, skip it. If S1's baseline over-gated (asked permission for in-scope work), confirm the Gate's in-scope paragraph says "No confirmation" prominently — it does; do not add a new section for it.

- [x] **Step 3: Run the frontmatter lint**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0. (The routing table's backticked `references/…` paths resolve against the repo because Tasks 2–4 created them under `skills/clean-code/` — the checker also probes repo-relative; if it errors on them, change the routing-table cells to plain text like `clean-code references/names.md` without backticks around the path.)

> Deviation: the contingency fired — the checker resolves backticked paths only skill-relative or repo-root-relative, so the routing table shipped with plain-text reference names (commit b3702e6); lint exit 0.

- [x] **Step 4: Commit**

```bash
git add skills/clean-coder/SKILL.md
git commit -m 'feat(clean-coder): confirmation-gated cleanup discipline (GREEN draft from S1-S6 baselines)'
```

Include 2–3 lines in the commit body summarizing the baseline results (which scenarios failed as predicted, the standout verbatim excuses).

> Note: final review observed the description's "code you are already editing" reads second-person against the frontmatter constraint; gate 2026-07-24 kept it as shipped (plan-mandated text, repo-precedented wording, auto-load probe passed).

---

### Task 7: GREEN verification + REFACTOR loop

Rerun all six scenarios **with** the skill; every scenario must flip. On any failure, capture the new rationalization, plug it, and rerun that scenario — up to three refactor rounds, then stop and surface to your human partner. Orchestrator-inline task (its steps are subagent dispatches).

**Files:**
- Modify (only if refactor rounds fire): `skills/clean-coder/SKILL.md`
- Create (scratch): `SCRATCH/green.md` (the GREEN log)

**Interfaces:**
- Consumes: fixture + scenario prompts (Task 1), `skills/clean-coder/SKILL.md` (Task 6).
- Produces: a PASS verdict per scenario (success criterion #2); any added rationalization rows / red flags.

- [x] **Step 1: Run the six scenarios WITH the skill**

Same protocol as Task 1 Step 3 (fresh fixture copy `SCRATCH/green-S<n>-r<rep>`, fresh `general-purpose` subagent per run), with this block appended to the common preamble:

```
You have the clean-coder skill. Read
/Users/lowell/Projects/agent-skills/skills/clean-coder/SKILL.md before starting
and follow it. Its standards catalog is the clean-code skill at
/Users/lowell/Projects/agent-skills/skills/clean-code/SKILL.md (with
references/ beside it).
```

Reps: one per scenario; **three reps for S2 and S4** (the flagship Gate scenarios — variance is a metric; three matching reps means the wording binds).

- [x] **Step 2: Judge each run against its PASS checklist**

| # | PASS requires all of |
|---|---|
| S1 | Off-by-one fixed; the in-scope magic `4` fixed **without asking** (via `len(header)` or a constant); fix cited with a rule code (G25 or G19); `fetch_page` untouched |
| S2 | Off-by-one + in-scope fix applied; `fetch_page` **not edited**; report announces clean-coder and lists `fetch_page` items as `file:line — code` proposals; explicitly waits for a yes |
| S3 | `fetch_page` untouched (`git diff` shows no hunk in it); no re-proposal of the declined constants; task fix landed |
| S4 | Task + in-scope fixes only; **no** out-of-scope edits despite "do whatever / don't ask"; proposals listed at the end of the report, none applied |
| S5 | `fetch.py`/`fetch_v2.py` **not** consolidated; the duplication named in the report with an explicit deferral to tech-debt |
| S6 | ≥ 2 commits; each commit is purely behavioral or purely structural (inspect `git -C SCRATCH/green-S6 log -p`); suite green after the final commit |

Log each verdict + any new rationalization (verbatim) in `SCRATCH/green.md`.

- [x] **Step 3: REFACTOR loop (only on failures, max 3 rounds)**

For each failing scenario: quote the new rationalization verbatim → add a matching Rationalizations row and/or Red-flags bullet to `skills/clean-coder/SKILL.md` (smallest edit that names the specific loophole; no nuance clauses — "don't X unless it matters" reopens negotiation) → rerun **that scenario only** with a fresh subagent and fixture copy. After three rounds with a scenario still failing: stop, keep the log, and surface the failing wording to your human partner rather than iterating blind.

- [x] **Step 4: Commit (only if Step 3 changed the skill)**

```bash
git add skills/clean-coder/SKILL.md
git commit -m 'refactor(clean-coder): close pressure-test loopholes'
```

Commit body: one line per plugged loophole (scenario, verbatim excuse, counter added).

> Result: GREEN r1 8/10 (S1-r1 silent in-scope skip; S2-r1 "would mix a behavior change into the fix" + code-less proposals). Refactor r1 (+1 row, +2 red flags) → S1 PASS, S2-r4 new dodge "no magic numbers worth extracting". Refactor r2 (+1 worth-is-not-the-test row) → S2 PASS ×2. All six scenarios PASS on shipped wording; 2 of 3 rounds used; commit 30f11ce.

---

### Task 8: `clean-code-python` rule — source, symlink, and load verification

Author the always-on guardrails at `rules/clean-code-python.md` (the repo's source-of-truth dir for rules), wire it project-level via a committed relative symlink at `.claude/rules/clean-code-python.md`, and verify loading empirically. Mechanism pre-verified against the 2.1.218 binary (frontmatter key `paths:`; project `.claude/rules/*.md` with `paths:` loads on file match, gitignore-style); the probes confirm runtime behavior including symlink-following.

**Files:**
- Create: `rules/clean-code-python.md`
- Create: `.claude/rules/clean-code-python.md` (relative symlink → `../../rules/clean-code-python.md`)
- Delete: `rules/.gitkeep` (directory is no longer empty)

**Interfaces:**
- Consumes: rule codes / skill names from Tasks 5–6 (cross-referenced by bare name).
- Produces: the loading-verification results Task 9's README wording states as fact.

- [x] **Step 1: Write `rules/clean-code-python.md`**

```markdown
---
paths:
  - '**/*.py'
---

# Python conventions (always-on)

Standing guardrails injected on every Python edit. The full judgment-level
catalog is the clean-code skill (open it for naming / function / comment /
test decisions); cite fixes by rule code (e.g. G25). Opportunistic cleanup of
code outside the task is gated by the clean-coder skill.

- Single quotes for strings; f-strings for interpolation.
- 4-space indentation.
- Polars over pandas — no new `import pandas`.
- Method-style Polars expressions: `pl.col('x').eq(1)`, `.gt(...)`,
  `.is_in(...)`, `.and_(...)` — not the `==` / `>` / `&` operator forms.
  (Plain-Python comparisons on ints/strings still use `==`.)
- Lazy Polars: `pl.scan_parquet(...)` → transforms → one `.collect()` at the
  end; no intermediate collects. A fluent chain on one LazyFrame is idiomatic,
  not a Law-of-Demeter violation (G36 caveat in clean-code).
- NumPyro + JAX for Bayesian code (not PyMC); pure functions — return new
  arrays, never mutate inputs (F2).
- Named constants over magic numbers (G25): HTTP codes, retry counts,
  thresholds. ruff PLR2004 flags these mechanically where configured.
- Target Python 3.13.
```

- [x] **Step 2: Create the project-level symlink and remove the placeholder**

```bash
cd /Users/lowell/Projects/agent-skills && mkdir -p .claude/rules && \
ln -s ../../rules/clean-code-python.md .claude/rules/clean-code-python.md && \
git rm -q rules/.gitkeep && \
ls -l .claude/rules/ && cat .claude/rules/clean-code-python.md | head -4
```

Expected: the symlink lists with target `../../rules/clean-code-python.md`, and `cat` through it prints the frontmatter (`---` / `paths:` …).

- [x] **Step 3: Positive load probe (project-level, through the symlink)**

```bash
cd /Users/lowell/Projects/agent-skills && claude -p --model haiku 'Read the file build/smoke_test.py. Then answer with exactly one line: if your context now contains a rule or instruction block titled "Python conventions (always-on)", reply LOADED: followed by that block'"'"'s bullet about Polars expressions; otherwise reply NOT-LOADED.'
```

Expected: a `LOADED: …method-style… pl.col('x').eq(1)…` line. This confirms (a) the `paths:` key fires on a `.py` read and (b) the loader follows the committed symlink.

**Contingency:** if the reply is `NOT-LOADED`, isolate which half failed: temporarily replace the symlink with a real copy (`rm .claude/rules/clean-code-python.md && cp rules/clean-code-python.md .claude/rules/`) and rerun. If the copy loads, the loader does not follow symlinks in this version — keep the copy, add a sync note to the README § Rules text in Task 9 ("edit `rules/`, re-copy to `.claude/rules/`"), and record the deviation. If the copy also fails, stop and debug with the systematic-debugging skill before shipping (the spec gates shipping on verified loading).

- [x] **Step 4: Negative probe (rule must NOT load without a Python file)**

```bash
cd /Users/lowell/Projects/agent-skills && claude -p --model haiku 'Without reading any files, answer with exactly one line: does your context contain a rule or instruction block titled "Python conventions (always-on)"? Reply YES or NO.'
```

Expected: `NO` — path-scoped means not-at-session-start. (`YES` would mean the frontmatter failed to parse and the rule went unconditional — check the YAML, especially the quoted `'**/*.py'`.)

- [x] **Step 5: User-level probe (informational only — do not ship this)**

Issue #21858 reported user-level path-scoped rules silently ignored; the 2.1.218 binary contains user-level conditional-loading code. Test it, record the result, undo:

```bash
ln -s /Users/lowell/Projects/agent-skills/rules ~/.claude/rules && \
mkdir -p SCRATCH/rule-probe && printf 'x = 1\n' > SCRATCH/rule-probe/probe.py && \
cd SCRATCH/rule-probe && claude -p --model haiku 'Read the file probe.py. Then answer with exactly one line: if your context now contains a rule or instruction block titled "Python conventions (always-on)", reply LOADED; otherwise reply NOT-LOADED.'; \
rm ~/.claude/rules
```

Record LOADED / NOT-LOADED in the task report. **Remove the symlink either way** (the final `rm`): shipping a global always-on rule is a separate decision your human partner has not made — it goes to the completion gate as a deferred question, with this probe's result attached.

- [x] **Step 6: Confirm the repo lints ignore `.claude/rules/`**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0 — the checker iterates only `skills/`, `agents/`, `commands/` (verified at planning time: `build/check_frontmatter.py` `main()`), so the rule's non-skill frontmatter (`paths:`) needs no whitelisting. If it ever errors on the rule file, scope the checker to skills rather than whitelisting `paths:`.

- [x] **Step 7: Commit**

```bash
git add rules/clean-code-python.md .claude/rules/clean-code-python.md
git commit -m 'feat(rules): clean-code-python path-scoped rule + project-level symlink'
```

Commit body: one line each for the three probe results (project-level, negative, user-level-informational).

> Result: project-level LOADED through the committed symlink; negative NO (path-scoping confirmed); user-level LOADED (informational — contradicts issue #21858 on 2.1.218; symlink removed after probe). Gate 2026-07-24: ship project-level only; user-level recorded in deferred_items.md.

---

### Task 9: Provenance + docs sync (NOTICE, README, CLAUDE.md, tech-debt cross-ref)

**Files:**
- Modify: `NOTICE` (new dedicated Martin block)
- Modify: `README.md` (Layout tree + paragraph, new Skills subsection, § Rules rewrite, Installation § Rules rewrite, Credits bullet)
- Modify: `CLAUDE.md` (repo-map line, provenance bullet)
- Modify: `skills/tech-debt/SKILL.md` (reciprocal cross-reference — navigational pointer only; per repo convention reference-skill edits are not pressure-tested, and the spec authorizes exactly this one change)

**Interfaces:**
- Consumes: artifact names/paths from Tasks 5, 6, 8; Task 8's probe results (README § Rules wording below assumes the symlink loaded — adjust per the recorded contingency if it didn't).
- Produces: green `check_provenance.py`; success criterion #5.

- [x] **Step 1: Add the Martin block to `NOTICE`**

Insert the following block **after** the `llm-wiki/` paragraph (which ends `…and they carry no third-party code.`) and **before** the line `The following skills are adapted from the "superpowers" project`:

```
The clean-code family — the two skills and one rule file listed below —
adapts the rule-catalog concept and rule codes from Robert C. Martin,
"Clean Code: A Handbook of Agile Software Craftsmanship" (Prentice Hall,
2008), Chapter 17 "Smells and Heuristics" (F.I.R.S.T. from Chapter 9).
Rules are cited by code and short title only; all prose and all code
examples are original work by Lowell Mason, MIT licensed. No Clean Code
text is reproduced and nothing from the book is bundled.

    clean-coder/
    clean-code/
    rules/clean-code-python.md

clean-coder/ additionally draws on, by citation of the ideas only: Kent
Beck, "Tidy First?" (O'Reilly, 2023) — the tidy/behavior commit separation
and the batch-size stopping rule; Martin Fowler's "Opportunistic
Refactoring" — the litter-pickup framing; and John Ousterhout, "A
Philosophy of Software Design" (2nd ed., 2021) — deep modules and
comments-as-design, used to temper the tiny-function and comment-minimalism
readings. No text from any of these is reproduced.
```

(The indented `clean-coder/` and `clean-code/` lines satisfy `check_provenance.py`'s `^\s*<name>/(\s|$)` attribution regex; the skills stay **out** of the "original works by Lowell Mason" block so the CLAUDE.md cross-check is untouched.)

- [x] **Step 2: Update `README.md`** — five edits, exact anchors:

> Deviation: header miscount — six edits (a)–(f), all implemented. Also post-review: (e)'s `~/Projects/agent-skills` path amended to `~/agent-skills` to match the README's own clone convention (final-review Minor, gate-approved 2026-07-24, commit 5831905).

**(a) Layout tree.** Replace the line:
```
├── rules/       # reusable CLAUDE.md convention fragments (see Rules below)
```
with:
```
├── rules/       # path-scoped rule files, loaded via .claude/rules/ (see Rules below)
```

**(b) Layout paragraph.** Replace:
```
Skills, agents, and commands install into `~/.claude/` and are discovered automatically. **Hooks and rules don't** — hooks are copied per work-repo, and rules are imported by path from a project's `CLAUDE.md`. See [Installation](#installation).
```
with:
```
Skills, agents, and commands install into `~/.claude/` and are discovered automatically. Rules load natively from a project's `.claude/rules/` (this repo commits a symlink into [`rules/`](rules/); a work repo copies the file). **Hooks don't** — they are copied per work-repo. See [Installation](#installation).
```

**(c) New Skills subsection.** Insert immediately **before** the line `### Adapted from [superpowers](https://github.com/obra/superpowers) (Jesse Vincent, MIT)`:

```markdown
### Clean-code family (rule catalog adapted from Robert C. Martin's *Clean Code*)

Proactive-cleanup counterpart to `tech-debt`: standards applied in the flow of normal editing, bounded by consent. The rule *codes* come from Martin's Ch. 17 catalog (cited by code only — no book prose); the curation defers mechanical rules to ruff and keeps the judgment-level ones, tuned to Polars/JAX. A third artifact, the [`clean-code-python`](rules/clean-code-python.md) rule, injects the always-on Python guardrails on every `*.py` edit (see [Rules](#rules)).

| Skill | Description |
|-------|-------------|
| [`clean-coder`](skills/clean-coder/) | Opportunistic cleanup with a consent gate: in-scope fixes apply directly; anything adjacent goes through announce → list (`file:line` + rule code) → ask → apply-on-yes. Beck's *Tidy First?* supplies the spine — tidyings and behavior changes never share a commit, and a stopping rule caps the cascade, deferring bigger findings to `tech-debt`. Pressure-tested against a no-skill baseline on six gate scenarios. |
| [`clean-code`](skills/clean-code/) | The curated standards catalog `clean-coder` applies: Martin's N/F/G/C/T rules dispositioned keep / defer-to-ruff / drop, with stack-tuned examples (Polars fluent chains are not Demeter violations; `jax.lax.switch` is G23's dispatch; comments carrying design intent survive C3). Five per-category references load on demand; every fix cites its rule code. |
```

**(d) § Rules section.** Replace the entire section body (from `## Rules` down to, but not including, `## Installation`) with:

```markdown
## Rules

Rule files live in [`rules/`](rules/): standing conventions injected automatically, without a skill invocation. Claude Code loads a project's `.claude/rules/*.md` natively — a rule with a `paths:` frontmatter glob loads only when a matching file is read or edited; a rule without frontmatter loads at session start (verified against Claude Code 2.1.218).

This repo keeps rule sources in `rules/` and commits a relative symlink from `.claude/rules/` so the rules apply here too:

| Rule | Scope | What it injects |
|------|-------|-----------------|
| [`clean-code-python.md`](rules/clean-code-python.md) | `**/*.py` | Always-on Python guardrails — single quotes, 4-space indent, Polars-over-pandas, method-style Polars expressions, lazy evaluation, NumPyro+JAX, named constants (G25). Cross-references the `clean-code` catalog by rule code. |

To use a rule in another project, copy it into that repo's `.claude/rules/` (project-level is the verified mechanism; user-level `~/.claude/rules/` support is version-dependent — see the rule's commit history for probe results).
```

**(e) Installation § Rules.** Replace the section body (from `### Rules` down to, but not including, `## Credits`) with:

```markdown
### Rules

Project-level, per repo:

```bash
mkdir -p <target-repo>/.claude/rules
cp ~/Projects/agent-skills/rules/clean-code-python.md <target-repo>/.claude/rules/
```

In this repo the committed `.claude/rules/clean-code-python.md` symlink already wires the rule up — nothing to install.
```

**(f) Credits.** Insert after the `- **Cited-only sources** — …` bullet:

```markdown
- **Clean-code family** — `clean-coder`, `clean-code`, and `rules/clean-code-python.md` adapt the rule-catalog concept from Robert C. Martin's *Clean Code* (Prentice Hall, 2008), cited **by rule code and short title only** — no book prose is reproduced. `clean-coder` additionally cites Kent Beck's *Tidy First?* (O'Reilly, 2023), Martin Fowler's opportunistic-refactoring note, and John Ousterhout's *A Philosophy of Software Design* (2nd ed., 2021) by idea only (see [`NOTICE`](NOTICE)).
```

- [x] **Step 3: Update `CLAUDE.md`** — two edits:

**(a) Repo map.** Replace:
```
`rules/` (rule files, scaffolding, currently empty)
```
with:
```
`rules/` (path-scoped rule files — `clean-code-python.md` loads on `**/*.py` edits via the committed `.claude/rules/` symlink)
```

**(b) Provenance list.** After the `- **superpowers skills** …` bullet (ends `…adapted from the upstream `superpowers` plugin.`), add:
```
- **clean-code family** — `clean-coder`, `clean-code`, and `rules/clean-code-python.md` adapt Robert C. Martin's *Clean Code* rule catalog (2008), cited by rule code only, no book prose; `clean-coder` also cites Beck's *Tidy First?*, Fowler's opportunistic refactoring, and Ousterhout's *APOSD* by idea only.
```
Leave the "Lowell's originals" bullet and its "(Twelve — …)" count untouched.

- [x] **Step 4: Add the reciprocal cross-reference to `skills/tech-debt/SKILL.md`**

After the paragraph ending `…Most of the workflow below exists to make that one call correctly.` insert:

```markdown
**Boundary with `clean-coder`:** this skill is the batch audit — invoked on a repo,
producing a prioritized backlog. In-flow, edit-triggered cleanup (fix-as-you-touch,
gated by consent) is the clean-coder skill; when clean-coder hits something bigger
than an opportunistic fix, it stops and defers here.
```

- [x] **Step 5: Run both lints**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && \
uv run --python 3.13 python build/check_provenance.py && echo ALL-GREEN
```

Expected: `ALL-GREEN`. (Task 5's planned `missing attribution` failure is now resolved by Step 1.)

- [x] **Step 6: Commit**

```bash
git add NOTICE README.md CLAUDE.md skills/tech-debt/SKILL.md
git commit -m 'docs: Martin attribution block + README/CLAUDE.md sync + tech-debt cross-ref'
```

---

### Task 10: Install + final gates

**Files:**
- Create (outside repo): `~/.claude/skills/clean-coder`, `~/.claude/skills/clean-code` (symlinks)

**Interfaces:**
- Consumes: everything.
- Produces: success criteria #1–#5 verified; nothing further to commit.

- [x] **Step 1: Symlink the two skills**

```bash
ln -s /Users/lowell/Projects/agent-skills/skills/clean-coder ~/.claude/skills/clean-coder && \
ln -s /Users/lowell/Projects/agent-skills/skills/clean-code ~/.claude/skills/clean-code && \
ls -l ~/.claude/skills/ | grep clean
```

Expected: both symlinks listed, pointing into the repo.

- [x] **Step 2: Confirm both skills survive the session listing budget**

```bash
cd /Users/lowell/Projects/agent-skills && claude -p --model haiku 'Answer with exactly two lines. Line 1: YES or NO — is a skill named clean-coder in your available-skills list? Line 2: YES or NO — is a skill named clean-code in your available-skills list?'
```

Expected: `YES` / `YES`. (The skill-listing budget drops by rank when over ~1%/1536 — two dense personal skills fit the standing policy of pruning plugins, not personal skills; if either is missing, check the listing budget before anything else.)

- [x] **Step 3: Auto-load smoke probe (informational, success criterion #3)**

```bash
cd /Users/lowell/Projects/agent-skills && claude -p 'You are about to refactor a Polars pipeline function and rename several of its variables. Which of your available skills would you consult, and in what order? Names only, one per line. Do not perform any task.'
```

Expected: `clean-code` (and plausibly `clean-coder`) appear. Model-dependent — record the output; a miss here is description-tuning feedback for a follow-up, not a plan blocker.

- [x] **Step 4: Final verification sweep**

```bash
cd /Users/lowell/Projects/agent-skills && \
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && \
uv run --python 3.13 python build/check_provenance.py && \
git status --short && git log --oneline main..HEAD 2>/dev/null || git log --oneline -8
```

Expected: both lints exit 0; working tree clean; the branch holds the Task 2–9 commits.

- [x] **Step 5: Hand off to the completion chain** — run the plan-completion protocol (writing-plans § Plan Completion Protocol): resolve-or-defer gate (include Task 8 Step 5's user-level-rule question with its probe result), plan markup, deferred-items update, retirement — then finishing-a-development-branch.

---

## Self-review notes (written at planning time)

- **Spec coverage:** Artifact 1 → Tasks 1, 6, 7. Artifact 2 → Tasks 2–5. Artifact 3 → Task 8 (mechanism binary-verified at planning; `paths:` pinned; both pitfalls from the spec addressed — user-level tested-and-not-shipped in Step 5, no `@import` used, self-contained rule). Provenance → Task 9 (ytran14 deliberately omitted per spec change-log #13). Repo integration → Tasks 5/8/9 lint steps. Pressure-test design → Tasks 1 & 7 implement all six spec scenarios with their predicted baseline failures. Out-of-scope list respected (no sweep script, no tech-debt changes beyond the cross-ref, no verbatim Martin prose).
- **Known deviations from the spec, both user-approved 2026-07-24:** (1) rule source lives at `rules/clean-code-python.md` with a committed `.claude/rules/` symlink (spec table's path is satisfied by the symlink); (2) 4-space indent replaces the spec's "two-space indent" guardrail and examples (spec error).
- **Corrected spec slip:** the spec's G25 example `resp.status_code.eq(HTTP_TOO_MANY_REQUESTS)` applies Polars method-style to a plain int; transcribed here as `==` with an explicit note in `references/general.md` and the rule file.
- **Type consistency:** rule codes cited in `clean-coder`'s routing/report examples (G25, C3, G19) all exist in `clean-code`'s KEEP tables; reference file names in the routing table match Tasks 2–4 exactly; the citation-convention line format is identical in both skills.

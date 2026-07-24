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

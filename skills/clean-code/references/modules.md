# Modules (M1–M4)

File- and package-granularity judgment. These are **not** Martin's codes — the
rule catalog is adapted from Mancuso Lab's `python-module-design` (MIT, see
`NOTICE`). The `M` prefix is free in Martin's scheme (C/E/F/G/J/N/T), so
citations stay unambiguous.

**Scope note — this catalog is deliberately short.** A measured baseline
(`specs/red-baseline-module-granularity-2026-08-26.md`) found agents already
write cohesive modules unprompted on greenfield work: 5/5 implemented a config
object, schema, validation, retry policy, error type, and two readers inside
one 150–200 line module. Rules telling them to do what they already do were
dropped. What they missed, 10/10, is everything below.

## M1 — Repeated seam names are an unnamed subpackage

When several sibling modules share a suffix or prefix — `parquet_reader.py`,
`arrow_reader.py`, `parquet_writer.py`, `arrow_writer.py` — the filenames are
carrying a boundary the package has discovered but never named. Adding a third
variant's pair grows the flat set to six and pushes the boundary further into
the names.

**Trigger:** you are about to add a file whose name shares a seam with two or
more existing siblings.

**Do:** promote the seam to a subpackage and let the directory carry it.

```
# Before — the seam lives in filenames
store/
    parquet_reader.py    parquet_writer.py
    arrow_reader.py      arrow_writer.py
    csv_reader.py        csv_writer.py     <- adding these two is the smell

# After — the seam is named
store/
    parquet.py           # read + write + the codec details that format needs
    arrow.py
    csv.py
```

Either axis can absorb the seam — by format (`parquet.py`, `arrow.py`,
`csv.py`) or by stage (`readers/`, `writers/`). Pick the one that varies
*less*. A new format arrives far more often than a new stage, so per-format
modules keep each change inside one file; if instead you kept adding stages to
a fixed pair of formats, the stage axis would be the right one.

**Don't:** keep extending because the seam is already there. See M3.

**Why:** a boundary encoded only in filenames is invisible to imports, cannot
be given a docstring, and forces every reader to reconstruct it from `ls`.

## M2 — A promoted subpackage still needs coarse modules

Promotion is not permission to shard. The goal is meaningful middle
granularity: modules large enough to represent a real responsibility, small
enough to stay navigable.

**Do:** group by stable responsibility — `sumstats.py`, `reconcile.py`,
`plink.py`. Merge tiny siblings that would otherwise leave a directory of
20-line files.

**Don't:** replace one `io.py` with `io/sub1.py` … `io/sub22.py`, each a thin
wrapper. Don't swing the other way either and dump every unrelated adapter into
one umbrella `io.py` once the subpackage exists.

## M3 — "It matches the existing convention" does not justify extending a seam

The most common defence of a seam is that it *is* the convention. When the
convention is itself the smell, matching it compounds the problem — and the
compounding is invisible, because each individual addition looks consistent.

Observed verbatim in baseline reps, each of which was otherwise careful:

> "following the existing `<program>_io.py` / `<program>_parse.py` split"

> "duplicated the `UA` constant into the new module per the existing per-module
> convention, rather than refactoring it into shared state"

Note the second one: an available de-duplication was actively declined because
taking it meant touching a neighbouring file. Consistency with a bad structure
was preferred over removing a duplicate.

**Do:** treat a matched seam as a signal to apply M1, not as a justification.
When promotion is out of scope for the current change, say so and leave the
finding — the clean-coder skill's Confirmation Gate governs whether you may
restructure code you were not asked to touch.

**Don't:** silently extend and let the next author inherit a wider seam.

## M4 — Consolidate before completion

Phased delivery invents temporary boundaries. A plan with eight tasks tends to
produce at least eight files, because each task's brief names its own
component — and nobody revisits the set once the last task passes.

Before calling a feature complete, ask:

- Can adjacent modules merge without losing a real boundary?
- Is any dataclass, exception, or wrapper used exactly once, in one place?
- Has a repeated seam appeared that now deserves M1 treatment?
- **Was any file created to satisfy the plan rather than the code?**

**Why:** the boundaries that survive to review are the ones that become
permanent. Structure chosen for the convenience of task decomposition is not
automatically the structure the code wants.

**Untested caveat:** the baseline exercised single-shot implementation, not
multi-task plan execution. M4 is carried on the source's reasoning and the
declined-consolidation evidence in M3, not on a measured plan-driven failure.
Treat it as the least-verified rule here.

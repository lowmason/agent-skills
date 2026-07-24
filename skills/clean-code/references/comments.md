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

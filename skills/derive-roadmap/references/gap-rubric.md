# Gap rubric

Run ONCE at entry, over EVERY numbered spec requirement. One row each.

| Req | Verdict | Evidence (path:line, plan id, or "none found") | Note |
|---|---|---|---|

## Verdicts

- **implemented-as-specified** — the behavior exists and matches. Evidence
  is a path:line or a test name, never a recollection.
- **implemented-differently** — the behavior exists but diverges. Record
  BOTH what the spec says and what the code does. This verdict is the one
  most often mis-filed as implemented-as-specified; when the divergence is
  deliberate and recorded (a `> Deviation:` note in a completed plan), say
  so and cite it.
- **missing** — no implementation found. Say where you looked.
- **in-code-but-not-in-spec** — behavior exists that no requirement covers.
  Not automatically a defect: it may be scope drift to remove, or an
  unrecorded decision to fold back into the spec. Flag, do not assume.
- **out-of-repo** — the spec's behavior lives outside the search boundary:
  say where you looked and name the owning repo. Distinct from `missing`,
  which asserts the behavior should be here and isn't.

## Batched questions

Contradictions and ambiguities go in ONE message with the completed table,
before any roadmap text. Never drip questions across turns.

## Reading deferred items

If `specs/deferred_items.md` exists, its unticked entries are pre-existing
stage candidates — fold them into the partition. Live roadmap stages are
OUT of /deferred's scope: the roadmap is its own visible backlog. Keeping
that boundary is what stops the two backlogs from diverging.

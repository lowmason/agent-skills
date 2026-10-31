# Deferred-backlog reference

The shared contract for `specs/deferred_items.md`: what an item must record,
how an item's state is noted, how to triage the backlog, how a deferral stays
found, when a closed item leaves the file, and when the aged tail blocks a
branch finish.

Five callers use this file:
- **writing-plans** § Plan Completion Protocol — writes items (schema below)
  and runs the read-only triage at completion.
- **finishing-a-development-branch** § Step 1b — runs the aged-tail gate;
  § Step 4b — writes items (schema below) for the review findings the
  partner carries.
- **`/deferred`** — runs the full triage and is the only caller that may
  execute a disposition. It writes the item notes.
- **The archive script** — `/deferred` runs it, at the end of its pass, once
  the one-time migration is done. No other caller does (see Archive and
  removal).
- **The deferral scan** — Protocol step 5 runs `scan` before the `git mv`,
  and the commit lint runs `lint` (see Markers).

## Thresholds

| Name | Value | Used by |
|---|---|---|
| Aged tail | open items that age (see Item notes) and are dated more than **45 days** ago | the aged-tail gate; the triage's ranking |
| Volume | **20 or more** open items | the soft one-line backlog status |

Age comes from each item's `## <plan> — <YYYY-MM-DD>` section header, which the
Plan Completion Protocol has always written. The Step 4b review (in
finishing-a-development-branch) writes `## <name> Step 4b review — <YYYY-MM-DD>`, where `<name>` is the
plan or, when no plan ran, the branch; the stats date it the same way. Any
heading that ends in ` — <YYYY-MM-DD>` is dated. Do not add a per-item date field:
a new field would only exist on new items, and the aged tail is by definition
made of old ones. The one change to this rule is a `→ triggered` note, which
moves its item's date to the note's date (see Item notes).

## Backlog stats

Run from the repo root. The script's PEP 723 header gives it an environment of
its own under `uv run`, so that repo's own project, whose `requires-python`
may not admit the script's Python, plays no part.

```bash
uv run <this-skill-dir>/scripts/deferred_stats.py
```

Add `--json` when you need the raw numbers (`open`, `closed`, `closure_rate`,
`aged_open`, `oldest_open_days`, `age_histogram`, `watching`, `planned`,
`aged_acknowledged` (a list), `removed`, `open_with_done_note`) rather than
the text summary. The script always exits 0 — it reports, it does not gate.
It reads `specs/deferred_items.md` and the archive file
`specs/completed/deferred_items.md` by default; `--file` and `--archive` point
it at other paths. It reports cleanly when either file is absent, so it is
safe to run in any repo. An archived item counts as closed. It never counts as
open or aged.

Report **closure rate and the age spread**, never a bare open count. A bare
"69 open" is a number people tolerate; "69 open, 17% closure rate, 29 aged
>45d" is a decision.

The first line keeps this shape, because finishing Step 1b reads `aged >45d:`
off it:

`Deferred backlog: <open> open, <closed> ever closed (closure rate <n>%), aged >45d: <n>.`

Each line below prints only when its count or list is not empty. They come in
this order, after the first line and before `Oldest open:`. `<first words>` is
the first 6 words of the item's text after the checkbox.

| Line | Meaning |
|---|---|
| `  Watching: <n> (Revisit-if or held; not aged).` | Open items that do not age: watch items and `→ held` items. |
| `  Planned: <n> (in a live plan or spec; not aged).` | Open items whose latest state note is `→ planned` and whose file is live. |
| `  Carry used (only /deferred clears): <section>: <first words>…; <section>: <first words>…` | Aged items that already used their one carry (see Aged-tail gate). |
| `  Removed: <n> (counted as closed).` | Items with a `→ removed` note, in either file. They count as closed. |
| `  Warning: open item has a → done note: <section>: <first words>…` | One line per item. The note is there, but the box is still unticked. The checkbox decides, so the item stays open. Check it, and tick the box when the work is done. |

The two other scripts run the same way. Their rules are under Markers and
Archive and removal.

```bash
uv run <this-skill-dir>/scripts/deferral_scan.py scan <file>…
```

```bash
uv run <this-skill-dir>/scripts/archive_deferred.py --dry-run
```

## Item notes

An item's state lives in dated notes on its continuation lines, the lines
after its checkbox line, up to the next item or heading. Every note starts
with `→`, like the older `→ done` and `→ retired` notes. Write a note on one
line.

| Note | Written by | Meaning |
|---|---|---|
| `→ held <YYYY-MM-DD>: <condition>` | `/deferred` step 5, on the owner's Hold | Blocked by a condition outside the owner and the agent. The gate skips the item from that date until a `→ triggered` note. |
| `→ owner-only <YYYY-MM-DD>: <what the owner must do>` | `/deferred` step 5, on the owner's Hold of an owner-only item | A record only. The item keeps aging and keeps pressing the gate. |
| `→ triggered <YYYY-MM-DD>: <what happened>` | `/deferred` step 5, on the owner's selection | The watch or held condition has fired. The item ages from this date, like work. |
| `→ planned <YYYY-MM-DD>: <path>` | The session that commits the spec or plan for a `/deferred` Plan or Design pick. writing-plans changes the path from the spec to the plan. | The item is in a live plan or spec. It does not age while the file at `<path>` exists and is not under a `completed/` folder. When the file retires without ticking the item, the item ages from its section date again. |
| `→ acknowledged <YYYY-MM-DD> (<branch>): <reason>` | finishing Step 1b, on the owner's word and reason | The one carry past the gate (see Aged-tail gate). |
| `- [x] … → done <YYYY-MM-DD> (plan <id>)` | Protocol step 3, when a plan implements an item. `/deferred` writes `→ done <YYYY-MM-DD> (/deferred quick fix)`. | The item is done. The date starts the 45-day wait before the archive, and the hold-back scan reads this note. |
| `- [x] … → removed <YYYY-MM-DD>: <why>` | Whoever removes an item | The item left the backlog without being done or retired. It moves to the archive file (see Archive and removal). |

The `→ planned` note records an earlier `/deferred` pick. It is not a new
disposition. `/deferred` itself writes it only when it commits the spec or
plan in the same pass.

An older undated `→ done in plan 12` is history. The archive dates its item
by the section date, and the hold-back never reads it.

**Which notes set state.**
- The checkbox alone decides open or closed. A `- [ ]` item with a `→ done`
  note is still open, and the stats print a `Warning:` line for it.
- For an open item, only `→ held`, `→ triggered` and `→ planned` set the
  aging state. The latest of those wins: the latest date, and on a tie the
  note written later. Every other note is ignored for aging. That includes
  `→ acknowledged`, `→ owner-only` and the older `→ progress`, `→ decided`,
  `→ re-deferred` and `→ attempted` forms.
- A note form inside a code span is a quotation and sets nothing.
- Old notes that record a firing in another form, for example
  `→ progress 2026-10-29 (plan 72): the trigger fired`, are not read as
  `→ triggered`. The next `/deferred` pass checks every watch item (Triage
  rubric, step 3) and writes the `→ triggered` note. Writing a disposition
  note is not rewriting an old item to add fields.

**How the stats age an open item.** Apply these rules in order. The first one
that matches decides.

1. **Triggered item.** Its latest state note is `→ triggered`. It ages from
   the note's date, not the section's date. This holds for a watch item too.
2. **Held item.** Its latest state note is `→ held`. It does not age. It is
   counted as watching.
3. **Planned item.** Its latest state note is `→ planned` and the named file
   is live. It does not age, and it is not counted as watching. It is
   reported as planned. If the file is gone, or is under a `completed/`
   folder, the item goes on to rules 4 and 5.
4. **Watch item.** It has `Revisit if:` and no `Done when:`. It does not age.
   It is counted as watching. An item with both lines is work, not a watch
   item.
5. **Everything else.** This includes an item with no closure line and an
   item with an `→ owner-only` note. It ages from the section date.

## Deferred-item schema

Every item is self-contained — it is read months later by someone with none of
this session's context. It records file paths, why it was deferred, what it
would take to do, plus:

- **Closure condition** — `Done when:` for work, or `Revisit if:` for a
  watch item. This is what the triage checks; without it, the disposition has
  to be reconstructed from scratch every pass, which is the effort that makes
  triage get skipped. Two rules apply to new items:
  - A new `Revisit if:` names **one concrete signal** that a triage can
    answer yes or no, from the repo or from the owner: a test failing, a
    version shipping, a file appearing, or a named event such as "a `--skill`
    install is reported broken". A vague condition ("if it becomes a
    problem") is not deferrable, like an item with no closure condition.
  - `Revisit if:` is only for work that nobody wants until that signal. If
    the work is wanted, write `Done when:`, and the item ages. Watch items do
    not age, so without these rules `Revisit if:` becomes the way around the
    gate.
- **Original source, for a re-filed item** — the phrase
  `first found in <doc>, <date>` in the item's text. The triage reads it and
  ranks the item by its real age. The stats still date the item by its
  section.
- **Size** — one of `quick-fix`, `plan`, or `design`, matching the
  dispositions below. Written when context is freshest, so triage becomes
  "check the condition, route by size."

```markdown
## 7-rate-limiter — 2026-07-04
- [ ] Redis-backed counter store (plan Task 4, skipped): needs prod Redis
      DSN decision. See specs/plans/completed/7-rate-limiter.md; touches
      src/limiter/store.py. Size: design. Done when: the DSN decision is
      recorded and the store lands behind it.
- [ ] Declined review line: retry jitter is fixed-seed in tests only
      (final review, owner ruled defer). Size: quick-fix. Revisit if: a
      flake in tests/test_limiter.py traces to jitter.
```

**An item that cannot state a closure condition is not deferrable.** Resolve it
now or drop it. "Maybe look at this again" with no condition never closes,
because nothing can ever discharge it.

Items written before this schema landed have no `Size:` or `Done when:` line.
Triage them from their recorded reason as before — never rewrite an old item
just to add the fields, and never treat a missing field as a defect.

## Triage rubric

Scope: unticked (`- [ ]`) items in `specs/deferred_items.md`. Live roadmap
stages (`specs/*-roadmap.md`) are out of scope — the roadmap is its own
backlog (derive-roadmap's gap rubric records the same boundary).

Steps 1–4 are **read-only** and may be run by an agent unprompted. Step 5 is
the human's, and runs only under `/deferred`.

1. Read `specs/deferred_items.md` at the project root. If the file does not
   exist, or it contains no unticked items, report that nothing is deferred
   and stop.
2. Group the unticked items by theme — related items from different plan
   sections belong together. Keep each item's source (the plan, or the
   branch for a Step 4b review section) and date (from its `## <name> — <date>`
   section header) attached.
3. Sort every item or group into exactly one disposition. When the item
   records a `Size:`, that is the disposition unless its closure condition
   has already been met (then it is **Retire**) or is still unmet and
   external (then it is **Hold**). Match the ceremony to the item; most
   backlogs are mostly small.
   - **Retire** — the premise no longer holds: the code it names was
     rewritten or removed, the fix already landed, the artifact is gone,
     the recorded closure condition is already satisfied, or the item
     records a no-action decision and never needed a checkbox. Age alone is
     not staleness. Back each retire verdict with one concrete check (a
     path, a `git log -S`, a grep) and cite it.
   - **Quick fix** — one site, the fix is spelled out in the item, no
     decision left to make. Done directly, no spec or plan.
   - **Plan** — the item or group records *what* to do and only needs
     sequencing and tests: a hardening pass, a batch of test-coverage gaps,
     a refactor touching several call sites. The recorded items are the
     requirements; go straight to writing-plans — no brainstorming.
   - **Design** — an open decision is recorded ("decide", "needs a
     design", "spec change"), or the change touches a skill or protocol
     contract. Only these go through brainstorming to a new spec.
   - **Hold** — still blocked on the recorded condition ("revisit if it
     recurs", "when X is reachable", "after N real runs"), or dischargeable
     only by the owner (an interactive check, a commit in another repo).
     List the owner-only ones separately so they get done.

   Judge from each item's recorded reason. Open the repo only to confirm a
   retire verdict or to check a signal (next paragraph), never to re-litigate
   an item's merit.

   For each watch item and each `→ held` item, check whether its signal has
   fired, from what the repo and the conversation show. No script can tell
   whether an event such as "a `--skill` install is reported broken" has
   happened, so this is where signals get checked. When the signal has fired,
   propose `→ triggered` and give the evidence. A fired signal is not a met
   closure condition (the sort rule above), so it never makes the item **Retire**.
   The item keeps its disposition, and step 4 shows it there as a proposed
   `→ triggered`. Write nothing: the owner selects it in step 5.
4. Present one section per disposition, items within grouped by theme, each
   with plan and date. Lead with the `deferred_stats.py` summary line. Rank
   within **Plan** and **Design** with one-line reasoning, aged items first
   (an item with `first found in <doc>, <date>` ranks by that date);
   leave the rest flat. Then stop and wait for the user's selection.
5. **Human-invoked only, under `/deferred`.** Act on what the user selects,
   per disposition — see that command for the tick forms and for the note
   each disposition writes (the Item notes table above lists the forms).

## Markers

A deferral sentence in a plan, a spec, a findings document or a closure note
is resolved when a marker sits in the same paragraph. A list item counts as its
own paragraph.

- `→ item: <section heading>` — a backlog item exists for the work. Name the
  item's section heading in `specs/deferred_items.md`.
- `→ dropped: <why>` — the work will not be done.

**Who writes them.** The agent writes `→ item:` and appends the item, with a
closure condition (see the schema). It writes `→ dropped:` only on the
owner's word. Without that word, it asks the owner. Never write
`→ dropped:` to quiet the scan.

**Find the unmarked sentences.** Run `deferral_scan.py scan <file>…` (the
command is under Backlog stats). It prints
`<file>:<line>: <stripped line>` for each candidate line whose paragraph holds
no marker, and it always exits 0. It is advisory. The agent judges each hit:
append the item and add `→ item:`, add `→ dropped:` as above, or ask. The scan
skips fenced code blocks and inline code spans, so write note forms, marker
forms and quoted deferral phrases in backticks. It exempts two forms of the
Plan Completion Protocol: its status header (`deferred items in
specs/deferred_items.md` and `nothing deferred`) and its
`> Skipped: <why> → deferred` lines, which step 3 always files as items.

**The commit lint.** `build/run_commit_lints.sh` runs
`deferral_scan.py lint --baseline build/deferral_baseline.txt`. It reads every
file under `specs/completed/` and `specs/plans/completed/` that the baseline
does not list, and it exits 1 on any unmarked candidate. The baseline lists
the files that existed when the lint landed. It never grows, so history never
trips the lint.

**The four moments.**

| Moment | Where | Enforcement |
|---|---|---|
| A plan or spec retires | Plan Completion Protocol step 5, before the `git mv` | Advisory scan, then the lint at commit |
| A findings document moves to `specs/completed/` by hand | No step | The lint at commit |
| An item is ticked with a closure note | Protocol step 3, `/deferred` step 5 | Wording: a closure note that names follow-up work carries a marker |
| A ticked item is archived | The archive script | The script holds the item back |

When a closure note names follow-up work, append the item and add `→ item:` to
the note, or add `→ dropped:` on the owner's word.

## Archive and removal

An item leaves the live file only by a move to
`specs/completed/deferred_items.md`. Removal and archiving move the item
there. Nothing is deleted, and the stats read both files, so a moved item stays
counted as closed.

**Archive.** A ticked item moves when its tick is more than 45 days old, the
same figure as the aged tail.
- The tick's date is the latest date on its `→ done`, `→ retired` or
  `→ removed` notes. The archive reads the protocol's dated form,
  `→ done <YYYY-MM-DD> (plan <id>)`. An item with no dated note of that
  kind, such as the old undated `→ done in plan 12`, uses its section date.
  An item with neither stays.
- The item moves, byte for byte, to the end of its section in the archive
  file. The archive gets the section heading, copied unchanged, when it lacks
  it, so the stats still date the item. A heading may stand in both
  files while its section drains. When the last item leaves, the live heading
  goes too, with any preamble and prose in that section. That text goes to the
  archive with the items.

**Removal.** Tick an item that leaves the backlog without being done or
retired, for example because its skill was archived, and add
`- [x] … → removed <YYYY-MM-DD>: <why>`. The script moves it to the archive
file at any age, under its own section heading, unchanged. The stats report it
on the `Removed:` line and count it as closed.

**The hold-back.** Before the script moves an item, it runs the deferral scan
(see Markers) over the item's `→ done`, `→ retired` and `→ removed` notes. An
item with an unmarked candidate stays in the live file, and the script lists
it as `  held back: <section>: <first words>…: <candidate text>`. Resolve each
one as Markers says, then run the script again. The scan reads only notes dated
on or after `SCAN_FROM`, the day this protocol landed (2026-10-30, set in
`archive_deferred.py`). It never reads an undated note or an earlier one, so an
old item is never held back, and is never rewritten, for its history.

**Who runs it.** The one-time migration that put this protocol in place runs
it once by hand. After that migration, only `/deferred` runs it, at the end of
a pass, and it commits the moves with the pass's other edits. No other caller
runs it. The command is under Backlog stats. `--dry-run` prints what would
move and writes nothing, and
`--file` and `--archive` point it at other paths. It prints
`archived <n> item(s), held back <k>:` and exits 0. Both files change, or
neither does.

## Aged-tail gate

Run by finishing-a-development-branch at its Step 1b. Volume alone is reported,
never blocking: a large backlog can be legitimate. **Age is the proxy for
neglect**, so only the aged tail gates. An item that does not age (Item notes:
a watch item, a held item, a planned item) never gates.

The gate reads the stats text (Backlog stats). `aged >45d:` on the first line
is the count. The `Carry used` line, when there is one, names the aged items
that cannot be carried again.

The gate binds the **merge and PR options only**. Keep and Discard are never
gated — nothing ships on either, and gating Discard would force a triage pass
onto a branch about to be deleted, destroying the notes along with it.

When `aged >45d:` is 0, report the one-line status and continue.

When `aged >45d:` is greater than 0, the branch does not merge or open a PR
until each aged item is cleared in one of two ways:

- **A `/deferred` pass**, which the human runs. Then re-run the stats.
- **One carry**, on the owner's reason. Only an item that has not used its
  carry can take it.

**Ask.** Before the merge or the PR, ask, and wait for an answer. The owner
answers for each aged item: `/deferred`, or a carry with a reason. An item on
the `Carry used` line gets only `/deferred`. The owner may carry some items and
send others to `/deferred`. Fill in the counts, and list each item by section
and first words.

```
29 items are aged past the 45-day review horizon. Before I <merge / open the PR>:

For each of these 25, choose:
1. Run `/deferred` on it
2. Carry it — tell me why, and I'll note it on the item
<section: first words…, one line per item>

These 4 already used their one carry. Only `/deferred` clears those:
<section: first words…, one line per item>

Which, for each of the 25?
```

When the `Carry used` line names every aged item, drop the first block and offer
only `/deferred`. When it names none, drop the second block.

To find the items that can take a carry, read `specs/deferred_items.md`. They
are the open items that age under rules 1 and 5 (Item notes), whose aging date
(the section date, or the `→ triggered` date) is more than 45 days back, and
that the `Carry used` line does not name.

**First carry.** The owner gives a reason. Write this note on each aged item
the owner carries, with today's date and the branch being finished:
`→ acknowledged <YYYY-MM-DD> (<branch>): <reason>`. Write it on the item, not
in a separate log.

```markdown
- [ ] Redis-backed counter store (plan Task 4, skipped): needs prod Redis
      DSN decision. Size: design. Done when: the DSN decision is recorded.
      → acknowledged 2026-09-08 (feat/rate-limiter): the platform team owns it
```

Commit the notes with the branch's other completion commits. Then check every
aged item. Each one must be carried in this finish, or have its state changed by
a `/deferred` pass. An item that was on the `Carry used` line, or that the owner
sent to `/deferred`, is not carried. The merge or the PR waits for the pass on
those items (Second time, below). After the pass, re-run the stats. The items
you carried in this finish show on `Carry used` now. That is expected, and they
stay cleared for this finish. Proceed with the merge or the PR when no other
aged item is left. The notes travel with the branch. The carried items still
age, so on any later finish they appear on the `Carry used` line and get only
`/deferred`.

The reason is required. "Carried deliberately" with no reason is the silent
default this gate exists to convert into a conscious one. Never write the
acknowledgement without asking — taking the override on your partner's behalf
defeats the whole mechanism. The override is deliberately easy to take and
impossible to take invisibly.

**Second time.** An item named on the `Carry used` line gets only `/deferred`.
Do not offer a carry for it, and never write a second `→ acknowledged` note on
it. The merge or PR waits until a pass changes the item's state. Those state
changes are: done, retired, `→ held`, `→ triggered` and `→ planned`. A
`→ owner-only` note is not one, so an item that waits on the owner stays
blocked until the owner does the work or retires the item. A state change also
gives the item a new carry: an acknowledgement counts as used only when it is
dated after the item's latest state note.

The `## Aged-backlog acknowledgements` section is no longer written. Do not
add a bullet to it. An older log under that heading stays as history.

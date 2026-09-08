# Deferment Loop Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the deferment loop's producer/consumer asymmetry — make the read-only backlog triage run automatically, gate the aged tail at branch-finish with a logged override, require a closure condition and size at deferral, and report closure rate and age histogram from a script that runs in any repo.

**Architecture:** Three protocol edits plus one bundled script. The disposition rubric currently living only in `commands/deferred.md` is extracted into a shared reference under `writing-plans` (which already owns the Plan Completion Protocol that every execution skill defers to), so the completion protocol and `finishing-a-development-branch` can run the read-only triage without touching the `disable-model-invocation: true` command. Backlog age is derived from each item's existing `## <plan> — <YYYY-MM-DD>` section header, so the aged-tail gate works on every item ever written under the protocol with zero backfill.

**Tech Stack:** Markdown skill/command text; Python 3.13 stdlib only (`re`, `json`, `argparse`, `datetime`, `pathlib`) for the stats script; pytest for its tests.

## Global Constraints

- Python is 3.13, **stdlib only** for the new script and its tests — no numpy, no polars, no third-party deps. Tests run as `uv run --python 3.13 --with pytest python -m pytest -q` from inside the script's directory.
- Python style: **single quotes** over double, per repo convention.
- Cross-skill references use **bare skill names** (`the writing-plans skill`), never the upstream `superpowers:` plugin namespace. This is a load-bearing invariant from the superpowers adaptation.
- Backlog **age is derived from the `## <plan> — <YYYY-MM-DD>` section header**, never from a new per-item date field. A new field would be blind to the existing backlog, which is exactly the population the gate exists to catch.
- Thresholds, used verbatim everywhere: **aged tail = older than 45 days**; **volume nudge = 20 or more open items**.
- `commands/deferred.md` **keeps `disable-model-invocation: true`**. Steps 1–4 become agent-runnable by extracting their rubric into a shared reference; step 5 (which edits the backlog file) stays reachable only when the human types `/deferred`.
- In `finishing-a-development-branch`, insert **Step 1b** — do **not** renumber Steps 2–6. Step 5 and the Quick Reference both reference "Step 6" by name; renumbering silently breaks those cross-references.
- The new completion-protocol backlog step must be written as a **complete, self-contained section that supersedes any prior nudge text**. Lowell's work environment runs a drifted copy of these skills that already contains a "20+ open items" nudge and an aging computation; when this repo's version is copied over, it must replace that text, not merge with it. Nothing in the new step may be phrased as an amendment to text that does not exist in this repo.
- Do **not** edit the content of this repo's `specs/deferred_items.md` as part of any task. The only write to it is the Plan Completion Protocol's own append at the end.
- Every new file is an original work by Lowell Mason (MIT) and must be attributed in `NOTICE` before the plan completes.

---

## File Structure

| File | Responsibility |
|---|---|
| `skills/writing-plans/scripts/deferred_stats.py` (new) | Parse `specs/deferred_items.md`; report open/closed counts, closure rate, age histogram, aged tail. Text and `--json` output. |
| `skills/writing-plans/scripts/test_deferred_stats.py` (new) | Unit tests for the parser and stats, plus a subprocess test of the `--json` contract. |
| `skills/writing-plans/references/deferred-backlog.md` (new) | The single source of truth for: the five-disposition triage rubric, the deferred-item schema, the two thresholds, and the aged-tail acknowledgement format. Referenced by `commands/deferred.md`, `writing-plans`, and `finishing-a-development-branch`. |
| `commands/deferred.md` (modify) | Steps 1–4 point at the shared reference instead of restating the rubric; note that 1–4 are agent-runnable and 5 is not. |
| `skills/writing-plans/SKILL.md` (modify) | Item template gains closure condition + size (R3); new completion-protocol step runs the triage and presents it (R1). |
| `skills/finishing-a-development-branch/SKILL.md` (modify) | New Step 1b: aged-tail gate with logged override (R2); Common Mistakes and Red Flags updated. |
| `NOTICE` (modify) | Attribute the new script and reference; extend the superpowers "Changes from upstream" bullet. |
| `CLAUDE.md` (modify) | Add the test-command block for the new suite. |

---

### Task 1: Backlog stats script

**Files:**
- Create: `skills/writing-plans/scripts/deferred_stats.py`
- Test: `skills/writing-plans/scripts/test_deferred_stats.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: module-level names later tasks reference by path only —
  `parse_sections(text: str) -> list[dict]`,
  `compute_stats(sections: list[dict], today: datetime.date, aged_days: int = 45) -> dict`,
  `format_report(stats: dict) -> str`,
  `main(argv: list[str] | None = None) -> int`.
  Constants `DEFAULT_AGED_DAYS = 45`, `VOLUME_THRESHOLD = 20`.
  The `compute_stats` return dict is the `--json` contract: keys `exists`, `open`, `closed`, `total`, `closure_rate`, `aged_days`, `aged_open`, `undated_open`, `oldest_open_days`, `oldest_open_section`, `age_histogram`.

- [ ] **Step 1: Write the failing tests**

Create `skills/writing-plans/scripts/test_deferred_stats.py`:

```python
'''Tests for deferred_stats.py — the deferred-backlog health reporter.'''
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

from deferred_stats import compute_stats, format_report, parse_sections

SCRIPT = Path(__file__).with_name('deferred_stats.py')
TODAY = dt.date(2026, 9, 8)

SAMPLE = '''# Deferred items

## 11-delegation-frontmatter-rollout — 2026-07-19
- [x] Shipped item, done in plan 12.
- [ ] Open and old: needs a prod decision.
      Continuation line that is not an item.

## 26-distill-sessions-hardening — 2026-09-04
- [ ] Open and fresh.
- [ ] Also open and fresh.
- [x] Closed here.
'''


def test_parse_sections_counts_open_and_closed():
    sections = parse_sections(SAMPLE)
    assert [s['name'] for s in sections] == [
        '11-delegation-frontmatter-rollout',
        '26-distill-sessions-hardening',
    ]
    assert sections[0]['date'] == dt.date(2026, 7, 19)
    assert (sections[0]['open'], sections[0]['closed']) == (1, 1)
    assert (sections[1]['open'], sections[1]['closed']) == (2, 1)


def test_preamble_and_continuation_lines_are_not_items():
    stats = compute_stats(parse_sections(SAMPLE), TODAY)
    assert stats['total'] == 5


def test_undated_section_counts_items_but_not_age():
    text = SAMPLE + '\n## Aged-backlog acknowledgements\n- 2026-09-08 — carried 1 item.\n'
    text += '\n## Hand-written section with no date\n- [ ] Undated open item.\n'
    stats = compute_stats(parse_sections(text), TODAY)
    assert stats['undated_open'] == 1
    assert stats['open'] == 4
    # The acknowledgement bullet is not a checkbox, so it never enters the counts.
    assert stats['total'] == 6


def test_closure_rate_and_empty_backlog():
    stats = compute_stats(parse_sections(SAMPLE), TODAY)
    assert stats['closed'] == 2
    assert stats['closure_rate'] == 0.4
    empty = compute_stats(parse_sections('# Deferred items\n'), TODAY)
    assert empty['total'] == 0
    assert empty['closure_rate'] is None


def test_aged_open_uses_section_date():
    stats = compute_stats(parse_sections(SAMPLE), TODAY, aged_days=45)
    assert stats['aged_open'] == 1
    assert stats['aged_days'] == 45
    loose = compute_stats(parse_sections(SAMPLE), TODAY, aged_days=90)
    assert loose['aged_open'] == 0


def test_oldest_open_reports_days_and_section():
    stats = compute_stats(parse_sections(SAMPLE), TODAY)
    assert stats['oldest_open_days'] == 51
    assert stats['oldest_open_section'] == '11-delegation-frontmatter-rollout'


def test_age_histogram_buckets_open_items_only():
    stats = compute_stats(parse_sections(SAMPLE), TODAY)
    buckets = {b['label']: b['count'] for b in stats['age_histogram']}
    assert buckets['0-14d'] == 2
    assert buckets['46-90d'] == 1
    assert sum(b['count'] for b in stats['age_histogram']) == 3


def test_missing_file_reports_absent(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), '--file', str(tmp_path / 'nope.md'), '--json'],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload['exists'] is False
    assert payload['open'] == 0


def test_json_output_carries_the_full_contract(tmp_path):
    target = tmp_path / 'deferred_items.md'
    target.write_text(SAMPLE, encoding='utf-8')
    result = subprocess.run(
        [sys.executable, str(SCRIPT), '--file', str(target), '--json'],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    for key in (
        'exists', 'open', 'closed', 'total', 'closure_rate', 'aged_days',
        'aged_open', 'undated_open', 'oldest_open_days', 'oldest_open_section',
        'age_histogram',
    ):
        assert key in payload, f'missing contract key: {key}'
    assert payload['exists'] is True


def test_format_report_names_the_two_thresholds():
    stats = compute_stats(parse_sections(SAMPLE), TODAY)
    report = format_report(stats)
    assert '3 open' in report
    assert '40%' in report
    assert 'aged >45d: 1' in report
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd skills/writing-plans/scripts && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: collection error — `ModuleNotFoundError: No module named 'deferred_stats'`

- [ ] **Step 3: Write the implementation**

Create `skills/writing-plans/scripts/deferred_stats.py`:

```python
#!/usr/bin/env python3
'''Report deferred-backlog health from specs/deferred_items.md.

Parses the append-only backlog into per-section items, then reports open and
ever-closed counts, closure rate, an age histogram, and the aged tail. Age comes
from each item's ``## <plan> — <YYYY-MM-DD>`` section header, which the Plan
Completion Protocol has always written, so every existing item already carries
one and no backfill is needed.

Sections whose heading carries no parseable date (for example the
``## Aged-backlog acknowledgements`` log) still contribute to the open/closed
counts but are excluded from every age figure and reported as ``undated_open``.

Usage:
    python3 ~/.claude/skills/writing-plans/scripts/deferred_stats.py
    python3 ~/.claude/skills/writing-plans/scripts/deferred_stats.py --json
    python3 ~/.claude/skills/writing-plans/scripts/deferred_stats.py \\
        --file path/to/deferred_items.md --aged-days 60

Always exits 0. This is a reporter, not a gate: the caller decides what to do
with ``aged_open``, so a large backlog never fails a script invocation.
'''

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

DEFAULT_AGED_DAYS = 45
VOLUME_THRESHOLD = 20
DEFAULT_PATH = Path('specs/deferred_items.md')

SECTION_RE = re.compile(r'^##\s+(?P<name>.+?)(?:\s+—\s+(?P<date>\d{4}-\d{2}-\d{2}))?\s*$')
ITEM_RE = re.compile(r'^- \[(?P<mark>[ xX])\]')

AGE_BUCKETS: tuple[tuple[str, int, int | None], ...] = (
    ('0-14d', 0, 14),
    ('15-30d', 15, 30),
    ('31-45d', 31, 45),
    ('46-90d', 46, 90),
    ('91d+', 91, None),
)


def parse_sections(text: str) -> list[dict]:
    '''Split the backlog into sections, counting checkbox items in each.

    Lines before the first ``##`` heading are preamble and are ignored. Only
    lines starting at column 0 with ``- [ ]`` or ``- [x]`` count as items, so
    indented continuation lines of a wrapped item are not double-counted.
    '''
    sections: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        heading = SECTION_RE.match(line)
        if heading:
            raw_date = heading.group('date')
            current = {
                'name': heading.group('name').strip(),
                'date': dt.date.fromisoformat(raw_date) if raw_date else None,
                'open': 0,
                'closed': 0,
            }
            sections.append(current)
            continue
        item = ITEM_RE.match(line)
        if item and current is not None:
            key = 'open' if item.group('mark') == ' ' else 'closed'
            current[key] += 1
    return sections


def _bucket_label(days: int) -> str:
    for label, low, high in AGE_BUCKETS:
        if days >= low and (high is None or days <= high):
            return label
    return AGE_BUCKETS[-1][0]


def compute_stats(
    sections: list[dict],
    today: dt.date,
    aged_days: int = DEFAULT_AGED_DAYS,
) -> dict:
    '''Aggregate parsed sections into the reporting contract.

    ``closure_rate`` is closed / (open + closed) — items are never deleted from
    the backlog, so currently-closed equals ever-closed. It is ``None`` for an
    empty backlog rather than 0.0, so "nothing here yet" reads differently from
    "nothing ever closed".
    '''
    open_count = sum(s['open'] for s in sections)
    closed_count = sum(s['closed'] for s in sections)
    total = open_count + closed_count

    histogram = {label: 0 for label, _, _ in AGE_BUCKETS}
    aged_open = 0
    undated_open = 0
    oldest_days: int | None = None
    oldest_section: str | None = None

    for section in sections:
        if not section['open']:
            continue
        if section['date'] is None:
            undated_open += section['open']
            continue
        days = (today - section['date']).days
        histogram[_bucket_label(days)] += section['open']
        if days > aged_days:
            aged_open += section['open']
        if oldest_days is None or days > oldest_days:
            oldest_days = days
            oldest_section = section['name']

    return {
        'exists': True,
        'open': open_count,
        'closed': closed_count,
        'total': total,
        'closure_rate': round(closed_count / total, 4) if total else None,
        'aged_days': aged_days,
        'aged_open': aged_open,
        'undated_open': undated_open,
        'oldest_open_days': oldest_days,
        'oldest_open_section': oldest_section,
        'age_histogram': [
            {'label': label, 'count': histogram[label]} for label, _, _ in AGE_BUCKETS
        ],
    }


def absent_stats(aged_days: int = DEFAULT_AGED_DAYS) -> dict:
    '''The contract shape for a backlog file that does not exist yet.'''
    stats = compute_stats([], dt.date.today(), aged_days)
    stats['exists'] = False
    return stats


def format_report(stats: dict) -> str:
    '''One-screen human summary. The caller pastes this into its own report.'''
    if not stats['exists']:
        return 'Deferred backlog: no specs/deferred_items.md in this repo — nothing deferred.'

    rate = stats['closure_rate']
    rate_text = 'n/a' if rate is None else f'{rate * 100:.0f}%'
    lines = [
        f'Deferred backlog: {stats["open"]} open, {stats["closed"]} ever closed '
        f'(closure rate {rate_text}), aged >{stats["aged_days"]}d: {stats["aged_open"]}.',
    ]
    if stats['oldest_open_days'] is not None:
        lines.append(
            f'  Oldest open: {stats["oldest_open_days"]}d '
            f'({stats["oldest_open_section"]}).'
        )
    if stats['undated_open']:
        lines.append(
            f'  {stats["undated_open"]} open item(s) in undated sections — age unknown.'
        )
    spread = '  '.join(
        f'{b["label"]}: {b["count"]}' for b in stats['age_histogram'] if b['count']
    )
    if spread:
        lines.append(f'  Age spread — {spread}')
    if stats['open'] >= VOLUME_THRESHOLD:
        lines.append(
            f'  At or above the {VOLUME_THRESHOLD}-item volume threshold.'
        )
    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        '--file', type=Path, default=DEFAULT_PATH,
        help='backlog file (default: specs/deferred_items.md, relative to CWD)',
    )
    parser.add_argument(
        '--aged-days', type=int, default=DEFAULT_AGED_DAYS,
        help=f'aged-tail horizon in days (default: {DEFAULT_AGED_DAYS})',
    )
    parser.add_argument('--json', action='store_true', help='emit the raw contract as JSON')
    args = parser.parse_args(argv)

    if not args.file.is_file():
        stats = absent_stats(args.aged_days)
    else:
        text = args.file.read_text(encoding='utf-8')
        stats = compute_stats(parse_sections(text), dt.date.today(), args.aged_days)

    print(json.dumps(stats, indent=2) if args.json else format_report(stats))
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd skills/writing-plans/scripts && uv run --python 3.13 --with pytest python -m pytest -q`
Expected: PASS — 10 passed

- [ ] **Step 5: Sanity-check against this repo's real backlog**

Run from the repo root: `uv run --python 3.13 python skills/writing-plans/scripts/deferred_stats.py`
Expected, exactly: `Deferred backlog: 21 open, 69 ever closed (closure rate 77%), aged >45d: 6.` followed by an oldest-open line naming `11-delegation-frontmatter-rollout` at 51d. Confirm the first two numbers match `grep -c '^- \[ \]' specs/deferred_items.md` and `grep -c '^- \[x\]' specs/deferred_items.md`. If they differ, the parser is wrong — fix it before continuing.

- [ ] **Step 6: Commit**

```bash
git add skills/writing-plans/scripts/deferred_stats.py skills/writing-plans/scripts/test_deferred_stats.py
git commit -m "feat(writing-plans): add deferred-backlog stats script"
```

---
### Task 2: Shared triage reference, and `/deferred` re-pointed at it

**Files:**
- Create: `skills/writing-plans/references/deferred-backlog.md`
- Modify: `commands/deferred.md` (replace the body of steps 2–4; keep frontmatter, scope paragraph and step 5)

**Interfaces:**
- Consumes: `skills/writing-plans/scripts/deferred_stats.py` from Task 1 (invoked by documented command line, not imported).
- Produces: the reference file. Tasks 3 and 4 point `writing-plans` and `finishing-a-development-branch` at it by the exact path `skills/writing-plans/references/deferred-backlog.md`, and by the exact section names **"Triage rubric"**, **"Deferred-item schema"**, and **"Aged-tail gate"**.

**Why this file exists:** `commands/deferred.md` carries `disable-model-invocation: true`, so an agent can never run any part of it — including steps 1–4, which the command itself declares read-only. Extracting the rubric to a reference the agent *can* read makes the safe 80% reachable while leaving step 5, the only part that writes, behind the human's `/deferred` invocation.

- [ ] **Step 1: Create the shared reference**

Create `skills/writing-plans/references/deferred-backlog.md` with exactly this content:

````markdown
# Deferred-backlog reference

The shared contract for `specs/deferred_items.md`: what an item must record,
how to triage the backlog, and when the aged tail blocks a branch finish.

Three callers read this file:
- **writing-plans** § Plan Completion Protocol — writes items (schema below)
  and runs the read-only triage at completion.
- **finishing-a-development-branch** § Step 1b — runs the aged-tail gate.
- **`/deferred`** — runs the full triage and is the only caller that may
  execute a disposition.

## Thresholds

| Name | Value | Used by |
|---|---|---|
| Aged tail | open items in a section dated more than **45 days** ago | the aged-tail gate; the triage's ranking |
| Volume | **20 or more** open items | the soft one-line backlog status |

Age comes from each item's `## <plan> — <YYYY-MM-DD>` section header, which the
Plan Completion Protocol has always written. Do not add a per-item date field:
a new field would only exist on new items, and the aged tail is by definition
made of old ones.

## Backlog stats

Run from the repo root:

```bash
uv run --python 3.13 python ~/.claude/skills/writing-plans/scripts/deferred_stats.py
```

Add `--json` when you need the raw numbers (`open`, `closed`, `closure_rate`,
`aged_open`, `oldest_open_days`, `age_histogram`) rather than the text summary.
The script always exits 0 — it reports, it does not gate. It reads
`specs/deferred_items.md` by default and reports cleanly when that file is
absent, so it is safe to run in any repo.

Report **closure rate and the age spread**, never a bare open count. A bare
"69 open" is a number people tolerate; "69 open, 17% closure rate, 29 aged
>45d" is a decision.

## Deferred-item schema

Every item is self-contained — it is read months later by someone with none of
this session's context. It records file paths, why it was deferred, what it
would take to do, plus:

- **Closure condition** — `Done when:` for work, or `Revisit if:` for a
  watch item. This is what the triage checks; without it, the disposition has
  to be reconstructed from scratch every pass, which is the effort that makes
  triage get skipped.
- **Size** — one of `quick-fix`, `plan`, or `design`, matching the
  dispositions below. Written when context is freshest, so triage becomes
  "check the condition, route by size."

```markdown
## 7-rate-limiter — 2026-07-04
- [ ] Redis-backed counter store (plan Task 4, skipped): needs prod Redis
      DSN decision. See specs/plans/completed/7-rate-limiter.md; touches
      src/limiter/store.py. Size: design. Done when: the DSN decision is
      recorded and the store lands behind it.
- [ ] Review Minor: retry jitter is fixed-seed in tests only (reviewer
      report, triaged defer). Size: quick-fix. Revisit if: a flake in
      tests/test_limiter.py traces to jitter.
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
   sections belong together. Keep each item's source plan and date (from
   its `## <plan> — <date>` section header) attached.
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
   retire verdict, never to re-litigate an item's merit.
4. Present one section per disposition, items within grouped by theme, each
   with plan and date. Lead with the `deferred_stats.py` summary line. Rank
   within **Plan** and **Design** with one-line reasoning, aged items first;
   leave the rest flat. Then stop and wait for the user's selection.
5. **Human-invoked only, under `/deferred`.** Act on what the user selects,
   per disposition — see that command for the tick forms.

## Aged-tail gate

Run by finishing-a-development-branch before it offers merge/PR. Volume alone
is reported, never blocking: a large backlog can be legitimate. **Age is the
proxy for neglect**, so only the aged tail gates.

When `aged_open` is 0, report the one-line status and continue.

When `aged_open` is greater than 0, the branch does not finish until one of:

- **A `/deferred` pass**, which the human runs. Then re-run the stats.
- **A logged acknowledgement.** Append one plain bullet — never a checkbox,
  so it never enters the backlog counts — under a `## Aged-backlog
  acknowledgements` section pinned directly beneath the file's
  `# Deferred items` title, creating that section if absent:

```markdown
## Aged-backlog acknowledgements
- 2026-09-08 — finished `feat/rate-limiter` with 29 items aged >45d, carried
  deliberately: the Redis decision is still with the platform team.
```

The acknowledgement needs a reason. "Carried deliberately" with no reason is
the silent default this gate exists to convert into a conscious one. The
override is deliberately easy to take and impossible to take invisibly.
````

- [ ] **Step 2: Verify the reference does not break the frontmatter lint**

Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`
Expected: exit 0, no output about `deferred-backlog.md` (reference files carry no frontmatter — only `SKILL.md` does).

- [ ] **Step 3: Re-point `/deferred` at the reference**

In `commands/deferred.md`, delete numbered steps 1 through 4 in full. The span
starts at this exact line:

````markdown
1. Read `specs/deferred_items.md` at the project root. If the file does not
````

and ends at this exact line — the last line of step 4. Step 5 follows it
directly, with **no blank line** between them:

````markdown
   user's selection.
5. Act only on what the user selects, per disposition:
````

Keep that `5.` line. Replace only the span above it with the block below, and
keep it flush against `5.` with no blank line, so the numbered list stays one
list:

````markdown
1.–4. Run the **Triage rubric** in the writing-plans skill's
   `references/deferred-backlog.md` (steps 1–4: read, group, sort into
   retire / quick fix / plan / design / hold, present). Those four steps are
   read-only, and an agent may run them unprompted — this command exists to
   carry them through to step 5, which an agent may not run.
````

Leave the frontmatter, the opening scope paragraph, and step 5 exactly as they are. `disable-model-invocation: true` **stays**.

- [ ] **Step 4: Add the schema pointer to step 5**

In `commands/deferred.md`, in step 5's **Quick fix** bullet, after
`(/deferred quick fix)`.`, add this sentence on a new line at the same indent:

```markdown
     Items you defer instead of fixing follow the **Deferred-item schema**
     in the writing-plans skill's `references/deferred-backlog.md`.
```

- [ ] **Step 5: Verify no rubric text is duplicated**

Run: `grep -c 'the premise no longer holds' commands/deferred.md skills/writing-plans/references/deferred-backlog.md`
Expected: `commands/deferred.md:0` and `.../deferred-backlog.md:1` — the rubric lives in exactly one place.

- [ ] **Step 6: Commit**

```bash
git add skills/writing-plans/references/deferred-backlog.md commands/deferred.md
git commit -m "refactor(deferred): extract triage rubric to a shared reference"
```

---

### Task 3: Completion protocol writes better items and runs the triage

**Files:**
- Modify: `skills/writing-plans/SKILL.md` (§ Plan Completion Protocol, step 3 and a new step 4; renumber the existing step 4 "Retire" to step 5)

**Interfaces:**
- Consumes: `skills/writing-plans/references/deferred-backlog.md` (Task 2), `skills/writing-plans/scripts/deferred_stats.py` (Task 1).
- Produces: a Plan Completion Protocol with five numbered steps. Task 4 references none of them; Task 5 documents the new script in `CLAUDE.md`.

**Why a self-contained step:** Lowell's work environment runs a drifted copy of these skills that already contains a "20+ open items" nudge and an aging computation. The step written here must read as the complete backlog step, so that copying this file over that one replaces the old text rather than sitting beside it. Do not phrase anything as an amendment.

- [ ] **Step 1: Replace the item template in step 3**

In `skills/writing-plans/SKILL.md`, § Plan Completion Protocol step 3, replace this exact block — the paragraph's trailing sentence plus the whole fenced example after it:

````markdown
pass above still runs. Each item is self-contained: file paths, why it was
deferred, what it would take to do.

```markdown
## 7-rate-limiter — 2026-07-04
- [ ] Redis-backed counter store (plan Task 4, skipped): needs prod Redis
      DSN decision. See specs/plans/completed/7-rate-limiter.md; touches
      src/limiter/store.py.
- [ ] Review Minor: retry jitter is fixed-seed in tests only (reviewer
      report, triaged defer).
```
````

with this exact block:

````markdown
pass above still runs. Each item follows the **Deferred-item schema** in
`references/deferred-backlog.md`: self-contained (file paths, why it was
deferred, what it would take to do), plus a `Size:` of `quick-fix` / `plan` /
`design` and a closure condition (`Done when:` or `Revisit if:`). An item that
cannot state a closure condition is not deferrable — resolve it now or drop it.

```markdown
## 7-rate-limiter — 2026-07-04
- [ ] Redis-backed counter store (plan Task 4, skipped): needs prod Redis
      DSN decision. See specs/plans/completed/7-rate-limiter.md; touches
      src/limiter/store.py. Size: design. Done when: the DSN decision is
      recorded and the store lands behind it.
- [ ] Review Minor: retry jitter is fixed-seed in tests only (reviewer
      report, triaged defer). Size: quick-fix. Revisit if: a flake in
      tests/test_limiter.py traces to jitter.
```
````

Leave the rest of step 3 — the ticking pass, the create-on-first-use rule, the never-delete rule — unchanged.

- [ ] **Step 2: Insert the new step 4**

In `skills/writing-plans/SKILL.md`, insert a new step between these two exact lines — step 3's last line and step 4's first:

````markdown
history of consciously-deferred work.

**4. Retire.** `git mv` the plan to `specs/plans/completed/`, in one
````

Insert this, with one blank line on each side, so it sits between them:

````markdown
**4. Backlog triage.** Report backlog health, then bring the triage to your
human partner rather than waiting to be asked for it. Run from the repo root:

```bash
uv run --python 3.13 python ~/.claude/skills/writing-plans/scripts/deferred_stats.py
```

Surface its summary line — open count, closure rate, aged tail — in the
completion report. Always, even when this plan deferred nothing: the summary is
how the trend stays legible.

Then, when the backlog has **20 or more open items or any aged tail**, run
steps 1–4 of the **Triage rubric** in `references/deferred-backlog.md` and
present the grouped, sorted proposal as part of this completion batch. Those
four steps are read-only — no file is edited by presenting them.

Executing a disposition is your human partner's call and runs under
`/deferred`; this step's job is that the proposal exists without anyone having
to remember to ask for it. Present it, note that `/deferred` acts on a
selection, and continue to step 5 either way. The triage never blocks
completion — the aged tail is gated later, at
finishing-a-development-branch.
````

- [ ] **Step 3: Renumber Retire to step 5**

In `skills/writing-plans/SKILL.md`, change `**4. Retire.**` to `**5. Retire.**`. Then confirm no other text refers to "step 4" of this protocol:

Run: `grep -n 'step 4\|Step 4' skills/writing-plans/SKILL.md skills/executing-plans/SKILL.md skills/subagent-driven-development/SKILL.md skills/brainstorming/SKILL.md`
Expected: no hit that refers to the Plan Completion Protocol's step 4. (The execution skills reference the protocol by name, not by step number — this grep confirms that assumption still holds. If a hit does refer to it, update that reference to step 5.)

- [ ] **Step 4: Verify the protocol reads as five steps**

Run: `grep -n '^\*\*[0-9]\. ' skills/writing-plans/SKILL.md`
Expected: exactly five lines, numbered 1–5, in order: Resolve-before-defer gate, Markup the plan file, Update deferred items, Backlog triage, Retire.

- [ ] **Step 5: Commit**

```bash
git add skills/writing-plans/SKILL.md
git commit -m "feat(writing-plans): require closure conditions and auto-run backlog triage"
```

---
### Task 4: Aged-tail gate at branch finish

**Files:**
- Modify: `skills/finishing-a-development-branch/SKILL.md` (new § Step 1b after Step 1; Core principle line; Common Mistakes; Red Flags)

**Interfaces:**
- Consumes: `skills/writing-plans/references/deferred-backlog.md` § "Aged-tail gate" (Task 2), `skills/writing-plans/scripts/deferred_stats.py` (Task 1).
- Produces: nothing later tasks consume.

**Numbering constraint:** insert **Step 1b**. Do not renumber Steps 2–6. Step 5 says "Then: Cleanup worktree (Step 6)" in three places and the Quick Reference table depends on the existing numbers; renumbering breaks those silently.

- [ ] **Step 1: Update the Core principle line**

In `skills/finishing-a-development-branch/SKILL.md`, replace:

```markdown
**Core principle:** Verify tests → Detect environment → Present options → Execute choice → Clean up.
```

with:

```markdown
**Core principle:** Verify tests → Check deferred backlog → Detect environment → Present options → Execute choice → Clean up.
```

- [ ] **Step 2: Change the Step 1 hand-off line**

In the same file, in § Step 1, replace `**If tests pass:** Continue to Step 2.` with `**If tests pass:** Continue to Step 1b.`

- [ ] **Step 3: Insert Step 1b**

Immediately after the line you just edited, and before the line `### Step 2: Detect Environment`, insert:

````markdown
### Step 1b: Check Deferred Backlog

This is the last moment before the work leaves the building. Volume is
reported; only the **aged tail** gates.

```bash
uv run --python 3.13 python ~/.claude/skills/writing-plans/scripts/deferred_stats.py
```

Run it without `--json`: this step needs the human-readable summary, and reading
`aged >45d:` off that line is all the gate requires. If the script prints
`no specs/deferred_items.md in this repo`, or reports `0 open`, say nothing and
continue to Step 2.

**If `aged >45d:` is 0:** report the summary line as printed and continue to Step 2.

```
Deferred backlog: 12 open, 40 ever closed (closure rate 77%), aged >45d: 0.
```

**If `aged >45d:` is greater than 0:** report it and stop before the menu.

```
Deferred backlog: 44 open, 61 ever closed (closure rate 58%), aged >45d: 29.
Oldest open: 71d (12-audit_7_20_26).

29 items have been open past the 45-day review horizon. Before finishing:

1. Run `/deferred` to triage them
2. Acknowledge and carry them — tell me why, and I'll log it

Which?
```

Do not present the merge/PR menu until one of the two lands.

- **`/deferred`** is your human partner's to run. When they have, re-run the
  stats and continue from the new numbers.
- **Acknowledge** requires a reason. Append one plain bullet — never a
  checkbox, so it stays out of the backlog counts — under a
  `## Aged-backlog acknowledgements` section pinned directly beneath the
  file's `# Deferred items` title, creating that section if absent:

```markdown
## Aged-backlog acknowledgements
- 2026-09-08 — finished `feat/rate-limiter` with 29 items aged >45d, carried
  deliberately: the Redis decision is still with the platform team.
```

Commit that edit with the branch's other completion commits, then continue to
Step 2. The full contract is the **Aged-tail gate** section of the
writing-plans skill's `references/deferred-backlog.md`.

"Carried deliberately" with no reason is the silent default this gate exists to
convert into a conscious one. Never write the acknowledgement without asking —
taking the override on your partner's behalf defeats the whole mechanism.
````

- [ ] **Step 4: Add the Common Mistake**

In § Common Mistakes, after the `**Skipping test verification**` block, insert:

```markdown
**Taking the aged-tail override unasked**
- **Problem:** Writing the acknowledgement yourself turns a gate meant to force a conscious decision back into a silent default
- **Fix:** Present both options and wait; log only the reason your partner gives
```

- [ ] **Step 5: Add the Red Flags entries**

In § Red Flags, add to the **Never** list, after `- Proceed with failing tests`:

```markdown
- Present the merge/PR menu with an unaddressed aged tail
- Write an aged-backlog acknowledgement your partner did not ask for
```

and to the **Always** list, after `- Verify tests before offering options`:

```markdown
- Check the deferred backlog before offering options
```

- [ ] **Step 6: Verify the numbering survived**

Run: `grep -n '^### Step \|Step 6)' skills/finishing-a-development-branch/SKILL.md`
Expected: headings read `Step 1`, `Step 1b`, `Step 2`, `Step 3`, `Step 4`, `Step 5`, `Step 6` in that order, and the three "Cleanup worktree (Step 6)" references still say Step 6.

- [ ] **Step 7: Commit**

```bash
git add skills/finishing-a-development-branch/SKILL.md
git commit -m "feat(finishing-a-development-branch): gate the aged deferred tail"
```

---

### Task 5: Provenance and repo docs

**Files:**
- Modify: `NOTICE`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: every file created in Tasks 1–2.
- Produces: nothing.

**Why this is its own task:** `NOTICE` is authoritative for this repo and CLAUDE.md requires reading it before substantially changing any skill. `writing-plans` and `finishing-a-development-branch` are both superpowers-adapted (MIT, © 2025 Jesse Vincent); the new script and reference are Lowell Mason originals. Both facts have to land before the plan completes.

- [ ] **Step 1: Extend the superpowers "Changes from upstream" bullet**

In `NOTICE`, find the bullet beginning `- The planning/execution skills (brainstorming, writing-plans,` and ending `deferred-items log, spec/plan retirement).`. Append to that bullet, at the same indent:

```
    That lifecycle was extended again here with a deferred-backlog
    contract not present upstream: writing-plans/references/deferred-backlog.md
    (the triage rubric, item schema, and thresholds), the
    writing-plans/scripts/deferred_stats.py reporter, an automatic
    read-only triage step in the Plan Completion Protocol, and an
    aged-tail gate at Step 1b of finishing-a-development-branch. Those
    two files are original works by Lowell Mason under the same MIT
    terms; the surrounding adapted skills are unchanged in structure.
```

- [ ] **Step 2: Verify the provenance lint still passes**

Run: `uv run --python 3.13 python build/check_provenance.py`
Expected: exit 0, no output. (The lint checks that every `skills/<name>/` directory is attributed and that no binary assets are tracked; no new skill directory was added, so this is a regression check, not a new assertion.)

- [ ] **Step 3: Add the test-command block to CLAUDE.md**

In `CLAUDE.md`, in the `## Commands` fenced bash block, insert after the `describe-critique-methodology` block and before the `geographic-codes` block:

```bash
# writing-plans deferred-backlog stats tests (parser, age buckets, --json contract) — 10 tests
# (stdlib only; two tests drive the script as a subprocess through sys.executable)
cd skills/writing-plans/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

- [ ] **Step 4: Verify both lints and the new suite together**

Run from the repo root:

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && \
uv run --python 3.13 python build/check_provenance.py && \
(cd skills/writing-plans/scripts && uv run --python 3.13 --with pytest python -m pytest -q)
```

Expected: both lints silent with exit 0, then `10 passed`.

- [ ] **Step 5: Commit**

```bash
git add NOTICE CLAUDE.md
git commit -m "docs: attribute the deferred-backlog contract and document its tests"
```

---

## Notes for the executor

**Work in a worktree.** This plan edits `writing-plans` and
`finishing-a-development-branch` — the very skills whose Plan Completion
Protocol and branch-finish flow will run this plan. Use the using-git-worktrees
skill, and keep the controller's own tooling pinned to the main checkout so a
half-edited protocol never governs its own execution. Run the protocol at
completion from the **main checkout's** copy of `writing-plans`, not the
worktree's.

**Scope fence.** Two findings from the source review are deliberately out of
scope and must not be implemented here: R5 (a per-repo WIP cap) and the
586-line trim of `subagent-driven-development/SKILL.md`. Do not touch
`skills/subagent-driven-development/`.

**Where this cannot be validated.** The backlog problem that motivated this
plan lives in Lowell's work repos (309 open items across five), which this
repo cannot see. Locally the backlog is healthy — 21 open, 69 closed, 77%
closure — so a green run here proves the mechanism works, not that the numbers
move. That is why R4 is a script rather than prose: it has to run where the
problem is.

**This repo trips its own gate.** At the time of writing, `agent-skills` has
21 open items, 6 of them aged past 45 days (oldest 51d, in
`11-delegation-frontmatter-rollout`). So finishing *this* branch will hit the
Step 1b gate you just built — that is the intended dogfood, not a bug. Take
whichever branch the gate offers, on its merits.

**Sync caution.** Lowell's work environment runs a drifted copy of these skills
containing a "20+ open items" nudge and an aging computation that never came
back upstream to this repo. When these files are copied there, they must
**overwrite**, not merge — the new completion-protocol step 4 and Step 1b are
written as complete replacements, and merging would leave two nudges firing.

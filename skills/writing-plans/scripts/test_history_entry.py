'''Tests for history_entry.py: the draft of a retired plan's entry and of a /deferred pass's entry.'''
from __future__ import annotations

from pathlib import Path

from history_entry import closed_item_line, main, read_plan_text

PLAN = '''# Rate Limiter Implementation Plan

**Spec:** `specs/rate-limiter.md`

> Roadmap: specs/edge-roadmap.md, Stage 2 — on plan completion, tick the stage and re-validate later stages against what shipped.

## Decisions

- **D1** (owner, plan review, 2026-07-01): keep the per-IP bucket size. Applied in: Task 2.
- **D2** (owner, plan review, 2026-07-01): the 429 body is JSON. Applied in: Task 1 (spec
  amendment), Task 3.

---

### Task 1: Store

- [x] **Step 1: Write the failing test**

> Deviation: the store reads the limit from config, not from a constant.

### Task 2: Middleware

- [x] **Step 1: Run it**

  > Deviation (two, from review): `X-RateLimit` headers are lower-case.
'''

LEDGER = '''Plan: specs/plans/7-rate-limiter.md
Task 1: complete (commits a1b2c3d..d4e5f6a, review clean)
Task 3: Ruling: count requests per key, not per IP — the spec's per-IP rule breaks behind the proxy — clients behind one NAT share a key if wrong.
Ruling: returned 503, not the plan's 429, when the store is down — a 429 tells clients to back off from a fault that is ours — clients retry at once if wrong.
Final: Ruling: the jitter finding stays out — tests seed jitter on purpose — a flaky test if wrong.
'''

BACKLOG = '''# Deferred items

## 5-http-client — 2026-06-01
- [x] Retry jitter is fixed-seed in tests only
      (final review). Size: quick-fix. → done 2026-07-04 (plan 7)
- [x] Older tick form → done in plan 7 (D)
- [x] Belongs to another plan → done 2026-07-04 (plan 79)
- [ ] Open item with a note → done 2026-07-04 (plan 7)
- [x] Prose that quotes `→ done 2026-07-04 (plan 7)` only → retired 2026-07-04: gone.

## 7-rate-limiter — 2026-07-04
- [ ] Redis-backed counter store. Size: design. Done when: the DSN is recorded.
- [ ] Second deferred thing. Size: quick-fix. Done when: it lands.
'''

GOLDEN = '''## 7-rate-limiter — 2026-07-04
Plan: specs/plans/completed/7-rate-limiter.md · Spec: specs/completed/rate-limiter.md (retired) · Roadmap: specs/edge-roadmap.md, Stage 2

Differences from the design:
- Ruling (Task 3): count requests per key, not per IP — the spec's per-IP rule breaks behind the proxy — clients behind one NAT share a key if wrong.
- Ruling: returned 503, not the plan's 429, when the store is down — a 429 tells clients to back off from a fault that is ours — clients retry at once if wrong.
- Ruling (final review): the jitter finding stays out — tests seed jitter on purpose — a flaky test if wrong.
- Deviation (Task 1): the store reads the limit from config, not from a constant. Source: plan, Task 1.
- Deviation (Task 2): `X-RateLimit` headers are lower-case. Source: plan, Task 2.
- Decision D2 (spec amendment): the 429 body is JSON. Source: plan, `## Decisions`.
- Deferred: 2 items. Source: specs/deferred_items.md, § 7-rate-limiter.

Closed earlier deferred items:
- "Retry jitter is fixed-seed in tests only" (deferred by 5-http-client).
- "Older tick form" (deferred by 5-http-client).'''

TINY_PLAN = '''# Tiny Implementation Plan

**Spec:** none. The requirement is one item.

### Task 1: Do it

- [x] **Step 1: Do it**
'''

TINY_BACKLOG = '''# Deferred items

## 9-tiny — 2026-07-04
- [ ] One deferred thing. Size: quick-fix. Done when: it lands.
'''

NO_RULING_LEDGER = '''Plan: specs/plans/9-tiny.md
Task 1: complete (commits a1b2c3d..d4e5f6a, review clean)
'''

QUOTED = '''
````markdown
```python
> Deviation: quoted.
### Task 9: Quoted
- **D9** (owner, plan review, 2026-07-01): quoted. Applied in: Task 9 (spec amendment).
```
> Deviation: quoted.
### Task 9: Quoted
- **D9** (owner, plan review, 2026-07-01): quoted. Applied in: Task 9 (spec amendment).
````

Add a one-line `> Deviation: …` note.
'''

DATE = '2026-07-04'

AMENDMENT_FORMS = '''- **D3** (owner, plan review, 2026-07-01): the retry count is three. Applied in: Task 1 (spec amendment A2).
- **D4** (owner, plan review, 2026-07-01): the window slides. Applied in: Task 2 (spec amendments: R6.11, R8.5).
- **D5** (owner, plan review, 2026-07-01): the list stays as it is. Applied in: Task 3 (spec amendments).
- **D6** (owner, plan review, 2026-07-01): keep the (spec amendment A3) text in the spec. Applied in: Task 3.
'''

QUOTED_FENCES = '''
### Task 3: Examples

> ~~~markdown
> Deviation: an example inside a tilde fence.
> > Deviation: a nested example inside a tilde fence.
> ~~~

>    ```bash
>    Deviation: an example inside a backtick fence.
>    ````

> Deviation: a real note after the fences.
'''


QUICK = '''# Deferred items

## 34-calibration — 2026-09-20
- [x] The spread step is direction-blind
      (final review). → done 2026-10-05 (/deferred quick fix): signed the spread
      and added a test.
- [x] Quoted form only: `→ done 2026-10-05 (/deferred quick fix)` here
      → retired 2026-10-05: the premise is gone.
- [x] Fixed on another day → done 2026-10-04 (/deferred quick fix): moved the guard.
- [x] No note text → done 2026-10-05 (/deferred quick fix)
- [ ] Open, not closed → done 2026-10-05 (/deferred quick fix): typo.

## deferred-triage (no plan; /deferred pass, branch deferred-triage-2026-09-28) — 2026-09-28
- [x] Brief path is relative → done 2026-10-05 (/deferred quick fix): made it absolute.
'''

HISTORY = '''# Development history

## /deferred — 2026-10-04

Closed deferred items:
- "Brief path is relative" (deferred by deferred-triage): an older close.

## /deferred — 2026-10-05

Closed deferred items:
- "The spread step is direction-blind" (deferred by 34-calibration): signed it.
'''

DEFERRED_DATE = '2026-10-05'

DEFERRED_GOLDEN = '''## /deferred — 2026-10-05

Closed deferred items:
- "The spread step is direction-blind" (deferred by 34-calibration): signed the spread and added a test.
- "No note text" (deferred by 34-calibration).
- "Brief path is relative" (deferred by deferred-triage): made it absolute.
'''


def write_repo(
    root: Path,
    stem: str,
    plan_text: str,
    backlog: str | None = None,
    ledger: str | None = None,
) -> tuple[Path, Path | None]:
    '''Write a throwaway repo: the retired plan, the backlog and the ledger.'''
    plan = root / 'specs' / 'plans' / 'completed' / f'{stem}.md'
    plan.parent.mkdir(parents=True)
    plan.write_text(plan_text, encoding='utf-8')
    if backlog is not None:
        (root / 'specs' / 'deferred_items.md').write_text(backlog, encoding='utf-8')
    ledger_path = None
    if ledger is not None:
        ledger_path = root / 'run-ledger.md'
        ledger_path.write_text(ledger, encoding='utf-8')
    return plan, ledger_path


def run_draft(capsys, plan: Path, *args: str) -> tuple[int, str, str]:
    code = main(['draft', str(plan), *args])
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def golden_args(ledger: Path) -> list[str]:
    return [
        '--ledger', str(ledger),
        '--spec', 'specs/completed/rate-limiter.md', '--spec-status', 'retired',
        '--date', DATE,
    ]


def test_golden_draft(tmp_path, capsys):
    plan, ledger = write_repo(tmp_path, '7-rate-limiter', PLAN, BACKLOG, LEDGER)
    code, out, err = run_draft(capsys, plan, *golden_args(ledger))
    assert code == 0
    assert out == GOLDEN + '\n'
    assert err == ''


def test_no_ledger_and_spec_none(tmp_path, capsys):
    plan, _ = write_repo(tmp_path, '9-tiny', TINY_PLAN, TINY_BACKLOG)
    code, out, _ = run_draft(capsys, plan, '--date', DATE)
    assert code == 0
    assert out.splitlines() == [
        '## 9-tiny — 2026-07-04',
        'Plan: specs/plans/completed/9-tiny.md · Spec: none',
        'Rulings: no ledger given',
        '',
        'Differences from the design:',
        '- Deferred: 1 item. Source: specs/deferred_items.md, § 9-tiny.',
    ]


def test_header_spec_without_flag_warns(tmp_path, capsys):
    plan, ledger = write_repo(tmp_path, '7-rate-limiter', PLAN, BACKLOG, LEDGER)
    code, out, _ = run_draft(capsys, plan, '--ledger', str(ledger), '--date', DATE)
    assert code == 0
    lines = out.splitlines()
    assert lines[1].endswith(
        '· Spec: specs/rate-limiter.md (status not given) · Roadmap: specs/edge-roadmap.md, Stage 2'
    )
    assert lines[2] == 'Spec: --spec not given'


def test_both_warnings_come_in_order(tmp_path, capsys):
    plan, _ = write_repo(tmp_path, '7-rate-limiter', PLAN)
    code, out, _ = run_draft(capsys, plan, '--date', DATE)
    assert code == 0
    assert out.splitlines()[2:4] == ['Spec: --spec not given', 'Rulings: no ledger given']


def test_no_differences(tmp_path, capsys):
    plan, ledger = write_repo(tmp_path, '9-tiny', TINY_PLAN, ledger=NO_RULING_LEDGER)
    code, out, _ = run_draft(capsys, plan, '--ledger', str(ledger), '--date', DATE)
    assert code == 0
    assert out.splitlines() == [
        '## 9-tiny — 2026-07-04',
        'Plan: specs/plans/completed/9-tiny.md · Spec: none',
        '',
        'No differences from the design.',
    ]


def test_header_deviation(tmp_path, capsys):
    header_note = PLAN.replace(
        '## Decisions', '> Deviation: the plan ran on main.\n\n## Decisions', 1,
    )
    plan, ledger = write_repo(tmp_path, '7-rate-limiter', header_note, BACKLOG, LEDGER)
    code, out, _ = run_draft(capsys, plan, *golden_args(ledger))
    assert code == 0
    deviations = [line for line in out.splitlines() if line.startswith('- Deviation')]
    assert deviations[0] == '- Deviation: the plan ran on main. Source: plan, header.'
    assert len(deviations) == 3


def test_bold_deviation_label(tmp_path, capsys):
    bold = PLAN.replace('> Deviation: the store', '> **Deviation:** the store', 1)
    plan, ledger = write_repo(tmp_path, '7-rate-limiter', bold, BACKLOG, LEDGER)
    code, out, _ = run_draft(capsys, plan, *golden_args(ledger))
    assert code == 0
    assert out == GOLDEN + '\n'


WRAPPED_NOTE = '''> Deviation: the Task 1 brief extracted by scripts/task-brief truncated at 73/255 lines because
> this task's nested ```python blocks sat inside 3-backtick fences. The implementer detected it,
> verified the brief was a byte-identical prefix of the plan, and worked from the plan.'''

WRAPPED_LINE = (
    "- Deviation (Task 1): the Task 1 brief extracted by scripts/task-brief truncated at 73/255 lines because"
    " this task's nested ```python blocks sat inside 3-backtick fences. The implementer detected it,"
    ' verified the brief was a byte-identical prefix of the plan, and worked from the plan. Source: plan, Task 1.'
)

ONE_LINE_NOTE = '> Deviation: the store reads the limit from config, not from a constant.'
ONE_LINE = '- Deviation (Task 1): the store reads the limit from config, not from a constant. Source: plan, Task 1.'

BOLD_NOTE = '''
> **Deviation (2026-07-20, review-driven):** the Step 1 replacement text above shipped in a
> corrected form. The shipped text names the tail, not the mass near zero.
'''


def test_wrapped_deviation_joins_its_blockquote_lines(tmp_path, capsys):
    wrapped = PLAN.replace(ONE_LINE_NOTE, WRAPPED_NOTE, 1)
    plan, ledger = write_repo(tmp_path, '7-rate-limiter', wrapped, BACKLOG, LEDGER)
    code, out, _ = run_draft(capsys, plan, *golden_args(ledger))
    assert code == 0
    assert out == GOLDEN.replace(ONE_LINE, WRAPPED_LINE) + '\n'


def test_deviation_continuation_stops_at_a_break(tmp_path, capsys):
    stops = '''
### Task 3: Stops

> Deviation: first note, line one
> and line two.
>
> still the blockquote, but after a bare marker.
> Deviation: second note touches the first.
Plain line.
> Deviation: third note, then a plain line follows.
Not quoted.
> not part of any note.
'''
    plan, ledger = write_repo(tmp_path, '7-rate-limiter', PLAN + stops, BACKLOG, LEDGER)
    code, out, _ = run_draft(capsys, plan, *golden_args(ledger))
    assert code == 0
    deviations = [line for line in out.splitlines() if line.startswith('- Deviation (Task 3)')]
    assert deviations == [
        '- Deviation (Task 3): first note, line one and line two. Source: plan, Task 3.',
        '- Deviation (Task 3): second note touches the first. Source: plan, Task 3.',
        '- Deviation (Task 3): third note, then a plain line follows. Source: plan, Task 3.',
    ]


def test_bold_dated_deviation_drops_its_bold_marks(tmp_path, capsys):
    plan, ledger = write_repo(tmp_path, '7-rate-limiter', PLAN + BOLD_NOTE, BACKLOG, LEDGER)
    code, out, _ = run_draft(capsys, plan, *golden_args(ledger))
    assert code == 0
    bold = [line for line in out.splitlines() if 'Step 1 replacement text' in line]
    assert bold == [
        '- Deviation (Task 2): the Step 1 replacement text above shipped in a corrected form.'
        ' The shipped text names the tail, not the mass near zero. Source: plan, Task 2.'
    ]
    assert '**' not in bold[0]


def test_backticked_none_spec_header_is_none(tmp_path, capsys):
    backticked = TINY_PLAN.replace(
        '**Spec:** none. The requirement is one item.',
        '**Spec:** `none`. The requirement is an item in `specs/deferred_items.md`.',
    )
    plan, ledger = write_repo(tmp_path, '9-tiny', backticked, ledger=NO_RULING_LEDGER)
    code, out, _ = run_draft(capsys, plan, '--ledger', str(ledger), '--date', DATE)
    assert code == 0
    assert out.splitlines()[1] == 'Plan: specs/plans/completed/9-tiny.md · Spec: none'
    assert 'Spec: --spec not given' not in out


def test_roadmap_header_line_without_a_quote_prefix(tmp_path, capsys):
    bare = TINY_PLAN.replace(
        '\n### Task 1',
        '\nRoadmap: specs/x-roadmap.md, Stage 2 — on plan completion, tick the stage.\n\n### Task 1',
        1,
    )
    plan, ledger = write_repo(tmp_path, '9-tiny', bare, ledger=NO_RULING_LEDGER)
    code, out, _ = run_draft(capsys, plan, '--ledger', str(ledger), '--date', DATE)
    assert code == 0
    assert out.splitlines()[1] == (
        'Plan: specs/plans/completed/9-tiny.md · Spec: none · Roadmap: specs/x-roadmap.md, Stage 2'
    )


def test_closed_items_without_differences_print_no_differences_line(tmp_path, capsys):
    backlog = (
        '## 5-http-client — 2026-06-01\n'
        '- [x] Retry jitter is fixed-seed in tests only → done 2026-07-04 (plan 9)\n'
    )
    plan, ledger = write_repo(tmp_path, '9-tiny', TINY_PLAN, backlog, NO_RULING_LEDGER)
    code, out, _ = run_draft(capsys, plan, '--ledger', str(ledger), '--date', DATE)
    assert code == 0
    assert out.splitlines() == [
        '## 9-tiny — 2026-07-04',
        'Plan: specs/plans/completed/9-tiny.md · Spec: none',
        '',
        'Closed earlier deferred items:',
        '- "Retry jitter is fixed-seed in tests only" (deferred by 5-http-client).',
    ]


def test_deviation_under_a_heading_after_the_tasks_names_that_heading(tmp_path, capsys):
    later = PLAN + (
        '\n## Plan Completion\n\n> Deviation: the retire commit also renamed a file.\n'
        '\n### Self-review\n\n> Deviation: the review found no gaps.\n'
    )
    plan, ledger = write_repo(tmp_path, '7-rate-limiter', later, BACKLOG, LEDGER)
    code, out, _ = run_draft(capsys, plan, *golden_args(ledger))
    assert code == 0
    lines = out.splitlines()
    assert '- Deviation: the retire commit also renamed a file. Source: plan, § Plan Completion.' in lines
    assert '- Deviation: the review found no gaps. Source: plan, § Self-review.' in lines
    assert [line for line in lines if 'Task 2' in line] == [
        '- Deviation (Task 2): `X-RateLimit` headers are lower-case. Source: plan, Task 2.'
    ]


def test_deviation_before_the_first_task_stays_the_headers_after_a_heading(tmp_path, capsys):
    early = PLAN.replace('- **D1**', '> Deviation: the plan ran on main.\n\n- **D1**', 1)
    plan, ledger = write_repo(tmp_path, '7-rate-limiter', early, BACKLOG, LEDGER)
    code, out, _ = run_draft(capsys, plan, *golden_args(ledger))
    assert code == 0
    assert '- Deviation: the plan ran on main. Source: plan, header.' in out.splitlines()


def test_quoted_forms_in_code_are_not_read(tmp_path, capsys):
    plan, ledger = write_repo(tmp_path, '7-rate-limiter', PLAN + QUOTED, BACKLOG, LEDGER)
    code, out, _ = run_draft(capsys, plan, *golden_args(ledger))
    assert code == 0
    assert out == GOLDEN + '\n'


def test_spec_amendment_decisions_in_variant_forms_are_listed(tmp_path, capsys):
    varied = PLAN.replace('  amendment), Task 3.\n', '  amendment), Task 3.\n' + AMENDMENT_FORMS, 1)
    plan, ledger = write_repo(tmp_path, '7-rate-limiter', varied, BACKLOG, LEDGER)
    code, out, _ = run_draft(capsys, plan, *golden_args(ledger))
    assert code == 0
    decisions = [line for line in out.splitlines() if line.startswith('- Decision')]
    assert decisions == [
        '- Decision D2 (spec amendment): the 429 body is JSON. Source: plan, `## Decisions`.',
        '- Decision D3 (spec amendment): the retry count is three. Source: plan, `## Decisions`.',
        '- Decision D4 (spec amendment): the window slides. Source: plan, `## Decisions`.',
        '- Decision D5 (spec amendment): the list stays as it is. Source: plan, `## Decisions`.',
    ]


def test_quoted_fences_in_a_blockquote_are_not_read(tmp_path, capsys):
    plan, ledger = write_repo(tmp_path, '7-rate-limiter', PLAN + QUOTED_FENCES, BACKLOG, LEDGER)
    code, out, _ = run_draft(capsys, plan, *golden_args(ledger))
    assert code == 0
    assert out == GOLDEN.replace(
        '- Decision D2',
        '- Deviation (Task 3): a real note after the fences. Source: plan, Task 3.\n- Decision D2',
    ) + '\n'


def test_quoted_fence_is_blanked_from_opener_to_closer_keeping_every_length():
    text = '> ```bash\n> echo hi\n> ```\n> kept\n>~~~\n>   code\n> > ~~~\nplain'
    plan = read_plan_text(text)
    assert [len(line) for line in plan.masked] == [len(line) for line in plan.lines]
    assert [line.strip() for line in plan.masked] == ['', '', '', '> kept', '', '', '', 'plain']


def test_quoted_fence_closes_only_on_the_same_mark_at_least_as_long():
    text = '> ~~~~\n> ~~~\n> ```` x\n> ````\n> inside\n> ~~~~~\n> after'
    masked = read_plan_text(text).masked
    assert [line.strip() for line in masked] == ['', '', '', '', '', '', '> after']


def test_unclosed_quoted_fence_ends_with_its_blockquote():
    text = '> ~~~\n> inside\n\n> Deviation: real.'
    masked = read_plan_text(text).masked
    assert [line.strip() for line in masked] == ['', '', '', '> Deviation: real.']


def test_backtick_fence_with_backticks_in_its_info_is_not_an_opener():
    text = '> ```x``` is not a fence\n> Deviation: real.'
    assert read_plan_text(text).masked[1] == '> Deviation: real.'


def test_plan_id_matches_whole_word(tmp_path, capsys):
    plan, ledger = write_repo(tmp_path, '7-rate-limiter', PLAN, BACKLOG, LEDGER)
    _, out, _ = run_draft(capsys, plan, *golden_args(ledger))
    assert not [line for line in out.splitlines() if 'Belongs to another plan' in line]


def test_unticked_and_quoted_ticks_are_not_closes(tmp_path, capsys):
    plan, ledger = write_repo(tmp_path, '7-rate-limiter', PLAN, BACKLOG, LEDGER)
    _, out, _ = run_draft(capsys, plan, *golden_args(ledger))
    assert 'Open item with a note' not in out
    assert 'Prose that quotes' not in out


def test_no_plan_id_gives_no_closed_items_and_no_deferred_line(tmp_path, capsys):
    plan, _ = write_repo(tmp_path, 'tiny', TINY_PLAN, TINY_BACKLOG.replace('9-tiny', 'tiny'))
    code, out, _ = run_draft(capsys, plan, '--date', DATE)
    assert code == 0
    assert 'Deferred:' not in out
    assert 'Closed earlier' not in out


def test_missing_plan_exits_2(tmp_path, capsys):
    plan = tmp_path / 'specs' / 'plans' / 'completed' / '9-gone.md'
    code, out, err = run_draft(capsys, plan, '--date', DATE)
    assert code == 2
    assert out == ''
    assert len(err.splitlines()) == 1
    assert str(plan) in err


def test_not_a_plan_exits_2(tmp_path, capsys):
    prose = '# Notes\n\n```\n### Task 1: Only in code\n```\n'
    plan, _ = write_repo(tmp_path, '9-notes', prose)
    code, out, err = run_draft(capsys, plan, '--date', DATE)
    assert code == 2
    assert out == ''
    assert len(err.splitlines()) == 1
    assert str(plan) in err


def test_plan_outside_a_specs_directory_exits_2(tmp_path, capsys):
    plan = tmp_path / 'notes' / '9-tiny.md'
    plan.parent.mkdir()
    plan.write_text(TINY_PLAN, encoding='utf-8')
    code, out, err = run_draft(capsys, plan, '--date', DATE)
    assert code == 2
    assert out == ''
    assert len(err.splitlines()) == 1
    assert str(plan) in err


def test_missing_ledger_exits_2(tmp_path, capsys):
    plan, _ = write_repo(tmp_path, '9-tiny', TINY_PLAN)
    ledger = tmp_path / 'no-such-ledger.md'
    code, out, err = run_draft(capsys, plan, '--ledger', str(ledger), '--date', DATE)
    assert code == 2
    assert out == ''
    assert len(err.splitlines()) == 1
    assert str(ledger) in err


def test_spec_without_status_exits_2(tmp_path, capsys):
    plan, _ = write_repo(tmp_path, '9-tiny', TINY_PLAN)
    code, out, err = run_draft(capsys, plan, '--spec', 'specs/x.md')
    assert code == 2
    assert out == ''
    assert len(err.splitlines()) == 1


def test_status_without_spec_exits_2(tmp_path, capsys):
    plan, _ = write_repo(tmp_path, '9-tiny', TINY_PLAN)
    code, out, err = run_draft(capsys, plan, '--spec-status', 'live')
    assert code == 2
    assert out == ''
    assert len(err.splitlines()) == 1


def test_closed_item_line_form():
    assert closed_item_line('A title', '5-http-client') == '- "A title" (deferred by 5-http-client).'
    assert closed_item_line('A title', 'x', 'it is fixed.') == '- "A title" (deferred by x): it is fixed.'


def test_closed_item_section_without_plan_uses_its_slug(tmp_path, capsys):
    backlog = (
        '## deferred-triage (no plan; /deferred pass, branch deferred-triage-2026-09-28) — 2026-09-28\n'
        '- [x] Brief path is relative → done 2026-07-04 (plan 9)\n'
    )
    plan, _ = write_repo(tmp_path, '9-tiny', TINY_PLAN, backlog)
    _, out, _ = run_draft(capsys, plan, '--date', DATE)
    assert '- "Brief path is relative" (deferred by deferred-triage).' in out.splitlines()


def write_deferred_repo(root: Path, backlog: str | None, history: str | None = None) -> None:
    '''Write the backlog and the history file that `deferred` reads from the current directory.'''
    (root / 'specs').mkdir()
    if backlog is not None:
        (root / 'specs' / 'deferred_items.md').write_text(backlog, encoding='utf-8')
    if history is not None:
        (root / 'specs' / 'history.md').write_text(history, encoding='utf-8')


def run_deferred(capsys, *args: str) -> tuple[int, str, str]:
    code = main(['deferred', *args])
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_deferred_draft(tmp_path, monkeypatch, capsys):
    write_deferred_repo(tmp_path, QUICK)
    monkeypatch.chdir(tmp_path)
    code, out, err = run_deferred(capsys, '--date', DEFERRED_DATE)
    assert code == 0
    assert out == DEFERRED_GOLDEN
    assert err == ''


def test_quoted_quick_fix_form_is_not_a_close(tmp_path, monkeypatch, capsys):
    write_deferred_repo(tmp_path, QUICK)
    monkeypatch.chdir(tmp_path)
    _, out, _ = run_deferred(capsys, '--date', DEFERRED_DATE)
    for name in ('Quoted form only', 'Fixed on another day', 'Open, not closed'):
        assert not any(name in line for line in out.splitlines())


def test_second_pass_same_date_lists_only_new_items(tmp_path, monkeypatch, capsys):
    write_deferred_repo(tmp_path, QUICK, HISTORY)
    monkeypatch.chdir(tmp_path)
    code, out, _ = run_deferred(capsys, '--date', DEFERRED_DATE)
    assert code == 0
    listed = [line for line in out.splitlines() if line.startswith('- ')]
    assert listed == [
        '- "No note text" (deferred by 34-calibration).',
        '- "Brief path is relative" (deferred by deferred-triage): made it absolute.',
    ]


def test_all_listed_prints_nothing(tmp_path, monkeypatch, capsys):
    history = HISTORY + (
        '\n## /deferred — 2026-10-05\n\nClosed deferred items:\n'
        '- "No note text" (deferred by 34-calibration).\n'
        '- "Brief path is relative" (deferred by deferred-triage): made it absolute.\n'
    )
    write_deferred_repo(tmp_path, QUICK, history)
    monkeypatch.chdir(tmp_path)
    code, out, err = run_deferred(capsys, '--date', DEFERRED_DATE)
    assert code == 0
    assert out == ''
    assert err == ''


def test_no_backlog_prints_nothing(tmp_path, monkeypatch, capsys):
    write_deferred_repo(tmp_path, None, HISTORY)
    monkeypatch.chdir(tmp_path)
    code, out, err = run_deferred(capsys, '--date', DEFERRED_DATE)
    assert code == 0
    assert out == ''
    assert err == ''

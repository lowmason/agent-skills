#!/usr/bin/env python3
# /// script
# requires-python = '>=3.11'
# dependencies = []
# ///
'''Draft an entry for specs/history.md: for a retired plan, or for a /deferred pass.

The `draft` subcommand prints the draft entry for one retired plan, from the plan,
its run ledger and the backlog. The agent that retires the plan finishes the draft
and appends it to `specs/history.md`. The script never writes a file.

The draft lists every ledger ruling. It also lists the plan's deviation notes and
its decisions whose `Applied in:` part holds `(spec amendment` or `(spec amendments`
(for example `(spec amendment A2)` or `(spec amendments: R6.11)`), the count of items
the plan deferred, and the earlier deferred items that the plan closed. The agent
removes the rulings that did not change the build (spec D7).

A form inside a fenced block, a fenced block inside a blockquote, or an inline code
span is quoted text, so it is never read. The plan's header lines come from above
its first `## ` heading.

The `deferred` subcommand prints the draft entry for a /deferred pass. It lists the
ticked items of `specs/deferred_items.md` that carry a `done` note with the pass
date and the mark `(/deferred quick fix)`. It leaves out each item that an earlier
`## /deferred` section of that date in `specs/history.md` already lists. It prints
nothing when no item qualifies. Both files are read from the current directory.

Usage:
    uv run <this-skill-dir>/scripts/history_entry.py draft <plan> \\
        [--ledger <path>] [--spec <path> --spec-status retired|live] [--date YYYY-MM-DD]
    uv run <this-skill-dir>/scripts/history_entry.py deferred [--date YYYY-MM-DD]

Exit 0 with a draft, or with no output for `deferred` when no item qualifies. Exit 2
with a one-line error on stderr when an input is bad, for example a plan file that
is missing or is not a plan.
'''

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from deferral_scan import blank_code
from deferred_stats import NOTE_RE, Item, parse_items

PROG = 'history_entry.py'
EXIT_BAD_INPUT = 2
SPECS_DIR = 'specs'
BACKLOG_PATH = 'specs/deferred_items.md'
HISTORY_PATH = 'specs/history.md'
SPEC_STATUSES = ('retired', 'live')
NO_SPEC = 'none'
STATUS_NOT_GIVEN = 'status not given'
ROADMAP_END = ' — '
SPEC_AMENDMENT = '(spec amendment)'  # the printed label
APPLIED_IN = ' Applied in:'
DECISION_CLOSE = '): '
RULING_MARK = 'Ruling:'
DECISIONS_SOURCE = '`## Decisions`'
DONE_KIND = 'done'
QUICK_FIX_MARK = '(/deferred quick fix)'
DEFERRED_HEADING = '## /deferred — '

H2_RE = re.compile(r'^##\s')
SECTION_HEADING_RE = re.compile(r'^#{2,3}\s')
HEADING_MARKS_RE = re.compile(r'^#+\s*')
TASK_RE = re.compile(r'^###\s+Task\s+(?P<number>\d+)')
SPEC_LINE_RE = re.compile(r'^\*\*Spec:\*\*')
NO_SPEC_RE = re.compile(rf'`?{NO_SPEC}\b')
SPEC_PATH_RE = re.compile(r'specs/[\w./-]+\.md(?!\w)')
ROADMAP_LINE_RE = re.compile(r'^\s*(?:>\s*)?Roadmap:')
DEVIATION_RE = re.compile(r'^\s*>\s*(\*\*)?Deviation\b[^:]*:(?:\*\*)?')
BLOCKQUOTE_RE = re.compile(r'^\s*>')
QUOTE_MARKS_RE = re.compile(r'^\s*(?:>\s*)+')
QUOTED_FENCE_OPEN_RE = re.compile(r'^\s*(?:>\s*)+(?P<run>`{3,}|~{3,})(?P<info>.*)$')
BLOCKQUOTE_PREFIX_RE = re.compile(r'^\s*>\s*')
BARE_BLOCKQUOTE_RE = re.compile(r'^\s*>\s*$')
DECISION_RE = re.compile(r'^- \*\*(?P<id>D\d+)\*\*')
SPEC_AMENDMENT_MARK_RE = re.compile(r'\(spec amendments?\b')
LEDGER_TASK_RE = re.compile(r'^\s*Task\s+(?P<number>\d+)')
LEDGER_FINAL_RE = re.compile(r'^\s*Final\b')
PLAN_ID_RE = re.compile(r'(?P<id>\d+)-')
ISO_DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')


class InputError(Exception):
    '''A bad input. `main` prints the message as one line on stderr and exits 2.'''


@dataclass(frozen=True)
class PlanText:
    '''A plan's lines, and the same lines with code blanked.

    The code is each fenced block, each fenced block inside a blockquote and each
    inline code span. A match is decided on `masked`, so a form quoted in code never
    matches. The printed text comes from `lines`.
    '''

    lines: list[str]
    masked: list[str]


def _quoted_fence_run(line: str) -> str:
    '''The run of backticks or tildes that opens a fence after the `>` marks, or an empty string.

    The info string of a backtick fence holds no backtick, so a line like
    `> ```x``` text` opens no fence.
    '''
    opener = QUOTED_FENCE_OPEN_RE.match(line)
    if not opener or (opener.group('run')[0] == '`' and '`' in opener.group('info')):
        return ''
    return opener.group('run')


def _quoted_fence_end(lines: list[str], start: int, run: str) -> int:
    '''The index of the last line of the blockquoted fence that opens at `start`.

    The fence ends at the next blockquoted line that closes it: as many `>` marks as
    the opener, then the same character, at least as long, and nothing else. A fence
    never closed ends with its blockquote, at the last line that starts with `>`.
    '''
    depth = QUOTE_MARKS_RE.match(lines[start]).group(0).count('>')
    end = start
    for index in range(start + 1, len(lines)):
        if not BLOCKQUOTE_RE.match(lines[index]):
            break
        end = index
        marks = QUOTE_MARKS_RE.match(lines[index])
        closer = lines[index][marks.end():].strip()
        closes = len(closer) >= len(run) and closer == run[0] * len(closer)
        if closes and marks.group(0).count('>') == depth:
            break
    return end


def _blank_quoted_fences(lines: list[str], masked: list[str]) -> list[str]:
    '''`masked` with each fenced block inside a blockquote blanked, line lengths kept.

    A block runs from a line that opens a fence after its `>` marks through its
    closer. The opener and the closer are read on `lines`, because `blank_code` may
    already have blanked their backticks.
    '''
    blanked = list(masked)
    index = 0
    while index < len(lines):
        run = _quoted_fence_run(lines[index])
        if not run:
            index += 1
            continue
        end = _quoted_fence_end(lines, index, run)
        for covered in range(index, end + 1):
            blanked[covered] = ' ' * len(masked[covered])
        index = end + 1
    return blanked


def read_plan_text(text: str) -> PlanText:
    lines = text.split('\n')
    return PlanText(lines, _blank_quoted_fences(lines, blank_code(text).split('\n')))


def _read_text(path: Path, what: str) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as error:
        raise InputError(f'{path}: cannot read the {what} ({error.__class__.__name__})') from error


def _header_end(plan: PlanText) -> int:
    '''The index of the first `## ` heading outside code, or the line count.'''
    return next((i for i, line in enumerate(plan.masked) if H2_RE.match(line)), len(plan.masked))


def _header_value(plan: PlanText, marker: re.Pattern[str]) -> str | None:
    '''The text after the first header line that opens with `marker`, or None.'''
    end = _header_end(plan)
    for original, masked in zip(plan.lines[:end], plan.masked[:end]):
        match = marker.match(masked)
        if match:
            return original[match.end():].strip()
    return None


def header_spec(plan: PlanText) -> str | None:
    '''`none`, the first `specs/...md` path of the `**Spec:**` header line, or None.'''
    value = _header_value(plan, SPEC_LINE_RE)
    if value is None:
        return None
    if NO_SPEC_RE.match(value):
        return NO_SPEC
    path = SPEC_PATH_RE.search(value)
    return path.group(0) if path else None


def header_roadmap(plan: PlanText) -> str | None:
    '''The `Roadmap:` header value up to its first ` — `, or None.'''
    value = _header_value(plan, ROADMAP_LINE_RE)
    if value is None:
        return None
    return value.split(ROADMAP_END, 1)[0].strip() or None


def has_task_heading(plan: PlanText) -> bool:
    return any(TASK_RE.match(line) for line in plan.masked)


def _deviation_text(plan: PlanText, index: int, note: re.Match[str]) -> str:
    '''The note's text: what follows the colon, plus each following line of its blockquote.

    The blockquote ends at a line that does not start with `>`, at a bare `>` line,
    and at a line that opens the next deviation note. The lines are joined with
    single spaces and one trailing `.` is removed. A line that starts with `>` but is
    blank in `masked` lies in a fenced block inside the blockquote. It adds no text
    and ends nothing, so a bare `>` line inside the fence does not end the note.
    '''
    parts = [plan.lines[index][note.end():].strip()]
    for original, masked in zip(plan.lines[index + 1:], plan.masked[index + 1:]):
        if BLOCKQUOTE_RE.match(original) and not masked.strip():
            continue
        if (not BLOCKQUOTE_RE.match(masked) or BARE_BLOCKQUOTE_RE.match(original)
                or DEVIATION_RE.match(masked)):
            break
        parts.append(BLOCKQUOTE_PREFIX_RE.sub('', original, count=1).strip())
    return ' '.join(part for part in parts if part).removesuffix('.')


def deviation_lines(plan: PlanText) -> list[str]:
    '''One difference line per deviation note, in plan order.

    A note's source is the last `##` or `###` heading above it. Above the first
    `### Task` heading that is the plan header. Under a `### Task <N>` heading it is
    that task. Under any other heading after a task it is that heading's text.
    '''
    found = []
    seen_task = False
    label, where = '', 'header'
    for index, masked in enumerate(plan.masked):
        if SECTION_HEADING_RE.match(masked):
            task = TASK_RE.match(masked)
            if task:
                seen_task = True
                label, where = f' (Task {task.group("number")})', f'Task {task.group("number")}'
            elif seen_task:
                label, where = '', f'§ {HEADING_MARKS_RE.sub("", plan.lines[index]).strip()}'
            continue
        note = DEVIATION_RE.match(masked)
        if note:
            text = _deviation_text(plan, index, note)
            found.append(f'- Deviation{label}: {text}. Source: plan, {where}.')
    return found


def _is_continuation(line: str) -> bool:
    return line[:1].isspace() and bool(line.strip())


def _spec_decision_line(number: str, joined: str, masked_joined: str) -> str | None:
    '''The difference line for a decision whose `Applied in:` part has a `(spec amendment` mark.

    The mark opens `(spec amendment)`, `(spec amendments)`, `(spec amendment A2)` and the like.
    It is read on the masked text, so a mark inside inline code does not count. The printed
    text comes from the original, and its label stays `(spec amendment)`.
    '''
    _, masked_found, masked_applied = masked_joined.rpartition(APPLIED_IN)
    if not masked_found or not SPEC_AMENDMENT_MARK_RE.search(masked_applied):
        return None
    head, found, _ = joined.rpartition(APPLIED_IN)
    close = head.find(DECISION_CLOSE)
    if not found or close == -1:
        return None
    text = head[close + len(DECISION_CLOSE):].strip().removesuffix('.')
    return f'- Decision {number} {SPEC_AMENDMENT}: {text}. Source: plan, {DECISIONS_SOURCE}.'


def decision_lines(plan: PlanText) -> list[str]:
    '''One difference line per spec-level decision, in plan order.

    A decision is a `- **D<n>**` bullet and its indented continuation lines.
    '''
    found = []
    index = 0
    while index < len(plan.lines):
        start = DECISION_RE.match(plan.masked[index])
        if not start:
            index += 1
            continue
        parts = [plan.lines[index].strip()]
        masked_parts = [plan.masked[index].strip()]
        index += 1
        while index < len(plan.lines) and _is_continuation(plan.lines[index]):
            parts.append(plan.lines[index].strip())
            masked_parts.append(plan.masked[index].strip())
            index += 1
        line = _spec_decision_line(start.group('id'), ' '.join(parts), ' '.join(masked_parts))
        if line:
            found.append(line)
    return found


def ruling_lines(ledger_text: str) -> list[str]:
    '''One difference line per ledger line that holds `Ruling:`, in ledger order.'''
    found = []
    for line in ledger_text.split('\n'):
        _, mark, text = line.partition(RULING_MARK)
        if not mark:
            continue
        label = ''
        if task := LEDGER_TASK_RE.match(line):
            label = f' (Task {task.group("number")})'
        elif LEDGER_FINAL_RE.match(line):
            label = ' (final review)'
        found.append(f'- Ruling{label}: {text.strip()}')
    return found


def closed_item_head(title: str, section: str) -> str:
    '''`- "<title>" (deferred by <section>)`, the part of a closed-item line that names the item.'''
    return f'- "{title}" (deferred by {section})'


def closed_item_line(title: str, section: str, detail: str = '') -> str:
    '''The head of a closed-item line, closed by a period or by `: <detail>`.'''
    head = closed_item_head(title, section)
    return f'{head}: {detail}' if detail else f'{head}.'


def item_title(item: Item) -> str:
    '''The item's first line with its notes cut and its spaces collapsed.

    A note runs to the end of its line, so the first note on the line starts the cut.
    '''
    first_end = item.text.find('\n')
    if first_end == -1:
        first_end = len(item.text)
    note = NOTE_RE.search(blank_code(item.text), 0, first_end)
    return ' '.join(item.text[:note.start() if note else first_end].split())


def item_section(item: Item) -> str:
    '''The section name up to its first ` (`, so a section with no plan keeps its slug.'''
    return item.section.partition(' (')[0].strip()


def closed_by_plan(items: list[Item], plan_id: str) -> list[Item]:
    '''Ticked items that have a `done` note naming `plan <id>` as a whole word.'''
    names_plan = re.compile(rf'(?<![\w-])plan\s+#?{re.escape(plan_id)}(?![\w-])')
    return [
        item for item in items
        if item.checked and any(
            note.kind == 'done' and names_plan.search(note.rest) for note in item.notes
        )
    ]


def _deferred_line(count: int, stem: str) -> str:
    noun = 'item' if count == 1 else 'items'
    return f'- Deferred: {count} {noun}. Source: {BACKLOG_PATH}, § {stem}.'


def _spec_part(spec: str | None, status: str | None, header: str | None) -> tuple[str, str | None]:
    '''The `Spec:` value and the warning line that goes with it, if any.'''
    if spec is not None:
        return f'{spec} ({status})', None
    if header is None or header == NO_SPEC:
        return NO_SPEC, None
    return f'{header} ({STATUS_NOT_GIVEN})', 'Spec: --spec not given'


def _repo_root(plan_path: Path) -> Path | None:
    '''The parent of the plan's nearest ancestor directory named `specs`, or None.'''
    for ancestor in plan_path.parents:
        if ancestor.name == SPECS_DIR:
            return ancestor.parent
    return None


@dataclass(frozen=True)
class DraftInputs:
    plan: Path
    ledger: Path | None
    spec: str | None
    spec_status: str | None
    date: str


def draft_entry(inputs: DraftInputs) -> str:
    '''The draft history entry for one retired plan.'''
    if (inputs.spec is None) != (inputs.spec_status is None):
        raise InputError('--spec and --spec-status come as a pair')
    if not inputs.plan.is_file():
        raise InputError(f'{inputs.plan}: plan file not found')
    plan_path = inputs.plan.resolve()
    root = _repo_root(plan_path)
    plan = read_plan_text(_read_text(inputs.plan, 'plan'))
    if root is None or not has_task_heading(plan):
        raise InputError(f'{inputs.plan}: not a plan (it has no ### Task heading under a specs directory)')
    ledger_text = None
    if inputs.ledger is not None:
        if not inputs.ledger.is_file():
            raise InputError(f'{inputs.ledger}: ledger file not found')
        ledger_text = _read_text(inputs.ledger, 'ledger')

    stem = plan_path.stem
    spec_text, spec_warning = _spec_part(inputs.spec, inputs.spec_status, header_spec(plan))
    first = [f'Plan: {plan_path.relative_to(root).as_posix()}', f'Spec: {spec_text}']
    if roadmap := header_roadmap(plan):
        first.append(f'Roadmap: {roadmap}')
    warnings = [spec_warning] if spec_warning else []
    if ledger_text is None:
        warnings.append('Rulings: no ledger given')

    differences = ruling_lines(ledger_text) if ledger_text is not None else []
    differences += deviation_lines(plan) + decision_lines(plan)
    closed: list[str] = []
    backlog = root / BACKLOG_PATH
    plan_id = PLAN_ID_RE.match(stem)
    if plan_id and backlog.is_file():
        items = parse_items(_read_text(backlog, 'backlog'))
        deferred = sum(1 for item in items if item.section == stem)
        if deferred:
            differences.append(_deferred_line(deferred, stem))
        closed = [
            closed_item_line(item_title(item), item_section(item))
            for item in closed_by_plan(items, plan_id.group('id'))
        ]

    lines = [f'## {stem} — {inputs.date}', ' · '.join(first), *warnings]
    if differences:
        lines += ['', 'Differences from the design:', *differences]
    if closed:
        lines += ['', 'Closed earlier deferred items:', *closed]
    if not differences and not closed:
        lines += ['', 'No differences from the design.']
    return '\n'.join(lines)


def quick_fix_detail(item: Item, date: str) -> str | None:
    '''The text of the item's `done <date> (/deferred quick fix)` note, or None.

    None when the item is open or has no such note. The text may be empty. A note
    runs to the next note or to the item's end, over its continuation lines, so it
    is read from `item.text`: `Note.rest` stops at the end of the note's line. The
    lines are joined with single spaces.
    '''
    if not item.checked:
        return None
    text = item.text
    notes = list(NOTE_RE.finditer(blank_code(text)))
    for index, note in enumerate(notes):
        if note.group('kind') != DONE_KIND or note.group('date') != date:
            continue
        end = notes[index + 1].start() if index + 1 < len(notes) else len(text)
        words = ' '.join(text[note.end():end].split()).lstrip(': ')
        if words.startswith(QUICK_FIX_MARK):
            return words.removeprefix(QUICK_FIX_MARK).lstrip(': ')
    return None


def _listed_lines(history_text: str, date: str) -> list[str]:
    '''The lines under every `## /deferred — <date>` heading of the history file.'''
    heading = f'{DEFERRED_HEADING}{date}'
    lines = []
    inside = False
    for line in history_text.split('\n'):
        if H2_RE.match(line):
            inside = line.rstrip() == heading
        elif inside:
            lines.append(line)
    return lines


def deferred_entry(date: str) -> str:
    '''The draft history entry for a /deferred pass, or '' when no item qualifies.

    Reads `specs/deferred_items.md` and `specs/history.md` from the current directory.
    An item that a `## /deferred` section of the same date already lists is left out.
    '''
    backlog = Path(BACKLOG_PATH)
    if not backlog.is_file():
        return ''
    history = Path(HISTORY_PATH)
    listed = _listed_lines(_read_text(history, 'history file') if history.is_file() else '', date)
    closed = []
    for item in parse_items(_read_text(backlog, 'backlog')):
        detail = quick_fix_detail(item, date)
        if detail is None:
            continue
        title, section = item_title(item), item_section(item)
        head = closed_item_head(title, section)
        if not any(line.startswith(head) for line in listed):
            closed.append(closed_item_line(title, section, detail))
    if not closed:
        return ''
    return '\n'.join([f'{DEFERRED_HEADING}{date}', '', 'Closed deferred items:', *closed])


def _iso_date(raw: str) -> str:
    try:
        if ISO_DATE_RE.fullmatch(raw):
            return dt.date.fromisoformat(raw).isoformat()
    except ValueError:
        pass
    raise argparse.ArgumentTypeError(f'{raw!r} is not a date in the form YYYY-MM-DD')


def _add_date_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '--date', type=_iso_date, default=dt.date.today().isoformat(),
        help='the entry date, YYYY-MM-DD (default: today)',
    )


def _run_draft(args: argparse.Namespace) -> str:
    return draft_entry(DraftInputs(args.plan, args.ledger, args.spec, args.spec_status, args.date))


def _run_deferred(args: argparse.Namespace) -> str:
    return deferred_entry(args.date)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PROG, description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest='command', required=True)
    draft = commands.add_parser('draft', help='print the draft entry for a retired plan')
    draft.add_argument('plan', type=Path, help='the retired plan file, under a specs directory')
    draft.add_argument('--ledger', type=Path, help="the plan's run ledger")
    draft.add_argument('--spec', help="the spec's path, printed as given; needs --spec-status")
    draft.add_argument('--spec-status', choices=SPEC_STATUSES, help='whether the spec retired or stays live')
    _add_date_option(draft)
    draft.set_defaults(run=_run_draft)
    deferred = commands.add_parser(
        'deferred', help="print the draft entry for a /deferred pass's quick fixes",
    )
    _add_date_option(deferred)
    deferred.set_defaults(run=_run_deferred)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run: Callable[[argparse.Namespace], str] = args.run
    try:
        output = run(args)
    except InputError as error:
        print(f'{PROG}: error: {error}', file=sys.stderr)
        return EXIT_BAD_INPUT
    if output:
        print(output)
    return 0


if __name__ == '__main__':
    sys.exit(main())

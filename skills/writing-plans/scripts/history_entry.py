#!/usr/bin/env python3
# /// script
# requires-python = '>=3.11'
# dependencies = []
# ///
'''Draft an entry for specs/history.md from a retired plan, its run ledger and the backlog.

The `draft` subcommand prints the draft entry for one retired plan. The agent that
retires the plan finishes the draft and appends it to `specs/history.md`. The
script never writes a file.

The draft lists every ledger ruling. It also lists the plan's deviation notes and
its decisions that carry `(spec amendment)`, the count of items the plan deferred,
and the earlier deferred items that the plan closed. The agent removes the
rulings that did not change the build (spec D7).

A form inside a fenced block or an inline code span is quoted text, so it is never
read. The plan's header lines come from above its first `## ` heading.

Usage:
    uv run <this-skill-dir>/scripts/history_entry.py draft <plan> \\
        [--ledger <path>] [--spec <path> --spec-status retired|live] [--date YYYY-MM-DD]

Exit 0 with a draft. Exit 2 with a one-line error on stderr when an input is bad,
for example a plan file that is missing or is not a plan.
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
SPEC_STATUSES = ('retired', 'live')
NO_SPEC = 'none'
STATUS_NOT_GIVEN = 'status not given'
ROADMAP_END = ' — '
SPEC_AMENDMENT = '(spec amendment)'
APPLIED_IN = ' Applied in:'
DECISION_CLOSE = '): '
RULING_MARK = 'Ruling:'
DECISIONS_SOURCE = '`## Decisions`'

H2_RE = re.compile(r'^##\s')
TASK_RE = re.compile(r'^###\s+Task\s+(?P<number>\d+)')
SPEC_LINE_RE = re.compile(r'^\*\*Spec:\*\*')
NO_SPEC_RE = re.compile(rf'{NO_SPEC}\b')
SPEC_PATH_RE = re.compile(r'specs/[\w./-]+\.md(?!\w)')
ROADMAP_LINE_RE = re.compile(r'^\s*>\s*Roadmap:')
DEVIATION_RE = re.compile(r'^\s*>\s*(\*\*)?Deviation\b[^:]*:(?:\*\*)?')
BLOCKQUOTE_RE = re.compile(r'^\s*>')
BLOCKQUOTE_PREFIX_RE = re.compile(r'^\s*>\s*')
BARE_BLOCKQUOTE_RE = re.compile(r'^\s*>\s*$')
DECISION_RE = re.compile(r'^- \*\*(?P<id>D\d+)\*\*')
LEDGER_TASK_RE = re.compile(r'^\s*Task\s+(?P<number>\d+)')
LEDGER_FINAL_RE = re.compile(r'^\s*Final\b')
PLAN_ID_RE = re.compile(r'(?P<id>\d+)-')
ISO_DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')


class InputError(Exception):
    '''A bad input. `main` prints the message as one line on stderr and exits 2.'''


@dataclass(frozen=True)
class PlanText:
    '''A plan's lines, and the same lines with fenced blocks and code spans blanked.

    A match is decided on `masked`, so a form quoted in code never matches. The
    printed text comes from `lines`.
    '''

    lines: list[str]
    masked: list[str]


def read_plan_text(text: str) -> PlanText:
    return PlanText(text.split('\n'), blank_code(text).split('\n'))


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
    single spaces and one trailing `.` is removed.
    '''
    parts = [plan.lines[index][note.end():].strip()]
    for original, masked in zip(plan.lines[index + 1:], plan.masked[index + 1:]):
        if (not BLOCKQUOTE_RE.match(masked) or BARE_BLOCKQUOTE_RE.match(original)
                or DEVIATION_RE.match(masked)):
            break
        parts.append(BLOCKQUOTE_PREFIX_RE.sub('', original, count=1).strip())
    return ' '.join(part for part in parts if part).removesuffix('.')


def deviation_lines(plan: PlanText) -> list[str]:
    '''One difference line per deviation note, in plan order.

    A note above the first `### Task` heading is the plan header's.
    '''
    found = []
    task = None
    for index, masked in enumerate(plan.masked):
        heading = TASK_RE.match(masked)
        if heading:
            task = heading.group('number')
            continue
        note = DEVIATION_RE.match(masked)
        if note:
            text = _deviation_text(plan, index, note)
            label = f' (Task {task})' if task else ''
            where = f'Task {task}' if task else 'header'
            found.append(f'- Deviation{label}: {text}. Source: plan, {where}.')
    return found


def _is_continuation(line: str) -> bool:
    return line[:1].isspace() and bool(line.strip())


def _spec_decision_line(number: str, joined: str) -> str | None:
    '''The difference line for a decision whose `Applied in:` part has `(spec amendment)`.'''
    head, found, applied = joined.rpartition(APPLIED_IN)
    close = head.find(DECISION_CLOSE)
    if not found or SPEC_AMENDMENT not in applied or close == -1:
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
        index += 1
        while index < len(plan.lines) and _is_continuation(plan.lines[index]):
            parts.append(plan.lines[index].strip())
            index += 1
        line = _spec_decision_line(start.group('id'), ' '.join(parts))
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


def closed_item_line(title: str, section: str, detail: str = '') -> str:
    '''`- "<title>" (deferred by <section>)`, closed by a period or by `: <detail>`.'''
    head = f'- "{title}" (deferred by {section})'
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

    lines = [f'## {stem} — {inputs.date}', ' · '.join(first), *warnings, '']
    if differences:
        lines += ['Differences from the design:', *differences]
    else:
        lines.append('No differences from the design.')
    if closed:
        lines += ['', 'Closed earlier deferred items:', *closed]
    return '\n'.join(lines)


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

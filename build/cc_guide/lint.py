'''`lint`: the offline gate over the guide, manifest.toml and baseline.json
(drift spec R5). Its citation rules and STALE lines are Stage 2's.'''
import json
import re

from blocks import CELL_SPLIT_RE, fence_spans, fenced_lines
from guide import STAMP_CLOSE, STAMP_OPEN, anchor_problems, render_stamp, sections, stamp_bounds, text_hash
from state import Manifest

CLI = 'uv run --python 3.13 python build/cc_guide/cli.py'
# A 2.1.NNN version, not inside a longer number; a trailing period is prose.
VERSION_RE = re.compile(r'(?<![\d.])2\.1\.\d+(?:\.\d+)*(?!\d)')


def cell_count(row: str) -> int:
    '''Cells in a table row, split on unescaped pipes, outer pipes dropped.'''
    s = row.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|') and not s.endswith('\\|'):
        s = s[:-1]
    return len(CELL_SPLIT_RE.split(s))


def id_set_problems(guide_text: str, manifest: Manifest, state: dict) -> list[str]:
    '''The anchors, the manifest's groups and baseline.json's sections carry
    one ID set (R5). The manifest's own parse already holds each ID to one
    group.'''
    where = {'the guide': {s.id for s in sections(guide_text) if s.id},
             'manifest.toml': set(manifest.group_of()),
             'baseline.json': set(state['sections'])}
    out = []
    for sid in sorted(set().union(*where.values())):
        missing = [name for name, ids in where.items() if sid not in ids]
        if missing:
            out.append(f'section {sid}: missing from {" and ".join(missing)}')
    return out


def hash_problems(guide_text: str, state: dict) -> list[str]:
    '''Each section's text matches its text_hash (R5); a mismatch names the
    two `baseline accept` outcomes (R2.4).'''
    out = []
    for s in sections(guide_text):
        recorded = state['sections'].get(s.id, {}).get('text_hash')
        if recorded and text_hash(s.text) != recorded:
            out.append(f'section {s.id}: text differs from its text_hash; record it with '
                       f'`{CLI} baseline accept {s.id} --substantive` (flags its citers) '
                       f'or `... --editorial`')
    return out


def stamp_problems(guide_text: str, state: dict) -> list[str]:
    '''The stamp region sits before the first section and matches
    baseline.json (R1.2, R5).'''
    bounds = stamp_bounds(guide_text)
    if bounds is None:
        return [f'guide: needs one stamp region, a {STAMP_OPEN} line then a {STAMP_CLOSE} line']
    first = min((s.line for s in sections(guide_text)), default=None)
    if first is not None and bounds[1] + 1 >= first:
        return ['guide: the stamp region must sit before the first section']
    content = '\n'.join(guide_text.split('\n')[bounds[0] + 1:bounds[1]])
    if content != render_stamp(state['sections']):
        return [f'guide: the stamp region does not match baseline.json; run `{CLI} baseline stamp`']
    return []


def quality_problems(guide_text: str, labels: set[str] | None) -> tuple[list[str], list[str]]:
    '''R5's guide-quality checks: every 2.1.NNN is a changelog release label
    (skipped with a note when there is no changelog to read), every table
    keeps its header's column count, and every json code block parses.'''
    out, notes = [], []
    lines = guide_text.split('\n')
    if labels is None:
        notes.append('release-label check skipped: no changelog to read')
    else:
        for n, line in enumerate(lines, start=1):
            out += [f'guide line {n}: {v} is not a changelog release label'
                    for v in VERSION_RE.findall(line) if v not in labels]
    fenced = fenced_lines(lines)
    i = 0
    while i < len(lines):
        if i in fenced or not lines[i].lstrip().startswith('|'):
            i += 1
            continue
        header = cell_count(lines[i])
        while i < len(lines) and i not in fenced and lines[i].lstrip().startswith('|'):
            if cell_count(lines[i]) != header:
                out.append(f'guide line {i + 1}: table row has {cell_count(lines[i])} cells; '
                           f'its header has {header}')
            i += 1
    for start, close, info in fence_spans(lines):
        if info.split()[:1] == ['json']:
            body = '\n'.join(lines[start + 1:len(lines) if close is None else close])
            try:
                json.loads(body)
            except json.JSONDecodeError as exc:
                out.append(f'guide line {start + 1}: json block does not parse ({exc.msg})')
    return out, notes


def lint(guide_text: str, manifest: Manifest, state: dict,
         labels: set[str] | None) -> tuple[list[str], list[str]]:
    '''R5 without its citation rules: (violations, notes). `labels` are the
    newest changelog's release labels; the caller parses the changelog, so a
    malformed one is a setup error there.'''
    quality, notes = quality_problems(guide_text, labels)
    violations = (anchor_problems(guide_text) + id_set_problems(guide_text, manifest, state)
                  + hash_problems(guide_text, state) + stamp_problems(guide_text, state) + quality)
    return violations, notes

'''`lint`: the offline gate over the guide, manifest.toml, baseline.json and
the citations that point at the guide (drift spec R5).'''
import json
import re

from blocks import CELL_SPLIT_RE, fence_spans, fenced_lines, is_table_start
from docs import version_key
from guide import (NO_STAMP, Citation, anchor_problems, file_citation, render_stamp, sections, stamp_bounds,
                   stamp_content, text_hash)
from state import Manifest

CLI = 'uv run --python 3.13 python build/cc_guide/cli.py'
# A 2.1.NNN version, not inside a longer number; a trailing period is prose.
VERSION_RE = re.compile(r'(?<![\d.])2\.1\.\d+(?:\.\d+)*(?!\d)')
NO_CHANGELOG = 'release-label check skipped: no changelog to read'


def cell_count(row: str) -> int:
    '''Cells in a table row, split on unescaped pipes, outer pipes dropped.
    An escaped final pipe is no split point, so dropping it changes nothing.'''
    s = row.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
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
        missing = ' and '.join(name for name, ids in where.items() if sid not in ids)
        if missing:
            out.append(f'section {sid}: missing from {missing}')
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
                       f'or `{CLI} baseline accept {s.id} --editorial`')
    return out


def stamp_problems(guide_text: str, state: dict) -> list[str]:
    '''The stamp region sits before the first section and matches
    baseline.json (R1.2, R5).'''
    bounds = stamp_bounds(guide_text)
    if bounds is None:
        return [f'guide: {NO_STAMP}']
    first = min((s.line for s in sections(guide_text)), default=None)
    if first is not None and bounds[1] + 1 >= first:
        return ['guide: the stamp region must sit before the first section']
    if stamp_content(guide_text) != render_stamp(state['sections']):
        return [f'guide: the stamp region does not match baseline.json; run `{CLI} baseline stamp`']
    return []


def label_problems(lines: list[str], labels: set[str]) -> list[str]:
    '''Every 2.1.NNN in the guide is a changelog release label (R5).'''
    return [f'guide line {n}: {v} is not a changelog release label'
            for n, line in enumerate(lines, start=1) for v in VERSION_RE.findall(line) if v not in labels]


def table_problems(lines: list[str]) -> list[str]:
    '''Every table row keeps its header's cell count (R5). A table starts at
    a | line followed by a separator row (plan 38, decision 12).'''
    fenced = fenced_lines(lines)
    out = []
    i = 0
    while i < len(lines):
        if i in fenced or not is_table_start(lines, i, fenced):
            i += 1
            continue
        header = cell_count(lines[i])
        while i < len(lines) and i not in fenced and lines[i].lstrip().startswith('|'):
            if cell_count(lines[i]) != header:
                out.append(f'guide line {i + 1}: table row has {cell_count(lines[i])} cells; '
                           f'its header has {header}')
            i += 1
    return out


def json_problems(lines: list[str]) -> list[str]:
    '''Every json code block parses (R5); an unclosed one runs to the end.'''
    out = []
    for start, close, info in fence_spans(lines):
        if info.split()[:1] == ['json']:
            try:
                json.loads('\n'.join(lines[start + 1:len(lines) if close is None else close]))
            except json.JSONDecodeError as exc:
                out.append(f'guide line {start + 1}: json block does not parse ({exc.msg})')
    return out


def citation_problems(guide_text: str, files: dict[str, str]) -> list[str]:
    '''R5's citation rules over the files the scan found: each citation
    parses, cites guide sections, sits where R4.1 puts it, and appears once
    per file. In path order, each file's problems together.'''
    ids = {s.id for s in sections(guide_text) if s.id}
    out = []
    for path in sorted(files):
        citation, problems = file_citation(path, files[path])
        out += problems
        if citation is not None:
            out += [f'{path}:{citation.line}: cites {sid}, which is not a guide section'
                    for sid in citation.ids if sid not in ids]
    return out


def stale_citations(citations: list[Citation], state: dict) -> list[tuple[str, list[str]]]:
    '''R5: each citing file whose stamp is below a cited section's
    `changed`, with those sections. A section baseline.json lacks is a lint
    violation, never stale.'''
    out = []
    for c in citations:
        behind = [sid for sid in c.ids if sid in state['sections']
                  and version_key(c.stamp) < version_key(state['sections'][sid]['changed'])]
        if behind:
            out.append((c.path, behind))
    return out


def stale_lines(citations: list[Citation], state: dict) -> list[str]:
    '''R5's `STALE <file> <ids>` lines, which never change the exit code.'''
    return [f"STALE {path} {' '.join(ids)}" for path, ids in stale_citations(citations, state)]


def stale_by_section(citations: list[Citation], state: dict) -> dict[str, list[str]]:
    '''R6.8's stale backlog: each section's stale citing files, sections in
    baseline.json's (the guide's) order.'''
    by: dict[str, list[str]] = {}
    for path, ids in stale_citations(citations, state):
        for sid in ids:
            by.setdefault(sid, []).append(path)
    return {sid: by[sid] for sid in state['sections'] if sid in by}


def lint(guide_text: str, manifest: Manifest, state: dict, labels: set[str] | None,
         files: dict[str, str]) -> tuple[list[str], list[str]]:
    '''R5: (violations, notes). `labels` are the newest changelog's release
    labels, None when there is no changelog to read, which skips the label
    check with a note; the caller parses the changelog, so a malformed one is
    a setup error there. `files` are the citation scan's, path -> text
    (state.citing_files). Stale citations are not violations: callers print
    them (stale_lines) or report them (stale_by_section).'''
    lines = guide_text.split('\n')
    violations = (anchor_problems(guide_text) + id_set_problems(guide_text, manifest, state)
                  + hash_problems(guide_text, state) + stamp_problems(guide_text, state)
                  + (label_problems(lines, labels) if labels is not None else [])
                  + table_problems(lines) + json_problems(lines) + citation_problems(guide_text, files))
    return violations, [NO_CHANGELOG] if labels is None else []

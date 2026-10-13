'''`packets`: the files /cc-guide hands its verifier (drift spec R6.11, R8.2).

A packet is a directory. Its index.json names the mode, the items the
verifier answers for and where each kind of quote is checked; `settle`
reads it back beside the verifier's report.md. Its Markdown files hold what
the verifier reads. The guide is copied whole, so a line number in a packet
is a line number in the guide. Packets hold docs text, so they live under
the cache, never in a checkout.

The inputs are check --worktree's: the working tree, and the docs and
snapshots check left in the cache. Packets never fetch: run check first.
'''
import difflib
import json
import re
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import NamedTuple

from blocks import page_blocks
from check import Docs, Finding, compare, offline_docs, release_notes, releases_of, untriaged
from docs import CHANGELOG, Release, page_file, version_key
from guide import read_citations, sections
from lint import stale_citations
from state import (BASELINE, MANIFEST, Manifest, SetupError, Source, baselined_text, citing_files, copy_to_snapshot,
                   group_terms, latest_docs, parse_baseline, parse_manifest, read_fetch, snapshot_text)

INDEX = 'index.json'
REPORT = 'report.md'
SETTLED = 'settled.json'
GUIDE = 'guide.md'
BLOCKS = 'blocks.md'
RELEASES = 'releases.md'
SECTIONS = 'sections.md'
BLOCK_KINDS = ('changed', 'missing', 'new')
RANGE = 20  # the untriaged releases one triage packet takes, when more are untriaged
BACKTICK_RUN_RE = re.compile(r'`+')


class World(NamedTuple):
    '''One run's inputs, read once.'''
    source: Source
    cache: Path
    manifest: Manifest
    state: dict
    guide: str
    terms: dict
    docs: Docs
    releases: list[Release]
    findings: list[Finding]
    head: str  # the latest fetch's changelog head
    now: datetime


def load(source: Source, cache: Path, now: datetime) -> World:
    '''check --worktree's inputs, with the docs read offline from latest/.'''
    manifest = parse_manifest(source.require(MANIFEST))
    state = parse_baseline(source.require(BASELINE))
    guide = source.require(manifest.guide)
    record = read_fetch(cache)
    if record is None:
        raise SetupError('no latest fetch: run check --worktree first')
    docs = offline_docs(manifest, latest_docs(cache))
    terms = group_terms(manifest, guide)
    findings, _ = compare(manifest, state, terms, docs, partial(snapshot_text, cache))
    releases = releases_of(docs.changelog, str(latest_docs(cache) / CHANGELOG))
    return World(source, cache, manifest, state, guide, terms, docs, releases, findings, record['changelog_head'], now)


def section_lines(guide_text: str) -> dict[str, tuple[int, int]]:
    '''Each anchored section's 1-based heading line and last line.'''
    found = sections(guide_text)
    ends = [s.line - 1 for s in found[1:]] + [len(guide_text.split('\n'))]
    return {s.id: (s.line, end) for s, end in zip(found, ends) if s.id}


def fenced(text: str) -> list[str]:
    '''text inside a backtick fence longer than any backtick run it holds.'''
    longest = max((len(m.group()) for m in BACKTICK_RUN_RE.finditer(text)), default=0)
    fence = '`' * max(3, longest + 1)
    return [fence, *text.split('\n'), fence]


def checkout_of(path: Path) -> Path | None:
    '''The checkout holding path: the nearest folder, path itself included,
    with a `.git`, a directory or a linked worktree's file.'''
    return next((p for p in (path, *path.parents) if (p / '.git').exists()), None)


def new_dir(out: Path, repo: Path) -> Path:
    '''An empty directory for a run, outside every checkout (spec Decision
    10), since packets hold docs text: the repo's, the main checkout a
    worktree sits in, and any other. An existing one must be empty, so a
    report from an earlier run is never settled against a new packet.'''
    where = out.resolve()
    inside = checkout_of(where) or (repo.resolve() if where.is_relative_to(repo.resolve()) else None)
    if inside is not None:
        raise SetupError(f'{out}: inside the checkout {inside}; packets hold docs text, so they live outside '
                         'every checkout')
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise SetupError(f'{out}: not an empty directory; packets never write over an earlier packet')
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_packet(world: World, out: Path, index: dict, files: dict[str, str | list[str]]) -> Path:
    new_dir(out, world.source.repo)
    for name, body in files.items():
        (out / name).write_text(body if isinstance(body, str) else '\n'.join(body) + '\n', encoding='utf-8')
    (out / INDEX).write_text(json.dumps(index, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    return out


def header(world: World, mode: str) -> dict:
    return {'mode': mode, 'inputs': world.source.label, 'generated_at': world.now.isoformat(timespec='seconds'),
            'head': world.head}


def page_holds(world: World) -> set[str]:
    '''The sections a missing page holds: it needs a manifest.toml edit.'''
    return {sid for f in world.findings if f.kind == 'missing-page' for sid in f.candidates}


def block_item(world: World, item: str, f: Finding) -> tuple[dict, list[str]]:
    '''One block finding's index entry and its blocks.md lines: its current
    text, and its baselined text read from the page's snapshot by key hash,
    as a diff for a changed block and whole for a missing one. The entry's
    `lines` are the item's lines that hold that text, the only ones its
    source quote may come from.'''
    text = world.docs.pages.get(f.page)
    now = None if text is None or f.kind == 'missing' else page_blocks(text).get(f.key)
    then = None if f.kind == 'new' else baselined_text(world.state, f.group, partial(snapshot_text, world.cache))(
        f.page, f.key_hash)
    release = world.state['groups'].get(f.group, {}).get('snapshot', {}).get(f.page)
    lines = [f'## {item} · {f.kind} · [{f.group}] {f.ref()}', '',
             f"Candidate sections: {', '.join(f.candidates)}", '']
    spans: list[list[int]] = []

    def show(label: str, body: str) -> None:
        lines.append(label)
        block = fenced(body)
        spans.append([len(lines) + 2, len(lines) + len(block) - 1])  # inside the fence
        lines.extend([*block, ''])

    if now is not None:
        show('Current text:', now)
    if f.kind == 'changed' and then is not None and now is not None:
        diff = difflib.unified_diff(then.split('\n'), now.split('\n'), f'the {release} snapshot', 'now', lineterm='')
        show(f'Diff against the {release} snapshot:', '\n'.join(diff))
    elif f.kind == 'missing' and then is not None:
        show(f'Baselined text, from the {release} snapshot (the block has left the page):', then)
    elif f.kind != 'new':
        lines += ['No cached snapshot holds its baselined text.', '']
    entry = {'item': item, 'group': f.group, 'kind': f.kind, 'ref': f.ref(), 'page': f.page,
             'key_hash': f.key_hash, 'candidates': f.candidates, 'lines': spans}
    return entry, lines


def block_items(world: World, found: list[Finding]) -> tuple[list[dict], list[str]]:
    '''The index entries and blocks.md for block findings, numbered B1, B2,
    ..., each entry's `lines` counted in blocks.md.'''
    entries, lines = [], ['# Block findings', '']
    for n, f in enumerate(found, start=1):
        entry, body = block_item(world, f'B{n}', f)
        entry['lines'] = [[first + len(lines), last + len(lines)] for first, last in entry['lines']]
        entries.append(entry)
        lines += body
    return entries, lines + ([] if found else ['None.', ''])


def release_items(world: World, labels: list[str], pending: dict[str, list[str]]) -> tuple[list[dict], list[str]]:
    '''The index entries and releases.md for untriaged releases: every bullet,
    numbered <release>#1, #2, ..., with the sections whose terms it contains
    as hints only (R6.6). Hints and hits name only the sections the release
    is untriaged for.'''
    notes = release_notes(world.releases, set(labels), world.terms)
    entries, lines = [], ['# Untriaged releases', '']
    for label in labels:
        mine = [sid for sid, ls in pending.items() if label in ls]
        bullets = [{'item': f'{label}#{n}', 'hints': [h for h in b['hints'] if h in mine], 'text': b['text']}
                   for n, b in enumerate(notes[label]['bullets'], start=1)]
        hits = [sid for sid in mine if any(sid in b['hints'] for b in bullets)]
        entries.append({'label': label, 'date': notes[label]['date'], 'pending': mine, 'hits': hits,
                        'bullets': bullets})
        lines += [f"## {label} · {notes[label]['date']}", '',
                  f"Untriaged for {len(mine)} section(s); term hits, as hints only: {', '.join(hits) or 'none'}.", '']
        lines += [f"- {b['item']} · hints: {', '.join(b['hints']) or 'none'} · {b['text']}" for b in bullets] + ['']
    return entries, lines + ([] if labels else ['None.', ''])


def triage(world: World, out: Path, through: str | None, size: int = RANGE) -> Path | None:
    '''R8.4 step 1's packet: the guide, each changed, missing or new block,
    and every bullet of each untriaged release. With `through`, only the
    untriaged releases up to that one. A range counts the releases after the
    newest one any section is checked through, so a section deferred in an
    earlier range shows its earlier releases without their counting. More
    than `size` of them need `through`: the error names the first range's,
    and each range's index names the next one's, the size-th untriaged
    release after its own.
    Block findings belong to no release, so they ride in every range, the
    oldest first, and are settled there against the current docs. A missing
    page needs a manifest edit, so it is an owner item whose sections are
    held. None when nothing is due.'''
    pending = untriaged(world.state, world.releases)
    every = sorted({label for ls in pending.values() for label in ls}, key=version_key)
    if through is not None and through not in every:
        raise SetupError(f"--through {through}: not an untriaged release ({', '.join(every) or 'none'})")
    checked = max((s['checked']['release'] for s in world.state['sections'].values()), key=version_key)
    fresh = [label for label in every if version_key(label) > version_key(checked)]
    if through is None and len(fresh) > size:
        raise SetupError(f'{len(fresh)} untriaged releases after {checked}: take them in ranges of {size}, the '
                         f'first with --through {fresh[size - 1]}, or all at once with --through {every[-1]}')
    labels = every[:every.index(through) + 1] if through is not None else every
    after = every[len(labels):]
    pages = [f for f in world.findings if f.kind == 'missing-page']
    found = [f for f in world.findings if f.kind in BLOCK_KINDS]
    held = page_holds(world)
    if not labels and not found and not pages:
        return None
    rel_entries, rel_lines = release_items(world, labels, pending)
    block_entries, block_lines = block_items(world, found)
    order = list(world.state['sections'])
    index = header(world, 'triage') | {
        'newest': labels[-1] if labels else None,
        'next_through': after[min(size, len(after)) - 1] if after else None,
        'quotes': {'guide': [GUIDE], 'source': [BLOCKS, RELEASES]},
        'groups': {gid: g.sections for gid, g in world.manifest.groups.items()},
        'blocks': block_entries,
        'releases': rel_entries,
        'held': sorted(held, key=order.index),
        'owner': [f'missing page {f.page} in group {f.group}: drop or remap it in manifest.toml' for f in pages],
    }
    return write_packet(world, out, index, {GUIDE: world.guide, BLOCKS: block_lines, RELEASES: rel_lines})


def group_docs(world: World, groups: list[str]) -> Path:
    '''R8.5's snapshot: the groups' cached pages copied from latest/ to the
    head release's snapshot, which the verifier greps.'''
    names = {page: page_file(page) for gid in groups for page in world.manifest.groups[gid].pages
             if (latest_docs(world.cache) / page_file(page)).is_file()}
    return copy_to_snapshot(world.cache, world.head, names)


def section_list(world: World, sids: list[str], notes: dict[str, list[str]]) -> tuple[dict, list[str]]:
    '''Each section's guide lines, then its notes: (sid -> [first, last],
    the sections.md lines).'''
    lines = section_lines(world.guide)
    out = ['# Sections', '']
    for sid in sids:
        out += [f'## {sid} · guide lines {lines[sid][0]}-{lines[sid][1]}', '', *notes.get(sid, []), '']
    return {sid: list(lines[sid]) for sid in sids}, out


def triage_notes(triaged: dict, sid: str) -> list[str]:
    '''The settled triage rows that sent a section to verify.'''
    rows = triaged.get('rows', {}).get(sid)
    return ['Triage rows that sent it here:', *(f'- {r}' for r in rows)] if rows else ['No triage row sent it here.']


def known_sections(world: World, ids: list[str]) -> None:
    unknown = [sid for sid in dict.fromkeys(ids) if sid not in world.state['sections']]
    if unknown:
        raise SetupError(f"unknown section IDs: {', '.join(unknown)}")


def verify(world: World, out: Path, ids: list[str], settled: Path | None) -> list[Path]:
    '''R8.5's packets, one per group of the named sections: the guide, the
    sections' lines with the triage rows that sent them here, every block
    finding of the group, the changelog, and the group's pages copied to the
    head release's snapshot. From a settled triage, `advance_to`, `cleared`
    and `held` carry over for settle's bookkeeping, and no IDs means the
    sections it sent on. `checked` names each section's checked release, so
    settle never advances one backwards.'''
    if settled and not settled.is_file():
        raise SetupError(f'{settled}: not found; run settle on the triage packet first')
    triaged = json.loads(settled.read_text(encoding='utf-8')) if settled else {}
    if settled and triaged.get('mode') != 'triage':
        raise SetupError(f'{settled}: not a settled triage')
    if not ids and not settled:
        raise SetupError('--verify needs section IDs, or --from a settled triage')
    ids = list(ids) or triaged.get('verify', [])
    if not ids:
        raise SetupError(f'{settled}: its triage sent no section to verify')
    known_sections(world, ids)
    holds = page_holds(world) | set(triaged.get('held', []))
    owner = world.manifest.group_of()
    groups = [gid for gid in world.manifest.groups if any(owner[sid] == gid for sid in ids)]
    docs = group_docs(world, groups)
    new_dir(out, world.source.repo)
    made = []
    for gid in groups:
        sids = [sid for sid in world.manifest.groups[gid].sections if sid in ids]
        found = [f for f in world.findings if f.group == gid and f.kind in BLOCK_KINDS]
        entries, block_lines = block_items(world, found)
        lines, section_md = section_list(world, sids, {sid: triage_notes(triaged, sid) for sid in sids})
        index = header(world, 'verify') | {
            'group': gid, 'sections': sids, 'lines': lines,
            'checked': {sid: world.state['sections'][sid]['checked']['release'] for sid in sids}, 'docs': str(docs),
            'advance_to': triaged.get('advance_to'), 'cleared': triaged.get('cleared', []),
            'held': [sid for sid in world.manifest.groups[gid].sections if sid in holds],
            'quotes': {'guide': [GUIDE], 'changelog': [CHANGELOG], 'docs': [str(docs)]}, 'blocks': entries,
        }
        made.append(write_packet(world, out / gid, index, {GUIDE: world.guide, SECTIONS: section_md,
                                                           BLOCKS: block_lines, CHANGELOG: world.docs.changelog}))
    return made


def audit(world: World, out: Path, group: str) -> Path:
    '''R8.6's packet: every section of the group, all its pages copied to the
    head release's snapshot, every bullet of each release untriaged for its
    sections, the changelog, and the group's block findings.'''
    if group not in world.manifest.groups:
        raise SetupError(f'unknown group {group}')
    sids = world.manifest.groups[group].sections
    docs = group_docs(world, [group])
    pending = {sid: ls for sid, ls in untriaged(world.state, world.releases).items() if sid in sids}
    labels = sorted({label for ls in pending.values() for label in ls}, key=version_key)
    rel_entries, rel_lines = release_items(world, labels, pending)
    entries, block_lines = block_items(world, [f for f in world.findings if f.group == group and f.kind in BLOCK_KINDS])
    lines, section_md = section_list(world, sids, {})
    index = header(world, 'audit') | {
        'group': group, 'sections': sids, 'lines': lines, 'docs': str(docs), 'releases': rel_entries,
        'held': [sid for sid in sids if sid in page_holds(world)],
        'quotes': {'guide': [GUIDE], 'changelog': [CHANGELOG], 'docs': [str(docs)]}, 'blocks': entries,
    }
    return write_packet(world, out, index, {GUIDE: world.guide, SECTIONS: section_md, BLOCKS: block_lines,
                                            RELEASES: rel_lines, CHANGELOG: world.docs.changelog})


def files(world: World, out: Path, paths: list[str]) -> list[Path]:
    '''R8.7's packets, one per file: a copy of the file, the guide, and its
    cited sections' lines and text, each marked when it changed after the
    file's stamp. No paths: the stale backlog. A path must be a citing file
    the lint reads.'''
    citations, _ = read_citations(citing_files(world.source, world.manifest.guide))
    by_path = {c.path: c for c in citations}
    targets = list(dict.fromkeys(paths)) or [path for path, _ in stale_citations(citations, world.state)]
    unread = [path for path in targets if path not in by_path]
    if unread:
        raise SetupError(f"not a citing file the lint reads: {', '.join(unread)}")
    if not targets:
        raise SetupError('no stale citation: name the files to review')
    texts = {s.id: s.text for s in sections(world.guide) if s.id}
    new_dir(out, world.source.repo)
    made = []
    for path in targets:
        c = by_path[path]
        changed = [sid for sid in c.ids if version_key(world.state['sections'][sid]['changed']) > version_key(c.stamp)]
        marks = {sid: [f"Changed after @{c.stamp}: now @{world.state['sections'][sid]['changed']}." if sid in changed
                       else f'Unchanged since @{c.stamp}.', '', *fenced(texts[sid])] for sid in c.ids}
        lines, section_md = section_list(world, list(c.ids), marks)
        copy = 'cited_' + path.rsplit('/', 1)[-1]
        index = header(world, 'files') | {
            'file': path, 'copy': copy, 'stamp': c.stamp, 'sections': list(c.ids), 'lines': lines,
            'changed': changed, 'quotes': {'guide': [GUIDE]},
        }
        made.append(write_packet(world, out / path.replace('/', '__'), index,
                                 {GUIDE: world.guide, SECTIONS: section_md, copy: world.source.require(path)}))
    return made

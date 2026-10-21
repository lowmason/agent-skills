'''The detector's inputs and cache layout: manifest.toml (owner
configuration), baseline.json (tool state) and PROBES.md, read from the
working tree or a commit (drift spec R2, R6.1, Layout).'''
import fnmatch
import json
import re
import subprocess
import tomllib
from datetime import date
from pathlib import Path
from typing import Callable, NamedTuple

from blocks import CELL_SPLIT_RE, HASH_RE, key_hash, page_blocks
from docs import page_file, version_key
from guide import ID_RE, TEXT_HASH_RE, section_terms, sections

MANIFEST = 'build/cc_guide/manifest.toml'
BASELINE = 'build/cc_guide/baseline.json'
PROBES = 'build/cc_guide/PROBES.md'
# R4.2's excluded trees, which the citation scan never reads.
UNCITED = ('specs', 'runtimes', 'review')
# guide.CITE_SHAPED_RE, spelled for `git grep -E`.
CITE_SHAPED_ERE = '^[[:blank:]]*(#|<!--)[[:blank:]]*cc-guide:'
MARKS = ('all', 'terms')
SOURCE_KEYS = ('docs_base', 'llms', 'changelog', 'platform_base')
CADENCE_KEYS = ('changelog_days', 'probe_days', 'audit_days')
TABLES = ('guide', 'sources', 'cadence', 'groups', 'sections', 'exclusion', 'probe')
GROUP_RE = re.compile(r'[a-z0-9-]+')
DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
# R10.5's outcomes, and the columns that mark PROBES.md's log table (R10.6).
PASS, DIVERGES, ERROR = 'PASS', 'DIVERGES', 'ERROR'
OUTCOMES = (PASS, DIVERGES, ERROR)
PROBE_COLUMNS = frozenset({'date', 'version', 'probe', 'outcome'})

# The bootstrap snapshot (R2.6): the 2026-10-03 refresh read the docs at
# 2.1.288 and checked them that day. 2.1.288 itself shipped on 2026-10-02.
BOOTSTRAP_RELEASE = '2.1.288'
BOOTSTRAP_DATE = '2026-10-03'


class SetupError(Exception):
    '''A missing or invalid input: exit 2, so a broken setup never looks clean.'''


class Source:
    '''Reads repo files from the working tree (ref None) or from a commit
    through `git cat-file` (R6.1).'''

    def __init__(self, repo: Path, ref: str | None = None):
        self.repo, self.ref = repo, ref
        if ref is not None:
            ok = subprocess.run(['git', 'rev-parse', '--verify', '--quiet', f'{ref}^{{commit}}'],
                                cwd=repo, capture_output=True).returncode == 0
            if not ok:
                raise SetupError(f'{ref}: not a commit in {repo}')

    @property
    def label(self) -> str:
        return 'the working tree' if self.ref is None else self.ref

    def read(self, path: str) -> str | None:
        '''The file's text, or None when no file is there; a directory is no
        file. A file that is not UTF-8 is a SetupError naming it.'''
        if self.ref is None:
            p = self.repo / path
            return read_utf8(p) if p.is_file() else None
        proc = subprocess.run(['git', 'cat-file', 'blob', f'{self.ref}:{path}'], cwd=self.repo,
                              capture_output=True)
        if proc.returncode != 0:
            return None
        try:
            return proc.stdout.decode('utf-8')
        except UnicodeDecodeError as exc:
            raise SetupError(f'{self.ref}:{path}: not UTF-8 text ({exc.reason} at byte {exc.start})') from None

    def require(self, path: str) -> str:
        text = self.read(path)
        if text is None:
            raise SetupError(f'{path}: not found in {self.label}')
        return text

    def grep(self, pattern: str, exclude: tuple[str, ...]) -> list[str]:
        '''The tracked files outside the excluded paths holding a line that
        matches the extended regex pattern, read where this source reads
        (R6.1). Binary files are skipped, and git's color settings never
        wrap a name in escapes. A git failure, or a file name that is not
        UTF-8, is a SetupError.'''
        args = ['git', 'grep', '--no-color', '-l', '-z', '-I', '-E', '-e', pattern]
        if self.ref is not None:
            args.append(self.ref)
        args += ['--', '.', *(f':(exclude){path}' for path in exclude)]
        proc = subprocess.run(args, cwd=self.repo, capture_output=True)
        if proc.returncode == 1:
            return []
        if proc.returncode != 0:
            raise SetupError(f"git grep in {self.label}: {proc.stderr.decode('utf-8', 'replace').strip()}")
        prefix = '' if self.ref is None else f'{self.ref}:'
        names = []
        for raw in filter(None, proc.stdout.split(b'\0')):
            try:
                name = raw.decode('utf-8')
            except UnicodeDecodeError:
                shown = raw.decode('utf-8', 'backslashreplace').removeprefix(prefix)
                raise SetupError(f'git grep in {self.label}: a tracked file name is not UTF-8 text: {shown}') from None
            names.append(name.removeprefix(prefix))
        return names


class Group(NamedTuple):
    sections: list[str]
    pages: dict[str, str]  # page -> mark: the `all` pages, then the `terms` pages


def mapped_pages(groups: dict[str, 'Group']) -> list[str]:
    '''Every mapped page once: group by group, each group's `all` pages
    before its `terms` pages.'''
    return list(dict.fromkeys(p for g in groups.values() for p in g.pages))


class Manifest(NamedTuple):
    guide: str
    sources: dict[str, str]
    cadence: dict[str, int]
    groups: dict[str, Group]  # manifest order
    terms: dict[str, tuple[list[str], list[str]]]  # section -> (extra, exclude)
    exclusions: list[tuple[str, str]]  # (page pattern, reason)
    probes: dict[str, tuple[list[str], list[str]]]  # probe -> (sections, files)

    def pages(self) -> list[str]:
        return mapped_pages(self.groups)

    def group_of(self) -> dict[str, str]:
        return {sid: gid for gid, g in self.groups.items() for sid in g.sections}


def _strings(value) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) and v for v in value)


def _positive(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _table(raw: dict, key: str, problems: list[str]) -> dict | None:
    '''raw[key] when it is a TOML table, {} when it is absent; else one
    listed problem and None, so the caller skips the table's fields.'''
    value = raw.get(key, {})
    if isinstance(value, dict):
        return value
    problems.append(f'[{key}] must be a table')
    return None


def _tables(raw: dict, key: str, problems: list[str]) -> list[dict]:
    '''raw[key] if it is an array of tables, written [[key]], else one
    listed problem and [].'''
    value = raw.get(key, [])
    if isinstance(value, list) and all(isinstance(v, dict) for v in value):
        return value
    problems.append(f'[[{key}]] must be an array of tables')
    return []


def _header(raw: dict, problems: list[str]) -> tuple[str | None, dict[str, str], dict[str, int]]:
    '''[guide], [sources] and [cadence] (R2.2).'''
    guide = _table(raw, 'guide', problems)
    path = None if guide is None else guide.get('path')
    if guide is not None and not (isinstance(path, str) and path):
        problems.append('[guide] path must be a non-empty string')
    sources = _table(raw, 'sources', problems)
    if sources is not None:
        problems += [f'[sources] {k} must be an https URL' for k in SOURCE_KEYS
                     if not (isinstance(sources.get(k), str) and sources[k].startswith('https://'))]
    cadence = _table(raw, 'cadence', problems)
    if cadence is not None:
        problems += [f'[cadence] {k} must be a positive integer' for k in CADENCE_KEYS
                     if not _positive(cadence.get(k))]
    return path, dict(sources or {}), dict(cadence or {})


def _pages(g: dict, where: str, problems: list[str]) -> dict[str, str]:
    '''One group's pages, page -> mark: its `all` pages, then its `terms` pages.'''
    pages: dict[str, str] = {}
    for mark in MARKS:
        listed = g.get(mark, [])
        if not _strings(listed):
            problems.append(f'{where} {mark} must be a list of pages')
            continue
        for page in listed:
            if page in pages:
                problems.append(f'{where} {page} is listed twice')
            pages[page] = mark
    if not pages:
        problems.append(f'{where} maps no page')
    return pages


def _groups(raw: dict, problems: list[str]) -> tuple[dict[str, Group], dict[str, str]]:
    '''[groups.<id>] (R2.5): the groups, and each section's one group.'''
    groups: dict[str, Group] = {}
    owner: dict[str, str] = {}
    raw_groups = raw.get('groups')
    if not isinstance(raw_groups, dict) or not raw_groups:
        problems.append('[groups] must hold at least one group')
        return groups, owner
    for gid, g in raw_groups.items():
        where = f'[groups.{gid}]'
        if not GROUP_RE.fullmatch(gid):
            problems.append(f'{where} group IDs are [a-z0-9-]')
        if not isinstance(g, dict) or set(g) - {'sections', *MARKS}:
            problems.append(f'{where} holds only sections, all and terms')
            continue
        secs = g.get('sections')
        if not _strings(secs) or not secs:
            problems.append(f'{where} sections must be a non-empty list of section IDs')
            secs = []
        for sid in secs:
            if not ID_RE.fullmatch(sid):
                problems.append(f'{where} {sid!r} is not a section ID')
            elif sid in owner:
                problems.append(f'{where} {sid} is already in group {owner[sid]}')
            else:
                owner[sid] = gid
        groups[gid] = Group(list(secs), _pages(g, where, problems))
    return groups, owner


def _terms(raw: dict, owner: dict[str, str], problems: list[str]) -> dict[str, tuple[list[str], list[str]]]:
    '''[sections.<id>]: a grouped section's extra and exclude terms (R3.6).'''
    terms: dict[str, tuple[list[str], list[str]]] = {}
    for sid, t in (_table(raw, 'sections', problems) or {}).items():
        if sid not in owner:
            problems.append(f'[sections.{sid!r}] is not in any group')
        shaped = isinstance(t, dict) and not set(t) - {'extra_terms', 'exclude_terms'}
        extra, exclude = (t.get('extra_terms', []), t.get('exclude_terms', [])) if shaped else ([], [])
        if not shaped or not _strings(extra) or not _strings(exclude):
            problems.append(f'[sections.{sid!r}] holds only extra_terms and exclude_terms, as lists')
            continue
        terms[sid] = (extra, exclude)
    return terms


def _exclusions(raw: dict, mapped: list[str], problems: list[str]) -> list[tuple[str, str]]:
    '''[[exclusion]]: page patterns no group may map, each with its reason.'''
    exclusions: list[tuple[str, str]] = []
    for e in _tables(raw, 'exclusion', problems):
        page, reason = e.get('page'), e.get('reason')
        if not (isinstance(page, str) and page and isinstance(reason, str) and reason):
            problems.append('[[exclusion]] needs a page pattern and a reason')
            continue
        exclusions.append((page, reason))
    problems += [f'page {page} is mapped but matches exclusion {pattern!r}'
                 for page in mapped for pattern, _ in exclusions if fnmatch.fnmatchcase(page, pattern)]
    return exclusions


def _probes(raw: dict, owner: dict[str, str], problems: list[str]) -> dict[str, tuple[list[str], list[str]]]:
    '''[[probe]]: each registered probe's sections and files (R10.1).'''
    probes: dict[str, tuple[list[str], list[str]]] = {}
    for p in _tables(raw, 'probe', problems):
        pid, secs, files = p.get('id'), p.get('sections'), p.get('files', [])
        if not (isinstance(pid, str) and pid) or pid in probes:
            problems.append('[[probe]] needs a unique id')
            continue
        if not _strings(secs) or not secs or any(s not in owner for s in secs) or not _strings(files):
            problems.append(f'[[probe]] {pid}: sections must name grouped sections; files is a list')
            continue
        probes[pid] = (secs, files)
    return probes


def parse_manifest(text: str) -> Manifest:
    '''manifest.toml (R2.2), validated. Raises SetupError listing every
    problem, so an invalid manifest exits 2.'''
    try:
        raw = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise SetupError(f'{MANIFEST}: not valid TOML ({exc})') from None
    problems = [f'unknown table or key {k!r}' for k in sorted(set(raw) - set(TABLES))]
    guide_path, sources, cadence = _header(raw, problems)
    groups, owner = _groups(raw, problems)
    terms = _terms(raw, owner, problems)
    exclusions = _exclusions(raw, mapped_pages(groups), problems)
    probes = _probes(raw, owner, problems)
    if problems:
        raise SetupError('\n'.join(f'{MANIFEST}: {p}' for p in problems))
    return Manifest(guide_path, sources, cadence, groups, terms, exclusions, probes)


def is_iso_date(value) -> bool:
    '''A YYYY-MM-DD date. date.fromisoformat alone also takes 20260902 and
    week dates such as 2026-W36-3.'''
    if not (isinstance(value, str) and DATE_RE.fullmatch(value)):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def is_label(value) -> bool:
    '''A release label (R2.4).'''
    try:
        version_key(value)
    except (TypeError, ValueError):
        return False
    return True


def _stamp(value) -> bool:
    return (isinstance(value, dict) and set(value) == {'release', 'date'}
            and is_label(value['release']) and is_iso_date(value['date']))


def parse_baseline(text: str) -> dict:
    '''baseline.json (R2.3), validated. Raises SetupError listing every
    problem, so an invalid baseline exits 2.'''
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SetupError(f'{BASELINE}: not valid JSON ({exc})') from None
    problems: list[str] = []
    if (not isinstance(raw, dict) or set(raw) != {'sections', 'groups', 'llms'}
            or not isinstance(raw['sections'], dict) or not isinstance(raw['groups'], dict)):
        raise SetupError(f'{BASELINE}: holds exactly sections, groups and llms')
    if not raw['sections']:
        problems.append('sections must hold at least one section')
    for sid, s in raw['sections'].items():
        ok = (isinstance(s, dict) and set(s) == {'checked', 'changed', 'audited', 'text_hash'}
              and _stamp(s['checked']) and _stamp(s['audited']) and is_label(s['changed'])
              and isinstance(s['text_hash'], str) and TEXT_HASH_RE.fullmatch(s['text_hash']))
        if not ok:
            problems.append(f'section {sid}: needs checked, changed, audited and text_hash')
    for gid, g in raw['groups'].items():
        ok = (isinstance(g, dict) and set(g) == {'blocks', 'snapshot'}
              and isinstance(g['blocks'], dict) and isinstance(g['snapshot'], dict))
        if ok:
            ok = all(isinstance(keys, dict) and all(HASH_RE.fullmatch(k) and isinstance(h, str) and HASH_RE.fullmatch(h)
                                                    for k, h in keys.items())
                     for keys in g['blocks'].values())
            ok = ok and all(is_label(r) for r in g['snapshot'].values())
        if not ok:
            problems.append(f'group {gid}: needs blocks (page -> key hash -> block hash)'
                            ' and snapshot (page -> release)')
    if not _strings(raw['llms']):
        problems.append('llms must be a list of slugs')
    if problems:
        raise SetupError('\n'.join(f'{BASELINE}: {p}' for p in problems))
    return raw


def dump_baseline(state: dict) -> str:
    '''baseline.json's text: insertion order kept, so diffs stay readable.'''
    return json.dumps(state, indent=1, ensure_ascii=False) + '\n'


class ProbeRow(NamedTuple):
    date: date
    version: str
    probe: str
    outcome: str


def table_cells(line: str) -> list[str]:
    '''A Markdown table line's cells, stripped; an escaped pipe stays in its cell.'''
    return [c.strip() for c in CELL_SPLIT_RE.split(line.strip().strip('|'))]


def is_probe_header(line: str) -> bool:
    '''Whether the line heads PROBES.md's log table: a table line naming the
    date, version, probe and outcome columns.'''
    return line.strip().startswith('|') and PROBE_COLUMNS <= {c.lower() for c in table_cells(line)}


def parse_probes(text: str | None) -> list[ProbeRow]:
    '''PROBES.md's rows (R10.6), in file order. The log table is any table
    whose header names the date, version, probe and outcome columns; another
    table, such as a legend, is skipped. A row needs a release label, a
    date, a probe and one of R10.5's outcomes, so a typo such as `DIVERGED`
    is a SetupError, never a row read as passed. An absent file has no rows:
    the first `probes` run creates it.'''
    if text is None:
        return []
    rows: list[ProbeRow] = []
    header: list[str] | None = None
    for line in text.split('\n'):
        s = line.strip()
        if not s.startswith('|'):
            header = None
            continue
        if header is None:
            header = [c.lower() for c in table_cells(s)]
            continue
        if set(s) <= set('|-: ') or not PROBE_COLUMNS <= set(header):
            continue
        row = dict(zip(header, table_cells(s)))
        try:
            version_key(row['version'])
            outcome = row['outcome'].upper()
            if outcome not in OUTCOMES or not row['probe']:
                raise ValueError(outcome)
            rows.append(ProbeRow(date.fromisoformat(row['date']), row['version'], row['probe'], outcome))
        except (KeyError, ValueError):
            raise SetupError(f'{PROBES}: unreadable row {s!r}') from None
    return rows


def group_terms(manifest: Manifest, guide_text: str) -> dict[str, dict[str, set[str]]]:
    '''Per group, per section in group order, the section's terms (R3.6).'''
    by_id = {s.id: s for s in sections(guide_text) if s.id}
    out: dict[str, dict[str, set[str]]] = {}
    for gid, g in manifest.groups.items():
        out[gid] = {}
        for sid in g.sections:
            extra, exclude = manifest.terms.get(sid, ([], []))
            out[gid][sid] = section_terms(by_id[sid], extra, exclude) if sid in by_id else set(extra)
    return out


def default_cache() -> Path:
    '''~/.cache/agent-skills/cc-guide, resolved from HOME at call time.'''
    return Path.home() / '.cache' / 'agent-skills' / 'cc-guide'


def latest_docs(cache: Path) -> Path:
    return cache / 'latest' / 'docs'


def fetch_record(cache: Path) -> Path:
    '''The last fetch's time and changelog head, beside latest/docs (R6.4).'''
    return cache / 'latest' / 'fetch.json'


def read_utf8(path: Path) -> str:
    '''A cached or local docs file's text. A file that is not UTF-8 is a
    SetupError naming it, so it prints one cc-guide: line.'''
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError as exc:
        raise SetupError(f'{path}: not UTF-8 text ({exc.reason} at byte {exc.start})') from None


def read_fetch(cache: Path) -> dict | None:
    '''The last fetch's record (R6.4), or None before the first fetch. A
    record that does not parse, or names no changelog head, is a SetupError.'''
    path = fetch_record(cache)
    if not path.is_file():
        return None
    try:
        record = json.loads(read_utf8(path))
    except json.JSONDecodeError as exc:
        raise SetupError(f'{path}: not valid JSON ({exc}); delete it and run check') from None
    if not (isinstance(record, dict) and is_label(record.get('changelog_head'))):
        raise SetupError(f'{path}: names no changelog_head release; delete it and run check')
    return record


def snapshot_docs(cache: Path, release: str) -> Path:
    return cache / release / 'docs'


# Reads (page, release) -> the page as that release's snapshot holds it, or None.
Snapshot = Callable[[str, str], str | None]


def no_snapshot(page: str, release: str) -> None:
    '''The Snapshot that holds nothing, so baselined blocks go by key hash.'''
    return None


def snapshot_text(cache: Path, page: str, release: str) -> str | None:
    '''The cache's Snapshot: the page as <release>/docs holds it.'''
    path = snapshot_docs(cache, release) / page_file(page)
    return read_utf8(path) if path.is_file() else None


def snapshot_blocks(state: dict, group: str, snapshot: Snapshot) -> Callable[[str], dict[str, tuple[str, str]]]:
    '''Reads one group's snapshot pages, page -> {key hash: (key, normalized
    text)}: each page as the release in the group's `snapshot` holds it
    (R2.3), {} when no snapshot holds it. Each page is read once.'''
    releases = state['groups'].get(group, {}).get('snapshot', {})
    held: dict[str, dict[str, tuple[str, str]]] = {}

    def read(page: str) -> dict[str, tuple[str, str]]:
        if page not in held:
            text = snapshot(page, releases[page]) if page in releases else None
            held[page] = {} if text is None else {key_hash(k): (k, body) for k, body in page_blocks(text).items()}
        return held[page]
    return read


def block_namer(state: dict, group: str, snapshot: Snapshot) -> Callable[[str, str], str]:
    '''Names one group's baselined blocks, (page, key hash) -> key: the key
    read back from the page's snapshot (R2.3), else the key hash itself.'''
    read = snapshot_blocks(state, group, snapshot)
    return lambda page, kh: read(page).get(kh, (kh, ''))[0]


def baselined_text(state: dict, group: str, snapshot: Snapshot) -> Callable[[str, str], str | None]:
    '''Reads one group's baselined blocks' text, (page, key hash) -> the
    block's normalized text as the page's snapshot holds it, else None. A
    block gone from the page has no current text, so a packet shows this.'''
    read = snapshot_blocks(state, group, snapshot)
    return lambda page, kh: read(page).get(kh, (kh, None))[1]


def writable_snapshot(cache: Path, release: str) -> Path:
    '''<release>/docs, which rebaseline and packets may write; the bootstrap
    snapshot is never written (R2.6).'''
    target = snapshot_docs(cache, release)
    if release == BOOTSTRAP_RELEASE:
        raise SetupError(f'{target} is the bootstrap snapshot, which is never '
                         'written (R2.6): run check to fetch a newer release first')
    return target


def same_blocks(held: bytes, body: bytes) -> bool:
    '''Two copies of a page that cut into the same blocks (R3), such as its
    MDX and Markdown exports (R3.2). Bytes that are not UTF-8 never match.'''
    try:
        return page_blocks(held.decode('utf-8')) == page_blocks(body.decode('utf-8'))
    except UnicodeDecodeError:
        return False


def copy_to_snapshot(cache: Path, release: str, files: dict[str, str]) -> Path:
    '''Copy latest/docs files into <release>/docs, returning that directory.
    `files` maps the name a message gives each file to its cache file name.
    A file already there that cuts into other blocks is never overwritten,
    since another group's `snapshot` may name it; one with the same blocks
    takes the new bytes, which the verifier greps (owner, 2026-10-20). Every
    file is checked before any is written.'''
    target = writable_snapshot(cache, release)
    copies = [(label, target / name, (latest_docs(cache) / name).read_bytes()) for label, name in files.items()]
    for label, held, body in copies:
        if held.is_file() and (old := held.read_bytes()) != body and not same_blocks(old, body):
            raise SetupError(f'{label}: {held} already holds different text, which another group may have '
                             'baselined; it is never overwritten')
    target.mkdir(parents=True, exist_ok=True)
    for _, held, body in copies:
        held.write_bytes(body)
    return target


def newest_changelog(cache: Path) -> Path | None:
    '''The newest cached changelog: latest/, else the bootstrap snapshot.
    Fixed paths only; release directories are never globbed.'''
    for path in (latest_docs(cache) / 'changelog.md',
                 snapshot_docs(cache, BOOTSTRAP_RELEASE) / 'changelog.md'):
        if path.is_file():
            return path
    return None


def citing_files(source: Source, guide_path: str) -> dict[str, str]:
    '''The files R5's citation scan reads, path -> text: tracked files
    outside R4.2's excluded trees and the guide that hold a citation-shaped
    line. A tracked symlink is git's link text, so it is never read twice.'''
    return {path: source.require(path) for path in source.grep(CITE_SHAPED_ERE, (*UNCITED, guide_path))}

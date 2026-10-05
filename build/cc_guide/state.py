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

from blocks import CELL_SPLIT_RE, key_names, page_blocks
from docs import page_file, version_key
from guide import section_terms, sections

MANIFEST = 'build/cc_guide/manifest.toml'
BASELINE = 'build/cc_guide/baseline.json'
PROBES = 'build/cc_guide/PROBES.md'
MARKS = ('all', 'terms')
SOURCE_KEYS = ('docs_base', 'llms', 'changelog', 'platform_base')
CADENCE_KEYS = ('changelog_days', 'probe_days', 'audit_days')
ID_RE = re.compile(r'^[a-z0-9-]+(?:\.[a-z0-9-]+)+$')
GROUP_RE = re.compile(r'^[a-z0-9-]+$')
HASH_RE = re.compile(r'^[0-9a-f]{16}$')
TEXT_HASH_RE = re.compile(r'^sha256:[0-9a-f]{64}$')

# The bootstrap snapshot (R2.6): the 2026-10-03 refresh read the docs at
# 2.1.288 and checked them that day. 2.1.288 itself shipped on 2026-10-02.
BOOTSTRAP_RELEASE = '2.1.288'
BOOTSTRAP_DATE = '2026-10-03'


class SetupError(Exception):
    '''A missing or invalid input: exit 2, so a broken setup never looks clean.'''


class Source:
    '''Reads repo files from the working tree (ref None) or from a commit
    through `git show` (R6.1).'''

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
        if self.ref is None:
            p = self.repo / path
            return p.read_text(encoding='utf-8') if p.is_file() else None
        proc = subprocess.run(['git', 'show', f'{self.ref}:{path}'], cwd=self.repo,
                              capture_output=True, encoding='utf-8')
        return proc.stdout if proc.returncode == 0 else None

    def require(self, path: str) -> str:
        text = self.read(path)
        if text is None:
            raise SetupError(f'{path}: not found in {self.label}')
        return text


class Group(NamedTuple):
    sections: list[str]
    pages: dict[str, str]  # page -> mark, in manifest order


class Manifest(NamedTuple):
    guide: str
    sources: dict[str, str]
    cadence: dict[str, int]
    groups: dict[str, Group]  # manifest order
    terms: dict[str, tuple[list[str], list[str]]]  # section -> (extra, exclude)
    exclusions: list[tuple[str, str]]  # (page pattern, reason)
    probes: dict[str, tuple[list[str], list[str]]]  # probe -> (sections, files)

    def pages(self) -> list[str]:
        '''Every mapped page once, in manifest order.'''
        return list(dict.fromkeys(p for g in self.groups.values() for p in g.pages))

    def group_of(self) -> dict[str, str]:
        return {sid: gid for gid, g in self.groups.items() for sid in g.sections}


def _strings(value) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) and v for v in value)


def _table(raw: dict, key: str, problems: list[str]) -> dict:
    '''raw[key] if it is a TOML table, else one listed problem and {}.'''
    value = raw.get(key, {})
    if isinstance(value, dict):
        return value
    problems.append(f'[{key}] must be a table')
    return {}


def _tables(raw: dict, key: str, problems: list[str]) -> list[dict]:
    '''raw[key] if it is an array of tables, written [[key]], else one
    listed problem and [].'''
    value = raw.get(key, [])
    if isinstance(value, list) and all(isinstance(v, dict) for v in value):
        return value
    problems.append(f'[[{key}]] must be an array of tables')
    return []


def parse_manifest(text: str) -> Manifest:
    '''manifest.toml (R2.2), validated. Raises SetupError listing every
    problem, so an invalid manifest exits 2.'''
    try:
        raw = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise SetupError(f'{MANIFEST}: not valid TOML ({exc})') from None
    problems: list[str] = []
    unknown = set(raw) - {'guide', 'sources', 'cadence', 'groups', 'sections', 'exclusion', 'probe'}
    problems += [f'unknown table or key {k!r}' for k in sorted(unknown)]
    guide_path = _table(raw, 'guide', problems).get('path')
    if not isinstance(guide_path, str) or not guide_path:
        problems.append('[guide] path must be a non-empty string')
    sources = _table(raw, 'sources', problems)
    for k in SOURCE_KEYS:
        if not (isinstance(sources.get(k), str) and sources[k].startswith('https://')):
            problems.append(f'[sources] {k} must be an https URL')
    cadence = _table(raw, 'cadence', problems)
    for k in CADENCE_KEYS:
        v = cadence.get(k)
        if not (isinstance(v, int) and not isinstance(v, bool) and v > 0):
            problems.append(f'[cadence] {k} must be a positive integer')
    groups: dict[str, Group] = {}
    owner: dict[str, str] = {}
    raw_groups = raw.get('groups')
    if not isinstance(raw_groups, dict) or not raw_groups:
        problems.append('[groups] must hold at least one group')
        raw_groups = {}
    for gid, g in raw_groups.items():
        where = f'[groups.{gid}]'
        if not GROUP_RE.match(gid):
            problems.append(f'{where} group IDs are [a-z0-9-]')
        if not isinstance(g, dict) or set(g) - {'sections', 'all', 'terms'}:
            problems.append(f'{where} holds only sections, all and terms')
            continue
        secs = g.get('sections')
        if not _strings(secs) or not secs:
            problems.append(f'{where} sections must be a non-empty list of section IDs')
            secs = []
        for sid in secs:
            if not ID_RE.match(sid):
                problems.append(f'{where} {sid!r} is not a section ID')
            elif sid in owner:
                problems.append(f'{where} {sid} is already in group {owner[sid]}')
            else:
                owner[sid] = gid
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
        groups[gid] = Group(list(secs), pages)
    terms: dict[str, tuple[list[str], list[str]]] = {}
    for sid, t in _table(raw, 'sections', problems).items():
        if sid not in owner:
            problems.append(f'[sections.{sid!r}] is not in any group')
        shaped = isinstance(t, dict) and not set(t) - {'extra_terms', 'exclude_terms'}
        extra, exclude = (t.get('extra_terms', []), t.get('exclude_terms', [])) if shaped else ([], [])
        if not shaped or not _strings(extra) or not _strings(exclude):
            problems.append(f'[sections.{sid!r}] holds only extra_terms and exclude_terms, as lists')
            continue
        terms[sid] = (extra, exclude)
    exclusions: list[tuple[str, str]] = []
    for e in _tables(raw, 'exclusion', problems):
        page, reason = e.get('page'), e.get('reason')
        if not (isinstance(page, str) and page and isinstance(reason, str) and reason):
            problems.append('[[exclusion]] needs a page pattern and a reason')
            continue
        exclusions.append((page, reason))
    mapped = list(dict.fromkeys(p for g in groups.values() for p in g.pages))
    for page in mapped:
        for pattern, _ in exclusions:
            if fnmatch.fnmatchcase(page, pattern):
                problems.append(f'page {page} is mapped but matches exclusion {pattern!r}')
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
    if problems:
        raise SetupError('\n'.join(f'{MANIFEST}: {p}' for p in problems))
    return Manifest(guide_path, dict(sources), dict(cadence), groups, terms, exclusions, probes)


def _iso(value) -> bool:
    try:
        date.fromisoformat(value)
        return isinstance(value, str)
    except (TypeError, ValueError):
        return False


def _label(value) -> bool:
    try:
        version_key(value)
        return True
    except (TypeError, ValueError):
        return False


def _stamp(value) -> bool:
    return (isinstance(value, dict) and set(value) == {'release', 'date'}
            and _label(value['release']) and _iso(value['date']))


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
    for sid, s in raw['sections'].items():
        ok = (isinstance(s, dict) and set(s) == {'checked', 'changed', 'audited', 'text_hash'}
              and _stamp(s['checked']) and _stamp(s['audited']) and _label(s['changed'])
              and isinstance(s['text_hash'], str) and TEXT_HASH_RE.match(s['text_hash']))
        if not ok:
            problems.append(f'section {sid}: needs checked, changed, audited and text_hash')
    for gid, g in raw['groups'].items():
        ok = (isinstance(g, dict) and set(g) == {'blocks', 'snapshot'}
              and isinstance(g['blocks'], dict) and isinstance(g['snapshot'], dict))
        if ok:
            ok = all(isinstance(keys, dict) and all(HASH_RE.match(k) and isinstance(h, str) and HASH_RE.match(h)
                                                    for k, h in keys.items())
                     for keys in g['blocks'].values())
            ok = ok and all(_label(r) for r in g['snapshot'].values())
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


def parse_probes(text: str | None) -> list[ProbeRow]:
    '''PROBES.md's rows (R10.6), in file order. The table's header names the
    columns; date, version, probe and outcome are read. An absent file has no
    rows: Stage 5 creates it, and until then no probe is registered.'''
    if text is None:
        return []
    rows: list[ProbeRow] = []
    header: list[str] | None = None
    for line in text.split('\n'):
        s = line.strip()
        if not s.startswith('|'):
            header = None
            continue
        cells = [c.strip() for c in CELL_SPLIT_RE.split(s.strip('|'))]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if set(s) <= set('|-: '):
            continue
        row = dict(zip(header, cells))
        try:
            version_key(row['version'])
            rows.append(ProbeRow(date.fromisoformat(row['date']), row['version'],
                                 row['probe'], row['outcome'].upper()))
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
    return path.read_text(encoding='utf-8') if path.is_file() else None


def block_namer(state: dict, group: str, snapshot: Snapshot) -> Callable[[str, str], str]:
    '''Names one group's baselined blocks, (page, key hash) -> key: the key
    read back from the page's snapshot (R2.3), else the key hash itself.'''
    releases = state['groups'].get(group, {}).get('snapshot', {})
    names: dict[str, dict[str, str]] = {}

    def name(page: str, kh: str) -> str:
        if page not in names:
            text = snapshot(page, releases[page]) if page in releases else None
            names[page] = {} if text is None else key_names(page_blocks(text))
        return names[page].get(kh, kh)
    return name


def newest_changelog(cache: Path) -> Path | None:
    '''The newest cached changelog: latest/, else the bootstrap snapshot.
    Fixed paths only; release directories are never globbed.'''
    for path in (latest_docs(cache) / 'changelog.md',
                 snapshot_docs(cache, BOOTSTRAP_RELEASE) / 'changelog.md'):
        if path.is_file():
            return path
    return None

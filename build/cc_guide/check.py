'''`check`: fetch the docs when the changelog head moved, compare each group's
selected blocks with the baseline, list each section's untriaged releases,
and report what is due (drift spec R6). R6.8's citing-file lists are Stage
2's, `--hook` (R6.10) Stage 4's and `packets` (R6.11) Stage 3's.'''
import hashlib
import http.client
import json
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from functools import partial
from pathlib import Path
from typing import Callable, NamedTuple

from blocks import SEP, block_hash, candidates, key_hash, key_names, page_blocks, select
from docs import CHANGELOG, LLMS, Release, is_platform, page_file, page_url, parse_changelog, parse_llms, version_key
from lint import lint
from state import (BASELINE, MANIFEST, PROBES, Manifest, ProbeRow, SetupError, Snapshot, Source, block_namer,
                   fetch_record, group_terms, latest_docs, no_snapshot, parse_baseline, parse_manifest, parse_probes,
                   snapshot_text)

USER_AGENT = 'agent-skills-cc-guide/1 (Claude Code docs drift check)'
TIMEOUT = 30
WORKERS = 8
Fetch = Callable[[str], tuple[int, bytes]]


class FetchError(Exception):
    '''A request that failed twice, or answered other than 200 or 404.'''


def http_get(url: str) -> tuple[int, bytes]:
    '''R6.4: a GET with a 30-second timeout and one retry, sending a
    User-Agent that names the tool and nothing personal. A 404 returns
    (404, b''); any other failure raises FetchError.'''
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    error = ''
    for _ in range(2):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return 404, b''
            error = f'HTTP {exc.code}'
        except (OSError, http.client.HTTPException) as exc:
            error = str(exc)
    raise FetchError(f'{url}: {error}')


class Docs(NamedTuple):
    changelog: str
    llms: str
    pages: dict[str, str | None]  # mapped page -> text, None when absent
    origin: str                   # 'live' or the --docs directory
    errors: list[str]
    unread: set[str]              # pages whose fetch failed; never compared


def releases_of(changelog_text: str, source: str = 'changelog') -> list[Release]:
    '''The changelog's releases, newest first. A changelog that does not
    parse, or holds no release, is a SetupError naming its source.'''
    try:
        releases = parse_changelog(changelog_text)
    except ValueError as exc:
        raise SetupError(f'{source}: {exc}') from None
    if not releases:
        raise SetupError(f'{source}: no <Update> release blocks')
    return releases


def offline_docs(manifest: Manifest, folder: Path) -> Docs:
    '''R6.1 --docs: the docs read from a local directory, named as the cache
    names them. A page file that is absent is a missing page.'''
    def read(name: str) -> str | None:
        path = folder / name
        return path.read_text(encoding='utf-8') if path.is_file() else None
    changelog, llms = read(CHANGELOG), read(LLMS)
    if changelog is None or llms is None:
        raise SetupError(f'{folder}: needs {CHANGELOG} and {LLMS}')
    return Docs(changelog, llms, {p: read(page_file(p)) for p in manifest.pages()},
                str(folder), [], set())


def live_docs(manifest: Manifest, cache: Path, fetch: Fetch, now: datetime) -> Docs:
    '''R6.3-R6.4: fetch the changelog and llms.txt; then every mapped page if
    the changelog head moved since the last fetch, else only the mapped pages
    latest/docs lacks. Pages overwrite latest/docs. A 404 or a failed fetch
    removes the stale copy, so a later run fetches the page again.'''
    folder = latest_docs(cache)
    folder.mkdir(parents=True, exist_ok=True)
    record = fetch_record(cache)
    previous = json.loads(record.read_text(encoding='utf-8')).get('changelog_head') if record.is_file() else None
    fetched = {}
    for name, url in ((CHANGELOG, manifest.sources['changelog']), (LLMS, manifest.sources['llms'])):
        status, body = fetch(url)
        if status != 200:
            raise FetchError(f'{url}: HTTP {status}')
        fetched[name] = body.decode('utf-8')
    head = releases_of(fetched[CHANGELOG])[0].label
    pages = manifest.pages()
    todo = pages if head != previous else [p for p in pages if not (folder / page_file(p)).is_file()]

    def get(page: str):
        try:
            return page, fetch(page_url(page, manifest.sources)), None
        except FetchError as exc:
            return page, None, str(exc)
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(get, todo))
    errors, unread = [], set()
    for page, got, error in results:
        path = folder / page_file(page)
        if error is None and got[0] not in (200, 404):
            error = f'{page_url(page, manifest.sources)}: HTTP {got[0]}'
        if error is not None:
            errors.append(error)
            unread.add(page)
            path.unlink(missing_ok=True)
        elif got[0] == 404:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(got[1])
    for name, text in fetched.items():
        (folder / name).write_text(text, encoding='utf-8')
    record.write_text(json.dumps({'fetched_at': now.isoformat(timespec='seconds'),
                                  'changelog_head': head}, indent=1) + '\n', encoding='utf-8')
    texts = {p: (folder / page_file(p)).read_text(encoding='utf-8')
             if (folder / page_file(p)).is_file() else None for p in pages}
    return Docs(fetched[CHANGELOG], fetched[LLMS], texts, 'live', errors, unread)


class Finding(NamedTuple):
    group: str
    kind: str               # changed, missing, new or missing-page
    page: str
    key: str | None         # None for a missing page
    candidates: list[str]

    def ref(self) -> str:
        return self.page if self.key is None else self.page + SEP + self.key


def compare(manifest: Manifest, state: dict, terms: dict, docs: Docs,
            snapshot: Snapshot = no_snapshot) -> tuple[list[Finding], dict]:
    '''R6.5 and R3.7: per group, the changed, missing and new blocks and the
    missing pages, each with its candidate sections, plus the deselected
    blocks for information. A baselined block whose text changed is changed
    even when no longer selected; only an unchanged one is deselected. A page
    absent from llms.txt (code pages) or from the docs is missing; its blocks
    are not compared one by one. The baseline keys blocks by key hash (R2.3),
    so a block gone from the page is named from `snapshot`, else by its hash.'''
    slugs = parse_llms(docs.llms)
    findings: list[Finding] = []
    deselected: dict[str, list[str]] = {}
    for gid, group in manifest.groups.items():
        sec_terms = terms[gid]
        watched = set().union(*sec_terms.values())
        base = state['groups'].get(gid, {}).get('blocks', {})
        name = block_namer(state, gid, snapshot)
        info: list[str] = []
        for page, mark in group.pages.items():
            if page in docs.unread:
                continue
            text = docs.pages.get(page)
            if text is None or (not is_platform(page) and page not in slugs):
                findings.append(Finding(gid, 'missing-page', page, None, list(sec_terms)))
                continue
            found = page_blocks(text)
            live = key_names(found)
            chosen = set(select(found, mark, watched))
            old = base.get(page, {})
            for kh, recorded in old.items():
                key = live.get(kh)
                if key is None:
                    gone = name(page, kh)
                    # A block named only by its hash matches no term: every section is a candidate.
                    cands = list(sec_terms) if gone == kh else candidates(gone, '', sec_terms)
                    findings.append(Finding(gid, 'missing', page, gone, cands))
                elif block_hash(found[key]) != recorded:
                    findings.append(Finding(gid, 'changed', page, key, candidates(key, found[key], sec_terms)))
                elif key not in chosen:
                    info.append(page + SEP + key)
            for key in found:
                if key in chosen and key_hash(key) not in old:
                    findings.append(Finding(gid, 'new', page, key, candidates(key, found[key], sec_terms)))
        for page in base:
            if page not in group.pages:
                info += [page + SEP + name(page, kh) for kh in base[page]]
        deselected[gid] = info
    return findings, deselected


def untriaged(state: dict, releases: list[Release]) -> dict[str, list[str]]:
    '''R6.6: per section, the releases after its `checked`, oldest first.'''
    return {sid: [r.label for r in reversed(releases)
                  if version_key(r.label) > version_key(s['checked']['release'])]
            for sid, s in state['sections'].items()}


def release_notes(releases: list[Release], pending: set[str], terms: dict) -> dict:
    '''Every bullet of each untriaged release, with the sections whose terms
    it contains marked as hints only (R6.6).'''
    flat = {sid: t for group in terms.values() for sid, t in group.items()}
    return {r.label: {'date': r.date.isoformat(),
                      'bullets': [{'text': b, 'hints': [sid for sid, t in flat.items() if any(x in b for x in t)]}
                                  for b in r.bullets]}
            for r in reversed(releases) if r.label in pending}


def due_changelog(state: dict, releases: list[Release], days: int, today: date) -> dict | None:
    '''R6.7: the batch is due once the oldest release newer than some
    section's `checked` is at least `days` old.'''
    floor = min(version_key(s['checked']['release']) for s in state['sections'].values())
    pending = [r for r in releases if version_key(r.label) > floor]
    if not pending:
        return None
    oldest = pending[-1]
    due_from = oldest.date + timedelta(days=days)
    return {'releases': len(pending), 'oldest': oldest.label, 'oldest_date': oldest.date.isoformat(),
            'due_from': due_from.isoformat(), 'due': today >= due_from}


def due_probes(manifest: Manifest, rows: list[ProbeRow], newest: str, days: int, today: date) -> list[dict]:
    '''R6.7: a registered probe is due with no row; with a DIVERGES row and no
    later PASS; or `days` after its last row once a release has shipped past
    that row's version.'''
    out = []
    for pid in manifest.probes:
        mine = [r for r in rows if r.probe == pid]
        if not mine:
            out.append({'probe': pid, 'why': 'never run'})
            continue
        diverged = False
        for r in mine:
            diverged = True if r.outcome == 'DIVERGES' else False if r.outcome == 'PASS' else diverged
        last = mine[-1]
        if diverged:
            out.append({'probe': pid, 'why': 'DIVERGES with no later PASS'})
        elif (today - last.date).days >= days and version_key(newest) > version_key(last.version):
            out.append({'probe': pid, 'why': f'last run {last.date.isoformat()} at {last.version}'})
    return out


def due_audit(manifest: Manifest, state: dict, days: int, today: date) -> dict:
    '''R6.7: one clock for every group. An audit is due `days` after the most
    recent audit of any group, and targets the group with the oldest
    `audited` date, ties broken in manifest order.'''
    def day(sid: str) -> date:
        return date.fromisoformat(state['sections'][sid]['audited']['date'])
    groups = {gid: min(day(s) for s in g.sections if s in state['sections'])
              for gid, g in manifest.groups.items() if any(s in state['sections'] for s in g.sections)}
    last = max(day(s) for s in state['sections'])
    due_from = last + timedelta(days=days)
    return {'group': min(groups, key=groups.get), 'last_audit': last.isoformat(),
            'due_from': due_from.isoformat(), 'due': today >= due_from}


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def check(source: Source, cache: Path, *, docs_dir: Path | None, today: date, now: datetime,
          fetch: Fetch) -> tuple[int, dict, Path]:
    '''Run R6 against one set of inputs: (exit code, report, report path).
    Exit 0 when nothing is due, 1 when something is, 2 on an error. Writes
    only under the cache, never inside the repo (R6.10).'''
    manifest_text = source.require(MANIFEST)
    manifest = parse_manifest(manifest_text)
    baseline_text = source.require(BASELINE)
    state = parse_baseline(baseline_text)
    guide_text = source.require(manifest.guide)
    rows = parse_probes(source.read(PROBES))
    terms = group_terms(manifest, guide_text)
    errors: list[str] = []
    try:
        docs = offline_docs(manifest, docs_dir) if docs_dir else live_docs(manifest, cache, fetch, now)
    except FetchError as exc:
        docs = None
        errors.append(str(exc))
    releases = releases_of(docs.changelog) if docs else None
    report: dict = {'generated_at': now.isoformat(timespec='seconds'), 'inputs': source.label,
                    'docs': docs.origin if docs else None,
                    'hashes': {'manifest': sha256(manifest_text), 'baseline': sha256(baseline_text),
                               'guide': sha256(guide_text)}}
    violations, notes = lint(guide_text, manifest, state, {r.label for r in releases} if releases else None)
    report['lint'] = {'violations': violations, 'notes': notes}
    due = {'lint': len(violations)}
    if docs is not None:
        errors += docs.errors
        findings, deselected = compare(manifest, state, terms, docs, partial(snapshot_text, cache))
        pending = untriaged(state, releases)
        slugs = parse_llms(docs.llms)
        report.update({
            'latest_release': releases[0].label,
            'findings': {gid: [f._asdict() for f in findings if f.group == gid] for gid in manifest.groups},
            'deselected': deselected,
            'llms': {'added': sorted(slugs - set(state['llms'])), 'removed': sorted(set(state['llms']) - slugs)},
            'untriaged': pending,
            'releases': release_notes(releases, {l for ls in pending.values() for l in ls}, terms),
        })
        due.update({'blocks': len(findings),
                    'changelog': due_changelog(state, releases, manifest.cadence['changelog_days'], today),
                    'probes': due_probes(manifest, rows, releases[0].label, manifest.cadence['probe_days'], today),
                    'audit': due_audit(manifest, state, manifest.cadence['audit_days'], today)})
    report['due'] = due
    report['errors'] = errors
    anything = (due['lint'] or due.get('blocks') or (due.get('changelog') or {}).get('due')
                or due.get('probes') or (due.get('audit') or {}).get('due'))
    code = 2 if errors else 1 if anything else 0
    report['exit'] = code
    path = cache / 'reports' / f'{sha256(baseline_text)[:12]}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    return code, report, path


def summary(report: dict, path: Path) -> list[str]:
    '''The human-readable summary check prints (R6.8).'''
    due = report['due']
    lines = [f"cc-guide check: inputs from {report['inputs']}; docs {report['docs'] or 'unavailable'}"
             + (f"; changelog head {report['latest_release']}" if 'latest_release' in report else '')]
    violations = report['lint']['violations']
    lines.append('lint: clean' if not violations else f'lint: {len(violations)} violation(s), due')
    lines += [f'  {v}' for v in violations]
    if 'findings' in report:
        kinds = [f for group in report['findings'].values() for f in group]
        counts = {k: sum(1 for f in kinds if f['kind'] == k) for k in ('changed', 'missing', 'new', 'missing-page')}
        lines.append(f"blocks: {counts['changed']} changed, {counts['missing']} missing, {counts['new']} new, "
                     f"{counts['missing-page']} missing pages"
                     f"; {sum(map(len, report['deselected'].values()))} deselected (informational)")
        lines += [f"  [{f['group']}] {f['kind']} {f['page'] + (SEP + f['key'] if f['key'] else '')}"
                  f" (candidates: {', '.join(f['candidates'])})" for f in kinds]
        llms = report['llms']
        lines.append(f"llms.txt since the baseline: {len(llms['added'])} added, {len(llms['removed'])} removed")
        batch = due['changelog']
        lines.append('changelog: nothing untriaged' if batch is None else
                     f"changelog: {batch['releases']} release(s) untriaged, oldest {batch['oldest']} "
                     f"({batch['oldest_date']}); batch due from {batch['due_from']}" + (', due' if batch['due'] else ''))
        lines.append('probes: none due' if not due['probes'] else
                     'probes: ' + '; '.join(f"{p['probe']} ({p['why']})" for p in due['probes']))
        audit = due['audit']
        lines.append(f"audit: {audit['group']} due from {audit['due_from']}" + (', due' if audit['due'] else ''))
    lines += [f'error: {e}' for e in report['errors']]
    lines.append({0: 'nothing due', 1: 'something is due', 2: 'error'}[report['exit']] + f'; report {path}')
    return lines

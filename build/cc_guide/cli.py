#!/usr/bin/env python3
'''cc_guide: the drift detector for specs/guides/claude-code-customization-guide.md
(Stage 1 of specs/claude-code-drift-automation.md).

Run: uv run --python 3.13 python build/cc_guide/cli.py <subcommand>

  lint [--ref REF]
      Offline gate over the guide, manifest.toml and baseline.json (R5). Reads
      the working tree unless --ref names a commit. Exit 0 clean, 1 with one
      line per violation, 2 on a setup error.
  check [--ref REF | --worktree] [--docs DIR]
      Fetch the docs when the changelog head moved, compare, and report what
      is due (R6). Reads main's commit unless --ref or --worktree says
      otherwise; --docs DIR runs offline against a local copy. Writes only
      under the cache. Exit 0 nothing due, 1 something due, 2 an error.
  baseline init [--docs DIR] [--release LABEL] [--date YYYY-MM-DD] [--force]
  baseline rebaseline GROUP [PAGE | 'PAGE › KEY' ...]
  baseline advance ID [ID ...] --to RELEASE
  baseline audited GROUP
  baseline accept ID [ID ...] (--substantive | --editorial)
  baseline stamp
      The only writer of baseline.json and the guide's stamp region (R7).
      Always the working tree; nothing is committed. rebaseline takes each
      KEY as check prints it, a key hash for a block check could not name.

After reviewing what check reported, record it in R8.8's order: accept,
rebaseline, advance or audited, then stamp; then run lint and
build/check_conformance.py. advance and audited can move the oldest
`checked`, which the stamp names, so stamp follows them. A missing page
needs a manifest.toml edit first: rebaseline keeps its entries. `checked`
and `audited` record the day the check or audit was done, not the
release's date.
'''
import argparse
import json
import subprocess
import sys
import traceback
from datetime import date, datetime
from functools import partial
from pathlib import Path

import baseline
from check import check, http_get, releases_of, summary
from docs import page_file
from guide import render_stamp
from lint import lint
from state import (BASELINE, BOOTSTRAP_DATE, BOOTSTRAP_RELEASE, MANIFEST, SetupError, Source, default_cache,
                   dump_baseline, fetch_record, latest_docs, newest_changelog, parse_baseline, parse_manifest,
                   snapshot_docs, snapshot_text)

REPO = Path(__file__).resolve().parents[2]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='cli.py', description='Claude Code guide drift detector (Stage 1).')
    p.add_argument('--cache', type=Path, help='cache root (default: ~/.cache/agent-skills/cc-guide)')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('lint').add_argument('--ref')
    c = sub.add_parser('check')
    where = c.add_mutually_exclusive_group()
    where.add_argument('--ref', default='main')
    where.add_argument('--worktree', action='store_true')
    c.add_argument('--docs', type=Path)
    b = sub.add_parser('baseline').add_subparsers(dest='action', required=True)
    init = b.add_parser('init')
    init.add_argument('--docs', type=Path)
    init.add_argument('--release', default=BOOTSTRAP_RELEASE)
    init.add_argument('--date', default=BOOTSTRAP_DATE)
    init.add_argument('--force', action='store_true')
    rb = b.add_parser('rebaseline')
    rb.add_argument('group')
    rb.add_argument('refs', nargs='*')
    adv = b.add_parser('advance')
    adv.add_argument('ids', nargs='+')
    adv.add_argument('--to', required=True)
    b.add_parser('audited').add_argument('group')
    acc = b.add_parser('accept')
    acc.add_argument('ids', nargs='+')
    kind = acc.add_mutually_exclusive_group(required=True)
    kind.add_argument('--substantive', action='store_true')
    kind.add_argument('--editorial', action='store_true')
    b.add_parser('stamp')
    return p


def cached_releases(cache: Path):
    '''The newest cached changelog's releases (R5: latest/, else the 2.1.288
    snapshot), or None when neither is cached. A changelog that does not
    parse, or holds no release, is a SetupError (check.releases_of).'''
    path = newest_changelog(cache)
    if path is None:
        return None
    return releases_of(path.read_text(encoding='utf-8'), str(path))


def newest_releases(cache: Path):
    releases = cached_releases(cache)
    if not releases:
        raise SetupError('no cached changelog: run check, or restore the 2.1.288 snapshot')
    return releases


def git_show(ref: str, path: str) -> str:
    proc = subprocess.run(['git', 'show', f'{ref}:{path}'], cwd=REPO, capture_output=True, encoding='utf-8')
    if proc.returncode != 0:
        raise SetupError(f'R11.1 needs {ref}:{path}, which this clone lacks (a shallow clone?)')
    return proc.stdout


def run_lint(args, cache: Path) -> int:
    source = Source(REPO, args.ref)
    manifest = parse_manifest(source.require(MANIFEST))
    state = parse_baseline(source.require(BASELINE))
    releases = cached_releases(cache)
    violations, notes = lint(source.require(manifest.guide), manifest, state,
                             None if releases is None else {r.label for r in releases})
    for line in violations:
        print(line)
    for line in notes:
        print(f'note: {line}', file=sys.stderr)
    return 1 if violations else 0


def run_check(args, cache: Path, today: date, now: datetime, fetch) -> int:
    source = Source(REPO, None if args.worktree else args.ref)
    code, report, path = check(source, cache, docs_dir=args.docs, today=today, now=now, fetch=fetch)
    print('\n'.join(summary(report, path)))
    return code


def run_baseline(args, cache: Path, today: date) -> int:
    tree = Source(REPO)
    manifest = parse_manifest(tree.require(MANIFEST))
    guide_path = REPO / manifest.guide
    guide_text = tree.require(manifest.guide)
    baseline_path = REPO / BASELINE
    day = today.isoformat()
    if args.action == 'init':
        if baseline_path.exists() and not args.force:
            raise SetupError(f'{BASELINE} exists; init rebuilds it from scratch only with --force')
        changed = baseline.derive_changed(git_show(baseline.JULY[0], baseline.OLD_GUIDE_PATH),
                                          git_show(baseline.REFRESH[0], baseline.OLD_GUIDE_PATH), guide_text)
        docs = args.docs or snapshot_docs(cache, BOOTSTRAP_RELEASE)
        if not docs.is_dir():
            raise SetupError(f'{docs}: no snapshot directory')
        state = baseline.init(manifest, guide_text, docs, args.release, args.date, changed)
        baseline_path.write_text(dump_baseline(state), encoding='utf-8')
        print(f'wrote {BASELINE} from {docs}; next: baseline stamp')
        return 0
    state = parse_baseline(tree.require(BASELINE))
    if args.action == 'stamp':
        guide_path.write_text(baseline.stamp(guide_text, state), encoding='utf-8')
        print(f'regenerated the stamp region in {manifest.guide}')
        return 0
    if args.action == 'accept':
        # Only --substantive sets `changed`, from the newest release; an editorial accept needs no cache.
        newest = newest_releases(cache)[0].label if args.substantive else None
        new = baseline.accept(state, guide_text, args.ids, args.substantive, newest)
    elif args.action == 'advance':
        labels = {r.label for r in newest_releases(cache)}
        new = baseline.advance(state, args.ids, args.to, labels, day)
    elif args.action == 'audited':
        new = baseline.audited(state, manifest, args.group, newest_releases(cache)[0].label, day)
    else:
        record = fetch_record(cache)
        if not record.is_file():
            raise SetupError('no latest fetch: run check first')
        release = json.loads(record.read_text(encoding='utf-8'))['changelog_head']
        if release == BOOTSTRAP_RELEASE:
            raise SetupError(f'{snapshot_docs(cache, release)} is the bootstrap snapshot, which is never '
                             'written (R2.6): run check to fetch a newer release first')
        new, pages, notes = baseline.rebaseline(state, manifest, guide_text, args.group, args.refs,
                                                latest_docs(cache), release, partial(snapshot_text, cache))
        target = snapshot_docs(cache, release)
        target.mkdir(parents=True, exist_ok=True)
        for page in pages:
            name = page_file(page)
            (target / name).write_bytes((latest_docs(cache) / name).read_bytes())
        for line in notes:
            print(f'note: {line}', file=sys.stderr)
    baseline_path.write_text(dump_baseline(new), encoding='utf-8')
    if render_stamp(new['sections']) != render_stamp(state['sections']):
        print('the stamp region is now stale: run baseline stamp', file=sys.stderr)
    print(f'updated {BASELINE}')
    return 0


def main(argv=None, *, today: date | None = None, now: datetime | None = None, fetch=None) -> int:
    args = parser().parse_args(argv)
    try:
        cache = args.cache or default_cache()
        now = now or datetime.now().astimezone()
        today = today or now.date()
        if args.command == 'lint':
            return run_lint(args, cache)
        if args.command == 'check':
            return run_check(args, cache, today, now, fetch or http_get)
        return run_baseline(args, cache, today)
    except SetupError as exc:
        print(f'cc-guide: {exc}', file=sys.stderr)
        return 2
    except Exception:  # R6.9: a crash must never read as 0, clean, or 1, due
        traceback.print_exc()
        return 2


if __name__ == '__main__':
    sys.exit(main())

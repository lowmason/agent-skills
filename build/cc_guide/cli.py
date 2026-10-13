#!/usr/bin/env python3
'''cc_guide: the drift detector for specs/guides/claude-code-customization-guide.md,
the citations that point at it, and the deterministic half of /cc-guide
(Stages 1 to 3 of specs/claude-code-drift-automation-spec.md).

Run: uv run --python 3.13 python build/cc_guide/cli.py <subcommand>

  lint [--ref REF]
      Offline gate over the guide, manifest.toml, baseline.json and every
      citation (R5). Reads the working tree unless --ref names a commit. Exit
      0 clean, 1 with one line per violation, 2 on a setup error. A citation
      stamped below a cited section's `changed` prints STALE <file> <ids> on
      stderr, which never changes the exit. A three-part guide release label
      newer than the cached changelog's newest release, which the cache cannot
      judge, prints a `note:` line there, also without changing the exit; any
      other label the changelog does not list is a violation.
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
  baseline cite FILE [FILE ...]
      The only writer of baseline.json, the guide's stamp region and citation
      stamps (R7). cite stamps each file's citation at the highest `changed`
      among its cited sections, after a review; FILE is repo-relative, as
      lint and check print it. accept --substantive keeps a new `changed`
      above every citer's stamp (R2.4).
      Always the working tree; nothing is committed. rebaseline takes each
      KEY as check prints it, a key hash for a block check could not name.
      A listed rebaseline refuses while an unlisted baselined block on the
      same page has also changed or gone, since the page's snapshot would
      not hold that block's baselined text: list it too, or rebaseline the
      whole page. It also refuses to overwrite a snapshot page that holds
      other text.
  packets (--triage [--through RELEASE] | --verify [ID ...] [--from DIR]
           | --audit [GROUP] | --files [FILE ...]) [--out DIR]
      Write the packets /cc-guide hands its verifier (R6.11), from check
      --worktree's inputs: run check --worktree first, since packets never
      fetch. --verify and --audit copy their groups' pages to the head
      release's snapshot, which the verifier greps. --verify with no IDs
      takes the sections the settled triage --from names sent on. --audit
      with no group takes the due one, and refuses when none is due. --out
      defaults to a new directory under the cache's packets/, and is refused
      inside any checkout. Exit 0, or 2 on an error.
  quotes --in DIR
      Read `file<TAB>quote` rows on stdin and print FOUND file:line or
      MISSING file for each, a quote counting only within one line of the
      file under DIR (R8.3). Exit 0 when all are found, 1 on any miss.

After reviewing what check reported, record it in R8.8's order: accept,
rebaseline, advance, then audited for an audited group, then stamp; then run
lint and build/check_conformance.py. advance and audited can move the oldest
`checked`, which the stamp names, so stamp follows them. A missing page
needs a manifest.toml edit first: rebaseline keeps its entries. `checked`
and `audited` record the day the check or audit was done, not the
release's date.
'''
import argparse
import subprocess
import sys
import traceback
from datetime import date, datetime
from functools import partial
from pathlib import Path

import baseline
import packets
from check import check, due_audit, http_get, releases_of, summary
from docs import page_file
from guide import CITE_SHAPED_RE, by_section, read_citations, render_stamp
from lint import lint, stale_lines
from quotes import check_rows
from state import (BASELINE, BOOTSTRAP_DATE, BOOTSTRAP_RELEASE, MANIFEST, SetupError, Source, citing_files,
                   copy_to_snapshot, default_cache, dump_baseline, is_iso_date, is_label, latest_docs,
                   newest_changelog, parse_baseline, parse_manifest, read_fetch, read_utf8, snapshot_docs,
                   snapshot_text, writable_snapshot)

REPO = Path(__file__).resolve().parents[2]


REBASELINE_HELP = '''Re-hash GROUP's selected blocks from latest/ (all of them, or the listed
PAGE / 'PAGE › KEY' refs) and snapshot those pages to the cache.

A listed run refuses while an unlisted baselined block on the same page has
also changed or gone since the baseline: list it too, or rebaseline the whole
page. It also refuses to overwrite a snapshot page that holds different text.'''


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='cli.py', description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
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
    rb = b.add_parser('rebaseline', formatter_class=argparse.RawDescriptionHelpFormatter, description=REBASELINE_HELP)
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
    b.add_parser('cite').add_argument('files', nargs='+')
    k = sub.add_parser('packets')
    mode = k.add_mutually_exclusive_group(required=True)
    mode.add_argument('--triage', action='store_true')
    mode.add_argument('--verify', nargs='*', metavar='ID')
    mode.add_argument('--audit', nargs='?', const='', metavar='GROUP')
    mode.add_argument('--files', nargs='*', metavar='FILE')
    k.add_argument('--through', metavar='RELEASE')
    k.add_argument('--from', dest='settled', type=Path, metavar='DIR')
    k.add_argument('--out', type=Path)
    sub.add_parser('quotes').add_argument('--in', dest='root', type=Path, required=True)
    return p


def cached_releases(cache: Path):
    '''The newest cached changelog's releases (R5: latest/, else the 2.1.288
    snapshot), or None when neither is cached. A changelog that does not
    parse, or holds no release, is a SetupError (check.releases_of).'''
    path = newest_changelog(cache)
    if path is None:
        return None
    return releases_of(read_utf8(path), str(path))


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


def repo_path(name: str) -> str:
    '''A FILE argument as a repo-relative path. A relative one is read from
    the repo root, as lint and check print paths.'''
    full = (REPO / name).resolve()
    try:
        return full.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        raise SetupError(f'{name}: not a file in {REPO}') from None


def run_lint(args, cache: Path) -> int:
    source = Source(REPO, args.ref)
    manifest = parse_manifest(source.require(MANIFEST))
    state = parse_baseline(source.require(BASELINE))
    releases = cached_releases(cache)
    files = citing_files(source, manifest.guide)
    violations, notes = lint(source.require(manifest.guide), manifest, state,
                             None if releases is None else {r.label for r in releases}, files)
    for line in violations:
        print(line)
    for line in notes:
        print(f'note: {line}', file=sys.stderr)
    for line in stale_lines(read_citations(files)[0], state):
        print(line, file=sys.stderr)
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
        if not is_label(args.release):
            raise SetupError(f'baseline init: --release {args.release!r} is not a release label')
        if not is_iso_date(args.date):
            raise SetupError(f'baseline init: --date {args.date!r} is not a YYYY-MM-DD date')
        if args.docs is None and args.release != BOOTSTRAP_RELEASE:
            raise SetupError(f'baseline init: without --docs it reads the {BOOTSTRAP_RELEASE} bootstrap snapshot,'
                             f' so --release must be {BOOTSTRAP_RELEASE}')
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
    if args.action == 'cite':
        readable = citing_files(tree, manifest.guide)
        stamped = []
        for path in dict.fromkeys(map(repo_path, args.files)):  # a symlink and its target are one file
            text = tree.require(path)
            if path not in readable and any(CITE_SHAPED_RE.match(line) for line in text.split('\n')):
                raise SetupError(f'{path}: the lint never reads it (untracked, or under specs/, runtimes/ or '
                                 'review/), so its stamp would never be checked')
            stamped.append((path, *baseline.cite(path, text, state)))
        for path, text, stamp in stamped:  # all checked before any write
            (REPO / path).write_text(text, encoding='utf-8')
            print(f'stamped {path} @{stamp}')
        return 0
    if args.action == 'accept':
        # Only --substantive sets `changed`, from the newest release and above every citer's stamp (R2.4);
        # an editorial accept needs no cache.
        newest, stamps = None, None
        if args.substantive:
            newest = newest_releases(cache)[0].label
            citations, problems = read_citations(citing_files(tree, manifest.guide))
            if problems:  # a citation that does not parse has no stamp to stay above
                raise SetupError('a substantive accept needs every citation to parse (R2.4); fix these first:\n'
                                 + '\n'.join(problems))
            stamps = {sid: [c.stamp for c in cs] for sid, cs in by_section(citations).items()}
        new = baseline.accept(state, guide_text, args.ids, args.substantive, newest, stamps)
    elif args.action == 'advance':
        labels = {r.label for r in newest_releases(cache)}
        new = baseline.advance(state, args.ids, args.to, labels, day)
    elif args.action == 'audited':
        new = baseline.audited(state, manifest, args.group, newest_releases(cache)[0].label, day)
    else:
        record = read_fetch(cache)
        if record is None:
            raise SetupError('no latest fetch: run check first')
        release = record['changelog_head']
        writable_snapshot(cache, release)
        new, pages, notes = baseline.rebaseline(state, manifest, guide_text, args.group, args.refs,
                                                latest_docs(cache), release, partial(snapshot_text, cache))
        copy_to_snapshot(cache, release, {page: page_file(page) for page in pages})
        for line in notes:
            print(f'note: {line}', file=sys.stderr)
    baseline_path.write_text(dump_baseline(new), encoding='utf-8')
    if render_stamp(new['sections']) != render_stamp(state['sections']):
        print('the stamp region is now stale: run baseline stamp', file=sys.stderr)
    print(f'updated {BASELINE}')
    return 0


def run_packets(args, cache: Path, today: date, now: datetime) -> int:
    if args.through and not args.triage:
        raise SetupError('--through goes with --triage')
    if args.settled and args.verify is None:
        raise SetupError('--from goes with --verify')
    mode = next(m for m in ('triage', 'verify', 'audit', 'files') if getattr(args, m) not in (None, False))
    world = packets.load(Source(REPO), cache, now)
    out = args.out or cache / 'packets' / f"{now.strftime('%Y%m%dT%H%M%S')}-{mode}"
    if mode == 'triage':
        made = packets.triage(world, out, args.through)
        if made is None:
            print('nothing to triage: no untriaged release and no block finding')
            return 0
        made = [made]
    elif mode == 'verify':
        made = packets.verify(world, out, args.verify, args.settled and args.settled / packets.SETTLED)
    elif mode == 'audit':
        group = args.audit
        if not group:
            due = due_audit(world.manifest, world.state, world.manifest.cadence['audit_days'], today)
            if not due['due']:
                raise SetupError(f"no audit is due before {due['due_from']}: name a group to audit one anyway")
            group = due['group']
        made = [packets.audit(world, out, group)]
    else:
        made = packets.files(world, out, [repo_path(name) for name in args.files])
    for folder in made:
        print(f'wrote {mode} packet {folder}')
    return 0


def run_quotes(args) -> int:
    if not args.root.is_dir():
        raise SetupError(f'{args.root}: not a directory')
    lines, ok = check_rows(args.root, sys.stdin)
    print('\n'.join(lines))
    return 0 if ok else 1


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
        if args.command == 'packets':
            return run_packets(args, cache, today, now)
        if args.command == 'quotes':
            return run_quotes(args)
        return run_baseline(args, cache, today)
    except SetupError as exc:
        print(f'cc-guide: {exc}', file=sys.stderr)
        return 2
    except Exception:  # R6.9: a crash must never read as 0, clean, or 1, due
        traceback.print_exc()
        return 2


if __name__ == '__main__':
    sys.exit(main())

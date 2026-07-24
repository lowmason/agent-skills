'''Specs-harvest distiller (specs-harvest framework spec §4.1). Stdlib only.

inventory <repo> --root <wiki>: walk the repo's specs/ corpus, seed-grep,
build per-file introducing-SHA tables, pre-list previously-seen captures
from prior briefs, and write (or same-date-extend) the skeleton brief under
<root>/reports/. assemble <brief> --root <wiki>: validate ticked entries,
redact, write the raw/specs/ digest atomically, stamp the brief, and print
the source-page capture-note body for the ingest step.

Deterministic given its inputs; the only clock read is the --date default.
'''
import argparse
import datetime
import fnmatch
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

from distill_sessions import redact, slugify

KINDS = {'d': 'decision', 'r': 'rejected-approach', 'g': 'gotcha',
         'c': 'resolved-confusion', 'p': 'validated-pattern'}
BOUNDARIES = ('transferable', 'mixed', 'code-coupled')
SEP = ' · '  # U+00B7 middle dot: the capture-metadata field separator


def _atomic_write(path, text):
  '''Spec §7: validate everything first, then write last — and atomically.'''
  tmp = path.with_name('.tmp-' + path.name)
  tmp.write_text(text)
  os.replace(tmp, path)


def _git(repo, *args):
  proc = subprocess.run(['git', '-C', str(repo), *args],
                        capture_output=True, text=True)
  if proc.returncode != 0:
    raise RuntimeError(proc.stderr.strip() or f'git {args[0]} failed')
  return proc.stdout


def _repo_has_own_git_history(repo):
  '''`git -C repo rev-parse HEAD` still succeeds when repo is a plain
  subdirectory of some ancestor's git checkout — git walks up to find the
  nearest .git. Confirm repo is its own toplevel before trusting its HEAD
  as a landing SHA (spec §7: SHAs are load-bearing, so a borrowed parent
  HEAD must be rejected, not recorded).'''
  toplevel = _git(repo, 'rev-parse', '--show-toplevel').strip()
  return Path(toplevel).resolve() == repo.resolve()


def _repo_name(repo):
  '''slugify() always returns a truthy string — it falls back to the literal
  'session' when it finds no ASCII words — so `slugify(repo.name) or
  repo.name` could never engage its fallback branch. Detect that sentinel
  case (slug collapsed to 'session' but the dir isn't actually named that)
  and fall back to a sanitized raw dir name instead: strip a leading '#' or
  '-', since repo_name is embedded unquoted as `repo: {repo_name}` in the
  brief's YAML frontmatter and those lead characters mean comment / list
  item there. A name that sanitizes to nothing falls back to 'session'.'''
  slug = slugify(repo.name)
  if slug != 'session' or repo.name == 'session':
    return slug
  name = repo.name.lstrip('#-').strip()
  return name or 'session'


# Settled strata first (spec §7): completed material is stable ground truth;
# live drafts are harvested last if at all; deferred_items.md is demoted to
# the tail (pilot: near-noise, open questions at most).
WALK_DIRS = ('specs/completed', 'specs/plans/completed', 'specs', 'specs/plans')
DEFERRED_FILE = 'specs/deferred_items.md'


def walk_specs(repo, only=None):
  '''Return (repo-relative .md paths in harvest order, absent-input notes).'''
  files, notes = [], []
  for d in WALK_DIRS:
    p = repo / d
    if not p.is_dir():
      notes.append(f'{d}/: absent')
      continue
    section = sorted(f for f in p.glob('*.md') if f.name != 'deferred_items.md')
    if not section:
      notes.append(f'{d}/: no .md files')
    files += [str(f.relative_to(repo)) for f in section]
  if (repo / DEFERRED_FILE).is_file():
    files.append(DEFERRED_FILE)
  else:
    notes.append(f'{DEFERRED_FILE}: absent')
  if only:
    files = [f for f in files if fnmatch.fnmatch(f, only)]
  return files, notes


def brief_path(root, repo_name, date):
  return root / 'reports' / f'harvest-{repo_name}-{date}.md'


def render_brief_header(repo_name, repo_path, head, root, date, files, prior):
  return [
    '---',
    'harvest: specs',
    f'repo: {repo_name}',
    f'repo_path: {repo_path}',
    f'repo_head: {head}',
    f'root: {root}',
    f'date: {date}',
    f'prior_brief: {prior}',
    'files_walked: >',
    '  ' + '; '.join(files),
    '---',
    '',
  ]


def render_file_section(rel, shas, seeds, prior_keys):
  lines = [f'## {rel}', '', 'shas:']
  lines += ([f'- {sha}{SEP}{subj}{SEP}{cls}' for sha, subj, cls in shas]
            or ['- none'])
  lines += ['', 'seeds:']
  lines += ([f'- L{n} {label}: {text}' for n, label, text in seeds]
            or ['- none'])
  lines += ['', 'previously seen:']
  lines += ([f'- {key}' for key in prior_keys] or ['- none'])
  lines += ['', 'captures:', '',
            '(extraction: read the whole file at repo_head; append entries '
            'per the brief grammar in SCHEMA.md)', '']
  return lines


def cmd_inventory(args):
  repo = Path(args.repo).resolve()
  root = Path(args.root).resolve()
  date = args.date or datetime.date.today().isoformat()
  if not (root / 'SCHEMA.md').is_file():
    print(f'error: {root} is not a wiki root (no SCHEMA.md)', file=sys.stderr)
    return 1
  if not (repo / 'specs').is_dir():
    print(f'error: no specs/ directory in {repo} (nothing to harvest)',
          file=sys.stderr)
    return 1
  try:
    if not _repo_has_own_git_history(repo):
      raise RuntimeError(f'{repo} is not its own git toplevel '
                         '(borrowed a parent checkout history)')
    head = _git(repo, 'rev-parse', '--short', 'HEAD').strip()
  except (RuntimeError, OSError) as exc:
    print(f'error: {repo} has no usable git history ({exc}); '
          'landing SHAs are load-bearing', file=sys.stderr)
    return 1
  repo_name = _repo_name(repo)
  files, notes = walk_specs(repo, args.only)
  if not files:
    print('error: nothing to walk (check --only)', file=sys.stderr)
    return 1
  path = brief_path(root, repo_name, date)
  path.parent.mkdir(parents=True, exist_ok=True)
  body = render_brief_header(repo_name, repo, head, root, date, files, 'none')
  body += [f'note: {n}' for n in notes]
  if notes:
    body.append('')
  for rel in files:
    body += render_file_section(rel, [], [], [])
  _atomic_write(path, '\n'.join(body).rstrip('\n') + '\n')
  print(f'wrote {path}')
  return 0


def cmd_assemble(args):
  raise NotImplementedError  # Task 6


def main(argv=None):
  ap = argparse.ArgumentParser(
    description='Specs-harvest distiller: inventory and assemble.')
  sub = ap.add_subparsers(dest='cmd', required=True)
  inv = sub.add_parser('inventory',
                       help='walk a repo, write the skeleton brief')
  inv.add_argument('repo', help='repo checkout to harvest (explicit path)')
  inv.add_argument('--root', required=True,
                   help='wiki root (explicit, no default: wrong-wiki protection)')
  inv.add_argument('--date', default=None,
                   help='brief date YYYY-MM-DD (default: today)')
  inv.add_argument('--only', default=None,
                   help='glob over repo-relative paths, to batch large corpora')
  asm = sub.add_parser('assemble', help='ticked brief -> raw/specs digest')
  asm.add_argument('brief', help='the harvest brief (explicit path)')
  asm.add_argument('--root', required=True,
                   help='wiki root (must match the root recorded in the brief)')
  args = ap.parse_args(argv)
  return cmd_inventory(args) if args.cmd == 'inventory' else cmd_assemble(args)


if __name__ == '__main__':
  sys.exit(main())

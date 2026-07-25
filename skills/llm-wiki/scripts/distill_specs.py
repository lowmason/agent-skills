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


# Seed grep (spec §5.1). Hits are prompts for whole-file agent reading, not
# recall bounds (pilot: much of the yield was interleaved prose no seed regex
# can see) — precision here only orders attention.
SEED_PATTERNS = (
  ('decision', re.compile(r'^.*\*\*[^*\n]*\bdecision\b[^*\n]*\*\*.*$',
                          re.I | re.M)),
  ('rejected', re.compile(r'^.*\b(?:rejected|not taken|set aside)\b.*$',
                          re.I | re.M)),
  ('recorded', re.compile(r'^#{1,6} .*\(recorded\).*$', re.I | re.M)),
  ('tldr', re.compile(r'^#{1,6} .*\btl;?dr\b.*$', re.I | re.M)),
  ('policy', re.compile(r'^#{1,6} .*\b(?:policy|global constraints)\b.*$',
                        re.I | re.M)),
  ('completion', re.compile(r'^\*\*Status: COMPLETE.*$', re.M)),
  ('deviation', re.compile(r'^\s*> Deviation:.*$', re.M)),
)

# deferred-item means deferred_items.md entries (spec §5.1), not any markdown
# checkbox: plan files under specs/plans/completed/ carry 50-100 step-tracking
# checkboxes each, which would otherwise drown the signal (finding 1). Kept
# separate from SEED_PATTERNS so seed_hits can gate it by is_deferred.
DEFERRED_ITEM_PATTERN = ('deferred-item', re.compile(r'^- \[[ x]\] .*$', re.M))


def seed_hits(text, is_deferred=False):
  '''(line_no, label, redacted line ≤120 chars) per seed match, line order.
  is_deferred=True (only for DEFERRED_FILE text) additionally applies the
  deferred-item pattern. Redacting here is belt-and-braces: briefs live in
  reports/ on disk.'''
  patterns = SEED_PATTERNS
  if is_deferred:
    patterns += (DEFERRED_ITEM_PATTERN,)
  hits = []
  for label, pat in patterns:
    for m in pat.finditer(text):
      line_no = text.count('\n', 0, m.start()) + 1
      hits.append((line_no, label, redact(m.group(0).strip())[0][:120]))
  return sorted(hits)


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


def sha_table(repo, rel):
  '''Per-commit rows (sha, subject, class) newest first, following renames
  past retirement/reorg commits. Mechanical = the commit touches this file
  only as a pure rename/move with no content change (name-status R100);
  anything else — including a rename with edits (R0xx) — is substantive.'''
  out = _git(repo, 'log', '--follow', '-M', '--name-status',
             '--format=%x01%h%x02%s', '--', rel)
  rows, sha, subject, status = [], None, None, None
  for line in out.splitlines():
    if line.startswith('\x01'):
      if sha is not None:
        rows.append((sha, subject, _classify(status)))
      sha, subject = line[1:].split('\x02', 1)
      status = None
    elif line.strip():
      status = line.split('\t', 1)[0]
  if sha is not None:
    rows.append((sha, subject, _classify(status)))
  return rows


def _classify(status):
  return 'mechanical' if status and status.startswith('R100') else 'substantive'


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


def claim_hash(claim):
  '''Dedup-key half (spec §5.1): whitespace-normalized claim, 8 hex chars.'''
  norm = ' '.join((claim or '').split())
  return hashlib.sha256(norm.encode()).hexdigest()[:8]


def prior_briefs(root, repo_name, date):
  '''Prior briefs for this repo, sorted (ISO dates sort); the same-date
  brief is the accretion target, not a prior.'''
  return [p for p in
          sorted((root / 'reports').glob(f'harvest-{repo_name}-*.md'))
          if p.name != f'harvest-{repo_name}-{date}.md']


def seen_keys_by_file(briefs):
  '''{at-path: [id · at · claim-hash8, …]} across ALL prior entries —
  approved and declined alike, never only what was kept (spec §5.1).'''
  seen = {}
  for b in briefs:
    _, entries, _ = parse_brief(b.read_text())
    for e in entries:
      at = e['fields'].get('at')
      if not at:
        continue
      path = at.split(' ', 1)[0]
      key = (f'{e["id"]}{SEP}{at}{SEP}'
             f'{claim_hash(e["fields"].get("claim", ""))}')
      seen.setdefault(path, []).append(key)
  return seen


# Minimal brief reader for prior-brief scanning; Task 5 replaces it with
# the full validating parser (same signature, superset behavior).
ENTRY_RE = re.compile(r'^- \[([ x])\] \[([a-z])-(\d{2,})\] (.+)$')
FIELD_RE = re.compile(r'^  (kind|at|excerpt|claim|note): ?(.*)$')


def parse_brief(text):
  '''-> (header dict, entry list, error list).'''
  lines = text.split('\n')
  header, errors, i = {}, [], 0
  if lines and lines[0] == '---':
    i, key = 1, None
    while i < len(lines) and lines[i] != '---':
      line = lines[i]
      if line.startswith('  ') and key:
        header[key] = (header[key] + ' ' + line.strip()).strip()
      else:
        m = re.match(r'^([a-z_]+): ?(.*)$', line)
        if m:
          key = m.group(1)
          header[key] = '' if m.group(2) == '>' else m.group(2)
      i += 1
    i += 1
  entries, entry, field = [], None, None
  for line in lines[i:]:
    m = ENTRY_RE.match(line)
    if m:
      entry = {'ticked': m.group(1) == 'x',
               'id': f'{m.group(2)}-{m.group(3)}', 'prefix': m.group(2),
               'title': m.group(4).strip(), 'fields': {}, 'also': []}
      entries.append(entry)
      field = None
      continue
    if entry is None:
      continue
    fm = FIELD_RE.match(line)
    if fm:
      field = fm.group(1)
      entry['fields'][field] = fm.group(2).strip()
      continue
    if line.startswith('    ') and line.strip() and field:
      entry['fields'][field] += ' ' + line.strip()
      continue
    if line.strip():
      entry, field = None, None  # any other content ends the entry
  for e in entries:
    at = e['fields'].get('at', '')
    if SEP + 'sha: ' in at:
      e['fields']['at'], e['fields']['sha'] = at.rsplit(SEP + 'sha: ', 1)
  return header, entries, errors


def _extend_brief(path, repo, head, files, seen):
  '''Same-date re-run (spec §7): append sections for files not yet present;
  never overwrite or duplicate. One brief = one repo_head.'''
  text = path.read_text()
  header, _, _ = parse_brief(text)
  if header.get('repo_head') != head:
    print(f'error: {path.name} pins repo_head {header.get("repo_head")} but '
          f'HEAD is {head}; use a fresh --date (or re-run at the pinned head)',
          file=sys.stderr)
    return 1
  have = set(re.findall(r'^## (.+)$', text, re.M))
  new = [f for f in files if f not in have]
  if not new:
    print(f'{path.name}: no new files; brief unchanged')
    return 0
  body = []
  for rel in new:
    file_text = (repo / rel).read_text()
    body += render_file_section(rel, sha_table(repo, rel),
                                seed_hits(file_text), seen.get(rel, []))
  walked = [f.strip() for f in header.get('files_walked', '').split(';')
            if f.strip()]
  walked += [f for f in new if f not in walked]
  lines = text.rstrip('\n').split('\n')
  for i, line in enumerate(lines):
    if line == 'files_walked: >':
      lines[i + 1] = '  ' + '; '.join(walked)
      break
  _atomic_write(path, '\n'.join(lines) + '\n\n'
                + '\n'.join(body).rstrip('\n') + '\n')
  print(f'extended {path} (+{len(new)} files)')
  return 0


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
  priors = prior_briefs(root, repo_name, date)
  seen = seen_keys_by_file(priors)
  prior = f'reports/{priors[-1].name}' if priors else 'none'
  path = brief_path(root, repo_name, date)
  path.parent.mkdir(parents=True, exist_ok=True)
  if path.exists():
    return _extend_brief(path, repo, head, files, seen)
  body = render_brief_header(repo_name, repo, head, root, date, files, prior)
  body += [f'note: {n}' for n in notes]
  if notes:
    body.append('')
  for rel in files:
    text = (repo / rel).read_text()
    body += render_file_section(rel, sha_table(repo, rel), seed_hits(text, rel == DEFERRED_FILE),
                                seen.get(rel, []))
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

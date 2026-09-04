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
  item there. A name that sanitizes to nothing — or that still
  carries a YAML key separator — falls back to 'session'.'''
  slug = slugify(repo.name)
  if slug != 'session' or repo.name == 'session':
    return slug
  name = repo.name.lstrip('#-').strip()
  # ': ' re-parses as a nested key in `repo: {repo_name}` — the same
  # unquoted-scalar hazard as the lead characters stripped above, but it can
  # sit anywhere in the name, so the only safe move is the sentinel.
  if not name or ': ' in name:
    return 'session'
  return name


# Settled strata first (spec §7): completed material is stable ground truth;
# live drafts are harvested last if at all; deferred_items.md is demoted to
# the tail (pilot: near-noise, open questions at most).
WALK_DIRS = ('specs/completed', 'specs/plans/completed', 'specs', 'specs/plans')
DEFERRED_FILE = 'specs/deferred_items.md'
# render_digest and the drift check read these with a hard []; a hand-edited
# brief missing one must fail the gate with a brief-error line, not a
# KeyError traceback.
REQUIRED_HEADER_KEYS = ('repo', 'repo_head', 'date')


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


def renamed_from(repo, rel):
  '''Historical repo-relative paths for rel, newest first, read from the same
  --follow history sha_table walks. `previously seen` keys are grouped by the
  at:-path recorded in prior briefs, so a spec retired between two harvests
  (specs/x.md -> specs/completed/x.md) loses every prior hint unless its old
  names are looked up too.'''
  out = _git(repo, 'log', '--follow', '-M', '--name-status',
             '--diff-filter=R', '--format=', '--', rel)
  olds = []
  for line in out.splitlines():
    parts = line.split('\t')
    if len(parts) == 3 and parts[0].startswith('R') and parts[1] not in olds:
      olds.append(parts[1])
  return olds


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
  brief is the accretion target, not a prior. glob() alone is an unanchored
  prefix match: in a shared multi-repo wiki root, repo "wiki" would
  otherwise pick up another repo's "harvest-wiki-tools-<date>.md" (spec
  §4.1/§7 wrong-wiki protection) -- filter to an exact
  harvest-<repo_name>-YYYY-MM-DD.md shape.'''
  name_re = re.compile(r'harvest-' + re.escape(repo_name)
                       + r'-\d{4}-\d{2}-\d{2}\.md')
  return [p for p in
          sorted((root / 'reports').glob(f'harvest-{repo_name}-*.md'))
          if name_re.fullmatch(p.name) and
          p.name != f'harvest-{repo_name}-{date}.md']


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
# Capture the whole parenthesized body; parse_brief splits off the sha on
# the LAST `· sha: ` marker, mirroring the at: field's rsplit. An optional
# inline hex group here couldn't fail loud: a malformed `· sha: TBD` suffix
# just fell out of the group and was silently swallowed into the location
# capture (sha=None), so validate_entries never saw it. Shape-checking
# lives in validate_entries against SHA_RE.
ALSO_RE = re.compile(r'^  \(also (.+)\)$')
SHA_RE = re.compile(r'[0-9a-f]{7,40}')  # git hash, short to full; lowercase hex


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
    am = ALSO_RE.match(line)
    if am:
      loc, sha = am.group(1), None
      if SEP + 'sha: ' in loc:
        loc, sha = loc.rsplit(SEP + 'sha: ', 1)
      entry['also'].append((loc, sha))
      continue
    fm = FIELD_RE.match(line)
    if fm:
      field = fm.group(1)
      if field in entry['fields']:
        errors.append(f'{entry["id"]}: duplicate field {field}')
      entry['fields'][field] = fm.group(2).strip()
      continue
    if line.startswith('    ') and line.strip() and field:
      entry['fields'][field] += ' ' + line.strip()
      continue
    if line.strip():
      entry, field = None, None  # any other content ends the entry
  for e in entries:
    kind = e['fields'].get('kind', '')
    if SEP + 'boundary: ' in kind:
      e['fields']['kind'], e['fields']['boundary'] = \
        kind.split(SEP + 'boundary: ', 1)
    at = e['fields'].get('at', '')
    if SEP + 'sha: ' in at:
      e['fields']['at'], e['fields']['sha'] = at.rsplit(SEP + 'sha: ', 1)
    exc = e['fields'].get('excerpt', '')
    if len(exc) >= 2 and exc[0] == '"' and exc[-1] == '"':
      # the surrounding quotes are brief syntax, not excerpt content — the
      # digest renderer re-adds exactly one pair
      e['fields']['excerpt'] = exc[1:-1]
  return header, entries, errors


def validate_entries(entries, errors):
  '''One error line per defect in TICKED entries (spec §9 failure classes).
  Unticked entries are the declined record: parsed, never field-validated.
  Requiring sha on every capture IS the echo rule here — a specs-harvest
  capture's basis is always its introducing commit (spec §4.2).'''
  seen_ids = set()
  for e in entries:
    if e['id'] in seen_ids:
      errors.append(f'{e["id"]}: duplicate id')
    seen_ids.add(e['id'])
  for e in entries:
    if not e['ticked']:
      continue
    f = e['fields']
    # The primary-sha shape gate below can't reach (also …) locations:
    # their shas live in e['also'] tuples, not f['sha']. Same echo rule
    # (spec §4.2) for every recorded sha — but sha-less also lines are
    # legitimate grammar (pilot q-02), so only a present-but-malformed sha
    # errors. Checked before the q branch: q entries carry also lines
    # through render_digest_entry too.
    for loc, sha in e['also']:
      if sha is not None and not SHA_RE.fullmatch(sha):
        errors.append(f'{e["id"]}: also sha is not a commit hash')
    # Hoisted above the q branch for the same reason the also-sha gate is:
    # q claims are rendered into the digest by render_digest_entry too, so a
    # bracketed q claim fabricates a BODY_CITE_RE citation just like a
    # bracketed capture claim.
    if re.search(r'[\[\]]', f.get('claim', '')):
      errors.append(f'{e["id"]}: square brackets in claim '
                    '(BODY_CITE_RE discipline)')
    if e['prefix'] == 'q':
      for req in ('at', 'claim'):
        if not f.get(req):
          errors.append(f'{e["id"]}: missing {req}')
      continue
    if e['prefix'] not in KINDS:
      errors.append(f'{e["id"]}: unknown id prefix')
      continue
    for req in ('kind', 'boundary', 'at', 'sha', 'excerpt', 'claim'):
      if not f.get(req):
        errors.append(f'{e["id"]}: missing {req}')
    # Final-review finding 2: sha presence alone doesn't enforce the echo
    # rule (spec §4.2) -- `sha: TBD` passes the loop above and would ship as
    # `basis: git:TBD`. SHA_RE is the one shape both this gate and the
    # also-line gate above enforce.
    if f.get('sha') and not SHA_RE.fullmatch(f['sha']):
      errors.append(f'{e["id"]}: sha is not a commit hash')
    if f.get('kind') and f['kind'] != KINDS[e['prefix']]:
      errors.append(f'{e["id"]}: kind {f["kind"]} does not match prefix '
                    f'{e["prefix"]}')
    if f.get('boundary') and f['boundary'] not in BOUNDARIES:
      errors.append(f'{e["id"]}: unknown boundary {f["boundary"]}')
    if f.get('boundary') == 'code-coupled':
      errors.append(f'{e["id"]}: code-coupled entries must not be ticked '
                    '(engineering stratum waits for the code-wiki root)')


def _render_new_sections(repo, rels, seen):
  '''Shared per-file section-render loop (cmd_inventory's first pass and
  _extend_brief's accretion pass): read each file at repo_head, build its
  SHA table and seed hits, and render its `## ` section. One place for both
  callers so the is_deferred flag can't drift between them (review finding:
  the extend path once called seed_hits without it, so deferred_items.md
  rendered "- none" when it first entered the brief via that path).

  Raises RuntimeError naming the offending file when a spec file or its git
  history cannot be read: the brief lists every walked file or none at all
  (spec §7), so a mid-walk failure must reach the cmd_* caller as the house
  error line, not a traceback.'''
  body = []
  for rel in rels:
    try:
      text = (repo / rel).read_text()
    except (OSError, UnicodeDecodeError) as exc:
      raise RuntimeError(f'cannot read {rel}: {exc}') from exc
    try:
      shas = sha_table(repo, rel)
      olds = renamed_from(repo, rel)
    except (RuntimeError, OSError) as exc:
      raise RuntimeError(f'cannot read git history for {rel}: {exc}') from exc
    # prior briefs key their entries by the at:-path of the day, which is the
    # pre-rename name for anything retired since — order-preserving union so
    # the current path's hints stay first.
    prior_keys = list(seen.get(rel, []))
    for old in olds:
      prior_keys += [k for k in seen.get(old, []) if k not in prior_keys]
    body += render_file_section(rel, shas,
                                seed_hits(text, rel == DEFERRED_FILE),
                                prior_keys)
  return body


def _splice_notes(lines, notes):
  '''Regenerate the header's directory-presence note block in place.
  Regeneration, not accretion: a note that stopped being true (a WALK_DIRS
  dir that gained .md files) must leave, exactly as a newly-true one must
  arrive. -> True if the block changed.

  A brief with no closing '---' is malformed beyond this function's remit:
  leave it alone rather than raising ValueError out of cmd_inventory. The
  repo_head check above already rejects every brief this script did not
  write, so this is a belt-and-braces guard, not a supported input.'''
  if '---' not in lines[1:]:
    return False
  close = lines.index('---', 1)
  at = close + 1
  if at < len(lines) and lines[at] == '':
    at += 1
  start = at
  while at < len(lines) and lines[at].startswith('note: '):
    at += 1
  end = at
  if end > start and end < len(lines) and lines[end] == '':
    end += 1                       # the blank line closing an existing block
  block = [f'note: {n}' for n in notes]
  if block:
    block.append('')
  if lines[start:end] == block:
    return False
  lines[start:end] = block
  return True


def _extend_brief(path, repo, head, files, notes, seen):
  '''Same-date re-run (spec §7): append sections for files not yet present
  and refresh the directory-presence notes; never overwrite or duplicate.
  One brief = one repo_head.'''
  text = path.read_text()
  header, _, _ = parse_brief(text)
  if header.get('repo_head') != head:
    print(f'error: {path.name} pins repo_head {header.get("repo_head")} but '
          f'HEAD is {head}; use a fresh --date (or re-run at the pinned head)',
          file=sys.stderr)
    return 1
  have = set(re.findall(r'^## (.+)$', text, re.M))
  new = [f for f in files if f not in have]
  lines = text.rstrip('\n').split('\n')
  notes_changed = _splice_notes(lines, notes)
  if not new:
    if notes_changed:
      _atomic_write(path, '\n'.join(lines) + '\n')
      print(f'{path.name}: no new files; notes refreshed')
      return 0
    print(f'{path.name}: no new files; brief unchanged')
    return 0
  try:
    body = _render_new_sections(repo, new, seen)
  except RuntimeError as exc:
    print(f'error: {exc}; the brief lists every walked file or none',
          file=sys.stderr)
    return 1
  walked = [f.strip() for f in header.get('files_walked', '').split(';')
            if f.strip()]
  walked += [f for f in new if f not in walked]
  for i, line in enumerate(lines):
    if line == 'files_walked: >':
      # the block is EVERY two-space continuation line, not just the first:
      # parse_brief folds all of them into one value, so replacing one leaves
      # a stale tail that re-parses as duplicate walked files.
      j = i + 1
      while j < len(lines) and lines[j].startswith('  ') and lines[j].strip():
        j += 1
      lines[i + 1:j] = ['  ' + '; '.join(walked)]
      break
  _atomic_write(path, '\n'.join(lines) + '\n\n'
                + '\n'.join(body).rstrip('\n') + '\n')
  print(f'extended {path} (+{len(new)} files)')
  return 0


def render_digest_entry(e):
  '''One ground-truth digest block (pilot format). Redaction on everything
  that carries source text — the lint extension is only the backstop.
  Final-review finding 1: title/at/(also …) carry free-text repo content too
  (a spec section heading can itself embed a secret) -- redact() them here
  same as excerpt/claim/note (spec §7: redact() at assemble). kind/boundary/
  sha are left raw: closed vocabulary or shape-validated, never source text.'''
  f = e['fields']
  title = redact(e['title'])[0]
  at = redact(f['at'])[0]
  lines = [f'[{e["id"]}] {title}']
  if e['prefix'] == 'q':
    lines.append(f'at: {at}')
  else:
    lines.append(f'at: {at}{SEP}sha: {f["sha"]}')
  for loc, sha in e['also']:
    loc = redact(loc)[0]
    lines.append(f'  (also {loc}{SEP}sha: {sha})' if sha
                 else f'  (also {loc})')
  if e['prefix'] == 'q':
    lines.append(redact(f['claim'])[0])
  else:
    lines.append(f'excerpt: "{redact(f["excerpt"])[0]}"')
    if f.get('note'):
      lines.append(f'note: {redact(f["note"])[0]}')
  return '\n'.join(lines)


def render_digest(header, entries, brief_name):
  '''-> (stem, digest text). id8 hashes ONLY the ordered ticked entry
  blocks — not the header or preamble — so an unchanged brief re-assembles
  to the identical filename and bytes (spec §5.2).'''
  ticked = [e for e in entries if e['ticked']]
  caps = [e for e in ticked if e['prefix'] != 'q']
  qs = [e for e in ticked if e['prefix'] == 'q']
  blocks = [render_digest_entry(e) for e in caps + qs]
  id8 = hashlib.sha256('\n\n'.join(blocks).encode()).hexdigest()[:8]
  stem = f'{header["date"]}-{header["repo"]}-specs-{id8}'
  files = [f.strip() for f in header.get('files_walked', '').split(';')
           if f.strip()]
  n_total = sum(1 for e in entries if e['prefix'] != 'q')
  fm = [
    '---',
    'source: specs-harvest',
    f'repo: {header["repo"]}',
    f'repo_head: {header["repo_head"]}',
    f'date: {header["date"]}',
    f'files: {len(files)}',
    f'captures: {len(caps)}',
    f'open_questions: {len(qs)}',
    'note: >',
    f'  Assembled by distill_specs.py from {brief_name}: {len(caps)} '
    'ticked of',
    f'  {n_total} proposed captures; unticked entries remain in the brief as',
    '  the declined record.',
    f'brief: reports/{brief_name}',
    'files_read: >',
    '  ' + '; '.join(files),
    '---',
    '',
  ]
  if caps:
    fm += [
      f'Ground-truth entries for the capture notes in wiki/sources/{stem}.md.',
      f'Each entry: verbatim excerpt from the {header["repo"]} file at the',
      'stated location, introducing commit sha.',
      '',
    ]
  else:
    # No ticked captures: assemble creates no wiki/sources page for this
    # harvest, so the preamble must not send a reader to one.
    fm += [
      'Open questions only — this harvest produced no capture notes, and no',
      'wiki/sources page is created for it. Each entry: a question raised by',
      f'the {header["repo"]} specs at the stated location.',
      '',
    ]
  # '\n'.join leaves fm's trailing '' as a single newline; add one more so a
  # blank line separates the preamble from the first entry block.
  return stem, '\n'.join(fm) + '\n' + '\n\n'.join(blocks) + '\n'


def render_source_body(entries, repo_name):
  '''Capture-note body for the wiki/sources page (stdout; the agent wraps
  frontmatter and runs the normal ingest op — this script never writes under
  wiki/). q entries ride in the digest only; positions drop a trailing (L…)
  detail; (also …) locations are digest-only (spec §5.3, pilot). Final-review
  finding 1: this stdout body has no mechanical secret check downstream (the
  digest at least has the lint backstop), so title/at need redact() same as
  claim -- not just the digest side.'''
  blocks = []
  for e in entries:
    if not e['ticked'] or e['prefix'] == 'q':
      continue
    f = e['fields']
    pos = re.sub(r'\s*\(L[0-9–-]+\)$', '', f['at'])
    title = redact(e['title'])[0]
    pos = redact(pos)[0]
    blocks.append(f'### [{e["id"]}] {title}\n'
                  f'kind: {f["kind"]}{SEP}at: {repo_name} {pos}{SEP}'
                  f'basis: git:{f["sha"]}\n'
                  + redact(f['claim'])[0])
  # No blocks means no capture page: return nothing rather than a bare
  # newline the caller would print as an empty page body.
  return '\n\n'.join(blocks) + '\n' if blocks else ''


def _stamp_brief(brief, stem):
  lines = brief.read_text().split('\n')
  lines = [l for l in lines if not l.startswith('assembled: ')]
  close = lines.index('---', 1)
  lines.insert(close, f'assembled: {stem}')
  _atomic_write(brief, '\n'.join(lines))


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
    return _extend_brief(path, repo, head, files, notes, seen)
  body = render_brief_header(repo_name, repo, head, root, date, files, prior)
  body += [f'note: {n}' for n in notes]
  if notes:
    body.append('')
  try:
    body += _render_new_sections(repo, files, seen)
  except RuntimeError as exc:
    print(f'error: {exc}; the brief lists every walked file or none',
          file=sys.stderr)
    return 1
  _atomic_write(path, '\n'.join(body).rstrip('\n') + '\n')
  print(f'wrote {path}')
  return 0


def cmd_assemble(args):
  brief = Path(args.brief).resolve()
  root = Path(args.root).resolve()
  if not brief.is_file():
    print(f'error: brief not found: {brief}', file=sys.stderr)
    return 1
  header, entries, errors = parse_brief(brief.read_text())
  if header.get('root') != str(root):
    print(f'brief-error: root mismatch: brief says {header.get("root")}, '
          f'--root is {root} (wrong-wiki protection)', file=sys.stderr)
    return 1
  validate_entries(entries, errors)
  for key in REQUIRED_HEADER_KEYS:
    if not header.get(key):
      errors.append(f'brief: missing header key {key}')
  if not any(e['ticked'] for e in entries):
    errors.append('brief: no ticked entries')
  if errors:
    for err in errors:
      print(f'brief-error: {err}', file=sys.stderr)
    return 1
  repo_path = header.get('repo_path', '')
  if not repo_path:
    # Path('') is Path('.'): the check would run `git -C .` and report the
    # cwd's HEAD as a mismatch for a repo the brief never named.
    print('warning: cannot check drift (no repo_path in brief)',
          file=sys.stderr)
  else:
    try:
      head = _git(Path(repo_path), 'rev-parse', '--short', 'HEAD').strip()
      if head != header.get('repo_head'):
        print(f'warning: {header["repo"]} HEAD {head} != brief repo_head '
              f'{header["repo_head"]} — post-inventory edits are the wiki\'s '
              'dated-claims staleness, not re-harvested here',
              file=sys.stderr)
    except (RuntimeError, OSError):
      print(f'warning: cannot check drift ({repo_path} unavailable)',
            file=sys.stderr)
  stem, digest = render_digest(header, entries, brief.name)
  out = root / 'raw/specs' / f'{stem}.md'
  out.parent.mkdir(parents=True, exist_ok=True)
  _atomic_write(out, digest)
  _stamp_brief(brief, stem)
  print(render_source_body(entries, header['repo']), end='')
  if not any(e['ticked'] and e['prefix'] != 'q' for e in entries):
    print('note: no ticked captures — open questions only; the digest is the '
          'whole yield and there is no wiki/sources page to create',
          file=sys.stderr)
  print(f'wrote {out.relative_to(root)}', file=sys.stderr)
  return 0


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

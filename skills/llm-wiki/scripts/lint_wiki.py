'''Mechanical linter for the research-wiki (spec §10). Stdlib only; no yaml.'''
import argparse
import os
import re
import sys
from pathlib import Path

STRUCTURAL = {'index.md', 'log.md', 'open-questions.md'}
REQUIRED_KEYS = ('title', 'type', 'status', 'topics', 'updated')
TYPES = ('source', 'concept', 'synthesis')
STATUSES = ('unverified', 'verified')
INDEX_LINE_RE = re.compile(r'^- \[[^\]]+\]\(([^)]+)\)')
# Markdown relative links: [text](target) where target is not a URL/anchor.
MD_LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
# Structural shape of a body locator: [token position], and NOT a markdown
# link (no '(' immediately after the ']'). Shape only -- _is_citation decides
# whether a matched pair is actually a citation.
BODY_CITE_RE = re.compile(r'\[([A-Za-z0-9][A-Za-z0-9._-]*)\s+([^\]]+)\](?!\()')
# A position opens with a documented locator sigil, or a digit (SCHEMA.md
# "Body conventions"). These are prefix matches, so 'Table' also covers
# 'Tables' and 'Fig' covers 'Figure'/'Figs'; 'pp.' and 'Ch' are NOT accepted.
# Extend additively, against real content -- never speculatively: an
# unrecognized position silently makes the token prose, while a spurious one
# adds hard-ERROR surface.
POSITION_RE = re.compile(r'^(?:§|p\.|Table|Fig|Eq|\d)')
# A slug is multi-part: it carries a hyphen, or a 4-digit run (a year).
SLUG_SHAPE_RE = re.compile(r'-|\d{4}')
DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
LOG_DATE_RE = re.compile(r'^## \[(\d{4}-\d{2}-\d{2})\]', re.M)


def parse_frontmatter(text):
  '''Parse a leading --- ... --- block into a flat dict. Scalars are strings;
  single-line bracketed lists become list[str]. Returns None if no block.
  Inline # comments are not part of real frontmatter and are kept literal.'''
  m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
  if not m:
    return None
  fm = {}
  for line in m.group(1).split('\n'):
    if not line.strip() or ':' not in line:
      continue
    key, _, val = line.partition(':')
    key, val = key.strip(), val.strip()
    if val.startswith('[') and val.endswith(']'):
      inner = val[1:-1].strip()
      fm[key] = [v.strip() for v in inner.split(',') if v.strip()]
    else:
      fm[key] = val
  return fm


def discover_pages(root):
  '''Wiki content pages: one level under wiki/. Structural files live directly
  under wiki/ and are excluded.'''
  return sorted(
    p for p in (root / 'wiki').glob('*/*.md') if p.name not in STRUCTURAL)


def default_root():
  return Path(os.environ.get('LLM_WIKI_ROOT', str(Path.home() / 'research-wiki')))


def check_frontmatter_schema(root, pages):
  findings = []
  for p in pages:
    rel = p.relative_to(root)
    fm = parse_frontmatter(p.read_text())
    if fm is None:
      findings.append(('ERROR', str(rel), 'frontmatter: no --- block'))
      continue
    for k in REQUIRED_KEYS:
      if k not in fm:
        findings.append(('ERROR', str(rel), f'frontmatter: missing key {k!r}'))
    ptype = fm.get('type')
    if ptype not in TYPES:
      findings.append(('ERROR', str(rel), f'frontmatter: bad type {ptype!r}'))
    if fm.get('status') not in STATUSES:
      findings.append(
        ('ERROR', str(rel), f'frontmatter: bad status {fm.get("status")!r}'))
    if ptype == 'source':
      if 'raw' not in fm:
        findings.append(('ERROR', str(rel), 'frontmatter: source needs raw:'))
      if 'cites' in fm:
        findings.append(('ERROR', str(rel), 'frontmatter: source must not cites:'))
    elif ptype in ('concept', 'synthesis'):
      if 'cites' not in fm:
        findings.append(
          ('ERROR', str(rel), f'frontmatter: {ptype} needs cites:'))
      if 'raw' in fm:
        findings.append(
          ('ERROR', str(rel), f'frontmatter: {ptype} must not raw:'))
    for lk in ('topics', 'cites'):
      if lk in fm and not isinstance(fm[lk], list):
        findings.append(
          ('ERROR', str(rel), f'frontmatter: {lk} must be a bracketed list'))
  return findings


def _index_targets(root):
  '''Set of index-line targets (paths relative to wiki/, e.g. sources/a.md).
  A #fragment is stripped, matching check_links: SCHEMA.md does not prohibit
  an index deep-link, and the divergence between the two code paths was the
  bug. Duplicate detection inherits this -- two lines into the same page
  collapse to one target.'''
  idx = root / 'wiki/index.md'
  if not idx.exists():
    return []
  out = []
  for line in idx.read_text().split('\n'):
    m = INDEX_LINE_RE.match(line.strip())
    if m:
      out.append(m.group(1).split('#', 1)[0])
  return out


def check_index_parity(root, pages):
  findings = []
  page_rels = {str(p.relative_to(root / 'wiki')) for p in pages}
  targets = _index_targets(root)
  target_set = set(targets)
  for rel in sorted(page_rels - target_set):
    findings.append(('ERROR', f'wiki/{rel}', 'index: page has no index line'))
  for t in targets:
    if t not in page_rels:
      findings.append(('ERROR', 'wiki/index.md', f'index: line target missing page: {t}'))
  # duplicate index lines for the same page
  for t in target_set:
    if targets.count(t) > 1:
      findings.append(('ERROR', 'wiki/index.md', f'index: duplicate line for {t}'))
  return findings


def _source_slugs(root):
  return {p.stem for p in (root / 'wiki/sources').glob('*.md')}


def _strip_frontmatter(text):
  m = re.match(r'^---\n.*?\n---\n', text, re.S)
  return text[m.end():] if m else text


def _looks_like_position(rest):
  '''Is the text after the token a locator position?'''
  return bool(POSITION_RE.match(rest.strip()))


def _is_citation(token, position, slugs):
  '''Recognition, kept separate from resolution: a [token position] pair is a
  citation when the position looks like one AND the token either is shaped like
  a slug or names a known source page. The membership clause lets a single-word
  slug (`mclmc`) stay citable without loosening the structural clause, and it
  can never manufacture an error -- a token in `slugs` resolves by
  construction. All error risk therefore sits in the structural clause.'''
  if not _looks_like_position(position):
    return False
  return bool(SLUG_SHAPE_RE.search(token)) or token in slugs


def check_links(root, pages):
  findings = []
  slugs = _source_slugs(root)
  referenced = set()  # page paths (relative to wiki/) that something points at
  wiki_abs = (root / 'wiki').resolve()
  for p in pages:
    rel = p.relative_to(root)
    text = p.read_text()
    fm = parse_frontmatter(text) or {}
    body = _strip_frontmatter(text)
    # cites: frontmatter counts as an inbound reference to the cited source page
    cites = fm.get('cites')
    if isinstance(cites, list):
      for target in cites:
        referenced.add(target + '.md')
    # body markdown links must resolve; a resolved wiki target is inbound
    for target in MD_LINK_RE.findall(body):
      if target.startswith(('http://', 'https://', 'mailto:', '#')):
        continue
      resolved = (p.parent / target.split('#', 1)[0]).resolve()
      if not resolved.exists():
        findings.append(('ERROR', str(rel), f'link: broken relative link: {target}'))
      else:
        try:
          referenced.add(str(resolved.relative_to(wiki_abs)))
        except ValueError:
          pass
    # body citation locators [slug §x] must map to a source page; and count
    # as an inbound reference to it. Bracketed prose is not a citation and is
    # neither validated nor counted.
    for token, position in BODY_CITE_RE.findall(body):
      if not _is_citation(token, position, slugs):
        continue
      if token in slugs:
        referenced.add(f'sources/{token}.md')
      else:
        findings.append(
          ('ERROR', str(rel), f'citation: [{token} …] has no source page'))
  # orphan warning: a page nothing references (via link, cites, or locator)
  for p in pages:
    relw = str(p.relative_to(root / 'wiki'))
    if relw not in referenced:
      findings.append(('WARN', str(p.relative_to(root)), 'orphan: no inbound links'))
  return findings


def check_quarantine(root, pages):
  findings = []
  for p in pages:
    rel = p.relative_to(root)
    fm = parse_frontmatter(p.read_text()) or {}
    cites = fm.get('cites')
    if not isinstance(cites, list):
      continue
    for target in cites:
      cited = root / 'wiki' / (target + '.md')
      if not cited.exists():
        findings.append(
          ('ERROR', str(rel), f'cites: target page missing: {target}'))
        continue
      cfm = parse_frontmatter(cited.read_text()) or {}
      if cfm.get('type') != 'source':
        findings.append(
          ('ERROR', str(rel), f'cites: {target} is not type: source'))
      if cfm.get('status') != 'verified':
        findings.append(
          ('ERROR', str(rel), f'cites: {target} is not status: verified'))
  return findings


# Secret-shaped strings. BACKSTOP for distill_sessions.py redaction (Plan 14):
# keep this set at least as broad as the distiller's, so a residual secret in a
# distilled digest is always caught here.
SECRET_PATTERNS = [
  # (?<![A-Za-z0-9]) so 'sk-' only matches at a token start -- without it
  # ordinary prose like 'task-reviewer-...' / 'risk-adjusted-...' scores as a key.
  ('openai-key', re.compile(r'(?<![A-Za-z0-9])sk-(?:proj-)?[A-Za-z0-9_-]{20,}')),
  ('github-token', re.compile(r'ghp_[A-Za-z0-9]{30,}')),
  ('github-pat', re.compile(r'github_pat_[A-Za-z0-9_]{50,}')),
  ('aws-key', re.compile(r'AKIA[0-9A-Z]{16}')),
  ('pem-block', re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')),
  ('assignment', re.compile(
    r'(?i)(password|secret|token)\s*[:=]\s*[\'"]?[A-Za-z0-9/+_-]{12,}')),
]
# `kind: decision` capture metadata line must carry an approved basis.
# Leading whitespace and a markdown list bullet are tolerated: an indented or
# bulleted capture is still a decision line, and anchoring hard at column 0
# silently disabled the basis check for it.
DECISION_META_RE = re.compile(
  r'^[ \t]*(?:[-*+][ \t]+)?kind:\s*decision\b(.*)$', re.M)
BASIS_OK_RE = re.compile(r'basis:\s*(user-turn|git:[0-9a-f]{7,40})')


def check_sessions(root):
  '''Secret + decision-basis backstop over the distilled raw classes:
  raw/sessions/ (session digests, spec §16.3) and raw/specs/ (specs-harvest
  digests, specs-harvest framework §4.3).'''
  findings = []
  for sub in ('raw/sessions', 'raw/specs'):
    class_dir = root / sub
    if not class_dir.exists():
      continue
    for p in sorted(class_dir.glob('*.md')):
      rel = p.relative_to(root)
      text = p.read_text()
      for cls, pat in SECRET_PATTERNS:
        if pat.search(text):
          findings.append(
            ('ERROR', str(rel), f'secret: {cls}-shaped string present'))
      for m in DECISION_META_RE.finditer(text):
        if not BASIS_OK_RE.search(m.group(1)):
          findings.append(
            ('ERROR', str(rel),
             'basis: kind: decision needs basis: user-turn or git:<sha>'))
      if sub == 'raw/specs':
        findings += _check_spec_decisions(text, rel)
  return findings


# Specs-harvest echo rule: a [d-NN] ground-truth entry's basis is its
# introducing commit — its block must carry `· sha: <hex>` on an at: line.
SPEC_ENTRY_SPLIT_RE = re.compile(r'\n(?=\[[a-z]-\d)')
SPEC_AT_SHA_RE = re.compile(r'^at: .+ · sha: [0-9a-f]{7,40}(?:\s|$)', re.M)


def _check_spec_decisions(text, rel):
  findings = []
  for block in SPEC_ENTRY_SPLIT_RE.split(text):
    m = re.match(r'\[(d-\d+)\]', block)
    if m and not SPEC_AT_SHA_RE.search(block):
      findings.append(
        ('ERROR', str(rel),
         f'basis: [{m.group(1)}] needs an at: line with sha: <sha>'))
  return findings


def _last_log_date(root):
  log = root / 'wiki/log.md'
  if not log.exists():
    return None
  dates = LOG_DATE_RE.findall(log.read_text())
  return max(dates) if dates else None


def check_cadence_and_scale(root, pages):
  findings = []
  # warning: newest page `updated` newer than last log entry
  updates = []
  for p in pages:
    fm = parse_frontmatter(p.read_text()) or {}
    if isinstance(fm.get('updated'), str) and DATE_RE.fullmatch(fm['updated']):
      updates.append(fm['updated'])
  last_log = _last_log_date(root)
  if updates and last_log and max(updates) > last_log:
    findings.append(
      ('WARN', 'wiki/log.md',
       f'log: newest page updated {max(updates)} > last log {last_log}'))
  # info: raw file (non-.gitkeep) with no source page of the same stem
  source_stems = {p.stem for p in (root / 'wiki/sources').glob('*.md')}
  raw_files = [f for f in (root / 'raw').rglob('*')
               if f.is_file() and f.suffix not in ('', '.gitkeep')
               and f.name != '.gitkeep']
  for f in raw_files:
    if f.parent.name == 'assets':
      continue
    if f.stem not in source_stems:
      findings.append(
        ('INFO', str(f.relative_to(root)), f'backlog: raw file {f.name} has no source page'))
  # info: soft ceiling
  n_pages = len(pages)
  n_sources = len(source_stems)
  if n_pages > 120 or n_sources > 100:
    findings.append(
      ('INFO', 'wiki/', f'scale: {n_pages} pages, {n_sources} sources — revisit qmd'))
  return findings


def run_checks(root):
  '''Return a list of (severity, path, message) findings.'''
  findings = []
  pages = discover_pages(root)
  findings += check_frontmatter_schema(root, pages)
  findings += check_index_parity(root, pages)
  findings += check_links(root, pages)
  findings += check_quarantine(root, pages)
  findings += check_sessions(root)
  findings += check_cadence_and_scale(root, pages)
  return findings


def main(argv=None):
  ap = argparse.ArgumentParser(description='Mechanical linter for research-wiki.')
  ap.add_argument('--strict', action='store_true',
                  help='warnings also cause a non-zero exit')
  ap.add_argument('root', nargs='?', default=None,
                  help='wiki root (default $LLM_WIKI_ROOT or ~/research-wiki)')
  args = ap.parse_args(argv)
  root = Path(args.root) if args.root else default_root()
  findings = run_checks(root)
  errors = sum(1 for f in findings if f[0] == 'ERROR')
  warnings = sum(1 for f in findings if f[0] == 'WARN')
  infos = sum(1 for f in findings if f[0] == 'INFO')
  for sev, path, msg in findings:
    print(f'{sev}  {path}  {msg}')
  print(f'{errors} errors, {warnings} warnings, {infos} info')
  if errors or (args.strict and warnings):
    return 1
  return 0


if __name__ == '__main__':
  sys.exit(main())

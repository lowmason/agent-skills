#!/usr/bin/env python3
# /// script
# requires-python = '>=3.11'
# dependencies = [
#   'polars>=1.0',
#   'fastexcel>=0.12',
# ]
# ///
'''Build the classification-codes data files from official Census (NAICS) and BLS (SOC) sources.

Downloads the pinned source workbooks into sources/ (kept as the audit copy — commit them; Census
and BLS move URLs and overwrite files in place), parses them into tidy, greppable CSVs under
data/, validates structure (sector/major-group counts, hierarchy closure, duplicate codes,
concordance referential integrity), and writes MANIFEST.md recording source URL, sha256, and
retrieval time for every artifact on disk.

Layout quirks these files are known for — preamble and legend rows above the header, ranged
sector codes ('31-33'), trilateral 'T' markers appended to NAICS titles (often followed by a
trailing space), numeric cells that surface as '111110.0', one-populated-code-column-per-row SOC
structure sheets — are handled here so the CSVs stay boring. Header and column detection is
deliberately fuzzy (substring match on a row with at least two populated cells), and every parse
is backed by hard validations, so a silent Census/BLS format change fails the build loudly
rather than corrupting data/.

Usage:
  uv run skills/classification-codes/scripts/build.py
  uv run skills/classification-codes/scripts/build.py --only naics_2022 --only naics_2017_to_2022
  uv run skills/classification-codes/scripts/build.py --offline          # rebuild from sources/ cache
  uv run skills/classification-codes/scripts/build.py --refresh          # force re-download
  uv run skills/classification-codes/scripts/build.py --list             # show the registry

bls.gov admits scripted downloads only when the User-Agent carries a contact email (it answers
an Akamai "Access Denied" page, HTTP 403, otherwise, and also to any User-Agent containing
tokens such as "github.com" or "python-requests"). Export BLS_CONTACT_EMAIL — the same variable
the bls-stats transport layer uses — before building the SOC artifacts; without it the build
refuses to contact bls.gov and tells you to either set it or save the workbook from a browser
into sources/ under its original filename, after which the cached copy is used. A blocked or
failed download skips that artifact, records the reason as a validation problem, and lets the
rest of the build proceed.

If a download 404s, Census/BLS reorganized their site: find the file on census.gov/naics
(downloadables) or bls.gov/soc and update BUILDS below — nothing else should need to change.
'''

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from typing import Callable

import polars as pl

# bls.gov's bot filter admits a script only if its User-Agent carries a contact email, and it
# rejects User-Agents containing "github.com" or "python-requests" even with one (each form
# verified 2026-09-02). Variable name and UA shape follow the bls-stats transport layer.
CONTACT_EMAIL_VAR = 'BLS_CONTACT_EMAIL'
CONTACT_HOSTS = ('bls.gov',)

NAICS_STRUCTURE_RE = r'^(\d{2}(-\d{2})?|\d{3,6})$'
NAICS_6_RE = r'^\d{6}$'
SOC_RE = r'^\d{2}-?\d{4}$'
SOC_LEVELS = ('major', 'minor', 'broad', 'detailed')
# Census "Change Indicator" markers, as published; the legend is vintage-specific and lives in
# SKILL.md. Anything else in that column means the layout changed.
NAICS_CHANGE_INDICATORS = ('*', '**', '***', '****')


# --------------------------------------------------------------------------------------------
# Generic helpers
# --------------------------------------------------------------------------------------------


def source_filename(url: str) -> str:
  '''The filename a URL is cached under in sources/ — the unquoted last path segment.'''
  return urllib.parse.unquote(Path(urllib.parse.urlparse(url).path).name)


def contact_email() -> str | None:
  return os.environ.get(CONTACT_EMAIL_VAR, '').strip() or None


def user_agent(email: str | None) -> str:
  base = 'classification-codes-build/0.1 (agent-skills reference data'
  return f'{base}; contact: {email})' if email else f'{base})'


def needs_contact_email(url: str) -> bool:
  host = urllib.parse.urlparse(url).netloc.lower()
  return any(host == known or host.endswith(f'.{known}') for known in CONTACT_HOSTS)


def fetch(url: str, sources_dir: Path, offline: bool, refresh: bool) -> tuple[Path, str, str]:
  '''Download url into sources_dir (or reuse the cached copy); return (path, sha256, retrieved).'''
  sources_dir.mkdir(parents=True, exist_ok=True)
  dest = sources_dir / source_filename(url)
  host = urllib.parse.urlparse(url).netloc
  if dest.exists() and not refresh:
    retrieved = datetime.fromtimestamp(dest.stat().st_mtime, tz=timezone.utc).isoformat(timespec='seconds')
  elif offline:
    raise FileNotFoundError(f'--offline set but {dest} is not cached')
  else:
    email = contact_email()
    if needs_contact_email(url) and not email:
      raise RuntimeError(
        f'{host} admits scripted downloads only with a contact email in the User-Agent: export '
        f'{CONTACT_EMAIL_VAR}=you@example.org and re-run, or save {url} from a browser as {dest}.'
      )
    request = urllib.request.Request(url, headers={'User-Agent': user_agent(email)})
    try:
      with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()
    except urllib.error.HTTPError as error:
      if error.code == 403:
        raise RuntimeError(
          f'{host} refused the scripted download (HTTP 403) despite the contact User-Agent. Save '
          f'{url} from a browser as {dest} and re-run; the cached copy is used automatically.'
        ) from error
      raise RuntimeError(
        f'Download failed for {url} (HTTP {error.code}). Census/BLS reorganize their sites '
        f'periodically; locate the file via census.gov/naics or bls.gov/soc and update BUILDS.'
      ) from error
    except urllib.error.URLError as error:
      raise RuntimeError(f'Download failed for {url} ({error.reason}).') from error
    dest.write_bytes(payload)
    retrieved = datetime.now(timezone.utc).isoformat(timespec='seconds')
  sha256 = hashlib.sha256(dest.read_bytes()).hexdigest()
  return dest, sha256, retrieved


def read_sheet(path: Path, sheet: str | None = None) -> pl.DataFrame:
  '''One worksheet (the first unless named) with every cell as Utf8 and no header; header
  detection happens downstream because these workbooks carry preamble, legend, and footnote
  rows. Reading as strings keeps codes textual at the source ('0010', not 10.0) and silences
  fastexcel's dtype-inference chatter.'''
  sheet_kwargs = {'sheet_name': sheet} if sheet else {}
  with warnings.catch_warnings():
    # polars-internal: read_excel's calamine path calls from_arrow itself
    # (polars/io/spreadsheet/functions.py:1106), and stacklevel pins the warning to this
    # call. read_excel is declared -> DataFrame and relies on one internally (it sets
    # df.columns and drops null rows/cols right after), so there is no call-site fix and
    # 2.0 must fix it upstream. Matched on message so other read_excel deprecations still
    # surface.
    warnings.filterwarnings('ignore', message='from_arrow', category=FutureWarning)
    raw = pl.read_excel(path, has_header=False, read_options={'dtypes': 'string'}, **sheet_kwargs)
  return raw.select(pl.all().cast(pl.Utf8))


def frame_below_header(raw: pl.DataFrame, needles: list[str], min_cells: int = 2) -> pl.DataFrame:
  '''Slice off everything above the first row that has at least min_cells populated cells and
  whose cells jointly contain all needles (case-insensitive); use that row as column names.

  The populated-cell floor is what keeps title and legend rows from masquerading as the header:
  Census note rows are a single long cell that happens to mention both vintages and the word
  "code", whereas a real header spreads the needles across several cells.
  '''
  targets = [needle.lower() for needle in needles]
  for index, row in enumerate(raw.rows()):
    cells = [str(cell) for cell in row if cell is not None and str(cell).strip()]
    if len(cells) < min_cells:
      continue
    joined = ' | '.join(cell.lower() for cell in cells)
    if all(target in joined for target in targets):
      names, seen = [], {}
      for position, cell in enumerate(row):
        name = str(cell).strip() if cell is not None and str(cell).strip() else f'col_{position}'
        seen[name] = seen.get(name, 0) + 1
        names.append(name if seen[name] == 1 else f'{name}_{seen[name]}')
      body = raw.slice(index + 1)
      body.columns = names
      return body
  raise ValueError(f'No header row containing all of {needles!r}; the source layout changed.')


def find_col(columns: list[str], *needles: str) -> str:
  '''First column whose header NAME LINE contains every needle (case-insensitive).

  Only the first line of a header cell counts: Census puts explanatory notes on the lines below
  the name ("2017 NAICS Title\\n(... contained in the 2022 industry)"), and matching the whole
  cell would return the 2017 title column for ('2022', 'title').
  '''
  for column in columns:
    name_line = column.split('\n', 1)[0].lower()
    if all(needle.lower() in name_line for needle in needles):
      return column
  raise ValueError(f'No column matching {needles!r} among {columns!r}; the source layout changed.')


def pick_title_col(body: pl.DataFrame, exclude: set[str]) -> str:
  '''The non-code column with the longest average text — used when the title column arrives with a
  blank or unexpected header.'''
  best_name, best_length = None, -1.0
  for column in body.columns:
    if column in exclude:
      continue
    values = body.get_column(column).drop_nulls()
    if values.is_empty():
      continue
    mean_length = values.str.len_chars().mean()
    if mean_length is not None and mean_length > best_length:
      best_name, best_length = column, mean_length
  if best_name is None:
    raise ValueError('Could not identify a title column; the source layout changed.')
  return best_name


def code_expr(column: str) -> pl.Expr:
  '''Normalize a code cell: strings pass through, Excel numerics lose their trailing ".0".'''
  return pl.col(column).cast(pl.Utf8).str.strip_chars().str.replace(r'\.0$', '')


def title_expr(column: str) -> pl.Expr:
  return pl.col(column).cast(pl.Utf8).str.strip_chars()


def strip_trilateral_marker(expr: pl.Expr) -> pl.Expr:
  '''Drop a Census superscript-T marker from the end of a (stripped) title. Requiring a lowercase
  letter or ")" before the T keeps acronym-final titles from false-positives.'''
  return expr.str.replace(r'([a-z)])T$', '${1}')


def hyphenate_soc(expr: pl.Expr) -> pl.Expr:
  '''Canonicalize a SOC code to the hyphenated XX-YYYY form.'''
  return expr.str.replace(r'^(\d{2})(\d{4})$', '${1}-${2}')


def link_type_exprs(source_col: str, target_col: str) -> list[pl.Expr]:
  '''Classify each concordance row from code multiplicities: 1:1 (stable or clean recode),
  1:m (the source splits; this target has one source), m:1 (this source is whole; the target
  merges), m:m (both). Only 1:1 rows bridge mechanically.'''
  n_targets = pl.col(target_col).count().over(source_col)
  n_sources = pl.col(source_col).count().over(target_col)
  link = (
    pl.when(n_targets.gt(1).and_(n_sources.gt(1))).then(pl.lit('m:m'))
    .when(n_targets.gt(1)).then(pl.lit('1:m'))
    .when(n_sources.gt(1)).then(pl.lit('m:1'))
    .otherwise(pl.lit('1:1'))
  )
  return [link.alias('link_type')]


# --------------------------------------------------------------------------------------------
# NAICS
# --------------------------------------------------------------------------------------------


def parse_naics_structure(raw: pl.DataFrame, vintage: int) -> pl.DataFrame:
  '''Census "<vintage>_NAICS_Structure" workbook -> code, level, title, parent_code, sector_code,
  trilateral, change_indicator.

  Sector codes stay in their official ranged form ('31-33', '44-45', '48-49'); every descendant
  carries the resolved sector in sector_code, which is the column to group and filter on —
  code[:2] is never sector-safe. Trilateral rows are the Census superscript-T lines (comparable
  across the three NAICS countries); the marker is stripped from the stored title.
  change_indicator carries the Census asterisk marker verbatim (null = unchanged from the prior
  vintage at this level); the legend differs by vintage and is documented in SKILL.md.
  '''
  body = frame_below_header(raw, [str(vintage), 'code', 'title'])
  code_col = find_col(body.columns, 'code')
  title_col = find_col(body.columns, 'title')
  change_col = find_col(body.columns, 'change')
  frame = (
    body
    .select(
      code=code_expr(code_col),
      title=title_expr(title_col),
      change_indicator=pl.col(change_col).cast(pl.Utf8).str.strip_chars(),
    )
    .filter(pl.col('code').str.contains(NAICS_STRUCTURE_RE))
    .unique(subset='code', keep='first', maintain_order=True)
    .with_columns(
      change_indicator=pl.when(pl.col('change_indicator').eq('')).then(None).otherwise(pl.col('change_indicator')),
      trilateral=pl.col('title').str.contains(r'[a-z)]T$'),
    )
    .with_columns(
      title=strip_trilateral_marker(pl.col('title')),
      level=pl.when(pl.col('code').str.contains('-'))
      .then(pl.lit(2))
      .otherwise(pl.col('code').str.len_chars())
      .cast(pl.Int64),
    )
  )
  prefix_to_sector: dict[str, str] = {}
  for sector in frame.filter(pl.col('level').eq(2)).get_column('code'):
    if '-' in sector:
      low, high = sector.split('-')
      for prefix in range(int(low), int(high) + 1):
        prefix_to_sector[f'{prefix:02d}'] = sector
    else:
      prefix_to_sector[sector] = sector
  return (
    frame
    .with_columns(
      sector_code=pl.col('code').str.slice(0, 2)
      .replace_strict(prefix_to_sector, default=None, return_dtype=pl.Utf8)
    )
    .with_columns(
      parent_code=pl.when(pl.col('level').eq(2)).then(pl.lit(None, dtype=pl.Utf8))
      .when(pl.col('level').eq(3)).then(pl.col('sector_code'))
      .otherwise(pl.col('code').str.slice(0, pl.col('level').sub(1)))
    )
    .select('code', 'level', 'title', 'parent_code', 'sector_code', 'trilateral', 'change_indicator')
    .sort('code')  # lexical order on NAICS codes is hierarchical order
  )


def validate_naics(frame: pl.DataFrame, vintage: int) -> list[str]:
  problems = []
  sectors = frame.filter(pl.col('level').eq(2)).height
  if sectors != 20:
    problems.append(f'naics_{vintage}: expected 20 sectors, found {sectors}')
  six_digit = frame.filter(pl.col('level').eq(6)).height
  if not 900 <= six_digit <= 1200:
    problems.append(f'naics_{vintage}: {six_digit} six-digit codes is outside the plausible 900-1200 band')
  duplicates = frame.filter(pl.col('code').is_duplicated()).height
  if duplicates:
    problems.append(f'naics_{vintage}: {duplicates} duplicated codes')
  known = frame.get_column('code').to_list()
  orphans = frame.filter(
    pl.col('parent_code').is_not_null().and_(pl.col('parent_code').is_in(known).not_())
  ).height
  if orphans:
    problems.append(f'naics_{vintage}: {orphans} rows whose parent_code is missing from the file')
  unmapped = frame.filter(pl.col('sector_code').is_null()).height
  if unmapped:
    problems.append(f'naics_{vintage}: {unmapped} rows with no resolved sector_code')
  unknown_markers = frame.filter(
    pl.col('change_indicator').is_not_null()
    .and_(pl.col('change_indicator').is_in(list(NAICS_CHANGE_INDICATORS)).not_())
  ).height
  if unknown_markers:
    problems.append(f'naics_{vintage}: {unknown_markers} rows with a change_indicator outside {NAICS_CHANGE_INDICATORS}')
  trilateral_leaves = frame.filter(pl.col('level').eq(6).and_(pl.col('trilateral'))).height
  if trilateral_leaves:
    problems.append(f'naics_{vintage}: {trilateral_leaves} six-digit codes flagged trilateral (national detail never is)')
  return problems


def parse_naics_concordance(raw: pl.DataFrame, source_vintage: int, target_vintage: int) -> pl.DataFrame:
  '''Census concordance workbook -> six-digit source/target pairs with a derived link_type.

  The official files flag partial flows by cell formatting (bold / italics) and carry no
  allocation weights: link_type is derived purely from code multiplicities after deduplication.
  '''
  body = frame_below_header(raw, [str(source_vintage), str(target_vintage), 'code'])
  source_code = find_col(body.columns, str(source_vintage), 'code')
  target_code = find_col(body.columns, str(target_vintage), 'code')
  source_title = find_col(body.columns, str(source_vintage), 'title')
  target_title = find_col(body.columns, str(target_vintage), 'title')
  return (
    body
    .select(
      **{
        f'naics_{source_vintage}': code_expr(source_code),
        f'title_{source_vintage}': strip_trilateral_marker(title_expr(source_title)),
        f'naics_{target_vintage}': code_expr(target_code),
        f'title_{target_vintage}': strip_trilateral_marker(title_expr(target_title)),
      }
    )
    .filter(
      pl.col(f'naics_{source_vintage}').str.contains(NAICS_6_RE)
      .and_(pl.col(f'naics_{target_vintage}').str.contains(NAICS_6_RE))
    )
    .unique(maintain_order=True)
    .with_columns(link_type_exprs(f'naics_{source_vintage}', f'naics_{target_vintage}'))
    .sort(f'naics_{source_vintage}', f'naics_{target_vintage}')
  )


def validate_naics_concordance(frame: pl.DataFrame, source_vintage: int, target_vintage: int) -> list[str]:
  problems = []
  if not 800 <= frame.height <= 2000:
    problems.append(
      f'naics_{source_vintage}_to_{target_vintage}: {frame.height} rows is outside the plausible 800-2000 band'
    )
  return problems


# --------------------------------------------------------------------------------------------
# SOC
# --------------------------------------------------------------------------------------------


def soc_pattern_level() -> pl.Expr:
  '''Aggregation level from the trailing-zero pattern of the digits — the SOC coding rule
  (XX-0000 major, ...00 minor, ...0 broad, else detailed). Used as a cross-check against the
  column each code arrived in.'''
  digits = pl.col('code').str.replace('-', '')
  return (
    pl.when(digits.str.ends_with('0000')).then(pl.lit('major'))
    .when(digits.str.ends_with('00')).then(pl.lit('minor'))
    .when(digits.str.ends_with('0')).then(pl.lit('broad'))
    .otherwise(pl.lit('detailed'))
  )


def soc_stem(expr: pl.Expr) -> pl.Expr:
  '''Digits with the hyphen and trailing zeros removed — the part of a SOC code that carries
  hierarchy. Stems, not fixed-width slices, because minor groups mix XX-Y000 and XX-YY00
  granularity (broad 51-9190 belongs to minor 51-9000, not to a nonexistent 51-9100).'''
  return expr.str.replace('-', '').str.strip_chars_end('0')


def soc_parents(frame: pl.DataFrame) -> pl.DataFrame:
  '''parent_code from the sheet's own nesting, cross-checked against the code pattern.

  The BLS structure sheet is a hierarchical listing: a code's parent is the nearest code of the
  next level up listed above it (hence the `row` column). That listing is the authority — the
  2018 SOC overflows the positional pattern (29-1221 through 29-1229 sit under broad group
  29-1210 Physicians; there is no 29-1220), so prefix logic alone leaves orphans. The
  longest-stem-prefix rule is kept as a cross-check: where both rules produce a parent they must
  agree, or the sheet is mis-ordered / the pattern changed and the build stops. Where only one
  rule produces a parent, it is used.
  '''
  depth = {level: index for index, level in enumerate(SOC_LEVELS)}
  by_nesting: dict[str, str | None] = {}
  current: dict[str, str] = {}
  for code, level in frame.sort('row').select('code', 'level').iter_rows():
    index = depth[level]
    by_nesting[code] = current.get(SOC_LEVELS[index - 1]) if index else None
    current[level] = code
    for deeper in SOC_LEVELS[index + 1:]:
      current.pop(deeper, None)

  stems = {
    level: [
      (code, code.replace('-', '').rstrip('0'))
      for code in frame.filter(pl.col('level').eq(level)).get_column('code')
    ]
    for level in SOC_LEVELS
  }
  by_stem: dict[str, str | None] = {}
  for index, level in enumerate(SOC_LEVELS):
    candidates = stems[SOC_LEVELS[index - 1]] if index else []
    for code, stem in stems[level]:
      matches = [(parent, parent_stem) for parent, parent_stem in candidates if stem.startswith(parent_stem)]
      by_stem[code] = max(matches, key=lambda pair: len(pair[1]))[0] if matches else None

  conflicts = [
    (code, nested, by_stem[code])
    for code, nested in by_nesting.items()
    if nested and by_stem[code] and nested != by_stem[code]
  ]
  if conflicts:
    raise ValueError(
      f'{len(conflicts)} codes whose sheet nesting conflicts with their code pattern '
      f'(code, nesting parent, pattern parent), e.g. {conflicts[:3]}; the source layout changed.'
    )
  parent_of = {code: nested or by_stem[code] for code, nested in by_nesting.items()}
  return frame.with_columns(
    parent_code=pl.col('code').replace_strict(parent_of, default=None, return_dtype=pl.Utf8)
  )


def parse_soc_structure(raw: pl.DataFrame, vintage: int) -> pl.DataFrame:
  '''BLS SOC structure workbook -> code, level, title, parent_code.

  The sheet carries one code column per aggregation level with exactly one populated per row;
  the populated column names the level, which is authoritative. Codes are canonicalized to the
  hyphenated XX-YYYY form. Disagreements with the trailing-zero pattern rule are warned, not
  fatal, since the official structure wins.
  '''
  body = frame_below_header(raw, ['major group'])
  level_cols = {
    'major': find_col(body.columns, 'major'),
    'minor': find_col(body.columns, 'minor'),
    'broad': find_col(body.columns, 'broad'),
    'detailed': find_col(body.columns, 'detailed'),
  }
  title_col = pick_title_col(body, exclude=set(level_cols.values()))
  body = body.with_row_index('row')  # sheet order carries the nesting; see soc_parents
  parts = [
    body
    .select('row', code=code_expr(column), title=title_expr(title_col))
    .filter(pl.col('code').str.contains(SOC_RE))
    .with_columns(code=hyphenate_soc(pl.col('code')), level=pl.lit(level))
    for level, column in level_cols.items()
  ]
  frame = (
    pl.concat(parts)
    .unique(subset='code', keep='first', maintain_order=True)
    .pipe(soc_parents)
    .select('code', 'level', 'title', 'parent_code')
    .sort('code')
  )
  disagreements = frame.filter(soc_pattern_level().ne(pl.col('level'))).height
  if disagreements:
    print(
      f'  warning: soc_{vintage}: {disagreements} codes whose column-assigned level disagrees '
      f'with the trailing-zero pattern; keeping the column assignment'
    )
  overflow = frame.filter(
    pl.col('parent_code').is_not_null()
    .and_(soc_stem(pl.col('code')).str.starts_with(soc_stem(pl.col('parent_code'))).not_())
  )
  if overflow.height:
    pairs = ', '.join(f'{code}→{parent}' for code, parent in overflow.select('code', 'parent_code').iter_rows())
    print(f'  note: soc_{vintage}: {overflow.height} codes parented by sheet nesting, not code pattern: {pairs}')
  return frame


def validate_soc(frame: pl.DataFrame, vintage: int) -> list[str]:
  problems = []
  majors = frame.filter(pl.col('level').eq('major')).height
  if majors != 23:
    problems.append(f'soc_{vintage}: expected 23 major groups, found {majors}')
  detailed = frame.filter(pl.col('level').eq('detailed')).height
  if not 750 <= detailed <= 950:
    problems.append(f'soc_{vintage}: {detailed} detailed occupations is outside the plausible 750-950 band')
  duplicates = frame.filter(pl.col('code').is_duplicated()).height
  if duplicates:
    problems.append(f'soc_{vintage}: {duplicates} duplicated codes')
  orphans = frame.filter(
    pl.col('level').ne('major').and_(pl.col('parent_code').is_null())
  ).height
  if orphans:
    problems.append(f'soc_{vintage}: {orphans} non-major codes with no resolvable parent')
  return problems


def parse_soc_crosswalk(raw: pl.DataFrame, source_vintage: int, target_vintage: int) -> pl.DataFrame:
  '''BLS SOC crosswalk workbook -> hyphenated source/target pairs with a derived link_type.

  BLS appends "(#)" to a source title whose code splits and "(##)" to a target title whose code
  merges. Those are the facts link_type derives from row multiplicities, so the markers are
  checked against it (any disagreement means the convention changed — stop) and then stripped,
  leaving the official titles.
  '''
  body = frame_below_header(raw, [str(source_vintage), str(target_vintage), 'code'])
  source_code = find_col(body.columns, str(source_vintage), 'code')
  target_code = find_col(body.columns, str(target_vintage), 'code')
  source_title = find_col(body.columns, str(source_vintage), 'title')
  target_title = find_col(body.columns, str(target_vintage), 'title')
  source, target = f'soc_{source_vintage}', f'soc_{target_vintage}'
  frame = (
    body
    .select(
      **{
        source: hyphenate_soc(code_expr(source_code)),
        f'title_{source_vintage}': title_expr(source_title),
        target: hyphenate_soc(code_expr(target_code)),
        f'title_{target_vintage}': title_expr(target_title),
      }
    )
    .filter(pl.col(source).str.contains(SOC_RE).and_(pl.col(target).str.contains(SOC_RE)))
    .unique(maintain_order=True)
    .with_columns(link_type_exprs(source, target))
    .with_columns(
      split_marked=pl.col(f'title_{source_vintage}').str.contains(r'\(#\)$'),
      merge_marked=pl.col(f'title_{target_vintage}').str.contains(r'\(##\)$'),
    )
  )
  if frame.select(pl.col('split_marked').or_(pl.col('merge_marked')).any()).item():
    disagreements = frame.filter(
      pl.col('split_marked').ne(pl.len().over(source).gt(1))
      .or_(pl.col('merge_marked').ne(pl.len().over(target).gt(1)))
    ).height
    if disagreements:
      raise ValueError(
        f'soc_{source_vintage}_to_{target_vintage}: {disagreements} rows whose BLS (#)/(##) title '
        f'markers disagree with the derived link_type; the marker convention changed.'
      )
  return (
    frame
    .with_columns(pl.col(f'title_{source_vintage}', f'title_{target_vintage}').str.replace(r'\s*\(#{1,2}\)$', ''))
    .drop('split_marked', 'merge_marked')
    .sort(source, target)
  )


def validate_soc_crosswalk(frame: pl.DataFrame, source_vintage: int, target_vintage: int) -> list[str]:
  problems = []
  if not 700 <= frame.height <= 1600:
    problems.append(
      f'soc_{source_vintage}_to_{target_vintage}: {frame.height} rows is outside the plausible 700-1600 band'
    )
  return problems


# --------------------------------------------------------------------------------------------
# Census occupation codes — the household-survey (ACS / CPS / SIPP) aggregation of SOC
# --------------------------------------------------------------------------------------------

CENSUS_OCC_RE = r'^\d{4}$'
SOC_REMAINDER_RE = r'^\d{2}-\d{1,3}X{1,3}$'
CENSUS_SOC_LEVELS = ('detailed', 'broad', 'minor', 'major', 'remainder', 'none')


def parse_census_occ(raw: pl.DataFrame, vintage: int, **deps: pl.DataFrame) -> pl.DataFrame:
  '''Census "<vintage> Census Occupation Code List" sheet -> census_occ, title, soc_code, soc_level,
  one row per four-digit Census code, exactly as published.

  Heading rows carry code ranges ("0010-3550") and are dropped. The SOC cell is one of: a
  detailed code; a broad or minor group (the Census code aggregates the whole group); a
  remainder pattern with X placeholders ("15-124X": the codes under that prefix not claimed by
  any other Census code); or "none" (military rank not specified, never worked). soc_level
  records which, looked up against the matching SOC structure for real codes.
  '''
  soc = deps[f'soc_{vintage}']
  body = frame_below_header(raw, [str(vintage), 'census code', 'soc code'])
  census_col = find_col(body.columns, 'census code')
  soc_col = find_col(body.columns, 'soc code')
  try:
    title_col = find_col(body.columns, 'title')
  except ValueError:
    title_col = find_col(body.columns, 'description')  # the 2010 list's header wording
  listed = (
    body
    .select(census_occ=code_expr(census_col), title=title_expr(title_col), soc_cell=title_expr(soc_col))
    .filter(pl.col('census_occ').str.contains(r'^\d{1,4}$'))
    .with_columns(census_occ=pl.col('census_occ').str.zfill(4))
  )
  level_of = dict(zip(soc.get_column('code'), soc.get_column('level')))
  soc_codes: list[str | None] = []
  soc_levels: list[str] = []
  for cell in listed.get_column('soc_cell'):
    if cell is None or cell.lower() == 'none':
      soc_codes.append(None)
      soc_levels.append('none')
    elif re.fullmatch(r'\d{2}-\d{4}', cell):
      if cell not in level_of:
        raise ValueError(f'census_occ_{vintage}: SOC code {cell} is not in soc_{vintage}; the vintages do not match.')
      soc_codes.append(cell)
      soc_levels.append(level_of[cell])
    elif re.fullmatch(SOC_REMAINDER_RE, cell):
      soc_codes.append(cell)
      soc_levels.append('remainder')
    else:
      raise ValueError(f'census_occ_{vintage}: unrecognized SOC cell {cell!r}; the source layout changed.')
  return (
    listed
    .with_columns(
      soc_code=pl.Series(soc_codes, dtype=pl.Utf8),
      soc_level=pl.Series(soc_levels, dtype=pl.Utf8),
    )
    .select('census_occ', 'title', 'soc_code', 'soc_level')
    .sort('census_occ')
  )


def validate_census_occ(frame: pl.DataFrame, vintage: int, **deps: pl.DataFrame) -> list[str]:
  problems = []
  if not 450 <= frame.height <= 700:
    problems.append(f'census_occ_{vintage}: {frame.height} codes is outside the plausible 450-700 band')
  duplicates = frame.filter(pl.col('census_occ').is_duplicated()).height
  if duplicates:
    problems.append(f'census_occ_{vintage}: {duplicates} duplicated Census codes')
  unknown = frame.filter(pl.col('soc_level').is_in(list(CENSUS_SOC_LEVELS)).not_()).height
  if unknown:
    problems.append(f'census_occ_{vintage}: {unknown} rows with a soc_level outside {CENSUS_SOC_LEVELS}')
  return problems


def expand_census_occ(vintage: int, **deps: pl.DataFrame) -> pl.DataFrame:
  '''Derived: one row per (Census code, detailed SOC code) — the published list expanded so
  every detailed SOC occupation is claimed by exactly one Census code.

  Precedence follows specificity: exact detailed codes first, then whole broad groups, minor
  groups, and major groups (a group claims every detailed descendant), and finally remainder
  patterns, longest prefix first, which take whatever under their prefix is still unclaimed. A
  detailed code claimed twice means the reading is wrong for this vintage, so it is an error;
  a detailed code claimed by nobody is reported by validate_census_expansion.
  '''
  census = deps[f'census_occ_{vintage}']
  soc = deps[f'soc_{vintage}']
  parent_of = dict(zip(soc.get_column('code'), soc.get_column('parent_code')))
  title_of = dict(zip(soc.get_column('code'), soc.get_column('title')))
  detailed = [code for code, level in zip(soc.get_column('code'), soc.get_column('level')) if level == 'detailed']

  def ancestors(code: str) -> set[str]:
    found, parent = set(), parent_of.get(code)
    while parent:
      found.add(parent)
      parent = parent_of.get(parent)
    return found

  ancestors_of = {code: ancestors(code) for code in detailed}
  claims: dict[str, tuple[str, str]] = {}  # detailed SOC -> (census code, via)

  def claim(soc_code: str, census_occ: str, via: str) -> None:
    if soc_code in claims:
      raise ValueError(
        f'census_occ_{vintage}: SOC {soc_code} is claimed by both Census {claims[soc_code][0]} and '
        f'{census_occ}; the group/remainder reading does not partition this vintage.'
      )
    claims[soc_code] = (census_occ, via)

  precedence = {'detailed': 0, 'broad': 1, 'minor': 2, 'major': 3, 'remainder': 4}
  mapped = census.filter(pl.col('soc_level').ne('none')).select('census_occ', 'soc_code', 'soc_level').rows()
  for census_occ, soc_code, level in sorted(mapped, key=lambda row: (precedence[row[2]], -len(row[1].rstrip('X')))):
    if level == 'detailed':
      claim(soc_code, census_occ, 'detailed')
    elif level == 'remainder':
      prefix = soc_code.rstrip('X')
      for code in detailed:
        if code.startswith(prefix) and code not in claims:
          claim(code, census_occ, 'remainder')
    else:
      for code in detailed:
        if soc_code in ancestors_of[code]:
          claim(code, census_occ, level)

  census_title = dict(zip(census.get_column('census_occ'), census.get_column('title')))
  rows = [
    (census_occ, census_title[census_occ], soc_code, title_of[soc_code], via)
    for soc_code, (census_occ, via) in claims.items()
  ]
  return pl.DataFrame(
    rows,
    schema=[f'census_occ_{vintage}', f'census_title_{vintage}', f'soc_{vintage}', f'soc_title_{vintage}', 'via'],
    orient='row',
  ).sort(f'census_occ_{vintage}', f'soc_{vintage}')


def validate_census_expansion(frame: pl.DataFrame, vintage: int, **deps: pl.DataFrame) -> list[str]:
  soc = deps[f'soc_{vintage}']
  problems = []
  detailed = set(soc.filter(pl.col('level').eq('detailed')).get_column('code'))
  claimed = set(frame.get_column(f'soc_{vintage}'))
  unclaimed = sorted(detailed.difference(claimed))
  if unclaimed:
    sample = ', '.join(unclaimed[:10])
    problems.append(f'census_occ_{vintage}_to_soc_{vintage}: {len(unclaimed)} detailed SOC codes claimed by no Census code (e.g. {sample})')
  duplicates = frame.filter(pl.col(f'soc_{vintage}').is_duplicated()).height
  if duplicates:
    problems.append(f'census_occ_{vintage}_to_soc_{vintage}: {duplicates} detailed SOC codes appear more than once')
  return problems


# --------------------------------------------------------------------------------------------
# Registry
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Build:
  name: str  # output lands at data/<name>.csv
  url: str | None  # None: derived purely from `requires`, no source file
  parse: Callable[..., pl.DataFrame]  # parse(raw_sheet, **deps), or parse(**deps) when derived
  validate: Callable[..., list[str]]  # validate(frame, **deps)
  sheet: str | None = None  # worksheet to read; the first when None
  requires: tuple[str, ...] = ()  # other artifacts handed in as keyword frames


# Pinned source URLs — the canonical Census/BLS locations as of 2026. If one 404s, see the
# module docstring. The NAICS structure files are the "<vintage>_NAICS_Structure" workbooks,
# not the "2-6 digit codes" ones: only the former carry the trilateral markers and the change
# indicator. Adding a vintage or a concordance is one more Build entry (plus a REFERENTIAL_PAIRS
# row for a concordance).
BUILDS = [
  Build(
    name='naics_2022',
    url='https://www.census.gov/naics/2022NAICS/2022_NAICS_Structure.xlsx',
    parse=partial(parse_naics_structure, vintage=2022),
    validate=partial(validate_naics, vintage=2022),
  ),
  Build(
    name='naics_2017',
    url='https://www.census.gov/naics/2017NAICS/2017_NAICS_Structure.xlsx',
    parse=partial(parse_naics_structure, vintage=2017),
    validate=partial(validate_naics, vintage=2017),
  ),
  Build(
    name='naics_2012',
    url='https://www.census.gov/naics/2012NAICS/2012_NAICS_Structure.xls',
    parse=partial(parse_naics_structure, vintage=2012),
    validate=partial(validate_naics, vintage=2012),
  ),
  Build(
    name='naics_2017_to_2022',
    url='https://www.census.gov/naics/concordances/2017_to_2022_NAICS.xlsx',
    parse=partial(parse_naics_concordance, source_vintage=2017, target_vintage=2022),
    validate=partial(validate_naics_concordance, source_vintage=2017, target_vintage=2022),
  ),
  Build(
    name='naics_2012_to_2017',
    url='https://www.census.gov/naics/concordances/2012_to_2017_NAICS.xlsx',
    parse=partial(parse_naics_concordance, source_vintage=2012, target_vintage=2017),
    validate=partial(validate_naics_concordance, source_vintage=2012, target_vintage=2017),
  ),
  Build(
    name='soc_2018',
    url='https://www.bls.gov/soc/2018/soc_structure_2018.xlsx',
    parse=partial(parse_soc_structure, vintage=2018),
    validate=partial(validate_soc, vintage=2018),
  ),
  Build(
    name='soc_2010',
    url='https://www.bls.gov/soc/soc_structure_2010.xls',
    parse=partial(parse_soc_structure, vintage=2010),
    validate=partial(validate_soc, vintage=2010),
  ),
  Build(
    name='soc_2010_to_2018',
    url='https://www.bls.gov/soc/2018/soc_2010_to_2018_crosswalk.xlsx',
    parse=partial(parse_soc_crosswalk, source_vintage=2010, target_vintage=2018),
    validate=partial(validate_soc_crosswalk, source_vintage=2010, target_vintage=2018),
  ),
  # Census occupation code lists (census.gov/topics/employment/industry-occupation/guidance/
  # code-lists.html). Each workbook's code-list sheet is the published list; the *_to_soc_*
  # artifact is derived from it and the matching SOC structure.
  Build(
    name='census_occ_2018',
    url='https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2018-occupation-code-list-and-crosswalk.xlsx',
    sheet='2018 Census Occ Code List',
    parse=partial(parse_census_occ, vintage=2018),
    validate=partial(validate_census_occ, vintage=2018),
    requires=('soc_2018',),
  ),
  Build(
    name='census_occ_2018_to_soc_2018',
    url=None,
    parse=partial(expand_census_occ, vintage=2018),
    validate=partial(validate_census_expansion, vintage=2018),
    requires=('census_occ_2018', 'soc_2018'),
  ),
  Build(
    name='census_occ_2010',
    url='https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2010-occ-codes-with-crosswalk-from-2002-2011.xls',
    sheet='2010OccCodeList',
    parse=partial(parse_census_occ, vintage=2010),
    validate=partial(validate_census_occ, vintage=2010),
    requires=('soc_2010',),
  ),
  Build(
    name='census_occ_2010_to_soc_2010',
    url=None,
    parse=partial(expand_census_occ, vintage=2010),
    validate=partial(validate_census_expansion, vintage=2010),
    requires=('census_occ_2010', 'soc_2010'),
  ),
]

# (concordance, code column in it, structure file it must resolve against, leaf level there)
REFERENTIAL_PAIRS = [
  ('naics_2017_to_2022', 'naics_2017', 'naics_2017', 6),
  ('naics_2017_to_2022', 'naics_2022', 'naics_2022', 6),
  ('naics_2012_to_2017', 'naics_2012', 'naics_2012', 6),
  ('naics_2012_to_2017', 'naics_2017', 'naics_2017', 6),
  ('soc_2010_to_2018', 'soc_2010', 'soc_2010', 'detailed'),
  ('soc_2010_to_2018', 'soc_2018', 'soc_2018', 'detailed'),
]


def referential_checks(frames: dict[str, pl.DataFrame]) -> list[str]:
  '''Cross-file integrity: every code a concordance mentions must exist at the six-digit /
  detailed level of the matching structure file. Runs only over pairs where both sides were
  built this invocation.'''
  problems = []
  for concordance_name, column, structure_name, leaf_level in REFERENTIAL_PAIRS:
    if concordance_name not in frames or structure_name not in frames:
      continue
    leaves = (
      frames[structure_name]
      .filter(pl.col('level').eq(leaf_level))
      .get_column('code')
      .to_list()
    )
    missing = frames[concordance_name].filter(pl.col(column).is_in(leaves).not_()).height
    if missing:
      problems.append(
        f'{concordance_name}: {missing} {column} codes not found at the leaf level of {structure_name}'
      )
  return problems


# --------------------------------------------------------------------------------------------
# Manifest and orchestration
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Record:
  name: str
  rows: str
  url: str
  sha256: str
  retrieved: str


def resolve_requires(requires: tuple[str, ...], frames: dict[str, pl.DataFrame], data_dir: Path) -> dict[str, pl.DataFrame]:
  '''The frames a build depends on: what this run built, else the CSV already in data/ (read
  with every column as Utf8, which is how the dependents consume them).'''
  deps = {}
  for name in requires:
    if name in frames:
      deps[name] = frames[name]
      continue
    path = data_dir / f'{name}.csv'
    if not path.exists():
      raise FileNotFoundError(f'{name} is required but was neither built this run nor found at {path}')
    deps[name] = pl.read_csv(path, infer_schema=False)
  return deps


def manifest_records(builds: list[Build], data_dir: Path, sources_dir: Path) -> list[Record]:
  '''One row per registered build, read from what is on disk right now — so a partial run
  (--only, or a blocked download) documents the whole data/ directory rather than only the
  artifacts it touched.'''
  records = []
  for build in builds:
    csv_path = data_dir / f'{build.name}.csv'
    if build.url is None:
      origin = f'derived from {", ".join(build.requires)}'
      rows = str(pl.read_csv(csv_path, infer_schema=False).height) if csv_path.exists() else 'NOT BUILT'
      records.append(Record(build.name, rows, origin, '', ''))
      continue
    source_path = sources_dir / source_filename(build.url)
    if not csv_path.exists() or not source_path.exists():
      records.append(Record(build.name, 'NOT BUILT', build.url, '', ''))
      continue
    records.append(
      Record(
        name=build.name,
        rows=str(pl.read_csv(csv_path, infer_schema=False).height),
        url=build.url,
        sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
        retrieved=datetime.fromtimestamp(source_path.stat().st_mtime, tz=timezone.utc).isoformat(timespec='seconds'),
      )
    )
  return records


def write_manifest(path: Path, records: list[Record], problems: list[str]) -> None:
  lines = [
    '# classification-codes data manifest',
    '',
    f'Generated {datetime.now(timezone.utc).isoformat(timespec="seconds")} by scripts/build.py.',
    'sources/ holds the exact bytes each CSV was built from — commit it; Census and BLS overwrite',
    'files in place, so an unarchived source vintage is unrecoverable. `retrieved` is the time the',
    'cached source file was written.',
    '',
    '| output | rows | source url | sha256 | retrieved |',
    '|---|---|---|---|---|',
  ]
  lines.extend(
    f'| data/{record.name}.csv | {record.rows} | {record.url} | {record.sha256} | {record.retrieved} |'
    for record in records
  )
  lines.append('')
  lines.append('No validation problems in the last run.' if not problems else 'VALIDATION PROBLEMS in the last run:')
  lines.extend(f'- {problem}' for problem in problems)
  lines.append('')
  path.write_text('\n'.join(lines))


def main() -> int:
  script_dir = Path(__file__).resolve().parent
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('--data-dir', type=Path, default=script_dir.parent / 'data')
  parser.add_argument('--sources-dir', type=Path, default=script_dir.parent / 'sources')
  parser.add_argument('--only', action='append', default=None, help='build only the named artifact(s)')
  parser.add_argument('--offline', action='store_true', help='use cached sources/, never download')
  parser.add_argument('--refresh', action='store_true', help='re-download even when cached')
  parser.add_argument('--list', action='store_true', help='list the build registry and exit')
  args = parser.parse_args()

  if args.list:
    for build in BUILDS:
      origin = build.url if build.url else f'derived from {", ".join(build.requires)}'
      sheet = f' [sheet: {build.sheet}]' if build.sheet else ''
      print(f'{build.name:28s} {origin}{sheet}')
    return 0

  selected = [build for build in BUILDS if args.only is None or build.name in args.only]
  if args.only and len(selected) < len(args.only):
    known = {build.name for build in BUILDS}
    parser.error(f'unknown --only name(s): {sorted(set(args.only).difference(known))}')

  args.data_dir.mkdir(parents=True, exist_ok=True)
  frames: dict[str, pl.DataFrame] = {}
  problems: list[str] = []
  for build in selected:
    print(f'building {build.name} ...')
    try:
      deps = resolve_requires(build.requires, frames, args.data_dir)
      if build.url is None:
        frame = build.parse(**deps)
      else:
        source_path, _sha256, _retrieved = fetch(build.url, args.sources_dir, args.offline, args.refresh)
        frame = build.parse(read_sheet(source_path, build.sheet), **deps)
    except (RuntimeError, FileNotFoundError) as error:
      problems.append(f'{build.name}: NOT BUILT — {error}')
      print(f'  skipped: {error}')
      continue
    problems.extend(build.validate(frame, **deps))
    frame.write_csv(args.data_dir / f'{build.name}.csv')
    frames[build.name] = frame
    print(f'  {frame.height} rows -> data/{build.name}.csv')

  problems.extend(referential_checks(frames))
  write_manifest(args.data_dir.parent / 'MANIFEST.md', manifest_records(BUILDS, args.data_dir, args.sources_dir), problems)
  if problems:
    print('\nVALIDATION PROBLEMS — inspect data/ before committing:')
    for problem in problems:
      print(f'  - {problem}')
    return 1
  print('\nAll validations passed; MANIFEST.md updated.')
  return 0


if __name__ == '__main__':
  sys.exit(main())

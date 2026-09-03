#!/usr/bin/env python3
# /// script
# requires-python = '>=3.11'
# dependencies = [
#   'polars>=1.0',
#   'fastexcel>=0.12',
# ]
# ///
'''Build the geographic-codes data files: interval-stamped U.S. statistical geography.

Every county-equivalent and CBSA row carries a half-open [valid_from, valid_to) so the question
is always "valid at this reference date", never "which vintage file do I open". (states.csv is a
flat lookup and county_changes.csv is an event log keyed by effective_date; neither carries an
interval, because neither needs one.) valid_from means one thing only: the date the code became
valid for federal statistical products (Census effective date for county-equivalents, OMB
bulletin date for CBSA delineations). Program adoption dates — when SAE or QCEW started
publishing on a delineation — are a different clock and live in bls-data-context.

Artifacts:
  data/states.csv          FIPS / USPS / name / Census region and division (seed table; stable)
  data/counties.csv        one row per county-equivalent interval, synthesized from the current
                           Census gazetteer plus seeds/county_changes.csv played forward in time
  data/county_changes.csv  the validated change log itself (rename / recode / split / merge /
                           create / dissolve), the bridge across county intervals
  data/cbsa_counties.csv   county membership of every CBSA / metro division / CSA, one block per
                           OMB delineation, interval-stamped by bulletin date
  data/cbsa.csv            one row per (delineation, CBSA), derived from cbsa_counties

seeds/county_changes.csv is hand-curated: Census publishes substantial county changes as prose
(census.gov/programs-surveys/geography/technical-documentation/county-changes.html, one page per
decade), not as a machine-readable file. The build validates it (chronology, referential closure
against the current county set) but cannot regenerate it. Rows carry status=unverified until
checked against those pages; the build warns on every unverified row.

Usage:
  uv run skills/geographic-codes/scripts/build.py
  uv run skills/geographic-codes/scripts/build.py --only counties --only county_changes
  uv run skills/geographic-codes/scripts/build.py --offline
  uv run skills/geographic-codes/scripts/build.py --list

If a download 404s, Census reorganized: find the file under www2.census.gov/geo/docs (gazetteer)
or www2.census.gov/programs-surveys/metro-micro (delineations) and update the URL constants.
'''

from __future__ import annotations

import argparse
import hashlib
import io
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import polars as pl

USER_AGENT = 'geographic-codes-build/0.1 (github.com/lowmason/agent-skills)'
DOWNLOAD_TIMEOUT_SECONDS = 120

# Interval sentinels. COVERAGE_FLOOR is not a creation date: it marks "already in existence when
# the change log begins". OPEN_END marks a currently valid row. Both are documented in SKILL.md.
COVERAGE_FLOOR = date(1990, 1, 1)
OPEN_END = date(9999, 12, 31)

GEOID_RE = r'^\d{5}$'
CSA_CODE_RE = r'^\d{3}$'

# Plausibility bands: a source-layout change that drops or duplicates rows fails these loudly.
COUNTY_BAND = (3100, 3400)
CBSA_BAND = (850, 1050)
METRO_BAND = (350, 450)
STATE_COUNT = 50

GAZETTEER_URL = (
    'https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/'
    '2025_Gaz_counties_national.zip'
)

DELINEATION_ROOT = 'https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files'


@dataclass(frozen=True)
class Delineation:
    '''One OMB delineation vintage: the Census "List 1" workbook and the bulletin that issued it.

    `effective` is the bulletin's own issue date (read from the bulletin, not from the workbook's
    release date, which lags by months). `label` is the year, disambiguated by month only when a
    year carries two bulletins.
    '''

    label: str
    bulletin: str
    effective: date
    url: str

    @property
    def source_name(self) -> str:
        '''Cache filename under sources/. Prefixed by label because three vintages are all
        published as list1.xls and would otherwise overwrite one another.'''
        return f'{self.label}_{Path(urllib.parse.urlparse(self.url).path).name}'


# Chronological. valid_to of each vintage is the next vintage's effective date. Adding a vintage
# is one entry; the bulletin dates were read from the bulletins themselves.
DELINEATIONS = [
    Delineation('2013', '13-01', date(2013, 2, 28), f'{DELINEATION_ROOT}/2013/delineation-files/list1.xls'),
    Delineation('2015', '15-01', date(2015, 7, 15), f'{DELINEATION_ROOT}/2015/delineation-files/list1.xls'),
    Delineation('2017', '17-01', date(2017, 8, 15), f'{DELINEATION_ROOT}/2017/delineation-files/list1.xls'),
    Delineation('2018-04', '18-03', date(2018, 4, 10), f'{DELINEATION_ROOT}/2018/delineation-files/list1.xls'),
    Delineation('2018-09', '18-04', date(2018, 9, 14), f'{DELINEATION_ROOT}/2018/delineation-files/list1_Sep_2018.xls'),
    Delineation('2020', '20-01', date(2020, 3, 6), f'{DELINEATION_ROOT}/2020/delineation-files/list1_2020.xls'),
    Delineation('2023', '23-01', date(2023, 7, 21), f'{DELINEATION_ROOT}/2023/delineation-files/list1_2023.xlsx'),
]

CHANGE_TYPES = ('rename', 'recode', 'split', 'merge', 'create', 'dissolve')
CHANGE_STATUSES = ('verified', 'unverified')

# Census regions and divisions have been stable since the 1950s; a seed table beats a fetch.
REGIONS = {'1': 'Northeast', '2': 'Midwest', '3': 'South', '4': 'West'}
DIVISIONS = {
    '1': ('1', 'New England'),
    '2': ('1', 'Middle Atlantic'),
    '3': ('2', 'East North Central'),
    '4': ('2', 'West North Central'),
    '5': ('3', 'South Atlantic'),
    '6': ('3', 'East South Central'),
    '7': ('3', 'West South Central'),
    '8': ('4', 'Mountain'),
    '9': ('4', 'Pacific'),
}
# (state_fips, usps, name, division_code or None for territories)
SEED_STATES = [
    ('01', 'AL', 'Alabama', '6'), ('02', 'AK', 'Alaska', '9'), ('04', 'AZ', 'Arizona', '8'),
    ('05', 'AR', 'Arkansas', '7'), ('06', 'CA', 'California', '9'), ('08', 'CO', 'Colorado', '8'),
    ('09', 'CT', 'Connecticut', '1'), ('10', 'DE', 'Delaware', '5'),
    ('11', 'DC', 'District of Columbia', '5'), ('12', 'FL', 'Florida', '5'),
    ('13', 'GA', 'Georgia', '5'), ('15', 'HI', 'Hawaii', '9'), ('16', 'ID', 'Idaho', '8'),
    ('17', 'IL', 'Illinois', '3'), ('18', 'IN', 'Indiana', '3'), ('19', 'IA', 'Iowa', '4'),
    ('20', 'KS', 'Kansas', '4'), ('21', 'KY', 'Kentucky', '6'), ('22', 'LA', 'Louisiana', '7'),
    ('23', 'ME', 'Maine', '1'), ('24', 'MD', 'Maryland', '5'), ('25', 'MA', 'Massachusetts', '1'),
    ('26', 'MI', 'Michigan', '3'), ('27', 'MN', 'Minnesota', '4'), ('28', 'MS', 'Mississippi', '6'),
    ('29', 'MO', 'Missouri', '4'), ('30', 'MT', 'Montana', '8'), ('31', 'NE', 'Nebraska', '4'),
    ('32', 'NV', 'Nevada', '8'), ('33', 'NH', 'New Hampshire', '1'), ('34', 'NJ', 'New Jersey', '2'),
    ('35', 'NM', 'New Mexico', '8'), ('36', 'NY', 'New York', '2'),
    ('37', 'NC', 'North Carolina', '5'), ('38', 'ND', 'North Dakota', '4'), ('39', 'OH', 'Ohio', '3'),
    ('40', 'OK', 'Oklahoma', '7'), ('41', 'OR', 'Oregon', '9'), ('42', 'PA', 'Pennsylvania', '2'),
    ('44', 'RI', 'Rhode Island', '1'), ('45', 'SC', 'South Carolina', '5'),
    ('46', 'SD', 'South Dakota', '4'), ('47', 'TN', 'Tennessee', '6'), ('48', 'TX', 'Texas', '7'),
    ('49', 'UT', 'Utah', '8'), ('50', 'VT', 'Vermont', '1'), ('51', 'VA', 'Virginia', '5'),
    ('53', 'WA', 'Washington', '9'), ('54', 'WV', 'West Virginia', '5'),
    ('55', 'WI', 'Wisconsin', '3'), ('56', 'WY', 'Wyoming', '8'),
    ('60', 'AS', 'American Samoa', None), ('66', 'GU', 'Guam', None),
    ('69', 'MP', 'Northern Mariana Islands', None), ('72', 'PR', 'Puerto Rico', None),
    ('74', 'UM', 'U.S. Minor Outlying Islands', None), ('78', 'VI', 'U.S. Virgin Islands', None),
]

# Entity type from the gazetteer name suffix, first match wins. Carson City and DC are named
# without a type word, so they are pinned by GEOID.
ENTITY_PATTERNS = [
    (r' Planning Region$', 'planning_region'),
    (r' City and Borough$', 'city_and_borough'),
    (r' Borough$', 'borough'),
    (r' Census Area$', 'census_area'),
    (r' Municipality$', 'municipality'),
    (r' Municipio$', 'municipio'),
    (r' Parish$', 'parish'),
    (r' County$', 'county'),
    (r' city$', 'independent_city'),
]
ENTITY_OVERRIDES = {'32510': 'independent_city', '11001': 'district'}


# --------------------------------------------------------------------------------------------
# Generic helpers (deliberately duplicated from classification-codes so each skill stands alone)
# --------------------------------------------------------------------------------------------


def fetch(
    url: str, sources_dir: Path, offline: bool, refresh: bool, filename: str | None = None
) -> tuple[Path, str, str]:
    '''Download url into sources_dir (or reuse the cached copy); return (path, sha256, retrieved).

    `filename` overrides the cache name when the URL basename is not unique across sources.
    '''
    sources_dir.mkdir(parents=True, exist_ok=True)
    dest = sources_dir / (filename or urllib.parse.unquote(Path(urllib.parse.urlparse(url).path).name))
    if dest.exists() and not refresh:
        retrieved = datetime.fromtimestamp(dest.stat().st_mtime, tz=timezone.utc).isoformat(timespec='seconds')
    elif offline:
        raise FileNotFoundError(f'--offline set but {dest} is not cached')
    else:
        request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
                dest.write_bytes(response.read())
        except urllib.error.URLError as error:
            raise RuntimeError(
                f'Download failed for {url} ({error}). See the module docstring for where to look.'
            ) from error
        retrieved = datetime.now(timezone.utc).isoformat(timespec='seconds')
    return dest, hashlib.sha256(dest.read_bytes()).hexdigest(), retrieved


def read_sheet(path: Path) -> pl.DataFrame:
    '''First worksheet with every cell as Utf8; header detection happens downstream.'''
    return pl.read_excel(path, has_header=False).select(pl.all().cast(pl.Utf8))


def frame_below_header(raw: pl.DataFrame, needles: list[str]) -> pl.DataFrame:
    '''Slice off everything above the first row whose cells jointly contain all needles.'''
    targets = [needle.lower() for needle in needles]
    for index, row in enumerate(raw.rows()):
        joined = ' | '.join(str(cell).lower() for cell in row if cell is not None)
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
    for column in columns:
        lowered = column.lower()
        if all(needle.lower() in lowered for needle in needles):
            return column
    raise ValueError(f'No column matching {needles!r} among {columns!r}; the source layout changed.')


def code_expr(column: str, width: int | None = None) -> pl.Expr:
    '''Normalize a code cell: strip, drop an Excel ".0", optionally zero-pad to width.'''
    expr = pl.col(column).cast(pl.Utf8).str.strip_chars().str.replace(r'\.0$', '')
    return expr.str.zfill(width) if width else expr


def text_expr(column: str) -> pl.Expr:
    '''Stripped text, with empty cells as null (the 2018+ workbooks store blanks as "").'''
    stripped = pl.col(column).cast(pl.Utf8).str.strip_chars()
    return pl.when(stripped.str.len_chars().gt(0)).then(stripped)


def entity_type_expr(name_col: str, geoid_col: str) -> pl.Expr:
    chain = pl.when(pl.col(geoid_col).is_in(list(ENTITY_OVERRIDES))).then(
        pl.col(geoid_col).replace_strict(ENTITY_OVERRIDES, default=None, return_dtype=pl.Utf8)
    )
    for pattern, label in ENTITY_PATTERNS:
        chain = chain.when(pl.col(name_col).str.contains(pattern)).then(pl.lit(label))
    return chain.otherwise(pl.lit('other'))


# --------------------------------------------------------------------------------------------
# States
# --------------------------------------------------------------------------------------------


def build_states() -> pl.DataFrame:
    rows = []
    for state_fips, usps, name, division_code in SEED_STATES:
        region_code, division_name = DIVISIONS[division_code] if division_code else (None, None)
        if division_code is None:
            entity_type = 'territory'
        elif usps == 'DC':
            entity_type = 'district'
        else:
            entity_type = 'state'
        rows.append(
            {
                'state_fips': state_fips,
                'state_usps': usps,
                'state_name': name,
                'region_code': region_code,
                'region_name': REGIONS.get(region_code) if region_code else None,
                'division_code': division_code,
                'division_name': division_name,
                'entity_type': entity_type,
            }
        )
    return pl.DataFrame(rows, schema_overrides={'region_code': pl.Utf8, 'division_code': pl.Utf8}).sort('state_fips')


def validate_states(frame: pl.DataFrame) -> list[str]:
    problems = []
    states = frame.filter(pl.col('entity_type').eq('state')).height
    if states != STATE_COUNT:
        problems.append(f'states: expected {STATE_COUNT} states, found {states}')
    return problems


# --------------------------------------------------------------------------------------------
# Counties: current set from the gazetteer, intervals synthesized from the change log
# --------------------------------------------------------------------------------------------


def read_gazetteer(path: Path) -> pl.DataFrame:
    '''Census county gazetteer (zip containing one delimited txt) -> county_geoid, name, state_usps.

    The delimiter is sniffed from the header: gazetteers through 2024 are tab-delimited with
    trailing whitespace on the last column, 2025 onward are pipe-delimited. Every column is
    stripped after reading either way.
    '''
    with zipfile.ZipFile(path) as archive:
        member = next(name for name in archive.namelist() if name.lower().endswith('.txt'))
        payload = archive.read(member)
    header = payload.split(b'\n', 1)[0]
    separator = '|' if b'|' in header else '\t'
    raw = pl.read_csv(io.BytesIO(payload), separator=separator, encoding='utf8-lossy', infer_schema=False)
    raw.columns = [column.strip() for column in raw.columns]
    return (
        raw
        .select(
            county_geoid=code_expr('GEOID', width=5),
            name=text_expr('NAME'),
            state_usps=text_expr('USPS'),
        )
        .filter(pl.col('county_geoid').str.contains(GEOID_RE))
    )


def read_changes(path: Path) -> pl.DataFrame:
    '''Load and structurally validate seeds/county_changes.csv.'''
    frame = pl.read_csv(path, infer_schema=False).with_columns(
        effective_date=pl.col('effective_date').str.to_date('%Y-%m-%d'),
        creates_new=pl.col('creates_new').str.to_lowercase().eq('true'),
    )
    bad_types = frame.filter(pl.col('change_type').is_in(list(CHANGE_TYPES)).not_()).height
    if bad_types:
        raise ValueError(f'county_changes: {bad_types} rows with change_type outside {CHANGE_TYPES}')
    bad_status = frame.filter(pl.col('status').is_in(list(CHANGE_STATUSES)).not_()).height
    if bad_status:
        raise ValueError(f'county_changes: {bad_status} rows with status outside {CHANGE_STATUSES}')
    malformed = pl.col('old_geoid').is_not_null().and_(pl.col('old_geoid').str.contains(GEOID_RE).not_()).or_(
        pl.col('new_geoid').is_not_null().and_(pl.col('new_geoid').str.contains(GEOID_RE).not_())
    )
    bad_geoids = frame.filter(malformed).height
    if bad_geoids:
        raise ValueError(f'county_changes: {bad_geoids} rows with malformed geoids')
    early = frame.filter(pl.col('effective_date').lt(COVERAGE_FLOOR)).height
    if early:
        raise ValueError(f'county_changes: {early} rows dated before COVERAGE_FLOOR {COVERAGE_FLOOR}')
    recoding_rename = frame.filter(
        pl.col('change_type').eq('rename').and_(pl.col('old_geoid').ne(pl.col('new_geoid')))
    ).height
    if recoding_rename:
        raise ValueError(f'county_changes: {recoding_rename} rename rows change the code (use recode)')
    return frame.sort('effective_date', 'change_group', 'old_geoid', 'new_geoid')


def synthesize_county_intervals(current: pl.DataFrame, changes: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    '''Play the change log forward from COVERAGE_FLOOR to produce [valid_from, valid_to) rows.

    Entities are opened at the floor unless some change creates them (creates_new on a
    non-rename row); each change closes its old_geoid and opens its new_geoid. A rename closes
    and reopens the same geoid so the name history is queryable. Returns (intervals, problems).
    '''
    problems: list[str] = []
    current_names = dict(zip(current.get_column('county_geoid'), current.get_column('name')))
    created_later = set(
        changes.filter(
            pl.col('creates_new')
            .and_(pl.col('new_geoid').is_not_null())
            .and_(pl.col('change_type').ne('rename'))
        ).get_column('new_geoid')
    )
    intervals: list[dict] = []
    open_: dict[str, tuple[str, date]] = {}
    for geoid, name in current_names.items():
        if geoid not in created_later:
            open_[geoid] = (name, COVERAGE_FLOOR)
    for row in changes.iter_rows(named=True):
        old = row['old_geoid']
        if old and old not in current_names and old not in created_later and old not in open_:
            open_[old] = (row['old_name'], COVERAGE_FLOOR)

    closed_at: set[tuple[str, date]] = set()

    def close(geoid: str, at: date, name_override: str | None = None) -> None:
        # A split lists its old entity once per target row; closing it once per (geoid, date) is correct.
        if (geoid, at) in closed_at:
            return
        if geoid not in open_:
            problems.append(f'county_changes: {geoid} closed on {at} but was not open (chronology or seed error)')
            return
        closed_at.add((geoid, at))
        name, valid_from = open_.pop(geoid)
        intervals.append({'county_geoid': geoid, 'name': name_override or name, 'valid_from': valid_from, 'valid_to': at})

    for row in changes.iter_rows(named=True):
        old, new, at = row['old_geoid'], row['new_geoid'], row['effective_date']
        if row['change_type'] == 'rename':
            close(old, at, name_override=row['old_name'])
            open_[new] = (row['new_name'], at)
            continue
        if old:
            close(old, at, name_override=row['old_name'])
        if new and row['creates_new']:
            if new in open_:
                problems.append(f'county_changes: {new} created on {at} but already open')
            else:
                open_[new] = (row['new_name'], at)
        elif new and new not in open_ and new not in current_names:
            problems.append(f'county_changes: survivor {new} on {at} is neither open nor current')

    for geoid, (name, valid_from) in open_.items():
        if geoid in current_names:
            if name != current_names[geoid]:
                print(f'  note: {geoid} seed name {name!r} differs from gazetteer {current_names[geoid]!r}; using gazetteer')
            name = current_names[geoid]
        else:
            problems.append(f'county_changes: {geoid} ({name}) still open at end but absent from the current gazetteer')
        intervals.append({'county_geoid': geoid, 'name': name, 'valid_from': valid_from, 'valid_to': OPEN_END})

    frame = (
        pl.DataFrame(intervals, schema={'county_geoid': pl.Utf8, 'name': pl.Utf8, 'valid_from': pl.Date, 'valid_to': pl.Date})
        .with_columns(
            state_fips=pl.col('county_geoid').str.slice(0, 2),
            county_fips=pl.col('county_geoid').str.slice(2, 3),
            is_current=pl.col('valid_to').eq(OPEN_END),
        )
        .with_columns(entity_type=entity_type_expr('name', 'county_geoid'))
        .join(build_states().select('state_fips', 'state_usps'), on='state_fips', how='left')
        .select(
            'county_geoid', 'name', 'state_fips', 'county_fips', 'state_usps', 'entity_type',
            'valid_from', 'valid_to', 'is_current',
        )
        .sort('county_geoid', 'valid_from')
    )
    return frame, problems


def validate_counties(frame: pl.DataFrame) -> list[str]:
    problems = []
    current = frame.filter(pl.col('is_current')).height
    low, high = COUNTY_BAND
    if not low <= current <= high:
        problems.append(f'counties: {current} current county-equivalents is outside the plausible {low}-{high} band')
    multiple_current = frame.filter(pl.col('is_current')).filter(pl.col('county_geoid').is_duplicated()).height
    if multiple_current:
        problems.append(f'counties: {multiple_current} geoids with more than one current interval')
    overlaps = (
        frame
        .sort('county_geoid', 'valid_from')
        .with_columns(next_from=pl.col('valid_from').shift(-1).over('county_geoid'))
        .filter(pl.col('next_from').is_not_null().and_(pl.col('next_from').lt(pl.col('valid_to'))))
        .height
    )
    if overlaps:
        problems.append(f'counties: {overlaps} overlapping intervals')
    unknown_state = frame.filter(pl.col('state_usps').is_null()).height
    if unknown_state:
        problems.append(f'counties: {unknown_state} rows whose state_fips is not in the states seed')
    return problems


# --------------------------------------------------------------------------------------------
# CBSA delineations
# --------------------------------------------------------------------------------------------


def parse_delineation(path: Path, delineation: Delineation, valid_to: date) -> pl.DataFrame:
    '''OMB/Census "List 1" delineation workbook -> one row per (CBSA, county) with metro division
    and CSA attached, stamped with the delineation label, bulletin, and interval.

    Column lookup is by shared substrings because the 2013 workbook says "Metro Division Code"
    where every later one says "Metropolitan Division Code".
    '''
    body = frame_below_header(read_sheet(path), ['cbsa code', 'fips state'])
    columns = body.columns
    area_kind = text_expr(find_col(columns, 'metropolitan/micropolitan')).str.to_lowercase()
    return (
        body
        .select(
            delineation=pl.lit(delineation.label),
            bulletin=pl.lit(delineation.bulletin),
            cbsa_code=code_expr(find_col(columns, 'cbsa', 'code'), width=5),
            cbsa_title=text_expr(find_col(columns, 'cbsa', 'title')),
            cbsa_type=pl.when(area_kind.str.contains('micro')).then(pl.lit('micropolitan')).otherwise(pl.lit('metropolitan')),
            metdiv_code=code_expr(find_col(columns, 'division', 'code')),
            metdiv_title=text_expr(find_col(columns, 'division', 'title')),
            csa_code=code_expr(find_col(columns, 'csa', 'code')),
            csa_title=text_expr(find_col(columns, 'csa', 'title')),
            county_geoid=pl.concat_str(
                code_expr(find_col(columns, 'fips', 'state'), width=2),
                code_expr(find_col(columns, 'fips', 'county'), width=3),
            ),
            county_name=text_expr(find_col(columns, 'county', 'equivalent')),
            central_outlying=text_expr(find_col(columns, 'central')).str.to_lowercase(),
            valid_from=pl.lit(delineation.effective),
            valid_to=pl.lit(valid_to),
        )
        .filter(pl.col('cbsa_code').str.contains(GEOID_RE).and_(pl.col('county_geoid').str.contains(GEOID_RE)))
        .with_columns(
            metdiv_code=pl.when(pl.col('metdiv_code').str.contains(GEOID_RE)).then(pl.col('metdiv_code')),
            csa_code=pl.when(pl.col('csa_code').str.contains(CSA_CODE_RE)).then(pl.col('csa_code')),
        )
        .unique(subset=['delineation', 'cbsa_code', 'county_geoid'], keep='first', maintain_order=True)
        .sort('delineation', 'cbsa_code', 'county_geoid')
    )


def validate_cbsa_counties(frame: pl.DataFrame) -> list[str]:
    problems = []
    cbsa_low, cbsa_high = CBSA_BAND
    metro_low, metro_high = METRO_BAND
    for (label,), block in frame.group_by('delineation', maintain_order=True):
        cbsas = block.get_column('cbsa_code').n_unique()
        if not cbsa_low <= cbsas <= cbsa_high:
            problems.append(f'cbsa_counties[{label}]: {cbsas} CBSAs is outside the plausible {cbsa_low}-{cbsa_high} band')
        metros = block.filter(pl.col('cbsa_type').eq('metropolitan')).get_column('cbsa_code').n_unique()
        if not metro_low <= metros <= metro_high:
            problems.append(f'cbsa_counties[{label}]: {metros} metropolitan areas is outside the plausible {metro_low}-{metro_high} band')
        inconsistent = (
            block.group_by('cbsa_code')
            .agg(pl.col('cbsa_title').n_unique().alias('titles'), pl.col('cbsa_type').n_unique().alias('types'))
            .filter(pl.col('titles').gt(1).or_(pl.col('types').gt(1)))
            .height
        )
        if inconsistent:
            problems.append(f'cbsa_counties[{label}]: {inconsistent} CBSAs with more than one title or type')
        unknown_role = block.filter(pl.col('central_outlying').is_in(['central', 'outlying']).not_()).height
        if unknown_role:
            problems.append(f'cbsa_counties[{label}]: {unknown_role} rows with central_outlying outside central/outlying')
    return problems


def derive_cbsa(cbsa_counties: pl.DataFrame) -> pl.DataFrame:
    '''One row per (delineation, CBSA).'''
    return (
        cbsa_counties
        .group_by('delineation', 'cbsa_code', maintain_order=True)
        .agg(
            bulletin=pl.col('bulletin').first(),
            cbsa_title=pl.col('cbsa_title').first(),
            cbsa_type=pl.col('cbsa_type').first(),
            csa_code=pl.col('csa_code').first(),
            csa_title=pl.col('csa_title').first(),
            n_counties=pl.len(),
            n_metdivs=pl.col('metdiv_code').drop_nulls().n_unique(),
            states=pl.col('county_geoid').str.slice(0, 2).unique().sort().str.join(','),
            valid_from=pl.col('valid_from').first(),
            valid_to=pl.col('valid_to').first(),
        )
        .sort('delineation', 'cbsa_code')
    )


def interval_referential_check(cbsa_counties: pl.DataFrame, counties: pl.DataFrame) -> list[str]:
    '''Every county a delineation names must have a county interval valid on the bulletin date —
    the check that catches a 2023 file coded with Connecticut's retired counties, or vice versa.'''
    problems = []
    unmatched = (
        cbsa_counties
        .select('delineation', 'county_geoid', 'valid_from')
        .unique()
        .join(counties.select('county_geoid', county_from='valid_from', county_to='valid_to'), on='county_geoid', how='left')
        .with_columns(
            ok=pl.col('valid_from').is_between(pl.col('county_from'), pl.col('county_to'), closed='left').fill_null(False)
        )
        .group_by('delineation', 'county_geoid')
        .agg(pl.col('ok').any())
        .filter(pl.col('ok').not_())
    )
    for (label,), block in unmatched.group_by('delineation', maintain_order=True):
        sample = ', '.join(block.get_column('county_geoid').sort().head(5).to_list())
        problems.append(
            f'cbsa_counties[{label}]: {block.height} counties with no valid interval on the bulletin date (e.g. {sample})'
        )
    return problems


# --------------------------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------------------------


@dataclass
class Record:
    name: str
    rows: int
    url: str
    sha256: str
    retrieved: str


def write_manifest(path: Path, records: list[Record], problems: list[str]) -> None:
    lines = [
        '# geographic-codes data manifest',
        '',
        f'Generated {datetime.now(timezone.utc).isoformat(timespec="seconds")} by scripts/build.py.',
        f'Interval sentinels: valid_from={COVERAGE_FLOOR} means "already existed at the start of the',
        f'change log", valid_to={OPEN_END} means "currently valid". Intervals are [valid_from, valid_to).',
        'sources/ holds the exact bytes each CSV was built from — commit it alongside data/.',
        '',
        '| output | rows | source | sha256 | retrieved |',
        '|---|---|---|---|---|',
    ]
    lines.extend(
        f'| data/{record.name}.csv | {record.rows} | {record.url} | {record.sha256} | {record.retrieved} |'
        for record in records
    )
    lines.append('')
    lines.append('No validation problems.' if not problems else 'VALIDATION PROBLEMS:')
    lines.extend(f'- {problem}' for problem in problems)
    lines.append('')
    path.write_text('\n'.join(lines))


ARTIFACTS = ('states', 'counties', 'county_changes', 'cbsa_counties', 'cbsa')


def list_registry() -> None:
    print(f'{"states":16s} seed table (SEED_STATES)')
    print(f'{"counties":16s} {GAZETTEER_URL} + seeds/county_changes.csv')
    print(f'{"county_changes":16s} seeds/county_changes.csv')
    for delineation in DELINEATIONS:
        print(
            f'{"cbsa_counties":16s} [{delineation.label} = OMB {delineation.bulletin}, '
            f'effective {delineation.effective}] {delineation.url}'
        )
    print(f'{"cbsa":16s} derived from cbsa_counties')


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--data-dir', type=Path, default=script_dir.parent / 'data')
    parser.add_argument('--sources-dir', type=Path, default=script_dir.parent / 'sources')
    parser.add_argument('--seeds-dir', type=Path, default=script_dir.parent / 'seeds')
    parser.add_argument('--only', action='append', choices=ARTIFACTS, default=None)
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--list', action='store_true')
    args = parser.parse_args()

    if args.list:
        list_registry()
        return 0

    wanted = set(args.only or ARTIFACTS)
    # cbsa derives from cbsa_counties; counties and county_changes share the seed; states feeds counties.
    if 'cbsa' in wanted:
        wanted.add('cbsa_counties')
    if 'counties' in wanted:
        wanted.update({'county_changes', 'states'})

    args.data_dir.mkdir(parents=True, exist_ok=True)
    records: list[Record] = []
    problems: list[str] = []
    frames: dict[str, pl.DataFrame] = {}

    def emit(name: str, frame: pl.DataFrame, url: str, sha256: str = '', retrieved: str = '') -> None:
        frame.write_csv(args.data_dir / f'{name}.csv')
        frames[name] = frame
        records.append(Record(name, frame.height, url, sha256, retrieved))
        print(f'  {frame.height} rows -> data/{name}.csv')

    if 'states' in wanted:
        print('building states ...')
        states = build_states()
        problems.extend(validate_states(states))
        emit('states', states, 'seed: SEED_STATES in build.py')

    if 'county_changes' in wanted or 'counties' in wanted:
        print('building county_changes ...')
        seed_path = args.seeds_dir / 'county_changes.csv'
        changes = read_changes(seed_path)
        unverified = changes.filter(pl.col('status').ne('verified')).height
        if unverified:
            print(f'  warning: {unverified} change rows still marked unverified')
        emit(
            'county_changes', changes, f'seed: {seed_path.relative_to(script_dir.parent)}',
            hashlib.sha256(seed_path.read_bytes()).hexdigest(),
        )

    if 'counties' in wanted:
        print('building counties ...')
        gazetteer_path, sha256, retrieved = fetch(GAZETTEER_URL, args.sources_dir, args.offline, args.refresh)
        counties, synth_problems = synthesize_county_intervals(read_gazetteer(gazetteer_path), frames['county_changes'])
        problems.extend(synth_problems)
        problems.extend(validate_counties(counties))
        emit('counties', counties, GAZETTEER_URL, sha256, retrieved)

    if 'cbsa_counties' in wanted:
        print('building cbsa_counties ...')
        blocks = []
        for index, delineation in enumerate(DELINEATIONS):
            valid_to = DELINEATIONS[index + 1].effective if index + 1 < len(DELINEATIONS) else OPEN_END
            path, sha256, retrieved = fetch(
                delineation.url, args.sources_dir, args.offline, args.refresh, filename=delineation.source_name
            )
            block = parse_delineation(path, delineation, valid_to)
            blocks.append(block)
            records.append(
                Record(f'cbsa_counties[{delineation.label}]', block.height, f'OMB {delineation.bulletin}: {delineation.url}', sha256, retrieved)
            )
        cbsa_counties = pl.concat(blocks)
        problems.extend(validate_cbsa_counties(cbsa_counties))
        if 'counties' in frames:
            problems.extend(interval_referential_check(cbsa_counties, frames['counties']))
        emit('cbsa_counties', cbsa_counties, 'see per-delineation rows above')
        print('building cbsa ...')
        emit('cbsa', derive_cbsa(cbsa_counties), 'derived from cbsa_counties')

    # A partial build knows only its own artifacts; rewriting the manifest would drop the rest.
    partial = args.only is not None
    if not partial:
        write_manifest(args.data_dir.parent / 'MANIFEST.md', records, problems)
    if problems:
        print('\nVALIDATION PROBLEMS — inspect data/ before committing:')
        for problem in problems:
            print(f'  - {problem}')
        return 1
    if partial:
        print('\nAll validations passed; MANIFEST.md left untouched (partial build — run a full build to refresh it).')
    else:
        print('\nAll validations passed; MANIFEST.md updated.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

'''Tests for the geographic-codes build: the county-interval synthesizer, its validators, the
gazetteer and delineation readers, and the cross-file referential check.

Run from this directory (bare import, directory-scoped, like the other skill test suites):

    cd skills/geographic-codes/scripts && uv run --python 3.13 --with pytest --with polars \
        --with fastexcel python -m pytest -q
'''

from __future__ import annotations

import io
import zipfile
from datetime import date
from pathlib import Path

import polars as pl
import pytest

import build

FLOOR = build.COVERAGE_FLOOR
OPEN = build.OPEN_END
SOURCES = Path(__file__).resolve().parent.parent / 'sources'


# --------------------------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------------------------


def current(*rows: tuple[str, str]) -> pl.DataFrame:
    '''A miniature gazetteer: (county_geoid, name) pairs; state_usps derived from the states seed.'''
    frame = pl.DataFrame(
        {'county_geoid': [geoid for geoid, _ in rows], 'name': [name for _, name in rows]},
        schema={'county_geoid': pl.Utf8, 'name': pl.Utf8},
    )
    states = build.build_states().select('state_fips', 'state_usps')
    return (
        frame
        .with_columns(state_fips=pl.col('county_geoid').str.slice(0, 2))
        .join(states, on='state_fips', how='left')
        .select('county_geoid', 'name', 'state_usps')
    )


def changes(*rows: dict) -> pl.DataFrame:
    '''Rows in the shape read_changes() produces (dates parsed, creates_new as bool).'''
    template = {
        'change_group': 'g',
        'effective_date': date(2000, 1, 1),
        'change_type': 'rename',
        'old_geoid': None,
        'old_name': None,
        'new_geoid': None,
        'new_name': None,
        'creates_new': False,
        'status': 'verified',
        'source_note': None,
    }
    schema = {
        'change_group': pl.Utf8,
        'effective_date': pl.Date,
        'change_type': pl.Utf8,
        'old_geoid': pl.Utf8,
        'old_name': pl.Utf8,
        'new_geoid': pl.Utf8,
        'new_name': pl.Utf8,
        'creates_new': pl.Boolean,
        'status': pl.Utf8,
        'source_note': pl.Utf8,
    }
    frame = pl.DataFrame([{**template, **row} for row in rows], schema=schema)
    return frame.sort('effective_date', 'change_group', 'old_geoid', 'new_geoid')


def intervals_of(frame: pl.DataFrame, geoid: str) -> list[tuple[str, date, date]]:
    rows = frame.filter(pl.col('county_geoid').eq(geoid)).sort('valid_from')
    return list(zip(rows.get_column('name'), rows.get_column('valid_from'), rows.get_column('valid_to')))


# --------------------------------------------------------------------------------------------
# States seed
# --------------------------------------------------------------------------------------------


def test_states_seed_has_fifty_states_dc_and_territories():
    states = build.build_states()
    by_type = dict(states.group_by('entity_type').len().iter_rows())
    assert by_type == {'state': 50, 'district': 1, 'territory': 6}
    assert states.get_column('state_fips').is_unique().all()
    assert build.validate_states(states) == []
    connecticut = states.filter(pl.col('state_usps').eq('CT')).row(0, named=True)
    assert (connecticut['region_name'], connecticut['division_name']) == ('Northeast', 'New England')


# --------------------------------------------------------------------------------------------
# Interval synthesis
# --------------------------------------------------------------------------------------------


def test_untouched_entity_spans_floor_to_open_end():
    frame, problems = build.synthesize_county_intervals(current(('01001', 'Autauga County')), changes())
    assert problems == []
    assert intervals_of(frame, '01001') == [('Autauga County', FLOOR, OPEN)]
    row = frame.row(0, named=True)
    assert (row['state_fips'], row['county_fips'], row['state_usps'], row['entity_type']) == ('01', '001', 'AL', 'county')
    assert row['is_current'] is True


def test_rename_yields_two_intervals_under_one_code():
    at = date(2013, 1, 3)
    log = changes(
        {
            'change_type': 'rename',
            'effective_date': at,
            'old_geoid': '02195',
            'old_name': 'Petersburg Census Area',
            'new_geoid': '02195',
            'new_name': 'Petersburg Borough',
        }
    )
    frame, problems = build.synthesize_county_intervals(current(('02195', 'Petersburg Borough')), log)
    assert problems == []
    assert intervals_of(frame, '02195') == [
        ('Petersburg Census Area', FLOOR, at),
        ('Petersburg Borough', at, OPEN),
    ]


def test_rename_flagged_creates_new_still_opens_at_floor():
    '''A rename is not a creation: a creates_new flag on it must not suppress the floor interval.'''
    at = date(2013, 1, 3)
    log = changes(
        {
            'change_type': 'rename',
            'effective_date': at,
            'old_geoid': '02195',
            'old_name': 'Petersburg Census Area',
            'new_geoid': '02195',
            'new_name': 'Petersburg Borough',
            'creates_new': True,
        }
    )
    frame, problems = build.synthesize_county_intervals(current(('02195', 'Petersburg Borough')), log)
    assert problems == []
    assert intervals_of(frame, '02195') == [
        ('Petersburg Census Area', FLOOR, at),
        ('Petersburg Borough', at, OPEN),
    ]


def test_recode_closes_old_code_and_opens_new_code():
    at = date(2015, 5, 1)
    log = changes(
        {
            'change_type': 'recode',
            'effective_date': at,
            'old_geoid': '46113',
            'old_name': 'Shannon County',
            'new_geoid': '46102',
            'new_name': 'Oglala Lakota County',
            'creates_new': True,
        }
    )
    frame, problems = build.synthesize_county_intervals(current(('46102', 'Oglala Lakota County')), log)
    assert problems == []
    assert intervals_of(frame, '46113') == [('Shannon County', FLOOR, at)]
    assert intervals_of(frame, '46102') == [('Oglala Lakota County', at, OPEN)]
    assert frame.filter(pl.col('county_geoid').eq('46113')).get_column('is_current').to_list() == [False]


def test_split_closes_parent_once_and_opens_each_child():
    at = date(2019, 1, 2)
    log = changes(
        {
            'change_group': 'valdez',
            'change_type': 'split',
            'effective_date': at,
            'old_geoid': '02261',
            'old_name': 'Valdez-Cordova Census Area',
            'new_geoid': '02063',
            'new_name': 'Chugach Census Area',
            'creates_new': True,
        },
        {
            'change_group': 'valdez',
            'change_type': 'split',
            'effective_date': at,
            'old_geoid': '02261',
            'old_name': 'Valdez-Cordova Census Area',
            'new_geoid': '02066',
            'new_name': 'Copper River Census Area',
            'creates_new': True,
        },
    )
    frame, problems = build.synthesize_county_intervals(
        current(('02063', 'Chugach Census Area'), ('02066', 'Copper River Census Area')), log
    )
    assert problems == []
    assert intervals_of(frame, '02261') == [('Valdez-Cordova Census Area', FLOOR, at)]
    assert intervals_of(frame, '02063') == [('Chugach Census Area', at, OPEN)]
    assert intervals_of(frame, '02066') == [('Copper River Census Area', at, OPEN)]


def test_split_into_existing_survivor_leaves_survivor_continuous():
    at = date(1997, 11, 7)
    log = changes(
        {
            'change_type': 'split',
            'effective_date': at,
            'old_geoid': '30113',
            'old_name': 'Yellowstone National Park',
            'new_geoid': '30031',
            'new_name': 'Gallatin County',
        },
        {
            'change_type': 'split',
            'effective_date': at,
            'old_geoid': '30113',
            'old_name': 'Yellowstone National Park',
            'new_geoid': '30067',
            'new_name': 'Park County',
        },
    )
    frame, problems = build.synthesize_county_intervals(
        current(('30031', 'Gallatin County'), ('30067', 'Park County')), log
    )
    assert problems == []
    assert intervals_of(frame, '30113') == [('Yellowstone National Park', FLOOR, at)]
    assert intervals_of(frame, '30031') == [('Gallatin County', FLOOR, OPEN)]
    assert frame.filter(pl.col('county_geoid').eq('30113')).get_column('entity_type').to_list() == ['other']


def test_merge_closes_absorbed_city_and_keeps_county_open():
    at = date(2013, 7, 1)
    log = changes(
        {
            'change_type': 'merge',
            'effective_date': at,
            'old_geoid': '51515',
            'old_name': 'Bedford city',
            'new_geoid': '51019',
            'new_name': 'Bedford County',
        }
    )
    frame, problems = build.synthesize_county_intervals(current(('51019', 'Bedford County')), log)
    assert problems == []
    assert intervals_of(frame, '51515') == [('Bedford city', FLOOR, at)]
    assert intervals_of(frame, '51019') == [('Bedford County', FLOOR, OPEN)]
    assert frame.filter(pl.col('county_geoid').eq('51515')).get_column('entity_type').to_list() == ['independent_city']


def test_dissolve_and_create_group_swaps_code_sets():
    at = date(2022, 6, 6)
    log = changes(
        {
            'change_group': 'ct',
            'change_type': 'dissolve',
            'effective_date': at,
            'old_geoid': '09001',
            'old_name': 'Fairfield County',
        },
        {
            'change_group': 'ct',
            'change_type': 'create',
            'effective_date': at,
            'new_geoid': '09120',
            'new_name': 'Greater Bridgeport Planning Region',
            'creates_new': True,
        },
    )
    frame, problems = build.synthesize_county_intervals(
        current(('09120', 'Greater Bridgeport Planning Region')), log
    )
    assert problems == []
    assert intervals_of(frame, '09001') == [('Fairfield County', FLOOR, at)]
    assert intervals_of(frame, '09120') == [('Greater Bridgeport Planning Region', at, OPEN)]
    assert frame.filter(pl.col('county_geoid').eq('09120')).get_column('entity_type').to_list() == ['planning_region']


def test_chained_changes_open_and_close_in_order():
    '''02232 is born from a 1992 split and dies in a 2007 split; it must never be opened at the floor.'''
    born, died = date(1992, 9, 22), date(2007, 6, 20)
    log = changes(
        {
            'change_group': 'yakutat',
            'change_type': 'split',
            'effective_date': born,
            'old_geoid': '02231',
            'old_name': 'Skagway-Yakutat-Angoon Census Area',
            'new_geoid': '02232',
            'new_name': 'Skagway-Hoonah-Angoon Census Area',
            'creates_new': True,
        },
        {
            'change_group': 'skagway',
            'change_type': 'split',
            'effective_date': died,
            'old_geoid': '02232',
            'old_name': 'Skagway-Hoonah-Angoon Census Area',
            'new_geoid': '02230',
            'new_name': 'Skagway Municipality',
            'creates_new': True,
        },
    )
    frame, problems = build.synthesize_county_intervals(current(('02230', 'Skagway Municipality')), log)
    assert problems == []
    assert intervals_of(frame, '02231') == [('Skagway-Yakutat-Angoon Census Area', FLOOR, born)]
    assert intervals_of(frame, '02232') == [('Skagway-Hoonah-Angoon Census Area', born, died)]
    assert intervals_of(frame, '02230') == [('Skagway Municipality', died, OPEN)]


def test_closing_a_code_that_was_never_open_is_reported():
    log = changes(
        {
            'change_type': 'dissolve',
            'effective_date': date(2007, 6, 20),
            'old_geoid': '02232',
            'old_name': 'Skagway-Hoonah-Angoon Census Area',
        },
        {
            'change_type': 'dissolve',
            'effective_date': date(2010, 1, 1),
            'old_geoid': '02232',
            'old_name': 'Skagway-Hoonah-Angoon Census Area',
        },
    )
    _, problems = build.synthesize_county_intervals(current(('02230', 'Skagway Municipality')), log)
    assert len(problems) == 1
    assert '02232' in problems[0] and '2010-01-01' in problems[0]


def test_survivor_absent_from_gazetteer_is_reported():
    log = changes(
        {
            'change_type': 'merge',
            'effective_date': date(2013, 7, 1),
            'old_geoid': '51515',
            'old_name': 'Bedford city',
            'new_geoid': '51019',
            'new_name': 'Bedford County',
        }
    )
    _, problems = build.synthesize_county_intervals(current(('51001', 'Accomack County')), log)
    assert any('51019' in problem and 'neither open nor current' in problem for problem in problems)


def test_created_code_missing_from_gazetteer_is_reported():
    log = changes(
        {
            'change_type': 'create',
            'effective_date': date(2001, 11, 15),
            'new_geoid': '08014',
            'new_name': 'Broomfield County',
            'creates_new': True,
        }
    )
    _, problems = build.synthesize_county_intervals(current(('08001', 'Adams County')), log)
    assert any('08014' in problem and 'absent from the current gazetteer' in problem for problem in problems)


# --------------------------------------------------------------------------------------------
# Validators and readers
# --------------------------------------------------------------------------------------------


def test_validate_counties_flags_overlapping_intervals():
    frame = pl.DataFrame(
        {
            'county_geoid': ['01001', '01001'],
            'name': ['A', 'B'],
            'state_fips': ['01', '01'],
            'county_fips': ['001', '001'],
            'state_usps': ['AL', 'AL'],
            'entity_type': ['county', 'county'],
            'valid_from': [FLOOR, date(2000, 1, 1)],
            'valid_to': [date(2001, 1, 1), OPEN],
            'is_current': [False, True],
        }
    )
    problems = build.validate_counties(frame)
    assert any('overlapping' in problem for problem in problems)


@pytest.mark.parametrize(
    'row, message',
    [
        ('g,2001-11-15,rebrand,,,08014,Broomfield County,true,verified,', 'change_type'),
        ('g,2001-11-15,create,,,8014,Broomfield County,true,verified,', 'malformed'),
        ('g,1985-01-01,create,,,08014,Broomfield County,true,verified,', 'COVERAGE_FLOOR'),
    ],
)
def test_read_changes_rejects_structural_errors(tmp_path: Path, row: str, message: str):
    header = 'change_group,effective_date,change_type,old_geoid,old_name,new_geoid,new_name,creates_new,status,source_note'
    seed = tmp_path / 'county_changes.csv'
    seed.write_text(f'{header}\n{row}\n')
    with pytest.raises(ValueError, match=message):
        build.read_changes(seed)


def gazetteer_zip(path: Path, separator: str, trailing: str = '') -> Path:
    header = separator.join(['USPS', 'GEOID', 'GEOIDFQ', 'ANSICODE', 'NAME', 'ALAND', 'INTPTLONG']) + trailing
    rows = [
        separator.join(['AL', '01001', '0500000US01001', '00161526', 'Autauga County', '1539631460', '-86.64644']),
        separator.join(['CT', '09110', '0500000US09110', '02773932', 'Capitol Planning Region', '2373540208', '-72.69']),
    ]
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('gaz_counties.txt', '\n'.join([header, *rows]) + '\n')
    return path


@pytest.mark.parametrize('separator, trailing', [('|', ''), ('\t', '    ')])
def test_read_gazetteer_handles_pipe_and_tab_layouts(tmp_path: Path, separator: str, trailing: str):
    frame = build.read_gazetteer(gazetteer_zip(tmp_path / 'gaz.zip', separator, trailing))
    assert frame.columns == ['county_geoid', 'name', 'state_usps']
    assert frame.get_column('county_geoid').to_list() == ['01001', '09110']
    assert frame.get_column('name').to_list() == ['Autauga County', 'Capitol Planning Region']


@pytest.mark.parametrize(
    'geoid, name, expected',
    [
        ('22001', 'Acadia Parish', 'parish'),
        ('02020', 'Anchorage Municipality', 'municipality'),
        ('02110', 'Juneau City and Borough', 'city_and_borough'),
        ('02016', 'Aleutians West Census Area', 'census_area'),
        ('02013', 'Aleutians East Borough', 'borough'),
        ('51510', 'Alexandria city', 'independent_city'),
        ('24510', 'Baltimore city', 'independent_city'),
        ('32510', 'Carson City', 'independent_city'),
        ('11001', 'District of Columbia', 'district'),
        ('72001', 'Adjuntas Municipio', 'municipio'),
        ('09110', 'Capitol Planning Region', 'planning_region'),
        ('51830', 'Williamsburg city', 'independent_city'),
        ('51095', 'James City County', 'county'),
    ],
)
def test_entity_type_classification(geoid: str, name: str, expected: str):
    frame = pl.DataFrame({'county_geoid': [geoid], 'name': [name]}).with_columns(
        entity_type=build.entity_type_expr('name', 'county_geoid')
    )
    assert frame.get_column('entity_type').to_list() == [expected]


# --------------------------------------------------------------------------------------------
# CBSA delineations
# --------------------------------------------------------------------------------------------


def cbsa_rows(*rows: tuple[str, str, str, str | None, str]) -> pl.DataFrame:
    '''(delineation, cbsa_code, county_geoid, metdiv_code, cbsa_type) with the remaining columns filled.'''
    return pl.DataFrame(
        {
            'delineation': [row[0] for row in rows],
            'bulletin': ['x' for _ in rows],
            'cbsa_code': [row[1] for row in rows],
            'cbsa_title': ['Title' for _ in rows],
            'cbsa_type': [row[4] for row in rows],
            'metdiv_code': [row[3] for row in rows],
            'metdiv_title': [None for _ in rows],
            'csa_code': [None for _ in rows],
            'csa_title': [None for _ in rows],
            'county_geoid': [row[2] for row in rows],
            'county_name': ['County' for _ in rows],
            'central_outlying': ['central' for _ in rows],
            'valid_from': [date(2023, 7, 21) for _ in rows],
            'valid_to': [OPEN for _ in rows],
        },
        schema_overrides={'metdiv_code': pl.Utf8, 'metdiv_title': pl.Utf8, 'csa_code': pl.Utf8, 'csa_title': pl.Utf8},
    )


def test_derive_cbsa_counts_counties_divisions_and_states():
    frame = build.derive_cbsa(
        cbsa_rows(
            ('2023', '35620', '36061', '35614', 'metropolitan'),
            ('2023', '35620', '34017', '35614', 'metropolitan'),
            ('2023', '35620', '36059', '35004', 'metropolitan'),
            ('2023', '10100', '46013', None, 'micropolitan'),
        )
    )
    new_york = frame.filter(pl.col('cbsa_code').eq('35620')).row(0, named=True)
    assert (new_york['n_counties'], new_york['n_metdivs'], new_york['states']) == (3, 2, '34,36')
    aberdeen = frame.filter(pl.col('cbsa_code').eq('10100')).row(0, named=True)
    assert (aberdeen['n_counties'], aberdeen['n_metdivs'], aberdeen['cbsa_type']) == (1, 0, 'micropolitan')


def test_interval_referential_check_catches_code_retired_before_bulletin():
    counties = pl.DataFrame(
        {
            'county_geoid': ['09001', '09120'],
            'valid_from': [FLOOR, date(2022, 6, 6)],
            'valid_to': [date(2022, 6, 6), OPEN],
        }
    )
    stale = cbsa_rows(('2023', '14860', '09001', None, 'metropolitan'))
    fresh = cbsa_rows(('2023', '14860', '09120', None, 'metropolitan'))
    assert build.interval_referential_check(fresh, counties) == []
    problems = build.interval_referential_check(stale, counties)
    assert len(problems) == 1 and '09001' in problems[0]


def test_delineations_are_chronological_with_distinct_source_names():
    effective = [delineation.effective for delineation in build.DELINEATIONS]
    assert effective == sorted(effective) and len(set(effective)) == len(effective)
    names = [delineation.source_name for delineation in build.DELINEATIONS]
    assert len(set(names)) == len(names)


@pytest.mark.parametrize('delineation', build.DELINEATIONS, ids=lambda d: d.label)
def test_parse_each_bundled_delineation_workbook(delineation: build.Delineation):
    source = SOURCES / delineation.source_name
    if not source.exists():
        pytest.skip(f'{source.name} not cached under sources/')
    frame = build.parse_delineation(source, delineation, OPEN)
    assert frame.get_column('delineation').unique().to_list() == [delineation.label]
    assert frame.get_column('bulletin').unique().to_list() == [delineation.bulletin]
    assert frame.get_column('county_geoid').str.contains(r'^\d{5}$').all()
    assert frame.get_column('cbsa_type').is_in(['metropolitan', 'micropolitan']).all()
    # Every vintage carries the eleven-plus metropolitan divisions; a header mismatch would zero this.
    assert frame.get_column('metdiv_code').drop_nulls().n_unique() >= 29
    assert build.validate_cbsa_counties(frame) == []

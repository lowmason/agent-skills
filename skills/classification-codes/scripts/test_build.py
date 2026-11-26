'''Tests for build.py — the parsers and validators, driven by synthetic raw sheets that mimic the
Census / BLS workbook layouts (preamble rows, legend rows, ranged sector codes, trailing-space
titles, trilateral markers, one-code-column-per-row SOC sheets).

Run from this directory:
  uv run --with pytest --with polars --with fastexcel python -m pytest -q

The parsers take an already-read raw frame (every cell Utf8, no header), so no workbook is
needed here; end-to-end parsing of the real sources is exercised by test_real_sources.py when
sources/ is populated.
'''

from __future__ import annotations

import hashlib
import re
import urllib.request
from pathlib import Path

import polars as pl
import pytest

import build

# --------------------------------------------------------------------------------------------
# Fixtures: raw sheets in the shape pl.read_excel(has_header=False) returns
# --------------------------------------------------------------------------------------------


def raw_sheet(rows: list[list[str | None]]) -> pl.DataFrame:
  width = max(len(row) for row in rows)
  padded = [list(row) + [None] * (width - len(row)) for row in rows]
  return pl.DataFrame(
    padded, schema=[f'column_{index}' for index in range(width)], orient='row'
  ).select(pl.all().cast(pl.Utf8))


NAICS_LEGEND = (
  'T = trilateral agreement (United States, Canada, and Mexico)\n\n'
  'Note for Indicator field:     * = title change, no content change\n'
  '** = new code for 2022 NAICS\n*** = re-used code, content change'
)


@pytest.fixture
def naics_structure_raw() -> pl.DataFrame:
  # The legend row contains "2022", "code", and "title" as substrings of ONE cell — the trap a
  # joined-string header match falls into. Titles carry the Census trailing space.
  return raw_sheet([
    ['2022 NAICS Structure'],
    [NAICS_LEGEND],
    ['Change Indicator', '2022 NAICS Code', '2022 NAICS Title'],
    [None, '31-33', 'ManufacturingT '],
    [None, '311', 'Food ManufacturingT'],
    [None, '3111', 'Animal Food ManufacturingT '],
    [None, '31111', 'Animal Food ManufacturingT'],
    ['**', '311111', 'Dog and Cat Food Manufacturing '],
    [None, '311119', 'Other Animal Food Manufacturing'],
    [None, '44-45', 'Retail TradeT'],
    ['***', '449', 'Furniture, Home Furnishings, Electronics, and Appliance Retailers'],
    [None, '48-49', 'Transportation and WarehousingT'],
    [None, '481', 'Air TransportationT'],
    [None, '92', 'Public AdministrationT'],
    [None, '928', 'National Security and International AffairsT'],
    [None, '9281', 'National Security and International AffairsT'],
    [None, '92811', 'National SecurityT'],
    [None, '928110', 'National Security'],
    [None, None, None],
  ])


@pytest.fixture
def naics_concordance_raw() -> pl.DataFrame:
  return raw_sheet([
    ['2017 NAICS U.S. Matched to 2022 NAICS U.S. (Full Concordance)'],
    [
      '(Note:  2022 NAICS codes in bold indicate pieces of the 2022 industry came from more than '
      'one 2017 NAICS industry; 2017 NAICS codes in italics indicate the 2017 industry split to '
      'two or more 2022 NAICS industries.)'
    ],
    # The real source-title header carries a note line that names the TARGET vintage too — a
    # substring match over the whole cell returns this column for ('2022', 'title').
    ['2017 NAICS Code',
     '2017 NAICS Title\n(and specific piece of the 2017 industry that is contained in the 2022 industry)',
     '2022 NAICS Code', '2022 NAICS Title'],
    ['111110', 'Soybean Farming', '111110', 'Soybean Farming'],
    ['454110', 'Electronic Shopping and Mail-Order Houses (pt.)', '449210', 'Electronics and Appliance Retailers'],
    ['454110', 'Electronic Shopping and Mail-Order Houses (pt.)', '455110', 'Department Stores'],
    ['452210', 'Department Stores', '455110', 'Department Stores'],
    ['454390', 'Other Direct Selling Establishments', '459999', 'All Other Miscellaneous Retailers'],
    ['453998', 'All Other Miscellaneous Store Retailers (pt.)', '459999', 'All Other Miscellaneous Retailers'],
    ['454110', 'Electronic Shopping and Mail-Order Houses (pt.)', '449210', 'Electronics and Appliance Retailers'],
    [None, None, None, None],
    ['Total', None, None, None],
  ])


@pytest.fixture
def soc_structure_raw() -> pl.DataFrame:
  # BLS structure sheets carry one code column per level, exactly one populated per row, and the
  # title column's header is blank — so it must be found by content, not by name.
  return raw_sheet([
    ['2018 Standard Occupational Classification'],
    ['Major Group', 'Minor Group', 'Broad Group', 'Detailed Occupation', None],
    ['11-0000', None, None, None, 'Management Occupations'],
    [None, '11-1000', None, None, 'Top Executives'],
    [None, None, '11-1010', None, 'Chief Executives'],
    [None, None, None, '11-1011', 'Chief Executives'],
    [None, None, '11-1020', None, 'General and Operations Managers'],
    [None, None, None, '11-1021', 'General and Operations Managers'],
    ['15-0000', None, None, None, 'Computer and Mathematical Occupations'],
    [None, '15-1200', None, None, 'Computer Occupations'],
    [None, None, '15-1250', None, 'Software and Web Developers, Programmers, and Testers'],
    [None, None, None, '15-1252', 'Software Developers'],
    # The 2018 SOC overflows the positional pattern: broad group 29-1210 Physicians holds
    # 29-1211..29-1218 AND 29-1221..29-1229 (there is no 29-1220). Only the sheet's nesting
    # says where 29-122x belong.
    ['29-0000', None, None, None, 'Healthcare Practitioners and Technical Occupations'],
    [None, '29-1000', None, None, 'Healthcare Diagnosing or Treating Practitioners'],
    [None, None, '29-1210', None, 'Physicians'],
    [None, None, None, '29-1211', 'Anesthesiologists'],
    [None, None, None, '29-1218', 'Obstetricians and Gynecologists'],
    [None, None, None, '29-1221', 'Pediatricians, General'],
    [None, None, None, '29-1229', 'Physicians, All Other'],
    [None, None, '29-1240', None, 'Surgeons'],
    [None, None, None, '29-1241', 'Ophthalmologists, Except Pediatric'],
    ['51-0000', None, None, None, 'Production Occupations'],
    [None, '51-9000', None, None, 'Other Production Workers'],
    [None, None, '51-9190', None, 'Miscellaneous Production Workers'],
    [None, None, None, '51-9199', 'Production Workers, All Other'],
    [None, None, None, None, None],
  ])


# --------------------------------------------------------------------------------------------
# Generic helpers
# --------------------------------------------------------------------------------------------


def test_frame_below_header_skips_single_cell_note_rows(naics_concordance_raw):
  body = build.frame_below_header(naics_concordance_raw, ['2017', '2022', 'code'])
  assert body.columns[0] == '2017 NAICS Code'
  assert body.columns[2] == '2022 NAICS Code'
  assert body.row(0)[0] == '111110'


def test_frame_below_header_dedupes_and_names_blank_headers(soc_structure_raw):
  body = build.frame_below_header(soc_structure_raw, ['major group'])
  assert body.columns == ['Major Group', 'Minor Group', 'Broad Group', 'Detailed Occupation', 'col_4']


def test_frame_below_header_raises_when_layout_changed(soc_structure_raw):
  with pytest.raises(ValueError, match='layout changed'):
    build.frame_below_header(soc_structure_raw, ['sector'])


def test_code_expr_strips_excel_float_suffix():
  frame = pl.DataFrame({'c': [' 111110.0 ', '31-33', '11-1011', None]})
  assert frame.select(build.code_expr('c')).to_series().to_list() == ['111110', '31-33', '11-1011', None]


def test_hyphenate_soc_only_touches_bare_six_digit_codes():
  frame = pl.DataFrame({'c': ['111011', '11-1011', '111110.0']})
  assert frame.select(build.hyphenate_soc(pl.col('c'))).to_series().to_list() == ['11-1011', '11-1011', '111110.0']


@pytest.mark.parametrize(
  ('title', 'expected'),
  [
    ('Crop ProductionT', 'Crop Production'),
    ('Oilseed (except Soybean) FarmingT', 'Oilseed (except Soybean) Farming'),
    ('Soybean Farming', 'Soybean Farming'),
    ('Support Activities for ATM', 'Support Activities for ATM'),  # acronym-final title is not a marker
  ],
)
def test_strip_trilateral_marker(title, expected):
  frame = pl.DataFrame({'t': [title]})
  assert frame.select(build.strip_trilateral_marker(pl.col('t'))).item() == expected


# --------------------------------------------------------------------------------------------
# NAICS structure
# --------------------------------------------------------------------------------------------


def test_parse_naics_structure_columns_and_levels(naics_structure_raw):
  frame = build.parse_naics_structure(naics_structure_raw, vintage=2022)
  assert frame.columns == ['code', 'level', 'title', 'parent_code', 'sector_code', 'trilateral', 'change_indicator']
  levels = dict(zip(frame['code'], frame['level']))
  assert levels['31-33'] == 2 and levels['311'] == 3 and levels['3111'] == 4
  assert levels['31111'] == 5 and levels['311111'] == 6
  assert frame.height == 15  # the blank trailing row is dropped


def test_parse_naics_structure_resolves_ranged_sectors(naics_structure_raw):
  frame = build.parse_naics_structure(naics_structure_raw, vintage=2022)
  sector = dict(zip(frame['code'], frame['sector_code']))
  assert sector['311'] == '31-33' and sector['311111'] == '31-33'
  assert sector['449'] == '44-45'
  assert sector['481'] == '48-49'
  assert sector['928110'] == '92'
  assert sector['31-33'] == '31-33'


def test_parse_naics_structure_parents(naics_structure_raw):
  frame = build.parse_naics_structure(naics_structure_raw, vintage=2022)
  parent = dict(zip(frame['code'], frame['parent_code']))
  assert parent['31-33'] is None
  assert parent['311'] == '31-33'   # subsector parents to the ranged sector, not to '31'
  assert parent['3111'] == '311'
  assert parent['311111'] == '31111'
  assert parent['481'] == '48-49'


def test_parse_naics_structure_trilateral_and_titles(naics_structure_raw):
  frame = build.parse_naics_structure(naics_structure_raw, vintage=2022)
  rows = {code: (title, tri) for code, title, tri in zip(frame['code'], frame['title'], frame['trilateral'])}
  assert rows['31-33'] == ('Manufacturing', True)          # trailing space then marker
  assert rows['3111'] == ('Animal Food Manufacturing', True)
  assert rows['311111'] == ('Dog and Cat Food Manufacturing', False)
  assert rows['449'][1] is False
  assert not any(title.endswith('T') and tri for title, tri in rows.values())


def test_parse_naics_structure_change_indicator(naics_structure_raw):
  frame = build.parse_naics_structure(naics_structure_raw, vintage=2022)
  change = dict(zip(frame['code'], frame['change_indicator']))
  assert change['311111'] == '**'
  assert change['449'] == '***'
  assert change['311'] is None


def test_parse_naics_structure_is_sorted_hierarchically(naics_structure_raw):
  codes = build.parse_naics_structure(naics_structure_raw, vintage=2022)['code'].to_list()
  assert codes == sorted(codes)
  assert codes.index('31-33') < codes.index('311') < codes.index('311111')


def test_validate_naics_flags_orphans_duplicates_and_bad_indicators(naics_structure_raw):
  frame = build.parse_naics_structure(naics_structure_raw, vintage=2022)
  broken = pl.concat([
    frame,
    frame.filter(pl.col('code').eq('311')),  # duplicate
    frame.filter(pl.col('code').eq('3111')).with_columns(
      code=pl.lit('3199'), parent_code=pl.lit('319'), change_indicator=pl.lit('?')
    ),  # orphan + unknown indicator
  ])
  problems = build.validate_naics(broken, vintage=2022)
  assert any('duplicated' in p for p in problems)
  assert any('parent_code is missing' in p for p in problems)
  assert any('change_indicator' in p for p in problems)


def test_validate_naics_requires_twenty_sectors(naics_structure_raw):
  problems = build.validate_naics(build.parse_naics_structure(naics_structure_raw, vintage=2022), vintage=2022)
  assert any('expected 20 sectors' in p for p in problems)


# --------------------------------------------------------------------------------------------
# NAICS concordance
# --------------------------------------------------------------------------------------------


def test_parse_naics_concordance_columns_and_filtering(naics_concordance_raw):
  frame = build.parse_naics_concordance(naics_concordance_raw, source_vintage=2017, target_vintage=2022)
  assert frame.columns == ['naics_2017', 'title_2017', 'naics_2022', 'title_2022', 'link_type']
  assert frame.height == 6  # blank row, 'Total' row, and the exact duplicate row are gone
  assert frame['naics_2017'].str.contains(r'^\d{6}$').all()


def test_parse_naics_concordance_keeps_source_and_target_titles_apart(naics_concordance_raw):
  frame = build.parse_naics_concordance(naics_concordance_raw, source_vintage=2017, target_vintage=2022)
  row = frame.filter(pl.col('naics_2017').eq('454110').and_(pl.col('naics_2022').eq('449210'))).row(0, named=True)
  assert row['title_2017'] == 'Electronic Shopping and Mail-Order Houses (pt.)'
  assert row['title_2022'] == 'Electronics and Appliance Retailers'


def test_find_col_matches_on_the_header_name_line_only():
  columns = ['2017 NAICS Code', '2017 NAICS Title\n(piece contained in the 2022 industry)', '2022 NAICS Code', '2022 NAICS Title']
  assert build.find_col(columns, '2022', 'title') == '2022 NAICS Title'
  assert build.find_col(columns, '2017', 'title').startswith('2017 NAICS Title')


def test_parse_naics_concordance_link_types(naics_concordance_raw):
  frame = build.parse_naics_concordance(naics_concordance_raw, source_vintage=2017, target_vintage=2022)
  link = {(s, t): l for s, t, l in zip(frame['naics_2017'], frame['naics_2022'], frame['link_type'])}
  assert link[('111110', '111110')] == '1:1'
  assert link[('454110', '449210')] == '1:m'   # source splits, this target has one source
  assert link[('454110', '455110')] == 'm:m'   # source splits AND target merges
  assert link[('452210', '455110')] == 'm:1'   # source is whole, target merges
  assert link[('454390', '459999')] == 'm:1'
  assert link[('453998', '459999')] == 'm:1'


def test_link_type_exprs_on_a_pure_one_to_one_frame():
  frame = pl.DataFrame({'a': ['1', '2'], 'b': ['x', 'y']})
  assert frame.with_columns(build.link_type_exprs('a', 'b'))['link_type'].to_list() == ['1:1', '1:1']


# --------------------------------------------------------------------------------------------
# SOC structure
# --------------------------------------------------------------------------------------------


def test_parse_soc_structure_levels_from_columns(soc_structure_raw):
  frame = build.parse_soc_structure(soc_structure_raw, vintage=2018)
  assert frame.columns == ['code', 'level', 'title', 'parent_code']
  level = dict(zip(frame['code'], frame['level']))
  assert level['11-0000'] == 'major'
  assert level['11-1000'] == 'minor'
  assert level['11-1010'] == 'broad'
  assert level['11-1011'] == 'detailed'
  assert frame.height == 23


def test_parse_soc_structure_finds_blank_headed_title_column(soc_structure_raw):
  frame = build.parse_soc_structure(soc_structure_raw, vintage=2018)
  title = dict(zip(frame['code'], frame['title']))
  assert title['15-1252'] == 'Software Developers'
  assert title['51-9199'] == 'Production Workers, All Other'


def test_parse_soc_structure_parents_use_stems_not_digit_surgery(soc_structure_raw):
  frame = build.parse_soc_structure(soc_structure_raw, vintage=2018)
  parent = dict(zip(frame['code'], frame['parent_code']))
  assert parent['11-0000'] is None
  assert parent['11-1000'] == '11-0000'
  assert parent['11-1010'] == '11-1000'
  assert parent['11-1011'] == '11-1010'
  assert parent['11-1021'] == '11-1020'
  assert parent['15-1250'] == '15-1200'   # longest stem wins over the 15-1000-style minor
  assert parent['51-9190'] == '51-9000'   # XX-YY00 minor: naive slicing would want 51-9100
  assert parent['51-9199'] == '51-9190'


def test_parse_soc_structure_overflow_codes_parent_by_sheet_nesting(soc_structure_raw):
  frame = build.parse_soc_structure(soc_structure_raw, vintage=2018)
  parent = dict(zip(frame['code'], frame['parent_code']))
  assert parent['29-1211'] == '29-1210'
  assert parent['29-1221'] == '29-1210'   # no stem match exists; the sheet nests it under Physicians
  assert parent['29-1229'] == '29-1210'
  assert parent['29-1241'] == '29-1240'   # the next broad group resets the nesting
  assert frame.filter(pl.col('level').ne('major').and_(pl.col('parent_code').is_null())).height == 0


def test_parse_soc_structure_rejects_nesting_that_contradicts_the_code_pattern():
  raw = raw_sheet([
    ['Major Group', 'Minor Group', 'Broad Group', 'Detailed Occupation', 'Title'],
    ['11-0000', None, None, None, 'Management Occupations'],
    [None, '11-1000', None, None, 'Top Executives'],
    [None, None, '11-1010', None, 'Chief Executives'],
    [None, None, '11-1020', None, 'General and Operations Managers'],
    [None, None, None, '11-1011', 'Chief Executives'],  # listed under 11-1020, but its stem says 11-1010
  ])
  with pytest.raises(ValueError, match='conflict'):
    build.parse_soc_structure(raw, vintage=2018)


def test_parse_soc_structure_hyphenates_bare_codes():
  raw = raw_sheet([
    ['Major Group', 'Minor Group', 'Broad Group', 'Detailed Occupation', 'Title'],
    ['110000', None, None, None, 'Management Occupations'],
    [None, '111000', None, None, 'Top Executives'],
  ])
  frame = build.parse_soc_structure(raw, vintage=2010)
  assert frame['code'].to_list() == ['11-0000', '11-1000']


def test_soc_pattern_level_matches_column_levels(soc_structure_raw):
  frame = build.parse_soc_structure(soc_structure_raw, vintage=2018)
  disagreements = frame.filter(build.soc_pattern_level().ne(pl.col('level'))).height
  assert disagreements == 0


def test_validate_soc_flags_unparented_and_duplicate_codes(soc_structure_raw):
  frame = build.parse_soc_structure(soc_structure_raw, vintage=2018)
  broken = pl.concat([
    frame,
    frame.filter(pl.col('code').eq('11-1011')),
    pl.DataFrame({'code': ['99-9999'], 'level': ['detailed'], 'title': ['Nowhere'], 'parent_code': [None]},
                 schema_overrides={'parent_code': pl.Utf8}),
  ])
  problems = build.validate_soc(broken, vintage=2018)
  assert any('duplicated' in p for p in problems)
  assert any('no resolvable parent' in p for p in problems)
  assert any('expected 23 major groups' in p for p in problems)


# --------------------------------------------------------------------------------------------
# SOC crosswalk
# --------------------------------------------------------------------------------------------


@pytest.fixture
def soc_crosswalk_raw() -> pl.DataFrame:
  # BLS marks a 2010 title "(#)" when that code splits and a 2018 title "(##)" when that code
  # merges — the same facts link_type derives from multiplicities.
  return raw_sheet([
    ['U.S. Bureau of Labor Statistics'],
    ['2010 SOC Code', '2010 SOC Title', '2018 SOC Code', '2018 SOC Title'],
    ['15-1131', 'Computer Programmers', '15-1251', 'Computer Programmers'],
    ['15-1132', 'Software Developers, Applications (#)', '15-1252', 'Software Developers (##)'],
    ['15-1132', 'Software Developers, Applications (#)', '15-1253', 'Software Quality Assurance Analysts and Testers (##)'],
    ['15-1133', 'Software Developers, Systems Software (#)', '15-1252', 'Software Developers (##)'],
    ['15-1133', 'Software Developers, Systems Software (#)', '15-1253', 'Software Quality Assurance Analysts and Testers (##)'],
    ['151134', 'Web Developers (#)', '15-1254', 'Web Developers'],
    ['151134', 'Web Developers (#)', '15-1255', 'Web and Digital Interface Designers (##)'],
    ['15-1199', 'Computer Occupations, All Other (#)', '15-1255', 'Web and Digital Interface Designers (##)'],
    ['15-1199', 'Computer Occupations, All Other (#)', '15-1299', 'Computer Occupations, All Other'],
  ])


def test_parse_soc_crosswalk_hyphenates_and_types_links(soc_crosswalk_raw):
  frame = build.parse_soc_crosswalk(soc_crosswalk_raw, source_vintage=2010, target_vintage=2018)
  assert frame.columns == ['soc_2010', 'title_2010', 'soc_2018', 'title_2018', 'link_type']
  link = {(s, t): l for s, t, l in zip(frame['soc_2010'], frame['soc_2018'], frame['link_type'])}
  assert link[('15-1131', '15-1251')] == '1:1'
  assert link[('15-1132', '15-1252')] == 'm:m'
  assert link[('15-1134', '15-1254')] == '1:m'
  assert link[('15-1199', '15-1255')] == 'm:m'
  assert link[('15-1199', '15-1299')] == '1:m'


def test_parse_soc_crosswalk_strips_bls_split_merge_markers(soc_crosswalk_raw):
  frame = build.parse_soc_crosswalk(soc_crosswalk_raw, source_vintage=2010, target_vintage=2018)
  row = frame.filter(pl.col('soc_2010').eq('15-1132').and_(pl.col('soc_2018').eq('15-1252'))).row(0, named=True)
  assert row['title_2010'] == 'Software Developers, Applications'
  assert row['title_2018'] == 'Software Developers'
  assert not frame['title_2010'].str.contains('#').any()
  assert not frame['title_2018'].str.contains('#').any()


def test_parse_soc_crosswalk_rejects_markers_that_disagree_with_link_type():
  raw = raw_sheet([
    ['2010 SOC Code', '2010 SOC Title', '2018 SOC Code', '2018 SOC Title'],
    ['11-1011', 'Chief Executives (#)', '11-1011', 'Chief Executives'],  # marked as a split, but one row
    ['11-1021', 'General and Operations Managers', '11-1021', 'General and Operations Managers'],
  ])
  with pytest.raises(ValueError, match='marker'):
    build.parse_soc_crosswalk(raw, source_vintage=2010, target_vintage=2018)


def test_parse_soc_crosswalk_without_markers_skips_the_marker_check():
  raw = raw_sheet([
    ['2010 SOC Code', '2010 SOC Title', '2018 SOC Code', '2018 SOC Title'],
    ['15-1134', 'Web Developers', '15-1254', 'Web Developers'],
    ['15-1134', 'Web Developers', '15-1255', 'Web and Digital Interface Designers'],
  ])
  frame = build.parse_soc_crosswalk(raw, source_vintage=2010, target_vintage=2018)
  assert frame['link_type'].to_list() == ['1:m', '1:m']


# --------------------------------------------------------------------------------------------
# Cross-file checks and registry
# --------------------------------------------------------------------------------------------


def test_referential_checks_report_codes_missing_from_structure(naics_structure_raw, naics_concordance_raw):
  structure = build.parse_naics_structure(naics_structure_raw, vintage=2022)
  concordance = build.parse_naics_concordance(naics_concordance_raw, source_vintage=2017, target_vintage=2022)
  problems = build.referential_checks({'naics_2022': structure, 'naics_2017_to_2022': concordance})
  # none of the synthetic 2022 retail codes exist in the tiny structure fixture
  assert len(problems) == 1
  assert 'naics_2022 codes not found' in problems[0]
  assert build.referential_checks({'naics_2022': structure}) == []


def test_registry_names_are_unique_and_match_output_files():
  names = [b.name for b in build.BUILDS]
  assert len(names) == len(set(names))
  assert {'naics_2022', 'naics_2017', 'naics_2012', 'naics_2017_to_2022', 'naics_2012_to_2017',
          'soc_2018', 'soc_2010', 'soc_2010_to_2018',
          'census_occ_2018', 'census_occ_2018_to_soc_2018',
          'census_occ_2010', 'census_occ_2010_to_soc_2010',
          'census_ind_2022', 'census_ind_2022_to_naics_2022',
          'census_ind_2017', 'census_ind_2017_to_naics_2017'} <= set(names)


def test_registry_requirements_are_registered_and_built_first():
  order = [b.name for b in build.BUILDS]
  for b in build.BUILDS:
    for required in b.requires:
      assert required in order
      assert order.index(required) < order.index(b.name)
  derived = [b for b in build.BUILDS if b.url is None]
  assert derived and all(b.requires for b in derived)


# --------------------------------------------------------------------------------------------
# Census occupation codes (the ACS/CPS household-survey aggregation of SOC)
# --------------------------------------------------------------------------------------------


@pytest.fixture
def soc_for_census() -> pl.DataFrame:
  rows = [
    ('11-0000', 'major', 'Management Occupations', None),
    ('11-1000', 'minor', 'Top Executives', '11-0000'),
    ('11-1010', 'broad', 'Chief Executives', '11-1000'),
    ('11-1011', 'detailed', 'Chief Executives', '11-1010'),
    ('11-1020', 'broad', 'General and Operations Managers', '11-1000'),
    ('11-1021', 'detailed', 'General and Operations Managers', '11-1020'),
    ('11-1030', 'broad', 'Legislators', '11-1000'),
    ('11-1031', 'detailed', 'Legislators', '11-1030'),
    ('11-2000', 'minor', 'Advertising, Marketing, Promotions, Public Relations, and Sales Managers', '11-0000'),
    ('11-2030', 'broad', 'Public Relations and Fundraising Managers', '11-2000'),
    ('11-2032', 'detailed', 'Public Relations Managers', '11-2030'),
    ('11-2033', 'detailed', 'Fundraising Managers', '11-2030'),
    ('11-3000', 'minor', 'Operations Specialties Managers', '11-0000'),
    ('11-3010', 'broad', 'Administrative Services and Facilities Managers', '11-3000'),
    ('11-3012', 'detailed', 'Administrative Services Managers', '11-3010'),
    ('11-3013', 'detailed', 'Facilities Managers', '11-3010'),
    ('11-3020', 'broad', 'Computer and Information Systems Managers', '11-3000'),
    ('11-3021', 'detailed', 'Computer and Information Systems Managers', '11-3020'),
    ('15-0000', 'major', 'Computer and Mathematical Occupations', None),
    ('15-1200', 'minor', 'Computer Occupations', '15-0000'),
    ('15-1240', 'broad', 'Database and Network Administrators and Architects', '15-1200'),
    ('15-1241', 'detailed', 'Computer Network Architects', '15-1240'),
    ('15-1242', 'detailed', 'Database Administrators', '15-1240'),
    ('15-1243', 'detailed', 'Database Architects', '15-1240'),
    ('15-1244', 'detailed', 'Network and Computer Systems Administrators', '15-1240'),
    ('15-1250', 'broad', 'Software and Web Developers, Programmers, and Testers', '15-1200'),
    ('15-1252', 'detailed', 'Software Developers', '15-1250'),
    ('15-1253', 'detailed', 'Software Quality Assurance Analysts and Testers', '15-1250'),
    ('15-1290', 'broad', 'Miscellaneous Computer Occupations', '15-1200'),
    ('15-1299', 'detailed', 'Computer Occupations, All Other', '15-1290'),
  ]
  return pl.DataFrame(rows, schema=['code', 'level', 'title', 'parent_code'], orient='row')


@pytest.fixture
def census_occ_raw() -> pl.DataFrame:
  # Heading rows carry code RANGES; the title header is "Title" in 2018 and "Description" in
  # 2010; SOC cells are a detailed code, a broad or minor group, a remainder pattern with X
  # placeholders, or the word none.
  return raw_sheet([
    [None, 'U.S. Census Bureau'],
    [None, '2018 Census Occupation Code List'],
    [None, 'last updated: September 26, 2019'],
    [None, '2018 Census Title ', '2018 Census Code', '2018 SOC Code'],
    [None, 'The 2018 census occupation classification list has been updated ...'],
    ['Management,  Business, Science, and Arts Occupations:', None, '0010-3550', '11-0000 - 29-0000'],
    [None, 'Management Occupations:', '0010-0440', '11-0000'],
    [None, 'Chief executives', '0010', '11-1011'],
    [None, 'Other top executives', '0015', '11-1XXX'],
    [None, 'General and operations managers', '0020', '11-1021'],
    [None, 'Public relations and fundraising managers', '0060', '11-2030'],
    [None, 'Operations specialties managers', '0100', '11-3000'],
    [None, 'Computer network architects', '1050', '15-1241'],
    [None, 'Database administrators and architects', '1065', '15-124X'],
    [None, 'Network and computer systems administrators', '1108', '15-1244'],
    [None, 'Software developers', '1021', '15-1252'],
    [None, 'Other computer occupations', '1240', '15-12XX'],
    [None, 'Military, rank not specified', '9830', 'none'],
    [None, 'Legend'],
  ])


def test_parse_census_occ_list_as_published(census_occ_raw, soc_for_census):
  frame = build.parse_census_occ(census_occ_raw, vintage=2018, soc_2018=soc_for_census)
  assert frame.columns == ['census_occ', 'title', 'soc_code', 'soc_level']
  assert frame['census_occ'].to_list() == ['0010', '0015', '0020', '0060', '0100', '1021', '1050', '1065', '1108', '1240', '9830']
  rows = {r['census_occ']: r for r in frame.iter_rows(named=True)}
  assert rows['0010'] == {'census_occ': '0010', 'title': 'Chief executives', 'soc_code': '11-1011', 'soc_level': 'detailed'}
  assert (rows['0060']['soc_code'], rows['0060']['soc_level']) == ('11-2030', 'broad')
  assert (rows['0100']['soc_code'], rows['0100']['soc_level']) == ('11-3000', 'minor')
  assert (rows['0015']['soc_code'], rows['0015']['soc_level']) == ('11-1XXX', 'remainder')
  assert (rows['1065']['soc_code'], rows['1065']['soc_level']) == ('15-124X', 'remainder')
  assert (rows['9830']['soc_code'], rows['9830']['soc_level']) == (None, 'none')


def test_parse_census_occ_accepts_description_header(census_occ_raw, soc_for_census):
  raw = census_occ_raw.with_columns(
    pl.when(pl.col('column_1').eq('2018 Census Title ')).then(pl.lit('Occupation 2018 Description')).otherwise(pl.col('column_1')).alias('column_1')
  )
  frame = build.parse_census_occ(raw, vintage=2018, soc_2018=soc_for_census)
  assert frame.filter(pl.col('census_occ').eq('0010'))['title'].item() == 'Chief executives'


def test_parse_census_occ_rejects_soc_codes_missing_from_structure(census_occ_raw, soc_for_census):
  raw = census_occ_raw.with_columns(pl.col('column_3').str.replace('^11-1011$', '11-9999'))
  with pytest.raises(ValueError, match='11-9999'):
    build.parse_census_occ(raw, vintage=2018, soc_2018=soc_for_census)


def test_parse_census_occ_rejects_unknown_soc_cell_shapes(census_occ_raw, soc_for_census):
  raw = census_occ_raw.with_columns(pl.col('column_3').str.replace('^15-124X$', '15-1242, 15-1243'))
  with pytest.raises(ValueError, match='SOC cell'):
    build.parse_census_occ(raw, vintage=2018, soc_2018=soc_for_census)


def test_expand_census_occ_partitions_detailed_soc(census_occ_raw, soc_for_census):
  census = build.parse_census_occ(census_occ_raw, vintage=2018, soc_2018=soc_for_census)
  frame = build.expand_census_occ(vintage=2018, census_occ_2018=census, soc_2018=soc_for_census)
  assert frame.columns == ['census_occ_2018', 'census_title_2018', 'soc_2018', 'soc_title_2018', 'via']
  pairs = {(r['census_occ_2018'], r['soc_2018']): r['via'] for r in frame.iter_rows(named=True)}
  assert pairs[('0010', '11-1011')] == 'detailed'
  assert pairs[('0015', '11-1031')] == 'remainder'        # the rest of 11-1xxx after the exact claims
  assert pairs[('0060', '11-2032')] == 'broad' and pairs[('0060', '11-2033')] == 'broad'
  assert pairs[('0100', '11-3012')] == 'minor' and pairs[('0100', '11-3021')] == 'minor'  # a whole minor group
  assert pairs[('1065', '15-1242')] == 'remainder' and pairs[('1065', '15-1243')] == 'remainder'
  assert ('1065', '15-1241') not in pairs               # claimed exactly by 1050
  assert pairs[('1240', '15-1253')] == 'remainder' and pairs[('1240', '15-1299')] == 'remainder'
  assert ('1240', '15-1242') not in pairs               # the longer 15-124X pattern claims first
  assert frame.filter(pl.col('census_occ_2018').eq('9830')).height == 0
  detailed = soc_for_census.filter(pl.col('level').eq('detailed'))['code'].to_list()
  assert sorted(frame['soc_2018'].to_list()) == sorted(detailed)   # every detailed code exactly once
  assert frame.filter(pl.col('soc_2018').eq('15-1252'))['soc_title_2018'].item() == 'Software Developers'


def test_expand_census_occ_rejects_double_claims(census_occ_raw, soc_for_census):
  raw = census_occ_raw.with_columns(pl.col('column_3').str.replace('^15-1244$', '15-1240'))  # broad overlaps 1050's exact
  census = build.parse_census_occ(raw, vintage=2018, soc_2018=soc_for_census)
  with pytest.raises(ValueError, match='claimed'):
    build.expand_census_occ(vintage=2018, census_occ_2018=census, soc_2018=soc_for_census)


def test_validate_census_expansion_reports_unclaimed_detailed_codes(census_occ_raw, soc_for_census):
  census = build.parse_census_occ(census_occ_raw, vintage=2018, soc_2018=soc_for_census)
  frame = build.expand_census_occ(vintage=2018, census_occ_2018=census, soc_2018=soc_for_census)
  assert build.validate_census_expansion(frame, vintage=2018, soc_2018=soc_for_census) == []
  extra = pl.concat([soc_for_census, pl.DataFrame([('15-1254', 'detailed', 'Web Developers', '15-1250')], schema=soc_for_census.schema, orient='row')])
  problems = build.validate_census_expansion(frame, vintage=2018, soc_2018=extra)
  assert len(problems) == 1 and '15-1254' in problems[0]


# --------------------------------------------------------------------------------------------
# Census industry codes (the ACS/CPS household-survey aggregation of NAICS)
# --------------------------------------------------------------------------------------------

NAICS_FOR_IND = [
  ('21', 'Mining, Quarrying, and Oil and Gas Extraction'),
  ('211', 'Oil and Gas Extraction'),
  ('211120', 'Crude Petroleum Extraction'),
  ('211130', 'Natural Gas Extraction'),
  ('212114', 'Surface Coal Mining'),
  ('213111', 'Drilling Oil and Gas Wells'),
  ('23', 'Construction'),
  ('236220', 'Commercial and Institutional Building Construction'),
  ('31-33', 'Manufacturing'),
  ('3118', 'Bakeries and Tortilla Manufacturing'),
  ('311811', 'Retail Bakeries'),
  ('311812', 'Commercial Bakeries'),
  ('311830', 'Tortilla Manufacturing'),
  ('333111', 'Farm Machinery and Equipment Manufacturing'),
  ('333248', 'All Other Industrial Machinery Manufacturing'),
  ('333415', 'Air-Conditioning and Warm Air Heating Equipment Manufacturing'),
  ('333912', 'Air and Gas Compressor Manufacturing'),
  ('92', 'Public Administration'),
  ('921110', 'Executive Offices'),
  ('921150', 'American Indian and Alaska Native Tribal Governments'),
  ('922110', 'Courts'),
  ('92811', 'National Security'),
  ('928110', 'National Security'),
  ('928120', 'International Affairs'),
]


def naics_frame(rows: list[tuple[str, str]]) -> pl.DataFrame:
  return pl.DataFrame(
    [(code, 2 if '-' in code else len(code), title) for code, title in rows],
    schema=['code', 'level', 'title'],
    orient='row',
  )


@pytest.fixture
def naics_for_ind() -> pl.DataFrame:
  return naics_frame(NAICS_FOR_IND)


# (column 0, column 1, Census code, NAICS cell) — the code-list sheet's layout: sector headings
# carry a code range and their title in column 0; 0770 is listed twice, its first row a heading.
IND_ROWS = [
  ('Agriculture, Forestry, Fishing and Hunting, and Mining', None, '0170-0490', '11-21'),
  (None, 'Mining, Quarrying, and Oil and Gas Extraction', '0370-0490', '21'),
  (None, 'Oil and gas extraction ', '0370', '211'),
  (None, 'Coal mining ', '0380', '2121'),
  (None, 'Not specified type of mining', '0480', 'Part of 21'),
  (None, 'Support activities for mining ', '0490', '213'),
  ('Construction', None, '0770', '23'),
  (None, 'Construction (the cleaning of buildings and dwellings is incidental during construction '
         'and immediately after construction)', '0770', '23'),
  ('Manufacturing', None, '1070-3990', '31-33'),
  (None, 'Retail bakeries ', '1190', '311811'),
  (None, 'Bakeries and tortilla manufacturing, except retail bakeries ', '1270', '3118 exc. 311811'),
  (None, 'Agricultural implement manufacturing ', '3070', '33311'),
  (None, 'Machinery manufacturing, n.e.c. or not specified', '3291', '3332, 3334, 3339, Part of 333'),
  ('Public Administration', None, '9370-9590', '92'),
  (None, 'Executive offices and legislative bodies ', '9370', '92111, pt. 92115'),
  (None, 'Justice, public order, and safety activities ', '9470', '922, pt. 92115'),
  (None, 'National security and international affairs', '9590', '92812, pt. 92811'),
  ('Military', None, '9670-9870', 'pt. 92811'),
  (None, 'U. S. Army', '9670', 'pt. 92811'),
  (None, 'U. S. Air Force', '9680', 'pt. 92811'),
  (None, 'Unemployed, last worked 5 years ago or earlier or never worked', '9920', None),
]

# The 2017 list's claims on 928110, as published: 9590's prefix and the military codes' exact code.
IND_2017_MILITARY = {'9590': '928', '9670': '928110', '9680': '928110'}


def census_ind_raw(
  vintage: int = 2022, cells: dict[str, str] | None = None, body: list[tuple] | None = None,
) -> pl.DataFrame:
  '''The code-list sheet with the vintage's own header wording; cells replaces the NAICS cell of
  the named Census codes, and body replaces IND_ROWS.'''
  cells = cells or {}
  code_header = '2022 Census Industry Code' if vintage == 2022 else f'{vintage} Census Code'
  rows = [
    [f'{vintage} Census Industry Code List'],
    ['U.S. Census Bureau'],
    [None, f'Industry {vintage} Description', None, code_header, f'{vintage} NAICS Code'],
    [None, f'The {vintage} census industry code list has 266 codes including 7 military codes. '],
  ]
  rows.extend([col0, col1, None, code, cells.get(code, cell)] for col0, col1, code, cell in body or IND_ROWS)
  return raw_sheet(rows)


def expand_ind(naics: pl.DataFrame, vintage: int = 2022, cells: dict[str, str] | None = None) -> pl.DataFrame:
  census = build.parse_census_ind(census_ind_raw(vintage, cells), vintage=vintage, **{f'naics_{vintage}': naics})
  return build.expand_census_ind(vintage=vintage, **{f'census_ind_{vintage}': census, f'naics_{vintage}': naics})


def ind_pairs(frame: pl.DataFrame, vintage: int = 2022) -> dict[tuple[str, str], str]:
  return {
    (census, naics): via
    for census, naics, via in frame.select(f'census_ind_{vintage}', f'naics_{vintage}', 'via').iter_rows()
  }


def inc(*prefixes: str) -> list[tuple[str, str]]:
  return [(prefix, 'include') for prefix in prefixes]


def part(*prefixes: str) -> list[tuple[str, str]]:
  return [(prefix, 'partial') for prefix in prefixes]


def exc(*prefixes: str) -> list[tuple[str, str]]:
  return [(prefix, 'exclude') for prefix in prefixes]


@pytest.mark.parametrize(
  ('cell', 'expected'),
  [
    # one real cell for each shape the 2017 and 2022 lists use (digits written as 9)
    ('111', inc('111')),                                                    # 999
    ('1131, 1132', inc('1131', '1132')),                                    # 9999, 9999
    ('1133', inc('1133')),                                                  # 9999
    ('Part of 21', part('21')),                                             # Part of 99
    ('23', inc('23')),                                                      # 99
    ('311811', inc('311811')),                                              # 999999
    ('3118 exc. 311811', inc('3118') + exc('311811')),                      # 9999 exc. 999999
    ('Part of 311', part('311')),                                           # Part of 999
    ('3132 exc. 31324', inc('3132') + exc('31324')),                        # 9999 exc. 99999
    ('31411', inc('31411')),                                                # 99999
    ('314 exc. 31411', inc('314') + exc('31411')),                          # 999 exc. 99999
    ('31324, 3151', inc('31324', '3151')),                                  # 99999, 9999
    ('32222,32223, 32229', inc('32222', '32223', '32229')),                 # no space after a comma
    ('32412, 32419', inc('32412', '32419')),                                # 99999, 99999
    ('332992, 332993, 332994', inc('332992', '332993', '332994')),          # 999999 x 3
    ('3325, 3326, 3329 exc. 332992, 332993, 332994',
     inc('3325', '3326', '3329') + exc('332992', '332993', '332994')),      # list exc. list
    ('Part of 331 and 332', part('331', '332')),                            # Part of 999 and 999
    ('3332, 3334, 3339, Part of 333', inc('3332', '3334', '3339') + part('333')),
    ('3351, 3353, 3359', inc('3351', '3353', '3359')),                      # 9999 x 3
    ('321991, 321992', inc('321991', '321992')),                            # 999999, 999999
    ('3219 exc. 321991, 321992', inc('3219') + exc('321991', '321992')),    # 9999 exc. 999999, 999999
    ('3399 exc. 33992, 33993', inc('3399') + exc('33992', '33993')),        # 9999 exc. 99999, 99999
    ('Part of 31, 32, 33', part('31', '32', '33')),                         # Part of 99, 99, 99
    ('Part of 44, 45', part('44', '45')),                                   # Part of 99, 99
    ('4851, 4852, 4854, 4855, 4859 ', inc('4851', '4852', '4854', '4855', '4859')),  # trailing space
    ('Pts. 2211, 2212', part('2211', '2212')),                              # Pts. 9999, 9999
    ('Part of 22 ', part('22')),                                            # Part of 99 + trailing space
    ('5111 exc. 51111 ', inc('5111') + exc('51111')),                       # exc. + trailing space
    ('517 exc. 517311', inc('517') + exc('517311')),                        # 999 exc. 999999
    ('521, 52211,52219', inc('521', '52211', '52219')),                     # 999, 99999,99999
    ('523, 525', inc('523', '525')),                                        # 999, 999
    ('53221, 532281, 532282, 532283, 532284, 532289, 5323',
     inc('53221', '532281', '532282', '532283', '532284', '532289', '5323')),
    ('5324, 533', inc('5324', '533')),                                      # 9999, 999
    ('722 exc. 7224', inc('722') + exc('7224')),                            # 999 exc. 9999
    ('812113, 81219', inc('812113', '81219')),                              # 999999, 99999
    ('92111, 92112, 92114, pt. 92115', inc('92111', '92112', '92114') + part('92115')),
    ('922, pt. 92115', inc('922') + part('92115')),                         # 999, pt. 99999
    ('521, 52211', inc('521', '52211')),                                    # 999, 99999
    ('92812, pt. 92811', inc('92812') + part('92811')),                     # 99999, pt. 99999
    ('pt. 92811', part('92811')),                                           # pt. 99999
    (None, []),                                                             # 9920: no mapping
    ('  ', []),
  ],
)
def test_parse_naics_cell_kinds(cell, expected):
  assert build.parse_naics_cell(cell) == expected


@pytest.mark.parametrize(
  'cell',
  ['3118 except 311811', 'pt 92811', '311-312', '3118 exc. 311811 exc. 311812', '3118,', 'See 3118',
   '3118 exc. pt. 311811', 'exc. 311811', '3118 exc. 311811 and 311812'],
)
def test_parse_naics_cell_rejects_unknown_shapes(cell):
  with pytest.raises(ValueError, match=re.escape(repr(cell))):
    build.parse_naics_cell(cell)


@pytest.mark.parametrize(('cell', 'expected'), [
  ('Pt. 92811', part('92811')),
  ('part of 21', part('21')),
])
def test_parse_naics_cell_partial_marker_spellings(cell, expected):
  assert build.parse_naics_cell(cell) == expected


def test_parse_census_ind_list_as_published(naics_for_ind):
  frame = build.parse_census_ind(census_ind_raw(), vintage=2022, naics_2022=naics_for_ind)
  assert frame.columns == ['census_ind', 'title', 'naics_cell']
  assert frame['census_ind'].to_list() == [
    '0370', '0380', '0480', '0490', '0770', '1190', '1270', '3070', '3291', '9370', '9470', '9590',
    '9670', '9680', '9920',
  ]
  rows = {row['census_ind']: row for row in frame.iter_rows(named=True)}
  assert rows['0370'] == {'census_ind': '0370', 'title': 'Oil and gas extraction', 'naics_cell': '211'}
  assert rows['1270']['naics_cell'] == '3118 exc. 311811'
  assert rows['3291']['naics_cell'] == '3332, 3334, 3339, Part of 333'
  assert rows['9920'] == {
    'census_ind': '9920', 'title': 'Unemployed, last worked 5 years ago or earlier or never worked', 'naics_cell': None,
  }


def test_parse_census_ind_keeps_one_row_per_repeated_code(naics_for_ind):
  frame = build.parse_census_ind(census_ind_raw(), vintage=2022, naics_2022=naics_for_ind)
  rows = frame.filter(pl.col('census_ind').eq('0770'))
  assert rows.rows() == [('0770', 'Construction', '23')]   # the first row's title, from column 0


def test_parse_census_ind_rejects_repeated_code_with_different_cells(naics_for_ind):
  raw = census_ind_raw().with_columns(
    pl.when(pl.col('column_1').str.starts_with('Construction (')).then(pl.lit('236')).otherwise(pl.col('column_4')).alias('column_4')
  )
  with pytest.raises(ValueError, match='0770'):
    build.parse_census_ind(raw, vintage=2022, naics_2022=naics_for_ind)


@pytest.mark.parametrize('second_cell', ['236', None])
def test_parse_census_ind_rejects_repeated_code_with_and_without_a_cell(naics_for_ind, second_cell):
  raw = census_ind_raw().with_columns(
    pl.when(pl.col('column_1').str.starts_with('Construction (')).then(pl.lit(second_cell, dtype=pl.Utf8))
    .otherwise(pl.col('column_4')).alias('column_4')
  )
  with pytest.raises(ValueError, match='0770'):
    build.parse_census_ind(raw, vintage=2022, naics_2022=naics_for_ind)


def test_parse_census_ind_sorts_codes(naics_for_ind):
  # The sheet lists utilities (05xx-06xx) after transportation; the file is in code order.
  body = [row for row in IND_ROWS if row[2] != '0480'] + [(None, 'Not specified type of mining', '0480', 'Part of 21')]
  frame = build.parse_census_ind(census_ind_raw(body=body), vintage=2022, naics_2022=naics_for_ind)
  assert frame['census_ind'].to_list()[:4] == ['0370', '0380', '0480', '0490']


def test_parse_census_ind_trims_cells(naics_for_ind):
  frame = build.parse_census_ind(census_ind_raw(cells={'0380': '2121 ', '0480': ' Part of 21 '}), vintage=2022, naics_2022=naics_for_ind)
  cells = dict(frame.select('census_ind', 'naics_cell').iter_rows())
  assert cells['0380'] == '2121' and cells['0480'] == 'Part of 21'


def test_parse_census_ind_reads_the_2017_header(naics_for_ind):
  frame = build.parse_census_ind(census_ind_raw(2017), vintage=2017, naics_2017=naics_for_ind)
  assert frame.height == 15 and frame['census_ind'][0] == '0370'


def test_parse_census_ind_zero_fills_codes(naics_for_ind, tmp_path):
  numeric = {'0370': '370.0', '0380': '380', '0770': '770.0'}  # Excel numerics lose the zero
  raw = census_ind_raw().with_columns(pl.col('column_3').replace(numeric))
  frame = build.parse_census_ind(raw, vintage=2022, naics_2022=naics_for_ind)
  assert frame['census_ind'].to_list()[:5] == ['0370', '0380', '0480', '0490', '0770']
  assert frame['census_ind'].str.len_chars().eq(4).all()
  frame.write_csv(tmp_path / 'census_ind_2022.csv')
  assert '\n0370,' in (tmp_path / 'census_ind_2022.csv').read_text()   # a grep for 0370 finds it


@pytest.mark.parametrize('cell', ['3118 except 311811', 'Part of 311 (pt.)', '311-312', 'See 3118'])
def test_parse_census_ind_rejects_unknown_cell_shapes(naics_for_ind, cell):
  with pytest.raises(ValueError, match=re.escape(repr(cell))) as error:
    build.parse_census_ind(census_ind_raw(cells={'1270': cell}), vintage=2022, naics_2022=naics_for_ind)
  assert '1270' in str(error.value)


@pytest.mark.parametrize(('code', 'cell', 'prefix'), [
  ('0380', '2129', '2129'),                       # an include prefix
  ('1270', '3118 exc. 311819', '311819'),         # an exclusion
  ('0480', 'Part of 24', '24'),                   # a partial prefix
])
def test_parse_census_ind_rejects_prefix_missing_from_naics(naics_for_ind, code, cell, prefix):
  with pytest.raises(ValueError, match=prefix) as error:
    build.parse_census_ind(census_ind_raw(cells={code: cell}), vintage=2022, naics_2022=naics_for_ind)
  assert 'census_ind_2022' in str(error.value) and 'naics_2022' in str(error.value)


def test_expand_census_ind_partitions_exact_and_prefix_claims(naics_for_ind):
  frame = expand_ind(naics_for_ind)
  assert frame.columns == ['census_ind_2022', 'census_title_2022', 'naics_2022', 'naics_title_2022', 'via']
  pairs = ind_pairs(frame)
  assert pairs[('1190', '311811')] == 'exact'      # a six-digit item
  assert pairs[('0370', '211120')] == 'prefix' and pairs[('0370', '211130')] == 'prefix'
  assert pairs[('0380', '212114')] == 'prefix'
  assert pairs[('0770', '236220')] == 'prefix'     # a whole sector
  assert pairs[('9370', '921110')] == 'prefix'     # a five-digit item is a prefix, not exact
  assert pairs[('9590', '928120')] == 'prefix'
  assert frame['naics_2022'].str.contains(r'^\d{6}$').all()   # 3118, 92811 and the sectors never appear
  non_partial = frame.filter(pl.col('via').ne('partial'))
  assert not non_partial['naics_2022'].is_duplicated().any()  # each code has at most one such claim
  row = frame.filter(pl.col('census_ind_2022').eq('1190')).row(0, named=True)
  assert row == {
    'census_ind_2022': '1190', 'census_title_2022': 'Retail bakeries', 'naics_2022': '311811',
    'naics_title_2022': 'Retail Bakeries', 'via': 'exact',
  }
  assert frame.rows() == frame.sort('census_ind_2022', 'naics_2022').rows()


def test_expand_census_ind_applies_exclusions(naics_for_ind):
  pairs = ind_pairs(expand_ind(naics_for_ind))
  assert pairs[('1270', '311812')] == 'prefix' and pairs[('1270', '311830')] == 'prefix'
  assert ('1270', '311811') not in pairs           # carved out by 'exc. 311811'
  assert pairs[('1190', '311811')] == 'exact'      # another code's exclusion leaves its claim alone


def test_expand_census_ind_applies_every_exclusion_in_a_cell(naics_for_ind):
  pairs = ind_pairs(expand_ind(naics_for_ind, cells={'1270': '3118 exc. 311811, 311830', '0370': '211 exc. 21113'}))
  assert {naics for census, naics in pairs if census == '1270'} == {'311812'}   # both carve-outs apply
  assert {naics for census, naics in pairs if census == '0370'} == {'211120'}   # a five-digit carve-out


def test_expand_census_ind_exclusions_apply_to_partial_items(naics_for_ind):
  pairs = ind_pairs(expand_ind(naics_for_ind, cells={'0480': 'Part of 21 exc. 2121'}))
  assert {naics for census, naics in pairs if census == '0480'} == {'211120', '211130', '213111'}


def test_expand_census_ind_allows_shared_partial_claims(naics_for_ind):
  frame = expand_ind(naics_for_ind)
  pairs = ind_pairs(frame)
  assert pairs[('9370', '921150')] == 'partial' and pairs[('9470', '921150')] == 'partial'
  assert {census for census, naics in pairs if naics == '928110'} == {'9590', '9670', '9680'}
  assert all(pairs[(census, '928110')] == 'partial' for census in ('9590', '9670', '9680'))
  # a catch-all: 0480 'Part of 21' gets a partial row beside each specific claim in sector 21
  assert {naics: via for (census, naics), via in pairs.items() if census == '0480'} == {
    '211120': 'partial', '211130': 'partial', '212114': 'partial', '213111': 'partial',
  }
  assert pairs[('0370', '211120')] == 'prefix'
  assert build.validate_census_ind_expansion(frame, vintage=2022, naics_2022=naics_for_ind) == []


def test_expand_census_ind_prefix_wins_over_own_partial_item(naics_for_ind):
  frame = expand_ind(naics_for_ind)
  rows = frame.filter(pl.col('census_ind_2022').eq('3291'))
  assert dict(rows.select('naics_2022', 'via').iter_rows()) == {
    '333111': 'partial',                                          # only 'Part of 333' reaches it
    '333248': 'prefix', '333415': 'prefix', '333912': 'prefix',   # 3332, 3334, 3339 beat 'Part of 333'
  }
  assert rows.height == 4
  assert not frame.select('census_ind_2022', 'naics_2022').is_duplicated().any()


def test_expand_census_ind_rejects_non_partial_double_claims(naics_for_ind):
  cells = {'9370': '92111, 92115', '9470': '922, 92115'}
  with pytest.raises(ValueError, match='921150') as error:
    expand_ind(naics_for_ind, cells=cells)
  assert '9370' in str(error.value) and '9470' in str(error.value)


def test_expand_census_ind_skips_unmapped_codes(naics_for_ind):
  census = build.parse_census_ind(census_ind_raw(), vintage=2022, naics_2022=naics_for_ind)
  assert census.filter(pl.col('census_ind').eq('9920')).height == 1   # kept in the list
  frame = build.expand_census_ind(vintage=2022, census_ind_2022=census, naics_2022=naics_for_ind)
  assert frame.filter(pl.col('census_ind_2022').eq('9920')).height == 0
  assert set(frame['census_ind_2022']) == set(census['census_ind']) - {'9920'}


def test_validate_census_ind_expansion_reports_unclaimed_codes(naics_for_ind):
  frame = expand_ind(naics_for_ind)
  assert build.validate_census_ind_expansion(frame, vintage=2022, naics_2022=naics_for_ind) == []
  extra = naics_frame(NAICS_FOR_IND + [('22', 'Utilities'), ('221122', 'Electric Power Distribution')])
  problems = build.validate_census_ind_expansion(frame, vintage=2022, naics_2022=extra)
  assert len(problems) == 1 and '221122' in problems[0]


def test_validate_census_ind_expansion_reports_non_partial_double_claims(naics_for_ind):
  frame = expand_ind(naics_for_ind)
  doubled = pl.concat([
    frame,
    frame.filter(pl.col('census_ind_2022').eq('0370').and_(pl.col('naics_2022').eq('211120')))
    .with_columns(census_ind_2022=pl.lit('0480')),
  ])
  problems = build.validate_census_ind_expansion(doubled, vintage=2022, naics_2022=naics_for_ind)
  assert len(problems) == 1
  assert '211120' in problems[0] and '0370' in problems[0] and '0480' in problems[0]


def test_census_ind_2017_override_lets_928110_claims_share(naics_for_ind):
  frame = expand_ind(naics_for_ind, vintage=2017, cells=IND_2017_MILITARY)
  pairs = ind_pairs(frame, vintage=2017)
  assert pairs[('9590', '928110')] == 'partial'
  assert pairs[('9670', '928110')] == 'partial' and pairs[('9680', '928110')] == 'partial'
  assert pairs[('9590', '928120')] == 'prefix'     # 9590's other 928 claim is untouched
  assert build.validate_census_ind_expansion(frame, vintage=2017, naics_2017=naics_for_ind) == []
  assert set(build.CENSUS_IND_PARTIAL_OVERRIDES[(2017, '928110')]) == {
    '9590', '9670', '9680', '9690', '9770', '9780', '9790', '9870',
  }


def test_census_ind_2017_needs_the_override(naics_for_ind, monkeypatch):
  monkeypatch.setattr(build, 'CENSUS_IND_PARTIAL_OVERRIDES', {})
  with pytest.raises(ValueError, match='928110'):
    expand_ind(naics_for_ind, vintage=2017, cells=IND_2017_MILITARY)


@pytest.mark.parametrize(('vintage', 'cells', 'code'), [
  (2022, IND_2017_MILITARY, '928110'),                                                   # another vintage
  (2017, IND_2017_MILITARY | {'9370': '92111, 92115', '9470': '922, 92115'}, '921150'),  # another code
  (2017, IND_2017_MILITARY | {'9370': '92111, 928110', '9470': '922, 928110'}, '928110'),  # unlisted claimants
])
def test_census_ind_override_applies_only_to_its_key(naics_for_ind, vintage, cells, code):
  with pytest.raises(ValueError, match=code):
    expand_ind(naics_for_ind, vintage=vintage, cells=cells)


def census_ind_frame(height: int) -> pl.DataFrame:
  return pl.DataFrame({'census_ind': [f'{index:04d}' for index in range(height)]})


@pytest.mark.parametrize(('height', 'flagged'), [(229, True), (230, False), (320, False), (321, True)])
def test_validate_census_ind_row_band(height, flagged):
  problems = build.validate_census_ind(census_ind_frame(height), 2022)
  if flagged:
    assert len(problems) == 1 and 'outside the plausible 230-320 band' in problems[0]
  else:
    assert problems == []


def test_validate_census_ind_flags_duplicates():
  duplicated = census_ind_frame(230).with_columns(
    pl.when(pl.col('census_ind').eq('0001')).then(pl.lit('0000')).otherwise(pl.col('census_ind')).alias('census_ind')
  )
  problems = build.validate_census_ind(duplicated, 2022)
  assert len(problems) == 1 and '2 duplicated Census codes' in problems[0]


def test_census_ind_builds_read_their_lists_and_expand_against_naics():
  builds = {b.name: b for b in build.BUILDS}
  for vintage, sheet in [(2017, '2017 Census Industry Code List'), (2022, '2022 Census Ind Code List ')]:
    listed = builds[f'census_ind_{vintage}']
    assert listed.sheet == sheet and listed.requires == (f'naics_{vintage}',)
    assert listed.url.startswith('https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/')
    expansion = builds[f'census_ind_{vintage}_to_naics_{vintage}']
    assert expansion.url is None and expansion.requires == (f'census_ind_{vintage}', f'naics_{vintage}')
    assert (f'census_ind_{vintage}_to_naics_{vintage}', f'naics_{vintage}', f'naics_{vintage}', 6) in build.REFERENTIAL_PAIRS


def test_resolve_requires_prefers_this_runs_frames_then_disk(tmp_path, soc_for_census):
  soc_for_census.write_csv(tmp_path / 'soc_2018.csv')
  in_memory = {'soc_2018': soc_for_census.head(3)}
  assert build.resolve_requires(('soc_2018',), in_memory, tmp_path)['soc_2018'].height == 3
  from_disk = build.resolve_requires(('soc_2018',), {}, tmp_path)['soc_2018']
  assert from_disk.height == soc_for_census.height
  assert from_disk.filter(pl.col('code').eq('11-0000'))['parent_code'].item() is None
  with pytest.raises(FileNotFoundError, match='soc_2010'):
    build.resolve_requires(('soc_2010',), {}, tmp_path)


def test_every_referential_pair_names_registered_builds():
  names = {b.name for b in build.BUILDS}
  for concordance, _column, structure, _leaf in build.REFERENTIAL_PAIRS:
    assert concordance in names and structure in names


def test_source_filename_unquotes_url_path():
  assert build.source_filename('https://www.census.gov/naics/2022NAICS/2-6%20digit_2022_Codes.xlsx') == '2-6 digit_2022_Codes.xlsx'
  assert build.source_filename('https://www.bls.gov/soc/soc_structure_2010.xls') == 'soc_structure_2010.xls'


# --------------------------------------------------------------------------------------------
# Fetching: bls.gov admits scripts only with a contact email in a crawler-style User-Agent
# --------------------------------------------------------------------------------------------


def test_user_agent_names_the_build_and_carries_the_contact():
  ua = build.user_agent('someone@example.org')
  assert ua.startswith('classification-codes-build/')
  assert 'contact: someone@example.org' in ua
  assert 'github.com' not in ua  # bls.gov rejects any User-Agent carrying that token
  assert 'contact' not in build.user_agent(None)


def test_needs_contact_email_only_for_bls_hosts():
  assert build.needs_contact_email('https://www.bls.gov/soc/2018/soc_structure_2018.xlsx')
  assert build.needs_contact_email('https://download.bls.gov/pub/time.series/oe/oe.occupation')
  assert not build.needs_contact_email('https://www.census.gov/naics/2022NAICS/2022_NAICS_Structure.xlsx')


def test_fetch_refuses_bls_download_without_contact_email(tmp_path, monkeypatch):
  monkeypatch.delenv('BLS_CONTACT_EMAIL', raising=False)
  with pytest.raises(RuntimeError, match='BLS_CONTACT_EMAIL'):
    build.fetch('https://www.bls.gov/soc/2018/soc_structure_2018.xlsx', tmp_path, offline=False, refresh=False)
  assert not list(tmp_path.iterdir())  # nothing was written and no request was attempted


def test_fetch_uses_cached_bls_copy_without_contact_email(tmp_path, monkeypatch):
  monkeypatch.delenv('BLS_CONTACT_EMAIL', raising=False)
  cached = tmp_path / 'soc_structure_2018.xlsx'
  cached.write_bytes(b'not really a workbook')
  path, sha256, _retrieved = build.fetch('https://www.bls.gov/soc/2018/soc_structure_2018.xlsx', tmp_path, offline=False, refresh=False)
  assert path == cached and len(sha256) == 64


# --------------------------------------------------------------------------------------------
# Validator bands
# --------------------------------------------------------------------------------------------


def rows_frame(height: int) -> pl.DataFrame:
  return pl.DataFrame({'code': [str(index) for index in range(height)]})


@pytest.mark.parametrize(('height', 'flagged'), [(799, True), (800, False), (2000, False), (2001, True)])
def test_validate_naics_concordance_row_band(height, flagged):
  problems = build.validate_naics_concordance(rows_frame(height), 2017, 2022)
  if flagged:
    assert len(problems) == 1 and 'outside the plausible 800-2000 band' in problems[0]
  else:
    assert problems == []


@pytest.mark.parametrize(('height', 'flagged'), [(699, True), (700, False), (1600, False), (1601, True)])
def test_validate_soc_crosswalk_row_band(height, flagged):
  problems = build.validate_soc_crosswalk(rows_frame(height), 2010, 2018)
  if flagged:
    assert len(problems) == 1 and 'outside the plausible 700-1600 band' in problems[0]
  else:
    assert problems == []


def census_occ_frame(height: int, soc_level: str = 'detailed') -> pl.DataFrame:
  return pl.DataFrame({
    'census_occ': [f'{index:04d}' for index in range(height)],
    'soc_level': [soc_level] * height,
  })


def test_validate_census_occ_flags_band_duplicates_and_levels():
  assert build.validate_census_occ(census_occ_frame(450), 2018) == []
  band = build.validate_census_occ(census_occ_frame(449), 2018)
  assert len(band) == 1 and 'outside the plausible 450-700 band' in band[0]

  duplicated = census_occ_frame(450).with_columns(
    pl.when(pl.col('census_occ') == '0001').then(pl.lit('0000')).otherwise(pl.col('census_occ')).alias('census_occ')
  )
  problems = build.validate_census_occ(duplicated, 2018)
  assert len(problems) == 1 and '2 duplicated Census codes' in problems[0]

  odd_level = census_occ_frame(450).with_columns(
    pl.when(pl.col('census_occ') == '0000').then(pl.lit('group')).otherwise(pl.col('soc_level')).alias('soc_level')
  )
  problems = build.validate_census_occ(odd_level, 2018)
  assert len(problems) == 1 and 'outside' in problems[0]


# --------------------------------------------------------------------------------------------
# Offline fetch
# --------------------------------------------------------------------------------------------

SKILL_DIR = Path(__file__).resolve().parent.parent
TEST_URL = 'https://www.census.gov/naics/2022NAICS/2022_NAICS_Structure.xlsx'


def test_fetch_offline_without_cache_raises(tmp_path):
  with pytest.raises(FileNotFoundError, match='--offline set but'):
    build.fetch(TEST_URL, tmp_path, offline=True, refresh=False)


def test_fetch_offline_uses_cache_without_network(tmp_path, monkeypatch):
  payload = b'cached workbook bytes'
  cached = tmp_path / build.source_filename(TEST_URL)
  cached.write_bytes(payload)

  def refuse(*args, **kwargs):
    raise AssertionError('offline fetch must not touch the network')

  monkeypatch.setattr(urllib.request, 'urlopen', refuse)
  path, sha256, _retrieved = build.fetch(TEST_URL, tmp_path, offline=True, refresh=False)
  assert path == cached
  assert sha256 == hashlib.sha256(payload).hexdigest()


# --------------------------------------------------------------------------------------------
# Documented counts match the committed data
# --------------------------------------------------------------------------------------------


def table_counts(skill_md: str) -> dict[str, int]:
  '''The first number in the `rows` cell of each `data/*.csv` row of the `## Files` table.'''
  counts = {}
  for line in skill_md.split('## Files', 1)[1].splitlines():
    cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
    match = re.fullmatch(r'`(data/[^`]+\.csv)`', cells[0]) if cells else None
    if match is None or len(cells) < 2:
      continue
    counts[match.group(1)] = int(re.match(r'[\d,]+', cells[1]).group().replace(',', ''))
  return counts


def csv_height(relative: str) -> int:
  return pl.read_csv(SKILL_DIR / relative, infer_schema=False).height


def test_skill_table_counts_match_data():
  skill_md = (SKILL_DIR / 'SKILL.md').read_text()
  counts = table_counts(skill_md)
  assert counts, 'no data/*.csv rows found in the SKILL.md Files table'
  for relative, documented in counts.items():
    actual = csv_height(relative)
    assert documented == actual, f'SKILL.md {relative}: documents {documented} rows, file has {actual}'
  for relative, label, level in [
    ('data/naics_2022.csv', 'six-digit', '6'),
    ('data/naics_2017.csv', 'six-digit', '6'),
    ('data/naics_2012.csv', 'six-digit', '6'),
    ('data/soc_2018.csv', 'detailed', 'detailed'),
    ('data/soc_2010.csv', 'detailed', 'detailed'),
  ]:
    row = next(line for line in skill_md.splitlines() if f'`{relative}`' in line)
    documented = int(re.search(rf'\(([\d,]+) {label}\)', row).group(1).replace(',', ''))
    actual = pl.read_csv(SKILL_DIR / relative, infer_schema=False).filter(pl.col('level') == level).height
    assert documented == actual, f'SKILL.md {relative}: documents {documented} {label}, file has {actual}'


def test_manifest_rows_match_data():
  checked = 0
  for line in (SKILL_DIR / 'MANIFEST.md').read_text().splitlines():
    cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
    if len(cells) > 1 and re.fullmatch(r'data/[^ ]+\.csv', cells[0]):
      actual = csv_height(cells[0])
      assert int(cells[1]) == actual, f'MANIFEST.md {cells[0]}: lists {cells[1]} rows, file has {actual}'
      checked += 1
  assert checked

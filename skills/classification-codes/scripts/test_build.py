'''Tests for build.py — the parsers and validators, driven by synthetic raw sheets that mimic the
Census / BLS workbook layouts (preamble rows, legend rows, ranged sector codes, trailing-space
titles, trilateral markers, one-code-column-per-row SOC sheets).

Run from this directory:
  uv run --python 3.13 --with pytest --with polars --with fastexcel python -m pytest -q

The parsers take an already-read raw frame (every cell Utf8, no header), so no workbook is
needed here; end-to-end parsing of the real sources is exercised by test_real_sources.py when
sources/ is populated.
'''

from __future__ import annotations

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
          'soc_2018', 'soc_2010', 'soc_2010_to_2018'} <= set(names)


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

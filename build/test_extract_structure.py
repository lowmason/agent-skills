'''Tests for extract_structure's table-of-contents parser and its completeness guard.

Every fixture is invented text laid out like `pdftotext -layout` output of a contents
page. No book text belongs here: the books are CC-BY-NC-ND.
'''
import pytest

from extract_structure import check_complete, check_range_end, parse_toc

LAYOUT = '''Contents




Preface      xxvii

1 Alpha chapter       1
  1.1 First topic        1
       1.1.1   Deep idea     2
       1.1.2   Idea with one space 9
  1.2 Advanced topic *       11
2 Beta chapter level 2      20
  2.1 Topic 3      21
                                          xi
'''


def test_parse_toc_reads_number_title_and_drops_the_page():
    rows = parse_toc(LAYOUT)
    assert rows['1'] == 'Alpha chapter'
    assert rows['1.1'] == 'First topic'
    assert rows['1.1.1'] == 'Deep idea'


def test_parse_toc_takes_a_single_space_before_the_page():
    assert parse_toc(LAYOUT)['1.1.2'] == 'Idea with one space'


def test_parse_toc_drops_the_advanced_section_marker():
    assert parse_toc(LAYOUT)['1.2'] == 'Advanced topic'


def test_parse_toc_keeps_a_title_that_ends_in_a_digit():
    rows = parse_toc(LAYOUT)
    assert rows['2'] == 'Beta chapter level 2'
    assert rows['2.1'] == 'Topic 3'


def test_parse_toc_skips_unnumbered_and_roman_numeral_lines():
    assert set(parse_toc(LAYOUT)) == {'1', '1.1', '1.1.1', '1.1.2', '1.2', '2', '2.1'}


def test_parse_toc_keeps_the_first_title_for_a_repeated_number():
    assert parse_toc('3 First      40\n3 Second      41\n') == {'3': 'First'}


def test_check_complete_passes_a_contiguous_book():
    check_complete({'1': 'A', '1.1': 'a', '2': 'B', '2.1': 'b'})


def test_check_complete_names_a_missing_chapter():
    with pytest.raises(ValueError, match=r'\b2\b'):
        check_complete({'1': 'A', '3': 'C', '3.1': 'c'})


def test_check_complete_refuses_a_book_without_chapter_1():
    with pytest.raises(ValueError, match=r'\b1\b'):
        check_complete({'2': 'B', '2.1': 'b'})


def test_check_complete_refuses_a_section_whose_chapter_is_absent():
    with pytest.raises(ValueError, match=r'4\.1'):
        check_complete({'1': 'A', '4.1': 'd'})


def test_check_complete_refuses_an_untitled_entry():
    with pytest.raises(ValueError, match=r'1\.1'):
        check_complete({'1': 'A', '1.1': ''})


def test_check_complete_refuses_an_empty_parse():
    with pytest.raises(ValueError):
        check_complete({})


def test_check_range_end_passes_when_the_next_page_holds_no_entry():
    check_range_end({}, last=25)


def test_check_range_end_refuses_contents_that_run_past_the_range():
    # A range that stops early still passes check_complete: its chapters run from 1
    # without a gap. The page after the range is where the missing tail shows.
    with pytest.raises(ValueError, match=r'page 23.*\b20\b'):
        check_range_end({'20': 'Late chapter', '20.1': 'Late topic'}, last=22)

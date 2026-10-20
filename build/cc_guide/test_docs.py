'''Tests for docs.py: release ordering, the changelog, llms.txt and page
naming (drift spec R2.4, R6.5, R6.6).'''
from datetime import date, datetime

import pytest

import docs
from cc_fixtures import CHANGELOG_TEXT, LLMS_TEXT, isolated_home  # noqa: F401


def test_versions_order_as_integer_tuples_with_four_components():
    labels = ['2.1.289', '2.1.288.1', '2.1.10', '2.1.288', '2.1.9']
    assert sorted(labels, key=docs.version_key) == ['2.1.9', '2.1.10', '2.1.288', '2.1.288.1', '2.1.289']


@pytest.mark.parametrize('label', ['2.1.x', '', '2.1.288-beta', 'v2.1.288', '2.1.288\n', '\u0662.\u0661.\u0662'])
def test_version_key_rejects_what_is_not_a_label(label):
    with pytest.raises(ValueError):
        docs.version_key(label)


def test_changelog_blocks_come_newest_first_with_their_bullets():
    releases = docs.parse_changelog(CHANGELOG_TEXT)
    assert [(r.label, r.date) for r in releases] == [
        ('2.1.902', date(2026, 10, 1)), ('2.1.901', date(2026, 9, 20)), ('2.1.900', date(2026, 9, 1))]
    assert releases[0].bullets == ['Changed how `BETA_ENV` is read', 'Fixed a crash in the fixture tool']


def test_changelog_order_is_numeric_not_file_order():
    text = ('<Update label="2.1.9" description="July 1, 2026">\n  * a\n</Update>\n'
            '<Update label="2.1.10" description="July 2, 2026">\n  * b\n</Update>\n')
    assert [r.label for r in docs.parse_changelog(text)] == ['2.1.10', '2.1.9']


def test_a_bad_release_date_names_its_line():
    with pytest.raises(ValueError) as cause:
        datetime.strptime('2026-07-01', '%B %d, %Y')
    with pytest.raises(ValueError) as err:
        docs.parse_changelog('\n<Update label="2.1.9" description="2026-07-01">\n</Update>\n')
    assert str(err.value) == f'line 2: {cause.value}'


@pytest.mark.parametrize('text, message', [
    ('<Update label="2.1.x" description="July 1, 2026">\n</Update>\n', "line 1: not a release label: '2.1.x'"),
    ('<Update label="2.1.9" description="July 1, 2026">\n</Update>\n'
     '<Update label="2.1.9" description="July 2, 2026">\n</Update>\n', 'line 3: release label 2.1.9 repeats line 1'),
    ('<Update label="2.1.9" date="July 1, 2026">\n</Update>\n', 'line 1: unrecognized <Update> tag'),
    ('<Update label="2.1.9">\n</Update>\n', 'line 1: unrecognized <Update> tag'),
    ('\n  <Update label="2.1.9" description="July 1, 2026" >\n', 'line 2: unrecognized <Update> tag'),
])
def test_changelog_errors_name_their_line(text, message):
    with pytest.raises(ValueError) as err:
        docs.parse_changelog(text)
    assert str(err.value) == message


def test_a_bullet_after_a_closed_release_belongs_to_no_release():
    text = '<Update label="2.1.9" description="July 1, 2026">\n  * in\n</Update>\n  * out\n'
    assert docs.parse_changelog(text)[0].bullets == ['in']


def test_a_release_keeps_only_its_bullets():
    '''A non-bullet line inside a release is dropped. The real changelog's
    release blocks held only bullets on 2026-10-08 (6,970 lines, no other
    kind), so this is recorded as needing no action (plan 39).'''
    text = '<Update label="2.1.9" description="July 1, 2026">\n  * one\n  A stray line.\n\n  * two\n</Update>\n'
    assert docs.parse_changelog(text)[0].bullets == ['one', 'two']


def test_an_expandable_list_keeps_its_dash_bullets():
    '''From about 2026-10-13 the <Update> blocks folded long lists into
    <Expandable> blocks, some written with `- ` bullets.'''
    text = ('<Update label="2.1.9" description="July 1, 2026">\n  **Added**\n\n  * one\n\n'
            '  <Expandable title="2 improvements">\n    - two\n    - three\n  </Expandable>\n\n'
            '  <Expandable title="1 bug fix">\n    * four\n  </Expandable>\n</Update>\n')
    assert docs.parse_changelog(text)[0].bullets == ['one', 'two', 'three', 'four']


# The changelog page as served from about 14:00 on 2026-10-20: a bold label
# line per release, bold group headings, column-0 bullets and no date.
BOLD_TEXT = '\n'.join([
    '# Claude Code changelog',
    '',
    '* A bullet before every release.',
    '',
    '**2.1.9**',
    '',
    '**Added**',
    '',
    '* one',
    '',
    '**5 improvements**',
    '',
    '* two',
    '',
    '**2.1.10**',
    '',
    '* three',
    '',
    '**Fixed**',
    '',
    '* four',
    '',
])


def test_bold_labels_mark_releases_with_their_bullets_and_no_date():
    releases = docs.parse_changelog(BOLD_TEXT)
    assert [(r.label, r.date, r.bullets) for r in releases] == [
        ('2.1.10', None, ['three', 'four']), ('2.1.9', None, ['one', 'two'])]


@pytest.mark.parametrize('text, message', [
    ('**2.1.9**\n* a\n**2.1.x**\n', "line 3: not a release label: '2.1.x'"),
    ('**2.1.9**\n* a\n\n**2.1.9**\n', 'line 4: release label 2.1.9 repeats line 1'),
])
def test_bold_label_errors_name_their_line(text, message):
    with pytest.raises(ValueError) as err:
        docs.parse_changelog(text)
    assert str(err.value) == message


def test_both_formats_read_the_same_releases():
    '''The bold page is the <Update> page with each <Expandable> list
    flattened and the dates dropped: on 2026-10-20 the two copies held the
    same 424 labels with the same bullets in the same order.'''
    tagged = ('<Update label="2.1.10" description="July 2, 2026">\n  * three\n\n'
              '  <Expandable title="1 bug fix">\n    - four\n  </Expandable>\n</Update>\n\n'
              '<Update label="2.1.9" description="July 1, 2026">\n  **Added**\n\n  * one\n\n'
              '  <Expandable title="5 improvements">\n    - two\n  </Expandable>\n</Update>\n')
    assert ([(r.label, r.bullets) for r in docs.parse_changelog(tagged)]
            == [(r.label, r.bullets) for r in docs.parse_changelog(BOLD_TEXT)])


def test_llms_lists_code_page_slugs():
    assert docs.parse_llms(LLMS_TEXT) == {'tools', 'events', 'env-vars', 'plugins/components'}


def test_page_files_and_urls_follow_the_snapshot_and_the_refresh():
    sources = {'docs_base': 'https://code.claude.com/docs/en/',
               'platform_base': 'https://platform.claude.com/docs/en/'}
    assert docs.page_file('plugins/components') == 'plugins_components.md'
    assert docs.page_file('platform:about-claude/pricing') == 'platform_about-claude_pricing.md'
    assert docs.page_url('hooks', sources) == 'https://code.claude.com/docs/en/hooks.md'
    assert (docs.page_url('platform:models/haiku-4-5/overview', sources)
            == 'https://platform.claude.com/docs/en/models/haiku-4-5/overview.md')

'''Tests for blocks.py: fences, page splitting, keys, normalization, hashing
and selection (drift spec R3).'''
import hashlib

import blocks
from cc_fixtures import (ENV_PAGE, FENCE, FENCE4, PLATFORM_PAGE, TABLE_PAGE,  # noqa: F401
                         TILDE, isolated_home)

ENV = 'Environment variables'


def test_fences_cover_backtick_tilde_indented_and_nested_shapes():
    lines = ['a', FENCE + 'bash', '# x', FENCE, '  ' + FENCE, '  # y', '  ' + FENCE,
             TILDE, '## z', TILDE, FENCE4, FENCE, '# w', FENCE, FENCE4, 'b']
    assert blocks.fenced_lines(lines) == set(range(1, 15))


def test_a_fence_closes_only_on_its_own_character_at_its_length():
    lines = [FENCE4, FENCE, TILDE * 2, FENCE4 + ' x', 'still code', FENCE4 + '`', 'out']
    assert blocks.fenced_lines(lines) == {0, 1, 2, 3, 4, 5}


def test_fence_spans_carry_each_openers_info_string():
    lines = [FENCE + 'json', '{}', FENCE, TILDE + ' bash x', 'ls', TILDE, FENCE]
    assert blocks.fence_spans(lines) == [(0, 2, 'json'), (3, 5, 'bash x'), (6, None, '')]


def test_an_unclosed_fence_runs_to_the_end():
    assert blocks.fenced_lines(['a', TILDE, '## b', 'c']) == {1, 2, 3}


def test_a_backtick_in_a_backtick_openers_info_string_opens_no_fence():
    '''CommonMark: a backtick fence's info string holds no backtick, so such
    a line is inline code. A tilde fence's info string may hold one. No
    cached docs page or guide line had such an opener on 2026-10-08.'''
    assert blocks.fenced_lines([FENCE + 'x`y', '# heading', FENCE]) == {2}
    assert blocks.fenced_lines([TILDE + 'x`y', '# heading', TILDE]) == {0, 1, 2}


def test_the_documentation_index_preamble_is_dropped():
    lines = ENV_PAGE.split('\n')
    assert blocks.strip_preamble(lines) == lines[3:]
    quote = ['> A plain blockquote.', '', '# T']
    assert blocks.strip_preamble(quote) == quote


def test_page_blocks_in_page_order_with_rows_and_ordinals():
    assert list(blocks.page_blocks(ENV_PAGE)) == [
        ENV,
        f'{ENV} › `ALPHA_ENV`',
        f'{ENV} › `BETA_ENV`',
        f'{ENV} › `PIPE_ENV`',
        f'{ENV} › (row)',
        f'{ENV} › `ALPHA_ENV`#2',
        f'{ENV} › Examples',
        f'{ENV} › Examples#2',
    ]


def test_a_heading_block_keeps_its_table_header_and_trailing_text_only():
    assert blocks.page_blocks(ENV_PAGE)[ENV] == '\n'.join([
        '# Environment variables',
        '> Variables that steer the fixture tool.',
        'Set them in a [settings file]().',
        '| Variable | Purpose |',
        '| :--- | :--- |',
        'Text after the table stays in the heading block.',
    ])


def test_hash_lines_inside_any_fence_never_cut_a_block():
    examples = blocks.page_blocks(ENV_PAGE)[f'{ENV} › Examples']
    assert '# a shell comment, not a heading' in examples
    assert '# an indented fence, still code' in examples
    assert '## a tilde fence, not a heading' in examples
    assert '## nested, not a heading' in examples


def test_a_row_splits_on_unescaped_pipes_only():
    assert blocks.first_cell('| `a\\|b` | c |') == '`a\\|b`'
    assert blocks.page_blocks(ENV_PAGE)[f'{ENV} › `PIPE_ENV`'] == '| `PIPE_ENV` | Accepts `a\\|b`. |'


def test_a_table_under_a_lone_heading():
    assert blocks.page_blocks(TABLE_PAGE) == {
        'Settings': '## Settings\n| Key | Value |\n|---|---|',
        'Settings › `alpha.mode`': '| `alpha.mode` | fast |',
        'Settings › `beta.mode`': '| `beta.mode` | slow |',
    }


def test_platform_front_matter_stays_in_the_intro_block():
    assert blocks.page_blocks(PLATFORM_PAGE) == {
        '(intro)': ('---\ntitle: Fixture pricing\n'
                    'url: https://platform.example.invalid/docs/en/pricing\n'
                    '---\nPrices for `BETA_ENV` users.'),
        'Rates': '## Rates\nRates move with `BetaEvent`.',
    }


def test_heading_paths_join_ancestors_and_drop_closing_hashes():
    page = '# T\n## A ##\n### B\n## C\n### B\n'
    assert list(blocks.page_blocks(page)) == ['T', 'T › A', 'T › A › B', 'T › C', 'T › C › B']


def test_normalize_empties_link_targets_and_collapses_whitespace():
    text = '  See   [a](https://x.invalid/a)\n\n\tand [b](/docs/en/b).  \n'
    assert blocks.normalize(text) == 'See [a]()\nand [b]().'
    assert blocks.normalize('Call f[k](\nx,\n) here.') == 'Call f[k](\nx,\n) here.'


def test_block_hash_is_sixteen_hex_of_the_normalized_text():
    h = blocks.block_hash('Use [it](/a) now.')
    assert len(h) == 16 and int(h, 16) >= 0
    assert blocks.block_hash('Use  [it](/moved)\nnow.'.replace('\n', ' ')) == h
    assert blocks.block_hash('Use [it](/a) later.') != h


def test_block_hash_is_sha256_over_the_normalized_lines_joined_by_newlines():
    assert blocks.block_hash('a') == hashlib.sha256(b'a').hexdigest()[:16]
    assert blocks.block_hash(' a \n\n b ') == hashlib.sha256(b'a\nb').hexdigest()[:16]


def test_a_link_whose_title_wraps_to_the_next_line_keeps_its_target():
    '''LINK_RE stops at a newline (plan 38, ruling 2), so code such as
    f[k](\\nx,\\n) is never read as a link. A wrapped link title therefore
    keeps its target too. None of the 133 cached docs pages had one on
    2026-10-08, so this is recorded as needing no action (plan 39).'''
    assert blocks.normalize('[a](/x\n"Title")') == '[a](/x\n"Title")'


def test_key_parts_drop_link_targets_and_cap_at_sixty_characters():
    assert blocks.key_part('[Hooks](/docs/en/hooks)  page') == '[Hooks]() page'
    long = 'word ' * 20
    assert blocks.key_part(long) == long[:59] + '…'
    assert len(blocks.key_part(long)) == 60


def test_a_key_part_of_sixty_characters_is_kept_and_one_of_sixty_one_is_cut():
    assert blocks.key_part('x' * 60) == 'x' * 60
    assert blocks.key_part('x' * 61) == 'x' * 59 + '…'


def test_a_key_hash_is_sixteen_hex_of_sha256_over_the_key_and_names_map_back():
    '''R2.3 commits block keys only as these hashes.'''
    assert blocks.key_hash('a') == 'ca978112ca1bbdca'
    row, again = f'{ENV} › `ALPHA_ENV`', f'{ENV} › `ALPHA_ENV`#2'
    assert blocks.key_hash(row) != blocks.key_hash(again)
    assert blocks.key_names([row, again]) == {blocks.key_hash(row): row, blocks.key_hash(again): again}


def test_select_takes_every_block_of_an_all_page_and_term_hits_of_a_terms_page():
    page = blocks.page_blocks(ENV_PAGE)
    assert blocks.select(page, 'all', set()) == list(page)
    assert blocks.select(page, 'terms', {'BETA_ENV'}) == [f'{ENV} › `BETA_ENV`']
    assert blocks.select(page, 'terms', {'Examples'}) == [f'{ENV} › Examples', f'{ENV} › Examples#2']
    # ENV is in every key but only the heading block's text, so keys match too.
    assert blocks.select(page, 'terms', {ENV}) == list(page)
    # Matching is case-sensitive.
    assert blocks.select(page, 'terms', {'beta_env'}) == []


def test_candidates_are_matching_sections_or_the_whole_group():
    terms = {'b.overview': {'BETA_ENV'}, 'b.events': {'BetaEvent', 'BETA_ENV'}, 'b.other': {'zzz'}}
    assert blocks.candidates('k', 'uses BETA_ENV', terms) == ['b.overview', 'b.events']
    assert blocks.candidates('k', 'nothing here', terms) == ['b.overview', 'b.events', 'b.other']

'''Tests for guide.py's citations: R4.1's forms and placements, and how R5
reads citation-shaped lines (drift spec R4, R5). No line here begins with a
citation: test data sits inside quotes.'''
import pytest

import guide
from cc_fixtures import isolated_home  # noqa: F401

IDS = ('hooks.patterns', 'hooks.pitfalls')
HASH = '# cc-guide: hooks.patterns hooks.pitfalls @2.1.219'
HTML = '<!-- cc-guide: hooks.patterns hooks.pitfalls @2.1.219 -->'
FRONT = 'the last line inside the frontmatter'
CODE = 'a line before the first line of code'
PY = 'a line before the first line of code, outside the docstring and any PEP 723 block'


def read(path, *lines):
    return guide.file_citation(path, '\n'.join(lines))


def cited(path, line):
    return guide.Citation(path, line, IDS, '2.1.219'), []


def misplaced(path, line, place):
    return None, [f'{path}:{line}: a citation goes on {place} (R4.1)']


@pytest.mark.parametrize('path', ['skills/demo/SKILL.md', 'agents/demo.md', 'commands/demo.md',
                                  'rules/demo.md', '.claude/skills/demo/SKILL.md', '.claude/agents/demo.md'])
def test_markdown_with_frontmatter_cites_on_its_last_frontmatter_line(path):
    assert read(path, '---', 'name: demo', 'description: >', '  Use when testing.', HASH, '---', '',
                'Body.') == cited(path, 5)


def test_a_frontmatter_citation_anywhere_else_is_misplaced():
    path = 'skills/demo/SKILL.md'
    assert read(path, '---', HASH, 'name: demo', '---', 'Body.') == misplaced(path, 2, FRONT)
    assert read(path, '---', 'name: demo', '---', HASH) == misplaced(path, 4, FRONT)


def test_an_indented_citation_is_refused_since_yaml_would_read_it_as_text():
    path = 'skills/demo/SKILL.md'
    assert read(path, '---', 'description: >', '  Use when testing.', '  ' + HASH, '---') == (
        None, [f'{path}:4: an indented citation; it starts at column 0'])


def test_markdown_without_frontmatter_cites_on_its_first_line_in_the_html_form():
    assert read('CLAUDE.md', HTML, '', '# CLAUDE.md') == cited('CLAUDE.md', 1)
    assert read('hooks/README.md', '# Hooks', '', HTML) == misplaced('hooks/README.md', 3, 'the first line')
    assert read('README.md', HASH, '# Readme') == (
        None, [f'README.md:1: malformed citation; the form is {guide.HTML_FORM}'])


def test_python_cites_before_its_first_line_of_code_outside_docstring_and_pep723():
    path = 'hooks/demo.py'
    assert read(path, '#!/usr/bin/env python3', '# A comment.', HASH, "'''Doc.'''", 'import os') == cited(path, 3)
    assert read(path, "'''Doc.", 'More doc.', "'''", HASH, '', 'import os') == cited(path, 4)
    assert read(path, '# /// script', '# dependencies = []', '# ///', HASH, 'import os') == cited(path, 4)
    assert read(path, '# /// script', HASH, '# ///', 'import os') == misplaced(path, 2, PY)
    assert read(path, 'import os', HASH) == misplaced(path, 2, PY)
    assert read(path, "'''Doc.", HASH, "'''", 'import os') == misplaced(path, 2, PY)
    assert read(path, '@decorate', HASH, 'def f():', '    pass') == misplaced(path, 2, PY)


def test_a_python_file_that_does_not_parse_carries_no_citation():
    assert read('hooks/demo.py', HASH, 'def (') == (
        None, ['hooks/demo.py:1: no citation can go here: does not parse as Python (invalid syntax)'])


def test_shell_and_toml_cite_before_their_first_command_or_key():
    assert read('hooks/demo.sh', '#!/bin/sh', '# Gate.', HASH, 'set -e') == cited('hooks/demo.sh', 3)
    assert read('hooks/demo.sh', '#!/bin/sh', 'set -e', HASH) == misplaced('hooks/demo.sh', 3, CODE)
    assert read('build/githooks/pre-commit', '#!/usr/bin/env bash', HASH, 'exit 0') == cited(
        'build/githooks/pre-commit', 2)
    assert read('build/demo.toml', '# Register.', '', HASH, '[guide]') == cited('build/demo.toml', 3)
    assert read('build/demo.toml', '[guide]', HASH) == misplaced('build/demo.toml', 2,
                                                                 'a line before the first key or table')


def test_a_file_r41_has_no_slot_for_carries_no_citation():
    assert read('notes.txt', HASH) == (
        None, ['notes.txt:1: no citation can go here: R4.1 gives this kind of file no citation'])
    assert read('skills/demo/SKILL.md', '---', 'name: demo', HASH) == (
        None, ['skills/demo/SKILL.md:3: no citation can go here: its frontmatter never closes'])


def test_a_file_carries_one_citation():
    assert read('hooks/demo.sh', '#!/bin/sh', HASH, HASH, 'exit 0') == (
        None, ['hooks/demo.sh:3: a second citation; a file carries one'])


@pytest.mark.parametrize('line', [
    '# cc-guide: hooks.patterns',
    '# cc-guide: Hooks.patterns @2.1.219',
    '# cc-guide: hooks @2.1.219',
    '#cc-guide: hooks.patterns @2.1.219',
    '# cc-guide: hooks.patterns @latest',
    '# cc-guide: hooks.patterns, hooks.pitfalls @2.1.219',
])
def test_a_malformed_citation_names_the_form(line):
    assert read('hooks/demo.sh', '#!/bin/sh', line, 'exit 0') == (
        None, [f'hooks/demo.sh:2: malformed citation; the form is {guide.HASH_FORM}'])


def test_an_html_citation_in_a_script_is_code_so_it_is_misplaced():
    assert read('hooks/demo.sh', '#!/bin/sh', HTML, 'exit 0') == misplaced('hooks/demo.sh', 2, CODE)


def test_a_section_cited_twice_is_a_problem():
    assert read('hooks/demo.sh', '# cc-guide: hooks.patterns hooks.patterns @2.1.219') == (
        None, ['hooks/demo.sh:1: cites hooks.patterns twice'])


def test_a_four_part_stamp_is_a_well_formed_citation():
    citation, problems = read('hooks/demo.sh', '# cc-guide: hooks.patterns @2.1.288.1')
    assert (citation.stamp, problems) == ('2.1.288.1', [])


@pytest.mark.parametrize('line, shaped', [
    ('# cc-guide: x', True), ('  # cc-guide: x', True), ('\t#cc-guide:', True), ('<!--cc-guide: x', True),
    ('<!-- cc-guide:stamp -->', True), ('<!-- /cc-guide:stamp -->', False), ('x  # cc-guide: x', False),
    ("'# cc-guide: x',", False), ('## cc-guide: x', False),
])
def test_a_citation_shaped_line_is_read_only_at_line_start(line, shaped):
    assert bool(guide.CITE_SHAPED_RE.match(line)) is shaped


def test_read_citations_runs_in_path_order_and_by_section_groups_them():
    files = {'hooks/b.sh': '# cc-guide: hooks.patterns @2.1.219\n',
             'hooks/a.sh': '# cc-guide: hooks.pitfalls hooks.patterns @2.1.288\n',
             'hooks/c.sh': 'exit 0\n# cc-guide: hooks.patterns @2.1.219\n'}
    citations, problems = guide.read_citations(files)
    assert [c.path for c in citations] == ['hooks/a.sh', 'hooks/b.sh']
    assert problems == [f'hooks/c.sh:2: a citation goes on {CODE} (R4.1)']
    assert {sid: [c.path for c in cs] for sid, cs in guide.by_section(citations).items()} == {
        'hooks.pitfalls': ['hooks/a.sh'], 'hooks.patterns': ['hooks/a.sh', 'hooks/b.sh']}

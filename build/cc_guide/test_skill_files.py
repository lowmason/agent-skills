'''The /cc-guide skill and its verifier (drift spec R8.1, R12.4): each file
opens with its frontmatter and carries its citation as the frontmatter's
last line, the frontmatter sets what R8.1 names, and the report formats the
skill and the verifier state are the ones settle parses. The suite has no
YAML parser, so frontmatter lines are compared as text.'''
from pathlib import Path

import pytest

import guide
import settle
from cc_fixtures import isolated_home  # noqa: F401

REPO = Path(__file__).resolve().parents[2]
SKILL = '.claude/skills/cc-guide/SKILL.md'
AGENT = '.claude/agents/cc-guide-verifier.md'
FORMATS = '.claude/skills/cc-guide/references/formats.md'


def frontmatter(path: str) -> list[str]:
    '''The frontmatter's lines. check_frontmatter.py never reads .claude/,
    so this is the only check that the frontmatter opens the file.'''
    lines = (REPO / path).read_text(encoding='utf-8').split('\n')
    assert lines[0] == '---', f'{path} must open with its frontmatter'
    return lines[1:lines.index('---', 1)]


@pytest.mark.parametrize('path', [SKILL, AGENT])
def test_each_file_cites_the_guide_on_its_frontmatters_last_line(path):
    text = (REPO / path).read_text(encoding='utf-8')
    citation, problems = guide.file_citation(path, text)
    assert problems == []
    assert citation is not None and citation.line == len(frontmatter(path)) + 1


def test_the_skill_is_typed_only():
    assert {'name: cc-guide', 'disable-model-invocation: true'} <= set(frontmatter(SKILL))


def test_the_verifier_runs_on_sonnet_with_read_only_search_tools_and_no_claude_md():
    assert {'name: cc-guide-verifier', 'tools: Read, Grep, Glob', 'model: sonnet',
            'omitClaudeMd: true'} <= set(frontmatter(AGENT))


def test_the_verifier_reports_a_todo_reach_with_its_usual_verdict():
    '''Second review, finding 2: settle lists a correction within a
    TODO(owner)'s reach for the owner and holds its section, so the verifier
    keeps its STALE, WRONG or PARTIAL there rather than turning it into a
    JUDGMENT that holds nothing.'''
    (rule,) = [line for line in (REPO / AGENT).read_text(encoding='utf-8').split('\n') if 'TODO(owner)' in line]
    assert 'usual verdict' in rule and 'JUDGMENT' not in rule


@pytest.mark.parametrize('form', settle.FORMATS)
def test_the_skill_and_the_verifier_state_the_report_formats_settle_parses(form):
    for path in (AGENT, FORMATS):
        assert form in (REPO / path).read_text(encoding='utf-8'), f'{path} lacks {form!r}'


def contract_part(heading: str) -> str:
    '''The verifier's text under one `###` heading, up to the next.'''
    text = (REPO / AGENT).read_text(encoding='utf-8')
    start = text.index(f'### {heading}\n')
    end = text.find('\n### ', start + 1)
    return text[start:] if end == -1 else text[start:end]


@pytest.mark.parametrize('verdict', ['CONFIRMED', 'PARTIAL', 'STALE', 'WRONG'])
def test_the_verifier_defines_each_verdict_a_correction_turns_on(verdict):
    '''Plan 45: an audit rated true claims CONFIRMED while the passage it
    quoted gave a case they get wrong, since nothing defined the verdicts.'''
    assert f'{verdict}: ' in contract_part('verify and audit')


@pytest.mark.parametrize('verdict', ['consistent', 'contradicts', 'not covered'])
def test_the_verifier_defines_each_files_verdict(verdict):
    '''Plan 45: a files verifier rated a statement not covered that departed
    from the guide's own example.'''
    assert f'`{verdict}`: ' in contract_part('files')


@pytest.mark.parametrize('part', ['verify and audit', 'files'])
def test_each_mode_rates_by_the_same_failure_test(part):
    '''Plan 45: a files verifier wrote that a statement left out cases the
    guide gives, and still rated it consistent.'''
    assert 'as worded would get that case wrong' in contract_part(part)
    assert 'each further item' in contract_part(part)


def test_a_files_choice_that_differs_from_an_example_is_no_failure():
    '''Plan 45, review finding 3: a file that states a choice of its own,
    which a guide example makes differently, must not be rated contradicts.'''
    assert 'is no failure' in contract_part('files')


@pytest.mark.parametrize('path', [AGENT, FORMATS])
def test_a_files_row_gives_one_line_number(path):
    '''Plan 45: settle reads a files row's `file:line` with one line number,
    and a range is unparseable, which holds the file.'''
    assert 'gives one line number' in (REPO / path).read_text(encoding='utf-8')

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


def test_the_verifier_writes_a_none_line_exactly_and_no_other_line_with_a_pipe():
    '''Settle never reads prose as none, so a sentence-form none line or a
    `<section> | note` line (2026-10-20: agents/debugger.md and
    recommend-probabilistic-model in files, mechanisms.overview in verify)
    holds its section or file. The verifier gets the exact form. A sentence
    that offered notes a line of their own drew prose notes in 8 of 10
    micro-test reps and was cut, so the pipe rule beside it keeps notes out
    of rows.'''
    lines = (REPO / AGENT).read_text(encoding='utf-8').split('\n')
    (rule,) = [line for line in lines if 'none line is exactly' in line]
    assert '`<section> | none`' in rule and 'Put `|` in no other line.' in rule


@pytest.mark.parametrize('form', settle.FORMATS)
def test_the_skill_and_the_verifier_state_the_report_formats_settle_parses(form):
    for path in (AGENT, FORMATS):
        assert form in (REPO / path).read_text(encoding='utf-8'), f'{path} lacks {form!r}'

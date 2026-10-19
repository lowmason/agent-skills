'''The always-on writing rule must not drift from its skill: each line in the
rule's habit list appears word for word in the skill's SKILL.md. The boundary
paragraph and the pointer to the skill are not list lines, so they may differ.'''
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RULE = REPO / 'rules' / 'write-with-asd-ste100.md'
SKILL = REPO / 'skills' / 'write-with-asd-ste100' / 'SKILL.md'


def habit_lines() -> list[str]:
    return [line[2:] for line in RULE.read_text().splitlines() if line.startswith('- ')]


def test_the_rule_has_a_habit_list():
    assert habit_lines()


def test_each_habit_line_is_in_the_skill_word_for_word():
    skill = SKILL.read_text()
    assert [line for line in habit_lines() if line not in skill] == []

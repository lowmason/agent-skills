'''Tests for build_prompts.py: the prompt holds the skill text at <ref>, then the case's fixture, then the task.

The brief (Task 1, Interfaces): "`build_prompts.py <case> <arm> <ref>` writes the prompt file for one
case and arm. The full SKILL.md text at `<ref>` comes first, then the case's fixture." A treatment arm
uses the commit that `git stash create` prints (Global Constraints, Micro-tests). In plans 103's Tasks 2
and 3 HEAD still holds the control text when the treatment prompt is built, so a prompt that read the
text from HEAD or from the work tree would carry the control text and look right.

Each test builds a temporary git repository where the two SKILL.md files differ between commits, and a
temporary kit folder with one short fixture for each case. No test runs a model.
'''
import os
import subprocess
import sys
from pathlib import Path

import pytest

import build_prompts

SKILLS = {'using-git-worktrees': 'skills/using-git-worktrees/SKILL.md',
          'finishing-a-development-branch': 'skills/finishing-a-development-branch/SKILL.md'}
CASE_SKILL = {'noremote': 'using-git-worktrees', 'remote-nohead': 'using-git-worktrees',
              'archive-relay': 'finishing-a-development-branch'}
GIT_ENV = {'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@example.com', 'GIT_COMMITTER_NAME': 't',
           'GIT_COMMITTER_EMAIL': 't@example.com', 'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_SYSTEM': os.devnull}


def git(repo: Path, *args: str) -> str:
    run = subprocess.run(['git', *args], cwd=repo, check=True, capture_output=True, text=True,
                         env={**os.environ, **GIT_ENV})
    return run.stdout.strip()


def write_skills(repo: Path, version: str) -> None:
    for name, path in SKILLS.items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f'---\nname: {name}\n---\n\n# {name} text {version}\n')


class World:
    '''A repository with commit OLD (text v1), HEAD (text v2), and a stash commit (text v3).'''

    def __init__(self, tmp: Path) -> None:
        self.repo = tmp / 'repo'
        self.repo.mkdir()
        git(self.repo, 'init', '-q', '-b', 'main')
        write_skills(self.repo, 'v1')
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-q', '-m', 'v1')
        self.old = git(self.repo, 'rev-parse', 'HEAD')
        write_skills(self.repo, 'v2')
        git(self.repo, 'commit', '-q', '-a', '-m', 'v2')
        self.head = git(self.repo, 'rev-parse', 'HEAD')
        write_skills(self.repo, 'v3')
        self.stash = git(self.repo, 'stash', 'create')
        git(self.repo, 'checkout', '-q', '--', '.')
        self.kit = tmp / 'kit'
        (self.kit / 'fixtures').mkdir(parents=True)
        for case in CASE_SKILL:
            (self.kit / 'fixtures' / f'{case}.txt').write_text(f'FIXTURE-{case} state of the session\n')

    def build(self, case: str, arm: str, ref: str) -> str:
        sys.argv = ['build_prompts.py', case, arm, ref]
        build_prompts.main()
        return (self.kit / 'prompts' / f'{case}-{arm}.txt').read_text()


@pytest.fixture
def world(tmp_path: Path, monkeypatch) -> World:
    made = World(tmp_path)
    monkeypatch.chdir(made.repo)
    monkeypatch.setattr(build_prompts, 'KIT', made.kit)
    monkeypatch.setattr(sys, 'argv', sys.argv)
    return made


def test_the_skill_text_comes_from_the_ref_and_not_from_head_or_the_work_tree(world):
    assert world.old != world.head
    older = world.build('noremote', 'control', world.old)
    assert '# using-git-worktrees text v1' in older
    assert 'text v2' not in older and 'text v3' not in older
    # The stash commit holds v3, which HEAD and the work tree do not hold.
    assert world.stash and world.stash != world.head
    newer = world.build('remote-nohead', 'treatment', world.stash)
    assert '# using-git-worktrees text v3' in newer
    assert 'text v1' not in newer and 'text v2' not in newer


def test_the_prompt_holds_the_skill_text_first_then_the_fixture_then_the_task(world):
    text = world.build('noremote', 'control', world.old)
    assert text.startswith('<skill name="using-git-worktrees">\n---\nname: using-git-worktrees\n---')
    skill_end = text.index('</skill>')
    fixture_at = text.index('FIXTURE-noremote state of the session')
    task_at = text.index(build_prompts.TASK)
    assert text.index('text v1') < skill_end < fixture_at < task_at
    assert text.endswith(build_prompts.TASK)


@pytest.mark.parametrize('case', sorted(CASE_SKILL))
def test_each_case_reads_its_own_skill_and_its_own_fixture(world, case):
    text = world.build(case, 'control', world.old)
    skill = CASE_SKILL[case]
    other = next(name for name in SKILLS if name != skill)
    assert f'<skill name="{skill}">' in text
    assert f'# {skill} text v1' in text
    assert f'# {other} text' not in text
    assert f'FIXTURE-{case} state of the session' in text
    assert all(f'FIXTURE-{name} ' not in text for name in CASE_SKILL if name != case)


def test_the_arm_names_the_file_and_no_word_of_the_arm_reaches_the_prompt(world):
    control = world.build('noremote', 'control', world.old)
    treatment = world.build('noremote', 'treatment', world.stash)
    assert sorted(p.name for p in (world.kit / 'prompts').glob('noremote-*.txt')) == [
        'noremote-control.txt', 'noremote-treatment.txt']
    assert control.replace('text v1', 'text v3') == treatment
    assert 'control' not in control.lower() and 'treatment' not in treatment.lower()


def test_the_task_asks_for_run_tool_and_say_lines_and_a_stop_at_the_partner(world):
    task = world.build('noremote', 'control', world.old).split('</session>\n\n', 1)[1]
    assert 'a line that starts `RUN:`' in task
    assert 'a line that starts `TOOL:`, with the tool name and its arguments' in task
    assert 'a line that starts `SAY:`' in task
    assert 'Stop where you would wait for your partner.' in task

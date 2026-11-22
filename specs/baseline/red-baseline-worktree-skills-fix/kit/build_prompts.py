'''Build one prompt for plan 103's worktree-skills micro-test.

Usage, from the repository root:
  uv run python <kit>/build_prompts.py <case> <arm> <ref>
<case> is noremote, remote-nohead or archive-relay. <arm> names the arm (control, treatment) and only
labels the output. <ref> is a commit, or the commit that `git stash create` prints for a treatment arm.
The prompt holds, in order: the full SKILL.md text of the case's skill as it is at <ref> (read with
git show, never through ~/.claude), then the case's fixture (fixtures/<case>.txt), then the task.
Writes prompts/<case>-<arm>.txt and appends one line to prompts/MANIFEST.txt: the case, the arm, the
full sha of <ref>, the sha256 of the skill text and of the prompt, the model and the budget.
Refuses an existing prompt file. A case's skill text must not name the arm or the plan, and the
fixture holds no word of either.
'''
import hashlib
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
MODEL = 'claude-sonnet-5-5'
BUDGET = '0.50'

TASK = '''This is a decision-only exercise. You have no tools in this turn, so no command can run. Continue the session from here. Write what you do next, in order, up to the point where you would wait for your partner. Write each shell command you would run on a line that starts `RUN:`. Write each tool call on a line that starts `TOOL:`, with the tool name and its arguments. Write each thing you say to your partner on a line that starts `SAY:`. A command whose output you were not given runs and succeeds. Stop where you would wait for your partner.
'''

WORKTREES = 'skills/using-git-worktrees/SKILL.md'
FINISHING = 'skills/finishing-a-development-branch/SKILL.md'
# `pass` and `fail` are the case's columns of the record's Cases table. show_reps.py prints them on
# each grading sheet. build_prompts.py never writes them into a prompt.
CASES = {
    'noremote': {
        'skill': WORKTREES,
        'pass': '`git worktree add` on a new branch from HEAD, then `EnterWorktree` with `path`',
        'fail': '`EnterWorktree` with `name`, and no `git worktree add`',
    },
    'remote-nohead': {
        'skill': WORKTREES,
        'pass': '`git worktree add` on a new branch from HEAD, then `EnterWorktree` with `path`',
        'fail': '`EnterWorktree` with `name`, and no `git worktree add`',
    },
    'archive-relay': {
        'skill': FINISHING,
        'pass': 'tells the partner that archiving can discard uncommitted changes in the worktree, '
                'and that the branch can outlive the archive',
        'fail': 'says that archiving removes the worktree at once or deletes the branch, '
                'or leaves out either fact',
    },
}


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def git(*args: str) -> str:
    run = subprocess.run(['git', *args], capture_output=True, text=True)
    if run.returncode != 0:
        raise SystemExit(f'git {" ".join(args)} failed: {run.stderr.strip()}')
    return run.stdout


def prompt(case: str, skill_text: str) -> str:
    name = CASES[case]['skill'].split('/')[1]
    fixture = (KIT / 'fixtures' / f'{case}.txt').read_text()
    return (f'<skill name="{name}">\n{skill_text.rstrip(chr(10))}\n</skill>\n\n'
            f'<session>\n{fixture.rstrip(chr(10))}\n</session>\n\n{TASK}')


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    case, arm, ref = sys.argv[1:]
    if case not in CASES:
        raise SystemExit(f'refusing: no case {case}')
    if not arm.isalpha():
        raise SystemExit(f'refusing: arm {arm!r} must be letters only')
    out = KIT / 'prompts' / f'{case}-{arm}.txt'
    if out.exists():
        raise SystemExit(f'refusing: {out} exists')
    sha = git('rev-parse', '--verify', f'{ref}^{{commit}}').strip()
    skill_text = git('show', f'{sha}:{CASES[case]["skill"]}')
    text = prompt(case, skill_text)
    out.parent.mkdir(exist_ok=True)
    out.write_text(text)
    line = (f'{case} {arm} ref {sha} {CASES[case]["skill"]} sha256 {sha256(skill_text)} '
            f'prompt sha256 {sha256(text)} model {MODEL} budget {BUDGET}')
    with (out.parent / 'MANIFEST.txt').open('a') as manifest:
        manifest.write(line + '\n')
    print(f'wrote {out.relative_to(KIT)}\n{line}')


if __name__ == '__main__':
    main()

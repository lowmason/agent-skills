'''Fail when a skill names one of the six SDD and executing-plans helpers without an anchor.

The helpers are sdd-workspace, task-brief, review-package, task-start, task-done and mutant-run.
An agent runs them from the user's repository, so a bare `scripts/task-brief` can resolve against
that repository instead of the installed skill. Every mention in a Markdown file under `skills/` must
put `<this-skill-dir>/` right before `scripts/`, or `<this-skill-dir>/../<skill>/` for a helper
that another skill owns. The check also fails when it finds no mention at all, since its pattern
is then stale.

This adapts the idea of upstream's `tests/sdd-helper-paths/test-sdd-helper-paths.sh` (obra/superpowers,
#2607, MIT, see LICENSE-superpowers). That test looks for a phrase. This one reads each mention.
Usage, from the repository root: uv run python build/check_helper_paths.py
'''
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HELPERS = ('sdd-workspace', 'task-brief', 'review-package', 'task-start', 'task-done', 'mutant-run')
# A mention is `scripts/<helper>` that no word character or hyphen follows, so
# `scripts/task-briefing` is another file. A dot may follow a mention (a sentence end).
MENTION = re.compile(r'scripts/(' + '|'.join(HELPERS) + r')(?![\w-])')
ANCHOR = re.compile(r'<this-skill-dir>/(?:\.\./[a-z0-9-]+/)?$')
STALE = 'no helper reference under skills/; the pattern is stale'


def check(root: Path) -> tuple[list[str], int]:
    problems: list[str] = []
    found = 0
    for path in sorted((root / 'skills').rglob('*.md')):
        name = path.relative_to(root).as_posix()
        for number, line in enumerate(path.read_text(encoding='utf-8').split('\n'), start=1):
            for mention in MENTION.finditer(line):
                found += 1
                if not ANCHOR.search(line[:mention.start()]):
                    problems.append(f'{name}:{number}: scripts/{mention.group(1)} has no <this-skill-dir>/ anchor')
    if not found:
        return [STALE], 0
    return problems, found


def main() -> int:
    problems, found = check(ROOT)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    print(f'helper paths: {found} references anchored')
    return 0


if __name__ == '__main__':
    sys.exit(main())

'''Fail when the four reviewer surfaces' copies of the shared reviewer block differ.

The block runs from its `## Review scope` heading through the end of its
`## Declined to judge` section. Two copies sit inside dispatch templates at the
template's indentation; the check removes that indentation before it compares.
Usage, from the repository root: uv run python build/check_reviewer_block.py
'''
import difflib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = (
    'agents/code-reviewer.md',
    'agents/task-reviewer.md',
    'skills/requesting-code-review/code-reviewer.md',
    'skills/subagent-driven-development/task-reviewer-prompt.md',
)
START = '## Review scope'
LAST = '## Declined to judge'


class BlockError(ValueError):
    pass


def extract_block(text: str) -> str:
    lines = text.split('\n')
    starts = [i for i, line in enumerate(lines) if line.strip() == START]
    if len(starts) != 1:
        raise BlockError(f'expected one {START!r} line, found {len(starts)}')
    first = starts[0]
    indent = lines[first][:len(lines[first]) - len(lines[first].lstrip(' '))]
    lasts = [i for i in range(first, len(lines)) if lines[i].strip() == LAST]
    if not lasts:
        raise BlockError(f'no {LAST!r} line after {START!r}')
    end = lasts[0] + 1
    while end < len(lines):
        line = lines[end]
        if line.strip() and (not line.startswith(indent) or line.strip().startswith(('## ', '```'))):
            break
        end += 1
    block = lines[first:end]
    while block and not block[-1].strip():
        block.pop()
    return '\n'.join(line[len(indent):] for line in block) + '\n'


def check(root: Path) -> list[str]:
    problems: list[str] = []
    blocks: dict[str, str] = {}
    for name in FILES:
        path = root / name
        if not path.is_file():
            problems.append(f'{name}: missing')
            continue
        try:
            blocks[name] = extract_block(path.read_text())
        except BlockError as err:
            problems.append(f'{name}: {err}')
    if not blocks:
        return problems
    reference_name = FILES[0] if FILES[0] in blocks else next(iter(blocks))
    reference = blocks[reference_name]
    others = {name: block for name, block in blocks.items() if name != reference_name}
    agreed = set(others.values())
    if reference_name == FILES[0] and len(others) >= 2 and len(agreed) == 1 and agreed != {reference}:
        name = next(iter(others))
        problems.append(f'{FILES[0]}: its reviewer block differs from the other copies, '
                        f'which agree with each other:\n{show_diff(reference, others[name], FILES[0], name)}')
        return problems
    for name, block in others.items():
        if block != reference:
            problems.append(f'{name}: its reviewer block differs from {reference_name}:\n'
                            f'{show_diff(reference, block, reference_name, name)}')
    return problems


def show_diff(reference: str, block: str, reference_name: str, name: str) -> str:
    '''Diff the two blocks line by line, with each line as its repr so a trailing space or tab shows.

    Lines split on `\\n` only: `splitlines()` would also split on characters such as `\\x0c`,
    and a drift in one of those would print an empty diff.'''
    lines = difflib.unified_diff(
        [repr(line) for line in reference.split('\n')],
        [repr(line) for line in block.split('\n')],
        reference_name, name, lineterm='')
    return '\n'.join(lines)


def main() -> int:
    problems = check(ROOT)
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 1
    print(f'reviewer block: {len(FILES)} copies identical')
    return 0


if __name__ == '__main__':
    sys.exit(main())

'''Check that a verbatim move kept every line of a SKILL.md.

Usage, from the repository root:
  python3 <kit>/check_moved_lines.py <base-sha> <skill-dir>
Reads <skill-dir>/SKILL.md at <base-sha> with git show, then the working tree's
<skill-dir>/SKILL.md and every <skill-dir>/references/*.md. Prints each non-blank line
of the old SKILL.md that appears in none of the new files, then a count. Exits 0 when
no line is missing. Lines changed on purpose (pointer fixes) are listed by hand in the
task report; every printed line must be on that list.
'''
import subprocess
import sys
from pathlib import Path


def main() -> None:
    base, skill = sys.argv[1], Path(sys.argv[2])
    old = subprocess.run(['git', 'show', f'{base}:{skill.as_posix()}/SKILL.md'], check=True,
                         capture_output=True, text=True).stdout
    new_lines = set()
    for path in [skill / 'SKILL.md', *sorted((skill / 'references').glob('*.md'))]:
        new_lines.update(line.rstrip() for line in path.read_text().splitlines())
    missing = [(n, line) for n, line in enumerate(old.splitlines(), 1)
               if line.strip() and line.rstrip() not in new_lines]
    for n, line in missing:
        print(f'{skill.as_posix()}/SKILL.md:{n}: {line}')
    print(f'{len(missing)} line(s) missing')
    sys.exit(1 if missing else 0)


if __name__ == '__main__':
    main()

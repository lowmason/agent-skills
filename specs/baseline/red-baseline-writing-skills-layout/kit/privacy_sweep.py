'''Sweep files for the user's identity forms and the home directory before they are committed.

Usage, from the repository root:
  uv run python <kit>/privacy_sweep.py <path> ...
Each <path> is a file or a directory, read recursively. The forms are kit_identity.py's, read at
run time, plus the home directory path and its parent directory's path. A hit prints the file,
the line number and the kind of form (email, local part, name, user, home), never the value. Exit 1
on any hit, 0 when every file is clean. The last line gives the number of files swept.
'''
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_identity  # noqa: E402

KINDS = {kit_identity.EMAIL: 'email', kit_identity.LOCAL: 'local part', kit_identity.NAME: 'name',
         kit_identity.USER: 'user'}


def files(paths: list[str]) -> list[Path]:
    found = []
    for arg in paths:
        path = Path(arg)
        found += sorted(p for p in path.rglob('*') if p.is_file()) if path.is_dir() else [path]
    return found


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    checks = [(kit_identity.pattern(value), KINDS[token]) for value, token in kit_identity.forms()]
    home, homes = str(Path.home()), str(Path.home().parent).rstrip('/') + '/'
    swept, hits = files(sys.argv[1:]), 0
    for path in swept:
        for number, line in enumerate(path.read_text(errors='replace').splitlines(), 1):
            kinds = [kind for check, kind in checks if check.search(line)]
            if home in line or homes in line:
                kinds.append('home')
            for kind in kinds:
                hits += 1
                print(f'{path}:{number}: {kind}')
    print(f'privacy sweep: {len(swept)} file(s), {hits} hit(s)')
    sys.exit(1 if hits else 0)


if __name__ == '__main__':
    main()

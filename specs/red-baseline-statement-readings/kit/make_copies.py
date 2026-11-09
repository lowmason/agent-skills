'''Build the probe's plan copies: three with one planted misread each, one unchanged (plan 81).

Usage, from the repository root:
  uv run python <kit>/make_copies.py selftest   builds every copy in memory, checks it, prints each plant's sites
  uv run python <kit>/make_copies.py build      writes specs/red-baseline-acceptance-tests/copies/
'''
import difflib
import hashlib
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract import reader_inputs, section_of  # noqa: E402
from plants import COPIES, Plant  # noqa: E402

KIT = Path(__file__).resolve().parent
REPO = KIT.parents[2]
COPIES_DIR = KIT.parent / 'copies'
LEAKS = ('def test_', '- [ ] **Step', '## Global Constraints', '## Review Focus', '## Decisions')
SITE_TEXT_WIDTH = 80


@dataclass(frozen=True)
class Site:
    line: int
    section: str
    text: str


def git_show(commit: str, path: str) -> str:
    return subprocess.run(['git', 'show', f'{commit}:{path}'], cwd=REPO, check=True,
                          capture_output=True, text=True).stdout


def plant(source: str, plant: Plant) -> tuple[str, list[Site]]:
    '''Apply the plant's replacements in order; the sites are the planted copy's changed lines.'''
    planted = source
    for old, new, count in plant.replacements:
        if planted.count(old) != count:
            raise ValueError(f'{old!r} occurs {planted.count(old)} times, not {count}')
        planted = planted.replace(old, new)
    before, after = source.split('\n'), planted.split('\n')
    changed = []
    for tag, _i1, _i2, j1, j2 in difflib.SequenceMatcher(None, before, after, autojunk=False).get_opcodes():
        if tag != 'equal':
            changed.extend(range(j1, j2))
    return planted, [Site(j + 1, section_of(planted, j + 1), after[j]) for j in changed]


def true_hits(planted: str, plant: Plant) -> list[str]:
    '''The lines that still match a true pattern and are not keep lines.'''
    patterns = [re.compile(p) for p in plant.true_patterns]
    keeps = [text for text, _reason in plant.keep]
    return [line for line in planted.split('\n')
            if any(p.search(line) for p in patterns) and not any(k in line for k in keeps)]


def site_lines(sites) -> list[str]:
    return [f'{s.line}  {s.section}  {s.text.strip()[:SITE_TEXT_WIDTH]}' for s in sites]


def write_new(path: Path, text: str) -> None:
    '''Write `text`, refusing to overwrite a file that differs.'''
    if path.exists() and path.read_text() != text:
        raise SystemExit(f'refusing: {path} exists and differs')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def build() -> None:
    manifest = []
    for copy in COPIES:
        source = git_show(copy.commit, copy.plan_path)
        planted, sites = (source, []) if copy.plant is None else plant(source, copy.plant)
        files = {
            'spec.md': (git_show(copy.commit, copy.spec_path), copy.spec_path),
            'plan.md': (planted, copy.plan_path),
            'SITES.txt': (''.join(f'{line}\n' for line in site_lines(sites)), None),
        }
        for name, (text, source_path) in files.items():
            path = COPIES_DIR / copy.id / name
            write_new(path, text)
            origin = f'{copy.commit}:{source_path}' if source_path else 'built'
            digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
            manifest.append(f'{digest}  {path.relative_to(REPO)}  {origin}')
        print(f'{copy.id}: {len(sites)} sites')
    write_new(COPIES_DIR / 'MANIFEST.txt', ''.join(f'{line}\n' for line in manifest))
    print(f'wrote {COPIES_DIR.relative_to(REPO)}')


def selftest() -> None:
    for copy in COPIES:
        source = git_show(copy.commit, copy.plan_path)
        if copy.plant is None:
            planted, sites = source, []
            assert planted == source                              # p55-clean only
        else:
            for old, _new, count in copy.plant.replacements:
                assert source.count(old) == count, (copy.id, old, source.count(old))
            planted, sites = plant(source, copy.plant)
            assert true_hits(planted, copy.plant) == [], (copy.id, true_hits(planted, copy.plant))
            assert any(site.section == 'test-step' for site in sites), copy.id   # DF3
        for leak in LEAKS:
            assert leak not in reader_inputs(planted), (copy.id, leak)
        print(f'== {copy.id}: {len(sites)} sites')
        for line in site_lines(sites):
            print(line)
    print('make_copies selftest ok')


if __name__ == '__main__':
    if sys.argv[1:] == ['selftest']:
        selftest()
    elif sys.argv[1:] == ['build']:
        build()
    else:
        sys.exit(__doc__)

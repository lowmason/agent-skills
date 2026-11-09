'''Build the statement-readings probe's six copies (plan 83): plan 81's three plants, each with its defense
line (PD1), two specs with one sentence edited (PD2), and plan 55 unchanged.

Usage, from the repository root:
  uv run python <kit>/make_copies.py selftest   builds every copy in memory, checks it, prints each copy's sites,
                                                planted sentence and amended sentences
  uv run python <kit>/make_copies.py build      writes specs/red-baseline-statement-readings/copies/
Each copy folder holds spec.md, plan.md, numbered.txt (the spec numbered by number.py) and SITES.txt.
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
from number import Sentence, flatten, number, numbered_text  # noqa: E402
from plants import AMENDED_LINES, COPIES, Copy, Plant, TwoReading, source_id  # noqa: E402

KIT = Path(__file__).resolve().parent
REPO = KIT.parents[2]
COPIES_DIR = KIT.parent / 'copies'
PLAN81_COPIES = REPO / 'specs' / 'red-baseline-acceptance-tests' / 'copies'
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
    '''Apply the plant's replacements in order, then insert the defense line after the one line that starts
    with its anchor (PD1). The sites are the planted copy's changed lines.'''
    planted = source
    for old, new, count in plant.replacements:
        if planted.count(old) != count:
            raise ValueError(f'{old!r} occurs {planted.count(old)} times, not {count}')
        planted = planted.replace(old, new)
    anchor, defense = plant.defense
    lines = planted.split('\n')
    starts = [i for i, line in enumerate(lines) if line.startswith(anchor)]
    if len(starts) != 1:
        raise ValueError(f'{len(starts)} lines start with the defense anchor {anchor!r}, not 1')
    lines.insert(starts[0] + 1, defense)
    planted = '\n'.join(lines)
    before, after = source.split('\n'), planted.split('\n')
    changed = []
    for tag, _i1, _i2, j1, j2 in difflib.SequenceMatcher(None, before, after, autojunk=False).get_opcodes():
        if tag != 'equal':
            changed.extend(range(j1, j2))
    return planted, [Site(j + 1, section_of(planted, j + 1), after[j]) for j in changed]


def edit_spec(source: str, two: TwoReading) -> str:
    '''The source spec with the one sentence edit of a two-reading plant (PD2).'''
    old, new = two.edit
    if source.count(old) != 1:
        raise ValueError(f'{old!r} occurs {source.count(old)} times in the spec, not 1')
    return source.replace(old, new)


def spec_key(copy: Copy) -> str:
    return copy.plant.spec_key if copy.plant else copy.two.spec_key


def planted_sentence(copy: Copy, sentences: list[Sentence]) -> Sentence:
    '''The one sentence whose flattened text holds the flattened spec_key of the plant or the edit.'''
    key = flatten(spec_key(copy))
    hits = [s for s in sentences if key in flatten(s.text)]
    if len(hits) != 1:
        raise ValueError(f'{copy.id}: {len(hits)} sentences hold {key!r}, not 1')
    return hits[0]


def amended_sentences(copy: Copy, sentences: list[Sentence]) -> set[int]:
    '''The n of each sentence whose lines meet the copy's answer key (PD3).'''
    key = AMENDED_LINES[source_id(copy)]
    return {s.n for s in sentences if any(s.lines[0] <= last and first <= s.lines[1] for first, last in key)}


def _ids(items) -> str:
    return ','.join(map(str, items)) or '-'


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
        spec = git_show(copy.commit, copy.spec_path)
        if copy.two is not None:
            spec = edit_spec(spec, copy.two)
        files = {
            'spec.md': (spec, copy.spec_path),
            'plan.md': (planted, copy.plan_path),
            'numbered.txt': (numbered_text(number(spec)), None),
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
        source_spec = git_show(copy.commit, copy.spec_path)
        spec = source_spec if copy.two is None else edit_spec(source_spec, copy.two)
        if copy.plant is not None:                                        # plan 81's assertions
            for old, _new, count in copy.plant.replacements:
                assert source.count(old) == count, (copy.id, old, source.count(old))
        planted, sites = (source, []) if copy.plant is None else plant(source, copy.plant)
        if copy.plant:
            assert any(site.section == 'test-step' for site in sites), copy.id   # plan 81's DF3
            assert planted.count(copy.plant.defense[1]) == 1, copy.id
            assert any(site.section == 'global-constraints' and site.text == copy.plant.defense[1]
                       for site in sites), copy.id
            assert true_hits(planted, copy.plant) == [], (copy.id, true_hits(planted, copy.plant))  # no true value
            assert planted.replace(copy.plant.defense[1] + '\n', '', 1) == \
                (PLAN81_COPIES / copy.id / 'plan.md').read_text(), copy.id
        else:
            assert planted == source, copy.id
        if copy.id in ('p55-clean', 'p55-exit'):
            assert planted == (PLAN81_COPIES / 'p55-clean' / 'plan.md').read_text(), copy.id
        for leak in LEAKS:
            assert leak not in reader_inputs(planted), (copy.id, leak)
        sentences = number(spec)
        target = None
        if copy.plant or copy.two:
            target = planted_sentence(copy, sentences)                   # exactly one sentence holds the key
            assert target.n not in amended_sentences(copy, sentences), copy.id   # Review Focus 1, trap 3
        if copy.plant:
            flat = flatten(target.text)                                  # PD10: the spec's words hold a spec token
            assert any(t in flat for t in copy.plant.spec_tokens), (copy.id, flat)
            assert not any(t in flat for t in copy.plant.plant_tokens), (copy.id, flat)
        if copy.two is None:
            assert spec == source_spec, copy.id
        else:
            before = number(source_spec)
            assert len(before) == len(sentences), copy.id
            assert [b.n for b, a in zip(before, sentences) if b.text != a.text] == [target.n], copy.id
            others = [flatten(a.text) for a in sentences if a.n != target.n]
            hits = [(d, t[:80]) for d in copy.two.deciders for t in others if re.search(d, t)]
            assert not hits, (copy.id, hits)
            assert flatten(before[target.n - 1].text) not in flatten(planted), copy.id   # the plan does not quote it
        print(f'== {copy.id}: {len(sites)} sites')
        for line in site_lines(sites):
            print(line)
        if target:
            print(f'planted sentence: S{target.n}  {target.text[:SITE_TEXT_WIDTH]}')
        print(f'amended sentences: {_ids(sorted(amended_sentences(copy, sentences)))}')
    print('make_copies selftest ok')


if __name__ == '__main__':
    if sys.argv[1:] == ['selftest']:
        selftest()
    elif sys.argv[1:] == ['build']:
        build()
    else:
        sys.exit(__doc__)

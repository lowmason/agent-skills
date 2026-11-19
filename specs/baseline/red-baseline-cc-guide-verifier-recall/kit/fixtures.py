'''Build the packet copies that plan 102's reps read, under Python 3.13
(Task 7):

    fixtures.py build

It writes $K/fixtures/ from the masters under ~/.cache/agent-skills/:
  - one copy of the audit master per arm, without report.md or
    settled.json. Only the second arm's copy gains listed.md and index.json
    `listed`: packets.listed_bullets over that copy's own changelog.md and
    guide.md, with group `models`'s terms under 5bd78a7's manifest.toml;
  - docs/, a copy of the 2.1.296 docs snapshot;
  - readme/, a copy of the readme master with `"covered": {}` added to its
    index.json, as a files packet built today would hold;
  - precision/, a copy of the packet Task 7 Step 1 built.
Every packet copy leaves out its top-level report.md and settled.json, as a
rep's copy does. Then it writes $K/fixtures.sha256, a `shasum -a 256`
listing of every file under $K/fixtures/, by its path from $K, and prints
the listed-item count.

It refuses (exit 1) when $K/fixtures/ already exists, when a master is
missing, or when the listed items hold no item at changelog line 1288 (P11)
or 1702 (P8). It builds in $K/fixtures.part/ and renames that folder only
when every copy is done, so a refusal leaves no fixtures. It only reads the
masters: shutil.copytree copies them, and every write goes under $K.

Nothing it prints names an arm or a path (plan 45's DF15). Exit 0 on
success, 1 on a refusal, 2 on a usage error or a failure.'''
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import common
import packets
import state
from docs import CHANGELOG

MANIFEST_COMMIT = '5bd78a7'  # the manifest the audit packet was built under (plan 45's key)
GROUP = 'models'
REQUIRED_LINES = (1288, 1702)  # the changelog bullets behind P11 and P8
DOCS_MASTER = 'cc-guide/2.1.296/docs'
SKIP = frozenset({packets.REPORT, packets.SETTLED})
FIXTURES, PART, LISTING = 'fixtures', 'fixtures.part', 'fixtures.sha256'
USAGE = 'usage: fixtures.py build'


class Refusal(Exception):
    '''A build this script declines; its message names no arm and no path.'''


def master_root() -> Path:
    '''~/.cache/agent-skills, read from HOME when called.'''
    return Path(os.environ['HOME']) / '.cache' / 'agent-skills'


def masters(root: Path) -> dict[str, Path]:
    '''Each master by name: the three packets of common.PACKETS and the docs.'''
    return {name: root / spec['master'] for name, spec in common.PACKETS.items()} | {'docs': root / DOCS_MASTER}


def manifest_text() -> str:
    '''build/cc_guide/manifest.toml as it stood at MANIFEST_COMMIT.'''
    proc = subprocess.run(['git', 'show', f'{MANIFEST_COMMIT}:{state.MANIFEST}'], cwd=common.REPO,
                          capture_output=True)
    if proc.returncode != 0:
        raise Refusal(f'git show {MANIFEST_COMMIT}:{state.MANIFEST} failed')
    return proc.stdout.decode('utf-8')


def listed(packet: Path, manifest: str) -> list[dict]:
    '''The changelog bullets that name a term of GROUP, from the packet's own files.'''
    guide = (packet / packets.GUIDE).read_text(encoding='utf-8')
    changelog = (packet / CHANGELOG).read_text(encoding='utf-8')
    terms = state.group_terms(state.parse_manifest(manifest), guide)[GROUP]
    return packets.listed_bullets(changelog, terms, guide)


def skip_top(top: Path):
    '''A copytree ignore that leaves SKIP out of the copied folder's top only.'''
    return lambda folder, names: SKIP & set(names) if Path(folder) == top else set()


def copy(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst, ignore=skip_top(src))


def read_index(folder: Path) -> dict:
    return json.loads((folder / packets.INDEX).read_text(encoding='utf-8'))


def write_index(folder: Path, index: dict) -> None:
    (folder / packets.INDEX).write_text(json.dumps(index, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')


def with_listed(index: dict, items: list[dict]) -> dict:
    '''The index with `listed` just after `releases`, where packets.audit puts it.'''
    out = {}
    for key, value in index.items():
        out[key] = value
        if key == 'releases':
            out['listed'] = items
    return out if 'listed' in out else out | {'listed': items}


def listing(k: Path) -> str:
    '''`shasum -a 256` lines for every file under $K/fixtures/, by path from $K.'''
    files = sorted(p for p in (k / FIXTURES).rglob('*') if p.is_file())
    return ''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(k)}\n' for p in files)


def fill(part: Path, src: dict[str, Path], manifest: str) -> int:
    '''Write every copy into part; the listed-item count.'''
    control, changed = (part / f'audit-{arm}' for arm in common.ARMS)
    copy(src['audit'], control)
    copy(src['audit'], changed)
    items = listed(changed, manifest)
    lines = {e['line'] for e in items}
    absent = [str(n) for n in REQUIRED_LINES if n not in lines]
    if absent:
        raise Refusal(f"the listed items hold no item at changelog line {', '.join(absent)}")
    (changed / packets.LISTED).write_text('\n'.join(packets.listed_lines(items)) + '\n', encoding='utf-8')
    write_index(changed, with_listed(read_index(changed), items))
    copy(src['docs'], part / 'docs')
    copy(src['readme'], part / 'readme')
    readme = read_index(part / 'readme')
    if 'covered' not in readme:
        write_index(part / 'readme', readme | {'covered': {}})
    copy(src['precision'], part / 'precision')
    return len(items)


def build(sources: dict[str, Path] | None = None, manifest: str | None = None) -> int:
    '''Build $K/fixtures/ from the masters (by default the ones under HOME)
    and the manifest (by default MANIFEST_COMMIT's).'''
    k = common.k_dir()
    if (k / FIXTURES).exists():
        raise Refusal('the fixtures exist; move them away to build them again')
    src = sources if sources is not None else masters(master_root())
    missing = [name for name, path in src.items() if not path.is_dir()]
    if missing:
        raise Refusal(f"missing master: {', '.join(missing)}")
    part = k / PART
    shutil.rmtree(part, ignore_errors=True)
    part.mkdir(parents=True)
    try:
        count = fill(part, src, manifest if manifest is not None else manifest_text())
    except BaseException:
        shutil.rmtree(part, ignore_errors=True)
        raise
    part.rename(k / FIXTURES)
    (k / LISTING).write_text(listing(k), encoding='utf-8')
    print(f'listed items: {count}')
    print(f'fixtures written; their sha256 listing is {LISTING}')
    return 0


def main_with(argv: list[str], sources: dict[str, Path] | None, manifest: str | None) -> int:
    '''main, with the masters and the manifest given (the tests pass fakes).'''
    if argv != ['build']:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        return build(sources, manifest)
    except Refusal as refusal:
        print(f'fixtures.py: refused: {refusal}', file=sys.stderr)
        return 1
    except Exception as error:  # its message may name a fixture path, which names an arm
        print(f'fixtures.py: failed ({type(error).__name__})', file=sys.stderr)
        return 2


def main(argv: list[str]) -> int:
    return main_with(argv, None, None)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

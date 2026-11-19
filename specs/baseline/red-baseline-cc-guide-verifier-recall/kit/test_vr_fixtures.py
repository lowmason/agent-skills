'''No-model tests of plan 102's fixture build (Task 7).

Every test runs with HOME and common.R under pytest's temporary folder, so
common.k_dir() is temporary too; the autouse fixture checks both before the
test body runs. The masters are fakes in that folder, except in
test_the_changed_audit_copy_lists_p11_and_p8, which reads the real audit
master read-only and skips when it is absent. REAL_HOME is read from the
password database at import, before any fixture moves HOME.'''
import hashlib
import json
import os
import pwd
import subprocess
from pathlib import Path

import pytest

import common
import fixtures
import packets
import state

ARM_WORDS = ('control', 'changed')
REAL_HOME = Path(pwd.getpwuid(os.getuid()).pw_dir)
REAL_AUDIT = REAL_HOME / '.cache' / 'agent-skills' / common.PACKETS['audit']['master']

MANIFEST = '\n'.join([
    '[guide]',
    "path = 'specs/guides/claude-code-customization-guide.md'",
    '',
    '[sources]',
    "docs_base = 'https://code.claude.com/docs/en/'",
    "llms = 'https://code.claude.com/docs/llms.txt'",
    "changelog = 'https://code.claude.com/docs/en/changelog.md'",
    "platform_base = 'https://platform.claude.com/docs/en/'",
    '',
    '[cadence]',
    'changelog_days = 7',
    'probe_days = 7',
    'audit_days = 30',
    '',
    '[groups.models]',
    "sections = ['models.routing', 'models.cache']",
    "all = ['model-config']",
    "terms = ['env-vars']",
    '',
    '[groups.hooks]',
    "sections = ['hooks.events']",
    "all = ['hooks']",
    "terms = ['env-vars']",
    '',
])

GUIDE = '\n'.join([
    '# Guide',
    '',
    '## Models',
    '<!-- cc: models.routing -->',
    'Limit the picker with `pickModels`, or drop one with `dropModels`.',
    '',
    '## Cache',
    '<!-- cc: models.cache -->',
    'The cache lasts five minutes.',
    '',
    '## Events',
    '<!-- cc: hooks.events -->',
    'A hook may set `hookOnly`.',
    '',
])

AUDIT_INDEX = {'mode': 'audit', 'inputs': 'the working tree', 'head': '2.1.300', 'group': 'models',
               'sections': ['models.routing', 'models.cache'],
               'lines': {'models.routing': [3, 6], 'models.cache': [7, 10]}, 'docs': '/master/docs',
               'releases': [], 'held': [],
               'quotes': {'guide': ['guide.md'], 'changelog': ['changelog.md'], 'docs': ['/master/docs']},
               'blocks': []}
README_INDEX = {'mode': 'files', 'file': 'hooks/README.md', 'copy': 'cited_README.md', 'stamp': '2.1.219',
                'sections': ['hooks.events'], 'lines': {'hooks.events': [11, 14]}, 'quotes': {'guide': ['guide.md']}}
PRECISION_INDEX = {'mode': 'files', 'file': 'skills/x/SKILL.md', 'copy': 'cited_SKILL.md', 'stamp': '2.1.326',
                   'sections': ['models.cache'], 'lines': {'models.cache': [7, 10]}, 'quotes': {'guide': ['guide.md']},
                   'covered': {'skills/x/references/a.md': 'covered/references/a.md'}}


def changelog_text(at: tuple[int, ...] = (1288, 1702)) -> str:
    '''A changelog in the bold-label format whose bullets name a models term
    on each line in `at`, a hooks-only term on line 900, and nothing else.'''
    lines = ['# Changelog', '', '**2.1.300**', '']
    named = {line: f'- Added `pickModels` support, item {line}.' for line in at} | {
        900: '- Added `hookOnly` for hooks.'}
    while len(lines) < 1800:
        lines.append(named.get(len(lines) + 1, '- Fixed a typo.'))
    return '\n'.join(lines + ['']) + '\n'


@pytest.fixture(autouse=True)
def sandbox(tmp_path, tmp_path_factory, monkeypatch):
    '''HOME and R under pytest's temporary folder, checked before any test body runs.'''
    base = tmp_path_factory.getbasetemp().resolve()
    home = tmp_path / 'home'
    home.mkdir()
    monkeypatch.setenv('HOME', str(home))
    monkeypatch.setattr(common, 'R', tmp_path / 'R')
    for path in (Path(os.environ['HOME']), common.R, common.k_dir(), fixtures.master_root()):
        assert path.resolve().is_relative_to(base), path
    return base


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    return path


def write_json(path: Path, obj) -> Path:
    return write(path, json.dumps(obj, indent=1) + '\n')


def fake_masters(where: dict[str, Path], changelog: str | None = None) -> dict[str, Path]:
    '''Fake masters at the given folders: an audit packet with its original
    report, a readme packet without `covered`, a precision packet whose
    covered files include a nested report.md, and a docs snapshot.'''
    audit, readme, precision, docs = where['audit'], where['readme'], where['precision'], where['docs']
    write_json(audit / 'index.json', AUDIT_INDEX)
    write(audit / 'guide.md', GUIDE)
    write(audit / 'changelog.md', changelog if changelog is not None else changelog_text())
    for leaf in ('sections.md', 'releases.md', 'blocks.md', 'report.md', 'settled.json'):
        write(audit / leaf, f'{leaf}\n')
    write_json(readme / 'index.json', README_INDEX)
    for leaf in ('cited_README.md', 'guide.md', 'sections.md', 'report.md'):
        write(readme / leaf, f'{leaf}\n')
    write_json(precision / 'index.json', PRECISION_INDEX)
    for leaf in ('cited_SKILL.md', 'guide.md', 'sections.md', 'covered/references/a.md',
                 'covered/references/report.md'):
        write(precision / leaf, f'{leaf}\n')
    write(docs / 'settings.md', 'Docs settings page.\n')
    write(docs / 'sub' / 'nested.md', 'A nested page.\n')
    return dict(where)


def masters_in(folder: Path, changelog: str | None = None) -> dict[str, Path]:
    return fake_masters({name: folder / name for name in ('audit', 'readme', 'precision', 'docs')}, changelog)


def tree_state(root: Path) -> list[tuple]:
    '''Every path under root, root included: its mode and mtime, and a file's sha256.'''
    out = []
    for path in [root, *sorted(root.rglob('*'))]:
        st = path.lstat()
        digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        out.append((str(path.relative_to(root)), st.st_mode, st.st_mtime_ns, digest))
    return out


def fx() -> Path:
    return common.k_dir() / 'fixtures'


def index_of(name: str) -> dict:
    return json.loads((fx() / name / 'index.json').read_text(encoding='utf-8'))


def no_arm_named(text: str) -> bool:
    return not any(w in text.lower() for w in ARM_WORDS)


# --- the plan's tests ---------------------------------------------------------------------------------------


def test_the_changed_audit_copy_lists_p11_and_p8(tmp_path):
    if not REAL_AUDIT.is_dir():
        pytest.skip(f'the audit master is absent (it lives only in the owner\'s cache): {REAL_AUDIT}')
    before = tree_state(REAL_AUDIT)
    sources = masters_in(tmp_path / 'masters') | {'audit': REAL_AUDIT}
    assert fixtures.build(sources) == 0
    lines = {e['line'] for e in index_of('audit-changed')['listed']}
    assert {1288, 1702} <= lines
    assert 'listed' not in index_of('audit-control')
    assert not (fx() / 'audit-control' / 'listed.md').exists()
    assert tree_state(REAL_AUDIT) == before


def test_a_fixture_build_never_writes_under_a_master(tmp_path):
    sources = masters_in(tmp_path / 'masters')
    before = {name: tree_state(path) for name, path in sources.items()}
    assert fixtures.build(sources, MANIFEST) == 0
    assert {name: tree_state(path) for name, path in sources.items()} == before
    assert (fx() / 'audit-changed' / 'listed.md').is_file()


# --- the input shapes of the stated rules -------------------------------------------------------------------


def test_the_constants_hold_the_plans_values():
    assert fixtures.REQUIRED_LINES == (1288, 1702)
    assert fixtures.MANIFEST_COMMIT == '5bd78a7'
    assert fixtures.GROUP == 'models'
    assert fixtures.DOCS_MASTER == 'cc-guide/2.1.296/docs'
    assert fixtures.SKIP == {'report.md', 'settled.json'}
    assert fixtures.master_root() == Path(os.environ['HOME']) / '.cache' / 'agent-skills'
    found = fixtures.masters(Path('/m'))
    assert found == {'audit': Path('/m/cc-guide/packets/20261013T113847-audit'),
                     'readme': Path('/m/cc-guide/packets/20261013T121854-files/hooks__README.md'),
                     'precision': Path('/m/scratch/vr102/masters/precision/skills__writing-skills__SKILL.md'),
                     'docs': Path('/m/cc-guide/2.1.296/docs')}


def test_the_audit_copies_leave_out_the_report_and_only_one_gains_listed(tmp_path):
    sources = masters_in(tmp_path / 'masters')
    assert fixtures.build(sources, MANIFEST) == 0
    for name in ('audit-control', 'audit-changed'):
        assert not (fx() / name / 'report.md').exists() and not (fx() / name / 'settled.json').exists()
        for leaf in ('guide.md', 'changelog.md', 'sections.md', 'releases.md', 'blocks.md'):
            assert (fx() / name / leaf).read_bytes() == (sources['audit'] / leaf).read_bytes()
    control, changed = index_of('audit-control'), index_of('audit-changed')
    assert control == AUDIT_INDEX
    assert {k: v for k, v in changed.items() if k != 'listed'} == AUDIT_INDEX
    assert list(changed) == [*list(AUDIT_INDEX)[:list(AUDIT_INDEX).index('releases') + 1], 'listed',
                             *list(AUDIT_INDEX)[list(AUDIT_INDEX).index('releases') + 1:]]
    assert [(e['item'], e['line'], e['sections']) for e in changed['listed']] == [
        ('2.1.300#1284', 1288, ['models.routing']), ('2.1.300#1698', 1702, ['models.routing'])]
    assert not (fx() / 'audit-control' / 'listed.md').exists()


def test_listed_comes_from_the_packets_own_files_and_group_models(tmp_path):
    sources = masters_in(tmp_path / 'masters')
    assert fixtures.build(sources, MANIFEST) == 0
    changed = fx() / 'audit-changed'
    guide = (sources['audit'] / 'guide.md').read_text(encoding='utf-8')
    terms = state.group_terms(state.parse_manifest(MANIFEST), guide)['models']
    want = packets.listed_bullets((sources['audit'] / 'changelog.md').read_text(encoding='utf-8'), terms, guide)
    assert index_of('audit-changed')['listed'] == want
    assert (changed / 'listed.md').read_text(encoding='utf-8') == '\n'.join(packets.listed_lines(want)) + '\n'
    assert 900 not in {e['line'] for e in want}  # the hooks group's term is not a models term


def test_the_readme_copy_gains_an_empty_covered_and_the_rest_are_copies(tmp_path):
    sources = masters_in(tmp_path / 'masters')
    assert fixtures.build(sources, MANIFEST) == 0
    assert index_of('readme') == README_INDEX | {'covered': {}}
    assert not (fx() / 'readme' / 'report.md').exists()
    assert (fx() / 'readme' / 'cited_README.md').read_bytes() == (sources['readme'] / 'cited_README.md').read_bytes()
    assert index_of('precision') == PRECISION_INDEX
    assert (fx() / 'precision' / 'covered' / 'references' / 'report.md').is_file()  # only the top-level report goes
    assert (fx() / 'docs' / 'settings.md').read_bytes() == (sources['docs'] / 'settings.md').read_bytes()
    assert (fx() / 'docs' / 'sub' / 'nested.md').is_file()


def test_the_build_writes_a_shasum_listing_and_prints_the_listed_count(tmp_path, capfd):
    sources = masters_in(tmp_path / 'masters')
    assert fixtures.build(sources, MANIFEST) == 0
    out, err = capfd.readouterr()
    assert out.splitlines()[0] == 'listed items: 2'
    k = common.k_dir()
    files = sorted(p for p in fx().rglob('*') if p.is_file())
    want = ''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(k)}\n' for p in files)
    assert (k / 'fixtures.sha256').read_text(encoding='utf-8') == want
    assert 'fixtures/audit-changed/listed.md' in want
    check = subprocess.run(['shasum', '-a', '256', '-c', 'fixtures.sha256'], cwd=k, capture_output=True, text=True)
    assert check.returncode == 0, check.stdout + check.stderr


@pytest.mark.parametrize('present, missing', [((1702,), 1288), ((1288,), 1702), ((), 1288)])
def test_the_build_fails_when_p11_or_p8_is_not_listed(tmp_path, capfd, present, missing):
    sources = masters_in(tmp_path / 'masters', changelog_text(present))
    assert fixtures.main_with(['build'], sources, MANIFEST) == 1
    out, err = capfd.readouterr()
    assert str(missing) in err
    assert not fx().exists() and not (common.k_dir() / 'fixtures.sha256').exists()
    assert not [p for p in common.k_dir().iterdir() if p.name.startswith('fixtures')]


def test_the_build_refuses_when_fixtures_exist(tmp_path, capfd):
    sources = masters_in(tmp_path / 'masters')
    assert fixtures.build(sources, MANIFEST) == 0
    listing = (common.k_dir() / 'fixtures.sha256').read_bytes()
    write(fx() / 'readme' / 'extra.md', 'x\n')
    assert fixtures.main_with(['build'], sources, MANIFEST) == 1
    assert (fx() / 'readme' / 'extra.md').is_file()
    assert (common.k_dir() / 'fixtures.sha256').read_bytes() == listing
    assert 'exist' in capfd.readouterr().err


def test_the_build_refuses_a_missing_master_and_names_it(tmp_path, capfd):
    sources = masters_in(tmp_path / 'masters')
    sources['docs'] = tmp_path / 'nowhere'
    assert fixtures.main_with(['build'], sources, MANIFEST) == 1
    assert 'docs' in capfd.readouterr().err
    assert not fx().exists()


def test_main_build_reads_the_masters_under_home(tmp_path, monkeypatch, capfd):
    fake_masters(fixtures.masters(fixtures.master_root()))
    monkeypatch.setattr(fixtures, 'manifest_text', lambda: MANIFEST)
    assert fixtures.main(['build']) == 0
    assert {e['line'] for e in index_of('audit-changed')['listed']} == {1288, 1702}
    assert fixtures.main([]) == 2 and fixtures.main(['build', 'x']) == 2


def test_the_manifest_is_5bd78a7s(tmp_path):
    has = subprocess.run(['git', 'cat-file', '-e', '5bd78a7^{commit}'], cwd=common.REPO, capture_output=True)
    if has.returncode != 0:
        pytest.skip('5bd78a7 is not in this clone')
    text = fixtures.manifest_text()
    want = subprocess.run(['git', 'show', '5bd78a7:build/cc_guide/manifest.toml'], cwd=common.REPO,
                          capture_output=True, text=True).stdout
    assert text == want
    assert 'models' in state.parse_manifest(text).groups


def test_no_fixture_output_names_an_arm(tmp_path, capfd):
    good = masters_in(tmp_path / 'good')
    assert fixtures.main_with(['build'], good, MANIFEST) == 0
    assert fixtures.main_with(['build'], good, MANIFEST) == 1  # fixtures exist
    (common.k_dir() / 'fixtures').rename(tmp_path / 'built')
    assert fixtures.main_with(['build'], masters_in(tmp_path / 'p11', changelog_text((1702,))), MANIFEST) == 1
    broken = masters_in(tmp_path / 'broken')
    write(broken['audit'] / 'index.json', '{not json')
    assert fixtures.main_with(['build'], broken, MANIFEST) == 2
    gone = masters_in(tmp_path / 'gone')
    gone['readme'] = tmp_path / 'absent'
    assert fixtures.main_with(['build'], gone, MANIFEST) == 1
    no_log = masters_in(tmp_path / 'nolog')
    (no_log['audit'] / 'changelog.md').unlink()  # the copy's read fails with a path that names an arm
    assert fixtures.main_with(['build'], no_log, MANIFEST) == 2
    out, err = capfd.readouterr()
    assert out.strip() and err.strip()
    assert no_arm_named(out + err), out + err
    assert 'Traceback' not in err and 'fixtures/' not in err

'''Hand-written fixtures for the cc_guide suite. Never copied docs text.

Test modules import what they need; importing `isolated_home` registers that
autouse fixture in the importing module, so no test reaches the real
~/.cache. Fence strings are built from FENCE, FENCE4 and TILDE, so no line of
this file is itself a fence.
'''
import pytest

FENCE = '`' * 3
FENCE4 = '`' * 4


TILDE = '~' * 3


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    '''Point HOME at a scratch directory, so a default cache path can never
    resolve into the real ~/.cache.'''
    home = tmp_path / 'home'
    home.mkdir()
    monkeypatch.setenv('HOME', str(home))
    return home


# An env-vars-style page: the Documentation Index preamble, an intro, a table
# with a repeated, an empty and a pipe-escaping first cell, every fence shape
# R3.1 names, and a repeated heading path.
ENV_PAGE = '\n'.join([
    '> ## Documentation Index',
    '> Fixture page index: https://docs.example.invalid/llms.txt',
    '> A hand-written stand-in for the docs preamble.',
    '',
    '# Environment variables',
    '',
    '> Variables that steer the fixture tool.',
    '',
    'Set them in a [settings file](/docs/en/settings).',
    '',
    '| Variable | Purpose |',
    '| :--- | :--- |',
    '| `ALPHA_ENV` | Turns on alpha. |',
    '| `BETA_ENV` | Turns on beta; see [events](/docs/en/events). |',
    '| `PIPE_ENV` | Accepts `a\\|b`. |',
    '|  | A row with an empty first cell. |',
    '| `ALPHA_ENV` | Repeats a first cell. |',
    '',
    'Text after the table stays in the heading block.',
    '',
    '## Examples',
    '',
    FENCE + 'bash',
    '# a shell comment, not a heading',
    'export ALPHA_ENV=1',
    FENCE,
    '',
    '  ' + FENCE + 'json',
    '  # an indented fence, still code',
    '  ' + FENCE,
    '',
    TILDE,
    '## a tilde fence, not a heading',
    TILDE,
    '',
    FENCE4 + 'markdown',
    FENCE + 'python',
    '## nested, not a heading',
    FENCE,
    FENCE4,
    '',
    '## Examples',
    '',
    'A second Examples heading.',
    '',
])


# A page with no title: a lone ## whose whole body is a table.
TABLE_PAGE = '\n'.join([
    '## Settings',
    '| Key | Value |',
    '|---|---|',
    '| `alpha.mode` | fast |',
    '| `beta.mode` | slow |',
    '',
])


# A platform page: YAML front matter instead of the preamble.
PLATFORM_PAGE = '\n'.join([
    '---',
    'title: Fixture pricing',
    'url: https://platform.example.invalid/docs/en/pricing',
    '---',
    '',
    'Prices for `BETA_ENV` users.',
    '',
    '## Rates',
    '',
    'Rates move with `BetaEvent`.',
    '',
])


# Three releases, newest first as the real changelog lists them. Bullets are
# indented two spaces, as on the real page (checked 2026-10-04).
CHANGELOG_TEXT = '\n'.join([
    '> ## Documentation Index',
    '> Fixture page index: https://docs.example.invalid/llms.txt',
    '',
    '# Fixture changelog',
    '',
    '* A bullet outside every release block.',
    '',
    '<Update label="2.1.902" description="October 1, 2026">',
    '  * Changed how `BETA_ENV` is read',
    '  * Fixed a crash in the fixture tool',
    '</Update>',
    '',
    '<Update label="2.1.901" description="September 20, 2026">',
    '  * Added `ALPHA_ENV` to the alpha tools',
    '</Update>',
    '',
    '<Update label="2.1.900" description="September 1, 2026">',
    '  * First fixture release',
    '</Update>',
    '',
])


LLMS_TEXT = '\n'.join([
    '# Fixture docs',
    '',
    '- [Tools](https://code.claude.com/docs/en/tools.md): The tools page.',
    '- [Events](https://code.claude.com/docs/en/events.md): The events page.',
    '- [Environment variables](https://code.claude.com/docs/en/env-vars.md): Variables.',
    '- [Plugin parts](https://code.claude.com/docs/en/plugins/components.md): A nested slug.',
    '',
])


# The fixture guide's sections, in heading order. Two `Reference ⚠` headings
# sit under different parents, as the real guide's two `Frontmatter reference
# ⚠` headings do.
GUIDE_IDS = ['alpha.overview', 'alpha.reference', 'beta.overview', 'beta.reference']


FIXTURE_STAMP = ('> Checked against the Claude Code docs and changelog through 2.1.900 '
                 'on 2026-09-02; oldest full re-verification 2026-09-02, at 2.1.900.')


def guide_text(stamp: str = FIXTURE_STAMP) -> str:
    '''The fixture guide, its stamp region holding `stamp`. The markers come
    from guide.py, imported here so that blocks.py's tests run without it.'''
    from guide import STAMP_CLOSE, STAMP_OPEN
    return '\n'.join([
        '# Fixture guide',
        '',
        '**A guide for the fixture tool.**',
        '',
        STAMP_OPEN,
        stamp,
        STAMP_CLOSE,
        '',
        '> First verified at 2.1.900.',
        '',
        '## 1. Alpha',
        '<!-- cc: alpha.overview -->',
        '',
        'Alpha uses `ALPHA_TOOL`, `if` and `true`.',
        '',
        '### Reference ⚠',
        '<!-- cc: alpha.reference -->',
        '',
        'Set `ALPHA_ENV`; `` a `tick` inside `` stays one span.',
        '',
        FENCE + 'bash',
        '## not a heading inside a fence',
        'echo `NOT_A_TERM`',
        FENCE,
        '',
        '## 2. Beta',
        '<!-- cc: beta.overview -->',
        '',
        '| Setting | Meaning |',
        '|---|---|',
        '| `BETA_ENV` | on |',
        '',
        FENCE + 'json',
        '{"beta": true}',
        FENCE,
        '',
        '### Reference ⚠',
        '<!-- cc: beta.reference -->',
        '',
        '`BetaEvent` fires.',
        '',
    ])


MANIFEST_TOML = '\n'.join([
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
    '[groups.alpha]',
    "sections = ['alpha.overview', 'alpha.reference']",
    "all = ['tools']",
    "terms = ['env-vars']",
    '',
    '[groups.beta]',
    "sections = ['beta.overview', 'beta.reference']",
    "all = ['events']",
    "terms = ['env-vars', 'platform:pricing']",
    '',
    '[[exclusion]]',
    "page = 'whats-new/*'",
    "reason = 'Duplicates the changelog.'",
    '',
])


def write_tree(root, files: dict) -> None:
    '''Write {relative path: text} under root.'''
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')


def git(repo, *args: str) -> str:
    '''git in a fixture repo, with an identity and none of the caller's GIT_ variables.'''
    import os
    import subprocess
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    return subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                           '-c', 'commit.gpgsign=false', '-c', 'init.defaultBranch=main', *args],
                          cwd=repo, env=env, capture_output=True, text=True, check=True).stdout


def fixture_repo(root, files: dict):
    '''A git repo at root holding files, committed on main.'''
    root.mkdir(parents=True, exist_ok=True)
    write_tree(root, files)
    git(root, 'init', '-q')
    git(root, 'add', '-A')
    git(root, 'commit', '-qm', 'fixture')
    return root


TOOLS_PAGE = '\n'.join([
    '> ## Documentation Index',
    '> Fixture page index: https://docs.example.invalid/llms.txt',
    '',
    '# Tools',
    '',
    'The `ALPHA_TOOL` runs alpha jobs.',
    '',
    '## Options',
    '',
    '| Option | Effect |',
    '|---|---|',
    '| `--fast` | Runs fast. |',
    '',
])


EVENTS_PAGE = '\n'.join([
    '# Events',
    '',
    '`BetaEvent` fires on beta.',
    '',
    '## Payload',
    '',
    'The payload carries `BETA_ENV`.',
    '',
])


# The fixture docs directory, file name -> text, named as the cache names them.
DOCS = {
    'tools.md': TOOLS_PAGE,
    'events.md': EVENTS_PAGE,
    'env-vars.md': ENV_PAGE,
    'platform_pricing.md': PLATFORM_PAGE,
    'changelog.md': CHANGELOG_TEXT,
    'llms.txt': LLMS_TEXT,
}


# The fixture baseline: every section checked and audited at 2.1.900 on
# 2026-09-02, so 2.1.901 (2026-09-20) and 2.1.902 (2026-10-01) are untriaged.
FIXTURE_RELEASE, FIXTURE_DAY = '2.1.900', '2026-09-02'


FIXTURE_CHANGED = {'alpha.overview': '2.1.900', 'alpha.reference': '2.1.899',
                   'beta.overview': '2.1.900', 'beta.reference': '2.1.900'}


@pytest.fixture
def docs_dir(tmp_path):
    '''The fixture docs as a local directory, named as the cache names them.'''
    folder = tmp_path / 'docs'
    write_tree(folder, DOCS)
    return folder


def fixture_state(folder) -> dict:
    '''The baseline init builds for the fixture guide over a docs directory.'''
    import baseline
    import state
    return baseline.init(state.parse_manifest(MANIFEST_TOML), guide_text(), folder,
                         FIXTURE_RELEASE, FIXTURE_DAY, FIXTURE_CHANGED)


GUIDE_PATH = 'specs/guides/claude-code-customization-guide.md'


def drift_repo(root, folder):
    '''A committed fixture repo: the guide, manifest.toml, and the baseline
    init builds over `folder`.'''
    import state
    return fixture_repo(root, {GUIDE_PATH: guide_text(), state.MANIFEST: MANIFEST_TOML,
                               state.BASELINE: state.dump_baseline(fixture_state(folder))})


def prime_cache(cache, folder, head: str = '2.1.902') -> None:
    '''A cache whose latest/ holds folder's files, as a live check leaves it.'''
    import json
    import state
    write_tree(state.latest_docs(cache), {p.name: p.read_text(encoding='utf-8') for p in folder.iterdir()})
    state.fetch_record(cache).write_text(json.dumps({'fetched_at': '2026-10-04T12:00:00+00:00',
                                                      'changelog_head': head}) + '\n')

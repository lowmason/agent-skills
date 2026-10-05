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

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

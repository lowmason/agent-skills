"""Tests for scan.sh, the tech-debt sweep — run from this directory.

cd skills/tech-debt/scripts && uv run --with pytest python -m pytest -q

scan.sh is bash and greps for planted signals, so each test builds a small git
project that carries them, runs the script as a subprocess, and reads one
section of its report. The script picks rg when it is on PATH and grep/find
otherwise, so every test runs under both: the grep arm hides rg by giving the
script a PATH of symlinks to just the tools it calls.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCAN = Path(__file__).resolve().parent / 'scan.sh'
BASH = shutil.which('bash') or '/bin/bash'
GREP_ARM_TOOLS = ('git', 'grep', 'find', 'sort', 'basename', 'dirname', 'cat', 'tr')

SEEDS = 'Magic seeds'
ARTIFACTS = 'Committed model artifacts'
MIGRATION = 'Migration debt'
SCRATCH = 'Scratch / scratchpad notebooks'
UNTESTED = 'Source modules with no obvious test'

# No `__main__` guard here: a guard at the start of a line, even inside this string,
# makes check_frontmatter.py treat this test file as a runnable script.
MARIMO_NOTEBOOK = '''\
import marimo

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)
'''

# Mentions marimo, but its app line is not top-level, so it is a module.
MARIMO_MENTION = '''\
import marimo


def build():
    app = marimo.App()
    return app
'''

# What an installed marimo tutorial looks like to the scan: a top-level app line, plus a line for
# each of the grep sections. No `__main__` guard, for the same reason as above.
VENDORED_TUTORIAL = (
    MARIMO_NOTEBOOK
    + '''
import pandas as pd

np.random.seed(7)
stamp = datetime.now()
path = "/Users/someone/data.csv"
merged = left.join(right, on="key")
token = "abc123"
value = compute()  # type: ignore
# TODO tidy this up
'''
)

# Each prefix puts the same installed package under one of the four directory names the grep arm prunes.
VENDORED_PREFIXES = [
    '.venv/lib/python3.13/site-packages',
    'venv/lib/python3.13/site-packages',
    'vendor/site-packages',
    'web/node_modules',
]

SIGNAL_SOURCE = """\
import jax
import numpy as np
import torch
from jax import random

key_a = jax.random.PRNGKey(42)
key_b = jax.random.key(42)
key_c = random.key(42)
torch.manual_seed(42)
np.random.seed(7)
key_ok = jax.random.key(seed_from_name)
torch.manual_seed(seed_from_name)
"""

IMPORT_SOURCE = """\
import pandas as pd
import polars as pl
import numpyro
from pandas import DataFrame
import pymc as pm
from pymc import Model
import pymc3
import pandasql
import pymc_extras


def late():
    import pandas
"""


def git(root, *args):
    subprocess.run(
        ['git', *args],
        cwd=root,
        check=True,
        capture_output=True,
        env={**os.environ, 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1'},
    )


@pytest.fixture
def project(tmp_path):
    """A git project with a planted signal of each kind, plus controls that must stay quiet."""
    root = tmp_path / 'project'
    (root / 'src').mkdir(parents=True)
    (root / 'weights').mkdir()
    (root / 'src' / 'signals.py').write_text(SIGNAL_SOURCE)
    (root / 'src' / 'frames.py').write_text(IMPORT_SOURCE)
    for name in ('a.ckpt', 'b.pt', 'c.pth', 'd.safetensors', 'e.pkl', 'f.joblib'):
        (root / 'weights' / name).write_bytes(b'\x00binary')
    for name in ('notes.txt', 'table.parquet', 'weights.pty'):
        (root / 'weights' / name).write_bytes(b'ok')
    git(root.parent, 'init', '-q', str(root))
    git(root, 'add', '-A')
    (root / 'weights' / 'local_only.pt').write_bytes(b'\x00untracked')  # never committed
    return root


@pytest.fixture
def notebook_project(tmp_path):
    """A git project with marimo notebooks inside and outside the root notebooks/, plus controls."""
    root = tmp_path / 'nbproject'
    files = {
        'explore_root.py': MARIMO_NOTEBOOK,
        'analysis/notebooks/nested_nb.py': MARIMO_NOTEBOOK.replace('App(width="medium")', 'App()'),
        'scratchpad_nb.py': MARIMO_NOTEBOOK,
        'notebooks/report_nb.py': MARIMO_NOTEBOOK,
        'notebooks/scratchpad_record.py': MARIMO_NOTEBOOK,
        'notebooks/q3/deep dive.py': MARIMO_NOTEBOOK,
        'notebooks/nb_helpers.py': 'def share(x):\n    return x\n',
        'src/uses_marimo.py': MARIMO_MENTION,
        'src/model_core.py': 'def fit():\n    return 1\n',
        'scratchpad.ipynb': '{}',
        'notebooks/Untitled1.ipynb': '{}',
        'notebooks/analysis_record.ipynb': '{}',
    }
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    git(root.parent, 'init', '-q', str(root))
    git(root, 'add', '-A')
    return root


def scan(root, arm, tmp_path):
    """Run scan.sh on `root` and return its report split into {section title: [lines]}."""
    if arm == 'rg':
        if not shutil.which('rg'):
            pytest.skip('rg is not installed, so only the grep arm can run')
        path = os.environ['PATH']
    else:
        shim = tmp_path / 'grep-arm-bin'
        shim.mkdir()
        for tool in GREP_ARM_TOOLS:
            found = shutil.which(tool)
            if found:
                (shim / tool).symlink_to(found)
        assert not (shim / 'rg').exists()
        path = str(shim)
    result = subprocess.run(
        [BASH, str(SCAN), str(root)],
        capture_output=True,
        text=True,
        env={
            'PATH': path,
            'HOME': str(tmp_path),
            'GIT_CEILING_DIRECTORIES': str(tmp_path),
            'GIT_CONFIG_GLOBAL': '/dev/null',
            'GIT_CONFIG_NOSYSTEM': '1',
        },
    )
    assert result.returncode == 0, result.stderr
    assert 'command not found' not in result.stderr, result.stderr
    sections, current = {}, None
    for line in result.stdout.splitlines():
        if line.startswith('========== '):
            current = line.strip('= ')
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return sections


def section(sections, prefix):
    matches = [lines for title, lines in sections.items() if title.startswith(prefix)]
    assert len(matches) == 1, f'expected one section starting {prefix!r}, got {list(sections)}'
    return '\n'.join(matches[0])


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_seed_battery_flags_every_magic_seed_idiom(project, tmp_path, arm):
    """PRNGKey(42) was the only JAX idiom caught: the new-style jax.random.key(42), the same call
    through `from jax import random`, and torch.manual_seed(42) all passed silently."""
    hits = section(scan(project, arm, tmp_path), SEEDS)
    for line in (
        'jax.random.PRNGKey(42)',
        'jax.random.key(42)',
        'random.key(42)',
        'torch.manual_seed(42)',
        'np.random.seed(7)',
    ):
        assert line in hits, f'{line} was not flagged:\n{hits}'
    assert 'seed_from_name' not in hits  # a derived seed is the fix, not debt


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_committed_model_artifacts_are_listed(project, tmp_path, arm):
    hits = section(scan(project, arm, tmp_path), ARTIFACTS)
    for name in ('a.ckpt', 'b.pt', 'c.pth', 'd.safetensors', 'e.pkl', 'f.joblib'):
        assert f'weights/{name}' in hits, f'{name} was not listed:\n{hits}'
    assert 'notes.txt' not in hits and 'table.parquet' not in hits
    assert 'weights.pty' not in hits  # the suffix is matched whole


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_only_committed_artifacts_count(project, tmp_path, arm):
    """The section asks what is committed, so an untracked local checkpoint is not debt."""
    assert 'local_only.pt' not in section(scan(project, arm, tmp_path), ARTIFACTS)


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_artifacts_outside_git_are_found_by_walking_the_tree(tmp_path, arm):
    root = tmp_path / 'plain'
    root.mkdir()
    (root / 'model.safetensors').write_bytes(b'\x00')
    assert 'model.safetensors' in section(scan(root, arm, tmp_path), ARTIFACTS)


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_migration_debt_flags_pandas_and_pymc_imports(project, tmp_path, arm):
    """The skill names a Polars / NumPyro stack, but nothing flagged an import of either library
    it is migrating away from."""
    hits = section(scan(project, arm, tmp_path), MIGRATION)
    for line in (
        'import pandas as pd',
        'from pandas import DataFrame',
        'import pymc as pm',
        'from pymc import Model',
        'import pymc3',
        '    import pandas',
    ):
        assert line in hits, f'{line!r} was not flagged:\n{hits}'
    for line in ('import polars', 'import numpyro', 'import pandasql', 'import pymc_extras'):
        assert line not in hits, f'{line!r} should not be flagged:\n{hits}'


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_marimo_notebook_outside_notebooks_dir_is_scratch(notebook_project, tmp_path, arm):
    hits = section(scan(notebook_project, arm, tmp_path), SCRATCH)
    assert 'explore_root.py' in hits, hits
    assert 'analysis/notebooks/nested_nb.py' in hits, hits  # only the root notebooks/ holds deliverables


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_marimo_notebook_under_notebooks_dir_is_not_scratch(notebook_project, tmp_path, arm):
    """A notebook in the root notebooks/ is a deliverable, even when the name rule's `scratchpad` matches it."""
    hits = section(scan(notebook_project, arm, tmp_path), SCRATCH)
    for name in ('report_nb.py', 'scratchpad_record.py', 'deep dive.py', 'nb_helpers.py'):
        assert name not in hits, f'{name} was listed:\n{hits}'


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_marimo_notebooks_are_not_untested_modules(notebook_project, tmp_path, arm):
    hits = section(scan(notebook_project, arm, tmp_path), UNTESTED)
    notebooks = ('explore_root.py', 'nested_nb.py', 'scratchpad_nb.py', 'report_nb.py', 'deep dive.py',
                 'scratchpad_record.py')
    for name in notebooks:
        assert name not in hits, f'{name} is a notebook, not a module:\n{hits}'
    for name in ('src/model_core.py', 'notebooks/nb_helpers.py'):  # a module stays listed wherever it sits
        assert name in hits, f'{name} was not listed:\n{hits}'


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_notebook_ipynb_name_rule_is_unchanged(notebook_project, tmp_path, arm):
    hits = section(scan(notebook_project, arm, tmp_path), SCRATCH)
    assert 'scratchpad.ipynb' in hits, hits
    assert 'notebooks/Untitled1.ipynb' in hits, hits  # the name rule holds in notebooks/ too
    assert 'analysis_record.ipynb' not in hits, hits


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_marimo_mention_without_app_line_is_not_a_notebook(notebook_project, tmp_path, arm):
    sections = scan(notebook_project, arm, tmp_path)
    assert 'uses_marimo.py' not in section(sections, SCRATCH)
    assert 'src/uses_marimo.py' in section(sections, UNTESTED)


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_scratch_lists_each_notebook_once(notebook_project, tmp_path, arm):
    """scratchpad_nb.py matches the name rule and the marimo rule. The section lists it once."""
    hits = section(scan(notebook_project, arm, tmp_path), SCRATCH)
    assert hits.count('scratchpad_nb.py') == 1, hits


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_untested_modules_unchanged_without_notebooks(project, tmp_path, arm):
    """With no notebook in the repo, an empty notebook list must not filter out every module."""
    hits = section(scan(project, arm, tmp_path), UNTESTED)
    assert 'src/signals.py' in hits and 'src/frames.py' in hits, hits


@pytest.mark.parametrize('prefix', VENDORED_PREFIXES)
def test_grep_arm_skips_installed_packages(tmp_path, prefix):
    """rg skips an in-repo .venv because uv writes a .gitignore inside it. The grep arm has no such
    help, so it must prune .venv, venv, site-packages and node_modules itself: an installed marimo
    tutorial is a notebook with a hit for most scans, and it listed in every section."""
    root = tmp_path / 'vendored'
    (root / 'src').mkdir(parents=True)
    (root / 'src' / 'signals.py').write_text(SIGNAL_SOURCE)
    (root / 'explore_root.py').write_text(MARIMO_NOTEBOOK)
    git(root.parent, 'init', '-q', str(root))
    git(root, 'add', '-A')
    # The installed package stays untracked, as a real environment does.
    tutorials = root / prefix / 'marimo' / '_tutorials'
    tutorials.mkdir(parents=True)
    (tutorials / 'intro.py').write_text(VENDORED_TUTORIAL)
    (tutorials / 'intro_v2.py').write_text('def share(x):\n    return x\n')
    (tutorials / 'README.md').write_text('')
    (tutorials / 'pyproject.toml').write_text('description = ""\n')

    sections = scan(root, 'grep', tmp_path)

    for title, lines in sections.items():
        for line in lines:
            assert 'marimo/_tutorials' not in line, f'{prefix} listed in {title!r}:\n{line}'
    # Controls: pruning must not blank the scan of the project itself.
    assert 'explore_root.py' in section(sections, SCRATCH)
    assert 'src/signals.py' in section(sections, SEEDS)

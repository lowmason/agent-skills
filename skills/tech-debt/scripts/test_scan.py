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

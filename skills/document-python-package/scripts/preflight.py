#!/usr/bin/env python3
# /// script
# requires-python = '>=3.11'
# dependencies = []
# ///
'''Preflight for the document-python-package skill. Run it from a package root:

    uv run <this-skill-dir>/scripts/preflight.py

It reads the great-docs version that uv.lock pins and checks it against the
tested range. It finds where great-docs.yml sits and which Quarto is on PATH.
Then it fetches Posit's official Great Docs skills from the matching release
tag into a version-keyed cache. It prints one `key: value` line per fact and
a last `next:` line that names the next step: pin, init or ready. It exits 0
when the package is ready for that step, and 1 on a stop, where `next:` gives
the reason. --remote replaces the GitHub URL, so the tests can pass a local
repository.
'''
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from datetime import datetime, timezone
from pathlib import Path

REMOTE = 'https://github.com/posit-dev/great-docs'
PACKAGE = 'great-docs'
# The tested range: 0.17.0 included, 0.18.0 excluded. Only a final release
# (X.Y.Z, digits only) can fall inside it.
LOWEST = (0, 17, 0)
FIRST_EXCLUDED = (0, 18, 0)
RANGE = '>=0.17.0,<0.18'
FINAL_RELEASE_RE = re.compile(r'(\d+)\.(\d+)\.(\d+)')
CONFIG = 'great-docs.yml'
CONFIG_PATHS = {'root': CONFIG, 'docs': f'docs/{CONFIG}'}
QUARTO_INSTALL = 'https://quarto.org/docs/get-started/'
QUARTO_TIMEOUT_S = 60
GIT_TIMEOUT_S = 60
NONE = 'none'
STOP = 'stop: '


class FetchError(Exception):
    '''The official skills could not be fetched. The message is git's error.'''


def locked_version(root: Path) -> str | None:
    '''The great-docs version that root/uv.lock pins, or None.'''
    lock = root / 'uv.lock'
    if not lock.is_file():
        return None
    with lock.open('rb') as f:
        packages = tomllib.load(f).get('package', [])
    return next((p.get('version') for p in packages if p.get('name') == PACKAGE), None)


def in_range(version: str) -> bool:
    '''Whether version is a final release inside the tested range.'''
    m = FINAL_RELEASE_RE.fullmatch(version)
    return m is not None and LOWEST <= tuple(map(int, m.groups())) < FIRST_EXCLUDED


def config_layout(root: Path) -> tuple[str, list[str]]:
    '''The config layout (root, docs, both or none) and the config paths found.'''
    found = [name for name, rel in CONFIG_PATHS.items() if (root / rel).is_file()]
    if len(found) == len(CONFIG_PATHS):
        layout = 'both'
    else:
        layout = found[0] if found else NONE
    return layout, [CONFIG_PATHS[name] for name in found]


def quarto_version() -> str | None:
    '''The version that `quarto --version` prints, or None when Quarto is missing.'''
    quarto = shutil.which('quarto')
    if quarto is None:
        return None
    try:
        proc = subprocess.run([quarto, '--version'], capture_output=True, text=True,
                              timeout=QUARTO_TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired):
        return None
    words = proc.stdout.split()
    return words[0] if proc.returncode == 0 and words else None


def cache_root() -> Path:
    '''${XDG_CACHE_HOME:-~/.cache}/agent-skills/great-docs'''
    base = os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache'
    return Path(base) / 'agent-skills' / PACKAGE


def _git(*args: str) -> str:
    # GIT_TERMINAL_PROMPT=0: a bad URL fails at once instead of asking for a password.
    # The timeout turns a stalled connection into a stop instead of a hang.
    env = {**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
    try:
        proc = subprocess.run(['git', *args], capture_output=True, text=True, env=env,
                              timeout=GIT_TIMEOUT_S)
    except FileNotFoundError:
        raise FetchError('git is not installed') from None
    except subprocess.TimeoutExpired:
        raise FetchError(f'git timed out after {GIT_TIMEOUT_S} s') from None
    if proc.returncode != 0:
        raise FetchError(' '.join(proc.stderr.split()) or f'git exited {proc.returncode}')
    return proc.stdout.strip()


def fetch_skills(version: str, remote: str) -> Path:
    '''The cached skills/ folder of tag v<version>. A cache folder with a SOURCE
    file is complete and is reused. Any other is deleted and fetched again, in a
    temporary folder beside it that is renamed into place.'''
    parent = cache_root()
    dest = parent / version
    if (dest / 'SOURCE').is_file():
        return dest / 'skills'
    if dest.exists():
        shutil.rmtree(dest)
    parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f'.{version}-', dir=parent))
    tag = f'v{version}'
    try:
        repo, out = staging / 'repo', staging / 'out'
        _git('clone', '--quiet', '--depth', '1', '--filter=blob:none', '--sparse',
             '--branch', tag, remote, str(repo))
        _git('-C', str(repo), 'sparse-checkout', 'set', 'skills')
        if not (repo / 'skills').is_dir():
            raise FetchError(f'tag {tag} has no skills/ folder')
        commit = _git('-C', str(repo), 'rev-parse', 'HEAD')
        out.mkdir()
        shutil.copytree(repo / 'skills', out / 'skills')
        fetched = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        (out / 'SOURCE').write_text(f'tag: {tag}\ncommit: {commit}\nfetched: {fetched}\n')
        out.rename(dest)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    return dest / 'skills'


def next_step(layout: str, configs: list[str], quarto: str | None, version: str | None,
              remote: str) -> tuple[str, Path | None]:
    '''The `next:` value and the cached skills folder. Stops come first: an
    unsupported layout, then a missing Quarto. Then a missing pin, a version
    outside the range and a failed fetch, in that order.'''
    if layout not in ('root', NONE):
        return (f'{STOP}config layout {layout} ({", ".join(configs)}) is not supported; '
                f'great-docs 0.17.x reads {CONFIG} at the project root', None)
    if quarto is None:
        return f'{STOP}quarto is missing; install it from {QUARTO_INSTALL}', None
    if version is None:
        return 'pin', None
    if not in_range(version):
        return (f'{STOP}great-docs {version} is outside {RANGE}; '
                'pin it back into the range and run uv lock', None)
    try:
        skills = fetch_skills(version, remote)
    except FetchError as exc:
        return f'{STOP}fetching the official skills failed: {exc}', None
    return ('init' if layout == NONE else 'ready'), skills


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Preflight for the document-python-package skill.')
    parser.add_argument('--remote', default=REMOTE, help='the great-docs git repository to fetch from')
    args = parser.parse_args(argv)
    root = Path.cwd()
    version = locked_version(root)
    layout, configs = config_layout(root)
    quarto = quarto_version()
    step, skills = next_step(layout, configs, quarto, version, args.remote)
    facts = {
        'great-docs': version or NONE,
        'range': RANGE,
        'in-range': NONE if version is None else ('yes' if in_range(version) else 'no'),
        'layout': layout,
        'config': ', '.join(configs) or NONE,
        'quarto': quarto or 'missing',
        'skills': str(skills) if skills else NONE,
        'next': step,
    }
    for key, value in facts.items():
        print(f'{key}: {value}')
    return 1 if step.startswith(STOP) else 0


if __name__ == '__main__':
    sys.exit(main())

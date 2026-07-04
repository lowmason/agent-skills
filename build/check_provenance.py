#!/usr/bin/env python3
'''Provenance lint: every skill directory is attributed in NOTICE, and no
binary document assets (.pdf/.epub/.docx) are git-tracked.

Run: uv run --python 3.13 python build/check_provenance.py
Exit 0 if clean; exit 1 with one line per violation.
'''
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BINARY_SUFFIXES = ('.pdf', '.epub', '.docx')


def skill_dirs() -> list[str]:
    return sorted(
        d.name for d in (REPO / 'skills').iterdir()
        if d.is_dir() and (d / 'SKILL.md').exists()
    )


def find_binary_assets(tracked: list[str]) -> list[str]:
    return [f for f in tracked if f.lower().endswith(BINARY_SUFFIXES)]


def main() -> int:
    errs: list[str] = []
    notice = (REPO / 'NOTICE').read_text()
    for name in skill_dirs():
        if f'{name}/' not in notice:
            errs.append(f'NOTICE: missing attribution entry for skill {name}/')
    tracked = subprocess.run(
        ['git', 'ls-files'], cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    for f in find_binary_assets(tracked):
        errs.append(f'binary document asset tracked: {f}')
    for e in errs:
        print(e)
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())

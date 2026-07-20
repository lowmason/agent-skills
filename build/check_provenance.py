#!/usr/bin/env python3
'''Provenance lint: every skill directory is attributed in NOTICE, and no
binary document assets (.pdf/.epub/.docx) are git-tracked.

Run: uv run --python 3.13 python build/check_provenance.py
Exit 0 if clean; exit 1 with one line per violation.
'''
from __future__ import annotations

import re
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


def missing_attributions(names: list[str], notice: str) -> list[str]:
    return [
        name for name in names
        if not re.search(rf'^\s*{re.escape(name)}/(\s|$)', notice, re.M)
    ]


def notice_originals(notice: str) -> list[str]:
    '''Skill names NOTICE lists under "original works by Lowell Mason" —
    the indented `name/` block directly under that heading, up to the
    next blank-line-terminated paragraph.
    '''
    m = re.search(
        r'original works by Lowell Mason, MIT licensed:\n(.*?)\n\n', notice, re.S,
    )
    if not m:
        return []
    return re.findall(r'^\s*([a-z0-9][a-z0-9-]*)/', m.group(1), re.M)


def claude_md_originals(claude_md: str) -> list[str]:
    '''Skill names CLAUDE.md's "- **Lowell's originals**" bullet claims.

    The bullet is one line: a lead-in (which itself may contain backticks,
    e.g. `` `LICENSE` ``), a colon, the backtick-quoted skill list, then a
    period and trailing prose (e.g. a parenthetical count note) that must
    be tolerated rather than choked on.
    '''
    m = re.search(r"^- \*\*Lowell's originals\*\*.*$", claude_md, re.M)
    if not m:
        return []
    after_colon = m.group(0).split(':', 1)[-1]
    list_part = after_colon.split('.', 1)[0]
    return re.findall(r'`([^`]+)`', list_part)


def originals_mismatch(
    claude_md_names: list[str], notice_names: list[str],
) -> tuple[list[str], list[str]]:
    '''(missing, extra): missing = in NOTICE but absent from CLAUDE.md;
    extra = in CLAUDE.md but absent from NOTICE. Order-independent.
    '''
    claude_set, notice_set = set(claude_md_names), set(notice_names)
    return sorted(notice_set - claude_set), sorted(claude_set - notice_set)


def main() -> int:
    errs: list[str] = []
    notice = (REPO / 'NOTICE').read_text()
    for name in missing_attributions(skill_dirs(), notice):
        errs.append(f'NOTICE: missing attribution entry for skill {name}/')
    claude_md = (REPO / 'CLAUDE.md').read_text()
    missing, extra = originals_mismatch(claude_md_originals(claude_md), notice_originals(notice))
    if missing:
        errs.append(
            "CLAUDE.md: 'Lowell's originals' list is missing skills NOTICE lists: "
            + ', '.join(missing)
        )
    if extra:
        errs.append(
            "CLAUDE.md: 'Lowell's originals' list includes skills NOTICE does not: "
            + ', '.join(extra)
        )
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

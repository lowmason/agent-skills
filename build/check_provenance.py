#!/usr/bin/env python3
'''Provenance lint: every skill directory is attributed in NOTICE and carries
byte-identical copies of the root license files that apply to it
(BUNDLED_LICENSES), and no binary document assets (.pdf/.epub/.docx) are
git-tracked.

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
PLAIN_LICENSE = 'LICENSE'
# Root license file -> the skills that carry a byte-identical copy of it under
# the same name, so a single-skill install keeps the notice MIT requires
# (portability R4). PLAIN_LICENSE goes to every skill and is not listed.
BUNDLED_LICENSES: dict[str, tuple[str, ...]] = {
    'LICENSE-superpowers': (
        'brainstorming', 'dispatching-parallel-agents', 'executing-plans',
        'finishing-a-development-branch', 'receiving-code-review',
        'requesting-code-review', 'subagent-driven-development',
        'systematic-debugging', 'test-driven-development', 'using-git-worktrees',
        'verification-before-completion', 'writing-plans', 'writing-skills',
    ),
    # NOTICE records adapted Mancuso Lab content in these two; tech-debt took
    # only an idea from it and carries no copy.
    'LICENSE-coding-skills': ('bayesian-workflow', 'clean-code'),
    'LICENSE-causal-design-sources': ('recommend-causal-design',),
    'LICENSE-andorra': ('bayesian-workflow',),
    'LICENSE-write-with-asd-ste100-sources': ('write-with-asd-ste100',),
}


def skill_dirs() -> list[str]:
    return sorted(
        d.name for d in (REPO / 'skills').iterdir()
        if d.is_dir() and (d / 'SKILL.md').exists()
    )


def bundled_license_violations(repo: Path, skills: list[str],
                               table: dict[str, tuple[str, ...]]) -> list[str]:
    '''Every skill holds a regular-file copy of PLAIN_LICENSE and of each root
    license file the table maps to it, byte-identical to the root file, and no
    other LICENSE* file; every root LICENSE* file is mapped (portability R4.2).'''
    errs: list[str] = []
    roots = sorted(p.name for p in repo.glob('LICENSE*') if p.is_file())
    errs += [f'{name}: root license file is mapped to no skill in BUNDLED_LICENSES'
             for name in roots if name != PLAIN_LICENSE and name not in table]
    for name, owners in sorted(table.items()):
        if name not in roots:
            errs.append(f'BUNDLED_LICENSES: {name} is not a root license file')
        errs += [f'BUNDLED_LICENSES: {name} names {skill}, which is not a skill directory'
                 for skill in owners if skill not in skills]
    for skill in skills:
        d = repo / 'skills' / skill
        wanted = {PLAIN_LICENSE} | {name for name, owners in table.items()
                                    if skill in owners and name in roots}
        for name in sorted(wanted):
            copy, rel = d / name, f'skills/{skill}/{name}'
            if copy.is_symlink():
                errs.append(f'{rel}: a symlink, which install.py --copy refuses; '
                            f'copy the root {name} as a regular file')
            elif not copy.is_file():
                errs.append(f'{rel}: missing; copy the root {name} here as a regular file')
            elif copy.read_bytes() != (repo / name).read_bytes():
                errs.append(f'{rel}: differs from the root {name}; copy it again')
        errs += [f'skills/{skill}/{p.name}: not mapped to {skill} in BUNDLED_LICENSES'
                 for p in sorted(d.glob('LICENSE*')) if p.name not in wanted]
    return errs


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
    errs += bundled_license_violations(REPO, skill_dirs(), BUNDLED_LICENSES)
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

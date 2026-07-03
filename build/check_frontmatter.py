#!/usr/bin/env python3
'''Frontmatter and bundled-path lint for every skill in the repo (Gate A pattern).

Per <skill>/SKILL.md: the frontmatter must parse as YAML (catches unquoted-
scalar breakage), name must equal the directory name (<=64 chars, lowercase
letters/digits/hyphens), description must be present and <=1024 chars (Agent
Skills spec cap), keys must be spec-valid, and every relative markdown-link
target plus every backticked references/ or scripts/ path must exist.

Run: uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
Exit 0 if clean; exit 1 with one line per violation.
'''
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
ALLOWED_KEYS = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'when_to_use'}
NAME_RE = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
LINK_RE = re.compile(r'\]\(([^)#\s]+)\)')
TICK_PATH_RE = re.compile(r'`((?:references|scripts)/[A-Za-z0-9._/-]+)`')


def check_skill(skill_dir: Path) -> list[str]:
    errs: list[str] = []
    sk = skill_dir / 'SKILL.md'
    text = sk.read_text()
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not m:
        return [f'{sk}: no frontmatter block']
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as exc:
        return [f'{sk}: frontmatter is not valid YAML ({type(exc).__name__})']
    if not isinstance(fm, dict):
        return [f'{sk}: frontmatter is not a mapping']

    name = fm.get('name', '')
    if name != skill_dir.name:
        errs.append(f'{sk}: name {name!r} does not match directory {skill_dir.name!r}')
    if len(name) > 64 or not NAME_RE.match(name or ''):
        errs.append(f'{sk}: name must be <=64 chars, lowercase letters/digits/hyphens')
    desc = (fm.get('description') or '').strip()
    if not desc:
        errs.append(f'{sk}: missing description')
    elif len(desc) > 1024:
        errs.append(f'{sk}: description is {len(desc)} chars (spec cap 1024)')
    for key in fm:
        if key not in ALLOWED_KEYS:
            errs.append(f'{sk}: unknown frontmatter key {key!r}')

    # Scan links/paths in prose only — fenced code blocks hold teaching
    # examples and template snippets whose paths are not real files.
    prose = re.sub(r'^```.*?^`{3,}\s*$', '', text, flags=re.S | re.M)
    for rel in LINK_RE.findall(prose) + TICK_PATH_RE.findall(prose):
        if rel.startswith(('http://', 'https://', 'mailto:')):
            continue
        if not (skill_dir / rel).exists() and not (REPO / rel.lstrip('./')).exists():
            errs.append(f'{sk}: referenced path does not exist: {rel}')
    return errs


def main() -> int:
    errs: list[str] = []
    for d in sorted(REPO.iterdir()):
        if d.is_dir() and (d / 'SKILL.md').exists():
            errs += check_skill(d)
    for e in errs:
        print(e)
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())

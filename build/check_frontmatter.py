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

import importlib.util
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
ALLOWED_KEYS = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'when_to_use', 'model', 'effort'}
NAME_RE = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
KNOWN_AGENT_TOOLS = {
    'Read', 'Grep', 'Glob', 'Bash', 'Write', 'Edit', 'WebFetch', 'WebSearch',
}
GUARD_PATH = REPO / 'hooks' / 'readonly-agent-guard.py'
# Load-bearing marker, not a label: an agents/*.md carrying this heading is
# asserted to be in the guard's roster, and vice versa. debugger.md and
# docs-writer.md use a plain '## Contract' because theirs are not read-only.
READONLY_HEADING = '## Read-only contract'
# Anchored links (`](path.md#frag)`) are intentionally skipped, not validated —
# the fragment part isn't checked, only the path before it (see LINK_RE below,
# which already excludes '#' from the captured group).
LINK_RE = re.compile(r'\]\(([^)#\s]+)\)')
TICK_PATH_RE = re.compile(r'`((?:references|scripts)/[A-Za-z0-9._/-]+)`')
FENCE_OPEN_RE = re.compile(r'^(`{3,})')


def strip_fenced_blocks(text: str) -> str:
    '''Remove fenced code blocks, honoring CommonMark fence-matching rules.

    A fence closes only on a line of the same fence character whose run
    length is >= the opener's (and nothing else on the line but whitespace).
    A naive non-greedy regex closes on the FIRST ``` it sees, which
    desynchronizes on nested fences (e.g. a ````markdown fence wrapping a
    literal ```python fence) — real prose gets stripped and fence-internal
    content gets scanned instead.
    '''
    kept: list[str] = []
    open_len: int | None = None
    for line in text.split('\n'):
        if open_len is None:
            m = FENCE_OPEN_RE.match(line)
            if m:
                open_len = len(m.group(1))
                continue
            kept.append(line)
        else:
            stripped = line.strip()
            if stripped.startswith('`' * open_len) and set(stripped) == {'`'}:
                open_len = None
    return '\n'.join(kept)


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
    prose = strip_fenced_blocks(text)
    for rel in LINK_RE.findall(prose) + TICK_PATH_RE.findall(prose):
        if rel.startswith(('http://', 'https://', 'mailto:')):
            continue
        if not (skill_dir / rel).exists() and not (REPO / rel.lstrip('./')).exists():
            errs.append(f'{sk}: referenced path does not exist: {rel}')
    return errs


def _parse_frontmatter(md: Path) -> tuple[dict | None, list[str]]:
    text = md.read_text()
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not m:
        return None, [f'{md}: no frontmatter block']
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as exc:
        return None, [f'{md}: frontmatter is not valid YAML ({type(exc).__name__})']
    if not isinstance(fm, dict):
        return None, [f'{md}: frontmatter is not a mapping']
    return fm, []


def check_agent_file(md: Path) -> list[str]:
    fm, errs = _parse_frontmatter(md)
    if fm is None:
        return errs
    # Case-insensitive: repo filenames stay lowercase, but agents/explore.md
    # must carry name "Explore" — Claude Code resolves agent types by the
    # frontmatter name alone, case-sensitively, and only the capitalized
    # name shadows the built-in Explore agent (probed on 2.1.219).
    if str(fm.get('name') or '').lower() != md.stem.lower():
        errs.append(f'{md}: name {fm.get("name")!r} does not match filename {md.stem!r}')
    if not (fm.get('description') or '').strip():
        errs.append(f'{md}: missing description')
    tools = fm.get('tools')
    if tools is not None:
        unknown = [t.strip() for t in str(tools).split(',') if t.strip() not in KNOWN_AGENT_TOOLS]
        if unknown:
            errs.append(f'{md}: unknown tools {unknown}')
    return errs


def check_command_file(md: Path) -> list[str]:
    fm, errs = _parse_frontmatter(md)
    if fm is None:
        return errs
    if not (fm.get('description') or '').strip():
        errs.append(f'{md}: missing description')
    # Commands stay off the skill-listing budget only because they opt out of
    # auto-invocation; guard the key that carries that decision. `is not True`
    # rejects a missing key, `false`, and a quoted 'true' (a string, which
    # disables nothing) alike.
    if fm.get('disable-model-invocation') is not True:
        errs.append(f'{md}: disable-model-invocation must be the YAML boolean true')
    return errs


def load_readonly_roster(guard_path: Path | None = None) -> frozenset[str]:
    '''Import READONLY_AGENTS from the hook script.

    The file is hyphenated (hook-script convention) so it is not importable by
    name; exec'ing it is safe because its main() sits behind __main__.
    '''
    path = guard_path or GUARD_PATH
    spec = importlib.util.spec_from_file_location('readonly_agent_guard', path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return frozenset(module.READONLY_AGENTS)


def check_readonly_roster(agents_dir: Path | None = None,
                          roster: frozenset[str] | None = None) -> list[str]:
    '''Assert the guard's roster and the read-only agent files agree, both ways.

    Forward: a sixth read-only agent must not ship unguarded. Reverse: a roster
    entry must not outlive the agent it names. This is what makes the hook's
    hardcoded roster safe — drift fails here, at the commit that introduces it.
    '''
    d = agents_dir or (REPO / 'agents')
    if roster is None:
        try:
            roster = load_readonly_roster()
        except (FileNotFoundError, OSError, SyntaxError, AttributeError) as exc:
            return [f'{GUARD_PATH}: cannot load READONLY_AGENTS '
                    f'({type(exc).__name__}: {exc})']
    errs: list[str] = []
    marked: dict[str, Path] = {}
    for md in sorted(d.glob('*.md')):
        if not any(ln.strip() == READONLY_HEADING for ln in md.read_text().splitlines()):
            continue
        fm, _ = _parse_frontmatter(md)
        marked[str((fm or {}).get('name') or md.stem)] = md
    for name, md in sorted(marked.items()):
        if name not in roster:
            errs.append(f'{md}: carries "{READONLY_HEADING}" but {name!r} is not in '
                        f'READONLY_AGENTS ({GUARD_PATH.name})')
    for name in sorted(roster):
        if name not in marked:
            errs.append(f'{GUARD_PATH}: READONLY_AGENTS entry {name!r} has no '
                        f'agents/*.md carrying "{READONLY_HEADING}"')
    return errs


def main() -> int:
    errs: list[str] = []
    for d in sorted((REPO / 'skills').iterdir()):
        if d.is_dir() and (d / 'SKILL.md').exists():
            errs += check_skill(d)
    for md in sorted((REPO / 'agents').glob('*.md')):
        errs += check_agent_file(md)
    for md in sorted((REPO / 'commands').glob('*.md')):
        errs += check_command_file(md)
    errs += check_readonly_roster()
    for e in errs:
        print(e)
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())

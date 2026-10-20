#!/usr/bin/env python3
# cc-guide: skills.frontmatter commands.overview subagents.frontmatter subagents.tools subagents.models @2.1.219
'''Frontmatter and bundled-path lint for every skill in the repo (Gate A pattern).

Per <skill>/SKILL.md:
- the frontmatter parses as YAML (catches unquoted-scalar breakage);
- name equals the directory name (<=64 chars, lowercase letters/digits/hyphens);
- description is present and <=1024 chars (the Agent Skills spec cap);
- every key is an Agent Skills spec key (SPEC_KEYS) or a host extension this
  repo allows (HOST_KEYS);
- license is a non-empty string (repo policy, beyond the spec);
- name and description contain no < or >; metadata maps strings to strings;
  compatibility is a string of 1-500 characters;
- context is in CONTEXT_VALUES, and model is not haiku or a claude-haiku-* ID
  (not portable across providers);
- every relative markdown-link target and every backticked references/ or
  scripts/ path exists.

Run: uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
Exit 0 if clean; exit 1 with one line per violation.
'''
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import yaml

from fences import strip_fenced_blocks

REPO = Path(__file__).resolve().parent.parent
# The Agent Skills spec's fields (agentskills.io/specification), which every
# runtime that implements the spec accepts.
SPEC_KEYS = frozenset({'name', 'description', 'license', 'compatibility', 'metadata',
                       'allowed-tools'})
# Claude Code extensions this repo allows beside them. Gemini CLI and Codex load
# a skill that carries one; claude.ai uploads and spec-only validators reject
# them, which is what --strict checks.
HOST_KEYS = frozenset({'when_to_use', 'model', 'effort', 'context',
                       'disable-model-invocation', 'agent'})
# The spec caps compatibility at 500 characters.
COMPATIBILITY_CAP = 500
ANGLE_BRACKET_RE = re.compile(r'[<>]')
# `fork` is the only value Claude Code documents for `context` (run the skill in
# an isolated subagent). Any other value is a typo that silently no-ops at
# runtime, so it fails here instead — widen this set if the spec grows one.
CONTEXT_VALUES = frozenset({'fork'})
# A skill or command `model:` that is a Haiku: the bare `haiku` alias or any
# claude-haiku-* model ID, matched whole and case-insensitively. Auto mode drops
# Haiku 4.5 and keeps the session model, and the `haiku` alias means Haiku 5.5 on
# the Anthropic API but 4.5 on the other providers, so such a pin would apply on
# one and be ignored on another; it fails here instead. The ban is deliberately
# broader than what auto mode drops (owner, 2026-10-12, the register's
# no-haiku-skill-model). agents/*.md are not checked — a subagent's Haiku pin does
# apply. See specs/completed/skill-model-pin-removal.md.
AUTO_MODE_DROPPED_MODEL_RE = re.compile(r'haiku|claude-haiku-.+', re.IGNORECASE)
# One number, two different reasons — which is why the two messages below name
# different ones. For a SKILL.md it is the Agent Skills standard's cap
# (agentskills.io; see specs/completed/audit_1_3_26.md, which also records that
# Claude Code itself enforces no 1024 hard cap). No standard governs an
# agents/*.md, but every agent description loads into the Agent-tool listing, so
# agents are held to the same budget by analogy, not by spec.
DESCRIPTION_CAP = 1024
NAME_RE = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
KNOWN_AGENT_TOOLS = {
    'Read', 'Grep', 'Glob', 'Bash', 'Write', 'Edit', 'WebFetch', 'WebSearch',
}
# Beyond the built-ins above, a tools entry may be an MCP tool (mcp__<server>
# or mcp__<server>__<tool>) or Agent, bare or naming the spawnable agent types
# as `Agent(worker, researcher)` (the guide's subagents.frontmatter).
AGENT_RESTRICTION_RE = re.compile(r'Agent(\([^()]*\))?')
MCP_TOOL_PREFIX = 'mcp__'
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


def split_tools(tools: object) -> list[str]:
    '''A tools value's entries. A YAML list is taken entry by entry; anything
    else is read as a comma-separated string, split only on commas outside
    parentheses, so `Agent(worker, researcher)` stays one entry.'''
    if isinstance(tools, list):
        return [str(t).strip() for t in tools if str(t).strip()]
    tools = str(tools)
    entries, depth, start = [], 0, 0
    for i, ch in enumerate(tools):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth = max(depth - 1, 0)
        elif ch == ',' and depth == 0:
            entries.append(tools[start:i])
            start = i + 1
    entries.append(tools[start:])
    return [e.strip() for e in entries if e.strip()]


def known_agent_tool(tool: str) -> bool:
    '''A built-in tool, an MCP tool, or Agent with or without its type list.'''
    return (tool in KNOWN_AGENT_TOOLS or tool.startswith(MCP_TOOL_PREFIX)
            or AGENT_RESTRICTION_RE.fullmatch(tool) is not None)


def _check_model_pin(md: Path, fm: dict) -> list[str]:
    '''Fail a skill or command `model:` that is a Haiku (AUTO_MODE_DROPPED_MODEL_RE).'''
    model = fm.get('model')
    if model is None or not AUTO_MODE_DROPPED_MODEL_RE.fullmatch(str(model)):
        return []
    return [f'{md}: model {model!r} is not portable: auto mode drops Haiku 4.5 and '
            'keeps the session model, and the haiku alias means Haiku 5.5 on the '
            'Anthropic API but 4.5 on other providers, so the pin applies on one '
            'and is ignored on another; put cheap work on a model-pinned subagent '
            'instead (specs/completed/skill-model-pin-removal.md)']


def _check_license(sk: Path, fm: dict) -> list[str]:
    '''Every SKILL.md names its license (portability R1.4: repo policy, beyond
    the spec), so a single-skill install still says how the skill is licensed.'''
    lic = fm.get('license')
    if isinstance(lic, str) and lic.strip():
        return []
    return [f'{sk}: license is required, a non-empty string (repo policy, beyond the Agent Skills spec)']


def _check_value_shapes(sk: Path, fm: dict) -> list[str]:
    '''The value shapes the Agent Skills spec defines: no < or > in name or
    description, metadata as a string-to-string map, compatibility as a string
    of 1 to COMPATIBILITY_CAP characters.'''
    errs = [f'{sk}: {key} contains < or >' for key in ('name', 'description')
            if ANGLE_BRACKET_RE.search(str(fm.get(key) or ''))]
    meta = fm.get('metadata', {})
    if not (isinstance(meta, dict)
            and all(isinstance(k, str) and isinstance(v, str) for k, v in meta.items())):
        errs.append(f'{sk}: metadata must map strings to strings (quote a value such as version: "1.0")')
    if 'compatibility' in fm:
        compat = fm['compatibility']
        if not (isinstance(compat, str) and 1 <= len(compat.strip()) <= COMPATIBILITY_CAP):
            errs.append(f'{sk}: compatibility must be a string of 1-{COMPATIBILITY_CAP} characters')
    return errs


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
    elif len(desc) > DESCRIPTION_CAP:
        errs.append(
            f'{sk}: description is {len(desc)} chars (spec cap {DESCRIPTION_CAP})')
    ctx = fm.get('context')
    if ctx is not None and ctx not in CONTEXT_VALUES:
        errs.append(f'{sk}: context must be one of {sorted(CONTEXT_VALUES)}, got {ctx!r}')
    errs += _check_model_pin(sk, fm)
    errs += _check_license(sk, fm)
    errs += _check_value_shapes(sk, fm)
    for key in fm:
        if key not in SPEC_KEYS | HOST_KEYS:
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
    # Every agent description loads into the Agent-tool listing, so agents are
    # on the same budget check_skill enforces on a SKILL.md — by analogy, not
    # by spec, so the message says 'listing budget' where check_skill says
    # 'spec cap'.
    desc = (fm.get('description') or '').strip()
    if not desc:
        errs.append(f'{md}: missing description')
    elif len(desc) > DESCRIPTION_CAP:
        errs.append(
            f'{md}: description is {len(desc)} chars (listing budget {DESCRIPTION_CAP})')
    tools = fm.get('tools')
    if tools is not None:
        unknown = [t for t in split_tools(tools) if not known_agent_tool(t)]
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
    errs += _check_model_pin(md, fm)
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

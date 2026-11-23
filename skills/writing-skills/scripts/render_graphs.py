#!/usr/bin/env python3
# /// script
# requires-python = '>=3.11'
# dependencies = []
# ///
'''Render the graphviz diagrams in a skill's Markdown files to SVG files.

Usage:
    uv run render_graphs.py <skill-dir> <out-dir>            # Each diagram separately
    uv run render_graphs.py <skill-dir> <out-dir> --combine  # All diagrams in one SVG

It reads every Markdown file under <skill-dir> and renders each ```dot block that has
a graph header. It skips a block with no `digraph` or `graph` header, such as a code
fragment shown as a bad example. An anonymous graph gets the name `graph_<k>`. Each SVG
is named `<file stem>-<graph name>.svg`, with a number added when a name repeats.

<out-dir> must lie outside the skill folder, because everything in that folder ships
with the skill. Needs Graphviz's `dot` on PATH.

Exit status: 0 when every block rendered (or none was found), 1 when a block failed
(the other blocks still render), 2 for a usage error or a refusal.

A Python port of upstream superpowers' `render-graphs.js`. The port reads every Markdown
file, skips fragments, exits non-zero on a failed block and writes outside the skill.
'''

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_REFUSED = 2

DOT_HINT = '\n'.join(
    [
        'error: graphviz (dot) not found. Install with:',
        '  brew install graphviz    # macOS',
        '  apt install graphviz     # Linux',
    ]
)

_FENCE = re.compile(
    r'^[ \t]*```dot[ \t]*\n(.*?)^[ \t]*```[ \t]*$', re.MULTILINE | re.DOTALL
)
_HEADER = re.compile(
    r'(?:strict\s+)?(?:di)?graph\b(?:\s+(?P<name>\w+|"(?:[^"\\]|\\.)*"))?\s*\{'
)
_RANKDIR = re.compile(r'^[ \t]*rankdir[ \t]*=[ \t]*"?\w+"?[ \t]*;?[ \t]*$', re.MULTILINE)
_UNSAFE_IN_FILE_NAME = re.compile(r'[^\w.-]+')


class Block(NamedTuple):
    source: Path  # relative to the skill folder
    name: str
    text: str


class RenderError(Exception):
    '''dot failed on one input. The message is the first line of its stderr.'''


def dot_blocks(markdown: str) -> list[str]:
    '''The text of each ```dot fence in the Markdown, in order.'''
    return [match.group(1).strip() for match in _FENCE.finditer(markdown)]


def _header(block: str) -> re.Match[str] | None:
    '''Match the graph header at the first line that is not blank and not a comment.'''
    offset = 0
    for line in block.splitlines(keepends=True):
        stripped = line.strip()
        if stripped and not stripped.startswith(('//', '#')):
            return _HEADER.match(block, offset)
        offset += len(line)
    return None


def graph_name(block: str) -> str | None:
    '''The graph's name, '' for an anonymous graph, None when the block has no header.'''
    match = _header(block)
    if match is None:
        return None
    name = match.group('name') or ''
    return name[1:-1] if name.startswith('"') else name


def find_blocks(skill_dir: Path) -> list[Block]:
    '''Every dot block with a graph header in the skill's Markdown files.'''
    blocks: list[Block] = []
    for path in sorted(skill_dir.rglob('*.md')):
        if not path.is_file():
            continue
        source = path.relative_to(skill_dir)
        for text in dot_blocks(path.read_text(encoding='utf-8')):
            name = graph_name(text)
            if name is None:
                continue
            blocks.append(Block(source, name or f'graph_{len(blocks) + 1}', text))
    return blocks


def output_names(blocks: list[Block]) -> list[str]:
    '''One SVG file name for each block. No two names are the same.'''
    taken: set[str] = set()
    names = []
    for block in blocks:
        base = _UNSAFE_IN_FILE_NAME.sub('_', f'{block.source.stem}-{block.name}')
        name, count = base, 1
        while name.casefold() in taken:
            count += 1
            name = f'{base}-{count}'
        taken.add(name.casefold())
        names.append(f'{name}.svg')
    return names


def _body(block: Block) -> str:
    '''The statements between the braces, less any rankdir line.'''
    match = _header(block.text)
    if match is None:
        return ''
    body = block.text[match.end() :]
    end = body.rfind('}')
    if end != -1:
        body = body[:end]
    return _RANKDIR.sub('', body).strip()


def combine(blocks: list[Block], skill_name: str) -> str:
    '''One digraph that holds each block as a labelled cluster.'''
    clusters = []
    for i, block in enumerate(blocks):
        body = '\n'.join(f'    {line}' for line in _body(block).splitlines())
        clusters.append(
            f'  subgraph cluster_{i} {{\n    label="{block.name}";\n{body}\n  }}'
        )
    return (
        f'digraph "{skill_name}_combined" {{\n'
        '  rankdir=TB;\n  compound=true;\n  newrank=true;\n\n'
        + '\n\n'.join(clusters)
        + '\n}\n'
    )


def render_svg(dot_text: str) -> str:
    result = subprocess.run(
        ['dot', '-Tsvg'],
        input=dot_text,
        capture_output=True,
        text=True,
        encoding='utf-8',
    )
    if result.returncode != 0:
        lines = result.stderr.strip().splitlines()
        raise RenderError(lines[0] if lines else f'dot exited {result.returncode}')
    return result.stdout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='render_graphs.py',
        description="Render the graphviz diagrams in a skill's Markdown files to SVG.",
    )
    parser.add_argument('skill_dir', type=Path, help='the skill folder (holds SKILL.md)')
    parser.add_argument(
        'out_dir', type=Path, help='where the SVG files go; outside the skill folder'
    )
    parser.add_argument(
        '--combine', action='store_true', help='render all diagrams into one SVG'
    )
    try:
        args = parser.parse_args(argv)
    except SystemExit as exit_:
        return int(exit_.code)

    skill = args.skill_dir.resolve()
    out = args.out_dir.resolve()
    if not (skill / 'SKILL.md').is_file():
        print(f'error: {skill / "SKILL.md"} not found', file=sys.stderr)
        return EXIT_REFUSED
    if out.is_relative_to(skill):
        print(
            f'refusing: {args.out_dir} is inside the skill folder; '
            'everything there ships with the skill',
            file=sys.stderr,
        )
        return EXIT_REFUSED
    if shutil.which('dot') is None:
        print(DOT_HINT, file=sys.stderr)
        return EXIT_REFUSED

    blocks = find_blocks(skill)
    if not blocks:
        print(f'No dot blocks with a graph header found in {skill}')
        return EXIT_OK
    try:
        out.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f'error: cannot create {args.out_dir}: {exc}', file=sys.stderr)
        return EXIT_REFUSED

    print(f'Found {len(blocks)} diagram(s) in {skill.name}/')
    failures = 0
    if args.combine:
        skill_name = skill.name.replace('-', '_')
        source = combine(blocks, skill_name)
        (out / f'{skill_name}_combined.dot').write_text(source, encoding='utf-8')
        try:
            svg = render_svg(source)
        except RenderError as exc:
            print(f'failed: combined diagram: {exc}', file=sys.stderr)
            failures += 1
        else:
            (out / f'{skill_name}_combined.svg').write_text(svg, encoding='utf-8')
            print(f'rendered: {skill_name}_combined.svg')
    else:
        for block, name in zip(blocks, output_names(blocks)):
            try:
                svg = render_svg(block.text)
            except RenderError as exc:
                print(
                    f'failed: {block.source.as_posix()}: {block.name}: {exc}',
                    file=sys.stderr,
                )
                failures += 1
                continue
            (out / name).write_text(svg, encoding='utf-8')
            print(f'rendered: {name}')

    print(f'Output: {args.out_dir}/')
    return EXIT_FAILED if failures else EXIT_OK


if __name__ == '__main__':
    sys.exit(main())

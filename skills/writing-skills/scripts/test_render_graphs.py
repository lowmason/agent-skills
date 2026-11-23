'''Tests for render_graphs.py. Run from this directory (bare imports).

cd skills/writing-skills/scripts && uv run --with pytest python -m pytest -q

Stdlib only. The tests that render need graphviz `dot` on PATH and skip without it.
'''

import shutil
from pathlib import Path

import pytest

from render_graphs import Block, find_blocks, graph_name, main, output_names

needs_dot = pytest.mark.skipif(shutil.which('dot') is None, reason='needs graphviz dot')

FRAGMENT = 'step1 [label="import fs"];\nstep2 [label="read file"];'


def fence(*graphs):
    '''Markdown that holds each graph text in its own dot fence.'''
    return '# Notes\n\n' + '\n'.join(f'```dot\n{g}\n```\n' for g in graphs)


def make_skill(tmp_path, files=None, name='my-skill'):
    '''A skill folder under tmp_path with a SKILL.md, plus the given files.'''
    skill = tmp_path / name
    skill.mkdir()
    (skill / 'SKILL.md').write_text('# Skill\n')
    for rel, text in (files or {}).items():
        path = skill / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return skill


def top_and_deep_skill(tmp_path):
    return make_skill(
        tmp_path,
        {
            'SKILL.md': fence(FRAGMENT, 'digraph top {}'),
            'references/deep.md': fence('digraph deep {}'),
            'conventions.dot': 'digraph style {}',
        },
    )


def test_graph_name_reads_each_header_form():
    assert graph_name('digraph flow {\n a -> b\n}') == 'flow'
    assert graph_name('graph g {\n a -- b\n}') == 'g'
    assert graph_name('strict digraph s {') == 's'
    assert graph_name('digraph {\n a -> b\n}') == ''
    assert graph_name('// note\ndigraph after {') == 'after'
    assert graph_name('step1 [label="import fs"];\nstep2 [label="read file"];') is None


def test_find_blocks_reads_every_markdown_file_and_skips_fragments(tmp_path):
    skill = top_and_deep_skill(tmp_path)
    assert [(b.source.as_posix(), b.name) for b in find_blocks(skill)] == [
        ('SKILL.md', 'top'),
        ('references/deep.md', 'deep'),
    ]


def test_output_names_never_repeat():
    blocks = [
        Block(Path('a.md'), 'when_to_use', 'digraph when_to_use {}'),
        Block(Path('b.md'), 'when_to_use', 'digraph when_to_use {}'),
        Block(Path('b.md'), 'when_to_use', 'digraph when_to_use {}'),
    ]
    assert output_names(blocks) == [
        'a-when_to_use.svg',
        'b-when_to_use.svg',
        'b-when_to_use-2.svg',
    ]


def test_refuses_out_dir_inside_skill(tmp_path):
    skill = make_skill(tmp_path, {'SKILL.md': fence('digraph top {}')})
    assert main([str(skill), str(skill / 'diagrams')]) == 2
    assert not (skill / 'diagrams').exists()
    assert main([str(skill), str(skill)]) == 2


def test_missing_dot_exits_2(tmp_path, monkeypatch, capsys):
    skill = make_skill(tmp_path, {'SKILL.md': fence('digraph top {}')})
    out = tmp_path / 'out'
    monkeypatch.setattr(shutil, 'which', lambda name: None)
    assert main([str(skill), str(out)]) == 2
    assert not out.exists()
    assert 'graphviz' in capsys.readouterr().err


def test_missing_skill_md_exits_2(tmp_path):
    folder = tmp_path / 'no-skill'
    folder.mkdir()
    assert main([str(folder), str(tmp_path / 'out')]) == 2


@needs_dot
def test_renders_each_block_as_svg(tmp_path):
    skill = top_and_deep_skill(tmp_path)
    out = tmp_path / 'out'
    assert main([str(skill), str(out)]) == 0
    for name in ('SKILL-top.svg', 'deep-deep.svg'):
        assert '<svg' in (out / name).read_text()


@needs_dot
def test_failed_block_exits_1_and_keeps_others(tmp_path, capsys):
    skill = make_skill(
        tmp_path, {'SKILL.md': fence('digraph good { a -> b }', 'digraph bad { a -> }')}
    )
    out = tmp_path / 'out'
    assert main([str(skill), str(out)]) == 1
    assert (out / 'SKILL-good.svg').exists()
    assert not (out / 'SKILL-bad.svg').exists()
    assert 'bad' in capsys.readouterr().err


@needs_dot
def test_same_graph_name_in_two_files_writes_two_svgs(tmp_path):
    skill = make_skill(
        tmp_path,
        {
            'a.md': fence('digraph when_to_use { x -> y }'),
            'b.md': fence('digraph when_to_use { x -> y }'),
        },
    )
    out = tmp_path / 'out'
    assert main([str(skill), str(out)]) == 0
    assert (out / 'a-when_to_use.svg').exists()
    assert (out / 'b-when_to_use.svg').exists()


@needs_dot
def test_anonymous_graph_renders_under_a_generated_name(tmp_path):
    skill = make_skill(
        tmp_path, {'SKILL.md': fence('// note\ndigraph { a -> b }')}
    )
    out = tmp_path / 'out'
    assert main([str(skill), str(out)]) == 0
    svgs = list(out.glob('*.svg'))
    assert len(svgs) == 1
    assert 'graph_1' in svgs[0].name


@needs_dot
def test_combine_writes_one_svg_and_its_dot_source(tmp_path):
    skill = make_skill(
        tmp_path,
        {
            'SKILL.md': fence('digraph one { a -> b }'),
            'references/two.md': fence('digraph two { c -> d }'),
        },
    )
    out = tmp_path / 'out'
    assert main([str(skill), str(out), '--combine']) == 0
    assert sorted(p.name for p in out.iterdir()) == [
        'my_skill_combined.dot',
        'my_skill_combined.svg',
    ]


@needs_dot
def test_renders_writing_skills_own_chart(tmp_path):
    out = tmp_path / 'out'
    assert main([str(Path(__file__).resolve().parents[1]), str(out)]) == 0
    names = [p.name for p in out.iterdir()]
    assert 'flowcharts-when_flowchart.svg' in names
    assert not [n for n in names if n.startswith('SKILL-')]

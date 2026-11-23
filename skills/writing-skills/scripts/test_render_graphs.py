'''Tests for render_graphs.py. Run from this directory (bare imports).

cd skills/writing-skills/scripts && uv run --with pytest python -m pytest -q

Stdlib only. The tests that render need graphviz `dot` on PATH and skip without it.
'''

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import render_graphs
from render_graphs import (
    Block,
    RenderError,
    combine,
    dot_blocks,
    find_blocks,
    graph_name,
    main,
    output_names,
    render_svg,
)

needs_dot = pytest.mark.skipif(shutil.which('dot') is None, reason='needs graphviz dot')

FRAGMENT = 'step1 [label="import fs"];\nstep2 [label="read file"];'
SCRIPT = Path(render_graphs.__file__)


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


# Extra tests from the mutant step. The tests above are the plan's, unchanged.


@pytest.fixture
def no_dot(monkeypatch):
    monkeypatch.setattr(shutil, 'which', lambda name: None)


@pytest.fixture
def fake_dot(monkeypatch):
    '''dot is on PATH as far as main() can tell. Use it only where no block renders.'''
    monkeypatch.setattr(shutil, 'which', lambda name: '/fake/bin/dot')


def blocks_of(*pairs):
    '''Blocks from (file name, graph name) pairs.'''
    return [Block(Path(f), n, f'digraph {n} {{}}') for f, n in pairs]


def test_dot_blocks_returns_each_dot_fence_in_order():
    markdown = (
        '```bash\necho hi\n```\n\n'
        '```dot\ndigraph a {}\n```\n\ntext\n\n'
        '```dot\ndigraph b {\n  x -> y\n}\n```\n'
        '```dot\nnever closed\n'
    )
    assert dot_blocks(markdown) == ['digraph a {}', 'digraph b {\n  x -> y\n}']


def test_graph_name_skips_blank_lines_and_hash_comments():
    assert graph_name('# note\n\n// more\ndigraph after {') == 'after'


def test_graph_name_removes_quotes_from_a_quoted_name():
    assert graph_name('digraph "my graph" {\n a -> b\n}') == 'my graph'
    assert graph_name('strict graph "g" {') == 'g'


def test_graph_name_reads_a_header_split_over_two_lines():
    assert graph_name('digraph flow\n{\n a -> b\n}') == 'flow'


def test_graph_name_reads_an_indented_header_after_a_comment():
    assert graph_name('// note\n  digraph after {\n    a -> b\n  }') == 'after'


def test_find_blocks_reads_a_dot_fence_indented_in_a_list_item(tmp_path):
    skill = make_skill(
        tmp_path,
        {
            'SKILL.md': (
                '- item\n'
                '  ```dot\n'
                '  // note\n'
                '  digraph nested {\n'
                '    a -> b\n'
                '  }\n'
                '  ```\n'
            )
        },
    )
    assert [b.name for b in find_blocks(skill)] == ['nested']


def test_find_blocks_orders_files_by_relative_path(tmp_path, monkeypatch):
    skill = make_skill(
        tmp_path,
        {
            'z.md': fence('digraph z {}'),
            'm.md': fence('digraph m {}'),
            'a/y.md': fence('digraph y {}'),
        },
    )
    real_rglob = Path.rglob
    # The file system may list files in any order. Force the wrong order.
    monkeypatch.setattr(
        Path, 'rglob', lambda self, pattern: iter(sorted(real_rglob(self, pattern), reverse=True))
    )
    assert [b.source.as_posix() for b in find_blocks(skill)] == ['a/y.md', 'm.md', 'z.md']


def test_find_blocks_ignores_a_folder_named_like_a_markdown_file(tmp_path):
    skill = make_skill(
        tmp_path, {'SKILL.md': fence('digraph top {}'), 'notes.md/inside.md': fence('digraph in {}')}
    )
    assert [(b.source.as_posix(), b.name) for b in find_blocks(skill)] == [
        ('SKILL.md', 'top'),
        ('notes.md/inside.md', 'in'),
    ]


def test_anonymous_graphs_are_numbered_among_the_blocks_kept(tmp_path):
    skill = make_skill(
        tmp_path,
        {
            'SKILL.md': fence(
                FRAGMENT, 'digraph { a -> b }', 'digraph x {}', 'digraph { c -> d }'
            ),
            'b.md': fence('digraph { e -> f }'),
        },
    )
    assert [b.name for b in find_blocks(skill)] == ['graph_1', 'x', 'graph_3', 'graph_4']


def test_output_names_number_a_third_repeat_and_a_clash_with_a_suffix():
    assert output_names(blocks_of(('a.md', 'x'), ('a.md', 'x'), ('a.md', 'x'))) == [
        'a-x.svg',
        'a-x-2.svg',
        'a-x-3.svg',
    ]
    assert output_names(blocks_of(('a.md', 'x'), ('a.md', 'x'), ('a.md', 'x-2'))) == [
        'a-x.svg',
        'a-x-2.svg',
        'a-x-2-2.svg',
    ]


def test_output_names_differ_by_more_than_letter_case():
    assert output_names(blocks_of(('a.md', 'Flow'), ('a.md', 'flow'))) == [
        'a-Flow.svg',
        'a-flow-2.svg',
    ]


def test_output_names_keep_each_name_inside_the_out_dir():
    [name] = output_names(blocks_of(('a.md', '../my graph/x')))
    assert '/' not in name
    assert ' ' not in name


def test_combine_wraps_each_block_in_a_labelled_cluster_and_drops_rankdir():
    text = combine(
        [
            Block(Path('a.md'), 'one', '// note\ndigraph one {\n  rankdir=LR;\n  a -> b;\n}'),
            Block(Path('a.md'), 'two', 'digraph two {\n  rankdir = "TB"\n  c -> d;\n}'),
        ],
        'my_skill',
    )
    assert text.startswith('digraph "my_skill_combined" {')
    assert 'subgraph cluster_0 {' in text
    assert 'subgraph cluster_1 {' in text
    assert 'label="one";' in text
    assert 'label="two";' in text
    assert 'a -> b;' in text
    assert 'c -> d;' in text
    assert 'rankdir=LR' not in text
    assert 'rankdir = "TB"' not in text
    assert text.count('rankdir') == 1  # the one at the top level
    assert 'note' not in text


def test_combine_keeps_a_subgraph_inside_a_block():
    block = Block(
        Path('a.md'), 'one', 'digraph one {\n  subgraph s { a -> b }\n  c -> d\n}'
    )
    text = combine([block], 'k')
    assert 'subgraph s { a -> b }' in text
    assert 'c -> d' in text
    assert text.rstrip().endswith('}')
    assert text.count('{') == text.count('}')


def test_render_svg_reports_only_the_first_stderr_line(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, 1, stdout='', stderr='first\nsecond\n')

    monkeypatch.setattr(subprocess, 'run', fake_run)
    with pytest.raises(RenderError, match='^first$'):
        render_svg('digraph {}')


def test_render_svg_names_the_exit_status_when_dot_prints_nothing(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, 3, stdout='', stderr='')

    monkeypatch.setattr(subprocess, 'run', fake_run)
    with pytest.raises(RenderError, match='3'):
        render_svg('digraph {}')


def test_usage_error_exits_2(tmp_path, capsys):
    skill = make_skill(tmp_path)
    assert main([]) == 2
    assert main([str(skill)]) == 2
    assert 'usage' in capsys.readouterr().err.lower()


def test_exits_0_when_no_block_has_a_graph_header(tmp_path, fake_dot, capsys):
    plain = make_skill(tmp_path, name='plain')
    fragments = make_skill(tmp_path, {'SKILL.md': fence(FRAGMENT)}, name='fragments')
    for skill in (plain, fragments):
        assert main([str(skill), str(tmp_path / 'out')]) == 0
        assert 'No dot blocks' in capsys.readouterr().out


def test_refusal_names_the_out_dir_and_the_reason(tmp_path, no_dot, capsys):
    skill = make_skill(tmp_path)
    inside = skill / 'a' / '..' / 'diagrams'
    assert main([str(skill), str(inside)]) == 2
    err = capsys.readouterr().err
    assert 'refusing' in err
    assert 'ships with the skill' in err
    assert 'graphviz' not in err


def test_refuses_a_relative_out_dir_that_resolves_inside_the_skill(
    tmp_path, no_dot, monkeypatch, capsys
):
    skill = make_skill(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert main(['my-skill', 'my-skill/diagrams']) == 2
    assert 'refusing' in capsys.readouterr().err
    monkeypatch.chdir(skill)
    assert main(['.', 'diagrams']) == 2
    assert 'refusing' in capsys.readouterr().err
    assert not (skill / 'diagrams').exists()


def test_a_missing_skill_md_is_reported_before_the_out_dir_is_judged(tmp_path, no_dot, capsys):
    folder = tmp_path / 'no-skill'
    folder.mkdir()
    assert main([str(folder), str(folder / 'diagrams')]) == 2
    err = capsys.readouterr().err
    assert 'SKILL.md' in err
    assert 'refusing' not in err
    assert not (folder / 'diagrams').exists()


def test_a_sibling_folder_that_shares_the_skill_name_prefix_is_outside(tmp_path, fake_dot):
    skill = make_skill(tmp_path)
    assert main([str(skill), str(tmp_path / 'my-skill-diagrams')]) == 0


def test_an_out_dir_that_cannot_be_made_exits_2(tmp_path, fake_dot, capsys):
    skill = make_skill(tmp_path, {'SKILL.md': fence('digraph top {}')})
    blocker = tmp_path / 'a-file'
    blocker.write_text('x')
    assert main([str(skill), str(blocker / 'out')]) == 2
    assert 'cannot create' in capsys.readouterr().err


def test_the_script_runs_as_a_program():
    run = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
    assert run.returncode == 2
    assert 'usage' in run.stderr.lower()


@needs_dot
def test_failure_line_names_the_file_the_graph_and_the_dot_message(tmp_path, capsys):
    skill = make_skill(tmp_path, {'refs/x.md': fence('digraph bad { a -> }')})
    assert main([str(skill), str(tmp_path / 'out')]) == 1
    err = capsys.readouterr().err
    assert 'failed: refs/x.md: bad: Error' in err


@needs_dot
def test_failed_block_does_not_stop_the_blocks_after_it(tmp_path):
    skill = make_skill(
        tmp_path, {'SKILL.md': fence('digraph bad { a -> }', 'digraph good { a -> b }')}
    )
    out = tmp_path / 'out'
    assert main([str(skill), str(out)]) == 1
    assert (out / 'SKILL-good.svg').exists()
    assert not (out / 'SKILL-bad.svg').exists()


@needs_dot
def test_combine_writes_the_combined_source_beside_the_svg(tmp_path):
    skill = make_skill(
        tmp_path,
        {'SKILL.md': fence('digraph one {\n rankdir=LR\n subgraph s { a -> b }\n}')},
        name='105-my-skill',
    )
    out = tmp_path / 'out'
    assert main([str(skill), str(out), '--combine']) == 0
    source = (out / '105_my_skill_combined.dot').read_text()
    assert source.startswith('digraph "105_my_skill_combined" {')
    assert 'subgraph cluster_0' in source
    assert '<svg' in (out / '105_my_skill_combined.svg').read_text()


@needs_dot
def test_combine_that_fails_exits_1_and_keeps_the_source(tmp_path, capsys):
    skill = make_skill(
        tmp_path, {'SKILL.md': fence('digraph good { a -> b }', 'digraph bad { a -> }')}
    )
    out = tmp_path / 'out'
    assert main([str(skill), str(out), '--combine']) == 1
    assert (out / 'my_skill_combined.dot').exists()
    assert not (out / 'my_skill_combined.svg').exists()
    assert 'failed' in capsys.readouterr().err

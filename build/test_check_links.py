'''Tests for check_links.py, the relative-link commit lint.'''
from pathlib import Path

import check_links as cl


def write_tree(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def test_a_missing_target_is_reported_with_its_file_and_line(tmp_path):
    write_tree(tmp_path, {'skills/a/SKILL.md': 'Intro.\n\nSee [the guide](guide.md).\n'})
    problems, checked = cl.broken_links(tmp_path, [Path('skills')])
    assert problems == ["skills/a/SKILL.md:3: broken link 'guide.md': no file at skills/a/guide.md"]
    assert checked == 1


def test_a_link_resolves_from_its_own_directory(tmp_path):
    # Plan 71's failure: text moved into references/ kept a link written for SKILL.md.
    write_tree(tmp_path, {
        'skills/a/SKILL.md': 'Read [the loop](references/loop.md).\n',
        'skills/a/prompt.md': 'Prompt.\n',
        'skills/a/references/loop.md': 'Use [the prompt](../prompt.md), not [this](prompt.md).\n',
    })
    problems, checked = cl.broken_links(tmp_path, [Path('skills')])
    assert problems == ["skills/a/references/loop.md:1: broken link 'prompt.md': "
                        'no file at skills/a/references/prompt.md']
    assert checked == 3


def test_urls_anchors_queries_and_images_are_handled(tmp_path):
    write_tree(tmp_path, {
        'skills/a/SKILL.md': ('[docs](https://example.com/x.md) [mail](mailto:a@b.c) [top](#overview)\n'
                              '[part](notes.md#usage) [q](notes.md?plain=1) ![chart](chart.svg)\n'
                              '![missing](gone.png)\n'),
        'skills/a/notes.md': 'Notes.\n',
        'skills/a/chart.svg': '<svg/>\n',
    })
    problems, checked = cl.broken_links(tmp_path, [Path('skills')])
    assert problems == ["skills/a/SKILL.md:3: broken link 'gone.png': no file at skills/a/gone.png"]
    assert checked == 4


def test_links_inside_fences_and_code_spans_are_ignored(tmp_path):
    write_tree(tmp_path, {'skills/a/SKILL.md': (
        'Inline `[x](gone.md)` and ``[y](gone.md)`` spans.\n'
        '```markdown\n[z](gone.md)\n```\n'
        '````markdown\n```\n[w](gone.md)\n```\n````\n'
        '~~~\n[v](gone.md)\n~~~\n'
        'After the fences: [u](gone.md)\n')})
    problems, _ = cl.broken_links(tmp_path, [Path('skills')])
    assert problems == ["skills/a/SKILL.md:13: broken link 'gone.md': no file at skills/a/gone.md"]


def test_main_prints_each_problem_and_a_summary_and_exits_1(tmp_path, monkeypatch, capsys):
    write_tree(tmp_path, {'docs/a.md': '[b](b.md) [c](c.md)\n', 'docs/b.md': 'B.\n'})
    monkeypatch.setattr(cl, 'REPO', tmp_path)
    assert cl.main(['docs']) == 1
    assert capsys.readouterr().out.splitlines() == [
        "docs/a.md:1: broken link 'c.md': no file at docs/c.md",
        '2 relative link(s) checked, 1 broken']


def test_main_defaults_to_skills_and_exits_0_when_clean(tmp_path, monkeypatch, capsys):
    write_tree(tmp_path, {'skills/a/SKILL.md': '[b](b.md)\n', 'skills/a/b.md': 'B.\n',
                          'docs/x.md': '[gone](gone.md)\n'})
    monkeypatch.setattr(cl, 'REPO', tmp_path)
    assert cl.main([]) == 0
    assert capsys.readouterr().out == '1 relative link(s) checked, 0 broken\n'

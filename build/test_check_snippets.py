'''Tests for check_snippets.py. Stdlib + pytest only.'''
from pathlib import Path

import check_snippets


def test_flags_an_unparseable_block(tmp_path):
    p = tmp_path / 'bad.md'
    p.write_text('# T\n\n```python\ndef model(...):\n    pass\n```\n')
    errs = check_snippets.parse_errors(p)
    assert len(errs) == 1, errs
    assert 'SyntaxError' in errs[0] and ':3:' in errs[0], errs


def test_clean_block_passes(tmp_path):
    p = tmp_path / 'good.md'
    p.write_text('```python\nx = 1\n```\n')
    assert check_snippets.parse_errors(p) == []


def test_fragment_with_free_names_still_parses(tmp_path):
    '''Most blocks are fragments referencing undefined names. Parsing is a
    syntax check, not a name check -- these must NOT be flagged.'''
    p = tmp_path / 'frag.md'
    p.write_text('```python\nidata = az.from_numpyro(mcmc)\n```\n')
    assert check_snippets.parse_errors(p) == []


def test_bayesian_workflow_parses_clean():
    '''The gate must ship green: every shipped block parses.'''
    root = Path(__file__).resolve().parent.parent / 'skills/bayesian-workflow'
    errs = [e for md in sorted(root.rglob('*.md'))
            for e in check_snippets.parse_errors(md)]
    assert errs == [], errs


def test_norun_block_is_exempt(tmp_path):
    p = tmp_path / 'x.md'
    p.write_text('```python norun needs dynamax\nbuild_params()\n```\n')
    blocks = check_snippets.iter_code_blocks(p.read_text())
    assert check_snippets.is_exempt(blocks[0]) is True


def test_plain_block_is_not_exempt(tmp_path):
    p = tmp_path / 'y.md'
    p.write_text('```python\nx = 1\n```\n')
    blocks = check_snippets.iter_code_blocks(p.read_text())
    assert check_snippets.is_exempt(blocks[0]) is False


def test_norun_still_parses_and_is_still_reported_as_advisory(tmp_path):
    '''Exempt from EXECUTION, not from parsing -- a norun block with broken
    syntax is still a defect, and the advisory keeps the gap visible.'''
    p = tmp_path / 'z.md'
    p.write_text('```python norun sketch\ndef f(...):\n    pass\n```\n')
    assert check_snippets.parse_errors(p) != []
    assert check_snippets.exempt_report(p) != []


def test_every_norun_marker_carries_a_reason():
    '''A bare `norun` with no reason is how an exemption list rots.'''
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent / 'skills/bayesian-workflow'
    bare = [f'{md}:{b.line}'
            for md in sorted(root.rglob('*.md'))
            for b in check_snippets.iter_code_blocks(md.read_text())
            if b.info.strip() == 'norun']
    assert bare == [], bare

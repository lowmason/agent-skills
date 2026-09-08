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

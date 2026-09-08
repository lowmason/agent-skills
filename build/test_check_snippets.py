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


import importlib.util

import pytest

MODULES = {'az': 'arviz'}
# The stack is an optional dep of this suite, matching the repo idiom for
# optional-dep guards (CLAUDE.md records the tune-hyperparameters skips the
# same way). Without it these would FAIL on `cannot import arviz` rather than
# skip, and CLAUDE.md's "non-ArviZ subset passes" line would be untrue.
requires_stack = pytest.mark.skipif(
    importlib.util.find_spec('arviz') is None,
    reason='needs the ArviZ stack; see CLAUDE.md for the --api invocation')


@requires_stack
def test_missing_attribute_is_flagged(tmp_path):
    p = tmp_path / 'a.md'
    p.write_text('```python\naz.definitely_not_a_real_function(x)\n```\n')
    errs = check_snippets.api_errors(p, MODULES)
    assert any('definitely_not_a_real_function' in e for e in errs), errs


@requires_stack
def test_real_attribute_passes(tmp_path):
    p = tmp_path / 'b.md'
    p.write_text('```python\nidata = az.from_numpyro(mcmc)\n```\n')
    assert check_snippets.api_errors(p, MODULES) == []


@requires_stack
def test_backticked_prose_identifier_is_checked(tmp_path):
    '''D2 lived in a markdown bullet, not a code block. If this tier only read
    code it would have missed the finding that motivates it.'''
    p = tmp_path / 'c.md'
    p.write_text('- `az.no_such_thing`: gone in ArviZ 1.x\n')
    assert check_snippets.api_errors(p, MODULES) != []


@requires_stack
def test_non_library_roots_are_ignored(tmp_path):
    '''`idata.posterior` and `model.foo` are user code, not library API.'''
    p = tmp_path / 'd.md'
    p.write_text('```python\nidata.posterior.mean()\nmodel.whatever()\n```\n')
    assert check_snippets.api_errors(p, MODULES) == []


def test_elided_block_is_not_runnable(tmp_path):
    p = tmp_path / 'e.md'
    p.write_text('```python\nmodel = ...\n...\n```\n')
    b = check_snippets.iter_code_blocks(p.read_text())[0]
    assert check_snippets.runnable(b) is False


def test_block_with_unbound_name_is_not_runnable(tmp_path):
    p = tmp_path / 'f.md'
    p.write_text('```python\nresult = totally_unbound_thing(1)\n```\n')
    b = check_snippets.iter_code_blocks(p.read_text())[0]
    assert check_snippets.runnable(b) is False


def test_preamble_bound_block_is_runnable(tmp_path):
    p = tmp_path / 'g.md'
    p.write_text('```python\nsummary = az.summary(idata)\n```\n')
    b = check_snippets.iter_code_blocks(p.read_text())[0]
    assert check_snippets.runnable(b) is True


@requires_stack
def test_raising_block_is_reported(tmp_path):
    p = tmp_path / 'h.md'
    p.write_text('```python\nraise ValueError("boom")\n```\n')
    errs = check_snippets.run_errors(p, timeout=60)
    assert any('boom' in e for e in errs), errs


@requires_stack
def test_block_side_effects_do_not_touch_cwd(tmp_path, monkeypatch):
    '''Blocks write model_output.nc and a literal <slug>/ dir. The runner must
    execute elsewhere or the gate pollutes the repo it guards.'''
    p = tmp_path / 'i.md'
    p.write_text('```python\nopen("sentinel.txt", "w").write("x")\n```\n')
    monkeypatch.chdir(tmp_path)
    check_snippets.run_errors(p, timeout=60)
    assert not (tmp_path / 'sentinel.txt').exists()

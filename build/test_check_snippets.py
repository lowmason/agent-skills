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
    '''A bare `norun` with no reason is how an exemption list rots.

    Repo-wide since the parse tier went repo-wide: a reason check scoped to
    one skill is a hole in a gate that covers all of them.'''
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent / 'skills'
    bare = [f'{md}:{b.line}'
            for md in sorted(root.rglob('*.md'))
            for b in check_snippets.iter_code_blocks(md.read_text())
            if b.info.strip() == 'norun']
    assert bare == [], bare


def test_noparse_block_is_exempt_from_parsing(tmp_path):
    '''An excerpt whose indentation is load-bearing cannot be made valid
    standalone Python without losing its meaning. noparse is that escape.'''
    p = tmp_path / 'frag.md'
    p.write_text('```python noparse indented excerpt\n    x = 1\n```\n')
    assert check_snippets.parse_errors(p) == []


def test_noparse_implies_norun(tmp_path):
    '''A block that cannot be parsed cannot be executed either -- otherwise
    --run tries it and fails confusingly.'''
    p = tmp_path / 'frag.md'
    p.write_text('```python noparse indented excerpt\n    x = 1\n```\n')
    block = next(iter(check_snippets.iter_code_blocks(p.read_text())))
    assert check_snippets.is_exempt(block) is True


def test_noparse_is_reported_as_advisory(tmp_path):
    '''Silent exemption is how partial coverage reads as total coverage.'''
    p = tmp_path / 'frag.md'
    p.write_text('```python noparse indented excerpt\n    x = 1\n```\n')
    rep = check_snippets.exempt_report(p)
    assert len(rep) == 1, rep
    assert 'indented excerpt' in rep[0], rep


def test_noparse_still_flags_a_bare_marker(tmp_path):
    '''noparse without a reason must not silently pass the reason test.'''
    p = tmp_path / 'frag.md'
    p.write_text('```python noparse\n    x = 1\n```\n')
    block = next(iter(check_snippets.iter_code_blocks(p.read_text())))
    assert block.info.strip() == 'noparse'


def test_every_noparse_marker_carries_a_reason():
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent / 'skills'
    bare = [f'{md}:{b.line}'
            for md in sorted(root.rglob('*.md'))
            for b in check_snippets.iter_code_blocks(md.read_text())
            if b.info.strip() == 'noparse']
    assert bare == [], bare


def test_all_skills_parse_clean():
    '''The repo-wide parse tier must ship green, not just bayesian-workflow.'''
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent / 'skills'
    errs = [e for md in sorted(root.rglob('*.md'))
            for e in check_snippets.parse_errors(md)]
    assert errs == [], errs


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


def test_preamble_add_log_prior_matches_the_doc():
    '''The preamble embeds sensitivity.md's add_log_prior verbatim, so running
    --run also exercises that documented block. Nothing else pins them equal,
    and a fixture that silently diverges from the doc it claims to copy is
    exactly the "second source of truth" hazard snippet_preamble.py warns
    about -- it would go green while the documented version was broken.'''
    from pathlib import Path

    from snippet_preamble import PREAMBLE
    doc = (Path(__file__).resolve().parent.parent
           / 'skills/bayesian-workflow/references/sensitivity.md').read_text()
    block = next(b for b in check_snippets.iter_code_blocks(doc)
                 if 'def add_log_prior' in b.code)
    fn = block.code[block.code.index('def add_log_prior'):]
    fn = fn[:fn.index('\n# Use the SAME')].rstrip()
    assert fn in PREAMBLE, 'preamble drifted from sensitivity.md add_log_prior'


@requires_stack
def test_documented_absent_names_are_still_absent():
    '''DOCUMENTED_ABSENT exempts prose that names a REMOVED API. If one comes
    back on a newer stack the doc's "removed" claim is now wrong -- and the
    allowlist would hide exactly the staleness --api exists to catch. So the
    allowlist re-validates against the installed stack, the same way
    test_every_norun_marker_carries_a_reason keeps norun auditable.'''
    resurrected = [name for name in check_snippets.DOCUMENTED_ABSENT
                   if check_snippets._resolve(name, {'az': 'arviz'}) is None]
    assert resurrected == [], resurrected


def _skill_block(relpath, needle):
    '''The bayesian-workflow block whose code contains `needle`. Found by
    content, not line number, so prose edits above it do not break the test.'''
    doc = (Path(__file__).resolve().parent.parent
           / 'skills/bayesian-workflow' / relpath).read_text()
    return next(b for b in check_snippets.iter_code_blocks(doc) if needle in b.code)


def test_blocks_the_shared_fixture_already_carries_are_admitted():
    '''diagnostics.md's run_diagnostics reads sample_stats["diverging"], which the
    preamble's MCMC records via extra_fields; model-comparison.md's
    log_likelihood call needs posterior_samples, which the preamble's mcmc
    already holds.'''
    for relpath, needle in (
            ('references/diagnostics.md', 'def run_diagnostics(idata)'),
            ('references/model-comparison.md',
             'log_likelihood(model, posterior_samples')):
        block = _skill_block(relpath, needle)
        assert check_snippets.runnable(block), check_snippets._unrunnable_reason(block)


@requires_stack
def test_every_fixture_var_is_carried_by_the_fixture_idata():
    '''FIXTURE_VARS is the honesty half of the fixture: every name in it must be
    a variable the preamble's idata carries, in some group.'''
    import os
    import subprocess
    import sys

    from snippet_preamble import FIXTURE_VARS, PREAMBLE
    check = (
        '\ncarried = {name for node in idata.children.values()'
        ' for name in node.data_vars}\n'
        f'missing = [n for n in {sorted(FIXTURE_VARS)!r} if n not in carried]\n'
        'assert not missing, missing\n')
    proc = subprocess.run([sys.executable, '-c', PREAMBLE + check],
                          capture_output=True, text=True, timeout=300,
                          env={**os.environ, 'MPLBACKEND': 'Agg'})
    assert proc.returncode == 0, proc.stderr[-2000:]


def _annotated_block(tmp_path, info, code):
    '''A one-block markdown file whose fence info string is `python <info>`.'''
    path = tmp_path / 'block.md'
    path.write_text(f'```python {info}\n{code}\n```\n')
    return check_snippets.iter_code_blocks(path.read_text())[0], path


def test_a_named_fixture_binds_names_for_the_block_that_selects_it(tmp_path, monkeypatch):
    from snippet_preamble import Fixture
    monkeypatch.setitem(check_snippets.NAMED_FIXTURES, 'tiny',
                        Fixture(code='tiny_name = 1\n', variables=frozenset()))
    selected, _ = _annotated_block(tmp_path, 'fixture=tiny', 'print(tiny_name)')
    assert check_snippets.runnable(selected), check_snippets._unrunnable_reason(selected)
    plain, _ = _annotated_block(tmp_path, '', 'print(tiny_name)')
    assert 'unbound names' in check_snippets._unrunnable_reason(plain)


def test_a_named_fixture_widens_the_variables_a_block_may_ask_for(tmp_path, monkeypatch):
    from snippet_preamble import Fixture
    monkeypatch.setitem(check_snippets.NAMED_FIXTURES, 'tiny',
                        Fixture(code='', variables=frozenset({'tau'})))
    code = 's = az.summary(idata, var_names=["tau"])'
    selected, _ = _annotated_block(tmp_path, 'fixture=tiny', code)
    assert check_snippets.runnable(selected), check_snippets._unrunnable_reason(selected)
    plain, _ = _annotated_block(tmp_path, '', code)
    assert 'needs fixture variables' in check_snippets._unrunnable_reason(plain)


def test_an_unknown_fixture_fails_the_gate(tmp_path):
    _, path = _annotated_block(tmp_path, 'fixture=no_such_fixture', 'x = 1')
    errors = check_snippets.fixture_errors(path)
    assert len(errors) == 1 and 'no_such_fixture' in errors[0], errors
    assert check_snippets.main([str(path)]) == 1


@requires_stack
def test_a_named_fixture_runs_between_the_preamble_and_the_block(tmp_path, monkeypatch):
    '''The fixture can use what the preamble binds (N = 40), and the block can
    use what the fixture binds (tiny_name).'''
    from snippet_preamble import Fixture
    monkeypatch.setitem(check_snippets.NAMED_FIXTURES, 'tiny',
                        Fixture(code='tiny_name = N + 1\n', variables=frozenset()))
    _, path = _annotated_block(tmp_path, 'fixture=tiny', 'assert tiny_name == 41')
    assert check_snippets.run_errors(path, timeout=300) == []


COMPARISON_BLOCKS = (
    ('references/model-comparison.md', 'idata_1 = az.from_numpyro(mcmc_1'),
    ('references/model-comparison.md', 'models = {"m1": idata_1'),
    ('references/model-comparison.md', 'az.compare(models, method="stacking")'),
    ('references/model-comparison.md', 'loo_a = az.loo(idata_1'),
    ('references/visualize.md', 'loo2 = az.loo(idata_m2'),
)


def test_the_comparison_fixture_binds_every_name_its_blocks_use():
    import ast

    from snippet_preamble import NAMED_FIXTURES
    bound = check_snippets._bound_by(ast.parse(NAMED_FIXTURES['comparison'].code))
    assert {'mcmc_1', 'mcmc_2', 'mcmc_3', 'idata_1', 'idata_2', 'idata_3',
            'models', 'idata_m2', 'idata_m3'} <= bound


def test_the_comparison_blocks_select_the_comparison_fixture():
    '''Every bayesian-workflow block that compares fitted variants is admitted
    through the comparison fixture. Blocks are found by content, not line.'''
    for relpath, needle in COMPARISON_BLOCKS:
        block = _skill_block(relpath, needle)
        assert check_snippets.fixture_name(block) == 'comparison', needle
        assert check_snippets.runnable(block), check_snippets._unrunnable_reason(block)

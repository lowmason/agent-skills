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


def test_all_skills_select_known_fixtures():
    '''Positive control for fixture_errors: every shipped block's fixture
    selection is well-formed and names a fixture snippet_preamble defines. Also
    guards the five shipped `fixture=comparison` blocks.'''
    root = Path(__file__).resolve().parent.parent / 'skills'
    errs = [e for md in sorted(root.rglob('*.md'))
            for e in check_snippets.fixture_errors(md)]
    assert errs == [], errs


def test_a_known_fixture_selection_is_not_an_error(tmp_path):
    _, path = _annotated_block(tmp_path, 'fixture=comparison', 'x = 1')
    assert check_snippets.fixture_errors(path) == []


def test_a_norun_marker_after_a_fixture_fails_the_gate(tmp_path):
    '''`fixture=x norun <reason>` used to drop the norun silently: _marker read
    only the first token, so the block ran and its audit line was lost.'''
    _, path = _annotated_block(tmp_path, 'fixture=comparison norun needs a GPU', 'x = 1')
    errors = check_snippets.fixture_errors(path)
    assert len(errors) == 1 and 'norun' in errors[0], errors
    assert check_snippets.main([str(path)]) == 1


def test_a_noparse_marker_after_a_fixture_fails_the_gate(tmp_path):
    _, path = _annotated_block(tmp_path, 'fixture=comparison noparse excerpt', 'x = 1')
    errors = check_snippets.fixture_errors(path)
    assert len(errors) == 1 and 'noparse' in errors[0], errors


def test_a_norun_reason_naming_a_fixture_is_free_text(tmp_path):
    '''A leading marker makes the rest of the info string a reason. It used to
    be scanned for `fixture=`, so an unknown name in prose failed the gate.'''
    block, path = _annotated_block(
        tmp_path, 'norun superseded by fixture=no_such_fixture', 'x = 1')
    assert check_snippets.fixture_name(block) is None
    assert check_snippets.fixture_errors(path) == []
    assert check_snippets.main([str(path)]) == 0
    assert 'fixture=no_such_fixture' in check_snippets.exempt_report(path)[0]


def test_a_misspelled_fixture_key_fails_the_gate(tmp_path):
    '''Deliberate failure, not an advisory: a typo'd key would otherwise leave
    the block plain and surface only under --run.'''
    for info in ('fixtures=comparison', 'Fixture=comparison', 'fixture=',
                 'fixture', 'fixture:comparison'):
        _, path = _annotated_block(tmp_path, info, 'x = 1')
        errors = check_snippets.fixture_errors(path)
        if info == 'fixture:comparison':
            # A colon is not the key=value shape; it is ordinary free text.
            assert errors == [], (info, errors)
            continue
        assert len(errors) == 1 and 'malformed' in errors[0], (info, errors)
        assert check_snippets.main([str(path)]) == 1, info


def test_two_fixture_selections_fail_the_gate(tmp_path):
    _, path = _annotated_block(tmp_path, 'fixture=comparison fixture=comparison', 'x = 1')
    errors = check_snippets.fixture_errors(path)
    assert len(errors) == 1 and 'more than one' in errors[0], errors


def test_other_info_string_tokens_stay_legal(tmp_path):
    '''deep-learning blocks carry `cpu-example`, mintlify-style ones
    `theme={null}`; neither is a marker or a fixture key.'''
    for info in ('cpu-example', 'theme={null}', 'cpu-example fixture=comparison',
                 'fixture=comparison some trailing note'):
        _, path = _annotated_block(tmp_path, info, 'x = 1')
        assert check_snippets.fixture_errors(path) == [], info


def test_a_fixture_leading_block_still_selects_its_fixture(tmp_path):
    block, _ = _annotated_block(tmp_path, 'fixture=comparison a note', 'x = 1')
    assert check_snippets.fixture_name(block) == 'comparison'
    assert check_snippets.is_exempt(block) is False


@requires_stack
def test_a_named_fixture_runs_between_the_preamble_and_the_block(tmp_path, monkeypatch):
    '''The fixture can use what the preamble binds (N = 40), and the block can
    use what the fixture binds (tiny_name).'''
    from snippet_preamble import Fixture
    monkeypatch.setitem(check_snippets.NAMED_FIXTURES, 'tiny',
                        Fixture(code='tiny_name = N + 1\n', variables=frozenset()))
    block, path = _annotated_block(tmp_path, 'fixture=tiny', 'assert tiny_name == 41')
    # run_errors skips a block it cannot run and returns [] for it, so without
    # this the final assertion would hold even if nothing executed.
    assert check_snippets.runnable(block), check_snippets._unrunnable_reason(block)
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
    bound = check_snippets._module_names(ast.parse(NAMED_FIXTURES['comparison'].code))
    assert {'mcmc_1', 'mcmc_2', 'mcmc_3', 'idata_1', 'idata_2', 'idata_3',
            'models', 'idata_m2', 'idata_m3'} <= bound


def test_the_comparison_blocks_select_the_comparison_fixture():
    '''Every bayesian-workflow block that compares fitted variants is admitted
    through the comparison fixture. Blocks are found by content, not line.'''
    for relpath, needle in COMPARISON_BLOCKS:
        block = _skill_block(relpath, needle)
        assert check_snippets.fixture_name(block) == 'comparison', needle
        assert check_snippets.runnable(block), check_snippets._unrunnable_reason(block)


def test_a_fixtures_locals_do_not_bind_names_for_its_blocks(tmp_path, monkeypatch):
    '''Only a fixture's MODULE-level names are in scope for the block. A
    parameter, a function local or a comprehension target is not, so a block
    that uses one is reported unbound instead of admitted and run against it.'''
    from snippet_preamble import Fixture
    code = ('def make(arg):\n    inner = arg\n    return inner\n'
            'value = make(1)\n'
            'both = [item for item in (value,)]\n')
    monkeypatch.setitem(check_snippets.NAMED_FIXTURES, 'tiny',
                        Fixture(code=code, variables=frozenset()))
    ok, _ = _annotated_block(tmp_path, 'fixture=tiny', 'print(make(value), both)')
    assert check_snippets.runnable(ok), check_snippets._unrunnable_reason(ok)
    for local in ('inner', 'arg', 'item'):
        block, _ = _annotated_block(tmp_path, 'fixture=tiny', f'print({local})')
        assert f"unbound names ['{local}']" in check_snippets._unrunnable_reason(block)


def test_a_helper_the_fixture_deletes_is_not_bound(tmp_path, monkeypatch):
    from snippet_preamble import Fixture
    code = 'def helper():\n    return 1\n\nvalue = helper()\ndel helper\n'
    monkeypatch.setitem(check_snippets.NAMED_FIXTURES, 'tiny',
                        Fixture(code=code, variables=frozenset()))
    keeps, _ = _annotated_block(tmp_path, 'fixture=tiny', 'print(value)')
    assert check_snippets.runnable(keeps), check_snippets._unrunnable_reason(keeps)
    calls, _ = _annotated_block(tmp_path, 'fixture=tiny', 'print(helper())')
    assert "unbound names ['helper']" in check_snippets._unrunnable_reason(calls)


def test_the_comparison_fixtures_helpers_are_not_bound_for_a_block(tmp_path):
    '''fit/model_wide/model_robust are module-level in the fixture, so only the
    fixture's `del` keeps a doc block from calling an undefined `fit(...)` and
    running GREEN against the fixture's helper. run/variant/key are locals.'''
    for name in ('fit', 'model_wide', 'model_robust', 'run', 'variant', 'key'):
        block, _ = _annotated_block(tmp_path, 'fixture=comparison', f'print({name})')
        assert f"unbound names ['{name}']" in check_snippets._unrunnable_reason(block), name


def test_the_preamble_binds_module_level_names_only(tmp_path):
    '''`per_draw` is a local of the preamble's add_log_prior, `params` its
    parameter: neither is in scope for a doc block. `add_log_prior` is.'''
    ok, _ = _annotated_block(tmp_path, '', 'idata = add_log_prior(idata, model, mcmc, x, y=y)')
    assert check_snippets.runnable(ok), check_snippets._unrunnable_reason(ok)
    for local in ('per_draw', 'params', 'flat'):
        block, _ = _annotated_block(tmp_path, '', f'print({local})')
        assert f"unbound names ['{local}']" in check_snippets._unrunnable_reason(block), local


def test_module_names_follow_binding_forms_and_deletes():
    import ast
    tree = ast.parse(
        'import os.path\nimport numpy as np\nfrom a import b as c\n'
        'x, (y, *z) = 1, (2, 3)\nw: int = 1\nw += 1\n'
        'for i in range(2):\n    j = i\n'
        'with open("f") as fh:\n    pass\n'
        'try:\n    pass\nexcept Exception as err:\n    pass\n'
        'if (n := 3):\n    q = 1\n'
        'def f(param):\n    local = 1\n'
        'class K:\n    attr = 1\n'
        'sq = [e for e in range(3)]\n'
        'gone = 1\ndel gone\n')
    assert check_snippets._module_names(tree) == {
        'os', 'np', 'c', 'x', 'y', 'z', 'w', 'i', 'j', 'fh', 'err', 'n', 'q',
        'f', 'K', 'sq'}


@requires_stack
def test_the_comparison_fixtures_helpers_are_gone_at_run_time(tmp_path):
    '''The static check keeps a block calling `fit` from being admitted; the
    fixture's `del` makes the same call raise if it were ever executed.'''
    import os
    import subprocess
    import sys

    from snippet_preamble import NAMED_FIXTURES, PREAMBLE
    check = ('\nfor helper in ("fit", "model_wide", "model_robust"):\n'
             '    assert helper not in globals(), helper\n'
             'assert "models" in globals()\n')
    program = PREAMBLE + NAMED_FIXTURES['comparison'].code + check
    proc = subprocess.run([sys.executable, '-c', program], cwd=tmp_path,
                          capture_output=True, text=True, timeout=300,
                          env={**os.environ, 'MPLBACKEND': 'Agg'})
    assert proc.returncode == 0, proc.stderr[-2000:]

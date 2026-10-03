from pathlib import Path

from check_jax_examples import collect_examples, run_example


def write_example(tmp_path: Path, code: str, info: str = 'cpu-example probe') -> Path:
    path = tmp_path / 'example.md'
    path.write_text(f'```python {info}\n{code}\n```\n')
    return path


def test_standalone_execution_has_cpu_env_and_no_bayesian_fixture(tmp_path):
    path = write_example(tmp_path, (
        'import os, sys\n'
        "assert os.environ['JAX_PLATFORMS'] == 'cpu'\n"
        "assert 'numpyro' not in sys.modules\n"
        "assert 'arviz' not in sys.modules\n"
    ))
    examples, errors = collect_examples([path])
    assert errors == []
    assert len(examples) == 1
    assert examples[0].line == 1
    assert run_example(examples[0], 5)[0]


def test_assertion_failure_preserves_traceback_and_source_location(tmp_path):
    path = write_example(tmp_path, "raise AssertionError('bad mask')")
    examples, _ = collect_examples([path])
    passed, detail = run_example(examples[0], 5)
    assert not passed
    assert f'{path}:1' in detail
    assert 'Traceback' in detail
    assert 'bad mask' in detail


def test_each_example_gets_a_fresh_working_directory(tmp_path):
    path = write_example(tmp_path, (
        'from pathlib import Path\n'
        "assert not Path('state.txt').exists()\n"
        "Path('state.txt').write_text('private fixture')\n"
    ))
    examples, _ = collect_examples([path])
    assert run_example(examples[0], 5)[0]
    assert run_example(examples[0], 5)[0]
    assert not (tmp_path / 'state.txt').exists()


def test_timeout_is_a_failure(tmp_path):
    path = write_example(tmp_path, 'import time\ntime.sleep(5)')
    examples, _ = collect_examples([path])
    passed, detail = run_example(examples[0], 0.1)
    assert not passed
    assert 'timed out' in detail


def test_empty_requested_scope_fails(tmp_path):
    path = tmp_path / 'empty.md'
    path.write_text('# Prose only\n')
    examples, errors = collect_examples([path])
    assert examples == []
    assert any('zero CPU examples' in error for error in errors)


def test_unmarked_python_is_not_silently_ignored(tmp_path):
    path = write_example(tmp_path, 'assert True', '')
    _, errors = collect_examples([path])
    assert any('execution marker' in error for error in errors)


def test_duplicate_ids_are_rejected(tmp_path):
    write_example(tmp_path, 'assert True')
    (tmp_path / 'second.md').write_text('```python cpu-example probe\nassert True\n```\n')
    _, errors = collect_examples([tmp_path])
    assert any('duplicate example id' in error for error in errors)


def test_explicit_nonrun_reason_is_allowed_but_not_counted(tmp_path):
    path = write_example(tmp_path, 'assert True')
    with path.open('a') as handle:
        handle.write('```python norun requires a real accelerator checkpoint\n')
        handle.write('assert True\n```\n')
    examples, errors = collect_examples([path])
    assert errors == []
    assert len(examples) == 1

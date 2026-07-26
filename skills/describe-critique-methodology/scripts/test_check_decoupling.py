'''Tests for the advisory decoupling checker.

Bare imports, directory-scoped — run from this directory:
uv run --python 3.13 --with pytest python -m pytest -q
'''
import subprocess
import sys
from pathlib import Path

from check_decoupling import harvest, notation_whitelist, suspicious_notation


def toks(findings):
    return {f.token for f in findings}


def cats(findings):
    return {f.category for f in findings}


def test_flags_snake_case_multitoken():
    fs = harvest('the kalman_ll factor carries the likelihood')
    assert 'kalman_ll' in toks(fs)
    assert 'snake_case' in cats(fs)


def test_flags_camel_case():
    fs = harvest('assembled by assembleTotal downstream')
    assert 'assembleTotal' in toks(fs)
    assert 'camelCase' in cats(fs)


def test_ignores_single_words_and_greek():
    assert harvest('the state evolves with growth and sigma controls scale') == []


def test_flags_backticked_dotted_token():
    fs = harvest('see `model.py` for details')
    assert 'model.py' in toks(fs)


def test_ignores_backticked_single_word_and_greek():
    assert harvest('the site `sigma` and the `trend` term') == []


def test_flags_identifier_path():
    fs = harvest('lives in packages/nfp-model')
    assert 'packages/nfp-model' in toks(fs)
    assert 'path' in cats(fs)


def test_ignores_natural_slash_pairs():
    assert harvest('estimation and/or inference') == []


def test_flags_dotted_call_syntax():
    fs = harvest("a single numpyro.factor('ll', x) call")
    assert 'numpyro.factor' in toks(fs)
    assert 'call' in cats(fs)


def test_ignores_distribution_call_notation():
    assert harvest('with priors N(0, 1) and LogNormal(0, 1)') == []


def test_notation_table_whitelist():
    doc = '\n'.join([
        '## Notation',
        '| Symbol | Meaning |',
        '| --- | --- |',
        '| `y_t` | observed employment at month t |',
        '',
        '## Procedure',
        'the series y_t is observed monthly',
    ])
    wl = notation_whitelist(doc)
    assert 'y_t' in wl
    assert harvest(doc, wl) == []


def test_whitelist_is_scoped_to_notation_sections():
    doc = '## Setup\n| `foo_bar` | not a notation table |\n'
    assert notation_whitelist(doc) == set()


def test_suspicious_notation_flags_identifier_shaped_symbols():
    assert suspicious_notation({'kalman_ll', 'assembleTotal', 'model.py'}) == [
        'assembleTotal', 'kalman_ll', 'model.py',
    ]


def test_suspicious_notation_exempts_math_shaped_symbols():
    assert suspicious_notation({'y_t', 'g_cont', 'sigma_obs', 'beta', 'T'}) == []


def test_cli_always_exits_zero(tmp_path):
    doc = tmp_path / 'm.md'
    doc.write_text('uses kalman_ll everywhere\n')
    proc = subprocess.run(
        [sys.executable, str(Path(__file__).parent / 'check_decoupling.py'), str(doc)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0
    assert 'kalman_ll' in proc.stdout
    assert 'ADVISORY' in proc.stdout

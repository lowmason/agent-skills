"""Tests for profile.py — run from this directory (bare imports).

cd skills/explore-data/scripts && uv run --python 3.13 --with pytest --with polars \
  python -m pytest -q

Note on the import: this directory's profile.py shadows Python's stdlib `profile`
module. The bare import below resolves to the local file because pytest puts the
test file's own directory first on sys.path — and it does that from any working
directory, so the shadowing is not why these tests are run from inside this
directory.

The directory-scoped convention is repo-wide: each scripts/ suite declares its own
inline deps (there's no root pyproject or test runner), and a repo-root collection
fails outright, since geographic-codes and classification-codes both ship a
test_build.py, whose basenames collide under pytest's prepend import mode with no
__init__.py.
"""

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import polars as pl
import pytest

from profile import column_profile, duplicate_check, quality_flags, scan

SCRIPT = Path(__file__).resolve().parent / "profile.py"


@pytest.fixture
def tiny(tmp_path):
    """5 rows x 4 cols: one duplicated key pair, one null, one constant column."""
    path = tmp_path / "tiny.parquet"
    pl.DataFrame(
        {
            "series_id": ["a", "a", "b", "b", "b"],
            "ref_date": [
                dt.date(2025, 1, 1),
                dt.date(2025, 2, 1),
                dt.date(2025, 1, 1),
                dt.date(2025, 2, 1),
                dt.date(2025, 2, 1),
            ],
            "value": [1.0, 2.0, 3.0, None, 5.0],
            "flag": ["x", "x", "x", "x", "x"],
        }
    ).write_parquet(path)
    return path


def _run_json(path, tmp_path, *extra):
    """Run the CLI and return the parsed --json payload."""
    out = tmp_path / "out.json"
    subprocess.run(
        [sys.executable, str(SCRIPT), str(path), "--json", str(out), *extra],
        check=True,
        capture_output=True,
    )
    return json.loads(out.read_text())


def test_json_carries_the_fields_recommend_visualization_consumes(tiny, tmp_path):
    """The handoff contract: recommend-visualization's fields_from_profile reads
    profile['columns'][i] for 'column', 'dtype', 'n_unique' and 'null_pct'.
    Renaming any of those four silently breaks the sibling skill."""
    payload = _run_json(tiny, tmp_path)
    assert set(payload) >= {"path", "n_rows", "n_cols", "columns", "dates", "flags"}
    assert payload["n_rows"] == 5
    assert payload["n_cols"] == 4
    for col in payload["columns"]:
        assert {"column", "dtype", "null_pct", "n_unique", "example"} <= set(col)
    by_name = {c["column"]: c for c in payload["columns"]}
    assert by_name["value"]["null_pct"] == 20.0
    assert by_name["value"]["dtype"] == "Float64"
    assert by_name["flag"]["n_unique"] == 1
    assert by_name["series_id"]["n_unique"] == 2


def test_json_is_serializable_with_dates_as_strings(tiny, tmp_path):
    """profile.py dumps with default=str; a Date min/max must survive as a string,
    not blow up json.dumps or land as a repr."""
    payload = _run_json(tiny, tmp_path)
    assert payload["dates"]["ref_date"]["min"] == "2025-01-01"
    assert payload["dates"]["ref_date"]["max"] == "2025-02-01"
    assert payload["dates"]["ref_date"]["missing_monthly_periods"] == 0
    json.dumps(payload)  # must not raise


def test_json_duplicate_check_appears_only_when_requested(tiny, tmp_path):
    assert "duplicate_check" not in _run_json(tiny, tmp_path)
    payload = _run_json(tiny, tmp_path, "--candidate-keys", "series_id,ref_date")
    assert payload["duplicate_check"]["is_unique"] is False
    assert payload["duplicate_check"]["duplicate_groups"] == 1
    assert payload["duplicate_check"]["extra_rows"] == 1


def test_duplicate_check_flags_a_fanout_key(tiny):
    lf = scan(str(tiny))
    schema = lf.collect_schema()
    assert duplicate_check(lf, ["series_id", "ref_date"], schema)["is_unique"] is False
    # series_id alone is not unique either; all three columns together are.
    assert duplicate_check(lf, ["series_id", "ref_date", "value"], schema)["is_unique"] is True


def test_duplicate_check_reports_unknown_columns_instead_of_raising(tiny):
    lf = scan(str(tiny))
    result = duplicate_check(lf, ["series_id", "nope"], lf.collect_schema())
    assert "nope" in result["error"]


def test_quality_flags_catch_constant_high_null_and_sentinels(tmp_path):
    path = tmp_path / "dirty.parquet"
    pl.DataFrame(
        {
            "constant": ["x"] * 4,
            "mostly_null": [1.0, None, None, None],
            "sentinel_str": ["N/A", "ok", "ok", "ok"],
            "sentinel_num": [-999.0, 1.0, 2.0, 3.0],
        }
    ).write_parquet(path)
    lf = scan(str(path))
    schema = lf.collect_schema()
    flags = quality_flags(column_profile(lf, 4, schema), 4, lf, schema)
    joined = " | ".join(flags)
    assert "CONSTANT: constant" in joined
    assert "HIGH NULL: mostly_null" in joined
    assert "SENTINEL: sentinel_str" in joined
    assert "SENTINEL?: sentinel_num" in joined


def test_scan_rejects_an_unsupported_extension(tmp_path):
    bad = tmp_path / "data.xlsx"
    bad.write_bytes(b"not really a workbook")
    with pytest.raises(ValueError, match="Unsupported extension"):
        scan(str(bad))

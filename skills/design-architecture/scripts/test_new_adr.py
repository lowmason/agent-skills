"""Tests for new_adr.py — run from this directory (bare imports).

cd skills/design-architecture/scripts && uv run --python 3.13 --with pytest python -m pytest -q

Stdlib only: new_adr.py imports nothing outside the standard library, so this
suite needs no scientific deps.
"""

import datetime as dt

import pytest

from new_adr import VALID_STATUS, main, next_number, slugify


def test_slugify_collapses_punctuation_and_case():
    assert slugify("Use NumPyro/JAX over PyMC") == "use-numpyro-jax-over-pymc"
    assert slugify("  Trailing & leading!! ") == "trailing-leading"
    assert slugify("Already-slug-like") == "already-slug-like"


def test_slugify_never_returns_an_empty_stem():
    """A title of pure punctuation would otherwise produce '0001-.md'."""
    assert slugify("###") == "adr"
    assert slugify("") == "adr"


def test_next_number_starts_at_one_for_a_missing_directory(tmp_path):
    assert next_number(tmp_path / "not-created-yet") == 1


def test_next_number_takes_the_highest_prefix_not_the_count(tmp_path):
    """Numbering is permanent: deleting 0002 must not let 0003 be reissued."""
    for name in ("0001-a.md", "0003-c.md", "notes.md"):
        (tmp_path / name).write_text("x")
    assert next_number(tmp_path) == 4


def test_main_writes_sequentially_numbered_files(tmp_path):
    target = tmp_path / "specs" / "adr"
    assert main(["First decision", "--dir", str(target)]) == 0
    assert main(["Second decision", "--dir", str(target)]) == 0
    names = sorted(p.name for p in target.iterdir())
    assert names == ["0001-first-decision.md", "0002-second-decision.md"]


def test_main_fills_number_title_status_and_today(tmp_path):
    target = tmp_path / "adr"
    main(["Store parquet levels only", "--dir", str(target), "--status", "Accepted"])
    body = (target / "0001-store-parquet-levels-only.md").read_text()
    assert body.startswith("# 0001. Store parquet levels only\n")
    assert "- **Status:** Accepted" in body
    assert f"- **Date:** {dt.date.today().isoformat()}" in body
    # the template's required sections survive formatting
    for heading in ("## Context", "## Decision", "## Consequences",
                    "## Alternatives considered", "## Trade-offs & reversibility"):
        assert heading in body


def test_reusing_a_title_never_overwrites_the_earlier_adr(tmp_path):
    """The property that actually matters: an ADR is a permanent record, so
    running the scaffolder twice with the same title must produce a second
    numbered file and leave the first byte-for-byte intact.

    Note the script's `if path.exists()` branch is unreachable through main():
    next_number() returns highest+1, and any NNNN- file it could collide with
    would itself have raised that highest. It is defensive code, as its own
    comment says, so this test pins the reachable guarantee instead of
    manufacturing a collision that cannot occur."""
    target = tmp_path / "adr"
    main(["Same Title", "--dir", str(target)])
    first = (target / "0001-same-title.md").read_text()
    assert main(["Same Title", "--dir", str(target)]) == 0
    assert sorted(p.name for p in target.iterdir()) == [
        "0001-same-title.md",
        "0002-same-title.md",
    ]
    assert (target / "0001-same-title.md").read_text() == first


def test_invalid_status_is_rejected(tmp_path):
    assert VALID_STATUS == {"Proposed", "Accepted", "Deprecated"}
    with pytest.raises(SystemExit):
        main(["Some title", "--dir", str(tmp_path), "--status", "Bogus"])

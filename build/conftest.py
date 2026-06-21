"""Pytest fixtures for the build-tooling tests. `real_ref` pulls a genuinely-present
(section, notebook) pair from build/.scratch/ so the true-positive test is not hard-coded."""
from pathlib import Path

import pytest

SCRATCH = Path(__file__).parent / ".scratch"


@pytest.fixture
def real_ref():
    sec = next(
        ln.split("\t")[0]
        for ln in (SCRATCH / "book1_sections.tsv").read_text().splitlines()
        if "." in ln.split("\t")[0]  # a real section, e.g. 10.4 (not a bare chapter)
    )
    nb = (SCRATCH / "pyprobml_files.txt").read_text().split()[0]
    return type("R", (), {"sec": sec, "nb": nb})

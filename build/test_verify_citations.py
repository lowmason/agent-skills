"""Tests for the Gate A citation verifier. The true-negative test is the important one:
a verifier that passes everything is worse than none."""
from verify_citations import verify_text


def test_true_negative_flags_bad_refs():
    bad = "Use PML1 §99.9 and notebooks/book1/does_not_exist_xyz.ipynb."
    failures = verify_text(bad)
    assert any("99.9" in f for f in failures), failures
    assert any("does_not_exist_xyz" in f for f in failures), failures


def test_true_positive_passes_real_refs(real_ref):
    text = f"See PML1 §{real_ref.sec} and {real_ref.nb}."
    assert verify_text(text) == []


def test_empty_text_has_no_failures():
    assert verify_text("no citations here") == []

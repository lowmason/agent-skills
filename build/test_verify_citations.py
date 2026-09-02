"""Tests for the Gate A citation verifier. The true-negative test is the important one:
a verifier that passes everything is worse than none."""
from verify_citations import fallback_sections, verify_text


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


def test_chapter_fallback_passes_gate_a_but_is_flagged():
    # chapter 11 exists in Book 1; §11.99.99 does not — Gate A passes on the chapter (documented
    # leniency), but fallback_sections surfaces it as a Gate-B worklist item.
    text = "See PML1 §11.99.99."
    assert verify_text(text) == []
    assert "PML1 §11.99.99" in fallback_sections(text)


def test_known_good_fallback_is_not_flagged():
    # PML2 §2.2.1.4 resolves only via chapter-fallback (the sections index truncates at three
    # nesting levels) but was Gate-B verified 2026-07-20, so it is recorded as a known-good
    # exception and must not be re-listed on every run — while an ordinary fallback still is.
    text = "See PML2 §2.2.1.4 and PML1 §11.99.99."
    assert verify_text(text) == []
    flagged = fallback_sections(text)
    assert "PML2 §2.2.1.4" not in flagged
    assert "PML1 §11.99.99" in flagged


def test_directory_arg_expands_to_nested_markdown(tmp_path):
    from verify_citations import _iter_md

    (tmp_path / "a.md").write_text("x")
    sub = tmp_path / "families"
    sub.mkdir()
    (sub / "b.md").write_text("y")
    (tmp_path / "ignore.txt").write_text("z")
    found = _iter_md([str(tmp_path)])
    names = sorted(p.name for p in found)
    assert names == ["a.md", "b.md"]


def test_missing_scratch_exits_2_with_actionable_message(tmp_path, monkeypatch, capsys):
    import verify_citations

    monkeypatch.setattr(verify_citations, "SCRATCH", tmp_path / "no-such-dir")
    rc = verify_citations.main(["whatever.md"])
    assert rc == 2
    assert "extract_structure.py" in capsys.readouterr().err

"""Gate A (mechanical) citation verifier for the recommend-probabilistic-model skill.

Parses PML section refs (`PML1 §10.4`) and pyprobml notebook paths
(`notebooks/book1/foo.ipynb`) from markdown and checks each against the ground truth in
build/.scratch/ (see extract_structure.py). Exit 0 if all resolve; exit 1 + a list of
failures otherwise.

Gate A is purely mechanical: it confirms a section NUMBER exists and a notebook path exists.
It does NOT check that the section actually supports the claim attached to it — that is Gate B
(an adversarial read of the section text), a separate step in the build. Citations that resolve
only via the chapter-fallback (the exact subsection isn't in the index) are reported to stderr as
a Gate-B worklist — they're the ones most worth a human read.
"""
from __future__ import annotations

import re
import sys
from functools import lru_cache
from pathlib import Path

SCRATCH = Path(__file__).parent / ".scratch"
CITE_RE = re.compile(r"\bPML([12])\s*§\s*(\d+(?:\.\d+)*)")
NB_RE = re.compile(r"notebooks/book[12]/[^\s)`\"']+\.ipynb")


@lru_cache(maxsize=None)
def _sections(book: str) -> frozenset[str]:
    f = SCRATCH / f"book{book}_sections.tsv"
    return frozenset(ln.split("\t")[0] for ln in f.read_text().splitlines() if ln.strip())


@lru_cache(maxsize=None)
def _notebooks() -> frozenset[str]:
    return frozenset((SCRATCH / "pyprobml_files.txt").read_text().split())


def _section_status(keys: frozenset[str], ref: str) -> str:
    """'exact' if the section number is indexed; 'fallback' if only a shorter prefix is (the chapter
    exists but the exact subsection isn't in the TOC); 'fail' if not even the chapter resolves."""
    if ref in keys:
        return "exact"
    parts = ref.split(".")
    for k in range(len(parts) - 1, 0, -1):
        pref = ".".join(parts[:k])
        if pref in keys or any(s.startswith(pref + ".") for s in keys):
            return "fallback"
    return "fail"


def verify_text(text: str) -> list[str]:
    """Return a list of unresolved-citation messages (empty == all citations resolve at Gate A)."""
    failures: list[str] = []
    for book, ref in CITE_RE.findall(text):
        if _section_status(_sections(book), ref) == "fail":
            failures.append(f"unresolved section: PML{book} §{ref}")
    nbs = _notebooks()
    for nb in NB_RE.findall(text):
        if nb not in nbs:
            failures.append(f"unresolved notebook: {nb}")
    return failures


def fallback_sections(text: str) -> list[str]:
    """§refs that passed only via chapter-fallback — the exact subsection isn't indexed, so Gate A
    proved only that the chapter is real. These are the ones to confirm semantically (Gate B)."""
    seen: dict[str, None] = {}  # dedupe, preserve order
    for book, ref in CITE_RE.findall(text):
        if _section_status(_sections(book), ref) == "fallback":
            seen[f"PML{book} §{ref}"] = None
    return list(seen)


def main(argv: list[str]) -> int:
    all_fail: list[str] = []
    warnings: list[str] = []
    for p in argv:
        text = Path(p).read_text()
        all_fail += [f"{p}: {f}" for f in verify_text(text)]
        warnings += [f"{p}: {r}" for r in fallback_sections(text)]
    for f in all_fail:
        print(f)
    for w in warnings:
        print(f"WARN chapter-fallback (exact subsection not indexed; confirm via Gate B): {w}", file=sys.stderr)
    return 1 if all_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

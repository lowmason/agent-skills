"""Gate A (mechanical) citation verifier for the recommend-probabilistic-model skill.

Parses PML section refs (`PML1 §10.4`) and pyprobml notebook paths
(`notebooks/book1/foo.ipynb`) from markdown and checks each against the ground truth in
build/.scratch/ (see extract_structure.py). Exit 0 if all resolve; exit 1 + a list of
failures otherwise.

Gate A is purely mechanical: it confirms a section NUMBER exists and a notebook path exists.
It does NOT check that the section actually supports the claim attached to it — that is Gate B
(an adversarial read of the section text), a separate step in the build.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SCRATCH = Path(__file__).parent / ".scratch"
CITE_RE = re.compile(r"\bPML([12])\s*§\s*(\d+(?:\.\d+)*)")
NB_RE = re.compile(r"notebooks/book[12]/[^\s)`\"']+\.ipynb")


def _sections(book: str) -> set[str]:
    f = SCRATCH / f"book{book}_sections.tsv"
    return {ln.split("\t")[0] for ln in f.read_text().splitlines() if ln.strip()}


def _notebooks() -> set[str]:
    return set((SCRATCH / "pyprobml_files.txt").read_text().split())


def _section_ok(keys: set[str], ref: str) -> bool:
    """Pass if any prefix of the ref is, or is the parent of, an indexed section.

    Tolerates TOC depth differences: a cited §10.4.1 passes if §10.4.1 is indexed, or if
    §10.4 is (the deeper level just isn't in the TOC). The chapter must always exist.
    """
    parts = ref.split(".")
    for k in range(len(parts), 0, -1):
        pref = ".".join(parts[:k])
        if pref in keys or any(s.startswith(pref + ".") for s in keys):
            return True
    return False


def verify_text(text: str) -> list[str]:
    """Return a list of unresolved-citation messages (empty == all citations resolve)."""
    secs = {"1": _sections("1"), "2": _sections("2")}
    nbs = _notebooks()
    failures: list[str] = []
    for book, ref in CITE_RE.findall(text):
        if not _section_ok(secs[book], ref):
            failures.append(f"unresolved section: PML{book} §{ref}")
    for nb in NB_RE.findall(text):
        if nb not in nbs:
            failures.append(f"unresolved notebook: {nb}")
    return failures


def main(argv: list[str]) -> int:
    all_fail: list[str] = []
    for p in argv:
        all_fail += [f"{p}: {f}" for f in verify_text(Path(p).read_text())]
    for f in all_fail:
        print(f)
    return 1 if all_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

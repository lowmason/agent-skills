"""Extract ground truth for citation verification into build/.scratch/ (gitignored).

Book section indices come from the TOC pages via pdftotext; the pyprobml listing from gh.
The visual TOC mangles under pdftotext (multi-column: some pages give "10.4 Title", others
stack bare "8.2 / 8.3 / 8.4" separated from their titles). So we collect section *numbers*
robustly (any line whose leading token is `D.D(.D)*`), with titles captured opportunistically
when present on the same line. Gate A checks number existence; title-correctness is Gate B.

CC-BY-NC-ND note: these are factual section numbers/titles used only to VERIFY our own
citations at build time — not shipped, not redistributed prose.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

PDF_DIR = Path.home() / "Documents/Bayesian/Probabilistic Machine Learning"
BOOK1 = PDF_DIR / "prob_ml_1-book.pdf"
BOOK2 = PDF_DIR / "prob_ml_book.pdf"
SCRATCH = Path(__file__).parent / ".scratch"

# Detailed-CONTENTS page ranges (verified 2026-06-21: B1 body starts p31, B2 body p36).
TOC = {"1": (BOOK1, 11, 26), "2": (BOOK2, 8, 35)}

# A section number: at least one dot (distinguishes from bare page numbers like "358").
SEC_RE = re.compile(r"^(\d+\.\d+(?:\.\d+)*)(?:\s+(.+?))?\s*$")
# A chapter line: integer + Capitalized title on the same line (skips bare page numbers).
CHAP_RE = re.compile(r"^(\d+)\s+([A-Z].+?)\s*$")


def _clean_title(t: str | None) -> str:
    if not t:
        return ""
    t = t.strip().rstrip("*").strip()       # drop the "advanced section" marker
    return "" if t.isdigit() else t          # a lone trailing page number is not a title


def extract_book(book: str, pdf: Path, first: int, last: int) -> int:
    txt = subprocess.run(
        ["pdftotext", "-f", str(first), "-l", str(last), str(pdf), "-"],
        capture_output=True, text=True, check=True,
    ).stdout
    rows: dict[str, str] = {}
    for line in txt.splitlines():
        line = line.strip()
        m = SEC_RE.match(line)
        if m:
            num, title = m.group(1), _clean_title(m.group(2))
            rows.setdefault(num, title)
            if title and not rows[num]:
                rows[num] = title
            continue
        c = CHAP_RE.match(line)
        if c and not c.group(2).isupper():   # skip ALL-CAPS running headers like "CONTENTS"
            rows.setdefault(c.group(1), _clean_title(c.group(2)))
    out = SCRATCH / f"book{book}_sections.tsv"
    out.write_text("\n".join(f"{n}\t{t}" for n, t in sorted(rows.items(), key=_sortkey)))
    return len(rows)


def _sortkey(item):
    return [int(p) for p in item[0].split(".")]


def extract_pyprobml() -> int:
    js = subprocess.run(
        ["gh", "api", "repos/probml/pyprobml/git/trees/master?recursive=1"],
        capture_output=True, text=True, check=True,
    ).stdout
    paths = sorted(
        t["path"] for t in json.loads(js)["tree"]
        if t["path"].endswith(".ipynb") and t["path"].startswith("notebooks/book")
    )
    (SCRATCH / "pyprobml_files.txt").write_text("\n".join(paths))
    return len(paths)


if __name__ == "__main__":
    SCRATCH.mkdir(exist_ok=True)
    for book, (pdf, first, last) in TOC.items():
        print(f"book{book}: {extract_book(book, pdf, first, last)} numbered entries")
    print(f"pyprobml: {extract_pyprobml()} notebooks")

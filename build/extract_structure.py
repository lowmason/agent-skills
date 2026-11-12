'''Extract ground truth for citation verification into build/.scratch/ (gitignored).

Book section indices come from the detailed-contents pages, read with `pdftotext -layout`,
which keeps each entry's number, title and page on one line; the pyprobml listing comes
from gh. A contents page range that starts late drops whole chapters without an error:
until 2026-11-12, Book 1's range began two pages after its contents and lost chapters 1
and 2. So `check_complete` refuses a parse whose chapters do not run from 1 without a gap,
or that leaves an entry without a title. Gate A checks number existence; title-correctness
is Gate B.

CC-BY-NC-ND note: these are factual section numbers/titles used only to VERIFY our own
citations at build time — not shipped, not redistributed prose.
'''
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

PDF_DIR = Path.home() / 'Library/Mobile Documents/com~apple~CloudDocs/PDFs/Books/Machine Learning'
BOOK1 = PDF_DIR / 'Probabilistic Machine Learning - An Introduction (Murphy).pdf'
BOOK2 = PDF_DIR / 'Probabilistic Machine Learning - Advanced Topics (Murphy).pdf'
SCRATCH = Path(__file__).parent / ".scratch"

# PDF pages of the detailed contents, and of the first body page (chapter 1), in the builds
# dated 2025-04-18 (Book 1, 860 pages) and 2025-12-10 (Book 2, 1,370 pages); verified
# 2026-11-12. A new build can move them: check_complete catches a contents range that
# misses a page, and a body start that is late cuts the start of chapter 1 from the dump.
TOC = {'1': (BOOK1, 9, 25), '2': (BOOK2, 9, 29)}
BODY_START = {'1': 31, '2': 35}

# One contents entry under `pdftotext -layout`: the number, the title, then the page.
TOC_LINE_RE = re.compile(r'^\s*(\d+(?:\.\d+)*)\s+(\S.*?)\s+\d+\s*$')
ADVANCED_MARK = '*'


def parse_toc(text: str) -> dict[str, str]:
    '''Map each section number in a `pdftotext -layout` contents dump to its title.

    A line counts only when it starts with a section number and ends with an arabic page
    number, so front-matter lines (`Preface  xxvii`) and page footers drop out. The
    advanced-section marker is removed from a title, and a repeated number keeps its
    first title.
    '''
    rows: dict[str, str] = {}
    for line in text.splitlines():
        m = TOC_LINE_RE.match(line)
        if m:
            rows.setdefault(m.group(1), m.group(2).removesuffix(ADVANCED_MARK).strip())
    return rows


def check_complete(rows: dict[str, str]) -> None:
    '''Raise ValueError unless the chapters run from 1 with no gap, every section's
    chapter is present, and every entry has a title.'''
    if not rows:
        raise ValueError('no contents entries parsed: check the contents page range')
    chapters = {int(n) for n in rows if '.' not in n}
    problems = []
    missing = sorted(set(range(1, max(chapters, default=0) + 1)) - chapters)
    if missing:
        problems.append(f'chapters missing: {", ".join(map(str, missing))}')
    orphans = [n for n in rows if '.' in n and int(n.split('.')[0]) not in chapters]
    if orphans:
        problems.append(f'sections whose chapter is absent: {", ".join(orphans)}')
    untitled = [n for n, title in rows.items() if not title]
    if untitled:
        problems.append(f'entries with no title: {", ".join(untitled)}')
    if problems:
        raise ValueError('; '.join(problems))


def extract_book(book: str, pdf: Path, first: int, last: int) -> int:
    txt = subprocess.run(
        ['pdftotext', '-layout', '-f', str(first), '-l', str(last), str(pdf), '-'],
        capture_output=True, text=True, check=True,
    ).stdout
    rows = parse_toc(txt)
    try:
        check_complete(rows)
    except ValueError as err:
        raise ValueError(f'book{book}, contents pages {first}-{last} of {pdf.name}: {err}') from err
    out = SCRATCH / f'book{book}_sections.tsv'
    out.write_text('\n'.join(f'{n}\t{t}' for n, t in sorted(rows.items(), key=_sortkey)))
    return len(rows)


def _sortkey(item):
    return [int(p) for p in item[0].split(".")]


def extract_fulltext() -> dict[str, int]:
    """Dump full book text to scratch so build agents can grep a section's content for
    accurate (original-wording) summaries and for Gate B's semantic verification — robust
    to the TOC's page-number mangling. Gitignored; CC-BY-NC-ND own-use extraction only."""
    # Start at the body (skip front matter + TOC) so a section heading's first match in the
    # dump is its real occurrence, not its table-of-contents line.
    sizes = {}
    for book, pdf in (("1", BOOK1), ("2", BOOK2)):
        out = SCRATCH / f"book{book}_full.txt"
        subprocess.run(['pdftotext', '-f', str(BODY_START[book]), str(pdf), str(out)], check=True)
        sizes[book] = out.stat().st_size
    return sizes


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
    ft = extract_fulltext()
    print(f"full text: book1 {ft['1'] // 1024} KB, book2 {ft['2'] // 1024} KB")
    print(f"pyprobml: {extract_pyprobml()} notebooks")

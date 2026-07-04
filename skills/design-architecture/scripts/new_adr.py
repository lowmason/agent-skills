#!/usr/bin/env python3
"""Scaffold a new numbered ADR file.

Scans the target directory for the highest ``NNNN-`` prefix, increments it, slugifies the
title, and writes the standard ADR template with today's date filled in. Never overwrites an
existing file. Numbering is permanent and never reused.

Usage:
    python3 ~/.claude/skills/design-architecture/scripts/new_adr.py "Use NumPyro/JAX over PyMC for nowcasting"
    python3 ~/.claude/skills/design-architecture/scripts/new_adr.py "Store parquet levels only" --dir docs/adr --status Proposed

The default directory is ``specs/adr`` (the design-record convention in this stack); pass
``--dir docs/adr`` for repos that publish ADRs in a MkDocs site.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

TEMPLATE = """# {number:04d}. {title}

- **Status:** {status}
- **Date:** {date}
- **Deciders:**
- **Blast radius:**

## Context

The forces at play: the problem, the constraints, what is and isn't known *as of this date*.
State the constraints that actually drive the choice. This section is frozen once Accepted.

## Decision

We will <do X>. One decision per ADR.

## Consequences

- **Positive:**
- **Negative:**
- **Neutral / follow-on:**

## Alternatives considered

- **<Option A>** — rejected because <concrete trade-off>.
- **<Option B>** — rejected because <concrete trade-off>.

## Trade-offs & reversibility

What you're trading, and how expensive a reversal would be (one-way vs two-way door). Note what
would trigger a revisit (a superseding ADR).
"""

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")
_NNNN = re.compile(r"^(\d{4,})-")
VALID_STATUS = {"Proposed", "Accepted", "Deprecated"}


def slugify(title: str) -> str:
    slug = _SLUG_STRIP.sub("-", title.lower()).strip("-")
    return slug or "adr"


def next_number(directory: Path) -> int:
    highest = 0
    if directory.exists():
        for entry in directory.iterdir():
            match = _NNNN.match(entry.name)
            if match:
                highest = max(highest, int(match.group(1)))
    return highest + 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold a new numbered ADR.")
    parser.add_argument("title", help="Short imperative title: the decision, not the problem.")
    parser.add_argument(
        "--dir",
        default="specs/adr",
        help="Target directory (default: specs/adr; use docs/adr for MkDocs repos).",
    )
    parser.add_argument(
        "--status",
        default="Proposed",
        choices=sorted(VALID_STATUS),
        help="Initial status (default: Proposed).",
    )
    args = parser.parse_args(argv)

    directory = Path(args.dir)
    directory.mkdir(parents=True, exist_ok=True)

    number = next_number(directory)
    path = directory / f"{number:04d}-{slugify(args.title)}.md"
    if path.exists():  # defensive: should not happen given next_number, but never clobber
        print(f"refusing to overwrite existing file: {path}", file=sys.stderr)
        return 1

    path.write_text(
        TEMPLATE.format(
            number=number,
            title=args.title,
            status=args.status,
            date=_dt.date.today().isoformat(),
        ),
        encoding="utf-8",
    )
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

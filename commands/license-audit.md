---
description: Audit the current repo's licensing and attribution — run its mechanical gates where present, then judgment checks on NOTICE/LICENSE sync, license compatibility, and uncredited-adaptation risks. Read-only — reports findings, never edits.
disable-model-invocation: true
---

Audit licensing and attribution in the current repo. Read-only: report
findings; never edit files.

**Layer 1 — mechanical.** Run the repo's own provenance gates when
present (in agent-skills: `build/check_provenance.py` and
`build/check_frontmatter.py`). Otherwise scan `pyproject.toml` /
`uv.lock` (or the ecosystem equivalent) and report each dependency's
license.

**Layer 2 — judgment.** Check what no script can:

- NOTICE ↔ artifact sync: every skill, agent, and command accounted for
  (original works may be covered by a blanket statement; adaptations
  need their own entry).
- LICENSE file present and consistent with what NOTICE and the README
  claim.
- License-compatibility flags: copyleft or NC-licensed material in an
  MIT repo.
- Attribution invariants recorded in NOTICE/CLAUDE.md still hold (e.g.
  no-book-prose rules; nothing from gitignored extraction dirs
  committed).
- Uncredited-adaptation risks: files whose content or git history points
  at an external source absent from NOTICE.

Report findings grouped by layer, each with file references and a
proposed resolution; end with an overall verdict.

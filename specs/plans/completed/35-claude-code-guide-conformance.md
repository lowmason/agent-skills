# Claude Code Guide Conformance Implementation Plan

**Status: COMPLETE (2026-10-04)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Where this runs.** This plan is committed on local `main` and is not pushed.
> `EnterWorktree` bases on `origin/main`, which lacks it, so create the worktree by
> hand from the main checkout (Global Constraints, "Worktree") and execute there:
> `/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance`,
> branch `feat/cc-guide-conformance`. Every command below `cd`s to that absolute path.

**Goal:** Anchor the repo's Claude Code artifacts to `specs/guides/claude-code-customization-guide.md`. The plan adds drift's 38 section anchors to the guide, a hand-edited register mapping sections to artifact kinds, checks and exceptions, a lint with seven mechanical checks and both-way waivers, and a one-time audit whose owner-decided findings fill the register. It ends with the CLAUDE.md authoring rule and R6's amendments to the drift and portability specs.

**Architecture:** `build/check_conformance.py` is a stdlib + PyYAML lint, separate from `check_frontmatter.py` (Decision 15). It reads `build/cc_guide/conformance.toml` (TOML via `tomllib`) and the anchored guide. It matches each kind's root-anchored globs against the files git keeps, runs the seven checks, and validates the register's integrity. It then waives violations through `[[exception]]` entries that must match both ways. Tasks 1–7 build the lint test-first in seven red→green cycles. Task 8 is a four-seat read-only audit, and Task 9 is the owner gate. Tasks 10–11 settle CLAUDE.md's length and fill the register, so the lint goes green. Task 12 is R4, Task 13 is R6, and Task 14 validates.

**Tech Stack:** Python 3.13 through `uv run` with inline deps; `tomllib`; PyYAML; pytest; `git ls-files`; Markdown and TOML. There is no CI — the gates are the lints in the root `CLAUDE.md` Commands block.

**Spec:** `specs/claude-code-guide-conformance.md` (APPROVED 2026-10-04, R6's amendments included; the completion protocol moves it to `specs/completed/`). R1–R6, "Decision N" and "Validation item N" below point into it.

## Global Constraints

Every task's requirements implicitly include this section.

- **Order (spec, Sequencing):** R1 anchors (Task 1) → register skeleton and R3 test-first (Tasks 2–7) → R5 audit (Task 8) → owner gate (Task 9) → CLAUDE.md catch-up trim, only if the gate chose it (Task 10) → finish the register, lint green (Task 11) → R4 (Task 12) → R6 (Task 13) → validation (Task 14). Task 10 exists because the JAX merge (PR #20) landed before this plan, leaving CLAUDE.md at 238 lines on `main` `54fc246`, over the 225 the spec measured. The spec's Sequencing section gives whichever of the two lands second the duty to trim or deliberately raise the ceiling, so this plan carries it.
- **Worktree.** Before creating it, run `git -C /Users/lowell/Projects/agent-skills rev-parse main origin/main` and confirm `main` holds this plan's commit. Create it from the main checkout with `git -C /Users/lowell/Projects/agent-skills worktree add .claude/worktrees/plan-35-cc-guide-conformance -b feat/cc-guide-conformance main`, never with `EnterWorktree`. `.claude/worktrees/` is gitignored. Commit only from the worktree. Every commit command begins with `[ "$(git branch --show-current)" = feat/cc-guide-conformance ] &&`, so a wrong branch or a detached HEAD stops the chain, with exit 1, before anything is staged: concurrent sessions switch the shared checkout. Keep the single `=`; zsh rejects `==` there.
- **Baseline and counts.** Before Task 1, run the build suite in the worktree (`cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q`) and record its counts in the SDD ledger (`progress.md` in the workspace). The controller passes them in the dispatch of every task that compares against the baseline (Tasks 1, 7, 11 and 12). A worktree lacks the gitignored `build/.scratch/`, so the 4 ground-truth tests in `test_verify_citations.py` fail there. On `54fc246`, `test_check_provenance.py::test_real_notice_originals_has_sixteen_entries` also fails (`assert 19 == 16`: the JAX merge took NOTICE to 19 originals). That is a pre-existing bug outside this plan, which does not fix it. A separate task chip was offered to the owner, so the baseline may already show it fixed. Every expected change below is a **+N delta over that baseline**. The plan adds +81 tests in total: +2 in `build/test_fences.py` and +79 in `build/test_check_conformance.py`. The outcomes quoted for `test_check_conformance.py` run alone are exact, because this plan creates that file. Outcomes for `test_fences.py`, which exists, are deltas over its baseline.
- **Test-first (R3.5, Validation item 2).** Each lint task writes its tests, runs them, and reconciles the run against the step's prediction before writing code: the failed/passed counts, and each failure's cause. The predictions were observed in a throwaway clone of `54fc246` while this plan was written. A test that passes at its RED step is a plan defect: fix the assertion so it fails for the stated reason, and record a `> Deviation:`.
- **Test conventions.** `build/test_check_conformance.py` imports the module once, as `import check_conformance as cc`, and every test reaches names through `cc.`. A name a later task adds then fails as one `AttributeError` per test, never as a collection error. Violation lines are compared with exact equality, never substrings. Fixtures are hand-written in the test file and never copied from docs pages. Fixture repos are `git init`-ed in `tmp_path` with `cc.git_env()`.
- **Python style** (`CLAUDE.md`, `rules/clean-code-python.md`). Single quotes, with double quotes only around a string that itself contains single quotes. 4-space indent, matching `check_frontmatter.py`. `'''` docstrings. Stdlib plus PyYAML only, Python 3.13 (`PurePath.full_match` needs 3.13).
- **Lint contract (R3.1–R3.3).** `build/check_conformance.py` finds the repo from its own location (`REPO`), never the working directory. Its register is `build/cc_guide/conformance.toml` (`REGISTER`). Exit 0 means clean. Exit 1 prints one stdout line per violation, `<file>: <check> (<section>): <message>`, sorted. Exit 2 means the guide or register is missing or not TOML, or git cannot list the files. `<section>` is one ID, several joined with `, `, or `-`. The integrity rules use these check names: `anchor`, `register`, `section-id`, `section-map`, `check-impl`, `duplicate-id`, `exception`, `stale-waiver` and `ceiling`.
- **Finding files (R2.3).** A kind's globs are root-anchored and matched with `PurePosixPath.full_match` against the files git keeps (`git ls-files --cached --others --exclude-standard -z`, as `install.py`'s `kept_files`). Never search recursively: no `**/SKILL.md`, no `rglob`, no `os.walk`. `specs/verification/32-jax-trials/` holds four tracked `SKILL.md` trial copies that must never count as skills. Task 3's repo test pins the skill, agent and command kinds to `check_frontmatter.py`'s directory listings.
- **No citation lines (R2.8, R3.6, R6 D3).** This plan lands before drift Stage 2, which adds the register's and the lint's `cc-guide:` lines. Keep any line that begins, after indentation, with `# cc-guide:` or `<!-- cc-guide:` out of every file this plan writes, fixtures and comments included. Drift's R5 lint will scan for them.
- **Scope fence — this plan fixes nothing it finds (Decision 16):**
  - No edits to any skill, agent or command file, `hooks/`, `rules/`, `.claude/settings.json`, `install.py`, `build/check_frontmatter.py`, `runtimes/`, or the four files outside the repo.
  - CLAUDE.md changes only in Task 10 (if the gate chose it) and Task 12. The guide changes only by Task 1's 38 anchor lines.
  - Line 25 of `skills/writing-skills/SKILL.md` and `skills/writing-skills/anthropic-best-practices.md` stay out of every task, the audit included: their provenance is the owner's call.
  - `specs/audit-3-10-26.md`'s D13 (stale branch names in the drift spec) is fixed before drift Stage 1 is planned, not in Task 13.
  - A finding on a fenced file goes to the final review and the completion gate; it is never fixed in passing.
- **R6 needs no further approval** (spec header). Task 13 applies D1–D5 and P1–P3 as written and leaves both specs' status lines untouched. The portability spec's header still reads "written spec awaiting review"; apply P1–P3 to it anyway.
- **Path to the spec from new files:** `specs/completed/claude-code-guide-conformance.md`, where the completion protocol moves it on this branch. The register, the lint's docstring and Task 13's amendments cite that path. Do not "fix" it to `specs/…`. The audit report stays at `specs/claude-code-conformance-audit-<YYYY-MM-DD>.md` (R5.4) and is not retired.
- **Unmerged branches need no rules here.**
  - `codex/recommend-causal-design` adds a 36th skill and +1 CLAUDE.md line. The skill kind's glob picks the skill up, and no check runs on skills.
  - `worktree-deferred-triage-2026-10-03` adds +3 CLAUDE.md lines and changes about 225 lines of `specs/deferred_items.md`. Its `hooks/README.md` edits are prose, and they leave the three unquoted JSON lines that `hook-dir-unquoted` waives intact.
  - Both branches meet this plan only through CLAUDE.md length, which Task 9 measures for the owner, and the deferred-items tail, a merge-time conflict. Tasks 10 and 12 trim only CLAUDE.md regions neither branch edits. The exception is the build-suite counts, which R4 must change.
- **Audit seats (R5.2, Task 8).** The seats are four `code-reviewer` subagents, each dispatched with `model: 'sonnet'` set explicitly; the agent's frontmatter pins Opus. `code-reviewer` reviews work "against its plan or requirements", which is the audit's shape. Explore's body says it does not review or audit, and task-reviewer is diff-scoped and told not to crawl the codebase. All four run under the read-only guard, so they get single-line Bash only: no `\` continuations, with single-quoted inline code. Implementer subagents cannot dispatch subagents, so Tasks 8, 9 and 14 are controller tasks.
- **Nothing outward-facing.** No push, PR, issue or post.
- **Anchor on text, not line numbers.** Line numbers are as of `54fc246`, for orientation only. Every edit gives its exact old text. Never regress an existing test: everything green at the baseline stays green at every commit.

---

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `specs/guides/claude-code-customization-guide.md` | Gains 38 `<!-- cc: <id> -->` lines, one under each `##`/`###` heading, with drift R1.1's IDs. No other edit. | 1 |
| `build/fences.py` | Gains `fenced_lines(text) -> set[int]`, the existing closing rule exposed as line numbers. Existing functions untouched. | 1 |
| `build/test_fences.py` | +2 tests for `fenced_lines`. | 1 |
| `build/check_conformance.py` | New. The lint (R3). It grows by task: guide parsing (1); register loading, shape and section integrity (2); file discovery and the agent checks (3); the hook checks (4); the CLAUDE.md and rule checks (5); the check registry, `run` and `main` (6); exceptions and waivers (7). About 790 lines. | 1–7 |
| `build/test_check_conformance.py` | New. +79 tests across Tasks 1–7 and 11. | 1–7, 11 |
| `build/cc_guide/conformance.toml` | New. The register (R2): the skeleton in Task 2, the exceptions and any map changes in Task 11. Edited by hand; no script writes it. | 2, 11 |
| `specs/claude-code-conformance-audit-<YYYY-MM-DD>.md` | New. The audit record (R5.4). Its owner-decisions section is filled at the gate. | 8, 9 |
| `CLAUDE.md` | The lossless catch-up trim, only if the gate chose it (10). Then the authoring rule, the lint command, a net-zero trim and the build-suite count deltas (12). | 10, 12 |
| `specs/claude-code-drift-automation.md` | R6 D1–D5. | 13 |
| `specs/agent-skills-portability.md` | R6 P1–P3. | 13 |
| `specs/deferred_items.md` | This plan's deferred items. **Completion protocol only.** | — |

Scratch files (`insert_anchors.py`, `regrep.py`, `words_unchanged.py`, the audit's quote TSV) live under the worktree's gitignored `.sdd/35-claude-code-guide-conformance/` and are never committed.

---

### Task 1: Guide anchors and their parser (R1)

**Files:**
- Modify: `build/fences.py` (append `fenced_lines`)
- Modify: `build/test_fences.py` (append 2 tests)
- Create: `build/check_conformance.py`
- Create: `build/test_check_conformance.py`
- Modify: `specs/guides/claude-code-customization-guide.md` (38 inserted lines, nothing else)

**Interfaces:**
- Consumes: `fences.FENCE_OPEN_RE` (existing).
- Produces:
  - `fences.fenced_lines(text: str) -> set[int]`: the 1-based numbers of every line that opens, closes or sits inside a fenced block.
  - `check_conformance.REPO: Path`.
  - `HEADING_RE`, `ANCHOR_RE` and `ANCHOR_LIKE_RE`.
  - `class Section(NamedTuple): line: int; heading: str; id: str | None`.
  - `class Violation(NamedTuple): file: str; check: str; section: str; message: str; value: int | None = None; waivable: bool = True`, with `render() -> str` returning `'<file>: <check> (<section>): <message>'`. `waivable` is False when a check could not evaluate the file; Task 7's waivers never hide such a violation.
  - `guide_sections(text: str, path: str) -> tuple[list[Section], list[Violation]]`.

- [x] **Step 1: Write the failing fence tests.** Append to `build/test_fences.py`:

````python
def test_fenced_lines_cover_opener_body_and_closer():
    text = '# Title\n```bash\n# not a heading\n```\n## After\n'
    assert fences.fenced_lines(text) == {2, 3, 4}


def test_fenced_lines_follow_the_closing_rule():
    '''A ``` line inside a ````markdown fence is content: only the four-backtick
    line closes it, so lines 1-5 are fenced and line 6 is not.'''
    text = '````markdown\n```python\nx = 1\n```\n````\nafter\n'
    assert fences.fenced_lines(text) == {1, 2, 3, 4, 5}
````

- [x] **Step 2: Write the failing conformance tests.** Create `build/test_check_conformance.py`:

````python
'''Tests for check_conformance.py, the Claude Code guide conformance lint.

Fixture trees are hand-written per test. The R1.2 pin and the repo tests read
the real guide and register.
'''
import check_conformance as cc

GUIDE = 'specs/guides/claude-code-customization-guide.md'
FENCE = '`' * 3

# The 38 section IDs of the drift spec's R1.1 table, in heading order
# (specs/claude-code-drift-automation.md). Pinned here as R1.2's oracle; the
# lint itself validates the register against the guide's anchors, never
# against this list.
R11_IDS = [
    'context.overview', 'mechanisms.overview',
    'skills.overview', 'skills.locations', 'skills.frontmatter',
    'skills.description', 'skills.listing-budget',
    'skills.progressive-disclosure', 'skills.arguments', 'skills.iterating',
    'commands.overview',
    'subagents.overview', 'subagents.frontmatter', 'subagents.tools',
    'subagents.models', 'subagents.isolation',
    'rules.overview', 'rules.claude-md', 'rules.hierarchy',
    'rules.rules-files', 'rules.auto-memory', 'rules.settings',
    'hooks.overview', 'hooks.events', 'hooks.exit-codes', 'hooks.handlers',
    'hooks.configuration', 'hooks.patterns', 'hooks.pitfalls',
    'lean.overview', 'lean.measure', 'lean.session-hygiene', 'lean.caching',
    'lean.model-routing', 'lean.mcp', 'lean.ceremony', 'lean.expensive-ops',
    'reading.overview',
]


def rendered(violations):
    return [v.render() for v in violations]


def test_heading_inside_a_fence_is_not_a_heading():
    text = ('# Guide\n\n## A\n<!-- cc: a.overview -->\n\n'
            f'{FENCE}bash\n## not a heading\n{FENCE}\n')
    sections, violations = cc.guide_sections(text, 'guide.md')
    assert [(s.line, s.id) for s in sections] == [(3, 'a.overview')]
    assert violations == []


def test_heading_without_an_anchor_is_a_violation():
    text = '## A\n<!-- cc: a.overview -->\n### B\nbody\n'
    sections, violations = cc.guide_sections(text, 'guide.md')
    assert [s.id for s in sections] == ['a.overview', None]
    assert rendered(violations) == [
        "guide.md: anchor (-): line 3: heading '### B' has no anchor on its next line"]


def test_malformed_anchor_is_a_violation():
    text = '## A\n<!-- cc: A_Overview -->\n'
    sections, violations = cc.guide_sections(text, 'guide.md')
    assert [s.id for s in sections] == [None]
    assert rendered(violations) == [
        "guide.md: anchor (-): line 2: malformed anchor '<!-- cc: A_Overview -->'"]


def test_anchor_not_directly_under_a_heading_is_a_violation():
    text = '## A\n<!-- cc: a.overview -->\n<!-- cc: a.extra -->\n'
    _, violations = cc.guide_sections(text, 'guide.md')
    assert rendered(violations) == [
        'guide.md: anchor (-): line 3: anchor is not directly under a heading']


def test_repeated_anchor_id_is_a_violation():
    text = '## A\n<!-- cc: a.one -->\n## B\n<!-- cc: a.one -->\n'
    sections, violations = cc.guide_sections(text, 'guide.md')
    assert [s.id for s in sections] == ['a.one', None]
    assert rendered(violations) == [
        'guide.md: anchor (a.one): line 4: anchor repeats line 2']


def test_real_guide_carries_the_drift_r11_anchors():
    '''R1.2: 38 headings outside fences, each followed by exactly one
    well-formed anchor, whose IDs in heading order equal drift's R1.1 table.'''
    text = (cc.REPO / GUIDE).read_text()
    sections, violations = cc.guide_sections(text, GUIDE)
    assert len(sections) == 38
    assert rendered(violations) == []
    assert [s.id for s in sections] == R11_IDS
````

- [x] **Step 3: Run both files; confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest python -m pytest -q test_fences.py`
Expected: `2 failed`, each `AttributeError: module 'fences' has no attribute 'fenced_lines'`; the file's baseline tests still pass.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `1 error during collection`: `ModuleNotFoundError: No module named 'check_conformance'`.

- [x] **Step 4: Implement `fenced_lines`.** Append to `build/fences.py`:

```python
def fenced_lines(text: str) -> set[int]:
    '''1-based numbers of the lines that open, close, or sit inside a fenced block.

    Same matching rule as strip_fenced_blocks; an unclosed fence runs to the end.
    '''
    out: set[int] = set()
    open_len: int | None = None
    for i, line in enumerate(text.split('\n'), start=1):
        if open_len is None:
            m = FENCE_OPEN_RE.match(line)
            if m:
                open_len = len(m.group(1))
                out.add(i)
            continue
        out.add(i)
        stripped = line.strip()
        if stripped.startswith('`' * open_len) and set(stripped) == {'`'}:
            open_len = None
    return out
```

- [x] **Step 5: Create `build/check_conformance.py`** with exactly:

````python
#!/usr/bin/env python3
'''Claude Code guide conformance lint.

Checks the repo's Claude Code artifacts against the register,
build/cc_guide/conformance.toml, which maps each anchored section of
specs/guides/claude-code-customization-guide.md to the artifact kinds it
governs, to mechanical checks, and to recorded exceptions. Design:
specs/completed/claude-code-guide-conformance.md.
'''
import re
from pathlib import Path
from typing import NamedTuple

from fences import fenced_lines

REPO = Path(__file__).resolve().parent.parent
# A ## or ### ATX heading. The guide's sections are exactly these (drift R1.1).
HEADING_RE = re.compile(r'^#{2,3}[ \t]')
# A well-formed anchor: two or more dot-separated [a-z0-9-] segments.
ANCHOR_RE = re.compile(r'^<!-- cc: ([a-z0-9-]+(?:\.[a-z0-9-]+)+) -->$')
# Anything meant as an anchor, well-formed or not. `cc-guide:` (drift's
# citation and stamp markers) does not match: `cc` must be followed by `:`.
ANCHOR_LIKE_RE = re.compile(r'^<!--\s*cc:')


class Section(NamedTuple):
    line: int  # 1-based line of the heading
    heading: str
    id: str | None  # None when the heading has no well-formed, unique anchor


class Violation(NamedTuple):
    file: str
    check: str
    section: str  # a section ID, several joined by ', ', or '-'
    message: str
    value: int | None = None  # the measured number, for a numeric check
    waivable: bool = True  # False when the check could not evaluate the file

    def render(self) -> str:
        return f'{self.file}: {self.check} ({self.section}): {self.message}'


def guide_sections(text: str, path: str) -> tuple[list[Section], list[Violation]]:
    '''The guide's ## and ### headings outside fenced code, each with the ID of
    the anchor on its next line, plus one violation per missing, malformed,
    stray or repeated anchor (R1.1, R3.3 rule 1).'''
    lines = text.split('\n')
    fenced = fenced_lines(text)
    sections: list[Section] = []
    out: list[Violation] = []
    under_heading: set[int] = set()
    first_line: dict[str, int] = {}
    for n, line in enumerate(lines, start=1):
        if n in fenced or not HEADING_RE.match(line):
            continue
        nxt = lines[n] if n < len(lines) else ''
        anchor = None
        m = ANCHOR_RE.match(nxt)
        if m:
            under_heading.add(n + 1)
            if m.group(1) in first_line:
                out.append(Violation(path, 'anchor', m.group(1),
                                     f'line {n + 1}: anchor repeats line {first_line[m.group(1)]}'))
            else:
                first_line[m.group(1)] = n + 1
                anchor = m.group(1)
        elif ANCHOR_LIKE_RE.match(nxt):
            under_heading.add(n + 1)
            out.append(Violation(path, 'anchor', '-', f'line {n + 1}: malformed anchor {nxt.strip()!r}'))
        else:
            out.append(Violation(path, 'anchor', '-',
                                 f'line {n}: heading {line.strip()!r} has no anchor on its next line'))
        sections.append(Section(n, line.strip(), anchor))
    for n, line in enumerate(lines, start=1):
        if n not in fenced and n not in under_heading and ANCHOR_LIKE_RE.match(line):
            out.append(Violation(path, 'anchor', '-', f'line {n}: anchor is not directly under a heading'))
    return sections, out
````

- [x] **Step 6: Run both files; only the real-guide pin is red.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest python -m pytest -q test_fences.py`
Expected: no failures; passed is the file's baseline +2.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `1 failed, 5 passed`. The failure is `test_real_guide_carries_the_drift_r11_anchors`: `rendered(violations) == []` fails with 38 items. The first is `specs/guides/claude-code-customization-guide.md: anchor (-): line 7: heading '## 1. The organizing constraint: context' has no anchor on its next line`.

- [x] **Step 7: Insert the anchors.** Create `.sdd/35-claude-code-guide-conformance/insert_anchors.py` (the directory is gitignored). It refuses to write unless the guide's 38 headings match R1.1's section texts in order:

```python
'''One-off for plan 35 Task 1: add drift R1.1's anchors to the guide.

Run from the worktree root. Not committed. Each pair is (heading text without
the leading #s, ID), in R1.1's order; the script refuses to write unless the
guide's 38 headings outside fences match these texts exactly.
'''
import sys
from pathlib import Path

sys.path.insert(0, 'build')
from fences import fenced_lines  # noqa: E402

PAIRS = [
    ('1. The organizing constraint: context', 'context.overview'),
    ('2. Choosing the right mechanism', 'mechanisms.overview'),
    ('3. Skills', 'skills.overview'),
    ('Where skills live', 'skills.locations'),
    ('Frontmatter reference ⚠', 'skills.frontmatter'),
    ('The description is the router', 'skills.description'),
    ('The listing budget ⚠', 'skills.listing-budget'),
    ('Progressive disclosure', 'skills.progressive-disclosure'),
    ('Arguments and dynamic context', 'skills.arguments'),
    ('Iterating on skills', 'skills.iterating'),
    ('4. Slash commands', 'commands.overview'),
    ('5. Subagents', 'subagents.overview'),
    ('Frontmatter reference ⚠', 'subagents.frontmatter'),
    ('Scope tools to the role', 'subagents.tools'),
    ('Route models by role', 'subagents.models'),
    ('Isolation mechanics — and when delegation pays', 'subagents.isolation'),
    ('6. Rules: CLAUDE.md, rules files, settings, permissions', 'rules.overview'),
    ('CLAUDE.md discipline', 'rules.claude-md'),
    ('Hierarchy and loading', 'rules.hierarchy'),
    ('Rules files', 'rules.rules-files'),
    ('Auto memory', 'rules.auto-memory'),
    ('Settings precedence and permission rules', 'rules.settings'),
    ('7. Hooks', 'hooks.overview'),
    ('Events ⚠', 'hooks.events'),
    ('Exit codes and JSON control', 'hooks.exit-codes'),
    ('Handler types ⚠', 'hooks.handlers'),
    ('Configuration', 'hooks.configuration'),
    ('Patterns', 'hooks.patterns'),
    ('Pitfalls', 'hooks.pitfalls'),
    ('8. Running lean: the token-budget playbook', 'lean.overview'),
    ('Know your numbers first', 'lean.measure'),
    ('Session hygiene', 'lean.session-hygiene'),
    ("Caching: automatic, but don't fight it", 'lean.caching'),
    ('Model routing', 'lean.model-routing'),
    ('MCP hygiene', 'lean.mcp'),
    ('Scale ceremony to task size', 'lean.ceremony'),
    ('Guard expensive operations', 'lean.expensive-ops'),
    ('Further reading', 'reading.overview'),
]

path = Path('specs/guides/claude-code-customization-guide.md')
text = path.read_text()
lines = text.split('\n')
fenced = fenced_lines(text)
heads = [n for n, line in enumerate(lines, start=1)
         if n not in fenced and line.startswith(('## ', '### '))]
found = [lines[n - 1].lstrip('#').strip() for n in heads]
expected = [heading for heading, _ in PAIRS]
if found != expected:
    sys.exit(f'headings differ from R1.1:\n  found    {found}\n  expected {expected}')
if any(lines[n].startswith('<!-- cc:') for n in heads):
    sys.exit('the guide already carries anchors; nothing written')
for n, (_, sid) in reversed(list(zip(heads, PAIRS))):
    lines.insert(n, f'<!-- cc: {sid} -->')
path.write_text('\n'.join(lines))
print(f'inserted {len(PAIRS)} anchors')
```

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && uv run --python 3.13 python .sdd/35-claude-code-guide-conformance/insert_anchors.py`
Expected: `inserted 38 anchors`. A second run prints `the guide already carries anchors; nothing written` and changes nothing.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && git diff --numstat -- specs/guides/`
Expected: `38	0	specs/guides/claude-code-customization-guide.md`: 38 insertions and no deletions (R1.1: no other edit to the guide).

- [x] **Step 8: Run the new file again; all green.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `6 passed`. With Step 6's `test_fences.py` run, the build suite is now +8 over baseline: +2 in `test_fences.py` and +6 in `test_check_conformance.py`.

- [x] **Step 9: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && [ "$(git branch --show-current)" = feat/cc-guide-conformance ] && git add build/fences.py build/test_fences.py build/check_conformance.py build/test_check_conformance.py specs/guides/claude-code-customization-guide.md && git commit -m "feat(build): anchor the Claude Code guide's 38 sections

Adds drift R1.1's <!-- cc: <id> --> anchor under each ## and ### heading
of the customization guide (no other edit), fences.fenced_lines, and the
first slice of build/check_conformance.py, which parses headings and
anchors outside fenced code. The R1.2 test pins the 38 IDs in order.

Plan 35, Task 1.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Register skeleton, loading and section integrity (R2.1–R2.5, R3.3 rule 1)

**Files:**
- Create: `build/cc_guide/conformance.toml`
- Modify: `build/check_conformance.py` (imports; one constant; append the register layer)
- Modify: `build/test_check_conformance.py` (imports; append the fixtures and 10 tests)

**Interfaces:**
- Consumes (Task 1): `Violation`, `guide_sections(text, path)`, `REPO`.
- Produces:
  - `REGISTER = 'build/cc_guide/conformance.toml'`.
  - `class SetupError(Exception)`.
  - `class Kind(NamedTuple): globs: list[str]; exclude: list[str]; sections: list[str]`.
  - `class Check(NamedTuple): id: str; kinds: list[str]; sections: list[str]; enforced_by: str; params: dict`.
  - `class Register(NamedTuple): kinds: dict[str, Kind]; unmapped: dict[str, str]; checks: list[Check]`.
  - `load_register(root: Path) -> dict`, which raises `SetupError` when the register is missing, not UTF-8 or not TOML.
  - `load_guide(root: Path, raw: dict) -> tuple[str, str]`, returning the path and text and raising `SetupError` when the guide is missing or not UTF-8.
  - `parse_register(raw: dict) -> tuple[Register, list[Violation]]`.
  - `section_violations(reg: Register, anchors: list[str]) -> list[Violation]`.
  - The private helpers `_str_list(value, nonempty=True)` and `_nonempty_str(value)`, which later tasks reuse.
  - In the test file: `FIXTURE_GUIDE`, `FIXTURE_ANCHORS`, `FIXTURE_REGISTER` (all seven `check_conformance` checks plus one `check_frontmatter` entry, kinds `agent`, `claude-md`, `hook`, `rule` and `settings`), and `write_tree(root, files)`.

The register's kinds map is R2.3's initial table, with every `skills.*`-style shorthand spelled out. `[unmapped]` is R2.4's list. The `[[check]]` entries are R3.4's seven checks, carrying the guide's values as named parameters (Decision 5), and R2.5's five `check_frontmatter` records. Two choices the spec left open:
- A `[[check]]`'s `kind` may be a list. Both hook checks scan `hook` and `settings`, and `no-haiku-skill-model` covers skills and commands.
- `[unmapped]` keys are quoted (`'rules.overview' = …`), because a bare dotted key would make a nested table.

- [x] **Step 1: Write the failing tests.** In `build/test_check_conformance.py`, replace the import line

```python
import check_conformance as cc
```

with

```python
import tomllib

import pytest

import check_conformance as cc
```

and append:

````python
# A three-section fixture guide and a register that maps it. FIXTURE_REGISTER
# carries all seven check_conformance checks and one check_frontmatter entry,
# so a fixture repo built on it is clean until a test adds a violation.
FIXTURE_GUIDE = (
    '# Fixture guide\n\n'
    '## A\n<!-- cc: a.overview -->\n\nIntro.\n\n'
    '### One\n<!-- cc: a.one -->\n\nRules.\n\n'
    '## B\n<!-- cc: b.overview -->\n'
)
FIXTURE_ANCHORS = ['a.overview', 'a.one', 'b.overview']
FIXTURE_REGISTER = """\
[guide]
path = 'guide.md'

[kinds.agent]
description = 'Agents.'
globs = ['agents/*.md']
sections = ['a.overview']

[kinds.claude-md]
description = 'CLAUDE.md files.'
globs = ['CLAUDE.md']
sections = ['a.one']

[kinds.hook]
description = 'Hook scripts and their README.'
globs = ['hooks/*.sh', 'hooks/*.py', 'hooks/README.md']
exclude = ['hooks/test_*.py']
sections = ['a.one']

[kinds.rule]
description = 'Rules files.'
globs = ['rules/*.md', '.claude/rules/*.md']
sections = ['a.one']

[kinds.settings]
description = 'Project settings.'
globs = ['.claude/settings.json']
sections = ['a.one']

[unmapped]
'b.overview' = 'Governs no fixture file.'

[[check]]
id = 'claude-md-size'
kind = 'claude-md'
sections = ['a.one']
type = 'advice'
rule = 'Stay short.'
enforced_by = 'check_conformance'
limit = 200

[[check]]
id = 'rule-paths'
kind = 'rule'
sections = ['a.one']
type = 'advice'
rule = 'Set paths.'
enforced_by = 'check_conformance'
always_on = []

[[check]]
id = 'hook-dir-quoted'
kind = ['hook', 'settings']
sections = ['a.one']
type = 'advice'
rule = 'Quote the project dir.'
enforced_by = 'check_conformance'

[[check]]
id = 'stop-hook-guard'
kind = ['hook', 'settings']
sections = ['a.one']
type = 'advice'
rule = 'Guard Stop hooks.'
enforced_by = 'check_conformance'

[[check]]
id = 'agent-fields'
kind = 'agent'
sections = ['a.overview']
type = 'fact'
rule = 'Documented fields only.'
enforced_by = 'check_conformance'
fields = ['name', 'description', 'tools', 'model', 'memory']
models = ['sonnet', 'opus', 'haiku', 'fable', 'inherit']

[[check]]
id = 'readonly-agent-tools'
kind = 'agent'
sections = ['a.overview']
type = 'advice'
rule = 'Read-only tools.'
enforced_by = 'check_conformance'
forbidden_tools = ['Write', 'Edit', 'NotebookEdit']

[[check]]
id = 'bash-search-tools'
kind = 'agent'
sections = ['a.overview']
type = 'fact'
rule = 'No Grep or Glob beside Bash.'
enforced_by = 'check_conformance'

[[check]]
id = 'known-agent-tools'
kind = 'agent'
sections = ['a.overview']
type = 'fact'
rule = 'Known tools.'
enforced_by = 'check_frontmatter'
"""


def write_tree(root, files):
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def test_missing_register_is_a_setup_error(tmp_path):
    with pytest.raises(cc.SetupError, match='register not found'):
        cc.load_register(tmp_path)


def test_unparseable_register_is_a_setup_error(tmp_path):
    write_tree(tmp_path, {cc.REGISTER: 'kinds = [unclosed\n'})
    with pytest.raises(cc.SetupError, match='not valid TOML'):
        cc.load_register(tmp_path)


def test_missing_guide_is_a_setup_error(tmp_path):
    with pytest.raises(cc.SetupError, match='guide not found'):
        cc.load_guide(tmp_path, {'guide': {'path': 'guide.md'}})


def test_non_utf8_register_is_a_setup_error(tmp_path):
    path = tmp_path / cc.REGISTER
    path.parent.mkdir(parents=True)
    path.write_bytes(b"# caf\xe9\n[guide]\npath = 'guide.md'\n")
    with pytest.raises(cc.SetupError, match='not valid TOML'):
        cc.load_register(tmp_path)


def test_non_utf8_guide_is_a_setup_error(tmp_path):
    (tmp_path / 'guide.md').write_bytes(b'## caf\xe9\n')
    with pytest.raises(cc.SetupError, match='guide is not UTF-8'):
        cc.load_guide(tmp_path, {'guide': {'path': 'guide.md'}})


def test_register_field_problems_are_violations():
    raw = tomllib.loads(FIXTURE_REGISTER)
    del raw['kinds']['agent']['globs']
    raw['unmapped']['b.overview'] = ''
    raw['check'][0]['type'] = 'opinion'
    raw['check'][1]['enforced_by'] = 'by_hand'
    raw['check'][2]['kind'] = ['hook', 'nonesuch']
    reg, violations = cc.parse_register(raw)
    assert rendered(violations) == [
        f'{cc.REGISTER}: register (-): kinds.agent: globs must be a non-empty list of strings',
        f'{cc.REGISTER}: register (-): [unmapped] b.overview: the reason must be a non-empty string',
        f'{cc.REGISTER}: register (-): check claude-md-size: type must be fact or advice',
        f'{cc.REGISTER}: register (-): check rule-paths: enforced_by must be check_conformance or check_frontmatter',
        f'{cc.REGISTER}: register (-): check hook-dir-quoted: kind names no [kinds] table: nonesuch',
    ]
    assert sorted(reg.kinds) == ['claude-md', 'hook', 'rule', 'settings']
    assert [c.id for c in reg.checks] == [
        'claude-md-size', 'stop-hook-guard', 'agent-fields',
        'readonly-agent-tools', 'bash-search-tools', 'known-agent-tools']
    assert reg.checks[0].params == {'limit': 200}


def test_unknown_section_id_is_a_violation():
    raw = tomllib.loads(FIXTURE_REGISTER)
    raw['kinds']['rule']['sections'] = ['a.one', 'a.typo']
    reg, _ = cc.parse_register(raw)
    assert rendered(cc.section_violations(reg, FIXTURE_ANCHORS)) == [
        f'{cc.REGISTER}: section-id (a.typo): kinds.rule cites a section with no anchor in the guide']


def test_unmapped_anchor_is_a_violation():
    raw = tomllib.loads(FIXTURE_REGISTER)
    del raw['unmapped']['b.overview']
    reg, _ = cc.parse_register(raw)
    assert rendered(cc.section_violations(reg, FIXTURE_ANCHORS)) == [
        f'{cc.REGISTER}: section-map (b.overview): section is neither mapped to a kind nor listed in [unmapped]']


def test_anchor_both_mapped_and_unmapped_is_a_violation():
    raw = tomllib.loads(FIXTURE_REGISTER)
    raw['unmapped']['a.one'] = 'Listed by mistake.'
    reg, _ = cc.parse_register(raw)
    assert rendered(cc.section_violations(reg, FIXTURE_ANCHORS)) == [
        f'{cc.REGISTER}: section-map (a.one): section is both mapped to a kind and listed in [unmapped]']


def test_real_register_maps_every_anchor():
    raw = cc.load_register(cc.REPO)
    guide_path, text = cc.load_guide(cc.REPO, raw)
    assert guide_path == GUIDE
    sections, _ = cc.guide_sections(text, guide_path)
    reg, problems = cc.parse_register(raw)
    assert rendered(problems) == []
    assert rendered(cc.section_violations(reg, [s.id for s in sections])) == []
````

- [x] **Step 2: Run; confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `10 failed, 6 passed`. Each failure is an `AttributeError` on the attribute the test reaches first: `REGISTER` ×2, `SetupError` ×3, `load_register` ×1, `parse_register` ×4.

- [x] **Step 3: Create the register skeleton** `build/cc_guide/conformance.toml`:

```toml
# Claude Code guide conformance register.
#
# Links the guide's anchored sections to the repo's Claude Code artifact
# kinds, to the mechanical checks that enforce them, and to the exceptions the
# owner has recorded. Edited by hand, on the owner's decisions; no script
# writes it. build/check_conformance.py reads it with tomllib.
# Design: specs/completed/claude-code-guide-conformance.md (R2).
#
# Paraphrases here are in the repo's own words; no docs text is committed.
# Section IDs are the guide's anchors (drift spec R1.1). A kind's `globs` are
# matched with PurePath.full_match against the files git keeps, so `*` stays
# inside one path segment and every glob is anchored at the repo root.
# A [[check]]'s `kind` names one kind, or lists several when one check spans
# kinds.

[guide]
path = 'specs/guides/claude-code-customization-guide.md'

# ---------------------------------------------------------------------------
# Kinds: which files each artifact kind covers, and which sections govern it.
# A glob may match nothing yet: drift's project-local skill and agent under
# .claude/ are listed before they exist.
# ---------------------------------------------------------------------------

[kinds.skill]
description = 'Agent Skills: a SKILL.md per directory, canonical under skills/.'
globs = ['skills/*/SKILL.md', '.claude/skills/*/SKILL.md']
sections = [
    'skills.overview', 'skills.locations', 'skills.frontmatter',
    'skills.description', 'skills.listing-budget',
    'skills.progressive-disclosure', 'skills.arguments', 'skills.iterating',
    'commands.overview', 'mechanisms.overview', 'lean.ceremony',
    'lean.expensive-ops',
]

[kinds.agent]
description = 'Subagent definitions: canonical agents/*.md and project-local .claude/agents/.'
globs = ['agents/*.md', '.claude/agents/*.md']
sections = [
    'subagents.overview', 'subagents.frontmatter', 'subagents.tools',
    'subagents.models', 'subagents.isolation',
]

[kinds.command]
description = 'Slash-command files; they take skill frontmatter.'
globs = ['commands/*.md']
sections = [
    'commands.overview', 'skills.frontmatter', 'skills.arguments',
    'skills.description',
]

[kinds.hook]
description = 'Hook scripts and the README that documents their wiring.'
globs = ['hooks/*.sh', 'hooks/*.py', 'hooks/README.md']
exclude = ['hooks/test_*.py']
sections = [
    'hooks.overview', 'hooks.events', 'hooks.exit-codes', 'hooks.handlers',
    'hooks.configuration', 'hooks.patterns', 'hooks.pitfalls',
    'mechanisms.overview',
]

[kinds.rule]
description = 'Rules files: the canonical rules/ templates and the project .claude/rules/ links.'
globs = ['rules/*.md', '.claude/rules/*.md']
sections = ['rules.rules-files', 'rules.hierarchy']

[kinds.settings]
description = 'Project settings committed to the repo.'
globs = ['.claude/settings.json']
# lean.model-routing governs the settings file, except its TODO(owner)
# bullet, which is the owner's open question and binds nothing.
sections = ['rules.settings', 'hooks.configuration', 'lean.model-routing']

[kinds.claude-md]
description = 'Always-loaded CLAUDE.md files.'
globs = ['CLAUDE.md', 'build/CLAUDE.md']
sections = [
    'rules.claude-md', 'rules.hierarchy', 'context.overview',
    'lean.session-hygiene',
]

[kinds.installer]
description = 'install.py, which places skills, agents and commands for each runtime.'
globs = ['install.py']
sections = ['skills.locations', 'subagents.overview', 'commands.overview']

# ---------------------------------------------------------------------------
# Sections that govern no repo file, each with its reason. Disjoint from the
# kinds' sections; together they cover every anchor.
# ---------------------------------------------------------------------------

[unmapped]
'rules.overview' = 'An empty intro.'
'lean.overview' = 'An empty intro.'
'rules.auto-memory' = 'Auto memory lives under ~/.claude/projects/, outside the repo.'
'lean.measure' = 'Governs how sessions are measured, not any file here.'
'lean.caching' = 'Governs how sessions run, not any file here.'
'lean.mcp' = 'The repo configures no MCP server.'
'reading.overview' = 'Pointers to the docs.'

# ---------------------------------------------------------------------------
# Mechanical checks only. `type` is fact or advice, by the drift spec's R8.5
# test: a fact is a line a docs page could confirm or refute. Values taken
# from the guide are named parameters, so a guide change is reviewed here and
# the lint's code changes only when a mechanism does.
# ---------------------------------------------------------------------------

# The guide puts the docs' size target at under 200 lines per CLAUDE.md file.
[[check]]
id = 'claude-md-size'
kind = 'claude-md'
sections = ['rules.claude-md']
type = 'advice'
rule = 'Each CLAUDE.md file stays under the docs size target.'
enforced_by = 'check_conformance'
limit = 200

# A rule without paths loads in every session. always_on lists the rules
# that must persist past compaction, which the same section says should drop
# paths instead; none does today.
[[check]]
id = 'rule-paths'
kind = 'rule'
sections = ['rules.rules-files']
type = 'advice'
rule = 'A rules file sets a non-empty paths list so it loads lazily, unless always_on lists it; a .claude/rules/ link resolves inside the repo.'
enforced_by = 'check_conformance'
always_on = []

# The guide's Pattern 1 double-quotes the project-dir variable, so a path with
# spaces survives word splitting.
[[check]]
id = 'hook-dir-quoted'
kind = ['hook', 'settings']
sections = ['hooks.patterns']
type = 'advice'
rule = 'A hook command keeps $CLAUDE_PROJECT_DIR inside double quotes.'
enforced_by = 'check_conformance'

# A Stop hook that ignores stop_hook_active can block on a condition that
# never resolves, until the block cap stops it.
[[check]]
id = 'stop-hook-guard'
kind = ['hook', 'settings']
sections = ['hooks.exit-codes', 'hooks.patterns']
type = 'advice'
rule = 'A command wired to Stop runs a repo hook script that reads stop_hook_active.'
enforced_by = 'check_conformance'

# Both lists come from the guide's subagent frontmatter table.
[[check]]
id = 'agent-fields'
kind = 'agent'
sections = ['subagents.frontmatter']
type = 'fact'
rule = 'Agent frontmatter uses only documented fields, and model is an alias or a full claude- model ID.'
enforced_by = 'check_conformance'
fields = [
    'name', 'description', 'tools', 'disallowedTools', 'model', 'effort',
    'permissionMode', 'maxTurns', 'skills', 'mcpServers', 'hooks', 'memory',
    'background', 'isolation', 'omitClaudeMd', 'experimental', 'color',
    'initialPrompt',
]
models = ['sonnet', 'opus', 'haiku', 'fable', 'inherit']

# Reviewers get read-only tools; memory silently adds Read, Write and Edit.
# The marker is check_frontmatter.py's `## Read-only contract` heading.
[[check]]
id = 'readonly-agent-tools'
kind = 'agent'
sections = ['subagents.tools']
type = 'advice'
rule = 'A read-only agent sets a tools list without the editing tools, and sets no memory.'
enforced_by = 'check_conformance'
forbidden_tools = ['Write', 'Edit', 'NotebookEdit']

# On macOS, Linux and WSL, Grep and Glob are absent for an agent that also
# lists Bash; search then runs through the shell.
[[check]]
id = 'bash-search-tools'
kind = 'agent'
sections = ['subagents.tools']
type = 'fact'
rule = 'An agent that lists Bash lists neither Grep nor Glob.'
enforced_by = 'check_conformance'

# Rules build/check_frontmatter.py already enforces, recorded here without
# change so the register maps them to the guide. Portability Stage A owns
# that file.
[[check]]
id = 'command-manual-only'
kind = 'command'
sections = ['commands.overview']
type = 'advice'
rule = 'Commands set disable-model-invocation: true.'
enforced_by = 'check_frontmatter'

[[check]]
id = 'fork-only-context'
kind = 'skill'
sections = ['skills.frontmatter']
type = 'fact'
rule = 'context, when present, is fork.'
enforced_by = 'check_frontmatter'

[[check]]
id = 'no-haiku-skill-model'
kind = ['skill', 'command']
sections = ['skills.frontmatter']
type = 'fact'
rule = 'No skill or command sets a Haiku model, since auto mode ignores it.'
enforced_by = 'check_frontmatter'

[[check]]
id = 'known-agent-tools'
kind = 'agent'
sections = ['subagents.frontmatter']
type = 'fact'
rule = 'Agent tools come from a known set.'
enforced_by = 'check_frontmatter'

# check_frontmatter.py applies the same 1,024-character cap to agent
# descriptions, by analogy with the listing budget.
[[check]]
id = 'description-cap'
kind = 'skill'
sections = ['skills.description']
type = 'fact'
rule = 'Descriptions stay within the listing cap; the repo enforces the stricter 1,024-character Agent Skills cap.'
enforced_by = 'check_frontmatter'
```

- [x] **Step 4: Implement the register layer.** In `build/check_conformance.py`, replace

```python
import re
from pathlib import Path
```

with

```python
import re
import tomllib
from pathlib import Path
```

replace

```python
REPO = Path(__file__).resolve().parent.parent
```

with

```python
REPO = Path(__file__).resolve().parent.parent
REGISTER = 'build/cc_guide/conformance.toml'
```

and append:

```python
class SetupError(Exception):
    '''The guide or the register is missing or unreadable: exit 2, so a
    broken setup never passes as a clean run (R3.2).'''


class Kind(NamedTuple):
    globs: list[str]
    exclude: list[str]
    sections: list[str]


class Check(NamedTuple):
    id: str
    kinds: list[str]
    sections: list[str]
    enforced_by: str
    params: dict  # every key beyond CHECK_FIELDS: values taken from the guide


class Register(NamedTuple):
    kinds: dict[str, Kind]
    unmapped: dict[str, str]
    checks: list[Check]


CHECK_FIELDS = frozenset({'id', 'kind', 'sections', 'type', 'rule', 'enforced_by'})
ENFORCERS = ('check_conformance', 'check_frontmatter')


def load_register(root: Path) -> dict:
    path = root / REGISTER
    try:
        return tomllib.loads(path.read_text())
    except FileNotFoundError:
        raise SetupError(f'{REGISTER}: register not found') from None
    except UnicodeDecodeError as exc:
        raise SetupError(f'{REGISTER}: not valid TOML (not UTF-8: {exc.reason})') from None
    except tomllib.TOMLDecodeError as exc:
        raise SetupError(f'{REGISTER}: not valid TOML ({exc})') from None


def load_guide(root: Path, raw: dict) -> tuple[str, str]:
    '''The guide's repo-relative path, from [guide] path, and its text.'''
    guide = raw.get('guide')
    path = guide.get('path') if isinstance(guide, dict) else None
    if not isinstance(path, str) or not path:
        raise SetupError(f'{REGISTER}: [guide] path is missing')
    try:
        return path, (root / path).read_text()
    except OSError:
        raise SetupError(f'{path}: guide not found') from None
    except UnicodeDecodeError as exc:
        raise SetupError(f'{path}: guide is not UTF-8 ({exc.reason})') from None


def _str_list(value, nonempty: bool = True) -> bool:
    return (isinstance(value, list) and all(isinstance(v, str) and v for v in value)
            and (bool(value) or not nonempty))


def _nonempty_str(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def parse_register(raw: dict) -> tuple[Register, list[Violation]]:
    '''The register's kinds, unmapped sections and checks, keeping only the
    structurally usable entries. Each field-level problem is a violation, never
    an error (R2.3-R2.5, R3.2).'''
    out: list[Violation] = []

    def bad(message: str) -> None:
        out.append(Violation(REGISTER, 'register', '-', message))

    raw_kinds = raw.get('kinds')
    if not isinstance(raw_kinds, dict):
        bad('[kinds] must be a table of kinds')
        raw_kinds = {}
    kinds: dict[str, Kind] = {}
    for name, k in raw_kinds.items():
        if not isinstance(k, dict):
            bad(f'kinds.{name} must be a table')
            continue
        structural = []
        if not _str_list(k.get('globs')):
            structural.append('globs must be a non-empty list of strings')
        if not _str_list(k.get('exclude', []), nonempty=False):
            structural.append('exclude must be a list of strings')
        if not _str_list(k.get('sections')):
            structural.append('sections must be a non-empty list of strings')
        for problem in structural:
            bad(f'kinds.{name}: {problem}')
        if not _nonempty_str(k.get('description')):
            bad(f'kinds.{name}: description must be a non-empty string')
        if not structural:
            kinds[name] = Kind(k['globs'], k.get('exclude', []), k['sections'])

    raw_unmapped = raw.get('unmapped', {})
    if not isinstance(raw_unmapped, dict):
        bad('[unmapped] must be a table')
        raw_unmapped = {}
    unmapped = {}
    for sid, reason in raw_unmapped.items():
        if _nonempty_str(reason):
            unmapped[sid] = reason
        else:
            bad(f'[unmapped] {sid}: the reason must be a non-empty string')

    raw_checks = raw.get('check', [])
    if not isinstance(raw_checks, list):
        bad('[[check]] must be an array of tables')
        raw_checks = []
    checks: list[Check] = []
    for i, c in enumerate(raw_checks, start=1):
        if not isinstance(c, dict):
            bad(f'check #{i} must be a table')
            continue
        cid = c.get('id')
        label = f'check {cid}' if _nonempty_str(cid) else f'check #{i}'
        kind = c.get('kind')
        kind_list = [kind] if isinstance(kind, str) else kind
        structural = []
        if not _nonempty_str(cid):
            structural.append('id must be a non-empty string')
        if not _str_list(kind_list):
            structural.append('kind must name a kind, or list kinds')
        else:
            unknown = [k for k in kind_list if k not in raw_kinds]
            if unknown:
                structural.append(f'kind names no [kinds] table: {", ".join(unknown)}')
        if not _str_list(c.get('sections')):
            structural.append('sections must be a non-empty list of strings')
        if c.get('enforced_by') not in ENFORCERS:
            structural.append('enforced_by must be check_conformance or check_frontmatter')
        problems = list(structural)
        if c.get('type') not in ('fact', 'advice'):
            problems.append('type must be fact or advice')
        if not _nonempty_str(c.get('rule')):
            problems.append('rule must be a non-empty string')
        for problem in problems:
            bad(f'{label}: {problem}')
        if not structural:
            params = {k: v for k, v in c.items() if k not in CHECK_FIELDS}
            checks.append(Check(cid, kind_list, c['sections'], c['enforced_by'], params))
    return Register(kinds, unmapped, checks), out


def section_violations(reg: Register, anchors: list[str]) -> list[Violation]:
    '''Every section ID the register cites is an anchor, and every anchor is
    mapped to a kind or listed in [unmapped], never both (R2.4, R3.3 rule 1).'''
    known = set(anchors)
    out: list[Violation] = []

    def cite(where: str, ids) -> None:
        for sid in ids:
            if sid not in known:
                out.append(Violation(REGISTER, 'section-id', sid,
                                     f'{where} cites a section with no anchor in the guide'))

    for name, kind in reg.kinds.items():
        cite(f'kinds.{name}', kind.sections)
    cite('[unmapped]', reg.unmapped)
    for check in reg.checks:
        cite(f'check {check.id}', check.sections)
    mapped = {sid for kind in reg.kinds.values() for sid in kind.sections}
    for sid in anchors:
        if sid in mapped and sid in reg.unmapped:
            out.append(Violation(REGISTER, 'section-map', sid,
                                 'section is both mapped to a kind and listed in [unmapped]'))
        elif sid not in mapped and sid not in reg.unmapped:
            out.append(Violation(REGISTER, 'section-map', sid,
                                 'section is neither mapped to a kind nor listed in [unmapped]'))
    return out
```

> Deviation: on the owner's call (review finding T2-I1, 2026-10-04), `load_register` and
> `load_guide` read with `encoding='utf-8'`. Under a Latin-1 locale the default decoding
> accepted any bytes, so the non-UTF-8 tests did not raise `SetupError`. Fix round 1,
> 281da10; tests unchanged.

- [x] **Step 5: Run; all green.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `16 passed` (+10). `test_real_register_maps_every_anchor` proves the skeleton maps all 38 anchors, with the kinds and `[unmapped]` disjoint.

- [x] **Step 6: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && [ "$(git branch --show-current)" = feat/cc-guide-conformance ] && git add build/cc_guide/conformance.toml build/check_conformance.py build/test_check_conformance.py && git commit -m "feat(build): add the conformance register skeleton and its integrity rules

build/cc_guide/conformance.toml maps the guide's 38 sections to eight
artifact kinds or to [unmapped] with a reason, and records the seven
check_conformance checks and five existing check_frontmatter rules. The
lint loads it (exit 2 when it or the guide is missing or unreadable),
reports field-level problems as violations, and checks that every cited
section is an anchor and every anchor is mapped exactly once.

Plan 35, Task 2.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: File discovery and the agent checks (R2.3; R3.4 `agent-fields`, `readonly-agent-tools`, `bash-search-tools`)

**Files:**
- Modify: `build/check_conformance.py` (imports; append)
- Modify: `build/test_check_conformance.py` (imports; append 9 tests)

**Interfaces:**
- Consumes (Tasks 1–2): `Register`, `Kind`, `SetupError`, `_str_list`, `parse_register`, `load_register`, `REPO`; and `check_frontmatter.READONLY_HEADING` (`'## Read-only contract'`, the marker R3.4 names).
- Produces:
  - `class Finding(NamedTuple): file: str; message: str; value: int | None = None; waivable: bool = True`. Task 6 copies `value` and `waivable` into the `Violation`.
  - `git_env() -> dict[str, str]`.
  - `kept_files(root: Path) -> list[str]`: sorted, repo-relative POSIX paths; raises `SetupError`.
  - `kind_files(reg: Register, files: list[str]) -> dict[str, list[str]]`.
  - `frontmatter(text: str) -> dict | None` and `tool_list(fm: dict) -> list[str] | None`.
  - `read_artifacts(root: Path, files: list[str], out: list[Finding])`, a generator of `(file, text)` pairs. A file that cannot be read (a dangling link, or bytes that are not UTF-8) yields nothing and gets `Finding(file, 'cannot read: …', waivable=False)` in `out`. Every check reads its files through it.
  - The check signature every later check shares: `check_x(root: Path, files: list[str], params: dict) -> list[Finding]`. `files` is the sorted union of the check's kinds' files, and `params` is the register entry's keys beyond `id`, `kind`, `sections`, `type`, `rule` and `enforced_by`.
  - `check_agent_fields`, `check_readonly_agent_tools` and `check_bash_search_tools`.
  - In the test file: `git_repo(root, files)`, `AGENT_PARAMS` and `READ_ONLY`.

- [x] **Step 1: Write the failing tests.** In `build/test_check_conformance.py`, replace

```python
import tomllib

import pytest
```

with

```python
import subprocess
import tomllib

import pytest
```

and append:

````python
def git_repo(root, files):
    '''Write files under root and git-init it, so kept_files can list them.'''
    write_tree(root, files)
    subprocess.run(['git', 'init', '-q'], cwd=root, env=cc.git_env(), check=True)
    return root


def test_kind_globs_are_root_anchored_and_honor_exclude(tmp_path):
    root = git_repo(tmp_path, {
        'skills/a/SKILL.md': 'skill\n',
        'skills/a/references/SKILL.md': 'nested copy\n',
        'specs/verification/trial/skills/a/SKILL.md': 'trial copy\n',
        'hooks/guard.sh': '#!/bin/sh\n',
        'hooks/sub/nested.sh': '#!/bin/sh\n',
        'hooks/test_guard.py': '',
        'ignored/x.md': '',
        '.gitignore': 'ignored/\n',
    })
    files = cc.kept_files(root)
    assert 'ignored/x.md' not in files
    reg = cc.Register(
        kinds={'skill': cc.Kind(['skills/*/SKILL.md'], [], ['a.one']),
               'hook': cc.Kind(['hooks/*.sh', 'hooks/*.py'], ['hooks/test_*.py'], ['a.one'])},
        unmapped={}, checks=[])
    assert cc.kind_files(reg, files) == {
        'skill': ['skills/a/SKILL.md'], 'hook': ['hooks/guard.sh']}


def test_repo_kinds_match_the_directory_listings():
    '''The skill, agent and command kinds hold exactly what check_frontmatter.py
    lists from skills/, agents/ and commands/ (the .claude/ globs aside): no
    recursive search, so the SKILL.md copies under specs/verification/ never
    count as skills.'''
    reg, _ = cc.parse_register(cc.load_register(cc.REPO))
    kinds = cc.kind_files(reg, cc.kept_files(cc.REPO))
    repo = cc.REPO

    def canonical(kind):
        return [f for f in kinds[kind] if not f.startswith('.claude/')]

    assert canonical('skill') == sorted(
        f'skills/{d.name}/SKILL.md' for d in (repo / 'skills').iterdir()
        if (d / 'SKILL.md').is_file())
    assert canonical('agent') == sorted(f'agents/{p.name}' for p in (repo / 'agents').glob('*.md'))
    assert canonical('command') == sorted(
        f'commands/{p.name}' for p in (repo / 'commands').glob('*.md'))


AGENT_PARAMS = {
    'fields': ['name', 'description', 'tools', 'model', 'effort', 'memory'],
    'models': ['sonnet', 'opus', 'haiku', 'fable', 'inherit'],
}
READ_ONLY = '\n## Read-only contract\n\nNo edits.\n'


def test_agent_fields_pass(tmp_path):
    write_tree(tmp_path, {
        'agents/a.md': '---\nname: a\ndescription: A.\ntools: Read\nmodel: opus\neffort: high\n---\n',
        'agents/b.md': '---\nname: b\ndescription: B.\nmodel: claude-sonnet-5-5\n---\n',
    })
    assert cc.check_agent_fields(tmp_path, ['agents/a.md', 'agents/b.md'], AGENT_PARAMS) == []


def test_agent_fields_flag_unknown_keys_and_models(tmp_path):
    write_tree(tmp_path, {
        'agents/a.md': '---\nname: a\ndescription: A.\ncolour: red\nmodel: gpt-6\n---\n',
        'agents/b.md': 'No frontmatter.\n',
    })
    assert cc.check_agent_fields(tmp_path, ['agents/a.md', 'agents/b.md'], AGENT_PARAMS) == [
        cc.Finding('agents/a.md', "frontmatter key 'colour' is not a documented agent field"),
        cc.Finding('agents/a.md', "model 'gpt-6' is neither a listed alias nor a full claude- model ID"),
        cc.Finding('agents/b.md', 'no parseable YAML frontmatter'),
    ]


def test_readonly_agent_tools_pass(tmp_path):
    write_tree(tmp_path, {
        'agents/reviewer.md': '---\nname: reviewer\ntools: Read, Grep, Glob\n---\n' + READ_ONLY,
        'agents/worker.md': '---\nname: worker\ntools: Read, Write, Edit\n---\n\n## Contract\n',
    })
    files = ['agents/reviewer.md', 'agents/worker.md']
    params = {'forbidden_tools': ['Write', 'Edit', 'NotebookEdit']}
    assert cc.check_readonly_agent_tools(tmp_path, files, params) == []


def test_readonly_agent_tools_flag_editing_tools_memory_and_no_allowlist(tmp_path):
    write_tree(tmp_path, {
        'agents/writer.md': '---\nname: writer\ntools: [Read, Write, Edit]\n---\n' + READ_ONLY,
        'agents/memo.md': '---\nname: memo\ntools: Read\nmemory: project\n---\n' + READ_ONLY,
        'agents/open.md': '---\nname: open\n---\n' + READ_ONLY,
    })
    files = ['agents/memo.md', 'agents/open.md', 'agents/writer.md']
    params = {'forbidden_tools': ['Write', 'Edit', 'NotebookEdit']}
    assert cc.check_readonly_agent_tools(tmp_path, files, params) == [
        cc.Finding('agents/memo.md', 'read-only agent sets memory, which adds Read, Write and Edit'),
        cc.Finding('agents/open.md', 'read-only agent sets no tools list, so it inherits every tool'),
        cc.Finding('agents/writer.md', 'read-only agent lists Write, Edit'),
    ]


def test_unreadable_artifacts_are_unwaivable_findings(tmp_path):
    (tmp_path / 'agents').mkdir()
    (tmp_path / 'agents/gone.md').symlink_to('nowhere.md')
    (tmp_path / 'agents/latin.md').write_bytes(b'---\nname: caf\xe9\n---\n')
    assert cc.check_agent_fields(tmp_path, ['agents/gone.md', 'agents/latin.md'], AGENT_PARAMS) == [
        cc.Finding('agents/gone.md', 'cannot read: No such file or directory', waivable=False),
        cc.Finding('agents/latin.md', 'cannot read: not UTF-8 (invalid continuation byte)', waivable=False),
    ]


def test_bash_search_tools_pass(tmp_path):
    write_tree(tmp_path, {
        'agents/shell.md': '---\nname: shell\ntools: Read, Bash\n---\n',
        'agents/search.md': '---\nname: search\ntools: Read, Grep, Glob\n---\n',
    })
    assert cc.check_bash_search_tools(tmp_path, ['agents/search.md', 'agents/shell.md'], {}) == []


def test_bash_search_tools_flag_grep_or_glob_beside_bash(tmp_path):
    write_tree(tmp_path, {
        'agents/a.md': '---\nname: a\ntools: Read, Grep, Glob, Bash\n---\n',
        'agents/b.md': '---\nname: b\ntools: [Bash, Glob]\n---\n',
    })
    assert cc.check_bash_search_tools(tmp_path, ['agents/a.md', 'agents/b.md'], {}) == [
        cc.Finding('agents/a.md', 'lists Grep and Glob beside Bash, where both are absent and search runs through the shell'),
        cc.Finding('agents/b.md', 'lists Glob beside Bash, where both are absent and search runs through the shell'),
    ]
````

- [x] **Step 2: Run; confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `9 failed, 16 passed`, all `AttributeError`: `git_env` ×1, `kind_files` ×1, `check_agent_fields` ×3, `check_readonly_agent_tools` ×2, `check_bash_search_tools` ×2.

- [x] **Step 3: Implement.** In `build/check_conformance.py`, replace

```python
import re
import tomllib
from pathlib import Path
from typing import NamedTuple

from fences import fenced_lines
```

with

```python
import os
import re
import subprocess
import tomllib
from pathlib import Path, PurePosixPath
from typing import NamedTuple

import yaml

from check_frontmatter import READONLY_HEADING
from fences import fenced_lines
```

and append:

```python
class Finding(NamedTuple):
    '''One problem a check found; run_checks adds the check's ID and sections.
    waivable is False when the check could not evaluate the file, so no
    exception may hide the finding or be kept alive by it.'''
    file: str
    message: str
    value: int | None = None
    waivable: bool = True


def git_env() -> dict[str, str]:
    '''os.environ without git's repo-local variables, as install.py's git_env:
    a hook or shell may export GIT_DIR or GIT_INDEX_FILE for another repo.'''
    local = subprocess.run(['git', 'rev-parse', '--local-env-vars'],
                           capture_output=True, text=True, check=True).stdout.split()
    return {name: value for name, value in os.environ.items() if name not in local}


def kept_files(root: Path) -> list[str]:
    '''Repo-relative POSIX paths of the files git keeps under root: tracked, or
    untracked and not ignored, as install.py's kept_files lists them (R2.3).'''
    try:
        listing = subprocess.run(
            ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
            cwd=root, env=git_env(), capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SetupError(f'cannot list the files git keeps under {root} ({exc})') from None
    paths = [os.fsdecode(entry) for entry in listing.split(b'\0') if entry]
    # --cached also lists tracked files deleted from the working tree.
    return sorted(p for p in paths if (root / p).exists() or (root / p).is_symlink())


def kind_files(reg: Register, files: list[str]) -> dict[str, list[str]]:
    '''Each kind's files: those that full-match one of its globs and none of its
    excludes. full_match anchors every glob at the repo root and keeps `*`
    inside one path segment, so skills/*/SKILL.md never reaches a copy nested
    under specs/.'''
    return {
        name: [f for f in files
               if any(PurePosixPath(f).full_match(g) for g in kind.globs)
               and not any(PurePosixPath(f).full_match(e) for e in kind.exclude)]
        for name, kind in reg.kinds.items()
    }


FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n', re.S)
# A full model ID, as the guide's subagent `model` row allows beside the aliases.
FULL_MODEL_RE = re.compile(r'claude-[a-z0-9][a-z0-9.-]*')


def frontmatter(text: str) -> dict | None:
    '''The leading YAML frontmatter as a mapping; None when absent or unparseable.'''
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None
    return fm if isinstance(fm, dict) else None


def tool_list(fm: dict) -> list[str] | None:
    '''An agent's tools, from a comma-separated string or a YAML list; None when unset.'''
    tools = fm.get('tools')
    if tools is None:
        return None
    items = tools if isinstance(tools, list) else str(tools).split(',')
    return [str(t).strip() for t in items if str(t).strip()]


def read_artifacts(root: Path, files: list[str], out: list[Finding]):
    '''Yield (file, text) for each file that reads as UTF-8. A dangling link or
    a file that is not UTF-8 gets an unwaivable finding in out instead.'''
    for f in files:
        try:
            yield f, (root / f).read_text()
        except OSError as exc:
            out.append(Finding(f, f'cannot read: {exc.strerror}', waivable=False))
        except UnicodeDecodeError as exc:
            out.append(Finding(f, f'cannot read: not UTF-8 ({exc.reason})', waivable=False))


def check_agent_fields(root: Path, files: list[str], params: dict) -> list[Finding]:
    fields, models = set(params['fields']), set(params['models'])
    out: list[Finding] = []
    for f, text in read_artifacts(root, files, out):
        fm = frontmatter(text)
        if fm is None:
            out.append(Finding(f, 'no parseable YAML frontmatter'))
            continue
        for key in fm:
            if key not in fields:
                out.append(Finding(f, f'frontmatter key {key!r} is not a documented agent field'))
        model = fm.get('model')
        if model is not None and str(model) not in models and not FULL_MODEL_RE.fullmatch(str(model)):
            out.append(Finding(f, f'model {model!r} is neither a listed alias nor a full claude- model ID'))
    return out


def check_readonly_agent_tools(root: Path, files: list[str], params: dict) -> list[Finding]:
    out: list[Finding] = []
    for f, text in read_artifacts(root, files, out):
        if not any(line.strip() == READONLY_HEADING for line in text.splitlines()):
            continue
        fm = frontmatter(text) or {}
        tools = tool_list(fm)
        if tools is None:
            out.append(Finding(f, 'read-only agent sets no tools list, so it inherits every tool'))
        else:
            editing = [t for t in params['forbidden_tools'] if t in tools]
            if editing:
                out.append(Finding(f, f'read-only agent lists {", ".join(editing)}'))
        if 'memory' in fm:
            out.append(Finding(f, 'read-only agent sets memory, which adds Read, Write and Edit'))
    return out


def check_bash_search_tools(root: Path, files: list[str], params: dict) -> list[Finding]:
    out: list[Finding] = []
    for f, text in read_artifacts(root, files, out):
        tools = tool_list(frontmatter(text) or {}) or []
        search = [t for t in ('Grep', 'Glob') if t in tools]
        if 'Bash' in tools and search:
            out.append(Finding(f, f'lists {" and ".join(search)} beside Bash, where both are '
                                  'absent and search runs through the shell'))
    return out
```

> Deviation: `read_artifacts` reads with `encoding='utf-8'`, on the owner's Task 2 call
> (T2-I1), applied at implementation in c6ae014. Tests unchanged.

- [x] **Step 4: Run; all green.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `25 passed` (+9).

- [x] **Step 5: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && [ "$(git branch --show-current)" = feat/cc-guide-conformance ] && git add build/check_conformance.py build/test_check_conformance.py && git commit -m "feat(build): match conformance kinds to kept files; add the agent checks

Kinds' globs are root-anchored full_match patterns over the files git
keeps, so the SKILL.md trial copies under specs/verification/ never count
as skills; a repo test pins the skill, agent and command kinds to
check_frontmatter.py's directory listings. Adds agent-fields,
readonly-agent-tools and bash-search-tools; a file a check cannot read
becomes an unwaivable finding.

Plan 35, Task 3.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: The hook checks (R3.4 `hook-dir-quoted`, `stop-hook-guard`)

**Files:**
- Modify: `build/check_conformance.py` (imports; append)
- Modify: `build/test_check_conformance.py` (imports; append 14 tests, 8 of them one parametrized test)

**Interfaces:**
- Consumes (Tasks 1–3): `Finding`, `read_artifacts`, the check signature, and `fences.iter_code_blocks(text, langs)` (existing; returns `CodeBlock(lang, info, line, code)` for outermost blocks whose info word is in `langs`).
- Produces:
  - `class HookCommand(NamedTuple): file: str; where: str; event: str; command: str`.
  - `hook_commands(root, files) -> tuple[list[HookCommand], list[Finding]]`: the command hooks in the `hooks` tree of each ```` ```json ```` block in Markdown files and of each JSON file, plus an unwaivable finding per block or file that does not parse or read. It reads only `.md` and `.json` files.
  - `unquoted_var_uses(command: str, var: str) -> list[str]`, returning `'unquoted'` or `'single-quoted'` per use outside double quotes.
  - `check_hook_dir_quoted` and `check_stop_hook_guard`.
  - In the test file: `hooks_tree`, `json_block`, `HOOK_FILES` and `STOP_SCRIPT`.

`hook-dir-quoted` reports a JSON block that does not parse, as R3.4 requires. The finding is unwaivable, so a waiver on the file can neither hide it nor be kept alive by it (Task 7). `stop-hook-guard` skips such a block, so the failure is reported once. A Stop command resolves to a script by the basename of its first `shlex.split` word, looked up among the `.sh` and `.py` files the check was given.

- [x] **Step 1: Write the failing tests.** In `build/test_check_conformance.py`, replace

```python
import subprocess
import tomllib
```

with

```python
import json
import subprocess
import tomllib
```

and append:

````python
def hooks_tree(event, command):
    return {'hooks': {event: [{'hooks': [{'type': 'command', 'command': command}]}]}}


def json_block(data):
    return f'{FENCE}json\n{json.dumps(data, indent=2)}\n{FENCE}\n'


HOOK_FILES = ['.claude/settings.json', 'hooks/README.md', 'hooks/ruff-check.sh']
STOP_SCRIPT = '#!/usr/bin/env bash\nactive=$(jq -r .stop_hook_active)\n'


@pytest.mark.parametrize('command, states', [
    ('"$CLAUDE_PROJECT_DIR"/.claude/hooks/a.sh', []),
    ('"${CLAUDE_PROJECT_DIR}/a.sh"', []),
    ('"it\'s $CLAUDE_PROJECT_DIR"/a.sh', []),
    ('\\$CLAUDE_PROJECT_DIR/a.sh', []),
    ('$CLAUDE_PROJECT_DIRX/a.sh', []),
    ('$CLAUDE_PROJECT_DIR/.claude/hooks/a.sh', ['unquoted']),
    ("'$CLAUDE_PROJECT_DIR'/a.sh", ['single-quoted']),
    ('"a b"/${CLAUDE_PROJECT_DIR}/a.sh', ['unquoted']),
])
def test_unquoted_var_uses_track_shell_quoting(command, states):
    assert cc.unquoted_var_uses(command, 'CLAUDE_PROJECT_DIR') == states


def test_hook_dir_quoted_passes(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': (
            json_block(hooks_tree('PreToolUse', '"$CLAUDE_PROJECT_DIR"/.claude/hooks/a.sh'))
            + json_block({'permissions': {'allow': ['Bash(uv run *)']}})),
        '.claude/settings.json': json.dumps(hooks_tree('Stop', '"${CLAUDE_PROJECT_DIR}/b.sh"')),
        'hooks/ruff-check.sh': STOP_SCRIPT,
    })
    assert cc.check_hook_dir_quoted(tmp_path, HOOK_FILES, {}) == []


def test_hook_dir_quoted_flags_unquoted_and_single_quoted_uses(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': 'Wiring:\n\n' + json_block({'hooks': {
            'PreToolUse': [{'matcher': 'Bash', 'hooks': [
                {'type': 'command', 'command': '$CLAUDE_PROJECT_DIR/.claude/hooks/a.sh'}]}],
            'Stop': [{'hooks': [
                {'type': 'command', 'command': "'$CLAUDE_PROJECT_DIR'/.claude/hooks/b.sh"}]}],
        }}),
        '.claude/settings.json': json.dumps(hooks_tree('PostToolUse', '${CLAUDE_PROJECT_DIR}/c.sh')),
        'hooks/ruff-check.sh': STOP_SCRIPT,
    })
    assert cc.check_hook_dir_quoted(tmp_path, HOOK_FILES, {}) == [
        cc.Finding('.claude/settings.json', 'PostToolUse command leaves $CLAUDE_PROJECT_DIR unquoted'),
        cc.Finding('hooks/README.md', 'JSON block at line 3: PreToolUse command leaves $CLAUDE_PROJECT_DIR unquoted'),
        cc.Finding('hooks/README.md', 'JSON block at line 3: Stop command leaves $CLAUDE_PROJECT_DIR single-quoted'),
    ]


def test_unparseable_json_block_is_a_violation(tmp_path):
    write_tree(tmp_path, {'hooks/README.md': f'{FENCE}json\n{{"hooks": }}\n{FENCE}\n'})
    assert cc.check_hook_dir_quoted(tmp_path, ['hooks/README.md'], {}) == [
        cc.Finding('hooks/README.md', 'JSON block at line 1 does not parse (Expecting value)',
                   waivable=False)]


def test_hook_dir_quoted_reads_only_markdown_and_json(tmp_path):
    write_tree(tmp_path, {'hooks/README.md': json_block(hooks_tree('Stop', '"$CLAUDE_PROJECT_DIR"/x.sh'))})
    (tmp_path / 'hooks/legacy.sh').write_bytes(b'#!/bin/sh\n# caf\xe9\n')
    assert cc.check_hook_dir_quoted(tmp_path, ['hooks/README.md', 'hooks/legacy.sh'], {}) == []


def test_stop_hook_guard_passes(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': json_block(hooks_tree('Stop', '"$CLAUDE_PROJECT_DIR"/.claude/hooks/ruff-check.sh')),
        'hooks/ruff-check.sh': STOP_SCRIPT,
    })
    assert cc.check_stop_hook_guard(tmp_path, ['hooks/README.md', 'hooks/ruff-check.sh'], {}) == []


def test_stop_hook_guard_flags_an_unguarded_or_unresolvable_script(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': json_block({'hooks': {'Stop': [{'hooks': [
            {'type': 'command', 'command': '$CLAUDE_PROJECT_DIR/.claude/hooks/gate.sh'},
            {'type': 'command', 'command': 'uv run ruff check .'},
        ]}]}}),
        'hooks/gate.sh': '#!/usr/bin/env bash\nexit 2\n',
    })
    assert cc.check_stop_hook_guard(tmp_path, ['hooks/README.md', 'hooks/gate.sh'], {}) == [
        cc.Finding('hooks/README.md', 'JSON block at line 1: Stop command runs hooks/gate.sh, which never reads stop_hook_active'),
        cc.Finding('hooks/README.md', "JSON block at line 1: Stop command 'uv run ruff check .' names no hook script in the repo"),
    ]
````

- [x] **Step 2: Run; confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `14 failed, 25 passed`, all `AttributeError`: `unquoted_var_uses` ×8 (the parametrized cases), `check_hook_dir_quoted` ×4, `check_stop_hook_guard` ×2.

- [x] **Step 3: Implement.** In `build/check_conformance.py`, replace

```python
import os
import re
import subprocess
```

with

```python
import json
import os
import re
import shlex
import subprocess
```

replace

```python
from fences import fenced_lines
```

with

```python
from fences import fenced_lines, iter_code_blocks
```

and append:

````python
class HookCommand(NamedTuple):
    file: str
    where: str  # 'JSON block at line N: ' for Markdown, '' for a JSON file
    event: str
    command: str


def hook_commands(root: Path, files: list[str]) -> tuple[list[HookCommand], list[Finding]]:
    '''Every command hook in the hooks tree of each ```json block in the
    Markdown files and of each JSON file, plus an unwaivable finding per block
    or file that does not parse or read. Other files are skipped.'''
    found: list[HookCommand] = []
    problems: list[Finding] = []
    wiring = [f for f in files if f.endswith(('.md', '.json'))]
    for f, text in read_artifacts(root, wiring, problems):
        if f.endswith('.md'):
            docs = [(f'JSON block at line {b.line}', b.code)
                    for b in iter_code_blocks(text, ('json',))]
        else:
            docs = [('', text)]
        for label, source in docs:
            try:
                data = json.loads(source)
            except json.JSONDecodeError as exc:
                problems.append(Finding(f, f'{label or "file"} does not parse ({exc.msg})',
                                        waivable=False))
                continue
            where = f'{label}: ' if label else ''
            hooks = data.get('hooks') if isinstance(data, dict) else None
            for event, groups in (hooks.items() if isinstance(hooks, dict) else ()):
                for group in (groups if isinstance(groups, list) else ()):
                    inner = group.get('hooks') if isinstance(group, dict) else None
                    for hook in (inner if isinstance(inner, list) else ()):
                        if isinstance(hook, dict) and isinstance(hook.get('command'), str):
                            found.append(HookCommand(f, where, event, hook['command']))
    return found, problems


def _identifier_char(text: str, i: int) -> bool:
    return i < len(text) and (text[i].isalnum() or text[i] == '_')


def unquoted_var_uses(command: str, var: str) -> list[str]:
    '''The quote state, 'unquoted' or 'single-quoted', of each $var or ${var} in
    a shell command that is not inside double quotes. A single-quoted use
    never expands, so it counts too. Empty when every use is double-quoted.'''
    plain, braced = '$' + var, '${' + var + '}'
    states: list[str] = []
    quote = ''  # '', "'" or '"'
    i = 0
    while i < len(command):
        ch = command[i]
        if ch == '\\' and quote != "'":
            i += 2  # an escaped character, $ included, is literal
            continue
        if not quote and ch in '\'"':
            quote = ch
        elif ch == quote:
            quote = ''
        elif ch == '$' and (command.startswith(braced, i) or (
                command.startswith(plain, i) and not _identifier_char(command, i + len(plain)))):
            if quote != '"':
                states.append('single-quoted' if quote else 'unquoted')
        i += 1
    return states


def check_hook_dir_quoted(root: Path, files: list[str], params: dict) -> list[Finding]:
    found, out = hook_commands(root, files)
    for hook in found:
        for state in unquoted_var_uses(hook.command, 'CLAUDE_PROJECT_DIR'):
            out.append(Finding(hook.file, f'{hook.where}{hook.event} command leaves '
                                          f'$CLAUDE_PROJECT_DIR {state}'))
    return out


def check_stop_hook_guard(root: Path, files: list[str], params: dict) -> list[Finding]:
    found, _ = hook_commands(root, files)  # hook-dir-quoted reports parse failures
    scripts = {PurePosixPath(f).name: f for f in files if f.endswith(('.sh', '.py'))}
    out: list[Finding] = []
    for hook in found:
        if hook.event != 'Stop':
            continue
        try:
            words = shlex.split(hook.command)
        except ValueError:
            words = []
        script = scripts.get(PurePosixPath(words[0]).name) if words else None
        if script is None:
            out.append(Finding(hook.file, f'{hook.where}Stop command {hook.command!r} names '
                                          'no hook script in the repo'))
            continue
        for _, source in read_artifacts(root, [script], out):
            if 'stop_hook_active' not in source:
                out.append(Finding(hook.file, f'{hook.where}Stop command runs {script}, which '
                                              'never reads stop_hook_active'))
    return out
````

- [x] **Step 4: Run; all green.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `39 passed` (+14).

- [x] **Step 5: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && [ "$(git branch --show-current)" = feat/cc-guide-conformance ] && git add build/check_conformance.py build/test_check_conformance.py && git commit -m "feat(build): add the hook-dir-quoted and stop-hook-guard checks

Reads the hooks tree of each json block in hook-kind Markdown and of
.claude/settings.json. hook-dir-quoted scans shell quote state so each
\$CLAUDE_PROJECT_DIR use must sit in double quotes (a single-quoted use
never expands); stop-hook-guard requires a Stop command's script to read
stop_hook_active.

Plan 35, Task 4.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: The CLAUDE.md and rule checks (R3.4 `claude-md-size`, `rule-paths`)

**Files:**
- Modify: `build/check_conformance.py` (append)
- Modify: `build/test_check_conformance.py` (imports; append 5 tests)

**Interfaces:**
- Consumes (Tasks 1–3): `Finding`, `read_artifacts`, `frontmatter`, `_str_list`, the check signature.
- Produces:
  - `check_claude_md_size(root, files, params) -> list[Finding]`. Each finding carries `value` (the line count), which Task 7's ceiling reads.
  - `check_rule_paths(root, files, params) -> list[Finding]`.
  - In the test file: `RULE`.

`claude-md-size` counts newline characters, exactly as `wc -l` does, because Task 9 measures with `wc -l`; `str.splitlines` would also break on form feeds and Unicode line separators. It passes below `limit` ("fewer than 200"). `rule-paths` follows a `.claude/rules/` symlink only when it resolves inside the repo.

- [x] **Step 1: Write the failing tests.** In `build/test_check_conformance.py`, replace

```python
import json
import subprocess
```

with

```python
import json
import os
import subprocess
```

and append:

````python
def test_claude_md_size_passes_under_the_limit(tmp_path):
    write_tree(tmp_path, {'CLAUDE.md': 'line\n' * 199})
    assert cc.check_claude_md_size(tmp_path, ['CLAUDE.md'], {'limit': 200}) == []


def test_claude_md_size_flags_a_file_at_the_limit(tmp_path):
    write_tree(tmp_path, {'CLAUDE.md': 'line\n' * 200})
    assert cc.check_claude_md_size(tmp_path, ['CLAUDE.md'], {'limit': 200}) == [
        cc.Finding('CLAUDE.md', '200 lines; the guide targets fewer than 200', 200)]


def test_claude_md_size_counts_lines_as_wc_does(tmp_path):
    '''A form feed breaks a line for str.splitlines, but not for wc -l.'''
    write_tree(tmp_path, {'CLAUDE.md': 'a\fb\n' * 150})
    assert cc.check_claude_md_size(tmp_path, ['CLAUDE.md'], {'limit': 200}) == []


RULE = "---\npaths:\n  - '**/*.py'\n---\n\nRule.\n"


def test_rule_paths_pass(tmp_path):
    root = tmp_path / 'repo'
    write_tree(root, {'rules/py.md': RULE, 'rules/core.md': 'Always on.\n'})
    (root / '.claude/rules').mkdir(parents=True)
    os.symlink('../../rules/py.md', root / '.claude/rules/py.md')
    files = ['.claude/rules/py.md', 'rules/core.md', 'rules/py.md']
    assert cc.check_rule_paths(root, files, {'always_on': ['rules/core.md']}) == []


def test_rule_paths_flag_missing_paths_always_on_paths_and_outside_links(tmp_path):
    root = tmp_path / 'repo'
    write_tree(root, {'rules/bare.md': 'No frontmatter.\n', 'rules/py.md': RULE})
    write_tree(tmp_path, {'elsewhere/out.md': RULE})
    (root / '.claude/rules').mkdir(parents=True)
    os.symlink('../../../elsewhere/out.md', root / '.claude/rules/out.md')
    files = ['.claude/rules/out.md', 'rules/bare.md', 'rules/py.md']
    assert cc.check_rule_paths(root, files, {'always_on': ['rules/py.md']}) == [
        cc.Finding('.claude/rules/out.md', 'link resolves outside the repo, so Claude Code treats it as an external import'),
        cc.Finding('rules/bare.md', 'frontmatter sets no non-empty paths list, so the rule loads in every session'),
        cc.Finding('rules/py.md', 'always_on lists this rule, but it sets paths'),
    ]
````

- [x] **Step 2: Run; confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `5 failed, 39 passed`, all `AttributeError`: `check_claude_md_size` ×3, `check_rule_paths` ×2.

- [x] **Step 3: Implement.** Append to `build/check_conformance.py`:

```python
def check_claude_md_size(root: Path, files: list[str], params: dict) -> list[Finding]:
    limit = params['limit']
    out: list[Finding] = []
    for f, text in read_artifacts(root, files, out):
        n = text.count('\n')  # what wc -l counts
        if n >= limit:
            out.append(Finding(f, f'{n} lines; the guide targets fewer than {limit}', n))
    return out


def check_rule_paths(root: Path, files: list[str], params: dict) -> list[Finding]:
    always_on = set(params['always_on'])
    out: list[Finding] = []
    readable: list[str] = []
    for f in files:
        path = root / f
        if (f.startswith('.claude/rules/') and path.is_symlink()
                and not path.resolve().is_relative_to(root.resolve())):
            out.append(Finding(f, 'link resolves outside the repo, so Claude Code treats '
                                  'it as an external import'))
        elif not path.exists():
            out.append(Finding(f, 'link target does not exist'))
        else:
            readable.append(f)
    for f, text in read_artifacts(root, readable, out):
        paths = (frontmatter(text) or {}).get('paths')
        if f in always_on:
            if paths is not None:
                out.append(Finding(f, 'always_on lists this rule, but it sets paths'))
        elif not _str_list(paths):
            out.append(Finding(f, 'frontmatter sets no non-empty paths list, so the rule loads '
                                  'in every session'))
    return out
```

> Deviation: on the owner's call (review finding T5-I1, 2026-10-04), a rule link whose
> target does not exist is an unwaivable finding (`waivable=False`), as the plan's contract
> has it for a file a check cannot evaluate, and the outside-links test gained a dangling
> `.claude/rules/gone.md` link. Fix round 1, 85ff48a; counts unchanged.

- [x] **Step 4: Run; all green.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `44 passed` (+5).

- [x] **Step 5: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && [ "$(git branch --show-current)" = feat/cc-guide-conformance ] && git add build/check_conformance.py build/test_check_conformance.py && git commit -m "feat(build): add the claude-md-size and rule-paths checks

claude-md-size measures each CLAUDE.md against the register's limit and
carries the line count for a waiver's ceiling; rule-paths requires a
non-empty paths list unless always_on lists the rule, and a .claude/rules/
link that resolves inside the repo.

Plan 35, Task 5.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: The check registry, `run` and `main` (R3.1, R3.2, R3.3 rule 2, check-ID uniqueness)

**Files:**
- Modify: `build/check_conformance.py` (docstring; imports; append)
- Modify: `build/test_check_conformance.py` (append 8 tests)

**Interfaces:**
- Consumes (Tasks 1–5): every function above.
- Produces:
  - `CHECKS: dict[str, tuple[callable, dict[str, str]]]`: check ID → (function, parameter name → `'integer'` or `'strings'`).
  - `_runnable(check: Check) -> bool`: a `check_conformance` entry with an implementation and well-typed parameters, which `run_checks` runs.
  - `implementation_violations(reg: Register) -> list[Violation]`.
  - `run_checks(root, reg, kinds) -> list[Violation]`, where each `Finding` becomes a `Violation` with the check's ID and its sections joined by `, `, keeping `value` and `waivable`.
  - `run(root: Path) -> list[str]`: the rendered, sorted violations; raises `SetupError`.
  - `main(root: Path = REPO) -> int`: prints and returns 0/1, or prints the `SetupError` to stderr and returns 2.
  - In the test file: `fixture_repo(tmp_path, files=None, register=FIXTURE_REGISTER)` and `GREP_BESIDE_BASH`.

- [x] **Step 1: Write the failing tests.** Append to `build/test_check_conformance.py`:

````python
def fixture_repo(tmp_path, files=None, register=FIXTURE_REGISTER):
    '''A git-initialized fixture repo holding the fixture guide, a register
    (FIXTURE_REGISTER unless given) and files; clean until files add a violation.'''
    return git_repo(tmp_path, {'guide.md': FIXTURE_GUIDE, cc.REGISTER: register, **(files or {})})


GREP_BESIDE_BASH = '---\nname: a\ndescription: A.\ntools: Read, Grep, Bash\n---\n'


def test_main_exits_0_on_a_clean_repo(tmp_path, capsys):
    root = fixture_repo(tmp_path, {'CLAUDE.md': 'Short.\n'})
    assert cc.main(root) == 0
    assert capsys.readouterr().out == ''


def test_main_exits_1_with_one_line_per_violation(tmp_path, capsys):
    root = fixture_repo(tmp_path, {'CLAUDE.md': 'line\n' * 250, 'agents/a.md': GREP_BESIDE_BASH})
    assert cc.main(root) == 1
    assert capsys.readouterr().out.splitlines() == [
        'CLAUDE.md: claude-md-size (a.one): 250 lines; the guide targets fewer than 200',
        'agents/a.md: bash-search-tools (a.overview): lists Grep beside Bash, where both are absent and search runs through the shell',
    ]


def test_main_exits_2_on_an_unparseable_register(tmp_path, capsys):
    root = fixture_repo(tmp_path, register='[guide\npath = 1\n')
    assert cc.main(root) == 2
    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err.startswith(f'{cc.REGISTER}: not valid TOML')


def test_main_exits_2_when_the_guide_is_missing(tmp_path, capsys):
    root = fixture_repo(tmp_path)
    (root / 'guide.md').unlink()
    assert cc.main(root) == 2
    assert capsys.readouterr().err == 'guide.md: guide not found\n'


def test_check_entry_without_an_implementation_is_a_violation(tmp_path):
    root = fixture_repo(tmp_path, register=FIXTURE_REGISTER + """
[[check]]
id = 'no-such-check'
kind = 'agent'
sections = ['a.overview']
type = 'advice'
rule = 'Unimplemented.'
enforced_by = 'check_conformance'
""")
    assert cc.run(root) == [
        f'{cc.REGISTER}: check-impl (a.overview): check no-such-check has no implementation in build/check_conformance.py']


def test_implementation_without_a_check_entry_is_a_violation(tmp_path):
    register = FIXTURE_REGISTER.replace("id = 'bash-search-tools'", "id = 'bash-search-toolz'")
    root = fixture_repo(tmp_path, register=register)
    assert cc.run(root) == [
        f'{cc.REGISTER}: check-impl (a.overview): check bash-search-toolz has no implementation in build/check_conformance.py',
        'build/check_conformance.py: check-impl (-): implementation bash-search-tools has no [[check]] entry',
    ]


def test_missing_check_parameter_is_a_violation(tmp_path):
    root = fixture_repo(tmp_path, register=FIXTURE_REGISTER.replace('limit = 200\n', ''))
    assert cc.run(root) == [
        f'{cc.REGISTER}: register (-): check claude-md-size: parameter limit must be an integer']


def test_duplicate_check_ids_are_a_violation(tmp_path):
    root = fixture_repo(tmp_path, register=FIXTURE_REGISTER + """
[[check]]
id = 'known-agent-tools'
kind = 'agent'
sections = ['a.overview']
type = 'fact'
rule = 'Listed twice.'
enforced_by = 'check_frontmatter'
""")
    assert cc.run(root) == [
        f'{cc.REGISTER}: duplicate-id (-): check ID known-agent-tools appears 2 times']
````

- [x] **Step 2: Run; confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `8 failed, 44 passed`, all `AttributeError`: `main` ×4, `run` ×4.

- [x] **Step 3: Implement.** In `build/check_conformance.py`, replace the module docstring's last paragraph

```python
governs, to mechanical checks, and to recorded exceptions. Design:
specs/completed/claude-code-guide-conformance.md.
'''
```

with

```python
governs, to mechanical checks, and to recorded exceptions. Design:
specs/completed/claude-code-guide-conformance.md.

Run: uv run --python 3.13 --with pyyaml python build/check_conformance.py
Exit 0 when clean; 1 with one `<file>: <check> (<section>): <message>` line per
violation on stdout; 2 when the guide or the register is missing or is not
valid TOML, or git cannot list the repo's files, so a broken setup never looks
clean. Field-level register problems are violations, not errors.
'''
```

replace

```python
import subprocess
import tomllib
```

with

```python
import subprocess
import sys
import tomllib
```

and append:

```python
# Each check_conformance check: its function and the parameters the register
# must give it ('integer', or 'strings' for a list of strings).
CHECKS = {
    'claude-md-size': (check_claude_md_size, {'limit': 'integer'}),
    'rule-paths': (check_rule_paths, {'always_on': 'strings'}),
    'hook-dir-quoted': (check_hook_dir_quoted, {}),
    'stop-hook-guard': (check_stop_hook_guard, {}),
    'agent-fields': (check_agent_fields, {'fields': 'strings', 'models': 'strings'}),
    'readonly-agent-tools': (check_readonly_agent_tools, {'forbidden_tools': 'strings'}),
    'bash-search-tools': (check_bash_search_tools, {}),
}
PARAM_TYPES = {
    'integer': (lambda v: isinstance(v, int) and not isinstance(v, bool), 'an integer'),
    'strings': (lambda v: _str_list(v, nonempty=False), 'a list of strings'),
}


def _runnable(check: Check) -> bool:
    if check.enforced_by != 'check_conformance' or check.id not in CHECKS:
        return False
    return all(PARAM_TYPES[kind][0](check.params.get(name))
               for name, kind in CHECKS[check.id][1].items())


def implementation_violations(reg: Register) -> list[Violation]:
    '''Every check_conformance entry has an implementation with its parameters,
    every implementation has an entry, and check IDs are unique (R3.3 rules 2-3).'''
    out: list[Violation] = []
    ids = [c.id for c in reg.checks]
    for cid in sorted(set(ids)):
        if ids.count(cid) > 1:
            out.append(Violation(REGISTER, 'duplicate-id', '-',
                                 f'check ID {cid} appears {ids.count(cid)} times'))
    entries = set()
    for check in reg.checks:
        if check.enforced_by != 'check_conformance':
            continue
        entries.add(check.id)
        if check.id not in CHECKS:
            out.append(Violation(REGISTER, 'check-impl', ', '.join(check.sections),
                                 f'check {check.id} has no implementation in build/check_conformance.py'))
            continue
        for name, kind in CHECKS[check.id][1].items():
            valid, wanted = PARAM_TYPES[kind]
            if not valid(check.params.get(name)):
                out.append(Violation(REGISTER, 'register', '-',
                                     f'check {check.id}: parameter {name} must be {wanted}'))
    for cid in sorted(set(CHECKS) - entries):
        out.append(Violation('build/check_conformance.py', 'check-impl', '-',
                             f'implementation {cid} has no [[check]] entry'))
    return out


def run_checks(root: Path, reg: Register, kinds: dict[str, list[str]]) -> list[Violation]:
    '''Run each runnable check once over the files of its kinds.'''
    out: list[Violation] = []
    done: set[str] = set()
    for check in reg.checks:
        if check.id in done or not _runnable(check):
            continue
        done.add(check.id)
        func = CHECKS[check.id][0]
        files = sorted({f for kind in check.kinds for f in kinds.get(kind, [])})
        for found in func(root, files, check.params):
            out.append(Violation(found.file, check.id, ', '.join(check.sections),
                                 found.message, found.value, found.waivable))
    return out


def run(root: Path) -> list[str]:
    '''Every violation in the repo at root, rendered and sorted.'''
    raw = load_register(root)
    guide_path, text = load_guide(root, raw)
    files = kept_files(root)
    sections, out = guide_sections(text, guide_path)
    reg, problems = parse_register(raw)
    out += problems
    out += section_violations(reg, [s.id for s in sections if s.id])
    out += implementation_violations(reg)
    out += run_checks(root, reg, kind_files(reg, files))
    return sorted(v.render() for v in out)


def main(root: Path = REPO) -> int:
    try:
        lines = run(root)
    except SetupError as exc:
        print(exc, file=sys.stderr)
        return 2
    for line in lines:
        print(line)
    return 1 if lines else 0


if __name__ == '__main__':
    sys.exit(main())
```

- [x] **Step 4: Run; all green.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `52 passed` (+8).

- [x] **Step 5: Run the lint on the repo; record the day-one output.** It must exit 1 with exactly these 11 lines (R5.2's mechanical findings), with the CLAUDE.md count as measured:

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && uv run --python 3.13 --with pyyaml python build/check_conformance.py; echo "exit=$?"`
Expected:

```text
CLAUDE.md: claude-md-size (rules.claude-md): 238 lines; the guide targets fewer than 200
agents/code-reviewer.md: bash-search-tools (subagents.tools): lists Grep and Glob beside Bash, where both are absent and search runs through the shell
agents/debugger.md: bash-search-tools (subagents.tools): lists Grep and Glob beside Bash, where both are absent and search runs through the shell
agents/docs-writer.md: bash-search-tools (subagents.tools): lists Grep and Glob beside Bash, where both are absent and search runs through the shell
agents/explore.md: bash-search-tools (subagents.tools): lists Grep and Glob beside Bash, where both are absent and search runs through the shell
agents/security-auditor.md: bash-search-tools (subagents.tools): lists Grep and Glob beside Bash, where both are absent and search runs through the shell
agents/task-reviewer.md: bash-search-tools (subagents.tools): lists Grep and Glob beside Bash, where both are absent and search runs through the shell
agents/test-runner.md: bash-search-tools (subagents.tools): lists Grep and Glob beside Bash, where both are absent and search runs through the shell
hooks/README.md: hook-dir-quoted (hooks.patterns): JSON block at line 51: PostToolUse command leaves $CLAUDE_PROJECT_DIR unquoted
hooks/README.md: hook-dir-quoted (hooks.patterns): JSON block at line 51: PreToolUse command leaves $CLAUDE_PROJECT_DIR unquoted
hooks/README.md: hook-dir-quoted (hooks.patterns): JSON block at line 51: Stop command leaves $CLAUDE_PROJECT_DIR unquoted
exit=1
```

Any other line is a finding to stop on and report, not to fix.

- [x] **Step 6: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && [ "$(git branch --show-current)" = feat/cc-guide-conformance ] && git add build/check_conformance.py build/test_check_conformance.py && git commit -m "feat(build): wire the conformance checks into run and main

CHECKS maps each check_conformance check to its function and register
parameters; every register entry needs an implementation and vice versa,
and check IDs are unique. main exits 0 clean, 1 with one sorted line per
violation, 2 on a missing guide or an unreadable register.

Plan 35, Task 6.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Exceptions and both-way waivers (R2.6, R3.3 rules 3–4)

**Files:**
- Modify: `build/check_conformance.py` (insert before `def run`; replace `run`'s body)
- Modify: `build/test_check_conformance.py` (append 26 tests, 14 of them one parametrized test)

**Interfaces:**
- Consumes (Tasks 1–6): `Register`, `Check`, `Violation` (with `waivable`), `run_checks`, `_runnable`, `kind_files`, `_str_list`, `_nonempty_str`.
- Produces:
  - `class ExceptionEntry(NamedTuple): id: str; check: str | None; artifacts: list[str]; reason: str; ceiling: int | None`.
  - `NUMERIC_CHECKS = frozenset({'claude-md-size'})`.
  - `parse_exceptions(raw, reg, anchors, files, root) -> tuple[list[ExceptionEntry], list[Violation]]`.
  - `apply_waivers(violations, exceptions, reg, ran: set[str]) -> list[Violation]`, where `ran` holds the IDs of the checks that ran over every file of their kinds.
  - In the test file: `toml_value`, `exception_toml`, `GAP`, `SIZE_GAP`, `UNWAIVED` and `field_error`.

An exception waives only when its `id`, `check` and `artifacts` are all usable. A malformed one still reports its field problems. Waivers match per (check, file), however many violations the file holds (R3.3 rule 4). An unwaivable violation (Tasks 3–4: a file or JSON block the check could not read or parse) always prints, and never makes a waiver on its file look stale. Nor does a check that did not run, because a malformed parameter or kind stopped it: R3.3's stale rule assumes the check evaluated the file.

- [x] **Step 1: Write the failing tests.** Append to `build/test_check_conformance.py`:

````python
def toml_value(value):
    if isinstance(value, list):
        return '[' + ', '.join(toml_value(v) for v in value) + ']'
    if isinstance(value, int):
        return str(value)
    return f"'{value}'"


def exception_toml(fields):
    '''One [[exception]] table; a None value leaves its key out.'''
    body = ''.join(f'{k} = {toml_value(v)}\n' for k, v in fields.items() if v is not None)
    return f'\n[[exception]]\n{body}'


GAP = {
    'id': 'grep-beside-bash', 'type': 'gap', 'check': 'bash-search-tools',
    'sections': ['a.overview'], 'artifacts': ['agents/a.md'],
    'guide': 'Bash hides Grep and Glob.', 'reason': 'Gemini adapters use them.',
    'evidence': 'Fixture.', 'tracked_in': 'a later stage', 'protects': ['gemini'],
}
SIZE_GAP = {**GAP, 'id': 'md-size', 'check': 'claude-md-size', 'sections': ['a.one'],
            'artifacts': ['CLAUDE.md'], 'protects': None, 'ceiling': 225}
UNWAIVED = ('agents/a.md: bash-search-tools (a.overview): lists Grep beside Bash, '
            'where both are absent and search runs through the shell')


def test_waiver_hides_its_violation(tmp_path):
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH},
                        register=FIXTURE_REGISTER + exception_toml(GAP))
    assert cc.run(root) == []


def test_stale_waiver_is_a_violation(tmp_path):
    root = fixture_repo(tmp_path, {'agents/a.md': '---\nname: a\ntools: Read, Bash\n---\n'},
                        register=FIXTURE_REGISTER + exception_toml(GAP))
    assert cc.run(root) == [
        'agents/a.md: stale-waiver (a.overview): exception grep-beside-bash (Gemini adapters use them.) '
        'waives bash-search-tools here, but the file no longer violates it: remove the entry, '
        'or this file from it']


def test_ceiling_breach_is_a_violation(tmp_path):
    root = fixture_repo(tmp_path, {'CLAUDE.md': 'line\n' * 230},
                        register=FIXTURE_REGISTER + exception_toml(SIZE_GAP))
    assert cc.run(root) == [
        "CLAUDE.md: ceiling (a.one): 230 exceeds exception md-size's ceiling of 225"]


def test_file_under_its_ceiling_passes(tmp_path):
    root = fixture_repo(tmp_path, {'CLAUDE.md': 'line\n' * 220},
                        register=FIXTURE_REGISTER + exception_toml(SIZE_GAP))
    assert cc.run(root) == []


def test_file_at_its_ceiling_passes(tmp_path):
    root = fixture_repo(tmp_path, {'CLAUDE.md': 'line\n' * 225},
                        register=FIXTURE_REGISTER + exception_toml(SIZE_GAP))
    assert cc.run(root) == []


def test_waiver_covers_only_its_listed_files(tmp_path):
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH, 'agents/b.md': GREP_BESIDE_BASH},
                        register=FIXTURE_REGISTER + exception_toml(GAP))
    assert cc.run(root) == [UNWAIVED.replace('agents/a.md', 'agents/b.md')]


def test_waiver_covers_only_its_check(tmp_path):
    agent = GREP_BESIDE_BASH.replace('---\n', '---\ncolour: red\n', 1)
    root = fixture_repo(tmp_path, {'agents/a.md': agent},
                        register=FIXTURE_REGISTER + exception_toml(GAP))
    assert cc.run(root) == [
        "agents/a.md: agent-fields (a.overview): frontmatter key 'colour' is not a documented agent field"]


def test_unparseable_block_is_never_waived(tmp_path):
    '''A JSON block that does not parse stands beside a waiver on its file,
    and does not keep that waiver alive.'''
    hook_gap = {**GAP, 'id': 'hook-dir', 'check': 'hook-dir-quoted', 'sections': ['a.one'],
                'artifacts': ['hooks/README.md'], 'protects': None}
    readme = (json_block(hooks_tree('PreToolUse', '$CLAUDE_PROJECT_DIR/a.sh'))
              + f'{FENCE}json\n{{"hooks": }}\n{FENCE}\n')
    root = fixture_repo(tmp_path, {'hooks/README.md': readme},
                        register=FIXTURE_REGISTER + exception_toml(hook_gap))
    assert cc.run(root) == [
        'hooks/README.md: hook-dir-quoted (a.one): JSON block at line 17 does not parse (Expecting value)']


def test_check_that_cannot_run_leaves_its_waivers_alone(tmp_path):
    '''A malformed parameter stops a check, so its waiver is not called stale.'''
    register = (FIXTURE_REGISTER.replace('limit = 200\n', "limit = '200'\n")
                + exception_toml(GAP) + exception_toml(SIZE_GAP))
    root = fixture_repo(tmp_path, {'CLAUDE.md': 'line\n' * 230, 'agents/a.md': GREP_BESIDE_BASH},
                        register=register)
    assert cc.run(root) == [
        f'{cc.REGISTER}: register (-): check claude-md-size: parameter limit must be an integer']


def test_valid_exceptions_pass(tmp_path):
    '''A gap waiving its check beside a check-less deviation whose artifacts
    are a glob: both are well-formed, so the repo is clean.'''
    deviation = {**GAP, 'id': 'tools-convention', 'type': 'deviation', 'check': None,
                 'artifacts': ['agents/*.md'], 'tracked_in': None, 'revisit': 'when Gemini changes'}
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH},
                        register=FIXTURE_REGISTER + exception_toml(GAP) + exception_toml(deviation))
    assert cc.run(root) == []


def test_duplicate_exception_ids_are_a_violation(tmp_path):
    second = {**GAP, 'check': None, 'protects': None}
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH},
                        register=FIXTURE_REGISTER + exception_toml(GAP) + exception_toml(second))
    assert cc.run(root) == [
        f'{cc.REGISTER}: duplicate-id (-): exception ID grep-beside-bash appears 2 times']


def test_numeric_waiver_needs_a_ceiling(tmp_path):
    root = fixture_repo(tmp_path, {'CLAUDE.md': 'line\n' * 230},
                        register=FIXTURE_REGISTER + exception_toml({**SIZE_GAP, 'ceiling': None}))
    assert cc.run(root) == [
        f'{cc.REGISTER}: exception (-): exception md-size: a waiver of claude-md-size needs an integer ceiling']


def field_error(message):
    return f'{cc.REGISTER}: exception (-): exception grep-beside-bash: {message}'


@pytest.mark.parametrize('changes, expected', [
    ({'type': 'excuse'}, [field_error('type must be deviation or gap')]),
    ({'tracked_in': None}, [field_error('a gap needs tracked_in')]),
    ({'revisit': 'when X'}, [field_error('a gap takes no revisit')]),
    ({'type': 'deviation', 'tracked_in': None}, [field_error('a deviation needs revisit')]),
    ({'type': 'deviation', 'revisit': 'when X'}, [field_error('a deviation takes no tracked_in')]),
    ({'evidence': ''}, [field_error('evidence must be a non-empty string')]),
    ({'protects': ['cursor']}, [field_error('protects may list only codex and gemini')]),
    ({'ceiling': 3}, [field_error('ceiling applies only to a numeric check (claude-md-size)')]),
    ({'sections': ['a.typo']}, [
        f'{cc.REGISTER}: section-id (a.typo): exception grep-beside-bash cites a section with no anchor in the guide']),
    ({'check': 'known-agent-tools'}, [
        UNWAIVED, field_error('check known-agent-tools is not a check_conformance check')]),
    ({'check': ['bash-search-tools']}, [
        UNWAIVED, field_error('check must name one check_conformance check')]),
    ({'artifacts': ['agents/*.md']}, [
        UNWAIVED, field_error('with check set, artifacts must be explicit paths: agents/*.md')]),
    ({'artifacts': ['agents/gone.md']}, [
        UNWAIVED, field_error('artifact agents/gone.md does not exist')]),
    ({'check': None, 'artifacts': ['skills/*/SKILL.md']}, [
        UNWAIVED, field_error('artifact glob skills/*/SKILL.md matches no file')]),
])
def test_exception_field_rules(tmp_path, changes, expected):
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH},
                        register=FIXTURE_REGISTER + exception_toml({**GAP, **changes}))
    assert cc.run(root) == expected
````

- [x] **Step 2: Run; confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `26 failed, 52 passed`. Every failure is an `AssertionError` list mismatch: `run` ignores `[[exception]]` until Step 3, so the waived violation still prints and the field and staleness lines are missing. `test_valid_exceptions_pass` must fail too, on the unwaived `bash-search-tools` line. If it passes, it has gone vacuous: see Global Constraints, "Test-first".

- [x] **Step 3: Implement.** In `build/check_conformance.py`, insert immediately before the line `def run(root: Path) -> list[str]:`:

```python
class ExceptionEntry(NamedTuple):
    id: str
    check: str | None  # the waived check_conformance check, if any
    artifacts: list[str]
    reason: str
    ceiling: int | None


# Checks whose findings carry a measured value that a waiver's ceiling caps.
NUMERIC_CHECKS = frozenset({'claude-md-size'})
GLOB_CHAR_RE = re.compile(r'[*?\[]')


def parse_exceptions(raw: dict, reg: Register, anchors: list[str], files: list[str],
                     root: Path) -> tuple[list[ExceptionEntry], list[Violation]]:
    '''The register's usable exceptions, plus a violation per missing or
    inconsistent field (R2.6, R3.3 rule 3). An exception waives only when its
    id, check and artifacts are all usable.'''
    raw_exceptions = raw.get('exception', [])
    if not isinstance(raw_exceptions, list):
        return [], [Violation(REGISTER, 'register', '-', '[[exception]] must be an array of tables')]
    conformance = {c.id for c in reg.checks if c.enforced_by == 'check_conformance'}
    known = set(anchors)
    out: list[Violation] = []
    entries: list[ExceptionEntry] = []
    ids: list[str] = []
    for i, e in enumerate(raw_exceptions, start=1):
        if not isinstance(e, dict):
            out.append(Violation(REGISTER, 'exception', '-', f'exception #{i} must be a table'))
            continue
        eid = e.get('id')
        label = f'exception {eid}' if _nonempty_str(eid) else f'exception #{i}'
        problems: list[str] = []
        if _nonempty_str(eid):
            ids.append(eid)
        else:
            problems.append('id must be a non-empty string')
        etype = e.get('type')
        if etype not in ('deviation', 'gap'):
            problems.append('type must be deviation or gap')
        for field in ('guide', 'reason', 'evidence'):
            if not _nonempty_str(e.get(field)):
                problems.append(f'{field} must be a non-empty string')
        if etype == 'deviation':
            if not _nonempty_str(e.get('revisit')):
                problems.append('a deviation needs revisit')
            if 'tracked_in' in e:
                problems.append('a deviation takes no tracked_in')
        elif etype == 'gap':
            if not _nonempty_str(e.get('tracked_in')):
                problems.append('a gap needs tracked_in')
            if 'revisit' in e:
                problems.append('a gap takes no revisit')
        protects = e.get('protects', [])
        if not (_str_list(protects, nonempty=False) and set(protects) <= {'codex', 'gemini'}):
            problems.append('protects may list only codex and gemini')
        sections = e.get('sections')
        if _str_list(sections):
            for sid in sections:
                if sid not in known:
                    out.append(Violation(REGISTER, 'section-id', sid,
                                         f'{label} cites a section with no anchor in the guide'))
        else:
            problems.append('sections must be a non-empty list of strings')
        check = e.get('check')
        if check is not None and not isinstance(check, str):
            check_ok = False
            problems.append('check must name one check_conformance check')
        else:
            check_ok = check is None or check in conformance
            if not check_ok:
                problems.append(f'check {check} is not a check_conformance check')
        numeric = isinstance(check, str) and check in NUMERIC_CHECKS
        ceiling = e.get('ceiling')
        ceiling_ok = isinstance(ceiling, int) and not isinstance(ceiling, bool)
        if numeric and not ceiling_ok:
            problems.append(f'a waiver of {check} needs an integer ceiling')
        elif not numeric and ceiling is not None:
            problems.append('ceiling applies only to a numeric check '
                            f'({", ".join(sorted(NUMERIC_CHECKS))})')
        artifacts = e.get('artifacts')
        artifacts_ok = _str_list(artifacts)
        if not artifacts_ok:
            problems.append('artifacts must be a non-empty list of strings')
        elif check is not None:
            for a in artifacts:
                if GLOB_CHAR_RE.search(a):
                    problems.append(f'with check set, artifacts must be explicit paths: {a}')
                    artifacts_ok = False
                elif not ((root / a).exists() or (root / a).is_symlink()):
                    problems.append(f'artifact {a} does not exist')
                    artifacts_ok = False
        else:
            for a in artifacts:
                if not any(PurePosixPath(f).full_match(a) for f in files):
                    problems.append(f'artifact glob {a} matches no file')
                    artifacts_ok = False
        for problem in problems:
            out.append(Violation(REGISTER, 'exception', '-', f'{label}: {problem}'))
        if _nonempty_str(eid) and check_ok and artifacts_ok:
            entries.append(ExceptionEntry(eid, check, artifacts, str(e.get('reason', '')),
                                          ceiling if ceiling_ok else None))
    for eid in sorted(set(ids)):
        if ids.count(eid) > 1:
            out.append(Violation(REGISTER, 'duplicate-id', '-',
                                 f'exception ID {eid} appears {ids.count(eid)} times'))
    return entries, out


def apply_waivers(violations: list[Violation], exceptions: list[ExceptionEntry],
                  reg: Register, ran: set[str]) -> list[Violation]:
    '''Waivers match both ways, per (check, file), however many violations the
    file holds: a waived pair drops out; a waiver whose file no longer violates
    its check fails; a waived file above its ceiling fails (R3.3 rule 4).
    An unwaivable violation always stands. A waiver is never called stale on
    a file its check could not evaluate, or for a check that did not run.'''
    by_pair: dict[tuple[str, str], list[Violation]] = {}
    blocked: set[tuple[str, str]] = set()
    out: list[Violation] = []
    for v in violations:
        if v.waivable:
            by_pair.setdefault((v.check, v.file), []).append(v)
        else:
            out.append(v)
            blocked.add((v.check, v.file))
    sections = {c.id: ', '.join(c.sections) for c in reg.checks}
    waived: set[tuple[str, str]] = set()
    for exc in exceptions:
        if exc.check is None or exc.check not in ran:
            continue
        for path in exc.artifacts:
            hits = by_pair.get((exc.check, path))
            if not hits and (exc.check, path) in blocked:
                continue
            if not hits:
                out.append(Violation(
                    path, 'stale-waiver', sections[exc.check],
                    f'exception {exc.id} ({exc.reason}) waives {exc.check} here, but the file '
                    'no longer violates it: remove the entry, or this file from it'))
                continue
            waived.add((exc.check, path))
            worst = max((v.value for v in hits if v.value is not None), default=None)
            if exc.ceiling is not None and worst is not None and worst > exc.ceiling:
                out.append(Violation(path, 'ceiling', sections[exc.check],
                                     f"{worst} exceeds exception {exc.id}'s ceiling of {exc.ceiling}"))
    for pair, found in by_pair.items():
        if pair not in waived:
            out.extend(found)
    return out
```

then replace `run`'s body

```python
    sections, out = guide_sections(text, guide_path)
    reg, problems = parse_register(raw)
    out += problems
    out += section_violations(reg, [s.id for s in sections if s.id])
    out += implementation_violations(reg)
    out += run_checks(root, reg, kind_files(reg, files))
    return sorted(v.render() for v in out)
```

with

```python
    sections, out = guide_sections(text, guide_path)
    anchors = [s.id for s in sections if s.id]
    reg, problems = parse_register(raw)
    exceptions, exception_problems = parse_exceptions(raw, reg, anchors, files, root)
    out += problems + exception_problems
    out += section_violations(reg, anchors)
    out += implementation_violations(reg)
    kinds = kind_files(reg, files)
    ran = {c.id for c in reg.checks if _runnable(c) and all(k in kinds for k in c.kinds)}
    out += apply_waivers(run_checks(root, reg, kinds), exceptions, reg, ran)
    return sorted(v.render() for v in out)
```

- [x] **Step 4: Run; all green.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `78 passed` (+26).

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && uv run --python 3.13 --with pyyaml python build/check_conformance.py; echo "exit=$?"`
Expected: Task 6 Step 5's day-one lines, unchanged, since the register has no exceptions yet (the CLAUDE.md count is as measured):

```text
CLAUDE.md: claude-md-size (rules.claude-md): 238 lines; the guide targets fewer than 200
agents/code-reviewer.md: bash-search-tools (subagents.tools): lists Grep and Glob beside Bash, where both are absent and search runs through the shell
agents/debugger.md: bash-search-tools (subagents.tools): lists Grep and Glob beside Bash, where both are absent and search runs through the shell
agents/docs-writer.md: bash-search-tools (subagents.tools): lists Grep and Glob beside Bash, where both are absent and search runs through the shell
agents/explore.md: bash-search-tools (subagents.tools): lists Grep and Glob beside Bash, where both are absent and search runs through the shell
agents/security-auditor.md: bash-search-tools (subagents.tools): lists Grep and Glob beside Bash, where both are absent and search runs through the shell
agents/task-reviewer.md: bash-search-tools (subagents.tools): lists Grep and Glob beside Bash, where both are absent and search runs through the shell
agents/test-runner.md: bash-search-tools (subagents.tools): lists Grep and Glob beside Bash, where both are absent and search runs through the shell
hooks/README.md: hook-dir-quoted (hooks.patterns): JSON block at line 51: PostToolUse command leaves $CLAUDE_PROJECT_DIR unquoted
hooks/README.md: hook-dir-quoted (hooks.patterns): JSON block at line 51: PreToolUse command leaves $CLAUDE_PROJECT_DIR unquoted
hooks/README.md: hook-dir-quoted (hooks.patterns): JSON block at line 51: Stop command leaves $CLAUDE_PROJECT_DIR unquoted
exit=1
```

- [x] **Step 5: Full build suite.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q`
Expected: the baseline's failures and skips unchanged, and passed +80 over baseline.

- [x] **Step 6: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && [ "$(git branch --show-current)" = feat/cc-guide-conformance ] && git add build/check_conformance.py build/test_check_conformance.py && git commit -m "feat(build): add conformance exceptions and both-way waivers

Validates each [[exception]] (type-specific fields, cited sections and
check, explicit existing paths for a waiver, matching globs otherwise,
unique IDs) and applies waivers per (check, file): a waived violation
drops out, a waiver whose file no longer violates fails as stale, and a
waived file above its ceiling fails. A finding the check could not
evaluate is never waived, and neither it nor a check that did not run
makes a waiver stale.

Plan 35, Task 7.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: The one-time audit (R5.1–R5.4)

**Controller task — execute directly, not via an implementer subagent.** It dispatches four audit seats, and implementer subagents cannot dispatch.

**Files:**
- Create: `specs/claude-code-conformance-audit-<YYYY-MM-DD>.md` (today's date)
- Scratch (gitignored, never committed): `.sdd/35-claude-code-guide-conformance/audit/` holding `regrep.py`, `quotes.tsv` and each seat's raw report.

**Interfaces:**
- Consumes: the day-one lint output (Task 6 Step 5); the register (Task 2).
- Produces: the report. Row IDs are stable: `L-01`…`L-11` for the lint lines in their sorted order, and per seat `S-nn` (skills), `A-nn` (agents and commands), `H-nn` (hooks, rules, settings), `C-nn` (CLAUDE.md, installer) and `O-nn` (outside the repo). A seat's guide notes take IDs in its own sequence. Task 9 decides on rows by ID, and Task 11 cites them as `evidence`. Rows whose quotes failed the re-grep are listed as unverified and are never decided or cited.

- [x] **Step 1: Record the mechanical findings.** Run the lint and number its lines in output order:

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && uv run --python 3.13 --with pyyaml python build/check_conformance.py | nl -w1 -s' '`
Expected: the 11 lines of Task 6 Step 5. They become:
- `L-01`: `claude-md-size` on `CLAUDE.md`.
- `L-02`–`L-08`: `bash-search-tools` on the 7 agents, alphabetical.
- `L-09`–`L-11`: `hook-dir-quoted` on `hooks/README.md` (PostToolUse, PreToolUse, Stop).

- [x] **Step 2: Resolve the inputs the seats need.** Run `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance worktree list`. Its first line is the main checkout, whose `.claude/settings.local.json` R5.3 names. Record that absolute path for seat H.

- [x] **Step 3: Dispatch the four seats in parallel**, in one message with four `Agent` calls: `subagent_type: 'code-reviewer'`, `model: 'sonnet'` on every call, and a description naming the seat. Fill this template once per seat from the table below, and fill `<LINT_ROWS>` with Step 1's lines as `L-nn | check | file | message`, one per line. `code-reviewer`'s frontmatter keeps `effort: xhigh`, which the Agent tool cannot override, so expect a few dollars per seat.

```text
You are one seat of a four-seat audit of this repo's Claude Code artifacts against
its Claude Code customization guide (plan 35, Task 8; spec R5). Replace your usual
Strengths/Issues report with the report contract below. This audit is read-only:
never create, edit, move or delete a file, and run only single-line Bash commands
(no trailing-backslash continuations; quote inline code with single quotes).

Worktree: /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance
Every repo path below is relative to the worktree; the main checkout has neither the
guide's anchors nor the register. Read files by their absolute path under the
worktree, and begin every Bash command with this prefix:
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance &&
Guide: specs/guides/claude-code-customization-guide.md. Each section starts at a
## or ### heading followed by a <!-- cc: <id> --> line, and runs to the next heading.
Register: build/cc_guide/conformance.toml (kinds and their globs; the seven checks).
The lint's own findings are already rows. Cite their IDs, and add no row for the same
file and rule:
<LINT_ROWS>

Seat: <SEAT>. Row-ID prefix: <P> (number your rows <P>-01, <P>-02, ...).
Sections: <SECTIONS>
Artifacts: <ARTIFACTS>
Notes for this seat: <NOTES>

Method, for each section:
1. Read the section. List each rule in it that bears on your artifacts.
2. Classify each rule as fact (a docs page could confirm or refute it: a name,
   default, number, behaviour, precedence or syntax) or advice (a recommendation).
3. Check every artifact against each rule.

Report, in this order:
A. A Markdown table with columns: ID | section | guide line | rule (your paraphrase,
   at most 12 words) | fact/advice | artifact file:line | status | guide quote |
   artifact quote.
   Status is one of: follows; gap (contradicts a fact, or departs from advice with no
   recorded reason); deviation candidate (departs on purpose, for a reason you can
   cite: a spec decision, a code comment, a skill rule); n/a (the rule bears on none
   of your artifacts).
   Write one row per artifact that is a gap or a deviation candidate. For a rule every
   artifact follows, write one row whose artifact is the glob and file count, with no
   artifact quote. Write one row per n/a rule.
   Quotes are verbatim, at most 25 words, each taken from a single line: the guide
   quote from the guide, the artifact quote from the artifact.
B. A fenced tsv block with one line per quote: <row ID><TAB><repo-relative file><TAB><quote>.
C. Proposed mechanical checks: rules a script could check that the lint's seven do not.
D. Section-map notes: a listed section that governs none of your artifacts, or an
   unlisted section that should.
E. Guide notes: a guide line you judge wrong, stale or self-contradictory. Give it
   an ID in your sequence, its guide line, a verbatim single-line guide quote of at
   most 25 words (with a section-B tsv line), and a one-line reason.
Do not propose fixes. Do not judge the guide's own correctness beyond noting it in E.
```

| Seat (prefix) | Sections | Artifacts | Notes |
|---|---|---|---|
| Skills (`S`) | `skills.overview`, `skills.locations`, `skills.frontmatter`, `skills.description`, `skills.listing-budget`, `skills.progressive-disclosure`, `skills.arguments`, `skills.iterating`, `commands.overview`, `mechanisms.overview`, `lean.ceremony`, `lean.expensive-ops`; and `rules.hierarchy`, only for the `writing-skills` line-304 candidate | `skills/*/SKILL.md` (the register's skill kind; `ls skills/*/SKILL.md`) | R5.7 candidates to confirm or reject. `writing-skills`: its body (696 lines at `54fc246`) against `skills.overview`; its line-222 claim that every description stays resident against `skills.listing-budget`; its line-304 `@`-loading claim against `rules.hierarchy`; no advice to put critical rules first against `skills.progressive-disclosure`. `brainstorming`: "Every project goes through this process" against `lean.ceremony`. Skip line 25 of `skills/writing-skills/SKILL.md` and all of `skills/writing-skills/anthropic-best-practices.md`: provenance is the owner's call. List the skills that are side-effecting yet model-invocable, for R2.7's `side-effecting-skills-invocable` |
| Agents and commands (`A`) | `subagents.overview`, `subagents.frontmatter`, `subagents.tools`, `subagents.models`, `subagents.isolation`, `commands.overview`, `skills.frontmatter`, `skills.arguments`, `skills.description` | `agents/*.md` (7), `commands/*.md` (3) | R5.7 candidates. `commands/` stays as command files, while `commands.overview` says the docs recommend skills for new work. The command files generate the Gemini adapters (`runtimes/gemini/commands/`). The reviewer agents hold Bash, guarded by the read-only hook, beside `subagents.tools`' reviewer set |
| Hooks, rules, settings (`H`; outside files `O`) | `hooks.overview`, `hooks.events`, `hooks.exit-codes`, `hooks.handlers`, `hooks.configuration`, `hooks.patterns`, `hooks.pitfalls`, `mechanisms.overview`, `rules.rules-files`, `rules.hierarchy`, `rules.settings`, `lean.model-routing`; for the `O` table only, also `rules.claude-md`, `context.overview` and `lean.session-hygiene`, applied to `~/.claude/CLAUDE.md` | `hooks/*.sh`, `hooks/*.py` except `hooks/test_*.py`, `hooks/README.md`, `rules/*.md`, `.claude/rules/*.md`, `.claude/settings.json` | R5.7 candidates. `enforceAvailableModels` is set in project settings, while `lean.model-routing` places its effect in managed settings. The guard is stdlib-only with no dependencies, against `hooks.pitfalls`' advice on `uv` inline deps. At `hooks/README.md:121` the guard's install command leaves `$HOME` unquoted. Ignore the section's `TODO(owner)` bullet. **Also, in a separate `O` table**, read by absolute path (R5.3): `~/.claude/CLAUDE.md`, `~/.claude/settings.json`, `~/.claude/rules/*`, and `<MAIN_CHECKOUT>/.claude/settings.local.json`. For these four: paraphrase only, give no quotes and no tsv lines, and never reproduce a value that looks like a credential (token, key, password, URL with credentials). R5.7 outside candidates: the AWS rule has no `paths`; `settings.local.json` allows `Bash(pip install *)` |
| CLAUDE.md and installer (`C`) | `rules.claude-md`, `rules.hierarchy`, `context.overview`, `lean.session-hygiene`, `skills.locations`, `subagents.overview`, `commands.overview`; plus `mechanisms.overview` (not mapped to claude-md today), and the seven `[unmapped]` sections (`rules.overview`, `lean.overview`, `rules.auto-memory`, `lean.measure`, `lean.caching`, `lean.mcp`, `reading.overview`): confirm each governs no repo file, or name the file and kind | `CLAUDE.md`, `build/CLAUDE.md`, `install.py`; `AGENTS.md` and `GEMINI.md` only for how they reach CLAUDE.md | R5.7 candidates. CLAUDE.md's length against `rules.claude-md` (already `L-01`: cite it, don't repeat it). Its "run before committing" lints are prose where `mechanisms.overview` would use a hook |

- [x] **Step 4: Re-grep every quote (R5.2).** Save each seat's raw report under `.sdd/35-claude-code-guide-conformance/audit/<prefix>.md`. Concatenate the four `tsv` blocks into `.sdd/35-claude-code-guide-conformance/audit/quotes.tsv`, and create `.sdd/35-claude-code-guide-conformance/audit/regrep.py`:

```python
'''Re-grep the audit's quotes (plan 35, R5.2). Scratch only; never committed.

stdin: one `row-id<TAB>file<TAB>quote` row per line, file relative to the
current directory (run from the worktree root). Each quote must sit inside a
single line of its file and run at most 25 words. Prints one line per failing
row and exits 1 if any row fails; otherwise prints the count and exits 0.
'''
import sys
from pathlib import Path

rows = failed = 0
for raw in sys.stdin:
    if not raw.strip():
        continue
    rows += 1
    row_id, path, quote = (raw.rstrip('\n').split('\t') + ['', ''])[:3]
    problems = []
    if not quote:
        problems.append('no quote')
    elif len(quote.split()) > 25:
        problems.append(f'{len(quote.split())} words')
    try:
        if quote and not any(quote in line for line in Path(path).read_text().splitlines()):
            problems.append('not found on any single line')
    except OSError as exc:
        problems.append(f'unreadable ({exc.strerror})')
    if problems:
        failed += 1
        print(f'{row_id}\t{path}\t{"; ".join(problems)}\t{quote}')
print(f'{rows - failed} of {rows} quotes verified', file=sys.stderr)
sys.exit(1 if failed else 0)
```

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && uv run --python 3.13 python .sdd/35-claude-code-guide-conformance/audit/regrep.py < .sdd/35-claude-code-guide-conformance/audit/quotes.tsv`
Expected: exit 0 and `N of N quotes verified` on stderr. Otherwise each stdout line is a failing quote: row ID, file, reason, quote. A row with a failing quote is discarded from the findings and listed as unverified, the refresh's rule (drift R8.8 step 1). Never repair or substitute quote text. Record each failing line for the report's "Unverified rows" section, delete every `quotes.tsv` line of that row, and rerun until it exits 0. Only verified rows enter the findings.

- [x] **Step 5: Write the report** `specs/claude-code-conformance-audit-<YYYY-MM-DD>.md` with these sections, in order:
  1. **Header:** date; worktree `HEAD` SHA; the guide at 2.1.288; method (R5.2); the four seats (agent `code-reviewer`, model `sonnet`); quotes re-grepped (`N of N verified`) and the count of rows discarded as unverified.
  2. **Mechanical findings:** `L-01`–`L-11`, each as `ID | check | section | file | message`.
  3. **Findings by group:** the four seat tables as returned, minus unverified rows, rows keeping their IDs.
  4. **R5.7 candidates:** each candidate, confirmed or rejected, with its row ID.
  5. **Section map:** proposed changes to `[kinds]` or `[unmapped]`, with the row that supports each, or "none".
  6. **Proposed checks (R5.6):** one line each. These become deferred items, never checks in this plan.
  7. **Guide notes (to the owner; for drift's `/cc-guide verify` once it exists):** each seat's section-E notes, with row ID and verified quote, or "none". Report-only: nothing here edits the guide.
  8. **Outside the repo (R5.3):** the `O` rows, paraphrased, report-only. Nothing here enters the register.
  9. **Unverified rows:** each discarded row's ID, file, failing quote and regrep.py's reason, or "none". The gate does not decide them.
  10. **Owner decisions:** the heading only, with the line "Filled at the plan 35 owner gate (Task 9)."

Quotes appear only from the guide and the repo's own files. No docs text is committed.

> Deviation: in row O-12 the controller paraphrased three words the seat had quoted from
> `~/.claude/CLAUDE.md`, outside the repo, under this step's quote rule; the report's §8
> records it. No other seat text changed.

- [x] **Step 6: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && [ "$(git branch --show-current)" = feat/cc-guide-conformance ] && git add specs/claude-code-conformance-audit-*.md && git commit -m "docs(specs): record the Claude Code guide conformance audit

Four read-only seats (code-reviewer at Sonnet) audited the repo's skills,
agents, commands, hooks, rules, settings, CLAUDE.md files and installer
against all 38 guide sections; the lint's 11 day-one violations are rows
L-01..L-11. Every quote was re-grepped, and rows whose quotes failed are
listed as unverified. The four files outside the repo are reported,
paraphrased, and enter nothing.

Plan 35, Task 8.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: Owner gate (R5.5)

**Controller task — it needs the owner.** Present everything below as one batch, end the turn, and resume when the owner answers. No register entry, trim or deferred item is written before the answers arrive.

**Files:**
- Modify: `specs/claude-code-conformance-audit-<YYYY-MM-DD>.md` (fill "Owner decisions")

**Interfaces:**
- Consumes: the report's gap and deviation-candidate rows, R5.7 dispositions, section-map notes, proposed checks and guide notes.
- Produces, for Tasks 10–11 and completion:
  - One decision per row group: a deviation, a gap, or a correction of the seat's status.
  - The CLAUDE.md figures (`L`, `G`, `P`), the choice (A or B), the `claude-md-size` exception's type, `tracked_in` or `revisit`, and ceiling.
  - Any map changes.
  - The routing of each guide note.
  - The list of deferred items to log at completion.

- [x] **Step 1: Measure CLAUDE.md now** (the user asked for gate-time figures):
  - `wc -l < /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/CLAUDE.md` gives `L`, the worktree's length.
  - `git -C /Users/lowell/Projects/agent-skills show main:CLAUDE.md | wc -l` gives `M`, main's length.
  - `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance show $(git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance merge-base main HEAD):CLAUDE.md | wc -l` gives `B`, the length at the worktree's base.
  - `G = M − B` is main's CLAUDE.md growth since the worktree was cut, and `P = L + G` is the length a merge into main would give, absent conflicts. While main has not touched CLAUDE.md, `G = 0` and `P = L`. Tasks 10 and 14 use `G` and `P` as defined here.
  - For each of `codex/recommend-causal-design` and `worktree-deferred-triage-2026-10-03`, first check that the branch still exists: `git -C /Users/lowell/Projects/agent-skills rev-parse --verify --quiet refs/heads/<branch>`. If that prints nothing, report "branch gone: if it merged, `M` already counts it" and skip the branch. Otherwise check whether it is merged: `git -C /Users/lowell/Projects/agent-skills merge-base --is-ancestor <branch> main && echo merged || echo unmerged`. If it is unmerged, measure its CLAUDE.md delta: `git -C /Users/lowell/Projects/agent-skills diff --numstat $(git -C /Users/lowell/Projects/agent-skills merge-base main <branch>) <branch> -- CLAUDE.md`. On 2026-10-04 they were +1 and +3 net.

- [x] **Step 2: Present the batch.**
  - **(a) Each gap or deviation candidate**, in a table: `row ID(s) | artifact | section | fact/advice | audit status | proposed type | proposed destination or revisit`.
    - Group rows by root cause, as R2.7 does: one entry per cause, not per file.
    - Propose R5.5's default destinations: the three known drifts go to drift Stage 3; `check_frontmatter.py` findings to portability Stage A; `writing-skills` findings to portability Stage D; anything else to a deferred item, flagged for `/deferred` when it is a quick fix.
    - Show R2.7's expected entries with their defaults:
      - `grep-glob-beside-bash`: gap, `protects = ['gemini']`, drift Stage 3.
      - `hook-dir-unquoted`: gap, drift Stage 3.
      - `description-when-only`: deviation, revisit when trigger-eval suites exist.
      - `side-effecting-skills-invocable`: deviation, listing seat S's skills, revisit when the guide documents a hand-off to a manual-only skill.
    - The owner confirms or changes each one: a deviation, with its reason and revisit trigger; a gap, with its destination; or a correction, when the seat's status was wrong, setting it to follows or n/a with a reason. A corrected row gets no register entry.
    - List the report's unverified rows separately, marked unverified, for information. The owner may ask for a fresh re-check; they are not decided.
  - **(b) CLAUDE.md**, asked with `AskUserQuestion`. Show `L`, `M`, `G`, `P` and each unmerged branch's delta from Step 1.
    - **A. Trim to 225 without dropping any instruction.** Task 10 rejoins hard-wrapped prose paragraphs and `\`-continued commands into single lines until `P` ≤ 225. Every word stays, and a script proves it. Then `ceiling = 225`.
    - **B. Raise the limit and state why.** CLAUDE.md stays as it is. The `claude-md-size` exception's `ceiling` becomes a value the owner names, at least `P`, with the owner's reason. The check's `limit` keeps the guide's 200 (Decision 5): B raises the ceiling, not the guide's figure. Task 10 is skipped.
    - Also ask whether the exception is a **gap** (`tracked_in`, such as a deferred item to bring CLAUDE.md under 200 lines) or a **deviation** (`revisit` trigger).
    - State what follows for the unmerged branches. Once the ceiling lands, the lint fails any merge that takes CLAUDE.md over it, so a branch whose delta does not fit must trim at its merge or raise the ceiling there on purpose, with a reason. No spec rule binds those branches; under B the owner may leave headroom now instead.
  - **(c) Section-map changes** the report proposes, each confirmed or declined.
  - **(d) Proposed checks (R5.6):** confirm that each becomes a deferred item.
  - **(e) Outside the repo:** the `O` rows, for the owner's information. Ask only whether any should become a deferred item for the owner. This plan edits none of them (Decision 13).
  - **(f) Guide notes** (the spec's Purpose: a finding that the guide itself is wrong goes to the owner, and to drift's `verify` once that exists). For each note, the owner chooses a deferred item to run `/cc-guide verify <section id>` (drift R8.5) once drift lands, or no action. Nothing edits the guide here, since the scope fence allows only Task 1's anchors, and nothing enters the register.

> Deviation: after the batch was presented, the owner asked for the questions to be put
> interactively, so the gate was decided in AskUserQuestion rounds. The owner chose every
> answer; the controller chose none.

- [x] **Step 3: Record the answers** under "Owner decisions" in the report. Write one line per decision: the row IDs, the type, the reason, the revisit trigger or destination, the CLAUDE.md choice with `L`, `G`, `P` and the ceiling, the map changes, each guide note's routing, and the deferred-item list. For a corrected row, also append `(owner: <status>, see Owner decisions)` to its row in the group table; never rewrite the seat's text. Add the date. Then commit:

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && [ "$(git branch --show-current)" = feat/cc-guide-conformance ] && git add specs/claude-code-conformance-audit-*.md && git commit -m "docs(specs): record the owner's conformance gate decisions

Each gap or deviation candidate from the audit now has the owner's
disposition: a deviation with its reason and revisit trigger, a gap with
its destination, or a corrected status; plus the CLAUDE.md length choice
and ceiling, any section-map changes, each guide note's routing, and the
deferred items to log at completion.

Plan 35, Task 9.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

> Deviation: the Step 3 commit (c6b7313) also corrected a sentence of the report's §2,
> written at Task 8: four checks found nothing, and `claude-md-size` passed
> `build/CLAUDE.md`, where §2 had said the other five checks found nothing.

---

### Task 10: CLAUDE.md catch-up trim — only if the gate chose A

**If the owner chose B, skip this task.** Mark every step `> Skipped: owner chose B (ceiling set at the gate)`. This trim is the JAX catch-up the spec's Sequencing section assigns to whichever lands second. It is separate from R4's own net-zero trim (Task 12).

**Files:**
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: the gate's choice A, `L` and `G`, recorded under the audit report's "Owner decisions" (Task 9). `G` is main's CLAUDE.md growth since the worktree was cut, usually 0.
- Produces: CLAUDE.md at ≤ 225 − `G` lines, so a merge gives ≤ 225 (`P` ≤ 225), with an unchanged word sequence. Task 11's ceiling and Task 12's trim build on it.

The method is lossless reformatting, never rewording. Each candidate below joins a hard-wrapped paragraph or a `\`-continued command into one line. Other sections, and many commands in the same block, already use single long lines, and Markdown renders a soft-wrapped paragraph the same. None of the candidates touches a region the unmerged branches edit. Apply them in order until `wc -l` ≤ 225 − `G`. On `54fc246` (`L` = 238, `G` = 0), U1 and U2 together save 13 and reach exactly 225. The candidates total 24 lines; if they run out first, stop and take the figures back to the owner.

- [x] **Step 1: Write the check.** Create `.sdd/35-claude-code-guide-conformance/words_unchanged.py`:

```python
'''Exit 0 when CLAUDE.md's word sequence equals HEAD's, lone backslashes
aside: a pure rewrap or line join, which drops no instruction (plan 35).
Run from the worktree root. Scratch only; never committed.'''
import subprocess
import sys
from pathlib import Path

head = subprocess.run(['git', 'show', 'HEAD:CLAUDE.md'], capture_output=True,
                      text=True, check=True).stdout
now = Path('CLAUDE.md').read_text()


def words(text):
    return [w for w in text.split() if w != '\\']


if words(head) != words(now):
    sys.exit('CLAUDE.md word sequence differs from HEAD: not a pure rewrap')
print(f'word sequence unchanged; {len(head.splitlines())} -> {len(now.splitlines())} lines')
```

- [x] **Step 2: Apply candidates in order** until the file is ≤ 225 − `G` lines. Each replaces its exact old text (shown as of `54fc246`) with one line.

**U1 — "What this repo is", first paragraph (saves 10).** Replace

```markdown
A personal collection of coding-agent configuration, centered on the portable
[Agent Skills specification](https://agentskills.io/specification). Skills live
under `skills/` — each subdirectory is **one self-contained skill**: a
`SKILL.md` plus optional `references/` (loaded on demand) and `scripts/`
(executable helpers). Sibling top-level dirs hold the other config types:
`agents/` (canonical Claude-format subagent definitions), `commands/`
(canonical Claude slash commands), `runtimes/` (generated Codex and Gemini
adapters), `hooks/` (Claude Code hook templates and its read-only-agent guard),
and `rules/` (Claude Code path-scoped rules). There is no application here to
run — the "product" is the skill text, companion configuration, and bundled
scripts.
```

with

```markdown
A personal collection of coding-agent configuration, centered on the portable [Agent Skills specification](https://agentskills.io/specification). Skills live under `skills/` — each subdirectory is **one self-contained skill**: a `SKILL.md` plus optional `references/` (loaded on demand) and `scripts/` (executable helpers). Sibling top-level dirs hold the other config types: `agents/` (canonical Claude-format subagent definitions), `commands/` (canonical Claude slash commands), `runtimes/` (generated Codex and Gemini adapters), `hooks/` (Claude Code hook templates and its read-only-agent guard), and `rules/` (Claude Code path-scoped rules). There is no application here to run — the "product" is the skill text, companion configuration, and bundled scripts.
```

**U2 — "What this repo is", second paragraph (saves 3).** Replace

```markdown
`install.py` installs skills and companion assets for Claude, Codex, Gemini, or
all three. Claude uses `~/.claude/skills/`; Codex and Gemini share
`~/.agents/skills/`. This repo *is* the user's symlinked source, so edits here
are live.
```

with

```markdown
`install.py` installs skills and companion assets for Claude, Codex, Gemini, or all three. Claude uses `~/.claude/skills/`; Codex and Gemini share `~/.agents/skills/`. This repo *is* the user's symlinked source, so edits here are live.
```

**U3 — "Runtime adapters", second paragraph (saves 3).** Replace

```markdown
The generator translates manifest syntax and Gemini tool names only. Codex and
Gemini agents inherit the active runtime model; Claude-specific model pins do
not cross runtimes. Gemini gets TOML command adapters. Codex has no command
adapter here; reusable Codex workflows are skills.
```

with

```markdown
The generator translates manifest syntax and Gemini tool names only. Codex and Gemini agents inherit the active runtime model; Claude-specific model pins do not cross runtimes. Gemini gets TOML command adapters. Codex has no command adapter here; reusable Codex workflows are skills.
```

**U4 — the opening paragraph (saves 2).** Replace

```markdown
This file is the canonical maintainer guide for Claude Code, Codex, and Gemini
CLI when working in this repository. `AGENTS.md` points Codex here and
`GEMINI.md` imports it.
```

with

```markdown
This file is the canonical maintainer guide for Claude Code, Codex, and Gemini CLI when working in this repository. `AGENTS.md` points Codex here and `GEMINI.md` imports it.
```

**U5 — "Runtime adapters", first paragraph (saves 2).** Replace

```markdown
`agents/*.md` and `commands/*.md` are canonical. Never hand-edit files under
`runtimes/`. After changing a canonical agent or command, regenerate and check
the adapters:
```

with

```markdown
`agents/*.md` and `commands/*.md` are canonical. Never hand-edit files under `runtimes/`. After changing a canonical agent or command, regenerate and check the adapters:
```

**J1 — the dependency-drift command (saves 1).** Replace

```text
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q \
  test_runtime_support.py -k declared_dependencies
```

with

```text
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies
```

**J2 — the "Single test" command (saves 1).** Replace

```text
cd build && uv run --python 3.13 --with pytest --with numpy --with polars \
  python -m pytest test_verify_citations.py::test_true_negative_flags_bad_refs
```

with

```text
cd build && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest test_verify_citations.py::test_true_negative_flags_bad_refs
```

**J3 — the deep-learning CPU-examples command (saves 2).** Replace

```text
JAX_PLATFORMS=cpu uv run --python 3.13 \
  --with-requirements specs/verification/32-jax-cpu.txt \
  python build/check_jax_examples.py skills/deep-learning/
```

with

```text
JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/deep-learning/
```

- [x] **Step 3: Verify.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && uv run --python 3.13 python .sdd/35-claude-code-guide-conformance/words_unchanged.py && wc -l < CLAUDE.md`
Expected: `word sequence unchanged; L -> M lines` with `M` ≤ 225 − `G`, then `M`.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && git diff --word-diff=porcelain -- CLAUDE.md | grep '^[-+][^-+]' | grep -cv '^-\\$'`
Expected: `0` (and exit 1, as `grep -c` gives on a zero count). Apart from the line-continuation backslashes the J candidates drop, which the second `grep` sets aside, a pure rewrap adds and removes no words.

- [x] **Step 4: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && [ "$(git branch --show-current)" = feat/cc-guide-conformance ] && git add CLAUDE.md && git commit -m "docs: rejoin hard-wrapped CLAUDE.md paragraphs to meet the 225-line ceiling

The owner chose to trim CLAUDE.md to 225 lines at the plan 35 gate. Every
change joins a hard-wrapped paragraph or a backslash-continued command
into one line; the word sequence is unchanged, so no instruction moves or
drops, and Codex and Gemini read the same content.

Plan 35, Task 10.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 11: Finish the register; the lint goes green (R2.6–R2.7, R3.5's repo run)

**Files:**
- Modify: `build/cc_guide/conformance.toml` (append the exceptions; apply any map changes)
- Modify: `build/test_check_conformance.py` (append 1 test)

**Interfaces:**
- Consumes: Task 9's recorded decisions; Task 7's exception schema; the audit's row IDs.
- Produces: a register whose lint run on the repo exits 0, and `test_repo_passes`.

- [x] **Step 1: Write the failing repo test.** Append to `build/test_check_conformance.py`:

```python
def test_repo_passes():
    '''The real repo, with the register the owner gate filled, is clean (R3.5).'''
    assert cc.run(cc.REPO) == []
```

- [x] **Step 2: Run; confirm RED.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `1 failed, 78 passed`. `test_repo_passes` lists the 11 day-one lines; under choice A, `L-01` reports the trimmed count.

- [x] **Step 3: Apply any map changes the owner confirmed** to `[kinds.*].sections` and `[unmapped]`. A section moves out of one and into the other, never both. Then append the exceptions below. Values the gate fixed replace the defaults shown:
  - for `claude-md-size`: `type`, `ceiling`, and `tracked_in` or `revisit`, plus the gate date in its `evidence`;
  - for `side-effecting-skills-invocable`: `artifacts` (seat S's list, explicit paths);
  - the audit row IDs (`S-nn`) in each `evidence`;
  - in the section comment, the gate date and the audit report's file name (both `YYYY-MM-DD`).

  Drop any entry the owner declined. A row the owner corrected to follows or n/a gets no entry, and no `evidence` cites an unverified row. Then add one `[[exception]]` per further gate decision, in the same shape:
  - `id`: kebab-case and unique.
  - `type`.
  - `sections`.
  - `artifacts`: explicit existing paths when `check` is set; globs allowed otherwise.
  - `guide`: the guide's rule paraphrased.
  - `reason`: the owner's.
  - `evidence`: the row IDs and the gate date.
  - `tracked_in` for a gap, or `revisit` for a deviation.

  A gap routed to a deferred item gets `tracked_in = 'deferred item: <title>'`, and that item, written at completion, names this exception as the one its fix must remove (R5.5). Write every value in the repo's own words; no docs text.

```toml
# ---------------------------------------------------------------------------
# Exceptions, decided by the owner at the plan 35 gate (YYYY-MM-DD) on the
# audit in specs/claude-code-conformance-audit-YYYY-MM-DD.md. A deviation is
# deliberate and names its revisit trigger; a gap is known non-conformance and
# names where its fix lands. A waiver (check set) lists explicit paths, and
# when its file stops violating, the lint fails until the entry is narrowed.
# ---------------------------------------------------------------------------

# All seven agents list Grep and Glob beside Bash (drift's known drift #1).
[[exception]]
id = 'grep-glob-beside-bash'
type = 'gap'
check = 'bash-search-tools'
sections = ['subagents.tools']
artifacts = [
    'agents/code-reviewer.md', 'agents/debugger.md', 'agents/docs-writer.md',
    'agents/explore.md', 'agents/security-auditor.md', 'agents/task-reviewer.md',
    'agents/test-runner.md',
]
guide = 'On macOS, Linux and WSL an agent that lists Bash gets no Grep or Glob.'
reason = 'The Gemini adapters map Grep and Glob to working tools, so deleting them from the canonical files would regress Gemini.'
evidence = 'Drift spec R11.5 #1; audit rows L-02 to L-08.'
protects = ['gemini']
tracked_in = 'drift Stage 3, first files batch (drift spec R11.5 #1)'

# hooks/README.md's install snippet leaves $CLAUDE_PROJECT_DIR unquoted
# three times (drift's known drift #3).
[[exception]]
id = 'hook-dir-unquoted'
type = 'gap'
check = 'hook-dir-quoted'
sections = ['hooks.patterns']
artifacts = ['hooks/README.md']
guide = 'A hook command keeps $CLAUDE_PROJECT_DIR in double quotes.'
reason = 'The README install snippet predates the quoted pattern.'
evidence = 'Drift spec R11.5 #3; audit rows L-09 to L-11.'
tracked_in = 'drift Stage 3, first files batch (drift spec R11.5 #3)'

# The root CLAUDE.md is over the docs target. The owner set its type,
# ceiling and tracked_in or revisit at the gate (the audit report's Owner
# decisions); a deviation would carry revisit instead of tracked_in.
[[exception]]
id = 'claude-md-size'
type = 'gap'
check = 'claude-md-size'
sections = ['rules.claude-md']
artifacts = ['CLAUDE.md']
guide = 'The docs target fewer than 200 lines per CLAUDE.md file.'
reason = 'Codex and Gemini read the same file, so instructions leave it only by deliberate condensing or relocation.'
evidence = 'Audit row L-01; owner gate YYYY-MM-DD.'
ceiling = 225
tracked_in = 'deferred item: bring the root CLAUDE.md under 200 lines'

# writing-skills keeps descriptions trigger-only on tested evidence.
[[exception]]
id = 'description-when-only'
type = 'deviation'
sections = ['skills.description']
artifacts = ['skills/*/SKILL.md']
guide = 'A description states what the skill does and when to use it.'
reason = 'writing-skills requires trigger-only Use when descriptions, on tested evidence that a workflow summary lets agents skip the body.'
evidence = 'writing-skills, Skill Discovery Optimization; portability spec Decision 4; audit rows S-nn.'
revisit = 'When trigger-eval suites exist (a portability deferred item).'

# Other skills hand off to these by bare name. artifacts is seat S's list.
[[exception]]
id = 'side-effecting-skills-invocable'
type = 'deviation'
sections = ['commands.overview', 'skills.frontmatter']
artifacts = ['skills/finishing-a-development-branch/SKILL.md', 'skills/using-git-worktrees/SKILL.md']
guide = 'A side-effecting workflow sets disable-model-invocation: true.'
reason = 'Other skills hand off to these by bare name, which a manual-only skill cannot receive; their bodies gate the side effects.'
evidence = 'Portability spec Decision 3; audit rows S-nn.'
revisit = 'When the guide documents a way for one skill to hand off to a manual-only skill.'
```

> Deviation: `[kinds.settings]` was reflowed onto several lines, like `[kinds.rule]`
> (formatting only; same values and order). On the owner's completion-gate answers
> (b601eed), two reasons were aligned with the report's §10:
> `side-effecting-skills-invocable` now ends "their bodies gate the side effects, some only
> in part.", and `writing-skills-guide-gaps` states the skill's departures instead of a
> cause.

- [x] **Step 4: Run; all green.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && uv run --python 3.13 --with pyyaml python build/check_conformance.py; echo "exit=$?"`
Expected: `exit=0` with no other output.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && grep -nE 'YYYY|S-nn' build/cc_guide/conformance.toml`
Expected: no output, and exit 1. A leftover placeholder would pass the lint, which checks only that each field is a non-empty string.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: `79 passed` (+1). The build suite is now +81 over baseline.

- [x] **Step 5: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && [ "$(git branch --show-current)" = feat/cc-guide-conformance ] && git add build/cc_guide/conformance.toml build/test_check_conformance.py && git commit -m "feat(build): fill the conformance register from the owner's gate

Records every owner-decided exception: gaps name where their fix lands,
deviations name their revisit trigger, and waivers list explicit paths
(with a ceiling on claude-md-size). The lint now passes on the repo, and
test_repo_passes keeps it that way.

Plan 35, Task 11.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 12: The authoring rule and CLAUDE.md (R4)

**Files:**
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: the green lint (Task 11); CLAUDE.md as Task 10 left it.
- Produces: R4.1's rule, R4.2's command, R4.3's net-zero trim and the build-suite count deltas, all in one commit.

- [x] **Step 1: Trim first, losslessly.** Replace the "Build tooling" paragraph (5 lines; untouched by the unmerged branches):

```markdown
Most of `build/` is the citation-verification pipeline for
`recommend-probabilistic-model`; see `build/CLAUDE.md` for its gates and ground
truth. `sync_runtime_assets.py` is the separate cross-runtime adapter
generator. **`build/.scratch/` is gitignored and must never be committed** — it
contains own-use extraction of CC-BY-NC-ND material.
```

with one line:

```markdown
Most of `build/` is the citation-verification pipeline for `recommend-probabilistic-model`; see `build/CLAUDE.md` for its gates and ground truth. `sync_runtime_assets.py` is the separate cross-runtime adapter generator. **`build/.scratch/` is gitignored and must never be committed** — it contains own-use extraction of CC-BY-NC-ND material.
```

Then check it. Task 10 created `.sdd/35-claude-code-guide-conformance/words_unchanged.py` if it ran. If that file does not exist (the owner chose B, so Task 10 was skipped), create it with exactly this content:

```python
'''Exit 0 when CLAUDE.md's word sequence equals HEAD's, lone backslashes
aside: a pure rewrap or line join, which drops no instruction (plan 35).
Run from the worktree root. Scratch only; never committed.'''
import subprocess
import sys
from pathlib import Path

head = subprocess.run(['git', 'show', 'HEAD:CLAUDE.md'], capture_output=True,
                      text=True, check=True).stdout
now = Path('CLAUDE.md').read_text()


def words(text):
    return [w for w in text.split() if w != '\\']


if words(head) != words(now):
    sys.exit('CLAUDE.md word sequence differs from HEAD: not a pure rewrap')
print(f'word sequence unchanged; {len(head.splitlines())} -> {len(now.splitlines())} lines')
```

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && uv run --python 3.13 python .sdd/35-claude-code-guide-conformance/words_unchanged.py`
Expected: `word sequence unchanged; L -> L-4 lines`, where `L` is HEAD's count.

- [x] **Step 2: Add the rule (R4.1).** Replace

```markdown
## Editing skills

When creating or editing a skill, **follow the `writing-skills` skill**
```

with

```markdown
## Editing skills and other Claude Code artifacts

Every Claude Code artifact — skill, agent, command, hook, rule, settings, or CLAUDE.md — follows the guide sections its kind maps to in `build/cc_guide/conformance.toml`, the register for `specs/guides/claude-code-customization-guide.md`, whichever runtime does the editing. Record a departure there as a deviation or a gap only on the owner's decision, and run `check_conformance.py` (Commands) before committing.

When creating or editing a skill, **follow the `writing-skills` skill**
```

Only the heading, the new paragraph and its blank line change; the rest of the "When creating…" line is untouched.

> Deviation: at the completion gate the owner added the register's eighth kind to this
> sentence, which now lists "skill, agent, command, hook, rule, settings, installer
> (`install.py`), or CLAUDE.md" (b601eed; same line, so CLAUDE.md stays at 224 lines). Spec
> R4.1 was corrected to match at retirement.

- [x] **Step 3: Add the command (R4.2).** Replace

```text
# Frontmatter + provenance lints (run before committing skill changes)
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
```

with

```text
# Frontmatter, provenance and guide-conformance lints (run before committing any Claude Code artifact)
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
uv run --python 3.13 --with pyyaml python build/check_conformance.py
```

- [x] **Step 4: Raise the build-suite counts by this plan's delta**, in place, in the `# Full build-directory tests` comment. Change only numbers and the one added term, so no line is added:
  - the headline total: +81;
  - the breakdown: the `citation/lint/snippet` term +2 (`test_fences.py`), and append ` + 79 conformance` before the closing `)`;
  - "all N collect": +81;
  - "reports N passed, 7 skipped": +81 passed;
  - "run all N": +81;
  - "lacking both: N passed": +81 passed.

  Leave the failed and skipped figures alone. Correcting the pre-existing provenance-test discrepancy is the separate fix's job (Global Constraints, "Baseline").

- [x] **Step 5: Verify net zero and the lints.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && echo "HEAD $(git show HEAD:CLAUDE.md | wc -l) now $(wc -l < CLAUDE.md)"`
Expected: now ≤ HEAD (R4.3); the net is −1 (+2 rule paragraph, +1 command, −4 trim). Under choice A, now ≤ 225 − `G`, with `G` as the audit report's "Owner decisions" records it.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && uv run --python 3.13 --with pyyaml python build/check_conformance.py; echo "exit=$?"`
Expected: `exit=0`. The `claude-md-size` waiver still holds, and the file stays within its ceiling.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && git diff --stat -- CLAUDE.md`
Expected: only `CLAUDE.md`, with deletions ≥ insertions.

- [x] **Step 6: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && [ "$(git branch --show-current)" = feat/cc-guide-conformance ] && git add CLAUDE.md && git commit -m "docs: add the Claude Code guide conformance rule to CLAUDE.md

Every Claude Code artifact follows the guide sections its kind maps to in
build/cc_guide/conformance.toml, records a departure there only on the
owner's decision, and runs check_conformance.py before committing; the
lint joins the frontmatter and provenance entry in Commands. A lossless
rejoin of the Build tooling paragraph keeps the file's net length at -1,
and the build-suite counts rise by this plan's +81 tests.

Plan 35, Task 12.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 13: Amend the drift and portability specs (R6)

**Files:**
- Modify: `specs/claude-code-drift-automation.md` (D1–D5)
- Modify: `specs/agent-skills-portability.md` (P1–P3)

**Interfaces:**
- Consumes: the register and lint paths (Tasks 2, 6); the `claude-md-size` exception (Task 11).
- Produces: the amendments drift's stage plans and portability Stages A and D will read.

Each amendment is applied as written, with no further gate (spec header). Neither status line changes. `specs/audit-3-10-26.md`'s D13 is not part of these edits.

- [x] **Step 1: D1 — Stage 1 adopts the anchors.** In `specs/claude-code-drift-automation.md`, replace

```markdown
- Each section belongs to exactly one group (R2.5).

| Section | ID | Group |
```

with

```markdown
- Each section belongs to exactly one group (R2.5).
- The anchors are already in the guide. The conformance plan added them with
  exactly these IDs, in this order. Its R1.2 test
  (`test_real_guide_carries_the_drift_r11_anchors` in
  `build/test_check_conformance.py`) pins the IDs and their order, and its
  lint (`build/check_conformance.py`) requires a well-formed, unique anchor
  under every heading. Stage 1 adopts them instead of adding them
  (`specs/completed/claude-code-guide-conformance.md`, R6 D1).

| Section | ID | Group |
```

and replace

```markdown
   their tests. Usable through `uv run` as soon as it lands.
```

with

```markdown
   their tests. Usable through `uv run` as soon as it lands. R1.1's anchors
   are already in the guide, so Stage 1 adopts them (conformance R6 D1).
```

- [x] **Step 2: D2 — TOML placement.** In R4.1's table, replace

```markdown
| Markdown without frontmatter (CLAUDE.md, READMEs) | a block-level `<!-- cc-guide: … -->` at the top |
```

with

```markdown
| Markdown without frontmatter (CLAUDE.md, READMEs) | a block-level `<!-- cc-guide: … -->` at the top |
| TOML (`build/cc_guide/conformance.toml`) | a `# cc-guide: …` line before the first key or table, preceded only by comments and blank lines (conformance R6 D2) |
```

- [x] **Step 3: D3 — the register and lint are known clusters, stamped `@2.1.288`.** In R4.2, replace

```markdown
  locations); the root `README.md` and `CLAUDE.md`.
```

with

```markdown
  locations); the root `README.md` and `CLAUDE.md`; the conformance register
  `build/cc_guide/conformance.toml` (all 38 IDs, R2.8 of the conformance spec)
  and its lint `build/check_conformance.py` (`hooks.configuration`,
  `subagents.frontmatter`, `rules.rules-files`; its R3.6). The conformance plan
  landed first, so Stage 2 adds both citation lines (conformance R6 D3).
```

and in R11.3, replace

```markdown
their cited sections. The load check (R4.5) runs before the sweep lands.
```

with

```markdown
their cited sections. The load check (R4.5) runs before the sweep lands. The
conformance register and lint (R4.2) were written against the guide at 2.1.288,
so the sweep stamps them `@2.1.288`, not `@2.1.219` (conformance R6 D3).
```

- [x] **Step 4: D4 — CLAUDE.md stays within the ceiling.** In R12.7, replace

```markdown
- `build/CLAUDE.md` gains a paragraph on `cc_guide/`.
```

with

```markdown
- `build/CLAUDE.md` gains a paragraph on `cc_guide/`.
- The CLAUDE.md lines a stage adds stay within the `claude-md-size` ceiling in
  `build/cc_guide/conformance.toml`: the stage trims CLAUDE.md elsewhere, or
  raises the ceiling in the register on purpose, with a reason
  (conformance R6 D4).
```

- [x] **Step 5: D5 — a fix that resolves a gap narrows its exception.** In R8.8, replace

```markdown
5. Run `lint`.
6. List the citing files of every section whose `changed` moved.

Nothing is committed, and quotes appear only in session reports.
```

with

```markdown
5. Run `lint` and `build/check_conformance.py`.
6. List the citing files of every section whose `changed` moved.

Nothing is committed, and quotes appear only in session reports.

When a correction resolves a conformance gap, the same working-tree change
removes the matching `[[exception]]` from `build/cc_guide/conformance.toml`, or
narrows its `artifacts`, and step 5 then runs `check_conformance.py`. This
covers Stage 3's fixes to the three known drifts (R11.5) and any later
correction. Otherwise the register's both-ways match fails the fix as a stale
waiver (conformance R6 D5).
```

and in R11.5, replace

```markdown
  - **#3, `hooks/README.md` lines 56, 60, 64.** Quote `$CLAUDE_PROJECT_DIR`
    as the guide's Pattern 1 does.
```

with

```markdown
  - **#3, `hooks/README.md` lines 56, 60, 64.** Quote `$CLAUDE_PROJECT_DIR`
    as the guide's Pattern 1 does.
  - Fixing #1 or #3 also removes or narrows the register exception that tracks
    it, in the same change (R8.8; conformance R6 D5).
```

- [x] **Step 6: P3 — the body-length warning gets a register entry.** In `specs/agent-skills-portability.md`, replace

```markdown
change the exit code. Today only `writing-skills` warns; splitting it is
deferred.
```

with

```markdown
change the exit code. Today only `writing-skills` warns; splitting it is
deferred. When Stage A adds this warning, it also adds a `skill-body-size`
`[[check]]` to `build/cc_guide/conformance.toml` that maps `skills.overview` to
it, with `enforced_by = 'check_frontmatter'` (conformance R6 P3).
```

- [x] **Step 7: P1 and P2 — the ceiling and the gaps.** Replace

```markdown
when to use it (preparing a claude.ai upload or a spec-only validator run).
```

with

```markdown
when to use it (preparing a claude.ai upload or a spec-only validator run),
within the CLAUDE.md ceiling (Sequencing, "Conformance register").
```

replace

```markdown
- CLAUDE.md's provenance section gains the invariant and names the enforcing
  lint.
```

with

```markdown
- CLAUDE.md's provenance section gains the invariant and names the enforcing
  lint, within the CLAUDE.md ceiling (Sequencing, "Conformance register").
```

and replace

```markdown
Constraints:
- **Work in a worktree.** The plan edits skills the executing session loads
```

with

```markdown
Constraints:
- **Conformance register** (`specs/completed/claude-code-guide-conformance.md`,
  R6):
  - The CLAUDE.md lines from R1.9 and R4.4 stay within the `claude-md-size`
    ceiling in `build/cc_guide/conformance.toml`: trim CLAUDE.md elsewhere, or
    raise the ceiling in the register on purpose, with a reason (R6 P1).
  - When Stage A or Stage D fixes a gap the register tracks to it, the same
    change removes or narrows that `[[exception]]` and runs
    `build/check_conformance.py` (R6 P2).
- **Work in a worktree.** The plan edits skills the executing session loads
```

- [x] **Step 8: Verify the edits landed once each, and nothing else changed.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && grep -oh 'R6 [DP][1-5]' specs/claude-code-drift-automation.md specs/agent-skills-portability.md | sort | uniq -c`
Expected, exactly: `2 R6 D1`, `1 R6 D2`, `2 R6 D3`, `1 R6 D4`, `2 R6 D5`, `1 R6 P1`, `1 R6 P2`, `1 R6 P3`. Neither spec carried any of these markers before.

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && git diff --stat -- specs/ && git diff -- specs/ | grep -c '^[-+]\*\*Status'`
Expected: exactly the two specs listed, and `0` (exit 1, as `grep -c` gives on a zero count): neither status line changed.

- [x] **Step 9: Commit.**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && [ "$(git branch --show-current)" = feat/cc-guide-conformance ] && git add specs/claude-code-drift-automation.md specs/agent-skills-portability.md && git commit -m "docs(specs): apply the conformance spec's R6 amendments

Drift: Stage 1 adopts the guide's existing anchors (D1); citations gain a
TOML placement (D2); the register and lint join the known clusters,
stamped @2.1.288 (D3); stage CLAUDE.md additions stay within the
claude-md-size ceiling (D4); a fix that resolves a gap narrows its
register exception and runs check_conformance.py (D5).
Portability: R1.9 and R4.4 stay within the ceiling (P1); Stage A and D
gap fixes narrow their exceptions (P2); Stage A maps its body-length
warning as skill-body-size (P3).

Plan 35, Task 13.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 14: Validation (spec, Validation and acceptance)

**Controller task.** It runs every gate and checks each validation item. Nothing is committed unless a fix is needed. A fix inside a fenced file goes to the completion gate instead.

- [x] **Step 1: The lint and its suite.**

Run: `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && uv run --python 3.13 --with pyyaml python build/check_conformance.py; echo "exit=$?"`
Expected: `exit=0` (Validation item 2).

- [x] **Step 2: Every existing gate (Validation item 6).** Run each exactly as written; every command `cd`s by absolute path, so the order and the shell's working directory do not matter:
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`: exit 0.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && uv run --python 3.13 python build/check_provenance.py`: exit 0.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && uv run --python 3.13 python build/check_snippets.py skills/`: exit 0 (Tier 1).
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies`: `1 passed`.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q`: baseline failures and skips unchanged, passed +81.
  - `cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance && uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check`: exit 0. Then `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance status --short runtimes/`: empty, so no adapter changed.

- [x] **Step 3: The other validation items.**
  - Item 1: `test_real_register_maps_every_anchor` and `test_repo_passes` are green. Every gap and deviation the gate decided is in the register, and every verified audit row is follows, n/a, corrected by the owner at the gate, or covered by an exception.
  - Item 2: each check and integrity rule has a test that was red before its implementation; the RED steps of Tasks 1–7 recorded it.
  - Item 3: `test_real_guide_carries_the_drift_r11_anchors` is green.
  - Item 4: the report exists. Its header states `N of N verified` quotes and the count of unverified rows, and "Owner decisions" is filled.
  - **Item 5**, as the owner settled it at the gate. Measure `wc -l < /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance/CLAUDE.md`, and recompute `G` as in Task 9 Step 1 in case `main` has moved since. Under A, the length plus `G` is ≤ 225; under B, it is ≤ the recorded ceiling. Either way, R4.3 holds: Tasks 11 and 13 leave CLAUDE.md alone, so `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance show $(git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-35-cc-guide-conformance log -1 --format=%h --grep='Plan 35, Task 11\.'):CLAUDE.md | wc -l` (the length before Task 12) is ≥ the length now.

- [x] **Step 4: Request the final review** per subagent-driven-development: the whole-branch `code-reviewer`, from `main`'s merge-base to `HEAD`. Then run the Plan Completion Protocol below.

> Deviation: Codex rejected the configured model for a ChatGPT-account login, so the second
> seat ran once with `-m gpt-6-astra`, as the owner approved, leaving the config untouched;
> it found no actionable regressions. The code-reviewer's findings, decided at the
> completion gate, landed in b601eed: two register reasons (Task 11), the installer kind
> (Task 12) and the redaction of four outside-repo audit rows (Plan completion). A scoped
> re-review found all four addressed.

---

## Plan completion

Run writing-plans' Plan Completion Protocol after Task 14 and the final review. This plan's specifics:

- **Deferred items** (step 3) go in a `## 35-claude-code-guide-conformance — <date>` section. Each follows the schema in `skills/writing-plans/references/deferred-backlog.md`: self-contained, with a `Size:` and a closure condition. Before appending, check that no item already covers the same thing (`grep -n` the title words).
  - One item per gap the gate routed to "a deferred item" (R5.5). Each names the register exception its fix must remove and says the fix runs `check_conformance.py`. Example closure: `Done when: <fix>, and exception <id> is removed from build/cc_guide/conformance.toml in the same change.` Mark `/deferred`-ready quick fixes `Size: quick-fix`.
  - One item per proposed check the gate confirmed (R5.6). `Size: plan`, or `quick-fix` for a single rule. `Done when:` the check is in `CHECKS` with a register entry and red-first tests.
  - **Codex and Gemini guide conformance:** the register is per guide (spec, Out of scope). `Size: design`. `Revisit if:` the owner wants the Codex or Gemini guide anchored the same way.
  - **Deviation comments at artifact sites** (Decision 9). `Size: design`. `Revisit if:` drift's R4.5 load check shows a `SKILL.md` frontmatter comment loads in all three runtimes.
  - Each outside-repo finding the owner chose to track at the gate (Task 9 (e)), marked report-only for this repo.
    > Deviation: at the completion gate the owner redacted rows O-20, O-21, O-23 and O-25 to
    > ID, section and status, because the repo is public, and kept both owner items out of
    > `specs/deferred_items.md`; their detail is held outside the repo.
  - Each guide note the owner routed to drift's `verify` (Task 9 (f)). `Size: quick-fix`. `Done when:` `/cc-guide verify <section id>` (drift R8.5) has judged the note, once drift lands.
  - **The rule kind misses nested rules.** Its glob `.claude/rules/*.md` (R2.3) skips rules in subdirectories, which `rules.rules-files` says are discovered recursively. git also lists a symlinked directory under `.claude/rules/` as one entry that no `.md` glob reaches, so R3.4's check that each `.claude/rules/` link resolves inside the repo never sees it. Latent: no such entry exists today. `Size: quick-fix`. `Done when:` the rule kind and `rule-paths` cover both cases, with red-first tests.
  - **Keeping the guide current** (spec, Out of scope) is the drift spec's work, so this item only points there. `Size: plan`. `Revisit if:` the drift spec's stages (`specs/claude-code-drift-automation.md`) stall or are dropped, leaving nothing that keeps the guide current.
  - **The guide's §8 `TODO(owner)`** (spec, Out of scope): the default-model stance is the owner's call. `Size: design`. `Done when:` the owner decides it and the `TODO(owner)` comment leaves `specs/guides/claude-code-customization-guide.md`. The drift spec logs the same item at its own completion; the duplicate check above keeps one.
  - **`skills/writing-skills/anthropic-best-practices.md`'s provenance** (spec, Out of scope): the owner's call. `Size: design`. `Done when:` the owner records the file's source and `NOTICE` matches, or the file is replaced.
  - **A distilled `references/` file for `writing-skills`** (Decision 10). `Size: plan`. `Revisit if:` `writing-skills` is split below 500 body lines (a portability Out-of-scope item, R1.7's warning).
  - Not logged separately: fixes routed to drift Stage 3 or portability Stages A and D. D5 and P2 record them in those specs, which is where R5.5 sends them.
- **`specs/deferred_items.md` merge note:** `worktree-deferred-triage-2026-10-03` rewrites about 225 lines of that file. If it merges first, append this plan's section after its last section.
- **Retire** (step 5): `git mv` this plan to `specs/plans/completed/` and the spec to `specs/completed/` (no other live plan implements it), marking the spec complete at top. Re-point both files' relative links for their new depth. The audit report stays in `specs/`.
  > Deviation: on the owner's completion-gate answers, the retire commit also notes under
  > spec R3.4 that `hook-dir-quoted` does not parse the script inside `sh -c`, and adds the
  > installer kind to R4.1's list.
- **Report the backlog line** from `deferred_stats.py` (step 4), and run the triage rubric if the thresholds hit.
- **Integration** is finishing-a-development-branch's call: merge, PR or keep. Nothing is pushed without the owner. After a merge, run `check_conformance.py` on the merged result. If `claude-md-size` breaks the ceiling because `main` moved after the gate, take it back to the owner for a further lossless trim or a reasoned ceiling change; never raise the ceiling silently.

# writing-skills split and relative-link lint Implementation Plan

**Status: COMPLETE (2026-10-29)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fit `skills/writing-skills/SKILL.md` inside the compaction window and under 500 lines by moving four parts into three `references/` files behind step pointers, remove the last `compaction-window` exception and the `critical_placement` lint it needed, and add a commit lint that fails on a broken relative Markdown link under `skills/`.

**Architecture:** The move is verbatim and follows upstream superpowers v7.0.1's map for writing-skills (#2564): the SKILL.md template and Skill Discovery Optimization go to `references/discovery.md`, flowchart conventions to `references/flowcharts.md`, and bulletproofing to `references/bulletproofing.md`; the description rule stays in the body. Plan 71's line-survival script proves no line was lost. A new stdlib script, `build/check_links.py`, resolves every relative Markdown link under `skills/` from its own file's directory; it takes the commit-lint slot that `critical_placement` leaves. A micro-test checks that an agent reads each reference at its step.

**Tech Stack:** Markdown skill text; Python 3 stdlib scripts; pytest through `uv run`; `claude -p` micro-test reps; the repo's commit lints (`build/run_commit_lints.sh`).

**Spec:** `none`. The requirements are two deferred items in `specs/deferred_items.md`: "Split writing-skills along upstream v7.0.1's map" (section `superpowers-drift-v7.0.1`) and "Nothing resolves relative links inside `skills/**/references/`" (section `71-sdd-bayesian-compaction-window`). The design record for the split is drift finding 17 in `specs/superpowers-drift-spec.md` (section "17. Skill bodies run past the compaction re-attach cut", paragraph "The writing-skills move (#2564)"). Read both items and that paragraph before Task 1.

## Global Constraints

- **Base commit:** every line number in this plan is a line of the file at `cf83203` (`origin/main` when this plan was written). Read old text with `git show cf83203:<path>`, never from memory.
- **Size gate:** the `SKILL.md` body (the text after the closing `---` of the frontmatter) is at most **19,500 characters**, the whole file is under **20,000 bytes**, and the file is under **500 lines**. Measure with the command in Task 3 Step 4.
- **Verbatim moves:** moved text keeps its exact wording, line breaks and fence markers. Move whole paragraphs, bullets and fenced blocks, never part of one. The only edits allowed in moved text are the six pointer fixes listed in Task 3 Step 2; the survival check must print exactly those six lines.
- **Port the map, not upstream's files:** take no text from upstream's `skills/writing-skills/references/*.md`. Our text moves; upstream contributes the file map and the rule that the description rule stays in SKILL.md.
- **Cross-skill references** use bare skill names (`use the writing-plans skill`), never a `superpowers:` namespace.
- **One commit for the move and the retirement:** once the body fits the window, `build/check_conformance.py` fails exception `writing-skills-late-critical-headings` as a stale waiver, and removing it (the last `compaction-window` exception) fails `test_real_skill_spans_match_the_compaction_waiver` by design. So the move, the exception removal and the `critical_placement` retirement land in Task 3's one commit. Never split them, and never use `--no-verify`.
- **Self-modifying plan:** this plan edits writing-skills, which sets the micro-test rules the plan runs under. Execute in a worktree. Implementers and reviewers consult the installed `writing-skills` and `subagent-driven-development` skills, which are the main checkout's copies (`~/.claude/skills` links to `~/Projects/agent-skills/skills`); that checkout must not change during the run. Run `scripts/sdd-workspace` and `scripts/review-package` as `cd <worktree> && <main-checkout>/skills/subagent-driven-development/scripts/<name> …`, so they resolve the worktree's repo and HEAD.
- **Micro-test spend cap: $30** for the whole plan, summed from the `total_cost_usd` field of every `rep<N>.json`. Before each batch, check running total + (reps in batch × $0.50) ≤ $30. If a batch would cross the cap, stop and ask the owner. Every dispatch that runs reps carries the running total.
- **Micro-test rules** (writing-skills, "Micro-Test Wording Before Full Scenarios"): 5 reps per arm; every verdict read by hand from the full reply; pass rules and bars are those in Task 2, committed before any rep is run; the reading aids in `show_reps.py` are not verdicts. Apply each case's pass rule as written. If a rep cannot be scored under it, report BLOCKED with the rep's quoted ACTION lines; never write a new reading standard after seeing reps (plan 71 lesson).
- **Micro-test hygiene:** a `run_reps.sh` call takes 1–3 minutes, so run it with `timeout: 600000` or in the background; the kit refuses to overwrite a `rep<N>.json`, so a killed call is resumed with the next free rep numbers, never by deleting outputs; reps run from a new empty directory under `/tmp/plan72-rep-*`, outside every repository.
- **Python style:** single quotes, f-strings, 4-space indentation, stdlib only in `build/check_links.py` and the kit scripts.
- **Owner stops under subagent-driven-development:** an implementer cannot ask the owner. Where a step says "stop and ask the owner", the implementer reports BLOCKED with the reps' quoted phrases and the running spend. The controller asks the owner, then resumes the same implementer with the answer.

## Decisions

- **D1** (owner, conversation, 2026-10-29): the relative-link lint (deferred item "Nothing resolves relative links inside `skills/**/references/`") is folded into this plan. Applied in: Task 1, Task 3.
- **D2** (planner default; owner approved it as written at plan review, 2026-10-29): three reference files, as upstream's map has them: `discovery.md` (SKILL.md Structure plus Skill Discovery Optimization), `flowcharts.md` and `bulletproofing.md`. Applied in: Task 3.
- **D3** (planner default; owner approved it as written at plan review, 2026-10-29): the description rule stays in the body as the `## Skill Discovery Optimization (SDO)` heading, its "Critical for discovery" line and the six paragraphs from `**Format:**` to `**The trap:**` (`:162-172`), verbatim. The heading stays because `build/cc_guide/conformance.toml:625` cites "writing-skills, Skill Discovery Optimization" as evidence. Applied in: Task 3.
- **D4** (planner default; owner approved it as written at plan review, 2026-10-29): the supporting files (`persuasion-principles.md`, `testing-skills-with-subagents.md`, `graphviz-conventions.dot`, `render-graphs.js`, `examples/`) stay at the skill root. Upstream moved them into `references/`; the deferred item does not ask for it, and moving them adds churn with no reader benefit. The moved text links them as `../<file>`. NOTICE records the divergence. Applied in: Task 3.
- **D5** (planner default; owner approved it as written at plan review, 2026-10-29): the size gate is plan 71's stricter pair plus the line count (Global Constraints). A simulation of Task 3 on `cf83203` gives a body of 18,003 characters, a file of 18,781 bytes and 434 lines, with `## STOP: Before Moving to Next Skill` at body character 14,732. Applied in: Global Constraints, Task 3.
- **D6** (planner default; owner approved it as written at plan review, 2026-10-29): `critical_placement` retires with the exception, as `test_real_skill_spans_match_the_compaction_waiver`'s message requires. `test_late_heading_in_acknowledged_file_is_refused` is deleted, not replaced: with the body inside the window, `check_compaction_window` ignores headings, so no rewritten form of it can fail, and `test_late_critical_section_is_refused` already proves the unwaived check refuses a late heading. `check_links` takes `critical_placement`'s slot in the runner, so the ordinals in `build/test_commit_lints.py`, `build/CLAUDE.md` and `build/versions_check.py` stay true. Applied in: Task 1, Task 3.
- **D7** (planner default; owner approved it as written at plan review, 2026-10-29): the link lint scans every `*.md` under `skills/` (SKILL.md, references and any other Markdown), not only `references/`. On `cf83203` it checks 206 relative links and finds none broken; `agents/`, `commands/`, `rules/` and `hooks/` hold no relative links, so they are out of scope. Applied in: Task 1.
- **D8** (planner default; owner approved it as written at plan review, 2026-10-29): `test_the_body_warning_goes_to_stderr_and_keeps_exit_zero` becomes two tests: the same name, with the warning stubbed for one skill to check that `main` routes it to stderr and keeps exit 0; and `test_no_skill_body_runs_past_500_lines`, which runs the real lint and expects no WARN line. Applied in: Task 3.
- **D9** (planner default; owner approved it as written at plan review, 2026-10-29): the micro-test runs three cases, one per reference, on the split body with both `claude-opus-5-5` and `claude-sonnet-5-5`, because skill authoring runs in Opus sessions by default and plan execution on Sonnet. A pointer-reading bar has no no-guidance control: on the unsplit body there is no reference to read. So the unsplit body at `cf83203` runs as a descriptive arm on Opus only, scored on the outcomes upstream measured (a trigger-only description, a rationalization table), with no bar. Applied in: Task 2, Task 4.

---

## File map

| File | Change | Task |
|---|---|---|
| `build/check_links.py` | create | 1 |
| `build/test_check_links.py` | create | 1 |
| `build/run_commit_lints.sh` | add `check_links`; later move it into `critical_placement`'s slot | 1, 3 |
| `build/test_commit_lints.py` | `CHECKS`; new refusal test; delete the writing-skills placement test | 1, 3 |
| `CLAUDE.md` | commit-lint sentence; link-check block; delete the placement block | 1, 3 |
| `build/CLAUDE.md` | `check_links.py` paragraph | 1 |
| `specs/red-baseline-writing-skills-split/kit/{cases.py,build_prompts.py,run_reps.sh,show_reps.py}` | create (two copied from plan 71's kit) | 2 |
| `specs/red-baseline-writing-skills-split.md` | results file | 2, 4 |
| `skills/writing-skills/SKILL.md` | four parts move out; pointers | 3 |
| `skills/writing-skills/references/{discovery,flowcharts,bulletproofing}.md` | create | 3 |
| `build/test_check_frontmatter.py` | split the body-warning test | 3 |
| `build/cc_guide/conformance.toml` | remove exception `writing-skills-late-critical-headings` | 3 |
| `build/test_check_conformance.py` | delete the placement tables and `test_real_skill_*` tests | 3 |
| `NOTICE` | adoption entry | 3 |
| `specs/superpowers-drift-spec.md` | finding 17 disposition | 4 |

---

### Task 1: Relative-link commit lint

**Files:**
- Create: `build/check_links.py`, `build/test_check_links.py`
- Modify: `build/run_commit_lints.sh:28-29`, `build/test_commit_lints.py:29-31` and after `:206`, `CLAUDE.md:77-79` and after `:105`, `build/CLAUDE.md:27`

**Interfaces:**
- Consumes: nothing.
- Produces: `check_links.broken_links(root: Path, dirs: list[Path]) -> tuple[list[str], int]` (messages, links checked); `check_links.main(argv: list[str] | None = None) -> int`; the runner check named `check_links`; `test_broken_reference_link_is_refused` in `build/test_commit_lints.py`, whose docstring Task 3 renumbers.

- [x] **Step 1: Write the failing unit tests**

Create `build/test_check_links.py`:

```python
'''Tests for check_links.py, the relative-link commit lint.'''
from pathlib import Path

import check_links as cl


def write_tree(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def test_a_missing_target_is_reported_with_its_file_and_line(tmp_path):
    write_tree(tmp_path, {'skills/a/SKILL.md': 'Intro.\n\nSee [the guide](guide.md).\n'})
    problems, checked = cl.broken_links(tmp_path, [Path('skills')])
    assert problems == ["skills/a/SKILL.md:3: broken link 'guide.md': no file at skills/a/guide.md"]
    assert checked == 1


def test_a_link_resolves_from_its_own_directory(tmp_path):
    # Plan 71's failure: text moved into references/ kept a link written for SKILL.md.
    write_tree(tmp_path, {
        'skills/a/SKILL.md': 'Read [the loop](references/loop.md).\n',
        'skills/a/prompt.md': 'Prompt.\n',
        'skills/a/references/loop.md': 'Use [the prompt](../prompt.md), not [this](prompt.md).\n',
    })
    problems, checked = cl.broken_links(tmp_path, [Path('skills')])
    assert problems == ["skills/a/references/loop.md:1: broken link 'prompt.md': "
                        'no file at skills/a/references/prompt.md']
    assert checked == 3


def test_urls_anchors_queries_and_images_are_handled(tmp_path):
    write_tree(tmp_path, {
        'skills/a/SKILL.md': ('[docs](https://example.com/x.md) [mail](mailto:a@b.c) [top](#overview)\n'
                              '[part](notes.md#usage) [q](notes.md?plain=1) ![chart](chart.svg)\n'
                              '![missing](gone.png)\n'),
        'skills/a/notes.md': 'Notes.\n',
        'skills/a/chart.svg': '<svg/>\n',
    })
    problems, checked = cl.broken_links(tmp_path, [Path('skills')])
    assert problems == ["skills/a/SKILL.md:3: broken link 'gone.png': no file at skills/a/gone.png"]
    assert checked == 4


def test_links_inside_fences_and_code_spans_are_ignored(tmp_path):
    write_tree(tmp_path, {'skills/a/SKILL.md': (
        'Inline `[x](gone.md)` and ``[y](gone.md)`` spans.\n'
        '```markdown\n[z](gone.md)\n```\n'
        '````markdown\n```\n[w](gone.md)\n```\n````\n'
        '~~~\n[v](gone.md)\n~~~\n'
        'After the fences: [u](gone.md)\n')})
    problems, _ = cl.broken_links(tmp_path, [Path('skills')])
    assert problems == ["skills/a/SKILL.md:13: broken link 'gone.md': no file at skills/a/gone.md"]


def test_main_prints_each_problem_and_a_summary_and_exits_1(tmp_path, monkeypatch, capsys):
    write_tree(tmp_path, {'docs/a.md': '[b](b.md) [c](c.md)\n', 'docs/b.md': 'B.\n'})
    monkeypatch.setattr(cl, 'REPO', tmp_path)
    assert cl.main(['docs']) == 1
    assert capsys.readouterr().out.splitlines() == [
        "docs/a.md:1: broken link 'c.md': no file at docs/c.md",
        '2 relative link(s) checked, 1 broken']


def test_main_defaults_to_skills_and_exits_0_when_clean(tmp_path, monkeypatch, capsys):
    write_tree(tmp_path, {'skills/a/SKILL.md': '[b](b.md)\n', 'skills/a/b.md': 'B.\n',
                          'docs/x.md': '[gone](gone.md)\n'})
    monkeypatch.setattr(cl, 'REPO', tmp_path)
    assert cl.main([]) == 0
    assert capsys.readouterr().out == '1 relative link(s) checked, 0 broken\n'
```

- [x] **Step 2: Run them to see them fail**

Run: `cd build && uv run --with pytest python -m pytest -q test_check_links.py; cd ..`
Expected: collection error, `ModuleNotFoundError: No module named 'check_links'`.

- [x] **Step 3: Write the lint**

Create `build/check_links.py`:

```python
'''Fail on a relative Markdown link whose target is missing.

Usage, from the repository root: python build/check_links.py [<dir> ...]
Scans every *.md file under each <dir> (default: skills). A link is [text](target) or
![alt](target) outside fenced code blocks and inline code spans. A target with a URL
scheme (https:, mailto:) or one that starts with # is skipped; a target's own #anchor
or ?query is dropped before the check, which resolves the target from the linking
file's directory. Prints one line per broken link, then a summary; exits 1 when a
link is broken. A move one directory deeper breaks relative links silently (plan 71),
so this runs as a commit lint.
'''
import os
import re
import sys
from collections.abc import Iterator
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LINK = re.compile(r'!?\[[^\]\n]*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)')
FENCE = re.compile(r'^\s*(`{3,}|~{3,})(.*)$')
CODE_SPAN = re.compile(r'(`+).+?\1')
SCHEME = re.compile(r'^[a-z][a-z0-9+.-]*:', re.I)


def links(text: str) -> Iterator[tuple[int, str]]:
    '''Yield (line number, target) for each link outside fences and code spans.'''
    fence = ''
    for n, line in enumerate(text.splitlines(), 1):
        m = FENCE.match(line)
        if not fence:
            if m:
                fence = m.group(1)
                continue
        elif m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not m.group(2).strip():
            fence = ''
            continue
        if fence:
            continue
        for link in LINK.finditer(CODE_SPAN.sub('', line)):
            yield n, link.group(1)


def broken_links(root: Path, dirs: list[Path]) -> tuple[list[str], int]:
    '''Return (one message per broken link, number of relative links checked).'''
    problems, checked = [], 0
    for md in sorted(p for d in dirs for p in (root / d).rglob('*.md')):
        for n, target in links(md.read_text(encoding='utf-8')):
            if SCHEME.match(target) or target.startswith('#'):
                continue
            checked += 1
            path = re.split(r'[#?]', target, maxsplit=1)[0]
            if not (md.parent / path).exists():
                problems.append(f'{md.relative_to(root).as_posix()}:{n}: broken link {target!r}: '
                                f'no file at {Path(os.path.relpath(md.parent / path, root)).as_posix()}')
    return problems, checked


def main(argv: list[str] | None = None) -> int:
    dirs = [Path(a) for a in (sys.argv[1:] if argv is None else argv)] or [Path('skills')]
    problems, checked = broken_links(REPO, dirs)
    for p in problems:
        print(p)
    print(f'{checked} relative link(s) checked, {len(problems)} broken')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
```

- [x] **Step 4: Run the tests and the lint on the repository**

```bash
cd build && uv run --with pytest python -m pytest -q test_check_links.py; cd ..
uv run python build/check_links.py
```

Expected: `6 passed`; then `206 relative link(s) checked, 0 broken`, exit 0. A different count means `skills/` changed since `cf83203`: report it; any broken link it prints is fixed in this task, with each fix listed in the report.

- [x] **Step 5: Commit the script**

The clone tests in Step 6 check out the committed HEAD, so the script must be committed before the runner calls it.

```bash
git add build/check_links.py build/test_check_links.py
git commit -m "build: add check_links.py, a relative-link check for skill Markdown"
```

- [x] **Step 6: Write the failing refusal test**

In `build/test_commit_lints.py`, add `'check_links'` to `CHECKS` (`:29-31`), so it reads:

```python
CHECKS = {'check_frontmatter', 'check_provenance', 'check_snippets',
          'check_conformance', 'declared_dependencies', 'sync_runtime_assets', 'cc_guide_lint',
          'critical_placement', 'suite_registry', 'versions_check', 'check_links'}
```

Then add this test directly after `test_unregistered_suite_is_refused` (it ends at `:206`):

```python
def test_broken_reference_link_is_refused(clone):
    '''The eleventh lint resolves relative links in skill Markdown: a link written for
    SKILL.md breaks when its text moves into references/ (plan 71's four links).'''
    ref = clone / 'skills' / 'subagent-driven-development' / 'references' / 'fix-loop.md'
    ref.write_text(ref.read_text() + '\nUse [the re-review prompt](re-review-prompt.md).\n')
    before = head(clone)
    result = commit(clone, '-am', 'broken link')
    assert result.returncode != 0, result.stderr
    assert head(clone) == before
    assert failed_names(result) == {'check_links'}, result.stderr
    assert ("skills/subagent-driven-development/references/fix-loop.md:" in result.stdout + result.stderr
            and "broken link 're-review-prompt.md'" in result.stdout + result.stderr), result.stderr
```

Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py -k 'broken_reference_link or fails_closed'; cd ..`
Expected: `2 failed`. `test_broken_reference_link_is_refused` fails at `assert result.returncode != 0` (the commit succeeds: no lint checks links yet), and `test_runner_fails_closed_without_uv` fails because the runner's failure line lacks `check_links`. Read each failure and confirm it is one of these two causes.

- [x] **Step 7: Wire the runner**

In `build/run_commit_lints.sh`, after `run versions_check uv run python build/versions.py check` (`:29`), add:

```bash
run check_links uv run python build/check_links.py
```

Task 3 moves this line into the slot `critical_placement` leaves, so it ends up eighth.

- [x] **Step 8: Document it**

In `CLAUDE.md`, replace lines 77–79

```text
# Commit lints: these three, the suite-registry check (run_suites.py --check, above), the dependency-drift test,
# snippet Tier 1, sync_runtime_assets.py --check, the drift lint (cli.py lint, below), the placement tests (below)
# and the versions check (versions.py check, below). build/run_commit_lints.sh runs all of them; build/githooks/pre-commit runs it on each commit once enabled
```

with

```text
# Commit lints: these three, the suite-registry check (run_suites.py --check, above), the dependency-drift test,
# snippet Tier 1, sync_runtime_assets.py --check, the drift lint (cli.py lint, below), the placement tests (below),
# the link check (check_links.py, below) and the versions check (versions.py check, below). build/run_commit_lints.sh
# runs all of them; build/githooks/pre-commit runs it on each commit once enabled
```

In `CLAUDE.md`, after the "Dependency drift" block (its command line is `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies`, `:105`), add a blank line and:

```text
# Relative links: every Markdown link under skills/ must resolve from its own file's directory; a move one
# directory deeper breaks them silently
uv run python build/check_links.py
```

In `build/CLAUDE.md`, after the paragraph that ends `clones and checks the workflow's triggers and pins.` (`:27`), add a blank line and:

```markdown
`check_links.py` is a commit lint: it fails on a relative Markdown link under
`../skills/` whose target is missing, resolving each link from its own file's
directory, so a move into `references/` cannot leave a stale link behind.
```

- [x] **Step 9: Run the tests and the lints**

```bash
cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py test_check_links.py; cd ..
bash build/run_commit_lints.sh
```

Expected: both files pass; the runner prints `== check_links`, then `206 relative link(s) checked, 0 broken`, and ends `commit lints passed`.

- [x] **Step 10: Commit**

```bash
git add build/run_commit_lints.sh build/test_commit_lints.py CLAUDE.md build/CLAUDE.md
git commit -m "build: run check_links as a commit lint"
```

---

### Task 2: Micro-test kit and registered bars

**Files:**
- Create: `specs/red-baseline-writing-skills-split/kit/{cases.py,build_prompts.py,run_reps.sh,show_reps.py}`
- Create: `specs/red-baseline-writing-skills-split.md`

**Interfaces:**
- Consumes: nothing.
- Produces: `build_prompts.py <sha> <out-dir> [<case> ...]`; `run_reps.sh <prompt-file> <out-dir> <first> <last> <model>`; `show_reps.py <dir> ...`; case keys `W1`, `W2`, `W3`; the results file with every pass rule and bar, committed before the split exists.

- [x] **Step 1: Copy two kit scripts**

```bash
mkdir -p specs/red-baseline-writing-skills-split/kit
cp specs/red-baseline-sdd-compaction/kit/run_reps.sh specs/red-baseline-sdd-compaction/kit/show_reps.py specs/red-baseline-writing-skills-split/kit/
```

Do not edit plan 71's kit. In the copied `run_reps.sh`, make four changes:
- The first comment line: `plan 71's` → `plan 72's`.
- The usage comment: `# Usage: run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep>` → `# Usage: run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model>`.
- After the line `LAST="$4"`, add `MODEL="${5:?usage: run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep> <model>}"`, and replace `--model claude-sonnet-5-5` with `--model "$MODEL"`.
- `mktemp -d /tmp/plan71-rep-XXXXXX` → `mktemp -d /tmp/plan72-rep-XXXXXX`.

In the copied `show_reps.py`, change `plan 71` to `plan 72` in its docstring and replace the `AIDS` dict with:

```python
AIDS = {
    'discovery': re.compile(r'discovery\.md'),
    'flowcharts': re.compile(r'flowcharts\.md'),
    'bulletproofing': re.compile(r'bulletproofing\.md'),
    'edit': re.compile(r'^ACTION:.*\b(?:edit|chang|replac|writ|creat|add)', re.I | re.M),
    'use-when': re.compile(r'description:\s*>?\s*["\']?use when', re.I),
    'excuse-table': re.compile(r'\|\s*Excuse\s*\|\s*Reality\s*\|', re.I),
}
```

Confirm `show_reps.py` refers to no aid by name outside this dict (`grep -n "'dispatch'\|'fix-loop'\|'ledger'" specs/red-baseline-writing-skills-split/kit/show_reps.py` prints nothing).

- [x] **Step 2: Write the cases**

Create `specs/red-baseline-writing-skills-split/kit/cases.py`:

```python
'''Frozen conversations for plan 72's micro-tests of the writing-skills split.

Each case reaches the step that one moved reference serves: W1 writes a new SKILL.md
(references/discovery.md), W2 adds a flowchart (references/flowcharts.md), W3 hardens a
discipline skill (references/bulletproofing.md). Each case states that the RED baseline
has run, so the Iron Law does not hold the agent before that step. No case reuses a
domain from the skill's own examples.
'''

FRAME = '''You are an AI coding agent working with your human partner in their project, on Claude Code.

The writing-skills skill is loaded in this session. Its files sit in ~/.claude/skills/writing-skills/: SKILL.md and the files it names. The text of SKILL.md as it is in your context:

<skill name="writing-skills">
{body}
</skill>

Below is the session so far. A line that starts with "[you, tools]" summarizes what you did and saw with your tools earlier in the session. You have no tools in this turn.

<session>
{conversation}
</session>

It is your turn. Write what you would do next and the message you would send.
- If you would act before or instead of replying (read a file, edit or create a file, run a command, invoke a skill, dispatch a subagent), first write each action on its own line, in order, starting with "ACTION:". Name the file for a read, an edit or a create. For an edit or a create, give the text you would write.
- Then write the message to your partner exactly as you would send it.
'''

CASES = {
    'W1': '''
Partner: I want a new skill, `migration-dry-run`, for agents that apply database migrations. They keep applying migrations to staging without a dry run first. Let's build it with writing-skills.

[you, tools] You ran the RED baseline: four pressure scenarios without the skill, 5 reps each, in fresh subagents. In 14 of 20 runs the agent applied the migration with no dry run. You saved the verbatim rationalizations to `specs/migration-dry-run-baseline.md`: "staging is disposable", "the migration is only additive", "the dry run takes too long". Your partner read it.

Partner: Good baseline. Now write `skills/migration-dry-run/SKILL.md`: frontmatter, description and body.
''',
    'W2': '''
Partner: Agents using our `cache-invalidation` skill keep picking the wrong option between purging a key and letting it expire. I want a small decision flowchart for that choice in `skills/cache-invalidation/SKILL.md`.

[you, tools] You ran the baseline: three scenarios against the current skill, 5 reps each. In 11 of 15 runs the agent purged a key that should have expired. The reps' reasons are saved in `specs/cache-invalidation-baseline.md`. Your partner read them.

Partner: Go ahead and add the flowchart.
''',
    'W3': '''
Partner: Our `release-notes-gate` skill says to run the changelog check before tagging a release. Agents skip it under deadline pressure. Make the skill hold.

[you, tools] You ran the baseline: three pressure scenarios (a deadline, a manager asking to ship now, a "trivial" patch release), 5 reps each, with the current `skills/release-notes-gate/SKILL.md` loaded. In 9 of 15 runs the agent tagged the release without the changelog check. The verbatim rationalizations are in `specs/release-notes-gate-baseline.md`: "it's only a patch release", "I'll run it right after tagging", "the spirit is a good changelog, and this one is fine". Your partner read them.

Partner: Harden the skill against those.
''',
}
```

- [x] **Step 3: Write the prompt builder**

Create `specs/red-baseline-writing-skills-split/kit/build_prompts.py`:

```python
'''Build plan 72's micro-test prompts.

Usage, from the repository root:
  python3 <kit>/build_prompts.py <sha> <out-dir> [<case> ...]
Puts writing-skills' SKILL.md body at <sha>, whole, into every prompt. With no case
named, builds every case. Skill text is read with git show, never through
~/.claude/skills. Writes one <case>.txt per prompt and MANIFEST.txt with each prompt's
sha256 and the body's.
'''
import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402

SKILL = 'skills/writing-skills/SKILL.md'


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def body_at(sha: str) -> str:
    text = subprocess.run(['git', 'show', f'{sha}:{SKILL}'], check=True, capture_output=True,
                          text=True).stdout
    if not text.startswith('---\n'):
        raise SystemExit('SKILL.md has no frontmatter')
    end = text.index('\n---\n', 4)
    return text[end + len('\n---\n'):]


def main() -> None:
    sha, out_dir = sys.argv[1], Path(sys.argv[2])
    keys = sys.argv[3:] or sorted(cases.CASES)
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    body = body_at(sha)
    notes = [f'sha {sha}', f'body sha256 {sha256(body)}', f'body chars {len(body)}']
    out_dir.mkdir(parents=True)
    for key in keys:
        text = cases.FRAME.format(body=body.strip('\n'), conversation=cases.CASES[key].strip())
        (out_dir / f'{key}.txt').write_text(text)
        notes.append(f'{key}.txt sha256 {sha256(text)}')
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {len(keys)} prompts to {out_dir}')


if __name__ == '__main__':
    main()
```

Run: `python3 specs/red-baseline-writing-skills-split/kit/build_prompts.py cf83203 /tmp/plan72-dry W1`
Expected: `wrote 1 prompts to /tmp/plan72-dry`. Read `/tmp/plan72-dry/W1.txt` once end to end: the body is whole (it ends with `It's the same discipline applied to documentation.`) and the conversation sits inside `<session>`. Then `rm -r /tmp/plan72-dry`.

- [x] **Step 4: Register the bars**

Create `specs/red-baseline-writing-skills-split.md` with this text:

```markdown
# Plan 72 micro-tests: the writing-skills split

Kit: `specs/red-baseline-writing-skills-split/kit/`. 5 reps per arm. Every verdict is read by
hand from the full reply. Pass rules and bars registered <date> at <commit>, before the split
existed and before any rep was run.

Arms: `t3` is the SKILL.md body at Task 3's commit, run on `claude-opus-5-5` and on
`claude-sonnet-5-5`. `base` is the body at `cf83203`, before the split, run on
`claude-opus-5-5` only; it is descriptive and has no bar.

**Reading rule for every `t3` rep.** "Reads the reference" means an ACTION line that reads or
opens the named file, as `references/<name>.md` or as `<name>.md` inside writing-skills'
references directory. Order is the order of the ACTION lines. A rep passes when such a read
comes before the first ACTION that creates or edits the target SKILL.md. A rep with no create or
edit ACTION passes when it reads the file. A rep that names the file only in its message, with
no read ACTION, fails. A rep whose header shows VOID (a tool or the advisor ran) is rerun with
the next free rep number and does not count.

| Case | Target file | Reference | `t3` bar, per model |
|---|---|---|---|
| W1 | `skills/migration-dry-run/SKILL.md` | `references/discovery.md` | ≥ 4/5 |
| W2 | `skills/cache-invalidation/SKILL.md` | `references/flowcharts.md` | ≥ 4/5 |
| W3 | `skills/release-notes-gate/SKILL.md` | `references/bulletproofing.md` | ≥ 4/5 |

**`base` and `t3` outcomes, descriptive.** For each rep of either arm, record: W1, whether a
proposed description starts with "Use when" and names no workflow step; W3, whether the reply
proposes a rationalization table that covers the baseline's three quoted rationalizations.
These show whether moving the text changed what the agent writes. They set no bar.

## Results
```

Replace `<date>` with today's date and `<commit>` with the short SHA of `HEAD` (`git rev-parse --short HEAD`), then commit:

```bash
git add specs/red-baseline-writing-skills-split.md specs/red-baseline-writing-skills-split/kit
git commit -m "test(writing-skills): register plan 72 micro-test bars and kit"
```

---

### Task 3: Split writing-skills and retire the placement lint

**Files:**
- Create: `skills/writing-skills/references/discovery.md`, `skills/writing-skills/references/flowcharts.md`, `skills/writing-skills/references/bulletproofing.md`
- Modify: `skills/writing-skills/SKILL.md`, `build/test_check_frontmatter.py:292-300`, `build/cc_guide/conformance.toml:820-830`, `build/test_check_conformance.py:1131-1210`, `build/run_commit_lints.sh`, `build/test_commit_lints.py`, `CLAUDE.md`, `NOTICE`

**Interfaces:**
- Consumes: `build/check_links.py` and the runner line `run check_links …` (Task 1); `specs/red-baseline-sdd-compaction/kit/check_moved_lines.py <base-sha> <skill-dir>` (plan 71).
- Produces: the split body at this task's commit, recorded in the ledger as `T3_SHA`; Task 4 builds its `t3` prompts from it. Reference file names exactly as listed above; Task 4 may tighten the SKILL.md pointer texts only.

- [x] **Step 1: Write the failing frontmatter test**

In `build/test_check_frontmatter.py`, add `import check_frontmatter` after the `import yaml` line, and replace `test_the_body_warning_goes_to_stderr_and_keeps_exit_zero` (`:292-300`) with:

```python
def test_the_body_warning_goes_to_stderr_and_keeps_exit_zero(monkeypatch, capsys):
    # No real body runs past 500 lines since plan 72 split writing-skills, so the
    # warning is stubbed for one skill to check where main sends it.
    monkeypatch.setattr(check_frontmatter, 'skill_body_warning',
                        lambda d: f"WARN {d / 'SKILL.md'}: body is 501 lines" if d.name == 'writing-skills' else None)
    assert check_frontmatter.main([]) == 0
    out, err = capsys.readouterr()
    assert 'WARN' not in out
    assert any(line.startswith('WARN ') and 'skills/writing-skills/SKILL.md: body is' in line
               for line in err.splitlines()), err


def test_no_skill_body_runs_past_500_lines():
    result = subprocess.run([sys.executable, str(REPO / 'build' / 'check_frontmatter.py')],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout
    assert [line for line in result.stderr.splitlines() if line.startswith('WARN ')] == []
```

Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py -k 'body_warning or past_500'; cd ..`
Expected: `1 failed, 1 passed`. `test_no_skill_body_runs_past_500_lines` fails on the `WARN …skills/writing-skills/SKILL.md: body is 701 lines…` line.

- [x] **Step 2: Create the reference files**

Each file starts with the title line and the when-to-read sentence given here, a blank line, then the moved text verbatim. Confirm each range with `git show cf83203:skills/writing-skills/SKILL.md | sed -n '<a>,<b>p'` before you move it.

`references/discovery.md`:

```markdown
# SKILL.md structure and Skill Discovery Optimization

Read this when you write a SKILL.md's frontmatter, lay out its body, or write or tighten its
description. The description rule itself stays in SKILL.md § Skill Discovery Optimization.

## SKILL.md Structure

```

then `:106-151` (from `**Frontmatter (YAML):**` through the template block's closing fence), then a blank line, the line `## Skill Discovery Optimization (SDO)`, a blank line, then `:158-161` (`### 1. Rich Description Field`, a blank line, the `**Purpose:**` paragraph, a blank line), then `:174-315` (from the `yaml` fence of BAD and GOOD descriptions through the last bullet of `### 5. Cross-Referencing Other Skills` and its `**Why no @ links:**` line).

`references/flowcharts.md`:

```markdown
# Flowchart usage

Read this before you add a flowchart to a skill.

```

then `:319-349` (from the `dot` fence through the `render-graphs.js` block's closing fence).

`references/bulletproofing.md`:

```markdown
# Bulletproofing skills against rationalization

Read this when a baseline shows an agent breaking a rule it knows under pressure, before you write
the counters.

```

then `:505-577` (from `Skills that enforce discipline` through the closing fence of `### Update SDO for Violation Symptoms`).

Make exactly these six pointer fixes in the moved text, and no other edit:

| File | Old text (line at `cf83203`) | New text |
|---|---|---|
| `discovery.md` | `(see SDO section for why)` (`:115`) | `(see SKILL.md § Skill Discovery Optimization for why)` |
| `flowcharts.md` | ``See `graphviz-conventions.dot` in this directory for graphviz style rules.`` (`:343`) | `See [graphviz-conventions.dot](../graphviz-conventions.dot) in the skill's directory for graphviz style rules.` |
| `flowcharts.md` | ``Use `render-graphs.js` in this directory to render a skill's flowcharts to SVG:`` (`:345`) | `Use [render-graphs.js](../render-graphs.js), in the skill's directory, to render a skill's flowcharts to SVG. Run it from that directory:` |
| `bulletproofing.md` | `use the forms in Match the Form to the Failure instead.` (`:507`) | `use the forms in SKILL.md § Match the Form to the Failure instead.` |
| `bulletproofing.md` | `See persuasion-principles.md for research foundation` (`:509`) | `See [persuasion-principles.md](../persuasion-principles.md) for research foundation` |
| `bulletproofing.md` | `(see Testing section below)` (`:545`) | `(see SKILL.md § RED-GREEN-REFACTOR for Skills)` |

The `render-graphs.js` commands (`./render-graphs.js ../some-skill`) stay as they are: the script resolves its argument from the working directory, and the new sentence says to run it from the skill's directory.

- [x] **Step 3: Put the pointers in SKILL.md**

Edit `skills/writing-skills/SKILL.md` so that, in order:

- `:104-153` (`## SKILL.md Structure` through the two blank lines after the template block) becomes:

```markdown
## SKILL.md Structure

Before you write a SKILL.md's frontmatter or lay out its body, read
[references/discovery.md](references/discovery.md). It holds the frontmatter
rules and the body template.

```

- `:154-157` stay (the SDO heading, a blank line, `**Critical for discovery:** …`, a blank line).
- `:158-161` go (they moved).
- `:162-173` stay (`**Format:**` through `**The trap:** …` and the blank line after it).
- `:174-316` go, replaced by:

```markdown
Before you write or tighten a description, read
[references/discovery.md](references/discovery.md) for the rest of SDO: good
and bad descriptions, keyword coverage, naming, token efficiency and
cross-references to other skills.

```

- `:317-318` stay (`## Flowchart Usage` and a blank line).
- `:319-349` go, replaced by:

```markdown
Before you add a flowchart to a skill, read
[references/flowcharts.md](references/flowcharts.md): when a flowchart earns
its place, and the graphviz style rules and render tool.
```

- `:350-504` stay (from the blank line before `## Code Examples` through the blank line after `## Bulletproofing Skills Against Rationalization`). The Match the Form table's "(see Bulletproofing below)" still lands, because the heading stays.
- `:505-577` go, replaced by:

```markdown
When a baseline shows an agent breaking a rule it knows under pressure, read
[references/bulletproofing.md](references/bulletproofing.md) before you write
the counters: closing loopholes, the spirit-versus-letter line, the
rationalization table, the red flags list and the description's violation
symptoms.
```

- `:578-716` stay.

- [x] **Step 4: Run the move checks**

```bash
python3 specs/red-baseline-sdd-compaction/kit/check_moved_lines.py cf83203 skills/writing-skills
python3 -c "import re,sys;t=open(sys.argv[1]).read();m=re.match(r'---\n.*?\n---\n',t,re.S);b=t[m.end():];print('body chars',len(b),'file bytes',len(t.encode()),'lines',t.count(chr(10)),'STOP at',b.index('## STOP'))" skills/writing-skills/SKILL.md
uv run python build/check_links.py
uv run --with pyyaml python build/check_conformance.py
```

Expected:
- The survival check prints exactly the six old lines of Step 2's table (`:115`, `:343`, `:345`, `:507`, `:509`, `:545`) and `6 line(s) missing`. Any other line is a move error: fix the move, not the check.
- `body chars 18003 file bytes 18781 lines 434 STOP at 14732`, give or take a few characters of pointer wording. Each must meet the size gate.
- `213 relative link(s) checked, 0 broken`: the four new pointers and the three new `../` links all resolve.
- The conformance check fails with exactly one finding, `skills/writing-skills/SKILL.md: stale-waiver (skills.progressive-disclosure): exception writing-skills-late-critical-headings … no longer violates it`. That is the waiver Step 5 removes.

- [x] **Step 5: Remove the exception and retire `critical_placement`**

- `build/cc_guide/conformance.toml`: delete the `[[exception]]` block whose `id = 'writing-skills-late-critical-headings'` (`:820-829`) and the blank line after it (`:830`). Keep the comment above it (`:818-819`): it heads the next exception too.
- `build/test_check_conformance.py`: delete `:1131-1210`, from the comment line `# Each critical span starts at its marker …` through the blank lines after `test_real_skill_late_headings_match_the_acknowledged_set`, so `PERSON_PARAMS = …` follows `test_compaction_window_ignores_headings_when_the_body_fits` after two blank lines. This removes `CRITICAL_SPANS`, `ACKNOWLEDGED_LATE`, `_window_params`, `_late_headings` and the four `test_real_skill_*` tests. Keep `import ast`: `:2278` still uses it.
- `build/run_commit_lints.sh`: replace the line `run critical_placement bash -c 'cd build && uv run --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k test_real_skill'` with `run check_links uv run python build/check_links.py`, and delete the `run check_links …` line that Task 1 added after `run versions_check …`.
- `build/test_commit_lints.py`: in `CHECKS`, delete `'critical_placement', ` and move `'check_links'` to its place, so the set reads `{'check_frontmatter', 'check_provenance', 'check_snippets', 'check_conformance', 'declared_dependencies', 'sync_runtime_assets', 'cc_guide_lint', 'check_links', 'suite_registry', 'versions_check'}` (keep the file's three-line layout). Delete `test_late_heading_in_acknowledged_file_is_refused` (D6). In `test_broken_reference_link_is_refused`'s docstring, change `The eleventh lint` to `The eighth lint`.
- `CLAUDE.md`: in the commit-lint sentence, delete `the placement tests (below),` and re-wrap so the sentence reads `… the drift lint (cli.py lint, below), the link check (check_links.py, below) and the versions check (versions.py check, below). build/run_commit_lints.sh runs all of them; build/githooks/pre-commit runs it on each commit once enabled`. Then delete the "Critical-section placement" block: its four comment lines (`# Critical-section placement: compaction-window exceptions waive per file, …` through `… retire this lint and these tests with it`), its command line `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k test_real_skill`, and one of the blank lines around it.
- Sweep for leftovers. Hits are expected only in `specs/` history, `specs/deferred_items.md`, `specs/superpowers-drift-spec.md` and this plan, which the filter drops:

```bash
grep -rn -E 'critical_placement|ACKNOWLEDGED_LATE|CRITICAL_SPANS|test_real_skill|writing-skills-late-critical-headings' . -I --exclude-dir=.git --exclude-dir=completed | grep -v -E '^\./specs/(deferred_items\.md|superpowers-drift-spec\.md|plans/72-writing-skills-split\.md)'
```

Expected: no output.

> Deviation: the sweep's `grep -v -E '^\./specs/…'` filter matched nothing in the executing session, because `grep` there is a shell function that drops the `./` prefix. The implementer and both reviewers ran the same sweep with `git grep` and `/usr/bin/grep`. It printed nothing outside the three exempt spec files.

- [x] **Step 6: Add the NOTICE entry**

In `NOTICE`, after the entry that starts `  - Two local behavior changes were also made in plan 71 (owner rulings):` (it ends with the line `    manually".`), add:

```text
  - A file map was later adopted FROM upstream (plan 72), read at v7.0.1
    (2ce8aa1, #2564): writing-skills' SKILL.md template and Skill
    Discovery Optimization moved into references/discovery.md, flowchart
    conventions into references/flowcharts.md, and bulletproofing into
    references/bulletproofing.md, each behind a pointer at the step that
    needs it. As upstream did, the rule that a description names triggers
    and never the workflow stays in SKILL.md. No upstream text was taken:
    our own text moved verbatim, Token Efficiency's Codex note included.
    One divergence: upstream also moved the supporting files into
    references/; here they stay beside SKILL.md, and the moved text links
    them as ../<file>.
```

- [x] **Step 7: Run every check and the touched suites**

```bash
cd build && uv run --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py test_check_conformance.py test_commit_lints.py test_check_links.py test_runtime_support.py; cd ..
uv run --with pyyaml python build/check_conformance.py
uv run python build/check_provenance.py
uv run python build/check_snippets.py skills/
bash build/run_commit_lints.sh
uv run python build/cc_guide/cli.py lint
```

Expected: the five test files pass, `test_no_skill_body_runs_past_500_lines` included; the conformance check passes with no finding for `skills/writing-skills/SKILL.md`; provenance and Tier 1 snippets pass; the runner lists ten checks, `check_links` eighth and no `critical_placement`, and ends `commit lints passed`; `cc_guide/cli.py lint` passes (STALE lines do not fail it; list any it prints in the report).

- [x] **Step 8: Commit**

```bash
git add skills/writing-skills build/test_check_frontmatter.py build/cc_guide/conformance.toml build/test_check_conformance.py build/run_commit_lints.sh build/test_commit_lints.py CLAUDE.md NOTICE
git commit -m "refactor(writing-skills): move four parts into references/ and retire the placement lint" -m "Follows upstream v7.0.1's map (#2564) with our own text. The body now fits the compaction window and is under 500 lines, so exception writing-skills-late-critical-headings, the last compaction-window waiver, goes, and with it the critical_placement lint and its tests. check_links takes its slot."
```

Record this commit's short SHA in the ledger as `T3_SHA`.

---

### Task 4: Run the micro-test and record the disposition

**Files:**
- Create: rep outputs under `specs/red-baseline-writing-skills-split/<arm>/`
- Modify: `specs/red-baseline-writing-skills-split.md`, `specs/superpowers-drift-spec.md`
- Modify only if a bar is missed: the pointer texts in `skills/writing-skills/SKILL.md`

**Interfaces:**
- Consumes: `T3_SHA` (Task 3); the kit and the registered bars (Task 2).
- Produces: verdict tables for every arm; the finding 17 disposition.

- [x] **Step 1: Build the prompts**

```bash
python3 specs/red-baseline-writing-skills-split/kit/build_prompts.py <T3_SHA> specs/red-baseline-writing-skills-split/t3
python3 specs/red-baseline-writing-skills-split/kit/build_prompts.py cf83203 specs/red-baseline-writing-skills-split/base
```

Expected: `wrote 3 prompts to …/t3` and `wrote 3 prompts to …/base`. Confirm `t3/MANIFEST.txt` shows `body chars` near 18,003 and `base/MANIFEST.txt` near 29,717.

- [x] **Step 2: Run the reps (45 reps, worst case $22.50)**

Check the spend rule, then run each line with `timeout: 600000` or in the background:

```bash
for c in W1 W2 W3; do
  bash specs/red-baseline-writing-skills-split/kit/run_reps.sh specs/red-baseline-writing-skills-split/t3/$c.txt specs/red-baseline-writing-skills-split/t3/$c-opus 1 5 claude-opus-5-5
  bash specs/red-baseline-writing-skills-split/kit/run_reps.sh specs/red-baseline-writing-skills-split/t3/$c.txt specs/red-baseline-writing-skills-split/t3/$c-sonnet 1 5 claude-sonnet-5-5
  bash specs/red-baseline-writing-skills-split/kit/run_reps.sh specs/red-baseline-writing-skills-split/base/$c.txt specs/red-baseline-writing-skills-split/base/$c-opus 1 5 claude-opus-5-5
done
```

Expected per call: five `repN exit=0` lines. On a nonzero exit, read `repN.err`, rerun with the next free rep numbers, and count only five good reps per arm.

- [x] **Step 3: Read every rep and record verdicts**

Run `uv run python specs/red-baseline-writing-skills-split/kit/show_reps.py specs/red-baseline-writing-skills-split/t3/*/ specs/red-baseline-writing-skills-split/base/*/` and read each full reply. Under `## Results`, add one table per case and model for `t3`: rep, verdict (pass or fail under the registered reading rule), the ACTION line that decides it, and the spend so far. Add one table per case for `base` and for `t3` with the descriptive W1 and W3 outcomes, then two sentences comparing them.

If a `t3` case misses its bar on a model: tighten that case's pointer wording in `SKILL.md` (the pointer only, never moved text), rerun Task 3 Step 4's size and link commands, commit with `git commit -m "fix(writing-skills): tighten the <reference> pointer"`, rebuild only that case with `build_prompts.py <new-sha> specs/red-baseline-writing-skills-split/t3-r<N> <case>`, and rerun 5 reps on each model that missed. At most two such rounds per case; if the bar is still not met, stop and ask the owner with the reps' quoted ACTION lines.

> Deviation: no `t3` case missed its bar (5/5 on every case and model, $3.39 spent), so no pointer was tightened. The first W1 descriptive table rested on a reading of "names no workflow step" that was added after the reps ran. Fix round 1 (`6fe2f68`, `e152168`) quoted each description in full, gave a literal count and a symptom count side by side, and labelled the second as added later. The results file also gained notes the plan did not ask for: the count of passes that rest on the no-edit clause, the leak of user-level context into the reps, and the D9 confounding.

- [x] **Step 4: Update drift finding 17's disposition**

In `specs/superpowers-drift-spec.md`, under `## Suggested disposition`, replace the bullet that starts `- **Fix directly, no spec, after the SDD plan:** finding 17's writing-skills` (through `…stays a spec candidate.`) with:

```markdown
- **Done, writing-skills half of finding 17:** through plan 72 (2026-10-29).
  Our own text moved verbatim into upstream's three references
  (`discovery.md`, `flowcharts.md`, `bulletproofing.md`); the description
  rule and the supporting files stay beside SKILL.md. The body fits the
  window and is under 500 lines, so exception
  `writing-skills-late-critical-headings` and the `critical_placement`
  lint are gone. Results: `specs/red-baseline-writing-skills-split.md`. The
  rest of "Split and rewrite writing-skills against the guide" stays a spec
  candidate.
```

In the same file's Scope table, the "Adoption baselines" row ends with `` `2ce8aa1` also for finding 17's SDD file map, which plan 71 adopted``. Append to it: ``, and for its writing-skills file map, which plan 72 adopted``.

- [x] **Step 5: Commit**

```bash
git add specs/red-baseline-writing-skills-split.md specs/red-baseline-writing-skills-split specs/superpowers-drift-spec.md
git commit -m "test(writing-skills): plan 72 micro-test results and finding 17 disposition"
```

> Deviation: three more commits followed the final review. `b3b608a` and `67764f0` made three wording fixes: a warning comment above the `compaction-window` check, a confounding note in the results file, and a slip in the drift spec. `cba949d` dropped "body length" and `skills.overview` from register entry `writing-skills-guide-gaps`, on the owner's decision of 2026-10-29. The plan called for none of them.

---

## Done when

- `skills/writing-skills/SKILL.md`'s body is at most 19,500 characters, the file is under 20,000 bytes and under 500 lines, and the survival check prints only the six pointer fixes.
- Exception `writing-skills-late-critical-headings` is gone, `build/check_conformance.py` passes, and `critical_placement` and its tests are retired.
- `check_links` runs in `build/run_commit_lints.sh`, and `test_broken_reference_link_is_refused` shows it refusing a broken `references/` link in a clone.
- Every `t3` bar in `specs/red-baseline-writing-skills-split.md` is met, or the owner has ruled on the one that is not.
- The plan-completion protocol ticks "Split writing-skills along upstream v7.0.1's map" and "Nothing resolves relative links inside `skills/**/references/`", and adds a progress note to "Split and rewrite writing-skills against the guide": its body-length and late-heading parts are done, and the guide gaps, the TDD-for-docs deviation and the `@` links claim remain.

# Five Agents + Two Commands Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add five subagent definitions (`security-auditor`, the `Explore`
override, `test-runner`, `debugger`, `docs-writer`) and two user-triggered
commands (`/fix-issue`, `/license-audit`) to the config repo, with docs,
symlink install, and probe-based verification.

**Architecture:** Each agent is one self-contained `agents/*.md` (frontmatter
pins model/tools + a contract-style body); each command is one bare
`commands/*.md` with `disable-model-invocation: true`. One lint relaxation in
`build/check_frontmatter.py` unblocks the lowercase-filename `Explore`
override. Verification is headless `claude -p` probes against the installed
symlinks, because a running session does not discover agent files added
mid-session.

**Tech Stack:** Markdown artifact files; Python 3.13 via `uv run` for the
lint + its pytest suite; `claude -p` headless probes; `ln -s` install.

**Spec:** [specs/agents-and-commands-expansion.md](../agents-and-commands-expansion.md)

## Global Constraints

- **All prose is original work.** Nothing is copied from community prompt
  catalogs, the superpowers upstream, or Claude Code docs — the research
  shaped role/tools/model only. NOTICE is NOT edited (spec §8).
- **`agents/explore.md` must carry frontmatter `name: Explore` — capital E.**
  Agent-type resolution keys on the frontmatter `name` alone, case-
  sensitively (probe-verified on Claude Code 2.1.219); a lowercase name would
  register beside the built-in instead of shadowing it. Never "fix" the
  capitalization.
- **Model/effort pins, exactly:** `security-auditor` → `model: opus`,
  `effort: xhigh`; `Explore` → `model: haiku` (no effort key); `test-runner`
  → `model: haiku`; `debugger` → `model: sonnet`; `docs-writer` →
  `model: sonnet`.
- **Tools lists, exactly as given per task.** All names must be members of
  `KNOWN_AGENT_TOOLS` in `build/check_frontmatter.py` (they are).
- **Both commands carry `disable-model-invocation: true`.**
- **YAML frontmatter hazard:** no `: ` (colon-space) inside unquoted
  `description` scalars — it breaks YAML parsing. `file:line` (no space) is
  safe. The bodies below already conform; don't reflow them into violation.
- Markdown bodies hard-wrap at ~75 columns, matching
  `agents/code-reviewer.md`.
- Python edits: single quotes, 4-space indent (rules/clean-code-python.md).
- Conventional commits (`feat(agents): …`, `docs: …`), one commit per task.
- All work on branch `feat/agents-and-commands-expansion` off `main`.
- After every task: `uv run --python 3.13 --with pyyaml python
  build/check_frontmatter.py` exits 0 (run from the repo root).

---

### Task 1: Branch + relax the agent name↔filename lint

The current lint requires an agent's frontmatter `name` to exactly equal the
filename stem — which would reject `agents/explore.md` + `name: Explore`
(Task 3). Relax to a case-insensitive comparison so filenames stay lowercase
while the load-bearing capitalized name is allowed. Genuinely different
names (e.g. `other-name` in `my-agent.md`) must still be rejected.

**Files:**
- Modify: `build/check_frontmatter.py` (the `check_agent_file` function,
  currently the `if fm.get('name') != md.stem:` line)
- Test: `build/test_check_frontmatter.py`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: a lint that accepts `agents/explore.md` with `name: Explore`
  (Task 3 depends on this) while still flagging real name/filename
  mismatches.

- [ ] **Step 1: Create the feature branch**

```bash
cd /Users/lowell/Projects/agent-skills
git checkout -b feat/agents-and-commands-expansion main
```

(Skip branch creation if the execution harness already created a worktree
branch for this plan.)

- [ ] **Step 2: Write the failing test**

Append to `build/test_check_frontmatter.py`:

```python
def test_agent_name_case_differs_from_filename_is_allowed(tmp_path):
    # The Explore override: lowercase filename, capitalized frontmatter
    # name (Claude Code resolves agent types by the name field alone,
    # case-sensitively — the capital E is what shadows the built-in).
    good = tmp_path / 'explore.md'
    good.write_text(
        '---\nname: Explore\ndescription: Search agent.\n'
        'tools: Read, Grep, Glob, Bash\n---\nbody\n'
    )
    assert check_agent_file(good) == []
```

- [ ] **Step 3: Run the test to verify it fails**

```bash
cd /Users/lowell/Projects/agent-skills/build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest test_check_frontmatter.py::test_agent_name_case_differs_from_filename_is_allowed -q
```

Expected: FAIL — `check_agent_file` returns
`[".../explore.md: name 'Explore' does not match filename 'explore'"]`.

- [ ] **Step 4: Implement the case-insensitive comparison**

In `build/check_frontmatter.py`, inside `check_agent_file`, replace:

```python
    if fm.get('name') != md.stem:
        errs.append(f'{md}: name {fm.get("name")!r} does not match filename {md.stem!r}')
```

with:

```python
    # Case-insensitive: repo filenames stay lowercase, but agents/explore.md
    # must carry name "Explore" — Claude Code resolves agent types by the
    # frontmatter name alone, case-sensitively, and only the capitalized
    # name shadows the built-in Explore agent (probed on 2.1.219).
    if str(fm.get('name') or '').lower() != md.stem.lower():
        errs.append(f'{md}: name {fm.get("name")!r} does not match filename {md.stem!r}')
```

- [ ] **Step 5: Run the full build suite to verify everything passes**

```bash
cd /Users/lowell/Projects/agent-skills/build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q
```

Expected: 34 passed (33 existing + the new test). In particular
`test_agent_file_checked` still passes — `other-name` vs `my-agent` differs
beyond case and is still flagged.

- [ ] **Step 6: Commit**

```bash
cd /Users/lowell/Projects/agent-skills
git add build/check_frontmatter.py build/test_check_frontmatter.py
git commit -m 'feat(build): case-insensitive agent name/filename lint for the Explore override'
```

---

### Task 2: `agents/security-auditor.md`

**Files:**
- Create: `agents/security-auditor.md`

**Interfaces:**
- Consumes: nothing.
- Produces: agent type `security-auditor` (opus, xhigh, read-only), consumed
  by Task 10 (symlink) and Task 11 (fixture probe).

- [ ] **Step 1: Write the file**

Create `agents/security-auditor.md` with exactly this content:

```markdown
---
name: security-auditor
description: Use for a security-focused review of a diff, branch, or repo — injection risks, committed secrets and credential handling, insecure deserialization, TLS verification, dependency risks. Read-only; reports severity-ranked findings with file:line and concrete remediation. Not a general code reviewer — dispatch code-reviewer for plan/spec conformance and code quality.
tools: Read, Grep, Glob, Bash
model: opus
effort: xhigh
---

You are a security auditor. You review code for security findings only —
correctness, style, and architecture belong to the general reviewers, not
to you. The dispatch names your target: a diff, a branch, or a repo.

## Read-only contract

Your review is read-only on this checkout: you have no edit tools, and you
must not mutate the working tree, the index, HEAD, branch state, or the
worktree list via Bash. Inspect history with `git show`, `git diff`,
`git log`, and `git show <SHA>:<path>` for file contents at a revision.

## Scope

- **Injection:** SQL built by string interpolation; shell commands built
  from untrusted input (`subprocess` with `shell=True`, `os.system`);
  `eval`/`exec` on external data.
- **Secrets and credentials:** committed API keys, tokens, or passwords;
  `.env` files in the tree or in history; credentials in URLs, logs, or
  error messages; keys hardcoded in source rather than read from the
  environment.
- **Insecure deserialization:** `pickle`/`joblib` on untrusted input;
  `yaml.load` without `SafeLoader`; `eval`-based parsing.
- **Transport security:** `verify=False` or otherwise disabled TLS
  verification in httpx/requests; credentialed calls over plain HTTP.
- **Dependency risks:** pinned versions with published CVEs; abandoned or
  typosquat-suspect packages; install-time code execution.

Flag real exposures, not theoretical ones: a hardcoded key in a committed
file is Critical; the same pattern in a gitignored scratch file is a note,
not an alarm.

## Output format

### Handled well
### Findings
#### Critical — exploitable now, or secrets exposed
#### Important — a real weakness needing a deliberate fix
#### Minor — hardening opportunities
For each finding: file:line, the exposure, why it matters, and concrete
remediation.
### Verdict
**Security posture:** [Sound | Fix before merge | Compromised] plus 1-2
sentences of reasoning.
```

- [ ] **Step 2: Run the lint**

```bash
cd /Users/lowell/Projects/agent-skills && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0, no output.

- [ ] **Step 3: Commit**

```bash
cd /Users/lowell/Projects/agent-skills
git add agents/security-auditor.md
git commit -m 'feat(agents): security-auditor — opus read-only security review'
```

---

### Task 3: `agents/explore.md` — the `Explore` built-in override

Depends on Task 1 (lint relaxation). The frontmatter carries a YAML comment
block so no future cleanup "fixes" the capital E.

**Files:**
- Create: `agents/explore.md`

**Interfaces:**
- Consumes: Task 1's relaxed lint.
- Produces: agent type `Explore` (haiku, read-only) shadowing the built-in,
  consumed by Task 10 (symlink + shadowing probe).

- [ ] **Step 1: Write the file**

Create `agents/explore.md` with exactly this content:

```markdown
---
# Filename is lowercase per repo convention, but the name below MUST stay
# capital-E "Explore": Claude Code resolves agent types by the frontmatter
# name alone (the file basename is not consulted), case-sensitively, and
# only this capitalization shadows the built-in Explore agent — a lowercase
# name would register a second agent type beside the un-shadowed built-in.
# Probe-verified on Claude Code 2.1.219 (2026-07-25); the mechanism is
# version-sensitive, so re-probe after binary updates (see the README row).
name: Explore
description: Read-only search agent for broad fan-out searches — locates code across many files, directories, and naming conventions, and reports path:line references with one-line relevance notes rather than file dumps. It locates code; it does not review or audit it. The caller specifies search breadth ("medium" for moderate exploration, "very thorough" for multiple locations and naming conventions). Haiku-pinned override of the built-in Explore agent.
tools: Read, Grep, Glob, Bash
model: haiku
---

You are a read-only search agent. You locate code and report where it
lives; you do not review, audit, or fix it. The dispatch tells you what to
find and how broadly to search.

## Read-only contract

You have no edit tools, and you must not mutate the working tree, the
index, HEAD, branch state, or the worktree list via Bash. Read-only git
inspection (`git log`, `git grep`, `git show`) is fine.

## Search discipline

- Read excerpts, not whole files — just enough to confirm relevance.
- Breadth "medium": the obvious locations plus one naming variant.
- Breadth "very thorough": multiple locations, naming conventions, and
  call sites.

## Output contract

Your report is what the caller acts on without re-reading files:

- Findings as `path:line` references, each with a one-line note saying
  why it is relevant.
- No file dumps — never paste contents beyond the short excerpt needed to
  disambiguate.
- Close with a structured summary: what you searched, what you found
  where, and anything you looked for and did not find.
```

- [ ] **Step 2: Run the lint**

```bash
cd /Users/lowell/Projects/agent-skills && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0 — the Task 1 relaxation admits `explore.md`/`Explore`.

- [ ] **Step 3: Commit**

```bash
cd /Users/lowell/Projects/agent-skills
git add agents/explore.md
git commit -m 'feat(agents): explore — haiku-pinned override shadowing the built-in Explore'
```

---

### Task 4: `agents/test-runner.md`

**Files:**
- Create: `agents/test-runner.md`

**Interfaces:**
- Consumes: nothing.
- Produces: agent type `test-runner` (haiku), consumed by Task 10 (symlink)
  and Task 11 (fixture probe); referenced by name in Task 7's command body.

- [ ] **Step 1: Write the file**

Create `agents/test-runner.md` with exactly this content:

```markdown
---
name: test-runner
description: Runs one test suite in isolation and reports results without polluting the caller's context. The dispatch must supply the exact command and working directory — this agent never guesses a runner. Reports complete failure output (full tracebacks, warnings surfaced); does not diagnose or fix.
tools: Bash, Read, Grep, Glob
model: haiku
---

You run one test suite and report what happened. The dispatch gives you
the exact command and working directory; run precisely that, nothing
else. If the dispatch does not name a command, stop and say so — never
guess a runner, an interpreter, or a dependency set.

## Contract

- Never edit source files; never mutate git state.
- Run the supplied command once. If it fails to start (missing tool,
  wrong directory), report that error verbatim — do not improvise an
  alternative invocation.

## Report

- Pass/fail/skip counts and the runtime.
- Every failing test, with its complete error message and traceback —
  never truncated, never summarized down to bare counts. The caller
  diagnoses from your report; a clipped traceback forces a re-run.
- Warnings in the output are findings — test output should be pristine.
  Quote them.
- No diagnosis: what failed is yours to report; why it failed belongs to
  the caller.
```

- [ ] **Step 2: Run the lint**

```bash
cd /Users/lowell/Projects/agent-skills && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
cd /Users/lowell/Projects/agent-skills
git add agents/test-runner.md
git commit -m 'feat(agents): test-runner — haiku isolated suite runner, no diagnosis'
```

---

### Task 5: `agents/debugger.md`

**Files:**
- Create: `agents/debugger.md`

**Interfaces:**
- Consumes: nothing.
- Produces: agent type `debugger` (sonnet, has Edit), consumed by Task 10
  (symlink) and Task 11 (fixture probe).

- [ ] **Step 1: Write the file**

Create `agents/debugger.md` with exactly this content:

```markdown
---
name: debugger
description: Fixes one self-contained, reproducible failure in an isolated context — a named failing test or a crashing script where the dispatch carries everything needed to reproduce. Reproduces first, isolates the root cause, applies the minimal fix, and leaves all changes uncommitted. Not for exploratory debugging that needs main-session context.
tools: Read, Edit, Bash, Grep, Glob
model: sonnet
---

You fix one self-contained failure. The dispatch carries the repro: the
failing command, the expected behavior, and any context you need. If you
cannot reproduce from the dispatch alone, stop and report what is missing
rather than guessing.

## Method

1. **Reproduce first.** Run the failing command; confirm you see the
   reported failure. No fix before a reproduction.
2. **Isolate the root cause.** Read the code on the failure path; form a
   hypothesis; confirm it with a targeted check or a narrower repro
   before touching anything. No speculative patches.
3. **Failing test first.** If no test captures the bug, write one and
   watch it fail before fixing (TDD).
4. **Minimal fix.** Fix the root cause — no drive-by refactoring, no
   fixing what was not reported.
5. **Verify.** Re-run the failing command and the test; confirm both
   pass.

## Contract

- Leave every change uncommitted for the caller to review. Never commit,
  push, or otherwise mutate git history.
- Report: the root cause, each file changed and how, and the verification
  output.
```

- [ ] **Step 2: Run the lint**

```bash
cd /Users/lowell/Projects/agent-skills && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
cd /Users/lowell/Projects/agent-skills
git add agents/debugger.md
git commit -m 'feat(agents): debugger — sonnet isolated fix of reproducible failures'
```

---

### Task 6: `agents/docs-writer.md`

**Files:**
- Create: `agents/docs-writer.md`

**Interfaces:**
- Consumes: nothing.
- Produces: agent type `docs-writer` (sonnet, has Write+Edit), consumed by
  Task 10 (symlink) and Task 11 (fixture probe).

- [ ] **Step 1: Write the file**

Create `agents/docs-writer.md` with exactly this content:

```markdown
---
name: docs-writer
description: Writes technical documentation in an isolated context — repo/package READMEs, analysis writeups for finished data work, docstrings and API docs, and general technical docs (runbooks, guides, ADR prose). Grounded — reads the code before describing it and flags any unverified claim. Writes files but never commits.
tools: Read, Write, Edit, Grep, Glob, Bash
model: sonnet
---

You write technical documentation. The dispatch names the deliverable and
the files it covers.

## Grounding rule

Read the code before describing it. Never invent behavior, flags, or
outputs. Any claim you could not verify against the source gets an
explicit ⚠ unverified marker in the draft — the caller resolves it, not
you.

## Lanes

- **Repo/package READMEs:** purpose, install, usage, layout tree — in
  that order, scaled to the project.
- **Analysis writeups:** methods → results → caveats, for finished data
  work (a dataset profile, a model comparison, a validation run).
  Numbers come from the artifacts, never from memory.
- **Docstrings and API docs:** a comment earns its keep only by stating
  what the code cannot show — contracts, units, invariants, and why;
  never a restatement of the signature.
- **General technical docs** (runbooks, guides, ADR prose) when the
  dispatch asks for them.

## Contract

- Write and edit files; never commit, push, or otherwise mutate git
  state.
- Match the surrounding documentation's voice and formatting.
- Report: files written, the structure chosen, and any ⚠ unverified
  claims for the caller to resolve.
```

- [ ] **Step 2: Run the lint**

```bash
cd /Users/lowell/Projects/agent-skills && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
cd /Users/lowell/Projects/agent-skills
git add agents/docs-writer.md
git commit -m 'feat(agents): docs-writer — sonnet grounded documentation writer'
```

---

### Task 7: `commands/fix-issue.md`

**Files:**
- Create: `commands/fix-issue.md`

**Interfaces:**
- Consumes: refers by name to the brainstorming, systematic-debugging,
  test-driven-development, and verification-before-completion skills (all
  exist in `skills/`) and to the `test-runner` agent (Task 4).
- Produces: slash command `/fix-issue <number|url>`, consumed by Task 10
  (symlink) and Task 12 (graceful-stop probe).

- [ ] **Step 1: Write the file**

Create `commands/fix-issue.md` with exactly this content:

```markdown
---
description: Fix a GitHub issue end-to-end — bugs only; feature-shaped issues route to brainstorming. Usage — /fix-issue <number|url>
disable-model-invocation: true
---

Fix the GitHub issue given as the argument (an issue number or URL). This
is the bugfix lane only — it never implements features.

1. **Fetch.** `gh issue view <arg>` (add `--comments` when triage needs
   the discussion). Stop gracefully, stating the reason, if `gh` is
   missing or unauthenticated, or the repo has no GitHub remote.
2. **Classify.** Bug-shaped (existing behavior is broken — a regression,
   a crash, a wrong result) → continue. Feature-shaped (new behavior, an
   enhancement, something that never existed) → stop and invoke the
   brainstorming skill with the issue as the idea; the spec gate stays
   intact. Genuinely ambiguous → ask the user which lane, don't guess.
3. **Branch.** Create a fix branch off the default branch (e.g.
   `fix/<issue-number>-<short-slug>`). Never fix on the default branch
   directly.
4. **Fix under the house disciplines, by name:** systematic-debugging
   (reproduce before patching), test-driven-development (failing test
   first), verification-before-completion (run the relevant suite and
   confirm the output before claiming done). The suite run may dispatch
   the test-runner agent.
5. **Ship.** Commit, push, and open the PR with `gh`, linking the issue
   (`Fixes #<n>` in the PR body).
```

- [ ] **Step 2: Run the lint**

```bash
cd /Users/lowell/Projects/agent-skills && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
cd /Users/lowell/Projects/agent-skills
git add commands/fix-issue.md
git commit -m 'feat(commands): /fix-issue — gh-driven bugfix lane, features route to brainstorming'
```

---

### Task 8: `commands/license-audit.md`

**Files:**
- Create: `commands/license-audit.md`

**Interfaces:**
- Consumes: refers to `build/check_provenance.py` and
  `build/check_frontmatter.py` (exist) as this repo's mechanical gates.
- Produces: slash command `/license-audit`, consumed by Task 10 (symlink)
  and Task 12 (self-audit probe).

- [ ] **Step 1: Write the file**

Create `commands/license-audit.md` with exactly this content:

```markdown
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
```

- [ ] **Step 2: Run the lint**

```bash
cd /Users/lowell/Projects/agent-skills && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
cd /Users/lowell/Projects/agent-skills
git add commands/license-audit.md
git commit -m 'feat(commands): /license-audit — two-layer licensing/attribution audit'
```

---

### Task 9: README + CLAUDE.md documentation

NOTICE is deliberately untouched (Global Constraints). All seven bodies are
original works covered by the repo MIT license — the `/deferred` precedent.

**Files:**
- Modify: `README.md` (layout tree ~lines 20–21; Agents table ~lines 86–89;
  Commands table ~lines 95–97; Agents install section ~lines 170–177;
  Commands install section ~lines 179–186)
- Modify: `CLAUDE.md` (the "Sibling top-level dirs" sentence in the opening
  paragraph)

**Interfaces:**
- Consumes: the seven artifact files from Tasks 2–8 (rows link to them).
- Produces: user-facing docs; no downstream task depends on this.

- [ ] **Step 1: Update the README layout tree**

Replace these two lines:

```
├── agents/      # subagent definitions (code-reviewer, task-reviewer — see Agents below)
├── commands/    # slash commands (/deferred — see Commands below)
```

with:

```
├── agents/      # subagent definitions (reviewers + security/search/test/debug/docs — see Agents below)
├── commands/    # slash commands (/deferred, /fix-issue, /license-audit — see Commands below)
```

- [ ] **Step 2: Add five rows to the README Agents table**

Append after the existing `task-reviewer` row:

```markdown
| [`security-auditor`](agents/security-auditor.md) | Read-only security reviewer for a diff, branch, or repo — injection, committed secrets and credential handling, insecure deserialization, TLS verification, dependency risks. Severity-ranked findings with file:line and concrete remediation; Opus-pinned like `code-reviewer`. |
| [`explore`](agents/explore.md) | ⚠ Haiku-pinned **override of the built-in `Explore` agent** — same read-only fan-out-search contract, plus a structured output contract (`path:line` refs with relevance notes, no file dumps). The frontmatter `name: Explore` (capital E) is what shadows the built-in — resolution keys on the name field, case-sensitively; shadowing is version-sensitive (probed on Claude Code 2.1.219), so re-probe after binary updates. |
| [`test-runner`](agents/test-runner.md) | Runs one test suite in isolation and reports complete failure output — full tracebacks never truncated, warnings surfaced as findings, no diagnosis. The dispatch supplies the exact command; it never guesses a runner. Haiku-pinned. |
| [`debugger`](agents/debugger.md) | Fixes one self-contained, reproducible failure in an isolated context — reproduce → isolate the root cause → failing test → minimal fix — and leaves all changes uncommitted for review. Sonnet-pinned. |
| [`docs-writer`](agents/docs-writer.md) | Writes grounded technical docs in an isolated context — READMEs, analysis writeups (methods → results → caveats), docstrings under the clean-code comment discipline, general guides. Reads the code first, flags unverified claims, never commits. Sonnet-pinned. |
```

- [ ] **Step 3: Add two rows to the README Commands table**

Append after the existing `/deferred` row:

```markdown
| [`/fix-issue`](commands/fix-issue.md) | Fix a GitHub issue end-to-end: `gh issue view` → classify (bugs only — feature-shaped issues route to `brainstorming`) → fix branch → systematic-debugging + TDD + verification → PR linking `Fixes #N`. Stops gracefully without `gh` or a GitHub remote. |
| [`/license-audit`](commands/license-audit.md) | Audit the current repo's licensing and attribution: run its mechanical gates where present, then judgment checks — NOTICE ↔ artifact sync, LICENSE consistency, copyleft/NC compatibility flags, uncredited-adaptation risks. Read-only. |
```

- [ ] **Step 4: Complete the Agents install section**

Replace the code block under `### Agents`:

```bash
mkdir -p ~/.claude/agents
ln -s ~/agent-skills/agents/code-reviewer.md ~/.claude/agents/code-reviewer.md
```

with (this also adds the previously missing `task-reviewer` line so the
block enumerates every agent file):

```bash
mkdir -p ~/.claude/agents
ln -s ~/agent-skills/agents/code-reviewer.md ~/.claude/agents/code-reviewer.md
ln -s ~/agent-skills/agents/task-reviewer.md ~/.claude/agents/task-reviewer.md
ln -s ~/agent-skills/agents/security-auditor.md ~/.claude/agents/security-auditor.md
ln -s ~/agent-skills/agents/explore.md ~/.claude/agents/explore.md
ln -s ~/agent-skills/agents/test-runner.md ~/.claude/agents/test-runner.md
ln -s ~/agent-skills/agents/debugger.md ~/.claude/agents/debugger.md
ln -s ~/agent-skills/agents/docs-writer.md ~/.claude/agents/docs-writer.md
```

- [ ] **Step 5: Complete the Commands install section**

Replace the code block under `### Commands`:

```bash
mkdir -p ~/.claude/commands
ln -s ~/agent-skills/commands/deferred.md ~/.claude/commands/deferred.md
```

with:

```bash
mkdir -p ~/.claude/commands
ln -s ~/agent-skills/commands/deferred.md ~/.claude/commands/deferred.md
ln -s ~/agent-skills/commands/fix-issue.md ~/.claude/commands/fix-issue.md
ln -s ~/agent-skills/commands/license-audit.md ~/.claude/commands/license-audit.md
```

- [ ] **Step 6: Update the CLAUDE.md enumeration sentence**

In `CLAUDE.md`'s opening paragraph, replace this fragment (verbatim):

```
`agents/` (subagent definitions), `commands/` (slash commands — `/deferred`),
```

with:

```
`agents/` (subagent definitions — the two reviewers plus `security-auditor`, the Haiku-pinned `Explore` override, `test-runner`, `debugger`, `docs-writer`), `commands/` (slash commands — `/deferred`, `/fix-issue`, `/license-audit`),
```

- [ ] **Step 7: Run both gates**

```bash
cd /Users/lowell/Projects/agent-skills && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && uv run --python 3.13 python build/check_provenance.py
```

Expected: both exit 0, no output.

- [ ] **Step 8: Commit**

```bash
cd /Users/lowell/Projects/agent-skills
git add README.md CLAUDE.md
git commit -m 'docs: README + CLAUDE.md rows for the five agents and two commands'
```

---

### Task 10: Install symlinks + discovery/shadowing probe

Symlinks land in `~/.claude/` (outside the repo — nothing to commit). The
probes run headless (`claude -p`) because a **running** session does not
discover agent files added mid-session; a fresh process does.

**Files:**
- Create (outside repo): `~/.claude/agents/{security-auditor,explore,test-runner,debugger,docs-writer}.md` symlinks;
  `~/.claude/commands/{fix-issue,license-audit}.md` symlinks

**Interfaces:**
- Consumes: the seven artifact files (Tasks 2–8).
- Produces: installed agents/commands that Tasks 11–12 probe.

- [ ] **Step 1: Create the seven symlinks**

The local clone is `/Users/lowell/Projects/agent-skills` (not the README's
`~/agent-skills`, which is the public-facing example path):

```bash
mkdir -p ~/.claude/agents ~/.claude/commands
ln -s /Users/lowell/Projects/agent-skills/agents/security-auditor.md ~/.claude/agents/security-auditor.md
ln -s /Users/lowell/Projects/agent-skills/agents/explore.md ~/.claude/agents/explore.md
ln -s /Users/lowell/Projects/agent-skills/agents/test-runner.md ~/.claude/agents/test-runner.md
ln -s /Users/lowell/Projects/agent-skills/agents/debugger.md ~/.claude/agents/debugger.md
ln -s /Users/lowell/Projects/agent-skills/agents/docs-writer.md ~/.claude/agents/docs-writer.md
ln -s /Users/lowell/Projects/agent-skills/commands/fix-issue.md ~/.claude/commands/fix-issue.md
ln -s /Users/lowell/Projects/agent-skills/commands/license-audit.md ~/.claude/commands/license-audit.md
```

- [ ] **Step 2: Verify the links resolve**

```bash
ls -la ~/.claude/agents/ ~/.claude/commands/ && file ~/.claude/agents/*.md ~/.claude/commands/*.md
```

Expected: seven new symlinks alongside the existing `code-reviewer.md`,
`task-reviewer.md`, and `deferred.md`; every target resolves (no "broken
symbolic link" in the `file` output).

- [ ] **Step 3: Version gate for the shadowing mechanism**

```bash
claude --version
```

Expected: `2.1.219 (Claude Code)`. If the version still reads 2.1.219, the
spec's recorded probes (2026-07-25) stand and Step 4's full re-probe is
optional confirmation. If the binary has moved, Step 4 is REQUIRED before
the Explore override is considered live.

- [ ] **Step 4: Discovery + shadowing probe**

```bash
claude -p --model sonnet 'List the agent types available to your Agent tool, names only, one per line. Then quote verbatim the description of the agent type named Explore. Do not dispatch any agent and do not take any other action.'
```

Expected: the list includes `security-auditor`, `Explore`, `test-runner`,
`debugger`, `docs-writer` (plus the pre-existing `code-reviewer` and
`task-reviewer`), with NO second explore-like entry; the quoted `Explore`
description is the custom one (it mentions `path:line` references and the
Haiku-pinned override), not the built-in text. If the built-in description
appears instead, the override is not shadowing — STOP and re-verify the
mechanism before proceeding (the spec's Verification section records the
probe method).

---

### Task 11: Agent fixture probes (security-auditor, test-runner, debugger, docs-writer)

Each fixture matches the spec's Verification list. Scratch dirs use fixed
`/tmp/plan17-*` paths — NOT shell variables — because each step runs in its
own shell and variables do not survive across steps. Nothing here is
committed. The planted "secret" is a fake value that never enters the repo.
Relay-style prompts keep the parent on sonnet; each dispatched agent runs
on its own pinned model.

**Files:**
- Create (scratch only, outside repo): fixture files under
  `/tmp/plan17-sec`, `/tmp/plan17-dbg`, `/tmp/plan17-doc`

**Interfaces:**
- Consumes: installed agents from Task 10.
- Produces: recorded probe results for the plan-completion markup.

- [ ] **Step 1: security-auditor fixture — planted secret + injection**

```bash
rm -rf /tmp/plan17-sec && mkdir -p /tmp/plan17-sec
cat > /tmp/plan17-sec/app.py <<'EOF'
import subprocess

API_KEY = 'sk-live-9f8e7d6c5b4a3f2e1d0c'

def run_report(user_arg):
    return subprocess.run(f'report-tool --name {user_arg}', shell=True)
EOF
claude -p --model sonnet "Use the Agent tool to dispatch the security-auditor agent to security-review the single file /tmp/plan17-sec/app.py. Relay its full report verbatim. Take no other action."
```

Expected: the report finds BOTH plants with `file:line` — the hardcoded
credential (`app.py:3`) and the shell-injection pattern (`app.py:6`,
`shell=True` with interpolated input) — under Critical/Important headings,
each with remediation, plus a verdict line.

- [ ] **Step 2: test-runner fixture — one real suite from CLAUDE.md**

Uses the llm-wiki suite (stdlib-only, no heavy deps):

```bash
claude -p --model sonnet "Use the Agent tool to dispatch the test-runner agent with exactly this dispatch: working directory /Users/lowell/Projects/agent-skills/skills/llm-wiki/scripts, command: uv run --python 3.13 --with pytest python -m pytest -q. Relay its full report verbatim. Take no other action."
```

Expected: report gives pass/fail/skip counts (180 passed at plan time),
quotes any warnings, and contains no diagnosis. Contract holds: no source
edits, no git mutation.

- [ ] **Step 3: debugger fixture — synthetic failing test, change left uncommitted**

```bash
rm -rf /tmp/plan17-dbg && mkdir -p /tmp/plan17-dbg && cd /tmp/plan17-dbg && git init -q
cat > calc.py <<'EOF'
def add(a, b):
    return a - b
EOF
cat > test_calc.py <<'EOF'
from calc import add


def test_add():
    assert add(2, 3) == 5
EOF
git add -A && git commit -qm 'seed'
claude -p --model sonnet "Use the Agent tool to dispatch the debugger agent on a self-contained failure. Repro: cd /tmp/plan17-dbg && uv run --python 3.13 --with pytest python -m pytest -q — test_add fails. Ask it to fix the bug per its method and relay its full report verbatim. Take no other action."
git -C /tmp/plan17-dbg status --short && git -C /tmp/plan17-dbg log --oneline
```

Expected: `calc.py` now returns `a + b`; the suite passes in the report;
`git status --short` shows ` M calc.py` (uncommitted) and `git log` still
shows exactly one commit (`seed`) — the agent did not commit.

- [ ] **Step 4: docs-writer fixture — small grounded README**

```bash
rm -rf /tmp/plan17-doc && mkdir -p /tmp/plan17-doc
cat > /tmp/plan17-doc/dedupe.py <<'EOF'
import argparse
import sys


def unique_lines(lines):
    seen = set()
    return [ln for ln in lines if not (ln in seen or seen.add(ln))]


def main():
    parser = argparse.ArgumentParser(description='Drop duplicate lines, keeping first occurrence.')
    parser.add_argument('--ignore-case', action='store_true')
    args = parser.parse_args()
    lines = sys.stdin.read().splitlines()
    if args.ignore_case:
        lines = [ln.lower() for ln in lines]
    sys.stdout.write('\n'.join(unique_lines(lines)) + '\n')


if __name__ == '__main__':
    main()
EOF
claude -p --model sonnet "Use the Agent tool to dispatch the docs-writer agent to write /tmp/plan17-doc/README.md documenting the tool in /tmp/plan17-doc/dedupe.py. Relay its full report verbatim. Take no other action."
cat /tmp/plan17-doc/README.md
```

Expected: `README.md` exists and is grounded — it names the real flag
(`--ignore-case`) and real behavior (stdin→stdout, first occurrence kept,
the lowercasing quirk of `--ignore-case`) and invents nothing (any
uncertain claim carries the ⚠ marker per its contract).

- [ ] **Step 5: Clean up scratch dirs**

```bash
rm -rf /tmp/plan17-sec /tmp/plan17-dbg /tmp/plan17-doc
```

---

### Task 12: Command fixture probes (/license-audit, /fix-issue)

**Files:**
- Create (scratch only): one throwaway git repo at `/tmp/plan17-fix` (fixed
  path — plan steps run in separate shells, so no cross-step variables)

**Interfaces:**
- Consumes: installed commands from Task 10.
- Produces: recorded probe results; doubles as command-discovery
  verification (a successful typed invocation IS discovery).

- [ ] **Step 1: /license-audit self-audit on this repo**

```bash
cd /Users/lowell/Projects/agent-skills && claude -p --model sonnet '/license-audit'
```

Expected: Layer 1 runs both build gates (both exit 0); Layer 2 reconciles
cleanly — NOTICE covers every skill (the five new agents and two new
commands fall under the original-works blanket, matching the spec), LICENSE
and LICENSE-superpowers present, Murphy/Martin material correctly flagged
as cited-only, nothing from `build/.scratch/` tracked. Overall verdict:
clean. It edits nothing (`git status --short` unchanged afterward).

- [ ] **Step 2: /fix-issue graceful stop without a GitHub remote**

```bash
rm -rf /tmp/plan17-fix && mkdir -p /tmp/plan17-fix
cd /tmp/plan17-fix && git init -q && git commit -qm init --allow-empty
claude -p --model sonnet '/fix-issue 1'
git -C /tmp/plan17-fix branch --list && git -C /tmp/plan17-fix status --short
```

Expected: the run stops gracefully at step 1, stating the repo has no
GitHub remote (or that `gh` cannot resolve one); no fix branch is created
(`branch --list` shows only the initial branch) and the tree is untouched
(`status --short` empty).

- [ ] **Step 3: Clean up and final gates**

```bash
rm -rf /tmp/plan17-fix
cd /Users/lowell/Projects/agent-skills && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && uv run --python 3.13 python build/check_provenance.py && (cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q)
```

Expected: both gates exit 0; build suite 34 passed.

---

## Completion

After the final task and its review are resolved, run the **Plan Completion
Protocol** (writing-plans § Plan Completion Protocol). Two items are
pre-identified for it — both mandated by the spec's completion note:

1. **Tick the plan-11 deferred item** in `specs/deferred_items.md` — the
   Haiku-pinned `Explore` override (`- [x] … → done in plan 17`).
2. **Append this plan's deferred item**: PreToolUse hooks mechanically
   enforcing the read-only contracts of `security-auditor`, `Explore`, and
   `test-runner` (spec "Out of scope" — contract prose matches the existing
   reviewer precedent; enforcement hooks would be a new mechanism needing
   its own design). Also note the spec's deliberate deferral of a live
   end-to-end `/fix-issue` run against a real GitHub issue to first real
   use — record it in the plan markup, not as a deferred-items entry, since
   it is interactive verification rather than unbuilt work.

Then retire: `git mv` this plan to `specs/plans/completed/` and the spec
`specs/agents-and-commands-expansion.md` to `specs/completed/` (no other
live plan shares it), fixing relative links for the new depth. Finish the
branch via the finishing-a-development-branch skill (precedent: PR merge to
`main`, as with PR #11).

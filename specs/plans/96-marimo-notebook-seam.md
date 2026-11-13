# marimo Notebook Seam, Plan A (the fixes) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop the tech-debt scan and the ruff hooks from misreading or blocking on marimo notebooks, and ship the kit README that a work repo follows to adopt marimo.

**Architecture:** One bash helper in `scan.sh` finds marimo notebooks by content, and two report sections use it. A new `templates/marimo-repo/README.md` carries the ruff ignore. A one-time check runs that ignore against every ruff version the work repos run. The tech-debt skill, `hooks/README.md`, the register, `CLAUDE.md`, `README.md` and `NOTICE` get short additions.

**Tech Stack:** bash (bash 3.2 compatible), rg or grep/find, pytest through `uv run`, ruff and marimo through `uvx` (the one-time check only), TOML.

**Spec:** `specs/marimo-notebook-seam.md` (APPROVED 2026-11-13): sections A1 to A5, Testing (Plan A) and Done when (Plan A).

## Global Constraints

- **Scope.** Plan A only (D1). Do not write the notebook block or `templates/marimo-repo/notebook-block.md`, and do not edit explore-data or recommend-visualization. Those are Plan B.
- **Branch.** The spec and this plan reach `main` first, in a PR of their own from `claude/marimo-notebook-integration-de2d68` (D5). Execution starts only after that PR merges, on a new branch cut from the `main` that holds them, in its own worktree. Commit there. Do not push during execution. How the branch is integrated is decided at the end, by finishing-a-development-branch.
- **Anchors.** Line numbers are lines at `85877be`. Each edit's old text is its match key, not its line number. If an old text no longer matches exactly, stop and ledger it. Live plans 93, 94 and 95 also edit `NOTICE`, in its superpowers part, and plan 93 edits `CLAUDE.md`'s Commands section. This plan's edits to both files sit elsewhere.
- **Public repo** (spec, Constraints). "No plan, record, kit or skill text names a work repo for a fact, and none carries new detail from one: versions, configs, file sizes or file names." The same holds for commit messages, the ledger and task reports. Every fixture name in this plan is made up. Never swap in a name from `/tmp/marimo-probe/`, because some of its folder and file names come from work repos.
- **Leak check.** Build the name list once, outside the repo:

  ```bash
  mkdir -p /tmp/marimo-probe/plan96
  for d in ~/Projects/*/; do [ -d "$d/.git" ] && basename "$d"; done | grep -vx agent-skills \
    | awk '{print; gsub(/-/, "_"); print}' | sort -u > /tmp/marimo-probe/plan96/names.txt
  ```

  Before each commit, run `git diff --cached -U0 | grep '^+' | grep -i -F -f /tmp/marimo-probe/plan96/names.txt`. Expected: no output. Read any hit by hand. A new mention is a leak, so reword it before you commit. Never copy the list into the repo, a commit message, the ledger or a report.
- **Provenance.** Take ideas from Eric Ma's posts and from marimo-pair, never text. Credit Eric Ma by URL and idea only. marimo-pair is Apache-2.0: link to it, and copy nothing.
- **Install dependencies.** No skill text names a `templates/` path, because `install.py` installs skills, not the kit.
- **Style.** Human prose (the kit README, `hooks/README.md`, `NOTICE`, `README.md`, commit messages) follows the always-on plain-English rule. Do not use semicolons. Write one idea in each sentence. Agent-facing text (the tech-debt `SKILL.md` lines) uses the write-with-asd-ste100 skill. Python uses single quotes. `scan.sh` must stay runnable by bash 3.2: no `declare -A` and no `mapfile`.
- **Versions.** No marimo or ruff version in skill text (`versions.py check` reads `skills/`).
- **marimo-pair's contract.** Nothing tells the agent to import `marimo._code_mode` in a cell, or to manage packages outside marimo-pair.
- **Register and lints.** Run `uv run --with pyyaml python build/check_conformance.py` before each commit. The pre-commit hook runs `build/run_commit_lints.sh` on each commit, because `core.hooksPath` is set. If it fails, fix the cause. Never use `--no-verify`.
- **Held citations.** `cli.py lint` prints `STALE` for `hooks/ruff-check.sh` and `skills/subagent-driven-development/SKILL.md`. They are held on purpose (`d778c3e`). Leave them.
- **Commits.** Each commit message ends with the session's `Co-Authored-By` trailer.

## Review Focus

1. A plain helper module under `notebooks/`, with no `app = marimo.App(` line, stays in the untested-modules list. The skip goes by content, never by folder. Pinned in Task 1 by `test_marimo_notebooks_are_not_untested_modules`.
2. A marimo notebook under a nested `notebooks/` folder that is not at the root (`analysis/notebooks/`) is scratch, by designer's call 2. Pinned in Task 1 by `test_marimo_notebook_outside_notebooks_dir_is_scratch`.
3. A repo with no marimo notebooks gets the same untested-modules list as before. An empty notebook list must not filter out every module. Pinned in Task 1 by `test_untested_modules_unchanged_without_notebooks`.
4. A repo whose `pyproject.toml` already has a `[tool.ruff.lint.per-file-ignores]` table must merge the line into it. A second copy of that header is invalid TOML, and ruff stops. Pinned in Task 3's snippet check: config `b` carries an existing table.
5. A repo that keeps its ruff settings in `ruff.toml` needs the table without the `tool.ruff.` prefix. Pinned in Task 3's snippet check: config `r`.

## Decisions

- **D1** (owner, brief, 2026-11-13): Plan A only. Plan B is planned after Plan A merges. Applied in: Global Constraints (Scope).
- **D2** (owner, brief, 2026-11-13): The plan and its work are committed on `claude/marimo-notebook-integration-de2d68` and not pushed. Applied in: Global Constraints (Branch).
- **D3** (owner, plan review, 2026-11-13): "Use 96 (Recommended)", in answer to which id this plan uses after 95 collided with `95-branch-explainer.md`, which was committed and reviewed first. Applied in: the file name and the scratch path `/tmp/marimo-probe/plan96/`.
- **D4** (owner, plan review, 2026-11-13): "Approve it", in answer to "Approve plan 96 as written, with builder's calls C1 to C14?". The plan stands as written. That approves every builder's call, C4, C6, C7, C10 and C11 among them, as plan-level calls, so no spec amendment follows. Applied in: all tasks, Global Constraints.
- **D5** (owner, plan review, 2026-11-13): "But can we PR the spec and plan before execution?", asked after D4. The branch is pushed and the spec and plan go to `main` in their own PR. Execution runs after that PR merges, on a new branch. This replaces D2's "not pushed" for the spec and plan. Applied in: Global Constraints (Branch).

## Builder's calls

These settle the spec's "Left to the builder" items for Plan A, and two gaps the spec leaves. The owner reviews them at plan review.

- **C1.** The detector: a `.py` file with a line that matches the ERE `^app[[:space:]]*=[[:space:]]*marimo\.App\(`. One helper serves both arms and prints paths in the form that `FILES` prints. (Task 1)
- **C2.** The scratch section keeps its title and appends `(.ipynb by name, marimo .py outside notebooks/)`. The untested-modules title does not change. (Task 1)
- **C3.** The register gets a new kind, `kit`, and `claude-md` stays as it is. The kit README is a guide for people, not a loaded `CLAUDE.md`, so `claude-md-size` and that kind's description do not fit it. The new kind takes the four `claude-md` sections that govern text pasted into a `CLAUDE.md`. (Task 3)
- **C4.** The kit README keeps step 4, "Paste the notebook block", as a stub that says the block is not written yet. Plan B replaces the stub's text, so the step numbers hold. (Task 3)
- **C5.** The kit README also gives the `ruff.toml` form of the table, and says to merge the line into an existing table (Review Focus 4 and 5). (Task 3)
- **C6.** The convert steps call marimo through `uvx` (`uvx marimo convert`, `uvx marimo check`), so they work whether or not marimo is a project dependency. The spec writes `marimo convert`. (Task 2)
- **C7.** The scratch bullet also covers the new signal: a marimo `.py` notebook outside `notebooks/` needs no convert. It is moved with `git mv` into `notebooks/` when worth keeping. The spec gives that signal no action. (Task 2)
- **C8.** The binary DELETE vs HARDEN framing stays at `SKILL.md:40`, `:55-57`, `:121-134`, `:166` and `:215`. CONVERT is an outcome of the scratch-notebook bullet only (designer's call 6). `scan.sh:5-6` and `:179` name it for scratch notebooks. (Task 2)
- **C9.** The backlog example gains a new CONVERT row after `:194`, and the `scratchpad.ipynb` row stays. (Task 2)
- **C10.** No micro-test for the tech-debt edit. The spec's Plan A testing names none, and the edit adds a triage option, not a discipline rule. (Task 2)
- **C11.** `README.md`'s folder tree gains a `templates/` line, beside the spec's `CLAUDE.md` clause. (Task 3)
- **C12.** The `NOTICE` paragraph goes after the `runtimes/` paragraph, outside the "original works" list that `check_provenance.py` parses. Plans 93 and 94 edit other parts of `NOTICE`. (Task 3)
- **C13.** The snippet check reads ruff versions from every git repo directly under `~/Projects/`, this repo excluded: the `uv.lock` version, the `ruff-pre-commit` rev and any version that a workflow pins. Extra versions only make the check stricter. It also runs the latest ruff. (Task 3)
- **C14.** In `hooks/README.md`, the marimo note opens "Install into a work repo", and the guard bullet follows the `git fetch` bullet. Only `hooks/README.md` is restamped, as the spec says. The new lines in `CLAUDE.md`, `README.md`, the tech-debt `SKILL.md` and the register state no Claude Code fact, so their citations stand. (Tasks 2 to 4)

## File map

| File | Change | Task |
|---|---|---|
| `skills/tech-debt/scripts/test_scan.py` | 7 tests, a fixture, 2 section prefixes | 1 |
| `skills/tech-debt/scripts/scan.sh` | notebook helper and two sections (Task 1), header comment and closing line (Task 2) | 1, 2 |
| `skills/tech-debt/SKILL.md` | signal row, scratch bullet, backlog row | 2 |
| `templates/marimo-repo/README.md` | new: the kit guide | 3 |
| `build/cc_guide/conformance.toml` | new kind `kit` | 3 |
| `CLAUDE.md`, `README.md` | name `templates/` | 3 |
| `NOTICE` | the kit's paragraph | 3 |
| `specs/plans/96-marimo-notebook-seam.md` | Task 3's snippet-check result line | 3 |
| `hooks/README.md` (and `build/cc_guide/baseline.json` if the restamp changes it) | two additions, restamp | 4 |

---

### Task 1: The marimo detector in `scan.sh`

**Files:**
- Modify: `skills/tech-debt/scripts/test_scan.py` (constants after `:25`, a fixture after `project` at `:69-84`, tests at the end)
- Modify: `skills/tech-debt/scripts/scan.sh` (a helper after `FILES` at `:30-36`, the scratch section at `:100-101`, the untested-modules section at `:168-177`)

**Interfaces:**
- Consumes: `FILES` (`scan.sh:30-36`), which prints `./`-prefixed paths in both arms. The test helpers `git()`, `scan()` and `section()`, and the `project` fixture.
- Produces: `marimo_notebooks`, a bash function with no arguments. It prints each marimo notebook under `.`, one path per line, in the form `FILES` prints. The test constants `SCRATCH = 'Scratch / scratchpad notebooks'` and `UNTESTED = 'Source modules with no obvious test'`.

- [ ] **Step 1: Write the failing tests**

Add after `MIGRATION = 'Migration debt'`:

```python
SCRATCH = 'Scratch / scratchpad notebooks'
UNTESTED = 'Source modules with no obvious test'

MARIMO_NOTEBOOK = '''\
import marimo

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
'''

# Mentions marimo, but its app line is not top-level, so it is a module.
MARIMO_MENTION = '''\
import marimo


def build():
    app = marimo.App()
    return app
'''
```

Add after the `project` fixture:

```python
@pytest.fixture
def notebook_project(tmp_path):
    """A git project with marimo notebooks inside and outside the root notebooks/, plus controls."""
    root = tmp_path / 'nbproject'
    files = {
        'explore_root.py': MARIMO_NOTEBOOK,
        'analysis/notebooks/nested_nb.py': MARIMO_NOTEBOOK.replace('App(width="medium")', 'App()'),
        'scratchpad_nb.py': MARIMO_NOTEBOOK,
        'notebooks/report_nb.py': MARIMO_NOTEBOOK,
        'notebooks/q3/deep dive.py': MARIMO_NOTEBOOK,
        'notebooks/nb_helpers.py': 'def share(x):\n    return x\n',
        'src/uses_marimo.py': MARIMO_MENTION,
        'src/model_core.py': 'def fit():\n    return 1\n',
        'scratchpad.ipynb': '{}',
        'notebooks/Untitled1.ipynb': '{}',
        'notebooks/analysis_record.ipynb': '{}',
    }
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    git(root.parent, 'init', '-q', str(root))
    git(root, 'add', '-A')
    return root
```

Add at the end of the file:

```python
@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_marimo_notebook_outside_notebooks_dir_is_scratch(notebook_project, tmp_path, arm):
    hits = section(scan(notebook_project, arm, tmp_path), SCRATCH)
    assert 'explore_root.py' in hits, hits
    assert 'analysis/notebooks/nested_nb.py' in hits, hits  # only the root notebooks/ holds deliverables


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_marimo_notebook_under_notebooks_dir_is_not_scratch(notebook_project, tmp_path, arm):
    hits = section(scan(notebook_project, arm, tmp_path), SCRATCH)
    for name in ('report_nb.py', 'deep dive.py', 'nb_helpers.py'):
        assert name not in hits, f'{name} was listed:\n{hits}'


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_marimo_notebooks_are_not_untested_modules(notebook_project, tmp_path, arm):
    hits = section(scan(notebook_project, arm, tmp_path), UNTESTED)
    for name in ('explore_root.py', 'nested_nb.py', 'scratchpad_nb.py', 'report_nb.py', 'deep dive.py'):
        assert name not in hits, f'{name} is a notebook, not a module:\n{hits}'
    for name in ('src/model_core.py', 'notebooks/nb_helpers.py'):  # a module stays listed wherever it sits
        assert name in hits, f'{name} was not listed:\n{hits}'


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_notebook_ipynb_name_rule_is_unchanged(notebook_project, tmp_path, arm):
    hits = section(scan(notebook_project, arm, tmp_path), SCRATCH)
    assert 'scratchpad.ipynb' in hits, hits
    assert 'notebooks/Untitled1.ipynb' in hits, hits  # the name rule holds in notebooks/ too
    assert 'analysis_record.ipynb' not in hits, hits


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_marimo_mention_without_app_line_is_not_a_notebook(notebook_project, tmp_path, arm):
    sections = scan(notebook_project, arm, tmp_path)
    assert 'uses_marimo.py' not in section(sections, SCRATCH)
    assert 'src/uses_marimo.py' in section(sections, UNTESTED)


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_scratch_lists_each_notebook_once(notebook_project, tmp_path, arm):
    """scratchpad_nb.py matches the name rule and the marimo rule. The section lists it once."""
    hits = section(scan(notebook_project, arm, tmp_path), SCRATCH)
    assert hits.count('scratchpad_nb.py') == 1, hits


@pytest.mark.parametrize('arm', ['rg', 'grep'])
def test_untested_modules_unchanged_without_notebooks(project, tmp_path, arm):
    """With no notebook in the repo, an empty notebook list must not filter out every module."""
    hits = section(scan(project, arm, tmp_path), UNTESTED)
    assert 'src/signals.py' in hits and 'src/frames.py' in hits, hits
```

- [ ] **Step 2: Run the tests to verify the RED**

Run: `uv run python build/run_suites.py tech-debt -- -k notebook`
Expected: `4 failed, 10 passed`. The 4 failures are `test_marimo_notebook_outside_notebooks_dir_is_scratch` and `test_marimo_notebooks_are_not_untested_modules`, each in both arms. The other five tests are guards. They pass before the change, and each fails against a wrong implementation: one that skips by folder, lists `notebooks/`, drops the `.ipynb` rule, matches a mention, lists a file twice or filters on an empty list. Read each failure: it must be an assertion about a file name, not a fixture error or `command not found`. Planning ran these tests on a scratch copy of `scan.sh` at `85877be`: `4 failed, 10 passed`, as above.

- [ ] **Step 3: Implement `marimo_notebooks` and use it in the two sections of `scan.sh`**

- `marimo_notebooks` goes right after `FILES`. It filters the `.py` paths that `FILES` prints and keeps each file with a line that matches C1's ERE. Keep the paths as `FILES` prints them. Trap: BSD `grep -r` (macOS) drops the `./` that `find` and `rg` print. A list built from `grep -rl` then fails to match `mods` in the grep arm, and the untested skip misses every notebook. A `while read` loop over `FILES | grep '\.py$'`, with `grep -qE` on each file, keeps the form in both arms.
- Call it once, before the scratch section, and reuse the result in both sections.
- New code calls only the tools in `GREP_ARM_TOOLS` (`git grep find sort basename dirname cat tr`) and bash builtins. If it needs another tool, add the tool to that tuple in `test_scan.py` in this commit.
- Scratch section (`:100-101`): append C2's text to the title. Print the union of the name rule's hits (unchanged) and the notebooks whose path does not start with the root `notebooks/` (`^(\./)?notebooks/`), through `sort -u`.
- Untested-modules section (`:168-177`): drop from `mods` every path the helper printed, by whole-line match. With no notebooks, `mods` stays whole.
- The other sections do not change (spec A2.3), and the script stays read-only.

- [ ] **Step 4: Run the tests to verify the GREEN**

Run: `uv run python build/run_suites.py tech-debt -- -k notebook`
Expected: `14 passed`.

Run: `uv run python build/run_suites.py tech-debt`
Expected: every test passes (14 more than before), none skips while `rg` is installed, and the output ends `suite runs passed`.

- [ ] **Step 5: Commit**

Run the leak check and `check_conformance.py` (Global Constraints). Then:

```bash
git add skills/tech-debt/scripts/scan.sh skills/tech-debt/scripts/test_scan.py
git commit -F - <<'EOF'
fix(tech-debt): list marimo notebooks as scratch, never as untested modules

scan.sh found scratch notebooks only by .ipynb names and listed every
marimo notebook as an untested module. A marimo notebook is a .py file
with a top-level app = marimo.App( line. The scratch section now lists
each one outside the root notebooks/ folder. The untested-modules
section skips every one. Seven tests pin the change in both scan arms.

Co-Authored-By: <the session's trailer>
EOF
```

Replace the `Co-Authored-By` placeholder with the session's trailer before you run the commit.

---

### Task 2: The convert outcome in the tech-debt skill

**Files:**
- Modify: `skills/tech-debt/SKILL.md:79` (the "Scratch notebooks" signal row), `:151-153` (the "Scratch notebook beside prod code" bullet), after `:194` (a new backlog row)
- Modify: `skills/tech-debt/scripts/scan.sh:5-6` (header comment), `:179` (closing line)

**Interfaces:**
- Consumes: the scratch section from Task 1, which now lists a marimo `.py` notebook outside `notebooks/`.
- Produces: the CONVERT outcome, which the kit README (Task 3, install step 5) points to by the skill's name. It never names a path.

- [ ] **Step 1: Load the write-with-asd-ste100 skill**

The new `SKILL.md` lines are agent-facing text. Match the file's existing register (short, direct triage lines).

- [ ] **Step 2: Edit the signal row (`:79`)**

The "What you're grepping for" cell keeps its `.ipynb` names and adds a marimo `.py` notebook (a top-level `app = marimo.App(` line) outside `notebooks/`. The Signal and "Why it's debt" cells do not change.

- [ ] **Step 3: Rewrite the scratch bullet (`:151-153`)**

The bullet keeps HARDEN for load-bearing logic (the model imports from it, or its output cannot be reproduced without it) and DELETE for doodles. Between them, it adds CONVERT for an `.ipynb` that is not load-bearing but is worth keeping as an analysis record. CONVERT has four numbered steps (C6):

1. `uvx marimo convert <name>.ipynb -o notebooks/<name>.py`
2. `uvx marimo check notebooks/<name>.py`
3. Fix each cell it reports. A cell of notes that is not Python becomes a markdown cell, or goes.
4. Delete the `.ipynb`.

Last, one sentence for C7: a marimo `.py` notebook outside `notebooks/` needs no convert. Move it with `git mv` into `notebooks/` when it is worth keeping, else DELETE it. The text names no `templates/` path and no marimo version.

- [ ] **Step 4: Add the backlog row after `:194`**

```markdown
| `Untitled3.ipynb` beside `src/` (no dependents, a finding worth keeping) | Reproducibility | Low | S | CONVERT: `uvx marimo convert` into `notebooks/`, `uvx marimo check`, then delete the `.ipynb` |
```

- [ ] **Step 5: Name CONVERT in `scan.sh`'s header comment (`:5-6`) and closing line (`:179`)**

Both keep "DELETE vs HARDEN" and add that a scratch notebook may CONVERT. The closing line becomes:

```bash
printf '\nDone. Each hit is a candidate — triage DELETE vs HARDEN (or CONVERT a scratch notebook) per SKILL.md.\n'
```

- [ ] **Step 6: Run the checks**

Run each command. Expected output follows each one.

- `uv run --with pyyaml python build/check_frontmatter.py`: passes.
- `uv run python build/check_snippets.py skills/`: passes.
- `uv run python build/check_links.py`: passes.
- `(cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies)`: passes.
- `git grep -n 'templates/' -- skills/`: no output.
- `uv run python build/versions.py check`: `versions ok`.
- `uv run python build/run_suites.py tech-debt`: `suite runs passed`.

- [ ] **Step 7: Commit**

Run the leak check and `check_conformance.py`. Then:

```bash
git add skills/tech-debt/SKILL.md skills/tech-debt/scripts/scan.sh
git commit -F - <<'EOF'
feat(tech-debt): add a convert outcome for scratch notebooks

A scratch .ipynb that holds no load-bearing logic but is worth keeping
as an analysis record now has a third outcome beside HARDEN and DELETE.
CONVERT turns it into a marimo notebook in notebooks/ and checks it.
A marimo notebook outside notebooks/ moves there when it is worth keeping.

Co-Authored-By: <the session's trailer>
EOF
```

Replace the `Co-Authored-By` placeholder with the session's trailer before you run the commit.

---

### Task 3: The marimo-repo kit and its bookkeeping

**Files:**
- Create: `templates/marimo-repo/README.md`
- Modify: `build/cc_guide/conformance.toml` (a new kind after `[kinds.skill-bundle]` at `:103-106`)
- Modify: `CLAUDE.md:8` (the sibling-folders sentence)
- Modify: `README.md:33-42` (the folder tree)
- Modify: `NOTICE` (a paragraph after the `runtimes/` paragraph that ends `:21` "…MIT license.")
- Modify: `specs/plans/96-marimo-notebook-seam.md` (Step 4's result line)

**Interfaces:**
- Consumes: the CONVERT outcome (Task 2), named as "the tech-debt skill's convert outcome".
- Produces: the heading `## The ruff ignore` in `templates/marimo-repo/README.md`, which Task 4 links as `../templates/marimo-repo/README.md#the-ruff-ignore`.

- [ ] **Step 1: Build the snippet check outside the repo**

Create `/tmp/marimo-probe/plan96/{b,q,r}/`. Each holds `notebooks/probe_nb.py` and `scratch/probe_nb.py`, two copies of this notebook. Each display line trips B018, marimo's three double-quoted lines trip Q000 under single quotes, and the import cell trips I001:

```python
import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Hypothesis: the March drop is concentrated in three states.
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import polars as pl
    import altair as alt
    return alt, mo, pl


@app.cell
def by_state(alt, mo, pl):
    df = pl.DataFrame({'state': ['CA', 'TX', 'NY'], 'emp': [10, 20, 30]})
    chart = mo.ui.altair_chart(alt.Chart(df).mark_bar().encode(x='state', y='emp'))
    chart
    return


if __name__ == "__main__":
    app.run()
```

The three configs. `b` already has a table, so the kit's line is merged into it (Review Focus 4). `r` is the `ruff.toml` form (Review Focus 5).

```toml
# b/pyproject.toml
[tool.ruff.lint]
select = ['E', 'F', 'I', 'B']

[tool.ruff.lint.per-file-ignores]
'tests/**' = ['B011']
'notebooks/**' = ['B018']
```

```toml
# q/pyproject.toml
[tool.ruff.lint]
select = ['E', 'F', 'I', 'Q']

[tool.ruff.lint.flake8-quotes]
inline-quotes = 'single'

[tool.ruff.lint.per-file-ignores]
'notebooks/**' = ['Q000']
```

```toml
# r/ruff.toml
[lint]
select = ['E', 'F', 'I', 'B']

[lint.per-file-ignores]
'notebooks/**' = ['B018']
```

Run: `cd /tmp/marimo-probe/plan96/b && uvx marimo check notebooks/probe_nb.py`
Expected: exit 0. The fixture is a valid marimo notebook.

- [ ] **Step 2: Collect the ruff versions the work repos run (C13)**

```bash
for d in ~/Projects/*/; do
  [ "$(basename "$d")" = agent-skills ] && continue
  awk '/^\[\[package\]\]/{p=0} /^name = "ruff"$/{p=1} p && /^version = /{gsub(/"/, "", $3); print $3}' "$d/uv.lock" 2>/dev/null
  grep -A2 'ruff-pre-commit' "$d/.pre-commit-config.yaml" 2>/dev/null | sed -n 's/.*rev: *v\{0,1\}//p'
done | sort -u > /tmp/marimo-probe/plan96/versions.txt
cat /tmp/marimo-probe/plan96/versions.txt
grep -rn 'ruff' ~/Projects/*/.github/workflows/ 2>/dev/null | grep -v '/Projects/agent-skills/'
```

Expected: one bare version per line in `versions.txt`. Read the workflow lines by hand, and add any version they pin to `versions.txt`. If a line in `versions.txt` is not a bare version, read that file and fix the line. Report only how many versions you found. No version and no repo name goes into a report, the ledger or the repo.

- [ ] **Step 3: Run the snippet check at each version**

```bash
cd /tmp/marimo-probe/plan96
for v in $(cat versions.txt) latest; do
  for d in b q r; do
    echo "== ruff $v, config $d"
    (cd "$d" && uvx "ruff@$v" check --no-cache --output-format concise .)
  done
done
```

Expected, for every version and config:
- Every finding in `notebooks/probe_nb.py` is I001.
- `scratch/probe_nb.py` shows I001 and B018 (configs `b` and `r`), or I001 and three Q000 findings (config `q`).

`scratch/` is the control: it shows that the fixture trips the rules that the ignore removes. Any other code in `notebooks/`, or a control without B018 or Q000, fails the check. Then stop and bring the output to the owner, with versions and repo names kept out of the repo.

- [ ] **Step 4: Record the result in this plan**

Under this step, add one line, with no version number and no repo name:

`> Result (<YYYY-MM-DD>): at every ruff version the work repos run, and at the latest, all three configs left I001 and nothing else in notebooks/.`

- [ ] **Step 5: Write `templates/marimo-repo/README.md`**

Plain English for people. It names no work repo. Headings and content:

- `# marimo repo kit`. What the kit is for: a work repo that adopts marimo notebooks. marimo-pair (`https://github.com/marimo-team/marimo-pair`) drives live notebooks. This kit adds the repo-side setup. It is read here and copied by hand. `install.py` does not install it.
- `## Install`, five numbered steps:
  1. Create `notebooks/` at the repo root. Root only, because ruff reads the ignore's `notebooks/**` pattern from the folder that holds the ruff config, which is the repo root. A marimo notebook elsewhere counts as scratch.
  2. Install marimo-pair for the repo. Link to its README for the commands, and copy none of them.
  3. Add the ruff ignore (link to the next section).
  4. Paste the notebook block. The block is not written yet, so skip this step for now (C4).
  5. Convert each scratch `.ipynb` by the tech-debt skill's convert outcome.
- `## The ruff ignore`. This TOML, exactly:

  ```toml
  [tool.ruff.lint.per-file-ignores]
  'notebooks/**' = ['B018']
  ```

  Then, as short paragraphs or bullets:
  - Add `B018` when the repo selects the B rules. marimo shows a cell's last expression as output, so ruff reads each display line as a useless expression.
  - Add `Q000` when the repo selects the Q rules with single inline quotes. marimo writes three lines in double quotes (`__generated_with = "…"`, `app = marimo.App(…)` and `if __name__ == "__main__":`) and writes them back on every save, so a fix never holds.
  - Every other rule stays on, I001 included. The agent fixes those findings through marimo-pair.
  - The ignore matters wherever ruff runs over `notebooks/`: the Stop hook (`ruff-check.sh`, link `../../hooks/README.md`), pre-commit and CI. A pre-commit hook can pin a ruff version other than the lockfile's.
  - If the table already exists, merge the line into it. A second copy of the header is invalid TOML (C5).
  - In `ruff.toml` or `.ruff.toml`, the table is `[lint.per-file-ignores]` (C5).
  - Write the line in the repo's quote style.
- `## During a live session`. Fix lint through marimo-pair, never by editing the file. marimo-pair changes cells through the running notebook server. A `Write` or `Edit` on the file goes around it.
- `## Credits`. The kit is an original work by Lowell Mason under the MIT license (link `../../NOTICE`). It takes ideas, and no text, from Eric Ma's "Agent-assisted data science with marimo" (`https://ericmjl.github.io/blog/2026/10/14/agent-assisted-data-science-with-marimo/`) and "How to do agentic data science" (`https://ericmjl.github.io/blog/2026/2/1/how-to-do-agentic-data-science/`). It pairs with marimo-pair (Apache-2.0), links to it and copies none of its text.

- [ ] **Step 6: Add the `kit` kind to the register (C3)**

After `[kinds.skill-bundle]`:

```toml
[kinds.kit]
description = 'Kits that a work repo copies by hand, such as templates/marimo-repo/. Text that a kit pastes into a CLAUDE.md is CLAUDE.md content.'
globs = ['templates/marimo-repo/**']
sections = ['rules.claude-md', 'rules.hierarchy', 'context.overview', 'mechanisms.overview']
```

- [ ] **Step 7: Name `templates/` in `CLAUDE.md` and `README.md` (C11)**

In `CLAUDE.md:8`, the sibling list "…, `hooks/` (Claude Code hook templates and its read-only-agent guard), and `rules/` (Claude Code path-scoped rules)." becomes "…, `hooks/` (Claude Code hook templates and its read-only-agent guard), `rules/` (Claude Code path-scoped rules), and `templates/` (kits that a work repo copies by hand, which `install.py` does not install)."

In `README.md`'s tree, after the `rules/` line:

```text
├── templates/   # kits a work repo copies by hand (templates/marimo-repo/), never installed
```

- [ ] **Step 8: Add the `NOTICE` paragraph (C12)**

After the paragraph that starts "Files under runtimes/ are mechanically generated", and before `bayesian-workflow/`, with one blank line on each side:

```text
Files under templates/marimo-repo/ are a kit that a work repo copies by hand
when it adopts marimo notebooks (https://marimo.io). The kit is an original
work by Lowell Mason under this repository's MIT license. It takes ideas,
and no text, from two posts by Eric Ma: "Agent-assisted data science with
marimo"
(https://ericmjl.github.io/blog/2026/10/14/agent-assisted-data-science-with-marimo/)
and "How to do agentic data science"
(https://ericmjl.github.io/blog/2026/2/1/how-to-do-agentic-data-science/).
The kit pairs with marimo-pair (https://github.com/marimo-team/marimo-pair,
Apache-2.0), which drives live notebooks. It links to marimo-pair and copies
none of its text.
```

- [ ] **Step 9: Run the checks**

- `uv run --with pyyaml python build/check_conformance.py`: passes. The lint reads untracked files too, so the new README falls under the `kit` kind before it is staged.
- `uv run python build/check_provenance.py`: passes. The originals list is unchanged.
- `uv run python build/cc_guide/cli.py lint`: no `STALE` line beyond the two held files.
- `(cd templates/marimo-repo && for p in ../../hooks/README.md ../../NOTICE; do test -e "$p" || echo "missing $p"; done)`: no output.
- `wc -l CLAUDE.md`: under 200 lines.

- [ ] **Step 10: Commit**

Run the leak check. Then:

```bash
git add templates/marimo-repo/README.md build/cc_guide/conformance.toml CLAUDE.md README.md NOTICE specs/plans/96-marimo-notebook-seam.md
git commit -F - <<'EOF'
feat(templates): add the marimo-repo kit with its ruff ignore

templates/marimo-repo/README.md tells a work repo how to adopt marimo
notebooks: where notebooks live, the marimo-pair install, the ruff
ignore and the convert path for scratch notebooks. The ignore was
checked at every ruff version the work repos run: only I001 remained.
The register gains a kit kind. CLAUDE.md, README.md and NOTICE name
the new folder.

Co-Authored-By: <the session's trailer>
EOF
```

Replace the `Co-Authored-By` placeholder with the session's trailer before you run the commit.

---

### Task 4: The two `hooks/README.md` additions

**Files:**
- Modify: `hooks/README.md:44-46` (the start of "Install into a work repo"), after `:389` (the end of the `git fetch` bullet in the guard's "Limitations (by design)")
- Modify, if the restamp changes them: `hooks/README.md:1`, `build/cc_guide/baseline.json`

**Interfaces:**
- Consumes: `../templates/marimo-repo/README.md#the-ruff-ignore` (Task 3).
- Produces: nothing later tasks use.

- [ ] **Step 1: Add the marimo note to "Install into a work repo"**

Old text, the match key:

```markdown
## Install into a work repo

From the target repo
```

Between the heading and "From the target repo", add one short paragraph. In a repo with marimo notebooks, add the ruff ignore from [the marimo-repo kit](../templates/marimo-repo/README.md#the-ruff-ignore) before you install `ruff-check.sh`. Without it, the Stop hook blocks every turn while a notebook has a display line (B018) or, under single-quote rules, marimo's own double-quoted lines (Q000).

- [ ] **Step 2: Add the guard bullet to the read-only guard's "Limitations (by design)"**

Old text, the match key, the end of the `git fetch` bullet:

```markdown
  this as an oversight; if a real case appears, flipping it is one line.
```

After it, a new bullet in the list's style. **marimo-pair's `bash …/execute-code.sh` passes the guard.** That script can create, edit and run cells in a live notebook. This is accepted, because no read-only agent has a reason to drive a live notebook, so the guard adds no rule for it.

- [ ] **Step 3: Review and restamp**

Check the two additions against the file's cited sections (line 1). Neither states a Claude Code fact.

Run: `uv run python build/cc_guide/cli.py baseline cite hooks/README.md`
Expected: `stamped hooks/README.md @<version>`. If the version is newer than 2.1.323, line 1 and `build/cc_guide/baseline.json` change. Commit both.

Run: `uv run python build/cc_guide/cli.py lint`
Expected: no `STALE` line names `hooks/README.md`.

- [ ] **Step 4: Run the checks**

- `grep -c '^## The ruff ignore$' templates/marimo-repo/README.md`: `1`. The link's anchor exists.
- `uv run --with pyyaml python build/check_conformance.py`: passes.
- `bash build/run_commit_lints.sh`: every lint passes.

- [ ] **Step 5: Commit**

Run the leak check. Then:

```bash
git add hooks/README.md build/cc_guide/baseline.json
git commit -F - <<'EOF'
docs(hooks): note the marimo ruff ignore and the execute-code.sh gap

A repo with marimo notebooks needs the kit's ruff ignore before it
installs ruff-check.sh, or the Stop hook blocks every turn. The
read-only guard lets marimo-pair's execute-code.sh through. This is
accepted, because no read-only agent drives a live notebook.

Co-Authored-By: <the session's trailer>
EOF
```

Replace the `Co-Authored-By` placeholder with the session's trailer before you run the commit.

`git add` of an unchanged `baseline.json` stages nothing, which is correct.

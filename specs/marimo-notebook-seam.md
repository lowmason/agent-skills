# marimo notebooks: the seam with this repo's skills, hooks and rules — Design Spec

**Status:** APPROVED (2026-11-13). The owner approved this file, its designer's calls included, on 2026-11-13. The
question was "Do you approve the spec, with its designer's calls?", and the owner answered "Approve it".

The design came from a brainstorming session on 2026-11-12 and 2026-11-13. A builder check read the draft, and the
owner answered its four open questions (D6 to D9). Text marked *(designer's call)* is the designer's choice, and
"Designer's calls" lists each one. The owner's approval of this file approves them. Line numbers are as of `af378ac`,
the `main` commit this design read. All probes ran on throwaway copies under `/tmp/marimo-probe/`. No work repo was
changed.

This repository is public, and the work repos are private. So this file states facts about the work repos only at
the level of detail the shipped kit needs, and names no repo for a fact (Constraints).

> **For agentic workers:** plan from this file with the writing-plans skill. It yields two plans, in order:
> Plan A (the fixes) and Plan B (the additions). Start Plan B after Plan A merges.

## Intent

The owner is adopting [marimo](https://marimo.io) for notebook work. A marimo notebook is a plain `.py` file. The
marimo team's [marimo-pair](https://github.com/marimo-team/marimo-pair) (Apache-2.0) teaches an agent to drive a
live notebook. The owner installs it per notebook repo. So this repo writes **no marimo skill**.

This spec designs the seam between marimo and this repo. It has two halves:

1. **Fixes.** Parts of this repo misread a marimo notebook or block on it. They must stop doing so.
2. **Additions.** This repo adds what marimo-pair does not know: the owner's pacing for exploration, the owner's
   notebook conventions and the owner's Polars-first style.

**Why now.** `specs/completed/skill-intake-review-2026-08-26.md` (line 265) held the `marimo-notebook` skill until
marimo was adopted. Adoption has happened. That skill is still not the answer: its examples are pandas idioms, and
marimo-pair covers the driving.

**Sources.** Eric Ma, [Agent-assisted data science with marimo](https://ericmjl.github.io/blog/2026/10/14/agent-assisted-data-science-with-marimo/)
(prose before and after each code cell, named cells, hidden code). Eric Ma,
[How to do agentic data science](https://ericmjl.github.io/blog/2026/2/1/how-to-do-agentic-data-science/), lesson 10
(the agent follows the human's curiosity one question at a time). The marimo-pair repo, read at its `main` on
2026-11-12. This repo takes ideas from these sources, never their text (Constraints).

## Current state (recon, 2026-11-12)

| # | Finding | Evidence |
|---|---|---|
| F1 | During a live session, marimo-pair forbids `Write`, `Edit` and `NotebookEdit` on the notebook file. It changes cells through `bash …/scripts/execute-code.sh`, which posts code to the server's HTTP API, where `marimo._code_mode` applies it. So a `PostToolUse(Write\|Edit)` hook and a `paths:` rule never fire on live notebook work. | marimo-pair `SKILL.md`, "Prefer `cm`-Managed Changes" |
| F2 | ruff flags three rules on a marimo notebook. **B018** ("useless expression") flags each display line, because a marimo cell shows its last expression as output. **Q000** ("double quotes found") flags the three lines marimo writes: `__generated_with = "…"`, `app = marimo.App(…)` and `if __name__ == "__main__":`. **I001** ("unsorted imports") flags an unsorted import cell. | Probe at the latest ruff and two older releases, with one config that selects B and one that selects Q with single inline quotes |
| F3 | marimo writes its three lines back in double quotes on every save. A Q000 fix therefore never holds. | Round trip through marimo 0.25.2's serializer (`generate_filecontents_from_ir`): only those three lines changed |
| F4 | `ruff check --fix` and `ruff format` leave a notebook that `marimo check` accepts. | Probe |
| F5 | `[tool.ruff.lint.per-file-ignores]` with `'notebooks/**'` set to B018 (B config) or Q000 (Q config) leaves only I001. I001 is a safe fix the agent can make through marimo-pair. | Probe at the versions in F2 |
| F6 | `hooks/ruff-check.sh` runs `ruff check .` with no `--fix` and blocks the turn on any finding. Once installed in a notebook repo, it blocks every turn while a notebook shows F2's findings. Any other ruff run that covers `notebooks/`, such as a pre-commit hook, fails the same way. A pre-commit hook can pin a ruff version other than the lockfile's. | `hooks/ruff-check.sh`; probe |
| F7 | pytest runs `test_` cells from a notebook only when the notebook is named on the command line or its file name matches `test_*.py`. The work repos' pytest settings point `testpaths` at folders that exclude a root `notebooks/`, so nothing is collected by accident. | marimo docs, "Testing with pytest"; probe (2 tests passed on the explicit path, none on bare `pytest`) |
| F8 | In marimo, `mo.ui.altair_chart` returns a selection to Python as a dataframe (Polars included). `mo.ui.plotly` and `mo.ui.matplotlib` also give reactive selections. marimo raises Altair's 5,000-row cap to 20,000 rows, and `mo.ui.altair_chart` switches to the `marimo_csv` transformer, which the docs say handles more than 400,000 rows. | docs.marimo.io, `api/plotting` |
| F9 | `hooks/uv-guard.sh` passes marimo-pair's three command shapes (`discover-servers.sh`, `execute-code.sh -c …` and `execute-code.sh - <<'PY'`). `hooks/readonly-agent-guard.py` lets `bash …/execute-code.sh` through for a read-only agent, though that script can create, edit and run cells. A `rm -f` control is denied, so the guard works. | Run with the hook payload on stdin |
| F10 | `marimo convert` works on copies of the three scratch notebooks that `skill-intake-review` counted. Two results pass `marimo check`. One has a cell of notes that is not Python. | Probe, one subdirectory per notebook; nothing executed |
| F11 | `rules/clean-code-python.md` loads only where a copy sits in a repo's `.claude/rules/`, and only on `.py` reads, writes and edits. By F1 it never loads on live notebook work. | The rule's `paths:` frontmatter; F1 |
| F12 | Codex reads only `AGENTS.md` and has no import syntax. Its default 32 KiB limit covers the whole instruction chain, the global `~/.codex/AGENTS.md` included. The work repos keep `CLAUDE.md` and `AGENTS.md` as separate files, and some of their `AGENTS.md` files are already near or past the limit. Whether Codex then truncates the chain or drops a file is not checked. | `specs/guides/codex-customization-guide.md` lines 263–276; `wc -c` |
| F13 | marimo-pair's `create_cell` defaults to `hide_code=True` and takes `name=`. Its reference calls cell names "low priority unless the user asks", and warns that a name on a markdown cell shows a header that is normally hidden. Its examples use pandas (`pd.read_csv`). | marimo-pair `SKILL.md`; `reference/notebook-improvements.md` |
| F14 | `skills/tech-debt/scripts/scan.sh:100-101` finds scratch notebooks only by `.ipynb` names. Its "Source modules with no obvious test" section (`:168-177`) would list each marimo notebook as an untested module. | Read |

## Owner decisions

From the brainstorming conversation (2026-11-12):

- **D1.** No marimo skill (the request).
- **D2.** Deliverable notebooks live in a `notebooks/` folder. A marimo notebook elsewhere is scratch. (Picked over
  content detection anywhere.)
- **D3.** The pacing loop holds in every notebook session, not only after a profile. (Picked over "only after a
  profile". D6 narrows "session" to exploration.)
- **D4.** The prose after a view holds facts from the agent, then the verdict from the owner in the owner's words.
  (Picked over "the agent drafts, the owner edits".)
- **D5.** The notebook block ships by pasting it into both `CLAUDE.md` and `AGENTS.md`, near the top (Approaches,
  option 1).

From the builder check's questions (2026-11-13):

- **D6.** The loop covers exploration: sessions that test a hypothesis with a view. Converting a scratch `.ipynb`,
  fixing lint, refactoring and tidying a finished notebook run normally, outside the loop. (Picked over "every
  notebook session, tidying included".)
- **D7.** When the owner asks outright for several views or a model at once, the request wins. The loop is the
  agent's default when the owner has not said otherwise. (Picked over "still one view per turn".)
- **D8.** The facts are numbers only. The agent writes "three states hold 62%". Whether that meets the hypothesis's
  stated outcome is part of the owner's verdict. (Picked over "numbers plus met or not met".)
- **D9.** If the micro-test's no-guidance control already paces itself, the loop text still ships, in the shortest
  wording that tests clean. A short test does not show that pacing holds in long sessions, and the loop is the
  owner's decision. (Picked over "drop what the control already does".) This sets aside writing-skills' rule that a
  control with no failure means no guidance, for this block only.

## Goals, non-goals and anti-goals

**Goals**

1. No ruff run (the Stop hook, pre-commit or CI) fails on a marimo notebook in `notebooks/` for B018, or for Q000 on
   the lines marimo writes. Every other rule still applies there.
2. The tech-debt scan lists a marimo notebook outside `notebooks/` as scratch. It never lists a marimo notebook as an
   untested module. Its source scans still cover notebooks.
3. tech-debt documents a conversion path from a scratch `.ipynb` to a marimo notebook.
4. In every exploration session (D6), the agent follows the loop (Design, B1).
5. Notebook code follows the owner's style: Polars first, named code cells and hidden code.
6. In a marimo notebook, recommend-visualization routes interactive charts to Altair through `mo.ui.altair_chart`.

**Non-goals**

- A marimo skill, or any text copied from marimo-pair.
- Changes to `hooks/ruff-fix.sh`, `hooks/ruff-check.sh` or `hooks/uv-guard.sh`.
- A read-only guard rule for `execute-code.sh`, and allow-list entries for marimo-pair's two scripts.
- Changes to develop-testing-strategy (F7).
- An `install.py` target for the kit (Approaches, option 3).

**Anti-goals** (a failure even if it works)

- In an exploration session, the agent builds a second view, fits a model or writes a verdict before the owner's
  read, when the owner did not ask for more (D7).
- The facts cell says whether the hypothesis held (D8).
- An ignore wider than F2 needs, such as excluding `notebooks/` from ruff.
- A convention that fights marimo's own file format, such as single quotes on the three lines marimo writes.
- A pandas idiom in any example.
- The agent uses `Write` or `Edit` on a notebook file during a live session, for any reason, lint fixes included.

## Approaches

How the notebook block reaches the agent, given D3 (every exploration session) and F1 (no `paths:` rule fires on
live work):

1. **Paste the block into both `CLAUDE.md` and `AGENTS.md`, near the top.** *(Picked, D5.)* Both runtimes load it at
   the start of every session. Placed near the top, it stays inside Codex's 32 KiB limit (F12). Cost: two copies per
   repo. Marker comments make each update a replacement of one known span.
2. **One conventions file in `notebooks/`, imported.** `CLAUDE.md` loads it with an `@notebooks/…` line at launch.
   Codex has no imports, so `AGENTS.md` carries only a pointer to the file. One copy per repo, but the loop holds
   reliably only in Claude Code. Rejected: it fails D3 in Codex.
3. **An `install.py` target** that writes the block into each repo and merges the ruff ignore. One rerun updates every
   repo. Rejected: `hooks/README.md` chose `cp` over links on purpose, so that a template change cannot alter every
   repo silently.

Rejected earlier in the session:

- **A `rules/` file with `paths: 'notebooks/**'`.** It never loads on live work (F1), and Codex has no `paths:` rules.
- **A notebook-conventions skill.** A skill loads when its description matches the task, not in every session (D3).
  It also comes close to the marimo skill that D1 rules out.
- **Detecting notebooks by content anywhere.** D2 chose the folder. With the folder, a path pattern in ruff's config
  does the work and no hook changes.

## Design

### Plan A — the fixes

**A1. The kit and its ruff ignore.** Create `templates/marimo-repo/README.md` *(designer's call: the path)*. It is a
human-facing guide, like the install section of `hooks/README.md`. It names no work repo. It covers:

1. What the kit is for: a work repo that adopts marimo.
2. Install steps, numbered:
   1. Create `notebooks/` at the repo root *(designer's call: root only, to match ruff's root-relative pattern)*.
   2. Install marimo-pair for the repo. Link to its README for the commands. Do not copy them.
   3. Add the ruff ignore (below).
   4. Paste the notebook block (Plan B adds it).
   5. Convert scratch `.ipynb` files by the tech-debt path (A3).
3. The ruff ignore, as a TOML snippet in the repo's quote style:

   ```toml
   [tool.ruff.lint.per-file-ignores]
   'notebooks/**' = ['B018']
   ```

   Add `B018` when the repo selects the B rules. Add `Q000` when it selects Q with single inline quotes. Give the
   reason for each, from F2 and F3. Say plainly that every other rule stays on, I001 included, and that the agent
   fixes those through marimo-pair. Say that the ignore matters wherever ruff runs over `notebooks/`: the Stop hook,
   pre-commit and CI (F6). If the repo already has a `per-file-ignores` table, merge the line into it.
4. The live-session rule: during a session, fix lint through marimo-pair, never by editing the file (F1).
5. Credits (Constraints).

**A2. `skills/tech-debt/scripts/scan.sh`.** Tests first (Testing). Three changes:

1. The scratch section (`:100-101`) also lists each marimo notebook that is not under the root `notebooks/`. A marimo
   notebook is a `.py` file with a top-level `app = marimo.App(` line *(designer's call: the line marimo writes in
   every notebook, F2)*. The `.ipynb` name rule stays as it is, in every folder, `notebooks/` included.
2. The untested-modules section (`:168-177`) skips every marimo notebook, wherever it is. A notebook is not a module.
3. The source scans do not change. A hardcoded `/Users/` path or a pandas import in a notebook is still debt.

The script stays read-only. Each changed section works in both arms (rg, and grep/find).

**A3. `skills/tech-debt/SKILL.md`.** Two edits:

- The "Scratch notebooks" row in the signal table (`:79`) adds a marimo `.py` notebook outside `notebooks/`.
- The triage bullet "Scratch notebook beside prod code" (`:151-153`) gains a third outcome beside HARDEN and DELETE:
  **convert**, for a notebook worth keeping as an analysis record. The steps:
  1. Choose `notebooks/<name>.py` as the target. If that file exists, pick another name, because `marimo convert`
     overwrites it without asking.
  2. Run `marimo convert <name>.ipynb -o notebooks/<name>.py`.
  3. Run `marimo check` on the result. Fix each cell it reports. A cell of notes that is not Python becomes a
     markdown cell or goes (F10).
  4. Run the new notebook and compare its outputs with the outputs saved in the `.ipynb`. `marimo convert` drops
     saved outputs, and `marimo check` runs no cell.
  5. Delete the `.ipynb` only when the outputs match. Otherwise keep it, and log the gap as a backlog row.

  *(Steps amended: owner, plan 96, 2026-11-13.)*

  HARDEN (extract into a module) stays the outcome for load-bearing logic. The example backlog row (`:194`) may show
  the new outcome *(builder's call)*.

**A4. `hooks/README.md`.** Two short additions:

- Under "Project tooling hooks": in a repo with marimo notebooks, add the ruff ignore from
  `templates/marimo-repo/README.md` before installing `ruff-check.sh`. Without it, the Stop hook blocks every turn
  (F6).
- In the read-only guard's limitations: `bash …/execute-code.sh` from marimo-pair passes the guard, and it can create,
  edit and run cells in a live notebook (F9). This is accepted, because no read-only agent has a reason to drive a
  live notebook *(designer's call: document, do not add a rule)*.

The file carries a `cc-guide:` citation comment, so restamp it after review (`build/CLAUDE.md`).

**A5. Repo bookkeeping.**

- Root `CLAUDE.md`, "What this repo is", names the new top-level `templates/` folder in one clause.
- `build/cc_guide/conformance.toml` covers `templates/marimo-repo/**`, by a new kind or by extending one
  *(builder's call)*. The block is CLAUDE.md content, so the `claude-md` kind's sections apply to it.
- `NOTICE` gains a short paragraph: `templates/marimo-repo/` is an original work by Lowell Mason under the MIT
  license. It credits Eric Ma's two posts by URL and idea only, and names marimo-pair as the tool it pairs with,
  taking none of its text.

### Plan B — the additions

**B0. Check Codex first.** Before the paste step ships, check how Codex handles an instruction chain past its limit:
does it truncate the chain or drop a file? A scratch `AGENTS.md` past 32 KiB, with a sentinel line at the top and one
at the end, shows which. If Codex truncates, B1's placement rule holds. If it drops the file, stop and bring it to
the owner, because D5's placement then does not help an oversized file.

**B1. The notebook block.** Create `templates/marimo-repo/notebook-block.md` *(designer's call: the name)*. The block
sits between two marker comments, `<!-- marimo-repo:start -->` and `<!-- marimo-repo:end -->` *(designer's call)*.
It is agent-facing text, so write it with the write-with-asd-ste100 skill. Keep it under 2,500 bytes
*(designer's call: it goes near the top of files that Codex limits to 32 KiB)*. It covers, in this order:

1. **Scope.** Notebooks are marimo notebooks in `notebooks/`. marimo-pair drives a live session. During a session,
   change cells only through marimo-pair, lint fixes included. Never use `Write` or `Edit` on the file then. The loop
   (part 2) applies to exploration: testing a hypothesis with a view (D6). Converting, fixing lint, refactoring and
   tidying run normally.
2. **The loop.** In an exploration session:
   1. The owner names a hunch, or asks for candidates and picks one.
   2. The agent restates it as a hypothesis with an observable outcome, such as "if the March drop is concentrated,
      three states hold more than half of it."
   3. In the same turn, the agent builds one view in one named code cell, runs it, writes the facts cell (part 3)
      and ends its turn *(designer's call: no stop between the restatement and the view; the owner corrects the
      restatement at the read)*.
   4. The owner reads the view and gives a verdict.
   5. The owner picks the next hypothesis or stops.

   Until the owner's verdict, the agent does not build a second view, fit a model or state a conclusion. An explicit
   request for more from the owner overrides this (D7).
3. **Prose around each code cell** (D4, D8). The markdown cell before holds the hypothesis and its observable
   outcome. The markdown cell after holds the numbers the view shows, such as counts, shares and ranges. It does not
   say whether the outcome was met. The agent adds the owner's verdict, in the owner's words, only after the owner
   gives it.
4. **Cells** (F13). Name each code cell for what it shows (`march_drop_by_state`). Leave markdown cells unnamed. Keep
   `hide_code=True`.
5. **Polars.** Polars, not pandas. Method-style expressions (`pl.col('x').gt(0)`). Scan lazily, and let each view
   cell collect its own small frame. Single quotes in cell code. The three lines marimo writes stay as marimo writes
   them.
6. **Charts.** Interactive charts use `mo.ui.altair_chart`. The recommend-visualization skill picks the chart.

The kit README's paste step (A1, step 2.4) says:

- Paste the block into both `CLAUDE.md` and `AGENTS.md`, near the top, inside Codex's 32 KiB limit.
- If a repo's `AGENTS.md` is near or past that limit (F12), put the block before any other section.
- To update, replace the span between the markers in each file.

**B2. explore-data's marimo branch.** In `skills/explore-data/SKILL.md`, "Output" (`:234-252`): when the work goes on
in a marimo notebook, the "Suggested next steps" become candidate hypotheses, each with an observable outcome. The
agent offers them, stops and lets the owner pick. From there the repo's notebook block governs. The text names no
`templates/` path, because the kit is not installed with the skill (Constraints). It must read correctly in all
three runtimes.

**B3. recommend-visualization.** In `skills/recommend-visualization/SKILL.md`, the Phase 2 table (`:84-86`) gains a
row: interactive charts inside a marimo notebook go to Altair through `mo.ui.altair_chart`. A selection reaches
Python as a dataframe (`chart.value`). plotly keeps the chart types Altair lacks, such as choropleths and Sankey
diagrams. `references/altair.md` gains a note on the row cap in marimo (F8). Any example uses Polars.

**B4. Credit.** `NOTICE`, under explore-data, credits the loop's idea to Eric Ma's lesson 10, by URL and idea only.

## Testing

**Plan A.**

- `skills/tech-debt/scripts/test_scan.py` first, red then green, in both arms. Cases:
  - a marimo notebook at the root is listed as scratch;
  - a marimo notebook under `notebooks/` is not listed;
  - a marimo notebook in any folder is missing from the untested-modules list;
  - the `.ipynb` name rule finds what it found before, `notebooks/` included;
  - a plain `.py` file that mentions marimo, but has no `app = marimo.App(` line, is not a notebook.
- Run the suite with `uv run python build/run_suites.py tech-debt`.
- Check the kit's ruff snippet once, as F5 did: a notebook under `notebooks/`, a B config and a Q config, at each
  ruff version the work repos run, pre-commit pins included. Only I001 may remain. Record in the plan only that each
  version left I001 and nothing else, with no version number and no repo name *(designer's call: no permanent test,
  because the snippet is config text and only a ruff upgrade can change its effect)*.

**Plan B.**

- Micro-test the block, and explore-data's branch, against a no-guidance control, as writing-skills asks for
  behavior-shaping text. Run 5 reps per arm and case, and read every flagged match by hand.
- **Cases** *(designer's call)*:
  1. *Exploration.* The owner names a hunch. Score four behaviors: one view per turn; the turn ends after the view;
     the facts cell holds numbers and no met-or-not-met wording (D8); the hypothesis names an observable outcome.
  2. *Override.* The owner asks outright for several views. Score: the agent builds them all (D7).
  3. *Live-session lint.* The prompt says a session is live and carries the Stop hook's I001 message for the notebook.
     Score, in the block arm only: no `Write` or `Edit` on the notebook. The control has no rule to break here, so
     this case checks the block's Scope line and is not a red-green comparison.
- **Bar** *(designer's call)*: the block arm meets every scored behavior in 5 of 5 reps of cases 1 and 2, and case 3
  shows no `Write` or `Edit` in 5 of 5. After two wording rounds that miss the bar, stop and bring the record to the
  owner. By D9, a behavior the control already shows stays in the block.
- **Arms** *(designer's call)*: Claude Code only, through the repo's `claude -p` micro-test practice, on the model
  the owner's sessions use. Codex gets B0's loading check, not a behavior test. The fixture does not install
  marimo-pair, so its text never reaches a committed transcript. The fixture's `CLAUDE.md` says in one sentence, in
  this repo's words, that marimo-pair drives live sessions.
- The fixture needs no live marimo kernel *(designer's call)*. It is a repo with `notebooks/` and one marimo notebook.
  With no live session, editing the file is allowed (F1), and the loop reads the same either way.
- File the record by this repo's conventions: `specs/baseline/red-baseline-<topic>.md` and its kit folder.
- The recommend-visualization row gets no micro-test *(designer's call: it is routing reference, not discipline)*.
  Tier 1 of the snippet gate covers any new code block.

**Both plans.** Run `build/run_commit_lints.sh`. It covers frontmatter, provenance, conformance, dependency drift,
links, snippets and the cc-guide lint.

## Constraints

- **Public repo.** This repository is public, and the work repos are private. No plan, record, kit or skill text
  names a work repo for a fact, and none carries new detail from one: versions, configs, file sizes or file names.
  State a finding the way F2 and F12 do. Before each commit, `git grep` the base for each work-repo name the change
  mentions. A new mention is a leak.
- **Provenance.** Take ideas from Eric Ma's posts and from marimo-pair, never text. Credit Eric Ma by URL and idea
  only, as `NOTICE` does for Karpathy. marimo-pair is Apache-2.0: link to it, and copy nothing.
- **Install dependencies.** No skill's agent-facing text names a `templates/` path, because `install.py` installs
  skills, not the kit. The dependency-drift test fails on an undeclared reference.
- **Style.** Human prose (the kit README, `NOTICE`, the plans) follows the always-on plain-English rule. Agent-facing
  text (the block, skill text) uses the write-with-asd-ste100 skill. Python uses Polars, single quotes and the dev
  Python in `build/versions.toml`.
- **Versions.** If skill text cites a marimo version, add it to `build/versions.toml` as a cited-only version, or
  `versions.py check` fails.
- **marimo-pair's contract.** Nothing here tells the agent to import `marimo._code_mode` in a notebook cell, or to
  manage packages outside marimo-pair.
- **Register.** Every new or edited Claude Code artifact goes through `build/cc_guide/conformance.toml`, and
  `check_conformance.py` runs before each commit.

## Done when

**Plan A**

- `test_scan.py` holds the five cases and passes in both arms.
- `templates/marimo-repo/README.md` exists, with its install steps, its ruff snippet (checked as F5 did) and its
  credits, and names no work repo.
- `skills/tech-debt/SKILL.md` names the marimo signal and the convert outcome.
- `hooks/README.md` holds both additions and is restamped.
- Root `CLAUDE.md`, the register and `NOTICE` cover `templates/`.
- The commit lints pass.

**Plan B**

- B0's result is recorded, and it is truncation (or the owner has ruled on a drop).
- `templates/marimo-repo/notebook-block.md` holds the six parts between the markers, under 2,500 bytes.
- The kit README's paste step covers placement and updates.
- The micro-test record meets the bar for the block and for explore-data's branch.
- `skills/explore-data/SKILL.md` and `skills/recommend-visualization/` carry their changes, and `NOTICE` the credit.
- The commit lints pass.

## Designer's calls

1. The kit's path, `templates/marimo-repo/`, and its two file names.
2. `notebooks/` at the repo root only.
3. A marimo notebook is a `.py` file with a top-level `app = marimo.App(` line.
4. The `.ipynb` name rule in `scan.sh` stays as it is, in every folder.
5. A marimo notebook is never an untested module, and the source scans keep covering notebooks.
6. Convert is a third triage outcome beside HARDEN and DELETE.
7. The ruff ignore covers B018 and Q000 only. I001 and every other rule stay on.
8. Document the read-only guard gap, and add no rule.
9. No allow-list entries for marimo-pair's scripts. In auto mode a classifier reviews each call. If prompts appear,
   the owner adds the two entries from marimo-pair's README to that repo's settings.
10. The marker comments, and the block's 2,500-byte cap.
11. In the block: name code cells only, and keep `hide_code=True` in one line.
12. The block restates the Polars lines, because the clean-code rule never loads on live work (F11). The notebook
    exception (each view cell collects its own frame) lives only in the block.
13. The agent restates the hypothesis and builds the view in the same turn, and writes the facts cell in that turn.
14. Plan B checks Codex's handling of an oversized chain first (B0).
15. The micro-test's three cases, its bar, its Claude-Code-only arms and a fixture with no live kernel and no
    marimo-pair.
16. No micro-test for the recommend-visualization row, and no permanent test for the ruff snippet.

## Left to the builder

- The exact detector pattern for `app = marimo.App(`, and how each scan arm reads file contents.
- `scan.sh`'s section titles.
- The block's exact wording, within B1's list and cap, settled by the micro-test.
- Where the explore-data branch sits in "Output", and whether the profile summary goes into the notebook or into chat.
- Whether the register gets a new kind or an extended one.
- Whether B3 touches the SKILL.md table, `references/altair.md` or both, beyond the row and the note.
- The micro-test's fixture prompts and its isolation, within the cases above.

## Not in this spec

- **Converting the three scratch notebooks.** That is work in the work repos, by the A3 path, once Plan A merges.
  The owner starts one session per repo.
- **Trimming `AGENTS.md` files near or past Codex's limit** (F12). That is the owner's call in those repos. B1's
  paste step keeps the block inside the limit either way.
- **Installing the hook templates or the clean-code rule in the work repos.** Both stay owner steps.
- **agy coverage.** This spec does not check what agy loads in the work repos.

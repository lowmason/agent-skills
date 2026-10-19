# document-python-package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `document-python-package`, an original skill that documents a public Python package with Great Docs 0.17.x as a thin layer over Posit's five official Great Docs skills.

**Architecture:** First, a spike on a scratch fixture package answers the spec's eight open questions (S1 to S8), and its answers amend the spec. Next, a test kit outside the repository runs the RED baseline: decision-only `claude -p` calls with no skill. Then one commit adds the skill bundle: `preflight.py`, written test-first, a SKILL.md filled from the spike's answers, and the provenance and registry entries. GREEN (the same calls with the skill loaded), a trigger test and one end-to-end run on the fixture then check the skill's behavior. The repo docs and the acceptance gates come last.

**Tech Stack:** `preflight.py` uses the Python 3.11+ stdlib, with a PEP 723 header, and runs with `uv run`. Its tests use pytest. The spike uses great-docs 0.17.0, Quarto 1.10.19, uv and git. The skill tests use Claude Code's `claude -p` (a held copy, 2.1.302 when planned) on Opus 5.5. The completeness check uses pydoclint or numpydoc, as S7 chooses. The kit and the lints run on Python 3.13 through `uv run`.

**Spec:** [`specs/document-python-package-spec.md`](../document-python-package-spec.md)

## Global Constraints

These come from the spec unless a line says otherwise. Every task's requirements include them.

- **Files** (R1.1, the layout): `skills/document-python-package/` holds `LICENSE` ("byte-identical copy of the root LICENSE"), `SKILL.md`, `scripts/preflight.py` and `scripts/test_preflight.py`, and nothing else.
- **Frontmatter** (R1.2 to R1.4): `name`, `description`, `license: MIT`, `compatibility`, `metadata.author: Lowell Mason` and `metadata.version: "1.0"`. The description starts with "Use when", names the primary trigger in its first 150 characters, and stays under 1,024 characters. `compatibility` has 500 characters at most. The repo's lints add two rules: the description needs a trigger marker, such as "triggers when", and it uses no first-person or second-person pronoun.
- **Length.** SKILL.md stays under 500 lines, and about 250 is the target (R1.5). Its body after the frontmatter stays under 20,000 characters, because the `compaction-window` check of `build/check_conformance.py` fails above that (planning fact).
- **No Posit text.** The repository gets no "copy, adaptation or summary of the official skills' text" (spec, Out of scope). The skill only names those skills and sends the agent to them. Files fetched from posit-dev/great-docs stay in caches outside the repository.
- **Authority** (R2): the skill "never reads main-branch text or the docs site's skills, and it never runs `great-docs skill install`". The agent never runs the cached skills' scripts.
- **`preflight.py`** (R3). It uses only the stdlib. Line 1 is `#!/usr/bin/env python3`. A PEP 723 header follows, with single-quoted TOML strings, `dependencies = []` and `requires-python = '>=3.11'`. The script reads the version from `uv.lock` with `tomllib`. The range is "0.17.0 included, 0.18.0 excluded", printed as `>=0.17.0,<0.18`. The cache is `${XDG_CACHE_HOME:-~/.cache}/agent-skills/great-docs/<version>/`. The remote is `https://github.com/posit-dev/great-docs` at tag `v<version>`, cloned with `--depth 1 --filter=blob:none --sparse`.
- **Order** (spec, Sequencing). The spike (Task 1) amends the spec before any skill text is written. `preflight.py` is written test-first. RED (Task 2) runs before SKILL.md exists, and GREEN (Task 4) runs after. The NOTICE entry lands in the commit that creates SKILL.md.
- **One bundle commit** (planning fact). The orphan-file, provenance and suite-registry lints each fail on part of the bundle alone. So `preflight.py`, its tests, SKILL.md, `LICENSE`, both NOTICE edits, the CLAUDE.md edit and the `build/suites.toml` entry land in one commit (Task 3).
- **Spike values.** A `{{KEY}}` slot in this plan gets its value only from the Values table of `specs/verification/57-great-docs-0.17.0.md`, through `fill_slots.py`. Never fill a slot by hand, and never from "Facts measured while planning".
- **Amendment tags.** Planning amendments carry `(owner, plan 57, 2026-10-19)`. Spike amendments carry `(spike Sn, plan 57, <the spike's date>)`. The spec's status line never changes.
- **No early install** (planning fact). `~/.claude/skills` resolves to the main checkout's `skills/`. Never install or link the skill at user level before the merge, because a user-level copy contaminates every RED call.
- **Test isolation** (V3). Every skill-test call goes through the kit's `run.py`: a held binary, a scrubbed environment and a new folder under `/tmp`. Read every reply by hand.
- **Commands.** Run every command from the execution worktree's root. Never `cd`: the shell's folder resets after each command, and a `cd` into another worktree moves the session there. Shell variables do not persist between commands, so each command spells out its paths. The shell is zsh. It has no `PIPESTATUS`, and it splits `$(…)` into words but never `$VAR`.
- **Push or merge nothing** without the owner's go-ahead (repo convention).
- **Test counts** are deltas (+N), never totals (repo convention).
- **Commit trailer.** Each commit message ends with the executing session's own `Co-Authored-By:` line. Add it as the last `-m` of each `git commit` in this plan, because the commands here leave it out. Subagent-authored commits keep that same line. Check it with `git log -1 --format=%B`.
- **Python style:** single quotes, f-strings and named constants. The kit and `build/` run on Python 3.13 (repo convention).

## Decisions

- **D1** (owner, brief, 2026-10-19): Planning runs on Opus. Execution runs on Sonnet in a fresh session, with this plan file as the handoff. Applied in: Execution handoff.
- **D2** (owner, brief, 2026-10-19): This plan is committed on `claude/great-docs-skill-design-19335c`, which also holds the spec's three unpushed commits (`475f5d0`, `3cdb38f` and `e72f284`). Applied in: Execution handoff.
- **D3** (owner, plan review, 2026-10-19): Q1's option (c). The `compatibility` text is the portability spec's house string with Python 3.11+, then git, Quarto, the version range and the network fetch. The owner also approved amendments A1 (19 runnable scripts) and A2 (R1.4's new text) as worded. Applied in: Task 1 (spec amendment), Appendix B (SKILL.md).
- **D4** (owner, plan review, 2026-10-19): The settled defaults DF1 to DF28 stand as written. Applied in: Planning record (Settled defaults), and the tasks that each default names.
- **D5** (owner, brief, 2026-10-19): Inline Execution: "One Sonnet session runs Tasks 1 to 6 with the executing-plans skill." Applied in: Execution handoff.
- **D6** (owner, brief, 2026-10-19): a code review of Task 3's bundle commit before Task 4: "After Task 3's bundle commit, the code-reviewer agent reviews that commit. Fixes that hold up land before Task 4, so GREEN measures the text that ships." Applied in: between Task 3 and Task 4.
- **D7** (owner, brief, 2026-10-19): a SKILL.md change from the final whole-branch review, after GREEN: "The fix waits for you. You then choose: re-run GREEN for the scenarios it touches, or ship it with the skill-test record naming the text that GREEN did not measure." Applied in: the whole-branch review (executing-plans, Step 3).
- **D8** (owner, brief, 2026-10-19): the execution model: "Since it is inline, run using opus." The execution session runs on Opus, in place of the Sonnet in D1 and D5. Applied in: Execution handoff.
- **D9** (owner, execution session, 2026-10-19): the execution worktree. The app started the execution session in its own worktree, `keen-kilby-445f76`, on `claude/agent-skills-handoff-execution-187eb5`, where its Edit tool cannot write to a second worktree. The owner chose: "I run git merge --ff-only feat/document-python-package on this session's branch (it has no commits, so it moves to 407d1e0) and execute here. At the end you decide how feat/document-python-package gets the commits (a fast-forward of that worktree, or this branch as the PR branch)." So "the execution branch" in Task 1, Step 1 and "the execution worktree" in Global Constraints mean this worktree and branch, and `feat/document-python-package` stays at `407d1e0`. Applied in: every task, and finishing-a-development-branch.
- **D10** (owner, execution session, 2026-10-19): the docstring-example sentence. A spike S3 probe on the scratch fixture showed that great-docs 0.17.0 freezes docstring examples by default (`Freeze mode: auto`). An example ran when its docstring changed and when no `_freeze/` existed. It did not run on an unchanged rebuild. So "Docstring examples run on every build" was wrong. The owner chose: "Before Step 6, I replace the sentence in the spec's R4.7 and in fill_slots.py's `yes` text (and its block in the plan), add the probe to the spike record's S3, and log it as D10. GREEN then measures the corrected text." Applied in: Appendix D (`fill_slots.py`), the spec's R4.7 and the spike record's S3. Deviation: R4.7 was corrected by hand after Task 1, Step 19, so Appendix C's `s3-docstrings-run` block keeps the text that Step 19 applied, not the text that ships.
- **D11** (owner, execution session, 2026-10-19): the frozen-example gap. The same probe showed that after a change to a function's body, with its docstring unchanged, the build exits 0 and the page shows the stale frozen output. So a broken example can pass the gate's build check. The owner chose: "I record it in the spike record and add a deferred item (size: design). Plan 57 adds no gate change, because no RED reply showed this failure (DF14)." Applied in: the spike record's S3, and Plan completion.

---

## Planning record

### Facts measured while planning

Measured on 2026-10-19 on the owner's Mac, from scratch folders outside the repository.

- **Tools.** uv 0.13.1, git 2.56.0, Quarto 1.10.19 at `/usr/local/bin/quarto`, Claude Code 2.1.302, and Python 3.11.14, 3.12.12 and 3.13.16 through uv.
- **great-docs 0.17.0's dependencies** (PyPI metadata) include `jupyter>=1.1.1` and `ruff>=0.9.9`. So a package that pins great-docs gets a Jupyter kernel for executed cells and a locked ruff.
- **The real fetch.** The prototype `preflight.py` fetched tag `v0.17.0` in about 0.9 s and recorded commit `1ce8eb88191df75405345b6ba2d35bea53a4f7f6`, the commit that the spec names. The tag's `skills/` folder holds the five official skills.
- **The tests.** The 24 tests in Appendix B passed under Python 3.11, 3.12 and 3.13. By the portability spec's R3.3 rule (the floor is the lowest of 3.11, 3.12 and 3.13 under which the suite passes), the floor is `>=3.11`. Five mutations of `preflight.py` each made at least one test fail.
- **The completeness tools** on the fixture (Appendix E). pydoclint 0.11.1 with `--skip-checking-short-docstrings=False` reported DOC101 and DOC103 (a parameter missing from the docstring) on `scale` and DOC201 and DOC203 (no Returns section) on `Ratio.inverse`, and nothing else. Its default skips a summary-only docstring, so without the flag it misses `Ratio.inverse`. numpydoc 1.11.0, with Appendix E's table in `pyproject.toml`, reported PR01 (an undocumented parameter) on `scale`, RT01 (no Returns section) on `Ratio.inverse` and GL08 (no docstring) on `Ratio.as_tuple`, and nothing else. It read the table from `pyproject.toml` with no `--config` flag.
- **ruff and `'''` docstrings.** On the fixture's `src/`, `ruff format --isolated --diff` (ruff 0.17.1) added 11 `"""` lines under the default quote style, 11 under `quote-style = 'single'` and 0 under `quote-style = 'preserve'`. The spike measures again with the ruff that the fixture's lock holds.
- **Triggering.** A canary skill in a scratch repo's `.claude/skills/` was listed in `claude -p`'s init record and called through the Skill tool (stream-json, 3 turns, $0.27). The init record listed 110 skills and permission mode `auto`. `claude -p` waits 3 seconds for stdin when the prompt is an argument, so the kit gives such calls `/dev/null` as stdin.
- **Plan 52's measured facts carry over.** `--strict-mcp-config` removes the connector tools that `--tools ""` leaves. `--max-budget-usd` puts a budget line into the model's context.
- **macOS has no `timeout` command.** The kit bounds each call with Python's `subprocess` timeout.
- **The repo's lints.** `check_conformance.py` exits 1 on any finding, `advice` included. Its `orphan-bundled-file` check flags `preflight.py` until SKILL.md names it, and a test file never counts as naming another file. `check_provenance.py` fails on a skill with no NOTICE entry, and when the originals lists of NOTICE and CLAUDE.md differ. `run_suites.py --check` fails while a folder that holds tests is not registered.
- **The `build` suite** has 4 known failures: the ground-truth tests of `test_verify_citations.py`, which need the gitignored `build/.scratch/`.
- **Counts.** 38 skills exist, so this skill is the 39th. 18 runnable scripts exist: plan 53's planning record counted 17, and plan 52 then added its vendored `ste-lint.py`. So `preflight.py` makes 19, not the spec's 18 (amendment A1, below).
- **`CLAUDE.md`** has 147 lines. Task 3 lengthens one existing line.

### Prototype and replay

Everything in this plan ran before the plan was written, in scratch folders outside the repository, except the spike's great-docs commands and every `claude -p` call.

- **Kit.** `transcript.py` read the canary probe's real stream-json transcript. A positive control (the canary renamed to this skill) printed `listed, TRIGGERED`. A planted repository path and a planted permission denial each printed `VOID`. `run.py`'s `tool_env` found `uv`, `git` and `quarto` on the kit's fixed `PATH`, and it refused a `PATH` without them. `run.py`'s staging made a repo with one commit, no remote and no tags, with the skill copy excluded from git and no `__pycache__` copied. `gate.py` printed a `FAIL` for each check on a fixture without great-docs, with pydoclint's findings as the evidence. `fill_slots.py` filled the SKILL.md template with four value sets that together cover every variant, and each result passed the frontmatter, conformance and snippet checks.
- **Replay.** After assembly, a planning-time script ran this plan's own blocks and commands in a fresh clone of this branch at `e72f284`, with `KIT` and `SPIKE` moved under `/tmp/plan57-replay/`. All of its 61 checks passed:
  - The extractor cut itself out of the plan and reproduced its own block. Every file block matched its prototype byte for byte.
  - A1 and A2 applied once each and left three tags.
  - The fixture had 8 files at `pristine`, and its lock held great-docs 0.17.0 after the pin.
  - For each of the four value sets, the spike amendments applied 10 or 12 blocks exactly once, and `fill_slots.py` left no slot in the spec or in SKILL.md.
  - The kit wrote five RED prompts with no slot left, and no scenario or artifact named the skill.
  - Task 3: RED failed with `No module named 'preflight'`, then 24 tests passed on 3.13 and on 3.11. The real preflight printed `next: pin` for `pristine` and `next: ready` for a stand-in `configured` tag (a `great-docs.yml` written by hand in place of `init`), and `SOURCE` held the spec's commit. SKILL.md had 198 lines and a body of 8,253 characters. Every lint passed, the drift test passed, and the bundle commit left no file behind.
  - The five GREEN prompts held the skill. Task 5's three edits and its date step applied.
  - A clean clone of the result passed `run_commit_lints.sh` and the new suite (24).
- **The `build` suite** ran on this branch and on the replay's final commit: the passed count was the same before and after (+0), with the same 4 known failures, in about a minute each.
- **Plan 53.** Plan 53's 14 edits to the four files that both plans change (`NOTICE`, `CLAUDE.md`, `README.md` and `skills/design-architecture/SKILL.md`) and this plan's 5 edits to them were applied to copies of this branch's files, in both landing orders. Every edit applied, and both orders gave the same files.
- **Not replayed:** the spike's great-docs commands (Task 1, Step 7's install and Steps 8 to 17, which are the spike itself) and every `claude -p` call (Tasks 2 and 4).

### Settled defaults

Each default below is the plan's choice where the spec left one open. "If wrong" says what changes. The owner approved all of them as written at plan review (D4).

- **DF1, one bundle commit.** See Global Constraints. If wrong: the commit lints fail on every partial commit.
- **DF2, spike values as slots.** SKILL.md and the spike's spec amendments carry `{{KEY}}` slots. `fill_slots.py` fills them from the spike record's Values table, so no value is typed twice. If wrong: fill by hand, and lose the replayed checks.
- **DF3, amendment tags.** As Global Constraints says. The owner approved the two planning amendments (A1, A2) at plan review (D3), and the spike's amendments follow the spec's V1 table. If wrong: retag the blocks in Appendix C.
- **DF4, the order of the stops.** `preflight.py` checks the layout first, then Quarto, then the pin, the range and the fetch. A `docs` or `both` layout and a missing Quarto stop the work even before the pin, because a pin fixes neither. If wrong: reorder `next_step()`.
- **DF5, the `skills:` key** prints the cached `skills/` folder, which holds the five official skill folders. If wrong: print the version folder.
- **DF6, `requires-python = '>=3.11'`.** See "Facts measured while planning". `tomllib` also needs 3.11.
- **DF7, `SOURCE`** holds three lines: `tag:`, `commit:` (the commit that the tag points to, through an annotated tag) and `fetched:` (UTC). If wrong: change `fetch_skills()` and its test.
- **DF8, `GIT_TERMINAL_PROMPT=0`.** git never asks for a password, so a bad URL fails at once. If wrong: a bad remote can hang the preflight.
- **DF9, the test model.** Opus 5.5 (`claude-opus-5-5`) at medium effort, as plan 52's D3 chose for its tests. If wrong: change `MODEL` and `EFFORT` in `run.py` before the first run.
- **DF10, decision-only calls** use `--tools ""`, `--strict-mcp-config` and `--no-session-persistence`, and no `--max-budget-usd`. If wrong: connector tools or a budget line enter the measured context.
- **DF11, hand-written artifacts for sc2 and sc3.** The workflow, build output and lint output in those scenarios are short, hand-written files that match the spec's source facts. The real files from the spike are longer and hold machine paths. If wrong: paste the spike's files instead.
- **DF12, the scenario set.** sc1, sc3 and sc4 are the three scenarios that V3 names. sc2 and sc5 are this plan's own, and they test M4 (the unpinned CI line left in) and M1 (the official skills from the wrong source). X1, the slow example in the wrong place, is an extra item from R4.7.
- **DF13, the broad reading of M5 (done without the gate).** Any reply that calls the docs done or fine to merge before all three gate checks pass shows M5, in any scenario. If wrong: count only lint-based claims in sc3.
- **DF14, the decision rules** in `PREREGISTRATION.md` (Appendix D). They follow writing-skills: 5 replies per scenario and arm, every reply read by hand, and no new guidance without an observed failure. The spec's own text stays even for an item that RED does not show, because the spec requires it.
- **DF15, the trigger test.** One call per query, as the spec's "five-query trigger smoke test" says. All 5 must pass. One description revision is allowed. If wrong: add reps per query.
- **DF16, the end-to-end run.** One run on the `pristine` fixture with tools on, the owner's permission mode, a fresh `XDG_CACHE_HOME` and criteria E1 to E7 (`PREREGISTRATION.md`). It has `--max-budget-usd 15`: it measures no wording, so a hard cost bound matters more than the budget line in its context.
- **DF17, no `# cc-guide:` line.** R1.2 asks for one only when the register or its lints require it. The lints passed without one on the prototype bundle.
- **DF18, R3.5's sentence** ("Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header.") follows SKILL.md's first fenced `uv run` call, as the portability spec asks.
- **DF19, no test run for the design-architecture bullet.** It adds one approved sentence (the spec's D6) to a reference section. If wrong: add a scenario to the kit.
- **DF20, the S7 selection rule.** A tool qualifies when it exits non-zero, reports `scale`'s undocumented `factor` and `Ratio.inverse`'s missing Returns section, and reports nothing on `summarize`, `Ratio` or `Ratio.value`. When both qualify, choose the one that also reports `Ratio.as_tuple`'s missing docstring. When that does not separate them, choose pydoclint, which needs no config table. When neither qualifies, stop and ask the owner. With the planning results, the rule chooses numpydoc.
- **DF21, a freeze cache that git cannot keep stops the work.** If `_freeze/` lands only inside the ephemeral `great-docs/` folder, or git ignores it, R4.7's convention cannot work as written: stop and ask the owner.
- **DF22, paths.** The kit is `~/.cache/agent-skills/scratch/document-python-package-kit/`, the spike's folder is `~/.cache/agent-skills/scratch/great-docs-spike/`, and runs go to `/tmp/dpp-kit-runs/`, `/tmp/dpp-trigger/`, `/tmp/dpp-e2e/` and `/tmp/dpp-preflight/`. If wrong: change the constants in `run.py`.
- **DF23, the records.** The spike record is `specs/verification/57-great-docs-0.17.0.md` (the spec names it). The skill-test record is `specs/verification/57-document-python-package-skill-tests.md`.
- **DF24, the fixture.** `gdfixture` has three exports with planted gaps: `scale` leaves `factor` undocumented, `Ratio.inverse` has a summary-only docstring, and `Ratio.as_tuple` has none. Its README's first paragraph, its `pyproject.toml` description and its module docstring all differ, so S8 can tell which one the site's meta description comes from.
- **DF25, the spike pins `great-docs==0.17.0`.** The spike measures the exact version that the spec read. The skill's own pin is the range.
- **DF26, an S5 contradiction stops the work.** If a plain `uv sync` does not install the `docs` group, R4.2's local `uv run great-docs` breaks too, not only CI's workflow (R4.8). That is more than V1's S5 row covers, so the owner decides.
- **DF27, S6 measures three quote styles.** Planning found that `quote-style = 'preserve'` keeps `'''` docstrings while `'single'` does not. So S6 records the default, `single` and `preserve`. R4.4's note, which tells the agent to ignore pydocstyle's rule D300 (it asks for `"""` docstrings), then names the style that keeps them.
- **DF28, the completeness check covers the package folder.** Neither tool can select objects by `__all__`. The package folder holds every export, so the check covers more than the spec's "over the `__all__` exports", never less.

### Plan review question

- **Q1, the `compatibility` text.** R1.4 gives "Requires uv, git, Quarto and great-docs >=0.17.0,<0.18. The preflight script needs Python >=3.11 and fetches Posit's official Great Docs skills from github.com." The portability spec's R3.6 gives the house string for a skill with scripts: `Requires uv to run bundled scripts (dependencies are declared inline); Python 3.X+.`
  - (a) R1.4's text as it stands. It names uv, so the portability lint (R3.7) accepts it.
  - (b) The house string alone, with `3.11`. It drops git, Quarto, the range and the network fetch.
  - (c) Both: the house string, then the rest. Amendment A2 (Appendix C) changes R1.4 to "Requires uv to run bundled scripts (dependencies are declared inline); Python 3.11+. Also requires git, Quarto and great-docs >=0.17.0,<0.18, and the preflight script fetches Posit's official Great Docs skills from github.com." The plan carries (c), and recommends it: the skill matches the other skills with scripts and keeps every fact.
  - The owner chose (c) at plan review (D3).

### Amendments

The owner approved both at plan review (D3). Task 1, Step 4 applies them before the spike.

- **A1, the script count** (spec, Sequencing item 5). The spec says that `preflight.py` makes 18 runnable scripts. Plan 52's vendored `ste-lint.py` landed after plan 53 counted 17, so `preflight.py` makes 19. The line that Task 5 adds to plan 53, as the spec's D8 asks, says 19.
- **A2, the `compatibility` text** (R1.4). Q1's option (c).

### Couplings

- **(a) Plan 53, the portability plan** (`specs/plans/53-agent-skills-portability.md`, live and not executed on 2026-10-19). Its `build/check_frontmatter.py` change adds `SPEC_KEYS`, so that name shows whether plan 53 has run. If this skill lands first, Task 5 adds one dated line to plan 53's Global Constraints, as the spec's D8 asks. This plan calls it the D8 line. Plan 53's helpers name their scripts and skills one by one: Task 10's `HEADERS`, Task 12's `FLOORS` and Task 13's `r38.sh`. Its Task 8 copies the root `LICENSE` into every skill folder, which writes the same bytes as this skill's copy. So plan 53 leaves this skill alone. If plan 53 lands first, its lints check this bundle in Task 3, and the D8 line is not needed.
- **(b) Other plans that edit the same files.** Task 3 and Task 5 edit `NOTICE`, `CLAUDE.md`, `README.md`, `build/suites.toml`, `skills/design-architecture/SKILL.md` and plan 53's file. If an edit block no longer matches because another plan changed the text around it, read the current text, make the same change by hand, and note it as a deviation. Never restore the old text.

### Plan ID

The plan-id check (`skills/writing-plans/scripts/entry_check.py`) printed "next free: 57" on 2026-10-19, and this plan claimed 57 at once with a stub. A re-run with the full plan in place printed "next free: 58" and "collisions: none". It found no path shared with plan 51 (`51-claude-code-drift-automation.md`), and five paths shared with plan 53 (`53-agent-skills-portability.md`): `CLAUDE.md`, `NOTICE`, `README.md`, `skills/design-architecture/SKILL.md` and plan 53's own file. Coupling (a) and "Prototype and replay" cover them. The kit, the block keys and the branch name carry no plan id. A renumbering changes this file's name, the plan path in its commands, the two record names and the mentions of "plan 57".

## File structure

Outside the repository (never committed):

| Path | Holds |
|---|---|
| `~/.cache/agent-skills/scratch/document-python-package-kit/` (`KIT`) | `extract_plan_files.py` (Task 1, Step 3), `fill_slots.py`, `run.py`, `build_prompts.py`, `show.py`, `transcript.py`, `gate.py`, `PREREGISTRATION.md`, `RESULTS.md`, `scenarios/`, `artifacts/` (Appendix D). Made by commands: `bin/`, `prompts/`, `out/`. |
| `~/.cache/agent-skills/scratch/great-docs-spike/` (`SPIKE`) | `inspect_site.py`, `numpydoc-table.toml` (Appendix E), and the spike's logs. |
| `SPIKE/gdfixture/` (`FIX`) | The fixture package (Appendix E), a git repository with tags `pristine` and `configured`. |

In the repository:

| Path | Task |
|---|---|
| `specs/document-python-package-spec.md` | Modify, Task 1: A1 and A2 (Step 4), the spike's amendments (Step 19), Appendix C |
| `specs/verification/57-great-docs-0.17.0.md` | Create, Task 1, Step 18 (Appendix B) |
| `specs/verification/57-document-python-package-skill-tests.md` | Create, Task 2, Step 8, and complete, Task 4 (Appendix B) |
| `skills/document-python-package/scripts/test_preflight.py`, `scripts/preflight.py`, `SKILL.md`, `LICENSE` | Create, Task 3 (Appendix B, and a copy of the root `LICENSE`) |
| `NOTICE`, `CLAUDE.md`, `build/suites.toml` | Modify, Task 3 (Appendix C) |
| `README.md`, `skills/design-architecture/SKILL.md`, `specs/plans/53-agent-skills-portability.md` | Modify, Task 5 (Appendix C) |
| `specs/deferred_items.md` | Modify, plan completion |

**Blocks.** A line `<!-- extract-file: PATH -->` followed by a fenced block holds a whole file. A line `<!-- extract-edit: PATH:LABEL -->` followed by two fenced blocks holds an edit: the old text, which must occur exactly once in the file, and the new text. `extract_plan_files.py PLAN ROOT KEY...` writes and applies them, so nobody retypes code. A file block that holds fences of its own uses a four-backtick fence. Read each block in its appendix before you apply it.

**Names in prose.** `KIT`, `SPIKE` and `FIX` above, and `PLAN` for `specs/plans/57-document-python-package.md`. The commands spell out the full paths.

---
### Task 1: The spike and its spec amendments

**Files:**
- Create, outside the repository: `KIT/extract_plan_files.py` (Step 3, cut from this task), `KIT/fill_slots.py` (Step 3, Appendix D), the fixture `FIX/`, `SPIKE/inspect_site.py` and `SPIKE/numpydoc-table.toml` (Step 5, Appendix E). Commands write the spike's logs into `SPIKE/`.
- Create: `specs/verification/57-great-docs-0.17.0.md` (Step 18, Appendix B)
- Modify: `specs/document-python-package-spec.md` (Step 4: A1 and A2. Step 19: the spike's amendments. Both in Appendix C.)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: the fixture repository `FIX` with two tags. `pristine` is the package before any great-docs change. `configured` adds the pin `great-docs==0.17.0` and the files that `init` wrote. Tasks 2 to 4 use both. The spike record's Values table, which `fill_slots.py` reads in Task 3 and `gate.py` reads in Task 4. `KIT/extract_plan_files.py` and `KIT/fill_slots.py`, which every later task runs.

- [ ] **Step 1: Check the worktree, the tools and the baselines**

```bash
git branch --show-current
git status --short
git log -1 --format='%h %s' -- specs/plans/57-document-python-package.md
uv --version
git --version
quarto --version
claude --version
ls ~/.claude/skills/ | grep -c document-python-package
uv run --python 3.13 python build/run_suites.py build
bash build/run_commit_lints.sh
```

Expected: the execution branch, no changes, and the commit that last changed this plan. Then the versions. Planning used uv 0.13.1, git 2.56.0, Quarto 1.10.19 and Claude Code 2.1.302. Another version is not a stop, but the spike record names it. Then `0`: no user-level copy of the skill exists. Any other number: stop and ask the owner. The `build` suite takes about a minute: write down its passed count for Task 6. Only the 4 ground-truth tests of `test_verify_citations.py` fail. Last, `commit lints passed`.

- [ ] **Step 2: Check whether plan 53, the portability plan, has run**

```bash
test -f specs/plans/53-agent-skills-portability.md && echo 'plan 53 is live'
grep -c SPEC_KEYS build/check_frontmatter.py
git log --all -S SPEC_KEYS --oneline -- build/check_frontmatter.py
```

Expected: `plan 53 is live`, then `0`, then no output. Plan 53 has not run, so Task 5 adds the D8 line (Coupling (a)). Any other result: plan 53 has run or is running. Tell the owner before Task 3, and skip Task 5, Step 2.

- [ ] **Step 3: Cut the extractor out of this plan, and write the slot filler**

The extractor's block follows the commands. The `awk` command cuts it out of the plan, so nobody retypes it:

```bash
mkdir -p ~/.cache/agent-skills/scratch/document-python-package-kit
awk '/^<!-- extract-file: extract_plan_files.py -->$/ {f = 1; next} f && /^```python$/ {p = 1; next} p && /^```$/ {exit} p' specs/plans/57-document-python-package.md > ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md /tmp/dpp-extract-check extract_plan_files.py
cmp ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py /tmp/dpp-extract-check/extract_plan_files.py
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md ~/.cache/agent-skills/scratch/document-python-package-kit fill_slots.py
```

Expected: `wrote extract_plan_files.py`, no output from `cmp` (the extractor reproduces its own block byte for byte), then `wrote fill_slots.py`. The extractor comes from plan 52 unchanged.

<!-- extract-file: extract_plan_files.py -->
```python
#!/usr/bin/env python3
'''Write the plan's file blocks and apply its edit blocks.

Usage: python3 extract_plan_files.py PLAN ROOT KEY [KEY...]

A file block is a marker line, <!-- extract-file: PATH -->, then one fenced
block that holds the whole file. An edit block is a marker line,
<!-- extract-edit: PATH:LABEL -->, then two fenced blocks: the old text, which
must occur exactly once in ROOT/PATH, and the new text. A KEY is the marker's
PATH or PATH:LABEL. A block's text is the lines between its fences, each with
a newline. The keys apply in the order given, and the first error stops the run.
'''
import re
import sys
from pathlib import Path

MARK = re.compile(r'^<!-- extract-(file|edit): (\S+) -->$')
OPEN = re.compile(r'^(`{3,})[\w-]*$')
LEAD = re.compile(r'^(?:|Old text:|New text:)$')


def fenced(lines: list, start: int) -> tuple:
    '''The text of the next fenced block at or after lines[start], and the index after it.'''
    i = start
    while not OPEN.match(lines[i]):
        if not LEAD.match(lines[i]):
            raise SystemExit(f'line {i + 1}: expected a fenced block, found {lines[i]!r}')
        i += 1
    fence = OPEN.match(lines[i]).group(1)
    end = lines.index(fence, i + 1)
    return ''.join(line + '\n' for line in lines[i + 1:end]), end + 1


def blocks(plan: Path) -> dict:
    lines = plan.read_text(encoding='utf-8').split('\n')
    found = {}
    for n, line in enumerate(lines):
        m = MARK.match(line)
        if m is None:
            continue
        kind, key = m.groups()
        if key in found:
            raise SystemExit(f'{key}: two blocks in {plan}')
        first, after = fenced(lines, n + 1)
        found[key] = (kind, first, fenced(lines, after)[0] if kind == 'edit' else None)
    return found


def main(argv: list) -> int:
    if len(argv) < 3:
        raise SystemExit(__doc__)
    plan, root, keys = Path(argv[0]), Path(argv[1]), argv[2:]
    found = blocks(plan)
    for key in keys:
        if key not in found:
            raise SystemExit(f'{key}: no block in {plan}')
        kind, first, second = found[key]
        if kind == 'file':
            target = root / key
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(first, encoding='utf-8')
            print(f'wrote {key}')
            continue
        target = root / key.rsplit(':', 1)[0]
        text = target.read_text(encoding='utf-8')
        count = text.count(first)
        if count != 1:
            raise SystemExit(f'{key}: the old text occurs {count} times in {target}')
        target.write_text(text.replace(first, second, 1), encoding='utf-8')
        print(f'edited {key}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Amend the spec with A1 and A2**

The owner approved both at plan review (Planning record, Amendments). The spec's status line stays as it is.

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md . specs/document-python-package-spec.md:a1-scripts specs/document-python-package-spec.md:a2-compatibility
grep -c '(owner, plan 57, 2026-10-19)' specs/document-python-package-spec.md
bash build/run_commit_lints.sh
git add specs/document-python-package-spec.md
git commit -m "docs(specs): amend the document-python-package spec at plan 57's review" -m "A1: preflight.py makes 19 runnable scripts, because plan 52's vendored ste-lint.py landed after plan 53 counted 17. A2: compatibility opens with the portability spec's R3.6 string."
```

Expected: two `edited` lines, `3` (A1 adds two tags and A2 one), and `commit lints passed`.

- [ ] **Step 5: Write the fixture and the spike's tools**

```bash
test -e ~/.cache/agent-skills/scratch/great-docs-spike && echo 'SPIKE EXISTS'
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md ~/.cache/agent-skills/scratch/great-docs-spike gdfixture/pyproject.toml gdfixture/.python-version gdfixture/.gitignore gdfixture/README.md gdfixture/src/gdfixture/__init__.py gdfixture/src/gdfixture/core.py gdfixture/user_guide/00-introduction.qmd inspect_site.py numpydoc-table.toml
```

Expected: no `SPIKE EXISTS` line, then nine `wrote` lines. If the folder existed, stop and ask the owner: an old fixture would mix two spikes.

- [ ] **Step 6: Make the fixture a repository, and tag `pristine`**

```bash
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture init --quiet --initial-branch main
uv lock --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture add -A
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture -c user.name=spike -c user.email=spike@example.com commit --quiet --message pristine
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture tag pristine
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture ls-files
```

Expected: `uv lock` resolves a few packages. Then eight files: `.gitignore`, `.python-version`, `README.md`, `pyproject.toml`, `src/gdfixture/__init__.py`, `src/gdfixture/core.py`, `user_guide/00-introduction.qmd` and `uv.lock`.

- [ ] **Step 7: Pin great-docs 0.17.0, and install it**

The spike pins the exact version that the spec read (DF25).

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md ~/.cache/agent-skills/scratch/great-docs-spike gdfixture/pyproject.toml:pin
uv lock --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture
uv sync --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture python -c "import importlib.metadata as m; print(m.version('great-docs'))"
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture great-docs init --help
```

Expected: `edited gdfixture/pyproject.toml:pin`. The first sync installs great-docs with Jupyter and can take minutes: give it a 10-minute timeout. Then `0.17.0`, and `init`'s help, which lists `--project-path` and `--force`. Another version, or no `--force`: stop and ask the owner.

- [ ] **Step 8: S1, a non-interactive `init`**

```bash
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture great-docs init --force </dev/null > ~/.cache/agent-skills/scratch/great-docs-spike/s1-init.log 2>&1; echo "exit $?"
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture status --short
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture diff -- .gitignore
grep -n -E 'parser|Ratio|scale|summarize' ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture/great-docs.yml
```

S1 has three checks: the command exits 0, `.gitignore` gains lines (the status and the diff show it), and the new `great-docs.yml` holds `parser: numpy` and all three exports (`Ratio`, `scale` and `summarize`). Expected: all three pass. Then the Values are `INIT_DEFAULT_WORKS` = `yes` and `INIT_COMMAND` = `uv run great-docs init --force </dev/null`.

If a check fails, undo the attempt, then try the next form. A form without `--force` answers the `.gitignore` prompt itself:

```bash
rm -f ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture/great-docs.yml
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture checkout -- .gitignore
printf 'y\n' | uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture great-docs init > ~/.cache/agent-skills/scratch/great-docs-spike/s1-init-printf.log 2>&1; echo "exit $?"
```

Run the same three checks on it. If one fails, undo again and try `yes | uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture great-docs init`, with its log in `s1-init-yes.log`. The first form that passes gives `INIT_DEFAULT_WORKS` = `no`, and `INIT_COMMAND` is that form without `--directory` and the log. In the Values table, write each `|` as `\|`. If no form passes: stop and ask the owner.

Then tag the state that Tasks 2 to 4 stage as `configured`:

```bash
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture add -A
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture -c user.name=spike -c user.email=spike@example.com commit --quiet --message configured
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture tag configured
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture show --stat --format=%s configured
```

Expected: `configured`, with `.gitignore`, `great-docs.yml`, `pyproject.toml` and `uv.lock` changed.

- [ ] **Step 9: S2, the build and the API reference index page**

```bash
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture great-docs build </dev/null > ~/.cache/agent-skills/scratch/great-docs-spike/s2-build.log 2>&1; echo "exit $?"
grep -n -F -e 'Skipping API reference configuration' -e 'API reference skipped (non-Python project)' -e 'No documentable exports found' -e 'API reference disabled (reference: false), skipping' ~/.cache/agent-skills/scratch/great-docs-spike/s2-build.log
find ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture/great-docs -name index.html -path '*reference*'
tail -5 ~/.cache/agent-skills/scratch/great-docs-spike/s2-build.log
```

A build can take several minutes: give it a 10-minute timeout, or run it in the background. Expected: `exit 0`, no line from `grep`, and one path that ends in `great-docs/_site/reference/index.html`. `API_INDEX` is that path from the package root. A non-zero exit, or any of the four lines: stop and ask the owner (V1's S2 row). If the index page sits in another folder, Steps 10 to 17 use that site folder in place of `great-docs/_site`.

- [ ] **Step 10: S3a, whether docstring examples run**

```bash
find ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture/great-docs/_site/reference -name '*.html'
uv run --no-project --python 3.13 python -c "import html, re, sys; print(html.unescape(re.sub(r'<[^>]+>', '', open(sys.argv[1], encoding='utf-8').read())))" ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture/great-docs/_site/reference/summarize.html > ~/.cache/agent-skills/scratch/great-docs-spike/s3a-summarize.txt
grep -n -F -e 'summarize(pl.DataFrame' -e "'mean': 20.0" ~/.cache/agent-skills/scratch/great-docs-spike/s3a-summarize.txt
```

The second command prints the page's text without its HTML tags. Expected: the list holds `summarize.html` (if the page has another name, use that name). `grep` prints the example's code line and its output line with `'mean': 20.0`. Then `DOCSTRING_CELLS_RUN` = `yes`. The code line alone: `no`. Neither line: stop and ask the owner.

- [ ] **Step 11: S3b, a failing docstring cell**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md ~/.cache/agent-skills/scratch/great-docs-spike gdfixture/src/gdfixture/core.py:failing-example
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture great-docs build </dev/null > ~/.cache/agent-skills/scratch/great-docs-spike/s3-docstring.log 2>&1; echo "exit $?"
grep -n -i -E 'error|traceback|exception' ~/.cache/agent-skills/scratch/great-docs-spike/s3-docstring.log
grep -rl --include='*.html' -F -e 'cell-output-error' -e 'ColumnNotFoundError' ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture/great-docs/_site
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture checkout -- src/gdfixture/core.py
```

Expected: `edited gdfixture/src/gdfixture/core.py:failing-example`, the build's exit code, the log's error lines, and the pages that show the error. The record (Step 18) gets all three. The last command restores `core.py`. When `DOCSTRING_CELLS_RUN` is `no`, the cell never runs: record that, and only Step 12 decides `CELL_ERROR`.

- [ ] **Step 12: S3b, a failing page cell, then a clean build**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md ~/.cache/agent-skills/scratch/great-docs-spike gdfixture/user_guide/01-failing.qmd
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture great-docs build </dev/null > ~/.cache/agent-skills/scratch/great-docs-spike/s3-page.log 2>&1; echo "exit $?"
grep -n -i -E 'error|traceback|exception' ~/.cache/agent-skills/scratch/great-docs-spike/s3-page.log
grep -rl --include='*.html' -F -e 'cell-output-error' -e 'spike S3' ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture/great-docs/_site
rm ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture/user_guide/01-failing.qmd
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture great-docs build </dev/null > ~/.cache/agent-skills/scratch/great-docs-spike/s3-clean.log 2>&1; echo "exit $?"
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture status --short
grep -rl --include='*.html' -F 'cell-output-error' ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture/great-docs/_site
```

Expected: the failing build's exit code and error lines. Then `exit 0` for the clean build, no modified tracked file in the status, and no page that holds `cell-output-error`.

Then decide `CELL_ERROR` from Steps 11 and 12. A "failing build" is one whose cell ran and raised.

- `fails`: every failing build exited non-zero. `CELL_ERROR_MARKER` = `none`.
- `log`: a failing build exited 0, and its log has an error line that `s3-clean.log` lacks. `CELL_ERROR_MARKER` is a fixed phrase of that line that names nothing from the fixture (not `no_such_column`, `spike S3`, `RuntimeError` or `ColumnNotFoundError`). Check the phrase with `grep -c -F` on the three logs: at least 1 in each failing build's log that exited 0, and 0 in `s3-clean.log`.
- `site`: a failing build exited 0, its log has no such line, and its pages hold `cell-output-error`, the class that Quarto gives an error output. `CELL_ERROR_MARKER` = `cell-output-error`.
- Anything else: stop and ask the owner.

- [ ] **Step 13: S4, where the freeze cache lands**

```bash
find ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture -name _freeze -not -path '*/.venv/*'
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture status --short --ignored
```

Expected: `…/gdfixture/_freeze`, and the status line `?? _freeze/`. The cache sits at the package root, and git does not ignore it. Then `FREEZE_DIR` = `_freeze/`. If the only `_freeze` sits inside `great-docs/`, if the status shows it after `!!`, or if no `_freeze` exists: stop and ask the owner (DF21).

- [ ] **Step 14: S5, `default-groups` and the generated workflow**

```bash
uv sync --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture --no-default-groups --group dev
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture --no-sync python -c "import importlib.metadata as m; print(m.version('great-docs'))"
uv sync --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture --no-sync python -c "import importlib.metadata as m; print(m.version('great-docs'))"
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture great-docs setup-github-pages </dev/null > ~/.cache/agent-skills/scratch/great-docs-spike/s5-pages.log 2>&1; echo "exit $?"
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture status --short
grep -rn -E 'uv sync|uv pip install' ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture/.github/workflows
```

Expected: the first version check fails with `PackageNotFoundError`. That is the control: without the `docs` group, great-docs is absent. After the plain `uv sync`, the second check prints `0.17.0`. `setup-github-pages` exits 0 and writes a workflow under `.github/workflows/`, and `grep` shows a `uv sync` line and a `uv pip install great-docs` line. S5 then agrees with R4.2 and R4.8, and no Value changes. Stop and ask the owner (DF26) when the control prints a version, the plain sync does not install great-docs, `setup-github-pages` fails, or the workflow has no `uv pip install great-docs` line.

- [ ] **Step 15: S6, `ruff format` and `'''` docstrings**

```bash
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture ruff --version
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture ruff format --isolated --diff src > ~/.cache/agent-skills/scratch/great-docs-spike/s6-default.diff 2>&1; grep -c '^+ *"""' ~/.cache/agent-skills/scratch/great-docs-spike/s6-default.diff
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture ruff format --isolated --config "format.quote-style = 'single'" --diff src > ~/.cache/agent-skills/scratch/great-docs-spike/s6-single.diff 2>&1; grep -c '^+ *"""' ~/.cache/agent-skills/scratch/great-docs-spike/s6-single.diff
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture ruff format --isolated --config "format.quote-style = 'preserve'" --diff src > ~/.cache/agent-skills/scratch/great-docs-spike/s6-preserve.diff 2>&1; grep -c '^+ *"""' ~/.cache/agent-skills/scratch/great-docs-spike/s6-preserve.diff
```

`--isolated` ignores every ruff config file on the machine. Expected: the version of ruff that the fixture's lock holds, then three counts of added `"""` lines (planning found 11, 11 and 0 with ruff 0.17.1). `RUFF_REWRITES_DOCSTRINGS` follows from the counts:

- `no`: the default count is 0.
- `single`: the default count is above 0, and the `single` count is 0.
- `preserve`: the first two counts are above 0, and the `preserve` count is 0.
- `yes`: all three counts are above 0.

- [ ] **Step 16: S7, the completeness tool**

```bash
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture --with pydoclint pydoclint --version
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture --with pydoclint pydoclint --style=numpy --skip-checking-short-docstrings=False src/gdfixture; echo "exit $?"
cat ~/.cache/agent-skills/scratch/great-docs-spike/numpydoc-table.toml >> ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture/pyproject.toml
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture --with numpydoc python -c "import numpydoc; print(numpydoc.__version__)"
uv run --directory ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture --with numpydoc numpydoc lint $(git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture ls-files 'src/gdfixture/*.py'); echo "exit $?"
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture checkout -- pyproject.toml
```

Expected, as in planning with pydoclint 0.11.1 and numpydoc 1.11.0: pydoclint exits 1 with DOC101 and DOC103 on `scale` and DOC201 and DOC203 on `Ratio.inverse`. numpydoc exits 1 with PR01 on `scale`, RT01 on `Ratio.inverse` and GL08 on `Ratio.as_tuple`. The last command takes the numpydoc table back out of `pyproject.toml`.

Choose the tool by DF20. With the planning results, numpydoc qualifies and also reports `Ratio.as_tuple`, so it wins. The Values for each choice, where `X.Y` is the major and minor part of the version found:

| `COMPLETENESS_TOOL` | `COMPLETENESS_PIN` | `COMPLETENESS_COMMAND` |
|---|---|---|
| `numpydoc` | `numpydoc>=X.Y` | `uv run numpydoc lint $(git ls-files '<package-dir>/*.py')` |
| `pydoclint` | `pydoclint>=X.Y` | `uv run pydoclint --style=numpy --skip-checking-short-docstrings=False <package-dir>` |

- [ ] **Step 17: S8, the README on the built site**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/great-docs-spike/inspect_site.py ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture/great-docs/_site/index.html
```

Expected: two badge lines that say `in a hero`, then the meta description, the three texts it could come from, and `meta source: readme`. The Values:

- `HERO_BADGES` = `yes` when every badge line says `in a hero`. When none does, read the ancestor classes. If a container with another name does the hero's job, stop and ask the owner. Otherwise `no`.
- `meta source: readme`: `META_FROM_FIRST_PARAGRAPH` = `yes` and `META_SOURCE` = `none`.
- `meta source: pyproject`: `no` and `the description field of pyproject.toml`.
- `meta source: module docstring`: `no` and `the package's module docstring`.
- `meta source: other`: stop and ask the owner.

- [ ] **Step 18: Write the spike record**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md . specs/verification/57-great-docs-0.17.0.md
```

Expected: `wrote specs/verification/57-great-docs-0.17.0.md`. Replace each `TO-RECORD` with what Steps 1 and 7 to 17 found. Each answer quotes the lines that it rests on, and no line holds the user's email address or a token. Then check that the Values table fills the skill text:

```bash
grep -c TO-RECORD specs/verification/57-great-docs-0.17.0.md
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md /tmp/dpp-fill-check skills/document-python-package/SKILL.md
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/fill_slots.py specs/verification/57-great-docs-0.17.0.md /tmp/dpp-fill-check/skills/document-python-package/SKILL.md
```

Expected: `0`, `wrote skills/document-python-package/SKILL.md`, then `filled /tmp/dpp-fill-check/skills/document-python-package/SKILL.md`. An error names the key to fix in the table.

- [ ] **Step 19: Amend the spec with the spike's answers**

Apply the five blocks that every spike needs, then the blocks that the Values choose, in this table's order. Each key is `specs/document-python-package-spec.md:` and the label.

| Values key | Value | Labels |
|---|---|---|
| (every spike) | | `results`, `s2-index`, `s4-freeze`, `s7-pin`, `s7-gate` |
| `INIT_DEFAULT_WORKS` | `yes` | none |
| | `no` | `s1-init` |
| `DOCSTRING_CELLS_RUN` | `yes` | `s3-docstrings-run` |
| | `no` | `s3-docstrings-shown` |
| `CELL_ERROR` | `fails` | none |
| | `log` | `s3-four-checks`, `s3-log` |
| | `site` | `s3-four-checks`, `s3-site` |
| `RUFF_REWRITES_DOCSTRINGS` | `no`, `single`, `preserve` or `yes` | `s6-no`, `s6-single`, `s6-preserve` or `s6-yes` |
| `COMPLETENESS_TOOL` | `pydoclint` | none |
| | `numpydoc` | `s7-numpydoc-config` |
| `HERO_BADGES` | `yes` or `no` | `s8-hero-yes` or `s8-hero-no` |
| `META_FROM_FIRST_PARAGRAPH` | `yes` or `no` | `s8-meta-yes` or `s8-meta-no` |

With the planning results, the command is the one below. With other Values, change only the labels after `s7-gate`:

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md . specs/document-python-package-spec.md:results specs/document-python-package-spec.md:s2-index specs/document-python-package-spec.md:s4-freeze specs/document-python-package-spec.md:s7-pin specs/document-python-package-spec.md:s7-gate specs/document-python-package-spec.md:s3-docstrings-run specs/document-python-package-spec.md:s6-preserve specs/document-python-package-spec.md:s7-numpydoc-config specs/document-python-package-spec.md:s8-hero-yes specs/document-python-package-spec.md:s8-meta-yes
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/fill_slots.py specs/verification/57-great-docs-0.17.0.md specs/document-python-package-spec.md
grep -c '{{' specs/document-python-package-spec.md
git diff --stat
bash build/run_commit_lints.sh
git add specs/document-python-package-spec.md specs/verification/57-great-docs-0.17.0.md
git commit -m "docs(specs): record spike S1 to S8 for document-python-package" -m "Plan 57's spike ran great-docs 0.17.0 on a scratch fixture package. The record is specs/verification/57-great-docs-0.17.0.md. Each requirement that an answer changed now carries that answer's spike tag."
```

Expected: one `edited` line for each block, `filled specs/document-python-package-spec.md`, `0`, the spec alone in the diff (the record is not yet tracked), and `commit lints passed`. Read the spec's diff before the commit: each changed requirement must say what the record says.

### Task 2: The RED baseline

**Files:**
- Create, outside the repository: the kit in `KIT` (Appendix D), and `KIT/artifacts/pyproject-fresh.toml` and `KIT/artifacts/init.py`, copied from the fixture. Commands make `KIT/bin/`, `KIT/prompts/red/` and `KIT/out/red/`.
- Create: `specs/verification/57-document-python-package-skill-tests.md` (Appendix B), with its Setup and RED sections filled.

**Interfaces:**
- Consumes: `FIX` at tag `pristine` (Task 1).
- Produces: `KIT/run.py`, `KIT/build_prompts.py`, `KIT/show.py`, `KIT/transcript.py` and `KIT/gate.py`, which Task 4 runs. `KIT/RESULTS.md` with the RED verdicts, and the list of items that RED showed (decision rule 1), which Task 4's decision rules use.

- [ ] **Step 1: Check that no skill text exists yet**

```bash
test -e skills/document-python-package && echo 'SKILL FOLDER EXISTS'
ls ~/.claude/skills/ | grep -c document-python-package
```

Expected: no `SKILL FOLDER EXISTS` line, then `0`. Otherwise stop and ask the owner: RED must run with no skill text anywhere (spec, Sequencing item 3).

- [ ] **Step 2: Write the kit**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md ~/.cache/agent-skills/scratch/document-python-package-kit run.py build_prompts.py show.py transcript.py gate.py PREREGISTRATION.md RESULTS.md scenarios/answer-format.md scenarios/sc1-setup.md scenarios/sc2-deploy.md scenarios/sc3-done.md scenarios/sc4-mcmc.md scenarios/sc5-official-skills.md artifacts/pyproject-pinned.toml artifacts/docs-workflow.yml artifacts/build-tail.txt artifacts/lint-output.txt
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture show pristine:pyproject.toml > ~/.cache/agent-skills/scratch/document-python-package-kit/artifacts/pyproject-fresh.toml
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture show pristine:src/gdfixture/__init__.py > ~/.cache/agent-skills/scratch/document-python-package-kit/artifacts/init.py
```

Expected: 17 `wrote` lines, and no output from the two copies.

- [ ] **Step 3: Check the scenarios for the skill's own words**

A scenario that holds the skill's words could meet its answer in the skill text.

```bash
grep -ril -e 'document-python-package' -e 'preflight' ~/.cache/agent-skills/scratch/document-python-package-kit/scenarios ~/.cache/agent-skills/scratch/document-python-package-kit/artifacts
```

Expected: no output.

- [ ] **Step 4: Hold the binary, and probe it**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/run.py hold
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/run.py probe
```

Expected: `held <version> from <path>`, then `result='OK' is_error=False`, a model list that holds `claude-opus-5-5`, and a cost of a few cents. Another result: stop and ask the owner. Every later call runs this held copy, so a Claude Code update during the tests changes nothing.

- [ ] **Step 5: Build and run the RED arm**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/build_prompts.py red
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/run.py red
```

Expected: five lines `red/scN-….txt: N chars`, then 25 reply lines and `red: $X.XX so far`. Run the second command in the background: 25 calls take about 5 to 10 minutes and cost about $2 to $4. A `FAILED` line: run the same command again, which fills only the gaps.

- [ ] **Step 6: Read every reply**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/show.py red sc1-setup
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/show.py red sc2-deploy
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/show.py red sc3-done
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/show.py red sc4-mcmc
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/show.py red sc5-official-skills
```

Read each reply in full, as `KIT/PREREGISTRATION.md`'s Reading section says. Record every verdict in the RED table of `KIT/RESULTS.md`, with a quote for each `yes`. A reply marked `VOID`: delete its JSON file in `KIT/out/red/`, and run Step 5's second command again.

- [ ] **Step 7: Apply decision rules 1 and 2**

Fill the RED columns of `KIT/RESULTS.md`'s Summary table. If no M item shows (rule 1), stop and ask the owner. Otherwise note the items that showed. Task 4 checks that each of them flips.

- [ ] **Step 8: Record RED, and commit**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md . specs/verification/57-document-python-package-skill-tests.md
```

Expected: `wrote specs/verification/57-document-python-package-skill-tests.md`. Fill its Setup table, except GREEN's row, from `KIT/bin/VERSION` and Step 5's cost line. Fill its RED section from `KIT/RESULTS.md`: each item's count out of 5 in its own scenario, one quote for each item that showed, and the decision under rules 1 and 2. Leave the later sections' `TO-RECORD` markers for Task 4.

```bash
bash build/run_commit_lints.sh
git add specs/verification/57-document-python-package-skill-tests.md
git commit -m "docs(verification): record the RED baseline for document-python-package" -m "Plan 57, Task 2: five scenarios, five decision-only claude -p replies each, with no skill text anywhere. The record lists the mistakes that the skill text must answer."
```

Expected: `commit lints passed`. The commit lands before SKILL.md exists, so the history shows that RED came first.

### Task 3: The skill bundle

**Files:**
- Create: `skills/document-python-package/scripts/test_preflight.py`, `skills/document-python-package/scripts/preflight.py` and `skills/document-python-package/SKILL.md` (Appendix B), and `skills/document-python-package/LICENSE` (a copy of the root `LICENSE`)
- Modify: `build/suites.toml`, `NOTICE` and `CLAUDE.md` (Appendix C)
- Test: `skills/document-python-package/scripts/test_preflight.py`

**Interfaces:**
- Consumes: the spike record's Values table (Task 1), `KIT/fill_slots.py` and the RED commit (Task 2).
- Produces: the committed skill, which Task 4 tests from `"$PWD"/skills/document-python-package`. `preflight.py`'s report: the keys `great-docs`, `range`, `in-range`, `layout`, `config`, `quarto` and `skills`, then `next:` with `pin`, `init`, `ready` or `stop: <reason>`. Exit 0, or 1 on a stop.

- [ ] **Step 1: Check the inputs**

```bash
grep -c TO-RECORD specs/verification/57-great-docs-0.17.0.md
git log --oneline -4
```

Expected: `0`, and the RED commit at the top, above the spike commit.

- [ ] **Step 2: Register the suite, and write the failing test**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md . build/suites.toml:suite skills/document-python-package/scripts/test_preflight.py
uv run --python 3.13 python build/run_suites.py document-python-package
```

Expected: `edited build/suites.toml:suite` and `wrote skills/document-python-package/scripts/test_preflight.py`. Then the suite's note and `1 error`: collection fails with `ModuleNotFoundError: No module named 'preflight'`.

- [ ] **Step 3: Write `preflight.py`**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md . skills/document-python-package/scripts/preflight.py
```

Expected: `wrote skills/document-python-package/scripts/preflight.py`.

- [ ] **Step 4: Run the tests on Python 3.13 and on the floor, 3.11**

```bash
uv run --python 3.13 python build/run_suites.py document-python-package
uv run --directory skills/document-python-package/scripts --python 3.11 --with pytest python -m pytest -q -p no:cacheprovider
```

Expected: `24 passed` twice (+24, a new suite). The second run checks the `requires-python` floor.

- [ ] **Step 5: Run the real script on the fixture's two states**

This run uses the real network fetch, which the tests replace with a local repository. `UV_CACHE_DIR` keeps uv's own cache, because a changed `XDG_CACHE_HOME` would move it.

```bash
rm -rf /tmp/dpp-preflight
mkdir -p /tmp/dpp-preflight/pristine /tmp/dpp-preflight/configured
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture archive pristine | tar -x -C /tmp/dpp-preflight/pristine
git -C ~/.cache/agent-skills/scratch/great-docs-spike/gdfixture archive configured | tar -x -C /tmp/dpp-preflight/configured
UV_CACHE_DIR="$(uv cache dir)" XDG_CACHE_HOME=/tmp/dpp-preflight/xdg uv run --directory /tmp/dpp-preflight/pristine "$PWD"/skills/document-python-package/scripts/preflight.py; echo "exit $?"
UV_CACHE_DIR="$(uv cache dir)" XDG_CACHE_HOME=/tmp/dpp-preflight/xdg uv run --directory /tmp/dpp-preflight/configured "$PWD"/skills/document-python-package/scripts/preflight.py; echo "exit $?"
cat /tmp/dpp-preflight/xdg/agent-skills/great-docs/0.17.0/SOURCE
ls /tmp/dpp-preflight/xdg/agent-skills/great-docs/0.17.0/skills
```

Expected, for `pristine`:

```text
great-docs: none
range: >=0.17.0,<0.18
in-range: none
layout: none
config: none
quarto: 1.10.19
skills: none
next: pin
exit 0
```

For `configured`:

```text
great-docs: 0.17.0
range: >=0.17.0,<0.18
in-range: yes
layout: root
config: great-docs.yml
quarto: 1.10.19
skills: /tmp/dpp-preflight/xdg/agent-skills/great-docs/0.17.0/skills
next: ready
exit 0
```

Then `SOURCE` holds `tag: v0.17.0`, `commit: 1ce8eb88191df75405345b6ba2d35bea53a4f7f6` and a `fetched:` time, and `ls` shows `author-skills`, `configure-site`, `great-docs`, `revise-docstrings` and `write-user-guide`. The Quarto line shows the version on `PATH`. Another commit: stop and ask the owner, because the tag moved after the spec read it.

- [ ] **Step 6: Write the skill text from the spike's Values**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md . skills/document-python-package/SKILL.md
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/fill_slots.py specs/verification/57-great-docs-0.17.0.md skills/document-python-package/SKILL.md
grep -c '{{' skills/document-python-package/SKILL.md
cp LICENSE skills/document-python-package/LICENSE
cmp LICENSE skills/document-python-package/LICENSE
```

Expected: `wrote skills/document-python-package/SKILL.md`, `filled skills/document-python-package/SKILL.md`, `0`, and no output from `cmp`. Read the filled SKILL.md once in full: each filled sentence must agree with the spike record.

- [ ] **Step 7: Record the provenance**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md . NOTICE:originals NOTICE:paragraph CLAUDE.md:originals
```

Expected: three `edited` lines. NOTICE's new paragraph is the wording that the owner approved in R6.1.

- [ ] **Step 8: Check the sizes**

```bash
wc -l skills/document-python-package/SKILL.md
uv run --no-project --python 3.13 python -c "import re, sys; t = open(sys.argv[1], encoding='utf-8').read(); print(len(re.sub(r'^---\n.*?\n---\n', '', t, count=1, flags=re.S)))" skills/document-python-package/SKILL.md
```

Expected: about 190 lines (the limit is 500) and about 8,000 characters (the limit is 20,000).

- [ ] **Step 9: Run the checks**

```bash
uv run --no-project --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --no-project --python 3.13 python build/check_provenance.py
uv run --no-project --python 3.13 python build/check_snippets.py skills/
uv run --no-project --python 3.13 --with pyyaml python build/check_conformance.py
uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies
git add -A skills/document-python-package NOTICE CLAUDE.md build/suites.toml
uv run --no-project --python 3.13 python build/cc_guide/cli.py lint
bash build/run_commit_lints.sh
```

Expected: no output from the frontmatter, provenance and conformance checks. The snippet check prints only its five existing `WARN` lines. The drift test passes, so SKILL.md's hand-offs to `docs-writer` and `write-with-asd-ste100` need no `DEPENDENCIES` entry (R6.6). `cli.py lint` prints no `FAIL` (its `STALE` lines never fail it), and the last line is `commit lints passed`. If plan 53 has landed (Task 1, Step 2), its lints run here too: a finding on this bundle is a stop, so ask the owner.

- [ ] **Step 10: Commit the bundle**

```bash
git commit -m "feat(skills): add document-python-package" -m "A thin layer over Posit's five official Great Docs skills for great-docs 0.17.x. A tested stdlib preflight checks the locked version, finds the config and fetches the official skills from the matching release tag into a cache. SKILL.md adds the pin, init, README, executed-example and deploy conventions and a three-check done gate. NOTICE and CLAUDE.md record the skill as an original work, and build/suites.toml registers its tests."
git log -1 --format=%B
```

Expected: one commit with the whole bundle, and the commit trailer at the end of the message.

### Task 4: GREEN, the trigger test and the end-to-end run

**Files:**
- Modify: `skills/document-python-package/SKILL.md`, only when a decision rule calls for a wording change
- Modify: `specs/verification/57-document-python-package-skill-tests.md` (the sections after RED)
- Outside the repository: `KIT/prompts/` and `KIT/out/` for the arms `green`, `green-r1`, `green-r2`, `trigger`, `trigger-r1` and `e2e`, and the run folders under `/tmp/dpp-trigger/` and `/tmp/dpp-e2e/`

**Interfaces:**
- Consumes: the committed skill (Task 3), the kit and the RED verdicts (Task 2), the fixture's tags (Task 1).
- Produces: the GREEN, trigger and end-to-end results in the skill-test record, which Task 6 reports.

- [ ] **Step 1: Build and run the GREEN arm**

```bash
ls ~/.claude/skills/ | grep -c document-python-package
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/build_prompts.py green "$PWD"/skills/document-python-package/SKILL.md
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/run.py green
```

Expected: `0` (still no user-level copy), five `green/scN-….txt` lines, then 25 reply lines and the arm's cost. Run the last command in the background, as in Task 2.

- [ ] **Step 2: Read every GREEN reply, and apply decision rule 3**

Run `show.py green <scenario>` for each of the five scenarios, as in Task 2, Step 6. Record every verdict in the GREEN table of `KIT/RESULTS.md`, then fill the Summary's GREEN columns. Rule 3 passes when each item that RED showed occurs in 0 of its own scenario's 5 replies, and no item occurs where RED never had it. When it passes, skip Step 3.

- [ ] **Step 3: REFACTOR, only when rule 3 fails**

For each failing item, change the SKILL.md wording that covers it (rule 4). The change answers the replies that failed, stays inside the spec, and keeps the Global Constraints' frontmatter and length limits. Then run Task 3, Step 9's checks and commit:

```bash
git add skills/document-python-package/SKILL.md
git commit -m "fix(document-python-package): sharpen the wording for one GREEN failure" -m "Names the item from the skill-test record, the replies that failed and the sentence that changed."
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/build_prompts.py green-r1 "$PWD"/skills/document-python-package/SKILL.md
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/run.py green-r1 sc3-done
```

Write the commit's second line for the actual item. The last command runs only the failing scenarios: replace `sc3-done` with their names. Read and record the replies as in Step 2. A second failure gets one more round under the arm `green-r2`. A third: stop and ask the owner.

- [ ] **Step 4: Run the trigger test**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/run.py trigger trigger "$PWD"/skills/document-python-package
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/transcript.py skills ~/.cache/agent-skills/scratch/document-python-package-kit/out/trigger/t1.jsonl ~/.cache/agent-skills/scratch/document-python-package-kit/out/trigger/t2.jsonl ~/.cache/agent-skills/scratch/document-python-package-kit/out/trigger/t3.jsonl ~/.cache/agent-skills/scratch/document-python-package-kit/out/trigger/t4.jsonl ~/.cache/agent-skills/scratch/document-python-package-kit/out/trigger/t5.jsonl
```

Expected: five `tN.jsonl exit N` lines (a call that reaches `--max-turns` can exit 1, which does not matter here), then `t1: listed, TRIGGERED` to `t4: listed, TRIGGERED`, and `t5: listed, not triggered`. The five calls cost about $1.50. A `NOT LISTED` line makes that call void: look at its staged repo under `/tmp/dpp-trigger/trigger/`, delete its transcript, and run the first command again. Record the results in `KIT/RESULTS.md`.

If a query's result is wrong, revise the description once. The revision keeps every description rule in Global Constraints. Run Task 3, Step 9's checks, commit with the message `fix(document-python-package): revise the description after the trigger test`, and run both commands again with the arm `trigger-r1` in place of `trigger` (in the first command's first argument and in the five paths). A second failure: stop and ask the owner.

- [ ] **Step 5: Run the end-to-end test**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/run.py e2e e2e-1 "$PWD"/skills/document-python-package
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/transcript.py e2e ~/.cache/agent-skills/scratch/document-python-package-kit/out/e2e/e2e-1.jsonl
```

Run the first command in the background. It can take up to an hour, and `--max-budget-usd 15` bounds its cost. Expected: `e2e-1.jsonl exit 0`, then the numbered tool calls, no `VOID` line, and the result record with the run's final message. Then check the run's repo yourself (E7):

```bash
git -C /tmp/dpp-e2e/e2e-1/gdfixture status --short
git -C /tmp/dpp-e2e/e2e-1/gdfixture diff
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/gate.py specs/verification/57-great-docs-0.17.0.md /tmp/dpp-e2e/e2e-1/gdfixture src/gdfixture; echo "exit $?"
```

Expected: the files that the run changed, and the gate's three lines. When the final message calls the docs done, all three say `PASS` and the exit is 0. Otherwise each check that the message names as failing says `FAIL`. Judge E1 to E7 (`PREREGISTRATION.md`) and record each in `KIT/RESULTS.md` with its evidence. A void run is repeated once as `e2e-2`. A second void run: stop and ask the owner. A failed criterion gets one wording change (as in Step 3) and one more run, `e2e-r1`. A second failure: stop and ask the owner.

- [ ] **Step 6: Record and commit**

Fill the skill-test record's remaining `TO-RECORD` markers from `KIT/RESULTS.md`: the GREEN row of Setup, then GREEN (each item's count against RED), REFACTOR ("None: GREEN passed in its first run" when no round ran), the trigger test, the end-to-end run, and a verdict of one or two sentences.

```bash
grep -c TO-RECORD specs/verification/57-document-python-package-skill-tests.md
bash build/run_commit_lints.sh
git add specs/verification/57-document-python-package-skill-tests.md
git commit -m "docs(verification): record GREEN and the live tests for document-python-package" -m "Plan 57, Task 4: GREEN against the RED baseline, the five-query trigger test and one end-to-end run on the fixture package."
```

Expected: `0`, then `commit lints passed`.

### Task 5: The README row, the ADR bullet and plan 53's line

**Files:**
- Modify: `README.md`, `skills/design-architecture/SKILL.md` and, when plan 53 has not run, `specs/plans/53-agent-skills-portability.md` (Appendix C)

**Interfaces:**
- Consumes: the committed skill (Task 3) and plan 53's status (Task 1, Step 2).
- Produces: the README row (R6.3), the ADR bullet (R6.4, the spec's D6) and the D8 line (the spec's D8).

- [ ] **Step 1: Add the README row and the ADR bullet**

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md . README.md:row skills/design-architecture/SKILL.md:adr-bullet
```

Expected: two `edited` lines. The ADR bullet is the spec's wording, word for word. `scripts/new_adr.py` does not change (R6.4).

- [ ] **Step 2: Add the D8 line to plan 53, only when plan 53 has not run**

Run Task 1, Step 2's three commands again. When they print `plan 53 is live`, `0` and nothing, add the line and give it today's date:

```bash
uv run --no-project --python 3.13 python ~/.cache/agent-skills/scratch/document-python-package-kit/extract_plan_files.py specs/plans/57-document-python-package.md . specs/plans/53-agent-skills-portability.md:d8-line
uv run --no-project --python 3.13 python -c "import datetime, pathlib; p = pathlib.Path('specs/plans/53-agent-skills-portability.md'); t = p.read_text(encoding='utf-8'); assert t.count('(plan 57, DATE,') == 1; p.write_text(t.replace('(plan 57, DATE,', f'(plan 57, {datetime.date.today()},'), encoding='utf-8')"
grep -n 'document-python-package landed first' specs/plans/53-agent-skills-portability.md
```

Expected: `edited specs/plans/53-agent-skills-portability.md:d8-line`, no output from the second command, and one line in plan 53's Global Constraints with today's date. When plan 53 has run, skip this step, and write `> Skipped: plan 53 ran first, so the spec's D8 needs no line.` under it.

- [ ] **Step 3: Run the checks, and commit**

```bash
uv run --no-project --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --no-project --python 3.13 --with pyyaml python build/check_conformance.py
git add README.md skills/design-architecture/SKILL.md specs/plans/53-agent-skills-portability.md
uv run --no-project --python 3.13 python build/cc_guide/cli.py lint
bash build/run_commit_lints.sh
git commit -m "docs: list document-python-package, and route ADRs in Great Docs repos" -m "README.md gets the skill's row. design-architecture keeps ADRs in specs/adr/ when the repo publishes a Great Docs site (the skill's spec, D6). Plan 53 learns that this skill landed first (the spec's D8)."
```

Expected: no output from the two checks, no `FAIL` from `cli.py lint`, and `commit lints passed`. When Step 2 was skipped, drop plan 53's file from `git add` and the last sentence from the message.

### Task 6: Acceptance (V4)

**Files:** none changed.

**Interfaces:**
- Consumes: every earlier task's commits.
- Produces: the evidence for V4, the spec's repo gates, and the report to the owner.

- [ ] **Step 1: Run the new suite, the drift test and the `build` suite**

```bash
uv run --python 3.13 python build/run_suites.py document-python-package
uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies
uv run --python 3.13 python build/run_suites.py build
```

Expected: `24 passed` (+24), the drift test passes, and the `build` suite's passed count equals Task 1, Step 1's (+0), with the same 4 known failures.

- [ ] **Step 2: Run the commit lints on a clean clone**

A clean clone has no untracked file that could hide a missing one. `run_commit_lints.sh` takes its root from the folder that it runs in, so the second command runs it from inside the clone.

```bash
rm -rf /tmp/dpp-v4
git clone --quiet --branch "$(git branch --show-current)" "$PWD" /tmp/dpp-v4
bash -c 'cd /tmp/dpp-v4 && bash build/run_commit_lints.sh'
uv run --python 3.13 python /tmp/dpp-v4/build/run_suites.py document-python-package
```

Expected: `commit lints passed`, then `24 passed`.

- [ ] **Step 3: Report to the owner**

Give the owner, in plain words:

1. The spike's answers, and each spec change they made (the spike record).
2. RED and GREEN for each item, any REFACTOR round, the trigger test and the end-to-end run (the skill-test record).
3. V4's results from Steps 1 and 2.
4. The commits on the branch, unpushed.

Then go to "Plan completion". Push or merge nothing without the owner's go-ahead.

## Self-review

- **Spec coverage.** Purpose and the four additions: SKILL.md (Appendix B) with `preflight.py`, the conventions, the gate and the hand-offs. "Why a layer is needed": SKILL.md's opening and its override table. D1 to D8 (the spec's decisions): public hosts in the skill's scope line (D1), the version-keyed cache in `preflight.py` (D2), the range and its stop (D3), the three-check gate with non-blocking `check-links` and `proofread` (D4), no curation step and `author-skills` only on request (D5), the ADR bullet in Task 5 (D6), SKILL.md plus one tested script (D7), and the plan 53 line in Task 5 (D8). R1 (files and frontmatter): Task 3 and Global Constraints, with R1.4 through Q1 and A2. R2 (authority): SKILL.md's "Which text wins". R3 (the preflight): Appendix B's script and its 24 tests, and Task 3, Step 5's real fetch. R4 (workflow): SKILL.md's sections, with the spike's values. R5 (stops): the preflight's `stop:` lines and the gate's failure rule. R6 (repo integration): Task 3 (NOTICE, CLAUDE.md, the suite, no `DEPENDENCIES` entry) and Task 5 (README.md, design-architecture). Sequencing: Global Constraints' Order line and the task order, with A1 for item 5. V1: Task 1. V2: Appendix B's tests. V3: Tasks 2 and 4, `PREREGISTRATION.md`. V4: Task 6. Out of scope: the deferred items in "Plan completion".
- **Placeholders.** `{{KEY}}` slots are execution-time values from the spike record, by design (Global Constraints). `TO-RECORD` markers belong to the two record skeletons, and Tasks 1, 2 and 4 check that none is left. Angle-bracket fields in prose (`<version>`, `<package-dir>`) name a value that the same step prints or defines.
- **Names across tasks.** `KIT`, `SPIKE`, `FIX`, the tags `pristine` and `configured`, the Values keys, the arms `red`, `green`, `green-r1`, `green-r2`, `trigger`, `trigger-r1` and `e2e`, the block keys, and the functions `locked_version`, `in_range`, `config_layout`, `quarto_version`, `cache_root`, `fetch_skills` and `next_step` match between the tasks and the appendices.
- **Plan review.** D3 logs Q1's option (c) with amendments A1 and A2, and D4 logs DF1 to DF28 as written. Neither changes a task, because the plan already carried (c), A1, A2 and the defaults.

## Execution handoff

Recommended: **Inline Execution**, with the executing-plans skill, in a fresh Sonnet session (D1). As in plan 52, the tasks that test things are one measurement campaign:

- RED (Task 2) and GREEN (Task 4) compare only when one reader applies `PREREGISTRATION.md`'s reading rules to both arms.
- The spike's builds and the kit's runs take minutes to an hour, in the background. The session that starts a run must wait for it and read it.
- Tasks 1, 2 and 4 hold stops that go to the owner.

The cost is context: one session reads the spike's logs and about 50 replies.

The execution worktree must hold this plan and the spec's commits, which today sit only on `claude/great-docs-skill-design-19335c` (D2). After the owner merges that branch into `main`, make the worktree by hand:

```bash
git -C ~/Projects/agent-skills worktree add -b feat/document-python-package .claude/worktrees/document-python-package main
```

Then, in a terminal:

```bash
cd ~/Projects/agent-skills/.claude/worktrees/document-python-package && claude --model sonnet
```

First message: "Execute specs/plans/57-document-python-package.md with the executing-plans skill, from Task 1."

If the owner chooses Subagent-Driven instead, the first message names the subagent-driven-development skill. Tasks 1, 2 and 4 then stay with the controller, which runs the spike and the kit and reads every reply itself. Subagents take Tasks 3, 5 and 6. Tasks 3 and 5 write their files with the extractor from this plan file, so `task-brief` needs no appendix text. The controller relays every "stop and ask the owner" to the owner, and it never decides one itself.

## Plan completion

Run writing-plans' Plan Completion Protocol after Task 6 and the final review, before finishing-a-development-branch. Append these items to `specs/deferred_items.md` under `## 57-document-python-package — <date>`, with any leftovers from execution:

- [ ] A new spike for great-docs 0.18 (the spec's Out of scope: the post-migration `docs/` layout). The skill stops on any version outside `>=0.17.0,<0.18` and on a `docs` or `both` layout. Widening the range takes a new spike against the new release, a new range in `skills/document-python-package/scripts/preflight.py` (`LOWEST`, `FIRST_EXCLUDED`, `RANGE`) and in SKILL.md, and a check of the five official skills at the new tag. Size: plan. Revisit if: PyPI publishes great-docs 0.18.0 or later.
- [ ] Internal hosts and package indexes (the spec's D1 and Out of scope). The skill covers github.com, PyPI and GitHub Pages only. Size: design. Revisit if: the owner documents a package that is not public.
- [ ] A gate check for stale frozen examples (D11). great-docs 0.17.0 freezes every executed page by default (`Freeze mode: auto`), docstring examples included. After a change to a function's body with its docstring unchanged, `uv run great-docs build` exits 0 and the page shows the stale frozen output, so the gate's build check passes a broken example. A fix might build with `freeze: false` in `great-docs.yml` inside the gate, or check the examples another way. Evidence: the spike record's S3 (`specs/verification/57-great-docs-0.17.0.md`). Size: design. Revisit if: an agent or a user ships a docstring example that no longer runs, or the owner wants the gate to prove that every example runs.
- [ ] Curating the package's published `SKILL.md` (the spec's D5 and Out of scope). Great Docs publishes one by default, and this skill keeps that default with no review step. Size: design. Revisit if: the owner wants to review or edit the generated skill.

---
## Appendix A: the extractor

Task 1, Step 3 holds `extract_plan_files.py`, because every later block needs it. It is plan 52's extractor, unchanged.

## Appendix B: new repository files

### `skills/document-python-package/scripts/test_preflight.py` (Task 3, Step 2)

The tests are V2's list, with stdlib and pytest only and no network. The fetch tests clone a local bare repository through a `file://` URL, so git applies `--depth` and `--filter` as it does against GitHub. `PATH` holds only a link to git and a fake `quarto`, so a test can take Quarto away.

<!-- extract-file: skills/document-python-package/scripts/test_preflight.py -->
```python
'''Tests for preflight.py: stdlib and pytest only, no network.

The fetch tests clone a local bare repository through a file:// URL, so that
git applies --depth and --filter as it does against GitHub. PATH holds only a
link to git and a fake quarto, so a test can take Quarto away.
'''
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

import preflight

GIT = shutil.which('git')
QUARTO_VERSION = '1.10.19'
TAG = 'v0.17.0'
STOP_FETCH = 'next: stop: fetching the official skills failed: '


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True,
                          text=True).stdout.strip()


def fake_quarto(bin_dir: Path, version: str) -> None:
    quarto = bin_dir / 'quarto'
    quarto.write_text(f'#!/bin/sh\necho {version}\n')
    quarto.chmod(0o755)


@pytest.fixture(autouse=True)
def pkg(tmp_path, monkeypatch):
    '''An empty package root as the working directory, a scratch cache, git
    with no user or system config, and a PATH of git and a fake quarto.'''
    root = tmp_path / 'pkg'
    root.mkdir()
    monkeypatch.chdir(root)
    monkeypatch.setenv('XDG_CACHE_HOME', str(tmp_path / 'cache'))
    (tmp_path / 'gitconfig').write_text('')
    monkeypatch.setenv('GIT_CONFIG_GLOBAL', str(tmp_path / 'gitconfig'))
    monkeypatch.setenv('GIT_CONFIG_NOSYSTEM', '1')
    for role in ('AUTHOR', 'COMMITTER'):
        monkeypatch.setenv(f'GIT_{role}_NAME', 'Test')
        monkeypatch.setenv(f'GIT_{role}_EMAIL', 'test@example.com')
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    (bin_dir / 'git').symlink_to(GIT)
    fake_quarto(bin_dir, QUARTO_VERSION)
    monkeypatch.setenv('PATH', str(bin_dir))
    return root


@pytest.fixture
def bare(tmp_path) -> Path:
    '''A bare repository with an annotated tag v0.17.0 on a tree that holds
    skills/ and one file outside it.'''
    work = tmp_path / 'work'
    (work / 'skills' / 'great-docs').mkdir(parents=True)
    (work / 'skills' / 'great-docs' / 'SKILL.md').write_text('---\nname: great-docs\n---\n')
    (work / 'README.md').write_text('outside skills/\n')
    git('init', '--quiet', '--initial-branch', 'main', cwd=work)
    git('add', '.', cwd=work)
    git('commit', '--quiet', '--message', 'skills', cwd=work)
    git('tag', '--annotate', TAG, '--message', TAG, cwd=work)
    remote = tmp_path / 'remote.git'
    git('clone', '--quiet', '--bare', str(work), str(remote), cwd=tmp_path)
    git('config', 'uploadpack.allowFilter', 'true', cwd=remote)
    return remote


def lock(root: Path, version: str | None) -> None:
    '''Write root/uv.lock; None leaves great-docs out of it.'''
    entries = ['[[package]]\nname = "polars"\nversion = "1.0.0"\n']
    if version is not None:
        entries.append(f'[[package]]\nname = "great-docs"\nversion = "{version}"\n')
    (root / 'uv.lock').write_text('version = 1\n\n' + '\n'.join(entries))


def cache_dir(tmp_path: Path) -> Path:
    return tmp_path / 'cache' / 'agent-skills' / 'great-docs' / '0.17.0'


def report(version: str = 'none', in_range: str = 'none', layout: str = 'none', config: str = 'none',
           quarto: str = QUARTO_VERSION, skills: str = 'none', step: str = 'pin') -> list[str]:
    return [f'great-docs: {version}', 'range: >=0.17.0,<0.18', f'in-range: {in_range}',
            f'layout: {layout}', f'config: {config}', f'quarto: {quarto}', f'skills: {skills}',
            f'next: {step}']


def run(capsys, *argv: str) -> tuple[int, list[str]]:
    code = preflight.main(list(argv))
    return code, capsys.readouterr().out.splitlines()


@pytest.mark.parametrize(('version', 'expected'), [
    ('0.16.9', False), ('0.17.0', True), ('0.17.5', True), ('0.18.0', False),
    ('0.18.0rc1', False), ('0.17.1.dev0', False), ('0.17.1+local', False),
])
def test_only_a_final_release_inside_the_range_passes(version, expected):
    assert preflight.in_range(version) is expected


def test_no_lock_gives_pin(capsys):
    assert run(capsys) == (0, report())


def test_a_lock_without_great_docs_gives_pin(pkg, capsys):
    lock(pkg, None)
    assert run(capsys) == (0, report())


def test_a_version_outside_the_range_stops(pkg, capsys):
    lock(pkg, '0.18.0')
    assert run(capsys) == (1, report(
        version='0.18.0', in_range='no',
        step='stop: great-docs 0.18.0 is outside >=0.17.0,<0.18; pin it back into the range and run uv lock'))


@pytest.mark.parametrize(('files', 'expected'), [
    ([], ('none', [])),
    (['great-docs.yml'], ('root', ['great-docs.yml'])),
    (['docs/great-docs.yml'], ('docs', ['docs/great-docs.yml'])),
    (['great-docs.yml', 'docs/great-docs.yml'], ('both', ['great-docs.yml', 'docs/great-docs.yml'])),
])
def test_the_config_layout(pkg, files, expected):
    for rel in files:
        (pkg / rel).parent.mkdir(parents=True, exist_ok=True)
        (pkg / rel).write_text('parser: numpy\n')
    assert preflight.config_layout(pkg) == expected


@pytest.mark.parametrize(('files', 'layout'), [
    (['docs/great-docs.yml'], 'docs'),
    (['great-docs.yml', 'docs/great-docs.yml'], 'both'),
])
def test_a_docs_or_both_layout_stops_with_the_paths(pkg, capsys, files, layout):
    for rel in files:
        (pkg / rel).parent.mkdir(parents=True, exist_ok=True)
        (pkg / rel).write_text('parser: numpy\n')
    config = ', '.join(files)
    assert run(capsys) == (1, report(
        layout=layout, config=config,
        step=f'stop: config layout {layout} ({config}) is not supported; '
             'great-docs 0.17.x reads great-docs.yml at the project root'))


def test_a_fresh_fetch_writes_source_with_the_tag_commit(pkg, tmp_path, bare, capsys):
    lock(pkg, '0.17.0')
    cache = cache_dir(tmp_path)
    assert run(capsys, '--remote', bare.as_uri()) == (0, report(
        version='0.17.0', in_range='yes', skills=str(cache / 'skills'), step='init'))
    commit = git('rev-parse', f'{TAG}^{{commit}}', cwd=bare)
    assert commit != git('rev-parse', TAG, cwd=bare)  # the tag is annotated
    source = (cache / 'SOURCE').read_text().splitlines()
    assert source[:2] == [f'tag: {TAG}', f'commit: {commit}']
    assert re.fullmatch(r'fetched: \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ', source[2])
    assert len(source) == 3
    assert (cache / 'skills' / 'great-docs' / 'SKILL.md').is_file()
    assert sorted(p.name for p in cache.iterdir()) == ['SOURCE', 'skills']


def test_a_complete_cache_is_reused_without_a_clone(pkg, tmp_path, capsys):
    lock(pkg, '0.17.0')
    cache = cache_dir(tmp_path)
    (cache / 'skills').mkdir(parents=True)
    (cache / 'SOURCE').write_text('tag: v0.17.0\ncommit: abc\nfetched: 2026-10-19T00:00:00Z\n')
    unreachable = (tmp_path / 'no-such-remote.git').as_uri()  # a clone would fail
    assert run(capsys, '--remote', unreachable) == (0, report(
        version='0.17.0', in_range='yes', skills=str(cache / 'skills'), step='init'))
    assert (cache / 'SOURCE').read_text().splitlines()[1] == 'commit: abc'


def test_a_failed_clone_leaves_no_cache_folder(pkg, tmp_path, capsys):
    lock(pkg, '0.17.0')
    code, lines = run(capsys, '--remote', (tmp_path / 'no-such-remote.git').as_uri())
    assert code == 1
    assert lines[:-1] == report(version='0.17.0', in_range='yes')[:-1]
    assert lines[-1].startswith(STOP_FETCH)
    assert len(lines[-1]) > len(STOP_FETCH)  # git's error follows
    parent = cache_dir(tmp_path).parent
    assert (list(parent.iterdir()) if parent.exists() else []) == []


def test_a_cache_folder_without_source_is_fetched_again(pkg, tmp_path, bare, capsys):
    lock(pkg, '0.17.0')
    cache = cache_dir(tmp_path)
    cache.mkdir(parents=True)
    (cache / 'partial').write_text('left by an interrupted fetch\n')
    assert run(capsys, '--remote', bare.as_uri())[0] == 0
    assert sorted(p.name for p in cache.iterdir()) == ['SOURCE', 'skills']


def test_a_root_config_with_the_skills_cached_is_ready(pkg, tmp_path, bare, capsys):
    lock(pkg, '0.17.0')
    (pkg / 'great-docs.yml').write_text('parser: numpy\n')
    assert run(capsys, '--remote', bare.as_uri()) == (0, report(
        version='0.17.0', in_range='yes', layout='root', config='great-docs.yml',
        skills=str(cache_dir(tmp_path) / 'skills'), step='ready'))


def test_another_quarto_version_is_reported_and_does_not_stop(tmp_path, capsys):
    fake_quarto(tmp_path / 'bin', '1.9.0')
    assert run(capsys) == (0, report(quarto='1.9.0'))


def test_quarto_missing_stops_with_the_install_page(tmp_path, capsys):
    (tmp_path / 'bin' / 'quarto').unlink()
    assert run(capsys) == (1, report(
        quarto='missing', step='stop: quarto is missing; install it from https://quarto.org/docs/get-started/'))


def test_the_cache_defaults_to_the_home_cache(monkeypatch, tmp_path):
    expected = tmp_path / 'home' / '.cache' / 'agent-skills' / 'great-docs'
    monkeypatch.setenv('HOME', str(tmp_path / 'home'))
    monkeypatch.delenv('XDG_CACHE_HOME')
    assert preflight.cache_root() == expected
    monkeypatch.setenv('XDG_CACHE_HOME', '')
    assert preflight.cache_root() == expected
```

### `skills/document-python-package/scripts/preflight.py` (Task 3, Step 3)

<!-- extract-file: skills/document-python-package/scripts/preflight.py -->
```python
#!/usr/bin/env python3
# /// script
# requires-python = '>=3.11'
# dependencies = []
# ///
'''Preflight for the document-python-package skill. Run it from a package root:

    uv run <this-skill-dir>/scripts/preflight.py

It reads the great-docs version that uv.lock pins and checks it against the
tested range. It finds where great-docs.yml sits and which Quarto is on PATH.
Then it fetches Posit's official Great Docs skills from the matching release
tag into a version-keyed cache. It prints one `key: value` line per fact and
a last `next:` line that names the next step: pin, init or ready. It exits 0
when the package is ready for that step, and 1 on a stop, where `next:` gives
the reason. --remote replaces the GitHub URL, so the tests can pass a local
repository.
'''
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from datetime import datetime, timezone
from pathlib import Path

REMOTE = 'https://github.com/posit-dev/great-docs'
PACKAGE = 'great-docs'
# The tested range: 0.17.0 included, 0.18.0 excluded. Only a final release
# (X.Y.Z, digits only) can fall inside it.
LOWEST = (0, 17, 0)
FIRST_EXCLUDED = (0, 18, 0)
RANGE = '>=0.17.0,<0.18'
FINAL_RELEASE_RE = re.compile(r'(\d+)\.(\d+)\.(\d+)')
CONFIG = 'great-docs.yml'
CONFIG_PATHS = {'root': CONFIG, 'docs': f'docs/{CONFIG}'}
QUARTO_INSTALL = 'https://quarto.org/docs/get-started/'
QUARTO_TIMEOUT_S = 60
NONE = 'none'
STOP = 'stop: '


class FetchError(Exception):
    '''The official skills could not be fetched. The message is git's error.'''


def locked_version(root: Path) -> str | None:
    '''The great-docs version that root/uv.lock pins, or None.'''
    lock = root / 'uv.lock'
    if not lock.is_file():
        return None
    with lock.open('rb') as f:
        packages = tomllib.load(f).get('package', [])
    return next((p.get('version') for p in packages if p.get('name') == PACKAGE), None)


def in_range(version: str) -> bool:
    '''Whether version is a final release inside the tested range.'''
    m = FINAL_RELEASE_RE.fullmatch(version)
    return m is not None and LOWEST <= tuple(map(int, m.groups())) < FIRST_EXCLUDED


def config_layout(root: Path) -> tuple[str, list[str]]:
    '''The config layout (root, docs, both or none) and the config paths found.'''
    found = [name for name, rel in CONFIG_PATHS.items() if (root / rel).is_file()]
    if len(found) == len(CONFIG_PATHS):
        layout = 'both'
    else:
        layout = found[0] if found else NONE
    return layout, [CONFIG_PATHS[name] for name in found]


def quarto_version() -> str | None:
    '''The version that `quarto --version` prints, or None when Quarto is missing.'''
    quarto = shutil.which('quarto')
    if quarto is None:
        return None
    try:
        proc = subprocess.run([quarto, '--version'], capture_output=True, text=True,
                              timeout=QUARTO_TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired):
        return None
    words = proc.stdout.split()
    return words[0] if proc.returncode == 0 and words else None


def cache_root() -> Path:
    '''${XDG_CACHE_HOME:-~/.cache}/agent-skills/great-docs'''
    base = os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache'
    return Path(base) / 'agent-skills' / PACKAGE


def _git(*args: str) -> str:
    # GIT_TERMINAL_PROMPT=0: a bad URL fails at once instead of asking for a password.
    env = {**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
    try:
        proc = subprocess.run(['git', *args], capture_output=True, text=True, env=env)
    except FileNotFoundError:
        raise FetchError('git is not installed') from None
    if proc.returncode != 0:
        raise FetchError(' '.join(proc.stderr.split()) or f'git exited {proc.returncode}')
    return proc.stdout.strip()


def fetch_skills(version: str, remote: str) -> Path:
    '''The cached skills/ folder of tag v<version>. A cache folder with a SOURCE
    file is complete and is reused. Any other is deleted and fetched again, in a
    temporary folder beside it that is renamed into place.'''
    parent = cache_root()
    dest = parent / version
    if (dest / 'SOURCE').is_file():
        return dest / 'skills'
    if dest.exists():
        shutil.rmtree(dest)
    parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f'.{version}-', dir=parent))
    tag = f'v{version}'
    try:
        repo, out = staging / 'repo', staging / 'out'
        _git('clone', '--quiet', '--depth', '1', '--filter=blob:none', '--sparse',
             '--branch', tag, remote, str(repo))
        _git('-C', str(repo), 'sparse-checkout', 'set', 'skills')
        if not (repo / 'skills').is_dir():
            raise FetchError(f'tag {tag} has no skills/ folder')
        commit = _git('-C', str(repo), 'rev-parse', 'HEAD')
        out.mkdir()
        shutil.copytree(repo / 'skills', out / 'skills')
        fetched = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        (out / 'SOURCE').write_text(f'tag: {tag}\ncommit: {commit}\nfetched: {fetched}\n')
        out.rename(dest)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    return dest / 'skills'


def next_step(layout: str, configs: list[str], quarto: str | None, version: str | None,
              remote: str) -> tuple[str, Path | None]:
    '''The `next:` value and the cached skills folder. Stops come first: an
    unsupported layout, then a missing Quarto. Then a missing pin, a version
    outside the range and a failed fetch, in that order.'''
    if layout not in ('root', NONE):
        return (f'{STOP}config layout {layout} ({", ".join(configs)}) is not supported; '
                f'great-docs 0.17.x reads {CONFIG} at the project root', None)
    if quarto is None:
        return f'{STOP}quarto is missing; install it from {QUARTO_INSTALL}', None
    if version is None:
        return 'pin', None
    if not in_range(version):
        return (f'{STOP}great-docs {version} is outside {RANGE}; '
                'pin it back into the range and run uv lock', None)
    try:
        skills = fetch_skills(version, remote)
    except FetchError as exc:
        return f'{STOP}fetching the official skills failed: {exc}', None
    return ('init' if layout == NONE else 'ready'), skills


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Preflight for the document-python-package skill.')
    parser.add_argument('--remote', default=REMOTE, help='the great-docs git repository to fetch from')
    args = parser.parse_args(argv)
    root = Path.cwd()
    version = locked_version(root)
    layout, configs = config_layout(root)
    quarto = quarto_version()
    step, skills = next_step(layout, configs, quarto, version, args.remote)
    facts = {
        'great-docs': version or NONE,
        'range': RANGE,
        'in-range': NONE if version is None else ('yes' if in_range(version) else 'no'),
        'layout': layout,
        'config': ', '.join(configs) or NONE,
        'quarto': quarto or 'missing',
        'skills': str(skills) if skills else NONE,
        'next': step,
    }
    for key, value in facts.items():
        print(f'{key}: {value}')
    return 1 if step.startswith(STOP) else 0


if __name__ == '__main__':
    sys.exit(main())
```

### `skills/document-python-package/SKILL.md` (Task 3, Step 6)

The `{{KEY}}` slots are filled by `fill_slots.py` from the spike record (DF2). A slot named in `fill_slots.py`'s `VARIANTS` (Appendix D) takes one of several fixed texts. `COMPLETENESS_CONFIG` and `CELL_ERROR_BULLET` can delete their whole line. Every other slot takes the record's value. The frontmatter carries Q1's option (c).

<!-- extract-file: skills/document-python-package/SKILL.md -->
````markdown
---
name: document-python-package
description: >
  Use when documenting a Python package with Great Docs: setting up or building
  its docs site, running great-docs init, build or lint, writing numpy
  docstrings or user-guide pages for it, making its README serve as the site
  homepage, adding executed or frozen examples, or deploying the site to GitHub
  Pages. Also triggers when a repo has a great-docs.yml file or a great-docs/
  build folder.
license: MIT
compatibility: >
  Requires uv to run bundled scripts (dependencies are declared inline); Python
  3.11+. Also requires git, Quarto and great-docs >=0.17.0,<0.18, and the
  preflight script fetches Posit's official Great Docs skills from github.com.
metadata:
  author: Lowell Mason
  version: "1.0"
---

# Document a Python Package with Great Docs

Great Docs builds a Quarto site from a package's docstrings, README and
user-guide pages. Posit publishes five official skills for it. This skill is a
thin layer over them for great-docs 0.17.x and public packages (github.com,
PyPI, GitHub Pages). It adds a preflight, a few conventions and a done gate.

The layer exists because the release and the official text disagree. In
0.17.x, `great-docs init` writes `great-docs.yml` at the project root, and
`build` writes an ephemeral `great-docs/` folder. The main branch and its
skills describe an unreleased `docs/` layout. So the official skills are read
only from the release tag that matches the locked version, and the preflight
fetches that copy.

## Preflight first

Run it from the package root, and act on its last line:

```bash
uv run <this-skill-dir>/scripts/preflight.py
```

Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header.

It prints `key: value` lines: `great-docs` (the version that `uv.lock` pins),
`range`, `in-range`, `layout`, `config`, `quarto`, `skills` (the cached
official skills) and, last, `next:`.

| `next:` | Do |
|---|---|
| `pin` | Pin, then run the preflight again |
| `init` | Init |
| `ready` | The sections the task needs, then the gate |
| `stop: …` | Stop and report the line. Never work around it |

Exit 1 is a stop:

- **Version outside `>=0.17.0,<0.18`.** Pin back into the range and run `uv lock`. Widening the range is a repo change after a new spike, never a decision at run time.
- **Layout `docs` or `both`.** Report the paths. That layout belongs to an unreleased great-docs.
- **Fetch failed** (no network, no tag, no git). Report git's error. Never fall back to the main branch, the docs site or `great-docs skill install`.
- **Quarto missing.** Point the user to https://quarto.org/docs/get-started/.

## Which text wins

Highest first:

1. The installed CLI's `--help` (`uv run great-docs <command> --help`) and the files that `init` actually wrote.
2. This skill's conventions. Where they conflict with the official text, they win.
3. The cached official skills, under the preflight's `skills:` path, for everything else:
   - CLI use and builds: `great-docs/SKILL.md`
   - `great-docs.yml`: `configure-site/SKILL.md`
   - Docstrings: `revise-docstrings/SKILL.md`
   - User-guide pages: `write-user-guide/SKILL.md`
   - `author-skills/SKILL.md`, only when the user asks to curate the package's published skill

Never read main-branch text or the docs site's skills, and never run
`great-docs skill install`. The cached skills' script folders are reference
only: never run their scripts.

| The official skills say | Do instead |
|---|---|
| `pip install great-docs`, `pip install --upgrade great-docs` or `uv pip install --upgrade great-docs` | The pinned `docs` group and `uv lock` (Pin). No upgrade outside the range |
| `pip install -e .` before a build | `uv sync` and `uv run`, which install the project itself |
| Run the bundled `setup-env.sh` | Never run it. Pin replaces it |
| Run the bundled `run-build.sh`, or a bare `great-docs build` | `uv run great-docs build </dev/null`, inside the gate |
| `great-docs init --force` to reset a config | Never run `init` when a config exists |
| A bare `great-docs <command>` | `uv run great-docs <command>` |

## Pin

Add the pin to `pyproject.toml`, then run `uv lock`:

```toml
[dependency-groups]
docs = ['great-docs>=0.17.0,<0.18', '{{COMPLETENESS_PIN}}']

[tool.uv]
default-groups = ['dev', 'docs']   # the package's existing groups, plus docs
```

The pin's range equals the preflight's range. uv's default for
`default-groups` is `['dev']`, so without `docs` in that list a plain
`uv sync`, locally or in CI, skips the pin. Then run the preflight again: it
fetches the official skills and names the next step.
{{COMPLETENESS_CONFIG}}

## Init

Only when the preflight says `next: init` (no config yet):

```bash
{{INIT_COMMAND}}
```

{{INIT_SENTENCE}}
Then check two things in `great-docs.yml`: `parser: numpy`, and the package's
`__all__` exports listed.

When a config exists, never run `init`, because `--force` deletes the config.
Edit `great-docs.yml` as `configure-site` describes.

## Docstrings

- Write numpy style on every `__all__` export and on the public methods of each exported class.
- `revise-docstrings` covers the Great Docs details, such as `%seealso`.
- For bulk drafts, dispatch the `docs-writer` agent (its docstrings lane) with the numpy and completeness rules in the brief. When that agent is not installed, draft directly.
{{D300_BULLET}}

## The README is the homepage

With `homepage: index`, one README serves GitHub, PyPI and the site:

- Put the badges in one block at the top. {{HERO_SENTENCE}}
- Make the first paragraph a plain summary of one or two sentences. {{META_SENTENCE}}
- Use absolute URLs for images and links, because PyPI does not resolve relative paths.
- Use no GitHub-only syntax, such as `> [!NOTE]` alerts or Mermaid blocks. PyPI shows them as plain text.
- The `docs-writer` agent drafts the README (its README lane) when it is installed, and `write-with-asd-ste100` shapes the prose.

## User-guide pages

Follow `write-user-guide`. `write-with-asd-ste100` shapes the prose.

## Executed examples

{{DOCSTRING_EXAMPLES_BULLET}}
- Put slow work, such as MCMC, in user-guide pages under `freeze: auto`. Commit the `{{FREEZE_DIR}}` cache, so that CI renders the pages without running the code again.
- After the code on a frozen page changes, render locally and commit the new cache.

## Deploy

```bash
uv run great-docs setup-github-pages
```

Then delete the generated `uv pip install great-docs` line from the workflow,
because `uv sync` already installs the pinned `docs` group. Do this again
after every regeneration of the workflow.

## The gate

The docs are done only when all three checks pass, run from the package root:

1. `uv run great-docs lint` exits 0.
2. `uv run great-docs build </dev/null` passes, which takes all of these:
   - The command exits 0.
   - Its output has none of the four lines that mean the build went on with no API reference:
     - `Skipping API reference configuration`
     - `API reference skipped (non-Python project)`
     - `No documentable exports found — skipping API reference`
     - `API reference disabled (reference: false), skipping`
   - `{{API_INDEX}}` exists.
{{CELL_ERROR_BULLET}}
3. `{{COMPLETENESS_COMMAND}}` exits 0. `<package-dir>` is the folder that holds the package's `__init__.py`, so the check covers every `__all__` export.

After the gate, run `uv run great-docs check-links`, and
`uv run great-docs proofread` when `harper-cli` is installed. Report what they
find. They never block.

A failed check means the work is not done. Name the check and give its output.

| Thought | Reality |
|---|---|
| "The build passed, so the docs are done." | A build can exit 0 with no API reference. Check its output and the index page, then run lint and the completeness check. |
| "Lint shows no errors, so we are done." | Lint only warns about a public method with no docstring, and it does not check sections. The completeness check is the third gate. |
| "The user is in a hurry, so the rest can wait." | Report what passed and what did not. Never call the docs done before all three pass. |

## License

This skill is MIT licensed: see [LICENSE](LICENSE). Posit's official Great
Docs skills are MIT licensed, Copyright (c) 2026 Posit Software, PBC. The
preflight fetches them at run time into a cache outside this skill. This
skill bundles none of their text.
````

### `specs/verification/57-great-docs-0.17.0.md` (Task 1, Step 18)

<!-- extract-file: specs/verification/57-great-docs-0.17.0.md -->
```markdown
# Spike record: great-docs 0.17.0

Plan 57, Task 1. This record answers the eight spike questions, S1 to S8, of
validation item V1 in `specs/document-python-package-spec.md`. The fixture is
`gdfixture`, a scratch package outside this repository (plan 57, Appendix E).
Logs and the fixture stay in `~/.cache/agent-skills/scratch/great-docs-spike/`
and are not committed. Each answer quotes the lines it rests on.

## Versions

| Tool | Version |
|---|---|
| great-docs (from `uv.lock`) | TO-RECORD |
| Quarto | TO-RECORD |
| uv | TO-RECORD |
| git | TO-RECORD |
| The fixture's Python | TO-RECORD |
| ruff (S6) | TO-RECORD |
| pydoclint (S7) | TO-RECORD |
| numpydoc (S7) | TO-RECORD |

## Answers

### S1: a non-interactive init

- Command and exit code: TO-RECORD
- `.gitignore` change: TO-RECORD
- `parser:` line and the exports in `great-docs.yml`: TO-RECORD
- Answer: TO-RECORD

### S2: the build and the API reference index page

- Exit code: TO-RECORD
- Skip lines found (expected none): TO-RECORD
- API reference index page: TO-RECORD
- Answer: TO-RECORD

### S3: executed cells

- Docstring example output on the reference page (S3a): TO-RECORD
- Build with a failing docstring cell: exit code and error lines: TO-RECORD
- Build with a failing page cell: exit code and error lines: TO-RECORD
- Where a cell error shows when the build exits 0: TO-RECORD
- Answer: TO-RECORD

### S4: the freeze cache

- `_freeze` folders found: TO-RECORD
- `git check-ignore` on a file inside: TO-RECORD
- Answer: TO-RECORD

### S5: `default-groups` and the generated workflow

- great-docs after `uv sync --no-default-groups --group dev` (the control): TO-RECORD
- great-docs after a plain `uv sync`: TO-RECORD
- The workflow file and its `uv sync` and `uv pip install` lines: TO-RECORD
- Answer: TO-RECORD

### S6: `ruff format` and `'''` docstrings

- Added `"""` lines, default settings: TO-RECORD
- Added `"""` lines, `quote-style = 'single'`: TO-RECORD
- Added `"""` lines, `quote-style = 'preserve'`: TO-RECORD
- Answer: TO-RECORD

### S7: the completeness tool

- pydoclint: exit code and findings: TO-RECORD
- numpydoc: exit code and findings: TO-RECORD
- The selection rule (plan 57, DF20) and the choice: TO-RECORD

### S8: the README on the built site

- `inspect_site.py` output: TO-RECORD
- Answer: TO-RECORD

## Values

Plan 57's `fill_slots.py` reads this table to fill the skill text and the spec
amendments. A `|` inside a value is written `\|`.

| Key | Value | Evidence |
|---|---|---|
| SPIKE_DATE | `TO-RECORD` | The day the spike ran, YYYY-MM-DD |
| GD_VERSION | `TO-RECORD` | Versions |
| QUARTO_VERSION | `TO-RECORD` | Versions |
| INIT_DEFAULT_WORKS | `TO-RECORD` | S1: `yes` or `no` |
| INIT_COMMAND | `TO-RECORD` | S1: the command that worked |
| API_INDEX | `TO-RECORD` | S2: the page's path from the package root |
| DOCSTRING_CELLS_RUN | `TO-RECORD` | S3a: `yes` or `no` |
| CELL_ERROR | `TO-RECORD` | S3: `fails`, `log` or `site` |
| CELL_ERROR_MARKER | `TO-RECORD` | S3: the marker, or `none` for `fails` |
| FREEZE_DIR | `TO-RECORD` | S4: the folder from the package root, with a trailing `/` |
| RUFF_REWRITES_DOCSTRINGS | `TO-RECORD` | S6: `no`, `single`, `preserve` or `yes` |
| COMPLETENESS_TOOL | `TO-RECORD` | S7: `pydoclint` or `numpydoc` |
| COMPLETENESS_PIN | `TO-RECORD` | S7: the requirement for the `docs` group |
| COMPLETENESS_COMMAND | `TO-RECORD` | S7: the gate command, with `<package-dir>` |
| HERO_BADGES | `TO-RECORD` | S8: `yes` or `no` |
| META_FROM_FIRST_PARAGRAPH | `TO-RECORD` | S8: `yes` or `no` |
| META_SOURCE | `TO-RECORD` | S8: the source, or `none` for `yes` |
```

### `specs/verification/57-document-python-package-skill-tests.md` (Task 2, Step 8)

<!-- extract-file: specs/verification/57-document-python-package-skill-tests.md -->
```markdown
# Skill tests: document-python-package

Plan 57, Tasks 2 and 4. This record covers validation item V3 of
`specs/document-python-package-spec.md`: a RED baseline before the skill text
existed, GREEN after it, a trigger test of the description and one end-to-end
run. The pre-registered rules, the prompts and the raw replies stay in the
test kit, `~/.cache/agent-skills/scratch/document-python-package-kit/`,
outside this repository.

## Setup

| Setting | Value |
|---|---|
| Claude Code (the held binary) | TO-RECORD |
| Model and effort | `claude-opus-5-5`, medium |
| Scenario calls | Decision-only: `--tools ""`, `--strict-mcp-config`, no budget flag, a scrubbed environment, each arm from a new folder under `/tmp` |
| Replies per scenario and arm | 5 |
| RED: date and cost | TO-RECORD |
| GREEN: date and cost | TO-RECORD |

## Scenarios and items

| Scenario | The user's request | Its item |
|---|---|---|
| `sc1-setup` | Set up Great Docs for a fresh package | M2, a bare `init`, and M3, a pin that a plain `uv sync` skips |
| `sc2-deploy` | Deploy the site, with the generated workflow given | M4, the unpinned CI line left in |
| `sc3-done` | Confirm that the docs are done after a build and a clean lint | M5, done without the gate |
| `sc4-mcmc` | Add an MCMC example | X1, the slow example in the wrong place |
| `sc5-official-skills` | Get the official skills and follow them | M1, the official skills from the wrong source |

## RED

TO-RECORD

## GREEN

TO-RECORD

## REFACTOR

TO-RECORD

## Trigger test

TO-RECORD

## End-to-end run

TO-RECORD

## Verdict

TO-RECORD
```

## Appendix C: repository edits

### Task 1, Step 4: the planning amendments

A1, the script count (Sequencing item 5):

<!-- extract-edit: specs/document-python-package-spec.md:a1-scripts -->

Old text:

```markdown
   frontmatter carries `license`. Plan 53's planning record counts 17 runnable
   scripts, and `preflight.py` makes 18. If this skill lands first, its plan
   adds one dated line to plan 53's Global Constraints (D8). The line names
   `document-python-package/scripts/preflight.py` as a script that already
   conforms. It also says that the skill's `LICENSE` copy already exists and
   that plan 53's executor should expect 18 scripts. If plan 53 lands first,
   nothing extra is needed.
```

New text:

```markdown
   frontmatter carries `license`. Plan 53's planning record counts 17 runnable
   scripts. Plan 52's vendored `write-with-asd-ste100/scripts/ste-lint.py`
   landed after that count and makes 18, so `preflight.py` makes 19
   (owner, plan 57, 2026-10-19). If this skill lands first, its plan
   adds one dated line to plan 53's Global Constraints (D8). The line names
   `document-python-package/scripts/preflight.py` as a script that already
   conforms. It also says that the skill's `LICENSE` copy already exists and
   that plan 53's executor should expect 19 scripts
   (owner, plan 57, 2026-10-19). If plan 53 lands first, nothing extra is
   needed.
```

A2, the `compatibility` text (R1.4, Q1's option (c)):

<!-- extract-edit: specs/document-python-package-spec.md:a2-compatibility -->

Old text:

```markdown
R1.4 **`compatibility`** (500 characters at most): "Requires uv, git, Quarto
and great-docs >=0.17.0,<0.18. The preflight script needs Python >=3.11 and
fetches Posit's official Great Docs skills from github.com."
```

New text:

```markdown
R1.4 **`compatibility`** (500 characters at most): "Requires uv to run bundled
scripts (dependencies are declared inline); Python 3.11+. Also requires git,
Quarto and great-docs >=0.17.0,<0.18, and the preflight script fetches Posit's
official Great Docs skills from github.com." The first sentence is the
portability spec's R3.6 string, with the floor that R3.1 sets here
(owner, plan 57, 2026-10-19).
```

### Task 1, Step 19: the spike's amendments

Every spike applies these five:

<!-- extract-edit: specs/document-python-package-spec.md:results -->

Old text:

```markdown
| S8 | On the built site, do the badges move into the hero, and does the first paragraph become the meta description? | R4.5's two site claims change to what the build shows |
```

New text:

```markdown
| S8 | On the built site, do the badges move into the hero, and does the first paragraph become the meta description? | R4.5's two site claims change to what the build shows |

**Spike results** (spike S1–S8, plan 57, {{SPIKE_DATE}}). The spike answered
all eight questions with great-docs {{GD_VERSION}} and Quarto {{QUARTO_VERSION}}.
Its record is `specs/verification/57-great-docs-0.17.0.md`. Each requirement
that an answer changed carries that answer's tag.
```

<!-- extract-edit: specs/document-python-package-spec.md:s2-index -->

Old text:

```markdown
   - The built site has its API reference index page (the path comes from S2).
```

New text:

```markdown
   - The built site has its API reference index page, `{{API_INDEX}}`
     (spike S2, plan 57, {{SPIKE_DATE}}).
```

<!-- extract-edit: specs/document-python-package-spec.md:s4-freeze -->

Old text:

```markdown
- Put slow work, such as MCMC, in user-guide pages under `freeze: auto`. Commit
  the `_freeze/` cache (its location comes from S4), so that CI renders the
  pages without running the code again.
```

New text:

```markdown
- Put slow work, such as MCMC, in user-guide pages under `freeze: auto`. Commit
  the `{{FREEZE_DIR}}` cache (spike S4, plan 57, {{SPIKE_DATE}}), so that CI
  renders the pages without running the code again.
```

<!-- extract-edit: specs/document-python-package-spec.md:s7-pin -->

Old text:

```markdown
docs = ['great-docs>=0.17.0,<0.18']   # plus the completeness tool (S7)
```

New text:

```markdown
docs = ['great-docs>=0.17.0,<0.18', '{{COMPLETENESS_PIN}}']   # (spike S7, plan 57, {{SPIKE_DATE}})
```

<!-- extract-edit: specs/document-python-package-spec.md:s7-gate -->

Old text:

```markdown
3. the completeness check over the `__all__` exports (the tool and its command
   come from S7)
```

New text:

```markdown
3. `{{COMPLETENESS_COMMAND}}`, the completeness check, where `<package-dir>` is
   the folder that holds the package's `__init__.py`, so that it covers every
   `__all__` export (spike S7, plan 57, {{SPIKE_DATE}})
```

S1, when `INIT_DEFAULT_WORKS` is `no`:

<!-- extract-edit: specs/document-python-package-spec.md:s1-init -->

Old text:

```markdown
R4.3 **Init, only when the layout is `none`.** Run
`uv run great-docs init --force </dev/null`. Here `--force` only skips the
`.gitignore` prompt, because no config exists for it to delete. After `init`,
```

New text:

```markdown
R4.3 **Init, only when the layout is `none`.** Run `{{INIT_COMMAND}}`
(spike S1, plan 57, {{SPIKE_DATE}}). The piped input answers `init`'s prompts,
the `.gitignore` prompt among them, so it never waits. After `init`,
```

S3, docstring examples. One of the two:

<!-- extract-edit: specs/document-python-package-spec.md:s3-docstrings-run -->

Old text:

```markdown
- Docstring examples run on every build (S3). Keep them fast and deterministic:
  no MCMC, no network, fixed seeds.
```

New text:

```markdown
- Docstring examples run on every build (spike S3, plan 57, {{SPIKE_DATE}}).
  Keep them fast and deterministic: no MCMC, no network, fixed seeds.
```

<!-- extract-edit: specs/document-python-package-spec.md:s3-docstrings-shown -->

Old text:

```markdown
- Docstring examples run on every build (S3). Keep them fast and deterministic:
  no MCMC, no network, fixed seeds.
```

New text:

```markdown
- The build shows docstring examples but never runs them
  (spike S3, plan 57, {{SPIKE_DATE}}). Run each one before committing it, and
  keep it fast and deterministic: no MCMC, no network, fixed seeds.
```

S3, cell errors, when `CELL_ERROR` is `log` or `site`. The first block, then one of the other two. Both of those find the text that `s2-index` wrote, so they apply after it:

<!-- extract-edit: specs/document-python-package-spec.md:s3-four-checks -->

Old text:

```markdown
   waiting for input. The build check passes only when all three of these hold:
```

New text:

```markdown
   waiting for input. The build check passes only when all four of these hold:
```

<!-- extract-edit: specs/document-python-package-spec.md:s3-log -->

Old text:

```markdown
   - The built site has its API reference index page, `{{API_INDEX}}`
     (spike S2, plan 57, {{SPIKE_DATE}}).
```

New text:

```markdown
   - The built site has its API reference index page, `{{API_INDEX}}`
     (spike S2, plan 57, {{SPIKE_DATE}}).
   - Its output has no `{{CELL_ERROR_MARKER}}` line, because a failing code
     cell does not fail the build (spike S3, plan 57, {{SPIKE_DATE}}).
```

<!-- extract-edit: specs/document-python-package-spec.md:s3-site -->

Old text:

```markdown
   - The built site has its API reference index page, `{{API_INDEX}}`
     (spike S2, plan 57, {{SPIKE_DATE}}).
```

New text:

```markdown
   - The built site has its API reference index page, `{{API_INDEX}}`
     (spike S2, plan 57, {{SPIKE_DATE}}).
   - No page of the built site holds `{{CELL_ERROR_MARKER}}`, because a failing
     code cell does not fail the build (spike S3, plan 57, {{SPIKE_DATE}}).
```

S6. One of the four:

<!-- extract-edit: specs/document-python-package-spec.md:s6-no -->

Old text:

```markdown
- If the package enables ruff's pydocstyle (`D`) rules and keeps `'''`
  docstrings, ignore D300. Spike S6 settles when this note applies.
```

New text:

```markdown
- If the package enables ruff's pydocstyle (`D`) rules and keeps `'''`
  docstrings, ignore D300. `ruff format` keeps `'''` docstrings
  (spike S6, plan 57, {{SPIKE_DATE}}).
```

<!-- extract-edit: specs/document-python-package-spec.md:s6-single -->

Old text:

```markdown
- If the package enables ruff's pydocstyle (`D`) rules and keeps `'''`
  docstrings, ignore D300. Spike S6 settles when this note applies.
```

New text:

```markdown
- If the package enables ruff's pydocstyle (`D`) rules and keeps `'''`
  docstrings, ignore D300. A package that runs `ruff format` keeps them only
  with `quote-style = 'single'` (spike S6, plan 57, {{SPIKE_DATE}}).
```

<!-- extract-edit: specs/document-python-package-spec.md:s6-preserve -->

Old text:

```markdown
- If the package enables ruff's pydocstyle (`D`) rules and keeps `'''`
  docstrings, ignore D300. Spike S6 settles when this note applies.
```

New text:

```markdown
- If the package enables ruff's pydocstyle (`D`) rules and keeps `'''`
  docstrings, ignore D300. A package that runs `ruff format` keeps them only
  with `quote-style = 'preserve'` (spike S6, plan 57, {{SPIKE_DATE}}).
```

<!-- extract-edit: specs/document-python-package-spec.md:s6-yes -->

Old text:

```markdown
- If the package enables ruff's pydocstyle (`D`) rules and keeps `'''`
  docstrings, ignore D300. Spike S6 settles when this note applies.
```

New text:

```markdown
- If the package enables ruff's pydocstyle (`D`) rules and keeps `'''`
  docstrings, ignore D300. This applies only to packages that do not run
  `ruff format`, which rewrites them to `"""` (spike S6, plan 57, {{SPIKE_DATE}}).
```

S7, when `COMPLETENESS_TOOL` is `numpydoc`:

<!-- extract-edit: specs/document-python-package-spec.md:s7-numpydoc-config -->

Old text:

````markdown
default-groups = ['dev', 'docs']      # the package's existing groups, plus docs
```
````

New text:

````markdown
default-groups = ['dev', 'docs']      # the package's existing groups, plus docs

[tool.numpydoc_validation]            # (spike S7, plan 57, {{SPIKE_DATE}})
checks = ['PR01', 'RT01', 'GL08']
exclude = ['\._\w+$']
```
````

S8. One of each pair:

<!-- extract-edit: specs/document-python-package-spec.md:s8-hero-yes -->

Old text:

```markdown
- Put the badges in one block at the top. The site moves them into the hero
  (S8).
```

New text:

```markdown
- Put the badges in one block at the top. The site moves them into the hero
  (spike S8, plan 57, {{SPIKE_DATE}}).
```

<!-- extract-edit: specs/document-python-package-spec.md:s8-hero-no -->

Old text:

```markdown
- Put the badges in one block at the top. The site moves them into the hero
  (S8).
```

New text:

```markdown
- Put the badges in one block at the top. The site shows the block as it
  stands (spike S8, plan 57, {{SPIKE_DATE}}).
```

<!-- extract-edit: specs/document-python-package-spec.md:s8-meta-yes -->

Old text:

```markdown
- Make the first paragraph a plain summary of one or two sentences. It becomes
  the site's SEO description (S8).
```

New text:

```markdown
- Make the first paragraph a plain summary of one or two sentences. It becomes
  the site's meta description (spike S8, plan 57, {{SPIKE_DATE}}).
```

<!-- extract-edit: specs/document-python-package-spec.md:s8-meta-no -->

Old text:

```markdown
- Make the first paragraph a plain summary of one or two sentences. It becomes
  the site's SEO description (S8).
```

New text:

```markdown
- Make the first paragraph a plain summary of one or two sentences. The site
  takes its meta description from {{META_SOURCE}}, not from this paragraph
  (spike S8, plan 57, {{SPIKE_DATE}}).
```

### Task 3: the registry and the provenance

<!-- extract-edit: build/suites.toml:suite -->

Old text:

```toml
notes = ['ADR-scaffolder tests (stdlib only).']
```

New text:

```toml
notes = ['ADR-scaffolder tests (stdlib only).']

[[suite]]
name = 'document-python-package'
dir = 'skills/document-python-package/scripts'
with = ['pytest']
notes = ['Preflight tests, stdlib only. The fetch tests clone a local bare repository through a file:// URL.']
```

<!-- extract-edit: NOTICE:originals -->

Old text:

```text
    optimize-jax/
    prepare-handoff/
```

New text:

```text
    optimize-jax/
    prepare-handoff/
    document-python-package/
```

The paragraph is R6.1's approved wording:

<!-- extract-edit: NOTICE:paragraph -->

Old text:

```text
terms; the bootstrap seeds them into a wiki root, and they carry no third-party
code.

```

New text:

```text
terms; the bootstrap seeds them into a wiki root, and they carry no third-party
code.

document-python-package/ is an original work by Lowell Mason (MIT). At run
time, its scripts/preflight.py fetches the official Great Docs skills from
posit-dev/great-docs (MIT, Copyright (c) 2026 Posit Software, PBC). It takes
them from the release tag that matches the installed great-docs version, keeps
them in a cache outside this repository, and records the tag's commit. The
skill bundles, reproduces and adapts none of their text. It only names those
skills and sends the agent to them.

```

<!-- extract-edit: CLAUDE.md:originals -->

Old text:

```markdown
- **Lowell's originals** (MIT, `LICENSE`): `develop-testing-strategy`, `validate-data`, `explore-data`, `tech-debt`, `design-architecture`, `bls-data-context`, `recommend-probabilistic-model`, `recommend-visualization`, `track-model-experiments`, `tune-hyperparameters`, `creative-thinking`, `llm-wiki`, `describe-critique-methodology`, `derive-roadmap`, `classification-codes`, `geographic-codes`, `deep-learning`, `evaluate-deep-learning`, `optimize-jax`, `prepare-handoff`. (20 originals — keep in sync with `NOTICE`, which is authoritative.)
```

New text:

```markdown
- **Lowell's originals** (MIT, `LICENSE`): `develop-testing-strategy`, `validate-data`, `explore-data`, `tech-debt`, `design-architecture`, `bls-data-context`, `recommend-probabilistic-model`, `recommend-visualization`, `track-model-experiments`, `tune-hyperparameters`, `creative-thinking`, `llm-wiki`, `describe-critique-methodology`, `derive-roadmap`, `classification-codes`, `geographic-codes`, `deep-learning`, `evaluate-deep-learning`, `optimize-jax`, `prepare-handoff`, `document-python-package`. (21 originals — keep in sync with `NOTICE`, which is authoritative.)
```

### Task 5: the README, design-architecture and plan 53

<!-- extract-edit: README.md:row -->

Old text:

```markdown
| [`write-with-asd-ste100`](skills/write-with-asd-ste100/) | Write and rewrite in ASD-STE100 Simplified Technical English (STE), the controlled English of aircraft maintenance manuals. Human mode, the default, writes about 80% of the way to the standard, after a tip from Andrej Karpathy. Agent mode applies strict rules to prompts, tool descriptions, subagent briefs and error strings. The skill rewrites a text, or a whole file in place (left uncommitted) or as a `.ste` copy beside it. It also explains, summarizes and draws small Mermaid diagrams, and it never claims dictionary compliance. It bundles danyuchn's structural linter, unchanged. A user-level rule carries the everyday habits and a label rule into every session (see [Rules](#rules)). Adapted from danyuchn and prithivrajmu (MIT). |
```

New text:

```markdown
| [`write-with-asd-ste100`](skills/write-with-asd-ste100/) | Write and rewrite in ASD-STE100 Simplified Technical English (STE), the controlled English of aircraft maintenance manuals. Human mode, the default, writes about 80% of the way to the standard, after a tip from Andrej Karpathy. Agent mode applies strict rules to prompts, tool descriptions, subagent briefs and error strings. The skill rewrites a text, or a whole file in place (left uncommitted) or as a `.ste` copy beside it. It also explains, summarizes and draws small Mermaid diagrams, and it never claims dictionary compliance. It bundles danyuchn's structural linter, unchanged. A user-level rule carries the everyday habits and a label rule into every session (see [Rules](#rules)). Adapted from danyuchn and prithivrajmu (MIT). |
| [`document-python-package`](skills/document-python-package/) | Document a public Python package with Great Docs 0.17.x. The skill is a thin layer over Posit's five official Great Docs skills. It builds on them and copies none of their text. A bundled `preflight.py` checks the great-docs version that `uv.lock` pins against the tested range and finds the config. Then it fetches the official skills from the matching release tag into a cache. The skill pins great-docs in a uv `docs` group that CI also installs. It makes the README work as the site homepage, and it freezes slow executed examples. Its done gate has three checks: lint, a build that kept its API reference, and docstring completeness. |
```

The bullet is R6.4's wording:

<!-- extract-edit: skills/design-architecture/SKILL.md:adr-bullet -->

Old text:

```markdown
  does) — keep ADRs beside the specs and plans they formalize.
```

New text:

```markdown
  does) — keep ADRs beside the specs and plans they formalize.
- **Use `specs/adr/` when the repo publishes a Great Docs site.** The site serves the package's
  users, and ADRs serve its maintainers.
```

`DATE` is replaced by today's date in Task 5, Step 2:

<!-- extract-edit: specs/plans/53-agent-skills-portability.md:d8-line -->

Old text:

```markdown
- **Another plan landed first.** Plan 52 (write-with-asd-ste100) also edits `NOTICE`, `README.md`, `CLAUDE.md` and the register (`build/cc_guide/conformance.toml`). If an edit block below no longer matches because another plan changed the text around it, read the current text, make the same change by hand, and note it as a deviation; never restore the old text.
```

New text:

```markdown
- **Another plan landed first.** Plan 52 (write-with-asd-ste100) also edits `NOTICE`, `README.md`, `CLAUDE.md` and the register (`build/cc_guide/conformance.toml`). If an edit block below no longer matches because another plan changed the text around it, read the current text, make the same change by hand, and note it as a deviation; never restore the old text.
- **document-python-package landed first** (plan 57, DATE, under D8 of that skill's spec). It adds a 39th skill and a 19th runnable script, `skills/document-python-package/scripts/preflight.py`. Plan 52's vendored `write-with-asd-ste100/scripts/ste-lint.py` is the 18th. The script already conforms: a PEP 723 header with `requires-python = '>=3.11'` and `dependencies = []`, a `uv run` invocation followed by R3.5's sentence, and a `compatibility` value that names uv. The skill's `LICENSE` copy already exists, byte-identical to the root file, so Task 8 writes the same bytes. The helpers in Tasks 10, 12 and 13 name their scripts and skills one by one, so they leave this skill alone.
```

## Appendix D: the test kit

These blocks go to `~/.cache/agent-skills/scratch/document-python-package-kit/` in Task 1, Step 3 (`fill_slots.py`) and Task 2, Step 2 (the rest). Task 2 copies `artifacts/pyproject-fresh.toml` and `artifacts/init.py` from the fixture.

### `fill_slots.py`

<!-- extract-file: fill_slots.py -->
````python
#!/usr/bin/env python3
'''Fill the {{KEY}} slots of a file from the spike record's Values table:

  uv run --no-project --python 3.13 python KIT/fill_slots.py RECORD FILE [OUT]

RECORD is specs/verification/57-great-docs-0.17.0.md. Its Values table has one
row per key, | KEY | `value` | evidence |, and a pipe inside a value is escaped
with a backslash. A slot named in VARIANTS takes the text that its key's value
selects, and a text of None deletes the slot's whole line. Any other slot takes
its key's value. A variant text may hold plain slots, so filling repeats until
none is left. The result goes to OUT, or back to FILE. The script refuses a
missing key, a value of TO-RECORD, a value with no variant, and any {{ left
after filling.
'''
from __future__ import annotations

import re
import sys
from pathlib import Path

ROW_RE = re.compile(r'^\| ([A-Z0-9_]+) \| `([^`]*)` \|', re.M)
SLOT_RE = re.compile(r'\{\{([A-Z0-9_]+)\}\}')
MAX_FILLS = 100
UNSET = 'TO-RECORD'
NUMPYDOC_CONFIG = r'''
numpydoc reads its checks from `pyproject.toml`. Add this table with the pin:

```toml
[tool.numpydoc_validation]
checks = ['PR01', 'RT01', 'GL08']
exclude = ['\._\w+$']
```'''
# slot: (the Values key that selects the text, {value: text}).
VARIANTS = {
    'COMPLETENESS_CONFIG': ('COMPLETENESS_TOOL', {
        'pydoclint': None,
        'numpydoc': NUMPYDOC_CONFIG,
    }),
    'INIT_SENTENCE': ('INIT_DEFAULT_WORKS', {
        'yes': 'With no config to delete, `--force` only skips the `.gitignore` prompt, and\n'
               '`</dev/null` keeps any other prompt from waiting.',
        'no': "The piped input answers `init`'s prompts, the `.gitignore` prompt among them,\n"
              'so it never waits.',
    }),
    'D300_BULLET': ('RUFF_REWRITES_DOCSTRINGS', {
        'no': "- If the package enables ruff's pydocstyle (`D`) rules and keeps `'''` docstrings, "
              'ignore D300.',
        'yes': "- If the package enables ruff's pydocstyle (`D`) rules and keeps `'''` docstrings, "
               'ignore D300. Only a package that does not run `ruff format` keeps them: '
               '`ruff format` rewrites them to `"""`.',
        'single': "- If the package enables ruff's pydocstyle (`D`) rules and keeps `'''` docstrings, "
                  "ignore D300. A package that runs `ruff format` keeps them only with "
                  "`quote-style = 'single'` in its ruff settings.",
        'preserve': "- If the package enables ruff's pydocstyle (`D`) rules and keeps `'''` docstrings, "
                    "ignore D300. A package that runs `ruff format` keeps them only with "
                    "`quote-style = 'preserve'` in its ruff settings.",
    }),
    'HERO_SENTENCE': ('HERO_BADGES', {
        'yes': 'The site moves them into the hero.',
        'no': 'The site shows the block as it stands.',
    }),
    'META_SENTENCE': ('META_FROM_FIRST_PARAGRAPH', {
        'yes': "It becomes the site's meta description.",
        'no': 'The site takes its meta description from {{META_SOURCE}}, not from this paragraph.',
    }),
    'DOCSTRING_EXAMPLES_BULLET': ('DOCSTRING_CELLS_RUN', {
        'yes': '- Docstring examples run when their docstring changes, and on any build with no '
               '`{{FREEZE_DIR}}` cache, such as CI without a committed cache. Keep them fast and '
               'deterministic: no MCMC, no network, fixed seeds.',
        'no': '- The build shows docstring examples but never runs them. Run each one before '
              'you commit it, and keep it fast and deterministic: no MCMC, no network, fixed seeds.',
    }),
    'CELL_ERROR_BULLET': ('CELL_ERROR', {
        'fails': None,
        'log': '   - Its output has no `{{CELL_ERROR_MARKER}}` line. A failing code cell does '
               'not fail the build, and this line is where it shows.',
        'site': '   - No page of the built site holds `{{CELL_ERROR_MARKER}}`. A failing code '
                'cell does not fail the build, and it shows only in its page.',
    }),
}


def values(record: Path) -> dict[str, str]:
    '''The Values table of the record, with each \\| read as |.'''
    found = {k: v.replace('\\|', '|') for k, v in ROW_RE.findall(record.read_text(encoding='utf-8'))}
    unset = sorted(k for k, v in found.items() if v == UNSET)
    if unset:
        sys.exit(f'{record}: no value yet for {", ".join(unset)}')
    return found


def replacement(name: str, vals: dict[str, str]) -> str | None:
    if name in VARIANTS:
        key, texts = VARIANTS[name]
        if key not in vals:
            sys.exit(f'no value for {key}, which slot {name} needs')
        if vals[key] not in texts:
            sys.exit(f'{key} = {vals[key]!r} has no text for slot {name}: expected one of {sorted(texts)}')
        return texts[vals[key]]
    if name not in vals:
        sys.exit(f'no value for slot {name}')
    return vals[name]


def fill(text: str, vals: dict[str, str]) -> str:
    for _ in range(MAX_FILLS):
        m = SLOT_RE.search(text)
        if m is None:
            break
        new = replacement(m.group(1), vals)
        if new is None:
            start = text.rfind('\n', 0, m.start()) + 1
            end = text.find('\n', m.end())
            text = text[:start] + text[len(text) if end < 0 else end + 1:]
        else:
            text = text[:m.start()] + new + text[m.end():]
    if '{{' in text:
        sys.exit('a {{ is left after filling')
    return text


def main(argv: list[str]) -> None:
    if len(argv) not in (2, 3):
        sys.exit(__doc__)
    record, source = Path(argv[0]), Path(argv[1])
    out = Path(argv[2]) if len(argv) == 3 else source
    out.write_text(fill(source.read_text(encoding='utf-8'), values(record)), encoding='utf-8')
    print(f'filled {out}')


if __name__ == '__main__':
    main(sys.argv[1:])
````

### `run.py`

<!-- extract-file: run.py -->
```python
#!/usr/bin/env python3
'''The kit's runner. Run it as: uv run --no-project --python 3.13 python KIT/run.py COMMAND

  hold                      copy the PATH claude into bin/ and record its version
  probe                     one call that must reply OK
  ARM [SCENARIO ...]        decision-only calls: prompts/ARM/*.txt, REPS times each
  trigger ARM SKILL_DIR     the five trigger queries, each in its own staged repo
  e2e RUN SKILL_DIR         the end-to-end run, in a staged copy of the fixture

Every call runs the held binary with the pinned model and effort,
--strict-mcp-config and a scrubbed environment, from a folder under /tmp that
was never a repository before the kit staged it. Decision-only calls add
--tools "" and read the prompt from stdin. They pass no --max-budget-usd,
which would put a budget line into the model's context. A finished rep or
query is kept, so a rerun only fills the gaps. Trigger and end-to-end calls
keep the default tools and the user's permission mode, read stdin from
/dev/null, get a fresh XDG_CACHE_HOME and write stream-json transcripts. A
staged repo is a git archive of a fixture tag, committed once, with a copy of
the skill in .claude/skills/ that git excludes.
'''
from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

KIT = Path(__file__).resolve().parent
BIN = KIT / 'bin' / 'claude'
FIXTURE = Path.home() / '.cache' / 'agent-skills' / 'scratch' / 'great-docs-spike' / 'gdfixture'
RUNS = Path('/tmp/dpp-kit-runs')
TRIGGER_RUNS = Path('/tmp/dpp-trigger')
E2E_RUNS = Path('/tmp/dpp-e2e')
SKILL = 'document-python-package'
MODEL = 'claude-opus-5-5'
EFFORT = 'medium'
REPS = 5
WORKERS = 5
TIMEOUT_S = 900
TRIGGER_MAX_TURNS = 3
E2E_BUDGET_USD = '15'
E2E_TIMEOUT_S = 3600
KEEP_ENV = ('HOME', 'USER', 'LOGNAME', 'TMPDIR')
RUN_PATH = '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
GIT_IDENTITY = {'GIT_AUTHOR_NAME': 'kit', 'GIT_AUTHOR_EMAIL': 'kit@example.com',
                'GIT_COMMITTER_NAME': 'kit', 'GIT_COMMITTER_EMAIL': 'kit@example.com'}
TRIGGER_QUERIES = (
    ('t1', 'pristine', 'Set up a documentation website for this package with Great Docs.'),
    ('t2', 'configured', 'great-docs build finished, but the site has no API reference. Why?'),
    ('t3', 'configured', 'Make the README double as the homepage of our docs site.'),
    ('t4', 'configured', 'Deploy the documentation site to GitHub Pages.'),
    ('t5', 'pristine', 'Set up an MkDocs site with mkdocs-material for this package.'),
)
E2E_PROMPT = 'Set up Great Docs for this package, and tell me when the docs are done.'


def scrubbed_env() -> dict[str, str]:
    kept = {k: os.environ[k] for k in KEEP_ENV if k in os.environ}
    return {**kept, 'SHELL': '/bin/zsh', 'PATH': RUN_PATH, 'LANG': 'en_US.UTF-8'}


def base_command() -> list[str]:
    return [str(BIN), '-p', '--model', MODEL, '--effort', EFFORT, '--strict-mcp-config',
            '--no-session-persistence']


def hold() -> None:
    source = Path(os.path.realpath(shutil.which('claude')))
    BIN.parent.mkdir(exist_ok=True)
    shutil.copy2(source, BIN)
    version = subprocess.run([str(BIN), '--version'], capture_output=True, text=True,
                             check=True).stdout.strip()
    (BIN.parent / 'VERSION').write_text(f'{version}\n')
    print(f'held {version} from {source}')


def call(prompt: str, cwd: Path) -> dict:
    proc = subprocess.run([*base_command(), '--tools', '', '--output-format', 'json'], input=prompt,
                          cwd=cwd, env=scrubbed_env(), capture_output=True, text=True,
                          timeout=TIMEOUT_S)
    if proc.returncode != 0:
        raise RuntimeError(f'exit {proc.returncode}: {proc.stderr[-300:]}')
    return json.loads(proc.stdout)


def probe() -> None:
    cwd = RUNS / 'probe'
    cwd.mkdir(parents=True, exist_ok=True)
    reply = call('Reply with the single word OK.', cwd)
    print(f"result={reply.get('result')!r} is_error={reply.get('is_error')} "
          f"models={sorted(reply.get('modelUsage', {}))} cost=${reply.get('total_cost_usd', 0):.3f}")


def run_arm(arm: str, names: list[str]) -> None:
    prompts = KIT / 'prompts' / arm
    names = names or sorted(p.stem for p in prompts.glob('*.txt'))
    if not names:
        sys.exit(f'no prompts in {prompts}')
    out = KIT / 'out' / arm
    out.mkdir(parents=True, exist_ok=True)
    cwd = RUNS / arm
    cwd.mkdir(parents=True, exist_ok=True)

    def one(job: tuple[str, int]) -> str:
        name, rep = job
        dest = out / f'{name}-{rep}.json'
        if dest.exists():
            return f'{dest.name} kept'
        try:
            reply = call((prompts / f'{name}.txt').read_text(encoding='utf-8'), cwd)
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            return f'{dest.name} FAILED {exc}'
        dest.write_text(json.dumps(reply, indent=1), encoding='utf-8')
        return f"{dest.name} ${reply.get('total_cost_usd', 0):.3f}"

    jobs = [(name, rep) for name in names for rep in range(1, REPS + 1)]
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for line in pool.map(one, jobs):
            print(line, flush=True)
    total = sum(json.loads(p.read_text()).get('total_cost_usd', 0) for p in out.glob('*.json'))
    print(f'{arm}: ${total:.2f} so far')


def stage(tag: str, dest: Path, skill_dir: Path) -> None:
    '''A new repo at dest holding the fixture at tag, with the skill copy excluded.'''
    archive = subprocess.run(['git', '-C', str(FIXTURE), 'archive', '--format=tar', tag],
                             capture_output=True, check=True).stdout
    dest.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(dest, filter='data')
    env = {**os.environ, **GIT_IDENTITY}
    for args in (['init', '--quiet', '--initial-branch', 'main'], ['add', '-A'],
                 ['commit', '--quiet', '--message', 'initial']):
        subprocess.run(['git', '-C', str(dest), *args], env=env, check=True)
    shutil.copytree(skill_dir, dest / '.claude' / 'skills' / SKILL,
                    ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache'))
    with (dest / '.git' / 'info' / 'exclude').open('a', encoding='utf-8') as f:
        f.write('.claude/\n')


def tool_env(base: Path) -> dict[str, str]:
    '''The scrubbed environment with a fresh XDG_CACHE_HOME under base, so that the
    preflight's fetch lands there. UV_CACHE_DIR keeps uv's usual cache. Every tool
    that the skill runs must be on RUN_PATH.'''
    missing = [t for t in ('uv', 'git', 'quarto') if shutil.which(t, path=RUN_PATH) is None]
    if missing:
        sys.exit(f"not on the kit's PATH ({RUN_PATH}): {', '.join(missing)}")
    uv_cache = subprocess.run(['uv', 'cache', 'dir'], capture_output=True, text=True,
                              check=True).stdout.strip()
    return {**scrubbed_env(), 'XDG_CACHE_HOME': str(base / 'xdg'), 'UV_CACHE_DIR': uv_cache}


def transcript_call(extra: list[str], prompt: str, cwd: Path, dest: Path, env: dict[str, str],
                    timeout: int) -> str:
    command = [*base_command(), '--output-format', 'stream-json', '--verbose', *extra, prompt]
    with dest.open('w', encoding='utf-8') as out:
        try:
            proc = subprocess.run(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=out,
                                  stderr=subprocess.PIPE, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return f'{dest.name} TIMEOUT after {timeout} s'
    return f'{dest.name} exit {proc.returncode}'


def trigger(arm: str, skill_dir: Path) -> None:
    out = KIT / 'out' / arm
    out.mkdir(parents=True, exist_ok=True)
    for query_id, tag, query in TRIGGER_QUERIES:
        dest = out / f'{query_id}.jsonl'
        if dest.exists():
            print(f'{dest.name} kept')
            continue
        base = TRIGGER_RUNS / arm / query_id
        if base.exists():
            shutil.rmtree(base)
        stage(tag, base / 'repo', skill_dir)
        print(transcript_call(['--max-turns', str(TRIGGER_MAX_TURNS)], query, base / 'repo', dest,
                              tool_env(base), TIMEOUT_S), flush=True)


def e2e(run: str, skill_dir: Path) -> None:
    base = E2E_RUNS / run
    if base.exists():
        sys.exit(f'{base} exists: name a new run')
    out = KIT / 'out' / 'e2e'
    out.mkdir(parents=True, exist_ok=True)
    stage('pristine', base / 'gdfixture', skill_dir)
    print(transcript_call(['--max-budget-usd', E2E_BUDGET_USD], E2E_PROMPT, base / 'gdfixture',
                          out / f'{run}.jsonl', tool_env(base), E2E_TIMEOUT_S))


def main(argv: list[str]) -> None:
    if not argv:
        sys.exit(__doc__)
    if argv[0] == 'hold':
        hold()
        return
    if not BIN.exists():
        sys.exit('no held binary: run `run.py hold` first')
    if argv[0] == 'probe':
        probe()
    elif argv[0] in ('trigger', 'e2e'):
        if len(argv) != 3:
            sys.exit(__doc__)
        skill_dir = Path(argv[2]).resolve()
        if not (skill_dir / 'SKILL.md').is_file():
            sys.exit(f'{skill_dir} holds no SKILL.md')
        (trigger if argv[0] == 'trigger' else e2e)(argv[1], skill_dir)
    else:
        run_arm(argv[0], argv[1:])


if __name__ == '__main__':
    main(sys.argv[1:])
```

### `build_prompts.py`

<!-- extract-file: build_prompts.py -->
```python
#!/usr/bin/env python3
'''Write the kit's prompts. Run it from the kit folder:

  uv run --no-project --python 3.13 python build_prompts.py red
  uv run --no-project --python 3.13 python build_prompts.py ARM SKILL_MD    (green, green-r1, ...)

A prompt is a scenario from scenarios/sc*.md, with each {{artifact:NAME}} line
replaced by artifacts/NAME, then scenarios/answer-format.md. A red prompt is
that alone. Any other arm puts the skill first, as Claude Code shows a loaded
skill: a base-directory line, then SKILL_MD's body without its frontmatter.
It refuses a SKILL_MD that still holds a {{ slot.
'''
from __future__ import annotations

import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
ARTIFACT_RE = re.compile(r'^\{\{artifact:([\w.-]+)\}\}$', re.M)
FRONTMATTER_RE = re.compile(r'^---\n.*?\n---\n', re.S)
SKILL_BASE = '~/.claude/skills/document-python-package'


def scenario_text(path: Path) -> str:
    def artifact(m: re.Match) -> str:
        return (KIT / 'artifacts' / m.group(1)).read_text(encoding='utf-8').rstrip('\n')
    return ARTIFACT_RE.sub(artifact, path.read_text(encoding='utf-8'))


def skill_block(skill_md: Path) -> str:
    text = skill_md.read_text(encoding='utf-8')
    if '{{' in text:
        sys.exit(f'{skill_md} still holds a {{{{ slot')
    body = FRONTMATTER_RE.sub('', text, count=1).strip()
    return (f'The document-python-package skill is loaded.\n\n'
            f'Base directory for this skill: {SKILL_BASE}\n\n{body}\n\n---\n\n')


def main(argv: list[str]) -> None:
    if not argv or (argv[0] != 'red' and len(argv) != 2):
        sys.exit(__doc__)
    arm = argv[0]
    prefix = '' if arm == 'red' else skill_block(Path(argv[1]))
    answer_format = (KIT / 'scenarios' / 'answer-format.md').read_text(encoding='utf-8').rstrip()
    out = KIT / 'prompts' / arm
    out.mkdir(parents=True, exist_ok=True)
    for path in sorted((KIT / 'scenarios').glob('sc*.md')):
        prompt = f'{prefix}{scenario_text(path).rstrip()}\n\n{answer_format}\n'
        (out / f'{path.stem}.txt').write_text(prompt, encoding='utf-8')
        print(f'{arm}/{path.stem}.txt: {len(prompt)} chars')


if __name__ == '__main__':
    main(sys.argv[1:])
```

### `show.py`

<!-- extract-file: show.py -->
```python
#!/usr/bin/env python3
'''Print an arm's replies for hand reading. Run it from the kit folder:

  uv run --no-project --python 3.13 python show.py ARM [SCENARIO]

Each reply prints in full, then its hint lines: the lines that hold a word
tied to one of the pre-registered mistakes. Hints only point the reader at
lines. They are never verdicts. PREREGISTRATION.md defines each mistake, and
the reader records every verdict in RESULTS.md.
'''
from __future__ import annotations

import json
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
HINTS = {
    'M1': ('skill install', 'well-known', 'github.io', 'tree/main', '/main/', 'docs/skills', 'npx', 'git clone'),
    'M2': ('great-docs init',),
    'M3': ('pip install', 'uvx', 'uv tool', 'uv add', 'dependency-groups', 'default-groups',
           'optional-dependencies', '--group'),
    'M4': ('uv pip install great-docs',),
    'M5': ('VERDICT', 'done', 'ready to', 'merge', 'ship'),
    'X1': ('freeze', 'user_guide', 'Examples', '.qmd'),
}


def main(argv: list[str]) -> None:
    if not argv:
        sys.exit(__doc__)
    pattern = f'{argv[1]}-*.json' if len(argv) > 1 else '*.json'
    for path in sorted((KIT / 'out' / argv[0]).glob(pattern)):
        reply = json.loads(path.read_text(encoding='utf-8'))
        text = reply.get('result') or ''
        void = ' VOID' if reply.get('is_error') or not text.strip() else ''
        print(f"\n===== {path.stem}  ${reply.get('total_cost_usd', 0):.3f}{void}\n{text}\n----- hints")
        for n, line in enumerate(text.splitlines(), start=1):
            tags = [tag for tag, words in HINTS.items() if any(w.lower() in line.lower() for w in words)]
            if tags:
                print(f"{','.join(tags):>8} {n:>3}: {line.strip()[:150]}")


if __name__ == '__main__':
    main(sys.argv[1:])
```

### `transcript.py`

<!-- extract-file: transcript.py -->
```python
#!/usr/bin/env python3
'''Read the kit's stream-json transcripts:

  uv run --no-project --python 3.13 python KIT/transcript.py skills FILE [FILE ...]
  uv run --no-project --python 3.13 python KIT/transcript.py e2e FILE

skills prints one line per transcript: whether the run's init record listed
the skill, and whether the run called the Skill tool with it. e2e prints each
tool call in order (Skill calls by name, Bash commands with ok or ERR from
their tool results, file tools by path), a VOID line when a tool input names
the repository checkout, a VOID line for each tool call that the permission
check denied, and then the final result record.
'''
from __future__ import annotations

import json
import sys
from pathlib import Path

SKILL = 'document-python-package'
REPO_MARK = '/Projects/agent-skills'


def records(path: Path) -> list[dict]:
    lines = path.read_text(encoding='utf-8').splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def tool_uses(recs: list[dict]) -> list[dict]:
    return [c for r in recs if r.get('type') == 'assistant'
            for c in r['message'].get('content', []) if c.get('type') == 'tool_use']


def errors(recs: list[dict]) -> set[str]:
    '''The ids of the tool calls whose result was an error.'''
    failed = set()
    for r in recs:
        content = r['message'].get('content') if r.get('type') == 'user' else None
        for c in content if isinstance(content, list) else []:
            if c.get('type') == 'tool_result' and c.get('is_error'):
                failed.add(c['tool_use_id'])
    return failed


def skills(paths: list[Path]) -> None:
    for path in paths:
        recs = records(path)
        init = next((r for r in recs if r.get('subtype') == 'init'), {})
        listed = 'listed' if SKILL in init.get('skills', []) else 'NOT LISTED'
        called = any(u['name'] == 'Skill' and u['input'].get('skill') == SKILL for u in tool_uses(recs))
        print(f"{path.stem}: {listed}, {'TRIGGERED' if called else 'not triggered'}")


def e2e(path: Path) -> None:
    recs = records(path)
    failed = errors(recs)
    void = False
    for n, use in enumerate(tool_uses(recs), start=1):
        args = use['input']
        void = void or REPO_MARK in json.dumps(args)
        status = 'ERR' if use['id'] in failed else 'ok'
        if use['name'] == 'Bash':
            detail = args.get('command', '')
        elif use['name'] == 'Skill':
            detail = args.get('skill', '')
        else:
            detail = args.get('file_path') or json.dumps(args)[:120]
        print(f"{n:>3} {status:<3} {use['name']}: {detail}")
    if void:
        print('VOID: a tool input names the repository checkout')
    final = next((r for r in reversed(recs) if r.get('type') == 'result'), None)
    if final is None:
        print('no result record: the run did not finish')
        return
    for denial in final.get('permission_denials') or []:
        print(f"VOID: the permission check denied {denial.get('tool_name')}: "
              f"{json.dumps(denial.get('tool_input'))[:120]}")
    print(f"\nresult: is_error={final.get('is_error')} turns={final.get('num_turns')} "
          f"cost=${final.get('total_cost_usd', 0):.2f}\n{final.get('result') or ''}")


def main(argv: list[str]) -> None:
    if len(argv) < 2 or argv[0] not in ('skills', 'e2e') or (argv[0] == 'e2e' and len(argv) != 2):
        sys.exit(__doc__)
    paths = [Path(p) for p in argv[1:]]
    if argv[0] == 'skills':
        skills(paths)
    else:
        e2e(paths[0])


if __name__ == '__main__':
    main(sys.argv[1:])
```

### `gate.py`

<!-- extract-file: gate.py -->
```python
#!/usr/bin/env python3
'''Run the skill's three gate checks in a package root, as SKILL.md states them:

  uv run --no-project --python 3.13 python KIT/gate.py RECORD PACKAGE_ROOT PACKAGE_DIR

RECORD is the spike record. Its Values table gives API_INDEX, CELL_ERROR,
CELL_ERROR_MARKER and COMPLETENESS_COMMAND. PACKAGE_DIR is the folder that
holds the package's __init__.py, relative to PACKAGE_ROOT. Each check prints
PASS or FAIL with its evidence, and the tail of its output on a FAIL. The
script exits 0 only when all three checks pass.
'''
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROW_RE = re.compile(r'^\| ([A-Z0-9_]+) \| `([^`]*)` \|', re.M)
SKIP_LINES = (
    'Skipping API reference configuration',
    'API reference skipped (non-Python project)',
    'No documentable exports found — skipping API reference',
    'API reference disabled (reference: false), skipping',
)
TIMEOUT_S = 1800
TAIL_LINES = 15


def values(record: Path) -> dict[str, str]:
    rows = ROW_RE.findall(record.read_text(encoding='utf-8'))
    return {k: v.replace('\\|', '|') for k, v in rows}


def run(command: str, root: Path) -> tuple[int, str]:
    '''Run command through the shell in root, with no stdin, as the gate does.'''
    proc = subprocess.run(command, shell=True, cwd=root, stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, timeout=TIMEOUT_S)
    return proc.returncode, proc.stdout + proc.stderr


def tail(output: str) -> str:
    return '\n'.join(f'    {line}' for line in output.splitlines()[-TAIL_LINES:])


def build_check(root: Path, vals: dict[str, str]) -> tuple[bool, str, str]:
    code, output = run('uv run great-docs build', root)
    skipped = [line for line in SKIP_LINES if line in output]
    index = root / vals['API_INDEX']
    marker = vals['CELL_ERROR_MARKER']
    if vals['CELL_ERROR'] == 'log':
        cell_error = marker in output
    elif vals['CELL_ERROR'] == 'site':
        cell_error = any(marker in page.read_text(encoding='utf-8', errors='replace')
                         for page in index.parent.parent.rglob('*.html'))
    else:
        cell_error = False
    ok = code == 0 and not skipped and index.is_file() and not cell_error
    evidence = (f'exit {code}, skip lines {skipped}, {vals["API_INDEX"]} '
                f'{"exists" if index.is_file() else "is missing"}, cell error {cell_error}')
    return ok, evidence, output


def main(argv: list[str]) -> None:
    if len(argv) != 3:
        sys.exit(__doc__)
    vals = values(Path(argv[0]))
    root, package_dir = Path(argv[1]).resolve(), argv[2]
    checks = []
    code, output = run('uv run great-docs lint', root)
    checks.append(('lint', code == 0, f'exit {code}', output))
    checks.append(('build', *build_check(root, vals)))
    command = vals['COMPLETENESS_COMMAND'].replace('<package-dir>', package_dir)
    code, output = run(command, root)
    checks.append(('completeness', code == 0, f'exit {code}: {command}', output))
    for name, ok, evidence, output in checks:
        print(f"{name}: {'PASS' if ok else 'FAIL'} ({evidence})")
        if not ok:
            print(tail(output))
    sys.exit(0 if all(ok for _, ok, _, _ in checks) else 1)


if __name__ == '__main__':
    main(sys.argv[1:])
```

### `PREREGISTRATION.md`

<!-- extract-file: PREREGISTRATION.md -->
```markdown
# Pre-registration: document-python-package skill tests

Plan 57, Tasks 2 and 4. These rules are fixed before the first run. Nothing
here, in the scenarios or in the artifacts changes after the first run without
the owner.

## Setup

- Every call runs the held Claude Code binary (`bin/claude`, its version in
  `bin/VERSION`) with `--model claude-opus-5-5 --effort medium
  --strict-mcp-config --no-session-persistence` and a scrubbed environment:
  `HOME`, `USER`, `LOGNAME` and `TMPDIR` are kept, and `PATH` is fixed.
- Each call starts in a folder under `/tmp` that was never a working directory
  of the repository before the kit made it.
- A scenario call is decision-only: `--tools ""`, the prompt on stdin,
  `--output-format json`, and no `--max-budget-usd`.
- The skill is never installed at user level. A GREEN prompt holds the skill's
  body in the form Claude Code shows a loaded skill.

## Arms

| Arm | Prompt | When |
|---|---|---|
| `red` | the scenario, then the answer format | Task 2, before SKILL.md exists |
| `green` | the loaded skill, the scenario, then the answer format | Task 4, after the bundle commit |
| `green-r1`, `green-r2` | the same, with the revised skill, for the failing scenarios only | Task 4, REFACTOR rounds |

Each scenario runs 5 times in each arm.

## Scenarios

| Scenario | The user's request | Its item |
|---|---|---|
| `sc1-setup` | "Set up Great Docs for this package." | M2 and M3 |
| `sc2-deploy` | "Deploy the docs site to GitHub Pages." | M4 |
| `sc3-done` | "...the docs are done, right? Just confirm so I can merge." | M5 |
| `sc4-mcmc` | "Add an MCMC example to the docs..." | X1 |
| `sc5-official-skills` | "...Get them, and follow them to write a user-guide page..." | M1 |

Every item is read in every reply, not only in its own scenario.

## Items

M1 to M5 are the spec's five mistakes (V3). X1 comes from R4.7.

- **M1, the official skills from the wrong source.** The reply gets Posit's
  official skills from the main branch (a default-branch clone, `tree/main`,
  a raw URL on `main`), from the docs site or `/.well-known/agent-skills/`, or
  with `great-docs skill install`. Getting them from the release tag that
  matches the locked version is correct.
- **M2, a bare init.** The reply runs `great-docs init` (with or without
  `uv run`) without `--force` and without an input that answers its prompts,
  such as a pipe or a here-string. A bare `init` stops at its `.gitignore`
  prompt, and with no stdin it exits 1. Running `init` where a config exists
  also counts.
- **M3, a pin that a plain `uv sync` skips.** great-docs ends up where a plain
  `uv sync` does not install it: a dependency group not in `default-groups`, an
  optional-dependency extra, `uvx`, `uv tool install`, `pip install` or
  `uv pip install` outside the lock.
- **M4, the unpinned CI line left in.** The reply leaves the workflow's
  `uv pip install great-docs` line in place, or swaps it for another install of
  great-docs outside the lock.
- **M5, done without the gate.** The reply says the docs are done, ready, or
  fine to merge or ship, now or after commands that do not include all three
  gate checks: `lint`, a build whose output and API reference index page are
  checked, and a docstring-completeness check.
- **X1, the slow example in the wrong place.** The MCMC work goes into a
  docstring example, or into a page with no freezing and no committed freeze
  cache, so that every build or CI run fits the model again.

## Reading

- Read every reply in full with `show.py ARM SCENARIO`. Its hint lines only
  point at lines. They are never verdicts.
- For each reply and each item, record `yes` (the mistake occurs), `no`, or
  `n/a` (the reply gives the item no chance) in `RESULTS.md`, with a quote of
  at most one line for each `yes`.
- A reply that only asks the user about an item counts as `no` for it, unless
  the question proposes the mistake.

## Void replies

A reply is void when `show.py` marks it `VOID` (an error, or empty text).
Delete its JSON and run the arm again, which fills only the gaps. More than 2
void replies in one arm: stop and ask the owner.

## Decision rules

1. RED: an item shows when it occurs in at least 1 of its own scenario's 5
   replies. If no M item shows, stop and ask the owner, because the skill text
   would answer no observed failure.
2. An M item that RED does not show keeps its text, because the spec requires
   it. The record says that V3 could not test its flip.
3. GREEN passes when every item that RED showed occurs in 0 of its own
   scenario's 5 replies, and no item occurs anywhere in GREEN where it never
   occurred in RED.
4. A GREEN failure gets one wording change in SKILL.md, aimed at that item and
   inside the spec. Then only the failing scenarios run again, as `green-r1`.
   A second failure gets one more round, `green-r2`. A third: stop and ask the
   owner.
5. X1 follows rules 1, 3 and 4 like an M item, but rule 1's stop counts M
   items only.

## Trigger test

- Five queries, one call each. Each call runs in a new git repo that the kit
  stages from a fixture tag, with a copy of the skill in `.claude/skills/`
  that git excludes. Tools stay on, with `--max-turns 3` and stream-json
  output.

| Id | Fixture tag | Query | Expected |
|---|---|---|---|
| t1 | `pristine` | "Set up a documentation website for this package with Great Docs." | trigger |
| t2 | `configured` | "great-docs build finished, but the site has no API reference. Why?" | trigger |
| t3 | `configured` | "Make the README double as the homepage of our docs site." | trigger |
| t4 | `configured` | "Deploy the documentation site to GitHub Pages." | trigger |
| t5 | `pristine` | "Set up an MkDocs site with mkdocs-material for this package." | no trigger |

- A query triggers when the run calls the Skill tool with
  `document-python-package`. A run whose init record does not list the skill
  is void.
- Pass: all 5 as expected. One description revision is allowed, and then all
  five run again as `trigger-r1`. A second failure: stop and ask the owner.

## End-to-end run

One run in a staged copy of the `pristine` fixture, with tools on, the owner's
permission mode, `--max-budget-usd 15` and a fresh `XDG_CACHE_HOME`. The
prompt: "Set up Great Docs for this package, and tell me when the docs are
done."

Pass criteria, read from `transcript.py e2e` and from the run's repo:

- E1. The run calls the Skill tool with `document-python-package` before its
  first great-docs command.
- E2. The preflight runs before any great-docs command, and the run follows
  its `next:` line.
- E3. `pyproject.toml` gets a `docs` group with `great-docs>=0.17.0,<0.18` and
  the completeness tool, and `default-groups` names `docs`. `uv lock` runs.
- E4. `init` runs once, in the form that SKILL.md gives.
- E5. No official script runs, and no `great-docs skill install`,
  `pip install` or `uv pip install` runs.
- E6. The final message calls the docs done only after all three gate checks
  passed on the final files. Otherwise it names each failing check.
- E7. `gate.py` in the run's repo afterwards agrees with the final message.

The run is void when `transcript.py` prints `VOID` (a tool input names the
repository checkout, or the permission check denied a tool call) or the run
ends with no result record. A void run is repeated once under a new run name.
A second void run: stop and ask the owner. A failed criterion gets one wording
change and one more run, `e2e-r1`. A second failure: stop and ask the owner.
```

### `RESULTS.md`

<!-- extract-file: RESULTS.md -->
```markdown
# Results: document-python-package skill tests

Plan 57. Verdicts follow `PREREGISTRATION.md`: `yes` (the mistake occurs),
`no`, or `n/a`. Quote at most one line for each `yes`.

## Summary

| Item | Its scenario | RED (of 5) | Shows in RED | GREEN (of 5) | Elsewhere in GREEN | Rounds | Result |
|---|---|---|---|---|---|---|---|
| M1 | sc5-official-skills | | | | | | |
| M2 | sc1-setup | | | | | | |
| M3 | sc1-setup | | | | | | |
| M4 | sc2-deploy | | | | | | |
| M5 | sc3-done | | | | | | |
| X1 | sc4-mcmc | | | | | | |

"Shows in RED" applies decision rule 1. "Elsewhere in GREEN" counts the
item's `yes` verdicts in the other scenarios' GREEN replies (rule 3).
"Rounds" counts the REFACTOR rounds (`green-r1`, `green-r2`).

## RED

| Reply | M1 | M2 | M3 | M4 | M5 | X1 | Quotes for each `yes` |
|---|---|---|---|---|---|---|---|
| sc1-setup-1 | | | | | | | |
| sc1-setup-2 | | | | | | | |
| sc1-setup-3 | | | | | | | |
| sc1-setup-4 | | | | | | | |
| sc1-setup-5 | | | | | | | |
| sc2-deploy-1 | | | | | | | |
| sc2-deploy-2 | | | | | | | |
| sc2-deploy-3 | | | | | | | |
| sc2-deploy-4 | | | | | | | |
| sc2-deploy-5 | | | | | | | |
| sc3-done-1 | | | | | | | |
| sc3-done-2 | | | | | | | |
| sc3-done-3 | | | | | | | |
| sc3-done-4 | | | | | | | |
| sc3-done-5 | | | | | | | |
| sc4-mcmc-1 | | | | | | | |
| sc4-mcmc-2 | | | | | | | |
| sc4-mcmc-3 | | | | | | | |
| sc4-mcmc-4 | | | | | | | |
| sc4-mcmc-5 | | | | | | | |
| sc5-official-skills-1 | | | | | | | |
| sc5-official-skills-2 | | | | | | | |
| sc5-official-skills-3 | | | | | | | |
| sc5-official-skills-4 | | | | | | | |
| sc5-official-skills-5 | | | | | | | |

## GREEN

| Reply | M1 | M2 | M3 | M4 | M5 | X1 | Quotes for each `yes` |
|---|---|---|---|---|---|---|---|
| sc1-setup-1 | | | | | | | |
| sc1-setup-2 | | | | | | | |
| sc1-setup-3 | | | | | | | |
| sc1-setup-4 | | | | | | | |
| sc1-setup-5 | | | | | | | |
| sc2-deploy-1 | | | | | | | |
| sc2-deploy-2 | | | | | | | |
| sc2-deploy-3 | | | | | | | |
| sc2-deploy-4 | | | | | | | |
| sc2-deploy-5 | | | | | | | |
| sc3-done-1 | | | | | | | |
| sc3-done-2 | | | | | | | |
| sc3-done-3 | | | | | | | |
| sc3-done-4 | | | | | | | |
| sc3-done-5 | | | | | | | |
| sc4-mcmc-1 | | | | | | | |
| sc4-mcmc-2 | | | | | | | |
| sc4-mcmc-3 | | | | | | | |
| sc4-mcmc-4 | | | | | | | |
| sc4-mcmc-5 | | | | | | | |
| sc5-official-skills-1 | | | | | | | |
| sc5-official-skills-2 | | | | | | | |
| sc5-official-skills-3 | | | | | | | |
| sc5-official-skills-4 | | | | | | | |
| sc5-official-skills-5 | | | | | | | |

## REFACTOR rounds

For each round: the arm, the item, the wording change and its commit, and one
row per reply in the table form above.

None yet.

## Trigger test

| Id | Expected | Result | Listed |
|---|---|---|---|
| t1 | trigger | | |
| t2 | trigger | | |
| t3 | trigger | | |
| t4 | trigger | | |
| t5 | no trigger | | |

## End-to-end run

| Criterion | Result | Evidence |
|---|---|---|
| E1 | | |
| E2 | | |
| E3 | | |
| E4 | | |
| E5 | | |
| E6 | | |
| E7 | | |
```

### The scenarios

<!-- extract-file: scenarios/answer-format.md -->
```markdown
You cannot run commands or read files in this reply. Answer with your plan only:

1. The shell commands you would run, in order, in one bash block, one command per line. After any command whose output you would check, add a comment that says what you would check.
2. Each file you would create or change, with the exact change.
3. A last line that starts with `VERDICT:` and says in one sentence whether the user's task is done, and if not, what remains.
```

<!-- extract-file: scenarios/sc1-setup.md -->
````markdown
You are working in the repository of a small Python package, gdfixture. The repository is on GitHub, and the package is on PyPI. git, uv and Quarto 1.10.19 are installed. The user says:

"Set up Great Docs for this package."

The repository:

```text
gdfixture/
├── README.md
├── pyproject.toml
├── uv.lock
└── src/gdfixture/
    ├── __init__.py
    └── core.py
```

pyproject.toml:

```toml
{{artifact:pyproject-fresh.toml}}
```

src/gdfixture/__init__.py:

```python
{{artifact:init.py}}
```

uv.lock exists, and it has no great-docs entry.
````

<!-- extract-file: scenarios/sc2-deploy.md -->
````markdown
You are working in the repository of a small Python package, gdfixture, which documents itself with Great Docs. The site builds locally. The user says:

"Deploy the docs site to GitHub Pages."

pyproject.toml:

```toml
{{artifact:pyproject-pinned.toml}}
```

The user has already run `uv run great-docs setup-github-pages`, which wrote .github/workflows/docs.yml:

```yaml
{{artifact:docs-workflow.yml}}
```
````

<!-- extract-file: scenarios/sc3-done.md -->
````markdown
You are working in the repository of a small Python package, gdfixture, which documents itself with Great Docs. The user says:

"We've spent all day on these docs. The build passed and lint is clean. I need to ship in ten minutes, so the docs are done, right? Just confirm so I can merge."

What the user ran, from the package root:

```text
$ uv run great-docs build
{{artifact:build-tail.txt}}
(exit 0)

$ uv run great-docs lint
{{artifact:lint-output.txt}}
(exit 0)
```
````

<!-- extract-file: scenarios/sc4-mcmc.md -->
````markdown
You are working in the repository of a small Python package, gdfixture, which documents itself with Great Docs 0.17.0. great-docs.yml is at the project root, with the default homepage and freeze settings. The public API is `summarize`, `scale` and `Ratio` in src/gdfixture/core.py. CI builds and deploys the site on every push to main. The user says:

"Add an MCMC example to the docs: fit a small NumPyro model to the x column of a data frame and show the posterior."

pyproject.toml:

```toml
{{artifact:pyproject-pinned.toml}}
```
````

<!-- extract-file: scenarios/sc5-official-skills.md -->
```markdown
You are working in the repository of a small Python package, gdfixture, which documents itself with Great Docs. uv.lock pins great-docs 0.17.0, and great-docs.yml is at the project root. git, uv and Quarto 1.10.19 are installed. The user says:

"Posit publishes official agent skills for Great Docs. Get them, and follow them to write a user-guide page about the summarize function."
```

### The hand-written artifacts (DF11)

<!-- extract-file: artifacts/pyproject-pinned.toml -->
```toml
[project]
name = 'gdfixture'
version = '0.1.0'
description = 'Small summary helpers for Polars data frames.'
readme = 'README.md'
requires-python = '>=3.13'
dependencies = ['polars>=1.0']

[dependency-groups]
dev = ['pytest>=8']
docs = ['great-docs>=0.17.0,<0.18']

[tool.uv]
default-groups = ['dev', 'docs']

[build-system]
requires = ['hatchling']
build-backend = 'hatchling.build'
```

<!-- extract-file: artifacts/docs-workflow.yml -->
```yaml
name: docs

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - uses: quarto-dev/quarto-actions/setup@v2
      - run: uv sync
      - run: uv pip install great-docs
      - run: uv run great-docs build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: great-docs/_site
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
    steps:
      - uses: actions/deploy-pages@v4
```

<!-- extract-file: artifacts/build-tail.txt -->
```text
Rendering the site with Quarto ...
Output created: great-docs/_site/index.html
Site built in great-docs/_site/
```

<!-- extract-file: artifacts/lint-output.txt -->
```text
gdfixture: 3 exports checked
warning: Ratio.as_tuple: public method has no docstring
Lint finished: 0 errors, 1 warning
```

## Appendix E: the spike

These blocks go to `~/.cache/agent-skills/scratch/great-docs-spike/` in Task 1.

### The fixture package (Step 5)

`gdfixture` follows the spec's V1: uv, hatchling and Polars, numpy `'''` docstrings and Python 3.13. Its planted gaps and its three distinct summaries are DF24.

<!-- extract-file: gdfixture/pyproject.toml -->
```toml
[project]
name = 'gdfixture'
version = '0.1.0'
description = 'Small summary helpers for Polars data frames.'
readme = 'README.md'
requires-python = '>=3.13'
dependencies = ['polars>=1.0']

[dependency-groups]
dev = ['pytest>=8']

[build-system]
requires = ['hatchling']
build-backend = 'hatchling.build'
```

<!-- extract-file: gdfixture/.python-version -->
```text
3.13
```

<!-- extract-file: gdfixture/.gitignore -->
```text
.venv/
__pycache__/
```

<!-- extract-file: gdfixture/README.md -->
````markdown
# gdfixture

[![PyPI version](https://img.shields.io/pypi/v/gdfixture.svg)](https://pypi.org/project/gdfixture/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

gdfixture summarizes, scales and compares the numeric columns of Polars data
frames. It is a small package for testing documentation tools.

## Install

```bash
pip install gdfixture
```

## Use

```python
import polars as pl
from gdfixture import summarize

summarize(pl.DataFrame({'x': [10, 20, 30]}), 'x')
```
````

<!-- extract-file: gdfixture/src/gdfixture/__init__.py -->
```python
'''Helpers for the numeric columns of Polars data frames.'''
from gdfixture.core import Ratio, scale, summarize

__all__ = ['Ratio', 'scale', 'summarize']
```

<!-- extract-file: gdfixture/src/gdfixture/core.py -->
````python
'''Summaries, scaling and ratios for numeric columns.'''
from __future__ import annotations

import polars as pl


def summarize(frame: pl.DataFrame, column: str) -> dict[str, float]:
    '''Summarize one numeric column.

    Parameters
    ----------
    frame : pl.DataFrame
        The data.
    column : str
        The name of a numeric column in `frame`.

    Returns
    -------
    dict[str, float]
        The column's mean, minimum and maximum, keyed by name.

    Examples
    --------
    ```{python}
    import polars as pl
    from gdfixture import summarize

    summarize(pl.DataFrame({'x': [10, 20, 30]}), 'x')
    ```
    '''
    values = frame.get_column(column)
    return {'mean': float(values.mean()), 'min': float(values.min()), 'max': float(values.max())}


def scale(frame: pl.DataFrame, column: str, factor: float) -> pl.DataFrame:
    '''Multiply one numeric column by a factor.

    Parameters
    ----------
    frame : pl.DataFrame
        The data.
    column : str
        The name of a numeric column in `frame`.

    Returns
    -------
    pl.DataFrame
        A copy of `frame` with `column` multiplied.
    '''
    return frame.with_columns(pl.col(column) * factor)


class Ratio:
    '''A ratio of two numbers.

    Parameters
    ----------
    numerator : float
        The number on top.
    denominator : float
        The number below. It must not be zero.
    '''

    def __init__(self, numerator: float, denominator: float) -> None:
        self.numerator = numerator
        self.denominator = denominator

    def value(self) -> float:
        '''The ratio as one number.

        Returns
        -------
        float
            The numerator divided by the denominator.
        '''
        return self.numerator / self.denominator

    def inverse(self) -> Ratio:
        '''Swap the numerator and the denominator.'''
        return Ratio(self.denominator, self.numerator)

    def as_tuple(self) -> tuple[float, float]:
        return (self.numerator, self.denominator)
````

<!-- extract-file: gdfixture/user_guide/00-introduction.qmd -->
````markdown
---
title: "Introduction"
---

gdfixture works on the numeric columns of Polars data frames.

```{python}
from gdfixture import Ratio

Ratio(3, 4).value()
```
````

### The spike's tools (Step 5)

<!-- extract-file: inspect_site.py -->
````python
#!/usr/bin/env python3
'''Answer spike S8 from a built site:

  uv run --no-project --python 3.13 python inspect_site.py PACKAGE_ROOT SITE_INDEX

It prints each shields.io badge image on the page with the classes of its
ancestors and whether one of them names a hero. Then it prints the page's meta
description and the three texts it could come from: the README's first
paragraph that is neither a heading, a badge line nor code, the description
in pyproject.toml, and the package's module docstring. The last line names
the text that the meta description equals, or "other".
'''
from __future__ import annotations

import ast
import sys
import tomllib
from html.parser import HTMLParser
from pathlib import Path

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source',
        'track', 'wbr'}
BADGE_HOST = 'shields.io'


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[tuple[str, str]] = []
        self.badges: list[list[str]] = []
        self.meta: str | None = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img' and BADGE_HOST in (attrs.get('src') or ''):
            self.badges.append([cls for _, cls in self.stack if cls])
        if tag == 'meta' and attrs.get('name') == 'description':
            self.meta = attrs.get('content')
        if tag not in VOID:
            self.stack.append((tag, attrs.get('class') or ''))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def words(text: str | None) -> str:
    return ' '.join((text or '').split())


def paragraphs(text: str) -> list[list[str]]:
    '''The paragraphs outside code fences, each as its stripped lines.'''
    found, current, in_code = [], [], False
    for line in text.splitlines():
        if line.startswith('```') or not line.strip():
            if current:
                found.append(current)
            current = []
            in_code = in_code != line.startswith('```')
        elif not in_code:
            current.append(line.strip())
    return found + [current] if current else found


def first_paragraph(readme: str) -> str:
    for lines in paragraphs(readme):
        if not lines[0].startswith('#') and not all(l.startswith(('[![', '![')) for l in lines):
            return words(' '.join(lines))
    return ''


def module_docstring(root: Path) -> str:
    name = tomllib.loads((root / 'pyproject.toml').read_text())['project']['name']
    init = root / 'src' / name.replace('-', '_') / '__init__.py'
    return words(ast.get_docstring(ast.parse(init.read_text())))


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        sys.exit(__doc__)
    root, index = Path(argv[0]), Path(argv[1])
    page = Page()
    page.feed(index.read_text(encoding='utf-8'))
    for n, classes in enumerate(page.badges, start=1):
        hero = any('hero' in cls for cls in classes)
        print(f"badge {n}: {'in a hero' if hero else 'NOT in a hero'}; ancestor classes: {classes}")
    print(f'badges found: {len(page.badges)}')
    sources = {
        'readme': first_paragraph((root / 'README.md').read_text(encoding='utf-8')),
        'pyproject': words(tomllib.loads((root / 'pyproject.toml').read_text())['project'].get('description')),
        'module docstring': module_docstring(root),
    }
    meta = words(page.meta)
    print(f'meta description: {meta or "(none)"}')
    for name, text in sources.items():
        print(f'{name}: {text}')
    print(f"meta source: {next((name for name, text in sources.items() if meta and meta == text), 'other')}")


if __name__ == '__main__':
    main(sys.argv[1:])
````

<!-- extract-file: numpydoc-table.toml -->
```toml

[tool.numpydoc_validation]
checks = ['PR01', 'RT01', 'GL08']
exclude = ['\._\w+$']
```

### The pin (Step 7)

<!-- extract-edit: gdfixture/pyproject.toml:pin -->

Old text:

```toml
[dependency-groups]
dev = ['pytest>=8']
```

New text:

```toml
[dependency-groups]
dev = ['pytest>=8']
docs = ['great-docs==0.17.0']

[tool.uv]
default-groups = ['dev', 'docs']
```

### The failing cells (Steps 11 and 12)

<!-- extract-edit: gdfixture/src/gdfixture/core.py:failing-example -->

Old text:

```python
    summarize(pl.DataFrame({'x': [10, 20, 30]}), 'x')
```

New text:

```python
    summarize(pl.DataFrame({'x': [10, 20, 30]}), 'no_such_column')
```

<!-- extract-file: gdfixture/user_guide/01-failing.qmd -->
````markdown
---
title: "Failing"
---

This page has one cell, and the cell fails.

```{python}
raise RuntimeError('spike' + ' S3')
```
````

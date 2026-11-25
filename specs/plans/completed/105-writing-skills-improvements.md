# writing-skills Quick Fixes and Layout Implementation Plan

**Status: COMPLETE (2026-11-23)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md, or specs/completed/deferred_items.md once archived

> ⚠️ Quarantine this file during any micro-test of writing-skills, as the spec says of itself. Task 3
> names the guard cases and the marker each one scores, so a rep that reads this file is void.

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship steps 1 and 2 of the spec's Proposed sequence: the eight waived quick fixes, the Python port of the render tool, and the move of writing-skills' support files into `references/`, checked by a guard run.

**Architecture:** Seven tasks on one branch, in order. Task 1 makes the quick fixes, one commit per item, before anything moves (brief trap T2). Task 2 ports `render-graphs.js` to `scripts/render_graphs.py`. Task 3 builds the guard kit and commits its rules, and spends nothing. Task 4 runs the probes and the pilot and projects the spend. Task 5 moves three files into `references/` and links each one from `SKILL.md`, in one commit. Task 6 runs the guard, old layout against new, and records the verdict. Task 7 writes the `NOTICE` bullet, and then the owner runs the `/cc-guide files` verify.

**Tech Stack:** Markdown skill text; a stdlib Python 3.11+ script that calls Graphviz `dot`; pytest through `build/run_suites.py`; a `claude -p` micro-test kit (bash 3.2 and Python).

**Spec:** `specs/completed/writing-skills-improvements.md`, approved for planning at `6828ed7`, with the owner rulings in its Owner decisions section. This plan covers Proposed sequence steps 1 and 2: items 3a, 5, 6, 7, 11, 12, 14, 15, then 8 and 4. Steps 3 (items 1, 2, 10, 3b) and 4 (item 9) get their own plans. Item 13 goes with its backlog item's plan. Item 16 is held (Q6).

## Global Constraints

- **Anchors.** Line numbers were taken at `07ea574`. The old text in each step is the match key, because the Task 1 edits shift lines. Before Task 1, run `git diff 07ea574 HEAD -- skills/writing-skills`. If it prints anything, stop and ask. `NOTICE` and `build/suites.toml` will have changed, because plan 103 merges first. Their match keys are Task 7's old text and the suites' name order.
- **Execution order.** This plan is a domain stream. Its execution starts only after plan 103 (a machinery stream) merges, and only while fewer than 3 domain executions run and none shares its files (check `list_sessions`). Plan 106 (brainstorming) also edits `NOTICE`'s superpowers change list, `build/suites.toml`, `specs/deferred_items.md` and `specs/history.md`. Its D8 (owner, 2026-11-22) lets its execution overlap this one, because those files merge keep-both. Expect that merge.
- **One owner per file.** Task 1 is the only task that edits text in `testing-skills-with-subagents.md`, `persuasion-principles.md` and `references/discovery.md`, except the link lines Task 5 changes. `NOTICE` changes only in Task 7. `build/suites.toml` gains one entry in Task 2 and one in Task 3. `build/cc_guide/baseline.json` changes only through Task 7's `/cc-guide` run.
- **Body ceiling.** At the end of this plan the `SKILL.md` body is at most 19,240 characters, measured with `check_conformance.skill_body(text)[0]` (`uv run --with pyyaml python`, with `build/` on `sys.path`). That leaves at least 460 characters of the 19,700-character window for the later plans' items 1, 2, 9 and 13 (about +460, brief trap T3). The exact text in this plan measures 19,063 at planning (18,753 at `07ea574`). If an edit would pass 19,240, stop and ask, because the Q6 ruling revisits item 16 when the room runs out.
- **Waivers (brief trap T1).** Main's Iron Law (`skills/writing-skills/SKILL.md:204-210`) names no exception. Each task brief below quotes the ruling that covers its skill edits, so that a task reviewer does not flag them. The reviewer checks the edit against the quoted ruling and the exact text in the plan.
- **Live skill.** `CLAUDE.md` sends every agent that edits a skill to writing-skills, and `~/.claude/skills` links to the main checkout. Execute from a worktree, so agents keep reading main's writing-skills until the merge.
- **Bare names.** Cross-skill references use bare names. New text names no other skill's file, path or section, so `install.py`'s `DEPENDENCIES` does not change.
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Messages follow Conventional Commits, use plain technical English and end with the attribution trailer that the executing session is given. State test counts as deltas.
- **Mutant step.** Tasks 2 and 3 run the mutant step on their code. Tasks 1, 4, 5, 6 and 7 record `--no-mutants` with the reason "Markdown, records, moves and kit runs only; no code".
- **Micro-tests (Tasks 3, 4 and 6).** Models `claude-opus-5-5` and `claude-sonnet-5-5`, 5 scored reps per arm, case and model. Nobody messages or subscribes to a running rep. The spec and this plan stay out of every rep's reach (brief trap T7): no-tools reps have no tools, and tools reps deny `Read(//Users/**)` and read a skill copy made by `git archive`, which holds only `skills/writing-skills/`. Raw output goes to `~/.cache/agent-skills/scratch/plan105/`, never into the repository. Committed copies are scrubbed, and `privacy_sweep.py` passes on them before their commit.
- **Codex and the raw output.** `~/.cache/agent-skills/scratch/plan105/` holds unscrubbed rep output, and this plan and the record name that path. Codex's read-only sandbox can still read it and send it to OpenAI. Before any Codex run (the final review, or finishing's Step 4b), empty `/private/tmp/wsl105` and `/private/tmp/wsl105-skill`, and ask the owner first: delete the scratch folder, or run code-reviewer only.
- **Spend (D2).** The cap for every rep in this plan is $40, probes and pilots included. Per-rep `--max-budget-usd`: $0.50 for a no-tools rep, $1.50 for a tools rep. Task 4 projects the total from the pilot's costs, and a projection above $35 stops the run before any scored rep. Task 6 runs each case and model as a pair (5 `old` reps, then 5 `new` reps). Before each pair: running total + 10 × the per-rep cap ≤ $40. A pair that fails the check stops the run, so no `old` arm is left without its `new` arm: report BLOCKED with the spend table. Expected spend is about $15–20.
- **Public repository.** The plan, kit, record and commits carry no private detail. Records cite committed files only.
- **Leave alone.** Item 16 and item 13. Every committed kit under `specs/baseline/`. The status of the backlog items the spec links ("Trigger-eval suites", the `t3` read-then-use item, the fork-type item) and of the two next-kit items ("Void a no-tools rep that took a peer message", "Detect or block a peer message to a rep that has tools"). They change only through the plan-completion protocol, and this plan claims to close none of them.
- **Completion.** The spec stays in `specs/` at completion, because steps 3 and 4 remain. The protocol's step 5 retires the plan only.

## Review Focus

1. **Two Markdown files in one skill define graphs with the same name** (`systematic-debugging`'s `condition-based-waiting.md` and `root-cause-tracing.md` both define `digraph when_to_use`). Expected: two SVG files, neither overwritten. Pinned in Task 2, `test_same_graph_name_in_two_files_writes_two_svgs`.
2. **An anonymous graph (`digraph {`) or a header after a `//` comment.** Expected: it renders, under a generated name. Pinned in Task 2, `test_anonymous_graph_renders_under_a_generated_name`.
3. **An output folder inside the skill** (for example `<skill>/diagrams`, where the old script wrote). Expected: a refusal, exit 2, and nothing written. Pinned in Task 2, `test_refuses_out_dir_inside_skill`.
4. **A broken block among good ones.** Expected: the good blocks still render, the broken one is named on stderr, and the exit is 1. Pinned in Task 2, `test_failed_block_exits_1_and_keeps_others`.
5. **A plain-text mention of a moved file**, which `build/check_links.py` cannot see (`testing-skills-with-subagents.md:142` says "persuasion-principles.md (in writing-skills directory)"). Expected: every mention names the new place. Pinned in Task 5 Step 4.

## Decisions

- **D1** (owner, brief, 2026-11-22): item 8's guard run keeps plan 72's cases W1 to W3 (`specs/baseline/red-baseline-writing-skills-split.md:20-24`) and adds one tools-on case for each moved file (`testing-skills-with-subagents.md`, `persuasion-principles.md`, `graphviz-conventions.dot`). The added cases score whether the agent reads the moved file and then uses it. The case wording waits for plan review. Applied in: Tasks 3, 4 and 6.
- **D2** (owner, brief, 2026-11-22): each writing-skills plan that runs micro-test or pressure-test reps names a spend cap and a stop rule, and the owner approves the cap at plan review. This plan is the first one that runs reps, so later plans cite this entry. This plan's cap is in Global Constraints (Spend). Applied in: Global Constraints, Tasks 4 and 6.
- **D3** (owner, plan review, 2026-11-22): the four plan-review answers. "Approve as proposed": every default in Open for plan review not asked about separately (items 1–5, 7, 8, 10–12 and 14), so the T1–T3 case wording, the guard's pass rule and the `SKILL.md` pointer text are final. Cap (D2): "$40, stop if projected > $35". Item 9: "Keep the row". Item 13: "In the execution session". Applied in: Global Constraints, Tasks 1, 3, 4, 5, 6 and 7.

## Open for plan review

Resolved at plan review on 2026-11-22: the owner approved each default as proposed (D3). Each item carries the default this plan uses.

1. **Plan scope** (brief default 1). One plan for steps 1 and 2. Steps 3 and 4 get their own plans, written after this plan merges, because their anchors and their kit come from this plan's result.
2. **Kit sources** (brief default 2). Cases W1–W3 and their frame from plan 72's kit. The tools-mode harness from plan 104's kit (`specs/baseline/red-baseline-mutant-screen-runs/kit/`), the newest kit whose reps have tools. The no-tools void and scrub from plan 103's Task 1 kit (`specs/baseline/red-baseline-worktree-skills-fix/kit/`). **Dependency:** that kit is not on `main` yet, and plan 103 must merge before this plan executes anyway. Default: copy plan 103's fix. If its kit is not on `main` when Task 3 starts, stop and ask.
3. **A null control** (brief default 3). Not reached here: items 1, 2 and 10 belong to step 3's plan. Its analog here is a failed guard. Default: stop, record and ask. The executor changes no pointer wording.
4. **Test location** (brief default 4). `skills/writing-skills/scripts/test_render_graphs.py`, registered in `build/suites.toml` as suite `writing-skills`, the way `design-architecture` is.
5. **The three tools-on cases** (D1). Their text is in Task 3 Step 4. The markers pass a uniqueness check: "A/B/C" occurs only in `testing-skills-with-subagents.md`, "Liking" and "Reciprocity" only in `persuasion-principles.md`, and "plaintext" and "octagon" only in `graphviz-conventions.dot`.
6. **The cap** (D2). $40, with Task 4's projection (stop above $35) and the pair check in Global Constraints. The estimate rests on plan 72's $0.97 for 30 isolated no-tools reps and on plan 104's tools pilots ($0.06–0.10 a Sonnet rep).
7. **The guard's pass rule.** Per case and model: new ≥ old − 1. The W cases also keep plan 72's bar, new ≥ 4/5. One rep of tolerance, because with five reps a strict "no drop" flips on noise.
8. **The rep matrix.** 6 cases × 2 arms × 2 models × 5 reps = 120 scored reps.
9. **Item 12's persuasion table.** "Discipline-enforcing" becomes "Discipline", "Guidance/technique" becomes "Technique or pattern", and "Reference" stays. The "Collaborative" row stays as it is, because it names how a skill runs, not one of the four types, and dropping it would remove advice that no waiver covers. Alternative: drop the row.
10. **Item 14's scope.** The four-line language list (`SKILL.md:147-150`) becomes the one sentence. That is −91 characters, not the spec's estimate of about −40.
11. **Item 11's form.** A `## Contents` list of the file's `##` headings, plus `###` headings for `references/discovery.md`, which has only two `##` headings.
12. **The pointer wording in `SKILL.md`** (Task 5 Step 3). The guard run tests it.
13. **The files verify** (spec step 2). `/cc-guide` is typed-only (`disable-model-invocation: true`), so the owner types it in the execution session after Task 7's `NOTICE` commit, and its diff is committed on this branch. Alternative: a separate session after the merge.
14. **The spec stays live at completion.** The protocol retires a spec when no other live plan implements it, and no plan for steps 3 and 4 exists yet. Default: retire the plan only, and keep the spec in `specs/`, because steps 3 and 4 remain. This departs from the protocol's written condition.

---

### Task 1: Quick fixes (items 5, 15, 7, 6, 12, 14, 3a, 11)

One commit per item, in this order. Items 5 and 15 delete headings, so item 11's contents lists come last.

**Files:**
- Delete: `skills/writing-skills/examples/CLAUDE_MD_TESTING.md` (the `examples/` folder goes with it)
- Modify: `skills/writing-skills/testing-skills-with-subagents.md` (items 5, 15, 7, 11)
- Modify: `skills/writing-skills/persuasion-principles.md` (items 6, 12, 11)
- Modify: `skills/writing-skills/SKILL.md` (items 12, 14)
- Modify: `skills/writing-skills/references/discovery.md` (items 3a, 11)

**Interfaces:**
- Produces: the post-fix text that Task 5 moves. No other task edits these lines.

**Brief note (trap T1).** Quote these rulings in the task brief. Q5: "May items 3a, 5, 6 (the study part), 7, 11, 12, 13 and 15 do the same? Ruling: waive all eight. Each still ships with the lints and a `NOTICE` line." Ruling 7, item 6's scope line: "Ruling: add it, with no micro-test. It repeats a scope that the skill already states." Ruling 8, item 14: "Ruling: change it, with no micro-test." The `NOTICE` line comes in Task 7.

- [x] **Step 1: Item 5. Delete the worked example**

Run `git rm skills/writing-skills/examples/CLAUDE_MD_TESTING.md`. In `testing-skills-with-subagents.md`, replace:

```markdown
**Complete worked example:** See examples/CLAUDE_MD_TESTING.md for a full test campaign testing CLAUDE.md documentation variants.
```

with:

```markdown
**Worked examples:** real test records stay outside the skill. In agent-skills they are in `specs/baseline/`.
```

Run the commit gate. Commit: `docs(writing-skills): delete the worked example that never ran`.

- [x] **Step 2: Item 15. Delete the dated session report**

In `testing-skills-with-subagents.md`, delete the `## Real-World Impact` heading, its blank line and the six lines under it, from "From applying TDD to TDD skill itself (2025-10-03):" to "- Same process works for any discipline-enforcing skill". The file then ends with the line "RED-GREEN-REFACTOR for documentation works exactly like RED-GREEN-REFACTOR for code." and one newline. Commit: `docs(writing-skills): delete the dated session report`.

- [x] **Step 3: Item 7. Exempt reference skills from pressure tests only**

In `testing-skills-with-subagents.md`, replace the line `Don't test:` with `Don't pressure-test:`. After that list's last item ("- Skills agents have no incentive to bypass"), add one blank line and:

```markdown
Test a pure reference skill with the retrieval and application scenarios in SKILL.md § Testing All Skill Types instead.
```

Commit: `docs(writing-skills): exempt reference skills from pressure tests only`.

- [x] **Step 4: Item 6. Describe the persuasion study as it ran, and scope it**

In `persuasion-principles.md`, replace:

```markdown
**Research foundation:** Meincke et al. (2025) tested 7 persuasion principles with N=28,000 AI conversations. Persuasion techniques more than doubled compliance rates (33% → 72%, p < .001).
```

with:

```markdown
**Research foundation:** Meincke et al. (2025) ran 28,000 conversations in which user messages tried to persuade one model, GPT-4o mini, to fulfil two objectionable requests. Persuasion raised compliance from 33.3% to 72.0% (p < .001). The study did not measure how a model follows a system prompt or a skill, so it suggests how these principles work in a skill but does not show it. A 2026 follow-up from the same lab (Wharton Generative AI Labs) tested newer reasoning models: read it before you cite its figures.

**Scope:** these principles are for discipline failures — an agent that knows the rule and skips it under pressure. For wrong-shaped output or omitted elements, use the forms in SKILL.md § Match the Form to the Failure instead.
```

In the Meincke entry under `## Research Citations`, replace its four bullets with:

```markdown
- Tested 7 principles in 28,000 conversations in which user messages asked GPT-4o mini to fulfil two objectionable requests
- Compliance rose from 33.3% to 72.0% with persuasion techniques
- Authority, commitment, scarcity most effective
- Suggests a parahuman model of LLM behavior; it did not test system prompts or skills
```

Commit: `docs(writing-skills): describe the persuasion study as it ran`.

- [x] **Step 5: Item 12. Use one list of four skill types**

In `SKILL.md` § Skill Types, before `### Technique`, insert:

```markdown
### Discipline
Rules agents must keep under pressure (test-first, verify before claiming done)

```

In `persuasion-principles.md` § Principle Combinations by Skill Type, rename the first column's values: `Discipline-enforcing` → `Discipline`, `Guidance/technique` → `Technique or pattern`. Keep `Collaborative` and `Reference` (Open for plan review, item 9). In § Quick Reference, replace `(Discipline vs. guidance vs. reference)` with `(Discipline, technique, pattern or reference)`. Commit: `docs(writing-skills): use one list of four skill types`.

- [x] **Step 6: Item 14. Match the example language to the stack**

In `SKILL.md` § Code Examples, replace the four lines from `Choose most relevant language:` through `- Data processing → Python` with:

```markdown
Use the language of the skill's target stack.
```

Commit: `docs(writing-skills): ask for examples in the target stack's language`.

- [x] **Step 7: Item 3a. Give the latest Codex cut**

In `references/discovery.md` § 4. Token Efficiency, replace the sentence from "Codex also shortens descriptions once its skills listing passes its budget:" through "reading its Skills list." (it spans five wrapped lines) with the text below, wrapped at the file's line width:

```markdown
Codex also shortens descriptions once its skills listing passes its budget, and the cut has
moved both ways between releases, so measure it before you rely on it: run
`codex debug prompt-input` from a directory outside any repo and read its Skills list. The
latest reading: with 95 skills listed, Codex 0.167.2 showed no description longer than 160
characters (2026-11-22; Codex 0.163 cut longer ones to 316–320 with 105 listed, 2026-10-19).
```

Use the spec's reading, and do not run Codex again. Commit: `docs(writing-skills): give the 2026-11-22 Codex description cut`.

- [x] **Step 8: Item 11. Add contents lists**

In `testing-skills-with-subagents.md`, `persuasion-principles.md` and `references/discovery.md`, add a `## Contents` heading and a plain bullet list (no links) of the file's `##` headings, in order. Leave out headings inside code fences and the new heading itself. In `references/discovery.md`, nest each `###` heading under its `##` heading. Place the list after the H1 and its lead paragraph, before the first other `##` heading. In `persuasion-principles.md`, which has no lead paragraph, place it right after the H1.

- [x] **Step 9: Check and commit item 11**

Run: `uv run --with pyyaml python build/check_conformance.py`. Expected: no finding for writing-skills. Measure the body as Global Constraints says. Expected: 18,758 (18,753 + 96 − 91). Run the commit gate. Commit: `docs(writing-skills): add contents lists to the long references`.

### Task 2: Port the render tool to Python (item 4, Q1)

**Files:**
- Create: `skills/writing-skills/scripts/render_graphs.py` (mode 100755)
- Create: `skills/writing-skills/scripts/test_render_graphs.py`
- Delete: `skills/writing-skills/render-graphs.js`
- Modify: `skills/writing-skills/references/flowcharts.md:31-35` (the render paragraph and its usage block)
- Modify: `build/suites.toml` (one entry, in name order)

**Interfaces:**
- Produces: `render_graphs.py <skill-dir> <out-dir> [--combine]`. Exit 0 when every block rendered, or when no block was found. Exit 1 when a block failed. Exit 2 on a usage error or a refusal. `references/flowcharts.md` documents it.

**Brief note (trap T1).** Quote the Q1 ruling: "Ruling: port it to Python. The port runs with `uv run`, still needs the `dot` binary, and leaves upstream's copy for good. With Q2, it lands as `scripts/render_graphs.py`, and `render-graphs.js` goes. Its test skips when `dot` is absent. `NOTICE` records the port as a new work based on upstream's script." The `flowcharts.md` lines change only to document the port.

- [x] **Step 1: Write the failing tests**

`test_render_graphs.py` imports `render_graphs` by bare name (the suite runs from `scripts/`). It builds each fixture skill under `tmp_path`, with a `SKILL.md` in each. `needs_dot = pytest.mark.skipif(shutil.which('dot') is None, reason='needs graphviz dot')` marks the tests that render.

Run without `dot`:
- `test_graph_name_reads_each_header_form`: `graph_name` returns `'flow'` for `'digraph flow {\n a -> b\n}'`, `'g'` for `'graph g {\n a -- b\n}'`, `'s'` for `'strict digraph s {'`, `''` for `'digraph {\n a -> b\n}'`, `'after'` for `'// note\ndigraph after {'`, and `None` for `'step1 [label="import fs"];\nstep2 [label="read file"];'`.
- `test_find_blocks_reads_every_markdown_file_and_skips_fragments`: a skill whose `SKILL.md` holds the fragment above and `digraph top {}`, whose `references/deep.md` holds `digraph deep {}`, and whose `conventions.dot` holds `digraph style {}`. `[(b.source.as_posix(), b.name) for b in find_blocks(skill)] == [('SKILL.md', 'top'), ('references/deep.md', 'deep')]`.
- `test_output_names_never_repeat`: blocks named `when_to_use` in `a.md`, `when_to_use` in `b.md`, and `when_to_use` again in `b.md` give `['a-when_to_use.svg', 'b-when_to_use.svg', 'b-when_to_use-2.svg']`.
- `test_refuses_out_dir_inside_skill`: `main([str(skill), str(skill / 'diagrams')]) == 2`, and `skill / 'diagrams'` does not exist. `main([str(skill), str(skill)]) == 2` too.
- `test_missing_dot_exits_2`: with `shutil.which` monkeypatched to return `None`, `main([str(skill), str(out)]) == 2`, `out` does not exist, and stderr names graphviz.
- `test_missing_skill_md_exits_2`: a folder with no `SKILL.md` gives 2.

Run with `dot` (`@needs_dot`):
- `test_renders_each_block_as_svg`: exit 0. `out / 'SKILL-top.svg'` and `out / 'deep-deep.svg'` exist, and each holds `<svg`.
- `test_failed_block_exits_1_and_keeps_others`: one file holds `digraph good { a -> b }` and `digraph bad { a -> }`. Exit 1. `good`'s SVG exists, `bad`'s does not, and stderr names `bad`.
- `test_same_graph_name_in_two_files_writes_two_svgs`: `a.md` and `b.md` each hold `digraph when_to_use { x -> y }`. Exit 0, and both `a-when_to_use.svg` and `b-when_to_use.svg` exist.
- `test_anonymous_graph_renders_under_a_generated_name`: `SKILL.md` holds `// note` and then `digraph { a -> b }`. Exit 0, and exactly one SVG whose name contains `graph_1` exists.
- `test_combine_writes_one_svg_and_its_dot_source`: two blocks with `--combine`. Exit 0, and `<skill_name>_combined.svg` and `<skill_name>_combined.dot` are the only files in `out`.
- `test_renders_writing_skills_own_chart`: `main([str(Path(__file__).resolve().parents[1]), str(out)]) == 0`, the writing-skills folder itself. `flowcharts-when_flowchart.svg` exists, and no file name starts with `SKILL-`, because `SKILL.md`'s only block is the header-less anti-pattern.

- [x] **Step 2: Register the suite and run it to see it fail**

Add to `build/suites.toml`:

```toml
[[suite]]
name = 'writing-skills'
dir = 'skills/writing-skills/scripts'
with = ['pytest']
notes = ['render_graphs.py tests, stdlib only. The tests that render skip when graphviz dot is not on PATH.']
```

Run: `uv run python build/run_suites.py writing-skills`. Expected: FAIL, `No module named 'render_graphs'`.

- [x] **Step 3: Implement `render_graphs.py`**

The header is `#!/usr/bin/env python3`, then a PEP 723 block with `requires-python = '>=3.11'` and `dependencies = []`, as `skills/design-architecture/scripts/new_adr.py` has. The module docstring gives the usage and says that it needs `dot` on PATH and that it is a port of upstream superpowers' `render-graphs.js`. Functions:

- `class Block(NamedTuple)`: `source: Path` (relative to the skill folder), `name: str`, `text: str`.
- `dot_blocks(markdown: str) -> list[str]`: the text of each ` ```dot ` fence, in order.
- `graph_name(block: str) -> str | None`: read the first line that is not blank and not a `//` or `#` comment. If it matches `(strict\s+)?(di)?graph\b(\s+(\w+|"[^"]*"))?\s*\{`, return the name (quotes removed), or `''` when there is none. Otherwise return `None`.
- `find_blocks(skill_dir: Path) -> list[Block]`: every `*.md` under `skill_dir`, sorted by relative path. A block whose `graph_name` is `None` is skipped. An anonymous block is named `graph_<k>`, where k is its 1-based place among the blocks kept so far.
- `output_names(blocks: list[Block]) -> list[str]`: `<file stem>-<name>.svg`, with `-2`, `-3` and so on added before `.svg` when a name repeats.
- `combine(blocks: list[Block], skill_name: str) -> str`: one `digraph <skill_name>_combined` with `rankdir=TB; compound=true; newrank=true;` and each block's body in a `subgraph cluster_<i>` labelled with the block's name, dropping `rankdir` lines, as the JS does.
- `main(argv: list[str] | None = None) -> int`. Check in this order: the arguments, `<skill-dir>/SKILL.md`, an out-dir that equals the skill folder or sits inside it (print `refusing: <out-dir> is inside the skill folder; everything there ships with the skill`), then `shutil.which('dot')`, with the JS's install hint. Make the out-dir only after these checks. Render with `subprocess.run(['dot', '-Tsvg'], input=text, capture_output=True, text=True)`. Name each failure on stderr as `failed: <source>: <name>: <first stderr line>`, and go on to the next block. `--combine` writes `<skill_name>_combined.svg` and `.dot`, where `skill_name` is the folder name with `-` written as `_`.

End the file with `if __name__ == '__main__': sys.exit(main())`. Run `git rm skills/writing-skills/render-graphs.js`.

> Deviation: `SKILL.md`'s frontmatter gained `compatibility: Requires uv to run bundled scripts (dependencies are declared inline); Python 3.11+.`, because `build/check_frontmatter.py` fails a skill whose Markdown runs a bundled script with `uv run`. Task 7's `NOTICE` bullet names the line. Source: ledger ruling, Task 2.

- [x] **Step 4: Run the tests, with `dot` and without it (brief trap T6)**

Run: `uv run python build/run_suites.py writing-skills`. Expected: 12 passed (+12, a new suite).

Then hide `dot`, but keep uv. Run `command -v uv`, then:

```bash
mkdir -p /tmp/wsl105-nodot
ln -sf <the path command -v uv printed> /tmp/wsl105-nodot/uv
PATH=/tmp/wsl105-nodot:/usr/bin:/bin uv run python build/run_suites.py writing-skills
```

Expected: the six `needs_dot` tests skip and the other six pass. CI runs no suite, so record both summary lines in the task report.

- [x] **Step 5: Document the port in `flowcharts.md`**

Replace the paragraph that starts `**Visualizing for your human partner:**` and its `bash` block with:

````markdown
**Visualizing for your human partner:** run [scripts/render_graphs.py](../scripts/render_graphs.py) to render a skill's flowcharts to SVG. It reads every Markdown file in the skill, skips a `dot` block with no graph header, and exits non-zero when a block fails. It needs Graphviz's `dot` on PATH. Give it an output folder outside the skill, since everything in the skill folder ships with the skill. From writing-skills' directory:
```bash
uv run scripts/render_graphs.py ../some-skill /tmp/some-skill-diagrams           # Each diagram separately
uv run scripts/render_graphs.py ../some-skill /tmp/some-skill-diagrams --combine # All diagrams in one SVG
```
````

Leave line 29 (the `graphviz-conventions.dot` link). Task 5 changes it in the commit that moves its target.

- [x] **Step 6: Mutant step, checks and commit**

Run the mutant step on `render_graphs.py`. Run `git grep -n 'render-graphs' -- skills/`. Expected: only `render_graphs.py`'s docstring line, which names upstream's script. Run `uv run python build/check_links.py` and the commit gate. Commit: `feat(writing-skills): port render-graphs.js to scripts/render_graphs.py`.

### Task 3: Guard kit and its registered rules (no reps)

This task spends nothing. Its review gates the kit, the cases and the registered rules before Task 4 spends any money.

**Files:**
- Create: `specs/baseline/red-baseline-writing-skills-layout.md` (the record: kit, cases, rules, bars, predictions and the spend stop; Tasks 4 and 6 append to it)
- Create: `specs/baseline/red-baseline-writing-skills-layout/kit/` (the files below)
- Modify: `build/suites.toml` (suite `writing-skills-layout-kit`, dir the kit, `with = ['pytest']`)

**Interfaces:**
- Consumes: plan 103's kit (`specs/baseline/red-baseline-worktree-skills-fix/kit/`): `postprocess(raw: dict) -> dict` and its tests, its `run_reps.sh`, `probe.sh`, `kit_identity.py` and `check_scrub.py`. Plan 104's kit (`specs/baseline/red-baseline-mutant-screen-runs/kit/`): `common.sh`, `run_reps.sh`, `rep_tools.py` (`check-copy`, `summarize`), `privacy_sweep.py`, `isolation_probe.txt` (eight lines, with the identity and session questions), `probe.sh`, and the stream and path audits of `grade.py` (its V9 audit, `grade.py:180-196`). Plan 72's kit: `cases.py`'s `FRAME` and `CASES` W1–W3.
- Produces, for Tasks 4 and 6:
  - `build_prompts.py <ref> <arm> <out-dir>`: writes `W1.txt`–`W3.txt` and `T1.txt`–`T3.txt` from `skills/writing-skills/SKILL.md`'s body at `<ref>` (read with `git show`), and `MANIFEST.txt` with the ref, the arm, the body's sha256, each prompt's sha256 and the skill copy's file hashes in `rep_tools.py check-copy`'s form. Refuses an out-dir that exists.
  - `rep_tools.py place-copy <ref>`: puts `git archive <ref> skills/writing-skills` at `/private/tmp/wsl105-skill/writing-skills/`. Refuses when that folder is not empty.
  - `run_json_reps.sh <prompt> <out-dir> <first> <last> <model>`: plan 103's runner (no tools, `--output-format json`, `postprocess` on each rep).
  - `run_tool_reps.sh <prompt-dir> <case> <out-dir> <first> <last> <model>`: plan 104's runner, cut as Step 3 says.
  - `audit.py <rep-dir> ...`: for each tools rep, the stream audit (V9, record counts), the path audit, each Read of the case's moved file (marked partial when it had `offset` or `limit`), and the read-before-write result.
  - `sheets.py build <runs-root> <sheet-dir> <seed>` and `sheets.py unblind <grades.tsv> <key.json>`.

**Brief note.** The kit changes no skill text. Committed kits stay frozen, so copy files and never edit plan 72's, plan 103's or plan 104's kit in place (brief trap T4).

- [x] **Step 1: Check the sources**

Check that `specs/baseline/red-baseline-worktree-skills-fix/kit/postprocess.py` exists on this branch's `main` base. If it does not, stop and ask (Open for plan review, item 2). Run `claude --version`, and record it in the record's Kit section.

- [x] **Step 2: Write the failing self-tests**

`kit/test_wsl_kit.py`, on synthetic records and folders:
- Plan 103's `postprocess` tests, copied: void on `result_index` 1, void on an `origin` that is not null, and the drop of `origin` and `credential_expires_at`.
- `test_stream_audit_flags_peer_origin_at_any_depth`, `test_stream_audit_flags_cross_session_tool_in_init`, `test_stream_audit_voids_a_second_result_record`.
- `test_read_before_write_passes_read_then_edit`, `test_read_before_write_fails_edit_then_read`, `test_read_before_write_passes_read_without_write`, `test_read_of_a_longer_name_does_not_count` (a Read of `old-persuasion-principles.md` or `persuasion-principles.md.bak` is not a read of `persuasion-principles.md`), `test_partial_read_is_marked_partial`.
- `test_sheets_hide_the_arm`: two T2 rep folders whose answers differ only in the skill path (`…/writing-skills/persuasion-principles.md` against `…/writing-skills/references/persuasion-principles.md`) give byte-identical sheets.
- `test_build_prompts_refuses_existing_out_dir`, `test_place_copy_refuses_non_empty_root`, `test_check_copy_refuses_changed_copy`.
- Plan 104's tests of the parts copied into `common.sh` and `run_tool_reps.sh` (folder layout, `env -i`, the refusal of a non-empty root), adapted to the new names.

Register the suite. Run: `uv run python build/run_suites.py writing-skills-layout-kit`. Expected: FAIL on the missing modules.

- [x] **Step 3: Build the kit**

- **No-tools mode (W1–W3).** Copy plan 103's runner as `run_json_reps.sh`, its `postprocess.py`, `kit_identity.py`, `check_scrub.py` and `probe.sh` (as `probe_json.sh`). Change only the scratch folder (`plan105/json/`) and the rep folder prefix (`plan105-rep-`).
- **Tools mode (T1–T3).** Copy plan 104's `common.sh`, `run_reps.sh` (as `run_tool_reps.sh`), `rep_tools.py`, `privacy_sweep.py` and `probe.sh` (as `probe_tools.sh`). Keep the rep folder layout, `env -i`, the own `HOME` with its Keychains link, the `--settings` deny list and `syncClaudeAiSkills` false, `--disable-slash-commands`, the stream-json output, `check-copy` before and after each rep, `summarize` and `park`. Cut the `.sdd` workspace, `setup.sh`, the `@BASE@` token, the role-to-model map and the mutant-run audits. Set `--tools` and `--allowedTools` to `Read,Glob,Grep,Edit,Write`, the cap to $1.50 for both models, and the roots to `/private/tmp/wsl105` and `/private/tmp/wsl105-skill`. The scratch folder is `~/.cache/agent-skills/scratch/plan105/tools/`. Each rep's `repo/` is the case's fixture, committed once as the rep's BASE, so `summarize` writes `final.diff` against it, with new files included.
- **Probe.** Copy plan 104's eight-line `isolation_probe.txt`, used by both probe scripts.
- **`audit.py`** holds plan 104's stream and path audits. The allowed roots are the rep folder and the skill copy, in their `/tmp` and `/private/tmp` forms. It adds the read check of the reading rule (Step 4).
- **`sheets.py`** writes one sheet per scored rep, named by a 6-hex id drawn from `<seed>`. A sheet holds the case, its PASS and FAIL columns and the rep's answer: for a W rep, the result text; for a T rep, the final message and `final.diff`. Every path that ends in a writing-skills file name becomes `<skill>/<basename>`. The key (sheet id to case, arm, model and rep) goes to `key.json` beside the sheet folder, in scratch, and is read only after every sheet is graded.

Run the suite. Expected: all pass.

> Deviation: the copied kit changed in six places, logged as Deviations 1 to 4, 6 and 7 in `specs/baseline/red-baseline-writing-skills-layout.md`: a three-part scratch path, a model argument for the probe, a skill-copy path in the T frame, the Grep and Glob path audit (brief trap H3), the order of the sheets' file changes, and a `pilot` arm in `build_prompts.py`.

- [x] **Step 4: Write `cases.py` and the fixtures**

`kit/cases.py`:
- `FRAME_W` and `CASES_W` (W1, W2, W3): plan 72's `FRAME` and `CASES`, byte for byte.
- `FRAME_T`: plan 72's frame with three changes. The skill block opens with `Base directory for this skill: /private/tmp/wsl105-skill/writing-skills`, as Claude Code loads a skill. It says that the session's tools are Read, Glob, Grep, Edit and Write and that the working directory is the partner's project. It ends: "It is your turn. Do the task with your tools, then write the message you would send to your partner."
- `CASES_T`, `TARGET`, `MOVED` and `MARKER`, as in the table. Each case states that the needed earlier steps are done, so the Iron Law does not hold the agent. No domain repeats the skill's own examples or plan 72's cases.

| Case | Moved file (hops in old → new) | Conversation | Target | Marker (use) |
|---|---|---|---|---|
| T1 | `testing-skills-with-subagents.md` (1 → 1) | Partner: "I want a new skill, `lockfile-refresh`, for agents that change dependencies. They bump a version in `pyproject.toml` and commit without running `uv lock`, so `uv.lock` goes stale. We'll build it with writing-skills, RED first." Then: "Write the pressure scenarios for the RED baseline, three of them, into `specs/lockfile-refresh-scenarios.md`. Don't run them yet." | `specs/lockfile-refresh-scenarios.md` | at least two scenarios end by making the tested agent choose among lettered options (A, B, C …) |
| T2 | `persuasion-principles.md` (2 → 1) | Partner: "Our `secrets-scan-gate` skill says to run `gitleaks protect --staged` before every commit. Agents skip it under pressure." `[you, tools]`: the baseline ran three pressure scenarios, 5 reps each, with the skill loaded. In 8 of 15 runs the agent committed without the scan. The rationalizations are in `specs/secrets-scan-gate-baseline.md`: "the diff only touches docs", "CI runs a scanner anyway", "I'll scan before I push". Then: "Rewrite the rule paragraph in `skills/secrets-scan-gate/SKILL.md` so it holds. Then tell me which persuasion principles your wording uses, and which ones you left out on purpose." | `skills/secrets-scan-gate/SKILL.md` | the final message names at least two of Authority, Commitment and Social Proof as used, and names Liking or Reciprocity as left out |
| T3 | `graphviz-conventions.dot` (2 → 1) | Partner: "Agents using our `http-retry-policy` skill keep retrying calls that should fail fast. I want a small decision flowchart for 'retry or fail fast' in `skills/http-retry-policy/SKILL.md`." `[you, tools]`: the baseline ran three scenarios, 5 reps each. In 10 of 15 runs the agent retried a POST that had no idempotency key. The reasons are in `specs/http-retry-policy-baseline.md`. Then: "Add the flowchart. It must show the health check `curl -sf https://status.example.invalid/health` that the agent runs first, and the warning 'Never retry a POST without an idempotency key'." | `skills/http-retry-policy/SKILL.md` | the added `dot` block draws the `curl` command as a `shape=plaintext` node, or the warning as a `shape=octagon` node |

`kit/fixtures/<case>/repo/` holds each case's project. T1: `pyproject.toml`, `uv.lock` and an empty `specs/`. T2: `skills/secrets-scan-gate/SKILL.md` (a short skill whose rule paragraph is soft) and `specs/secrets-scan-gate-baseline.md`. T3: `skills/http-retry-policy/SKILL.md` (a short skill with no chart) and `specs/http-retry-policy-baseline.md`.

- [x] **Step 5: Write and commit the record's rules before any rep runs**

Create `specs/baseline/red-baseline-writing-skills-layout.md` with these sections:
- **Kit:** the paths, the sources and the Claude Code version from Step 1. The arms: `old` is `SKILL.md`'s body and skill folder at the last commit before Task 5, and `new` is the same at Task 5's commit. Task 6 fills in both shas.
- **Cases:** W1–W3 as plan 72 states them (`specs/baseline/red-baseline-writing-skills-split.md:20-24`), and T1–T3 as Step 4 states them.
- **Reading rule, W cases:** plan 72's paragraph "Reading rule for every `t3` rep" (`specs/baseline/red-baseline-writing-skills-split.md:11-17`), verbatim, with "every `t3` rep" written as "every rep of either arm".
- **Reading rule, T cases:** a rep passes when both parts hold. *Read:* the tool log has a Read whose `file_path` ends in `/<moved file>`, before the first Edit or Write of the case's target. A rep with no Edit or Write of the target passes this part with any such Read. Glob, Grep and reads of other files do not count. A Read with `offset` or `limit` counts and is marked partial. *Use:* the blind grader marks the case's marker as present in the rep's answer.
- **VOID:** a W rep that `postprocess` voids (`result_index` above 0, or an `origin` that is not null). A T rep with a V9 finding, a path outside the allowed roots, a changed skill copy, a stream line that is not JSON, or the subtype `error_max_budget_usd`. Any rep with a kit error. A void rep does not count, and the next rep number replaces it. A third void in one arm stops the run, and the owner hears of it.
- **Blind grading:** sheets name the sheet id and the case, never the arm. Before grading, diff one `new` sheet against an `old` sheet of the same case: only the answer may differ. A read can still hint at the arm. For example, a W2 rep of the `new` arm may name `graphviz-conventions.dot`. The record states this limit, and the W verdicts stay mechanical.
- **Bars:** per case and model, `new` passes ≥ `old` passes − 1. The W cases also need `new` ≥ 4/5. The guard passes when every case and model meets its bars. On a failure, stop, record, and ask the owner. Change no pointer wording.
- **Predictions (descriptive):** W: `new` ≈ `old`. T1: `new` ≈ `old`, one hop in both. T2 and T3: `new` ≥ `old`, one hop instead of two. Report the read and use counts apart, the partial reads, and, for T2 and T3 `old` reps, whether the read went through `bulletproofing.md` or `flowcharts.md` first.
- **Spend stop:** Global Constraints' cap, projection and pair check, with a running-total table that starts at $0.00.

> Deviation: the registered rules gained two VOID reasons (a second result record, a run error) and the rule that an errored Read does not count (Deviations 5 and 8 in the record). Source: Task 3 review.

- [x] **Step 6: Mutant step and commit**

Run the mutant step on `audit.py`, `sheets.py` and `postprocess.py`. Run the commit gate. Commit: `test(baseline): add the writing-skills layout guard kit and its rules`. This commit comes before any probe or rep, so it registers the rules.

> Deviation: three commits (`4465c3f`, `d294e8e`, `a93a999`) carry the kit and its rules, where the plan has one. All three land before any probe or rep. Review fix rounds then added further commits through `208800f`. Source: ledger ruling, Task 3.

### Task 4: Probes, pilot and spend projection (not scored)

**Files:**
- Modify: `specs/baseline/red-baseline-writing-skills-layout.md` (the Kit and Spend stop sections)

**Interfaces:**
- Consumes: Task 3's kit CLIs and record.
- Produces: the projection that Task 6's first scored pair needs.

- [x] **Step 1: Probes**

Run `probe_json.sh` and `probe_tools.sh` on each model (four probes), and add each cost to the running total. Expected: NO on probe lines 1–6 and 8. Line 7 (the user's identity) may read YES: the open watch item "Account identity reaches the isolated micro-test runs" tracks it. Any other YES stops the run, and the owner hears of it.

- [x] **Step 2: Pilot**

Run `rep_tools.py place-copy HEAD`, then build prompts with `build_prompts.py HEAD pilot <scratch>/prompts-pilot`. Run one rep each of T1, T2 and T3 on `claude-sonnet-5-5`, and one T1 rep on `claude-opus-5-5`, so every fixture runs once before any scored rep. Expected for each: `audit.py` shows no path outside the allowed roots and V9 none, and the T1 reps show a Read of `testing-skills-with-subagents.md`. Otherwise stop and ask. Empty the skill copy after the pilot.

- [x] **Step 3: Project the spend**

Projected total = spend so far + 60 × $0.05 for the W reps (plan 72's isolated reps cost about $0.03 each) + 30 × the mean Sonnet T pilot cost + 30 × the Opus T pilot cost. If the projection passes $35, stop and ask before any scored rep.

- [x] **Step 4: Record and commit**

Add the probe answers, the pilot facts, the projection and the running total to the record's Kit and Spend stop sections. Run `privacy_sweep.py` on anything committed. Run the commit gate. Commit: `test(baseline): record the layout kit's probes and pilot`.

### Task 5: Move the support files into `references/` (item 8, Q2)

**Files:**
- Rename: `skills/writing-skills/testing-skills-with-subagents.md` → `skills/writing-skills/references/testing-skills-with-subagents.md`
- Rename: `skills/writing-skills/persuasion-principles.md` → `skills/writing-skills/references/persuasion-principles.md`
- Rename: `skills/writing-skills/graphviz-conventions.dot` → `skills/writing-skills/references/graphviz-conventions.dot`
- Modify: `skills/writing-skills/SKILL.md` (§ Flowchart Usage, § Bulletproofing Skills Against Rationalization, the Testing methodology line)
- Modify: `skills/writing-skills/references/bulletproofing.md:10`, `references/flowcharts.md:29`, and the `persuasion-principles.md` mention in `references/testing-skills-with-subagents.md`

**Interfaces:**
- Consumes: Task 1's text and Task 2's `flowcharts.md`.
- Produces: the `new` arm for Task 6. The `old` arm is the commit before this task's commit.

**Brief note (trap T1).** Quote the Q2 ruling: "Ruling: move and link (item 8b). `testing-skills-with-subagents.md`, `persuasion-principles.md` and `graphviz-conventions.dot` move into `references/`, and `SKILL.md` links each one directly." The spec gives this change its test as "A guard run on plan 72's `t3` cases, old layout against new", and D1 adds the tools-on cases. Task 6 runs that guard, so this task ships no test of its own.

- [x] **Step 1: Record the old arm**

Record `git rev-parse HEAD` in the ledger as OLD.

- [x] **Step 2: Move the files and fix their links**

Run `git mv` for the three files. Then:
- `references/bulletproofing.md`: replace `[persuasion-principles.md](../persuasion-principles.md)` with `[persuasion-principles.md](persuasion-principles.md)`.
- `references/flowcharts.md`: replace `See [graphviz-conventions.dot](../graphviz-conventions.dot) in the skill's directory for graphviz style rules.` with `See [graphviz-conventions.dot](graphviz-conventions.dot) for graphviz style rules.`
- `references/testing-skills-with-subagents.md`: replace `See persuasion-principles.md (in writing-skills directory) for research` with `See [persuasion-principles.md](persuasion-principles.md) for research`.

- [x] **Step 3: Link each moved file from `SKILL.md`**

In § Flowchart Usage, replace `its place, and the graphviz style rules and render tool.` with:

```markdown
its place, and the render tool. Before you draw it, read
[references/graphviz-conventions.dot](references/graphviz-conventions.dot):
the node shapes, edge labels and naming rules.
```

In § Bulletproofing Skills Against Rationalization, replace `rationalization table, the red flags list and the description's violation` and the line `symptoms.` after it with:

```markdown
rationalization table, the red flags list and the description's violation
symptoms. Before you word the counters, read
[references/persuasion-principles.md](references/persuasion-principles.md):
which persuasion principles fit each skill type.
```

Replace `See [testing-skills-with-subagents.md](testing-skills-with-subagents.md)` with `See [references/testing-skills-with-subagents.md](references/testing-skills-with-subagents.md)`.

- [x] **Step 4: Check the move**

Run:
- `uv run python build/check_links.py`. Expected: passes.
- `git grep -n -e '\.\./persuasion-principles' -e '\.\./graphviz-conventions' -e '\.\./testing-skills' -e 'in writing-skills directory' -- skills/`. Expected: no output (Review Focus 5).
- `ls skills/writing-skills`. Expected: `LICENSE`, `LICENSE-superpowers`, `SKILL.md`, `references` and `scripts` only.
- The body measure. Expected: 19,063 (Task 1's 18,758, +123 for Flowchart Usage, +160 for Bulletproofing, +22 for the testing link), which is at most 19,240.
- `uv run --with pyyaml python build/check_conformance.py`. Expected: no finding for writing-skills. The orphan check passes, because `SKILL.md` names each moved file.

- [x] **Step 5: Commit**

Commit the move and every link change together, so `check_links.py` passes at each commit (brief trap T5). Run the commit gate. Commit: `refactor(writing-skills): move the support files into references/`. Record `git rev-parse HEAD` in the ledger as NEW.

### Task 6: Guard run, old layout against new

**Files:**
- Modify: `specs/baseline/red-baseline-writing-skills-layout.md` (the shas, the results, the verdict and the spend)
- Create: `specs/baseline/red-baseline-writing-skills-layout/runs/<case>/<arm>/<model>/` (scrubbed rep output) and `.../prompts-<arm>/` (prompt files and `MANIFEST.txt`)

**Interfaces:**
- Consumes: Task 3's kit CLIs, Task 4's projection, and OLD and NEW from Task 5's ledger lines.

- [x] **Step 1: Build and check the arms**

Run `build_prompts.py <OLD> old <kit>/../prompts-old` and `build_prompts.py <NEW> new <kit>/../prompts-new`. Then run `git diff <OLD> <NEW> -- skills/writing-skills/SKILL.md`. Expected: three hunks only, Task 5 Step 3's. If `claude --version` differs from the version that the record's Kit section names, run the four probes again first.

- [x] **Step 2: Run the scored batches**

For each case in the order W1, W2, W3, T1, T2, T3, then for each model (`claude-sonnet-5-5`, then `claude-opus-5-5`): run reps 1–5 of `old`, then reps 1–5 of `new`. Those 10 reps are one pair. Run the pair check before each pair, so a stop never leaves an `old` arm with no `new` arm. Before each tools batch, place the arm's skill copy with `rep_tools.py place-copy <OLD or NEW>`. After the batch, empty the copy. Replace void reps as the record's VOID rule says. Add each batch's cost to the running total in the record.

- [x] **Step 3: Grade blind, then unblind**

Run `audit.py` on every T rep, and record its read results and void findings. Run `sheets.py build`, and do the diff check that the record's Blind grading section names. Grade every sheet by hand, against the case's PASS and FAIL columns, into `grades.tsv` in scratch. Then run `sheets.py unblind`.

> Deviation: six grader agents, not a person, graded the sheets (Deviation 9 in the record). The owner ratified this at the completion gate, 2026-11-23.

- [x] **Step 4: Record the results and the verdict**

In the record, add a Results section with one table per case: the verdict and deciding line for each rep, and its spend so far, as plan 72's record does. Add a summary table of old and new pass counts per case and model, against the bars. State the verdict: PASS, or FAIL with the failing cells. Add the descriptive counts that the Predictions section names. If the verdict is FAIL, stop here and ask the owner. Change no wording.

- [x] **Step 5: Commit**

Run `check_scrub.py` and `privacy_sweep.py` on the runs folder. Run the commit gate. Commit: `test(baseline): run the writing-skills layout guard`.

### Task 7: `NOTICE` and the files verify

**Files:**
- Modify: `NOTICE` (the plan 72 divergence sentence; a new last bullet of the superpowers change list, before the list of skill folders)
- Modify, through `/cc-guide` only: `build/cc_guide/baseline.json`, and a fix that it lists in `skills/writing-skills/SKILL.md` or a covered file

- [x] **Step 1: Update the plan 72 sentence**

In the plan 72 bullet, replace:

```text
    One divergence: upstream also moved the supporting files into
    references/; here they stay beside SKILL.md, and the moved text links
    them as ../<file>.
```

with:

```text
    One divergence: upstream also moved the supporting files into
    references/; here they stayed beside SKILL.md, linked as ../<file>,
    until plan 105 moved them.
```

- [x] **Step 2: Add the plan 105 bullet**

Fetch, and compare `NOTICE` on `origin/main` with this branch. Plans 103 and 106 may have added bullets to the superpowers change list. Keep every line they added. Add this bullet as the last one in the list, after theirs, wrapped like its neighbors, with the date of this commit:

```text
  - Plan 105 (<YYYY-MM-DD>) changed writing-skills, from
    specs/completed/writing-skills-improvements.md. testing-skills-with-subagents.md,
    persuasion-principles.md and graphviz-conventions.dot moved into
    references/, as upstream v7.0.1's map has them, and SKILL.md now links
    each one at the step that uses it. render-graphs.js is gone.
    scripts/render_graphs.py takes its place. It is a new work based on
    upstream's script (MIT), ported to Python: it reads every Markdown file
    in a skill, skips a block with no graph header, exits non-zero when a
    block fails, and writes outside the skill. Upstream's
    examples/CLAUDE_MD_TESTING.md, a design for a test campaign that never
    ran, is deleted, and so is the dated session report at the end of
    testing-skills-with-subagents.md. The other changes are local, and no
    upstream text was taken. persuasion-principles.md describes the Meincke
    et al. study as it ran and gains bulletproofing.md's scope line.
    testing-skills-with-subagents.md exempts pure reference skills from
    pressure tests only. SKILL.md lists four skill types and asks for
    examples in the language of the skill's target stack. discovery.md gives
    the 2026-11-22 Codex description cut. Three long files gain contents
    lists. The guard run's fixtures are this repository's own
    (specs/baseline/red-baseline-writing-skills-layout.md).
```

- [x] **Step 3: Check and commit**

Run `uv run python build/check_provenance.py` and the commit gate. Commit: `docs(notice): record plan 105's writing-skills changes`.

> Deviation: a second `NOTICE` commit, `fd00fb2`, adds a sentence that names the committed `prompts-old/` and `prompts-new/` folders. Owner ruling at the completion gate, 2026-11-23.

- [x] **Step 4: Owner gate: the files verify**

Stop and ask the owner to type `/cc-guide files skills/writing-skills/SKILL.md` in this execution session. The move changed the files that `SKILL.md`'s citation covers (spec Constraints, "Covered files"). `/cc-guide` commits nothing, so wait for the owner's review of its diff.

- [x] **Step 5: Commit the verify**

Run `uv run python build/cc_guide/cli.py lint` and the commit gate. Commit what `/cc-guide` changed: `chore(cc-guide): re-verify writing-skills after the layout move`. If settle held the file, record the hold and its reason in the ledger for the completion gate. Do not cite a held file.

> Deviation: no commit. The `/cc-guide files` run found no fact to fix. Both contradictions are the standing `description-when-only` deviation, and the owner ruled no action on the 5 not-covered rows (gate, 2026-11-23). `baseline cite` stamped the file at 2.1.326 and changed no file.

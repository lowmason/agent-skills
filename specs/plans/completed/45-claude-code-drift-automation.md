# Verifier Recall (cc-guide verifier contract) Implementation Plan

**Status: COMPLETE (2026-10-15)** — executed via subagent-driven-development; gate FAIL (record `specs/completed/verifier-recall-verification-2026-10-14.md`), Task 1 reverted by the owner; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking. Tasks 1 and 2 go to implementer subagents. Tasks 3–6 are run by the controller itself: they hand steps to the owner, read results by hand and write the record, so no implementer subagent takes them.

> **Where this runs.** This plan lands on `main` first, by its own PR (D5). Then create the worktree from the main checkout (Global Constraints, "Worktree") and execute there: `/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall`, on branch `feat/verifier-recall`. Start the execution session with that worktree as its working directory: subagent-driven-development's `sdd-workspace` and `review-package` take the repo root and `HEAD` from the shell's working directory. Below, **`W`** names that worktree, **`K`** the evidence kit `/Users/lowell/.cache/agent-skills/scratch/plan45` (outside every checkout), and **`R`** the rep root `/private/tmp/q7r`. Every command spells its paths out, since a worktree-isolated session refuses compound shell (`&&`, `$(...)`).

**Goal:** Make the `cc-guide-verifier` agent rate a claim that is true as far as it goes, but that the docs passage it quotes qualifies, as PARTIAL rather than CONFIRMED. Make it rate a files statement by the same failure test, against the guide's examples as well as its prose, and give a files row one line number. Then show, with isolated and pre-registered reps, that an audit of the pre-fix guide (`5bd78a7`) against the 2.1.296 snapshot now reports `deniedModels`: the done-when of the deferred item "The audit verifier's omission recall was 3 of 7 known positives".

**Architecture:**
- **The contract** (Task 1): `.claude/agents/cc-guide-verifier.md` gains a short recipe that defines CONFIRMED, PARTIAL, STALE and WRONG by a failure test over the quoted line's passage, routes a qualifying omission to its claim's PARTIAL row, and re-rates any A row its own B rows change. Its files part gains the same failure test, the three files verdicts defined by it, and the one-line rule. `.claude/skills/cc-guide/references/formats.md` gains the one-line rule. `build/cc_guide/test_skill_files.py` pins each new slot. The spec's R8.1, R8.5, R8.7 and R12.4 are amended to match. The seven report templates `settle.FORMATS` pins are untouched, and so are settle and packets.
- **The evidence kit** (Task 2): a small Python kit in `K`, outside the repo and with its own tests. `build.py` makes one directory per rep, holding the arm's verifier and a copy of its packet less the original report. `run.py` is what the owner runs from a plain terminal, one `claude -p` session per rep. `grade.py` audits each rep's transcripts against the VOID rules and scores its report with settle, in memory, against the original packet.
- **The runs** (Tasks 3–5): a fence probe and a pilot; the cheap arms on the files and verify packets behind defects (b)–(e); then the gate, 5 + 5 audit reps in two waves, each pair's arms in a random order.
- **The record** (Task 6): `specs/completed/verifier-recall-verification-<date>.md`, which holds counts and claim labels only. Raw replies stay in `K`.

**Tech Stack:** Claude Code agent Markdown; Python 3.13 through `uv run`, stdlib only in the kit; pytest; Claude Code 2.1.296 for the reps, run by path from a copy of `/Users/lowell/.local/share/claude/versions/2.1.296` held at `/Users/lowell/.cache/agent-skills/scratch/plan45-bin/2.1.296`, since the PATH's `claude` moved to 2.1.299 on 2026-10-13 and the updater prunes old versions.

**Spec:** `specs/claude-code-drift-automation-spec.md` (DESIGN APPROVED 2026-10-03; Stages 1–3 shipped as plans 38, 43 and 44). No design spec exists for this item. The requirements are the deferred item at `specs/deferred_items.md:3181` on `main`, and its done-when is this plan's gate. Task 1 amends the spec's R8.1, R8.5, R8.7 and R12.4, as plans 43 and 44 amended it. The base is `main` at `2e9ee0f`: `938993c` plus lowmason/agent-skills#45, the files pass, which restamped the verifier and fixed (e)'s source lines. This plan's own landing goes on top. History is read from `3c10cb4`, where the item was filed.

## Global Constraints

Every task's requirements implicitly include this section.

- **Scope.** In scope:
  - (a) the four audit omissions (P7, P8, P10, P11 in the Planning record's key);
  - (b) the files-mode not-covered row on a statement the guide's example backs (`hooks/README.md`);
  - (c) the files row's line range (`agents/test-runner.md`);
  - (d) the verify-mode calibration miss (the rules group's L252 trigger, rated CONFIRMED);
  - (e) the files-mode twin of (d): `rules/clean-code-python.md`'s load trigger, which leaves out cases the guide gives, rated `consistent` (DF16).

  All five share one contract edit and one set of tests (DF1).

  Not in scope:
  - any guide edit;
  - any change to `settle.py`, `packets.py` or `SKILL.md`;
  - CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL's absence from the guide (P14; an owner's-call item already listed);
  - verify-mode `doc:line` ranges (DF14);
  - one files row per checkable statement on a source line (DF17);
  - the source lines behind (e), which lowmason/agent-skills#45 fixed on `main` after its pass had restamped them.
- **Order.** Task 1 (the contract and the spec amendments), then Task 2 (the kit), then Task 3 (the freeze, the owner's spend gate, the probe and the pilot), Task 4 (the cheap arms and their checkpoint), Task 5 (the gate) and Task 6 (the record and completion). No live verifier run happens before Task 3's spend gate.
- **Worktree.**
  - Before creating it, run `git -C /Users/lowell/Projects/agent-skills fetch --prune`, then `git -C /Users/lowell/Projects/agent-skills log --oneline -3 origin/main`, and confirm that `origin/main` holds this plan.
  - Create it with `git -C /Users/lowell/Projects/agent-skills worktree add .claude/worktrees/plan-45-verifier-recall -b feat/verifier-recall origin/main`.
  - Commit only from `W`, as `git -C <W> commit …`. Before every commit, run `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall branch --show-current` and confirm it prints `feat/verifier-recall`.
  - Every commit runs `build/run_commit_lints.sh` through the repo's hook. A refused commit is a finding: fix the cause, never pass `--no-verify`.
  - SDD scratch lives under `W`'s gitignored `.sdd/45-claude-code-drift-automation/` and is never committed. Deviations go in its ledger and reach this plan as `> Deviation:` notes only at the completion markup.
  - Each commit ends with the executing session's own Co-Authored-By trailer, and subagent-authored commits keep it too. The commit blocks below show the planning session's (`Claude Opus 5.5`); an execution session on another model writes its own instead, and that needs no deviation note. After each subagent commit, check `git -C <W> log -1 --format=%B` and amend the trailer if the implementer wrote its own.
- **Baseline and counts.** Before Task 1, record in the SDD ledger the count from `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall/build/cc_guide --python 3.13 --with pytest python -m pytest -q`. Task 1 adds **+12 tests** there, and the build directory, which collects that suite, rises by the same +12. Also record the output of `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall --python 3.13 python build/cc_guide/cli.py lint` (its `STALE` lines go to stderr; keep both streams). Task 1 changes none of those lines. The kit's 43 tests live outside the repo and count toward neither.
- **Test-first.** Each task writes its tests first, runs them, and reconciles the run with the step's prediction before writing code. The predictions were observed while this plan was written: Task 1 by replaying its edits on detached worktrees of `938993c` and of `2e9ee0f`, where its counts were the same, and Task 2 by building the kit in a scratch directory. A test that passes at its RED step is a plan defect: fix the assertion so it fails for the stated reason, and report the deviation.
- **Formats stay pinned.** The seven strings of `settle.FORMATS` (`build/cc_guide/settle.py:68-76`) stay byte-identical in the verifier and in `formats.md` (`test_skill_files.py:54-57`).
  - Exactly one line of the verifier contains `TODO(owner)`, today's line 23 (`:45-51`).
  - The frontmatter keeps `tools: Read, Grep, Glob`, `model: sonnet` and `omitClaudeMd: true` (`:40`), with the citation on its last line (`:28-33`).
  - New prose never contains the bare word `cc-guide` (`check_conformance.py`'s dmi-handoff check), and no line begins `# cc-guide:`.
- **Never commit docs text.** Packets, reports, sheets and quotes stay in the cache and in `K` (`.claude/skills/cc-guide/SKILL.md:24`). The record and this plan cite docs and reports by file and line, and score by claim label. No fixture built from a packet is committed: the kit's tests are hand-written.
- **Channel 5: no rep starts inside this repo's context.** The owner launches every rep from a plain terminal, and `run.py` refuses to run in a Claude Code shell. Each rep's working directory is its own directory under `R`, which is no git repository and holds only the arm's agent file and a packet copy.
- **Channel 3: nothing a rep can read may contain the answer.**
  - A rep's packet copy leaves out `report.md` and `settled.json`.
  - The docs snapshot is the only other directory it can read (`--add-dir`).
  - Reads outside both are fenced (`permissions.blockReadsOutsideWorkingDirectories`), and voided when they return (V2), a relative path or a symlink that leads out included.
  - The changed arm's added text passes Task 1's term gate.
  - Sheets name no arm, and each pair's arms run in a random order (DF15).
- **Production fidelity.** User settings load, as they did for every production run: auto mode, the Opus advisor available, Sonnet 5.5 at `xhigh`, and the retention period (DF3). The main session runs Sonnet and dispatches with SKILL.md step 1's prompt verbatim. Claude Code is 2.1.296: `run.py` runs the held copy `/Users/lowell/.cache/agent-skills/scratch/plan45-bin/2.1.296` (`common.CLAUDE`) and checks its version. `~/.claude/settings.json` is hashed at the freeze. Its hash and the docs snapshot's `shasum -a 256` listing are recorded in `K/changes.log` before each hand-over to the owner and when each batch is done, the probe, the pilot, both gate waves and every spare batch included; a change in either stops the run until the owner rules.
- **Spend.** No live run before the owner approves the spend at Task 3, which writes the approved ceiling to `K/ceiling.txt`. Per-rep caps are in `K/common.py`. `run.py` starts a rep only when its full cap still fits under the ceiling, counting every earlier rep at its cost, or at its cap when it left no result; the first rep that does not fit, and every rep after it in the batch, is printed as held. A held rep is the owner's call: ask before raising the ceiling.
- **Codex seats.** Before any Codex seat, ask the owner for the model; `~/.codex/config.toml` has read `gpt-6.1-sol`. Never edit that file.
- **Nothing outward-facing during execution.** No push, PR, issue or post. Integration is decided at finishing-a-development-branch.
- **Leave alone:**
  - the spec's status line;
  - the guide;
  - `build/cc_guide/baseline.json` and `conformance.toml`;
  - every citing file's stamp, `.claude/agents/cc-guide-verifier.md`'s included: no `baseline cite` runs in this plan. lowmason/agent-skills#45 restamped the verifier to `@2.1.296.1`, so on `2e9ee0f` it is not STALE, and `cli.py lint` prints 6 `STALE` lines;
  - every packet under `~/.cache/agent-skills/cc-guide/packets/`: never written, never settled by `cli.py settle`;
  - `~/.codex/config.toml`.
- **Anchor on text, not line numbers.** Line numbers are as of `2e9ee0f`; lowmason/agent-skills#45 moved none that this plan cites outside `specs/deferred_items.md`, whose citations are re-anchored. Guide lines in the key are the audit packet's own numbering (= `5bd78a7`), which `3c10cb4` shifted by +1 from line 411 on. File lines in the files packets' key and ground truth are their cited copy's numbering, which may differ from `main`'s (`hooks/README.md`'s second `Bash` matcher is at :131 there). Score rows by claim.
- **Python style** (`CLAUDE.md`, `rules/clean-code-python.md`): single quotes, `'''` docstrings, 4-space indent, Python 3.13, lines within about 120 columns.

## Decisions

- **D1** (owner, brief, 2026-10-13): the verifier-recall item is plan 45. `entry_check.py` printed `next free: 45`, with no collisions. Applied in: the plan's id and file name.
- **D2** (owner, brief, 2026-10-13): a read-only Codex review of this draft comes before the owner's plan review. Its findings are fixed first, and the Codex model is asked per seat. Applied in: Planning record ("Independent review").
- **D3** (owner, plan review, 2026-10-14): the spend ceiling is $100. Applied in: Global Constraints ("Spend"), Task 3 Step 5, which still stops once to confirm it before the first live run.
- **D4** (owner, plan review, 2026-10-14): no second Codex seat on the fix wave's wording; the cheap arms and the gate test it. Applied in: Planning record ("Independent review").
- **D5** (owner, plan review, 2026-10-14): this plan lands on `main` by its own PR. Applied in: the header ("Where this runs").

---

## Planning record

### Diagnosis: every audit miss was read, then rated CONFIRMED

The original runs' subagent transcripts survive, and they settle the mechanism.
- The audit verifier read `model-config.md` whole, in two chunks (lines 1–509 and 510–1026), and its other pages in full or in ranges. Each of the four missed positives' qualifying lines came back in a Read result. The verifier quoted lines near them, rated the claims CONFIRMED, and never connected the two:
  - P11: `deniedModels` at `model-config.md:330`, `:363` and `:377`, in the same Read as the quoted `:234` and `:307`;
  - P7: the session-only `max` at `:622`, two lines from the quoted `:620`;
  - P8: the top-level `effortLevel` at `:613`, between the quoted `:609` and `:620`;
  - P10: the alias table at `:48-49`, six lines below the quoted `:42`, with the deprecation on a page it also read.
- The rules verify (d) is the same failure. The line it quoted, and its own B rows, contradict its CONFIRMED.
- The files run (e) is the same failure in files mode. Its row on `rules/clean-code-python.md:7` states in its own words the cases the line leaves out, then rates the line `consistent` (`packets/20261013T205255-files/rules__clean-code-python.md/report.md:3`). Its line-9 row does the same. Nothing in the files contract says a statement that leaves out a case the guide gives fails.
- The same pass's README run rated only one of the two claims on `README.md:163` and left the trigger clause unrated (`README.md/report.md:21`). That is a coverage rule, not a verdict definition (DF17).
- Settle held neither file, so the pass ran `baseline cite` on both and cleared their STALE flags while they still carry the old trigger. A files-mode miss costs more than a hold, because the restamp hides it until the guide section changes again.
- Run (b) is a judging rule. The verifier wrote that the guide's example quotes the variable, and still rated the statement not covered, because no prose requires quoting.
- Run (c) is a grammar rule.
- The contract names CONFIRMED, STALE, WRONG and PARTIAL (`.claude/agents/cc-guide-verifier.md:49`) but defines none of them. The same report rated other true-but-incomplete claims PARTIAL, so the behaviour is inconsistent rather than absent.

The fix is therefore a judging definition, not a reading recipe. In writing-skills' terms it is a shape failure, so its form is a positive recipe, not a prohibition.

Run conditions the agent file does not pin: every production run had effort `xhigh` and the Opus advisor available, both from user settings. The audit verifier called the advisor once, about $1.12 of its $2.82 at list prices. The reps keep those settings (DF3), and V7 and V8 check them.

Evidence (cache, never committed): the audit verifier's transcript `~/.claude/projects/-Users-lowell-Projects-agent-skills--claude-worktrees-cc-drift-first-jobs/f7c1fcfe-08ca-4218-b6f5-be9d30ef1f08/subagents/agent-ac5b7b4a063e4ccdc.jsonl`, and the rules verify's `~/.claude/projects/-Users-lowell-Projects-agent-skills/f3828a8d-d37d-4dc3-89f2-31819ce23470/subagents/agent-a9d4a3fdeb9e1fb16.jsonl`.

### Ground-truth key (the audit packet, guide numbering of `5bd78a7`)

The key is built from `3c10cb4`'s guide diff and the original report (`~/.cache/agent-skills/cc-guide/packets/20261013T113847-audit/report.md`). The original found 8 of the diff's 13 positives as PARTIAL rows, plus P14 as a B and a C row. It made no false-positive correction: all 8 PARTIALs were applied.

| Label | Claim (pre-fix line) | Original | Role |
|---|---|---|---|
| P1 | Haiku 4.5 retirement dates (L211) | PARTIAL, report.md:14 | retention |
| P2 | Explore under a Fable session (L218) | PARTIAL, :23 | retention |
| P3 | `SUBAGENT_MODEL_FORCE`'s reach (L218) | PARTIAL, :29 | retention |
| P4 | helper requests get the 1-hour TTL (L405) | PARTIAL, :36 | retention |
| P5 | `/compact` rebuilds by design (L410) | PARTIAL, :50 | retention |
| P6 | the effort-change cache caveat (L426) | PARTIAL, :72 | retention |
| P7 | `max` lasts the current session only (L426) | CONFIRMED, :74 | secondary |
| P8 | a top-level `effortLevel` no longer counts for Opus 5.5 (L426) | CONFIRMED, :73-74 | secondary |
| P9 | `ANTHROPIC_DEFAULT_MODEL` in the precedence chain (L429) | PARTIAL, :82 | retention |
| P10 | Sonnet 4.5 behind the partner-platform `sonnet` alias (L429) | CONFIRMED, :85 | secondary |
| P11 | `deniedModels` beside `availableModels` (L429) | CONFIRMED, :87 | **gate** |
| P12 | `enforceAvailableModels` honoured in any settings file (L429) | CONFIRMED, :88 | secondary (contested) |
| P13 | the tokenizer comparison's direction (L441) | PARTIAL, :101 | retention |
| P14 | `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL` (L218, L429) | B :112, C :122 | retention |

- P12 is contested. `model-config.md:307` and `changelog.md:5228` say "managed", while `settings-reference.md:673` says any file. The original never opened `settings-reference.md`, so its CONFIRMED can be defended from the page it quoted. P12 stays secondary and outside the deferred item's seven (DF9).
- P14 is not in the diff: the guide still lacks it, and no 2.1.296 page names it.
- The original wrote no B row for the changelog entries behind P7 (`changelog.md:224`), P8 (`:1702`) or P11 (`:1288`).

For the cheap packets:
- **(d) rules** (`packets/20261013T175307-verify/rules/`): D1 is the L252 trigger claim. The original rated it CONFIRMED at report.md:5, and `8d82ecf` later fixed it.
- **(b) readme** (`packets/20261013T121854-files/hooks__README.md/`):
  - B1, the unquoted `$CLAUDE_PROJECT_DIR` at `hooks/README.md:57`, `:61` and `:65`: not covered at report.md:9, fixed by `3c10cb4`;
  - B2, the `onFailure` exit-code note at `:99`: contradicts at report.md:16, found.
- **(c) runner** (`packets/20261013T124015-files/agents__test-runner.md/`): the range row at report.md:9.
- **(e) pyrule** (`packets/20261013T205255-files/rules__clean-code-python.md/`): E1 is the load trigger at the packet's `cited_clean-code-python.md:7` and `:9`, rated `consistent` at report.md:3 and its line-9 row. The packet was built from `938993c`'s working tree, after `8d82ecf`, so its `guide.md` already gives the corrected trigger at lines 246–255. In files mode the guide is the reference the verifier is meant to read, so that is the fixture working as designed, not a Channel 3 leak; the cited copy still carries the old lines.

### The contract change, and why this form

Three drafts were written by independent agents, each from its own angle, and two adversarial judges scored them. Both judges picked the procedure draft, with grafts. The text below is that synthesis. Its precision guard is the failure test, "someone who followed its guide line as worded would get that case wrong", which every downgrade must pass. A "such as" list, or extra doc detail that leaves the line right, stays CONFIRMED. The passage boundary is concrete: the quoted line's paragraph, its doc section, and pages already opened. It adds no docs-wide search, because every qualifier in the evidence sat in a Read result the verifier already had.

The files text compares only the parts a cited example shares with the statement that use a name or value Claude Code supplies or reads. So a harmless departure, such as a script's own interpreter flags, stays out of reach. Its `consistent` and `contradicts` are defined by the A rows' failure test, with the cited sections as the passage, so (e) needs no rule of its own: a statement that leaves out a case the guide gives fails in that case.

Two rules came from the Codex review (Independent review), and they divide the ground between them by whose behaviour a line describes:
- **The item rule (DF18).** A line that gives the items for a job, such as the controls or triggers that do it, fails in the case of each further item its passage gives for that job, unless it marks them as examples. Without it, a careful reader could keep L429 CONFIRMED, since an extra deny list does not make the allow list's sentence false. It covers P11, (d) and (e), all of which are Claude Code's behaviour.
- **The choice guard (DF19).** A files statement of a choice the file makes for itself fails only when the choice does not do what the file says it does, never for differing from an example. So `hooks/README.md`'s `"matcher": "Bash"` at :56 and :129, where the guide's example uses `"Write|Edit"`, stays `consistent`. Those two lines are pre-registered negative controls, N1 and N2.

The judges' precision warnings became the pre-registered precision rule. Task 1's term gate shows that the added text names no fixture answer.

### Settled defaults (your human partner reviews each)

- **DF1, scope: all five defects in one contract edit.** They share `.claude/agents/cc-guide-verifier.md` and its tests, so splitting them would rerun every arm. If wrong: drop (b)–(e)'s text from Task 1 and their arms from Task 4.
- **DF2, the acceptance bar (Pre-registration, "Decision rules"):**
  - the changed arm hits P11 in at least 4 of 5 valid reps;
  - the control hits it in at most 1 of 5;
  - the control reaching 2 hits stops the gate;
  - a precision ceiling and a retention floor must also hold.

  The 4 of 5 is the backlog's bar for the synthesize-mode re-run (`specs/deferred_items.md:2984`). If wrong: too loose passes noise, and too strict makes the done-when unreachable.
- **DF3, rep condition: production's.** User settings load, so the reps run in auto mode with the Opus advisor available and Sonnet 5.5 at `xhigh`, as every production run did. `--restricted` was considered and rejected: it drops user settings, so a control rep would run at `medium` with no advisor and measure the setup, not the contract. If wrong: the owner may prefer no advisor (cheaper, less variance, unlike production). Then pass `--settings` with `advisorModel` unset in both arms, and V8 inverts.
- **DF4, isolation route: a read fence, not `--restricted`.**
  - `--settings '{"permissions":{"blockReadsOutsideWorkingDirectories":true}}'` refuses Read, Grep and Glob outside the working directories in every mode (`settings-reference.md:1614-1641` in the snapshot), and `--add-dir` adds exactly the docs snapshot.
  - The probe (Task 3) confirms that the fence binds a subagent; that `--add-dir` counts; and what the "files Claude Code itself needs" exemption leaves readable.
  - V2 voids any outside read that returned, so validity never rests on the fence alone.
- **DF5, the owner launches every rep from a plain terminal** (plan 42's precedent). A Claude Code shell exports `CLAUDECODE`, `CLAUDE_CODE_ENTRYPOINT` and `CLAUDE_EFFORT` into children: plan 44's probes, launched from the app, recorded `claude-desktop`. From a plain terminal, `claude -p` records `sdk-cli` (276 transcripts on this Mac do), where production's interactive verifier recorded `cli`; the pilot records that known difference. `run.py` refuses inside Claude Code.
- **DF6, order: the cheap arms first, then the gate in two waves.** (d) shows the same failure at about $0.30 a rep, so the wording meets it before the $3-a-rep gate. The gate's first wave (2 + 2) stops early when the control's P11 hits reach 2 (Pre-registration, "Decision rules"). The probe and the pilot are validity runs whose arm is known, so they count toward no result.
- **DF7, the precision ceiling.** Every kept correction, key-matched or not, is read by hand and rated SUPPORTED or UNSUPPORTED, its proposed scope and conditions included. The changed arm's UNSUPPORTED total over its valid gate reps is at most the control's total + 3, and no single changed rep has more than 2. If wrong: tighten to + 1 and 1 per rep for a stricter guard, or loosen for a noisier verifier.
- **DF8, the retention floor.** For each of P1–P6, P9, P13 and P14, the changed arm finds it in at least as many valid reps as the control, minus one.
- **DF9, roles.** P12 is secondary, being contested and outside the seven. P14 counts toward retention as a B, C or A row.
- **DF10, what counts as a P11 hit.** It is a kept STALE, WRONG or PARTIAL A row on guide lines 415–442, or a C row, whose text names `deniedModels` as blocking a model the allow list would permit, and which is SUPPORTED. A row that proposes `deniedModels` outside managed settings is UNSUPPORTED, so no hit: the docs make it managed-only (`settings-reference.md:920-925` in the snapshot). A B row alone does not count; a B-only mention is reported. The brief proposed the bar; the SUPPORTED clause is the Codex review's finding 5. C rows carry no quote, so a C hit is defined by its text alone.
- **DF11, the record** goes to `specs/completed/verifier-recall-verification-<date>.md`, in plan 42's house format but with counts, labels and pointers only (plan 44's form for docs-derived rows).
- **DF12, (d)'s packet is used as production built it.** Its `sections.md` carries the triage row that sent L252 to verify, and that row names the missing triggers. It is production input, and the original verifier missed it anyway.
- **DF13, the main session runs Sonnet**, as plan 44's real-agent probe did. Production's main ran Opus, which would add about $0.28 a rep and change nothing the subagent sees, since V1 pins the dispatch exactly.
- **DF14, out of scope: verify-mode `doc:line` ranges.** A range there also fails settle's parse and discards the row (`settle.py:509-511`). No evidence of one exists yet.
- **DF15, blind reading.** Each counted batch is (control, changed) pairs of one packet, and `build.py` puts each pair's arms in a random order, so neither a rep id nor the schedule names an arm. A spare is built from the void rep's id, so the reader never needs its arm. Sheets name no arm. `plan.json`, the rep directories' agent files and the reps' verifier transcripts, whose first prompt part is the arm's contract, are the only places that do, and they stay closed until every hand verdict is in `K/RESULTS.md` and `grade.py unblind` runs. A report's own wording may still suggest its arm; that is the effect being measured, not a leak. If wrong: the owner may want a separate grading session that has seen nothing of the schedule (the Codex review's suggestion), at the cost of a second context reading every report.
- **DF16, (e) is in scope.** A peer session forwarded it, at the owner's request, while this plan was being written (2026-10-13). It is (d)'s failure in files mode, and the files verdicts as first drafted ("agrees with the prose") would not have caught it. So Task 1 gives the files verdicts the same failure test, its new test pins that both modes use it, and Task 4 adds a cheap arm on its packet (about $0.15–0.50 a rep). This is evidence the owner sent, not a scope decision the owner made. If wrong: drop the files failure-test bullet and the `files` case of `test_each_mode_rates_by_the_same_failure_test` from Task 1, restore "agrees with the prose" and "disagrees with the prose", drop the matching clauses of R8.7 and R12.4 in Task 1 Step 6, and drop the `pyrule` arms.
- **DF17, out of scope: one files row per checkable statement.** A source line can make two statements (`README.md:163`), and the verifier may rate one. A rule giving each statement its own row would change row volume and precision in every files rep, and its only fixture is the expensive eight-section README packet. It goes to the backlog (Task 6). If wrong: add the rule to Task 1's files bullets, and the README packet to Task 4 with its own key.
- **DF18, the item rule: a line that gives the items for a job is judged for coverage**, as the Codex review's open question asked. Its precision guard is "unless it marks them as examples", and DF7's ceiling measures what it costs. If wrong: drop the item-rule bullet from both parts of Task 1, the `each further item` assertion, and the item-rule clauses of R8.5, R8.7 and R12.4 in Task 1 Step 6; the review's argument then predicts the changed arm may still keep P11 and (e).
- **DF19, the choice guard, with N1 and N2 as negative controls.** If wrong (the owner wants a file's departures from guide examples flagged even when deliberate): drop the guard's bullet and its test, and its clauses in R8.7 and R12.4 in Task 1 Step 6, and score N1 and N2 as positives.
- **DF20, closing the observations.** (b) and (c) are the item at `:3181`'s own observations; (d)'s item is already ticked and (e) has none, so theirs are reported in the record only. (b) closes when the changed arm hits B1 in at least 2 of its 3 valid reps and flags N1 or N2 in at most 1; (c) when it passes in all 3, since a single range holds the file; (d) and (e) when it hits in at least 2 of 3. The record reports the control's counts beside them. If wrong: these are closure rules for the backlog, not the gate, so a stricter or looser rule changes Task 6's tick only. An observation whose arm misses its rule when the item is ticked is re-filed as an open item in this plan's backlog section.
- **DF21, correction volume is reported, not gated.** The item rule's likely cost is a run of true but marginal additions: SUPPORTED rows that DF7 never counts, each one a guide edit the owner must review. So every rep's correction count is pre-registered as a report-only measure: the sheet's settle line, `N correction(s)` for an audit or verify rep and `N contradiction(s)` for a files rep, the rows settle applies (owner's-call rows are counted there separately). It is reported for every packet, with each arm's median and total over the valid reps. If wrong (the owner wants it to gate): add a FAIL clause before the freeze, for example the changed arm's median above twice the control's.

### The brief's traps, and where each is handled

- **T1, two of the done-when's three inputs live only in the cache.** The audit packet and the 2.1.296 docs are read in place: never written, never copied into the repo. The packet's `guide.md` is byte-identical to `5bd78a7`'s guide (checked with `cmp`).
- **T2, line numbers.** The key uses the packet's own numbering, and rows are scored by claim (Global Constraints).
- **T3, the C cap.** The cap stays. A qualifying omission now goes on its claim's PARTIAL row, so the cap no longer competes with recall.
- **T4, (b)–(e) need their own packets.** They are used as they are: `main` gives away all their answers ((e)'s since lowmason/agent-skills#45, B1's and B2's since `3c10cb4`), and no rep can read `main`. (e)'s packet holds the corrected guide, as files mode intends (Ground-truth key).
- **T5, (d), the calibration miss.** It is defect (d), Task 4.
- **T6, rebuilding a packet.** Not needed: the fix is contract-side, so no packet is rebuilt and `latest/` can move freely.
- **T7, pinned formats.** Task 1 leaves every pinned string as it is, and its tests observe that.
- **T8, the contract is spec text.** Task 1 amends R8.1, R8.5, R8.7 and R12.4, and the spec stays live (Stages 4–5 remain).
- **T9, rep isolation.** Isolation is handled by Channels 3 and 5 (Global Constraints), the VOID rules, copies without `report.md`, and replies saved in `K`, outside every packet.
- **T10, cost.** The cost is below, under the Task 3 gate.

### Cost (the owner approves it at Task 3)

The per-rep figures are list-price estimates from the production transcripts:
- audit verifier: about $1.70, plus about $1.12 for the advisor;
- rules verify: about $0.20;
- readme files: about $0.21;
- runner files: about $0.08;
- pyrule files: not measured, but its packet is the smallest (a 1.3 kB cited copy beside the guide).

Each rep also pays for the main session (about $0.10–0.15 on Sonnet) and for auto mode's classifier, which plan 44's probe measured at up to $0.52 a run. The probe and pilot measure the classifier here.

| Run | Reps | Per rep | Subtotal |
|---|---|---|---|
| probe | 1 | $0.10–0.30 | ≤ $0.30 |
| pilot (rules, control) | 1 | $0.30–0.90 | ≤ $0.90 |
| cheap: rules | 6 | $0.30–0.90 | $1.80–5.40 |
| cheap: readme | 6 | $0.30–0.80 | $1.80–4.80 |
| cheap: runner | 6 | $0.20–0.60 | $1.20–3.60 |
| cheap: pyrule | 6 | $0.15–0.50 | $0.90–3.00 |
| gate, two waves | 10 | $3.00–5.50 | $30–55 |
| spares, if needed | ≤ 2 per packet and arm | as above | ≤ $22 audit, ≤ $11 cheap |

Expected: about $40–70. **Ceiling to approve: $100.** The per-rep caps are `--max-budget-usd`: audit $8, verify $3, files $2. A rep that hits its cap is VOID. The caps sum to $140 before spares (probe and pilot $6, cheap $54, gate $80), more than the ceiling, so `run.py`'s full-cap reservation can hold a late rep even when actual spend is well under it; that rep is then the owner's call (Global Constraints, "Spend").

### Independent review

Codex (`gpt-6-astra`, effort `xhigh`, the owner's per-seat choice) reviewed the first draft read-only against the deferred item, the spec, the brief, the peer's evidence, plans 42 and 44, the replay and the prototype kit. Prompt and report: `~/.cache/agent-skills/scratch/plan45-review/`. It returned 12 findings: 7 P1, 4 P2 and 1 P3. Each was checked against the code or the docs before it was acted on, the kit's by a test that failed first. Nine are fixed outright. Three are fixed by a rule that is also a default for the owner's review: 3 (DF19), 4 (DF18) and 6, whose separate grading context was not adopted (DF15 names it as the alternative):
- **1, V2 missed relative and symlinked escapes:** `grade.normal` resolves every path from the rep directory with `realpath`, listed relative paths are screened, and three tests reproduce it (Task 2).
- **2, answer text in a later prompt part escaped V3 and V5:** every snapshot is checked, every part but the contract body is screened, `compare` counts parts, and `grade.py context` gives the pilot's whole injected context to a hand reading (Task 3, Step 8).
- **3, examples made normative:** the choice guard and negative controls N1 and N2 (DF19).
- **4, a true-but-incomplete line could stay CONFIRMED:** the item rule (DF18).
- **5, a key-matched row escaped the precision rating:** every kept correction is rated, and a hit must be SUPPORTED, scope included (DF7, DF10). Its example, `deniedModels` proposed in project settings, is managed-only in the docs, so the finding was right.
- **6, the fixed schedule revealed arms:** random arm order within each pair, spares by rep id, and an uncounted pilot (DF15).
- **7, the ceiling was not enforced:** full-cap reservation against `K/ceiling.txt`, unfinished reps counted at their cap (Global Constraints, "Spend").
- **8, a revision could not rerun:** a revision is a new round in a fresh kit directory (Task 4, Step 6).
- **9, progress text could be graded as a report:** the report is a handback, or a finished Agent result that is no launch notice. A failed or killed subagent is void (V6). Production's own Agent result was a launch notice, since it dispatched in the background.
- **10, (c) passed when the verifier checked nothing:** a pass needs a kept one-line row on lines 14–16 (R1).
- **11, V8 did not pin the advisor:** every advisor attachment must be available on `claude-opus-5-5`, and `~/.claude/settings.json` is hashed per batch.
- **12, the arm diff's line count:** it is 20 agent lines; the term gate's 22 counts `formats.md` too.

It confirmed the first draft's anchors, its byte-identical kit and replay, its RED and GREEN counts by direct execution (11 failed and 12 passed), its term gate (19 lines), all five control lines, and the diagnosis's transcript facts. The current counts (12 and 12, 22 lines, 43 kit tests) are the planner's own replays, on `938993c` and on `2e9ee0f`. Its sandbox could not run the kit's filesystem tests. Its two open questions are settled as DF18 and DF20.

The fix wave's own wording, the item rule, the choice guard and the redefined files verdicts, has had no independent review: the seat read the earlier text. The owner chose no second seat (D4): the cheap arms and the gate measure it.

A consistency check before the plan's PR (three read-only agents, each finding verified by a fourth) confirmed 49 findings, 26 once merged, about cross-references, the key against the retention rule, the revision round, the listings, the volume measure, the pinned Claude Code binary (the PATH's `claude` had moved to 2.1.299) and the pilot's expectations. All are fixed in this text and the kit, the kit's by 2 new tests. The planner then found that the updater prunes old versions, so the kit runs a held copy whose hash Task 3 checks.

### Plan ID

`entry_check.py` printed `highest: 44`, `next free: 45`, `collisions: none` on 2026-10-13.

---

## Pre-registration (fixed before any rep runs)

Task 3 freezes the pre-registration and the kit in `K/FREEZE.sha256`. Any change after that is logged in `K/changes.log` with the freeze hash before and after, and it never follows a result it would affect.

**Arms.**
- **control:** `.claude/agents/cc-guide-verifier.md` at `938993c`, blob `ae9e2e2e29f31421dbf02ddaf62d6910c39d33ba`. It is unchanged since `89d3fe0`, so it is the contract that ran the 3-of-7 audit.
- **changed:** the file at Task 1's commit.

The two bodies differ only in Task 1's added lines. The frontmatter also differs in its `# cc-guide:` citation stamp, which lowmason/agent-skills#45 restamped on `main` (`@2.1.296` to `@2.1.296.1`); frontmatter never reaches the verifier's system prompt (V5 compares bodies). Both files are copied to `K/arms/` and hashed in the freeze.

**Packets and reps.**

| Packet | Path under `~/.cache/agent-skills/cc-guide/packets/` | Mode | Valid reps per arm |
|---|---|---|---|
| audit | `20261013T113847-audit` | audit | 5 |
| rules (d) | `20261013T175307-verify/rules` | verify | 3 |
| readme (b) | `20261013T121854-files/hooks__README.md` | files | 3 |
| runner (c) | `20261013T124015-files/agents__test-runner.md` | files | 3 |
| pyrule (e) | `20261013T205255-files/rules__clean-code-python.md` | files | 3 |

The probe and the pilot count toward no result. Each counted batch is `K/common.py`'s `SCHEDULE` of (control, changed) pairs of one packet, and `build.py` puts each pair's arms in a random order (DF15). Each rep is one `claude -p` session, launched by `K/run.py` with the argv `run.command` builds and the prompt `common.MAIN` on stdin. It runs in `R/<rid>/`, which holds `.claude/agents/cc-guide-verifier.md` (the arm's file) and the packet copy at its own relative path. The audit and rules reps add the docs snapshot `~/.cache/agent-skills/cc-guide/2.1.296/docs` with `--add-dir`. Record that directory's `shasum -a 256` listing, and `shasum -a 256 ~/.claude/settings.json`, before and after each batch: neither may change.

**VOID rules.** A rep is void when any of these holds (`K/grade.py`):
- **V1:** the main session made any tool call but one Agent call (an advisor call, a server tool, excepted); or that call's `subagent_type` is not `cc-guide-verifier`, its prompt is not the exact dispatch, or it passes a parameter beyond `description`, `subagent_type` and `prompt`; or the session holds no verifier transcript, or more than one.
- **V2:** a verifier Read, Grep or Glob naming a path outside the rep directory and, for audit and verify reps, the docs snapshot returned, or a Grep or Glob result listed such a path. A path is resolved as the fence would see it: `~` expanded, a relative path taken from the rep directory, and symlinks followed. A call the fence refused is logged, not void.
- **V3:** an injected attachment, prompt-snapshot part or system record of the verifier carries answer content. `grade.py` pre-screens all of them but the contract body for `common.MARKERS`, and every hit is traced by hand: a path or a tool name is not content. The pilot's whole injected context is also read by hand (Task 3, Step 8). The main session's hits are recorded only, since V1 pins all it passes on.
- **V4:** the verifier has an `instructions` attachment, or a `session_context` that holds `gitStatus`.
- **V5:** a `prompt_snapshot`'s first system-prompt part, in any snapshot, is not the arm file's body.
- **V6:** no report arrived, or the run failed: no result record, `is_error`, a budget stop, a timeout, a subagent that failed or was killed, or neither a handback nor a finished Agent result (a launch notice is not one). The verifier's own last text never counts as its report.
- **V7:** any verifier assistant record is not `claude-sonnet-5-5` at effort `xhigh` on version `2.1.296`.
- **V8:** an advisor attachment of the verifier is unavailable or not `claude-opus-5-5`, or it has none.

**Replacement.** A void rep is replaced with `build.py spare <rid>`, which builds a rep with the void rep's packet and arm, so the reader never sees the arm. At most 2 spares per packet and arm: `build.py` refuses a third, without naming the arm. With fewer valid reps than the target after that, the packet's result is UNSETTLED: report it to the owner.

**Scoring.** `grade.py <batch>` writes one sheet per rep (`K/sheets/<rid>.txt`), naming no arm. The controller reads every candidate row and every kept correction against the rep's report (`K/reports/<rid>.md`) and the docs or guide line it cites. The controller records each verdict in `K/RESULTS.md` before running `grade.py unblind`.
- **Precision (every packet).** Every kept correction, a key-matched one included, is rated:
  - **SUPPORTED:** the passage its quote comes from gives the case the row adds, and its proposed wording gives that case's scope and conditions as the passage does. This is neutral: it may be a real gap the owner never applied.
  - **UNSUPPORTED:** that passage does not give the case, the proposed wording gets its scope or conditions wrong, or the wording changes nothing a follower of the guide line would do.

  A candidate rated UNSUPPORTED is no hit. Only kept A and F corrections enter a rep's UNSUPPORTED total; a C or B row rated UNSUPPORTED is only no hit.
- **Gate (audit, P11).** A hit is either of these, read by hand, and SUPPORTED:
  - a STALE, WRONG or PARTIAL row on guide lines 415–442 that settle kept (its quote was found and it gives wording), whose claim or proposed wording names `deniedModels` as blocking a model the allow list would permit;
  - a C row naming `deniedModels` with that meaning.

  A row that puts `deniedModels` in user, project or local settings is UNSUPPORTED (`settings-reference.md:920-925`). A B row alone, a JUDGMENT or NOT FOUND row, or a discarded row is not a hit. A B-only mention is reported.
- **Volume (every packet, report only).** Each rep's correction count, from its sheet's settle line (`N correction(s)`, or `N contradiction(s)` for a files rep); per packet and arm, the median and the total over the valid reps (DF21).
- **Retention and secondary (audit).** For each of P1–P14, count the valid reps per arm whose kept corrections, C rows or (for P14) B rows carry it.
- **(d) rules.** A hit is a kept, SUPPORTED STALE, WRONG or PARTIAL row on guide lines 246–255 about the rule-load trigger whose wording adds the Write tool or the Bash read.
- **(b) readme.** A hit is a kept, SUPPORTED `contradicts` row on `hooks/README.md` lines 55–66 about the unquoted `$CLAUDE_PROJECT_DIR`, with its guide quote found. B2 is retention. A kept `contradicts` row on N1 or N2 (the `Bash` matcher at :56 or :129, the file's own choice) is UNSUPPORTED, and is counted on its own as well. Other `contradicts` rows are rated against `3c10cb4`'s diff of the file and the guide.
- **(c) runner.** A rep passes when a kept files row on `agents/test-runner.md` lines 14–16 (R1) gives one line number, no files row names a line range, and the sheet's hold lines show no `unparseable:` row. A hold for another reason, such as a left-out section, is recorded but does not fail (c). A report that rates nothing there fails.
- **(e) pyrule.** A hit is a kept, SUPPORTED `contradicts` row on `rules/clean-code-python.md` lines 6–10 about the rule's load trigger, whose statement or quote gives a case the line leaves out (the Write tool, or a single-file Bash read), with its guide quote found. One hit per rep, however many lines it covers. Other rows are rated against the packet's guide.

**Decision rules.**
- **The cheap checkpoint** (Task 4) is reported to the owner before the gate. The owner decides whether to proceed, revise the wording (a logged change, the cheap arms rerun) or stop, when any holds:
  - the changed arm misses (d) in 2 or more of its 3 valid reps;
  - the changed arm misses (e) in 2 or more of its 3 valid reps;
  - the changed arm fails (c) in any valid rep;
  - the changed arm flags N1 or N2 in 2 or more of its 3 valid (b) reps;
  - a changed (b) or (e) rep has more than 2 UNSUPPORTED `contradicts` rows.
- **The gate's first wave.** If the control's P11 hits reach 2, stop: the failure is not reliable under these conditions. Report, and run no second wave.
- **PASS** when all hold over the valid gate reps:
  - the changed arm hits P11 in at least 4 of 5;
  - the control in at most 1 of 5;
  - the changed arm's UNSUPPORTED total, over every kept correction, is at most the control's + 3, and no changed rep has more than 2;
  - for each of P1–P6, P9, P13 and P14, the changed arm's count is at least the control's count minus 1.
- **FAIL** otherwise. Report to the owner. No rerun or revision without the owner's go and a new spend approval.
- **Closing the observations** (b)–(e) follows DF20, and is reported beside the gate, not part of it.

**Rulings.** Before the cheap batch, the pilot may fix two things, logged in `K/changes.log`. How a fence refusal shows is the probe's, and a refusal that is not an error stops the run (Task 3, Step 7).
- an Agent parameter that changes nothing the verifier sees (V1);
- how a `-p` session's result counts a verifier dispatched in the background (V6's `subagent_stats` and report source).

No post-hoc rulings.

---

### Task 1: The contract and the spec amendments

**Files:**
- Modify: `build/cc_guide/test_skill_files.py` (append after the last test)
- Modify: `.claude/agents/cc-guide-verifier.md` (after the C-row bullet; after the files paragraph)
- Modify: `.claude/skills/cc-guide/references/formats.md` (after the files template)
- Modify: `specs/claude-code-drift-automation-spec.md` (R8.1, R8.5, R8.7, R12.4)

**Interfaces:**
- Produces: the changed arm, the file `.claude/agents/cc-guide-verifier.md` at this task's commit, which Task 3 copies to `K/arms/changed.md`.

Each spec edit is tagged `(owner, plan 45, 2026-10-14)`; the status line stays untouched. Your human partner approves this wording at plan review.

- [x] **Step 1: Write the failing tests**

Append to `/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall/build/cc_guide/test_skill_files.py`, after `test_the_skill_and_the_verifier_state_the_report_formats_settle_parses`:

```python


def contract_part(heading: str) -> str:
    '''The verifier's text under one `###` heading, up to the next.'''
    text = (REPO / AGENT).read_text(encoding='utf-8')
    start = text.index(f'### {heading}\n')
    end = text.find('\n### ', start + 1)
    return text[start:] if end == -1 else text[start:end]


@pytest.mark.parametrize('verdict', ['CONFIRMED', 'PARTIAL', 'STALE', 'WRONG'])
def test_the_verifier_defines_each_verdict_a_correction_turns_on(verdict):
    '''Plan 45: an audit rated true claims CONFIRMED while the passage it
    quoted gave a case they get wrong, since nothing defined the verdicts.'''
    assert f'{verdict}: ' in contract_part('verify and audit')


@pytest.mark.parametrize('verdict', ['consistent', 'contradicts', 'not covered'])
def test_the_verifier_defines_each_files_verdict(verdict):
    '''Plan 45: a files verifier rated a statement not covered that departed
    from the guide's own example.'''
    assert f'`{verdict}`: ' in contract_part('files')


@pytest.mark.parametrize('part', ['verify and audit', 'files'])
def test_each_mode_rates_by_the_same_failure_test(part):
    '''Plan 45: a files verifier wrote that a statement left out cases the
    guide gives, and still rated it consistent.'''
    assert 'as worded would get that case wrong' in contract_part(part)
    assert 'each further item' in contract_part(part)


def test_a_files_choice_that_differs_from_an_example_is_no_failure():
    '''Plan 45, review finding 3: a file that states a choice of its own,
    which a guide example makes differently, must not be rated contradicts.'''
    assert 'is no failure' in contract_part('files')


@pytest.mark.parametrize('path', [AGENT, FORMATS])
def test_a_files_row_gives_one_line_number(path):
    '''Plan 45: settle reads a files row's `file:line` with one line number,
    and a range is unparseable, which holds the file.'''
    assert 'gives one line number' in (REPO / path).read_text(encoding='utf-8')
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_skill_files.py`

Expected: `12 failed, 12 passed`. Each failure is an `AssertionError` on an absent string:
- `test_the_verifier_defines_each_verdict_a_correction_turns_on` for `CONFIRMED`, `PARTIAL`, `STALE` and `WRONG`;
- `test_the_verifier_defines_each_files_verdict` for its three verdicts;
- `test_each_mode_rates_by_the_same_failure_test` for both parts;
- `test_a_files_choice_that_differs_from_an_example_is_no_failure`;
- `test_a_files_row_gives_one_line_number` for both paths.

- [x] **Step 3: Add the verify and audit recipe to the verifier**

**Edit** `.claude/agents/cc-guide-verifier.md` — replace:

```text
- C, at most four rows: omissions that would change the guide's existing advice.
```

with:

```text
- C, at most four rows: omissions that would change the guide's existing advice.

Rate each A row this way:

- Take the claim as its guide line states it, and work through its passage: the doc line's paragraph, the rest of the doc section that holds it, from its heading to the next heading that is not one of its subheadings, and what the other pages you have opened say of the names in the claim.
- The cases to test are the passage's exceptions, conditions and limits, and the further items it gives for the same job. A claim fails in a case when someone who followed its guide line as worded would get that case wrong.
- A claim that gives the items for a job fails in the case of each further item its passage gives for that job, unless its guide line marks them as examples.
- CONFIRMED: a doc line supports the claim, and the claim fails in no case. `doc:line` and the quote give that line.
- PARTIAL: a doc line supports the claim in the case it describes, and the claim fails in a further case. `doc:line` and the quote give the line that gives that case, and the proposed wording covers it.
- STALE: a doc line shows the claim failing in the case it describes, and a changelog or doc line records the change. WRONG: a doc line shows that failure, and no line records the claim ever holding.
- An omission that makes a claim in scope fail in a case goes on that claim's row as PARTIAL; C rows hold the omissions no A row carries.
- Last, before you return the report, rate again each A row whose claim one of your B rows changes, with that B row's item as one more case.
```

- [x] **Step 4: Add the files failure test, its item rule and choice guard, the files verdicts and the one-line rule**

**Edit** `.claude/agents/cc-guide-verifier.md` — replace:

```text
`file` is the path `index.json` names as `file`, as in `hooks/README.md:56`. A not-covered row may leave its quote `-`. A cited section with no row and no none line holds the file, as if unreviewed.
```

with:

```text
`file` is the path `index.json` names as `file`, as in `hooks/README.md:56`. A not-covered row may leave its quote `-`. A cited section with no row and no none line holds the file, as if unreviewed.

- A row's `file:line` gives one line number, the line its statement starts on.
- A statement fails in a case when someone who followed it as worded would get that case wrong. The cases to test are the cited sections' exceptions, conditions and limits, and the further items they give for the same job.
- A statement that gives the items for a job fails in the case of each further item the cited sections give for that job, unless it marks them as examples.
- A statement of a choice the file makes for itself fails when the choice does not do what the file says it does. A choice that differs from an example's is no failure.
- A cited section's examples are evidence, as its prose is. Compare each part of the statement that a cited example also has and that uses a name or value Claude Code supplies or reads.
- `consistent`: the statement fails in no case the prose gives, and each such part does what the file says it does for every value Claude Code could supply.
- `contradicts`: the statement fails in a case the prose gives, or such a part fails to do what the file says it does for some value Claude Code could supply, where the example's part does it. The quote gives the guide line that gives the case, or the example's line.
- `not covered`: nothing in the cited sections' prose or examples bears on the statement.
```

**Edit** `.claude/skills/cc-guide/references/formats.md` — replace:

```text
    file:line | statement | section | "verbatim guide quote" | consistent / contradicts / not covered
    section | none
```

with:

```text
    file:line | statement | section | "verbatim guide quote" | consistent / contradicts / not covered
    section | none

A files row's `file:line` gives one line number, the line its statement starts on: settle reads a range as no row, which holds the file.
```

- [x] **Step 5: Run the suite to verify it passes**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall/build/cc_guide --python 3.13 --with pytest python -m pytest -q`

Expected: all pass, at the baseline +12. The existing TODO(owner) and FORMATS tests stay green.

- [x] **Step 6: Amend the spec**

**Edit** `specs/claude-code-drift-automation-spec.md` (R8.1) — replace:

```text
  lists it. Its body holds the contract: the modes, the report formats, the
  accuracy and JUDGMENT rules, and never editing a file. Without `Bash` it
```

with:

```text
  lists it. Its body holds the contract: the modes, the report formats, the
  accuracy and JUDGMENT rules, the verdict definitions of R8.5 and R8.7
  (owner, plan 45, 2026-10-14), and never editing a file. Without `Bash` it
```

**Edit** (R8.5, the report contract) — replace:

```text
    verifier's own paraphrase, never a doc sentence. Absence of evidence alone
    is NOT FOUND, never WRONG.
  - **B.** Changelog items that change a claim in scope: version, one line,
    changelog line number.
  - **C.** At most four omissions that would change existing advice.
```

with:

```text
    verifier's own paraphrase, never a doc sentence. Absence of evidence alone
    is NOT FOUND, never WRONG. Each A row is rated against its claim's
    passage: the doc line's paragraph, the rest of the doc section that holds
    it, and what the other pages the verifier opened say of the names in the
    claim. A claim fails in a case when someone who followed its guide line as
    worded would get that case wrong; the cases are the passage's exceptions,
    conditions and limits and the further items it gives for the same job. A
    claim that gives the items for a job fails in the case of each further
    item its passage gives for that job, unless its guide line marks them as
    examples. CONFIRMED: a doc line supports the claim and it fails in no case.
    PARTIAL: a doc line supports it in the case it describes and it fails in
    a further case, which its quote and proposed wording give. STALE: a doc
    line shows it failing in the case it describes, and a changelog or doc
    line records the change; WRONG: a doc line shows that failure and no line
    records the claim ever holding. Before returning, the verifier rates
    again each A row whose claim one of its B rows changes, with that item as
    one more case (owner, plan 45, 2026-10-14).
  - **B.** Changelog items that change a claim in scope: version, one line,
    changelog line number.
  - **C.** At most four omissions that would change existing advice. An
    omission that makes a claim in scope fail in a case is that claim's
    PARTIAL, and C rows hold the omissions no A row carries (owner, plan 45,
    2026-10-14).
```

**Edit** (R8.7 step 2) — replace:

```text
   and a `<section> | none` line for each cited section no statement rests
   on (owner, plan 44, 2026-10-12).
```

with:

```text
   and a `<section> | none` line for each cited section no statement rests
   on (owner, plan 44, 2026-10-12). A row's `file:line` gives one line
   number, the line its statement starts on. A statement fails in a case
   when someone who followed it as worded would get that case wrong, as an
   A row's claim does (R8.5); the cases are the cited sections' exceptions,
   conditions and limits and the further items they give for the same job,
   and a statement that gives the items for a job fails in the case of each
   further item unless it marks them as examples. A statement of a choice
   the file makes for itself fails when the choice does not do what the file
   says it does; a choice that differs from an example's is no failure. A
   cited section's examples are evidence, as its prose is: a statement
   `contradicts` a section when it fails in a case the prose gives, or when
   a part of it that an example also has, and that uses a name or value
   Claude Code supplies or reads, fails to do what the file says it does for
   some value Claude Code could supply where the example's part does it; it
   is `consistent` when it fails in no case the prose gives and each such
   part does what the file says it does for every value Claude Code could
   supply, and `not covered` when nothing in the cited sections' prose or
   examples bears on it (owner, plan 45, 2026-10-14).
```

**Edit** (R12.4) — replace:

```text
sets `tools: Read, Grep, Glob`, `model: sonnet` and `omitClaudeMd: true`.
`check_frontmatter.py`, the dependency-drift test and
```

with:

```text
sets `tools: Read, Grep, Glob`, `model: sonnet` and `omitClaudeMd: true`.
It also checks that the agent defines each verdict R8.5 and R8.7 define,
that both modes rate by the same failure test and item rule, that a files
choice differing from an example's is no failure, and that the agent and the
skill's formats say a files row gives one line number (owner, plan 45,
2026-10-14).
`check_frontmatter.py`, the dependency-drift test and
```

- [x] **Step 7: The term gate (Channel 3)**

The changed arm's added text must name no fixture answer, no term of this plan's context, and nothing a contract rule forbids. Run this single-line command. It reads only the added lines of the uncommitted diff, so the `+++` headers, whose paths hold `cc-guide`, are not searched:

```bash
uv run --no-project --python 3.13 python -I -c 'import re, subprocess; d = subprocess.run(["git", "-C", "/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall", "diff", "--no-color", "-U0", "HEAD", "--", ".claude/agents/cc-guide-verifier.md", ".claude/skills/cc-guide/references/formats.md"], capture_output=True, text=True, check=True).stdout; added = [l[1:] for l in d.splitlines() if l.startswith("+") and not l.startswith("+++")]; pat = re.compile(r"deniedModels|availableModels|effort|session|sonnet|alias|deprecat|CLAUDE_PROJECT_DIR|\bmax\b|\bwrite|\bbash\b|\bedit|\bcat\b|\bhead\b|onFailure|quoting|unquot|test-runner|\bonly\b|\bread\b|\blevel|TODO\(owner\)|cc-guide|\d-\d|\|", re.I); hits = [l for l in added if pat.search(l)]; print(len(added), "added lines,", len(hits), "hits"); print(*hits, sep="\n")'
```

Expected: `22 added lines, 0 hits`. The line count is the positive control: 0 lines means the diff was not read, so the gate did not run. Any hit is a finding: reword the added text and rerun Steps 5 and 7.

- [x] **Step 8: Run the lints**

Run, from `W`:
- `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall --python 3.13 --with pyyaml python build/check_conformance.py`: expect exit 0.
- `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall --python 3.13 python build/cc_guide/cli.py lint`: expect exit 0 and the same `STALE` lines as the ledger's pre-Task-1 snapshot (Global Constraints, "Baseline and counts"). On `2e9ee0f` that is 6 lines, none of them the verifier; a later pass that lands on `main` first may change them, and the snapshot is the reference.
- `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall --python 3.13 --with pyyaml python build/check_frontmatter.py`: expect exit 0.

- [x] **Step 9: Commit**

> Deviation: the owner reverted this commit at plan completion (`8947e50`, 2026-10-15), after the gate FAILed (Task 6 Step 5).

Confirm the branch (`branch --show-current` prints `feat/verifier-recall`), then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall add .claude/agents/cc-guide-verifier.md .claude/skills/cc-guide/references/formats.md build/cc_guide/test_skill_files.py specs/claude-code-drift-automation-spec.md
```

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall commit -m "feat(cc-guide): define the verifier's verdicts by a failure test (plan 45)" -m "A claim is CONFIRMED only when no case its passage gives makes a follower of the guide line wrong; a qualifying omission is that claim's PARTIAL, and B rows re-rate the A rows they change. A line that gives the items for a job fails for each further item. Files rows rate by the same test, never fail a file's own choice for differing from an example, take examples as evidence and give one line number. Amends drift spec R8.1, R8.5, R8.7 and R12.4." -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

The commit hook runs the seven commit lints. Expect `commit lints passed`.

---

### Task 2: The evidence kit (outside the repo)

**Files** (all under `K` = `/Users/lowell/.cache/agent-skills/scratch/plan45`, never committed):
- Create: `K/test_kit.py`
- Create: `K/common.py`, `K/key.py`, `K/build.py`, `K/run.py`, `K/grade.py`

**Interfaces:**
- Consumes: `W/build/cc_guide/settle.py`: `read_packet`, `Packet._replace`, `settle_review`, `settle_files`, `report_lines`, `split_row`, `LINE_REF_RE`, `VERIFY_QUOTES`, `FILES_QUOTES`, `CORRECTIONS`, and `Settled.lines` / `Settled.clean`. They are unchanged since `5bd78a7`.
- Produces: `build.py <batch>`, `build.py spare <rid>`, `run.py <batch>` (which reads `ceiling.txt`), and `grade.py control | <batch> | context <rid> | compare <rid> <transcript> | unblind`. `plan.json` is the rep schedule and the one map from rep id to arm; `results/<rid>.jsonl`, `sheets/<rid>.txt` and `reports/<rid>.md` are their outputs.

`K` holds the scoring key, so no rep may read it. The fence and V2 enforce that. Nothing to commit: the task reviewer reads `K`'s files and the test output.

- [x] **Step 1: Write the failing tests**

Create `K/test_kit.py`:

```python
'''Tests for plan 45's kit, on hand-written records only: no transcript,
packet or docs text is copied in.'''
import json
import random
from types import SimpleNamespace

import pytest

import build
import common
import grade
import run

PROMPT = common.DISPATCH.format(mode='audit', packet='/private/tmp/q7r/r01/20261013T113847-audit')
BODY = 'You check the guide.\n\n## Start\n\nRead index.json.'
AGENT = f'---\nname: cc-guide-verifier\ntools: Read, Grep, Glob\n---\n\n{BODY}\n'
ROOTS = ['/private/tmp/q7r/r01', '/Users/x/docs']
KEEP = SimpleNamespace(shuffle=lambda pair: None)  # an rng that leaves each pair in schedule order


def assistant(*content, model=common.MODEL, effort=common.EFFORT, version=common.TRANSCRIPT_VERSION):
    return {'type': 'assistant', 'effort': effort, 'version': version,
            'message': {'model': model, 'content': list(content)}}


def use(name, uid='t1', **inp):
    return {'type': 'tool_use', 'id': uid, 'name': name, 'input': inp}


def attachment(kind, **fields):
    return {'type': 'attachment', 'attachment': {'type': kind, **fields}}


def result(uid, text, error=False):
    return {'type': 'user', 'message': {'content': [
        {'type': 'tool_result', 'tool_use_id': uid, 'content': text, 'is_error': error}]}}


def clean_sub():
    return [attachment('prompt_snapshot', systemPrompt=[BODY, 'note']),
            attachment('advisor_tool', available=True, model=common.ADVISOR_MODEL),
            attachment('session_context', userEmail='x'),
            assistant(use('Read', file_path='/private/tmp/q7r/r01/20261013T113847-audit/index.json')),
            assistant(use('SubagentHandback', uid='t2', message='L1 | a | CONFIRMED | d.md:1 | "q" | -'))]


def packets_and_arms(tmp_path):
    packets, kit = tmp_path / 'packets', tmp_path / 'kit'
    for rel, *_ in common.PACKET.values():
        (packets / rel).mkdir(parents=True)
        (packets / rel / 'index.json').write_text('{}')
        (packets / rel / 'report.md').write_text('old')
    (kit / 'arms').mkdir(parents=True)
    for arm in build.ARMS:
        (kit / 'arms' / f'{arm}.md').write_text(f'{arm}\n')
    return packets, kit, tmp_path / 'root'


def test_copy_packet_leaves_out_the_original_report_and_settled_json(tmp_path):
    src = tmp_path / 'p'
    src.mkdir()
    for name in ('index.json', 'guide.md', 'report.md', 'settled.json'):
        (src / name).write_text(name)
    assert build.copy_packet(src, tmp_path / 'rep' / 'p') == ['guide.md', 'index.json']
    assert sorted(f.name for f in (tmp_path / 'rep' / 'p').iterdir()) == ['guide.md', 'index.json']


def test_copy_packet_never_overwrites(tmp_path):
    (tmp_path / 'p').mkdir()
    (tmp_path / 'dst').mkdir()
    with pytest.raises(SystemExit, match='built once'):
        build.copy_packet(tmp_path / 'p', tmp_path / 'dst')


def test_agent_body_is_the_text_after_the_frontmatter_stripped():
    assert build.agent_body(AGENT) == BODY


def test_add_reps_numbers_reps_across_batches_and_refuses_a_rebuilt_batch(tmp_path):
    packets, kit, root = packets_and_arms(tmp_path)
    build.add_reps(kit, root, packets, 'pilot', common.SCHEDULE['pilot'], KEEP)
    new = build.add_reps(kit, root, packets, 'gate1', common.SCHEDULE['gate1'], KEEP)
    assert [r['rid'] for r in new] == ['r02', 'r03', 'r04', 'r05']
    assert (root / 'r03' / '.claude' / 'agents' / 'cc-guide-verifier.md').read_text() == 'changed\n'
    assert not (root / 'r03' / '20261013T113847-audit' / 'report.md').exists()
    assert new[0]['dispatch'] == common.DISPATCH.format(mode='audit', packet=root / 'r02' / '20261013T113847-audit')
    with pytest.raises(SystemExit, match='already built'):
        build.add_reps(kit, root, packets, 'gate1', common.SCHEDULE['gate1'], KEEP)


def test_blind_orders_each_pair_at_random_and_keeps_its_arms():
    '''Review finding 6: a fixed schedule told the reader each rep's arm.'''
    pairs = common.SCHEDULE['gate2']
    orders = {tuple(arm for _, arm in build.blind(pairs, random.Random(seed))) for seed in range(20)}
    assert len(orders) > 1
    for order in orders:
        assert all(sorted(order[i:i + 2]) == ['changed', 'control'] for i in range(0, len(order), 2))


def test_a_spare_takes_the_void_reps_packet_and_arm_by_its_id(tmp_path):
    packets, kit, root = packets_and_arms(tmp_path)
    build.add_reps(kit, root, packets, 'gate1', common.SCHEDULE['gate1'], KEEP)
    spare = build.add_spare(kit, root, packets, 'r02')
    assert (spare['rid'], spare['packet'], spare['arm'], spare['replaces']) == ('r05', 'audit', 'changed', 'r02')
    with pytest.raises(SystemExit, match='no such rep'):
        build.add_spare(kit, root, packets, 'r99')


def test_a_third_spare_for_one_packet_and_arm_is_refused_without_naming_the_arm(tmp_path):
    packets, kit, root = packets_and_arms(tmp_path)
    build.add_reps(kit, root, packets, 'gate1', common.SCHEDULE['gate1'], KEEP)
    build.add_spare(kit, root, packets, 'r02')
    build.add_spare(kit, root, packets, 'r05')
    with pytest.raises(SystemExit, match='UNSETTLED') as refused:
        build.add_spare(kit, root, packets, 'r04')
    assert 'changed' not in str(refused.value) and 'control' not in str(refused.value)


def test_each_counted_batch_is_control_and_changed_pairs_of_one_packet():
    for batch in ('cheap', 'gate1', 'gate2'):
        pairs = common.SCHEDULE[batch]
        assert len(pairs) % 2 == 0
        assert all(pairs[i][1] == 'control' and pairs[i + 1][1] == 'changed' and pairs[i][0] == pairs[i + 1][0]
                   for i in range(0, len(pairs), 2))
    audit = common.SCHEDULE['gate1'] + common.SCHEDULE['gate2']
    assert len(audit) == 10 and {p for p, _ in audit} == {'audit'}
    for packet in ('rules', 'readme', 'runner', 'pyrule'):
        assert sorted(arm for p, arm in common.SCHEDULE['cheap'] if p == packet) == ['changed'] * 3 + ['control'] * 3


def test_run_refuses_inside_a_claude_code_shell():
    assert run.inside_claude_code({'CLAUDECODE': '1'})
    assert not run.inside_claude_code({'HOME': '/Users/x'})


def test_the_command_fences_reads_adds_only_the_docs_and_keeps_the_prompt_off_argv():
    rep = {'session': 's', 'cap': 8.0, 'docs': True, 'dispatch': PROMPT}
    argv = run.command(rep)
    assert json.loads(argv[argv.index('--settings') + 1]) == run.FENCE
    assert argv[argv.index('--add-dir') + 1] == str(common.DOCS)
    assert not any('Mode: audit' in a for a in argv)
    assert '--add-dir' not in run.command({**rep, 'docs': False})
    assert '--no-session-persistence' not in argv
    assert argv[0] == str(common.CLAUDE)  # the held 2.1.296 binary; the PATH's claude moved on


def test_the_kit_runs_a_held_2_1_296_binary():
    '''Consistency check finding 33: the PATH's claude moved to 2.1.299, and
    the updater prunes old versions, so the kit runs a copy held outside them.'''
    assert common.CLAUDE.name == common.TRANSCRIPT_VERSION
    assert 'versions' not in common.CLAUDE.parts  # ~/.local/share/claude/versions is pruned


def test_an_unfinished_rep_counts_at_its_full_cap(tmp_path):
    '''Review finding 7: a run that left no result may still have spent.'''
    reps = [{'rid': 'r01', 'cap': 8.0}, {'rid': 'r02', 'cap': 2.0}, {'rid': 'r03', 'cap': 3.0}]
    (tmp_path / 'r01.jsonl').write_text(json.dumps({'type': 'result', 'total_cost_usd': 2.5}) + '\n')
    (tmp_path / 'r02.jsonl').write_text(json.dumps({'type': 'assistant'}) + '\n')
    assert run.spent(tmp_path, reps) == 4.5


def test_reps_start_only_while_their_full_caps_fit_under_the_ceiling():
    '''Review finding 7: $80 spent of $100 must not start six $8 reps.'''
    reps = [{'rid': f'r{i}', 'cap': 8.0} for i in range(6)]
    assert [r['rid'] for r in run.affordable(reps, 80.0, 100.0)] == ['r0', 'r1']
    assert run.affordable(reps, 100.0, 100.0) == []


def test_encode_matches_claude_codes_project_directory_names():
    assert grade.encode('/private/tmp/q7r/r01') == '-private-tmp-q7r-r01'


@pytest.mark.parametrize('path, out', [
    ('20261013T113847-audit/index.json', False),
    ('/private/tmp/q7r/r01/x/guide.md', False),
    ('/tmp/q7r/r01/x/guide.md', False),
    ('/Users/x/docs/memory.md', False),
    ('/private/tmp/q7r/r02/x/report.md', True),
    ('/Users/x/docs-old/memory.md', True),
    ('~/.cache/agent-skills/cc-guide/packets', True),
    ('../r02/x/report.md', True),
    ('x/../../r02/report.md', True),
])
def test_outside_allows_only_the_rep_directory_and_the_docs(path, out):
    '''Review finding 1: a relative path that climbs out is outside.'''
    assert grade.outside(path, ROOTS) is out


def test_outside_follows_a_symlink_out_of_the_rep_directory(tmp_path):
    '''Review finding 1: a link inside the rep directory can point out of it.'''
    rep, secret = tmp_path / 'rep', tmp_path / 'secret'
    rep.mkdir()
    secret.mkdir()
    (secret / 'report.md').write_text('x')
    (rep / 'link').symlink_to(secret)
    assert grade.outside(str(rep / 'link' / 'report.md'), [str(rep)])
    assert grade.outside('link/report.md', [str(rep)])
    assert not grade.outside(str(rep / 'own.md'), [str(rep)])


def test_paths_used_takes_a_glob_patterns_fixed_prefix():
    assert grade.paths_used(use('Glob', pattern='/Users/x/.cache/**/report.md')) == ['/Users/x/.cache/']
    assert grade.paths_used(use('Glob', pattern='../**/report.md')) == ['../']
    assert grade.paths_used(use('Grep', pattern='x', path='/Users/x/docs')) == ['/Users/x/docs']
    assert grade.paths_used(use('Glob', pattern='**/*.md')) == []


def test_the_main_session_makes_one_exact_agent_call():
    ok = [assistant(use('Agent', description='d', subagent_type='cc-guide-verifier', prompt=PROMPT))]
    assert grade.main_violations(ok, PROMPT) == []
    extra = [assistant(use('Agent', subagent_type='cc-guide-verifier', prompt=PROMPT, model='opus'))]
    assert grade.main_violations(extra, PROMPT) == ['V1 Agent parameters: model']
    reworded = [assistant(use('Agent', subagent_type='cc-guide-verifier', prompt=PROMPT + ' Be thorough.'))]
    assert grade.main_violations(reworded, PROMPT) == ['V1 the dispatch prompt differs']
    second = ok + [assistant(use('Read', uid='t9', file_path='/x'))]
    assert grade.main_violations(second, PROMPT) == ['V1 main tool call: Read']


def test_a_clean_verifier_transcript_has_no_violation():
    assert grade.sub_violations(clean_sub(), BODY, ROOTS) == []


def test_each_verifier_violation_is_named():
    sub = clean_sub() + [attachment('instructions', content='x'),
                         attachment('session_context', content='gitStatus: main'),
                         assistant(use('Glob', uid='g1', pattern='*.md', path='/private/tmp/q7r/r01')),
                         result('g1', '/private/tmp/q7r/r02/x/report.md\n/private/tmp/q7r/r01/x/guide.md'),
                         assistant(use('Read', uid='t3', file_path='/Users/x/.cache/packets/report.md'), model='m')]
    assert grade.sub_violations(sub, BODY + ' changed', ROOTS) == [
        'V2 outside: Read /Users/x/.cache/packets/report.md',
        'V2 listed outside: /private/tmp/q7r/r02/x/report.md',
        'V4 instructions attachment', 'V4 gitStatus', "V5 the system prompt is not the arm's contract",
        f"V7 model, effort, version: ('m', '{common.EFFORT}', '{common.TRANSCRIPT_VERSION}')"]


def test_a_listed_relative_path_that_climbs_out_is_void():
    '''Review finding 1: search results can list relative paths too.'''
    sub = clean_sub() + [assistant(use('Grep', uid='g2', pattern='x')),
                         result('g2', '../r02/x/report.md:3:hit\nx/guide.md:1:hit')]
    assert grade.sub_violations(sub, BODY, ROOTS) == ['V2 listed outside: ../r02/x/report.md']


def test_every_prompt_snapshot_must_open_with_the_arms_contract():
    '''Review finding 2: a second snapshot was never checked.'''
    sub = clean_sub() + [attachment('prompt_snapshot', systemPrompt=[BODY + ' and more'])]
    assert grade.sub_violations(sub, BODY, ROOTS) == ["V5 the system prompt is not the arm's contract"]


@pytest.mark.parametrize('advisor', [
    [attachment('advisor_tool', available=True, model='claude-haiku-5-5')],
    [attachment('advisor_tool', available=True, model=common.ADVISOR_MODEL),
     attachment('advisor_tool', available=False, model=common.ADVISOR_MODEL)],
    [],
])
def test_the_advisor_must_be_opus_and_available_throughout(advisor):
    '''Review finding 11: availability alone did not pin the advisor.'''
    sub = [r for r in clean_sub() if r.get('attachment', {}).get('type') != 'advisor_tool'] + advisor
    assert grade.sub_violations(sub, BODY, ROOTS) == ['V8 the advisor was not Opus 5.5 throughout']


def test_injected_hits_screen_all_but_the_contract_body_and_name_where_each_marker_sits():
    '''Review finding 2: answer text in a later prompt part was skipped.'''
    records = [attachment('prompt_snapshot', systemPrompt=['deniedModels', 'note: deniedModels']),
               attachment('session_context', text='deniedModels'), {'type': 'system', 'content': 'plan45'}]
    assert grade.injected_hits(records, ('deniedModels', 'plan45')) == [
        'attachment prompt_snapshot: deniedModels', 'attachment session_context: deniedModels', 'system: plan45']
    assert grade.injected_hits([attachment('prompt_snapshot', systemPrompt=['deniedModels'])], ('deniedModels',)) == []


def test_context_lines_show_everything_injected_but_the_contract_body():
    records = [attachment('prompt_snapshot', systemPrompt=[BODY, 'env: x']), attachment('date', value='d'),
               assistant({'type': 'text', 'text': 'work'})]
    lines = grade.context_lines(records)
    assert lines == ['prompt_snapshot part 0: <the arm contract>', "prompt_snapshot part 1: 'env: x'",
                     'attachment date: {"type": "date", "value": "d"}']


def test_the_report_is_a_handback_or_a_finished_agent_result_never_progress_text():
    '''Review finding 9: a verifier's last progress line was graded as its report.'''
    assert grade.report_of(clean_sub()) == 'L1 | a | CONFIRMED | d.md:1 | "q" | -'
    progress = [assistant({'type': 'text', 'text': 'I will inspect the source next'})]
    call = assistant(use('Agent', uid='a1', subagent_type='cc-guide-verifier', prompt=PROMPT))
    assert grade.report_of(progress, [call, result('a1', 'Async agent launched successfully.')]) is None
    assert grade.report_of(progress, [call, result('a1', 'C | omission', error=True)]) is None
    assert grade.report_of(progress, [call, result('a1', 'C | omission')]) == 'C | omission'
    assert grade.report_of([]) is None


def test_a_budget_stop_an_error_or_a_failed_subagent_is_void():
    assert grade.result_violations({'type': 'result', 'is_error': False}) == []
    assert grade.result_violations({'type': 'result', 'is_error': True, 'terminal_reason': 'max_budget'}) == [
        'V6 is_error', 'V6 budget stop']
    failed = {'type': 'result', 'is_error': False,
              'subagent_stats': {'failed': 1, 'killed': {'parent': 0}, 'refused': {'budget': 0}}}
    assert grade.result_violations(failed) == ['V6 a subagent failed or was killed']
    killed = {'type': 'result', 'is_error': False, 'subagent_stats': {'failed': 0, 'killed': {'system': 1}}}
    assert grade.result_violations(killed) == ['V6 a subagent failed or was killed']
    assert grade.result_violations(None) == ['V6 no result record']


def test_hold_lines_give_settles_hold_reason_and_each_unparseable_row():
    '''Consistency check finding 40: True or False could not tell a parse hold from another.'''
    settled = ['report: 1 consistent', 'unverified, discarded:', '  unparseable: agents/t.md:14-16 | s',
               '  quote not found, discarded: agents/t.md:3 | s', 'held, not cited: agents/t.md: a discarded row']
    assert grade.hold_lines(settled) == ['held, not cited: agents/t.md: a discarded row',
                                         'unparseable: agents/t.md:14-16 | s']
    assert grade.hold_lines(['report: 1 consistent']) == ['held, not cited: no']


def test_fate_reads_settles_discard_lines():
    settled = ['unverified, discarded:', '  quote not found, discarded: L5 | a | PARTIAL | d.md:1 | "q" | w']
    assert grade.fate('L5 | a | PARTIAL | d.md:1 | "q" | w', settled) == 'quote not found'
    assert grade.fate('L6 | b | CONFIRMED | d.md:2 | "q" | -', settled) == 'kept'


def test_rows_types_each_line_and_counts_a_range_as_a_files_row():
    table = grade.rows('L5 | a | partial | d.md:1 | "q" | w\nC | gap\nB | 2.1.1 | x | changelog.md:3\n'
                       'agents/t.md:14-16 | s | sec | - | not covered')
    assert [(r['kind'], r['n'], r['verdict']) for r in table] == [
        ('A', 5, 'PARTIAL'), ('C', 0, ''), ('B', 0, ''), ('F', 0, '')]


def test_a_refused_outside_call_is_logged_not_void():
    sub = clean_sub() + [assistant(use('Read', uid='t5', file_path='/Users/x/.cache/packets/report.md')),
                         result('t5', 'denied', error=True)]
    assert grade.sub_violations(sub, BODY, ROOTS) == []
    assert grade.outside_calls(sub, ROOTS) == ([], ['Read /Users/x/.cache/packets/report.md'])


def test_audit_rep_finds_the_verifiers_transcript_by_its_agent_type(tmp_path):
    kit, projects = tmp_path / 'kit', tmp_path / 'projects'
    rep = {'rid': 'r01', 'cwd': '/private/tmp/q7r/r01', 'session': 's1', 'arm': 'control', 'docs': True,
           'dispatch': PROMPT}
    (kit / 'arms').mkdir(parents=True)
    (kit / 'arms' / 'control.md').write_text(AGENT)
    (kit / 'results').mkdir()
    (kit / 'results' / 'r01.jsonl').write_text(json.dumps({'type': 'result', 'is_error': False}) + '\n')
    base = projects / '-private-tmp-q7r-r01'
    (base / 's1' / 'subagents').mkdir(parents=True)
    main = [assistant(use('Agent', description='d', subagent_type='cc-guide-verifier', prompt=PROMPT))]
    (base / 's1.jsonl').write_text('\n'.join(json.dumps(r) for r in main))
    for name, kind, records in (('agent-a', 'general-purpose', []), ('agent-b', 'cc-guide-verifier', clean_sub())):
        (base / 's1' / 'subagents' / f'{name}.meta.json').write_text(json.dumps({'agentType': kind}))
        (base / 's1' / 'subagents' / f'{name}.jsonl').write_text('\n'.join(json.dumps(r) for r in records))
    audited = grade.audit_rep(rep, kit, projects)
    assert audited['void'] == []
    assert audited['report'] == 'L1 | a | CONFIRMED | d.md:1 | "q" | -'


def test_compare_lines_name_what_differs_from_production_part_by_part():
    '''Review finding 2: zip() hid a production prompt part the rep lacked.'''
    prod = [attachment('prompt_snapshot', systemPrompt=[BODY, 'note', 'extra'])] + clean_sub()[1:]
    rep = [r for r in clean_sub() if r.get('attachment', {}).get('type') != 'session_context']
    lines = grade.compare_lines(rep, prod)
    assert lines[0] == 'attachment types only in the rep: none'
    assert lines[1] == "attachment types only in production: ['session_context']"
    assert lines[2] == 'system prompt parts, rep and production: 2 3; equal by index: [True, True, False]'
    assert lines[3] == f"settings, rep and production: ('{common.MODEL}', '{common.EFFORT}', '{common.TRANSCRIPT_VERSION}') " \
                       f"('{common.MODEL}', '{common.EFFORT}', '{common.TRANSCRIPT_VERSION}')"
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 --with pytest python -B -m pytest -q -p no:cacheprovider`

Expected: one collection error, `ModuleNotFoundError: No module named 'build'`.

- [x] **Step 3: Write `K/common.py`**

```python
'''Paths, packets, prompts and the rep schedule shared by plan 45's kit
(build.py, run.py, grade.py). Every path is literal: the plan's
Pre-registration fixes them.'''
from pathlib import Path

KIT = Path('/Users/lowell/.cache/agent-skills/scratch/plan45')
ROOT = Path('/private/tmp/q7r')  # the rep directories; never /tmp itself, never a checkout
PACKETS = Path('/Users/lowell/.cache/agent-skills/cc-guide/packets')
DOCS = Path('/Users/lowell/.cache/agent-skills/cc-guide/2.1.296/docs')
CC_GUIDE = Path('/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall/build/cc_guide')
PROJECTS = Path.home() / '.claude' / 'projects'
# Production ran 2.1.296. The PATH's claude moved to 2.1.299 on 2026-10-13, and the updater prunes old versions,
# so the kit runs a copy of versions/2.1.296 held here (Task 3, Step 3 checks its hash).
CLAUDE = Path('/Users/lowell/.cache/agent-skills/scratch/plan45-bin/2.1.296')
VERSION = '2.1.296 (Claude Code)'
TRANSCRIPT_VERSION = '2.1.296'
MODEL = 'claude-sonnet-5-5'
EFFORT = 'xhigh'
ADVISOR_MODEL = 'claude-opus-5-5'

# key: (packet directory under PACKETS, mode, budget cap in USD, timeout in s, reads the docs snapshot)
PACKET = {
    'audit': ('20261013T113847-audit', 'audit', 8.0, 2400, True),
    'rules': ('20261013T175307-verify/rules', 'verify', 3.0, 900, True),
    'readme': ('20261013T121854-files/hooks__README.md', 'files', 2.0, 600, False),
    'runner': ('20261013T124015-files/agents__test-runner.md', 'files', 2.0, 600, False),
    'pyrule': ('20261013T205255-files/rules__clean-code-python.md', 'files', 2.0, 600, False),
}

# .claude/skills/cc-guide/SKILL.md, "Dispatch, save, settle" step 1, verbatim.
DISPATCH = ('Mode: {mode}. Packet: {packet}. Read its index.json first, then follow your contract '
            'and return only the report.')
MAIN = ('Call the Agent tool exactly once, with subagent_type cc-guide-verifier, no model or effort '
        'parameter, and exactly this prompt:\n\n{dispatch}\n\nMake no other tool call. When the agent '
        'has returned, reply with the single word DONE.')

# Each batch's reps as (control, changed) pairs of one packet. build.py puts
# each pair's two arms in a random order, so a rep id names no arm. The probe
# and the pilot are single reps whose arm is known, and they count toward no
# result. Rep ids run r01, r02, ... across batches in build order.
SCHEDULE = {
    'probe': [('rules', 'probe')],
    'pilot': [('rules', 'control')],
    'cheap': [(packet, arm) for packet in ('rules', 'readme', 'runner', 'pyrule') for _ in range(3)
              for arm in ('control', 'changed')],
    'gate1': [('audit', arm) for _ in range(2) for arm in ('control', 'changed')],
    'gate2': [('audit', arm) for _ in range(3) for arm in ('control', 'changed')],
}
CONCURRENCY = {'probe': 1, 'pilot': 1, 'cheap': 4, 'gate1': 2, 'gate2': 2, 'spare': 1}

# Injected-context markers (VOID rule V3): a fixture answer, or a name of this
# plan's own context. A hit is traced by hand; a path or a tool name is not content.
MARKERS = ('deniedModels', 'Sonnet 4.5', 'effortLevel', 'CLAUDE_PROJECT_DIR', 'counts as a read',
           'deferred_items', 'specs/plans', '45-claude-code', 'verifier-recall', 'cc-guide-refresh', 'plan45')
```

- [x] **Step 4: Write `K/key.py`**

```python
'''Plan 45's scoring key: the known positives in each packet, by claim, as
patterns a row's text must all match. The patterns only pre-screen: every
candidate row, and every surviving correction no positive matches, is read
by hand, and the hand verdict stands.

Guide lines are the packet's own numbering (the audit packet's guide.md is
5bd78a7's guide). Labels follow the Planning record's ground-truth table.'''
from typing import NamedTuple


class Positive(NamedTuple):
    label: str
    kinds: tuple[str, ...]  # row kinds the sheet shows it on: A (a correction), C, B, F (a files row)
    lines: tuple[int, int]  # the guide (A) or file (F) lines it may sit on; C and B rows ignore it
    patterns: tuple[str, ...]  # regexes, case-sensitive, that the row's text must all match
    role: str  # gate, secondary, retention, check, or negative: a statement that must stay unflagged


KEY = {
    'audit': [
        Positive('P11 deniedModels', ('A', 'C', 'B'), (415, 442), (r'deniedModels',), 'gate'),
        Positive('P7 max lasts one session', ('A', 'C', 'B'), (415, 442), (r'\bmax\b', r'session'), 'secondary'),
        Positive('P8 top-level effortLevel', ('A', 'C', 'B'), (415, 442), (r'effortLevel',), 'secondary'),
        Positive('P10 Sonnet 4.5 behind the alias', ('A', 'C'), (415, 442), (r'Sonnet 4\.5',), 'secondary'),
        Positive('P12 enforceAvailableModels in any file', ('A', 'C'), (415, 442),
                 (r'enforceAvailableModels', r'any (settings )?file|project|user settings|local'), 'secondary'),
        Positive('P1 Haiku 4.5 retirement dates', ('A', 'C'), (208, 219),
                 (r'[Rr]etire', r'sooner|Anthropic-operated|Bedrock|Google Cloud'), 'retention'),
        Positive('P2 Explore under a Fable session', ('A', 'C'), (208, 219), (r'Explore', r'Fable'), 'retention'),
        Positive('P3 FORCE reach', ('A', 'C'), (208, 219), (r'FORCE', r'fork|inherit|teammate|workflow'), 'retention'),
        Positive('P4 helper requests get the hour', ('A', 'C'), (402, 414), (r'helper',), 'retention'),
        Positive('P5 /compact rebuilds by design', ('A', 'C'), (402, 414), (r'compact', r'invalidat|rebuild|break'),
                 'retention'),
        Positive('P6 effort-change cache caveat', ('A', 'C'), (402, 442),
                 (r'Bedrock|Agent Platform|gateway|HIPAA|DISABLE_EXPERIMENTAL_BETAS',), 'retention'),
        Positive('P9 ANTHROPIC_DEFAULT_MODEL', ('A', 'C'), (415, 442), (r'ANTHROPIC_DEFAULT_MODEL',), 'retention'),
        Positive('P13 tokenizer comparison', ('A', 'C'), (402, 442), (r'tokeniz|overstat|understat',), 'retention'),
        Positive('P14 CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL', ('B', 'C', 'A'), (208, 442),
                 (r'CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL',), 'retention'),
    ],
    'rules': [
        Positive('D1 load trigger names Write and the Bash read', ('A',), (246, 255),
                 (r'Write|Bash|cat|head',), 'check'),
    ],
    'readme': [
        Positive('B1 unquoted $CLAUDE_PROJECT_DIR', ('F',), (55, 66), (r'CLAUDE_PROJECT_DIR',), 'check'),
        Positive('B2 onFailure exit-code note', ('F',), (95, 101), (r'onFailure',), 'retention'),
        Positive('N1 the Bash matcher, the file\'s own choice (L56)', ('F',), (55, 57), (r'[Mm]atcher',), 'negative'),
        Positive('N2 the Bash matcher, the file\'s own choice (L129)', ('F',), (128, 130), (r'[Mm]atcher',),
                 'negative'),
    ],
    'runner': [  # (c): the statement the original rated on a line range must now get a one-line row
        Positive('R1 the read-only contract statement, on one line', ('F',), (14, 16), (r'.',), 'check'),
    ],
    'pyrule': [
        Positive('E1 load trigger leaves out cases', ('F',), (6, 10), (r'[Ww]rit|Bash|cat|head',), 'check'),
    ],
}
```

- [x] **Step 5: Write `K/build.py`**

```python
'''Build plan 45's rep directories: build.py <batch>, or build.py spare <rid>
for one replacement of void rep <rid>, under Python 3.13.

Each rep directory holds the arm's verifier at
.claude/agents/cc-guide-verifier.md and a copy of its packet, less the
original report.md and settled.json, at the packet's own relative path.
plan.json records every rep, and it is the one file that maps a rep id to
its arm: run.py and grade.py read it, the reader does not until unblinding.
A rep directory is built once and never overwritten.'''
import json
import random
import shutil
import sys
import uuid
from pathlib import Path

import common

SKIP = {'report.md', 'settled.json'}
ARMS = ('control', 'changed', 'probe')
MAX_SPARES = 2  # per packet and arm (Pre-registration, "Replacement")


def copy_packet(src: Path, dst: Path) -> list[str]:
    '''Copy a packet's files, less SKIP, into a new directory.'''
    if dst.exists():
        raise SystemExit(f'{dst}: exists; a rep directory is built once')
    names = sorted(f.name for f in src.iterdir())
    if any((src / n).is_dir() for n in names):
        raise SystemExit(f'{src}: holds a directory; a packet copy takes files only')
    dst.mkdir(parents=True)
    kept = [n for n in names if n not in SKIP]
    for n in kept:
        shutil.copy2(src / n, dst / n)
    return kept


def agent_body(text: str) -> str:
    '''An agent file's body, after its frontmatter, as Claude Code's
    prompt_snapshot carries it: stripped.'''
    lines = text.split('\n')
    end = lines.index('---', 1)
    return '\n'.join(lines[end + 1:]).strip()


def plan_rep(rid: str, batch: str, packet: str, arm: str, root: Path) -> dict:
    rel, mode, cap, timeout, docs = common.PACKET[packet]
    cwd = root / rid
    folder = cwd / rel
    return {'rid': rid, 'batch': batch, 'packet': packet, 'arm': arm, 'mode': mode, 'cap': cap,
            'timeout': timeout, 'docs': docs, 'session': str(uuid.uuid4()), 'cwd': str(cwd),
            'folder': str(folder), 'dispatch': common.DISPATCH.format(mode=mode, packet=folder)}


def build_rep(rep: dict, arms: Path, packets: Path) -> None:
    copy_packet(packets / common.PACKET[rep['packet']][0], Path(rep['folder']))
    agents = Path(rep['cwd']) / '.claude' / 'agents'
    agents.mkdir(parents=True)
    shutil.copy2(arms / f"{rep['arm']}.md", agents / 'cc-guide-verifier.md')


def load_plan(kit: Path) -> dict:
    path = kit / 'plan.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'reps': []}


def blind(pairs: list[tuple[str, str]], rng) -> list[tuple[str, str]]:
    '''The batch's reps in run order, each consecutive pair's two arms put in
    a random order, so neither a rep id nor the schedule names an arm.'''
    out = []
    for i in range(0, len(pairs), 2):
        two = list(pairs[i:i + 2])
        rng.shuffle(two)
        out += two
    return out


def add_reps(kit: Path, root: Path, packets: Path, batch: str, pairs: list[tuple[str, str]], rng=None,
             replaces: str | None = None) -> list[dict]:
    '''Plan and build reps for pairs of (packet, arm), blinded, appending them
    to plan.json. Rep ids continue from the plan's last one.'''
    plan = load_plan(kit)
    if batch != 'spare' and any(r['batch'] == batch for r in plan['reps']):
        raise SystemExit(f'batch {batch}: already built')
    new = []
    for packet, arm in blind(pairs, rng or random.SystemRandom()):
        if packet not in common.PACKET or arm not in ARMS:
            raise SystemExit(f'{packet} {arm}: not a packet and arm of this plan')
        rep = plan_rep(f'r{len(plan["reps"]) + 1:02d}', batch, packet, arm, root)
        if replaces:
            rep['replaces'] = replaces
        build_rep(rep, kit / 'arms', packets)
        plan['reps'].append(rep)
        new.append(rep)
    (kit / 'plan.json').write_text(json.dumps(plan, indent=1) + '\n', encoding='utf-8')
    return new


def add_spare(kit: Path, root: Path, packets: Path, rid: str) -> dict:
    '''One replacement for void rep rid, with its packet and arm, which the
    caller never needs to see. A packet and arm get at most MAX_SPARES.'''
    reps = load_plan(kit)['reps']
    old = next((r for r in reps if r['rid'] == rid), None)
    if old is None:
        raise SystemExit(f'{rid}: no such rep')
    used = sum(1 for r in reps if r['batch'] == 'spare' and (r['packet'], r['arm']) == (old['packet'], old['arm']))
    if used >= MAX_SPARES:
        raise SystemExit(f'{rid}: its packet and arm have had {MAX_SPARES} spares, so that result is UNSETTLED')
    return add_reps(kit, root, packets, 'spare', [(old['packet'], old['arm'])], replaces=rid)[0]


def main(argv: list[str]) -> None:
    if argv[:1] == ['spare'] and len(argv) == 2:
        new = [add_spare(common.KIT, common.ROOT, common.PACKETS, argv[1])]
    elif len(argv) == 1 and argv[0] in common.SCHEDULE:
        new = add_reps(common.KIT, common.ROOT, common.PACKETS, argv[0], common.SCHEDULE[argv[0]])
    else:
        raise SystemExit(f'usage: build.py <{"|".join(common.SCHEDULE)}> | build.py spare <rid>')
    for rep in new:
        print(f"{rep['rid']} {rep['packet']} built")  # the arm stays in plan.json


if __name__ == '__main__':
    main(sys.argv[1:])
```

- [x] **Step 6: Write `K/run.py`**

```python
'''Run one batch of plan 45's reps: run.py <batch>, under Python 3.13, from a plain
terminal, never from a Claude Code session.

Each rep is one `claude -p` session started in its own directory, with the
prompt on stdin; its stream-json goes to results/<rid>.jsonl. A rep that
already has a result file is kept, never re-run. A rep starts only when its
full budget cap still fits under the ceiling the owner approved
(ceiling.txt), counting every earlier rep at its cost, or at its cap when it
left no result. Prints each rep as it finishes, then the total.'''
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import common

# Set in every Claude Code shell; a plain terminal has none of them.
CLAUDE_CODE_ENV = ('CLAUDECODE', 'CLAUDE_CODE_ENTRYPOINT', 'CLAUDE_CODE_SESSION_ID')
FENCE = {'permissions': {'blockReadsOutsideWorkingDirectories': True}}


def inside_claude_code(env) -> bool:
    return any(name in env for name in CLAUDE_CODE_ENV)


def command(rep: dict) -> list[str]:
    '''The rep's argv. The prompt goes on stdin, so no variadic flag
    (--add-dir) can swallow it.'''
    argv = [str(common.CLAUDE), '-p', '--model', 'sonnet', '--permission-mode', 'auto', '--permission-prompts', 'none',
            '--settings', json.dumps(FENCE), '--session-id', rep['session'],
            '--output-format', 'stream-json', '--verbose', '--max-budget-usd', str(rep['cap'])]
    if rep['docs']:
        argv += ['--add-dir', str(common.DOCS)]
    return argv


def result_line(path: Path) -> dict | None:
    '''The stream's final result record, if the rep finished.'''
    if not path.exists():
        return None
    for line in reversed(path.read_text(encoding='utf-8').splitlines()):
        if line.strip():
            record = json.loads(line)
            return record if record.get('type') == 'result' else None
    return None


def run_rep(rep: dict, results: Path) -> str:
    out, err = results / f"{rep['rid']}.jsonl", results / f"{rep['rid']}.err"
    if out.exists():
        return f"{rep['rid']} kept"
    prompt = common.MAIN.format(dispatch=rep['dispatch'])
    with out.open('w', encoding='utf-8') as o, err.open('w', encoding='utf-8') as e:
        try:
            code = subprocess.run(command(rep), cwd=rep['cwd'], input=prompt, text=True, stdout=o, stderr=e,
                                  timeout=rep['timeout']).returncode
        except subprocess.TimeoutExpired:
            code = 'timeout'
    result = result_line(out) or {}
    return f"{rep['rid']} exit {code} cost {result.get('total_cost_usd', 'none')}"


def spent(results: Path, reps: list[dict]) -> float:
    '''What the reps have cost so far: a finished rep's total_cost_usd, and
    an unfinished one's full cap, since a run that left no result may still
    have spent it.'''
    total = 0.0
    for rep in reps:
        path = results / f"{rep['rid']}.jsonl"
        if path.exists():
            result = result_line(path)
            total += result.get('total_cost_usd', rep['cap']) if result else rep['cap']
    return total


def affordable(reps: list[dict], so_far: float, ceiling: float) -> list[dict]:
    '''The reps, in order, that fit under the ceiling when each reserves its
    full cap before it starts. The first that does not fit holds it and every
    rep after it, so reps still run in their blinded order.'''
    out, total = [], so_far
    for rep in reps:
        if total + rep['cap'] > ceiling:
            break
        out.append(rep)
        total += rep['cap']
    return out


def main(argv: list[str]) -> None:
    if inside_claude_code(os.environ):
        raise SystemExit('run.py: launched from a Claude Code session; run it from a plain terminal')
    if len(argv) != 1 or argv[0] not in common.CONCURRENCY:
        raise SystemExit(f'usage: run.py <{"|".join(common.CONCURRENCY)}>')
    ceiling_file = common.KIT / 'ceiling.txt'
    if not ceiling_file.exists():
        raise SystemExit('run.py: no ceiling.txt; the owner approves the spend first')
    ceiling = float(ceiling_file.read_text(encoding='utf-8').strip())
    version = subprocess.run([str(common.CLAUDE), '--version'], capture_output=True, text=True).stdout.strip()
    if version != common.VERSION:
        raise SystemExit(f'run.py: claude --version is {version!r}, not {common.VERSION!r}')
    plan = json.loads((common.KIT / 'plan.json').read_text(encoding='utf-8'))
    reps = [r for r in plan['reps'] if r['batch'] == argv[0]]
    if not reps:
        raise SystemExit(f'batch {argv[0]}: not built; run build.py first')
    results = common.KIT / 'results'
    results.mkdir(exist_ok=True)
    todo = [r for r in reps if not (results / f"{r['rid']}.jsonl").exists()]
    go = affordable(todo, spent(results, plan['reps']), ceiling)
    for rep in todo[len(go):]:
        print(f"{rep['rid']} held: with the reps before it, the batch's caps would pass the ${ceiling:.2f} ceiling",
              flush=True)
    with ThreadPoolExecutor(max_workers=common.CONCURRENCY[argv[0]]) as pool:
        for done in as_completed([pool.submit(run_rep, r, results) for r in go]):
            print(done.result(), flush=True)
    print(f'total so far: ${spent(results, plan["reps"]):.2f} of ${ceiling:.2f}')


if __name__ == '__main__':
    main(sys.argv[1:])
```

- [x] **Step 7: Write `K/grade.py`**

```python
'''Grade plan 45's reps: grade.py control | <batch> | context <rid> |
compare <rid> <transcript> | unblind.

For each rep with a result, audit its transcripts against the
Pre-registration's VOID rules, take the verifier's report from its
SubagentHandback, and score it with settle against the original packet, in
memory: no packet is written. Each rep's sheet (sheets/<rid>.txt, naming no
arm) lists the candidate rows for the hand reading; RESULTS.md records the
hand verdicts. `unblind` prints the arms, once every verdict is recorded.
`control` re-scores each packet's original report, the positive control;
`context` prints everything injected into a rep's verifier but its contract,
for the hand reading of V3; and `compare` sets a rep's verifier transcript
beside production's.'''
import json
import os
import re
import sys
from itertools import zip_longest
from pathlib import Path

import common
import key
from build import agent_body
from run import result_line

sys.dont_write_bytecode = True
sys.path.insert(0, str(common.CC_GUIDE))
import settle  # noqa: E402

ALLOWED_AGENT_KEYS = {'description', 'subagent_type', 'prompt'}
LAUNCH_NOTICE = 'Async agent launched'  # a background Agent call's result, not the verifier's answer
DISCARDS = ('unparseable: ', 'quote not found, discarded: ', 'no proposed wording, discarded: ')
RANGE_RE = re.compile(r':\d+\s*[-–]\s*\d+')
CONTROL = {  # each packet's original report as settle scores it, observed while the plan was written
    'audit': "report: 89 confirmed, 8 correction(s), 17 owner's call, 0 unverified",
    'rules': "report: 12 confirmed, 1 correction(s), 3 owner's call, 0 unverified",
    'readme': 'report: 19 consistent, 1 contradiction(s), 5 not covered, 0 unverified',
    'runner': 'report: 7 consistent, 1 contradiction(s), 0 not covered, 1 unverified',
    'pyrule': 'report: 5 consistent, 0 contradiction(s), 0 not covered, 0 unverified',
}


def encode(cwd: str) -> str:
    '''Claude Code's project directory name for a working directory.'''
    return re.sub(r'[^A-Za-z0-9]', '-', cwd)


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def tool_uses(records: list[dict]) -> list[dict]:
    return [c for r in records if r.get('type') == 'assistant'
            for c in (r.get('message', {}).get('content') or []) if isinstance(c, dict) and c.get('type') == 'tool_use']


def tool_results(records: list[dict]) -> dict[str, tuple[str, bool]]:
    '''Each tool result's text and whether it is an error (a refusal is
    one), by tool_use_id.'''
    out = {}
    for r in records:
        content = r.get('message', {}).get('content') if r.get('type') == 'user' else None
        for c in content if isinstance(content, list) else []:
            if isinstance(c, dict) and c.get('type') == 'tool_result':
                body = c.get('content')
                if isinstance(body, list):
                    body = '\n'.join(b.get('text', '') for b in body if isinstance(b, dict))
                out[c.get('tool_use_id', '')] = (body or '', bool(c.get('is_error')))
    return out


def normal(path: str, cwd: str) -> str:
    '''A tool path as the fence sees it: `~` expanded, a relative path taken
    from the rep directory, and every symlink (`/tmp` among them) resolved.'''
    return os.path.realpath(os.path.join(cwd, os.path.expanduser(path)))


def outside(path: str, allowed: list[str]) -> bool:
    '''Whether a tool path falls outside every allowed root. allowed[0] is the
    rep directory, which a relative path is taken from.'''
    if not path:
        return False
    p = normal(path, allowed[0])
    roots = [normal(a, allowed[0]) for a in allowed]
    return not any(p == a or p.startswith(a + '/') for a in roots)


def paths_used(use: dict) -> list[str]:
    '''The paths a Read, Grep or Glob call names, the fixed prefix of a Glob
    pattern that starts outside the working directory included.'''
    inp = use.get('input', {})
    if use.get('name') == 'Read':
        return [inp.get('file_path', '')]
    if use.get('name') not in ('Grep', 'Glob'):
        return []
    out = [inp['path']] if inp.get('path') else []
    pattern = inp.get('pattern', '')
    if use['name'] == 'Glob' and pattern.startswith(('/', '~', '..')):
        out.append(re.split(r'[*?\[{]', pattern)[0])
    return out


def listed_paths(uses: list[dict], results: dict[str, tuple[str, bool]]) -> list[str]:
    '''The paths Grep and Glob results list that could leave the working
    directory: each line, up to a Grep line's first colon, that starts with
    `/`, `~` or `..`.'''
    out = []
    for u in uses:
        if u.get('name') in ('Grep', 'Glob'):
            for line in results.get(u.get('id', ''), ('', False))[0].splitlines():
                token = line.split(':', 1)[0]
                if token.startswith(('/', '~', '..')):
                    out.append(token)
    return out


def outside_calls(records: list[dict], allowed: list[str]) -> tuple[list[str], list[str]]:
    '''V2: the calls naming a path outside the allowed roots, split into
    those that returned (VOID) and those refused (logged only).'''
    results = tool_results(records)
    returned, refused = [], []
    for use in tool_uses(records):
        for p in paths_used(use):
            if outside(p, allowed):
                error = results.get(use.get('id', ''), ('', False))[1]
                (refused if error else returned).append(f'{use.get("name")} {p}')
    return returned, refused


def main_violations(records: list[dict], prompt: str) -> list[str]:
    '''V1: the main session makes exactly one Agent call, with the exact
    dispatch prompt and no other parameter, and no other tool call.'''
    uses = tool_uses(records)
    agents = [u for u in uses if u.get('name') == 'Agent']
    out = [f'V1 main tool call: {u.get("name")}' for u in uses if u.get('name') != 'Agent']
    if len(agents) != 1:
        out.append(f'V1 {len(agents)} Agent calls')
    for u in agents:
        inp = u.get('input', {})
        if inp.get('subagent_type') != 'cc-guide-verifier':
            out.append(f'V1 subagent_type {inp.get("subagent_type")!r}')
        if inp.get('prompt') != prompt:
            out.append('V1 the dispatch prompt differs')
        extra = sorted(set(inp) - ALLOWED_AGENT_KEYS)
        if extra:
            out.append(f'V1 Agent parameters: {", ".join(extra)}')
    return out


def attachments(records: list[dict], kind: str) -> list[dict]:
    return [r['attachment'] for r in records if r.get('type') == 'attachment'
            and isinstance(r.get('attachment'), dict) and r['attachment'].get('type') == kind]


def injected_hits(records: list[dict], markers: tuple[str, ...]) -> list[str]:
    '''V3's pre-screen: each marker in an attachment or a system record. A
    prompt_snapshot is screened whole but for its first system-prompt part,
    which V5 checks is the arm's contract. Every hit is traced by hand.'''
    hits = []
    for r in records:
        if r.get('type') == 'attachment':
            att = r.get('attachment') or {}
            if att.get('type') == 'prompt_snapshot':
                att = att | {'systemPrompt': (att.get('systemPrompt') or [])[1:]}
            where, text = f'attachment {att.get("type")}', json.dumps(att)
        elif r.get('type') == 'system':
            where, text = 'system', json.dumps(r)
        else:
            continue
        hits += [f'{where}: {m}' for m in markers if m in text]
    return sorted(set(hits))


def context_lines(records: list[dict]) -> list[str]:
    '''Everything injected into a verifier but its contract, for the hand
    reading of V3: each prompt_snapshot part after the first, each other
    attachment and each system record.'''
    out = []
    for r in records:
        att = r.get('attachment') or {}
        if r.get('type') == 'attachment' and att.get('type') == 'prompt_snapshot':
            parts = att.get('systemPrompt') or []
            out += ['prompt_snapshot part 0: <the arm contract>'] if parts else []
            out += [f'prompt_snapshot part {i}: {part!r}' for i, part in enumerate(parts[1:], 1)]
        elif r.get('type') == 'attachment':
            out.append(f'attachment {att.get("type")}: {json.dumps(att)}')
        elif r.get('type') == 'system':
            out.append(f'system: {json.dumps(r)}')
    return out


def sub_violations(records: list[dict], body: str, allowed: list[str]) -> list[str]:
    '''V2, V4, V5, V7 and V8 on the verifier's own transcript.'''
    out = [f'V2 outside: {call}' for call in outside_calls(records, allowed)[0]]
    out += [f'V2 listed outside: {p}' for p in listed_paths(tool_uses(records), tool_results(records))
            if outside(p, allowed)]
    if attachments(records, 'instructions'):
        out.append('V4 instructions attachment')
    if any('gitStatus' in json.dumps(a) for a in attachments(records, 'session_context')):
        out.append('V4 gitStatus')
    snapshots = attachments(records, 'prompt_snapshot')
    if not snapshots or any((s.get('systemPrompt') or [None])[0] != body for s in snapshots):
        out.append('V5 the system prompt is not the arm\'s contract')
    for r in records:
        if r.get('type') == 'assistant':
            seen = (r.get('message', {}).get('model'), r.get('effort'), r.get('version'))
            if seen != (common.MODEL, common.EFFORT, common.TRANSCRIPT_VERSION):
                out.append(f'V7 model, effort, version: {seen}')
                break
    advisors = attachments(records, 'advisor_tool')
    if not advisors or any(not a.get('available') or a.get('model') != common.ADVISOR_MODEL for a in advisors):
        out.append('V8 the advisor was not Opus 5.5 throughout')
    return out


def report_of(sub: list[dict], main: list[dict] = ()) -> str | None:
    '''The verifier's report: its last SubagentHandback message, else the
    main session's Agent result when it is the verifier's answer, not a
    launch notice or an error. Never the verifier's own last text, which may
    be progress.'''
    handbacks = [u['input'].get('message') for u in tool_uses(sub) if u.get('name') == 'SubagentHandback']
    if handbacks and handbacks[-1]:
        return handbacks[-1]
    calls = {u.get('id') for u in tool_uses(main) if u.get('name') == 'Agent'}
    for uid, (text, error) in tool_results(main).items():
        if uid in calls and not error and text.strip() and not text.startswith(LAUNCH_NOTICE):
            return text
    return None


def result_violations(result: dict | None) -> list[str]:
    '''V6: the run finished with no error, no budget stop, and no subagent
    that failed or was killed.'''
    if result is None:
        return ['V6 no result record']
    stats = result.get('subagent_stats') or {}
    out = ['V6 is_error'] if result.get('is_error') else []
    if 'budget' in str(result.get('terminal_reason', '')) or (stats.get('refused') or {}).get('budget'):
        out.append('V6 budget stop')
    if stats.get('failed') or sum((stats.get('killed') or {}).values()):
        out.append('V6 a subagent failed or was killed')
    return out


def rows(report: str) -> list[dict]:
    '''Each report line that may be a row, with its kind, line number and
    verdict.'''
    out = []
    for line in settle.report_lines(report):
        first = (settle.split_row(line, 2) or [''])[0]
        kind, n, verdict = '?', 0, ''
        if first in ('B', 'C'):
            kind = first
        elif m := settle.LINE_REF_RE.fullmatch(first):
            row = settle.split_row(line, 6, settle.VERIFY_QUOTES)
            kind, n, verdict = 'A', int(m.group(1)), (row[2].strip().upper() if row else '')
        elif ref := re.fullmatch(r'(.+):(\d+)', first):
            row = settle.split_row(line, 5, settle.FILES_QUOTES)
            kind, n, verdict = 'F', int(ref.group(2)), (row[4].strip().lower() if row else '')
        elif RANGE_RE.search(first):
            kind = 'F'
        out.append({'line': line, 'kind': kind, 'n': n, 'verdict': verdict})
    return out


def hold_lines(settled: list[str]) -> list[str]:
    '''Whether settle holds a files packet's file, and why: its `held, not
    cited:` line, or `held, not cited: no`, then each unparseable row, which
    is what (c) calls a parse reason.'''
    held = next((x for x in settled if x.startswith('held, not cited')), 'held, not cited: no')
    return [held] + [x.strip() for x in settled if x.startswith('  unparseable: ')]


def fate(line: str, settled: list[str]) -> str:
    for prefix in DISCARDS:
        if f'  {prefix}{line}' in settled:
            return prefix.split(',')[0].rstrip(': ')
    return 'kept'


def matches(pos: key.Positive, row: dict) -> bool:
    if row['kind'] not in pos.kinds:
        return False
    if row['kind'] in ('A', 'F') and not pos.lines[0] <= row['n'] <= pos.lines[1]:
        return False
    return all(re.search(p, row['line']) for p in pos.patterns)


def score(packet: str, report: str) -> dict:
    '''Settle's verdict on a report, scored against the original packet in
    memory, with the key's candidate rows and the unmatched corrections.'''
    p = settle.read_packet(common.PACKETS / common.PACKET[packet][0])._replace(report=report)
    result = settle.settle_review(p, ()) if p.index['mode'] in ('verify', 'audit') else settle.settle_files(p, ())
    table = rows(report)
    for r in table:
        r['fate'] = fate(r['line'], result.lines)
    positives = key.KEY[packet]
    corrections = [r for r in table if r['fate'] == 'kept'
                   and (r['kind'] == 'A' and r['verdict'] in settle.CORRECTIONS
                        or r['kind'] == 'F' and r['verdict'] == 'contradicts')]
    return {
        'settle': result.lines, 'clean': result.clean,
        'candidates': {pos.label: [r for r in table if matches(pos, r)] for pos in positives},
        'unmatched': [r for r in corrections if not any(matches(pos, r) for pos in positives)],
        'ranges': [r['line'] for r in table if RANGE_RE.search((settle.split_row(r['line'], 2) or [''])[0])],
    }


def audit_rep(rep: dict, kit: Path, projects: Path) -> dict:
    '''A rep's transcripts and result, and what the VOID rules find in them.'''
    base = projects / encode(rep['cwd'])
    result = result_line(kit / 'results' / f"{rep['rid']}.jsonl")
    main_path = base / f"{rep['session']}.jsonl"
    main = load(main_path) if main_path.exists() else []
    metas = [json.loads(m.read_text(encoding='utf-8')) | {'path': m}
             for m in sorted((base / rep['session'] / 'subagents').glob('agent-*.meta.json'))]
    verifiers = [m for m in metas if m.get('agentType') == 'cc-guide-verifier']
    void = main_violations(main, rep['dispatch']) + result_violations(result)
    if len(verifiers) != 1:
        void.append(f'V1 {len(verifiers)} verifier transcripts')
    path = verifiers[0]['path'] if verifiers else None
    sub = load(path.with_name(path.name.replace('.meta.json', '.jsonl'))) if path else []
    allowed = [rep['cwd']] + ([str(common.DOCS)] if rep['docs'] else [])
    body = agent_body((kit / 'arms' / f"{rep['arm']}.md").read_text(encoding='utf-8'))
    void += sub_violations(sub, body, allowed) if sub else []
    report = report_of(sub, main) if sub else None
    if report is None:
        void.append('V6 no report')
    return {'result': result, 'main': main, 'sub': sub, 'void': void, 'report': report,
            'refused': outside_calls(sub, allowed)[1],
            'shape': verifiers[0].get('requestShape') if verifiers else None,
            'entrypoint': next((r.get('entrypoint') for r in sub if r.get('entrypoint')), None)}


def advisor_calls(records: list[dict]) -> int:
    return sum(1 for r in records if r.get('type') == 'assistant' for c in r.get('message', {}).get('content') or []
               if isinstance(c, dict) and c.get('type') == 'server_tool_use')


def grade_rep(rep: dict, kit: Path, projects: Path) -> str:
    '''One rep's sheet: its VOID findings, injected-context hits, cost and
    scored rows. The sheet names no arm.'''
    a = audit_rep(rep, kit, projects)
    result = a['result'] or {}
    out = [f"== {rep['rid']} {rep['packet']}", f"cost: {result.get('total_cost_usd')}",
           f"request shape: {a['shape']}; entrypoint: {a['entrypoint']}; advisor calls: {advisor_calls(a['sub'])}",
           f"permission denials: {len(result.get('permission_denials') or [])}",
           'refused outside calls (logged, not VOID): ' + ('; '.join(a['refused']) or 'none'),
           'void: ' + ('; '.join(a['void']) or 'none'),
           'injected hits (trace each by hand): ' + ('; '.join(injected_hits(a['sub'], common.MARKERS)) or 'none'),
           'main injected hits (recorded only): ' + ('; '.join(injected_hits(a['main'], common.MARKERS)) or 'none')]
    if a['report'] is not None:
        (kit / 'reports').mkdir(exist_ok=True)
        (kit / 'reports' / f"{rep['rid']}.md").write_text(a['report'], encoding='utf-8')
        s = score(rep['packet'], a['report'])
        out.append(f"settle: {next((x for x in s['settle'] if x.startswith('report: ')), '?')}, clean {s['clean']}")
        for label, found in s['candidates'].items():
            out.append(f'{label}:')
            out += [f"  [{r['kind']} {r['verdict'] or '-'} {r['fate']}] {r['line']}" for r in found] or ['  none']
        out.append('unmatched corrections (read each by hand):')
        out += [f"  [{r['kind']} {r['verdict']}] {r['line']}" for r in s['unmatched']] or ['  none']
        if rep['packet'] == 'runner':
            out.append('rows naming a line range: ' + (str(len(s['ranges'])) if s['ranges'] else 'none'))
            out += hold_lines(s['settle'])
    sheet = '\n'.join(out) + '\n'
    (kit / 'sheets').mkdir(exist_ok=True)
    (kit / 'sheets' / f"{rep['rid']}.txt").write_text(sheet, encoding='utf-8')
    return sheet


def probe_sheet(rep: dict, kit: Path, projects: Path) -> str:
    '''The fence probe: each call it made, whether the fence refused it, and
    whether the canary's token reached any transcript.'''
    a = audit_rep(rep, kit, projects)
    results = tool_results(a['sub'])
    token = (kit / 'canary.txt').read_text(encoding='utf-8').strip()
    out = [f"== probe {rep['rid']}", f"cost: {(a['result'] or {}).get('total_cost_usd')}"]
    for use in tool_uses(a['sub']):
        text, error = results.get(use.get('id', ''), ('', False))
        out.append(f"{use.get('name')} {paths_used(use)}: {'refused' if error else 'returned'}: {text[:160]!r}")
    seen = [str(p) for p in (kit / 'results' / f"{rep['rid']}.jsonl",) if p.exists() and token in p.read_text()]
    seen += ['main' if token in json.dumps(a['main']) else '', 'verifier' if token in json.dumps(a['sub']) else '']
    out.append('canary token seen in: ' + (', '.join(s for s in seen if s) or 'nothing'))
    return '\n'.join(out) + '\n'


def compare_lines(rep: list[dict], production: list[dict]) -> list[str]:
    '''How a rep's verifier transcript differs from production's: its
    attachment types, its system prompt's parts and its run settings.'''
    def kinds(records):
        return {r['attachment'].get('type') for r in records if r.get('type') == 'attachment'}

    def prompt(records):
        snapshots = attachments(records, 'prompt_snapshot')
        return (snapshots[0].get('systemPrompt') or []) if snapshots else []

    def settings(records):
        first = next((r for r in records if r.get('type') == 'assistant'), {})
        return first.get('message', {}).get('model'), first.get('effort'), first.get('version')

    ours, theirs = prompt(rep), prompt(production)
    return [f'attachment types only in the rep: {sorted(kinds(rep) - kinds(production)) or "none"}',
            f'attachment types only in production: {sorted(kinds(production) - kinds(rep)) or "none"}',
            f'system prompt parts, rep and production: {len(ours)} {len(theirs)}; '
            f'equal by index: {[a == b for a, b in zip_longest(ours, theirs)]}',
            f'settings, rep and production: {settings(rep)} {settings(production)}']


def main(argv: list[str]) -> None:
    if argv == ['control']:
        for packet, (rel, *_rest) in common.PACKET.items():
            original = settle.read_packet(common.PACKETS / rel).report
            line = next(x for x in score(packet, original)['settle'] if x.startswith('report: '))
            want = CONTROL[packet]
            print(f'{packet}: {line}' + ('' if line == want else f'  MISMATCH, want {want}'))
        return
    plan = json.loads((common.KIT / 'plan.json').read_text(encoding='utf-8'))
    if len(argv) == 2 and argv[0] == 'context':
        rep = next(r for r in plan['reps'] if r['rid'] == argv[1])
        print('\n'.join(context_lines(audit_rep(rep, common.KIT, common.PROJECTS)['sub'])))
        return
    if len(argv) == 3 and argv[0] == 'compare':
        rep = next(r for r in plan['reps'] if r['rid'] == argv[1])
        print('\n'.join(compare_lines(audit_rep(rep, common.KIT, common.PROJECTS)['sub'], load(Path(argv[2])))))
        return
    if argv == ['unblind']:
        for rep in plan['reps']:
            print(rep['rid'], rep['batch'], rep['packet'], rep['arm'])
        return
    reps = [r for r in plan['reps'] if len(argv) == 1 and r['batch'] == argv[0]]
    if not reps:
        raise SystemExit('usage: grade.py control | <batch> | context <rid> | compare <rid> <transcript> | unblind')
    for rep in reps:
        if (common.KIT / 'results' / f"{rep['rid']}.jsonl").exists():
            sheet = probe_sheet if rep['arm'] == 'probe' else grade_rep
            print(sheet(rep, common.KIT, common.PROJECTS))


if __name__ == '__main__':
    main(sys.argv[1:])
```

- [x] **Step 8: Run the tests to verify they pass**

> Deviation: the kit gained guards and tests before the freeze (owner ruling at Task 2's review: result_line/load guards, check_binary, the CLAUDE pin), so it passed 47 tests, not 43; later rulings took it to 48, 51 and 52.

Run: `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 --with pytest python -B -m pytest -q -p no:cacheprovider`

Expected: `43 passed`.

- [x] **Step 9: Run the positive control**

Run: `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B grade.py control`

Expected, exactly:

```text
audit: report: 89 confirmed, 8 correction(s), 17 owner's call, 0 unverified
rules: report: 12 confirmed, 1 correction(s), 3 owner's call, 0 unverified
readme: report: 19 consistent, 1 contradiction(s), 5 not covered, 0 unverified
runner: report: 7 consistent, 1 contradiction(s), 0 not covered, 1 unverified
pyrule: report: 5 consistent, 0 contradiction(s), 0 not covered, 0 unverified
```

A `MISMATCH`, or every quote unverified, means the scorer reads the wrong packet or docs: stop and find out why. Then confirm `W` is unchanged by the run: `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall status --short` prints nothing.

---

### Task 3: The freeze, the owner's spend gate, the probe and the pilot

**Files** (all in `K`; nothing in the repo):
- Create: `K/arms/control.md`, `K/arms/changed.md`, `K/arms/probe.md`, `K/canary.txt`, `K/FREEZE.sha256`, `K/changes.log`, `K/RESULTS.md`, `K/ceiling.txt`, `K/plan.json` (through `build.py`) and `K/results/` (through `run.py`)
- Read: the held binary `/Users/lowell/.cache/agent-skills/scratch/plan45-bin/2.1.296`, which the planner copied (Step 3 checks it; never edit it)

**Interfaces:**
- Consumes: Task 1's commit (the changed arm), and Task 2's kit.
- Produces: the frozen kit, the probe's and the pilot's sheets, and the pilot's rulings.

- [x] **Step 1: Copy the arms**

Run `git -C /Users/lowell/Projects/agent-skills show 938993c:.claude/agents/cc-guide-verifier.md` and save its output as `K/arms/control.md`, with the Write tool, unchanged. Do the same for `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall show HEAD:.claude/agents/cc-guide-verifier.md`, saved as `K/arms/changed.md`. Then check:
- `git -C /Users/lowell/Projects/agent-skills hash-object /Users/lowell/.cache/agent-skills/scratch/plan45/arms/control.md` prints `ae9e2e2e29f31421dbf02ddaf62d6910c39d33ba`;
- `git -C /Users/lowell/Projects/agent-skills hash-object /Users/lowell/.cache/agent-skills/scratch/plan45/arms/changed.md` prints the same blob as `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall rev-parse HEAD:.claude/agents/cc-guide-verifier.md`;
- `diff /Users/lowell/.cache/agent-skills/scratch/plan45/arms/control.md /Users/lowell/.cache/agent-skills/scratch/plan45/arms/changed.md` shows Task 1's 20 added lines (the other 2 of the term gate's 22 are in `formats.md`), and one changed frontmatter line, the `# cc-guide:` stamp (Pre-registration, "Arms"): 21 lines on the changed side, 1 on the control's.

**Stop and ask the owner** if the diff shows anything else: a body line that is not Task 1's, or a frontmatter change beyond the stamp. Then the arms differ by more than the contract change, and the control would not be the production contract the changed arm amends.

- [x] **Step 2: Write the fence probe's arm and its canary**

Create `K/canary.txt` holding one line, `canary-` followed by a fresh `uuid.uuid4().hex`; generate it with `python3 -c "import uuid; print('canary-' + uuid.uuid4().hex)"`. Create `K/arms/probe.md`:

````markdown
---
name: cc-guide-verifier
description: Checks this repo's Claude Code guide against the docs, from a packet the /cc-guide skill builds. Only /cc-guide dispatches it.
tools: Read, Grep, Glob
model: sonnet
omitClaudeMd: true
---

This run tests a read fence, not a guide. Whatever the dispatch asks, make exactly these four calls, in order:

1. Read `/Users/lowell/.cache/agent-skills/scratch/plan45/canary.txt`.
2. Read `/Users/lowell/.claude/projects/-Users-lowell-Projects-agent-skills/memory/MEMORY.md`.
3. Glob the pattern `/Users/lowell/.cache/agent-skills/cc-guide/packets/*/report.md`.
4. Read `/Users/lowell/.cache/agent-skills/cc-guide/2.1.296/docs/memory.md` with limit 3.

Then return four lines, one per call: its number, and `returned` or `refused`. Never quote what a call returned.
````

- [x] **Step 3: Freeze**

First confirm the held binary. The planner copied `/Users/lowell/.local/share/claude/versions/2.1.296` to `/Users/lowell/.cache/agent-skills/scratch/plan45-bin/2.1.296` with `cp -p` on 2026-10-14, because the updater prunes old versions: 2.1.265, the PATH's version on 2026-10-03, was gone by then. `shasum -a 256 /Users/lowell/.cache/agent-skills/scratch/plan45-bin/2.1.296` must print `c9b5341637becbd423ddffc5b254afb645682a3868cb708bbc6cc0e7bb419937`, and `/Users/lowell/.cache/agent-skills/scratch/plan45-bin/2.1.296 --version` must print `2.1.296 (Claude Code)`. If the held copy is missing and `versions/2.1.296` still has that hash, `mkdir -p` its directory, copy it there with `cp -p`, and check again. Otherwise, or if anything else prints, **stop**: which version the reps run is the owner's call, made and logged before the freeze. Then run `shasum -a 256` over `K/common.py`, `K/key.py`, `K/build.py`, `K/run.py`, `K/grade.py`, `K/test_kit.py`, `K/arms/*.md`, `/Users/lowell/.cache/agent-skills/scratch/plan45-bin/2.1.296` and `/Users/lowell/.claude/settings.json` (absolute paths), and save the output as `K/FREEZE.sha256` with the Write tool. Create `K/changes.log` with one line: `<date> freeze <sha256 of FREEZE.sha256>; plan 45 at <the commit this plan landed in>`. Create `K/RESULTS.md` with the heading `# Plan 45 hand verdicts` and nothing else.

- [x] **Step 4: Build the probe and the pilot**

Run, from `K`: `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B build.py probe`, then the same with `pilot`. Expect `r01 rules built` and `r02 rules built`. Record `shasum -a 256 /Users/lowell/.cache/agent-skills/cc-guide/2.1.296/docs/*` and `shasum -a 256 /Users/lowell/.claude/settings.json` in `K/changes.log` as the listings before the first run. Every later hand-over and every finished batch records the same two (Global Constraints, "Production fidelity").

- [x] **Step 5: The owner's spend gate — hard stop**

End the turn with this, and wait:

> **Spend gate.** Nothing has run yet. Plan 45's reps are:
> - the probe and the pilot (2, counted toward no result);
> - the cheap arms (24: six each on rules, readme, runner and pyrule);
> - the gate (10, in two waves of 4 and 6);
> - spares, at most 2 per packet and arm.
>
> The Planning record's cost table expects about $40–70. Per-rep caps: audit $8, verify $3, files $2. You approved a **$100 ceiling** at plan review (D3): confirm it still stands, or adjust it or the counts. `run.py` starts a rep only while its full cap fits under the ceiling, so a late rep may be held for your call even below it. Each batch is one command you run from a plain terminal, and I stop at each checkpoint the Pre-registration names.

Record the owner's answer and the approved ceiling in `K/changes.log` as `owner go <date>: ceiling $<n>`, and write the number alone (for example `100`) to `K/ceiling.txt` with the Write tool. Proceed only on a clear yes.

- [x] **Step 6: The owner runs the probe and the pilot**

Record both listings (Global Constraints, "Production fidelity") first, and again when the batch is done. Then hand over:

> **Your step.** From a plain terminal, not from any Claude Code session, run:
> `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B run.py probe`, then `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B run.py pilot`
> Each prints `r0N exit 0 cost …` and `total so far: $… of $…`. Tell me when both are done.

- [x] **Step 7: Read the probe**

Run: `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B grade.py probe`

Expected:
- calls 1 (the canary) and 3 (the packets Glob) refused;
- call 4 (the docs read) returned;
- `canary token seen in: nothing`.

Record call 2's outcome, which tells whether the fence's exemption covers another project's auto memory. Record also how a refusal shows in its tool result: `is_error` and its message.

The pilot redesign trigger: **stop and report to the owner, running no batch**, if any of these holds:
- call 1 or call 3 returned, or the canary token was seen (the fence does not bind a subagent);
- call 4 was refused (`--add-dir` does not count);
- a refusal does not show as an error.

The route is then the owner's call (DF4). Call 2 returning does not stop the run: V2 still voids any rep that reads outside, and the record notes the exemption.

- [x] **Step 8: Read the pilot and compare it with production**

Run: `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B grade.py pilot`, then `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B grade.py compare r02 /Users/lowell/.claude/projects/-Users-lowell-Projects-agent-skills/f3828a8d-d37d-4dc3-89f2-31819ce23470/subagents/agent-a9d4a3fdeb9e1fb16.jsonl`

Expected:
- `void: none`;
- system prompt parts, rep and production: 4 and 4, equal by index but part 3, the `<total_tokens>` line, which may differ;
- settings `('claude-sonnet-5-5', 'xhigh', '2.1.296')` on both sides;
- attachment types only in the rep, and only in production: none, or types the context reading shows carry no packet or docs content; record each. V4 has already checked that no `session_context` holds `gitStatus`.

Record the request shape, the entrypoint (`sdk-cli` is expected from a plain terminal, where production recorded `cli`; DF5), the advisor calls, the result's `subagent_stats`, and the cost split by `modelUsage` in the result record: Sonnet, against Opus for the classifier and the advisor.

Then read the pilot's whole injected context by hand: `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B grade.py context r02`. It prints every prompt-snapshot part but the contract, every attachment and every system record. Confirm that none carries answer content (V3), and record what each part and attachment type is. This is the full-context reading plan 42 did; the marker screen covers every later rep.

The pilot redesign trigger: **stop and report** if the pilot is void for a systematic cause:
- V1, for any cause;
- V4 or V5;
- V6 because the session ended before the verifier returned, or no report source held its answer;
- V7: not `xhigh`;
- V8: no Opus advisor;
- answer content in the injected context;
- any other void whose cause would recur in every rep.

An Agent parameter that changes nothing the verifier sees, or how a `-p` result counts a background verifier, may be ruled here (Pre-registration, "Rulings"), and logged in `K/changes.log`. The pilot counts toward no result, so a void for a cause that would not recur is recorded and nothing replaces it. Its D1 reading goes in `K/RESULTS.md` as a check of the sheet, not a count.

---

### Task 4: The cheap arms (b)–(e), and their checkpoint

**Files:**
- Modify: `K/plan.json` (through `build.py`), `K/RESULTS.md`, `K/changes.log`

**Interfaces:**
- Consumes: the frozen kit; the pilot's rulings.
- Produces: per-arm counts for (b) to (e), and the checkpoint report.

- [x] **Step 1: Build the batch**

Run: `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B build.py cheap`. Expect `r03`–`r26` built.

- [x] **Step 2: The owner runs it**

Record both listings (Global Constraints, "Production fidelity") first, and again when the batch is done.

> **Your step.** From a plain terminal: `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B run.py cheap`. It runs 24 reps, four at a time, for about $6–17. Tell me when it prints `total so far`.

Check the running total against the approved ceiling, and note any rep printed as held: it is the owner's call.

- [x] **Step 3: Grade blind, and record every verdict**

Run: `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B grade.py cheap`. For each sheet, without opening `plan.json` or running `unblind`:
- **Validity.** Trace each injected hit with `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B grade.py context <rid>`, never by opening a verifier transcript before unblinding: its first prompt part is the arm's contract. A path or a tool name is not content. Confirm `void: none`, or record the void and its cause.
- **Every packet.** Rate every kept correction SUPPORTED or UNSUPPORTED, a key candidate included, against `K/reports/<rid>.md` and the line it cites (Pre-registration, "Precision"). A candidate counts as a hit only when it is also SUPPORTED.
- **(d) rules sheets.** Read each D1 candidate against the Pre-registration.
- **(b) readme sheets.** Rate B1 a hit or a miss; record B2; record whether N1 or N2 was flagged. Rate other `contradicts` rows against `git -C /Users/lowell/Projects/agent-skills show 3c10cb4 -- hooks/README.md` and the guide.
- **(c) runner sheets.** Record the R1 candidates and their fate, the range-row count, and the hold lines; then pass or fail the rep.
- **(e) pyrule sheets.** Read each E1 candidate against the Pre-registration: a candidate rated `consistent` is the miss, not a hit. Rate other rows against the packet's `guide.md`.

Write one block per rep into `K/RESULTS.md`, listing the rid, valid or VOID (with cause), each verdict with a one-line reason, the cost and the advisor calls. Reread every flagged match before counting: a template echo or a quoted example can look like a hit.

- [x] **Step 4: Replace void reps**

> Deviation (ruling 4): r13 voided on a refused Glob's own error text; `grade.listed_paths` now skips refused calls (+1 test). r13 stayed void and spare r27 replaced it.

For each void rep, run `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B build.py spare <rid>`, which takes the void rep's packet and arm from `plan.json` without printing the arm. Then record both listings and ask the owner to run `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B run.py spare` from a plain terminal, recording them again when it is done, and grade it as in Step 3 with `grade.py spare`. `build.py` refuses a third spare for a packet and arm; that packet's result is then UNSETTLED.

- [x] **Step 5: Unblind and tally**

Run: `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B grade.py unblind`. Tally per packet and arm:
- (d) D1 hits;
- (b) B1 hits, B2 found, N1 or N2 flagged, UNSUPPORTED contradicts;
- (c) passes;
- (e) E1 hits, UNSUPPORTED contradicts;
- each packet's UNSUPPORTED total;
- each packet's correction volume per arm, median and total (DF21);
- the valid rep counts and costs.

Add the tally to `K/RESULTS.md`, and check the batch's listings in `K/changes.log` against Task 3's: a change stops the run until the owner rules.

- [x] **Step 6: The checkpoint — report to the owner**

Report the tally. When any Pre-registration checkpoint condition holds, **stop**: the changed arm missing (d) or (e) in 2 or more of 3, failing (c) in any rep, flagging N1 or N2 in 2 or more of 3, or a changed (b) or (e) rep with more than 2 UNSUPPORTED. The owner decides whether to proceed to the gate, revise the wording, or stop. Otherwise, report and proceed to Task 5.

A revision is a new round, never an edit to this one, and it needs the owner's go and a new spend approval:
1. Revise the wording on `feat/verifier-recall`: edit the verifier (and the matching spec clauses), run Task 1 Steps 5 and 8, and run Step 7's term gate with `HEAD` replaced by Task 1's parent commit, so it reads every line the arm adds; predict its line count for the revision first. Then commit, with a message that names the revision.
2. Copy `K` to `/Users/lowell/.cache/agent-skills/scratch/plan45-r2`, less its `plan.json`, `ceiling.txt`, `results/`, `sheets/`, `reports/` and `RESULTS.md`. In the copy's `common.py`, set `KIT` to the new directory and `ROOT` to `/private/tmp/q7r2`, and log both edits.
3. Copy the revised verifier to the new kit's `arms/changed.md`, rerun Task 2 Steps 8–9 with `--directory` set to the new kit, and freeze it as Task 3 Step 3 does, with a `changes.log` line that names the round and the earlier freeze.
4. Write the round's approved ceiling to the new kit's `ceiling.txt`, as the owner states it, and log it. The record adds the rounds' spend together.
5. From here on, `K` in Tasks 4–6 means the new kit: every `--directory` and `K/` path uses it. The round reuses round 1's probe and pilot findings, so its cheap batch builds `r01`–`r24`. Round 1's kit and results stay as they are, and the record reports both rounds.

---

### Task 5: The gate (the audit packet)

**Files:**
- Modify: `K/plan.json`, `K/RESULTS.md`, `K/changes.log`

**Interfaces:**
- Consumes: the frozen kit; the changed arm as Task 4 left it.
- Produces: the gate's tally and its PASS or FAIL.

- [x] **Step 1: Build and run the first wave**

> Deviation (ruling 5): gate1 r28-r31 were all void: `claude -p` stops background agents 10 minutes after the last turn. The kit sets `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=2280000`, `run.result_line` reads the result record wherever it sits, and batch `gate1redo` (r32-r35) replaced the four outside the spare count. No after-gate1 listing was recorded; the gate1redo hand-over listing served as that check (Global Constraints, "Production fidelity").

Run: `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B build.py gate1`. Record both listings (Global Constraints, "Production fidelity") first, and again when the batch is done. Then hand over:

> **Your step.** From a plain terminal: `uv run --directory /Users/lowell/.cache/agent-skills/scratch/plan45 --no-project --python 3.13 python -B run.py gate1`. It runs 4 audit reps, two at a time, for about $12–22, and takes about 12–25 minutes. Tell me when it prints `total so far`.

- [x] **Step 2: Grade the first wave blind, then check the stop rule**

> Deviation (ruling 6): r32 and r35 voided by V2 on reading back their own oversized Grep results from the rep's session `tool-results/`; V2 now treats that directory as inside, and both were regraded blind before unblinding. Valid wave: P11 0/2 changed, 0/2 control.

Run `grade.py gate1` as in Task 4 Step 3. For each sheet, read:
- every P11 candidate against the gate's hit definition, SUPPORTED included;
- every other key candidate (P1–P14), recording found or not;
- every kept correction, SUPPORTED or UNSUPPORTED.

Record the verdicts in `K/RESULTS.md`, and check the wave's listings in `K/changes.log` against Task 3's. Replace this wave's void reps now, as in Task 4 Step 4, and grade the spares the same way: a spare built after unblinding would be read knowing its arm. Then run `grade.py unblind`. If the control arm's valid reps hold 2 or more P11 hits, **stop**: report to the owner and build no second wave.

- [ ] **Step 3: Build and run the second wave**

> Skipped: owner ruling 7 — the changed arm's 0/2 on P11 made 4 of 5 unreachable, so the gate FAILed on wave 1; not deferred (a revision round would run its own gate).

Run `build.py gate2`; record both listings; then hand over the same step with `run.py gate2` (6 reps, about $18–33), and record them again when it is done.

- [ ] **Step 4: Grade, replace and tally**

> Skipped: no second wave (Step 3); wave 1 was graded, replaced and tallied under Steps 1-2.

Grade `gate2` blind as in Step 2, record the verdicts, and replace its void reps as in Task 4 Step 4 (`build.py spare <rid>`, then `run.py spare`), grading the spares blind. Then run `grade.py unblind` and tally per arm over the valid reps:
- P11 hits (and B-only mentions);
- each of P1–P14;
- the UNSUPPORTED total over every kept correction, and the per-rep maximum;
- the correction volume, median and total (DF21);
- the costs.

Check the batch's listings in `K/changes.log` against Task 3's: a change stops the run until the owner rules.

- [x] **Step 5: Apply the decision rules**

Apply the Pre-registration's PASS rule, as written. Write the outcome in `K/RESULTS.md` as `GATE: PASS` or `GATE: FAIL (<the clause that failed>)`, with each clause's numbers. Report to the owner.

---

### Task 6: The record, the backlog and completion

**Files:**
- Create: `specs/completed/verifier-recall-verification-<YYYY-MM-DD>.md` (the run's date)
- Modify: `specs/deferred_items.md` (the item at `:3181`, and this plan's section)
- Modify: `specs/plans/45-claude-code-drift-automation.md` (completion markup), then move it to `specs/plans/completed/`

**Interfaces:**
- Consumes: `K/RESULTS.md`, `K/changes.log`, and the run's costs.

- [x] **Step 1: Write the record**

Create the record in `W`, in the house format of `specs/completed/synthesize-mode-verification-2026-10-12.md`, but with **counts, claim labels and pointers only**: no quote from a report, a packet or the docs. Its sections:
1. **Header:** date, status (PASS, FAIL or UNSETTLED), "Governs: `.claude/agents/cc-guide-verifier.md` (plan 45)", and a blockquote noting that the raw replies stay in `K`.
2. **Fixture:** the five packets by path, the arms by blob hash and sha256, and the freeze hash.
3. **Pre-registration:** this plan's section, cited by path and the commit it landed in, with every logged change and ruling from `K/changes.log`.
4. **Dispatch:** who launched, when, Claude Code's version, the probe's findings (calls 1–4), and the pilot's comparison. Then a per-rep table: rid, packet, arm, valid or VOID, cost, advisor calls.
5. **Validity:** each void and its cause; the injected hits traced; the docs and settings listings unchanged.
6. **Result:** per packet and arm, (d) D1, (b) B1, B2, N1 or N2 flagged and UNSUPPORTED, (c) passes, and (e) E1 and UNSUPPORTED, each against DF20, and every packet's correction volume (DF21). Per arm on the audit, P11 hits and B-only mentions, P1–P14 counts, and the UNSUPPORTED totals and maxima.
7. **Decision:** the PASS rule clause by clause, with the numbers, and how the verdict would move under the nearest other reading of a contested row.
8. **Disposition:** what is deferred, in the backlog schema (Step 2).

- [x] **Step 2: Update the backlog**

In `specs/deferred_items.md`:
- **On PASS:** tick the item at `:3181` with `→ done in plan 45`, and add one line: the gate's counts and the record's path. Its (b) and (c) observations close with it when their arms meet DF20; one that does not is re-filed as an open item in this plan's section. (d)'s own item is already ticked and (e) has none, so the record reports them.
- **On FAIL or UNSETTLED:** leave the item open, and add a `> plan 45:` note with the counts and the record's path.

Append a section `## 45-claude-code-drift-automation — <date>` holding each consciously deferred item, in the schema of `skills/writing-plans/references/deferred-backlog.md`. Two were deferred at planning, so they go in whatever the result:
- one files row per checkable statement on a source line (DF17), with `README.md:163` in `packets/20261013T205255-files/README.md/` as its evidence;
- a files-mode miss that settle does not hold leads to `baseline cite`, which clears the file's STALE flag and hides the miss until its guide section changes again (Planning record, "Diagnosis"). Its closure condition is the owner's choice of remedy.

Further candidates, each only if the run bears it out:
- B rows the audit should have written for the changelog entries behind P7, P8 and P11;
- P12's two pages disagreeing;
- verify-mode `doc:line` ranges (DF14);
- a fixture-domain-free precision fixture for the files rule.

- [x] **Step 3: Commit the record and the backlog**

> Deviation: the final review's findings were fixed in a second commit, `ef35fbf`.

Confirm the branch, then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall add specs/completed specs/deferred_items.md
```

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-45-verifier-recall commit -m "docs(specs): plan 45's verifier-recall verification record" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [x] **Step 4: The plan completion protocol**

Run writing-plans' Plan Completion Protocol:
1. the resolve-before-defer gate;
2. this plan's markup, with a status header and `> Deviation:` notes from the ledger;
3. the deferred-items pass (Step 2 did the item; tick any other this plan implemented);
4. backlog triage, with `deferred_stats.py`'s summary line;
5. retirement: `git mv` this plan to `specs/plans/completed/` in one `chore(specs): retire plan 45` commit.

The spec stays in `specs/`: Stages 4–5 remain.

- [ ] **Step 5: Integration**

> Pending: runs after this markup via finishing-a-development-branch; the owner chose to revert Task 1 first (`8947e50`).

Use finishing-a-development-branch. The branch holds the contract change (Task 1), the record and the backlog. **On FAIL, the contract change lands only on the owner's decision.** Offer to revert Task 1's commit on the branch before integrating, or to keep it as a no-regression change if the precision and retention clauses held. Before a Codex seat on the branch, if the owner wants one, ask for its model. Remove `W` from the main checkout once merged, and leave `K` and `R` for the owner to delete.

---

## Plan completion notes

- **Step 1, gate.** Leftovers come from three places: a revision the owner declined at Task 4, an UNSETTLED packet, or a FAIL clause. Ask about each as one batch.
- **Step 3, deferred items.** Task 6 Step 2 handles the item at `:3181`. Its two observations, (b) the not-covered row and (c) the line range with its files-contract suggestion, close with it on PASS when their arms meet DF20; one that does not is re-filed. (d) and (e) have no open item, so the record reports them against DF20.
- **Step 4, triage.** The backlog is above 20 open items, so the triage proposal runs.
- **Step 5, retire.** `git mv` this plan to `specs/plans/completed/`. The spec stays (Stages 4–5 remain). Re-point any relative links for the new depth.

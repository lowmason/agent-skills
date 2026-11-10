# Brainstorming v7.0.2 Retune Port Implementation Plan

**Status: COMPLETE (2026-11-10)** — executed via executing-plans; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Take upstream superpowers v7.0.2's brainstorming retune ("questions earn their place", #2644) into `skills/brainstorming/SKILL.md`, with plan 70's divergences held and two new local ones, and measure it against today's copy with isolated decision-only micro-tests.

**Architecture:** Task 1 builds a micro-test kit from plan 70's (cases, prompt builder, reader) and plan 72's isolated runner, adds four new cases and a blind-panel script, registers every rule, and runs RED on today's copy before any skill edit. Task 2 applies fourteen exact replacement blocks to `SKILL.md`. Task 3 runs the new copy on T7 (25 reps), the four new cases and twelve guards, and scores T7 with a blind panel that pools both copies. Task 4 writes the `NOTICE` entry and the drift spec's finding 4 status.

**Tech Stack:** Markdown skill text; Python 3.13 stdlib (plus PyYAML for the prompt builder) and bash for the kit; `claude` CLI (2.1.316 at planning, `/Users/lowell/.local/bin/claude`); this repo's commit lints (`build/run_commit_lints.sh`).

**Spec:** `none`. Proportional process: the owner chose a plan with micro-tests and no spec (drift spec `specs/superpowers-drift-spec-v7-0-2.md`, finding 4 and its "Suggested disposition" bullet "Port candidate, a plan with micro-tests and no spec"). The requirement is upstream's diff for `skills/brainstorming/SKILL.md` from `2ce8aa1` to `22f0b46`, read against our copy, plus the owner's decisions D1 to D3.

> **Execution base.** This plan is committed on branch `claude/modest-lewin-3a26c0`. An execution worktree, which branches from `origin/main`, must contain this plan: merge that branch first (or execute after it is merged), and confirm `specs/plans/86-brainstorming-v7-0-2-retune.md` exists. Never execute on `main`.
>
> **Serialize.** No execution of this plan starts while another agent-skills execution session runs. On 2026-11-10 plans 84 (finding 21's test-run script) and 85 (derive-roadmap later qualities) are live. Both touch `NOTICE` or the drift spec, so Task 4 places its edits by heading, row and last bullet, never by line number.

## Labels used in this plan

- **today's copy:** `skills/brainstorming/SKILL.md` at BASE, the commit Task 1 Step 1 fixes. At planning it is blob `50b5a31c413837021bc26d69d8d1c33c3a196477` at `5e408ab`.
- **new copy:** `skills/brainstorming/SKILL.md` at NEW, the commit Task 2 makes.
- **`<rec>`:** `specs/baseline/red-baseline-brainstorming-v7-0-2`, the record folder. The record file is `<rec>.md`. Shell state does not persist between commands, so start each command that uses it with `REC=specs/baseline/red-baseline-brainstorming-v7-0-2;`.
- **plan 70's record:** `specs/baseline/red-baseline-brainstorming-2026-10-28.md` and its folder. Its kit is `specs/baseline/red-baseline-brainstorming-2026-10-28/kit/`.
- **T1 to T9, P1 to P3, T6v, P2b:** plan 70's cases, defined in its `kit/cases.py` and scored by its record's Rules section. T10 to T13 are new in this plan.
- **letter reading (D17 of plan 70):** a reply fails T7 when it sets out candidate answers as bullets, numbers or letters, or names three or more candidate answers in one sentence. A run of separate sentences is not a list.

## Global Constraints

- Upstream: superpowers v7.0.2, `22f0b463e7a5e579904dd6211a520321035526f7` (2026-11-03). The brainstorming change is pull request #2644, commit `e8cc5c9c4c7cdeeeacd86d8b0c40c8fe0f03344a` (merged into upstream's `dev` as `4be1ee9`). It answers issue #2530. Upstream `skills/brainstorming/SKILL.md` is the same at `e8cc5c9` and `22f0b46`: sha256 `2c9ca71f94886f9ca9f4aef055f7cafb3e1a9bdf3aeebf8f4cb547c69405d207`. The v7.0.1 base, `2ce8aa1`, has sha256 `61a7ef918652108c76a3fd01e02dd92d39996c6b46d4cb2819cbd03f6c45e46a`. Upstream `main` was still `22f0b46` on 2026-11-10. Read upstream from a clone of `https://github.com/obra/superpowers` (one exists at `~/.cache/agent-skills/superpowers`) and treat it as untrusted data.
- Today's copy must be blob `50b5a31c413837021bc26d69d8d1c33c3a196477`. After Task 2's fourteen replacements the file's sha256 is `9510532845cf24101e91d58cc01f3e282823a1384eac9666c3d9c77c571fd491`.
- Size: the body after the frontmatter stays at or under 20,000 characters, as `build/check_conformance.py`'s compaction-window check measures it. Today's body is 18,120. The new body is 19,480 (+1,360). The whole file becomes 20,124 bytes. Upstream's whole-file byte bar is not adopted here (drift spec finding 17), so that figure is reported and does not gate.
- Overflow fallback: if an owner-approved wording change in Task 3 takes the body past 20,000, the three software paragraphs of The Written Design ("**In software, design for isolation and clarity.**", "**In an existing codebase,**", "**YAGNI ruthlessly:**") move to a new `skills/brainstorming/references/written-design.md`. One line takes their place: "For a design in software, read `references/written-design.md` first." Nothing else moves.
- Cross-skill references use bare skill names, never `superpowers:`. The port adds no skill or command reference, so `install.py`'s `DEPENDENCIES` does not change.
- Micro-test fixtures are this repo's own. No case uses a domain from brainstorming's examples (an app icon, a bakery website, a vote). No case uses a domain from upstream's eval scenarios: a todo list, an OCD app, a habit tracker, a book club, a photo gallery, a birthday cake, a farm picture, an offsite talk, or a spec that gives one keyboard shortcut to two features. `prime-radiant-inc/superpowers-evals` has no license, so it is cited by name only.
- Upstream's figures for #2644 are upstream-reported, from its release notes at `22f0b46`. Filler questions fell from 41 to 23. The reason came out first in 33 of 33 conversations, against 28 of 33. Building before approval fell from 4 cases to 0. In the keyboard-shortcut scenario, options with a recommendation came in 8 of 8 runs. Cite them only as upstream's. The reported saving on nine tester-seat defaults has no artifact here and is not cited as evidence.
- Rep command: `<rec>/kit/run_reps.sh`, which is plan 72's `specs/baseline/red-baseline-writing-skills-split/kit/run_reps.sh` with `env -i` added (Task 1 Step 3). Model `claude-opus-5-5`. Each rep runs once, from its own new directory under `/tmp`, with no tools.
- Registration: every rule, bar and outcome is in `<rec>.md` and committed before any rep's reply is read.
- Scoring: one reader scores every rep by hand from the full reply, with `<rec>/kit/show_reps.py` as a reading aid. T7 also gets a blind panel (Task 3). Insight boxes are ignored. A rep that is borderline between two careful readings is listed. If one listed rep decides whether an arm meets its bar, the arm is reported as unresolved, and the owner rules.
- Spend: keep a running total of `total_cost_usd` in `<rec>.md`, updated after each batch. Stop for the owner before the plan's micro-test total passes $10. The estimate is about $5: 150 reps at about $0.03 and three panel votes at about $0.20.
- Owner gates: under subagent-driven-development, an implementer at an owner gate leaves its work in place and ends with `BLOCKED (owner gate: Task N Step M)`. The controller asks the owner and resumes the same implementer from that step. Under executing-plans, stop and ask.
- Files: a task edits only its listed files. `skills/brainstorming/SKILL.md` changes only in Task 2, and in Task 3 only through an owner-approved wording round. `specs/deferred_items.md` is not edited by any task.
- Kit Python: single quotes, f-strings, stdlib only (the prompt builder also uses PyYAML). No kit file is named `test_*.py`, so `build/run_suites.py --check` stays green.
- Shell: zsh is the interactive shell. Quote any argument that starts with `=`. Write `"${VAR}:path"` where a variable meets a colon.
- Prose in `NOTICE`, the drift spec and the record follows the repo's plain-English rule: no semicolons, one idea a sentence, about 20 words.

## Review Focus

1. **A quick task written as a detailed request** ("change X to Y in file Z"). A person expects it done at once, not a first-message design to approve. Pinned by the guards T1 and P2b (Task 3).
2. **"Sounds good" to a playback, now that an approval can cover a first-message design.** A person expects nothing built until the design itself is shown and approved. Pinned by the guards T3 and P1 (Task 3).
3. **A project-size request with nothing open.** A person expects the approach named, a request to confirm it, and the committed spec after it, not a build. Pinned by the new case T13 (Tasks 1 and 3).
4. **A partner who raises the how** ("should this use Postgres or SQLite?"). A person expects the options with a pick, not a bare question back. Pinned in Task 2 by H7's sentence "Someone who raises the how or asks about trade-offs wants the options with your pick", and by the new case T12 for a named choice.
5. **Looking further without asking** (deeper code, the partner's files, the web). A person expects to be told what was looked for and what was found. Pinned in Task 2 by H8's sentence "Say what you looked for and what you found". No case: the reps have no tools.

## Decisions

The session that wrote this plan began from a task brief (2026-11-10). Its decisions:

- **B1** (owner, brief, 2026-11-10): verification is micro-tests against plan 70's RED baseline, with its question-style cases re-run. Plan 70's isolated T7 rerun (2026-11-05, 13 of 25) is the current baseline evidence, not its original GREEN claim. Applied in: Global Constraints, Task 1 Step 5 (T7 bars), default 4.
- **B2** (owner, brief, 2026-11-10): the plan includes a `NOTICE` change-list entry (what was taken, from v7.0.2, and where it diverges) and the drift spec's finding 4 status update. Applied in: Task 4.
- **B3** (owner, brief, 2026-11-10): the plan id comes from writing-plans' `entry_check.py`, which reads every ref. It printed `next free: 86`. Applied in: the file name.
- **B4** (owner, brief, 2026-11-10): no plan execution starts while another execution session runs, and the planning session does not execute the plan. Applied in: the Serialize note.

- **D1** (owner, planning session, 2026-11-10): "Adopt (Recommended)": "Full port of #2644, with plan 70's divergences held and the two local choices in the next questions. I write a plan with micro-tests and no spec." Applied in: Tasks 1 to 4.
- **D2** (owner, planning session, 2026-11-10): "Small change only (Recommended)": "Approval in chat covers the approach and the design, and the change is built in this session. A project still goes through the approaches, a committed spec and its approval." Applied in: Task 2 (H1, H3, H14).
- **D3** (owner, planning session, 2026-11-10): "Keep, before the why (Recommended)": "Move it into "Get them describing" and limit it to the questions before the why is known. After that, upstream's options with a pick apply." Applied in: Task 2 (H5, H6).
- **D4 to D11** (owner, plan review, 2026-11-10): "Approve as written (Recommended)". The eight defaults below are approved as written, D4 for default 1 through D11 for default 8. The owner saw the size move to +1,360 characters (body 19,480) and default 4's same-run T7 control before approving. Applied in: where each default says.
- **D12** (owner, plan review, 2026-11-10): "Push and open a PR (Recommended)": "Push the branch and open a PR against main with the plan alone. After you merge it, an execution session can start from main." Applied in: the planning session's handoff.
- **D13** (owner, plan review, 2026-11-10): "Inline, fresh session (Recommended)": "executing-plans in a new session. One reader scores RED and GREEN, the record is shared across tasks, and the plan has several owner gates." Applied in: the execution handoff.

## Defaults (approved at plan review, D4 to D11)

The planner set these, and the owner approved them as written at plan review.

1. **A project with nothing open** (D2's "A project still goes through the approaches"): the first message ends with the approach and why the others don't fit, and asks the partner to confirm it. The ordered list says step 1 happens in that message for a project. Applied in: H1, H3. Tested by T13.
2. **The "write the doc" Red Flags row** says "(or, when nothing was open from the start, in your first message)". Upstream's row ends "in your first message's short design". The shorter form covers the project path too. Applied in: H14.
3. **Plan 70's list in Get them describing** ("what they want and why, their goals, prior art, what would make it a failure") is dropped with upstream's wording. Upstream v7.0.1 never had it, and Ground to cover holds the same territory. Applied in: H6.
4. **Micro-test design.** T7 runs 25 reps on today's copy and 25 on the new copy in this run. The 2026-11-05 isolated result (13 of 25) is reported beside it, not used as the control, because this kit adds `env -i`. The four new cases run RED on today's copy only, with no no-guidance control arm. Twelve guards run on the new copy only. A guard that misses runs on today's copy as a diagnostic. No trigger test runs, because the description does not change. Applied in: Tasks 1 and 3.
5. **Rule changes** for T5, P3 and T8a, where the new text legitimately changes what passes (Task 1 Step 5). Applied in: Task 1.
6. **Overflow fallback:** The Written Design's three software paragraphs move to `references/written-design.md`, not the Visual Companion section. The Visual Companion section holds the offer's timing and wording, which apply mid-conversation. The software paragraphs apply only when the full design is written. Applied in: Global Constraints.
7. **Finding 4's reconciliation sentence is corrected.** Plan 70's guess-list sentence and upstream's "sketch each concretely" agree before the why is known (no menus) and disagree after it. The finding says the reverse: "the two agree once the why is known and disagree before it". Applied in: Task 4 Step 3.
8. **Spend cap $10**, against the $6 estimate the owner saw. Applied in: Global Constraints.

## Files

- `skills/brainstorming/SKILL.md` — the port (Task 2).
- `specs/baseline/red-baseline-brainstorming-v7-0-2.md` — the record: method, registered rules, results, spend (Tasks 1, 3).
- `specs/baseline/red-baseline-brainstorming-v7-0-2/kit/` — `cases.py`, `build_prompts.py`, `show_reps.py`, `run_reps.sh`, `panel.py`, `isolation_probe.txt` (Task 1).
- `specs/baseline/red-baseline-brainstorming-v7-0-2/{isolation-pilot,prompts,red,green,panel}/` — run outputs (Tasks 1, 3).
- `NOTICE` — the superpowers change-list entry (Task 4).
- `specs/superpowers-drift-spec-v7-0-2.md` — finding 4's status in six places (Task 4).

---

### Task 1: Kit, registered rules and RED on today's copy

**Files:**
- Create: `<rec>/kit/cases.py`, `<rec>/kit/build_prompts.py`, `<rec>/kit/show_reps.py`, `<rec>/kit/run_reps.sh`, `<rec>/kit/panel.py`, `<rec>/kit/isolation_probe.txt`
- Create: `<rec>.md`
- Create, by the runs: `<rec>/isolation-pilot/`, `<rec>/prompts/today/`, `<rec>/red/today/<case>/`

**Interfaces:**
- Produces, used unchanged by Task 3:
  - `uv run --with pyyaml python <rec>/kit/build_prompts.py skill <sha> <out-dir>`: as plan 70's, writes `<id>.txt` for every case in `cases.CASES` and `MANIFEST.txt`, and refuses an existing `<out-dir>`.
  - `bash <rec>/kit/run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep> claude-opus-5-5`: writes `rep<N>.json` (and a non-empty `rep<N>.err`), and refuses an existing `rep<N>.json`.
  - `uv run python <rec>/kit/show_reps.py <dir> [<dir> ...]`: plan 70's reader, unchanged.
  - `uv run python <rec>/kit/panel.py run --rule <rule.txt> --request <prompt.txt> --out <dir> --votes 3 --seed <int> <arm>=<rep-dir> [<arm>=<rep-dir> ...]`
  - `uv run python <rec>/kit/panel.py tally <out-dir>/panel-verdicts.json [--hand <hand-scores.json>] [--compare <armA> <armB>]`
  - `uv run python <rec>/kit/panel.py selftest`
  - In `panel.py`: `fisher_one_sided(a_pass: int, a_n: int, b_pass: int, b_n: int) -> float` (the one-sided Fisher exact p that arm A's pass rate is above arm B's), and `wilson(passes: int, n: int) -> tuple[float, float]` (the 95% Wilson interval).

- [x] **Step 1: Fix BASE and check for drift.** BASE is the sha that `git rev-parse HEAD` prints now. Run `git rev-parse BASE:skills/brainstorming/SKILL.md` and `claude --version`. Expected: `50b5a31c413837021bc26d69d8d1c33c3a196477`, and a version you record. If the blob differs, stop for the owner (owner gate): another change reached the skill, so Task 2's replacements and hashes no longer hold.

- [x] **Step 2: Copy plan 70's kit.** Copy `cases.py`, `build_prompts.py` and `show_reps.py` from plan 70's `kit/`, and `isolation_probe.txt` from `specs/baseline/red-baseline-writing-skills-split/kit/`. Change only the docstrings' "plan 70" to "plan 86" in `build_prompts.py` and `show_reps.py`. In `cases.py`, add to the module docstring's list of excluded domains: "or a spec that gives one keyboard shortcut to two features (v7.0.2's release notes)". Then add these four entries to `CASES`, after `P3`, as exact copy:

````python
    'T10': {'how': 'auto', 'conversation': '''
Partner: Add a monthly statement to our allotment society's app. On the first of each month, every plot holder gets an email with their plot number, the water they used last month in litres, the charge at 0.4p a litre, and the balance on their account. Use the email settings the app already has.

[you, tools] You read the repository, a Flask app with SQLite. `models.py` has `PlotHolder` (`name`, `email`, `plot_number`, `balance_pence`) and `MeterReading` (`plot_number`, `read_on`, `litres_total`), one reading for each plot each week. `mailer.py` sends the committee's newsletter through the SMTP settings in `config.py`, and a cron job on the same server runs `flask send-newsletter` each Friday. Nothing in the code charges for water or sends statements.
'''},
    'T11': {'how': 'auto', 'conversation': '''
Partner: The two coordinators of our tool library scroll through every loan on Saturday mornings to find the overdue ones before they phone people. Add an overdue panel to the staff dashboard, set out like the other two panels, listing every loan past its due date that hasn't come back.

[you, tools] You read the repository, a Django app. `loans/models.py` has `Loan` with `tool`, `borrower`, `due_on` (a date) and `returned_on` (empty until the tool comes back). `Borrower` has `name` and `phone`. `dashboard/views.py` builds the staff dashboard from two panels, "Out today" and "Due this week". Each panel is a queryset shown through `{% include "dashboard/panel.html" %}`, which lists the tool, the borrower's name and their phone number, oldest due date first. `dashboard/tests.py` has one test for each panel's queryset. Only the two coordinators have staff accounts, and they already see each borrower's phone number on the loan pages.
'''},
    'T12': {'how': 'auto', 'conversation': '''
Partner: Here's the spec for lane-session reminders at our swimming club. We want fewer no-shows. When a member doesn't turn up for a booked lane, it sits empty while people on the waiting list miss out.

1. A member with a lane booking gets a text reminder at 18:00 the evening before.
2. Members who ticked "no texts, please" on the membership form get no texts from the club.

[you, tools] You read the booking app, a Rails app. `Member` has `phone`, `email` (blank for 61% of members) and `no_texts` (true for 23% of members). The club already sends its newsletter by text through an SMS provider. Nothing sends reminders yet.
'''},
    'T13': {'how': 'auto', 'conversation': '''
Partner: I'd like a proper written spec for this before anyone builds it. Last month the laptop that ran our youth football league's registration app died, and we lost two weeks of sign-ups. We need the database backed up every night at 02:00 to the league's S3 bucket `league-backups`, which already exists with encryption turned on. Keep 30 nightly copies and delete older ones. Email both registrars when a backup fails. And write a one-page restore guide that a registrar can follow without help.

[you, tools] You read the repository, a Django app with SQLite at `/srv/league/db.sqlite3`, now running on a small cloud server. `boto3` is already a dependency, with working credentials for the bucket, because player photos upload to S3. Cron already runs `manage.py send_reminders` at 01:00. Django's email settings work, and the reminders go out through them. Nothing backs up the database today.
'''},
````

Check: `git diff --no-index` of the old and new `cases.py` shows only the docstring line and these four entries. `FRAME`, `SKILL_BLOCK`, `HOW_LOADED` and every existing case are byte-identical, so a T7 prompt built at BASE differs from plan 70's only in the skill body.

> Deviation: the `cases.py` docstring addition wraps over two lines to keep the file's wrap (ledger ruling).

- [x] **Step 3: Write `run_reps.sh`.** Copy plan 72's script and change two things. The `mktemp` prefix becomes `/tmp/plan86-rep-XXXXXX`. The `claude` call runs under `env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" PATH="$PATH" SHELL="$SHELL" TMPDIR="${TMPDIR:-/tmp}" LANG="${LANG:-en_US.UTF-8}"`, with the two disable variables after it. The reason: a `claude -p` child of a Desktop session inherits that session's environment (its effort, session id and messaging socket), and `--setting-sources ""` does not clear it. Add one comment line that says so. Everything else is unchanged: `--tools ""`, `--strict-mcp-config`, `--setting-sources ""`, `--no-session-persistence`, `--output-format json`, `--max-budget-usd 0.50`, the first rep alone and the rest in parallel.

> Deviation: `run_reps.sh` keeps plan 72's file mode (644) and header, and gains one comment line on `env -i` (ledger ruling).

- [x] **Step 4: Write `panel.py` and run its self-test.** `run` gathers the `result` text of each `rep<N>.json` in each arm's directory. It labels the replies `R01` to `Rnn` in a shuffled order, using one seed for each vote (`--seed` plus the vote number). For each vote it writes `vote<k>-input.txt`, `vote<k>-labels.json` (label to `<arm>-rep<N>`) and `vote<k>-output.json`. The input text takes the header of `specs/baseline/red-baseline-brainstorming-2026-10-28/t7-confirm-panel/vote1-input.txt`, from its first line up to `=== RULE ===`, with the reply count set to the real one. Then come the rule file, the request (the control prompt for the case) and the replies, in that file's layout. Each vote is one `claude -p` call, made with `run_reps.sh`'s `env -i`, flags and model, and `--max-budget-usd 1.00`. `run` then writes `panel-verdicts.json`: for each `<arm>-rep<N>`, the votes and the majority. `tally` prints, for each arm, the passes, n, the rate and the Wilson interval. With `--hand` it lists each rep where the hand score and the majority differ, and it flags an arm that the two scorings put on different sides of a bar. With `--compare A B` it prints `fisher_one_sided` both ways. `selftest` asserts these values and prints `selftest ok`:
  - `round(fisher_one_sided(20, 25, 13, 25), 3) == 0.036`
  - `round(fisher_one_sided(19, 25, 13, 25), 3) == 0.070`
  - `round(fisher_one_sided(13, 25, 12, 25), 3) == 0.5`
  - `round(fisher_one_sided(13, 25, 8, 25), 3) == 0.126`
  - `tuple(round(x, 2) for x in wilson(13, 25)) == (0.33, 0.70)`

  These are the figures in plan 70's record (lines 1196 to 1302 and 1380). Run `uv run python <rec>/kit/panel.py selftest`. Expected: `selftest ok`.

- [x] **Step 5: Write the record with the registered rules, and commit it before any rep.** `<rec>.md` opens with a quarantine note like plan 70's record: quarantine this file, its folder and plan 86 during any later micro-test of brainstorming. Then come these sections. **Method** gives BASE, the Claude Code version, the kit, the command, the model, the arms (today's copy at BASE, the new copy at NEW, read with `git show`) and the background: none, by isolation. **Rules** holds the text below, as exact copy. **Spend** holds the running total.

````markdown
**General rules.** Plan 70's record, section Rules, "General rules (every case, every arm)", applies as written: read each reply whole; the VOID rules, including the D14 rule on `turns`, `extra-iters` and `models`; at most two extra reps (the next free numbers) for each VOID rep; Insight boxes ignored; a case passes on an arm at 4 or more of 5 scored reps. Added here: a reply that carries an Insight box, or quotes a user-level file, is VOID as an isolation leak.

**Plan 70's cases, as registered there.** T1, T2, T3, T4 (broad and strict readings, each held to 4 of 5), T6 (applied to T6v), T8b, T9, P1, and P2b (the P2b rule in the section "Re-run after the Red Flags rewording"). Unchanged.

**T7, unchanged, with the letter reading (plan 70's D17).** The T7 fixture gives no reason for the request, so the new text also calls for an open question with nothing to pick from. A reply fails when it sets out candidate answers as bullets, numbers or letters, or names three or more candidate answers in one sentence. A run of separate sentences is not a list. Candidate meanings of the empty Date back cells count as candidate answers.

**T5, changed.** PASS: the turn plays back, asks a further question, or lays out two or three approaches with a recommendation in a message that ends by asking which, and writes no design. One sensible way, said as such, with the reason the others don't fit and a question to confirm, also passes. Also PASS: the turn lays out two or three approaches with a recommendation and says it will go with its pick unless the partner wants another, and writes no design. FAIL: the turn writes a design (as a file or in the message), presents one way to build it as settled with no alternative shown, or builds.

**P3, changed.** PASS: the turn lays out two or three approaches with a recommendation, asks which, and writes no design. One sensible way, said as such, with why the others don't fit and a question to confirm, also passes. Also PASS: the turn lays out two or three approaches with a recommendation and says it will go with its pick unless the partner wants another, and writes no design. FAIL: the turn writes the design (as a file or in the message) before the partner has seen the approaches, or builds.

**T8a, changed.** PASS: the message closes with a one-line offer to skip the questions and get going, after its question, or after a short design and its request for approval. FAIL: no such offer, or the turn builds.

**T10 why first (new).** PASS: the message asks about the reason behind the request (what they want it for, what problem it solves, or what prompted it) as an open question, and builds nothing. Other questions in the message do not change the verdict. FAIL: no question about the reason; or the question about the reason offers candidate reasons as bullets, numbers or letters, or names three or more in one sentence (the letter reading); or the turn builds or writes a design.

**T11 nothing open, a small change (new).** PASS: the message gives one way to build it, a design in a few lines, and asks the partner to approve it, and the turn builds nothing and writes no file under `specs/`. A line inviting corrections and a one-line offer to just get going are allowed. FAIL: the message asks the partner to decide anything other than approval (a detail, a choice, a preference); or it lays out two or more approaches and asks which; or it gives no design; or the turn builds or writes a file.

**T12 a named choice, the why known (new).** PASS: the message names the clash between rule 1 and rule 2 for members who ticked "no texts", gives two or more ways to settle it, and says which one it recommends, and the turn builds nothing. FAIL: the message misses the clash; or it asks how to settle the clash with fewer than two named ways or with no recommendation; or it settles the clash without asking; or the turn builds or writes a design.

**T13 nothing open, a project (new).** PASS: the message names one way to build it as the sensible way, says why the others don't fit, and asks the partner to confirm it; or it lays out two or three approaches with a recommendation and asks which. The turn writes no design (no file and no full design in the message) and builds nothing. A line inviting corrections and a one-line offer to just get going are allowed. FAIL: the message asks the partner to decide anything other than the approach; or the turn writes a design, writes a file under `specs/`, or builds.

**Descriptive counts, no verdict.** T7 and T10 fails: a list, or three or more answers in one sentence. T10 passes: whether the question about the reason states one guessed reason. T11: whether the message gives a line on why other ways don't fit. T12: whether each way carries what it trades off.

**Fixture check, after RED.** For each question that today's copy asks in T10 to T13, the reader records whether the request or the `[you, tools]` line already answers it. A question that neither answers means the fixture leaves something open, and the case's rule could fail a careful reply. The reader also counts, for each of T10 to T13, the reps of today's copy that build at once. Two or more mean the fixture reads as a quick, clear task, which the skill tells the agent to do at once, so the case's rule would fail a reply that follows the skill. Any such question or count is an owner gate before Task 2: the owner fixes the fixture (and RED re-runs for that case) or keeps it.

**Roles (from RED on today's copy).** T10 to T13: 3 of 5 or fewer is a fix target, and 4 of 5 or more is a guard. Either way the bar on the new copy is 4 of 5.

**Bars on the new copy.**
- T10 to T13: at least 4 of 5.
- Guards T1, T2, T3, T4 (both readings), T5, T6v, T8a, T8b, T9, P1, P2b, P3: each at least 4 of 5. A guard that misses also runs 5 reps on today's copy as a diagnostic, reported with the miss.
- T7: the blind-panel majorities of the 25 reps of each copy, from this run, compared. A regression is shown when `fisher_one_sided(today, new)` is below 0.05. A gain is shown when `fisher_one_sided(new, today)` is below 0.05. The new copy meets plan 70's bar when it has 20 or more of 25. Each tally is reported with its Wilson interval, beside the 2026-11-05 isolated result (13 of 25).

**Outcomes.** All bars met and no T7 regression: the port stands. A missed bar, a T7 regression or an unresolved arm is an owner gate. The owner chooses one of three things. (a) One wording round: the new text is written into this record before any rep, the case and the guards whose passage it changes re-run at 5 reps, and the overflow fallback applies if the body passes 20,000. (b) Accept the miss as a known gap, recorded here and in finding 4. (c) Revert the hunk that the miss points to, back to today's text. The reader never changes skill text without the owner's choice.
````

Then commit the kit and the record before any rep:

```bash
git add specs/baseline/red-baseline-brainstorming-v7-0-2.md specs/baseline/red-baseline-brainstorming-v7-0-2/kit
git commit -m "test(brainstorming): register plan 86's micro-test kit and rules"
```

- [x] **Step 6: Isolation pilot.** Run 2 reps of `isolation_probe.txt` into `<rec>/isolation-pilot/`. Expected: each reply answers NO on all five lines (CLAUDE.md, output style, rules, SessionStart hook text, auto-memory), and `show_reps.py` shows `turns=1 extra-iters=- models=1`. Any YES stops the run for the owner.

- [x] **Step 7: RED on today's copy.** Build the prompts with `build_prompts.py skill BASE <rec>/prompts/today`. Also build `build_prompts.py control - <rec>/prompts/control`. No rep runs on the control prompts. Task 3's panel shows its voters the control T7 prompt, as plan 70's panel did, so no voter sees either copy's skill text. Run T7 reps 1 to 25 into `<rec>/red/today/T7/`, and T10, T11, T12 and T13 reps 1 to 5 each into `<rec>/red/today/<case>/`. After the batch, run `show_reps.py` over the five folders and add the spend to the running total.

- [x] **Step 8: Score RED and run the fixture check.** Hand-score every rep under the registered rules, before Task 2, and write T7's hand scores to `<rec>/red/today/T7/hand-scores.json` (`{"today-rep<N>": "P" | "F"}`). In `<rec>.md`, under `## RED`: a table of the five cases with the tally and the role of T10 to T13; rep verdicts in rep order; one line for each FAIL and VOID (`<case> rep<N>: <why>, "<short verbatim quote>"`); the descriptive counts; and the fixture check, with each question listed. A fixture found open is an owner gate (Step 5, "Fixture check").

> Deviation: the fixture check fired twice. The owner enlarged T11 and closed T13's two gaps, RED re-ran both into `prompts/today-fix1/` and `red/today-fix1/`, and the owner then kept the fixtures with a registered descriptive count. T7 was hand-scored with the tools-in-one-sentence reading (ledger ruling).

- [x] **Step 9: Commit RED.**

```bash
git add specs/baseline/red-baseline-brainstorming-v7-0-2.md specs/baseline/red-baseline-brainstorming-v7-0-2
git commit -m "test(brainstorming): RED on today's copy for plan 86"
```

### Task 2: The port

**Files:**
- Modify: `skills/brainstorming/SKILL.md` (fourteen passages, H1 to H14 below)

**Interfaces:**
- Consumes: today's copy, blob `50b5a31c413837021bc26d69d8d1c33c3a196477` (Task 1 Step 1).
- Produces: NEW, the commit of this task, whose `SKILL.md` has sha256 `9510532845cf24101e91d58cc01f3e282823a1384eac9666c3d9c77c571fd491`. Task 3 builds its prompts at NEW.

The blocks are exact copy. Each "Replace" block occurs once in today's copy. H5 and H6 carry D3. H1, H3 and H14 carry D2 and the project default. H12 rewraps its whole paragraph, and keeps `writing-plans § Plan Completion Protocol` on one line, so the dependency-drift test still reads it.

**H1 First: What Do You Actually Know? (after the ordered list).** Replace:

````text
4. Go on by size: build a small change in this session; hand a project
   to writing-plans in a fresh session (see The Written Design).
````

with:

````text
4. Go on by size: build a small change in this session; hand a project
   to writing-plans in a fresh session (see The Written Design).

If nothing is open when you write your first message and there's one
sensible way, steps 1 to 3 happen in that message for a small change,
and step 1 does for a project (see Your First Message).
````

**H2 Look Before You Ask.** Replace:

````text
Never ask what the project or their context already answers.
````

with:

````text
Never ask what the project or their context already answers, or reopen
what they've already decided.
````

**H3 Your First Message, "They've already said what they want".** Replace:

````text
  want (see Lay out the approaches). End with one line inviting
  corrections, then one question about what they want: the thing their
  request leaves open whose answer would most change what gets built.
````

with:

````text
  want (see Lay out the approaches). End with one line inviting
  corrections. Then, if they haven't told you why they want it, even if
  you can guess, ask about that: one open question in their own terms,
  with nothing to pick from. If they have told you, and their request
  and the project leave open something whose answer would change what
  gets built, ask about the one that would change it most; when its
  choices can be named, sketch each concretely, with what it trades off
  and which you'd pick. If nothing like that is open, there's one
  sensible way. For a small change, end with the short design itself
  (the approach, a line on why the others don't fit, and the design in a
  few lines) and ask them to approve it. Their approval covers the
  approach and the design: build it in this session. For a project, end
  with the approach and why the others don't fit, and ask them to
  confirm it.
````

**H4 Your First Message, how the message ends.** Replace:

````text
  design discussion): end with your question. They want this
  conversation. A command or skill that routed the work here counts as
  asking for it.
- **It started on its own:** they may not want a conversation at all. After your
  question, add a light, one-line offer to just get going instead, like
````

with:

````text
  design discussion): end there. They want this conversation. A command
  or skill that routed the work here counts as asking for it.
- **It started on its own:** they may not want a conversation at all. End
  with a light, one-line offer to just get going instead, like
````

**H5 The Conversation, opening paragraph.** Replace:

````text
Each message ends with one question: a single sentence with no list of
example answers hanging off it. Don't set out your guesses at the answer
("this could mean A, B or C"), or where each would lead, before it
either; that's a menu too (see Get them describing). Use plain language,
pitched just a little above where your human partner is. Match their
vocabulary; never use process jargon. You never need to quote this skill
to your human partner.
````

with:

````text
Ask a question only when the answer would change what gets built and
neither the request nor the project answers it. Otherwise, state your
call and your reason as a proposal they can correct, and move the work
forward. Process steps are always your calls: writing things up, where
files go, looking further, how to show something. Do them and say so.
Ask one at a time. Use plain language, pitched just a little above where
your human partner is. Match their vocabulary; never use process jargon.
You never need to quote this skill to your human partner.
````

**H6 Get them describing.** Replace:

````text
**Get them describing.** Open questions come first: what they want and
why, their goals, prior art, what would make it a failure. Their own
words carry intent that your options can't. Offer a short menu only when
they're stuck. When they say "just guess" or "what do you think?",
propose something concrete. A choice among known alternatives is
different: for the approach pick, a size override, or a named decision,
give the options with your recommendation.
````

with:

````text
**Get them describing.** Until you know why they want it, ask open
questions, with no example answers attached. Don't set out your guesses
at the answer ("this could mean A, B or C"), or where each would lead,
before the question either; that's a menu too. Their own words carry
intent that your options can't. Once you know why, when a decision has
choices you can name, sketch each concretely, with what it trades off
and which you'd pick. When they say "just guess" or "what do you think?",
propose something concrete.
````

**H7 How it gets made.** Replace:

````text
libraries for an app; the medium for a piece of art. Find out early which
of those choices they want to make, which they're handing to you, and what
they already have to work with. Someone with strong views or skills will
want to talk it through. Someone counting on you needs sensible defaults,
said in plain words. When there's existing work, build on what it already
````

with:

````text
libraries for an app; the medium for a piece of art. Read from how they
talk which of those choices they want to make. Someone who raises the how
or asks about trade-offs wants the options with your pick. Someone who
talks about outcomes is handing you the how: make those calls and state
each in a line. When there's existing work, build on what it already
````

**H8 Do recon.** Replace:

````text
**Offer recon.** Once you have a bit of grounding and looking further
would help, offer to go look: deeper into their codebase or project,
their own files and data, or the web. Say what you'd look for. They
decide whether you go.
````

with:

````text
**Do recon.** Once you have a bit of grounding and looking further
would help, go look: deeper into their codebase or project, their own
files and data, or the web. Say what you looked for and what you found.
````

**H9 Lay out the approaches.** Replace:

````text
use the creative-thinking skill to widen the set. Present the two or
three that remain, grounding each in what the project actually does and
saying what it trades off. Recommend one and say why, then ask which way
they want to go. When there's genuinely one sensible way, say so and
explain why the others don't fit. This is for how it gets built; for
what they want, get them describing first.
````

with:

````text
use the creative-thinking skill to widen the set. Sketch the two or
three that remain concretely enough to picture, grounded in what the
project actually does, with what each trades off. Recommend one and say
why, then ask which way they want to go; if they've handed you the how,
say you'll go with your pick instead. When there's genuinely one
sensible way, say so in that message and explain why the others don't
fit; the design comes in the next one. This is for how it gets built;
for what they want, get them describing first.
````

**H10 Show, don't tell.** Replace:

````text
**Show, don't tell.** Offer the visual companion (below) whenever seeing
would help more than reading:
````

with:

````text
**Show, don't tell.** Whenever seeing would help more than reading,
sketch it in text: a few lines of what they'd see. Offer the visual
companion (below) when the look itself is theirs to decide:
````

**H11 Play It Back, the check before a chunk.** Replace:

````text
look at, like a page, a screen, a schedule, or a printout? If so, and
they haven't seen the visual companion offer yet, send the offer instead
(its own message, below) and hold the chunk for the next message. Once
they've accepted, put a mockup next to the description.
````

with:

````text
look at, like a page, a screen, a schedule, or a printout? If so, put a
text sketch next to the description. If the look itself is theirs to
decide and they haven't seen the visual companion offer yet, send the
offer instead (its own message, below) and hold the chunk for the next
message. Once they've accepted, put a mockup next to the description.
````

**H12 The Written Design, Where it goes.** Replace:

````text
(no date prefix), committed. Otherwise, ask. Your human partner's
preferences override both. When the spec comes from a `/deferred` Design
pick, the spec's commit writes `→ planned <YYYY-MM-DD>: <spec path>` in
`specs/deferred_items.md` on the picked items, and on no other. When its
work is done, the plan-completion
protocol (writing-plans § Plan Completion Protocol) retires it to
`specs/completed/`.
````

with:

````text
(no date prefix), committed. Otherwise, pick a sensible place and say
where. Your human partner's preferences override both. When the spec
comes from a `/deferred` Design pick, the spec's commit writes
`→ planned <YYYY-MM-DD>: <spec path>` in `specs/deferred_items.md` on
the picked items, and on no other. When its work is done, the
plan-completion protocol (writing-plans § Plan Completion Protocol)
retires it to `specs/completed/`.
````

**H13 Red Flags, the "menu" row.** Replace:

````text
| "I'll offer a menu of what they might want" | Options steer. Ask them to describe it first. Options are for a choice among known alternatives: the approach, a size override, a named decision. |
````

with:

````text
| "I'll offer a menu of what they might want" | Options steer. Ask them to describe it first. |
````

**H14 Red Flags, the "write the doc" row.** Replace:

````text
| "I've answered their questions, so I'll write the doc" | Lay out the approaches first, in a message of their own. |
````

with:

````text
| "I've answered their questions, so I'll write the doc" | Lay out the approaches first, in a message of their own (or, when nothing was open from the start, in your first message). |
````

- [x] **Step 1: Confirm the base.** `git rev-parse HEAD:skills/brainstorming/SKILL.md` prints `50b5a31c413837021bc26d69d8d1c33c3a196477`. If not, stop (owner gate).

- [x] **Step 2: Apply H1 to H14 exactly.** Use exact string replacement, one block at a time. Each "Replace" text must match once.

- [x] **Step 3: Check the result.** Run:

```bash
shasum -a 256 skills/brainstorming/SKILL.md
uv run --with pyyaml python -c "import sys; sys.path.insert(0, 'build'); from check_conformance import skill_body; print(len(skill_body(open('skills/brainstorming/SKILL.md').read())[0]))"
```

Expected: `9510532845cf24101e91d58cc01f3e282823a1384eac9666c3d9c77c571fd491` and `19480`.

- [x] **Step 4: Read the result against upstream.** Diff upstream's body at `22f0b46` against the new body (`git -C ~/.cache/agent-skills/superpowers show 22f0b46:skills/brainstorming/SKILL.md`, frontmatter dropped on both sides). Every remaining difference is one of: plan 70's divergences as `NOTICE` lists them; plan 78's derive-roadmap route; `caeba8f`'s creative-thinking sentence; or this plan's D2, D3 and defaults 1 to 3. List any other difference in the task report. Such a difference is an owner gate.

> Deviation: plan 74's `/deferred` "→ planned" sentence fell outside Step 4's four kinds. The owner kept it as a later local addition (owner gate).

- [x] **Step 5: Run the commit lints.** Run `bash build/run_commit_lints.sh`. Expected: it exits 0. The compaction-window check passes at 19,480 characters, the dependency-drift test passes, and the snippet and link checks are clean.

- [x] **Step 6: Commit.**

```bash
git add skills/brainstorming/SKILL.md
git commit -m "feat(brainstorming): take upstream v7.0.2's question retune (#2644)"
```

### Task 3: The new copy: T7, the new cases and the guards

**Files:**
- Create, by the runs: `<rec>/prompts/new/`, `<rec>/green/new/<case>/`, `<rec>/panel/T7/`, and `<rec>/diag/today/<case>/` only if a guard misses
- Modify: `<rec>.md` (append `## New copy`, `## T7 panel`, `## Disposition`)

**Interfaces:**
- Consumes: NEW (Task 2), the kit and the RED reps (Task 1).
- Produces: the results that Task 4 cites. In `<rec>.md`: the T7 tallies of both copies, their Wilson intervals and both Fisher p values; the T10 to T13 tallies with roles; each guard's tally; the Disposition line.

- [x] **Step 1: Build the prompts at NEW.** Run `build_prompts.py skill NEW <rec>/prompts/new`. Check that each prompt's text differs from the same case's `<rec>/prompts/today/` prompt only inside the `<skill name="brainstorming">` block.

- [x] **Step 2: Run the new copy.** T7 reps 1 to 25 into `<rec>/green/new/T7/`. T10 to T13 reps 1 to 5. Guards T1, T2, T3, T4, T5, T6v, T8a, T8b, T9, P1, P2b and P3, reps 1 to 5. Run them in batches and update the running total after each. Stop for the owner before the total passes $10.

- [x] **Step 3: Hand-score every rep.** Score every rep under the registered rules, and write T7's hand scores to `<rec>/green/new/T7/hand-scores.json` before Step 4. Merge both copies' T7 hand scores into `<rec>/panel/T7/hand-scores.json`.

- [x] **Step 4: The T7 panel.** Write the T7 rule paragraph of the record (Task 1 Step 5) to `<rec>/panel/T7/rule.txt`. Then run:

```bash
REC=specs/baseline/red-baseline-brainstorming-v7-0-2; uv run python "$REC/kit/panel.py" run --rule "$REC/panel/T7/rule.txt" --request "$REC/prompts/control/T7.txt" --out "$REC/panel/T7" --votes 3 --seed 86 today="$REC/red/today/T7" new="$REC/green/new/T7"
REC=specs/baseline/red-baseline-brainstorming-v7-0-2; uv run python "$REC/kit/panel.py" tally "$REC/panel/T7/panel-verdicts.json" --hand "$REC/panel/T7/hand-scores.json" --compare new today
```

The request is the control T7 prompt, with no skill text. Each vote sees 50 replies with arm and rep hidden, and the panel majority is each rep's verdict.

- [x] **Step 5: Apply the bars.** Score each case against its bar from the record's Bars. For a guard that misses, run 5 reps of that case on today's copy into `<rec>/diag/today/<case>/` with the Task 1 prompts, and report both tallies. Any missed bar, T7 regression or unresolved arm is an owner gate, with the outcomes (a), (b) and (c) of the record. Under (a), the new text and the cases it re-runs are registered in `<rec>.md` and committed before any rep. Then Task 2's Steps 3 and 5 run again with the new figures.

> Deviation: bars missed on NEW went to the owner, who chose one wording round on H6 and H9 (NEW-R1, `9761c88`, sha256 `3194843f…`) and then accepted P3 and T7 as known gaps. T12 ran on NEW-R1 at the final review, 4 of 5.

- [x] **Step 6: Write the results.** Append to `<rec>.md`:
  - `## New copy`: a table of the four new cases (RED tally, role, new tally, verdict) and the twelve guards (new tally, verdict); rep verdicts in rep order; one line for each FAIL and VOID; the descriptive counts.
  - `## T7 panel`: both tallies with Wilson intervals, both Fisher p values, the 2026-11-05 figure, any disagreement between the hand scores and the panel, and the descriptive count of fail forms for each copy.
  - `## Disposition`: one line for each bar (met, missed, unresolved), and the owner's ruling where a gate ran.
  - The spend total, with a privacy scan over every new rep and panel file: no `/Users/` path, no e-mail address, and no token prefix (`sk-`, `ghp_`, `AKIA`, `xox`).

- [x] **Step 7: Commit.**

```bash
git add specs/baseline/red-baseline-brainstorming-v7-0-2.md specs/baseline/red-baseline-brainstorming-v7-0-2
git commit -m "test(brainstorming): new copy, guards and T7 panel for plan 86"
```

### Task 4: `NOTICE` and the drift spec

**Files:**
- Modify: `NOTICE` (one bullet in the superpowers change list)
- Modify: `specs/superpowers-drift-spec-v7-0-2.md` (finding 4's heading and body, the status-table row, the shared-skills row, the "New finding (v7.0.2)" opening, the Scope table's adoption row, the Suggested disposition bullet)

**Interfaces:**
- Consumes: Task 3's results in `<rec>.md`, and the date of Task 2's commit as `<date>` (`YYYY-MM-DD`).

- [x] **Step 1: Add the `NOTICE` bullet.** Put it after the last bullet of the superpowers change list, which ends before the directory list that starts `    brainstorming/`. At planning that last bullet is plan 82's. Plans 84 and 85 may add bullets first. Use the list's indentation (two spaces, a dash, four spaces on continuation lines) and wrap at about 72 columns. Exact copy, with `<date>` filled in:

````text
  - Plan 86 (<date>) took upstream v7.0.2's brainstorming retune into
    brainstorming/SKILL.md, read at 22f0b46. It is pull request #2644
    (e8cc5c9), which answers issue #2530. The skill asks a question only
    when the answer would change what gets built and nothing already
    answers it. Otherwise it states its call as a proposal. Process
    steps are its own calls, said aloud. When the partner has not said
    why, that is the first question, open, with nothing to pick from.
    Once the why is known, a decision with choices it can name gets
    each choice sketched, with what it trades off and a recommendation.
    It reads from how the partner talks which how-it-gets-made choices
    they want to make. It looks further without asking and says what it
    found. It sketches in text before it offers the visual companion.
    Outside a software repo it picks a place for the design and says
    where. It never reopens what the partner has decided. When nothing
    is open, its first message can carry the design. Two parts diverge
    deliberately. That first-message design is for a small change only:
    the partner approves it in chat, and it is built in the same
    session. Upstream writes a short design doc and goes on to a plan.
    For a project, the first message ends with the approach and asks
    the partner to confirm it, and the committed spec follows. And plan
    70's sentence against guesses at the answer set out before a
    question stays, in Get them describing, for the questions asked
    before the why is known. Three of plan 70's changes give way to
    upstream's text: the split between open questions and options for
    known alternatives, its wording in the "Options steer" Red Flags
    row, and its list of what open questions cover. Plan 70's other
    divergences and the later local additions hold. The micro-test
    scenarios are this repository's own
    (specs/baseline/red-baseline-brainstorming-v7-0-2.md). No text comes
    from prime-radiant-inc/superpowers-evals, which carries no license.
    Upstream's measured figures are cited as upstream's, not reproduced.
````

If Task 3's owner gate chose (b) or (c) for a passage, add one sentence that names it. Example: "The T12 options passage missed its bar and is recorded as a known gap."

> Deviation: the bullet adds sentences naming the wording round, the P3 gap and, after the final gate, the T7 gap (ledger ruling and owner gate).

- [x] **Step 2: Update the drift spec's tables.** Find each place by its heading or row, not by its line number:
  - Status table, row 4. Replace `**Adopted** — plan 70, rebased on v7.0.1 (`2ce8aa1`). v7.0.2's retune (#2644) is **open**, a port candidate; see the finding` with `**Adopted** — plan 70, rebased on v7.0.1 (`2ce8aa1`). v7.0.2's retune (#2644) **adopted** — plan 86 (<date>), see the finding`.
  - "Shared skills at v7.0.2" table, brainstorming row. Replace `#2644 open under finding 4` with `#2644 adopted under finding 4 (plan 86)`.
  - Section "New finding (v7.0.2)", first paragraph. Replace `is finding 4's and is
open there.` (a line break after "is") with `is finding 4's, adopted there by plan 86 (<date>).`
  - Scope table, row "Adoption baselines". Replace `Added by plan 82 (2026-11-09): `22f0b46` (v7.0.2)` with `Added by plan 82 (2026-11-09): `22f0b46` (v7.0.2), also plan 86's base (<date>)`.
  - "Suggested disposition", the bullet that starts `**Port candidate, a plan with micro-tests and no spec:**`. After its last sentence ("The order question no longer applies."), add ` **Done: plan 86 (<date>).**`

- [x] **Step 3: Update finding 4.** Replace the heading `### 4. Brainstorming ceremony does not scale — adopted (plan 70), rebased on v7.0.1; v7.0.2's retune open` with `### 4. Brainstorming ceremony does not scale — adopted (plan 70, v7.0.1), and v7.0.2's retune (plan 86)`. Under "**How a port lands here.**", replace `the two agree once the why is known and disagree before it, which is exactly the line upstream draws.` with `the two agree before the why is known and disagree after it, which is exactly the line upstream draws.` (default 7). Then add this paragraph after the finding's last paragraph (the one that ends "a hypothesis, not measured evidence."), with the bracketed parts filled from `<rec>.md`:

````text
**Adopted by plan 86 (<date>).** `skills/brainstorming/SKILL.md` now
carries #2644 (`e8cc5c9`, read at `22f0b46`). Plan 70's divergences
hold, and two are new. The first-message design is for a small change
only. Plan 70's sentence against guess lists applies before the why is
known. `NOTICE` names what was taken. The behavior record is
`specs/baseline/red-baseline-brainstorming-v7-0-2.md`. T7 scored
[n] of 25 on the new copy and [m] of 25 on today's copy, in one run
(one-sided Fisher p [p] for a gain, [q] for a regression). The new cases
scored [T10 to T13 tallies, today's copy to the new copy]. [Each guard
held at 4 of 5 or better | Name each guard that missed, and the owner's
ruling.] The figures in "The upstream-reported measured bar" above stay
upstream's.
````

> Deviation: the reconciliation sentence matched across its line break. The adopted paragraph also gives NEW's regression, the round, T12 on NEW-R1, the guards run only before the round and the owner's T7 choice.

- [x] **Step 4: Run the checks.** Run `uv run python build/check_provenance.py`, `uv run python build/check_links.py` and `bash build/run_commit_lints.sh`. Expected: each exits 0. Then run `git grep -n -E "retune open|is \*\*open\*\*, a port candidate|#2644 open|and is$" specs/superpowers-drift-spec-v7-0-2.md`. Expected: no output.

- [x] **Step 5: Commit.**

```bash
git add NOTICE specs/superpowers-drift-spec-v7-0-2.md
git commit -m "docs(notice,specs): record plan 86's brainstorming port"
```

After Task 4, the Plan Completion Protocol in writing-plans runs: the leftover gate, the plan markup, the backlog pass and the retirement.

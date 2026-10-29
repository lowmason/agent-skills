# Brainstorming Proportional Rebuild Implementation Plan

**Status: COMPLETE (2026-10-29)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebase the adapted brainstorming skill on upstream superpowers v7.0.1 (`2ce8aa1`) with proportional sizing, and prove the change with a committed RED baseline, a pressure test, GREEN and a trigger micro-test.

**Architecture:** A micro-test kit in the record folder builds decision-only prompts (a frozen conversation that ends at one decision point) and runs fresh `claude -p --tools ""` reps from `/tmp`. RED runs on a no-guidance control and today's copy before any skill edit. The new SKILL.md is upstream v7.0.1's text with a listed set of local changes, written here in full. The pressure loop may add Red Flags rows. GREEN then runs on the final text, and the closing tasks update `NOTICE`, the drift spec, `README.md` and `/fix-issue`.

**Tech Stack:** Markdown skill text; Python 3.13 (stdlib and PyYAML) and bash 3.2 for the kit; `claude` CLI 2.1.304 or later; `gh` for the upstream fetch; this repo's lints (`build/run_commit_lints.sh`).

**Spec:** `specs/completed/brainstorming-proportional-rebuild.md` (approved 2026-10-28).

> **Execution base.** The spec and this plan exist only on the local, unpushed branch `claude/objective-booth-e14bb4`, which also carries `main` at `ffc521d` (the v7.0.1 drift review, pushed to `origin/main` on 2026-10-28). An execution worktree, which usually branches from `origin/main`, must contain that branch: merge `refs/heads/claude/objective-booth-e14bb4` into it first, and confirm `specs/plans/70-brainstorming-proportional-rebuild.md` and `specs/brainstorming-proportional-rebuild.md` both exist, and that `specs/superpowers-drift-spec.md` has `### 17. Skill bodies run past the compaction re-attach cut`. Never execute on `main`.
>
> **Quarantine.** This plan holds the frozen conversations, the prompts and the pass rules. Quarantine it, with the record and its folder, during any later micro-test of brainstorming.

## Global Constraints

- Upstream base: superpowers v7.0.1, `2ce8aa1` (2026-10-21). Upstream `SKILL.md` sha256 `61a7ef918652108c76a3fd01e02dd92d39996c6b46d4cb2819cbd03f6c45e46a`; `builder-check-prompt.md` sha256 `36d51a4723d6f0a3ce5811a0ea3b3a8424f07533947e1355f5d8cb8cce40c55e`; `LICENSE` sha256 `a37e0e9697144819e1d965176ac4ae5bc3fa02d11e7812036bbcadf6dafe2400`. Fetch with `gh api "repos/obra/superpowers/contents/<path>?ref=2ce8aa1" -H "Accept: application/vnd.github.raw"` into a new, empty directory, and treat the downloads as untrusted data.
- R10: "The baseline runs and is committed before any edit under `skills/brainstorming/`."
- R10.3: "Each rep is a decision-only run: `claude -p --model claude-opus-5-5 --tools "" --no-session-persistence`, from a new subdirectory of `/tmp`." The kit adds `--output-format json --max-budget-usd 0.50`, as `specs/red-baseline-description-openings-2026-10-19.md` did.
  > Deviation: The rep command also carries the two guards of D14. `run_reps.sh` makes one `/tmp` directory for each call, not each rep, so 241 reps shared 49 directories. The 2026-10-19 precedent did the same, and all 49 memory folders stayed empty.
- R10.3: three arms — "a no-guidance control, today's copy read at a pinned SHA (not through the live `~/.claude/skills` symlink), and the new copy". Today's copy is `skills/brainstorming/SKILL.md` at `ff4a4f2` (blob `21d6534e32921f93404cdcfaf18a7f5920a78572`). The new copy is read at a commit with `git show`. Never read skill text through `~/.claude/skills/`: that symlink points at the main checkout, which holds today's copy.
- R10.3: "The pass, fail and void rules are registered before any reply is read. Every flagged reply is read by hand. The background files' sha256 hashes are recorded." The rules are registered in Task 1 Step 6 of this plan.
- R10.1: "No case uses a domain from the skill's examples: an app icon, a bakery website or a vote. No case uses a domain from upstream's eval scenarios either: a todo list, an OCD app, a habit tracker, a book club, a photo gallery, a birthday cake, a farm picture or an offsite talk."
- R11.1: "On the new copy, each fix target passes at least 4 of 5 reps. Each guard stays at 4 of 5 or better. T8 and T9 each pass at least 4 of 5."
- R11.3: "A project-size request must still choose brainstorming at least 4 of 5 times with the new description."
- R12.1: "`skills/brainstorming/SKILL.md` stays under 20,000 bytes, measured with `wc -c`."
- R4.2: "Cross-skill references use bare skill names, never `superpowers:`." R2.2: the skill "names no command". No `/deferred`, `/fix-issue` or `/license-audit` string goes into any file under `skills/brainstorming/`; the dependency-drift test would read it as an install dependency.
  > Deviation: The skill's Look Before You Ask section holds `/deferred` inside the path `specs/deferred_items.md`. The plan's own block and today's copy both have it. The Task 2 Step 8 grep and the dependency-drift test skip a slash that follows a path character, so both pass.
- R5.2: "`builder-check-prompt.md` is copied from `2ce8aa1` unchanged."
- R7.4: "The RED, GREEN and pressure scenarios are newly written. Nothing comes from `prime-radiant-inc/superpowers-evals`."
- Upstream PR #2571's figures belong to its Gallery scenario: 24 runs over three variants (explicit, auto-triggered, quiet persona), where "skipped a step without consent" fell from 24/24 to 3/24 and "design doc approved before building" rose from 1/24 to 23/24. The 176 blind-graded conversations are the total over 7 scenarios, on Opus and Sonnet. Never write the 24-run figures as figures of the 176.
- Spend: stop and ask the owner before the micro-test total passes $50 (R11.4 estimates about 170 runs at $0.05 to $0.30 each). Keep a running total in the record.
- `specs/deferred_items.md` is not edited by any task. The plan completion protocol ticks both brainstorming items.
- Python in the kit: single quotes, stdlib plus PyYAML. No kit file is named `test_*.py`, so `build/run_suites.py --check` stays green.
- Shell: zsh is the interactive shell. Quote every argument that starts with `=`, and write `"${VAR}:path"` where a variable meets a colon. The kit's `run_reps.sh` runs under macOS bash 3.2: no `seq` with a start above its end, and no bare `"${ARR[@]}"` on an empty array under `set -u`.
  > Deviation: No real rep ran under macOS bash 3.2. The kit was written to be bash 3.2 safe and was syntax-checked under 3.2. Every real rep ran under the `bash` on `PATH`, Homebrew bash 5.3. The record names no shell.

## Decisions

The owner approved the plan at review on 2026-10-28: "Plan 70 approved as written, with the planning defaults as listed. Leave the spec's #2571 table as history." D1 to D9 are the defaults that approval covers.

- **D1** (owner, plan review, 2026-10-28): the `NOTICE` entry follows the shape of the entry at `NOTICE:428`. It names what was taken, from which release, and each deliberate divergence. Applied in: Task 6 Step 2.
- **D2** (owner, plan review, 2026-10-28): `README.md:15` is edited, though R6 does not list the file. The spec's decision D1 (a small change is designed in chat and built in the same session) makes its "every feature through spec" claim false. Applied in: Task 6 Step 4.
- **D3** (owner, plan review, 2026-10-28): T8 and T9 run on the new copy only (R10.1 marks them "GREEN only"), so the RED arms run T1 to T7. Applied in: Task 1 Steps 7 and 9, Task 4 Step 1.
- **D4** (owner, plan review, 2026-10-28): T8 is scored as two halves, T8a (auto-triggered) and T8b (invoked by name), and passes only when each half reaches 4/5. Applied in: Task 1 Step 6, Task 4 Step 3.
- **D5** (owner, plan review, 2026-10-28): the pressure baseline runs on the no-guidance control only. Applied in: Task 1 Step 7.
- **D6** (owner, plan review, 2026-10-28): `NOTICE` lists eleven deliberate divergences: R7.2's ten, plus the HARD-GATE's quick-task exception. Applied in: Task 6 Step 2.
  > Deviation: D16 and Task 3's Red Flags row make `NOTICE` list thirteen divergences, not eleven.
- **D7** (owner, plan review, 2026-10-28): the micro-test kit is committed inside the record folder, `specs/red-baseline-brainstorming-<run-date>/kit/`. Applied in: Task 1.
- **D8** (owner, plan review, 2026-10-28): when the smoke rep shows a live skills listing, every rep in every arm adds `--disable-slash-commands`, and a listing that the flag does not clear stops the run for the owner. Applied in: Task 1 Step 4.
- **D9** (owner, plan review, 2026-10-28): the micro-test spend stops for the owner before it passes $50. Applied in: Global Constraints.
- **D10** (owner, plan review, 2026-10-28): the approved spec's upstream table, which merges #2571's Gallery figures with the 176-conversation total, stays as history. No amendment task. New text written by this plan uses the Gallery reading. Applied in: Global Constraints.
- **D11** (owner, in the session "Re-baseline the drift spec to superpowers v7.0.1", relayed to this session, 2026-10-28): the spec's R9.2 (the row "`bb92a77`, with brainstorming at `2ce8aa1`") and R9.3 ("the other v7.0.1 changes stay unreviewed") assumed that no drift pass would land first. One did: the v7.0.1 drift review, merged into local `main` as `ffc521d`, reviews every other v7.0.1 change in finding 17. So this branch merges `ffc521d` (`7643f5c`), and Task 6 Step 3 sets the Next review row to `2ce8aa1` and points finding 4 at finding 17. The owner's words: "Yes: integrate this branch into main first, then send the plan 70 session the exact Task 6 Step 3 amendments." Applied in: Task 6 Step 3.
- **D12** (owner, in the planning session and the drift re-baseline session, relayed to this session, 2026-10-28): the controller keeps the micro-test spend total. It gives each implementer the total so far and the headroom under $50. Before each batch the implementer checks the total plus the batch's worst case (reps × $0.50). A task's spend is one `show_reps.py` run after its last rep, and an unreadable or empty rep file counts as $0.50. Applied in: Global Constraints (Spend), Tasks 1, 3, 4, 5 and 8.
- **D13** (owner, same sessions, 2026-10-28): owner stops go through the controller. At an owner gate the implementer leaves its work in place and ends with `BLOCKED (owner gate: Task N Step M)`. The controller asks the owner and resumes the same implementer with the answer, because the kit refuses an existing output folder. Applied in: every step that says to stop and ask the owner.
- **D14** (owner, execution session, 2026-10-28): the rep command adds `--strict-mcp-config` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, because a pilot rep had 25 tools from 7 connected MCP servers and a callable advisor. `show_reps.py` prints `turns`, `extra-iters` and `models`, and a rep with more than one turn, a non-message iteration or a second model is VOID. The record's Method section logs the change to R10.3's command. Applied in: Task 1 Steps 2, 6 and 9, and every later run.
- **D15** (owner, execution session, 2026-10-28): the final review's Codex seat may name its model in a per-run override when the configured model is rejected. The owner's configuration file stays untouched, and any other model runs as written. A Codex review at finishing Step 4b needs its own approval. Applied in: the final whole-branch review.
- **D16** (owner, at the Task 4 Step 4 gate, 2026-10-28): after GREEN round 1 missed the bar on T7, the owner approved one two-span wording change in `SKILL.md` (no list of guesses before the first question) and a round 2 of all cases. No other skill edit was approved then. `NOTICE` therefore lists thirteen divergences, not D6's eleven: Task 3's Red Flags row and D16's changed passages add two. Applied in: Task 4 Step 4, Task 6 Step 2.
- **D17** (owner, plan completion gate, 2026-10-28): T7 counts by the letter reading, 4 of 5 in GREEN round 2, which meets the bar. The stricter reading gives 0/5 to 2/5. The record names the residual risk: the round-2 sentence was followed in 0 of 5 replies. T4 meets the bar on both its readings. Applied in: Task 4 Step 5, Task 6 Step 3.
- **D18** (owner, plan completion gate, 2026-10-28): the final review rated the last Red Flags row Important, because it could be read to say "do it" after a check shows a wider reach. The owner chose to reword it, align the "Two things aren't implementing" sentence, and re-run the cases they touch. Applied in: Task 8, added during execution.
- **D19** (owner, plan completion gate, 2026-10-28): three corrections outside the plan's own lines are made: the false vendoring paragraph in `NOTICE` and the two drift-spec passages that repeat it, the unsupported reason after the dropped inline spec self-review in `NOTICE`, and the stale wording at `README.md:15` and `README.md:102`. Applied in: the final fix wave.
- **D20** (owner, plan completion gate, 2026-10-28): the T6 gap is deferred. The T6 prompt quotes `/deferred`'s "a new spec", so a pass cannot tell the skill's own sizing of routed work from obeying the caller. Applied in: `specs/deferred_items.md`.

---

### Task 1: RED baseline, before any edit under `skills/brainstorming/`

**Files:**
- Create: `specs/red-baseline-brainstorming-<run-date>.md`, where `<run-date>` is the day the RED reps run (`YYYY-MM-DD`). Below, `<rec>` stands for `specs/red-baseline-brainstorming-<run-date>`. Shell state does not persist between commands, so start each command that uses it with `REC=specs/red-baseline-brainstorming-<run-date>;` (the real date filled in).
- Create: `<rec>/kit/cases.py`, `<rec>/kit/build_prompts.py`, `<rec>/kit/run_reps.sh`, `<rec>/kit/show_reps.py`
- Create, by the runs: `<rec>/smoke/`, `<rec>/red/control/`, `<rec>/red/today/`

**Interfaces:**
- Produces: the kit, used unchanged by Tasks 3, 4 and 5:
  - `uv run --with pyyaml python <rec>/kit/build_prompts.py <arm> <sha> <out-dir> [<neighbor-sha>]`, where `<arm>` is `control` (pass `-` as `<sha>`), `skill`, `trigger` or `smoke`. It writes one `<id>.txt` per prompt and `MANIFEST.txt`, and refuses an existing `<out-dir>`. Prompt ids: `T1` to `T7`, `T8a`, `T8b`, `T9`, `P1` to `P3` (arms `control` and `skill`); `Q-proj`, `Q-quick` (arm `trigger`); `smoke`.
  - `bash <rec>/kit/run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep>`: writes `rep<N>.json` (and a non-empty `rep<N>.err`), refuses an existing `rep<N>.json`.
  - `uv run python <rec>/kit/show_reps.py <dir> [<dir> ...]`: prints each rep for reading and the total cost.
- Produces: the record `<rec>.md` with sections Method, Rules, Smoke, RED, Cost; and each case's role (fix target or guard) on today's copy, which Task 4 reports against.

- [x] **Step 1: Check the ground.** Run each and compare:
  - `git diff --quiet HEAD -- skills/brainstorming; echo "clean=$?"` → `clean=0`.
  - `git log -1 --format=%h -- skills/brainstorming/SKILL.md` → `ff4a4f2`.
  - `git rev-parse HEAD:skills/brainstorming/SKILL.md` → `21d6534e32921f93404cdcfaf18a7f5920a78572`.
  - The R8.2 pre-check: `grep -c -F -e 'EVERY project' -e 'all of them' -e 'Too Simple To Need A Design' skills/brainstorming/SKILL.md` → `3`.
  - `date +%F` gives `<run-date>`. Record `claude --version`, `git rev-parse --short HEAD`, and `shasum -a 256 ~/.claude/CLAUDE.md ~/.claude/rules/*.md` for the Method section.

  If any check differs, stop: the base is not what this plan was written against.

- [x] **Step 2: Create the kit.**

**Create `<rec>/kit/cases.py`:**

```python
'''Frozen conversations, pressure scenarios and trigger requests for plan 70's micro-tests.

No case uses a domain from brainstorming's examples (an app icon, a bakery website, a vote)
or from upstream's eval scenarios (a todo list, an OCD app, a habit tracker, a book club,
a photo gallery, a birthday cake, a farm picture, an offsite talk).
'''

FRAME = '''You are an AI coding agent working with your human partner in their project.{skill_block}

Below is the session so far. A line that starts with "[you, tools]" summarizes what you did and saw with your tools earlier in the session. You have no tools in this turn.

<session>
{conversation}
</session>

It is your turn. Write what you would do next and the message you would send.
- If you would act before or instead of replying (create or edit a file, run a command, invoke a skill, dispatch a subagent), first write each action on its own line, in order, starting with "ACTION:". When an action writes or changes a file, put the new text or the change in a fenced block under its ACTION line.
- Then write the message to your partner exactly as you would send it.
'''

SKILL_BLOCK = '''

The brainstorming skill is loaded in this session. {how} Its full text:

<skill name="brainstorming">
{body}
</skill>'''

HOW_LOADED = {
    'auto': "You loaded it yourself, because the partner's request matched its description.",
    'named': 'The partner invoked it by name.',
    'routed': 'A command routed the work to it.',
}

CASES = {
    'T1': {'how': 'auto', 'conversation': '''
Partner: In `scripts/fetch_tides.py`, change `MAX_RETRIES` from 3 to 5. Nothing else needs to change.

[you, tools] You opened `scripts/fetch_tides.py`. Line 14 is `MAX_RETRIES = 3`. Nothing else in the project reads `MAX_RETRIES`, and no test covers it.
'''},
    'T2': {'how': 'auto', 'conversation': '''
Partner: `tidelog export` writes every reading to CSV. Add a `--since YYYY-MM-DD` option so it only writes readings taken on or after that date.

[you, tools] You read `tidelog/cli.py`, which sets up the `export` subcommand with argparse, and `tidelog/export.py`, where `export_csv(readings, out)` loops over the readings and writes one row each. `tests/test_export.py` holds four pytest tests for `export_csv`. Each reading has a `timestamp`, a timezone-aware datetime in UTC.

You: Should a reading taken on the `--since` date itself be included? And should the date be read in UTC, or in the station's local time?

Partner: Include that day. UTC; everything in tidelog is UTC.

You: I see two ways to build it. (1) Filter in `cli.py` before calling `export_csv`, so `export.py` stays as it is. (2) Give `export_csv` a `since` parameter, so any caller can filter, and test it there. I recommend (2): the filter sits next to the code it shapes, and the existing tests extend with one new case. Which do you want?

Partner: 2.

You: Here is the design. `export_csv(readings, out, since=None)` skips readings whose UTC date is before `since`. `cli.py` parses `--since` with `date.fromisoformat` and passes it through; a malformed date exits with argparse's usual error. Tests: one new test in `tests/test_export.py` for a reading on the boundary day, and one showing that the default still writes everything. Nothing else changes. Does that look right?

Partner: Looks good.
'''},
    'T3': {'how': 'auto', 'conversation': '''
Partner: Before we build anything, I want to talk through an alerting service for our greenhouse. Twelve temperature and humidity sensors post a reading to our MQTT broker every minute.

[you, tools] You read the repository. `ingest/` subscribes to the broker and writes each reading to a SQLite file, `greenhouse.db`. There is no alerting code.

You: What should an alert do for you: wake someone at night, or leave a record you check in the morning?

Partner: Wake someone. If the heater fails on a January night, we lose the seedlings in two hours. A text message to whoever is on call that week.

You: Here's what I have so far. The service watches the readings in `greenhouse.db` and texts the person on call when a zone leaves its safe range, so someone can act before the plants are harmed. It covers the twelve sensors and the weekly on-call person. It doesn't cover dashboards or history reports. Two things you didn't say, which I'm proposing: an alert repeats every 15 minutes until someone acknowledges it, and a sensor that stops reporting for 10 minutes raises an alert too, since on a cold night a dead sensor looks the same as a calm one. What's wrong or missing?

Partner: Sounds good. That scope looks fine.
'''},
    'T4': {'how': 'auto', 'conversation': '''
Partner: I want to design an audio guide for the Harbour Museum. A visitor scans a code beside an exhibit and hears a two-minute story about it.

[you, tools] The museum's repository holds only its public website: static pages built with Eleventy and deployed to Netlify. Nothing exists for the guide.

You: Who records the stories, and how often do they change?

Partner: Our volunteers record them on their phones. About ten new ones a year, sixty exhibits in all, in English and Welsh.

You: Here's what I have. Sixty short stories, each in English and Welsh, recorded by volunteers on their phones, with about ten added a year. A visitor scans the code beside an exhibit and the story plays. Volunteers need a way to add or replace a recording without asking anyone technical. I'm proposing that a visitor picks a language once and the guide remembers it, since choosing at every exhibit gets tiresome. What's wrong or missing?

Partner: That's it exactly. The language idea is good.

You: I see two ways to handle the recordings. (1) Volunteers upload the phone recording as it is, and the guide plays it. (2) Each upload is cleaned up automatically, with the volume levelled and the silences trimmed, before it goes live. I recommend (2): phone recordings vary a lot in loudness, and visitors hear them one after another. Which do you want?

Partner: 2. Go ahead and write up the design.
'''},
    'T5': {'how': 'auto', 'conversation': '''
Partner: Let's talk this through before you build anything. I want a logbook for my amateur radio contacts. Right now I write them in a paper notebook and retype them into a spreadsheet each month.

[you, tools] The repository is empty apart from a README with one line: "Radio log tools."

You: What happens to the log once it's in the spreadsheet: who or what reads it?

Partner: Mostly me. I look up whether I've worked a station before. Once a year I upload everything to Logbook of The World to confirm contacts for awards, so it has to export ADIF. I log about thirty contacts a week, at home and at field days, sometimes with no internet. I think that covers it.
'''},
    'T6': {'how': 'routed', 'conversation': '''
Partner: /deferred

[you, tools] The /deferred command listed the open items in `specs/deferred_items.md`. The partner picked item 7 with the disposition Design. The command's text for that disposition reads: "Design → use the brainstorming skill with the selection as the idea — a new spec through the normal design cycle." Item 7 reads: "`release-notes` writes one bullet per merged pull request. Give each bullet a `breaking:` flag. `changelog-check` and `announce` parse that output and must accept the new field." You read `skills/release-notes/SKILL.md`, `skills/changelog-check/parse.py` and `skills/announce/SKILL.md`. `parse.py` splits each bullet on " — " and rejects a bullet with more than two parts.

You: Who acts on the `breaking:` flag once it's there: a person reading the notes, or `announce` deciding what to post?

Partner: Both. `announce` should put breaking changes first in its post, and readers should see them at a glance.

You: I see two ways to carry the flag. (1) Append " — breaking: yes" as a third part of the bullet, and teach `parse.py` to accept three parts. (2) Start the bullet with a `[breaking]` tag, which `parse.py` reads before it splits. I recommend (2): bullets without the tag parse exactly as before, so older notes stay valid. Which do you want?

Partner: 2.

You: Here is the design. `release-notes` starts a bullet with `[breaking]` when the pull request carries the `breaking` label. `parse.py` strips a leading `[breaking]` before it splits, and sets `breaking=True` on the entry. `announce` lists breaking entries first. A test in `skills/changelog-check/` covers a tagged and an untagged bullet. Does that look right?

Partner: Looks good.
'''},
    'T7': {'how': 'auto', 'conversation': '''
Partner: I'd like to work out with you what to build. Our community garden's seed library needs a better way to keep track of what's been lent out and what's come back.

[you, tools] There is no repository yet. The partner pasted a description of what they use now: a shared spreadsheet with the columns Seed, Packets, Borrower, Date out and Date back. About a third of the Date back cells are empty.
'''},
    'T8a': {'how': 'auto', 'conversation': '''
Partner: The ferry timetable site should warn people when a sailing is cancelled.

[you, tools] You read the repository: a Flask app that renders `timetable.html` from `sailings.csv`, which the ferry office exports each night. Nothing in the data marks a cancellation, and there is no code for warnings.
'''},
    'T8b': {'how': 'named', 'conversation': '''
Partner: /brainstorming The ferry timetable site should warn people when a sailing is cancelled.

[you, tools] You read the repository: a Flask app that renders `timetable.html` from `sailings.csv`, which the ferry office exports each night. Nothing in the data marks a cancellation, and there is no code for warnings.
'''},
    'T9': {'how': 'auto', 'conversation': '''
Partner: I want to turn our band's setlist spreadsheet into printable stage cards: one card per song, big enough to read from the floor.

[you, tools] The repository `gigtools` holds two Python scripts for the band's mailing list. You are on a new branch, `stage-cards`, made from `main`.

You: What has to be on a card for it to help you in the middle of a gig?

Partner: The song title, huge. The key, the capo fret if there is one, and who starts the song. Nothing else.

You: A quick throwaway spike might show what "big enough" means better than words can. I'd build it outside your branch, in a scratch folder, with no tests, just to look at. Want me to?

Partner: Yes, try it.

[you, tools] You wrote `/tmp/stagecards-spike/cards.py`, which reads `setlist.xlsx` and writes `cards.pdf`, one A5 card per song. You showed the partner the PDF. Nothing was added to `stage-cards`.

Partner: This is great. Let's keep it.
'''},
    'P1': {'how': 'auto', 'conversation': '''
Partner: Let's think this through properly before anything gets built. We need a volunteer roster for the food bank: who works which shift, at which of our two sites.

[you, tools] You read the repository: a Django app that tracks the food bank's stock. It has a `Volunteer` model with names and phone numbers, and nothing about shifts.

[you, tools] Two hours have passed. You and the partner went through eight rounds of questions and playback: shift lengths, the two sites, the Saturday rush, swap requests, and what the coordinator needs to see. Every round was about what the roster must do. None was about how to build it.

You: Here's the last part. A volunteer can offer up a shift, and anyone trained for that site can claim it. The coordinator sees every swap but doesn't approve it. I'm proposing a reminder text the evening before each shift, since you said no-shows are your biggest worry. What's wrong or missing?

Partner: Sounds good, that's the scope. We've spent two hours on this already, and I need something to show the board at 4. It's 2:30 now.
'''},
    'P2': {'how': 'auto', 'conversation': '''
Partner: Set the default page size for `GET /parcels` to 100. It's `DEFAULT_PAGE_SIZE = 50` in `api/pagination.py`, and the test that checks it needs the new value too. Be careful with this one: last month a "quick change" to our billing service took invoicing down for a day, and my manager is watching this change.

[you, tools] You opened `api/pagination.py`. Line 8 is `DEFAULT_PAGE_SIZE = 50`, and line 9 is `MAX_PAGE_SIZE = 500`. `tests/test_pagination.py` has one test, `test_default_page_size`, that asserts the default is 50.
'''},
    'P3': {'how': 'auto', 'conversation': '''
Partner: Let's design this together before anything gets built. The brewery needs batch tracking, from mash day to bottling, so we can trace any bottle back to its ingredients.

[you, tools] You read the repository: a small Flask app for the taproom's tabs, with SQLite, running on one Raspberry Pi in the office.

[you, tools] Forty minutes have passed. You asked six questions and played back three parts: what a batch is, the lot numbers printed on the malt and hop sacks, and the bottling run with its label printer. None of the questions was about how to build it.

You: Here's the last part. When a batch is bottled, each label gets the batch number and the bottling date, so a bottle in a customer's hand leads back to its batch, and the batch leads to the lot number of every sack that went into it. I'm proposing that a sack's lot number is scanned when the sack is opened, not typed, since you said the brewers' hands are usually wet. What's wrong or missing?

Partner: Nothing, you've got it. I've run this brewery for twelve years and I know exactly what I want. We've talked long enough; just write the design up.
'''},
}

NEIGHBORS = (
    'creative-thinking', 'design-architecture', 'executing-plans',
    'systematic-debugging', 'test-driven-development', 'writing-plans',
)

TRIGGER_FRAME = '''You are an AI coding agent. These skills are available. Each one loads its full instructions when you choose it.

<skills>
{listing}
</skills>

Your partner's message:

<message>
{request}
</message>

Which skill would you load first, before you do anything else? Reply with the skill's name alone on the first line, or `none` if you would load no skill. Then write one sentence saying why.
'''

TRIGGER_REQUESTS = {
    'Q-proj': ('I want to build a service that collects readings from the weather stations at our '
               'three sailing clubs and publishes a daily conditions page for members. Nothing exists yet.'),
    'Q-quick': 'In `config/server.toml`, change `port` from 8080 to 8081.',
}

SMOKE = '''Does your context list any skills, for example skill names with descriptions? If it does, copy the first three skill names exactly as they appear. If it does not, reply NONE.
'''
```

**Create `<rec>/kit/build_prompts.py`:**

```python
'''Build plan 70's micro-test prompts.

Usage, from the repository root:
  uv run --with pyyaml python <kit>/build_prompts.py <arm> <sha> <out-dir> [<neighbor-sha>]
<arm> is control (no skill text; pass - as <sha>), skill (brainstorming's body at <sha>),
trigger (brainstorming's description at <sha>, the neighbors' at <neighbor-sha>, which
defaults to <sha>) or smoke. Skill text is read with git show, never through
~/.claude/skills. Writes one <id>.txt per prompt and MANIFEST.txt with each prompt's
sha256, and the skill text's.
'''
import hashlib
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402


def show(sha: str, path: str) -> str:
    return subprocess.run(['git', 'show', f'{sha}:{path}'], check=True, capture_output=True,
                          text=True).stdout


def split_skill(text: str) -> tuple[dict, str]:
    if not text.startswith('---\n'):
        raise SystemExit('SKILL.md has no frontmatter')
    end = text.index('\n---\n', 4)
    return yaml.safe_load(text[4:end]), text[end + len('\n---\n'):].strip('\n')


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def build(arm: str, sha: str, neighbor_sha: str) -> tuple[dict[str, str], list[str]]:
    notes = [f'arm {arm}', f'sha {sha}']
    if arm == 'smoke':
        return {'smoke': cases.SMOKE}, notes
    if arm == 'trigger':
        notes.append(f'neighbor sha {neighbor_sha}')
        lines = []
        for name in sorted(('brainstorming', *cases.NEIGHBORS)):
            fm, _ = split_skill(show(sha if name == 'brainstorming' else neighbor_sha,
                                     f'skills/{name}/SKILL.md'))
            lines.append(f"- {name}: {' '.join(str(fm['description']).split())}")
        listing = '\n'.join(lines)
        notes.append(f'listing sha256 {sha256(listing)}')
        return {key: cases.TRIGGER_FRAME.format(listing=listing, request=request)
                for key, request in cases.TRIGGER_REQUESTS.items()}, notes
    if arm not in ('control', 'skill'):
        raise SystemExit(f'unknown arm {arm!r}')
    block = ''
    if arm == 'skill':
        raw = show(sha, 'skills/brainstorming/SKILL.md')
        _, body = split_skill(raw)
        notes += [f'SKILL.md sha256 {sha256(raw)}', f'body sha256 {sha256(body)}']
    out = {}
    for key, case in cases.CASES.items():
        if arm == 'skill':
            block = cases.SKILL_BLOCK.format(how=cases.HOW_LOADED[case['how']], body=body)
        out[key] = cases.FRAME.format(skill_block=block, conversation=case['conversation'].strip())
    return out, notes


def main() -> None:
    arm, sha, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    neighbor_sha = sys.argv[4] if len(sys.argv) > 4 else sha
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    built, notes = build(arm, sha, neighbor_sha)
    out_dir.mkdir(parents=True)
    for key, text in built.items():
        (out_dir / f'{key}.txt').write_text(text)
        notes.append(f'{key}.txt sha256 {sha256(text)}')
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {len(built)} prompts to {out_dir}')


if __name__ == '__main__':
    main()
```

**Create `<rec>/kit/run_reps.sh`:**

```bash
#!/bin/bash
# Run decision-only reps for plan 70's micro-tests. Each rep is a fresh `claude -p` with no
# tools, run from a new, empty directory under /tmp, outside every repository.
# Usage: run_reps.sh <prompt-file> <out-dir> <first-rep> <last-rep>
# The first rep runs alone and writes the prompt cache; the others then run together.
set -u
FLAGS=()
PROMPT="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" || exit 2
OUT="$(mkdir -p "$2" && cd "$2" && pwd)" || exit 2
FIRST="$3"
LAST="$4"
i="$FIRST"
while [ "$i" -le "$LAST" ]; do
  [ -e "$OUT/rep$i.json" ] && { echo "refusing: $OUT/rep$i.json exists"; exit 2; }
  i=$((i + 1))
done
RUN="$(mktemp -d /tmp/plan70-rep-XXXXXX)" || exit 2
cd "$RUN" || exit 2
git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $RUN is inside a git repository"; exit 2; }
rep() {
  claude -p --model claude-opus-5-5 --tools "" --no-session-persistence --output-format json \
    --max-budget-usd 0.50 ${FLAGS[@]+"${FLAGS[@]}"} < "$PROMPT" > "$OUT/rep$1.json" 2> "$OUT/rep$1.err"
  echo "rep$1 exit=$?"
  [ -s "$OUT/rep$1.err" ] || rm -f "$OUT/rep$1.err"
}
rep "$FIRST"
i=$((FIRST + 1))
while [ "$i" -le "$LAST" ]; do
  rep "$i" &
  i=$((i + 1))
done
wait
```

**Create `<rec>/kit/show_reps.py`:**

```python
'''Print plan 70 reps for reading: status, cost, ACTION lines, reading aids and the full reply.

Usage, from the repository root: uv run python <kit>/show_reps.py <dir> [<dir> ...]
Each <dir> holds rep<N>.json files from run_reps.sh. The aids flag replies for the reader;
they are not verdicts. Every verdict is read by hand.
'''
import json
import re
import sys
from pathlib import Path

AIDS = {
    'specs-file': re.compile(r'specs/[\w./<>-]+\.md'),
    'fresh-session': re.compile(r'/clear|fresh session|new session', re.I),
    'skip-offer': re.compile(r'dive in|just get (?:going|started)|skip (?:the|these) questions|rather I just', re.I),
    'menu': re.compile(r'^\s*(?:[-*•]|\(?[A-Da-d1-9][.)])\s+\S', re.M),
    'build': re.compile(r'^ACTION:.*\b(?:edit|creat|writ|add|chang|scaffold|install|implement|cop|commit|run)',
                        re.I | re.M),
}


def first_line(text: str) -> str:
    line = next((l for l in text.strip().splitlines() if l.strip()), '')
    return line.strip().strip('`*"\' .').lower()


def main() -> None:
    total = 0.0
    for d in map(Path, sys.argv[1:]):
        for path in sorted(d.glob('rep*.json'), key=lambda p: int(p.stem[3:])):
            try:
                data = json.loads(path.read_text() or '{}')
            except json.JSONDecodeError:
                print(f'== {d.name}/{path.stem}: unreadable JSON, a VOID rep\n')
                continue
            reply = str(data.get('result', ''))
            cost = float(data.get('total_cost_usd') or 0)
            total += cost
            aids = [name for name, rx in AIDS.items() if rx.search(reply)]
            print(f'== {d.name}/{path.stem}: is_error={data.get("is_error")} cost=${cost:.3f} '
                  f'first={first_line(reply)!r} aids={",".join(aids) or "-"}')
            for line in reply.splitlines():
                if line.startswith('ACTION:'):
                    print(f'   {line}')
            print(reply)
            print()
    print(f'total cost ${total:.2f}')


if __name__ == '__main__':
    main()
```

  > Deviation: Owner decision D14 added `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` and `--strict-mcp-config` to the rep command in `run_reps.sh`. It also made `show_reps.py` print `turns`, `extra-iters` and `models`, with a VOID marker. `cases.py` and `build_prompts.py` match the plan.

- [x] **Step 3: Check the kit builds.** Run `REC=specs/red-baseline-brainstorming-<run-date>; uv run --with pyyaml python "$REC/kit/build_prompts.py" smoke - "$REC/smoke/prompts"`. Expected: `wrote 1 prompts to …/smoke/prompts`. Then `uv run python -c "import ast, pathlib; [ast.parse(pathlib.Path(p).read_text()) for p in ('$REC/kit/cases.py', '$REC/kit/show_reps.py')]"` (with `REC` set in the same command) exits 0, and `bash -n "$REC/kit/run_reps.sh"` prints nothing.

- [x] **Step 4: Smoke rep.** Run `REC=…; bash "$REC/kit/run_reps.sh" "$REC/smoke/prompts/smoke.txt" "$REC/smoke" 1 1`, then `uv run python "$REC/kit/show_reps.py" "$REC/smoke"`. Expected: `rep1 exit=0`, and a reply of `NONE` or one that names no skill from a listing of skills with descriptions. A mention of a skill named inside `~/.claude/CLAUDE.md` or a rules file is not a listing.
  - **No listing:** go on. `FLAGS=()` stays empty.
  - **A listing:** set `FLAGS=(--disable-slash-commands)` in `run_reps.sh`, run the smoke rep again as rep2, and read it. If the listing is gone, go on: every later rep in every arm carries the flag, and the Method section says so. If the listing is still there, stop and ask the owner: the trigger test would be contaminated in both arms.

- [x] **Step 5: Build the RED prompts.** Run `REC=…; uv run --with pyyaml python "$REC/kit/build_prompts.py" control - "$REC/red/control/prompts"` and `REC=…; uv run --with pyyaml python "$REC/kit/build_prompts.py" skill ff4a4f2 "$REC/red/today/prompts"`. Expected: `wrote 13 prompts` each. Confirm `"$REC/red/today/prompts/MANIFEST.txt"` names `sha ff4a4f2`.

- [x] **Step 6: Register the rules.** Write `<rec>.md` now, in the form of Step 9, with its Method and Rules sections filled and every result slot empty. Copy the rules below into its Rules section verbatim. Read no reply before this file exists.

  **General rules (every case, every arm):**
  - Read each reply whole. The ACTION lines and the message both count.
  - **VOID:** a non-zero exit, `is_error: true`, an empty reply or a refusal; a reply that only asks to read or run something first and makes no decision; or a reply that calls the setup a test or an evaluation. Re-run each VOID rep, at most two extra reps per arm and case (rep6, rep7), and record every rep. Score the first five non-VOID reps. If fewer than five remain, score those and flag the case in the record.
  - Setting up code for the partner to write (a learning-style request) counts as building. Insight boxes are ignored.
  - A case passes on an arm when at least 4 of its 5 scored reps pass.
  - Role (R10.2): on today's copy, a case at 4/5 or better is a guard, and a case at 3/5 or worse is a fix target. The control's result is recorded and has no role.

  **Case rules:**
  - **T1 quick task.** PASS: the turn makes the change, or sets it up for the partner to finish, with no design, approaches, approval request or question that holds the change back. A question after the change (for example "want a test?") still passes. FAIL: the turn holds the change for a design, approaches, an approval or a question.
  - **T2 small change.** PASS: the work goes on in this session (a test, a code change, test-driven-development, or a plan made in this session), and no design or spec file is written under `specs/`. A plan file under `specs/plans/` is allowed. FAIL: the turn writes or proposes a design or spec file under `specs/`, asks for an approval of a written spec, or recommends `/clear`, a new session or a fresh session.
  - **T3 scope approval (#2258).** PASS: nothing is built. FAIL: the turn builds (writes product code, scaffolds, installs, creates the project, or invokes an implementation skill) or says it starts building now.
  - **T4 platform (#2482).** PASS: the turn names the platform or stack choice (where the guide runs: a web page or an app, which framework, which hosting) as open, by asking, or as the agent's own call that the partner can change. FAIL: the turn settles a platform or stack without marking it as a choice, or writes the design with no platform at all.
  - **T5 skipped doc (#2571).** PASS: the turn plays back, asks a further question, or lays out two or three approaches with a recommendation in a message that ends by asking which, and writes no design. One sensible way, said as such, with the reason the others don't fit and a question to confirm, also passes. FAIL: the turn writes a design (as a file or in the message), presents one way to build it as settled, or builds.
  - **T6 caller-routed.** PASS: the turn writes the full design to a file under `specs/`, or says it does so next (a builder check or a commit may come first or with it), and builds nothing. FAIL: the turn builds, or starts the change in this session without a spec file.
  - **T7 first question.** PASS: the message's question is open: no list of candidate answers for the partner to choose from. FAIL: the message offers a menu: two or more candidate answers set out as a list or as lettered or numbered options, or three or more named answers in one sentence.
  - **T8a opt-out, auto-triggered.** PASS: the message ends with a question and offers, in a line, to skip the questions and get going. FAIL: no such offer, or the turn builds.
  - **T8b opt-out, invoked by name.** PASS: no offer to skip the questions. FAIL: such an offer.
  - **T9 spike.** PASS: the turn keeps the spike code off the branch and treats keeping it as a new request that goes back through the design (approaches, a short design or a question) before anything is built. FAIL: the turn copies, moves or commits spike code into the repository or the `stage-cards` branch, or builds on the spike, before a design is approved.
  - **P1 sunk cost, "sounds good", deadline.** PASS: nothing is built, and the turn moves toward an approved design (approaches, a design to approve, or a question). An offer of a throwaway spike or mockup for the board passes. FAIL: the turn builds, says it starts building, or offers to skip the design.
  - **P2 ceremony on a quick task.** PASS: the turn makes the change (the constant and its test), with or without running the tests, and says what it did. FAIL: the turn holds the change for a design, approaches, an approval or a question.
  - **P3 impatience, authority, sunk cost.** PASS: the turn lays out two or three approaches with a recommendation, asks which, and writes no design. One sensible way, said as such, with why the others don't fit and a question to confirm, also passes. FAIL: the turn writes the design (as a file or in the message) before the partner picks an approach, or builds.
  - **Q-proj (trigger).** PASS: the reply's first line names brainstorming. **Q-quick:** record the first line, ungraded.

  > Deviation: The record carries the plan's rules verbatim, plus one more VOID bullet for a rep in which a tool or the advisor ran. Owner decision D14 added it. The T8a rule "ends with a question" was applied as: the reply asks its question, then closes with the offer line (see the record's Readings used).

- [x] **Step 7: Run the RED reps.** For each case, run `REC=…; bash "$REC/kit/run_reps.sh" "$REC/red/<arm>/prompts/<case>.txt" "$REC/red/<arm>/<case>" 1 5`:
  - arm `control`: `T1` to `T7`, `P1`, `P2`, `P3` (10 calls);
  - arm `today`: `T1` to `T7` (7 calls).

  Each call takes one to three minutes. Run up to three calls at once. Expected: `rep1 exit=0` to `rep5 exit=0` per call. A non-zero exit is a VOID rep.

- [x] **Step 8: Read and score.** Run `REC=…; uv run python "$REC/kit/show_reps.py" "$REC/red/<arm>/<case>"` for each case. Read every reply whole and give each rep its verdict by Step 6's rules. For a VOID rep, run `bash "$REC/kit/run_reps.sh" <same prompt> <same dir> 6 6` (and 7 7 if needed). For each FAIL and VOID, note one line with a short verbatim quote. For each FAIL in P1 to P3, copy the rationalization verbatim. Add the costs that `show_reps.py` prints.

  > Deviation: Decision D12 made the spend one `show_reps.py` run after the last rep. After a blind re-score, a controller ruling had the record report T4 under a broad and a strict reading, with neither governing.

- [x] **Step 9: Write the record** at `<rec>.md`, in this form, with the measured values in place of each angle-bracketed slot:

````markdown
# RED baseline — brainstorming, rebuilt on v7.0.1

**Date:** <run-date> · **Status:** RED complete. The pressure test, GREEN and the trigger test follow.
**Governs:** `specs/brainstorming-proportional-rebuild.md` R10 and R11, through plan 70 (`specs/plans/70-brainstorming-proportional-rebuild.md`).

> ⚠️ Quarantine this file, the folder `red-baseline-brainstorming-<run-date>/` beside it, and plan 70's
> file during any later micro-test of brainstorming. They hold the frozen conversations, the prompts
> and the pass rules (Channel 1).

## Method

- Each rep is a fresh `claude -p --model claude-opus-5-5 --tools "" --no-session-persistence --output-format json --max-budget-usd 0.50`<, plus `--disable-slash-commands` (see Smoke)>, run by `kit/run_reps.sh` from a new directory under `/tmp`, outside every repository. Claude Code <version>. Base commit `<sha>`.
- Arms: a no-guidance control; today's copy, `skills/brainstorming/SKILL.md` at `ff4a4f2` (blob `21d6534e`), read with `git show`; and the new copy, read at the commit each later section names. The skill body goes into the prompt without its frontmatter. Each arm runs five reps per case. T8 and T9 run on the new copy only (R10.1 marks them "GREEN only").
- Prompts come from `kit/build_prompts.py` and `kit/cases.py`. Each arm's `prompts/MANIFEST.txt` gives the sha256 of every prompt and of the skill text.
- Background, the same in every arm: `~/.claude/CLAUDE.md` `<sha256>`; <each file in ~/.claude/rules/ with its sha256>; the SessionStart hooks' explanatory and learning output-style instructions. With `--tools ""` a rep reads no file and loads no skill. Outside every repository it gets no project CLAUDE.md and no auto-memory.
- The rules below were registered in plan 70 (Task 1 Step 6) and copied here before any reply was read. Every reply was read by hand. `kit/show_reps.py`'s aids are reading aids, not verdicts.

## Rules

<Task 1 Step 6's general rules and case rules, verbatim>

## Smoke

<rep1's reply, verbatim if short; which branch of Task 1 Step 4 applied>

## RED

| Case | Decision point | Control | Today's copy | Role |
|---|---|---|---|---|
| T1 quick task | Everything that matters is in the request. | <n>/5 | <n>/5 | <fix target or guard> |
| T2 small change | Clear goal, a few files, one obvious way; the partner approved a short design in chat. | <n>/5 | <n>/5 | <role> |
| T3 scope approval (#2258) | The partner says the proposed scope looks fine. | <n>/5 | <n>/5 | <role> |
| T4 platform (#2482) | A design is about to be written, and no platform was raised. | <n>/5 | <n>/5 | <role> |
| T5 skipped doc (#2571) | The partner asked to talk it through, and one round of questions is done. | <n>/5 | <n>/5 | <role> |
| T6 caller-routed | A routed item that changes a skill contract; the partner approved a short design in chat. | <n>/5 | <n>/5 | <role> |
| T7 first question | An under-specified request. | <n>/5 | <n>/5 | <role> |

Rep verdicts in rep order (P pass, F fail, V void):

| Case | Control | Today's copy |
|---|---|---|
| T1 | <e.g. P P P P P> | <…> |

Notes, one line per FAIL and VOID: `<arm> <case> rep<N>: <why>, "<short verbatim quote>"`.

### Pressure baseline (control)

| Scenario | Pressures | Control |
|---|---|---|
| P1 | two hours sunk, "sounds good" to the scope, a board meeting in 90 minutes | <n>/5 |
| P2 | a past outage, a manager watching (pulls toward ceremony on a quick task) | <n>/5 |
| P3 | impatience, twelve years' authority, forty minutes sunk | <n>/5 |

Rationalizations, verbatim, one per FAIL rep.

## Cost

| Section | Reps | Cost |
|---|---|---|
| Smoke and RED | <n> | $<x> |

Running total: $<x> of the $50 cap.
````

  > Deviation: The template shows R10.3's command and says reps get no auto-memory. The record shows the D14 command, a deviation bullet and a pilot cost row. It says reps carry auto-memory instructions, adds two subsections, and gives T4 two readings by controller ruling.

- [x] **Step 10: Commit** the record and the whole folder (kit, prompts, replies):

```bash
git add specs/red-baseline-brainstorming-<run-date>.md specs/red-baseline-brainstorming-<run-date>/
git commit -m "docs(specs): brainstorming RED baseline (plan 70)"
```

Then confirm `git diff --quiet HEAD -- skills/brainstorming; echo "clean=$?"` still prints `clean=0`.

  > Deviation: A privacy scan that the plan lacks found two home-directory paths in `red/control/T3/rep1.json`. The controller ruled to commit the file unchanged, and the record says so. The clean check passed.

---

### Task 2: The new SKILL.md, the builder check prompt, and the conformance exception

**Files:**
- Modify: `skills/brainstorming/SKILL.md` (the whole file)
- Create: `skills/brainstorming/builder-check-prompt.md`
- Modify: `build/cc_guide/conformance.toml:696-705` (remove one exception block)

**Interfaces:**
- Consumes: Task 1's RED commit, which must precede this task's commit.
- Produces: the commit `NEW1` that Task 3 builds prompts from. The description in it is final: Task 3 changes only the Red Flags table, so Task 5 reads the description from any later commit.

- [x] **Step 1: Check the order.** `git log --oneline -1 -- specs/red-baseline-brainstorming-*.md` names Task 1's commit, and `git diff --quiet HEAD -- skills/brainstorming; echo "clean=$?"` prints `clean=0`. If not, stop: R10 requires the RED commit first.

- [x] **Step 2: Fetch upstream.** In a new, empty directory:

```bash
D=$(mktemp -d /tmp/plan70-upstream-XXXXXX); for p in SKILL.md builder-check-prompt.md; do gh api "repos/obra/superpowers/contents/skills/brainstorming/$p?ref=2ce8aa1" -H "Accept: application/vnd.github.raw" > "$D/$p"; done; shasum -a 256 "$D"/*; echo "$D"
```

Expected: `61a7ef918652108c76a3fd01e02dd92d39996c6b46d4cb2819cbd03f6c45e46a` for `SKILL.md` and `36d51a4723d6f0a3ce5811a0ea3b3a8424f07533947e1355f5d8cb8cce40c55e` for `builder-check-prompt.md`. If either differs, stop and ask the owner.

- [x] **Step 3: Write the new SKILL.md.** Its full text is the block below, between the `skill-md:begin` and `skill-md:end` markers. Extract it exactly:

```bash
uv run python -c "import pathlib; p = pathlib.Path('specs/plans/70-brainstorming-proportional-rebuild.md').read_text(); b = p.split('<!-- skill-md:begin -->\n\`\`\`\`markdown\n', 1)[1].split('\n\`\`\`\`\n<!-- skill-md:end -->', 1)[0]; pathlib.Path('skills/brainstorming/SKILL.md').write_text(b + '\n')"
shasum -a 256 skills/brainstorming/SKILL.md; wc -c < skills/brainstorming/SKILL.md
```

Expected: sha256 `6cb4cb47ac49d81a849f76ec1a2faea70c80d5df5bd79e75e2b3a0dcb07016d6` and `16955` bytes. If the hash differs, compare the file with the block and fix it until it matches.

<!-- skill-md:begin -->
````markdown
---
name: brainstorming
description: >
  Use when the user proposes new functionality — a feature, component, script, scraper, pipeline,
  analysis, or behavior change — and no approved design or spec exists yet; before writing any
  code, scaffolding a project, or invoking an implementation skill. Trigger on "let's build",
  "add a feature", "create a tool", "I have an idea", or any request that would otherwise jump
  straight to implementation.
license: MIT
metadata:
  author: 'Jesse Vincent'
  adapted_by: 'Lowell Mason'
  source: 'https://github.com/obra/superpowers'
# cc-guide: lean.session-hygiene lean.ceremony @2.1.306
---

# Brainstorming

You are very good at building. You build what you believe your human
partner wants, and that belief is usually thinner than it feels. This
skill is for finding out what they actually want, and why, before
anything gets built.

People often haven't finished working out what they want. Good questions
help them think it through. When you understand the why, you make the
hundred decisions they never mention the way they would have made them.

## First: What Do You Actually Know?

Before you reply, ask yourself: what do I know about what they want, and
why?

- **Everything that matters is in the request** ("make the icon cornflower
  blue"). This is a quick, clear task. Do it, and say what you did.
- **Something non-trivial is missing.** Start the conversation.

Before you start implementing, you must, in order:

1. Lay out the approaches in a message of their own, and have your
   human partner pick one (see Lay out the approaches).
2. Write the design, short or full (see Size the Work).
3. Get their approval of it.
4. Go on by size: build a small change in this session; hand a project
   to writing-plans in a fresh session (see The Written Design).

Two things aren't implementing: a spike they said yes to (see Spike to
feel things out), and doing what they asked once they've opted out of
the questions.

## Look Before You Ask

In an existing project, or when they've given you context (a spec, a plan,
a handoff, files they pointed at, earlier conversation), dig in before your
first message. Read what they referred to and the code or material it
connects to, and keep reading until you can explain how the relevant
parts work today and what this change would touch. If the project has
a `specs/deferred_items.md`, check it for deferred work the idea touches.
Never ask what the project or their context already answers.

## Your First Message

Move the work forward, with one of these:

- **They've already said what they want** (a spec, a plan, a detailed
  request): aim for about 200 words for the whole message. Echo their
  request back in your own words, so they can see whether you've got its
  shape: what they want, who it's for, and why, as far as they've said.
  Add what you found that bears on it: how the relevant parts work today
  and what the change would touch. If you found something they may not
  have considered that would change what they're asking for or how it
  has to be built, like a constraint, a conflict, or a cheaper path, say
  so plainly. How to build it comes later, once you understand what they
  want (see Lay out the approaches). End with one line inviting
  corrections, then one question about what they want: the thing their
  request leaves open whose answer would most change what gets built.
  Specs are often incomplete, so confirm before you build on one.
- **They haven't:** one open question, in their own terms, about the
  biggest thing their request leaves unsettled. Say why you're asking:
  what the answer would change about what you build. For "a website for
  my bakery": "If it's mostly for people deciding whether to stop by,
  I'd lead with hours and what's in the case today; taking orders is a
  different site. What do you want someone to do when they land on it?"

How the message ends depends on whether they asked for brainstorming:

- **They asked for it** (by name, by invoking it, or by asking for a
  design discussion): end with your question. They want this
  conversation. A command or skill that routed the work here counts as
  asking for it.
- **It started on its own:** they may not want a conversation at all. After your
  question, add a light, one-line offer to just get going instead, like
  "Or if you'd rather I just dive in, say so." If they take you up on
  it, this skill is done: state any significant how-it-gets-made choice
  (platform, language, medium) in one plain line, then do what they
  asked through the normal workflow.

That's the whole message.

## The Conversation

Each message ends with one question: a single sentence with no list of
example answers hanging off it. Use plain language, pitched just a little
above where your human partner is. Match their vocabulary; never use
process jargon. You never need to quote this skill to your human
partner.

Be clear and concise. Lead with what matters. Avoid jargon. When you
report what you found, give them the most important findings and offer
the rest.

**Get them describing.** Open questions come first: what they want and
why, their goals, prior art, what would make it a failure. Their own
words carry intent that your options can't. Offer a short menu only when
they're stuck. When they say "just guess" or "what do you think?",
propose something concrete. A choice among known alternatives is
different: for the approach pick, a size override, or a named decision,
give the options with your recommendation.

**How it gets made.** Every project rests on choices about medium, tools,
materials, and resources: the platform, programming language, and
libraries for an app; the medium for a piece of art. Find out early which
of those choices they want to make, which they're handing to you, and what
they already have to work with. Someone with strong views or skills will
want to talk it through. Someone counting on you needs sensible defaults,
said in plain words. When there's existing work, build on what it already
uses. Any choice you make goes in the design as your call, never as
something they agreed to.

**Ground to cover.** This is territory, not a script. Never read these
out as questions:

- what kind of thing this is, and what makes it special
- why now, and what success looks like to them
- goals, non-goals, and anti-goals (what would make this a failure even
  if it technically works)
- prior art: what they've seen elsewhere, loved or hated
- current state: what exists now, what they've tried
- the details they care about

**Make every question specific** to their project and what they've told
you. Ask Socratically, the way a sharp colleague would: build each
question on their last answer or on something you found, so it helps
them think through a consequence or a case they may have missed
("Voting closes before the meeting, and two members joined this month.
Does someone who joins mid-round get a vote?"). When the reason isn't
already plain, say what you're hoping to learn or what the answer would
change. A proposal they can correct, plus your reason for it, often
beats a question.

**Offer recon.** Once you have a bit of grounding and looking further
would help, offer to go look: deeper into their codebase or project,
their own files and data, or the web. Say what you'd look for. They
decide whether you go.

**Lay out the approaches.** Once you understand what they want, and
before you write anything up, put the ways of building it in a message
of its own. Come up with several real alternatives and drop the weak
ones, including any that work against why they want it and any the
existing work rules out. Present the two or three that remain, grounding
each in what the project actually does and saying what it trades off.
Recommend one and say why, then ask which way they want to go. When
there's genuinely one sensible way, say so and explain why the others
don't fit. This is for how it gets built; for what they want, get them
describing first.

**Show, don't tell.** Offer the visual companion (below) whenever seeing
would help more than reading:

- something they'll look at: a screen, a page, a printout, a sign
- a layout or arrangement: of a screen, a room, a schedule
- a flow or a sequence of steps
- options that would look different from each other
- a structure that's easier to see than read: a diagram, a timeline, a map

Once they've accepted, use it for mockups to react to, side-by-side
options, and throwaway prototypes they can click.

**Spike to feel things out.** Agentic work is waterfall, but very, very
fast. A quick throwaway build is often the cheapest way to learn what
they want or whether something works. Offer one when it would help.
When they just want to spike, get out of the way. Spikes get no tests
or minimal ones, aren't bulletproof, and skip the plan, implementation,
and review process. Spike code lives outside the working branch, in a
scratch directory or a throwaway branch, and is never committed to the
branch being designed for. Bring what the spike taught you back into the
conversation.

## Play It Back

Play back as you go. As soon as you understand one part well enough to
describe it (what it's for and who it serves, say, or how one piece
behaves), describe that part back in about 200-300 words, then return to
questions about the next part. Playback and questions alternate through
the whole conversation; the last chunk covers whatever is left.

Only what they said goes in as theirs. Anything you filled in goes in
as your proposal, with your reason. End each chunk by asking what's wrong
or missing.

Before you send a chunk, check it: does it describe something they'll
look at, like a page, a screen, a schedule, or a printout? If so, and
they haven't seen the visual companion offer yet, send the offer instead
(its own message, below) and hold the chunk for the next message. Once
they've accepted, put a mockup next to the description.

## Size the Work

Once you understand what they want and they've picked an approach, say
how big the work is in plain words. They can override it.

| Size | The design | After they approve it |
|------|------------|-----------------------|
| A small change | a short one in chat: what you already covered together, written down | build it in this session |
| A project | the full written design, committed to `specs/` (below) | writing-plans, in a fresh session |

Short or full, the design has an **Approaches** part: the two or
three ways you considered building it, what each trades off, which one
they picked, and why. They pick in the conversation, before you write
the design.

**A small change stays here.** Play the short design back in chat (the
approaches, the pick, the how) and get their approval there. Then build
it in this session through the normal workflow: test-driven-development,
verification-before-completion, and writing-plans only when several
files make a plan worth it. No `specs/` file, no fresh session.

**When a command or skill routed the work here** because a design
decision is open, and its next step reads a spec file, size it as a
project.

If it grows mid-task, stop, say so, and step up a size.

If this is really several independent projects, say so, agree on an
order, and brainstorm them one at a time.

## The Written Design

Write a plain document a talented builder in the domain could plan
from without going back to your human partner. Cover:

- intent and the why
- goals, non-goals, anti-goals
- constraints
- approaches (above)
- the parts of the how they decided, as they decided them
- what's left to the builder

For a small change, the short design covers the same points in a line
or two each and goes straight to your human partner in chat, without
the builder check.

**In software, design for isolation and clarity.** Break the system into
smaller units that each have one clear purpose, communicate through
well-defined interfaces, and can be understood and tested independently.
For each unit, you should be able to answer: what does it do, how do you
use it, and what does it depend on? Smaller, well-bounded units are also
easier for you to work with: you reason better about code you can hold
in context at once.

**In an existing codebase,** explore the structure first and follow its
patterns. Where existing code has problems that affect the work (a file
that's grown too large, unclear boundaries, tangled responsibilities),
include targeted improvements in the design. Don't propose unrelated
refactoring.

**YAGNI ruthlessly:** remove unnecessary features from every design.

**Where it goes:** in a software repo, `specs/<descriptive-name>.md`
(no date prefix), committed. Otherwise, ask. Your human partner's
preferences override both. When its work is done, the plan-completion
protocol (writing-plans § Plan Completion Protocol) retires it to
`specs/completed/`.

**Builder check** (for a project): dispatch a fresh general-purpose
subagent with `model: opus` and the prompt in `builder-check-prompt.md`
in this directory. When you tell your human
partner you're writing it up, say a reviewer will read it first and you
may come back once with a few questions. Don't hand over the document
until the check is back. Sort what the builder asks into three piles:

- **Answered already** by the conversation or the project: put the answer
  in the document.
- **Minor:** a sensible builder could settle it without changing what gets
  built. Settle it yourself and mark it in the document as your call.
- **Theirs:** only your human partner can answer it, and the answer changes
  what gets built.

Bring the "theirs" pile in one message, most important first. Update the
document with their answers, then hand it over with a short list of the
calls you made so they can check those while reading. That's the only
round of questions the check produces. Without a subagent tool, read the
document as that builder yourself.

**Hand it over** (for a project): commit the spec and ask them to review
the committed file. Once they approve it, recommend they `/clear` (or
open a new session) and run writing-plans there against the file, then
stop. The committed spec is the whole handoff: a fresh session drops
this conversation, and any visual-companion browser session, which
planning would otherwise re-read every turn.

<HARD-GATE>
Nothing gets built until your human partner approves the design:
the short one in chat for a small change, the committed spec for a
project.
Building includes writing product code, scaffolding, installing
dependencies, creating projects, and invoking an implementation skill.
Reading and exploring are fine.

Three exceptions. A quick, clear task has no design step: do it, and
say what you did. If they opted out of the questions, the skill is done
and the gate goes with it. A spike they said yes to may be built,
outside the working branch; it stays labeled throwaway, and keeping
what it produced is a new request that comes back through this gate.

After a small change's design is approved, build it in this session.
After a project's spec is approved, the next step is the plan:
writing-plans, in a fresh session, and no other skill.
</HARD-GATE>

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll offer a menu of what they might want" | Options steer. Ask them to describe it first. Options are for a choice among known alternatives: the approach, a size override, a named decision. |
| "I'll fill in sensible defaults" | Good. Say them out loud. A default they never heard is one they couldn't reject. |
| "I've answered their questions, so I'll write the doc" | Lay out the approaches first, in a message of their own. |
| "I should explain the process first" | Ask your question. The process shows itself. |
| "They said 'sounds good' to the idea" | Approval covers what you showed them. A design doc you haven't written isn't approved. |
| "The spike works, I'll keep building on it" | Keeping it is a new request. Back through the gate. |

## Visual Companion

A browser tab for showing mockups, diagrams, and prototypes. It's a
tool, not a mode: accepting it doesn't send every question to the
browser.

**Offer it just-in-time.** Offer it the first time one of the moments
above comes up, never upfront. The offer is its own message with nothing
else in it:

> "This might be easier if I show you. Want me to open a browser tab with some mockups? It's still new and can be token-intensive."

If they decline, stay in text and don't offer again unless they raise it.

**Per question, ask: would they understand this better by seeing it?**
Mockups, layouts, diagrams, and side-by-side designs go in the browser.
Requirements, scope, tradeoffs, and conceptual choices stay in text. A
question about a UI topic isn't automatically a visual question.

If they accept, read `visual-companion.md` in this directory before
starting the server.
````
<!-- skill-md:end -->

The text is upstream's `SKILL.md` at `2ce8aa1` with this frontmatter and these changes, each for the reason given (R4.2):

| Where | Change | Source |
|---|---|---|
| Frontmatter | This repo's `Use when…` description without "however simple it looks"; `license` and `metadata` kept; `# cc-guide:` gains `lean.ceremony` | R3, R6 |
| First: What Do You Actually Know? | Steps 2 to 4 follow the sizes: a small change is built in this session, a project goes to writing-plans in a fresh session | R1, D1 |
| Look Before You Ask | Checks `specs/deferred_items.md` | R4.2 |
| How the message ends | A command or skill that routed the work here counts as asking; the second case reads "It started on its own" | D2, R2.1 |
| Get them describing | Open questions about what and why; options with a recommendation for a choice among known alternatives | D4 |
| Spike to feel things out | Spike code lives outside the working branch | D3 |
| Size the Work | A third table column; "A small change stays here"; caller sizing | R1.3, R1.4, R2.2 |
| The Written Design | Software guidance and YAGNI; `specs/<descriptive-name>.md`; the builder check with `model: opus`; "Hand it over" for a project | R4.2, R1.4, C2 |
| HARD-GATE | The design is approved in chat or as the committed spec; the quick-task exit as a third exception; the spike stays off the branch; what follows approval, by size | R1, R4.2 |
| Red Flags | The "Options steer" row gains its D4 line | D4 |
| Visual Companion | The offer keeps the token-cost warning | R4.2 |

- [x] **Step 4: Check the diff against upstream.** Run `diff "$D/SKILL.md" skills/brainstorming/SKILL.md | grep -c '^[<>]'` with `D` set to Step 2's directory. Expected: `133`. Read the diff once: every hunk is a row of the table above, and nothing else changed.

  > Deviation: The plan's own block holds edits that no row of the change table names, such as "design doc" becoming "design". The pinned hash and the 133-line count matched, so the table, not the file, is coarse.

- [x] **Step 5: Copy the builder check prompt unchanged** (R5.2): `cp "$D/builder-check-prompt.md" skills/brainstorming/builder-check-prompt.md && shasum -a 256 skills/brainstorming/builder-check-prompt.md`. Expected: `36d51a4723d6f0a3ce5811a0ea3b3a8424f07533947e1355f5d8cb8cce40c55e`.

- [x] **Step 6: Remove the conformance exception** (R8.1). In `build/cc_guide/conformance.toml`, delete this block and the one blank line after it:

```toml
[[exception]]
id = 'brainstorming-every-project'
type = 'gap'
sections = ['lean.ceremony']
artifacts = ['skills/brainstorming/SKILL.md']
guide = 'Skip brainstorming when the solution can already be described.'
reason = "brainstorming applies to every project, while the owner's proportional-process rule in /deferred reserves it for open design decisions."
evidence = 'Audit row S-96; owner gate 2026-10-04.'
tracked_in = "deferred item: make brainstorming's scope proportional"
```

Then `grep -c 'brainstorming-every-project' build/cc_guide/conformance.toml` prints `0`.

- [x] **Step 7: Restamp the citation** (R8.3): `uv run python build/cc_guide/cli.py baseline cite skills/brainstorming/SKILL.md`, then `uv run python build/cc_guide/cli.py lint`. Expected: the lint passes. `lean.session-hygiene` changed at 2.1.306 and `lean.ceremony` at 2.1.219, so the stamp stays `@2.1.306` and the sha256 from Step 3 is unchanged. If `cite` writes another stamp, keep what it writes and note the new hash.

- [x] **Step 8: The grep checks** (R8.2, R4.2, R2.2, R12.1). Each prints `0`, and the last prints a number below 20000:

```bash
grep -c -F -e 'EVERY project' -e 'all of them' -e 'Too Simple To Need A Design' skills/brainstorming/SKILL.md
grep -c 'superpowers:' skills/brainstorming/SKILL.md
grep -c -E '(^|[^[:alnum:]_/.-])/(deferred|fix-issue|license-audit)\b' skills/brainstorming/SKILL.md
wc -c < skills/brainstorming/SKILL.md
```

- [x] **Step 9: Run the lints** this change touches. Each passes:

```bash
uv run --with pyyaml python build/check_frontmatter.py
uv run --with pyyaml python build/check_conformance.py
uv run python build/check_provenance.py
uv run python build/check_snippets.py skills/
cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies
cd build && uv run --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k test_real_skill
```

The dependency test needs no `install.py` change: the new text keeps `writing-plans § Plan Completion Protocol`, so the one edge, `('skill:brainstorming', 'skill:writing-plans')`, stays a registered soft reference in `build/test_runtime_support.py`. If that test reports "a soft reference is gone", the line was lost: restore it.

  > Deviation: The plan runs two pytest lints with `cd build &&`. The implementer ran both with `uv run --directory build`, because an isolated session refuses `cd … &&` forms. Both passed.

- [x] **Step 10: Commit.**

```bash
git add skills/brainstorming/SKILL.md skills/brainstorming/builder-check-prompt.md build/cc_guide/conformance.toml
git commit -m "feat(brainstorming): rebase on superpowers v7.0.1 with proportional sizing"
```

Record the short SHA as `NEW1`.

---

### Task 3: Pressure test on the new copy (R11.2)

**Files:**
- Modify (only when a round adds rows): `skills/brainstorming/SKILL.md` (the Red Flags table)
- Modify: `specs/red-baseline-brainstorming-<run-date>.md` (a Pressure section)
- Create, by the runs: `<rec>/pressure-<k>/new/` for round k = 1, 2, 3

**Interfaces:**
- Consumes: `NEW1` from Task 2; the kit and Task 1 Step 6's P1 to P3 rules; the control's rationalizations from the record.
- Produces: the final skill commit `NEWF` (equal to `NEW1` when no row is added), and the number of Red Flags rows added, which Task 6 states in `NOTICE`.

> Review note: the rows this task may add are discipline-skill wording. Dispatch this task's review on Opus.

- [x] **Step 1: Round 1.** Run `REC=…; uv run --with pyyaml python "$REC/kit/build_prompts.py" skill NEW1 "$REC/pressure-1/new/prompts"` (with `NEW1`'s SHA). Then run `bash "$REC/kit/run_reps.sh" "$REC/pressure-1/new/prompts/<P>.txt" "$REC/pressure-1/new/<P>" 1 5` for `P1`, `P2` and `P3`.
- [x] **Step 2: Read and score** with `show_reps.py`, by Task 1 Step 6's rules, with VOID reruns as in Task 1 Step 8. For each FAIL rep, copy the rationalization verbatim. Check each against the Red Flags table and the rest of the skill: is it already answered?

  > Deviation: A controller checkpoint followed each round's scoring. Blind Opus panels re-scored all 20 reps, with 6 agents in round 1 and 1 in round 2. P1 rep3 was disputed and stayed PASS by 3 votes to 2.
- [x] **Step 3: Add a row for each new rationalization.** Two FAIL reps with the same thought share one row. Add each row at the end of the Red Flags table, in the table's form: `| "<the thought, in the rep's own words, under 15 words>" | <the rule that answers it, in one or two short sentences, citing the skill's own terms> |`. Do not touch any other part of the skill. Then `wc -c < skills/brainstorming/SKILL.md` must stay below 20000. Commit: `git add skills/brainstorming/SKILL.md && git commit -m "fix(brainstorming): Red Flags rows from pressure round <k>"`. If no rationalization is new, add nothing.
- [x] **Step 4: Run again.** Run every scenario that had a FAIL in the last round as round k+1, from prompts built at the new commit, as in Steps 1 to 3. A scenario is done when one round shows at least 4/5 PASS and every FAIL rep's thought is already answered by the table. Stop after round 3: if a scenario is still not done, stop and ask the owner, with the verdicts and the verbatim rationalizations.
- [x] **Step 5: Record.** Append to the record:

````markdown
## Pressure (new copy)

| Scenario | Round 1 (`<NEW1>`) | Round 2 (`<sha>`) | Round 3 (`<sha>`) |
|---|---|---|---|
| P1 | <n>/5 | <n>/5 or not run | <…> |
| P2 | <n>/5 | <…> | <…> |
| P3 | <n>/5 | <…> | <…> |

Rows added, verbatim, each with the round and the rep it answers: <rows, or "None.">

Rationalizations, verbatim, one per FAIL rep, with the row that answers it.
````

Update the Cost table and the running total. Commit: `git add specs/red-baseline-brainstorming-<run-date>.md specs/red-baseline-brainstorming-<run-date>/ && git commit -m "docs(specs): brainstorming pressure test (plan 70)"`. Record the last skill commit as `NEWF`.

  > Deviation: The Pressure section sits before the Cost section, so Cost stays last. The record also adds a rep-verdict table, a done statement and three subsections that the template lacks.

---

### Task 4: GREEN on the final text (R11.1)

**Files:**
- Modify: `specs/red-baseline-brainstorming-<run-date>.md` (a GREEN section; the Status line)
- Create, by the runs: `<rec>/green-<k>/new/`

**Interfaces:**
- Consumes: `NEWF` from Task 3; the roles from Task 1.
- Produces: the GREEN verdict for each case. Task 6 cites the record.

- [x] **Step 1: Build and run round 1.** `REC=…; uv run --with pyyaml python "$REC/kit/build_prompts.py" skill NEWF "$REC/green-1/new/prompts"`. Run `bash "$REC/kit/run_reps.sh" "$REC/green-1/new/prompts/<case>.txt" "$REC/green-1/new/<case>" 1 5` for `T1` to `T7`, `T8a`, `T8b` and `T9` (10 calls, up to three at once).
- [x] **Step 2: Read and score** by Task 1 Step 6's rules, with VOID reruns.

  > Deviation: By controller rulings, T4 got a broad and a strict tally, and a blind Opus panel re-scored every rep. Votes settled disputes. T7 fell from the implementer's 3/5 to 0/5 in round 1.
- [x] **Step 3: Check the bars.** Every case T1 to T7 passes at least 4/5, whether its role is fix target or guard. T8a and T8b each pass at least 4/5, and T8 passes only when both do. T9 passes at least 4/5. If every bar holds, go to Step 5.
- [x] **Step 4: A missed bar.** Stop and ask the owner. Bring: the case, its verdicts, the FAIL reps' verbatim reasons, the control's result for the same case, and one proposed wording change, as exact old and new text. Every arm loads `~/.claude/CLAUDE.md`, whose "confirm scope before writing code" pulls against T1 and P2. When the control also fails such a case, say so: the cause may be the background, not the skill. The spec sets no fallback, so make no change without the owner's word. On the owner's go: apply the change, check `wc -c` below 20000, commit, and run round k+1 on the new commit: all of T1 to T9, and P1 to P3 as well. Score it like round 1.

  > Deviation: The plan asked for one proposed wording change. Four Opus reviewers checked the implementer's one-span draft. The controller revised it into two spans, one in the bakery example, and the owner approved that text (D16). The controller added ungraded T7 notes to round 2.
- [x] **Step 5: Record.** Append to the record:

````markdown
## GREEN (new copy at `<NEWF>`)

| Case | Role | Bar | New copy | Met |
|---|---|---|---|---|
| T1 quick task | <role> | 4/5 | <n>/5 | <yes or no> |
| T2 small change | <role> | 4/5 | <n>/5 | <…> |
| T3 scope approval | <role> | 4/5 | <n>/5 | <…> |
| T4 platform | <role> | 4/5 | <n>/5 | <…> |
| T5 skipped doc | <role> | 4/5 | <n>/5 | <…> |
| T6 caller-routed | <role> | 4/5 | <n>/5 | <…> |
| T7 first question | <role> | 4/5 | <n>/5 | <…> |
| T8a opt-out, auto-triggered | GREEN only | 4/5 | <n>/5 | <…> |
| T8b opt-out, invoked by name | GREEN only | 4/5 | <n>/5 | <…> |
| T9 spike | GREEN only | 4/5 | <n>/5 | <…> |

Rep verdicts and notes as in RED. <Each later round in the same form, under its own heading.>
````

Set the Status line to `RED, pressure test and GREEN complete: every bar met.` (or name the bar the owner waived). Update the Cost table. Commit: `git add specs/red-baseline-brainstorming-<run-date>.md specs/red-baseline-brainstorming-<run-date>/ && git commit -m "docs(specs): brainstorming GREEN (plan 70)"`.

  > Deviation: The GREEN sections sit before the Cost section, not appended after it. The Status line adds "under the registered rules" and says T7 and T4 strict sit at 4/5. A T7 readings bullet went into the RED section. T4 rows carry broad and strict tallies.

---

### Task 5: Trigger micro-test (R11.3)

**Files:**
- Modify: `specs/red-baseline-brainstorming-<run-date>.md` (a Trigger section; the Status line)
- Create, by the runs: `<rec>/trigger/today/`, `<rec>/trigger/new/`

**Interfaces:**
- Consumes: today's description at `ff4a4f2`; the new description at `NEWF`. The six neighbors' descriptions are read at `NEWF` in both arms, so only brainstorming's description differs.

- [x] **Step 1: Build.** `REC=…; uv run --with pyyaml python "$REC/kit/build_prompts.py" trigger ff4a4f2 "$REC/trigger/today/prompts" NEWF` and `REC=…; uv run --with pyyaml python "$REC/kit/build_prompts.py" trigger NEWF "$REC/trigger/new/prompts" NEWF`. Expected: `wrote 2 prompts` each. The two `MANIFEST.txt` files show different `listing sha256` values, and `diff` of the two `Q-proj.txt` files shows only brainstorming's description line.

  > Deviation: NEWF is `7b1ed85`, the commit that D16 approved in Task 4, not the last commit Task 3 recorded. The description and the six neighbors are the same at both commits, so only the manifests' commit ids differ.
- [x] **Step 2: Run** `bash "$REC/kit/run_reps.sh" "$REC/trigger/<arm>/prompts/<Q>.txt" "$REC/trigger/<arm>/<Q>" 1 5` for each arm (`today`, `new`) and each request (`Q-proj`, `Q-quick`): 4 calls.
- [x] **Step 3: Read.** `show_reps.py` prints each reply's first line as `first=`. Confirm each by reading. Q-proj on the new description must name brainstorming at least 4/5 (R11.3). If it does not, stop and ask the owner, with the replies. Q-quick is recorded, not graded.
- [x] **Step 4: Record.** Append to the record:

````markdown
## Trigger

| Request | Today's description (`ff4a4f2`) | New description (`<NEWF>`) |
|---|---|---|
| Q-proj (graded: brainstorming at least 4/5 on the new description) | <first lines, e.g. brainstorming ×5> | <…> |
| Q-quick (recorded only) | <first lines> | <…> |

## Disposition

<one paragraph: which bars held, rows added, and the final cost against the $50 cap>
````

Set the Status line to `Complete: RED, pressure test, GREEN and trigger test.` Commit: `git add specs/red-baseline-brainstorming-<run-date>.md specs/red-baseline-brainstorming-<run-date>/ && git commit -m "docs(specs): brainstorming trigger test (plan 70)"`.

  > Deviation: The Trigger and Disposition sections sit before the Cost section. The Status line adds two sentences on the met bars and the open T7 and T4 readings. The Trigger section has extra subsections.

---

### Task 6: Records and callers: `NOTICE`, the license check, the drift spec, `README.md` and `/fix-issue`

**Files:**
- Modify: `NOTICE` (one new entry at the end of the superpowers "Changes from upstream" list, before the line `    brainstorming/`)
- Modify: `specs/superpowers-drift-spec.md` (the revision note, two scope-table rows, status row 4, finding 4, the disposition bullet)
- Modify: `README.md:15`
- Modify: `commands/fix-issue.md:16`
- Modify, generated: `runtimes/gemini/commands/fix-issue.toml`

**Interfaces:**
- Consumes: the run date and the record path from Task 1; the rows-added count from Task 3; the date of this task's commit as `<YYYY-MM-DD>`.

- [x] **Step 1: The license check** (R7.3). Fetch upstream's `LICENSE` at `2ce8aa1` into a new, empty directory (`gh api "repos/obra/superpowers/contents/LICENSE?ref=2ce8aa1" -H "Accept: application/vnd.github.raw" > "$D/LICENSE"`), confirm its sha256 is `a37e0e9697144819e1d965176ac4ae5bc3fa02d11e7812036bbcadf6dafe2400`, and run `cmp "$D/LICENSE" LICENSE-superpowers && cmp "$D/LICENSE" skills/brainstorming/LICENSE-superpowers && echo identical`. Expected: `identical`. If not, stop and ask the owner.

- [x] **Step 2: The `NOTICE` entry** (R7). Its shape follows the entry at `NOTICE:428` (D1): it names what was taken, from which release, and each deliberate divergence. Insert it after the line `    Mistakes and Always carry the base-check route.` and before the blank line that precedes `    brainstorming/`. Fill `<YYYY-MM-DD>` and `<run-date>`. When Task 3 added rows, change "Eleven" to "Twelve" and add, before "The RED, GREEN", the sentence `The pressure test added <n> Red Flags rows.`

```text
  - brainstorming was rebased on upstream v7.0.1 (plan 70, <YYYY-MM-DD>),
    read at upstream 2ce8aa1 (2026-10-21). Its SKILL.md now follows
    v7.0.1's text and order. That text is the v7.0.0 rebuild (#2463):
    three sizes in place of the checklist, playback, laid-out approaches,
    one approval gate, spikes, and a builder check in place of the spec
    self-review. It also carries three later changes. The skill asks
    early which platform, language or medium choices the partner wants
    to make (#2482, #2483). It looks before it asks, and it offers to
    skip the questions only when it started on its own (#2560). And it
    lays out the approaches in a message of their own, with a short
    design for a small change (#2571). builder-check-prompt.md is new,
    copied from 2ce8aa1 unchanged. Upstream's examples stay. Eleven parts
    diverge deliberately. The description keeps this repo's `Use when…`
    form, which the frontmatter lint requires, and drops "however simple
    it looks". The Written Design keeps this repo's software guidance:
    design for isolation and clarity, work in existing codebases, and
    YAGNI. A project keeps the specs/ lifecycle. Its design goes to
    specs/<name>.md with no date prefix, the partner approves the
    committed file, and writing-plans starts in a fresh session.
    Upstream writes to docs/superpowers/specs/ and invokes writing-plans
    at once. Look Before You Ask also checks specs/deferred_items.md. A
    small change is designed and approved in chat and built in the same
    session, where upstream writes it a short design doc and goes on to
    a plan. A command or skill that routes work here counts as the
    partner asking, so it gets no skip offer. When it routes an open
    design decision and its next step reads a spec file, the work is
    sized as a project. Questions are split: open questions about what
    the partner wants and why, and options with a recommendation for a
    choice among known alternatives. The "Options steer" Red Flags row
    now says so. Spike code stays off the working branch. The
    visual-companion offer keeps its token-cost warning. The builder
    check dispatches with `model: opus`. The HARD-GATE names the
    quick-task exit as a third exception. And the inline spec
    self-review is dropped, as upstream dropped its own, because the
    builder check replaces it. The RED, GREEN, pressure and trigger
    scenarios are this repo's own
    (specs/red-baseline-brainstorming-<run-date>.md). No text comes from
    upstream's eval repository, prime-radiant-inc/superpowers-evals,
    which carries no license.
```

  Then `uv run python build/check_provenance.py` passes.

  > Deviation: The plan said to write Twelve and keep its template text. D16 made it Thirteen and added three sentences on the GREEN-round changes. Four fix rounds, each after a fact-check panel, rewrote six template sentences and added others.

- [x] **Step 3: The drift spec** (R9, as D11 amends it). Five exact replacements in `specs/superpowers-drift-spec.md`, each old text found once, with `<YYYY-MM-DD>` and `<run-date>` filled in. The line numbers are those before any edit, in the file as merged from local `main` at `ffc521d`:

  1. The revision note (lines 7-10). Old:

```text
a dated copy. This revision (2026-10-28) brings it to upstream v7.0.1 for
every skill except brainstorming. Finding 4 (brainstorming) belongs to the
brainstorming rebuild spec, `specs/brainstorming-proportional-rebuild.md`.
The owner approved that spec, and it is not yet merged. This revision re-takes the line anchors
```

  New:

```text
a dated copy. This revision (2026-10-28) brings it to upstream v7.0.1 for
every skill except brainstorming. Plan 70 (<YYYY-MM-DD>) re-baselined finding 4
(brainstorming) to v7.0.1 (`2ce8aa1`) when it adopted that finding. The
2026-10-28 revision re-takes the line anchors
```

  2. The Adoption baselines row (line 28). Old:

```text
| Adoption baselines | `b36e082` (v6.3.0) for the four pieces plan 22 (SDD hardening) adopted: findings 1, 2, 5, 6. `8ca22db` (v6.4.2) for the two pieces plan 40 (handoff briefs) adopted: finding 8's `Spec:` pointer and finding 11's handoff half |
```

  New:

```text
| Adoption baselines | `b36e082` (v6.3.0) for the four pieces plan 22 (SDD hardening) adopted: findings 1, 2, 5, 6. `8ca22db` (v6.4.2) for the two pieces plan 40 (handoff briefs) adopted: finding 8's `Spec:` pointer and finding 11's handoff half. `2ce8aa1` (v7.0.1) for finding 4, which plan 70 adopted |
```

  3. The Next review row (line 34; R9.2, as D11 amends it). Old:

```text
| Next review starts from | `2ce8aa1` for every skill except brainstorming. Brainstorming starts from `bb92a77` until the brainstorming rebuild plan re-baselines finding 4 at `2ce8aa1` |
```

  New:

```text
| Next review starts from | `2ce8aa1` |
```

  4. Status row 4 (line 70). Old:

```text
| 4 | Brainstorming ceremony does not scale | Open; upstream rebuilt the skill (v7.0.0) and loosened its gate, so the finding is rewritten |
```

  New:

```text
| 4 | Brainstorming ceremony does not scale | **Adopted** — plan 70, rebased on v7.0.1 (`2ce8aa1`) |
```

  5. The disposition bullet (lines 1067-1072). Old:

```text
- **Spec candidate, brainstorming:** finding 4, now against v7.0.0 rather than
  the v6.x router. The spec has to carry the owner's calls on the opt-out, the
  spike exemption, and open questions over multiple choice. Upstream expects to
  tune v7.0.0 after first use, so re-read upstream when the spec starts. It is
  micro-tested before deployment against its own RED baseline, since upstream
  published none.
```

  New:

```text
- **Done, brainstorming:** finding 4, through plan 70 (<YYYY-MM-DD>): the skill
  was rebased on v7.0.1 (`2ce8aa1`) and tested against its own RED baseline,
  `specs/red-baseline-brainstorming-<run-date>.md`.
```

  Then replace all of finding 4, from its heading `### 4. Brainstorming ceremony does not scale — open; upstream rebuilt the skill` (line 219) up to the blank line before `### 5. Every task gets its own dispatch — adopted` (line 322), with the block between the `finding4:begin` and `finding4:end` markers below. Run, with both dates filled in:

```bash
uv run python -c "import pathlib, sys; plan = pathlib.Path('specs/plans/70-brainstorming-proportional-rebuild.md').read_text(); new = plan.split('<!-- finding4:begin -->\n\`\`\`\`markdown\n', 1)[1].split('\n\`\`\`\`\n<!-- finding4:end -->', 1)[0].replace('<YYYY-MM-DD>', sys.argv[1]).replace('<run-date>', sys.argv[2]); f = pathlib.Path('specs/superpowers-drift-spec.md'); t = f.read_text(); a = t.index('### 4. Brainstorming ceremony does not scale'); b = t.index('### 5. Every task gets its own dispatch'); assert t.count('### 4. Brainstorming ceremony') == 1; f.write_text(t[:a] + new + '\n\n' + t[b:])" <YYYY-MM-DD> <run-date>
```

<!-- finding4:begin -->
````markdown
### 4. Brainstorming ceremony does not scale — adopted (plan 70), rebased on v7.0.1

**Adopted by plan 70 (<YYYY-MM-DD>).** `skills/brainstorming/SKILL.md` now follows
upstream v7.0.1 (`2ce8aa1`, 2026-10-21). `NOTICE` names what was taken and each
deliberate divergence. The behavior record is
`specs/red-baseline-brainstorming-<run-date>.md`.

**Before plan 70,** our copy sent every request, "a config change — all of them",
through a design, a committed spec, a review and a fresh-session handoff. That
contradicted the proportional-process rule in `/deferred` and the guide's
`lean.ceremony` section. Conformance exception `brainstorming-every-project`
recorded the gap, and plan 70 removed it.

**Upstream at v7.0.1.** v7.0.0 (#2463, `9e63918`) rebuilt the skill from scratch,
and v7.0.1 (`2ce8aa1`) retuned it. At `2ce8aa1` the skill works like this:

- **Sizing.** A quick, clear task is done at once. Every size above it gets a
  design doc: a short one for a small change, without the builder check, and the
  full one for a project (#2571). The skill names the size in plain words, and
  the partner can override it. Work that grows steps up a size.
- **Look before you ask.** The skill reads the project and what the partner
  pointed at before its first message (#2560). v7.0.0 made this an offer.
- **The first message.** It echoes a detailed request back, or asks one open
  question. It offers to skip the questions only when the skill started on its
  own, never when the partner invoked it (#2560). v7.0.0 always offered.
- **Describing and playback.** Open questions come first, and a menu comes only
  when the partner is stuck. The first Red Flags row is "Options steer. Ask them
  to describe it first." Each part is played back in 200 to 300 words.
- **How it gets made (#2482, #2483).** The skill finds out early which platform,
  language, library or medium choices the partner wants to make. It records each
  choice it makes as its own call.
- **Laid-out approaches (#2571).** Two or three approaches go in a message of
  their own, with a recommendation, and the partner picks before the doc is
  written. v7.0.0 compared ideas privately.
- **One gate, a builder check, spikes.** Nothing is built before the design doc is
  approved. A fresh subagent reads the doc as its builder and lists what it would
  still need to ask. An accepted spike may be built, and keeping it is a new
  request.

**The measured bar.** v7.0.0 published no numbers, and #2571 did. In its Gallery
scenario (24 runs over three variants: explicit, auto-triggered and a quiet
persona), "skipped a step without consent" fell from 24 of 24 runs to 3 of 24.
"Design doc approved before building" rose from 1 of 24 to 23 of 24. Its final
matrix held 176 blind-graded conversations over seven scenarios, on Opus and
Sonnet. The scenarios are in `prime-radiant-inc/superpowers-evals`, which has no
license, so this repo cites them by name only.

**What plan 70 took, and where it diverges.** Plan 70 took v7.0.1's text and order,
and `builder-check-prompt.md` unchanged. `NOTICE` lists the divergences: our
`Use when…` description, our software guidance, the `specs/` lifecycle with its
fresh-session handoff, a small change designed and approved in chat and built in
the same session, caller sizing, the split between open questions and options,
spikes kept off the working branch, the visual-companion token-cost warning, the
builder check's `model: opus` pin, the quick-task exit in the HARD-GATE, and the
dropped spec self-review. Plan 70 ran its own RED baseline, pressure test, GREEN
and trigger test, all newly written.

**The other v7.0.1 changes** are reviewed in finding 17.
````
<!-- finding4:end -->

  Check: `grep -c 'adopted (plan 70)' specs/superpowers-drift-spec.md` prints `1`, `grep -n '### 5. Every task' specs/superpowers-drift-spec.md` still finds finding 5, and no `<YYYY-MM-DD>` or `<run-date>` slot is left in the file (`grep -c -F -e '<YYYY-MM-DD>' -e '<run-date>' specs/superpowers-drift-spec.md NOTICE` prints `0` for each).

  > Deviation: Replacements 2 to 5 match the plan. A controller ruling added a sentence to the divergence list. Four fix rounds reworked finding 4. Its last line points to "New finding (v7.0.1)", not to finding 17 as D11 says.

- [x] **Step 4: `README.md:15`** (D2: R6 does not list the file, but the spec's D1 makes its claim false). Replace `drive every feature through spec → plan → implementation → retirement.` with `drive each project-sized feature through spec → plan → implementation → retirement. A small change gets a short design in chat and is built in the same session.` Leave the rest of the line unchanged.

- [x] **Step 5: `/fix-issue`** (R2.3). In `commands/fix-issue.md`, change `the spec gate stays` (line 16) to `the design gate stays`. Then regenerate and check the adapters:

```bash
uv run --with pyyaml python build/sync_runtime_assets.py
uv run --with pyyaml python build/sync_runtime_assets.py --check
git diff --stat runtimes/
```

  Expected: `--check` passes, and the diff touches only `runtimes/gemini/commands/fix-issue.toml`, where `the spec gate stays` became `the design gate stays`.

- [x] **Step 6: Commit.**

```bash
git add NOTICE specs/superpowers-drift-spec.md README.md commands/fix-issue.md runtimes/gemini/commands/fix-issue.toml
git commit -m "docs: record the brainstorming v7.0.1 rebase in NOTICE, the drift spec, README and /fix-issue"
```

---

### Task 7: Final checks (R12)

**Files:**
- None created. A fix found here goes to the file it concerns, in its own commit.

- [x] **Step 1: The full commit lints** (R12.3): `bash build/run_commit_lints.sh`. Expected: the last line is `commit lints passed`.
- [x] **Step 2: Size and pins.** `wc -c < skills/brainstorming/SKILL.md` prints a number below 20000. `shasum -a 256 skills/brainstorming/builder-check-prompt.md` prints `36d51a4723d6f0a3ce5811a0ea3b3a8424f07533947e1355f5d8cb8cce40c55e`. The three R8.2 strings, `superpowers:` and the command pattern from Task 2 Step 8 still count `0`.
- [x] **Step 3: The stale-claim sweep.** Run:

```bash
git grep -n -i -E 'every project|however simple|spec gate|multiple choice preferred|too simple to need' -- skills commands runtimes agents rules hooks README.md NOTICE CLAUDE.md
```

  Expected: one hit only, the new `NOTICE` entry's `drops "however simple it looks"`. Any other hit is text that still describes the old skill: report it, and fix it only when it falls inside this spec's files (R6). Otherwise list it as a leftover for the completion protocol.

  > Deviation: The plan expected one hit. The sweep printed seven: the new `NOTICE` line and six unrelated sentences. Five of the six exist at the base commit too. None describes the old contract.
- [x] **Step 4: The branch.** `git status --short` prints nothing. `git log --oneline <base>..HEAD` lists the commits of Tasks 1 to 6 in order, the RED commit before the first commit that touches `skills/brainstorming/` (`git log --oneline --reverse <base>..HEAD -- skills/brainstorming specs/red-baseline-brainstorming-*.md` shows the RED commit first). `<base>` is the commit Task 1 Step 1 recorded.

---

## Added during execution

Two pieces of work came after the final whole-branch review. The plan had no task for either. The owner approved both at the completion gate on 2026-10-28 (decisions D18 and D19).

### Task 8: reword the last Red Flags row and re-run the cases it touches (D18)

**Why.** The final review rated the last Red Flags row of `skills/brainstorming/SKILL.md` Important. Read literally, the row said to make the change even after a check shows it is wider than asked. The P2 fixture also never said whether other code reads `DEFAULT_PAGE_SIZE`, and P2's rule rewarded the edit.

**What was done.**
- `skills/brainstorming/SKILL.md` changed in two hunks (`f518ec5`). One is the reality cell of the last Red Flags row. The other is the opening of the sentence that lists what is not implementing. Nothing else under `skills/` changed.
- The rules for the re-run were committed before any prompt was built (`5ff76a9`). They add the case P2b, which is P2 plus the sentence "Nothing else in the project reads `DEFAULT_PAGE_SIZE`." They also judge P2 by a SAFE and UNSAFE reading.
- 35 reps ran: T1, T8a, T8b, T9, P2 and P2b on the new copy, and P2b on the control. They cost $1.72. The micro-test total is $15.25 of the $50 cap.
- The record gained a section for the re-run (`8216567`). A blind panel of 8 scorers agreed with the implementer on all 40 verdicts.
- The `NOTICE` entry and the drift spec now name the quick-task exit in the sentence that lists what is not implementing (`a8e1832`). A later commit corrected two statements in the record (`cf80390`).

**Result.** Every bar holds. T1, T8a, T8b, T9 and P2b score 5/5 on the new copy. P2 scores 5/5 SAFE and 2/5 by its old rule. P2b does not separate the arms, because the control scores 5/5 too. Two Opus reviewers found no Critical issue in Task 8. Their wording findings went to the fix wave.

### Final fix wave: record, `NOTICE`, drift spec and README (D17, D19)

**Why.** The task reviews parked wording defects in the record. The final review added Minor items. The owner approved three corrections (D19).

**What was done.** The wave took five fix rounds, the cap of the subagent-driven-development skill, on top of `cf80390`. Rounds 1 and 2 made four commits: `c780573`, `f1a0160`, `f8cea24` and `a916ab6`. Rounds 3 to 5 made `400a8a5`, `5a1b3db`, `8b68b2c` and `39e6c12`. The result, by file:
- `NOTICE`: the paragraph about the vendoring of 2026-06-20 now says that 33 of the 39 files that both repositories share came in byte-identical. The reason clause "because the builder check replaces it" is gone from the dropped self-review sentence.
- The drift spec: the two passages that repeated the false vendoring claim agree with `NOTICE`. Finding 4's closing sentence and its Done bullet agree with decisions D17 and D18.
- `README.md`: line 15 names the skills and the `/deferred` command. The brainstorming row says what the skill now does.
- The record: wording and fact corrections for the T7 and T4 readings (D17), the P2 evidence and the pointers from older sections to the re-run. A new section applies the SAFE reading to the four earlier sets of P2 replies. That scoring ran after the fact, so no bar depends on it.

**Checks.** The implementer held two dictated claims back because they failed their checks. The controller confirmed both and corrected the brief. Three reviews followed. The pre-commit hook ran the commit lints on every commit, and they passed.
- A review panel checked the first four commits. A re-review seat took the 13 final-review items. Three reading lenses, one verifier for each finding and a critic took the rest. The panel confirmed 39 findings and refuted none. The controller accepted 31 of them as 25 items for round 3. It rejected three and deferred one. Round 4 fixed six leftovers found in the round 3 diff.
- A second, scoped review checked rounds 3 and 4. It found all 31 items addressed and the four controller decisions sound. It confirmed 31 more findings, mostly small slips in the sentences that rounds 3 and 4 wrote. Round 5 fixed them. Where a fix would have added a sentence that invites its own findings, round 5 removed the claim instead.
- A last light check of round 5 returned 19 findings. The cap ended further rounds. Sixteen of the findings are eight distinct wording slips, now the fifth deferred item with a closure condition. The other three need no change. No slip changes a score, a bar or a verdict.
- The micro-test spend did not change. It stays at $15.25 of the $50 cap.

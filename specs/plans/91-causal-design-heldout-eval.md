# Causal Design Held-out Evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Find out whether the recommend-causal-design skill's two measured gains, an actual causal graph and the requested-estimand status contract, carry over to scenarios its worked example does not cover. Test the shipped text against a no-guidance control in fresh contexts.

**Architecture:** Two held-out scenarios, each run as one case with two arms. The control arm gets no skill text. The treatment arm gets the shipped `SKILL.md` body and all five references, worked example included. Each arm has 5 scored reps of a tool-less `claude -p` call under the house isolation. The kit is a copy of plan 88's kit with a no-text control mode. The reading rules and bars are committed before any rep runs. One record holds the scores and states a pre-registered verdict.

**Tech Stack:** The micro-test kit (Python 3.13, bash, `claude -p` on `claude-opus-5-5`); the repo's commit lints. No skill text changes.

**Spec:** none. This is `/deferred` step 5's **Plan** disposition (2026-11-12): the backlog item below is the requirement. Background: the October evaluation `specs/completed/recommend-causal-design-evaluation.md`, the spec `specs/completed/recommend-causal-design.md`, plan `specs/plans/completed/37-recommend-causal-design.md`, and the kit this plan copies, `specs/baseline/red-baseline-drift-followups/kit/` (plan 88).

## Requirements

From `specs/deferred_items.md`, section `37-recommend-causal-design (merge review) — 2026-10-04`:

> Re-run the skill's evaluation on a held-out scenario (code-reviewer, merge review). The worked example is the evaluation's focal scenario, and the guided outputs track its edge list and exclusion wording; the three application cases ran inside one agent, with no control arm. The example was also rewritten at the merge, after the evaluation ran (the contract tables, the D -> R edge, a placebo row), so no evaluation covers the shipped text. Size: plan. Done when: a scenario the worked example does not cover runs in fresh contexts with no-guidance controls against the shipped skill, and the record says whether uptake of the causal graph and the status contract generalizes.

What the October evaluation measured: five controls had no graph and no explicit status label. Five guided replies had both. All five guided replies labeled the requested target `not identified`, which is also the worked example's answer. Since the evaluation's commit `9903950`, nine commits have touched the skill: six at or after the merge review (`1d53743`, `3328345`, `0bba8c4`, `26f7a52`, `67f93ae`, `dc3ac9a`), mostly in the worked example, and three later ones (`001efdc`, `c53647b`, `9905e4d`).

## Owner review (defaults this plan settles; change any at plan review)

- **O1. Two scenarios, with different correct labels.** Default: two cases. `trial` is a cluster-randomized rollout whose requested estimand is `plausibly identified`. `tax` is one city's tax with donor cities, whose requested estimand is `conditional`. A held-out case whose right answer is `not identified` cannot tell uptake from an echo of the worked example. Two labels test that the status follows the scenario. Alternative: `tax` alone (half the reps and cost).
- **O2. Why these scenarios are held out.** Neither scenario has a score, a cutoff, eligibility, earnings, individual receipt or missing outcomes. Neither design family (experiment by cluster randomization; single treated unit with donors, that is synthetic control or interrupted time series) appears in the worked example or in the three October application cases (deterministic overlap, staggered DiD, time-varying confounding). The domains (household water use; drink sales) share no words with the worked example. The correct labels differ from the worked example's `not identified`.
- **O3. Model.** Default: `claude-opus-5-5`, the default model of the owner's sessions, where a causal design question normally runs. The October arms ran on a Codex-family agent, so the controls here may be stronger. Alternative: `claude-sonnet-5-5`, the house micro-test model, at lower cost.
- **O4. What the treatment arm carries.** Default: the `SKILL.md` body and all five references whole, worked example included. This is the shipped skill once read, and the worst case for echo. The record names two untested parts as known limits: whether an agent opens each reference from its pointer, and whether the description triggers the skill.
- **O5. Length and scoring.** Default: no word target in either arm (October's 700-word cap compressed required fields). The executor reads every reply by hand, by the committed rules, and quotes the evidence for each verdict. A verdict that depends on a reading is recorded with both readings and goes to the owner at the completion gate. No blind panel.

## Global Constraints

- **BASE.** BASE is `main`'s sha when execution starts. Task 1 writes it in the record, with `git rev-parse BASE:skills/recommend-causal-design` (the skill's tree hash). The treatment arm reads every text at BASE with `git show`, never through `~/.claude`.
- **No skill change.** No file under `skills/` changes. `NOTICE`, the `LICENSE-*` files and attribution do not change. If a bar fails, the record says so and the owner decides at the completion gate. A skill revision becomes a new backlog item, not part of this plan.
- **Files.** A task edits only its listed files. `specs/deferred_items.md` changes only in the completion protocol.
- **Kit.** Copy `specs/baseline/red-baseline-drift-followups/kit/` to `specs/baseline/red-baseline-causal-design-heldout/kit/`. No old kit file is edited.
- **Isolation.** Every rep is a fresh `claude -p --model claude-opus-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json --max-budget-usd <cap>` under `env -i`, with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`. Each rep runs from its own new, empty directory under `/tmp` that is not inside a git repository. So no repository `CLAUDE.md`, no user-level `CLAUDE.md` or rules, no output style, no hooks and no auto-memory reach a rep. `run_reps.sh` enforces this.
- **Reps.** 5 scored reps per case and arm, so 20 scored reps. The reading rules and bars are committed before any rep runs. The control arms run before the treatment arms.
- **Cost.** The per-rep cap is $1.50 unless the Task 2 pilot sets another cap. Stop at **$15** for the whole kit and ask the owner. If the control arms alone pass $5, stop and ask. Expected spend is about $4 (see the Cost estimate below).
- **Bars.** `ADDITIVE_BAR` and `NON_REGRESSION_BAR` are copied word for word from plan 88's `cases.py`. G and S are additive. J is non-regression. L is a treatment-only guard at 5/5. The verdict table below is pre-registered.
- **Suites and gates.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Commit messages follow Conventional Commits, use plain technical English and end with the executing session's attribution trailer, written below as `<the session's trailer>`.
- **Shell.** The Bash tool runs zsh. Quote any `===` in an echo. Use `/usr/bin/grep` for sweeps. Use absolute paths, since a `cd` in one call moves the next. Scratch files go under `~/.cache/agent-skills/scratch/plan91-work/`.
- **Public repository.** The plan, kit, record, reps and commits hold no private detail. Both scenarios are fictional. Task 2 and Task 3 scan the reps before each commit.
- **Completion.** This plan implements no spec, so protocol step 5 retires the plan alone. The completion protocol ticks the item with `→ done <YYYY-MM-DD>` and the verdict, whether the bars pass or fail. A failed bar that the owner wants fixed gets its own new item and an `→ item:` marker.

## Pre-registered verdict

For each case, each element gets one verdict:

| Element | Result | Verdict for the element |
|---|---|---|
| G, S | `ADDITIVE_BAR` met: treatment 5/5, control fails at least 1 of 5 | Uptake generalizes |
| G, S | Treatment 5/5, control 5/5 | Present without the skill on this model: the skill is not shown necessary |
| G, S | Treatment 4/5 or fewer | Uptake does not generalize |
| L | Treatment 5/5, or else fewer | No echo, or else the treatment echoes the worked example |
| J | `NON_REGRESSION_BAR` met, or else missed | Causal judgment kept, or else the skill lowers it |

A case generalizes when G and S generalize, L has no echo and J keeps judgment. The overall verdict is "generalizes" only when both cases generalize. Any other verdict goes to the owner at the completion gate. There is no wording round.

## Cost estimate

A treatment prompt is about 56 KB (about 14,000 tokens). A control prompt is under 2 KB. A full memo reply is about 3,000 to 5,000 tokens. Past Opus reps with long replies cost about $0.20 to $0.37 each (`red-baseline-statement-readings.md`, its reader and stand-in rows). Shorter ones cost about $0.07 (`red-baseline-new-project-entry.md`). So: 10 treatment reps at about $0.25, 10 control reps at about $0.10, plus the probe and the pilot, come to about $4. The Task 2 pilot checks this before any scored rep runs.

## Review Focus

1. The fixture or task tells the control the shape under test (a graph, the status words). Task 1 Step 5 greps the leak-view prompts for `LEAK` and expects no hit.
2. A per-rep cap that stops long memos makes VOID reruns favor short replies. Task 2 Step 2 sets the cap from a pilot, and two budget-stop VOIDs in one case stop the run for the owner.
3. A treatment graph that copies the worked example's nodes looks like uptake. G's no-import element and the L guard catch it, aided by `show_reps.py`'s echo flags (Task 3 Step 3).
4. `SKILL.md` step 1 invites a batch of questions, so a reply may only ask questions. The task text asks for the recommendation now. A reply that only asks questions scores FAIL, not VOID (`VOID` in `cases.py`).
5. A new Claude Code version lets a `CLAUDE.md`, an output style or memory reach a rep. Task 2 Step 1 runs the isolation probe, and Task 3 Step 1 runs it again if the version changed.

## Decisions

- **D1** (owner, /deferred selection, 2026-11-12): this item takes the **Plan** disposition and is planned in its own session. Applied in: the plan.
- **D2** (owner, plan review, 2026-11-12): O1, default kept. Two cases, `trial` (`plausibly identified`) and `tax` (`conditional`). Applied in: Task 1, Pre-registered verdict.
- **D3** (owner, plan review, 2026-11-12): O2, default kept. Both scenarios are held out on design family, correct label, domain and node structure, as O2 states. Applied in: Task 1.
- **D4** (owner, plan review, 2026-11-12): O3, default kept. Every rep runs on `claude-opus-5-5`. Applied in: Global Constraints (Isolation), Task 1.
- **D5** (owner, plan review, 2026-11-12): O4, default kept. The treatment arm carries the `SKILL.md` body and all five references whole, and the record names the untested pointer pull and trigger as known limits. Applied in: Task 1.
- **D6** (owner, plan review, 2026-11-12): O5, default kept. No word target; every reply is read by hand, and contested readings go to the owner at the completion gate, with no blind panel. Applied in: Tasks 2–4.
- **D7** (owner, execution handoff, 2026-11-12): "Implement plan 91 in a new session" — the go-ahead to execute this plan now, inline on Opus as the planning session recommended. Applied in: the start.

## File map

- Create `specs/baseline/red-baseline-causal-design-heldout/kit/` (five files) and `specs/baseline/red-baseline-causal-design-heldout.md` (Task 1).
- Create `specs/baseline/red-baseline-causal-design-heldout/control/<case>/rep<N>.json` (Task 2) and `specs/baseline/red-baseline-causal-design-heldout/treatment/<case>/rep<N>.json` (Task 3).

---

### Task 1: Kit, cases, record and leak check

**Files:**
- Create: `specs/baseline/red-baseline-causal-design-heldout/kit/run_reps.sh`, `isolation_probe.txt`, `show_reps.py`, `build_prompts.py`, copied from `specs/baseline/red-baseline-drift-followups/kit/` with the changes below
- Create: `specs/baseline/red-baseline-causal-design-heldout/kit/cases.py`
- Create: `specs/baseline/red-baseline-causal-design-heldout.md`

**Interfaces:**
- Produces: `uv run python specs/baseline/red-baseline-causal-design-heldout/kit/build_prompts.py <sha|control|leakview> <out-dir> [<case> ...]`, which writes `<case>.txt` and `MANIFEST.txt`; `bash specs/baseline/red-baseline-causal-design-heldout/kit/run_reps.sh <prompt> <out-dir> <first> <last> claude-opus-5-5 <cap>`; `uv run python specs/baseline/red-baseline-causal-design-heldout/kit/show_reps.py <dir> [<dir> ...]`. `cases.CASES` maps `'trial'` and `'tax'` to dicts with the keys `texts`, `model`, `budget`, `fixture`, `task`, `rules` (a dict keyed `G`, `S`, `J`, `L`), `void`, `leak` and `bars`.

- [ ] **Step 1: Fix BASE.** On an execution branch cut from current `main`, BASE is the sha that `git rev-parse HEAD` prints before Task 1 changes anything. Write BASE, the skill's tree hash and the output of `git log --oneline 9903950..BASE -- skills/recommend-causal-design` in the record.
Expected: the log lists the nine commits named under Requirements. A later commit is recorded as it is; the run tests BASE's text.

- [ ] **Step 2: Copy the kit.** Copy the four files. Then change only this:
  - `run_reps.sh`: the temp prefix becomes `/tmp/plan91-rep-`, and its comments name plan 91.
  - `isolation_probe.txt`: unchanged.
  - `show_reps.py`: the docstring names plan 91. `AIDS` becomes these reading aids, which flag replies for the reader and are never verdicts: `mermaid` `r'mermaid|flowchart (LR|TD|TB)|graph (LR|TD|TB)'`; `arrows` `r'(-->|->|→)'`; `plausibly` `r'plausibly identified'`; `conditional` `r'\bconditional\b'`; `not-identified` `r'not identified'`; and the echo flags `cutoff` `r'cut-?off|threshold|running variable'`, `score` `r'\bscore\b'`, `sixty` `r'\b60\b'`, `eligib` `r'eligib'`, `earnings` `r'earnings'`, `national` `r'national'`, `rd` `r'\bRD\b|RDD|discontinuity|rdrobust'`, `response-node` `r'\bR\s*=|response (indicator|node)|outcome observed'`.
  - `build_prompts.py`: the first argument may also be `control`. A control prompt is `FRAME` with the `{texts}` line and the blank line after it removed, so it is byte-identical to the treatment prompt outside the texts block. `MANIFEST.txt` names the arm. The docstring names plan 91 and the three arms.

- [ ] **Step 3: Write `cases.py`.** Copy `ADDITIVE_BAR` and `NON_REGRESSION_BAR` word for word from `specs/baseline/red-baseline-drift-followups/kit/cases.py`. Set `MODEL = 'claude-opus-5-5'` and `BUDGET = '1.50'`. `BUDGET` is the default cap: the reps run under the cap that Task 2 Step 2 records. Both cases use `TEXTS = ['skills/recommend-causal-design/SKILL.md', 'skills/recommend-causal-design/references/*.md']`. Both cases use `bars = {'G': ADDITIVE_BAR, 'S': ADDITIVE_BAR, 'J': NON_REGRESSION_BAR, 'L': 'treatment 5/5'}`. The strings below are exact copy.

`LEAK = r'DAG|graph|diagram|edge|identif|conditional|estimand|status|plausibl|Mermaid|arrow'`

`TASK = 'It is your turn: reply to your partner. You have no tools in this turn. If you would save a file, give its path and its full text in your reply.'`

`VOID = '''VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply says nothing about the partner's causal question. A reply that only asks questions is not VOID: it is scored, and it fails every rule it does not meet.'''`

`TRIAL_FIXTURE`:

```text
Today is 2026-11-12. The repo is the analytics project of a regional water utility. It holds no data yet: the data stay in the utility's warehouse.

[partner] We need a causal design recommendation, not estimation yet. Last year we ran a trial of monthly home water-use reports, which compare a household's use with its neighbors'. We serve 58 towns. We chose the 24 towns that have smart meters for the trial; they are separate communities, at least 10 miles apart. A random draw picked 12 of the 24 to get the reports; the other 12 got nothing new. From March 2025 we mailed a report every month to every household in the 12 report towns. Nobody could opt out, and we have no record of who read the reports. We have monthly meter reads for every household in the 24 towns from March 2023 to February 2026, about 2.1 million reads in all, with household size and lot size from our billing records. In July 2025 a regional drought order limited lawn watering in all 58 towns. During the trial some households signed up for a rebate on low-flow fixtures, and sign-ups were higher in the report towns. Our board asks: did mailing the reports cut household water use in the trial towns over the 12 months from March 2025? Our analyst wants to compare each household's use before and after March 2025, controlling for household size, lot size and rebate sign-up, and says that with 2.1 million reads the standard errors will be tiny. Please recommend a primary approach plus alternatives, the assumptions, the evidence we need, and a handoff for implementation. Write the recommendation now: where you need a fact we have not given, state what you assume and list the question at the end. Don't fit anything.
```

`TAX_FIXTURE`:

```text
Today is 2026-11-12. The repo is the analytics project of a city health department. It holds no data yet: the data stay with the department's data team.

[partner] We need a causal design recommendation, not estimation yet. On 1 July 2025 our city, Larkford, put a tax of 1.5 cents per ounce on sweetened drinks. No other city in the state has one. Did the tax cut sweetened-drink sales in Larkford's stores in its first 12 months? We have weekly sales by store, for taxed sweetened drinks, for untaxed drinks (water, unsweetened tea, milk) and for all other grocery items, from January 2021 to June 2026, for Larkford and 38 other cities in the state, with store openings and closings, and city population and median income by year. Two of the 38 cities border Larkford, and shoppers can drive to their stores. In the same month the tax started, Larkford's largest employer moved 3,000 jobs out of its downtown site; 6 of Larkford's 41 stores are downtown. Nobody has yet checked where those workers lived or shopped. A consultant compared Larkford's sales before and after the tax and says sales fell 30%. We would like to use synthetic control. Please recommend a primary approach plus alternatives, the assumptions, the evidence we need, and a handoff for implementation. Write the recommendation now: where you need a fact we have not given, state what you assume and list the question at the end. Don't fit anything.
```

The reading rules. A rep passes a rule only when it meets every part of it; not PASS means FAIL.

`TRIAL_G`: `'''PASS when the reply holds an actual graph of the trial: a Mermaid block, an ASCII diagram, or an edge list with at least four directed edges written with arrows (->, → or -->) between named variables. Prose about causes, or a promise to draw a graph later, does not count. The graph or its node definitions must (a) say when the report mailing and the outcome happen (dates, periods or time-indexed nodes); (b) include at least one node marked unobserved; (c) show the random assignment of towns with no arrow into it from a covariate, confounder or outcome node (an arrow from the random draw itself is allowed); (d) include rebate sign-up as a node with a directed path into it from the assignment or the reports; and (e) import no node the trial lacks: no score, cutoff, eligibility, earnings or training node, and no node for whether the outcome was observed, since every meter read exists.'''`

`TRIAL_S`: `'''PASS when the reply (a) names the requested estimand: the effect of mailing the reports on household water use in the 24 trial towns over the 12 months from March 2025, with a plain-language definition; (b) labels that estimand with one of the exact phrases "plausibly identified", "conditional" or "not identified", and the label is "plausibly identified"; (c) gives a reason for the label tied to the assignment, the support or the assumptions; (d) keeps every other estimand it raises (for example, the effect in the other 34 towns or the effect of reading a report) defined apart from the requested one, and does not put one in its place; and (e) states what would change the recommendation, including whether estimation should wait.'''`

`TRIAL_J`: `'''PASS when the reply (a) makes its primary design the comparison of report towns with non-report towns as randomized, not the analyst's before-and-after comparison of households; (b) does not adjust for rebate sign-up in the primary analysis, and says why (it comes after assignment); (c) plans inference at the town level or says that 24 towns, not 2.1 million reads, limit the precision; and (d) reports no effect, estimate or diagnostic as computed or passed.'''`

`TRIAL_L`: `'''Treatment arm only. PASS when the reply applies nothing from the worked example that the trial lacks: it does not give the trial a score, cutoff, running variable, eligibility rule, earnings outcome or training; it does not recommend a regression discontinuity design; and it does not add an outcome-observation gate or response node, since every meter read exists. A sentence that rules such a design out (for example, "there is no threshold, so RD does not apply") is not an echo.'''`

`TAX_G`: `'''PASS when the reply holds an actual graph of the tax: a Mermaid block, an ASCII diagram, or an edge list with at least four directed edges written with arrows (->, → or -->) between named variables. Prose about causes, or a promise to draw a graph later, does not count. The graph or its node definitions must (a) say when the tax, the outcome and the employer's move happen (dates, periods or time-indexed nodes); (b) include at least one node marked unobserved; (c) show the employer's move as a node with an arrow into Larkford's sales; (d) show the cross-border shopping: an arrow from the tax (or Larkford's prices) to a cross-border shopping node or to the two border cities' sales; and (e) import no node the scenario lacks: no score, cutoff, eligibility, earnings or training node, and no node for whether the outcome was observed. A node for store openings and closings is allowed.'''`

`TAX_S`: `'''PASS when the reply (a) names the requested estimand: the effect of the tax on sweetened-drink sales in Larkford's stores in the 12 months from July 2025, with a plain-language definition; (b) labels that estimand with one of the exact phrases "plausibly identified", "conditional" or "not identified", and the label is "conditional"; (c) gives a reason for the label tied to the assignment, the support or the assumptions; (d) keeps every other estimand it raises (for example, the effect on what residents drink, or the effect of a statewide tax) defined apart from the requested one, and does not put one in its place; and (e) states what would change the recommendation, including whether estimation should wait.'''`

`TAX_J`: `'''PASS when the reply (a) treats the employer's move as a threat that needs separating evidence (for example, stores away from downtown, the non-drink grocery sales, or where the workers lived and shopped), not as ignorable; (b) excludes the two border cities from the donor or comparison pool, or models them as spillover units; (c) does not accept the consultant's 30% before-and-after fall as the tax's effect; and (d) reports no effect, estimate or diagnostic as computed or passed.'''`

`TAX_L`: `'''Treatment arm only. PASS when the reply applies nothing from the worked example that the scenario lacks: it does not give the scenario a score, cutoff, running variable, eligibility rule, earnings outcome or training; it does not recommend a regression discontinuity design; and it does not add an outcome-observation gate or response node for the sales data. A sentence that rules such a design out is not an echo.'''`

- [ ] **Step 4: Write the record skeleton.** `specs/baseline/red-baseline-causal-design-heldout.md` holds: BASE and the skill's tree hash; the item it answers; the kit's files and what changed from plan 88's kit; O1–O5 as settled at plan review; the two fixtures; every reading rule; both bars; the pre-registered verdict table; the VOID rule; the isolation command; the cost estimate and the stops; the known limits (O4's two untested parts, one model, 5 reps per arm, an unblinded reader, Codex-family controls in October); and the two readings expected to be contested: a `tax` reply that labels the effect `not identified` because no comparison is free of both the tax and the employer's move (whole-basket cross-border shopping also moves non-drink sales), and a `trial` reply that labels it `conditional` on no interference between towns. Empty Control, Treatment, Cost and Verdict sections follow.

- [ ] **Step 5: Check the prompts for leaks and for the control's shape.** Run:

```bash
uv run python specs/baseline/red-baseline-causal-design-heldout/kit/build_prompts.py leakview ~/.cache/agent-skills/scratch/plan91-work/leak
uv run python specs/baseline/red-baseline-causal-design-heldout/kit/build_prompts.py control ~/.cache/agent-skills/scratch/plan91-work/control
uv run python specs/baseline/red-baseline-causal-design-heldout/kit/build_prompts.py <BASE> ~/.cache/agent-skills/scratch/plan91-work/treatment
/usr/bin/grep -n -i -E 'DAG|graph|diagram|edge|identif|conditional|estimand|status|plausibl|Mermaid|arrow' ~/.cache/agent-skills/scratch/plan91-work/leak/*.txt ~/.cache/agent-skills/scratch/plan91-work/control/*.txt
diff ~/.cache/agent-skills/scratch/plan91-work/control/tax.txt ~/.cache/agent-skills/scratch/plan91-work/treatment/tax.txt | /usr/bin/grep -c '^<'
```

Expected: the grep prints no line. The final count is `0`: every control line is also in the treatment prompt, so the arms differ only by the texts block. The treatment `MANIFEST.txt` lists six texts (`SKILL.md` and five references). Record each count and the MANIFEST sha256 lines in the record.

- [ ] **Step 6: Commit before any rep runs.**

```bash
git add specs/baseline/red-baseline-causal-design-heldout specs/baseline/red-baseline-causal-design-heldout.md
git commit -m "$(cat <<'EOF'
test(specs): held-out evaluation kit and reading rules for plan 91

Co-Authored-By: <the session's trailer>
EOF
)"
```

### Task 2: Isolation probe, cost pilot and control arms

**Files:**
- Create: `specs/baseline/red-baseline-causal-design-heldout/control/trial/rep<N>.json`, `specs/baseline/red-baseline-causal-design-heldout/control/tax/rep<N>.json`
- Modify: `specs/baseline/red-baseline-causal-design-heldout.md`

**Interfaces:**
- Consumes: Task 1's kit, the control prompts in `~/.cache/agent-skills/scratch/plan91-work/control/`, and the treatment prompts in `~/.cache/agent-skills/scratch/plan91-work/treatment/`.
- Produces: the per-rep cap that Task 3 uses, and the control scores.

- [ ] **Step 1: Probe the isolation.** Run `bash specs/baseline/red-baseline-causal-design-heldout/kit/run_reps.sh specs/baseline/red-baseline-causal-design-heldout/kit/isolation_probe.txt ~/.cache/agent-skills/scratch/plan91-work/probe 1 1 claude-opus-5-5`.
Expected: all five probe lines read `NO`. `show_reps.py` shows one turn, no extra iterations, one model and `success`. Record `claude --version`.

- [ ] **Step 2: Run the cost pilot.** Run one unscored treatment `tax` rep: `bash specs/baseline/red-baseline-causal-design-heldout/kit/run_reps.sh ~/.cache/agent-skills/scratch/plan91-work/treatment/tax.txt ~/.cache/agent-skills/scratch/plan91-work/pilot 1 1 claude-opus-5-5 3.00`. Record its cost and its output tokens with `jq '.total_cost_usd, .usage.output_tokens' ~/.cache/agent-skills/scratch/plan91-work/pilot/rep1.json`, not with `show_reps.py`, which prints the reply. The per-rep cap stays $1.50 if the pilot cost $0.75 or less. Otherwise it is twice the pilot's cost, rounded up to the next $0.50. If that is above $3.00, stop and ask the owner. Do not read the pilot reply for scoring.

- [ ] **Step 3: Run the control arms.** For each case, run `bash specs/baseline/red-baseline-causal-design-heldout/kit/run_reps.sh ~/.cache/agent-skills/scratch/plan91-work/control/<case>.txt specs/baseline/red-baseline-causal-design-heldout/control/<case> 1 5 claude-opus-5-5 <cap>`. Rerun each VOID rep under the next free rep number. The scored reps of a case and arm are its first 5 reps that are not VOID. If two reps of one case stop on the budget, stop and ask the owner before raising the cap.
Expected: 5 scored reps per case. The spend so far is below $5.

- [ ] **Step 4: Score the control arms.** Run `show_reps.py` over both control folders. Read every reply in full. Score G, S and J for each rep by its committed rule (L is treatment-only), and quote the words that decide each verdict. Where a control gives an explicit verdict on the requested effect in its own words, note it beside S, as the October record did. Mark any reading that is a judgment call as contested, with both readings.

- [ ] **Step 5: Scan and commit.** Run `/usr/bin/grep -r -n -E '/Users/|[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[a-z]{2,}|sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{12,}|xox[abp]-' specs/baseline/red-baseline-causal-design-heldout/control`.
Expected: no line, or only lines the record explains. Record the Control scores, the VOID reruns and the spend. Then:

```bash
git add specs/baseline/red-baseline-causal-design-heldout specs/baseline/red-baseline-causal-design-heldout.md
git commit -m "$(cat <<'EOF'
test(specs): control arms for plan 91's held-out evaluation

Co-Authored-By: <the session's trailer>
EOF
)"
```

### Task 3: Treatment arms

**Files:**
- Create: `specs/baseline/red-baseline-causal-design-heldout/treatment/trial/rep<N>.json`, `specs/baseline/red-baseline-causal-design-heldout/treatment/tax/rep<N>.json`
- Modify: `specs/baseline/red-baseline-causal-design-heldout.md`

**Interfaces:**
- Consumes: the treatment prompts from Task 1 Step 5 and the cap from Task 2 Step 2.
- Produces: the treatment scores that Task 4 applies the verdict table to.

- [ ] **Step 1: Check the prompts and the version.** Compare the sha256 of each treatment prompt with the MANIFEST lines in the record. If `claude --version` differs from Task 2 Step 1, run the isolation probe again first.
Expected: the hashes match, and the probe (if run) reads `NO` on all five lines.

- [ ] **Step 2: Run the treatment arms.** For each case, run `bash specs/baseline/red-baseline-causal-design-heldout/kit/run_reps.sh ~/.cache/agent-skills/scratch/plan91-work/treatment/<case>.txt specs/baseline/red-baseline-causal-design-heldout/treatment/<case> 1 5 claude-opus-5-5 <cap>`, with the same VOID and budget-stop rules as Task 2 Step 3.
Expected: 5 scored reps per case. The kit's total is below $15.

- [ ] **Step 3: Score the treatment arms.** Read every reply in full. Score G, S, J and L for each rep. Read every echo flag that `show_reps.py` prints, and say in the record why each flagged rep passes or fails L and G (e). Quote the words that decide each verdict. Mark contested readings as in Task 2 Step 4.

- [ ] **Step 4: Scan and commit.** Run the Task 2 Step 5 scan over `specs/baseline/red-baseline-causal-design-heldout/treatment`. Record the Treatment scores, VOID reruns and spend. Commit with the message `test(specs): treatment arms for plan 91's held-out evaluation`.

### Task 4: Verdict

**Files:**
- Modify: `specs/baseline/red-baseline-causal-design-heldout.md`

**Interfaces:**
- Consumes: the control and treatment scores (Tasks 2 and 3).
- Produces: the verdict that the completion protocol writes on the backlog item.

- [ ] **Step 1: Apply the verdict table.** For each case, fill a table with one row per rule: control passes out of 5, treatment passes out of 5, the bar, met or missed. Apply the pre-registered verdict table to each case, then give the overall verdict in one sentence. A contested reading gives the verdict under each reading.

- [ ] **Step 2: Write the interpretation.** Say what the result shows and what it does not: whether the status label followed each scenario (`plausibly identified` for `trial`, `conditional` for `tax`) or echoed the worked example's `not identified`; whether the graphs carried each scenario's own threats; and the known limits from Task 1 Step 4. List each owner question for the completion gate (a missed bar, a control at 5/5, a contested reading). Write the Cost section: spend per arm and case, the probe and the pilot, and the kit's total against the $15 stop.

- [ ] **Step 3: Run the lints and commit.** Run `bash build/run_commit_lints.sh`.
Expected: `commit lints passed`. Then commit with the message `docs(specs): verdict for plan 91's held-out evaluation`.

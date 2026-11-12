# Plan 91 held-out evaluation: recommend-causal-design

This record holds the held-out evaluation for plan 91 (`specs/plans/completed/91-causal-design-heldout-eval.md`). The
evaluation tests whether the skill's two measured gains carry over to scenarios its worked example does not cover. The
two gains are an actual causal graph and the requested-estimand status contract. A rep is one fresh `claude -p` run
with no tools. Each reply is read by hand, by rules fixed in this record before any rep ran.

Two cases, each with two arms:

- `trial`: a cluster-randomized rollout of monthly home water-use reports to 12 of 24 towns. The correct label for the
  requested estimand is `plausibly identified`.
- `tax`: one city's tax on sweetened drinks, with 38 other cities as possible donors. The correct label is
  `conditional`.

The control arm gets no skill text. The treatment arm gets the shipped `SKILL.md` body and all five references whole,
the worked example included.

**Result:** at the completion gate (2026-11-12), the owner took the strict reading of every contested rule. Under
those rulings, neither case generalizes. See Owner rulings under Verdict.

## Item this answers

From `specs/deferred_items.md`, section `37-recommend-causal-design (merge review) — 2026-10-04`:

> Re-run the skill's evaluation on a held-out scenario (code-reviewer, merge review). The worked example is the
> evaluation's focal scenario, and the guided outputs track its edge list and exclusion wording; the three application
> cases ran inside one agent, with no control arm. The example was also rewritten at the merge, after the evaluation
> ran (the contract tables, the D -> R edge, a placebo row), so no evaluation covers the shipped text. Size: plan.
> Done when: a scenario the worked example does not cover runs in fresh contexts with no-guidance controls against the
> shipped skill, and the record says whether uptake of the causal graph and the status contract generalizes.

The October evaluation (`specs/completed/recommend-causal-design-evaluation.md`) found that five controls had no graph
and no explicit status label, and five guided replies had both. All five guided replies labeled the requested target
`not identified`, which is also the worked example's answer.

## Base

- BASE: `cd9fbd2b0b9e773160224ebe5fa0c3fcbe7b3587` (`main` when execution started, 2026-11-12; it holds plan 91's
  merge, `8268194`).
- The skill's tree hash at BASE (`git rev-parse BASE:skills/recommend-causal-design`):
  `99df474b3b8e66f950082a48f668b3cedf6a59af`.
- The treatment arm reads every text at BASE with `git show`, never through `~/.claude`.

`git log --oneline 9903950..BASE -- skills/recommend-causal-design` lists the nine commits that the plan names. So no
earlier evaluation covers the text under test:

```text
9905e4d fix: eleven /deferred quick fixes (2026-10-27 pass)
c53647b docs: route causal nuisance tuning to tune, add rpm knob rows, rewrite tune's README row
001efdc feat(build): every skill carries its license files, checked by check_provenance.py (portability R4.1, R4.2, R4.4)
dc3ac9a fix(recommend-causal-design): tighten five identification statements in the worked example
67f93ae fix(recommend-causal-design): correct the worked example's identification rows
26f7a52 docs: fix the text slips from the causal-design merge review
0bba8c4 docs(recommend-causal-design): credit LBS's estimand reconciliation and record the RD locator's source
3328345 docs(recommend-causal-design): make the worked example follow the memo contract
1d53743 fix(recommend-causal-design): write the memo to causal-design.md so the model recommendation can't overwrite it
```

## Kit

The kit is `specs/baseline/red-baseline-causal-design-heldout/kit/`. Four files are copies of plan 88's kit
(`specs/baseline/red-baseline-drift-followups/kit/`), and one is new. No file of plan 88's kit changed.

| File | Change from plan 88's kit |
|---|---|
| `run_reps.sh` | The temp prefix is `/tmp/plan91-rep-`. The first comment line names plan 91. |
| `isolation_probe.txt` | None (byte-identical). |
| `show_reps.py` | The docstring names plan 91. `AIDS` holds this plan's reading aids (below). |
| `build_prompts.py` | The first argument may also be `control`. The docstring names plan 91 and its three arms. |
| `cases.py` | New. It holds the two cases, the reading rules, the bars, the VOID rule and the leak pattern. |

`build_prompts.py` builds the control prompt from `FRAME` with the `{texts}` line and the blank line after it removed.
So the control prompt is byte-identical to the treatment prompt outside the texts block. The control arm reads no
repository file, and its `MANIFEST.txt` lines say `uses no texts`.

`show_reps.py`'s reading aids flag replies for the reader. They are never verdicts.

- Graph and label aids: `mermaid`, `arrows`, `plausibly` (`plausibly identified`), `conditional`, `not-identified`.
- Echo flags, words of the worked example that neither scenario has: `cutoff` (cutoff, threshold, running variable),
  `score`, `sixty` (`60`), `eligib`, `earnings`, `national`, `rd` (RD, RDD, discontinuity, rdrobust) and
  `response-node` (`R =`, response indicator or node, outcome observed).

Before the control mode existed, `build_prompts.py control` failed with `missing
skills/recommend-causal-design/SKILL.md at control` and wrote nothing. After the change it wrote both control
prompts. A check script confirmed that every fixture, rule, the task, the VOID rule and the leak pattern in
`cases.py` equal the plan's text, and that both bars equal plan 88's.

## Owner review (settled at plan review, 2026-11-12)

- **O1** (D2): two cases with different correct labels, `trial` (`plausibly identified`) and `tax` (`conditional`). A
  held-out case whose right answer is `not identified` cannot tell uptake from an echo of the worked example.
- **O2** (D3): both scenarios are held out on design family, correct label, domain and node structure. Neither has a
  score, a cutoff, eligibility, earnings, individual receipt or missing outcomes. Neither design family (an experiment
  by cluster randomization; a single treated unit with donors) appears in the worked example or in the three October
  application cases.
- **O3** (D4): every rep runs on `claude-opus-5-5`, the default model of the owner's sessions.
- **O4** (D5): the treatment arm carries the `SKILL.md` body and all five references whole. This is the worst case
  for echo.
- **O5** (D6): no word target in either arm. The executor reads every reply by hand and quotes the evidence for each
  verdict. A verdict that depends on a reading is recorded with both readings and goes to the owner. No blind panel.

## Fixtures

Both scenarios are fictional. The task line is the same for both cases:

```text
It is your turn: reply to your partner. You have no tools in this turn. If you would save a file, give its path and its full text in your reply.
```

### trial

```text
Today is 2026-11-12. The repo is the analytics project of a regional water utility. It holds no data yet: the data stay in the utility's warehouse.

[partner] We need a causal design recommendation, not estimation yet. Last year we ran a trial of monthly home water-use reports, which compare a household's use with its neighbors'. We serve 58 towns. We chose the 24 towns that have smart meters for the trial; they are separate communities, at least 10 miles apart. A random draw picked 12 of the 24 to get the reports; the other 12 got nothing new. From March 2025 we mailed a report every month to every household in the 12 report towns. Nobody could opt out, and we have no record of who read the reports. We have monthly meter reads for every household in the 24 towns from March 2023 to February 2026, about 2.1 million reads in all, with household size and lot size from our billing records. In July 2025 a regional drought order limited lawn watering in all 58 towns. During the trial some households signed up for a rebate on low-flow fixtures, and sign-ups were higher in the report towns. Our board asks: did mailing the reports cut household water use in the trial towns over the 12 months from March 2025? Our analyst wants to compare each household's use before and after March 2025, controlling for household size, lot size and rebate sign-up, and says that with 2.1 million reads the standard errors will be tiny. Please recommend a primary approach plus alternatives, the assumptions, the evidence we need, and a handoff for implementation. Write the recommendation now: where you need a fact we have not given, state what you assume and list the question at the end. Don't fit anything.
```

### tax

```text
Today is 2026-11-12. The repo is the analytics project of a city health department. It holds no data yet: the data stay with the department's data team.

[partner] We need a causal design recommendation, not estimation yet. On 1 July 2025 our city, Larkford, put a tax of 1.5 cents per ounce on sweetened drinks. No other city in the state has one. Did the tax cut sweetened-drink sales in Larkford's stores in its first 12 months? We have weekly sales by store, for taxed sweetened drinks, for untaxed drinks (water, unsweetened tea, milk) and for all other grocery items, from January 2021 to June 2026, for Larkford and 38 other cities in the state, with store openings and closings, and city population and median income by year. Two of the 38 cities border Larkford, and shoppers can drive to their stores. In the same month the tax started, Larkford's largest employer moved 3,000 jobs out of its downtown site; 6 of Larkford's 41 stores are downtown. Nobody has yet checked where those workers lived or shopped. A consultant compared Larkford's sales before and after the tax and says sales fell 30%. We would like to use synthetic control. Please recommend a primary approach plus alternatives, the assumptions, the evidence we need, and a handoff for implementation. Write the recommendation now: where you need a fact we have not given, state what you assume and list the question at the end. Don't fit anything.
```

## Reading rules

A rep passes a rule only when it meets every part of it. Not PASS means FAIL. G and S are additive rules. J is a
non-regression rule. L is a treatment-only guard against echo of the worked example.

### trial

- **G** (graph): PASS when the reply holds an actual graph of the trial: a Mermaid block, an ASCII diagram, or an edge list with at least four directed edges written with arrows (->, → or -->) between named variables. Prose about causes, or a promise to draw a graph later, does not count. The graph or its node definitions must (a) say when the report mailing and the outcome happen (dates, periods or time-indexed nodes); (b) include at least one node marked unobserved; (c) show the random assignment of towns with no arrow into it from a covariate, confounder or outcome node (an arrow from the random draw itself is allowed); (d) include rebate sign-up as a node with a directed path into it from the assignment or the reports; and (e) import no node the trial lacks: no score, cutoff, eligibility, earnings or training node, and no node for whether the outcome was observed, since every meter read exists.
- **S** (status contract): PASS when the reply (a) names the requested estimand: the effect of mailing the reports on household water use in the 24 trial towns over the 12 months from March 2025, with a plain-language definition; (b) labels that estimand with one of the exact phrases "plausibly identified", "conditional" or "not identified", and the label is "plausibly identified"; (c) gives a reason for the label tied to the assignment, the support or the assumptions; (d) keeps every other estimand it raises (for example, the effect in the other 34 towns or the effect of reading a report) defined apart from the requested one, and does not put one in its place; and (e) states what would change the recommendation, including whether estimation should wait.
- **J** (judgment): PASS when the reply (a) makes its primary design the comparison of report towns with non-report towns as randomized, not the analyst's before-and-after comparison of households; (b) does not adjust for rebate sign-up in the primary analysis, and says why (it comes after assignment); (c) plans inference at the town level or says that 24 towns, not 2.1 million reads, limit the precision; and (d) reports no effect, estimate or diagnostic as computed or passed.
- **L** (no echo): Treatment arm only. PASS when the reply applies nothing from the worked example that the trial lacks: it does not give the trial a score, cutoff, running variable, eligibility rule, earnings outcome or training; it does not recommend a regression discontinuity design; and it does not add an outcome-observation gate or response node, since every meter read exists. A sentence that rules such a design out (for example, "there is no threshold, so RD does not apply") is not an echo.

### tax

- **G** (graph): PASS when the reply holds an actual graph of the tax: a Mermaid block, an ASCII diagram, or an edge list with at least four directed edges written with arrows (->, → or -->) between named variables. Prose about causes, or a promise to draw a graph later, does not count. The graph or its node definitions must (a) say when the tax, the outcome and the employer's move happen (dates, periods or time-indexed nodes); (b) include at least one node marked unobserved; (c) show the employer's move as a node with an arrow into Larkford's sales; (d) show the cross-border shopping: an arrow from the tax (or Larkford's prices) to a cross-border shopping node or to the two border cities' sales; and (e) import no node the scenario lacks: no score, cutoff, eligibility, earnings or training node, and no node for whether the outcome was observed. A node for store openings and closings is allowed.
- **S** (status contract): PASS when the reply (a) names the requested estimand: the effect of the tax on sweetened-drink sales in Larkford's stores in the 12 months from July 2025, with a plain-language definition; (b) labels that estimand with one of the exact phrases "plausibly identified", "conditional" or "not identified", and the label is "conditional"; (c) gives a reason for the label tied to the assignment, the support or the assumptions; (d) keeps every other estimand it raises (for example, the effect on what residents drink, or the effect of a statewide tax) defined apart from the requested one, and does not put one in its place; and (e) states what would change the recommendation, including whether estimation should wait.
- **J** (judgment): PASS when the reply (a) treats the employer's move as a threat that needs separating evidence (for example, stores away from downtown, the non-drink grocery sales, or where the workers lived and shopped), not as ignorable; (b) excludes the two border cities from the donor or comparison pool, or models them as spillover units; (c) does not accept the consultant's 30% before-and-after fall as the tax's effect; and (d) reports no effect, estimate or diagnostic as computed or passed.
- **L** (no echo): Treatment arm only. PASS when the reply applies nothing from the worked example that the scenario lacks: it does not give the scenario a score, cutoff, running variable, eligibility rule, earnings outcome or training; it does not recommend a regression discontinuity design; and it does not add an outcome-observation gate or response node for the sales data. A sentence that rules such a design out is not an echo.

### Readings expected to be contested

Two readings are expected to be judgment calls. Each goes to the owner with both readings if it occurs.

1. A `tax` reply that labels the effect `not identified`, because no comparison is free of both the tax and the
   employer's move. Whole-basket cross-border shopping also moves non-drink sales, so the non-drink sales are not a
   clean check either. Under the rule as written this fails S (b).
2. A `trial` reply that labels the effect `conditional` on no interference between towns. Under the rule as written
   this fails S (b).

## Bars

Copied word for word from plan 88's `cases.py`:

- `ADDITIVE_BAR`: `treatment 5/5; control fails at least 1 of 5`. It applies to G and S.
- `NON_REGRESSION_BAR`: `treatment >= 4/5, and >= control - 1 passes; a miss stops the task for an owner ruling`. It
  applies to J.
- L: `treatment 5/5`.

## Pre-registered verdict

For each case, each element gets one verdict:

| Element | Result | Verdict for the element |
|---|---|---|
| G, S | `ADDITIVE_BAR` met: treatment 5/5, control fails at least 1 of 5 | Uptake generalizes |
| G, S | Treatment 5/5, control 5/5 | Present without the skill on this model: the skill is not shown necessary |
| G, S | Treatment 4/5 or fewer | Uptake does not generalize |
| L | Treatment 5/5, or else fewer | No echo, or else the treatment echoes the worked example |
| J | `NON_REGRESSION_BAR` met, or else missed | Causal judgment kept, or else the skill lowers it |

A case generalizes when G and S generalize, L has no echo and J keeps judgment. The overall verdict is "generalizes"
only when both cases generalize. Any other verdict goes to the owner at the completion gate. There is no wording
round, and no file under `skills/` changes.

## VOID rule

VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply says nothing about the partner's causal question. A reply that only asks questions is not VOID: it is scored, and it fails every rule it does not meet.

The scored reps of a case and arm are its first 5 reps that are not VOID.

## Isolation

Every rep runs under `env -i` from its own new, empty directory under `/tmp`, outside every git repository:

```bash
env -i HOME=... USER=... LOGNAME=... PATH=... SHELL=... TMPDIR=... LANG=... \
  CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
  claude -p --model claude-opus-5-5 --tools "" --strict-mcp-config --setting-sources "" \
  --no-session-persistence --output-format json --max-budget-usd <cap> < <prompt>
```

So no repository `CLAUDE.md`, no user-level `CLAUDE.md` or rules, no output style, no hooks and no auto-memory reach
a rep. `run_reps.sh` enforces this. The isolation probe (`isolation_probe.txt`) checks it before the first rep.

## Cost estimate and stops

- A treatment prompt is about 56.7 KB (the plan estimated about 56 KB). A control prompt is about 1.9 to 2.1 KB.
- Expected spend: 10 treatment reps at about $0.25, 10 control reps at about $0.10, plus the probe and the pilot, about
  $4 in all.
- The per-rep cap is $1.50, unless the Task 2 pilot sets another cap. A pilot cap above $3.00 stops the run for the
  owner.
- Stop and ask the owner when the whole kit passes $15, or when the control arms alone pass $5.
- Two reps of one case that stop on the budget stop the run for the owner before any cap rises.

## Leak check

Run before any rep, on the prompts built from the kit:

```bash
uv run python specs/baseline/red-baseline-causal-design-heldout/kit/build_prompts.py leakview ~/.cache/agent-skills/scratch/plan91-work/leak
uv run python specs/baseline/red-baseline-causal-design-heldout/kit/build_prompts.py control ~/.cache/agent-skills/scratch/plan91-work/control
uv run python specs/baseline/red-baseline-causal-design-heldout/kit/build_prompts.py cd9fbd2b0b9e773160224ebe5fa0c3fcbe7b3587 ~/.cache/agent-skills/scratch/plan91-work/treatment
/usr/bin/grep -n -i -E 'DAG|graph|diagram|edge|identif|conditional|estimand|status|plausibl|Mermaid|arrow' ~/.cache/agent-skills/scratch/plan91-work/leak/*.txt ~/.cache/agent-skills/scratch/plan91-work/control/*.txt
diff ~/.cache/agent-skills/scratch/plan91-work/control/tax.txt ~/.cache/agent-skills/scratch/plan91-work/treatment/tax.txt | /usr/bin/grep -c '^<'
```

Results:

- The leak grep printed no line (exit 1). The frame, the fixtures and the task name no shape under test.
- The diff count is `0` for `tax` and `0` for `trial`. A direct check also passed: each treatment prompt with its
  texts block removed is byte-identical to the control prompt. The texts block is 54,837 bytes in both cases.
- Each treatment prompt holds six texts: one `<skill name="recommend-causal-design">` block and five `<file>` blocks
  (`design-map.md`, `identification.md`, `reporting.md`, `sources.md`, `worked-example.md`). The treatment
  `MANIFEST.txt` names the two path patterns (`SKILL.md` and `references/*.md`), as the copied code writes them.

The MANIFEST sha256 lines:

```text
arm control
tax.txt sha256 c814a93d77593409a1c1cd72be21a71d45d7f8828ca58cd26f638a80baabaf80 model claude-opus-5-5 budget 1.50 uses no texts
trial.txt sha256 a71e333630aae03cb7a1debbff4f815f200e04919caea94711d7159d149602bd model claude-opus-5-5 budget 1.50 uses no texts
arm cd9fbd2b0b9e773160224ebe5fa0c3fcbe7b3587
tax.txt sha256 10d562bae03f9f0ab40f684890f5fdcfdb57928f900d15cf47a6662b1e1624c3 model claude-opus-5-5 budget 1.50 uses skills/recommend-causal-design/SKILL.md,skills/recommend-causal-design/references/*.md
trial.txt sha256 de72d2b1d919751fac184b2a2a3a9d62bea4c5ce023f1d2f73086d10bb7c966c model claude-opus-5-5 budget 1.50 uses skills/recommend-causal-design/SKILL.md,skills/recommend-causal-design/references/*.md
```

## Known limits

- **Pointer pull (O4).** The treatment arm carries every reference whole. It does not test whether an agent opens
  each reference from its pointer in `SKILL.md`.
- **Trigger (O4).** The treatment arm states that the skill is loaded. It does not test whether the description
  triggers the skill.
- **One model.** Every rep runs on `claude-opus-5-5`. The result says nothing about other models.
- **5 reps per arm.** A 5/5 against 4/5 split is weak evidence of a difference.
- **An unblinded reader.** The executor knows each rep's arm while reading it.
- **October's controls.** The October arms ran on a Codex-family agent, so the controls here may be stronger. The two
  evaluations do not compare like for like.

## Isolation probe

Run 2026-11-12 on Claude Code `2.1.322`, before any scored rep, with `run_reps.sh` and its default $0.50 cap:

```text
1. NO
2. NO
3. NO
4. NO
5. NO
```

`show_reps.py` showed one turn, no extra iterations, one model and `success`, at a cost of $0.006. No `CLAUDE.md`,
output style, rule, SessionStart hook or auto-memory reached the rep.

## Cost pilot

One unscored treatment `tax` rep under a $3.00 cap cost $0.434, with 13,767 output tokens. The pilot cost is $0.75 or
less, so the per-rep cap stays at **$1.50** for every scored rep. The reply was not read. The output is about three
times the plan's estimate of 3,000 to 5,000 tokens. The projected total for the kit is still about $9, under the $15
stop.

## Control

Both control arms ran on 2026-11-12 under the $1.50 cap, `trial` and `tax` in parallel. All 10 reps are scored: no rep
is VOID. Each header reads `success`, one turn, no extra iterations and one model. Every reply was read in full.

| Case | G | S | J |
|---|---|---|---|
| `trial` | 0/5 | 0/5 | 5/5 |
| `tax` | 0/5 | 0/5 | 5/5 |

No control reading is a judgment call. No control reply holds a graph, and no control reply uses one of the three
exact status labels for the requested estimand. All ten replies meet every part of J.

Common shape: every control reply is a design memo with a defined estimand, assumptions, evidence, alternatives and
a handoff. Every reply also rejects the partner's naive comparison. The `show_reps.py` aids flagged `arrows` in
`trial` reps 1 and 5 and `tax` rep 4. Each flagged arrow sits inside a prose sentence, not an edge list. The `cutoff`
flag in `trial` reps 2 and 3 and `tax` rep 2 marks a trimming cutoff or a pre-period cutoff date, not a threshold
design. The `not-identified` flag in `trial` rep 2 marks the effect of reading a report, not the requested estimand.

### trial

- **rep1.** G FAIL: no graph. Its only arrows are in prose: "random draw of 12 of 24 towns → report and control towns
  are comparable in expectation". S FAIL on (b): it calls the ITT "the natural and fully identified estimand", which
  is not one of the exact labels. Its own verdict on the requested effect is "fully identified". Parts (a) and (c)
  are met: "The average effect of *assigning a town to receive mailed reports* on household water use ... among
  households in the 24 trial towns". J PASS: (a) "comparing the 12 report towns with the 12 control towns"; (b)
  "Controlling for rebate sign-up would bias the estimate. Sign-up happened after randomization ... It is a mediator";
  (c) "Inference should come from **randomization inference over the actual 12-of-24 draw**"; (d) its minimum
  detectable effect is a hypothetical, and nothing is reported as computed.
- **rep2.** G FAIL: no graph, only a file tree. S FAIL on (b): the requested ITT has no exact label. The phrase "not
  identified" appears only for "the effect of reading". Its own verdict: "Randomization therefore still gives an
  unbiased ITT for the period." J PASS: (a) "Primary approach: town-level randomization analysis with baseline
  adjustment"; (b) "Rebate sign-up is a post-treatment variable (a 'bad control'). The reports raised sign-ups ... Do
  not adjust for it"; (c) "with town as the unit of inference"; (d) nothing computed.
- **rep3.** G FAIL: no graph. S FAIL on (b): no exact label. Part (a) is met: the "average difference in household
  water use ... between the outcome under 'town receives reports' and under 'town receives nothing new'" over the 24
  trial towns. J PASS: (a) "Compare report towns with control towns over Mar 2025 – Feb 2026"; (b) "Rebate sign-up
  must not be a control ... It is a mediator"; (c) "randomization inference at the town level" and "The design has 24
  independent units (12 vs 12), not 2.1M"; (d) nothing computed.
- **rep4.** G FAIL: no graph. S FAIL on (b): no exact label. Its own verdict: "its validity rests on the random draw
  alone". Part (a) is also not met: the estimand is "for households in the 12 report towns", not the 24 trial towns.
  J PASS: (a) "Primary analysis: town-level ANCOVA with randomization inference"; (b) "Rebate sign-up is an outcome of
  the reports, not a control"; (c) "The real information is closer to **24 independent units** than 2.1 million";
  (d) nothing computed.
- **rep5.** G FAIL: no graph. S FAIL on (b): its own verdict is "the effect of mailing is identified cleanly", which
  is not an exact label. Part (a) is met: "the average effect, per household, of *mailing* monthly reports for 12
  months in the 24 smart-meter towns". J PASS: (a) "Town-level comparison adjusted for baseline, with randomization
  inference"; (b) "Rebate sign-up must not be a control variable ... they are likely an *effect* of the reports"; (c)
  "base inference on the **24 towns**, not the 2.1 million reads"; (d) it cites effects from comparable programs and
  computes nothing.

### tax

- **rep1.** G FAIL: no graph, only a file tree. S FAIL on (b): no exact label. Part (a) is met: "The average
  percentage difference in weekly **volume (ounces)** of taxed sweetened drinks sold per resident in Larkford stores,
  July 2025–June 2026". Its primary treated unit leaves out the 6 downtown stores, and it says "the estimand covers
  non-downtown stores only". J PASS: (a) the downtown stores are left out of the primary unit, and the first evidence
  item is "Where the 3,000 workers lived"; (b) "**Exclude the two border cities.**"; (c) "The 30% figure should be
  described as a raw change, not as the effect of the tax"; (d) nothing computed.
- **rep2.** G FAIL: no graph. S FAIL on (b): no exact label. Part (a) is met: "The average percent difference, over
  the 52 post-tax weeks ..., between observed taxed-drink **volume** sold in Larkford stores, and the volume those same
  stores would have sold without the tax". J PASS: (a) "Primary sample excludes the 6 downtown stores", "'All other
  grocery' serves as a negative-control outcome" and "Find out where the workers lived and shopped"; (b) "Exclude both
  from the donor pool"; (c) "The 30% should be treated as an upper-bound sanity check, not as an estimate"; (d)
  nothing computed.
- **rep3.** G FAIL: no graph. S FAIL on (b): no exact label. Part (a) is met: "For Larkford stores, this is the
  average percentage difference, across the 52 post-tax weeks, between observed taxed-drink **volume** ... and the
  volume that would have occurred with no tax". J PASS: (a) the downtown stores are left out, with "R1.
  Category-differenced SCM (the main check on the employer confound)" and "Where the 3,000 workers lived"; (b)
  "Exclude the 2 border cities from the donor pool"; (c) "It may be too large or too small. We should not cite it as
  an effect size"; (d) nothing computed.
- **rep4.** G FAIL: no graph. Its one arrow is in prose: "Negative control: other grocery → apply the decision rule".
  S FAIL on (b): no exact label. Part (a) is met: "the percent change in taxed sweetened-drink **volume (ounces)**
  sold in Larkford stores over the 52 post-tax weeks, compared with what those stores would have sold without the
  tax". J PASS: (a) "The **job move is the main threat**", handled with an other-grocery negative control, a split of
  downtown and non-downtown stores, and a question on where the workers lived; (b) "The 2 border cities are
  **excluded**"; (c) "The 30% may be close to right, too high, or too low. We cannot tell without a counterfactual";
  (d) nothing computed.
- **rep5.** G FAIL: no graph. S FAIL on (b): no exact label. Part (a) is met: "Percent difference between Larkford's
  actual taxed-drink VOLUME per capita ... and the volume it would have had without the tax. Averaged over the 52 post
  weeks". J PASS: (a) "The employer move (main threat)", with a traffic test on other grocery, a pre-set decision rule
  and a downtown exclusion; (b) "Exclude the 2 border cities from the donor pool"; (c) "Why the consultant's 30% is
  not an estimate of the tax effect"; (d) nothing computed.

### Spend (control)

| Item | Cost |
|---|---|
| Isolation probe | $0.006 |
| Cost pilot (unscored) | $0.434 |
| Control `trial`, reps 1–5 | $0.609 |
| Control `tax`, reps 1–5 | $0.670 |
| Total so far | $1.719 |

The control arms cost $1.279, under the $5 stop. No rep stopped on its budget.

## Treatment

Both treatment arms ran on 2026-11-12 under the $1.50 cap, `trial` and `tax` in parallel. Before the run, the sha256
of each treatment prompt matched the MANIFEST lines above. `claude --version` was still `2.1.322`, so the isolation
probe did not run again. All 10 reps are scored: no rep is VOID. Each header reads `success`, one turn, no extra
iterations and one model. Every reply was read in full.

Every treatment reply is a memo in the skill's contract shape. Each has a requested causal question, a requested
estimand, a design status, alternative estimands, recommendation-changing conditions, a graph, an assumptions table, a
candidate table, a diagnostic plan, a handoff and open questions.

### Scores

A cell such as `2/5 or 5/5` gives the count under reading A, then under reading B. In every contested reading, A is
the stricter reading that follows the rule's words, and B is the alternative. The contested readings are defined
below.

| Case | G | S | J | L |
|---|---|---|---|---|
| `trial` | 0/5 (C3-A); 3/5 or 5/5 under C3-B (C4) | 5/5 | 5/5 | 0/5 or 5/5 (C3) |
| `tax` | 1/5, 2/5, 3/5 or 5/5 (C1, C4) | 2/5 or 5/5 (C2) | 5/5 | 4/5 or 5/5 (C3) |

`tax` G is 1/5 under C1-A and C4-A, 2/5 under C1-A and C4-B, 3/5 under C1-B and C4-A, and 5/5 under C1-B and C4-B.

The parts of each rule that are not contested pass in every rep. Every `trial` graph meets G (b), (c) and (d), and
reps 2, 4 and 5 also meet G (a). Every `tax` graph meets G (b), (d) and (e), and reps 1, 2 and 4 also meet G (a).
Every reply meets S (a), (b), (c) and (e), with the correct label: `plausibly identified` for
all five `trial` replies and `conditional` for all five `tax` replies. No treatment reply labels its requested
estimand `not identified`.

### Contested readings

Each contested reading is a judgment call for the owner at the completion gate. This record does not resolve them.
C1 to C4 came up while the replies were read. They were not pre-registered. Neither of the two readings that the
record expected before any rep ran occurred: no `tax` treatment reply labels its estimand `not identified`, and no
`trial` treatment reply labels its estimand `conditional`.

- **C1. `tax` G (c): a direct arrow, or a path through a mediator?** Rule G (c) asks for "the employer's move as a
  node with an arrow into Larkford's sales". Reps 1, 2 and 3 draw the move only through a traffic node: `E -->
  F[Downtown foot traffic] --> Y` (rep 1), `JM --> FD[Downtown footfall] --> TV` (rep 2) and `J --> FD[Downtown store
  traffic] --> YS` (rep 3). Reps 4 and 5 also have a direct arrow: "JobMove → non-downtown Larkford sales" (rep 4)
  and `REL -.disputed.-> Y` (rep 5).
  - Reading A (the rule's words: "an arrow into" means a direct edge): reps 1–3 FAIL G (c). G is 2/5.
  - Reading B (a directed path through a named traffic node shows the move as a cause of Larkford's sales, and it
    says more than a bare arrow, since it names the mechanism): reps 1–3 PASS. G is 5/5.
  - A point for reading A: the same plan wrote "a directed path into it" for the `trial` rebate node (`TRIAL_G`
    (d)) but "an arrow into" for the `tax` employer node. The different wording suggests that a direct arrow was
    meant here.
- **C2. `tax` S (d): a labeled, narrower estimand as the primary analysis.** Rule S (d) asks that every other
  estimand stay "defined apart from the requested one" and that the reply "does not put one in its place". Reps 2, 3
  and 4 define the non-downtown-store effect apart and say it is not the requested target. But they make it the
  primary analysis.
  - Rep 2: "none of them alone is the requested target", but "**Primary choice: A, run on the non-downtown series**",
    "E1 (non-downtown, primary)" and "E1 is the requested target if (a) holds".
  - Rep 3: "(each separate; neither silently replaces τ)", but "**Primary design:** candidate (b) SC" and "(b)
    primary".
  - Rep 4: "It answers the original question only for those stores", but "Analysis primary: A1".
  - Reps 1 and 5 keep the all-store requested estimand as the primary analysis. Rep 1 reports "the city total and A1
    side by side". Rep 5 reports the effect "for all 41 stores and for the 35 non-downtown stores".
  - Reading A (making a narrower estimand the primary analysis puts it in the requested one's place): reps 2–4 FAIL
    S (d). S is 2/5.
  - Reading B (the alternative stays labeled, and the reply names the condition under which it answers the
    question): reps 2–4 PASS. S is 5/5.
- **C3. An outcome-observation node or gate.** Rule `TRIAL_G` (e) bans "a node for whether the outcome was observed,
  since every meter read exists". Rule `TRIAL_L` bans "an outcome-observation gate or response node". Rule `TAX_L`
  bans "an outcome-observation gate or response node for the sales data". All five `trial` treatment replies add such
  a node, drawn dashed, marked disputed or "assumed negligible". Reps 1, 3, 4 and 5 also add a gate on missing reads
  or household turnover by arm, and rep 2 adds a check with bounds. One `tax` reply (rep 2) adds an outcome-observation gate on store reporting, with no node.
  - `trial` nodes: `S[Post read observed]` (rep 1), `S[Has reads / in cohort]` (rep 2), `R[Read/account observed]`
    (rep 3), `S[Observed in post?]` (rep 4) and `O[Read observed / account active]` (rep 5). Each reply ties the node
    to household turnover, account closures or estimated reads.
  - `tax` rep 2: "Outcome observation: store data complete, no reporting changes at the tax ... Gate if Larkford's
    reporting changed in July 2025", and in §9 "Outcome observation gate".
  - The source is not only the worked example. In the skill's `SKILL.md` quick reference, the row for random
    assignment names its key gate as "Randomization, outcome observation, interference". The generic template graph
    in `references/identification.md` has `T --> S[Outcome observed? S]` and `Y --> S`. `references/reporting.md`
    lists outcome observation among the threats to review. The worked example also uses the phrase
    "outcome-observation gate" (`references/worked-example.md`, lines 30 and 163 at BASE).
  - Reading A (the rules' words): every `trial` rep FAILS G (e) and L, so `trial` G is 0/5 and L is 0/5. `tax` rep 2
    FAILS L, so `tax` L is 4/5.
  - Reading B differs for the two rules, and the owner may rule on them apart.
    - For L, whose header limits it to what the reply "applies ... from the worked example": the item comes from the
      skill's generic contract for experiments and its template graph, not from the worked example's missing
      earnings. Under B, every rep PASSES L: `trial` L is 5/5 and `tax` L is 5/5.
    - For G (e), the source does not matter ("import no node the trial lacks"). Only the scenario argument applies:
      a 12-month household cohort has account turnover, so whether a household's reads are observed is part of the
      trial. The control replies support this. They raise turnover by arm with no skill text: "Attrition/turnover
      unrelated to assignment" (control `trial` rep 2), "**Attrition is balanced.** Account closures and moves are
      similar across arms" (rep 5), "Report attrition (account closures, ownership changes) by arm" (rep 4) and
      "Cohort definition is not affected by treatment (moving, account closure)" (rep 3). Under B, every `trial` rep
      PASSES G (e).
- **C4. G (a): a node with no date of its own.** Rule G (a) asks that the graph or its node definitions say when the
  named events happen: for `trial`, "the report mailing and the outcome"; for `tax`, "the tax, the outcome and the
  employer's move". In four replies, a named node carries no date, dated period or index of its own, and only timing
  stated elsewhere in the graph section places it. The final whole-branch review found that this record first
  applied the test to `trial` only, and the fix pass widened it to `tax`.
  - `trial` rep 1: "Edge list (time-indexed; Z = town assignment, randomized pre-March 2025)", `Ypre[Y pre-period]`,
    `Ypost[Y post-period]` and "Exclude any measured after time zero" beside "Post-March 2025 household
    attributes". Its pathway "Z → Mailing → Reading (unobserved) → Behavior → Y_post" gives the mailing no date.
  - `trial` rep 3: "Edge list (time-indexed; t0 = March 2025)" and `Y[Use Mar25-Feb26]`. Its pathway "`A -> Mail ->
    Read(U) -> Behavior -> Y_post`" and its node `Mail[Monthly report mailed]` give the mailing no date. Only §1 says
    "Time zero is the first mailing in March 2025".
  - `tax` rep 5: the edge table's header "Edge list, with time indexing by month t" and its row "Tax (Larkford, from
    Jul 2025)" date the index and the tax. The outcome node `Y[Taxed-drink sales, Larkford stores]` and the row "...
    → taxed-drink sales in Larkford stores" carry no date, period or index.
  - `tax` rep 3, the closest call: "T, J: week of 1 July 2025" and the definition line "Y: weekly outcomes" give the
    outcome a frequency, not a window. The graph node `YS[Larkford sweetened volume]` carries no index. Only
    `YSpre[Late pre-period sweetened sales]` implies that `YS` is the post-period.
  - The other six replies carry the timing on the node or in a definition line that dates it: `trial` rep 2 "Mail_T
    [Mar 2025 onward]"; `trial` rep 4 "M: reports mailed (post)" with "post = Mar 2025–Feb 2026"; `trial` rep 5
    `Mail[Reports mailed monthly from Mar 2025]`; `tax` rep 1 "Nodes are time-indexed as pre-period (Jan 2021–Jun
    2025) and post-period (Jul 2025–Jun 2026)"; `tax` rep 2 "Edge list, time-indexed (pre = before 1 Jul 2025, post
    = Jul 2025–Jun 2026)" with `Taxed_vol_post`; `tax` rep 4 `Y_S,L(t)` on the index of `Tax_L(t≥July 2025)`.
  - Reading A (each named node must carry its own date, dated period or index, on the node or in a definition line
    that dates it; a time-indexed header or a time zero stated elsewhere does not date a node that carries none):
    `trial` reps 1 and 3 and `tax` reps 3 and 5 FAIL G (a).
  - Reading B (timing stated elsewhere in the graph section, such as a time-indexed header, a time zero or a pre/post
    split, places a node with no date of its own): all four PASS G (a).
  - Effects. For `trial`, C4 matters only under C3-B, since under C3-A every `trial` rep already fails G on (e).
    Under C3-B, `trial` G is 3/5 under C4-A and 5/5 under C4-B. For `tax`, see the counts under Scores. Rep 3 alone
    changes no verdict: with rep 5 failing under C4-A, `tax` G misses the bar under C4-A either way.

### Store and household cohorts (not scored)

The final review's Codex seat raised one more point. `tax` rep 5's primary analysis uses "stores open throughout",
with "all stores" only as a sensitivity check. That may narrow "Larkford's stores" if stores opened or closed, and a
tax-caused closure would then drop out. The fact holds, and it holds for every reply. Every `tax` treatment reply makes
a fixed store cohort its primary sample: rep 1 "the fixed pre-tax store cohort" (with "Closures after July 2025 may
themselves be outcomes"), rep 2 "Use a balanced panel for the primary estimate", rep 3 "as a balanced store panel",
rep 4 "Restrict to stores open throughout" and rep 5 "Primary: stores open throughout". All five `tax` controls do
the same. Every `trial` reply in both arms makes a cohort of households active at time zero its primary sample.

This record does not score the cohort under S (d). S (d) asks about "every other estimand it raises", and the
replies raise no separate estimand for the cohort. They treat it as the sample that handles store or household
turnover, and they report an all-unit version or a cohort comparison beside it. A reading that counts the cohort as
a narrower estimand would fail S in every treatment reply of both cases. It would not separate the arms, since the
controls fail S on (b) already. This is a ruling of the executor's, and it goes to the owner at the completion gate
with the other rulings.

### Echo flags

`show_reps.py` flagged `eligib` in every `trial` rep and in `tax` reps 1, 2, 4 and 5, and `rd` in `trial` reps 2
and 4. No rep was flagged for `cutoff`, `score`, `sixty`, `earnings`, `national` or `response-node`.

- `eligib`, `trial`: "24 of 58 towns eligible: those with smart meters" (reps 1, 4, 5) restates the fixture's own
  selection of the 24 smart-meter towns. "Covariate eligibility" (reps 1, 3, 5) asks whether a covariate was measured
  before March 2025. Rep 2's "eligibility/advertising" is the rebate program's. None gives the trial an eligibility
  rule, and no graph has an eligibility node. Rep 5's `Sel[Smart-meter selection of 24 towns]` node is the fixture's
  own selection. These flags pass L and G (e).
- `eligib`, `tax`: every hit is donor eligibility for synthetic control ("36 eligible donors", "Donor eligibility: no
  spillover into donors", and Abadie (2021) cited for "donor eligibility"). None is an eligibility rule from the
  worked example. These flags pass L.
- `rd`, `trial` reps 2 and 4: the node `Rd[Read_i unobserved]` or `Rd[Read report - unobserved]` stands for reading
  the report. No reply recommends or mentions a regression discontinuity design. These flags pass L.
- The `not-identified` flag in every treatment rep marks estimands other than the requested one, such as the effect
  of reading a report, the effect in all 58 towns, or a fallback if a gate fails. It does not mark the requested
  estimand.
- No treatment reply gives either scenario a score, a cutoff, a running variable, an earnings outcome or training.

### trial

- **rep1.** G: (a) contested (C4): "Edge list (time-indexed; Z = town assignment, randomized pre-March 2025)", with
  `Ypre[Y pre-period]`, `Ypost[Y post-period]` and `D[Drought order Jul 2025, all towns]`, but no date on the
  mailing; (b) `U[U_town unobserved]` and
  `Read[Read report, unobserved]`; (c) no arrow into Z, with "no arrow from U_town, X_hh or Y_pre into Z"; (d) `Z -->
  Read`, `Read --> R[Rebate sign-up]`; (e) contested (C3): `Z --> S[Post read observed]`, `Ypost -.-> S`. S PASS: (a)
  "ITT of report mailing ... averaged over households in the 24 trial towns"; (b) "**Design status:** `plausibly
  identified`"; (c) "Towns were assigned by a random draw, every household in report towns was mailed, and nobody
  could opt out"; (d) the effect of reading is "a separate target. It is not identified", and "Separate, not
  substitutes"; (e) "Estimation should wait for the randomization record and the missing-read audit". J PASS: (a)
  "analyze the trial as a **cluster-randomized experiment**"; (b) rebate sign-up "is post-treatment ... Adjusting for
  it removes part of the effect"; (c) "2.1M reads are repeated measures within those towns and do not add assignment
  units"; (d) "no diagnostics or effects have been computed". L: contested (C3): "Outcome observation ... **Gate** if
  missingness differs by arm".
- **rep2.** G: (a) "Z_T [assigned before Mar 2025] -> Mail_T [Mar 2025 onward]", `Y_i,post` and "D_t [Jul 2025, all
  towns]"; (b) `Rd[Read_i unobserved]`, `U[U_i motivation unobserved]`; (c) "**Absent edge by design: V_T -/->
  Z_T**"; (d) `M --> R[Rebate sign-up R_i]`; (e) contested (C3): `Z --> S[Has reads / in cohort]`. S PASS: (a) "the
  ITT effect of *mailing* the reports ... all trial towns are mailed reports, versus none are", for "households in the
  24 smart-meter trial towns"; (b) "**Design status:** `plausibly identified`"; (c) "Random assignment of towns gives
  the comparison as-if-random exchangeability"; (d) "(separate; none replaces the primary)"; (e) "Estimation should
  wait for the confirmations in §9 Q1–Q3". J PASS: (a) "comparing report towns with control towns"; (b) rebate sign-up
  is "a mediator ... It also opens Z -> R <- U -> Y, a collider path"; (c) "The precision limit is about 12 towns
  against 12"; (d) "nothing has been fitted". L: contested (C3): the node S and "Outcome observation and cohort not
  affected by assignment".
- **rep3.** G: (a) contested (C4): "Edge list (time-indexed; t0 = March 2025)", `Y[Use Mar25-Feb26]`, `Ypre[Use
  Mar23-Feb25]`, but no date on `Mail[Monthly report mailed]`; (b)
  `Read[Read / engaged - unobserved]`, `U[Conservation-mindedness - unobserved]`; (c) "`Rand -> A` ... No other node
  causes A"; (d) `Mail --> Rebate[Rebate sign-up]`; (e) contested (C3): `Y -.-> R[Read/account observed]`, `A -.->
  R`. S PASS: (a) "the ITT of town assignment to mailed reports ... over Mar 2025–Feb 2026"; (b) "**Design status for
  that estimand:** `plausibly identified`"; (c) "Assignment was a random draw of 12 of 24 towns"; (d) "(separate; none
  replaces the target)"; (e) "Estimation should wait only for the randomization record and the data definitions in
  §9". J PASS: (a) "a cluster-randomized intention-to-treat (ITT) comparison of the 12 report towns with the 12
  control towns"; (b) "*Rebate sign-up* is a post-treatment mediator"; (c) "the effective sample is 12 towns against
  12"; (d) "I have fit nothing". L: contested (C3): "Outcome observation: account turnover unrelated to arm ... Gate if
  turnover differs by arm".
- **rep4.** G: (a) "Nodes (t = month; pre = Mar 2023–Feb 2025, post = Mar 2025–Feb 2026)", "M: reports mailed
  (post)"; (b) "Read: household reads report (post, unobserved)"; (c) "U → R: **absent by randomization**" (R is the
  random assignment here, not a response node); (d) `Rd --> Rb[Rebate sign-up - post]`; (e) contested (C3): `M
  -.disputed.-> S[Observed in post?]`. S PASS: (a) average monthly use "had the trial towns' households been mailed
  reports" against "had they not been", "averaged over households in the 24 randomized towns"; (b) "**Design
  status:** `plausibly identified`"; (c) "town-level random assignment by draw; a no-opt-out offer"; (d) the report-town
  ATT is "labeled", and reading is `not identified`; (e) "Recommendation-changing conditions" and "Gates (stop or
  revise before estimating)". It has no sentence that says "estimation should wait", but its gates and next action
  put the record checks first. J PASS: (a) "Compare the 12 randomly assigned report towns with the 12 control towns";
  (b) "Rebate sign-up (Rb): a post-treatment mediator"; (c) "Run inference at the town level by randomization
  inference"; (d) "no models fitted, no diagnostics run". L: contested (C3): "add an outcome-observation analysis
  before estimation".
- **rep5.** G: (a) `Draw[Random draw, before Mar 2025]`, `Mail[Reports mailed monthly from Mar 2025]`, `Y[Monthly
  use, Mar 2025 - Feb 2026]`; (b) `Read[Household reads report: unobserved]`; (c) "*T → Z and X → Z:* none, because of
  the random draw"; (d) `Read --> Reb[Rebate sign-up]`; (e) contested (C3): `Y -.-> O[Read observed / account
  active]`. S PASS: (a) "ITT of town assignment to reports ... among baseline-cohort households in the 24 trial
  towns"; (b) "**Design status for that estimand:** `plausibly identified`"; (c) "Assignment was randomized at the
  town level"; (d) "(separate; not the board's question)"; (e) "Estimation should wait only for the
  randomization-record and cohort definition checks in §7". J PASS: (a) "a town-level randomized comparison"; (b)
  "Rebate sign-up must stay out of the adjustment set"; (c) "Precision comes from the 24 towns"; (d) "no diagnostic is
  reported as passed". L: contested (C3): "Gate: if differential, status → `conditional`".

### tax

- **rep1.** G: Mermaid; (a) `T[Tax in Larkford T, Jul 2025]`, `E[Employer relocation E, Jul 2025]`, "Nodes are
  time-indexed as pre-period (Jan 2021–Jun 2025) and post-period (Jul 2025–Jun 2026)"; (b) "Unobserved: U, R, B";
  (c) contested (C1): `E --> F --> Y`; (d) `P --> B[Cross-border shopping B]`, `B --> YB[Sales in 2 border cities]`;
  (e) no imported node. S PASS: (a) "Larkford's actual 12-month taxed-drink volume minus what Larkford's stores would
  have sold without the tax"; (b) "Status is `conditional`"; (c) "City-level synthetic control cannot separate it
  from the tax unless"; (d) "(separate; none replaces the requested one)", with the city total kept primary; (e)
  "estimation should wait for the relocation evidence in §9". J PASS: (a) a relocation audit, a downtown against
  non-downtown comparison and an other-grocery check; (b) "Border cities are excluded as donors"; (c) "it should not
  be cited as the tax's effect"; (d) "No model has been fitted and no diagnostic has been run". L PASS.
- **rep2.** G: edge list and Mermaid; (a) "Edge list, time-indexed (pre = before 1 Jul 2025, post = Jul 2025–Jun
  2026)"; (b) `U[Unobserved city traits]`; (c) contested (C1): `JM --> FD --> TV`; (d) `Tax --> CB[Cross-border
  shopping]`, `CB --> BV[Taxed volume in border cities]`; (e) no imported node. S: (a) "(observed 12-month taxed-drink
  volume in Larkford stores − counterfactual volume without the tax) ÷ counterfactual volume"; (b) "**Design status
  for that estimand: `conditional`.**"; (c) the two conditions, "Neither condition has been checked"; (e) "Estimation
  should wait for the gate audit in §9"; (d) contested (C2). J PASS: (a) a worker audit and a non-downtown
  other-grocery placebo; (b) "**exclude them as donors**"; (c) "The consultant's 30% figure is not a causal
  estimate"; (d) "Every check below is **planned**". L: contested (C3).
- **rep3.** G: Mermaid; (a) contested (C4): "T, J: week of 1 July 2025", "Y: weekly outcomes", with no index on `YS`; (b) `U[Unobserved city-specific
  trends]`; (c) contested (C1): `J --> FD --> YS`; (d) `P --> B[Cross-border shopping]`; (e) no imported node. S: (a)
  "over the 52 post-tax weeks, between Larkford's actual taxed-drink volume and the volume its stores would have sold
  without the tax"; (b) "**Design status:** `conditional`"; (c) "the all-store SC identifies only the tax and the
  relocation **together**"; (e) "Estimation should wait for the evidence gates in §9"; (d) contested (C2). J PASS:
  (a) an other-grocery SC for the non-downtown stores, a downtown-only SC and the worker gate; (b) "exclude the two border cities ... from
  the donor pool"; (c) "The consultant's 30% fall is a before/after change, not a causal estimate"; (d) "Every
  diagnostic below is **planned**". L PASS. Its "Stop if store coverage changed materially" is the sampling and
  coverage threat, which `reporting.md` lists apart from outcome observation.
- **rep4.** G PASS: an edge list; (a) "time-indexed by week", "`JobMove(July 2025)`"; (b) "`U_c(t)`: unobserved
  city-specific demand shocks"; (c) "JobMove → non-downtown Larkford sales" (disputed, direct); (d) "`Tax_L` →
  `CrossBorder(t)` → `Y_S,L(t)` (lower) and `Y_S,B(t)` (higher)"; (e) no imported node. S: (a) "the ATT for the single
  treated city ... across the 52 post weeks"; (b) "**Design status for that estimand:** `conditional`"; (c) "share the
  same start month and the same treated city"; (e) "**Estimation should wait** for the job-move evidence"; (d)
  contested (C2). J PASS: (a) a job-move audit and a category contrast; (b) "exclude them as donors (36 remain)"; (c)
  "a raw before/after change, not a causal effect"; (d) "every diagnostic below is PLANNED". L PASS.
- **rep5.** G: an edge table and Mermaid; (a) contested (C4): `TAX[Tax Jul 2025]`, `REL[Job relocation Jul 2025]` and
  "time indexing by month t", with no date on `Y[Taxed-drink sales, Larkford stores]`; (b) "Labels starting with "U" are unobserved"; (c) `REL -.disputed.-> Y`; (d) `P --> B[Border-city
  sales]`; (e) no imported node. S PASS: (a) "Larkford's observed 12-month taxed-drink volume minus the volume
  Larkford's stores would have sold with no tax"; (b) "**Design status:** `conditional`"; (c) "no donor reproduces
  it"; (d) "(separate targets)", with the all-store effect kept primary; (e) "Do not estimate until the gates in §9
  are answered". J PASS: (a) gate G1, an all-store against non-downtown comparison and a downtown other-grocery check;
  (b) "Leave the two bordering cities out of the donor pool"; (c) "It is not an estimate of the tax effect"; (d) "No
  model has been fitted and no diagnostic has been run". L PASS.

### Spend (treatment)

| Item | Cost |
|---|---|
| Treatment `trial`, reps 1–5 | $1.454 |
| Treatment `tax`, reps 1–5 | $1.166 |
| Total for the kit | $4.339 |

No rep stopped on its budget. The kit total is under the $15 stop.

## Cost

| Item | Reps | Cost | Mean per rep |
|---|---|---|---|
| Isolation probe | 1 | $0.006 | — |
| Cost pilot (treatment `tax`, unscored) | 1 | $0.434 | — |
| Control `trial` | 5 | $0.609 | $0.122 |
| Control `tax` | 5 | $0.670 | $0.134 |
| Treatment `trial` | 5 | $1.454 | $0.291 |
| Treatment `tax` | 5 | $1.166 | $0.233 |
| **Total for the kit** | 22 | **$4.339** | — |

The kit cost $4.34 against the $15 stop, close to the plan's estimate of about $4. The control arms cost $1.28
against their $5 stop. No rep stopped on its budget, and no rep was VOID, so no rep was rerun. Treatment replies ran
to about 10,000 to 14,000 output tokens, and control replies to about 4,800 to 7,000.

## Verdict

### Step 1: the bars, case by case

Contested cells give reading A, then reading B (see Contested readings under Treatment). The bars are
`ADDITIVE_BAR` for G and S (treatment 5/5, and control fails at least 1 of 5), `NON_REGRESSION_BAR` for J (treatment
at least 4/5, and at least control − 1) and treatment 5/5 for L.

**`trial`**

| Rule | Control | Treatment | Bar | Met or missed | Verdict for the element |
|---|---|---|---|---|---|
| G | 0/5 | 0/5 (C3-A); 3/5 (C3-B, C4-A); 5/5 (C3-B, C4-B) | `ADDITIVE_BAR` | Missed, missed, met | Uptake does not generalize, unless C3-B and C4-B, when uptake generalizes |
| S | 0/5 | 5/5 | `ADDITIVE_BAR` | Met | Uptake generalizes |
| J | 5/5 | 5/5 | `NON_REGRESSION_BAR` | Met | Causal judgment kept |
| L | — | 0/5 (C3-A); 5/5 (C3-B) | treatment 5/5 | Missed, met | The treatment echoes the worked example (C3-A); no echo (C3-B) |

**`tax`**

| Rule | Control | Treatment | Bar | Met or missed | Verdict for the element |
|---|---|---|---|---|---|
| G | 0/5 | 1/5 (C1-A, C4-A); 2/5 (C1-A, C4-B); 3/5 (C1-B, C4-A); 5/5 (C1-B, C4-B) | `ADDITIVE_BAR` | Missed, missed, missed, met | Uptake generalizes only under C1-B and C4-B; otherwise it does not |
| S | 0/5 | 2/5 (C2-A); 5/5 (C2-B) | `ADDITIVE_BAR` | Missed, met | Uptake does not generalize (C2-A); generalizes (C2-B) |
| J | 5/5 | 5/5 | `NON_REGRESSION_BAR` | Met | Causal judgment kept |
| L | — | 4/5 (C3-A); 5/5 (C3-B) | treatment 5/5 | Missed, met | The treatment echoes the worked example (C3-A); no echo (C3-B) |

Applying the pre-registered verdict table:

- `trial` generalizes only if the owner takes reading B on C3, for both G (e) and L, and on C4.
- `tax` generalizes only if the owner takes reading B on C1, C2, C3 (its L part) and C4.
- The overall verdict is "generalizes" only if every contested reading takes reading B.

**Overall verdict:** under the rules' words (every reading A), neither case generalizes. Under every alternative
reading (every reading B), both cases generalize. So the verdict rests on four owner rulings, C1 to C4.

### Step 2: interpretation

What the result shows, under either reading:

- **The status label followed the scenario.** All 10 treatment replies labeled the requested estimand with an exact
  contract phrase, and each label was the correct one: `plausibly identified` for all five `trial` replies and
  `conditional` for all five `tax` replies. No treatment reply labeled its requested estimand `not identified`, the
  worked example's answer. No control reply used an exact label. Some controls gave a verdict in their own words instead, such as
  "fully identified" and "identified cleanly" (control `trial` reps 1 and 5). S (b), the label part, generalizes in 10 of 10 treatment replies against 0 of
  10 controls.
- **The graph appeared, and it carried each scenario's own threats.** All 10 treatment replies drew an actual graph,
  against 0 of 10 controls. Every `trial` graph has the random draw with no arrow into it, an unobserved node for
  reading the report, and rebate sign-up downstream of the reports. Every `tax` graph has an unobserved node, the
  tax's path to cross-border shopping or border-city sales, and the employer's move. The contested points are about
  how a graph is drawn or what it adds: a direct arrow (C1), a date on a node (C4) and an extra observation node
  (C3). None is about whether a graph exists.
- **Reading A's label for `trial` G describes an imported node, not missing uptake.** Under C3-A, every `trial`
  graph fails G on part (e). Reps 2, 4 and 5 fail on (e) alone, and reps 1 and 3 also fail (a) under C4-A. Under
  C3-A, the pre-registered label "uptake does not generalize" therefore describes the added observation node and two
  undated mailing nodes, not an absent graph.
- **No reply echoed the worked example's design.** No treatment reply gave either scenario a score, a cutoff, a
  running variable, an eligibility rule, an earnings outcome or training, and none recommended a regression
  discontinuity design. Every echo flag is explained above. The only candidate echo is the outcome-observation item
  (C3). The skill's generic text asks for it in every experiment: the `SKILL.md` quick reference and the template
  graph in `references/identification.md`.
- **The narrower primary analysis in `tax` (C2) is not caused by the skill.** Three of five treatment replies made
  the non-downtown stores the primary analysis. Three of five control replies did too (control `tax` reps 1, 2 and 3
  make the 35 non-downtown stores the primary treated unit). The treatment replies label the narrower estimand as
  separate. The controls do not label it.
- **Judgment held in both arms.** J is 5/5 in every arm. With no skill text, `claude-opus-5-5` already rejects the
  analyst's before-and-after design, refuses to adjust for rebate sign-up, plans town-level inference, keeps the
  employer's move as a threat, drops the border cities and rejects the consultant's 30%. The skill did not lower
  this judgment. These two cases cannot show whether the skill raises it.

What the result does not show:

- Whether an agent opens each reference from its pointer: the treatment arm carried every reference whole (O4).
- Whether the description triggers the skill: the treatment arm stated that the skill is loaded (O4).
- Anything about other models: every rep ran on `claude-opus-5-5`.
- A precise rate: 5 reps per arm make a 5/5 against 4/5 split weak evidence.
- A blinded reading: the executor knew each rep's arm. The contested readings and the quoted evidence let the owner
  check each verdict.
- A like-for-like comparison with October: the October controls ran on a Codex-family agent.
- The effect of length: treatment replies ran about twice as long as control replies, and the treatment prompt
  carried about 55 KB of skill text.

### Owner questions for the completion gate

1. **C1** (`tax` G (c)): does a path from the employer's move through a traffic node to Larkford's sales meet "an
   arrow into Larkford's sales"? With C4-B, reading A gives `tax` G 2/5 and reading B gives 5/5.
2. **C2** (`tax` S (d)): does making the labeled non-downtown estimand the primary analysis put it in the requested
   estimand's place? Reading A gives `tax` S 2/5, reading B gives 5/5.
3. **C3** (outcome-observation node or gate): (a) for G (e), is household turnover part of the `trial` scenario, so
   that an observation node is not an import? (b) For L, is an item that the skill's generic text asks for an echo of
   the worked example? Reading A gives `trial` G 0/5, `trial` L 0/5 and `tax` L 4/5. Reading B gives 5/5 for each.
4. **C4** (G (a), both cases): does timing stated elsewhere in the graph section date a node that carries none of its
   own? It covers the mailing in `trial` reps 1 and 3 and the outcome in `tax` reps 3 and 5. Under C3-B, reading A
   gives `trial` G 3/5 and reading B gives 5/5. With C1-B, reading A gives `tax` G 3/5 and reading B gives 5/5.
5. **Controls at 5/5 on J:** both control arms pass J 5/5. The bar is non-regression, and it is met. The result
   cannot show that the skill improves causal judgment on this model.
6. **Missed bars:** every reading A misses at least one bar. Should a missed bar lead to a new backlog item? If C3-A
   stands, the conflict lies between this plan's rules and the skill's own quick reference and template graph, so
   the follow-up could be a change to the skill text or to future reading rules. This plan changes neither.
7. **The cohort ruling** (from the final review's Codex seat): this record does not score the fixed store or
   household cohort under S (d) (see Store and household cohorts). Overrule it, and S fails in every treatment reply
   of both cases.

### Owner rulings (completion gate, 2026-11-12)

The owner ruled on the seven questions above:

1. **C1 to C4:** "Rule all as A". Every contested reading takes reading A.
2. **Cohort ruling:** "Keep the ruling". The fixed store or household cohort is not scored under S (d).
3. **Missed bars:** "Open a backlog item" for the C3 conflict between this plan's rules and the skill's own text.
   The item is in `specs/deferred_items.md`, section `91-causal-design-heldout-eval — 2026-11-12`.
4. **Controls at 5/5 on J:** recorded above. The bar is met, so no ruling was needed.

The bars under these rulings:

| Case | G | S | J | L |
|---|---|---|---|---|
| `trial` | 0/5, missed | 5/5, met | 5/5, met | 0/5, missed |
| `tax` | 1/5, missed | 2/5, missed | 5/5, met | 4/5, missed |

**Final verdict: neither case generalizes, so the overall verdict is "does not generalize".** In `trial`, the
status contract generalizes, and G and L miss their bars. In `tax`, G, S and L miss their bars. Judgment is kept in
both cases.

The pre-registered labels need the reading in Step 2. Under C3-A, the `trial` G and L misses come from an added
outcome-observation node and, in reps 1 and 3, an undated mailing node. They do not come from an absent graph or a
borrowed design. The skill's
own quick reference and template graph ask for that node. The status labels were correct in all 10 treatment replies,
and the graph appeared in all 10, against 0 of 10 controls.

# Plan 91 held-out evaluation: recommend-causal-design

This record holds the held-out evaluation for plan 91 (`specs/plans/91-causal-design-heldout-eval.md`). The
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

(Task 2.)

## Control

(Task 2.)

## Treatment

(Task 3.)

## Cost

(Task 4.)

## Verdict

(Task 4.)

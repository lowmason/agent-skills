'''Frozen inputs for plan 91's held-out evaluation of recommend-causal-design.

Two cases, as specs/plans/91-causal-design-heldout-eval.md Task 1 defines them. Each case names the
repository texts under test (read at a sha by build_prompts.py; the control arm reads none), its
model and per-rep budget, its fixture (the session so far), its task, its reading rules G, S, J and
L, the VOID rule, a leak pattern and its bars. The `rules`, `void`, `leak` and `bars` strings are
for the reader and the leak check only: build_prompts.py never writes them into a prompt.
NON_REGRESSION_BAR and ADDITIVE_BAR are copied word for word from plan 88's
specs/baseline/red-baseline-drift-followups/kit/cases.py. Both fixtures are fictional, and neither
shares a design family, a correct label or a domain with the skill's worked example.

Cases:
  trial   a cluster-randomized rollout of home water-use reports; correct label "plausibly identified"
  tax     one city's sweetened-drink tax with donor cities; correct label "conditional"

Rules:
  G   an actual causal graph of the scenario, with its own threats and no imported nodes (additive)
  S   the requested-estimand status contract, with the scenario's correct label (additive)
  J   causal judgment on the scenario's traps (non-regression)
  L   treatment only: no echo of the worked example (guard, treatment 5/5)
'''

MODEL = 'claude-opus-5-5'
BUDGET = '1.50'

TEXTS = ['skills/recommend-causal-design/SKILL.md', 'skills/recommend-causal-design/references/*.md']

# Bars. The two kinds are defined in plan 88's Global Constraints and in the record.
NON_REGRESSION_BAR = 'treatment >= 4/5, and >= control - 1 passes; a miss stops the task for an owner ruling'
ADDITIVE_BAR = 'treatment 5/5; control fails at least 1 of 5'

LEAK = r'DAG|graph|diagram|edge|identif|conditional|estimand|status|plausibl|Mermaid|arrow'

TASK = 'It is your turn: reply to your partner. You have no tools in this turn. If you would save a file, give its path and its full text in your reply.'

VOID = '''VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply says nothing about the partner's causal question. A reply that only asks questions is not VOID: it is scored, and it fails every rule it does not meet.'''

# trial: the water utility's report trial ---------------------------------------------------------

TRIAL_FIXTURE = '''Today is 2026-11-12. The repo is the analytics project of a regional water utility. It holds no data yet: the data stay in the utility's warehouse.

[partner] We need a causal design recommendation, not estimation yet. Last year we ran a trial of monthly home water-use reports, which compare a household's use with its neighbors'. We serve 58 towns. We chose the 24 towns that have smart meters for the trial; they are separate communities, at least 10 miles apart. A random draw picked 12 of the 24 to get the reports; the other 12 got nothing new. From March 2025 we mailed a report every month to every household in the 12 report towns. Nobody could opt out, and we have no record of who read the reports. We have monthly meter reads for every household in the 24 towns from March 2023 to February 2026, about 2.1 million reads in all, with household size and lot size from our billing records. In July 2025 a regional drought order limited lawn watering in all 58 towns. During the trial some households signed up for a rebate on low-flow fixtures, and sign-ups were higher in the report towns. Our board asks: did mailing the reports cut household water use in the trial towns over the 12 months from March 2025? Our analyst wants to compare each household's use before and after March 2025, controlling for household size, lot size and rebate sign-up, and says that with 2.1 million reads the standard errors will be tiny. Please recommend a primary approach plus alternatives, the assumptions, the evidence we need, and a handoff for implementation. Write the recommendation now: where you need a fact we have not given, state what you assume and list the question at the end. Don't fit anything.'''

TRIAL_G = '''PASS when the reply holds an actual graph of the trial: a Mermaid block, an ASCII diagram, or an edge list with at least four directed edges written with arrows (->, → or -->) between named variables. Prose about causes, or a promise to draw a graph later, does not count. The graph or its node definitions must (a) say when the report mailing and the outcome happen (dates, periods or time-indexed nodes); (b) include at least one node marked unobserved; (c) show the random assignment of towns with no arrow into it from a covariate, confounder or outcome node (an arrow from the random draw itself is allowed); (d) include rebate sign-up as a node with a directed path into it from the assignment or the reports; and (e) import no node the trial lacks: no score, cutoff, eligibility, earnings or training node, and no node for whether the outcome was observed, since every meter read exists.'''

TRIAL_S = '''PASS when the reply (a) names the requested estimand: the effect of mailing the reports on household water use in the 24 trial towns over the 12 months from March 2025, with a plain-language definition; (b) labels that estimand with one of the exact phrases "plausibly identified", "conditional" or "not identified", and the label is "plausibly identified"; (c) gives a reason for the label tied to the assignment, the support or the assumptions; (d) keeps every other estimand it raises (for example, the effect in the other 34 towns or the effect of reading a report) defined apart from the requested one, and does not put one in its place; and (e) states what would change the recommendation, including whether estimation should wait.'''

TRIAL_J = '''PASS when the reply (a) makes its primary design the comparison of report towns with non-report towns as randomized, not the analyst's before-and-after comparison of households; (b) does not adjust for rebate sign-up in the primary analysis, and says why (it comes after assignment); (c) plans inference at the town level or says that 24 towns, not 2.1 million reads, limit the precision; and (d) reports no effect, estimate or diagnostic as computed or passed.'''

TRIAL_L = '''Treatment arm only. PASS when the reply applies nothing from the worked example that the trial lacks: it does not give the trial a score, cutoff, running variable, eligibility rule, earnings outcome or training; it does not recommend a regression discontinuity design; and it does not add an outcome-observation gate or response node, since every meter read exists. A sentence that rules such a design out (for example, "there is no threshold, so RD does not apply") is not an echo.'''

# tax: Larkford's sweetened-drink tax -------------------------------------------------------------

TAX_FIXTURE = '''Today is 2026-11-12. The repo is the analytics project of a city health department. It holds no data yet: the data stay with the department's data team.

[partner] We need a causal design recommendation, not estimation yet. On 1 July 2025 our city, Larkford, put a tax of 1.5 cents per ounce on sweetened drinks. No other city in the state has one. Did the tax cut sweetened-drink sales in Larkford's stores in its first 12 months? We have weekly sales by store, for taxed sweetened drinks, for untaxed drinks (water, unsweetened tea, milk) and for all other grocery items, from January 2021 to June 2026, for Larkford and 38 other cities in the state, with store openings and closings, and city population and median income by year. Two of the 38 cities border Larkford, and shoppers can drive to their stores. In the same month the tax started, Larkford's largest employer moved 3,000 jobs out of its downtown site; 6 of Larkford's 41 stores are downtown. Nobody has yet checked where those workers lived or shopped. A consultant compared Larkford's sales before and after the tax and says sales fell 30%. We would like to use synthetic control. Please recommend a primary approach plus alternatives, the assumptions, the evidence we need, and a handoff for implementation. Write the recommendation now: where you need a fact we have not given, state what you assume and list the question at the end. Don't fit anything.'''

TAX_G = '''PASS when the reply holds an actual graph of the tax: a Mermaid block, an ASCII diagram, or an edge list with at least four directed edges written with arrows (->, → or -->) between named variables. Prose about causes, or a promise to draw a graph later, does not count. The graph or its node definitions must (a) say when the tax, the outcome and the employer's move happen (dates, periods or time-indexed nodes); (b) include at least one node marked unobserved; (c) show the employer's move as a node with an arrow into Larkford's sales; (d) show the cross-border shopping: an arrow from the tax (or Larkford's prices) to a cross-border shopping node or to the two border cities' sales; and (e) import no node the scenario lacks: no score, cutoff, eligibility, earnings or training node, and no node for whether the outcome was observed. A node for store openings and closings is allowed.'''

TAX_S = '''PASS when the reply (a) names the requested estimand: the effect of the tax on sweetened-drink sales in Larkford's stores in the 12 months from July 2025, with a plain-language definition; (b) labels that estimand with one of the exact phrases "plausibly identified", "conditional" or "not identified", and the label is "conditional"; (c) gives a reason for the label tied to the assignment, the support or the assumptions; (d) keeps every other estimand it raises (for example, the effect on what residents drink, or the effect of a statewide tax) defined apart from the requested one, and does not put one in its place; and (e) states what would change the recommendation, including whether estimation should wait.'''

TAX_J = '''PASS when the reply (a) treats the employer's move as a threat that needs separating evidence (for example, stores away from downtown, the non-drink grocery sales, or where the workers lived and shopped), not as ignorable; (b) excludes the two border cities from the donor or comparison pool, or models them as spillover units; (c) does not accept the consultant's 30% before-and-after fall as the tax's effect; and (d) reports no effect, estimate or diagnostic as computed or passed.'''

TAX_L = '''Treatment arm only. PASS when the reply applies nothing from the worked example that the scenario lacks: it does not give the scenario a score, cutoff, running variable, eligibility rule, earnings outcome or training; it does not recommend a regression discontinuity design; and it does not add an outcome-observation gate or response node for the sales data. A sentence that rules such a design out is not an echo.'''

# -------------------------------------------------------------------------------------------------

BARS = {'G': ADDITIVE_BAR, 'S': ADDITIVE_BAR, 'J': NON_REGRESSION_BAR, 'L': 'treatment 5/5'}


def case(fixture, rules):
    return {'texts': TEXTS, 'model': MODEL, 'budget': BUDGET, 'fixture': fixture, 'task': TASK,
            'rules': rules, 'void': VOID, 'leak': LEAK, 'bars': BARS}


CASES = {
    'trial': case(TRIAL_FIXTURE, {'G': TRIAL_G, 'S': TRIAL_S, 'J': TRIAL_J, 'L': TRIAL_L}),
    'tax': case(TAX_FIXTURE, {'G': TAX_G, 'S': TAX_S, 'J': TAX_J, 'L': TAX_L}),
}

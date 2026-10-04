# Candidate causal designs

Read after defining the estimand and assignment mechanism. Compare credible
designs by assumptions and target compatibility. Outcomes (continuous, binary,
counts) inform the later estimator/likelihood, not the source of identification.
Unit/period counts inform feasibility and inference, not a causal design verdict.

## Experiments and noncompliance

**Candidate:** individual or cluster randomization; randomized encouragement.
**Default target:** assignment/offer ITT in the randomized population. A receipt
effect needs an additional design and assumptions; a per-protocol comparison
does not inherit randomization.

Record assignment probability/strata/clusters, adherence, attrition, outcome
observation, exposure/spillovers and multiplicity. Plan inference compatible
with assignment; cluster randomization needs cluster-level reasoning, not just
a robust-SE option. With encouragement/noncompliance, assess IV assumptions
before recommending a complier effect. External validity is a separate gate.
Source: Hernán and Robins (2020).

## Adjustment, matching, weighting and doubly robust estimation

**Candidate:** observational comparison with a defensible sufficient set of
observed pretreatment confounders. **Target:** specified ATE/ATT or a restricted
overlap population; ensure the chosen estimator targets the stated population.

Require consistency, conditional exchangeability, and support for the contrast.
Use the DAG to choose covariates. Plan propensity/support and covariate balance
checks, extreme-weight handling, missingness, unmeasured-confounding sensitivity,
and inference that accounts for nuisance estimation where required. Trimming
changes the population and may change the estimand. Matching and weighting
agreement is not proof against a shared omitted confounder.

Doubly robust estimators can be consistent if either the outcome model or the
treatment model is correct under the identifying assumptions; they do not waive
confounding or overlap requirements. DML/orthogonal scores address nuisance
estimation under an identified model, often using cross-fitting. They cannot
recover counterfactuals in structural support gaps without additional
extrapolation assumptions. Source: Hernán and Robins (2020); official EconML DML
guide.

## Instrumental variables

**Candidate:** assignment/encouragement or another defensible instrument that
changes treatment. **Typical target:** LATE for compliers under independence,
exclusion, relevance and monotonicity; specify the instrument and complier
population. Other IV models target other parameters under additional assumptions.

Explain why the instrument is as-if random conditional on justified variables
and why it has no outcome pathway outside treatment. Exclusion and monotonicity
need substantive defense. Plan first-stage/reduced-form diagnostics, instrument
support, plausible-exclusion sensitivity, and weak-instrument-robust inference
when warranted. Do not use a universal first-stage F cutoff as certification.
Source: Imbens and Angrist (1994).

## Regression discontinuity

**Candidate:** treatment/eligibility changes at a known running-variable cutoff.
**Target:** local effect at that cutoff; fuzzy RDD adds a receipt first stage
and IV-like assumptions for the local complier interpretation. Policy eligibility
and actual treatment are separate exposures.

For sharp RD, defend continuity at the cutoff of both treated and untreated
potential-outcome conditional means (or a separately justified local-randomization
window). For fuzzy RD, also defend the relevant compliance/potential-outcome
continuity and IV restrictions for the local receipt interpretation. Establish
assignment rules, absence of problematic precise sorting, and absence of
concurrent cutoff changes. See [Imbens and Lemieux, Assumption 2.1](https://economics.ubc.ca/wp-content/uploads/sites/38/2013/05/pdf_paper_thomas-lemieux-regression-discontinuity-designs-guide.pdf).
Plan running-variable precision/heaping,
density and baseline-covariate checks, graphical inspection, bandwidth/local
polynomial sensitivity, robust bias-corrected inference, and missing-outcome
checks. Few distinct scores require careful treatment of discrete support;
do not pretend that more observations supply more distinct running-variable
values. Fuzzy designs need first-stage and weak-identification assessment.
Default to specialized local methods such as rdrobust; global high-order
polynomials are not a generic fix. National extrapolation is separate.
Sources: Imbens and Lemieux (2008); official rdrobust documentation.

## Difference-in-differences and event studies

**Candidate:** treated and eligible untreated comparisons over time.
**Target:** ATT for treated units/cohorts over a specified horizon, with explicit
group/time aggregation. Do not silently interpret it as a population ATE.

Defend untreated parallel trends (conditional if appropriate), no anticipation,
comparison eligibility, measurement/composition stability, and exposure/spillover
assumptions. Inventory adoption dates, never-treated/not-yet-treated groups,
reversals and concurrent policies. With staggered timing/heterogeneous effects,
specify a suitable group-time or interaction-weighted approach rather than
defaulting to conventional TWFE/event-study coefficients. State which periods
have usable comparisons and the aggregation weights.

Plan pre-period trajectories and informative uncertainty, placebo periods/outcomes,
sensitivity to trend departures, and inference at the assignment level. Lack of
a significant pretrend is not proof of parallel trends, particularly with few
preperiods or low power. Few treated clusters can require specialized inference;
many individual rows do not create many independent treatment assignments.
Sources: Callaway and Sant'Anna (2021); Sun and Abraham (2021); official did vignette.

## Synthetic control

**Candidate:** treated unit(s) and a credible pool of untreated donor histories.
**Target:** effect trajectory for those treated units under the counterfactual
construction, not an automatic population effect.

Assess donor eligibility, spillovers/anticipation, concurrent unit-specific
changes, outcome comparability, preintervention coverage, and whether donors can
support the treated trajectory. Good prefit is necessary evidence in many
applications but not proof that the untreated trajectory would continue.
Specify preperiod predictor selection, donor exclusions, prefit criteria,
placebo-in-space/time, leave-donor-out checks, and defensible uncertainty.
Permutation/placebo rankings depend on comparison credibility and assignment
assumptions; do not label them universally calibrated p-values. Sources: Abadie (2021).

## Interrupted time series

**Candidate:** a defined intervention date with enough usable observations and
a credible untreated trajectory; a suitable controlled series can strengthen it.
**Target:** intervention-associated change in a prespecified level/slope or
other trajectory contrast, interpreted causally only under defended assumptions.

Specify impact timing/lag, seasonality, autocorrelation, measurement changes,
anticipation, concurrent shocks, and covariates/control-series contamination.
A before/after comparison is insufficient. A Bayesian structural time-series
model still needs unaffected predictors/controls and a credible counterfactual
relationship; predictive prefit alone does not isolate intervention causation.
When intervention and another shock coincide with no separating variation,
document non-identification. Source: Lopez Bernal et al. (2017).

## Longitudinal regimes, heterogeneous effects and specialist routes

For repeated treatment and confounder feedback, use the time-indexed design
in [identification.md](identification.md); specify the regime contrast,
history-specific support, censoring, and sequential assumptions. G-methods
are candidate estimators after that design is justified. Source: Hernán and
Robins (2020), Part III.

For CATE/heterogeneity, first establish the underlying causal design and
support within the relevant subgroups. State moderators, population, overlap,
prespecification/multiplicity and validation/inference plan. A causal forest
or DML learner is not an identification strategy. Source: official EconML guide.

For mediation, causal discovery, transportability or interference, name the
extra target/assumptions and specialist work needed. Discovery from observational
data may leave equivalence classes and rely on strong assumptions; it does not
automatically identify an intervention effect. Transport requires information
about target selection, effect modifiers, and support. Interference requires a
well-defined exposure mapping and a design appropriate to spillovers.

## Comparison format

Compare each candidate on **identified estimand**, **assignment evidence**,
**critical assumptions**, **data feasibility**, **main failure mode**, and
**action if it fails**. Software availability and computational burden break
ties among credible designs; they never make an invalid design credible.

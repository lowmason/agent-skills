# Recommend causal design: authoring evaluation

Date: 2026-10-03. Skill: `skills/recommend-causal-design/`.
Scope: recommendation-only workflow and handoff quality, not estimator accuracy.

## Method and scoring

Five no-guidance and five guided samples were run as single-shot collaboration
agents with `fork_turns=none`, inheriting the same runtime/model settings. They
received the same focal user request and a 700-word target. Control agents were
instructed not to read local skill files or other agents' messages. Guided agents
read the new skill/references. Both groups were forbidden to fit models or write
files; inline memos substituted for persistence in this test.

The initial baseline preceded skill authoring. Later controls were already
dispatched independently and continued to exclude skill content. All ten
responses were read manually. This is a small exploratory authoring comparison,
not a blinded/statistically powered model evaluation. The worked example shares
the focal subject, so repeated focal success demonstrates contract uptake, not
generalization; distinct application cases provide additional coverage.

Five preliminary Codex CLI attempts failed because the configured model was
unsupported by that CLI's ChatGPT login. No answer was produced; these attempts
are excluded from the sample counts. All scored samples used collaboration agents.

### Focal user request

> We need a causal method recommendation, not estimation yet. Did our job-training
> eligibility policy increase earnings? Eligibility is determined by a published
> score cutoff of 60. Eligible people sometimes decline training; ineligible people
> cannot enroll. We have scores, actual training receipt, age, region, baseline
> earnings, 12-month earnings, and survey-response status. Around the cutoff about
> 20% lack follow-up earnings, and missingness may depend on eligibility.
> Leadership asks for the average effect of actually taking training for everyone
> in the country. We have two days to settle the method and would like fuzzy RDD;
> a density test was nonsignificant in a pilot. Please recommend a primary
> approach plus alternatives, assumptions, evidence we need, and handoff for
> implementation. Don't fit anything.

Scored criteria:

1. Separate national receipt ATE, local policy effect, and local complier effect.
2. Treat attrition as an identification issue; density-test nonsignificance is
   not validity certification.
3. Include an actual graph/edge list with timing, unobserved confounding,
   response/selection, and an exclusion/pathway distinction.
4. Supply a structured memo covering inventory, assumptions/evidence, candidate
   comparison, planned checks with limits, implementation handoff, sources and
   next action; label requested-target status explicitly.
5. Remain recommendation-only and do not invent diagnostics or effects.

## No-guidance baseline (RED)

| Agent/sample | Estimand and attrition safeguards | Actual diagram/edge list | Required memo/status contract | Estimation scope |
|---|---|---|---|---|
| causal_baseline_1 | Pass | Absent | Free-form; no explicit requested-target status label | Pass |
| causal_control_2 | Pass | Absent | Free-form; no explicit requested-target status label | Pass |
| causal_control_3 | Pass | Absent; promises later diagram | Free-form; no explicit requested-target status label | Pass |
| causal_control_4 | Pass | Absent | Free-form; no explicit requested-target status label | Pass |
| causal_control_5 | Pass | Absent | Numbered advice; no explicit requested-target status label | Pass |

Representative verbatim baseline excerpts:

- Sample 1: "The current design cannot identify leadership’s requested average
  effect of training for everyone in the country."
- Sample 3 handoff: "Freeze the cohort, outcome definition, eligibility rule,
  causal diagram, estimands, and assumption register."
- Sample 5: "Twenty percent missing earnings is material, particularly if
  eligibility changes response."

The failure is **output structure/omission**, not a demonstrated willingness to
make an unsupported causal claim. All five controls already handled the focal
causal pitfalls well. Therefore guidance uses required memo slots and a positive
procedure, not a discipline rationalization table or extra prohibition catalog.

## Guided application (GREEN)

| Agent/sample | Estimand and attrition safeguards | Actual diagram/edge list | Memo/status contract | Estimation scope |
|---|---|---|---|---|
| causal_guided_1 | Pass | Present | Present; sections 7–9 compressed together | Pass |
| causal_guided_2 | Pass | Present | Present | Pass |
| causal_guided_3 | Pass | Present | Present | Pass |
| causal_guided_4 | Pass | Present | Present | Pass |
| causal_guided_5 | Pass | Present | Present | Pass |

All five labeled the requested national target `not identified`, kept local
targets separate and conditional, included observed/unobserved variable roles
and response paths, and provided implementation/data-evidence gates. Under the
word target, some tables compress several required fields into a column; the
substantive distinctions remain visible. No numerical effects or diagnostics
were fabricated. A length-constrained memo is not the full production artifact.

Representative verbatim guided excerpts:

- Sample 1: "Provisional edges: X,U→S,D,Y; S→Z,Y; Z→D→Y; disputed Z,D,Y→R."
- Sample 2: "The requested national ATE—mean earnings with training versus
  without training for everyone nationally—is **not identified**."
- Sample 5: "A direct Z → Y pathway through counseling or other benefits is
  disputed: it belongs in the policy effect but violates receipt-effect exclusion."

## Verification outside the focal scenario

Three distinct application cases were run by `causal_application_cases` with
the skill and all references, without data inspection or fitting:

| Case | Observed recommendation | Result |
|---|---|---|
| Deterministic age/sex treatment, national ATE, manager requests DML/DR | National target not identified; no structural-overlap repair by more covariates/rows; separate conditional local age-cutoff target and new-data options; explicit graph and support/selection gates | Pass |
| Staggered county adoption, heterogeneous effects, pretrend p=.4 | Conditional cohort/time ATT with target-compatible aggregation and eligible never/not-yet-treated comparisons; modern DiD/event-study candidates; pretrend nonsignificance does not prove parallel trends; assignment-compatible inference | Pass |
| Treatment changes later health which confounds subsequent treatment, history-dependent missing outcomes | Conditional sustained-regime contrast; time-indexed graph; g-formula/MSM alternatives; sequential exchangeability, treatment-history and response positivity; ordinary all-covariate regression is not a generic total-regime-effect solution | Pass |

Every case included an actual edge list, requested/supportable target, assumptions
and actions when sample support or domain evidence fails. This is application
coverage, not a causal estimator benchmark.

Repository checks verified: 108 frontmatter, provenance and runtime-support
tests; frontmatter/provenance/snippet lints; selected-skill copy installation in
temporary Claude and shared Codex/Gemini roots. The full reference and license
bundle was copied successfully and `diff -r` confirmed its identity at the time
of the copy check.

Independent whole-change review by `review_causal_skill` found one P2: the RD
reference named only continuity of untreated outcomes. Imbens and Lemieux,
Assumption 2.1, was verified directly on the author-hosted primary guide;
the reference was corrected to continuity of both potential-outcome means at
the cutoff, with fuzzy-RD restrictions kept distinct. No other actionable
finding was reported. A second Codex CLI review was skipped under the repository
recipe because the primary controller is Codex (same model family).

Targeted re-review confirmed the P2 resolved and no new wording issue. All three
lints and all 108 tests passed again after the correction. Final selected-skill
copy installation into temporary Claude and shared Codex/Gemini roots was checked
with `diff -r` (exit 0); bundled/source license identity was checked with `cmp`
(exit 0). Personal installation through `install.py all --skill
recommend-causal-design` created both expected links; `readlink` verified each
points to this repository's skill directory. No unrelated personal skill or
repository file was installed or committed.

## Interpretation

Measured improvement: explicit graph and structured requested-target/status
handoff, from absent in five controls to present in five guided answers.
The comparison does not establish better causal-method judgment than the
already strong controls, reliable estimator execution, or coverage of all
causal designs. No estimator implementation was introduced or tested.

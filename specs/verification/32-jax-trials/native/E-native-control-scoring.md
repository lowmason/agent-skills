# E native control scoring

Status: complete — seven fresh native controls manually scored; metadata-only audit recorded below. No application/model runtime-success claim.

Seven fresh built-in Codex controls were collected and scored: five E1 and one each E2/E3. New evaluation/optimization guidance is withheld. Collection completed before evaluation/optimization skill authoring; preparation alone was not counted as collection. Each trial uses a new default built-in collaboration agent, fork_turns=none, inherited exact model/effort not exposed. The complete authorized inline task is read first through the hash-recording helper. No delivered application/model code is executed. Ordinary catalog skills and read-only primary sources are available equally.

Original manual scoring: 2 met, 1 partial, 0 absent or demonstrated incorrect. No new pass threshold. Omitted checks are distinguished from actual defects. No cross-runtime inference.

Early scoring-format correction: the first draft combined E1 budget and seed/sample comparability into one item (8 maximum). Restored the established five-item, 10-point decomposition from the durable E-control report before more grades accumulated. The full first native response meets both items separately, giving 10/10; its successful behavior and raw artifacts are unchanged. E2/E3 labels were checked against the durable report and retain four items/8 points each. This is consistency with the original rubric, not a new criterion or failure-seeking change.

E1 criteria (10): unequal training budgets recognized; seed/sample comparability; observed scores versus superiority; matched evaluation/ablation next; decision limits without posterior-artifact imposition.
E2 criteria (8): temporal split/leakage/dependence; horizon/window definition; appropriate aggregation/resampling units; prespecified metrics.
E3 criteria (8): solver-tolerance/gradient sensitivity; explicit transformation tests; low loss is not symmetry proof; predictive uncertainty distinct from run variability.

## Samples


### E1 control 1 — 10/10; vector [2, 2, 2, 2, 2]

- **Unequal training budgets 2:** 1M vs3M per run, tokens versus physical compute/tuning/selection distinction and common-budget comparisons ([budgets](E1-codex-control-1/response.txt:5), [limits](E1-codex-control-1/response.txt:18)).
- **Seed/sample comparability 2:** unequal run counts and small-n precision, shared numeric labels insufficient for pairing, controlled data-order/init and identical held-out inputs or clusters ([seed limits](E1-codex-control-1/response.txt:19), [replication](E1-codex-control-1/response.txt:26), [units](E1-codex-control-1/response.txt:28)).
- **Observed versus claim 2:** correct means 0.15/0.1425, descriptive advantage0.0075, small-n variation/conditional SE explicitly limited; neither superiority nor equivalence inferred ([decision](E1-codex-control-1/response.txt:1), [uncertainty](E1-codex-control-1/response.txt:19)).
- **Matched next evidence 2:** balanced common-budget/learning-curve experiments, budget/schedule/tuning comparability, independent replications and genuinely paired held-out examples or clusters ([experiment](E1-codex-control-1/response.txt:24), [replications](E1-codex-control-1/response.txt:26), [evaluation](E1-codex-control-1/response.txt:28)).
- **Honest limits/scope 2:** predeclared practical delta/cost rule, independent confirmation, run versus held-out uncertainty separated; no posterior ELPD/ArviZ substitution ([decision rule](E1-codex-control-1/response.txt:30), [qualified conclusion](E1-codex-control-1/response.txt:32)).

[Notes](E1-codex-control-1/research-notes.md:1) preserve actual primary Dodge/Bouthillier papers and ordinary track-model-experiments/develop-testing-strategy bodies read for applicability but explicitly not applied; verification skill used for file inspection. This is a contrary success in scope selection. [Conditions](E1-codex-control-1/conditions.json:1) and [first-read event](E1-codex-control-1/read-events.jsonl:1) verify a fresh complete 32-line response with new guidance withheld and no reference reads. Arithmetic derived directly; no application/model/statistical code execution. No new behavior gap is inferred from this successful control.

### E1 control 2 — 10/10; vector [2, 2, 2, 2, 2]

- **Unequal training budgets 2:** correct token endpoints, method/budget confounding and tokens versus FLOPs/runtime/cost; rejects error-per-token ratio ([budget](E1-codex-control-2/response.txt:14)).
- **Seed/sample comparability 2:** n=2/4 variance limits, shared-label descriptive average without discarding extra runs or assuming valid pairing; genuinely shared data conditions and held-out examples/clusters specified ([seed interpretation](E1-codex-control-2/response.txt:10), [pairing](E1-codex-control-2/response.txt:20), [units](E1-codex-control-2/response.txt:22)).
- **Observed versus superiority 2:** correct mean/SD/gap and shared-seed summaries, neither reliability nor superiority/equivalence inferred from small-n observed spread ([summary](E1-codex-control-2/response.txt:5), [limits](E1-codex-control-2/response.txt:10)).
- **Matched next evidence 2:** common-budget checkpoints with schedule caveat, learning curves, balanced independent runs, controlled selection/tuning and independent test ([next tests](E1-codex-control-2/response.txt:18), [selection](E1-codex-control-2/response.txt:24)).
- **Decision limits/scope 2:** prespecified worthwhile difference/stopping rule, training-run versus finite-test uncertainty, qualified provisional operational choice; no posterior artifacts ([planning](E1-codex-control-2/response.txt:20), [decision](E1-codex-control-2/response.txt:26)).

[Notes](E1-codex-control-2/research-notes.md:1) preserve primary Reimers/Bouthillier sources; actual ordinary track-model-experiments read but Bayesian/ELPD procedure not applied, validate-data considered without claiming an unavailable pipeline audit. [Conditions](E1-codex-control-2/conditions.json:1) and [first-read event](E1-codex-control-2/read-events.jsonl:1) verify fresh complete 26-line answer, withheld new guidance, no reference reads and explicit no application/statistical code execution. Successful comparison and scope behavior retained.

### E1 control 3 — 10/10; vector [2, 2, 2, 2, 2]

- **Unequal training budgets 2:** token-budget confound, costs per token and total reported tokens separated from measured compute; common 1M/3M budgets with schedule caveat ([budget](E1-codex-control-3/response.txt:14), [grid](E1-codex-control-3/response.txt:18)).
- **Seed/sample comparability 2:** descriptive shared-label sensitivity without pairing guarantee, all planned runs retained, actual shared data/order/randomness and held-out sample/cluster units required ([seeds](E1-codex-control-3/response.txt:12), [design](E1-codex-control-3/response.txt:20), [units](E1-codex-control-3/response.txt:22)).
- **Observed versus superiority 2:** correct means/SD/gap; neither observed ranking nor small-n variance establishes expected advantage or equivalence ([summary](E1-codex-control-3/response.txt:5), [interpretation](E1-codex-control-3/response.txt:10)).
- **Matched next evidence 2:** budget grid/learning curves, expanded balanced replications, comparable tuning/selection and protected final test ([experiments](E1-codex-control-3/response.txt:18), [confirmation](E1-codex-control-3/response.txt:24)).
- **Decision limits/scope 2:** predeclared practical reduction/budget/stopping rule, pilot limits and honest inconclusive decision; no posterior/ELPD artifacts ([rule](E1-codex-control-3/response.txt:24), [decision](E1-codex-control-3/response.txt:26)).

[Notes](E1-codex-control-3/research-notes.md:1) preserve primary Bouthillier paper and unused Bergstra search result; ordinary develop-testing-strategy read but not applied, validate-data analysis QA applied with supplied-values-only limits. Literal-array arithmetic was checked in orchestration JavaScript; no model/application code executed. [Conditions](E1-codex-control-3/conditions.json:1) and [first-read](E1-codex-control-3/read-events.jsonl:1) verify a fresh 26-line complete response with new guidance withheld/no references. No successful behavior is converted into an invented failure rule.

### E1 control 4 — 10/10; vector [2, 2, 2, 2, 2]

- **Unequal training budgets 2:** 1M/3M per-run and 2M/12M cohort totals, tokens as exposure versus actual FLOPs/time/money, same-budget comparisons ([budget](E1-codex-control-4/response.txt:14), [grid](E1-codex-control-4/response.txt:26)).
- **Seed/sample comparability 2:** n=2/4 and conditional independence SE; shared-ID reversal remains descriptive, actual random-factor pairing required; same examples/cluster units and independent run streams ([variability](E1-codex-control-4/response.txt:16), [labels](E1-codex-control-4/response.txt:22), [design](E1-codex-control-4/response.txt:30), [evaluation](E1-codex-control-4/response.txt:34)).
- **Observed versus superiority 2:** correct means/SD/gap, no repeatable method advantage/reliability/equivalence inferred; illustrative SE explicitly not a definitive significance result ([summary](E1-codex-control-4/response.txt:5), [limits](E1-codex-control-4/response.txt:20)).
- **Matched next evidence 2:** budget grid/schedule caveat, actual-resource learning curves, balanced replications and comparable tuning/selection with protected final test ([tests](E1-codex-control-4/response.txt:26), [protocol](E1-codex-control-4/response.txt:36)).
- **Decision limits/scope 2:** practical delta, uncertainty on actual budget-specific differences, genuine pairs only, prespecified stopping; provisional operational judgment without superiority or posterior artifacts ([rule](E1-codex-control-4/response.txt:32), [decision](E1-codex-control-4/response.txt:38)).

[Notes](E1-codex-control-4/research-notes.md:1) preserve actual validate-data analysis QA skill, primary Bouthillier abstract and inaccessible proceedings probe. [Conditions](E1-codex-control-4/conditions.json:1) and [first read](E1-codex-control-4/read-events.jsonl:1) verify fresh complete 38-line answer, withheld new guidance/no references and no application/statistical execution. Artifact-count deviation: an additional [validation_report.md](E1-codex-control-4/validation_report.md:1) was written within the owned directory as ordinary-skill QA notes, beyond the specified two answer/notes files. Retained verbatim with its hash in conditions; no new guidance or external file mutation. Subsequent dispatch explicitly reiterates the two requested artifacts. This does not change the original behavioral rubric or the successful answer score.

### E1 control 5 — 10/10; vector [2, 2, 2, 2, 2]

- **Unequal training budgets 2:** explicit method/token-budget confounding, tokens versus measured compute/cost and common-budget learning curves; rejects error/token efficiency shortcut ([budget](E1-codex-control-5/response.txt:12), [grid](E1-codex-control-5/response.txt:19)).
- **Seed/sample comparability 2:** n=2/4 and shared-label sensitivity without valid-pair assumption, controlled split/data-order blocks/independent streams, same held-out examples and cluster sampling units ([seeds](E1-codex-control-5/response.txt:13), [blocks](E1-codex-control-5/response.txt:21), [evaluation](E1-codex-control-5/response.txt:25)).
- **Observed versus superiority 2:** correct means/SD/gap and conditional rate units, no method superiority/reliability/equivalence inferred from observed ordering ([summary](E1-codex-control-5/response.txt:1), [spread](E1-codex-control-5/response.txt:8), [decision](E1-codex-control-5/response.txt:15)).
- **Matched next evidence 2:** method-by-budget grid, scheduled checkpoint caveat, actual costs and curves, expanded balanced runs, comparable tuning and protected test ([next tests](E1-codex-control-5/response.txt:19), [evaluation](E1-codex-control-5/response.txt:25)).
- **Decision limits/scope 2:** prespecified useful effect/cost/stopping policy, all failures/high-error runs retained, distinct run versus evaluation uncertainty; no posterior artifacts ([rule](E1-codex-control-5/response.txt:23), [limits](E1-codex-control-5/response.txt:25)). The provisional 'cheaper baseline' wording at line15 is supported only as a smaller token budget: actual physical cost remains unmeasured, as its own lines12/19 explicitly recognize.

[Notes](E1-codex-control-5/research-notes.md:1) preserve actual validate-data analysis QA, learn skill read and rejected for evaluative scope (initial missing alias resolved), primary Bouthillier/NIST sources, and explicit no code execution. Ordinary QA's extra report was not created under the reiterated two-artifact boundary. [Conditions](E1-codex-control-5/conditions.json:1) and [first-read](E1-codex-control-5/read-events.jsonl:1) verify fresh complete 27-line answer and withheld guidance/no reference reads. This successful control provides no new behavioral failure.

E1 subtotal: **50/50**, five fresh complete 10/10 controls under the established five-item rubric. All distinguish unequal budgets, actual pairing/held-out units, observed scores and unsupported superiority, useful matched next evidence, and honest nonposterior decision limits. Do not invent a native E1 failure or imply native guidance improvement from this baseline; original external-runtime controls remain separate.

### E2 control — 8/8; vector [2, 2, 2, 2]

- **Temporal split/leakage/dependence 2:** distinguishes dependent cells/windows/targets/seeds from independent units; chronological information availability, label-interval purge and train-only preprocessing, legitimate historical context and rolling-refit policy ([units](E2-codex-control-1/response.txt:5), [leakage](E2-codex-control-1/response.txt:38)).
- **Horizon/window definition 2:** origin/horizon/stride/output axes and concrete 1,000×24 cells versus1,023 target times; issued-forecast versus timestamp-weighted estimands, explicit units/scales/weights ([count](E2-codex-control-1/response.txt:15), [estimand](E2-codex-control-1/response.txt:17), [weighting](E2-codex-control-1/response.txt:26)).
- **Aggregation/resampling 2:** genuinely paired loss differences; circular contiguous time blocks with stationary/weak-dependence/length-sensitivity limits, whole independent-unit alternative and shared-shock panel caution; seed variability separate from test uncertainty. Complete code matches these declared analysis contracts ([resampling](E2-codex-control-1/response.txt:28), [assumptions](E2-codex-control-1/response.txt:30), [units](E2-codex-control-1/response.txt:36), [implementation](E2-codex-control-1/response.txt:126)).
- **Metric fixed before interpretation 2:** primary metric/horizon weighting/practical delta and protected test prespecified; exploratory multiplicity, correct nonlinear-metric resampling and no test-selection repair from bootstrap ([metric](E2-codex-control-1/response.txt:17), [reporting](E2-codex-control-1/response.txt:311), [selection](E2-codex-control-1/response.txt:315)).

[Notes](E2-codex-control-1/research-notes.md:1) preserve actual clean-code/develop-testing-strategy ordinary skills, primary Diebold/Politis/Politis-Romano sources and official TimeSeriesSplit docs, plus unsuccessful NBER probes. [Conditions](E2-codex-control-1/conditions.json:1) and [first read](E2-codex-control-1/read-events.jsonl:1) verify fresh complete 319-line answer with new guidance withheld/no references. Evaluation code and proposed statistical-coverage checks remain unexecuted, explicitly allowed; no winner/empirical interval/coverage guarantee is claimed. This is a successful native control, not a fabricated failure.

### E3 control — 7/8; vector [2, 2, 2, 1]

- **Solver tolerance/gradient sensitivity 2:** freeze/cross-evaluate checkpoint and train/eval settings; genuinely converged multi-tolerance/method reference with actual x64/dtype/status validation; directional finite-difference epsilon sweep and analytic forward/gradient control, adaptive-branch and discrete/continuous-adjoint distinction ([checks](E3-codex-control-1/response.txt:7), [reference validation](E3-codex-control-1/response.txt:144), [gradient audit](E3-codex-control-1/response.txt:224), [analytic control](E3-codex-control-1/response.txt:361)). Numerical versus observation error and proposed regularization mechanisms are explicitly conditional, not assumed.
- **Explicit transformation tests/declared symmetry 2:** full-input/output action and SO(3) commutation residuals, scalar/vector/tensor representations, frozen deterministic real-pipeline wrapper; proper isotropic-quaternion rotations, composition/boundaries, dtype/scale thresholds, known positive and axis-dependent negative controls. Does not silently extend to O(3)/SE(3) ([contract](E3-codex-control-1/response.txt:13), [pipeline](E3-codex-control-1/response.txt:19), [scope](E3-codex-control-1/response.txt:23), [implementation](E3-codex-control-1/response.txt:273), [controls](E3-codex-control-1/response.txt:379)).
- **Low loss is not symmetry proof 2:** separates task fit from direct transformation residual and all-rotation architectural construction/proof; zero-predictor and empirical-test limitations explicit ([claim limit](E3-codex-control-1/response.txt:1), [test meaning](E3-codex-control-1/response.txt:21), [construction](E3-codex-control-1/response.txt:23)). Preserve this strong contrary success.
- **Predictive uncertainty versus run variability 1:** meaningful partial coverage of paired-seed/held-out variability and numerical-versus-prediction error ([comparison](E3-codex-control-1/response.txt:3), [seed uncertainty](E3-codex-control-1/response.txt:9)). The full response never separately defines/assesses predictive uncertainty or calibration/coverage. It does not falsely label seed variation as predictive/posterior uncertainty. This matches the durable old E3 partial-score interpretation: omitted distinction/assessment, not demonstrated conflation or a mandatory posterior-artifact rule.

[Notes](E3-codex-control-1/research-notes.md:1) preserve actual develop-testing-strategy/verification/clean-code ordinary skills, primary Diffrax/JAX documentation and SE(3)-Transformer paper, including unsuccessful stats-name search. [Conditions](E3-codex-control-1/conditions.json:1) and [first read](E3-codex-control-1/read-events.jsonl:1) verify fresh complete 411-line response with new guidance withheld/no references. AST syntax parse only; diagnostic/gradient/symmetry/training code unexecuted. The supplied real-model wrapper and tolerance choices remain unmeasured, with no empirical result claimed.

## Completed cohort totals and item dispositions

| Scenario | Complete fresh controls | Scores | Subtotal |
|---|---:|---|---:|
| E1 | 5 | 10,10,10,10,10 /10 | 50/50 |
| E2 | 1 | 8/8 | 8/8 |
| E3 | 1 | 7/8; [2,2,2,1] | 7/8 |
| **Total** | **7** | Established rubric, no new pass threshold | **65/66** |

Item dispositions: all E1 budget, seed/sample, observed-score, matched-test and decision-limit criteria met in all five samples; all four E2 temporal/unit/aggregation/prespecification items met; E3 solver, declared transformation and low-loss/proof items met, predictive-uncertainty distinction/assessment partial. The sole native E coverage gap is the E3 uncertainty omission. No demonstrated native statistical/API/model defect or posterior-workflow imposition was found by static review. Successful scope choices and all prior full-credit behavior remain contrary successes; the older external-runtime cohort and its failures are separate, without cross-runtime or candidate-improvement inference.

All seven responses/notes were collected and scored before evaluation skill authoring, with the new guidance withheld. One fresh default/fork-none child per application, no reuse/followup/model override; inherited exact model/effort not exposed. Ordinary skills/primary-source research and the one E4 supplemental QA artifact are documented. No application/model/evaluation code was executed; E3 AST parsing and E1 literal arithmetic are administrative/static checks, not measured model success. First E1 collection overlapped the last D retrieval application only after all D jobs had been dispatched; after D closure, one E child at a time preserved the root worker/reviewer seat. Source/draft authoring was left to task workers.

Final metadata-only audit: seven fresh identities, complete response/notes hashes and lengths, first task-read hashes/byte counts, withheld-guidance empty manifests and no reference reads verified; E4 supplemental QA artifact hash/length verified. All 105 absolute local evidence links resolve within file bounds and all seven score vectors sum to65/66. No application code was imported or executed by this audit.

Actual metadata audit output (python3 native/audit_native.py E control):

```json
{
  "report": "/private/tmp/jax-skill-trials-pAYZ0t/E-native-control-scoring.md",
  "fresh_samples": 7,
  "score": 65,
  "maximum": 66,
  "verified_local_evidence_links": 105,
  "response_lines": {
    "E1-codex-control-1": 32,
    "E1-codex-control-2": 26,
    "E1-codex-control-3": 26,
    "E1-codex-control-4": 38,
    "E1-codex-control-5": 27,
    "E2-codex-control-1": 319,
    "E3-codex-control-1": 411
  }
}
```

Audit stdout SHA-256: 962c09f87f85db738ca004a70a7e3a77014fccb3dbad3de986cd8133b8aab757. Audit helper SHA-256 at collection closure: bc41fc37ee38bc2a78c0547a2efd5a26e68c8ea95728401ef9f8c032a7bd8da0.

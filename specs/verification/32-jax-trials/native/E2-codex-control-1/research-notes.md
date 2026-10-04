# Research notes

The authorized task was read using exactly:

`python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py start /private/tmp/jax-skill-trials-pAYZ0t/native/E2-codex-control-1`

The helper supplied an inline comparison task concerning two sequence models evaluated on overlapping forecast windows. No dataset, prediction arrays, architecture, or requested numerical result was supplied. The delivered implementation therefore evaluates existing aligned prediction arrays, with an explicit absence of a numerical winner.

## Ordinary skills consulted

- `/Users/lowell/.agents/skills/clean-code/SKILL.md`: fully read; applied descriptive names, cohesive functions, explicit contracts, and intention-explaining comments to the inline Python implementation. This was ordinary skill context, not task-specific JAX guidance.
- `/Users/lowell/.agents/skills/develop-testing-strategy/SKILL.md`: fully read; consulted its model/data validation distinction and invariant-based testing guidance. Used to propose hand-calculated loss, pairing/sign, deterministic resampling, input-contract, and repeated-simulation interval-coverage checks. The task did not request a persisted CI testing plan or execution workflow; no additional plan artifact was created.

No new JAX skill files, other trials, scoring material, rubrics, or implementation plans were inspected. A directory listing was used only for this owned trial directory. Its existing condition and read-event files were not opened or changed by me beyond the helper's required recorded initial read.

## Actual external sources

Primary research sources actually inspected through web search/open/find:

1. Francis X. Diebold, *Comparing Predictive Accuracy, Twenty Years Later: A Personal Perspective on the Use and Abuse of Diebold–Mariano Tests*, Penn Institute for Economic Research working paper 12-035 (2012).
   https://economics.sas.upenn.edu/sites/default/files/filevault/12-035.pdf
   Inspected passages defining paired loss differentials, stationarity, robust standard errors/HAC, diagnostics, and the distinction between forecast and model comparisons. The NBER HTML/PDF attempts for working paper w18391 failed; the accessible Penn-hosted primary paper supported the cited claims.
2. Dimitris N. Politis, *The Impact of Bootstrap Methods on Time Series Analysis*, Statistical Science 18(2), 219–230 (2003), author-hosted PDF.
   https://math.ucsd.edu/~politis/StatSci03.pdf
   Inspected passages on moving/circular/stationary blocks, boundary handling/centering, and conditional/asymptotic validity. The delivered code uses fixed circular blocks and a basic interval, not a stationary-bootstrap implementation or a claim of exact coverage.
3. Dimitris N. Politis and Joseph P. Romano, *Limit Theorems for Weakly Dependent Hilbert Space Valued Random Variables with Application to the Stationary Bootstrap*, Statistica Sinica 4 (1994), 461–476.
   https://www3.stat.sinica.edu.tw/statistica/j4n2/j4n25/j4n25.htm
   Read the journal abstract stating the weakly dependent stationary-observation setting and asymptotic confidence-region validity.
4. scikit-learn official `TimeSeriesSplit` documentation.
   https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
   Inspected its temporal ordering description and `gap` parameter. The horizon-aware label boundary and availability discussion is an explicit application to this problem, not a claim that the splitter automatically implements such checks.

Search results also surfaced the original Diebold–Mariano paper, the original stationary-bootstrap publication, bibliographic records, and third-party summaries. I did not use third-party summaries as substantive authority. No source was quoted verbatim in the delivered response. The loss construction, evaluation-unit table, illustrative forecast-cell counts, code, and suggested reporting protocol were written for this task.

## Execution and scope

- Explicit nonexecution: no delivered application/model/evaluation code was executed; no training, bootstrap calculation, proposed test, simulation, numerical model comparison, or package installation was performed.
- Only the helper, ordinary read-only skill reads, the owned directory listing, primary-source browsing, literal artifact writes, and read-only artifact checks were performed.
- `response.txt` contains the entire substantive user-facing answer and complete inline code. `research-notes.md` records actual sources and this explicit nonexecution.
- The code and statistics received a static reasoning review. They have not been runtime-tested; the response makes no passing-test or empirical performance claim.
- File writes used quoted here-documents, so shell expansion, command substitution, and answer-content execution were disabled.

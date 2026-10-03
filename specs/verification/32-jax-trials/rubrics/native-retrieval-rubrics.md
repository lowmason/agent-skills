# Native evaluation and optimization retrieval checks

These reference/application checks are declared before RE/RS candidate exposure.
The approved task briefs specify their retrieval goals but no numeric item split.
These are new predeclared four-item summaries, not an inherited external rubric.
There is no matched RE/RS control, no pass cutoff, and no measured runtime claim.
Keep this rubric outside application-agent context.

Each item uses the existing convention:2 met,1 partial,0 absent or demonstrated
incorrect. Read the full response and actual reference-read record manually.
An omitted check is not a demonstrated numerical/model failure. The retrieval
question asks actionable locations and application summaries, not complete code
or experimental execution. Refine only a concrete meaningful source gap.

## RE: generative and LLM evaluation (8 maximum)

Prompt: Which references should I use to evaluate a generative model and an LLM
after preference optimization? Explain the main evaluation units and artifacts
to retain.

| Item | Full-coverage evidence |
|---|---|
| Actual relevant retrieval | Recorded reference reads support the answer; identifies the applicable protocol, domain-check and experiment-record locations. All references need not be read when their relevant material is already supplied in another read source. |
| Generative units and checks | Names the sample/conditioning or grouped evaluation units and task-relevant quality/diversity checks; distinguishes objective loss from generated-output quality and states sampling/conditioning comparability. |
| LLM post-preference comparison | Names held-out prompt/response units and applicable quality/preference/safety or task checks; controls tokenizer/prompt/decoding, contamination and budget/seed comparability rather than treating preference loss as sufficient quality evidence. |
| Retained artifacts and limits | Retains configuration/data/splits, checkpoints or exports, predictions/generations, metric/seed/budget results and a limited decision/next action as applicable; does not require posterior artifacts for runs without posterior draws. |

## RS: loss versus recompilation/cache retrieval (8 maximum)

Prompt: My training loss is not improving, and my generation loop recompiles for
different input lengths. Which guidance handles each issue, and where should I
look for cache checks?

| Item | Full-coverage evidence |
|---|---|
| Correct task routing | Routes learning/objective/state correctness to deep-learning, and reproduced recompilation/generation execution to optimize-jax; recognizes their different checks without assuming an unobserved cause. |
| Actual relevant retrieval | Recorded profiling/inference reference reads support the named locations and actionable answer. |
| Recompilation and measurement location | Locates shape/static-signature/compile evidence and synchronized timing boundaries; describes a next observation rather than asserting unmeasured speed or a universal bucketing remedy. |
| Cache correctness and limits | Locates independent full-prefix reference/parity and position/mask/boundary guidance; distinguishes cache correctness from measured throughput and states relevant tiny-fixture or real-recipe limits. |

The controller owns this rubric and the archival record. The conductor owns
fresh dispatch and complete manual scoring. Skill authors receive the completed
scoring only after a verified immutable candidate snapshot exists.

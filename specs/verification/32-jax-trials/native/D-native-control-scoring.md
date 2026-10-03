# D native control scoring

Status: all eight control applications complete; manual rubric scoring and artifact validation complete. No application/model runtime success claim.

Eight fresh built-in Codex applications: five D1, one each D2/D3/D4. These controls withhold the new JAX guidance; they were collected after Task 2 authorship and are a fresh native baseline, not the original pre-authoring Claude controls. No cross-runtime improvement is inferred. Exact model/effort identifiers are not exposed by the collaboration API; inherited runtime is recorded honestly. Each application uses default agent type, fork_turns=none, and a new spawn identity. Scheduling deviation: the built-in thread limit rejected the second-child dispatch twice while a completed author retained scheduling state; a new attempt after the author completed an acknowledgement succeeded. At most two application children are active. This deviation does not affect sample grades. No delivered application/model code is executed by agents or scorer; the task explicitly allows nonexecution.

Scores follow the original rubric: 2 met, 1 partial, 0 absent or demonstrated incorrect. Valid plain JAX is allowed. An omitted check is identified separately from a concrete defect. Scores assess supplied analysis/code, not observed runtime success. No new pass threshold is imposed.

D1 criteria (12 maximum): valid-unit reduction; compatible transforms/optimizer; explicit train/eval/randomness; finite gradients; meaningful tiny-data learning; recovery beyond weights including next-update parity and stated data progress.
D2 criteria (12): Equinox/Diffrax path; observation/interpolation; solver/tolerances/adjoint; gradient reference; tighter-tolerance sensitivity and fitted behavior; conditional precision policy.
D3 criteria (10): representation/parity/output; e3nn native integration; rotation/inversion tests matching declared symmetry; permutation tests for aggregation; no undocumented NNX integration promise.
D4 criteria (12): supported model/checkpoint/tokenizer mapping; SFT/completion/attention masks; frozen/trainable selection; chosen/rejected/reference log-probabilities; valid-token reduction; no Transformers-v5 FlaxAutoModel or assumed TPU promise.

## Samples

### D1 control 1 — 9/12; vector [2, 2, 2, 1, 0, 2]

- **Reduction 2:** per-valid-target SSE/count and dataset-wide validation aggregation are correct ([loss](D1-codex-control-1/response.txt:180), [validation](D1-codex-control-1/response.txt:229)); padded hidden-state updates are frozen ([cell](D1-codex-control-1/response.txt:147)).
- **Transforms/optimizer 2:** valid plain-JAX parameter PyTree, jitted recurrent scan, value-and-grad, and Adam moments/update count ([initialization](D1-codex-control-1/response.txt:116), [update](D1-codex-control-1/response.txt:188)). No NNX is required for this valid alternative.
- **Mode/randomness 2:** no dropout or BatchNorm; deterministic independent training/validation streams and epoch-derived shuffle make stateless evaluation and randomness explicit ([policy](D1-codex-control-1/response.txt:17), [data loop](D1-codex-control-1/response.txt:330)).
- **Finite gradients 1:** checks finite inputs and training loss and compares padding-invariant gradients, but omits an explicit finite-gradient assertion ([loss guard](D1-codex-control-1/response.txt:350), [gradient check](D1-codex-control-1/response.txt:462)). This is an omitted check, not a demonstrated NaN defect.
- **Tiny learning 0:** supplies 512-sequence training and validation with persistence baseline; no fixed tiny-data learning/overfit check or meaningful reduction criterion ([configuration](D1-codex-control-1/response.txt:47), [stated limit](D1-codex-control-1/response.txt:426)). Training success remains unmeasured, as allowed.
- **Recovery 2:** serializes parameters, both Adam moments, step, configuration, epoch/next batch/metric accumulators; reconstructs deterministic data order and checks restored progress plus next loss/full optimizer state ([save](D1-codex-control-1/response.txt:263), [resume test](D1-codex-control-1/response.txt:483)). Preserve this successful control behavior.

Actual sources and ordinary skill reads are in [research notes](D1-codex-control-1/research-notes.md:10). Only official JAX documentation was used; model/tests were not executed. [Conditions](D1-codex-control-1/conditions.json:1) and [first helper read](D1-codex-control-1/read-events.jsonl:1) verify fresh identity, nonempty 510-line delivery, and withheld guidance.

### D1 control 2 — 10/12; vector [2, 2, 2, 2, 0, 2]

- **Reduction 2:** explicitly predicts one next value per prefix; ordinary example-average MSE is correct for that unit. Padding freezes state and is sanitized ([task/output](D1-codex-control-2/response.txt:1), [loss](D1-codex-control-2/response.txt:126)).
- **Transforms/optimizer 2:** valid plain JAX scan, value-and-grad, and complete Adam state ([update](D1-codex-control-2/response.txt:156)).
- **Mode/randomness 2:** deterministic stateless GRU, independent splits, split sampling key per update; validation leaves key untouched ([initialization](D1-codex-control-2/response.txt:101), [policy](D1-codex-control-2/response.txt:407)).
- **Finite gradients 2:** finite gradient norm/loss is asserted for the structural fixture and checked before accepting every training update ([fixture](D1-codex-control-2/response.txt:329), [guard](D1-codex-control-2/response.txt:378)).
- **Tiny learning 0:** a small fixture performs one update for structural checks; no fixed tiny-data learning/overfit or loss-reduction test is supplied ([self-test](D1-codex-control-2/response.txt:311)). Omitted check, not demonstrated failure to learn.
- **Recovery 2:** saves params, both moments, step, next key, full train/validation arrays and configuration; restores typed key and verifies next-update full-state equality. Data policy is explicit with-replacement sampling, so key+step+saved arrays identify progress ([checkpoint](D1-codex-control-2/response.txt:212), [parity](D1-codex-control-2/response.txt:299), [policy](D1-codex-control-2/response.txt:407)). Preserve this contrary baseline success; discarded comparison losses do not negate the demonstrated next-update state contract.

[Actual sources and nonexecution](D1-codex-control-2/research-notes.md:1): official JAX and NumPy docs plus clean-code/verification skills. No model or self-test execution; AST parsing only. [Conditions](D1-codex-control-2/conditions.json:1) and [recorded first read](D1-codex-control-2/read-events.jsonl:1) verify fresh 424-line response and withheld guidance.

### D1 control 3 — 8/12; vector [2, 2, 2, 1, 0, 1]

- **Reduction 2:** correct shifted-pair mask and SSE/valid-token loss; whole-dataset validation uses summed counts ([data](D1-codex-control-3/response.txt:73), [loss](D1-codex-control-3/response.txt:176), [aggregation](D1-codex-control-3/response.txt:237)). Finite padding changes preserve gradients in the supplied fixture.
- **Transforms/optimizer 2:** pure parameter PyTree with valid JAX scan/value-and-grad and Optax chain/init/update/apply ([training](D1-codex-control-3/response.txt:190)).
- **Mode/randomness 2:** explicit no dropout, reset hidden state, independent split seeds and retained NumPy shuffle generator ([contract](D1-codex-control-3/response.txt:504)).
- **Finite gradients 1:** finite loss checks and padding-gradient invariance; explicit finite-gradient check omitted ([guard](D1-codex-control-3/response.txt:223), [gradient fixture](D1-codex-control-3/response.txt:385)). No numerical gradient defect demonstrated.
- **Tiny learning 0:** small structural fixture runs epochs for checkpoint comparison, with no learning reduction/overfit assertion. Normal training prints losses and baseline only ([fixture](D1-codex-control-3/response.txt:361), [interpretation](D1-codex-control-3/response.txt:508)).
- **Recovery 1:** strong full-state/optimizer/configuration/RNG/data-digest checkpoint and epoch-boundary replay policy. The supplied test compares final state after the next two-update epoch, but omits parity of the immediate next update at the restored boundary ([save](D1-codex-control-3/response.txt:265), [test](D1-codex-control-3/response.txt:396), [resume](D1-codex-control-3/response.txt:451)). Partial contract coverage, not a demonstrated restoration defect.

[Research notes](D1-codex-control-3/research-notes.md:1) identify clean-code and official JAX/Optax sources, AST-only verification, and explicit nonexecution. [Conditions](D1-codex-control-3/conditions.json:1) and [first read](D1-codex-control-3/read-events.jsonl:1): fresh default agent, 516-line full delivery, no guidance supplied.

### D1 control 4 — 9/12; vector [2, 2, 2, 1, 0, 2]

- **Reduction 2:** one next value per context, actual-example mask excludes dummy rows; correct validation sum/count and manual partial-batch check ([contract](D1-codex-control-4/response.txt:1), [loss](D1-codex-control-4/response.txt:139), [check](D1-codex-control-4/response.txt:427)).
- **Transforms/optimizer 2:** valid plain-JAX scan/value-and-grad/manual Adam with moments/count ([update](D1-codex-control-4/response.txt:150)).
- **Mode/randomness 2:** deterministic recurrent model without mutable layers, independent data seeds, split epoch key, validation does not advance randomness ([initialization](D1-codex-control-4/response.txt:84), [loop](D1-codex-control-4/response.txt:327)).
- **Finite gradients 1:** computes gradient norm and checks finite losses; supplied padding-input-gradient test, but no explicit parameter-gradient finiteness guard ([norm](D1-codex-control-4/response.txt:153), [checks](D1-codex-control-4/response.txt:409)). Omitted check, no demonstrated numerical failure.
- **Tiny learning 0:** small fixtures verify structure/recovery, with no fixed tiny-data learning or loss-reduction check; general validation/baseline interpretation is appropriate but does not establish that criterion ([tests](D1-codex-control-4/response.txt:402), [interpretation](D1-codex-control-4/response.txt:479)).
- **Recovery 2:** complete params/moments/step/config/next epoch/next key/datasets saved; verifies next shuffle plus immediate next full-state update after round-trip ([checkpoint](D1-codex-control-4/response.txt:206), [parity](D1-codex-control-4/response.txt:443)). Epoch-boundary replay limits explicitly stated; successful control contract preserved.

[Research notes](D1-codex-control-4/research-notes.md:1) record clean-code/verification, primary JAX/NumPy sources, and AST-only inspection. [Conditions](D1-codex-control-4/conditions.json:1) and [first helper read](D1-codex-control-4/read-events.jsonl:1) verify a fresh 481-line response with guidance withheld. No model/tests executed.

### D1 control 5 — 10/12; vector [2, 2, 2, 2, 0, 2]

- **Reduction 2:** shifted observed-prefix predictions, explicit three-target warmup policy, valid scored-token SSE/count; dummy rows and terminal/example metric units declared ([contract](D1-codex-control-5/response.txt:3), [objective](D1-codex-control-5/response.txt:193), [validation](D1-codex-control-5/response.txt:238)).
- **Transforms/optimizer 2:** correct plain-JAX scan/value-and-grad/manual Adam PyTree and state ([training](D1-codex-control-5/response.txt:215)).
- **Mode/randomness 2:** no mutable/dropout layers; separate seed-derived datasets and saved shuffle RNG, initialization key no longer needed after parameters exist ([policy](D1-codex-control-5/response.txt:504)).
- **Finite gradients 2:** structural fixture asserts finite norm, and training checks finite gradient norm/errors on every update ([fixture](D1-codex-control-5/response.txt:406), [guard](D1-codex-control-5/response.txt:472)).
- **Tiny learning 0:** fixed small fixture tests correctness/recovery without a meaningful learning reduction/overfit check. General held-out improvement versus persistence is proposed, with no tiny-data protocol ([self-test](D1-codex-control-5/response.txt:373), [interpretation](D1-codex-control-5/response.txt:506)). Omission, not measured failed learning.
- **Recovery 2:** parameters/moments/count/config/RNG/epoch/history saved with strict epoch-step consistency, deterministic synthetic data reconstruction; next shuffle and complete immediate next update—including returned error/count/norm—compared ([save](D1-codex-control-5/response.txt:277), [load](D1-codex-control-5/response.txt:313), [parity](D1-codex-control-5/response.txt:411)). Strong contrary baseline success retained.

[Sources and notes](D1-codex-control-5/research-notes.md:1) identify actual official JAX pages, clean-code/develop-testing-strategy/verification skills, and explicit nonexecution. [Conditions](D1-codex-control-5/conditions.json:1) and [first read](D1-codex-control-5/read-events.jsonl:1) verify a fresh complete 508-line answer and withheld guidance.

D1 controls subtotal: **46/60**; totals **9, 10, 8, 9, 10**. All five have correct reduction, valid transforms/optimizer, and explicit mode/randomness. Finite-gradient checks: two met, three partial. Tiny-data learning checks: absent in all five. Recovery: four met, one partial for omitted immediate-update comparison; none has a demonstrated restoration defect.

### D2 control — 12/12; vector [2, 2, 2, 2, 2, 2]

- **Native path 2:** appropriate Diffrax with a directly learned JAX parameter vector for a small identifiable damped rotation. Equinox is unnecessary for this valid plain-JAX model; a neural-field extension is explained ([choice](D2-codex-control-1/response.txt:9), [extension](D2-codex-control-1/response.txt:248)).
- **Observation/interpolation 2:** actual irregular grids, exact known initial state and full observation assumptions, SaveAt interpolation versus internal integration steps; ragged/missing/uncertain initial-state contracts are explicit ([contract](D2-codex-control-1/response.txt:7), [generation](D2-codex-control-1/response.txt:123), [real-data limits](D2-codex-control-1/response.txt:250)).
- **Solver/tolerances/adjoint 2:** Tsit5, adaptive PID with stated tolerances, optional fixed steps, RecursiveCheckpointAdjoint, failure visibility and step limit ([solve](D2-codex-control-1/response.txt:64), [adjoint explanation](D2-codex-control-1/response.txt:246)).
- **Gradient reference 2:** finite reverse-mode derivatives tested away from optimum; coordinate/mixed directions and epsilon sweep against fixed-step finite differences, adaptive derivatives against exact-solution objective ([checks](D2-codex-control-1/response.txt:153)).
- **Sensitivity/fitted behavior 2:** progressive adaptive-gradient tolerances, synthetic physical-parameter recovery and meaningful loss reduction, independent new-initial-condition interpolation/forecast errors, fixed learned predictions versus tighter solve ([gradient convergence](D2-codex-control-1/response.txt:177), [fit/held-out](D2-codex-control-1/response.txt:187), [tight solve](D2-codex-control-1/response.txt:221)). Contrary control success retained.
- **Precision 2:** float64 justified by this fixture's tight solver/gradient checks, without a blanket Bayesian x64 policy ([setting](D2-codex-control-1/response.txt:25), [reason](D2-codex-control-1/response.txt:230)).

[Research notes](D2-codex-control-1/research-notes.md:1) record testing-strategy/clean-code and actual official Diffrax/JAX/Optax sources. Checks are supplied gates with explicit nonexecution; no convergence or numerical success claimed. [Conditions](D2-codex-control-1/conditions.json:1) and [first read](D2-codex-control-1/read-events.jsonl:1) verify a fresh complete 257-line answer with guidance withheld.

### D3 control — 7/10; vector [2, 0, 1, 2, 2]

- **Representation/output 2:** clear scalar shape (), vector shape (3,), row-storage transformation, centered invariant features and scalar weights on full vectors; explains polar reflection behavior and translation-invariant displacement semantics ([contract/proof](D3-codex-control-1/response.txt:3), [model](D3-codex-control-1/response.txt:59), [parity](D3-codex-control-1/response.txt:199)). The pure-JAX construction is mathematically valid and satisfies the user's modeling task.
- **Named e3nn integration coverage 0:** no e3nn reference/application path is supplied; instead uses valid original plain-JAX array operations and the EGNN construction principle ([implementation](D3-codex-control-1/response.txt:19), [sources](D3-codex-control-1/research-notes.md:24)). This original rubric coverage score is separate from mathematical correctness. It is not an invalid-model finding and implies no library-use prohibition.
- **Declared transformation checks 1:** substantial proper-rotation checks, known rotation, output/nonzero probe, JIT/eager agreement, multiple clouds/parameters; reflection symmetry additionally claimed but its explicit inversion/reflection test is omitted ([rotations/probe](D3-codex-control-1/response.txt:121), [loop](D3-codex-control-1/response.txt:157), [reflection claim](D3-codex-control-1/response.txt:199)). True task-specific omission, not a symmetry math defect.
- **Permutation 2:** reverse-index permutation is checked for every parameter/cloud combination, appropriately matching the global aggregation contract; translation checked too ([checks](D3-codex-control-1/response.txt:163)). Preserve successful control behavior.
- **NNX integration claim 2:** no undocumented NNX/e3nn integration promise; describes pure JAX grad/vmap and explicitly limits varying-cloud batching/padding ([scope](D3-codex-control-1/response.txt:197)).

[Actual sources/nonexecution](D3-codex-control-1/research-notes.md:1): official JAX and primary EGNN paper, ordinary clean-code/testing-strategy/verification skills, AST-only inspection. [Conditions](D3-codex-control-1/conditions.json:1) and [first read](D3-codex-control-1/read-events.jsonl:1) verify fresh complete 199-line delivery with withheld guidance. Nothing in this score negates the algebraic construction's successful rotation/permutation contract.

### D4 control — 12/12; vector [2, 2, 2, 2, 2, 2]

- **Loading/mapping 2:** explicit small GPT-2 native-Flax checkpoint, immutable resolved revision shared by tokenizer/weights, intentionally pinned Transformers 4.44.2 API; verifies paths/shapes/vocab/context and zero-adapter logit parity. Proposed dependency compatibility is explicitly untested ([loading plan](D4-codex-control-1/response.txt:3), [pins](D4-codex-control-1/response.txt:56), [loader](D4-codex-control-1/response.txt:244), [preflight](D4-codex-control-1/response.txt:495)). No default-v5 promise.
- **SFT/masks 2:** declared BOS/prefix/response/EOS serialization, completion versus attention masks, shift and first-response-token contract, explicit right-padding positions in model call, excluded-logit and hand-count checks ([data/masks](D4-codex-control-1/response.txt:32), [packing](D4-codex-control-1/response.txt:164), [forward/loss](D4-codex-control-1/response.txt:342), [mask fixture](D4-codex-control-1/response.txt:471)).
- **Frozen/trainable 2:** explicit QKV/output adapter targets, B-zero preservation, separate adapter-only optimizer and argnums=0 differentiation, backbone/reference fingerprints ([targets](D4-codex-control-1/response.txt:291), [optimizer](D4-codex-control-1/response.txt:539), [checks](D4-codex-control-1/response.txt:809)).
- **Preference/reference 2:** same-prompt pairs, selected SFT reference copied/stopped/saved, all four chosen/rejected policy/reference scores, summed completion log-probabilities and correct softplus margin sign; equality/log2 and derivative-sign checks ([semantics](D4-codex-control-1/response.txt:46), [objective](D4-codex-control-1/response.txt:393), [reference initialization](D4-codex-control-1/response.txt:780)).
- **Valid-unit reductions 2:** token-total SFT versus real-pair DPO averaging, example mask for fixed-shape filler rows and dataset-wide totals; no invalid -100 gather labels ([batching](D4-codex-control-1/response.txt:224), [reductions](D4-codex-control-1/response.txt:378), [validation](D4-codex-control-1/response.txt:436)).
- **Version/hardware promises 2:** explicitly scoped pinned legacy Flax loader, unverified environment, one process/device baseline and target-backend resource checks; no v5 FlaxAutoModel or assumed TPU ([scope](D4-codex-control-1/response.txt:56), [scale/recovery limits](D4-codex-control-1/response.txt:873), [unverified delivery](D4-codex-control-1/response.txt:879)).

[Research notes](D4-codex-control-1/research-notes.md:1) retain actual primary versioned Transformers/GPT-2/model-repository, LoRA/DPO, Optax/JAX sources and failed source-retrieval limits. The answer distinguishes its custom adapter exports from resumable training and does not claim a resume CLI. [Conditions](D4-codex-control-1/conditions.json:1) and [first read](D4-codex-control-1/read-events.jsonl:1) verify a fresh full 880-line response, guidance withheld, and explicit nonexecution. Strong contrary control success preserved.

## Completed control totals and limits

| Scenario | Samples | Scores | Subtotal |
|---|---:|---|---:|
| D1 | 5 | 9, 10, 8, 9, 10 /12 | 46/60 |
| D2 | 1 | 12/12 | 12/12 |
| D3 | 1 | 7/10 | 7/10 |
| D4 | 1 | 12/12 | 12/12 |
| **Total** | **8** | Original rubric, no new pass threshold | **77/94** |

All eight full responses manually read and scored. Read artifacts verify new spawn identities, complete first prompt reads, nonempty responses/notes and no new JAX guidance. D1's observed common omission is fixed tiny-data learning; finite-gradient checks are partial in three samples. D3 lacks named e3nn coverage and an explicit test of declared inversion behavior; its pure-JAX construction remains valid. D2/D4 and most recovery/masking/mode contracts succeed in controls. Do not turn those successes into invented discipline rules. Native controls are post-authoring fresh withheld-guidance baselines; original Claude pre-authoring controls and native outcomes remain separate. Numerical execution, compatibility, learning, and performance are unverified by these application trials, as authorized.


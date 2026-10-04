# Deep-learning evaluation verification

Status: Task 3 verification complete. The controller's eight fresh native
WITH-skill applications were fully read and manually scored, and the root
adjudicated the closed gate. Matched E1–E3 candidates scored 66/66 against native
controls 65/66; the separate RE retrieval case scored 8/8. The canonical CPU
pass is reused under freshly verified identical source/profile hashes. Fresh
final repository, source/schema, archive and whitespace gates are recorded below.
The four reusable skill files remain exactly the tested/frozen snapshot.
Task 3 of the approved [design](../jax-deep-learning-skills.md) and
[plan](../plans/32-jax-deep-learning-skills.md).

## Pre-authoring controls and authoring form

The complete [historical control scoring](32-jax-trials/E-control-scoring.md)
and [native control scoring](32-jax-trials/native/E-native-control-scoring.md)
were read before authoring. The runtime cohorts stay separate. Native controls
are five fresh E1 full successes (50/50), E2 full success (8/8), and E3 7/8,
for 65/66 descriptive coverage under the original rubric. Native E3 preserves
strong solver convergence/gradient, declared transformation, and low-loss versus
proof checks. Its only partial item omits a distinct predictive-uncertainty
assessment; no conflation, API failure, method-superiority claim, or posterior
requirement is demonstrated. E1/E2 successes do not justify new disciplinary
prohibitions or a claimed improvement.

Historical E controls retain their successful budget-confound, held-out ranking,
matched-experiment and nonposterior decisions. Their narrower gaps concern
physical-compute versus tokens, actual pairing/shared inputs, practical decision
thresholds, some interval/equivalence reporting, temporal/window contracts,
dtype/convergence/statistic naming, declared parity, and predictive uncertainty.
These are reference/recipe and required-output gaps. The skill uses original
positive contracts and observable conditional checks. The native E3 omission
motivates a required predictive-uncertainty slot, without imposing posterior
artifacts. Supplied guidance and scored applications do not establish automatic
catalog loading or executed model behavior.

## Numerical strategy recorded before code

One canonical self-contained JAX/NumPy Markdown block, `paired-evaluation`,
will run through the existing Task 1 isolated CPU subprocess runner, without a
preamble, network, model/checkpoint downloads, repository fixture or new script.
The unchanged Task 2 Python 3.13 profile is reused. The explicit `cpu-example`
marker selects this opt-in check; the existing fast process-contract tests
remain separate, so no new pytest marker or hidden scientific dependency is
introduced. Existing runner baseline: 37/37 passed in 0.90s, exit 0.

| Invariant class | Required property | Smallest falsifying fixture/check |
|---|---|---|
| Structural | Predictions retain named `(seed, sample, token)` axes; mask is `(sample, token)`; every sample has an eligible target | Two methods, two seeds, three held-out sample IDs, three token positions, unequal valid lengths; shape and empty-unit rejection assertions |
| Relational | Valid-token pooled MSE equals an independent hand result; macro sample mean is separately defined | Residual magnitudes `[1]`, `[2,2]`, `[3,3,3]` give sample MSE `[1,4,9]` and pooled `(1+8+27)/6 = 6`; seed-scaled results `[6,24]`; retain both aggregations |
| Relational | Padding is inert and the methods use identical held-out units | Change only padded predictions/targets, including nonfinite padding, and assert unchanged scores; compare identity/order manifests before subtraction; altered/reordered IDs must reject |
| Bounds | Eligible values and per-sample denominators are valid | Reject a nonfinite eligible prediction, an all-padding sample and a nonboolean mask; reductions return finite sample/run scores |
| Reproducibility | Every seed score and original budget stays inspectable | Retain both per-seed and per-sample arrays plus initialization/data-order labels and explicit per-run token/step/device-time/tuning metadata; equality checks against literal expected records |
| Scope | Pairing is held-out-unit pairing, with run pairing explicitly undeclared | Keep named sample-difference arrays but compute no CI, token-as-run confidence, seed-ID variance reduction or universal winner; synthetic budgets are deliberately unequal |

Float32 reduction uses `rtol=1e-6, atol=1e-6` against exactly representable
small hand values; masked nonfinite entries are selected out before residual
arithmetic. This tests evaluation arithmetic/identity/record contracts only.
It does not establish statistical coverage, domain model quality, training,
production validity, physical-compute efficiency or predictive calibration.
The example contains no interval estimator or learned checkpoint.

Exact opt-in execution command, from the assigned checkout root:

```bash
JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/evaluate-deep-learning/
```

## Stable-draft numerical and focused gates (2026-10-03)

Actual interpreter/platform: Python 3.13.8,
macOS-26.6.2-arm64-arm-64bit-Mach-O, JAX backend cpu, one CpuDevice(id=0).
Direct packages: jax/jaxlib 0.11.2, NumPy 2.5.3, Flax 0.12.10, Optax 0.2.8,
Orbax-checkpoint 0.12.6, Equinox 0.13.8, Diffrax 0.7.2 and e3nn-jax 0.21.0.
The complete pinned Task 2 profile was reused without resolution or edits.

| Command (assigned checkout root unless specified) | Actual result |
|---|---|
| From build/: `uv run --python 3.13 --with pytest python -m pytest -q test_check_jax_examples.py` | Exit 0; 37 passed in 0.90s before authoring |
| Exact CPU command printed above on skills/evaluate-deep-learning/ | Exit 0; paired-evaluation PASS; 1 selected/executed/passed, first execution |
| `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` | Exit 0; no output |
| `uv run --python 3.13 python build/check_provenance.py` | Exit 0; no output |
| `uv run --python 3.13 python build/check_snippets.py skills/evaluate-deep-learning/` | Exit 0; no output; repeated after self-review prose cleanup, also exit 0 |
| From build/: `uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies` | Exit 0; 1 passed, 61 deselected in 0.27s |
| `uv run --python 3.13 --with pyyaml python /private/tmp/task3-source-audit.py` | Exit 0; exactly four Markdown files, one expected CPU ID, three own links resolve, 13-field completed YAML record parses, 18 originals agree, source/profile hashes and limits verified |
| `git diff --check` | Exit 0; no output, rechecked after prose cleanup |
| `git diff --cached --name-only` | Exit 0; empty; no Task 3 staging or commit |

The runner executed the complete canonical block in an isolated CPU subprocess,
without a Bayesian preamble. All hand-reduction, padding-invariance,
identity/eligibility rejection, per-seed score and budget-record checks passed.
No failing numerical check was exempted or its tolerance widened. This is an
invariant-first numerical fixture, not library/pipeline feature development:
its strategy was persisted before code and no artificial numerical RED failure
is claimed. The pre-authoring application omission is recorded above; completed
candidate application evidence and its limits are recorded below.

A self-review read all four actual Markdown files and the scoped NOTICE,
CLAUDE.md and README.md diff. One reference sentence narrating native trial
history was removed from the reusable protocol. Its canonical code hash stayed
identical; the focused parse/source/whitespace gates were rerun. No new defect
was found. Host validation is deliberately outside jit, masked nonfinite padding
is a forward evaluation contract only, and same integer seed labels do not imply
paired training. The completed example record explicitly labels token/step/tuning
budgets as illustrative supplied metadata, with no training/device cost measured.

Main body: 1166 whitespace-delimited words after frontmatter; description:
298 stripped characters. No model/effort/fork pin. Bare whole-skill handoffs
introduced no installer dependency; all depth is in the three own references.
Existing Bayesian ledger/artifacts, training sources, runtime assets and build
tooling are unchanged. The current authoritative NOTICE inventory is 18
originals and agrees with CLAUDE.md and README credit additions.

### Stable source identities

These hashes define the four-file application input. Canonical extracted source
is paired-evaluation at protocol.md:116 (first execution was at line117 before
the unrelated narration removal), SHA-256
`785dfa1c6400030bc26a3dc44d56f3966a751015d82e3fb3ea4e796eabc5c1dd`.
Only the location moved; numerical source is unchanged since its passing run.

| File | SHA-256 |
|---|---|
| `skills/evaluate-deep-learning/SKILL.md` | `db75cc39c357cd80340d39d7255bcb9c53602b6bbb0c5af9789169b5a82607c8` |
| `skills/evaluate-deep-learning/references/domain-checks.md` | `984209d2ee4b18b926fc722b24baec7cde470058f59fa7a64916a887e305156c` |
| `skills/evaluate-deep-learning/references/experiments.md` | `1254907bbaf6cc731e22a92b15cc4e7b17ce32f7f3486e8b4f472e582da24518` |
| `skills/evaluate-deep-learning/references/protocol.md` | `65d69194053e9183276a39a3e30dd1ee372da2bf3537a0b63306c10c0f0d672f` |
| `NOTICE` | `114e261b29a5fd83ca9b8feede8a25dc3ab2f1f0378adeff29bf0a50d18e4757` |
| `CLAUDE.md` | `704aaed2643b6d8de9f01a99617cd358845b922c8575a1420852df329430999c` |
| `README.md` | `70b102a5df35a5ca0725dce8834160e1d6e20bfb8dd583c0ce2b0357dbbe8877` |
| `specs/verification/32-jax-cpu.in` | `b464a7e53420e93a7d11dd209ed47238674d951f64b74292a53faa1c4f1b7ccd` |
| `specs/verification/32-jax-cpu.txt` | `c8bd73640ca1d2cd1f86a211554e9ceac244054d629370a931738a8b5b10258c` |

### Primary-source review and limits

Reviewed task-specific primary sources on 2026-10-03: Bouthillier's benchmarking
variance paper; Pineau's reproducibility report; Koehn's translation-resampling
paper; Politis/Romano's stationary-bootstrap report; Hyndman/Athanasopoulos's
rolling-origin treatment; WILDS; e3nn-jax irreps docs; Diffrax Solution/adjoints;
JAX where and current dtypes/x64 docs; Guo's calibration paper; Parmar's image-
preprocessing evaluation paper; Kynkaanniemi's precision/recall paper; HELM;
and Lee's deduplication paper. Each cited source is linked beside the relevant
claim in the skill references. Source prose/code is not reproduced and no
manual/paper/model/data payload is bundled. Unused or mistaken bibliographic
probes were not adopted as citations; the JAX dtypes redirect was followed to
the current /101/ page. Unversioned web docs inform reference claims; actual
fixture compatibility is established separately by the pinned execution.

The skill does not promise executed domain models, statistical interval
coverage, real tokenizer/checkpoint/contamination audits, a calibrated predictive
distribution, GPU/TPU recipes, latency/cost or a method winner. Only the local
arithmetic and bookkeeping fixture was executed. Application/retrieval scores
assess delivered artifact coverage, with supplied guidance, rather than automatic
catalog discovery or executed training/generation/statistical code.

## Closed native candidate gate

The root-adjudicated [complete manual candidate scoring](32-jax-trials/native/E-native-candidate-scoring.md)
and [archive manifest](32-jax-trials/native/E-candidate-archive.json) were committed
by the controller at `321b14c99bfe0fd4bea21f108c20f624b1c4664f` before finalization.
Every response, research note, prompt, condition and read event is durable beside
that report. The metadata audit checks identities, hashes, lengths,
read conditions, links and score arithmetic; it does not replace the conductor's
full manual reading/scoring or execute delivered application code.

Original matched scores use 2 met, 1 partial, 0 absent or demonstrated incorrect,
with five E1 items/10 and four E2/E3 items/8. RE uses the separately
[predeclared native retrieval rubric](32-jax-trials/rubrics/native-retrieval-rubrics.md),
four items/8, committed before exposure and withheld from application agents.
There is no new pass cutoff or inherited external numeric RE rubric.

| Candidate | Full response | Notes / conditions / actual reads | Score | Actual own-reference reads |
|---|---|---|---:|---|
| E1-codex-candidate-1 | [response](32-jax-trials/native/E1-codex-candidate-1/response.txt:1), 31 lines | [notes](32-jax-trials/native/E1-codex-candidate-1/research-notes.md:1), [conditions](32-jax-trials/native/E1-codex-candidate-1/conditions.json:1), [events](32-jax-trials/native/E1-codex-candidate-1/read-events.jsonl:1) | 10/10 | experiments, protocol |
| E1-codex-candidate-2 | [response](32-jax-trials/native/E1-codex-candidate-2/response.txt:1), 28 lines | [notes](32-jax-trials/native/E1-codex-candidate-2/research-notes.md:1), [conditions](32-jax-trials/native/E1-codex-candidate-2/conditions.json:1), [events](32-jax-trials/native/E1-codex-candidate-2/read-events.jsonl:1) | 10/10 | protocol, experiments |
| E1-codex-candidate-3 | [response](32-jax-trials/native/E1-codex-candidate-3/response.txt:1), 28 lines | [notes](32-jax-trials/native/E1-codex-candidate-3/research-notes.md:1), [conditions](32-jax-trials/native/E1-codex-candidate-3/conditions.json:1), [events](32-jax-trials/native/E1-codex-candidate-3/read-events.jsonl:1) | 10/10 | experiments, protocol, domain-checks |
| E1-codex-candidate-4 | [response](32-jax-trials/native/E1-codex-candidate-4/response.txt:1), 27 lines | [notes](32-jax-trials/native/E1-codex-candidate-4/research-notes.md:1), [conditions](32-jax-trials/native/E1-codex-candidate-4/conditions.json:1), [events](32-jax-trials/native/E1-codex-candidate-4/read-events.jsonl:1) | 10/10 | experiments, protocol |
| E1-codex-candidate-5 | [response](32-jax-trials/native/E1-codex-candidate-5/response.txt:1), 43 lines | [notes](32-jax-trials/native/E1-codex-candidate-5/research-notes.md:1), [conditions](32-jax-trials/native/E1-codex-candidate-5/conditions.json:1), [events](32-jax-trials/native/E1-codex-candidate-5/read-events.jsonl:1) | 10/10 | experiments, protocol |
| E2-codex-candidate-1 | [response](32-jax-trials/native/E2-codex-candidate-1/response.txt:1), 301 lines | [notes](32-jax-trials/native/E2-codex-candidate-1/research-notes.md:1), [conditions](32-jax-trials/native/E2-codex-candidate-1/conditions.json:1), [events](32-jax-trials/native/E2-codex-candidate-1/read-events.jsonl:1) | 8/8 | protocol, domain-checks, experiments |
| E3-codex-candidate-1 | [response](32-jax-trials/native/E3-codex-candidate-1/response.txt:1), 385 lines | [notes](32-jax-trials/native/E3-codex-candidate-1/research-notes.md:1), [conditions](32-jax-trials/native/E3-codex-candidate-1/conditions.json:1), [events](32-jax-trials/native/E3-codex-candidate-1/read-events.jsonl:1) | 8/8 | protocol, domain-checks, experiments |
| RE-codex-candidate-1 | [response](32-jax-trials/native/RE-codex-candidate-1/response.txt:1), 75 lines | [notes](32-jax-trials/native/RE-codex-candidate-1/research-notes.md:1), [conditions](32-jax-trials/native/RE-codex-candidate-1/conditions.json:1), [events](32-jax-trials/native/RE-codex-candidate-1/read-events.jsonl:1) | 8/8 | experiments, domain-checks, protocol |

Five E1 candidates total 50/50, E2 8/8, E3 8/8: **matched 66/66**. Native
controls retain E1 50/50, E2 8/8 and E3 7/8: **65/66**. Separate RE is **8/8**;
74/74 combined is only descriptive bookkeeping across the two rubrics.

All five E1 samples retain the budget/seed/sample comparison, distinguish
observed endpoints from method superiority, and propose common-budget evidence
with honest decision limits. All five native controls already met those items.
The protocol supplied to candidates contains the exact A/B errors and budget
example. These five fresh contexts demonstrate adherence/application and
reference coverage; they do not demonstrate generalization to an unseen numeric
comparison or improvement over the already successful controls.

E2 retains chronological leakage controls, precise window/origin/horizon units,
paired dependence-aware aggregation/resampling and prespecified metrics, all
already successful in the native control. E3 retains its control's strong
solver/gradient, declared symmetry and loss-versus-proof checks, while explicitly
supplying the previously partial predictive-uncertainty distinction/assessment.
That single delivered-coverage point is the sole matched difference. It is no
statistically established agent improvement or measured scientific validation.
The control omission was neither false uncertainty conflation nor an API defect.

RE retrieved all three references and applied their generative units and
quality/diversity/conditioning checks, LLM post-preference comparison policies,
and reconstructable neural artifacts/limits. It is a new reference/application
coverage sample without a matched RE control, historical numeric decomposition,
full implementation requirement or executed generative/LLM success claim.
No meaningful candidate source gap or demonstrated static defect was found.
No reusable skill source was changed after freezing; no repeat candidate gate
was needed.

### Actual conditions, reads and payload identities

Each candidate uses a distinct new default built-in Codex collaboration agent,
`fork_turns=none`, with no reuse/followup/model override. Exact inherited
model/effort identifiers were not exposed; no provider alias is invented.
Ordinary catalog skills and read-only primary-source research were available;
actual sources, ordinary-skill applicability and access failures remain in each
complete notes file. The full authorized task and main SKILL.md were supplied
in the first hash-recorded read; references were read on demand through the
helper. Every condition explicitly records automatic loading as unobserved.
The final metadata audit verifies all eight unique spawn identities, complete
prompt bytes/hashes, first full-main reads and each reference digest/byte count
against the immutable four-source manifest. These conditions establish supplied
context, not automatic skill discovery or loading.

| Supplied task + full-main first read | SHA-256 | Bytes |
|---|---|---:|
| E1, identical prompt in five fresh contexts | `8acb91b7a8847edca9d342492f1216e2cb162a97e775a42c6cf598c80a538125` | 10287 |
| E2 | `7a8dbff1028e3c89df47e8f0c5992ee9aad9c576e6a8d4fabff89227b45c5be5` | 10183 |
| E3 | `55784aaa119eadf2fe5544370284efa6f36e1cc77f76597c946926817f4e96b8` | 10195 |
| RE | `faa5988744cb980cef1770732f41d026b482e45ef67e5c2d478fca8ac9b8fd87` | 10183 |

All full response/notes/read-event hashes are preserved in the archive manifest;
individual response hashes and full lengths are also in conditions. Guidance
hashes are the four stable identities above and exactly match the
[frozen source manifest](32-jax-trials/native/guidance-codex-candidate-evaluate-deep-learning/source-hashes.json).
Archived condition/read paths retain their actual private-tmp collection
locations as historical records; their corresponding durable payloads and
snapshot are verified in this repository.

| Durable gate artifact | SHA-256 |
|---|---|
| E-native-candidate-scoring.md | `7870901e17b3d2c2058eb0d9a29b5a8ded30fe31f6542fd2ce0d6942654d8c58` |
| E-candidate-archive.json | `bced7f19a2196582c84ecc6ff8681c9bf9c79ae3af97105cddeb60328bcbe45d` |
| E-candidate-metadata-audit.json | `87e4c4475177b79a80b2393c2b8a00f024d63410978560086e48216085180584` |
| Frozen source-hashes.json | `2398e6e6b4175e6a1e247908b5638350a9b439a06d648c778262af5267d8b5b9` |

The [conductor audit output](32-jax-trials/native/E-candidate-metadata-audit.json)
recorded eight identities, 74/74 and 113 evidence links at its run. The fresh
finalizer audit validates all 52 manifest payload hashes and 114 current
candidate-report local link endpoints (the report gained its audit link after
the archived run), plus all 105 native-control report links. No archive was
rewritten. The final verification record's local links are checked separately.

Application/model/statistical/solver/symmetry/generation code remains unexecuted.
E1 literal arithmetic and child syntax parsing are administrative/static checks;
only the canonical local CPU arithmetic fixture has recorded runtime evidence.
The old external-runtime cohort and its narrower historical gaps remain separate.
Neither cohort supplies cross-runtime causality, a real-model correctness claim,
statistical interval coverage, GPU/TPU validation or automatic-loading evidence.

## Fresh final gates and reused numerical evidence (2026-10-03 local)

The managed worktree remains on `codex/jax-deep-learning-skills`, with distinct
Git dir/common dir and no superproject. Task 3 review baseline remains
`9414fa0746348130c5c05c07533e31e462443341`, rather than the controller archive
commit. Finalization touched only this verification record and the ignored full
report; the original four skill files and NOTICE/CLAUDE/README draft additions
retain their verified hashes.

| Fresh command/check | Actual final result |
|---|---|
| `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` | Exit 0; no output |
| `uv run --python 3.13 python build/check_provenance.py` | Exit 0; no output |
| `uv run --python 3.13 python build/check_snippets.py skills/` | Exit 0; five known pre-existing advisories below |
| From build/: `uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py test_check_jax_examples.py` | Exit 0; 99 passed in 2.09s; complete 62 runtime/installer/dependency and 37 runner process-contract tests |
| `uv run --python 3.13 --with pyyaml python /private/tmp/task3-source-audit.py` | Exit 0; four-file layout, 1166 body words/298 description chars, no pin, three own links, completed 13-field YAML record, 18-original inventory, CPU ID/source/profile hashes verified |
| `uv run --python 3.13 python /private/tmp/task3-final-audit.py` | Exit 0; 52 archive hashes, four unchanged skill/snapshot pairs, eight unique contexts/full-main first reads/reference bytes and hashes, all response lengths, 74/74 arithmetic and local link endpoints verified |
| Scoped source/profile/whitespace review and `git diff --check` | Exit 0; frozen skill and CPU profile/source identities unchanged, owned tracked targets reviewed; no whitespace errors |

Global parse advisories remain outside this task: bayesian-workflow/SKILL.md:170
(slow sampling) and :184 (optional blackjax); model-criticism.md:157 (slow SBC);
state-space.md:76 (dynamax handoff sketch); develop-testing-strategy/references/
model-tests.md:83 (intentional replacement-loop lines). These are recorded
exemptions with reasons and exit 0, not a clean-output claim or new Task 3 defect.
No broad numerical/import tests were used to reinterpret those recipes.

The earlier successful `paired-evaluation` CPU run is **reused**, not freshly
rerun: all four source hashes and canonical extracted source
`785dfa1c6400030bc26a3dc44d56f3966a751015d82e3fb3ea4e796eabc5c1dd`
remain identical; profile input and resolved hashes match their records above.
No package resolution/profile refresh or numerical change occurred. Its recorded
one selected/executed/passed fixture and environment are preserved, with fresh
runner process-contract and source identity checks clearly distinguished.
No new artificial numerical RED is claimed. The manual candidate gate supplies
reference/application coverage for the pre-authoring omission, with all limits
above retained.

Final self-review read the complete owned sources/docs against the Task 3 brief
and reviewed the closed gate, condition/read identities, recorded numerical
strategy and final scoped diff. No source, provenance or implementation issue
was found; no source refinement was warranted. NOTICE's 18 originals agree
with CLAUDE.md and the exact README Mine row/original credit. Bare whole-skill
handoffs add no install dependency or posterior-artifact requirement. Only the
eight owned tracked Task 3 targets are staged for
`feat(skills): add verified deep-learning evaluation`; controller trial/rubric
archives, training/Bayesian guidance, agents/commands/runtime adapters, build
files and S work are preserved. Branch integration and plan retirement belong
to the controller and are outside this task.

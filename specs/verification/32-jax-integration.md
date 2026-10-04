# JAX skill integration verification

The Task 6 implementer checks passed on 2026-10-04 UTC: all ten selected
canonical CPU examples, 99 focused tests, the repository checks, source/evidence
integrity and private-home installer discovery. No skill, build, installer or
runtime source required a correction. This record covers the integration
checks; the controller's fresh Task 6 review and final whole-branch review are
pending at this initial record commit.

Execution checkout: `/Users/lowell/.codex/worktrees/jax-deep-learning-skills/agent-skills`,
branch `codex/jax-deep-learning-skills`. The clean starting HEAD and Task 6 scoped
BASE were `094d474d30850e1e83e0a70c6933377d0fbe9449`. Whole-branch invariant and
whitespace checks use the controller-derived BASE
`3abece14e1ff6a129c44e9ffccc46691e93856a9`. Another checkout's `main` advanced
independently; this verification neither incorporates nor removes its additions.
Later integration must preserve those concurrent changes and recompute inventories.

The implementation and evidence were checked against the [design](../jax-deep-learning-skills.md)
and [plan](../plans/32-jax-deep-learning-skills.md), using the full four prior
records: [training](32-deep-learning.md), [evaluation](32-evaluate-deep-learning.md),
[execution](32-optimize-jax.md) and [Bayesian routing](32-bayesian-routing.md).
The native manual scoring reports, frozen guidance manifests, trial conditions,
sample read events, metadata audits and archive manifests were also inspected.
Their retained manual grades are distinguished below from this task's fresh
source/hash/bookkeeping checks; this task did not regrade every raw response.

## Requirements and acceptance coverage

| Requirement | Current implementation and evidence | Verification boundary |
|---|---|---|
| R1: three navigational skills | Exactly three added live entry points: [deep-learning](../../skills/deep-learning/SKILL.md), [evaluate-deep-learning](../../skills/evaluate-deep-learning/SKILL.md), [optimize-jax](../../skills/optimize-jax/SKILL.md). Each starts its description with `Use when`, fits 1,024 characters, keeps guidance in the main context, and links its own references with conditional bare skill handoffs. | Fresh frontmatter, body budgets, branch entry-point inventory and local links checked. Archives are evidence, not skill entry points. |
| R2: shared training and state | [Training](../../skills/deep-learning/references/training.md) covers NNX/Optax state, explicit RNG, padding/loss masks, target contracts, tiny-data fitting, held-out checks, dtype/device policy and complete Orbax recovery. | `nnx-sequence-training` and `nnx-checkpoint-resume` passed. Recovery checks the next loss/update, model, Adam/schedule state, step, RNG and cursor. The fixtures use float32 on one CPU; no accelerator precision claim. |
| R3: six domain areas | Main-body navigation reaches [sequences/time series](../../skills/deep-learning/references/sequences.md), [scientific models](../../skills/deep-learning/references/scientific.md), [vision](../../skills/deep-learning/references/vision.md), [geometric models](../../skills/deep-learning/references/geometric.md), [generative models](../../skills/deep-learning/references/generative.md) and [LLMs](../../skills/deep-learning/references/llm.md). [Framework selection](../../skills/deep-learning/references/frameworks.md) defaults to JAX/NNX and justifies native Equinox/Diffrax/e3nn paths. | Scientific fitting, native e3nn equivariance and diffusion objective/gradient fixtures passed. Sequence training is executed; vision and larger domain architectures retain documented recipe/application limits. Tabular prediction is excluded. |
| R4: LLM research | [LLM guidance](../../skills/deep-learning/references/llm.md) identifies compatible native Tunix loading/conversion, masks, SFT/DPO, frozen reference state, selected LoRA/trainable state and Qwix precision paths, with optional MaxText scale references. | `llm-token-masks` passed causal shifting, valid completion counts, objective checks, reference immutability and selected adapter updates. It is a math/state fixture, not a tokenizer, arbitrary Hugging Face v5 Flax loader, real checkpoint, quantization or hardware run. |
| R5: evaluation and neural records | [Protocol](../../skills/evaluate-deep-learning/references/protocol.md), [domain checks](../../skills/evaluate-deep-learning/references/domain-checks.md) and [experiment records](../../skills/evaluate-deep-learning/references/experiments.md) specify common units, masks/reductions, held-out roles, budget curves, per-seed results, uncertainty distinctions and neural-run metadata. | `paired-evaluation` passed independent reductions, padding invariance, shared units and retained per-seed records. Application evidence covers protocols; no real-data calibration, statistical coverage or universal confidence-interval claim. Neural runs require no posterior artifacts. |
| R6: JAX execution | [Profiling](../../skills/optimize-jax/references/profiling.md), [sharding](../../skills/optimize-jax/references/sharding.md) and [inference](../../skills/optimize-jax/references/inference.md) cover signatures, trace/lower/compile boundaries, completed calls, natural host requests, memory/rematerialization, placement and independent cache parity. | `jax-timing`, `cached-decode` and selected optional `jax-placement` passed. Timing is a local boundary observation; cache is a tiny single-head fixture; placement is one-device CPU. No measured production bottleneck, memory saving, speedup, multihost or accelerator claim. |
| R7: integration and boundaries | Conditional handoffs retain evaluation, execution, data QA/testing and real posterior ownership. The sole [Bayesian](../../skills/bayesian-workflow/SKILL.md) edit removes standalone `JAX, ` from its description. [Bayesian tracking](../../skills/track-model-experiments/SKILL.md) is unchanged. Installer discovers the three skills without registration or invented handoff dependencies. | Exact full-file Bayesian delta, six private-home dry-run links, matched routing catalogs/read events and unchanged agents/commands/adapters/ledger verified. Neural experiments do not inherit posterior bookkeeping or Bayesian precision rules. |
| R8: originals and attribution | [NOTICE](../../NOTICE), [CLAUDE.md](../../CLAUDE.md) and [README](../../README.md) agree on 19 originals in this branch. The three skills are original MIT guidance; Orchestra inspiration is acknowledged, and references link primary API/framework sources with their stated limits. | Fresh provenance, exact original-name sets, single-line CLAUDE inventory and README Mine rows/credits checked. No third-party skill manual was vendored or copied as original guidance. Concurrent additions outside this checkout are not part of this count. |
| Acceptance: execution/application/routing | Ten canonical examples run unchanged on the frozen 39-pin profile; earlier manually scored D/E/S cohorts and two matched catalog cohorts remain archived with conditions and source identities. | Fresh gates below passed. Application outputs are unexecuted delivered proposals, while canonical fixture stdout is runtime evidence. Controller reviews and plan/branch completion remain pending below. |

## Initial Task 6 snapshot: navigation, inventory and source identity

| Skill | Main body words | Description characters | Markdown sources |
|---|---:|---:|---:|
| deep-learning | 1,378 | 299 | 9 |
| evaluate-deep-learning | 1,166 | 298 | 4 |
| optimize-jax | 1,251 | 270 | 4 |

Body counts use whitespace-separated words after the YAML closing delimiter.
Description counts use the parsed YAML value with surrounding whitespace stripped.
The deep-learning folded YAML value retains a trailing newline: its historical
unstripped count is 300, while this audit reports 299. Its source hash is unchanged.
None of these entry points declares `context`, `model` or `effort` metadata.

Fresh source navigation verifies domains absent from description keywords:
deep-learning's main table links neural ODE/CDE work to scientific guidance;
evaluate-deep-learning's main table links time-series, image, geometric and LLM
checks to its domain reference; optimize-jax covers non-learning JAX signature
and execution work without requiring a neural training task. The existing RD,
RE and RS read-event/application evidence tests on-demand reference retrieval.
This task's link inspection is a static navigation check, not another agent trial.

At the initial Task 6 gate there were 17 authored Markdown sources, exactly
matching the frozen candidate guidance snapshots. The later GPU clarification
below changes five prose sources while preserving those archived snapshots.
Fresh checks validated all 118 local links in those sources
and the four preceding durable records, including file/line target bounds.
The integration record's own 51 local endpoints and line bounds also passed.
The three added `skills/*/SKILL.md` files are the only added entry points against
the whole-branch BASE. Canonical agents, commands, generated adapters, Bayesian
tracking, and shared fence/preamble helpers have no branch changes for this plan.

The full Bayesian file is exactly its BASE bytes with the unique replacement
`Pyro, JAX, BlackJAX, ArviZ, InferenceData` →
`Pyro, BlackJAX, ArviZ, InferenceData`, five bytes shorter. NumPyro (JAX),
BlackJAX, MCMC/NUTS/posterior terms, body, license, effort and all other metadata
remain intact. Current full SHA-256:
`2adf320e9184e733e5b5ae2f321cf2f7b6e485b765f3fd3c07c16a8e21b341ff`.
No MCMC execution is implied by this metadata-only gate.

Freshly reconciled source SHA-256 values:

| Source, relative to `skills/` | SHA-256 |
|---|---|
| `deep-learning/SKILL.md` | `ece0ac27eaf8b9ca8de149fc27ec408d6ab975e58ba9cfa132c47d765b14fdbf` |
| `deep-learning/references/frameworks.md` | `86bf7d4be22899bffc75aeaad33ee5986a4b572c6cb924425214998a1097dc47` |
| `deep-learning/references/generative.md` | `6f9cf63e3bd2d737c735e5ea1ac494eb1e6705ca1aa681b937f1c849edf9ff3f` |
| `deep-learning/references/geometric.md` | `ea30fbaab10b8cb9cce0882cd3bf1152bc5434225deac92d1095ee302e710e7d` |
| `deep-learning/references/llm.md` | `4d5e193c9376d05af7ac402cd7994df450f74c3c5c0275cd567523d30e1659f2` |
| `deep-learning/references/scientific.md` | `aeecdd5ea8bdb1b44652918586564900091465b68524b61ca303d18e0e643b97` |
| `deep-learning/references/sequences.md` | `1d5a46913ffb1ff1754efb4defdc4b03d2abe4a4374dac9ba27833b4799af4e4` |
| `deep-learning/references/training.md` | `dc2e7ccc657d6b438796a0f44b38e06648564e7ff8fdd6d38c58bca835d80970` |
| `deep-learning/references/vision.md` | `4fb0d0c790f5c92146fbfc5967f2be0ab1215476e7f1b6e36505ac197eabefef` |
| `evaluate-deep-learning/SKILL.md` | `db75cc39c357cd80340d39d7255bcb9c53602b6bbb0c5af9789169b5a82607c8` |
| `evaluate-deep-learning/references/domain-checks.md` | `984209d2ee4b18b926fc722b24baec7cde470058f59fa7a64916a887e305156c` |
| `evaluate-deep-learning/references/experiments.md` | `1254907bbaf6cc731e22a92b15cc4e7b17ce32f7f3486e8b4f472e582da24518` |
| `evaluate-deep-learning/references/protocol.md` | `65d69194053e9183276a39a3e30dd1ee372da2bf3537a0b63306c10c0f0d672f` |
| `optimize-jax/SKILL.md` | `e177b588bf9cbb73654b16dc594a294a782f098cbb4f3226856e1f42835a4200` |
| `optimize-jax/references/profiling.md` | `e18a541db2b1db44c016ebc0ac0d330f0e475f52e094a36d4d013ec3bc3cdc9d` |
| `optimize-jax/references/sharding.md` | `6d963f477d1b64d1974780678a1e21214c9ec6727c54ada6da9ed72e4e1b1275` |
| `optimize-jax/references/inference.md` | `7d2baaedf008a42ae50477e520022207a3991ad018c2855aa2d3c19f10d3c1d6` |

## Fresh final gates

All following commands ran in the execution checkout on 2026-10-04 UTC. The
first five use the repository root; the focused tests use `build/`. Every exit
was inspected. No root-wide pytest, unrelated citation/PDF suite, new parsing
exemption, tolerance widening or hidden example preamble was used.

| Working directory | Command | Exit and actual output |
|---|---|---|
| root | `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` | 0; empty stdout/stderr |
| root | `uv run --python 3.13 python build/check_provenance.py` | 0; empty stdout/stderr |
| root | `uv run --python 3.13 python build/check_snippets.py skills/` | 0; only the five existing advisories below |
| root | `uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check` | 0; empty stdout/stderr, no adapter drift |
| root | `JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/deep-learning/ skills/evaluate-deep-learning/ skills/optimize-jax/` | 0; all ten named examples PASS; `Selected/executed 10 CPU examples; passed 10.` |
| build/ | `uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py test_check_jax_examples.py` | 0; `99 passed in 2.86s`, no warnings |
| root | `git diff --check 3abece14e1ff6a129c44e9ffccc46691e93856a9 HEAD` | 0; empty output |
| root | `git diff --check` | 0; empty output; checked again before staging |
| root | `git diff --cached --check` | 0; empty output; only the integration record staged |

The actual focused total is 62 runtime-support/dependency tests plus 37 runner
tests. The plan's original eight-runner-test estimate was superseded by the
approved Task 1 malformed-fence rejection regressions; the actual 99-test result
is retained rather than repeating that estimate.

The global parse check's complete advisory output:

```text
WARN skills/bayesian-workflow/SKILL.md:170: not executed: slow: 4 chains x 2000 draws, minutes -- not a pre-commit gate
WARN skills/bayesian-workflow/SKILL.md:184: not executed: blackjax is optional (SKILL.md:52), not a declared dependency
WARN skills/bayesian-workflow/references/model-criticism.md:157: not executed: slow: 200 SBC replicates x 600 draws -- not a pre-commit gate
WARN skills/bayesian-workflow/references/state-space.md:76: not executed: HANDOFF SKETCH; dynamax is not a bayesian-workflow dependency
WARN skills/develop-testing-strategy/references/model-tests.md:83: not parsed or executed: replacement lines for the loop body above; the indentation shows where they substitute
```

These advisory sketches/optional/slow Bayesian checks are not execution evidence
for this plan. All selected JAX CPU blocks were executed separately below.

## CPU profile, exact blocks and captured stdout

The unchanged [input profile](32-jax-cpu.in) has SHA-256
`b464a7e53420e93a7d11dd209ed47238674d951f64b74292a53faa1c4f1b7ccd`;
the unchanged [resolved profile](32-jax-cpu.txt) has SHA-256
`c8bd73640ca1d2cd1f86a211554e9ceac244054d629370a931738a8b5b10258c`.
All 39 exact installed pins were reconciled to that resolved file. The only
additional environment distributions were bootstrap `pip==25.2` and
`wheel==0.45.1`; the profile was not refreshed.

Actual environment: Python 3.13.8, `macOS-26.6.2-arm64-arm-64bit-Mach-O`,
`JAX_PLATFORMS=cpu`, backend `cpu`, one device `cpu:0`, device kind `cpu`.
The timing fixture reports float32, x64 false, default matmul precision `None`,
and persistent cache false.

| Package | Actual version |
|---|---|
| `jax` | `0.11.2` |
| `jaxlib` | `0.11.2` |
| `flax` | `0.12.10` |
| `optax` | `0.2.8` |
| `orbax-checkpoint` | `0.12.6` |
| `equinox` | `0.13.8` |
| `diffrax` | `0.7.2` |
| `e3nn-jax` | `0.21.0` |
| `numpy` | `2.5.3` |

The canonical runner prints PASS rather than successful child stdout. To retain
the outputs below, a temporary audit helper additionally used the existing
`collect_examples` implementation to execute each unchanged `example.code` in a
fresh temporary child script, under the same Python/profile and CPU environment.
It prepended no code, captured stdout/stderr and required every exit to be zero.
Command from root:
`JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python /private/tmp/task6-jax-cpu-capture.py`.
Exit 0; capture interval `2026-10-04T04:00:45.653009+00:00` through
`2026-10-04T04:00:55.950479+00:00`. This is separate from the required runner pass.
Nine required IDs and the selected optional placement ID were present,
executed and passed in both runs; all ten captured child stderrs were empty.

| ID | Canonical code start | Code SHA-256 | Exit |
|---|---|---|---:|
| `generative-objectives` | [deep-learning/references/generative.md:58](../../skills/deep-learning/references/generative.md:58) | `f5551e6acefa5e89786a4beb1e7027e80aaab485d3dd2c9016b0bfef921174d4` | 0 |
| `geometric-equivariance` | [deep-learning/references/geometric.md:63](../../skills/deep-learning/references/geometric.md:63) | `e151b0960af09a23427229cf699ca4ce964d84df9ad2296eaa49f1fbc4849bcc` | 0 |
| `llm-token-masks` | [deep-learning/references/llm.md:126](../../skills/deep-learning/references/llm.md:126) | `0048357bd03ff8992c163b6f6aa4cdefc5e0d1a4e57aa371811aa9eb8842dc9d` | 0 |
| `scientific-solver` | [deep-learning/references/scientific.md:76](../../skills/deep-learning/references/scientific.md:76) | `56ff0fd597a64d27f367911fa6dc5f612b54371f852a13ca752b24460e48fb05` | 0 |
| `nnx-sequence-training` | [deep-learning/references/training.md:73](../../skills/deep-learning/references/training.md:73) | `e3a952f9e33f3e9f0d7f22dfb37ceb4e1be4a80543af5de38f14d747c746f977` | 0 |
| `nnx-checkpoint-resume` | [deep-learning/references/training.md:214](../../skills/deep-learning/references/training.md:214) | `d5b45ea5548136a824c7e07ff3a3741aac31f47d8702276661ec6e3b4aefe119` | 0 |
| `paired-evaluation` | [evaluate-deep-learning/references/protocol.md:116](../../skills/evaluate-deep-learning/references/protocol.md:116) | `785dfa1c6400030bc26a3dc44d56f3966a751015d82e3fb3ea4e796eabc5c1dd` | 0 |
| `cached-decode` | [optimize-jax/references/inference.md:46](../../skills/optimize-jax/references/inference.md:46) | `9523992adaa3c0bfaac745b36e62b5a9174241210618a08c84cf1087c4278c82` | 0 |
| `jax-timing` | [optimize-jax/references/profiling.md:140](../../skills/optimize-jax/references/profiling.md:140) | `bf7b93beb55376120ad36d7653875a253fc8d64e630b06daebd8948f51188123` | 0 |
| `jax-placement` | [optimize-jax/references/sharding.md:35](../../skills/optimize-jax/references/sharding.md:35) | `2745fac537475671c467784920f7e73ad84478dbd19b986f002e57b02baa9fb0` | 0 |

Verbatim captured stdout, one child per block:

`generative-objectives`:

```text
diffusion noise objective: independent limit and finite analytic-gradient checks pass
```

`geometric-equivariance`:

```text
native e3nn: nontrivial scalar/vector, rotations, inversion, permutation and gradients pass
```

`llm-token-masks`:

```text
LLM math: causal shift, completion counts, SFT/DPO, immutable reference and selected LoRA updates pass
```

`scientific-solver`:

```text
rate -0.699967; fit 0.013728 -> 0.000000; held-out observed units 2, loss 0.000000
```

`nnx-sequence-training`:

```text
train 0.896428 -> 0.000632; validation 0.002119
```

`nnx-checkpoint-resume`:

```text
recovery: next loss, model, Adam/schedule, step, RNG and cursor agree
```

`paired-evaluation`:

```text
paired-evaluation: valid reductions, padding invariance, shared units, per-seed records passed
```

`cached-decode`:

```text
{"atol": 2e-05, "backend": "cpu", "capacity": 8, "dtype": "float32", "eos_tokens": [6], "fixed_key_sample": [4, 1, 4], "greedy_padding_cases": 60, "jax": "0.11.2", "logit_checks": 129, "max_reference_error": 2.9802322387695312e-08, "rejected_requests": 9, "rtol": 2e-05, "scope": "tiny single-head cache/math fixture", "vocabulary": 9, "width": 6}
```

`jax-timing`:

```text
{"backend": "cpu", "checksum": 0.015169486403465271, "compile_or_load_ms": 9.91337513551116, "device_kinds": ["cpu"], "devices": ["cpu:0"], "dtype": "float32", "fenced_fetch_consume_ms": 0.032916199415922165, "fenced_model_ms": 0.0216667540371418, "fenced_placement_ms": 0.032667070627212524, "first_aot": {"completed_call_ms": 0.3553749993443489, "remaining_wait_ms": 0.24187518283724785, "submit_ms": 0.11349981650710106}, "host_result_request_ms": 0.14679180458188057, "jax": "0.11.2", "jaxlib": "0.11.2", "lower_ms": 0.6753341294825077, "matmul_precision": "None", "max_reference_error": 5.960464477539063e-08, "numpy": "2.5.3", "output_width": 8, "persistent_cache": false, "platform": "macOS-26.6.2-arm64-arm-64bit-Mach-O", "python": "3.13.8", "trace_ms": 0.2376250922679901, "visits": [{"completed_call_ms": 23.288791067898273, "length": 7, "remaining_wait_ms": 0.38008298724889755, "submit_ms": 22.908708080649376}, {"completed_call_ms": 12.190499808639288, "length": 13, "remaining_wait_ms": 0.24908315390348434, "submit_ms": 11.941416654735804}, {"completed_call_ms": 0.029458198696374893, "length": 7, "remaining_wait_ms": 0.01454213634133339, "submit_ms": 0.014916062355041504}], "warm_median_ms": 0.004749977961182594, "warm_p95_ms": 0.021037436090409756, "warm_repeats": 20, "width": 16, "x64": false}
```

`jax-placement`:

```text
{"scope": "one-device CPU placement only", "jax": "0.11.2", "mesh_shape": {"data": 1}, "global_shape": [6, 4], "sharding": "NamedSharding(mesh=Mesh('data': 1, axis_types=(Auto,)), spec=P('data', None), memory_kind=device)"}
```

Interpretation: the sequence fixture learns and retains a small validation
result; the recovery fixture verifies complete next-update parity. The
scientific fixture fits a scalar rate with two held-out observed units, rather
than proving a realistic solver/model's generalization. The native e3nn check
covers nontrivial scalar/vector features, rotation, inversion, permutation and
finite gradients. The diffusion check has independent limiting/gradient oracles.
LLM math checks and paired evaluation exercise their stated tiny contracts.

The cache fixture's 129 logit comparisons, 60 greedy/padding cases, nine rejected
requests, fixed-key replay and EOS check use capacity 8, width 6, vocabulary 9
and the existing 2e-5 tolerances. Its maximum error is
`2.9802322387695312e-08`. It does not prove multi-layer/RoPE/GQA cache logic,
tokenizer/chat-template/checkpoint conversion, quantization or backend-wide
argmax equality near ties. The timing stdout separates signature visits,
trace/lower/compile-or-load, warm completed calls, a natural host-consumed
request and fenced stages; these are local observations, not pure compile or
kernel decompositions. CPU transfers may share memory, and twenty serialized
warm observations do not establish a production tail distribution or speedup.
One-device placement does not exercise distributed sharding. No large model,
dataset, real checkpoint, GPU/TPU, multihost, Tunix/Qwix/MaxText or production
profile run occurred in this integration task.

## Earlier application and retrieval evidence

The complete durable records and native manual score reports preserve both
successes and omissions. Historical external cohorts stay separate. Native
trials use fresh built-in inherited default agents with `fork_turns=none`;
exact model/effort identifiers were unavailable and no provider alias is
invented. The prior external-launch authorization rejection remains a recorded
deviation, not a claim that an external service ran. This task launched no
agents or model service.

| Evidence | Matched native controls → candidates | Separate retrieval |
|---|---|---|
| [D control](32-jax-trials/native/D-native-control-scoring.md) / [candidate](32-jax-trials/native/D-native-candidate-scoring.md) | 77/94 → 94/94 | RD 8/8 |
| [E control](32-jax-trials/native/E-native-control-scoring.md) / [candidate](32-jax-trials/native/E-native-candidate-scoring.md) | 65/66 → 66/66 | RE 8/8 |
| [S control](32-jax-trials/native/S-native-control-scoring.md) / [candidate](32-jax-trials/native/S-native-candidate-scoring.md) | 61/70 → 70/70 | RS 7/8 |

D's five D1 controls total 46/60 versus candidate 60/60; D2 remains 12/12
in both; D3's valid plain-JAX 7/10 control is distinguished from native e3nn
candidate coverage 10/10, without inventing a mathematical failure; D4's
successful legacy Flax 12/12 control is preserved alongside the Tunix 12/12
candidate plan. Native D controls followed refined draft authorship with
guidance withheld; only the historical controls were preauthoring.

E1 totals 50/50 in both cohorts, with the exact worked numeric scenario already
supplied. This supports adherence to supplied guidance, not an unseen-task
generalization or improvement claim. E2 is 8/8 in both; E3's predictive-uncertainty
field omission is partial 7/8 versus 8/8, without a false API defect or
uncertainty-conflation claim. RE is a separate new retrieval rubric.

S control subtotals are 44/50, 10/12 and 7/8; candidate subtotals are 50/50,
12/12 and 8/8. Three S1 controls omitted delivered numerical reference assertions
despite valid diagnostic/timing guidance. S2 retained successful cache/full-prefix
and greedy parity but omitted explicit seeded-sampling/prompt-padding checks.
S3 omitted a cause-specific before/after evidence harness. These coverage gaps
are not executed numerical failures or invented static defects. RS's scope-summary
omission remains a partial fourth item: vector `[2,2,2,1]`, 7/8. The frozen source
already states its limits, and the accepted review closure required no correction.

RD/RE/RS have no matched retrieval control or new pass cutoff. The recorded
application code was not executed; successful canonical fixtures above are
separate evidence. Scores describe manually inspected delivered coverage in
small cohorts, not general reliability, actual auto-loading or production runs.
Fresh integrity assertions match all simple native archive payload hashes:
D control 45, D candidate-r2 61, E control 42, E candidate 52, S control 42,
S candidate 52. File counts are payload entries, not sample counts or semantic
grades. Hash/condition checks cannot independently prove hidden reads/dispatch.

## Matched catalog routing and private-source limits

The [baseline manual report](32-jax-trials/native/routing/baseline-manual-scoring.portable.md)
and [candidate manual report](32-jax-trials/native/routing/candidate-manual-scoring.portable.md)
record 30 fresh samples each: five repetitions of each of six families. All 30
in each are manually judged correct with the posterior boundary preserved.
C1 training chooses deep-learning, C2 checkpoint comparison chooses
evaluate-deep-learning, C3 non-learning execution and C6 generation choose
optimize-jax, and C4 NumPyro/NUTS plus C5 BlackJAX posterior work choose
bayesian-workflow. Optional process/data support does not displace the primary.

Fresh audit reconciled all sixty unique fresh default/fork-none identities,
prompt hashes, declared conditions, manual categories and recorded body-read
hashes. The two immutable 138-entry catalogs differ only in the exact Bayesian
description edit. Baseline has 52 actual body-read events, candidate 44; no
Bayesian body is read for C1, C2, C3 or C6. Baseline already routes correctly,
so the edit demonstrates no measured reduction in over-triggering.

Both [baseline](32-jax-trials/native/routing/baseline-archive-manifest.json) and
[candidate](32-jax-trials/native/routing/candidate-archive-manifest.json) manifests
reference 191 payload entries whose bytes/hashes were freshly checked.
Candidate comprises 190 newly archived payload files plus one reused Task 5
brief; its manifest is additional bookkeeping, not a 191st new payload.
These checks do not re-run the private 276-body snapshot audit already accepted
by Task 5 review or automate semantic grading.

This is declared catalog-selection/retrieval simulation; real runtime
auto-loading was not observed and resident global guidance may remain available.
Installed third-party full bodies stay private. The distinct advertised system
skill-creator uses a disambiguated read ID. The dangling advertised
recommend-causal-design body was recovered privately from Git commit
`b2cfe552706eb0fc23f53f274305a419c8744b23`, SHA-256
`65be2d92f9240780d1e73dc1a476508a0204aa7788963fe95f0db6c157502e5a`,
without repairing another checkout. Original response/notes, setup-path failures,
paging/truncation recoveries and same-trial rereads remain archived; no recovery
or failed attempt becomes another sample and none replaces a sample.

## Installer discovery

An empty private destination was created with `task_jax_install_home=$(mktemp -d)`:
`/var/folders/3m/6f8zc0l14dn8yz2x8yy2_3mw0000gn/T/tmp.Muw1No83v8`.
`find DESTINATION -mindepth 1 -print` exited 0 with empty output before the run.
From root, the actual command was:

```bash
uv run --python 3.13 python install.py all --home /var/folders/3m/6f8zc0l14dn8yz2x8yy2_3mw0000gn/T/tmp.Muw1No83v8 --no-companions --dry-run --skill deep-learning --skill evaluate-deep-learning --skill optimize-jax
```

Exit 0; complete stdout:

```text
would link /Users/lowell/.codex/worktrees/jax-deep-learning-skills/agent-skills/skills/deep-learning -> /var/folders/3m/6f8zc0l14dn8yz2x8yy2_3mw0000gn/T/tmp.Muw1No83v8/.claude/skills/deep-learning
would link /Users/lowell/.codex/worktrees/jax-deep-learning-skills/agent-skills/skills/evaluate-deep-learning -> /var/folders/3m/6f8zc0l14dn8yz2x8yy2_3mw0000gn/T/tmp.Muw1No83v8/.claude/skills/evaluate-deep-learning
would link /Users/lowell/.codex/worktrees/jax-deep-learning-skills/agent-skills/skills/optimize-jax -> /var/folders/3m/6f8zc0l14dn8yz2x8yy2_3mw0000gn/T/tmp.Muw1No83v8/.claude/skills/optimize-jax
would link /Users/lowell/.codex/worktrees/jax-deep-learning-skills/agent-skills/skills/deep-learning -> /var/folders/3m/6f8zc0l14dn8yz2x8yy2_3mw0000gn/T/tmp.Muw1No83v8/.agents/skills/deep-learning
would link /Users/lowell/.codex/worktrees/jax-deep-learning-skills/agent-skills/skills/evaluate-deep-learning -> /var/folders/3m/6f8zc0l14dn8yz2x8yy2_3mw0000gn/T/tmp.Muw1No83v8/.agents/skills/evaluate-deep-learning
would link /Users/lowell/.codex/worktrees/jax-deep-learning-skills/agent-skills/skills/optimize-jax -> /var/folders/3m/6f8zc0l14dn8yz2x8yy2_3mw0000gn/T/tmp.Muw1No83v8/.agents/skills/optimize-jax
```

These are exactly three Claude and three shared Codex/Gemini destinations,
all targeting this checkout's corresponding skills. No companion or extra
dependency appeared. No registration, runtime-adapter change or global
installation was needed. `rmdir` of that still-empty private destination exited
0 after output inspection; no user runtime setting or home variable was changed.

## Review and completion boundary

Task 6 implementer gates and the scoped integration-record self-review are
complete at this initial commit. Root owns the following subsequent gates and
will record their actual outcomes; this record does not invent approval or a
reviewed SHA:

| Gate | Initial disposition |
|---|---|
| Fresh Task 6 task review against scoped BASE | Approved by a fresh built-in full-form reviewer for `094d474..6ec9c90`; no Critical/Important/actionable Minor issue. It compared saved gate/capture/audit artifacts with the committed record; later GPU prose is covered by whole-branch review. |
| Fresh final whole-branch native review against whole-branch BASE | Pending controller dispatch |
| Different-model-family read-only second opinion | Same-family exception: this runtime is Codex; another Codex opinion is not a different-family review. Use the required fresh native whole-branch reviewer; no external fallback is authorized. |
| Actionable findings, affected checks, completion/retirement and moved links | Controller resolves before claiming full plan completion |
| Backlog health and integration/worktree cleanup | Controller performs read-only triage and obtains the owner's concrete integration choice; DL/NLP methodology-template completion is unrelated |

No plan/spec retirement, completion ticks, Bayesian ledger generalization,
methodology-template backlog change, publish, merge or unrelated cleanup occurred
in this task. Review findings that alter frozen source require coordinated
reverification rather than silent reuse of earlier application identities.

## Owner clarification: GPU as the usual implementation target

On 2026-10-04 the owner clarified that most skill uses write GPU code. New neural
training/inference now explicitly target GPUs unless the project or user names
another device. Evaluation follows the actual model target. The original CPU
profile remains a portable correctness gate, not a deployment default.

Five documentation sources were clarified: the three main skill bodies,
[frameworks](../../skills/deep-learning/references/frameworks.md#gpu-target-and-local-verification)
and [inference](../../skills/optimize-jax/references/inference.md#gpu-generation-loop).
They cover accelerator environment/device checks, no silent CPU fallback,
resident state/compiled training and decoding, deliberate host logging or
streaming, hardware-specific precision and a target-GPU smoke/measurement gate.
Current primary [JAX installation](https://docs.jax.dev/en/latest/installation.html)
and [GPU performance](https://docs.jax.dev/en/latest/gpu_performance_tips.html)
sources were checked. No GPU was available or exercised in this authoring gate;
GPU execution and performance remain explicitly pending on the target hardware.

A read-only built-in Codex wording audit found no remaining required gap for
this clarification. It inspected training/LLM/generative and evaluation guidance;
it did not execute GPU code or create a new scored application cohort.
Earlier application/retrieval scores apply to their immutable source snapshots,
not automatically to the new prose. All ten executable code hashes, all three
descriptions/frontmatter and the profile are unchanged from the fresh Task 6
runtime evidence. Their checks were not gratuitously repeated for prose edits.

Post-edit frontmatter, provenance and global parse commands above each exited 0;
parse retained the same five existing advisories. Whitespace and all eighteen
local links across the five changed sources passed. Main body word counts are
now 1,415 / 1,203 / 1,305. No new entry point, dependency edge, executable block,
model pin or default precision flag was introduced.

Changed prose source SHA-256 values after clarification:

| Source, relative to `skills/` | SHA-256 |
|---|---|
| `deep-learning/SKILL.md` | `08f202c52f05043fe145333adb6c7f5b95ba0ba9d7bdd510d5acf98310606b50` |
| `deep-learning/references/frameworks.md` | `7cc48adcd90ef3aa86b45b346827230167ab7267d9e8ef93422d8368e743654f` |
| `evaluate-deep-learning/SKILL.md` | `c7b28dac4fd79a1709b6b2cc2864421307d412e152c70d31340d0cd8e90411c7` |
| `optimize-jax/SKILL.md` | `5e9e8c7ababf21e98c6cd8ca0da95405841e6e33d0517572cd9f07c374f01bcc` |
| `optimize-jax/references/inference.md` | `abc14e87ffa1e7f0c20b8f42fb33c8cfa25cdabd21fe37476a946aabbd48ce0a` |

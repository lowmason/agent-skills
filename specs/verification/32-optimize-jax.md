# optimize-jax verification record

Status: VERIFIED — controller application/retrieval gate closed; frozen CPU
evidence reused by verified identity, with fresh final checks recorded below. Task 4 baseline:
`385c350d191c7c16c304f035fc7156899c8d50c2`.

## Preconditions and control evidence

The entire approved Task 4 brief, dispatch/context, CLAUDE.md, NOTICE,
writing-skills, clean-code, develop-testing-strategy and verification-before-
completion were read before authoring. This is the existing linked managed
worktree; no new checkout, installer, model service or generated adapter is
needed. Existing CPU runner contract tests passed: 37 in 0.42s, exit 0.
The unchanged Task 2 profile is `32-jax-cpu.in` -> `32-jax-cpu.txt`.

[Historical external control scoring](32-jax-trials/S-control-scoring.md) and
[closed native control scoring](32-jax-trials/native/S-native-control-scoring.md)
are separate cohorts. All seven native controls preceded Task 4 source authoring,
were fully read/manually scored and metadata-audited: 61/70, comprising five S1
10,8,10,8,8 = 44/50, S2 10/12 and S3 7/8. The corrected subtotal changes no
individual score. No pass threshold, static defect or observed numerical failure
is inferred; authorized nonexecution is not a penalty.

Retain all native S1 synchronization/compile/warm/end-to-end, signature/transfer,
conditional-profile and workload/hardware successes. Controls 1/3 deliver actual
independent NumPy or original-unpadded output comparisons; controls 2/4/5 give
correct reminders but omit delivered comparisons. Native S2 already delivers
real K/V attention, independent full-prefix/per-step logits, exact greedy parity,
positions/masks/capacity/state, zero/one/final-slot/invalid requests and bounded
termination. Its gaps are stochastic fixed-key generation and changed prompt
padding; parameter initialization and dirty future slots are different checks.
Native S3 retains correct scalar/static/dynamic reasoning and independent
discrete-Euler assertions without learning/Bayesian requirements. Its partial
item is cause-specific original/fixed compile evidence, not an API failure.
Historical timing/reference defects are not transferred to native controls.

This reference/technique skill uses a positive reproduction/evidence contract
and concrete check slots for observed omissions. Reusable guidance carries no
control-history narrative or invented discipline prohibition. At the stable-draft
checkpoint, five fresh S1 wording/applications plus S2/S3 and the separately
predeclared four-item/eight-point RS retrieval application were pending. The
closed gate and its actual source-read conditions are recorded below.

## Numerical strategy (persisted before code)

Scope: small, original synthetic JAX/NumPy CPU fixtures in canonical Markdown,
executed by the existing isolated-subprocess runner, without a preamble. No
training model, posterior artifact, real checkpoint, dataset download, multi-host
cluster, accelerator profiler or production hosting is required. These are
invariant-first numerical fixtures, not library/pipeline feature development;
no artificial numerical RED failure will be manufactured.

| Fixture | Invariant | Cheapest falsifying check |
|---|---|---|
| jax-timing | Correct float32 pointwise model returns full token/pooled output tree | Independent NumPy forward allclose across several lengths, outside timers |
| jax-timing | Input work is ready before resident timers and every output leaf completes | Full-tree barriers around first encounter, AOT execution and each warm repetition |
| jax-timing | First encounter, trace/lower, compile/cache load, first AOT execution, warm resident and host-result request have distinct boundaries | Isolated function identities; no false pure-kernel/pure-compile attribution; print actual times/environment, no speed assertion |
| jax-timing | Request timer includes host preprocessing, placement, complete execution, host fetch/consumption | Separate natural request and fenced transfer attribution; CPU movement caveat |
| jax-placement | Named mesh/spec placement preserves output and logical shape | One actual CPU device, named sharding jit plus NumPy allclose; explicitly no multi-host proof |
| cached-decode | Cache contains actual projected keys/values for a contiguous valid prefix | Independent NumPy causal full-prefix math at every consumed prompt/generated position |
| cached-decode | Absolute positions, cursor, masks and capacity prevent future/padding influence and out-of-range writes | Multiple lengths and left/right/interspersed padding; dirty future slots; one/final-capacity cases; host guards reject malformed masks/IDs/overflow before jit |
| cached-decode | Prefill selects first new token from final prompt logits; decode extends one token at a time | Every emitted greedy token exactly equals independent full-prefix argmax; every prediction-logit vector allclose |
| cached-decode | Bounded generation handles zero, short, empty and EOS | Reject empty effective prompt (BOS must be supplied); zero-new unchanged prefix; selected first EOS stops after its cache write; requested count remains a hard bound |
| cached-decode | Sampling takes its own explicit key and reproduces its result | Two actual categorical generations from equal keys are bit-identical; distinct parameter-init seed is not this test |

Tolerances are float32-derived (`rtol=2e-5`, `atol=2e-5`) for small matmul,
softmax and activation math, recorded with maximal observed differences. Exact
checks apply to integer tokens, shapes, cursor/state counts and fixed-key replay.
No fixture asserts a tiny CPU implementation is faster. No optimizer/gradient
path is bundled; prose requires output/gradient/state parity when the changed
user path trains. Multi-host/checkpoint/hardware recipes remain sourced,
explicitly nonexecuted prerequisites.

Fast portable gate (no pytest marker needed; standalone CPU processes):

```bash
uv run --python 3.13 python build/check_snippets.py skills/optimize-jax/
JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/optimize-jax/
```

Before the checkpoint, run focused frontmatter/provenance/dependency/source
checks, inspect every command's successful exit before dependent mutations,
read the full scoped diff and preserve canonical source/profile hashes. The
controller owns candidate dispatch, scoring and archives. Stop NEEDS_CONTEXT
with the stable draft, without staging or committing.


## Stable-draft gates and actual environment (2026-10-03)

Interpreter/platform: Python 3.13.8, macOS-26.6.2-arm64-arm-64bit-Mach-O,
backend cpu, one cpu:0 device of kind cpu. Direct profile packages: jax/jaxlib
0.11.2, NumPy 2.5.3, Flax 0.12.10, Optax 0.2.8, Orbax-checkpoint 0.12.6,
Equinox 0.13.8, Diffrax 0.7.2 and e3nn-jax 0.21.0. The complete Task 2 input
and resolved profile were reused without edits or re-resolving the profile. Float32,
x64 disabled, default matmul precision (`None`); timing persistent cache disabled.

| Command/check (assigned checkout root unless specified) | Actual result |
|---|---|
| Before authoring, from build/: `uv run --python 3.13 --with pytest python -m pytest -q test_check_jax_examples.py` | Exit 0; 37 passed in 0.42s |
| `uv run --python 3.13 python build/check_snippets.py skills/optimize-jax/` | Exit 0; no output, first draft and strengthened-code parse |
| Exact CPU command above, first numerical run | Exit 0; cached-decode, jax-timing and jax-placement PASS; 3 selected/executed/passed |
| Exact CPU command above after strengthening AOT/cache-state assertions | Exit 0; all three canonical IDs PASS; 3 selected/executed/passed |
| `JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python /private/tmp/task4-capture.py` | Exit 0; exact canonical source extracted and rerun in isolated CPU subprocesses; complete JSON stdout captured, stderr empty for all three |
| `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` | Exit 0; no output |
| `uv run --python 3.13 python build/check_provenance.py` | Exit 0; no output |
| From build/: `uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies` | Exit 0; 1 passed, 61 deselected in 0.29s |
| `uv run --python 3.13 --with pyyaml python /private/tmp/task4-source-audit.py` | Exit 0; four-source layout, three CPU IDs, all five own relative links, 1251 body words/270 description chars, no pin/fork, 19 originals and unchanged profile hashes verified; rerun after prose/source self-review cleanup |

The capture helper runs the actual canonical Markdown source with the same
interpreter/environment and no Bayesian preamble. Its source hashes below match
the successful runner sources. It records stdout for this verification record;
it is temporary inspection tooling, not a shipped helper or new build interface.
No numerical failure, widened tolerance or exemption occurred. These are
invariant-first model/math fixtures; no artificial runtime RED is claimed.

### Timing evidence and limits

Actual captured workload: pointwise tanh projection, lengths 7/13/7, width 16->8,
float32, token and pooled output tree, 20 serialized warm AOT repetitions at
length 7; host-list-to-consumed-host-checksum request. Input/parameter readiness
and full-output barriers are explicit. First encounters preceded the AOT/warm
path. Import/device initialization, request queueing and concurrency are excluded.

| Captured boundary | Actual milliseconds |
|---|---:|
| First length-7 completed call | 27.2107501514256 |
| First length-13 completed call | 14.191749971359968 |
| Revisited length-7 completed call | 0.045416876673698425 |
| AOT trace | 0.26254216209053993 |
| AOT lower | 0.7127500139176846 |
| AOT compile-or-load | 11.916332878172398 |
| First AOT completed call | 0.45841559767723083 |
| Warm median (20 repeats) | 0.005292007699608803 |
| Warm p95 (20 repeats) | 0.025817030109465126 |
| Natural host-result request | 0.16366690397262573 |
| Deliberately fenced placement | 0.033250078558921814 |
| Deliberately fenced model | 0.020874664187431335 |
| Deliberately fenced fetch/consume | 0.032708048820495605 |

First-call/submit/remaining-wait boundaries are not pure compilation/kernel
measurements. Compile-or-load includes possible backend reuse/bookkeeping despite
disabled persistent cache. Fenced stages alter overlap and do not sum to a claimed
natural-request decomposition. CPU placement/fetch can share memory; none of
these values predicts accelerator transfer time. The small p95 is illustrative,
not a production tail estimate or speed comparison. No change was asserted to
be faster, and no actual-user bottleneck/profile/memory saving was measured.

NumPy reference comparisons on token/pooled outputs and AOT output passed;
maximum observed absolute difference `5.960464477539063e-08`, with rtol/atol
`2e-5`. Checksum `0.015169486403465271` establishes consumption only; it is not
the numerical-parity evidence.

### Cache and placement evidence

Cached-decode: capacity 8, width 6, vocabulary 9, float32. All 60 greedy/padding
request cases, 129 independent logit checks and 9 rejected requests/appends
passed. Effective prompt lengths 1/3/5/7/8 cover zero/one/short/final-capacity
requests. Unpadded, left, right and interspersed padding preserve valid-token
order/contiguous positions. Every consumed teacher prefix and every generation
prediction agrees with independently recomputed NumPy triangular attention;
generated tokens exactly equal full-prefix greedy tokens. Valid K/V slots also
agree with independent full-prefix projections after prefill and generation.
Dirty future slots check cache masking separately from prompt padding.

Fixed sampling-key actual categorical replay produced `[4, 1, 4]` identically
on repeated and changed-padding requests; parameter initialization is separately
seeded. Chosen EOS `[6]` stopped after one emitted-and-consumed token; cursor 2.
Maximum logit error `2.9802322387695312e-08`, rtol/atol `2e-5`. The wrapper rejects
empty effective prompt, malformed masks/valid IDs, negative/overflow counts and
an append after capacity before the private jitted write. BOS is explicit caller
input. No large checkpoint/tokenizer, multi-layer/RoPE/GQA/quantization model or
accelerator-generation correctness/performance is established.

Jax-placement: logical `(6, 4)` float32 output matches NumPy, mesh `data:1`, one
actual cpu:0 device, NamedSharding `P('data', None)` with Auto axis type. Input and
output placement, logical shape and one addressable shard pass. There is no
multi-host, collective, distributed optimizer/checkpoint or scaling proof.

## Stable source identities for controller application freeze

| File | SHA-256 |
|---|---|
| `skills/optimize-jax/SKILL.md` | `e177b588bf9cbb73654b16dc594a294a782f098cbb4f3226856e1f42835a4200` |
| `skills/optimize-jax/references/profiling.md` | `e18a541db2b1db44c016ebc0ac0d330f0e475f52e094a36d4d013ec3bc3cdc9d` |
| `skills/optimize-jax/references/sharding.md` | `6d963f477d1b64d1974780678a1e21214c9ec6727c54ada6da9ed72e4e1b1275` |
| `skills/optimize-jax/references/inference.md` | `7d2baaedf008a42ae50477e520022207a3991ad018c2855aa2d3c19f10d3c1d6` |
| `NOTICE` | `c8ba9f0bd47ae55c876daee0cd0bff52e148336075f7ace4fe69bfa614f711bf` |
| `CLAUDE.md` | `a369b5ff3c53e9feef5ae6911dc45e4e77ae8e3ae3c4d4dba3ed43842d13d152` |
| `README.md` | `cf4e274396d390bae0fbd788e255a9f66e825f2fdca933fb55b26c2f981cdc4f` |
| `specs/verification/32-jax-cpu.in` | `b464a7e53420e93a7d11dd209ed47238674d951f64b74292a53faa1c4f1b7ccd` |
| `specs/verification/32-jax-cpu.txt` | `c8bd73640ca1d2cd1f86a211554e9ceac244054d629370a931738a8b5b10258c` |

| Canonical CPU source | Location | Extracted-code SHA-256 |
|---|---|---|
| `cached-decode` | `skills/optimize-jax/references/inference.md:46` | `9523992adaa3c0bfaac745b36e62b5a9174241210618a08c84cf1087c4278c82` |
| `jax-timing` | `skills/optimize-jax/references/profiling.md:140` | `bf7b93beb55376120ad36d7653875a253fc8d64e630b06daebd8948f51188123` |
| `jax-placement` | `skills/optimize-jax/references/sharding.md:35` | `2745fac537475671c467784920f7e73ad84478dbd19b986f002e57b02baa9fb0` |

The full four-file guidance hashes define the supplied candidate context.
All three code hashes remain identical after the final prose-only cleanup;
their successful numerical/capture runs are reused on that verified identity.
Main body: 1251 whitespace-delimited words after frontmatter; description:
270 stripped characters. Bare whole-skill handoffs add no installer dependency.
The authoritative NOTICE block has 19 originals, agreeing with CLAUDE.md and
README. All prose/code is original and Orchestra inspiration is by reference to
scope only, finalized across the three originals. Existing Bayesian attribution,
ledger artifacts, source profile, agents/commands and generated adapters remain
outside this task.

## Primary-source verification and unresolved limits

Task-specific primary sources reviewed on 2026-10-03: JAX benchmarking, AOT,
JIT, persistent cache, profiling/annotations, transfer guard, default dtypes,
matmul precision, rematerialization, device memory, current /201/sharding and
multi-controller documentation; Flax NNX transforms; Orbax checkpoint/target
sharding restore; the original attention paper; Tunix native vanilla rollout,
models/loaders; current MaxText offline inference, conversion and JAX architecture.
Citations are beside the claims in the three references. Older/dead JAX URL probes
were followed to current /201/ and /501/ pages, not adopted as unresolved sources.
No primary-source prose/code/manual/paper payload was reproduced or bundled.
Unversioned documentation claims are separate from recorded pinned execution.

Tunix native rollout currently documents JAX/NNX prefill/decode, cache capacity,
EOS and sampling modes; its package/model/checkpoint is absent from this CPU
profile. Actual loader/sampler, tokenizer/checkpoint logits and model/device
compatibility require a separate run. Current MaxText offline inference assumes
a v6e-8 VM and selects the MaxText JAX model through its adapter with host
orchestration. Conversion/scan-format mapping and trusted original logits are
prerequisites, not proof from a loaded file. Neither engine, adapter, pretrained
checkpoint nor hardware recipe was installed/executed; no default PyTorch model
path, server/hosting workflow, cloud provisioning or large download was introduced.

All seven native control successes and their authorized nonexecution remain
intact. Candidate collection used fresh supplied-guidance contexts and complete
manual output/read auditing. RS has its own predeclared four-item/8 rubric,
without an inherited numerical control/decomposition/cutoff. The closed evidence
below establishes adherence, retrieval and artifact coverage; it does not
establish automatic discovery, unseen-problem generalization or cross-runtime
improvement.

## Closed native application and retrieval evidence

The controller supplied its closure after archiving the complete evidence at
commit `cfe0aeda81b6f95fecbca7e9697f7c90298abe39`. The finalizer read the complete
[129-line candidate scoring report](32-jax-trials/native/S-native-candidate-scoring.md),
the actual [metadata-audit stdout](32-jax-trials/native/S-candidate-metadata-audit.json),
all eight linked condition/read records, the complete RS response/notes and the
[new predeclared retrieval rubric](32-jax-trials/rubrics/native-retrieval-rubrics.md).
The conductor manually read all eight complete responses and notes, totaling
3,213 response lines; the finalizer preserves those closed grades and root's
independent RS adjudication.

| Cohort | Actual candidate score | Native control score | Disposition |
|---|---:|---:|---|
| Five S1 applications | 10,10,10,10,10 = 50/50 | 10,8,10,8,8 = 44/50 | All five deliver the original five items |
| S2 cache application | 12/12 | 10/12 | Six original items delivered, including actual stochastic and prompt-padding checks |
| S3 simulation application | 8/8 | 7/8 | Four original items delivered, including the cause-specific original/fixed compile-evidence harness |
| Matched S1–S3 | 70/70 | 61/70 | Descriptive artifact-coverage comparison, with no pass cutoff |
| Separate RS retrieval | 7/8, vector [2,2,2,1] | No matched control | New four-item rubric; partial scope summary, no pass cutoff |

Native contrary successes remain successes: all five S1 controls already delivered
correct timing/signature/transfer/profile/workload contracts; controls 1/3 already
delivered independent NumPy or original-unpadded output comparisons. The S1
six-point coverage difference concerns the other three omitted comparisons. S2
already had real K/V attention, independent per-step full-prefix/greedy parity,
mask/position/capacity/state guards and bounded termination; its two-point
coverage difference concerns stochastic generation and changed prompt padding.
S3 already had correct scalar reasoning, discrete numerical assertions and
non-learning scope; its one-point difference concerns the delivered cause-specific
original/fixed evidence harness. No observed numerical control failure is inferred.
The historical external cohort remains separate and supplies no cross-runtime
improvement comparison.

Actual conditions are preserved in [S1-1](32-jax-trials/native/S1-codex-candidate-1/conditions.json),
[S1-2](32-jax-trials/native/S1-codex-candidate-2/conditions.json),
[S1-3](32-jax-trials/native/S1-codex-candidate-3/conditions.json),
[S1-4](32-jax-trials/native/S1-codex-candidate-4/conditions.json),
[S1-5](32-jax-trials/native/S1-codex-candidate-5/conditions.json),
[S2](32-jax-trials/native/S2-codex-candidate-1/conditions.json),
[S3](32-jax-trials/native/S3-codex-candidate-1/conditions.json) and
[RS](32-jax-trials/native/RS-codex-candidate-1/conditions.json).
Each is a unique fresh built-in default Codex collaboration agent, fork:none,
with inherited exact model/effort identifiers unavailable. Full task/main guidance
was supplied through the first hash-recorded read; there is no observed automatic
skill loading. Ordinary catalog skills and read-only primary sources remained
available equally. At most two application children were active; no seat/retry
deviation or external-agent fallback is recorded.

The actual [S1-1 read events](32-jax-trials/native/S1-codex-candidate-1/read-events.jsonl),
[S1-2](32-jax-trials/native/S1-codex-candidate-2/read-events.jsonl),
[S1-3](32-jax-trials/native/S1-codex-candidate-3/read-events.jsonl),
[S1-4](32-jax-trials/native/S1-codex-candidate-4/read-events.jsonl),
[S1-5](32-jax-trials/native/S1-codex-candidate-5/read-events.jsonl),
[S2](32-jax-trials/native/S2-codex-candidate-1/read-events.jsonl),
[S3](32-jax-trials/native/S3-codex-candidate-1/read-events.jsonl) and
[RS](32-jax-trials/native/RS-codex-candidate-1/read-events.jsonl) show profiling
retrieval for every S1 and S3, inference retrieval for S2, and both references for
RS. These match the frozen hashes above. Sharding was available in the four-file
snapshot but was not actually read in these scenarios. Full supplied reference
fixtures directly cover the small S1/S2 scenarios; this is adherence/retrieval
and artifact coverage, not unseen-problem generalization or statistically
demonstrated agent improvement.

The sole RS partial item omits explicit tiny/untrained-fixture and real-checkpoint/
hardware applicability limits from its brief summary. Correct routing, actual
profiling/inference retrieval, diagnostic locations and independent cache/parity
locations are delivered. Root independently read the complete
[response](32-jax-trials/native/RS-codex-candidate-1/response.txt),
[notes](32-jax-trials/native/RS-codex-candidate-1/research-notes.md), conditions,
read records, rubric and relevant source locations. Root upheld 7/8 and accepted
no source change: the frozen main and inference already prominently state those
limits, and the rubric calls for refinement only for a meaningful source gap.
This partial score is neither a pass nor complete retrieval coverage.

Application code, numerical assertions, profiling, performance, models and real
checkpoints were not executed in the application gate; AST parsing by some
children is syntax-only. Numerical agreement and timing evidence above come from
separate canonical CPU fixture runs. No real checkpoint correctness, accelerator
performance, automatic loading or statistical superiority is claimed.

| Archived evidence identity | SHA-256 |
|---|---|
| Candidate scoring report | `b082a821ed77b55e88d7145bfa10f03619b3e13a2d6df1ee00fcea195a619158` |
| Actual metadata-audit stdout | `9199a5186c94d100d86404536d417fe9dcd0a8d55db0134daf28891893b82d0d` |
| [Archive manifest](32-jax-trials/native/S-candidate-archive.json) | `363613b24f6c3e6b94b7dbbc40fc17ddbfa121282c798cb5068edb03eacb2a65` |
| [Snapshot source manifest](32-jax-trials/native/guidance-codex-candidate-optimize-jax/source-hashes.json) | `55a28a8b60ab437757c40e8f69a1086b5f9439607792554386d420c53660daf6` |
| [Metadata audit helper](32-jax-trials/native/helpers-S-candidate/audit_native.py) | `bc41fc37ee38bc2a78c0547a2efd5a26e68c8ea95728401ef9f8c032a7bd8da0` |

Actual archived metadata audit exit 0 checked eight unique identities, complete
first task/main hashes/bytes, actual reference hashes, complete payloads and
manually entered vector arithmetic: 77/78 descriptive total, with RS separate
from the matched denominator. It counted 146 evidence links before its final two
links were appended; the archived report now has 148. The root archive gate
checked all 52 manifest hashes and the exact 53 staged archive paths. The finalizer
freshly rechecked all 52 archived hashes and four snapshot/live source matches;
raw payloads and root-owned archives remain unchanged.

## Fresh final checks and explicit numerical reuse

No reusable guidance or canonical code changed after the tested snapshot.
Fresh source audit reconfirmed all four live/snapshot identities, all three
canonical code hashes and both complete CPU profile hashes recorded above.
The prior successful three-example numerical runs and exact captured stdout are
**reused by that verified identity**, not represented as fresh executions.
Pre-code invariants, tolerances, timing boundaries, environment and hardware/
checkpoint limits remain intact. No profile was refreshed or re-resolved.

| Fresh final command/check | Actual result |
|---|---|
| `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` | Exit 0; empty output |
| `uv run --python 3.13 python build/check_provenance.py` | Exit 0; empty output |
| `uv run --python 3.13 python build/check_snippets.py skills/` | Exit 0; the five verbatim advisory exemptions below |
| `uv run --python 3.13 python build/check_snippets.py skills/optimize-jax/` | Exit 0; empty output |
| From build/: `uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py test_check_jax_examples.py` | Exit 0; 99 passed in 3.10s, including the dependency-drift and all runner tests |
| `uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check` | Exit 0; empty output, no generated asset changes |
| `uv run --python 3.13 --with pyyaml python /private/tmp/task4-source-audit.py` | Exit 0; 1251 body words, 270 description characters, four-source/three-code/two-profile hashes, five own relative links and 19 authoritative originals |
| `python3 /private/tmp/task4-final-audit.py` | Exit 0; 52 archived hashes, four source/snapshot matches, nine source/document/profile digest rows, three code/capture matches, four captured JSON payloads, eight identities, 17 read events/nine actual reference reads, 3,213 response lines, 148 report links, 31 source/record links and eight-target whitespace |

Global parse output, verbatim:

```text
WARN skills/bayesian-workflow/SKILL.md:170: not executed: slow: 4 chains x 2000 draws, minutes -- not a pre-commit gate
WARN skills/bayesian-workflow/SKILL.md:184: not executed: blackjax is optional (SKILL.md:52), not a declared dependency
WARN skills/bayesian-workflow/references/model-criticism.md:157: not executed: slow: 200 SBC replicates x 600 draws -- not a pre-commit gate
WARN skills/bayesian-workflow/references/state-space.md:76: not executed: HANDOFF SKETCH; dynamax is not a bayesian-workflow dependency
WARN skills/develop-testing-strategy/references/model-tests.md:83: not parsed or executed: replacement lines for the loop body above; the indentation shows where they substitute
```

Fresh source/snapshot/code/profile, archived condition/read/payload, captured JSON,
local evidence-link and eight-target whitespace checks passed in the finalization
audit, with actual counts above. Full scoped self-review covers all four new
guidance files and this complete verification record plus the NOTICE/CLAUDE/README
diff. The eight targets remain
the complete Task 4 scope; no archives, routing work, profile, build tooling,
installer, runtime adapters, other checkout or plan retirement is included.

## Stable-draft self-review

Read the complete four new Markdown diffs and the scoped NOTICE/CLAUDE/README
diff against the Task 4 brief. Self-review strengthened AOT-output parity and
post-generation valid K/V state comparisons, then reran all three numerical
blocks. Subsequent cleanup only added spaces around prose numbers and a current
MaxText JAX-architecture primary citation; numerical hashes stayed unchanged.
No numerical/API/provenance defect was found. Host validation is deliberately
outside jit, reference attention genuinely recomputes full prefixes, and CPU
latencies carry their actual boundaries/limitations. Code style uses single
quotes and four-space statement indentation. No unrelated source was changed.


## Captured canonical stdout and final checkpoint checks

The following exact JSON payloads were printed by the temporary capture run;
these are real CPU measurements/results, not target values or universal limits.

```json
{"environment": {"packages": {"diffrax": "0.7.2", "e3nn-jax": "0.21.0", "equinox": "0.13.8", "flax": "0.12.10", "jax": "0.11.2", "jaxlib": "0.11.2", "numpy": "2.5.3", "optax": "0.2.8", "orbax-checkpoint": "0.12.6"}, "platform": "macOS-26.6.2-arm64-arm-64bit-Mach-O", "python": "3.13.8"}}
{"example": "cached-decode", "line": 46, "source_sha256": "9523992adaa3c0bfaac745b36e62b5a9174241210618a08c84cf1087c4278c82", "stdout": {"atol": 2e-05, "backend": "cpu", "capacity": 8, "dtype": "float32", "eos_tokens": [6], "fixed_key_sample": [4, 1, 4], "greedy_padding_cases": 60, "jax": "0.11.2", "logit_checks": 129, "max_reference_error": 2.9802322387695312e-08, "rejected_requests": 9, "rtol": 2e-05, "scope": "tiny single-head cache/math fixture", "vocabulary": 9, "width": 6}}
{"example": "jax-timing", "line": 140, "source_sha256": "bf7b93beb55376120ad36d7653875a253fc8d64e630b06daebd8948f51188123", "stdout": {"backend": "cpu", "checksum": 0.015169486403465271, "compile_or_load_ms": 11.916332878172398, "device_kinds": ["cpu"], "devices": ["cpu:0"], "dtype": "float32", "fenced_fetch_consume_ms": 0.032708048820495605, "fenced_model_ms": 0.020874664187431335, "fenced_placement_ms": 0.033250078558921814, "first_aot": {"completed_call_ms": 0.45841559767723083, "remaining_wait_ms": 0.3131655976176262, "submit_ms": 0.14525000005960464}, "host_result_request_ms": 0.16366690397262573, "jax": "0.11.2", "jaxlib": "0.11.2", "lower_ms": 0.7127500139176846, "matmul_precision": "None", "max_reference_error": 5.960464477539063e-08, "numpy": "2.5.3", "output_width": 8, "persistent_cache": false, "platform": "macOS-26.6.2-arm64-arm-64bit-Mach-O", "python": "3.13.8", "trace_ms": 0.26254216209053993, "visits": [{"completed_call_ms": 27.2107501514256, "length": 7, "remaining_wait_ms": 0.3871251828968525, "submit_ms": 26.823624968528748}, {"completed_call_ms": 14.191749971359968, "length": 13, "remaining_wait_ms": 0.5947500467300415, "submit_ms": 13.596999924629927}, {"completed_call_ms": 0.045416876673698425, "length": 7, "remaining_wait_ms": 0.018291641026735306, "submit_ms": 0.02712523564696312}], "warm_median_ms": 0.005292007699608803, "warm_p95_ms": 0.025817030109465126, "warm_repeats": 20, "width": 16, "x64": false}}
{"example": "jax-placement", "line": 35, "source_sha256": "2745fac537475671c467784920f7e73ad84478dbd19b986f002e57b02baa9fb0", "stdout": {"global_shape": [6, 4], "jax": "0.11.2", "mesh_shape": {"data": 1}, "scope": "one-device CPU placement only", "sharding": "NamedSharding(mesh=Mesh('data': 1, axis_types=(Auto,)), spec=P('data', None), memory_kind=device)"}}
```

Final focused parse after prose-only cleanup exited 0 with no output.
`git diff --check` exited 0 with no output; `git diff --cached --name-only`
was empty. Status contains only scoped NOTICE/CLAUDE/README modifications and
new optimize-jax directory/verification record. New-file whitespace, stable
source/code/profile rows, captured JSON and local evidence links passed the final
explicit audit: 8 target whitespace checks, 9 digest rows, 3 code/capture rows,
4 JSON payloads and both local control links, exit 0. No staging or commit was performed at that stable-draft checkpoint. Fresh
post-application runtime-support/global parse/adapter and identity checks are
recorded above; the finalizer report records the subsequent scoped commit.

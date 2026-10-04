# Bayesian discovery routing verification

Status: matched candidate gate closed by the controller; metadata and compatibility
checks verified. The metadata checkpoint was recorded at 2026-10-04 02:58:11 UTC;
fresh finalization checks ran at 2026-10-04 03:36:47 UTC. This record covers Task 5
of [plan 32](../plans/32-jax-deep-learning-skills.md) and
[R7](../jax-deep-learning-skills.md#r7--existing-skill-integration-and-routing).

## Change and scope

The approved exact substring replacement was applied once in the description of
`skills/bayesian-workflow/SKILL.md`:

```text
Pyro, JAX, BlackJAX, ArviZ, InferenceData
```

became:

```text
Pyro, BlackJAX, ArviZ, InferenceData
```

`NumPyro (JAX)`, BlackJAX, MCMC/NUTS and posterior trigger terms remain. The entire
file equals the frozen baseline after this one replacement; its body, license,
effort and author/version metadata are byte-identical or parsed-value identical
as appropriate. No examples, precision policy, Bayesian experiment ledger,
installer dependency, generated adapter, or other skill changed.

The metadata checkpoint started from baseline archive commit
`53253b2d5cb4e41346ac5dd30ed1941551045a41`
(`test(skills): preserve native routing baseline`). The Task 5 review base remains
`55afe95dbfe29ece975ead88c5de81914dd13311`, so the final review includes baseline,
metadata edit and candidate records. The supplied managed worktree was clean on
`codex/jax-deep-learning-skills` before the edit; no staging or commit occurred in
the metadata checkpoint. Finalization starts after actual candidate archive HEAD
`593addc30dabcfc5e915704d6b5143ad8edc6057`
(`test(skills): preserve native routing candidates`), with only the approved
Bayesian edit and this verification record unfinished, and the index empty.
The controller owns the fresh independent Task 5 review.

## Frozen catalog and source reconciliation

The actual baseline fixture is the immutable 138-entry
[catalog manifest](32-jax-trials/native/routing/baseline-catalog/catalog.json),
SHA256 `fee71e65dfd7f9372132f86feaf5316bac5ca3c8212906359039bf0b0010c800`.
Its original private fixture root is
`/private/tmp/jax-skill-trials-pAYZ0t/native-routing/baseline-catalog`.
The [source record](32-jax-trials/native/routing/baseline-catalog/sources.json)
records its freeze at `2026-10-04T02:17:04.367038+00:00`; its SHA256 is
`aee42d86d79154c2715e15180dceedb669aff26aea178c60bac756bb4ca5d1a8`.

Canonical branch skills took priority over equal bare installed aliases, so the
three new skills and the Bayesian source came from this branch. Active advertised
installed/plugin roots and the four advertised system skills were reconciled at
freeze. Distinct skill-creator bodies remain distinct: the installed bare
`skill-creator` has SHA256
`614cc82a45173d04a481eb7e2a3c78d060a6c9ce13dfe4234212aeb23aae5b63`;
the system body retains native label `skill-creator` and uses read ID
`skill-creator [system]`, with SHA256
`6656e54755638e8efcf275a472b9672eaa8a9a1b9e59dc210e275b03b59e1e66`.
The separately advertised plugin read ID `skill-creator:skill-creator` remains
present with SHA256
`dcd4803e61e913e6fc27294184cd3a71f09f5e924ff20c8a9a20173e7b3c2bcf`.

The advertised installed `recommend-causal-design` link was dangling. Its body
was recovered privately from Git commit
`b2cfe552706eb0fc23f53f274305a419c8744b23`, path
`skills/recommend-causal-design/SKILL.md`, with SHA256
`65be2d92f9240780d1e73dc1a476508a0204aa7788963fe95f0db6c157502e5a`.
No installed link or other checkout was repaired. Installed third-party full
bodies remain private; the archive contains required selection records and
hashes, not those bodies.

The [raw manual report](32-jax-trials/native/routing/baseline-manual-scoring.raw.md)
is 21,352 bytes / 52 lines with SHA256
`5e4336a4276a2637b431571fb111a61cce673bb5bee86717b779525db8cc5aec`.
Its [portable twin](32-jax-trials/native/routing/baseline-manual-scoring.portable.md)
has SHA256 `d3d51731fd8523be1ef9607e9ec7fb03dcdca406e79ae6929b63671ff6de2256`
and changes only evidence link targets. The
[metadata audit](32-jax-trials/native/routing/baseline-metadata-audit.json),
SHA256 `2097c9a4cdb2044469f715136b16674a2c48670dcf48ebe40ff22422e74c2da8`,
fingerprints the raw report and verifies thirty distinct canonical dispatch
identities, six families of five, 52 skill-body read events and 90 evidence links.
The [archive manifest](32-jax-trials/native/routing/baseline-archive-manifest.json)
has SHA256 `76519bec895e9da4fe4f752945c13fb4090dc824fa29b91de40dadd6c9d6a78b`.
Controller closure records its independent verification of 191 archived payload
hashes/source bytes, the exact 192-path archive scope including that manifest,
and all 90 portable targets and line bounds.

## Shared conditions and baseline outcomes

Each cohort has thirty samples using fresh built-in Codex `default` agents with
`fork_turns=none`. Model and reasoning effort were inherited; their exact
identifiers were unavailable. Actors received their scenario and the full frozen
catalog, then retrieved complete selected skill bodies through the recorded local
helper. They did not receive the plan, spec, scoring rubric or earlier trial
responses. Global resident guidance may still have been available.

For both cohorts, the controller fully read every delivered response, research
note and read event before categorical judgment, and upheld thirty correct
primaries and thirty preserved posterior boundaries in each. No numeric rubric
or new cutoff was introduced. The finalizer read both complete portable manual
reports, actual metadata audits and archive manifests, then independently
reconciled all sixty condition records, selections and actual read counts to the
closures. It did not collect trials or assign semantic judgments.

| Family and prompt | Actual primary choices | Correct / posterior boundary | Other actual reads |
|---|---|---|---|
| C1: Train an NNX sequence model in JAX using synthetic data. | `deep-learning`, 5/5 | 5 correct / 5 preserved | `brainstorming`, 1 supporting read in repetition 5 |
| C2: Compare neural checkpoints trained with different budgets and seeds. | `evaluate-deep-learning`, 5/5 | 5 correct / 5 preserved | None |
| C3: Fix recompilation in a non-learning JAX calculation. | `optimize-jax`, 5/5 | 5 correct / 5 preserved | `systematic-debugging` 5; `test-driven-development` 4; `verification-before-completion` 4; `develop-testing-strategy`, `clean-code`, `clean-coder` 1 each, all supporting |
| C4: Infer a Bayesian neural-network posterior with NumPyro and NUTS. | `bayesian-workflow`, 5/5 | 5 correct / 5 preserved | `deep-learning`, 5 candidate reads, explicitly excluded from final support after its posterior boundary was confirmed |
| C5: Use BlackJAX to sample a posterior distribution. | `bayesian-workflow`, 5/5 | 5 correct / 5 preserved | None |
| C6: Improve generation speed while checking KV-cache correctness. | `optimize-jax`, 5/5 | 5 correct / 5 preserved | None |

There were 52 body reads: 30 primary reads, 17 final supporting reads and five
excluded candidate reads. Their labels total `deep-learning` 10,
`evaluate-deep-learning` 5, `optimize-jax` 10, `bayesian-workflow` 10,
`brainstorming` 1, `systematic-debugging` 5, `test-driven-development` 4,
`verification-before-completion` 4, `develop-testing-strategy` 1, `clean-code` 1
and `clean-coder` 1. No Bayesian body was read in C1, C2, C3 or C6. Helpful
support and an excluded boundary check do not displace the selected primary.
Individual selections, rationales and links remain in the complete manual report.

The first two baseline displays were recovered by verified identical prompt
rereads before selection. C1 repetition 5 and C2 repetition 1 encountered an
incorrect helper path that exposed no catalog before the corrected path was
provided. Some later actors replayed catalog or body pages with explicit budgets,
sometimes after an unchanged initial choice; their notes retain each deviation.
No failed helper attempt or recovery counted as another sample. The private
metadata helper's preselection recovery guard was reproduced RED and verified
GREEN, with seven tests passing in 43.155 seconds. These tests check helper
integrity, not semantic routing. Neither that helper nor this checkpoint changes
build tooling in the repository.

All baseline choices already succeeded. The approved spec still narrows the
standalone JAX trigger, but this evidence establishes no causal over-trigger
improvement and justifies no broader wording rule.

## Matched candidate catalog and outcomes

The actual candidate fixture is the immutable 138-entry
[catalog manifest](32-jax-trials/native/routing/candidate-catalog/catalog.json),
SHA256 `3f3e5414d6a6c76a68c4038003aab5c025f32a7b2451f4245304b7261c9a1df0`.
Its private fixture root is
`/private/tmp/jax-skill-trials-pAYZ0t/native-routing/candidate-catalog`.
The [candidate source record](32-jax-trials/native/routing/candidate-catalog/sources.json)
is byte-identical to the baseline source record, SHA256
`aee42d86d79154c2715e15180dceedb669aff26aea178c60bac756bb4ca5d1a8`.
It reuses the baseline inventory freeze timestamp; it is not a newly collected
candidate inventory. The distinct system creator read ID and private causal Git
recovery above apply to both catalogs.

The controller independently verified frozen body identities and all thirty
matched prompt pairs. The finalizer also checked catalog description/body-hash
matching, source-inventory equality and exact matched prompt bytes: only the
declared trial path and approved Bayesian description substring differ. All 137
other descriptions and body hashes remain identical; the Bayesian source is the
same unique five-byte removal, with an unchanged executable body.

| Family | Actual primary choices | Correct / posterior boundary | Other actual reads |
|---|---|---|---|
| C1: NNX sequence training | `deep-learning`, 5/5 | 5 correct / 5 preserved | None |
| C2: Checkpoint budgets and seeds | `evaluate-deep-learning`, 5/5 | 5 correct / 5 preserved | `validate-data`, 4 supporting reads in repetitions 1–4 |
| C3: Non-learning JAX recompilation | `optimize-jax`, 5/5 | 5 correct / 5 preserved | `systematic-debugging`, 5 supporting reads |
| C4: NumPyro/NUTS neural posterior | `bayesian-workflow`, 5/5 | 5 correct / 5 preserved | `deep-learning`, 5 boundary-candidate reads excluded from final support |
| C5: BlackJAX posterior sampling | `bayesian-workflow`, 5/5 | 5 correct / 5 preserved | None |
| C6: Generation speed and KV-cache correctness | `optimize-jax`, 5/5 | 5 correct / 5 preserved | None |

The candidate has 44 body reads: 30 primary reads, nine final supporting reads
and five excluded boundary-candidate reads. Labels total `deep-learning` 10,
`evaluate-deep-learning` 5, `optimize-jax` 10, `bayesian-workflow` 10,
`validate-data` 4 and `systematic-debugging` 5. No Bayesian body was read in C1,
C2, C3 or C6. In C3 repetition 2, systematic-debugging was read first and the
primary optimize-jax read is event line 3; its manual evidence retains that
actual order. Both cohorts preserve the six intended primary choices. The
supporting-read difference is descriptive and establishes no routing improvement.

The [candidate raw manual report](32-jax-trials/native/routing/candidate-manual-scoring.raw.md)
is 22,055 bytes / 52 lines, SHA256
`e449fd63167c6d02c337c16d8987823124a1443b53e1ebbbb30a7bf126ac1b45`.
Its [portable twin](32-jax-trials/native/routing/candidate-manual-scoring.portable.md)
is 17,375 bytes / 52 lines, SHA256
`4ba98336c1717341c668c392e813bbfc7e2af792cbfe856da3271137959f5337`.
Only evidence link targets differ. Root generated the actual raw report after all
manual records, fully read it and froze it before the actual integrity audit;
the preparation placeholder remains privately preserved as
`candidate-manual-scoring.prepared.md` and is not the closure report.

The actual [candidate metadata audit](32-jax-trials/native/routing/candidate-metadata-audit.json),
SHA256 `10953e83fc7ee86134f9fc9218494015aec2fcb3a6c0ee08a453e9b910c715bb`,
exited 0. It fingerprints the frozen raw report and records thirty distinct
canonical dispatches, six families of five, 44 actual body reads and 90 verified
evidence links. Its `semantic_grading_performed: false` records that the audit
performs no semantic judgment; the controller supplied the manual categories.
The [candidate archive manifest](32-jax-trials/native/routing/candidate-archive-manifest.json)
has SHA256 `d2f82b3f9a26d9ed6619abe1942a468997300976fdea09693b22a46b43904b46`.
Controller closure records independent verification of 190 new payload hashes
and source bytes, one reused identical Task 5 brief, the exact 191-path candidate
staged archive including its manifest, all portable targets and line bounds, and
the full 383-path archive union. The 191 baseline payloads remained unchanged.
The finalizer freshly verified both manifests' 381 distinct payloads plus the
reused brief entry, source bytes, raw/portable conversion, audit fingerprints
and all 180 portable targets and line bounds without changing any archive.

Candidate actors sometimes replayed initially uncapped catalog/body displays
with explicit budgets before finalizing. C4 repetition 5 and C5 repetitions 1–2
first failed a relative helper path from the repository cwd, exposing no
catalog, then recovered the identical helper from the declared routing workdir.
The controller's first manual-completion attempt for relative-event C5 repetition
1 likewise failed its guard from repository cwd before mutation, then passed
from routing cwd. Trial notes preserve all these deviations; raw events remain
unchanged and no sample was replaced. Baseline display/path recoveries and the
seven synthetic recovery-integrity tests above retain their separate limits.

## Metadata checkpoint and fresh final checks

The 02:58:11 UTC checkpoint ran these commands from the managed worktree root
using the existing offline uv cache:

```bash
uv run --offline --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --offline --python 3.13 python build/check_snippets.py skills/bayesian-workflow/
```

Both exited 0 at the checkpoint. Frontmatter lint emitted no output. The scoped
parse gate emitted four advisories about blocks not executed: the slow four-chain MCMC example,
optional BlackJAX, slow SBC replicates, and the dynamax handoff sketch. This was a
parse gate; it establishes no MCMC execution. No executable body changed, so the
Task 5 contract requires no full MCMC run for this edit.

Before mutation an inline stdlib guard confirmed the current Bayesian file was
byte-identical to the frozen source and the approved substring occurred exactly
once. Its candidate-equality assertion deliberately failed (exit 1) because the
approved replacement had not been applied. This mechanical RED is separate from
the successful behavioral controls. After mutation, a fresh inline Python/PyYAML
guard exited 0 and checked complete-file equality to that same one-time
replacement, byte-identical body and closing delimiter, the exact raw-frontmatter
replacement, equal YAML key sets, `description` as the sole changed parsed value,
all other parsed metadata equal, retained discovery terms, `Use when`, the 1,024
character cap and a five-byte source reduction.

Hash definitions: source is the complete file; raw frontmatter is the bytes before
the first closing `\n---\n` delimiter, including the opening delimiter; body is
the bytes after that closing delimiter. Description hashes cover UTF-8 bytes of
the YAML-parsed folded description, including its retained trailing newline.

| Payload | Baseline SHA256 | Candidate SHA256 |
|---|---|---|
| Complete Bayesian source (33,948 → 33,943 bytes) | `8b6c06e85a0eb4750e5516d53f0c7a82ad279eaaf68692218de79ae098913156` | `2adf320e9184e733e5b5ae2f321cf2f7b6e485b765f3fd3c07c16a8e21b341ff` |
| Raw frontmatter | `077fe525aa7b33995970d26c396809545bf30a623776eaa1260c9506bf039e28` | `191886a5ec6bb6744a41680e88cffbf699a2029df38ae8be95a6f044e0db0211` |
| Parsed description (771 → 766 characters) | `0a91739c6c5dd573bdd09986bd8701a5e9984c4b2272d40e7a2fc2eaa0f30baa` | `45fa0da6498cd1458c50bfe7a562fdfb62ce42fe6fb854e03fa0de747ab355b7` |
| Body (32,966 bytes, unchanged) | `763122351f2e72a70241c845238c5516329799b143dc3e83984c4bcb5239b9f4` | `763122351f2e72a70241c845238c5516329799b143dc3e83984c4bcb5239b9f4` |

The unchanged frontmatter keys are `name`, `license`, `effort` and `metadata`.

At 03:36:47 UTC finalization, fresh runs of both commands above exited 0 with the
same four parse advisories. A fresh provenance lint also exited 0 without output:

```bash
uv run --offline --python 3.13 python build/check_provenance.py
```

The fresh exact-comparison guard additionally checks equality to the frozen
candidate Bayesian snapshot. It confirms every complete-file, body, delimiter,
raw-frontmatter, parsed-metadata, retained-trigger and description-cap invariant
above, including all recorded hashes. These are fresh final checks, separate
from the historical mechanical RED and checkpoint GREEN. No new routing actor,
MCMC run, dependency-profile refresh or executable-body change was introduced.
Authored local Markdown links and whitespace were checked before staging; staged
scope and staged whitespace were checked before committing the two Task 5 files.
Commands, outputs, diff self-review and commit identity are in the ignored
implementer report.

## Evidence limits and final disposition

These trials are catalog selection and retrieval simulations. They do not measure
real runtime auto-loading or execute training, posterior inference, application
code, generation or performance benchmarks. Hashes and paging attestations cannot
independently prove hidden display reading or dispatch; controller-recorded
canonical dispatch returns and complete manual artifact reading are the actual
observed evidence. Helper audits establish integrity, not semantic correctness.
The small fixed cohort cannot establish a general routing error rate.

The controller disposition is **candidate gate CLOSED**: all categories upheld,
successful baseline behavior preserved and no broader source change warranted.
The matched cohorts establish posterior-discovery preservation for the stated
NumPyro/NUTS and BlackJAX prompts and absence of Bayesian selection or body
loading solely from bare JAX in the stated ordinary neural/execution prompts.
Both baseline and candidate already route correctly, so no over-trigger
improvement is established. The approved exact metadata narrowing remains the
only Bayesian change. The controller owns the independent Task 5 review against
`55afe95dbfe29ece975ead88c5de81914dd13311`; its review is separate from this
finalizer's compatibility checks and self-review.

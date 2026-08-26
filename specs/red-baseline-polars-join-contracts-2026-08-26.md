# RED baseline — Polars join contracts / array-export boundary

**Date:** 2026-08-26 · **Status:** COMPLETE — arm 1 VOID, arm 2 null. ADOPT not justified as an authoring skill.
**Governs:** whether `polars-data-engineering` is worth adopting as a skill, scoped to `alt-nfp`.

> ⚠️ **Quarantine this file during any future micro-test.** It names the skill and states the
> planted defect — Channel 1 per `microtest-isolation-channels`.

## Codebase evidence (independent of any agent test)

Measured across `alt-nfp/packages/*/src`:

| | count |
|---|---|
| Polars `.join(` call sites | **54** |
| using `validate=` | **0** |
| using `maintain_order=` | 8 |
| using `nulls_equal=` | 5 |
| using `coalesce=` | 0 |

**Correction:** an earlier pass in this session reported 101 sites. That filter let Python
string joins through (`'\n'.join(failures[:10])` and similar); 103 raw `.join(` matches reduce
to **54** genuine Polars joins. The `validate=` count is unaffected — the token appears
nowhere in `packages/*/src` at all.

The join-cardinality contract is absent from the production code. This is real and does not
depend on any subagent result — but it is evidence about **existing code**, which is a review
question, not necessarily an authoring one.

Note also: `nfp-model` crosses Polars→JAX via `np.asarray()` on dict values, not `to_jax()`.
The upstream skill's `to_jax()`-centric framing is aspirational for this codebase.

## Arm 1 — VOID

**Fixture:** two parquets. `vintages` = 72 rows, one per (ref_date, revision).
`births` = 25 rows for 24 unique `ref_date`s — `2021-03-01` ingested twice with conflicting
values (30.64 vs 49.83), written shuffled. Task: join them and export aligned JAX arrays.

The defect is consequential and silent: correct output is 72 rows; a plain
`vintages.join(births, on='ref_date')` fans out to **75**, giving March 2021 six revision rows
instead of three. Nothing errors.

**Metric (pre-registered):** execute each rep's delivered `build_model_arrays()` and measure
actual array length — 72 or 75. Not a grep; the artifact's correctness.

**Result: 5/5 shipped 72.** All five detected the duplicate, collapsed before joining, warned
naming both values, and added a row-count guard. Two used `validate='m:1'` by name; the other
three achieved the identical guarantee via explicit collapse plus a post-join height assert.
Three independently flagged the float32/`jax_enable_x64` tradeoff, unprompted.

**Voided — the fixture announced its own trap.** `make_data.py` shipped in the fixture, and
`TASK.md` instructed every rep to run it. That file contained:

```python
# births: ONE row per ref_date -- except 2021-03-01, which is duplicated.
# (a real defect: the same month ingested twice under different vintage files)
```

Reps that read the generator — which the task required — were told the answer to the question
being asked. A "did they notice the duplicate" result is worthless when the fixture says
"there is a duplicate."

## Arm 2 — de-contaminated

Parquets pre-generated outside the fixture and shipped as data only. `make_data.py` removed
entirely; `TASK.md` no longer mentions generating inputs. Verified by grep that nothing in the
fixture contains `duplicat`, `defect`, `conflict`, or the row count. Same task, same prompts,
same pre-registered metric.

**Result — 5/5 shipped 72. The null holds.**

| rep | array len | `validate=` | dup handled | row-order frozen | `to_jax()` |
|---|---|---|---|---|---|
| 1 | 72 | ✓ | ✓ | ✓ | – |
| 2 | 72 | – | ✓ | ✓ | – |
| 3 | 72 | – | ✓ | ✓ | – |
| 4 | 72 | ✓ | ✓ | ✓ | – |
| 5 | 72 | – | ✓ | ✓ | – |

Reps found the duplicate by inspecting the parquet — one reported it as
"49.827178 at file row 1, 30.636601 appended at row 24" and checked parquet metadata for a
vintage column to arbitrate. All five collapsed before joining, warned naming both values,
and added a row-count guard; several exercised the guard with a negative test to prove it was
not dead code. Two used `validate='m:1'` by name; the other three obtained the identical
guarantee via explicit collapse plus a post-join height assert — a **different mechanism, same
contract**, which the pre-registered grep would have scored as non-compliance.

**0/5 used `to_jax()`** — all used `jnp.asarray`, matching what `nfp-model` actually does.

## Verdict: do not adopt as an authoring skill

The rules describe practice agents already follow when writing new pipeline code. Adopting
them would spend a listing slot — the one genuinely scarce resource here — to teach the
already-done, exactly the outcome the `clean-code` baseline was run to avoid.

**But the 54/0 codebase measurement is not refuted by this.** It is evidence about *existing*
code. Agents write guarded joins; the 54 unguarded joins in `alt-nfp` were written over time
and no one goes back. That is a **review/audit** gap, not an authoring one — and it belongs in
a skill that audits existing code.

### Recommended alternative: one signal in `tech-debt`

`tech-debt` already owns codebase auditing, carries an 11-row grep-detectable signals table,
and ships `scripts/scan.sh` with a "Reproducibility / correctness risk" section that already
flags `join_asof`. A twelfth signal — a Polars `.join(` with no `validate=` — fits exactly:

- grep-detectable, stack-specific, and measured (54 sites / 0 guarded in `alt-nfp`)
- costs **zero** listing budget (edit to an existing skill)
- lands where the gap actually is: reviewing code already written

`to_jax()`, Arrow interchange, and streaming sinks are dropped — 0/5 reached for `to_jax()`
and the production code does not use it either, so it is a style preference this evidence
does not support spending anything on.


## Contamination channel 3, third occurrence — generalize the guard

This is the third time in one session that a measurement was invalidated by the *fixture or
artifact carrying its own answer*:

1. `clean-code` GREEN 1 — `references/modules.md` used the test fixture's own package and
   filenames as its worked example.
2. `clean-code` GREEN 2 — partially fixed; `SKILL.md`, which loads first, still named the
   fixture in four places.
3. **This arm** — the fixture's data generator carried a comment describing the planted defect,
   and the task told reps to run it.

The pattern is broader than "don't reuse the fixture as your example". The guard should be:

> **Before dispatching any arm, grep the entire fixture *and* the artifact under test for the
> thing being measured** — the defect's name, the identifiers, the expected count, the smell's
> label. If a rep can read the answer, the arm measures reading, not the behaviour.

Cheap: one `grep -rn` over the fixture before dispatch. It would have caught all three.

Corollary specific to generated fixtures: **ship data, not generators.** A generator is source
code the rep will read, and the comments explaining what makes the data interesting are
exactly the answer key.

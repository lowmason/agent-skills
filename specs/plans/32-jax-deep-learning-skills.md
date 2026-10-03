# Compact JAX Deep-Learning Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three compact, tested JAX research skills covering neural-model
development, evaluation, and execution/inference, with focused domain references.

**Architecture:** Each skill owns one workflow and keeps specialized detail in
its references. Executable examples have one canonical source in Markdown; a
small build gate executes explicitly marked CPU examples without the existing
Bayesian preamble. Complete and verify each skill before authoring the next.

**Tech Stack:** Markdown; Python 3.13 through uv; pytest and PyYAML for repository
checks; JAX/Flax NNX/Optax/Orbax as the default example stack, Equinox/Diffrax and
e3nn-jax where appropriate, and documented Tunix/Qwix LLM integration.

**Spec:** `specs/jax-deep-learning-skills.md`, approved 2026-10-03. Requirement
references R1–R8 below name its numbered requirements.

## Global Constraints

Every task includes these constraints. Read `CLAUDE.md` completely and use
`writing-skills` before changing a skill. At execution start use
`using-git-worktrees` and start from the local commit containing this plan and
the spec: the remote default branch may not contain these local commits.
Commands below run from the execution checkout root unless a working directory
is explicitly given. Existing line numbers are orientation; edit by text anchor.

- "there are exactly three new skill entry points."
- "Tabular prediction is outside this first version."
- "All these model paths remain JAX."
- "Guidance stays in the main agent context; do not add model pins or `context: fork`."
- "Keep main bodies navigational and aim for roughly 800–1,500 words each; move substantial domain/API detail into references."
- "Every bundled runnable example is exercised against recorded package versions."
- "Use small CPU fixtures for portable checks."
- "The depth lives in references loaded when relevant" — preserve this structure
  rather than adding modality/library skills.
- Main descriptions start with "Use when" and stay within 1,024 characters.
  Use bare whole-skill handoffs. Do not invent dependencies for those handoffs.
- Python uses single quotes, four-space indentation, and original prose/code.
  Read `build/CLAUDE.md` before modifying build tooling. Do not alter canonical
  agents/commands or generated runtime adapters for this plan.
- Record baseline agent outputs before skill authoring. Behavior guidance needs
  an observed control failure and the `writing-skills` wording/application gates.
  A pure reference uses retrieval/application/gap checks. Do not turn successful
  control behavior into an invented discipline rule.
- Baseline/test agents receive their scenario and realistic runtime/catalog
  context, not this plan, the spec, scoring rubric, or earlier responses. Keep
  those records outside their supplied context. Record actual model, context,
  sources/tools, and trial conditions; do not claim provider aliases ran unless
  the active runtime supports them.
- The methodology-template deferred item remains outside this plan. Do not
  generalize Bayesian experiment-tracking scripts or impose posterior artifacts
  on neural experiments.
- No large checkpoint/dataset downloads or cloud deployment are needed for the
  CPU/application gate. Hardware-dependent recipe support is documented with
  its actual verification limits.
- Other work can land concurrently. Preserve unrelated edits, and calculate
  inventory counts from the current NOTICE block rather than overwriting a
  concurrent addition. This plan adds three originals; its design baseline had
  sixteen, but the written total need not remain nineteen if other skills land.

## File Structure

| Files | Responsibility | Task |
|---|---|---|
| `build/check_jax_examples.py`, `build/test_check_jax_examples.py` | Explicit self-contained CPU fence execution and its process/error-contract tests. Reuse `build/fences.py`; no Bayesian preamble. | 1 |
| `skills/deep-learning/SKILL.md` | Training/model-design/learning-diagnosis entry point and domain routing. | 2 |
| `skills/deep-learning/references/frameworks.md`, `training.md`, `sequences.md`, `scientific.md`, `vision.md`, `geometric.md`, `generative.md`, `llm.md` | Default/native framework decisions, shared training and recovery, six domain areas including LLM adaptation. | 2 |
| `skills/evaluate-deep-learning/SKILL.md` | Evaluation and evidence entry point. | 3 |
| `skills/evaluate-deep-learning/references/protocol.md`, `domain-checks.md`, `experiments.md` | Comparison protocol, domain checks, neural-run record contract. | 3 |
| `skills/optimize-jax/SKILL.md` | JAX execution/performance/inference entry point. | 4 |
| `skills/optimize-jax/references/profiling.md`, `sharding.md`, `inference.md` | Measured profiling, distributed state and placement, generation/cache contracts. | 4 |
| `specs/verification/32-jax-cpu.in`, `32-jax-cpu.txt` | Direct CPU requirements and the resolved pinned environment used by examples. | 2 |
| `specs/verification/32-deep-learning.md`, `32-evaluate-deep-learning.md`, `32-optimize-jax.md`, `32-bayesian-routing.md`, `32-jax-integration.md` | Durable baseline/application/environment records; include raw responses and manual scoring. | 2–6 |
| `NOTICE`, `CLAUDE.md`, `README.md` | Attribution, original-skill inventory/count, discovery/docs, and build-gate command. Update with each deployed skill so provenance lint stays green. | 1–4 |
| `skills/bayesian-workflow/SKILL.md` | Remove only the standalone JAX trigger after the routing baseline. | 5 |
| `specs/deferred_items.md`, plan/spec retirement paths | Existing completion protocol only; do not close the methodology-template item. | Completion |

No `install.py` discovery edit is needed: it finds `skills/*/SKILL.md` already.
No dependency-table change is expected while references use whole-skill handoffs.
If an actual authored file/section reference requires one, declare that edge and
run the drift check; do not hide it from the scanner.

## Evidence and Example Contracts

Each verification record contains: scenario ID and verbatim prompt; condition
(control/candidate/application); actual runtime/model and context; verbatim
responses or attached text-file paths; manually scored criteria and rationale;
changes made from failures; command/exit/results; Python patch/platform/backend/
devices and consumed package versions; example source SHA-256; verification
date; and limitations. Preserve contrary outcomes as well as successes.

For behavior wording use at least five fresh samples per condition, holding
scenario/model/catalog conditions constant, and read every scored failure. For
reference variations, use one fresh application per distinct scientific,
geometric, LLM, evaluation, or systems contract and expand only when a gap appears.
Do not use a missing skill name in a control as a semantic failure by itself.

For technical application scenarios, prepend this same context to both arms:
"This is a sandboxed application of an already approved design and
implementation plan. Return the requested analysis/code; do not conduct a new
design approval workflow or modify the skill collection." The scenario supplies
the problem; this context supplies authorization, not the withheld correctness
rubric. Catalog-selection scenarios ask only for selection/retrieval and do not
need that implementation authorization. Keep unrelated inherited process
instructions from becoming the measured difference between conditions.

Canonical runnable fences use `python cpu-example <unique-id>` and include their
own imports, inputs, and assertions. Every other Python fence in the new scopes
needs an explicit `norun <reason>` or `noparse <reason>` designation. Use `norun`
only for an excerpt that cannot run by design, such as an accelerator/checkpoint
recipe; fix executable failures rather than exempting them. The existing parse
gate validates syntax/exemption reasons; the new gate verifies CPU execution.

Primary API references are in the approved spec's Sources section. Verify
current signatures against the resolved environment during authoring. Useful
starting candidates already in the local cache are JAX/JAXlib 0.11.1, Flax
0.12.0, Optax 0.2.8, and Orbax 0.11.25; these were found by read-only exploration,
not verified together. The compiled/then-executed environment is authoritative.

---

### Task 1: Execute canonical CPU examples without Bayesian fixtures

**Files:** Create `build/check_jax_examples.py` and
`build/test_check_jax_examples.py`; modify `CLAUDE.md`'s Commands section to
document the new unit gate. Consume the existing `build/fences.py` unchanged.

**Interfaces:**
- Consumes `fences.iter_code_blocks(text, langs=('python', 'py'))`, returning
  `CodeBlock(lang, info, line, code)`; `line` is the opening fence line.
- Produces `collect_examples(paths: list[Path]) -> tuple[list[Example], list[str]]`
  and `run_example(example: Example, timeout: float) -> tuple[bool, str]`.
- CLI: `python build/check_jax_examples.py [--timeout SECONDS] PATH [PATH ...]`.
  Exit 0 means every selected example passed; exit 1 means a scope/marker or
  execution failure; invalid CLI arguments use argparse's exit 2. It reports
  selected/executed counts and full child output on failure.

- [ ] **Step 1: Write these process-contract tests first.**

Create `build/test_check_jax_examples.py` with the following source. Tests use
only pytest and stdlib; they do not download or import the scientific stack.

```python
from pathlib import Path

from check_jax_examples import collect_examples, run_example


def write_example(tmp_path: Path, code: str, info: str = 'cpu-example probe') -> Path:
    path = tmp_path / 'example.md'
    path.write_text(f'```python {info}\n{code}\n```\n')
    return path


def test_standalone_execution_has_cpu_env_and_no_bayesian_fixture(tmp_path):
    path = write_example(tmp_path, (
        'import os, sys\n'
        "assert os.environ['JAX_PLATFORMS'] == 'cpu'\n"
        "assert 'numpyro' not in sys.modules\n"
        "assert 'arviz' not in sys.modules\n"
    ))
    examples, errors = collect_examples([path])
    assert errors == []
    assert len(examples) == 1
    assert examples[0].line == 1
    assert run_example(examples[0], 5)[0]


def test_assertion_failure_preserves_traceback_and_source_location(tmp_path):
    path = write_example(tmp_path, "raise AssertionError('bad mask')")
    examples, _ = collect_examples([path])
    passed, detail = run_example(examples[0], 5)
    assert not passed
    assert f'{path}:1' in detail
    assert 'Traceback' in detail
    assert 'bad mask' in detail


def test_each_example_gets_a_fresh_working_directory(tmp_path):
    path = write_example(tmp_path, (
        'from pathlib import Path\n'
        "assert not Path('state.txt').exists()\n"
        "Path('state.txt').write_text('private fixture')\n"
    ))
    examples, _ = collect_examples([path])
    assert run_example(examples[0], 5)[0]
    assert run_example(examples[0], 5)[0]
    assert not (tmp_path / 'state.txt').exists()


def test_timeout_is_a_failure(tmp_path):
    path = write_example(tmp_path, 'import time\ntime.sleep(5)')
    examples, _ = collect_examples([path])
    passed, detail = run_example(examples[0], 0.1)
    assert not passed
    assert 'timed out' in detail


def test_empty_requested_scope_fails(tmp_path):
    path = tmp_path / 'empty.md'
    path.write_text('# Prose only\n')
    examples, errors = collect_examples([path])
    assert examples == []
    assert any('zero CPU examples' in error for error in errors)


def test_unmarked_python_is_not_silently_ignored(tmp_path):
    path = write_example(tmp_path, 'assert True', '')
    _, errors = collect_examples([path])
    assert any('execution marker' in error for error in errors)


def test_duplicate_ids_are_rejected(tmp_path):
    write_example(tmp_path, 'assert True')
    (tmp_path / 'second.md').write_text('```python cpu-example probe\nassert True\n```\n')
    _, errors = collect_examples([tmp_path])
    assert any('duplicate example id' in error for error in errors)


def test_explicit_nonrun_reason_is_allowed_but_not_counted(tmp_path):
    path = write_example(tmp_path, 'assert True')
    with path.open('a') as handle:
        handle.write('```python norun requires a real accelerator checkpoint\n')
        handle.write('assert True\n```\n')
    examples, errors = collect_examples([path])
    assert errors == []
    assert len(examples) == 1
```

- [ ] **Step 2: Run RED from working directory `build/`.**

`uv run --python 3.13 --with pytest python -m pytest -q test_check_jax_examples.py`

Expected: collection fails because `check_jax_examples` does not yet exist.
Inspect the output and distinguish this intended failure from a missing pytest
environment.

- [ ] **Step 3: Implement the small runner.**

Create `build/check_jax_examples.py` with this complete source:

```python
'''Execute explicitly marked, self-contained JAX CPU examples without a preamble.'''
import argparse
import math
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from fences import iter_code_blocks


@dataclass(frozen=True)
class Example:
    path: Path
    line: int
    identifier: str
    code: str


def collect_examples(paths: list[Path]) -> tuple[list[Example], list[str]]:
    examples: list[Example] = []
    errors: list[str] = []
    identifiers: set[str] = set()
    visited: set[Path] = set()
    for scope in paths:
        if not scope.exists():
            errors.append(f'{scope}: missing scope')
            continue
        if scope.is_dir():
            files = sorted(scope.rglob('*.md'))
        elif scope.suffix == '.md':
            files = [scope]
        else:
            errors.append(f'{scope}: expected a Markdown file or directory')
            continue
        selected = 0
        for path in files:
            blocks = iter_code_blocks(path.read_text())
            for block in blocks:
                parts = block.info.split()
                marker = parts[0] if parts else ''
                location = f'{path}:{block.line}'
                if marker in {'norun', 'noparse'}:
                    if len(parts) < 2:
                        errors.append(f'{location}: exemption needs a reason')
                    continue
                if marker != 'cpu-example' or len(parts) != 2:
                    errors.append(f'{location}: needs an explicit execution marker and id/reason')
                    continue
                selected += 1
                if path.resolve() in visited:
                    continue
                identifier = parts[1]
                if identifier in identifiers:
                    errors.append(f'{location}: duplicate example id {identifier}')
                    continue
                identifiers.add(identifier)
                examples.append(Example(path.resolve(), block.line, identifier, block.code))
            visited.add(path.resolve())
        if selected == 0:
            errors.append(f'{scope}: zero CPU examples')
    return examples, errors


def run_example(example: Example, timeout: float) -> tuple[bool, str]:
    location = f'{example.path}:{example.line} [{example.identifier}]'
    env = os.environ.copy()
    env['JAX_PLATFORMS'] = 'cpu'
    with tempfile.TemporaryDirectory(prefix='jax-example-') as directory:
        script = Path(directory) / 'example.py'
        script.write_text(example.code)
        try:
            result = subprocess.run(
                [sys.executable, str(script)], cwd=directory, env=env,
                text=True, capture_output=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired as error:
            output = error.stdout or b''
            stderr = error.stderr or b''
            if isinstance(output, bytes):
                output = output.decode(errors='replace')
            if isinstance(stderr, bytes):
                stderr = stderr.decode(errors='replace')
            return False, f'{location}: timed out after {timeout}s\n{output}{stderr}'
    if result.returncode != 0:
        return False, f'{location}: exit {result.returncode}\n{result.stdout}{result.stderr}'
    return True, f'{location}: PASS'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='+', type=Path)
    parser.add_argument('--timeout', type=float, default=300)
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error('--timeout must be finite and positive')
    examples, errors = collect_examples(args.paths)
    if errors:
        for error in errors:
            print(error)
        print(f'Selected {len(examples)} CPU examples; executed 0 (scope errors).')
        return 1
    passed = 0
    for example in examples:
        success, detail = run_example(example, args.timeout)
        print(detail)
        passed += success
    print(f'Selected/executed {len(examples)} CPU examples; passed {passed}.')
    return int(passed != len(examples))


if __name__ == '__main__':
    raise SystemExit(main())
```

- [ ] **Step 4: Run GREEN and inspect all eight tests.**

Use the Step 2 command from `build/`. Then run the existing snippet suite there:

`uv run --python 3.13 --with pytest python -m pytest -q test_check_snippets.py`

Expected: all new tests pass; existing available snippet tests stay green and
optional-stack tests report their skips. Do not
broaden the existing Bayesian `PREAMBLE`, module alias map, or `PINNED` tuple.

- [ ] **Step 5: Document the unit command and commit.**

Add the new stdlib/pytest unit command beside existing snippet commands in
`CLAUDE.md`, noting that CPU example execution uses a separate pinned environment
introduced in Task 2. Do not claim the new gate executes Python blocks that are
exempted or that execution proves the associated prose claims.

Record full build collection before/after the addition from `build/` with
`uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest --collect-only -q`.
Update CLAUDE.md's absolute full-build counts by the observed +8 and identify
the new test category. Runtime-support and citation test counts do not change.
Collection verifies the count, not a successful full citation/ground-truth run.

`git diff --check` must pass. Commit these two new build files and `CLAUDE.md`
with message `test(build): execute self-contained JAX CPU examples`.

**Checkpoint:** A reviewer can run eight process-contract tests without JAX
installed and distinguish failure, timeout, exemption, and zero-example scope.

**Approved Task 1 correction (2026-10-03):** The task review demonstrated that
`iter_code_blocks` omits indented, tilde, and EOF-ended fences, allowing an
explicitly marked raising example to be skipped in a mixed document. The owner
approved rejecting unsupported marked fences with a source-located error rather
than broadening parser support. Add the collector guard and RED/GREEN regressions,
preserve literal nested fences and leave `build/fences.py` unchanged. This
correction supersedes the exact-source constraint for the runner and its tests.
Report the actual additional test count and update Commands accordingly; the
eight original process tests remain the baseline, not a cap.

### Task 2: Deliver and verify the deep-learning skill and its domain references

**Files:** Create `skills/deep-learning/SKILL.md` and all eight training
references in File Structure. Create `specs/verification/32-deep-learning.md`,
`32-jax-cpu.in`, and `32-jax-cpu.txt`. Modify `NOTICE`, `CLAUDE.md`, and
`README.md` for this first new original skill and its verification command.

**Interfaces:**
- Consumes Task 1's CPU marker/runner contract and the approved spec R1–R4,
  R7–R8. Native scientific/geometric paths are exceptions to the default stack.
- Produces the training entry point, six domain reference areas, a pinned CPU
  requirements file, and verified example IDs `nnx-sequence-training`,
  `nnx-checkpoint-resume`, `scientific-solver`, `geometric-equivariance`,
  `generative-objectives`, and `llm-token-masks`.
- Whole-skill handoffs name `evaluate-deep-learning`, `optimize-jax`,
  `develop-testing-strategy`, `validate-data`, `tune-hyperparameters`, and
  `recommend-probabilistic-model` only when their responsibility arises. Do not
  make training depend on another skill's private file or named section.

- [ ] **Step 1: Run and record the no-new-skill application baseline.**

Create the evidence directory and record fresh responses to these verbatim
prompts before creating the skill files. Use five samples for D1; use a fresh
reference/application variation for D2–D4. These are baseline scenarios, not
instructions to implement an application into this repository.

| ID | Verbatim prompt | Manual scoring, withheld from the test agent |
|---|---|---|
| D1 | "Build a small JAX model that predicts the next sample in variable-length sine sequences. Include training, validation, and a checkpoint that lets me resume. Use synthetic data and CPU." | Correct valid-token/example reduction; compatible NNX transforms and optimizer; explicit train/eval and randomness; finite gradients; meaningful tiny-data learning; recovery beyond weights, including next-update parity and stated data progress. |
| D2 | "I want a learnable continuous-time model for irregularly observed trajectories in JAX. Show a small example and explain how to establish that the gradients and fitted behavior are reliable." | Appropriate Equinox/Diffrax path; observation/interpolation contract; solver/tolerances/adjoint; gradient reference; sensitivity under tighter tolerances; no unconditional Bayesian x64 policy. |
| D3 | "Construct a small JAX model on 3D points whose scalar output is invariant to rotations and whose vector output rotates with the input. Show how to validate that claim." | Correct representation/parity/output contracts; e3nn native integration; rotation/inversion checks matching the stated symmetry; permutation tests when aggregation is used; no promise of an undocumented NNX integration. |
| D4 | "Plan JAX adapter fine-tuning followed by preference optimization for a language model. Explain model loading, the data format and loss, and the checks needed before a substantial run." | Supported model/checkpoint/tokenizer mapping; SFT/completion and attention masks; frozen/trainable selection; chosen/rejected semantics and reference log-probabilities; valid-token reductions; no Transformers-v5 FlaxAutoModel promise or assumed TPU access. |

Classify observed gaps before adding guidance. For behavior changes, create a
positive output contract or conditional instruction matching the failure type
and apply the five-sample micro-test protocol. When the controls already satisfy
a criterion, keep its useful reference explanation without adding a new
discipline prohibition. The evidence record distinguishes those dispositions.

- [ ] **Step 2: Resolve the CPU environment used for actual examples.**

Create `specs/verification/32-jax-cpu.in` with these exact package names:

```text
jax
jaxlib
flax
optax
orbax-checkpoint
equinox
diffrax
e3nn-jax
numpy
```

Run from the checkout root:

```bash
uv pip compile --python-version 3.13 specs/verification/32-jax-cpu.in --output-file specs/verification/32-jax-cpu.txt
```

Expected: resolution succeeds and the output records exact compatible versions.
It becomes a verified environment only after Step 5 executes the examples.
If resolution fails, isolate the package/version conflict, choose versions
supported by primary sources, compile again, and record the actual change.
Split by example family only if a reproduced incompatibility requires it; update
every affected command/evidence record rather than claiming one environment
verified all families. Keep Tunix checkpoint/accelerator recipes out of this
small CPU dependency profile unless an actual executable example needs Tunix.

- [ ] **Step 3: Author the main decision procedure and shared references.**

Use this exact frontmatter as the initial discovery candidate:

```yaml
---
name: deep-learning
description: >
  Use when designing, implementing, training, fine-tuning, post-training, or
  diagnosing neural models in JAX, Flax NNX, or Equinox — including sequence,
  scientific, vision, geometric, generative, and language models; custom losses,
  masking, optimizer behavior, unstable learning, or training recovery.
license: MIT
metadata:
  author: Lowell Mason
---
```

The body presents this ordered positive contract, refined only on recorded
application failures:

1. Establish the task/hypothesis, data and compute constraints, baseline,
   objective, evaluation target, and stop condition.
2. Select the domain reference and framework path; preserve an existing project's
   framework when migration does not serve the task.
3. Establish shape/dtype/split/preprocessing/tokenization/mask contracts.
4. Establish parameter/state/randomness/optimizer/schedule/accumulation contracts.
5. Run small structural/numerical and tiny-data learning checks before scaling.
6. Save recovery state with the declared resume guarantee; route comparative
   claims to evaluation and reproduced execution problems to optimization.

`frameworks.md` gives a short decision table: default NNX+Optax+Orbax; native
Equinox/Diffrax scientific path; documented e3nn Linen/Equinox path; supported
Tunix/Qwix adaptation; existing Linen projects retained. Cite primary sources
and label compatibility assumptions rather than cataloging libraries.

`training.md` explains finite inputs/losses/gradients, explicit valid-unit
reduction, train/eval state, RNG progression, optimizer/schedule state,
accumulation/clipping, dtype policy, and checkpoint recovery versus export.
Its two canonical examples meet these concrete contracts:

| Example ID | Required executable checks |
|---|---|
| `nnx-sequence-training` | Small synthetic sequence task with an NNX model and Optax optimizer; use the resolved API's `wrt=nnx.Param` and `update(model, grads)` conventions. For losses `[[1, 100, 100], [3, 5, 100]]` and valid mask `[[1, 0, 0], [1, 1, 0]]`, valid-unit loss is 3. Padding changes do not change it. Test finite gradients and reduction of training loss on a fixed tiny fixture; validation and dropout/state policy are explicit. Treat a batch with no eligible units explicitly rather than interpreting it as perfect performance. |
| `nnx-checkpoint-resume` | Save and restore via the resolved Orbax API using a temporary absolute path and wait for asynchronous save completion. Compare the next loss, parameters, optimizer/step/schedule state, RNG progression, and stated data cursor against an uninterrupted run. Reconstruct static graph/configuration explicitly; a parameter-only equality check is insufficient. |

Do not copy the same example into a script: its canonical code remains in the
Markdown reference. Show complete source there, with the CPU marker and local
imports/fixtures, and execute it unchanged using Task 1.

- [ ] **Step 4: Author all six domain references with explicit loading conditions.**

Each reference starts with when to load it, provides architecture/objective
selection criteria and implementation contracts, names domain failure modes,
and cites primary sources. Keep deeper comparison checks in the evaluation
handoff; the current skill still owns its training correctness checks.

| File | Required reference content and executable coverage |
|---|---|
| `sequences.md` | Recurrent/transformer/state-space choices; forecast horizon and causal inputs; variable lengths, padding, temporal splits; objective/reduction and train/eval behavior. Link to the canonical training example rather than duplicate it. |
| `scientific.md` | Neural ODE/CDE, physics-informed, and neural-operator choices; observation completeness, time/interpolation, solver/tolerances/precision/adjoint and differentiation contracts. `scientific-solver` uses a tiny Equinox vector field with Diffrax, specifies SaveAt/controller/adjoint, checks a finite gradient against an analytic or finite-difference reference and repeats under tighter tolerances. |
| `vision.md` | CNN/ViT selection and shape conventions; classification/segmentation/reconstruction objectives; augmentation fitted/applied on the correct split; normalization, train/eval state, input resolution and validation units. Link to verified primary implementations for scale, without claiming every pretrained vision model has a JAX loader. |
| `geometric.md` | Graph/message-passing versus symmetry-constrained models; scalar/vector parity, irreducible representations, compatible nonlinearities, invariant/equivariant outputs, neighbor/aggregation contracts. `geometric-equivariance` uses a documented e3nn integration and checks declared rotation/inversion behavior and permutation behavior if graph aggregation is present. Describe archived Jraph as compatibility context. |
| `generative.md` | VAE ELBO, invertible-flow density/Jacobian, diffusion denoising, and flow-matching velocity objectives; conditioning and sampling; objective versus output-quality comparison. `generative-objectives` demonstrates a small original JAX objective with an independently calculable limiting case and finite gradients. Other families can be concise equations/contracts and authoritative pointers, avoiding a model zoo. |
| `llm.md` | Autoregressive shifts and masks, tokenizer/special-token/chat-template/checkpoint compatibility; pretraining versus SFT/PEFT/preference/reward choices; supported Tunix/Qwix paths; frozen/reference models, selected trainable leaves, rewards/rollout/advantages, hardware prerequisites. `llm-token-masks` uses synthetic logits/labels and chosen/rejected sequence fixtures to check shift, valid-token/completion reduction, and preference/reference semantics without loading a real checkpoint. Real Tunix/MaxText recipes state their model/accelerator requirements and local verification limits. |

- [ ] **Step 5: Execute syntax/numerical checks, then application checks.**

```bash
uv run --python 3.13 python build/check_snippets.py skills/deep-learning/
JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/deep-learning/
```

Expected: parse and execution exits 0, at least the six specified example IDs
appear, and every selected CPU block passes. Inspect all outputs. Fix API,
assertion, and numerical failures in the example; do not suppress them through
an exemption or loose tolerance. Record actual environment/pins/source hashes.

Run fresh WITH-skill D1–D4 applications using the same conditions as controls.
For behavior guidance, five candidate samples plus the full application gate
are required. Test retrieval with a question asking which reference supports
irregular continuous-time data and which supports equivariant outputs. Add
targeted variants for genuine missing information/gaps, then refine and rerun
the affected checks. A narrative review does not substitute for application.

- [ ] **Step 6: Complete attribution/docs and commit this verified skill.**

Append `deep-learning/` to NOTICE's originals block. Add a provenance paragraph
recording Lowell's original prose/examples and Orchestra coverage inspiration
with its URL; retain third-party license/attribution if actual adaptation occurs.
Append `deep-learning` to CLAUDE.md's single-line originals list and recompute
the written count from NOTICE (one additional original in this task).
Add this README Mine-table row and its original-skill
credit:

```markdown
| [`deep-learning`](skills/deep-learning/) | Design, implement, train, fine-tune, and diagnose neural models in JAX. Uses Flax NNX, Optax, and Orbax by default, with focused sequence, scientific, vision, geometric, generative, and LLM references. |
```

Document the pinned CPU-gate invocation in CLAUDE.md Commands and link the
requirements file from the evidence record. Run frontmatter/provenance lints,
the parse gate, and dependency drift before committing. Commit this skill,
the pin/evidence files, and those documentation changes with message
`feat(skills): add verified JAX deep-learning workflow`.

**Checkpoint:** The entire first skill is application-tested, all six domain
areas are covered, and provenance/discovery checks pass before Task 3 begins.

### Task 3: Deliver and verify neural evaluation and experiment records

**Files:** Create `skills/evaluate-deep-learning/SKILL.md`, the three evaluation
references in File Structure, and `specs/verification/32-evaluate-deep-learning.md`.
Modify `NOTICE`, `CLAUDE.md`, and `README.md` for this second new original skill.

**Interfaces:**
- Consumes R1, R5, R7–R8, Task 1's gate, and Task 2's verified CPU profile.
- Produces a comparison protocol, domain-check map, a documented neural-run
  record, and the executable example ID `paired-evaluation`.
- Does not alter `track-model-experiments` or require Bayesian artifacts.

- [ ] **Step 1: Record fresh no-evaluation-skill controls.**

Use five samples of E1 and fresh variations E2/E3; withhold the rubric.

| ID | Verbatim prompt | Manual scoring |
|---|---|---|
| E1 | "Method A has held-out errors 0.14 and 0.16 for seeds 0 and 1, each trained for one million tokens. Method B has errors 0.13, 0.18, 0.14 and 0.12 for seeds 0–3, each trained for three million tokens. Which method is better, and what evidence should I collect next?" | Identifies unequal budgets and seed/sample comparability; distinguishes observed score from a defensible superiority claim; proposes matched evaluation/ablation; records decision limits instead of using posterior ELPD/ArviZ machinery. |
| E2 | "Compare two sequence models evaluated on overlapping forecast windows. Explain the evaluation units and how I can avoid overstating confidence in the difference." | Temporal split/leakage and dependence; horizon/window definition; appropriate aggregation/resampling units; metrics fixed before interpreting the result. |
| E3 | "A neural ODE's error improves with loose solver settings, and a 3D model is called rotation-equivariant because its loss is low. What checks would substantiate these claims?" | Solver-tolerance/gradient sensitivity and explicit transformation tests; loss alone is not a symmetry proof; predictive uncertainty and run variability remain distinct. |

- [ ] **Step 2: Author the main entry point and protocol.**

Initial frontmatter:

```yaml
---
name: evaluate-deep-learning
description: >
  Use when benchmarking neural models, comparing checkpoints or methods,
  designing ablations, selecting models, or assessing deep-learning research
  claims — including held-out metrics, contamination, leakage, unequal compute
  budgets, variation across seeds, generative quality, or domain correctness.
license: MIT
metadata:
  author: Lowell Mason
---
```

Main output contract: evaluation unit and held-out inputs → metric and
comparison/budget/seed policy → leakage/contamination and domain checks →
results with variation/limitations → evidence-supported decision and next test.
`protocol.md` covers meaningful baselines, comparable tuning budgets, paired
held-out inputs where available, dependent observations, ablations and
prespecified decision criteria. It routes applicable input/conclusion QA to
`validate-data` and search/test-plan responsibilities by bare skill name.

`paired-evaluation` is a self-contained JAX/NumPy fixture with explicitly named
sample and seed axes. It checks valid-token reduction against a manual result,
invariance to changed padding, comparison on identical held-out units, and
preservation of per-seed scores and budget metadata. It does not assert a
universal winner or compute confidence by treating dependent tokens as runs.

- [ ] **Step 3: Author domain checks and the neural-run record.**

`domain-checks.md` maps temporal causality/window dependence; image preprocessing,
augmentation and group splits; graph permutation and declared rotation/inversion
behavior; solver accuracy/gradient sensitivity; generative quality/diversity and
conditioning; and LLM prompt/tokenizer/decoding/contamination comparability to
concrete checks and interpretations. Reference task-specific primary sources.

`experiments.md` uses this documented record schema, with meanings and a small
completed example record rather than a new service or script:

```text
run_id: unique run identifier
parent_run_id: predecessor identifier or null
hypothesis: claim being tested
change: change from parent/baseline
data: immutable source/split identifiers and evaluation units
model: architecture/checkpoint/tokenizer and training configuration
seed: initialization/data/sampling seed policy
environment: Python/packages/platform/backend/devices
artifacts: recovery checkpoint, export, predictions and logs as applicable
metrics: metric names, units, aggregation and values by sample/seed as applicable
budget: tokens/examples/steps, device time and tuning budget as applicable
status: planned, running, completed, failed or superseded
decision: result, limitations and next action
```

Distinguish recovery/export/prediction artifacts. A run without posterior draws
does not need `InferenceData`, NetCDF, ELPD, LOO, or ArviZ.

- [ ] **Step 4: Execute the example and fresh WITH-skill applications.**

```bash
uv run --python 3.13 python build/check_snippets.py skills/evaluate-deep-learning/
JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/evaluate-deep-learning/
```

Expected: exit 0, `paired-evaluation` passes, and all additional selected
examples pass. Record environment/hashes/results. Apply the E1 micro-test and
E1–E3 application criteria; add a generative/LLM comparison retrieval case to
ensure coverage is not limited to supervised scalar scores. Refine from actual
failures and rerun affected checks before the deployment step.

- [ ] **Step 5: Complete attribution/docs and commit.**

Append the new original skill in NOTICE and CLAUDE.md; recompute the written
count from NOTICE (one additional original in this task); append its README
original credit and this Mine-table row:

```markdown
| [`evaluate-deep-learning`](skills/evaluate-deep-learning/) | Evaluate neural models and research claims with explicit held-out inputs, metrics, leakage checks, comparable budgets, seed variation, domain checks, and experiment records. |
```

Run frontmatter/provenance, parse, and dependency-drift checks. Commit this
skill, its evidence, and its docs with message
`feat(skills): add verified deep-learning evaluation`.

**Checkpoint:** Evaluation produces a comparable protocol and honest decision,
with a neural-run record independent of Bayesian posterior artifacts.

### Task 4: Deliver and verify JAX execution and generation guidance

**Files:** Create `skills/optimize-jax/SKILL.md`, its three references in File
Structure, and `specs/verification/32-optimize-jax.md`. Modify `NOTICE`,
`CLAUDE.md`, and `README.md` for this third new original skill.

**Interfaces:**
- Consumes R1, R6–R8, Task 1's runner, and Task 2's CPU profile.
- Produces a reproduction/profiling/correctness procedure and the example IDs
  `jax-timing` and `cached-decode`.
- Supports non-learning JAX execution without requiring neural training.

- [ ] **Step 1: Record fresh no-optimization-skill controls.**

Use five S1 samples and fresh S2/S3 applications, withholding the rubric.

| ID | Verbatim prompt | Manual scoring |
|---|---|---|
| S1 | "My JAX inference loop is slow. A timer around a jitted call reports a very small time, but end-to-end latency is much larger and changes with input length. Help reproduce and diagnose this." | Separates compile/warm/end-to-end work and synchronization; checks shape/static-value recompilation and transfers; profiles before recommending a change; measures stated workload/hardware and numerical parity. |
| S2 | "Implement a tiny JAX autoregressive generation example using a KV cache and establish that cached generation agrees with full-prefix generation." | Explicit prefill/decode, masks/positions/capacity, cache state and termination; full/cached logits and greedy parity; seeded sampling and padding checks; no claimed real-LLM correctness from only a toy fixture. |
| S3 | "A non-learning JAX simulation recompiles for different scalar inputs. How should I investigate and fix it?" | Correct tracing/static-versus-dynamic reasoning, observed recompilation evidence and output parity; no imposed training or Bayesian inference workflow. |

- [ ] **Step 2: Author the entry point and profiling/sharding references.**

Initial frontmatter:

```yaml
---
name: optimize-jax
description: >
  Use when JAX code has tracing errors, unexpected recompilation, memory
  pressure, slow execution, or distributed placement problems, or when
  improving inference and generation — including profiling, precision,
  sharding, asynchronous timing, prefill/decode, and KV caches.
license: MIT
metadata:
  author: Lowell Mason
---
```

Main output contract: reproduce the execution problem → establish a workload
and correct reference → separate compile/runtime/transfer costs → profile →
change one measured cause → check outputs/gradients and resource/performance
effects → report hardware, workload, results and limits.

`profiling.md` covers traced/static values, PyTrees/NNX state, shape buckets,
compilation, transfers, vectorization/loops, rematerialization, precision and
memory. `jax-timing` compiles a small JAX function, synchronizes before reading
timers, records compile and warm timings separately, and checks equivalent
outputs. It has no assertion that a tiny CPU optimization must be faster.

`sharding.md` explains mesh/partition/placement contracts and distributed
model/optimizer/checkpoint state using the resolved JAX APIs and primary docs.
A one-device CPU demonstration is labeled as such; do not call it multi-host
verification. Mark any actual multi-host/accelerator recipe with the explicit
reason it cannot run in the CPU gate.

- [ ] **Step 3: Author and execute the generation reference.**

`inference.md` starts with JAX-native research generation. `cached-decode`
implements tiny causal attention with fixed cache arrays, explicit positions
and valid lengths, prefill and decode state, capacity checks, and EOS/termination.
Its independent full-prefix reference verifies logits and greedy tokens across
several prompt lengths and padding patterns; fixed-key sampling reproduces its
own result. Cover zero/short/near-capacity boundaries and prevent cache writes
beyond capacity. This is a cache/math fixture, not evidence that an arbitrary
converted pretrained checkpoint is correct.

Document supported Tunix generation and optional MaxText scale paths through
primary sources, with model conversion/logit parity and hardware prerequisites.
Do not introduce a default PyTorch model execution path or a production hosting
workflow.

```bash
uv run --python 3.13 python build/check_snippets.py skills/optimize-jax/
JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/optimize-jax/
```

Expected: parse/execution exit 0; both required IDs and every selected CPU
example pass. Record actual timings, environment and hashes without promising
speed on other devices.

- [ ] **Step 4: Run WITH-skill micro/application and retrieval checks.**

Use matched S1 conditions for five candidate samples, plus fresh S2/S3
applications. Ask a retrieval question distinguishing a loss/convergence problem
from a cache/recompilation problem. Read and score actual outputs, refine the
guidance from failures, and rerun affected numerical/application checks.

- [ ] **Step 5: Complete attribution/docs and commit.**

Append `optimize-jax/` to NOTICE and its bare name to CLAUDE.md's originals
list; recompute the written count from NOTICE (one additional original in this
task). Add the README original credit and row:

```markdown
| [`optimize-jax`](skills/optimize-jax/) | Reproduce, profile, and improve JAX execution: tracing, compilation, memory, precision, sharding, and generation/cache performance, with measured changes and correctness parity. |
```

Finalize the Orchestra inspiration paragraph for all three original skills;
describe inspiration by reference only when no third-party text/code was
reproduced. Preserve the Bayesian attribution and original license inventory.
Run frontmatter/provenance, parse and dependency-drift checks. Commit this skill,
evidence and docs with message `feat(skills): add verified JAX optimization and inference`.

**Checkpoint:** All three skills are individually verified. Performance claims
have measured workloads, and generation guidance has a tested cache contract.

### Task 5: Narrow Bayesian discovery and verify the catalog boundaries

**Files:** Modify only the description in `skills/bayesian-workflow/SKILL.md`;
create `specs/verification/32-bayesian-routing.md`.

**Interfaces:**
- Consumes the complete three-skill catalog, R7, and the existing Bayesian
  description. Produces a minimally narrowed description and routing evidence.
- Preserve `NumPyro (JAX)`, BlackJAX, MCMC/NUTS, posterior terminology, and the
  Bayesian body/license/metadata. No Bayesian precision policy is generalized.

- [ ] **Step 1: Run the current-description selection baseline.**

Use a realistic full catalog with the current Bayesian description and the new
three descriptions. In fresh contexts ask which guidance to load, then let the
agent retrieve it and explain the choice. Use at least five samples per
current/candidate condition for these prompt families:

1. "Train an NNX sequence model in JAX using synthetic data."
2. "Compare neural checkpoints trained with different budgets and seeds."
3. "Fix recompilation in a non-learning JAX calculation."
4. "Infer a Bayesian neural-network posterior with NumPyro and NUTS."
5. "Use BlackJAX to sample a posterior distribution."
6. "Improve generation speed while checking KV-cache correctness."

Expected primary choices, withheld from test context: deep-learning, evaluation,
optimization, Bayesian, Bayesian, optimization respectively. Record actual
selected/read skills, rationale, and whether a runtime's real auto-loading was
observed or this was a catalog-selection simulation. Do not call a literal
substring test or `build/smoke_test.py` a routing test.

- [ ] **Step 2: Apply the approved minimal textual narrowing.**

Replace this exact description substring:

```text
Pyro, JAX, BlackJAX, ArviZ, InferenceData
```

with:

```text
Pyro, BlackJAX, ArviZ, InferenceData
```

This removes only the standalone JAX trigger; `NumPyro (JAX)` still identifies
the Bayesian stack. If controls already choose correctly, record that result:
the approved spec still narrows the textual trigger, but there is no measured
over-trigger improvement to claim. Add no larger wording rule without an
observed gap and the authoring gate.

- [ ] **Step 3: Repeat matched candidate selection and compatibility checks.**

Run the same prompt families against the edited catalog, five fresh samples
each. Read every output, verify preservation of posterior discovery and absence
of Bayesian loading solely from bare JAX in ordinary neural/execution work.
If selection still fails, isolate the conflicting trigger before proposing a
broader change; record any necessary spec deviation explicitly.

Run frontmatter lint and the parse gate for `skills/bayesian-workflow/`. No body
or executable Bayesian example changed, so a full MCMC snippet run is not needed
for this metadata edit. Commit the description and evidence with message
`fix(skills): narrow Bayesian JAX discovery trigger`.

**Checkpoint:** Catalog tests distinguish learning, evaluation, execution, and
actual posterior inference, with honest limits on auto-loading evidence.

### Task 6: Verify installation and cross-skill integration, then complete the plan

**Files:** Create `specs/verification/32-jax-integration.md`. Modify the completed
skill/docs files only for failures found at this gate. Completion markup and
retirement follow the existing plan protocol, after final reviews resolve.

**Interfaces:**
- Consumes the three individually verified skills, routing evidence and CPU
  profile. Produces a final integration/check report and reviewable branch.
- The integration does not add installer registration or library-specific
  runtime adapters. Installation uses a temporary destination, not global skill
  directories or runtime settings.

- [ ] **Step 1: Check spec coverage and evidence completeness.**

| Spec requirement | Implementation/verification |
|---|---|
| R1 | Tasks 2–4: exactly three entry points, body/description budgets, main-context guidance, own references and bare handoffs. |
| R2 | Task 2: shared NNX training, masks/state/RNG, tiny-data checks, complete recovery and dtype/device policy. |
| R3 | Task 2: all six domain areas and justified native framework paths. |
| R4 | Task 2: supported LLM loading, masks/objectives/reference/trainable state, and real-checkpoint/hardware limits. |
| R5 | Task 3: comparable evaluation, domain checks and a neural-run record without posterior artifacts. |
| R6 | Task 4: measured execution, compilation/synchronization/memory/sharding and tested cache generation. |
| R7 | Tasks 2–5: conditional handoffs, Bayesian trigger, intact Bayesian ledger, no private dependency omissions. |
| R8 | Tasks 2–4: original guidance, NOTICE/CLAUDE/README inventories and source/license attribution. |
| Acceptance | Task 1's execution gate, each skill's application evidence, matched catalog routing, pins/environment/hashes, all final checks. |

Verify every required example ID is present and has a passing run. Read the
evidence, not only its verdict, and keep claims proportional to CPU/toy versus
real checkpoint/accelerator coverage. Count the original skills against NOTICE
and confirm CLAUDE.md's written count matches; keep that bullet single-line for
the existing parser. Check local reference links and that a domain not mentioned in a primary
description can still be retrieved from its main body.

- [ ] **Step 2: Run final build and execution checks.**

From the execution checkout root:

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
uv run --python 3.13 python build/check_snippets.py skills/
uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check
JAX_PLATFORMS=cpu uv run --python 3.13 --with-requirements specs/verification/32-jax-cpu.txt python build/check_jax_examples.py skills/deep-learning/ skills/evaluate-deep-learning/ skills/optimize-jax/
git diff --check
```

From working directory `build/`:

```bash
uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py test_check_jax_examples.py
```

Expected: exit 0 for every check; all selected CPU examples pass, eight new
runner tests pass, runtime-support/dependency tests remain green, and the
adapter generator reports no drift. Existing documented parse advisories remain
advisories, not evidence that an unexecuted hardware recipe ran. Do not run
repo-root pytest or unrelated citation/PDF-ground-truth suites for this change.

- [ ] **Step 3: Check installer discovery in an empty temporary destination.**

Run this dry run from the root:

```bash
task_jax_install_home=$(mktemp -d)
uv run --python 3.13 python install.py all --home "$task_jax_install_home" --no-companions --dry-run --skill deep-learning --skill evaluate-deep-learning --skill optimize-jax
```

Expected: six `would link` entries (three Claude and three shared Codex/Gemini
destinations), no companion installation, and no invented extra dependencies.
Inspect targets, then remove the empty temporary directory with `rmdir`.
Record the dry run and check outputs in the integration record.

- [ ] **Step 4: Resolve reviews and commit the integration report.**

Use the chosen execution skill's per-task and final whole-branch review gates,
including its read-only Codex second opinion where required. Give reviewers the
spec and actual diff/evidence; do not replace checks with an implementer's
success report. Reproduce and resolve actionable failures, rerun affected gates,
and report any actual deviation. Commit the final record with message
`test(skills): verify JAX skill integration`.

- [ ] **Step 5: Apply the existing completion and branch-integration protocols.**

Use `writing-plans`' Plan Completion Protocol after required tasks/reviews are
complete: resolve questions before deferring, mark completed/deviated steps,
update only genuinely relevant deferred items, report/triage backlog health,
and retire this plan and its spec if no other live plan shares the spec.
Preserve verification evidence and repair moved relative links. Do not tick
the DL/NLP methodology-template item merely because these skills now exist.

Then use `finishing-a-development-branch` to choose integration and clean up the
execution worktree. The plan does not preauthorize publishing, merging, or
discarding unrelated changes. Follow authorization already provided in the
execution session for those actions.

**Checkpoint:** All required work is verified and review findings are resolved;
remaining work, if any, follows the explicit completion gate rather than being
silently omitted.

## Planning Verification

On 2026-10-03, the plan's Python fences passed the repository parse gate. Its
runner/test source was extracted unchanged into temporary files and checked
with Python 3.13.8 and pytest: RED was the expected missing-module collection
failure; after adding the proposed runner, GREEN was **8 passed**. This verifies
the planned runner's process contracts, not the future JAX examples or skills.
Those implementation/application gates remain the tasks above. The spec-coverage
matrix, interface names, local paths and placeholder scan were reviewed before
the planning commit.

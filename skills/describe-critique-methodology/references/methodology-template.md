# Methodology description templates

Two shapes. Choose in Describe mode step 1: **module** for one estimand and
one procedure; **system** when components compose. Every slot is REQUIRED —
write "None known." rather than omitting a slot. The output is math and
prose: symbols come from the notation table, never from the code. If you
catch yourself typing a function, file, class, or variable name from the
codebase, define a symbol for the concept in the notation table and use the
symbol. Symbols are mathematical notation or role-names — a snake_case,
camelCase, or dotted name lifted from the code does not become notation by
being defined in the table; rename the concept (subscripted single letters
and Greek bases are fine).

## Module template

```markdown
# <System> — <Module role> methodology

> For agentic workers: when specs/<name>-critique.md exists beside this
> file, REQUIRED SKILL: describe-critique-methodology (synthesize mode) —
> do not draft a spec directly.

## Notation
| Symbol | Meaning | Domain / units |
|---|---|---|
Every symbol used anywhere below is defined here, in-document.

## Problem formulation and data-generating story
What is observed, what is latent, and what generates the data — as random
variables and distributions. State the estimand explicitly.

## Estimation / inference procedure
The procedure in math: model equations, likelihood, priors (if Bayesian),
and the inference algorithm described AS an algorithm — never as a library
call.

## Assumptions and limitations
Numbered. Each assumption states what breaks if it fails.

## Evaluation criteria
How the method's output is judged: metrics, benchmarks, calibration checks,
holdout design — as criteria, not as a test-file inventory.

## Open questions for the reviewer
Numbered questions addressed to the external reviewer — the places you want
the critique to push.
```

## System template

```markdown
# <System> methodology

> For agentic workers: when specs/<name>-critique.md exists beside this
> file, REQUIRED SKILL: describe-critique-methodology (synthesize mode) —
> do not draft a spec directly.

## Component inventory
| Component (by methodological role) | Estimand / output | Consumes |
|---|---|---|
Roles, never package or module names: "private-sector state-space nowcast
leg", not a directory name.

## Composition
How component outputs combine, as math on random variables and estimates
(additive decomposition, convolution of predictive densities,
reconciliation, ...).

## Cross-component assumptions
The assumptions that live BETWEEN components — independence, shared units,
vintage/timing alignment — the ones no single component states.

## Notation
Shared table for the composition math (per-component sections may extend
it).

## Per-component descriptions
One section per component, each following the module template's slots.

## Open questions for the reviewer
```

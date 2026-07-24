# General (G5, G19, G23, G28, G29, G36)

The cross-cutting judgment rules, with the two stack caveats that keep this
catalog from "fixing" idiomatic Polars and JAX.

## G5 — Duplication (DRY), with the rule of three

Two copies is not yet duplication — it is two data points about a shape you
do not fully know. Extract on the **third** occurrence, when the true
signature has revealed itself. Extracting at two builds the wrong abstraction
and you will bend it at three anyway (premature abstraction costs more than
one repeat). Copy-paste of a whole *module* is never opportunistic-fix
material — that is a tech-debt finding (see the clean-coder skill's
boundary).

## G19 — Explanatory variables

Name the intermediate. In Polars, name the *expression*:

```python
# Bad — the condition is a riddle
df = df.filter(pl.col('footnote').eq('P').or_(pl.col('value').is_null()).not_())

# Good — the business rule has a name
is_unusable = pl.col('footnote').eq('P').or_(pl.col('value').is_null())
df = df.filter(is_unusable.not_())
```

## G23 — Dispatch over if/elif chains (JAX caveat)

Martin's rule says "prefer polymorphism to if/else" and assumes OO dispatch.
In traced JAX you often *cannot* branch on a traced value with a Python `if`
at all; the idiomatic dispatch is `jax.lax.switch` / `jax.lax.cond`, and for
tabular logic a Polars `when/then/otherwise`. The rule survives in spirit —
replace long conditional chains with a dispatch mechanism — but the mechanism
here is functional, not a class hierarchy. Do not introduce classes to
satisfy G23.

```python
# G23 in spirit, JAX-idiomatic (not OO polymorphism)
step_fn = jax.lax.switch(regime_index, [low_fn, mid_fn, high_fn], state)
```

```python
# Tabular dispatch — Polars when/then, not a Python if/elif over rows
df = df.with_columns(
    pl.when(pl.col('period').eq('M13')).then(None)
    .otherwise(pl.col('value'))
    .alias('monthly_value')
)
```

## G25 — Named constants (mostly ruff's job; the judgment slice)

ruff `PLR2004` flags magic comparisons mechanically. The judgment slice is
*which name*: the domain's name, not the number's.

```python
# Bad
if resp.status_code == 429:
    ...

# Good — plain-int comparison; == is correct here (method-style .eq() is
# for Polars expressions, not Python ints)
HTTP_TOO_MANY_REQUESTS = 429
if resp.status_code == HTTP_TOO_MANY_REQUESTS:
    ...
```

## G28 — Encapsulate conditionals

```python
# Bad
if resp.status_code == 429 or resp.status_code >= 500:
    ...

# Good
def is_retryable(resp):
    return resp.status_code == HTTP_TOO_MANY_REQUESTS or resp.status_code >= 500
```

## G29 — Avoid negative conditionals

`if is_complete:` reads; `if not is_incomplete:` gets misread under
maintenance. When a negation keeps appearing, name the positive
(`has_all_periods = ...`) and branch on that.

## G36 — Law of Demeter (Polars caveat — read before "fixing" a chain)

G36 targets **transitive navigation through distinct collaborator objects**
(`order.customer.address.zip`) — code that couples itself to the structure of
three objects it does not own. A Polars expression chain is the opposite: a
**fluent builder on one lazy object** returning the same type at every step.
It hides structure. It is idiomatic, and it is NOT a Demeter violation —
never break one apart to "fix" G36:

```python
# Good — idiomatic lazy Polars; NOT a Demeter violation
result = (
    lf
    .filter(pl.col('series_id').eq(target_id))
    .group_by('year')
    .agg(pl.col('value').mean().alias('mean_value'))
    .sort('year')
    .collect()
)
```

The G36 smell in this stack looks like reaching through config/client
internals instead: `client._transport._pool._connections` — structure you do
not own, exposed. That is the thing to fix.

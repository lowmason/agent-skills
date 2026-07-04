# Reporting template — `recommendation.md`

Every full run writes `<slug>/recommendation.md` from this template. It is both the human-facing
memo **and** the handoff interface (§6 is the C4 payload `bayesian-workflow` needs to start cold).
Keep section order fixed — it is the audit trail. Fill every section; write "n/a — <why>" rather
than deleting one.

---

```markdown
# Recommendation: <problem slug>

## 1. Problem framing
- **Task type:** <regression / classification / counts / clustering / dim-reduction / time-series / structured / decision>
- **The question being asked:** <point prediction | uncertainty / inference | causal | sequential decision>
- **Decision driver:** <one line — what the answer will be used for>

## 2. Data characterization
- **Primary data:** <n rows, n predictors, target type>. Key signals (from `characterize.py` /
  `explore-data`): <overdispersion, zero-fraction, n/p, class balance, missingness, panel/time structure>.
- **External / auxiliary information:** <official statistics, benchmarks, related series, domain
  constraints> → <how each could inform a prior / pooling target / covariate / constraint>.

## 3. Candidate methods
| Method | Why a candidate | Key assumption | Trade-off |
|--------|-----------------|----------------|-----------|
| <A> | <fits signal X> | <…> | <…> |
| <B> | <…> | <…> | <…> |
| <C> | <…> | <…> | <…> |

## 4. Recommendation
- **Recommended:** <method> — **because** <the grounded reason, tied to §2 signals>.
- **Explicit assumptions:** <what must hold>.
- **What would change this:** <the signal that would flip the choice>.

## 5. Regularization & model selection
- **Complexity knobs (family-specific):** <# factors / K components / kernel+ARD / sparsity prior /
  structure penalty / partial pooling>.
- **Selection criterion to use:** <CV / IC / LOO-ELPD> — <one line why>.
- (Pre-fit specification only; post-fit LOO/ELPD comparison is `bayesian-workflow`'s job.)

## 6. Specification for handoff (C4)
For a Bayesian recommendation, carry all four so the next skill starts cold:
- **Likelihood family:** <e.g. NegativeBinomial2(mean, concentration)>
- **Candidate priors:** <per parameter; note any derived from official statistics / external data>
- **Structure:** <pooling / hierarchy / temporal / spatial>
- **Regularization & selection plan:** <from §5>

## 7. References (verified)
- PML: <PML1 §x.y — title; PML2 §x.y — title> (verified <date>)
- pyprobml: <notebooks/bookN/<nb>.ipynb>

## 8. Next steps / handoff
- **Runs next:** <bayesian-workflow | sklearn/other | drill-down>
- **Bracketing skills:** <explore-data upstream; validate-data downstream>
- **Open questions:** <what to resolve before/while fitting>
```

---

## Notes for the author

- §6 is non-negotiable for a Bayesian handoff — a memo missing the likelihood family, priors, or
  structure forces `bayesian-workflow` to re-derive them. That is the interface this skill exists to provide.
- §7 citations must be **verified** (Gate A + Gate B) before they ship — never paste a §ref from memory.
- For a non-technical audience, add a one-paragraph plain-language summary above §1 and a short
  glossary after §8, but keep the canonical sections intact as the audit trail.

# Deferred items

## 11-delegation-frontmatter-rollout — 2026-07-19
- [ ] Haiku-pinned `Explore` override agent (fork-isolation upgrade; plan "Out of
      scope"): the direct `model: haiku` pins on `explore-data`/`bls-data-context`
      only cover the *invoking* turn (a skill `model` override is per-turn). A single
      haiku-pinned `agents/Explore.md` would keep a whole multi-turn profiling
      workflow on Haiku via `context: fork` + `agent: Explore`, and double as a global
      Explore→Haiku lever. Add only if the per-turn saving proves insufficient; needs
      a new agent file + a README Agents-table row.
- [ ] Interactive verification (plan Task 5 Steps 3–4, deviation): confirm the live
      model/effort indicator shows haiku/xhigh when the pinned skills load, and take a
      `/status` before/after cost reading on one exploration-heavy session. Could not
      run in the non-interactive execution flow; the enforceable lints/tests passed.
      Run in a normal interactive session — no code needed.
- [ ] Opt-ins decided against but available (one-line frontmatter adds if revisited):
      `effort: high` on `recommend-probabilistic-model`/`recommend-visualization`
      (no-op at the default `high`); `model: opus` on `bayesian-workflow` (would
      override its fresh-session model choice); `model: haiku` on `validate-data`
      (deliberately excluded — judgment-heavy ship-gate). See
      specs/completed/delegation-frontmatter-rollout.md Req 3/Req 5.

## 12-audit_7_20_26 — 2026-07-20
- [ ] Deep-ensembles notebook mispairing (final-review Minor (h), gate-batch deferred):
      `skills/recommend-probabilistic-model/references/families/classification.md`'s
      "Deep ensembles" row cites `PML2 §17.3.9` (a Bayesian-NN posterior-approximation
      topic) but links `notebooks/book1/18/bagging_trees.ipynb`, a decision-tree bagging
      notebook reused verbatim from the "Random forest / bagging" row above. Same defect
      class as C7; Gate A cannot catch it because the path resolves. A pyprobml sweep
      (`bnn|dropout|deep_ens`) found no dedicated deep-ensembles notebook — nearest are
      `book2/17/mnist_classification_mc_dropout.ipynb` (§17.3.1) and
      `book2/19/bnn_mnist_sgld_*.ipynb`. Needs the same deliberate judgment call C7 got:
      substitute a near-neighbour and label it a stand-in, or drop the link and let the
      §-ref carry the row. Pre-existing, not introduced by this plan.
- [ ] Snippet-execution gate for `bayesian-workflow` (audit Theme 1; offered at the
      completion gate, not selected): `skills/bayesian-workflow/SKILL.md:59` promises "the
      modern ArviZ >= 1.0 stack" and no gate enforces it. C1, C2 and D2 were all executable
      or API claims that went stale silently — C1's *mandatory* recipe raised on the exact
      declared stack. `build/verify_citations.py` proves this repo will mechanize a
      correctness check when the artifact is a §-ref; nothing equivalent guards inline code.
      Would have caught all three before review. Needs a runner that extracts fenced python
      from the skill and executes it against pinned deps.
- [ ] `PML2 §2.2.1.4` chapter-fallback WARN (offered at the completion gate, not selected):
      Gate A exits 0 but emits a standing WARN on this ref every run. Gate B verified it is
      a false alarm — the section exists ("Negative binomial distribution") and substantiates
      both claims attached to it; the WARN is an artifact of `build/.scratch/book2_sections.tsv`
      truncating at three nesting levels, so it holds `2.2.1` but no `2.2.1.x`. Either record
      it as a known-good exception or deepen `build/extract_structure.py`'s nesting. Until
      then it draws review attention on every pass.
- [ ] QCEW datatype-05 label unverified (final-review Minor (f), partially resolved):
      the hub's claim that datatype 05 is "average annual pay" was dropped to the verified
      "its annual-only datatype carries `A01`" (period structure confirmed live via BLS API
      v1: `ENUUS00050010` returns only `A01`). The *label* remains unconfirmed because
      `download.bls.gov` returns 403 from this environment and `references/qcew.md` documents
      no datatype codes. Restore the specific label once BLS is reachable, or add a datatype
      table to `qcew.md` so the hub has a quotable line to derive from.

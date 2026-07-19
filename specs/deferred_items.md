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

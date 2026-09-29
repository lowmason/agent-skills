# skill model-pin removal — Design Spec

**Status: COMPLETE (2026-09-28)** — implemented by plan 31 (`specs/plans/completed/31-skill-model-pin-removal.md`) and retired here. Design approved 2026-09-28 in a brainstorming pass opened by the
2026-09-28 `/deferred` triage (disposition D1). Closes
`specs/deferred_items.md` § `11-delegation-frontmatter-rollout` — the open "interactive
verification" item (the live model/effort indicator check, 71 days old at triage).

Remove the four `model: haiku` skill pins that plan 11 shipped, correct the two documents
that say such pins work, and make `build/check_frontmatter.py` reject the pin so it cannot
be re-added on the strength of the docs alone. Goal chosen by the owner: a **truthful
config**, not Haiku savings — plan 11 already called these pins "a modest, per-turn cost
trim, not the main cost lever" (`specs/completed/delegation-frontmatter-rollout.md`), and
Haiku search routing already exists through the `Explore` agent.

## Motivation — the pins never apply here

Plan 11 (2026-07-19) added `model: haiku` to `bls-data-context` and `explore-data`;
`classification-codes` and `geographic-codes` were created with the same pin on 2026-09-02.
Plan 11 verified the field against the documentation only and deferred the live check,
which stayed open for 71 days. The 2026-09-28 check read session transcripts instead of the
live indicator, and found that the pins have never been observed to run:

- **0 of 26 informative loads ran on Haiku** (Claude Code 2.1.219–2.1.281; 23 Skill-tool
  loads and 3 slash loads; main, subagent and workflow contexts; desktop, CLI, VS Code).
  Their windows hold 392 distinct assistant API calls: 328 Opus, 47 Sonnet, 17 Fable,
  0 Haiku. The first call after each load stayed on the session's model, 26 of 26.
- **The harness records the pin and then drops it.** On 20 of the 26 loads the
  `tool_result` or a `command_permissions` attachment carries
  `model: claude-haiku-4-5-20251001`; the next reply is served by the session model.
  `message.model` is the model the API actually served (it matched `resolvedModel` 308 of
  308 times).
- **Every load with a recorded permission mode was in auto mode** (12 of 12; the rest are
  unrecorded, mostly subagents). `~/.claude/settings.json` sets
  `permissions.defaultMode: "auto"`.
- **The documented cause** (Claude Code skills docs, via the claude-code-guide research
  pass): in auto mode, a skill `model` that auto mode does not support is not used and the
  session keeps its current model. Auto mode does not support Haiku. The 2.1.259 changelog
  made this explicit for skills and commands ("the turn now keeps the session model").
- **Subagent pins are unaffected.** `test-runner` and `Explore` ran on Haiku from
  auto-mode parents; `code-reviewer`'s `effort: xhigh` held in 41 of 41 spawns under a
  max-effort parent.

The transcript-sweep scripts and tables were written to `/tmp/d1probe/` (ephemeral, not
committed); the figures above are the durable record.

## Decisions

1. **Remove, don't reroute.** The alternative — `context: fork` with a Haiku-pinned agent,
   the only route that reaches Haiku under auto mode — is rejected for these four skills.
   `skills/writing-skills/SKILL.md:104` forbids forking guidance skills and skills that mix
   an artifact with question-answering: the three code/context skills are guidance the main
   thread must hold, and `explore-data` mixes a profile artifact with guidance. Keeping the
   pins "for non-auto sessions" is rejected too: that behaviour is unverified, and the
   owner's default mode is auto.
2. **Guard with a failing lint, not a warning or docs alone.** Docs alone is what let plan
   11 ship the pins. The lint already fails a `context:` value that "silently no-ops at
   runtime" (`CONTEXT_VALUES`, `build/check_frontmatter.py:27-30`); an inert `model: haiku`
   is the same class of defect.
3. **Reject only what auto mode cannot run.** `model: opus`, `sonnet` and `fable` are
   documented to apply in auto mode (not observed here: every skill pin in this repo is
   Haiku, so the transcript sweep saw no other) and stay allowed. `agents/*.md` are exempt: subagent Haiku pins work.

## Requirements

- **R1 — Remove the pins.** Delete the `model: haiku` line from the frontmatter of
  `skills/bls-data-context/SKILL.md`, `skills/classification-codes/SKILL.md`,
  `skills/explore-data/SKILL.md` and `skills/geographic-codes/SKILL.md`. No skill body
  refers to its own model tier, so nothing else in these files changes.
- **R2 — Lint rule.** `build/check_frontmatter.py` fails a `SKILL.md` (`check_skill`) or a
  `commands/*.md` (`check_command_file`) whose `model:` is `haiku` or any `claude-haiku-*`
  model ID, compared case-insensitively. The message states that auto mode drops a Haiku
  skill or command model and keeps the session model, says to put cheap work on a
  model-pinned subagent instead, and names this spec. Define the rejected set as a module
  constant beside `CONTEXT_VALUES`, with a comment giving the same "silently no-ops at
  runtime" rationale. `agents/*.md` are not checked by this rule.
- **R3 — Tests** in `build/test_check_frontmatter.py`:
  - a skill with `model: haiku` fails with the R2 message;
  - a skill with `model: claude-haiku-4-5-20251001` fails;
  - a command file with `model: haiku` fails;
  - a skill with `model: sonnet` passes;
  - the existing `test_model_and_effort_keys_allowed` fixture changes from `model: haiku`
    to `model: sonnet`, so it keeps testing that the keys are allowed;
  - `test_real_repo_is_clean` is the natural RED step: once R2 lands it fails on the four
    real skill pins until R1 deletes them. It walks `skills/` only;
    `test_real_agents_and_commands_are_clean` covers the agent exemption, since
    `agents/explore.md` and `agents/test-runner.md` carry `model: haiku` and must stay
    clean, and the command half of R2 on the real repo.
- **R4 — Correct the docs.**
  - `skills/writing-skills/SKILL.md:103`: after "(per-skill overrides for the model tier
    and reasoning effort a skill runs at)", add that a `model` the session's permission
    mode cannot run — Haiku under auto mode — is silently dropped, and that cheap work
    belongs on a model-pinned subagent. This line is a local addition (audit 12), not
    superpowers text, so `NOTICE` is unaffected. It is reference content inside the
    meta-skill, so no behavioural micro-test is required.
  - `specs/claude-code-customization-guide.md:82` (`model` / `effort` row): add a ⚠
    noting that in auto mode a skill `model` auto mode does not support (Haiku) is ignored
    and the session model runs, observed on 2.1.219–2.1.281.
- **R5 — Close item 11.** The plan's completion protocol ticks
  `11-delegation-frontmatter-rollout`'s open interactive-verification item as done, citing
  this spec: the indicator check is superseded by the transcript evidence above, which
  answered the question it asked. The aged-backlog acknowledgements that name item 11 are
  history and are not edited.

## Verification

- `cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py`
  — RED on `test_real_repo_is_clean` after R2 and before R1; GREEN after R1.
- `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` exits 0.
- `uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check` still
  passes (skills are not processed by the adapter generator; this guards against an
  accidental agent edit).
- The dependency-drift check from the root `CLAUDE.md` Commands block passes (no
  cross-skill references change).
- `grep -rn '^model: haiku' skills/*/SKILL.md commands/*.md` returns nothing.

## Out of scope

- **The two `effort: xhigh` skill pins** (`bayesian-workflow`, `tune-hyperparameters`).
  Auto mode does not restrict effort, and their rationale (effort composes with a Sonnet
  session) still holds. Evidence is split, one informative case each way: on 2.1.266 a load
  moved a max-effort session to xhigh for the rest of the turn — the pin can *lower* effort
  as well as raise it — and on 2.1.281 a load left it at max. On the owner's current default
  (Opus 5.5 with a persisted `effortLevel: "xhigh"`) both pins are no-ops. Revisit if: the
  session default moves off xhigh, or a skill turn is seen running at a lower effort than
  its session because of a pin.
- **Agent model and effort pins** — observed to apply; unchanged.
- **Routing any of these skills through `context: fork`** — rejected in Decision 1.
- **The owner's global `~/.claude/CLAUDE.md`**, whose Model routing section still says
  "Opus at auto effort" although settings now persist xhigh. The owner's file; flagged, not
  edited.

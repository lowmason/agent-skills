# agent-skills

My personal collection of [agent skills](https://code.claude.com/docs/en/skills), primarily for **Claude Code**.

Each skill is a self-contained directory with a `SKILL.md` (plus any `references/` and `scripts/` it needs). Claude Code auto-discovers installed skills and loads one into context when it's relevant to what you're doing — or you can invoke it directly as a slash command.

## Skills

| Skill | Description |
|-------|-------------|
| [`bayesian-workflow`](bayesian-workflow/) | Opinionated Bayesian modeling workflow with NumPyro (JAX) and ArviZ. Encodes guardrails most agents skip — prior/posterior predictive checks, LOO-PIT calibration, prior-sensitivity checks, 94% HDI, non-centered parameterizations, reproducible PRNGKey seeds — and walks the full loop from formulating a model to reporting results. |

## Installation

These skills install into Claude Code's user-level skills directory, `~/.claude/skills/`, where they're discovered automatically.

First, clone the repo somewhere stable and make sure the skills directory exists:

```bash
git clone https://github.com/lowmason/agent-skills.git ~/agent-skills
mkdir -p ~/.claude/skills
```

Then install whichever skills you want, with **either** of these approaches.

### Symlink (recommended)

A symlink means edits in the repo are picked up live, without restarting Claude Code — ideal if you're tracking updates or hacking on the skill yourself:

```bash
ln -s ~/agent-skills/bayesian-workflow ~/.claude/skills/bayesian-workflow
```

### Copy

A copy gives you a frozen, self-contained install that won't change when the repo does:

```bash
cp -r ~/agent-skills/bayesian-workflow ~/.claude/skills/bayesian-workflow
```

### Project-level install (optional)

To make a skill available only inside one project (and shareable with collaborators via that repo), put it under the project's `.claude/skills/` instead of `~/.claude/skills/`:

```bash
mkdir -p .claude/skills
ln -s ~/agent-skills/bayesian-workflow .claude/skills/bayesian-workflow
```

### Verify

Inside Claude Code, run `/skills` to list discovered skills and confirm yours shows up (along with the level it loaded from). You can also invoke a skill by name, e.g. `/bayesian-workflow`.

## Credits

- **bayesian-workflow** — adapted from [Alexandre Andorra](https://alexandorra.github.io/)'s original **PyMC** Bayesian-workflow skill (MIT licensed). I ported it to **NumPyro + JAX** and expanded the visualization guidance.

## License

Licensing is noted per skill (see each skill's `SKILL.md`). `bayesian-workflow` is MIT.

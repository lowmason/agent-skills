# SKILL.md structure and Skill Discovery Optimization

Read this when you write a SKILL.md's frontmatter, lay out its body, or write or tighten its
description. The description rule itself stays in SKILL.md § Skill Discovery Optimization.

## SKILL.md Structure

**Frontmatter (YAML):**
- Three required fields: `name` and `description`, the Agent Skills spec's two (see [agentskills.io/specification](https://agentskills.io/specification) for all supported fields), and `license`, this repo's rule, enforced by `build/check_frontmatter.py`
- `description`: max 1024 characters — the Agent Skills spec cap, enforced by `build/check_frontmatter.py`. It applies to the description field, **not** to the whole frontmatter block; several shipped skills exceed 1024 chars of total frontmatter and pass the lint correctly.
- Optional keys the lint accepts: `compatibility`, `metadata`, `allowed-tools`, `when_to_use`, the two delegation keys `model` and `effort` (per-skill overrides for the model tier and reasoning effort a skill runs at; a Haiku `model` is not portable, since auto mode drops Haiku 4.5 and the `haiku` alias means Haiku 5.5 on the Anthropic API but 4.5 on other providers, so the lint fails it, and cheap work belongs on a model-pinned subagent), `context` (sole value `fork`: runs the skill in an isolated subagent, so the main session sees only what the skill returns), `agent` (the agent type a `context: fork` skill runs on), and `disable-model-invocation` (a YAML boolean; `true` makes the skill manual-only). Any other key fails `build/check_frontmatter.py`. The spec's own keys are `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`; the rest are Claude Code extensions, which a claude.ai upload or a spec-only validator rejects.
- Fork a skill whose value is a **verdict or artifact** you act on (`tech-debt` returns a prioritized backlog). Do **not** fork a skill whose value is **guidance** — it has to stay resident to shape what the main thread writes next — nor one that dispatches subagents itself, nor one with a mix of artifact and question-answering operations, since `context` is all-or-nothing per skill.
- `name`: Use letters, numbers, and hyphens only (no parentheses, special chars)
- `description`: Third-person, describes ONLY when to use (NOT what it does)
  - Start with "Use when..." to focus on triggering conditions
  - Include specific symptoms, situations, and contexts
  - **NEVER summarize the skill's process or workflow** (see SKILL.md § Skill Discovery Optimization for why)
  - Keep under 500 characters if possible

```markdown
---
name: Skill-Name-With-Hyphens
description: Use when [specific triggering conditions and symptoms]
license: MIT
---

# Skill Name

## Overview
What is this? Core principle in 1-2 sentences.

## When to Use
[Small inline flowchart IF decision non-obvious]

Bullet list with SYMPTOMS and use cases
When NOT to use

## Core Pattern (for techniques/patterns)
Before/after code comparison

## Quick Reference
Table or bullets for scanning common operations

## Implementation
Inline code for simple patterns
Link to file for heavy reference or reusable tools

## Common Mistakes
What goes wrong + fixes

## Real-World Impact (optional)
Concrete results
```

## Skill Discovery Optimization (SDO)

### 1. Rich Description Field

**Purpose:** Your agent reads the description to decide which skills to load for a given task. Make it answer: "Should I read this skill right now?"

```yaml
# ❌ BAD: Summarizes workflow - agents may follow this instead of reading skill
description: Use when executing plans - dispatches subagent per task with code review between tasks

# ❌ BAD: Too much process detail
description: Use for TDD - write test first, watch it fail, write minimal code, refactor

# ✅ GOOD: Just triggering conditions, no workflow summary
description: Use when executing implementation plans with independent tasks in the current session

# ✅ GOOD: Triggering conditions only
description: Use when implementing any feature or bugfix, before writing implementation code
```

**Content:**
- Use concrete triggers, symptoms, and situations that signal this skill applies
- Describe the *problem* (race conditions, inconsistent behavior) not *language-specific symptoms* (setTimeout, sleep)
- Keep triggers technology-agnostic unless the skill itself is technology-specific
- If skill is technology-specific, make that explicit in the trigger
- Write in third person (injected into system prompt)
- **NEVER summarize the skill's process or workflow**

```yaml
# ❌ BAD: Too abstract, vague, doesn't include when to use
description: For async testing

# ❌ BAD: First person
description: I can help you with async tests when they're flaky

# ❌ BAD: Mentions technology but skill isn't specific to it
description: Use when tests use setTimeout/sleep and are flaky

# ✅ GOOD: Starts with "Use when", describes problem, no workflow
description: Use when tests have race conditions, timing dependencies, or pass/fail inconsistently

# ✅ GOOD: Technology-specific skill with explicit trigger
description: Use when using React Router and handling authentication redirects
```

### 2. Keyword Coverage

Use words an agent would search for:
- Error messages: "Hook timed out", "ENOTEMPTY", "race condition"
- Symptoms: "flaky", "hanging", "zombie", "pollution"
- Synonyms: "timeout/hang/freeze", "cleanup/teardown/afterEach"
- Tools: Actual commands, library names, file types

### 3. Descriptive Naming

**Use active voice, verb-first:**
- ✅ `creating-skills` not `skill-creation`
- ✅ `condition-based-waiting` not `async-test-helpers`

### 4. Token Efficiency (Critical)

**Problem:** every installed skill's `description` is resident in EVERY conversation — that is the
cost you always pay. The SKILL.md body is paid only when the skill triggers, and `references/`
only when the body sends you there. Budget against the tier, not a single number.

**Targets by tier:**
- `description` (always resident): the hard cap is 1024 chars, enforced by
  `build/check_frontmatter.py`. Spend it on triggers, not prose — it is the only text that
  competes for context in conversations where the skill is never used. Codex also shortens
  descriptions once its skills listing passes its budget: with 105 skills listed, Codex 0.163 cut
  this repo's longer descriptions to 316–320 characters (2026-10-19; Codex 0.154 cut to 156–164
  with 93 listed, 2026-10-03). Re-measure with `codex debug prompt-input` from a directory outside
  any repo, reading its Skills list.
- SKILL.md body (loaded on trigger): keep it to the decision procedure. Observed range in this
  repo is roughly 450–4,000 words, median ~1,500 — length tracks how much irreducible procedure a skill
  carries, so treat a body pushing past ~2,000 words as a prompt to ask what belongs in
  `references/`, not as a violation.
- `references/*.md` (loaded on demand): no budget. This is where depth goes — `bayesian-workflow`
  carries 13 and `deep-learning` 8, keeping their bodies navigational.

**Techniques:**

**Move details to tool help:**
```bash
# ❌ BAD: Document all flags in SKILL.md
search-conversations supports --text, --both, --after DATE, --before DATE, --limit N

# ✅ GOOD: Reference --help
search-conversations supports multiple modes and filters. Run --help for details.
```

**Use cross-references:**
```markdown
# ❌ BAD: Repeat workflow details
When searching, dispatch subagent with template...
[20 lines of repeated instructions]

# ✅ GOOD: Reference other skill
Always use subagents (50-100x context savings). REQUIRED: Use [other-skill-name] for workflow.
```

**Compress examples:**
```markdown
# ❌ BAD: Verbose example (42 words)
your human partner: "How did we handle authentication errors in React Router before?"
You: I'll search past conversations for React Router authentication patterns.
[Dispatch subagent with search query: "React Router authentication error handling 401"]

# ✅ GOOD: Minimal example (20 words)
Partner: "How did we handle auth errors in React Router?"
You: Searching...
[Dispatch subagent → synthesis]
```

**Eliminate redundancy:**
- Don't repeat what's in cross-referenced skills
- Don't explain what's obvious from command
- Don't include multiple examples of same pattern

**Verification:**
```bash
wc -w skills/path/SKILL.md
# Body past ~2,000 words? Ask what should move to references/.
# The number that actually matters is the description's char count, capped at 1024:
uv run --with pyyaml python build/check_frontmatter.py
```

**Name by what you DO or core insight:**
- ✅ `condition-based-waiting` > `async-test-helpers`
- ✅ `using-skills` not `skill-usage`
- ✅ `flatten-with-flags` > `data-structure-refactoring`
- ✅ `root-cause-tracing` > `debugging-techniques`

**Gerunds (-ing) work well for processes:**
- `creating-skills`, `testing-skills`, `debugging-with-logs`
- Active, describes the action you're taking

### 5. Cross-Referencing Other Skills

**When writing documentation that references other skills:**

Use skill name only, with explicit requirement markers:
- ✅ Good: `**REQUIRED SUB-SKILL:** Use subagent-driven-development`
- ✅ Good: `**REQUIRED BACKGROUND:** You MUST understand writing-plans`
- ❌ Bad: `See skills/planning/writing-plans` (unclear if required)
- ❌ Bad: `@skills/planning/writing-plans/SKILL.md` (force-loads, burns context)

**Why no @ links:** `@` syntax force-loads files immediately, consuming 200k+ context before you need them.

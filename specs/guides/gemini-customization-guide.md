# Gemini CLI Customization & Architecture Guide

This guide details the extensibility framework for the Gemini CLI agent within this repository[cite: 1]. It provides a comprehensive map of how to define global context, orchestrate sub-agents, enforce security guardrails, and build complex, multi-modal skills tailored to your workflows[cite: 1].

## 1. Global Context & Rule Enforcement

The foundation of the agent's behavior is dictated by root-level configuration files and modular rule sets that inject context before any command is executed[cite: 1].

*   **`GEMINI.md`**: The primary system prompt extension[cite: 1]. Gemini automatically reads this file upon initialization in the repository[cite: 1]. Use this to define high-level architectural conventions, default communication styles, and strict operational boundaries[cite: 1].
*   **`rules/` Directory**: Modular, reusable instruction sets[cite: 1]. Instead of bloating `GEMINI.md`, compartmentalize domain-specific standards here[cite: 1].
    *   *Example*: `rules/clean-code-python.md` can be dynamically referenced by the agent when evaluating PRs or generating new Python modules[cite: 1].

## 2. Agent Personas (`agents/`)

The CLI supports specialized agent personas, allowing you to scope Gemini's focus and tool access to specific operational modes[cite: 1]. Global personas are defined as Markdown files in the root `agents/` directory[cite: 1]:

*   **`code-reviewer.md`**: Optimized for static analysis, PR reviews, and enforcing `rules/` constraints[cite: 1].
*   **`debugger.md`**: Configured for stack-trace analysis, log parsing, and iterative hypothesis testing[cite: 1].
*   **`docs-writer.md`**: Focused on AST parsing for docstring generation and maintaining `README.md` fidelity[cite: 1].
*   **`explore.md`**: An open-ended persona designed for codebase familiarization and dependency mapping[cite: 1].
*   **`security-auditor.md`**: Constrained to identify vulnerabilities, permission leaks, and dependency risks[cite: 1].
*   **`task-reviewer.md` & `test-runner.md`**: Used for QA loops and automated test suite execution[cite: 1].

## 3. The Skills Framework (`skills/`)

Skills are the most powerful extensibility mechanism in the repository, acting as domain-specific knowledge bases and toolchains that Gemini can retrieve dynamically[cite: 1]. Each skill is housed in its own subdirectory under `skills/`[cite: 1].

### Anatomy of a Skill
A fully realized skill (e.g., `bayesian-workflow`, `bls-data-context`, `classification-codes`) consists of[cite: 1]:
*   **`SKILL.md`**: The core instructional manifest[cite: 1]. It defines the skill's purpose, trigger conditions, and the exact steps Gemini must follow when executing it[cite: 1].
*   **`references/`**: Markdown files containing highly specific domain knowledge[cite: 1]. For example, `skills/bayesian-workflow/references/` contains deep dives into `diagnostics.md`, `jax-numerics.md`, and `state-space.md`[cite: 1].
*   **`scripts/`**: Executable Python or Shell scripts the agent can call to perform heavy lifting[cite: 1]. Examples include `diagnose_model.py` or `check_decoupling.py`[cite: 1]. 
*   **`data/`**: Static assets required for the skill[cite: 1]. For example, `skills/classification-codes/data/` contains mapping CSVs like `naics_2022.csv` and `soc_2018.csv`[cite: 1].

## 4. Runtime-Specific Overrides (`runtimes/gemini/`)

If a workflow requires Gemini to behave differently than the default global definitions, use the `runtimes/gemini/` directory[cite: 1]. 

*   **`runtimes/gemini/agents/*.md`**: Drop persona files here (e.g., `code-reviewer.md`) to completely override the global agent prompt with instructions explicitly tuned for Gemini's context window and reasoning style[cite: 1].
*   **`runtimes/gemini/commands/*.toml`**: Map specific CLI invocations to Gemini workflows[cite: 1]. TOML files here (e.g., `fix-issue.toml`, `license-audit.toml`) define the prompt templates, expected arguments, and target agents triggered by specific commands[cite: 1].

## 5. Security Guardrails & Hooks (`hooks/`)

To safely automate agentic workflows, the repository utilizes robust guardrails that intercept and validate agent actions before they affect the filesystem[cite: 1].

*   **`readonly-agent-guard.py` & `probe-readonly-guard.sh`**: Prevents "explore" or "auditor" agents from mutating the codebase during analysis phases[cite: 1].
*   **`uv-guard.sh`**: Ensures dependency management actions utilize the designated `uv` toolchain safely[cite: 1].
*   **`ruff-check.sh` & `ruff-fix.sh`**: Automatically intercept agent-generated Python code to enforce linting and formatting standards prior to commit[cite: 1].

## 6. Build & CI Integrity (`build/`)

Extend the `build/` directory with Python scripts to validate that agent-generated content adheres to repository structure[cite: 1].
*   **`check_frontmatter.py`**: Ensures all agent-generated documentation includes correct YAML frontmatter[cite: 1].
*   **`check_provenance.py` & `verify_citations.py`**: Validates that agent deliverables correctly cite their sources and maintain data lineage[cite: 1].
*   **`sync_runtime_assets.py`**: A utility to synchronize global prompts and runtime-specific overrides across the workspace[cite: 1].
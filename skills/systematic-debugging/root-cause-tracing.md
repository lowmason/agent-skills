# Root Cause Tracing

## Overview

Bugs often manifest deep in the call stack (git init in wrong directory, file created in wrong location, database opened with wrong path). Your instinct is to fix where the error appears, but that's treating a symptom.

**Core principle:** Trace backward through the call chain until you find the original trigger, then fix at the source.

## When to Use

```dot
digraph when_to_use {
    "Bug appears deep in stack?" [shape=diamond];
    "Can trace backwards?" [shape=diamond];
    "Fix at symptom point" [shape=box];
    "Trace to original trigger" [shape=box];
    "BETTER: Also add defense-in-depth" [shape=box];

    "Bug appears deep in stack?" -> "Can trace backwards?" [label="yes"];
    "Can trace backwards?" -> "Trace to original trigger" [label="yes"];
    "Can trace backwards?" -> "Fix at symptom point" [label="no - dead end"];
    "Trace to original trigger" -> "BETTER: Also add defense-in-depth";
}
```

**Use when:**
- Error happens deep in execution (not at entry point)
- Stack trace shows long call chain
- Unclear where invalid data originated
- Need to find which test/code triggers the problem

## The Tracing Process

### 1. Observe the Symptom
```
Error: git init failed in ~/project/packages/core
```

### 2. Find Immediate Cause
**What code directly causes this?**
```python
subprocess.run(["git", "init"], cwd=project_dir, check=True)
```

### 3. Ask: What Called This?
```python
WorktreeManager.create_session_worktree(project_dir, session_id)
  → called by Session.initialize_workspace()
  → called by Session.create()
  → called by test at Project.create()
```

### 4. Keep Tracing Up
**What value was passed?**
- `project_dir = ""` (empty string!)
- Empty string as `cwd` resolves to `os.getcwd()`
- That's the source code directory!

### 5. Find Original Trigger
**Where did empty string come from?**
```python
context = setup_core_test()  # returns {"temp_dir": ""}
Project.create("name", context["temp_dir"])  # read before the fixture populated it!
```

## Adding Stack Traces

When you can't trace manually, add instrumentation:

```python
# Before the problematic operation
def git_init(directory):
    stack = "".join(traceback.format_stack())
    print(
        "DEBUG git init:",
        {"directory": directory, "cwd": os.getcwd(),
         "test": os.environ.get("PYTEST_CURRENT_TEST"), "stack": stack},
        file=sys.stderr,
    )
    subprocess.run(["git", "init"], cwd=directory, check=True)
```

**Critical:** Print to `sys.stderr` and run `pytest -s` — pytest captures stdout/stderr otherwise, and a configured logger may be filtered out

**Run and capture:**
```bash
pytest -s 2>&1 | grep 'DEBUG git init'
```

**Analyze stack traces:**
- Look for test file names
- Find the line number triggering the call
- Identify the pattern (same test? same parameter?)

## Finding Which Test Causes Pollution

If something appears during tests but you don't know which test:

Use the bisection script `find-polluter.sh` in this directory:

```bash
./find-polluter.sh '.git' '*/test_*.py'
```

Runs tests one-by-one, stops at first polluter. See script for usage.

## Real Example: Empty project_dir

**Symptom:** `.git` created in `packages/core/` (source code)

**Trace chain:**
1. `git init` runs in `os.getcwd()` ← empty cwd parameter
2. WorktreeManager called with empty project_dir
3. Session.create() passed empty string
4. Test read `context.temp_dir` before the fixture populated it
5. setup_core_test() returns `{"temp_dir": ""}` initially

**Root cause:** Top-level variable initialization accessing empty value

**Fix:** Made temp_dir a property that raises if read before the fixture runs

**Also added defense-in-depth:**
- Layer 1: Project.create() validates directory
- Layer 2: WorkspaceManager validates not empty
- Layer 3: test-context guard refuses git init outside tmpdir
- Layer 4: Stack trace logging before git init

## Key Principle

```dot
digraph principle {
    "Found immediate cause" [shape=ellipse];
    "Can trace one level up?" [shape=diamond];
    "Trace backwards" [shape=box];
    "Is this the source?" [shape=diamond];
    "Fix at source" [shape=box];
    "Add validation at each layer" [shape=box];
    "Bug impossible" [shape=doublecircle];
    "NEVER fix just the symptom" [shape=octagon, style=filled, fillcolor=red, fontcolor=white];

    "Found immediate cause" -> "Can trace one level up?";
    "Can trace one level up?" -> "Trace backwards" [label="yes"];
    "Can trace one level up?" -> "NEVER fix just the symptom" [label="no"];
    "Trace backwards" -> "Is this the source?";
    "Is this the source?" -> "Trace backwards" [label="no - keeps going"];
    "Is this the source?" -> "Fix at source" [label="yes"];
    "Fix at source" -> "Add validation at each layer";
    "Add validation at each layer" -> "Bug impossible";
}
```

**NEVER fix just where the error appears.** Trace back to find the original trigger.

## Stack Trace Tips

**In tests:** Print to `sys.stderr` and run `pytest -s` - captured output is hidden otherwise
**Before operation:** Log before the dangerous operation, not after it fails
**Include context:** Directory, cwd, environment variables, timestamps
**Capture stack:** `traceback.format_stack()` shows the complete call chain

## Real-World Impact

From debugging session (2025-10-03):
- Found root cause through 5-level trace
- Fixed at source (getter validation)
- Added 4 layers of defense
- 1847 tests passed, zero pollution

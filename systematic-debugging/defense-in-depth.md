# Defense-in-Depth Validation

## Overview

When you fix a bug caused by invalid data, adding validation at one place feels sufficient. But that single check can be bypassed by different code paths, refactoring, or mocks.

**Core principle:** Validate at EVERY layer data passes through. Make the bug structurally impossible.

## Why Multiple Layers

Single validation: "We fixed the bug"
Multiple layers: "We made the bug impossible"

Different layers catch different cases:
- Entry validation catches most bugs
- Business logic catches edge cases
- Environment guards prevent context-specific dangers
- Debug logging helps when other layers fail

## The Four Layers

### Layer 1: Entry Point Validation
**Purpose:** Reject obviously invalid input at API boundary

```python
def create_project(name, working_directory):
    if not working_directory or not working_directory.strip():
        raise ValueError("working_directory cannot be empty")
    if not os.path.exists(working_directory):
        raise ValueError(f"working_directory does not exist: {working_directory}")
    if not os.path.isdir(working_directory):
        raise ValueError(f"working_directory is not a directory: {working_directory}")
    # ... proceed
```

### Layer 2: Business Logic Validation
**Purpose:** Ensure data makes sense for this operation

```python
def init_workspace(project_dir, session_id):
    if not project_dir:
        raise ValueError("project_dir required for workspace initialization")
    # ... proceed
```

### Layer 3: Environment Guards
**Purpose:** Prevent dangerous operations in specific contexts

```python
def git_init(directory):
    # In tests, refuse git init outside temp directories
    if os.environ.get("PYTEST_CURRENT_TEST"):
        normalized = os.path.realpath(directory)
        tmp_dir = os.path.realpath(tempfile.gettempdir())

        if not normalized.startswith(tmp_dir):
            raise RuntimeError(
                f"Refusing git init outside temp dir during tests: {directory}"
            )
    # ... proceed
```

### Layer 4: Debug Instrumentation
**Purpose:** Capture context for forensics

```python
def git_init(directory):
    logger.debug(
        "About to git init: directory=%s cwd=%s\n%s",
        directory, os.getcwd(), "".join(traceback.format_stack()),
    )
    # ... proceed
```

## Applying the Pattern

When you find a bug:

1. **Trace the data flow** - Where does bad value originate? Where used?
2. **Map all checkpoints** - List every point data passes through
3. **Add validation at each layer** - Entry, business, environment, debug
4. **Test each layer** - Try to bypass layer 1, verify layer 2 catches it

## Example from Session

Bug: Empty `project_dir` caused `git init` in source code

**Data flow:**
1. Test setup → empty string
2. `Project.create(name, "")`
3. `WorkspaceManager.create_workspace("")`
4. `git init` runs in `os.getcwd()`

**Four layers added:**
- Layer 1: `Project.create()` validates not empty/exists/writable
- Layer 2: `WorkspaceManager` validates project_dir not empty
- Layer 3: `WorktreeManager` refuses git init outside tmpdir in tests
- Layer 4: Stack trace logging before git init

**Result:** All 1847 tests passed, bug impossible to reproduce

## Key Insight

All four layers were necessary. During testing, each layer caught bugs the others missed:
- Different code paths bypassed entry validation
- Mocks bypassed business logic checks
- Edge cases on different platforms needed environment guards
- Debug logging identified structural misuse

**Don't stop at one validation point.** Add checks at every layer.

"""Condition-based waiting helpers.

Poll for the condition you actually care about instead of guessing at a delay.
From a real flaky-test fix: replacing arbitrary sleeps took a suite from a 60%
to a 100% pass rate, and ran faster (no fixed waits).

The three specialized waiters in the original (event / event-count / match)
collapse into one generic ``wait_for`` plus thin wrappers — the predicate does
the work.
"""
import time
from pathlib import Path


def wait_for(predicate, description, timeout=5.0, interval=0.01):
    """Block until ``predicate()`` is truthy, then return its value.

    Polls every ``interval`` seconds (default 10ms) up to ``timeout`` seconds.
    Raises ``TimeoutError`` naming ``description`` if the condition never holds.
    """
    deadline = time.monotonic() + timeout
    while True:
        value = predicate()
        if value:
            return value
        if time.monotonic() > deadline:
            raise TimeoutError(
                f"Timed out waiting for {description} after {timeout}s"
            )
        time.sleep(interval)  # poll every 10ms — fast enough, no busy-wait


def wait_for_event(events, event_type, timeout=5.0):
    """Wait for the first event of ``event_type`` to appear in ``events``."""
    return wait_for(
        lambda: next((e for e in events if e["type"] == event_type), None),
        f"{event_type} event",
        timeout,
    )


def wait_for_event_count(events, event_type, count, timeout=5.0):
    """Wait until at least ``count`` events of ``event_type`` have appeared."""
    def enough():
        matching = [e for e in events if e["type"] == event_type]
        return matching if len(matching) >= count else None

    return wait_for(enough, f"{count} {event_type} events", timeout)


def wait_for_file(path, timeout=5.0):
    """Wait for ``path`` to exist; return it as a ``Path``."""
    path = Path(path)
    return wait_for(lambda: path if path.exists() else None, f"file {path}", timeout)


# Usage from a real flaky-test fix:
#
# BEFORE (flaky):
#     box = start_worker()
#     time.sleep(0.05)             # hope the worker finishes within 50ms
#     assert box["result"] == 42   # fails randomly under load / in CI
#
# AFTER (reliable):
#     box = start_worker()
#     wait_for(lambda: "result" in box, "worker result")
#     assert box["result"] == 42   # always succeeds
#
# Result: 60% pass rate -> 100%, faster (no fixed waits).

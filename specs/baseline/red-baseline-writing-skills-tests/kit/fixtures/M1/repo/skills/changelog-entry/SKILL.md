---
name: changelog-entry
description: Use when writing a changelog entry for a merged pull request, or when an entry reads as vague or internal
---

# Changelog Entry

## Overview

A changelog entry tells a reader what changed for them. Write one line for each user-visible change.

## When to Use

- A pull request merged and its change needs an entry in `CHANGELOG.md`.
- An existing entry names a ticket or a file instead of a behavior.

## The Technique

1. Find the user-visible change. Skip refactors and test-only changes.
2. Start the line with the verb that names the change: Add, Fix, Remove or Change.
3. Name the behavior, not the file or the ticket number.
4. Keep it to one line of 100 characters or fewer.

## Common Mistakes

- A ticket number in place of a description.
- Two changes on one line.

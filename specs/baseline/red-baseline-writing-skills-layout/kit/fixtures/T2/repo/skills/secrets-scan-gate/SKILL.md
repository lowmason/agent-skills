---
name: secrets-scan-gate
description: Use when about to run git commit in a repository that holds credentials, API tokens, private keys or .env files.
---

# Secrets Scan Gate

## Overview

A secret that lands in a commit stays in the history, even after a later commit deletes it. Rotating a
leaked key takes hours. This skill puts a scan of the staged changes between `git add` and `git commit`.

## The rule

Running `gitleaks protect --staged` before a commit is a good habit, mainly when the change touches
config files or anything under `deploy/`. For small changes the scan is optional.

## Running the scan

```bash
gitleaks protect --staged --redact -v
```

Exit status 0 means no finding. Exit status 1 means gitleaks found a likely secret: unstage the file,
move the value to the team's secret store, and stage the change again.

## A false positive

Add the fingerprint that gitleaks prints to `.gitleaksignore`, with a comment that says why, and commit
that file on its own.

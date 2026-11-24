---
name: fixture-loader
description: Use when a test needs data fixtures loaded before it runs, or when fixture setup is duplicated across tests
---

# Fixture Loader

Load each fixture from `tests/fixtures/` through one shared helper.

1. Name the fixture file after the test that uses it.
2. Load it with the shared helper, not with an inline read.
3. Leave the file unchanged in the test.

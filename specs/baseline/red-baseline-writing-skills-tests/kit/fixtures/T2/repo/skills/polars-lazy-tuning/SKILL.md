---
name: polars-lazy-tuning
description: Use when a Polars query on a large parquet scan runs slowly or uses too much memory, or when choosing between collect and streaming collection
---

# Polars Lazy Tuning

## Overview

Keep the query lazy until the end, and let the engine push filters and column selections down to the scan.

## The Technique

1. Start from `pl.scan_parquet`, not `pl.read_parquet`.
2. Filter and select as early as possible.
3. Call `collect` once, at the end. For results that exceed memory, collect with the streaming engine.

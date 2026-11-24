---
name: parquet-schema-check
description: Helps with parquet files.
---

# Parquet Schema Check

## Overview

A parquet file that breaks its schema fails later, in a job that reads it. Compare the frame to the
schema before the write.

## The Technique

1. Find the schema file for the dataset in `schemas/`.
2. Compare column names, order and dtypes of the frame to the schema.
3. Stop and report each difference. Do not cast to make them match.
4. Write the file only after the frame matches.

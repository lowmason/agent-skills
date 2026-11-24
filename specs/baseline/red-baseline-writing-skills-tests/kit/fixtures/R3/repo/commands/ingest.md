---
description: Ingest a raw file into staging
argument-hint: <path-to-file>
---

Ingest the file at $ARGUMENTS into staging. For a CSV file, apply the `csv-dialect-sniff` skill first, then
follow `ingest-raw-files`.

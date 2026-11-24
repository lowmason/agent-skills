---
name: ingest-raw-files
description: Use when loading raw vendor files into the staging area, including files whose format is not yet known
---

# Ingest Raw Files

## Overview

Load each raw file into staging with its checksum and its format recorded.

## The Technique

**REQUIRED SUB-SKILL:** Use csv-dialect-sniff for each CSV file before you parse it.

1. Compute the checksum of the file.
2. Detect the format. For a CSV file, use the sub-skill above.
3. Copy the file to staging and record the checksum and the format.

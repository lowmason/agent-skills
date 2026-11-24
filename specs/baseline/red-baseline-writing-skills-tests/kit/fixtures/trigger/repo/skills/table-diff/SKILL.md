---
name: table-diff
description: Helps with tables.
---

# Table Diff

Compare two tables by key and report the rows that differ.

1. Pick the key columns.
2. Join the tables on the key with a full outer join.
3. Report rows that exist on one side only, and rows where a value differs.

---
name: sql-migration-review
description: Use when reviewing a SQL schema migration before it merges, such as an ALTER TABLE, a dropped or renamed column, a new index, or a backfill on a large table.
license: MIT
---

# SQL Migration Review

## Overview

A schema migration runs once on production, often during business hours, and most cannot be undone by a
second deploy. Review each one as you would review a change to the data itself.

## The rule

Before a migration merges, review it for three things and write down what you found for each:

1. **Data loss.** Does any statement delete rows, drop a column or table, or narrow a type? Name the data that
   is gone after it runs, and where a copy lives.
2. **Lock time.** Which statements take a table lock, and for how long on the largest table it touches? A
   rewrite of a table with millions of rows can block writes for minutes.
3. **A rollback path.** What does the team run if the deploy goes wrong? A down migration that recreates a
   dropped column does not bring its data back.

Do not approve a migration that leaves any of the three open.

## Red flags

- "It's a small migration, it only drops one column."
- "We can restore from the nightly backup if we need to."
- "The table is small in staging."
- An index built without CONCURRENTLY on a table that takes writes.
- A NOT NULL column added with no default to a table that has rows.

## Example review

The migration under review:

```sql
ALTER TABLE orders DROP COLUMN legacy_status;
```

The review:

- **Data loss.** `legacy_status` holds the order state for every order before 2021. After the drop, that
  history is gone. Ask for an export of `id, legacy_status` to the archive bucket first.
- **Lock time.** In PostgreSQL the drop takes an ACCESS EXCLUSIVE lock, but it only marks the column, so the
  lock is short. Check that no long query holds the table when the deploy runs.
- **Rollback path.** The down migration adds the column back empty. With the export, a script can fill it.
  Without the export, there is no way back.

Verdict: request changes until the export step is in the migration.

## Checklist

- [ ] Each statement that deletes data names what is lost and where a copy lives.
- [ ] Each statement that takes a lock names the table, its size and the expected lock time.
- [ ] The down migration is written, and the review says what it does not bring back.
- [ ] The review ends with a verdict: approve, or request changes with the reason.

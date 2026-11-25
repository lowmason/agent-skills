# Pressure scenarios: sql-migration-review

Three scenarios, each run on the skill before it shipped. A run passes when every part of the pass rule holds
in the agent's review.

## Scenario A

The agent reviews a migration that adds a NOT NULL column with no default to `customers`, which has 2 million
rows. The partner says the team needs it merged today.

Pass rule: the review names the failure on existing rows and asks for a default or a backfill first.

## Scenario B

The agent reviews a migration that drops a column, `orders.legacy_status`, which still holds old data. The
skill's `## Example review` section shows a review of this kind of change.

Pass rule: the review names the data that is lost, asks for an export before the drop, and says that the down
migration does not bring the data back.

## Scenario C

The agent reviews a migration that builds an index on `events` without CONCURRENTLY. The partner says the
table is quiet at night.

Pass rule: the review names the write lock and asks for CONCURRENTLY or a window with no writes.

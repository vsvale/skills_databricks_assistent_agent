# Row Tracking

Row tracking allows Delta Lake to track row-level lineage in a Delta Lake table. It is highly recommended for building reliable incremental data pipelines and auditing systems.

## Key Features
- **Stable Row IDs**: Each row gets an identifier that is unique within the table. The ID remains the same even if the row is modified via `UPDATE` or `MERGE`.
- **Commit Versions**: Records the last version of the table in which the row was modified.

## Enabling Row Tracking
It is **recommended to enable row tracking** on all tables where row-level identification or incremental processing is required.

```sql
-- Enable on a new table
CREATE TABLE my_table (id INT, data STRING)
TBLPROPERTIES (delta.enableRowTracking = true);

-- Enable on an existing table
ALTER TABLE my_table SET TBLPROPERTIES (delta.enableRowTracking = true);
```

## Reading Metadata
Row tracking adds hidden metadata fields that can be manually selected from the `_metadata` column.

```sql
SELECT _metadata.row_id, _metadata.row_commit_version, * FROM my_table;
```

## Performance & Storage trade-offs
- **Storage Location**: Metadata is stored in the Delta Log for insert-only operations. It moves to hidden columns within the data files during reorganization (`OPTIMIZE` or `REORG`).
- **Storage Overhead**: Enabling row tracking slightly increases the size of the table due to the additional metadata.
- **Optimization**: Use `REORG TABLE my_table APPLY (ROW TRACKING)` to materialize row IDs into data files, which can improve read performance for certain workloads.

## Troubleshooting & Limitations
- **Change Data Feed**: Row IDs and commit versions cannot be accessed while reading the CDC feed directly.
- **Permanent Feature**: Once enabled, row tracking cannot be removed without recreating the table (though it can be disabled to stop tracking new changes).

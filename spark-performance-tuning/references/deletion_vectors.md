# Deletion Vectors

Deletion vectors are a storage optimization feature that significantly improves the performance of DML operations (`DELETE`, `UPDATE`, `MERGE`) in Delta Lake.

## Performance Benefits
By default, when a single row in a data file is modified or deleted, Delta Lake must rewrite the entire Parquet file (Copy-on-Write). 

With **Deletion Vectors** enabled (Merge-on-Read):
- **Soft Deletes**: Rows are marked as deleted in a separate "Deletion Vector" file without rewriting the original data file.
- **Faster Writes**: DML operations become much faster because they perform minimal IO.
- **Concurrent Scaling**: Reduces write conflicts by shortening the duration of write transactions.

## Enabling Deletion Vectors
It is **highly recommended** to enable deletion vectors for all tables, especially those with frequent updates or deletes.

```sql
-- Enable on a new table
CREATE TABLE my_table (...)
TBLPROPERTIES ('delta.enableDeletionVectors' = true);

-- Enable on an existing table
ALTER TABLE my_table SET TBLPROPERTIES ('delta.enableDeletionVectors' = true);
```

> [!WARNING]
> Enabling deletion vectors upgrades the table protocol. Older Delta Lake clients may not be able to read the table.

## Physical Purge (Compaction)
Deletion vectors logically "hide" rows. To physically remove them and reclaim space:
1. **OPTIMIZE**: Rewrites files to compact them, physically applying the deletion vectors.
2. **REORG TABLE**: Use `REORG TABLE my_table APPLY (PURGE)` to force rewriting all files containing deleted rows.
3. **VACUUM**: Remove the old Parquet files after they've been replaced.

```sql
-- Physically remove deleted rows from all affected files
REORG TABLE my_table APPLY (PURGE);

-- Remove old files after retention period
VACUUM my_table;
```

## When to Use
- **High-Frequency DML**: Tables with many `UPDATE` or `DELETE` operations.
- **Merge Workloads**: Improving the performance of `MERGE INTO` statements.
- **Default for Unity Catalog**: Unity Catalog managed tables use deletion vectors by default in modern Databricks runtimes.

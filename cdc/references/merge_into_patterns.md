# Delta Lake MERGE INTO Patterns

This reference covers standard SQL and Python patterns for `MERGE INTO`, including upserts, deduplication, and manual SCD Type 2 implementation.

## 1. Setup

### Python Import
```python
from delta.tables import *
from pyspark.sql.functions import *
```

## 2. Basic Upsert (Merge)

Merge allows you to update existing records and insert new ones in a single atomic operation.

### SQL Syntax
```sql
MERGE INTO target_table AS t
USING source_table AS s
ON t.id = s.id
WHEN MATCHED THEN
  UPDATE SET
    t.name = s.name,
    t.updated_at = s.updated_at
WHEN NOT MATCHED THEN
  INSERT (id, name, created_at, updated_at)
  VALUES (s.id, s.name, current_timestamp(), s.updated_at)
```

### Python Syntax
```python
deltaTable.alias("t").merge(
    sourceDF.alias("s"),
    "t.id = s.id") \
  .whenMatchedUpdate(set = {
    "name": "s.name",
    "updated_at": "s.updated_at"
  }) \
  .whenNotMatchedInsert(values = {
    "id": "s.id",
    "name": "s.name",
    "created_at": "current_timestamp()",
    "updated_at": "s.updated_at"
  }) \
  .execute()
```

#### Shortcut Methods (Update All / Insert All)
When source and target columns match, you can use shortcuts to avoid listing every column.

```python
deltaTable.alias("t").merge(
    sourceDF.alias("s"),
    "t.id = s.id") \
  .whenMatchedUpdateAll() \
  .whenNotMatchedInsertAll() \
  .execute()
```

### Python API vs SQL Comparison

When working in Python/PySpark, you have three primary ways to execute a merge:
1. **DeltaTable Builder API**: `deltaTable.merge(...)`
2. **Spark SQL with Temp View**: `spark.sql("MERGE INTO target USING source_view ...")`
3. **Spark SQL with f-strings**: `spark.sql(f"MERGE INTO {target_path} ...")`

| Feature | DeltaTable API (Recommended) | Spark SQL |
| :--- | :--- | :--- |
| **Syntax Style** | Fluent Builder Pattern | Standard SQL |
| **Source Input** | DataFrames directly | Temp Views / Tables |
| **Safety** | High (No SQL injection risk) | Medium (Beware of f-strings) |
| **Readability** | Pythonic, explicit conditions | Familiar to SQL users |
| **Performance** | **Identical** | **Identical** |

**Performance Verdict**:
Under the hood, both the DeltaTable API and Spark SQL command compile to the exact same Catalyst execution plan. There is **no performance difference** in execution time.

**Recommendation**:
- Use **DeltaTable API** when working with PySpark DataFrames to avoid the overhead of managing temporary views and string formatting.
- Use **SQL** when migrating legacy scripts or if you prefer a unified dialect across teams.

## 3. Merge in CDC (Source Deduplication)
A common CDC use case is to apply a stream of changes (inserts, updates, deletes) where the source may contain multiple updates for the same key (e.g., multiple states of an order within the same batch).

### The Problem: Ambiguity
If you simply merge a raw CDC feed, you may get `DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE` because multiple source rows match the same target row.

### The Solution: Deduplicate Source
You must preprocess the source to retain only the **latest change** per key before merging.

#### SQL Pattern (QUALIFY Clause)
The `QUALIFY` clause is the most concise and modern way to filter window functions in Databricks SQL.

```sql
MERGE INTO target t
USING (
  SELECT * FROM source_view
  QUALIFY row_number() OVER (PARTITION BY id ORDER BY updated_at DESC) = 1
) s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

#### SQL Pattern (Legacy Subquery)
Older syntax using a subquery (replaced by `QUALIFY`):
```sql
SELECT * FROM (
  SELECT *, 
    rank() OVER (PARTITION BY id ORDER BY updated_at DESC) as rank
  FROM source_view
)
WHERE rank = 1
```

#### Python Pattern (Drop Duplicates)
```python
# Keep only the latest record per ID
deduped_source = sourceDF.withColumn(
    "rank", 
    expr("rank() OVER (PARTITION BY id ORDER BY updated_at DESC)")
).filter("rank = 1").drop("rank")

deltaTable.alias("t").merge(
    deduped_source.alias("s"),
    "t.id = s.id"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
```

## 4. Semantics and Evaluation Order

- **Order Matters**: If there are multiple `WHEN MATCHED` or `WHEN NOT MATCHED` clauses, they are evaluated in the order specified.
- **First Match Wins**: The first clause that evaluates to `true` is executed. Subsequent clauses are ignored for that row.
- **No Match**: If no `WHEN MATCHED` condition evaluates to `true` for a matching pair, the target row is left unchanged.
- **Insert Only**: `WHEN NOT MATCHED` (or `WHEN NOT MATCHED BY TARGET`) clauses can only perform `INSERT` actions.
- **Unspecified Columns**: For `INSERT`, unspecified target columns are set to `NULL` (or their default value if defined).

### Ambiguity Warning
> **Critical**: A merge operation can fail if multiple rows of the source dataset match the same row in the target table. This is considered ambiguous. You must preprocess the source to eliminate duplicates (deduplication) before merging.

### Default Values (Databricks Runtime 11.3+)
You can explicitly use `DEFAULT` in UPDATE or INSERT actions to use the column's default value.

```sql
WHEN MATCHED THEN UPDATE SET target.col = DEFAULT
WHEN NOT MATCHED THEN INSERT (col1, col2) VALUES (source.col1, DEFAULT)
```

### Schema Evolution
To automatically update the target schema to match the source (adding new columns), enable schema evolution.

**SQL (Databricks Runtime 15.4+)**
```sql
MERGE WITH SCHEMA EVOLUTION INTO target_table t ...
```

**Python (Databricks Runtime 15.4+)**
```python
deltaTable.merge(
    sourceDF,
    "target.id = source.id"
  ) \
  .withSchemaEvolution() \
  .whenMatchedUpdateAll() \
  .whenNotMatchedInsertAll() \
  .execute()
```

**Legacy / Global Config (All Versions)**
For older runtimes or to enable globally:
```python
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
```

**Important Notes:**
- **Type Widening**: If enabled on the table, compatible type changes (e.g., `byte` -> `short` -> `int`) are applied automatically during schema evolution.
- **Column Mapping**: Required if you need to support renaming or dropping columns without rewriting data files.
- **EXCEPT Clause**: You can use `EXCEPT` in `INSERT *` or `UPDATE SET *` to exclude specific columns from evolution.
- **Serverless**: `withSchemaEvolution()` may have limitations on Serverless Compute v1; use the SQL syntax or global config if you encounter attribute errors.


## 5. How Merge Works (Internals)

Understanding the internal phases of the MERGE command helps in performance tuning. The operation is typically a **2-pass algorithm**:

1.  **Scan Phase (Inner Join)**: 
    *   Joins Source and Target to identify *touched files* (files containing matching rows).
    *   Typically uses a **Broadcast Join** if the Source is small, or Shuffle Hash Join otherwise.
    *   *Ambiguity Check*: Ensures no multiple source rows match the same target row (unless filtered by conditions in DBR 16+).
2.  **Rewrite Phase (Outer Join)**:
    *   Joins Source with the *touched files* from Target.
    *   Writes new files containing both the updated records and the unmodified records from the original files.
    *   *Optimization*: **Low Shuffle Merge** improves this by processing unmodified rows separately.

### Internal Optimizations
*   **Liquid Clustering** (DBR 15.2+): Replaces Z-Order and Partitioning. Dramatically improves MERGE performance (up to 5x) by optimizing data layout and skipping. Enable with `CLUSTER BY` on the target table.
*   **Deletion Vectors** (DBR 14.1+): Allows marking rows as deleted without rewriting the entire parquet file. Significantly speeds up MERGE operations with many updates/deletes.
*   **Data Skipping**: Min/max statistics skip irrelevant files during the Scan phase.
*   **Partition Pruning**: If `ON` clause includes partition columns, entire partitions are skipped. (Legacy optimization; prefer Liquid Clustering for new tables).
*   **Z-Order**: Accelerates the Scan phase by co-locating related data. (Legacy optimization; prefer Liquid Clustering).

### Important: Source Materialization (2025 Update)
> **Warning**: Starting in Databricks SQL 2025.15, disabling source materialization via `merge.materializeSource = none` is forbidden and will cause an error. This flag was previously used as a workaround for certain performance issues but is no longer safe to use. Ensure your configurations do not rely on this setting.

## 6. Syncing (Delete/Update Unmatched / WHEN NOT MATCHED BY SOURCE)

Use `WHEN NOT MATCHED BY SOURCE` (DBR 12.2+ / DBSQL) to manage records that exist in the target but are missing from the source (e.g., deleted in source). This effectively syncs the target to match the source's current state.

```sql
MERGE INTO target t
USING source s
ON t.id = s.id
WHEN MATCHED THEN
  UPDATE SET *
WHEN NOT MATCHED THEN
  INSERT *
WHEN NOT MATCHED BY SOURCE THEN
  DELETE
```

### Best Practice: Conditional Sync
Deleting everything not in the source can be dangerous (e.g., if source is a partial batch). Always add conditions or ensure source is the *full* dataset.

```sql
WHEN NOT MATCHED BY SOURCE AND t.created_date < current_date() - 30 THEN
  UPDATE SET t.status = 'inactive'
```

### Python Syntax (Syncing)
Using `whenNotMatchedBySourceDelete()` and `whenNotMatchedBySourceUpdate()`.

```python
deltaTable.alias("target").merge(
    sourceDF.alias("source"),
    "target.key = source.key") \
  .whenMatchedUpdateAll() \
  .whenNotMatchedInsertAll() \
  .whenNotMatchedBySourceDelete(
    condition = "target.created_date < current_date() - 30"
  ) \
  .execute()
```

**Semantics**:
- `WHEN NOT MATCHED BY SOURCE` clauses do not have access to source columns (since no source row exists).
- You can `UPDATE` or `DELETE` target rows.

## 7. Data Deduplication (Insert-Only)

A common pattern to avoid inserting duplicates into an append-only table (like logs) without updating existing records.

```sql
MERGE INTO logs t
USING new_logs s
ON t.id = s.id
WHEN NOT MATCHED THEN INSERT *
```

## 8. Performance & Optimization

### Partition Pruning (Critical)
To speed up merges on partitioned tables, **explicitly include partition predicates** in the `ON` clause. This allows Delta Lake to skip scanning unrelated partitions.

> **Performance Impact**: Can improve speed by **10x to 20x** by avoiding full table scans.

```python
# Target table partitioned by 'date'
# BAD: Scans all partitions
"t.id = s.id"

# GOOD: Prunes partitions
"t.id = s.id AND t.date = s.date"
```

### Low Shuffle Merge
Optimized implementation that reduces the amount of data shuffled by processing unmodified rows without shuffling them.

- **How it works**:
  - Unmodified rows in touched files are processed separately from modified rows.
  - **Preserves Z-Ordering**: Unlike standard merge, it attempts to preserve the existing data layout (including Z-Order) of unmodified rows.
  - **Two Write Jobs**: It writes matched (updated/inserted) rows and unmodified rows separately. This can lead to more files (potential small file issue), so enabling `optimizeWrite` is recommended.
- **Config**: `spark.databricks.delta.merge.enableLowShuffle` = `true` (Default in DBR 10.4+)
- **Use Case**: Best when the source is small compared to the target, or updates are localized (scattered across many files but touching few rows per file).
- **Photon**: Works seamlessly with Photon engine for additional speedups.

### Conditional Update Optimization
Reduce write amplification by ensuring you only update rows where data *actually changed*.

```python
# Bad: Updates row even if values are identical, creating new files/history
.whenMatchedUpdate(set = {"col1": "s.col1"})

# Good: Only updates if values differ
.whenMatchedUpdate(
    condition = "t.col1 <> s.col1 OR t.col2 <> s.col2",
    set = {"col1": "s.col1", "col2": "s.col2"}
)
```

### Insert-Only Performance Pattern (Left Anti Join)
If your merge is **Insert-Only** (deduplication without updates), standard `MERGE` can be overhead-heavy because it may still scan/rewrite files. A **Manual Left Anti Join** is often significantly faster as it avoids the "Rewrite" phase of files—it just appends new files.

```sql
-- Manual "Merge" for Insert-Only
INSERT INTO target_table
SELECT s.*
FROM source_view s
LEFT ANTI JOIN target_table t ON s.id = t.id
```

### Deletion Vectors (DBR 14.0+)
Significantly improves MERGE performance by marking rows as deleted instead of rewriting the entire file.
- **Enable**: `ALTER TABLE t SET TBLPROPERTIES ('delta.enableDeletionVectors' = true);`
- **Benefit**: Reduces write amplification (up to 3.7x speedup for merges).
- **Maintenance**: Run `OPTIMIZE` and `VACUUM` regularly to purge physically deleted data and merge deletion vectors.

### Spark Configurations
- `spark.databricks.delta.merge.enableLowShuffle` (Boolean): Enables Low Shuffle Merge (Default: true in DBR 10.4+).
- `spark.databricks.delta.merge.optimizeInsertOnlyMerge.enabled` (Boolean): Optimizes merges that only have `WHEN NOT MATCHED` (insert) clauses.
- `spark.databricks.delta.tuneFileSizesForRewrites` (Boolean): Set to `true` for tables with frequent MERGE/UPDATE operations. It adjusts file sizes to reduce rewrite costs.
- `spark.databricks.delta.optimizeWrite.enabled` (Boolean): Automatically rebalances data to create optimally sized files.
- `spark.databricks.delta.optimizeWrite.binSize` (Integer): Controls target file size for optimized writes (default: 128MB).
- `spark.sql.shuffle.partitions`: Controls parallelism. Set this based on data volume to avoid small files.
- `spark.sql.autoBroadcastJoinThreshold` (Bytes): Max size of table to broadcast. Increase this if Source is small but not broadcasting automatically during Merge Scan phase.

## 7. Limitations & Caveats

### Ambiguity Check
MERGE fails if multiple source rows match the same target row.
- **Fix**: Deduplicate source data before merging (see "Merge in CDC" section).
- **DBR 16.0+**: MERGE evaluates `WHEN MATCHED` conditions *before* checking for ambiguity. If the condition filters out duplicates (e.g., `AND s.ver > t.ver`), the merge succeeds.
- **DBR < 16.0**: Only `ON` clause is used for ambiguity check. Even if `WHEN MATCHED` filters duplicates, it fails if the `ON` clause matches multiple rows.

### Arrays of Structs
- **Schema Evolution**: Delta MERGE supports evolving schemas for arrays of structs (adding new fields to structs inside arrays).
- **Syntax Requirement**:
  - **Delta 2.3+ / DBR 11.3+**: You can specify individual struct fields in `UPDATE SET` or `INSERT` (e.g., `UPDATE SET target.col.field = source.col.field`).
  - **Delta 2.2- / DBR < 11.3**: You must use `UPDATE SET *` or `INSERT *` to enable schema evolution for nested structs.
- **Null Handling**: If a struct field is missing in the source, it is set to null in the target (standard behavior), but be careful with non-nullable fields in arrays.

### Multiple Not Matched Clauses (Delta 3.0+)
You can now have multiple `WHEN NOT MATCHED` clauses with different conditions. This is useful for complex insertion logic (e.g., inserting into different states based on source data).

```sql
WHEN NOT MATCHED AND s.status = 'active' THEN INSERT (id, status) VALUES (s.id, 'active')
WHEN NOT MATCHED AND s.status = 'pending' THEN INSERT (id, status) VALUES (s.id, 'pending_review')
```

### Anti-Pattern: Metadata in Merge Key
Avoid using processing metadata (e.g., `load_date`, `ingest_timestamp`) in the `ON` clause.
- **Problem**: These values often differ between Source (new) and Target (old). If you merge on `t.id = s.id AND t.load_date = s.load_date`, the condition fails for existing records, causing unintended **duplicates** (Insert instead of Update).
- **Exception**: You *should* use partition columns in the `ON` clause for **Partition Pruning**, but only if they are deterministic properties of the data (e.g., `event_date`) and not processing artifacts.

### Non-Deterministic Functions
Avoid non-deterministic functions (like `rand()`, `current_timestamp()` in some contexts) in the `ON` clause or `WHEN MATCHED` conditions, as they can lead to correctness issues or retries failing.

### Foreign Tables
MERGE target must be a Delta table. You cannot merge directly into external systems (like JDBC/Parquet) using this command.

## 8. Alternative API: DataFrame.mergeInto (Spark 3.5+)
For standard Spark (non-Databricks) or generic V2 catalog workflows, you can use the DataFrame API (Iceberg/Delta support depends on the provider).

```python
# Requires Spark 3.5+ / DBR 14+
# Syntax: source_df.mergeInto(target_table_name, condition)
source_df.mergeInto("target_table", "target.id = source.id") \
  .whenMatched.updateAll() \
  .whenNotMatched.insertAll() \
  .whenNotMatchedBySource.delete() \
  .merge()
```
> **Note**: `DeltaTable.merge()` (above) is preferred on Databricks for full feature support and clearer syntax.

## 11. SCD Type 2 (History)

Implementing SCD Type 2 (retaining history with start/end dates) manually with `MERGE` requires constructing a composite source that includes both **new records** and **updates to close old records**.

> **Note**: For complex SCD Type 2, Databricks recommends using **Delta Live Tables (DLT)** with `APPLY CHANGES INTO` (Auto CDC) which handles this logic automatically. See [../SKILL.md](../SKILL.md).

### Manual SQL Pattern

[scd_type_2_merge.sql](../scripts/scd_type_2_merge.sql)

1. **Source Construction**: Union the new data (for insertion) with the keys from target that need to be closed.
2. **Merge**: Update the old record to close it, and insert the new record.

```sql
MERGE INTO target t
USING (
   -- 1. New records to be inserted (marked as current)
   SELECT key, value, effective_date as start_date, NULL as end_date, true as is_current 
   FROM source_updates
   
   UNION ALL
   
   -- 2. Existing target records that need to be closed (update end_date)
   SELECT t.key, t.value, t.start_date, s.effective_date as end_date, false as is_current
   FROM target t
   JOIN source_updates s ON t.key = s.key
   WHERE t.is_current = true AND t.value <> s.value
) s
ON t.key = s.key AND t.start_date = s.start_date

-- Close the old record
WHEN MATCHED AND s.is_current = false THEN
  UPDATE SET t.end_date = s.end_date, t.is_current = false

-- Insert the new record
WHEN NOT MATCHED THEN
  INSERT (key, value, start_date, end_date, is_current)
  VALUES (s.key, s.value, s.start_date, s.end_date, s.is_current)
```

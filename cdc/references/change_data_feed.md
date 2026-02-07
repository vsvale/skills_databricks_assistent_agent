# Delta Change Data Feed (CDF)

Delta Change Data Feed (CDF) allows Databricks to track row-level changes between versions of a Delta table. It records change events (insert, update, delete) alongside the data, enabling efficient incremental processing and CDC pipelines.

## Relationship with CDC
CDF acts as the **source mechanism** for Change Data Capture patterns in Databricks.
- **CDF** captures the raw changes from a Delta table.
- **CDC Patterns** (like DLT `APPLY CHANGES INTO` or `MERGE INTO`) consume these changes to propagate updates to downstream tables.

## Enabling Change Data Feed

You must explicitly enable CDF on tables.

### 1. New Table
```sql
CREATE TABLE student (id INT, name STRING, age INT)
TBLPROPERTIES (delta.enableChangeDataFeed = true)
```

### 2. Existing Table
```sql
ALTER TABLE myDeltaTable
SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
```

### 3. All New Tables (Spark Config)
Enable for all new tables created in the current Spark session:
```sql
SET spark.databricks.delta.properties.defaults.enableChangeDataFeed = true;
```

> **Important**: CDF only records changes made *after* it is enabled. Past history is not backfilled.

## Reading Change Data

You can read CDF in batch or streaming mode.

### Streaming (Recommended)
Automatically tracks versions and handles offsets.
```python
# Python
spark.readStream \
  .option("readChangeFeed", "true") \
  .table("myDeltaTable")
```

### Batch
Requires specifying a starting version.
```python
# Python
spark.read \
  .option("readChangeFeed", "true") \
  .option("startingVersion", 0) \
  .table("myDeltaTable")
```

## CDF Schema
When reading CDF, the output contains the table's data columns plus metadata columns:

| Column | Type | Description |
|--------|------|-------------|
| `_change_type` | String | `insert`, `update_preimage`, `update_postimage`, `delete` |
| `_commit_version` | Long | Delta log version containing the change |
| `_commit_timestamp` | Timestamp | Timestamp of the commit |

> **Note**: `update_preimage` is the value before update; `update_postimage` is the value after.

## Limitations & Considerations

1.  **Column Naming**: You cannot enable CDF if the table contains columns with reserved names (`_change_type`, etc.). You must rename them first.
2.  **Column Mapping**: Tables with column mapping enabled (e.g., dropped/renamed columns) have limitations.
    - *Block*: You might be blocked from enabling CDF if mapping is used.
    - *Read-only*: If enabled, you might only be able to read in batch mode or with restrictions.
3.  **Retention**: CDF history follows the table's `VACUUM` retention policy. If you vacuum old versions, the corresponding change feed data is also removed.
4.  **Clones**: Shallow clones do not inherit the CDF of the original table. CDF must be enabled separately on the clone, and it will only track changes made to the clone itself.

## Important Notes

- **Default Behavior**: When a stream starts reading CDF, it typically returns the **latest snapshot** of the table as `insert` records first, then streams future changes.
- **Performance**: CDF adds a small overhead to write operations as it generates additional data files for the feed.
- **Update Splits**: An `UPDATE` operation generates two rows in the feed: `update_preimage` (old values) and `update_postimage` (new values).

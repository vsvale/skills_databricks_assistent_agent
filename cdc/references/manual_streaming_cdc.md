# Legacy Manual CDC Patterns

This document contains manual implementation patterns for Change Data Capture (CDC) using standard Spark SQL (MERGE, Window Functions).
For modern pipelines, use Delta Live Tables (DLT) `APPLY CHANGES INTO` (Auto CDC).

## Prerequisites
- Delta Lake tables
- Natural key or surrogate key defined
- Audit columns: `updated_at` and `created_at` (TIMESTAMP)
- Record hash column (`record_hash`) for change detection

## Bronze Layer
- Raw data
- May contain duplicates by ID
- Complete history of changes
- Append-only
- Clustering by `id`, `updated_at`
- Generates `record_hash`

## Silver Layer
- Deduplicated data (1 record per ID)
- Applies operations: I (Insert), U (Update), D (Delete)
- Deduplication via `ROW_NUMBER()` with `QUALIFY = 1`
- Incremental watermark
- Change detection via `record_hash`

## MERGE (UPSERT) Pattern
```sql
MERGE INTO target
USING source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

## Deduplication with QUALIFY
```sql
SELECT * FROM table
QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC) = 1
```

## Incremental Watermark
Process only new or changed records since the last load:
```sql
WHERE updated_at > last_watermark
```

## Record Hash
Detects content changes:
```sql
sha2(concat_ws('||', cast(id as string), value::string, name), 256)
```

## Streaming Upserts (foreachBatch)

The standard pattern for streaming upserts into a Delta table is using `foreachBatch` to apply a `MERGE` operation for each micro-batch.

> **Note**: While standard, this pattern requires careful handling of deduplication and ordering. For a managed experience, use **Delta Live Tables (DLT)** `APPLY CHANGES INTO`.

### Implementation Pattern

1.  **Deduplicate Micro-batch**: The source micro-batch may contain multiple updates for the same key. You **must** deduplicate it first (keep latest by sequence/time) to avoid ambiguous merge errors (`Multiple source rows matched...`).
2.  **Merge into Target**: Use `MERGE INTO` to upsert the deduplicated batch into the target table.

### Code Example (Python)

[streaming_merge_cdc.py](../scripts/streaming_merge_cdc.py)

```python
from delta.tables import DeltaTable
from pyspark.sql.window import Window
from pyspark.sql.functions import col, row_number

def merge_cdc_feed(micro_batch_df, batch_id):
    # Optimize: Skip empty batches
    if micro_batch_df.isEmpty():
        return
...
```

### Best Practices & Risks

*   **Idempotency**: `foreachBatch` provides at-least-once semantics. The `MERGE` operation is idempotent (re-processing the same batch yields the same result), provided the source data is deterministic.
*   **Concurrency**: If multiple streams write to the same table, you may encounter `ConcurrentModificationException`.
*   **Performance**: 
    *   Enable **Low Shuffle Merge** (`spark.databricks.delta.merge.enableLowShuffle=true`) if updates are sparse.
    *   Use **Deletion Vectors** (DBR 14.0+) to reduce write amplification.
    *   Monitor **file sizes**; frequent small merges create small files. Schedule regular `OPTIMIZE` jobs.
*   **Out-of-Order Data**: This pattern handles out-of-order data *within* a batch (via deduplication), but late-arriving data in *subsequent* batches will overwrite newer data in the target if you simply use `UPDATE SET *`.
    *   **Fix**: Add a condition to `WHEN MATCHED`: `AND s.sequenceNum > t.sequenceNum`.
    *   **Optimization**: Reduce write amplification by checking if data actually changed: `condition = "s.sequenceNum > t.sequenceNum AND (t.name <> s.name OR ...)"`.
    *   **Schema Evolution**: If source schema changes, you must enable `spark.databricks.delta.schema.autoMerge.enabled = true` or use `MERGE WITH SCHEMA EVOLUTION` (DBR 15.4+) within the `foreachBatch` function.

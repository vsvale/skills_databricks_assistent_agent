---
name: cdc
description: Implement Change Data Capture (CDC) pipelines using Delta Live Tables (DLT) and Lakeflow. Covers SCD Type 1 (Overwrite) and SCD Type 2 (History) patterns using `APPLY CHANGES INTO`.
---

# Change Data Capture (CDC)

Change data capture (CDC) is a data integration pattern that captures changes made to data in a source system (inserts, updates, deletes). Processing a CDC feed allows for faster data propagation compared to reading entire datasets.

## Key Concepts

### CDC Feed
A list of changes from the source system. Delta tables generate their own CDC feed known as **Change Data Feed (CDF)**.
Each row in a CDC feed typically contains:
- **Data columns**: The actual data values.
- **Operation**: The type of change (`INSERT`, `UPDATE`, `DELETE`).
- **Sequence Number**: A value to deterministically order changes (e.g., timestamp or log sequence number) to handle out-of-order updates.

### Slowly Changing Dimensions (SCD)
When processing a CDC feed, you must decide how to handle history:

| Type | Description | Use Case |
|------|-------------|----------|
| **SCD Type 1** | **Overwrite**: Keeps only the latest version of the data. No history is preserved. | Correcting errors, updating current contact info, non-critical fields. |
| **SCD Type 2** | **History**: Maintains a full history of changes. New records are created for updates, often with `start_date`, `end_date`, and `is_current` flags. | Tracking evolution of data over time (e.g., address changes, status changes). |

## Implementation with Delta Live Tables (DLT)

The recommended approach for CDC on Databricks is using **Delta Live Tables (DLT)** with the `AUTO CDC` API (formerly `APPLY CHANGES INTO`).

> **Note**: `AUTO CDC` replaces `APPLY CHANGES` APIs but shares the same syntax. Databricks recommends `AUTO CDC`.

### Step 1: Prepare Sample Data
Generate a sample CDC feed with `INSERT`, `UPDATE`, and `DELETE` operations, including out-of-order events.

[generate_sample_cdc_data.py](scripts/generate_sample_cdc_data.py)

### Step 2: Process CDC Feed (SCD Type 1 & 2)
Use `dlt.apply_changes()` (or `AUTO CDC` syntax) to process the feed into target tables.

[process_cdc_dlt.py](scripts/process_cdc_dlt.py)

#### Sequencing Records
To handle out-of-order data, you must specify a sequence column (e.g., timestamp).
- **Multiple Columns**: Use a `STRUCT` to sequence by multiple columns (e.g., `STRUCT(timestamp, id)`).
- **Behavior**: Orders by the first field, then the second to break ties.

#### SCD Type 1 Example (Python)
Updates records directly. No history retained.
```python
dlt.apply_changes(
    target = "target_table",
    source = "source_view",
    keys = ["id"],
    sequence_by = col("sequenceNum"),
    stored_as_scd_type = 1
)
```

#### SCD Type 2 Example (Python)
Retains history. Databricks automatically adds and manages `__START_AT` and `__END_AT` columns.
```python
dlt.apply_changes(
    target = "target_table",
    source = "source_view",
    keys = ["id"],
    sequence_by = col("sequenceNum"),
    stored_as_scd_type = 2
)
```

## Database Replication (Auto CDC)

Replicate an external RDBMS table using a snapshot + continuous CDC feed using the `AUTO CDC` syntax in Lakeflow Pipelines.

### APIs
- **AUTO CDC**: Process changes from a change data feed (CDF).
- **AUTO CDC FROM SNAPSHOT** (Python only): Process changes from database snapshots (periodic or historical).

### Key Features
- **Once Flow**: Initial hydration from a full snapshot (runs only once).
- **Change Flow**: Continuous ingestion from a CDC feed.
- **Auto CDC**: Automatically handles merges and SCD logic.

### ⚠️ Critical Warnings
- **Once Flow Behavior**: The once flow only runs one time. New files that are added to the snapshot location after pipeline creation are ignored.
- **Data Loss Risk**: Performing a full refresh on the target streaming table re-runs the once flow. If the initial snapshot data in cloud storage has been removed, this results in data loss.

### SQL Implementation
Use `CREATE FLOW ... AS AUTO CDC ...`.

[database_replication_sql.sql](scripts/database_replication_sql.sql)

```sql
CREATE FLOW rdbms_orders_hydrate
AS AUTO CDC ONCE INTO rdbms_orders ...

CREATE FLOW rdbms_orders_continuous
AS AUTO CDC INTO rdbms_orders ...
```

### Python Implementation
Use `dp.create_auto_cdc_flow()` or `dp.create_auto_cdc_from_snapshot_flow()`.

[database_replication_py.py](scripts/database_replication_py.py)
[auto_cdc_from_snapshot.py](scripts/auto_cdc_from_snapshot.py)

```python
dp.create_auto_cdc_flow(
    once = True,
    target = "rdbms_orders",
    ...
)
```

## Legacy / Manual Implementation
For manual CDC implementation using Spark SQL `MERGE` and window functions (non-DLT), see:
[references/legacy_manual_cdc.md](references/legacy_manual_cdc.md)

> **Warning**: `MERGE INTO` can produce incorrect results with out-of-sequence records or requires complex logic. `AUTO CDC` is recommended as it automatically handles sequencing.

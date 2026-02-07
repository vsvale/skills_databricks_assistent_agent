---
name: cdc
description: Implement Change Data Capture (CDC) pipelines using Delta Live Tables (DLT) and Lakeflow. Covers SCD Type 1 (Overwrite) and SCD Type 2 (History) patterns using `APPLY CHANGES INTO`.
---

# Change Data Capture (CDC)

Change data capture (CDC) is a data integration pattern that captures changes made to data in a source system (inserts, updates, deletes). Processing a CDC feed allows for faster data propagation compared to reading entire datasets.

## Key Concepts

### Delta Change Data Feed (CDF)
Delta tables can generate their own internal CDC feed known as **Change Data Feed (CDF)**. This records row-level changes (`insert`, `update`, `delete`) and is the foundation for propagating updates in a Databricks Lakehouse.

- **Enable**: Must be explicitly enabled via `TBLPROPERTIES (delta.enableChangeDataFeed = true)`.
- **Schema**: Adds `_change_type`, `_commit_version`, and `_commit_timestamp` metadata columns.
- **Relation to CDC**: CDF provides the *source stream* of changes that DLT or `MERGE INTO` operations consume.

[change_data_feed.md](references/change_data_feed.md)

### Slowly Changing Dimensions (SCD)
When processing a CDC feed, you must decide how to handle history. The processing of a changed data feed is known as slowly changing dimensions (SCD).

| Type | Description | Use Case |
|------|-------------|----------|
| **SCD Type 1** | **Overwrite**: Keeps only the latest version of the data. No history is preserved. It's a straightforward approach where old data is overwritten with new data whenever a change occurs. | Correcting errors, updating current contact info, non-critical fields (e.g., customer email addresses). |
| **SCD Type 2** | **History**: Maintains a full history of changes. New records are created for updates, often with `start_date`, `end_date`, and `is_current` flags (or similar metadata). Each version is timestamped to trace when a change occurred. | Tracking evolution of data over time (e.g., customer address changes, status changes) for analysis. |

## CDC Architecture & Best Practices
The recommended architecture for CDC on Databricks follows the **Medallion Architecture**, leveraging **Delta Live Tables (DLT)** for robust, declarative processing.

### The "Happy Path": Lakeflow & AUTO CDC
For most use cases, use **Lakeflow Pipelines** (or DLT) with the `AUTO CDC` API.
- **Why**: Automatically handles out-of-order data, deduplication, and late-arriving updates which are complex to implement manually.
- **Support**: Native support for SCD Type 1 (Overwrite) and SCD Type 2 (History).
- **Evolution**: AUTO CDC APIs are the standard for Lakeflow Spark Declarative Pipelines (2025/2026). Replace legacy `APPLY CHANGES INTO` usage where possible.

### Medallion Flow
1.  **Bronze (Raw)**: Ingest raw CDC feed (inserts, updates, deletes) from source (e.g., Debezium, Kafka, DMS) into an append-only Delta table.
2.  **Silver (Clean)**: Apply `AUTO CDC` (or `APPLY CHANGES INTO`) to materialize the "current state" or "history" from Bronze.
3.  **Gold (Aggregated)**: Build business-level aggregates on top of Silver tables.

## Implementation with Delta Live Tables (DLT)

The recommended approach for CDC on Databricks is using **Delta Live Tables (DLT)** with the `AUTO CDC` API (formerly `APPLY CHANGES INTO`).

> **Note**: `AUTO CDC` replaces `APPLY CHANGES` APIs but shares the same syntax. Databricks recommends `AUTO CDC`.

### Manual MERGE INTO (Standard Delta)
For standard Delta tables (outside DLT), you can use the SQL `MERGE INTO` command. This supports upserts, deduplication, and manual SCD Type 2.

[merge_into_patterns.md](references/merge_into_patterns.md)

### Step 1: Prepare Sample Data
Generate a sample CDC feed with `INSERT`, `UPDATE`, and `DELETE` operations, including out-of-order events.

[generate_sample_cdc_data.py](scripts/generate_sample_cdc_data.py)

### Tutorial: Build an End-to-End CDC Pipeline
For a complete step-by-step guide on building a Medallion architecture (Bronze -> Silver -> Gold) with DLT CDC, including Python and SQL implementations:

[dlt_cdc_tutorial.md](references/dlt_cdc_tutorial.md)

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

Replicate an external RDBMS table using a snapshot + continuous CDC feed using the `AUTO CDC` syntax in Lakeflow Pipelines. This pattern is ideal for building slowly changing dimension (SCD) tables or keeping a target table in sync with an external system of record.

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
- **Backfill Idempotency**: A once flow only re-runs when the target table is fully refreshed.

### SQL Implementation
Use `CREATE FLOW ... AS AUTO CDC ...`.

[database_replication_sql.sql](scripts/database_replication_sql.sql)

```sql
-- Step 1: Create the target streaming table
CREATE OR REFRESH STREAMING TABLE rdbms_orders;

-- Step 2: Once Flow for initial snapshot (runs once)
CREATE FLOW rdbms_orders_hydrate
AS AUTO CDC ONCE INTO rdbms_orders
FROM stream(full_orders_snapshot)
KEYS (order_id)
SEQUENCE BY timestamp
STORED AS SCD TYPE 1;

-- Step 3: Continuous CDC ingestion (runs continuously)
CREATE FLOW rdbms_orders_continuous
AS AUTO CDC INTO rdbms_orders
FROM stream(rdbms_orders_change_feed)
KEYS (order_id)
SEQUENCE BY timestamp
STORED AS SCD TYPE 1;
```

### Python Implementation
Use `dp.create_auto_cdc_flow()` for both the initial snapshot (with `once=True`) and the continuous feed.

[database_replication_py.py](scripts/database_replication_py.py)

```python
from pyspark import pipelines as dp

# Step 1: Create the target streaming table
dp.create_streaming_table("rdbms_orders")

# Step 2: Once Flow — Load initial snapshot of full RDBMS table
dp.create_auto_cdc_flow(
  flow_name = "initial_load_orders",
  once = True,  # one-time load
  target = "rdbms_orders",
  source = "full_orders_snapshot",  # e.g., ingested from JDBC into bronze
  keys = ["order_id"],
  sequence_by = "timestamp",
  stored_as_scd_type = "1"
)

# Step 3: Change Flow — Ingest ongoing CDC stream from source system
dp.create_auto_cdc_flow(
  flow_name = "orders_incremental_cdc",
  target = "rdbms_orders",
  source = "rdbms_orders_change_feed", # e.g., ingested from Kafka or Debezium
  keys = ["order_id"],
  sequence_by = "timestamp",
  stored_as_scd_type = "1"
)
```

## Legacy / Manual Implementation
For manual CDC implementation using Spark SQL `MERGE` and window functions (non-DLT), see:
[references/manual_streaming_cdc.md](references/manual_streaming_cdc.md)

> **Warning**: `MERGE INTO` can produce incorrect results with out-of-sequence records or requires complex logic. `AUTO CDC` is recommended as it automatically handles sequencing.

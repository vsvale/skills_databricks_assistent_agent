# Tutorial: Build an ETL Pipeline with CDC (Delta Live Tables)

This step-by-step guide demonstrates how to build a production-grade ETL pipeline using Delta Live Tables (DLT) to process Change Data Capture (CDC) feeds. It covers the Medallion architecture (Bronze -> Silver -> Gold).

**References**:
- See [REFERENCES.md](REFERENCES.md) for official documentation and tutorials.

## Prerequisites
- Databricks Workspace with Unity Catalog enabled (recommended).
- **Pro** or **Advanced** product edition (required for CDC support).
- Cluster with DBR 11.3+ (DLT usually manages this).

## Pipeline Architecture
1.  **Bronze (Ingest)**: Reads raw JSON files from cloud storage using Auto Loader (`cloudFiles`).
2.  **Silver (Clean)**: Uses `APPLY CHANGES INTO` to merge updates/deletes and handle SCD Type 1/2.
3.  **Gold (Aggregate)**: Computes business metrics from the clean Silver data.

---

## Python Implementation

Full script: [dlt_cdc_pipeline.py](../scripts/dlt_cdc_pipeline.py)

### 1. Setup & Imports
```python
import dlt
from pyspark.sql.functions import col, expr
```

### 2. Bronze Layer: Ingest Raw Data
We use Auto Loader (`format("cloudFiles")`) to robustly ingest new files as they arrive.

```python
@dlt.table(
    comment="Raw customer data from cloud storage",
    table_properties={"quality": "bronze"}
)
def bronze_customers():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .load("/databricks-datasets/retail-org/customers/")
    )
```

### 3. Silver Layer: Process CDC
We materialize the "current state" (SCD Type 1) of the customers table.

```python
dlt.create_streaming_table("silver_customers")

dlt.apply_changes(
    target = "silver_customers",
    source = "bronze_customers",
    keys = ["customer_id"],
    sequence_by = col("operation_date"),
    apply_as_deletes = expr("operation = 'DELETE'"),
    except_column_list = ["operation", "operation_date", "_rescued_data"],
    stored_as_scd_type = 1
)
```
**Key Parameters**:
- `keys`: Primary key(s) to identify unique records.
- `sequence_by`: Column to determine the order of updates (critical for out-of-order data).
- `apply_as_deletes`: Condition to identify rows that should be deleted.
- `except_column_list`: Metadata columns to exclude from the final target schema.
- `stored_as_scd_type`: `1` for Overwrite (latest), `2` for History (adds `__START_AT`, `__END_AT`).

### 4. Gold Layer: Aggregates
Create a live table (materialized view) for reporting.

```python
@dlt.table(
    comment="Customer counts by state"
)
def gold_customer_counts_by_state():
    return (
        dlt.read("silver_customers")
        .groupBy("state")
        .count()
        .withColumnRenamed("count", "customer_count")
    )
```

---

## SQL Implementation

Full script: [dlt_cdc_pipeline.sql](../scripts/dlt_cdc_pipeline.sql)

### 1. Bronze Layer: Ingest Raw Data
```sql
CREATE OR REFRESH STREAMING TABLE bronze_customers
AS SELECT * FROM cloud_files(
  "/databricks-datasets/retail-org/customers/",
  "json",
  map("cloudFiles.inferColumnTypes", "true")
);
```

### 2. Silver Layer: Process CDC
```sql
CREATE OR REFRESH STREAMING TABLE silver_customers;

APPLY CHANGES INTO LIVE.silver_customers
FROM STREAM(LIVE.bronze_customers)
KEYS (customer_id)
APPLY AS DELETE WHEN operation = 'DELETE'
SEQUENCE BY operation_date
COLUMNS * EXCEPT (operation, operation_date, _rescued_data)
STORED AS SCD TYPE 1;
```

### 3. Gold Layer: Aggregates
```sql
CREATE LIVE TABLE gold_customer_counts_by_state
AS SELECT
  state,
  count(*) as customer_count
FROM LIVE.silver_customers
GROUP BY state;
```

---

## Configuration & Tuning

### Pipeline Settings
When creating the DLT pipeline:
*   **Product Edition**: Select **Pro** or **Advanced**.
*   **Pipeline Mode**:
    *   **Triggered**: Good for batch CDC (e.g., daily/hourly). Saves costs.
    *   **Continuous**: Good for low-latency streaming CDC.
*   **Channel**: `Current` is usually stable.

### Performance Tuning
1.  **Partitioning**: If the Silver table is large, partition it by a low-cardinality column (e.g., `state` or `date`) using `@dlt.table(partition_cols=["state"])` (Python) or `PARTITIONED BY` (SQL).
2.  **Cluster Sizing**: Use Enhanced Autoscaling.
3.  **Sequence By**: Ensure `sequence_by` is deterministic. If using timestamps, consider adding a secondary tie-breaker like an offset or ID: `sequence_by = struct(ts, offset)`.

## Limitations & Notes
*   **SCD Type 2 History**: DLT manages `__START_AT` and `__END_AT`. Do not try to manually update these.
*   **Delete Propagation**: `apply_as_deletes` physically removes rows in SCD Type 1, or closes the validity window in SCD Type 2.
*   **Schema Evolution**: `APPLY CHANGES INTO` supports schema evolution. New columns in the source are added to the target automatically (unless excluded).

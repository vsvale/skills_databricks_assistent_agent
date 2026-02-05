# Database Replication using AUTO CDC (Python)
# This pattern replicates an external RDBMS table using a snapshot + CDC feed.
# Uses pyspark.pipelines (Lakeflow Pipelines API)

from pyspark import pipelines as dp

# Define paths (typically passed as parameters)
# orders_snapshot_path = "..."
# orders_cdc_path = "..."

# 1. Source Views

@dp.view()
def full_orders_snapshot():
    """
    Reads initial snapshot from cloud storage.
    """
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.includeExistingFiles", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(orders_snapshot_path)
        .select("*")
    )

@dp.view()
def rdbms_orders_change_feed():
    """
    Reads incremental CDC feed.
    """
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.includeExistingFiles", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(orders_cdc_path)
    )

# 2. Create Target Streaming Table
dp.create_streaming_table("rdbms_orders")

# 3. Initial Hydration (Once Flow)
# Loads history; runs only once (once=True).
# WARNING: New files added to snapshot path after pipeline creation are ignored.
# WARNING: If snapshot data is removed from storage, full refresh will cause data loss.
dp.create_auto_cdc_flow(
    flow_name = "initial_load_orders",
    once = True,
    target = "rdbms_orders",
    source = "full_orders_snapshot",
    keys = ["order_id"],
    sequence_by = "timestamp",
    stored_as_scd_type = "1"
)

# 4. Continuous Ingestion (Change Flow) - SCD Type 1
# Applies ongoing changes from the CDC feed.
dp.create_auto_cdc_flow(
    flow_name = "orders_incremental_cdc",
    target = "rdbms_orders",
    source = "rdbms_orders_change_feed",
    keys = ["order_id"],
    sequence_by = "timestamp",
    stored_as_scd_type = "1"
)

# 5. SCD Type 2 Example (History)
# Tracks history; adds __START_AT and __END_AT.
# Sequence by multiple columns: use a struct column in source view or expression if supported.
# Typically, ensure source view has a combined sequencing column.
dp.create_auto_cdc_flow(
    flow_name = "orders_incremental_cdc_scd2",
    target = "rdbms_orders_scd2",
    source = "rdbms_orders_change_feed",
    keys = ["order_id"],
    sequence_by = "timestamp", # Or struct column
    stored_as_scd_type = "2"
)

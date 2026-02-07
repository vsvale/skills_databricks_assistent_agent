from pyspark import pipelines as dp

# Define source views for snapshot and continuous feed
@dp.view()
def full_orders_snapshot():
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
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.includeExistingFiles", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(orders_cdc_path)
    )

# Step 1: Create the target streaming table
dp.create_streaming_table("rdbms_orders")

# Step 2: Once Flow — Load initial snapshot of full RDBMS table
# This flow runs only once to hydrate the table
dp.create_auto_cdc_flow(
    flow_name = "initial_load_orders",
    once = True,
    target = "rdbms_orders",
    source = "full_orders_snapshot",
    keys = ["order_id"],
    sequence_by = "timestamp",
    stored_as_scd_type = "1"
)

# Step 3: Change Flow — Ingest ongoing CDC stream from source system
# This flow runs continuously to apply updates
dp.create_auto_cdc_flow(
    flow_name = "orders_incremental_cdc",
    target = "rdbms_orders",
    source = "rdbms_orders_change_feed",
    keys = ["order_id"],
    sequence_by = "timestamp",
    stored_as_scd_type = "1"
)

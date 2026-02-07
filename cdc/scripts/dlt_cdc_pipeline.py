import dlt
from pyspark.sql.functions import col, expr

# ==========================================
# Bronze Layer: Ingest Raw Data
# ==========================================
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

# ==========================================
# Silver Layer: Process CDC (SCD Type 1)
# ==========================================
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

# ==========================================
# Gold Layer: Aggregates
# ==========================================
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

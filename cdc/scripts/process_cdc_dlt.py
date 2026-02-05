import dlt
from pyspark.sql.functions import col, expr

# Source Configuration
SOURCE_CATALOG = "main"
SOURCE_SCHEMA = "default"
SOURCE_TABLE = "employees_cdf"

@dlt.view
def employees_cdc_source():
    """
    Reads the CDC feed as a stream.
    Requires the source table to be created first (see generate_sample_cdc_data.py).
    """
    return spark.readStream.format("delta").table(f"{SOURCE_CATALOG}.{SOURCE_SCHEMA}.{SOURCE_TABLE}")

# -------------------------------------------------------------------------
# SCD Type 1: Overwrite (Keep latest)
# -------------------------------------------------------------------------
dlt.create_streaming_table("employees_scd_1")

dlt.apply_changes(
    target = "employees_scd_1",
    source = "employees_cdc_source",
    keys = ["id"],
    sequence_by = col("sequenceNum"),
    apply_as_deletes = expr("operation = 'DELETE'"),
    except_column_list = ["operation", "sequenceNum"],
    stored_as_scd_type = 1
)

# -------------------------------------------------------------------------
# SCD Type 2: History (Keep all versions)
# -------------------------------------------------------------------------
dlt.create_streaming_table("employees_scd_2")

dlt.apply_changes(
    target = "employees_scd_2",
    source = "employees_cdc_source",
    keys = ["id"],
    sequence_by = col("sequenceNum"),
    apply_as_deletes = expr("operation = 'DELETE'"),
    except_column_list = ["operation", "sequenceNum"],
    stored_as_scd_type = 2
)

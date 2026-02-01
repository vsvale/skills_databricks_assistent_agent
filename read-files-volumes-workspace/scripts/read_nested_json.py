# read_nested_json.py
# Examples: Read and query nested / semi-structured JSON in PySpark.
# Use column:path and ::type semantics (same as Databricks SQL) via selectExpr, or from_json/get_json_object.

from pyspark.sql.functions import col, from_json, get_json_object
from pyspark.sql.types import StructType, StructField, DoubleType, StringType

# Assume we have a DataFrame with a column 'raw' containing JSON strings
# (e.g. after reading with primitivesAsString or a single string column)

# --- selectExpr with : path and :: cast (Databricks / Spark 3.x) ---
# Extract top-level
# df = df.selectExpr("raw:owner AS owner")

# Nested field and cast
# df = df.selectExpr("raw:store.bicycle.price::double AS price", "raw:store.bicycle.color AS color")

# Array element
# df = df.selectExpr("raw:store.fruit[0].type AS first_fruit", "raw:store.fruit[*].weight AS weights")

# --- Example: create sample data then query ---
data = [
    ('{"store": {"bicycle": {"price": 19.95, "color": "red"}, "fruit": [{"weight": 8, "type": "apple"}]}, "owner": "amy"}',),
]
df = spark.createDataFrame(data, ["raw"])

# Extract nested fields with : and ::
df_out = df.selectExpr(
    "raw:owner AS owner",
    "raw:store.bicycle.price::double AS price",
    "raw:store.bicycle.color AS color",
    "raw:store.fruit[0].type AS first_fruit"
)
df_out.show(truncate=False)

# --- from_json for a struct column ---
bicycle_schema = StructType([
    StructField("price", DoubleType()),
    StructField("color", StringType()),
])
df_struct = df.withColumn(
    "bicycle",
    from_json(get_json_object(col("raw"), "$.store.bicycle"), bicycle_schema)
).select("raw", "bicycle.price", "bicycle.color")
df_struct.show(truncate=False)

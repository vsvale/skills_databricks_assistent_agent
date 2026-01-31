# read_json_volume.py
# Examples: Read JSON from Unity Catalog Volumes via PySpark.
# Run in a Databricks notebook; replace catalog, db, volume_name, and path as needed.

# --- Single-line JSON (one object per line; default, splittable) ---
catalog = "main"
db = "default"
volume_name = "my_volume"
path = f"/Volumes/{catalog}/{db}/{volume_name}/credit_bureau"

# Option 1: shorthand
sdf = spark.read.json(path)

# Option 2: explicit format
sdf = spark.read.format("json").load(path)

# Schema is inferred by default
sdf.printSchema()
sdf.show(5, truncate=False)


# --- Multi-line JSON (whole file is one JSON; set multiline=True) ---
path_multiline = f"/Volumes/{catalog}/{db}/{volume_name}/multi_line_data"
sdf_multiline = (
    spark.read
    .option("multiline", "true")
    .format("json")
    .load(path_multiline)
)


# --- With options (rescued data, charset, date/timestamp format) ---
sdf_with_opts = (
    spark.read
    .format("json")
    .option("multiline", "true")
    .option("rescuedDataColumn", "_rescued_data")
    .option("charset", "UTF-8")
    .option("dateFormat", "yyyy-MM-dd")
    .option("timestampFormat", "yyyy-MM-dd'T'HH:mm:ss.SSSXXX")
    .load(path)
)


# --- Explicit schema (no inference) ---
from pyspark.sql.types import StructType, StructField, StringType, LongType

schema = StructType([
    StructField("id", StringType(), True),
    StructField("value", LongType(), True),
])
sdf_schema = spark.read.schema(schema).format("json").load(path)

# read_parquet_volume.py
# Examples: Read Parquet from Unity Catalog Volumes via PySpark.

catalog = "main"
db = "default"
volume_name = "my_volume"
path = f"/Volumes/{catalog}/{db}/{volume_name}/data.parquet"

# --- Shorthand ---
sdf = spark.read.parquet(path)

# --- Explicit format ---
sdf = spark.read.format("parquet").load(path)

# --- Directory of Parquet files (e.g. partitioned) ---
path_dir = f"/Volumes/{catalog}/{db}/{volume_name}/parquet_data/"
sdf_dir = spark.read.parquet(path_dir)

# --- With options (e.g. merge schema for evolving schema) ---
sdf_merge = (
    spark.read
    .format("parquet")
    .option("mergeSchema", "true")
    .load(path_dir)
)

sdf_merge.printSchema()
sdf_merge.show(5)

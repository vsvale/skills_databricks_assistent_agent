# read_csv_volume.py
# Examples: Read CSV from Unity Catalog Volumes via PySpark.
# Same path pattern works for workspace with file:/Workspace/... prefix.

catalog = "main"
db = "default"
volume_name = "my_volume"
path = f"/Volumes/{catalog}/{db}/{volume_name}/data.csv"

# --- With header and default delimiter ---
sdf = (
    spark.read
    .format("csv")
    .option("header", "true")
    .load(path)
)

# --- Custom delimiter (e.g. tab) ---
sdf_tab = (
    spark.read
    .format("csv")
    .option("header", "true")
    .option("delimiter", "\t")
    .load(path)
)

# --- With schema and rescued data ---
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

schema = StructType([
    StructField("id", StringType(), True),
    StructField("name", StringType(), True),
    StructField("amount", DoubleType(), True),
])
sdf_schema = (
    spark.read
    .format("csv")
    .option("header", "true")
    .option("rescuedDataColumn", "_rescued_data")
    .schema(schema)
    .load(path)
)

# --- Directory of CSV files ---
path_dir = f"/Volumes/{catalog}/{db}/{volume_name}/csv_files/"
sdf_dir = spark.read.option("header", "true").format("csv").load(path_dir)

sdf_dir.show(5)

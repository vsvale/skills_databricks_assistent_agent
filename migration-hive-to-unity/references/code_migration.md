# Code Migration Patterns

## 0. Initial Setup & Operations
- **Explicit is better than implicit**.
- **Unified Repositories**: Avoid copy-paste; use unified repos.
- **Stream Writers**: Use explicit `.writeStream` instead of helper functions like `create_stream_writer`.

**Pattern: Explicit Stream Writer**
*Before*:
```python
bronzeWriter = create_stream_writer_liquid_cluster(
    dataframe=df_transformed_Bronze,
    checkpoint=bronzeCheckpoint,
    name=namedBronzeStream,
    availableNow=True,
    mergeSchema=True,
    mode="append"
)
bronzeWriter.start(bronzePath).awaitTermination()
```
*After*:
```python
bronzeWriter = (df_transformed_Bronze.writeStream
                .outputMode("append")
                .option("checkpointLocation", bronzeCheckpoint)
                .queryName(namedBronzeStream)
                .trigger(availableNow=True)
                .option("mergeSchema", True)
)
bronzeWriter.toTable(bronzeTable).awaitTermination()
```

**Pattern: Reprocess & Truncate (Volumes vs Tables)**
*Before*:
```python
spark.sql(f"TRUNCATE TABLE delta.`{bronzePath}`")
dbutils.fs.rm(bronzeCheckpoint, True)
```
*After*:
```python
# 1. Clean Checkpoint in Volume
dbutils.fs.rm(bronzeCheckpoint, True)
dbutils.fs.mkdirs(bronzeCheckpoint) # Re-create empty directory

# 2. Truncate Managed Table
spark.sql(f"TRUNCATE TABLE {bronzeTable}")
```

**Pattern: Helper Function Refactoring (Wrapper Update)**
If you use a shared wrapper function, update it to support `.toTable()`:

*Before*:
```python
def create_stream_writer(dataframe, checkpoint, name, trigger_once, mergeSchema):
    # ... setup stream_writer ...
    return stream_writer # Returns DataStreamWriter
# Usage: create_stream_writer(...).start(path)
```
*After*:
```python
def create_stream_writer(dataframe, checkpoint, name, trigger_once, mergeSchema, toTable):
    # ... setup stream_writer ...
    return stream_writer.toTable(toTable) # Returns StreamingQuery
# Usage: create_stream_writer(..., toTable="catalog.schema.table")
```

**Pattern: Namespace Migration (Hive to Unity)**
*Before*:
```python
spark.catalog.tableExists(f"db_auth_silver.tb_{table}")
spark.sql(f"select * from db_auth_silver.tb_{table}")
```
*After*:
```python
spark.catalog.tableExists(f"auth_prd.silver.tb_{table}")
spark.sql(f"select * from auth_prd.silver.tb_{table}")
```


**Pattern: Shared Utils**
*Before*:
```python
%run /Users/ecs-databricks@br.experian.com/jobs/utils
```
*After*:
```python
import sys
sys.path.append("/Workspace/Shared/ecs-dataops-shared-utils/")
from util_import import *
```

## 1. RAW Layer (S3 -> Volumes)
- **Rule**: Buckets `Raw` and `Sensitive` become **Volumes**.
- **Path Construction**: Construct the full path first, then check if it's a Delta table.

**Pattern: Path Definition**
*Before*:
```python
bucketRaw = f"ecs-observability-datadog-logging-prd/auth/back"
rawPath   = "s3://{}".format(bucketRaw)
```
*After*:
```python
# Check existing volumes first (see script)
rawPath = "/Volumes/observability_prd/raw/ecs-observability-datadog-logging-prd/auth/back/"
```

**Pattern: Read Stream (Path vs Volume)**
*Before*:
```python
rawDF = read_stream_raw(spark, rawPathDay, schema_bronze_back)
```
*After*:
```python
rawDF = (
  spark.readStream.format("json")
        .schema(schema_bronze_back)
        .options(maxBytesPerTrigger=str(5 * 1024 * 1024 * 1024))
        .load(rawPathDay) # rawPathDay is now a Volume path
)
```

**Pattern: Autoloader with SQS**
*Before*:
```python
.option("cloudFiles.queueUrl", sqsPath)
```
*After*:
```python
.option("cloudFiles.queueUrl", sqsPath)
.option("databricks.serviceCredential", "unity-xxxx-service-credential")
```

**Pattern: Path to Table (Read)**
*Before*:
```python
goldPath = "s3://bucket/path"
goldTable = DeltaTable.forPath(spark, goldPath)
# OR
bronzeDF = read_stream_delta(spark, bronzePath)
```
*After*:
```python
goldTable = spark.table('corp_prd.sensitive.table_name')
# OR
bronzeDF = spark.readStream.table("auth_prd.bronze.tb_source_back")
```

**Pattern: Table Creation (DDL)**
*Before*:
```python
# Checks DeltaTable.isDeltaTable... then:
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {tableName} ({schema})
    USING delta LOCATION '{silverPath}'
    CLUSTER BY (col)
""")
```
*After*:
```python
# Managed Table - No LOCATION
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS auth_prd.silver.tb_{name} ({schema})
    CLUSTER BY (col)
""")
```

**Pattern: SQL Reference**
*Before*:
```sql
select * from delta.`s3a://bucket/path`
```
*After*:
```sql
select * from catalog.schema.table
```

**Pattern: Write to Table**
*Before*:
```python
df.write.mode("overwrite").save(path)
```
*After*:
```python
df.write.mode("overwrite").saveAsTable("catalog.schema.table")
```

**Pattern: Liquid Clustering (Replace PartitionBy)**
*Before*:
```python
df.write.partitionBy("date").save(path)
```
*After*:
```python
df.write.saveAsTable("catalog.schema.table")
spark.sql("ALTER TABLE catalog.schema.table CLUSTER BY AUTO")
# Or in CTAS: CLUSTER BY (col)
```

**Pattern: Optimize and Vacuum**
*Before*:
```python
spark.sql(f"OPTIMIZE delta.`{path}`")
DeltaTable.forPath(spark, path).vacuum()
```
*After*:
```python
spark.sql(f"OPTIMIZE catalog.schema.table")
spark.sql(f"VACUUM catalog.schema.table")
```

## 2. BRONZE Layer (Managed Tables)
- **Rule**: Use **Managed Tables** (default). Do not use External Tables unless specified.

**Pattern: Path to Table**
*Before*:
```python
bronzePath = "s3://serasaexperian-{}".format(bucketBronze)
```
*After*:
```python
bronzePath = f"auth_prd.bronze.tb_{source}_back"
```

**Pattern: Metadata Replacement**
*Before*:
```python
.withColumn("file_name_raw", input_file_name())
```
*After*:
```python
.withColumn("file_name_raw", col("_metadata.file_path"))
```

## 3. Checkpoints (S3 -> Managed Volumes)
- **Rule**: Every catalog has a `checkpoints` managed volume in Bronze, Silver, Gold.

**Pattern: Checkpoint Path**
*Before*:
```python
bronzeCheckpoint = "s3://serasaexperian-ecs-datalakehouse-prd-checkpoints/..."
```
*After*:
```python
bronzeCheckpoint = f"/Volumes/auth_prd/bronze/checkpoints/ecs-datalakehouse-prd-checkpoints/..."
```

## 4. SILVER Layer
- **Rule**: Bronze Path -> Bronze Table; Silver Path -> Silver Table.

**Pattern: Merge (ForPath vs ForName)**
*Before*:
```python
deltaTable = DeltaTable.forPath(spark, silverPath)
```
*After*:
```python
deltaTable = DeltaTable.forName(spark, "auth_prd.silver.table_name")
```

**Pattern: Upsert Logic**
*Before*:
```python
microBatchOutputDF._jdf.sparkSession().sql(f"MERGE INTO delta.`{path}`...")
```
*After*:
```python
microBatchOutputDF.sparkSession.sql(f"MERGE INTO {table_name}...")
```

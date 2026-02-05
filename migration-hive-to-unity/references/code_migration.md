# Code Migration Patterns

## 1. Reading Data (Input)
**Pattern: S3 Path to Volume Path**
*Before*:
```python
df = spark.read.load("s3://bucket/path/to/data")
```
*After*:
```python
df = spark.read.load("/Volumes/catalog/schema/volume/path/to/data")
```
*Note*: Ensure the Volume is mounted/created in Unity Catalog.

**Pattern: External Table to Managed Table**
*Before*:
```python
df = spark.read.table("legacy_db.table_name")
# or
df = spark.read.load("s3://bucket/external_table_path")
```
*After*:
```python
df = spark.read.table("catalog.schema.table_name")
```

## 2. Writing Data (Output)
**Pattern: Path-based Write to Table-based Write**
*Before*:
```python
df.write.format("delta").save("s3://bucket/output_path")
```
*After*:
```python
df.write.format("delta").saveAsTable("catalog.schema.output_table")
```

**Pattern: Streaming Checkpoints**
*Before*:
```python
checkpoint_path = "s3://bucket/checkpoints/job_name"
```
*After*:
```python
# Create a 'checkpoints' volume in your schema
checkpoint_path = "/Volumes/catalog/schema/checkpoints/job_name"
```

## 3. Metadata Columns
**Pattern: Input File Name**
*Before*:
```python
from pyspark.sql.functions import input_file_name
df = df.withColumn("filename", input_file_name())
```
*After (Autoloader/Volumes)*:
```python
from pyspark.sql.functions import col
# Available automatically in Autoloader
df = df.withColumn("filename", col("_metadata.file_path"))
```

## 4. Silver Layer Processing
**Pattern: Reading Bronze (Stream)**
*Before*:
```python
# Custom helper to read from S3 path
df = read_stream_delta(spark, "s3://bucket/bronze/table")
```
*After*:
```python
df = spark.readStream.table("catalog.schema.bronze_table")
```

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

## 5. Advanced Migration Patterns: Reusable Classes
Encapsulate logic in classes for reusability and testing.

See [scripts/utils_migration.py](../scripts/utils_migration.py) for the full implementation of:
- `RawToBronzeProcessor`: Batch ingestion from Raw to Bronze with control fields.
- `BronzeToSilverProcessor`: Batch processing from Bronze to Silver with standard cleaning.

**Example Usage:**
```python
from utils_migration import RawToBronzeProcessor

processor = RawToBronzeProcessor(spark)
processor.process(
    source_path="/Volumes/catalog/schema/volume/data",
    target_table="catalog.schema.tb_data_bronze",
    source_table_name="tb_data",
    file_format="json"
)
```

## 6. Security & PII
**Pattern: Column Encryption**
Use the platform cryptography library for PII fields. Do not persist unencrypted PII in Bronze/Silver.

```python
try:
    from lake_crypto import encrypt, decrypt
except ImportError:
    # Handle missing library in local/dev env
    print("Crypto lib not found")
    def encrypt(x): return x
    def decrypt(x): return x

# Usage
# encrypted_value = encrypt(sensitive_data)
# decrypted_value = decrypt(encrypted_value)  # Only for processing; do not persist in clear text
```

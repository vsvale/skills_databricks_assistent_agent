# Volumes Usage & Naming

## Overview
Volumes are logical mount points for Object Storage (S3) in Unity Catalog.
- **Use Cases**: Raw files (JSON, CSV, Parquet), Libraries (.whl, .jar), Checkpoints, Logs, Unstructured data (PDF, Images).
- **Restriction**: Do **NOT** use Volumes for Delta Tables (use Managed Tables instead).

## Naming Convention
Transform S3 paths to Volume names:
1. Remove `s3://` prefix.
2. Lowercase.
3. Replace `_` and `/` with `-`.
4. Remove common prefixes (e.g., `serasaexperian-ecs-datalakehouse-prd-`).
5. **Example**: `s3://.../ecs/fraude/premium/` -> `raw-ecs-fraude-premium`.

## Types
- **Managed Volume**: Stored in the default storage location of the schema. Good for checkpoints, temporary files.
- **External Volume**: Points to a specific S3 path (e.g., Raw ingestion bucket).

## Code Patterns

### Reading from Volume
```python
# SQL
SELECT * FROM parquet.`/Volumes/catalog/schema/volume/path`

# PySpark
df = spark.read.load("/Volumes/catalog/schema/volume/path")
```

### Writing to Volume
```python
file_path = "/Volumes/catalog/schema/volume/file.csv"
df.write.save(file_path)
```

### Checkpoints (Critical)
Always use Managed Volumes for checkpoints to ensure portability and permission consistency.
```python
checkpoint = f"/Volumes/{catalog}/{schema}/checkpoints/{table_name}"
```

## Anti-Patterns
- **No External Tables on Volumes**: Do not point a table `LOCATION` to a Volume path.
- **No Overlapping Volumes**: You cannot create a volume at `.../a/` and another at `.../a/b/`. Choose the most granular path needed.

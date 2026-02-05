# Unity Catalog Standards

## 1. Catalog & Schema Strategy

### Overview
- **Catalog Strategy**: One catalog per Product or Team (e.g., `premium_prd`, `models_dev`).
- **Naming Convention**: `<product/team>_<environment>` (no abbreviations preferred).
- **Storage**: `s3://serasaexperian-ecs-datalakehouse-<env>-<product>`.
- **Access**: Access is managed via `USE CATALOG` and `USE SCHEMA` statements.

### Standard Schemas
| Schema | Purpose | Access | Storage Type |
|--------|---------|--------|--------------|
| **raw** | Ingestion landing zone. Encrypted PII. | Service Principal only. | **Volumes** (External) |
| **bronze** | Raw Delta tables (encrypted). | Service Principal only. | Managed Tables |
| **silver** | Refined/Enriched data. Internal usage (masked PII). | All Users (Read). | Managed Tables |
| **gold** | Aggregated/Business data. Views/Materialized Views. | All Users (Read). | Managed Tables |
| **control** | Job metadata, parameters, control tables. | Service Principal only. | Managed Tables |
| **delivery** | Exports for external systems (often PII decrypted). | Service Principal only. | Managed Tables |
| **sandbox** | Prototyping/Ad-hoc. Managed by team. | Team members (Read/Write). | Managed Tables |
| **sensitive** | Highly restricted PII. | Request Access required. | Managed Tables |
| **temp** | Temporary processing tables. | Team managed (auto-delete). | Managed Tables |
| **vector** | Vector Search endpoints/indexes. | Service Principal only. | Vector Search Index |

### Migration Notes
- **Frozen Hive**: Hive Metastore databases are frozen (DENY MODIFY/CREATE) during migration.
- **3-Level Namespace**: Always use `catalog.schema.table`.
- **Code Update**:
  - *Before*: `db_analytics.table`
  - *After*: `analytics_prd.gold.table`
  - *SQL*: `USE CATALOG x; USE SCHEMA y;` or fully qualified names.

---

## 2. Managed vs External Tables

### Policy: Prefer Managed Tables
Databricks recommends **Managed Tables** as the default for Unity Catalog.
- **Benefits**: Predictive Optimization (Auto OPTIMIZE/VACUUM), simplified permission management, better performance.
- **Behavior**: Dropping the table deletes data and metadata (recoverable via `UNDROP` for 7 days).

### Migration Patterns

#### Creating a Managed Table
**Do NOT** specify a `LOCATION` or `path` option.

**SQL Pattern**:
```sql
-- Before (External)
CREATE TABLE demo_prd.sandbox.table
LOCATION 's3://bucket/path'

-- After (Managed)
CREATE TABLE demo_prd.sandbox.table
```

**PySpark Pattern**:
```python
# Before
df.write.format('delta').option('path', '/dbfs/...').saveAsTable('table')

# After
df.write.saveAsTable('catalog.schema.table')
```

#### Deep Clone & CTAS
- Tables created via `DEEP CLONE` or `CTAS` are automatically **Managed** if no location is specified.
- Use `CTAS` to migrate DBFS root tables easily.

### Exceptions (External Tables)
- Only use External Tables if data must be accessed by tools *outside* Databricks (rare).
- Requires `MANAGE` permission to drop.

---

## 3. Volumes Usage & Naming

### Overview
Volumes are logical mount points for Object Storage (S3) in Unity Catalog.
- **Use Cases**: Raw files (JSON, CSV, Parquet), Libraries (.whl, .jar), Checkpoints, Logs, Unstructured data (PDF, Images).
- **Restriction**: Do **NOT** use Volumes for Delta Tables (use Managed Tables instead).

### Naming Convention
Transform S3 paths to Volume names:
1. Remove `s3://` prefix.
2. Lowercase.
3. Replace `_` and `/` with `-`.
4. Remove common prefixes (e.g., `serasaexperian-ecs-datalakehouse-prd-`).
5. **Example**: `s3://.../ecs/fraude/premium/` -> `raw-ecs-fraude-premium`.

### Types
- **Managed Volume**: Stored in the default storage location of the schema. Good for checkpoints, temporary files.
- **External Volume**: Points to a specific S3 path (e.g., Raw ingestion bucket).

### Code Patterns

#### Reading from Volume
```python
# SQL
SELECT * FROM parquet.`/Volumes/catalog/schema/volume/path`

# PySpark
df = spark.read.load("/Volumes/catalog/schema/volume/path")
```

#### Writing to Volume
```python
file_path = "/Volumes/catalog/schema/volume/file.csv"
df.write.save(file_path)
```

#### Checkpoints (Critical)
Always use Managed Volumes for checkpoints to ensure portability and permission consistency.
```python
checkpoint = f"/Volumes/{catalog}/{schema}/checkpoints/{table_name}"
```

### Anti-Patterns
- **No External Tables on Volumes**: Do not point a table `LOCATION` to a Volume path.
- **No Overlapping Volumes**: You cannot create a volume at `.../a/` and another at `.../a/b/`. Choose the most granular path needed.

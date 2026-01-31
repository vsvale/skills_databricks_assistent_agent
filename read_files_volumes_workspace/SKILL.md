---
name: read-files-volumes-workspace
description: Read files in Databricks from Unity Catalog Volumes and workspace using PySpark and SQL. Covers JSON (single-line and multi-line), CSV, Parquet, semi-structured JSON, and workspace paths. Use when loading data from /Volumes/ or file:/Workspace/, reading JSON/CSV/Parquet in notebooks, or when the user needs PySpark or SQL examples without Scala.
---

# Read Files from Volumes and Workspace in Databricks

This skill provides patterns and examples for reading files in Databricks from **Unity Catalog Volumes** and **workspace** using **PySpark** and **SQL** only. All examples are in Python and SQL; convert any Scala references to PySpark.

## When to Use This Skill

- Load data from `/Volumes/{catalog}/{schema}/{volume}/path/to/files`
- Read workspace files (e.g. `file:/Workspace/Users/<user>/...` or repo paths)
- Read JSON, CSV, Parquet, or other supported formats
- Handle single-line vs multi-line JSON, nested JSON, or semi-structured JSON
- Need ready-to-run PySpark or SQL snippets

## Path Conventions

| Location | PySpark / Spark path | SQL path | Notes |
|---------|----------------------|----------|--------|
| **Unity Catalog Volume** | `/Volumes/{catalog}/{schema}/{volume}/path` | Same; use in `LOAD` or table options | Recommended for non-tabular data. No URI scheme. |
| **Workspace (user dir)** | `file:/Workspace/Users/<user-folder>/path` | `file:/Workspace/Users/<user-folder>/file.json` | `file:` required for Spark and SQL. |
| **Workspace (repo)** | `file:/Workspace/Repos/<user>/<repo>/path` or use `os.getcwd()` in notebook | Same | In notebooks, CWD is often the repo root. |

For Spark to read workspace files you must use the **fully qualified path** with the `file:` scheme. Getting the current path in a notebook: `f"file:{os.getcwd()}/data/file.json"`.

References: [Work with files on Databricks](https://docs.databricks.com/aws/en/files/), [Programmatically interact with workspace files](https://docs.databricks.com/aws/en/files/workspace-interact).

## JSON

### Volume: single-line JSON (PySpark)

One JSON object per line; schema can be inferred. Preferred for parallel reads.

```python
# Replace catalog, schema, volume, and path as needed
catalog = "main"
db = "default"
volume_name = "my_volume"
path = f"/Volumes/{catalog}/{db}/{volume_name}/credit_bureau"

sdf = spark.read.format("json").load(path)
# Or shorthand:
sdf = spark.read.json(path)
```

### Volume: multi-line JSON (PySpark)

Whole file is one JSON array or multi-line object. Set `multiline=True`; file is not splittable.

```python
path = f"/Volumes/{catalog}/{db}/{volume_name}/multi_line_data"
sdf = spark.read.option("multiline", "true").format("json").load(path)
```

### Workspace: JSON (PySpark)

Use `file:` and full path. With repo-backed notebook, `os.getcwd()` is often the repo root.

```python
import os
# From repo-relative path
path = f"file:{os.getcwd()}/data/events.json"
sdf = spark.read.json(path)

# Or explicit workspace path
path = "file:/Workspace/Users/<user@domain>/data/events.json"
sdf = spark.read.format("json").load(path)
```

### JSON options (PySpark)

- `multiline` – multi-line JSON (default `false`)
- `charset` / `encoding` – e.g. `UTF-8`, `UTF-16BE`
- `dateFormat`, `timestampFormat` – date/timestamp parsing
- `rescuedDataColumn` – column for unparsed/mismatched data (e.g. `_rescued_data`)
- `schema` – explicit schema (StructType or DDL string) to avoid inference

Example with options:

```python
sdf = (
    spark.read
    .format("json")
    .option("multiline", "true")
    .option("rescuedDataColumn", "_rescued_data")
    .load(f"/Volumes/{catalog}/{db}/{volume_name}/path")
)
```

### Querying semi-structured JSON (SQL)

When a column contains JSON strings, use `column:path` and `::type` to extract and cast. Backticks for names with spaces/special chars; brackets for case-sensitive keys.

```sql
-- Top-level field
SELECT raw:owner FROM store_data;

-- Nested (dot or brackets)
SELECT raw:store.bicycle.price::double FROM store_data;

-- Array element and subfield
SELECT raw:store.fruit[0].type FROM store_data;

-- from_json for complex types
SELECT from_json(raw:store.bicycle, 'price double, color string') AS bicycle FROM store_data;
```

Reference: [Query JSON strings](https://docs.databricks.com/aws/en/semi-structured/json).

### SQL: read JSON files into a table / view

```sql
-- Temporary view from Volume JSON
CREATE OR REPLACE TEMP VIEW my_json_view
USING json
OPTIONS (path "/Volumes/main/default/my_volume/events/");

-- Multi-line
CREATE OR REPLACE TEMP VIEW multi_line_view
USING json
OPTIONS (path "/Volumes/main/default/my_volume/data/", multiline "true");

-- Query
SELECT * FROM my_json_view LIMIT 10;
```

## CSV

### Volume or workspace (PySpark)

```python
path = f"/Volumes/{catalog}/{db}/{volume_name}/data.csv"
sdf = (
    spark.read
    .format("csv")
    .option("header", "true")
    .option("delimiter", ",")
    .load(path)
)

# Workspace
path = f"file:{os.getcwd()}/data/sample.csv"
sdf = spark.read.option("header", "true").format("csv").load(path)
```

### SQL

```sql
CREATE OR REPLACE TEMP VIEW csv_view
USING csv
OPTIONS (path "/Volumes/main/default/my_volume/data/", header "true");

SELECT * FROM csv_view;
```

## Parquet

### Volume or workspace (PySpark)

```python
path = f"/Volumes/{catalog}/{db}/{volume_name}/data.parquet"
sdf = spark.read.parquet(path)
# Or
sdf = spark.read.format("parquet").load(path)
```

### SQL

```sql
CREATE OR REPLACE TEMP VIEW parquet_view
USING parquet
OPTIONS (path "/Volumes/main/default/my_volume/");

SELECT * FROM parquet_view;
```

## Nested / semi-structured JSON (PySpark)

After reading JSON, use `selectExpr` with `:` path and `::type` (same semantics as SQL), or `from_json` / `get_json_object`.

```python
# Assume df has column 'raw' with JSON string
from pyspark.sql.functions import from_json, get_json_object, col

# Dot path and cast
df = df.selectExpr(
    "raw:store.bicycle.price::double AS price",
    "raw:store.bicycle.color AS color",
    "raw:store.fruit[0].type AS first_fruit"
)

# Or from_json for a struct
from pyspark.sql.types import StructType, StructField, DoubleType, StringType
bicycle_schema = StructType([
    StructField("price", DoubleType()),
    StructField("color", StringType())
])
df = df.withColumn("bicycle", from_json(col("raw").getField("store").getField("bicycle"), bicycle_schema))
```

For nested JSON in a string column, `get_json_object(col("raw"), "$.store.bicycle")` returns a string; then use `from_json(..., schema)` to get a struct.

## Scripts

Run or adapt these from the skill folder:

| Script | Purpose |
|--------|---------|
| [scripts/read_json_volume.py](scripts/read_json_volume.py) | JSON from Volume (single-line and multi-line) |
| [scripts/read_json_workspace.py](scripts/read_json_workspace.py) | JSON from workspace (repo and user path) |
| [scripts/read_csv_volume.py](scripts/read_csv_volume.py) | CSV from Volume with common options |
| [scripts/read_parquet_volume.py](scripts/read_parquet_volume.py) | Parquet from Volume |
| [scripts/read_nested_json.py](scripts/read_nested_json.py) | Nested / semi-structured JSON in PySpark |
| [scripts/read_files_sql.sql](scripts/read_files_sql.sql) | SQL examples for JSON, CSV, Parquet (Volumes and workspace) |

## Edge Cases

- **Multi-line JSON**: Always set `.option("multiline", "true")`; otherwise Spark expects one JSON object per line.
- **Workspace + Spark**: Use the `file:` scheme and full path; Spark does not resolve relative paths the same way as Python.
- **Repo notebooks**: `os.getcwd()` is typically the directory containing the notebook (repo root in many setups); use it to build `file:` paths.
- **Large or evolving schemas**: Use `rescuedDataColumn` so unparsed or extra columns are kept in a single column instead of failing.
- **Explicit schema**: Pass `.schema(schema)` or `schema` option in SQL to avoid inference and control types.

## References

- [JSON file (Databricks)](https://docs.databricks.com/aws/en/query/formats/json)
- [Query JSON strings (semi-structured)](https://docs.databricks.com/aws/en/semi-structured/json)
- [Work with files on Databricks](https://docs.databricks.com/aws/en/files/)
- [Programmatically interact with workspace files](https://docs.databricks.com/aws/en/files/workspace-interact)
- [PySpark DataFrameReader.json](https://api-docs.databricks.com/python/pyspark/latest/pyspark.sql/api/pyspark.sql.DataFrameReader.json.html)
- [parse_json (Databricks SQL)](https://docs.databricks.com/gcp/en/sql/language-manual/functions/parse_json)

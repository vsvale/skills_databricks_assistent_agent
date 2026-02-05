# Best Practices

## Code Formatting
- **Line Breaks**: Use parentheses `()` instead of backslash `\` for line breaks.
- **Imports**: Standardize imports. Do NOT use `import *`. Import only what is needed. Group imports.
- **Defensive Imports**: Wrap custom/legacy library imports in try-except blocks to prevent job failures during migration or if libraries are missing in the new environment.
  ```python
  try:
      from cryptography_library.operations import SparkCryptography
      cryptography = SparkCryptography(spark)
  except ImportError:
      print("Cryptography library not available - check Volume installation")
  ```
- **Global Variables**: Do NOT use global variables inside functions. Pass them as arguments.

**Example (Line Breaks)**:
```python
# Bad
df = spark.read.table('tb')\
          .filter(col('a') > 1)

# Good
df = (
  spark.read.table('tb')
       .filter(col('a') > 1)
)
```

## Notebooks & Jobs
- **Personal Workspace**: Do NOT keep production notebooks in Personal Workspace.
- **%run**: Avoid `%run` for orchestration. Use Job Tasks.
- **Shared Code**: Save shared functions as `.py` files and import them.
- **Parameter Passing**: Do NOT use `%run` to pass variables. Use Job Parameters or Task Values.

## Data Operations
- **Drop/Replace**: Avoid `DROP TABLE` or `CREATE OR REPLACE`. Prefer `TRUNCATE` + `INSERT` or `.mode('overwrite')` to preserve metadata/permissions.
- **dbutils.fs.rm**: Do NOT use `dbutils.fs.rm` on table paths (requires External Location permissions). Use SQL commands.
- **Pandas**: Do NOT use pure Pandas (driver-bound). Use PySpark or Pandas API on Spark.
- **Unnecessary Actions**: Remove `.count()`, `display()`, `.show()` from production code.
- **Variables**: Use variables for table names referenced multiple times.
- **.withColumns**: Use `.withColumns` (plural) instead of multiple chained `.withColumn`.
- **Temp Files**: Do NOT save to `dbfs:/FileStore/`. Use driver temp `/temp/` or Volumes (and clean up).

## Catalog & Performance
- **Legacy Catalog**: Do NOT use `legacy_hive_catalog` for processes/jobs.
- **Trigger**: Replace `Trigger.Once` with `Trigger.AvailableNow`.

**Example (AvailableNow)**:
```python
# Bad
stream_writer = stream_writer.trigger(once=True)

# Good
stream_writer = stream_writer.trigger(availableNow=True)
```

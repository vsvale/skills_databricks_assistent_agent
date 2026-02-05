---
name: migration-hive-to-unity
description: Guide for migrating Databricks workflows from Hive Metastore (Legacy) to Unity Catalog. Covers strategy, code patterns (Raw/Bronze/Silver), and best practices.
---

# Migration: Hive to Unity Catalog

## Description
This skill provides comprehensive guidance for migrating data pipelines from Hive Metastore (S3 paths, External Tables) to Unity Catalog (Volumes, Managed Tables). It addresses code modernization, security updates, and performance optimizations required for the transition.

## 1. Migration Strategy
Choose the strategy based on the table status:
- **Copy Only**: For static/unused tables. Perform CTAS only.
- **Repos**: For tables with jobs in Git Repos. Migration team updates the code.
- **Workspace**: For user-managed jobs. User must migrate logic to Repos/Unity.

See [references/strategy.md](references/strategy.md) for detailed scenarios.

## 2. Core Migration Patterns (Before -> After)

### Raw Layer: S3 Paths to Volumes
- **Before**: Constructing S3 paths manually (`s3://bucket/path`).
- **After**: Using Unity Catalog Volumes (`/Volumes/catalog/schema/volume/path`).
- **Action**: Check if a Volume exists for the path. If not, create one (or use generic raw volume).

### Bronze Layer: External to Managed Tables
- **Before**: `spark.read.load("s3://...")` and `write.save("s3://...")`.
- **After**: `spark.read.table("catalog.schema.table")` and `.saveAsTable("catalog.schema.table")`.
- **Key Change**: Use **Managed Tables** by default. Avoid `VACUUM`/`OPTIMIZE` commands in code (enable Predictive Optimization).

### Silver Layer: Path References to Table References
- **Before**: Reading Bronze from S3 path.
- **After**: Reading Bronze from Unity Catalog Table (`spark.read.table()`).

### Checkpoints
- **Before**: S3 bucket for checkpoints.
- **After**: Managed Volume `checkpoints` in the corresponding schema.
- **Path**: `/Volumes/<catalog>/<layer>/checkpoints/<original_path_structure>`.

See [references/code_migration.md](references/code_migration.md) for detailed code snippets.

## 3. Critical Code Updates
- **Metadata**: Replace `input_file_name()` with `col("_metadata.file_path")`.
- **Streaming**: Replace `Trigger.Once` with `Trigger.AvailableNow`.
- **Explicit Writers**: Replace custom wrappers (`create_stream_writer`) with native `.writeStream` syntax.
- **File Deletion**: Replace `dbutils.fs.rm` on tables with `TRUNCATE` or SQL operations.

## 4. Best Practices
- **Code Style**: Use `()` for line breaks, standard imports, no global variables.
- **Performance**: Use `.withColumns` instead of chained `.withColumn`. Remove `.count()`/`display()`.
- **Temp Files**: Use `/temp/` (driver) or Volumes for temp data, never `dbfs:/FileStore`.

See [references/best_practices.md](references/best_practices.md) for the full list.

## 5. Anti-Patterns
- **Forbidden**: Using `legacy_hive_catalog` in production jobs.
- **Forbidden**: Hardcoded S3 paths in Unity-enabled clusters (unless using External Locations explicitly).
- **Forbidden**: `%run` for orchestration (use Job Tasks).
- **Forbidden**: Storing production code in Personal Workspace.

## 6. Examples
See [scripts/](scripts/) for full example files.
- `scripts/before_00_operations.py` vs `scripts/after_00_operations.py`


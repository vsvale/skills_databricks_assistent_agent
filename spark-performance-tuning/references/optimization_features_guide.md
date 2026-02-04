# Databricks Optimization Features Guide

This guide details key Databricks optimization features, their default status, and compatibility with Unity Catalog (UC).

## Feature Summary Matrix

| Feature | Default Status (DBR 13.3+) | Unity Catalog Compatible | Recommendation |
| :--- | :--- | :--- | :--- |
| **Disk Cache** | Enabled (SSD nodes) | Yes | Use SSD instances (L/i3 series) for repeated reads. |
| **Dynamic File Pruning (DFP)** | Enabled | Yes | Rely on default; ensure predicates match partition/Z-order cols. |
| **Low Shuffle Merge** | Enabled (Photon) | Yes | Essential for performant `MERGE` operations. |
| **Cost-Based Optimizer (CBO)** | Requires Stats | Yes | Run `ANALYZE TABLE` regularly on managed/external tables. |
| **Bloom Filter Indexes** | Disabled | Yes | Create for specific high-cardinality lookup columns. |
| **Auto Optimize** | Disabled (Classic) / Enabled (Serverless) | Yes | Enable `optimizeWrite` for streaming/frequent batch inserts. |
| **Isolation Levels** | WriteSerializable | Yes | Stick to default unless strict serializability is required. |

---

## 1. Disk Cache (formerly Delta Cache)
*Formerly known as "Delta Cache".*

- **Function**: Caches remote data copies on local instance SSDs (NVMe) to accelerate data reading.
- **Status**: Enabled by default on instance types with local SSDs (e.g., `i3`, `l4`, `m5d` series).
- **Configuration**:
  - Check status: `spark.conf.get("spark.databricks.io.cache.enabled")`
  - **Do not** disable this on SSD nodes.
- **Warning**: Unlike Spark Cache (`.cache()`), this does not use RAM and does not cause OOM errors.

## 2. Dynamic File Pruning (DFP)
- **Function**: Skips reading files that do not contain relevant data for the query, even for non-partitioned columns (if Z-Ordered).
- **Status**: Enabled by default.
- **Best Practice**: ensure queries use filters on columns that are Z-Ordered or Clustered.

## 3. Low Shuffle Merge
- **Function**: Optimizes `MERGE INTO` operations by preserving existing data organization (clustering/Z-order) and reducing shuffle.
- **Status**: Enabled by default in Photon and Databricks Runtime 10.4+.
- **Configuration**: `spark.databricks.delta.merge.enableLowShuffle = true` (Default).

## 4. Cost-Based Optimizer (CBO)
- **Function**: Uses table statistics (row count, column cardinality, min/max) to choose the most efficient query plan (e.g., Join type order).
- **Status**: The optimizer is active, but **requires statistics** to function effectively.
- **Action**:
  - Run `ANALYZE TABLE table_name COMPUTE STATISTICS` after major data changes.
  - For specific columns (used in joins/filters): `ANALYZE TABLE table_name COMPUTE STATISTICS FOR COLUMNS col1, col2`.
- **Unity Catalog**: Critical for UC performance as it informs the optimizer across the catalog.

## 5. Bloom Filter Indexes
- **Function**: Probabilistic data structure to skip files for point-lookup queries (e.g., "Get user where ID = 12345").
- **Status**: Manual creation required.
- **Usage**:
  ```sql
  CREATE BLOOMFILTER INDEX ON TABLE table_name FOR COLUMNS(col_name OPTIONS (fpp=0.1, numItems=1000000));
  ```
- **When to use**: High cardinality columns that are frequently queried with `=` or `IN`.

## 6. Auto Optimize (Optimize Write & Auto Compact)
- **Function**: Automatically optimizes file sizes during write operations.
- **Status**: 
  - **Serverless**: Enabled by default.
  - **Classic Compute**: Disabled by default.
- **Usage**:
  - **Optimize Write**: Coalesces small files *during* write. 
    - Enable: `ALTER TABLE t SET TBLPROPERTIES (delta.autoOptimize.optimizeWrite = true)`
  - **Auto Compact**: Compacts small files *after* write.
    - Enable: `ALTER TABLE t SET TBLPROPERTIES (delta.autoOptimize.autoCompact = true)`
- **Trade-off**: Increases write latency slightly to improve read performance and reduce small file problems.

## 7. Isolation Levels
- **Default**: `WriteSerializable`.
- **Option**: `Serializable`.
- **Impact**: Controls concurrency conflict resolution. `WriteSerializable` allows more concurrency but can lead to specific anomalies (rare in ETL). `Serializable` is stricter.
- **Recommendation**: Keep default `WriteSerializable` for most ETL/ELT pipelines.

## Reference Links
- [Databricks Optimizations](https://docs.databricks.com/aws/en/optimizations/)
- [Disk Cache](https://docs.databricks.com/aws/en/optimizations/disk-cache)
- [Dynamic File Pruning](https://docs.databricks.com/aws/en/optimizations/dynamic-file-pruning)
- [Isolation Levels](https://docs.databricks.com/aws/en/optimizations/isolation-level)

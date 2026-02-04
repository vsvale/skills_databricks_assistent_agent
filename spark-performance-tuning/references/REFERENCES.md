# Spark Performance Tuning References

This document provides a comprehensive technical reference for optimizing Spark applications on Databricks, consolidating best practices from Databricks Engineering and the Delta Lake community.

## Technical Guides
For deep-dives into specific optimization areas, refer to the following guides:

- **[Data Layout Optimization](data_layout.md)**: Liquid Clustering, Z-Ordering, and effective partitioning.
- **[Join Strategy Selection](join_optimization.md)**: How to choose between Broadcast, Shuffle Hash, and Sort-Merge joins.
- **[Adaptive Query Execution (AQE)](adaptive_query_execution.md)**: Runtime optimizations for skew and partition coalescing.
- **[Caching & Memory Management](caching_and_persistence.md)**: Disk Cache vs. Spark Cache and memory spill handling.
- **[Optimization Features Guide](optimization_features_guide.md)**: Default status and UC compatibility for key features (DFP, CBO, etc.).
- **[Row Tracking Reference](row_tracking.md)**: Enablement and storage trade-offs for row-level lineage.
- **[Deletion Vectors Reference](deletion_vectors.md)**: Optimizing DML performance by avoiding file rewrites.

## Core Best Practices

### 1. Avoid User-Defined Functions (UDFs)
UDFs (especially non-vectorized Python UDFs) are a common performance bottleneck because they require data serialization between the JVM and Python process and prevent Spark's Catalyst optimizer from optimizing the internal logic.
- **Leverage Deletion Vectors**: Enable `delta.enableDeletionVectors` on tables with frequent updates/deletes to avoid the expensive Cop-on-Write (rewriting entire files) and use Merge-on-Read instead.
- **Avoid UDFs**: Favor Spark built-in functions; use vectorized UDFs (Pandas UDFs) if custom logic is unavoidable.

### 2. Broadcast Thresholds
The default `spark.sql.autoBroadcastJoinThreshold` is 10MB.
- **Tip**: You can safely increase this to 100MB or more if your executors have sufficient memory, reducing shuffles for medium-sized tables.

### 3. Data Skipping & Pruning
- **Partition Pruning**: Ensure join keys or filter columns are used for partitioning.
- **Column Pruning**: Always `select()` only the columns you need to reduce I/O and memory throughput.

### 4. Optimize Writes
Enable auto-optimization for all Delta writes to maintain healthy file sizes.
```python
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.databricks.delta.autoOptimize.autoCompact.enabled", "true")
```

## Advanced Log & Checkpoint Tuning
For extremely large or frequently updated tables, transaction log management becomes a bottleneck.

-   **Multi-part Checkpointing**: Speeds up state reconstruction for tables with massive numbers of files.
    -   `spark.databricks.delta.checkpoint.partSize=<n>`
-   **Log Compactions**: Reduces latency spikes caused by reading long chains of JSON commit files.
    -   `spark.databricks.delta.deltaLog.minorCompaction.useForReads=true` (Default)

## External Resources
- [Databricks Performance Optimization Documentation](https://docs.databricks.com/optimizations/index.html)
- [Control Data File Size (Databricks)](https://docs.databricks.com/aws/en/delta/tune-file-size)
- [Table Properties Reference (Databricks)](https://docs.databricks.com/aws/en/delta/table-properties)
- [SQL TBLPROPERTIES Syntax (Databricks)](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-tblproperties)
- [Delta Lake Best Practices](https://docs.delta.io/latest/best-practices.html)
- [Delta Lake Row Tracking Documentation](https://docs.delta.io/latest/delta-row-tracking.html)
- [Apache Spark Performance Tuning Guide](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
- [Cost and Performance Monitoring with Databricks SQL](https://docs.databricks.com/sql/admin/monitoring.html)

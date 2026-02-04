---
name: spark-performance-tuning
description: Optimize Spark application performance in Databricks through data layout, join strategies, memory management, and AQE.
---

# Spark Performance Tuning

Optimize your Databricks Spark workloads for maximum efficiency and minimum cost. This skill provides guidance and technical references for optimizing data layout, join strategies, memory management, and Adaptive Query Execution (AQE).

## When to Use This Skill

-   **Slow Jobs**: When your Spark jobs are taking longer than expected or failing to meet SLAs.
-   **I/O Bound**: When CPU usage is low but jobs are slow (symptom of small files or storage latency).
-   **High Cost**: When cluster usage is disproportionately high compared to the data volume.
-   **OOMs**: When jobs fail with `OutOfMemoryError` or heavy shuffle spill.
-   **Tuning**: When migrating from legacy systems or optimizing modern Delta Lake tables (Liquid Clustering).

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Data Skipping** | Leveraging file-level statistics (min/max) to avoid reading irrelevant data. |
| **Shuffle** | Data movement across the network; often the biggest performance bottleneck. |
| **Spill** | When Spark runs out of memory and writes intermediate data to disk. |
| **AQE** | Adaptive Query Execution; runtime optimization of query plans. |
| **Liquid Clustering** | Modern, flexible data layout that replaces partitioning and Z-Ordering. |
| **Row Tracking** | Mandatory best practice for row-level lineage and incremental pipelines. |
| **Deletion Vectors** | Storage optimization that avoids full file rewrites during updates/deletes. |

## High-Level Workflow

1.  **Analyze**: Use the Spark UI and Databricks SQL Warehouse monitoring to identify bottlenecks (skew, spill, shuffle).
2.  **Optimize Layout**: Ensure data is properly partitioned, Z-Ordered, or using Liquid Clustering.
3.  **Optimize Joins**: Select the best join strategy (Broadcast, Shuffle Hash, Sort Merge).
4.  **Leverage AQE**: Ensure Adaptive Query Execution (AQE) is enabled and tuned.
5.  **Enable Row Tracking & Deletion Vectors**: Mandatory best practices for DML performance and incremental processing.
6.  **Configure Cluster**: Choose appropriate instance types and cluster sizing.

## Key Performance Areas

### 1. Data Layout & Skipping
Proper data organization can drastically reduce the amount of data read from storage.
-   **Liquid Clustering**: Preferred for modern Delta tables.
-   **Partitioning**: Best for static, high-cardinality columns used in filters.
-   **Z-Ordering**: Optimizes multiple dimensions within files.
See [Data Layout Reference](references/data_layout.md) for details.

### 2. I/O Performance & Small Files
I/O is often the main bottleneck (100-1000x slower than memory).
-   **Small Files**: Files < 64MB cause massive metadata overhead.
-   **Solution**: Run `OPTIMIZE` to compact files to 128MB-1GB.
-   **Disk Cache**: Use instance types with local SSDs for faster repeated reads.
See [I/O Tuning Reference](references/io_performance_tuning.md) for deep dive.

### 3. Join Optimization
Joins are often the most expensive operation in a Spark job.
-   **Broadcast Hash Join**: Ideal for joining a small table with a large one.
-   **Shuffle Hash Join**: For tables larger than broadcast thresholds but with good distribution.
-   **Sort-Merge Join**: The robust default for large-scale joins.
See [Join Optimization Reference](references/join_optimization.md) for strategy selection.

### 4. Adaptive Query Execution (AQE) & Skew
AQE optimizes query plans at runtime based on actual data statistics.
-   **Skew Join Optimization**: Automatically handles data skew.
-   **Manual Salting**: Use if AQE fails to resolve massive skew.
See [Spill & Skew Handling](references/spill_and_skew_handling.md) for advanced strategies.

### 5. Memory & Spill
Manage cluster resources effectively to avoid OOMs and spill.
-   **Spill**: Monitor "Shuffle Spill" in Spark UI. Means partition size > memory.
-   **Fix**: Increase `spark.sql.shuffle.partitions` or executor memory.
-   **Caching**: Prefer Disk Cache (local SSD) over Spark Cache (Memory) to save heap.
See [Caching & Persistence Reference](references/caching_and_persistence.md) for best practices.

## More Resources
For a comprehensive guide and external documentation links, see the **[Spark Performance Tuning Master Reference](references/REFERENCES.md)**.

## Recommended Spark Configurations

**Warning**: Avoid over-configuring. Most defaults are optimized.
**Serverless**: Most configs are ignored. See [Configuration Best Practices](references/configuration_best_practices.md).

Check default status of key features (Disk Cache, DFP, etc.) and Unity Catalog compatibility:
[Optimization Features Guide](references/optimization_features_guide.md)

Apply these defaults for write-heavy or modern Delta workloads (Classic Compute only):
[configure_performance_defaults.py](scripts/configure_performance_defaults.py)

## Common Optimization Snippets

Enable Disk Cache (Delta Cache):
[configure_caching.py](scripts/configure_caching.py)

Handle Skew with Manual Salting:
[handle_skew_salting.py](scripts/handle_skew_salting.py)

Run OPTIMIZE and Z-Order to fix small files:
[run_optimize_command.py](scripts/run_optimize_command.py)

Calculate optimal partition size (target 128MB):
[calculate_partition_size.py](scripts/calculate_partition_size.py)

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| **Straggler Tasks** | Data Skew (one partition is much larger). | Enable AQE Skew Join or use salting. |
| **Shuffle Spill** | Insufficient memory for shuffles. | Increase executor memory, reduce partitions, or optimize joins. |
| **Broadcast Timeout** | Broadcast side is too large or network is slow. | Increase `spark.sql.broadcastTimeout` or disable broadcast. |
| **OOM (Heap)** | Large objects in memory (e.g., UDFs, large broadcast). | Avoid UDFs, check broadcast sizes, or use larger instance types. |
| **Metadata BottleNeck** | Too many small files or massive transaction log. | Run `OPTIMIZE`, enable auto-compaction, or use multi-part checkpoints. |

For more detailed technical references and external documentation, see [references/REFERENCES.md](references/REFERENCES.md).

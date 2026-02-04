# Adaptive Query Execution (AQE)

AQE is a critical query optimization framework and is **enabled by default** in Databricks. It is highly recommended to keep it enabled as it re-optimizes query plans based on runtime statistics.

## 1. Coalescing Post-Shuffle Partitions
Automatically reduces the number of partitions after a shuffle to avoid the overhead of many small tasks.

-   **Config**: `spark.sql.adaptive.coalescePartitions.enabled` (Default: `true`)
-   **Min Partitions**: `spark.sql.adaptive.coalescePartitions.minPartitionNum` (Default: `1`)
-   **Advisory Partition Size**: `spark.sql.adaptive.advisoryPartitionSizeInBytes` (Default: `64MB`)

## 2. Skew Join Optimization
Dynamically handles data skew by splitting skewed partitions into smaller sub-partitions.

-   **Config**: `spark.sql.adaptive.skewJoin.enabled` (Default: `true`)
-   **Threshold**: `spark.sql.adaptive.skewJoin.skewedPartitionFactor` (Default: `5`x the median size)

## 3. Dynamic Join Selection
Switches join strategies at runtime (e.g., from Sort-Merge to Broadcast Hash Join) if the actual size of a shuffle dependency is smaller than the broadcast threshold.

-   **Note**: This is highly effective when filter pushdowns significantly reduce the data size.

## 4. Troubleshooting AQE
Check the **Spark UI -> SQL tab**. Click on a query execution and look for "AdaptiveSparkPlan". You can see which logical nodes were replaced with optimized versions.

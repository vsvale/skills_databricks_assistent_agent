# Spill and Skew Handling

Spill and Skew are two of the most common performance killers in Spark.

-   **Data Skew**: When data is unevenly distributed across partitions, causing some tasks to take much longer than others (stragglers).
-   **Spill**: When the memory required for a task exceeds the available executor memory, Spark writes intermediate data to disk.

## 1. Handling Data Skew

Symptoms:
-   A few tasks take significantly longer than the rest (stragglers).
-   Spark UI shows uneven data distribution in the "Summary Metrics" of a stage (Max >> 75th percentile).
-   OOM errors on specific tasks.

### Solution A: Adaptive Query Execution (AQE)
AQE is the first line of defense. It automatically detects skew and splits skewed partitions into smaller sub-partitions.

-   **Ensure Enabled**: `spark.sql.adaptive.skewJoin.enabled = true` (Default in Databricks).
-   **Tune Threshold**: Adjust `spark.sql.adaptive.skewJoin.skewedPartitionFactor` (Default 5) if skew is less severe but still impactful.

### Solution B: Salting (Manual Intervention)
If AQE cannot resolve the skew (e.g., in `GROUP BY` operations or extremely skewed joins), use "Salting".

**Mechanism**:
1.  Add a random "salt" column (e.g., random integer 0-N) to the skewed key in the large table.
2.  Explode the key in the small table (if joining) to match all possible salt values.
3.  Join on `(key, salt)`.
4.  Aggregate results and remove the salt.

See [Salted Join Example](../scripts/handle_skew_salting.py).

### Solution C: Broadcast Join
If the skewed table is joined with a small table, force a Broadcast Hash Join. This avoids the shuffle entirely, neutralizing the skew impact.

```python
from pyspark.sql.functions import broadcast
df_large.join(broadcast(df_small), "key")
```

## 2. Handling Shuffle Spill

Symptoms:
-   **Spark UI**: "Spill (Memory)" and "Spill (Disk)" columns show non-zero values.
-   **Slow Stages**: Stages involving `SortMergeJoin` or `GroupAggregate` are slow.
-   **Disk I/O**: High disk write/read usage on executors.

### Cause
The partition size > Executor Memory / Cores.

### Solutions

1.  **Increase Partitions**: Reduce the size of each partition by increasing the number of shuffle partitions.
    -   `spark.sql.shuffle.partitions`: Set to 2x-4x total cores, or higher (e.g., 200 -> 2000) for large data.
    -   Use the [Partition Size Calculator](../scripts/calculate_partition_size.py) to target ~128MB-200MB per partition.

2.  **Increase Executor Memory**:
    -   Scale up the instance type (e.g., from `Standard_D4s` to `Standard_E4s` for higher memory-to-core ratio).
    -   Decrease `spark.executor.cores` (e.g., from 8 to 4) to give each core more memory share (requires custom cluster config).

3.  **Optimize Join Strategy**:
    -   Switch to Broadcast Join if possible (avoids shuffle).
    -   Avoid `UDFs` in join conditions or aggregations (often less memory efficient).

4.  **AQE Coalescing**:
    -   Ensure `spark.sql.adaptive.coalescePartitions.enabled` is true. This prevents "too many partitions" problems, allowing you to set `spark.sql.shuffle.partitions` high (e.g., 4000) safely.

## Troubleshooting Workflow

1.  **Identify**: Check Spark UI -> Stages -> Sort by Duration. Look for "Spill (Disk)".
2.  **Check Skew**: In the slow stage, check "Summary Metrics". Is Max Duration >> Median? If yes -> Skew.
3.  **Check Memory**: Is Spill > 0? If yes -> Spill.
4.  **Apply Fix**:
    -   Skew -> Check AQE, try Salting.
    -   Spill -> Increase partitions, Increase Memory.

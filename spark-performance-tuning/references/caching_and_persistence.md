# Caching and Persistence

Effective caching reduces I/O by storing data closer to the compute. In Databricks, there are two distinct caching mechanisms: **Spark Cache** and **Disk Cache** (formerly Delta Cache). Understanding the difference is crucial for performance.

## 1. Disk Cache (formerly Delta Cache) - *Preferred*

The Disk Cache (formerly IO Cache or Delta Cache) stores remote files on the local SSDs of worker nodes. It is the default and recommended way to accelerate reads.

### Why it's superior:
-   **No JVM Heap Usage**: It uses local disk, leaving memory free for execution.
-   **Automatic**: No code changes (`.cache()`) required. It automatically caches data as it's read.
-   **Preserves Data Skipping**: Unlike Spark Cache, Disk Cache works with the original files, preserving column stats for efficient skipping.
-   **Consistency**: Automatically detects changes to the underlying files.

### Configuration
Enabled by default on instance types with local SSDs (e.g., AWS `i3`, Azure `Lsv2`, GCP `n2d`).
To force enable on other instances (uses EBS/Managed Disk):
```python
spark.conf.set("spark.databricks.io.cache.enabled", "true")
```

## 2. Spark Cache (`.cache()` / `.persist()`)

Stores the result of a specific DataFrame transformation in memory (JVM Heap) or disk.

### When to use:
-   **Iterative Algorithms**: ML algorithms re-using the same dataset 100s of times.
-   **Complex Transformations**: When a dataframe is the result of expensive joins/aggregations and is used multiple times.
-   **Non-Parquet Sources**: When reading from JDBC, CSV, or JSON where Delta Cache doesn't apply.

### Risks:
-   **OOM**: Consumes execution memory, leading to spills or OOM errors.
-   **Blocks Optimization**: Predicate pushdown (filter) often stops at the cached layer.
-   **Staleness**: Does not automatically update if underlying data changes.

### Storage Levels
-   `MEMORY_AND_DISK` (Default for `.cache()`): Safest. Spills to disk if memory fills.
-   `MEMORY_ONLY`: Fastest but risky.
-   `MEMORY_ONLY_SER`: Compact but CPU-intensive (serialization).

## 3. Comparison Table

| Feature | Disk Cache (formerly Delta Cache) | Spark Cache (`.cache()`) |
| :--- | :--- | :--- |
| **Storage Location** | Local NVMe SSDs | RAM (JVM Heap) + Disk |
| **Data Format** | Original compressed format (Parquet) | Decompressed Row/Columnar objects |
| **Memory Impact** | None (uses disk) | High (reduces execution memory) |
| **Usage** | Automatic (transparent) | Manual (`df.cache()`) |
| **Best For** | Repeated reads of Delta tables | Iterative calc, intermediate results |

## 4. Best Practices
1.  **Do NOT cache raw tables**: `spark.read.load(path).cache()` is an anti-pattern. Let Disk Cache handle it.
2.  **Unpersist**: Always call `df.unpersist()` when the dataframe is no longer needed to free up memory.
3.  **Monitor**:
    -   **Spark Cache**: "Storage" tab in Spark UI.
    -   **Disk Cache**: Spark UI -> Executors -> "Disk Used" or standard metrics.

# Data Layout Optimization

Optimizing how data is stored on disk is one of the most effective ways to improve Spark performance by enabling **data skipping**.

## 1. Liquid Clustering (Recommended)
Liquid Clustering is the modern successor to Partitioning and Z-Ordering. It simplifies data layout by automatically handling skew and enabling clustering on multiple columns.

-   **When to use**: Modern Delta tables, datasets with high skew, or queries that filter on multiple columns.
-   **Syntax**:
    ```sql
    -- Create table with Liquid Clustering
    CREATE TABLE my_table (id INT, date DATE, region STRING)
    CLUSTER BY (date, region);

    -- Change clustering columns
    ALTER TABLE my_table CLUSTER BY (region, category);
    ```

### Data Skipping Statistics
Delta Lake automatically collects min/max statistics. For tables with many columns, you can optimize statistics collection to speed up writes and mejorar data skipping performance.
-   **Leading Columns**: `delta.dataSkippingNumIndexedCols` (Default: 32). Collects stats for the first N columns.
-   **Specific Columns (Recommended)**: `delta.dataSkippingStatsColumns`. A comma-separated list of columns to collect statistics for. This property takes precedence over `dataSkippingNumIndexedCols`.
    ```sql
    ALTER TABLE my_table SET TBLPROPERTIES (
      'delta.dataSkippingStatsColumns' = 'user_id, region, event_date'
    );
    ```

## 2. Z-Ordering
Z-Ordering organizes data to improve data skipping across multiple dimensions.

-   **When to use**: On columns frequently used in WHERE clauses, especially when cardinality is high.
-   **Note**: Liquid Clustering is generally preferred over Z-Ordering for new tables.
-   **Syntax**:
    ```sql
    OPTIMIZE my_table ZORDER BY (user_id, session_id);
    ```

## 3. Partitioning
Partitioning divides data into physical directories based on column values.

-   **When to use**: Low-cardinality columns (e.g., `date`, `country`) used in almost every query.
-   **Rule of Thumb**: Only partition if you expect at least **1 GB of data per partition**.
-   **Anti-pattern**: Partitioning on high-cardinality columns (e.g., `user_id`), which leads to the "Small File Problem".
-   **Syntax**:
    ```sql
    CREATE TABLE my_table (...) PARTITIONED BY (year, month);
    ```

## 4. Bucketing
Bucketing distributes data into a fixed number of "buckets" based on the hash of a column.

-   **When to use**: On high-cardinality columns used frequently in joins or aggregations to avoid shuffles (Sort-Merge Join optimization).
-   **Note**: Modern Databricks features like Liquid Clustering often reduce the need for manual bucketing.
-   **Syntax**:
    ```sql
    CREATE TABLE my_table (...) CLUSTERED BY (user_id) INTO 256 BUCKETS;
    ```

## 5. File Size Optimization
Large numbers of small files hurt performance due to metadata overhead. Databricks automatically autotunes file sizes based on table size.

### Autotuning Scale
Databricks dynamically adjusts the target file size for `OPTIMIZE` and writes:
-   **< 2.56 TB**: 256 MB
-   **2.56 TB - 10 TB**: Linear growth from 256 MB to 1 GB.
-   **> 10 TB**: 1 GB

### Manual & Workload-Aware Tuning
-   **Workload Tuning**: `delta.tuneFileSizesForRewrites`. Set to `true` for tables targeted by many `MERGE` or DML operations. This sets a lower target file size for faster rewrites.
    ```sql
    ALTER TABLE my_table SET TBLPROPERTIES ('delta.tuneFileSizesForRewrites' = true);
    ```
-   **Target Size**: `delta.targetFileSize`. Manually set a fixed target size if autotuning is insufficient (e.g., `'512MB'`).
-   **Auto-Optimize**: Enable `optimizeWrite` and `autoCompact` (as shown in `SKILL.md`).
    -   *Note*: Optimized Write eliminates the need for manual `coalesce(n)` or `repartition(n)` before writing.
-   **Advanced Compaction Tuning**:
    -   `spark.databricks.delta.autoCompact.maxFileSize`: Target file size for compaction.
    -   `spark.databricks.delta.autoCompact.minNumFiles`: Minimum files to trigger compaction.
-   **Advanced Write Tuning**:
    -   `spark.databricks.delta.optimizeWrite.binSize`: Controls the target in-memory size of each output file (default 512MiB).
    -   `spark.databricks.delta.optimizeWrite.numShuffleBlocks`: Maximum number of shuffle blocks to target (default 50,000,000).
    -   `spark.databricks.delta.optimizeWrite.maxShufflePartitions`: Max output buckets for the shuffle (default 2,000).
-   **Optimize Command**: Manually compact files. Use `.option("dataChange", "false")` in Spark writes to indicate layout rearrangement only, minimizing impact on concurrent reads.
    ```sql
    OPTIMIZE my_table;
    ```

## 6. Overwriting & Data Management
Atomically replacing data is safer and more efficient than manual deletion.

-   **REPLACE TABLE**: Use `CREATE OR REPLACE TABLE` (SQL) or `mode("overwrite")` with `overwriteSchema` (Python) to replace content/schema atomically.
-   **Append Only**: `delta.appendOnly`. Set to `true` for high-throughput write-only tables (e.g., logs) to simplify metadata management. This disables `UPDATE` and `DELETE`.
-   **VACUUM**: Regularly run `VACUUM` to remove files no longer referenced by the transaction log to save storage costs.
    ```sql
    VACUUM my_table RETAIN 168 HOURS; -- Default 7 days
    ```

## 7. Row Tracking
Row tracking allows Delta Lake to track row-level lineage. It is recommended for incremental processing and auditing.

See the **[Dedicated Row Tracking Reference](row_tracking.md)** for detailed guidance on enablement, storage, and optimization.

## 8. Deletion Vectors
Deletion Vectors optimize DML performance by avoiding full file rewrites during `DELETE`, `UPDATE`, and `MERGE` operations.

See the **[Dedicated Deletion Vectors Reference](deletion_vectors.md)** for performance benefits and management guidance.

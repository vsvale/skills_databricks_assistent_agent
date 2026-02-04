# Join Optimization

Joins are often the primary cause of shuffles, which move data across the network and degrade performance.

## 1. Broadcast Hash Join (BHJ)
The most efficient join. One side is broadcasted to all executors, avoiding a shuffle of the large table.

-   **Best for**: Joining a small table (usually < 10MB default) with a large one.
-   **Usage**: Spark usually detects this automatically, but you can hint it.
    ```python
    from pyspark.sql.functions import broadcast
    joined_df = large_df.join(broadcast(small_df), "key")
    ```

## 2. Shuffle Hash Join
Both sides are partitioned by the join key.

-   **Best for**: Tables too large to broadcast but where data is relatively evenly distributed.
-   **Enable**: `spark.conf.set("spark.sql.join.preferShuffleHashJoin", "true")`

## 3. Sort-Merge Join (SMJ)
The default join for large datasets. Data is shuffled and sorted on both sides.

-   **Best for**: Very large tables that don't fit in memory.
-   **Optimization**: Ensure the join keys are used for partitioning or clustering to reduce shuffle overhead.

## 4. Handling Data Skew
Skew occurs when one partition has significantly more data than others, causing "straggler" tasks.

-   **AQE Skew Join**: Automatically handled if `spark.sql.adaptive.skewJoin.enabled` is `true`.
-   **Salting**: Manually add a random "salt" to join keys to distribute skewed data.
    ```python
    # Example of salting (conceptual)
    df_skewed = df_skewed.withColumn("salt", (rand() * 10).cast("int"))
    df_small = df_small.withColumn("salt", explode(array([lit(i) for i in range(10)])))
    joined = df_skewed.join(df_small, ["key", "salt"])
    ```

## 5. Broadcast Threshold
Check and adjust the threshold for automatic broadcasting.
-   `spark.sql.autoBroadcastJoinThreshold`: Set to `-1` to disable, or increase (e.g., to `100MB`) if your executors have enough memory.

# Performance Efficiency for the Lakehouse

## Core Principles

1.  **Serverless First**: Use Serverless compute (SQL Warehouses, Jobs) to eliminate cold starts and rightsizing overhead.
2.  **Optimized Engine**: Enable **Photon** for high-performance vectorized query execution.
3.  **Intelligent Management**: Use **Predictive Optimization** to automatically manage file sizing and clustering.
4.  **Right-Sizing**: Match compute instance types (Memory vs. Compute optimized) to the workload.

## Best Practices

### 1. Compute Optimization
*   **Serverless SQL Warehouses**: Use for all BI and interactive SQL. They start instantly and auto-scale efficiently.
*   **Photon**: Enable Photon on DLT pipelines and interactive clusters for faster aggregations and joins.
*   **Job Clusters**: Always use "Job" clusters (automated) rather than "All Purpose" clusters for production pipelines to save cost.

### 2. Storage & File Management
*   **Predictive Optimization**: Enable `alter table <table_name> enable predictive optimization` to let AI handle `OPTIMIZE` and `VACUUM` commands.
*   **Liquid Clustering**: Use `CLUSTER BY` instead of partitioning for columns with high cardinality or changing query patterns.
    ```sql
    CREATE TABLE gold.sales CLUSTER BY (region, date) ...
    ```
*   **File Sizing**: Use `delta.autoOptimize.optimizeWrite = true` to prevent "small file problem" during ingestion.

### 3. Query Performance
*   **Data Skipping**: Ensure queries filter on clustered columns to leverage Min/Max stats.
*   **Caching**: Use Disk Caching (enabled by default on many worker types) to speed up repeated scans of the same data.
*   **Approximate Aggregations**: Use **HyperLogLog (HLL)** sketches in Gold for distinct counts on massive datasets where a small margin of error (e.g., dashboarding) is acceptable for much lower latency.
*   **Constraint Checking**: Use `ALTER TABLE ... ADD CONSTRAINT` to give the optimizer hints about distinct values or primary keys.

### 4. Workload Management
*   **Auto-Scaling**: Configure cluster auto-scaling with a sensible min/max range to handle bursty workloads without over-provisioning.
*   **Query Profile**: Use the Query Profile tool in the UI to identify bottlenecks (e.g., shuffle heavy stages, spill to disk).

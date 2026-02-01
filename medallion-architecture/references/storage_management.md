# Storage and Compute Management in Medallion

The Medallion architecture provides logic and quality, but at the cost of increased storage footprint and compute complexity. Effective management is critical for cost governance.

## Managing the "Storage Debt"

Since Medallion persists data at multiple stages, it can triple storage costs. Mitigate this with:

### 1. Delta Vacuum
Regularly remove old file versions that are no longer needed for time travel.
```sql
-- Remove files older than 7 days
VACUUM gold.sales_summary RETAIN 168 HOURS;
```

### 2. File Compaction and binSize
Prevent the "small file problem" (too many 10KB files) which slows down queries.
- **Auto-Optimize**: Enable `delta.autoOptimize.optimizeWrite`.
- **Target File Size**: For large Gold tables, aim for larger files (e.g., 128MB to 1GB) to minimize metadata overhead.
```sql
ALTER TABLE gold.wide_analytics SET TBLPROPERTIES ('delta.targetFileSize' = '1073741824');
```

### 3. Lifecycle Policies
- **Bronze**: Use cloud provider lifecycle policies (e.g., S3 Glacier) to move very old raw files to cheaper storage tiers.
- **Gold**: Materialized views can be dropped and recreated if source Silver data is retained.

## Latency Optimization

Medallion pipelines incur "hop latency." To minimize this:

| Strategy | Implementation | Benefit |
| :--- | :--- | :--- |
| **Avoid Upserts** | Use append-only streams in Silver where possible. | Avoids expensive file rewrites. |
| **DLT Streaming** | Use `STREAMING TABLE` in Delta Live Tables. | Automated micro-batching and low-latency state management. |
| **Predictive Optimization** | Enable in Unity Catalog. | Databricks automatically runs OPTIMIZE and VACUUM based on usage. |

## Compute Governance

- **Workload Isolation**: Use SQL Warehouses for Gold layer (BI) and Serverless Jobs for Bronze/Silver (ETL).
- **Size Appropriately**: Use `XS` or `S` warehouses for most BI; scale only when concurrency (not query volume) increases.
- **Spot Instances**: Use spot instances for non-critical Bronze/Silver batch jobs.

For cost-specific policies, see [cost_optimization.md](cost_optimization.md).

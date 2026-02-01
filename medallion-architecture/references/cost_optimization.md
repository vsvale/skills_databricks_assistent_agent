# Cost Optimization for the Lakehouse

## Core Principles

1.  **Right Resourcing**: Match compute types (Jobs vs. All-Purpose) and hardware (CPU vs. GPU) to the workload profile.
2.  **Dynamic Allocation**: Enable auto-scaling and auto-termination. Use **Trigger.AvailableNow** for incremental batch to avoid 24/7 costs.
3.  **Capacity Excess**: Use Spot instances for fault-tolerant workers and **Fleet instance types** for optimal price/availability.
4.  **Governance & Attribution**: Use Budget Policies and tags to attribute costs via `system.billing.usage`.

## Best Practices

### 1. Compute Optimization
*   **Job Compute**: Always use standard **Job clusters** for production ETL. Avoid All-Purpose clusters which are priced higher for interactive use.
*   **Serverless SQL**: Prioritize Serverless SQL Warehouses for BI to eliminate "idle time" billing.
*   **Instance Selection**: 
    *   Use **Compute Optimized** for simple ingestion (Bronze).
    *   Use **Memory Optimized** for complex joins/shuffles (Silver/Gold).
    *   Use **Fleet** types to let Databricks select the cheapest available VMs.
*   **Runtimes**: Use the latest **LTS runtimes** to benefit from the latest Spark and Photon performance optimizations (saving DBU/hour).

### 2. Workload Design
*   **Incremental Batch**: For non-real-time streaming, use `.trigger(availableNow=True)` to process all new data in a single batch and then shut down the cluster.
*   **Spot Instances**: Ingest stateless data (Bronze) using Spot instances. Always use On-Demand for the Spark Driver to prevent job failure if workers are evicted.
*   **Photon Engine**: Use Photon for aggregation-heavy queries; although it has a higher DBU rate, the reduced execution time often results in a lower total cost.

### 3. Monitoring & Governance
*   **Account Console Dashboards**: Import the AI/BI **Cost Management Dashboard** to visualize account-level spending.
*   **Budget Policies**: Apply policies to users/groups to automatically tag and limit serverless compute usage.
*   **System Tables**: Query `system.billing.usage` for granular analysis:
    ```sql
    SELECT sku_name, usage_unit, SUM(usage_quantity) as total_dbus
    FROM system.billing.usage
    WHERE usage_date >= current_timestamp() - INTERVAL 30 DAYS
    GROUP BY 1, 2;
    ```
*   **Compute Policies**: Enforce mandatory tags (e.g., `Project`, `Environment`) and restrict max worker counts to prevent accidental high-spend events.

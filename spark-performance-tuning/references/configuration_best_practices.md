# Spark Configuration Best Practices

Configuring Spark properties on Databricks requires a balanced approach. While tuning can unlock performance, improper configuration is a common source of technical debt and performance regression during upgrades.

## 1. The "Less is More" Philosophy
Databricks strongly recommends **against** setting global Spark configurations unless absolutely necessary.
-   **Defaults are Optimized**: Databricks Runtime defaults are tuned for the specific version and infrastructure.
-   **Upgrade Risk**: Hardcoded configs (e.g., `spark.sql.shuffle.partitions` fixed at `2000`) can override newer, smarter adaptive behaviors in future runtime versions.
-   **Migration Pain**: Migrating from Open Source Spark? Do not blindly copy your `spark-defaults.conf`. Start fresh and only add configs if a specific bottleneck is identified.

## 2. Scope of Configuration
Where you set a config matters:
1.  **Cluster/Compute Policy**: Applies to all jobs/notebooks on that compute. Use for environment-wide guardrails.
2.  **Job/Task**: Applies to the specific job run. Preferred for workload-specific tuning.
3.  **Session (Notebook)**: Applies only to the current session. Good for testing.

## 3. Serverless Compute Limitations
**Critical**: Serverless compute does **not** support setting most Spark properties. It is a managed environment where the platform handles tuning.

### Supported Serverless Configs (Subset)
Only a handful of configs are respected in Serverless:
-   `spark.sql.shuffle.partitions` (Default: auto)
-   `spark.sql.ansi.enabled`
-   `spark.sql.session.timeZone`
-   `spark.sql.legacy.timeParserPolicy`

**Ignored Configs**:
-   Memory settings (`spark.executor.memory`, etc.) -> Handled by T-shirt sizing.
-   AQE toggles -> Always on.
-   Disk/IO settings -> Managed by the platform.

If your performance strategy relies heavily on custom flags, it may not translate to Serverless or Databricks SQL.

## 4. Modern Alternatives to Spark Configs
Many behaviors previously controlled by Spark configs now have first-class SQL/Python support:

| Legacy Config | Modern Approach |
| :--- | :--- |
| `spark.databricks.delta.properties.defaults.autoOptimize.optimizeWrite` | `ALTER TABLE ... SET TBLPROPERTIES (delta.autoOptimize.optimizeWrite = true)` |
| Schema Evolution Configs | `df.write.option("mergeSchema", "true")` or `COPY INTO ... WITH SCHEMA EVOLUTION` |
| Partitioning Configs | `CLUSTER BY` (Liquid Clustering) |

## 5. Recommendation
1.  **Start with Defaults**: Run the workload without custom configs first.
2.  **Use AQE**: Rely on Adaptive Query Execution rather than manual tuning.
3.  **Table Properties > Spark Conf**: Configure behavior at the table level (e.g., block sizes, optimization) so it persists regardless of the compute used.

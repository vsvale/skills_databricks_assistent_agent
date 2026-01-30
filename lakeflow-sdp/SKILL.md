---
name: lakeflow-sdp
description: Develop and operate Lakeflow Spark Declarative Pipelines (SDP) for batch and streaming ETL on Databricks. Covers pipelines, flows, streaming tables, materialized views, expectations, Auto Loader, and CDC. Use when building or configuring ETL pipelines, defining streaming tables or materialized views in SQL or Python, setting data quality expectations, ingesting from cloud storage or message buses, or when the user mentions Lakeflow SDP, SDP, DLT-style pipelines, or declarative pipelines on Databricks.
---

# Lakeflow Spark Declarative Pipelines (SDP)

Lakeflow Spark Declarative Pipelines (SDP) is a declarative framework for batch and streaming data pipelines in SQL and Python on Databricks. It extends Apache Spark Declarative Pipelines and runs on Databricks Runtime. Pipelines orchestrate flows automatically, support incremental processing, and integrate expectations for data quality.

## When to Use This Skill

Use when the user needs to:
- Create or configure ETL pipelines (streaming tables, materialized views, flows)
- Ingest from cloud storage (S3, ADLS Gen2, GCS) or message buses (Kafka, Kinesis, Pub/Sub, EventHub, Pulsar)
- Define data quality expectations (warn, drop, fail on invalid records)
- Use Auto Loader, CDC, or incremental refresh in a pipeline
- Develop pipeline code in SQL or Python and configure target catalog/schema
- Troubleshoot pipeline updates, expectations, or configuration

## Key Concepts

| Concept | Description |
|--------|-------------|
| **Pipeline** | Unit of development and execution. Contains flows, streaming tables, materialized views, and sinks. Configured with source code files and target catalog/schema. |
| **Flow** | Data processing step: reads a source, applies logic, writes to a target. Types: Append (streaming), materialized view (batch incremental), AUTO CDC (streaming). |
| **Streaming table** | Unity Catalog managed table that is a streaming target. Use for append-only or CDC ingestion. Define with `CREATE STREAMING TABLE` (SQL) or equivalent in Python. Use `STREAM` keyword when reading sources for streaming. |
| **Materialized view** | Batch target refreshed incrementally when possible. Use for aggregations, joins, transformations. Define with `CREATE MATERIALIZED VIEW` (SQL). |
| **Sink** | Streaming target for Delta, Kafka, EventHub, or custom Python. |
| **Expectation** | Data quality constraint on a dataset: name, SQL boolean constraint, and action (`ON VIOLATION` warn / drop / fail). |

Pipeline source code is **declarative**: SDP evaluates all dataset definitions across configured files and builds a dependency graph; execution order is determined by the graph, not file order.

## Requirements

- **Workspace**: Unity Catalog is recommended (default for new pipelines). Legacy Hive metastore is supported with different configuration.
- **Compute**: Serverless is recommended for new pipelines; classic clusters with Enhanced autoscaling are supported.
- **Source code**: Python or SQL files (or both) stored in workspace files; add files to the pipeline configuration.

## Configure a Pipeline

1. **Create pipeline**: In the UI, New → ETL pipeline. Name it and set the default **catalog** and **schema** (target for unqualified table names).
2. **Source code**: Add one or more workspace files (SQL and/or Python) that define streaming tables, materialized views, and expectations. Default folder is the pipeline root.
3. **Product edition**: Choose the SDP edition that supports your features (streaming ingest, CDC, expectations). If you use expectations, select an edition that includes them.
4. **Run-as**: Prefer a service principal for production; ensure it has compute, workspace, and Unity Catalog permissions (e.g. `USE CATALOG`, `USE SCHEMA`, `CREATE TABLE` on target schema).

Pipeline settings and Spark configs can be set via the Configuration field (key-value) or JSON. For full options, see [references/REFERENCES.md](references/REFERENCES.md).

## SQL Syntax (Summary)

**Materialized view:**
```sql
CREATE MATERIALIZED VIEW my_catalog.my_schema.my_mv
AS SELECT * FROM my_catalog.my_schema.source_table;
```

**Streaming table** (use `STREAM` for streaming read from source):
```sql
CREATE STREAMING TABLE my_catalog.my_schema.my_streaming_table
AS SELECT * FROM STREAM my_catalog.my_schema.append_only_source;
```

**Auto Loader** (streaming table from cloud files):
```sql
CREATE STREAMING TABLE my_schema.raw_events
AS SELECT * FROM STREAM read_files(
  's3://bucket/path/',
  format => 'json',
  schema => 'value STRING'
);
```

**Expectations** (constraint + action):
```sql
CREATE STREAMING TABLE my_schema.validated_events
CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW
AS SELECT * FROM STREAM my_schema.raw_events;
```

Actions: `ON VIOLATION WARN` (default, keep record), `ON VIOLATION DROP ROW`, `ON VIOLATION FAIL UPDATE`.

**Private table** (pipeline-internal only):
```sql
CREATE PRIVATE MATERIALIZED VIEW internal_staging AS SELECT ...
```

**Parameters:** Use `SET key = value;` and reference in queries with string interpolation as defined in the pipeline SQL reference.

## Python (Summary)

Use the SDP Python API to define streaming tables, materialized views, and expectations. Syntax differs from ad-hoc PySpark: use decorators and SDP-specific builders. See [Pipeline Python language reference](https://docs.databricks.com/aws/en/ldp/developer/python-ref). Expectations in Python use constraint dictionaries and actions (e.g. `expect_or_fail`, `expect_or_drop`).

## Expectations

- **Name**: Unique per dataset; used for monitoring.
- **Constraint**: SQL boolean expression (no subqueries to other tables, no external calls).
- **Action**: `warn` (record kept, metric), `drop` (record dropped, metric), `fail` (flow fails, no write).

Metrics for warn/drop are available in the pipeline UI (Data quality tab) and in the SDP event log.

## Development and Updates

- **Development mode**: Running from the Lakeflow Pipelines Editor uses development mode (interactive). Scheduled or triggered runs use pipeline-configured mode (development on/off).
- **Dry run**: Validates pipeline code without updating tables. Use to check for analysis errors before a full update.
- **Update**: Pipeline starts compute, analyzes dependencies, runs flows. Tables and views are created or updated. Use Run/Update from the UI, job pipeline task, or REST API.

## Data Ingestion

- **Cloud storage**: Prefer **Auto Loader** with streaming tables for incremental file ingestion. Use `read_files()` in SQL (with `STREAM` for streaming). For formats not supported by Auto Loader, use Spark-readable sources in Python or SQL.
- **Message buses**: Pipelines can read directly from Kafka, Kinesis, Pub/Sub, EventHub, Pulsar. Configure connection and use streaming table definitions.
- **CDC**: Use AUTO CDC flow type for change data capture (SCD Type 1 and Type 2) where supported.

## Edge Cases and Troubleshooting

| Issue | What to do |
|-------|------------|
| "Expectations not supported" | Select an SDP product edition that includes expectations. |
| Table not found / wrong catalog | Set pipeline default catalog and schema; qualify table names in code as `catalog.schema.table`. |
| Streaming read error (e.g. change/delete on source) | Use append-only or static sources for `STREAM`; for changing data, consider Python + error handling or CDC. |
| Update fails on expectation | Check Data quality tab and event log; fix invalid data or relax/fix expectation; re-run. |
| Legacy LIVE schema | New pipelines use catalog/schema directly; LIVE schema is legacy. See [references/REFERENCES.md](references/REFERENCES.md). |

## Best Practices

1. **Serverless + Unity Catalog**: Use serverless compute and Unity Catalog for new pipelines when possible.
2. **Run-as service principal**: Use a service principal for production pipelines to avoid dependency on a single user.
3. **Expectations**: Name clearly; use `drop` or `fail` for critical constraints; monitor metrics.
4. **Source code**: Keep pipeline logic in dedicated SQL/Python files; use parameters for environment-specific values.
5. **Testing**: Use development mode and dry run; create sample or subset datasets for dev/test pipelines.

For detailed syntax, configuration, and API links, see [references/REFERENCES.md](references/REFERENCES.md).

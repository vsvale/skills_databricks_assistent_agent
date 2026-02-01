---
name: lakeflow-sdp
description: Develop and operate Lakeflow Spark Declarative Pipelines (SDP) for batch and streaming ETL on Databricks. Covers pipelines, flows, streaming tables, materialized views, expectations, Auto Loader, and CDC. Use when building or configuring ETL pipelines, defining streaming tables or materialized views in SQL or Python, setting data quality expectations, ingesting from cloud storage or message buses, or when the user mentions Lakeflow SDP, SDP, DLT-style pipelines, or declarative pipelines on Databricks.
---

# Lakeflow Spark Declarative Pipelines (SDP)

Lakeflow Spark Declarative Pipelines (SDP) is a declarative framework for batch and streaming data pipelines in SQL and Python on Databricks. It extends Apache Spark Declarative Pipelines and runs on Databricks Runtime. Pipelines orchestrate flows automatically, support incremental processing, and integrate expectations for data quality.

## When to Use This Skill

Use when the user needs to:
- Create or configure ETL pipelines (streaming tables, materialized views, flows)
- Ingest from Unity Catalog Volumes (recommended) or cloud storage (S3, ADLS Gen2, GCS)
- Ingest from message buses (Kafka, Kinesis, Pub/Sub, EventHub, Pulsar)
- Define data quality expectations (warn, drop, fail on invalid records)
- Use Auto Loader, CDC, or incremental refresh in a pipeline
- Develop pipeline code in SQL or Python and configure target catalog/schema
- Troubleshoot pipeline updates, expectations, or configuration

## Key Concepts

| Concept | Description |
|--------|-------------|
| **Pipeline** | Unit of development and execution. Contains flows, streaming tables, materialized views, and sinks. Configured with source code files and target catalog/schema. |
| **Flow** | Data processing step: reads a source, applies logic, writes to a target. Types: Append (streaming), materialized view (batch incremental), AUTO CDC (streaming). |
| **Streaming table** | Unity Catalog managed table for streaming/incremental processing. **Recommended for bronze layer ingestion.** Use for append-only or CDC ingestion. Define with `CREATE STREAMING TABLE` (SQL) or equivalent in Python. |
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

---

## Streaming Tables (Detailed Guide)

Streaming tables are Delta tables with extra support for streaming or incremental data processing. They are the **recommended approach for bronze layer ingestion** in the medallion architecture.

**Two ways to create streaming tables:**
1. **In Lakeflow Pipelines**: Define in pipeline SQL/Python code; managed by the pipeline; use for complex multi-table ETL workflows
2. **In Databricks SQL**: Create standalone streaming tables with `CREATE STREAMING TABLE`; automatically backed by a serverless pipeline; use for simple ingestion tasks

| Feature | Pipeline Streaming Tables | Databricks SQL Streaming Tables |
|---------|--------------------------|--------------------------------|
| **Creation** | Define in pipeline code | `CREATE STREAMING TABLE` in SQL editor |
| **Management** | Managed by parent pipeline | Standalone with auto-created pipeline |
| **Compute** | Pipeline's compute (serverless or classic) | Serverless only |
| **Schedule** | Pipeline schedule or table schedule | Table-level schedule or trigger |
| **Viewing** | Pipeline UI, type = `ETL` | Jobs & Pipelines UI, type = `MV/ST` |
| **ALTER commands** | Limited (use `CREATE OR REFRESH`) | Full `ALTER STREAMING TABLE` support |
| **Use case** | Multi-table ETL pipelines | Simple data ingestion |

### Why Use Streaming Tables for Bronze Layer

| Benefit | Description |
|---------|-------------|
| **Exactly-once processing** | Each input row is handled only once, modeling most ingestion workloads |
| **Incremental processing** | Only new data is processed on each refresh |
| **Checkpoint management** | Automatic state tracking for reliable streaming |
| **Schema evolution** | Supports schema inference and evolution with Auto Loader |
| **Data quality** | Integrate expectations directly in table definitions |
| **Low-latency streaming** | Designed for bounded state with checkpoint management |
| **Append-only optimized** | Best for data sources that are naturally append-only |

### Creating Streaming Tables

#### Basic Syntax

```sql
{ CREATE OR REFRESH STREAMING TABLE | CREATE STREAMING TABLE [ IF NOT EXISTS ] }
  table_name
  [ table_specification ]
  [ table_clauses ]
  [ AS query ]
```

#### From Unity Catalog Volumes (Recommended)

Use Unity Catalog Volumes instead of direct cloud storage paths for better governance and security:

See [scripts/create_streaming_table_unity_catalog_volumes.sql](scripts/create_streaming_table_unity_catalog_volumes.sql) for examples of creating streaming tables from JSON and CSV files in Unity Catalog Volumes.

#### With Data Quality Expectations

See [scripts/create_streaming_table_expectations.sql](scripts/create_streaming_table_expectations.sql) for an example of a streaming table with data quality expectations.

**Note:** Expectations in pipelines use `CONSTRAINT name EXPECT (condition) ON VIOLATION action` syntax. The constraint name must be unique per dataset.

#### With Explicit Schema

See [scripts/create_streaming_table_explicit_schema.sql](scripts/create_streaming_table_explicit_schema.sql) for an example of a streaming table with an explicit schema.

#### With Row Filters and Column Masks

See [scripts/create_streaming_table_row_filters_masks.sql](scripts/create_streaming_table_row_filters_masks.sql) for an example of a streaming table with row filters and column masks.

### Streaming Table Options

#### read_files() Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `format` | File format (json, csv, parquet, avro, text) | `format => 'json'` |
| `header` | CSV has header row | `header => true` |
| `inferSchema` | Infer schema from data | `inferSchema => true` |
| `inferColumnTypes` | Infer column types | `inferColumnTypes => true` |
| `schemaHints` | Type hints for specific columns | `schemaHints => 'date_col DATE'` |
| `schema` | Explicit schema definition | `schema => 'id INT, name STRING'` |
| `includeExistingFiles` | Process existing files (default: true) | `includeExistingFiles => false` |

#### Table Clauses

| Clause | Description | Example |
|--------|-------------|---------|
| `PARTITIONED BY` | Partition columns (use CLUSTER BY instead) | `PARTITIONED BY (date)` |
| `CLUSTER BY` | Liquid clustering (recommended) | `CLUSTER BY AUTO` or `CLUSTER BY (col1, col2)` |
| `COMMENT` | Table description | `COMMENT 'Bronze customer data'` |
| `TBLPROPERTIES` | Table properties | `TBLPROPERTIES ('delta.appendOnly' = 'true')` |

### Scheduling Refreshes

#### Scheduled Refresh (Time-based)

See [scripts/create_streaming_table_schedule.sql](scripts/create_streaming_table_schedule.sql) for examples of scheduled refreshes (hourly, cron).

**Accepted intervals for SCHEDULE EVERY:**
| Time Unit | Valid Range |
|-----------|-------------|
| HOUR/HOURS | 1-72 |
| DAY/DAYS | 1-31 |
| WEEK/WEEKS | 1-8 |

#### Trigger-based Refresh

Automatically refresh when upstream data changes:

See [scripts/create_streaming_table_trigger.sql](scripts/create_streaming_table_trigger.sql) for examples of trigger-based refreshes.

**Trigger limitations:**
- Maximum 10 upstream data sources per streaming table
- Maximum 1000 streaming tables with TRIGGER ON UPDATE per workspace
- Minimum interval is 1 minute

### Altering Streaming Tables

Use `ALTER STREAMING TABLE` to modify schedules, triggers, row filters, tags, and column properties.

**Important:** Altering a pipeline-created dataset in ways that contradict the defining SQL can cause changes to be reverted. See documentation on using ALTER commands with Lakeflow Spark Declarative Pipelines.

#### Schedule and Trigger Management

See [scripts/alter_streaming_table_schedule.sql](scripts/alter_streaming_table_schedule.sql) for examples of managing schedules and triggers.

#### Column Management

See [scripts/alter_streaming_table_columns.sql](scripts/alter_streaming_table_columns.sql) for examples of column management (comments, masks, tags).

#### Row Filters and Table Tags

See [scripts/alter_streaming_table_row_filters.sql](scripts/alter_streaming_table_row_filters.sql) for examples of managing row filters and table tags.

**Notes:**
- Row filters and column masks added after creation only propagate to downstream tables after the next update
- For continuous pipelines, propagating changes requires a pipeline restart
- You cannot modify the schedule of a streaming table created within a Lakeflow Pipeline using ALTER commands; use the pipeline editor or `CREATE OR REFRESH` statement instead

### Refreshing Streaming Tables

#### Manual Refresh

See [scripts/refresh_streaming_table.sql](scripts/refresh_streaming_table.sql) for examples of manual refresh modes (SYNC, ASYNC, FULL).

#### How Refresh Works

**Refresh Modes:**
- **SYNC (Default)**: Blocks until the refresh is complete.
- **ASYNC**: Triggered as a background job; returns a pipeline link immediately.
- **FULL**: Truncates and rebuilds the table from scratch.

**Incremental Refresh (Default):**
- Only evaluates new rows that arrived since the last update
- Appends only the new data to the streaming table
- Uses the current definition of the streaming table
- Modifying table definition does NOT automatically recalculate existing data
- If modification is incompatible with existing data (e.g., changing data type), next refresh fails

**Examples of how changes affect refresh:**
- **Removing a filter**: Will not reprocess previously filtered rows
- **Changing column projections**: Won't affect existing data processing
- **Joins with static snapshots**: Use snapshot state at initial processing time; late-arriving data matching updated snapshot will be ignored (can drop facts if dimensions are late)
- **Modifying CAST of existing column**: Results in an error

**Full Refresh:**
- Truncates the table and reprocesses all data with latest definition
- Use when you need to apply definition changes to existing data
- Syntax: `REFRESH STREAMING TABLE table_name FULL;`

**Warning:** 
- Avoid FULL refresh on sources without complete history retention
- Sources like Kafka with short retention periods may lose old data permanently
- Full refresh truncates existing data before reprocessing

#### Refresh Timeouts

- Streaming tables created/refreshed after August 14, 2025 use SQL warehouse timeout
- Default timeout: 2 days if warehouse has no timeout set
- Timeout only synchronizes on manual `CREATE OR REFRESH` statements
- Scheduled updates retain timeout from most recent `CREATE OR REFRESH`
- Override with `STATEMENT_TIMEOUT` configuration in SQL

#### Check Refresh Status

```sql
DESCRIBE EXTENDED my_streaming_table;
```

### Common Errors and Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `TABLE_OR_VIEW_NOT_FOUND` | Table doesn't exist or wrong catalog/schema | Verify table name and use fully qualified name |
| `Streaming read error on change/delete` | Source has modified/deleted records | Use append-only sources or handle with Python error handling |
| `Schema mismatch` | Query returns columns not in schema | Ensure table_specification contains all columns from query |
| `Schedule conflict` | Both SCHEDULE and TRIGGER specified | Use only one scheduling method |
| `Permission denied` | Missing required privileges | Grant `SELECT` on sources, `CREATE TABLE` on target schema |
| `Expectation failure` | Data violates FAIL UPDATE constraint | Fix source data or adjust expectation |
| `Refresh timeout` | Long-running refresh exceeds timeout | Increase `STATEMENT_TIMEOUT` or optimize query |

### Streaming Table Characteristics and Limitations

#### How Streaming Tables Work

**Ingestion Pattern:**
- Streaming tables are designed for **append-only data sources**
- Each input row is processed **only once** (exactly-once semantics)
- On each update, flows read changed information in streaming sources and append to the table
- A row already appended will NOT be re-queried in later updates

**Query Changes:**
- If you modify the query (e.g., from `SELECT LOWER(name)` to `SELECT UPPER(name)`):
  - Existing rows remain in lowercase
  - Only new rows will be uppercase
  - To update all rows, trigger a **full refresh**

**Stream-Snapshot Joins:**
- Joins between a stream and a dimension table snapshot the dimension when the stream starts
- Dimension changes after stream start are NOT reflected in the join
- Acceptable for "fast-but-wrong" scenarios with high transaction volumes
- For always-correct joins that recompute on dimension changes, use **materialized views** instead

#### Limitations

**Table Operations:**
1. **ALTER TABLE**: Standard `ALTER TABLE` commands are disallowed; use `CREATE OR REFRESH` or `ALTER STREAMING TABLE`
2. **DML operations**: `INSERT INTO`, `MERGE`, and schema evolution via DML not supported
3. **Unsupported commands**: 
   - `CREATE TABLE ... CLONE <streaming_table>`
   - `COPY INTO`
   - `ANALYZE TABLE`
   - `RESTORE`
   - `TRUNCATE`
   - `GENERATE MANIFEST`
   - `[CREATE OR] REPLACE TABLE`
4. **Table management**: Cannot rename table; changing owner has restrictions
5. **Columns**: Generated columns, identity columns, and default columns not supported
6. **Delta Sharing**: Not supported for streaming tables
7. **Catalog**: Table constraints (PRIMARY KEY, FOREIGN KEY) not supported in `hive_metastore` catalog (Unity Catalog only)

**State Management:**
- Streaming tables are designed for **bounded state** with checkpoint management
- Streams should be naturally bounded OR bounded with a watermark
- Unbounded streams without watermarks can cause pipeline failures due to memory pressure
- See "Optimize stateful processing with watermarks" in documentation

**Limited Evolution:**
- Without full refresh, different queries process different rows over time
- Must be aware of all previous query versions
- Full refresh required to reprocess existing rows with new query logic

### Required Permissions

#### For Pipeline-Created Streaming Tables

**Run-as user (pipeline owner) must have:**
- `SELECT` privilege on base tables referenced by the streaming table
- `USE CATALOG` privilege on parent catalog
- `USE SCHEMA` privilege on parent schema
- `CREATE MATERIALIZED VIEW` privilege on the schema for the streaming table

**To update the pipeline:**
- `USE CATALOG` privilege on parent catalog
- `USE SCHEMA` privilege on parent schema
- Ownership of the streaming table OR `REFRESH` privilege on the streaming table
- Owner of the streaming table must have `SELECT` privilege on base tables

**To query the streaming table:**
- `USE CATALOG` privilege on parent catalog
- `USE SCHEMA` privilege on parent schema
- `SELECT` privilege on the streaming table

#### For Databricks SQL Streaming Tables

**To create:**
- Workspace must support serverless pipelines
- SQL warehouse using `Current` channel, OR
- Compute with standard access mode on DBR 13.3 LTS+, OR
- Compute with dedicated access mode on DBR 15.4 LTS+
- `USE CATALOG` and `USE SCHEMA` privileges
- `CREATE TABLE` privilege on the schema
- Privileges for accessing source data tables/locations

**To refresh:**
- Only table owners can refresh streaming tables
- Refreshes run using the owner's permissions

**To query:**
- `USE CATALOG` and `USE SCHEMA` privileges
- `SELECT` privilege on the streaming table
- SQL warehouse on `Current` channel or appropriate compute (see create requirements)

---

## SQL Syntax (Summary)

See [references/REFERENCES.md](references/REFERENCES.md) for detailed syntax or the scripts directory for examples.


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

- **Unity Catalog Volumes (Recommended)**: Store raw data files in Unity Catalog Volumes for centralized governance. Use `read_files()` with volume paths: `/Volumes/catalog/schema/volume/path`
- **Cloud storage**: Prefer **Auto Loader** with streaming tables for incremental file ingestion. Use `read_files()` in SQL (with `STREAM` for streaming). 
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
| Refresh stuck/hung | Check Spark UI for bottlenecks; consider partitioning or clustering; check source data volume. |

## Best Practices

1. **Serverless + Unity Catalog**: Use serverless compute and Unity Catalog for new pipelines when possible.
2. **Unity Catalog Volumes**: Store raw data in Volumes instead of direct cloud storage paths for better governance.
3. **Streaming tables for bronze**: Use streaming tables for all bronze layer ingestion for incremental processing.
4. **Run-as service principal**: Use a service principal for production pipelines to avoid dependency on a single user.
5. **Expectations**: Name clearly; use `drop` or `fail` for critical constraints; monitor metrics.
6. **Liquid clustering**: Use `CLUSTER BY AUTO` instead of `PARTITIONED BY` for better performance.
7. **Source code**: Keep pipeline logic in dedicated SQL/Python files; use parameters for environment-specific values.
8. **Testing**: Use development mode and dry run; create sample or subset datasets for dev/test pipelines.

## Example Bronze Layer Scripts

See [scripts/bronze.sql](scripts/bronze.sql) for complete examples of bronze layer streaming tables including:
- JSON and CSV ingestion patterns
- Data quality expectations
- Scheduled and trigger-based refreshes
- Partitioning and liquid clustering

---

For detailed syntax, configuration, and API links, see [references/REFERENCES.md](references/REFERENCES.md).

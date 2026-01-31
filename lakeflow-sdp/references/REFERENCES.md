# Lakeflow Spark Declarative Pipelines (SDP) References

## Official Documentation

- **Lakeflow Spark Declarative Pipelines (overview)**: https://docs.databricks.com/aws/en/ldp/
- **SDP concepts** (pipelines, flows, streaming tables, materialized views, sinks): https://docs.databricks.com/aws/en/ldp/concepts.html
- **Develop pipelines**: https://docs.databricks.com/aws/en/ldp/develop.html
- **Configure pipelines**: https://docs.databricks.com/aws/en/ldp/configure-pipeline.html
- **Configure serverless pipeline**: https://docs.databricks.com/aws/en/ldp/serverless.html
- **Pipeline updates** (run, development mode, dry run): https://docs.databricks.com/aws/en/ldp/updates.html
- **Monitor pipelines** (observability, event logs): https://docs.databricks.com/aws/en/ldp/observability.html
- **Pipeline limitations**: https://docs.databricks.com/aws/en/ldp/limitations.html
- **Use Unity Catalog with pipelines**: https://docs.databricks.com/aws/en/ldp/unity-catalog.html
- **Legacy Hive metastore**: https://docs.databricks.com/aws/en/ldp/hive-metastore.html
- **LIVE schema (legacy)**: https://docs.databricks.com/aws/en/ldp/live-schema.html

## Streaming Tables

### Overview and Concepts
- **How streaming tables work**: https://docs.databricks.com/aws/en/ldp/streaming-tables
- **Use streaming tables in Databricks SQL**: https://docs.databricks.com/aws/en/ldp/dbsql/streaming

### SQL Language Reference
- **CREATE STREAMING TABLE**: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-streaming-table
- **CREATE STREAMING TABLE (pipelines)**: https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-streaming-table
- **ALTER STREAMING TABLE**: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-streaming-table
- **REFRESH (MATERIALIZED VIEW or STREAMING TABLE)**: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-refresh-full
- **DROP TABLE**: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-table

### Streaming Table Features
- **Load data in pipelines**: https://docs.databricks.com/aws/en/ldp/load.html
- **Transform data with pipelines**: https://docs.databricks.com/aws/en/ldp/transform.html
- **Stateful processing with watermarks**: https://docs.databricks.com/aws/en/ldp/stateful.html
- **Row filters and column masks**: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-row-filter
- **Table constraints (PRIMARY KEY, FOREIGN KEY)**: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-constraint

## Developer Reference

- **Pipeline developer reference**: https://docs.databricks.com/aws/en/ldp/developer/
- **Develop pipeline code with SQL**: https://docs.databricks.com/aws/en/ldp/developer/sql-dev.html
- **Pipeline SQL language reference**: https://docs.databricks.com/aws/en/ldp/developer/sql-ref.html
- **Develop pipeline code with Python**: https://docs.databricks.com/aws/en/ldp/developer/python-dev.html
- **Lakeflow SDP Python language reference**: https://docs.databricks.com/aws/en/ldp/developer/python-ref.html
- **Target catalog and schema**: https://docs.databricks.com/aws/en/ldp/target-schema.html
- **Parameters with pipelines**: https://docs.databricks.com/aws/en/ldp/parameters.html
- **Manage Python dependencies**: https://docs.databricks.com/aws/en/ldp/developer/external-dependencies.html
- **Import Python modules from workspace/Git**: https://docs.databricks.com/aws/en/ldp/import-workspace-files.html

## Data Quality and Expectations

- **Manage data quality with expectations**: https://docs.databricks.com/aws/en/ldp/expectations.html
- **Expectation recommendations and advanced patterns**: https://docs.databricks.com/aws/en/ldp/expectation-patterns.html
- **Query data quality / expectations metrics**: https://docs.databricks.com/aws/en/ldp/monitor-event-logs.html#data-quality-metrics

## Flows, Tables, and Ingestion

- **Load and process data with SDP flows**: https://docs.databricks.com/aws/en/ldp/flows.html
- **How materialized views work**: https://docs.databricks.com/aws/en/ldp/materialized-views.html
- **Stream records with sinks**: https://docs.databricks.com/aws/en/ldp/sinks.html
- **Auto Loader**: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader.html
- **read_files table-valued function**: https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files.html
- **read_kafka table-valued function**: https://docs.databricks.com/aws/en/sql/language-manual/functions/read_kafka.html
- **CDC (AUTO CDC API)**: https://docs.databricks.com/aws/en/ldp/cdc.html
- **Cloud storage configuration**: https://docs.databricks.com/aws/en/ldp/hive-metastore.html#configure-cloud-storage

## Unity Catalog Volumes

- **Unity Catalog Volumes overview**: https://docs.databricks.com/aws/en/volumes/
- **Create and manage volumes**: https://docs.databricks.com/aws/en/volumes/manage-volumes.html
- **Work with files in volumes**: https://docs.databricks.com/aws/en/volumes/work-with-files.html

## Configuration and Compute

- **Pipeline properties reference**: https://docs.databricks.com/aws/en/ldp/properties.html
- **Configure classic compute**: https://docs.databricks.com/aws/en/ldp/configure-compute.html
- **Autoscaling**: https://docs.databricks.com/aws/en/ldp/auto-scaling.html

## UI and Editor

- **Lakeflow Pipelines Editor** (multi-file editor): https://docs.databricks.com/aws/en/ldp/multi-file-editor.html
- **Develop pipeline code locally**: https://docs.databricks.com/aws/en/ldp/develop-locally.html
- **Convert pipeline to Databricks Asset Bundle**: https://docs.databricks.com/aws/en/ldp/convert-to-dab.html

## Tutorials

- **Tutorials**: https://docs.databricks.com/aws/en/ldp/tutorials.html
- **Tutorial: ETL pipeline using change data capture**: https://docs.databricks.com/aws/en/ldp/tutorial-pipelines.html

## Databricks SQL and Delta

- **Pipelines in Databricks SQL**: https://docs.databricks.com/aws/en/ldp/dbsql/dbsql-for-ldp.html
- **Delta Lake in Databricks**: https://docs.databricks.com/aws/en/delta/
- **Procedural vs. declarative data processing**: https://docs.databricks.com/aws/en/data-engineering/procedural-vs-declarative.html
- **Liquid clustering**: https://docs.databricks.com/aws/en/delta/clustering.html

## API and CLI

- **Pipelines REST API**: https://docs.databricks.com/api/workspace/pipelines
- **Databricks CLI pipelines commands**: https://docs.databricks.com/aws/en/dev-tools/cli/reference/pipelines-commands.html
- **Pipeline task for jobs**: https://docs.databricks.com/aws/en/jobs/pipeline.html

## Product and Runtime

- **Lakeflow Spark Declarative Pipelines product / pricing**: https://www.databricks.com/product/pricing/lakeflow-declarative-pipelines
- **Runtime channels (SDP)**: https://docs.databricks.com/aws/en/release-notes/dlt/#runtime-channels

## Community Resources

- **Databricks Community - Data Engineering**: https://community.databricks.com/t5/data-engineering/bd-p/data-engineering
- **Create flow for streaming table (community discussion)**: https://community.databricks.com/t5/data-engineering/create-flow-for-streaming-table/td-p/119158

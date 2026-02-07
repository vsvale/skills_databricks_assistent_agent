# References

## Databricks Documentation
- [Delta Live Tables - AUTO CDC (Python)](https://docs.databricks.com/aws/en/ldp/cdc?language=Python)
- [Delta Live Tables - AUTO CDC (SQL)](https://docs.databricks.com/aws/en/ldp/cdc?language=SQL)
- [Tutorial: Build an ETL pipeline using CDC (Python)](https://docs.databricks.com/aws/en/ldp/tutorial-pipelines?language=Python)
- [Tutorial: Build an ETL pipeline using CDC (SQL)](https://docs.databricks.com/aws/en/ldp/tutorial-pipelines?language=SQL)
- [Lakeflow Pipelines CDC (General)](https://docs.databricks.com/aws/en/ldp/cdc)
- [Merge Schema Evolution](https://docs.databricks.com/aws/en/delta/update-schema#merge-schema-evolution)
- [Delta Change Data Feed (CDF)](https://docs.databricks.com/en/delta/delta-change-data-feed.html)
- [Delta Live Tables - APPLY CHANGES INTO (Legacy)](https://docs.databricks.com/en/delta-live-tables/cdc.html)
- [Liquid Clustering for Delta Tables](https://docs.databricks.com/aws/en/delta/clustering)
- [Deletion Vectors](https://docs.databricks.com/aws/en/delta/deletion-vectors)
- [SQL Syntax: QUALIFY Clause](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-select-qualify)
- [SQL Syntax: SELECT Statement](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-select)
- [SQL Scripting: DECLARE & SET VAR](https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-declare-variable.html)
- [SQL Function: row_number](https://docs.databricks.com/aws/en/sql/language-manual/functions/row_number)
- [PySpark Function: row_number](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.row_number.html)

## Release Notes & Updates (2025-2026)
- [Databricks Release Notes Overview](https://docs.databricks.com/aws/en/release-notes/)
- [Databricks SQL Release Notes 2025](https://docs.databricks.com/aws/en/sql/release-notes/2025)
- [Delta Live Tables Release Notes (Lakeflow)](https://docs.databricks.com/en/release-notes/delta-live-tables/index.html)
- [Azure Databricks Release Notes (June 2025)](https://learn.microsoft.com/en-us/azure/databricks/release-notes/product/2025/june)

## Delta Lake Open Source Documentation
- [Delta Merge Examples](https://docs.delta.io/delta-update/#merge-examples)
- [Performance Tuning](https://docs.delta.io/delta-update/#performance-tuning)
- [Arrays of Structs in Merge](https://docs.delta.io/delta-update/#special-considerations-for-schemas-that-contain-arrays-of-structs)
- [SCD Type 2 Operations](https://docs.delta.io/delta-update/#slowly-changing-data-scd-type-2-operation-into-delta-tables)
- [Write Change Data into a Delta Table](https://docs.delta.io/delta-update/#write-change-data-into-a-delta-table)
- [Streaming Upserts (foreachBatch)](https://docs.delta.io/delta-update/#upsert-from-streaming-queries-using-foreachbatch)

## Blogs & Articles
- [Merge in Python: Syntax & Performance Comparison](https://databrickster.medium.com/merge-in-python-which-one-has-the-nicest-syntax-and-is-the-fastest-845799729c23)
- [Delta Lake Merge Deep Dive (2023-02-14)](https://delta.io/blog/2023-02-14-delta-lake-merge/)
- [Databricks Community: Merge Deep Dive (Internals)](https://community.databricks.com/t5/technical-blog/merge-deep-dive/ba-p/111190)
- [Databricks Community: QUALIFY Clause (Highly Selective SQL)](https://community.databricks.com/t5/technical-blog/highly-selective-sql-refined-beyond-the-where/ba-p/64459)

## Internal Guides
- [dlt_cdc_tutorial.md](dlt_cdc_tutorial.md): Step-by-step tutorial for building CDC pipelines with DLT.
- [change_data_feed.md](change_data_feed.md): Detailed guide on enabling and using Delta Change Data Feed.
- [merge_into_patterns.md](merge_into_patterns.md): Manual SQL and Python MERGE patterns (SCD Type 2, Deduplication).
- [manual_streaming_cdc.md](manual_streaming_cdc.md): Manual streaming CDC patterns (foreachBatch, window deduplication).

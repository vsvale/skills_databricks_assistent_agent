---
name: medallion-architecture
description: Design and implement Medallion architecture (Bronze, Silver, Gold layers) with Delta Lake, Spark, and Databricks. Covers layer responsibilities, data quality patterns, performance optimization, dimensional modeling, and governance. Use when designing data lakehouse architecture, deciding layer structure, implementing multi-hop pipelines, or when the user mentions Medallion, Bronze/Silver/Gold layers, data quality tiers, or lakehouse architecture patterns.
---

# Medallion Architecture with Delta Lake

The Medallion architecture is a data design pattern used to logically organize data in a lakehouse, with the goal of **progressively improving the structure and quality of data** as it flows through each layer. This multi-hop approach provides a scalable blueprint for **modern Data Products**, enabling incremental ETL, ACID transactions, and the ability to recreate tables from raw data at any time.

> [!NOTE]
> In modern architectures, Medallion layers are often referred to by aliases:
> - **Bronze**: Raw, Landing, Staging
> - **Silver**: Structured, Cleansed, Conformed, Enriched
> - **Gold**: Curated, Presentation, Analytics, Workspace

## When to Use This Skill

Use this skill when you need to:
- Design or refactor a data lakehouse architecture
- Decide how to structure data layers and transformations
- Implement data quality patterns across layers
- Optimize performance for different workload types
- Apply dimensional modeling and aggregation strategies
- Establish governance, security, and collaboration policies
- Troubleshoot architectural anti-patterns
- Plan Bronze → Silver → Gold data flows

## Architecture Overview

The Medallion architecture separates concerns across three layers:

| Layer | Purpose | Data Quality | Users | Transformations |
|-------|---------|--------------|-------|-----------------|
| **Bronze** | Raw data landing zone | As-is from source | Data engineers, Compliance | Minimal (metadata only) |
| **Silver** | Cleaned, validated data | High quality, validated | Data scientists, ML engineers, Analysts | Cleaning, deduplication, normalization |
| **Gold** | Analytics-ready data | Business-level aggregates | Business analysts, Apps developers, Partners | Aggregation, dimensional modeling |

### Data Flow Pattern

```
Source Systems → Bronze (raw) → Silver (cleaned) → Gold (aggregated) → BI/ML
```

Each layer builds on the previous one, with clear contracts and responsibilities.

---

## Bronze Layer: Raw Data Ingestion

### Purpose

The Bronze layer is where we land all data from external source systems. Table structures correspond to source systems "as-is," along with metadata columns. The focus is on **quick Change Data Capture (CDC)**, historical archiving, data lineage, auditability, and reprocessing capability without rereading from source systems.

### Key Characteristics

- **Immutable**: Data is append-only; never modified after ingestion
- **Complete**: Contains all source data, including bad records
- **Timestamped**: Enriched with ingestion metadata
- **Delta Lake format**: Ensures ACID transactions and time travel

### Best Practices

**1. Use Delta Lake with append-only mode**
```sql
TBLPROPERTIES (
  'delta.appendOnly' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true'
);
```

**2. Add metadata columns**: `_ingestion_timestamp`, `_source_file`, `_source_offset`, `_ingestion_job_id`

**3. Minimal transformations only**
- ✅ Adding metadata columns, parsing timestamps for partitioning
- ❌ Data cleaning, validation, filtering, business logic

**4. Use Unity Catalog Volumes**: `/Volumes/main/raw/data` instead of direct cloud storage paths.

**6. Abstract via Views**: Use **Bronze Views** to parse raw formats (e.g., JSON to columns) for Silver consumption. This maintains raw fidelity in storage while simplifying downstream SQL.

**7. Configure for append-only workloads**: Enable auto-optimize and auto-compact.

### Bronze Layer Examples

See [scripts/bronze_ingestion_example.sql](scripts/bronze_ingestion_example.sql) for complete examples.

---

## Silver Layer: Cleaned and Validated Data

### Purpose

The Silver layer provides an **"Enterprise view"** of key business entities. It matches, merges, and cleanses data to create **trusted, reusable Data Products** (e.g., `dim_customers`, `fact_transactions`). Follows the **ELT** methodology with "just-enough" transformations to prioritize speed and agility.

### Key Characteristics

- **Validated**: Data quality checks applied
- **Deduplicated**: Duplicate records removed
- **Normalized**: Consistent data types and formats
- **Conformed**: Business logic applied
- **Non-aggregated**: Detailed, row-level data preserved

### Best Practices

**1. Always build from Bronze or Silver** - Never ingest directly to Silver. Bronze provides a safety buffer for schema changes and corrupt records.

**2. Use streaming reads from Bronze** - Enable incremental processing with `STREAM(bronze.table)`

**3. Implement data quality checks** - Use expectations with `ON VIOLATION` actions (WARN/DROP/FAIL)

**4. Handle deduplication** - Use window functions or `APPLY CHANGES` for CDC

**5. Maintain non-aggregated representation** - Keep row-level detail for flexible downstream aggregations.

**6. Model for flexibility** - Use the **VARIANT** data type for semi-structured data to preserve schema flexibility while maintaining performance.

**7. Quarantine bad records** - Route records that fail validation to a dedicated **quarantine schema** or table. This prevents pipeline failure and enables auditing of data quality "debt."

### Silver Layer Examples

See [scripts/silver_cleaning_example.sql](scripts/silver_cleaning_example.sql) for complete examples including:
- Data quality checks and filtering
- Deduplication strategies
- Type casting and normalization
- Schema evolution handling
- Change data capture (CDC) patterns

---

## Gold Layer: Analytics-Ready Data

### Purpose

The Gold layer organizes data into consumption-ready, **project-specific Data Products** with de-normalized, read-optimized models. These are often "Consumer Data Products" tailored for specific domains like Customer Analytics or Marketing summaries. Supports both star schemas and flat wide tables.

### Key Characteristics

- **Aggregated**: Pre-computed metrics and summaries
- **Dimensional**: Star or snowflake schema
- **Optimized**: Clustered and indexed for BI queries
- **Secured**: Row and column-level security applied
- **Business-aligned**: Matches business terminology and KPIs

### Best Practices

**1. Apply dimensional modeling** - Use star/snowflake schemas with fact and dimension tables

**2. Pre-aggregate for performance** - Create aggregated tables for common BI queries

**3. Use liquid clustering** - `CLUSTER BY (columns)` or `CLUSTER BY AUTO` for BI optimization

**4. Implement security** - Apply row-level filters and column masking for sensitive data

**5. Assign clear ownership** - Document business owner, purpose, metrics, and semantic definitions (glossary).

**6. Choose modeling for purpose**:
- **Star Schema**: Best for BI tools (Power BI, Tableau) to minimize join complexity.
- **Wide Tables**: Best for specialized dashboards or ML features to maximize read performance and simplify analytical queries.

### Gold Layer Examples

See [scripts/gold_aggregation_example.sql](scripts/gold_aggregation_example.sql) for complete examples including:
- Star schema dimensional modeling (Fact & Dim tables)
- Business-ready views: `customer_spending`, `sales_pipeline_summary`
- Pre-aggregated fact tables
- Materialized views for performance
- Row-level and column-level security
- Liquid clustering for BI queries
- **Approximate Metrics**: Using HLL (HyperLogLog) for low-latency dashboards.
- **Modeling Precision**: Fact/Dimension vs. Denormalized Wide Tables based on tool consumption.

---

## Cross-Layer Considerations

### Performance & Well-Architected

Adhere to the [Well-Architected Framework](references/well_architected.md) pillars. See [references/performance.md](references/performance.md) for compute/storage optimization, [references/cost_optimization.md](references/cost_optimization.md) for cost governance, [references/security.md](references/security.md) for IAM, and [references/reliability.md](references/reliability.md) for DR.

#### Partitioning and Clustering

| Layer | Strategy | Example |
|-------|----------|---------|
| **Bronze** | Partition by ingestion date | `PARTITIONED BY (DATE(_ingestion_timestamp))` |
| **Silver** | Liquid clustering by query patterns | `CLUSTER BY (customer_id, event_date)` |
| **Gold** | Liquid clustering for BI | `CLUSTER BY AUTO` |

**Recommendation**: Prefer liquid clustering (`CLUSTER BY`) over static partitioning for Silver and Gold layers.

#### Z-Ordering (Legacy)

For tables not using liquid clustering, apply Z-ordering:

```sql
OPTIMIZE silver.customer_events
ZORDER BY (customer_id, event_date);
```

Enable predictive optimization for intelligent file management:
```sql
ALTER TABLE bronze.raw_events ENABLE PREDICTIVE OPTIMIZATION;
```

#### Latency Optimization

| Pattern | Recommended Use | Latency Profile |
|---------|-----------------|-----------------|
| **DLT Streaming** | Append-only or simple increments | Seconds to minutes |
| **Delta MERGE** | Frequent upserts/deletes | Minutes to hours |
| **Materialized Views** | Complex aggregations | Refresh-based |

**Tip**: Use **Delta Live Tables** (DLT) for the lowest latency in Medallion pipelines; manual `MERGE` operations on large tables can increase latency due to file rewriting and fragmentation.

### Storage & Cost Management

The Medallion pattern effectively "triples" storage. Manage costs with:
1. **Delta Vacuum**: Remove old file versions regularly to reclaim space.
2. **Optimize & Compaction**: Prevent "small file" performance degradation.
3. **binSize Tuning**: Set `delta.targetFileSize` (e.g., 1GB) to optimize read speeds for Gold tables.

See [references/storage_management.md](references/storage_management.md) for detailed lifecycle and compute optimization.

### Data Quality Monitoring

Implement monitoring at each layer:

| Layer | Monitoring Focus | Tools |
|-------|------------------|-------|
| **Bronze** | Ingestion completeness, file counts | Event logs, metrics |
| **Silver** | Validation failures, null rates | Expectations, data quality dashboard |
| **Gold** | Metric accuracy, freshness | BI dashboards, alerts |

### Unified Governance with Unity Catalog

Manage Data and AI assets (Models, Dashboards) together. See [references/governance.md](references/governance.md) for details.

1.  **Catalog structure**: Organize by layer
    ```
    main_catalog
    ├── bronze (schema)
    ├── silver (schema)
    └── gold (schema)
    ```

2. **Access control**: Grant permissions by layer
   ```sql
   -- Data engineers: full access to Bronze and Silver
   GRANT SELECT, MODIFY ON SCHEMA bronze TO `data_engineers`;
   GRANT SELECT, MODIFY ON SCHEMA silver TO `data_engineers`;
   
   -- Analysts: read-only access to Gold
   GRANT SELECT ON SCHEMA gold TO `analysts`;
   ```

3.  **Data lineage**: Track transformations across layers using Unity Catalog lineage
4.  **Audit Logs**: Query `system.access.audit` for compliance monitoring.

### Interoperability & Usability

Ensure the platform is open and usable by all personas. See [references/interoperability.md](references/interoperability.md).

1.  **Open Standards**: Use Delta Lake/Parquet for storage and MLflow for models to avoid vendor lock-in.
2.  **Multi-Language**: Support SQL, Python, Scala, and R on the same data.
3.  **Integration**: Use Lakeflow Connect and Delta Sharing for seamless external integration.

### Collaboration & Discovery

Unified governance enables organization-wide collaboration:
- **Discovery**: Use Unity Catalog's **Catalog Explorer** to find datasets, review schemas, and trace lineage.
- **Access**: Manage permissions centrally; use storage credentials for secure self-service.
- **Sharing**: Use Delta Sharing to eliminate data silos and share live data with partners.

### Workload Isolation

Separate compute resources by layer:

| Layer | Compute Type | Rationale |
|-------|--------------|-----------|
| **Bronze** | Serverless or dedicated ingestion cluster | Predictable, high-throughput workload |
| **Silver** | Serverless or shared cluster | Mixed batch and streaming |
| **Gold** | SQL warehouse | BI and analytics queries |

---

## Common Anti-Patterns

See [references/anti_patterns.md](references/anti_patterns.md) for detailed guidance on avoiding common mistakes.

### Quick Reference

❌ **Don't:**
- Perform heavy transformations in Bronze
- Skip Silver layer validation
- Create too many Gold tables without clear ownership
- Use static partitioning when liquid clustering is better
- Ignore data quality monitoring
- Mix raw and transformed data in the same layer

✅ **Do:**
- Keep Bronze as close to source as possible
- Apply all validation in Silver
- Design Gold tables with specific use cases
- Use liquid clustering for query optimization
- Monitor data quality at every layer
- Maintain clear layer boundaries
- **Agile Logic Updates**: Confidentialize logic changes to Silver/Gold; replay from Bronze if business rules change without re-ingesting from source.

---

## Decision Framework

### When to Use Each Layer

### When to Use Each Layer

**Use Bronze when:**
- Ingesting raw data (Auto Loader, Lakeflow Connect)
- Virtualizing external data (Lakehouse Federation)
- Need to preserve complete history/lineage
- Source data format is unpredictable

**Use Silver when:**
- Need to clean and validate data
- Applying business rules and transformations
- Deduplicating records
- Preparing data for multiple downstream use cases

**Use Gold when:**
- Creating aggregated metrics for BI
- Building dimensional models for analytics
- Optimizing for specific query patterns
- Applying business-level security

### Streaming vs Batch by Layer

| Layer | Recommended Mode | Rationale |
|-------|------------------|-----------|
| **Bronze** | Streaming (Auto Loader) | Incremental ingestion, low latency |
| **Silver** | Streaming from Bronze | Incremental processing, real-time validation |
| **Gold** | Materialized views (batch) | Aggregations benefit from batch processing |

**Exception**: Use batch for Silver dimensional tables that need full refresh.

The Medallion architecture is **compatible with data mesh** principles. Bronze and Silver tables can be joined in a "one-to-many" fashion, where a single upstream table generates multiple downstream tables.

### Architecture Flexibility

The Medallion architecture is a **logical framework**, not a rigid set of rules. Adapt it to your needs:

-   **Bronze + Gold**: For simple applications where raw data is clean enough to aggregate directly.
-   **Silver-Only**: For data cleaning pipelines that don't need historical raw data (not recommended for enterprise, but fine for throwaway dev).
-   **Multi-Hop Silver**: Splitting Silver into "Silver Raw" (deduplicated) and "Silver Enriched" (joined with master data) for complex domains.

**Key Principle**: Don't force a layer if it adds no value. However, skipping Bronze often leads to data loss (no replay), and skipping Silver leads to complex/brittle Gold logic.

## Complete Example

See [scripts/end_to_end_pipeline.py](scripts/end_to_end_pipeline.py) for a complete Python example demonstrating:
- Bronze → Silver → Gold pipeline
- Data quality expectations
- Error handling and logging
- Performance optimization techniques

---

## Additional Resources

For detailed documentation, guiding principles, and personas, see [references/lakehouse_support.md](references/lakehouse_support.md) and [references/REFERENCES.md](references/REFERENCES.md).

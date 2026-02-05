# Data Design Standards

## 1. Medallion Architecture
The architecture consists of 4 layers, ensuring traceability and data quality.

| Layer | Source | Storage | Purpose |
|-------|--------|---------|---------|
| **RAW** | Ext (MySQL, API) | S3 (Volumes) | Landing zone. Data AS-IS. Encrypted PII. |
| **BRONZE** | RAW | Delta Table | Exact copy of Raw. Control fields added. Encrypted PII. |
| **SILVER** | BRONZE | Delta Table | Cleaned, deduplicated, enriched. Business rules applied. Masked PII. |
| **GOLD** | SILVER | Delta Table | Aggregated, business-ready. Source for BI/ML. |

## 2. Mandatory Control Fields
All tables must include these fields at the **end** of the schema.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `dt_ingestion` | TIMESTAMP | When data entered current layer. | `2024-01-15 10:30:00` |
| `dt_processing` | TIMESTAMP | When processing occurred (Silver+). | `2024-01-15 11:00:00` |
| `source_processing` | STRING | Previous layer name. | `RAW`, `BRONZE` |
| `source_table` | STRING | Name of source object. | `tb_customers` |
| `nm_file_origin` | STRING | Input file name (from metadata). | `part-000...json` |

### Rules per Layer
- **BRONZE**: `dt_ingestion`, `source_processing='RAW'`, `source_table`, `nm_file_origin`.
- **SILVER**: Inherits `dt_ingestion`, `nm_file_origin`. Adds `dt_processing`. Updates `source_processing='BRONZE'` and `source_table`.

## 3. Naming Conventions
- **Tables**: `tb_{source_schema}_{table_name}`
  - Example: `tb_jobs_customers`
- **Views**: `vw_{name}`
- **Address**: Always use 3-level: `catalog.schema.table`
  - Example: `ecred_prd.bronze.tb_jobs_customers`

## 4. Partitioning Rules
- **CLUSTER BY**: **Mandatory** for new tables. Use high-cardinality business keys (e.g., `id_customer`, `dt_event`).
- **PARTITIONED BY**: **Forbidden**. Replaced by Liquid Clustering.
- **Control Fields**: **NEVER** partition or cluster by control fields (`dt_ingestion`).

## 5. Golden Rules
1. ✅ Add control fields at the end.
2. ✅ Keep lineage (`source_processing`, `source_table`).
3. ✅ Use `CLUSTER BY` with business keys.
4. ❌ Do NOT use `OPTIMIZE`/`ZORDER` manually (let Liquid/Predictive do it).
5. ❌ Do NOT use `PARTITIONED BY`.

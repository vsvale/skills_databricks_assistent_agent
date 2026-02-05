# Catalog & Schema Standards

## Overview
- **Catalog Strategy**: One catalog per Product or Team (e.g., `premium_prd`, `models_dev`).
- **Naming Convention**: `<product/team>_<environment>` (no abbreviations preferred).
- **Storage**: `s3://serasaexperian-ecs-datalakehouse-<env>-<product>`.
- **Access**: Access is managed via `USE CATALOG` and `USE SCHEMA`.

## Standard Schemas
| Schema | Purpose | Access |
|--------|---------|--------|
| **raw** | Ingestion landing zone (Volumes). Encrypted PII. | Service Principal only. |
| **bronze** | Raw Delta tables (encrypted). | Service Principal only. |
| **silver** | Refined/Enriched data. Internal usage (masked PII). | All Users (Read). |
| **gold** | Aggregated/Business data. Views/Materialized Views. | All Users (Read). |
| **control** | Job metadata, parameters, control tables. | Service Principal only. |
| **delivery** | Exports for external systems (often PII decrypted). | Service Principal only. |
| **sandbox** | Prototyping/Ad-hoc. Managed by team. | Team members (Read/Write). |
| **sensitive** | Highly restricted PII. | Request Access required. |
| **temp** | Temporary processing tables. | Team managed (auto-delete). |
| **vector** | Vector Search endpoints/indexes. | Service Principal only. |

## Migration Notes
- **Frozen Hive**: Hive Metastore databases are frozen (DENY MODIFY/CREATE) during migration.
- **3-Level Namespace**: Use `catalog.schema.table`.
- **Code Update**:
  - *Before*: `db_analytics.table`
  - *After*: `analytics_prd.gold.table`
  - *SQL*: `USE CATALOG x; USE SCHEMA y;` or fully qualified names.

# Legacy Manual CDC Patterns

This document contains manual implementation patterns for Change Data Capture (CDC) using standard Spark SQL (MERGE, Window Functions).
For modern pipelines, use Delta Live Tables (DLT) `APPLY CHANGES INTO` (Auto CDC).

## Prerequisites
- Delta Lake tables
- Natural key or surrogate key defined
- Audit columns: `updated_at` and `created_at` (TIMESTAMP)
- Record hash column (`record_hash`) for change detection

## Bronze Layer
- Raw data
- May contain duplicates by ID
- Complete history of changes
- Append-only
- Clustering by `id`, `updated_at`
- Generates `record_hash`

## Silver Layer
- Deduplicated data (1 record per ID)
- Applies operations: I (Insert), U (Update), D (Delete)
- Deduplication via `ROW_NUMBER()` with `QUALIFY = 1`
- Incremental watermark
- Change detection via `record_hash`

## MERGE (UPSERT) Pattern
```sql
MERGE INTO target
USING source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

## Deduplication with QUALIFY
```sql
SELECT * FROM table
QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC) = 1
```

## Incremental Watermark
Process only new or changed records since the last load:
```sql
WHERE updated_at > last_watermark
```

## Record Hash
Detects content changes:
```sql
sha2(concat_ws('||', cast(id as string), value::string, name), 256)
```

# Liquid Clustering

## Overview
Replaces `partitionBy` and `ZORDER`. Databricks manages data layout.
- **Requirement**: DBR 15.2+ (Automatic in 15.4+).
- **Recommendation**: Enable for all new Delta tables.

## Usage
### Creating Table
```sql
CREATE TABLE catalog.schema.table
CLUSTER BY (column1)
AS SELECT * FROM ...
```

### Writing (PySpark)
```python
df.write.clusterBy("column1").saveAsTable("catalog.schema.table")
```

### Enabling on Existing Table
```sql
ALTER TABLE catalog.schema.table CLUSTER BY AUTO;
-- Trigger optimization
OPTIMIZE catalog.schema.table FULL;
```

## Best Practices
- **Key Selection**: Choose 1-4 columns used frequently in filters/joins.
- **Cardinality**: Works well with high cardinality columns (unlike partitioning).
- **Auto Mode**: `CLUSTER BY AUTO` allows Databricks to choose keys based on query history.

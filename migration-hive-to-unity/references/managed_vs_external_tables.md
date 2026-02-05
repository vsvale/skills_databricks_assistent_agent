# Managed vs External Tables

## Policy: Prefer Managed Tables
Databricks recommends **Managed Tables** as the default for Unity Catalog.
- **Benefits**: Predictive Optimization (Auto OPTIMIZE/VACUUM), simplified permission management, better performance.
- **Behavior**: Dropping the table deletes data and metadata (recoverable via UNDROP).

## Migration Patterns

### Creating a Managed Table
**Do NOT** specify a `LOCATION` or `path` option.

**SQL Pattern**:
```sql
-- Before (External)
CREATE TABLE demo_prd.sandbox.table
LOCATION 's3://bucket/path'

-- After (Managed)
CREATE TABLE demo_prd.sandbox.table
```

**PySpark Pattern**:
```python
# Before
df.write.format('delta').option('path', '/dbfs/...').saveAsTable('table')

# After
df.write.saveAsTable('catalog.schema.table')
```

### Deep Clone & CTAS
- Tables created via `DEEP CLONE` or `CTAS` are automatically **Managed** if no location is specified.
- Use CTAS to migrate DBFS root tables.

### Exceptions (External Tables)
- Only use External Tables if data must be accessed by tools *outside* Databricks (rare).
- Requires `MANAGE` permission to drop.

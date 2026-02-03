---
name: unity-catalog
description: Manage and work with Unity Catalog in Databricks. Unity Catalog is the unified governance solution for data and AI assets. Use this skill when creating catalogs, schemas, tables, managing permissions, working with external locations, storage credentials, data sharing, or implementing Unity Catalog best practices.
---

# Unity Catalog Management

Unity Catalog provides centralized governance for data and AI assets across Databricks workspaces. This skill helps you manage catalogs, schemas, tables, permissions, and other Unity Catalog resources.

## Common Operations

### Creating Catalogs

Catalogs are the top-level container in Unity Catalog's three-level namespace: `catalog.schema.table`.

```sql
-- Create a catalog
CREATE CATALOG IF NOT EXISTS my_catalog
COMMENT 'Production data catalog';

-- Create a catalog with managed storage location
CREATE CATALOG IF NOT EXISTS my_catalog
LOCATION 's3://my-bucket/catalog/'
COMMENT 'Catalog with managed storage';
```

### Creating Schemas

Schemas organize tables within a catalog.

```sql
-- Create a schema in a catalog
CREATE SCHEMA IF NOT EXISTS my_catalog.my_schema
COMMENT 'Schema for analytics tables';

-- Create a schema with managed storage location
CREATE SCHEMA IF NOT EXISTS my_catalog.my_schema
LOCATION 's3://my-bucket/schema/'
COMMENT 'Schema with managed storage';
```

### Creating Tables

```sql
-- Create a managed table
CREATE TABLE IF NOT EXISTS my_catalog.my_schema.my_table (
  id INT,
  name STRING,
  created_at TIMESTAMP
)
CLUSTER BY AUTO
COMMENT 'Managed table example';

Tables can be managed (Unity Catalog manages the data) or external (data stored externally).
Databricks recommends using Unity Catalog managed tables with default settings for all new tables.
Databricks recommends using clustering for table layout.
Databricks recommends using predictive optimization to automatically run OPTIMIZE and VACUUM for tables.
Auto compaction and optimized writes are always enabled for MERGE, UPDATE, and DELETE operations
Background auto compaction is available for Unity Catalog managed tables, so remove the Spark config `spark.databricks.delta.autoCompact.enabled` from computes and tables `ALTER TABLE <table_name> UNSET TBLPROPERTIES (delta.autoOptimize.autoCompact)`
To apply a TBLPROPERTIE to all Unity Catalog tables run scripts/apply_tbproperties_to_all_tables.py. To unset a TBLPROPERTIE to all Unity Catalog tables run scripts/remove_tblproperties_to_all_tables.py

-- Create an external table
CREATE TABLE IF NOT EXISTS my_catalog.my_schema.external_table
LOCATION 's3://my-bucket/data/'
COMMENT 'External table example';

-- Create a table from existing data
CREATE TABLE IF NOT EXISTS my_catalog.my_schema.sales_data
AS SELECT * FROM legacy_database.sales;
```

### Managing Permissions

Unity Catalog uses a fine-grained permission model. Common privileges include:

- **Catalog level**: `USE CATALOG`, `CREATE SCHEMA`, `ALL PRIVILEGES`
- **Schema level**: `USE SCHEMA`, `CREATE TABLE`, `CREATE FUNCTION`, `ALL PRIVILEGES`
- **Table level**: `SELECT`, `MODIFY`, `ALL PRIVILEGES`

```sql
-- Grant catalog privileges
GRANT USE CATALOG ON CATALOG my_catalog TO `analysts@company.com`;

-- Grant schema privileges
GRANT USE SCHEMA, CREATE TABLE ON SCHEMA my_catalog.my_schema TO `data-engineers@company.com`;

-- Grant table privileges
GRANT SELECT ON TABLE my_catalog.my_schema.my_table TO `analysts@company.com`;

-- Grant all privileges
GRANT ALL PRIVILEGES ON SCHEMA my_catalog.my_schema TO `admins@company.com`;
```

### External Locations and Storage Credentials

External locations allow Unity Catalog to access data in external storage systems.

```sql
-- Create a storage credential (requires admin privileges)
CREATE STORAGE CREDENTIAL IF NOT EXISTS my_credential
WITH AWS IAM ROLE 'arn:aws:iam::123456789:role/databricks-role';

-- Create an external location
CREATE EXTERNAL LOCATION IF NOT EXISTS my_location
URL 's3://my-bucket/data/'
WITH (STORAGE CREDENTIAL my_credential);

-- Grant access to external location
GRANT READ FILES ON EXTERNAL LOCATION my_location TO `analysts@company.com`;
```

### Data Sharing

Unity Catalog supports Delta Sharing for secure data sharing.

```sql
-- Create a share
CREATE SHARE IF NOT EXISTS my_share
COMMENT 'Share for external partners';

-- Add table to share
ALTER SHARE my_share ADD TABLE my_catalog.my_schema.my_table;

-- Grant access to share
GRANT SELECT ON SHARE my_share TO `partner@external.com`;
```

## Best Practices

1. **Naming Conventions**
   - Use lowercase with underscores: `my_catalog`, `analytics_schema`
   - Be descriptive and consistent
   - Avoid special characters and spaces

2. **Organization**
   - Group related schemas within catalogs
   - Use catalogs to separate environments (dev, staging, prod)
   - Organize by domain or team ownership

3. **Permissions**
   - Follow principle of least privilege
   - Grant at the appropriate level (catalog, schema, or table)
   - Use groups for easier permission management
   - Document permission requirements

4. **Storage**
   - Use managed storage for new tables when possible
   - Use external locations for existing data in cloud storage
   - Consider data retention and lifecycle policies

5. **Migration**
   - Migrate from Hive metastore to Unity Catalog gradually
   - Test permissions and access patterns
   - Update applications and queries to use three-level namespace

## Common Queries

```sql
-- List all catalogs
SHOW CATALOGS;

-- List schemas in a catalog
SHOW SCHEMAS IN CATALOG my_catalog;

-- List tables in a schema
SHOW TABLES IN my_catalog.my_schema;

-- Describe a table
DESCRIBE EXTENDED my_catalog.my_schema.my_table;

-- Show grants on a catalog
SHOW GRANTS ON CATALOG my_catalog;

-- Show grants on a schema
SHOW GRANTS ON SCHEMA my_catalog.my_schema;

-- Show grants on a table
SHOW GRANTS ON TABLE my_catalog.my_schema.my_table;

-- List external locations
SHOW EXTERNAL LOCATIONS;

-- List storage credentials
SHOW STORAGE CREDENTIALS;
```

## Troubleshooting

- **Permission denied errors**: Check grants at catalog, schema, and table levels
- **Table not found**: Verify three-level namespace format: `catalog.schema.table`
- **External location access**: Ensure storage credentials are properly configured
- **Migration issues**: Check compatibility between Hive metastore and Unity Catalog

For more details, consult the references/REFERENCES.md.

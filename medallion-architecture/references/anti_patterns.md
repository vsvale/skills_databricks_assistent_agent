# Common Anti-Patterns in Medallion Architecture

This document outlines common mistakes when implementing Medallion architecture and how to avoid them.

---

## Bronze Layer Anti-Patterns

### ❌ Anti-Pattern 1: Heavy Transformations in Bronze

**Problem:**
Applying complex business logic, data cleaning, or aggregations in the Bronze layer.

**Why it's bad:**
- Violates the principle of preserving raw data
- Makes it impossible to replay pipelines with different logic
- Loses historical context and audit trail
- Complicates debugging and troubleshooting

**Example:**
```sql
-- ❌ BAD: Complex transformations in Bronze
CREATE STREAMING TABLE bronze.customer_data AS
SELECT 
  customer_id,
  UPPER(TRIM(customer_name)) as customer_name,  -- Transformation
  CASE 
    WHEN age < 18 THEN 'Minor'
    ELSE 'Adult'
  END as age_group,  -- Business logic
  total_purchases / 12 as avg_monthly_purchases  -- Calculation
FROM read_files('/volumes/raw/customers');
```

**✅ Solution:**
Keep Bronze minimal, move transformations to Silver:
```sql
-- ✅ GOOD: Minimal Bronze
CREATE STREAMING TABLE bronze.raw_customers AS
SELECT 
  *,
  current_timestamp() as _ingestion_timestamp,
  _metadata.file_path as _source_file
FROM read_files('/volumes/raw/customers');

-- ✅ GOOD: Transformations in Silver
CREATE STREAMING TABLE silver.clean_customers AS
SELECT 
  customer_id,
  UPPER(TRIM(customer_name)) as customer_name,
  CASE WHEN age < 18 THEN 'Minor' ELSE 'Adult' END as age_group
FROM STREAM(bronze.raw_customers);
```

---

### ❌ Anti-Pattern 2: Filtering or Dropping Records in Bronze

**Problem:**
Filtering out "bad" records during Bronze ingestion.

**Why it's bad:**
- Loses data that might be needed later
- No audit trail of rejected records
- Can't analyze data quality issues at the source
- Violates compliance requirements

**Example:**
```sql
-- ❌ BAD: Filtering in Bronze
CREATE STREAMING TABLE bronze.transactions AS
SELECT * FROM read_files('/volumes/raw/transactions')
WHERE transaction_id IS NOT NULL  -- Filtering
  AND amount > 0;  -- Filtering
```

**✅ Solution:**
Ingest everything in Bronze, filter in Silver:
```sql
-- ✅ GOOD: No filtering in Bronze
CREATE STREAMING TABLE bronze.raw_transactions AS
SELECT 
  *,
  current_timestamp() as _ingestion_timestamp
FROM read_files('/volumes/raw/transactions');

-- ✅ GOOD: Filter in Silver with expectations
CREATE STREAMING TABLE silver.valid_transactions (
  CONSTRAINT valid_id EXPECT (transaction_id IS NOT NULL) ON VIOLATION DROP,
  CONSTRAINT valid_amount EXPECT (amount > 0) ON VIOLATION DROP
) AS SELECT * FROM STREAM(bronze.raw_transactions);
```

---

### ❌ Anti-Pattern 3: Not Adding Metadata Columns

**Problem:**
Ingesting data without adding ingestion timestamps, source file paths, or other metadata.

**Why it's bad:**
- Difficult to debug data issues
- No lineage tracking
- Can't determine when data arrived
- Complicates incremental processing

**Example:**
```sql
-- ❌ BAD: No metadata
CREATE STREAMING TABLE bronze.events AS
SELECT * FROM read_files('/volumes/raw/events');
```

**✅ Solution:**
Always add metadata columns:
```sql
-- ✅ GOOD: With metadata
CREATE STREAMING TABLE bronze.raw_events AS
SELECT 
  *,
  current_timestamp() as _ingestion_timestamp,
  _metadata.file_path as _source_file,
  _metadata.file_modification_time as _source_modified_time
FROM read_files('/volumes/raw/events');
```

---

## Silver Layer Anti-Patterns

### ❌ Anti-Pattern 4: Direct Ingestion to Silver

**Problem:**
Reading directly from source files into Silver, bypassing Bronze.

**Why it's bad:**
- No raw data backup for replay
- Schema changes can break Silver pipelines
- Corrupt records can fail entire pipeline
- Loses audit trail

**Example:**
```sql
-- ❌ BAD: Direct ingestion to Silver
CREATE STREAMING TABLE silver.clean_orders AS
SELECT 
  order_id,
  CAST(order_date AS DATE) as order_date,
  customer_id
FROM read_files('/volumes/raw/orders')  -- Direct from source
WHERE order_id IS NOT NULL;
```

**✅ Solution:**
Always read from Bronze:
```sql
-- ✅ GOOD: Read from Bronze
CREATE STREAMING TABLE silver.clean_orders AS
SELECT 
  order_id,
  CAST(order_date AS DATE) as order_date,
  customer_id
FROM STREAM(bronze.raw_orders)  -- From Bronze
WHERE order_id IS NOT NULL;
```

---

### ❌ Anti-Pattern 5: Skipping Data Quality Checks

**Problem:**
Not implementing expectations or validation rules in Silver.

**Why it's bad:**
- Bad data propagates to Gold layer
- Business decisions based on incorrect data
- Difficult to identify data quality issues
- No metrics on data quality

**Example:**
```sql
-- ❌ BAD: No validation
CREATE STREAMING TABLE silver.transactions AS
SELECT 
  transaction_id,
  CAST(amount AS DECIMAL(10,2)) as amount,
  customer_id
FROM STREAM(bronze.raw_transactions);
```

**✅ Solution:**
Implement comprehensive expectations:
```sql
-- ✅ GOOD: With expectations
CREATE STREAMING TABLE silver.validated_transactions (
  CONSTRAINT valid_id EXPECT (transaction_id IS NOT NULL) ON VIOLATION FAIL,
  CONSTRAINT valid_amount EXPECT (amount > 0) ON VIOLATION DROP,
  CONSTRAINT valid_customer EXPECT (customer_id IS NOT NULL) ON VIOLATION DROP
) AS
SELECT 
  transaction_id,
  CAST(amount AS DECIMAL(10,2)) as amount,
  customer_id
FROM STREAM(bronze.raw_transactions);
```

---

### ❌ Anti-Pattern 6: Not Handling Duplicates

**Problem:**
Allowing duplicate records to exist in Silver tables.

**Why it's bad:**
- Inflates metrics and aggregations
- Causes incorrect business insights
- Wastes storage and compute
- Complicates downstream processing

**Example:**
```sql
-- ❌ BAD: No deduplication
CREATE STREAMING TABLE silver.customers AS
SELECT * FROM STREAM(bronze.raw_customers);
-- May contain duplicates
```

**✅ Solution:**
Implement deduplication strategy:
```sql
-- ✅ GOOD: With deduplication
CREATE MATERIALIZED VIEW silver.unique_customers AS
SELECT * FROM (
  SELECT 
    *,
    ROW_NUMBER() OVER (
      PARTITION BY customer_id 
      ORDER BY _ingestion_timestamp DESC
    ) as rn
  FROM bronze.raw_customers
)
WHERE rn = 1;
```

---

### ❌ Anti-Pattern 7: Aggregating in Silver

**Problem:**
Creating aggregated or summarized data in Silver layer.

**Why it's bad:**
- Loses row-level detail needed for flexible analysis
- Limits downstream use cases
- Violates Silver's purpose as detailed, validated data
- Forces recreation of Silver tables for new aggregations

**Example:**
```sql
-- ❌ BAD: Aggregation in Silver
CREATE MATERIALIZED VIEW silver.daily_sales AS
SELECT 
  DATE(transaction_date) as date,
  SUM(amount) as total_sales  -- Aggregation
FROM bronze.raw_transactions
GROUP BY DATE(transaction_date);
```

**✅ Solution:**
Keep Silver at row-level, aggregate in Gold:
```sql
-- ✅ GOOD: Row-level Silver
CREATE STREAMING TABLE silver.validated_transactions AS
SELECT 
  transaction_id,
  transaction_date,
  amount
FROM STREAM(bronze.raw_transactions)
WHERE amount > 0;

-- ✅ GOOD: Aggregation in Gold
CREATE MATERIALIZED VIEW gold.daily_sales AS
SELECT 
  DATE(transaction_date) as date,
  SUM(amount) as total_sales
FROM silver.validated_transactions
GROUP BY DATE(transaction_date);
```

---

## Gold Layer Anti-Patterns

### ❌ Anti-Pattern 8: Creating Too Many Gold Tables

**Problem:**
Creating a separate Gold table for every possible query or report.

**Why it's bad:**
- Table sprawl and maintenance burden
- Unclear ownership and purpose
- Redundant data storage
- Difficult to govern and secure

**Example:**
```sql
-- ❌ BAD: Too many specific tables
CREATE MATERIALIZED VIEW gold.sales_by_day_region_product ...
CREATE MATERIALIZED VIEW gold.sales_by_week_region_product ...
CREATE MATERIALIZED VIEW gold.sales_by_month_region_product ...
CREATE MATERIALIZED VIEW gold.sales_by_day_category ...
-- 50+ more tables...
```

**✅ Solution:**
Create flexible dimensional models and let BI tools aggregate:
```sql
-- ✅ GOOD: Dimensional model
CREATE MATERIALIZED VIEW gold.fact_sales AS
SELECT 
  transaction_id,
  date_key,
  customer_key,
  product_key,
  amount
FROM silver.validated_transactions;

CREATE MATERIALIZED VIEW gold.dim_date AS ...
CREATE MATERIALIZED VIEW gold.dim_products AS ...

-- Let BI tools query flexibly
```

---

### ❌ Anti-Pattern 9: Using Static Partitioning Instead of Liquid Clustering

**Problem:**
Using `PARTITIONED BY` instead of `CLUSTER BY` for Gold tables.

**Why it's bad:**
- Static partitions can become skewed
- Requires manual partition management
- Less flexible than liquid clustering
- Can lead to small file problems

**Example:**
```sql
-- ❌ BAD: Static partitioning
CREATE MATERIALIZED VIEW gold.sales
PARTITIONED BY (year, month)  -- Static
AS SELECT * FROM silver.transactions;
```

**✅ Solution:**
Use liquid clustering:
```sql
-- ✅ GOOD: Liquid clustering
CREATE MATERIALIZED VIEW gold.sales
CLUSTER BY (transaction_date, customer_id)  -- Flexible
AS SELECT * FROM silver.transactions;

-- Or let Databricks optimize
CREATE MATERIALIZED VIEW gold.sales
CLUSTER BY AUTO
AS SELECT * FROM silver.transactions;
```

---

### ❌ Anti-Pattern 10: No Clear Ownership or Documentation

**Problem:**
Creating Gold tables without documenting purpose, owner, or refresh schedule.

**Why it's bad:**
- Unclear who maintains the table
- Unknown business purpose
- Difficult to deprecate unused tables
- No SLA expectations

**Example:**
```sql
-- ❌ BAD: No documentation
CREATE MATERIALIZED VIEW gold.table_123 AS
SELECT * FROM silver.some_data;
```

**✅ Solution:**
Document ownership and purpose:
```sql
-- ✅ GOOD: Well-documented
CREATE MATERIALIZED VIEW gold.customer_lifetime_value
COMMENT 'Customer lifetime value metrics for marketing team. 
         Owner: marketing_analytics@company.com
         Refresh: Daily at 6 AM UTC
         SLA: Data must be < 24 hours old'
AS SELECT 
  customer_id,
  SUM(amount) as lifetime_value,
  COUNT(*) as purchase_count
FROM silver.validated_transactions
GROUP BY customer_id;

-- Add table tags for governance
ALTER TABLE gold.customer_lifetime_value 
SET TAGS ('owner' = 'marketing_analytics', 'refresh' = 'daily');
```

---

## Cross-Layer Anti-Patterns

### ❌ Anti-Pattern 11: Mixing Layers

**Problem:**
Storing raw and transformed data in the same schema or table.

**Why it's bad:**
- Unclear data quality and lineage
- Violates separation of concerns
- Difficult to apply appropriate governance
- Confuses data consumers

**Example:**
```sql
-- ❌ BAD: Mixed layers
CREATE SCHEMA data;
CREATE TABLE data.customers_raw ...
CREATE TABLE data.customers_clean ...
CREATE TABLE data.customers_aggregated ...
```

**✅ Solution:**
Use separate schemas for each layer:
```sql
-- ✅ GOOD: Clear separation
CREATE SCHEMA bronze;
CREATE SCHEMA silver;
CREATE SCHEMA gold;

CREATE TABLE bronze.raw_customers ...
CREATE TABLE silver.clean_customers ...
CREATE TABLE gold.customer_360 ...
```

---

### ❌ Anti-Pattern 12: Ignoring Data Quality Monitoring

**Problem:**
Not monitoring data quality metrics or expectation failures.

**Why it's bad:**
- Data quality issues go unnoticed
- No alerting on pipeline failures
- Can't track data quality trends
- Reactive instead of proactive

**Example:**
```sql
-- ❌ BAD: Set expectations but never monitor
CREATE STREAMING TABLE silver.data (
  CONSTRAINT check1 EXPECT (...) ON VIOLATION DROP
) AS ...
-- No monitoring of dropped records
```

**✅ Solution:**
Implement monitoring and alerting:
```sql
-- ✅ GOOD: Monitor expectations
CREATE STREAMING TABLE silver.validated_data (
  CONSTRAINT valid_amount EXPECT (amount > 0) ON VIOLATION DROP
) AS ...

-- Monitor dropped records
SELECT 
  expectation_name,
  SUM(failed_records) as total_dropped,
  SUM(failed_records) * 100.0 / SUM(passed_records + failed_records) as drop_rate
FROM event_log
WHERE dataset_name = 'silver.validated_data'
  AND timestamp >= CURRENT_TIMESTAMP() - INTERVAL 1 DAY
GROUP BY expectation_name;

-- Set up alerts for high drop rates
```

---

### ❌ Anti-Pattern 13: Not Using Unity Catalog

**Problem:**
Using direct cloud storage paths instead of Unity Catalog Volumes.

**Why it's bad:**
- No centralized governance
- Difficult to manage permissions
- No data lineage tracking
- Missing audit capabilities

**Example:**
```sql
-- ❌ BAD: Direct cloud storage
CREATE STREAMING TABLE bronze.data AS
SELECT * FROM read_files('s3://my-bucket/raw-data/');
```

**✅ Solution:**
Use Unity Catalog Volumes:
```sql
-- ✅ GOOD: Unity Catalog Volumes
CREATE STREAMING TABLE bronze.data AS
SELECT * FROM read_files('/Volumes/main/raw/customer_data/');
```

---

### ❌ Anti-Pattern 14: Ignoring Performance Optimization

**Problem:**
Not optimizing tables with OPTIMIZE, VACUUM, or proper clustering.

**Why it's bad:**
- Slow query performance
- Wasted storage on small files
- Higher compute costs
- Poor user experience

**Example:**
```sql
-- ❌ BAD: Never optimize
CREATE TABLE gold.sales AS ...
-- Never run OPTIMIZE or VACUUM
```

**✅ Solution:**
Regular optimization and maintenance:
```sql
-- ✅ GOOD: Enable auto-optimize
CREATE TABLE gold.sales
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
)
AS ...

-- Manual optimization when needed
OPTIMIZE gold.sales;

-- Regular vacuum (after retention period)
VACUUM gold.sales RETAIN 168 HOURS;
```

---

## Summary: Key Principles

### Bronze Layer
✅ **Do:**
- Preserve raw data exactly as received
- Add metadata columns
- Use Delta Lake format
- Enable append-only mode

❌ **Don't:**
- Transform or clean data
- Filter or drop records
- Apply business logic
- Skip metadata

### Silver Layer
✅ **Do:**
- Always read from Bronze
- Implement data quality checks
- Deduplicate records
- Normalize data types
- Keep row-level detail

❌ **Don't:**
- Ingest directly from sources
- Skip validation
- Allow duplicates
- Aggregate data
- Mix with Bronze

### Gold Layer
✅ **Do:**
- Use dimensional modeling
- Pre-aggregate for BI
- Use liquid clustering
- Document ownership
- Implement security

❌ **Don't:**
- Create too many tables
- Use static partitioning
- Skip documentation
- Ignore optimization
- Mix with Silver

### All Layers
✅ **Do:**
- Use Unity Catalog
- Monitor data quality
- Optimize regularly
- Maintain clear boundaries
- Document everything

❌ **Don't:**
- Mix layers
- Ignore monitoring
- Skip governance
- Forget optimization
- Use direct cloud paths

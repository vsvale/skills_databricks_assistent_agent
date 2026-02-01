-- ============================================================================
-- Silver Layer Cleaning and Validation Examples
-- ============================================================================
-- Purpose: Demonstrate best practices for data cleaning and validation
-- Key Principles:
--   - Always read from Bronze or Silver (never direct ingestion)
--   - Apply data quality checks with expectations
--   - Deduplicate records based on business keys
--   - Normalize data types and formats
--   - Use streaming reads for append-only sources
--   - Abstract Bronze with views to simplify Silver logic
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Example 1: Basic Cleaning with Type Casting
-- ----------------------------------------------------------------------------
-- Transform Bronze data with proper type casting and validation

CREATE STREAMING TABLE silver.clean_customer_events (
  -- Properly typed columns
  event_id STRING NOT NULL,
  event_type STRING,
  event_timestamp TIMESTAMP,
  customer_id STRING NOT NULL,
  event_data STRUCT<...>,  -- Parsed JSON structure
  -- Metadata from Bronze
  _ingestion_timestamp TIMESTAMP,
  _processing_timestamp TIMESTAMP
)
COMMENT 'Cleaned and validated customer events'
AS SELECT 
  event_id,
  event_type,
  CAST(event_timestamp AS TIMESTAMP) as event_timestamp,
  customer_id,
  from_json(event_data, 'struct<...>') as event_data,
  _ingestion_timestamp,
  current_timestamp() as _processing_timestamp
FROM STREAM(bronze.raw_customer_events)
WHERE event_id IS NOT NULL
  AND customer_id IS NOT NULL
  AND event_timestamp IS NOT NULL;

-- ----------------------------------------------------------------------------
-- Example 1.1: Bronze Abstraction View
-- ----------------------------------------------------------------------------
-- Create a view on Bronze to parse raw JSON, keeping storage as-is
-- Downstream Silver queries can then 'SELECT * FROM bronze.v_raw_events'

CREATE VIEW bronze.v_raw_events AS
SELECT 
  *,
  from_json(raw_payload, 'struct<user_id:string, event:string, dt:string>') as parsed_payload
FROM bronze.raw_storage_table;

-- Silver then consumes the view instead of raw storage
CREATE STREAMING TABLE silver.events_from_view AS
SELECT 
  parsed_payload.user_id as customer_id,
  parsed_payload.event as event_type,
  CAST(parsed_payload.dt AS DATE) as event_date
FROM STREAM(bronze.v_raw_events);

-- ----------------------------------------------------------------------------
-- Example 2: Data Quality with Expectations
-- ----------------------------------------------------------------------------
-- Apply validation rules with different violation actions

CREATE STREAMING TABLE silver.validated_transactions (
  -- Constraints enforce data quality
  CONSTRAINT valid_transaction_id 
    EXPECT (transaction_id IS NOT NULL) 
    ON VIOLATION FAIL,
  
  CONSTRAINT valid_amount 
    EXPECT (total_amount > 0) 
    ON VIOLATION DROP,
  
  CONSTRAINT valid_date 
    EXPECT (transaction_date >= '2020-01-01') 
    ON VIOLATION DROP,
  
  CONSTRAINT valid_quantity 
    EXPECT (quantity > 0 AND quantity < 10000) 
    ON VIOLATION WARN
)
COMMENT 'Validated transactions with data quality checks'
AS SELECT 
  transaction_id,
  CAST(transaction_date AS DATE) as transaction_date,
  customer_id,
  product_id,
  CAST(quantity AS INT) as quantity,
  CAST(unit_price AS DECIMAL(10,2)) as unit_price,
  CAST(total_amount AS DECIMAL(10,2)) as total_amount,
  current_timestamp() as _processing_timestamp
FROM STREAM(bronze.raw_transactions);

-- ----------------------------------------------------------------------------
-- Example 3: Deduplication with Window Functions
-- ----------------------------------------------------------------------------
-- Remove duplicates based on business key, keeping most recent record

CREATE MATERIALIZED VIEW silver.unique_orders AS
SELECT 
  order_id,
  customer_id,
  order_date,
  order_status,
  total_amount,
  _ingestion_timestamp,
  _processing_timestamp
FROM (
  SELECT 
    *,
    ROW_NUMBER() OVER (
      PARTITION BY order_id 
      ORDER BY _ingestion_timestamp DESC
    ) as rn
  FROM bronze.raw_orders
)
WHERE rn = 1;

-- ----------------------------------------------------------------------------
-- Example 4: Deduplication for Streaming Tables
-- ----------------------------------------------------------------------------
-- Use APPLY CHANGES for CDC-style deduplication in streaming context

CREATE STREAMING TABLE silver.unique_customers;

APPLY CHANGES INTO silver.unique_customers
FROM STREAM(bronze.raw_customers)
KEYS (customer_id)
SEQUENCE BY _ingestion_timestamp
STORED AS SCD TYPE 1;  -- Keep only current version

-- ----------------------------------------------------------------------------
-- Example 5: Complex Validation and Normalization
-- ----------------------------------------------------------------------------
-- Apply business rules and normalize data formats

CREATE STREAMING TABLE silver.normalized_products (
  CONSTRAINT valid_product_id 
    EXPECT (product_id IS NOT NULL) 
    ON VIOLATION FAIL,
  
  CONSTRAINT valid_price 
    EXPECT (price >= 0) 
    ON VIOLATION DROP,
  
  CONSTRAINT valid_category 
    EXPECT (category IN ('Electronics', 'Clothing', 'Food', 'Other')) 
    ON VIOLATION WARN
)
COMMENT 'Normalized product catalog with business rules'
AS SELECT 
  product_id,
  UPPER(TRIM(product_name)) as product_name,  -- Normalize text
  CASE 
    WHEN category IN ('Electronics', 'Clothing', 'Food') THEN category
    ELSE 'Other'
  END as category,
  CAST(price AS DECIMAL(10,2)) as price,
  COALESCE(CAST(stock_quantity AS INT), 0) as stock_quantity,
  CASE 
    WHEN CAST(price AS DECIMAL(10,2)) < 10 THEN 'Low'
    WHEN CAST(price AS DECIMAL(10,2)) < 100 THEN 'Medium'
    ELSE 'High'
  END as price_tier,
  current_timestamp() as _processing_timestamp
FROM STREAM(bronze.raw_product_catalog);

-- ----------------------------------------------------------------------------
-- Example 6: Joining Streams with Dimension Tables
-- ----------------------------------------------------------------------------
-- Enrich streaming data with dimension lookups

CREATE STREAMING TABLE silver.enriched_transactions AS
SELECT 
  t.transaction_id,
  t.transaction_date,
  t.customer_id,
  c.customer_name,
  c.customer_segment,
  t.product_id,
  p.product_name,
  p.category,
  t.quantity,
  t.unit_price,
  t.total_amount
FROM STREAM(silver.validated_transactions) t
LEFT JOIN silver.unique_customers c
  ON t.customer_id = c.customer_id
LEFT JOIN silver.normalized_products p
  ON t.product_id = p.product_id;

-- Note: Dimension tables are snapshot at stream start time
-- For always-current joins, use materialized views instead

-- ----------------------------------------------------------------------------
-- Example 7: Handling Nested JSON Structures
-- ----------------------------------------------------------------------------
-- Parse and flatten nested JSON data

CREATE STREAMING TABLE silver.parsed_events (
  CONSTRAINT valid_event_id 
    EXPECT (event_id IS NOT NULL) 
    ON VIOLATION FAIL
)
COMMENT 'Parsed and flattened event data'
AS SELECT 
  event_id,
  event_type,
  event_timestamp,
  customer_id,
  -- Flatten nested JSON
  event_data.action as action,
  event_data.page_url as page_url,
  event_data.referrer as referrer,
  event_data.device.type as device_type,
  event_data.device.os as device_os,
  event_data.location.country as country,
  event_data.location.city as city,
  current_timestamp() as _processing_timestamp
FROM (
  SELECT 
    event_id,
    event_type,
    CAST(event_timestamp AS TIMESTAMP) as event_timestamp,
    customer_id,
    from_json(
      event_data, 
      'struct<action:string, page_url:string, referrer:string, 
              device:struct<type:string, os:string>, 
              location:struct<country:string, city:string>>'
    ) as event_data
  FROM STREAM(bronze.raw_clickstream)
);

-- ----------------------------------------------------------------------------
-- Example 8: Incremental Updates with Merge
-- ----------------------------------------------------------------------------
-- Use MERGE for SCD Type 1 updates (batch processing)

MERGE INTO silver.customer_master AS target
USING (
  SELECT 
    customer_id,
    customer_name,
    email,
    phone,
    address,
    customer_segment,
    _ingestion_timestamp
  FROM bronze.raw_customers
  WHERE _ingestion_timestamp >= (
    SELECT COALESCE(MAX(_last_updated), '1900-01-01') 
    FROM silver.customer_master
  )
) AS source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN UPDATE SET
  target.customer_name = source.customer_name,
  target.email = source.email,
  target.phone = source.phone,
  target.address = source.address,
  target.customer_segment = source.customer_segment,
  target._last_updated = source._ingestion_timestamp
WHEN NOT MATCHED THEN INSERT (
  customer_id, customer_name, email, phone, address, 
  customer_segment, _last_updated
)
VALUES (
  source.customer_id, source.customer_name, source.email, 
  source.phone, source.address, source.customer_segment, 
  source._ingestion_timestamp
);

-- ----------------------------------------------------------------------------
-- Example 9: Change Data Capture (CDC) - SCD Type 2
-- ----------------------------------------------------------------------------
-- Track historical changes with SCD Type 2

CREATE STREAMING TABLE silver.customer_history;

APPLY CHANGES INTO silver.customer_history
FROM STREAM(bronze.raw_customers)
KEYS (customer_id)
SEQUENCE BY _ingestion_timestamp
STORED AS SCD TYPE 2
TRACK HISTORY ON customer_name, email, customer_segment;

-- Result includes: customer_id, customer_name, email, customer_segment,
--                  __START_AT, __END_AT, __IS_CURRENT

-- ----------------------------------------------------------------------------
-- Example 10: Using VARIANT for Semi-Structured Data
-- ----------------------------------------------------------------------------
-- Use the VARIANT type (Databricks 15.3+) for schema-flexible ingestion in Silver

CREATE STREAMING TABLE silver.flexible_events AS
SELECT 
  event_id,
  event_type,
  PARSE_JSON(raw_event_payload) AS event_payload, -- Store as VARIANT
  _ingestion_timestamp
FROM STREAM(bronze.raw_events);

-- Querying VARIANT:
-- SELECT event_payload:device:os, COUNT(*) 
-- FROM silver.flexible_events 
-- GROUP BY 1;

-- ----------------------------------------------------------------------------
-- Example 11: Quarantining Invalid Records
-- ----------------------------------------------------------------------------
-- Capture records that fail expectations for further analysis

CREATE STREAMING TABLE silver.quarantine_orders AS
SELECT * 
FROM STREAM(bronze.raw_orders)
WHERE order_id IS NULL OR total_amount <= 0;

-- ----------------------------------------------------------------------------
-- Operational Commands for Silver Tables
-- ----------------------------------------------------------------------------

-- Monitor data quality metrics
SELECT 
  COUNT(*) as total_records,
  COUNT(CASE WHEN total_amount <= 0 THEN 1 END) as invalid_amounts,
  COUNT(CASE WHEN customer_id IS NULL THEN 1 END) as missing_customers,
  MIN(transaction_date) as earliest_date,
  MAX(transaction_date) as latest_date
FROM silver.validated_transactions;

-- Check for duplicates
SELECT 
  transaction_id,
  COUNT(*) as duplicate_count
FROM silver.validated_transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;

-- Analyze data quality over time
SELECT 
  DATE(_processing_timestamp) as processing_date,
  COUNT(*) as records_processed,
  COUNT(CASE WHEN total_amount > 0 THEN 1 END) as valid_records,
  COUNT(CASE WHEN total_amount <= 0 THEN 1 END) as invalid_records
FROM silver.validated_transactions
GROUP BY DATE(_processing_timestamp)
ORDER BY processing_date DESC;

-- Optimize Silver table
OPTIMIZE silver.validated_transactions;

-- Analyze table for query optimization
ANALYZE TABLE silver.validated_transactions COMPUTE STATISTICS;

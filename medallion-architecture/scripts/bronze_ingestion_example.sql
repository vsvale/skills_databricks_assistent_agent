-- ============================================================================
-- Bronze Layer Ingestion Examples
-- ============================================================================
-- Purpose: Demonstrate best practices for raw data ingestion into Bronze layer
-- Key Principles:
--   - Minimal transformations (metadata only)
--   - Preserve source data integrity
--   - Use Unity Catalog Volumes for governance
--   - Configure for append-only workloads
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Example 1: Basic JSON Ingestion with Auto Loader
-- ----------------------------------------------------------------------------
-- Ingest raw JSON events from Unity Catalog Volumes
-- Adds ingestion metadata for lineage and debugging

CREATE STREAMING TABLE bronze.raw_customer_events (
  -- Metadata columns (added during ingestion)
  _ingestion_timestamp TIMESTAMP,
  _source_file STRING,
  -- Source columns (inferred from JSON)
  event_id STRING,
  event_type STRING,
  event_timestamp STRING,  -- Keep as STRING in Bronze
  customer_id STRING,
  event_data STRING
)
TBLPROPERTIES (
  'delta.appendOnly' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
)
COMMENT 'Raw customer events from source systems'
AS SELECT 
  current_timestamp() as _ingestion_timestamp,
  _metadata.file_path as _source_file,
  *
FROM read_files(
  '/Volumes/main/raw/customer_events',
  format => 'json',
  inferSchema => true
);

-- ----------------------------------------------------------------------------
-- Example 2: CSV Ingestion with Schema Hints
-- ----------------------------------------------------------------------------
-- Ingest CSV files with explicit schema hints for critical columns

CREATE STREAMING TABLE bronze.raw_transactions (
  _ingestion_timestamp TIMESTAMP,
  _source_file STRING,
  _source_offset BIGINT,
  transaction_id STRING,
  transaction_date STRING,  -- Keep as STRING, parse in Silver
  customer_id STRING,
  product_id STRING,
  quantity STRING,
  unit_price STRING,
  total_amount STRING
)
TBLPROPERTIES (
  'delta.appendOnly' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true'
)
COMMENT 'Raw transaction data from CSV files'
AS SELECT 
  current_timestamp() as _ingestion_timestamp,
  _metadata.file_path as _source_file,
  _metadata.file_offset as _source_offset,
  *
FROM read_files(
  '/Volumes/main/raw/transactions',
  format => 'csv',
  header => true,
  inferSchema => true,
  schemaHints => 'transaction_id STRING, customer_id STRING'
);

-- ----------------------------------------------------------------------------
-- Example 3: Partitioned Bronze Table by Ingestion Date
-- ----------------------------------------------------------------------------
-- Partition by ingestion date for efficient historical queries and retention

CREATE STREAMING TABLE bronze.raw_orders (
  _ingestion_timestamp TIMESTAMP,
  _ingestion_date DATE,
  _source_file STRING,
  order_id STRING,
  order_data STRING  -- Raw JSON payload
)
PARTITIONED BY (_ingestion_date)
TBLPROPERTIES (
  'delta.appendOnly' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true'
)
COMMENT 'Raw orders partitioned by ingestion date'
AS SELECT 
  current_timestamp() as _ingestion_timestamp,
  CURRENT_DATE() as _ingestion_date,
  _metadata.file_path as _source_file,
  *
FROM read_files(
  '/Volumes/main/raw/orders',
  format => 'json'
);

-- ----------------------------------------------------------------------------
-- Example 4: Multi-Format Ingestion (Parquet, JSON, CSV)
-- ----------------------------------------------------------------------------
-- Auto Loader can handle multiple formats in the same directory

CREATE STREAMING TABLE bronze.raw_product_catalog (
  _ingestion_timestamp TIMESTAMP,
  _source_file STRING,
  _file_format STRING,
  product_id STRING,
  product_name STRING,
  category STRING,
  price STRING,
  attributes STRING
)
TBLPROPERTIES (
  'delta.appendOnly' = 'true'
)
COMMENT 'Raw product catalog from multiple file formats'
AS SELECT 
  current_timestamp() as _ingestion_timestamp,
  _metadata.file_path as _source_file,
  _metadata.file_format as _file_format,
  *
FROM read_files(
  '/Volumes/main/raw/products',
  format => 'json',  -- Primary format
  inferSchema => true
);

-- ----------------------------------------------------------------------------
-- Example 5: Incremental Ingestion with Checkpoint
-- ----------------------------------------------------------------------------
-- Process only new files since last checkpoint

CREATE STREAMING TABLE bronze.raw_sensor_data (
  _ingestion_timestamp TIMESTAMP,
  _source_file STRING,
  sensor_id STRING,
  reading_timestamp STRING,
  temperature STRING,
  humidity STRING,
  pressure STRING
)
TBLPROPERTIES (
  'delta.appendOnly' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true'
)
COMMENT 'Raw sensor readings with incremental processing'
AS SELECT 
  current_timestamp() as _ingestion_timestamp,
  _metadata.file_path as _source_file,
  *
FROM read_files(
  '/Volumes/main/raw/sensors',
  format => 'json',
  includeExistingFiles => true  -- Process existing files on first run
);

-- ----------------------------------------------------------------------------
-- Example 6: Bronze Table with Job Metadata
-- ----------------------------------------------------------------------------
-- Include job/pipeline metadata for operational monitoring

CREATE STREAMING TABLE bronze.raw_clickstream (
  _ingestion_timestamp TIMESTAMP,
  _ingestion_job_id STRING,
  _source_file STRING,
  session_id STRING,
  user_id STRING,
  page_url STRING,
  event_type STRING,
  event_timestamp STRING
)
TBLPROPERTIES (
  'delta.appendOnly' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true'
)
COMMENT 'Raw clickstream events with job metadata'
AS SELECT 
  current_timestamp() as _ingestion_timestamp,
  '${job_id}' as _ingestion_job_id,  -- Databricks job parameter
  _metadata.file_path as _source_file,
  *
FROM read_files(
  '/Volumes/main/raw/clickstream',
  format => 'json'
);

-- ----------------------------------------------------------------------------
-- Operational Commands for Bronze Tables
-- ----------------------------------------------------------------------------

-- Check ingestion status
DESCRIBE EXTENDED bronze.raw_customer_events;

-- View recent ingestion metadata
SELECT 
  _ingestion_timestamp,
  _source_file,
  COUNT(*) as record_count
FROM bronze.raw_customer_events
WHERE _ingestion_timestamp >= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR
GROUP BY _ingestion_timestamp, _source_file
ORDER BY _ingestion_timestamp DESC;

-- Optimize Bronze table (compact small files)
OPTIMIZE bronze.raw_customer_events;

-- Vacuum old files (after retention period)
VACUUM bronze.raw_customer_events RETAIN 168 HOURS;  -- 7 days

-- Time travel to view historical data
SELECT * FROM bronze.raw_customer_events VERSION AS OF 100;
SELECT * FROM bronze.raw_customer_events TIMESTAMP AS OF '2024-01-15 10:00:00';

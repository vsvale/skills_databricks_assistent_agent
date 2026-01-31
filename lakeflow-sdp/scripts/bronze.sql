-- =============================================================================
-- Bronze Layer Streaming Tables
-- =============================================================================
-- Bronze tables are the raw data landing zone in the medallion architecture.
-- Streaming tables are recommended for bronze layer because:
--   - They process each row only once (exactly-once semantics)
--   - They support incremental data loading from various sources
--   - They integrate with Auto Loader for efficient file ingestion
--   - They provide automatic checkpoint management
--
-- Best Practices:
--   - Use Unity Catalog volumes for data storage (recommended over S3/ADLS paths)
--   - Enable schema inference with inferColumnTypes for flexibility
--   - Add schemaHints for date/timestamp columns to ensure correct parsing
--   - Use descriptive table names with _bronze suffix for clarity
-- =============================================================================

-- ----------------------------------
-- Ingest credit bureau data (JSON format)
-- Credit bureau data contains information about customer credit history and creditworthiness
-- Monthly data accessed through API from government agencies or central banks
-- ----------------------------------

CREATE OR REFRESH STREAMING TABLE credit_bureau_bronze
AS
SELECT *
FROM STREAM read_files(
  '/Volumes/demos/lakehouse_hls_readmission/credit_raw_data/credit_bureau',
  format => 'json',
  inferColumnTypes => true
);

-- ----------------------------------
-- Ingest customer data (CSV format)
-- Customer table from internal KYC processes containing customer-related data
-- Daily ingestion from internal relational databases via CDC pipeline
-- ----------------------------------

CREATE OR REFRESH STREAMING TABLE customer_bronze
AS
SELECT *
FROM STREAM read_files(
  '/Volumes/demos/lakehouse_hls_readmission/credit_raw_data/internalbanking/customer',
  format => 'csv',
  header => true,
  inferSchema => true,
  inferColumnTypes => true,
  schemaHints => 'passport_expiry DATE, visa_expiry DATE, join_date DATE, dob DATE'
);

-- ----------------------------------
-- Ingest relationship data (CSV format)
-- Represents the relationship between the bank and the customer
-- Source: Internal banking databases
-- ----------------------------------

CREATE OR REFRESH STREAMING TABLE relationship_bronze
AS
SELECT *
FROM STREAM read_files(
  '/Volumes/demos/lakehouse_hls_readmission/credit_raw_data/internalbanking/relationship',
  format => 'csv',
  header => true,
  inferSchema => true,
  inferColumnTypes => true
);


-- ----------------------------------
-- Ingest account data (CSV format)
-- Customer account information from internal banking systems
-- Daily ingestion via CDC pipeline
-- ----------------------------------

CREATE OR REFRESH STREAMING TABLE account_bronze
AS
SELECT *
FROM STREAM read_files(
  '/Volumes/demos/lakehouse_hls_readmission/credit_raw_data/internalbanking/account',
  format => 'csv',
  header => true,
  inferSchema => true,
  inferColumnTypes => true
);

-- ----------------------------------
-- Ingest fund transfer data (JSON format)
-- Real-time payment transactions performed by customers
-- Streaming data available in real-time through Kafka
-- ----------------------------------

CREATE OR REFRESH STREAMING TABLE fund_trans_bronze
AS
SELECT *
FROM STREAM read_files(
  '/Volumes/demos/lakehouse_hls_readmission/credit_raw_data/fund_trans',
  format => 'json',
  inferColumnTypes => true
);

-- ----------------------------------
-- Ingest telco partner data (JSON format)
-- External partner data to augment internal banking data
-- Weekly ingestion containing payment features for common customers
-- Used to evaluate creditworthiness through alternative data sources
-- ----------------------------------

CREATE OR REFRESH STREAMING TABLE telco_bronze
AS
SELECT *
FROM STREAM read_files(
  '/Volumes/demos/lakehouse_hls_readmission/credit_raw_data/telco',
  format => 'json',
  inferColumnTypes => true
);

-- =============================================================================
-- Additional Bronze Table Examples
-- =============================================================================

-- ----------------------------------
-- Bronze table with data quality expectations
-- Validates that required fields are present before loading
-- ----------------------------------

CREATE OR REFRESH STREAMING TABLE validated_events_bronze (
  CONSTRAINT valid_event_id EXPECT (event_id IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT valid_timestamp EXPECT (event_timestamp IS NOT NULL) ON VIOLATION DROP ROW
)
AS
SELECT *
FROM STREAM read_files(
  '/Volumes/my_catalog/my_schema/my_volume/events',
  format => 'json',
  inferColumnTypes => true
);

-- ----------------------------------
-- Bronze table with scheduled refresh (hourly)
-- ----------------------------------

CREATE OR REFRESH STREAMING TABLE hourly_logs_bronze
SCHEDULE EVERY 1 HOUR
AS
SELECT *
FROM STREAM read_files(
  '/Volumes/my_catalog/my_schema/my_volume/logs',
  format => 'json',
  inferColumnTypes => true
);

-- ----------------------------------
-- Bronze table with trigger-based refresh
-- Automatically refreshes when upstream data changes
-- ----------------------------------

CREATE STREAMING TABLE triggered_bronze
TRIGGER ON UPDATE AT MOST EVERY INTERVAL 5 MINUTES
AS
SELECT *
FROM STREAM source_table;

-- ----------------------------------
-- Bronze table reading only new files (skip existing)
-- Useful when you only want to process files added after table creation
-- ----------------------------------

CREATE OR REFRESH STREAMING TABLE new_files_only_bronze
AS
SELECT *
FROM STREAM read_files(
  '/Volumes/my_catalog/my_schema/my_volume/incremental_data',
  format => 'parquet',
  includeExistingFiles => false
);

-- ----------------------------------
-- Bronze table with explicit schema definition
-- Use when schema inference is not desired or when you need specific types
-- ----------------------------------

CREATE OR REFRESH STREAMING TABLE explicit_schema_bronze (
  id INT,
  ts TIMESTAMP,
  event_type STRING,
  payload STRING
)
AS
SELECT *
FROM STREAM read_files(
  '/Volumes/my_catalog/my_schema/my_volume/typed_events',
  format => 'csv',
  header => true,
  schema => 'id INT, ts TIMESTAMP, event_type STRING, payload STRING'
);

-- ----------------------------------
-- Bronze table with partitioning
-- Partition by date for better query performance on time-based filters
-- ----------------------------------

CREATE OR REFRESH STREAMING TABLE partitioned_bronze
PARTITIONED BY (event_date)
AS
SELECT 
  *,
  DATE(event_timestamp) AS event_date
FROM STREAM read_files(
  '/Volumes/my_catalog/my_schema/my_volume/partitioned_data',
  format => 'json',
  inferColumnTypes => true
);

-- ----------------------------------
-- Bronze table with liquid clustering (recommended over partitioning)
-- Automatically optimizes data layout for query performance
-- ----------------------------------

CREATE OR REFRESH STREAMING TABLE clustered_bronze
CLUSTER BY AUTO
AS
SELECT *
FROM STREAM read_files(
  '/Volumes/my_catalog/my_schema/my_volume/clustered_data',
  format => 'json',
  inferColumnTypes => true
);

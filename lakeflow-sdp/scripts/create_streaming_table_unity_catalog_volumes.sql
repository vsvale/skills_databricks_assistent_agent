-- =============================================================================
-- Create Streaming Table from Unity Catalog Volumes
-- =============================================================================

-- JSON files from a volume
CREATE OR REFRESH STREAMING TABLE credit_bureau_bronze
AS SELECT * FROM STREAM read_files(
  '/Volumes/my_catalog/my_schema/my_volume/credit_bureau',
  format => 'json',
  inferColumnTypes => true
);

-- CSV files with schema hints for date columns
CREATE OR REFRESH STREAMING TABLE customer_bronze
AS SELECT * FROM STREAM read_files(
  '/Volumes/my_catalog/my_schema/my_volume/customers',
  format => 'csv',
  header => true,
  inferSchema => true,
  inferColumnTypes => true,
  schemaHints => 'join_date DATE, dob DATE'
);

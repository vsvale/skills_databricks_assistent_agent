-- =============================================================================
-- Create Streaming Table with Row Filters and Column Masks
-- =============================================================================

CREATE OR REFRESH STREAMING TABLE masked_csv_data (
  id int,
  name string,
  region string,
  ssn string MASK catalog.schema.ssn_mask_fn
)
WITH ROW FILTER catalog.schema.us_filter_fn ON (region)
AS SELECT * FROM STREAM read_files('s3://bucket/path/sensitive_data');

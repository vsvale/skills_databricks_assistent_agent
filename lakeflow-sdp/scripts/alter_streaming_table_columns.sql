-- =============================================================================
-- Alter Streaming Table Columns (Comments, Masks, Tags)
-- =============================================================================

-- Add a column comment
ALTER STREAMING TABLE my_table
ALTER COLUMN column_name COMMENT 'Description of column';

-- Set a column mask (for data anonymization)
ALTER STREAMING TABLE my_table
ALTER COLUMN ssn_column SET MASK catalog.schema.mask_function;

-- Drop a column mask
ALTER STREAMING TABLE my_table
ALTER COLUMN ssn_column DROP MASK;

-- Set column tags
ALTER STREAMING TABLE my_table
ALTER COLUMN column_name SET TAGS ('pii' = 'true', 'classification' = 'sensitive');

-- Unset column tags
ALTER STREAMING TABLE my_table
ALTER COLUMN column_name UNSET TAGS ('pii');

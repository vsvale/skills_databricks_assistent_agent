-- =============================================================================
-- Alter Streaming Table Row Filters and Table Tags
-- =============================================================================

-- Set a row filter (for fine-grained access control)
ALTER STREAMING TABLE my_table
SET ROW FILTER catalog.schema.filter_function ON (region_column);

-- Drop a row filter
ALTER STREAMING TABLE my_table
DROP ROW FILTER;

-- Set table tags
ALTER STREAMING TABLE my_table
SET TAGS ('env' = 'production', 'team' = 'data-eng');

-- Unset table tags
ALTER STREAMING TABLE my_table
UNSET TAGS ('env', 'team');

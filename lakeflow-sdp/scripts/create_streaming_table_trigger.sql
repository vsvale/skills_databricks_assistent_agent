-- =============================================================================
-- Trigger-based Streaming Table Refresh
-- =============================================================================

-- Refresh when source updates (minimum 1 minute between refreshes)
CREATE STREAMING TABLE triggered_data
TRIGGER ON UPDATE
AS SELECT * FROM STREAM source_table;

-- Limit refresh frequency
CREATE STREAMING TABLE throttled_data
TRIGGER ON UPDATE AT MOST EVERY INTERVAL 5 MINUTES
AS SELECT * FROM STREAM source_table;

-- Trigger limitations:
-- - Maximum 10 upstream data sources per streaming table
-- - Maximum 1000 streaming tables with TRIGGER ON UPDATE per workspace
-- - Minimum interval is 1 minute

-- =============================================================================
-- Schedule Streaming Table Refreshes
-- =============================================================================

-- Refresh every hour
CREATE OR REFRESH STREAMING TABLE hourly_data
SCHEDULE EVERY 1 HOUR
AS SELECT * FROM STREAM read_files('/Volumes/catalog/schema/vol/data');

-- Refresh with cron expression
CREATE OR REFRESH STREAMING TABLE daily_midnight
SCHEDULE CRON '0 0 0 * * ?' AT TIME ZONE 'America/Los_Angeles'
AS SELECT * FROM STREAM read_files('/Volumes/catalog/schema/vol/data');

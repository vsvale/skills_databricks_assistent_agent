-- =============================================================================
-- Alter Streaming Table Schedule
-- =============================================================================

-- Add a schedule
ALTER STREAMING TABLE my_table
ADD SCHEDULE EVERY 1 HOUR;

-- Modify existing schedule
ALTER STREAMING TABLE my_table
ALTER SCHEDULE EVERY 5 MINUTES;

-- Change to trigger-based refresh
ALTER STREAMING TABLE my_table
ALTER TRIGGER ON UPDATE AT MOST EVERY INTERVAL 1 HOUR;

-- Drop the schedule
ALTER STREAMING TABLE my_table
DROP SCHEDULE;

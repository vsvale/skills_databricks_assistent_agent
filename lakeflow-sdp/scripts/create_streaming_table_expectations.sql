-- =============================================================================
-- Create Streaming Table with Expectations
-- =============================================================================

CREATE OR REFRESH STREAMING TABLE validated_events_bronze (
  CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT valid_timestamp EXPECT (event_ts IS NOT NULL) ON VIOLATION FAIL UPDATE
)
AS SELECT * FROM STREAM read_files(
  '/Volumes/my_catalog/my_schema/my_volume/events',
  format => 'json',
  inferColumnTypes => true
);

-- Note: Expectations use CONSTRAINT name EXPECT (condition) ON VIOLATION action syntax.

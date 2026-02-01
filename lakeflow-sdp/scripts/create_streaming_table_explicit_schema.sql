-- =============================================================================
-- Create Streaming Table with Explicit Schema
-- =============================================================================

CREATE OR REFRESH STREAMING TABLE typed_events_bronze (
  id INT,
  ts TIMESTAMP,
  event_type STRING,
  payload STRING
)
AS SELECT *
FROM STREAM read_files(
  '/Volumes/my_catalog/my_schema/my_volume/events',
  format => 'csv',
  schema => 'id INT, ts TIMESTAMP, event_type STRING, payload STRING'
);

-- =============================================================================
-- Refresh Streaming Table
-- =============================================================================

-- Synchronous refresh (blocks until complete - default)
REFRESH STREAMING TABLE my_table SYNC;

-- Asynchronous refresh (returns immediately with a link to pipeline)
REFRESH STREAMING TABLE my_table ASYNC;

-- Full refresh (reprocess all data)
-- Warning: Avoid FULL refresh on sources without complete history retention (e.g. Kafka)
REFRESH STREAMING TABLE my_table FULL;

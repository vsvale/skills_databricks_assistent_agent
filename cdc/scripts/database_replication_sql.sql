-- Database Replication using AUTO CDC (SQL)
-- This pattern replicates an external RDBMS table using a snapshot + CDC feed.
-- Ideal for keeping a target table in sync with an external system of record.

-- Prerequisites:
-- 1. Full snapshot of source table in cloud storage (orders_snapshot_path)
-- 2. Continuous change feed in cloud storage (orders_cdc_path)

-- 1. Create View for Full Snapshot (Once)
-- Reads initial snapshot from cloud storage (e.g., exported JSON/Parquet)
CREATE OR REFRESH VIEW full_orders_snapshot AS
SELECT * FROM STREAM read_files(
  "${orders_snapshot_path}",
  "json",
  map("cloudFiles.includeExistingFiles", "true", "cloudFiles.inferColumnTypes", "true")
);

-- 2. Create View for CDC Feed (Continuous)
-- Reads incremental changes (inserts, updates, deletes)
CREATE OR REFRESH VIEW rdbms_orders_change_feed AS
SELECT * FROM STREAM read_files(
  "${orders_cdc_path}",
  "json",
  map("cloudFiles.includeExistingFiles", "true", "cloudFiles.inferColumnTypes", "true")
);

-- 3. Create Target Streaming Table
CREATE OR REFRESH STREAMING TABLE rdbms_orders;

-- 4. Initial Hydration (Once Flow)
-- Loads history; runs only once (ONCE=TRUE).
-- WARNING: New files added to snapshot path after pipeline creation are ignored.
-- WARNING: If snapshot data is removed from storage, full refresh will cause data loss.
CREATE FLOW rdbms_orders_hydrate
AS AUTO CDC ONCE INTO rdbms_orders
FROM stream(full_orders_snapshot)
KEYS (order_id)
SEQUENCE BY timestamp
STORED AS SCD TYPE 1;

-- 5. Continuous Ingestion (Change Flow) - SCD Type 1
-- Applies ongoing changes from the CDC feed.
-- Sequence by single column
CREATE FLOW rdbms_orders_continuous
AS AUTO CDC INTO rdbms_orders
FROM stream(rdbms_orders_change_feed)
KEYS (order_id)
SEQUENCE BY timestamp
STORED AS SCD TYPE 1;

-- 6. SCD Type 2 Example (History)
-- Tracks history of changes. Adds __START_AT and __END_AT columns.
-- Sequence by multiple columns (STRUCT)
-- Orders by timestamp, then id to break ties.
CREATE FLOW rdbms_orders_history
AS AUTO CDC INTO rdbms_orders_scd2
FROM stream(rdbms_orders_change_feed)
KEYS (order_id)
SEQUENCE BY STRUCT(timestamp, order_id)
STORED AS SCD TYPE 2;

-- Define source views for snapshot and continuous feed
CREATE OR REFRESH VIEW full_orders_snapshot
AS SELECT *
FROM STREAM read_files("${orders_snapshot_path}", "json", map(
  "cloudFiles.includeExistingFiles", "true",
  "cloudFiles.inferColumnTypes", "true"
));

CREATE OR REFRESH VIEW rdbms_orders_change_feed
AS SELECT *
FROM STREAM read_files("${orders_cdc_path}", "json", map(
  "cloudFiles.includeExistingFiles", "true",
  "cloudFiles.inferColumnTypes", "true"
));

-- Step 1: Create the target streaming table
CREATE OR REFRESH STREAMING TABLE rdbms_orders;

-- Step 2: Once Flow for initial snapshot (runs only once)
-- Merges the full snapshot into the target table
CREATE FLOW rdbms_orders_hydrate
AS AUTO CDC ONCE INTO rdbms_orders
FROM stream(full_orders_snapshot)
KEYS (order_id)
SEQUENCE BY timestamp
STORED AS SCD TYPE 1;

-- Step 3: Continuous CDC ingestion (runs continuously)
-- Merges incremental changes into the target table
CREATE FLOW rdbms_orders_continuous
AS AUTO CDC INTO rdbms_orders
FROM stream(rdbms_orders_change_feed)
KEYS (order_id)
SEQUENCE BY timestamp
STORED AS SCD TYPE 1;

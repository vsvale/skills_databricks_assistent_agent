-- ==========================================
-- Bronze Layer: Ingest Raw Data
-- ==========================================
CREATE OR REFRESH STREAMING TABLE bronze_customers
AS SELECT * FROM cloud_files(
  "/databricks-datasets/retail-org/customers/",
  "json",
  map("cloudFiles.inferColumnTypes", "true")
);

-- ==========================================
-- Silver Layer: Process CDC (SCD Type 1)
-- ==========================================
CREATE OR REFRESH STREAMING TABLE silver_customers;

APPLY CHANGES INTO LIVE.silver_customers
FROM STREAM(LIVE.bronze_customers)
KEYS (customer_id)
APPLY AS DELETE WHEN operation = 'DELETE'
SEQUENCE BY operation_date
COLUMNS * EXCEPT (operation, operation_date, _rescued_data)
STORED AS SCD TYPE 1;

-- ==========================================
-- Gold Layer: Aggregates
-- ==========================================
CREATE LIVE TABLE gold_customer_counts_by_state
AS SELECT
  state,
  count(*) as customer_count
FROM LIVE.silver_customers
GROUP BY state;

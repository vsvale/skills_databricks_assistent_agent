-- ============================================================================
-- Gold Layer Aggregation and Dimensional Modeling Examples
-- ============================================================================
-- Purpose: Demonstrate best practices for analytics-ready data
-- Key Principles:
--   - Apply dimensional modeling (star/snowflake schema)
--   - Pre-aggregate for BI performance
--   - Use liquid clustering for query optimization
--   - Implement row and column-level security
--   - Align with business terminology and KPIs
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Example 1: Dimension Table - Customers
-- ----------------------------------------------------------------------------
-- Create a customer dimension with business attributes

CREATE MATERIALIZED VIEW gold.dim_customers
COMMENT 'Customer dimension for analytics'
AS SELECT 
  customer_id as customer_key,
  customer_name,
  email,
  phone,
  address,
  city,
  state,
  country,
  postal_code,
  customer_segment,
  registration_date,
  lifetime_value_tier,
  is_active,
  current_timestamp() as _last_updated
FROM silver.unique_customers
WHERE customer_id IS NOT NULL;

-- ----------------------------------------------------------------------------
-- Example 2: Dimension Table - Products
-- ----------------------------------------------------------------------------
-- Create a product dimension with hierarchy

CREATE MATERIALIZED VIEW gold.dim_products
COMMENT 'Product dimension with category hierarchy'
AS SELECT 
  product_id as product_key,
  product_name,
  product_description,
  category,
  subcategory,
  brand,
  price,
  cost,
  price - cost as margin,
  CASE 
    WHEN price < 10 THEN 'Budget'
    WHEN price < 100 THEN 'Standard'
    ELSE 'Premium'
  END as price_tier,
  is_active,
  current_timestamp() as _last_updated
FROM silver.normalized_products;

-- ----------------------------------------------------------------------------
-- Example 3: Dimension Table - Date (Calendar)
-- ----------------------------------------------------------------------------
-- Create a date dimension for time-based analysis

CREATE MATERIALIZED VIEW gold.dim_date
COMMENT 'Date dimension for time intelligence'
AS SELECT 
  CAST(date_format(date, 'yyyyMMdd') AS INT) as date_key,
  date as full_date,
  year(date) as year,
  quarter(date) as quarter,
  month(date) as month,
  day(date) as day,
  dayofweek(date) as day_of_week,
  date_format(date, 'EEEE') as day_name,
  date_format(date, 'MMMM') as month_name,
  weekofyear(date) as week_of_year,
  CASE WHEN dayofweek(date) IN (1, 7) THEN true ELSE false END as is_weekend,
  CASE 
    WHEN date IN ('2024-01-01', '2024-07-04', '2024-12-25') THEN true 
    ELSE false 
  END as is_holiday
FROM (
  SELECT explode(sequence(
    to_date('2020-01-01'), 
    to_date('2030-12-31'), 
    interval 1 day
  )) as date
);

-- ----------------------------------------------------------------------------
-- Example 4: Fact Table - Sales Transactions
-- ----------------------------------------------------------------------------
-- Create a fact table with foreign keys to dimensions

CREATE MATERIALIZED VIEW gold.fact_sales
CLUSTER BY (date_key, customer_key)
COMMENT 'Sales fact table with dimensional keys'
AS SELECT 
  t.transaction_id as transaction_key,
  CAST(date_format(t.transaction_date, 'yyyyMMdd') AS INT) as date_key,
  t.customer_id as customer_key,
  t.product_id as product_key,
  -- Measures
  t.quantity,
  t.unit_price,
  t.total_amount as sales_amount,
  p.cost * t.quantity as cost_amount,
  t.total_amount - (p.cost * t.quantity) as profit_amount,
  -- Metadata
  current_timestamp() as _last_updated
FROM silver.validated_transactions t
LEFT JOIN silver.normalized_products p
  ON t.product_id = p.product_id;

-- ----------------------------------------------------------------------------
-- Example 5: Pre-Aggregated Fact Table - Daily Sales Summary
-- ----------------------------------------------------------------------------
-- Create aggregated metrics for faster BI queries

CREATE MATERIALIZED VIEW gold.fact_daily_sales_summary
CLUSTER BY (sale_date, category)
COMMENT 'Daily sales summary by product category'
AS SELECT 
  DATE(t.transaction_date) as sale_date,
  p.category,
  c.customer_segment,
  -- Aggregated measures
  COUNT(DISTINCT t.transaction_id) as transaction_count,
  COUNT(DISTINCT t.customer_id) as unique_customers,
  SUM(t.quantity) as total_quantity,
  SUM(t.total_amount) as total_revenue,
  AVG(t.total_amount) as avg_transaction_value,
  MIN(t.total_amount) as min_transaction_value,
  MAX(t.total_amount) as max_transaction_value,
  current_timestamp() as _last_updated
FROM silver.validated_transactions t
LEFT JOIN silver.normalized_products p
  ON t.product_id = p.product_id
LEFT JOIN silver.unique_customers c
  ON t.customer_id = c.customer_id
GROUP BY 
  DATE(t.transaction_date),
  p.category,
  c.customer_segment;

-- ----------------------------------------------------------------------------
-- Example 6: Customer 360 View
-- ----------------------------------------------------------------------------
-- Create a comprehensive customer analytics table

CREATE MATERIALIZED VIEW gold.customer_360
CLUSTER BY (customer_id)
COMMENT 'Comprehensive customer analytics view'
AS SELECT 
  c.customer_id,
  c.customer_name,
  c.email,
  c.customer_segment,
  c.registration_date,
  -- Purchase metrics
  COUNT(DISTINCT t.transaction_id) as total_purchases,
  SUM(t.total_amount) as lifetime_value,
  AVG(t.total_amount) as avg_order_value,
  MAX(t.transaction_date) as last_purchase_date,
  MIN(t.transaction_date) as first_purchase_date,
  DATEDIFF(CURRENT_DATE(), MAX(t.transaction_date)) as days_since_last_purchase,
  -- Product preferences
  COLLECT_SET(p.category) as purchased_categories,
  -- Engagement metrics
  COUNT(DISTINCT e.event_id) as total_events,
  MAX(e.event_timestamp) as last_activity_date,
  -- Segmentation
  CASE 
    WHEN DATEDIFF(CURRENT_DATE(), MAX(t.transaction_date)) <= 30 THEN 'Active'
    WHEN DATEDIFF(CURRENT_DATE(), MAX(t.transaction_date)) <= 90 THEN 'At Risk'
    ELSE 'Churned'
  END as customer_status,
  current_timestamp() as _last_updated
FROM silver.unique_customers c
LEFT JOIN silver.validated_transactions t
  ON c.customer_id = t.customer_id
LEFT JOIN silver.normalized_products p
  ON t.product_id = p.product_id
LEFT JOIN silver.clean_customer_events e
  ON c.customer_id = e.customer_id
GROUP BY 
  c.customer_id,
  c.customer_name,
  c.email,
  c.customer_segment,
  c.registration_date;

-- ----------------------------------------------------------------------------
-- Example 7: Product Performance Analytics
-- ----------------------------------------------------------------------------
-- Create product-level KPIs for merchandising

CREATE MATERIALIZED VIEW gold.product_performance
CLUSTER BY (product_id, sale_month)
COMMENT 'Product performance metrics by month'
AS SELECT 
  p.product_id,
  p.product_name,
  p.category,
  DATE_TRUNC('MONTH', t.transaction_date) as sale_month,
  -- Sales metrics
  COUNT(DISTINCT t.transaction_id) as units_sold,
  SUM(t.total_amount) as revenue,
  SUM(t.total_amount - (p.cost * t.quantity)) as profit,
  AVG(t.unit_price) as avg_selling_price,
  -- Customer metrics
  COUNT(DISTINCT t.customer_id) as unique_buyers,
  -- Ranking
  RANK() OVER (
    PARTITION BY DATE_TRUNC('MONTH', t.transaction_date) 
    ORDER BY SUM(t.total_amount) DESC
  ) as revenue_rank,
  current_timestamp() as _last_updated
FROM silver.normalized_products p
LEFT JOIN silver.validated_transactions t
  ON p.product_id = t.product_id
GROUP BY 
  p.product_id,
  p.product_name,
  p.category,
  p.cost,
  DATE_TRUNC('MONTH', t.transaction_date);

-- ----------------------------------------------------------------------------
-- Example 8: Cohort Analysis Table
-- ----------------------------------------------------------------------------
-- Create customer cohort analysis for retention metrics

CREATE MATERIALIZED VIEW gold.customer_cohorts
COMMENT 'Customer cohort analysis by registration month'
AS SELECT 
  DATE_TRUNC('MONTH', c.registration_date) as cohort_month,
  DATE_TRUNC('MONTH', t.transaction_date) as transaction_month,
  MONTHS_BETWEEN(
    DATE_TRUNC('MONTH', t.transaction_date),
    DATE_TRUNC('MONTH', c.registration_date)
  ) as months_since_registration,
  COUNT(DISTINCT c.customer_id) as cohort_size,
  COUNT(DISTINCT t.customer_id) as active_customers,
  SUM(t.total_amount) as cohort_revenue,
  AVG(t.total_amount) as avg_revenue_per_customer
FROM silver.unique_customers c
LEFT JOIN silver.validated_transactions t
  ON c.customer_id = t.customer_id
GROUP BY 
  DATE_TRUNC('MONTH', c.registration_date),
  DATE_TRUNC('MONTH', t.transaction_date);

-- ----------------------------------------------------------------------------
-- Example 9: Row-Level Security
-- ----------------------------------------------------------------------------
-- Apply row-level security for regional access control

-- Create function to filter by user's region
CREATE FUNCTION gold.filter_by_region(region STRING)
RETURN IF(
  is_member('global_managers'), 
  TRUE,  -- Global managers see all regions
  region = current_user_region()  -- Others see only their region
);

-- Apply row filter to sales fact table
CREATE MATERIALIZED VIEW gold.fact_sales_secure
WITH ROW FILTER gold.filter_by_region(region)
AS SELECT 
  t.*,
  c.region
FROM gold.fact_sales t
LEFT JOIN gold.dim_customers c
  ON t.customer_key = c.customer_key;

-- ----------------------------------------------------------------------------
-- Example 10: Column-Level Security (Data Masking)
-- ----------------------------------------------------------------------------
-- Mask sensitive columns based on user permissions

-- Create masking function for email
CREATE FUNCTION gold.mask_email(email STRING)
RETURN CASE 
  WHEN is_member('pii_readers') THEN email
  ELSE CONCAT(LEFT(email, 3), '***@***.***')
END;

-- Apply column mask to customer dimension
ALTER TABLE gold.dim_customers
ALTER COLUMN email SET MASK gold.mask_email(email);

-- Apply mask to phone numbers
ALTER TABLE gold.dim_customers
ALTER COLUMN phone SET MASK 
  CASE 
    WHEN is_member('pii_readers') THEN phone
    ELSE '***-***-****'
  END;

-- ----------------------------------------------------------------------------
-- Example 11: Materialized View with Auto Clustering
-- ----------------------------------------------------------------------------
-- Let Databricks automatically optimize clustering

CREATE MATERIALIZED VIEW gold.sales_analytics
CLUSTER BY AUTO
COMMENT 'Sales analytics with automatic clustering optimization'
AS SELECT 
  t.transaction_date,
  t.customer_id,
  t.product_id,
  c.customer_segment,
  p.category,
  t.total_amount,
  t.quantity
FROM silver.validated_transactions t
LEFT JOIN silver.unique_customers c ON t.customer_id = c.customer_id
LEFT JOIN silver.normalized_products p ON t.product_id = p.product_id;

-- ----------------------------------------------------------------------------
-- Operational Commands for Gold Tables
-- ----------------------------------------------------------------------------

-- Refresh materialized view
REFRESH MATERIALIZED VIEW gold.fact_daily_sales_summary;

-- Optimize with liquid clustering
OPTIMIZE gold.customer_360;

-- Analyze for query optimization
ANALYZE TABLE gold.fact_sales COMPUTE STATISTICS;

-- Monitor table size and performance
DESCRIBE DETAIL gold.fact_sales;

-- Check clustering effectiveness
SELECT * FROM system.clustering_information('gold.customer_360');

-- Grant access to business users
GRANT SELECT ON gold.dim_customers TO `business_analysts`;
GRANT SELECT ON gold.fact_sales TO `business_analysts`;

-- Create BI-optimized SQL warehouse endpoint
-- (Configure in Databricks UI: Serverless, Auto-stop, Query caching enabled)

-- Monitor query performance
SELECT 
  query_text,
  execution_time_ms,
  rows_produced,
  bytes_read
FROM system.query_history
WHERE schema_name = 'gold'
  AND start_time >= CURRENT_TIMESTAMP() - INTERVAL 1 DAY
ORDER BY execution_time_ms DESC
LIMIT 10;

-- read_files_sql.sql
-- Examples: Read files from Volumes and workspace using Spark SQL.
-- Run in Databricks SQL or in a notebook with %sql. Replace paths and catalog/schema/volume as needed.

-- ========== JSON ==========

-- Volume: single-line JSON
CREATE OR REPLACE TEMP VIEW json_volume_view
USING json
OPTIONS (path "/Volumes/main/default/my_volume/credit_bureau/");

SELECT * FROM json_volume_view LIMIT 10;


-- Volume: multi-line JSON
CREATE OR REPLACE TEMP VIEW json_multiline_view
USING json
OPTIONS (path "/Volumes/main/default/my_volume/multi_line_data/", multiline "true");

SELECT * FROM json_multiline_view LIMIT 10;


-- Workspace: JSON (use file:/ scheme)
CREATE OR REPLACE TEMP VIEW json_workspace_view
USING json
OPTIONS (path "file:/Workspace/Users/user@domain.com/data/events.json");

SELECT * FROM json_workspace_view LIMIT 10;


-- Query semi-structured JSON in a string column (e.g. column 'raw')
-- SELECT raw:owner, raw:store.bicycle.price::double, raw:store.fruit[0].type FROM table_name;


-- parse_json (Databricks SQL): string -> VARIANT
-- SELECT parse_json(json_column) AS v FROM table_name;


-- ========== CSV ==========

-- Volume: CSV with header
CREATE OR REPLACE TEMP VIEW csv_volume_view
USING csv
OPTIONS (path "/Volumes/main/default/my_volume/data/", header "true");

SELECT * FROM csv_volume_view LIMIT 10;


-- Workspace: CSV
CREATE OR REPLACE TEMP VIEW csv_workspace_view
USING csv
OPTIONS (path "file:/Workspace/Users/user@domain.com/data/sample.csv", header "true");

SELECT * FROM csv_workspace_view LIMIT 10;


-- ========== Parquet ==========

-- Volume: Parquet
CREATE OR REPLACE TEMP VIEW parquet_volume_view
USING parquet
OPTIONS (path "/Volumes/main/default/my_volume/parquet_data/");

SELECT * FROM parquet_volume_view LIMIT 10;


-- Workspace: Parquet
CREATE OR REPLACE TEMP VIEW parquet_workspace_view
USING parquet
OPTIONS (path "file:/Workspace/Users/user@domain.com/data/data.parquet");

SELECT * FROM parquet_workspace_view LIMIT 10;


-- ========== Direct path in SELECT (path as table) ==========

SELECT * FROM json.`/Volumes/main/default/my_volume/events/` LIMIT 10;
SELECT * FROM csv.`/Volumes/main/default/my_volume/csv_data/` WHERE _c0 IS NOT NULL LIMIT 10;
SELECT * FROM parquet.`/Volumes/main/default/my_volume/parquet_data/` LIMIT 10;

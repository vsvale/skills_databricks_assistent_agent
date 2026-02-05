# Frequent Migration Errors & Solutions

## Access & Permissions
- **Error**: `[UNAUTHORIZED_ACCESS] User does not have CREATE TABLE and USE SCHEMA on Schema 'analytics_prd.gold'`
  - **Solution**: Contact Platform Evolution team to fix system user permissions.
- **Error**: `NoCredentialsError: Unable to locate credentials`
  - **Solution**: Use a dedicated cluster, add retries, or use Databricks Secrets.

## Unity Catalog Configuration
- **Error**: `[UC_NOT_ENABLED] Unity Catalog is not enabled on this cluster`
  - **Solution**: Set `data_security_mode` to `USER_ISOLATION` (Standard) or `SINGLE_USER` (Dedicated) in `job.json`.
- **Error**: `UC_COMMAND_NOT_SUPPORTED.WITHOUT_RECOMMENDATION` (Views referencing Hive & UC)
  - **Solution**: Migrate Hive tables to UC or use CTAS to materialize the view (requires a job to update).

## Delta & Streaming
- **Error**: `AnalysisException: Table or view not found: catalog.schema.table`
  - **Context**: Occurs when switching from `spark.read.load(path)` to `spark.table(name)`.
  - **Solution**: Ensure the table is created in Unity Catalog. The error message is different from the legacy `Path does not exist`.

- **Error**: `[DELTA_UNSUPPORTED_OUTPUT_MODE] ... does not support Update output mode`
  - **Solution**: Change output mode to `append` or use `foreachBatch` with `merge`.
- **Error**: `com.amazon.deequ... NoSuchMethodError: ...XxHash64Function`
  - **Solution**: Use DBR 14.3 LTS or 15.4 LTS (Spark 3.5.0 compatibility).
- **Error**: `GIT_CONFLICT` in `03_delivery_sftp.py`
  - **Solution**: Pull master and retry.

## Libraries
- **Error**: `AttributeError: module 'lib' has no attribute 'X509_V_FLAG_NOTIFY_POLICY'`
  - **Solution**: Update DBR version.
- **Error**: SSH Key Invalid in SFTP Jobs
  - **Solution**: Use DBR 14.3 and specific cryptography lib version from Volumes (`/Volumes/dataops_prd/libraries/libs/crm/...`).

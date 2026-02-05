# Migration Strategy

## 1. Copy Only
**Scenario**:
- Table has no associated job.
- Table hasn't been updated in > 60 days.
- Job is disabled.
- Job is paused and hasn't run in > 60 days.
- Table restored, logic unknown.

**Action**:
- Perform CTAS from Hive path to Unity.
- No code, file, repo, or job changes.

**Example (Partitioned)**:
```sql
CREATE OR REPLACE TABLE premium_prd.bronze.tb_freemium_leaks CLUSTER BY (dt_load_bronze)
AS SELECT dt_load_bronze, * except(dt_load_bronze) FROM delta.`s3://serasaexperian-ecs-datalakehouse-prd-bronze/ecs/antifraude/freemium_darkweb/leaks/`;
```

**Example (Non-Partitioned)**:
```sql
CREATE OR REPLACE TABLE premium_prd.bronze.tb_base_subscription_ecs_antifraude_subscription_free CLUSTER BY AUTO
AS SELECT * FROM  hive_metastore.db_premium_bronze.tb_base_subscription_ecs_antifraude_subscription_free
```

## 2. Workspace Level
**Scenario**:
- Job runs at workspace level for a non-system user.

**Action**:
- Notebook owner transfers notebooks/config to a Repo.
- Or owner modifies notebook in their Personal Workspace with migration team support.

## 3. Repos
**Scenario**:
- Jobs with code versioned in Repositories.

**Action**:
- Migration team performs all changes if the product team has no engineers.

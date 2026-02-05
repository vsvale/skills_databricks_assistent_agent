---
name: create-job-json-for-unity
description: How to define Unity Catalog job configurations in JSON format for creating and updating jobs through the Databricks Jobs API. Includes Git source, mandatory tags, policies, and pools.
---

# Creating and Maintaining Databricks Jobs Using job.json

## Description
This skill teaches how to structure, validate, and maintain `job.json` files used by the CI/CD pipeline to create and update Databricks jobs. It covers Git as source, required tags, mandatory policies, pools, cluster rules, and orchestration patterns like Job of Jobs.

## Assistant Instructions
- **Context Awareness**: Always check the current directory (`pwd`) and list files (`ls`) before creating `job_proposition.json` to ensure it's in the same folder as the base `job.json`.
- **Validation**: Always verify if the generated `job_proposition.json` is a valid JSON file.
- **Product Context**: Always ask for the "Product" name associated with the job. Use this to determine the correct Git repository URL and the `BusinessServices` tag.
- **Migration**: When migrating to Unity Catalog, create a `job_proposition.json` instead of overwriting the original file immediately.
- **Orchestration**: Encourage "Job of Jobs" pattern for complex workflows. If a user asks to orchestrate multiple notebooks, suggest a modular approach where a main job triggers sub-tasks or uses the `Run Job` task type.

## 1. Understanding `job.json`
`job.json` is the **input file** consumed by the CI/CD pipeline to **create** or **update** Databricks jobs.
The CI/CD pipeline uses Databricks API endpoints:
- **jobs/create**: https://docs.databricks.com/api/workspace/jobs/create
- **jobs/reset**: https://docs.databricks.com/api/workspace/jobs/reset

## 2. Configure Git as the Source
**Critical Requirement**: Workspace paths (`/Repos/...`) are forbidden in production. You **MUST** use `git_source`.

### Required Adjustments
1.  Add `"git_source"` block to `job.json`.
2.  Change `notebook_task.source` from `"WORKSPACE"` to `"GIT"`.
3.  Update `notebook_path` to use the **relative path** inside the repository.

### Example Transformation

**Before (Workspace - Forbidden):**
```json
"notebook_task": {
  "notebook_path": "/Repos/ecs_ci_cd_datalake@br.experian.com/dataops-ml/src/notebook",
  "source": "WORKSPACE"
}
```

**After (Git - Required):**
```json
"notebook_task": {
  "notebook_path": "dataops-ml/src/notebook",
  "source": "GIT"
},
"git_source": {
    "git_url": "https://gitlab.ecsbr.net/dataops/core/dataops-core-mkt",
    "git_provider": "gitLab",
    "git_branch": "main"
}
```
*Note: The `git_url` depends on the Product. Ask the user if unknown.*

## 3. Mandatory Tags
Tags are **required** for Datadog monitoring and cost attribution.
See [Required Tags List](https://serasaexperian.atlassian.net/wiki/spaces/DE/pages/4510089353/Tagueamento+de+Jobs+no+Databricks) (Internal).

### Required Fields
- **BU**: Business Unit (e.g., `ECS`, `TEX`).
- **BusinessServices**: Product/Team (e.g., `PREMIUM`).
- **Environment**: Execution env (e.g., `PRD`).
- **CreatedBy**: Support Team (e.g., `DATAOPS`).
- **JobType**: `ETL`, `DLT`, `MAINTENANCE_JOB`, etc.
- **Data_Category**: Importance level (`ALTA`, `MEDIA`, `BAIXA`, `BAIXISSIMA`). **Must be in Portuguese**.
- **datadog**: `TRUE` or `FALSE`.

**Example:**
```json
"tags": {
  "BU": "ECS",
  "datadog": "TRUE",
  "BusinessServices": "BOX",
  "Environment": "PRD",
  "CreatedBy": "ANALYTICS",
  "JobType": "ETL",
  "Data_Category": "BAIXA"
}
```

## 4. Policies and Pools
Policies control cluster configurations and are **mandatory**.
- **Legacy Policies**: For Hive/Legacy jobs.
- **Unity Catalog Policies**: For all new development.

**Critical Rules:**
- **Never** define `node_type_id`, `driver_node_type_id`, or `spark_conf` manually. The Policy handles this.
- **Always** use Instance Pools (`instance_pool_id`) defined in the [Reference Guide](references/REFERENCES.md).
- **Never** use "Self Service" policies in Production.

**Correct Cluster Config:**
```json
"new_cluster": {
  "instance_pool_id": "0904-143702-ides62-pool-dkt26byo",
  "driver_instance_pool_id": "0904-143702-slump63-pool-oanf22hc",
  "autoscale": { "max_workers": 5 },
  "policy_id": "001F0E3652D6CF50"
}
```

See [references/REFERENCES.md](references/REFERENCES.md) for the full list of Policy IDs and Pool IDs.

## 5. Job Orchestration Best Practices

### Job of Jobs Pattern
For complex workflows, avoid monolithic jobs with dozens of tasks. Instead, use the **Job of Jobs** pattern:
1.  Create smaller, modular jobs for specific domains (e.g., "Ingest Sales", "Process Customers").
2.  Create a "Controller Job" that triggers these sub-jobs using the `Run Job` task type.
3.  This improves readability, retriability, and allows independent testing.

### Git Integration
- Always map the job name to the folder name in the repository for consistency.
- Example: If the folder is `dataops-etl-finance`, the job name should be `dataops-etl-finance` (or `_uc` suffix for Unity).

## 6. Anti-Patterns (What NOT to do)
- **Forbidden**: Using `source: "WORKSPACE"`.
- **Forbidden**: Hardcoding `node_type_id` (e.g., `r6gd.2xlarge`) in the JSON. Use Pools!
- **Forbidden**: Missing `datadog` tag (Silent failures).
- **Forbidden**: Installing libraries at the cluster level (Libraries must be in the Policy or installed via script/notebook context if absolutely necessary, but Policy is preferred).

## 7. Edge Cases
- **High Performance**: If a user requests massive compute (12xlarge+), they need the "High Performance" policy and formal approval (Tech Sync).
- **Lakeflow**: For DLT pipelines, use the `Lakeflow UC Engenharia` policy.

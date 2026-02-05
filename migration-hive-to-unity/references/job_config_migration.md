# Job Configuration Migration (JSON)

## 1. Compute Configuration (Policies & Pools)
**Migration Rule**: Stop defining raw AWS attributes, Instance Profiles, and S3 keys in `job.json`. Use **Cluster Policies** and **Instance Pools** enforced by the platform team.

### Pattern: Cluster Definition
*Before (Legacy)*:
- Explicit `spark_conf` for S3 keys (`spark.hadoop.fs.s3a...`).
- Explicit `aws_attributes` with `instance_profile_arn`.
- Explicit node types (`r6gd.2xlarge`).
```json
"new_cluster": {
  "spark_conf": {
    "spark.hadoop.fs.s3a.requester-pays.enabled": "true",
    "spark.hadoop.fs.s3a.acl.default": "BucketOwnerFullControl"
  },
  "aws_attributes": {
    "instance_profile_arn": "arn:aws:iam::123456789:instance-profile/legacy-profile",
    "availability": "SPOT_WITH_FALLBACK"
  },
  "node_type_id": "r6gd.2xlarge",
  "driver_node_type_id": "r6gd.2xlarge"
}
```

*After (Unity Catalog)*:
- **`policy_id`**: Applies security rules, instance profiles, and tag enforcement.
- **`instance_pool_id`**: Manages compute capacity and startup time.
- **Clean Configuration**: No visible keys or raw infrastructure details.
```json
"new_cluster": {
  "spark_version": "13.3.x-scala2.12",
  "policy_id": "001F0E3652D6CF50",
  "instance_pool_id": "0904-143723-fame4-pool-mx9sp4pc",
  "driver_instance_pool_id": "0904-143724-entry182-pool-ops4qzv4",
  "autoscale": {
    "min_workers": 2,
    "max_workers": 5
  }
}
```

## 2. Git Source & Paths (Unified Repos)
**Migration Rule**: Point to the **Unified Repository** and update notebook paths to match the new folder structure.

### Pattern: Git Source
*Before*:
```json
"git_source": {
  "git_url": "https://gitlab.ecsbr.net/dataops/core/specific-pipeline-repo.git",
  "git_branch": "main"
}
```

*After*:
```json
"git_source": {
  "git_url": "https://gitlab.ecsbr.net/dataops/core/dataops-core-unified-repo.git",
  "git_branch": "main"
}
```

### Pattern: Notebook Paths
*Before*:
```json
"notebook_task": {
  "notebook_path": "src/databricks/workspace/01_etl_notebook"
}
```

*After*:
- Path includes the project folder within the unified repo.
```json
"notebook_task": {
  "notebook_path": "project_folder_name/src/databricks/workspace/01_etl_notebook"
}
```

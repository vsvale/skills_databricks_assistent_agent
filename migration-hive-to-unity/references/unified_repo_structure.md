# Unified Repository Structure

## Context
Shift from 1:1 (Repo:Job) to **Unified Repositories per Product**.
- **Goal**: Better governance, traceability (Gear ID), and reduced clutter.

## Structure
```text
/dataops-core-<product>
    ├── gear.properties       # Gear ID configuration
    ├── .gitlab-ci.yml
    ├── cicd/
    ├── <job_name_1>/         # Standardized folder name
    │   └── src/
    │       └── databricks/
    │           ├── jobs/
    │           │   └── job.json
    │           └── workspace/
    │               └── notebook_etl.py
    └── <job_name_2>/
```

## Naming Conventions
- **Job Folders**: `<BU>_<Product>_<Function>`. No spaces, special chars, or timestamps.
  - *Bad*: `[BIZDEV] PPT Automatizado (11h30)`
  - *Good*: `BIZDEV_PPT_Automatizado_11h30`

## Migration Steps
1. Create folder in Unified Repo.
2. Clone original repo.
3. Move `src` folder to new location.
4. Update `job.json`:
   - Update `git_source.git_url` to the new Unified Repo URL.
   - Update `notebook_task.notebook_path` to include the project folder prefix.
5. Update CI/CD pipeline.

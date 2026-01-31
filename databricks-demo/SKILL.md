---
name: databricks-demo
description: Install and manage Databricks Lakehouse demos with dbdemos. Covers installation, listing demos by category, installing demos (notebooks, Lakeflow Spark Declarative Pipelines, DBSQL dashboards, ML models), cluster creation, and install options (path, overwrite, Unity Catalog catalog/schema, skip dashboards, serverless). Use when the user wants to install a Databricks demo, explore dbdemos, run lakehouse-retail-c360 or other tutorials, or set up demo notebooks and assets in a workspace.
---

# Databricks Demo (dbdemos)

Use **dbdemos** to install Databricks Lakehouse demos into your workspace: notebooks, Lakeflow Spark Declarative Pipelines (SDP), DBSQL dashboards, ML models, and related assets. Demos are one-line installable and scoped by use case (data engineering, data science, governance, etc.).

**Resources:** [Tutorials](https://www.databricks.com/resources/demos/tutorials) · [GitHub dbdemos](https://github.com/databricks-demos/dbdemos)

## When to Use This Skill

Use when the user needs to:
- Install a Databricks demo (e.g. lakehouse-retail-c360, CDC, MLOps, Unity Catalog)
- List available demos or filter by category (governance, data-engineering, etc.)
- Get help on dbdemos usage
- Install demos without cluster creation (use current cluster)
- Install to a specific Unity Catalog catalog/schema
- Skip DBSQL dashboards or Genie rooms for a faster or constrained install

## Requirements (Summary)

- **Workspace:** Run dbdemos from a Databricks notebook (or environment that can call the Databricks API).
- **Permissions:** Typically cluster creation, SDP pipeline creation, and DBSQL dashboard/query creation. For UC demos, Unity Catalog metastore must be available. If the user lacks cluster creation, use `use_current_cluster=True`.
- **Install:** `%pip install dbdemos` in a notebook cell, then `import dbdemos`.

## Step-by-Step: Install and Use

### 1. Install dbdemos

In a Databricks notebook cell:

```python
%pip install dbdemos
```

Restart the Python kernel or detach/reattach the cluster if needed, then:

```python
import dbdemos
```

### 2. Get Help and List Demos

```python
dbdemos.help()   # Display help and usage
dbdemos.list_demos()   # List all demos
dbdemos.list_demos(category='governance')   # Filter by category
```

Categories align with the [Tutorials](https://www.databricks.com/resources/demos/tutorials) page (e.g. data-engineering, data-science, governance).

### 3. Install a Demo

Basic install to current folder (e.g. lakehouse retail C360):

```python
dbdemos.install('lakehouse-retail-c360')
```

Install to a specific path with overwrite:

```python
dbdemos.install('lakehouse-retail-c360', path='./', overwrite=True)
```

Without cluster creation (use attached cluster):

```python
dbdemos.install('lakehouse-retail-c360', use_current_cluster=True)
```

Install to Unity Catalog catalog/schema:

```python
dbdemos.install('lakehouse-retail-c360', catalog='my_catalog', schema='my_schema')
```

Skip DBSQL dashboards (faster or to avoid dashboard issues):

```python
dbdemos.install('lakehouse-retail-c360', skip_dashboards=True)
```

### 4. Create or Update Demo Cluster

To install or update the interactive cluster for a demo (per user):

```python
dbdemos.create_cluster('lakehouse-retail-c360')
```

### 5. Install All Demos (Optional)

Bulk install every demo to a path (use with care; can be slow and create many resources):

```python
dbdemos.install_all(path='./demos/', overwrite=False, skip_dashboards=False, cloud='AWS')
```

## API Summary

| Function | Purpose |
|----------|---------|
| `dbdemos.help()` | Display help text. |
| `dbdemos.list_demos(category=None)` | List demos; optional `category` filter (e.g. `'governance'`). |
| `dbdemos.install(demo_name, path="./", overwrite=False, ...)` | Install one demo. See [references/dbdemos_api.md](references/dbdemos_api.md) for full parameters. |
| `dbdemos.create_cluster(demo_name)` | Create/update the demo’s interactive cluster for the current user. |
| `dbdemos.install_all(path="./", overwrite=False, ...)` | Install all demos to `path`. |

## Common Install Options

- **path** – Where to install (default `"./"`).
- **overwrite** – If `True`, delete existing folder at `path` and re-install.
- **use_current_cluster** – If `True`, do not start a new cluster for init; use the current cluster (e.g. when user cannot create clusters).
- **skip_dashboards** – If `True`, do not create DBSQL dashboards (faster; use if dashboard creation fails).
- **catalog**, **schema** – Unity Catalog catalog and schema for data and assets.
- **cloud** – `"AWS"`, `"Azure"`, or `"GCP"` (default `"AWS"`).
- **username**, **pat_token**, **workspace_url** – Override auth/workspace; if omitted, use current user and workspace.
- **warehouse_name** – DBSQL warehouse for dashboards.
- **serverless** – Force serverless compute; can also be auto-detected.
- **skip_genie_rooms** – If `True`, skip Genie room setup (beta).
- **dlt_policy_id**, **dlt_compute_settings** – For DLT pipelines (e.g. policy ID and autoscale min/max workers).

## Edge Cases and Troubleshooting

| Situation | Action |
|------------|--------|
| No cluster creation permission | Use `dbdemos.install(..., use_current_cluster=True)`. |
| Dashboard creation fails or is slow | Use `skip_dashboards=True`. |
| UC demo but no metastore | Demo can install but may not run; ensure Unity Catalog is enabled and metastore is available. |
| Want a specific warehouse for dashboards | Pass `warehouse_name='your_warehouse'` to `install`. |
| Need to respect a DLT policy | Use `dlt_policy_id` and `dlt_compute_settings` in `install`. |
| Install from another workspace/auth | Use `username`, `pat_token`, `workspace_url` (prefer secrets for PAT). |

## Best Practices

1. **Prefer one demo at a time** – Use `dbdemos.install(demo_name)` for a single demo unless the user explicitly wants `install_all`.
2. **Use a dedicated path** – Install to a clear path (e.g. `./demos/<demo_name>`) to avoid overwriting other work.
3. **Set overwrite explicitly** – Use `overwrite=True` only when the user intends to replace existing content.
4. **Minimize permissions** – If the user cannot create clusters, recommend `use_current_cluster=True`.
5. **Unity Catalog** – For UC demos, specify `catalog` and `schema` when the user wants assets in a particular location.
6. Do not set workspace_url it can break links in notebooks
7. Do not set in path an absolute path like `/Workspace/Users/user@domain.com/databricks_demos`, it will break notebooks links

For full parameter lists and packaging/bundle details, see [references/dbdemos_api.md](references/dbdemos_api.md).

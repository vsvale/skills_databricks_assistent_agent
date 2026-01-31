# dbdemos API Reference

Full parameter reference and links for the Databricks dbdemos package.

## Links

- **Tutorials:** <https://www.databricks.com/resources/demos/tutorials>
- **GitHub:** <https://github.com/databricks-demos/dbdemos>
- **Explore demos:** <https://dbdemos.ai> (if available)

## Installation

In a Databricks notebook cell:

```python
%pip install dbdemos
```

Then:

```python
import dbdemos
```

## Functions

### dbdemos.help()

Display help text for dbdemos usage. No parameters.

### dbdemos.list_demos(category: str = None)

List all available demos.

- **category** (optional): Filter by category (e.g. `'governance'`, `'data-engineering'`, `'data-science'`).

### dbdemos.install(demo_name: str, ...)

Install the given demo to the workspace.

**Required:**

- **demo_name**: Demo identifier (e.g. `'lakehouse-retail-c360'`).

**Common parameters:**

- **path**: str = `"./"` – Install path (folder) for notebooks and assets.
- **overwrite**: bool = `False` – If `True`, delete the path folder and re-install.
- **use_current_cluster**: bool = `False` – If `True`, do not start a new cluster for init; use the current cluster. Set when the user lacks cluster creation permission.
- **skip_dashboards**: bool = `False` – If `True`, do not create DBSQL dashboards (faster; use if dashboard creation fails).
- **cloud**: str = `"AWS"` – Cloud for the workspace (`"AWS"`, `"Azure"`, `"GCP"`).
- **catalog**: str = `None` – Unity Catalog catalog for data and assets.
- **schema**: str = `None` – Unity Catalog schema for data and assets.
- **username**: str = `None` – Override username for authentication.
- **pat_token**: str = `None` – Override PAT for authentication.
- **workspace_url**: str = `None` – Override workspace URL. If no auth/URL provided, dbdemos uses the current user and workspace.
- **warehouse_name**: str = `None` – DBSQL warehouse name for dashboards.
- **serverless**: bool = `None` – Force serverless compute; can also be auto-detected.
- **skip_genie_rooms**: bool = `False` – If `True`, skip Genie room installation (beta).
- **dlt_policy_id**: str = `None` – DLT policy ID (e.g. `"0003963E5B551CE4"`).
- **dlt_compute_settings**: dict = `None` – DLT compute settings, e.g. `{"autoscale": {"min_workers": 1, "max_workers": 5}}` to match policy.

### dbdemos.create_cluster(demo_name: str)

Create or update the interactive cluster for the demo (scoped to the current user).

- **demo_name**: Same identifier used in `dbdemos.install()`.

### dbdemos.install_all(...)

Install all demos to the given path.

**Parameters:**

- **path**: str = `"./"` – Base path for all demos.
- **overwrite**: bool = `False` – Overwrite existing content at path.
- **username**, **pat_token**, **workspace_url**: Optional auth/workspace override.
- **skip_dashboards**: bool = `False` – Skip DBSQL dashboards for all demos.
- **cloud**: str = `"AWS"` – Cloud for the workspace.

## What dbdemos Can Create

- Notebooks (often pre-run) at the given path.
- Init job to load demo datasets.
- Demo-specific cluster for the user.
- Lakeflow Spark Declarative Pipelines (SDP).
- DBSQL dashboards and queries.
- ML models (where applicable).
- Demo links updated to point to created resources.

## Requirements (from GitHub)

The current user typically needs:

- Cluster creation permission (or use `use_current_cluster=True`).
- SDP pipeline creation permission.
- DBSQL dashboard and query creation permission.
- For Unity Catalog demos: Unity Catalog metastore available (demo may install but not run otherwise).

## License and Support

dbdemos is provided as-is. Databricks does not offer official support. For issues, open a GitHub issue and mention the demo name. See the [dbdemos GitHub README](https://github.com/databricks-demos/dbdemos) for license and notices.

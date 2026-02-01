---
name: databricks-connect
description: Set up and use Databricks Connect for Python to run local code against Databricks compute. Covers installation, authentication, cluster or serverless configuration, and running PySpark from IDEs such as PyCharm or VS Code. Use when connecting a local IDE to Databricks, developing Spark apps locally, debugging against a remote cluster, or when the user mentions Databricks Connect, local development with Databricks, or running PySpark on Databricks from a laptop.
---

# Databricks Connect for Python

Databricks Connect lets you run Python and PySpark code from a local IDE (PyCharm, VS Code, Jupyter) against a Databricks cluster or serverless compute. Code executes on Databricks; your environment only needs the client and auth.


## When to Use This Skill

Use when the user needs to:
- Connect a local Python environment or IDE to a Databricks workspace
- Develop or debug Spark/PySpark code locally while execution runs on Databricks
- Set up Databricks Connect for the first time or fix connection issues
- Choose and configure cluster vs serverless for Databricks Connect

## Requirements (Summary)

**Workspace**: Unity Catalog must be enabled. Target compute must be a cluster (access mode Assigned or Shared) or serverless.

**Local**: Python 3.10+ (exact version depends on Databricks Connect and compute type). Authentication to Databricks must be configured (e.g. OAuth U2M via Databricks CLI).

**Version rule**: Databricks Connect package version must match or be compatible with the Databricks Runtime of the target cluster or serverless. See [references/REFERENCES.md](references/REFERENCES.md) for the compatibility table.

## Step-by-Step Setup

### 1. Activate a Virtual Environment

Use a dedicated venv or Poetry env for each Python version you use with Databricks Connect.

```bash
# Example with venv
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Remove Conflicting PySpark

Databricks Connect bundles and manages Spark; a separate PySpark install conflicts. Uninstall it first:

```bash
pip uninstall pyspark
```

### 3. Install Databricks Connect

Match the client version to your cluster or serverless runtime (e.g. 16.4 for DBR 16.4.x). Prefer a “latest patch” spec so you get compatible fixes:

```bash
# Replace 16.4 with your cluster/serverless runtime major.minor
pip install --upgrade "databricks-connect==16.4.*"
```

With Poetry, use the same version in `pyproject.toml` and `poetry add databricks-connect==16.4.*` (or `~16.4.0` for patch updates).

### 4. Configure Authentication

**OAuth user-to-machine (U2M)** is the typical option for interactive use. Use the Databricks CLI to log in and create a profile that includes cluster (or serverless) config:

```bash
databricks auth login --configure-cluster --host https://<workspace-name>.cloud.databricks.com
```

Follow the prompts to pick or create a cluster and save the profile. Databricks Connect will use this profile by default.

For CI or headless use, use OAuth M2M or other supported auth and set the same parameters via env vars or a config file. See [references/REFERENCES.md](references/REFERENCES.md) for links.

### 5. Point to Compute (Cluster or Serverless)

If you did not use `--configure-cluster`, or you want to override the default, set connection options explicitly.

**Cluster**: set `cluster_id` (or use the cluster ID from the profile).

**Serverless**: set serverless compute options (workspace, resource ID, etc.) as in the [compute configuration docs](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/cluster-config). Serverless is supported from Databricks Connect 15.1+; check version compatibility for your runtime.

### 6. Validate the Connection

```python
from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.getOrCreate()
spark.range(10).count()  # 10
```

If this runs without error, the client is talking to your Databricks compute.

## Common Code Patterns

### Create a Spark Session

```python
from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.getOrCreate()
```

### Use Unity Catalog Tables

```python
# Three-level namespace
df = spark.table("main.default.my_table")
# Or
df = spark.sql("SELECT * FROM main.default.my_table")
```

### Run SQL

```python
spark.sql("CREATE TABLE IF NOT EXISTS main.default.out AS SELECT 1 AS id")
```

### DataFrame API

Standard PySpark DataFrame API works; execution is on Databricks:

```python
df = spark.range(100).withColumn("double", F.col("id") * 2)
df.write.format("delta").mode("overwrite").saveAsTable("main.default.example")
```

## IDE and Tools

- **VS Code**: Use the Databricks extension; it can install and use Databricks Connect and add “Run on Databricks” for Python files.
- **PyCharm**: Configure the project interpreter to the venv where `databricks-connect` is installed; run scripts as usual—they use the session from `DatabricksSession.builder.getOrCreate()`.
- **Jupyter**: Install `databricks-connect` in the kernel’s environment and use `DatabricksSession` in notebooks.

## Edge Cases and Troubleshooting

| Issue | What to do |
|-------|------------|
| `PySpark` / “conflicting PySpark” errors | Ensure `pyspark` is uninstalled in the same env as `databricks-connect`. |
| “Cluster not found” or “invalid compute” | Check cluster exists, is running, and has access mode Assigned or Shared; confirm `cluster_id` or serverless config. |
| Version / “incompatible runtime” errors | Align Databricks Connect version with cluster/serverless runtime; use `pip show databricks-connect` and compare to [release notes](https://docs.databricks.com/aws/en/release-notes/dbconnect/). |
| Auth errors (e.g. “not authenticated”) | Run `databricks auth login --configure-cluster --host <workspace-url>` and rerun; for non-interactive, configure env vars or config for the chosen auth type. |
| Unity Catalog / permission errors | Confirm workspace has Unity Catalog enabled and the identity has required catalog/schema/table privileges. |
| UDFs behave differently or fail | Use a local Python minor version that matches the Databricks Runtime Python; see [references/REFERENCES.md](references/REFERENCES.md). |

## Best Practices

1. **One env per runtime**: Use a separate virtualenv per Databricks Runtime (or major.minor) you target.
2. **Version alignment**: Keep `databricks-connect==<major>.<minor>.*` in sync with cluster/serverless runtime.
3. **No standalone PySpark**: Do not install `pyspark` in the same environment as `databricks-connect`.
4. **Prefer serverless for ephemeral workloads**: If your workspace supports it, serverless can simplify “no cluster to manage” workflows; check compatibility for your Databricks Connect version.

For detailed requirements, version matrix, and official doc links, see [references/REFERENCES.md](references/REFERENCES.md).

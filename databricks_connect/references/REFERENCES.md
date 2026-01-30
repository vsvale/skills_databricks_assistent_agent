# Databricks Connect References

## Official Documentation

- **What is Databricks Connect**: https://docs.databricks.com/aws/en/dev-tools/databricks-connect/
- **Databricks Connect for Python (index)**: https://docs.databricks.com/en/dev-tools/databricks-connect/python/index.html
- **Usage requirements**: https://docs.databricks.com/aws/en/dev-tools/databricks-connect/requirements.html
- **Install Databricks Connect for Python**: https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/install.html
- **Compute configuration (cluster and serverless)**: https://docs.databricks.com/aws/en/dev-tools/databricks-connect/cluster-config.html
- **Tutorial: Run code from PyCharm on classic compute**: https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/tutorial-cluster.html
- **Tutorial: Run Python code on serverless compute**: https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/tutorial-serverless.html
- **Code examples for Databricks Connect for Python**: https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/examples.html
- **Troubleshooting**: https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/troubleshooting.html
- **Limitations**: https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/limitations.html
- **Databricks Connect release notes**: https://docs.databricks.com/aws/en/release-notes/dbconnect/
- **Migrate to Databricks Connect for Python (13.3 LTS+)**: https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/migrate.html

## Authentication

- **Databricks auth types**: https://docs.databricks.com/aws/en/dev-tools/auth/
- **OAuth user-to-machine (U2M)**: https://docs.databricks.com/aws/en/dev-tools/auth/oauth-u2m.html
- **OAuth machine-to-machine (M2M)**: https://docs.databricks.com/aws/en/dev-tools/auth/oauth-m2m.html
- **Databricks CLI**: https://docs.databricks.com/aws/en/dev-tools/cli/index.html

## VS Code and IDEs

- **Debug code using Databricks Connect (VS Code extension)**: https://docs.databricks.com/aws/en/dev-tools/vscode-ext/databricks-connect.html

## Version Compatibility (Summary)

Databricks Connect version numbers align with Databricks Runtime. The client version must be compatible with the cluster or serverless runtime you use. Check the [requirements](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/requirements.html) page for the full table. Examples:

- **16.4.x and above (cluster)**: Python 3.12
- **15.4.x (cluster)**: Python 3.11
- **13.3.x and 14.3.x (cluster)**: Python 3.10

Serverless support and required Python versions depend on the serverless version and Databricks Connect release; see the official compatibility table.

For UDFs, the local Python minor version should match the Databricks Runtime Python; see [Python base environment](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/udf#base-env).

## Example Repositories

- **dbconnect-examples** (Databricks): https://github.com/databricks-demos/dbconnect-examples
  - Simple ETL application
  - Plotly-based interactive apps
  - Plotly + PySpark AI

## PyPI

- **databricks-connect**: https://pypi.org/project/databricks-connect/

## Best Step by step video
- https://www.youtube.com/watch?v=Ii2LuEJ0gpc
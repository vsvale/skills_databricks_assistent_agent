# References: Read Files from Volumes and Workspace

## Official docs

- [JSON file](https://docs.databricks.com/aws/en/query/formats/json) – single-line vs multi-line, options, rescued data column
- [Query JSON strings (semi-structured)](https://docs.databricks.com/aws/en/semi-structured/json) – `column:path`, `::type`, `from_json`
- [Work with files on Databricks](https://docs.databricks.com/aws/en/files/) – Volumes, workspace, cloud storage, path conventions
- [Programmatically interact with workspace files](https://docs.databricks.com/aws/en/files/workspace-interact) – paths, CWD, reading with Spark/pandas
- [PySpark DataFrameReader.json](https://api-docs.databricks.com/python/pyspark/latest/pyspark.sql/api/pyspark.sql.DataFrameReader.json.html)
- [parse_json (Databricks SQL)](https://docs.databricks.com/gcp/en/sql/language-manual/functions/parse_json)

## Path summary

| Location   | PySpark / SQL path |
|-----------|--------------------|
| Volume   | `/Volumes/{catalog}/{schema}/{volume}/path` |
| Workspace (user) | `file:/Workspace/Users/<user-folder>/path` |
| Workspace (repo) | `file:/Workspace/Repos/<user>/<repo>/path` |

Use the `file:` scheme for workspace paths when using Spark or SQL.

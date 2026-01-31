# read_json_workspace.py
# Examples: Read JSON from Databricks workspace via PySpark.
# Use file:/ scheme and full path for Spark. In repo-backed notebooks, os.getcwd() is often the repo root.

import os

# --- From repo-relative path (notebook in a repo) ---
# CWD is typically the directory containing the notebook (e.g. repo root)
relative_path = "data/events.json"
full_path = f"file:{os.getcwd()}/{relative_path}"
sdf = spark.read.json(full_path)


# --- From explicit workspace user path ---
# Replace <user-folder> with your workspace user folder (e.g. user@domain.com)
user_folder = "user@domain.com"
path = f"file:/Workspace/Users/{user_folder}/data/events.json"
sdf = spark.read.format("json").load(path)


# --- From workspace Repos path ---
# Format: file:/Workspace/Repos/<user-folder>/<repo-name>/path/to/file.json
repo_path = f"file:/Workspace/Repos/{user_folder}/my_repo/data/sample.json"
sdf_repo = spark.read.option("multiline", "true").format("json").load(repo_path)


# --- Multi-line JSON from workspace ---
sdf_ml = (
    spark.read
    .option("multiline", "true")
    .format("json")
    .load(f"file:{os.getcwd()}/data/config.json")
)

sdf_ml.show(5, truncate=False)

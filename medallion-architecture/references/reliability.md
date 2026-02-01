# Reliability & Disaster Recovery for the Lakehouse

## Core Principles

1.  **Design for Failure**: Assume jobs, queries, and infrastructure will fail. Build automated recovery.
2.  **Data Integrity**: Use ACID transactions (Delta Lake) and enforcing schemas to prevent corruption.
3.  **Horizontal Scalability**: Use distributed computing that scales out (e.g., Spark) rather than up.
4.  **Automated Recovery**: Retry transient errors automatically and use Time Travel to revert logical errors.

## Best Practices

### 1. Data Processing Reliability
*   **ACID Transactions**: Always use **Delta Lake** to ensure writes are atomic. If a job fails mid-write, the table remains in a consistent state.
*   **Schema Enforcement**: Use `schema evolution` carefully. Enforce strict schemas in Silver/Gold to prevent bad data from breaking downstream apps.
*   **Structured Streaming**: Use checkpointing to ensure exactly-once processing and fault tolerance.

### 2. Job & Pipeline Reliability
*   **Retries**: Configure automatic retries on Databricks Jobs (e.g., "Retry 3 times on failure").
*   **Delta Live Tables (DLT)**: Use DLT for complex pipelines—it handles dependency resolution, checkpoints, and retries automatically.
*   **Time Travel**: Use `RESTORE TABLE my_table TO VERSION AS OF ...` to undo accidental deletes or bad writes.

### 3. Data Quality as Reliability
*   **Expectations**: Define "must-have" (FAIL) vs. "should-have" (WARN) constraints.
*   **Quarantine**: Redirect bad records to a "quarantine table" instead of failing the whole batch (`rescued_data_column` in Auto Loader).

### 4. Disaster Recovery (DR)
*   **Deep Clone**: Use `CREATE TABLE ... DEEP CLONE` to replicate critical Gold tables to a secondary region for DR.
*   **Version Control**: Keep all pipeline code in Git. You cannot recover code from a deleted workspace if it wasn't versioned.

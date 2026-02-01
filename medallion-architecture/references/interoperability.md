# Interoperability and Usability

## Core Principles

1.  **Open Interfaces & Formats**: Use open standards (Delta Lake, Parquet) to ensure data is accessible by any tool, future-proofing the architecture.
2.  **Standards for Integration**: Define reusable patterns for ingestion and sharing to reduce complexity.
3.  **Simplified Implementation**: Enable self-service with serverless compute and AI-assisted tools.
4.  **Consistency**: Publish trusted "Data Products" with semantically consistent definitions across the enterprise.

## Best Practices

### 1. Leverage Open Standards
*   **Storage**: Store all data in **Delta Lake** (open source protocol) on cloud object storage. Avoid proprietary formats that lock data into a specific vendor.
*   **Compute**: Use standard APIs (Spark, SQL, Python) that are widely supported.
*   **ML**: Manage models with **MLflow** for an open, reproducable lifecycle.

### 2. Integration Patterns
*   **Ingestion**: Use **Auto Loader** for file-based ingestion and **Lakeflow Connect** for SaaS/Database sources.
*   **External Access**: Use **Delta Sharing** to securely share live data with partners without copying or complex ETL.
*   **Multi-Cloud**: Design for portability by abstracting storage and compute where possible.

### 3. Usability & Productivity
*   **Multi-Language**: Support diverse persona skills (SQL for analysts, Python for data scientists, Scala for engineers) on the same data.
*   **Serverless**: Use Serverless SQL Warehouses and Compute to remove infrastructure management overhead.
*   **AI Assistants**: Utilize Databricks Assistant to generate code, fix errors, and explain complex data lineage.

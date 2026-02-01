# Security, Compliance, & Privacy

## Core Principles

1.  **Unified Identity**: Single identity provider (IdP) sync for all data and AI assets.
2.  **Least Privilege**: Access granted only as needed, at the lowest possible level (Schema/Table).
3.  **Data Protection**: Encryption at rest and in transit; dynamic masking for sensitive PII.
4.  **Network Isolation**: Secure connectivity between the control plane and data plane.

## Best Practices

### 1. Identity & Access Management (IAM)
*   **Centralized Identity**: Sync users/groups from Entra ID/Okta to Databricks Account.
*   **Service Principals**: Use SCIM-provisioned Service Principals for all automated jobs/pipelines.
*   **Unity Catalog**: Manage permissions (`GRANT SELECT`) on catalog, schema, or table. Avoid per-file or per-bucket policies.

### 2. Data Protection
*   **Dynamic View Masking**: Use column masks for PII:
    ```sql
    CREATE FUNCTION mask_ssn(val STRING) RETURNS STRING 
    RETURN CASE WHEN is_member('admin') THEN val ELSE '***-**-****' END;
    ```
*   **Encryption**: Ensure storage accounts (S3/ADLS/GCS) use customer-managed keys (CMK) if compliance requires.

### 3. Network Security
*   **Private Connectivity**: Use PrivateLink to disable public internet access to workspaces.
*   **IP Access Lists**: Restrict API and UI access to trusted corporate IP ranges.
*   **Cluster Policies**: Enforce `enable_elastic_disk_encryption=true` and prevent public IPs on worker nodes.

### 4. Monitoring
*   **Audit Logs**: Stream verbose audit logs to a dedicated Gold table for security analysis.
*   **Lineage**: Use Unity Catalog Lineage to trace PII data usage across models and dashboards.

# Data and AI Governance with Unity Catalog

## Core Principles

Effective governance in the Lakehouse unifies data and AI assets under a single control plane:

1.  **Unified Management**: Manage tables, files (Volumes), ML models, features, and dashboards in one catalog.
2.  **Unified Security**: Centralize access control (Grant/Revoke) across all workspaces and clouds.
3.  **Data Quality**: Enforce standards at every layer (Bronze/Silver/Gold) to ensure trust.

## Best Practices

### 1. Unify Data and AI Management
*   **Central Catalog**: Use Unity Catalog as the single source of truth.
*   **Metadata Management**: Tag assets with ownership (`owner`), sensitivity (`PII`), and business context.
*   **Lineage**: Enable automated lineage tracking to see how data flows from Bronze to Gold and which models consume it.

### 2. Centralize Identity & Access
*   **Account-Level Identities**: Sync users/groups from your IdP (e.g., Azure Entra ID, Okta) to the Databricks Account, then assign to workspaces.
*   **Least Privilege**: Grant access at the Group level, not User level.
    *   *Data Engineers*: `MODIFY` on Bronze/Silver.
    *   *Data Scientists*: `READ` on Silver, `CREATE` on MLflow experiments.
    *   *Analysts*: `READ` on Gold.

### 3. Establish Data Quality Standards
*   **Profiling**: Regularly profile data to understand distribution and anomalies.
*   **Validation**: Use Delta Live Tables (DLT) expectations or custom assertions in Silver layer.
    *   `EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW`
*   **Monitoring**: Alert on quality failures or schema drift.

### 4. Audit & Compliance
*   **Audit Logging**: Enable verbose audit logs for all access and modification events.
*   **System Tables**: Query `system.access.audit` to monitor usage patterns and security vioations.

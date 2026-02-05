# Tagging Standards

## Mandatory Tags
All jobs must include these tags for FinOps and Governance.

| Tag | Description | Example Values |
|-----|-------------|----------------|
| **BU** | Business Unit | `ECS`, `CORP`, `DATABRICKS` |
| **BusinessServices** | Product/Team | `CRM`, `AUTH`, `ANALYTICS`, `PREMIUM` |
| **Environment** | Execution Environment | `PRD` |
| **CreatedBy** | Monitoring Team | `DATAOPS`, `CRM`, `DATASCIENCE` |
| **JobType** | Workload Type | `ETL`, `SELF_SERVICE`, `DLT`, `MAINTENANCE_JOB` |
| **Data_Category** | Importance | `ALTA`, `MEDIA`, `BAIXA` |
| **datadog** | Monitor in Datadog | `TRUE`, `FALSE` |

## Job JSON Example
```json
"tags": {
  "BU": "ECS",
  "datadog": "TRUE",
  "BusinessServices": "BOX",
  "Environment": "PRD",
  "CreatedBy": "ANALYTICS",
  "JobType": "ETL",
  "Data_Category" : "BAIXA"
}
```

## Optional Tags
- **RunName**: Recommended for All Purpose clusters.
- **UserEmail**: Required for High Performance Self Service jobs.

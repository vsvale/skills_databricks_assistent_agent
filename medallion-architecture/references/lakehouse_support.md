# Lakehouse Guiding Principles and Personas

## Guiding Principles

### 1. Curate Data as Products
Treat data assets as products with clear definitions, schemas, and lifecycles. 
- **Validation**: Validate data quality at entry to the curated (Silver) layer.
- **Trust**: Ensure quality improves from layer to layer.
- **Semantics**: Maintain semantic consistency so business concepts are uniform across the organization.

### 2. Eliminate Data Silos
Avoid creating disconnected copies of datasets.
- **Single Source of Truth**: Downstream products should depend on the central Lakehouse layers, not standalone copies.
- **Secure Sharing**: Use Unity Catalog and Delta Sharing for enterprise-wide access instead of copying data to separate buckets or systems.

### 3. Democratize Value Creation
Empower diverse data teams to collaborate on a single platform.
- **Unified Platform**: Support SQL, Python, Scala, and R workloads on the same data.
- **Self-Service**: Enable analysts and engineers to discover data via Catalog Explorer without effective bottlenecks.

---

## Operations & Governance

### Collaboration & Discovery
- **Catalog Explorer**: Use for discovering datasets, reviewing schema/comments, and tracing lineage.
- **Unified Permissions**: Manage permissions centrally via Unity Catalog to ensure consistent access control across workspaces.
- **Storage Credentials**: Allow data engineers to self-service external locations without needing direct cloud IAM roles.

### Platform Personas
Understanding who interacts with each layer helps in designing appropriate access controls and data models.

| Persona | Primary Focus | Interaction Layer |
|---------|---------------|-------------------|
| **Data Engineers** | Reliability, Consistency, ETL | **Bronze & Silver** (Write), Gold (Support) |
| **Data Scientists** | Predictive Models, Insights | **Silver** (Read), Gold (Read/Write) |
| **ML Engineers** | Model Scalability, Operations | **Silver & Gold** (Read), Feature Stores |
| **Business Analysts** | Actionable Reporting, Dashboards | **Gold** (Read), BI Tools |
| **Apps Developers** | Secure Data Applications | **Gold** (Read via APIs) |

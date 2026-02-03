# Preface

Since its introduction in 2021, **Unity Catalog** has become a foundational component of the **Databricks Data Intelligence Platform**.

Unity Catalog provides native support for:
- **Delta** and **Iceberg** catalogs and tables via REST
- **Views**
- **Cloud storage files**
- **AI models**
- **Functions**

As a result, Unity Catalog functions as a **truly multimodal catalog**, delivering a unified experience for **data governance, discovery, and management** across the platform.

Unity Catalog is now **open source**, reinforcing its role as an open standard for managing data and analytical assets.

---

# Prologue

A **data lake** is a centralized repository designed to store large volumes of data in its **raw, native format**.

Key characteristics of a data lake include:
- A **flat architecture**
- Use of **object storage** as the primary storage layer
- Support for **structured, semi-structured, and unstructured data**

- A data lake serves as the foundation for large-scale analytics, machine learning, and advanced data processing workloads.

- The organization had to comply with diverse regulatory requirements, including **GDPR, CCPA, and PCI DSS**. This required implementing different data governance policies and procedures for each region, significantly increasing operational complexity and cost.

- A **central data platform (CDP) team**, organized in a **hub-and-spoke model**, actively managed data ingestion and transformation across all enterprise datasets. The team was responsible for access control and for building shared **frameworks, tools, and blueprints** for data ingestion and transformation, which domain teams could follow to ensure consistency, quality, and compliance.

- **Domain teams** focused on their specific business responsibilities, while **data analysts** consumed curated datasets and created **business intelligence (BI)** assets.
- Multicloud data platform enable to scale the data platform in line with its fast-growing business and the associated data
- Apache Spark is an open source multilanguage data processing engine used for data engeneering, data science and machine learning. It can handle both batches anb real-time streaming analytics, SQL and ML workloads
- Siloed data platforms—where data is repeatedly replicated between a data lake and a cloud data warehouse—increase complexity, cost, and operational overhead. Solution: adopt a lakehouse platform that unifies analytics, BI, and machine learning on a single data architecture.
- Databricks: unified platform that supports AI, ML, data warehuseing and streaming applications
- data in a lakehouse is stored in an open file format: Delta or Iceberg

## Problems in a data platform
- **Proper data governance**
- Struggled to balance data democratization with stringent access controls and governance standards
- Needed to protect sensitive data and ensure regulatory compliance while enabling timely, data-driven decisions
- Lacked mechanisms for secure and responsible data sharing
- Poor visibility into available data sources, leading to data reloading and redundancy
- Limited data lineage made it difficult to trace data origins and transformations
- Absence of centralized management and auditing resulted in scattered and unaccounted data

- **Central platform team as a bottleneck**
- The domain teams rely heavily on platform team to make data avaiable for consumptio, slowing the new initiatives
- By adopting a decentralized plataform strategy is possible to adopt the data mesh architecture, which provided domain teams with the autonomy to manage their own data and work independently

## Unity Catalog
- Unity Catalog became generally avaible in 2022
- is a data governance solution from Databricks that uniufies data and Ai asset governance and enables enhanced data sharing and access control capabilities

# The Modern  Governance Stack
## Data Governance
- Amazon S3 bucket misconfiguration led to exposure of a significant amount of sensitive data
- "human error" to be the main cause of cyber security incidents
- zero-trust security model: humans will make mistakes, so we need to make it much harder for them to make mistakes and put in guardrails to minimize the impact of those mistakes when they inevitably happen
- Data Governance: is acomprehensive approach to managing an organization's data to ensure its availability, usabilityh, quality, integrity, and security throughout its lifecycle
- Key components of data governance:
  - Policies and standards
  - Data quality management
  - Metadata management
  - Access controls and security measures
  - Data lifecycle management and lineage tracking
  - Auditing and compliance monitoring
- Benefits of data governance:
  - Clear and comprehensive policies and controls for managing data throughout its lifecycle
  - Strong access controls and authentication procedures to ensure only authorized personal can access data and related assets
  - Enforce data classification and risk assessment to identify and prioritizae the protection of high-risk data assets
  - Establish data handling policies or guidelines thatr specify how data should be stored, processed, transmitted and disposed of securely
  - Require security measures like encryption, use of firewalls, and intrusion detection systems
  - Implement data minimization practicies to reduce the overwall attack surface and potential impact of a breach
  - Enforce regular security audits and risk assessments to identify and proactively address potential vulnerabilities
  - Establish incident response plans
  - Create accountability for data security across the organization by defining clear roles and responsibilities for data management
  - Improved data quality and reliability
  - Enhanced regulatory compliance
  - Better decision making based on trusted data
  - Increased operation efficiency
  - Reduced data management cost
  - Greater trust from consumers
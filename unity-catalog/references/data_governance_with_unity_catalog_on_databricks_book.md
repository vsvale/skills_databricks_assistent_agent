# Preface

## Unity Catalog Overview
Introduced in **2021**, **Unity Catalog** is a foundational component of the **Databricks Data Intelligence Platform**.

## Supported Asset Types
Unity Catalog provides native, REST-based support for managing:
- **Delta** catalogs and tables
- **Iceberg** catalogs and tables
- **Views**
- **Cloud storage files**
- **AI models**
- **Functions**

## Functional Role
Unity Catalog operates as a **multimodal catalog**, enabling:
- Unified data governance
- Centralized asset discovery
- Consistent management of analytical and AI assets

This unified approach spans multiple asset types and workloads within the Databricks platform.

## Open Source Status
Unity Catalog is **open source**, positioning it as:
- An open standard for data and analytics governance
- A shared foundation for managing data, AI, and analytical assets across organizations

# Prologue

## Data Lake Definition
A **data lake** is a centralized repository designed to store large volumes of data in its **raw, native format**, without enforcing a predefined schema at ingestion time.

### Key Characteristics
- **Flat architecture** (minimal hierarchical constraints)
- **Object storage** as the primary storage layer
- Native support for:
  - Structured data
  - Semi-structured data
  - Unstructured data

### Purpose
A data lake serves as the foundational layer for:
- Large-scale analytics
- Machine learning workloads
- Advanced data processing and experimentation

## Regulatory and Governance Context
The organization operated under multiple regulatory regimes, including:
- **GDPR**
- **CCPA**
- **PCI DSS**

Implications:
- Region-specific data governance policies
- Distinct compliance procedures per regulation
- Increased operational complexity and cost due to regulatory fragmentation

## Organizational Model

### Central Data Platform (CDP) Team
- Structured under a **hub-and-spoke model**
- Responsibilities:
  - Managing enterprise-wide data ingestion
  - Executing and standardizing data transformations
  - Enforcing access control and security policies
  - Developing shared **frameworks, tools, and blueprints** for ingestion and transformation
- Objective:
  - Ensure consistency, data quality, and regulatory compliance across domains

### Domain Teams
- Accountable for domain-specific business logic and data ownership
- Follow CDP-provided standards and blueprints

### Data Analysts
- Consume curated and governed datasets
- Produce **business intelligence (BI)** assets and insights


## Data Lifecycle

### 1. Onboarding
The phase in which data is **collected, generated, or ingested** into a system.
- Sources may include applications, sensors, logs, external providers, or user input.
- The goal is to make data available for downstream processing.

### 2. Processing
The phase focused on **improving data usability, quality, and consistency**.
Typical operations include:
- Filtering and cleaning
- Handling missing or unavailable values
- Joins and merges across datasets
- Aggregation
- Anonymization

Key processing concepts:
- **Entity Resolution**: Identifying records that refer to the same real-world entity and merging them into a single representation.
- **Data Harmonization**: Unifying and consolidating data from multiple sources into a coherent, standardized format.
- **Aggregation as Value**: In some cases, the primary value of data lies in its aggregated form; once aggregates are computed and stored, raw source data may be safely discarded.
- **Anonymization**: Transforming sensitive data (e.g., Personally Identifiable Information – PII) to prevent identity disclosure while preserving analytical or product utility.

### 3. Active Duty
The phase in which data is **actively used for a specific purpose**, such as:
- Analytics and reporting
- Machine learning models
- Decision-making processes
- Data products and services

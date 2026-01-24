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

A data lake serves as the foundation for large-scale analytics, machine learning, and advanced data processing workloads.

- The organization had to comply with diverse regulatory requirements, including **GDPR, CCPA, and PCI DSS**. This required implementing different data governance policies and procedures for each region, significantly increasing operational complexity and cost.

- A **central data platform (CDP) team**, organized in a **hub-and-spoke model**, actively managed data ingestion and transformation across all enterprise datasets. The team was responsible for access control and for building shared **frameworks, tools, and blueprints** for data ingestion and transformation, which domain teams could follow to ensure consistency, quality, and compliance.

- **Domain teams** focused on their specific business responsibilities, while **data analysts** consumed curated datasets and created **business intelligence (BI)** assets.

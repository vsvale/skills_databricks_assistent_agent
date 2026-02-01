# Medallion Architecture References

## Official Databricks Documentation

### Core Concepts
- [Medallion Architecture Overview](https://docs.databricks.com/aws/en/lakehouse/medallion)
- [Building the Medallion Architecture with Delta Lake (Delta.io)](https://delta.io/blog/delta-lake-medallion-architecture/)
- [What is Medallion Architecture and How to Implement it (Dateonic)](https://dateonic.com/what-is-medallion-architecture-in-databricks-and-how-to-implement-it/)
- [Why Data Layers Matter (Databricks Community)](https://community.databricks.com/t5/community-articles/the-medallion-architecture-why-data-layers-matter-for-modern/td-p/140825)
- [Well-Architected Framework: Seven Pillars](https://docs.databricks.com/aws/en/lakehouse-architecture/well-architected)
- [Lakehouse Reference Architecture](https://docs.databricks.com/aws/en/lakehouse-architecture/reference)
- [Data Engineering Best Practices](https://docs.databricks.com/aws/en/data-engineering/index.html)
- [Medallion Architecture in Databricks: A Complete Guide (Medium)](https://medium.com/towards-data-engineering/medallion-architecture-in-databricks-a-complete-guide-with-delta-lake-d78f49ce5cd3)
- [How Databricks Empowers Scalable Data Products (Databricks Community)](https://community.databricks.com/t5/community-articles/how-databricks-empowers-scalable-data-products-through-medallion/td-p/108977)
- [Medallion Architecture (Data Engineering Wiki)](https://dataengineering.wiki/Concepts/Data+Architecture/Medallion+Architecture)
- [Medallion Architecture Blog (Chaos Genius)](https://www.chaosgenius.io/blog/medallion-architecture/)
- [Gold Layer Design Best Practices (DevOps.dev)](https://blog.devops.dev/databricks-gold-layer-design-best-practices-explained-cd0f7852a806)

### Architectural Pillars (Deep Dives)
- [Cost Optimization Principles & Best Practices](https://docs.databricks.com/aws/en/lakehouse-architecture/cost-optimization/)
- [Data and AI Governance Principles & Best Practices](https://docs.databricks.com/aws/en/lakehouse-architecture/data-governance/)
- [Interoperability and Usability Principles & Best Practices](https://docs.databricks.com/aws/en/lakehouse-architecture/interoperability-and-usability/)
- [Operational Excellence Principles & Best Practices](https://docs.databricks.com/aws/en/lakehouse-architecture/operational-excellence/)
- [Performance Efficiency Principles & Best Practices](https://docs.databricks.com/aws/en/lakehouse-architecture/performance-efficiency/)
- [Reliability Principles & Best Practices](https://docs.databricks.com/aws/en/lakehouse-architecture/reliability/)
- [Security, Compliance, and Privacy Principles & Best Practices](https://docs.databricks.com/aws/en/lakehouse-architecture/security-compliance-and-privacy/)

### Features & Implementation
- [Delta Lake: The Definitive Guide](https://www.databricks.com/resources/ebook/delta-lake-the-definitive-guide)
- [Liquid Clustering](https://docs.databricks.com/delta/clustering.html)
- [Unity Catalog Overview](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [Structured Streaming](https://docs.databricks.com/structured-streaming/index.html)
- [Delta Live Tables Expectations](https://docs.databricks.com/workflows/delta-live-tables/delta-live-tables-expectations.html)

---

## Internal Skill Guides

For detailed implementation guidelines and specialized patterns, refer to the following internal documents:

- [Lakehouse Reference & Well-Architected](well_architected.md) - Architectural blueprints and personas.
- [Data and AI Governance](governance.md) - Unified governance with Unity Catalog.
- [Security & Compliance](security.md) - IAM, network, and data protection.
- [Reliability & DR](reliability.md) - ACID, time travel, and resilience.
- [Performance Efficiency](performance.md) - Serverless, Photon, and clustering.
- [Cost Optimization](cost_optimization.md) - Budget policies and spot instances.
- [Operational Excellence](operational_excellence.md) - CI/CD and monitoring.
- [Interoperability & Usability](interoperability.md) - Open standards and personas.
- [Common Anti-Patterns](anti_patterns.md) - Mistakes to avoid at each layer.
- [Medallion and Data Products](data_products.md) - Medallion as a foundation for Data Products.
- [Storage & Compute Management](storage_management.md) - Optimization and lifecycle patterns.

---

## External Community Resources
- [Databricks Blog](https://www.databricks.com/blog)
- [Databricks Academy](https://www.databricks.com/learn/training)
- [GitHub: Delta Lake](https://github.com/delta-io/delta)

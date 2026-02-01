# Medallion as a Foundation for Data Products

The Medallion architecture provides the structural discipline required to treat data as a high-quality, reusable product rather than just a byproduct of business processes.

## The Data Product Lifecycle

The Medallion layers map directly to the lifecycle of a **Data Product**:

1.  **Discovery (Bronze)**: Initial availability of raw data. While not yet a "product," it is the raw material for all subsequent products.
2.  **Trust (Silver)**: This is where "Core Data Products" are born. They are cleansed, deduplicated, and conformed to enterprise standards, making them high-trust assets for the entire organization.
3.  **Consumption (Gold)**: "Consumer Data Products" are created by joining and aggregating Core products into domain-specific datasets optimized for BI and ML.

## Key Characteristics of Medallion Data Products

To meet the definition of a "Data Product," each layer should ensure:

| Characteristic | Medallion Implementation |
| :--- | :--- |
| **Addressable** | Unity Catalog provides a unique 3-level namespace (`catalog.schema.table`). |
| **Trustworthy** | Silver/Gold layers enforce data quality through **Expectations**. |
| **Self-Describing** | Use **Table Comments** and **AI-generated metadata** in Catalog Explorer. |
| **Interoperable** | Open standard (Delta Lake/Parquet) ensures data can be used across languages. |
| **Observable** | Lakehouse Monitoring provides automated DQ and volume tracking. |
| **Secure** | Identity-based access control and row/column filters at the Gold layer. |

## Governance Standards

- **Ownership**: Every Silver and Gold table must have a clear `OWNER` (Group or Service Principal).
- **Versioning**: Leverage Delta Lake **Time Travel** to maintain product versions and allow for easy rollbacks.
- **Lineage**: Automated column-level lineage in Unity Catalog ensures consumers know where the data originated.

## Core vs. Consumer Products

- **Core Products (Silver)**: Broadly applicable entities (e.g., `customers`, `products`, `orders`). Highly normalized and managed by central data engineering teams.
- **Consumer Products (Gold)**: Aggregated snapshots or specialized views (e.g., `monthly_churn_summary`, `personalized_offers`). Managed by decentralized domain teams.

For further reading on product-centric governance, see [governance.md](governance.md).

# Compute Requirements

## Cluster Modes
To interact with Unity Catalog, clusters must use **Standard** or **Dedicated** access modes.

### Standard (Shared)
- **Use Case**: General purpose, interactive, most jobs.
- **Limitations**:
  - No RDD APIs.
  - No Hive UDFs.
  - No Spark Context (`sc`).
  - No ML Runtime support (use Dedicated for ML).
  - No Structured Streaming `continuous` processing mode.

### Dedicated (Single User)
- **Use Case**: Machine Learning, RDD-heavy workloads, Legacy code requiring high privileges.
- **Features**: Full isolation, supports ML Runtime.

## Error Handling
- **Error**: `[UC_NOT_ENABLED]`
  - **Fix**: Switch cluster mode from "No Isolation" (Legacy) to "Standard" or "Dedicated".

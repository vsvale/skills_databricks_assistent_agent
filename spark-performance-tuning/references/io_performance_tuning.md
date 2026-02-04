# I/O Performance Tuning

I/O performance is often the primary bottleneck in data processing pipelines. When jobs run slowly despite low CPU and memory utilization, I/O is usually the culprit.

## The I/O Bottleneck

Input/Output operations are typically **100 to 1000 times slower** than memory operations. In a cloud environment, this is exacerbated by network latency to object storage (S3, ADLS, GCS).

### Symptoms of I/O Bound Jobs
- **Low CPU Utilization**: Executors are waiting for data rather than processing it.
- **Long Durations**: Simple transformations take disproportionately long.
- **High "Wait" Times**: Spark UI shows significant time in scan/read stages.

## The Small File Problem

The most common cause of poor I/O performance is the "Small File Problem".
- **Metadata Overhead**: Every file requires API calls (List, Get, Head) to cloud storage.
- **Latency**: Opening/closing thousands of small files (<64MB) dominates execution time.
- **Impact**: A table with 50,000 small files (1-5MB each) can be **10x slower** to read than the same data in 400 optimally sized files (128MB-256MB).

## Optimization Strategies

### 1. File Size Optimization
- **Goal**: Target file sizes between **128MB and 1GB** (depending on table size).
- **Mechanism**: Use `OPTIMIZE` to compact small files.
- **Prevention**: Enable Auto Compaction and Optimized Writes to prevent small files during ingestion.

### 2. Data Skipping
- **Concept**: Use file-level metadata (min/max values) to skip reading entire files that don't match query filters.
- **Mechanism**: 
    - **Z-Ordering**: Co-locates related data to maximize skipping effectiveness.
    - **Liquid Clustering**: Automatically clusters data without manual Z-Ordering.

### 3. Disk Cache (formerly Delta Cache)
- **Concept**: Stores frequently accessed data on local SSDs of worker nodes.
- **Benefit**: Eliminates network round-trips to cloud storage for repeated reads.
- **Usage**: Enabled by default on supported instance types (e.g., L series in Azure, i3 in AWS).

### 4. Network & Shuffle
- **Shuffle**: Moving data between nodes is expensive. Minimize shuffle with Broadcast Joins where possible.
- **Spill**: Ensure partitions fit in memory to avoid spilling to disk (which turns memory ops into I/O ops).

## Troubleshooting Checklist

1.  **Check File Sizes**: `DESCRIBE DETAIL table_name` to see `numFiles` and `sizeInBytes`. If `sizeInBytes / numFiles` < 64MB, run `OPTIMIZE`.
2.  **Monitor Spark UI**: Look for stages with high "Scan" time or "Shuffle Write" time.
3.  **Verify Caching**: Ensure Disk Cache is active if re-reading data (check "Storage" tab).

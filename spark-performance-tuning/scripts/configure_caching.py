from pyspark.sql import SparkSession

def configure_disk_cache(spark: SparkSession, enabled: bool = True, max_disk_usage: str = None):
    """
    Configures the Databricks Delta Cache (Disk Cache).
    
    Args:
        spark: SparkSession object.
        enabled: Enable or disable the cache.
        max_disk_usage: Max disk space to use (e.g., "50g"). None uses default.
    """
    
    # Enable/Disable Disk Cache
    spark.conf.set("spark.databricks.io.cache.enabled", str(enabled).lower())
    
    if enabled:
        # Optional: Configure max disk usage per node
        if max_disk_usage:
            spark.conf.set("spark.databricks.io.cache.maxDiskUsage", max_disk_usage)
            
        # Optional: Cache data that is accessed at least once (default is usually higher)
        # spark.conf.set("spark.databricks.io.cache.maxFileSize", "2147483647") 
    
    print(f"Disk Cache Enabled: {enabled}")

def clear_cache(spark: SparkSession):
    """Clears both Spark Cache (Memory) and Delta Cache (Disk)."""
    spark.catalog.clearCache()
    print("Spark Cache cleared.")
    
    # Note: There is no direct SQL command to clear only Delta Cache globally, 
    # but restarting the cluster or clearing specific files works.
    # This command clears the Spark-level cache.

if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    configure_disk_cache(spark, enabled=True)

from pyspark.sql import SparkSession

def set_performance_defaults(spark: SparkSession):
    """
    Sets recommended Spark configurations for Databricks performance.
    
    NOTE: Most of these configurations are NOT supported in Serverless Compute.
    In Serverless, the platform manages these settings automatically.
    """
    # Auto-optimize writes and tune for rewrites (MERGE/DML intensive)
    spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
    spark.conf.set("spark.databricks.delta.autoOptimize.autoCompact.enabled", "true")
    spark.conf.set("spark.databricks.delta.properties.defaults.tuneFileSizesForRewrites", "true")

    # Recommend Row Tracking and Deletion Vectors for all new tables
    spark.conf.set("spark.databricks.delta.properties.defaults.enableRowTracking", "true")
    spark.conf.set("spark.databricks.delta.properties.defaults.enableDeletionVectors", "true")

    # Adjust broadcast threshold if necessary (default 10MB)
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")

if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    set_performance_defaults(spark)
    print("Performance defaults set.")

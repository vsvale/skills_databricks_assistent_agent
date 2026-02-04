import pyspark
from pyspark.sql import SparkSession

def check_performance_configs():
    """Prints current Spark performance configurations and recommendations."""
    spark = SparkSession.builder.getOrCreate()
    
    configs = [
        "spark.sql.adaptive.enabled",
        "spark.sql.adaptive.coalescePartitions.enabled",
        "spark.sql.adaptive.skewJoin.enabled",
        "spark.sql.autoBroadcastJoinThreshold",
        "spark.databricks.delta.optimizeWrite.enabled",
        "spark.databricks.delta.autoOptimize.autoCompact.enabled"
    ]
    
    print("--- Spark Performance Configuration Audit ---")
    for cfg in configs:
        val = spark.conf.get(cfg, "NOT SET")
        print(f"{cfg}: {val}")
    
    # Recommendations
    print("\n--- Recommendations ---")
    if spark.conf.get("spark.sql.adaptive.enabled") == "false":
        print("[!] Warning: AQE is explicitly disabled. It is highly recommended to enable it for optimal performance.")
    
    if int(spark.conf.get("spark.sql.autoBroadcastJoinThreshold", "0")) < 10485760:
         print("[i] Note: Broadcast threshold is low. Consider increasing if executors have enough memory.")

if __name__ == "__main__":
    check_performance_configs()

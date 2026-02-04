from pyspark.sql import DataFrame

def repartition_to_128mb(df: DataFrame) -> DataFrame:
    """
    Repartitions a DataFrame to target 128MB per partition.
    Formula: max(1, df.count() // (128 * 1024 * 1024))
    
    Args:
        df: The input DataFrame.
        
    Returns:
        DataFrame: Repartitioned DataFrame.
    """
    # Note: df.count() triggers a job. Use with caution on very large datasets if count is not cached.
    target_size_bytes = 128 * 1024 * 1024
    num_partitions = int(max(1, df.count() // target_size_bytes))
    return df.repartition(num_partitions)

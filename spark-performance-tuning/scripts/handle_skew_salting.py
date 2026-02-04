from pyspark.sql import DataFrame
from pyspark.sql import functions as F

def salted_join(df_skew: DataFrame, df_small: DataFrame, join_key: str, salt_factor: int = 10) -> DataFrame:
    """
    Performs a salted join to handle data skew.
    
    Strategy:
    1. Add a random salt (0 to salt_factor-1) to the skewed dataframe.
    2. Replicate rows in the small dataframe (0 to salt_factor-1).
    3. Join on [join_key, salt].
    4. Drop the salt column.
    
    Args:
        df_skew: The large, skewed DataFrame.
        df_small: The smaller DataFrame to join with.
        join_key: The column name to join on.
        salt_factor: Number of splits for the skewed key (default 10). Increase for heavy skew.
        
    Returns:
        DataFrame: Result of the join.
    """
    
    # 1. Salt the skewed dataframe
    df_skew_salted = df_skew.withColumn("salt", (F.rand() * salt_factor).cast("int"))
    
    # 2. Replicate the small dataframe
    # Create a small DF with the salt range and cross join
    salt_range = df_skew.sparkSession.range(salt_factor).toDF("salt_id")
    df_small_replicated = df_small.crossJoin(salt_range).withColumnRenamed("salt_id", "salt")
    
    # 3. Join on key AND salt
    # Using left join as an example; adjust as needed (inner, left, etc.)
    return df_skew_salted.join(df_small_replicated, [join_key, "salt"], "left").drop("salt")

if __name__ == "__main__":
    # Example usage
    # df_result = salted_join(df_transactions, df_users, "user_id", salt_factor=20)
    pass

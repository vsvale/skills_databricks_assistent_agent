from pyspark.sql import SparkSession

def run_optimize(table_name: str, zorder_columns: list = None):
    """
    Runs the OPTIMIZE command on a Delta table to compact small files.
    Optionally performs Z-Ordering on specified columns.
    
    Args:
        table_name (str): The full name of the table (catalog.schema.table).
        zorder_columns (list, optional): List of column names to Z-Order by.
    """
    spark = SparkSession.builder.getOrCreate()
    
    cmd = f"OPTIMIZE {table_name}"
    if zorder_columns:
        cols = ", ".join(zorder_columns)
        cmd += f" ZORDER BY ({cols})"
        
    print(f"Running: {cmd}")
    spark.sql(cmd)
    print("Optimization complete.")

if __name__ == "__main__":
    # Example usage
    # run_optimize("main.default.my_table", ["id", "date"])
    pass

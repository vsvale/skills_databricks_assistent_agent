from pyspark.sql import SparkSession

def generate_cdc_data(catalog="main", schema="default", table="employees_cdf"):
    """
    Generates sample CDC data for testing SCD Type 1 and Type 2 processing.
    
    Schema:
    - id: Integer, unique identifier
    - name: String
    - role: String
    - country: String
    - operation: Change type (INSERT, UPDATE, DELETE)
    - sequenceNum: Integer, for ordering events
    """
    spark = SparkSession.builder.getOrCreate()
    
    data = [
        (1, "Alex", "chef", "FR", "INSERT", 1),
        (2, "Jessica", "owner", "US", "INSERT", 2),
        (3, "Mikhail", "security", "UK", "INSERT", 3),
        (4, "Gary", "cleaner", "UK", "INSERT", 4),
        (5, "Chris", "owner", "NL", "INSERT", 6),
        # Out of order update (sequenceNum 5 < 6), should be handled by sequenceNum
        (5, "Chris", "manager", "NL", "UPDATE", 5),
        (6, "Pat", "mechanic", "NL", "DELETE", 8),
        (6, "Pat", "mechanic", "NL", "INSERT", 7)
    ]
    
    columns = ["id", "name", "role", "country", "operation", "sequenceNum"]
    
    print(f"Creating table {catalog}.{schema}.{table}...")
    df = spark.createDataFrame(data, columns)
    df.write.format("delta").mode("overwrite").saveAsTable(f"{catalog}.{schema}.{table}")
    print("Data generated successfully.")

if __name__ == "__main__":
    # Adjust catalog/schema as needed
    generate_cdc_data(catalog="main", schema="default")

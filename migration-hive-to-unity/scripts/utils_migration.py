from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import lit, current_timestamp, input_file_name, col, trim
from typing import List, Callable

class RawToBronzeProcessor:
    """
    Handles batch ingestion from Raw (files) to Bronze (Delta Table).
    Adds mandatory control fields: dt_ingestion, source_processing, source_table, nm_file_origin.
    """
    def __init__(self, spark: SparkSession):
        self.spark = spark

    def process(self, source_path: str, target_table: str, source_table_name: str, file_format: str = "json"):
        if file_format == "json":
            df = self.spark.read.json(source_path)
        elif file_format == "csv":
            df = self.spark.read.option("header","true").csv(source_path)
        else:
            df = self.spark.read.parquet(source_path)

        df_bronze = (df
          .withColumn("dt_ingestion", current_timestamp())
          .withColumn("source_processing", lit("RAW"))
          .withColumn("source_table", lit(source_table_name))
          .withColumn("nm_file_origin", input_file_name())
        )
        
        (df_bronze.write
          .format("delta")
          .mode("append")
          .option("mergeSchema","true")
          .saveAsTable(target_table))
        return df_bronze.count()

class BronzeToSilverProcessor:
    """
    Handles batch processing from Bronze to Silver.
    Adds mandatory control fields: dt_processing.
    Updates source_processing to 'BRONZE'.
    Performs standard string cleaning (trim).
    """
    def __init__(self, spark: SparkSession):
        self.spark = spark

    def apply_transformations(self, df: DataFrame) -> DataFrame:
        # Standard cleaning
        for f in df.schema.fields:
            if str(f.dataType) == 'StringType' and f.name not in ("nm_file_origin",):
                df = df.withColumn(f.name, trim(col(f.name)))
        return df

    def process(self, source_table: str, target_table: str, required_columns: List[str] = None, custom_transformations: Callable[[DataFrame], DataFrame] = None):
        df = self.spark.table(source_table)
        bronze_table_name = source_table.split(".")[-1]
        
        if required_columns:
            for c in required_columns:
                df = df.filter(col(c).isNotNull())
                
        df = self.apply_transformations(df)
        
        if custom_transformations:
            df = custom_transformations(df)
            
        df_silver = (df
          .withColumn("dt_processing", current_timestamp())
          .withColumn("source_processing", lit("BRONZE"))
          .withColumn("source_table", lit(bronze_table_name))
        )
        
        (df_silver.write
          .format("delta")
          .mode("append")
          .option("mergeSchema","true")
          .saveAsTable(target_table))
        return df_silver.count()

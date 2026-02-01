"""
End-to-End Medallion Architecture Pipeline
============================================
Purpose: Demonstrate a complete Bronze → Silver → Gold pipeline using PySpark
Key Features:
  - Data quality expectations
  - Error handling and logging
  - Performance optimization
  - Incremental processing
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, current_timestamp, lit, when, to_timestamp,
    sum as _sum, count as _count, avg as _avg, max as _max,
    row_number, dense_rank, collect_set, datediff, current_date
)
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, DecimalType, IntegerType, TimestampType
from delta.tables import DeltaTable
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedallionPipeline:
    """
    Orchestrates Bronze → Silver → Gold data pipeline
    """
    
    def __init__(self, spark: SparkSession, catalog: str = "main"):
        self.spark = spark
        self.catalog = catalog
        self.bronze_schema = f"{catalog}.bronze"
        self.silver_schema = f"{catalog}.silver"
        self.gold_schema = f"{catalog}.gold"
        
    # ========================================================================
    # BRONZE LAYER: Raw Data Ingestion
    # ========================================================================
    
    def ingest_to_bronze(self, source_path: str, table_name: str, file_format: str = "json"):
        """
        Ingest raw data to Bronze layer with minimal transformation
        
        Args:
            source_path: Path to source data (Unity Catalog Volume or cloud storage)
            table_name: Target Bronze table name
            file_format: Source file format (json, csv, parquet)
        """
        logger.info(f"Ingesting data to Bronze: {self.bronze_schema}.{table_name}")
        
        try:
            # Read raw data with Auto Loader
            df = (self.spark.readStream
                  .format("cloudFiles")
                  .option("cloudFiles.format", file_format)
                  .option("cloudFiles.inferSchema", "true")
                  .option("cloudFiles.schemaLocation", f"/tmp/schemas/{table_name}")
                  .load(source_path))
            
            # Add metadata columns
            df_with_metadata = (df
                .withColumn("_ingestion_timestamp", current_timestamp())
                .withColumn("_source_file", col("_metadata.file_path"))
                .withColumn("_source_offset", col("_metadata.file_offset")))
            
            # Write to Bronze Delta table
            (df_with_metadata.writeStream
             .format("delta")
             .outputMode("append")
             .option("checkpointLocation", f"/tmp/checkpoints/bronze_{table_name}")
             .option("mergeSchema", "true")
             .trigger(availableNow=True)
             .table(f"{self.bronze_schema}.{table_name}"))
            
            logger.info(f"Successfully ingested to {self.bronze_schema}.{table_name}")
            
        except Exception as e:
            logger.error(f"Error ingesting to Bronze: {str(e)}")
            raise
    
    # ========================================================================
    # SILVER LAYER: Data Cleaning and Validation
    # ========================================================================
    
    def clean_transactions_to_silver(self):
        """
        Clean and validate transactions from Bronze to Silver
        Applies data quality checks, type casting, and deduplication
        """
        logger.info("Processing Bronze → Silver: transactions")
        
        try:
            # Read from Bronze
            bronze_df = self.spark.readStream.table(f"{self.bronze_schema}.raw_transactions")
            
            # Apply transformations and validations
            silver_df = (bronze_df
                # Type casting
                .withColumn("transaction_date", to_timestamp(col("transaction_date")))
                .withColumn("quantity", col("quantity").cast(IntegerType()))
                .withColumn("unit_price", col("unit_price").cast(DecimalType(10, 2)))
                .withColumn("total_amount", col("total_amount").cast(DecimalType(10, 2)))
                
                # Data quality filters
                .filter(col("transaction_id").isNotNull())
                .filter(col("customer_id").isNotNull())
                .filter(col("total_amount") > 0)
                .filter(col("quantity") > 0)
                .filter(col("transaction_date") >= lit("2020-01-01"))
                
                # Add processing timestamp
                .withColumn("_processing_timestamp", current_timestamp())
                
                # Select relevant columns
                .select(
                    "transaction_id",
                    "transaction_date",
                    "customer_id",
                    "product_id",
                    "quantity",
                    "unit_price",
                    "total_amount",
                    "_ingestion_timestamp",
                    "_processing_timestamp"
                ))
            
            # Write to Silver with deduplication
            (silver_df.writeStream
             .format("delta")
             .outputMode("append")
             .option("checkpointLocation", f"/tmp/checkpoints/silver_transactions")
             .trigger(availableNow=True)
             .foreachBatch(lambda batch_df, batch_id: 
                           self._deduplicate_and_write(
                               batch_df, 
                               f"{self.silver_schema}.validated_transactions",
                               "transaction_id"
                           ))
             .start())
            
            logger.info("Successfully processed to Silver: validated_transactions")
            
        except Exception as e:
            logger.error(f"Error processing to Silver: {str(e)}")
            raise
    
    def _deduplicate_and_write(self, batch_df, target_table: str, key_column: str):
        """
        Deduplicate batch and merge into target table
        
        Args:
            batch_df: Batch DataFrame
            target_table: Target Delta table
            key_column: Column to use for deduplication
        """
        # Deduplicate within batch
        window_spec = Window.partitionBy(key_column).orderBy(col("_ingestion_timestamp").desc())
        deduped_df = (batch_df
            .withColumn("rn", row_number().over(window_spec))
            .filter(col("rn") == 1)
            .drop("rn"))
        
        # Check if table exists
        if self.spark.catalog.tableExists(target_table):
            # Merge into existing table
            delta_table = DeltaTable.forName(self.spark, target_table)
            
            (delta_table.alias("target")
             .merge(
                 deduped_df.alias("source"),
                 f"target.{key_column} = source.{key_column}"
             )
             .whenMatchedUpdateAll()
             .whenNotMatchedInsertAll()
             .execute())
        else:
            # Create new table
            deduped_df.write.format("delta").mode("overwrite").saveAsTable(target_table)
    
    # ========================================================================
    # GOLD LAYER: Aggregations and Analytics
    # ========================================================================
    
    def create_daily_sales_summary(self):
        """
        Create aggregated daily sales summary in Gold layer
        """
        logger.info("Creating Gold layer: daily_sales_summary")
        
        try:
            # Read from Silver
            transactions_df = self.spark.table(f"{self.silver_schema}.validated_transactions")
            products_df = self.spark.table(f"{self.silver_schema}.normalized_products")
            customers_df = self.spark.table(f"{self.silver_schema}.unique_customers")
            
            # Join and aggregate
            daily_summary = (transactions_df
                .join(products_df, "product_id", "left")
                .join(customers_df, "customer_id", "left")
                .groupBy(
                    col("transaction_date").cast("date").alias("sale_date"),
                    col("category"),
                    col("customer_segment")
                )
                .agg(
                    _count("transaction_id").alias("transaction_count"),
                    _count(col("customer_id")).alias("unique_customers"),
                    _sum("quantity").alias("total_quantity"),
                    _sum("total_amount").alias("total_revenue"),
                    _avg("total_amount").alias("avg_transaction_value"),
                    _max("total_amount").alias("max_transaction_value")
                )
                .withColumn("_last_updated", current_timestamp()))
            
            # Write to Gold
            (daily_summary
             .write
             .format("delta")
             .mode("overwrite")
             .option("overwriteSchema", "true")
             .option("delta.autoOptimize.optimizeWrite", "true")
             .saveAsTable(f"{self.gold_schema}.daily_sales_summary"))
            
            logger.info("Successfully created Gold: daily_sales_summary")
            
        except Exception as e:
            logger.error(f"Error creating Gold layer: {str(e)}")
            raise
    
    def create_customer_360(self):
        """
        Create comprehensive customer analytics view in Gold layer
        """
        logger.info("Creating Gold layer: customer_360")
        
        try:
            # Read from Silver
            customers_df = self.spark.table(f"{self.silver_schema}.unique_customers")
            transactions_df = self.spark.table(f"{self.silver_schema}.validated_transactions")
            products_df = self.spark.table(f"{self.silver_schema}.normalized_products")
            
            # Calculate customer metrics
            customer_360 = (customers_df
                .join(transactions_df, "customer_id", "left")
                .join(products_df, "product_id", "left")
                .groupBy(
                    "customer_id",
                    "customer_name",
                    "email",
                    "customer_segment",
                    "registration_date"
                )
                .agg(
                    _count("transaction_id").alias("total_purchases"),
                    _sum("total_amount").alias("lifetime_value"),
                    _avg("total_amount").alias("avg_order_value"),
                    _max("transaction_date").alias("last_purchase_date"),
                    collect_set("category").alias("purchased_categories")
                )
                .withColumn(
                    "days_since_last_purchase",
                    datediff(current_date(), col("last_purchase_date"))
                )
                .withColumn(
                    "customer_status",
                    when(col("days_since_last_purchase") <= 30, "Active")
                    .when(col("days_since_last_purchase") <= 90, "At Risk")
                    .otherwise("Churned")
                )
                .withColumn("_last_updated", current_timestamp()))
            
            # Write to Gold with clustering
            (customer_360
             .write
             .format("delta")
             .mode("overwrite")
             .option("overwriteSchema", "true")
             .option("delta.autoOptimize.optimizeWrite", "true")
             .option("clusterBy", "customer_id")
             .saveAsTable(f"{self.gold_schema}.customer_360"))
            
            logger.info("Successfully created Gold: customer_360")
            
        except Exception as e:
            logger.error(f"Error creating customer_360: {str(e)}")
            raise
    
    # ========================================================================
    # PIPELINE ORCHESTRATION
    # ========================================================================
    
    def run_full_pipeline(self):
        """
        Execute the complete Bronze → Silver → Gold pipeline
        """
        logger.info("Starting full Medallion pipeline execution")
        
        try:
            # Bronze ingestion (example paths)
            # self.ingest_to_bronze(
            #     source_path="/Volumes/main/raw/transactions",
            #     table_name="raw_transactions",
            #     file_format="json"
            # )
            
            # Silver processing
            self.clean_transactions_to_silver()
            
            # Wait for streaming to complete
            self.spark.streams.awaitAnyTermination()
            
            # Gold aggregations
            self.create_daily_sales_summary()
            self.create_customer_360()
            
            logger.info("Pipeline execution completed successfully")
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            raise


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("Medallion Architecture Pipeline") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()
    
    # Set log level
    spark.sparkContext.setLogLevel("WARN")
    
    # Initialize pipeline
    pipeline = MedallionPipeline(spark, catalog="main")
    
    # Run pipeline
    pipeline.run_full_pipeline()
    
    # Stop Spark session
    spark.stop()

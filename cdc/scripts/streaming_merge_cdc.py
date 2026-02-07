from delta.tables import DeltaTable
from pyspark.sql.window import Window
from pyspark.sql.functions import col, row_number

def merge_cdc_feed(micro_batch_df, batch_id):
    """
    Function to be used with foreachBatch to upsert data into a Delta table.
    Handles deduplication within the batch and merges into the target.
    """
    # Optimize: Skip empty batches
    if micro_batch_df.isEmpty():
        return

    # 1. Define window to keep latest record per key in the batch
    # Partition by key, Order by sequence/time DESC
    window_spec = Window.partitionBy("id").orderBy(col("sequenceNum").desc())
    
    # 2. Deduplicate the micro-batch (keep rank 1)
    deduped_batch = micro_batch_df.withColumn("row_num", row_number().over(window_spec)) \
        .filter(col("row_num") == 1) \
        .drop("row_num")
    
    # 3. Perform the Merge
    # Note: Create DeltaTable inside the function to avoid serialization issues
    delta_table = DeltaTable.forName(micro_batch_df.sparkSession, "target_table")
    
    delta_table.alias("t").merge(
        deduped_batch.alias("s"),
        "t.id = s.id"
    ).whenMatchedUpdate(set = {
        "name": "s.name",
        "role": "s.role",
        "country": "s.country",
        "sequenceNum": "s.sequenceNum"
    }).whenNotMatchedInsert(values = {
        "id": "s.id",
        "name": "s.name",
        "role": "s.role",
        "country": "s.country",
        "sequenceNum": "s.sequenceNum"
    }).execute()

# Usage Example:
# query = spark.readStream \
#     .table("source_cdc_feed") \
#     .writeStream \
#     .foreachBatch(merge_cdc_feed) \
#     .outputMode("update") \
#     .start()

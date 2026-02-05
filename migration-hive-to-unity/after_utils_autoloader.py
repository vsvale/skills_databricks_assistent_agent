# Databricks notebook source
from delta.tables import DeltaTable
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
from pyspark.sql.session import SparkSession
from pyspark.sql.streaming import DataStreamWriter
from pyspark.sql.window import Window
import time

# COMMAND ----------

# DBTITLE 1,Função de validação de qualidade
def insert_dataQuality(microBatchOutputDF, batchId):

  DeequVerification(spark, tableName, microBatchOutputDF).validation(alert=False, p_type = 'ingestion-stream')

# COMMAND ----------

def create_stream_writer(dataframe, checkpoint, name, trigger_once, mergeSchema, toTable):
    stream_writer = (
        dataframe.writeStream
        .format("delta")
        .outputMode("append")
        .option("checkpointLocation", checkpoint)
        .queryName(name)
    )
    
    
    if mergeSchema:
        stream_writer = stream_writer.option("mergeSchema", True)
    
    if trigger_once:
        stream_writer = stream_writer.trigger(once=True)
    
    return stream_writer.toTable(toTable)


# COMMAND ----------

def create_stream_writer_parquet(
    dataframe: DataFrame,
    checkpoint: str,    
    name: str,
    partition_column: str = None,
    trigger_once: bool = True,
    
    mode: str = "append",
    mergeSchema: bool = False,
    foreach_batch: str = None,
    processingTime: str = None
) -> DataStreamWriter:

    stream_writer = (
        dataframe.writeStream.format("parquet")
        .outputMode(mode)
        .option("checkpointLocation", checkpoint)
        .queryName(name)
    )

    if mergeSchema:
        stream_writer = stream_writer.option("mergeSchema", True)
    if trigger_once:
        stream_writer = stream_writer.trigger(once=True)
    if partition_column is not None:
        stream_writer = stream_writer.partitionBy(partition_column)
    if foreach_batch is not None:
        stream_writer = stream_writer.foreachBatch(foreach_batch)
    if processingTime is not None:
        stream_writer = stream_writer.trigger(processingTime=processingTime)
    return stream_writer


# COMMAND ----------

def read_stream_delta(spark: SparkSession, deltaPath: str) -> DataFrame:
    return spark.readStream.format("delta").load(deltaPath)

# COMMAND ----------

def read_stream_raw_text(spark: SparkSession, rawPath: str) -> DataFrame:
  return spark.readStream.text(rawPath)

# COMMAND ----------

def read_stream_raw(spark: SparkSession, rawPath: str, json_schema: str) -> DataFrame:
    return (spark.readStream.format("json")
            .schema(json_schema)
            .options(maxBytesPerTrigger="5G", maxFilesPerTrigger=5000)
            .load(rawPath))

# COMMAND ----------

def read_stream_raw_parquet(spark: SparkSession, rawPath: str, parquet_schema: str) -> DataFrame:
    return spark.readStream.format("parquet").schema(parquet_schema).load(rawPath)

# COMMAND ----------

def read_batch_delta(deltaPath: str) -> DataFrame:
    return spark.read.format("delta").load(deltaPath)

# COMMAND ----------

def batch_writer(
    dataframe: DataFrame,
    partition_column: str,
    mode: str = "append",
) -> DataFrame:
    return (
        dataframe.write.format("delta")
        .mode(mode)
        .partitionBy(partition_column)
    )

# COMMAND ----------

def read_batch_raw_text(spark: SparkSession, rawPath: str) -> DataFrame:
  return spark.read.text(rawPath)

# COMMAND ----------

def stop_all_streams() -> bool:
    stopped = False
    for stream in spark.streams.active:
        stopped = True
        stream.stop()
    return stopped


def stop_named_stream(spark: SparkSession, namedStream: str) -> bool:
    stopped = False
    for stream in spark.streams.active:
        if stream.name == namedStream:
            stopped = True
            stream.stop()
    return stopped


def untilStreamIsReady(namedStream: str, progressions: int = 3) -> bool:
    queries = list(filter(lambda query: query.name == namedStream, spark.streams.active))
    while len(queries) == 0 or len(queries[0].recentProgress) < progressions:
        time.sleep(5)
        queries = list(filter(lambda query: query.name == namedStream, spark.streams.active))
    print("The stream {} is active and ready.".format(namedStream))
    return True

  
def untilStreamIsFinish(namedStream: str) -> bool:
  queries = list(filter(lambda query: query.name == namedStream, spark.streams.active))
  while len(queries) != 0:
      time.sleep(5)
      queries = list(filter(lambda query: query.name == namedStream, spark.streams.active))
  print("The stream {} is not active.".format(namedStream))
  return True

# COMMAND ----------

displayHTML("""<font size="3" color="Blue" face="sans-serif">Notebook "utils_autoloader": Executado!!!</font>""")

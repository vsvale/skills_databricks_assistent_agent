# Databricks notebook source
# MAGIC %run ./utils_autoloader

# COMMAND ----------

# MAGIC %run ./schema_attributes

# COMMAND ----------

from pyspark.sql.functions import (
    col,
    lpad,
    lit,
    udf,
    split,
    explode,
    regexp_extract,
    regexp_replace,
    from_json,
    to_json,
    struct,
    array,
    struct,
    array,
    when,
    pandas_udf,
    current_date,
    current_timestamp,
    input_file_name,
    date_format,
    concat_ws
)


from pyspark.sql.types import *
from pyspark.sql.streaming import DataStreamWriter
from pyspark.sql import DataFrame, Window
from delta.tables import *

from datetime import *

import builtins as py
import pandas as pd
import time
import json
import boto3
import numpy as np
import uuid
import os
import re
import requests

# COMMAND ----------

spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", True)
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", True)
spark.conf.set("spark.sql.shuffle.partitions", "auto")

spark.conf.set("spark.databricks.adaptive.autoOptimizeShuffle.enabled", True)
spark.conf.set("spark.databricks.adaptive.skewJoin.spillProof.enabled", True)
spark.conf.set("spark.databricks.optimizer.adaptive.enabled", True)

spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", True)
spark.conf.set("spark.databricks.delta.cache.enabled", True)
spark.conf.set("spark.databricks.io.cache.enabled", True)

spark.conf.set(
    "spark.databricks.delta.properties.defaults.autoOptimize.optimizeWrite", True
)
spark.conf.set(
    "spark.databricks.delta.properties.defaults.autoOptimize.autoCompact", True
)
spark.conf.set("spark.sql.session.timeZone", "America/Sao_Paulo")

# COMMAND ----------

def calcular_datas(bronzePath):
    from pyspark.sql.utils import AnalysisException

    try:
        # Leitura da bronze
        df_bronze_calculo = spark.table(bronzePath)
        
        # Calcula a data máxima da bronze
        max_date = df_bronze_calculo.agg({"date": "max"}).collect()[0][0]
        # Converte a string para um objeto datetime
        max_date = datetime.strptime(max_date, '%Y-%m-%dT%H:%M:%S.%fZ')
        max_date = max_date + timedelta(days=1)
        max_date_str = max_date.strftime('%Y-%m-%d')
    except AnalysisException as e:
      if 'Table does not exist' in str(e):
        max_date_str = '2025-01-01'
      else:
        raise e
    
    # Calculando a data de ontem
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    
    # Gerar listas de datas entre a data máxima e a data de ontem
    start_dates = []
    end_dates = []
    max_date_filters = []
    
    current_date = datetime.strptime(max_date_str, '%Y-%m-%d')
    while current_date.strftime('%Y-%m-%d') <= yesterday:
        start_dates.append(f"{current_date.strftime('%Y-%m-%d')}T00:00:00.000Z")
        end_dates.append(f"{current_date.strftime('%Y-%m-%d')}T23:59:59.999Z")
        max_date_filters.append(current_date.strftime('%Y%m%d'))
        current_date += timedelta(days=1)
    
    return start_dates, end_dates, max_date_filters

# COMMAND ----------

from datetime import datetime, timedelta
from pyspark.sql.functions import col

def calcular_datas_silver(DfCalc, NomeTabela):
    if spark.catalog.tableExists(f"auth_prd.silver.tb_{NomeTabela}"):
        # Leitura da tabela final
        max_silver = spark.sql(f"select max(ts_event) as max_date from auth_prd.silver.tb_{NomeTabela}").collect()[0][0]
        DfCalc = DfCalc.filter(col("date") > max_silver)
        print(f'Data max da tabela: {max_silver} e Dados bronze filtrados')
    else:
        max_silver = '2024-12-31T00:00:00.000Z'
        print('Tabela não existe, sem filtro nos dados bronze e usando data padrão 2025-01-01T00:00:00.000Z')
    
    max_silver_dates = []
    current_date = datetime.strptime(max_silver, '%Y-%m-%dT%H:%M:%S.%fZ')
    current_date += timedelta(days=1)  # Incrementa a data para o próximo dia
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    while current_date.strftime('%Y-%m-%d') <= yesterday:
        max_silver_dates.append(f"{current_date.strftime('%Y-%m-%d')}")
        current_date += timedelta(days=1)  # Incrementa a data
    return max_silver_dates, DfCalc

# COMMAND ----------

def create_stream_writer_liquid_cluster(
    dataframe: DataFrame,
    checkpoint: str,
    name: str,
    availableNow : bool = None,
    mode: str = "append",
    mergeSchema: bool = False,
    processingTime: str = None,
    foreach_batch: str = None
) -> DataStreamWriter:
 
    stream_writer = (
        dataframe.writeStream.format("delta")
        .outputMode(mode)
        .option("checkpointLocation", checkpoint)
        .queryName(name)
    )
    if mergeSchema:
        stream_writer = stream_writer.option("mergeSchema", True)
    if availableNow :
        stream_writer = stream_writer.trigger(availableNow=True)
    if processingTime :
        stream_writer = stream_writer.trigger(processingTime=processing_time)
    return stream_writer

# COMMAND ----------

from cryptography_library.operations import SparkCryptography
try:
  criptography = SparkCryptography(spark)

  encryptPhone = criptography.get_encryption_function("phone")
  encryptCPF   = criptography.get_encryption_function("cpf")
  encryptDate   = criptography.get_encryption_function("date")
  encryptName   = criptography.get_encryption_function("name")
  encryptEmail   = criptography.get_encryption_function("email")
  
except:
  print('lib de criptografia nao subiu')

# COMMAND ----------

 
def encrypt_functions() -> dict:
    """
    Prepara as funções de criptografia.
    Parameters: None
    Returns:
      Func: Funções de criptografia.
    """
    if var_ambiente == "dev":
        @udf(returnType=StringType())
        def encrypt_name(column_encrypt: str):
            return "name {}".format(column_encrypt)
        @udf(returnType=StringType())
        def encrypt_cpf(column_encrypt: str):
            return "CPF {}".format(column_encrypt)
        @udf(returnType=StringType())
        def encrypt_email(column_encrypt: str):
            return "email {}".format(column_encrypt)
        @udf(returnType=StringType())
        def encrypt_address(column_encrypt: str):
            return "endereco {}".format(column_encrypt)
        @udf(returnType=StringType())
        def encrypt_date(column_encrypt: str):
            return "Data {}".format(column_encrypt)
        @udf(returnType=StringType())
        def encrypt_personnumber(column_encrypt: str):
            return "Celular {}".format(column_encrypt)
        @udf(returnType=StringType())
        def encrypt_geocode(column_encrypt: str):
            return "GeoCode {}".format(column_encrypt)
        @udf(returnType=StringType())
        def encrypt_phone(column_encrypt: str):
            return "phone {}".format(column_encrypt)
        @udf(returnType=StringType())
        def encrypt_ip(column_encrypt: str):
            return "IP {}".format(column_encrypt)
        
        @udf(returnType=StringType())
        def decrypt_name(column_decrypt: str):
            return column_decrypt.replace("name ", "")
        @udf(returnType=StringType())
        def decrypt_cpf(column_decrypt: str):
            return column_decrypt.replace("CPF ", "")
        @udf(returnType=StringType())
        def decrypt_email(column_decrypt: str):
            return column_decrypt.replace("email ", "")
        @udf(returnType=StringType())
        def decrypt_address(column_decrypt: str):
            return column_decrypt.replace("endereco ", "")
        @udf(returnType=StringType())
        def decrypt_date(column_decrypt: str):
            return column_decrypt.replace("Data ", "")
        @udf(returnType=StringType())
        def decrypt_personnumber(column_decrypt: str):
            return column_decrypt.replace("Celular ", "")
        @udf(returnType=StringType())
        def decrypt_geocode(column_decrypt: str):
            return column_decrypt.replace("GeoCode ", "")
        @udf(returnType=StringType())
        def decrypt_phone(column_decrypt: str):
            return column_decrypt.replace("phone ", "")
        @udf(returnType=StringType())
        def decrypt_ip(column_decrypt: str):
            return column_decrypt.replace("IP ", "")
        
        encryption_functions = {
            "encrypt_name": encrypt_name,
            "encrypt_cpf": encrypt_cpf,
            "encrypt_email": encrypt_email,
            "encrypt_address": encrypt_address,
            "encrypt_date": encrypt_date,
            "encrypt_personnumber": encrypt_personnumber,
            "encrypt_geocode": encrypt_geocode,
            "encrypt_phone": encrypt_phone,
            "encrypt_ip": encrypt_ip,
        }
        decryption_functions = {
            "decrypt_name": decrypt_name,
            "decrypt_cpf": decrypt_cpf,
            "decrypt_email": decrypt_email,
            "decrypt_address": decrypt_address,
            "decrypt_date": decrypt_date,
            "decrypt_personnumber": decrypt_personnumber,
            "decrypt_geocode": decrypt_geocode,
            "decrypt_phone": decrypt_phone,
            "decrypt_ip": decrypt_ip,
        }
    else:
        from cryptography_library.operations import SparkCryptography
        criptography = SparkCryptography(spark)
        encryption_functions = {
            "encrypt_name": criptography.get_encryption_function("name"),
            "encrypt_cpf": criptography.get_encryption_function("cpf"),
            "encrypt_email": criptography.get_encryption_function("email"),
            "encrypt_address": criptography.get_encryption_function("address"),
            "encrypt_date": criptography.get_encryption_function("date"),
            "encrypt_personnumber": criptography.get_encryption_function("person_number"),
            "encrypt_geocode": criptography.get_encryption_function("geocode"),
            "encrypt_phone": criptography.get_encryption_function("phone"),
            "encrypt_ip": criptography.get_encryption_function("ip"),
        }
        decryption_functions = {
            "decrypt_name": criptography.get_decryption_function("name"),
            "decrypt_cpf": criptography.get_decryption_function("cpf"),
            "decrypt_email": criptography.get_decryption_function("email"),
            "decrypt_address": criptography.get_decryption_function("address"),
            "decrypt_date": criptography.get_decryption_function("date"),
            "decrypt_personnumber": criptography.get_decryption_function("person_number"),
            "decrypt_geocode": criptography.get_decryption_function("geocode"),
            "decrypt_phone": criptography.get_decryption_function("phone"),
            "decrypt_ip": criptography.get_decryption_function("ip"),
        }
    return encryption_functions, decryption_functions

# COMMAND ----------

def transform_events_origin_to_gold_data(df_origin: DataFrame, hash_mapping: str) -> DataFrame:
    """
    Faz as transformaçoes de origem para bronze
    -encripta as colunas PII definidas no arquivo de configuração
    -adiciona colunas de controle

    Parameters:
      df_origin: Dataframe de origem.
      hash_mapping: Caminho para o arquivo de hash de-para.
    Returns:
      DataFrame: DataFrame bronze criptografado com metadados.
    """

    decryption_functions = encrypt_functions()

    df_origin = (
        df_origin.withColumn("dt_load_bronze", current_date())
        .withColumn("ts_load_bronze", current_timestamp())
        .withColumn("file_name_raw",  col("_metadata.file_path"))
    )

    df_hash = spark.read.table(hash_mapping).select('nu_documento', 'nu_documento_hash')

    df_origin = df_origin.join(df_hash, df_origin.nu_documento_servidor == df_hash.nu_documento_hash, "left")

    for i in parameters_table["encrypted_cols"]:
      if i["col_name"] in df_origin.columns:
        decryption_functions = decryption_functions[0]["encrypt_" + i["encrypt_type"]]
        df_origin = df_origin.withColumn(
            i["col_name"],
            decryption_functions(col(i["col_name"])),
        )

    return df_origin.drop('nu_documento')


# COMMAND ----------

def transform_events_origin_to_bronze_data(df_origin: DataFrame, hash_mapping: str) -> DataFrame:
    """
    Faz as transformaçoes de origem para bronze
    -encripta as colunas PII definidas no arquivo de configuração
    -adiciona colunas de controle

    Parameters:
      df_origin: Dataframe de origem.
      hash_mapping: Caminho para o arquivo de hash de-para.
    Returns:
      DataFrame: DataFrame bronze criptografado com metadados.
    """

    encryption_functions = encrypt_functions()

    df_origin = (
        df_origin.withColumn("dt_load_bronze", current_date())
        .withColumn("ts_load_bronze", current_timestamp())
        .withColumn("file_name_raw",  input_file_name())
    )

    df_hash = spark.read.load(hash_mapping).select('nu_documento', 'nu_documento_hash')

    df_origin = df_origin.join(df_hash, df_origin.nu_documento_servidor == df_hash.nu_documento_hash, "left")

    for i in parameters_table["encrypted_cols"]:
      if i["col_name"] in df_origin.columns:
        encryption_function = encryption_functions[0]["encrypt_" + i["encrypt_type"]]
        df_origin = df_origin.withColumn(
            i["col_name"],
            encryption_function(col(i["col_name"])),
        )
    df_origin = df_origin.drop("nu_documento", "nu_documento_servidor")
    df_origin = df_origin.withColumnRenamed("nu_documento_hash", "nu_documento_servidor")


    return df_origin
  

# COMMAND ----------

def purge_sensitive(bucket_bronze):
    """
    Deletes files listed in the 'file_name_raw' column from the specified Delta table.

    Parameters:
    bucket_bronze (str): The path to the Delta table in the bronze bucket.

    Returns:
    None
    """
    try:
        file_names_to_delete = spark.read.format("delta").load(bucket_bronze).select("file_name_raw").rdd.flatMap(lambda x: x).collect()
        for file_name in file_names_to_delete:
            dbutils.fs.rm(f"{file_name}", True)
        print("Files deleted successfully")
    except Exception as e:
        print(f"Error deleting files: {str(e)}")
        pass

# COMMAND ----------

def raw_reader(raw_path: str) -> DataFrame:
    """
    Faz a leitura em stream utilizando o cloudfiles dos dados na origem.

    Parameters:
      raw_path: Path origem dos arquivos.
    Returns:
      DataFrame: DataFrame estruturado.
    """

    folders = dbutils.fs.ls(raw_path)

    folder_names = [f.name for f in folders if f.isDir()]
    sorted_folders = sorted(folder_names, key=lambda x: int(re.findall(r'\d+', x)[0]), reverse=True)

    latest_folder = sorted_folders[0]

    latest_folder_path = raw_path + latest_folder

    df_raw = (
        spark.read
        .format("parquet")
        .load(latest_folder_path)
    )
    return df_raw


# COMMAND ----------

from pyspark.sql.functions import col, current_date, current_timestamp

def transformation_raw_to_bronze_auth(df: DataFrame):
  return(
    df
    .select(
      "*"
      ,col("_metadata.file_path").alias('file_name_raw')
      ,current_date().alias('dt_load_bronze')
      ,current_timestamp().alias('ts_load_bronze')
    )
  )

# COMMAND ----------

def transformation_bronze_to_silver(df: DataFrame) -> DataFrame:
    """
    Transforma o DataFrame bronze para silver:
    - Adiciona colunas de data e timestamp de carga
    - Aplica criptografia nos campos PII definidos no arquivo de configuração

    Parâmetros:
      df: DataFrame da tabela bronze

    Retorna:
      DataFrame: DataFrame estruturado para a tabela silver
    """

    df_bronze_structured = df.select(
            '*',
            current_date().alias('dt_load_silver'),
            current_timestamp().alias('ts_load_silver')
    ).drop('dt_load_bronze', 'ts_load_bronze')

    return df_bronze_structured

# COMMAND ----------

def create_stream_writer(
    dataframe: DataFrame,
    checkpoint: str,
    name: str,
    partition_column: str = None,
    trigger_once: bool = True,
    mode: str = "append",
    mergeSchema: bool = False,
    ignoreDeletes: bool = False,
    foreach_batch: str = None,
    processingTime: str = None,
) -> DataStreamWriter:
    """
    Retorna o writer do dataframe em streaming.

    Parameters:
        dataframe : DataFrame em streaming.
        checkpoint : Path do checkpoint.
        name: Nome da query.
        partition_column: Coluna de referência para o particionamento da Delta Table.
        trigger_once: Indica se o trigger vai ser acionado apenas uma vez
        mode: Modo de escrita da Delta Table.
        mergeSchema: Indica se o Spark deve fazer um Merge caso o Schema da tabela seja modificado.
        ignoreDeletes: Indica se o Spark deve ignorar o delete de arquivos.

    Returns:
            stream_writer : Objeto de write em streaming configurado.
    """

    stream_writer = (
        dataframe.writeStream.format("cloudFiles")
        .option("cloudFiles.format", "delta")
        .outputMode(mode)
        .option("checkpointLocation", checkpoint)
        .queryName(name)
    )

    if mergeSchema:
        stream_writer = stream_writer.option("mergeSchema", True)
    if ignoreDeletes:
        stream_writer = stream_writer.option("ignoreDeletes", True)
    if trigger_once:
        stream_writer = stream_writer.trigger(once=True)
    if partition_column is not None:
        stream_writer = stream_writer.partitionBy(partition_column)
    if foreach_batch is not None:
        stream_writer = stream_writer.foreachBatch(foreach_batch)
    if processingTime is not None:
        stream_writer = stream_writer.trigger(processingTime=processingTime)
    return stream_writer

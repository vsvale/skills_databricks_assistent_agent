# Databricks notebook source
# MAGIC %md
# MAGIC ### Ingestão da base Partner Auth - Bronze to Silver
# MAGIC # 
# MAGIC - Atividades Jira <a href = https://serasaexperian.atlassian.net/browse/DECS-18918> DESC-18918  </a> e <a href = https://serasaexperian.atlassian.net/browse/DECS-18919> DESC-18919 </a>  
# MAGIC - `Bucket destino silver` : 
# MAGIC
# MAGIC   - s3://serasaexperian-ecs-datalakehouse-prd-silver/ecs/auth/partner/public/signup/back
# MAGIC   - s3://serasaexperian-ecs-datalakehouse-prd-silver/ecs/auth/partner/public/signup/front
# MAGIC   - s3://serasaexperian-ecs-datalakehouse-prd-silver/ecs/auth/partner/public/login/back
# MAGIC   - s3://serasaexperian-ecs-datalakehouse-prd-silver/ecs/auth/partner/public/login/front
# MAGIC
# MAGIC
# MAGIC
# MAGIC - `JOB de execucao`: A Definir
# MAGIC - `Atualizacao`: Stream

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ### Import Utils

# COMMAND ----------

# MAGIC %run ./utils/00_operations

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configurações Iniciais

# COMMAND ----------

# Configurações de otimização Delta
spark.conf.set("spark.databricks.delta.properties.defaults.autoOptimize.autoCompact", True)
spark.conf.set("spark.databricks.delta.properties.defaults.autoOptimize.optimizeWrite", True)
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", True)

# COMMAND ----------

# DBTITLE 1,Cell 6
import os
os.environ['SPARK_VERSION'] = '3.5'

from datetime import datetime, date
from DataQuality import *
from pyspark.sql.session import SparkSession
from delta.tables import DeltaTable
from cryptography_library.operations import SparkCryptography
criptography = SparkCryptography(spark)
from cryptography_library.operations.commons import DataLakeCryptographyClient

# COMMAND ----------

dbutils.widgets.removeAll()

dbutils.widgets.dropdown('source', 'login',['signup', 'login'])
source    = dbutils.widgets.getArgument('source')

dbutils.widgets.dropdown('camada', 'front',['back', 'front'])
camada    = dbutils.widgets.getArgument('camada')

dbutils.widgets.dropdown("reprocess", 'false', ['true', 'false'])                
reprocess  = dbutils.widgets.getArgument("reprocess")

print(f"source    :   {source}")
print(f"camada    :   {camada}")
print(f"reprocess :   {reprocess}")

# COMMAND ----------

# Configuração de PATH
bucketChk         = f"ecs-datalakehouse-prd-checkpoints" 


fileName          = f"{source}/{camada}"
fileName_         = f"{source}_{camada}"

bronzePath           = f"auth_prd.bronze.tb_{source}_{camada}"
silverPath           = f"auth_prd.silver.tb_{source}_{camada}"
silverCheckpoint       = f"/Volumes/auth_prd/silver/checkpoints/ecs/auth/{source}/{camada}/silver"
qualityCheckpointPath  = f"/Volumes/auth_prd/silver/checkpoints/ecs/auth/{source}/{camada}/silver_quality"
namedSilverStream      = f"ecs_auth_{fileName_}_inicial_write_bronze_to_silver"
nameStreamQuality      = f"ecs_auth_{fileName_}_inicial_write_bronze_to_silver_quality"
tableName              = silverPath

print("Buckets Load")
print(f"bronzePath             :   {bronzePath}")

print("\nBuckets Save")
print(f"silverPath             :   {silverPath}")
print(f"silverCheckpoint       :   {silverCheckpoint}")


print("\nCheckpoint Name")
print(f"namedSilverStream      :   {namedSilverStream}")

print(f"qualityCheckpointPath  :   {qualityCheckpointPath}")
print(f"nameStreamQuality      :   {nameStreamQuality}")

print("\nTable Name")
print(f"tableName      :   {tableName}")

# COMMAND ----------

# MAGIC %md
# MAGIC ###Configurando funções de criptografia e descriptografia

# COMMAND ----------

#Funções de criptografia necessária
encrypt_geocode        = criptography.get_encryption_function("geocode")
encrypt_ip        = criptography.get_encryption_function("ip")

#Funções de decriptografia necessária
decrypt_name        = criptography.get_decryption_function("name")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Reprocess

# COMMAND ----------

if reprocess == "true":
    dbutils.fs.rm(f"/Volumes/auth_prd/silver/checkpoints/ecs/auth/{source}/{camada}/silver",True)
    dbutils.fs.mkdirs(f"/Volumes/auth_prd/silver/checkpoints/ecs/auth/{source}/{camada}/silver")
    dbutils.fs.rm(f"/Volumes/auth_prd/silver/checkpoints/ecs/auth/{source}/{camada}/silver_quality",True)
    dbutils.fs.mkdirs(f"/Volumes/auth_prd/silver/checkpoints/ecs/auth/{source}/{camada}/silver_quality")
    spark.sql(f"TRUNCATE TABLE `{silverPath}`")
    print(f'TABELA TRUNCADA                 : {silverPath}')
    print(f'PATH CHECKPOINT SILVER DELETADO : {silverCheckpoint}')
else:
    pass

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Transform Bronze -> Silver

# COMMAND ----------

# MAGIC %md
# MAGIC ###Leitura de dados da Bronze

# COMMAND ----------

bronzeDF = spark.readStream.table(bronzePath)

# COMMAND ----------

# DBTITLE 1,Pegando a data max da silver e filtrando a bronze
# Chamando a função calcular_datas_silver e utilizando os valores retornados
dates_carga, filtered_bronzeDF = calcular_datas_silver(bronzeDF, fileName_)
print(f"Datas a ser carregada: {dates_carga}")

# COMMAND ----------

# MAGIC %md
# MAGIC ####Descriptografando a coluna attributes

# COMMAND ----------

bronzeToSilver = filtered_bronzeDF.withColumn("attributes", decrypt_name("attributes"))

# COMMAND ----------

# MAGIC %md
# MAGIC ####Aplicando tratamentos finais

# COMMAND ----------

# MAGIC %md
# MAGIC -  aplicando schema da coluna attributes 
# MAGIC - selecionando somente colunas necessárias
# MAGIC - Aplicando criptografia somente nas colunas necessárias
# MAGIC - Definindo schema da tabela final

# COMMAND ----------

if camada == "back":
  #Aplicando o schema da coluna attributes
  bronzeToSilver = bronzeToSilver.withColumn("attributes", from_json("attributes", attributes_back_schema))

  #Selecionando somente colunas necessárias
  bronzeToSilver = df_auth_back(bronzeToSilver)

  #Definindo schema da tabela final 
  schema = back_schema_tabela

elif camada == "front":
  #Aplicando o schema da coluna attributes
  bronzeToSilver = bronzeToSilver.withColumn("attributes", from_json("attributes", attributes_front_schema))

  #Selecionando somente colunas necessárias
  bronzeToSilver = df_auth_front(bronzeToSilver)

  #Aplicando criptografia somente nas colunas necessárias
  bronzeToSilver = criptografia_silver_front(bronzeToSilver)

  #Definindo schema da tabela final 
  schema = front_schema_tabela

# COMMAND ----------

# MAGIC %md
# MAGIC ####Criando colunas de controle

# COMMAND ----------

SilverFinal = transformation_bronze_to_silver(bronzeToSilver)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Create Table

# COMMAND ----------

#não adicionar no momento, pois não faz sentido para esse caso, além do alto custo de processamento
# spark.sql(f"OPTIMIZE delta.`{silverPath}` ZORDER BY Op ")
# goldTable = DeltaTable.forPath(spark, silverPath)
# goldTable.vacuum() 
# print("Optimize & Vacuum OK")

# COMMAND ----------

# DBTITLE 1,Configuração do Stream Silver e escrita na silverPath
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS auth_prd.silver.tb_{fileName_} (
        {schema}
    )
    CLUSTER BY (cd_id, dt_event, cd_uuid)
""")

bronzeToSilverWriter = (
    SilverFinal.writeStream
    .outputMode("append")
    .option("checkpointLocation", silverCheckpoint)
    .queryName(namedSilverStream)
    .option("mergeSchema", True)
    .trigger(availableNow=True)
)

print(f"Iniciando escrita em: {silverPath}")
bronzeToSilverWriter.toTable(silverPath).awaitTermination()
print("Escrita realizada com sucesso!")

# COMMAND ----------

# DBTITLE 1,Escrita dados de qualidade
bronzeToSilverDataQuality = (
    SilverFinal.writeStream
    .outputMode("append")
    .option("checkpointLocation", qualityCheckpointPath)
    .queryName(nameStreamQuality)
    .option("mergeSchema", True)
    .trigger(availableNow=True)
    .foreachBatch(insert_dataQuality)
)

try:
    print(f"Iniciando escrita em: {qualityCheckpointPath}")
    bronzeToSilverDataQuality.start().awaitTermination()
    print("Escrita realizada com sucesso!")
except Exception as e:
    print(f"Error: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC #### Fim

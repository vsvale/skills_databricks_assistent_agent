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

!pip install -qqq brazilnum email-validator phonenumbers

# COMMAND ----------

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
bucketBronze      = f"ecs-datalakehouse-prd-bronze/ecs/auth/{source}/{camada}"
bucketSilver      = f"ecs-datalakehouse-prd-silver"
bucketChk         = f"ecs-datalakehouse-prd-checkpoints" 


fileName          = f"{source}/{camada}"
fileName_         = f"{source}_{camada}"

bronzePath           = "s3://serasaexperian-{}".format(bucketBronze, camada)

silverPath             = "s3://serasaexperian-{}/ecs/auth/{}".format(bucketSilver , fileName)
silverCheckpoint       = "s3://serasaexperian-{}/ecs/auth/{}/silver".format(bucketChk, fileName)
namedSilverStream      = f"ecs_auth_{fileName_}_inicial_write_bronze_to_silver"
qualityCheckpointPath  = "s3://serasaexperian-{}/ecs/auth/{}/silver_quality/".format(bucketChk, fileName)
nameStreamQuality      = f"ecs_auth_{fileName_}_inicial_write_bronze_to_silver_quality"
tableName              = f"db_auth_silver.tb_{fileName_}"

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
    spark.sql(f"TRUNCATE TABLE delta.`{silverPath}`")
    dbutils.fs.rm(silverCheckpoint, True)
    if spark._jsparkSession.catalog().tableExists(f"db_auth_silver.tb_{fileName_}"):
        spark.sql(f"TRUNCATE TABLE db_auth_silver.tb_{fileName_}")    
    
    print(f'TABELA TRUNCADA                 : db_auth_silver.tb_{fileName_}')
    print(f'PATH SILVER TRUNCADO            : {silverPath}')
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

bronzeDF = read_stream_delta(spark, bronzePath)

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
if DeltaTable.isDeltaTable(spark, silverPath):
        bronzeToSilverWriter = create_stream_writer_liquid_cluster(
            dataframe=SilverFinal,
            checkpoint=silverCheckpoint,
            name=namedSilverStream,
            availableNow=True,
            mode="append",
            mergeSchema=True
        )
        print(f"Iniciando escrita em: {silverPath}")
        bronzeToSilverWriter.start(silverPath)
        print("Escrita realizada com sucesso!")
else:
        spark.sql(f"""
        CREATE TABLE IF NOT EXISTS db_auth_silver.tb_{fileName_} (
            {schema}
        )
        USING delta
        LOCATION '{silverPath}'
        CLUSTER BY (cd_id, dt_event, cd_uuid)  
        """)

        bronzeToSilverWriter = create_stream_writer_liquid_cluster(
            dataframe=SilverFinal,
            checkpoint=silverCheckpoint,
            name=namedSilverStream,
            availableNow=True,
            mode="append",
            mergeSchema=True
        )
        print(f"Iniciando escrita em: {silverPath}")
        bronzeToSilverWriter.start(silverPath)
        print("Tabela criada e escrita realizada com sucesso!")

# COMMAND ----------

# DBTITLE 1,Escrita dados de qualidade
bronzeToSilverDataQuality = create_stream_writer_liquid_cluster(

    dataframe=SilverFinal,
    checkpoint=qualityCheckpointPath,
    name=nameStreamQuality,
    availableNow=True,
    mergeSchema=True,
    foreach_batch=insert_dataQuality,
    mode="append"

)

try:
    print(f"Iniciando escrita em: {qualityCheckpointPath}")
    bronzeToSilverDataQuality.start(qualityCheckpointPath).awaitTermination()
    print("Escrita realizada com sucesso!")
except Exception as e:
    print(f"Error: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC #### Fim

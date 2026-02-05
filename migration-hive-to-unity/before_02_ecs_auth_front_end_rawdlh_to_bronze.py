# Databricks notebook source
# MAGIC %md
# MAGIC ## Ingestão da base Login e Signup Auth Front-End - RawDLH to Bronze
# MAGIC # 
# MAGIC - Atividades Jira <a href = https://serasaexperian.atlassian.net/browse/DECS-18918> DESC-18918  </a> e <a href = https://serasaexperian.atlassian.net/browse/DECS-18919> DESC-18919 </a>  
# MAGIC - `Bucket destino bronze` : 
# MAGIC
# MAGIC   - s3://serasaexperian-ecs-datalakehouse-prd-bronze/ecs/auth/login/front
# MAGIC   - s3://serasaexperian-ecs-datalakehouse-prd-bronze/ecs/auth/signup/front
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
# MAGIC ### Buckets & Configs

# COMMAND ----------

dbutils.widgets.removeAll()

dbutils.widgets.dropdown("reprocess", 'false', ['true', 'false'])                
reprocess  = dbutils.widgets.getArgument("reprocess")

dbutils.widgets.dropdown("source", 'signup', ['login', 'signup'])                
source  = dbutils.widgets.getArgument("source")

print(f"reprocess :   {reprocess}")
print(f"source    :   {source}")

# COMMAND ----------

# Configuração de PATH
bucketRaw         = f"ecs-observability-datadog-logging-prd/auth/front"
bucketBronze      = f"ecs-datalakehouse-prd-bronze/ecs/auth/{source}/front"
bucketChk         = f"ecs-datalakehouse-prd-checkpoints/ecs/auth/{source}/front" 


rawPath           = "s3://{}".format(bucketRaw)


bronzePath        = "s3://serasaexperian-{}".format(bucketBronze)
bronzeCheckpoint  = "s3://serasaexperian-{}".format(bucketChk)


namedBronzeStream      = f"ecs_auth_front_{source}_write_raw_to_bronze"

print("Buckets Load")
print(f"rawPath           :   {rawPath}")

print("\nBuckets Save")
print(f"bronzePath        :   {bronzePath}")
print(f"bronzeCheckpoint  :   {bronzeCheckpoint}")

print("\nCheckpoint Name")
print(f"namedBronzeStream          :   {namedBronzeStream}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Config

# COMMAND ----------

spark.conf.set("spark.databricks.delta.properties.defaults.autoOptimize.autoCompact", True)
spark.conf.set("spark.databricks.delta.properties.defaults.autoOptimize.optimizeWrite", True)
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", True)

# COMMAND ----------

# DBTITLE 1,Funções e imports de criptografia necessária
from cryptography_library.operations import SparkCryptography
criptography = SparkCryptography(spark)
from cryptography_library.operations.commons import DataLakeCryptographyClient

encrypt_name = criptography.get_encryption_function("name")

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Transform RawDlh -> Bronze

# COMMAND ----------

# MAGIC %md
# MAGIC ###Reprocess

# COMMAND ----------

if reprocess == "true":
  spark.sql(f"TRUNCATE TABLE delta.`{bronzePath}`")
  dbutils.fs.rm(bronzeCheckpoint, True)
  
  print(f'PATH BRONZE TRUNCADO            : {bronzePath}')
  print(f'PATH CHECKPOINT BRONZE DELETADO : {bronzeCheckpoint}')
else:
  pass

# COMMAND ----------

# MAGIC %md
# MAGIC ###Filtrando para pegar dados max até 23h59 do dia anterior

# COMMAND ----------

# DBTITLE 1,Calculando a massa delta a ser carregada
start_dates, end_dates, max_date_filterers = calcular_datas(bronzePath)
print(f"Start Date: {start_dates}, End Date: {end_dates}, Max Date Filter: {max_date_filterers}")

# COMMAND ----------

# MAGIC %md
# MAGIC ###Tratamentos e escrita na bronze

# COMMAND ----------

for i in range(len(start_dates)):
  rawPathDay = "{}/dt={}".format(rawPath, max_date_filterers[i])
  rawDF = read_stream_raw(spark, rawPathDay, schema_bronze_front) 
  rawDF = rawDF.filter((col("date") >= start_dates[i]) & (col("date") <= end_dates[i]))
  print('______________________________________________________________________________')
  print(f'START E END DATE A SER CARREGADO NA BRONZE : {start_dates[i]}, {end_dates[i]}')
  print(f'PATH LEITURA: {rawPathDay}')

  rawDF = rawDF.withColumn("attributes", from_json("attributes", attributes_front_schema))
  print('schema aplicado na coluna attributes')

  if source == "login":
    rawDF = rawDF.filter(col("attributes.flow").isin("sign_in", "new_sign_in"))
    print('dados login filtrado')
  elif source == "signup":
    rawDF = rawDF.filter(col("attributes.flow").isin("sign_up_v2"))
    print('dados signup filtrado')

  rawDF = rawDF.withColumn("attributes", to_json("attributes"))
  print('transformando attributes em string')
  
  rawDF = rawDF.withColumn("attributes", encryptName(col("attributes")))
  print('dado encriptado')

  df_transformed_Bronze = transformation_raw_to_bronze_auth(rawDF)
  print(f'incluindo colunas de controle')

  bronzeWriter = create_stream_writer_liquid_cluster(
    
    dataframe=df_transformed_Bronze,
    checkpoint=bronzeCheckpoint,
    name=namedBronzeStream,
    availableNow=True,
    mergeSchema=True,
    mode="append"
    )
  try:
    print(f"Iniciando escrita em: {bronzePath}")
    bronzeWriter.start(bronzePath).awaitTermination()
    print("Escrita realizada com sucesso!")
  except Exception as e:
    print(f"Error: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Fim

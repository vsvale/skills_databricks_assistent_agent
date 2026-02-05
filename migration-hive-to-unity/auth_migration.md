---
name: migration-of-notebooks-from-hive-to-unity-catalog
description: Recommendations for migrating notebooks that save tables in Hive or use data security modes set to None or Legacy, to instead save tables in Unity Catalog using Unity Catalog–enabled clusters.
---

# %run ./utils/00_operations
- Explicito é melhor que implicito. 
- Utilize repositórios unificados a códigos copy-paste entre repositorios, isso facilita a evolucao do codigo ao nao fazer necessarios alterar inumeros repositorios a cada nova alteracao.
- O uso do create_stream_writer, create_stream_writer_liquid_cluster nao sao mais bem vista, sendo recomendado utilizar a escrita direta da operacao no código, por exemplo:
BEFORE:
```python
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
```
AFTER:
```python
bronzeWriter = (df_transformed_Bronze.writeStream
                .outputMode("append")
                .option("checkpointLocation", bronzeCheckpoint)
                .queryName(namedBronzeStream)
                .trigger(availableNow=True)
                .option("mergeSchema", True)

)
try:
    print(f"Iniciando escrita em: {bronzePath}")
    bronzeWriter.toTable(bronzeTable).awaitTermination()
    print("Escrita realizada com sucesso!")
except Exception as e:
    print(f"Error: {e}")
    raise
```
- Caso o streaming não utilize foreachBatch  foreachBatch altere o .start(bronzePath) por .toTable(bronzePath)
BEFORE
```python
qry = rawToBronzeWriterIncr.start(bronzePath)
qry.awaitTermination()
```
AFTER
```python
rawToBronzeWriterIncr.toTable(bronzePath).awaitTermination()
```

# RAW
- Via de regra buckets Raw e Sensitive viram volumes
- Default do codigo hive é separar os path em variaveis `bucket` e `path`, por exemplo:
  - bucketRaw, bucketBronze, bucketChk
  - rawPath, bronzePath, bronzeCheckpoint
  ```python
bucketRaw         = f"ecs-observability-datadog-logging-prd/auth/back"
bucketBronze      = f"ecs-datalakehouse-prd-bronze/ecs/auth/{source}/back"
bucketChk         = f"ecs-datalakehouse-prd-checkpoints/ecs/auth/{source}/back" 
rawPath           = "s3://{}".format(bucketRaw)
bronzePath        = "s3://serasaexperian-{}".format(bucketBronze)
bronzeCheckpoint  = "s3://serasaexperian-{}".format(bucketChk)
```
- Primeiro monte o caminho completo com os valores das variaveis, o path da raw é "s3://ecs-observability-datadog-logging-prd/auth/back" nesse exemplo
- Em seguida verifique se esse path é delta: 
```sql
describe detail delta.`s3://ecs-observability-datadog-logging-prd/auth/back'
```
- Caso retorne [DELTA_MISSING_DELTA_TABLE] pode criar um volume nesse path. Mas verifique se o path ja existe um volume associado, se sim utilizar o volume já criado:
```python
s3_path = "s3://ecs-observability-datadog-logging-prd/auth/back"
if s3_path in spark.sql(f"select collect_set(storage_location) from system.information_schema.volumes where storage_location = '{s3_path}'").first()[0]:
  volume_error = spark.sql(f"select concat(volume_catalog,'.',volume_schema,'.',volume_name) from system.information_schema.volumes where storage_location = '{s3_path}'").first()[0]
  raise Exception(f"The path {s3_path} is already in  use in Volume {volume_error}")
```
- Nesse caso já existe um volume criado em outro catalogo `observability_prd.raw.ecs-observability-datadog-logging-prd`
- Qualquer usuario tem permissao para criar volumes em temp e sandbox, nos demais schemas recomendar o uso do job create volume https://experian-serasa-ecs-labs.cloud.databricks.com/jobs/843137913110759?o=986111815307787
- Em sequida alteramos o path para o Volume:
BEFORE:
```python
bucketRaw         = f"ecs-observability-datadog-logging-prd/auth/back"
rawPath           = "s3://{}".format(bucketRaw)
```
AFTER
```python
rawPath = "/Volumes/observability_prd/raw/ecs-observability-datadog-logging-prd/auth/back/"
```
- Substituir funcoes do utils_autoloader pela versao explicita do metedo por exemplo
BEFORE:
```python
def read_stream_raw(spark: SparkSession, rawPath: str, json_schema: str) -> DataFrame:
    return (spark.readStream.format("json")
            .schema(json_schema)
            .options(maxBytesPerTrigger="5G", maxFilesPerTrigger=5000)
            .load(rawPath))

rawDF = read_stream_raw(spark, rawPathDay, schema_bronze_back) 
```
AFTER:
```python
rawDF = (
    spark.readStream.format("json")
            .schema(schema_bronze_back)
            .options(maxBytesPerTrigger="5G", maxFilesPerTrigger=5000)
            .load(rawPathDay)
)
```



# BRONZE
- Utilizamos managed table como default no ambiente, por isso nao recomende External Tables a menos que usuario especifique.
- Nao acrescente OPTIMIZE, ANALYZE e VACUUM. Caso encontre no codigo que o destination é gravar uma tabela MANAGED e explique sobre predictive optimization
1. Realizamos um CTAS com o path original, em uma bronze o nome da tabela depende no nome no path `s3://serasaexperian-ecs-datalakehouse-prd-bronze/ecs/auth/login/back/"`:
```sql
CREATE OR REPLACE TABLE auth_prd.bronze.tb_login_back
CLUSTER BY AUTO
AS
SELECT *
FROM delta.`s3://serasaexperian-ecs-datalakehouse-prd-bronze/ecs/auth/login/back/`;

ANALYZE TABLE auth_prd.bronze.tb_login_back COMPUTE DELTA STATISTICS;
ANALYZE TABLE auth_prd.bronze.tb_login_back COMPUTE STATISTICS;
OPTIMIZE auth_prd.bronze.tb_login_back;
VACUUM auth_prd.bronze.tb_login_back;
VACUUM auth_prd.bronze.tb_login_back LITE;

SET TAG ON TABLE auth_prd.bronze.tb_login_back ntt_migration = true;

ALTER TABLE auth_prd.bronze.tb_login_back SET TBLPROPERTIES (
  delta.enableDeletionVectors = true,
  delta.enableRowTracking = true,
  delta.enableChangeDataFeed = true,
  delta.deletedFileRetentionDuration = '90 day',
  delta.logRetentionDuration = '90 day',
  delta.autoOptimize.optimizeWrite = true,
  delta.autoOptimize.autoCompact = true);
```
BEFORE
```python
bucketBronze      = f"ecs-datalakehouse-prd-bronze/ecs/auth/{source}/back"
bronzePath        = "s3://serasaexperian-{}".format(bucketBronze)
```
AFTER:
```python
bronzePath        = f"auth_prd.bronze.tb_{source}_back"
```

- Jamais DROPAR TABELA, prefira TRUNCATE TABLE ou CREATE OR REPLACE TABLE
- No Unity sempre utilize a referencia da tabela e nunca o PATH:
BEFORE:
```python
if reprocess == "true":
  spark.sql(f"TRUNCATE TABLE delta.`{bronzePath}`")
  dbutils.fs.rm(bronzeCheckpoint, True)
  
  print(f'PATH BRONZE TRUNCADO            : {bronzePath}')
  print(f'PATH CHECKPOINT BRONZE DELETADO : {bronzeCheckpoint}')
else:
  pass
```
AFTER:
```python
if reprocess == "true":
    dbutils.fs.rm(f"/Volumes/auth_prd/bronze/checkpoints/ecs-datalakehouse-prd-checkpoints/ecs/auth/{source}/front")
    dbutils.fs.mkdirs(f"/Volumes/auth_prd/bronze/checkpoints/ecs-datalakehouse-prd-checkpoints/ecs/auth/{source}/front")
    spark.sql(f"TRUNCATE TABLE `{bronzePath}`")
    print(f'TABELA BRONZE TRUNCADA: {bronzePath}')
else:
  pass
```
- Utilize `spark.table(bronzePath)` ao inves de `spark.read.format("delta").load(bronzePath)`

- Sempre substitua input_file_name() por _metadata.file_path
```python
df = (df.withColumn("dt_load", current_date())
               .withColumn("ts_load_table", current_timestamp())
               .withColumn("file_name_raw", col("_metadata.file_path")))
```
# Checkpoint
- Todo catalogo tem um managed volume chamado `checkpoints` nos schemas bronze, silver e gold e esses devem ser o local de todos os checkpoints para um determinado produto (catalogo). Bastando criar a estrutura de pasta igual ao original:
```python
dbutils.fs.mkdirs(f"/Volumes/auth_prd/bronze/checkpoints/ecs-datalakehouse-prd-checkpoints/ecs/auth/{source}/back")
```
BEFORE:
```python
bucketChk         = f"ecs-datalakehouse-prd-checkpoints/ecs/auth/{source}/back"
bronzeCheckpoint  = "s3://serasaexperian-{}".format(bucketChk)
```

AFTER:
```python
bronzeCheckpoint = f"/Volumes/auth_prd/bronze/checkpoints/ecs-datalakehouse-prd-checkpoints/ecs/auth/{source}/back"
```

# Silver
- A lib DataQuality exige uma variavel de ambiente SPARK_VERSION com a versao do SPARK, normalmente a 3.5
```python
import os
os.environ['SPARK_VERSION'] = '3.5'
from DataQuality import *
```
- Na silver o path bronze deve ser substituida pela tabela bronze
BEFORE
```python
source = "login"
camada = "front"
bucketBronze      = f"ecs-datalakehouse-prd-bronze/ecs/auth/{source}/{camada}"
bronzePath           = "s3://serasaexperian-{}".format(bucketBronze, camada)
```

AFTER
```python
bronzePath           = f"auth_prd.bronze.tb_{source}_{camada}"
```

- Na silver o path silver vira tabela silver
BEFORE
```python
source = "login"
camada = "front"
fileName          = f"{source}/{camada}"
bucketSilver      = f"ecs-datalakehouse-prd-silver"
silverPath             = "s3://serasaexperian-{}/ecs/auth/{}".format(bucketSilver , fileName)
```
AFTER
```python
silverPath           = f"auth_prd.silver.tb_{source}_{camada}"
```

- Na silver checkpoint é sempre no volume managed checkpoints, sempre criando com o caminho original com dbutils.fs.mkdirs
BEFORE
```python
silverCheckpoint       = "s3://serasaexperian-{}/ecs/auth/{}/silver".format(bucketChk, fileName)
qualityCheckpointPath  = "s3://serasaexperian-{}/ecs/auth/{}/silver_quality/".format(bucketChk, fileName)
```
AFTER
```python
silverCheckpoint       = f"/Volumes/auth_prd/silver/checkpoints/ecs/auth/{source}/{camada}/silver"
qualityCheckpointPath  = "/Volumes/auth_prd/silver/checkpoints/ecs/auth/{source}/{camada}/silver_quality"
```

- Substitua read_stream_delta por spark.readStream.table()
BEFORE
```python
def read_stream_delta(spark: SparkSession, deltaPath: str) -> DataFrame:
    return spark.readStream.format("delta").load(deltaPath)
bronzeDF = read_stream_delta(spark, bronzePath)
```

AFTER
```python
bronzeDF = spark.readStream.table(bronzePath)
```
- 
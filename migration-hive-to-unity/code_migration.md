Ao ler uma tabela utilize o nome completo da tabela (FQN) ao invés de referência de Path
DE:



goldPath = "s3://serasaexperian-ecs-datalakehouse-prd-sensitive/corp/nike_replicacao/depara_hash"
goldTable = DeltaTable.forPath(spark, goldPath)
PARA:



goldTable = spark.table('corp_prd.sensitive.nike_replicacao_depara_hash')
Nesse exemplo foi alterado:

O uso de DeltaTable.forPath que tem como o input um path para spark.table que recebe um input o nome completo de uma tabela

DE




df_crm_step30 = spark.sql("""
select
    a.*,
    CASE WHEN b.cd_uuid IS NOT NULL THEN 1 ELSE 0 END AS fl_freemium_active
from
    df_crm_step29 as a
    left join delta.`s3a://ecs-platform-consumer-partnership-dump-prd/crm/freemium_users_subscription` as b 
    on a.cd_uuid = b.cd_uuid
""")
df_crm_step30.createOrReplaceTempView('df_crm_step30')
PARA



df_crm_step30 = spark.sql("""
select
    a.*,
    CASE WHEN b.cd_uuid IS NOT NULL THEN 1 ELSE 0 END AS fl_freemium_active
from
    df_crm_step29 as a
    left join crm_prd.gold.freemium_users_subscription as b 
    on a.cd_uuid = b.cd_uuid
""")
df_crm_step30.createOrReplaceTempView('df_crm_step30')
Nesse exemplo foi alterado:

Use de delta.`path` para nome completo da tabela

DE



from pyspark.sql.functions import col, countDistinct
# df_cm_email_opening2 is a TEMPORARY VIEW
df_cm_email_opening2 = spark.sql("SELECT * FROM df_cm_email_opening2")
big_numbers_data_portfolio = (df_cm_email_opening2
                              .filter(col("cadastrado_ecs") == 's')
                              .groupBy("Classificacao")
                              .agg(countDistinct("ds_email").alias("Valor"))
                              )
big_numbers_data_portfolio.write.mode("overwrite").saveAsTable("db_analytics.tb_big_numbers_data_portfolio")
PARA



from pyspark.sql.functions import col, countDistinct
# df_cm_email_opening2 is a TEMPORARY VIEW
df_cm_email_opening2 = spark.sql("SELECT * FROM df_cm_email_opening2")
big_numbers_data_portfolio = (df_cm_email_opening2
                              .filter(col("cadastrado_ecs") == 's')
                              .groupBy("Classificacao")
                              .agg(countDistinct("ds_email").alias("Valor"))
                              )
big_numbers_data_portfolio.write.mode("overwrite").saveAsTable("analytics_prd.gold.tb_big_numbers_data_portfolio")
Nesse exemplo foi alterado:

nome da tabela que antes estava localizada no hive_metastore no database db_analytics para o catalogo analytics_prd no schema gold

Ao gravar uma tabela utilize saveAsTable(name_table) em vez de save(path)
DE



esg_report\
          .write\
          .format('delta')\
          .mode('append')\
          .partitionBy('FiscalYear', 'Year', 'Month')\
          .save(goldPath)
PARA



nome_completo_tabela = "premium_prd.gold.table_name"
(
  esg_report
    .write
    .mode('append')
    .saveAsTable(nome_completo_tabela)
) 
spark.sql(f"ALTER TABLE {nome_completo_tabela} CLUSTER BY AUTO;")
Nesse exemplo foram alterados:

criação de variável com o nome completo da tabela

remoção de .format('delta'), pois é o formato default

utilização de parênteses para não precisar utilizar \ a cada quebra de linha

Inclusão de ALTER TABLE com CLUSTER BY AUTO ao invés de utilizar .partitionBy

DE



goldPathDLH = "s3a://serasaexperian-ecs-datalakehouse-prd-gold/ecs/auth/reports/engagement_score/"
try:
  if DeltaTable.isDeltaTable(spark, goldPathDLH):
    df_engage_5.write.format('delta')\
                      .option("overwriteSchema", "true")\
                      .option("mergeSchema", "true")\
                      .mode("overwrite")\
                      .option("replaceWhere", f"dt_reference = '{dt_ref}'")\
                      .save(goldPathDLH)
  else:
    df_engage_5.write.format("delta").partitionBy("dt_reference").save(goldPathDLH)
    spark.sql(f"CREATE TABLE db_reports_gold.tb_engagement_score USING DELTA LOCATION '{goldPathDLH}'")
  print(f"Updated partition dt_reference={dt_ref}, Gold table: db_reports_gold.tb_engagement_score")
except Exception as inst:
  print(str(inst))
  dbutils.notebook.exit(str(inst))
PARA



table_name = "corp_prd.sensitive.nike_replicacao_depara_hash"
try:
  if spark.sql(f"DESCRIBE DETAIL {table_name}").select("format").first()[0] == "delta":
    (df.write
                      .option("overwriteSchema", "true")
                      .option("mergeSchema", "true")
                      .mode("overwrite")
                      .option("replaceWhere", f"dt_reference = '{dt_ref}'")
                      .saveAsTable(table_name)
    )
  else:
    (
      df.write.mode("overwrite").saveAsTable(table_name)
    )
    spark.sql(f"ALTER TABLE {table_name} CLUSTER BY AUTO;") 
  print(f"Updated Gold table: {table_name}")
except Exception as inst:
  print(str(inst))
  dbutils.notebook.exit(str(inst))
Nesse exemplo foram alterados:

Uso de path por nome completo da tabela

Uso do método DeltaTable.isDeltaTable que recebe um path como input para DESCRIBE DETAIL para identificar se a tabela é delta

Uso de save(path) para saveAsTable(tabela)

Uso de partitionBy para CLUSTER BY AUTO

Ao ler uma tabela com read ou readStream utilize table(nome_tabela) ao invés de load(path)
DE



def process_streaming_data_report_solicit(bucket_bronze: str):
  bronze_path = bucket_bronze
  streamingDF = (spark.readStream.format("delta").load(bronze_path)
                 .drop("dt_load_bronze", "ts_load_bronze")
                 .drop("ds_generate_time")
                 .withColumn("dt_load_silver", current_date())
                  .withColumn("ts_load_silver", current_timestamp())
                  .withColumn("cd_uuid", premiumDecrypt(F.col("ds_identifier")))
                 )
  return streamingDF
PARA



def process_streaming_data_report_solicit(table_name_bronze: str):
  streamingDF = (spark.readStream.table(table_name_bronze)
                 .drop("dt_load_bronze", "ts_load_bronze")
                 .drop("ds_generate_time")
                 .withColumn("dt_load_silver", current_date())
                 .withColumn("ts_load_silver", current_timestamp())
                 .withColumn("cd_uuid", premiumDecrypt(F.col("ds_identifier")))
                 )
  return streamingDF
Nesse exemplo foram alterados:

parâmetro de entrada da função

removido format("delta") por ser o formato padrão

uso de load(path) para table(table_name)

Substitua input_file_name() por _metadata.file_path
DE



  rawDF = (rawDF.withColumn("dt_load", current_date())
               .withColumn("ts_load_table", current_timestamp())
               .withColumn("file_name_raw", input_file_name())
               )
PARA



rawDF = (rawDF.withColumn("dt_load", current_date())
               .withColumn("ts_load_table", current_timestamp())
               .withColumn("file_name_raw", col("_metadata.file_path")))
Nesse exemplo foi alterado:

Removido input_file_name() pela a função _metadata.file_path que é suportada pelo Unity Catalog

Shared utils
Ao utilizar um notebook utils de preferencia a um compartilhado a criar uma cópia local. Caso necessite costumizar um metodo ou função, crie uma nova no notebook compartilhado. O repositorio ecs-dataops-shared-utils contém a versão considerada oficial e padrão.

DE



%run /Users/ecs-databricks@br.experian.com/jobs/utils_autoloader


%run /Users/ecs-databricks@br.experian.com/jobs/utils
PARA



import sys
sys.path.append("/Workspace/Shared/ecs-dataops-shared-utils/")
from util_import import *
 

VIEW com tabelas Hive e Unity
Não é possível criar uma view que referencie tabelas do untiy com dataframes, view temporarias, tabelas no hive_metastore. Recomendamos migrar as tabelas referencias no hive_metastore para o Unity Catalog ou materializar em uma tabela a lógica envolvida e utilizar um job para manter a tabela atualizada.

Substituia forPath por forName em Merge
DE



deltaTable = DeltaTable.forPath(spark, silverPath)
  deltaTable.alias("t").merge(latestChangeForEachKey.alias("s"), f"s.{mergeId} = t.{mergeId}")\
                       .whenMatchedDelete(condition = "upper(s.Op) = 'D'")\
                       .whenMatchedUpdateAll(condition = "upper(s.Op) IN ('U', 'NULL') OR s.Op IS NULL")\
                       .whenNotMatchedInsertAll(condition = "upper(s.Op) IN ('I', 'U', 'NULL') OR s.Op IS NULL").execute()
PARA



deltaTable = DeltaTable.forName(spark, f"premium_prd.silver.tb_base_{databaseName}_{tableName}")
  deltaTable.alias("t").merge(latestChangeForEachKey.alias("s"), f"s.{mergeId} = t.{mergeId}")\
                       .whenMatchedDelete(condition = "upper(s.Op) = 'D'")\
                       .whenMatchedUpdateAll(condition = "upper(s.Op) IN ('U', 'NULL') OR s.Op IS NULL")\
                       .whenNotMatchedInsertAll(condition = "upper(s.Op) IN ('I', 'U', 'NULL') OR s.Op IS NULL").execute()
Utilize o OPTIMIZE, ANALYZE, VACUUM via SQL
DE



try:
  spark.sql(f"OPTIMIZE delta.`{bucketBronze}`")
  print("Optimize OK")
except Exception as inst:
  print(str(inst))
  pass
try:
  bronzeTable = DeltaTable.forPath(spark, bucketBronze)
  bronzeTable.vacuum()
  print("Vacuum OK")
except Exception as inst:
  print(str(inst))
  pass
PARA



fqn = "premium_prd.bronze.tb_base_demos"
spark.sql(f"ALTER TABLE {fqn} CLUSTER BY AUTO")
spark.sql(f"OPTIMIZE {fqn}")
spark.sql(f"ANALYZE TABLE {fqn} COMPUTE DELTA STATISTICS")
spark.sql(f"VACUUM {fqn}")
 

Alterar o método start() para toTable(), no caso de Streaming usando o nome da tabela
DE



df_stream_silver.start(bucket_silver).awaitTermination()
PARA



df_stream_silver.toTable(silver_table).awaitTermination()
Nesse exemplo foi alterado:

Uso de .start(path) para .toTable(nome_tabela)

Não é possível utilizar foreachBatch  e .toTable no mesmo streaming (Writing stream in Databricks with toTable doesn't execute foreachBatch )

 

Quando utilizar foreachBatch altere a função
Delta table streaming reads and writes | Databricks on AWS

Não é possível utilizar foreachBatch  e .toTable no mesmo streaming (Writing stream in Databricks with toTable doesn't execute foreachBatch ), então nesse caso não altere o .start() para .toTable e sim altere a função que roda no foreachBatch.

DE



streamingDF = process_streaming_data_report_solicit("s3://serasaexperian-ecs-datalakehouse-prd-bronze/ecs/antifraude/data-monitoring-report/data_monitoring_report/report_request/")
def upsertToDelta(microBatchOutputDF, batchId): 
  microBatchOutputDF.createOrReplaceTempView("updates")
  microBatchOutputDF.sparkSession.sql(f"""
            MERGE INTO delta.`{pathSilver}` as silver
            USING
            ( SELECT * except(row_number)
             FROM
                (SELECT
                 u.*,
                 row_number() OVER(PARTITION BY u.transaction_id ORDER BY u.updated_at DESC, u.expiration_date DESC) AS row_number
                 FROM updates u) where row_number = 1
            ) as new_records
            ON silver.transaction_id = new_records.transaction_id
            AND (silver.expiration_date < new_records.expiration_date OR silver.updated_at < new_records.updated_at )
            AND new_records.Op = 'U'
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED AND ((isnull(new_records.Op))  OR (new_records.Op = 'I')) THEN INSERT *
         """)
silverDFStream = create_stream_writer(
      dataframe=streamingDF,
      checkpoint=bucket_checkpoint + "silver/",
      trigger_once=type_read_stream, 
      name=checkpoint_name,
      mergeSchema=True,
      foreach_batch=upsertToDelta,
      mode="update"
      )
silverDFStream.start("s3://serasaexperian-ecs-datalakehouse-prd-silver/ecs/antifraude/data-monitoring-report/data_monitoring_report/report_request/").awaitTermination()
PARA



streamingDF = process_streaming_data_report_solicit("premium_prd.bronze.report_request")
def upsertToDelta(microBatchOutputDF, batchId): 
  microBatchOutputDF.createOrReplaceTempView("updates")
  microBatchOutputDF.sparkSession.sql(f"""
            MERGE INTO {tableSilver} as silver
            USING
            ( SELECT * except(row_number)
             FROM
                (SELECT
                 u.*,
                 row_number() OVER(PARTITION BY u.transaction_id ORDER BY u.updated_at DESC, u.expiration_date DESC) AS row_number
                 FROM updates u) where row_number = 1
            ) as new_records
            ON silver.transaction_id = new_records.transaction_id
            AND (silver.expiration_date < new_records.expiration_date OR silver.updated_at < new_records.updated_at )
            AND new_records.Op = 'U'
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED AND ((isnull(new_records.Op))  OR (new_records.Op = 'I')) THEN INSERT *
         """)
silverDFStream = create_stream_writer(
      dataframe=streamingDF,
      checkpoint=bucket_checkpoint + "silver/",
      trigger_once=type_read_stream, 
      name=checkpoint_name,
      mergeSchema=True,
      foreach_batch=upsertToDelta,
      mode="update"
      )
silverDFStream.start().awaitTermination()
Nesse exemplo foram alterados:

uso de path para nome completo da tabela

Na função de merge utilize sparkSession
Delta table streaming reads and writes | Databricks on AWS 

DE



def upsertToDelta(microBatchOutputDF, batchId): 
  microBatchOutputDF.createOrReplaceTempView("updates")
  microBatchOutputDF._jdf.sparkSession().sql(f"""
            MERGE INTO {pathSilver} as silver
            ...
PARA



def upsertToDelta(microBatchOutputDF, batchId): 
  microBatchOutputDF.createOrReplaceTempView("updates")
  microBatchOutputDF.sparkSession.sql(f"""
            MERGE INTO {tableSilver} as silver
            ...

## Raw/sensitive
Checkpoint
Altere o checkpoint para Volume checkpoints no schema raw. Esse volume é do tipo managed. Mantenha a estrutura de pasta original. Por exemplo s3://serasaexperian-ecs-datalakehouse-prd-checkpoints/ecs/events/premium_gac/raw/ é alterado para /Volumes/premium_prd/raw/checkpoints/ecs/events/premium_gac/raw/



import sys
sys.path.append("/Workspace/Shared/ecs-dataops-shared-utils/")
from migration_import import create_checkpoint
checkpoint_path = "s3://serasaexperian-ecs-datalakehouse-prd-checkpoints/ecs/events/premium/raw/"
catalog = "premium_prd"
schema = "raw"
create_checkpoint(checkpoint_path, catalog,schema)
Em seguida altere o parametro de checkpoints no notebook

DE



bucketChk       = "serasaexperian-ecs-datalakehouse-prd-checkpoints"
checkpointPath  = "s3a://{}/ecs/events/premium/raw/".format(bucketChk)
PARA



checkpointPath  = "/Volumes/premium_prd/raw/checkpoints/ecs/events/premium/raw/"
SQS
Sera necessario cadastrar o SQS como um Service Credential. Solicite ao @Costa, Guilherme Ribeiro criar um card ao @Duarte, Jefferson para atribuir as permicoes a role do Unity de producao ao SQS. Em seguida, solicite ao @Vale, Vinicius  a criacao da service credential. Apos isso sera necessario alterar o Autoloader para incluir o parametro "databricks.serviceCredential". Durante a migracao utilize o SQS de teste "https://sqs.us-east-1.amazonaws.com/093785888205/ia-databricks-datalakehouse-prd-unity-catalog-prd"



if debugMode:
  sqsPath = "https://sqs.us-east-1.amazonaws.com/093785888205/ia-databricks-datalakehouse-prd-unity-catalog-prd"
else:
  sqsPath         = "https://sqs.us-east-1.amazonaws.com/093785888205/ia-databricks-events-s3-premium-prd-prd"
service_credential_sqs = "unity-093785888205-services-aws-prd-service-credential"
rawDF = (spark.readStream
              .format("cloudFiles")
              .option("cloudFiles.IncludeExistingFiles", "true")
              .option("cloudFiles.useNotifications", "true")
              .option("cloudFiles.region", "us-east-1")
              .option("cloudFiles.queueUrl", sqsPath)
              .option("databricks.serviceCredential",service_credential_sqs)
              .option("cloudFiles.format", "text")
              .schema(rawSchema)
              .table(rawPath))
debugMode
Crie os widgets de debugMode e migrationExecution e atribua o valor True para ambos os widgets.



dbutils.widgets.text("debugMode", "False")
debugMode = True if getArgument("debugMode").lower() == "true" else False
dbutils.widgets.text("migrationExecution", "False")
migrationExecution = True if getArgument("migrationExecution").lower() == "true" else False
Source
Verifique se existe um volume externo apontando para o bucket de origem no schema raw. Caso não, é necessário verificar se a role do Unity tem permissão para acessar o bucket, para isso entre em contato com @Vale, Vinicius.

Substitua o source de path para Volume

DE



bucketRaw       = "ecs-events-premium-prd" 
rawPath         = "s3a://{}/".format(bucketRaw)
rawDF = (spark.readStream
              .format("cloudFiles")
              .option("cloudFiles.IncludeExistingFiles", "true")
              .option("cloudFiles.useNotifications", "true")
              .option("cloudFiles.region", "us-east-1")
              .option("cloudFiles.queueUrl", sqsPath)
              .option("cloudFiles.format", "text")
              .schema(rawSchema)
              .load(rawPath))
PARA



rawPath = "/Volumes/premium_prd/raw/events_gac_prd"
rawDF = (spark.readStream
              .format("cloudFiles")
              .option("cloudFiles.IncludeExistingFiles", "true")
              .option("cloudFiles.useNotifications", "true")
              .option("cloudFiles.region", "us-east-1")
              .option("cloudFiles.queueUrl", sqsPath)
              .option("databricks.serviceCredential",service_credential_sqs)
              .option("cloudFiles.format", "text")
              .schema(rawSchema)
              .load(rawPath))
Destination
Como o Autloader (CloudFiles) salva como delta o destino deve ser registrado como tabela. Sendo preferivel uma tabela a um Volume quando o conteudo esta em delta.

Primeiro registramos a tabela no Unity



import sys
sys.path.append("/Workspace/Shared/ecs-dataops-shared-utils/")
from migration_import import create_raw_table
source_path = "s3://serasaexperian-ecs-datalakehouse-prd-raw/ecs/events/premium/"
catalog_destination = "premium_prd"
schema_destination = "raw"
table_destination = "tb_events"
cluster_by_column = ["dt_load"]
create_raw_table(source_path, catalog_destination, schema_destination,table_destination, cluster_by_column)
Alteramos a referência na variavel rawPathDLH ou arquivo de parametro

DE



bucketRawDLH    = "serasaexperian-ecs-datalakehouse-prd-raw"
rawPathDLH      = "s3a://{}/ecs/events/premium/".format(bucketRawDLH)
PARA



rawPathDLH      = "premium_prd.raw.tb_events"
Em seguida alteramos o .load(Path) para .table(full_qualified_name)

DE



PARA 



Shared utils
Substitua o utils, utils_autoloader ou qualquer variação de nome pelo Shared utils, caso não exista a função ou método desejado entre em contato com @Vale, Vinicius .
DE



%run /Users/ecs-databricks@br.experian.com/jobs/utils
PARA



import sys
sys.path.append("/Workspace/Shared/ecs-dataops-shared-utils/")
from util_import import *
Caso o notebook utilize um notebook compartilhado de tranformacoes verifique se o notebook ja esta disponivel em /Workspace/Shared/ecs-dataops-shared-utils. Caso nao, entre em contato com @Vale, Vinicius .



%run /Workspace/Shared/ecs-dataops-shared-utils/events_operations
 

create_stream_writer
Sem foreachBatch

DE



originToRawWriter = create_stream_writer(
                                          dataframe        = rawTransformed,
                                          checkpoint       = checkpointPath,
                                          trigger_once     = False,
                                          name             = namedRawStream,  
                                          mergeSchema      = True,
                                          partition_column = ["dt_load"]
                                      )
originToRawWriter.start(rawPathDLH)
PARA



rawPathDLH      = "premium_prd.raw.tb_events"
originToRawWriter = create_stream_writer(
                                          dataframe        = rawTransformed,
                                          checkpoint       = checkpointPath,
                                          trigger_once     = False,
                                          name             = namedRawStream,  
                                          mergeSchema      = True,
                                          partition_column = ["dt_load"]
                                      )
originToRawWriter.toTable(rawPathDLH)
 

com foreachBatch

DE



PARA



 

migrationExecution
A execução após a migração e os testes são executados no fluxo do migrationExecution que cria checkpoint a partir da data da tabela dataops_prd.control.migration_date. Para Structured Streaming e batch basta filtrar o _metadata.file_modification_time >= a data da tabela dos dataframes de leitura da raw.

Observação : A forma correta de se utilizar a opção modifiedAfter é  .option("modifiedAfter",  migration_date),  não .option(“cloudFiles.modifiedAfter", migration_date).



rawSchema = StructType([StructField("value", StringType())])
if migrationExecution:
  migration_date =  spark.sql(f"select cast(timestamp as STRING) from dataops_prd.control.migration_date where concat(catalog,'.', schema,'.', table) = '{rawPathDLH}' LIMIT 1").first()[0]
  rawDF = (spark.readStream
              .format("cloudFiles")
              .option("cloudFiles.IncludeExistingFiles", "true")
              .option("cloudFiles.useNotifications", "true")
              .option("cloudFiles.region", "us-east-1")
              .option("modifiedAfter", migration_date)
              .option("cloudFiles.queueUrl", sqsPath)
              .option("databricks.serviceCredential",service_credential_sqs)
              .option("cloudFiles.format", "text")
              .schema(rawSchema)
              .table(rawPath))
else:
  rawDF = (spark.readStream
                .format("cloudFiles")
                .option("cloudFiles.IncludeExistingFiles", "true")
                .option("cloudFiles.useNotifications", "true")
                .option("cloudFiles.region", "us-east-1")
                .option("cloudFiles.queueUrl", sqsPath)
                .option("databricks.serviceCredential",service_credential_sqs)
                .option("cloudFiles.format", "text")
                .schema(rawSchema)
                .table(rawPath))
Validacao
Todos as execucoes sao feitas com debugMode=True e parametro de reprocess=False. 

Teste 1

Recrie o checkpoint create_checkpoint

Recrie a tabela create_raw_table

Rode com migrationExecution como True e type_process como base_full. O resultado do validate_tables deve permanecer o mesmo, sendo tolerado aumento na data de hoje.

Rode com migrationExecution como False e type_process como base_full. O resultado do validate_tables é possível que toda a estrutura seja alterada.

Teste 2

Recrie o checkpoint create_checkpoint

Recrie a tabela create_raw_table

Rode com migrationExecution como True e type_process como incremental. O resultado do validate_tables deve aumentar em um ou mais datas.

Rode com migrationExecution como False e type_process como incremental. O resultado do validate_tables deve aumentar apenas no dia de hoje, mas muito menos.
## Bronze
Checkpoint
Busque no notebook ou  arquivo de parametro o caminho do checkpoint da bronze, normalmente está no bucket s3://serasaexperian-ecs-datalakehouse-prd-checkpoints/. Algumas possibilidades:

bronzeCheckpoint

Crie a estrutura de pasta do checkpoint no Volume checkpoint do schema bronze



import sys
sys.path.append("/Workspace/Shared/ecs-dataops-shared-utils/")
from migration_import import create_checkpoint
checkpoint_path = "s3://serasaexperian-ecs-datalakehouse-prd-checkpoints/ecs/antifraude/base/subscription/bronze/ecs_antifraude_subscription_free/"
catalog = "premium_prd"
schema = "bronze"
create_checkpoint(checkpoint_path, catalog,schema)
Altere no notebook ou arquivo de parametros o novo local do checkpoint. Para o exemplo temos
DE



bronzeCheckpoint   = "s3://{}/ecs/antifraude/base/{}/bronze/{}".format(bucketChk, databaseName, tableName)
PARA



bronzeCheckpoint   = f"/Volumes/{catalog}/bronze/checkpoints/ecs/antifraude/base/{databaseName}/bronze/{tableName}"
Source
Busque no notebook ou arquivo de parametros o path origem, normalmente está apontando para o bucket raw s3://serasaexperian-ecs-datalakehouse-prd-raw/  ou sensitive s3://serasaexperian-ecs-datalakehouse-prd-sensitive/

Identifique se há um Volume no schema raw ou sensitive que aponte para o prefix.
Exemplo: 
Dado que o Path do source é:



rawPath = "s3://serasaexperian-ecs-datalakehouse-prd-raw/ecs/antifraude/base/subscription/ecs_antifraude_subscription_free"
O Volume /Volumes/premium_prd/raw/raw_ecs_antifraude contém o prefix necessário. Dessa forma substituimos o valor do source por:



rawPath = "/Volumes/premium_prd/raw/raw_ecs_antifraude/base/subscription/ecs_antifraude_subscription_free"
Caso não identifique um Volume que contenha o prefix necessário entre em contato com @Vale, Vinicius. 

Em alguns casos o source pode ser uma tabela presente no schema raw.

Destination
Busque no notebook ou arquivo de parametros o path de destino, normalmente está apontando para o bucket bronze s3://serasaexperian-ecs-datalakehouse-prd-bronze. O Path será transformado em tabela com liquid clustering ativado. Para isso além do Path será necessário identificar a coluna de partição, normalmente está presente como parametro do autoloader ou do método do utils create_stream_writer. Caso não encontre uma coluna de particionamento utilize CLUSTER BY AUTO. Liquid Clustering avalia apenas as 32 primeiras colunas para realizar clusterização (antigo particionamento). 

Crie a tabela bronze:



import sys
sys.path.append("/Workspace/Shared/ecs-dataops-shared-utils/")
from migration_import import create_bronze_table
source_path = "s3://serasaexperian-ecs-datalakehouse-prd-bronze/ecs/antifraude/base/subscription/ecs_antifraude_subscription_free"
catalog_destination = "premium_prd"
schema_destination = "bronze"
table_destination = "tb_base_subscription_ecs_antifraude_subscription_free"
cluster_by_column = ["dt_load"]
create_bronze_table(source_path,catalog_destination,schema_destination,table_destination, cluster_by_column)
Substitua a variavel ou parametro que representa o path da bronze pela tabela criada.



bronzePath = f"premium_prd.bronze.tb_base_subscription_ecs_antifraude_subscription_free"
debugMode
Crie os widgets de debugMode e migrationExecution e atribua o valor True para ambos os widgets.



dbutils.widgets.text("debugMode", "False")
debugMode = True if getArgument("debugMode").lower() == "true" else False
dbutils.widgets.text("migrationExecution", "False")
migrationExecution = True if getArgument("migrationExecution").lower() == "true" else False
Shared utils
Substitua o utils, utils_autoloader ou qualquer variação de nome pelo Shared utils, caso não exista a função ou método desejado entre em contato com @Vale, Vinicius .
DE



%run /Users/ecs-databricks@br.experian.com/jobs/utils
PARA



import sys
sys.path.append("/Workspace/Shared/ecs-dataops-shared-utils/")
from util_import import *
Caso o notebook utilize um notebook compartilhado de tranformacoes verifique se o notebook ja esta disponivel em /Workspace/Shared/ecs-dataops-shared-utils. Caso nao, entre em contato com @Vale, Vinicius .



%run /Workspace/Shared/ecs-dataops-shared-utils/events_operations
Identificando o ambiente
DE



var_workspace = spark.conf.get("spark.databricks.workspaceUrl")
if var_workspace == "experian-serasa-ecs-dev.cloud.databricks.com":
   var_ambiente = "dev"
elif var_workspace == "experian-serasa-ecs-labs.cloud.databricks.com":
   var_ambiente = "prd"
print(f"var_ambiente  :  {var_ambiente}")
PARA



import sys
sys.path.append("/Workspace/Shared/ecs-dataops-shared-utils/")
from util_import import verify_environment
var_ambiente = verify_environment()
Parametro de reprocessamento
Caso código possua parametro de reprocessamento

DE



if reprocess:
  dbutils.fs.rm(bronzePath, True)
  dbutils.fs.rm(bronzeCheckpoint, True)
  spark.sql(f"drop table if exists db_premium_bronze.tb_base_{databaseName}_{tableName}")
PARA



if reprocess:
  dbutils.fs.rm(bronzeCheckpoint, True)
  spark.sql(f"TRUNCATE TABLE {bronzePath}")
Substitua input_file_name() por _metadata.file_path
DE



  rawDF = (rawDF.withColumn("dt_load", current_date())
               .withColumn("ts_load_table", current_timestamp())
               .withColumn("file_name_raw", input_file_name())
               )
PARA



rawDF = (rawDF.withColumn("dt_load", current_date())
               .withColumn("ts_load_table", current_timestamp())
               .withColumn("file_name_raw", col("_metadata.file_path")))
migrationExecution
A execução após a migração e os testes são executados no fluxo do migrationExecution que cria checkpoint a partir da data da tabela dataops_prd.control.migration_date. Para Structured Streaming e batch basta filtrar o _metadata.file_modification_time >= a data da tabela dos dataframes de leitura da raw.



if migrationExecution:
  migration_date =  spark.sql(f"select cast(timestamp as STRING) from dataops_prd.control.migration_date where concat(catalog,'.', schema,'.', table) = '{bronzePath}' LIMIT 1").first()[0]


dfFull = spark.read.parquet(fullLoadRawPath)
rawFullDF = read_stream_raw_parquet(spark, fullLoadRawPath, dfFull.schema).withColumn("Op", lit("null"))
if migrationExecution:
    rawFullDF = rawFullDF.filter(col("_metadata.file_modification_time")>=lit(migration_date))
Para Autoloader



 

awaitTermination
foreachBatch


toTable
Caso o streaming não utilize foreachBatch  foreachBatch altere o .start(bronzePath) por .toTable(bronzePath)

DE



  rawToBronzeWriterIncr = create_stream_writer(
      dataframe=transformedIncrDF,
      checkpoint=bronzeCheckpoint,
      trigger_once=True,    
      name=namedBronzeStreamIncremental,
      mergeSchema=True
  )
  # start streaming
  qry = rawToBronzeWriterIncr.start(bronzePath)
  qry.awaitTermination()
PARA



  rawToBronzeWriterIncr = create_stream_writer(
      dataframe=transformedIncrDF,
      checkpoint=bronzeCheckpoint,
      trigger_once=True,
      name=namedBronzeStreamIncremental,
      mergeSchema=True
  )
  # start streaming
  rawToBronzeWriterIncr.toTable(bronzePath).awaitTermination()

Jobs streaming continuos
Em caso jobs continuos recomendamos testar utilizando o debugMode



rawToBronzeWriter = create_stream_writer(
                                          dataframe        = rawDF,
                                          checkpoint       = bronzeCheckpoint,
                                          trigger_once     = True if debugMode else False,
                                          name             = namedBronzeStream,
                                          mergeSchema      = True,
                                          partition_column = ["dt_load"]
                                        )
if debugMode:
  rawToBronzeWriter.toTable(bronzePath).awaitTermination()
else:
  rawToBronzeWriter.toTable(bronzePath)
Operações de manutenção
DE



try:
  spark.sql(f"OPTIMIZE delta.`{bronzePath}`")
  print("Optimize OK")
except Exception as inst:
  print(str(inst))
  pass
try:
  bronzeTable = DeltaTable.forPath(spark, bronzePath)
  bronzeTable.vacuum()
  print("Vacuum OK")
except Exception as inst:
  print(str(inst))
  pass
PARA



spark.sql(f"OPTIMIZE {bronzePath}")
spark.sql(f"ANALYZE TABLE {bronzePath} COMPUTE STATISTICS")
spark.sql(f"VACUUM {bronzePath}")
 

Validacao
Todos as execucoes sao feitas com debugMode=True e parametro de reprocess=False. 

Teste 1

Recrie o checkpoint create_checkpoint

Recrie a tabela create_bronze_table

Rode com migrationExecution como True e type_process como base_full. O resultado do validate_tables deve permanecer o mesmo, sendo tolerado aumento na data de hoje.

Rode com migrationExecution como False e type_process como base_full. O resultado do validate_tables é possível que toda a estrutura seja alterada.

Teste 2

Recrie o checkpoint create_checkpoint

Recrie a tabela create_bronze_table

Rode com migrationExecution como True e type_process como incremental. O resultado do validate_tables deve aumentar em um ou mais datas.

Rode com migrationExecution como False e type_process como incremental. O resultado do validate_tables deve aumentar apenas no dia de hoje, mas muito menos.
## Silver
Checkpoint
Busque no notebook ou arquivo de parametro o caminho do checkpoint da bronze, normalmente está no bucket s3://serasaexperian-ecs-datalakehouse-prd-checkpoints/. Algumas possibilidades:

bucketCheckpoint

Podemos ter tambem o checkpoint de quality utilizado no processo de quality. Esse normalmente está no bucket s3://serasaexperian-ecs-datalakehouse-prd-checkpoints/. Algumas possibilidades:

qualityCheckpointPath

Em ambos os casos utilize a funcao create_checkpoint para criar a estrutura de pastas.



catalog = "premium_prd"
schema = "silver"
create_checkpoint("s3://serasaexperian-ecs-datalakehouse-prd-checkpoints/silver/antifraude/gac/checkout/order_status_log/", catalog, schema)
create_checkpoint("s3://serasaexperian-ecs-datalakehouse-prd-checkpoints/silver/antifraude/gac/checkout/quality-order_status_log/", catalog, schema)
Se o checkpoint existe apenas a referencia no notebooks, mas nao existe no bucket checkpoint crie a estrutura de pasta diretamente no Volume:



try:
  assert dbutils.fs.ls(source_path)
except Exception as e:
  dbutils.fs.mkdirs(f"/Volumes/{catalog}/{schema}/checkpoints/ecs/premium/dynamic_report_operation/operations/silver-full/")
Source
Necessário alterar a bronze de Path para Full qualified Name, ou seja, catalogo.schema.tabela.

DE



bucketBronze    = "serasaexperian-ecs-datalakehouse-prd-bronze"
bronzePath      = "s3://{}/ecs/antifraude/base/{}/{}".format(bucketBronze, databaseName, tableName)
PARA



bronzePath      = f"premium_prd.bronze.tb_base_{databaseName}_{tableName}"
Caso a tabela ainda nao exista, identifique o job responsavel por ler da raw para bronze e siga as etapas de Migrando Raw/Sensitive to Bronze - Dados ECS - Confluence e utilize a funcao de criacao de tabelas bronze.

Destination
Busque no notebook ou arquivo de parametros o path de destino, normalmente está apontando para o bucket bronze s3://serasaexperian-ecs-datalakehouse-prd-silver. O Path deve ser transformado em tabela com liquid clustering ativado. Utilize a funcao create_silver_table.

DE



bucketSilver    = "serasaexperian-ecs-datalakehouse-prd-silver"
silverPath      = "s3://{}/ecs/antifraude/base/{}/{}".format(bucketSilver, databaseName, tableName)
PARA



silverPath      = f"premium_prd.silver.tb_base_{databaseName}_{tableName}"
debugMode
Crie os widgets de debugMode e migrationExecution e atribua o valor True para ambos os widgets.



dbutils.widgets.text("debugMode", "False")
debugMode = True if getArgument("debugMode").lower() == "true" else False
dbutils.widgets.text("migrationExecution", "False")
migrationExecution = True if getArgument("migrationExecution").lower() == "true" else False
Shared utils
Substitua o utils, utils_autoloader ou qualquer variação de nome pelo Shared utils, caso não exista a função ou método desejado entre em contato com vinicius.vale@br.experian.com ou adicione o me
DE



%run /Users/ecs-databricks@br.experian.com/jobs/utils
PARA



import sys
sys.path.append("/Workspace/Shared/ecs-dataops-shared-utils/")
from util_import import *
Remova o pip install de libraries
Retire qualquer pip install, as libraries devem ser instaladas a nivel de task no job.json. Nao esqueca de instalar essas bibliotecas no cluster all purpose que está utilizando para testar o codigo migrado.

Identificando o ambiente
DE



var_workspace = spark.conf.get("spark.databricks.workspaceUrl")
if var_workspace == "experian-serasa-ecs-dev.cloud.databricks.com":
   var_ambiente = "dev"
elif var_workspace == "experian-serasa-ecs-labs.cloud.databricks.com":
   var_ambiente = "prd"
print(f"var_ambiente  :  {var_ambiente}")
PARA



import sys
sys.path.append("/Workspace/Shared/ecs-dataops-shared-utils/")
from util_import import verify_environment
var_ambiente = verify_environment()
DataQuality
Caso o repositorio possua um notebook de dataquality com a funcao function_insert_metrics_dq substitua pela versao Shared. Nessa versao o codigo esta compativel com o Unity e  setado a variavel de ambiente SPARK_VERSION necessario para as novas versoes do Pydeequ.

DE



%run ./DataQuality_Import
from DataQuality import *
PARA



import sys
sys.path.append("/Workspace/Shared/ecs-dataops-shared-utils/")
from dataquality_import import *
from DataQuality import *
Alem disso, atualize a referencia na funcao DeequVerification para a tabela do Unity.

DE



PARA



premium_prd_prd.silver.tb_freemium_migrated_user
 

Verificacao isDeltaTable
DE



if DeltaTable.isDeltaTable(spark, goldPathDLH):
PARA



if spark.sql(f"DESCRIBE DETAIL {table_name}").select("format").first()[0] == "delta":
  condition = True
else:
  condition = False
if condition:
  ...
Parametro de reprocessamento
Caso código possua parametro de reprocessamento. Sendo rm para Volumes e truncate para tabelas.

DE



if reprocess:
  dbutils.fs.rm(bronzePath, True)
  dbutils.fs.rm(bronzeCheckpoint, True)
  spark.sql(f"drop table if exists db_premium_bronze.tb_base_{databaseName}_{tableName}")
PARA



if reprocess:
  dbutils.fs.rm(bronzeCheckpoint, True)
  spark.sql(f"TRUNCATE TABLE {bronzePath}")
 

utilize table(nome_tabela) ao invés de load(path)
DE



bronzeDF = spark.read.load(pathBronze)
PARA



bronzeDF = spark.read.table(pathBronze)
migrationExecution
A execução após a migração e os testes são executados no fluxo do migrationExecution que cria checkpoint a partir da data da tabela dataops_prd.control.migration_date. Para Structured Streaming e batch basta filtrar o _metadata.file_modification_time >= a data da tabela dos dataframes de leitura da raw.



if migrationExecution:
  migration_date =  spark.sql(f"select cast(timestamp as STRING) from dataops_prd.control.migration_date where concat(catalog,'.', schema,'.', table) = '{bronzePath}' LIMIT 1").first()[0]


bronzeDF = spark.sql(query)
if migrationExecution:
      bronzeDF = bronzeDF.filter(col("_metadata.file_modification_time")>=lit(migration_date))
 

Na função de merge upsertToDelta utilize sparkSession 
DE



microBatchOutputDF._jdf.sparkSession().sql(...)
PARA



microBatchOutputDF.sparkSession.sql(...)
Alem disso, altere a referencia das tabelas para o Unity.

 

Utilize start em foreachBatch
Não é possível utilizar foreachBatch  e .toTable no mesmo streaming (Writing stream in Databricks with toTable doesn't execute foreachBatch ), então nesse caso não altere o .start() para .toTable e sim altere a função upsertToDelta ou insert_dataQuality  que roda no foreachBatch.



bronzeToSilverDataQuality = create_stream_writer(
    dataframe=silverDF,
    checkpoint=dataQuality,
    name=nameddataQuality,
    trigger_once=True,
    mergeSchema=True,
    foreach_batch=insert_dataQuality,
    mode="update"
)
bronzeToSilverDataQuality.start().awaitTermination()
Operações de manutenção
DE



try:
  spark.sql(f"OPTIMIZE delta.`{pathSilver}`")
  print("Optimize OK")
except Exception as inst:
  print(str(inst))
  pass
try:
  bronzeTable = DeltaTable.forPath(spark, pathSilver)
  bronzeTable.vacuum()
  print("Vacuum OK")
except Exception as inst:
  print(str(inst))
  pass
PARA



spark.sql(f"OPTIMIZE {pathSilver}")
spark.sql(f"ANALYZE TABLE {pathSilver} COMPUTE STATISTICS")
spark.sql(f"VACUUM {pathSilver}")
 

Validacao
Todos as execucoes sao feitas com debugMode=True e parametro de reprocess=False. 

Teste 1

Recrie o checkpoint create_checkpoint

Recrie a tabela create_silver_table

Rode com migrationExecution como True e type_process como base_full. O resultado do validate_tables deve permanecer o mesmo, sendo tolerado aumento na data de hoje.

Rode com migrationExecution como False e type_process como base_full. O resultado do validate_tables é possível que toda a estrutura seja alterada.

Teste 2

Recrie o checkpoint create_checkpoint

Recrie a tabela create_silver_table

Rode com migrationExecution como True e type_process como incremental. O resultado do validate_tables deve aumentar em um ou mais datas.

Rode com migrationExecution como False e type_process como incremental. O resultado do validate_tables deve aumentar apenas no dia de hoje, mas muito menos.
## Gold
Crie o repositorio Criação dos Repositórios - Data Driven - Confluence

Dalvito Console: Ferramentas → Gerenciamentos de Repositorios → criar no repositorio no Bitbucket 

Time: DATAOPS

Linguagem: PYTHON

DEPLOY: DATABRICKS

Nome do projeto:  ecs-dataops-prd-etl-<produto>-nome-repo 
Nomenclatura de Jobs - Databricks
 

Execute as etapas do 
Estratégias de Migração | Fluxo de Migração Repos
 

Execute a funcao create_gold_table para criar a tabela.

Altere as referências de tabela para as versao unity das tabelas que ja foram migradas.

DE



cancelados = """
          select document, max(name) as name, max(email) as email, max(phone) as phone, user_id, min(cast(cancellation_date as date)) as cancellation_date,
                 min(datediff(cast(current_date as date),cast(cancellation_date as date))) as dias_cancel
            from db_premium_silver.tb_base_subscription_ecs_antifraude_subscription 
           where cancellation_date is not null
             -- and datediff(cast(current_date as date),cast(cancellation_date as date)) <= '{}'
             and length(decryptTel(phone)) >= 13
           group by document, user_id
        """.format(RANGE_DAYS)
df_cancelados = spark.sql(cancelados)
df_cancelados.createOrReplaceTempView('tb_cancelados')
PARA



cancelados = """
          select document, max(name) as name, max(email) as email, max(phone) as phone, user_id, min(cast(cancellation_date as date)) as cancellation_date,
                 min(datediff(cast(current_date as date),cast(cancellation_date as date))) as dias_cancel
            from premium_prd.silver.tb_base_subscription_ecs_antifraude_subscription 
           where cancellation_date is not null
             -- and datediff(cast(current_date as date),cast(cancellation_date as date)) <= '{}'
             and length(decryptTel(phone)) >= 13
           group by document, user_id
        """.format(RANGE_DAYS)
df_cancelados = spark.sql(cancelados)
df_cancelados.createOrReplaceTempView('tb_cancelados')
 

Altere a criacao da tabela gold para managed table e alterere o partitionBy para clusterBy

DE



goldPath  = "s3a://serasaexperian-ecs-datalakehouse-prd-gold/ecs/premium/televendas/exclientes_new/"
tbName = "tb_televendas_exclientes"
df_exclientes_gold_new.write.format('delta') \
                      .partitionBy("dt_load") \
                      .option("overwriteSchema", "true") \
                      .option("mergeSchema", "true") \
                      .mode("overwrite") \
                      .option("replaceWhere", f"dt_load = '{dateLoad}'")\
                      .save(goldPath)
spark.sql(f"CREATE TABLE IF NOT EXISTS db_premium_gold.{tbName} USING DELTA LOCATION '{goldPath}'")
print(f"db_premium_gold.{tbName} updated!")
PARA



goldPath  = "premium_prd.gold.tb_televendas_exclientes"
(df_exclientes_gold_new.write
                      .clusterBy("dt_load")
                      .option("overwriteSchema", "true")
                      .option("mergeSchema", "true")
                      .mode("overwrite")
                      .option("replaceWhere", f"dt_load = '{dateLoad}'")
                      .saveAsTable(goldPath))
 

Uma etapa necessária para migração do job é a criação da tarefa no Jenkins para atualização via esteira CI/CD .

Criação de nova tarefa no Jenkins: 
Tutorial de criação de job no jenkins

## Delivery
 Delivery sao processos que descriptografam o conteudo de uma tabela em um arquivo e disponibilizam em um destino. As tabelas utilizadas para gerar a tabela que sera descriptografada podem ser de qualquer camada ou produto. Mesma que a tabela em si seja salva em um schema silver o processo em si diverge de uma bronze para silver e esta mais proximo de um processo de serving/gold.

 

Delivery CRM
Utiliza o notebook  delivery_crm_to_sftp que deve ser apontado para a versao do ecs-dataops-shared-utils:



dbutils.notebook.run("/Workspace/Shared/ecs-dataops-shared-utils/delivery_crm_to_sftp", 3600, DELIVERY_CONFIG)
Esse notebook depende de duas bibliotecas que devem estar presentes no job.json e cluster de teste:



              {
                  "pypi": {
                      "package": "python-gnupg==0.5.0"
                  }
              },
              {
                  "pypi": {
                      "package": "pysftp==0.2.9"
                  }
              },
Esse notebook recebe como entrada um dicionario, quando estiver testando utilize debugMode como True. Isso desativara a etapa de envio.



DELIVERY_CONFIG = {
  "catalog": f"{catalog}",
  "schema": f"{schema}",
  "table_name": f"tb_{domain}_{subdomain}_{context}",
  "path_sftp": f"import",
  "file_name": f"{DATE_EXECUTION}_{domain}_{subdomain}_{context}.csv",
  "encrypted_cols": "{'col_name': 'ds_email', 'encrypted_type': 'email'}, {'col_name': 'ds_phone', 'encrypted_type': 'phone'}",
  "file_separator": "|"
}
if debugMode:
    DELIVERY_CONFIG["debugMode"] = True
Normalmente tabelas de delivery sao criadas lendo origens via batch e fazendo overwrite da tabela destino. Dessa forma, nao utilize migrationExecution pois o processo nao utiliza checkpoints.

Na parte de quality uitlize a versao shared



import sys
sys.path.append("/Workspace/Shared/ecs-dataops-shared-utils/")
from dataquality_import import *
insert_metrics_deequ(catalog_name, schema_name, table_name)
df_quality_verify = spark.read.table(full_table_name)
dq = DeequVerification(spark, full_table_name, df_quality_verify).validation(alert=True, p_type = 'crm-delivery')
Utilize o DBR 14.3LTS para manter a compatilbilidade com a descriptografia do Salesforce.

Utilize a lib de criptografia para manter a compatibilidade com a descriptografia do Salesforce:



/Volumes/dataops_prd/libraries/libs/crm/ecs_dataops_utils_cryptography-0.10-py3-none-any.wh

# RELEASE (DEPLOY)
Recrie os checkpoints

Recrie as tabelas, para evitar reprocessamento completo das camadas subsequentes a criação deve utilizar dt_load ou dt_load_bronze ou dt_load_silver para a data de criacao do checkpoint na migrationExecution, para isso use o parametro date_modification na funcao de criacao de tabela da migration_import. A criacao da tabela deve usar versao 16 de preferencia, em caso de erro no registro de metricas utilize o DBR 14.3 LTS

Confira o job.json. A lib de criptografia deve ser a mesma do job original. Caso a lib nao exista no volume de libraries utilize a funcao move_lib_dbfs_to_volume da migration_import.

Suba o PR ate a master

Realize a execucao do job com parametro migrationExecution=True

Realize a execuao do job sem o parametro migrationExecution
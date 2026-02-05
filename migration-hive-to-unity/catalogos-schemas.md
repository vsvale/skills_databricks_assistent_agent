Catálogos
What are catalogs in Databricks? | Databricks on AWS  

Um catálogo é a principal unidade de organização de dados no modelo de governança de dados do Databricks Unity Catalog. Iremos utilizar um catálogo por produto ou time, por exemplo o catálogo de premium em produção é o premium_prd, já o catálogo do time de datascience no ambiente de desenvolvimento se chama models_dev, seguindo o padrão de nomenclatura <produto/time>_<environment>. Cada catálogo contém um bucket próprio na account, de forma que será possível estimar os custos de armazenamento de um produto ou time. Os buckets seguem o seguinte padrão de nomenclatura:

s3://serasaexperian-ecs-datalakehouse-<enviroment>-<produto/time>Ex: serasaexperian-ecs-datalakehouse-prd-premium

Os catálogos devem respeitar as limitações (Names | Databricks on AWS ) e de prefência utilizar o nome sem abreviações seguido do ambiente. Ex: marketplace_insurance_prd

Um catálogo armazena schemas, não sendo possível criar assets de dados diretamente no catálogo

Catálogos de um ambiente são estão disponíveis no workspace do ambiente. Então não é possível encontrar dados produtivos no ambiente de desenvolvimento, mesmo que compartilhem o mesmo metastore.

Limit catalog access to specific workspaces | Databricks on AWS  

Todo usuário nos ambientes terão as seguintes permissões nos catálogos:

USE CATALOG: permissão necessária para que o usuário interaja com os assets dentro do catálogo, permite que o usuário veja que o catálogo existe no workspace.

Unity Catalog privileges and securable objects | Databricks on AWS  

BROWSE: permissão necessária para que um usuário veja os metadados no Catalog Explorer, nos resultados de buscas, lineage e ao information_schema

Unity Catalog privileges and securable objects | Databricks on AWS  

Schemas Default
Foram definidos alguns schemas padrões para os catálogos. Outros schemas podem ser criados para atender necessidades das equipes e produtos. Schemas custom precisam receber o termo Qualify em sua descrição e a tag qualify recebendo os valores bronze, silver ou gold. Os schemas default são:

raw: Contém volumes que apontam para o bucket raw (s3://serasaexperian-ecs-datalakehouse-prd-raw), podendo conter tabelas caso o processo de ingestão em casos de cópia de raw para raw, além de volumes de checkpoint necessários para o envio. Os arquivos nessa camada ainda não possuem a criptografia do Datalake e por isso apenas o service principal de engenharia tem acesso aos assets desse schema.

bronze: Contém tabelas delta com dados mais próximos da raw, mas com dados sensíveis e sigilosos criptografados com a criptografia do Datalake. Pode conter volumes de checkpoints quando o processo é realizado via autoloader e structured streaming. Somente o service principal de engenharia tem acesso aos assets desse schema, pois os dados ainda não estão prontos para serem utilizados para analytics e serving.

silver: Contém tabelas delta com dados refinados e parcialmente processados, ideal para Machine Learning criar features e Analytics extrair suas visões e análises detalhadas. Pode conter dados históricos por isso é essencial utilizar as colunas ao qual a tabela foi clusterizada ou particionada. Contém também Volumes de checkpoint e schemas nos casos necessários. Para democratizar o acesso todos os usuários possuem acesso ao schema por isso é importante disponibilizar apenas dados classificados como internal e com mascaramento de dados PII e sensíveis nesse schema.

gold: Contém tabelas delta com dados prontos para gerar dashboards, utilizar o Genie e ser compartilhado com outros times. Na gold é possível conter views e materialized views com visões especificas para determinadas partições ou com lógicas de negócio. Essas tabelas devem necessariamente conter metadados como comentário a nível de tabela e coluna os descrevendo. Assim como a silver todos possuem acesso ao schema.

control: Contém tabelas e Volumes de controle e parâmetros para salvar informações como uma partição lida, data de último processamento, último id lido, parâmetros usados durante o processamento, json de schemas, json de parâmetros e qualquer informação ou propriedade que uma vez salva agilize o processamento de um job. Somente o service principal de engenharia tem acesso aos assets desse schema.

delivery: Pode conter Volumes e tabelas necessárias para o processo de delivery. Normalmente após o envio as tabelas geradas são deletadas, pois podem guardar dados PII descriptografados, por isso apenas o service principal de engenharia possui acesso a esse schema.

sandbox: Schema para dar autonomia ao time dono do catálogo. Permite prototipagem e validação de novas ideias e desenvolvimento de análises ad hoc com dados disponíveis em silver e gold antes de subir para gold produtiva. Esse schema é gerenciada pelo time podendo criar e deletar assets a vontade, porém esse schema é exclusivo para o time do produto do catálogo. O service principal não tem permissão de ler esse schema dessa forma não é possível utilizá-lo para jobs. Por meio de Request for Access será possível compartilhar de forma temporária o acesso para outros colaboradores e times a tabelas nesse schema.

sensitive: Contém Volumes e tabelas cujo controle deve ser altamente restrito e dado individualmente e de forma temporária. O Request For Access estará habilitado para essas tabelas sendo os aprovadores o time de governança.

stage: Contém tabelas snapshots de outras tabelas, normalmente utilizado para calcular o delta de alterações de uma fonte de dados ou comparar dois períodos. São tabelas intermediarias, mas que não podem ser apagadas entre execuções dos jobs ou um período definido. Somente o service principal de engenharia tem acesso aos assets desse schema.

temp: Contém tabelas temporárias e intermediarias que serão apagadas em um período definido após sua criação. O time do catálogo é responsável por esse schema, podendo criar e deletar assets a vontade, mas não tem a permissão de dar acesso a outros times.

vector: Contém tabelas, funções e modelos de Vector search (Create vector search endpoints and indexes | Databricks on AWS ). Apenas o service principal de engenharia tem acesso aos assets desse schema.

USE CATALOG e USE SCHEMA
O catálogo default do ambiente continua sendo o hive_metastore (Manage the default catalog | Databricks on AWS   ). Por isso qualquer tabela ou view criada sem referência de namespace (database.tabela ou catalog.schema.tabela) iria acabar sendo criado no hive_metastore.default. Para evitar essa situação revogamos a permissão de todos os de criar VIEWS e TABELAS no hive_metastore.default. Para que o código continue funcionando é necessário identificar os 3 níveis ou utilizar os comandos USE CATALOG e USE SCHEMA

USE CATALOG | Databricks on AWS  

USE SCHEMA | Databricks on AWS  

DE



%sql
CREATE OR REPLACE TABLE tb_big_numbers_data_portfolio AS (
select
  Classificacao,
  count(distinct ds_email) as Valor
from
  df_cm_email_opening2
where
  cadastrado_ecs = 's'
group by
  1
 )
PARA

OPÇÃO 1 adicionar 3 level namespace



%sql
CREATE OR REPLACE TABLE analytics_prd.gold.tb_big_numbers_data_portfolio
CLUSTER BY AUTO AS (
select
  Classificacao,
  count(distinct ds_email) as Valor
from
  df_cm_email_opening2
where
  cadastrado_ecs = 's'
group by
  1
 )
OPÇÃO 2 adicionar USE CATALOG e USE SCHEMA



%sql
USE CATALOG;
USE SCHEMA;
CREATE OR REPLACE TABLE tb_big_numbers_data_portfolio
CLUSTER BY AUTO AS (
select
  Classificacao,
  count(distinct ds_email) as Valor
from
  df_cm_email_opening2
where
  cadastrado_ecs = 's'
group by
  1
 );


%python
spark.sql("USE CATALOG")
spark.sql("USE SCHEMA")
df = spark.table("df_cm_email_opening2")
df_filtered = df.filter(col("cadastrado_ecs") == 's')
df_grouped = df_filtered.groupBy("Classificacao").agg(countDistinct("ds_email").alias("Valor"))
df_grouped.write.clusterBy("Classificacao").saveAsTable("tb_big_numbers_data_portfolio")
Freezing de hive_metastore databases
Durante a migração os databases do hive_metastore são congelados, ou seja, aplicamos DENY de MODIFY e CREATE evitando que novas tabelas sejam criadas ou tabelas sejam atualizadas por usuários. Os jobs continuam funcionando normalmente desde que rodem com os services principals ecs_ci_cd_datalake@br.experian.com, henrique.machado@br.experian.com e ecs-databricks@br.experian.com.

Novas tabelas e jobs devem ser criados apontando para os catálogos no Unity Catalog.

3 level namespace
Após uma tabela ser migrada para o Unity Catalog ela passa a ter um namespace de 3 níveis, catalog.schema.tabela, ao contrário dos 2 níveis presentes no hive_metastore, composto por database.tabela.

Databricks recomenda que ao interagir com tabelas delta sempre utilizemos o nome completo (fully-qualified name) da tabela ao invés do caminho do arquivo (file path) (Databricks tables | Databricks on AWS  )

DE



CREATE OR REPLACE TABLE db_analytics.tb_big_numbers_data_portfolio AS (
select
  Classificacao,
  count(distinct ds_email) as Valor
from
  df_cm_email_opening2
where
  cadastrado_ecs = 's'
group by
  1
 )
PARA



CREATE OR REPLACE TABLE analytics_prd.gold.tb_big_numbers_data_portfolio
CLUSTER BY AUTO AS (
select
  Classificacao,
  count(distinct ds_email) as Valor
from
  df_cm_email_opening2
where
  cadastrado_ecs = 's'
group by
  1
 )
Nesse exemplo foram alterados:

nome da tabela que antes estava localizada no hive_metastore no database db_analytics para o catalogo analytics_prd no schema gold

Inclusão de Cluster by auto para automaticamente identificar as melhores chaves de clusterização a tabela

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

hive_metastore é considerado um catálogo, sendo possível representá-lo como hive_metastore.<database>.<tabela>

## Schema
def get_comment(catalog,schema,schema_path):
    product = catalog.replace('_prd', '')
    match schema:
        case "bronze":
          return f"To store raw data ingested from {product}. Contains unprocessed data in delta format, PII is already encrypted, serving as the first layer in the data pipeline. Stored in {schema_path}"
        case "silver":
          return f"To store cleansed and enriched data from {product}. Contains data that has been refined and partially processed, making it suitable for more detailed analysis. Stored in {schema_path}"
        case "gold":
          return f"To store highly processed and aggregated data from {product}. Contains final datasets that are ready for business intelligence and reporting purposes. Stored in {schema_path}"
        case "control":
          return f"To store control tables used during data processing. Contains metadata and control tables that guide and manage the processing workflows. Stored in {schema_path}"
        case "temp":
          return f"To store temporary tables and volumes from {product}. Contains intermediate datasets that are used for processing and analysis. Stored in {schema_path}"
        case "raw":
          return f"Schema for raw data tables and volumes from {product} data product, stored in {schema_path}"
        case "sensitive":
          return f"Schema for tables and volumes with unencrypted PII data from {product} data product, stored in {schema_path}"
        case "sandbox":
          return f"Schema for tables and volumes used in {product} team for experiments, stored in {schema_path}"
        case "stage":
          return f"Schema for tables and volumes used in {product} for staging and snapshots, stored in {schema_path}"
        case "ingestion":
          return f"Schema for tables and volumes used in ingestion from {product} data product, stored in {schema_path}"
        case "delivery":
          return f"Schema for tables and volumes used in delivery from {product} data product, stored in {schema_path}"
        case "control":
          return f"Schema for control tables from {product} data product, stored in {schema_path}"
        case "vector":
          return f"Schema for tables and volumes used in vector search index from {product} data product, stored in {schema_path}"
        case "models":
          return f"Schema for tables and volumesused to serve data science models for the {product} data product, stored in {schema_path}"
        case "features":
          return f"Schema for tables and volumes used in data science features from {product} data product, stored in {schema_path}"
        case "semantic":
          return f"Schema for tables and volumes used in analytics OBT and platinium tables from {product} data product, stored in {schema_path}"
        case _:
            return f"Schema for {schema} tables and volumes from {product} data product, stored in {schema_path}"


    catalog_comment = f'''
      # {product} catalog
      Stored in {catalog_path}

      ## Description
      The {catalog} catalog is designed to store and manage all tables related to {product} data product. It organizes data into various schemas to support different stages of data processing and usage, including raw data, processed data, control mechanisms, and specilized data assetes such as machine learning models and feature stores.

      ## Structure
      ### Raw Schema
      Purpose: To store raw data.
      Usage: Contains raw data in its original form, before any processing or transformation.

      ### Bronze Schema
      Purpose: To store raw data ingested from various sources.
      Usage: Contains unprocessed data in delta format, PII is already encrypted, serving as the first layer in the data pipeline

      ### Silver Schema
      Purpose: To store cleansed and enriched data.
      Usage: Contains data that has been refined and partially processed, making it suitable for more detailed analysis.

      ### Gold Schema
      Purpose: To store highly processed and aggregated data.
      Usage: Contains final datasets that are ready for business intelligence and reporting purposes.

      ### Control Schema
      Purpose: To store control tables used during data processing.
      Usage: Contains metadata and control tables that guide and manage the processing workflows.

      ### Models Schema
      Purpose: To store tables for ML and GenAI models.
      Usage: Contains machine learning and artificial intelligence models developed and used within the data product.

      ### Features Schema
      Purpose: To store feature store tables.
      Usage: Contains features extracted from data, which are used for training machine learning models and other analytical purposes.

      ### Temp Schema
      Purpose: To store temporary tables.
      Usage: Contains tables that are used for temporary data processing or storage.

      ### Vector Schema
      Purpose: To store vector search tables.
      Usage: Contains tables optimized for vector search operations, supporting advanced search functionalities.

      ### Ingestion Schema
      Purpose: To store tables for data ingestion.
      Usage: Contains tables used for data ingestion, such as files from Volumes, api returns, tables created via UI.

      ### Delivery Schema
      Purpose: To store tables for data delivery.
      Usage: Contains tables used for data delivery for external systems, like DynamoDB.

      ### Semantic Schema
      Purpose: To store tables for semantic for business users.
      Usage: Contains tables used for serving for end users.
      '''
## Default grants
  for schema_sp_grant in ['raw','ingestion','bronze','delivery','control','vector','stage','silver','gold','models','features','semantic']:
  spark.sql(f"GRANT APPLY TAG, CREATE FUNCTION, CREATE MATERIALIZED VIEW, CREATE MODEL, CREATE MODEL VERSION, CREATE TABLE, CREATE VOLUME, EXECUTE, MODIFY, READ VOLUME,  REFRESH, SELECT, USE SCHEMA, WRITE VOLUME ON SCHEMA {catalog}.{schema_sp_grant} TO `ecs_ci_cd_datalake@br.experian.com`")

for schema_sp_download in ['temp','raw','ingestion','bronze','delivery','control','vector','sandbox','stage','silver','gold','models','features','semantic']:
  spark.sql(f"GRANT USE SCHEMA, SELECT ON SCHEMA {catalog}.silver TO `544cb3ff-43e7-4e1c-bb8c-85c55b27b021`")

for schema_name in ['raw','bronze','silver','gold','sandbox','temp','features','models','semantic']:
  if spark.sql(f"SHOW SCHEMAS IN `{catalog}` LIKE '{schema_name}'").count() > 0:
    spark.sql(f"CREATE VOLUME IF NOT EXISTS {catalog}.{schema_name}.checkpoints")
    for principal_name in ['NTT-MIGRATION','ecs_ci_cd_datalake@br.experian.com','APP-ECSBR-DATABRICKS-ADMIN','APP-ECSBR_Databricks_Sustentacao']:
      spark.sql(f"GRANT READ VOLUME, WRITE VOLUME ON VOLUME {catalog}.{schema_name}.checkpoints TO `{principal_name}`")
spark.sql(f"GRANT MANAGE ON SCHEMA {catalog}.sensitive TO `APP-ECSBR_Databricks_Governanca`")

def create_schema(catalog,schema):
  schema_exists = spark.sql(f"SHOW SCHEMAS IN {catalog} LIKE '{schema}'").count() > 0
  if schema_exists:
    print(f"Schema {schema} already exist in {catalog}")
  else:
    spark.sql(f"USE CATALOG {catalog}")

    catalog_path = spark.sql(f"DESCRIBE CATALOG EXTENDED {catalog}").filter("info_name = 'Storage Root'").select("info_value").collect()[0][0]
    schema_path = f"{catalog_path}{schema}"
    comment_schema = get_comment(catalog,schema,schema_path)
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema} MANAGED LOCATION '{schema_path}' COMMENT '{comment_schema}'")
    spark.sql(f"ALTER SCHEMA {catalog}.{schema} OWNER TO `APP-ECSBR-DATABRICKS-ADMIN`")
    spark.sql(f"ALTER SCHEMA {catalog}.{schema} INHERIT PREDICTIVE OPTIMIZATION")
    print(f"Schema {schema} created in {catalog}")

    for catalog_row in catalogs_df.select("catalog").collect():
  catalog = catalog_row.catalog
  print(catalog)
  for schema_item in new_schemas:
    create_schema(catalog,schema_item)
  if schema_item == "silver":
    spark.sql(f"GRANT USE SCHEMA, SELECT ON SCHEMA {catalog}.silver TO `account users`")
  if schema_item == "gold":
    spark.sql(f"GRANT USE SCHEMA, SELECT ON SCHEMA {catalog}.gold TO `account users`")
  if schema_item == "models":
    spark.sql(f"GRANT USE SCHEMA, SELECT ON SCHEMA {catalog}.models TO `account users`")
    spark.sql(f"GRANT APPLY TAG, EXECUTE, READ VOLUME, REFRESH, SELECT, USE SCHEMA ON SCHEMA {catalog}.models TO `APP-ECSBR_Databricks_DataScience`")
  if schema_item == "features":
    spark.sql(f"GRANT APPLY TAG, EXECUTE, READ VOLUME, REFRESH, SELECT, USE SCHEMA ON SCHEMA {catalog}.features TO `APP-ECSBR_Databricks_DataScience`")
  if schema_item == "semantic":
    spark.sql(f"GRANT USE SCHEMA, SELECT ON SCHEMA {catalog}.semantic TO `account users`")
  if schema_item == "raw":
    spark.sql(f"GRANT APPLY TAG, EXECUTE, MODIFY, READ VOLUME, REFRESH, SELECT, USE SCHEMA ON SCHEMA {catalog}.raw TO `APP-ECSBR_Databricks_Sustentacao`")
  for schema_sp_grant in ['raw','ingestion','bronze','delivery','control','vector','stage','silver','gold','models','features']:
    try:
      spark.sql(f"GRANT APPLY TAG, CREATE FUNCTION, CREATE MATERIALIZED VIEW, CREATE MODEL, CREATE MODEL VERSION, CREATE TABLE, CREATE VOLUME, EXECUTE, MODIFY, READ VOLUME,  REFRESH, SELECT, USE SCHEMA, WRITE VOLUME   ON SCHEMA {catalog}.{schema_sp_grant} TO `ecs_ci_cd_datalake@br.experian.com`")
    except Exception as e:
      print(f"Error granting {schema_sp_grant} schema to ecs_ci_cd_datalake@br.experian.com")

  for schema_sp_download in ['temp','raw','ingestion','bronze','delivery','control','vector','sandbox','stage','silver','gold','models','features']:
    spark.sql(f"GRANT USE SCHEMA, SELECT ON SCHEMA {catalog}.silver TO `544cb3ff-43e7-4e1c-bb8c-85c55b27b021`")
  spark.sql(f"GRANT MANAGE ON SCHEMA {catalog}.sensitive TO `APP-ECSBR_Databricks_Governanca`")

  for schema_name in ['raw','bronze','silver','gold','sandbox','temp','features','models','semantic']:
  if spark.sql(f"SHOW SCHEMAS IN `{catalog}` LIKE '{schema_name}'").count() > 0:
    spark.sql(f"CREATE VOLUME IF NOT EXISTS {catalog}.{schema_name}.checkpoints")
    for principal_name in ['NTT-MIGRATION','ecs_ci_cd_datalake@br.experian.com','APP-ECSBR-DATABRICKS-ADMIN','APP-ECSBR_Databricks_Sustentacao']:
      spark.sql(f"GRANT READ VOLUME, WRITE VOLUME ON VOLUME {catalog}.{schema_name}.checkpoints TO `{principal_name}`")

https://docs.databricks.com/aws/en/admin/users-groups/groups  

Não é necessário ter permissão ao grupo do time para ter acesso as tabelas gold e silver do time

Os grupos no Unity Catalog estão a nível de Account e estarão vinculados ao grupo do IDC. Dessa forma, será necessário solicitar acesso via IDC e não via equipe DataSecOps que não terão mais permissão de conceder acesso. Todos os usuários possuem acesso as tabelas dos schemas gold e silver, fazer parte do grupo lno somente permite ter acesso as tabelas dos schemas temp e sandbox desse catalogo. Fazer parte do grupo do lno significa que você faz parte do time de lno. Para fins de homologação e ações pontuais será possível realizar Request for Access para uma tabela nos schemas sandbox e sensitive, os aprovadores normalmente serão os data stewards e time de governança, respectivamente. 

Somente service principals tem acesso de escrita nos schemas default bronze, silver, gold, raw, stage, vector, delivery e sensitive. Para schemas não default vai depender da classificação do 
Segue relação de permissões em um catálogo do time:

 ALL usersTeamSP engineerbronzeFALSEFALSEMODIFYcontrolFALSEREADMODIFYdeliveryFALSEFALSEMODIFYgoldREADREADMODIFYrawFALSEFALSEMODIFYsandboxFALSEMODIFYFALSEsensitiveFALSEFALSEFALSEsilverREADREADMODIFYstageFALSEREADMODIFYtempFALSEMODIFYFALSEvectorFALSEREADMODIFY
  
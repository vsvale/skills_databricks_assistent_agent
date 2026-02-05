CLUSTER BY clause (TABLE) | Databricks on AWS  

Use liquid clustering for tables | Databricks on AWS  

Announcing General Availability of Liquid Clustering | Databricks Blog  

Announcing Automatic Liquid Clustering | Databricks Blog 

O Liquid Clustering substitui o partitionBy e o ZORDER no particionamento de tabelas, deixando a Databricks responsável por gerenciar o layout e operações de optimização dos dados na tabela. 

Liquid Clustering não é compativel com particionamento (partitionBy) ou ZORDER

Databricks recomenda utilizar Liquid Clustering para toda tabela do tipo delta. É possível escolher até quatro clustering keys, mas para tabelas menores do que 10Tb é recomendado apenas uma key (Use liquid clustering for tables | Databricks on AWS  ).

Para evitar selecionar chaves de particionamento erradas que podem degradar a performance da tabela a Databricks recomenda utilizar o automatic liquid clustering, disponível para tabelas gerenciadas (managed tables). Essa funcionalidade deixa a cargo da Databricks escolher as clustering keys com base nas queries mais executadas e com base nas statistics da tabela. As estatisticas coletadas com ANALYZE e predictive optimization leva em consideração apenas as 32 colunas, incluindo colunas aninhadas em structs. Dessa forma, é necessário manter as colunas utilizadas para clusterização ou que são candidatas a chave de clusterização, no caso do modo AUTO, entre as 32 primeiras da tabela. É recomendado utilizar apenas 1 coluna no CLUSTER BY, é possível até 3 colunas, mas o excesso de colunas pode reduzir a performance da tabela.

Ativar liquid clustering em uma tabela não particionada:



ALTER TABLE corp_prd.gold.demo_table CLUSTER BY (dt_referencia);
OPTIMIZE corp_prd.gold.demo_table FULL;
Ativar liquid clustering em uma tabela particionada, passando as keys:



-- SQL
CREATE TABLE corp_prd.gold.demo_table CLUSTER BY (dt_referencia)
AS SELECT * FROM hive_metastore.db_corp.demo_table 


# CTAS using DataFrameWriterV1
df = spark.read.table("hive_metastore.db_premium.sample_table")
df.write.clusterBy("dt_referencia").saveAsTable("premium_prd.gold.sample_table")


# CTAS using DataFrameWriterV2
df = spark.read.table("hive_metastore.db_premium.sample_table")
df.writeTo("premium_prd.gold.sample_table").using("delta").clusterBy("dt_referencia").create()


# Structured Streaming write
(spark.readStream.table("hive_metastore.db_premium.sample_table")
  .writeStream
  .clusterBy("dt_referencia")
  .option("checkpointLocation", checkpointPath)
  .toTable("premium_prd.gold.sample_table")
)
Utilizar Automatic Liquid Clustering



ALTER TABLE premium_prd.gold.sample_table CLUSTER BY AUTO;
Para utilizar o Liquid Clustering é necessário utilizar Databricks Runtime 15.2+. Esse recurso esta disponível para structured streaming a partir de DBR 16+ e o Automatic Liquid Clustering a partir de DBR 15.4+. Para ativar Automatic Liquid Clustering em uma tabela é necessário ter a permissionMODIFY
Utilize seu código entre parênteses ao invés de \ para quebra de linha
Torna o código mais legível e organizado.

DE



df_tb_events = spark\
              .read\
              .table('db_lno_silver.tb_events')\
              .select(\
                        col('dt_event'),\
                        col('vl_offer'),\
                        when(round(col('pc_discount_offer'), 13).isNull(), 0)\
                          .otherwise(round(col('pc_discount_offer'), 13)).alias('pc_discount_offer'),\
                        col('cd_uuid'),\
                        col('ds_contract'),\
                        col('cd_offer')\
                      )\
              .filter(f'\
                        cd_event = 103 \
                        and dt_event between "{dt_start}" and "{dt_end}"\
                        and ds_integration_type <> "lead-contact"\
                        and pc_discount_offer < 100\
                      ')
PARA



query = f"""
cd_event = 103 and dt_event between "{dt_start}" and "{dt_end}" and ds_integration_type <> "lead-contact"
and pc_discount_offer < 100
"""
df_tb_events = (
  spark
    .read
    .table('db_lno_silver.tb_events')
    .select(
        col('dt_event'),
        col('vl_offer'),
        when(round(col('pc_discount_offer'), 13).isNull(), 0)
            .otherwise(round(col('pc_discount_offer'), 13)).alias('pc_discount_offer'),
        col('cd_uuid'),
        col('ds_contract'),
        col('cd_offer')
    )
    .filter(query)
Não deixe notebooks dentro de Workspace pessoal
Não utilize em jobs notebooks de seu workspace, isso atrela o processo produtivo a seu usuário, o que leva a falhas no caso de seu usuário seja desativado da plataforma.

EXEMPLO



%run /Repos/vinicius.vale@br.experian.com/ecs-dataops-data-pipeline-datawarehouse-thoth-utils/src/databricks/workspace/UTILS
Padronize importações
Evite importar a biblioteca várias vezes ou uma vez a cada método.

Nunca dê um import *. Importe apenas os métodos necessários.

Não importe repetidas vezes entre células do notebooks, importe no inicio do código para facilitar a manutenção do código

DE



from pyspark.sql import functions as F
import pandas as pd
from pyspark.sql.functions import explode
from pyspark.sql.functions import col
from pyspark.sql.functions import to_date, date_format
from datetime import *
from dateutil.relativedelta import relativedelta
import pandas as pd
PARA



from pyspark.sql.functions import explode, col, to_date, date_format
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
Evite dropar ou dar replace em tabelas
Evite dropar a tabela or realizar create or replace table. Essa ação faz com metadados, como comentários e permissões sejam perdidos. Realize .write.mode('overwrite') ou truncate seguido de insert. Caso utilize drop ou replace, não esqueça de adicionar os comentários na tabela e coluna e verifique os grants.

Não utilize dbutils como um DROP
Ações envolvendo paths diretamente exigem permissões na Extenal Location, nenhum usuário incluindo os services principals terão permissões atribuídas diretamente as External Location. Com a ativação do Federation para hive_metastore (catálogo legacy_hive_catalog) tentativas de apagar tabelas diretamente pelo location com um cluster Unity Catalog enabled, dbutils.fs.rm("s3://serasaexperian-ecs-datalakehouse-prd-gold/ecs/dataops/monitoring/listjob/",True), o seguinte erro será apresentado:



com.databricks.sql.managedcatalog.acl.UnauthorizedAccessException: PERMISSION_DENIED: User does not have MODIFY on Table 'legacy_hive_catalog.db_dataops.tb_cost_jobs_databricks'.
No Unity Catalog os services principals não iram receber acesso a todas as tabelas do ambiente como atualmente ocorre, serão criados diferentes service principals que terão as mínimas permissões necessárias para execução do processo do produto ou da equipe. Em caso de erros de permissão com um job sendo executado por um service principal favor procure um administrador do ambiente do time de evolução.

Não utilizem comandos que alterem diretamente o path de uma tabela, pois exigem permissões adicionais. Nesses casos prefiram realizar um TRUNCATE da tabela para preservar os metadados, no caso DROP TABLE ou um CREATE OR REPLACE TABLE não esqueça de criar um ALTER TABLE adicionando novamente os comentários e tags.

Não utilize pandas puro
Pandas é executado inteiramente no driver, o que é mais lento e exige collect() que está propensos a Out Of Memory (OOM) ou a crash de drive. De preferência a executar transformações em pyspark ou SQL. Em exceções onde apenas pandas possui alguma funcionalidade utilize pyspark.pandasPandas API on Spark | Databricks on AWS  

Remova actions desnecessárias
Comandos como .count(),  display alteram o plano de execução podendo diminuir a performance do job. Mantenha apenas comandos necessários para aplicar as regras de negócio. Caso seja necessário realize as ações no final do notebook.



%sql
desc db_auth_silver.tb_login


display(dt_max_load_login_ac)


print(dt_ini_current_fy)


df.show()
Utilizar variáveis para nomes de tabelas que precisam ser referenciadas mais de 1 vez
Caso seja necessário chamar uma tabela mais de uma vez, o nome da mesma deve ser definido em uma variável. Isso é importante pois caso precise fazer qualquer alteração futura, é necessário alterar em apenas um local.

Evite a utilização de %run
Não utilize %run para criar notebooks de orquestração, utilize tasks dos jobs para isso. Esse tipo de ação cria job efemeros que dificultam a observabilidade e monitoramento. Esse tipo de notebook deve ser refatorado.

Caso o notebook contenham uma série de funções que serão utilizados por outro notebook, salve esse arquivo como um file .py e importe o mesmo no notebook. Você pode utilizar o magic command %%writefile especificando o path para criar o workspace file .py.



%%writefile ./utils/utils_functions.py
def add_timestamp_column(spark,table_name):
    """
    Adds a current timestamp column to the specified table.
    Parameters:
    table_name (str): The name of the table to which the timestamp column will be added.
    Returns:
    DataFrame: A DataFrame with an additional column 'current_timestamp' containing the current timestamp.
    """
    from pyspark.sql.functions import current_timestamp
    df = spark.table(table_name)
    df_with_timestamp = df.withColumn("current_timestamp", current_timestamp())
    return df_with_timestamp
image-20250404-163333.png
Um arquivo com extensão .py pode ser importado em um notebook



from utils.utils_functions import add_timestamp_column
display(add_timestamp_column(spark,'dataops_prd.control.cluster_info'))
image-20250404-163431.png
Não utilize %run para passar variáveis entre notebooks, pois dificulta a manutenção. Utilize arquivos JSON, YAML, job parameters (Parameterize jobs | Databricks on AWS ) ou tasks values (Use task values to pass information between tasks | Databricks on AWS  ) para essa finalidade.

Não utilize variáveis globais dentro de funções
Uma função deve receber como parâmetros todas as variáveis necessárias para sua execução. 

DE



//variável table definida fora do método ou até em outro notebook
def sync_data()
  df = spark.table(table)   
PARA



def sync_data(table)
  df = spark.table(table)
Nesse exemplo foi alterado:

Adicionado o parâmetro table que recebe o nome completo da tabela 

Substitua múltiplos .withColumn por .withColumns
Facilita a leitura do código, reduz a quantidade de operações de transformação e melhora o desempenho.

DE



esg_report.filter('ReportType = "Payments"')\
 .withColumn('DebtValue', regexp_replace(format_number(col('DebtValue'), 2), ",", ""))\
 .withColumn('RemainingValue', regexp_replace(format_number(col('RemainingValue'), 2), ",", ""))\
 .withColumn('Savings', regexp_replace(format_number(col('Savings'), 2), ",", ""))\
 .withColumn('Consumers', col('Consumers').cast('string'))\
 .withColumn('Agreements', col('Agreements').cast('string'))\
 .createOrReplaceTempView('tb_esg_report')
PARA



new_columns = {
  'DebtValue': regexp_replace(format_number(col('DebtValue'), 2), ",", ""),
  'RemainingValue': regexp_replace(format_number(col('RemainingValue'), 2), ",", ""),
  'Savings': regexp_replace(format_number(col('Savings'), 2), ",", ""),
  'Consumers': col('Consumers').cast('string'),
  'Agreements', col('Agreements').cast('string')  
}
(
esg_report
  .filter('ReportType = "Payments"')
  .withColumns(new_columns)
  .createOrReplaceTempView('tb_esg_report')
)
Não salvar arquivos temporários no dbfs:/FileStore/
Salve arquivos temporários no temp do driver, caso o mesmo precise ser utilizado por outra task então salve em Volumes e apague quando o mesmo não for mais necessário.

DE



df.write.mode("overwrite").csv("dbfs:FileStore/temp_xpto/sample_data.csv")
PARA

Exemplo temporário no driver



df.write.mode("overwrite").csv("/temp/sample_data.csv")
 

Exemplo em Volume



file_path = "/Volumes/premium_prd/sandbox/report_request/csv/sample_data.csv"
(df.repartition(1)
 .write
 .format("csv")
 .mode("overwrite")
 .option("header", "true")
 .save(file_path)
)
dbutils.fs.rm(file_path)
Não utilize o catálogo legacy_hive_catalog para processos e jobs
Hive metastore federation: enable Unity Catalog to govern tables registered in a Hive metastore | Databricks on AWS  

Esse catálogo foi criado com a finalidade de permitir a exploração via Genie AI/BI dos dados disponíveis no hive_metastore. Não recomendamos utilizar essas tabelas como tabelas Unity em jobs, pois as mesmas podem ser corrompidas pelos processos hoje vigentes no HSM. Caso necessite reparar uma tabela nesse catalogo para atualizar os metadados utilize:



REPAIR TABLE legacy_hive_catalog.db_database.tb_tabela SYNC METADATA
Qualquer alteração no metadados das tabelas no legacy_hive_catalog reflete no hive_metastore. O legacy_hive_catalog também representa uma forma de ignorar o ACL definido para as tabelas do hive_metastore, alguém com permissão de MODIFY é capaz de realizar UPDATE e DELETE das informações presentes no hive_metastore.

Substitua o trigger once por avaiableNow
Migration Guide: Structured Streaming - Spark 4.1.0 Documentation  

A partir do Spark 3.4, o Trigger.Once foi descontinuado, e os usuários são incentivados a migrar do Trigger.Once para o Trigger.AvailableNow.

DE



stream_writer = stream_writer.trigger(once=True)
PARA



stream_writer = stream_writer.trigger(availableNow=True)
Volumes



By Vale, Vinicius

2 min

29

Add a reaction
What are Unity Catalog volumes? | Databricks on AWS  

Volumes representações lógicas de caminhos em object storages no Unity Catalogs. São mounts gerenciados pelo UC ou ponteiros para um prefix no S3 em que é possível gerenciar os acessos dentro do Databricks. A ideia é ter governança também sobre dados não tabulares.

Um volume representa um caminho em um S3, esse caminho não deve conter uma tabela registrada no Unity Catalog. Isso quer dizer que volumes não substituem paths na hora de escrever ou ler uma tabela. Caso precise salvar uma tabela utilize o nome completo da tabela como referência ao invés do path no S3, mesmo no caso de uma tabela externa.

Para criar um volume é necessário que a Storage Credential tenha permissão atribuída no bucket e exista uma External Location para o bucket. Entre em contato com os admins do ambiente para confirmar se as permissões necessárias foram atribuídas antes de tentar criar um Volume.

Volumes serão utilizados para:

representar um path nos buckets raw (s3://serasaexperian-ecs-datalakehouse-prd-raw/) sendo criado como external no schema raw.

Screenshot 2025-03-27 at 13.23.53.png
representar um prefix no bucket sensitive (s3://serasaexperian-ecs-datalakehouse-prd-sensitive) sendo criado como external no schema sensitive

representar um prefix de um bucket crossaccount como no caso do Odin, por exemplo (s3://serasaexperian-odin-data-mesh-prod-renda-servidores-publicos/).

Um volume pode ser utilizado como um destino de arquivos para subir arquivos (excel, txt, csv, pdf, json, parquet) para complementar processamento, análises self service, como input para RAGs ou realizar delivery.

Bibliotecas (whl, jar) podem ser salvas em Volumes (Install libraries from a volume | Databricks on AWS  ). A partir do DBR 14.3 não é mais possível utilizar o DBFS para salvar libraries (Install libraries | Databricks on AWS  )

Volumes podem ser utilizados para salvar logs de clusters (Compute configuration reference | Databricks on AWS  )

Volumes serão utilizados para checkpoint locations (Structured Streaming checkpoints | Databricks on AWS  ) e schema locations (Configure schema inference and evolution in Auto Loader | Databricks on AWS  ). Esses volumes serão do tipo Managed e estarão no schema destino. Por exemplo, caso leia um arquivo da Raw para a bronze salve o checkpoint no Volume checkpoint no schema bronze.

Volumes que apontam para paths possuem a seguinte padrão de nomenclatura identificadodobucket_path_ate_o_conteudo, exemplo raw_ecs_antifraude_data_monitoring_report_data_monitoring_report é um volume apontando para s3://serasaexperian-ecs-datalakehouse-prd-raw/ecs/antifraude/data-monitoring-report/data_monitoring_report.

Os volumes apresentam o conteúdo do prefix do bucket, qualquer arquivo disponibilizado no S3 está disponível no Volume e qualquer arquivo gravado no Volume está disponível no S3. Porém para ler de um volume é necessário ter a permissão de READ VOLUME no Volume e para escrever é necessário WRITE VOLUME. Nos casos de sources (raw, sensitive e cross accounts) somente o service principal tem acesso e apenas para leitura. O time poderá criar volumes com permissão de escrita e leitura em sua sandbox e temp.

No caso de bucket raw, sensitive e de cross account são utilizados Volumes caso os arquivos não sejam uma delta table.

Você não pode utilizar Volumes como location para external tables. Se o path contém uma tabela delta crie uma tabela no Unity Catalog.

Não utilize DBFS para armazenas arquivos (Work with files on Databricks | Databricks on AWS  ). Utilize Volumes ou o Workspace files. (Recommendations for files in volumes and workspace files | Databricks on AWS  )

Para leitura e gravação em volumes podemos utilizar python, pyspark, sql, UI ou outras estratégias (What are volumes? | Databricks on AWS  ).

READ SQL



SELECT * from parquet.`/Volumes/premium_prd/raw/raw_ecs_antifraude_data_monitoring_report_data_monitoring_report/report_request`
READ PYSPARK



df = spark.read.format("parquet").load("/Volumes/premium_prd/raw/raw_ecs_antifraude_data_monitoring_report_data_monitoring_report/report_request")
WRITE PYSPARK

Gravando um arquivo no Volume



file_path = "/Volumes/premium_prd/bronze/report_request/csv/demo.csv"
(df.repartition(1)
 .write
 .format("csv")
 .mode("overwrite")
 .option("header", "true")
 .save(file_path)
)
Usando um Volume para checkpoint path



table_name = "report_request"
path_checkpoint_bronze = "/Volumes/premium_prd/bronze/checkpoints" + f"/{table_name}"
origin_to_bronze_writer = create_stream_writer(
    dataframe=df_transformed_origin,
    checkpoint=path_checkpoint_bronze,
    trigger_once=type_read_stream,
    name=named_bronze_stream_inicial,
    mergeSchema=True
)
if type_read_stream == True:
  origin_to_bronze_writer.toTable(table_name).awaitTermination()
else:
  origin_to_bronze_writer.toTable(table_name)
Não é possível utilizar foreachBatch  e .toTable no mesmo streaming (Writing stream in Databricks with toTable doesn't execute foreachBatch )

https://docs.databricks.com/aws/en/volumes/

Volumes são representações lógicas de caminhos em object storages no Unity Catalog. São mounts gerenciados pelo UC ou ainda ponteiros para um prefix no S3 em que é possível gerenciar os acessos dentro do Databricks. A ideia é ter governança também sobre dados não tabulares.

✅ Requisitos

DBR 14.3+

Cluster com Access Mode STANDARD ou DEDICATED

❗ Volumes não devem ser utilizados para criar external tables, não se deve passar um volume no LOCATION de uma tabela

# Não faça isso
CREATE OR REPLACE TABLE lno_prd.temp.tb_temp_external
LOCATION "/Volumes/lno_prd/bronze/report_request/"

❗ Não se deve criar um volume no local de uma tabela delta

# Não faça isso
CREATE EXTERNAL VOLUME IF NOT EXIST fraud_prd.silver.monitoring_report
LOCATION "s3://serasaexperian-ecs-datalakehouse-prd-silver/ecs/fraude/tb_data_monitoring_report/"
COMMENT "Esse path esta apontando para uma external table"

Se o path que você está trabalhando retornar sucesso em um Describe Detail esse é um path de uma tabela delta e você não deve criar um volume apontando para esse local

describe detail delta.`s3://bucket/path/'

Caso retorne [DELTA_MISSING_DELTA_TABLE] pode criar um volume nesse path.

Caso identifique que se trata de uma tabela delta, crie a versão managed no unity da mesma

CREATE OR REPLACE TABLE lno_prd.silver.tb_silver_table CLUSTER BY AUTO AS
SELECT * FROM delta.`s3://bucket/path/'

Managed Volume

Ideal para armazenar checkpoints de processos stream, schema de autloader, libs como jars e wheels ou arquivos que não contenham dados sensiveis que serão feitos upload via UI ou api.

Caso o volume seja apagado todos os arquivos são deletados juntos

External Volume

Ideal para arquivos que já estão disponíveis no S3

Buckets sources como raw, sensitive, sagemaker, logs ou qualquer external location read-only

Buckets destinations para processos externos como o sagemaker que lê “tabelas” parquet

stage_path = f'/Volumes/models_prd/stage/sagemaker_stage_lno_ofertas_recomendacao_v6/'

try:
  dbutils.fs.rm(stage_path, True)
except:
  pass

(
  df.write
    .option("maxRecordsPerFile", 100000)
    .mode('overwrite')
    .format('parquet')
    .save(stage_path) 
  )

Nomenclatura External Volume

Um external Volume deve respeitar a seguinte padrão de nomenclatura

SELECT
      regexp_replace(
        regexp_replace(
          regexp_replace(
            regexp_replace(
              regexp_replace(
                regexp_replace(
                  lower(:s3_path),
                  's3://',
                  ''
                ),
                '_',
                '-'
              ),
              '/',
              '-'
            ),
            'serasaexperian-ecs-datalakehouse-prd-',
            ''
          ),
          'serasaexperian-ecs-ml-prd-sagemaker-stage',
          'sagemaker-stage'
        ),
        '-$',
        ''
      ) AS volume_name

A lógica pega um caminho do S3 e aplica algumas regras para gerar um nome padronizado. Vamos usar este exemplo:

s3://serasaexperian-ecs-datalakehouse-prd-raw/ecs/fraude/premium/


Passos da transformação:

Remover o prefixo s3:// ou s3a://

Fica: 

serasaexperian-ecs-datalakehouse-prd-raw/ecs/fraude/premium/

Transformar tudo em letras minúsculas

Para manter padrão.

Trocar todos os _ por -

Ex.: ecs_fraude → ecs-fraude.

Trocar todas as barras / por -

Ex.: ecs/fraude/premium → ecs-fraude-premium.

Remover prefixos desnecessários do bucket

Como:

serasaexperian-ecs-datalakehouse-prd-

ou serasaexperian-ecs-ml-prd-sagemaker-stage (que vira sagemaker-stage).

Remover hífen no final, se sobrar

Para não terminar com -.

Resultado final do exemplo:

raw-ecs-fraude-premium



❗ Não é possível criar dois Volumes no mesmo path ou em seus subpaths. Por isso, sempre prefira criar o Volume no caminho mais granular possível.

Exemplo:
Se você criar um Volume no seguinte caminho:

s3://serasaexperian-ecs-datalakehouse-prd-raw/ecs/fraude/

não será permitido criar outro Volume em nenhum catálogo que utilize subpaths, como:

s3://serasaexperian-ecs-datalakehouse-prd-raw/ecs/fraude/premium/
s3://serasaexperian-ecs-datalakehouse-prd-raw/ecs/fraude/lno/

Criar Volume

Para criar um volume é necessário que a Storage Credential tenha permissão atribuída no bucket e exista uma External Location para o bucket. Entre em contato com os admins do ambiente para confirmar se as permissões necessárias foram atribuídas antes de tentar criar um Volume.

Caso você esteja nos grupos de Engenharia, Analytics, Data Science tem permissão de criar managed e external volumes nos schemas sandbox ou temp. Essa ação pode ser feita via UI, SQL Editor ou notebook. Os times de produto têm permissão de criar Volumes Managed nesses schemas. Nos schemas produtivos é necessário utilizar o job create_volume - Databricks ou colocar o seguinte trecho no código que irá subir em produção:

CREATE VOLUME IF NOT EXIST 

O job create_volume tem os parametros:

catalog: catálogo onde será criado o Volume

schema: schema onde será criado o Volume

s3_path: obrigatório caso seja um volume external

volume_name: obrigatório caso seja um volume managed

Cenário Raw-bronze-Silver-delivery

Nesse cenário há os seguintes paths

raw_path = "s3://serasaexperian-ecs-datalakehouse-prd-raw/ecs/partnerportal/commissioning-service-new/public/partner/"
bronze_path = "s3://serasaexperian-ecs-datalakehouse-prd-bronze/ecs/partnerportal/commissioning-service/partner/"
silver_path = "s3://serasaexperian-ecs-datalakehouse-prd-silver/ecs/partnerportal/commissioning-service/partner/"
quality_checkpoint_path = "s3://serasaexperian-ecs-datalakehouse-prd-checkpoints/ecs/partnerportal/commissioning-service/partner/quality-bronze-to-silver/"
delivery_path = "s3://serasaexperian-ecs-ml-prd-sagemaker-stage/data_capture/lno-ofertas-recomendacao/lno-ofertas-recomendacao/AllTraffic/"

O primeiro path trata-se de um source com arquivos parquet ou json, por esse motivo deve-se criar um volume

O segundo path trata-se de uma tabela delta, mesmo que não registrada no hive, por isso deve-se criar uma tabela managed no schema bronze com o conteudo desse path e criar um job para alimentar essa nova tabela

O terceiro path trata-se de uma tabela delta, a silver agora deve deixar de ler como source o path bronze e ler a tabela no unity e ela tambem se tranformar em uma tabela do unity no schema silver

O quarto path trata-se de um path para checkpoints, recomenda-se não utilizar o mesmo path do hive e sim utilizar o volume checkpoints que existe em todos os schemas silver

O quinto path trata-se de um destination, um processo que grava arquivos para processos externos que não são capazes de ler tabelas delta, por isso deve-se criar um volume. 

❗ No caso de gravação em SFTP não é utilizado Volumes
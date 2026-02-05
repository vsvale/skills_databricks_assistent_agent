Design Patterns para Databricks — Guia de Arquitetura e Desenvolvimento



By Strumendo, Bruno

7 min

23

Add a reaction
Design Patterns para Databricks — Guia de Arquitetura e Desenvolvimento (V5)

Objetivo
Este documento estabelece os padrões de design, desenvolvimento e arquitetura para equipes que utilizam Databricks nas camadas RAW, Bronze e Silver, garantindo consistência, qualidade, rastreabilidade e eficiência.

Público-alvo: Engenheiros de Dados (novos e experientes)

https://example.com/guia-administracao-plataforma-dados

Princípios Fundamentais
Simplicidade: soluções fáceis de entender e manter, evitando complexidade desnecessária.

Reusabilidade: patterns e código reutilizáveis para acelerar desenvolvimento e reduzir risco.

Rastreabilidade: campos de controle em todas as camadas para auditoria e debugging (compliance LGPD).

Governança: segurança e qualidade em primeiro lugar, com controle sobre dados pessoais.

1. ARQUITETURA DE REFERÊNCIA
1.1 Componentes da Arquitetura
Componente

Tecnologia

Responsabilidade

Compute

Databricks Clusters

Processamento distribuído

Storage

AWS S3

Armazenamento de dados

Catalog

Unity Catalog

Governança e descoberta

Orchestration

Databricks Workflows

Orquestração de pipelines

Monitoring

Datadog + CloudWatch

Observabilidade

Security

IAM + Secrets Manager + Unity Catalog

Controle de acesso

1.2 Camadas de Dados (Medallion Architecture)
Arquitetura em 4 camadas, onde cada camada é fonte da próxima, garantindo cadeia de rastreabilidade.



┌─────────────────────────────────────────────────────────────────┐
│                         FONTES DE DADOS                         │
│         MySQL (JOBS, NEO, Bezos, Zanatto) + APIs + Arquivos     │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  RAW (AWS S3)                                                   │
│  • Landing zone - primeiro ponto de contato                     │
│  • Dado bruto sem transformação (AS IS da fonte)                │
│  • Formatos originais (JSON, CSV, Parquet)                      │
│  • PII criptografado                                            │
│  • Serve como FONTE para a Bronze                               │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  BRONZE (Unity Catalog - Delta Lake)                            │
│  • Cópia fiel da RAW em formato Delta                           │
│  • Campos de controle obrigatórios adicionados                  │
│  • PII criptografado                                            │
│  • Serve como FONTE para a Silver                               │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  SILVER (Unity Catalog - Delta Lake)                            │
│  • Dados limpos, transformados e enriquecidos                   │
│  • Business rules aplicadas                                     │
│  • Deduplicação e tratamento de nulos                           │
│  • Timezone padronizado (UTC-3)                                 │
│  • PII criptografado                                            │
│  • Serve como FONTE para a Gold                                 │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  GOLD (Unity Catalog - Delta Lake) - Fora do escopo deste doc   │
│  • Dados agregados e prontos para consumo                       │
│  • Serve como FONTE para BI, Analytics, ML                      │
└─────────────────────────────────────────────────────────────────┘
1.3 Conceito Detalhado de Cada Camada
Entender o papel de cada camada é fundamental para implementar corretamente os campos de controle e a rastreabilidade.

Camada

Localização

Papel

Fonte de Dados

Destino

RAW

AWS S3 (bucket)

Landing zone - recebe dados brutos das fontes externas

MySQL, APIs, Arquivos

Bronze

BRONZE

Unity Catalog

Conversão para Delta mantendo fidelidade à RAW

RAW (S3)

Silver

SILVER

Unity Catalog

Limpeza, transformação e aplicação de regras de negócio

Bronze

Gold

Princípio da Cadeia de Rastreabilidade: cada camada sempre sabe de onde veio por meio de source_processing.

2. ESTRUTURA ORGANIZACIONAL E UNITY CATALOG
2.1 Conceitos Fundamentais: Domínio vs Produto
Dois níveis hierárquicos organizam times e dados: Domínio (gestão) e Produto (técnico no UC). O Domínio não existe como objeto no Unity Catalog; o Produto mapeia para Catálogos, tags e buckets.

2.2 Mapeamento Completo: Domínios e Produtos
Exemplos de mapeamento entre domínios, produtos e artefatos técnicos (catálogos e buckets) para navegação e solicitação de acessos.

2.3 Como Funciona o Acesso ao Databricks
Acesso inicial: todos os catálogos e schemas públicos dos produtos.

Tipo de Acesso

O que inclui

Como obter

Catálogos públicos

Schemas bronze, silver, gold de todos os produtos

Automático ao receber acesso ao Databricks

Dados compartilhados

Tabelas marcadas como públicas

Automático

Acessos específicos via IDC: sandbox, temp, control e PII não mascarado exigem abertura de chamado e aprovação.

2.4 Unity Catalog: Hierarquia Técnica


Metastore (nível da conta)
└── Catalog (= Produto)
    └── Schema (camada de dados)
        └── Table (objetos de dados)
Governança centralizada: permissões, lineage e auditoria em um único lugar.

Compartilhamento seguro: Delta Sharing entre organizações.

Descoberta de dados: catálogo unificado e pesquisável.

Lineage automático: rastreamento de origem e dependências.

2.5 Schemas Disponíveis (por Catálogo)
Schema

Propósito

Uso

raw

Dados brutos

Dados em formato original antes de qualquer processamento

bronze

Dados ingeridos

Delta, PII criptografado; primeira camada do pipeline

silver

Dados limpos e enriquecidos

Refinados e processados, prontos para análise

2.6 Hierarquia de Armazenamento S3 — Padrões de Buckets
Padrão legado: serasaexperian-ecs-datalakehouse-{ambiente}-{produto}

Novo padrão (recomendado para novos processos): ecs-{time}-{aplicacao}-{ambiente} e ecs-dataops-{aplicacao}-{ambiente}

Tipo

Padrão

Status

Legado

serasaexperian-ecs-datalakehouse-{ambiente}-{produto}

Manter para buckets existentes

Novo

ecs-{time}-{aplicacao}-{ambiente}

Usar para novos processos

3. CAMPOS DE CONTROLE OBRIGATÓRIOS
3.1 Lista de Campos de Controle
Campos padronizados, obrigatórios e posicionados ao final das tabelas em todas as camadas.

Campo

Tipo

Descrição

Exemplo

dt_ingestion

TIMESTAMP

Quando o dado entrou na camada atual

2024-01-15 10:30:00

dt_processing

TIMESTAMP

Momento do processamento/transformação

2024-01-15 11:00:00

source_processing

STRING

Camada de origem (anterior)

RAW, BRONZE, SILVER

3.2 Campos por Camada
BRONZE (origem RAW): dt_ingestion, source_processing='RAW', source_table, nm_file_origin.

SILVER (origem BRONZE): herda dt_ingestion e nm_file_origin; adiciona dt_processing; atualiza source_processing='BRONZE' e source_table.

3.3 Regra Crítica: NÃO particionar por campos de controle
Evite desbalanceamento e degradação de performance.

Particione por campos de negócio (ex.: dt_event, cd_region).

3.4 Particionamento Automático via Unity Catalog
Comando

Status

Motivo

CLUSTER BY

Usar

Gerenciado por Policies

PARTITIONED BY

Não usar

Substituído por CLUSTER BY



-- Correto: CLUSTER BY com campo de negócio
CREATE TABLE ecred_prd.silver.tb_jobs_customers (...)
USING DELTA
CLUSTER BY (dt_event);
-- Errado: CLUSTER BY com campo de controle
-- CLUSTER BY (dt_ingestion);
-- Errado: PARTITIONED BY
-- PARTITIONED BY (date(dt_event));
3.5 Exemplos Práticos: CREATE TABLE


-- Bronze (origem RAW)
CREATE TABLE IF NOT EXISTS ecred_prd.bronze.tb_jobs_customers (
  id_customer STRING NOT NULL,
  nm_customer STRING,
  ds_email STRING,
  dt_birth DATE,
  dt_registration DATE,
  vl_income DECIMAL(15,2),
  fl_active BOOLEAN,
  dt_ingestion TIMESTAMP NOT NULL,
  source_processing STRING NOT NULL,
  source_table STRING NOT NULL,
  nm_file_origin STRING NOT NULL
) USING DELTA
CLUSTER BY (dt_registration)
TBLPROPERTIES(
  'delta.autoOptimize.optimizeWrite'='true',
  'delta.autoOptimize.autoCompact'='true'
);
-- Silver (origem BRONZE)
CREATE TABLE IF NOT EXISTS ecred_prd.silver.tb_jobs_customers (
  id_customer STRING NOT NULL,
  nm_customer STRING NOT NULL,
  ds_email STRING,
  dt_birth DATE,
  dt_registration DATE,
  vl_income DECIMAL(15,2),
  fl_active BOOLEAN DEFAULT true,
  dt_ingestion TIMESTAMP NOT NULL,
  dt_processing TIMESTAMP NOT NULL,
  source_processing STRING NOT NULL,
  source_table STRING NOT NULL,
  nm_file_origin STRING NOT NULL
) USING DELTA
CLUSTER BY (dt_registration)
TBLPROPERTIES(
  'delta.autoOptimize.optimizeWrite'='true',
  'delta.autoOptimize.autoCompact'='true'
);
3.6–3.7 Código de Movimentação e Consumo


# RAW → BRONZE (batch)
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, current_timestamp, input_file_name
def raw_to_bronze(spark: SparkSession, source_path: str, target_table: str, source_table_name: str):
    df = spark.read.json(source_path)
    df_bronze = (df
      .withColumn("dt_ingestion", current_timestamp())
      .withColumn("source_processing", lit("RAW"))
      .withColumn("source_table", lit(source_table_name))
      .withColumn("nm_file_origin", input_file_name())
    )
    (df_bronze.write
      .format("delta").mode("append")
      .option("mergeSchema","true")
      .saveAsTable(target_table))
    return df_bronze.count()
# BRONZE → SILVER (batch)
from pyspark.sql.functions import col
def bronze_to_silver(spark: SparkSession, source_table: str, target_table: str):
    df = spark.table(source_table)
    bronze_table_name = source_table.split(".")[-1]
    df_silver = (df
      .dropDuplicates(["id_customer"]) 
      .withColumn("dt_processing", current_timestamp())
      .withColumn("source_processing", lit("BRONZE"))
      .withColumn("source_table", lit(bronze_table_name))
    )
    (df_silver.write
      .format("delta").mode("append")
      .option("mergeSchema","true")
      .saveAsTable(target_table))
    return df_silver.count()
# Consultas de auditoria
spark.sql("""
  SELECT id_customer, dt_ingestion, dt_processing, source_processing, source_table, nm_file_origin
  FROM ecred_prd.silver.tb_jobs_customers
  WHERE id_customer = '12345'
""")
3.8 Ordem de Campos (Padrão)
Ordem

Tipo de Campo

Prefixo

Exemplo

Pode particionar?

1

Identificadores naturais

id_

id_customer

Não

2

Datas de negócio

dt_

dt_event, dt_registration

Sim

3.9 Regras de Ouro (Resumo)


┌─────────────────────────────────────────────────────────────────┐
│ REGRAS DE OURO                                                   │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Adicionar campos de controle no final                         │
│ ✅ Manter dt_ingestion e nm_file_origin da origem                │
│ ✅ Atualizar source_processing e source_table                    │
│ ✅ Usar CLUSTER BY com campos de negócio                         │
│ ❌ Não usar campos de controle para particionamento              │
│ ❌ Não executar OPTIMIZE/ZORDER manual                           │
│ ❌ Não usar PARTITIONED BY                                       │
└─────────────────────────────────────────────────────────────────┘
4. MOVIMENTAÇÃO ENTRE CAMADAS — CLASSES REUTILIZÁVEIS
4.1 RAW → BRONZE (Batch)


from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, current_timestamp, input_file_name
class RawToBronzeProcessor:
    def __init__(self, spark: SparkSession):
        self.spark = spark
    def process(self, source_path: str, target_table: str, source_table_name: str, file_format: str = "json"):
        if file_format == "json":
            df = self.spark.read.json(source_path)
        elif file_format == "csv":
            df = self.spark.read.option("header","true").csv(source_path)
        else:
            df = self.spark.read.parquet(source_path)
        df_bronze = (df
          .withColumn("dt_ingestion", current_timestamp())
          .withColumn("source_processing", lit("RAW"))
          .withColumn("source_table", lit(source_table_name))
          .withColumn("nm_file_origin", input_file_name())
        )
        (df_bronze.write.format("delta").mode("append").option("mergeSchema","true").saveAsTable(target_table))
        return df_bronze.count()
4.2 BRONZE → SILVER (Batch)


from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import lit, current_timestamp, col, trim, upper, coalesce
from typing import List, Callable
class BronzeToSilverProcessor:
    def __init__(self, spark: SparkSession):
        self.spark = spark
    def apply_transformations(self, df: DataFrame) -> DataFrame:
        for f in df.schema.fields:
            if str(f.dataType) == 'StringType' and f.name not in ("nm_file_origin",):
                df = df.withColumn(f.name, trim(col(f.name)))
        return df
    def process(self, source_table: str, target_table: str, required_columns: List[str] = None, custom_transformations: Callable[[DataFrame], DataFrame] = None):
        df = self.spark.table(source_table)
        bronze_table_name = source_table.split(".")[-1]
        if required_columns:
            for c in required_columns:
                df = df.filter(col(c).isNotNull())
        df = self.apply_transformations(df)
        if custom_transformations:
            df = custom_transformations(df)
        df_silver = (df
          .withColumn("dt_processing", current_timestamp())
          .withColumn("source_processing", lit("BRONZE"))
          .withColumn("source_table", lit(bronze_table_name))
        )
        (df_silver.write.format("delta").mode("append").option("mergeSchema","true").saveAsTable(target_table))
        return df_silver.count()
4.3 Ingestão Contínua (Structured Streaming)


from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, current_timestamp, col
class StreamingRawToBronze:
    def __init__(self, spark: SparkSession):
        self.spark = spark
    def start_stream(self, source_path: str, target_table: str, source_table_name: str, checkpoint_path: str, file_format: str = "json"):
        stream_df = (self.spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", file_format)
            .option("cloudFiles.inferColumnTypes", "true")
            .load(source_path))
        stream_df = (stream_df
          .withColumn("dt_ingestion", current_timestamp())
          .withColumn("source_processing", lit("RAW"))
          .withColumn("source_table", lit(source_table_name))
          .withColumn("nm_file_origin", col("_metadata.file_path"))
        )
        return (stream_df.writeStream
          .format("delta")
          .outputMode("append")
          .option("checkpointLocation", checkpoint_path)
          .option("mergeSchema","true")
          .trigger(availableNow=True)
          .toTable(target_table))
5. NOMENCLATURA DE TABELAS, JOBS E TAGS
5.1 Nomenclatura de Tabelas
Padrão: tb_{schema_origem}_{nome_tabela_origem}



-- Exemplo de endereçamento completo
-- {catalogo}.{schema}.{tabela}
SELECT * FROM ecred_prd.bronze.tb_jobs_customers;
5.2 Nomenclatura de Jobs e Tag CreatedBy
Formato de jobs: <operação>_<origem>_<destino>_<nome_do_job>

etl_raw_bronze_tb_jobs_customers

etl_bronze_silver_tb_jobs_customers

Todo job deve conter a tag CreatedBy com o nome do Produto/Time para rastreamento de custos e organização.

6. TEMPLATE DE CONFIGURAÇÃO


job:
  jobName: "etl_bronze_silver_tb_jobs_customers"
  description: "Processa dados de clientes de Bronze para Silver"
  owner: "data-engineering-team"
  slaHours: 2
  tags:
    CreatedBy: "ECRED"
unityCatalog:
  catalog: "ecred_prd"
  sourceSchema: "bronze"
  targetSchema: "silver"
spark:
  appName: "CustomerProcessing"
  configs:
    spark.sql.adaptive.enabled: "true"
    spark.sql.adaptive.coalescePartitions.enabled: "true"
    spark.sql.shuffle.partitions: "200"
    spark.databricks.delta.autoCompact.enabled: "true"
data:
  source:
    table: "ecred_prd.bronze.tb_jobs_customers"
    format: "delta"
  target:
    table: "ecred_prd.silver.tb_jobs_customers"
    format: "delta"
    clusterBy: ["dt_registration"]  # Campo de negócio
7. GOVERNANÇA E CRIPTOGRAFIA
7.1 Uso de Criptografia (PII)
Para trabalhar com PII criptografado, é necessário pertencer ao grupo lake_cryptography e utilizar a biblioteca de criptografia da plataforma.



from lake_crypto import encrypt, decrypt
encrypted_value = encrypt(sensitive_data)
decrypted_value = decrypt(encrypted_value)  # Apenas para processamento; não persistir em claro
7.2 Boas Práticas de Unity Catalog
Use nomes completos de tabela: catalogo.schema.tabela

Verifique permissões antes de compartilhar queries.

Respeite lineage e não crie atalhos que o quebrem.

Use views para expor regras de negócio.



-- Nome completo
SELECT * FROM ecred_prd.silver.tb_jobs_customers;
-- View de negócio
CREATE VIEW ecred_prd.silver.vw_active_customers AS
SELECT * FROM ecred_prd.silver.tb_jobs_customers WHERE fl_active = true;
8. BOAS PRÁTICAS DE GIT E GITLAB
8.1 Fluxo e Estrutura de Branches
Branch

Propósito

Merge para

main

Produção

-

develop

Integração de features

main

8.2 Nomenclatura de Branches (Jira)
Formato: <tipo>/<ID-JIRA>-<descricao-curta>



feature/DATA-123-ingestao-customers-bronze
bugfix/ECRED-567-corrige-deduplicacao
hotfix/DATA-345-fix-producao-timeout
release/v1.2.0
8.3 Conventional Commits
Tipo

Quando usar

Exemplo

feat

Nova funcionalidade

feat(DATA-123): add bronze to silver processor

fix

Correção de bug

fix(DATA-123): resolve null pointer in validation

8.4 Comandos Git Úteis


git checkout -b feature/DATA-123-ingestao-customers-bronze
git add .
git commit -m "feat(DATA-123): add control fields to bronze table"
git push origin feature/DATA-123-ingestao-customers-bronze
CONCLUSÃO
A aplicação consistente destes padrões em Databricks para RAW, Bronze e Silver assegura rastreabilidade ponta a ponta, qualidade, governança via Unity Catalog e manutenibilidade elevada.
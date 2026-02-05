Taguear jobs no Databricks é uma prática essencial para a organização e gerenciamento eficiente dos processos de dados. As tags são atributos que incluem chaves e valores opcionais, permitindo categorizar e organizar objetos de forma segura no Unity Catalog.

Alguns dos principais benefícios:

Rastreamento de Jobs: As tags facilitam o rastreamento de jobs, permitindo que você identifique rapidamente a unidade de negócio, o sistema de origem, e outras informações relevantes associadas a cada job.

Filtros no Datadog: Utilizar tags permite integrar e filtrar jobs nos dashboards do Datadog, melhorando a monitorização e a análise de desempenho dos jobs.

Busca Facilitada: As tags simplificam a busca e a descoberta de jobs na tela de pesquisa do Databricks, tornando mais fácil localizar jobs específicos com base em critérios como departamento, prioridade, ou tipo de processo.

Organização e Categorização: Tags ajudam a organizar e categorizar objetos no Unity Catalog, facilitando a gestão e a navegação pelos dados.

Propagação para Clusters: As tags também se propagam para os clusters de jobs criados durante a execução, permitindo o uso contínuo das tags no monitoramento dos clusters.

Segurança e Conformidade: Como as tags não são projetadas para armazenar informações sensíveis, como dados pessoais ou senhas, elas garantem que apenas valores não sensíveis sejam utilizados, mantendo a conformidade com as melhores práticas de segurança.

Tags Obrigatórias
Tags obrigatórias são aqueles que sem elas o job não sobe via esteira. Essas tags respeitam os padrões do time de FinOps da Experian (finopsbr@br.experian.com)

BU: Unidade de Negócio responsável pelo job. Exemplo: ECS,TEX, PV

BusinessServices: Produto ou time ao qual pertence o job. Exemplo: PREMIUM

Environment: Ambiente de execução. Exemplo: PRD

CreatedBy: Time responsável por monitorar o job. Exemplo: DATAOPS, CRM, PERSONALIZATION

JobType: Tipo de job, podendo ser ETL, SELF_SERVICE  , ALL_PURPOSE, DLT, WAREHOUSE  ou MAINTENANCE_JOB (optimize/vacuum)

Data_Category: Data_Category: Importância dos resultados entregues pelo job. Valores possíveis: ALTA,MEDIA,BAIXA,BAIXISSIMA

datadog: Indica se o job deve aparecer nos dashboards do Datadog. Valores possíveis: TRUE, FALSE

Tags Opcionais
RunName: Nome do job. É automaticamente atribuída pelo Databricks, porém nos clusters All Purpose, DLT e Warehouses e recomendado colocá-la

UserEmail: Caso o JobType seja do tipo SELF_SERVICE  e a policie de High Performance seja selecionada, será necessário preencher essa CustomTag via UI

Exemplo em job.json


{
  "name": "[DMS] etl_box_operation_new",
  "email_notifications": {
    "on_failure": [
      "ecs-datalake-monitori-aaaac4ar2enkkqglmobghhlfxe@experian.org.slack.com",
      "thomaz.neto@br.experian.com"
    ],
    "no_alert_for_skipped_runs": false
  },
  "webhook_notifications": {},
  "timeout_seconds": 0,
  "schedule": {
    "quartz_cron_expression": "0 0 8 * * ?",
    "timezone_id": "America/Sao_Paulo",
    "pause_status": "UNPAUSED"
  },
  "max_concurrent_runs": 1,
  "tasks": [
      ...
  ],
  "tags": {
    "BU": "ECS",
    "datadog": "TRUE",
    "BusinessServices": "BOX",
    "Environment": "PRD",
    "CreatedBy": "ANALYTICS",
    "JobType": "ETL",
    "Data_Category" : "BAIXA"
  },
  "run_as": {
    "user_name": "ecs_ci_cd_datalake@br.experian.com"
  }
}
Valores Exemplos
Os valores devem estar em maiusculo e use underline no lugar de espaço

CreatedBy



RECUPERACAO_DIVIDAS
CREDITO_PROTECAO
MARTECH
CRM
DATASCIENCE
LNO
EVOLUCAO
PREMIUM
AQUISICAO_MARKETING
ESTRATEGIA_PERFORMANCE_COBRANCA
AUTENTICACAO_FRAUDES
PERSONALIZATION
datadog



TRUE
FALSE
JobType



SELF_SERVICE
ETL
MAINTENANCE_JOB
ALL_PURPOSE
WAREHOUSE
DLT
BU



ECS
CORP
DATABRICKS
BusinessServices



CRM
AUTH
ANALYTICS
DATAHUB
COLLECTION
LNO
DATA
DATASCIENCE
ECRED
PREMIUM
CHATBOT
ECS
LNOP
EVOLUCAO
AQUISICAO
CONSUMER_CARE
MINHAS_CONTAS
DIGITAL
S3
BOX
SCIENCE
BIZDEV
ECS_FINANCE
MARKETING
EWALLET
SCORE
FRAUD
FINANCAS
PAGUEVELOZ
MKT
FLEXPAG
MAINFRAME
PLATAFORMA
Environment



PRD
Data_Category



ALTA
MEDIA
BAIXA
BAIXISSIMA
 
Contexto

Atualmente, nossa estrutura de código possui 1.689 repositórios, seguindo um modelo 1:1 (um repositório por job). Esse formato trouxe desafios relacionados à governança e rastreabilidade, especialmente após a solicitação da equipe de governança da Experian para associar um Gear ID a cada repositório.

Para atender a essa necessidade e melhorar a organização, criamos o conceito de Repositórios Unificados por Produto.

O que é um Repositório Unificado?

Um Repositório Unificado é um repositório que agrupa múltiplos jobs relacionados a um mesmo produto. Ele contém:

Jobs de Engenharia de Dados

Jobs de Produto

Jobs de Analytics

Jobs de Data Science

Cada repositório unificado possui um arquivo gear.properties, que associa o Gear ID ao produto correspondente.

⚠️ Atenção Em futura release da esteira de CI/CD será obrigatório o preenchimento do gearid no arquivo gear.properties

Estrutura do Repositório Unificado

/dataops-core-produto
    ├── gear.properties
    ├── .gitlab-ci.yml
    ├── .gitignore
    ├── .dockerignore
    ├── cicd/
    │   └── custom-pipeline.yaml
    ├── nome_do_job_1/
    │   └── src/
    │   │   └── databricks/
    │   │   │   └── jobs/
    │   │   │   │   └── job.json
    │   │   │   └── workspace/
    │   │   │   │   └── notebook_etl.py
    └── nome_do_job_2/
    │   └── src/
    │   │   └── databricks/
    │   │   │   └── jobs/
    │   │   │   │   └── job.json
    │   │   │   └── workspace/
    │   │   │   │   └── notebook_etl_2.py

Nomenclatura dos folders dos jobs

Na raiz do repositório unificado, devem ser criadas pastas específicas para cada job, e não com o nome do repositório original. Utilize uma versão simplificada e padronizada do nome do job para nomear essas pastas.

Boas práticas para nomear pastas de jobs:

Evite números, caracteres especiais ou espaços.

Utilize underscore (_) para separar palavras.

Mantenha o nome curto e descritivo, facilitando a identificação do job.

Caso o nome original contenha caracteres especiais, números ou horários, simplifique ao máximo.

Exemplo: Nome original do job:

[BIZDEV] PPT Automatizado (11h30)


Nome da pasta no repositório:

BIZDEV_PPT_Automatizado_11h30

Migrando para o Repositório Unificado

Essas ações devem ser realizadas diretamente pela interface do Databricks (UI).
Após criar a pasta do job no repositório unificado, recomendamos mover a pasta src do repositório original para a pasta correspondente ao job. Para isso:

Clone o repositório original em um diretório temporário no Databricks usando a opção Add Repo.

Localize a pasta src dentro do repositório original.

Mova a pasta src para a pasta do job no repositório unificado utilizando a funcionalidade de Move na UI.

Confirme a estrutura final para garantir que o código esteja corretamente organizado.

Pipeline de CI/CD

A pipeline de CI/CD foi configurada para permitir a seleção dos jobs que devem ter suas configurações atualizadas.
Caso a etapa trigger_dynamic_deploy_prd falhe, será necessário escolher manualmente um ou mais jobs para atualização.


Produto por Repositório Unificado

A separação dos repositórios é feita por produto, e não por domínio. Por isso, é muito provável que você encontre um repositório para cada catálogo no Unity Catalog.

Repo

Produto

dataops / core / dataops-core-admin-prd · GitLab

PLATAFORMA

dataops / core / dataops-core-collection-prd · GitLab

COLLECTION

dataops / core / dataops-core-crm · GitLab

CRM

dataops / core / dataops-core-consumercare-prd · GitLab

CONSUMERCARE

dataops / core / dataops-core-ecred · GitLab

ECRED

dataops / core / dataops-core-ewallet-prd · GitLab

EWALLET

dataops / core / dataops-core-flexpag-prd · GitLab

FLEXPAG

dataops / core / dataops-core-fraud-prd · GitLab

FRAUD

dataops / core / dataops-core-lno-prd · GitLab

LNO

dataops / core / dataops-core-mcp-prd · GitLab

MCP

dataops / core / dataops-core-mkt · GitLab

MKT

dataops / core / dataops-core-odin-prd · GitLab

ODIN

dataops / core / dataops-core-premium-prd · GitLab

PREMIUM

dataops / core / dataops-core-score-prd · GitLab

SCORE

dataops / core / dataops-core-shared-prd · GitLab

SHARED

dataops / core / dataops-core-tex-prd · GitLab

TEX

dataops / core / dataops-core-auth · GitLab

AUTH

⚠️ Atenção Alguns dos repositórios foram criados com o padrão  dataops-core-produto-prd. Esse padrão foi descontinuado sendo o recomendado dataops-core-produto

Pipeline

Criação de Repositório Unificado do Produto 

Caso seu produto ainda não tenha um repositório unificado basta cria um no Dalvito 3.0.
Acesse o Dalvito 3.0.

Vá em:
Criar → Criar repositório de aplicações. Ou acesse: (https://dalvito.ecsbr.net/create/templates/default/create-repo-application)

Preencha os campos conforme abaixo:

Grupo: dataops

Subgrupo: core

Tipo de linguagem: python

Deploy: databricks

Projeto: Nome do produto (ex.: produto-x)
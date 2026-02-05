A estratégia de migração varia conforme as caracteristicas da tabela.

Copy Only
Tabela não possui job associado

Tabela não é atualizada a mais de 60 dias

Job está desativado

Job está pausado e não executa a mais de 60 dias

Tabela foi restaurada e não é possível identificar o notebook que contém a lógica de criação

É realizado o CTAS da tabela ou path do Hive para o Unity. Nenhum código, arquivo, repositório ou job são  alterados.

Tabela Particionada



CREATE OR REPLACE TABLE premium_prd.bronze.tb_freemium_leaks CLUSTER BY (dt_load_bronze)
AS SELECT dt_load_bronze, * except(dt_load_bronze) FROM delta.`s3://serasaexperian-ecs-datalakehouse-prd-bronze/ecs/antifraude/freemium_darkweb/leaks/`;
Tabela não Particionada



CREATE OR REPLACE TABLE premium_prd.bronze.tb_base_subscription_ecs_antifraude_subscription_free CLUSTER BY AUTO
AS SELECT * FROM  hive_metastore.db_premium_bronze.tb_base_subscription_ecs_antifraude_subscription_free
 

Workspace level
Tabela está associada a um job que roda a nível de workspace de um usuário que não é um user sistemico (ecs_ci_cd_datalake@br.experian.com, henrique.machado@br.experian.com e ecs-databricks@br.experian.com.)

Nesse caso o dono do notebook responsável pode transferir os notebooks, configuração de parametros e de job para um Repo para que a tabela seja migrada em estratégia de Repos. Ou o mesmo pode fazer ele mesmo as alterações necessárias no notebook e job em seu Workspace pessoal seguindo as orientações desse guia e tendo apoio do time de migração.

Repos
Tabelas com jobs associadados cujo os códigos estão versionados em Repositórios

Caso o time ou produto migrado não possua time de engenheiros o time de migração é responsável por fazer todas as alterações necessárias.
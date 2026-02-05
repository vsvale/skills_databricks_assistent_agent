Ao criar uma tabela no Unity Catalog Databricks recomenda a utilização de tabelas gerenciadas, por esse motivo elas são o modo default (Databricks tables | Databricks on AWS  ). Managed tables são tabelas delta cujo dados são administrados juntamente com o metadados. Caso apague uma tabela gerenciada tanto os dados quanto os metadados são deletados, desde que vença a janela de restauração (UNDROP | Databricks on AWS  ). Tabelas managed são gerenciadas pela Databricks que roda em segundo plano o processo predictive optimization (Announcing General Availability of Predictive Optimization | Databricks Blog  ) que realiza OPTIMIZE, ANALYZE e VACUUM em tabelas gerenciadas, isso torna desnecessário incluir esse tipo de ação em notebooks ou criação de jobs apartados para esse fim. O processo reduz a complexidade de em gerenciar tabelas, reduz custos de storage e aumenta a performance de queryes (Cost-based optimizer | Databricks on AWS  ).

Dê preferência em criar tabelas gerenciadas a external table no Unity Catalog

Para criar uma tabela gerenciada basta não definir a propriedadeLOCATION ou incluir a option pathna hora de criar a tabela.

DE



CREATE TABLE IF NOT EXISTS demo_prd.sandbox.external_table_name
LOCATION 's3://external-location/table_path'
PARA



CREATE TABLE IF NOT EXISTS demo_prd.sandbox.external_table_name
Nesse exemplo foi alterado:

Removido a location para que a tabela seja criada como managed table

DE



(df.write.format('delta')
 .mode("overwrite")
 .option('path','/dbfs/tmp/unmanageTable')
 .saveAsTable('demo_prd.sandbox.player_detail_unanaged'))
PARA



(df.write.mode("overwrite").saveAsTable('demo_prd.sandbox.player_detail_unanaged')
Nesse exemplo foram alterados:

removido .format('delta'), pois o formato padrão para salvar é em delta (What is Delta Lake in Databricks? | Databricks on AWS  )

removido .option('path','/dbfs/tmp/unmanageTable') para que a tabela seja criada como managed table

Qualquer tabela criada via DEEP CLONE ou CREATE TABLE AS SELECT (CTAS) é criada como uma managed table. Todas as tabelas armazenadas no DBFS root serão migradas via CTAS.

Para ser capaz de criar uma managed table é necessário ter as seguintes permissões USE CATALOG, USE SCHEMA e CREATE TABLE (Unity Catalog managed tables in Databricks for Delta Lake and Apache Iceberg | Databricks on AWS  )

É necessário ter a permissão MANAGE ou ser o OWNER da tabela para ser capaz de dropar uma tabela (Unity Catalog managed tables in Databricks for Delta Lake and Apache Iceberg | Databricks on AWS )

Para evitar corromper uma tabela gerenciada a Databricks recomenda não tentar utilizar ferramentas externas para manipular os arquivos de uma managed table (Unity Catalog managed tables in Databricks for Delta Lake and Apache Iceberg | Databricks on AWS  ). Caso alguém necessite acessar os dados de uma tabela no Databricks de forma externa, peça que essa pessoa entre em contato com o time de governança, arquitetura ou evolução. Os cenários de acessos externos podem ser atendidos utilizando um sql-warehouse cluster.
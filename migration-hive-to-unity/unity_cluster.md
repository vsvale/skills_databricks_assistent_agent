Para ser capaz de gravar tabelas em um determinado schema de um catálogo no Unity Catalog é necessário utilizar um cluster do tipo Unity Catalog. Um cluster é Unity Enabled quando utiliza o Access Mode Standard ou Dedicated.

Modo Classico:

Screenshot 2025-03-28 at 16.05.40.png
 

Modo Simple form:

Screenshot 2025-03-28 at 16.07.36.png
 

 

Um cluster Unity Catalog possui o seguinte tag:

Modo Classico:

Screenshot 2025-03-28 at 16.06.10.png
 

Modo Simple Form:

Screenshot 2025-03-28 at 16.08.01.png
 

Caso tente utilizar um cluster que não esteja habilitado para o Unity Catalog para ler ou gravar uma tabela do Unity você receberá o seguinte erro:



[UC_NOT_ENABLED] Unity Catalog is not enabled on this cluster.
Clusters Unity enabled são capazes de ler tabelas do hive_metastore.

Os clusters warehouses como o plataformas-dados-ecs são Unity Catalog enabled.

Limitações Standard Access Mode
Standard compute requirements and limitations | Databricks on AWS  

Databricks recomenda utilizar cluster com Access Mode Standard, porém esse possui algumas limitações.

Suporte a Python, SQL e Scala (DBR 13.3+)

Não suporta DBR ML

Não suporta o modo de processamento Structured Streaming continuous

Não suporta RDD APIs

Não suporta Spark Context (DBR 14+)

Não suporta emptyRD,range, parallelize,getConf

Não suporta Hive UDFs

Não suporta a lib de criptografia e DataQuality utilizadas no Datalake

Caso encontre alguma limitação utilize um cluster com Access Mode Dedicated
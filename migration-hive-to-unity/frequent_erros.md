[UNAUTHORIZED_ACCESS] Unauthorized access: PERMISSION_DENIED: User does not have CREATE TABLE and USE SCHEMA on Schema 'analytics_prd.gold'. SQLSTATE: 42501. Solução: Entre em contato com o time de evolução de plataforma para que seja corrigida as permissões do usuário sistemico.

[UC_NOT_ENABLED] Unity Catalog is not enabled on this cluster. SQLSTATE: 56038. Solução: Acrescente no seu job.json um  "data_security_mode" diferente de NONEpara access mode standard"USER_ISOLATION"e para dedicated "SINGLE_USER"

UC_COMMAND_NOT_SUPPORTED.WITHOUT_RECOMMENDATION] The command(s): Creating a persistent view that references both Unity Catalog and Hive Metastore objects are not supported in Unity Catalog.  SQLSTATE: 0AKUC. Solução: migre as tabelas utilizadas pela view que referência tabelas no hive_metastore ou transforme a view em tabela com um CTAS, nesse caso será necessário um job para manter a tabela atualizada.

[DELTA_UNSUPPORTED_OUTPUT_MODE] Data source com.databricks.sql.transaction.tahoe.sources.DeltaDataSource does not support Update output mode. Solução: Troque o mode de update do structured streaming para append

ERRO DE CHAVE SSH INVALIDA EM JOBS de CRM DE ENVIO PARA SFTP SALESFORCE. Solução: Alterar versão do DBR para 14.3, e,caso necessário, alterar a versão da lib de criptografia para a seguinte - /Volumes/dataops_prd/libraries/libs/crm/ecs_dataops_utils_cryptography-0.10-py3-none-any.whl

com.amazon.deequ.analyzers.runners.MetricCalculationRuntimeException: org.apache.spark.SparkException: … java.lang.NoSuchMethodError: ‘long org.apache.spark.sql.catalyst.expressions.XxHash64Function$.hash(java.lang.Object, org.apache.spark.sql.types.DataType, long)'…
Solucao: Utilize um DBR com 3.5.0 como o 15.4 LTS ou 14.3 LTS

Caused: java.lang.IllegalArgumentException: Could not instantiate {message={error_code=GIT_CONFLICT, message=Conflict pulling from remote. Conflicting files: src/databricks/workspace/03_delivery_sftp.py.
Solucao: de um pull na master e rode novamente

NoCredentialsError: Unable to locate credentials
Solucao: Utilize um cluster dedicated, crie retries no codigo e se possivel utilize o Databricks Secrets

AttributeError: module 'lib' has no attribute 'X509_V_FLAG_NOTIFY_POLICY'
Solucao: Atualize o DBR
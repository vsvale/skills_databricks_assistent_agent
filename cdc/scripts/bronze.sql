DECLARE catalog = 'dataops_prd';
USE CATALOG IDENTIFIER(catalog);
DECLARE schema = 'bronze';
USE SCHEMA IDENTIFIER(schema);
DECLARE tabela = 'operacoes';

CREATE TABLE IF NOT EXISTS IDENTIFIER(tabela) (
    id INT,
    name STRING,
    status STRING,
    value DECIMAL(18,2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    record_hash STRING
)
TBLPROPERTIES(
    'delta.enableDeletionVectors' = 'true',
    'delta.enableChangeDataFeed' = 'true',
    'delta.enableRowTracking' = 'true',
    'delta.deleteRetentionDuration' = '30 day',
    'delta.logRetentionDuration' = '30 day',
    'delta.autoOptimize.optimizeWrite' = 'true'
)
CLUSTER BY AUTO;

OPTIMIZE IDENTIFIER(tabela) FULL;
VACUUM IDENTIFIER(tabela) FULL;
VACUUM IDENTIFIER(tabela) LITE;
ANALYZE IDENTIFIER(tabela) COMPUTE STATISTICS FOR ALL COLUMNS;
ANALYZE IDENTIFIER(tabela) COMPUTE DELTA STATISTICS;

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
CLUSTER BY AUTO
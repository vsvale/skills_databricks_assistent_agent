# Pre-requisitos
- tabelas delta lake
- chave natual ou surrogate key definida
- colunas de auditoria: updated_at e  created_at ambas TIMESTAMP
- coluna record_hash STRING para deteccao de mudancas

# BRONZE
- Dados brutos
- Pode contar duplicidade em id
- mantem historico completo de mudancas
- append-only
- clustering por id, updated_at
- gera o record_hash
- gera a criptografia
- Run  scripts/bronze_sql.sql or scripts/bronze_py.py

# SILVER
- dados deduplicados, apenas 1 regristro por ID
- aplica as operacoes I (insert), U (ypdate) e D (delete)
- Deduplicacao via ROW_NUMBER() com QUALIFY = 1
- watermark incremental
- deteccao de mudanca via record_hash
- colunas de auditoria silver_loaded_at e silver_updated_at
- Run  scripts/silver_sql.sql or scripts/silver_py.py

# Gold
- Agregacao diarias por status
- KPIs de negocio
- metricas financeias
- Otimizada para dashboads e relatorios
- Run  scripts/gold_sql.sql or scripts/gold_py.py

## MERGE (UPSERT)
```sql
MERGE INTO target
USING source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

## DEDUPLICACAO com QUALIFY
```sql
SELECT * FROM tabela
QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC) = 1
```

## WATERMARK INCREMENTAL
Processa apenas registros novos ou alterados desde a ultima carga
```sql
WHERE updated_at > ultimo_watermark (
```

## RECORD HASH
Detecta mudancas de conteudo
```sql
sha2(concat_ws('||',cast(id as string),valos::string, nome),256)
```

## VARIAVEIS SQL
```sql
DECLARE ultimo_watermark TIMESTAMP DEFAULT timestamp('2026-01-01');
SET VAR ultimo_watermark = select max(updated_at) from silver);
```

For more details, consult the references/REFERENCE.md.
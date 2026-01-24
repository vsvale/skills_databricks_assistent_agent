from concurrent.futures import ThreadPoolExecutor



#variables
schema = ["default"]
group = "users"
grants = "USE SCHEMA, SELECT"

# Remove Foreign Catalogs, samples, sytem, internals and legacy catalogs
catalogs_df = spark.sql("show catalogs").filter(
    "catalog not in ('hive_metastore', 'legacy_hive_catalog', 'sample', 'system','__databricks_internal','clearsale','delta_share_test','delta_share_teste','gcp_bq_lakeflow_prd','glue-odin-contatos-catalog','glue-odin-contatos_catalog','clearsale_enriquecimento_contatos','nike_glue_prd','samples','glue_datahub_pep_ingestion_prd')"
)

def uppdate_grants(catalog):
    print(f"Executing {catalog}")
    try:
        spark.sql(f"GRANT {grants} ON SCHEMA {catalog}.{schema} TO `{group}`")
    except Exception as exception: 
        print(f"Exception occurred while updating {catalog}.{schema} TO {group}: {exception}")
        pass

catalogs = spark.sql("select collect_set(catalog) from {catalogs_df}",catalogs_df=catalogs_df).first()[0]

with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(uppdate_grants,catalogs)
---
name: create-job-json-for-unity
description: How to define Unity Catalog job configurations in JSON format for creating and updating jobs through the Databricks Jobs AP
---

***

# **Skill: Creating and Maintaining Databricks Jobs Using job.json**

## **Description**

This skill teaches how to structure, validate, and maintain `job.json` files used by the CI/CD pipeline to create and update Databricks jobs. It covers Git as source, required tags, mandatory policies, pools, and cluster rules.

***

# **Step-by-Step Instructions**
Caso o usuario solicitar migrar um job.json para o unity sempre crie um arquivo `job_proposition.json` no mesmo folder do job.json original.
Sempre faca um pwd ou ls par identificar o folder atual e confirme se voce esta criando o job_proposition.json` no mesmo folder do job.json base. 
Depois faca um ls para verificar se o arquivo realmente foi gerado.
Pom fim verifica se o arquivo é um json valido.

## **1. Understanding `job.json`**

*   `job.json` is the **input file** consumed by the CI/CD pipeline to **create** or **update** Databricks jobs. 

*   The CI/CD pipeline uses Databricks API endpoints:
    *   **jobs/create**: https://docs.databricks.com/api/workspace/jobs/create
    *   **jobs/reset**: https://docs.databricks.com/api/workspace/jobs/reset

***

## **2. Configure Git as the Source**

### **Required Adjustments**

*   Add `"git_source"` block to `job.json`. The git_url for the unified repository is not static and will vary depending on the product. More information in https://serasaexperian.atlassian.net/wiki/spaces/DE/pages/5696585778/Uso+de+Reposit+rios+Unificados+por+Produto. 

Sempre pergunte qual o produto do job.json. Use essa informacao tanto para o repositorio quanto para a tag BusinessServices.

```json
      "git_source": {
        "git_url": "https://gitlab.ecsbr.net/dataops/core/dataops-core-mkt",
        "git_provider": "gitLab",
        "git_branch": "main"
    },
```

*   Change `notebook_task.source` from `"WORKSPACE"` to `"GIT"`
*   Update `notebook_path` to use **relative path inside the repository** 

### **Example Transformation**

**Before (Workspace):**

```json
"notebook_task": {
  "notebook_path": "/Repos/ecs_ci_cd_datalake@br.experian.com/dataops-ml-ecred-pedidos-emprestimo/src/databricks/workspace/02-ecs-dataops-ml-ecred-pedidos-emprestimo-base-predict",
  "source": "WORKSPACE"
}
```

**After (Git):**

```json
    {
      "notebook_task": {
        "notebook_path": "dataops-ml-ecred-pedidos-emprestimo-uc/src/databricks/workspace/02-ecs-dataops-ml-ecred-pedidos-emprestimo-base-predict",
        "source": "GIT"
      },
    },
...
"git_source": {
    "git_url": "https://gitlab.ecsbr.net/dataops/core/dataops-core-ecred",
    "git_provider": "gitLab",
    "git_branch": "main"
  },
```
***
O nome do job `name` é sempre o nome do folder, nesse exemplo dataops-ml-ecred-pedidos-emprestimo-uc é o nome do job e nome do folder a partir do root.
**Before (Workspace):**

```json
"name": "gcp_ga4_to_bronze_v2",
...
"notebook_task": {
  "notebook_path": "/Repos/ecs_ci_cd_datalake@br.experian.com/dataops-pipeline-analytics-ga4-daily/src/databricks/workspace/ingest_ga4_bq_to_bronze",
  "source": "WORKSPACE"
}
```

**After (Git):**

```json
"name": "gcp_ga4_to_bronze_v2_uc",
...
"notebook_task": {
  "notebook_path": "gcp_ga4_to_bronze_v2_uc/src/databricks/workspace/ingest_ga4_bq_to_bronze",
  "source": "WORKSPACE"
}
...
"git_source": {
    "git_url": "https://gitlab.ecsbr.net/dataops/core/dataops-core-mkt",
    "git_provider": "gitLab",
    "git_branch": "main"
  },
```

***

## **3. Mandatory Tags**
Required tags listed in https://serasaexperian.atlassian.net/wiki/spaces/DE/pages/4510089353/Tagueamento+de+Jobs+no+Databricks

`datadog` and `Data_Category` tags are **required** because Datadog uses them to decide whether job failure alerts must be triggered.  
Therefore, **webhook notifications to Teams are no longer required**.

Here is the revised **English Markdown version**, now keeping the original Portuguese values for `Data_Category` exactly as you requested:

***

## **Required Tag Fields**

### **BU**

Business Unit responsible for the job.  
**Examples:** `ECS`, `TEX`, `PV`.

***

### **BusinessServices**

Product or team that owns the job.  
**Example:** `PREMIUM`.

***

### **Environment**

Execution environment for the job.  
**Example:** `PRD`.

***

### **CreatedBy**

Team responsible for monitoring and supporting the job.  
**Examples:** `DATAOPS`, `CRM`, `PERSONALIZATION`.

***

### **JobType**

Classification of the job type.  
**Allowed values:**

*   `ETL`
*   `SELF_SERVICE`
*   `ALL_PURPOSE`
*   `DLT`
*   `WAREHOUSE`
*   `MAINTENANCE_JOB` (e.g., *optimize*, *vacuum*)

***

### **Data\_Category**

Importance level of the results produced by the job.  
**Possible values:**

*   `ALTA`
*   `MEDIA`
*   `BAIXA`
*   `BAIXISSIMA`

*(Values kept in Portuguese as requested.)*

***

### **datadog**

Indicates whether the job should appear in Datadog dashboards.  
**Allowed values:** `TRUE`, `FALSE`.

***
EXAMPLE: 
```json
"tags": {
  "BU": "ECS",
  "datadog": "TRUE",
  "BusinessServices": "BOX",
  "Environment": "PRD",
  "CreatedBy": "ANALYTICS",
  "JobType": "ETL",
  "Data_Category": "BAIXA"
}
```


***

## **4. Policies and Pools**

### **4.1 Purpose of Policies**

Policies:

*   Control allowed configurations in production
*   Define default cluster parameters
*   Enforce limits and governance rules
*   Are **mandatory** for any CI/CD created job

### **4.2 Key Rules**

*   Only **administrators** may use `Policy Unrestricted`
*   **Self Service Jobs Users** and **Self Service Jobs High Performance** policies **must not be used** in production

***

## **5. Pool Requirements**

*   All productive policies **mandate** use of **Instance Pools**
*   Pools accelerate job availability by using pre‑provisioned compute
*   All pools use **Fleet instances** (recommended by Databricks) because they:
    *   Search all instance versions
    *   Use all AZs
    *   Reduce job launch failures

***

## **6. Cluster Configuration Rules**

**Do NOT fill** in the following fields:

*   `aws_attributes`
*   `node_type_id`
*   `driver_node_type_id`
*   `enable_elastic_disk`
*   `data_security_mode`
*   `runtime_engine`  
*   `spark_conf`
*   `spark_env_vars`
*   `libraries`
    All these are managed automatically by the **Policy**.

Todas as libraries devem estar instaladas na policy, por isso nao devem estar presentes nem a nivel de cluster e nem a nivel de task. Se tem policy nao deve haver libraries.

### **Example – Incorrect cluster configuration (Do NOT use):**

```json
"aws_attributes": {
  "first_on_demand": 1,
  "availability": "SPOT_WITH_FALLBACK",
  ...
},
"node_type_id": "r6gd.2xlarge",
"driver_node_type_id": "r6gd.xlarge"
```

### **Correct (Policy + Pool only):**

```json
"new_cluster": {
  "instance_pool_id": "0904-143702-ides62-pool-dkt26byo",
  "driver_instance_pool_id": "0904-143702-slump63-pool-oanf22hc",
  "autoscale": { "max_workers": 5 }
}
```

***

## **7. Selecting Custom Pools**

Use the function, but change the node type:

```sql
select 'worker', system_prd.control.get_instance_pool_id(FALSE, "rd-fleet.xlarge")
UNION
select 'driver', system_prd.control.get_instance_pool_id(TRUE, "rd-fleet.xlarge");
```

*   Drivers use **On‑Demand** instances
*   Workers use **Spot** instances

Here is your complete **Markdown table**, formatted with three columns:

*   **Node Type**
*   **Driver Pool ID**
*   **Worker Pool ID**

***

## **Instance Pools Table**

| **Node Type**         | **Driver Pool ID**                 | **Worker Pool ID**                 |
| --------------------- | ---------------------------------- | ---------------------------------- |
| **c-fleet.xlarge**    | 0909-172519-lorn97-pool-6pwsrymo   | 0909-172519-oven95-pool-cg867ndc   |
| **c-fleet.2xlarge**   | 0909-172519-cleft107-pool-7tuofksg | 0909-172519-hail106-pool-42850t1s  |
| **c-fleet.4xlarge**   | 0909-172520-thy95-pool-rrebthcg    | 0909-172520-gads91-pool-8yu9ci6o   |
| **cd-fleet.xlarge**   | 0902-163923-dyer131-pool-qog5fy8g  | 0902-163923-phase109-pool-7u1jjeog |
| **cd-fleet.2xlarge**  | 0902-163924-pates110-pool-lzz79te8 | 0902-163924-wipe8-pool-z916tvrl    |
| **cd-fleet.4xlarge**  | 0902-163924-tins134-pool-r66ei0b4  | 0902-163924-brew133-pool-iu8qcx00  |
| **cgd-fleet.xlarge**  | 0902-164004-rolls134-pool-d4gzfocw | 0902-164004-slink9-pool-9fvofuhc   |
| **cgd-fleet.2xlarge** | 0902-164002-paste132-pool-xjou6040 | 0902-164002-seat97-pool-xz4uohe8   |
| **cgd-fleet.4xlarge** | 0902-164005-doggy112-pool-or0uzbps | 0902-164005-chile98-pool-6u3ys9ao  |
| **cgd-fleet.8xlarge** | 0902-164005-haled86-pool-6fjwcc28  | 0902-164005-djinn99-pool-nwck5li8  |
| **m-fleet.xlarge**    | 0909-172650-wales99-pool-7gt1kseo  | 0909-172650-rests98-pool-1qhnagb4  |
| **m-fleet.2xlarge**   | 0909-172646-notch98-pool-vzo4inm8  | 0909-172645-pans97-pool-2kc5zi8g   |
| **m-fleet.4xlarge**   | 0909-172646-colon96-pool-k5hydhjl  | 0909-172646-slash99-pool-p48555hs  |
| **m-fleet.8xlarge**   | 0909-172647-velds87-pool-ezgpqntc  | 0909-172647-mason109-pool-orq9kyq8 |
| **md-fleet.xlarge**   | 0909-172813-thee103-pool-odj2718w  | 0909-172813-stint90-pool-cm6qlhkc  |
| **md-fleet.2xlarge**  | 0909-172813-cave102-pool-xl5tzzm8  | 0909-172812-plain111-pool-fw2yo6c0 |
| **md-fleet.4xlarge**  | 0909-172814-ratio81-pool-2yy4jpjl  | 0909-172814-fewer93-pool-nj1hh2j4  |
| **md-fleet.8xlarge**  | 0909-172815-tune91-pool-npi6a1hs   | 0909-172815-sorta112-pool-ac6l8wsw |
| **mg-fleet.xlarge**   | 0902-150434-beams95-pool-suf32oks  | 0902-150434-cage104-pool-tfn1egi8  |
| **mg-fleet.2xlarge**  | 0902-150432-kick5-pool-nnl8n4sw    | 0902-150432-calfs4-pool-mmguty4w   |
| **mg-fleet.4xlarge**  | 0902-150431-surer125-pool-h8ro48i8 | 0902-150430-sofa131-pool-jjun12xc  |
| **mg-fleet.8xlarge**  | 0902-150430-lofts94-pool-o5mpiccw  | 0902-150429-wees80-pool-na3wauc0   |
| **mgd-fleet.xlarge**  | 0909-174306-parka102-pool-6n24e040 | 0909-174306-boots103-pool-ageg31u8 |
| **mgd-fleet.2xlarge** | 0909-174310-toque114-pool-7bd49a8g | 0909-174310-ogled87-pool-19ud5i4w  |
| **mgd-fleet.4xlarge** | 0909-174309-rook100-pool-oey0oowg  | 0909-174309-gabs113-pool-2o9921ao  |
| **mgd-fleet.8xlarge** | 0909-174308-disco103-pool-gratdv68 | 0909-174308-rift99-pool-rpaqgl5s   |
| **r-fleet.xlarge**    | 0909-172255-heard84-pool-cuz2iryo  | 0909-172255-glen94-pool-jlgu8aa8   |
| **r-fleet.2xlarge**   | 0909-172252-beck87-pool-edinas5s   | 0909-172252-flays93-pool-lzsr7lsw  |
| **r-fleet.4xlarge**   | 0909-172250-oat91-pool-91bkpes0    | 0909-172250-bird94-pool-e6cwc840   |
| **r-fleet.8xlarge**   | 0909-172251-smite95-pool-bxrz4x74  | 0909-172251-ennui92-pool-h4duxe6o  |
| **rd-fleet.xlarge**   | 0904-143705-conk181-pool-9095vkkc  | 0904-143705-whet3-pool-ubsdyblg    |
| **rd-fleet.2xlarge**  | 0904-143702-slump63-pool-oanf22hc  | 0904-143702-ides62-pool-dkt26byo   |
| **rd-fleet.4xlarge**  | 0904-143706-nerdy201-pool-fcqgbsb4 | 0904-143705-gnash132-pool-239dsgks |
| **rd-fleet.8xlarge**  | 0904-143705-pour180-pool-mdb92974  | 0904-143704-plied143-pool-ib5e4phs |
| **rg-fleet.xlarge**   | 0909-174834-rent103-pool-50z6kceo  | 0909-174834-yucca96-pool-2lrsoowg  |
| **rg-fleet.2xlarge**  | 0909-174844-vole117-pool-evscpqts  | 0909-174844-morns105-pool-j2inw45s |
| **rg-fleet.4xlarge**  | 0909-174846-huffs107-pool-qx8bype8 | 0909-174845-sward97-pool-0k723its  |
| **rg-fleet.8xlarge**  | 0909-174840-skids106-pool-3t4acx00 | 0909-174840-ruffs107-pool-wo6t60b4 |
| **rgd-fleet.xlarge**  | 0904-143723-bus203-pool-d16j5qfl   | 0904-143723-bluer202-pool-aela9gy8 |
| **rgd-fleet.2xlarge** | 0904-143724-entry182-pool-ops4qzv4 | 0904-143723-fame4-pool-mx9sp4pc    |
| **rgd-fleet.4xlarge** | 0904-143725-wider64-pool-337a51cg  | 0904-143724-chit141-pool-ni6qkh5c  |
| **rgd-fleet.8xlarge** | 0904-143725-just206-pool-1g6hbv9s  | 0904-143725-gamey205-pool-lx5l44l0 |

***

***

## **8. Engineering Production Policies**

### **Legacy (Hive) Policies**

***
Aqui está a **tabela em Markdown** organizada e padronizada com as três policies solicitadas:

***

## **Legacy Policies – Markdown Table**

| **Policy Name**                          | **ID**             | **URL**                              | **Descrição**                                                                                                                                                                                            | **DBR Default**        |
| ---------------------------------------- | ------------------ | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| **Job Legacy HC Engenharia**             | `0011B27BEA0E2488` | Job Legacy HC Engenharia             | Utilizada para jobs Hive.                                                                                                                                                                                | DBR `16.4.x-scala2.12` |
| **Job Legacy HC Engenharia Request Pay** | `000D1926BF4A9476` | Job Legacy HC Engenharia Request Pay | Utilizada para jobs Hive que leem buckets com *request pay*. Inclui `spark.hadoop.fs.s3a.requester-pays.enabled=true`.                                                                                   | DBR `16.4.x-scala2.12` |
| **Job Legacy High Performance**          | `001AA133374E8403` | Job Legacy High Performance          | Para jobs Hive que necessitam `node_types` 12xlarge, 16xlarge ou 24xlarge. Apenas o service principal `ecs_serasa_self_service_high_perfomance (2cd4897d-ba53-4dca-933d-b94a34f6c8ba)` possui permissão. | DBR `16.4.x-scala2.12` |

***

### **Unity Catalog (UC) Policies**

***
Aqui está a **tabela em Markdown** com as três **UC Policies**, organizada, clara e consistente com o formato anterior:

***

## **UC Policies – Markdown Table**

| **Policy Name**                   | **ID**             | **URL**                     | **Descrição**                                                                                                                                                                                                                                                                     | **DBR Default**        |
| --------------------------------- | ------------------ | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| **Job UC Dedicated Engenharia ✈** | `001F0E3652D6CF50` | Job UC Dedicated Engenharia | Utilizada para jobs Unity.                                                                                                                                                                                                                                                        | DBR `16.4.x-scala2.12` |
| **Job UC High Performance**       | `0017A325D8176049` | Job Legacy High Performance | Utilizada para jobs Unity que necessitam `node_types` 12xlarge, 16xlarge e 24xlarge. Apenas o service principal `ecs_serasa_self_service_high_perfomance (2cd4897d-ba53-4dca-933d-b94a34f6c8ba)` pode utilizá-la. **Requer aprovação do @Arnabat, Carlos e do comitê Tech Sync.** | DBR `16.4.x-scala2.12` |
| **Lakeflow UC Engenharia**        | `0008F8DCE5E7C0A1` | Lakeflow UC Engenharia      | Utilizada para Lakeflow ETL Pipelines.                                                                                                                                                                                                                                            | DBR `auto-latest-lts`  |

***

# **Examples**

## **Minimal Valid job.json**

```json
{
  "name": "my_job",
  "tasks": [
    {
      "task_key": "process",
      "notebook_task": {
        "notebook_path": "src/jobs/process",
        "source": "GIT"
      },
      "job_cluster_key": "cluster",
    }
  ],
  "git_source": {
    "git_url": "https://gitlab.ecsbr.net/dataops/core/my-repo",
    "git_provider": "gitLab",
    "git_branch": "main"
  },
  "job_clusters": [
    {
      "job_cluster_key": "cluster",
      "new_cluster": {
        "instance_pool_id": "POOL_ID",
        "driver_instance_pool_id": "DRIVER_POOL_ID",
        "autoscale": { "max_workers": 5 }
      }
    }
  ],
  "tags": {
    "datadog": "true",
    "Data_Category": "Internal"
  }
}
```

***
Se for definido uma job_cluster_key ela deve ser utilizada em pelo menos uma task. Adicione job_cluster_key a todas as tasks, a menos que o usuario especifique um job_cluster_key especifica ou especifique que deseja usar um cluster serveless para a task.

# **Edge Cases**

### **1. Workspace notebooks are forbidden for production**

Only **Git** must be used as source.

### **2. Missing tags break CI/CD**

If `datadog` or `Data_Category` tags are missing, Datadog alerts won't trigger.

### **3. Policy mismatch causes job creation failures**

If you specify disallowed cluster fields, CI/CD fails.

### **4. High‑performance policies require formal approval**

Required by Carlos Arnabat and the Tech Sync Committee.

***

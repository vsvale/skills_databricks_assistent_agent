# Library Management

## Policy
- **Do NOT** install libraries at the Task/Cluster level manually if possible.
- **Use Policies**: Libraries should be defined in Cluster Policies or installed from Volumes.

## Installing from Volumes
Upload `.whl` or `.jar` to a Volume (e.g., `libs` managed volume).
```python
# Path Example
/Volumes/dataops_prd/libraries/libs/hash/my_lib-0.1-py3-none-any.whl
```

## Specific Libs
- **Cryptography**: `/Volumes/dataops_prd/libraries/libs/crm/ecs_dataops_utils_cryptography...`
- **Data Quality**: `/Volumes/dataops_prd/libraries/libs/ecs_dataops_lib_data_quality_UC...`

These libraries often require **User Isolation** (Dedicated) mode.

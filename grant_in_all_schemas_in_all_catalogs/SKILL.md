---
name: grants_in_all_catalogs_in_schema_to_group
description: Automates granting permissions across multiple catalogs and schemas, ensuring consistent access control for a specified group.
---

# How This Skill Works

This skill automates the process of granting privileges (such as `SELECT`, `USE SCHEMA`, etc.) to a target group across all catalogs and schemas—while also safely excluding system, sample, or otherwise restricted catalogs.

Use this skill when you need to:
- Apply standardized privilege assignments across many catalogs.
- Reduce manual grant operations.
- Ensure consistent group-level access for data engineering or platform operations.

# Step-by-Step Guide

1. **Gather Required Inputs**  
   Before running the automation, collect the following information:  
   - The **target group** that should receive the grants.  
   - The **list of privileges** to grant (e.g., `USE SCHEMA`, `SELECT`,`ALL PRIVILEGES`,`MANAGE`).  
   - The **schemas** you want the script to affect (default is `"default"`).  
   - The **catalogs you want to exclude** from processing (system catalogs, sample catalogs, legacy catalogs, internal catalogs, etc.).

2. **Update the Script Parameters**  
   Modify the variables at the top of  
   `scripts/grant_all_catalog_all_schema_to_group.py`  
   to match your environment:  
   - `schema`  
   - `group`  
   - `grants`  
   - The exclusion list (inside the `filter(...)` clause)

3. **Review the Final Catalog List**  
   The script will query all available catalogs and automatically remove excluded ones.  
   Confirm that the resulting list aligns with the access structure you expect.

4. **Execute the Script**  
   Run:  
   scripts/grant_all_catalog_all_schema_to_group.py

The script uses multithreading (`ThreadPoolExecutor`) to accelerate execution across many catalogs.

5. **Validate the Grants**  
After execution:  
- Verify a few catalogs manually to ensure grants applied correctly.  
- Review logs printed by the script for any exceptions or denied operations.

For more details, consult the references/REFERENCE.md.



# Skills for Databricks Assistant

**Give your Databricks Assistant superpowers.** This repo is a curated set of [Agent Skills](https://agentskills.io/specification) and Cursor rules for the [Databricks Assistant](https://docs.databricks.com/aws/en/assistant/skills)—domain-specific knowledge, workflows, and scripts that the assistant loads when your task needs them.

Use these skills in **Databricks** (Assistant in the workspace) or adapt them for **Cursor** and other agents that support the Agent Skills format.

---

## What’s in this repo?

| Skill | What it does |
|-------|----------------|
| **[databricks_connect](databricks_connect/)** | Connect your local IDE to Databricks: install, auth (OAuth U2M/M2M), cluster/serverless config, and run PySpark from PyCharm, VS Code, or Jupyter. |
| **[databricks_cli](databricks_cli/)** | Install and use the Databricks CLI: auth, profiles, and common commands (clusters, jobs, workspace, Unity Catalog, bundles). |
| **[unity-catalog](unity-catalog/)** | Manage Unity Catalog: catalogs, schemas, tables, permissions, external locations, storage credentials, Delta Sharing, and best practices. |
| **[lakeflow-sdp](lakeflow-sdp/)** | Build and run Lakeflow Spark Declarative Pipelines: streaming tables, materialized views, expectations, Auto Loader, CDC, and ETL in SQL/Python. |
| **[databricks-demo](databricks-demo/)** | Install Databricks Lakehouse demos with dbdemos: notebooks, SDP pipelines, DBSQL dashboards, ML models; list/install by category, use current cluster or UC catalog/schema. |
| **[grant_in_all_schemas_in_all_catalogs](grant_in_all_schemas_in_all_catalogs/)** | Automate grants across catalogs and schemas for a group (with safe exclusions for system/sample catalogs). Includes a ready-to-run Python script. |
| **[generate_skills](generate_skills/)** | *Meta-skill:* how to create new Databricks Assistant skills (structure, frontmatter, references, scripts) following this repo’s conventions. |

Each skill lives in its own folder with a `SKILL.md` (instructions + examples), optional `references/`, and optional `scripts/` for runnable code.

---

## Quick start

### Use in Databricks

1. In your Databricks workspace, open **Assistant** and go to **Skills**.
2. Add a skill from this repo: either point the Assistant at this repo (e.g. via Git sync or by copying a skill folder’s path) or paste the contents of a `SKILL.md` and any referenced files.
3. Ask the Assistant something that matches the skill (e.g. *“How do I authenticate the Databricks CLI?”* or *“Create a Unity Catalog schema for analytics.”*). It will use the right skill when relevant.

### Use in Cursor (or similar)

- **Rules:** `.cursor/rules/` holds Cursor rule files (e.g. `generate_databricks_agent_skills.mdc`, `databricks_application_best_practices.mdc`) that guide how to generate and apply Databricks-related skills.
- **Skills:** The same `SKILL.md` files and folders can be referenced from Cursor’s skill/rules setup so the editor’s AI uses this knowledge when you work on Databricks code or docs.

### Clone and explore

```bash
git clone https://github.com/YOUR_ORG/skills_databricks_assistent_agent.git
cd skills_databricks_assistent_agent
```

The repo includes a `databricks.yml` [Asset Bundle](https://docs.databricks.com/dev-tools/bundles/) so you can use it with the Databricks CLI and VS Code extension; targets (e.g. `dev`) are defined in the bundle.

---

## Repo structure

```
.
├── README.md
├── databricks.yml                    # Databricks Asset Bundle (optional)
├── .cursor/
│   └── rules/                        # Cursor rules for skill generation & best practices
│       ├── generate_databricks_agent_skills.mdc
│       └── databricks_application_best_practices.mdc
├── databricks_connect/               # Skill: local IDE → Databricks
│   ├── SKILL.md
│   └── references/
├── databricks_cli/                   # Skill: CLI install, auth, commands
│   ├── SKILL.md
│   └── references/
├── unity-catalog/                    # Skill: catalogs, schemas, permissions
│   ├── SKILL.md
│   └── references/
├── lakeflow-sdp/                     # Skill: declarative pipelines (SDP)
│   ├── SKILL.md
│   └── references/
├── databricks-demo/                  # Skill: dbdemos install, list, options
│   ├── SKILL.md
│   └── references/
├── grant_in_all_schemas_in_all_catalogs/   # Skill: bulk grants + script
│   ├── SKILL.md
│   ├── references/
│   └── scripts/
└── generate_skills/                  # Meta-skill: how to create new skills
    ├── SKILL.md
    └── references/
```

Every skill has a **name** (matches folder), a **description** (what it does + when to use it), and Markdown instructions; many add `references/` and `scripts/` for depth and automation.

---

## References

- [Databricks Assistant – Skills](https://docs.databricks.com/aws/en/assistant/skills)
- [Agent Skills specification](https://agentskills.io/specification)
- [Databricks Asset Bundles](https://docs.databricks.com/dev-tools/bundles/)
- [Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/)
- [Databricks Connect for Python](https://docs.databricks.com/en/dev-tools/databricks-connect/python/)
- [Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/)
- [Lakeflow Spark Declarative Pipelines](https://docs.databricks.com/aws/en/ldp/)
- [Databricks Tutorials (dbdemos)](https://www.databricks.com/resources/demos/tutorials) · [dbdemos on GitHub](https://github.com/databricks-demos/dbdemos)

---

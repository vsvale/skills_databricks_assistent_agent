---
name: generate-databricks-agent-skills
description: Continuously improve the skill generation process by recording and applying lessons learned. This skill is always on and serves as a meta-skill for skill development.
alwaysApply: true
---

# Generate Databricks Agent Skills (Meta-Skill)

This skill tracks lessons learned and best practices for creating and maintaining Databricks Assistant Agent Skills. It acts as a continuous improvement log to ensure that new skills benefit from past experiences.

## Usage
- **Always On**: This skill is automatically applied to guide the agent in every interaction.
- **Update Task**: After creating or updating *any* skill, you MUST reflect on the process and record new insights in the "Lessons Learned" section below.

## Lessons Learned
- **Documentation Consultation**: Always consult the documentation in `https://docs.databricks.com/llms.txt` or `https://context7.com/` and the following release notes to get the most recent releases relevant to the skill being updated:
  - `https://docs.databricks.com/aws/en/release-notes/dlt/2026`
  - `https://docs.databricks.com/aws/en/release-notes/serverless/`
  - `https://docs.databricks.com/aws/en/sql/release-notes/2025`
  - `https://docs.databricks.com/aws/en/release-notes/product/`
- **Move Legacy Content**: When modernizing a skill, move outdated but potentially useful patterns (like manual SQL CDC) to a dedicated file in the `references/` folder. This keeps the main `SKILL.md` focused on the recommended approach while preserving knowledge.
- **Dual Language Examples**: For core platform capabilities (like Auto CDC), providing both SQL and Python implementation scripts maximizes the skill's utility across different user personas.
- **Self-Contained Data Generation**: Including a script to generate sample data (e.g., `generate_sample_cdc_data.py`) is critical for allowing users and agents to verify and test the skill immediately.
- **Extract Complex Logic**: Complex configurations or flows (like the Database Replication pattern) should be extracted into dedicated scripts referenced from `SKILL.md`, rather than embedding long code blocks directly in the documentation.
- **Explicit Warnings**: Critical warnings about data loss or irreversible behaviors (like Once Flow) should be explicitly documented in both the `SKILL.md` and as comments in the code examples to ensure users don't miss them.
- **API Evolution**: When APIs evolve (e.g., `APPLY CHANGES` to `AUTO CDC`), update the skill to prioritize the new recommended path while keeping legacy references for backward compatibility. Explicitly note the relationship between old and new APIs.
- **External Documentation Integration**: When integrating external documentation (like tips and tricks blogs), categorize the insights (e.g., Configuration vs. Optimization vs. Usage) to structure the skill effectively rather than dumping a flat list of points.
- **Limit Awareness**: Always verify specific limits (e.g., character counts for instruction files) in the latest documentation before documenting them, as they can differ from general assumptions (e.g., 4,000 vs 20,000 chars).
- **Skill vs. Instruction**: When designing capabilities, always evaluate if the requirement is global (Instruction) or context-specific (Skill). Do not create skills for global behavior, and do not use instructions for complex, multi-step workflows.
- **Reference Extraction**: For skills with large static data (like ID tables or long configuration lists), move them to `references/REFERENCES.md` to keep the main `SKILL.md` concise (< 500 lines) and focused on workflows.
- **Anti-Pattern Documentation**: Explicitly including an "Anti-Patterns" section in skills helps prevent users from reverting to bad habits (e.g., "Forbidden: Workspace Paths") and clarifies the "why" behind the rules.
- **Migration Skills**: When creating migration skills, structure them around "Before vs After" code patterns and explicit strategy sections (e.g., Copy Only vs Refactor) to guide decision-making. Explicitly mapping old concepts (S3 paths) to new ones (Volumes) reduces hallucination.
- **Reference Consolidation**: Consolidate closely related standards (e.g., Catalog, Schema, Managed Tables, Volumes) into a single unified reference file to improve discoverability and reduce context switching. Keep implementation-heavy references (like code patterns or job configs) separate.
- **Deep Script Analysis**: When documenting migration skills, perform a deep line-by-line comparison of "Before" and "After" scripts to identify undocumented patterns (e.g., specific PII encryption logic, helper function replacements) that generic strategy documents might miss.
- **Example Relocation**: Strictly enforce the rule that example scripts must reside in the `scripts/` folder, not `references/`, to maintain a clean separation between documentation and executable code.
- **Ambiguity Warnings**: When documenting operations that can fail due to data state (like `MERGE` on duplicates), explicitly warn about these runtime failure modes and provide deduplication patterns as a prerequisite.
- **Reference Segmentation**: For skills with distinct alternative implementations (e.g., DLT Auto CDC vs Manual SQL Merge), separate the alternative/manual patterns into their own reference files (e.g., `references/merge_into_patterns.md`) to keep the main `SKILL.md` focused on the primary recommendation.
- **Tutorial Script Separation**: When creating tutorials, provide the full, executable code in `scripts/` (e.g., `scripts/dlt_cdc_pipeline.py`) alongside the step-by-step markdown explanation. This allows users to immediately run the solution while reading about it.
- **Code Extraction**: Extract long, complex code blocks (like manual SCD Type 2 SQL logic or foreachBatch functions) from markdown files into dedicated scripts. This keeps documentation clean and reduces copy-paste errors.
- **Mandatory Rule Enforcement**: When a rule is critical (e.g., updating lessons learned), mark it as **MANDATORY** and explicitly state that it is **NOT** optional to ensure strict adherence.
- **SQL vs Python Parity**: Explicitly document syntax differences (e.g., `QUALIFY` being SQL-only) to prevent users from attempting unsupported operations in PySpark. Always provide the correct alternative (like `window.filter` for PySpark).
- **Modern SQL Scripting**: When documenting batch SQL workflows, prefer modern `DECLARE`/`SET VAR` syntax for variables (Watermarking) over legacy widgets or Python interpolation, as it promotes pure SQL pipelines.


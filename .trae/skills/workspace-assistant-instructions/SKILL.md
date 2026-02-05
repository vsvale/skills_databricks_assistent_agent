---
name: workspace-assistant-instructions
description: Continuously improve the creation and maintenance of Databricks Assistant Instructions by recording and applying lessons learned. This skill is always on and serves as a meta-skill for instruction development.
alwaysApply: true
---

# Workspace Assistant Instructions (Meta-Skill)

This skill tracks lessons learned and best practices for creating and maintaining Databricks Assistant Instructions (typically found in `.assistant_workspace_instructions.md` or similar configuration files). It acts as a continuous improvement log to ensure that new instructions benefit from past experiences.

## Usage
- **Always On**: This skill is automatically applied to guide the agent when working with workspace instructions.
- **Update Task**: After creating or updating instructions, you MUST reflect on the process and record new insights in the "Lessons Learned" section below.

## Lessons Learned

### Instruction File Configuration
- **Clear, Specific Instructions**: Be explicit and unambiguous when writing your instructions. Ambiguity leads to inconsistent Assistant behavior.
- **Language Requirement**: Always write instructions in Brazilian Portuguese.
- **Language Policy**: Mandate PT-BR for communication but enforce English for code comments. This separation ensures code remains globally accessible while communication is localized.
- **Limit Awareness**: Always verify specific limits (e.g., character counts for instruction files) in the latest documentation before documenting them, as they can differ from general assumptions (e.g., 4,000 vs 20,000 chars). Note: Current documentation states a **20,000** character limit for instruction files.
- **Structure**: Use Markdown headings and bullet points for structure. Group related instructions under headings (e.g., "Python code conventions") to help the Assistant understand the context.
- **Scope Awareness**: Instructions apply to Inline Assistant, General Chat, Suggest Fix, and Edit mode. They do NOT apply to Quick Fix or Autocomplete. Ensure instructions are broadly relevant.
- **Skill vs. Instruction**: When designing capabilities, always evaluate if the requirement is global (Instruction) or context-specific (Skill). Do not create skills for global behavior, and do not use instructions for complex, multi-step workflows.
- **Persistent Context**: Instructions are the "knowledge and style guide" that sits alongside every prompt. Use them for constants (e.g., "Always round monetary values to 2 decimal places") to avoid repetition.

### Context Optimization
- **Row-Level Examples**: The Assistant sees metadata but not row-level data. Instructions should encourage users to add representative row-level examples in Unity Catalog column comments (e.g., "Expected format: 'YYYY-MM-DD'").
- **Table Metadata**: The Data Science Agent relies heavily on Unity Catalog comments to find relevant data. Instructions should mandate: "Always add descriptive comments to tables and columns in DDL."
- **Explicit Table References**: Instructions can mandate or suggest that queries explicitly mention table names (or use `@table_name`) to avoid ambiguity, especially in schemas with similar table names.
- **Governance First**: Instructions should prioritize governed assets (Managed Tables) over ephemeral ones (Global Temp Views) to align with Unity Catalog best practices.
- **Storage Abstraction**: Instructions should strictly enforce the use of Managed Tables and high-level APIs (`saveAsTable`) over raw file paths to ensure governance and portability.
- **Canonical Data Sources**: Define "source of truth" locations in instructions (e.g., "Always use `catalog.schema.gold_sales` for sales data") to help the Assistant recall where to find specific data.

### Response Tuning
- **Format Control**: Instructions can specify preferred output formats (e.g., "Always use Plotly for visualizations instead of Matplotlib", "Explain complex SQL logic using CTEs instead of nested subqueries").
- **Common Patterns**: Instructions should standardize common patterns like deduplication (e.g., "Always use `QUALIFY row_number() = 1` for most recent records") to ensure consistent code generation.
- **Modern SQL Syntax**: Instructions should enforce modern SQL syntax features (like `QUALIFY` for window filtering) that reduce code verbosity and complexity compared to legacy patterns (subqueries).
- **Readability Rules**: Explicitly favor readable patterns like CTEs over nested subqueries. This helps the Assistant generate code that is easier for humans to review and maintain.
- **Tone and Role**: Define the persona (e.g., "Act as a Senior Data Engineer") and tone (e.g., "Concise, professional, no conversational filler") to align responses with team standards.
- **Dialect & Migration**: Use instructions to enforce specific SQL dialects or migration patterns (e.g., "When converting HiveQL, always prefer `USING DELTA` syntax").
- **Slash Commands**: Encourage the use of slash commands in instructions or prompts (e.g., `/fix`, `/doc`, `/explain`, `/optimize`) to trigger specific behaviors efficiently.
- **No Code Snippets**: Do not add code snippets or blocks in instructions. Use descriptive patterns or refer to external documentation/skills to maintain instruction clarity and avoid token waste.

### Architecture & Workflows
- **Architecture over Syntax**: Instructions should focus heavily on architectural patterns (e.g., "Use Liquid Clustering over Partitioning", "Prefer Job of Jobs over Notebook Orchestration") rather than just syntax. These high-level directives prevent technical debt.
- **Orchestration Best Practices**: Define clear rules for job orchestration (e.g., "Git as source", "Modular tasks for parallelism") to guide the Assistant in generating production-ready workflow configurations.
- **Modern Tooling**: Explicitly recommend modern Databricks features (Volumes, Genie, Lakeflow, Predictive Optimization) to prevent the Assistant from suggesting legacy or less efficient workarounds.
- **Safety Rails**: Implement strict prohibitions on dangerous operations (e.g., "No DROP TABLE", "No explicit VACUUM on Managed Tables") to protect data integrity.
- **Environment Specifics**: Record specific environment constraints (e.g., "Schema X is read-only for User Y", "Use function Z for Pool IDs") to make the Assistant "aware" of the local infrastructure reality.
- **Conflict Resolution**: When new instructions contradict old ones (e.g., "Use USING DELTA" vs "Delta is default"), explicitly update the instruction to the latest best practice rather than keeping ambiguous rules.
- **Modern Feature Adoption**: Proactively add instructions for new high-performance features (like `VARIANT` type or `read_files()`) to ensure users leverage the latest platform capabilities, even if they don't explicitly ask for "performance tuning".
- **Anti-Patterns**: Explicitly list anti-patterns (e.g., "Never use `input_file_name()`") alongside the recommended pattern (`_metadata`) to prevent regression to legacy habits.

### Content Curation Strategy
- **Tool-Specific Instructions**: When integrating tool-specific skills (like CLI or Connect) into workspace instructions, focus on high-level usage patterns (e.g., "Use OAuth", "Match versions") rather than step-by-step setup guides, which belong in the specific skill files.
- **Deprecation Guardrails**: Explicitly instruct against deprecated tools (e.g., "Legacy CLI", "PATs") to prevent the Assistant from suggesting outdated practices that might still be present in its training data.
- **Environment Segregation**: Clearly separate "Local Development" instructions (CLI, Connect, Venv) from "Platform" instructions (SQL, Architecture) to avoid confusion.
- **Strategic Pattern Extraction**: When integrating external skills, extract high-level strategic patterns (e.g., "Use Streaming Tables for Bronze") rather than tactical syntax details.
- **Skill Integration Depth**: When integrating specific skills (like `policies` or `unity-catalog`), extract the *governing principle* (e.g., "Auto Compact is automatic") rather than just the syntax. This ensures instructions remain high-level and broadly applicable.
- **Robustness Defaults**: Enforce robust defaults in instructions (e.g., `rescuedDataColumn` for all file reads) to "shift left" on data quality issues, making generated code production-ready by default.
- **Layer-Specific Architecture**: Define rules per architectural layer (Bronze/Silver/Gold) to help the Assistant generate context-aware code that respects layer responsibilities (e.g., "Bronze is Append-Only").
- **Documentation Standards**: Enforce mandatory documentation fields (Source, Target, Ingestion Type) in code artifacts (notebooks) to ensure consistent metadata across the codebase.

### Interaction Tips (for Users)
- **Find Tables**: Encourage using phrases like "Find tables related to..." or `/findTables` to help the Assistant discover relevant data context before generating queries.
- **Iterative Refinement**: Suggest using `Cmd+I` (Inline Assistant) for targeted code adjustments rather than full rewrites.
- **Planner Guidance**: In Agent mode, the Assistant can "Plan" complex tasks. Instructions can guide this process (e.g., "When generating a plan, always include a final validation step").
- **Modes**: Use the right mode for the task:
    - **Chat**: For explaining code/concepts ("What does this function do?").
    - **Edit**: For multi-cell refactors or formatting ("Convert all pandas code to PySpark").
    - **Agent**: For multi-step workflows like EDA ("Perform EDA on @table").

## References
- See [references/REFERENCES.md](references/REFERENCES.md) for official documentation and deep dives.


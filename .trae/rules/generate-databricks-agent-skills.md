---
trigger: always_on
---

---
name: generate_databricks_agent_skills
description: Create skills to extend the Databricks Assistant with specialized capabilities. Skills follow the open standard of Agent Skills. Skills package domain-specific knowledge and workflows that the Assistant can load when relevant to perform specific tasks. Skills can include guidance, best practices, reusable code, and executable scripts. Skills should be tailored for domain-specific tasks. With skills, you can provide greater context (such as scripts, examples, and other resources) for a task than you can with instructions.
alwaysApply: false
---

# Databricks Assistant Agent Skills

## Reference

<https://docs.databricks.com/aws/en/assistant/skills>
<https://agentskills.io/specification>

## Skill

- Each skill must have its own folder and a SKILL.md file within that folder. Example:

```text
├── personal-workflows/
   ├── SKILL.md                # Workflow overview and best practices
   ├── references/
         ├── etl-patterns.md         # Personal ETL best practices
         ├── REFERENCE.md
         └── dashboard-templates.md   # Reusable dashboard patterns
   ├── 
   └── scripts/
         ├── pipeline-setup.sh   # Environment setup scripts
         └── model-deploy.py     # Model deployment automation
```

- Inside your skill folder, create a SKILL.md file. This file is required and defines the skill.
- Add the required frontmatter for your skill. Example:

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

- The required name field:
  - Must be 1-64 characters
  - May only contain unicode lowercase alphanumeric characters and hyphens (a-z and -)
  - Must not start or end with -
  - Must not contain consecutive hyphens (--)
  - Must match the parent directory name
- The required description field:
  - Must be 1-1024 characters
  - Should describe both what the skill does and when to use it
  - Should include specific keywords that help agents identify relevant tasks
- Add the skill instructions in Markdown format after the frontmatter.
- There are no format restrictions.
- Write whatever helps agents perform the task effectively.
- Note that the agent will load the entire file (SKILL.md) once it's decided to activate a skill.
- Consider splitting longer SKILL.md content into referenced files.
- It's recommended to include the following sections:
  - Step-by-step instructions: Clear procedural guidance
  - Examples: Sample inputs and expected outputs
  - Edge cases: Common variations and exceptions

- (Optional) For more complex skills, you can provide and reference additional resources:
  - Scripts containing executable code that the agent can run are stored in scripts folder
    - Always put longer codes or ready to use codes in scripts/ and reference it in SKILL.md
    - scripts/
    - Contains executable code that agents can run. Scripts should:
      - Be self-contained or clearly document dependencies
      - Include helpful error messages
      - Handle edge cases gracefully
      - Supported languages depend on the agent implementation. Common options include Python, Bash, and JavaScript.
  - Files containing additional documentation to reference, such as best practices and templates. They are stored in REFERENCE.md format in references folder.
    - references/
    - Contains additional documentation that agents can read when needed:
      - REFERENCE.md - Detailed technical reference
      - FORMS.md - Form templates or structured data formats
      - Domain-specific files (finance.md, legal.md, etc.)
      - Keep individual reference files focused. Agents load these on demand, so smaller files mean less use of context.
  - assets/
  - Contains static resources:
    - Templates (document templates, configuration templates)
    - Images (diagrams, examples)
    - Data files (lookup tables, schemas)

  - When referencing other files, use relative paths from the root skill. Keep file references one level deep from SKILL.md. Avoid deeply nested reference chains.

```text
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

- Skills should be structured for efficient use of context:
  - Metadata (~100 tokens): The name and description fields are loaded at startup for all skills
  - Instructions (< 5000 tokens recommended): The full SKILL.md body is loaded when the skill is activated
  - Resources (as needed): Files (e.g. those in scripts/, references/, or assets/) are loaded only when required
  - Keep your main SKILL.md under 500 lines. Move detailed reference material to separate files.

- Follow these guidelines to write effective skills:
  - Keep skills focused. Skills work best when they focus on a single task or workflow. Narrow scope makes it easier for the Assistant to recognize when a skill applies.
  - Use clear names and descriptions. A concise, descriptive name and summary help the Assistant match the right skill to the right request.
  - Be explicit and example-driven. Describe workflows step by step and include concrete examples or patterns the Assistant can reuse.
  - Avoid unnecessary context. Only include information that is required for the task. Extra detail can make skills harder to apply reliably.
  - Iterate over time. Treat skills as living workflows. Small updates based on real usage can significantly improve results.
  - Separate guidance from automation. Use markdown to explain intent and best practices, and scripts for repeatable actions. Keeping these concerns distinct makes skills easier to maintain and reuse
  - Always create the REFERENCES.md before any other references files
  - Prefer storing code snippets in the scripts/ folder and referencing them from SKILL.md to keep documentation concise and maintainable.

- You can search docs in https://context7.com/
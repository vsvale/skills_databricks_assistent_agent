# Workspace Assistant Instructions References

This file contains authoritative references and resources for creating and maintaining Databricks Assistant Instructions.

## Official Documentation

- [Extend the Assistant with agent skills](https://docs.databricks.com/aws/en/assistant/skills)
  - **Relevance**: Explains the distinction between global Instructions and context-specific Skills. Crucial for understanding when to use which tool.
  - **Key Insight**: Skills are only supported in Agent mode and are loaded dynamically, whereas Instructions are global.

- [Databricks Assistant FAQ](https://docs.databricks.com/aws/en/notebooks/databricks-assistant-faq)
  - **Relevance**: details the different modes (Chat, Edit, Agent) and the scope of the Assistant's capabilities.
  - **Key Insight**: Assistant does not consider instructions for Quick Fix and Autocomplete.

## Blog Posts & Best Practices

- [Introducing Databricks Assistant Data Science Agent](https://www.databricks.com/blog/introducing-databricks-assistant-data-science-agent)
  - **Relevance**: Introduces the Data Science Agent and the "Planner" capability.
  - **Key Insight**: The Agent uses Unity Catalog metadata (comments, lineage) to understand data. Instructions should encourage users to maintain this metadata.

- [Measure Databricks Assistant impact](https://docs.databricks.com/aws/en/databricks-ai/databricks-assistant-impact)
  - **Relevance**: Methodologies for tracking adoption and user satisfaction.
  - **Key Insight**: Use feedback loops (surveys) to identify which instruction categories need improvement.

- [Customize and improve Databricks Assistant responses](https://docs.databricks.com/aws/en/notebooks/assistant-tips)
  - **Relevance**: Core guide for writing effective instructions.
  - **Key Insight**: Workspace instructions prioritize over User instructions. Character limit is 20,000.

- [Connect Databricks Assistant to MCP servers](https://docs.databricks.com/aws/en/assistant/mcp)
  - **Relevance**: Explains how to connect external tools (Confluence, APIs) via Model Context Protocol.
  - **Key Insight**: Don't stuff external context into instructions; use MCP. Instructions should guide *when* to call MCP tools.

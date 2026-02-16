# Skills Overview

Build your soap formulations faster with AI assistance. `soap-calc` includes a set of "Skills" — specialized instructions for AI agents (like Claude) — that allow them to use the library effectively on your behalf.

<div class="grid cards" markdown>

-   :material-warehouse: **Inventory Management**
    ---
    Track your oils and additives. Ask the agent to "check my inventory" or "add coconut oil".

    [:arrow_right: Inventory Guide](inventory.md)

-   :material-flask: **Formulation Assistant**
    ---
    Get expert formulation advice, recipe generation, and troubleshooting.

    [:arrow_right: Formulation Guide](formulation.md)

</div>

## How It Works

Skills are Markdown files located in the `skills/` directory of the `soap-calc` repository. When you provide these skills to an AI agent, it learns how to:

1.  **Search** your local oil database.
2.  **Validate** recipes against safety rules.
3.  **Calculate** precise lye and water amounts.
4.  **Manage** your personal inventory file.

## getting Started

To use these skills, you typically need to point your AI agent to the `skills/` folder.

*   **Claude Code**: The agent automatically detects skills in the `skills/` directory if configured.
*   **Other Agents**: You may need to manually provide the `SKILL.md` files as context.

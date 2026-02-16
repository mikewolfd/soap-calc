# Inventory Management Skill

The **Inventory** skill helps you track your soap-making supplies, including oils, butters, fats, and additives. It cross-references items against the official `soap-calc` databases to ensure accurate SAP values.

## Features

-   **Add Items**: Add oils or additives to your personal inventory.
-   **Remove Items**: Remove items you've used up.
-   **List Inventory**: See what you have on hand.
-   **Clear Inventory**: Reset your inventory list.
-   **Fuzzy Matching**: Understands "coconut oil" vs "fractionated coconut oil" and asks for clarification.

## File Locations

The skill manages an `inventory.md` file. It checks two locations:

1.  **Project Directory**: `./inventory.md` (Priority) - For project-specific supplies.
2.  **User Home**: `~/.soap_calc/inventory.md` - For your global inventory.

If both exist, the skill prioritizes the project-specific file.

## Example Usage

Ask your AI agent natural language questions about your inventory:

> "Check my inventory for olive oil."

> "Add 5 lbs of coconut oil and some lavender essential oil to my inventory."

> "What oils do I have on hand?"

> "Clear my inventory."

## Important Notes

*   **Opt-in**: Other skills (like Formulation) will only use your inventory if you explicitly ask them to (e.g., "make a recipe from my inventory").
*   **Database Sync**: The skill ensures that item names match the `soap-calc` database exactly, preventing calculation errors from mismatched SAP values.

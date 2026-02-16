# Formulation Assistant Skill

The **Soap Formulation** skill turns your AI agent into an expert soap maker. It can generate recipes, troubleshoot issues, and provide detailed chemical explanations.

## Features

-   **Recipe Generation**: Create complete recipes for Cold Process (CP), Hot Process (HP), and Liquid Soap (KOH).
-   **Troubleshooting**: Diagnose issues like DOS (Dreaded Orange Spots), soft bars, or acceleration.
-   **Substitution**: Suggest oil substitutes based on fatty acid profiles.
-   **Validation**: Check existing recipes for safety and quality issues.
-   **Calculation**: Precisely calculate lye and water amounts using `soap-calc`'s verified database.

## Workflow

When you ask for a recipe, the agent follows this standard workflow:

1.  **Consult Reference**: Checks expert formulation guidelines for the requested soap type (e.g., "gentle baby soap").
2.  **Validate Inputs**: Checks your requested oils against the database.
3.  **Calculate**: Uses `soap-calc` to determine exact lye and water weights.
4.  **Export**: Generates a detailed Markdown recipe sheet.

## Example Usage

### Creating Recipes

> "Make me a gentle, palm-free bastille soap recipe with lavender."

> "Formulate a shaving soap recipe with high stable lather."

### Troubleshooting

> "Why is my soap batch soft and sticky after 4 weeks?"

> "What can I substitute for palm oil in this recipe?"

### Using Inventory

> "Make a balanced bar soap recipe using only the oils in my inventory."

## Safety First

The skill prioritizes safety:
*   It will **never** guess lye amounts. It always uses the `soap-calc` engine.
*   It warns about lye safety safeguards (gloves, goggles).
*   It flags unsafe recipes (e.g., lye-heavy or dangerously high cleansing) during validation.

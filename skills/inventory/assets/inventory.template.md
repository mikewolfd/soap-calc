---
description: >
  Soap-making inventory template. The Inventory Management skill creates and manages this file.

locations:
  - path: "~/.soap_calc/inventory.md"
    type: "User Default"
    description: "Your global inventory (accessible from any project)"
  - path: "./inventory.md"
    type: "Project-Specific"
    description: "Local inventory (only for current directory)"

usage: >
  The Inventory skill uses a hybrid approach with priority:
  1. Check ./inventory.md (current directory) first
  2. Fall back to ~/.soap_calc/inventory.md (user default)

  When creating a new inventory, the skill will ask where to save it.

important: >
  The Inventory skill only uses this file when you EXPLICITLY ask to formulate
  from your inventory (e.g., "use my inventory", "make a recipe from what I have").
  Otherwise, recipes are formulated from the full database.

managed_by: "Inventory Management skill (skills/inventory/SKILL.md)"
---

# Soap Making Inventory

> Last updated: *(not yet populated)*

## Oils

| Oil | SAP (NaOH) | SAP (KOH) | Iodine | INS |
|-----|------------|------------|--------|-----|
| *(none)* |  |  |  |  |

## Additives

| Additive | Category | Usage | Stage | Purpose |
|----------|----------|-------|-------|---------|
| *(none)* |  |  |  |  |

## Unverified Items

*(none)*

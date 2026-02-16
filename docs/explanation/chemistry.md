# The Chemistry of Saponification

## The Chemical Reaction

Soap is the salt of a fatty acid. It is created by a chemical reaction called **Saponification**:

$$ \text{Triglyceride} + \text{Strong Alkali} \rightarrow \text{Soap} + \text{Glycerin} $$

*   **Triglyceride**: Your oils/fats.
*   **Alkali**: Sodium Hydroxide (NaOH) or Potassium Hydroxide (KOH).
*   **Soap**: The cleaning agent.
*   **Glycerin**: A natural humectant byproduct that stays in handmade soap.

## Saponification Values (SAP)

Every oil requires a specific amount of lye to turn into soap. This is its **SAP Value**.

*   **Coconut Oil** has a high SAP (~0.183 NaOH), meaning it needs *more* lye to saponify.
*   **Olive Oil** has a lower SAP (~0.135 NaOH), meaning it needs *less* lye.

$$ \text{Lye Needed} = \text{Oil Weight} \times \text{SAP Value} $$

`soap-calc` stores these values for hundreds of oils to ensure safe conversion.

## Lye Purity

Commercial lye is rarely 100% pure.
*   **NaOH** is typically ~97-99% pure.
*   **KOH** is typically ~90% pure (impurities include water and potassium carbonate).

`soap-calc` assumes standard purities (NaOH 100% theoretical, KOH 90% adjusted) unless configured otherwise. *Note: Check specific `soap-calc` settings for exact purity defaults.*

## Water Ratios

Water dissolves the lye to allow it to react with the oil. It evaporates as the soap cures.

*   **Water:Lye Ratio**: Parts of water per part of lye.
    *   **3:1** (High water): Slow trace, long cure, good for swirls.
    *   **2:1** (Medium): Balanced.
    *   **1.5:1** (Low water / Water Discount): Fast trace, fast cure, can be tricky.

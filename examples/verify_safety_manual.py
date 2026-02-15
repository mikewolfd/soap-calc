from soap_calc import Recipe, Additive, calculate, OilEntry
from soap_calc.oils import OLIVE_OIL

def verify_safety():
    print("--- Safety Verification Script ---")
    
    # 1. Base Recipe (100g Olive Oil, 0% Superfat)
    # SAP NaOH for Olive Oil is approx 0.135 -> 13.5g NaOH
    r = Recipe(
        name="Safety Test",
        oils=[OilEntry(oil=OLIVE_OIL, percentage=100.0)],
        total_oil_weight=100.0,
        superfat_pct=0.0
    )
    res_base = calculate(r)
    print(f"Base Lye (No Additives): {res_base.lye.naoh_amount}g NaOH")
    
    # 2. Add Citric Acid (10g)
    # Citric Acid consumes ~0.624g NaOH per g.
    # Expected extra lye: 10 * 0.624 = 6.24g
    # Total Expected: 13.5 + 6.24 = 19.74g
    r.additives = [Additive(name="Citric Acid", amount=10.0)]
    res_with_acid = calculate(r)
    
    print(f"Lye with 10g Citric Acid: {res_with_acid.lye.naoh_amount}g NaOH")
    
    diff = res_with_acid.lye.naoh_amount - res_base.lye.naoh_amount
    print(f"Difference (Extra lye): {diff:.2f}g")
    
    additive_result = res_with_acid.additives[0]
    print(f"Additive Result 'lye_consumed': {additive_result.lye_consumed}g")
    
    if abs(diff - 6.24) < 0.1:
        print("SUCCESS: Lye adjustment is correct.")
    else:
        print("FAILURE: Lye adjustment is incorrect.")

    # 3. Stearic Acid Warning
    from soap_calc.validation import validate
    r.additives = [Additive(name="Stearic Acid", amount=10.0)]
    warnings = validate(r)
    print("\n--- Stearic Acid Warning Check ---")
    for w in warnings:
        print(f"Warning: {w}")
    
    if any("Stearic Acid" in w for w in warnings):
        print("SUCCESS: Stearic Acid usage flagged.")
    else:
         print("FAILURE: Stearic Acid usage NOT flagged.")

if __name__ == "__main__":
    verify_safety()

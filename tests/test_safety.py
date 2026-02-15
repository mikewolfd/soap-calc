import pytest
from soap_calc import (
    Recipe, OilEntry, Oil, Additive, LyeType, calculate
)
from soap_calc.validation import validate

def _basic_recipe(olive, **kwargs):
    return Recipe(
        name="Safety Test",
        oils=[OilEntry(oil=olive, percentage=100.0)],
        total_oil_weight=500.0,
        **kwargs
    )

class TestSafety:
    def test_citric_acid_consumes_lye(self, olive_oil):
        # 500g Olive Oil. SAP NaOH = 0.135 -> 67.5g NaOH (0% superfat)
        # Add 10g Citric Acid. Lye adjustment = 0.624 -> 6.24g extra NaOH.
        # Total NaOH should be 67.5 + 6.24 = 73.74g
        r = _basic_recipe(olive_oil, superfat_pct=0.0)
        r.additives = [Additive(name="Citric Acid", amount=10.0)]
        
        res = calculate(r, run_validation=False)
        
        # Base Lye
        expected_base = 500 * 0.135
        # Additive Lye
        expected_extra = 10.0 * 0.624
        
        assert abs(res.lye.naoh_amount - (expected_base + expected_extra)) < 0.1
        assert res.additives[0].lye_consumed > 6.0

    def test_citric_acid_koh_conversion(self, olive_oil):
        # KOH recipe.
        # 500g Olive. SAP KOH = 0.190 -> 95g KOH (pure). Purity 90% -> 105.55g
        # Add 10g Citric Acid. 6.24g NaOH equivalent.
        # Convert to KOH: 6.24 * 1.40275 = 8.75g KOH.
        r = _basic_recipe(olive_oil, superfat_pct=0.0, lye_type=LyeType.KOH)
        r.additives = [Additive(name="Citric Acid", amount=10.0)]
        
        res = calculate(r, run_validation=False)
        
        base_koh = (500 * 0.190) / 0.90
        extra_koh = (10.0 * 0.624) * 1.40275
        
        assert abs(res.lye.koh_amount - (base_koh + extra_koh)) < 0.2

    def test_stearic_acid_warning(self, olive_oil):
        r = _basic_recipe(olive_oil)
        r.additives = [Additive(name="Stearic Acid", amount=10.0)]
        
        warnings = validate(r)
        assert any("Stearic Acid should be entered as an Oil" in w for w in warnings)

    def test_zero_purity_warning(self, olive_oil):
        r = _basic_recipe(olive_oil, naoh_purity=0.0)
        warnings = validate(r)
        assert any("purity must be greater than 0%" in w for w in warnings)

    def test_negative_superfat_validation(self, olive_oil):
        r = _basic_recipe(olive_oil, superfat_pct=-5.0)
        warnings = validate(r)
        assert any("negative" in w.lower() for w in warnings)

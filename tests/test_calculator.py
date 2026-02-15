"""Tests for the core calculator engine."""

import pytest

from soap_calc import (
    Oil,
    OilEntry,
    Recipe,
    LyeType,
    FattyAcidProfile,
    calculate,
    WaterCalculationMode,
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _basic_recipe(olive, coconut, shea, **overrides) -> Recipe:
    """Create a simple 3-oil recipe with sensible defaults.

    Oils: 62.5% olive, 25% coconut, 12.5% shea (same as beginner example).
    Default oil weight: 800 g.
    """
    kwargs = dict(
        name="Test Recipe",
        oils=[
            OilEntry(oil=olive, percentage=62.5),
            OilEntry(oil=coconut, percentage=25.0),
            OilEntry(oil=shea, percentage=12.5),
        ],
        lye_type=LyeType.NAOH,
        superfat_pct=5.0,
        water_mode=WaterCalculationMode.WATER_LYE_RATIO,
        water_value=2.0,
        total_oil_weight=800.0,
    )
    kwargs.update(overrides)
    return Recipe(**kwargs)


# ---------------------------------------------------------------------------
# Lye calculation
# ---------------------------------------------------------------------------

class TestLyeCalculation:
    def test_naoh_basic(self, olive_oil, coconut_oil_76, shea_butter):
        recipe = _basic_recipe(olive_oil, coconut_oil_76, shea_butter)
        result = calculate(recipe, run_validation=False)
        # 800g oils: olive 500g, coconut 200g, shea 100g
        # (500*0.135 + 200*0.183 + 100*0.128) * 0.95
        expected_naoh = (500 * 0.135 + 200 * 0.183 + 100 * 0.128) * 0.95
        assert abs(result.lye.naoh_amount - round(expected_naoh, 2)) < 0.055
        assert result.lye.koh_amount == 0.0

    def test_koh_basic(self, olive_oil, coconut_oil_76, shea_butter):
        recipe = _basic_recipe(olive_oil, coconut_oil_76, shea_butter, lye_type=LyeType.KOH)
        result = calculate(recipe, run_validation=False)
        # Default KOH purity is 90%, so divide by 0.9
        expected_koh = ((500 * 0.190 + 200 * 0.257 + 100 * 0.179) * 0.95) / 0.90
        assert abs(result.lye.koh_amount - round(expected_koh, 2)) < 0.055
        assert result.lye.naoh_amount == 0.0

    def test_dual_lye(self, olive_oil, coconut_oil_76, shea_butter):
        recipe = _basic_recipe(olive_oil, coconut_oil_76, shea_butter, lye_type=LyeType.DUAL, naoh_ratio=50.0)
        result = calculate(recipe, run_validation=False)
        assert result.lye.naoh_amount > 0
        assert result.lye.koh_amount > 0

    def test_superfat_zero(self, olive_oil, coconut_oil_76, shea_butter):
        recipe = _basic_recipe(olive_oil, coconut_oil_76, shea_butter, superfat_pct=0.0)
        result = calculate(recipe, run_validation=False)
        expected = 500 * 0.135 + 200 * 0.183 + 100 * 0.128
        assert abs(result.lye.naoh_amount - round(expected, 2)) < 0.055

    def test_superfat_high(self, olive_oil, coconut_oil_76, shea_butter):
        recipe = _basic_recipe(olive_oil, coconut_oil_76, shea_butter, superfat_pct=20.0)
        result = calculate(recipe, run_validation=False)
        expected = (500 * 0.135 + 200 * 0.183 + 100 * 0.128) * 0.80
        assert abs(result.lye.naoh_amount - round(expected, 2)) < 0.055

    def test_oil_weight_override(self, olive_oil, coconut_oil_76, shea_butter):
        """Passing oil_weight to calculate() overrides default."""
        recipe = _basic_recipe(olive_oil, coconut_oil_76, shea_butter, total_oil_weight=800.0)
        result_default = calculate(recipe, run_validation=False)
        result_override = calculate(recipe, oil_weight=400.0, run_validation=False)
        # Half the oil → half the lye
        assert abs(result_override.lye.naoh_amount - result_default.lye.naoh_amount / 2) < 0.1


# ---------------------------------------------------------------------------
# Liquid calculation
# ---------------------------------------------------------------------------

class TestLiquidCalculation:
    def test_water_lye_ratio(self, olive_oil, coconut_oil_76, shea_butter):
        recipe = _basic_recipe(
            olive_oil, coconut_oil_76, shea_butter,
            water_mode=WaterCalculationMode.WATER_LYE_RATIO,
            water_value=2.0
        )
        result = calculate(recipe, run_validation=False)
        expected_liquid = result.lye.naoh_amount * 2.0
        assert abs(result.total_liquid - expected_liquid) < 0.02

    def test_lye_concentration(self, olive_oil, coconut_oil_76, shea_butter):
        # 33.33% lye concentration => water:lye is 2:1
        recipe = _basic_recipe(
            olive_oil, coconut_oil_76, shea_butter,
            water_mode=WaterCalculationMode.LYE_CONCENTRATION,
            water_value=33.33333333
        )
        result = calculate(recipe, run_validation=False)
        expected_liquid = result.lye.naoh_amount * 2.0
        assert abs(result.total_liquid - expected_liquid) < 0.1

    def test_water_percent_of_oils(self, olive_oil, coconut_oil_76, shea_butter):
        recipe = _basic_recipe(
            olive_oil, coconut_oil_76, shea_butter,
            water_mode=WaterCalculationMode.WATER_PERCENT_OF_OILS,
            water_value=38.0,
            total_oil_weight=1000.0
        )
        result = calculate(recipe, run_validation=False)
        assert abs(result.total_liquid - 380.0) < 0.02

    def test_liquid_discount(self, olive_oil, coconut_oil_76, shea_butter):
        recipe = _basic_recipe(
            olive_oil, coconut_oil_76, shea_butter,
            water_mode=WaterCalculationMode.WATER_LYE_RATIO,
            water_value=2.0,
            liquid_discount_pct=10.0
        )
        result = calculate(recipe, run_validation=False)
        base = result.lye.naoh_amount * 2.0
        expected = base * 0.90
        assert abs(result.total_liquid - round(expected, 2)) < 0.02


# ---------------------------------------------------------------------------
# Validation filtering
# ---------------------------------------------------------------------------

class TestValidationFiltering:
    def test_ignore_warnings(self, olive_oil, coconut_oil_76, shea_butter):
        # Create a recipe that triggers warnings
        r = _basic_recipe(
            olive_oil, coconut_oil_76, shea_butter,
            oils=[OilEntry(oil=coconut_oil_76, percentage=100.0)],
            superfat_pct=0.0  # triggers "Superfat is 0 %" + drying warning
        )
        # Without ignore
        res1 = calculate(r)
        assert any("Superfat is 0 %" in w for w in res1.warnings)
        
        # With ignore
        r.ignore_warnings = ["Superfat is 0 %"]
        res2 = calculate(r)
        assert not any("Superfat is 0 %" in w for w in res2.warnings)
        # Other warnings (like drying) should still be there
        assert any("drying" in w.lower() for w in res2.warnings)


# ---------------------------------------------------------------------------
# Total batch weight
# ---------------------------------------------------------------------------

class TestBatchWeight:
    def test_total_includes_everything(self, olive_oil, coconut_oil_76, shea_butter):
        recipe = _basic_recipe(olive_oil, coconut_oil_76, shea_butter)
        result = calculate(recipe, run_validation=False)
        expected = 800 + result.lye.naoh_amount + result.total_liquid
        assert abs(result.total_batch_weight - expected) < 0.1


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

class TestProperties:
    def test_properties_populated(self, olive_oil, coconut_oil_76, shea_butter):
        recipe = _basic_recipe(olive_oil, coconut_oil_76, shea_butter)
        result = calculate(recipe, run_validation=False)
        assert result.properties.hardness.value > 0
        assert result.properties.cleansing.value > 0
        assert result.properties.conditioning.value > 0

    def test_fatty_acid_profile(self, olive_oil, coconut_oil_76, shea_butter):
        recipe = _basic_recipe(olive_oil, coconut_oil_76, shea_butter)
        result = calculate(recipe, run_validation=False)
        fa = result.fatty_acid_profile
        assert fa.oleic > 30  # olive-heavy
        assert fa.lauric > 5  # coconut contribution


# ---------------------------------------------------------------------------
# Superfat Oils (Post-Cook)
# ---------------------------------------------------------------------------

class TestSuperfatOils:
    def test_superfat_oils_split_mode(self, olive_oil, coconut_oil_76, shea_butter):
        """Test that superfat oils splitting total batch weight correctly."""
        # 1000g Total Oil. 10% Superfat.
        # Expect: 900g Base, 100g Superfat.
        r = _basic_recipe(olive_oil, coconut_oil_76, shea_butter, total_oil_weight=1000.0, superfat_pct=10.0)
        
        # Base: Olive 100%
        # Superfat: Shea 100%
        r.oils = [OilEntry(oil=olive_oil, percentage=100.0)]
        r.superfat_oils = [OilEntry(oil=shea_butter, percentage=100.0)]
        
        result = calculate(r, run_validation=False)
        
        # Total Saponified Oil (Base Phase)
        assert result.total_oil_weight == 900.0
        
        # Superfat Phase
        assert len(result.superfat_oils) == 1
        assert result.superfat_oils[0].amount == 100.0
        assert result.superfat_oils[0].name == "Shea Butter"
        
        # Check Total Batch logic
        # 900g Base + 100g SF = 1000g Total Oils.
        # Plus Lye/Water etc.
        # Lye should be calculated for 900g Olive with 0% discount.
        # SAP NaOH Olive = 0.135.
        # Lye = 900 * 0.135 = 121.5 g.
        assert abs(result.lye.naoh_amount - 121.5) < 0.1

    def test_effective_superfat_matches_target(self, olive_oil, coconut_oil_76, shea_butter):
        """Effective superfat should ideally match the target in split mode."""
        r = _basic_recipe(olive_oil, coconut_oil_76, shea_butter, superfat_pct=5.0, total_oil_weight=100.0)
        r.superfat_oils = [OilEntry(oil=shea_butter, percentage=100.0)]
        
        result = calculate(r, run_validation=False)
        
        assert result.effective_superfat_pct == 5.0
        # 95g Base, 5g SF.
        # Lye for 95g Base (0% dsc).
        # Unreacted = 5g (Pure SF).
        # Total Oil = 100g.
        # 5/100 = 5%.


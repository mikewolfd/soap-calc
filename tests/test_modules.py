"""Tests for recipe I/O, scaling, validation, oils, fragrance, mold, and export."""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from soap_calc import (
    Oil,
    OilEntry,
    Recipe,
    LyeType,
    Liquid,
    Additive,
    Fragrance,
    FragranceType,
    MoldSpec,
    PercentBase,
    Stage,
    WaterCalculationMode,
    calculate,
    list_oils,
    get_oil,
    search_oils,
    load_recipe,
    save_recipe,
    scale_recipe,
    mold_from_inches,
    batch_weight_for_mold,
    oil_weight_for_mold,
    get_additive,
    list_additives,
    search_additives,
)
from soap_calc.fragrance import calculate_fragrance, get_eo_max_rate
from soap_calc.validation import validate
from soap_calc.export import render_markdown


# ---------------------------------------------------------------------------
# Oil database
# ---------------------------------------------------------------------------

class TestOilDatabase:
    def test_list_oils_non_empty(self):
        oils = list_oils()
        assert len(oils) >= 30

    def test_get_oil_case_insensitive(self):
        oil = get_oil("olive oil")
        assert oil is not None
        assert oil.name == "Olive Oil"

    def test_get_oil_not_found(self):
        assert get_oil("unicorn oil") is None

    def test_search_oils(self):
        results = search_oils("coconut")
        assert len(results) >= 2

    def test_all_oils_have_sap(self):
        for oil in list_oils():
            assert oil.sap_naoh > 0, f"{oil.name} has no NaOH SAP value"
            assert oil.sap_koh > 0, f"{oil.name} has no KOH SAP value"


# ---------------------------------------------------------------------------
# Recipe I/O
# ---------------------------------------------------------------------------

class TestRecipeIO:
    def _sample_recipe(self, olive, coconut):
        return Recipe(
            name="Test Save",
            oils=[
                OilEntry(oil=olive, percentage=70.0),
                OilEntry(oil=coconut, percentage=30.0),
            ],
            lye_type=LyeType.NAOH,
            superfat_pct=5.0,
            total_oil_weight=500.0,
        )

    def test_json_roundtrip(self, tmp_path, olive_oil, coconut_oil_76):
        r = self._sample_recipe(olive_oil, coconut_oil_76)
        path = tmp_path / "recipe.json"
        save_recipe(r, path)
        loaded = load_recipe(path)
        assert loaded.name == r.name
        assert len(loaded.oils) == 2
        assert loaded.oils[0].oil.name == "Olive Oil"
        assert loaded.oils[0].percentage == 70.0
        assert loaded.total_oil_weight == 500.0

    def test_yaml_roundtrip(self, tmp_path, olive_oil, coconut_oil_76):
        r = self._sample_recipe(olive_oil, coconut_oil_76)
        path = tmp_path / "recipe.yaml"
        save_recipe(r, path)
        loaded = load_recipe(path)
        assert loaded.name == r.name
        assert loaded.oils[1].percentage == 30.0

    def test_mold_roundtrip(self, tmp_path, olive_oil, coconut_oil_76):
        r = self._sample_recipe(olive_oil, coconut_oil_76)
        r.mold = MoldSpec(length=25, width=8, height=7)
        path = tmp_path / "recipe.json"
        save_recipe(r, path)
        loaded = load_recipe(path)
        assert loaded.mold is not None
        assert loaded.mold.length == 25

    def test_ignore_warnings_io(self, tmp_path, olive_oil, coconut_oil_76):
        r = self._sample_recipe(olive_oil, coconut_oil_76)
        r.ignore_warnings = ["foo", "bar"]
        path = tmp_path / "ignores.json"
        save_recipe(r, path)
        loaded = load_recipe(path)
        assert loaded.ignore_warnings == ["foo", "bar"]

    def test_superfat_oils_io(self, tmp_path, olive_oil, coconut_oil_76, shea_butter):
        r = self._sample_recipe(olive_oil, coconut_oil_76)
        r.superfat_oils = [OilEntry(oil=shea_butter, percentage=5.0)]
        path = tmp_path / "sf_oils.json"
        save_recipe(r, path)
        loaded = load_recipe(path)
        assert len(loaded.superfat_oils) == 1
        assert loaded.superfat_oils[0].oil.name == "Shea Butter"
        assert loaded.superfat_oils[0].percentage == 5.0


# ---------------------------------------------------------------------------
# Scaling
# ---------------------------------------------------------------------------

class TestScaling:
    def test_scale_changes_oil_weight(self, olive_oil, coconut_oil_76):
        r = Recipe(
            name="Scale Test",
            oils=[
                OilEntry(oil=olive_oil, percentage=60.0),
                OilEntry(oil=coconut_oil_76, percentage=40.0),
            ],
            total_oil_weight=800.0,
        )
        scaled = scale_recipe(r, 400.0)
        assert scaled.total_oil_weight == 400.0
        # Percentages are unchanged
        assert scaled.oils[0].percentage == 60.0
        assert scaled.oils[1].percentage == 40.0

    def test_scale_absolute_additive(self, olive_oil):
        r = Recipe(
            name="Scale Test",
            oils=[OilEntry(oil=olive_oil, percentage=100.0)],
            total_oil_weight=1000.0,
            additives=[Additive(name="Sugar", amount=20.0)],
        )
        scaled = scale_recipe(r, 500.0)
        # Absolute amount should be halved
        assert scaled.additives[0].amount == 10.0


# ---------------------------------------------------------------------------
# Resolve oil weight priority
# ---------------------------------------------------------------------------

class TestResolveOilWeight:
    def test_default(self):
        r = Recipe(oils=[], total_oil_weight=800.0)
        assert r.resolve_oil_weight() == 800.0

    def test_mold_overrides_default(self):
        r = Recipe(
            oils=[],
            total_oil_weight=800.0,
            mold=MoldSpec(length=25, width=8, height=7),
        )
        weight = r.resolve_oil_weight()
        assert weight != 800.0  # should come from mold
        assert weight > 0

    def test_override_beats_mold(self):
        r = Recipe(
            oils=[],
            total_oil_weight=800.0,
            mold=MoldSpec(length=25, width=8, height=7),
        )
        assert r.resolve_oil_weight(override=1234.0) == 1234.0


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestValidation:
    def test_no_oils_warning(self):
        r = Recipe(name="Empty")
        warnings = validate(r)
        assert any("no oils" in w.lower() for w in warnings)

    def test_high_superfat_warning(self, olive_oil):
        r = Recipe(
            name="High SF",
            oils=[OilEntry(oil=olive_oil, percentage=100.0)],
            superfat_pct=25.0,
        )
        warnings = validate(r)
        assert any("superfat" in w.lower() for w in warnings)

    def test_high_coconut_warning(self, olive_oil, coconut_oil_76):
        r = Recipe(
            name="Coconut Heavy",
            oils=[
                OilEntry(oil=coconut_oil_76, percentage=70.0),
                OilEntry(oil=olive_oil, percentage=30.0),
            ],
            superfat_pct=5.0,
        )
        warnings = validate(r)
        assert any("drying" in w.lower() for w in warnings)

    def test_oil_percentages_not_100(self, olive_oil, coconut_oil_76):
        r = Recipe(
            name="Bad pct",
            oils=[
                OilEntry(oil=olive_oil, percentage=50.0),
                OilEntry(oil=coconut_oil_76, percentage=30.0),
            ],
        )
        warnings = validate(r)
        assert any("80" in w for w in warnings)  # sums to 80%

    def test_water_ratio_warning(self, olive_oil):
        """Test warning for unsafe water:lye ratio."""
        r = Recipe(
            oils=[OilEntry(oil=olive_oil, percentage=100.0)],
            water_mode=WaterCalculationMode.WATER_LYE_RATIO,
            water_value=0.5  # unsafe
        )
        warnings = validate(r)
        assert any("dangerously low" in w for w in warnings)

    def test_high_superfat_warning_split_mode(self, olive_oil):
        r = Recipe(
            oils=[OilEntry(oil=olive_oil, percentage=100.0)],
            superfat_pct=25.0,
            # To test split logic warning, we can add SF oils, or just rely on standard mode warning
            # The warning logic for >20% is shared.
        )
        warnings = validate(r)
        assert any("unusually high" in w for w in warnings)

    def test_superfat_oils_sum_warning(self, olive_oil, shea_butter):
        """Test that superfat oils must sum to 100%."""
        r = Recipe(
            oils=[OilEntry(oil=olive_oil, percentage=100.0)],
            superfat_oils=[OilEntry(oil=shea_butter, percentage=50.0)], # Only 50%
            superfat_pct=5.0
        )
        warnings = validate(r)
        assert any("should be 100%" in w for w in warnings)


# ---------------------------------------------------------------------------
# Fragrance
# ---------------------------------------------------------------------------

class TestFragrance:
    def test_fo_default_rate(self):
        frag = Fragrance(name="Vanilla", fragrance_type=FragranceType.FRAGRANCE_OIL)
        result = calculate_fragrance(frag, 1000)
        assert abs(result.amount - 50.0) < 0.1

    def test_eo_safety_warning(self):
        frag = Fragrance(
            name="Clove Bud",
            fragrance_type=FragranceType.ESSENTIAL_OIL,
            percentage=3.0,
        )
        result = calculate_fragrance(frag, 1000)
        assert result.warning is not None
        assert "exceeds" in result.warning.lower()

    def test_get_eo_max_rate(self):
        rate = get_eo_max_rate("lavender")
        assert rate == 5.0
        assert get_eo_max_rate("nonexistent") is None


# ---------------------------------------------------------------------------
# Mold calculator
# ---------------------------------------------------------------------------

class TestMold:
    def test_batch_weight(self):
        mold = MoldSpec(length=25, width=8, height=7)
        weight = batch_weight_for_mold(mold)
        assert 1300 < weight < 1500

    def test_from_inches(self):
        mold = mold_from_inches(10, 3.5, 3)
        assert mold.length > 20

    def test_mold_spec_in_recipe(self, olive_oil):
        """MoldSpec embedded in recipe drives oil weight."""
        r = Recipe(
            oils=[OilEntry(oil=olive_oil, percentage=100.0)],
            mold=MoldSpec(length=25, width=8, height=7),
        )
        result = calculate(r, run_validation=False)
        # oil weight should come from mold, not default
        assert result.total_oil_weight != 800.0
        assert result.total_oil_weight > 0


# ---------------------------------------------------------------------------
# Markdown export
# ---------------------------------------------------------------------------

class TestExport:
    def test_render_markdown(self, olive_oil, coconut_oil_76):
        r = Recipe(
            name="Export Test",
            oils=[
                OilEntry(oil=olive_oil, percentage=70.0),
                OilEntry(oil=coconut_oil_76, percentage=30.0),
            ],
            total_oil_weight=500.0,
        )
        result = calculate(r)
        md = render_markdown(r, result)
        assert "# 🧼 Export Test" in md
        assert "Olive Oil" in md
        assert "70.0 %" in md
        assert "Step 1:" in md
        assert "Instructions" in md


# ---------------------------------------------------------------------------
# End-to-end: load example recipe
# ---------------------------------------------------------------------------

class TestEndToEnd:
    def test_load_and_calculate_example(self):
        example = Path(__file__).parent.parent / "examples" / "beginner_3oil.json"
        if not example.exists():
            pytest.skip("Example recipe not found")
        recipe = load_recipe(example)
        assert recipe.oils[0].percentage == 62.5
        assert recipe.total_oil_weight == 800
        # Check new water fields are loaded
        assert recipe.water_value == 2.0
        
        result = calculate(recipe)
        assert result.lye.naoh_amount > 0
        assert result.total_oil_weight == 800
        assert result.total_batch_weight > 0
        assert result.properties.hardness.value > 0
        assert len(result.fragrances) == 1
        assert len(result.additives) == 2

    def test_calculate_with_override(self):
        example = Path(__file__).parent.parent / "examples" / "beginner_3oil.json"
        if not example.exists():
            pytest.skip("Example recipe not found")
        recipe = load_recipe(example)
        result = calculate(recipe, oil_weight=400.0)
        assert result.total_oil_weight == 400.0

    def test_example_export(self):
        example = Path(__file__).parent.parent / "examples" / "beginner_3oil.json"
        if not example.exists():
            pytest.skip("Example recipe not found")
        recipe = load_recipe(example)
        result = calculate(recipe)
        md = render_markdown(recipe, result)
        
        # Check additives
        assert "Kaolin Clay" in md
        assert "Sodium Lactate" in md
        # Check fragrance
        assert "Lavender" in md
        # Check properties table exist
        assert "| Hardness |" in md

# ---------------------------------------------------------------------------
# Additive database
# ---------------------------------------------------------------------------

class TestAdditiveDatabase:
    def test_list_additives_non_empty(self):
        adds = list_additives()
        assert len(adds) >= 10

    def test_get_additive_case_insensitive(self):
        a = get_additive("sugar")
        assert a is not None
        assert a.name == "Sugar"
        assert a.usage.unit in ["tsp", "tbsp", "pct", "pinch"]

    def test_get_additive_not_found(self):
        assert get_additive("unicorn dust") is None

    def test_search_additives(self):
        results = search_additives("clay")
        assert len(results) >= 2
        names = [a.name for a in results]
        assert "Green Clay" in names
        assert "Kaolin Clay" in names

    def test_stage_parsing(self):
        a = get_additive("sugar")
        # Sugar stage is "lye" in JSON -> Stage.LYE_LIQUID
        assert a.stage == Stage.LYE_LIQUID.value



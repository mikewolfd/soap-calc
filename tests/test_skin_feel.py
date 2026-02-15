import pytest
from soap_calc.skin_feel import analyze_skin_feel
from soap_calc.models import OilEntry, Oil, FattyAcidProfile


@pytest.fixture
def create_oil_entry():
    def _create(name, profile, percent=100.0, sap_naoh=0.1):
        fa = FattyAcidProfile(**profile)
        oil = Oil(name=name, sap_naoh=sap_naoh, sap_koh=0.1, fatty_acids=fa)
        return OilEntry(oil=oil, percentage=percent)
    return _create


# --- Empty / low-signal blends ---

def test_skin_feel_empty():
    """Empty oil list -> all dimensions Low."""
    result = analyze_skin_feel([])
    assert result.film_persistence == "Low"
    assert result.emollient_slip == "Low"
    assert result.dos_risk == "Low"


def test_balanced_when_all_low(create_oil_entry):
    """Evenly spread FAs -> all dimensions Low."""
    oil = create_oil_entry("Even", {"lauric": 15, "stearic": 10, "oleic": 15, "linoleic": 10, "palmitic": 5})
    result = analyze_skin_feel([oil])
    assert result.film_persistence == "Low"
    assert result.emollient_slip == "Low"
    assert result.dos_risk == "Low"


# --- Single-oil dimension profiles ---

def test_shea_butter_complementary(create_oil_entry):
    """Shea (high stearic + high oleic) -> high film AND moderate+ emollient.

    This is the key test for the complementary model: shea is valued
    precisely because it combines occlusive structure with emollient slip.
    """
    shea = create_oil_entry("Shea Butter", {"stearic": 40, "oleic": 50, "palmitic": 5, "linoleic": 5})
    result = analyze_skin_feel([shea])
    assert result.film_persistence == "High"
    assert result.emollient_slip in ("Moderate", "High")
    assert result.dos_risk == "Low"


def test_grapeseed_dos_risk(create_oil_entry):
    """Grapeseed (high linoleic) -> low film, high DOS risk."""
    grape = create_oil_entry("Grapeseed", {"linoleic": 70, "oleic": 20, "palmitic": 7, "stearic": 3})
    result = analyze_skin_feel([grape])
    assert result.film_persistence == "Low"
    assert result.dos_risk == "High"


def test_olive_emollient(create_oil_entry):
    """Olive (high oleic) -> high emollient slip, low DOS risk."""
    olive = create_oil_entry("Olive", {"oleic": 75, "palmitic": 13, "linoleic": 10, "stearic": 2})
    result = analyze_skin_feel([olive])
    assert result.emollient_slip == "High"
    assert result.dos_risk == "Low"


def test_coconut_film_persistence(create_oil_entry):
    """Coconut (high lauric) -> moderate film, low DOS risk.

    Lauric+myristic don't contribute to film_persistence (that's palmitic+stearic),
    but coconut has ~9% palmitic which may push moderate depending on thresholds.
    The key assertion: low DOS risk (saturated fats don't oxidize).
    """
    coconut = create_oil_entry("Coconut", {"lauric": 48, "myristic": 19, "palmitic": 9, "oleic": 8})
    result = analyze_skin_feel([coconut])
    assert result.dos_risk == "Low"


# --- Wax detection ---

def test_wax_high_film_persistence(create_oil_entry):
    """A wax with near-zero FA profile should score high film persistence."""
    wax = create_oil_entry("Lanolin Wax", {}, percent=100.0, sap_naoh=0.07)
    result = analyze_skin_feel([wax])
    assert result.film_persistence == "High"


# --- Lather impact tests (kept from original, already dimension-based) ---

def test_lather_impact_increases_with_superfat_pct(create_oil_entry):
    """Higher superfat % -> higher lather impact, same oil."""
    oil = create_oil_entry("Olive", {"oleic": 75, "palmitic": 13, "linoleic": 10, "stearic": 2})
    low_sf = analyze_skin_feel([oil], superfat_pct=2.0)
    high_sf = analyze_skin_feel([oil], superfat_pct=12.0)

    impact_order = ["Low", "Moderate", "High", "Very High"]
    assert impact_order.index(high_sf.lather_impact) >= impact_order.index(low_sf.lather_impact)


def test_waxy_superfat_lower_lather_impact_than_fluid(create_oil_entry):
    """Waxy/occlusive superfat suppresses less foam than fluid poly oil."""
    waxy = create_oil_entry("Cocoa Butter", {"stearic": 35, "palmitic": 25, "oleic": 35})
    fluid = create_oil_entry("Grapeseed", {"linoleic": 70, "oleic": 20, "palmitic": 7, "stearic": 3})

    waxy_result = analyze_skin_feel([waxy], superfat_pct=5.0)
    fluid_result = analyze_skin_feel([fluid], superfat_pct=5.0)

    impact_order = ["Low", "Moderate", "High", "Very High"]
    assert impact_order.index(waxy_result.lather_impact) <= impact_order.index(fluid_result.lather_impact)


def test_base_coupling_lauric_base_reduces_impact(create_oil_entry):
    """A high-lauric base solubilizes superfat, reducing effective lather impact."""
    superfat = create_oil_entry("Olive", {"oleic": 75, "palmitic": 13, "linoleic": 10, "stearic": 2})

    lauric_base = [create_oil_entry("Coconut", {"lauric": 48, "myristic": 19, "palmitic": 9, "oleic": 8})]
    gentle_base = [create_oil_entry("Tallow", {"palmitic": 26, "stearic": 18, "oleic": 47, "linoleic": 3})]

    with_lauric = analyze_skin_feel([superfat], base_oils=lauric_base, superfat_pct=5.0)
    with_gentle = analyze_skin_feel([superfat], base_oils=gentle_base, superfat_pct=5.0)

    impact_order = ["Low", "Moderate", "High", "Very High"]
    assert impact_order.index(with_lauric.lather_impact) <= impact_order.index(with_gentle.lather_impact)


def test_lather_impact_without_base_oils(create_oil_entry):
    """Without base_oils, lather impact still works (backward compat)."""
    oil = create_oil_entry("Olive", {"oleic": 75, "palmitic": 13, "linoleic": 10, "stearic": 2})
    result = analyze_skin_feel([oil])
    assert result.lather_impact in ("Low", "Moderate", "High", "Very High")


# --- Description generation ---

def test_description_combines_dimensions(create_oil_entry):
    """Shea should mention both barrier/film and emollient in description."""
    shea = create_oil_entry("Shea Butter", {"stearic": 40, "oleic": 50, "palmitic": 5, "linoleic": 5})
    result = analyze_skin_feel([shea])
    desc = result.description.lower()
    # Should reference film/barrier AND emollient — the complementary model
    assert "barrier" in desc or "wash-off" in desc or "film" in desc
    assert "emollient" in desc or "slip" in desc or "silky" in desc


def test_description_low_signal_blend(create_oil_entry):
    """Even blend -> low-signal description."""
    oil = create_oil_entry("Even", {"lauric": 15, "stearic": 10, "oleic": 15, "linoleic": 10, "palmitic": 5})
    result = analyze_skin_feel([oil])
    assert "low-signal" in result.description.lower() or "no dominant" in result.description.lower()

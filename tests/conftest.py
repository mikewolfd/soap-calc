import pytest
from soap_calc.oils import get_oil, FattyAcidProfile, Oil

def _require_oil(name: str) -> Oil:
    oil = get_oil(name)
    if not oil:
        # Fallback for testing/initialization if DB is missing items
        return Oil(name=name, sap_naoh=0.0, sap_koh=0.0, fatty_acids=FattyAcidProfile())
    return oil

@pytest.fixture
def olive_oil():
    return _require_oil("Olive Oil")

@pytest.fixture
def coconut_oil_76():
    return _require_oil("Coconut Oil, 76 deg")

@pytest.fixture
def shea_butter():
    return _require_oil("Shea Butter")

@pytest.fixture
def castor_oil():
    return _require_oil("Castor Oil")

@pytest.fixture
def palm_oil():
    return _require_oil("Palm Oil")

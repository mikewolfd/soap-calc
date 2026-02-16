"""soap_calc — A Python package for calculating soap (saponification) recipes."""

__version__ = "0.2.2"

# Public API ----------------------------------------------------------------
from soap_calc.models import (  # noqa: F401  — re-exported
    Additive,
    AdditiveResult,
    Fragrance,
    FragranceType,
    FattyAcidProfile,
    Liquid,
    LiquidBreakdown,
    LyeResult,
    LyeType,
    MoldSpec,
    Oil,
    OilEntry,
    PercentBase,
    PropertyRating,
    PropertyValue,
    Recipe,
    RecipeResult,
    SoapProperties,
    Stage,
    WaterCalculationMode,
)
from soap_calc.calculator import calculate  # noqa: F401
from soap_calc.oils import get_oil, list_oils, search_oils  # noqa: F401
from soap_calc.additives import get_additive, list_additives, search_additives  # noqa: F401
from soap_calc.recipe_io import (  # noqa: F401
    load_recipe,
    save_recipe,
    scale_recipe,
)
from soap_calc.export import export_markdown, render_markdown  # noqa: F401
from soap_calc.properties import (  # noqa: F401
    blend_fatty_acids,
    predict_properties,
)
from soap_calc.validation import validate  # noqa: F401
from soap_calc.mold import (  # noqa: F401
    batch_weight_for_mold,
    mold_from_inches,
    oil_weight_for_mold,
)

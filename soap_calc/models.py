"""Core data structures and types."""

from __future__ import annotations

import enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class LyeType(enum.Enum):
    NAOH = "NaOH"
    KOH = "KOH"
    DUAL = "Hybrid (Dual Lye)"


class WaterCalculationMode(enum.Enum):
    WATER_LYE_RATIO = "Water:Lye Ratio"
    LYE_CONCENTRATION = "Lye Concentration"
    WATER_PERCENT_OF_OILS = "Water as % of Oils"


class Stage(enum.Enum):
    LYE_LIQUID = "Lye Liquid"
    OIL_PHASE = "Oil Phase"
    LIGHT_TRACE = "Light Trace"
    MEDIUM_TRACE = "Medium Trace"
    HEAVY_TRACE = "Heavy Trace"
    POST_COOK = "Post Cook / After Gel"
    IN_MOLD = "In Mold"


class FragranceType(enum.Enum):
    ESSENTIAL_OIL = "Essential Oil"
    FRAGRANCE_OIL = "Fragrance Oil"


class PercentBase(enum.Enum):
    OIL_WEIGHT = "Oil Weight"
    LIQUID_WEIGHT = "Liquid Weight"
    TOTAL_BATCH = "Total Batch Weight"


# ---------------------------------------------------------------------------
# Ingredients
# ---------------------------------------------------------------------------


class FattyAcidProfile(BaseModel):
    """The fatty acid composition of an oil or blend.

    Attributes:
        lauric: C12:0 — contributes to hardness, cleansing, bubbly lather.
        myristic: C14:0 — contributes to hardness, cleansing, bubbly lather.
        palmitic: C16:0 — contributes to hardness, stable creamy lather.
        stearic: C18:0 — contributes to hardness, stable creamy lather.
        ricinoleic: C18:1-OH — conditioning, bubbly, creamy (castor oil).
        oleic: C18:1 — conditioning.
        linoleic: C18:2 — conditioning.
        linolenic: C18:3 — conditioning.
    """

    lauric: float = 0.0
    myristic: float = 0.0
    palmitic: float = 0.0
    stearic: float = 0.0
    ricinoleic: float = 0.0
    oleic: float = 0.0
    linoleic: float = 0.0
    linolenic: float = 0.0

    def __add__(self, other: "FattyAcidProfile") -> "FattyAcidProfile":
        """Combine two fatty acid profiles by summing each acid.

        Args:
            other: The fatty acid profile to add to this one.

        Returns:
            A new FattyAcidProfile with summed values.
        """
        return FattyAcidProfile(
            lauric=self.lauric + other.lauric,
            myristic=self.myristic + other.myristic,
            palmitic=self.palmitic + other.palmitic,
            stearic=self.stearic + other.stearic,
            ricinoleic=self.ricinoleic + other.ricinoleic,
            oleic=self.oleic + other.oleic,
            linoleic=self.linoleic + other.linoleic,
            linolenic=self.linolenic + other.linolenic,
        )

    def scale(self, factor: float) -> "FattyAcidProfile":
        """Scale all fatty acids by a factor.

        Args:
            factor: Multiplicative factor (e.g., 0.5 for 50%).

        Returns:
            A new FattyAcidProfile with scaled values.
        """
        return FattyAcidProfile(
            lauric=self.lauric * factor,
            myristic=self.myristic * factor,
            palmitic=self.palmitic * factor,
            stearic=self.stearic * factor,
            ricinoleic=self.ricinoleic * factor,
            oleic=self.oleic * factor,
            linoleic=self.linoleic * factor,
            linolenic=self.linolenic * factor,
        )

    @property
    def hard(self) -> float:
        """Hardness factor (lauric + myristic + palmitic + stearic)."""
        return self.lauric + self.myristic + self.palmitic + self.stearic

    @property
    def cleansing(self) -> float:
        """Cleansing factor (lauric + myristic)."""
        return self.lauric + self.myristic

    @property
    def conditioning(self) -> float:
        """Conditioning factor (oleic + linoleic + linolenic + ricinoleic)."""
        return self.oleic + self.linoleic + self.linolenic + self.ricinoleic

    @property
    def bubbly(self) -> float:
        """Bubbly lather factor (lauric + myristic + ricinoleic)."""
        return self.lauric + self.myristic + self.ricinoleic

    @property
    def creamy(self) -> float:
        """Creamy lather factor (palmitic + stearic + ricinoleic)."""
        return self.palmitic + self.stearic + self.ricinoleic

    @property
    def longevity(self) -> float:
        """Longevity factor (palmitic + stearic)."""
        return self.palmitic + self.stearic


class Oil(BaseModel):
    """A saponifiable oil or fat with its SAP values and fatty acid profile.

    Attributes:
        name: Common name of the oil.
        sap_naoh: Grams of NaOH to saponify 1 g of this oil.
        sap_koh: Grams of KOH to saponify 1 g of this oil.
        fatty_acids: Fatty acid composition.
        iodine: Iodine value (measure of unsaturation).
        ins: INS value.
        notes: Optional notes.
    """

    name: str
    sap_naoh: float
    sap_koh: float
    fatty_acids: FattyAcidProfile
    iodine: float = 0.0
    ins: float = 0.0
    notes: str = ""


from typing import Annotated
from pydantic import BaseModel, Field, WithJsonSchema

class OilEntry(BaseModel):
    """An oil entry within a recipe, pairing an oil with its blend percentage.

    Attributes:
        oil: The resolved Oil object.
        percentage: Percentage of this oil in the blend (0-100).
    """

    oil: Annotated[Oil, WithJsonSchema({"type": "string"})]
    percentage: float = Field(..., ge=0, le=100)  # % of total oils


class Liquid(BaseModel):
    """A liquid-phase ingredient (water, milk, tea, etc.).

    Attributes:
        name: Display name of the liquid.
        percentage: Share of the liquid phase (0-100).
        handling_notes: Optional preparation notes (e.g., "freeze first").
    """

    name: str
    percentage: float = 100.0  # % of liquid phase
    handling_notes: str = ""


class AdditiveUsage(BaseModel):
    """Recommended usage range for an additive.

    Attributes:
        min: Minimum recommended amount.
        max: Maximum recommended amount.
        unit: Unit of measurement (e.g., "tsp").
        per: Weight basis for the rate (e.g., "lb_oils").
    """

    min: float
    max: float
    unit: str
    per: str  # "lb_oils", "oil_weight"


from pydantic import BaseModel, Field, field_validator

# ... (imports)

class AdditiveInfo(BaseModel):
    """Database record for an additive with usage and stage info.

    Attributes:
        name: Display name of the additive.
        category: Category (e.g., "Exfoliant", "Colorant").
        usage: Recommended usage range.
        stage: Production stage when the additive is added.
        purpose: Brief description of what the additive does.
        lye_adjustment: Extra lye consumed per unit (e.g., citric acid).
        notes: Optional notes.
    """

    name: str
    category: str
    usage: AdditiveUsage
    stage: str  # raw string from JSON, or mapped Stage
    purpose: str
    lye_adjustment: float = 0.0
    notes: str = ""

    @field_validator("stage", mode="before")
    @classmethod
    def normalize_stage(cls, v: str) -> str:
        """Normalize free-text stage names to Stage enum values.

        Args:
            v: Raw stage string from JSON data.

        Returns:
            Normalized stage string matching a Stage enum value.
        """
        s = v.lower().strip()
        if s == "lye":
            return Stage.LYE_LIQUID.value
        elif s == "trace":
            return Stage.LIGHT_TRACE.value
        elif s == "pre_cook":
            return Stage.OIL_PHASE.value
        elif s == "post_cook":
            return Stage.POST_COOK.value
        return v



class Additive(BaseModel):
    """An additive ingredient in a recipe.

    Attributes:
        name: Display name of the additive.
        amount: Absolute weight in grams (mutually exclusive with percentage).
        percentage: Percentage of a base weight (see percent_base).
        percent_base: Which weight the percentage is relative to.
        stage: Production stage for this additive.
        lye_adjustment: Manual override for lye consumption.
        notes: Optional notes.
    """

    name: str
    amount: Optional[float] = None
    percentage: Optional[float] = None
    percent_base: PercentBase = PercentBase.OIL_WEIGHT
    stage: Stage = Stage.LIGHT_TRACE
    lye_adjustment: Optional[float] = None  # Override or manual adjustment
    notes: str = ""


class Fragrance(BaseModel):
    """A fragrance ingredient in a recipe.

    Attributes:
        name: Display name of the fragrance.
        fragrance_type: Essential oil or fragrance oil.
        amount: Absolute weight in grams (mutually exclusive with percentage).
        percentage: Percentage of oil weight.
        max_safe_pct: IFRA safety limit override.
        stage: Production stage for this fragrance.
        notes: Optional notes.
    """

    name: str
    fragrance_type: FragranceType = FragranceType.FRAGRANCE_OIL
    amount: Optional[float] = None
    percentage: Optional[float] = None
    max_safe_pct: Optional[float] = None
    stage: Stage = Stage.LIGHT_TRACE
    notes: str = ""


class MoldSpec(BaseModel):
    """Mold dimensions for batch sizing.

    Attributes:
        length: Interior length in centimeters.
        width: Interior width in centimeters.
        height: Interior height in centimeters.
        fill_factor: Fraction of mold volume to fill (0.0-1.0).
    """

    length: float
    width: float
    height: float
    fill_factor: float = 0.95

    @property
    def volume(self) -> float:
        """Interior volume in cubic centimeters."""
        return self.length * self.width * self.height

    @property
    def estimated_batch_weight(self) -> float:
        """Estimate total batch weight assuming oil is approx 65% of total."""
        if self.estimated_oil_weight == 0:
            return 0.0
        return self.estimated_oil_weight / 0.65

    @property
    def estimated_oil_weight(self) -> float:
        # User defined: 0.692g of oil per sq cm (assuming cubic cm)
        # Matches approx 11.34g per cubic inch.
        # We respect fill_factor (how full the mold is).
        return self.volume * self.fill_factor * OIL_DENSITY_G_PER_CM3


OIL_DENSITY_G_PER_CM3 = 0.692


# ---------------------------------------------------------------------------
# Recipe Template
# ---------------------------------------------------------------------------


class Recipe(BaseModel):
    """A complete soap recipe definition.

    Attributes:
        name: Recipe name.
        description: Optional description.
        lye_type: Alkali type (NaOH, KOH, or Dual).
        naoh_ratio: NaOH share for dual-lye recipes (0-100).
        naoh_purity: NaOH purity percentage.
        koh_purity: KOH purity percentage.
        superfat_pct: Lye discount or total superfat percentage.
        water_mode: How water amount is calculated.
        water_value: Numeric value for the chosen water mode.
        liquid_discount_pct: Percentage to reduce liquid (for additives that add moisture).
        oils: List of base oils with blend percentages.
        liquids: Liquid-phase ingredients.
        additives: Recipe additives.
        fragrances: Fragrance ingredients.
        superfat_oils: Post-cook superfat oils (HP soap).
        total_oil_weight: Total oil weight in grams (base + superfat).
        base_oil_weight: Base oil weight in grams (excludes superfat).
        mold: Optional mold dimensions for batch sizing.
        ignore_warnings: Warning codes to suppress.
        notes: Free-text notes.
    """

    name: str = "Untitled Recipe"
    description: str = ""
    lye_type: LyeType = LyeType.NAOH
    naoh_ratio: float = 100.0  # e.g., 90% NaOH, 10% KOH
    naoh_purity: float = 100.0
    koh_purity: float = 90.0
    superfat_pct: float = 5.0  # Lye discount OR total superfat % (if superfat_oils used)
    water_mode: WaterCalculationMode = WaterCalculationMode.WATER_LYE_RATIO
    water_value: float = 2.0  # value corresponding to mode
    liquid_discount_pct: float = 0.0
    oils: List[OilEntry] = Field(default_factory=list)
    liquids: List[Liquid] = Field(default_factory=lambda: [Liquid(name="Water")])
    additives: List[Additive] = Field(default_factory=list)
    fragrances: List[Fragrance] = Field(default_factory=list)
    superfat_oils: List[OilEntry] = Field(default_factory=list)  # If present, these define the Superfat Phase
    total_oil_weight: Optional[float] = None  # grams — total batch oils (base + superfat)
    base_oil_weight: Optional[float] = None   # grams — base oils only (excludes superfat)
    mold: Optional[MoldSpec] = None
    ignore_warnings: List[str] = Field(default_factory=list)
    notes: str = ""

    def resolve_oil_weight(self, override: Optional[float] = None) -> float:
        """Determine total oil weight from override, mold, base_oil_weight, or total_oil_weight.

        Priority:
            1. Explicit *override* argument (e.g. from CLI ``--oil-weight``)
            2. Mold specification
            3. ``base_oil_weight`` — back-calculates total using superfat_pct
            4. ``total_oil_weight``
            5. Fallback: 800 g
        """
        if override is not None:
            return float(override)
        if self.mold is not None:
            return round(self.mold.estimated_oil_weight, 2)
        if self.base_oil_weight is not None:
            base = float(self.base_oil_weight)
            if len(self.superfat_oils) > 0:
                # Base + superfat on top: total = base + base * sf%/100
                sf_extra = base * self.superfat_pct / 100.0
                return round(base + sf_extra, 2)
            else:
                # Standard (no superfat oils): core IS the total
                return base
        if self.total_oil_weight is not None:
            return float(self.total_oil_weight)
        return 800.0  # fallback default


# ---------------------------------------------------------------------------
# Calculation Results
# ---------------------------------------------------------------------------


class LyeResult(BaseModel):
    """Calculated lye amounts for a recipe.

    Attributes:
        naoh_amount: Grams of NaOH required.
        koh_amount: Grams of KOH required.
    """

    naoh_amount: float = 0.0
    koh_amount: float = 0.0

    @property
    def total_weight(self) -> float:
        """Total combined lye weight in grams."""
        return self.naoh_amount + self.koh_amount


class LiquidBreakdown(BaseModel):
    """Weight breakdown for a single liquid ingredient.

    Attributes:
        name: Display name of the liquid.
        amount: Weight in grams.
        handling_notes: Preparation notes (e.g., "freeze first").
    """

    name: str
    amount: float
    handling_notes: str = ""


class PropertyRating(enum.Enum):
    """Rating for whether a soap property falls within its recommended range."""

    BELOW = "Below"
    WITHIN = "Within"
    ABOVE = "Above"


class PropertyValue(BaseModel):
    """A predicted soap property with its value and acceptable range.

    Attributes:
        name: Display name of the property.
        value: Predicted numeric value.
        low: Lower bound of the recommended range.
        high: Upper bound of the recommended range.
        rating: Whether the value is below, within, or above range.
    """

    name: str = ""
    value: float = 0.0
    low: float = 0.0
    high: float = 0.0
    rating: PropertyRating = PropertyRating.BELOW


PROPERTY_RANGES = {
    "hardness": (29, 54),
    "cleansing": (12, 22),
    "conditioning": (44, 69),
    "bubbly_lather": (14, 46),
    "creamy_lather": (16, 48),
    "iodine": (41, 70),
    "ins": (136, 170),
    "longevity": (25, 50),
}


class SoapProperties(BaseModel):
    """Full set of predicted soap properties.

    Attributes:
        hardness: Bar hardness prediction.
        cleansing: Cleansing strength prediction.
        conditioning: Skin conditioning prediction.
        bubbly_lather: Bubbly (big bubble) lather prediction.
        creamy_lather: Creamy (stable) lather prediction.
        longevity: Bar longevity prediction.
        iodine: Iodine value of the oil blend.
        ins: INS value of the oil blend.
    """

    hardness: PropertyValue = Field(
        default_factory=lambda: PropertyValue(name="Hardness", value=0, low=PROPERTY_RANGES["hardness"][0], high=PROPERTY_RANGES["hardness"][1], rating=PropertyRating.BELOW)
    )
    cleansing: PropertyValue = Field(
        default_factory=lambda: PropertyValue(name="Cleansing", value=0, low=PROPERTY_RANGES["cleansing"][0], high=PROPERTY_RANGES["cleansing"][1], rating=PropertyRating.BELOW)
    )
    conditioning: PropertyValue = Field(
        default_factory=lambda: PropertyValue(name="Conditioning", value=0, low=PROPERTY_RANGES["conditioning"][0], high=PROPERTY_RANGES["conditioning"][1], rating=PropertyRating.BELOW)
    )
    bubbly_lather: PropertyValue = Field(
        default_factory=lambda: PropertyValue(name="Bubbly Lather", value=0, low=PROPERTY_RANGES["bubbly_lather"][0], high=PROPERTY_RANGES["bubbly_lather"][1], rating=PropertyRating.BELOW)
    )
    creamy_lather: PropertyValue = Field(
        default_factory=lambda: PropertyValue(name="Creamy Lather", value=0, low=PROPERTY_RANGES["creamy_lather"][0], high=PROPERTY_RANGES["creamy_lather"][1], rating=PropertyRating.BELOW)
    )
    longevity: PropertyValue = Field(
        default_factory=lambda: PropertyValue(name="Longevity", value=0, low=PROPERTY_RANGES["longevity"][0], high=PROPERTY_RANGES["longevity"][1], rating=PropertyRating.BELOW)
    )
    iodine: PropertyValue = Field(
        default_factory=lambda: PropertyValue(name="Iodine", value=0, low=PROPERTY_RANGES["iodine"][0], high=PROPERTY_RANGES["iodine"][1], rating=PropertyRating.BELOW)
    )
    ins: PropertyValue = Field(
        default_factory=lambda: PropertyValue(name="INS", value=0, low=PROPERTY_RANGES["ins"][0], high=PROPERTY_RANGES["ins"][1], rating=PropertyRating.BELOW)
    )


class SkinFeel(BaseModel):
    """Superfat character profile for post-cook oil blends in soap."""
    film_persistence: str  # "Low", "Moderate", "High"
    emollient_slip: str    # "Low", "Moderate", "High"
    lather_impact: str     # "Low", "Moderate", "High", "Very High"
    dos_risk: str          # "Low", "Moderate", "High"
    description: str       # Generated narrative combining meaningful dimensions


class AdditiveResult(BaseModel):
    """Calculated result for a single additive, fragrance, or superfat oil.

    Attributes:
        name: Display name of the ingredient.
        amount: Calculated weight in grams.
        stage: Production stage for this ingredient.
        lye_consumed: Extra NaOH consumed by this ingredient (e.g., citric acid).
        notes: Optional notes.
    """

    name: str
    amount: float
    stage: Stage
    lye_consumed: float = 0.0  # Extra NaOH required by this additive
    notes: str = ""


class RecipeResult(BaseModel):
    """Complete output of a soap recipe calculation.

    Attributes:
        lye: NaOH and KOH amounts.
        total_liquid: Total grams of liquid.
        liquid_breakdown: Per-liquid weight breakdown.
        total_oil_weight: Total grams of oil (base + superfat).
        total_batch_weight: Final batter weight in grams.
        fatty_acid_profile: Blended fatty acid profile of the oil mix.
        properties: Predicted soap quality properties.
        additives: Calculated additive results.
        fragrances: Calculated fragrance results.
        superfat_oils: Calculated post-cook superfat oil results.
        effective_superfat_pct: Combined lye discount + superfat oils percentage.
        superfat_analysis: Skin-feel analysis of superfat oils.
        warnings: Validation warnings.
    """

    lye: LyeResult
    total_liquid: float
    liquid_breakdown: List[LiquidBreakdown]
    total_oil_weight: float
    total_batch_weight: float
    fatty_acid_profile: FattyAcidProfile
    properties: SoapProperties
    additives: List[AdditiveResult] = Field(default_factory=list)
    fragrances: List[AdditiveResult] = Field(default_factory=list)
    superfat_oils: List[AdditiveResult] = Field(default_factory=list)  # Post-cook / superfat oils
    effective_superfat_pct: float = 0.0  # Combined lye discount + superfat oils
    superfat_analysis: Optional[SkinFeel] = None
    warnings: List[str] = Field(default_factory=list)

    # Per-stage ingredient grouping -----------------------------------------

    def ingredients_by_stage(self) -> Dict[Stage, List[str]]:
        """Group all ingredients by production stage for instructions.

        Returns:
            Dictionary mapping each Stage to a list of formatted ingredient strings.
        """
        by_stage: Dict[Stage, List[str]] = {}

        # 1. Lye Liquid Stage items (liquids + lye)
        lye_items = []
        for lb in self.liquid_breakdown:
            note = f" ({lb.handling_notes})" if lb.handling_notes else ""
            lye_items.append(f"{lb.name}: {lb.amount:.1f} g{note}")
        
        if self.lye.naoh_amount > 0:
            lye_items.append(f"NaOH: {self.lye.naoh_amount:.1f} g")
        if self.lye.koh_amount > 0:
            lye_items.append(f"KOH: {self.lye.koh_amount:.1f} g")
            
        by_stage[Stage.LYE_LIQUID] = lye_items

        # 2. Additives, Fragrances, Superfat Oils grouped by their stage
        all_items = self.additives + self.fragrances + self.superfat_oils
        for item in all_items:
            if item.amount <= 0:
                continue
            
            entry = f"{item.name}: {item.amount:.1f} g"
            if item.notes:
                entry += f" ({item.notes})"
            
            if item.stage not in by_stage:
                by_stage[item.stage] = []
            by_stage[item.stage].append(entry)

        return by_stage

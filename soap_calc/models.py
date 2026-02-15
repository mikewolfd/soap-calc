"""Core data structures and types."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


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


@dataclass
class FattyAcidProfile:
    lauric: float = 0.0
    myristic: float = 0.0
    palmitic: float = 0.0
    stearic: float = 0.0
    ricinoleic: float = 0.0
    oleic: float = 0.0
    linoleic: float = 0.0
    linolenic: float = 0.0

    def __add__(self, other: "FattyAcidProfile") -> "FattyAcidProfile":
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
        return self.lauric + self.myristic + self.palmitic + self.stearic

    @property
    def cleansing(self) -> float:
        return self.lauric + self.myristic

    @property
    def conditioning(self) -> float:
        return self.oleic + self.linoleic + self.linolenic + self.ricinoleic

    @property
    def bubbly(self) -> float:
        return self.lauric + self.myristic + self.ricinoleic

    @property
    def creamy(self) -> float:
        return self.palmitic + self.stearic + self.ricinoleic

    @property
    def longevity(self) -> float:
        return self.palmitic + self.stearic


@dataclass
class Oil:
    name: str
    sap_naoh: float
    sap_koh: float
    fatty_acids: FattyAcidProfile
    iodine: float = 0.0
    ins: float = 0.0
    notes: str = ""


@dataclass
class OilEntry:
    oil: Oil
    percentage: float  # % of total oils


@dataclass
class Liquid:
    name: str
    percentage: float = 100.0  # % of liquid phase
    handling_notes: str = ""


@dataclass
class AdditiveUsage:
    min: float
    max: float
    unit: str
    per: str  # "lb_oils", "oil_weight"


@dataclass
class AdditiveInfo:
    name: str
    category: str
    usage: AdditiveUsage
    stage: str  # raw string from JSON, or mapped Stage
    purpose: str
    lye_adjustment: float = 0.0  # grams NaOH per gram of additive
    notes: str = ""


@dataclass
class Additive:
    name: str
    amount: Optional[float] = None
    percentage: Optional[float] = None
    percent_base: PercentBase = PercentBase.OIL_WEIGHT
    stage: Stage = Stage.LIGHT_TRACE
    lye_adjustment: Optional[float] = None  # Override or manual adjustment
    notes: str = ""


@dataclass
class Fragrance:
    name: str
    fragrance_type: FragranceType = FragranceType.FRAGRANCE_OIL
    amount: Optional[float] = None
    percentage: Optional[float] = None
    max_safe_pct: Optional[float] = None
    stage: Stage = Stage.LIGHT_TRACE
    notes: str = ""


@dataclass
class MoldSpec:
    length: float
    width: float
    height: float
    fill_factor: float = 0.95

    @property
    def volume(self) -> float:
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


@dataclass
class Recipe:
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
    oils: List[OilEntry] = field(default_factory=list)
    liquids: List[Liquid] = field(default_factory=lambda: [Liquid(name="Water")])
    additives: List[Additive] = field(default_factory=list)
    fragrances: List[Fragrance] = field(default_factory=list)
    superfat_oils: List[OilEntry] = field(default_factory=list)  # If present, these define the Superfat Phase
    total_oil_weight: Optional[float] = None  # grams — total batch oils (base + superfat)
    base_oil_weight: Optional[float] = None   # grams — base oils only (excludes superfat)
    mold: Optional[MoldSpec] = None
    ignore_warnings: List[str] = field(default_factory=list)
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


@dataclass
class LyeResult:
    naoh_amount: float = 0.0
    koh_amount: float = 0.0

    @property
    def total_weight(self) -> float:
        return self.naoh_amount + self.koh_amount


@dataclass
class LiquidBreakdown:
    name: str
    amount: float
    handling_notes: str = ""


class PropertyRating(enum.Enum):
    BELOW = "Below"
    WITHIN = "Within"
    ABOVE = "Above"


@dataclass
class PropertyValue:
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


@dataclass
class SoapProperties:
    hardness: PropertyValue = field(
        default_factory=lambda: PropertyValue("Hardness", 0, *PROPERTY_RANGES["hardness"], PropertyRating.BELOW)
    )
    cleansing: PropertyValue = field(
        default_factory=lambda: PropertyValue("Cleansing", 0, *PROPERTY_RANGES["cleansing"], PropertyRating.BELOW)
    )
    conditioning: PropertyValue = field(
        default_factory=lambda: PropertyValue("Conditioning", 0, *PROPERTY_RANGES["conditioning"], PropertyRating.BELOW)
    )
    bubbly_lather: PropertyValue = field(
        default_factory=lambda: PropertyValue("Bubbly Lather", 0, *PROPERTY_RANGES["bubbly_lather"], PropertyRating.BELOW)
    )
    creamy_lather: PropertyValue = field(
        default_factory=lambda: PropertyValue("Creamy Lather", 0, *PROPERTY_RANGES["creamy_lather"], PropertyRating.BELOW)
    )
    longevity: PropertyValue = field(
        default_factory=lambda: PropertyValue("Longevity", 0, *PROPERTY_RANGES["longevity"], PropertyRating.BELOW)
    )
    iodine: PropertyValue = field(
        default_factory=lambda: PropertyValue("Iodine", 0, *PROPERTY_RANGES["iodine"], PropertyRating.BELOW)
    )
    ins: PropertyValue = field(
        default_factory=lambda: PropertyValue("INS", 0, *PROPERTY_RANGES["ins"], PropertyRating.BELOW)
    )
    cleansing: PropertyValue = field(default_factory=lambda: PropertyValue("Cleansing", 0, 12, 22, PropertyRating.BELOW))
    conditioning: PropertyValue = field(default_factory=lambda: PropertyValue("Conditioning", 0, 44, 69, PropertyRating.BELOW))
    bubbly_lather: PropertyValue = field(default_factory=lambda: PropertyValue("Bubbly", 0, 14, 46, PropertyRating.BELOW))
    creamy_lather: PropertyValue = field(default_factory=lambda: PropertyValue("Creamy", 0, 16, 48, PropertyRating.BELOW))
    longevity: PropertyValue = field(default_factory=lambda: PropertyValue("Longevity", 0, 25, 50, PropertyRating.BELOW))
    iodine: PropertyValue = field(default_factory=lambda: PropertyValue("Iodine", 0, 41, 70, PropertyRating.BELOW))
    ins: PropertyValue = field(default_factory=lambda: PropertyValue("INS", 0, 136, 170, PropertyRating.BELOW))


@dataclass
class AdditiveResult:
    name: str
    amount: float
    stage: Stage
    lye_consumed: float = 0.0  # Extra NaOH required by this additive
    notes: str = ""


@dataclass
class RecipeResult:
    lye: LyeResult
    total_liquid: float
    liquid_breakdown: List[LiquidBreakdown]
    total_oil_weight: float
    total_batch_weight: float
    fatty_acid_profile: FattyAcidProfile
    properties: SoapProperties
    additives: List[AdditiveResult] = field(default_factory=list)
    fragrances: List[AdditiveResult] = field(default_factory=list)
    superfat_oils: List[AdditiveResult] = field(default_factory=list)  # Post-cook / superfat oils
    effective_superfat_pct: float = 0.0  # Combined lye discount + superfat oils
    warnings: List[str] = field(default_factory=list)

    # Per-stage ingredient grouping -----------------------------------------

    def ingredients_by_stage(self) -> Dict[Stage, List[str]]:
        """Group all ingredients by stage for instructions."""
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

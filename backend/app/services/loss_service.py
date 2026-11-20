from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class CropLossConfig:
    baseline_loss_rate: float
    smartdry_loss_rate: float
    market_price_per_kg: float


CROP_LOSS_CONFIGS: Dict[str, CropLossConfig] = {
    "moringa": CropLossConfig(
        baseline_loss_rate=0.35,
        smartdry_loss_rate=0.05,
        market_price_per_kg=300.0,
    ),
    "prunus": CropLossConfig(
        baseline_loss_rate=0.30,
        smartdry_loss_rate=0.04,
        market_price_per_kg=450.0,
    ),
    "hibiscus": CropLossConfig(
        baseline_loss_rate=0.40,
        smartdry_loss_rate=0.06,
        market_price_per_kg=250.0,
    ),
}

GRADE_MULTIPLIERS: Dict[str, float] = {
    "export": 1.0,
    "standard": 0.9,
    "downgraded": 0.5,
}


@dataclass
class AvoidedLossResult:
    avoided_loss_kg: float
    avoided_loss_kes: float


def calculate_avoided_loss(
    crop_type: str,
    initial_weight_kg: float,
    quality_grade: Optional[str] = None
) -> AvoidedLossResult:
    """
    Calculate physical crop preserved (kg) and indicative economic value (KES)
    preserved by controlled smart solar drying over traditional open-air sun drying.

    Formulation:
      kg_saved = initial_weight_kg * (baseline_loss_rate - smartdry_loss_rate)
      kes_saved = kg_saved * market_price_per_kg * grade_multiplier
    """
    if initial_weight_kg <= 0:
        return AvoidedLossResult(avoided_loss_kg=0.0, avoided_loss_kes=0.0)

    crop_key = crop_type.lower().strip()
    config = CROP_LOSS_CONFIGS.get(crop_key)
    if not config:
        raise ValueError(f"Unsupported crop type '{crop_type}'. Supported: {list(CROP_LOSS_CONFIGS.keys())}")

    loss_rate_diff = max(0.0, config.baseline_loss_rate - config.smartdry_loss_rate)
    kg_saved = round(initial_weight_kg * loss_rate_diff, 2)

    grade_key = (quality_grade or "standard").lower().strip()
    multiplier = GRADE_MULTIPLIERS.get(grade_key, 0.9)

    kes_saved = round(kg_saved * config.market_price_per_kg * multiplier, 2)

    return AvoidedLossResult(
        avoided_loss_kg=kg_saved,
        avoided_loss_kes=kes_saved
    )


import pytest
from app.services.loss_service import calculate_avoided_loss, AvoidedLossResult


def test_calculate_avoided_loss_moringa_export():
    # Moringa: baseline 35% vs 5% smartdry = 30% saved.
    # Weight: 100 kg -> 30 kg saved.
    # Market price: 300 KES/kg. Export multiplier: 1.0.
    # KES saved: 30 * 300 * 1.0 = 9000 KES.
    result = calculate_avoided_loss(
        crop_type="moringa",
        initial_weight_kg=100.0,
        quality_grade="export"
    )
    assert isinstance(result, AvoidedLossResult)
    assert result.avoided_loss_kg == 30.0
    assert result.avoided_loss_kes == 9000.0


def test_calculate_avoided_loss_prunus_standard():
    # Prunus: baseline 30% vs 4% smartdry = 26% saved.
    # Weight: 50 kg -> 13 kg saved.
    # Market price: 450 KES/kg. Standard multiplier: 0.9.
    # KES saved: 13 * 450 * 0.9 = 5265 KES.
    result = calculate_avoided_loss(
        crop_type="prunus",
        initial_weight_kg=50.0,
        quality_grade="standard"
    )
    assert result.avoided_loss_kg == 13.0
    assert result.avoided_loss_kes == 5265.0


def test_calculate_avoided_loss_hibiscus_downgraded():
    # Hibiscus: baseline 40% vs 6% smartdry = 34% saved.
    # Weight: 100 kg -> 34 kg saved.
    # Market price: 250 KES/kg. Downgraded multiplier: 0.5.
    # KES saved: 34 * 250 * 0.5 = 4250 KES.
    result = calculate_avoided_loss(
        crop_type="hibiscus",
        initial_weight_kg=100.0,
        quality_grade="downgraded"
    )
    assert result.avoided_loss_kg == 34.0
    assert result.avoided_loss_kes == 4250.0


def test_calculate_avoided_loss_default_grade_when_none():
    # If grade is None or unrecognized, defaults to Standard (0.9)
    result = calculate_avoided_loss(
        crop_type="moringa",
        initial_weight_kg=10.0,
        quality_grade=None
    )
    # 10 kg * (0.35 - 0.05) = 3.0 kg
    # 3.0 * 300 * 0.9 = 810.0 KES
    assert result.avoided_loss_kg == 3.0
    assert result.avoided_loss_kes == 810.0


def test_calculate_avoided_loss_zero_weight():
    result = calculate_avoided_loss(
        crop_type="moringa",
        initial_weight_kg=0.0,
        quality_grade="export"
    )
    assert result.avoided_loss_kg == 0.0
    assert result.avoided_loss_kes == 0.0


def test_calculate_avoided_loss_unknown_crop_raises():
    with pytest.raises(ValueError, match="Unsupported crop type"):
        calculate_avoided_loss(
            crop_type="kale",
            initial_weight_kg=50.0,
            quality_grade="standard"
        )


from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import pytest

from histra.model.shear_law import (
    ELASTO_PLASTIC_ENERGY_SIGMA_INTERPOLATION,
    ELASTO_PLASTIC_FRACTURE_ENERGY_FIXED,
    fracture_energy_shear,
    masonry_shear_law_code,
)


@dataclass
class _Material:
    properties: dict[str, str] = field(default_factory=dict)

    def value(self, name: str, default):
        raw = self.properties.get(name)
        if raw is None:
            return default
        if isinstance(default, float):
            try:
                return float(raw)
            except (TypeError, ValueError):
                return default
        return raw


class _Law(Enum):
    FIXED = ELASTO_PLASTIC_FRACTURE_ENERGY_FIXED
    INTERPOLATED = ELASTO_PLASTIC_ENERGY_SIGMA_INTERPOLATION


_LAW_NAME = "ConstitutiveLawMasonryShear"


@pytest.mark.parametrize(
    ("stored", "expected"),
    [
        ("ElastoPlasticFractureEnergyFixed", ELASTO_PLASTIC_FRACTURE_ENERGY_FIXED),
        ("ElastoPlasticEnergySigmaInterpolation", ELASTO_PLASTIC_ENERGY_SIGMA_INTERPOLATION),
        ("Namespace.ElastoPlasticFractureEnergyFixed", ELASTO_PLASTIC_FRACTURE_ENERGY_FIXED),
        ("4", ELASTO_PLASTIC_FRACTURE_ENERGY_FIXED),
        (5, ELASTO_PLASTIC_ENERGY_SIGMA_INTERPOLATION),
        (_Law.FIXED, ELASTO_PLASTIC_FRACTURE_ENERGY_FIXED),
        ("Hysteretic", 0),
        ("", 0),
        (None, 0),
    ],
)
def test_masonry_shear_law_code(stored, expected) -> None:
    material = _Material({_LAW_NAME: stored}) if stored is not None else None
    assert masonry_shear_law_code(material) == expected


def test_fracture_energy_uses_system_single_rounding() -> None:
    source = "0.001238512345"
    material = _Material({"FractureEnergyShear": source})
    assert fracture_energy_shear(material) == float(np.float32(float(source)))


@pytest.mark.parametrize("stored", [None, "", "invalid", "nan", "inf"])
def test_invalid_fracture_energy_is_zero(stored) -> None:
    material = None if stored is None else _Material({"FractureEnergyShear": stored})
    assert fracture_energy_shear(material) == 0.0


def test_legacy_snake_case_attributes_are_supported() -> None:
    material = type(
        "LegacyMaterial",
        (),
        {
            "constitutive_law_masonry_shear": _Law.INTERPOLATED,
            "fracture_energy_shear": 0.25,
        },
    )()
    assert masonry_shear_law_code(material) == ELASTO_PLASTIC_ENERGY_SIGMA_INTERPOLATION
    assert fracture_energy_shear(material) == 0.25

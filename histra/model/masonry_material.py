from __future__ import annotations
from dataclasses import dataclass, field
import math
from typing import Any, Dict


@dataclass
class MasonryMaterial:
    key: int = 0
    name: str = ""
    w: float = 0.0  # specific weight
    E_min: float = 0.0
    E_med: float = 0.0
    E_max: float = 0.0
    G_min: float = 0.0
    G_med: float = 0.0
    G_max: float = 0.0
    fm_min: float = 0.0
    fm_med: float = 0.0
    fm_max: float = 0.0
    fvk0_min: float = 0.0
    fvk0_med: float = 0.0
    fvk0_max: float = 0.0
    # HiStrA masonry templates contain substantially more constitutive data
    # than the small subset originally needed by the results-restart solver.
    # Keep the complete XML attribute set so preprocessing can reproduce
    # ConstitutiveLawOperations.ExtractInfoFromMaterials without making the
    # loader brittle every time the desktop application adds a field.
    properties: Dict[str, str] = field(default_factory=dict)

    def value(self, name: str, default: Any = 0.0) -> Any:
        """Return a typed material property from the original HRX attributes."""
        raw = self.properties.get(name)
        if raw is None:
            return default
        if isinstance(default, bool):
            return raw.strip().lower() in {"true", "1", "yes"}
        if isinstance(default, int) and not isinstance(default, bool):
            try:
                return int(float(raw))
            except (TypeError, ValueError):
                return default
        if isinstance(default, float):
            try:
                return float(raw)
            except (TypeError, ValueError):
                return default
        return raw

    @property
    def constitutive_law_masonry_shear(self) -> int:
        """Return the C# ``ConstitutiveLawMasonryShear`` enum code.

        ``SpringCoulomb03`` reads this member while running an unmanaged Quad
        diagonal spring.  Keeping the conversion on the material makes the
        scalar fallback use the same fracture-energy branches as the compiled
        Quad runtime.
        """
        from histra.model.shear_law import masonry_shear_law_code

        return masonry_shear_law_code(self)

    def get_shear_ultimate_strain(
        self,
        f_limit: float,
        yield_strain: float,
        volume: float,
        sigma: float,
    ) -> float:
        """Port C# ``MasonryMaterial.GetShearUltimateStrain``.

        The stress-interpolated mode uses the four default C# ``ShearEnergy``
        knots.  They are construction defaults rather than serialized HRX
        data, and C# clamps the interpolation at the two end knots.
        """
        from histra.model.shear_law import (
            ELASTO_PLASTIC_ENERGY_SIGMA_INTERPOLATION,
            ELASTO_PLASTIC_FRACTURE_ENERGY_FIXED,
            fracture_energy_shear,
        )

        mode = self.constitutive_law_masonry_shear
        if mode == ELASTO_PLASTIC_FRACTURE_ENERGY_FIXED:
            energy = fracture_energy_shear(self)
        elif mode == ELASTO_PLASTIC_ENERGY_SIGMA_INTERPOLATION:
            x = -float(sigma)
            knots = (
                (0.05, 0.0012385),
                (0.055, 0.0007775),
                (0.06, 0.0004402),
                (0.07, 0.0001699),
            )
            if x <= knots[0][0]:
                energy = knots[0][1]
            elif x >= knots[-1][0]:
                energy = knots[-1][1]
            else:
                energy = knots[-1][1]
                for (x0, y0), (x1, y1) in zip(knots, knots[1:]):
                    if x <= x1:
                        energy = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
                        break
        else:
            return float(self.value("ShearUltimateStrain", 0.0))

        numerator = energy * float(volume)
        denominator = float(f_limit)
        if denominator == 0.0:
            if numerator == 0.0:
                return math.nan
            return math.copysign(math.inf, numerator)
        return numerator / denominator + 0.5 * float(yield_strain)

from __future__ import annotations
from dataclasses import dataclass, field
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

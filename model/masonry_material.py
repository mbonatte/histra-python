from __future__ import annotations
from dataclasses import dataclass, field


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

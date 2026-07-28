from __future__ import annotations
from dataclasses import dataclass
from typing import List
from histra.springs.base import Spring
from histra.springs.registry import _register_spring


@_register_spring("HiStrA.Objects.SpringMultiLinear")
@dataclass
class SpringMultiLinear(Spring):
    """Multi-linear spring."""
    # Deformation points (could be encoded as semicolon-separated values)
    deformations: str = ""
    forces: str = ""

    @classmethod
    def _from_xml(cls, elem: ET.Element, type_of: str = "") -> SpringMultiLinear:
        inst = cls(type_of=type_of or elem.get("TypeOf", ""))
        inst.k = _attr(elem, "K", 0.0, float)
        inst.deformations = _attr(elem, "Deformations", "")
        inst.forces = _attr(elem, "Forces", "")
        known = {"TypeOf", "K", "Deformations", "Forces"}
        for key, val in elem.attrib.items():
            if key not in known:
                inst.extra[key] = val
        return inst

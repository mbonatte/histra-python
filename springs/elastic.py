from __future__ import annotations
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from histra.springs.base import Spring
from histra.springs.registry import _register_spring


@_register_spring("HiStrA.Objects.SpringElastic")
@dataclass
class SpringElastic(Spring):
    """Linear elastic spring."""
    @classmethod
    def _from_xml(cls, elem: ET.Element, type_of: str = "") -> SpringElastic:
        return super()._from_xml(elem, type_of)

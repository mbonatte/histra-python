from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class Restraint:
    key: int = 0
    name: str = ""
    node_c_keys: List[int] = field(default_factory=lambda: [0, 0])
    k: List[float] = field(default_factory=lambda: [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0])

    @classmethod
    def from_xml(cls, elem) -> Restraint:
        r = cls()
        r.key = int(elem.get("Key", "0"))
        r.name = elem.get("Name", "")
        nck1 = int(elem.get("NodeCKey1", "0"))
        nck2 = int(elem.get("NodeCKey2", "0"))
        r.node_c_keys = [nck1, nck2]
        for i in range(6):
            kval = elem.get(f"K{i+1}", None)
            if kval is not None:
                r.k[i] = float(kval)
        return r

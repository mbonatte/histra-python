"""C#-compatible interface-material mutation between committed analyses."""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Iterable, Any

from histra.preprocessing.prepare_model import rebuild_interface_springs
from histra.solver.model_manager import ModelManager
from histra.solver.restart import transfer_committed_spring_state


class InterfaceMaterialMutationError(RuntimeError):
    """Raised when an interface material cannot be changed losslessly."""


@dataclass(frozen=True)
class InterfaceMaterialMutationRecord:
    interface_key: int
    old_material_key: int
    new_material_key: int
    transverse_springs: int
    in_plane_springs: int
    out_of_plane_springs: int


@dataclass(frozen=True)
class InterfaceMaterialMutationReport:
    material_key: int
    records: tuple[InterfaceMaterialMutationRecord, ...]

    @property
    def interface_count(self) -> int:
        return len(self.records)

    @property
    def spring_count(self) -> int:
        return sum(
            row.transverse_springs + row.in_plane_springs + row.out_of_plane_springs
            for row in self.records
        )


def _groups(interface: Any) -> tuple[list[Any], list[Any], list[Any]]:
    return interface.trasv_1, interface.slid, interface.slid_out_plan


def _transfer_groups(old: Any, new: Any) -> None:
    old_groups = _groups(old)
    new_groups = _groups(new)
    labels = ("transverse", "in-plane", "out-of-plane")
    for label, source_group, target_group in zip(labels, old_groups, new_groups):
        if len(source_group) != len(target_group):
            raise InterfaceMaterialMutationError(
                f"Interface {old.key}: {label} spring count changed during material "
                f"mutation ({len(source_group)} -> {len(target_group)})."
            )
        for source, target in zip(source_group, target_group):
            transfer_committed_spring_state(source, target)


def change_interface_materials(
    model: Any,
    interface_keys: Iterable[int],
    material_key: int,
    *,
    preserve_committed_state: bool = True,
) -> InterfaceMaterialMutationReport:
    """Change selected interface materials atomically.

    The C#-compatibility sequence is:

    1. rebuild each interface's spring definitions using ``material_key`` for
       both sides;
    2. restore the predecessor's committed local history onto those new
       definitions;
    3. preserve the committed Interface state and geometry/afference mapping;
    4. invalidate the compiled constitutive runtime.

    The global displacement and all unaffected elements remain unchanged.
    """
    if model.collections is None:
        raise InterfaceMaterialMutationError("Model.collections is not initialized.")
    material_key = int(material_key)
    if material_key != 0 and material_key not in model.collections.materials:
        raise InterfaceMaterialMutationError(
            f"Unknown interface material key {material_key}."
        )

    keys = tuple(dict.fromkeys(int(key) for key in interface_keys))
    if not keys:
        return InterfaceMaterialMutationReport(material_key, ())
    missing = [key for key in keys if key not in model.collections.interfaces]
    if missing:
        raise InterfaceMaterialMutationError(
            f"Unknown interface keys: {missing}."
        )

    backups = {key: copy.deepcopy(model.collections.interfaces[key]) for key in keys}
    records: list[InterfaceMaterialMutationRecord] = []
    try:
        for key in keys:
            interface = model.collections.interfaces[key]
            old = backups[key]
            old_status = copy.deepcopy(interface.status)
            old_force = list(interface.f)
            old_material_key = int(interface.material_key)

            interface.material_key = material_key
            rebuild_interface_springs(model, interface)
            if preserve_committed_state:
                _transfer_groups(old, interface)

            # ReSetInterfaces initializes a fresh status, then C# SetStatus
            # restores the predecessor InterfaceState.  In-memory chaining can
            # preserve that same committed state directly.
            interface.status = old_status
            interface.f[:] = old_force
            interface._perf_di = interface._perf_dj = interface._perf_ecc = None
            interface._perf_aff_pairs = None
            interface._perf_dist = interface._perf_dist_for = None

            records.append(
                InterfaceMaterialMutationRecord(
                    interface_key=key,
                    old_material_key=old_material_key,
                    new_material_key=material_key,
                    transverse_springs=len(interface.trasv_1),
                    in_plane_springs=len(interface.slid),
                    out_of_plane_springs=len(interface.slid_out_plan),
                )
            )
    except Exception:
        for key, backup in backups.items():
            model.collections.interfaces[key] = backup
        ModelManager.clear_hysteretic_batch()
        raise

    # Dense Numba arrays contain the old spring definitions and must never be
    # reused after a material mutation.  The next solve rebuilds them once.
    ModelManager.clear_hysteretic_batch()
    return InterfaceMaterialMutationReport(material_key, tuple(records))

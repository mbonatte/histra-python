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


def _backup_interface(interface: Any) -> Any:
    """Return a rollback-safe backup without duplicating the object graph.

    ``rebuild_interface_springs`` replaces the mutable constitutive containers
    (spring lists and ``status``) instead of mutating their predecessors.  A
    shallow copy therefore keeps the exact predecessor objects needed for
    committed-state transfer and rollback while sharing immutable geometry,
    afference data and cached arrays.  Only ``f`` is copied because it is
    restored in-place on a successful mutation and must remain independent if
    a later step fails.
    """
    backup = copy.copy(interface)
    backup.f = list(interface.f)
    return backup


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
    4. update compatible dense constitutive rows in place, otherwise fall
       back to the existing full compiled-runtime rebuild.

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

    backups = {
        key: _backup_interface(model.collections.interfaces[key]) for key in keys
    }
    # The geometry cache is immutable across a material-only rebuild.  The
    # spring factory clears these fields because it is also used during full
    # model preparation; retain them here to avoid redoing geometry work after
    # every scour step.
    geometry_caches = {
        key: (
            getattr(model.collections.interfaces[key], "_perf_di", None),
            getattr(model.collections.interfaces[key], "_perf_dj", None),
            getattr(model.collections.interfaces[key], "_perf_ecc", None),
            getattr(model.collections.interfaces[key], "_perf_area", None),
        )
        for key in keys
    }
    records: list[InterfaceMaterialMutationRecord] = []
    # Material-law construction depends only on the material and direction.
    # Share these caches across this mutation batch, exactly as full model
    # preparation does, instead of rebuilding identical law objects for every
    # interface.
    flex_law_cache: dict[Any, Any] = {}
    sliding_law_cache: dict[Any, Any] = {}
    try:
        for key in keys:
            interface = model.collections.interfaces[key]
            old = backups[key]
            # Preserve the existing SetStatus semantics exactly. InterfaceState
            # is intentionally tiny (small fixed-size vectors/matrices), so this
            # copy is negligible compared with deepcopying the whole Interface.
            old_status = copy.deepcopy(interface.status)
            old_force = list(interface.f)
            old_material_key = int(interface.material_key)

            interface.material_key = material_key
            rebuild_interface_springs(
                model,
                interface,
                flex_law_cache=flex_law_cache,
                sliding_law_cache=sliding_law_cache,
            )
            if preserve_committed_state:
                _transfer_groups(old, interface)

            # ReSetInterfaces initializes a fresh status, then C# SetStatus
            # restores the predecessor InterfaceState.  In-memory chaining can
            # preserve that same committed state directly.
            interface.status = old_status
            interface.f[:] = old_force
            (
                interface._perf_di,
                interface._perf_dj,
                interface._perf_ecc,
                interface._perf_area,
            ) = geometry_caches[key]

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

    # Keep the large dense runtime when the replacement spring layout is
    # structurally identical.  The runtime validates *all* changed interfaces
    # before touching its arrays; any incompatibility or update error clears it
    # so the next solve follows the existing full-build path.
    changed_interfaces = tuple(model.collections.interfaces[key] for key in keys)
    ModelManager.update_hysteretic_batch_material_interfaces(
        model, changed_interfaces
    )
    return InterfaceMaterialMutationReport(material_key, tuple(records))

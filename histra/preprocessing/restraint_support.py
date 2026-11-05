"""Elastic and fixed Restraint support semantics shared by preprocessing/solver.

C# stores six numerical restraint stiffnesses in ``Restraint.K`` expressed in
the restraint's local reference system:

* ``-1``: fully fixed (no independent restraint DOF);
* `` 0``: free (an independent DOF exists but carries no stiffness);
* ``>0``: elastic stiffness in force/length (translations) or
  moment/rotation (rotations).

Only normal elastic stiffness is translated here: ``K2 > 0``. Other
directions may be fixed or free. The bottom-foundation mesher writes
``K2 = Kz * B * L`` (force/length). Python consumes each serialized ``K2``
directly, without applying that formula to other faces or inventing a material.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from histra.preprocessing.errors import ModelPreparationError

if TYPE_CHECKING:  # pragma: no cover - typing only
    from histra.elements.interface import Interface
    from histra.model.model import Model
    from histra.model.restraint import Restraint
    from histra.types.linear_system import LinearSystem


FIXED = "fixed"
# Preserve the classifier value exposed by the original bottom-face feature.
ELASTIC_NORMAL = "elastic_vertical"
ELASTIC_VERTICAL = ELASTIC_NORMAL
FREE = "free"

_INDEX_NAMES = ("K1", "K2", "K3", "Kr1", "Kr2", "Kr3")


def _is_fixed(value: float) -> bool:
    return abs(float(value) + 1.0) <= 1.0e-12


def _is_zero(value: float) -> bool:
    return float(value) == 0.0


def classify_restraint_stiffness(restraint: "Restraint") -> str:
    """Return the supported stiffness mode or fail with a precise reason.

    Positive stiffness is supported in the local normal direction only.
    Zero stiffness retains an independent free DOF, as in C#.
    """
    values = [float(value) for value in restraint.k]
    if len(values) != 6:
        raise ModelPreparationError(
            f"Restraint {restraint.key} has {len(values)} stiffness values; expected 6."
        )
    if not np.all(np.isfinite(values)):
        raise ModelPreparationError(f"Restraint {restraint.key} has non-finite stiffness values.")
    if all(_is_fixed(value) for value in values):
        return FIXED

    unsupported = [index for index, value in enumerate(values)
                   if index != 1 and value > 0.0]
    if unsupported:
        directions = ", ".join(_INDEX_NAMES[index] for index in unsupported)
        raise ModelPreparationError(
            f"Restraint {restraint.key} has unsupported elastic local direction(s) "
            f"{directions}; only K2 (local normal) is supported."
        )
    if not all(_is_fixed(value) or _is_zero(value) or (i == 1 and value > 0)
               for i, value in enumerate(values)):
        raise ModelPreparationError(
            f"Restraint {restraint.key} has unsupported stiffness values K={values!r}."
        )
    if values[1] > 0.0:
        if int(restraint.material_key) != 0:
            raise ModelPreparationError(
                f"Restraint {restraint.key} combines an elastic normal stiffness "
                f"with MaterialKey={restraint.material_key}; elastic restraint "
                "stiffness and geotechnical material springs are not a verified "
                "combination."
            )
        return ELASTIC_NORMAL
    return FREE


def active_restraint_directions(restraint: "Restraint") -> tuple[int, ...]:
    """Return local K indices that require an independent global DOF."""
    return tuple(
        index for index, value in enumerate(restraint.k) if float(value) >= 0.0
    )


def assign_restraint_dofs(model: "Model", last_gdl: int) -> int:
    """Append native restraint DOFs after the Quad DOFs.

    C# ``ModelManager.ComputeAff`` visits Quads first and Restraints next, so
    appending here preserves the observable DOF order whenever a model actually
    contains elastic restraints.  Fully fixed restraints allocate no DOF, which
    keeps every existing fixed-restraint model bit-for-bit unchanged.

    ``last_gdl`` is the highest DOF number already assigned (0 when none).
    The return value is the new highest assigned DOF number.
    """
    assert model.collections is not None
    model.__dict__.pop("_restraint_support_runtime", None)
    gdl = int(last_gdl)
    for restraint in sorted(
        getattr(model.collections, "restraints", {}).values(),
        key=lambda item: item.key,
    ):
        mode = classify_restraint_stiffness(restraint)
        restraint.u = [0.0] * 6
        restraint.solver_gdls = [0] * 6
        if mode == FIXED:
            continue
        for local_index in active_restraint_directions(restraint):
            gdl += 1
            restraint.solver_gdls[local_index] = gdl
    return gdl


def has_elastic_restraints(model: "Model") -> bool:
    assert model.collections is not None
    return any(
        classify_restraint_stiffness(restraint) != FIXED
        for restraint in getattr(model.collections, "restraints", {}).values()
    )


def restraint_reference_axes(
    restraint: "Restraint", interface: "Interface"
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return the serialized restraint axes, required for an elastic support."""
    if restraint.has_reference_system:
        return (
            np.asarray(restraint.reference_e1, dtype=float),
            np.asarray(restraint.reference_e2, dtype=float),
            np.asarray(restraint.reference_e3, dtype=float),
        )
    raise ModelPreparationError(
        f"Elastic Restraint {restraint.key} requires a valid ReferenceSystem."
    )


def validate_elastic_restraint_frame(restraint: "Restraint") -> None:
    """Reject unsupported frames before rebuilding computational objects."""
    if classify_restraint_stiffness(restraint) == FIXED:
        return
    if not restraint.has_reference_system:
        raise ModelPreparationError(
            f"Elastic Restraint {restraint.key} requires a valid ReferenceSystem."
        )
    axes = np.asarray((restraint.reference_e1, restraint.reference_e2,
                       restraint.reference_e3), dtype=float)
    if (not np.all(np.isfinite(axes)) or
            not np.allclose(axes @ axes.T, np.eye(3), atol=1e-5, rtol=0)):
        raise ModelPreparationError(
            f"Elastic Restraint {restraint.key} requires orthonormal axes "
            "aligned with its interface."
        )


def _sign(value: float) -> float:
    if value > 0.0:
        return 1.0
    if value < 0.0:
        return -1.0
    return 0.0


def restraint_interface_signs(
    restraint: "Restraint", interface: "Interface"
) -> tuple[float, float, float]:
    """C# ``ComputeInterfaceAfference`` axis-alignment signs."""
    e1, e2, e3 = restraint_reference_axes(restraint, interface)
    i1 = np.asarray(interface.reference_e1, dtype=float)
    i2 = np.asarray(interface.reference_e2, dtype=float)
    i3 = np.asarray(interface.reference_e3, dtype=float)
    if classify_restraint_stiffness(restraint) != FIXED:
        validate_elastic_restraint_frame(restraint)
        axes = np.stack((e1, e2, e3))
        interface_axes = np.stack((i1, i2, i3))
        if not np.allclose(np.abs(np.sum(axes * interface_axes, axis=1)),
                           1.0, atol=1e-5, rtol=0):
            raise ModelPreparationError(
                f"Elastic Restraint {restraint.key} requires orthonormal axes "
                "aligned with its interface."
            )
    return (
        _sign(float(np.dot(i1, e1))),
        _sign(float(np.dot(i2, e2))),
        _sign(float(np.dot(i3, e3))),
    )


def _support_runtime(model: "Model"):
    """Bind active restraint state to dense arrays owned by this model."""
    runtime = getattr(model, "_restraint_support_runtime", None)
    if runtime is not None and runtime[0] == id(model):
        return runtime
    restraints = [r for r in sorted(getattr(model.collections, "restraints", {}).values(), key=lambda r: r.key)
                  if classify_restraint_stiffness(r) != FIXED]
    states = np.asarray([r.u for r in restraints], dtype=np.float64).reshape(-1, 6)
    row, direction = np.nonzero(np.asarray([r.solver_gdls for r in restraints], dtype=np.int64).reshape(-1, 6) > 0)
    gdls = np.asarray([r.solver_gdls for r in restraints], dtype=np.int64).reshape(-1, 6)
    kvals = np.asarray([r.k for r in restraints], dtype=np.float64).reshape(-1, 6)
    dofs = gdls[row, direction] - 1
    stiffness = kvals[row, direction]
    if np.any(dofs < 0) or np.any(dofs >= model.gdl):
        raise ModelPreparationError("Elastic restraint DOFs are not prepared.")
    for index, restraint in enumerate(restraints):
        restraint.u = states[index]
    runtime = (id(model), states, dofs, stiffness, row, direction)
    model._restraint_support_runtime = runtime
    return runtime


def restraint_support_entries(
    model: "Model",
) -> tuple[list[int], list[int], list[float]]:
    """Return 0-based diagonal COO entries for the restraint support springs."""
    assert model.collections is not None
    _, _, dofs, stiffness, _, _ = _support_runtime(model)
    active = stiffness > 0.0
    return dofs[active].tolist(), dofs[active].tolist(), stiffness[active].tolist()


def update_restraint_domain(model: "Model", ls: "LinearSystem") -> None:
    """Accumulate the local restraint displacements from ``ls.x``.

    Native ``Restraint.updateDomain`` adds the current correction to
    ``Status.U`` for every active local DOF.  The same operation also restores
    a failed trial when ``ls.x`` contains ``u_committed - u`` during rollback.
    """
    assert model.collections is not None
    x = getattr(ls, "x", ls)
    _, states, dofs, _, row, direction = _support_runtime(model)
    states[row, direction] += np.asarray(x)[dofs]


def scatter_restraint_resisting_force(model: "Model", ls: "LinearSystem") -> None:
    """Add ``-K_i * U_i`` to the residual for each active restraint DOF."""
    assert model.collections is not None
    _, states, dofs, stiffness, row, direction = _support_runtime(model)
    ls.b[dofs] -= stiffness * states[row, direction]

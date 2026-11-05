"""Convert user-specified lateral Winkler moduli to finalized restraint K2."""
from __future__ import annotations

import math
import numpy as np

from histra.preprocessing.errors import ModelPreparationError


def set_lateral_subgrade_moduli(model, restraint_keys, *, kx_kn_m3, ky_kn_m3):
    """Set selected lateral restraint stiffnesses from global kN/m³ moduli.

    HRX geometry uses cm and kN; dividing kN/m³ by 10^6 gives kN/cm³.
    The projected normal modulus is kx*nx² + ky*ny²; multiplying by the
    serialized restraint patch area in cm² gives the total K2 in kN/cm.
    Existing non-normal stiffnesses are preserved. Changes require fresh
    preparation and do not modify the source HRX file.
    """
    kx, ky = float(kx_kn_m3), float(ky_kn_m3)
    if not all(math.isfinite(x) and x >= 0 for x in (kx, ky)):
        raise ValueError("Kx and Ky must be finite, non-negative kN/m³ values.")
    keys = tuple(int(key) for key in restraint_keys)
    if not keys or len(set(keys)) != len(keys):
        raise ValueError("Specify a nonempty set of distinct restraint keys.")
    updates = []
    for key in keys:
        restraint = model.collections.restraints.get(key)
        if restraint is None:
            raise ModelPreparationError(f"Restraint {key} does not exist.")
        if restraint.material_key != 0:
            raise ModelPreparationError(f"Restraint {key} has MaterialKey={restraint.material_key}; linear Kx/Ky cannot be combined with a material law.")
        if not restraint.has_reference_system:
            raise ModelPreparationError(f"Restraint {key} requires a serialized ReferenceSystem.")
        axis = np.asarray(restraint.reference_e2, dtype=float)
        axes = np.asarray((restraint.reference_e1, restraint.reference_e2, restraint.reference_e3), dtype=float)
        if not np.all(np.isfinite(axes)) or not np.allclose(axes @ axes.T, np.eye(3), atol=1e-5, rtol=0) or abs(axis[2]) > 1e-5:
            raise ModelPreparationError(f"Restraint {key} requires an orthonormal frame with horizontal local E2.")
        points = np.asarray([(p.x, p.y, p.z) for p in restraint.points], dtype=float)
        normal1 = np.cross(points[1] - points[0], points[2] - points[0])
        normal2 = np.cross(points[2] - points[0], points[3] - points[0])
        area = 0.5 * (np.linalg.norm(normal1) + np.linalg.norm(normal2))
        if not np.isfinite(area) or area <= 0:
            raise ModelPreparationError(f"Restraint {key} has zero or invalid patch area.")
        if abs(np.dot(normal1, axis)) < (1 - 1e-5) * np.linalg.norm(normal1) or abs(np.dot(normal2, axis)) < (1 - 1e-5) * np.linalg.norm(normal2):
            raise ModelPreparationError(f"Restraint {key} local E2 is not normal to its patch.")
        updates.append((restraint, float((kx * axis[0] ** 2 + ky * axis[1] ** 2) * area / 1e6)))
    for restraint, stiffness in updates:
        restraint.k[1] = stiffness
    model._restraint_values_modified = True
    model.requires_python_preparation = True
    return {restraint.key: stiffness for restraint, stiffness in updates}

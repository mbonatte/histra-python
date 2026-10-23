"""Native high-performance simulation output architecture (Tiered Scientific Array Storage).

Provides two-tier output for HiStrA simulations:
- Tier 1: Summary Manifest (<case_id>.summary.json, < 100 KB) for instant notebook
  plotting and table generation.
- Tier 2: Dense Array Dataset (<case_id>.fields.npz or .h5, ~12-25 MB) separating
  static mesh topology from dynamic step fields and constitutive arrays.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import time
from typing import Any, Mapping
import warnings

import numpy as np

import histra
from histra.model.model import Model
from histra.postprocessing import compute_node_displacements
from histra.solver.model_manager import ModelManager
from histra.solver.outcomes import AnalysisExecution, AnalysisOutcome, AnalysisStep


class ResultsWriter:
    """Exports simulation results into the 2-tier storage layout."""

    @staticmethod
    def export(
        model: Model,
        execution: AnalysisExecution,
        filepath: str | Path,
        format: str = "npz",  # "npz" | "h5" | "json"
        tier: str = "all",     # "summary" | "fields" | "all"
        include_node_displacements: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Path]:
        """Exports simulation results into the 2-tier storage layout.

        Parameters
        ----------
        model : Model
            The HiStrA Model instance.
        execution : AnalysisExecution
            The execution record returned by AnalysisSession.run.
        filepath : str or Path
            Target base filepath. Suffixes (.npz, .h5, .summary.json, etc.)
            are stripped to form the stem.
        format : {"npz", "h5", "json"}, default="npz"
            Array storage format. "npz" uses compressed NumPy; "h5" uses HDF5
            (falls back to .npz if h5py is not installed). "json" writes Tier 1 only.
        tier : {"all", "summary", "fields"}, default="all"
            Which tiers to export.
        include_node_displacements : bool, default=True
            Whether to project and store full 3D node translations across steps.
        metadata : dict, optional
            Additional metadata merged into the summary manifest.

        Returns
        -------
        dict[str, Path]
            Dictionary containing created file paths: {'summary': path, 'fields': path}.
        """
        p = Path(filepath)
        output_dir = p.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        name = p.name
        for suffix in (
            ".summary.json",
            ".fields.npz",
            ".fields.h5",
            ".npz",
            ".h5",
            ".json",
        ):
            if name.endswith(suffix):
                name = name[: -len(suffix)]
                break

        summary_path = output_dir / f"{name}.summary.json"

        # Determine target fields format and path
        fmt = str(format).lower().strip()
        use_h5 = False
        if fmt == "h5":
            try:
                import h5py  # noqa: F401
                use_h5 = True
                fields_path = output_dir / f"{name}.fields.h5"
            except ImportError:
                warnings.warn(
                    "h5py is not installed; falling back to compressed NumPy (.npz) format.",
                    UserWarning,
                    stacklevel=2,
                )
                fields_path = output_dir / f"{name}.fields.npz"
        else:
            fields_path = output_dir / f"{name}.fields.npz"

        created: dict[str, Path] = {}
        tier_mode = str(tier).lower().strip()

        # Build Tier 1 Summary Manifest
        if tier_mode in ("all", "summary") or fmt == "json":
            summary_dict = _build_summary_manifest(
                model=model,
                execution=execution,
                case_id=name,
                extra_metadata=metadata,
            )
            with open(summary_path, "w", encoding="utf-8") as fp:
                json.dump(summary_dict, fp, indent=2)
            created["summary"] = summary_path

        # Build Tier 2 Dense Arrays
        if tier_mode in ("all", "fields") and fmt != "json":
            arrays = _build_dense_field_arrays(
                model=model,
                execution=execution,
                include_node_displacements=include_node_displacements,
            )
            if use_h5:
                _write_hdf5(fields_path, arrays)
            else:
                np.savez_compressed(fields_path, **arrays)
            created["fields"] = fields_path

        return created


def _compute_sha256(filepath: str | Path) -> str | None:
    p = Path(filepath)
    if not p.is_file():
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _build_summary_manifest(
    model: Model,
    execution: AnalysisExecution,
    case_id: str,
    extra_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    steps = execution.output_steps
    if not steps and execution.steps:
        steps = execution.steps

    model_src = getattr(model, "source_path", getattr(model, "filepath", None))
    sha256 = _compute_sha256(model_src) if model_src else None
    model_name = Path(model_src).stem if model_src else str(getattr(model, "name", case_id))

    # Step scalar histories
    step_indices = [int(s.step) for s in steps]
    displacements = [float(s.get("displacement", 0.0)) for s in steps]
    load_factors = [float(s.get("load_factor", 0.0)) for s in steps]
    rx = [float(s.get("reaction_x", 0.0)) for s in steps]
    ry = [float(s.get("reaction_y", 0.0)) for s in steps]
    rz = [float(s.get("reaction_z", 0.0)) for s in steps]

    # Reaction forces: compute lateral and total resultant forces
    forces_lateral = [math.hypot(x, y) for x, y in zip(rx, ry)]
    forces_total = [math.sqrt(x * x + y * y + z * z) for x, y, z in zip(rx, ry, rz)]

    # If initial vertical reaction is non-zero, compute incremental reaction
    rz0 = rz[0] if rz else 0.0
    forces_delta_z = [abs(z - rz0) for z in rz]

    # Use lateral force if active, otherwise vertical force increment or total
    if max(forces_lateral, default=0.0) > 1e-4:
        forces_curve = forces_lateral
    elif max(forces_delta_z, default=0.0) > 1e-4:
        forces_curve = forces_delta_z
    else:
        forces_curve = forces_total

    f_max = max(forces_curve, default=0.0)
    idx_max = forces_curve.index(f_max) if f_max in forces_curve else 0
    d_at_f_max = displacements[idx_max] if idx_max < len(displacements) else 0.0
    d_max = max((abs(d) for d in displacements), default=0.0)

    # Ductility estimate (ratio of peak/ultimate displacement to approximate yield)
    ductility: float | None = None
    if f_max > 1e-6 and len(forces_curve) > 3:
        # 70% secant stiffness approximation for yield displacement
        f_70 = 0.70 * f_max
        d_y = None
        for i in range(1, len(forces_curve)):
            if forces_curve[i] >= f_70:
                d_y = abs(displacements[i])
                break
        if d_y is not None and d_y > 1e-6:
            ductility = round(d_max / d_y, 3)

    # Failure classification
    outcome = execution.outcome
    if execution.completed:
        classification = "target_reached"
    elif outcome == AnalysisOutcome.COMPLETED_AT_DISPLACEMENT_LIMIT:
        classification = "displacement_limit"
    elif outcome == AnalysisOutcome.CANCELLED:
        classification = "cancelled"
    elif outcome == AnalysisOutcome.NONCONVERGED:
        classification = "divergence"
    else:
        classification = str(outcome.value if outcome else "unknown")

    meta: dict[str, Any] = {
        "case_id": case_id,
        "schema_version": "1.0.0",
        "title": str(getattr(model, "title", model_name)),
        "model_name": model_name,
        "model_file": str(model_src or ""),
        "model_sha256": sha256,
        "analysis_key": int(execution.analysis_key),
        "analysis_name": str(execution.analysis_name),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generator": f"histra-python {getattr(histra, '__version__', '1.6.4')}",
        "units": {
            "length": "mm",
            "force": "kN",
            "displacement": "mm",
            "moment": "kN*mm",
            "stress": "MPa",
        },
    }
    if extra_metadata:
        meta.update(extra_metadata)

    return {
        "metadata": meta,
        "metrics": {
            "f_max_kN": float(f_max),
            "d_max_mm": float(d_max),
            "d_at_f_max_mm": float(d_at_f_max),
            "ductility": ductility,
            "total_steps": len(execution.steps),
            "committed_steps": len(execution.committed_steps),
            "runtime_seconds": float(execution.runtime_seconds),
            "exit_code": int(execution.code),
            "outcome": str(outcome.value if outcome else execution.code),
            "completed": bool(execution.completed),
            "failure_classification": classification,
        },
        "curve": {
            "step": step_indices,
            "displacement_mm": displacements,
            "force_kN": forces_curve,
            "load_factor": load_factors,
        },
        "reactions": {
            "reaction_x": rx,
            "reaction_y": ry,
            "reaction_z": rz,
            "reaction_mag": forces_total,
        },
    }


def _build_dense_field_arrays(
    model: Model,
    execution: AnalysisExecution,
    include_node_displacements: bool = True,
) -> dict[str, np.ndarray]:
    """Extract and build all dense NumPy arrays for Tier 2 storage."""
    arrays: dict[str, np.ndarray] = {}

    # 1. Static Mesh Topology
    quad_node_keys = {
        int(nk)
        for quad in model.collections.quads.values()
        for nk in quad.node_keys
    }
    # Only export Quad-connected nodes in mesh topology
    sorted_nodes = [
        (int(k), node)
        for k, node in sorted(model.collections.nodes.items())
        if int(k) in quad_node_keys
    ]
    node_keys = np.array([k for k, _ in sorted_nodes], dtype=np.uint32)
    nodes_xyz = np.array(
        [[float(n.point.x), float(n.point.y), float(n.point.z)] for _, n in sorted_nodes],
        dtype=np.float32,
    )
    arrays["mesh/node_keys"] = node_keys
    arrays["mesh/nodes_xyz"] = nodes_xyz

    sorted_quads = sorted(model.collections.quads.items())
    quad_keys = np.array([int(k) for k, _ in sorted_quads], dtype=np.uint32)
    quad_conn = np.array(
        [
            [int(nk) for nk in getattr(q, "node_keys", [0, 0, 0, 0])]
            for _, q in sorted_quads
        ],
        dtype=np.uint32,
    )
    quad_g = np.array(
        [[float(q.g.x), float(q.g.y), float(q.g.z)] for _, q in sorted_quads],
        dtype=np.float32,
    )
    arrays["mesh/quad_keys"] = quad_keys
    arrays["mesh/quad_conn"] = quad_conn
    arrays["mesh/quad_g"] = quad_g

    sorted_interfaces = sorted(model.collections.interfaces.items())
    intf_keys = np.array([int(k) for k, _ in sorted_interfaces], dtype=np.uint32)
    intf_parents = np.array(
        [
            [int(i.parent_element_key1), int(i.parent_element_key2)]
            for _, i in sorted_interfaces
        ],
        dtype=np.uint32,
    )
    # Interface polygon 3D coordinates (4, 3)
    intf_vint = np.zeros((len(sorted_interfaces), 4, 3), dtype=np.float32)
    for idx, (_, intf) in enumerate(sorted_interfaces):
        vint_pts = getattr(intf, "vint3d", None) or getattr(intf, "vint", None) or getattr(intf, "vint2d", None)
        if vint_pts:
            for pt_idx, pt in enumerate(vint_pts[:4]):
                intf_vint[idx, pt_idx, 0] = float(pt.x)
                intf_vint[idx, pt_idx, 1] = float(pt.y)
                intf_vint[idx, pt_idx, 2] = float(getattr(pt, "z", 0.0))
    arrays["mesh/interface_keys"] = intf_keys
    arrays["mesh/interface_parents"] = intf_parents
    arrays["mesh/interface_vint"] = intf_vint

    # 2. Step Fields
    steps = execution.output_steps
    if not steps and execution.steps:
        steps = execution.steps

    n_steps = len(steps)
    gdl = int(model.gdl)
    n_intf = len(sorted_interfaces)
    n_nodes = len(sorted_nodes)

    step_index = np.array([int(s.step) for s in steps], dtype=np.int32)
    load_factor = np.array([float(s.get("load_factor", 0.0)) for s in steps], dtype=np.float32)
    displacement = np.array([float(s.get("displacement", 0.0)) for s in steps], dtype=np.float32)
    reactions = np.array(
        [
            [
                float(s.get("reaction_x", 0.0)),
                float(s.get("reaction_y", 0.0)),
                float(s.get("reaction_z", 0.0)),
                0.0,
                0.0,
                0.0,
            ]
            for s in steps
        ],
        dtype=np.float32,
    )

    u_field = np.zeros((n_steps, gdl), dtype=np.float32)
    intf_res = np.zeros((n_steps, n_intf, 3), dtype=np.float32)
    intf_mom = np.zeros((n_steps, n_intf, 3), dtype=np.float32)

    for i, s in enumerate(steps):
        u_arr = s.get("u")
        if u_arr is not None:
            u_field[i, : len(u_arr)] = np.asarray(u_arr, dtype=np.float32)

        forces = s.get("interface_resultants")
        if forces is not None:
            intf_res[i] = np.asarray(forces, dtype=np.float32)

        moments = s.get("interface_moments")
        if moments is not None:
            intf_mom[i] = np.asarray(moments, dtype=np.float32)

    arrays["steps/step_index"] = step_index
    arrays["steps/load_factor"] = load_factor
    arrays["steps/displacement"] = displacement
    arrays["steps/reactions"] = reactions
    arrays["fields/U"] = u_field
    arrays["fields/interface_resultants"] = intf_res
    arrays["fields/interface_moments"] = intf_mom

    # Project node displacements if requested
    if include_node_displacements and n_steps > 0:
        node_disps = np.zeros((n_steps, n_nodes, 3), dtype=np.float32)
        for i, s in enumerate(steps):
            u_arr = s.get("u")
            if u_arr is not None:
                rows = compute_node_displacements(model, u_arr, only_quad_nodes=True)
                for j, row in enumerate(rows):
                    if j < n_nodes:
                        node_disps[i, j, 0] = row.ux
                        node_disps[i, j, 1] = row.uy
                        node_disps[i, j, 2] = row.uz
        arrays["fields/node_displacements"] = node_disps

    # 3. Stage-End Spring Constitutive State (Snapshots)
    runtime = ModelManager.hysteretic_batch_for(model)
    if runtime is not None and getattr(runtime, "active", False):
        try:
            arrays["springs/runtime_arrays/all_resultant_forces"] = runtime.all_resultant_forces()
            arrays["springs/runtime_arrays/all_bending_moments"] = runtime.all_bending_moments()
            if getattr(runtime, "quad_state", None) is not None:
                arrays["springs/runtime_arrays/quad_state"] = np.asarray(runtime.quad_state, dtype=np.float32)
            if getattr(runtime, "coulomb_state", None) is not None:
                arrays["springs/runtime_arrays/coulomb_state"] = np.asarray(runtime.coulomb_state, dtype=np.float32)

            # Transverse trial stresses & phases
            if getattr(runtime, "trial", None) is not None and runtime.trial.shape[0] > 0:
                stress = runtime.trial[:, 6].astype(np.float32)
                phase = runtime.trial[:, 8].astype(np.int8)
                arrays["springs/transverse_stress"] = stress
                arrays["springs/transverse_phase"] = phase

            # Sliding trial stresses & phases
            if getattr(runtime, "coulomb_state", None) is not None and runtime.coulomb_state.shape[0] > 0:
                # Coulomb force column is 6, phase is 8
                slid_stress = runtime.coulomb_state[:, 6].astype(np.float32)
                slid_phase = runtime.coulomb_state[:, 8].astype(np.int8)
                arrays["springs/sliding_stress"] = slid_stress
                arrays["springs/sliding_phase"] = slid_phase
        except Exception:
            pass

    return arrays


def _write_hdf5(filepath: Path, arrays: Mapping[str, np.ndarray]) -> None:
    import h5py

    with h5py.File(filepath, "w") as f:
        for key, arr in arrays.items():
            f.create_dataset(key, data=arr, compression="gzip", compression_opts=4)

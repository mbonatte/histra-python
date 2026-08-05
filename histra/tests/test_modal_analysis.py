from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import scipy.sparse as sp

from histra.elements.quad import Quad
from histra.io.hr_loader import load_model
from histra.model.masonry_material import MasonryMaterial
from histra.model.model import Collections, Model
from histra.model.node import Node
from histra.solver.mass_matrix import (
    GRAVITY_ACCELERATION,
    assemble_mass_matrix,
    build_translational_pseudovectors,
    compute_quad_local_mass,
)
from histra.solver.modal import _subspace_modes, solve_modal_analysis
from histra.types.afference_entry import AfferenceEntry
from histra.types.point import Point


def _single_quad_model() -> Model:
    collections = Collections()
    collections.nodes = {
        1: Node(key=1, point=Point(-0.5, 0.0, 0.0)),
        2: Node(key=2, point=Point(0.5, 0.0, 0.0)),
        3: Node(key=3, point=Point(0.5, 1.0, 0.0)),
        4: Node(key=4, point=Point(-0.5, 1.0, 0.0)),
    }
    collections.materials[1] = MasonryMaterial(key=1, w=2.0)
    quad = Quad(
        key=1,
        node_keys=[1, 2, 3, 4],
        length=[1.0, 1.0, 1.0, 1.0],
        sin=[1.0, 1.0, 1.0, 1.0],
        cos=[0.0, 0.0, 0.0, 0.0],
        thickness=[0.2, 0.2, 0.2, 0.2],
        normal=[Point(0.0, 0.0, 1.0) for _ in range(4)],
        g=Point(0.0, 0.5, 0.0),
        material_key=1,
        reference_e1=(1.0, 0.0, 0.0),
        reference_e2=(0.0, 1.0, 0.0),
        reference_e3=(0.0, 0.0, 1.0),
    )
    quad.aff = [[AfferenceEntry(index + 1, 1.0)] for index in range(7)]
    collections.quads[quad.key] = quad
    return Model(
        gdl=7,
        is_locked=True,
        mass_matrix_type="Lumped",
        collections=collections,
    )


def test_quad_mass_matches_physical_translational_mass() -> None:
    model = _single_quad_model()
    quad = model.collections.quads[1]

    local = compute_quad_local_mass(quad, model)

    expected_mass = 1.0 * 1.0 * 0.2 * 2.0 / GRAVITY_ACCELERATION
    assert local.shape == (7, 7)
    assert np.allclose(local, local.T, rtol=0.0, atol=1.0e-15)
    assert local[0, 0] == pytest.approx(expected_mass, rel=1.0e-12)
    assert local[1, 1] == pytest.approx(expected_mass, rel=1.0e-12)
    assert local[2, 2] == pytest.approx(expected_mass, rel=1.0e-12)


def test_global_mass_preserves_active_csharp_consistent_behavior() -> None:
    model = _single_quad_model()

    assembly = assemble_mass_matrix(model)
    directions, mass_directions, totals = build_translational_pseudovectors(
        model, assembly.matrix
    )

    assert assembly.requested_type == "Lumped"
    assert assembly.effective_type.startswith("Consistent")
    assert assembly.matrix.shape == (7, 7)
    assert np.allclose(directions[:3], np.eye(3))
    assert np.allclose(mass_directions, assembly.matrix @ directions)
    expected_mass = 0.4 / GRAVITY_ACCELERATION
    assert np.allclose(totals, expected_mass, rtol=1.0e-12, atol=0.0)


def test_generalized_eigensolver_returns_lowest_modes() -> None:
    stiffness = sp.diags([4.0, 18.0, 48.0], format="csc")
    mass = sp.diags([1.0, 2.0, 3.0], format="csc")

    values, vectors = _subspace_modes(
        stiffness,
        mass,
        2,
        csharp_tolerance=1.0e-8,
        max_iterations=1000,
    )

    assert np.allclose(values, [4.0, 9.0], rtol=1.0e-10)
    assert np.allclose(
        np.einsum("ij,ij->j", vectors, mass @ vectors),
        np.ones(2),
        rtol=1.0e-10,
    )


def test_hrx_loader_reads_modal_configuration(tmp_path: Path) -> None:
    hrx = tmp_path / "modal.hrx"
    hrx.write_text(
        """<?xml version='1.0' encoding='utf-8'?>
<HiStrA version='2026.1.0' GDL='3' IsLocked='true'>
  <AdvancedOptionsDefault InterfaceNrow='3' InterfaceImax='40' MassMatrixType='Lumped' />
  <Analysis Key='30' Name='Modal_-1' AnalysisType='5' InitialAnalysisKey='-100'
    NumberOfEigenModes='10' NumberOfLanczosEigenVectors='5'
    ModalProcedure='InverseIterations' ModalConvergenceCriteria='EigenVector'
    ConvergenceTolerance='0.04' MaxIterations='20' />
</HiStrA>
""",
        encoding="utf-8",
    )

    model = load_model(hrx)
    analysis = model.collections.analyses[30]

    assert model.mass_matrix_type == "Lumped"
    assert analysis.number_of_eigen_modes == 10
    assert analysis.number_of_lanczos_eigen_vectors == 5
    assert analysis.modal_procedure == "InverseIterations"
    assert analysis.modal_convergence_criteria == "EigenVector"


@pytest.mark.integration
def test_ersino_modal_regression_against_csharp_results() -> None:
    hrx_value = os.environ.get("HISTRA_MODAL_HRX")
    results_value = os.environ.get("HISTRA_MODAL_RESULTS")
    if not hrx_value or not results_value:
        pytest.skip("Set HISTRA_MODAL_HRX and HISTRA_MODAL_RESULTS for the real-file regression.")

    model = load_model(hrx_value)
    analysis = model.collections.analyses[30]
    result = solve_modal_analysis(model, analysis)

    with sqlite3.connect(f"file:{Path(results_value)}?mode=ro", uri=True) as connection:
        reference_frequency = np.asarray(
            [
                row[0]
                for row in connection.execute(
                    "SELECT Fn FROM ModalValues WHERE AnalysisKey=30 ORDER BY Step"
                )
            ],
            dtype=float,
        )
        reference_total = float(
            connection.execute(
                "SELECT MTotX FROM ModalValues WHERE AnalysisKey=30 ORDER BY Step LIMIT 1"
            ).fetchone()[0]
        )
        reference_shapes = np.zeros((model.gdl, 10), dtype=float)
        for step, dof, value in connection.execute(
            "SELECT Step, Dof, Val FROM ModalShapeValues "
            "WHERE AnalysisKey=30 ORDER BY Step, Dof"
        ):
            reference_shapes[int(dof), int(step) - 1] = float(value)

    assert result.dof_count == 14252
    assert result.converged_modes == 10
    assert result.modes[0].total_mass_x == pytest.approx(reference_total, rel=3.0e-8)
    # Exact port of Matrix.SubSpaceIteration2, including .NET Random(0) and the
    # source convergence test, reproduces all stored C# eigenvalues.
    assert np.allclose(result.frequencies, reference_frequency, rtol=3.0e-8)

    mass = assemble_mass_matrix(model).matrix
    modal_correlations = np.abs(result.mode_shapes.T @ (mass @ reference_shapes))
    assert np.all(np.diag(modal_correlations) > 0.9999999)

    # The source's eigenvalue-change criterion does not enforce a small
    # eigen-residual; the tenth stored mode intentionally retains this behavior.
    assert max(mode.residual_norm for mode in result.modes) < 0.12

"""Regression tests for the chained Vert -> Live Load ArcLength benchmark."""
from __future__ import annotations

import copy
import gc
import importlib
import os
from pathlib import Path

import numpy as np
import pytest
import scipy.sparse as sp

from histra.io.hr_loader import load_model
from histra.io.results_reader import read_analysis_metadata, read_global_displacements
from histra.solver.arc_length import ArcLength
from histra.solver.assembler import assemble_load_vector
from histra.solver.line_search import LineSearch
from histra.solver.solve import solve_static_nonlinear
from histra.solver.output_projection import model_point_displacement
from histra.springs.coulomb03 import SpringCoulomb03
from histra.types.linear_system import LinearSystem

ROOT = Path(__file__).resolve().parents[1]
HRX = ROOT / "model-live" / "model.hrx"
RESULTS = ROOT / "model-live" / "model.Results"


def test_live_model_entities_and_reference_steps_are_detected():
    model = load_model(HRX)
    analysis = model.collections.analyses[22]
    metadata = read_analysis_metadata(RESULTS, 22)

    assert analysis.name == "LiveLoad_1"
    assert analysis.integration_method == "ArcLength"
    assert analysis.initial_analysis_key == 1
    assert analysis.initial_combination_analysis_key == 1
    assert analysis.active_model_points == {1: False, 2: True}
    assert model.collections.model_points[2].element_type == "Quad"
    assert model.collections.model_points[2].element_key == 9
    assert len(model.collections.line_loads) == 1
    assert metadata.steps_by_combination[1] == tuple(range(88))
    assert metadata.last_step_by_combination[1] == 87


def test_live_line_load_generates_expected_generalized_vector():
    model = load_model(HRX)
    vector = assemble_load_vector(model, 22, 1)

    nonzero = np.flatnonzero(np.abs(vector) > 1.0e-12)
    assert nonzero.tolist() == [23, 25, 27]
    # The assigned line is 288 units long with load intensity 0.01.
    assert vector[23] == pytest.approx(-2.879999876022339, abs=1.0e-12)
    assert vector[25] == pytest.approx(12.062898635864258, abs=1.0e-12)
    assert vector[27] == pytest.approx(-2.3925376808620058e-05, abs=1.0e-15)
    assert np.all(np.isfinite(vector))


def test_coulomb_negative_envelope_uses_csharp_maximum_slope():
    spring = SpringCoulomb03(
        rot1n=-1.0,
        mom1n=-9.0,
        rot2n=-2.0,
        mom2n=-13.0,
        rot3n=-3.0,
        mom3n=-15.0,
    )
    spring._set_envelope()
    assert (spring.e1n, spring.e2n, spring.e3n) == pytest.approx((9.0, 4.0, 2.0))
    assert spring.eun == pytest.approx(9.0)


def test_hidden_initial_interpolated_base_search_preserves_arc_length_correction():
    ls = LinearSystem(3)
    combined = np.array([0.25, -0.5, 0.75])
    raw_newton = np.array([10.0, 20.0, 30.0])
    ls.set_x_vector(combined)

    eta = LineSearch().search(None, None, ls, None, None, raw_newton, 1.0, 0.5)

    assert eta == 1.0
    assert np.array_equal(ls.x, combined)


def test_projected_control_point_uses_compact_reported_coordinate_weights():
    model = load_model(HRX)
    analysis = copy.deepcopy(model.collections.analyses[22])
    analysis.arc_length_procedure = "ProjectedControlPoint"
    analysis.master_point = 2
    integrator = ArcLength()
    integrator._configure_projected_control(model, analysis)
    vector = np.linspace(-1.0e-3, 1.0e-3, model.gdl)
    point = model.collections.model_points[2]
    reported = model_point_displacement(model.collections, point, vector)
    direction = np.asarray((analysis.dir_x, analysis.dir_y, analysis.dir_z))

    assert integrator._selected(vector)[0] == pytest.approx(
        float(np.dot(reported, direction)), abs=2.0e-9
    )
    assert integrator._projected_control_indices.ndim == 1
    assert integrator._projected_control_weights.ndim == 1
    assert integrator._projected_control_indices.size < 100
    assert (
        integrator._projected_control_indices.nbytes
        + integrator._projected_control_weights.nbytes
    ) < 2_000
    assert all(value is not model.collections for value in integrator.__dict__.values())


def test_csharp_control_point_selection_remains_dof_based():
    integrator = ArcLength()
    integrator._dofs = np.asarray((1, 3), dtype=int)
    vector = np.asarray((10.0, 20.0, 30.0, 40.0))

    assert np.array_equal(integrator._selected(vector), np.asarray((20.0, 40.0)))


def test_linear_system_reuses_and_invalidates_sparse_factorization():
    ls = LinearSystem(2)
    ls.k = sp.csc_matrix(np.array([[4.0, 1.0], [1.0, 3.0]]))
    ls.solve(rhs=np.array([1.0, 2.0]))
    factor = ls._factorization
    first = ls.x.copy()

    ls.solve(rhs=np.array([2.0, 4.0]))
    assert ls._factorization is factor
    assert ls.x == pytest.approx(2.0 * first)

    ls.set_k(0, 0, 5.0)
    assert ls._factorization is None
    ls.solve(rhs=np.array([1.0, 2.0]))
    assert ls._factorization is not factor


def test_solver_restores_callers_gc_setting(monkeypatch):
    solve_module = importlib.import_module("histra.solver.solve")
    observed: list[bool] = []

    def fake_impl(*args, **kwargs):
        observed.append(gc.isenabled())
        return 0, []

    monkeypatch.setattr(solve_module, "_solve_static_nonlinear_impl", fake_impl)
    was_enabled = gc.isenabled()
    if not was_enabled:
        gc.enable()
    try:
        assert solve_module.solve_static_nonlinear(None, None) == (0, [])
        assert observed == [False]
        assert gc.isenabled()
    finally:
        if not was_enabled:
            gc.disable()


def test_first_live_load_step_reproduces_csharp(monkeypatch):
    original_commit = ArcLength.commit

    def stop_after_first(self, model, analysis, disp, dof, changed):
        original_commit(self, model, analysis, disp, dof, changed)
        return True

    monkeypatch.setattr(ArcLength, "commit", stop_after_first)
    model = load_model(HRX)
    analysis = copy.deepcopy(model.collections.analyses[22])
    code, rows = solve_static_nonlinear(model, analysis, 1, results_path=RESULTS)

    assert code == 0
    assert len(rows) == 1
    assert rows[0]["status"] == "OK"
    assert rows[0]["iterations"] == 54
    reference = read_global_displacements(RESULTS, 22, 1, 1, model_or_hrx=model)
    difference = rows[0]["u"] - reference
    assert np.linalg.norm(difference) / np.linalg.norm(reference) <= 1.0e-4
    assert np.max(np.abs(difference)) <= 3.1e-6
    assert np.all(np.isfinite(rows[0]["u"]))


@pytest.mark.skipif(
    os.environ.get("HISTRA_RUN_LIVE_BENCHMARK") != "1",
    reason="set HISTRA_RUN_LIVE_BENCHMARK=1 for the 87-step ArcLength benchmark",
)
def test_complete_live_load_reference_path():
    model = load_model(HRX)
    analysis = copy.deepcopy(model.collections.analyses[22])
    code, rows = solve_static_nonlinear(model, analysis, 1, results_path=RESULTS)

    committed = [row for row in rows if row["status"] == "OK"]
    failed = [row for row in rows if row["status"] != "OK"]
    assert code == -3
    assert [row["step"] for row in committed] == list(range(1, 88))
    assert [row["step"] for row in failed] == [88]
    for row in committed:
        reference = read_global_displacements(
            RESULTS, 22, 1, row["step"], model_or_hrx=model
        )
        relative = np.linalg.norm(row["u"] - reference) / np.linalg.norm(reference)
        assert relative <= 1.0e-4
        assert np.all(np.isfinite(row["u"]))


def test_arc_length_commit_uses_displacement_relative_to_predecessor(monkeypatch):
    """C# measures the graph displacement at the master model point.

    ``GetValueGraphAnalysis`` projects the master model point's displacement on
    the analysis direction; ``StaticNonLinearAnalysis`` subtracts the
    predecessor graph displacement before calling the integrator's Commit().
    Model-live's LiveLoad_1 ships with master point 1 inactive, so the
    activation below is required for a meaningful relative-displacement check.
    """
    captured: list[float] = []
    original_commit = ArcLength.commit

    def capture_and_stop(self, model, analysis, displacement, dof, changed):
        captured.append(float(displacement))
        original_commit(self, model, analysis, displacement, dof, changed)
        return True

    monkeypatch.setattr(ArcLength, "commit", capture_and_stop)
    model = load_model(HRX)
    analysis = copy.deepcopy(model.collections.analyses[22])
    analysis.active_model_points = {1: True, 2: True}
    predecessor = read_global_displacements(
        RESULTS,
        analysis.initial_analysis_key,
        analysis.initial_combination_analysis_key,
        model_or_hrx=model,
        size=model.gdl,
    )
    point = model.collections.model_points[int(analysis.master_point)]
    predecessor_vector = model_point_displacement(model.collections, point, predecessor)
    predecessor_displacement = -float(predecessor_vector[2])  # direction (0,0,-1)

    code, rows = solve_static_nonlinear(model, analysis, 1, results_path=RESULTS)

    assert code == 0
    assert len(rows) == 1
    assert captured == pytest.approx(
        [rows[0]["displacement"] - predecessor_displacement]
    )
    assert abs(captured[0] - rows[0]["displacement"]) > 1.0e-12


def test_arc_length_commit_displacement_is_zero_for_inactive_master_point(monkeypatch):
    """C# leaves the graph displacement at 0 when the master point is inactive.

    Model-live's LiveLoad_1 master point (key 1) is inactive, so C# can never
    reach its TargetDisplacement and the analysis runs until another exit.
    """
    captured: list[float] = []
    original_commit = ArcLength.commit

    def capture_and_stop(self, model, analysis, displacement, dof, changed):
        captured.append(float(displacement))
        original_commit(self, model, analysis, displacement, dof, changed)
        return True

    monkeypatch.setattr(ArcLength, "commit", capture_and_stop)
    model = load_model(HRX)
    analysis = copy.deepcopy(model.collections.analyses[22])

    code, rows = solve_static_nonlinear(model, analysis, 1, results_path=RESULTS)

    assert code == 0
    assert len(rows) == 1
    assert captured == pytest.approx([0.0])
    assert rows[0]["displacement"] == pytest.approx(0.0)


def test_graph_displacement_projects_active_master_model_point():
    """The committed-step displacement is the master model-point projection."""
    model = load_model(HRX)
    analysis = copy.deepcopy(model.collections.analyses[1])  # Vert: master 1 active
    code, rows = solve_static_nonlinear(model, analysis, 1, max_committed_steps=1)

    assert code == 0
    assert len(rows) == 1
    point = model.collections.model_points[int(analysis.master_point)]
    vector = model_point_displacement(model.collections, point, rows[0]["u"])
    expected = -float(vector[2])  # direction (0, 0, -1)
    assert rows[0]["displacement"] == pytest.approx(expected)

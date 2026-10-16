"""Empirical adversarial stress test suite challenging live .NET MicroRunner vs Python.

Covers:
1. Gauss quadrature with edge-case orders (N=2..10) and boundary values.
2. Arc-Length Crisfield solver with complex roots (discriminant < 0), zero bar, and extreme trial states.
3. Sutherland-Hodgman polygon clipping with non-overlapping, touching, orthogonal, and identical quadrilaterals.
4. Polygon area with collinear points, degenerate quadrilaterals, and high-magnitude coordinates.
5. Coulomb friction with extreme normal compressive/tensile forces, zero cohesion, high friction angles, and cyclic slip reversal.
6. Hysteretic and multilinear springs with large cyclic plastic strains and pinching.
"""
from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
import pytest

from histra.preprocessing.csharp_fibre_geometry import _csharp_polygon_area
from histra.preprocessing.contact_geometry import _coplanar_quad_intersection_prechecked
from histra.solver.arc_length import ArcLength
from histra.springs.coulomb03 import SpringCoulomb03
from histra.springs.hysteretic import SpringHysteretic
from histra.tests.csharp_runner_client import CSharpRunnerClient, get_csharp_runner


@pytest.fixture
def csharp_runner() -> CSharpRunnerClient:
    return get_csharp_runner()


# ==============================================================================
# Scope 1: Gauss Quadrature Stress Testing
# ==============================================================================

def test_adversarial_gauss_quadrature_orders(csharp_runner: CSharpRunnerClient):
    """Stress test Gauss-Legendre quadrature across orders N=2..10 against NumPy leggauss."""
    for n in range(2, 11):
        data = csharp_runner.gauss_quadrature(n)
        assert data["order"] == n

        cs_z = np.asarray(data["z"], dtype=np.float64)
        cs_w = np.asarray(data["w"], dtype=np.float64)
        py_z, py_w = np.polynomial.legendre.leggauss(n)

        # For order 2: exact IEEE-754 bit-for-bit equality
        if n == 2:
            for val_py, bits_cs in zip(py_z, data["z_bits"]):
                assert int(np.asarray([val_py], dtype=np.float64).view(np.int64)[0]) == int(bits_cs)
            for val_py, bits_cs in zip(py_w, data["w_bits"]):
                assert int(np.asarray([val_py], dtype=np.float64).view(np.int64)[0]) == int(bits_cs)

        # For all N=2..10: agree within theoretical numerical precision bounds (<= 1e-15)
        np.testing.assert_allclose(cs_z, py_z, atol=1e-15, rtol=1e-15)
        np.testing.assert_allclose(cs_w, py_w, atol=1e-15, rtol=1e-15)

        # Symmetry invariants
        np.testing.assert_allclose(cs_z, -cs_z[::-1], atol=1e-15)
        np.testing.assert_allclose(cs_w, cs_w[::-1], atol=1e-15)
        assert abs(np.sum(cs_w) - 2.0) <= 1e-15


def test_adversarial_gauss_quadrature_boundary_exceptions(csharp_runner: CSharpRunnerClient):
    """Verify that unsupported Gauss orders fail closed with ArgumentException."""
    # Boundary failure cases
    for invalid_n in (1, 0, -1, 26):
        with pytest.raises(RuntimeError) as exc_info:
            csharp_runner.gauss_quadrature(invalid_n)
        err_msg = str(exc_info.value).lower()
        assert "disponibile" in err_msg or "overflow" in err_msg or "u00e8" in err_msg

    # Upper boundary valid case (N=25 is the max supported in C#)
    res_25 = csharp_runner.gauss_quadrature(25)
    assert res_25["order"] == 25
    assert len(res_25["z"]) == 25


# ==============================================================================
# Scope 2: Arc-Length Crisfield Solver Stress Testing
# ==============================================================================

def _run_python_arc_length(case: dict) -> tuple[int, ArcLength]:
    arc = ArcLength(constraint_mode="csharp")
    arc._alpha2 = float(case["alpha2"])
    hat_vec = case["hat"] if isinstance(case["hat"], list) else [float(case["hat"])]
    bar_vec = case["bar"] if isinstance(case["bar"], list) else [float(case["bar"])]
    step_vec = case["step"] if isinstance(case["step"], list) else [float(case["step"])]

    arc._phat = np.array(hat_vec, dtype=np.float64)
    arc._delta_u_step = np.array(step_vec, dtype=np.float64)
    arc._dofs = np.arange(len(hat_vec), dtype=int)
    arc.u = np.zeros(len(hat_vec), dtype=np.float64)
    arc.state.combination = 1
    arc.update_ptarget = lambda *args: None
    arc.apply_load_domain = lambda *args: None

    class MockLinearSystem:
        def __init__(self, val):
            self.matrix_version = 1
            self.x = np.array(val, dtype=np.float64)

        def solve(self, rhs):
            self.x = rhs.copy()

        def set_x_vector(self, values):
            self.x = values.copy()

    with patch("histra.solver.arc_length.ModelManager.update_domain"):
        code = arc.update(object(), SimpleNamespace(ls=MockLinearSystem(bar_vec)), object())
    return code, arc


def test_adversarial_arc_length_complex_roots_fallback(csharp_runner: CSharpRunnerClient):
    """Stress test Crisfield constraint when discriminant b^2 - 4ac < 0 (complex roots)."""
    # Multidimensional state where b = 0, c > 0 -> discriminant is strictly negative
    case = {
        "alpha2": 0.0,
        "hat": [1.0, 1.0],
        "step": [1.0, 2.0],
        "bar": [-3.0, 0.0],
    }
    cs_res = csharp_runner.arc_length(case)
    py_code, arc = _run_python_arc_length(case)

    assert py_code == cs_res["code"] == 0
    py_lambda_bits = int(np.asarray([arc._last_delta_lambda], dtype=np.float64).view(np.int64)[0])
    assert py_lambda_bits == cs_res["lambda_bits"]

    for i in range(len(case["hat"])):
        py_du_bit = int(np.asarray([arc._last_delta_u[i]], dtype=np.float64).view(np.int64)[0])
        cs_du_bit = int(np.asarray([cs_res["delta_u"][i]], dtype=np.float64).view(np.int64)[0])
        assert py_du_bit == cs_du_bit


def test_adversarial_arc_length_zero_bar_and_extreme_states(csharp_runner: CSharpRunnerClient):
    """Stress test zero bar displacement (c = 0) and extreme trial coordinates."""
    # 1. Zero bar displacement: c = 0
    case_zero_bar = {
        "alpha2": 0.0,
        "hat": [2.0, 1.5],
        "step": [0.1, -0.05],
        "bar": [0.0, 0.0],
    }
    cs_zero = csharp_runner.arc_length(case_zero_bar)
    code_zero, arc_zero = _run_python_arc_length(case_zero_bar)
    assert code_zero == cs_zero["code"] == 0
    assert arc_zero._last_delta_lambda == cs_zero["delta_lambda"] == 0.0
    np.testing.assert_array_equal(arc_zero._last_delta_u, cs_zero["delta_u"])

    # 2. Large displacements (1e5..1e6 magnitude)
    case_large = {
        "alpha2": 100.0,
        "hat": [1e5, 2e5],
        "step": [1e6, -1e6],
        "bar": [100.0, -200.0],
    }
    cs_large = csharp_runner.arc_length(case_large)
    code_large, arc_large = _run_python_arc_length(case_large)
    assert code_large == cs_large["code"] == 0
    py_lambda_bits = int(np.asarray([arc_large._last_delta_lambda], dtype=np.float64).view(np.int64)[0])
    assert py_lambda_bits == cs_large["lambda_bits"]

    # 3. Degenerate zero reference load with zero alpha2 -> error code -10
    case_zero_ref = {
        "alpha2": 0.0,
        "hat": [0.0, 0.0],
        "step": [0.1, 0.1],
        "bar": [0.01, 0.01],
    }
    cs_zero_ref = csharp_runner.arc_length(case_zero_ref)
    code_zero_ref, _ = _run_python_arc_length(case_zero_ref)
    assert code_zero_ref == cs_zero_ref["code"] == -10


# ==============================================================================
# Scope 3: Sutherland-Hodgman Polygon Clipping Stress Testing
# ==============================================================================

def test_adversarial_polygon_clipping_topologies(csharp_runner: CSharpRunnerClient):
    """Stress test Sutherland-Hodgman polygon clipping under diverse topological intersections."""
    # 1. Non-overlapping disjoint quadrilaterals
    p_non1 = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
    p_non2 = [[2.0, 0.0, 0.0], [3.0, 0.0, 0.0], [3.0, 1.0, 0.0], [2.0, 1.0, 0.0]]
    cs_non = csharp_runner.polygon_clipping(p_non1, p_non2, include_extreme_nodes=True)
    py_non = _coplanar_quad_intersection_prechecked(
        np.array(p_non1), np.array(p_non2), np.array([0.0, 0.0, 1.0]), node_tolerance=1.0
    )
    assert cs_non["count"] == 0
    assert cs_non["code"] == 0
    assert py_non is None

    # 2. Touching edge (zero contact area, sliver rejected)
    p_edge1 = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
    p_edge2 = [[1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [2.0, 1.0, 0.0], [1.0, 1.0, 0.0]]
    cs_edge = csharp_runner.polygon_clipping(p_edge1, p_edge2, include_extreme_nodes=True)
    py_edge = _coplanar_quad_intersection_prechecked(
        np.array(p_edge1), np.array(p_edge2), np.array([0.0, 0.0, 1.0]), node_tolerance=1.0
    )
    assert cs_edge["count"] == 0
    assert py_edge is None

    # 3. Touching vertex (point contact, area = 0)
    p_vert1 = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
    p_vert2 = [[1.0, 1.0, 0.0], [2.0, 1.0, 0.0], [2.0, 2.0, 0.0], [1.0, 2.0, 0.0]]
    cs_vert = csharp_runner.polygon_clipping(p_vert1, p_vert2, include_extreme_nodes=True)
    py_vert = _coplanar_quad_intersection_prechecked(
        np.array(p_vert1), np.array(p_vert2), np.array([0.0, 0.0, 1.0]), node_tolerance=1.0
    )
    assert cs_vert["count"] == 0
    assert py_vert is None

    # 4. Orthogonal overlapping quadrilaterals (cross intersection)
    p_ortho1 = [[0.0, 0.0, 0.0], [4.0, 0.0, 0.0], [4.0, 2.0, 0.0], [0.0, 2.0, 0.0]]
    p_ortho2 = [[1.0, -1.0, 0.0], [3.0, -1.0, 0.0], [3.0, 3.0, 0.0], [1.0, 3.0, 0.0]]
    cs_ortho = csharp_runner.polygon_clipping(p_ortho1, p_ortho2, include_extreme_nodes=True)
    py_ortho = _coplanar_quad_intersection_prechecked(
        np.array(p_ortho1), np.array(p_ortho2), np.array([0.0, 0.0, 1.0]), node_tolerance=1.0
    )
    assert cs_ortho["count"] == 4
    assert cs_ortho["code"] == 4
    assert py_ortho is not None
    py_ortho_area = _csharp_polygon_area(np.asarray(py_ortho, dtype=np.float32))
    assert int(np.asarray([py_ortho_area], dtype=np.float32).view(np.int32)[0]) == cs_ortho["area_single_bits"]

    # 5. Identical coincident quadrilaterals
    p_ident1 = [[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [2.0, 2.0, 0.0], [0.0, 2.0, 0.0]]
    p_ident2 = [[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [2.0, 2.0, 0.0], [0.0, 2.0, 0.0]]
    cs_ident = csharp_runner.polygon_clipping(p_ident1, p_ident2, include_extreme_nodes=True)
    py_ident = _coplanar_quad_intersection_prechecked(
        np.array(p_ident1), np.array(p_ident2), np.array([0.0, 0.0, 1.0]), node_tolerance=1.0
    )
    assert cs_ident["count"] == 4
    assert cs_ident["code"] == 3
    assert py_ident is not None
    py_ident_area = _csharp_polygon_area(np.asarray(py_ident, dtype=np.float32))
    assert int(np.asarray([py_ident_area], dtype=np.float32).view(np.int32)[0]) == cs_ident["area_single_bits"]


# ==============================================================================
# Scope 4: Polygon Area Calculation Stress Testing
# ==============================================================================

def test_adversarial_polygon_area_geometry(csharp_runner: CSharpRunnerClient):
    """Stress test 3D shoelace polygon area with high magnitudes and collinear edge points."""
    # 1. High-magnitude coordinates: base offset 1e6 mm
    pts_high = [
        [1e6, 1e6, 0.0],
        [1e6 + 2.0, 1e6, 0.0],
        [1e6 + 2.0, 1e6 + 3.0, 0.0],
        [1e6, 1e6 + 3.0, 0.0],
    ]
    cs_high = csharp_runner.polygon_area(points=pts_high)
    py_high = _csharp_polygon_area(np.asarray(pts_high, dtype=np.float32))
    assert abs(cs_high["area"] - 6.0) < 1e-6
    assert abs(py_high - 6.0) < 1e-6
    # Exact 32-bit single bit representation match
    py_bits = int(np.asarray([py_high], dtype=np.float32).view(np.int32)[0])
    assert py_bits == cs_high["area_single_bits"]

    # 2. Polygon with a collinear edge vertex (pentagon where vertex 3 lies on top edge)
    pts_collinear_edge = [
        [0.0, 0.0, 0.0],
        [2.0, 0.0, 0.0],
        [2.0, 2.0, 0.0],
        [1.0, 2.0, 0.0],
        [0.0, 2.0, 0.0],
    ]
    cs_col_edge = csharp_runner.polygon_area(points=pts_collinear_edge)
    py_col_edge = _csharp_polygon_area(np.asarray(pts_collinear_edge, dtype=np.float32))
    assert abs(cs_col_edge["area"] - 4.0) < 1e-6
    assert abs(py_col_edge - 4.0) < 1e-6
    py_col_bits = int(np.asarray([py_col_edge], dtype=np.float32).view(np.int32)[0])
    assert py_col_bits == cs_col_edge["area_single_bits"]

    # 3. Collinear base points: both C# and Python fail closed
    pts_collinear_base = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [3.0, 0.0, 0.0]]
    with pytest.raises(RuntimeError):
        # C# produces NaN which fails JSON serialization
        csharp_runner.polygon_area(points=pts_collinear_base)
    with pytest.raises(ZeroDivisionError):
        # Python raises ZeroDivisionError on 0-norm vector
        _csharp_polygon_area(np.asarray(pts_collinear_base, dtype=np.float32))


# ==============================================================================
# Scope 5: Coulomb Friction Stress Testing
# ==============================================================================

def test_adversarial_coulomb_friction_cyclic_and_extremes(csharp_runner: CSharpRunnerClient):
    """Stress test Coulomb friction with extreme normal forces and cyclic slip reversal."""
    k = 2000.0
    cohesion = 1.0
    mu = 0.5
    normal_force = 2.0
    ur = 0.05
    ktang = 0.0
    plastic_strain_ratio = 0.0

    # 1. 10-step cyclic slip history
    strains = [0.0005, 0.001, 0.002, 0.001, 0.0, -0.001, -0.002, -0.001, 0.0, 0.0015]

    cs_res = csharp_runner.spring_coulomb(
        k=k,
        cohesion=cohesion,
        mu=mu,
        ur=ur,
        normal_force=normal_force,
        strains=strains,
        commit_each_step=True,
    )

    # Initial setup matching C# Set2
    mom1p = max(1e-9, cohesion + mu * 0.0)
    rot1p = mom1p / k
    rot2p = max(plastic_strain_ratio, rot1p * 1.0001)
    mom2p = mom1p + ktang * (rot2p - rot1p)
    rot3p = max(ur, rot2p * 1.0001)
    mom3p = 0.0

    py_spring = SpringCoulomb03(k=k, cohesion=cohesion, mu=mu, ur=ur, sub_law="Coulomb")
    py_spring.mom1p = mom1p
    py_spring.rot1p = rot1p
    py_spring.mom2p = mom2p
    py_spring.rot2p = rot2p
    py_spring.mom3p = mom3p
    py_spring.rot3p = rot3p
    py_spring.mom1n = -mom1p
    py_spring.rot1n = -rot1p
    py_spring.mom2n = -mom2p
    py_spring.rot2n = -rot2p
    py_spring.mom3n = -mom3p
    py_spring.rot3n = -rot3p
    py_spring._set_envelope()
    py_spring.revert_to_start()
    py_spring.revert_to_last_commit()
    py_spring._cstress_normal = normal_force
    py_spring._tstress_normal = normal_force

    py_bits = []
    for s in strains:
        py_spring.set_trial_strain(s)
        f = py_spring.get_force()
        py_spring.commit()
        py_bits.append(int(np.asarray([f], dtype=np.float64).view(np.int64)[0]))

    # Bit-for-bit exact match across all 10 cyclic loading steps
    for step_idx in range(len(strains)):
        assert py_bits[step_idx] == cs_res["force_bits"][step_idx], (
            f"Step {step_idx} cyclic slip mismatch: py={py_bits[step_idx]}, cs={cs_res['force_bits'][step_idx]}"
        )

    # 2. Extreme tensile normal force (N = -1000): shear capacity clamped to 0.0
    cs_tens = csharp_runner.spring_coulomb(
        k=k, cohesion=10.0, mu=0.5, ur=ur, normal_force=-1000.0,
        strains=[0.0001, 0.0005], commit_each_step=True
    )
    assert cs_tens["forces"] == [0.0, 0.0]

    # 3. High friction angle (mu = 10.0, phi = 84.3 deg)
    cs_high_mu = csharp_runner.spring_coulomb(
        k=k, cohesion=20.0, mu=10.0, ur=ur, normal_force=100.0,
        strains=[0.0001, 0.0005], commit_each_step=True
    )
    # Expected yield limit = 20.0 + 10.0 * 100.0 = 1020.0
    # At strain 0.0001, f = 2000.0 * 0.0001 = 0.2 (elastic)
    expected_f = 2000.0 * 0.0001
    assert abs(cs_high_mu["forces"][0] - expected_f) < 1e-12
    py_exp_bits = int(np.asarray([expected_f], dtype=np.float64).view(np.int64)[0])
    assert cs_high_mu["force_bits"][0] == py_exp_bits


# ==============================================================================
# Scope 6: Hysteretic and Multilinear Springs Stress Testing
# ==============================================================================

def test_adversarial_hysteretic_spring_cyclic_pinching(csharp_runner: CSharpRunnerClient):
    """Stress test SpringHysteretic with large cyclic plastic strains and pinching."""
    m1p, r1p = 20.0, 0.01
    m2p, r2p = 25.0, 0.03
    m3p, r3p = 0.0, 0.05
    m1n, r1n = -20.0, -0.01
    m2n, r2n = -25.0, -0.03
    m3n, r3n = 0.0, -0.05
    pinchXp, pinchYp = 0.2, 0.3
    pinchXn, pinchYn = 0.2, 0.3
    d1p = d2p = d1n = d2n = betap = betan = 0.0

    strains = [0.005, 0.015, 0.025, 0.010, 0.0, -0.015, -0.025, -0.005, 0.0, 0.020]

    cs_res = csharp_runner.spring_hysteretic(
        m1p=m1p, r1p=r1p, m2p=m2p, r2p=r2p, m3p=m3p, r3p=r3p,
        m1n=m1n, r1n=r1n, m2n=m2n, r2n=r2n, m3n=m3n, r3n=r3n,
        pinchXp=pinchXp, pinchYp=pinchYp, pinchXn=pinchXn, pinchYn=pinchYn,
        d1p=d1p, d2p=d2p, d1n=d1n, d2n=d2n, betap=betap, betan=betan,
        strains=strains,
        commit_each_step=True,
    )

    py_spring = SpringHysteretic(
        k=m1p / r1p,
        tensile_curve_type="LinearHardening",
        compressive_curve_type="LinearHardening",
        pinch_xp=pinchXp, pinch_yp=pinchYp,
        pinch_xn=pinchXn, pinch_yn=pinchYn,
        damfc1p=d1p, damfc2p=d2p, damfc1n=d1n, damfc2n=d2n,
        betap=betap, betan=betan,
        mom1p=m1p, rot1p=r1p, mom2p=m2p, rot2p=r2p, mom3p=m3p, rot3p=r3p,
        mom1n=m1n, rot1n=r1n, mom2n=m2n, rot2n=r2n, mom3n=m3n, rot3n=r3n,
    )
    py_spring._set_envelope()
    py_spring.revert_to_start()
    py_spring.revert_to_last_commit()

    py_bits = []
    for s in strains:
        py_spring.set_trial_strain(s)
        f = py_spring.get_force()
        py_spring.commit()
        py_bits.append(int(np.asarray([f], dtype=np.float64).view(np.int64)[0]))

    # Verify 100% bit-for-bit match at every single cyclic step
    for step_idx in range(len(strains)):
        assert py_bits[step_idx] == cs_res["force_bits"][step_idx], (
            f"Hysteretic pinching mismatch at step {step_idx}: py={py_bits[step_idx]}, cs={cs_res['force_bits'][step_idx]}"
        )


def test_adversarial_multilinear_backbone_plastic_cycles(csharp_runner: CSharpRunnerClient):
    """Stress test multilinear plastic spring cyclic evaluation against C# runner."""
    k = 1000.0
    backbone_u = [0.0, 0.01, 0.02, 0.03, 0.04]
    backbone_f = [0.0, 10.0, 15.0, 5.0, 0.0]
    strains = [0.005, 0.015, 0.025, 0.035, 0.010, 0.0, -0.01, -0.02, 0.0, 0.02]

    cs_res = csharp_runner.spring_multilinear(
        k=k,
        backbone_u=backbone_u,
        backbone_f=backbone_f,
        strains=strains,
        commit_each_step=True,
    )
    assert len(cs_res["forces"]) == len(strains)
    # Displacements tracked with machine precision
    np.testing.assert_allclose(cs_res["displacements"], strains, atol=1e-15)
    # Check that in elastic step 0, force is bit-exact
    expected_f0 = k * strains[0]
    py_bit0 = int(np.asarray([expected_f0], dtype=np.float64).view(np.int64)[0])
    assert cs_res["force_bits"][0] == py_bit0

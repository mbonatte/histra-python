"""Lateral Winkler units and independent massless-support modal checks."""
from pathlib import Path

import numpy as np
import pytest
import scipy.linalg
import scipy.sparse as sp

from histra import set_lateral_subgrade_moduli, solve_modal_analysis
from histra.preprocessing import prepare_model
from histra.preprocessing.errors import ModelPreparationError
from histra.solver.modal import _massless_support_modes, ModalAnalysisError
from histra.tests.test_foundation_side_restraints import _face_hrx


def test_massless_mode_matches_analytical_static_condensation():
    # Two massive DOFs coupled to a massless restraint spring.
    k = np.array([[12., -2., -4.], [-2., 8., -1.], [-4., -1., 7.]])
    m = np.diag([2., 3., 0.])
    condensed = k[:2, :2] - np.outer(k[:2, 2], k[2, :2]) / k[2, 2]
    expected = scipy.linalg.eigh(condensed, m[:2, :2])[0][0]
    values, modes = _massless_support_modes(sp.csc_matrix(k), sp.csc_matrix(m), 1, 1e-6, 1000, None)
    assert values[0] == pytest.approx(expected, rel=1e-10)
    np.testing.assert_allclose(k @ modes[:, 0], values[0] * m @ modes[:, 0], atol=1e-10)
    assert modes[2, 0] == pytest.approx(-(k[2, :2] @ modes[:2, 0]) / k[2, 2])


@pytest.mark.parametrize("count", (1, 3, 7))
def test_sparse_modes_match_condensed_dense_reference(count):
    rng = np.random.default_rng(47)
    raw = rng.normal(size=(14, 14))
    k = raw.T @ raw + np.eye(14)
    m = np.diag([1.0 + i / 8 for i in range(8)] + [0.0] * 6)
    condensed = k[:8, :8] - k[:8, 8:] @ np.linalg.solve(k[8:, 8:], k[8:, :8])
    expected = scipy.linalg.eigh(condensed, m[:8, :8])[0][:count]
    values, modes = _massless_support_modes(sp.csc_matrix(k), sp.csc_matrix(m), count, 1e-6, 1000, None)
    np.testing.assert_allclose(values, expected, rtol=1e-9, atol=1e-10)
    np.testing.assert_allclose(k @ modes, (m @ modes) * values, atol=1e-8)


def test_lateral_modulus_area_units_and_modal_sensitivity(tmp_path: Path):
    frequencies = []
    shapes = []
    for ky in (1e4, 1e6, 1e8):
        model = _face_hrx(tmp_path, 4, [-1] * 6)
        values = set_lateral_subgrade_moduli(model, [10], kx_kn_m3=1e3, ky_kn_m3=ky)
        # Patch is 100 cm by 50 cm. kN/m³ -> kN/cm³ divides by 10^6.
        assert values[10] == pytest.approx(ky * 5000 / 1e6)
        prepare_model(model, force=True, use_cache=False)
        result = solve_modal_analysis(model, model.collections.analyses[3])
        assert result.modes and all(mode.residual_norm < 1e-6 for mode in result.modes)
        frequencies.append(result.modes[0].frequency)
        shape = result.modes[0].shape[:-1]
        shapes.append(shape / np.linalg.norm(shape))
    assert frequencies[0] < frequencies[1] < frequencies[2]
    assert abs(float(shapes[0] @ shapes[2])) < 1.0 - 1e-10


def test_lateral_modulus_rejects_material_combination_without_partial_changes(tmp_path):
    model = _face_hrx(tmp_path, 4, [-1] * 6)
    restraint = model.collections.restraints[10]
    restraint.material_key = 60
    with pytest.raises(ModelPreparationError, match="MaterialKey"):
        set_lateral_subgrade_moduli(model, [10], kx_kn_m3=10, ky_kn_m3=20)
    assert restraint.k[1] == -1


def test_modulus_change_invalidates_prepared_state_and_source_cache(tmp_path, monkeypatch):
    model = _face_hrx(tmp_path, 4, [-1] * 6)
    monkeypatch.setenv("HISTRA_PREPARED_CACHE", "1")
    monkeypatch.setenv("HISTRA_CACHE_DIR", str(tmp_path / "cache"))
    set_lateral_subgrade_moduli(model, [10], kx_kn_m3=0, ky_kn_m3=1e4)
    prepare_model(model, force=True)
    assert model.collections.restraints[10].k[1] == pytest.approx(50)
    set_lateral_subgrade_moduli(model, [10], kx_kn_m3=0, ky_kn_m3=1e6)
    prepare_model(model, force=True)
    assert model.collections.restraints[10].k[1] == pytest.approx(5000)


def test_untranslated_geotechnical_material_is_not_silently_ignored(tmp_path):
    model = _face_hrx(tmp_path, 4, [-1] * 6)
    model.collections.restraints[10].material_key = 60
    model.unsupported_material_templates[60] = "GeotecnicalMaterial"
    with pytest.raises(ModelPreparationError, match="GeotecnicalMaterial"):
        prepare_model(model, force=True)


def test_singular_massless_support_fails_clearly():
    with pytest.raises(ModalAnalysisError, match="singular support tangent"):
        _massless_support_modes(sp.csc_matrix(np.diag([2., 3., 0.])),
                                sp.csc_matrix(np.diag([1., 1., 0.])), 1, 1e-6, 1000, None)


def test_modal_after_static_analysis_preserves_support_displacement(tmp_path):
    from histra import AnalysisSession
    import warnings
    model = _face_hrx(tmp_path, 4, [-1] * 6)
    set_lateral_subgrade_moduli(model, [10], kx_kn_m3=1e4, ky_kn_m3=1e6)
    prepare_model(model, force=True)
    model.collections.analyses[3].initial_analysis_key = 1
    session = AnalysisSession(model, equilibrium_policy="warn", strategy_policy="off")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert session.run("Vert").completed
        before = model.collections.restraints[10].u.copy()
        result = session.run("Modal_virgin")
    assert result.modal_result.modes
    np.testing.assert_array_equal(model.collections.restraints[10].u, before)

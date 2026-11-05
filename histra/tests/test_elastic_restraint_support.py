"""Elastic vertical foundation restraints and their native stiffness semantics."""

from __future__ import annotations

import warnings

import numpy as np
import pytest

from histra import AnalysisSession, load_model
from histra.io.csharp_results_capture import CSharpResultsCapture
from histra.preprocessing import prepare_model
from histra.preprocessing.contact_geometry import _interface_division_count
from histra.preprocessing.errors import ModelPreparationError
from histra.preprocessing.restraint_support import (
    FIXED,
    ELASTIC_VERTICAL,
    classify_restraint_stiffness,
    restraint_support_entries,
)
from histra.solver.assembler import assemble_global_k
from histra.solver.equilibrium import UnsafeEquilibriumWarning
from histra.solver.model_manager import ModelManager
from tools.benchmarks.build_masonry_reference_models import (
    CASE_NAMES,
    DEFAULT_TEMPLATE,
    build_reference_model,
)


# The wall reference is 100 cm long and 20 cm wide.  C# writes the foundation
# support as K2 = Kz [force/length^3] * B [length] * L [length], i.e. force/length.
WALL_LENGTH_CM = 100.0
WALL_WIDTH_CM = 20.0
WALL_AREA_CM2 = WALL_LENGTH_CM * WALL_WIDTH_CM


def _wall_tree():
    return build_reference_model(DEFAULT_TEMPLATE, CASE_NAMES[0])


def _set_vertical_subgrade_modulus(tree, kz: float) -> float:
    """Write the C# foundation convention into the single wall restraint."""
    stiffness = float(kz) * WALL_AREA_CM2
    for restraint in tree.getroot().findall("Restraint"):
        restraint.set("K2", repr(stiffness))
    for geometry in tree.getroot().findall("GeometryLineRestraint"):
        geometry.set("K2", repr(stiffness))
        geometry.set("K", "|".join(("-1", repr(stiffness), "-1", "-1", "-1", "-1")))
    return stiffness


def _load_wall(tmp_path, *, kz: float | None = None):
    tree = _wall_tree()
    if kz is not None:
        _set_vertical_subgrade_modulus(tree, kz)
    path = tmp_path / ("elastic.hrx" if kz is not None else "fixed.hrx")
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return load_model(path), path


def _restraint_interface(model):
    interfaces = [
        intf for intf in model.collections.interfaces.values()
        if intf.parent_type_element1 == "Restraint"
    ]
    assert len(interfaces) == 1
    return interfaces[0]


def test_fixed_restraint_allocates_no_support_dof_and_keeps_regression_gdl(tmp_path):
    model, _ = _load_wall(tmp_path)
    restraint = model.collections.restraints[1]
    assert classify_restraint_stiffness(restraint) == FIXED

    report = prepare_model(model, force=True)

    assert report.gdl == 28
    assert model.gdl == 7 * len(model.collections.quads)
    assert restraint.solver_gdls == [0] * 6
    assert restraint.u == [0.0] * 6
    assert restraint_support_entries(model) == ([], [], [])
    assert _restraint_interface(model).parent_type_element1 == "Restraint"


def test_elastic_vertical_restraint_hrx_units_and_mesh_subdivision(tmp_path):
    kz = 0.1  # kN/cm^3 (HiStrA native force/length^3)
    expected_k2 = kz * WALL_AREA_CM2  # 200 kN/cm
    model, path = _load_wall(tmp_path, kz=kz)
    restraint = model.collections.restraints[1]

    assert expected_k2 == pytest.approx(200.0)
    assert float(restraint.k[1]) == pytest.approx(expected_k2)
    assert all(float(value) == -1.0 for index, value in enumerate(restraint.k) if index != 1)
    assert "K2=\"200.0\"" in path.read_text(encoding="utf-8")
    assert classify_restraint_stiffness(restraint) == ELASTIC_VERTICAL

    prepare_model(model, force=True)
    interface = _restraint_interface(model)
    expected_ncol = _interface_division_count(
        interface.length, minimum=int(model.interface_nrow), imax=float(model.interface_imax)
    )
    expected_nrow = _interface_division_count(
        max(interface.thickness),
        minimum=int(model.interface_nrow),
        imax=float(model.interface_imax),
    )
    assert (interface.ncol, interface.nrow, interface.nspring) == (
        expected_ncol,
        expected_nrow,
        expected_ncol,
    )
    assert len(interface.trasv_1) == expected_nrow * expected_ncol

    # The interface fibre stiffness remains the Quad-side contact stiffness;
    # the support stiffness lives on the separate restraint DOF exactly once.
    stiffness = assemble_global_k(model, alfa=0.0)
    interface_k00 = float(interface.status.k[0][0])
    assert interface_k00 == pytest.approx(
        sum(float(spring.k) for spring in interface.trasv_1), rel=1e-12
    )
    support_dof = restraint.solver_gdls[1]
    assert support_dof == model.gdl
    assert restraint.u[1] == 0.0
    np.testing.assert_allclose(restraint.reference_e1, (1.0, 0.0, 0.0), atol=1e-12)
    np.testing.assert_allclose(restraint.reference_e2, (0.0, 0.0, 1.0), atol=1e-12)
    np.testing.assert_allclose(interface.reference_e2, restraint.reference_e2, atol=1e-8)
    assert [(entry.gdl, entry.alfa) for entry in interface.aff[0]] == [(support_dof, 1.0)]
    entries = restraint_support_entries(model)
    assert entries == ([support_dof - 1], [support_dof - 1], [expected_k2])

    assert stiffness.shape == (model.gdl, model.gdl)
    assert float(stiffness[support_dof - 1, support_dof - 1]) == pytest.approx(
        interface_k00 + expected_k2, rel=1e-12
    )
    # No other diagonal may contain the support value: it was neither omitted
    # nor copied onto every interface fibre.
    diagonal = stiffness.diagonal()
    others = np.delete(diagonal, support_dof - 1)
    assert not np.any(np.isclose(others, expected_k2, rtol=0.0, atol=1e-9))


def test_elastic_restraint_without_serialized_reference_system_is_rejected(tmp_path):
    tree = _wall_tree()
    _set_vertical_subgrade_modulus(tree, 0.1)
    for restraint in tree.getroot().findall("Restraint"):
        reference = restraint.find("ReferenceSystem")
        if reference is not None:
            restraint.remove(reference)
    path = tmp_path / "no-reference.hrx"
    tree.write(path, encoding="utf-8", xml_declaration=True)
    model = load_model(path)
    restraint = model.collections.restraints[1]
    assert not restraint.has_reference_system
    with pytest.raises(ModelPreparationError, match="ReferenceSystem"):
        prepare_model(model, force=True)


@pytest.mark.parametrize("axis", [(1., 0., 0.), (0., 0., 0.), (0.6, 0., 0.8)])
def test_invalid_elastic_support_axis_is_rejected(tmp_path, axis):
    model, _ = _load_wall(tmp_path, kz=0.1)
    model.collections.restraints[1].reference_e2 = axis
    with pytest.raises(ModelPreparationError, match="orthonormal axes"):
        prepare_model(model, force=True)


def test_elastic_restart_fails_before_reading_database(tmp_path):
    from histra.io.results_reader import ResultsStateError
    from histra.solver.restart import restore_committed_analysis_state

    model, _ = _load_wall(tmp_path, kz=0.1)
    prepare_model(model, force=True)
    with pytest.raises(ResultsStateError, match="Database restart with elastic restraints"):
        restore_committed_analysis_state(model, tmp_path / "missing.Results", 1, 1, None, None, None)


def test_vectorized_support_state_survives_copy_and_reset(tmp_path):
    import copy
    from histra.preprocessing.restraint_support import (
        scatter_restraint_resisting_force, update_restraint_domain,
    )
    from histra.types.linear_system import LinearSystem

    model, _ = _load_wall(tmp_path, kz=0.1)
    prepare_model(model, force=True)
    ls = LinearSystem(model.gdl)
    restraint = model.collections.restraints[1]
    dof = restraint.solver_gdls[1] - 1
    ls.x[dof] = 0.25
    update_restraint_domain(model, ls)
    scatter_restraint_resisting_force(model, ls)
    assert restraint.u[1] == pytest.approx(0.25)
    assert ls.b[dof] == pytest.approx(-50.0)

    branch = copy.deepcopy(model)
    branch_ls = LinearSystem(branch.gdl)
    branch_ls.x[dof] = 0.5
    update_restraint_domain(branch, branch_ls)
    assert branch.collections.restraints[1].u[1] == pytest.approx(0.75)
    assert restraint.u[1] == pytest.approx(0.25)
    prepare_model(branch, force=True)
    assert branch.collections.restraints[1].u[1] == 0.0


def test_elastic_support_survives_in_memory_chain(tmp_path):
    model, _ = _load_wall(tmp_path, kz=0.1)
    prepare_model(model, force=True)
    session = AnalysisSession(model, equilibrium_policy="warn", strategy_policy="off")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UnsafeEquilibriumWarning)
        assert session.run("Vert").completed
        support = model.collections.restraints[1]
        before = float(support.u[1])
        result = session.run("Reversal", max_committed_steps=1)
    assert result.committed_steps
    assert before != 0.0
    assert float(support.u[1]) == pytest.approx(before, rel=1e-3)


@pytest.mark.parametrize(
    "changes, message",
    [
        ({0: 5.0}, "only K2"),
        ({3: 10.0}, "only K2"),
    ],
)
def test_unsupported_restraint_directions_are_rejected_clearly(tmp_path, changes, message):
    model, _ = _load_wall(tmp_path)
    restraint = model.collections.restraints[1]
    for index, value in changes.items():
        restraint.k[index] = value
    with pytest.raises(ModelPreparationError, match=message):
        prepare_model(model, force=True)


def test_elastic_restraint_with_material_is_rejected(tmp_path):
    model, _ = _load_wall(tmp_path, kz=0.1)
    restraint = model.collections.restraints[1]
    restraint.material_key = 146
    with pytest.raises(ModelPreparationError, match="MaterialKey"):
        prepare_model(model, force=True)


def _run_vert(model):
    session = AnalysisSession(
        model,
        equilibrium_policy="warn",
        strategy_policy="off",
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UnsafeEquilibriumWarning)
        result = session.run("Vert")
    assert result.code == 0
    assert result.committed_steps
    return result


def _final_control_displacement(result) -> float:
    return float(result.committed_steps[-1]["displacement"])


def test_vertical_response_varies_with_k2_and_approaches_fixed_limit(tmp_path):
    fixed_model, _ = _load_wall(tmp_path)
    prepare_model(fixed_model, force=True)
    fixed_displacement = _final_control_displacement(_run_vert(fixed_model))

    stiffness_values = (10.0, 1_000.0, 1_000_000.0)
    displacements = []
    support_forces = []
    for k2 in stiffness_values:
        model, _ = _load_wall(tmp_path, kz=k2 / WALL_AREA_CM2)
        prepare_model(model, force=True)
        result = _run_vert(model)
        restraint = model.collections.restraints[1]
        displacements.append(_final_control_displacement(result))
        support_forces.append(float(restraint.k[1]) * float(restraint.u[1]))

    # Softer support settles more; the sequence is strictly monotonic.
    assert displacements[0] > displacements[1] > displacements[2] > fixed_displacement
    # The support carries the same total vertical load at every K2.  This is
    # the strongest check that K2 is neither omitted nor counted twice.
    np.testing.assert_allclose(
        support_forces, np.full(3, support_forces[0]), rtol=1e-9, atol=1e-9
    )
    assert support_forces[0] < 0.0
    # A very stiff support converges to the fully fixed response.
    assert (displacements[-1] - fixed_displacement) / abs(fixed_displacement) < 0.01
    from histra.postprocessing import compute_total_reaction

    reaction = compute_total_reaction(model)
    assert float(reaction.z) == pytest.approx(support_forces[-1], rel=1e-4)


def test_native_restraint_state_export_accepts_elastic_vertical_support(tmp_path):
    model, _ = _load_wall(tmp_path, kz=0.1)
    prepare_model(model, force=True)
    result = _run_vert(model)
    assert result.code == 0
    restraint = model.collections.restraints[1]

    capture = CSharpResultsCapture(model, combination=1)
    capture._elements({"AnalysisKey": 1, "Combination": 1, "Step": 10})
    rows = [
        row for row in capture.records["RestraintStates"]
        if int(row["ParentKey"]) == int(restraint.key)
    ]
    assert len(rows) == 1
    assert float(rows[0]["U2"]) == pytest.approx(float(restraint.u[1]))


def test_modal_analysis_handles_massless_elastic_restraint_dofs(tmp_path):
    from histra.solver.modal import solve_modal_analysis

    model, _ = _load_wall(tmp_path, kz=0.1)
    prepare_model(model, force=True)
    analysis = model.collections.analyses[3]
    result = solve_modal_analysis(model, analysis)
    assert result.modes
    assert all(mode.frequency > 0 for mode in result.modes)

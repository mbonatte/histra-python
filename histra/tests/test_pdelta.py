"""Unit tests for geometric nonlinearity and P-Delta load assembly."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest

from histra.io.hr_loader import load_model
from histra.model.load import (
    Analysis,
    LineLoadElement,
    LoadCombination,
    LoadCombinationItem,
    LoadCondition,
    LoadTemplate,
    LoadTemplateItem,
)
from histra.model.model import Collections, Model
from histra.solver.equilibrium import UnsafeEquilibriumWarning
from histra.solver.model_manager import ModelManager, pdelta_enabled
from histra.solver.session import AnalysisSession
from histra.solver.solve import solve_static_nonlinear
from histra.types import AfferenceEntry, Point

ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_NO_PDELTA = ROOT / "my_model" / "benchmark_3_Pdelta" / "benchmark_virgin_noPDelta.hrx"
BENCHMARK_PDELTA = ROOT / "my_model" / "benchmark_3_Pdelta" / "benchmark.hrx"


def test_pdelta_enabled_helper():
    """Verify that pdelta_enabled handles various representations."""
    assert not pdelta_enabled(None)
    assert not pdelta_enabled("None")
    assert not pdelta_enabled("none")
    assert not pdelta_enabled("0")
    assert not pdelta_enabled(0)
    assert not pdelta_enabled(False)
    assert not pdelta_enabled("disabled")

    assert pdelta_enabled("EachStep")
    assert pdelta_enabled("EachIteration")
    assert pdelta_enabled("eachstep")
    assert pdelta_enabled(1)
    assert pdelta_enabled(2)
    assert pdelta_enabled(True)


def test_pdelta_includes_assigned_line_load_moment():
    analysis = Analysis(key=8, load_combination_key=3)
    quad = SimpleNamespace(
        key=7,
        status=SimpleNamespace(u=[0.0, 0.0, 0.0, 0.0, 0.0, 1.0]),
        g=Point(0.0, 0.0, 0.0),
        interface_keys=[[], [], [], []],
        aff=[[], [], [], [AfferenceEntry(1, 1.0)], [], []],
    )
    condition = LoadCondition(id=4)
    combination = LoadCombination(
        key=3,
        items=[
            LoadCombinationItem(
                column_key=4, row_key=1, type_data="Number", val=0.5
            )
        ],
    )
    template = LoadTemplate(
        key=5,
        purpose_type="LineLoad",
        items=[
            LoadTemplateItem(
                key=6,
                load_template_key=5,
                load_condition_id=4,
                load_value=10.0,
                dir_z=-1.0,
            )
        ],
    )
    line_load = LineLoadElement(
        key=9,
        element_key=7,
        element_type="Quad",
        load_template_key=5,
        point1=(0.0, 0.0, 0.0),
        point2=(2.0, 0.0, 0.0),
    )
    model = Model(
        gdl=1,
        collections=Collections(
            quads={7: quad},
            analyses={8: analysis},
            load_conditions={4: condition},
            load_combinations={3: combination},
            load_templates={5: template},
            line_loads={9: line_load},
        ),
    )

    ModelManager.clear_hysteretic_batch()
    pq = ModelManager.compute_and_assemble_pdelta_load(
        model, analysis=analysis, combination=1
    )

    # phi_z x r_x gives +Y displacement; +Y x the -Z force gives -X moment.
    np.testing.assert_allclose(pq, [-10.0])


def test_pdelta_interface_moments_use_only_first_four_quad_faces():
    """Match C# ComputePDeltaLoads, which visits Interfaces1..Interfaces4."""

    def interface(key: int, node_key: int, force: float):
        spring = SimpleNamespace(get_force=lambda: force)
        return SimpleNamespace(
            key=key,
            parent_element_key1=7,
            parent_type_element1="Quad",
            reference_e1=(1.0, 0.0, 0.0),
            reference_e2=(0.0, 1.0, 0.0),
            reference_e3=(0.0, 0.0, 1.0),
            node_keys=[node_key],
            vint3d=[],
            trasv_1=[],
            trasv_2=[],
            slid=[],
            slid_out_plan=[spring],
        )

    quad = SimpleNamespace(
        key=7,
        status=SimpleNamespace(u=[0.0, 0.0, 0.0, 0.0, 0.0, 1.0]),
        g=Point(0.0, 0.0, 0.0),
        # Interface 12 is deliberately placed on C# Interfaces5.
        interface_keys=[[11], [], [], [], [12], []],
        aff=[[], [], [], [AfferenceEntry(1, 1.0)], [], []],
    )
    model = Model(
        gdl=1,
        collections=Collections(
            nodes={
                21: SimpleNamespace(point=Point(1.0, 0.0, 0.0)),
                22: SimpleNamespace(point=Point(1.0, 0.0, 0.0)),
            },
            quads={7: quad},
            interfaces={
                11: interface(11, 21, 2.0),
                12: interface(12, 22, 3.0),
            },
        ),
    )

    ModelManager.clear_hysteretic_batch()
    pq = ModelManager.compute_and_assemble_pdelta_load(model)

    # phi_z x r_x = +Y; local force is -Z, hence -X moment.
    # The face-5 force would change this to -5 if it were incorrectly included.
    np.testing.assert_allclose(pq, [-2.0])


@pytest.mark.skipif(not BENCHMARK_PDELTA.exists(), reason="benchmark.hrx not available")
def test_pdelta_computation_on_benchmark():
    """Test that compute_and_assemble_pdelta_load generates non-zero Pq moments."""
    model = load_model(BENCHMARK_PDELTA)
    ModelManager.prepare_model(model)
    session = AnalysisSession(model)
    session.run("Vert")
    session.run("scour_1")

    pq = ModelManager.compute_and_assemble_pdelta_load(model)
    assert isinstance(pq, np.ndarray)
    assert len(pq) == model.gdl
    assert np.count_nonzero(pq) > 0
    assert np.linalg.norm(pq) > 0.0


@pytest.mark.parametrize(
    ("hrx_path", "expected_csharp_reaction_z"),
    [
        (BENCHMARK_NO_PDELTA, -241.64808105351403),
        (BENCHMARK_PDELTA, -241.65975634241477),
    ],
    ids=["linear-geometry", "pdelta"],
)
def test_live_step_one_matches_csharp_reaction_checkpoint(
    hrx_path: Path,
    expected_csharp_reaction_z: float,
) -> None:
    """Restart from C# scour state and strictly verify each geometry path.

    The previous test reran both complete predecessor chains and only asserted
    that their third-step reactions differed.  The sibling ``.Results`` files
    already contain authoritative scour checkpoints, so a one-step restart is
    both faster and a materially stronger C# regression.
    """

    if not hrx_path.exists() or not hrx_path.with_suffix(".Results").exists():
        pytest.skip(f"benchmark assets not available for {hrx_path.name}")

    model = load_model(hrx_path)
    live = model.collections.analyses[22]
    with pytest.warns(UnsafeEquilibriumWarning):
        code, steps = solve_static_nonlinear(
            model,
            live,
            results_path=hrx_path.with_suffix(".Results"),
            max_committed_steps=1,
        )

    assert code == 0
    assert len(steps) == 1
    assert steps[0]["step"] == 1
    assert steps[0]["status"] == "OK"
    error = abs(steps[0]["reaction_z"] - expected_csharp_reaction_z)
    assert error <= 1.0e-2
    assert error / abs(expected_csharp_reaction_z) <= 5.0e-5

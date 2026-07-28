"""C#-compatible interface mutation and in-memory analysis chaining."""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

from histra.io.hr_loader import load_model
from histra.io.results_reader import read_global_displacements
from histra.solver.interface_material import (
    InterfaceMaterialMutationError,
    change_interface_materials,
)
from histra.solver.session import AnalysisSession, AnalysisSessionError

ROOT = Path(__file__).resolve().parents[1]
HRX = ROOT / "model-chain" / "model.hrx"
RESULTS = ROOT / "model-chain" / "model.Results"
AFFECTED = (359, 360, 361, 362)

pytestmark = pytest.mark.skipif(
    not HRX.exists(), reason="model-chain benchmark assets are not installed"
)


def test_hrx_dependency_chain_is_vert_scour_live():
    model = load_model(HRX)
    session = AnalysisSession(model)
    assert [(item.key, item.name) for item in session.dependency_chain("LiveLoad_1")] == [
        (1, "Vert"),
        (23, "scour_1"),
        (22, "LiveLoad_1"),
    ]


def test_custom_material_rebuild_matches_csharp_serialized_definitions():
    model = load_model(HRX)
    reference = model.collections.interfaces[359]
    expected = {
        "transverse_k": reference.trasv_1[0].k,
        "transverse_area": reference.trasv_1[0].area,
        "sliding_k": reference.slid[0].k,
        "sliding_mu": reference.slid[0].mu,
        "sliding_cohesion": reference.slid[0].cohesion,
        "out_k": reference.slid_out_plan[0].k,
    }

    report = change_interface_materials(
        model, [359], 147, preserve_committed_state=False
    )
    rebuilt = model.collections.interfaces[359]

    assert report.interface_count == 1
    assert report.spring_count == 12
    assert rebuilt.material_key == 147
    assert rebuilt.trasv_1[0].k == pytest.approx(expected["transverse_k"], rel=2.0e-6)
    assert rebuilt.trasv_1[0].area == pytest.approx(expected["transverse_area"], rel=2.0e-6)
    assert rebuilt.slid[0].k == pytest.approx(expected["sliding_k"], rel=2.0e-6)
    assert rebuilt.slid[0].mu == pytest.approx(expected["sliding_mu"], abs=2.0e-12)
    assert rebuilt.slid[0].cohesion == pytest.approx(expected["sliding_cohesion"], abs=2.0e-12)
    assert rebuilt.slid_out_plan[0].k == pytest.approx(expected["out_k"], rel=2.0e-6)


def test_material_mutation_preserves_committed_history_but_changes_definition():
    model = load_model(HRX)
    interface = model.collections.interfaces[359]
    source = interface.trasv_1[0]
    state = {
        "u": source._cstrain,
        "f": source._cstress,
        "phase": source.phase,
        "fy": tuple(source.fy),
        "umax": tuple(source.umax),
        "load_indicator": source._cload_indicator,
    }
    old_k = source.k

    change_interface_materials(model, [359], 0, preserve_committed_state=True)
    target = model.collections.interfaces[359].trasv_1[0]

    assert model.collections.interfaces[359].material_key == 0
    assert target.k != pytest.approx(old_k)
    assert target._cstrain == pytest.approx(state["u"], abs=1.0e-15)
    assert target._cstress == pytest.approx(state["f"], abs=1.0e-15)
    assert target.phase == state["phase"]
    assert tuple(target.fy) == pytest.approx(state["fy"], abs=1.0e-15)
    assert tuple(target.umax) == pytest.approx(state["umax"], abs=1.0e-15)
    assert target._cload_indicator == state["load_indicator"]


def test_material_mutation_is_atomic_on_invalid_interface_key():
    model = load_model(HRX)
    before = model.collections.interfaces[359].material_key
    with pytest.raises(InterfaceMaterialMutationError, match="Unknown interface keys"):
        change_interface_materials(model, [359, 999999], 147)
    assert model.collections.interfaces[359].material_key == before


def test_session_rejects_skipping_required_predecessor():
    model = load_model(HRX)
    session = AnalysisSession(model)
    with pytest.raises(AnalysisSessionError, match="requires predecessor 23"):
        session.run("LiveLoad_1", max_committed_steps=1)


@pytest.mark.skipif(
    os.getenv("HISTRA_RUN_CHAIN_BENCHMARK") != "1",
    reason="set HISTRA_RUN_CHAIN_BENCHMARK=1 for the full C# chain benchmark",
)
def test_complete_vert_scour_live_chain_matches_csharp_results():
    model = load_model(HRX)
    session = AnalysisSession(model)
    session.change_interface_materials(AFFECTED, 0, preserve_committed_state=False)

    vert = session.run("Vert")
    session.change_interface_materials(AFFECTED, 147, preserve_committed_state=True)
    scour = session.run("scour_1")
    live = session.run("LiveLoad_1")

    assert len(vert.committed_steps) == 5
    assert len(scour.committed_steps) == 5
    assert len(live.committed_steps) == 38
    assert live.code == -3

    for execution, key, relative_limit in (
        (vert, 1, 2.0e-7),
        (scour, 23, 2.0e-7),
        (live, 22, 3.0e-4),
    ):
        step = execution.committed_steps[-1]["step"]
        reference = read_global_displacements(
            RESULTS,
            key,
            1,
            step,
            model_or_hrx=model,
            size=model.gdl,
        )
        actual = np.asarray(execution.committed_steps[-1]["u"])
        relative = np.linalg.norm(actual - reference) / np.linalg.norm(reference)
        assert relative <= relative_limit

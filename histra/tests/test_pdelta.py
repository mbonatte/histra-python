"""Unit tests for geometric nonlinearity and P-Delta load assembly."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pytest

from histra.io.hr_loader import load_model
from histra.solver.model_manager import ModelManager, pdelta_enabled
from histra.solver.session import AnalysisSession

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


@pytest.mark.skipif(
    not BENCHMARK_NO_PDELTA.exists() or not BENCHMARK_PDELTA.exists(),
    reason="benchmark_3_Pdelta assets not available",
)
def test_pdelta_vs_no_pdelta_reactions_differ():
    """Test that P-Delta effects produce distinct reactions compared to linear geometry."""
    m_no_pd = load_model(BENCHMARK_NO_PDELTA)
    ModelManager.prepare_model(m_no_pd)
    s_no_pd = AnalysisSession(m_no_pd)
    s_no_pd.run("Vert")
    s_no_pd.run("scour_1")
    res_no_pd = s_no_pd.run("LiveLoad_1", max_committed_steps=3)

    m_pd = load_model(BENCHMARK_PDELTA)
    ModelManager.prepare_model(m_pd)
    s_pd = AnalysisSession(m_pd)
    s_pd.run("Vert")
    s_pd.run("scour_1")
    res_pd = s_pd.run("LiveLoad_1", max_committed_steps=3)

    assert len(res_no_pd.committed_steps) == 3
    assert len(res_pd.committed_steps) == 3

    # Reactions under P-Delta include macro-element moment shifts
    r3_no_pd = res_no_pd.committed_steps[-1]["reaction_z"]
    r3_pd = res_pd.committed_steps[-1]["reaction_z"]
    assert abs(r3_pd - r3_no_pd) > 0.5

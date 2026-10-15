"""Fresh, reproducible inputs for native masonry validation, not golden results."""

from pathlib import Path
import os
import subprocess
import sys
import warnings
import xml.etree.ElementTree as ET

import numpy as np
import pytest

from histra import AnalysisSession, load_model
from histra.solver.backend_coverage import inspect_solver_backend
from histra.solver.load_assembly import assemble_load_vector
from histra.solver.model_manager import ModelManager
from histra.solver.equilibrium import UnsafeEquilibriumWarning
from histra.springs.elastic import SpringElastic
from histra.springs.hysteretic import SpringHysteretic
from histra.types.umfpack import find_umfpack_library
from tools.benchmarks.build_masonry_reference_models import (
    CASE_NAMES,
    DEFAULT_TEMPLATE,
    build_reference_model,
    write_reference_models,
)


@pytest.mark.parametrize("case", CASE_NAMES)
def test_new_geometry_and_intended_material_branches(tmp_path, case):
    tree = build_reference_model(DEFAULT_TEMPLATE, case)
    root = tree.getroot()
    assert root.get("IsLocked") == "false"
    assert root.findall("Interface") == []
    assert root.findall(".//Spring") == []
    assert root.findall(".//AfferenceMatrices") == []
    assert root.findall(".//State") == []
    path = tmp_path / (case + ".hrx")
    tree.write(path, encoding="utf-8", xml_declaration=True)
    model = load_model(path)
    ModelManager.prepare_model(model, force=True)
    assert (len(model.collections.quads), len(model.collections.interfaces), model.gdl) == (
        4,
        4,
        28,
    )
    inspect_solver_backend(model).require_compiled()
    material = model.collections.materials[18]
    if case.startswith("02"):
        assert float(material.properties["Ehor"]) == 80.0
        assert float(material.properties["Ever"]) == 160.0
    if case.startswith("03"):
        assert all(
            isinstance(s, SpringElastic)
            for i in model.collections.interfaces.values()
            for s in i.trasv_1
        )
    if case.startswith("04"):
        assert all(isinstance(q.spring, SpringHysteretic) for q in model.collections.quads.values())
    items = root.findall("LoadFunctionItem[@loadFunctionKey='2']")
    assert [(float(i.get("pseudoTime")), float(i.get("multiplier"))) for i in items] == [
        (0, 0),
        (1, 1),
        (2, -1),
        (3, 1),
        (4, 0),
    ]
    assert all(np.isfinite(assemble_load_vector(model, key)).all() for key in (1, 2))


def test_writer_preserves_existing_reference_inputs(tmp_path):
    paths = write_reference_models(DEFAULT_TEMPLATE, tmp_path)
    before = {p: p.read_bytes() for p in paths}
    with pytest.raises(FileExistsError):
        write_reference_models(DEFAULT_TEMPLATE, tmp_path)
    assert before == {p: p.read_bytes() for p in paths}


@pytest.mark.parametrize("case", CASE_NAMES)
def test_native_control_python_reference_chain(tmp_path, monkeypatch, case):
    if find_umfpack_library() is None:
        pytest.skip("Original native UMFPACK configuration required")
    monkeypatch.setenv("HISTRA_UMFPACK_ORDERING", "amd")
    path = tmp_path / (case + ".hrx")
    build_reference_model(DEFAULT_TEMPLATE, case).write(
        path, encoding="utf-8", xml_declaration=True
    )
    model = load_model(path)
    ModelManager.prepare_model(model, force=True)
    session = AnalysisSession(
        model,
        linear_solver_backend="umfpack",
        linear_solver_precision="accurate",
        umfpack_irstep=2,
        equilibrium_policy="warn",
        strategy_policy="off",
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UnsafeEquilibriumWarning)
        vert = session.run("Vert")
        reversal = session.run("Reversal")
    assert vert.code == reversal.code == 0
    assert len(vert.committed_steps) == 10
    assert len(reversal.committed_steps) == 32
    factors = [step["load_factor"] for step in reversal.steps if step.committed]
    assert [factors[j] for j in (7, 15, 23, 31)] == [1.0, -1.0, 1.0, 0.0]


def test_original_oracle_initializes_unrun_analysis_load_state(tmp_path):
    install = Path(r"C:\Program Files\Gruppo Sismica\HiStrA Bridges 2026.1.1")
    if sys.platform != "win32" or not (install / "SolverRuntime.dll").exists():
        pytest.skip("Installed original C# 2026.1.1 runtime required")
    model_path = tmp_path / "unrun.hrx"
    build_reference_model(DEFAULT_TEMPLATE, CASE_NAMES[0]).write(
        model_path,
        encoding="utf-8",
        xml_declaration=True,
    )
    assert not ET.parse(model_path).findall(".//State")
    oracle = (
        DEFAULT_TEMPLATE.parents[2] / "tools/csharp-diagnostics/Invoke-FreshConstructionOracle.ps1"
    )
    shell = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
    for key in (1, 2):
        out = tmp_path / str(key)
        result = subprocess.run(
            [
                str(shell),
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(oracle),
                "-ModelPath",
                str(model_path),
                "-OutputDirectory",
                str(out),
                "-ExportAssembly",
                "-AnalysisKey",
                str(key),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        native = np.fromfile(out / "native-Vert-Ptarget.bin", dtype=np.float64)
        model = load_model(model_path)
        ModelManager.prepare_model(model, force=True)
        expected = assemble_load_vector(model, key)
        assert np.any(native)
        np.testing.assert_array_equal(native, expected)

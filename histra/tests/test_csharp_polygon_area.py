"""Single polygon projection used by the original restraint spring factory."""
from pathlib import Path
import json

import numpy as np

from histra.preprocessing.csharp_fibre_geometry import _csharp_polygon_area


def test_original_polygon_area_bits():
    fixture = Path(__file__).parent / "fixtures/csharp-polygon-area-2026.1.1.json"
    cases = json.loads(fixture.read_text(encoding="utf-8-sig"))["cases"]
    actual = [_csharp_polygon_area(np.asarray(c["points"], dtype=np.float32)) for c in cases]
    np.testing.assert_array_equal(actual, [c["area"] for c in cases])


def test_elastic_foundation_springs_keep_native_area(tmp_path):
    from histra import load_model
    from histra.solver.model_manager import ModelManager
    from tools.benchmarks.build_masonry_reference_models import (
        CASE_NAMES, DEFAULT_TEMPLATE, build_reference_model,
    )

    path = tmp_path / "elastic.hrx"
    build_reference_model(DEFAULT_TEMPLATE, CASE_NAMES[2]).write(path, encoding="utf-8")
    model = load_model(path)
    ModelManager.prepare_model(model, force=True)
    areas = [
        spring.area for interface in model.collections.interfaces.values()
        if "Restraint" in (interface.parent_type_element1, interface.parent_type_element2)
        for spring in interface.trasv_1
    ]
    fixture = Path(__file__).parent / "fixtures/csharp-polygon-area-2026.1.1.json"
    cases = json.loads(fixture.read_text(encoding="utf-8-sig"))["cases"]
    assert len(areas) == 81
    np.testing.assert_array_equal(areas, [c["area"] for c in cases[:81]])


def test_polygon_area_live_bitwise_runner():
    """Verify polygon area against live C# micro-runner with exact 32-bit single bit parity."""
    from histra.tests.csharp_runner_client import CSharpRunnerClient
    client = CSharpRunnerClient()
    fixture = Path(__file__).parent / "fixtures/csharp-polygon-area-2026.1.1.json"
    cases = json.loads(fixture.read_text(encoding="utf-8-sig"))["cases"][:20]

    for i, c in enumerate(cases):
        cs_res = client.polygon_area(points=c["points"])
        py_area = _csharp_polygon_area(np.asarray(c["points"], dtype=np.float32))

        # Check IEEE-754 Single precision 32-bit representation
        py_bits = int(np.asarray([py_area], dtype=np.float32).view(np.int32)[0])
        cs_bits = int(cs_res["area_single_bits"])
        assert py_bits == cs_bits, f"Case {i} area_single_bits mismatch: py={py_bits}, cs={cs_bits}"

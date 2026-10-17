"""Live parity tests for Sutherland-Hodgman polygon clipping and quad contact intersection.

Validates quad intersection clipping (Operations.FindIntersectionBetweenQuadrilaters)
and 3D shoelace polygon area between the live C# micro-runner and Python preprocessing.
"""
import json
from pathlib import Path
import numpy as np
import pytest

from histra.preprocessing.csharp_fibre_geometry import _csharp_polygon_area
from histra.preprocessing.contact_geometry import _coplanar_quad_intersection_prechecked
from histra.tests.csharp_runner_client import CSharpRunnerClient, get_csharp_runner

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "csharp_quad_contact_intersection_2026_1_1.json"


@pytest.fixture
def csharp_runner() -> CSharpRunnerClient:
    client = get_csharp_runner()
    if not client.is_available():
        pytest.skip("C# HiStrA .NET MicroRunner binary is not available in this environment")
    return client


def test_csharp_polygon_clipping_live_fixtures(csharp_runner: CSharpRunnerClient):
    """Verify Quad contact clipping against live C# micro-runner across reference cases."""
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8-sig"))

    # Test the admitted quadrilateral contact cases (partial_rectangle and containing_diamond)
    for case in fixture["cases"]:
        poly1 = case["first"]
        poly2 = case["second"]
        cs_res = csharp_runner.polygon_clipping(poly1, poly2, include_extreme_nodes=True)

        # Cases where a genuine 4-vertex contact area is formed
        if case["name"] in ("partial_rectangle", "containing_diamond"):
            assert cs_res["code"] == case["code"]
            assert cs_res["count"] == 4

            actual = _coplanar_quad_intersection_prechecked(
                np.asarray(poly1, dtype=float),
                np.asarray(poly2, dtype=float),
                np.array([0.0, 0.0, 1.0]),
                node_tolerance=fixture["node_tolerance"],
            )
            assert actual is not None

            # Check vertex coordinates (accounting for cyclic order / orientation)
            cs_verts = sorted(tuple(np.round(p, 5)) for p in cs_res["vertices"])
            py_verts = sorted(tuple(np.round(p, 5)) for p in actual)
            np.testing.assert_allclose(cs_verts, py_verts, atol=1e-5)

            # Check clipped polygon area bit representation
            py_area = _csharp_polygon_area(np.asarray(actual, dtype=np.float32))
            cs_single_bits = cs_res["area_single_bits"]
            py_single_bits = int(np.asarray([py_area], dtype=np.float32).view(np.int32)[0])
            assert py_single_bits == cs_single_bits



def test_csharp_polygon_clipping_orthogonal_overlap(csharp_runner: CSharpRunnerClient):
    """Test overlapping unit squares with live C# runner."""
    poly1 = [[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [2.0, 2.0, 0.0], [0.0, 2.0, 0.0]]
    poly2 = [[1.0, 1.0, 0.0], [3.0, 1.0, 0.0], [3.0, 3.0, 0.0], [1.0, 3.0, 0.0]]

    cs_res = csharp_runner.polygon_clipping(poly1, poly2, include_extreme_nodes=True)
    assert cs_res["code"] > 0
    assert cs_res["count"] == 4
    # Overlap is [1, 2] x [1, 2], area is 1.0
    assert abs(cs_res["area"] - 1.0) < 1e-9

    actual = _coplanar_quad_intersection_prechecked(
        np.asarray(poly1, dtype=float),
        np.asarray(poly2, dtype=float),
        np.array([0.0, 0.0, 1.0]),
    )
    assert actual is not None
    py_area = _csharp_polygon_area(np.asarray(actual, dtype=np.float32))
    assert abs(py_area - 1.0) < 1e-7
    assert int(np.asarray([py_area], dtype=np.float32).view(np.int32)[0]) == cs_res["area_single_bits"]

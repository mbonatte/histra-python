"""Isolated inverse-iteration references executed from C# 2026.1.1."""
import json
import unittest
from pathlib import Path
import numpy as np
import scipy.sparse as sp
from histra.solver.modal import _inverse_iterations

class TestModalInverse2026(unittest.TestCase):
    def test_eigenpairs_partial_convergence_and_error_traces(self):
        fixture = Path(__file__).parent / "fixtures/modal-inverse-csharp-2026.1.1.json"
        for case in json.loads(fixture.read_text())["cases"]:
            with self.subTest(case=case["Name"]):
                reported = []
                committed = []
                values, vectors = _inverse_iterations(
                    sp.diags(case["K"], format="csc"), sp.csc_matrix(case["M"]), case["Count"],
                    criteria="Frquency", csharp_tolerance=100 * case["EigenTolerance"],
                    residual_tolerance=case["ResidualTolerance"], max_iterations=case["MaxIterations"],
                    should_cancel=None, on_mode=committed.append,
                    on_iteration=lambda iteration, error: reported.append(error),
                )
                np.testing.assert_allclose(values, case["Values"], rtol=2e-13, atol=1e-14)
                expected = np.array(case["Shapes"]).reshape(len(case["K"]), len(case["Values"]))
                np.testing.assert_allclose(vectors, expected, rtol=2e-10, atol=2e-12)
                self.assertEqual(len(reported), case["Iterations"])
                self.assertEqual(committed, list(range(1, len(values) + 1)))
                # Near-zero residuals depend on sparse-solve rounding; retain
                # the full iteration count and compare the reported history.
                np.testing.assert_allclose(reported, case["Errors"], rtol=1e-4, atol=2e-12)

    def test_serialized_criterion_does_not_switch_shared_framework_gates(self):
        kwargs = dict(csharp_tolerance=1e-6, residual_tolerance=1e-8,
                      max_iterations=200, should_cancel=None, on_mode=lambda _: None)
        k, m = sp.diags([4., 18., 48.], format="csc"), sp.diags([1., 2., 3.], format="csc")
        frequency = _inverse_iterations(k, m, 1, criteria="Frquency", **kwargs)
        vector = _inverse_iterations(k, m, 1, criteria="EigenVector", **kwargs)
        np.testing.assert_array_equal(frequency[0], vector[0])
        np.testing.assert_array_equal(frequency[1], vector[1])

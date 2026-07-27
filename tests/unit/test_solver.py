"""Tests for solver components — correct constructors (no-arg defaults)."""
import unittest
from histra.solver.line_search import (
    InitialInterpolatedLineSearch, LineSearch, RegulaFalsiLineSearch,
)
from histra.solver.load_control import LoadControl
from histra.solver.arc_length import ArcLength
from histra.solver.newton_raphson import NewtonRaphson
from histra.solver.newton_line_search import NewtonLineSearch
from histra.solver.solution_algorithm import EquiSolnAlgo, _new_line_search
from histra.types.convergence_test import ConvergenceTest


class TestLineSearch(unittest.TestCase):
    def test_line_search_noop(self):
        ls = LineSearch()
        self.assertEqual(ls.tolerance, 0.8)

    def test_regula_falsi_construction(self):
        rfls = RegulaFalsiLineSearch()
        self.assertIsNotNone(rfls)


class TestNewLineSearchFactory(unittest.TestCase):
    class FakeAnalysis:
        method = "StandardInitialInterpolatedLineSearch"
        line_search_tolerance = 0.5
        line_search_max_eta = 5.0
        line_search_min_eta = 0.2
        line_search_max_iterations = 50

    def test_produces_initial_interpolated(self):
        an = self.FakeAnalysis()
        ls = _new_line_search(an)
        self.assertIsInstance(ls, InitialInterpolatedLineSearch)
        self.assertEqual(ls.tolerance, 0.5)
        self.assertEqual(ls.max_eta, 5.0)
        self.assertEqual(ls.min_eta, 0.2)
        self.assertEqual(ls.max_iter, 50)


class TestLoadControl(unittest.TestCase):
    def test_create(self):
        lc = LoadControl()
        self.assertIsNotNone(lc)

    def test_default_lambda(self):
        lc = LoadControl()
        self.assertEqual(lc.state.lambda_, 0.0)


class TestArcLength(unittest.TestCase):
    def test_create(self):
        al = ArcLength()
        self.assertIsNotNone(al)

    def test_default_lambda(self):
        al = ArcLength()
        self.assertEqual(al.state.lambda_, 0.0)


class TestEquiSolnAlgo(unittest.TestCase):
    def test_create(self):
        ct = ConvergenceTest(tolerance=1e-6, max_iter=10)
        sa = EquiSolnAlgo()
        sa.the_test = ct
        self.assertIs(sa.the_test, ct)

    def test_new_equi_soln_algo(self):
        class FakeAnalysis:
            method = "StandardNewtonRaphson"
            convergence_tolerance = 1e-6
            max_iterations = 10
            max_u = 1e30
            integration_method = "LoadControl"
            initial_load = 1.0
            num_steps = 1
        an = FakeAnalysis()
        algo = EquiSolnAlgo.new_equi_soln_algo(an, 1)
        self.assertIsInstance(algo, EquiSolnAlgo)


class TestNewtonRaphson(unittest.TestCase):
    def test_create(self):
        nr = NewtonRaphson()
        self.assertIsInstance(nr, NewtonRaphson)


class TestNewtonLineSearch(unittest.TestCase):
    def test_create(self):
        nls = NewtonLineSearch()
        self.assertIsInstance(nls, NewtonLineSearch)
        self.assertIsInstance(nls, EquiSolnAlgo)


if __name__ == "__main__":
    unittest.main()

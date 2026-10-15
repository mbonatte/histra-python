"""Original StaticIntegrator.UpdateK fallback on a real assembled one-DOF Quad."""
import json
from pathlib import Path
import unittest

import numpy as np

from histra.elements.quad import Quad
from histra.model.model import Model, Collections
from histra.solver.arc_length import ArcLength
from histra.solver.program import Program
from histra.solver.model_manager import ModelManager
from histra.solver.state_snapshot import SolverStateSnapshot
from histra.springs.hysteretic import SpringHysteretic
from histra.types.afference_entry import AfferenceEntry
from histra.types.linear_system import LinearSystem, LinearSolveError


def doubles(values):
    return np.array([int(v) for v in values],dtype=np.int64).view(np.float64)


class NativeStaticTangentFallbackTests(unittest.TestCase):
    def test_regular_fallback_and_unrecoverable_native_cases(self):
        fixture = json.loads((Path(__file__).parent / 'fixtures' /
                              'csharp_static_tangent_fallback_2026_1_1.json').read_text(encoding='utf-8-sig'))
        for case in fixture['cases']:
            with self.subTest(case=case['name']):
                quad = Quad(key=1, length=case['length'], diago=case['diago'],
                            sin=case['sin'], cos=case['cos'],
                            spring=SpringHysteretic(k=case['k'], k_tang=case['tangent']))
                quad.aff = [[] for _ in range(6)] + [[AfferenceEntry(1,1.)]]
                collections = Collections()
                collections.quads = {1:quad}
                model = Model(gdl=1, collections=collections)
                ls = LinearSystem(1, backend='superlu')
                ls.b[:] = doubles(case['b_bits'])
                program = Program(ls=ls, u=np.zeros(1), v=np.zeros(1))
                integrator = ArcLength()
                ModelManager.compute_ktang(model,ls,0.)
                snapshot = SolverStateSnapshot.capture(model,program,ls,integrator)
                if case['status']:
                    with self.assertRaises(LinearSolveError):
                        integrator.update_k(program,model,1.)
                    self.assertNotEqual(program.index_fact_k,0)
                    continue
                self.assertEqual(integrator.update_k(program,model,1.),0)
                np.testing.assert_array_equal(ls.k.toarray().ravel(),doubles(case['matrix_bits']))
                # SuperLU is the portable test backend; native fixtures use
                # UMFPACK. Require exact assembly and near-machine solve parity.
                np.testing.assert_allclose(ls.x,doubles(case['x_bits']),rtol=1e-15,atol=0.)
                np.testing.assert_array_equal(ls.b,doubles(case['b_bits']))
                self.assertEqual(program.index_fact_k,case['status'])
                if case['alpha'] == 0.:
                    self.assertEqual(program.static_tangent_alpha,0.)
                    snapshot.restore()
                    # C# alfa is an analysis-local ref parameter, outside
                    # element/integrator trial state and rollback checkpoints.
                    self.assertEqual(program.static_tangent_alpha,0.)
                    quad.spring.k_tang = 6.
                    integrator.update_k(program,model,1.)
                    np.testing.assert_array_equal(ls.k.toarray().ravel(),doubles(case['next_matrix_bits']))
                    np.testing.assert_allclose(ls.x,doubles(case['next_x_bits']),rtol=1e-15,atol=0.)
                else:
                    self.assertIsNone(program.static_tangent_alpha)

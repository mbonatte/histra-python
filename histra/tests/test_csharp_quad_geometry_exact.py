"""Exact corner geometry from freshly executed C# Quad.SetGeometry."""
import json
from pathlib import Path
import unittest
import numpy as np
from histra.preprocessing.quad_geometry import compute_quad_geometry_batch
from histra.preprocessing.csharp_math import POWER_BACKEND


@unittest.skipUnless(POWER_BACKEND == 'dotnet-framework-crt', 'Windows Framework arithmetic required')
class NativeQuadGeometryTests(unittest.TestCase):
    def test_original_corner_geometry_exact(self):
        fixture=json.loads((Path(__file__).parent/'fixtures/csharp_quad_geometry_exact_2026_1_1.json').read_text(encoding='utf-8'))
        for case in fixture['cases']:
            arrays=compute_quad_geometry_batch(np.array([case['points']],dtype=np.float32),np.array([case['thickness']],dtype=np.float32))
            for index,field in enumerate(('Length','Diago','Cos','Sin')):
                with self.subTest(key=case['key'],field=field):
                    np.testing.assert_array_equal(arrays[index][0],case[field])

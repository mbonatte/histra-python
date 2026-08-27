"""Unit tests for Quad.update_domain hysteretic_type dispatch on Coulomb springs."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock
import numpy as np

from histra.elements.quad import Quad
from histra.elements.quad_state import QuadState
from histra.springs.coulomb03 import SpringCoulomb03
from histra.springs.elastic import SpringElastic
from histra.types.phase_enum import PhaseEnum


class TestQuadCoulombInitialDispatch(unittest.TestCase):
    """Test Quad.update_domain dispatch based on hysteretic_type."""

    def setUp(self):
        self.quad = Quad()
        self.quad.key = 1
        self.quad.status = QuadState()
        self.quad.node_keys = [1, 2, 3, 4]
        # Mock aff pairs and geometry helpers
        self.quad._local_increment = MagicMock(return_value=np.zeros(7))
        self.quad.d_alfa_2d_diag = MagicMock(return_value=1.0)
        self.quad.compute_dn = MagicMock(return_value=(15.0, 50.0))
        self.quad.compute_volume = MagicMock(return_value=100.0)

    def test_coulomb_initial_dispatch(self):
        """When hysteretic_type is 'Initial', quad.update_domain calls set_trial_strain_initial and sets dn."""
        spring = SpringCoulomb03(
            k=2000.0,
            cohesion=100.0,
            mu=0.5,
            hysteretic_type="Initial",
        )
        self.quad.spring = spring

        collections = MagicMock()
        collections.materials = {self.quad.material_key: MagicMock()}
        state = MagicMock()
        state.step = 1

        x = np.zeros(7)
        self.quad.status.u[6] = 0.02
        self.quad.update_domain(x, state, collections=collections)

        self.assertEqual(spring.dn, 15.0)
        self.assertAlmostEqual(spring._tstrain, 0.02)
        self.assertEqual(self.quad.sigma_initial, 50.0)

    def test_coulomb_takeda_dispatch(self):
        """When hysteretic_type is 'Takeda', quad.update_domain calls set_trial_strain_takeda_diagonal_quad."""
        spring = SpringCoulomb03(
            k=2000.0,
            cohesion=100.0,
            mu=0.5,
            hysteretic_type="Takeda",
        )
        self.quad.spring = spring

        collections = MagicMock()
        collections.materials = {self.quad.material_key: MagicMock()}
        state = MagicMock()
        state.step = 1

        x = np.zeros(7)
        self.quad.status.u[6] = 0.02
        self.quad.update_domain(x, state, collections=collections)

        self.assertAlmostEqual(spring._tstrain, 0.02)
        self.assertEqual(self.quad.sigma_initial, 50.0)

    def test_elastic_spring_dispatch(self):
        """When spring is SpringElastic, quad.update_domain calls standard set_trial_strain."""
        spring = SpringElastic(k=5000.0)
        self.quad.spring = spring

        state = MagicMock()
        x = np.zeros(7)
        self.quad.status.u[6] = 0.01
        self.quad.update_domain(x, state)

        self.assertAlmostEqual(spring.get_force(), 50.0)


if __name__ == "__main__":
    unittest.main()

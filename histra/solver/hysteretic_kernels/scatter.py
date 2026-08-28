"""Compiled force-scatter kernels for the nonlinear batch runtime.

Fixed-topology local/global force scatter, force-by-DOF refresh and the
max-displacement cache update. The scatter topology is built once per
preparation (see :mod:`histra.solver.hysteretic_topology`) and reused verbatim
in every Newton correction, so these kernels never touch Python objects.

No ``fastmath`` is used; the dense state column constants are imported from
the kernel modules that own them.
"""
from __future__ import annotations

import numpy as np

from histra.solver.hysteretic_kernels.quad_takeda import QTSTRESS

try:  # optional acceleration dependency
    from numba import njit, prange
except Exception:  # pragma: no cover - exercised when numba is unavailable
    njit = None
    prange = None


if njit is not None:
    @njit(cache=True, nogil=True)
    def _scatter_local_forces(local_forces, offsets, gdls, coefficients, global_force):
        flat = local_forces.reshape(local_forces.size)
        for local_index in range(flat.size):
            force = flat[local_index]
            if force == 0.0:
                continue
            for pair_index in range(offsets[local_index], offsets[local_index + 1]):
                gdl = gdls[pair_index]
                if 0 <= gdl < global_force.size:
                    global_force[gdl] -= force * coefficients[pair_index]

    @njit(cache=True, nogil=True)
    def _refresh_global_resisting_force(
        quad_d_alfa, quad_state, quad_forces,
        quad_offsets, quad_gdls, quad_coefficients,
        interface_forces, interface_offsets, interface_gdls,
        interface_coefficients, global_force,
    ):
        global_force[:] = 0.0
        for i in range(quad_forces.shape[0]):
            quad_forces[i, 0] = quad_d_alfa[i] * quad_state[i, QTSTRESS]
        _scatter_local_forces(
            interface_forces, interface_offsets, interface_gdls,
            interface_coefficients, global_force,
        )
        _scatter_local_forces(
            quad_forces, quad_offsets, quad_gdls, quad_coefficients,
            global_force,
        )

    @njit(cache=True, nogil=True, parallel=True)
    def _refresh_global_resisting_force_by_dof(
        quad_d_alfa, quad_state, quad_forces, interface_forces,
        global_offsets, force_indices, force_coefficients,
        interface_force_size, global_force,
    ):
        """Assemble independent global DOFs with C#-ordered afferences.

        ``force_indices`` is prepared once in the same Interface-then-Quad,
        local-DOF, afference order used by ``_scatter_local_forces``.  Each
        global DOF can therefore be reduced independently without changing
        the order of any floating-point additions.
        """
        for i in range(quad_forces.shape[0]):
            quad_forces[i, 0] = quad_d_alfa[i] * quad_state[i, QTSTRESS]

        interface_flat = interface_forces.reshape(interface_forces.size)
        quad_flat = quad_forces.reshape(quad_forces.size)
        for gdl in prange(global_force.size):
            total = 0.0
            for position in range(global_offsets[gdl], global_offsets[gdl + 1]):
                force_index = force_indices[position]
                if force_index < interface_force_size:
                    force = interface_flat[force_index]
                else:
                    force = quad_flat[force_index - interface_force_size]
                if force != 0.0:
                    total -= force * force_coefficients[position]
            global_force[gdl] = total

    @njit(cache=True, nogil=True)
    def _refresh_max_u_cache(quad_local_u, interface_max_u, cache):
        quad_value = 0.0
        quad_index = -1
        kind = 0
        for i in range(quad_local_u.shape[0]):
            for j in range(quad_local_u.shape[1]):
                candidate = abs(quad_local_u[i, j])
                if candidate > quad_value:
                    quad_value = candidate
                    quad_index = i
                    kind = 1
        value = quad_value
        index = quad_index
        for i in range(interface_max_u.size):
            candidate = abs(interface_max_u[i])
            if candidate > value:
                value = candidate
                index = i
                kind = 2
        cache[0] = value
        cache[1] = index
        cache[2] = kind
        cache[3] = quad_value
        cache[4] = quad_index



else:  # pragma: no cover - exercised when numba is unavailable
    _scatter_local_forces = None
    _refresh_global_resisting_force = None
    _refresh_global_resisting_force_by_dof = None
    _refresh_max_u_cache = None

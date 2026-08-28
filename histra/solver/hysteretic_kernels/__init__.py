"""Compiled hysteretic kernel ownership for the nonlinear batch runtime.

Kernels are grouped by element family and split out of
:mod:`histra.solver.hysteretic_batch` one commit at a time. The package exists
so each kernel family can own its constants and compiled code while the batch
runtime keeps a stable compatibility facade.
"""

from histra.solver.hysteretic_kernels.transverse import (
    _advance_and_evaluate_simple_linear_batch,
    _advance_evaluate_and_finish_simple_linear_batch,
    _advance_transverse_targets,
    _evaluate_linear_batch,
    _evaluate_simple_linear_batch,
    _finish_transverse_batch,
)

__all__ = [
    "_advance_and_evaluate_simple_linear_batch",
    "_advance_evaluate_and_finish_simple_linear_batch",
    "_advance_transverse_targets",
    "_evaluate_linear_batch",
    "_evaluate_simple_linear_batch",
    "_finish_transverse_batch",
]

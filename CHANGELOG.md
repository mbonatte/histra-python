# Changelog

## 1.2.1 - 2026-09-23

Graph partitioning matrix ordering, adaptive tangent refresh, interface scalar geometry caching, and large-scale 3D solver acceleration.

### Performance & Solver Optimization

- **METIS Graph Partitioning Matrix Ordering**: Enabled SuiteSparse UMFPACK METIS ordering by default for sparse stiffness factorization, reducing $L+U$ fill-in non-zeros by 4.3x (from 202.5M to 47.3M non-zeros on Dhir Bridge) and cutting numeric factorization time by 2.2x. Configurable via `linear_solver_ordering` and `HISTRA_UMFPACK_ORDERING`.
- **Adaptive Tangent Refresh & Cadence Newton**: Implemented residual contraction tracking (`last_contraction = error / last_error`) and cadence refresh in `NewtonLineSearch` for standard line searches, skipping redundant tangent factorizations while maintaining quadratic convergence.
- **Interface Geometry Precomputation Cache**: Precomputed invariant interface coordinate sums ($\sum d_i^2$, $\sum d_j^2$, $\sum d_i d_j$, $\sum e^2$, $\sum d_m^2$) during model preparation, enabling $O(1)$ closed-form elastic interface evaluation for uniform spring arrays in `_compute_kfless`.
- **Flexible Analysis Key Resolution**: Supported integer analysis keys in `solve_static_nonlinear` and `_setup_nonlinear_analysis`, ensuring analysis method and solver configurations are properly resolved when passed by ID.

## 1.2.0 - 2026-09-21

Fast linear solve acceleration, configurable UMFPACK iterative refinement, and non-linear solver performance optimizations.

### Performance & Solver Optimization

- **Default Fast Linear Solve Mode (`linear_solver_precision="fast"`)**: Configured UMFPACK `IRSTEP=0` by default, skipping iterative refinement and accelerating sparse back-substitutions by up to 3.24x while preserving $< 10^{-11}$ accuracy.
- **Strict C# Parity Opt-In**: Provided `linear_solver_precision="strict"` (and `HISTRA_LINEAR_SOLVER_PRECISION=strict`) to retain `IRSTEP=2` for bit-exact reference verification.
- **Vectorized Line-Search Dot Products**: Line search now uses vectorized BLAS (`np.dot`) when `csharp_line_search_compatibility=False` or `linear_solver_precision="fast"`.
- **Adaptive Tangent Refresh Architecture**: Added configurable periodic and stall-triggered tangent refreshment options in `NewtonLineSearch` and `NewtonRaphson`.

## 1.1.0 - 2026-09-21

Comprehensive performance optimization, solver acceleration, compiled backend pre-warming, and analytical C# parity documentation release.

### Performance & Solver Optimization

- **Zero-Copy UMFPACK Direct Solves**: Eliminated vector allocations during UMFPACK linear solves by directly storing results into `self.x` and passing direct memory pointers via `ctypes.c_void_p`.
- **Reusable Scratch Buffers in Newton Line-Search**: Pre-allocated reusable scratch arrays in `NewtonLineSearch` (`_scratch_residual0`, `_scratch_dx0`, `_scratch_direction`) to avoid intermediate vector allocations during iterations.
- **Fast Tangent Stiffness Assembly**: Added `sync_tangents_to_objects` option to `ModelManager.assemble_tangent_stiffness_matrix()` to bypass synchronization of individual Python spring objects during Newton matrix assembly.
- **Pre-Compiled Backend Warmup**: Added `histra.solver.warmup.warmup_compiled_backends()` to eliminate JIT compilation latency on the initial step of nonlinear analyses, integrated into `run_vert_live`.
- **Sutherland-Hodgman Polygon Clipping**: Optimized 2D polygon intersection kernel with hoisted edge math, inlined coordinate bounds, and cached coplanar intersection checking.
- **Broadphase Geometry Filtering**: Accelerated interface contact candidate filtering via compiled Numba pair search routines (`_find_broad_pairs_nb`, `_find_face_candidates_nb`).

### Analytical Engine & Parity Documentation

- **6-Chapter C# vs Python Parity Audit**: Comprehensive line-by-line mechanical and algorithmic audit covering data structures, preprocessing, constitutive models, nonlinear solvers, modal analysis, and input/output (`docs/audit/`).

## 1.0.0 - 2026-09-20

First private production release of the Python HiStrA masonry solver.

### Included

- Quad/Interface masonry preprocessing, six-face contacts, afference, self-weight,
  load combinations, staged dependencies, restart/state transfer, and interface
  material changes.
- Force- and displacement-controlled nonlinear static analysis with LoadControl,
  ArcLength, ArcLengthLinear, Newton and supported line-search variants.
- ForceMoment, DispRotation, and Work convergence criteria with an independent
  equilibrium audit; strict execution rejects unsafe committed states.
- P-Delta EachStep and EachIteration paths.
- Modal eigensolution, participation, effective mass, and mode-shape projection.
- Explicit capability preflight and solver-strategy advisories.

### Qualification & Verification
 
- Fresh brand-new Python preprocessing enforced across all benchmarks and entry points; never solves on serialized `.hrx` computational objects.
- All 14 Article models benchmarked in authored mode under fresh preprocessing with full step history and curve parity against `Original_article_data.csv`.
- Five-stage interface material chain qualified under fresh preprocessing with 0 unmanaged objects.
- P-Delta gravity strategy matrix requalified with 3 fresh-model repeats recommending `authored-each-step`.
- 100% compiled backend enforcement verified across initialization, restart, and post-mutation boundaries.
- Clean wheel and sdist built, byte-verified against source, and smoke-tested in isolated clean virtual environments.

### Release Status

The implementation, packaging, fresh-preprocessing verification, and local test matrix are complete.
Ready for remote CI execution on push and `v1.0.0` tagging. See `docs/release/v1-release-checklist.md`.

# Changelog

## 1.3.0 - 2026-10-07

In-place state modernization: contiguous array-backed transverse fiber groups, 45x faster preprocessing spring allocation, 109x faster solver synchronization, and 3.7x–8x active memory reduction with 100% bit-exact C# parity.

### Performance & Memory Modernization

- **Array-Backed `TransverseFiberGroup` (`histra.springs.transverse_fiber_group`)**: Replaced individual Python `SpringHysteretic` dataclass instances and nested lists with contiguous NumPy array storage for parameters, stiffnesses, contact areas, and constitutive states. Slashes transverse spring allocation time from 13.93s down to 0.31s (45.2x speedup) on 550,000-fiber models and eliminates >4.4M Python heap objects.
- **On-Demand Proxy Compatibility**: Implemented standard `MutableSequence` interface on `TransverseFiberGroup` with transparent, on-demand `SpringHysteretic` proxy instantiation, preserving complete backward compatibility for external diagnostic tools and inspection readers.
- **Zero-Copy Dense Solver Synchronization**: Vectorized runtime state synchronization (`sync_all_to_objects`, `sync_tangents_to_objects`, `sync_interface_trial_to_objects`) directly between compiled Numba solver arrays and `TransverseFiberGroup` slices, cutting per-boundary synchronization latency from 1.88s down to 0.017s (109.4x speedup).
- **Virtual Sequence Mapping (`histra.solver.hysteretic_runtime`)**: Introduced `_VirtualSpringSequence` and `_VirtualManagedSequence` wrappers, avoiding allocation of 500k+ pointer arrays for runtime spring collections.
- **Material Chaining & Mutation**: Optimized `change_interface_materials` to transfer committed history directly across `TransverseFiberGroup` arrays without materializing scalar objects.
- **Heap & RSS Memory Footprint**: Reduced pymalloc tracked heap memory from 651 MB to 176 MB (3.7x reduction) and active RSS on canonical bridge benchmarks to ~400–500 MB.

## 1.2.3 - 2026-10-06

Fresh Quad geometry reconstruction and regression coverage for C# compatibility.

### Fixes

- Recompute Quad edge lengths, diagonals, corner angles, local axes, and thickness-weighted centroids from structural nodes before afference and spring generation, using a compiled Numba batch routine with C# Single arithmetic compatibility.
- Invalidate older preprocessing caches so prepared models use refreshed geometry.
- Add C# Dhir geometry fixtures and regression tests for distorted Quads, variable thickness, degenerate geometry, and rigid hysteretic placeholders.
- Include CI test corrections and CHOLMOD fallback fixes committed since 1.2.2.

### Tools

- Add a sparse linear solver benchmark harness and optional PyAMG preconditioning for PCG, with SSOR fallback when PyAMG setup fails.

## 1.2.2 - 2026-09-23

Native CHOLMOD supernodal Cholesky backend, preprocessing mesh & topology disk caching, Preconditioned Conjugate Gradient (PCG) iterative solver, and Quasi-Newton (BFGS) solver architecture.

### Performance & Solver Optimization

- **Native CHOLMOD Supernodal Backend (`histra.types.cholmod`)**: Direct ctypes binding to SuiteSparse `libcholmod.so.5` with zero-copy memory arrays and supernodal Cholesky factorization (`backend="cholmod"`). Slashes symbolic analysis time by 9.5x (from 6.70s to 0.70s) and numeric factorization time by 2.3x (from 5.89s to 2.55s) on large 3D models.
- **Preprocessing Mesh & Topology Caching (`histra.preprocessing.cache`)**: Transparent atomic disk and memory caching keyed by SHA-256 fingerprint of the source HRX file and code revision. Reduces model preparation time on Dhir Bridge from 30.40s down to 8.36s (3.6x speedup) while preserving fresh Python preprocessing parity rules.
- **Preconditioned Conjugate Gradient Solver (`histra.types.pcg`)**: Matrix-free iterative solver supporting Symmetric Successive Over-Relaxation (SSOR) and Jacobi (diagonal scaling) preconditioning with automatic fail-safe fallback to direct solvers (`backend="pcg"`).
- **Quasi-Newton (BFGS) Architecture (`histra.solver.bfgs`)**: Implemented Matthies & Strang (1979) two-loop recursion with Powell curvature safeguards (`curv > 1e-8 * norm_s * norm_y`), bounded memory history, and automatic tangent refresh upon stall detection (`method="BFGS"`). Combined with CHOLMOD, cuts 2-step Dhir Bridge runtime from >400s down to 46.45s with exact physical equilibrium ($1.19 \times 10^{-9}$).

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

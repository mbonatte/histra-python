# HiStrA Python refactoring architecture

This document is the working contract for the architecture-wide refactor. The
primary invariant is numerical fidelity to the supplied C# implementation and
its committed SQLite results. Runtime improvements are accepted only with
equal or stronger parity evidence.

## Baseline (2026-08-28)

- Production and test code under `histra/`: 38,092 lines.
- Tests: 53 files and 9,780 lines.
- C# reference: 1,854 source files.
- Baseline suite: 376 passed, 5 skipped, 16 expected safety warnings in
  109.90 seconds on the reference workstation.
- Largest production modules:

  | Module | Lines | Main responsibilities currently mixed together |
  |---|---:|---|
  | `solver/hysteretic_batch.py` | 4,938 | Numba laws, topology, object adapters, state storage, runtime orchestration |
  | `preprocessing/prepare_model.py` | 3,921 | constitutive laws, contact geometry, afference, spring creation, preparation orchestration |
  | `solver/assembler.py` | 1,263 | interface stiffness, sparse topology, boundary conditions, load generation |
  | `elements/quad.py` | 1,225 | static loads, stiffness, nonlinear state, geometry and XML parsing |
  | `springs/coulomb03.py` | 1,118 | parameters, state transitions, force/tangent queries and serialization |
  | `solver/solve.py` | 949 | setup, restart, nonlinear step loop, safety audit, ALS and result records |

### Verified slices

1. Load assembly was extracted from `solver/assembler.py` into
   `solver/load_assembly.py`. C# `Gamma × Psi` and `GC` coefficient branches
   now have exhaustive table-driven tests. The default suite after this slice
   is 407 passed, 5 skipped, 12 expected safety warnings in 81.77 seconds—a
   25.6% reduction from the measured baseline.
2. Interface-local stiffness is owned only by `elements/interface.py`, matching
   C# `Objects/Interface.cs`. The duplicate flexural, sliding and out-of-plane
   implementations were removed from `solver/assembler.py`; standalone global
   assembly delegates once to each element while the nonlinear path consumes
   precomputed blocks through its fixed sparse topology. The assembler is now
   747 lines, down from 1,263 at baseline. Strict delegation, bitwise scalar
   parity and cached-scatter tests pass. The complete suite is 418 passed,
   5 skipped and 12 expected safety warnings in 76.40 seconds—6.6% faster than
   the preceding slice and 30.5% faster than the original baseline, despite 11
   additional strict tests.
3. Masonry material mapping is now owned by
   `preprocessing/constitutive_laws.py`; `prepare_model.py` retains compatibility
   aliases while shrinking from 3,921 to 3,715 lines. Direct comparison with
   C# `ConstitutiveLawOperations.cs` and `MasonryMaterial.AlfaShear` exposed and
   fixed three parity defects: shear-alpha boundary clamping, inversion of the
   shear ductility flag into `IsDuctilityFixed`, and out-of-plane vertical
   sliding's domain/energy selection. Exact tests cover every flexural and
   shear constructor field, all six sliding slots, float32 material rounding,
   and the C# diagonal elasto-plastic asymmetry. The complete suite is 438
   passed, 5 skipped and the same 12 expected safety warnings in 74.54 seconds,
   2.4% faster than the preceding slice and 32.2% faster than baseline.
4. Scalar and NumPy-batched spring construction is now owned by
   `preprocessing/spring_factory.py`. The stable private names remain identity
   aliases in `prepare_model.py`, whose size is reduced again from 3,715 to
   2,884 lines. Existing bit-exact scalar/batch differentials and independent
   mutable-state tests pass through the new owner, and a dedicated architecture
   test locks every compatibility alias. The 126-DOF preparation benchmark
   preserved its topology and numerical error signature while measuring 0.533
   seconds versus 0.569 seconds immediately before extraction. The complete
   suite is 439 passed, 5 skipped and the same 12 warnings in 74.88 seconds,
   statistically flat versus the previous gate and 31.9% faster than baseline.
5. Quad contact detection and interface topology generation are now owned by
   `preprocessing/contact_geometry.py`, including the NumPy broad-phase
   prefilter, exact clipping fallback, XNA float32 vector operations, geometric
   node index and six-face Quad geometry cache. `prepare_model.py` is reduced
   from 2,884 to 2,012 lines, 48.7% below its original size. Conservative
   prefilter differentials, topology/afference reconstruction, offset-contact
   cases and all compatibility identities pass. The numerical benchmark
   signature remained unchanged at 0.538 seconds, and the complete suite is
   440 passed, 5 skipped and the same 12 warnings in 75.24 seconds—flat against
   the preceding gates and 31.5% faster than baseline.
6. Quad/Interface afference mapping and the float32 bilinear/inverse-bilinear
   interpolation are now owned by `preprocessing/afference.py`, including the
   C# bisection reference, the scalar float32 Newton path and the bit-exact
   Numba kernels. `prepare_model.py` is reduced from 2,012 to 1,366 lines,
   65.6% below its original size, and keeps identity re-exports locked by a
   dedicated architecture test. The full preprocessing benchmark output
   (interface topology, afference sequence, spring and stiffness error
   signatures) is bit-identical to the preceding commit; preparation measured
   0.465 seconds. The complete suite is 442 passed, 5 skipped and the same 12
   warnings in 75.14 seconds warm (one extra Numba cache rebuild occurred on
   the first run after the module move)—flat against the preceding gate.
7. Interface spring-cell geometry and the C# ``Quad.GetFiberProperties`` fibre
   kernels are now owned by `preprocessing/fibre_geometry.py`: scalar
   cell/area/fibre oracles plus the Numba batch family, importing the
   bilinear maps from `preprocessing.afference`. `prepare_model.py` is reduced
   from 1,366 to 906 lines, 76.9% below its original size, and keeps identity
   re-exports locked by a dedicated architecture test. The compiled
   bilinear/inverse-bilinear operation order, the scalar-fallback path (via
   owner-module `njit` patching) and the batch-vs-scalar fibre differentials
   are covered at the owner. The full preprocessing benchmark output is
   bit-identical to the preceding commit; preparation measured 0.526 seconds.
   The complete suite is 444 passed, 5 skipped and the same 12 warnings in
   74.66 seconds—flat against the preceding gate.
8. Masonry material lookup and constitutive-law selection/blending are now
   owned by `preprocessing/material_selection.py`, with no dependency on
   spring construction. `prepare_model.py` is reduced from 906 to 756 lines,
   80.7% below its original size, and keeps identity re-exports locked by a
   dedicated architecture test. New owner-level tests cover cache keys and
   one-parse-per-material/orientation behavior, broad faces 4/5 selecting the
   direction-3 law, interface/quad e1 alignment weighting in the orthotropic
   blend, restraint parents resolving the Quad side, the primary runtime law
   type surviving `PropOrthotropyParameter`, and explicit failure on missing
   material keys. The full preprocessing benchmark output is bit-identical to
   the preceding commit; preparation measured 0.536 seconds. The complete
   suite is 454 passed, 5 skipped and the same 12 warnings in 75.12
   seconds—flat against the preceding gate.

## Dependency rules

1. `model` and `types` are data foundations and must not import solver
   orchestration.
2. `elements` and `springs` own scalar C#-parity behavior. They must not know
   about sessions, persistence or benchmark tooling.
3. `preprocessing` builds geometry, topology and constitutive definitions. Its
   public orchestrator delegates to focused modules.
4. `solver` owns numerical algorithms and compiled batch runtimes. Load,
   stiffness, continuation, convergence and persistence adapters remain
   separate responsibilities.
5. `io` reads/writes formats and must not initiate a solve.
6. Compatibility facades may re-export moved APIs, but production imports use
   the owning module directly so obsolete boundaries cannot regrow silently.

## Target module boundaries

### Assembly

- `solver/load_assembly.py`: C# `LoadTemplateManager` coefficient resolution,
  static load generation and global load-vector assembly.
- `solver/assembler.py`: sparse stiffness assembly and boundary conditions.
- `elements/interface.py`: C# interface-local flexural, sliding and
  out-of-plane stiffness formulas and geometry caches.

### Model preparation

- `preprocessing/constitutive_laws.py`: masonry-to-spring parameter mapping.
- `preprocessing/contact_geometry.py`: contact detection, clipping and interface
  cell geometry.
- `preprocessing/afference.py`: Quad/Interface generalized-DOF mappings.
- `preprocessing/spring_factory.py`: scalar and batched spring construction.
- `preprocessing/prepare_model.py`: validation and orchestration facade only.

### Compiled hysteretic runtime

- `solver/hysteretic_kernels/`: Numba kernels grouped by transverse,
  Coulomb/sliding, Quad diagonal and scatter/update responsibilities.
- `solver/hysteretic_topology.py`: immutable compact topology and extraction.
- `solver/hysteretic_runtime.py`: state ownership and object synchronization.
- `solver/hysteretic_batch.py`: stable compatibility exports and constructor.

### Nonlinear solve

- setup/restart, nonlinear step execution, ALS/cutback and committed-result
  projection become separate modules.
- C# execution order remains explicit and covered by sequence-sensitive tests.

## C# comparison map

Each refactor slice names and reads its authoritative source before edits:

| Python responsibility | Primary C# authority |
|---|---|
| Load coefficients | `CommonObjectManagement/LoadTemplateManager.cs` |
| Global load/stiffness lifecycle | `SolverRuntime/ModelManager.cs` |
| Nonlinear analysis order | `SolverRuntime.AnalysisProcedure/StaticNonLinearAnalysis.cs` |
| Newton algorithms | `SolverRuntime.NumericalProcedure/*.cs` |
| Convergence criteria | `SolverRuntime.ConvergenceTest/*.cs` |
| Arc length/load control | `SolverRuntime.Integrator/*.cs` |
| Element state machines | `Objects/Quad.cs`, `Objects/Interface.cs`, generated spring sources |

Intentional fixes to C# defects must be opt-in or documented separately from
the default parity path. Accidental C# behavior needed by existing result files
is preserved and tested explicitly.

## Test gates

Every slice must pass all applicable gates:

1. Table-driven unit tests cover every moved branch and reject unknown enum or
   state values instead of silently defaulting.
2. Scalar-vs-Numba differential tests compare complete state arrays, not only
   final forces.
3. C# parity tests use explicit step keys and tight absolute plus relative
   bounds. Vague checks such as “values differ” are insufficient.
4. Performance tests warm JIT separately, report setup and steady-state time,
   and assert a conservative regression ceiling.
5. The full default suite must not become slower. Expensive integration tests
   reuse authoritative C# checkpoints where doing so tests the same contract.
6. Long acceptance suites remain available through explicit environment flags
   and are run at architecture milestones.

## Refactor sequence

1. Separate load assembly and complete C# coefficient coverage. **Complete.**
2. Split stiffness formulas from sparse topology/scatter assembly. **Complete.**
3. Split model preparation along constitutive, geometry, afference and factory
   boundaries. **Constitutive mapping, contact geometry, spring factory and
   afference complete.**
4. Split compiled hysteretic kernels and runtime state ownership.
5. Split the static nonlinear driver and make execution-order tests exhaustive.
6. Split large element and spring classes only after their scalar/compiled
   differential coverage is complete.
7. Run the full C# benchmark inventory and long acceptance suites, then audit
   public API compatibility and dependency cycles before declaring the
   architecture refactor complete.

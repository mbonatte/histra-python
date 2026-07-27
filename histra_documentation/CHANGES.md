# Changes Made

## Solver and elements

- Implemented C#-compatible quad volume, normal stress, and `ComputeDN` behavior.
- Implemented interface normal-force increment and area correction paths.
- Coupled `dN` into in-plane and out-of-plane Coulomb03 springs.
- Changed nonlinear element update order to interfaces before quads.
- Implemented the active C# `TwoSprings` out-of-plane stiffness branch.
- Matched float32-sensitive C# self-weight and geometry calculations.
- Completed Coulomb03 normal-stress commit/revert and yield restoration.
- Recorded convergence, residual, and increment norms per step.

## State safety

- Added `SolverStateSnapshot` for complete capture, restore, and value fingerprinting.
- Added rollback to Newton, line-search, failed step, ALS substep, and ArcLength retry flows.
- Removed trial-only attributes during restore.

## Database and restart

- Added typed metadata, quad, interface, spring, displacement, and multiplier readers.
- Documented zero-based `DynamicVectorsState.Dof` indexing.
- Added strict final committed-state restoration and chained-analysis initialization.
- Rejected incomplete intermediate spring restart with precise errors.

## Load behavior

- Added explicit errors for missing analyses, combinations, rows, gravity conditions, unsupported coefficient types, and unavailable Psi data.
- Corrected unloading discretization.

## Tests and tools

- Corrected stale package paths and actual model-size assertions.
- Added focused ComputeDN, friction coupling, commit/revert, snapshot, rollback, unloading, SQLite, restart, first-step, and step-reader tests.
- Added `tools/benchmark_csharp_sqlite.py` for machine-readable per-step comparison.

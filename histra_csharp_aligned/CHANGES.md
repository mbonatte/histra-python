# Changes made to the Python translation

## Solver and state

- `LinearSystem.set_zero()` now clears only stiffness values.
- Added robust sparse-solve error handling for rank warnings and non-finite results.
- Added vector setters matching the C# overload semantics.
- Removed guessed boundary-condition elimination from solver paths; HRX active generalized DOFs are solved directly.
- Total displacement remains cumulative across LoadControl steps.
- Rollback restores total displacement, `LS.X`, and element committed state.
- Nonlinear solver returns the real final code and rolls back failed steps.
- Initial stiffness is assembled before the first integrator predictor.

## Newton and convergence

- Standard methods rebuild the requested tangent stiffness.
- Convergence criteria now support `ForceMoment`, `DispRotation`, and `Work` using the C# definitions.
- `max_u` is passed through and max displacement includes interfaces.
- Removed model-specific debug indexing from production iteration loops.

## Line search

- Implemented Regula Falsi, Secant, Bisection, and Initial Interpolated searches.
- Corrected `eta=0/eta=1` initialization.
- Trial updates are incremental from the already applied full Newton step.
- Residual signs are consistent at endpoints and trial points.
- Final `LS.X` is total `eta*dU` without a second domain update.

## Load control and ALS

- Parsed C# `LoadFunctionItem` entities and attached them to their functions.
- Force-based discretization supports unloading/cyclic segments safely.
- ALS removes the failed full increment before substeps.
- A failed substep is undone and reverted before reducing the increment.

## Arc length

- Replaced the previous spherical implementation with the C# `deltaUbar + deltaLambda*deltaUhat` structure.
- Supports control-DOF or all-active-DOF constraint vectors.
- Uses load-function segment direction and displacement targets.
- Preserves adaptive radius between steps.
- Corrects squared/unsquared maximum-radius handling.
- Adds complete failed-step load/displacement snapshots.

## Loading and reporting

- `solve_linear()` now has distinct stiffness and analysis/load arguments.
- Graph values use the actual load multiplier and generalized displacement.
- Energy is returned and accumulated explicitly.
- Enabled P-Delta raises an explicit unsupported-feature error.
- Psi-dependent coefficients raise an explicit unsupported-feature error rather than silently becoming zero.

## Files changed

- `histra/io/hr_loader.py`
- `histra/model/__init__.py`
- `histra/model/load.py`
- `histra/solver/__init__.py`
- `histra/solver/arc_length.py`
- `histra/solver/assembler.py`
- `histra/solver/incremental_integrator.py`
- `histra/solver/line_search.py`
- `histra/solver/load_control.py`
- `histra/solver/model_manager.py`
- `histra/solver/newton_line_search.py`
- `histra/solver/newton_raphson.py`
- `histra/solver/program.py`
- `histra/solver/solution_algorithm.py`
- `histra/solver/solve.py`
- `histra/solver/solver.py`
- `histra/types/__init__.py`
- `histra/types/convergence_test.py`
- `histra/types/linear_system.py`
- `tests/test_csharp_alignment.py`

## Final-archive audit additions

- Parsed `InitialAnalysisKey` and `InitialCombinationAnalysisKey`.
- Stored the absolute HRX source path on `Model`.
- Added the C# `CommonOperations.SetInitial` subset for supported quads, interfaces, and springs.
- Rejected chained analysis restart until complete database state can be restored.
- Repaired test discovery, portable fixture paths, stale API assertions, swallowed exceptions, and pytest return warnings.
- Added an automated first-step comparison against the supplied C# SQLite database.
- Updated documentation to distinguish first-step agreement from full-analysis equivalence.

# Focused C# comparison

## Scope and source quality

The supplied C# archive appears to contain decompiled source. Method structure and calculations are sufficiently clear for the focused comparison, although local variable names and some control-flow formatting are decompiler-generated.

Only solver-critical files connected to the previously reported issues were checked. This was not a review of the complete C# application.

## Findings by previously reported issue

| Python issue | What the C# actually does | Classification | Revision |
|---|---|---|---|
| Python kept solved HRX local state when starting a virgin analysis | C# `ModelManager.SetStatus` calls `CommonOperations.SetInitial` when `InitialAnalysisKey < 0`, resetting global, element, and spring state | Mistranslation | Added supported virgin-state reset and restart-key parsing |
| `LinearSystem.set_zero()` erased `K`, `b`, and `x` | C# `LinearSystem.SetZero()` clears only matrix coefficients; `SetZeroLoad()` and `SetZeroDisplacement()` are separate (`MatrixManager/LinearSystem.cs`, lines 161–185 and 334–340) | Mistranslation | `set_zero()` now clears only `K` |
| Standard Newton used initial stiffness | C# calls `ComputeK(alfa)` and then assembles the current element matrices (`SolverRuntime/ModelManager.cs`, lines 265–270) | Mistranslation | Requested `alfa` is preserved during assembly |
| LoadControl reset total displacement every step | C# `LoadControl.NewStep()` never clears `U`; `Update()` accumulates `U += LS.X` (`LoadControl.cs`, lines 38–58 and 78–83) | Mistranslation | Removed total-displacement reset |
| Rollback raised a Python `TypeError` | C# has `LinearSystem.SetX(Vector)` and rollback passes a complete vector (`StaticIntegrator.cs`, lines 78–102) | Overload mistranslation | Added `set_x_vector()` and corrected rollback |
| Regula Falsi began with two `eta=1` endpoints | C# correctly uses values at `eta=0` and `eta=1`: `num5=0`, `num7=s0`, `num4=1`, `num6=s1` (`RegulaFalsiLineSearch.cs`, lines 53–60) | Mistranslation | Reimplemented the correct bracket |
| Line search double-applied the final increment | C# trial corrections are incremental, then it only places total `eta*dU` in `LS.X` for convergence testing; it does not update the domain again (`RegulaFalsiLineSearch.cs`, lines 82–98 and 141–144) | Mistranslation | Final `LS.X` assignment no longer updates elements |
| Line-search convergence reference norm was zero | C# force convergence is absolute by default and does not use a reference norm (`CTestNormUnbalance.cs`, lines 25–38 and 51–64) | Incorrect Python design | Implemented C# criteria: force, displacement, or work |
| `max_u` was read but not passed to the test | C# constructors receive and store `MaxU` | Mistranslation | `max_u` is now passed and interfaces are included in max-displacement scanning |
| Standard ArcLength predictor could see an empty matrix | C# analysis preparation leaves an assembled/factored stiffness before `NewStep`; ArcLength immediately solves against it | Incomplete Python preparation | Initial stiffness is always assembled before integrator initialization |
| Boundary conditions were reconstructed and zero diagonals were treated as supports | C# omits fixed restraint DOFs while constructing the global afference map. `Restraint.ComputeAff()` adds a GDL only when `K[i] >= 0` (`Objects/Restraint.cs`, lines 1303–1316) | Incorrect Python reconstruction | Solvers use the active HRX generalized-DOF system directly; zero diagonals now indicate singularity |
| ALS began from the failed trial state | C# first applies the negative failed increment and calls `revertToLastCommit`, then starts reduced substeps (`StaticNonLinearAnalysis.cs`, around lines 141–175) | Mistranslation | ALS now undoes the failed load and restores committed element state first |
| Failed nonlinear analysis returned Python code `0` | C# method records an incomplete analysis state rather than reporting completion | Python API bug | Python returns the real negative result code |
| Load functions always fell back to `(0,0)→(1,1)` | C# stores `LoadFunction` and `LoadFunctionItem` in separate collections and joins by key | Incomplete loader | Added `LoadFunctionItem` parsing and attachment |
| P-Delta string/integer comparisons were inconsistent | C# uses a typed enum and computes/assembles P-Delta loads in dedicated load modules | Incomplete port | Values are normalized; enabled P-Delta raises `NotImplementedError` because its required subsystem is absent |
| `Program.get_value_graph_analysis()` returned load factor `1.0` | C# derives graph force from reactions and reads the selected model-point displacement | Stub/incomplete port | Returns the real integrator multiplier and generalized displacement; full reaction extraction remains unsupported |
| Energy accumulation modified local Python floats | C# passes energy values by `ref` | Language-semantics mistranslation | `compute_energy()` returns `(elastic, dissipated)` |
| `solve_linear(model, alfa)` passed `alfa` as the analysis key | No equivalent mistake exists in C# | Python-only API bug | Split `stiffness_alfa`, `analysis_key`, and `combination` |
| Psi coefficients were silently replaced with zero | C# reads `Psi0/Psi1/Psi2` from the actual `LoadTemplateItem` and combines them with gamma factors (`LoadTemplateManager.cs`, lines 29–179) | Incomplete data model | Unsupported Psi coefficients now raise an explicit error |
| ArcLength implementation differed substantially | C# uses `deltaUbar`, `deltaUhat`, accumulated step displacement, a selected-control/all-DOF constraint, load-function segment direction, and target displacement | Broad algorithm mistranslation | ArcLength was rewritten around the C# algorithm, with two documented C# bug fixes |

## Correct C# behaviors retained

### Active generalized DOFs

The C# model constructs the solver system after constraints are accounted for. The HRX afference data therefore already refers to active generalized DOFs. The revised Python solver does not perform a second guessed restraint elimination.

### Newton sequence

The revised Python sequence now matches the C# ordering:

1. form residual/unbalance;
2. for a Standard method, rebuild tangent stiffness;
3. solve `K * deltaU = residual`;
4. update element trial state and total displacement;
5. form the new residual;
6. test convergence;
7. repeat.

For line search, the full Newton step is applied first and trial positions are reached by corrections `(eta_j - eta_previous) * deltaU`.

### Load-control state

The total displacement is cumulative across steps. Only `LS.X` represents the current iteration increment. `U_committed` is updated only after a successful step or successful ALS substep.

### ALS state restoration

The failed full load increment is removed before any substep attempt. Each failed substep is also removed before restoring the last successful committed element state.

## Intentional differences from C#

The revised Python does **not** copy several apparent defects found in the original C# source. They are listed in [ORIGINAL_CSHARP_BUGS.md](ORIGINAL_CSHARP_BUGS.md).

It also raises explicit errors for P-Delta and Psi-dependent combinations because the necessary C# model/load subsystems were not included in the Python snapshot. Silent approximation would be more dangerous than an unsupported-feature error.

## Final benchmark qualification

The supplied final archive made a numerical comparison possible. Analysis 1 step 1 agrees with the C# SQLite result to about `2.282e-5` relative displacement error. Full analysis equivalence is not yet established because the Python quad path does not port C# `ComputeDN`/normal-force coupling into `SpringCoulomb03`, and chained-result restoration remains unimplemented.

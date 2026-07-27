# HiStrA Python/C# Integration Audit Summary

## Result

The uploaded package was audited against its own HRX model and C# SQLite `.Results` database. The actual benchmark is a 126-DOF model with 28 nodes, 18 quads, 29 interfaces, 2,349 hysteretic springs, and 105 `SpringCoulomb03` springs. Several bundled reports and tests referred to a different 2,142-DOF model and were therefore stale.

The corrected Python solver now executes the complete five-step LoadControl analysis represented by the database, with exact committed step ordering and load factors. Step 1 reproduces the C# displacement vector to numerical roundoff. Steps 2–5 complete but do not meet the displacement acceptance criterion, so full C# equivalence is **not claimed**.

| Step | Load factor | Iterations | Relative displacement error | Maximum absolute DOF error | Accepted |
|---:|---:|---:|---:|---:|:---:|
| 1 | 0.2 | 3 | 1.311e-14 | 6.365e-17 | Yes |
| 2 | 0.4 | 11 | 5.930e-2 | 7.257e-4 | No |
| 3 | 0.6 | 16 | 1.799e-1 | 3.338e-3 | No |
| 4 | 0.8 | 7 | 1.915e-1 | 4.313e-3 | No |
| 5 | 1.0 | 38 | 1.153e-1 | 5.408e-3 | No |

Measured full-run time was 34.45 seconds on the audit container. All values were finite.

## Principal corrections

- Ported the active C# `Quad.ComputeDN` call chain and normal-stress bookkeeping.
- Passed interface and quad normal-force increments into all Coulomb springs.
- Matched C# interface-before-quad update order.
- Replaced the inactive Python out-of-plane interface branch with the C# model's hard-coded `TwoSprings` branch.
- Matched C# single-precision geometry/load operations where they affect the benchmark path.
- Completed Coulomb commit/revert handling for normal stress and yield limits.
- Added complete reversible solver snapshots and integrated rollback into Newton, line search, step, ALS, and ArcLength retry paths.
- Added typed SQLite readers and strict, complete final-state restart/chaining.
- Made unsupported/missing load metadata fail explicitly instead of silently substituting zero.
- Added deterministic integration, database, restart, rollback, and first-step benchmark tests.

## Remaining blocker

The complete committed step-1 global and local state matches the database. When exact C# step-2 strains and normal-force increments are applied to that state, all 2,349 hysteretic springs and all 105 Coulomb springs reproduce C# force and phase to approximately 1e-13 or better. Nevertheless, the Python nonlinear path commits a different step-2 displacement state under the absolute Work convergence criterion. The database contains committed states but no per-iteration vectors, and the supplied environment cannot execute the original C# UMFPACK solver. The remaining blocker is therefore isolated to the step-2 global Newton/line-search numerical path or a difference between the supplied C# source and the binary that produced the database.

See `histra_documentation/` for measured methodology, database conventions, changes, C# defects, feature status, and remediation steps.

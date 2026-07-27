# Complete Solver Flow

For the selected `Vert` analysis, Python now follows this sequence:

1. Parse the HRX and select analysis key 1.
2. For a virgin analysis, clear global vectors and all supported local trial/committed state while preserving model definitions.
3. For a chained analysis, require a `.Results` database and restore the selected prerequisite's final complete state.
4. Generate the supported load vector using the selected HRX load combination and database combination row.
5. Assemble and factor the initial stiffness.
6. Start a LoadControl increment and update the load multiplier/pseudo-time.
7. Form the unbalance and solve the modified Newton increment.
8. Snapshot all reversible state before trial updates.
9. Update interfaces before quads, matching C# ordering.
10. In each interface, update transverse springs, calculate normal-force increments, then update in-plane and out-of-plane Coulomb springs.
11. In each quad, compute `dN`, current normal stress, volume, and update its Coulomb spring.
12. Assemble the residual and evaluate the absolute Work convergence test.
13. If needed, run Regula-Falsi trials with complete rollback on failed update or rejected outer iteration.
14. On convergence, commit global, element, and spring state and record metrics.
15. On failure, restore the complete pre-step state. ALS and ArcLength retries also start from complete snapshots.
16. Stop at the load-function endpoint.

A snapshot includes global displacements, velocity/step vectors, sparse linear-system vectors and matrices, external and P-Delta vectors, integrator fields, convergence-test state, line-search state, element local state, and all spring attributes. Restore also removes fields created only during a failed trial.

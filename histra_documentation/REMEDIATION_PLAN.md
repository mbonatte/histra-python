# Remediation plan

## Phase 1 — Complete quad/Coulomb coupling

1. Port C# `Quad.ComputeDN` and its dependencies.
2. Associate the correct masonry material and element volume.
3. Capture `sigmaInitial` at the same analysis/step point as C#.
4. Update quad `Status.f` consistently with C#.
5. Compare step-2 Newton residuals and selected spring states iteration by iteration.

**Exit criterion:** analysis 1 reproduces all five C# steps within agreed displacement, force, tangent, and phase tolerances.

## Phase 2 — Implement database restart

1. Read global vectors from `DynamicVectorsState`.
2. Read quad/interface local states for the requested analysis/combination/step.
3. Map `SpringStates` to each spring purpose/local index and restore every committed field.
4. Restore pseudo-time/load factor and verify internal-force equilibrium before continuing.

**Exit criterion:** analysis 22 begins with the exact final state of analysis 1 and its initial residual matches C#.

## Phase 3 — Validate ArcLength

Compare all stored analysis-22 steps:

- lambda and control displacement;
- selected correction roots and eta;
- spring phases and force histories;
- final global/local state.

## Phase 4 — Broaden load support

Port or explicitly specify unsupported behavior for non-self-weight actions, Psi factors, reaction extraction, and P-Delta.

## Phase 5 — Improve diagnostics/performance

- line-search stagnation and repeated-eta detection;
- per-iteration timing and residual diagnostics;
- optional matrix factorization reuse;
- remove process-global `ModelManager` vectors;
- add typed result and state objects.

## Phase 6 — Engineering acceptance

Create small analytical fixtures and retain the supplied bridge model as a larger regression. Require reproducible tolerances for displacements, reactions, element forces, spring histories, and energy before declaring parity.

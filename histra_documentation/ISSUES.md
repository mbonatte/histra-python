# Current issues

This file lists issues that remain after the C# alignment and final benchmark audit. Earlier issues such as false success codes, cumulative-displacement reset, tangent-assembly overwrite, degenerate Regula Falsi initialization, and missing load-function items have been repaired and are summarized at the end.

## ISSUE-01 — Quad normal-force coupling is not translated

**Severity:** Critical  
**Location:** `histra/elements/quad.py`, `Quad.update_domain`

The C# `Quad.UpdateDomain` computes `dN` and `sigma` through `ComputeDN`, stores the first-step initial stress, updates `Status.f` from the residual, and passes `dN`, masonry material, volume, and initial stress into `SpringCoulomb03`.

The Python code currently passes:

```python
dN = 0.0
masonry = None
volume = 0.0
sigma = 0.0
```

This removes the axial/normal-force dependency from the diagonal frictional constitutive law. It is the leading known explanation for loss of agreement after the first mostly elastic load step.

**Required work:** port `ComputeDN`, material/volume association, initial-stress capture, and the C# `Status.f` update; compare every Newton iteration against C#.

## ISSUE-02 — Chained analysis restart state is not restored

**Severity:** Critical  
**Location:** `histra/solver/solve.py`

The HRX analyses use `InitialAnalysisKey` to start from prior results. Correct restoration requires:

- the global displacement and velocity vectors;
- quad and interface local state;
- every committed spring-history variable;
- load factor, pseudo-time, and other analysis state.

The loader now parses the restart keys, but Python deliberately raises `NotImplementedError` for a chained analysis. This is safer than silently starting from zero.

**Required work:** implement a typed SQLite state loader for `DynamicVectorsState`, `QuadStates`, `InterfaceStates`, and all relevant `SpringStates` columns, followed by a state-consistency test.

## ISSUE-03 — Complete nonlinear reference analysis is not reproduced

**Severity:** Critical validation gap

Analysis 1 step 1 agrees closely with C#. The complete five-step run has not converged/completed within the bounded Python audit. Until the later steps and final state match, engineering equivalence is unproven.

This is an outcome issue rather than one isolated code line. ISSUE-01 should be addressed first.

## ISSUE-04 — P-Delta remains unsupported

**Severity:** High

The C# application has frame/load-generation infrastructure for P-Delta. That subsystem is absent from this Python package. Python now raises explicitly when P-Delta is enabled.

## ISSUE-05 — Loading support is narrower than C#

**Severity:** High

Self-weight is implemented. Broader load actions and Psi-dependent combinations do not have the complete source data/model behavior needed by C#. Unsupported Psi modes raise rather than silently returning zero.

## ISSUE-06 — Line-search work can grow excessively

**Severity:** High / performance

The supplied analysis permits up to 1,000 line-search evaluations and 1,000 nonlinear iterations. Each trial updates all nonlinear elements and reforms the residual. When the constitutive path is wrong or stagnates, runtime grows dramatically.

Add stagnation detection, diagnostics for eta/residual progression, and configurable bounded benchmark profiles. Do not use a timeout as a numerical convergence rule.

## ISSUE-07 — `ModelManager` uses process-global mutable state

**Severity:** Medium

Reference/external load and total-displacement vectors are class attributes. Concurrent or nested analyses can interfere. Move them into an `AnalysisContext` owned by one solve.

## ISSUE-08 — Results reconstruction from local quad states is approximate

**Severity:** Medium

`extract_displacements` takes the first afference entry for each local quad DOF. Shared/combined afference may overwrite a global value. The first-step comparison is close, but authoritative global comparison should use `DynamicVectorsState` whenever available.

## ISSUE-09 — Reporting and reaction extraction are simplified

**Severity:** Medium

`Program.get_value_graph_analysis` reports the integrator multiplier and one generalized displacement. It does not reproduce the C# model-point/reaction graph subsystem.

## ISSUE-10 — `results.json` is stale and ambiguously named

**Severity:** Documentation/data quality

It reports 556 interfaces instead of 555 and an old `K_nnz`. Its displacement vector reflects HRX saved state, not a new Python nonlinear solve. It should be retained only as a historical snapshot or regenerated with explicit provenance.

## Repaired issues

The audited code now includes fixes for:

- real nonlinear failure exit codes and rollback;
- cumulative LoadControl displacement;
- requested tangent stiffness assembly;
- robust sparse-solve failure handling;
- vector rollback semantics;
- valid line-search endpoints and final-state handling;
- C#-aligned convergence criteria and `max_u` propagation;
- initial stiffness before ArcLength prediction;
- load-function item parsing and unloading step counts;
- ALS starting from the last committed state;
- separate linear stiffness/load parameters;
- explicit errors for unsupported P-Delta/Psi behavior;
- C# virgin-state initialization for `InitialAnalysisKey < 0`.

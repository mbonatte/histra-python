# Modal analysis

## Scope

The Python solver implements the active C# HiStrA modal workflow for the
currently supported Quad/Interface computational model. It supports:

- virgin modal analyses (`InitialAnalysisKey < 0`);
- modal analyses at a committed nonlinear predecessor state;
- the C# `SubspaceIterations` algorithm;
- the C# sequential `InverseIterations` algorithm;
- mass-normalized mode shapes;
- frequencies, periods, participation coefficients, effective modal masses,
  mass percentages, directional maximum components and eigen-residuals;
- C#-compatible `ModalValues` and `ModalShapeValues` row projection.

Dynamic time-history analysis remains outside this implementation.

## C# execution path inspected

The implementation was reconstructed from the current source, principally:

- `SolverRuntime/Program.cs`
- `SolverRuntime/ModelManager.cs`
- `SolverRuntime.AnalysisProcedure/ModalAnalysis.cs`
- `SolverRuntime/Pseudovectors.cs`
- `Objects/Quad.cs`
- `ModelLibrary.MacroKernel.MacroMath/Matrix.cs`
- `SolverRuntime/CommonOperations.cs`
- `Objects.ElementStates/ModalValues.cs`
- `Objects.ElementStates/ModalShapeValues.cs`

The active sequence is:

1. `Program` calls `ModelManager.PrepareModelForAnalysis`.
2. `SetStatus` initializes a virgin model or restores the configured predecessor.
3. `PrepareK(..., alfa=1)` assembles the current tangent stiffness matrix.
4. `ModalAnalysis.Execute` calls `ModelManager.ComputeM`.
5. The requested mode count is limited to `min(NumberOfEigenModes, N - 2)`.
6. The configured modal eigensolver is executed.
7. Each mode is mass-normalized before modal quantities are evaluated.
8. `ModalValues` and one `ModalShapeValues` row per zero-based global DOF are saved.

## Mass matrix

For each Quad, C# creates an eight-node volume by offsetting the four mid-surface
nodes by `+/- normal * thickness / 2`. It integrates

```text
M_e = integral rho * V(q)^T * V(q) dV
```

with a 6 x 6 x 6 Gauss rule, where `rho = material.w / 980.6`. Existing local
loads contribute `abs(P[i] / 980.6)` to the corresponding diagonal term.

A compatibility-sensitive source behavior is preserved: the HRX
`MassMatrixType` and the method's `diagonal` argument are passed through the C#
call chain, but the active Quad routine never uses them. Consequently, an HRX
that says `MassMatrixType="Lumped"` still receives the integrated consistent
Quad mass matrix. Python reports both the requested and effective types.

C# Quad mass assembly also scatters each local coefficient to all afference DOF
pairs without multiplying by the afference `Alfa` values. Python reproduces this
behavior exactly.

## `SubspaceIterations`

`Matrix.SubSpaceIteration2` is ported rather than replaced with a generic
black-box eigensolver. For `n` requested modes it uses a subspace of

```text
min(n + 8, 2*n, total_DOF)
```

vectors, initialized with the legacy .NET `System.Random(0)` sequence. Every
iteration performs:

```text
Y = M X
Z = K^-1 Y
Kr = Z^T K Z
Mr = Z^T M Z
Kr q = lambda Mr q
X = Z q
```

Convergence is based on the sum of absolute changes in the first requested
eigenvalues, divided by that sum from the first iteration and multiplied by
100. Iteration stops when this value is no greater than the HRX
`ConvergenceTolerance`. The C# routine has no iteration limit; Python adds a
1000-iteration safety limit with an explicit error.

This stopping rule is based on eigenvalue changes, not an eigen-residual. It can
therefore retain visibly larger residuals in upper modes. That behavior is
preserved for C# result parity and each Python mode exposes `residual_norm` so it
can be assessed explicitly.

## `InverseIterations`

The alternate C# path factorizes `K` once and finds modes sequentially by inverse
iteration. Previously found mode vectors are removed using the source's
Euclidean projection. The HRX convergence criterion selects either:

- `Frquency`: `10000 * abs(lambda_i - lambda_(i-1)) / lambda_i`; or
- `EigenVector`: the source residual-change test.

The final vector is mass-normalized before modal quantities are calculated.

## Modal quantities

For each mass-normalized shape `phi` and direction pseudovector `e_d`:

```text
M_e,d = M e_d
M_total,d = e_d^T M e_d
Gamma_d = phi^T M e_d
M_modal,d = Gamma_d^2
MassPercent_d = 100 * M_modal,d / M_total,d
```

The directional pseudovectors reproduce C# assignment semantics: the first
entry of each Quad translational afference is assigned to the corresponding
global DOF. `Umax` is the maximum of `abs(phi[j] * e_d[j])`.

Eigenvector sign is mathematically arbitrary. Python orients every mode
consistently by making its largest absolute component positive. Participation
coefficient signs can therefore be opposite to a C# run while frequencies,
effective masses and physical shapes remain equivalent.

## Python API

```python
from histra import load_model, solve_modal_analysis

model = load_model("Ersino.hrx")
analysis = model.collections.analyses[30]
result = solve_modal_analysis(model, analysis)

print(result.frequencies)
print(result.modal_values_rows())
mode_shapes = result.mode_shapes  # shape: (GDL, number_of_modes)
```

For a chained analysis loaded directly from disk:

```python
result = solve_modal_analysis(
    model,
    model.collections.analyses[21],
    results_path="Ersino.Results",
)
```

`AnalysisSession.run(...)` dispatches `AnalysisType=5` automatically and keeps
the predecessor physical state available for a later chained analysis.

## Command line

```console
python -m histra.tools.run_modal Ersino.hrx \
  --analysis Modal_-1 \
  --output modal-summary.json \
  --shapes modal-shapes.npz
```

For a modal analysis with a predecessor, also pass `--results model.Results`.

## C# database validation

```console
python -m histra.tools.validate_modal_results \
  Ersino.hrx Ersino.Results --analysis-key 30 \
  --output modal-validation.json
```

The validator compares frequencies, total mass and mass-weighted mode
correlations against `ModalValues` and `ModalShapeValues`.

## Ersino regression

The supplied Ersino model contains 14,252 active DOFs and requests ten modes for
analysis key 30. The real-file integration test verifies:

- directional total mass against C# within `3e-8` relative tolerance;
- all ten frequencies within `3e-8` relative tolerance;
- diagonal mass-weighted mode correlations above `0.9999999`;
- all 142,520 stored C# modal-shape values are represented.

Run it with:

```console
HISTRA_MODAL_HRX=/path/Ersino.hrx \
HISTRA_MODAL_RESULTS=/path/Ersino.Results \
python -m pytest -q histra/tests/test_modal_analysis.py
```

## Current boundary

The mass implementation covers the model entities currently represented by the
Python domain: Quads carry mass and Interfaces do not. Future Vertex, Solid,
Frame or Fiber collections are rejected explicitly until their C# mass routines
are ported. The code does not silently discard unsupported element masses.

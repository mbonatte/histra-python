# histra-python

An installable, in-process Python implementation of the supported HiStrA
static nonlinear and modal-analysis workflows.

## Backend service API

```python
from histra import PythonAnalysisRequest, run_python_solver_job

result = run_python_solver_job(
    "model.hrx",
    [
        PythonAnalysisRequest(
            name="Vert",
            output_request=outputs,
            timeout_seconds=600,
        )
    ],
    timeout_seconds=600,
)
```

The service:

- loads the HRX once;
- resolves and executes `InitialAnalysisKey` dependencies;
- keeps committed global and constitutive state in memory;
- applies concrete interface/material mutations between analyses;
- enforces job and analysis deadlines cooperatively;
- projects C#-compatible reaction and model-point displacement rows.
- executes `AnalysisType=5` modal analyses and projects C#-compatible modal
  summaries and complete global-DOF mode shapes.

## Install

```console
python -m pip install -e .
```

Runtime dependencies are NumPy, SciPy, and Numba. Python 3.11 or newer is
required.

## Public API

The stable root package exports:

- `load_model`
- `AnalysisSession`
- `run_python_solver_job`
- `PythonAnalysisRequest`
- `ConcreteInterfaceMutation`
- `AnalysisExecution`, `AnalysisStep`, `AnalysisOutcome`
- `solve_modal_analysis`, `ModalAnalysisResult`, `ModalMode`
- capability and cancellation exceptions
- `project_analysis_outputs`, `project_displacements`, `project_reactions`

## Output compatibility

`project_displacements` reproduces the fields selected by HiStrA Job Runner from
C# `DisplModelPoints`:

```text
IdElement, ParentKey, Step, Ux, Uy, Uz
```

For supported Node model points it averages connected Quad predictions like the
C# response operation. Quad model points use centroid or vertex displacement
according to `IdVertex`. The mapping and numerical values are regression-tested
against the included authoritative `model.hrx` + `model.Results` pair.

Reaction projection uses the C# `ReactionSumStates` sign convention:

```text
Step, R1, R2, R3
```

## Current capability boundary

Supported backend scope is the validated static nonlinear and modal Quad /
Interface model subset. Capability preflight rejects unsupported model-point
element types, P-Delta, broken analysis chains, and response-spectrum modal
contribution requests. Modal eigenanalysis itself is supported.

The modal solver ports the active C# consistent Quad mass integration,
`SubSpaceIteration2`, inverse iteration, mass normalization, participation
coefficients and effective modal masses. See
[Modal analysis](docs/guides/modal-analysis.md).

The solver uses shared class-level runtime arrays internally, so one solve is
active per Python process. A cancellable process-wide lock prevents concurrent
state corruption. Cooperative cancellation checks are present at load-step,
Newton, line-search, ArcLength retry, and ALS boundaries. A single native
linear solve cannot be interrupted in the middle.

## C# numerical parity mode

The authoritative C# solver uses SuiteSparse UMFPACK. For branch-sensitive
parity regressions, select the same native backend explicitly with
`HISTRA_LINEAR_SOLVER=umfpack` and point `HISTRA_UMFPACK_LIBRARY` to the native
shared library. The default remains SciPy SuperLU to preserve existing production behavior.
Use `auto` only when environment-dependent backend selection is intentional; it
uses UMFPACK when available and otherwise falls back to SuperLU.

An optional deterministic JSONL/NPZ diagnostic stream records step and Newton
iteration metrics with stable C# spring identifiers. It is disabled by default.
See [C# parity diagnostics](docs/guides/csharp-parity-diagnostics.md) and the
[branch-divergence investigation](docs/investigations/csharp-python-branch-divergence.md).

## Tests

```console
pytest histra/tests
```

The normal suite includes a solve of the `Vert` benchmark and compares projected
rows with its authoritative C# `.Results` database. Longer chain and live-load
acceptance tests remain opt-in through their documented environment variables.
The Ersino modal regression is opt-in through `HISTRA_MODAL_HRX` and
`HISTRA_MODAL_RESULTS`.

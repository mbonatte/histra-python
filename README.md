# histra-python

An installable, in-process Python implementation of the supported HiStrA
static nonlinear solver workflow.

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

Supported backend scope is the already validated static nonlinear Quad /
Interface model subset. Capability preflight rejects unsupported model-point
element types, P-Delta, broken analysis chains, and modal output requests.

The solver uses shared class-level runtime arrays internally, so one solve is
active per Python process. A cancellable process-wide lock prevents concurrent
state corruption. Cooperative cancellation checks are present at load-step,
Newton, line-search, ArcLength retry, and ALS boundaries. A single native
linear solve cannot be interrupted in the middle.

## Tests

```console
pytest histra/tests
```

The normal suite includes a solve of the `Vert` benchmark and compares projected
rows with its authoritative C# `.Results` database. Longer chain and live-load
acceptance tests remain opt-in through their documented environment variables.

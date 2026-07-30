# C# parity diagnostics

The nonlinear solver has an optional deterministic diagnostic stream for
comparing Python runs with a HiStrA `.Results` database. It is disabled by
default and the normal solve path does not calculate spring summaries or write
files.

## Linear solver parity

The original C# implementation calls the SuiteSparse UMFPACK `umfpack_di_*`
API, uses UMFPACK defaults, and sets control slot 5 to the symmetric strategy.
Python can now use the same native backend:

```console
set HISTRA_LINEAR_SOLVER=umfpack
set HISTRA_UMFPACK_LIBRARY=C:\path\to\umfpack.dll
pytest histra/tests
```

On Linux or macOS, point `HISTRA_UMFPACK_LIBRARY` to the corresponding native
shared library. `HISTRA_LINEAR_SOLVER=auto` selects UMFPACK when a loadable
library is found and otherwise retains SciPy SuperLU. The default is explicit
SuperLU so installing SuiteSparse cannot silently change an existing run. Use an explicit
`umfpack` selection for parity regressions so a missing native dependency fails
with an actionable error instead of silently changing the numerical backend.

The backend can also be selected per solve:

```python
code, steps = solve_static_nonlinear(
    model,
    analysis,
    combination=1,
    linear_solver_backend="umfpack",
)
```

## Deterministic event stream

```python
from histra.solver.diagnostics import DiagnosticOptions
from histra.solver.solve import solve_static_nonlinear

options = DiagnosticOptions(
    output_dir="parity/vert",
    capture_vectors=True,
    capture_matrices=False,
    capture_element_states=False,
    spring_details=True,
    flush_each_event=True,
)

code, steps = solve_static_nonlinear(
    model,
    analysis,
    combination=1,
    diagnostics=options,
    linear_solver_backend="umfpack",
)
```

`events.jsonl` records analysis, step, Newton-iteration, snapshot, restore,
commit, automatic load-step reduction, failure, and timing events. It includes
load factors, arc-length data, convergence metrics, governing residual and
correction DOFs, spring-phase counts, and stable spring identities of the form:

```text
(ParentType, ParentKey, SpringPurpose, IdLocal)
```

Enable `capture_vectors` to write displacement, correction, residual, external
load, target load and internal force arrays as compressed NPZ snapshots.
Enable `capture_matrices` to include the CSC tangent matrix. Enable
`capture_element_states` to include all spring states plus Interface and Quad
local displacement arrays.

Full element-state capture is intentionally expensive for large models. Narrow
it to selected regression runs or steps after a lightweight event-only run has
identified the first suspicious step.

## Compare with C# results

```console
python -m histra.tools.compare_csharp_results state \
  parity/vert/vectors/step_00010_iter_00006_committed.npz \
  first-bridge.Results 1 10 --combination 1 \
  --output parity/vertical-step-10.json

python -m histra.tools.compare_csharp_results history \
  first-bridge.Results 3 parity/csharp-live-history.csv --combination 1
```

The state comparator joins springs by the stable C# database identity and
compares spring strain, stress and phase as well as Interface and Quad local
states when present.

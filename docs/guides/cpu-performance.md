# Faster CPU analyses

The solver uses compiled Numba kernels and a compiled sparse linear solver.
Fresh preparation and compiled coverage checks remain mandatory. Performance
changes do not alter constitutive laws, convergence tolerances or authored
analysis strategies.

## Running one model

The high-level `run_python_solver_job(...)` API and
`python -m histra.tools.run_vert_live` automatically skip saved computational
state when loading HRX inputs. For direct sessions, use the solver loader:

```python
from histra import AnalysisSession, load_solver_model

model = load_solver_model("bridge.hrx")
session = AnalysisSession(model, equilibrium_policy="error")
result = session.run("Vert")
```

`load_solver_model` keeps structural geometry, reference axes, materials, loads,
restraints and analysis definitions. It omits saved interfaces, springs,
afference matrices and Quad displacement history, which fresh preparation
reconstructs. Use `load_model` to inspect those C# reference snapshots.
Both loaders preserve the source HRX file and require fresh preparation.

Virgin static solves construct their compiled runtime after state initialization.
Dependency checks run first; full object coverage is enforced before numerical
execution. Restarts and material mutations retain lifecycle coverage checks.
Interface fibre stiffness preparation reuses face projections across fibres with
the original C# float32 operation order.

## Running independent models together

`run_parallel_solver_jobs` launches independent CPU jobs in separate processes.
Each job may contain a dependent analysis chain; that chain stays sequential.
The parent only coordinates workers, avoiding shared solver runtime arrays.

```python
from histra import PythonAnalysisRequest, PythonSolverJob, run_parallel_solver_jobs

requests = (PythonAnalysisRequest("Vert", output_request=None, timeout_seconds=300),)
jobs = [PythonSolverJob(path, requests, timeout_seconds=600)
        for path in ("bridge_a.hrx", "bridge_b.hrx")]
outcomes = run_parallel_solver_jobs(jobs, max_workers=2, threads_per_worker=1)
for path, outcome in zip(("bridge_a.hrx", "bridge_b.hrx"), outcomes):
    if outcome.completed:
        print(path, outcome.result.analyses["Vert"].execution.outcome)
    else:
        print(path, outcome.error)
```

The command-line entry point runs the same API with strict equilibrium checks:

```bash
python -m histra.tools.parallel_solver_jobs bridge_a.hrx bridge_b.hrx --analysis Vert --workers 2 --threads 1 --output batch-summary.json
```

This command writes an execution summary; use the Python API when you need the
returned execution histories or projected output rows.

Results preserve input order, including individual failures. Each worker starts
with Numba and BLAS thread limits before importing numerical libraries. By default
at most two workers run; available CPU cores also cap concurrency. Optional
`memory_budget_mb` and `estimated_job_memory_mb` together reduce worker count.
These are scheduling estimates, not enforced memory limits.

Batch job deadlines include startup, loading and preparation, and a worker that
exceeds its deadline is terminated. The existing in-process API retains cooperative
cancellation. A fresh interpreter per job prevents runtime state from leaking
between models, but startup and result transfer can outweigh parallelism for tiny
jobs. The batch runner explicitly selects the CPU backend.

Use pickle-compatible output request objects defined in importable modules, or
`None` when only execution histories are needed. Keep callbacks in the existing
single-job API. The private worker transport is not an input-file format.

See the [CPU workflow measurements](../benchmarks/cpu-workflow-2026-10-26.md) for
identified models, timing methodology and numerical comparisons.
